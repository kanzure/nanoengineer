# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.

'''
debug.py -- debugging functions

(Collects various functions related to debugging.)

$Id$

Names and behavior of some functions here (print_compact_traceback, etc)
are partly modelled after code by Sam Rushing in asyncore.py
in the Python library, but this implementation is newly written from scratch;
see PythonDocumentation/ref/types.html for traceback, frame, and code objects,
and sys module documentation about exc_info() and _getframe().

#e Desirable new features:

- print source lines too;

- in compact_stack, include info about how many times each frame has been
previously printed, and/or when it was first seen (by storing something in the
frame when it's first seen, and perhaps incrementing it each time it's seen).

History:

Created by bruce.

bruce 050913 used env.history in some places.
'''

import sys, os, time, types
from constants import debugButtons, noop
from prefs_constants import QToolButton_MacOSX_Tiger_workaround_prefs_key, mainwindow_geometry_prefs_key_prefix
import env
import platform

from debug_prefs import debug_prefs_menuspec # bruce 050614

# note: some debug features run user-supplied code in this module's
# global namespace (on platforms where this is permitted by our licenses).

# enable the undocumented debug menu by default [bruce 040920]
# (moved here from GLPane, now applies to all widgets using DebugMenuMixin [bruce 050112])
debug_menu_enabled = 1 
debug_events = 0 # set this to 1 to print info about many mouse events

API_ENFORCEMENT = False   # for performance, commit this only as False

class APIViolation(Exception):
    pass

# We compare class names to find out whether calls to private methods
# are originating from within the same class (or one of its friends). This
# could give false negatives, if two classes defined in two different places
# have the same name. A work-around would be to use classes as members of
# the "friends" tuple instead of strings. But then we need to do extra
# imports, and that seems to be not only inefficient, but to sometimes
# cause exceptions to be raised.

def _getClassName(frame):
    """Given a frame (as returned by sys._getframe(int)), dig into
    the list of local variables' names in this stack frame. If the
    frame represents a method call in an instance of a class, then the
    first local variable name will be "self" or whatever was used instead
    of "self". Use that to index the local variables for the frame and
    get the instance that owns that method. Return the class name of
    the instance.
    See http://docs.python.org/ref/types.html for more details.
    """
    varnames = frame.f_code.co_varnames
    selfname = varnames[0]
    methodOwner = frame.f_locals[selfname]
    return methodOwner.__class__.__name__

def _privateMethod(friends=()):
    """Verify that the call made to this method came either from within its
    own class, or from a friendly class which has been granted access. This
    is done by digging around in the Python call stack. The "friends" argument
    should be a tuple of strings, the names of the classes that are considered
    friendly. If no list of friends is given, then any calls from any other
    classes will be flagged as API violations.

    CAVEAT: Detection of API violations is done by comparing only the name of
    the class. (This is due to some messiness I encountered while trying to
    use the actual class object itself, apparently a complication of importing.)
    This means that some violations may not be detected, if we're ever careless
    enough to give two classes the same name.

    ADDITIONAL CAVEAT: Calls from global functions will usually be flagged as API
    violations, and should always be flagged. But this approach will not catch
    all such cases. If the first argument to the function happens to be an
    instance whose class name is the same as the class wherein the private
    method is defined, it won't be caught.
    """
    f1 = sys._getframe(1)
    f2 = sys._getframe(2)
    called = _getClassName(f1)
    caller = _getClassName(f2)
    if caller == called or caller in friends:
        # These kinds of calls are okay.
        return
    # Uh oh, an API violation. Print information that will
    # make it easy to track it down.
    import inspect
    f1 = inspect.getframeinfo(f1)
    f2 = inspect.getframeinfo(f2)
    lineno, meth = f1[1], f1[2]
    lineno2, meth2 = f2[1], f2[2]
    print
    print (called + "." + meth +
           " (line " + repr(lineno) + ")" +
           " is a private method called by")
    print (caller + "." + meth2 +
           " (line " + repr(lineno2) + ")" +
           " in file " + f2[0])
    raise APIViolation

if API_ENFORCEMENT:
    privateMethod = _privateMethod
else:
    # If we're not checking API violations, be as low-impact as possible.
    # In this case 'friends' is ignored.
    def privateMethod(friends=None):
        return

# ==
# Generally useful line number function, wware 051205
def linenum():
    try:
        raise Exception
    except:
        tb = sys.exc_info()[2]
        f = tb.tb_frame.f_back
        print f.f_code.co_filename, f.f_code.co_name, f.f_lineno

# ==
# Enter/leave functions which give performance information

_timing_stack = [ ]

def enter():
    if platform.atom_debug:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            fname = f.f_code.co_name
        _timing_stack.append((fname, time.time()))
        print 'ENTER', fname

def leave():
    if platform.atom_debug:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            fname = f.f_code.co_name
        fname1, start = _timing_stack.pop()
        assert fname == fname1, 'enter/leave mismatch, got ' + fname1 + ', expected ' + fname
        print 'LEAVE', fname, time.time() - start

