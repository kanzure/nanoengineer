# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
ProgressBar.py

$Id$
'''
__author__ = "Mark"

import os, time
from qt import *
from ProgressBarDialog import *

class ProgressBar( progressBarDialog ):
    def __init__(self):
        ### Huaicai 1/10/05: make the dialog as a modal dialog, 
        ### otherwise, if the user close the main window, it will get 
        ### "RuntimeError: underlying C/C++ object has been deleted   
        progressBarDialog.__init__(self, None, None, True)
        
        self.duration = 0 # Seconds that the progress bar takes to complete

    # Start the progressbar
    def launch( self , nsteps, filename = '', caption = "Progress", message = "Calculating...", dflag = 0):
        """Launch a progress bar dialog and update while a file is being written.
            nsteps - total steps for the progress bar (final size in bytes of filename)
            filename - name of file we are waiting for.
            caption - dialog caption
            message - text that appears above the progress bar
            dflag - if True, display duration (in seconds) below progressbar
        """
        
        self.abort = False
        filesize = 0
        sinc = .1
        self.stime = time.time()
        
        # This is a temporary fix for bug #490.  Mark 050325
        if caption == "Minimize": 
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
            
            if dflag: # Display duration.
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
        time.sleep(0.1)  # Give the progress bar a moment show 100%
        self.hide()
        self.progress.reset() # Reset the progress bar.
        return 0
        
    def abort(self):
        """Slot for abort button"""
        self.abort = True
        
    def hhmmss_str(self, secs):
        """Given the number of seconds, return the elapsed time as a string in hh:mm:ss format"""
        if secs < 3600: hours = 0
        else: hours = int(secs/3600.0)
        minutes = int(secs/60.0 - hours*60.0)
        seconds = int(secs - minutes*60.0)
        if hours:
            return '%02d:%02d:%02d' % (hours, minutes, seconds)
        else:
            return '%02d:%02d' % (minutes, seconds)