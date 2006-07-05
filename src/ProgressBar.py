# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
ProgressBar.py - progress bar dialog, for use while waiting for simulator
to finish writing output into a known file of known final length.

$Id$
'''
__author__ = "Mark"

import os, time

from qt import qApp, QMessageBox
from ProgressBarDialog import ProgressBarDialog
    #bruce 050415 removed "import *" from both of those

from platform import hhmmss_str #bruce 060106 moved that function there
import env #bruce 060103

class ProgressBar( ProgressBarDialog ):
    def __init__(self):
        ### Huaicai 1/10/05: make the dialog as a modal dialog, 
        ### otherwise, if the user close the main window, it will get 
        ### "RuntimeError: underlying C/C++ object has been deleted
        ## parent = None
        ## modal = True
        #bruce 060103 experiment: see if we can let it be nonmodal if we give it a parent.
        # This works, though it also changes its style and IMHO (on my Mac) makes it worse
        # (thinner dragbar with tinier closebuttons).
        # Also there could be bugs for some ops user might do while minimize is running
        # (but the best fix for those would be to make it safe and permit the ops).
        # But for now I'll disable this experiment (modal = True).
        parent = env.mainwindow()
        modal = True # can work with False, see comment above
        ProgressBarDialog.__init__(self, parent, None, modal)
            #args are: def __init__(self,parent = None,name = None,modal = 0,fl = 0)

        
        self._duration = 0 # Seconds that the progress bar takes to complete
            # [bruce 050415 comment: 'duration' is a public attribute, used by external code
            #  after the progress bar is hidden and the launch method has returned.]
            # [bruce 060103: I've now removed that kluge from runSim.py.
            #  This attr should now be considered private.
            #  I think I'll rename it to '_duration' to verify that. ####@@@@]

    # Start the progressbar [see also StatusBar.py's show_progressbar_and_stop_button, which is a modified copy of this method]
    def launch( self , nsteps, filename = '', caption = "Progress", message = "Calculating...", show_duration = 0):
        """Launch a progress bar dialog, and update it while a file is being written
        by some other process, to show the size of that file as progress, while waiting
        for that size to reach a given value; when it does, hide the dialog and return 0.
        If the user first presses the Abort button on the dialog, hide it and return 1.
        Parameters:
            nsteps - total steps for the progress bar (final size in bytes of filename)
            filename - name of file we are waiting for.
            caption - dialog caption
            message - text that appears above the progress bar
            show_duration - if True, display duration (in seconds) below progressbar
        Return value: 0 if file reached desired size, 1 if user hit abort button.
        """
        #bruce 050415 revised docstring, renamed dflag -> show_duration
        self.abort = False
        filesize = 0
        sinc = .1
        self.stime = time.time()
        
        # This is a temporary fix for bug #490.  Mark 050325
        # [bruce 050415 comment: Mark's comment#1 in bug 490 says that its effect
        #  is to remove the progressbar from the dialog during Minimize.
        #  Note that this is hiding or showing self.progressbar, not self as in
        #  the code below. ###e should change this to use a new optional flag]
        if caption.startswith("Adjust") or caption.startswith("Minimiz"): # KLUGE. match Adjust or Minimize or Minimizing [bruce 060705]
            self.progress.hide()
        else:
            self.progress.show()
        
        # Set up and show progress box
        # Need to set the border icon to "minimize", "simulator" or default based on flag.  Later...
        self.setCaption(caption)
        self.msgLabel.setText(message)
        self.msgLabel2.setText('')
        self.progress.setTotalSteps(nsteps) # nsteps = final moviefile size in bytes.
        self.progress.setProgress(0)
        self.show() # Show the progressbar dialog

        # Main loop
        while filesize < nsteps:
            if os.path.exists(filename): filesize = os.path.getsize(filename)
            self.progress.setProgress( filesize )
            import env
            env.call_qApp_processEvents()
                # Process queued events (i.e. clicking Abort button).
            
            if show_duration: # Display duration.
                elapsedtime = self._duration
                self._duration = time.time() - self.stime
                if elapsedtime == self._duration: continue
                elapmsg = "Elapsed Time: " + hhmmss_str(int(self._duration))
                self.msgLabel2.setText(elapmsg) 
            
            if self.abort: # User hit abort button
                self.hide()
                return 1

            time.sleep(sinc) # Take a rest
            
        # End of Main loop
        self.progress.setProgress(nsteps) # 100% done
        self._duration = time.time() - self.stime
        time.sleep(0.1)  # Give the progress bar a moment to show 100%
        self.hide()
        self.progress.reset() # Reset the progress bar.
            # [bruce 050415 comment: we should probably reset it at start of launch method, too. ###e]
        return 0
        
    def abort_run(self):
        "Slot for abort button"
        
        # Added confirmation before aborting as part of fix to bug 915. Mark 050824.
        ret = QMessageBox.warning( self, "Confirm",
            "Please confirm you want to abort.\n",
            "Confirm",
            "Cancel", 
            None, 
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
        if ret==0: # Confirmed
            self.abort = True

    def reject(self):
        '''Slot for Escape key or when the user hits the close button in the dialog border. 
        
        From the Qt documentation:
        "If the user presses the Escape key in a dialog, QDialog.reject() will be called. 
        This will cause the window to close, but note that no closeEvent will occur."
        
        In other words, hitting the Escape key closes the dialog and it cannot be 
        retrieved.  This is very confusing since the simulation run is still running, but
        there is no way to see progress info or abort the run.  To fix this situation,
        we simply call abort_run if QDialog.reject() is called.
        '''
        self.abort_run()
        
    pass # end of class ProgressBar

# end
