# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_PreferencesDialog.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in the NE1 Preferences dialog only. 

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text 
for widgets in the Main Window.

@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

def whatsThis_PreferencesDialog(preferencesDialog):
    """
    Assigning the I{What's This} text for the Preferences dialog.
    """
    
    _pd = preferencesDialog
    
    # Bond line thickness

    _text = \
        "<b>Bond line thickness</b>"\
        "<p>"\
        "Sets the line thickness to <i>n</i> pixels wheneven bonds "\
        "are rendered as lines (i.e. when the Global Display Style is set to "\
        "<b>Lines</b> display style)."\
        "</p>"

    _pd.bond_line_thickness_spinbox.setWhatsThis(_text) # nice!
    
    # and What's This text for all the others widgets (yuk!)
    
    _pd.display_origin_axis_checkbox.setWhatsThis("""<p><b>Display Origin Axis</b></p><p>Shows/Hides the Origin Axis""")
    _pd.display_pov_axis_checkbox.setWhatsThis("""<p><b>Display Point of View Axis</b></p><p>Shows/Hides the Point
                                            of View Axis""")
    _pd.compassGroupBox.setWhatsThis("""<p><b>Display Compass</b></p><p>Shows/Hides the Display Compass""")
    _pd.display_compass_labels_checkbox.setWhatsThis("""<p><b>Display Compass</b></p><p>Shows/Hides the Display Compass""")
    _pd.update_btngrp.setWhatsThis("""<p><b>Watch motion in real time</b>
    </p>Enables/disables realtime graphical updates during adjust operations
    when using <b>Adjust All</b> or <b>Adjust Selection</b>""")
    _pd.update_number_spinbox.setWhatsThis("""<b>Update every <i>n units.</u></b>
    <p>Specify how often to update
    the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
    _pd.update_units_combobox.setWhatsThis("""<b>Update every <i>n units.</u></b>
                                            <p>Specify how often to update
                                            the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
    _pd.update_every_rbtn.setWhatsThis("""<b>Update every <i>n units.</u></b>
    <p>Specify how often to update
    the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
    _pd.update_asap_rbtn.setWhatsThis("""<b>Update as fast as possible</b>
    <p>Update every 2 seconds, or faster (up to 20x/sec) if it doesn't slow adjustments by more than 20%</p>""")
    _pd.endrms_lbl.setWhatsThis("""<b>EndRMS</b>
                             <p>Continue until this RMS force is reached.</p>""")
    _pd.endmax_lbl.setWhatsThis("""<b>EndMax</b>
                             <p>Continue until no interaction exceeds this force.</p>""")
    _pd.endMaxDoubleSpinBox.setWhatsThis("""<b>EndMax</b>
                                 <p>Continue until no interaction exceeds this force.</p>""")
    _pd.endRmsDoubleSpinBox.setWhatsThis("""<b>EndRMS</b>
                                 <p>Continue until this RMS force is reached.</p>""")
    _pd.cutovermax_lbl.setWhatsThis("""<b>CutoverMax</b>
                                     <p>Use steepest descent until no interaction
                                     exceeds this force.</p>""")
    _pd.cutoverMaxDoubleSpinBox.setWhatsThis("""<b>CutoverMax</b>
                                         <p>Use steepest descent until no interaction
                                         exceeds this force.</p>""")
    _pd.cutoverRmsDoubleSpinBox.setWhatsThis("""<b>CutoverRMS</b>
                                         <p>Use steepest descent until this RMS force
                                         is reached.</p>""")
    _pd.cutoverrms_lbl.setWhatsThis("""<b>CutoverRMS</b>
                                         <p>Use steepest descent until this RMS force
                                         is reached.</p>""")
    # Sponsor Logos Download Permission
    _pd.sponsorLogosGroupBox.setWhatsThis("""<b>Sponsor Logos Download Permission</b>
                                           <p>This group of buttons sets the permission for downloading sponsor 
                                           logos.</p>""")
    _pd.logoAlwaysAskRadioBtn.setWhatsThis("""<b>Always ask before downloading</b>
                                            <p>When sponsor logos have been updated, ask permission to download 
                                            them.</p>""")
    _pd.logoNeverAskRadioBtn.setWhatsThis("""<b>Never ask before downloading</b>
                                           <p>When sponsor logos have been updated, download them without asking
                                           permission to do so.</p>""")
    _pd.logoNeverDownLoadRadioBtn.setWhatsThis("""<b>Never download</b>
                                                <p>Don't ask permission to download sponsor logos and don't download 
                                                them.</p>""")

    _pd.animate_views_checkbox.setWhatsThis("""<p><b>Animate Between Views</b></p><p>Enables/disables animation
                                         when switching between the current view and a new view.</p>""")
    _pd.animation_speed_slider.setWhatsThis("""<p><b>View Animation Speed</b></p><p>Sets the animation speed when
                                             animating between view (i.e. Front View to Right View).  It is recommended that this be set to Fast when working on large
                                             models.</p>""")
    _pd.textLabel1_7.setWhatsThis("""<p><b>Level of Detail</b></p><p>Sets the <b>Level of Detail</b>
                                   for atoms and bonds.<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics
                                   quality<br> <b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between
                                   High, Medium and Low based on the model size (number of atoms).</p>""")
    _pd.level_of_detail_combox.setWhatsThis("""<p><b>Level of Detail</b></p><p>Sets the graphics quality for atoms
                                             (and bonds)<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics quality<br>
                                             <b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between High, Medium
                                             and Low based on the number of atoms in the current part.""")
    _pd.textLabel1_3_2.setWhatsThis("""<p><b>Ball and Stick Atom Scale</b></p><p>Sets the Ball and Stick
                                 Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
    _pd.cpk_atom_rad_spinbox.setWhatsThis("""<p><b>Ball and Stick Atom Scale</b></p><p>Sets the Ball and Stick
                                       Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
    _pd.textLabel1_3_2_2.setWhatsThis("""<p><b>CPK Atom Scale</b></p><p>Changes the CPK Atom Scale factor.
                                   It is best to change the scale factor while in CPK display mode so you can see the graphical effect of changing the scale.""")
    _pd.cpk_scale_factor_linedit.setWhatsThis("""Displays the value of the CPK Atom Scale""")
    _pd.cpk_scale_factor_slider.setWhatsThis("""<p><b>CPK Atom Scale</b></p><p>Slider control for chaning the CPK
                                              Atom Scale factor. It is best to change the scale factor while in CPK display mode so you can see the graphical effect of
                                              changing the scale.""")
    _pd.reset_cpk_scale_factor_btn.setWhatsThis("""Restore the default value of the CPK Scale Factor""")
    _pd.multCyl_radioButton.setWhatsThis("""<p><b>Multiple Cylinders</b></p><p>
                                          <p><b>High Order Bonds</b> are
                                          displayed using <b>Multiple Cylinders.</b></p><p>
                                          <b>Double bonds</b> are drawn with two cylinders.<br>
                                          <b>Triple bonds</b>
                                          are drawn with three cylinders.<br>
                                          <b>Aromatic bonds</b> are drawn as a single cylinder with a short green cylinder in the
                                          middle.""")
    _pd.vanes_radioButton.setWhatsThis("""<p><b>Vanes</b></p><p>
                                        <p><i>High Order Bonds</i> are displayed
                                        using <b>Vanes.</b></p><p>
                                        <p>Vanes represent <i>pi systems</i> in high order bonds and are rendered as rectangular polygons.
                                        The orientation of the vanes approximates the orientation of the pi system(s).</p>
                                        <p>Create an acetylene or ethene molecule
                                        and select this option to see how vanes are rendered.</p>""")
    _pd.ribbons_radioButton.setWhatsThis("""<p><b>Ribbons</b></p><p>
                                          <p><i>High Order Bonds</i> are displayed
                                          using <b>Ribbons.</b></p><p>
                                          <p>Ribbons represent <i>pi systems</i> in high order bonds and are rendered as ribbons. The orientation of the ribbons approximates the orientation of the pi system.</p>
                                          <p>Create an acetylene or ethene molecule and select this option to see how ribbons are rendered.</p>""")
    _pd.show_bond_labels_checkbox.setWhatsThis("""<p><b>Show Bond Type Letters</b></p><p>
                                                <p>Shows/Hides Bond Type
                                                letters (labels) on top of bonds.</p>
                                                <u>Bond Type Letters:</u><br>
                                                <b>2</b> = Double bond<br>
                                                <b>3</b> = Triple bond<br>
                                                <b>A</b>
                                                = Aromatic bond<br>
                                                <b>G</b> = Graphitic bond<br>""")
    _pd.show_valence_errors_checkbox.setWhatsThis("""<p><b>Show Valence Errors</b></p><p>Enables/Disables Valence
                                                   Error Checker.</p>When enabled, atoms with valence errors are displayed with a pink wireframe sphere. This indicates
                                                   that one or more of the atom's bonds are not of the correct order (type), or that the atom has the wrong number of bonds,
                                                   or (for PAM DNA pseudoatoms) that there is some error in bond directions or in which PAM elements are bonded. The error details can be seen in the tooltip for the atom.""")
    _pd.textLabel1_3.setWhatsThis("""<p><b>Ball and Stick Bond Scale</b></p><p>Set scale (size) factor for the cylinder representing bonds in Ball and Stick display mode""")
    _pd.cpk_cylinder_rad_spinbox.setWhatsThis("""<p><b>Ball and Stick Bond Scale</b></p><p>Set scale (size) factor
                                           for the cylinder representing bonds in Ball and Stick display mode""")
    
    _pd.autobond_checkbox.setWhatsThis("""Build mode's default setting for Autobonding at startup (enabled/disabled)""")
    _pd.water_checkbox.setWhatsThis("""Build mode's default setting for Water at startup (enabled/disabled)""")
    _pd.buildmode_select_atoms_checkbox.setWhatsThis("""<p><b>Select Atoms of Deposited Object</b></p><p>
                                                  When depositing atoms, clipboard chunks or library parts, their atoms will automatically be selected.""")
    _pd.buildmode_highlighting_checkbox.setWhatsThis("""Build mode's default setting for Highlighting at startup (enabled/disabled)""")

    _pd.gromacs_label.setWhatsThis("""Enable GROMACS and choose the mdrun executable path to use.""")
    _pd.gromacs_checkbox.setWhatsThis("""This enables GROMACS as a plug-in. GROMACS is a free rendering program available from http://www.gromacs.org/. GROMACS must be installed on your computer before you can enable the GROMACS plug-in.  Check this and choose the the path to the mdrun executable from your GROMACS distribution.""")
    _pd.gromacs_path_lineedit.setWhatsThis("""The full path to the mdrun executable file for GROMACS.""")
    _pd.gromacs_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                     location of the GROMACS executable (mdrun).""")

    _pd.cpp_label.setWhatsThis("""Specify the C-preprocessor (cpp) for GROMACS to use.""")
    _pd.cpp_checkbox.setWhatsThis("""Specify the C-preprocessor (cpp) for GROMACS to use.""")
    _pd.cpp_path_lineedit.setWhatsThis("""The full path to the C-preprocessor (cpp) executable file for GROMACS to use.""")
    _pd.cpp_choose_btn.setWhatsThis("""Allows you to choose the path to the C-preprocessor (cpp) executable file for GROMACS to use.""")

    _pd.povray_checkbox.setWhatsThis("""This enables POV-Ray as a plug-in. POV-Ray is a free raytracing program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray plug-in.""")
    _pd.povray_lbl.setWhatsThis("""This enables POV-Ray as a plug-in. POV-Ray is a free raytracing program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray plug-in.""")

    _pd.qutemol_lbl.setWhatsThis("""This enables QuteMolX as a plug-in. QuteMolX is available for download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be installed on your computer before you can enable this plug-in.""")
    _pd.qutemol_checkbox.setWhatsThis("""This enables QuteMolX as a plug-in. QuteMolX is available for download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be installed on your computer before you can enable the this plug-in.""")

    _pd.nanohive_lbl.setWhatsThis("""This enables Nano-Hive as a plug-in. Nano-Hive is available for download from  http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive plug-in.""")
    _pd.nanohive_checkbox.setWhatsThis("""This enables Nano-Hive as a plug-in. Nano-Hive is available for download from http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive plug-in.""")

    _pd.povray_path_lineedit.setWhatsThis("""The full path to the POV-Ray executable file.""")
    _pd.qutemol_path_lineedit.setWhatsThis("""The full path to the QuteMolX executable file.""")
    _pd.nanohive_path_lineedit.setWhatsThis("""The full path to the Nano-Hive executable file.""")
    _pd.gamess_lbl.setWhatsThis("""<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS) as a plug-in. </p>
                                 <p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
                                 PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
                                 <p>For Linux and MacOS users,
                                 GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer before you can enable the GAMESS plug-in.</p>""")
    _pd.megapov_path_lineedit.setWhatsThis("""The full path to the MegaPOV executable file (megapov.exe).""")
    _pd.megapov_checkbox.setWhatsThis("""This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed while rendering).""")
    _pd.gamess_path_lineedit.setWhatsThis("""The gamess executable file. Usually it's called gamess.??.x or
                                       ??gamess.exe.""")
    _pd.gamess_checkbox.setWhatsThis("""<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS)
                                      as a plug-in. </p>
                                      <p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
                                      PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
                                      <p>For Linux and MacOS users,
                                      GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer before you can enable the GAMESS plug-in.</p>""")
    _pd.povdir_lineedit.setWhatsThis("""Specify a directory for where to find POV-Ray or MegaPOV include
                                  files such as transforms.inc.""")


    _pd.qutemol_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                     location of the QuteMolX executable.""")
    _pd.nanohive_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                      location of the Nano-Hive executable.""")
    _pd.povray_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                    location of the POV-Ray executable.""")
    _pd.megapov_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                     location of the MegaPOV executable (megapov.exe).""")
    _pd.gamess_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                    location of the GAMESS or PC-GAMESS executable.""")
    _pd.megapov_lbl.setWhatsThis("""This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed while rendering).""")
    _pd.povdir_checkbox.setWhatsThis("""Select a user-customized directory for POV-Ray and MegaPOV include files, such as transforms.inc.""")
    _pd.undo_automatic_checkpoints_checkbox.setWhatsThis("""<p><b>Automatic Checkpoints</b></p><p>Specifies whether <b>Automatic
                                                          Checkpointing</b> is enabled/disabled during program startup only.  It does not enable/disable <b>Automatic Checkpointing</b>
                                                          when the program is running.
                                                          <p><b>Automatic Checkpointing</b> can be enabled/disabled by the user at any time from <b>Edit > Automatic Checkpointing</b>. When enabled, the program maintains the Undo stack automatically.  When disabled, the user is required to manually set Undo checkpoints using the <b>Set Checkpoint</b> button in the Edit Toolbar/Menu.</p>
                                                          <p><b>Automatic Checkpointing</b> can impact program performance. By disabling Automatic Checkpointing, the program will run faster.</p><p><b><i>Remember to you must set your own Undo checkpoints manually when Automatic Checkpointing is disabled.</i></b></p><p>""")
    _pd.undo_restore_view_checkbox.setWhatsThis("""<p><b>Restore View when Undoing Structural Changes</b></p><p>
                                                 <p>When checked, the current view is stored along with each <b><i>structural change</i></b> on the undo stack.  The view is then
                                                 restored when the user undoes a structural change.</p>
                                                 <p><b><i>Structural changes</i></b> include any operation that modifies the model. Examples include adding, deleting or moving an atom, chunk or jig. </p>
                                                 <p>Selection (picking/unpicking) and view changes are examples of operations that do not modify the model (i.e. are not structural changes).</p>""")
    _pd.groupBox3.setWhatsThis("""Format Prefix and Suffix text the delimits the part name in the caption in window border.""")
    _pd.save_current_btn.setWhatsThis("""Saves the main window's current position and size for the next time the program starts.""")
    _pd.restore_saved_size_btn.setWhatsThis("""Saves the main window's current position and size for the next time the program starts.""")
    return
