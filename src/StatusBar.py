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
import env

def do_what_MainWindowUI_should_do(win):
        """Create some widgets inside the Qt-supplied statusbar, self.statusBar()."""
        # (see also env.history.message())
        
        # Create progressbar.
        win.status_pbar = QProgressBar(win)
        win.status_pbar.setMaximumWidth(300)
        win.status_pbar.setCenterIndicator(True)
        win.statusBar().addWidget(win.status_pbar,0,True)
        win.status_pbar.hide()
        
        # Create sim abort (stop) button.
        win.simAbortButton = QToolButton(win, "")
        from Utility import imagename_to_pixmap
        pixmap = imagename_to_pixmap("stopsign.png")
        win.simAbortButton.setIconSet(QIconSet(pixmap))
        win.simAbortButton.setMaximumWidth(32)
        win.statusBar().addWidget(win.simAbortButton,1,True)
        win.connect(win.simAbortButton,SIGNAL("clicked()"),win.simAbort)
        win.simAbortButton.hide()

        # Create (current) display mode bar.
        win.dispbarLabel = QLabel(win.statusBar(), "dispbarLabel")
        win.dispbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        win.statusBar().addWidget(win.dispbarLabel, 0, True)
        
        # Create (current) mode bar.        
        win.modebarLabel = QLabel(win.statusBar(), "modebarLabel")
        win.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        win.statusBar().addWidget(win.modebarLabel, 0, True)
        
        # Taken from MWsemantics.make_buttons_not_in_UI_file().  
        # Changed occurances of self.simAbortAction to win.simAbortButton
        # mark 060105
        if 0: #######@@@@@@@ DISABLED FOR SAFE COMMIT OF UNFINISHED CODE [bruce 060104]
            from extended_ops import ExtendedOpStack
            win.stack_of_extended_ops = ExtendedOpStack(win, [win.simAbortButton])
                #e in present implem this knows a lot about self.simAbortAction; needs cleanup
            self.stack_of_extended_ops.update_UI()

        win._duration = 0 # Seconds that the progress bar takes to complete
            # [bruce 050415 comment: 'duration' is a public attribute, used by external code
            #  after the progress bar is hidden and the launch method has returned.]
            # [bruce 060103: I've now removed that kluge from runSim.py.
            #  This attr should now be considered private.
            #  I think I'll rename it to '_duration' to verify that. ####@@@@
            
        return


def show_progressbar_and_stop_button(win, nsteps, filename = '', show_duration = 0):
        """Display the statusbar's progressbar and stop button, and update it while a file is 
        being written by some other process, to show the size of that file as progress, while 
        waiting for that size to reach a given value; when it does, hide the progressbar and stop
        button and return 0. If the user first presses the Stop button on the statusbar, hide the 
        progressbar and stop button and return 1.
        Parameters:
            win - the main window
            nsteps - total steps for the progress bar (final size in bytes of filename)
            filename - name of file we are waiting for.
            show_duration - if True, display duration (in seconds) below progressbar
        Return value: 0 if file reached desired size, 1 if user hit abort button.
        """
        
        win.abort = False
        filesize = 0
        sinc = .1
        win.stime = time.time()

#        print "StatusBar: nsteps =",nsteps,", filename =", filename
        
        win.status_pbar.reset()
        win.status_pbar.setTotalSteps(nsteps)
        win.status_pbar.setProgress(0)
        win.status_pbar.show()
        
        win.simAbortButton.show()
        

        # Main loop
        while filesize < nsteps:
            if os.path.exists(filename): filesize = os.path.getsize(filename)
            win.status_pbar.setProgress( filesize )
            import env
            env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
                # Process queued events (i.e. clicking Abort button).
            
            if show_duration: # Display duration.
                elapsedtime = win._duration
                win._duration = time.time() - win.stime
                if elapsedtime == win._duration: continue
                elapmsg = "Elasped Time: " + hhmmss_str(int(win._duration))
                # Need to display the duration somewhere.  History msg?
                env.history.statusbar_msg(elapmsg)
            
            if win.abort: # User hit abort button
                win.status_pbar.hide()
                win.simAbortButton.hide()
                env.history.statusbar_msg("Aborted.")
                return 1

            time.sleep(sinc) # Take a rest
            
        # End of Main loop
        win.status_pbar.setProgress(nsteps)
        win._duration = time.time() - win.stime
        time.sleep(0.1)  # Give the progress bar a moment to show 100%
        win.status_pbar.hide()
        win.simAbortButton.hide()
        env.history.statusbar_msg("Done.")
        return 0

def abort_run(win):
        '''Original slot for Abort button.
        This is currently not used and superceded by simAbort()
        '''
        
        # Added confirmation before aborting as part of fix to bug 915. Mark 050824.
        ret = QMessageBox.warning( win, "Confirm",
            "Please confirm you want to abort.\n",
            "Confirm",
            "Cancel", 
            None, 
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
        if ret==0: # Confirmed
            win.abort = True
            
# An identical copy of this function is in ProgressBar.py (soon to be obsolete).
# runSim.py and GamessJob.py both import this function. 
# This should be moved to another file.  Ask Bruce.  Mark 060105.
def hhmmss_str(secs):
    """Given the number of seconds, return the elapsed time as a string in hh:mm:ss format"""
    # [bruce 050415 comment: this is sometimes called from external code
    #  after the progressbar is hidden and our launch method has returned.]
    # bruce 050415 revising this to use pure int computations (so bugs from
    #  numeric roundoff can't occur) and to fix a bug when hours > 0 (commented below).
    secs = int(secs)
    hours = int(secs/3600) # use int divisor, not float
    # (btw, the int() wrapper has no effect until python int '/' operator changes to produce nonints)
    minutes = int(secs/60 - hours*60)
    seconds = int(secs - minutes*60 - hours*3600) #bruce 050415 fix bug 439: also subtract hours
    if hours:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)
    else:
        return '%02d:%02d' % (minutes, seconds)

# end