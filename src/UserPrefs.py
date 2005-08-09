# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
UserPrefs.py

$Id$

History:

Created by Mark.

Modified somewhat by Bruce 050805 for bond color prefs.
'''
__author__ = "Mark"

from qt import *
from UserPrefsDialog import UserPrefsDialog
import preferences
import os, sys
from constants import *
from debug import print_compact_traceback
import env
from widgets import RGBf_to_QColor #bruce 050805 moved RGBf_to_QColor from here to widgets.py
from prefs_widgets import connect_colorpref_to_colorframe
import platform

# This list of mode names correspond to the names listed in the modes combo box.
modes = ['SELECTMOLS', 'SELECTATOMS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']

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
        self._init_prefs()
        self.prefs_tab.setCurrentPage(0)  # Show General tab/page
        self.exec_loop()

    ###### Private methods ###############################
    
    def _init_prefs(self):
        '''Retreive preferences from the pref db that are needed before updating widgets in the UI.
        '''
        prefs = preferences.prefs_context()
        self.gmspath = prefs.get(gmspath_prefs_key, '')
        self.default_display_mode = prefs.get(defaultDisplayMode_prefs_key, diVDW)
        
        
    def _setup_general_page(self):
        ''' Setup widgets to initial (default or defined) values on the general page.
        '''

        self.display_compass_checkbox.setChecked(self.glpane.displayCompass)
        self.compass_position_btngrp.setButton(self.glpane.compassPosition)
        self.display_origin_axis_checkbox.setChecked(self.glpane.displayOriginAxis)
        self.display_pov_axis_checkbox.setChecked(self.glpane.displayPOVAxis)
                
        # GAMESS path label and value.
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")

        self.gamess_path_linedit.setText(self.gmspath) # Retrieved from _init_prefs().

    def _setup_background_page(self):
        ''' Setup widgets to initial (default or defined) values on the background page.
        '''
        # Set the mode drop box to the current mode, 
        # or "Select Chunks" if the mode is not in the "modes" list.
        if self.glpane.mode.modename in modes:
            self.mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        else:
            self.mode_combox.setCurrentItem(0) # Set to Select Chunks

        self.bg_mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        
        if self.bg_mode.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()

    def _setup_atoms_page(self):
        ''' Setup widgets to initial (default or defined) values on the display page.
        '''
        # Set colors for atom color swatches
##        self.atom_hilite_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(orange))
##        self.free_valence_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(red))

        #bruce 050805 new way (see comment in _setup_bonds_page):
        connect_colorpref_to_colorframe( atomHighlightColor_prefs_key, self.atom_hilite_color_frame)
        ## not implemented:
        ##   connect_colorpref_to_colorframe( freeValenceColor_prefs_key, self.free_valence_color_frame) #[problematic]
        connect_colorpref_to_colorframe( atomHotspotColor_prefs_key, self.hotspot_color_frame)

        # Bug 799 fix.  Mark 050731
        self.default_display_btngrp.setButton(self.default_display_mode) # Retrieved from _init_prefs().
            # bruce comments:
            # - it's wrong to use any other data source here than the prefs db, e.g. via env.prefs.
            # - the codes for the buttons are (by experiment) 2,4,5,3 from top to bottom. Apparently these
            #   match our internal display mode codes, and are set by buttongroup.insert in the pyuic output file,
            #   but for some reason the buttons are inserted in a different order than they're shown.

        return
    
    def _setup_bonds_page(self):
        ''' Setup widgets to initial (default or defined) values on the bonds page.
        '''
        # Set colors for bond color swatches
##        self.bond_hilite_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(blue))
##        self.bond_stretch_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(red))
##        self.bond_vane_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(violet)) # Purple
##        self.bond_cpk_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(gray))

        #bruce 050805 here's the new way: subscribe to the preference value,
        # but make sure to only have one such subs (for one widget's bgcolor) at a time.
        # The colors in these frames will now automatically update whenever the prefs value changes.
        ##e (should modify this code to share its prefskey list with the one for restore_defaults)
        connect_colorpref_to_colorframe( bondHighlightColor_prefs_key, self.bond_hilite_color_frame)
        connect_colorpref_to_colorframe( bondStretchColor_prefs_key, self.bond_stretch_color_frame)
        connect_colorpref_to_colorframe( bondVaneColor_prefs_key, self.bond_vane_color_frame)
        connect_colorpref_to_colorframe( bondCPKColor_prefs_key, self.bond_cpk_color_frame)

        # also handle the non-color prefs on this page:
        #  ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
        pibondstyle_sym = env.prefs[ pibondStyle_prefs_key]
        button_code = { 'multicyl':0,'vane':1, 'ribbon':2 }.get( pibondstyle_sym, 0)
            # Errors in prefs db are not detected -- we just use the first button because (we happen to know) it's the default.
            # This int encoding is specific to this buttongroup.
            # The prefs db and the rest of the code uses the symbolic strings listed above.
        self.high_order_bond_display_btngrp.setButton( button_code)

        #  ('pi_bond_letters', 'boolean',                     pibondLetters_prefs_key, False ),
        self.show_bond_labels_checkbox.setChecked( env.prefs[ pibondLetters_prefs_key] )
            # I don't know whether this sends the signal as if the user changed it
            # (and even if Qt doc says no, this needs testing since I've seen it be wrong about those things before),
            # but in the present code it doesn't matter unless it causes storing default value explicitly into prefs db
            # (I can't recall whether or not it does). Later this might matter more, e.g. if we have prefs-value modtimes.
            # [bruce 050806]

        # ('show_valence_errors',        'boolean', showValenceErrors_prefs_key,   True ),
        # (This is a per-atom warning, but I decided to put it on the Bonds page since you need it when
        #  working on high order bonds. And, since I could fit that into the UI more easily.)

        if hasattr(self, 'show_valence_errors_checkbox'):
            self.show_valence_errors_checkbox.setChecked( env.prefs[ showValenceErrors_prefs_key] )
            # note: this does cause the checkbox to send its "toggled(bool)" signal to our slot method.
        
        return
        
    def _setup_history_page(self):
        ''' Setup widgets to initial (default or defined) values on the history page.
        '''
        # History height widgets will be hidden for A6, to be reinstituted at a later time (A7 or A8) for
        # Bruce to decide.  He will be implementing this feature.  Mark 050731.
        self.history_height_lbl.hide()
        self.history_height_spinbox.hide()
        self.history_lines_lbl.hide()
        
        self.history_height_spinbox.setValue(self.history.history_height)
        self.msg_serial_number_checkbox.setChecked(self.history.msg_serial_number)
        self.msg_timestamp_checkbox.setChecked(self.history.msg_timestamp)

    def _setup_caption_page(self):
        ''' Setup widgets to initial (default or defined) values on the captions page.
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
        #bruce 050804/050806 comments: this method is wrong in at least these ways: ###@@@
        # - it doesn't yet include all the prefs. (But the new ones are being handled separately, anyway.)
        # - it's only called when we exit the dialog (or perhaps change the page), not when we e.g. choose individual new colors.
        #   But that will be fixed not here, but by making individual pref controls update those prefs when changed.
        #   That's already being done for the bond prefs and atom color prefs.
        # - it updates the prefs db even for values which were not stored there before and not changed by the user.
        #   [It's not clear that's wrong, but it does cause problems for change tracking,
        #    and it causes bugs when the default values are wrong in new prefs code under development.
        #    But probably those problems need to be addressed somehow within preferences.py itself.
        #    I have addressed them for change tracking, and maybe for making default values, when set explicitly,
        #    not get into the prefs db if nothing was yet there (but I'm not sure about that one #k).]
        
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
        # Will do later.  Mark 050716.
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
        # [this doesn't need to include the ones that update themselves whenever changed,
        #  and the code should be revised so that all of them do that,
        #  and then none of them will need to be updated here. bruce 050806 comment]
        self.history.history_height = self.history_height_spinbox.value()
        self.history.msg_serial_number = self.msg_serial_number_checkbox.isChecked()
        self.history.msg_timestamp = self.msg_timestamp_checkbox.isChecked()
        
        all_prefs = { displayCompass_prefs_key: self.glpane.displayCompass,
                            compassPosition_prefs_key: self.glpane.compassPosition,
                            displayOriginAxis_prefs_key: self.glpane.displayOriginAxis,
                            displayPOVAxis_prefs_key: self.glpane.displayPOVAxis,
                            gmspath_prefs_key: self.gmspath,
                            defaultDisplayMode_prefs_key: self.default_display_mode,
                            captionPrefix_prefs_key: self.win.caption_prefix,
                            captionSuffix_prefs_key: self.win.caption_suffix,
                            captionFullPath_prefs_key: self.win.caption_fullpath,
                            historyHeight_prefs_key: self.history.history_height,
                            historyMsgSerialNumber_prefs_key: self.history.msg_serial_number,
                            historyMsgTimestamp_prefs_key: self.history.msg_timestamp
                            }
        
        prefs = preferences.prefs_context()
        
        try:
            prefs.update(all_prefs) # Opens prefs db only once.
        except:
            print_compact_traceback("bug in _update_prefs: ")

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
    
    ########## Slot methods for "Atoms" page widgets ################

    def usual_change_color(self, prefs_key, caption = "choose"): #bruce 050805
        from prefs_widgets import colorpref_edit_dialog
        colorpref_edit_dialog( self, prefs_key, caption = caption)
    
    def change_atom_hilite_color(self):
        '''Change the atom highlight color.'''
        self.usual_change_color( atomHighlightColor_prefs_key)        
            
    def change_free_valence_color(self):
        '''Change the free valence color.'''
        ## self.usual_change_color( freeValenceColor_prefs_key) #[problematic]
        print '''Change the free valence color -- not yet implemented.''' ###@@@
        # fyi, i recommended implementing this preference in Element Colors Dialog, rather than here. [bruce 050808]

    def change_hotspot_color(self): #bruce 050808 implement new slot which Mark recently added to .ui file
        '''Change the free valence hotspot color.'''
        #e fyi, we might rename hotspot to something like "bonding point" someday...
        self.usual_change_color( atomHotspotColor_prefs_key)
    
    def reset_atom_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
            atomHighlightColor_prefs_key,
            ## freeValenceColor_prefs_key, #[problematic]
            atomHotspotColor_prefs_key,
        ])
            
    def set_default_display_mode(self, val):
        '''Set default display mode of GLpane.
        '''
        self.default_display_mode = val
        self.glpane.setDisplay(val, True)
        self.glpane.gl_update()
        
    ########## End of slot methods for "Atoms" page widgets ###########
    
    ########## Slot methods for "Bonds" page widgets ################
    
    def change_bond_hilite_color(self):
        '''Change the bond highlight color.'''
        self.usual_change_color( bondHighlightColor_prefs_key)        
    
    def change_bond_stretch_color(self):
        '''Change the bond stretch color.'''
        self.usual_change_color( bondStretchColor_prefs_key)        
    
    def change_bond_vane_color(self):
        '''Change the bond vane color for pi orbitals.'''
        self.usual_change_color( bondVaneColor_prefs_key)
    
    def change_bond_cpk_color(self):
        '''Change the bond CPK cylinder color.'''
        self.usual_change_color( bondCPKColor_prefs_key)        
    
    def reset_bond_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
            bondHighlightColor_prefs_key,
            bondStretchColor_prefs_key,
            bondVaneColor_prefs_key,
            bondCPKColor_prefs_key,
        ])
        
    def change_high_order_bond_display(self, val): #bruce 050806 filled this in
        "Slot for the button group that sets the high order bond display."
        #  ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
        try:
            symbol = {0:'multicyl', 1:'vane', 2:'ribbon'}[val]
            # note: this decoding must use the same (arbitrary) int->symbol mapping as the button group does.
            # It's just a coincidence that the order is the same as in the prefs-type listed above.
        except:
            print "bug in change_high_order_bond_display: unknown val ignored:", val
        else:
            env.prefs[ pibondStyle_prefs_key ] = symbol
        return
        
    def change_bond_labels(self, val): #bruce 050806 filled this in
        "Slot for the checkbox that turns Pi Bond Letters on/off."
        # (BTW, these are not "labels" -- someday we might add user-settable longer bond labels,
        #  and the term "labels" should refer to that. These are just letters indicating the bond type. [bruce 050806])
        env.prefs[ pibondLetters_prefs_key ] = not not val
        # See also the other use of pibondLetters_prefs_key, where the checkbox is kept current when first shown.
        return
        
    def change_show_valence_errors(self, val): #bruce 050806 made this up
        "Slot for the checkbox that turns Show Valence Errors on/off."
        env.prefs[ showValenceErrors_prefs_key ] = not not val
