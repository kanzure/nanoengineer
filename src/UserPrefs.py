# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
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
from widgets import double_fixup
from prefs_widgets import connect_colorpref_to_colorframe, connect_checkbox_with_boolean_pref
import platform
from povray import get_default_plugin_path

debug_sliders = False # Do not commit as True

def debug_povdir_signals():
    return 0 and env.debug()

# This list of mode names correspond to the names listed in the modes combo box.
modes = ['SELECTMOLS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']

# List of Default Modes and Startup Modes.  Mark 050921.
# [bruce 060403 guesses these need to correspond to certain combobox indices.]
default_modes = ['SELECTMOLS', 'MODIFY', 'DEPOSIT']
startup_modes = ['$DEFAULT_MODE', 'DEPOSIT']

def fix_modename_pref( modename, modename_list, modename_fallback = None): #bruce 060403
    """modename came from prefs db; if it's in modename_list, return it unchanged,
    but if not, return one of the modenames in modename_list to be used in place of it, or modename_fallback.
    This is REQUIRED for decoding any modename-valued prefs value.
    """
    assert len(modename_list) > 0 or modename_fallback
    if modename in modename_list:
        return modename
    # handle SELECTATOMS being superseded by DEPOSIT
    if modename == 'SELECTATOMS' and 'DEPOSIT' in modename_list:
        return 'DEPOSIT'
    # handle future modes not yet supported by current code
    # (at this point it might be better to return the user's default mode;
    #  callers wanting this can pass it as modename_fallback)
    return modename_fallback or modename_list[-1]
        # could use any arbitrary element rather than the last one (at -1),
        # but in the list constants above, the last choices seem to be best

def default_modename(): #bruce 060403
    """Return the modename string of the user's default mode.
    External code should use this, rather than directly using env.prefs[ defaultMode_prefs_key ].
    """
    return fix_modename_pref( env.prefs[ defaultMode_prefs_key ], default_modes)

def startup_modename(): #bruce 060403
    """Return the modename string (literal or symbolic, e.g. '$DEFAULT_MODE') of the user's startup mode.
    External code should use this, rather than directly using env.prefs[ startupMode_prefs_key ].
    """
    return fix_modename_pref( env.prefs[ startupMode_prefs_key ], startup_modes, startup_modes[0] )

def parentless_open_dialog_pref(): #bruce 060710 for Mac A8
    # see if setting this True fixes the Mac-specific bugs in draggability of this dialog, and CPU usage while it's up
    from debug_prefs import debug_pref, Choice_boolean_False
    return debug_pref("parentless open file dialogs?", Choice_boolean_False,
                      prefs_key = "A8.1 devel/parentless open file dialogs")

parentless_open_dialog_pref()

def get_filename_and_save_in_prefs(parent, prefs_key, caption=''):
    '''Present user with the Qt file chooser to select a file.
    prefs_key is the key to save the filename in the prefs db
    caption is the string for the dialog caption.
    '''
    # see also get_dirname_and_save_in_prefs, which has similar code
    from platform import get_rootdir
    
    if parentless_open_dialog_pref():
        parent = None
    
    filename = str(QFileDialog.getOpenFileName(
                    get_rootdir(), # '/' on Mac or Linux, something else on Windows
                    None, # filter (kinds of files to permit choosing)
                    parent,
                    None, # name
                    caption ))
                
    if not filename: # Cancelled.
        return None
    
    # Save filename in prefs db.    
    prefs = preferences.prefs_context()
    prefs[prefs_key] = str(os.path.normpath(filename))
        
    return filename

