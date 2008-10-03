# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_PreferencesDialog.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in the NE1 Preferences dialog only. 

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text 
for widgets in the Main Window.

@version: $Id: WhatsThisText_for_PreferencesDialog.py 13141 2008-06-06 19:06:39Z ninadsathaye $
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

PLUGIN_TEXT = {
    "MegaPOV":
    { 
        "checkbox" : 
        """<p>This enables MegaPOV as a plug-in. MegaPOV is a free addon
        raytracing program available from http://megapov.inetart.net/.
        Both MegaPOV and POV-Ray must be installed on your computer before
        you can enable the MegaPOV plug-in. MegaPOV allows rendering to
        happen silently on Windows (i.e. no POV_Ray GUI is displayed while
        rendering).</p>""", 
        "chooser" : 
        """The full path to the MegaPOV executable file (megapov.exe).""",
        "button" : 
        """Allows you to choose the path to the MegaPOV executable."""
    },    
    "POV include dir":
    { 
        "checkbox" : 
        """<p>Specify a directory for where to find POV-Ray or MegaPOV include
        files such as transforms.inc.</p>""", 
        "chooser" : 
        """<p>Specify a directory for where to find POV-Ray or MegaPOV include
        files such as transforms.inc.</p>""",
        "button" : 
        """Allows you to choose the path to the include directory."""
    },    
    "Rosetta":
    { 
        "checkbox" : 
        """This enables the use of Rosetta as a plug-in.""", 
        "chooser" : 
        """The full path to the Rosetta executable file.""",
        "button" : 
        """Allows you to choose the path to the Rosetta executable."""
    },    
    "Rosetta DB":
    { 
        "checkbox" : 
        """This enables the selection of the path to the Rosetta Database.""", 
        "chooser" : 
        """The full path to the Rosetta Database.""",
        "button" : 
        """Allows you to choose the path to the Rosetta Database."""
    },    
    "QuteMolX" :
    { 
        "checkbox" : 
        """<p>This enables QuteMolX as a plug-in. QuteMolX is available for
        download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be
        installed on your computer before you can enable this plug-in.</p>""", 
        "chooser" : 
        """The full path to the QuteMolX executable.""",
        "button" : 
        """Allows you to choose the path to the QuteMolX executable."""
    },
    "GROMACS" : 
    { 
        "checkbox" : 
        """<p>This enables GROMACS as a plug-in. GROMACS is a free rendering
        program available from http://www.gromacs.org/. GROMACS must be
        installed on your computer before you can enable the GROMACS plug-in.
        Check this and choose the the path to the mdrun executable from
        your GROMACS distribution.</p>""", 
        "chooser" : 
        """The full path to the mdrun executable file for GROMACS.""",
        "button" : 
        """<p>This opens up a file chooser dialog so that you can specify the
        location of the GROMACS executable (mdrun).</p>"""
    },
    "cpp" :
    {
        "checkbox" : 
        """This enables selecting the C-preprocessor that GROMACS will use""", 
        "chooser" : 
        """<p>The full path to the C-preprocessor (cpp) executable file
        for GROMACS to use.</p>""",
        "button" : 
        """<p>Allows you to choose the path to the C-preprocessor (cpp)
        executable file for GROMACS to use.</p>"""
    },
    "POV-Ray" :
    {
        "checkbox" : 
        """<p>This enables POV-Ray as a plug-in. POV-Ray is a free raytracing
        program available from http://www.povray.org/. POV-Ray must be
        installed on your computer before you can enable the POV-Ray plug-in.
        </p>""",
        "chooser" : 
        """The full path to the POV-Ray executable.""",
        "button" : 
        """Allows you to choose the path to the POV-Ray executable."""
    } }


import sys