def middle():
    if platform.atom_debug:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            fname, line = f.f_code.co_name, f.f_lineno
        fname1, start = _timing_stack[-1]
        assert fname == fname1, 'enter/middle mismatch, got ' + fname1 + ', expected ' + fname
        print 'MIDDLE', fname, line, time.time() - start

# ==
def standardExclude(attr, obj):
    from MWsemantics import MWsemantics
    from GLPane import GLPane
    # I am rarely interested in peeking inside these, and they create
    # tons of output.
    return isinstance(obj, MWsemantics) or isinstance(obj, GLPane)

class ObjectDescender:
    def __init__(self, maxdepth, outf=sys.stderr):
        self.already = [ ]
        self.maxdepth = maxdepth
        self.outf = outf

    def exclude(self, attr, obj):
        return False
    def showThis(self, attr, obj):
        return True

    def prefix(self, depth, pn):
        return ((depth * "\t") + ".".join(pn) + ": ")

    def handleLeaf(self, v, depth, pn):
        def trepr(v):
            if v == None:
                return "None"
            elif type(v) == types.InstanceType:
                r = v.__class__.__name__
            else:
                r = repr(type(v))
            return "%s at %x" % (r, id(v))
        if type(v) in (types.ListType, types.TupleType):
            self.outf.write(self.prefix(depth, pn) + trepr(v))
            if len(v) == 0:
                self.outf.write(" (empty)")
            self.outf.write("\n")
        elif type(v) in (types.StringType, types.IntType,
                         types.FloatType, types.ComplexType):
            self.outf.write(self.prefix(depth, pn) + repr(v) + "\n")
        else:
            self.outf.write(self.prefix(depth, pn) + trepr(v) + "\n")

    def getAttributes(self, obj):
        lst = dir(obj)
        if hasattr(obj, "__dict__"):
            for x in obj.__dict__.keys():
                if x not in lst:
                    lst.append(x)
        lst.sort()
        def filt(x):
            return x not in ("__doc__",)
        return filter(filt, lst)

    def descend(self, obj, depth=0, pathname=[ ]):
        if obj in self.already:
            return
        self.already.append(obj)
        if depth == 0:
            self.handleLeaf(obj, depth, pathname)
        if depth >= self.maxdepth:
            return
        if type(obj) in (types.ListType, types.TupleType):
            lst = [ ]
            if len(pathname) > 0:
                lastitem = pathname[-1]
                pathname = pathname[:-1]
            else:
                lastitem = ""
            for i in range(len(obj)):
                x = obj[i]
                if not self.exclude(i, x):
                    y = pathname + [ lastitem + ("[%d]" % i) ]
                    lst.append((i, x, y))
            for i, v, pn in lst:
                if self.showThis(i, v):
                    self.handleLeaf(v, depth+1, pn)
            for i, v, pn in lst:
                self.descend(v, depth+1, pn)
        elif type(obj) in (types.DictType,):
            keys = obj.keys()
            lst = [ ]
            if len(pathname) > 0:
                lastitem = pathname[-1]
                pathname = pathname[:-1]
            else:
                lastitem = ""
            for k in keys:
                x = obj[k]
                if not self.exclude(k, x):
                    y = pathname + [ lastitem + ("[%s]" % repr(k)) ]
                    lst.append((k, x, y))
            for k, v, pn in lst:
                if self.showThis(k, v):
                    self.handleLeaf(v, depth+1, pn)
            for k, v, pn in lst:
                self.descend(v, depth+1, pn)
        elif (hasattr(obj, "__class__") or
            type(obj) in (types.InstanceType, types.ClassType,
                          types.ModuleType, types.FunctionType)):
            ckeys = [ ]
            if True:
                # Look at instance variables, ignore class variables and methods
                if hasattr(obj, "__class__"):
                    ckeys = self.getAttributes(obj.__class__)
            else:
                # Look at all variables and methods
                ckeys = ( )
            keys = filter(lambda x: x not in ckeys, self.getAttributes(obj))
            lst = [ ]
            for k in keys:
                x = getattr(obj, k)
                if not self.exclude(k, x):
                    lst.append((k, x, pathname + [ k ]))
            for k, v, pn in lst:
                if self.showThis(k, v):
                    self.handleLeaf(v, depth+1, pn)
            for k, v, pn in lst:
                self.descend(v, depth+1, pn)

def objectBrowse(obj, maxdepth=5, exclude=standardExclude, showThis=None, outf=sys.stderr):
    od = ObjectDescender(maxdepth=maxdepth, outf=outf)
    if showThis != None:
        od.showThis = showThis
    od.exclude = exclude
    od.descend(obj, pathname=['arg'])

def findChild(obj, showThis, maxdepth=8):
    # Drill down deeper because we're being more selective
    def prefix(depth, pn):
        # no indentation
        return (".".join(pn) + ": ")
    f = Finder(maxdepth=maxdepth)
    f.showThis = showThis
    f.prefix = prefix
    f.descend(obj, pathname=['arg'])