def get_dirname_and_save_in_prefs(parent, prefs_key, caption=''): #bruce 060710 for Mac A8
    '''Present user with the Qt file chooser to select an existing directory.
    If they do that, and if prefs_key is not null, save its full pathname in env.prefs[prefs_key].
    <caption> is the string for the dialog caption.
    '''
    # see also get_filename_and_save_in_prefs, which has similar code
    from platform import get_rootdir
    
    if parentless_open_dialog_pref():
        parent = None
    
    filename = str(QFileDialog.getExistingDirectory(
                    get_rootdir(), # '/' on Mac or Linux -- maybe not the best choice if they've chosen one before?
                    parent, ### if this was None, it might fix the Mac bug where you can't drag the dialog around [bruce 060710]
                    None, # name
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
        
def get_pref_or_optval(key, val, optval):
    """Return <key>'s value. If <val> is equal to <key>'s value, return <optval> instead.
    """
    if env.prefs[key] == val:
        return optval
    else:
        return env.prefs[key]

class UserPrefs(UserPrefsDialog):
    '''The User Preferences dialog used for accessing and changing user preferences
    '''
       
    def __init__(self, assy):
        UserPrefsDialog.__init__(self)
        self.glpane = assy.o
        self.w = assy.w
        self.assy = assy
        
        #mark 060627
        # Validator for the linedit widgets. [WARNING: bruce 060705 copied this into MinimizeEnergyProp.py]
        self.endrms_validator = QDoubleValidator(self)
        self.endrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0.0 to 100, 2 decimal places
        self.endrms_linedit.setValidator(self.endrms_validator)
        
        self.endmax_validator = QDoubleValidator(self)
        self.endmax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.endmax_linedit.setValidator(self.endmax_validator)
        
        self.cutoverrms_validator = QDoubleValidator(self)
        self.cutoverrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutoverrms_linedit.setValidator(self.cutoverrms_validator)
        
        self.cutovermax_validator = QDoubleValidator(self)
        self.cutovermax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutovermax_linedit.setValidator(self.cutovermax_validator)
        
        #bruce 050811 added these:
        self._setup_window_page() # make sure the LineEdits are initialized before we hear their signals
        self._setup_caption_signals()
        self._setup_plugin_signals() #bruce 060710
        
        # This is where What's This descriptions should go for UserPrefs.
        # Mark 050831.
        from whatsthis import create_whats_this_descriptions_for_UserPrefs_dialog
        create_whats_this_descriptions_for_UserPrefs_dialog(self)

        QWhatsThis.add(self.display_origin_axis_checkbox, """<p><b>Display Origin Axis</b></p>Shows/Hides the Origin Axis""")
        QWhatsThis.add(self.display_pov_axis_checkbox, """<p><b>Display Point of View Axis</b></p>Shows/Hides the Point
        of View Axis""")
        QWhatsThis.add(self.display_compass_checkbox, """<p><b>Display Compass</b></p>Shows/Hides the Display Compass""")
        QWhatsThis.add(self.display_compass_labels_checkbox, """<p><b>Display Compass</b></p>Shows/Hides the Display Compass""")
        QWhatsThis.add(self.watch_min_in_realtime_checkbox, """<p><b>Watch motion in real time</b></p>Enables/disables real
        time graphical updates during adjust operations when using <b>Adjust All</b> or <b>Adjust Selection</b>""")
        QWhatsThis.add(self.update_number_spinbox, """<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        QWhatsThis.add(self.update_units_combobox, """<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        QWhatsThis.add(self.update_every_rbtn, """<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        QWhatsThis.add(self.update_asap_rbtn, """<b>Update as fast as possible</b>
        <p>
        Update every 2 seconds,
        or faster (up to 20x/sec) if it doesn't slow adjustments by more than 20%</p>""")
        QWhatsThis.add(self.endrms_lbl, """<b>EndRMS</b>
        <p>Continue until this RMS force is reached.</p>""")
        QWhatsThis.add(self.endmax_lbl, """<b>EndMax</b>
        <p>Continue until no interaction exceeds this force.</p>""")
        QWhatsThis.add(self.endmax_linedit, """<b>EndMax</b>
        <p>Continue until no interaction exceeds this force.</p>""")
        QWhatsThis.add(self.endrms_linedit, """<b>EndRMS</b>
        <p>Continue until this RMS force is reached.</p>""")
        QWhatsThis.add(self.cutovermax_lbl, """<b>CutoverMax</b>
        <p>Use steepest descent until no interaction
        exceeds this force.</p>""")
        QWhatsThis.add(self.cutovermax_linedit, """<b>CutoverMax</b>
        <p>Use steepest descent until no interaction
        exceeds this force.</p>""")
        QWhatsThis.add(self.cutoverrms_linedit, """<b>CutoverRMS</b>
        <p>Use steepest descent until this RMS force
        is reached.</p>""")
        QWhatsThis.add(self.cutoverrms_lbl, """<b>CutoverRMS</b>
        <p>Use steepest descent until this RMS force
        is reached.</p>""")
        QWhatsThis.add(self.groupBox14, """<b>Settings for Adjust</b>
        <p>This group of settings affect the
        behavior of <b>Adjust All</b> and <b>Adjust Selection</b>.</p>""")
        QWhatsThis.add(self.animate_views_checkbox, """<p><b>Animate Between Views</b></p>Enables/disables animation
        when switching between the current view and a new view.""")
        QWhatsThis.add(self.animation_speed_slider, """<p><b>View Animation Speed</b></p>Sets the animation speed when
        animating between view (i.e. Front View to Right View).  It is recommended that this be set to Fast when working on large
        models.""")
        QWhatsThis.add(self.textLabel1_7, """<p><b>Level of Detail</b></p>Sets the <b>Level of Detail</b>
        for atoms and bonds.<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics
        quality<br> <b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between
        High, Medium and Low based on the model size (number of atoms).""")
        QWhatsThis.add(self.level_of_detail_combox, """<p><b>Level of Detail</b></p>Sets the graphics quality for atoms
        (and bonds)<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics quality<br>
        <b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between High, Medium
        and Low based on the number of atoms in the current part.""")
        QWhatsThis.add(self.textLabel1_3_2, """<p><b>Ball and Stick Atom Scale</b></p>Sets the Ball and Stick
        Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
        QWhatsThis.add(self.cpk_atom_rad_spinbox, """<p><b>Ball and Stick Atom Scale</b></p>Sets the Ball and Stick
        Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
        QWhatsThis.add(self.textLabel1_3_2_2, """<p><b>CPK Atom Scale</b></p>Changes the CPK Atom Scale factor.
        It is best to change the scale factor while in CPK display mode so you can see the graphical effect of changing the scale.""")
        QWhatsThis.add(self.cpk_scale_factor_linedit, """Displays the value of the CPK Atom Scale""")
        QWhatsThis.add(self.cpk_scale_factor_slider, """<p><b>CPK Atom Scale</b></p>Slider control for chaning the CPK
        Atom Scale factor. It is best to change the scale factor while in CPK display mode so you can see the graphical effect of
        changing the scale.""")
        QWhatsThis.add(self.reset_cpk_scale_factor_btn, """Restore the default value of the CPK Scale Factor""")
        QWhatsThis.add(self.radioButton11, """<p><b>Multiple Cylinders</b></p>
        <p><b>High Order Bonds</b> are
        displayed using <b>Multiple Cylinders.</b></p>
        <b>Double bonds</b> are drawn with two cylinders.<br>
        <b>Triple bonds</b>
        are drawn with three cylinders.<br>
        <b>Aromatic bonds</b> are drawn as a single cylinder with a short green cylinder in the
        middle.""")
        QWhatsThis.add(self.radioButton11_2, """<p><b>Vanes</b></p>
        <p><i>High Order Bonds</i> are displayed
        using <b>Vanes.</b></p>
        <p>Vanes represent <i>pi systems</i> in high order bonds and are rendered as rectangular polygons.
        The orientation of the vanes approximates the orientation of the pi system(s).</p>
        <p>Create an acetylene or ethene molecule
        and select this option to see how vanes are rendered.</p>""")
        QWhatsThis.add(self.radioButton11_2_2, """<p><b>Ribbons</b></p>
        <p><i>High Order Bonds</i> are displayed
        using <b>Ribbons.</b></p>
        <p>Ribbons represent <i>pi systems</i> in high order bonds and are rendered as ribbons. The orientation
        of the ribbons approximates the orientation of the pi system.</p>
        <p>Create an acetylene or ethene molecule and select this
        option to see how ribbons are rendered.</p>""")
        QWhatsThis.add(self.show_bond_labels_checkbox, """<p><b>Show Bond Type Letters</b></p>
        <p>Shows/Hides Bond Type
        letters (labels) on top of bonds.</p>
        <u>Bond Type Letters:</u><br>
        <b>2</b> = Double bond<br>
        <b>3</b> = Triple bond<br>
        <b>A</b>
        = Aromatic bond<br>
        <b>G</b> = Graphitic bond<br>""")
        QWhatsThis.add(self.show_valence_errors_checkbox, """<p><b>Show Valence Errors</b></p><p>Enables/Disables Valence
        Error Checker.</p>
        When enabled, atoms with valence errors are displayed with an orange wireframe sphere. This indicates
        that one or more of the atom's bonds are not of the correct order (type).""")
        QWhatsThis.add(self.textLabel1_3, """<p><b>Ball and Stick Bond Scale</b></p>Set scale (size) factor
        for the cylinder representing bonds in Ball and Stick display mode""")
        QWhatsThis.add(self.textLabel1, """<p><b>Bond Line Thickness</b></p>Bond thickness (in pixels) for
        Lines Display Mode""")
        QWhatsThis.add(self.cpk_cylinder_rad_spinbox, """<p><b>Ball and Stick Bond Scale</b></p>Set scale (size) factor
        for the cylinder representing bonds in Ball and Stick display mode""")
        QWhatsThis.add(self.bond_line_thickness_spinbox, """<p><b>Bond Line Thickness</b></p>Bond thickness (in pixels) for
        Lines Display Mode""")
        QWhatsThis.add(self.startup_mode_lbl, """<p><b>Startup Mode</b></p>This specifies which mode the program
        will start in.""")
        QWhatsThis.add(self.startup_mode_combox, """<p><b>Startup Mode</b></p>This specifies which mode the program
        will start in.""")
        QWhatsThis.add(self.default_mode_lbl, """<p><b>Default Mode</b></p>This specifies which mode the user
        will be placed in when exiting any other mode.""")
        QWhatsThis.add(self.default_mode_combox, """<p><b>Default Mode</b></p>This specifies which mode the user
        will be placed in when exiting any other mode.""")
        QWhatsThis.add(self.mode_combox, """<p><b>Mode Settings: Mode</b></p>
        This specifies which mode you
        are changing the <b>Display Mod</b>e or <b>Background Color</b> for below.""")
        QWhatsThis.add(self.display_mode_combox, """<p><b>Display Mode</b></p>
        <p>Sets the Display Mode for the current
        mode. If set to <b>Default</b>, then atoms and bonds are displayed in the display mode defined by <b>Default Display Mode</b>.</p>""")
        QWhatsThis.add(self.fill_type_combox, """<p><b>Fill Type</b></p>
        <p>Sets the fill type of the background.
        Each mode can have a different color, if desired.</p>""")
        QWhatsThis.add(self.vwd_rbtn, """<u><b>CPK (Space Filling)</b></u><br>
        <p>Changes the <i>Default
        Display Mode</i>  to <b>CPK</b> mode.
        Atoms are rendered as space filling spheres. Bonds are not rendered.</p>""")
        QWhatsThis.add(self.cpk_rbtn, """<u><b>Ball and Stick</b></u><br>
        <p>Changes the <i>Default Display
        Mode</i>  to <b>Ball and Stick</b> mode.
        Atoms are rendered  as spheres (balls) and bonds are rendered as narrow cylinders
        (sticks).</p>""")
        QWhatsThis.add(self.lines_rbtn, """<u><b>Lines</b></u><br>
        <p>Changes the <i>Default Display Mode</i>
        to <b>Lines</b> mode.
        Bonds are rendered as lines. Atoms are not rendered.</p>""")
        QWhatsThis.add(self.tubes_rbtn, """<u><b>Tubes</b></u><br>
        <p>Changes the <i>Default Display Mode</i>
        to <b>Tubes</b> mode.
        Atoms and bonds are rendered as colored tubes.</p>""")
        QWhatsThis.add(self.autobond_checkbox, """Build mode's default setting for Autobonding at startup (enabled/disabled)""")
        QWhatsThis.add(self.water_checkbox, """Build mode's default setting for Water at startup (enabled/disabled)""")
        QWhatsThis.add(self.buildmode_select_atoms_checkbox, """<p><b>Select Atoms of Deposited Object</b></p>
        When depositing
        atoms, clipboard chunks or library parts, their atoms will automatically be selected.""")
        QWhatsThis.add(self.buildmode_highlighting_checkbox, """Build mode's default setting for Highlighting at startup (enabled/disabled)""")
        QWhatsThis.add(self.povray_checkbox, """This enables POV-Ray as a plug-in. POV-Ray is a free raytracing
        program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray
        plug-in.""")
        QWhatsThis.add(self.povray_lbl, """This enables POV-Ray as a plug-in. POV-Ray is a free raytracing
        program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray
        plug-in.""")
        QWhatsThis.add(self.nanohive_lbl, """This enables Nano-Hive as a plug-in. Nano-Hive is available for
        download from http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive
        plug-in.""")
        QWhatsThis.add(self.nanohive_checkbox, """This enables Nano-Hive as a plug-in. Nano-Hive is available for
        download from http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive
        plug-in.""")
        QWhatsThis.add(self.povray_path_linedit, """The full path to the POV-Ray executable file.""")
        QWhatsThis.add(self.nanohive_path_linedit, """The full path to the Nano-Hive executable file.""")
        QWhatsThis.add(self.gamess_lbl, """<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS)
        as a plug-in. </p>
        <p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
        PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
        <p>For Linux and MacOS users,
        GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer
        before you can enable the GAMESS plug-in.</p>""")
        QWhatsThis.add(self.megapov_path_linedit, """The full path to the MegaPOV executable file (megapov.exe).""")
        QWhatsThis.add(self.megapov_checkbox, """This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing
        program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you
        can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed
        while rendering).""")
        QWhatsThis.add(self.gamess_path_linedit, """The gamess executable file. Usually it's called gamess.??.x or
        ??gamess.exe.""")
        QWhatsThis.add(self.gamess_checkbox, """<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS)
        as a plug-in. </p>
        <p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
        PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
        <p>For Linux and MacOS users,
        GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer
        before you can enable the GAMESS plug-in.</p>""")
        QWhatsThis.add(self.povdir_linedit, """Specify a directory for where to find POV-Ray or MegaPOV include
        files such as transforms.inc.""")
        QWhatsThis.add(self.nanohive_choose_btn, """This opens up a file chooser dialog so that you can specify the
        location of the Nano-Hive executable.""")
        QWhatsThis.add(self.povray_choose_btn, """This opens up a file chooser dialog so that you can specify the
        location of the POV-Ray executable.""")
        QWhatsThis.add(self.megapov_choose_btn, """This opens up a file chooser dialog so that you can specify the
        location of the MegaPOV executable (megapov.exe).""")
        QWhatsThis.add(self.gamess_choose_btn, """This opens up a file chooser dialog so that you can specify the
        location of the GAMESS or PC-GAMESS executable.""")
        QWhatsThis.add(self.megapov_lbl, """This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing
        program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you
        can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed
        while rendering).""")
        QWhatsThis.add(self.povdir_checkbox, """Select a user-customized directory for POV-Ray and MegaPOV include
        files, such as transforms.inc.""")
        QWhatsThis.add(self.undo_automatic_checkpoints_checkbox, """<p><b>Automatic Checkpoints</b></p>Specifies whether <b>Automatic
        Checkpointing</b> is enabled/disabled during program startup only.  It does not enable/disable <b>Automatic Checkpointing</b>
        when the program is running.
        <p><b>Automatic Checkpointing</b> can be enabled/disabled by the user at any time from <b>Edit
        > Automatic Checkpointing</b>. When enabled, the program maintains the Undo stack automatically.  When disabled, the user
        is required to manually set Undo checkpoints using the <b>Set Checkpoint</b> button in the Edit Toolbar/Menu.</p>
        <p><b>Automatic
        Checkpointing</b> can impact program performance. By disabling Automatic Checkpointing, the program will run faster.</p>
        <p><b><i>Remember
        to you must set your own Undo checkpoints manually when Automatic Checkpointing is disabled.</i></b></p>""")
        QWhatsThis.add(self.undo_restore_view_checkbox, """<p><b>Restore View when Undoing Structural Changes</b></p>
        <p>When
        checked, the current view is stored along with each <b><i>structural change</i></b> on the undo stack.  The view is then
        restored when the user undoes a structural change.</p>
        <p><b><i>Structural changes</i></b> include any operation that modifies
        the model. Examples include adding, deleting or moving an atom, chunk or jig. </p>
        <p>Selection (picking/unpicking) and view
        changes are examples of operations that do not modify the model (i.e. are not structural changes).</p>""")
        QWhatsThis.add(self.groupBox3, """Format Prefix and Suffix text the delimits the part name in the
        caption in window border.""")
        QWhatsThis.add(self.save_current_btn, """Saves the main window's current position and size for the next
        time the program starts.""")
        QWhatsThis.add(self.restore_saved_size_btn, """Saves the main window's current position and size for the next
        time the program starts.""")
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
            # [later, bruce 060710 -- probably due to a Qt Designer property on the button, fixable by .setAutoDefault(0) ###@@@]
            # (Both for the lineedit whose signal we're catching, and the one whose signal catching is initially nim.)
            # Certainly that makes it a good idea to catch it, though it'd be better to somehow "capture" it
            # so it would not close the dialog.
        self.any_caption_text_changed()        

    # caption_suffix slot methods can be equivalent to the ones for caption_prefix
    caption_suffix_linedit_textChanged = caption_prefix_linedit_textChanged
    caption_suffix_linedit_returnPressed = caption_prefix_linedit_returnPressed

    def _setup_plugin_signals(self): #bruce 060710
        self.connect( self.povdir_linedit, SIGNAL("textChanged ( const QString & ) "), \
                      self.povdir_linedit_textChanged )
        self.connect( self.povdir_linedit, SIGNAL("returnPressed()"), \
                      self.povdir_linedit_returnPressed )
    
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
        elif pagename == 'Lighting':
            self.prefs_tab.setCurrentPage(4)
        elif pagename == 'Plug-ins':
            self.prefs_tab.setCurrentPage(5)
        elif pagename == 'Undo':
            self.prefs_tab.setCurrentPage(6)
        elif pagename == 'Caption':
            #bruce 051216 comment: I don't know if it's safe to change this string to 'Window' to match tab text
            self.prefs_tab.setCurrentPage(7)
        else:
            print 'Error: Preferences page unknown: ', pagename

        self.mmkit_was_hidden = self.w.hide_MMKit_during_open_or_save_on_MacOS() # Mark 060704
        
        self.exec_loop()
        # bruce comment 050811: using exec_loop rather than show forces this dialog to be modal.
        # For now, it's probably still only correct if it's modal, so I won't change this for A6.
        return

    ###### Private methods ###############################
        
    def _setup_general_page(self):
        ''' Setup widgets to initial (default or defined) values on the General page.
        '''
        connect_checkbox_with_boolean_pref( self.display_compass_checkbox, displayCompass_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_compass_labels_checkbox, displayCompassLabels_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_origin_axis_checkbox, displayOriginAxis_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_pov_axis_checkbox, displayPOVAxis_prefs_key )
        self.compass_position_combox.setCurrentItem(self.glpane.compassPosition)
        self.default_projection_btngrp.setButton(env.prefs[defaultProjection_prefs_key])
        connect_checkbox_with_boolean_pref( self.high_quality_graphics_checkbox, animateHighQualityGraphics_prefs_key )
        connect_checkbox_with_boolean_pref( self.animate_views_checkbox, animateStandardViews_prefs_key )
        connect_checkbox_with_boolean_pref( self.watch_min_in_realtime_checkbox, Adjust_watchRealtimeMinimization_prefs_key )
        
        speed = int (env.prefs[animateMaximumTime_prefs_key] * -100)
        self.animation_speed_slider.setValue(speed)
        
        self.update_btngrp.setEnabled(env.prefs[Adjust_watchRealtimeMinimization_prefs_key])

        # [WARNING: bruce 060705 copied this into MinimizeEnergyProp.py]        
        self.endrms = get_pref_or_optval(Adjust_endRMS_prefs_key, -1.0, '')
        self.endrms_linedit.setText(str(self.endrms))
        
        self.endmax = get_pref_or_optval(Adjust_endMax_prefs_key, -1.0, '')
        self.endmax_linedit.setText(str(self.endmax))
        
        self.cutoverrms = get_pref_or_optval(Adjust_cutoverRMS_prefs_key, -1.0, '')
        self.cutoverrms_linedit.setText(str(self.cutoverrms))
        
        self.cutovermax = get_pref_or_optval(Adjust_cutoverMax_prefs_key, -1.0, '')
        self.cutovermax_linedit.setText(str(self.cutovermax))

    def _setup_plugins_page(self):
        ''' Setup widgets to initial (default or defined) values on the Plug-ins page.
        '''
        
        # GAMESS label.
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")

        # Nano-Hive executable path.
        self.nanohive_checkbox.setChecked(env.prefs[nanohive_enabled_prefs_key])
        self.nanohive_path_linedit.setText(env.prefs[nanohive_path_prefs_key])
        
        # POV-Ray executable path.
        self.povray_checkbox.setChecked(env.prefs[povray_enabled_prefs_key])
        self.povray_path_linedit.setText(env.prefs[povray_path_prefs_key])
        
        # MegaPOV executable path.
        self.megapov_checkbox.setChecked(env.prefs[megapov_enabled_prefs_key])
        self.megapov_path_linedit.setText(env.prefs[megapov_path_prefs_key])
        
        # POV include dir (directory for POV-Ray or MegaPOV include files, or "" to get the default choice)
        # Added by Will & Bruce 060710 for Mac A8 release, not present in Windows A8,
        # since needed to support use of Unix compiles of those programs on the Mac,
        # which is the only way to get a command-line version which NE1 can call. [bruce 060710]
        self.povdir_checkbox.setChecked(env.prefs[povdir_enabled_prefs_key])
        self.povdir_linedit.setText(env.prefs[povdir_path_prefs_key])

        self._update_povdir_enables() #bruce 060710

        # GAMESS executable path.
        self.gamess_checkbox.setChecked(env.prefs[gamess_enabled_prefs_key])
        self.gamess_path_linedit.setText(env.prefs[gmspath_prefs_key])
        
    def _setup_modes_page(self):
        ''' Setup widgets to initial (default or defined) values on the Modes page.
        '''
        # Set the mode drop box to the current mode, 
        # or "Select Chunks" if the mode is not in the "modes" list.
        if self.glpane.mode.modename in modes:
            self.mode_combox.setCurrentItem(modes.index(self.glpane.mode.modename))
        else:
            self.mode_combox.setCurrentItem(0) # Set to Select Chunks

        self.currentItem_mode = self.glpane._find_mode(modes[self.mode_combox.currentItem()])
            # The mode object of the current item selected in the 'Mode' combobox.
        
        self.display_mode_combox.setCurrentItem(self.currentItem_mode.displayMode) 
            # Update the Display Mode combobox.
        
        # Update the "Default Mode" and "Startup Mode" combo boxes.
        self.default_mode_combox.setCurrentItem( default_modes.index( default_modename() )) #bruce 060403 revised this
        
        # Fix for bug 1008. Mark 050924. [use '$DEFAULT_MODE' == startup_modes[0] if smode not in startup_modes]
        # [then bruce 060403 revised this to do same thing in a different way]
        smode = startup_modename()
##        smode = env.prefs[ startupMode_prefs_key ]
##        if smode not in startup_modes:
##            smode = startup_modes[0] # = Default Mode
        
        self.startup_mode_combox.setCurrentItem(startup_modes.index(smode))

        if self.currentItem_mode.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()
            
        # Bug 799 fix.  Mark 050731
        self.default_display_btngrp.setButton( env.prefs[defaultDisplayMode_prefs_key] ) #bruce 050810 revised this
            # bruce comments:
            # - it's wrong to use any other data source here than the prefs db, e.g. via env.prefs. Fixed, 050810.
            # - the codes for the buttons are (by experiment) 2,4,5,3 from top to bottom. Apparently these
            #   match our internal display mode codes, and are set by buttongroup.insert in the pyuic output file,
            #   but for some reason the buttons are inserted in a different order than they're shown.
            # - this is only sufficient because nothing outside this dialog can change env.prefs[defaultDisplayMode_prefs_key]
            #   while the dialog is shown.
        
        # Build Mode Defaults.  mark 060203.
        connect_checkbox_with_boolean_pref( self.autobond_checkbox, buildModeAutobondEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.water_checkbox, buildModeWaterEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_highlighting_checkbox, buildModeHighlightingEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_select_atoms_checkbox, buildModeSelectAtomsOfDepositedObjEnabled_prefs_key )
        

# Let's reorder all these _setup methods in order of appearance soon. Mark 051124.
    def _setup_lighting_page(self, lights=None): #mark 051124
        ''' Setup widgets to initial (default or defined) values on the Lighting page.
        '''
        if not lights:
            self.lights = self.original_lights = self.glpane.getLighting()
        else:
            self.lights = lights
            
        light_num = self.light_combobox.currentItem()
        
        self.update_light_combobox_items()
        
        # Move lc_prefs_keys upstairs.  Mark.
        lc_prefs_keys = [light1Color_prefs_key, light2Color_prefs_key, light3Color_prefs_key]
        self.current_light_key = lc_prefs_keys[light_num] # Get prefs key for current light color.
        connect_colorpref_to_colorframe(self.current_light_key, self.light_color_frame)
        self.light_color = env.prefs[self.current_light_key]
        
        # These sliders generate signals whenever their 'setValue()' slot is called (below).
        # This creates problems (bugs) for us, so we disconnect them temporarily.
        self.disconnect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.disconnect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.disconnect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        
        # self.lights[light_num][0] contains 'color' attribute.  
        # We already have it (self.light_color) from the prefs key (above).
        a = self.lights[light_num][1] # ambient intensity
        d = self.lights[light_num][2] # diffuse intensity
        s = self.lights[light_num][3] # specular intensity
        
        self.light_ambient_slider.setValue(int (a * 100)) # generates signal
        self.light_diffuse_slider.setValue(int (d * 100)) # generates signal
        self.light_specularity_slider.setValue(int (s * 100)) # generates signal
        
        self.light_ambient_linedit.setText(str(a))
        self.light_diffuse_linedit.setText(str(d))
        self.light_specularity_linedit.setText(str(s))
        
        self.light_x_linedit.setText(str (self.lights[light_num][4]))
        self.light_y_linedit.setText(str (self.lights[light_num][5]))
        self.light_z_linedit.setText(str (self.lights[light_num][6]))
        self.light_checkbox.setChecked(self.lights[light_num][7])
        
        # Reconnect the slots to the light sliders.
        self.connect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        
        self._setup_material_group()

# _setup_material_group() should be folded back into _setup_lighting_page(). Mark 051204.
    def _setup_material_group(self, reset=False):
        ''' Setup Material Specularity widgets to initial (default or defined) values on the Lighting page.
        If reset = False, widgets are reset from the prefs db.
        If reset = True, widgets are reset from their previous values.
        '''

        if reset:
            self.material_specularity = self.original_material_specularity
            self.whiteness = self.original_whiteness
            self.shininess = self.original_shininess
            self.brightness = self.original_brightness
        else:
            self.material_specularity = self.original_material_specularity = \
                env.prefs[material_specular_highlights_prefs_key]
            self.whiteness = self.original_whiteness = \
                int(env.prefs[material_specular_finish_prefs_key] * 100)
            self.shininess = self.original_shininess = \
                int(env.prefs[material_specular_shininess_prefs_key])
            self.brightness = self.original_brightness= \
                int(env.prefs[material_specular_brightness_prefs_key] * 100)
            
        # Enable/disable specular highlights.
        self.ms_on_checkbox.setChecked(self.material_specularity )

        # For whiteness, the stored range is 0.0 (Plastic) to 1.0 (Metal).  The Qt slider range
        # is 0 - 100, so we multiply by 100 (above) to set the slider.  Mark. 051129.
        self.ms_finish_slider.setValue(self.whiteness) # generates signal
        self.ms_finish_linedit.setText(str(self.whiteness * .01))
        
        # For shininess, the range is 15 (low) to 60 (high).  Mark. 051129.
        self.ms_shininess_slider.setValue(self.shininess) # generates signal
        self.ms_shininess_linedit.setText(str(self.shininess))
        
        # For brightness, the range is 0.0 (low) to 1.0 (high).  Mark. 051203.
        self.ms_brightness_slider.setValue(self.brightness) # generates signal
        self.ms_brightness_linedit.setText(str(self.brightness * .01))

    def _setup_atoms_page(self):
        ''' Setup widgets to initial (default or defined) values on the atoms page.
        '''
        # Set colors for atom color swatches
##        self.atom_hilite_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(orange))

        #bruce 050805 new way (see comment in _setup_bonds_page):
        connect_colorpref_to_colorframe( atomHighlightColor_prefs_key, self.atom_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHighlightColor_prefs_key, self.bondpoint_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHotspotColor_prefs_key, self.hotspot_color_frame)

        lod = env.prefs[ levelOfDetail_prefs_key ]
        lod = int(lod)
        loditem = lod # index of corresponding spinbox item -- this is only correct for 0,1,2; other cases handled below
        if lod <= -1: # 'variable' (only -1 is used now, but other negative values might be used in future)
            # [bruce 060215 changed prefs value for 'variable' from 3 to -1, in case we have more LOD levels in the future]
            loditem = 3 # index of the spinbox item that says "variable"
        #bruce 060317 fix bug 1551 (in two files) by removing lod == 3 case. It should never be reactivated.
        # This comment and commented-out code can be removed after A7 release.
##        elif lod == 3:
##            # 3 is an illegal value now -- fix it
##            # (this case can be removed after a few days; in A7 3 or higher should be a legal value equivalent to 2)
##            env.prefs[ levelOfDetail_prefs_key ] = -1
##            loditem = 3
##        elif lod > 3: # change this to compare to '2' for A7 (in a few days)
        elif lod > 2:
            loditem = 2
        self.level_of_detail_combox.setCurrentItem(loditem)
        
        # Set Ball & Stick Atom radius (percentage).  Mark 051003.
        self.cpk_atom_rad_spinbox.setValue(int (env.prefs[diBALL_AtomRadius_prefs_key] * 100.0))
        
        cpk_sf = env.prefs[cpkScaleFactor_prefs_key]
        # This slider generate signals whenever its 'setValue()' slot is called (below).
        # This creates problems (bugs) for us, so we disconnect it temporarily.
        self.disconnect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.cpk_scale_factor_slider.setValue(int (cpk_sf * 200.0)) # generates signal
        self.connect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.cpk_scale_factor_linedit.setText(str(cpk_sf))
        
        # I couldn't figure out a way to get a pref's default value without changing its current value.
        # Something like this would be very handy:
        #   default_cpk_sf = env.prefs.get_default_value(cpkScaleFactor_prefs_key)
        # Talk to Bruce about this. mark 060309.
        if cpk_sf == 0.775: # Hardcoded for now.
            # Disable the reset button if the CPK Scale Factor is currently the default value.
            self.reset_cpk_scale_factor_btn.setEnabled(0)
        else:
            self.reset_cpk_scale_factor_btn.setEnabled(1)
            
        return
    
    def _setup_bonds_page(self):
        ''' Setup widgets to initial (default or defined) values on the bonds page.
        '''
        # Set colors for bond color swatches
##        self.bond_hilite_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(blue))
##        self.bond_stretch_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(red))
##        self.bond_vane_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(violet)) # Purple
##        self.ballstick_bondcolor_frame.setPaletteBackgroundColor(RGBf_to_QColor(gray))

        #bruce 050805 here's the new way: subscribe to the preference value,
        # but make sure to only have one such subs (for one widget's bgcolor) at a time.
        # The colors in these frames will now automatically update whenever the prefs value changes.
        ##e (should modify this code to share its prefskey list with the one for restore_defaults)
        connect_colorpref_to_colorframe( bondHighlightColor_prefs_key, self.bond_hilite_color_frame)
        connect_colorpref_to_colorframe( bondStretchColor_prefs_key, self.bond_stretch_color_frame)
        connect_colorpref_to_colorframe( bondVaneColor_prefs_key, self.bond_vane_color_frame)
        connect_colorpref_to_colorframe( diBALL_bondcolor_prefs_key, self.ballstick_bondcolor_frame)

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
        self.update_bond_line_thickness_suffix()
        self.bond_line_thickness_spinbox.setValue( env.prefs[linesDisplayModeThickness_prefs_key] )
        
        # Set CPK Cylinder radius (percentage).  Mark 051003.
        self.cpk_cylinder_rad_spinbox.setValue(int (env.prefs[diBALL_BondCylinderRadius_prefs_key] * 100.0))
        
        return
        
    def _setup_undo_page(self):
        ''' Setup widgets to initial (default or defined) values on the Undo page.
        '''

        connect_checkbox_with_boolean_pref( self.undo_restore_view_checkbox, undoRestoreView_prefs_key )
        connect_checkbox_with_boolean_pref( self.undo_automatic_checkpoints_checkbox, undoAutomaticCheckpoints_prefs_key )
        self.undo_stack_memory_limit_spinbox.setValue( env.prefs[undoStackMemoryLimit_prefs_key] )
        
        # Hiding Undo Stack Memory Limit label and spinbox until Bruce hooks up the spinbox. mark 060406
        self.undo_stack_memory_limit_label.hide()
        self.undo_stack_memory_limit_spinbox.hide()
        
        #& History height widgets have been removed for A7, to be reinstituted at a later time, probably A8. mark 060314.
        #& self.history_height_lbl.hide()
        #& self.history_height_spinbox.hide()
        
        ## self.history_height_spinbox.setValue(self.history.history_height) #bruce 050810 removed this
        
        connect_checkbox_with_boolean_pref( self.msg_serial_number_checkbox, historyMsgSerialNumber_prefs_key )
        connect_checkbox_with_boolean_pref( self.msg_timestamp_checkbox, historyMsgTimestamp_prefs_key )
        return

    def _setup_window_page(self): #bruce 050810 revised this, and also call it from __init__ to be safe
        ''' Setup widgets to initial (default or defined) values on the window page.
        '''
        from platform import screen_pos_size, get_window_pos_size
        
        # Update the max value of the Current Size Spinboxes
        screen = screen_pos_size()
        ((x0,y0),(w,h)) = screen
        self.current_width_spinbox.setMaxValue(w)
        self.current_height_spinbox.setMaxValue(h)
        
        # Set value of the Current Size Spinboxes
        pos, size = get_window_pos_size(self.w)
        self.current_width_spinbox.setValue(size[0])
        self.current_height_spinbox.setValue(size[1])
        
        # Set string of Saved Size Lineedits
        from platform import get_prefs_for_window_pos_size
        from prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        pos, size = get_prefs_for_window_pos_size( self.w, keyprefix)
        self.update_saved_size(size[0], size[1])

        connect_checkbox_with_boolean_pref( self.remember_win_pos_and_size_checkbox, rememberWinPosSize_prefs_key )
        
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
        '''Slot for the Display Compass checkbox, which enables/disables the Display Compass Labels checkbox.
        '''
        self.display_compass_labels_checkbox.setEnabled(val)
        
    def set_compass_position(self, val):
        '''Set position of compass, where <val> is:
            0 = upper right
            1 = upper left
            2 = lower left
            3 = lower right
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
    
    def change_high_quality_graphics(self, state): #mark 060315.
        "Enable/disable high quality graphics during view animations."
        # Let the user know this is NIY. Addresses bug 1249 for A7. mark 060314.
        msg = "High Quality Graphics is not implemented yet."
        from HistoryWidget import orangemsg
        env.history.message(orangemsg(msg))
        
    def change_view_animation_speed(self):
        '''Sets the view animation speed between .25 (fast) and 3.0 (slow) seconds.
        '''
        # To change the range, edit the maxValue and minValue attr for the slider.
        # For example, if you want the fastest animation time to be .1 seconds,
        # change maxValue to -10.  If you want the slowest time to be 4.0 seconds,
        # change minValue to -400.  mark 060124.
        env.prefs[animateMaximumTime_prefs_key] = \
            self.animation_speed_slider.value() / -100.0

    # [WARNING: bruce 060705 copied some of the following methods into MinimizeEnergyProp.py]
    def change_endrms(self, text):
        '''Slot for EndRMS.
        This gets called each time a user types anything into the widget.
        '''
        try:
            endrms_str = double_fixup(self.endrms_validator, self.endrms_linedit.text(), self.endrms)
            self.endrms_linedit.setText(endrms_str)
            if endrms_str:
                env.prefs[Adjust_endRMS_prefs_key] = float(str(endrms_str))
            else:
                env.prefs[Adjust_endRMS_prefs_key] = -1.0
            self.endrms = endrms_str
        except:
            print_compact_traceback("bug in change_endrms ignored: ") #bruce 060627
        
    def change_endmax(self, text):
        '''Slot for EndMax.
        This gets called each time a user types anything into the widget.
        '''
        try:
            endmax_str = double_fixup(self.endmax_validator, self.endmax_linedit.text(), self.endmax)
            self.endmax_linedit.setText(endmax_str)
            if endmax_str:
                env.prefs[Adjust_endMax_prefs_key] = float(str(endmax_str))
            else:
                env.prefs[Adjust_endMax_prefs_key] = -1.0
            self.endmax = endmax_str
        except:
            print_compact_traceback("bug in change_endmax ignored: ") #bruce 060627
            
    def change_cutoverrms(self, text):
        '''Slot for Cutover RMS.
        This gets called each time a user types anything into the widget.
        '''
        try:
            cutoverrms_str = double_fixup(self.cutoverrms_validator, self.cutoverrms_linedit.text(), self.cutoverrms)
            self.cutoverrms_linedit.setText(cutoverrms_str)
            if cutoverrms_str:
                env.prefs[Adjust_cutoverRMS_prefs_key] = float(str(cutoverrms_str))
            else:
                env.prefs[Adjust_cutoverRMS_prefs_key] = -1.0
            self.cutoverrms = cutoverrms_str
        except:
            print_compact_traceback("bug in change_cutoverrms ignored: ") #bruce 060627
            
    def change_cutovermax(self, text):
        '''Slot for Cutover Max.
        This gets called each time a user types anything into the widget.
        '''
        try:
            cutovermax_str = double_fixup(self.cutovermax_validator, self.cutovermax_linedit.text(), self.cutovermax)
            self.cutovermax_linedit.setText(cutovermax_str)
            if cutovermax_str:
                env.prefs[Adjust_cutoverMax_prefs_key] = float(str(cutovermax_str))
            else:
                env.prefs[Adjust_cutoverMax_prefs_key] = -1.0
            self.cutovermax = cutovermax_str
        except:
            print_compact_traceback("bug in change_cutovermax ignored: ") #bruce 060627
            
    ########## End of slot methods for "General" page widgets ###########
    
    ########## Slot methods for "Atoms" page widgets ################
    
    def change_element_colors(self):
        '''Display the Element Color Settings Dialog.
        '''
        # Since the prefs dialog is modal, the element color settings dialog must be modal.
        self.w.showElementColorSettings(self)

    def usual_change_color(self, prefs_key, caption = "choose"): #bruce 050805
        from prefs_widgets import colorpref_edit_dialog
        colorpref_edit_dialog( self, prefs_key, caption = caption)
    
    def change_atom_hilite_color(self):
        '''Change the atom highlight color.'''
        self.usual_change_color( atomHighlightColor_prefs_key)
    
    def change_bondpoint_hilite_color(self):
        '''Change the bondpoint highlight color.'''
        self.usual_change_color( bondpointHighlightColor_prefs_key)    

    def change_hotspot_color(self): #bruce 050808 implement new slot which Mark recently added to .ui file
        '''Change the free valence hotspot color.'''
        #e fyi, we might rename hotspot to something like "bonding point" someday...
        self.usual_change_color( bondpointHotspotColor_prefs_key)

    def reset_atom_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
            atomHighlightColor_prefs_key,
            bondpointHighlightColor_prefs_key,
            bondpointHotspotColor_prefs_key
        ])
    
    def change_level_of_detail(self, level_of_detail_item): #bruce 060215 revised this
        '''Change the level of detail, where <level_of_detail_item> is a value between 0 and 3 where:
            0 = low
            1 = medium
            2 = high
            3 = variable (based on number of atoms in the part)
                [note: the prefs db value for 'variable' is -1, to allow for higher LOD levels in the future] 
        '''
        lod = level_of_detail_item
        if level_of_detail_item == 3:
            lod = -1
        env.prefs[levelOfDetail_prefs_key] = lod
        self.glpane.gl_update()
        # the redraw this causes will (as of tonight) always recompute the correct drawLevel (in Part._recompute_drawLevel),
        # and chunks will invalidate their display lists as needed to accomodate the change. [bruce 060215]
        return
        
    def change_ballstick_atom_radius(self, val):
        '''Change the CPK (Ball and Stick) atom radius by % value <val>.
        '''
        #bruce 060607 renamed change_cpk_atom_radius -> change_ballstick_atom_radius in this file and the .py/.ui dialog files.
        env.prefs[diBALL_AtomRadius_prefs_key] = val * .01
        self.glpane.gl_update() #k this gl_update is probably not needed and sometimes a slowdown [bruce 060607]
    
    def change_cpk_scale_factor(self, val):
        '''Slot called when moving the slider.
        Change the % value displayed in the LineEdit widget for CPK Scale Factor.
        '''
        sf = val * .005
        self.cpk_scale_factor_linedit.setText(str(sf))
        
    def save_cpk_scale_factor(self):
        '''Slot called when releasing the slider.
        Saves the CPK (VdW) scale factor.
        '''
        env.prefs[cpkScaleFactor_prefs_key] = self.cpk_scale_factor_slider.value() * .005
        self.glpane.gl_update()
        self.reset_cpk_scale_factor_btn.setEnabled(1)
        
    def reset_cpk_scale_factor(self):
        '''Slot called when pressing the CPK Scale Factor reset button.
        Restores the default value of the CPK Scale Factor.
        '''
        env.prefs.restore_defaults([cpkScaleFactor_prefs_key])
        self.cpk_scale_factor_slider.setValue(int (env.prefs[cpkScaleFactor_prefs_key] * 200.0))
            # generates signal (good), which calls slot save_cpk_scale_factor().
        self.reset_cpk_scale_factor_btn.setEnabled(0)
        
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
    
    def change_ballstick_bondcolor(self): #bruce 060607 renamed this in this file and .ui/.py dialog files
        '''Change the bond cylinder color used in Ball & Stick display mode.'''
        self.usual_change_color( diBALL_bondcolor_prefs_key)        
    
    def reset_bond_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
            bondHighlightColor_prefs_key,
            bondStretchColor_prefs_key,
            bondVaneColor_prefs_key,
            diBALL_bondcolor_prefs_key,
        ])
        
    def change_high_order_bond_display(self, val): #bruce 050806 filled this in
        "Slot for the button group that sets the high order bond display."
        #  ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
        try:
            symbol = {0:'multicyl', 1:'vane', 2:'ribbon'}[val]
            # note: this decoding must use the same (arbitrary) int->symbol mapping as the button group does.
            # It's just a coincidence that the order is the same as in the prefs-type listed above.
        except KeyError: #bruce 060627 added specific exception class (untested)
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
        self.update_bond_line_thickness_suffix()
        
    def update_bond_line_thickness_suffix(self):
        '''Updates the suffix for the bond line thickness spinbox.
        '''
        if env.prefs[linesDisplayModeThickness_prefs_key] == 1:
            self.bond_line_thickness_spinbox.setSuffix(' pixel')
        else:
            self.bond_line_thickness_spinbox.setSuffix(' pixels')
        
    def change_ballstick_cylinder_radius(self, val): 
        '''Change the CPK (Ball and Stick) cylinder radius by % value <val>.
        '''
        #bruce 060607 renamed change_cpk_cylinder_radius -> change_ballstick_cylinder_radius (in this file and .ui/.py dialog files)
        env.prefs[diBALL_BondCylinderRadius_prefs_key] = val *.01
        self.glpane.gl_update() #k gl_update is probably not needed and in some cases is a slowdown [bruce 060607 comment]
    
    ########## End of slot methods for "Bonds" page widgets ###########
    
    ########## Slot methods for "Modes" page widgets ################

    def mode_changed(self, val):
        '''Slot called when the user changes the mode in the mode-bgcolor drop box.
        '''
        self.currentItem_mode = self.glpane._find_mode(modes[val])
        
        self.display_mode_combox.setCurrentItem(self.currentItem_mode.displayMode) 
            # Update the Display Mode combobox.
        
        if modes[val] == 'COOKIE':
            # Cannot change Cookie mode's display mode.
            self.display_mode_combox.setEnabled(False)
        else:
            self.display_mode_combox.setEnabled(True)
        
        # Update the modes page.
        if self.currentItem_mode.backgroundGradient:
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
        # Same thing goes for change_bg1_color().  Mark 051029.
        if self.currentItem_mode == self.glpane.mode:
            self.glpane.gl_update()
        
    def bg_solid_setup(self):
        '''Setup the BG color page for a solid fill type.
        '''

        self.bg1_color_lbl.setEnabled(True)
        self.bg1_color_frame.setEnabled(True)
        self.choose_bg1_color_btn.setEnabled(True)
        
        self.fill_type_combox.setCurrentItem(0) # Solid
        
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        self.bg1_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(self.currentItem_mode.backgroundColor))
        
        self.currentItem_mode.set_backgroundGradient(False) # This also stores the pref in the db.
    
    def bg_gradient_setup(self):
        '''Setup the Modes page for the background gradient fill type.
        '''

        self.bg1_color_lbl.setEnabled(False)
        self.bg1_color_frame.setEnabled(False)
        self.choose_bg1_color_btn.setEnabled(False)
        
        self.fill_type_combox.setCurrentItem(1) # Gradient
        
        # Get the bg color rgb values of the mode selected in the "Mode" combo box.
        self.bg1_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(self.currentItem_mode.backgroundColor))
        
        self.currentItem_mode.set_backgroundGradient(True) # This also stores the pref in the db.

    def change_bg1_color(self):
        '''Change a mode's primary background color.
        '''
        # Allow user to select a new background color and set it.
        c = QColorDialog.getColor(self.bg1_color_frame.paletteBackgroundColor(), self, "choose")
        if c.isValid():
            bgcolor = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
            self.currentItem_mode.set_backgroundColor( bgcolor )
            self.bg1_color_frame.setPaletteBackgroundColor(c)
            
        # Update the GLPane if the selected mode is the current mode.
        # See Bruce's note about this in fill_type_changed().  Mark 051029.
        if self.currentItem_mode == self.glpane.mode:
            self.glpane.gl_update()
                
    def restore_default_bgcolor(self):
        '''Slot for "Restore Default Color" button, which restores the selected mode's bg color.
        '''
        # Set the background color and gradient to the default.
        self.currentItem_mode.set_backgroundColor(self.currentItem_mode.__class__.backgroundColor)
        self.currentItem_mode.set_backgroundGradient(self.currentItem_mode.__class__.backgroundGradient)
        # Now update the UI.
        if self.currentItem_mode.__class__.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()
        # If the selected mode is the current mode, update the glpane to display the new (default) bg color.
        if self.currentItem_mode == self.glpane.mode:
            self.glpane.gl_update()
            
    def set_default_display_mode(self, val): #bruce 050810 revised this to set the pref immediately
        '''Set default display mode of GLpane.
        '''
        if val == env.prefs[defaultDisplayMode_prefs_key]:
            print "No Change in Default Display Mode: ddm=", val
            return
        # set the pref
        env.prefs[defaultDisplayMode_prefs_key] = val
        
        # If the current mode's display mode is 'Default', update.
        if self.glpane.mode.displayMode == diDEFAULT:
            self.glpane.setDisplay(val, True)
            self.glpane.gl_update()
        
    def change_display_mode(self, val):
        '''Slot for "Display Mode" dropbox, which changes the display mode for this mode.
        '''
        self.currentItem_mode.set_displayMode( val )
        # If the selected mode is the current mode, update the model with the new display mode.
        if self.currentItem_mode == self.glpane.mode:
            self.glpane.setDisplay(val, True)
            self.glpane.gl_update()
        
    ########## End of slot methods for "Modes" page widgets ###########
    
    ########## Slot methods for "Lighting" page widgets ################

    def change_lighting(self):
        '''Updates glpane lighting using the current lighting parameters from the
        light checkboxes and sliders. This is also the slot for the light sliders.
        '''
        
        light_num = self.light_combobox.currentItem()
        
        light1, light2, light3 = self.glpane.getLighting()
        
        a = self.light_ambient_slider.value() * .01
        d = self.light_diffuse_slider.value() * .01
        s = self.light_specularity_slider.value()  * .01
        
        self.light_ambient_linedit.setText(str(a))
        self.light_diffuse_linedit.setText(str(d))
        self.light_specularity_linedit.setText(str(s))
        
        new_light = [  self.light_color, a, d, s, \
                    float(str(self.light_x_linedit.text())), \
                    float(str(self.light_y_linedit.text())), \
                    float(str(self.light_z_linedit.text())), \
                    self.light_checkbox.isChecked()]
                
        # This is a kludge.  I'm certain there is a more elegant way.  Mark 051204.
        if light_num == 0:
            self.glpane.setLighting([new_light, light2, light3])
        elif light_num == 1:
            self.glpane.setLighting([light1, new_light, light3])
        elif light_num == 2:
            self.glpane.setLighting([light1, light2, new_light])
        else:
            print "Unsupported light # ", light_num,". No lighting change made."
        
    def change_active_light(self):
        '''Slot for the Light number combobox.  This changes the current light.
        '''
        self._setup_lighting_page()

    def change_light_color(self):
        '''Slot for light color "Choose" button.  Saves the new color in the prefs db.
        Changes the current Light color in the graphics area and the light color swatch in the UI.'''
        self.usual_change_color(self.current_light_key)
        self.light_color = env.prefs[self.current_light_key]
        self.save_lighting()
        
    def update_light_combobox_items(self):
        '''Updates all light combobox items with '(On)' or '(Off)' label.
        '''
        for i in range(3):
            if self.lights[i][7]:
                txt = "%d (On)" % (i+1)
            else:
                txt = "%d (Off)" % (i+1)
            self.light_combobox.changeItem(txt, i)
    
    def toggle_light(self, on):
        '''Slot for light 'On' checkbox.  
        It updates the current item in the light combobox with '(On)' or '(Off)' label.
        '''
        if on:
            txt = "%d (On)" % (self.light_combobox.currentItem()+1)
        else:
            txt = "%d (Off)" % (self.light_combobox.currentItem()+1)
        self.light_combobox.setCurrentText(txt)
        
        self.save_lighting()
            
    def save_lighting(self):
        '''Saves lighting parameters (but not material specularity parameters) to pref db.
        This is also the slot for light sliders (only when released).
        '''
        self.change_lighting()
        self.glpane.saveLighting()

    def toggle_material_specularity(self, val):
        '''This is the slot for the Material Specularity Enabled checkbox.
        '''
        env.prefs[material_specular_highlights_prefs_key] = val
                        
    def change_material_finish(self, finish):
        '''This is the slot for the Material Finish slider.
        'finish' is between 0 and 100. 
        Saves finish parameter to pref db.
        '''
        # For whiteness, the stored range is 0.0 (Metal) to 1.0 (Plastic).
        # The Qt slider range is 0 - 100, so we multiply by 100 to set the slider.  Mark. 051129.
        env.prefs[material_specular_finish_prefs_key] = float(finish * 0.01)
        self.ms_finish_linedit.setText(str(finish * 0.01))
        
    def change_material_shininess(self, shininess):
        ''' This is the slot for the Material Shininess slider.
        'shininess' is between 15 (low) and 60 (high).
        '''
        env.prefs[material_specular_shininess_prefs_key] = float(shininess)
        self.ms_shininess_linedit.setText(str(shininess))
        
    def change_material_brightness(self, brightness):
        ''' This is the slot for the Material Brightness slider.
        'brightness' is between 0 (low) and 100 (high).
        '''
        env.prefs[material_specular_brightness_prefs_key] = float(brightness * 0.01)
        self.ms_brightness_linedit.setText(str(brightness * 0.01))
        
    def change_material_finish_start(self):
        if debug_sliders: print "Finish slider pressed"
        env.prefs.suspend_saving_changes() #bruce 051205 new prefs feature - keep updating to glpane but not (yet) to disk
        
    def change_material_finish_stop(self):
        if debug_sliders: print "Finish slider released"
        env.prefs.resume_saving_changes() #bruce 051205 new prefs feature - save accumulated changes now
    
    def change_material_shininess_start(self):
        if debug_sliders: print "Shininess slider pressed"
        env.prefs.suspend_saving_changes()
        
    def change_material_shininess_stop(self):
        if debug_sliders: print "Shininess slider released"
        env.prefs.resume_saving_changes()
        
    def change_material_brightness_start(self):
        if debug_sliders: print "Brightness slider pressed"
        env.prefs.suspend_saving_changes()
        
    def change_material_brightness_stop(self):
        if debug_sliders: print "Brightness slider released"
        env.prefs.resume_saving_changes()
        
    def reset_lighting(self):
        "Slot for Reset button"
        # This has issues.  I intend to remove the Reset button for A7.  Confirm with Bruce.  Mark 051204.
        self._setup_material_group(reset=True)
        self._setup_lighting_page(self.original_lights)
        self.glpane.saveLighting()
        
    def restore_default_lighting(self):
        "Slot for Restore Defaults button"
        
        self.glpane.restoreDefaultLighting()
        
        # Restore defaults for the Material Specularity properties
        env.prefs.restore_defaults([
            material_specular_highlights_prefs_key,
            material_specular_shininess_prefs_key,
            material_specular_finish_prefs_key,
            material_specular_brightness_prefs_key, #bruce 051203 bugfix
            ])
        
        self._setup_lighting_page()
        self.save_lighting()

    ########## End of slot methods for "Lighting" page widgets ###########
    
    ########## Slot methods for "Plug-ins" page widgets ################

    def set_gamess_path(self):
        '''Slot for GAMESS path "Choose" button.
        '''
        gamess_exe = get_filename_and_save_in_prefs(self, gmspath_prefs_key, 'Choose GAMESS Executable')
         
        if gamess_exe:
            self.gamess_path_linedit.setText(os.path.normpath(gamess_exe))
            
    def enable_gamess(self, enable=True):
        '''GAMESS is enabled when enable=True.
        GAMESS is disabled when enable=False.
        '''
        if enable:
            self.gamess_path_linedit.setEnabled(1)
            self.gamess_choose_btn.setEnabled(1)
            env.prefs[gamess_enabled_prefs_key] = True
            
        else:
            self.gamess_path_linedit.setEnabled(0)
            self.gamess_choose_btn.setEnabled(0)
            self.gamess_path_linedit.setText("")
            env.prefs[gmspath_prefs_key] = ''
            env.prefs[gamess_enabled_prefs_key] = False

    def set_nanohive_path(self):
        '''Slot for Nano-Hive path "Choose" button.
        '''

        nh = get_filename_and_save_in_prefs(self, nanohive_path_prefs_key, 'Choose Nano-Hive Executable')
        
        if nh:
            self.nanohive_path_linedit.setText(nh)
            
    def enable_nanohive(self, enable=True):
        '''Enable/disables Nano-Hive plug-in when enable=True/False.
        '''
        if enable:
            self.nanohive_path_linedit.setEnabled(1)
            self.nanohive_choose_btn.setEnabled(1)
            # Leave Nano-Hive action button/menu hidden for A7.  Mark 2006-01-04.
            # self.w.simNanoHiveAction.setVisible(1)
            
            # Sets the Nano-Hive (executable) path to the standard location, if it exists.
            if not env.prefs[nanohive_path_prefs_key]:
                env.prefs[nanohive_path_prefs_key] = get_default_plugin_path(
                    "C:\\Program Files\\Nano-Hive\\bin\\win32-x86\\NanoHive.exe", \
                    "/usr/local/bin/NanoHive", \
                    "/usr/local/bin/NanoHive")

            
            env.prefs[nanohive_enabled_prefs_key] = True
            self.nanohive_path_linedit.setText(env.prefs[nanohive_path_prefs_key])
                
            # Create the Nano-Hive dialog widget.
            # Not needed for A7.  Mark 2006-01-05.
            #if not self.w.nanohive:
            #    from NanoHive import NanoHive
            #    self.w.nanohive = NanoHive(self.assy)
            
        else:
            self.nanohive_path_linedit.setEnabled(0)
            self.nanohive_choose_btn.setEnabled(0)
            self.w.nanohive = None
            self.w.simNanoHiveAction.setVisible(0)
            self.nanohive_path_linedit.setText("")
            env.prefs[nanohive_path_prefs_key] = ''
            env.prefs[nanohive_enabled_prefs_key] = False
            
    def set_povray_path(self):
        '''Slot for POV-Ray path "Choose" button.
        '''
        povray_exe = get_filename_and_save_in_prefs(self, povray_path_prefs_key, 'Choose POV-Ray Executable')
         
        if povray_exe:
            self.povray_path_linedit.setText(povray_exe)
            
    def enable_povray(self, enable=True):
        '''POV-Ray is enabled when enable=True.
        POV-Ray is disabled when enable=False.
        '''
        if enable:
            self.povray_path_linedit.setEnabled(1)
            self.povray_choose_btn.setEnabled(1)
            env.prefs[povray_enabled_prefs_key] = True
            
            # Sets the POV-Ray (executable) path to the standard location, if it exists.
            if not env.prefs[povray_path_prefs_key]:
                env.prefs[povray_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\pvengine.exe", \
                    "/usr/local/bin/pvengine", \
                    "/usr/local/bin/pvengine")
            
            self.povray_path_linedit.setText(env.prefs[povray_path_prefs_key])
            
        else:
            self.povray_path_linedit.setEnabled(0)
            self.povray_choose_btn.setEnabled(0)
            self.povray_path_linedit.setText("")
            env.prefs[povray_path_prefs_key] = ''
            env.prefs[povray_enabled_prefs_key] = False
        self._update_povdir_enables() #bruce 060710
            
    def set_megapov_path(self):
        '''Slot for MegaPOV path "Choose" button.
        '''
        megapov_exe = get_filename_and_save_in_prefs(self, megapov_path_prefs_key, 'Choose MegaPOV Executable')
         
        if megapov_exe:
            self.megapov_path_linedit.setText(megapov_exe)
            
    def enable_megapov(self, enable=True):
        '''MegaPOV is enabled when enable=True.
        MegaPOV is disabled when enable=False.
        '''
        if enable:
            self.megapov_path_linedit.setEnabled(1)
            self.megapov_choose_btn.setEnabled(1)
            env.prefs[megapov_enabled_prefs_key] = True
            
            # Sets the MegaPOV (executable) path to the standard location, if it exists.
            if not env.prefs[megapov_path_prefs_key]:
                env.prefs[megapov_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\megapov.exe", \
                    "/usr/local/bin/megapov", \
                    "/usr/local/bin/megapov")
            
            self.megapov_path_linedit.setText(env.prefs[megapov_path_prefs_key])
            
        else:
            self.megapov_path_linedit.setEnabled(0)
            self.megapov_choose_btn.setEnabled(0)
            self.megapov_path_linedit.setText("")
            env.prefs[megapov_path_prefs_key] = ''
            env.prefs[megapov_enabled_prefs_key] = False
        self._update_povdir_enables() #bruce 060710

    # pov include directory [bruce 060710 for Mac A8; will be A8.1 in Windows, not sure about Linux]
    
    def _update_povdir_enables(self): #bruce 060710
        """[private method]
        Call this whenever anything changes regarding when to enable the povdir checkbox, line edit, or choose button.
        We enable the checkbox when either of the POV-Ray or MegaPOV plugins is enabled.
        We enable the line edit and choose button when that condition holds and when the checkbox is checked.
        We update this when any relevant checkbox changes, or when showing this page.
        This will work by reading prefs values, so only call it from slot methods after they have updated prefs values.
        """
        enable_checkbox = env.prefs[povray_enabled_prefs_key] or env.prefs[megapov_enabled_prefs_key]
        self.povdir_checkbox.setEnabled(enable_checkbox)
        self.povdir_lbl.setEnabled(enable_checkbox)
        enable_edits = enable_checkbox and env.prefs[povdir_enabled_prefs_key]
            # note: that prefs value should and presumably does agree with self.povdir_checkbox.isChecked()
        self.povdir_linedit.setEnabled(enable_edits)
        self.povdir_choose_btn.setEnabled(enable_edits)
        return
    
    def enable_povdir(self, enable=True): #bruce 060710
        '''slot method for povdir checkbox.
        povdir is enabled when enable=True.
        povdir is disabled when enable=False.
        '''
        env.prefs[povdir_enabled_prefs_key] = not not enable
        self._update_povdir_enables()
##        self.povdir_linedit.setText(env.prefs[povdir_path_prefs_key])
        return
            
    def set_povdir(self): #bruce 060710
        '''Slot for Pov include dir "Choose" button.
        '''
        povdir_path = get_dirname_and_save_in_prefs(self, povdir_path_prefs_key, 'Choose Custom POV-Ray Include directory')
        # note: return value can't be ""; if user cancels, value is None;
        # to set "" you have to edit the lineedit text directly, but this doesn't work since
        # no signal is caught to save that into the prefs db!
        # ####@@@@ we ought to catch that signal... is it returnPressed?? would that be sent if they were editing it, then hit ok?
        # or if they clicked elsewhere? (currently that fails to remove focus from the lineedits, on Mac, a minor bug IMHO)
        # (or uncheck the checkbox for the same effect). (#e do we want a "clear" button, for A8.1?)
        
        if povdir_path:
            self.povdir_linedit.setText(os.path.normpath(povdir_path))
            # the function above already saved it in prefs, under the same condition
        return
    
    def povdir_linedit_textChanged(self, *args): #bruce 060710
        if debug_povdir_signals():
            print "povdir_linedit_textChanged",args
            # this happens on programmatic changes, such as when the page is shown or the choose button slot sets the text
        try:
            # note: Ideally we'd only do this when return was pressed, mouse was clicked elsewhere (with that also removing keyfocus),
            # other keyfocus removals, including dialog ok or cancel. That is mostly nim,
            # so we have to do it all the time for now -- this is the only way for the user to set the text to "".
            # (This even runs on programmatic sets of the text. Hope that's ok.)
            env.prefs[povdir_path_prefs_key] = path = str( self.povdir_linedit.text() ).strip()
            if debug_povdir_signals():
                print "debug fyi: set pov include dir to [%s]" % (path,)
        except:
            if env.debug():
                print_compact_traceback("bug, ignored: ")
        return
    
    def povdir_linedit_returnPressed(self, *args): #bruce 060710
        if debug_povdir_signals():
            print "povdir_linedit_returnPressed",args
            # this happens when return is pressed in the widget, but NOT when user clicks outside it
            # or presses OK on the dialog -- which means it's useless when taken alone,
            # in case user edits text and then presses ok without ever pressing return.

    ########## End of slot methods for "Plug-ins" page widgets ###########
    
    ########## Slot methods for "Window" (former name "Caption") page widgets ################
    
    def change_undo_stack_memory_limit(self, mb_val):
        '''Slot for 'Undo Stack Memory Limit' spinbox. Sets the RAM limit for the Undo Stack.
        <mb-val> can range from 0-99999 (MB).
        '''
        env.prefs[undoStackMemoryLimit_prefs_key] = mb_val
        
    ########## End of slot methods for "Plug-ins" page widgets ###########

    ########## Slot methods for "Window" (former name "Caption") page widgets ################

    #e there are some new slot methods for this in other places, which should be refiled here. [bruce 050811]
    
    def change_window_size(self, val=0):
        '''Slot for both the width and height spinboxes that change the current window size.
        Also called from other slots to change the window size based on new values in spinboxes.
        <val> is not used.
        '''
        w = self.current_width_spinbox.value()
        h = self.current_height_spinbox.value()
        self.w.resize(w,h)
        
    def update_saved_size(self, w, h):
        'Update the saved width and height text'
        self.saved_width_lineedit.setText(QString(str(w) + " pixels"))
        self.saved_height_lineedit.setText(QString(str(h) + " pixels"))

    def save_current_win_pos_and_size(self): #bruce 051218; see also debug.py's _debug_save_window_layout
        from platform import save_window_pos_size
        from prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        save_window_pos_size( self.w, keyprefix) # prints history message
        size = self.w.size()
        self.update_saved_size(size.width(), size.height())
        return
    
    def restore_saved_size(self):
        'Restore the window size, but not the position, from the prefs db'
        from platform import get_prefs_for_window_pos_size
        from prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        pos, size = get_prefs_for_window_pos_size( self.w, keyprefix)
        w = size[0]
        h = size[1]
        self.update_saved_size(w, h)
        self.current_width_spinbox.setValue(w)
        self.current_height_spinbox.setValue(h)
        self.change_window_size()
    
    def set_caption_fullpath(self, val): #bruce 050810 revised this
        # there is now a separate connection which sets the pref, so this is not needed:
        ## self.win.caption_fullpath = val
        # and there is now a Formula in MWsemantics which makes the following no longer needed:
        ## self.win.update_mainwindow_caption(self.win.assy.has_changed())
        pass

    def update_number_spinbox_valueChanged(self,a0):
        # some day we'll use this to set a user preferences, for now it's a no-op
        pass
        
    ########## End of slot methods for "Window" page widgets ###########
    
    ########## Slot methods for "Undo" page widgets ################
    
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
        try:
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
            elif pagename == 'Lighting':
                self._setup_lighting_page()
            elif pagename == 'Plug-ins':
                self._setup_plugins_page()
            elif pagename == 'Undo':
                self._setup_undo_page()
            elif pagename == 'Window':
                self._setup_window_page()
            else:
                print 'Error: Preferences page unknown: ', pagename
        except:
            print_compact_traceback("bug in setup_current_page ignored: ") #bruce 060627
            
    def accept(self):
        '''The slot method for the 'OK' button.'''
        # self._update_prefs() # Mark 050919
        if self.mmkit_was_hidden: self.glpane.mode.MMKit.show() # Mark 060704.
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
        if self.mmkit_was_hidden: self.glpane.mode.MMKit.show() # Mark 060704.
        QDialog.reject(self)

    pass # end of class UserPrefs

# end