def whatsThis_PreferencesDialog(preferencesDialog):
    """
    Assigning the I{What's This} text for the Preferences dialog.
    """
    
    _pd = preferencesDialog
    
    setWhatsThis_General(_pd)
    setWhatsThis_Graphics_Area(_pd)
    setWhatsThis_Zoom_Pan_and_Rotate(_pd)
    setWhatsThis_Rulers(_pd)
    setWhatsThis_Atoms(_pd)
    setWhatsThis_Bonds(_pd)
    setWhatsThis_DNA(_pd)
    setWhatsThis_Minor_groove_error_indicator(_pd)
    setWhatsThis_Base_orientation_indicator(_pd)
    setWhatsThis_Adjust(_pd)
    setWhatsThis_Plugins(_pd)
    setWhatsThis_Undo(_pd)
    setWhatsThis_Window(_pd)
    setWhatsThis_Reports(_pd)
    setWhatsThis_Tooltips(_pd)
    return

def setWhatsThis_General(pd):
    if sys.platform == 'darwin':        
        _keyString = "<b>(Cmd + C and Cmd + V)</b> respectively"
    else:
        _keyString = "<b>(Ctrl + C and Ctrl + V)</b> respectively"
    pd.logo_download_RadioButtonList.setWhatsThis(
        """<p><b>Always ask before downloading</b></p>
        <p>
        When sponsor logos have been updated, ask permission to download them.
        </p>
        <p><b>Never ask before downloading</b></p>
        <p>
        When sponsor logos have been updated, download them without asking
        permission to do so.
        </p>
        <p><b>Never download</b></p>
        <p>
        Don't ask permission to download sponsor logos and don't download them.
        </p>""")
    pd.autobondCheckBox.setWhatsThis("""<p>Default setting for <b>Autobonding</b> at startup
        (enabled/disabled)</p>""")
    pd.hoverHighlightCheckBox.setWhatsThis("""<p>Default setting for <b>Hover highlighting</b> at startup
        (enabled/disabled)</p>""")
    pd.waterCheckBox.setWhatsThis("""<p>Default setting for <b>Water (surface)</b> at startup
        (enabled/disabled)</p>""")
    pd.autoSelectAtomsCheckBox.setWhatsThis("""<b>Auto select atoms of deposited object</b>
        <p>
        When depositing atoms, clipboard chunks or library parts,
        their atoms will automatically be selected.""")
    _text = """<b>Offset scale factor for pasting chunks</b>
            <p>When one or more chunks, that are placed as independent nodes in the 
            Model Tree, are copied and then pasted using the modifier 
            keys %s, this scale factor determines the offset of the pasted chunks 
            from the original chunks. Note that if the copied selection includes any 
            DNA objects such as DNA segments, strands etc, the program will use 
            an offset scale that is used for pasting the DNA objects instead of this 
            offset scale) </p>"""%(_keyString)
    pd.pasteOffsetForChunks_doublespinbox.setWhatsThis(_text)
    pd.pasteOffsetForChunks_doublespinbox.labelWidget.setWhatsThis(_text)
    _text = """<b>Offset scale factor for pasting Dna objects</b>
            <p>When one or more DNA objects such as DNA segments, strands etc, are 
            copied and then pasted using the modifier keys %s, this scale factor 
            determines the offset of the pasted DNA objects from the original ones. 
            Note that this also applies to pasting chunks within a group in the Model 
            Tree. </p>"""%(_keyString)
    pd.pasteOffsetForDNA_doublespinbox.setWhatsThis(_text)
    pd.pasteOffsetForDNA_doublespinbox.labelWidget.setWhatsThis(_text)
    return