# python -c "import debug; debug.testDescend()"
def testDescend():
    class Foo:
        pass
    x = Foo()
    y = Foo()
    z = Foo()
    x.a = 3.14159
    x.b = "When in the course of human events"
    x.c = y
    x.d = [3,1,4,1,6]
    y.a = 2.71828
    y.b = "Apres moi, le deluge"
    y.c = z
    z.a = [x, y, z]
    z.b = range(12)
    x.e = {'y': y, 'z': z}
    objectBrowse(x)
    def test(name, val):
        return name == "a"
    findChild(x, test)


# ==

# Stopwatch for measuring run time of algorithms or code snippets.
# wware 051104
class Stopwatch:
    def __init__(self):
        self.__marks = [ ]
    def start(self):
        self.__start = time.time()
    def mark(self):
        self.__marks.append(time.time() - self.__start)
    def getMarks(self):
        return self.__marks
    def now(self):
        return time.time() - self.__start

def time_taken(func): #bruce 051202 moved this here from undo.py
    "call func and measure how long this takes. return a triple (real-time-taken, cpu-time-taken, result-of-func)."
    from time import time, clock
    t1c = clock()
    t1t = time()
    res = func()
    t2c = clock()
    t2t = time()
    return (t2t - t1t, t2c - t1c, res)

def call_func_with_timing_histmsg( func): #bruce 051202 moved this here from undo.py
    realtime, cputime, res = time_taken(func)
    env.history.message( "done; took %0.4f real secs, %0.4f cpu secs" % (realtime, cputime) )
    return res

# ==

# the following are needed to comply with our Qt/PyQt license agreements.

def legally_execfile_in_globals(filename, globals, error_exception = True):
    """if/as permitted by our Qt/PyQt license agreements,
    execute the python commands in the given file, in this process.
    """
    try:
        import gpl_only
    except ImportError:
        msg = "execfile(%r): not allowed in this non-GPL version" % (filename,)
        print msg #e should be in a dialog too, maybe depending on an optional arg
        if error_exception:
            raise ValueError, msg
        else:
            print "ignoring this error, doing nothing (as if the file was empty)"
    else:
        gpl_only._execfile_in_globals(filename, globals) # this indirection might not be needed...
    return

def legally_exec_command_in_globals( command, globals, error_exception = True ):
    """if/as permitted by our Qt/PyQt license agreements,
    execute the given python command (using exec) in the given globals,
    in this process.
    """
    try:
        import gpl_only
    except ImportError:
        msg = "exec is not allowed in this non-GPL version"
        print msg #e should be in a dialog too, maybe depending on an optional arg
        print " fyi: the command we hoped to exec was: %r" % (command,)
        if error_exception:
            raise ValueError, msg
        else:
            print "ignoring this error, doing nothing (as if the command was a noop)"
    else:
        gpl_only._exec_command_in_globals( command, globals) # this indirection might not be needed...
    return

def exec_allowed():
    "are exec and/or execfile allowed in this version?"
    try:
        import gpl_only
    except ImportError:
        return False
    return True

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
        while traceback is not None:
            # cf. PythonDocumentation/ref/types.html;
            # starting from current stack level (of exception handler),
            # going deeper (towards innermost frame, where exception occurred):
            filename = traceback.tb_frame.f_code.co_filename
            lineno = traceback.tb_lineno
            printlines.append("[%s:%r]" % ( os.path.basename(filename), lineno ))
            traceback = traceback.tb_next
        del traceback
        ctb = ' '.join(printlines)
        return "%s: %s\n  %s" % (type, value, ctb)
    except:
        del traceback
        return "<bug in compact_traceback(); exception from that not shown>"
    pass

# stack

def print_compact_stack( msg = "current stack:\n", skip_innermost_n = 2 ):
    print >> sys.__stderr__, msg + \
          compact_stack( skip_innermost_n = skip_innermost_n )

STACKFRAME_IDS = False # don't commit with True,
    # but set to True in debugger to see more info in compact_stack printout [bruce 060330]

def compact_stack( skip_innermost_n = 1 ):
    printlines = []
    frame = sys._getframe( skip_innermost_n)
    while frame is not None: # innermost first
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        extra = ""
        if STACKFRAME_IDS:
            #bruce 060330
            # try 1 failed
##            try:
##                frame._CS_seencount # this exception messed up some caller, so try getattr instead... no, that was not what happened
##            except:
##                frame._CS_seencount = 1
##            else:
##                frame._CS_seencount += 1
            # try 2 failed - frame object doesn't permit arbitrary attrs to be set on it
##            count = getattr(frame, '_CS_seencount', 0)
##            count += 1
##            print frame.f_locals
##            frame._CS_seencount = count # this is not allowed. hmm.
            # so we'll store a new fake "local var" into the frame, assuming frame.f_locals is an ordinary dict
            count = frame.f_locals.get('_CS_seencount', 0)
            count += 1
            frame.f_locals['_CS_seencount'] = count
            if count > 1:
                extra = "|%d" % count
        printlines.append("[%s:%r%s]" % ( os.path.basename(filename), lineno, extra ))
        frame = frame.f_back
    printlines.reverse() # make it outermost first, like compact_traceback
    return ' '.join(printlines)

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