##        if platform.atom_debug:
##            print showValenceErrors_prefs_key, env.prefs[ showValenceErrors_prefs_key ] #k prints true, from our initial setup of page
        return
    
    ########## End of slot methods for "Bonds" page widgets ###########
    
    ########## Slot methods for "Background" page widgets ################

    def mode_changed(self, val):
        '''Slot called when the user changes the mode in the drop box.
        '''
        self.bg_mode = self.glpane._find_mode(modes[val])
        
        # Update the background page.
        if self.bg_mode.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()
    
    def fill_type_changed(self, ftype):
        '''Slot called when the user changes the Fill Type.
        '''
        if ftype == 'Solid':
            self.bg_solid_setup()
        else: # 'Blue Sky'
            self.bg_gradient_setup()
        
        # Update the GLPane if the selected mode is the current mode.
        if self.bg_mode == self.glpane.mode:
            self.glpane.gl_update()
        
    def bg_solid_setup(self):
        '''Setup the BG color page for a solid fill type.
        '''
        #self.bg1_color_lbl.show()
        #self.bg1_color_frame.show()
        #self.choose_bg1_color_btn.show()
        
        self.bg1_color_lbl.setEnabled(True)
        self.bg1_color_frame.setEnabled(True)
        self.choose_bg1_color_btn.setEnabled(True)
        
        self.fill_type_combox.setCurrentItem(0) # Solid
        
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        self.bg1_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(self.bg_mode.backgroundColor))
        
        self.bg_mode.set_backgroundGradient(False) # This also stores the pref in the db.
    
    def bg_gradient_setup(self):
        '''Setup the Background page for a gradient fill type.
        '''
        #self.bg1_color_lbl.hide()
        #self.bg1_color_frame.hide()
        #self.choose_bg1_color_btn.hide()
        
        self.bg1_color_lbl.setEnabled(False)
        self.bg1_color_frame.setEnabled(False)
        self.choose_bg1_color_btn.setEnabled(False)
        
        self.fill_type_combox.setCurrentItem(1) # Gradient
        
        self.bg_mode.set_backgroundGradient(True) # This also stores the pref in the db.

    def change_bg1_color(self):
        '''Change a mode's primary background color.
        '''
        # Allow user to select a new background color and set it.
        c = QColorDialog.getColor(self.bg1_color_frame.paletteBackgroundColor(), self, "choose")
        if c.isValid():
            bgcolor = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
            self.bg_mode.set_backgroundColor( bgcolor )
            self.bg1_color_frame.setPaletteBackgroundColor(c)
                
    def restore_default_bgcolor(self):
        '''Slot for "Restore Default Color" button, which restores the selected mode's bg color.
        '''
        # Set the background color to the default.
        self.bg_mode.set_backgroundColor(self.bg_mode.__class__.backgroundColor)
        # Now update the UI.
        self.bg_solid_setup()
        # If the selected mode is the current mode, update the glpane to display the new (default) bg color.
        if self.bg_mode == self.glpane.mode:
            self.glpane.gl_update()
        
    ########## End of slot methods for "Background" page widgets ###########

    ########## Slot methods for "Caption" page widgets ################
        
    def set_caption_fullpath(self, val):
        self.win.caption_fullpath = val
        self.win.update_mainwindow_caption(self.win.assy.has_changed())
        
    ########## End of slot methods for "Caption" page widgets ###########
    
    ########## Slot methods for "History" page widgets ################
    
    def set_history_height(self, height):
        print 'set_history_height: height =', height
        # HistoryWidget needs a new method to properly set the height of the widget given 'height'.
        # Needs research - not obvious how to do this.  Mark 050729.
        # self.history.set_height(height)

    ########## Slot methods for top level widgets ################
    
    def setup_current_page(self, pagename):
        if pagename == 'General':
            self._setup_general_page()
        elif pagename == 'Atoms':
            self._setup_atoms_page()
        elif pagename == 'Bonds':
            self._setup_bonds_page()
        elif pagename == 'Background':
            self._setup_background_page()
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
        # when the user hits the dialog's "Close" button in the dialog's window border (upper right X).
        # Since I've not implemented 'Cancel', it is safer to go ahead and
        # save all preferences anyway.  Otherwise, any changed preferences
        # will not be persistent (after this session).  
        # This will need to be removed when we implement a true cancel function.
        # Mark 050629.
        self._update_prefs()
        QDialog.reject(self)