def setWhatsThis_Graphics_Area(pd):
    pd.globalDisplayStyleStartupComboBox.setWhatsThis(
        """Changes the appearance of any objects in the work place.""")
    pd.display_compass_CheckBox.setWhatsThis("""<p><b>Display compass</b></p>
        <p>
        Shows/Hides the display compass""")
    _text = """Changes the location of the display compass."""
    pd.compass_location_ComboBox.setWhatsThis(_text)
    pd.compass_location_ComboBox.labelWidget.setWhatsThis(_text)
    pd.display_compass_labels_checkbox.setWhatsThis(
        """Shows/Hides the display compass axis labels.""")
    pd.display_origin_axis_checkbox.setWhatsThis("""<p><b>Display origin axis</b></p>
        <p>
        Shows/Hides the origin axis""")
    pd.display_pov_axis_checkbox.setWhatsThis("""<p><b>Display point of view axis</b></p>
        <p>
        Shows/Hides the point of view axis""")
    pd.cursor_text_font_size_SpinBox.setWhatsThis("""Sets the font size for the standard cursor text.""")
    pd.cursor_text_reset_Button.setWhatsThis(
        """Resets the cursor text font size to the default value.""")
    _text = """Sets the color of the cursor text."""
    pd.cursor_text_color_ComboBox.setWhatsThis(_text)
    pd.cursor_text_color_ComboBox.labelWidget.setWhatsThis(_text)
    pd.display_confirmation_corner_CheckBox.setWhatsThis(
        """Enables/Disables the display of the "Confirmation Corner" within the
        draw window""")
    pd.anti_aliasing_CheckBox.setWhatsThis(
        """Enables/Disables anti-aliased text.  <p>This will not be in effect 
        until the next session.</p>""")
    return

def setWhatsThis_Zoom_Pan_and_Rotate(pd):
    pd.animate_views_CheckBox.setWhatsThis("""<p><b>Animate between views</b></p>
        <p>
        Enables/disables animation when switching between the current view
        and a new view.
        </p>""")
    pd.view_animation_speed_Slider.setWhatsThis("""<p><b>View animation speed</b></p>
        <p>
        Sets the animation speed when animating between views 
        (i.e. Front view to Right view).  It is recommended that this be set 
        to Fast when working on large models.
        </p>""")
    pd.view_animation_speed_reset_ToolButton.setWhatsThis(
        """Resets the animation speed to the default value.""")
    pd.mouse_rotation_speed_Slider.setWhatsThis("""<p><b>Mouse rotation speed</b></p>
        <p>
        Specifies the speed factor to use when rotating the view by dragging
        the mouse (i.e. during the <b>Rotate</b> command or when using the
        middle mouse button).
        </p>""")
    pd.mouse_rotation_speed_reset_ToolButton.setWhatsThis(
        """Resets the mouse rotation speed to the default value.""")
    _text = """Sets the zoom direction for the mouse scroll wheel"""
    pd.zoom_directon_ComboBox.setWhatsThis(_text)
    pd.zoom_directon_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """Sets where the image centers on when zooming in."""
    pd.zoom_in_center_ComboBox.setWhatsThis(_text)
    pd.zoom_in_center_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """Sets where the image centers on when zooming out."""
    pd.zoom_out_center_ComboBox.setWhatsThis(_text)
    pd.zoom_out_center_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """<p>Sets the length of time that the mouse will "hover" over an
        object before highlighting it.</p>"""
    pd.hover_highlighting_timeout_SpinBox.setWhatsThis(_text)
    pd.hover_highlighting_timeout_SpinBox.labelWidget.setWhatsThis(_text)
    return

def setWhatsThis_Rulers(pd):
    _text = """This determines which rulers to display"""
    pd.display_rulers_ComboBox.setWhatsThis(_text)
    pd.display_rulers_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """<p>This determines which corner of the draw area the rulers will
        use as their origin.</p>"""
    pd.origin_rulers_ComboBox.setWhatsThis(_text)
    pd.origin_rulers_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """Determines the background color or the displayed rulers."""
    pd.ruler_color_ColorComboBox.setWhatsThis(_text)
    pd.ruler_color_ColorComboBox.labelWidget.setWhatsThis(_text)
    _text = """Determines how opaque the rulers will look."""
    pd.ruler_opacity_SpinBox.setWhatsThis(_text)
    pd.ruler_opacity_SpinBox.labelWidget.setWhatsThis(_text)
    pd.show_rulers_in_perspective_view_CheckBox.setWhatsThis(
        """Enables/Disables the rulers when using the perspective view.""")
    return

