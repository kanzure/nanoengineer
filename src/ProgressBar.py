# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
ProgressBar.py

$Id$
'''
__author__ = "Mark"

import os, time
from qt import *


#bruce 050415 I want to rename progressBarDialog to ProgressBarDialog
# but plan to ask someone else to do it in the .ui file.
# So I'll temporarily kluge this to work either way:

progressBarDialog = ProgressBarDialog = None

from ProgressBarDialog import * # should define one or the other of those two classnames but not both

assert not (progressBarDialog and ProgressBarDialog), "p and P are %r and %r" % (progressBarDialog , ProgressBarDialog)

ProgressBarDialog = progressBarDialog or ProgressBarDialog
del progressBarDialog

#end bruce 050415 temporary kluge


class ProgressBar( ProgressBarDialog ):
    def __init__(self):
        ### Huaicai 1/10/05: make the dialog as a modal dialog, 
        ### otherwise, if the user close the main window, it will get 
        ### "RuntimeError: underlying C/C++ object has been deleted   
        ProgressBarDialog.__init__(self, None, None, True)
        
        self.duration = 0 # Seconds that the progress bar takes to complete
            # [bruce 050415 comment: this is a public atttribute, used by external code
            #  after the progress bar is hidden and the launch method has returned.]

    # Start the progressbar
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
        if caption.startswith("Minimize"): #bruce 050415 changed == to startswith
            self.progress.hide()
        else:
            self.progress.show()

#        print "ProgressBar: nsteps =",nsteps,", filename =", filename
        
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
            qApp.processEvents() # Process queued events (i.e. clicking Abort button).
            
            if show_duration: # Display duration.
                elapsedtime = self.duration
                self.duration = time.time() - self.stime
                if elapsedtime == self.duration: continue
                elapmsg = "Elasped Time: " + self.hhmmss_str(int(self.duration))
                self.msgLabel2.setText(elapmsg) 
            
            if self.abort: # User hit abort button
                self.hide()
                return 1

            time.sleep(sinc) # Take a rest
            
        # End of Main loop
        self.progress.setProgress(nsteps) # 100% done
        self.duration = time.time() - self.stime
        time.sleep(0.1)  # Give the progress bar a moment to show 100%
        self.hide()
        self.progress.reset() # Reset the progress bar.
            # [bruce 050415 comment: we should probably reset it at start of launch method, too. ###e]
        return 0
        
    def abort(self):
        """Slot for abort button"""
        self.abort = True
        
    def hhmmss_str(self, secs):
        """Given the number of seconds, return the elapsed time as a string in hh:mm:ss format"""
        # [bruce 050415 comment: this is sometimes called from external code
        #  after the progressbar is hidden and our launch method has returned.]
        # bruce 050415 revising this to use pure int computations (so bugs from
        #  numeric roundoff can't occur) and to fix a bug when hours > 0 (commented below).
        secs = int(secs)
        hours = int(secs/3600) # use int divisor, not float
            # (btw, the int() wrapper has no effect until python int '/' operator changes to produce nonints)
        minutes = int(secs/60 - hours*60)
        seconds = int(secs - minutes*60 - hours*3600) #bruce 050415 bugfix: also subtract hours
        if hours:
            return '%02d:%02d:%02d' % (hours, minutes, seconds)
        else:
            return '%02d:%02d' % (minutes, seconds)
        pass
    pass # end of class ProgressBar

# end
