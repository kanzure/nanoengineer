# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
zoomMode.py -- zoom mode.

$Id$
"""
__author__ = "Mark"

from modes import *
#import preferences

class zoomMode(basicMode):

    # class constants
    #
    #  We need to mimic the previous mode, including the background color, dashboard
    # and default_mode_status_text.
    # 
    backgroundColor = 0.5, 0.5, 0.5
    modename = 'ZOOM'
    default_mode_status_text = "Mode: Zoom"  # This should be set to the previous mode's text

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self):
        # Set background color to the previous mode's bg color
        self.backgroundColor = self.o.prevModeColor
        basicMode.Enter(self)

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.o.setCursor(self.w.ZoomCursor)
        
        # Get the previous mode's dashboard widget and show it.
        self.getDashboard() 
        self.dashboard.show()
        
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor
        self.dashboard.hide()

    # Dashboard methods for zoomMode

    def getDashboard(self):
        """Return the dashboard widget for the previous mode.
        """
        prevMode = self.o.prevMode
        if prevMode == 'SELECTMOLS':
            self.dashboard = self.w.selectMolDashboard
        elif prevMode == 'SELECTATOMS':
            self.dashboard = self.w.selectAtomsDashboard
        elif prevMode == 'MODIFY':
            self.dashboard = self.w.moveMolDashboard
        elif prevMode == 'DEPOSIT':
            self.dashboard = self.w.depositAtomDashboard
        elif prevMode == 'MOVIE':
            self.dashboard = self.w.moviePlayerDashboard
            
    # mouse and key events

    def leftDown(self, event):
        return
    
    def leftDrag(self, event):
        return

    def leftUp(self, event):
        self.o.mode.Done()
        self.o.setMode(self.o.prevMode)

    def Draw(self):
        return

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Done', self.Done),
         ]

    pass # end of class zoomMode