def setWhatsThis_Atoms(pd):
    pd.change_element_colors_PushButton.setWhatsThis(
        """<p>This brings up another dialog which allows the user to change the 
        colors that each of the avaliable atoms is drawn in.</p>""")
    #_text = """Sets the color used when highlighting atoms."""
    #pd.atom_highlighting_ColorComboBox.setWhatsThis(_text)
    #pd.atom_highlighting_ColorComboBox.labelWidget.setWhatsThis(_text)
    #_text = """Sets the color used when hightlighting bondpoints."""
    #pd.bondpoint_highlighting_ColorComboBox.setWhatsThis(_text)
    #pd.bondpoint_highlighting_ColorComboBox.labelWidget.setWhatsThis(_text)
    #_text = """Sets the color used when highlighting bondpoint highlights"""
    #pd.bondpoint_hotspots_ColorComboBox.setWhatsThis(_text)
    #pd.bondpoint_hotspots_ColorComboBox.labelWidget.setWhatsThis(_text)
    pd.restore_element_colors_PushButton.setWhatsThis(
        """<p>Restores the atom and bondpoint hightlighting colors to their 
        default colors.</p>""")
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
    pd.atoms_detail_level_ComboBox.setWhatsThis(_text)
    pd.atoms_detail_level_ComboBox.labelWidget.setWhatsThis(_text)
    _text = """<p><b>Ball and stick atom scale</b></p>
        <p>
        Sets the ball and stick atom scale factor. It is best to
        change the scale factor while the current model is displayed
        in ball and stick mode."""
    pd.ball_and_stick_atom_scale_SpinBox.setWhatsThis(_text)
    pd.ball_and_stick_atom_scale_reset_ToolButton.setWhatsThis(
        """<p>Sets the ball and stick atom scale factor back to its default 
        value</p>""")
    pd.CPK_atom_scale_doubleSpinBox.setWhatsThis(
        """<p><b>CPK atom scale</b></p>
        <p>
        Changes the CPK atom scale factor. It is best to change the scale
        factor while in CPK display mode so you can see the graphical effect of
        changing the scale.""")
    pd.CPK_atom_scale_reset_ToolButton.setWhatsThis(
        """<p>Sets the CPK atom scale factor back to its default 
        value</p>""")
    #pd.overlapping_atom_indicators_CheckBox.setWhatsThis(""" """)
    #pd.force_to_keep_bonds_during_transmute_CheckBox.setWhatsThis(""" """)
    return

