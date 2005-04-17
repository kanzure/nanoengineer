# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

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
'''

import sys, os, time
from constants import debugButtons, noop

# note: some debug features run user-supplied code in this module's
# global namespace (on platforms where this is permitted by our licenses).

# enable the undocumented debug menu by default [bruce 040920]
# (moved here from GLPane, now applies to all widgets using DebugMenuMixin [bruce 050112])
debug_menu_enabled = 1 
debug_events = 0 # set this to 1 to print info about many mouse events

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
        while traceback:
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

def compact_stack( skip_innermost_n = 1 ):
    printlines = []
    frame = sys._getframe( skip_innermost_n)
    while frame: # innermost first
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        printlines.append("[%s:%r]" % ( os.path.basename(filename), lineno ))
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
        print "will execute (from %s): %s" % (source, command)
    else:
        nlines = command.count('\n')+1
        print "will execute (from %s; %d lines):\n%s" % (source, nlines, command)
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

    def makemenu(self, lis): # bruce 050304 added this, so subclasses no longer have to
        "[can be overridden by a subclass, but probably never needs to be]"
        from widgets import makemenu_helper
        return makemenu_helper(self, lis)
    
    def _debug_history(self):
        # figure out where to send history messages
        # (can't be done at init time since value of win.history can change)
        try:
            return self._debug_win.history
        except: # (more than one error possible here)
            return None

    def debug_menu_items(self):
        """#doc; as of 050416 this will be called every time the debug menu needs to be put up,
        so that the menu contents can be different each time (i.e. so it can be a dynamic menu)
        [subclasses can override this; best if they call this superclass method
        and modify its result, e.g. add new items at top or bottom]
        """
        import debug
        res = [
            ('(debugging menu)', noop, 'disabled'),
            # None, # separator
        ]
        if self._debug_win:
            res.extend( [
                ('load window layout', self._debug_load_window_layout ),
                ('save window layout', self._debug_save_window_layout ),
                    #bruce 050117 prototype "save window layout" here; when it works, move it elsewhere
            ] )
        if debug.exec_allowed():
            #bruce 041217 made this item conditional on whether it will work
            res.extend( [
                ('run py code', self._debug_runpycode),
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
        res.extend( [
            ('choose font', self._debug_choose_font),
        ] )
        if self._debug_win:
            res.extend( [
                ('call update_parts()', self._debug_update_parts ), ###e also should offer check_parts
            ] )
        res.extend( [
            ('print self', self._debug_printself),
        ] )
        return res

    def _debug_save_window_layout(self):
        from platform import save_window_pos_size
        win = self._debug_win
        keyprefix = "main window/geometry"
        histfunc = self._debug_history().message
        save_window_pos_size( win, keyprefix, histmessage = histfunc)

    def _debug_load_window_layout(self):
        from platform import load_window_pos_size
        win = self._debug_win
        keyprefix = "main window/geometry"
        histfunc = self._debug_history().message
        load_window_pos_size( win, keyprefix, histmessage = histfunc)

    def _debug_update_parts(self):
        win = self._debug_win
        win.assy.update_parts()
        
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
    
    def debug_event(self, event, funcname, permit_debug_menu_popup = 0):
        """[the main public method for subclasses]
           Debugging method -- no effect on normal users.  Does two
           things -- if a global flag is set, prints info about the
           event; if a certain modifier key combination is pressed,
           and if caller passed permit_debug_menu_popup = 1, puts up
           an undocumented debugging menu, and returns 1 to caller.
           As of 040916, the debug menu is put up by
           Shift-Option-Command-click on the Mac, and for other OS's I
           predict it either never happens or happens only for some
           similar set of 3 modifier keys.
           -- bruce 040916
        """
        # In constants.py: debugButtons = cntlButton | shiftButton | altButton
        # On the mac, this really means command-shift-alt [alt == option].
        # On Linux, reports Josh (050118), "I get the debug menu with
        # <cntrl><shift><alt><left click>" [in the glpane, one of our callers].
        
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
            lis = self.debug_menu_items()
            menu = self.makemenu( lis ) # might be []
        except:
            print_compact_traceback("bug in do_debug_menu ignored; menu_spec is %r" % (lis,) )
            menu = None # for now
        
        ## removed [bruce 050416] since badly named and not yet used:
        ## self.current_event = event # (so debug commands can see it)
        if menu:
            menu.exec_loop(event.globalPos(), 1)
        ## self.current_event = None
        return 1

    def _debug_printself(self):
        print self

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

    pass # end of class DebugMenuMixin

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

# end
