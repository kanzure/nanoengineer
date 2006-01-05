# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
extended_ops.py

Coordination and UI framework for extended operations that might be requested in parallel,
where the old one might accomodate the new one by suspending or aborting itself,
or might merge the new one into itself, run it in parallel, or arrange to do it later.

Also provides shared UI with buttons and menuitems for Abort and Pause/Continue (and maybe more).

$Id$

This module's docstring got very long, so it's in a separate file, extended_ops.txt.

==

History:

bruce 060104 needed this for Minimize realtime's abort button.

'''
__author__ = 'bruce'

###e WRONG NAMES of classes and methods, will be changed


class ExtendedOpStack:
    "stack of extended operations (suspended or active) and support for their shared UI."
    def __init__(self, win, ui_elements):
        self.current_abortables = [] # either public or we'll provide accessors (at least for scan)
        self.win = win #k needed?
        (self.simAbortAction,) = ui_elements
        return
    def add_abortable(self, object):
        ### , text = "Abort Current Action", tooltip_text = None):  ### this doc is WRONG:
        """Add object to our list of abortable extended actions... it should be the controller for an extended action
        that just started and that will accept the do_abort method call when the user hits the abort button.
        (Whether it's legal to add this inside others already running is up to the caller --
         we don't check it here. [#e Maybe we should add a flag to do that? But there's more than one choice of what to do
         if the check fails, so it's probably better to just let the stack be public.])
           Text should be a short phrase suitable in menu text... optional tooltip_text can also be supplied.
        """
        self.current_abortables.append(object)
        self.update_UI()

    def update_UI(self):
        "Let current abortable update all UI elements shared by all abortables."
        if self.current_abortables:
            last = self.current_abortables[-1]
            last.update_simAbortAction( self.simAbortAction) #e method belongs in an object that knows about this UI, not in last
        else:
            self.simAbortAction.setEnabled(False)
        #e could set tooltip to info about last item + count of hidden/suspended items
        return
    
    def simAbort(self):
        "[gets called directly by a slot method]" ###e move this back into MWsem... let it pass msg to abortable-stack object
        if self.current_abortables:
            # (condition should always be true, since button should be disabled when it's not)
            self.current_abortables[-1].do_abort()
        return

    def remove_abortable(self, object):
        """Object should be the most recently added abortable (if not, discard the more recent ones and complain).
        It should have already been aborted, or be about to be immediately aborted, before calling this.
        Remove it from the list of abortable objects, and update the abort button to reflect the current innermost object on it.
        [#e Maybe also notify that object it's now the last one again? Not sure.]
        """
        assert object in self.current_abortables # bug in caller if not
        while 1:
            assert self.current_abortables, "bug in this loop"
            last = self.current_abortables.pop()
            if last is not object:
                print "bug: some abortable forgot to remove itself"
                # tell last about this??
                continue
            # the pop removed the right one -- tell the next one down (if any) anything??
            break
        self.update_UI()
        return

    pass

class ExtendedOp:
    """Something to put on the stack of (suspended or active) extended operations.
    [Relation to CommandRun: probably a member of some of them -- not sure. #e]
    """
    def __init__(self, stack, what = "current operation"):
        self.stack = stack # the stack of extended operations we'll be put on (when we start, or maybe before??###k)
        self.what = what # used in text like "Abort <what>" or "Pause <what>"...
        #e does the word "Abort" also need to be customized?
    def do_abort(self):
        print "do_abort nim in",self
    def do_pause(self):
        print "do_pause nim in",self
    def do_continue(self):
        print "do_continue nim in",self
    def add_to_stack(self):
        self.stack.add(self)
    def remove_from_stack(self):
        self.stack.remove(self)
    def get_abort_text(self):
        return "Abort %s" % self.what
    def update_simAbortAction(self, action): #e this method probably doesn't belong in this class, but in its client UI code
        "Update the simAbort action (button/menuitem) for self's current state, assuming self is the active abortable"
        ##k Does it make sense for each abortable to know about each UI element it needs to update? I guess it has to
        # unless we force this to be more uniform -- which we could; but for now let superclass have the common code
        # and let subclasses customize it using get_text only.
        action.setEnabled(True)
        #e change iconset too??
        text = self.get_abort_text()
        action.setText(text) # removed __tr, could add it back if desired
        action.setMenuText(text + '...')
        return
    def safe_start(self):
        try:
            self.start()
        except:
            self.report_exception() #e analogous to print_compact_traceback
    #e etc for other safe_xxx methods
    def loop(self):
        "Standard loop structure for an extended operation." #k not sure if this makes sense to have here, but nice if we can...
        # before this runs, all options and args were stored on self.
        self.safe_start() # safe_ means protected from exceptions; subclasses can just override plain start, etc
            # not sure where uniform code like start_time measurement should go. maybe right in this method? but should be overridable.
        while 1:
            self.safe_step() # 'continue' is a Python keyword
                # this or anything else can set flags saying to stop, and if so, whether an error occurred and what it was
            if self.stop:
                break
            #e do the other op's steps, including the event loop's (not sure if it's a special case)
            env.call_qApp_processEvents() # this might call our coordination methods from potentially nested or new parallel ops
            #e check for changes you care about
            self.safe_check_for_changes() # sets .stop if necessary (??) (###e or might it want to pause?)
            if self.stop:
                break
            
                
                        
        self.safe_finish() # whether error, abort, or normal
        return
    pass

#e refile; add info about what nested ops are prohibited, what UI buttons to disable when active, etc? related to CommandRun class??
class MinimizeExtendedOp(ExtendedOp):
    def __init__(self, stack, command):
        ExtendedOp.__init__(self, stack, "Minimize")
        self.command = command #k or in superclass?
    def do_abort(self):
        self.command.abort_sim #### not true, that's probably LL, not sure though, ..
    pass

'''
add to runsim

            self.abortable = MinimizeAbortable(self) ### also for Dynamics... or should self just *be* the abortable?
                # then we have methods with prefixes so we can mixin the abortable superclass and tell it our command name text
                # or let it asks for our ordinary command name....