def setWhatsThis_Bonds(pd):
    #pd.bond_highlighting_ColorComboBox.setWhatsThis(""" """)
    #pd.ball_and_stick_cylinder_ColorComboBox.setWhatsThis(""" """)
    #pd.bond_stretch_ColorComboBox.setWhatsThis(""" """)
    #pd.vane_ribbon_ColorComboBox.setWhatsThis(""" """)
    pd.restore_bond_colors_PushButton.setWhatsThis(
        """<p>Restores the colors used for bond functions to their default
        values.</p>""")
    _text = \
        """<p><b>Ball and stick bond scale</b></p>
        <p>
        Set scale (size) factor for the cylinder representing bonds
        in ball and stick display mode"""
    pd.ball_and_stick_bond_scale_SpinBox.setWhatsThis(_text)
    pd.ball_and_stick_bond_scale_SpinBox.labelWidget.setWhatsThis(_text)
    _text = \
        "<b>Bond line thickness</b>"\
        "<p>"\
        "Sets the line thickness to <i>n</i> pixels wheneven bonds "\
        "are rendered as lines (i.e. when the global display style is set to "\
        "<b>Lines</b> display style)."\
        "</p>"
    pd.bond_line_thickness_SpinBox.setWhatsThis(_text)
    pd.bond_line_thickness_SpinBox.labelWidget.setWhatsThis(_text)
    _text = """<p><b>Multiple cylinders</b></p>
        <p>
        <p><b>High order bonds</b>
        are displayed using <b>multiple cylinders.</b></p>
        <p>
        <b>Double bonds</b> are drawn with two cylinders.<br>
        <b>Triple bonds</b> are drawn with three cylinders.<br>
        <b>Aromatic bonds</b> are drawn as a single cylinder with a
        short green cylinder in the middle.
        <p><b>Vanes</b></p>
        <p>
        <p><i>High order bonds</i> are displayed using <b>Vanes.</b></p>
        <p>
        <p>Vanes represent <i>pi systems</i> in high order bonds and are
        rendered as rectangular polygons. The orientation of the vanes
        approximates the orientation of the pi system(s).</p>
        <p>Create an acetylene or ethene molecule and select this option
        to see how vanes are rendered.
        </p>
        <p><b>Ribbons</b></p>
        <p>
        <p><i>High order bonds</i> are displayed using <b>Ribbons.</b></p>
        <p>
        <p>Ribbons represent <i>pi systems</i> in high order bonds and are
        rendered as ribbons. The orientation of the ribbons approximates the
        orientation of the pi system.</p>
        <p>Create an acetylene or ethene molecule and select this option
        to see how ribbons are rendered.
        </p>"""
    pd.high_order_bonds_RadioButtonList.setWhatsThis(_text)
    pd.show_bond_type_letters_CheckBox.setWhatsThis(
        """<p><b>Show bond type letters</b></p>
        <p>
        <p>Shows/Hides bond type letters (labels) on top of bonds.</p>
        <u>Bond type letters:</u><br>
        <b>2</b> = Double bond<br>
        <b>3</b> = Triple bond<br>
        <b>A</b> = Aromatic bond<br>
        <b>G</b> = Graphitic bond<br>""")
    pd.show_valence_errors_CheckBox.setWhatsThis(
        """<p><b>Show valence errors</b></p>
        <p>
        Enables/Disables valence error checker.</p>
        When enabled, atoms with valence errors are displayed with a pink
        wireframe sphere. This indicates that one or more of the atom's bonds
        are not of the correct order (type), or that the atom has the wrong
        number of bonds, or (for PAM DNA pseudoatoms) that there is some error
        in bond directions or in which PAM elements are bonded. The error
        details can be seen in the tooltip for the atom.""")
    pd.show_bond_stretch_indicators_CheckBox.setWhatsThis(
        """Enables/Disables the display of bond stretch indicators""")
    return

def setWhatsThis_DNA(pd):
    pd.conformation_ComboBox.setWhatsThis(""" """)
    pd.bases_per_turn_DoubleSpinBox.setWhatsThis(""" """)
    pd.rise_DoubleSpinBox.setWhatsThis(""" """)
    pd.strand1_ColorComboBox.setWhatsThis(""" """)
    pd.strand2_ColorComboBox.setWhatsThis(""" """)
    pd.segment_ColorComboBox.setWhatsThis(""" """)
    pd.restore_DNA_colors_PushButton.setWhatsThis(""" """)
    pd.show_arrows_on_backbones_CheckBox.setWhatsThis(""" """)
    pd.show_arrows_on_3prime_ends_CheckBox.setWhatsThis(""" """)
    pd.show_arrows_on_5prime_ends_CheckBox.setWhatsThis(""" """)
    pd.three_prime_end_custom_ColorComboBox.setWhatsThis(""" """)
    pd.five_prime_end_custom_ColorComboBox.setWhatsThis(""" """)
    return

def setWhatsThis_Minor_groove_error_indicator(pd):
    pd.minor_groove_error_indicatiors_CheckBox.setWhatsThis(""" """)
    pd.minor_groove_error_minimum_angle_SpinBox.setWhatsThis(""" """)
    pd.minor_groove_error_maximum_angle_SpinBox.setWhatsThis(""" """)
    pd.minor_groove_error_color_ColorComboBox.setWhatsThis(""" """)
    pd.minor_groove_error_reset_PushButton.setWhatsThis(""" """)
    return

def setWhatsThis_Base_orientation_indicator(pd):
    pd.base_orientation_indicatiors_CheckBox.setWhatsThis(""" """)
    pd.plane_normal_ComboBox.setWhatsThis(""" """)
    pd.indicators_color_ColorComboBox.setWhatsThis(""" """)
    pd.inverse_indicators_color_ColorComboBox.setWhatsThis(""" """)
    pd.enable_inverse_indicatiors_CheckBox.setWhatsThis(""" """)
    pd.angle_threshold_DoubleSpinBox.setWhatsThis(""" """)
    pd.terminal_base_distance_SpinBox.setWhatsThis(""" """)
    return

