# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
debug.py -- various debugging utilities and debug-related UI code

TODO: split into several modules in a debug package.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

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

Created by Bruce. Added to by various developers, especially Will.

Bruce 071107 split out two modules by Will:
- objectBrowse.py 
- scratch/api_enforcement.py 

"""

import sys, os, time, traceback
from utilities.constants import noop
import foundation.env as env
from utilities import debug_flags

# note: some debug features run user-supplied code in this module's
# global namespace (on platforms where this is permitted by our licenses).

# ==

_default_x = object()

def print_verbose_traceback(x = _default_x):
    traceback.print_stack(file = sys.stdout)
    if x is not _default_x:
        print x
    print

# ==

# Generally useful line number function, wware 051205
def linenum(depth = 0):
    try:
        raise Exception
    except:
        tb = sys.exc_info()[2]
        f = tb.tb_frame
        for i in range(depth + 1):
            f = f.f_back
        print f.f_code.co_filename, f.f_code.co_name, f.f_lineno

# ==

# Enter/leave functions which give performance information
# (by Will; bruce 071107 renamed them to be easier to search for.)

_timing_stack = [ ]

def debug_enter():
    if debug_flags.atom_debug:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            fname = f.f_code.co_name
        _timing_stack.append((fname, time.time()))
        print 'ENTER', fname

def debug_leave():
    if debug_flags.atom_debug:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            fname = f.f_code.co_name
        fname1, start = _timing_stack.pop()
        assert fname == fname1, 'enter/leave mismatch, got ' + fname1 + ', expected ' + fname
        print 'LEAVE', fname, time.time() - start

def debug_middle():
    if debug_flags.atom_debug:
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

# usage:
#    start = begin_timing("description of stuff")
#    ...stuff to be timed...
#    end_timing(start, "description of stuff")
def begin_timing(msg = ""):
    print "begin_timing: %s" % msg
    return time.time()

def end_timing(start, msg = ""):
    print "end_timing: %s %s" % (msg, time.time() - start)

def time_taken(func):
    """
    call func and measure how long this takes.

    @return: a triple (real-time-taken, cpu-time-taken, result-of-func),
             but see warning for a caveat about the cpu time measurement.

    @warning: we measure cpu time using time.clock(), but time.clock() is
              documented as returning "the CPU time or real time since the
              start of the process or since the first call to clock()."
              Tests show that on Mac it probably returns CPU time. We have
              not tested this on other platforms.
    """
    t1c = time.clock()
    t1t = time.time()
    res = func()
    t2c = time.clock()
    t2t = time.time()
    return (t2t - t1t, t2c - t1c, res)

def call_func_with_timing_histmsg( func):
    realtime, cputime, res = time_taken(func)
    env.history.message( "done; took %0.4f real secs, %0.4f cpu secs" % (realtime, cputime) )
    return res

# ==

# the following are needed to comply with our Qt/PyQt license agreements.
# [in Qt4, all-GPL, they work on all platforms, as of 070425]

def legally_execfile_in_globals(filename, globals, error_exception = True):
    """
    if/as permitted by our Qt/PyQt license agreements,
    execute the python commands in the given file, in this process.
    """
    try:
        import platform_dependent.gpl_only as gpl_only
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
    """
    if/as permitted by our Qt/PyQt license agreements,
    execute the given python command (using exec) in the given globals,
    in this process.
    """
    try:
        import platform_dependent.gpl_only as gpl_only
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
    """
    are exec and/or execfile allowed in this version of NE1?
    """
    try:
        import platform_dependent.gpl_only as gpl_only
    except ImportError:
        return False
    return True

# ==

def safe_repr(obj, maxlen = 1000):
    # fyi: this import doesn't work: from asyncore import safe_repr
    try:
        maxlen = int(maxlen)
        assert maxlen >= 5
    except:
        #e should print once-per-session error message & compact_stack (using helper function just for that purpose)
        maxlen = 5
    try:
        rr = "%r" % (obj,)
    except:
        rr = "<repr failed for id(obj) = %#x, improve safe_repr to print its class at least>" % id(obj)
    if len(rr) > maxlen:
        return rr[(maxlen - 4):] + "...>" #e this should also be in a try/except; even len should be
    else:
        return rr
    pass

# ==

# traceback / stack utilities (see also print_verbose_traceback)

def print_compact_traceback(msg = "exception ignored: "):
    print >> sys.__stderr__, msg + compact_traceback() # bruce 061227 changed this back to old form
    return
    ## import traceback
    ## print >> sys.__stderr__, msg
    ## traceback.print_stack()   # goes to stderr by default
    ## # bug: that doesn't print the exception itself.

def compact_traceback():
    type, value, traceback1 = sys.exc_info()
    if (type, value) == (None, None):
        del traceback1 # even though it should be None
            # Note (pylint bug): when this local var was named traceback,
            # this del confused pylint -- even though we immediately return
            # (so this del has no effect in the subsequent code), pylint
            # now thinks traceback inside the try clause below refers to the
            # module in our global namespace, not the local variable. I'll
            # rename the local variable to traceback1 to see if this helps.
            # (It may only partly help -- maybe pylint will now complain
            #  falsely about an undefined variable.) [bruce 071108]
        return "<incorrect call of compact_traceback(): no exception is being handled>"
    try:
        printlines = []
        while traceback1 is not None:
            # cf. PythonDocumentation/ref/types.html;
            # starting from current stack level (of exception handler),
            # going deeper (towards innermost frame, where exception occurred):
            filename = traceback1.tb_frame.f_code.co_filename
            lineno = traceback1.tb_lineno
            printlines.append("[%s:%r]" % ( os.path.basename(filename), lineno ))
            traceback1 = traceback1.tb_next
        del traceback1
        ctb = ' '.join(printlines)
        return "%s: %s\n  %s" % (type, value, ctb)
    except:
        del traceback1
        return "<bug in compact_traceback(); exception from that not shown>"
    pass

# stack

def print_compact_stack( msg = "current stack:\n", skip_innermost_n = 2, **kws ):
    #bruce 061118 added **kws
    #bruce 080314 pass our msg arg to new msg arg of compact_stack
    print >> sys.__stderr__, \
          compact_stack( msg, skip_innermost_n = skip_innermost_n, **kws )

STACKFRAME_IDS = False # don't commit with True,
    # but set to True in debugger to see more info in compact_stack printout [bruce 060330]

def compact_stack( msg = "", skip_innermost_n = 1, linesep = ' ', frame_repr = None ):
    #bruce 061118 added linesep, frame_repr; 080314 added msg arg
    printlines = []
    frame = sys._getframe( skip_innermost_n)
    while frame is not None: # innermost first
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        extra = more = ""
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
        if frame_repr:
            more = frame_repr(frame)
        printlines.append("[%s:%r%s]%s" % ( os.path.basename(filename), lineno, extra, more ))
        frame = frame.f_back
    printlines.reverse() # make it outermost first, like compact_traceback
    return msg + linesep.join(printlines)

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
    """
    Execute a python command, supplied by the user via some sort of debugging interface (named by source),
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
        from utilities.Log import _graymsg, quote_html
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

