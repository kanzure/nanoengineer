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
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.o.assy.selwhat = 0

    def init_gui(self):

        self.w.toolsMoviePlayerAction.setOn(1) # toggle on the Movie Player icon

        # Disable some action items in the main window.
        self.w.modifyMinimizeAction.setEnabled(0) # Disable "Minimize"
        self.w.toolsSimulatorAction.setEnabled(0) # Disable "Simulator"
        self.w.fileSaveAction.setEnabled(0) # Disable "File Save"
        self.w.fileSaveAsAction.setEnabled(0) # Disable "File Save As"
        self.w.fileOpenAction.setEnabled(0) # Disable "File Open"
        self.w.fileCloseAction.setEnabled(0) # Disable "File Close"
        self.w.fileInsertAction.setEnabled(0) # Disable "File Insert"
        self.w.editDeleteAction.setEnabled(0) # Disable "Delete"
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
        
        # MP dashboard initialization.
        self.w.frameNumberSB.setValue(self.o.assy.m.currentFrame) # SB = Spinbox
        self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
        self.w.moviePlayerDashboard.show()
        
        if self.o.assy.m.filename: # We have a movie file ready.  It's showtime!
            self.o.assy.m._setup() # Cue movie.
        else:
            self.o.assy.m._controls(0) # Movie control buttons are disabled.

    def haveNontrivialState(self):
        self.o.assy.m._close()
        return False

    def StateDone(self):
        self.o.assy.m._close()
        return None

    def restore_gui(self):
        self.w.moviePlayerDashboard.hide()
        self.w.modifyMinimizeAction.setEnabled(1) # Enable "Minimize"
        self.w.toolsSimulatorAction.setEnabled(1) # Enable "Simulator"
        self.w.fileSaveAction.setEnabled(1) # Enable "File Save"
        self.w.fileSaveAsAction.setEnabled(1) # Enable "File Save"
        self.w.fileOpenAction.setEnabled(1) # Enable "File Open"
        self.w.fileCloseAction.setEnabled(1) # Enable "File Close"
        self.w.fileInsertAction.setEnabled(1) # Enable "File Insert"
        self.w.editDeleteAction.setEnabled(1) # Enable "Delete"
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Reset Movie', self.o.assy.m._reset),
            ('Done', self.Done)
         ]
                
    def Draw(self):
        basicMode.Draw(self)
        self.o.assy.draw(self.o)

    # mouse and key events
            
    def keyPress(self,key):
        
        # Disable delete key
        if key == Qt.Key_Delete: return 
        
        # Left or Down arrow keys - advance back one frame
        if key == Qt.Key_Left or key == Qt.Key_Down:
            self.o.assy.m._playFrame(self.o.assy.m.currentFrame - 1)
        
        # Right or Up arrow keys - advance forward one frame
        if key == Qt.Key_Right or key == Qt.Key_Up:
            self.o.assy.m._playFrame(self.o.assy.m.currentFrame +1)
        
        return