in this context

[!5072] sim/src % diff -c !*
diff -c {$B,$W}/runSim.py
*** /Nanorex/Bunker/cad/src/runSim.py   Wed Jan  4 16:07:45 2006
--- /Nanorex/Working/cad/src/runSim.py  Wed Jan  4 16:04:53 2006
***************
*** 215,222 ****
                  # this works for developers if they set up symlinks... might not be right...
              worked = self.import_dylib_sim(self.dylib_path)
              if not worked:
!                 #####@@@@@ fix dylib filename in this message
!                 msg = redmsg("The simulator dynamic library [sim.so on Mac or Linux, in " + self.dylib_path +
                               "] is missing or could not be imported. Trying standalone executable simulator.")
                  env.history.message(cmd + msg)
                  ## return -1
--- 215,225 ----
                  # this works for developers if they set up symlinks... might not be right...
              worked = self.import_dylib_sim(self.dylib_path)
              if not worked:
!                 # The dylib filename on Windows can be either sim.dll or sim.pyd -- should we mention them both?
!                 # If the imported name is not the usual one, or if two are present, should we print a warning?
!                 ##e Surely this message text (and the other behavior suggested above) should depend on the platform
!                 # and be encapsulated in some utility function for loading dynamic libraries. [bruce 060104]
!                 msg = redmsg("The simulator dynamic library [sim.so or sim.dll, in " + self.dylib_path +
                               "] is missing or could not be imported. Trying standalone executable simulator.")
                  env.history.message(cmd + msg)
                  ## return -1
***************
*** 736,741 ****
--- 739,747 ----
              # (items 1 & 2 & 4 have been done)
              # 3. if callback caller in C has an exception from callback, it should not *keep* calling it, but reset it to NULL
  
+             self.abortable = MinimizeAbortable(self) ### also for Dynamics... or should self just *be* the abortable?
+                 # then we have methods with prefixes so we can mixin the abortable superclass and tell it our command name text
+                 # or let it asks for our ordinary command name....
              import time
              start = time.time()
              simobj.go( frame_callback = self.sim_frame_callback)
Exit 1
[!5073] sim/src % 

'''
