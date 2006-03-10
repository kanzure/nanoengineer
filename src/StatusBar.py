# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
StatusBar.py - status bar widgets and their methods.

$Id$

History: Started with ProgressBar.py and widdled it down, replacing the original
progressbar dialog with the new MainWindow progress bar and simAbort "Stop Sign" button.
by mark on 060105.

'''
__author__ = "Mark"

import os, time
from qt import QProgressBar, QFrame, QToolButton, QIconSet, QLabel, SIGNAL, QMessageBox
from platform import hhmmss_str #bruce 060106 moved that function there
import env
from HistoryWidget import redmsg #bruce 060208 fix bug in traceback printing re bug 1263 (doesn't fix 1263 itself)

def do_what_MainWindowUI_should_do(win):
    """Create some widgets inside the Qt-supplied statusbar, self.statusBar()."""
    # (see also env.history.message())
    
    # Create progressbar.
    win.status_pbar = QProgressBar(win)
    win.status_pbar.setMaximumWidth(300)
    win.status_pbar.setCenterIndicator(True)
    win.statusBar().addWidget(win.status_pbar,0,True)
    win.status_pbar.hide()
    
    # Create a status message bar. Bug 1343, wware 060309
    win.statusMsgLabel = QLabel(win.statusBar(), "statusMsgLabel")
    win.statusMsgLabel.setMinimumWidth(150)
    win.statusMsgLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
    win.statusBar().addWidget(win.statusMsgLabel, 0, True)
    
    # Create sim abort (stop) button.
    win.simAbortButton = QToolButton(win, "")
    from Utility import imagename_to_pixmap
    pixmap = imagename_to_pixmap("stopsign.png")
    win.simAbortButton.setIconSet(QIconSet(pixmap))
    win.simAbortButton.setMaximumWidth(32)
    win.statusBar().addWidget(win.simAbortButton,1,True)
    win.connect(win.simAbortButton,SIGNAL("clicked()"),win.simAbort)
        # as of 060106 this puts up confirmation dialog,
        # then does self.sim_abort_button_pressed = True (if user confirms)
    win.simAbortButton.hide()

    # Create (current) display mode bar.
    win.dispbarLabel = QLabel(win.statusBar(), "dispbarLabel")
    win.dispbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
    win.statusBar().addWidget(win.dispbarLabel, 0, True)
    
    # Create (current) mode bar.        
    win.modebarLabel = QLabel(win.statusBar(), "modebarLabel")
    win.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
    win.statusBar().addWidget(win.modebarLabel, 0, True)

    # == following code is unused as of 060106 -- might become real soon, don't know yet;
    # please don't remove it without asking me [bruce 060106]
##    if 0: #######@@@@@@@ DISABLED FOR SAFE COMMIT OF UNFINISHED CODE [bruce 060104]        
##        # Taken from MWsemantics.make_buttons_not_in_UI_file().  
##        # Changed occurances of self.simAbortAction to win.simAbortButton
##        # mark 060105
##        from extended_ops import ExtendedOpStack
##        win.stack_of_extended_ops = ExtendedOpStack(win, [win.simAbortButton])
##            #e in present implem this knows a lot about win.simAbortAction; needs cleanup
##        win.stack_of_extended_ops.update_UI()

    win._duration = 0 # Seconds that the progress bar takes to complete
        # [bruce 050415 comment: 'duration' is a public attribute, used by external code
        #  after the progress bar is hidden and the launch method has returned.]
        # [bruce 060103: I've now removed that kluge from runSim.py.
        #  This attr should now be considered private.
        #  I think I'll rename it to '_duration' to verify that. ####@@@@
        
    return


def show_progressbar_and_stop_button(win, nsteps, filename = '', cmdname = "<unknown command>", show_duration = 0):
    # misnamed, since specialized for watching a growing file, and since also waits for progress to be done... [bruce 060106 comment]
    """Display the statusbar's progressbar and stop button, and update it while a file is 
    being written by some other process, to show the size of that file as progress, while 
    waiting for that size to reach a given value; when it does, hide the progressbar and stop
    button and return 0. If the user first presses the Stop button on the statusbar, hide the 
    progressbar and stop button and return 1.
    Parameters:
        win - the main window
        nsteps - total steps for the progress bar (final size in bytes of filename)
        filename - name of file we are waiting for.
        cmdname - name of command (used in some messages and in abort button tooltip)
        show_duration - if True, display duration (in seconds) below progressbar
    Return value: 0 if file reached desired size, 1 if user hit abort button.
    """
    # (note: mark circa 060105 made this by copying and modifying ProgressBar.launch(). bruce 060112 added cmdname.)
    
    #bruce 060106 splitting this into pieces so Pyrex sim interface can share some of its code.
    # (These pieces are global functions, but should really be methods of a new class, but that can wait. #e)
    
    ## win.sim_abort_button_pressed = False # moved into AbortButtonForOneTask.start
    filesize = 0
    sinc = .1
    
    ###e the following is WRONG if there is more than one task at a time... [bruce 060106 comment]
    win.stime = time.time() 
    win.status_pbar.reset()
    win.status_pbar.setTotalSteps(nsteps)
    win.status_pbar.setProgress(0)
    win.status_pbar.show()
    
    ## win.simAbortButton.show() # moved into AbortButtonForOneTask.start

    abortbutton = AbortButtonForOneTask( cmdname)
        #bruce 060106 moved some code from this loop into that class (so pyrex sim can use it too)
    abortbutton.start()
    
    # Main loop
    while filesize < nsteps:
        if os.path.exists(filename): filesize = os.path.getsize(filename)
        win.status_pbar.setProgress( filesize )
        import env
        env.call_qApp_processEvents()
            # Process queued events (e.g. clicking Abort button,
            # but could be anything -- no modal dialog involved anymore).
        
        if show_duration: # Display duration.
            elapsedtime = win._duration
            win._duration = time.time() - win.stime
            if elapsedtime == win._duration: continue
            elapmsg = "Elapsed Time: " + hhmmss_str(int(win._duration))
            # Need to display the duration somewhere.  History msg?
            env.history.statusbar_msg(elapmsg)
                #e if this is a non-modal background task, that statusbar_msg
                # might mess up more important ones from foreground operations --
                # need to reconsider this (even if we prohibit other long-running
                # tasks from being launched during this time). [bruce 060106 comment]

        abortbutton.step()
        if abortbutton.status == ABORTING:
        ## if win.sim_abort_button_pressed: # User hit abort button
            ## win.sim_abort_button_pressed = False #bruce 060106 -- make sure at most one task responds [not sure this is good]
                # I decided not to add that, since until we have a better/safer way to control multiple long running tasks,
                # we might as well let 'abort' clear out all the ongoing tasks at once! Chnces are the user didn't even
                # realize there was more than one, and furthermore, if they continue they might mess things up more than
                # this one (running inside them and effectively suspending them) has already done!
                # [bruce 060106]
            win.status_pbar.hide()
            abortbutton.finish()
            ## win.simAbortButton.hide()
            env.history.statusbar_msg("Aborted.")
            return 1

        time.sleep(sinc) # Take a rest
        
    # End of Main loop (this only runs if it ended without being aborted)
    win.status_pbar.setProgress(nsteps)
    win._duration = time.time() - win.stime
    time.sleep(0.1)  # Give the progress bar a moment to show 100%
    win.status_pbar.hide()
    abortbutton.finish()
    ## win.simAbortButton.hide()
    env.history.statusbar_msg("Done.")
    return 0

def show_pbar_and_stop_button_for_esp_calculation(win, sim_id, nh_socket, show_duration = 0):
    """Display the statusbar's progressbar and stop button, and update it while an ESP calculation
    is being run by Nano-Hive.
    Parameters:
        win - the main window
        sim_id - simulation Id
        nh_socket - the Nano-Hive socket
        show_duration - if True, display duration (in seconds) below progressbar
    Return value: 0 if Nano-Hive finished, 1 if user hit abort button.
    """
        
    win.sim_abort_button_pressed = False
    sinc = .1
    win.stime = time.time()
        
    win.status_pbar.reset()
    win.status_pbar.setTotalSteps(100) # 0-100 percent
    win.status_pbar.setProgress(0)
    win.status_pbar.show()
        
    win.simAbortButton.show()
        
    done = False
    percentDone = 0
        
    # Main loop
    while not done:
            
        success, response = nh_socket.sendCommand("status " + sim_id) # Send "status" command.
        #print success, response
        r, p = response.split(sim_id)
        #print "responseCode=", r,", percent=", p
            
        responseCode = int(r)
        
        # Need to do this since we only get a percent value when responseCode == 5 (sim is running).
        # If responseCode != 5, p can be None (r=10) or a whitespace char (r=4).
        if responseCode == 5: #
            percentDone = int(p)

        #print "responseCode =", responseCode,", percentDone =", percentDone

        win.status_pbar.setProgress( percentDone )
        import env
        env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
        # Process queued events (i.e. clicking Abort button).
            
        if show_duration: # Display duration.
            elapsedtime = win._duration
            win._duration = time.time() - win.stime
            if elapsedtime == win._duration: continue
            elapmsg = "Elapsed Time: " + hhmmss_str(int(win._duration))
            env.history.statusbar_msg(elapmsg)
                
        if responseCode == 4: # 5 == Sim is Idle (Done)
            done = True
            
        if win.sim_abort_button_pressed: # User hit abort button
            win.status_pbar.hide()
            win.simAbortButton.hide()
            env.history.statusbar_msg("Aborted.")
            return 1

        time.sleep(sinc) # Take a rest
            
    # End of Main loop
    win.status_pbar.setProgress(100) # 100 percent
    win._duration = time.time() - win.stime
    time.sleep(0.1)  # Give the progress bar a moment to show 100%
    win.status_pbar.hide()
    win.simAbortButton.hide()
    env.history.statusbar_msg("Done.")
    return 0

# ==

abortables = [] #bruce 060112 quick fix to prevent more than one task at a time from owning the stopsign button
    ########@@@@@@@ partly NIM

def cmdname_already_running():
    if not abortables:
        return "" # nothing is running
    cmdname = abortables[-1].cmdname # command name of what's running (which is why a new command can't start)
    return cmdname or "<some command>" # ensure this retval is True (bug if cmdname is not, but don't bother to catch that here)

def ok_to_start(cmdname, explain_why_not = False):
    """Is it ok to start a new task of the command of the given name? If yes return True,
    if no return False. If no and explain_why_not is true, first emit a standard
    history message explaining why not.
    """
    old = cmdname_already_running()
    ok = not old
    if not ok and explain_why_not:
        env.history.message(redmsg("%s is not allowed while %s is still running" % (cmdname, old) ))
    return ok

class AbortButtonForOneTask: #bruce 060106; will become a subclass of something like "subtask with its own start/step/finish methods"
    "initial stub or kluge -- all tasks use the same abort button -- will probably mess up if more than one task is run at once"
    #e a task name (for tooltip, history, etc) should be passed to some method here...
    #e note: if this would create its own copy of the stopsign button, with a custom tooltip, and its own signal/slot/flag,
    # then we'd have (1) visible warning of multiple tasks, (2) prototype of "task icons on sbar" proposal,
    # (3) better chance of avoiding bugs from multiple tasks.
    def __init__(self, cmdname):
        self.cmdname = cmdname or '<unknown command>' # required argument
        self.win = env.mainwindow()
            # used for the global flag self.win.sim_abort_button_pressed (shared among all tasks for now)
        self.abortButton = self.win.simAbortButton
        self.status = None
        self.error = None
        self.force_quit = False
    def ok_to_start(self, explain_why_not = False):
        return ok_to_start(self.cmdname, explain_why_not = explain_why_not)
    def start(self):
        ok = self.ok_to_start(explain_why_not = True)
        assert ok, "self == %r should have checked self.ok_to_start() before calling start"
        abortables.append(self)
        self.win.sim_abort_button_pressed = False
            # This is very dubious if there is more than one task at a time... [bruce 060106 comment]
        self.status = STARTED
        self.set_tooltip("Abort %s" % self.cmdname)
        self.abortButton.show()
    def set_tooltip(self, text):
        print "set tooltip for abort button is nim:",text ####@@@@
        pass ### self.abortButton.setText(text) ###k setTooltip ok for Action, but not Button... what is correct?
    def step(self):
        assert not self.force_quit # purpose of this is to raise an exception to force caller to quit! KeyboardInterrupt might be better
        if self.win.sim_abort_button_pressed: # User hit abort button [and main window slot method noticed that and set this flag]
            self.win.sim_abort_button_pressed = False # so we can detect if it's pressed again
            if self.status in [None, FINISHED]:
                print "unexpected status %d in %r.step()" % (self.status, self)
            if self.status in [ABORTING, FINISHED]:
                # pressed more than once
                self.force_quit()
            elif self.status in [STARTED,None]:
                self.abort()
            pass
        return
    def abort(self):
        self.status = ABORTING # client can notice this (or in future, subscribe to it #e)
        self.error = 'abort button pressed' ###@@@ not yet used??
        self.set_tooltip("Force Quit %s" % self.cmdname) # only seen if the abort fails (I hope)
        ###e history message good here?
        return
    def aborting(self):
        "[specialized method for only this subclass -- i think -- or one which generates internal aborts, anyway ##k]"
        self.step()
        return self.status == ABORTING
    def force_quit(self):
        # ideally this should never happen, but it might if system gets slow and user gets impatient
        self.set_tooltip("Force Quit already done on %s" % self.cmdname)
        self.force_quit = True
        print "force quit",self
        env.history.message(redmsg("Force Quit %s (since it didn't respond to first abort)" % self.cmdname))
        self.finish()
        return
    def finish(self):
        """This should be called when the task it's about ends for any reason,
        whether success or error or abort or even crash;
        if not called it will prevent all other abortable tasks from running!
        """
        ####e should try to figure out a way to auto-call it for tasks that user clicked abort for but that failed to call it...
        # for example, if user clicks abort button twice for same task. or if __del__ called (have to not save .win). #####@@@@@
        try:
            abortables.remove(self)
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: bug: failure in abortables.remove(self): ")
            pass
        if not abortables: # (could just as well be 'if 1' until we permit more than one abortable object)
            self.abortButton.hide()
                # this is very dubious if there is more than one task, in fact it's VERY WRONG for success of subtask
                # and MIGHT NOT HAVE BEEN AS BAD IN THE OLD CODE (if it didn't happen for all finishes but only aborting ones) (???),
                # but at least the current code will try to abort them all at once
                # when the abort button is pressed once. [bruce 060106 comment]
        self.status = FINISHED # whether or not it was ABORTING earlier
    pass

_junk, STARTED, ABORTING, FINISHED = range(4)

# end