# run python commands from various sorts of integrated debugging UIs
# (for users who are developers); used in GLPane.py [or in code farther below
#  which used to live in GLPane.py].
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
        msg = "will execute (from %s): %s" % (source, command)
    else:
        nlines = command.count('\n')+1
        msg = "will execute (from %s; %d lines):\n%s" % (source, nlines, command)
    print msg
    try:
        # include in history file, so one can search old history files for useful things to execute [bruce 060409]
        import env
        from HistoryWidget import _graymsg, quote_html
        env.history.message( _graymsg( quote_html( msg)))
    except:
        print_compact_traceback("exception in printing that to history: ")
    command = command + '\n' #k probably not needed
    try:
        ## exec command in globals()
        legally_exec_command_in_globals( command, globals() )
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
    from qt import QInputDialog # bruce 041216 bugfix
    text, ok = QInputDialog.getText(title, label)
    if ok:
        # fyi: type(text) == <class '__main__.qt.QString'>
        command = str(text)
        command = command.replace("@@@",'\n')
        debug_run_command(command, source = source)
    else:
        print "run py code: cancelled"
    return

def debug_hackNanotubes_from_a_dialog( source = "some debug menu??", nanotubeIndex=[ 1 ]):
    title = "debug: SW/MW/HJ nanotubes"
    label = "put in parameters, e.g. 'SW 20 0 30 1' or\n'HJ 20 10 20 5 0 20 1' or\n'MW 20 5 15 3 5 1'"
    from qt import QInputDialog
    text, ok = QInputDialog.getText(title, label)
    # text contains both the command name (might need to end with .exe on Windows) and the arguments
    if ok:
        from platform import find_or_make_Nanorex_subdir
        from HistoryWidget import redmsg
        contubPath = find_or_make_Nanorex_subdir('CoNTub')
        ntmmp = os.path.join(contubPath, "nt.mmp")
        # fyi: type(text) == <class '__main__.qt.QString'>
        command = os.path.join(contubPath, str(text))
            # kluge: spaces in text are treated here as part of a file basename, but won't be quoted
        command += (' %d > ' % nanotubeIndex[0]) + ntmmp #guess: this means last argument is used to help form a nodename in nt.mmp
	print "System command: [", command, "]"
        if os.system(command) == 0: #k Windows?
            from files_mmp import insertmmp
            nanotubeIndex[0] += 1
            w = env.mainwindow()
            assy = w.assy
            glpane = w.glpane
            try:
                insertmmp(assy, ntmmp)
                glpane.scale = assy.bbox.scale()
                w.win_update()
            except:
                print_compact_traceback( "Error inserting MMP file [%s]: " % ntmmp )
                env.history.message( redmsg( "Error while inserting MMP file: " + ntmmp) )
            else:
                assy.changed() #k needed?
                env.history.message( "MMP file inserted: " + ntmmp )
        else:
            env.history.message(redmsg("Command failed: \"" + command + "\""))
    else:
        print "hack graphene structures: cancelled"
    return

# ==

def debug_timing_test_pycode_from_a_dialog( ): #bruce 051117
    title = "debug: time python code"
    label = "one line of python to compile and exec REPEATEDLY in debug.py's globals()\n(or use @@@ to fake \\n for more lines)"
    from qt import QInputDialog
    text, ok = QInputDialog.getText(title, label)
    if not ok:
        print "time python code code: cancelled"
        return
    # fyi: type(text) == <class '__main__.qt.QString'>
    command = str(text)
    command = command.replace("@@@",'\n')
    print "trying to time the exec or eval of command:",command
    from code import compile_command
    try:
        try:
            mycode = compile( command + '\n', '<string>', 'exec') #k might need '\n\n' or '' or to be adaptive in length?
            # 'single' means print value if it's an expression and value is not None; for timing we don't want that so use 'eval'
            # or 'exec' -- but we don't know which one is correct! So try exec, if that fails try eval.
            print "exec" # this happens even for an expr like 2+2 -- why?
        except SyntaxError:
            print "try eval" # i didn't yet see this happen
            mycode = compile_command( command + '\n', '<string>', 'eval')
    except:
        print_compact_traceback("exception in compile_command: ")
        return
    if mycode is None:
        print "incomplete command:",command
        return
    # mycode is now a code object
    print_exec_timing_explored(mycode)

def print_exec_timing_explored(mycode, ntimes = 1, trymore = True): #bruce 051117
    """After making sure exec of user code is legally permitted, and exec of mycode works,
    execute mycode ntimes and print how long that takes in realtime (in all, and per command).
    If it took <1 sec and trymore is True, repeat with ntimes *= 4, repeatedly until it took >= 1 sec.
    """
    glob = globals()
    legally_exec_command_in_globals( mycode, glob )
    # if we get to here, exec of user code is legally permitted, and mycode threw no exception,
    # so from now on we can say "exec mycode in glob" directly.
    toomany = 10**8
    while 1:
        timetook = print_exec_timing(mycode, ntimes, glob) # print results, return time it took in seconds
        if trymore and timetook < 1.0:
            if ntimes > toomany:
                print "%d is too many to do more than, even though it's still fast. (bug?)" % ntimes
                break
            ntimes *= 4
            continue
        else:
            break
    print "done"
    return

