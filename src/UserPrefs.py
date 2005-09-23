# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
UserPrefs.py

$Id$

History:

Created by Mark.

Modified somewhat by Bruce 050805 for bond color prefs,
and 050810 to fix bugs 785 (partly in MWsemantics.py) and 881 for Alpha6.
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
from prefs_widgets import connect_colorpref_to_colorframe, connect_checkbox_with_boolean_pref
import platform

# This list of mode names correspond to the names listed in the modes combo box.
modes = ['SELECTMOLS', 'SELECTATOMS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']

# List of Default Modes and Startup Modes.  Mark 050921.
default_modes = ['SELECTMOLS', 'SELECTATOMS', 'MODIFY', 'DEPOSIT']
startup_modes = ['$DEFAULT_MODE', 'DEPOSIT']

def get_filename_and_save_in_prefs(parent, prefs_key, caption=''):
    '''Present user with the Qt file chooser to select a file.
    prefs_key is the key to save the filename in the prefs db
    caption is the string for the dialog caption.
    '''
    from platform import get_rootdir
    
    filename = str(QFileDialog.getOpenFileName(
                    get_rootdir(), # Def
                    None,
                    parent,
                    None,
                    caption ))
                
    if not filename: # Cancelled.
        return None
    
    # Save filename in prefs db.    
    prefs = preferences.prefs_context()
    prefs[prefs_key] = str(filename)
        
    return filename
    
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
        self.glpane = assy.o
        self.w = assy.w
        self.assy = assy
        #bruce 050811 added these:
        self._setup_caption_page() # make sure the LineEdits are initialized before we hear their signals
        self._setup_caption_signals()
        
        # This is where What's This descriptions should go for UserPrefs.
        # Mark 050831.
        from whatsthis import create_whats_this_descriptions_for_UserPrefs_dialog
        create_whats_this_descriptions_for_UserPrefs_dialog(self)
    
        return

    def _setup_caption_signals(self):
        # caption_prefix signals
        self.connect( self.caption_prefix_linedit, SIGNAL("textChanged ( const QString & ) "), \
                      self.caption_prefix_linedit_textChanged )
        self.connect( self.caption_prefix_linedit, SIGNAL("returnPressed()"), \
                      self.caption_prefix_linedit_returnPressed )
        # caption_suffix signals
        self.connect( self.caption_suffix_linedit, SIGNAL("textChanged ( const QString & ) "), \
                      self.caption_suffix_linedit_textChanged )
        self.connect( self.caption_suffix_linedit, SIGNAL("returnPressed()"), \
                      self.caption_suffix_linedit_returnPressed )
        return

    # caption_prefix slot methods [#e should probably refile these with other slot methods?]
    def caption_prefix_linedit_textChanged(self, qstring):
        ## print "caption_prefix_linedit_textChanged: %r" % str(qstring) # this works
        self.any_caption_text_changed()
    
    def caption_prefix_linedit_returnPressed(self):
        ## print "caption_prefix_linedit_returnPressed"
            # This works, but the Return press also closes the dialog!
            # (Both for the lineedit whose signal we're catching, and the one whose signal catching is initially nim.)
            # Certainly that makes it a good idea to catch it, though it'd be better to somehow "capture" it
            # so it would not close the dialog.
        self.any_caption_text_changed()        

    # caption_suffix slot methods can be equivalent to the ones for caption_prefix
    caption_suffix_linedit_textChanged = caption_prefix_linedit_textChanged
    caption_suffix_linedit_returnPressed = caption_prefix_linedit_returnPressed
    
    def showDialog(self, pagename='General'):
        '''Display the Preferences dialog with page 'pagename'. '''
        
        # Added to fix bug 894.  Mark.
        # [circa 050817, adds bruce; what's new is the pagename argument]
        if pagename == 'General': # Default
            self.prefs_tab.setCurrentPage(0)
        elif pagename == 'Atoms':
            self.prefs_tab.setCurrentPage(1)
        elif pagename == 'Bonds':
            self.prefs_tab.setCurrentPage(2)
        elif pagename == 'Modes':
            self.prefs_tab.setCurrentPage(3)
        elif pagename == 'Plug-ins':
            self.prefs_tab.setCurrentPage(4)
        elif pagename == 'History':
            self.prefs_tab.setCurrentPage(5)
        elif pagename == 'Caption':
            self.prefs_tab.setCurrentPage(6)
        else:
            print 'Error: Preferences page unknown: ', pagename

        self.exec_loop()
        # bruce comment 050811: using exec_loop rather than show forces this dialog to be modal.
        # For now, it's probably still only correct if it's modal, so I won't change this for A6.
        return

    ###### Private methods ###############################
        
    def _setup_general_page(self):
        ''' Setup widgets to initial (default or defined) values on the General page.
        '''
        self.display_compass_checkbox.setChecked(self.glpane.displayCompass)
        self.compass_position_btngrp.setButton(self.glpane.compassPosition)
        self.display_origin_axis_checkbox.setChecked(self.glpane.displayOriginAxis)
        self.display_pov_axis_checkbox.setChecked(self.glpane.displayPOVAxis)
        
        self.default_projection_btngrp.setButton(env.prefs.get(defaultProjection_prefs_key, 0))


    def _setup_plugins_page(self):
        ''' Setup widgets to initial (default or defined) values on the Plug-ins page.
        '''
        
        # GAMESS label.
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")

        # GAMESS executable path.
        self.gamess_checkbox.setChecked(env.prefs[gamess_enabled_prefs_key])
        self.gamess_path_linedit.setText(env.prefs[gmspath_prefs_key])
        
        # Nano-Hive executable path.
        self.nanohive_checkbox.setChecked(env.prefs[nanohive_enabled_prefs_key])
        self.nanohive_path_linedit.setText(env.prefs[nanohive_path_prefs_key])

