# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
Process.py

Provides class Process, a QProcess subclass which is more convenient to use,
and a convenience function run_command() for using it to run external commands.

$Id$

History:

bruce 050902 made this, using Qt doc and existing QProcess calls for guidance.

Future plans:

This can be extended as needed to be able to do more flexible communication
with external processes, and have better convenience functions, e.g. for
running multiple processes concurrently.

And it might as well be extended enough to replace some existing uses of QProcess
with uses of this class, if that would simplify them (but I'm not sure whether it would).
'''

__author__ = 'bruce'

from qt import QProcess, QStringList, qApp, SIGNAL, QDir, QString
import time

def ensure_QStringList(args):
    if type(args) == type([]):
        arguments = QStringList()
        for arg in args:
            arguments.append(arg)
        args = arguments
    assert isinstance(args, QStringList) # fails if caller passes the wrong thing
    return args

def ensure_QDir(arg):
    if type(arg) == type(""):
        arg = QString(arg)
    if isinstance(arg, QString):
        arg = QDir(arg)
    assert isinstance(arg, QDir) # fails if caller passes the wrong thing
    return arg

super = QProcess

class Process(QProcess):
    "Subclass of QProcess which is able to capture and record stdout/stderr, and has other convenience methods."
    stdout = stderr = None
    def __init__(self, *args):
        """Like QProcess.__init__, but the form with arguments might not be usable with a Python list.
        (But see our setArguments method, which is overridden to accept one.)
        """
        super.__init__(self, *args)
        # I don't know if we'd need to use these signals if we wanted to discard the data.
        # The issue is whether it's going into a pipe which fills up and blocks the process.
        # In order to not have to worry about this, we read it all, whether or not caller wants it.
        # We discard it here (in these slot methods) if caller didn't call set_stdout or set_stderr.
        # See also QProcess.communication property (whose meaning or effect is not documented in Qt Assistant).
        self.connect( self, SIGNAL('readyReadStdout()'), self.read_stdout) ###k
        self.connect( self, SIGNAL('readyReadStderr()'), self.read_stderr) ###k
    def read_stdout(self):
        bytes = self.readStdout() # QByteArray
        bytes = str(bytes) ###k
        self.got_stdout(bytes)
    def read_stderr(self):
        bytes = self.readStderr() # QByteArray
        bytes = str(bytes) ###k
        self.got_stderr(bytes)
    def setArguments(self, args): #k needed?
        "Overrides QProcess.setArguments so it can accept a Python list as well as a QStringList."
        args = ensure_QStringList(args)
        super.setArguments(self, args)
    def setWorkingDirectory(self, arg): # definitely needed
        "Overrides QProcess.setWorkingDirectory so it can accept a Python string or QString as well as a QDir object."
        arg = ensure_QDir(arg)
        super.setWorkingDirectory(self, arg)
    def set_stdout(self, stdout):
        """Cause stdout from this process to be written to the given file-like object
        (which must have write method, and whose flush method is also used if it exists).
        This should be called before starting the process.
        If it's never called, stdout from the process will be read and discarded.
        """
        self.stdout = stdout
    def set_stderr(self, stderr):
        "Like set_stdout but for stderr."
        self.stderr = stderr
    def got_stdout(self, bytes):
        if self.stdout is not None:
            self.stdout.write(bytes)
            self.try_flush(self.stdout)
    def got_stderr(self, bytes):
        if self.stderr is not None:
            self.stderr.write(bytes)
            self.try_flush(self.stderr)
    def try_flush(self, file):
        try:
            file.flush # see if attr is present
        except:
            pass
        else:
            file.flush()
        return
    def wait_for_exit(self):
        """Wait for the process to exit (sleeping by 0.05 seconds in a loop).
        Return its exitcode.
        Call this only after the process was successfully started using self.start() or self.launch().
        """
        while self.isRunning():
            import env
            env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
                #k is this required for us to get the slot calls for stdout / stderr ?
                # I don't know, but we want it even if not.
            time.sleep(0.05)
        return self.exitcode()
    def exitcode(self):
        "Return the exitcode, or -2 if it crashed or was terminated. Only call this after it exited."
        assert not self.isRunning()
        if self.normalExit():
            return self.exitStatus()
        return -2
    def run(self, args = None):
        """Do everything needed to run the process with these args
        (a list of strings, starting with program name or path),
        except for the setX methods which caller might want to call first,
        like set_stdout, set_stderr, setWorkingDirectory,
        and optionally setArguments if args are not provided here.
        """
        if args is not None:
            self.setArguments(args)
        self.start() #k ok that we provide no stdin? #e might need to provide an env here
        return self.wait_for_exit()
    pass

def run_command( program, args = [], stdout = None, stderr = None, cwd = None ):
    """Run program, with optional args, as a separate process,
    optionally capturing its stdout and stderr to the given file-like objects
    (or discarding it if those are not provided),
    optionally changing its current working directory to the specified directory cwd.
       Wait for it to exit and return its exitcode, or -2 if it crashed.
    If something goes wrong in finding or starting the program, raise an exception.
    """
    pp = Process()
    pp.setArguments([program] + args)
    if cwd:
        pp.setWorkingDirectory(cwd)
    pp.set_stdout( stdout) # ok if this is None
    pp.set_stderr( stderr)
    ec = pp.run()
    return ec

# == test code

def _test(args, wd = None):
    import sys
    pp = Process()

    print
    print "args:", args
    if wd:
        print "working dir:", wd

    pp.setArguments(args)
    if wd:
        pp.setWorkingDirectory(wd)
    pp.set_stdout( sys.stdout) #k might be more useful if we labelled the first uses or the lines...
    pp.set_stderr( sys.stderr)
    print "running it"
    ec = pp.run()
    print "exitcode was", ec

def _all_tests():
    _test( ["date","-r","8"] )
    ##Wed Dec 31 16:00:08 PST 1969
    ##exitcode was 0

    _test( ["date","-rrr","8"] )
    ##date: illegal time format
    ##usage: date [-nu] [-r seconds] [+format]
    ##       date [[[[[cc]yy]mm]dd]hh]mm[.ss]
    ##exitcode was 1

    _test( ["ls","-f"], "/tmp" )
    ##501
    ##mcx_compositor
    ##printers
    ##exitcode was 0

if __name__ == '__main__':
    _all_tests()

# end