def print_exec_timing(mycode, ntimes, glob): #bruce 051117
    """Execute mycode in glob ntimes and print how long that takes in realtime (in all, and per command).
    Return total time taken in seconds (as a float). DON'T CALL THIS ON USER CODE UNTIL ENSURING OUR LICENSE
    PERMITS EXECUTING USER CODE in the caller; see print_exec_timing_explored for one way to do that.
    """
    start = time.time()
    for i in xrange(ntimes):
        exec mycode in glob
    end = time.time()
    took = float(end - start)
    tookper = took / ntimes
    print "%d times: total time %f, time per call %f" % (ntimes, took, tookper)
    return took

# ==

#bruce 050823 preliminary system for letting other modules register commands for debug menu (used by Undo experimental code)
# revised/generalized 050923 [committed 051006]

_commands = {}

class menu_cmd: #bruce 050923 [committed 051006]. #e maybe the maker option should be turned into a subclass-choice... we'll see.
    "public attrs: name, order"
    def __init__(self, name, func, order = None, maker = False, text = None):
        "for doc of args see register_debug_menu_command"
        # public attrs: 
        self.name = name # self.name is used for replacement of previous same-named commands in client-maintained sets
            # (but the name arg is also used as default value for some other attrs, below)
        self.func = func
        self.maker = not not maker # if true, some of the rest don't matter, but never mind
        if order is not None:
            self.order = (0, order)
        else:
            self.order = (1, name) # unordered ones come after ordered ones, and are sorted by name
        self.text = text or name # text of None or "" is replaced by name
            # self.text won't be used if maker is true
        return
    def menu_spec(self, widget):
        if self.maker:
            try:
                res = self.func(widget) # doesn't need the other attrs, I think... tho passing self might someday be useful #e
            except:
                print_compact_traceback("exception in menu_spec: ")
                try:
                    errmsg = 'exception in menu_spec for %r' % (self.name,)
                except:
                    errmsg = 'exception in menu_spec'
                return [(errmsg, noop, 'disabled')]
            #e should also protect caller from badly formatted value... or maybe menu spec processor should do that?
            return res
        text, func = self.text, self.func
        return [ (text, lambda func=func, widget=widget: func(widget)) ]    
            # (the func=func was apparently necessary, otherwise the wrong func got called,
            #  always the last one processed here)
            # [that comment is from before revision of 050923 but probably still applies]
    pass

def register_debug_menu_command( *args, **kws ):
    """Let other modules register commands which appear in the debug menu.
    When called, they get one arg, the widget in which the debug menu appeared.
       If order is supplied and not None, it's used to sort the commands in the menu
    (the other ones come at the end in order of their names).
       Duplicate names cause prior-registered commands to be silently replaced
    (even if other options here cause names to be ignored otherwise).
       If text is supplied, it rather than name is the menu-text. (Name is still used for replacement and maybe sorting.)
       If maker is true [experimental feature], then func is not the command but the sub-menu-spec maker,
    which runs (with widget as arg) when menu is put up, and returns a menu-spec list;
    in this case name is ignored except perhaps for sorting purposes.
    """
    cmd = menu_cmd( *args, **kws )
    _commands[cmd.name] = ( cmd.order, cmd )
        # store by .name so duplicate names cause replacement;
        # let values be sortable by .order
    return

def register_debug_menu_command_maker( *args, **kws): # guess: maker interface is better as a separate function.
    assert not kws.has_key('maker')
    kws['maker'] = True
    assert not kws.has_key('text') # since not useful for maker = True
    register_debug_menu_command( *args, **kws)
    return

def registered_commands_menuspec( widget):
    order_cmd_pairs = _commands.values()
    order_cmd_pairs.sort()
    spec = []
    for orderjunk, cmd in order_cmd_pairs:
        spec.extend( cmd.menu_spec(widget) )
    if not spec:
        return spec # i.e. []
    return [ ('other', spec) ]

# ==

# Mixin class to help some of our widgets offer a debug menu.
# [split from some GLPane methods and moved here by bruce 050112]

