# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movieMode.py -- movie player mode.

$Id$
"""

__author__ = "Mark"

from modes import *

class movieMode(basicMode):
    """ This class is used to play movie files.
       Users know it as "Movie mode".
    """

    # class constants
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    modename = 'MOVIE'
    default_mode_status_text = "Mode: Movie Player"
    
    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and init_gui (fyi)
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.o.assy.selwhat = 0

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        
        # We have a moviefile ready to go.  It's showtime!!!
        self.w.toolsMoviePlayerAction.setOn(1) # toggle on the Movie Player icon
#        self.w.moviePauseAction.setVisible(0)
#        self.w.moviePlayAction.setVisible(1)
#        self.w.movieProgressBar.reset()
#       self.w.frameNumberLCD.display(self.o.assy.currentFrame)
        self.w.frameNumberSB.setValue(self.o.assy.m.currentFrame) # SB = Spinbox
#        self.w.frameNumberSL.setMaxValue(self.o.assy.m.totalFrames)
#        self.w.frameNumberSL.setValue(self.o.assy.m.currentFrame) # SL = Slider
        
        self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
        self.w.moviePlayerDashboard.show()
        
        self.w.modifyMinimizeAction.setEnabled(0) # Disable "Minimize"
        self.w.toolsSimulatorAction.setEnabled(0) # Disable "Simulator"
        self.w.fileSaveAction.setEnabled(0) # Disable "File Save"
        self.w.fileSaveAsAction.setEnabled(0) # Disable "File Save"
        self.w.fileOpenAction.setEnabled(0) # Disable "File Open"
        
        self.o.assy.m._setup() # Cue movie.

    # methods related to exiting this mode [bruce 040922 made these from
    # old Done method, and added new code; there was no Flush method]

    def haveNontrivialState(self):
#        print "movieMode.haveNontrivialState() called"
        self.o.assy.m._close()
        return False
        #return self.modified # bruce 040923 new code

    def StateDone(self):
#        print "movieMode.StateDone() called"
        self.o.assy.m._close()
        return None
    # we never have undone state, but we have to implement this method,
    # since our haveNontrivialState can return True
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
#        print "movieMode.restore_gui() called"
        self.w.moviePlayerDashboard.hide()
        self.w.modifyMinimizeAction.setEnabled(1) # Enable "Minimize"
        self.w.toolsSimulatorAction.setEnabled(1) # Enable "Simulator"
        self.w.fileSaveAction.setEnabled(1) # Enable "File Save"
        self.w.fileSaveAsAction.setEnabled(1) # Enable "File Save"
        self.w.fileOpenAction.setEnabled(1) # Enable "File Open"


    def makeMenus(self):
        self.Menu_spec = [
            None,
         ]
                
    def Draw(self):
        # bruce comment 040922: code is almost identical with modifyMode.Draw;
        # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
        basicMode.Draw(self)   
        #self.griddraw()
        if self.sellist: self.pickdraw()
        self.o.assy.draw(self.o)
        
    # other dashboard methods
    

        
    # mouse and key events
    
    def keyPress(self,key):
        if key == Qt.Key_Delete:
            print "delete key"
            pass
        if key == Qt.Key_End:
            pass
        if key == Qt.Key_Left or key == Qt.Key_Down:
            self.o.assy.m._playFrame(self.o.assy.m.currentFrame - 1)
        if key == Qt.Key_Right or key == Qt.Key_Up:
            self.o.assy.m._playFrame(self.o.assy.m.currentFrame +1)
        return