def setWhatsThis_Adjust(pd):
    pd.physics_engine_choice_ComboBox.setWhatsThis(""" """)
    pd.enable_electrostatics_CheckBox.setWhatsThis(""" """)
    pd.watch_motion_in_realtime_CheckBox.setWhatsThis(""" """)
    pd.constant_animation_update_RadioButton.setWhatsThis(""" """)
    pd.update_every_RadioButton.setWhatsThis(""" """)
    pd.update_rate_SpinBox.setWhatsThis(""" """)
    pd.animation_detail_level_ComboBox.setWhatsThis(""" """)
    pd.endRMS_DoubleSpinBox.setWhatsThis(""" """)
    pd.endmax_DoubleSpinBox.setWhatsThis(""" """)
    pd.cutoverRMS_DoubleSpinBox.setWhatsThis(""" """)
    pd.cutoverMax_DoubleSpinBox.setWhatsThis(""" """)
    return

def setWhatsThis_Plugins(pd):
    for plugin in PLUGIN_TEXT: 
        pd.checkboxes[plugin].setWhatsThis(PLUGIN_TEXT[plugin]["checkbox"])
        pd.choosers[plugin].lineEdit.setWhatsThis(
            PLUGIN_TEXT[plugin]["chooser"])
        pd.choosers[plugin].browseButton.setWhatsThis(
            PLUGIN_TEXT[plugin]["button"])
    return
    
def setWhatsThis_Undo(pd):
    pd.undo_restore_view_CheckBox.setWhatsThis(""" """)
    pd.undo_automatic_checkpoints_CheckBox.setWhatsThis(""" """)
    pd.undo_stack_memory_limit_SpinBox.setWhatsThis(""" """)
    return

def setWhatsThis_Window(pd):
    pd.current_width_SpinBox.setWhatsThis(""" """)
    pd.current_height_SpinBox.setWhatsThis(""" """)
    pd.current_size_save_Button.setWhatsThis(""" """)
    pd.restore_saved_size_Button.setWhatsThis(""" """)
    pd.saved_size_label.setWhatsThis(""" """)
    pd.save_size_on_quit_CheckBox.setWhatsThis(""" """)
    pd.caption_prefix_LineEdit.setWhatsThis(""" """)
    pd.caption_suffix_LineEdit.setWhatsThis(""" """)
    pd.caption_prefix_save_ToolButton.setWhatsThis(""" """)
    pd.caption_suffix_save_ToolButton.setWhatsThis(""" """)
    pd.display_full_path_CheckBox.setWhatsThis(""" """)
    pd.use_custom_font_CheckBox.setWhatsThis(""" """)
    pd.custom_fontComboBox.setWhatsThis(""" """)
    pd.custom_font_size_SpinBox.setWhatsThis(""" """)
    pd.make_default_font_PushButton.setWhatsThis(""" """)
    return

def setWhatsThis_Reports(pd):
    pd.history_include_message_serial_CheckBox.setWhatsThis(""" """)
    pd.history_include_message_timestamp_CheckBox.setWhatsThis(""" """)
    return

def setWhatsThis_Tooltips(pd):
    pd.atom_chunk_information_CheckBox.setWhatsThis(""" """)
    pd.atom_mass_information_CheckBox.setWhatsThis(""" """)
    pd.atom_XYZ_coordinates_CheckBox.setWhatsThis(""" """)
    pd.atom_XYZ_distance_CheckBox.setWhatsThis(""" """)
    pd.atom_include_vdw_CheckBox.setWhatsThis(""" """)
    pd.atom_distance_precision_SpinBox.setWhatsThis(""" """)
    pd.atom_angle_precision_SpinBox.setWhatsThis(""" """)
    pd.bond_distance_between_atoms_CheckBox.setWhatsThis(""" """)
    pd.bond_chunk_information_CheckBox.setWhatsThis(""" """)
    return