# ==

def debug_timing_test_pycode_from_a_dialog( ): #bruce 051117
    # TODO: rewrite this to call grab_text_using_dialog (should be easy)
    title = "debug: time python code"
    label = "one line of python to compile and exec REPEATEDLY in debug.py's globals()\n(or use @@@ to fake \\n for more lines)"
    from PyQt4.Qt import QInputDialog
    parent = None
    text, ok = QInputDialog.getText(parent, title, label) # parent argument needed only in Qt4 [bruce 070329, more info above]
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
    """
    After making sure exec of user code is legally permitted, and exec of mycode works,
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
    """
    Execute mycode in glob ntimes and print how long that takes in realtime (in all, and per command).
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
    """
    @note: public attributes: name, order
    """
    def __init__(self, name, func, order = None, maker = False, text = None):
        """
        for doc of args see register_debug_menu_command
        """
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
        return [ (text, lambda func = func, widget = widget: func(widget)) ]    
            # (the func = func was apparently necessary, otherwise the wrong func got called,
            #  always the last one processed here)
            # [that comment is from before revision of 050923 but probably still applies]
    pass

def register_debug_menu_command( *args, **kws ):
    """
    Let other modules register commands which appear in the debug menu.
    When called, they get one arg, the widget in which the debug menu appeared.
       If order is supplied and not None, it's used to sort the commands in the menu
    (the other ones come at the end in order of their names).
       Duplicate names cause prior-registered commands to be silently replaced
    (even if other options here cause names to be ignored otherwise).
       If text is supplied, it rather than name is the menu-text. (Name is still used for replacement and maybe sorting.)
       If maker is true [experimental feature], then func is not the command but the sub-menu-spec maker,
    which runs (with widget as arg) when menu is put up, and returns a menu-spec list;
    in this case name is ignored except perhaps for sorting purposes.

    @param name: text for menu command

    @param function: function which implements menu command (runs with one arg, the widget)
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

# ===

def overridden_attrs( class1, instance1 ): #bruce 050108
    """
    return a list of the attrs of class1 which are overridden by instance1
    """
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

debug_reload_once_per_event = False # do not commit with true

def reload_once_per_event(module, always_print = False, never_again = True, counter = None, check_modtime = False):
    """
    Reload module (given as object or as name),
    but at most once per user-event or redraw, and only if debug_flags.atom_debug.
    Assumes w/o checking that this is a module it's ok to reload, unless the module defines _reload_ok as False,
    in which case, all other reload tests are done, but a warning is printed rather than actually reloading it.
       If always_print is True, print a console message on every reload, not just the first one per module.
       If never_again is False, refrain from preventing all further reload attempts for a module, after one reload fails for it.
       If counter is supplied, use changes to its value (rather than to env.redraw_counter) to decide when to reload.
       If check_modtime is True, the conditions for deciding when to reload are used, instead, to decide when to check
    the module's source file's modtime, and the actual reload only occurs if that has changed. (If the source file can't
    be found, a warning is printed, and reload is only attempted if never_again is False.)
       WARNING about proper use of check_modtime:
    if module A imports module B, and A and B are only imported after this function is called on them
    with check_modtime = True, and the counter increases and B's source file has been modified,
    then the developer probably wishes both A and B would be reloaded -- but nothing will be reloaded,
    since A has not been modified and that's what this function checks. When A is later modified, both will be reloaded.
       To fix this, the caller would need to make sure that, before any import of A, this function is called on both A and B
    (either order is ok, I think). We might someday extend this function to make that task easier, by having it record
    sub-imports it handles. We might use facilities in the exprs module (not currently finished) as part of that. #e
       Usage note: this function is intended for use by developers who might modify
    a module's source code and want to test the new code in the same session.
    But the default values of options are designed more for safety in production code,
    than for highest developer convenience. OTOH, it never reloads at all unless
    ATOM_DEBUG is set, so it might be better to revise the defaults to make them more convenient for developers.
    See cad/src/exprs/basic.py for an example of a call optimized for developers.
    """
    if not debug_flags.atom_debug:
        return
    if type(module) == type(""):
        # also support module names
        module = sys.modules[module]
    if counter is None:
        now = env.redraw_counter
    else:
        now = counter
    try:
        old = module.__redraw_counter_when_reloaded__
    except AttributeError:
        old = -1
    if old == now: 
        return
    # after this, if debug_reload_once_per_event, print something every time
    if debug_reload_once_per_event:
        print "reload_once_per_event(%r)" % (module,)
    if old == 'never again': #bruce 060304
        return
    # now we will try to reload it (unless prevented by modtime check or _reload_ok == False)
    assert sys.modules[module.__name__] is module
    module.__redraw_counter_when_reloaded__ = now # do first in case of exceptions in this or below, and to avoid checking modtime too often
    if check_modtime:
        ok = False # we'll set this to whether it's ok to check the modtime,
            # and if we set it True, put the modtime in our_mtime,
            # or if we set it False, print something
        try:
            ff = module.__file__
            if ff.endswith('.pyc'):
                ff = ff[:-1]
            ok = ff.endswith('.py') and os.path.isfile(ff)
            if ok:
                # check modtime
                our_mtime = os.stat(ff).st_mtime
            else:
                print "not ok to check modtime of source file of %r: " % (module,)
        except:
            print_compact_traceback("problem checking modtime of source file of %r: " % (module,) )
            ok = False
        if ok:
            old_mtime = getattr(module, '__modtime_when_reloaded__', -1) # use -1 rather than None for ease of printing in debug msg
            # only reload if modtime has changed since last reload
            want_reload = (old_mtime != our_mtime)
            setattr(module, '__modtime_when_reloaded__', our_mtime)
            if debug_reload_once_per_event:
                print "old_mtime %s, our_mtime %s, want_reload = %s" % \
                      (time.asctime(time.localtime(old_mtime)), time.asctime(time.localtime(our_mtime)), want_reload)
            pass 
        else:
            want_reload = not never_again
            if debug_reload_once_per_event:
                print "want_reload = %s" % want_reload
        if not want_reload:
            return
        pass
    # check for _reload_ok = False, but what it affects is lower down, by setting flags about what we do and what we print.
    # the point is to isolate the effect conditions here, ensuring what we do and print matches,
    # but to not print anything unless we would have without this flag being False.
    _reload_ok = getattr(module, '_reload_ok', True)
    if _reload_ok:
        def doit(module):
            reload(module)
        reloading = "reloading"
    else:
        def doit(module):
            pass 
        reloading = "NOT reloading (since module._reload_ok = False)"
    del _reload_ok
    # now we will definitely try to reload it (or not, due to _reload_ok), and in some cases print what we're doing
    if old == -1:
        print reloading, module.__name__
        if not always_print:
            print "  (and will do so up to once per redraw w/o saying so again)"
    elif always_print:
        print reloading, module.__name__
    try:
        doit(module)
    except:
        #bruce 060304 added try/except in case someone sets ATOM_DEBUG in an end-user version
        # in which reload is not supported. We could check for "enabling developer features",
        # but maybe some end-user versions do support reload, and for them we might as well do it here.
        print_compact_traceback("reload failed (not supported in this version?); continuing: ")
        if never_again:
            module.__redraw_counter_when_reloaded__ = 'never again'
    return


DO_PROFILE = False

def doProfile(t):
    global DO_PROFILE
    DO_PROFILE = t
    return

_profile_function = None
_profile_args = None
_profile_keywordArgs = None
_profile_output_file = 'profile.output'

def _run_profile():
    _profile_function(*_profile_args, **_profile_keywordArgs)

def profile(func, *args, **keywordArgs):
    """
    Profile a function call, if profiling is enabled.  Change a normal
    function call f(a, b, c=3) into profile(f, a, b, c=3), and f will
    be profiled.  A method call can also be profiled: o.f(a) becomes
    profile(o.f, a).

    Profiling is enabled by setting DO_PROFILE = True in
    utilities.debug.  Otherwise, the function is called without
    profiling.

    Fancier schemes, like profiling the Nth call of a function could
    be implemented here, if desired.
    """
    global _profile_function
    global _profile_args
    global _profile_keywordArgs
    global DO_PROFILE
    
    _profile_function = func
    _profile_args = args
    _profile_keywordArgs = keywordArgs

    if (DO_PROFILE):
        import cProfile
        print "Capturing profile..."
        cProfile.run('from utilities.debug import _run_profile; _run_profile()', _profile_output_file)
        print "...end of profile capture"
    else:
        _run_profile()

    _profile_function = None
    _profile_args = None
    _profile_keywordArgs = None

# ==

def import_all_modules_cmd(glpane): #bruce 080721 experimental
    del glpane
    
    import os
    from utilities.constants import CAD_SRC_PATH
    
    _original_cwd = os.getcwd() # so we can restore it before returning
    
    try:
        os.chdir(CAD_SRC_PATH)
        
        # this doesn't work, don't know why:
        ## pipe = os.popen("./tools/AllPyFiles.sh")
        ## modules = pipe.readlines() # IOError: [Errno 4] Interrupted system call
        ## pipe.close()
        
        # so try this instead:
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
        tmpdir = find_or_make_Nanorex_subdir("TemporaryFiles")
        tmpfile = os.path.join( tmpdir, "_all_modules" )
        os.system("./tools/AllPyFiles.sh > '%s'" % tmpfile)
        file1 = file(tmpfile, "rU")
        modules = file1.readlines()
        file1.close
        os.remove(tmpfile)
        
        print "will import %d modules" % len(modules) # 722 modules as of 080721!

        modules.sort()

        SKIP_THESE = ("_import_roots", "main", "ExecSubDir")

        import_these = []
        
        for module in modules:
            module = module.strip()
            if module.startswith("./"):
                module = module[2:]
            basename = module
            assert os.path.exists(module), "should exist: %r" % (module,)
            assert module.endswith(".py"), "should end with .py: %r" % (module,)
            module = module[:-3]
            if module in SKIP_THESE or ' ' in module or '-' in module:
                # those funny chars can happen when developers have junk files lying around
                # todo: do a real regexp match, permit identifiers and '/' only;
                # or, only do this for files known to svn?
                print "skipping import of", basename
                continue
            import_these.append(module.replace('/', '.'))
            continue

        for module in import_these:
            statement = "import " + module
            try:
                exec statement
            except:
                print_compact_traceback("ignoring exception in %r: " % statement)
                pass

        print "done importing all modules"
        
    except:
        print_compact_traceback("ignoring exception: ")
        
    os.chdir(_original_cwd)
    return

register_debug_menu_command( "Import all source files", import_all_modules_cmd )

# end