# Changed "Background" page to "Modes" page.  Mark 050911.
    def _setup_modes_page(self):
        ''' Setup widgets to initial (default or defined) values on the Modes page.
        '''
        # Set the mode drop box to the current mode, 
        # or "Select Chunks" if the mode is not in the "modes" list.
        if self.glpane.mode.modename in modes:
            self.mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        else:
            self.mode_combox.setCurrentItem(0) # Set to Select Chunks

        self.bg_mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
        
        # Update the "Default Mode" and "Startup Mode" combo boxes.
        self.default_mode_combox.setCurrentItem(default_modes.index(env.prefs[ defaultMode_prefs_key ]))
        
        # Fix for bug 1008. Mark 050923.
        if env.prefs[ startupMode_prefs_key ] not in startup_modes: 
            env.prefs[ startupMode_prefs_key ] = startup_modes[0] # = Default Mode

        self.startup_mode_combox.setCurrentItem(startup_modes.index(env.prefs[ startupMode_prefs_key ]))
        
        if self.bg_mode.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()

    def _setup_atoms_page(self):
        ''' Setup widgets to initial (default or defined) values on the atoms page.
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
        self.default_display_btngrp.setButton( env.prefs[defaultDisplayMode_prefs_key] ) #bruce 050810 revised this
            # bruce comments:
            # - it's wrong to use any other data source here than the prefs db, e.g. via env.prefs. Fixed, 050810.
            # - the codes for the buttons are (by experiment) 2,4,5,3 from top to bottom. Apparently these
            #   match our internal display mode codes, and are set by buttongroup.insert in the pyuic output file,
            #   but for some reason the buttons are inserted in a different order than they're shown.
            # - this is only sufficient because nothing outside this dialog can change env.prefs[defaultDisplayMode_prefs_key]
            #   while the dialog is shown.

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
        
        # Set Lines Dislplay Mode line thickness.  Mark 050831.
        self.bond_line_thickness_spinbox.setValue( env.prefs[linesDisplayModeThickness_prefs_key] )
        
        return
        
    def _setup_history_page(self):
        ''' Setup widgets to initial (default or defined) values on the history page.
        '''
        # History height widgets will be hidden for A6, to be reinstituted at a later time (A7 or A8) for
        # Bruce to decide.  He will be implementing this feature.  Mark 050731.
        self.history_height_lbl.hide()
        self.history_height_spinbox.hide()
        self.history_lines_lbl.hide()
        
        ## self.history_height_spinbox.setValue(self.history.history_height) #bruce 050810 removed this
        
        #bruce 050810 revised the following; nothing else about those checkboxes or prefs_keys is needed.
##        self.msg_serial_number_checkbox.setChecked(env.prefs[historyMsgSerialNumber_prefs_key])
##        self.msg_timestamp_checkbox.setChecked(env.prefs[historyMsgTimestamp_prefs_key])
        connect_checkbox_with_boolean_pref( self.msg_serial_number_checkbox, historyMsgSerialNumber_prefs_key )
        connect_checkbox_with_boolean_pref( self.msg_timestamp_checkbox, historyMsgTimestamp_prefs_key )
        return

    def _setup_caption_page(self): #bruce 050810 revised this, and also call it from __init__ to be safe
        ''' Setup widgets to initial (default or defined) values on the captions page.
        '''
        self.caption_prefix_linedit.setText(env.prefs[captionPrefix_prefs_key])
        self.caption_suffix_linedit.setText(env.prefs[captionSuffix_prefs_key])
            ##e someday we should make a 2-way connector function for LineEdits too
        connect_checkbox_with_boolean_pref( self.caption_fullpath_checkbox, captionFullPath_prefs_key )
        return

    #e this is really a slot method -- should refile it
    def any_caption_text_changed(self):
        # Update Caption prefs
        # The prefix and suffix updates should be done via slots [bruce 050811 doing that now] and include a validator.
        # Will do later.  Mark 050716.

        # (in theory, only one of these has changed, and even though we resave prefs for both,
        #  only the changed one will trigger any formulas watching the prefs value for changes. [bruce 050811])        
        prefix = QString(self.caption_prefix_linedit.text())
        text = prefix.stripWhiteSpace() # make sure prefix is not just whitespaces
        if text: 
            env.prefs[captionPrefix_prefs_key] = str(text) + ' '
        else:
            env.prefs[captionPrefix_prefs_key] = ''
        
        suffix = QString(self.caption_suffix_linedit.text())
        text = suffix.stripWhiteSpace() # make sure suffix is not just whitespaces
        if text: 
            env.prefs[captionSuffix_prefs_key] = ' ' + str(text)
        else:
            env.prefs[captionSuffix_prefs_key] = ''
        return

    ###### End of private methods. ########################
    
    ########## Slot methods for "General" page widgets ################   

    def display_compass(self, val):
        '''Display or Hide the Compass
        '''
        # set the pref
        env.prefs[displayCompass_prefs_key] = val
        # update the glpane
        self.glpane.displayCompass = val
        self.glpane.gl_update()
        
    def display_origin_axis(self, val):
        '''Display or Hide Origin Axis
        '''
        # set the pref
        env.prefs[displayOriginAxis_prefs_key] = val
        # update the glpane
        self.glpane.displayOriginAxis = val
        self.glpane.gl_update()
        
    def display_pov_axis(self, val):
        '''Display or Hide Point of View Axis
        '''
        # set the pref
        env.prefs[displayPOVAxis_prefs_key] = val
        # update the glpane
        self.glpane.displayPOVAxis = val
        self.glpane.gl_update()

    def set_compass_position(self, val):
        '''Set position of compass
        '''
        # set the pref
        env.prefs[compassPosition_prefs_key] = val
        # update the glpane
        self.glpane.compassPosition = val
        self.glpane.gl_update()

    def set_default_projection(self, projection):
        "Set projection, where 0 = Perspective and 1 = Orthographic"
        # set the pref
        env.prefs[defaultProjection_prefs_key] = projection
        self.glpane.setViewProjection(projection)
        
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
            
    def set_default_display_mode(self, val): #bruce 050810 revised this to set the pref immediately
        '''Set default display mode of GLpane.
        '''
        # set the pref
        env.prefs[defaultDisplayMode_prefs_key] = val
        # change the current display mode too
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
        
    def change_bond_line_thickness(self, pixel_thickness): #mark 050831
        '''Set the default bond line thickness for Lines display.  
        pixel_thickness can be 1, 2 or 3.
        '''
        env.prefs[linesDisplayModeThickness_prefs_key] = pixel_thickness
    
    ########## End of slot methods for "Bonds" page widgets ###########
    
    ########## Slot methods for "Modes" page widgets ################

    def mode_changed(self, val):
        '''Slot called when the user changes the mode in the mode-bgcolor drop box.
        '''
        self.bg_mode = self.glpane._find_mode(modes[val])
        
        # Update the modes page.
        if self.bg_mode.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()

    def change_startup_mode(self, option):
        "Slot for the combobox that sets the Startup Mode."
        env.prefs[ startupMode_prefs_key ] = startup_modes[self.startup_mode_combox.currentItem()]
        return
        
    def change_default_mode(self, val):
        "Slot for the combobox that sets the Default Mode."
        env.prefs[ defaultMode_prefs_key ] = default_modes[self.default_mode_combox.currentItem()]
        self.glpane.mode.UpdateDashboard() # Update Done button on dashboard.
        return
            
    def fill_type_changed(self, ftype):
        '''Slot called when the user changes the Fill Type.
        '''
        if ftype == 'Solid':
            self.bg_solid_setup()
        else: # 'Blue Sky'
            self.bg_gradient_setup()
        
        # Update the GLPane if the selected mode is the current mode.
        # [bruce comment 050911: this and related code needs review when dialog becomes non-modal,
        #  since mode objects might be replaced with new instances,
        #  so it ought to store modenames, not mode objects, in self. ###@@@]
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
        '''Setup the Modes page for the background gradient fill type.
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
        
    ########## End of slot methods for "Modes" page widgets ###########
    
    ########## Slot methods for "Plug-ins" page widgets ################

    def set_gamess_path(self):
        '''Slot for GAMESS path "Choose" button.
        '''
        gamess_exe = get_filename_and_save_in_prefs(self, gmspath_prefs_key, 'Choose GAMESS Executable')
         
        if gamess_exe:
            self.gamess_path_linedit.setText(gamess_exe)
            
    def enable_gamess(self, enable=True):
        '''GAMESS is enabled when enable=True.
        GAMESS is disabled when enable=False.
        '''
        if enable:
            self.gamess_path_linedit.setEnabled(1)
            self.gamess_choose_btn.setEnabled(1)
            self.w.jigsGamessAction.setVisible(1)
            env.prefs[gamess_enabled_prefs_key] = True
            
        else:
            self.gamess_path_linedit.setEnabled(0)
            self.gamess_choose_btn.setEnabled(0)
            self.w.jigsGamessAction.setVisible(0)
            self.gamess_path_linedit.setText("")
            env.prefs[gmspath_prefs_key] = ''
            env.prefs[gamess_enabled_prefs_key] = False

    def set_nanohive_path(self):
        '''Slot for Nano-Hive path "Choose" button.
        '''
        nanohive_exe = get_filename_and_save_in_prefs(self, nanohive_path_prefs_key, 'Choose Nano-Hive Executable')
         
        if nanohive_exe:
            self.nanohive_path_linedit.setText(nanohive_exe)
            self.enable_nanohive(1)
            
    def enable_nanohive(self, enable=True):
        '''Nano-Hive is enabled when enable=True.
        Nano-Hive is disabled when enable=False.
        '''
        if enable:
            self.nanohive_path_linedit.setEnabled(1)
            self.nanohive_choose_btn.setEnabled(1)
            self.w.simNanoHiveAction.setVisible(1)
            # Create the Nano-Hive dialog widget.
            # Mark 050914.
            from NanoHive import NanoHive
            self.w.nanohive = NanoHive(self.assy)
        
            self.w.simNanoHiveAction.setVisible(1)
            env.prefs[nanohive_enabled_prefs_key] = True
            
        else:
            self.nanohive_path_linedit.setEnabled(0)
            self.nanohive_choose_btn.setEnabled(0)
            self.w.nanohive = None
            self.w.simNanoHiveAction.setVisible(0)
            self.nanohive_path_linedit.setText("")
            env.prefs[nanohive_path_prefs_key] = ''
            env.prefs[nanohive_enabled_prefs_key] = False
            
                            
    ########## End of slot methods for "Plug-ins" page widgets ###########

    ########## Slot methods for "Caption" page widgets ################

    #e there are some new slot methods for this in other places, which should be refiled here. [bruce 050811]
    
    def set_caption_fullpath(self, val): #bruce 050810 revised this
        # there is now a separate connection which sets the pref, so this is not needed:
        ## self.win.caption_fullpath = val
        # and there is now a Formula in MWsemantics which makes the following no longer needed:
        ## self.win.update_mainwindow_caption(self.win.assy.has_changed())
        pass
        
    ########## End of slot methods for "Caption" page widgets ###########
    
    ########## Slot methods for "History" page widgets ################
    
    def set_history_height(self, height):
        print 'set_history_height: height =', height
        # HistoryWidget needs a new method to properly set the height of the widget given 'height'.
        # Needs research - not obvious how to do this.  Mark 050729.
        # self.history.set_height(height)

    ########## Slot methods for top level widgets ################
    
    def setup_current_page(self, pagename):        
        #bruce 050817 fix new A6 bug introduced by Mark's fix of bug 894
        # (which was: lack of showing general page could reset gamess path to ""):
        # always call self._setup_general_page regardless of argument,
        # as well as the page named in the argument.
        if pagename != 'General':
            self._setup_general_page()
        # end of bruce 050817 fix
        
        if pagename == 'General':
            self._setup_general_page()
        elif pagename == 'Atoms':
            self._setup_atoms_page()
        elif pagename == 'Bonds':
            self._setup_bonds_page()
        elif pagename == 'Modes':
            self._setup_modes_page()
        elif pagename == 'Plug-ins':
            self._setup_plugins_page()
        elif pagename == 'History':
            self._setup_history_page()
        elif pagename == 'Caption':
            self._setup_caption_page()
        else:
            print 'Error: Preferences page unknown: ', pagename
            
    def accept(self):
        '''The slot method for the 'OK' button.'''
        # self._update_prefs() # Mark 050919
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
        # self._update_prefs() # Removed by Mark 050919.
        QDialog.reject(self)

    pass # end of class UserPrefs

# end