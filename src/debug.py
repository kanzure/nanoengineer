# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

'''
debug.py -- debugging functions

Names and behavior partly modelled after code by Sam Rushing in asyncore.py
in the Python library, but this implementation is newly written from scratch;
see PythonDocumentation/ref/types.html for traceback, frame, and code objects,
and sys module documentation about exc_info() and _getframe().

#e Desirable new features:

- print source lines too;

- in compact_stack, include info about how many times each frame has been
previously printed, and/or when it was first seen (by storing something in the
frame when it's first seen, and perhaps incrementing it each time it's seen).

$Id$
'''

import sys, os

# traceback

def print_compact_traceback(msg = "exception ignored: "):
    print >> sys.__stderr__, msg + compact_traceback()

def compact_traceback():
    type, value, traceback = sys.exc_info()
    if (type, value) == (None, None):
        del traceback # even though it should be None
        return "<incorrect call of compact_traceback(): no exception is being handled>"
    try:
        printlines = []
        while traceback:
            # cf. PythonDocumentation/ref/types.html;
            # starting from current stack level (of exception handler),
            # going deeper (towards innermost frame, where exception occurred):
            filename = traceback.tb_frame.f_code.co_filename
            lineno = traceback.tb_lineno
            printlines.append("[%s:%r]" % ( os.path.basename(filename), lineno ))
            traceback = traceback.tb_next
        del traceback
        ctb = '\n'.join(printlines)
        return "%s: %s\n%s" % (type, value, ctb)
    except:
        del traceback
        return "<bug in compact_traceback(); exception from that not shown>"
    pass

# stack

def print_compact_stack( msg = "current stack:\n", skip_innermost_n = 2 ):
    print >> sys.__stderr__, msg + \
          compact_stack( skip_innermost_n = skip_innermost_n )

def compact_stack( skip_innermost_n = 1 ):
    printlines = []
    frame = sys._getframe( skip_innermost_n)
    while frame: # innermost first
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        printlines.append("[%s:%r]" % ( os.path.basename(filename), lineno ))
        frame = frame.f_back
    printlines.reverse() # make it outermost first, like compact_traceback
    return '\n'.join(printlines)

# test code for those -- but more non-test code follows, below this!

if __name__ == '__main__':
    print "see sys.__stderr__ (perhaps a separate console) for test output"
    def f0():
        return f1()
    def f1():
        return f2()
    def f2():
        print_compact_stack("in f2(); this is the stack:\n")
        try:
            f3()
        except:
            print_compact_traceback("exception in f3(): ")
        print >> sys.__stderr__, "done with f2()"
    def f3():
        f4()
    def f4():
        assert 0, "assert 0"
    f0()
    print >> sys.__stderr__, "returned from f0()"
    print "test done"
    pass

# ===

# import some things to make debugging commands more convenient
import sys, os, time

# run python commands from various sorts of integrated debugging UIs (for users who are developers); used in GLPane.py.
# (moved here from GLPane.py by bruce 040928; docstring and messages maybe not yet fixed)

def debug_run_command(command, source = "user debug input"): #bruce 040913-16 in GLPane.py; modified 040928
    """Execute a python command, supplied by the user via some sort of debugging interface (named by source),
       in debug.py's globals. Return 1 for ok (incl empty command), 0 for any error.
       Caller should not print exception diagnostics -- this function does that
       (and does not reraise the exception).
    """
    #e someday we might record time, history, etc
    command = "" + command # i.e. assert it's a string
    #k what's a better way to do the following?
    while command and command[0] == '\n':
        command = command[1:]
    while command and command[-1] == '\n':
        command = command[:-1]
    if not command:
        print "empty command (from %s), nothing executed" % (source,)
        return 1
    if '\n' not in command:
        print "will execute (from %s): %s" % (source, command)
    else:
        nlines = command.count('\n')+1
        print "will execute (from %s; %d lines):\n%s" % (source, nlines, command)
    command = command + '\n' #k probably not needed
    try:
        exec command in globals()
    except:
        print_compact_traceback("exception from that: ")
        return 0
    else:
        print "did it!"
        return 1
    pass

def debug_runpycode_from_a_dialog( source = "some debug menu??"):
    title = "debug: run py code"
    label = "one line of python to exec in debug.py's globals()\n(or use @@@ to fake \\n for more lines)\n(or use execfile)"
    text, ok = QInputDialog.getText(title, label)
    if ok:
        # fyi: type(text) == <class '__main__.qt.QString'>
        command = str(text)
        command = command.replace("@@@",'\n')
        debug_run_command(command, source = source)
    else:
        print "run py code: cancelled"
    return

    
# end