class DebugMenuMixin:
    """Helps widgets have the "standard undocumented debug menu".
    Provides some methods and attrs to its subclasses,
    all starting debug or _debug, especially self.debug_event().
    Caller of _init1 should provide main window win, or [temporary kluge?]
    let this be found at self.win; some menu items affect it or emit
    history messages to it.
    [As of 050913 they should (and probably do) no longer use win for history,
    but use env.history instead.]
    """
    #doc better
    #e rename private attrs to start with '_debug' instead of 'debug'
    #e generalize so the debug menu can be customized? not sure it's needed.

    ## debug_menu = None # needed for use before _init1 or if that fails
    
    def _init1(self, win = None):
        # figure out this mixin's idea of main window
        if not win:
            try:
                self.win # no need: assert isinstance( self.win, QWidget)
            except AttributeError:
                pass
            else:
                win = self.win
        self._debug_win = win
        # figure out classname for #doc
        try:
            self._debug_classname = "class " + self.__class__.__name__
        except:
            self._debug_classname = "<some class>"
        # make the menu -- now done each time it's needed
        return

    def makemenu(self, menu_spec): # bruce 050304 added this, so subclasses no longer have to
        """Make and return a menu object for use in this widget, from the given menu_spec.
        [This can be overridden by a subclass, but probably never needs to be,
        unless it needs to make *all* menus differently (thus we do use the overridden
        version if one is present) or unless it uses it independently from this mixin
        and wants to be self-contained.]
        """
        from widgets import makemenu_helper
        return makemenu_helper(self, menu_spec)
    
    def debug_menu_items(self):
        """#doc; as of 050416 this will be called every time the debug menu needs to be put up,
        so that the menu contents can be different each time (i.e. so it can be a dynamic menu)
        [subclasses can override this; best if they call this superclass method
        and modify its result, e.g. add new items at top or bottom]
        """
        import debug
        res = [
            ('debugging menu (unsupported)', noop, 'disabled'), #bruce 060327 revised text
            # None, # separator
        ]
        if 0 and self._debug_win: #bruce 060327 disabled this, superseded by prefs dialog some time ago
            res.extend( [
                ('load window layout', self._debug_load_window_layout ),
                ('save window layout', self._debug_save_window_layout ),
                    #bruce 050117 prototype "save window layout" here; when it works, move it elsewhere
            ] )
        if debug.exec_allowed():
            #bruce 041217 made this item conditional on whether it will work
            res.extend( [
                ('run py code', self._debug_runpycode),
                ('SW/MW/HJ nanotubes', self._debug_hackNanotubes),
                ('speed-test py code', self._debug_timepycode), #bruce 051117; include this even if not platform.atom_debug
            ] )
        #bruce 050416: use a "checkmark item" now that we're remaking this menu dynamically:
        import platform
        if platform.atom_debug:
            res.extend( [
                ('ATOM_DEBUG', self._debug_disable_atom_debug, 'checked' ),
            ] )
        else:
            res.extend( [
                ('ATOM_DEBUG', self._debug_enable_atom_debug ),
            ] )

        if (sys.platform == 'darwin' or platform.atom_debug) and self._debug_win:
            #bruce 050806 to give Alpha6 a workaround for Mac OS X 10.4 Tiger QToolButton bug
            #bruce 050810 use checkmark item to let that be a persistent pref,
            # and provide this on all platforms when ATOM_DEBUG is set
            # (so we can see if it works and we like it, on other systems)
            checked = env.prefs[QToolButton_MacOSX_Tiger_workaround_prefs_key]
            res.extend( [
                ('Mac OS 10.4 QToolButton workaround', self._debug_toggle_QToolButton_workaround, checked and 'checked' or None ),
            ] )
        
        #bruce 060124 changes: always call debug_prefs_menuspec, but pass platform.atom_debug to filter the prefs,
        # and change API to return a list of menu items (perhaps empty) rather than exactly one
        res.extend( debug_prefs_menuspec( platform.atom_debug ) ) #bruce 050614 (submenu)

        if 1: #bruce 050823
            some = registered_commands_menuspec( self)
            res.extend(some)
        
        res.extend( [
            ('choose font', self._debug_choose_font),
        ] )
        if self._debug_win:
            res.extend( [
                ('call update_parts()', self._debug_update_parts ), ###e also should offer check_parts
            ] )

        if 1: #bruce 060327; don't show them in the menu itself, we need to see them in time, in history, with and without atom_debug
            res.extend( [
                ('print object counts', self._debug_print_object_counts),
            ] )
        
        res.extend( [
            ('print self', self._debug_printself),
        ] )
        if platform.atom_debug: # since it's a dangerous command
            res.extend( [
                ('debug._widget = this widget', self._debug_set_widget),
                ('destroy this widget', self._debug_destroy_self),
            ] )
        return res

    def _debug_save_window_layout(self): # [see also UserPrefs.save_current_win_pos_and_size, new as of 051218]
        from platform import save_window_pos_size
        win = self._debug_win
        keyprefix = mainwindow_geometry_prefs_key_prefix
        save_window_pos_size( win, keyprefix)

    def _debug_load_window_layout(self): # [similar code is in pre_main_show in startup_funcs.py, new as of 051218]
        from platform import load_window_pos_size
        win = self._debug_win
        keyprefix = mainwindow_geometry_prefs_key_prefix
        load_window_pos_size( win, keyprefix)

    def _debug_update_parts(self):
        win = self._debug_win
        win.assy.update_parts()

    def _debug_print_object_counts(self):
        #bruce 060327 for debugging memory leaks: report Atom & Bond refcounts, and objs that might refer to them
        from HistoryWidget import _graymsg
        msglater = "" # things to print all in one line
        for clasname, modulename in (
                ('Atom', 'chem'),
                 ('Bond', 'bonds'),
                 # ('Node', 'Utility'), # Node or Jig is useless here, we need the specific subclasses!
                 ('Chunk', 'chunk'),
                 ## ('PiBondSpChain', 'pi_bond_sp_chain'), # no module pi_bond_sp_chain -- due to lazy load or atom-debug reload??
                 ('Group', 'Utility'), # doesn't cover subclasses PartGroup, ClipboardItemGroup, RootGroup(sp?)
                 ('Part', 'part'),
                 ('Assembly', 'assembly')):
            # should also have a command to look for other classes with high refcounts
            if sys.modules.has_key(modulename):
                module = sys.modules[modulename]
                clas = getattr(module, clasname, None)
                if clas:
                    msg = "%d %ss" % (sys.getrefcount(clas), clasname)
                    msg = msg.replace("ys","ies") # for spelling of Assemblies
                    # print these things all at once
                    if msglater:
                        msglater += ', '
                    msglater += msg
                    msg = None
                else:
                    msg = "%s not found in %s" % (clasname, modulename)
            else:
                msg = "no module %s" % (modulename,)
            if msg:
                env.history.message( _graymsg( msg))
        if msglater:
            env.history.message( _graymsg( msglater))
        return
    
    def _debug_choose_font(self): #bruce 050304 experiment; works; could use toString/fromString to store it in prefs...
        oldfont = self.font()
        from qt import QFontDialog
        newfont, ok = QFontDialog.getFont(oldfont)
            ##e can we change QFontDialog to let us provide initial sample text,
            # and permit typing \n into it? If not, can we fool it by providing
            # it with a fake "paste" event?
        if ok:
            self.setFont(newfont)
            try:
                import platform
                if platform.atom_debug:
                    print "atom_debug: new font.toString():", newfont.toString()
            except:
                print_compact_traceback("new font.toString() failed: ")
        return
    
    def _debug_enable_atom_debug(self):
        import platform
        platform.atom_debug = 1
    
    def _debug_disable_atom_debug(self):
        import platform
        platform.atom_debug = 0
    
    def debug_event(self, event, funcname, permit_debug_menu_popup = 0): #bruce 040916
        """[the main public method for subclasses]
           Debugging method -- no effect on normal users.  Does two
           things -- if a global flag is set, prints info about the
           event; if a certain modifier key combination is pressed,
           and if caller passed permit_debug_menu_popup = 1, puts up
           an undocumented debugging menu, and returns 1 to caller.
              Modifier keys to bring it up:
           Mac: Shift-Option-Command-click
           Linux: <cntrl><shift><alt><left click>
           Windows: probably same as linux
        """
        # In constants.py: debugButtons = cntlButton | shiftButton | altButton
        # On the mac, this really means command-shift-alt [alt == option].
        if debug_menu_enabled and permit_debug_menu_popup and ((event.state() & debugButtons) == debugButtons):
            ## print "\n* * * fyi: got debug click, will try to put up a debug menu...\n" # bruce 050316 removing this
            self.do_debug_menu(event)
            return 1 # caller should detect this and not run its usual event code...
        if debug_events:
            try:
                after = event.stateAfter()
            except:
                after = "<no stateAfter>" # needed for Wheel events, at least
            print "%s: event; state = %r, stateAfter = %r; time = %r" % (funcname, event.state(), after, time.asctime())
            
        # It seems, from doc and experiments, that event.state() is
        # from just before the event (e.g. a button press or release,
        # or move), and event.stateAfter() is from just after it, so
        # they differ in one bit which is the button whose state
        # changed (if any).  But the doc is vague, and the experiments
        # incomplete, so there is no guarantee that they don't
        # sometimes differ in other ways.
        # -- bruce ca. 040916
        return 0

    def do_debug_menu(self, event):
        "[public method for subclasses] #doc"
        ## menu = self.debug_menu
        #bruce 050416: remake the menu each time it's needed
        menu = None
        try:
            menu_spec = "<not yet computed>" # might be needed for error message in 'except' clause [bruce 050509 bugfix]
            menu_spec = self.debug_menu_items()
            menu = self.makemenu( menu_spec ) # might be []
        except:
            print_compact_traceback("bug in do_debug_menu ignored; menu_spec is %r" % (menu_spec,) )
            menu = None # for now
        
        ## removed [bruce 050416] since badly named and not yet used:
        ## self.current_event = event # (so debug commands can see it)
        if menu:
            menu.exec_loop(event.globalPos(), 1)
        ## self.current_event = None
        return 1

    def _debug_printself(self):
        print self

    def _debug_set_widget(self): #bruce 050604
        import debug
        debug._widget = self
        print "set debug._widget to",self
    
    def _debug_destroy_self(self): #bruce 050604
        #e should get user confirmation
        ## self.destroy() ###k this doesn't seem to work. check method name.
        self.deleteLater()

    def debug_menu_source_name(self): #bruce 050112
        "can be overriden by subclasses" #doc more
        try:
            return "%s debug menu" % self.__class__.__name__
        except:
            return "some debug menu"

    def _debug_runpycode(self):
        from debug import debug_runpycode_from_a_dialog
        debug_runpycode_from_a_dialog( source = self.debug_menu_source_name() )
            # e.g. "GLPane debug menu"
        return

    def _debug_hackNanotubes(self):
        from debug import debug_hackNanotubes_from_a_dialog
        debug_hackNanotubes_from_a_dialog( source = self.debug_menu_source_name() )
            # e.g. "GLPane debug menu"
        return

    def _debug_timepycode(self): #bruce 051117
        ## from debug import debug_timing_test_pycode_from_a_dialog
        debug_timing_test_pycode_from_a_dialog( )
        return

    def _debug_toggle_QToolButton_workaround(self): #bruce 050806, revised 050810
        """[only provided in menu on Mac (or maybe on all systems when ATOM_DEBUG is set),
        and only needed for Mac OS X 10.4 Tiger, but might work for all platforms -- who knows]
        """
        enabled_now = env.prefs[QToolButton_MacOSX_Tiger_workaround_prefs_key]
        enable = not enabled_now
        from HistoryWidget import orangemsg, redmsg, greenmsg
        if enable:
            ###e ask user if ok; if we add that feature, also add "..." to menu command text
            # note: if we enable, disable, and enable, all in one session, the following happens twice, but that's ok.
            env.history.message( greenmsg( "Modifying every QToolButton to work around a Qt bug in Mac OS X 10.4 Tiger..." ))
            from widget_hacks import hack_every_QToolButton, hack_every_QToolButton_warning
            if hack_every_QToolButton_warning:
                env.history.message( orangemsg( hack_every_QToolButton_warning ))
            hack_every_QToolButton( self._debug_win )
            env.prefs[QToolButton_MacOSX_Tiger_workaround_prefs_key] = True
            env.history.message( "Done. This will be redone automatically in new sessions (with no history message)" \
                                 " unless you disable this menu item.")
            # see auto_enable_MacOSX_Tiger_workaround_if_desired and its call, for how it gets enabled in new sessions.
        else:
            env.prefs[QToolButton_MacOSX_Tiger_workaround_prefs_key] = False
            env.history.message( orangemsg(
                "Disabled the workaround for the QToolButton bug in Mac OS X 10.4 Tiger." \
                " This change in pressed toolbutton appearance will only take effect" \
                " after you quit and restart this program." ))
        return
        
    pass # end of class DebugMenuMixin

