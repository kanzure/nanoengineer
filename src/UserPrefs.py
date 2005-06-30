# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
UserPrefs.py

$Id$
'''
__author__ = "Mark"

from qt import *
from UserPrefsDialog import UserPrefsDialog
import preferences
import os, sys
from constants import *

modes = ['SELECTMOLS', 'SELECTATOMS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']
default_bgcolor = [ (189/255.0, 228/255.0, 238/255.0), # Select Chunks
                                (189/255.0, 228/255.0, 238/255.0), # Select Atoms
                                (254/255.0, 173/255.0, 246/255.0), # Move Chunks
                                (74/255.0, 186/255.0, 226/255.0), # Build
                                (103/255.0, 124/255.0, 53/255.0), # Cookie Cutter
                                (199/255.0, 100/255.0, 100/255.0), # Extrude
                                (200/255.0, 200/255.0, 200/255.0), # Fuse Chunks
                                (189/255.0, 228/255.0, 238/255.0)] # Movie Player

def get_gamess_path(parent):
    '''Present user with the Qt file chooser to select the GAMESS executable.
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
    
    # Save GAMESS executable path in prefs db.    
    prefs = preferences.prefs_context()
    prefs[gmspath_prefs_key] = str(gmspath)
        
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
        # This sends a signal to self.setup_current_page(), which will call self._setup_general_page()
        self.prefs_tab.setCurrentPage(0) 
        self.exec_loop()

    ###### Private methods ###############################
    
    def _setup_general_page(self):
        ''' Setup widgets to initial (default or defined) values on the general page.
        '''

        self.display_compass_checkbox.setChecked(self.glpane.displayCompass)
        self.compass_position_btngrp.setButton(self.glpane.compassPosition)
        self.display_origin_axis_checkbox.setChecked(self.glpane.displayOriginAxis)
        self.display_pov_axis_checkbox.setChecked(self.glpane.displayPOVAxis)
                
        # GAMESS path label
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")

        # Get GAMESS executable path from prefs db and update the lineEdit widget.
        prefs = preferences.prefs_context()
        self.gmspath = prefs.get(gmspath_prefs_key)
        
        if self.gmspath:
            self.gamess_path_linedit.setText(self.gmspath)
        else:
            self.gamess_path_linedit.setText('')
        
        return 0

    def _setup_background_page(self):
        ''' Setup widgets to initial (default or defined) values on the background page.
        '''
        self.mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        self.bg_solid_setup()
                        
    def _update_prefs(self):
        '''Update user preferences in the shelf
        '''
        prefs = preferences.prefs_context()
        
        # Do this just in case the user typed in the GAMESS executable path by hand.
        # We do not need to check whether the path exists as this is checked
        # each time GAMESS is launched.  If the path is wrong, the user will be
        # alerted and asked to supply a new path via the file chooser.
        # Mark 050629
        self.gmspath = str(self.gamess_path_linedit.text())
        
        # General tab prefs
        general_changes = { displayCompass_prefs_key: self.glpane.displayCompass,
                            compassPosition_prefs_key: self.glpane.compassPosition,
                            displayOriginAxis_prefs_key: self.glpane.displayOriginAxis,
                            displayPOVAxis_prefs_key: self.glpane.displayPOVAxis,
                            gmspath_prefs_key: self.gmspath }
        
        prefs.update(general_changes) # Open prefs db once.

    ###### End of private methods. ########################
    
    ########## Slot methods for "General" page widgets ################   

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
        '''Slot for GAMESS path "Modify" button.
        '''
        self.gmspath = get_gamess_path(self)
        if self.gmspath:
            self.gamess_path_linedit.setText(self.gmspath)
        else:
            self.gamess_path_linedit.setText('')
            
    ########## End of slot methods for "General" page widgets ###########
    
    ########## Slot methods for "Background" page widgets ################

    def mode_changed(self, val):
        self.bg_solid_setup()
        
    def bg_solid_setup(self):
        '''Setup the BG color page for a solid fill type.
        '''
        self.color1_lbl.setText("Color :")
        r, g, b = self.get_mode_backgroundColor(modes[self.mode_combox.currentItem()])
        self.color1_frame.setPaletteBackgroundColor(QColor(r, g, b))
        
        # Hide the gradient widgets - don't know if I'll be able to get "Gradient" backgrounds working by A6.
        # Mark 050630
        self.color2_lbl.hide()
        self.color2_frame.hide()
        self.color2_btn.hide()
        self.gradient_orient_btngrp.hide()
    
    def get_mode_backgroundColor(self, modename):
        "Returns the RGB integer values of a mode given a mode name."
        
#        print "modename =", modename
        key = "mode %s backgroundColor" % modename
        prefs = preferences.prefs_context()
        
        # bgcolor is set to the mode's background color if found in the prefs db.
        # or the mode's default background color if not found in the prefs db.
        bgcolor = prefs.get( key, default_bgcolor[self.mode_combox.currentItem()] )
        
        # Compute r, g, b integer values of mode's background color
        r = int (bgcolor[0] * 255)
        g = int (bgcolor[1] * 255)
        b = int (bgcolor[2] * 255) 
        return r, g, b

    def edit_color1(self):
        '''Change "color1" of a mode's background color.  This is the color for solid backgrounds.
        color1 is the top (vertical) or left (horizontal) color for gradient backgrounds.
        '''
        # get r, g, b values of current background color
        r, g, b = self.get_mode_backgroundColor(modes[self.mode_combox.currentItem()])

        # allow user to select a new background color and set it.
        # bruce 050105: now this new color persists after new files are opened,
        # and into new sessions as well.
        c = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if c.isValid():
            bgcolor = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
            if self.glpane.mode.modename == modes[self.mode_combox.currentItem()]:
                self.glpane.mode.set_backgroundColor( bgcolor )
                self.glpane.gl_update()
            else:
                self.set_mode_backgroundColor(modes[self.mode_combox.currentItem()], bgcolor)
            self.color1_frame.setPaletteBackgroundColor(c)
            
    def set_mode_backgroundColor(self, modename, bgcolor):
        key = "mode %s backgroundColor" % modename
        prefs = preferences.prefs_context()
        prefs[key] = bgcolor # this stores the new color into a prefs db file
        return
    
    ########## End of slot methods for "Background" page widgets ###########

    ########## Slot methods for top level widgets ################
    
    def setup_current_page(self, pagename):
        if pagename == 'General':
            self._setup_general_page()
        elif pagename == 'Background':
            self._setup_background_page()
        else:
            print 'Error: Page unknown: ', pagename
            
    def accept(self):
        '''The slot method for the 'OK' button.'''
        self._update_prefs()
        QDialog.accept(self)
        
    def reject(self):
        '''The slot method for the "Cancel" button.'''
        # The Cancel button has been removed, but this still gets called
        # when the user hits the dialog's "Close" button in the dialog's border.
        # Since I've not implemented 'Cancel', it is safer to go ahead and
        # save all preferences anyway.  Otherwise, any changed preferences
        # will not be persistent (after this session).  
        # This will need to be removed when we implement a true cancel function.
        # Mark 050629.
        self._update_prefs()
        QDialog.reject(self)