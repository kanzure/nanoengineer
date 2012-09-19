# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Process.py

Provides class Process, a QProcess subclass which is more convenient to use,
and a convenience function run_command() for using it to run external commands.

@author: Bruce, EricM
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050902 made this, using Qt doc and existing QProcess calls for guidance.

ericm 0712xx apparently ported it to Qt 4 (?), and added some features.

Future plans:

This can be extended as needed to be able to do more flexible communication
with external processes, and have better convenience functions, e.g. for
running multiple processes concurrently.

And it might as well be extended enough to replace some existing uses of QProcess
with uses of this class, if that would simplify them (but I'm not sure whether it would).
"""

from PyQt4.Qt import QProcess, QStringList, qApp, SIGNAL, QDir, QString
import time

import foundation.env as env

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
    """
    Subclass of QProcess which is able to capture and record stdout/stderr,
    and has other convenience methods.
    """
    stdout = stderr = None
    def __init__(self, *args):
        """
        Like QProcess.__init__, but the form with arguments might not be usable with a Python list.
        """
        super.__init__(self, *args)
        # I don't know if we'd need to use these signals if we wanted to discard the data.
        # The issue is whether it's going into a pipe which fills up and blocks the process.
        # In order to not have to worry about this, we read it all, whether or not caller wants it.
        # We discard it here (in these slot methods) if caller didn't call set_stdout or set_stderr.
        # See also QProcess.communication property (whose meaning or effect is not documented in Qt Assistant).
        self.connect( self, SIGNAL('readyReadStandardOutput()'), self.read_stdout) ###k
        self.connect( self, SIGNAL('readyReadStandardError()'), self.read_stderr) ###k
        self.connect( self, SIGNAL('error(int)'), self.got_error) ###k
        self.connect( self, SIGNAL('finished(int)'), self.process_exited) ###k

        self.currentError = None
        self.stdoutRedirected = False
        self.stderrRedirected = False
        self.stdoutPassThrough = False
        self.stderrPassThrough = False
        self.processName = "subprocess"

    def read_stdout(self):
        self.setReadChannel(QProcess.StandardOutput)
        while (self.bytesAvailable()):
            line = self.readLine() # QByteArray
            line = str(line) ###k
            self.standardOutputLine(line)

    def read_stderr(self):
        self.setReadChannel(QProcess.StandardError)
        while (self.bytesAvailable()):
            line = self.readLine() # QByteArray
            line = str(line) ###k
            self.standardErrorLine(line)

    def got_error(self, err):
        # it doesn't seem like Qt ever calls this on Linux
        self.currentError = err
        print "got error: " + self.processState()

    def process_exited(self, exitvalue):
        self.set_stdout(None)
        self.set_stderr(None)
        #exit_code = self.exitCode()
        #exit_status = self.exitStatus()
        #print "%s exited, code: %d, status: %d" % (self.processName, exit_code, exit_status)

    ##def setArguments(self, args): #k needed?
        ##"Overrides QProcess.setArguments so it can accept a Python list as well as a QStringList."
        ##args = ensure_QStringList(args)
        ##super.setArguments(self, args)

    ##def setWorkingDirectory(self, arg): # definitely needed
        ##"Overrides QProcess.setWorkingDirectory so it can accept a Python string or QString as well as a QDir object."
        ##arg = ensure_QDir(arg)
        ##super.setWorkingDirectory(self, arg)

    def set_stdout(self, stdout):
        """
        Cause stdout from this process to be written to the given file-like object
        (which must have write method, and whose flush method is also used if it exists).
        This should be called before starting the process.
        If it's never called, stdout from the process will be read and discarded.
        """
        if (self.stdout and self.stdoutRedirected):
            self.stdout.close()
        self.stdoutRedirected = False
        self.stdout = stdout

    def set_stderr(self, stderr):
        """
        Like set_stdout but for stderr.
        """
        if (self.stderr and self.stderrRedirected):
            self.stderr.close()
        self.stderrRedirected = False
        self.stderr = stderr

    def redirect_stdout_to_file(self, filename):
        self.stdout = open(filename, 'w')
        self.stdoutRedirected = True

    def redirect_stderr_to_file(self, filename):
        self.stderr = open(filename, 'w')
        self.stderrRedirected = True

    def setStandardOutputPassThrough(self, passThrough):
        self.stdoutPassThrough = passThrough

    def setStandardErrorPassThrough(self, passThrough):
        self.stderrPassThrough = passThrough

    def setProcessName(self, name):
        self.processName = name

    def standardOutputLine(self, bytes):
        if self.stdout is not None:
            self.stdout.write(bytes)
            self.try_flush(self.stdout)
        if (self.stdoutPassThrough):
            print "%s: %s" % (self.processName, bytes.rstrip())

    def standardErrorLine(self, bytes):
        if self.stderr is not None:
            self.stderr.write(bytes)
            self.try_flush(self.stderr)
        if (self.stdoutPassThrough):
            print "%s(stderr): %s" % (self.processName, bytes.rstrip())

    def try_flush(self, file):
        try:
            file.flush # see if attr is present
        except:
            pass
        else:
            file.flush()
        return

    def processState(self):
        s = self.state()
        if (s == QProcess.NotRunning):
            state = "NotRunning"
        elif (s == QProcess.Starting):
            state = "Starting"
        elif (s == QProcess.Running):
            state = "Running"
        else:
            state = "UnknownState: %s" % s
        if (self.currentError != None):
            if (self.currentError == QProcess.FailedToStart):
                err = "FailedToStart"
            elif (self.currentError == QProcess.Crashed):
                err = "Crashed"
            elif (self.currentError == QProcess.Timedout):
                err = "Timedout"
            elif (self.currentError == QProcess.ReadError):
                err = "ReadError"
            elif (self.currentError == QProcess.WriteError):
                err = "WriteError"
            else:
                err = "UnknownError"
        else:
            err = ""
        return state + "[" + err + "]"

    def wait_for_exit(self, abortHandler, pollFunction = None):
        """
        Wait for the process to exit (sleeping by 0.05 seconds in a
        loop).  Calls pollFunction each time around the loop if it is
        specified.  Return its exitcode.  Call this only after the
        process was successfully started using self.start() or
        self.launch().
        """
        abortPressCount = 0
        while (not self.state() == QProcess.NotRunning):
            if (abortHandler):
                pc = abortHandler.getPressCount()
                if (pc > abortPressCount):
                    abortPressCount = pc
                    if (abortPressCount > 1):
                        self.terminate()
                    else:
                        self.kill()
            env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
                #k is this required for us to get the slot calls for stdout / stderr ?
                # I don't know, but we want it even if not.
            if (pollFunction):
                pollFunction()
            time.sleep(0.05)
        if (abortHandler):
            abortHandler.finish()
        return self.exitCode()

    def getExitValue(self, abortHandler, pollFunction = None):
        """
        Return the exitcode, or -2 if it crashed or was terminated. Only call
        this after it exited.
        """
        code = self.wait_for_exit(abortHandler, pollFunction)
        if (self.exitStatus() == QProcess.NormalExit):
            return code
        return -2

    def run(self, program, args = None, background = False, abortHandler = None, pollFunction = None):
        """
        Starts the program I{program} in a new process, passing the command
        line arguments in I{args}.

        On Windows, arguments that contain spaces are wrapped in quotes.

        @param program: The program to start.
        @type  program: string

        @param args: a list of arguments.
        @type  args: list

        @param background: If True, starts the program I{program} in a new
                           process, and detaches from it. If NE1 exits, the
                           detached process will continue to live.
                           The default is False (not backgrounded).
        @type  background: boolean

        @param abortHandler: The abort handler.
        @type  abortHandler: L{AbortHandler}

        @param pollFunction: Called once every 0.05 seconds while process is running.
        @type  pollFunction: function.

        @return: 0 if the process starts successfully.
        @rtype:  int

        @note: processes are started asynchronously, which means the started()
        and error() signals may be delayed. If this is not a backgrounded
        process, run() makes sure the process has started (or has failed to
        start) and those signals have been emitted. For a backgrounded process
        """
        if (args is None):
            args = []
        self.currentError = None

        if background:
            print "\n%s [%s]: starting in the background with args:\n%s" \
                  % (self.processName, program, args)
            # Run 'program' as a separate process.
            # startDetached() returns True on success.
            rval = not self.startDetached(program, args)
        else:
            print "\n%s [%s]: starting in the foreground with args:\n%s" \
                  % (self.processName, program, args)
            # Run 'program' as a child process.
            self.start(program, args) #k ok that we provide no stdin? #e might need to provide an env here
            rval = self.getExitValue(abortHandler, pollFunction)

        if 1:
            print "%s: started. Return val=%d" % (self.processName, rval)
        return rval

    pass

def run_command( program, args = [], stdout = None, stderr = None, cwd = None ):
    """
    Run program, with optional args, as a separate process,
    optionally capturing its stdout and stderr to the given file-like objects
    (or discarding it if those are not provided),
    optionally changing its current working directory to the specified directory cwd.
       Wait for it to exit and return its exitcode, or -2 if it crashed.
    If something goes wrong in finding or starting the program, raise an exception.
    """
    pp = Process()
    if cwd:
        pp.setWorkingDirectory(cwd)
    pp.set_stdout( stdout) # ok if this is None
    pp.set_stderr( stderr)
    ec = pp.run(program, args)
    return ec

# == test code

class ProcessTest(object):

    def _test(self, program, args = None, wd = None):
        import sys
        pp = Process()

        print
        print "program: %s, args: " % program, args
        if wd:
            print "working dir:", wd

        if wd:
            pp.setWorkingDirectory(wd)
        #pp.set_stdout( sys.stdout) #k might be more useful if we labelled the first uses or the lines...
        pp.set_stderr(sys.stderr)
        ##pp.setProcessChannelMode(QProcess.ForwardedChannels)
        ec = pp.run(program, args)
        print "exitcode was", ec

    def _all_tests(self):
        self._test("ferdisaferd")
        ##Wed Dec 31 16:00:08 PST 1969
        ##exitcode was 0

        #self._test("date", ["-rrr", "8"] )
        ##date: illegal time format
        ##usage: date [-nu] [-r seconds] [+format]
        ##       date [[[[[cc]yy]mm]dd]hh]mm[.ss]
        ##exitcode was 1

        #self._test("ls", ["-f"], "/tmp" )
        ##501
        ##mcx_compositor
        ##printers
        ##exitcode was 0
        global app
        app.quit()

if __name__ == '__main__':
    from PyQt4.Qt import QApplication, QTimer
    import sys
    test = ProcessTest()
    app = QApplication(sys.argv, False)
    timer = QTimer()
    timer.connect(timer, SIGNAL("timeout()"), test._all_tests)
    timer.setSingleShot(True)
    timer.start(10)
    app.exec_()

# end
