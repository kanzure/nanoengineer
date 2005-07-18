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

# This list of mode names correspond to the names listed in the modes combo box.
modes = ['SELECTMOLS', 'SELECTATOMS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']

# There is probably a more elegant way to do this.  I'll ask Bruce.  Mark 050718
style2display = {'VdW':diVDW,'CPK':diCPK,'Tubes':diTUBES,'Lines':diLINES}
display2style = {diVDW:'VdW',diCPK:'CPK',diTUBES:'Tubes',diLINES:'Lines'}

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

def validate_gamess_path(parent, gmspath):
    '''Checks that gmspath (GAMESS executable) exists.  If not, the user is asked
    if they want to use the File Chooser to select the GAMESS executable.
    This function does not check whether the GAMESS path is actually GAMESS 
    or if it is the correct version of GAMESS for this platform (i.e. PC GAMESS for Windows).
    Returns: 
            - "gmspath" if it is validated or if the user does not want to change it for any reason, or
            - "new_gmspath" if gmspath is invalid and the user selected a new GAMESS executable.
    '''
        
    if not gmspath: # It is OK if gmspath is empty.
        return ''
    elif os.path.exists(gmspath):
        return gmspath
    else:
        ret = QMessageBox.warning( parent, "GAMESS Executable Path",
            gmspath + " does not exist.\nDo you want to use the File Chooser to browse for the GAMESS executable?",
            "&Yes", "&No", None,
            0, 1 )
                
        if ret==0: # Yes
            new_gmspath = get_gamess_path(parent)
            if not new_gmspath:
                return gmspath # Cancelled from file chooser.  Just return the original gmspath.
            else:
                return new_gmspath
            
        else: # No
            return gmspath

