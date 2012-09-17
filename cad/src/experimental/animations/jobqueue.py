# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.

"""\
jobqueue.py

$Id$

Python code for parallelizing various kinds of jobs on a cluster of
Linux/Unix/Mac machines. Initially being used for raytracing jobs, but
should be useful for other things, perhaps parallel simulations some
day.
"""

import os, sys, types, threading, time, string

worker_list = [ 'localhost' ]

DEBUG = 0
if os.environ.has_key("DEBUG"):
    DEBUG = string.atoi(os.environ["DEBUG"])

all_workers_stop = False

def do(cmd):
    print cmd
    if os.system(cmd) != 0:
        raise Exception(cmd)

class Worker(threading.Thread):

    def __init__(self, jobqueue, machine, workdir):
        threading.Thread.__init__(self)
        self.machine = machine
        self.jobqueue = jobqueue
        self.workdir = workdir
        if machine in ('localhost', '127.0.0.1'):
            self.do = do
            self.get = self._local_get
            self.put = self._local_put
        else:
            self.do = self._remote_do
            self.get = self._remote_get
            self.put = self._remote_put

    def _remote_do(self, cmd):
        do('ssh ' + self.machine + ' ' + cmd)

    def _local_put(self, filelist, srcdir):
        # Transfer files from host to worker, NON DESTRUCTIVELY
        do('for x in %s; do cp %s/$x %s; done' %
           (" ".join(filelist), srcdir, self.workdir))

    def _local_get(self, filelist, dstdir):
        # Transfer files from host to worker
        do('for x in %s; do mv %s/$x %s; done' %
           (" ".join(filelist), self.workdir, dstdir))

    def _remote_put(self, filelist, srcdir):
        # Transfer files from host to worker
        do('(cd %s; tar cf - %s) | gzip | ssh %s "(cd %s; gunzip | tar xf -)"' %
           (srcdir, " ".join(filelist), self.machine, self.workdir))

    def _remote_get(self, filelist, dstdir):
        # Transfer files from host to worker
        do('ssh %s "(cd %s; tar cf - %s)" | gzip | (cd %s; gunzip | tar xf -)' %
           (self.machine, self.workdir, " ".join(filelist), dstdir))

    # Each worker grabs a new jobs as soon as he finishes the previous
    # one. This allows mixing of slower and faster worker machines;
    # each works at capacity.
    def run(self):
        global all_workers_stop
        self.do('mkdir -p ' + self.workdir)
        while not all_workers_stop:
            job = self.jobqueue.get()
            if job is None:
                return
            try:
                job.go(self)
                self.do('rm -rf ' + self.workdir)
                self.do('mkdir -p ' + self.workdir)
            except:
                all_workers_stop = True
                raise

_which_job = 0

class Job:

    def __init__(self, srcdir, dstdir, inputfiles, outputfiles):
        global _which_job
        self.index = index = _which_job
        _which_job += 1
        self.srcdir = srcdir
        self.dstdir = dstdir
        self.inputfiles = inputfiles
        self.outputfiles = outputfiles

    def shellScript(self):
        raise Exception, 'overload me'

    def preJob(self, worker):
        pass

    def postJob(self, worker):
        pass

    def go(self, worker):
        self.preJob(worker)
        scriptname = 'job_%08d.sh' % self.index
        longname = os.path.join(self.srcdir, scriptname)
        script = ("(cd " + worker.workdir + "\n" +
                  (self.shellScript()) + ")\n")
        if DEBUG >= 1:
            print worker.machine + ' <<<\n' + script + '>>>'
        outf = open(longname, 'w')
        outf.write(script)
        outf.close()
        os.system('chmod +x ' + longname)
        worker.put(self.inputfiles + [ scriptname ], self.srcdir)
        worker.do(os.path.join(worker.workdir, scriptname))
        worker.get(self.outputfiles, self.dstdir)
        self.postJob(worker)


class JobQueue:

    def __init__(self, _worker_list=None):
        if _worker_list is None:
            _worker_list = worker_list
        self.worker_pool = worker_pool = [ ]
        self.jobqueue = [ ]
        self._lock = threading.Lock()
        for macdir in _worker_list:
            try:
                machine, workdir = macdir
            except:
                machine = macdir
                assert type(machine) is types.StringType
                workdir = '/tmp/jobqueue'
            worker = Worker(self, machine, workdir)
            worker_pool.append(worker)

    def append(self, job):
        self._lock.acquire()   # thread safety
        self.jobqueue.append(job)
        self._lock.release()
    def get(self):
        self._lock.acquire()   # thread safety
        try:
            r = self.jobqueue.pop(0)
        except IndexError:
            r = None
        self._lock.release()
        return r

    def start(self):
        for worker in self.worker_pool:
            worker.start()

    def wait(self):
        busy_workers = self.worker_pool[:]
        while True:
            busy_workers = filter(lambda x: x.isAlive(),
                                  busy_workers)
            if len(busy_workers) == 0:
                break
            if all_workers_stop:
                raise Exception('somebody stopped')
            time.sleep(0.5)

def runjobs(mydir, infiles, outfiles, script):
    """Here is a simple usage, if each job takes one input file and
    produces one output file, and if we use the same directory for
    srcdir and dstdir.
    """
    q = JobQueue(worker_list)
    for ifile, ofile in map(None, infiles, outfiles):
        class MyJob(Job):
            def shellScript(self, script=script, ifile=ifile, ofile=ofile):
                return script % { 'ifile': ifile,
                                  'ofile': ofile }
        q.append(MyJob(mydir, mydir, [ifile], [ofile]))
    q.start()
    q.wait()

# ============================================================

if __name__ == "__main__":

    worker_list = [ 'localhost' ] # , 'server', 'mac', 'laptop' ]
    mydir = '/tmp/tryit'
    os.system('rm -rf ' + mydir)
    os.system('mkdir -p ' + mydir)

    N = 20
    inputfiles = [ ]
    outputfiles = [ ]
    for i in range(N):
        ifile = 'input%03d' % i
        ofile = 'output%03d' % i
        inputfiles.append(ifile)
        outputfiles.append(ofile)
        outf = open(os.path.join(mydir, ifile), 'w')
        outf.write('hello\n')
        outf.close()

    runjobs(mydir, inputfiles, outputfiles,
            """sleep 20
            if [ -f %(ifile)s ]; then
                cp %(ifile)s %(ofile)s
            else
                echo BAD > %(ofile)s
            fi
            """)

    # verify correct outputs, and clean up
    for ofile in outputfiles:
        assert open(os.path.join(mydir, ofile)).read() == 'hello\n'
