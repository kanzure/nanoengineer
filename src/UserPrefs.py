# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
UserPrefs.py

$Id$
'''
__author__ = "Mark"

from qt import *
from UserPrefsDialog import UserPrefsDialog
from preferences import prefs_context
import os, sys


def get_gamess_path(parent):
    '''Present user with a dialog to select the GAMESS executable.
    This routine also updates the shelf with the GAMESS executable path.
    '''
    from platform import get_rootdir
    
    gmspath = str(QFileDialog.getOpenFileName(
                    get_rootdir(), # Def
                    None,
                    parent,
                    None,
                    "Choose GAMESS executable." ))
                
    if not gmspath: # Cancelled.
        return None

    if not os.path.exists(gmspath): # User typed in name that doesn't exist
        return None
        
    prefs = prefs_context()
    prefs['A6/gmspath'] = str(gmspath)
        
    return gmspath
        
class UserPrefs(UserPrefsDialog):
    '''The User Preferences dialog used for accessing and changing user preferences
    '''
       
    def __init__(self, assy):
        UserPrefsDialog.__init__(self)
        self.history = assy.w.history
        self.glpane = assy.o
        self.gmspath = None
        
    def showDialog(self):
        '''Display the Preferences dialog'''
        if self._setup(): return
        self.exec_loop()

    ###### Private methods ###############################
    
    def _setup(self):
        ''' Setup widgets to initial (default or defined) values.
        '''
        
        
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")
            
        self._load_userprefs()
        
        if self.gmspath:
            self.gamess_path_linedit.setText(self.gmspath)
            
        return 0
        
    def _load_userprefs(self):
        '''Load user preferences from the shelf
        '''
        prefs = prefs_context()
        self.gmspath = prefs.get('A6/gmspath')
    
    def _save_userprefs(self):
        '''Store user preferences to the shelf
        '''
        if self.gmspath:
            prefs['gmspath'] = self.gmspath

    ###### End of private methods. ########################
    
    ##########Slot methods for some GUI controls################   

    def display_compass(self, val):
        '''Display or Hide the Compass
        '''
        self.glpane.displayCompass = val
        self.glpane.gl_update()
        
    def display_origin_axis(self, val):
        '''Display or Hide Origin Axis
        '''
        self.glpane.displayOriginAxis = val
        self.glpane.gl_update()
        
    def display_pov_axis(self, val):
        '''Display or Hide Point of View Axis
        '''
        self.glpane.displayPOVAxis = val
        self.glpane.gl_update()

    def set_compass_position(self, val):
        '''Set position of compass
        '''
        self.glpane.compassPosition = val
        self.glpane.gl_update()

    def set_gamess_path(self):
        self.gmspath = get_gamess_path(self)
        if self.gmspath:
            self.gamess_path_linedit.setText(self.gmspath)
        
    def accept(self):
        """The slot method for the 'OK' button."""
        QDialog.accept(self)
    
    def reject(self):
        """The slot method for the 'Cancel' button."""
        QDialog.reject(self)