# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_PreferencesDialog.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in the NE1 Preferences dialog only. 

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text 
for widgets in the Main Window.

@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

"""
import sys

def whatsThis_PreferencesDialog(preferencesDialog):
    """
    Assigning the I{What's This} text for the Preferences dialog.
    """
    
    _pd = preferencesDialog

    if sys.platform == 'darwin':        
        # TODO: figure out how to get fix_whatsthis_text_and_links to handle
        # this for us (like it does for most whatsthis text).
        # For more info see comments from today in other files.
        # [bruce 081209 comment]
        _keyString = "<b>(Cmd + C and Cmd + V)</b> respectively"
    else:
        _keyString = "<b>(Ctrl + C and Ctrl + V)</b> respectively"
    
    #General preference 
    _text = """<b>Offset scale factor for pasting chunks</b>
    <p>When one or more chunks, that are placed as independent nodes in the 
    Model Tree, are copied and then pasted using the modifier 
    keys %s, this scale factor determines the offset of the pasted chunks 
    from the original chunks. Note that if the copied selection includes any 
    DNA objects such as DNA segments, strands etc, the program will use 
    an offset scale that is used for pasting the DNA objects instead of this 
    offset scale) </p>"""%(_keyString)
    _pd.pasteOffsetScaleFactorForChunks_doubleSpinBox.setWhatsThis(_text)
    _pd.pasteOffsetForChunks_lable.setWhatsThis(_text)
    
    _text = """<b>Offset scale factor for pasting Dna objects</b>
    <p>When one or more DNA objects such as DNA segments, strands etc, are 
    copied and then pasted using the modifier keys %s, this scale factor 
    determines the offset of the pasted DNA objects from the original ones. 
    Note that this also applies to pasting chunks within a group in the Model 
    Tree. </p>"""%(_keyString)
    _pd.pasteOffsetScaleFactorForDnaObjects_doubleSpinBox.setWhatsThis(_text)
    _pd.pasteOffsetForDna_lable.setWhatsThis(_text)
    # Bond line thickness

    _text = \
        "<b>Bond line thickness</b>"\
        "<p>"\
        "Sets the line thickness to <i>n</i> pixels wheneven bonds "\
        "are rendered as lines (i.e. when the global display style is set to "\
        "<b>Lines</b> display style)."\
        "</p>"

    _pd.bond_line_thickness_spinbox.setWhatsThis(_text) # nice!
    _pd.textLabel1.setWhatsThis(_text)
    # and What's This text for all the others widgets (yuk!)
    
    _pd.display_origin_axis_checkbox.setWhatsThis(
        """<p><b>Display origin axis</b></p>
        <p>
        Shows/Hides the origin axis""")
    _pd.display_pov_axis_checkbox.setWhatsThis(
        """<p><b>Display point of view axis</b></p>
        <p>
        Shows/Hides the point of view axis""")
    _text = \
        """<p><b>Display compass</b></p>
        <p>
        Shows/Hides the display compass"""
    _pd.compassGroupBox.setWhatsThis(_text)
    _pd.display_compass_labels_checkbox.setWhatsThis(
        """Shows/Hides the display compass axis labels.""")
    _pd.watch_motion_groupbox.setWhatsThis(
        """<p><b>Watch motion in real time</b></p>
        <p>
        Enables/disables realtime graphical updates during adjust operations
        when using <b>Adjust All</b> or <b>Adjust Selection</b>""")
    _text = \
        """Changes the location of the display compass."""
    _pd.textLabel1_4.setWhatsThis(_text)
    _pd.compass_position_combox.setWhatsThis(_text)
    _text = \
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the adjustment.
        This allows the user to monitor results during adjustments.
        </p>"""
    _pd.update_number_spinbox.setWhatsThis(_text)
    _pd.update_units_combobox.setWhatsThis(_text)
        
    _pd.update_every_rbtn.setWhatsThis(
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the adjustment.
        This allows the user to monitor results during adjustments.
        </p>""")
    _pd.update_asap_rbtn.setWhatsThis(
        """<b>Update as fast as possible</b>
        <p>
        Update every 2 seconds, or faster (up to 20x/sec)if it doesn't
        slow adjustments by more than 20%
        </p>""")
    _text = \
        """<b>EndRMS</b>
        <p>
        Continue until this RMS force is reached.
        </p>"""
    _pd.endrms_lbl.setWhatsThis(_text)
    _pd.endRmsDoubleSpinBox.setWhatsThis(_text)
    _text = \
        """<b>EndMax</b>
        <p>
        Continue until no interaction exceeds this force.
        </p>"""
    _pd.endmax_lbl.setWhatsThis(_text)
    _pd.endMaxDoubleSpinBox.setWhatsThis(_text)
    
    _text = \
        """<b>CutoverMax</b>
        <p>Use steepest descent until no interaction exceeds this force.
        </p>"""
    _pd.cutovermax_lbl.setWhatsThis(_text)
    _pd.cutoverMaxDoubleSpinBox.setWhatsThis(_text)
    
    _text = \
        """<b>CutoverRMS</b>
        <p>
        Use steepest descent until this RMS force is reached.
        </p>"""
    _pd.cutoverRmsDoubleSpinBox.setWhatsThis(_text)
    _pd.cutoverrms_lbl.setWhatsThis(_text)
    # Sponsor Logos Download Permission
    _pd.sponsorLogosGroupBox.setWhatsThis(
        """<b>Sponsor logos download permission</b>
        <p>
        This group of buttons sets the permission for downloading sponsor logos.
        </p>""")
    _pd.logoAlwaysAskRadioBtn.setWhatsThis(
        """<b>Always ask before downloading</b>
        <p>
        When sponsor logos have been updated, ask permission to download them.
        </p>""")
    _pd.logoNeverAskRadioBtn.setWhatsThis(
        """<b>Never ask before downloading</b>
        <p>
        When sponsor logos have been updated, download them without asking
        permission to do so.
        </p>""")
    _pd.logoNeverDownLoadRadioBtn.setWhatsThis(
        """<b>Never download</b>
        <p>
        Don't ask permission to download sponsor logos and don't download them.
        </p>""")

    _pd.animate_views_checkbox.setWhatsThis(
        """<p><b>Animate between views</b></p>
        <p>
        Enables/disables animation when switching between the current view
        and a new view.
        </p>""")
    _text = \
        """<p><b>View animation speed</b></p>
        <p>
        Sets the animation speed when animating between views 
        (i.e. Front view to Right view).  It is recommended that this be set 
        to Fast when working on large models.
        </p>"""
    _pd.textLabel1_5.setWhatsThis(_text)
    _pd.animation_speed_slider.setWhatsThis(_text)
    
    _text = \
        """<p><b>Mouse rotation speed</b></p>
        <p>
        Specifies the speed factor to use when rotating the view by dragging
        the mouse (i.e. during the <b>Rotate</b> command or when using the
        middle mouse button).
        </p>"""
    _pd.mouseSpeedDuringRotation_slider.setWhatsThis(_text)
    _pd.rotationSensitivity_txtlbl.setWhatsThis(_text)
    
    _text = \
        """<p><b>Level of detail</b></p>
        <p>
        Sets the level of detail for atoms and bonds.<br>
        <br>  
        <b>High</b> = Best graphics quality (slowest rendering speed)<br>
        <b>Medium</b> = Good graphics quality<br> 
        <b>Low</b> = Poor graphics quality (fastest rendering speed) <br>
        <b>Variable</b> automatically switches between High, Medium and Low
        based on the model size (number of atoms).
        </p>"""
    _pd.textLabel1_7.setWhatsThis(_text)
    _pd.level_of_detail_combox.setWhatsThis(_text)
    
    _pd.textLabel1_3_2.setWhatsThis(
        """<p><b>Ball and stick atom scale</b></p>
        <p>
        Sets the ball and stick atom scale factor. It is best to
        change the scale factor while the current model is displayed
        in ball and stick mode.""")
    _pd.ballStickAtomScaleFactorSpinBox.setWhatsThis(
        """<p><b>Ball and stick atom scale</b></p>
        <p>
        Sets the atom scale factor for ball and stick display style. It is best
        to change the scale factor while the global display style is
        set to ball and stick.""")
    _pd.textLabel1_3_2_2.setWhatsThis(
        """<p><b>CPK atom scale</b></p>
        <p>
        Changes the CPK atom scale factor. It is best to change the scale
        factor while in CPK display mode so you can see the graphical effect of
        changing the scale.""")
    _pd.cpkAtomScaleFactorDoubleSpinBox.setWhatsThis(
        """<p><b>CPK atom scale</b></p>
        <p>
        Set the atom scale factor for CPK display style. It is best to change
        the scale factor while the global display style is set to CPK so you
        can see the graphical effect of changing the scale.""")
    _pd.reset_cpk_scale_factor_btn.setWhatsThis(
        """Restore the default value of the CPK scale factor""")
    _pd.reset_ballstick_scale_factor_btn.setWhatsThis(
        """Restore the default value of the ball and stick scale factor.""")
    _pd.haloWidthResetButton.setWhatsThis(
        """Restore the default value of halo width.""")
    _pd.multCyl_radioButton.setWhatsThis(
        """<p><b>Multiple cylinders</b></p>
        <p>
        <p><b>High order bonds</b>
        are displayed using <b>multiple cylinders.</b></p>
        <p>
        <b>Double bonds</b> are drawn with two cylinders.<br>
        <b>Triple bonds</b> are drawn with three cylinders.<br>
        <b>Aromatic bonds</b> are drawn as a single cylinder with a
        short green cylinder in the middle.""")
    _pd.vanes_radioButton.setWhatsThis(
        """<p><b>Vanes</b></p>
        <p>
        <p><i>High order bonds</i> are displayed using <b>Vanes.</b></p>
        <p>
        <p>Vanes represent <i>pi systems</i> in high order bonds and are
        rendered as rectangular polygons. The orientation of the vanes
        approximates the orientation of the pi system(s).</p>
        <p>Create an acetylene or ethene molecule and select this option
        to see how vanes are rendered.
        </p>""")
    _pd.ribbons_radioButton.setWhatsThis(
        """<p><b>Ribbons</b></p>
        <p>
        <p><i>High order bonds</i> are displayed using <b>Ribbons.</b></p>
        <p>
        <p>Ribbons represent <i>pi systems</i> in high order bonds and are
        rendered as ribbons. The orientation of the ribbons approximates the
        orientation of the pi system.</p>
        <p>Create an acetylene or ethene molecule and select this option
        to see how ribbons are rendered.
        </p>""")
    _pd.show_bond_labels_checkbox.setWhatsThis(
        """<p><b>Show bond type letters</b></p>
        <p>
        <p>Shows/Hides bond type letters (labels) on top of bonds.</p>
        <u>Bond type letters:</u><br>
        <b>2</b> = Double bond<br>
        <b>3</b> = Triple bond<br>
        <b>A</b> = Aromatic bond<br>
        <b>G</b> = Graphitic bond<br>""")
    _pd.show_valence_errors_checkbox.setWhatsThis(
        """<p><b>Show valence errors</b></p>
        <p>
        Enables/Disables valence error checker.</p>
        When enabled, atoms with valence errors are displayed with a pink
        wireframe sphere. This indicates that one or more of the atom's bonds
        are not of the correct order (type), or that the atom has the wrong
        number of bonds, or (for PAM DNA pseudoatoms) that there is some error
        in bond directions or in which PAM elements are bonded. The error
        details can be seen in the tooltip for the atom.""")
    _text = \
        """<p><b>Ball and stick bond scale</b></p>
        <p>
        Set scale (size) factor for the cylinder representing bonds
        in ball and stick display mode"""
    _pd.textLabel1_3.setWhatsThis(_text)
    _pd.cpk_cylinder_rad_spinbox.setWhatsThis(_text)
    
    _pd.autobond_checkbox.setWhatsThis(
        """<p>Default setting for <b>Autobonding</b> at startup
        (enabled/disabled)</p>""")

    _pd.water_checkbox.setWhatsThis(
        """<p>Default setting for <b>Water (surface)</b> at startup
        (enabled/disabled)</p>""")
    _pd.buildmode_select_atoms_checkbox.setWhatsThis(
        """<b>Auto select atoms of deposited object</b>
        <p>
        When depositing atoms, clipboard chunks or library parts,
        their atoms will automatically be selected.""")
    _pd.buildmode_highlighting_checkbox.setWhatsThis(
        """<p>Default setting for <b>Hover highlighting</b> at startup
        (enabled/disabled)</p>""")
    
    _pd.gromacs_label.setWhatsThis(
        """Enable GROMACS and choose the mdrun executable path to use.""")
    _pd.gromacs_checkbox.setWhatsThis(
        """This enables GROMACS as a plug-in. GROMACS is a free rendering
        program available from http://www.gromacs.org/. GROMACS must be
        installed on your computer before you can enable the GROMACS plug-in.
        Check this and choose the the path to the mdrun executable from
        your GROMACS distribution.""")
    _pd.gromacs_path_lineedit.setWhatsThis(
        """The full path to the mdrun executable file for GROMACS.""")
    _pd.gromacs_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the GROMACS executable (mdrun).""")
    _text = \
        """Specify the C-preprocessor (cpp) for GROMACS to use."""
    _pd.cpp_label.setWhatsThis(_text)
    _pd.cpp_checkbox.setWhatsThis(_text)
    _pd.cpp_path_lineedit.setWhatsThis(
        """The full path to the C-preprocessor (cpp) executable file
        for GROMACS to use.""")
    _pd.cpp_choose_btn.setWhatsThis(
        """Allows you to choose the path to the C-preprocessor (cpp)
        executable file for GROMACS to use.""")

    _text = \
        """This enables POV-Ray as a plug-in. POV-Ray is a free raytracing
        program available from http://www.povray.org/. POV-Ray must be
        installed on your computer before you can enable the POV-Ray plug-in.
        """
    _pd.povray_checkbox.setWhatsThis(_text)
    _pd.povray_lbl.setWhatsThis(_text)
    _text = \
        """This enables QuteMolX as a plug-in. QuteMolX is available for
        download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be
        installed on your computer before you can enable this plug-in."""
    _pd.qutemol_lbl.setWhatsThis(_text)
    _pd.qutemol_checkbox.setWhatsThis(_text)

    _text = \
        """This enables Nano-Hive as a plug-in. Nano-Hive is available for
        download from  http://www.nano-hive.com/. Nano-Hive must be installed
        on your computer before you can enable the Nano-Hive plug-in."""
    _pd.nanohive_lbl.setWhatsThis(_text)
    _pd.nanohive_checkbox.setWhatsThis(_text)

    _pd.povray_path_lineedit.setWhatsThis(
        """The full path to the POV-Ray executable file.""")
    _pd.qutemol_path_lineedit.setWhatsThis(
        """The full path to the QuteMolX executable file.""")
    _pd.nanohive_path_lineedit.setWhatsThis(
        """The full path to the Nano-Hive executable file.""")
    _text = \
        """<p>This enables PC-GAMESS (Windows) or GAMESS
        (Linux or MacOS) as a plug-in. </p>
        <p>For Windows users, PC-GAMESS is available for download from
        http://classic.chem.msu.su/gran/gamess/. PC-GAMESS must be installed on
        your computer before you can enable the PC-GAMESS plug-in.</p>
        <p>For Linux and MacOS users, GAMESS is available for download from
        http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed
        on your computer before you can enable the GAMESS plug-in.
        </p>"""
    _pd.gamess_lbl.setWhatsThis(_text)
    _pd.gamess_checkbox.setWhatsThis(_text)
    _pd.megapov_path_lineedit.setWhatsThis(
        """The full path to the MegaPOV executable file (megapov.exe).""")
    _text = \
        """This enables MegaPOV as a plug-in. MegaPOV is a free addon
        raytracing program available from http://megapov.inetart.net/.
        Both MegaPOV and POV-Ray must be installed on your computer before
        you can enable the MegaPOV plug-in. MegaPOV allows rendering to
        happen silently on Windows (i.e. no POV_Ray GUI is displayed while
        rendering)."""
    _pd.megapov_checkbox.setWhatsThis(_text)
    _pd.megapov_lbl.setWhatsThis(_text)
    _pd.gamess_path_lineedit.setWhatsThis(
        """The gamess executable file. Usually it's called gamess.??.x or
        ??gamess.exe.""")
    _pd.povdir_lineedit.setWhatsThis(
        """Specify a directory for where to find POV-Ray or MegaPOV include
        files such as transforms.inc.""")
    _pd.qutemol_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the QuteMolX executable.""")
    _pd.nanohive_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the Nano-Hive executable.""")
    _pd.povray_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the POV-Ray executable.""")
    _pd.megapov_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the MegaPOV executable (megapov.exe).""")
    _pd.gamess_choose_btn.setWhatsThis(
        """This opens up a file chooser dialog so that you can specify the
        location of the GAMESS or PC-GAMESS executable.""")
    _pd.povdir_checkbox.setWhatsThis(
        """Select a user-customized directory for POV-Ray and MegaPOV include
        files, such as transforms.inc.""")
    _pd.undo_automatic_checkpoints_checkbox.setWhatsThis(
        """<p><b>Automatic checkpoints</b></p>
        <p>
        Specifies whether <b>automatic checkpointing</b> is enabled/disabled
        during program startup only. It does not enable/disable
        <b>automatic checkpointing</b> when the program is running.
        <p><b>Automatic checkpointing</b> can be enabled/disabled by the user
        at any time from <b>Edit > Automatic checkpointing</b>. When enabled,
        the program maintains the undo stack automatically.  When disabled,
        the user is required to manually set undo checkpoints using the
        <b>set checkpoint</b> button in the Edit Toolbar/Menu.</p>
        <p><b>Automatic checkpointing</b> can impact program performance. By
        disabling automatic checkpointing, the program will run faster.</p>
        <p><b><i>Remember to you must set your own undo checkpoints manually
        when automatic checkpointing is disabled.</i></b></p>
        <p>""")
    _pd.undo_restore_view_checkbox.setWhatsThis(
        """<p><b>Restore view when undoing structural changes</b></p>
        <p>
        <p>When checked, the current view is stored along with each
        <b><i>structural change</i></b> on the undo stack.  The view is then
        restored when the user undoes a structural change.</p>
        <p><b><i>Structural changes</i></b> include any operation that modifies
        the model. Examples include adding, deleting or moving an atom,
        chunk or jig. </p>
        <p>Selection (picking/unpicking) and view changes are examples of
        operations that do not modify the model
        (i.e. are not structural changes).
        </p>""")
    _pd.groupBox3.setWhatsThis(
        """Format prefix and suffix text the delimits the part name in the
        caption in window border.""")
    _text = \
        """Saves the main window's current position and size for the next
        time the program starts."""
    _pd.save_current_btn.setWhatsThis(_text)     
    _pd.restore_saved_size_btn.setWhatsThis(
        """Restores the main window's current position from the last time
        the program was closed""")
    _text = \
        """Sets background color from preset list or choose to
        customize your own background color"""
    _pd.label_8.setWhatsThis(_text)
    _pd.backgroundColorComboBox.setWhatsThis(_text)
    _pd.hoverHighlightingStyleGroupBox.setWhatsThis(
        """<p><b>Hover highlighting style</b></p>
        <p>
        <p>Creates a highlight surrounding an object that the cursor is
        placed over. The highlight shows what would be selected if the mouse
        was clicked. Has options to view the highlighting in many ways as
        well as choose the color of the highlight.
        </p>""")
    _pd.selectionColorStyleGroupBox.setWhatsThis(
        """<p><b>Selection style</b></p>
        <p>
        <p>When an object or objects have been selected they become
        highlighted. The highlighting has many textures and colors that
        may be changed.
        </p>""")
    _text = \
        """Sets the width of the colored halo if colored halo is chosen
        as a highlighting style or selection style."""
    _pd.label_25.setWhatsThis(_text)
    _pd.haloWidthSpinBox.setWhatsThis(_text)
    _text = \
        """Changes the appearance of any objects in the work place."""
    _pd.label_9.setWhatsThis(_text)
    _pd.globalDisplayStyleStartupComboBox.setWhatsThis(_text)
    return