def get_rgb_from_bgcolor(bgcolor):
    "Returns the RGB integer values for bgcolor."
    r = int (bgcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
    g = int (bgcolor[1]*255 + 0.5)
    b = int (bgcolor[2]*255 + 0.5)
    return r, g, b
        

class UserPrefs(UserPrefsDialog):
    '''The User Preferences dialog used for accessing and changing user preferences
    '''
       
    def __init__(self, assy):
        UserPrefsDialog.__init__(self)
        self.win = assy.w
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
        ''' Setup widgets to initial (default or defined) values on the "General" page.
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
        self.gmspath = prefs.get(gmspath_prefs_key, '')
        self.gamess_path_linedit.setText(self.gmspath)
        
#        if self.gmspath:
#            self.gamess_path_linedit.setText(self.gmspath)
#        else:
#            self.gamess_path_linedit.setText('')

    def _setup_background_page(self):
        ''' Setup widgets to initial (default or defined) values on the "Background" page.
        '''
        # Set the mode drop box to the current mode, 
        # or "Select Chunks" if the mode is not in the "modes" list.
        if self.glpane.mode.modename in modes:
            self.mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        else:
            self.mode_combox.setCurrentItem(0) # Set to Select Chunks

        self.bg_solid_setup()

    def _setup_display_page(self):
        ''' Setup widgets to initial (default or defined) values on the "Display" page.
        '''
        # Set the mode drop box to the current mode, 
        # or "Select Chunks" if the mode is not in the "modes" list.
        if self.glpane.mode.modename in modes:
            self.display_mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        else:
            self.display_mode_combox.setCurrentItem(0) # Set to Select Chunks
            
        self.update_display_style()

    def _setup_history_page(self):
        ''' Setup widgets to initial (default or defined) values on the "History" page.
        '''
        self.msg_serial_number_checkbox.setChecked(self.history.msg_serial_number)
        self.msg_timestamp_checkbox.setChecked(self.history.msg_timestamp)

    def _setup_caption_page(self):
        ''' Setup widgets to initial (default or defined) values on the "Caption" page.
        '''
        self.caption_prefix_linedit.setText(self.win.caption_prefix)
        self.caption_suffix_linedit.setText(self.win.caption_suffix)
        self.caption_fullpath_checkbox.setChecked(self.win.caption_fullpath)
                                        
    def _update_prefs(self):
        '''Update user preferences and store them in the shelf.
        This method has two parts:
            1. Update the preference variables stored in various objects (i.e. win, assy, history, etc.)
            2. Save the prefences to the shelf.
        '''
        
        # Do this just in case the user typed in the GAMESS executable path by hand.
        # We do not need to check whether the path exists as this is checked
        # each time GAMESS is launched.  If the path is wrong, the user will be
        # alerted and asked to supply a new path via the file chooser.
        # Mark 050629
        self.gmspath = str(self.gamess_path_linedit.text())
        
        # Bruce suggested I validate the gamess path before updating the prefs.  
        # This works, but it needs more thought.  It will annoy users more than
        # help them.  I'm leaving this for later until I discuss with Bruce.
        # Mark 050630.
#        self.gmspath = validate_gamess_path(self, str(self.gamess_path_linedit.text()))
        
        # Update Caption prefs #########################################
        # The prefix and suffix updates should be done via slots and include a validator.
        # Mark 050716.
        prefix = QString(self.caption_prefix_linedit.text())
        
        text = prefix.stripWhiteSpace() # make sure prefix is not just whitespaces
        if text: 
            self.win.caption_prefix = str(text) + ' '
        else:
            self.win.caption_prefix = ''
        
        suffix = QString(self.caption_suffix_linedit.text())
        
        text = suffix.stripWhiteSpace() # make sure suffix is not just whitespaces
        if text: 
            self.win.caption_suffix = ' ' + str(text)
        else:
            self.win.caption_suffix = ''
            
        self.win.update_mainwindow_caption(self.win.assy.has_changed())
        
        # Update History pref variables
        self.history.msg_serial_number = self.msg_serial_number_checkbox.isChecked()
        self.history.msg_timestamp = self.msg_timestamp_checkbox.isChecked()
        
        # General tab prefs
        general_changes = { displayCompass_prefs_key: self.glpane.displayCompass,
                                            compassPosition_prefs_key: self.glpane.compassPosition,
                                            displayOriginAxis_prefs_key: self.glpane.displayOriginAxis,
                                            displayPOVAxis_prefs_key: self.glpane.displayPOVAxis,
                                            gmspath_prefs_key: self.gmspath,
                                            defaultDisplayMode_prefs_key: self.glpane.display,
                                            captionPrefix_prefs_key: self.win.caption_prefix,
                                            captionSuffix_prefs_key: self.win.caption_suffix,
                                            captionFullPath_prefs_key: self.win.caption_fullpath,
                                            historyMsgSerialNumber_prefs_key: self.history.msg_serial_number,
                                            historyMsgTimestamp_prefs_key: self.history.msg_timestamp
                                             }
        
        prefs = preferences.prefs_context()
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
            
    ########## End of slot methods for "General" page widgets ###########
    
    ########## Slot methods for "Background" page widgets ################

    def mode_changed(self, val):
        '''Slot called when the user changes the mode in the drop box.
        '''
        # Gradient option is disabled for A6.  This will alway call bg_solid_setup() until A7.
        if self.fill_type_combox.currentText() == 'Solid':
            self.bg_solid_setup()
        else: # Gradient
            self.bg_gradient_setup()
    
    def fill_type_changed(self, ftype):
        '''Slot called when the user changes the Fill Type.
        '''
        if ftype == 'Solid':
            self.bg_solid_setup()
        else:
            self.bg_gradient_setup()
        
    def bg_solid_setup(self):
        '''Setup the BG color page for a solid fill type.
        '''
        self.color1_lbl.setText("Color :")
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        r, g, b = get_rgb_from_bgcolor(mode.backgroundColor)
        self.color1_frame.setPaletteBackgroundColor(QColor(r, g, b))
        
        # Hide the gradient widgets
        # I doubt I'll be able to get "Gradient" backgrounds working by A6.
        # Mark 050630
        self.color2_lbl.hide()
        self.color2_frame.hide()
        self.choose_color2_btn.hide()
        self.gradient_orient_btngrp.hide()
    
    def bg_gradient_setup(self):
        '''Setup the Background page for a gradient fill type.
        This is never called in A6.
        '''
        self.color1_lbl.setText("Color 1 :")
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        r, g, b = get_rgb_from_bgcolor(mode.backgroundColor)
        self.color1_frame.setPaletteBackgroundColor(QColor(r, g, b))
        self.color2_frame.setPaletteBackgroundColor(QColor(r, g, b))
        
        # Show the gradient widgets.
        self.color2_lbl.show()
        self.color2_frame.show()
        self.choose_color2_btn.show()
        self.gradient_orient_btngrp.show()

    def change_bgcolor1(self):
        '''Change a mode's background color.
        '''
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        r, g, b = get_rgb_from_bgcolor(mode.backgroundColor)

        # Allow user to select a new background color and set it.
        c = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if c.isValid():
            bgcolor = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
            mode.set_backgroundColor( bgcolor )
            self.color1_frame.setPaletteBackgroundColor(c)
                
    def restore_default_bgcolor(self):
        '''Slot for "Restore Default Color" button, which restores the selected mode's bg color.
        '''
        # Get the mode object selected in the combo box.
        mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        # Set the background color to the default.
        mode.set_backgroundColor(mode.__class__.backgroundColor)
        # Now update the color square (frame).
        r, g, b = get_rgb_from_bgcolor(mode.backgroundColor)
        c = QColor(r, g, b)
        self.color1_frame.setPaletteBackgroundColor(c)
        # If the selected mode is the current mode, update the glpane to display the new (default) bg color.
        if mode == self.glpane.mode:
            self.glpane.gl_update()
        
    ########## End of slot methods for "Background" page widgets ###########

    ########## Slot methods for "Display" page widgets ################

    # FYI, I use the term "style" to refer to the mode's display here.  It was too
    # confusing to use both "mode" (as in the tool) and "display" (as in display mode)
    # together in the "Display" page slots/methods.  I substitute "style" for "display" 
    # throughout here.  I think we should replace the mode attribute "display" with a 
    # less ambiguous name like "rendering_style".
    # Mark 050718.
    
    def display_mode_changed(self, modename):
        '''Slot called when the user changes the mode in the drop box.
        '''
        self.update_display_style()

    def update_display_style(self):
        '''Updates the Style combobox based on the display_mode_combox setting.
        '''
        mode = self.glpane._find_mode(modes[self.display_mode_combox.currentItem()])
        display_key = mode.display
        style = display2style[display_key]
        self.display_style_combox.setCurrentText(style)
    
    def display_style_changed(self, style):
        '''Slot called when the user changes the Style.
        '''
        mode = self.glpane._find_mode(modes[self.display_mode_combox.currentItem()])
        style_key = str(style)
        display = style2display[style_key]
        mode.set_display( style2display[style_key] )
        if mode == self.glpane.mode:
            self.win.setDisplay(style2display[style_key])  # Does gl_update().
            
    def restore_default_display_mode(self):
        '''Slot for "Restore Default" button, which restores the selected mode's display style.
        '''
        # Get the mode object selected in the combo box.
        mode = self.glpane._find_mode(modes[self.display_mode_combox.currentItem()])
        # Set the display to the default.
        mode.set_display(mode.__class__.display)
        # If the selected mode is the current mode, update the glpane to display the new (default) bg color.
        if mode == self.glpane.mode:
            self.win.setDisplay(mode.__class__.display)  # Does gl_update().
        self.update_display_style() # Update the style combobox to the default style.
        
    ########## End of slot methods for "Display" page widgets ###########

    ########## Slot methods for "Caption" page widgets ################
        
    def set_caption_fullpath(self, val):
        self.win.caption_fullpath = val
        self.win.update_mainwindow_caption(self.win.assy.has_changed())
        
    ########## End of slot methods for "Caption" page widgets ###########

    ########## Slot methods for top level widgets ################
    
    def setup_current_page(self, pagename):
        if pagename == 'General':
            self._setup_general_page()
        elif pagename == 'Background':
            self._setup_background_page()
        elif pagename == 'Display':
            self._setup_display_page()
        elif pagename == 'History':
            self._setup_history_page()
        elif pagename == 'Caption':
            self._setup_caption_page()
        else:
            print 'Error: Preferences page unknown: ', pagename
            
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