def auto_enable_MacOSX_Tiger_workaround_if_desired( win): #bruce 050810
    enable = env.prefs[QToolButton_MacOSX_Tiger_workaround_prefs_key]
    if enable:
        from widget_hacks import hack_every_QToolButton
        hack_every_QToolButton( win)
    return

# ===

def overridden_attrs( class1, instance1 ): #bruce 050108
    "return a list of the attrs of class1 which are overridden by instance1"
    # probably works for class1, subclass1 too [untested]
    res = []
    for attr in dir(class1):
        ca = getattr(class1, attr)
        ia = getattr(instance1, attr)
        if ca != ia:
            try:
                # is ca an unbound instance method, and ia its bound version for instance1?
                if ia.im_func == ca.im_func:
                    # (approximate test; could also verify the types and the bound object in ia #e)
                    # (note: im_func seems to work for both unbound and bound methods; #k py docs)
                    continue
            except AttributeError:
                pass
            res.append(attr)
    return res

# ==

def reload_once_per_event(module):
    """Reload module (given as object or as name),
    but at most once per user-event or redraw, and only if platform.atom_debug.
    Assumes w/o checking that this is a module it's ok to reload.
    """
    import platform
    if not platform.atom_debug:
        return
    if type(module) == type(""):
        # also support module names
        module = sys.modules[module]
    now = env.redraw_counter
    try:
        old = module.redraw_counter_when_reloaded
    except AttributeError:
        old = -1
    if old == now:
        return
    if old == 'never again': #bruce 060304
        return
    assert sys.modules[module.__name__] is module
    module.redraw_counter_when_reloaded = now # do first in case of exceptions in this or below
    if old == -1:
        print "reloading",module.__name__
        print "  (and will do so up to once per redraw w/o saying so again)"
    try:
        reload(module)
    except:
        #bruce 060304 added try/except in case someone sets ATOM_DEBUG in an end-user version
        # in which reload is not supported. We could check for "enabling developer features",
        # but maybe some end-user versions do support reload, and for them we might as well do it here.
        # Note: the except clause (and its 'never again' feature) is untested.
        print_compact_traceback("reload failed (not supported in this version?); continuing: ")
        module.redraw_counter_when_reloaded = 'never again'
    return

# ==

#bruce 050823 - this is a convenient place to import some Undo experimental code --
# though it's not a sensible permanent place for that ####@@@@

import undo

#bruce 051202 - same for extensions.py (which tests Pyrex code, for now; later handles all our custom extension modules)

import extensions

# don't add custom display mode imports here -- add them to _initialize_custom_display_modes() in startup_funcs.py. [bruce 060609]

import chem_patterns

# end
