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
        progressBarDialog.__init__(self)

    # Start the progressbar
    def launch( self , nsteps, filename = '', caption = "Progress", message = "Calculating..."):
        """Launch a progress bar dialog and update while a file is being written.
            nsteps - total steps for the progress bar (final size in bytes of filename)
            filename - name of file we are waiting for.
            caption - dialog caption
            message - text that appears above the progress bar
        """
        
        self.abort = False
        filesize = 0
        sinc = .1
        self.stime = time.time()
        self.timeout = 10 # timeout period

#        print "ProgressBar: nsteps =",nsteps,", filename =", filename
        
        # Set up and show progress box
        # Need to set the border icon to "minimize", "simulator" or default based on flag.  Later...
        self.setCaption(caption)
        self.msgLabel.setText(message)
        self.progress.setTotalSteps(nsteps)
        self.progress.setProgress(0)
        self.show() # Show the Progress Box

        # The file may not yet exist.  Let's wait for it...
        while not os.path.exists(filename): 
            time.sleep(sinc)
            w = time.time() - self.stime
            if w > self.timeout: 
                self.hide()
                QMessageBox.warning(self, "File hasn't showed up:", filename)
                return 1 # File never showed up.

        # Main loop
        while filesize < nsteps:
            filesize = os.path.getsize(filename)
            self.progress.setProgress( filesize )
            qApp.processEvents()
            time.sleep(sinc)
            
            if self.abort: # User hit abort button
                self.hide()
                return 1

        # End of Main loop
        
        self.hide()
        return 0
        
    def abort(self):
        """Slot for abort button"""
        self.abort = True
