# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_PropertyManagers.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in all NE1 Property Managers only. 

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text 
for widgets in the Main Window.

@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

"""

def whatsThis_DnaDuplexPropertyManager(propMgr):
    """
    Whats This text for the DnaDuplex Property Manager
    @see: B{DnaDuplexPropertyManager._addWhatsThisText}
    """
    
    propMgr.conformationComboBox.setWhatsThis(
        """<b>Conformation</b>
        <p>
        DNA exists in several possible conformations, with
        A-DNA, B-DNA, and Z-DNA being the most common.</p> 
        <p>
        Only B-DNA is currently supported in NanoEngineer-1.
        </p>""")
    
    propMgr.dnaModelComboBox.setWhatsThis(
        """<b>Model Choice</b>
        <p>
        Selects between the model types supported by NanoEngineer-1: PAM3,
        PAM5, and atomistic representations of DNA.
        </p>""")
    
    propMgr.numberOfBasePairsSpinBox.setWhatsThis(
        """<b>Base Pairs</b>
        <p>
        Allows the user to create a duplex by specifying the number 
        of base pairs
        </p>""")
    
    propMgr.basesPerTurnDoubleSpinBox.setWhatsThis(
        """<b>Bases Per Turn</b>
        <p>
        Allows the user to specifying the number of base pairs between one full 
        turn of the DNA helix
        </p>""")
    
    propMgr.duplexLengthLineEdit.setWhatsThis(
        """<b>Duplex Length</b>
        <p>
        Displays the length of the DNA duplex in angstroms
        </p>""")
    
    propMgr.dnaRubberBandLineDisplayComboBox.setWhatsThis(
        """<b>Display As</b>
        <p>
        Selects between Ribbon and Ladder display styles
        </p>""")
    
    propMgr.lineSnapCheckBox.setWhatsThis(
     """<b>Enable Line Snap</b>
        <p>
        When checked a duplex will be constrained to a grid
        </p>""")
    
    return # End of whatsThis_DnaDuplexPropertyManager

def whatsThis_MakeCrossoversPropertyManager(propMgr):
    """
    Whats This text for the DnaDuplex Property Manager
    @see: B{MakeCrossovers_PropertyManager._addWhatsThisText}
    """
    propMgr.segmentListWidget.setWhatsThis("""<b> List of Dna segments for 
    crossover search</b>
    <p>Lists DnaSegments that will be searched for potential crossover sites. 
    To add/remove Dna segments to/from this list, activate the appropriate tool
    in this property manager and select the whole axis of the Dna segment.
    To add/remove multiple segments to the list at once, hold down left mouse 
    button and drag it to draw a selection rectangle around the segments. 
    </p>
    """)
    propMgr.crossoversBetGivenSegmentsOnly_checkBox.setWhatsThis("""
    <b> Between above segments only Checkbox </b>
    <p>*If checked, program will search for the crossover sites <b>only 
     between</b> the DNA segments listed in the segment's list. <br><br>
    *Unchecking this checkbox will make the program search for the crossover 
     sites between each DNA segment in the segment's list and <b>all</b>
     the DNA segments in the model, that are within a certain distance from 
     that particular DNA segment. 
    <br><br><b>Note</b>This operation could be time consuming so it is 
    recommended that user keeps this checkbox checked.</p>""")
    return # End of whatsThis_whatsThis_MakeCrossoversPropertyManager
    

def whatsThis_PeptideGeneratorPropertyManager(propMgr):
    """
    "Whats This" text for widgets in the Peptide Generator Property Manager.
    """
    
    propMgr.aaTypeComboBox.setWhatsThis(
        """<b>Chain Confirmation</b>
        <p>
        Lists the available confirmations for the polypeptide chain
        </p>""")
    
    propMgr.startOverButton.setWhatsThis(
        """<b>Start Over</b>
        <p>
        Deletes the current sequence from the sequence editor
        </p>""")
    
    propMgr.sequenceEditor.setWhatsThis(
        """<b>Sequence Editor</b>
        <p>
        Displays the current amino acid sequence 
        </p>""")
    return

def whatsThis_PeptideGeneratorPropertyManager(propMgr):
    """
    "Whats This" text for widgets in the Peptide Generator Property Manager.
    """
    propMgr.aaTypeComboBox.setWhatsThis(
        """<b>Chain Confirmation</b>
        <p>
        Lists the available confirmations for the polypeptide chain
        </p>""")

    propMgr.startOverButton.setWhatsThis(
        """<b>Start Over</b>
        <p>
        Deletes the current sequence from the sequence editor
        </p>""")

    propMgr.phiAngleField.setWhatsThis(
        """<b>Phi angle</b>
        <p>
        Sets a Phi dihedral backbone angle of the polypeptide chain  
        </p>""")

    propMgr.psiAngleField.setWhatsThis(
        """<b>Psi angle</b>
        <p>
        Sets a Psi dihedral backbone angle of the polypeptide chain  
        </p>""")

    propMgr.invertChiralityPushButton.setWhatsThis(
        """<b>Invert chirality</b>
        <p>
        Inverts a chirality of the polypeptide backbone   
        </p>""")

    propMgr.aaTypesButtonGroup.setWhatsThis(
        """<b>Amino acids</b>
        <p>
        Adds an amino acid to the constructed peptide   
        </p>""")

    propMgr.sequenceEditor.setWhatsThis(
        """<b>Sequence Editor</b>
        <p>
        Displays the current amino acid sequence 
        </p>""")

    return # End of whatsThis_PeptideGeneratorPropertyManager

def whatsThis_NanotubeGeneratorPropertyManager(propMgr):
    """
    "Whats This" text for widgets in the Nanotube Property Manager.
    """
        
    propMgr.chiralityNSpinBox.setWhatsThis(
        """<b>Chirality (n)</b>
        <p>
        Specifies <i>n</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation 
        R = na1 + ma2 .
        </p>""")
    
    propMgr.chiralityMSpinBox.setWhatsThis(
        """<b>Chirality (m)</b>
        <p>
        Specifies <i>m</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation 
        R = na1 + ma2 .
        </p>""")
            
    propMgr.typeComboBox.setWhatsThis(
        """<b>Type</b>
        <p>
        Specifies the type of nanotube to generate.</p>
        <p>
        Selecting <b>Carbon</b> creates a carbon nanotube (CNT) made 
        entirely of carbon atoms.
        <p>
        Selecting <b>Boron nitride</b> creates a boron nitride (BN) nanotube
        made of boron and nitrogen atoms.
        </p>""")
    
    propMgr.endingsComboBox.setWhatsThis(
        """<b>Endings</b>
        <p>
        Specify how to deal with bondpoints on the two ends of the nanotube.</p>
        <p>
        Selecting <b>None</b> does nothing, leaving bondpoints on the ends.</p>
        <p>
        Selecting <b>Hydrogen</b>terminates the bondpoints using hydrogen 
        atoms.</p>
        <p>
        Selecting <b>Nitrogen </b>transmutes atoms with bondpoints into
        nitrogen atoms.
        </p>""")
    
    propMgr.lengthField.setWhatsThis(
        """<b>Length</b>
        <p>
        Specify the length of the nanotube in angstroms.
        </p>""")
    
    propMgr.bondLengthField.setWhatsThis(
        """<b>Bond Length</b>
        <p>
        Specify the bond length between atoms in angstroms.</p>""")
    
    propMgr.twistSpinBox.setWhatsThis(
        """<b>Twist</b>
        <p>
        Introduces a twist along the length of the nanotube specified in 
        degrees/angstrom.
        </p>""")
    
    propMgr.zDistortionField.setWhatsThis(
        """<b>Z-distortion</b>
        <p>
        Distorts the bond length between atoms along the length of the
        nanotube by this amount in angstroms.
        </p>""")
    
    propMgr.bendSpinBox.setWhatsThis(
        """<b>Bend</b>
        <p>
        Bend the nanotube by the specified number of degrees.
        </p>""")
    
    propMgr.xyDistortionField.setWhatsThis(
        """<b>XY-distortion</b>
        <p>
        Distorts the tube's cross-section so that the width in the X direction
        is this many angstroms greater than the width in the Y direction. 
        Some distortion  of bond lengths results.
        </p>""")
    
    propMgr.mwntCountSpinBox.setWhatsThis(
        """<b>Number of Nanotubes</b>
        <p>
        Specifies the number or Multi-Walled Nanotubes. Multi-Walled nanotubes
        (MWNT) consist of many concentric tubes wrapped one inside another.</p>
        <p>
        The specified chirality applies only to the innermost nanotube. 
        The others, being larger, will have larger chiralities.
        </p>""")
    
    propMgr.mwntSpacingField.setWhatsThis(
        """<b>Spacing</b>
        <p>
        Specify the spacing between nanotubes in angstroms.
        </p>""")
    return

def whatsThis_InsertNanotube_PropertyManager(propMgr):
    """
    "Whats This" text for widgets in the Nanotube Property Manager.
    """
    
    propMgr.ntTypeComboBox.setWhatsThis(
        """<b>Type</b>
        <p>
        Specifies the type of nanotube to insert.</p>
        <p>
        Selecting <b>Carbon</b> creates a carbon nanotube (CNT) made 
        entirely of carbon atoms.
        <p>
        Selecting <b>Boron Nitride</b> creates a boron nitride nanotube (BNNT) 
        made of boron and nitrogen atoms.
        </p>""")
    
    propMgr.ntDiameterLineEdit.setWhatsThis(
        """<b>Diameter</b>
        <p>
        Displays the diameter of the nanotube in angstroms.
        </p>""")
    
    propMgr.chiralityNSpinBox.setWhatsThis(
        """<b>Chirality (n)</b>
        <p>
        Specifies <i>n</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation 
        R = na1 + ma2 .
        </p>""")
    
    propMgr.chiralityMSpinBox.setWhatsThis(
        """<b>Chirality (m)</b>
        <p>
        Specifies <i>m</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation 
        R = na1 + ma2 .
        </p>""")
            
    propMgr.endingsComboBox.setWhatsThis(
        """<b>Endings</b>
        <p>
        Specify how to deal with bondpoints on the two ends of the nanotube.</p>
        <p>
        Selecting <b>None</b> does nothing, leaving bondpoints on the ends.</p>
        <p>
        Selecting <b>Hydrogen</b> terminates the bondpoints using hydrogen 
        atoms.</p>
        <p>
        Selecting <b>Nitrogen</b> transmutes atoms with bondpoints into
        nitrogen atoms.
        </p>""")
    
    propMgr.bondLengthDoubleSpinBox.setWhatsThis(
        """<b>Bond Length</b>
        <p>
        Specify the bond length between neighboring atoms in angstroms.</p>""")
    
    propMgr.twistSpinBox.setWhatsThis(
        """<b>Twist</b>
        <p>
        Introduces a twist along the length of the nanotube specified in 
        degrees/angstrom.
        </p>""")
    
    propMgr.zDistortionDoubleSpinBox.setWhatsThis(
        """<b>Z-distortion</b>
        <p>
        Distorts the bond length between atoms along the length of the
        nanotube by this amount in angstroms.
        </p>""")
    
    propMgr.bendSpinBox.setWhatsThis(
        """<b>Bend</b>
        <p>
        Bend the nanotube by the specified number of degrees.
        </p>""")
    
    propMgr.xyDistortionDoubleSpinBox.setWhatsThis(
        """<b>XY-distortion</b>
        <p>
        Distorts the tube's cross-section so that the width in the X direction
        is this many angstroms greater than the width in the Y direction. 
        Some distortion of bond lengths results.
        </p>""")
    
    propMgr.mwntCountSpinBox.setWhatsThis(
        """<b>Number of Nanotubes</b>
        <p>
        Specifies the number or Multi-Walled Nanotubes. Multi-Walled nanotubes
        (MWNT) consist of many concentric tubes wrapped one inside another.</p>
        <p>
        The specified chirality applies only to the innermost nanotube. 
        The others, being larger, will have larger chiralities.
        </p>""")
    
    propMgr.mwntSpacingDoubleSpinBox.setWhatsThis(
        """<b>Wall Spacing</b>
        <p>
        Specify the spacing between nanotubes in angstroms.
        </p>""")
    return

def whatsThis_GrapheneGeneratorPropertyManager(propMgr):
    """
    "What's This" text for widgets in the Graphene Property Manager.
    """
    
    propMgr.heightField.setWhatsThis(
        """<b>Height</b>
        <p>
        The height (up to 50 angstroms) of the graphite sheet in angstroms.
        </p>""")
    
    propMgr.widthField.setWhatsThis(
        """<b>Width</b>
        <p>
        The width (up to 50 angstroms) of the graphene sheet in angstroms.
        </p>""")
    
    propMgr.bondLengthField.setWhatsThis(
        """<b>Bond length</b>
        <p>
        You can change the bond lengths (1.0-3.0 angstroms) in the
        graphene sheet. We believe the default value is accurate for sp
        <sup>2</sup>-hybridized carbons.
        </p>""")
    
    propMgr.endingsComboBox.setWhatsThis(
        """<b>Endings</b>
        <p>
        Graphene sheets can be unterminated (dangling bonds), 
        or terminated with hydrogen atoms or nitrogen atoms.
        </p>""")
    return

def whatsThis_MovePropertyManager(propMgr):
    """
    "What's This" text for widgets in the Move Property Manager.
    """

    # Translate group box widgets ################################

    propMgr.translateComboBox.setWhatsThis(
        """<b>Translation Options</b>
        <p>
        This menu provides different options for translating the
        current selection where:</p>
        <p>
        <b>Free Drag</b>: translates the selection by dragging the mouse
        while holding down the left mouse button (LMB).</p>
        <p>
        <b>By Delta XYZ</b>: tranlates the selection by a specified 
        offset.</p>
        <p>
        <b>To XYZ Position</b>: moves the selection to an absolute XYZ
        coordinate. The <i>centroid</i> of the selection is used for
        this operation.
        </p>""")

    propMgr.transFreeButton.setWhatsThis(
        """<b>Unconstrained Translation</b>
        <p>
        Translates the selection freely within the plane of the screen.
        </p>""")

    propMgr.transXButton.setWhatsThis(
        """<b>X Translation</b>
        <p>
        Constrains translation of the selection to the X axis.
        </p>""")

    propMgr.transYButton.setWhatsThis(
        """<b>Y Translation</b>
        <p>
        Constrains translation of the selection to the Y axis.
        </p>""")

    propMgr.transZButton.setWhatsThis(
        """<b>Z Translation</b>
        <p>Constrains translation of the selection to the Z axis.
        </p>""")

    propMgr.transAlongAxisButton.setWhatsThis(
        """<b>Axial Translation/Rotation</b>
        <p>
        Constrains both translation and rotation of the selection along
        the central axis of the selected object(s). This is especially
        useful for translating and rotating DNA duplexes along their
        own axis.
        </p>""")
    
    propMgr.moveFromToButton.setWhatsThis(
        """<b>Move From To</b>
        <p>
        Moves selection by offset vector between two user defined points
        </p>""")

    # By Delta XYZ widgets

    propMgr.moveDeltaXSpinBox.setWhatsThis(
        """<b>Delta X</b>
        <p>
        The X offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveDeltaYSpinBox.setWhatsThis(
        """<b>Delta Y</b>
        <p>
        The Y offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveDeltaZSpinBox.setWhatsThis(
        """<b>Delta Z</b>
        <p>
        The Z offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.transDeltaPlusButton.setWhatsThis(
        """<b>Delta +</b>
        <p>
        Moves the current selection by an offset
        specified by the Delta X, Y and Z spinboxes.
        </p>""")

    propMgr.transDeltaMinusButton.setWhatsThis(
        """<b>Delta -</b>
        <p>
        Moves the current selection by an offset opposite of that 
        specified by the Delta X, Y and Z spinboxes.
        </p>""")

    # To XYZ Position widgets

    propMgr.moveXSpinBox.setWhatsThis(
        """<b>X</b>
        <p>
        The X coordinate the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveYSpinBox.setWhatsThis(
        """<b>Y</b>
        <p>
        The Y coordinate the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveZSpinBox.setWhatsThis(
        """<b>Z</b>
        <p>
        The Z coordinate the selection is moved when 
        clicking the <b>Move to Absolute Position</b> button.
        </p>""")

    propMgr.moveAbsoluteButton.setWhatsThis(
        """<b>Move to Absolute Position</b>
        <p>
        Moves the current selection to the position
        specified by the X, Y and Z spinboxes. The selection's centroid
        is used compute how the selection is moved.
        </p>""")

    # Rotate group box widgets ############################

    propMgr.rotateComboBox.setWhatsThis(
        """<b>Rotate Options</b>
        <p>
        This menu provides different options for rotating the
        current selection where:</p>
        <p>
        <b>Free Drag</b>: rotates the selection by dragging the mouse
        while holding down the left mouse button (LMB).</p>
        <p>
        <b>By Specified Angle</b>: rotates the selection by a specified 
        angle.
        </p>""")

    # Free Drag widgets.

    propMgr.rotateFreeButton.setWhatsThis(
        """<b>Unconstrained Rotation</b>
        <p>
        Rotates the selection freely about its centroid.
        </p>""")

    propMgr.rotateXButton.setWhatsThis(
        """<b>X Rotation</b>
        <p>
        Constrains rotation of the selection to the X axis.
        </p>""")

    propMgr.rotateYButton.setWhatsThis(
        """<b>Y Rotation</b>
        <p>
        Constrains rotation of the selection to the Y axis.
        </p>""")

    propMgr.rotateZButton.setWhatsThis(
        """<b>Z Rotation</b>
        <p>
        Constrains rotation of the selection to the Z axis.
        </p>""")

    propMgr.rotAlongAxisButton.setWhatsThis(
        """<b>Axial Translation/Rotation</b>
        <p>
        Constrains both translation and rotation of the selection along
        the central axis of the selected object(s). This is especially
        useful for translating and rotating DNA duplexes along their
        own axis.
        </p>""")

    propMgr.rotateAsUnitCB.setWhatsThis(
        """<b>Rotate as unit</b>
        <p>
        When <b>checked</b>, the selection is rotated as a unit about its
        collective centroid.<br>
        When <b>unchecked</b>, the selected objects are rotated about their 
        own individual centroids.
        </p>""")

    # By Specified Angle widgets

    propMgr.rotateXButton.setWhatsThis(
        """<b>Rotate about X axis</b>
        <p>
        Constrains rotation about the X axis.
        </p>""")

    propMgr.rotateYButton.setWhatsThis(
        """<b>Rotate about Y axis</b>
        <p>
        Constrains rotation about the Y axis.
        </p>""")

    propMgr.rotateZButton.setWhatsThis(
        """<b>Rotate about Z axis</b>
        <p>
        Constrains rotation about the Z axis.
        </p>""")

    propMgr.rotateThetaSpinBox.setWhatsThis(
        """<b>Rotation angle</b>
        <p>
        Specifies the angle of rotation.
        </p>""")

    # These next two aren't working. 
    # I don't understand why not. Mark 2007-06-25.
    propMgr.rotateThetaPlusButton.setWhatsThis(
        """<b>Rotate</b>
        <p>
        Rotates the selection by the specified angle.
        </p>""")

    propMgr.rotateThetaMinusButton.setWhatsThis(
        """<b>Rotate (minus)</b>
        <p>
        Rotates the selection by the specified angle 
        (in the opposite direction).
        </p>""")
    
    propMgr.rotXaxisButton.setWhatsThis(
        """<b>Rotate about X axis</b>
        <p>
        Constrains rotation about the X axis.
        </p>""")
    
    propMgr.rotYaxisButton.setWhatsThis(
        """<b>Rotate about Y axis</b>
        <p>
        Constrains rotation about the Y axis.
        </p>""")
    
    propMgr.rotZaxisButton.setWhatsThis(
        """<b>Rotate about Z axis</b>
        <p>
        Constrains rotation about the Z axis.
        </p>""")
    
    return # End of whatsThis_DnaDuplexPropertyManager

def whatsThis_MoviePropertyManager(propMgr):
    """
    "What's This" text for widgets in the Movie Property Manager.
    """
    propMgr.frameNumberSpinBox.setWhatsThis(
        """<b>Frame Number</b>
        <p>
        Advances the movie to a specified frame 
        </p>""")
    
    propMgr.movieLoop_checkbox.setWhatsThis(
          """<b>Loop</b>
        <p>
        Displays the movie as a continuous loop. When enabled the movie player
        will automatically reset to the first frame after the last frame 
        is shown and replay the movie. 
        </p>""")
    
    propMgr.frameSkipSpinBox.setWhatsThis(
        """<b>Skip</b>
        <p>
        Allows you to skip the entered amount of frames during movie playback.
        </p>""")
    
    propMgr.fileOpenMovieAction.setWhatsThis(
          """<b>Open Movie File</b>
        <p>
        Loads an exsisting movie from file
        </p>""")
    
    propMgr.fileSaveMovieAction.setWhatsThis(
          """<b>Save Movie File</b>
        <p>
        Loads and exsisting movie file or saves the file as a POV-ray series 
        to be used in an animation
        </p>""")
    
    propMgr.moviePlayRevAction.setWhatsThis(
        """<b>Play Reverse</b>
        <p>
        Plays the movie backward in time
        </p>""")
    
    propMgr.moviePlayAction.setWhatsThis(
     """<b>Play Forward</b>
        <p>
        Plays the movie forward in time
        </p>""")
    
    propMgr.moviePauseAction.setWhatsThis(
        """<b>Pause Movie</b>
        <p>
        Pauses movie on current frame
        </p>""")
    
    propMgr.movieMoveToEndAction.setWhatsThis(
        """<b>Advance to End</b>
        <p>
        Advances movie to last frame
        </p>""")
    
    propMgr.movieResetAction.setWhatsThis(
         """<b>Reset Movie</b>
        <p>
        Advances movie to first frame
        </p>""")
    
    propMgr.frameNumberSlider.setWhatsThis(
        """<b>Advance Frame</b>
        <p>
       Dragging the slider advances the movie
        </p>""")
    return

def whatsThis_SequenceEditor(propMgr):
    """
    "What's This" text for widgets in the DNA Sequence Editor.
    """
    propMgr.loadSequenceButton.setWhatsThis(
        """<b>Load Sequence File</b>
        <p>
       Loads an existing strand sequence from a text file
        </p>""")
    
    propMgr.sequenceTextEdit.setWhatsThis(
        """<b>Edit Sequence </b>
        <p>
       Allows the user to edit a strand sequence 
        </p>""")
    
    propMgr.saveSequenceButton.setWhatsThis(
        """<b>Save Sequence </b>
        <p>
       Saves a strand sequence as a text file
        </p>""")
    
    propMgr.baseDirectionChoiceComboBox.setWhatsThis(
        """<b>Strand Directon </b>
        <p>
       Sets sequence direction between three prime and five prime strand ends
        </p>""")
    
    propMgr.findLineEdit.setWhatsThis(
        """<b>Find Sequence </b>
        <p>
       Searches for a specific sequence within the strand
        </p>""")
    
    propMgr.findPreviousToolButton.setWhatsThis(
        """<b>Find Previous </b>
        <p>
       Searches for the previous occurrence of given sequence along the strand
        </p>""")
    
    propMgr.findNextToolButton.setWhatsThis(
        """<b>Find Next </b>
        <p>
       Searches for the next occurrence of given sequence along the strand
        </p>""")
    
    propMgr.replacePushButton.setWhatsThis(
        """<b>Replace </b>
        <p>
       Allows user to edit the strand sequence returned by the <b>Find</b>
       command 
        </p>""")
    
    propMgr.sequenceTextEdit_mate.setWhatsThis(
        """<b>Mate </b>
        <p>
       Shows the complementary strand sequence
        </p>""")
    return

def whatsThis_ExtrudePropertyManager(propMgr):
    """
    "What's This" text for widgets in the Extrude Property Manager.
    """
    propMgr.extrude_productTypeComboBox.setWhatsThis(
        """<b>Final product</b>
        <p>
        The type of product to create. Options are:</p>
        <p>
        <b>Rod</b>: a straight rod.
        <br>
        <b>Ring</b>: a closed ring.
        </p>""")
    
    propMgr.extrudeSpinBox_n.setWhatsThis(
        """<b>Number of copies</b>
        <p>
        The total number of copies, including the originally selected 
        chunk(s).
        </p>""")
    
    propMgr.showEntireModelCheckBox.setWhatsThis(
        """<b>Show Entire Model</b>
        <p>
        Normally, only the selection and their copies are displayed 
        during the Extrude command. Checking this option displays 
        everything in the current model.
        </p>""")
        
    propMgr.makeBondsCheckBox.setWhatsThis(
        """<b>Make Bonds</b>
        <p>
        When checked, bonds will be made between pairs of bondpoints
        highlighted in blue and green after clicking <b>Done</b>.
        </p>""")
    
    propMgr.extrudeBondCriterionSlider.setWhatsThis(
        """<b>Tolerance slider</b>
        <p>
        Sets the bond criterion tolerance. The larger the tolerance 
        value, the further bonds will be formed between pairs of 
        bondpoints.
        </p>""")
    
    propMgr.extrudePrefMergeSelection.setWhatsThis(
        """<b>Merge Selection</b>
        <p>
        Merges the selected chunks into a single chunk after 
        clicking <b>Done</b>.
        </p>""")
        
    propMgr.mergeCopiesCheckBox.setWhatsThis(
        """<b>Merge Copies</b>
        <p>
        When checked, copies are merged with the original chunk
        after clicking <b>Done</b>.
        </p>""")
    
    propMgr.extrudeSpinBox_length.setWhatsThis(
        """<b>Total Offset</b>
        <p>
        The total offset distance between copies.
        </p>""")
    
    propMgr.extrudeSpinBox_x.setWhatsThis(
        """<b>X Offset</b>
        <p>
        The X offset distance between copies.
        </p>""")
        
    propMgr.extrudeSpinBox_y.setWhatsThis(
        """<b>Y Offset</b>
        <p>
        The Y offset distance between copies.
        </p>""")
        
    propMgr.extrudeSpinBox_z.setWhatsThis(
        """<b>Z Offset</b>
        <p>
        The Z offset distance between copies.
        </p>""")
    return
    
def whatsThis_CookiePropertyManager(propMgr):
    """
    "What's This" text for widgets in the Build Crystal Property Manager.
    """
    
    propMgr.surface100_btn.setWhatsThis(\
        "<b>Surface 100</b>"\
        "<p>"\
        "Reorients the view to the nearest angle that would "\
        "look straight into a (1,0,0) surface of a "\
        "diamond lattice."\
        "</p>")
    
    # Surface 110
    propMgr.surface110_btn.setWhatsThis(\
        "<b>Surface 110</b>"\
        "<p>"\
        "Reorients the view to the nearest angle that would "\
        "look straight into a (1,1,0) surface of a "\
        "diamond lattice."\
        "</p>")

    # Surface 111
    propMgr.surface111_btn.setWhatsThis(\
        "<b>Surface 111</b>"\
        "<p>"\
        "Reorients the view to the nearest angle that would "\
        "look straight into a (1,1,1) surface of a "\
        "diamond lattice."\
        "</p>")
    
    propMgr.addLayerButton.setWhatsThis(\
        "<b>Add Layer</b>"\
        "<p>"\
        "Adds a new layer of diamond lattice to the existing "\
        "layer."\
        "</p>")
    
    propMgr.latticeCBox.setWhatsThis(
        "<b>Lattice Type</b>"\
        "<p>"\
        "Selects which lattice structure is displayed, either "\
        "Diamond or Lonsdaleite"\
        "</p>")
    
    propMgr.rotateGridByAngleSpinBox.setWhatsThis(
        "<b>Rotate By</b>"\
        "<p>"\
        "Allows you to select the degree of rotation"\
        "</p>")
    
    propMgr.rotGridAntiClockwiseButton.setWhatsThis(
        "<b>Rotate Counter Clockwise</b>"\
        "<p>"\
        "Rotates the current view in a counter-clockwise direction"\
        "</p>")
    
    propMgr.rotGridClockwiseButton.setWhatsThis(
        "<b>Rotate Clockwise</b>"\
        "<p>"\
        "Rotates the current view in a clockwise direction"\
        "</p>")
    
    propMgr.layerCellsSpinBox.setWhatsThis(
        "<b>Lattice Cells</b>"\
        "<p>"\
        "Determines the thickness of the crystal layer"\
        "</p>")
    
    propMgr.dispModeComboBox.setWhatsThis (
        "<b>Display Style</b>"\
        "<p>"\
        "Lets you select the format in which your crystal selection "
        "is displayed"\
        "</p>")
    
    propMgr.layerThicknessLineEdit.setWhatsThis(
        "<b>Thickness</b>"\
        "<p>"\
        "Thickness of layer in angstroms is displayed"\
        "</p>")
    
    propMgr.gridLineCheckBox.setWhatsThis(
        "<b>Show Grid</b>"\
        "<p>"\
        "Allows you to turn on/off the orange lattice grid lines"\
        "</p>")
    
    propMgr.fullModelCheckBox.setWhatsThis(
        "<b>Show Model</b>"\
        "<p>"\
        "Allows you to view your current model from the Graphics Area in "\
        "overlay with the Crystal Cutter lattice view"\
        "</p>")
        
    propMgr.snapGridCheckBox.setWhatsThis(
        "<b>Snap Grid</b>"\
        "<p>"\
        "Makes your lattice selection correspond with the grid lines "\
        "</p>")
    
    propMgr.freeViewCheckBox.setWhatsThis(
        "<b>Free View</b>"\
        "<p>"\
        "Allows you to change the current view of the lattice structure so "\
        "that it can be viewed from any angle. This can be done by using the "\
        "middle mouse button."\
        "</p>")
    return
        
def whatsThis_RotaryMotorPropertyManager(propMgr):
    """
    What's This text for some of the widgets in the Property Manager.
    """
    
    # Removed name field from property manager. Mark 2007-05-28
    #propMgr.nameLineEdit.setWhatsThis("""<b>Name</b><p>Name of Rotary Motor 
    #that appears in the Model Tree</p>""")
    
    propMgr.torqueDblSpinBox.setWhatsThis(
        """<b>Torque </b>
        <p>
        Simulations will begin with the motor's torque set to this value.
        </p>""")
    
    propMgr.initialSpeedDblSpinBox.setWhatsThis(
        """<b>Initial Speed</b> 
        <p>
        Simulations will begin with the motor's flywheel rotating at 
        this velocity.
        </p>""")
    
    propMgr.finalSpeedDblSpinBox.setWhatsThis(
        """<b>Final Speed</b>
        <p>
        The final velocity of the motor's flywheel during simulations.
        </p>""")
    
    propMgr.dampersCheckBox.setWhatsThis(
        """<b>Dampers</b>
        <p>
        If checked, the dampers are enabled for this motor during a simulation. 
        See the Rotary Motor web page on the NanoEngineer-1 Wiki for 
        more information.
        </p>""")
    
    propMgr.enableMinimizeCheckBox.setWhatsThis(
        """<b>Enable in Minimize <i>(experimental)</i></b>
        <p>
        If checked, the torque specified above will be applied to the 
        motor atoms during a structure minimization.  While intended to 
        allow simulations to begin with rotary motors running at speed, 
        this feature requires more work to be useful.
        </p>""")
    
    propMgr.motorLengthDblSpinBox.setWhatsThis(
        """<b>Motor Length</b>
        <p>
        The motor jig is drawn as a cylinder. This is the
        dimensions of the solid's length, measured in angstroms.
        </p>""")
    
    propMgr.motorRadiusDblSpinBox.setWhatsThis(
        """<b>Motor Radius</b>
        <p>
        The motor jig is drawn as a cylinder. This is the
        radius of the cylinder, measured in angstroms.
        </p>""")
    
    propMgr.spokeRadiusDblSpinBox.setWhatsThis(
        """<b>Spoke Radius</b>
        <p>
        Atoms are connected to the motor body by spokes, and this is the 
        radius of the spokes, measured in angstroms. 
        </p>""")
    
    propMgr.motorColorComboBox.setWhatsThis(
        """<b>Color</b>
        <p>
        Changes the color of the motor.
        </p>""")
    
    propMgr.directionPushButton.setWhatsThis(
        """<b>Change Direction</b>
        <p>
        Changes direction of the motor
        </p>""")
    return
    
def whatsThis_LinearMotorPropertyManager(propMgr):
    """
    What's This text for widgets in the Linear Motor Property Manager.
    """
    
    propMgr.forceDblSpinBox.setWhatsThis(
        """<b>Force </b>
        <p>
        Simulations will begin with the motor's force set to this value.
        </p>""")
    
    propMgr.enableMinimizeCheckBox.setWhatsThis(
        """<b>Enable in Minimize <i>(WARNING: EXPERIMENTAL FEATURE)</i></b>
        <p>
        If checked, the force specified above will be applied to the 
        motor atoms during a structure minimization.  While intended to 
        allow simulations to begin with Linear motors running at speed, 
        this feature requires more work to be useful.
        </p>""")
    
    propMgr.stiffnessDblSpinBox.setWhatsThis(
        """<b>Stiffness</b>
        <p>
        If non-zero, this parameter will modify the motor's force according 
        to its position, as though the motor were a spring.</p>
        <p>
        When stiffness = 0, the motor's force is constant and will have the
        same direction and magnitude regardless of atom position.
        </p>""")
    
    propMgr.motorLengthDblSpinBox.setWhatsThis(
        """<b>Motor Length</b>
        <p>
        The body of the motor jig is drawn as a rectangular solid, with the
        long dimension in the direction of the motor's motion. This is the
        dimensions of the solid's length, measured in angstroms.
        </p>""")
    
    propMgr.motorWidthDblSpinBox.setWhatsThis(
        """<b>Motor Width</b>
        <p>
        The body of the motor jig is drawn as a rectangular solid, with the
        long dimension in the direction of the motor's motion. This is the
        dimensions of the solid's width, measured in angstroms.
        </p>""")
    
    propMgr.spokeRadiusDblSpinBox.setWhatsThis(
        """<b>Spoke Radius</b>
        <p>
        Atoms are connected to the motor body by spokes, and this is the 
        radius of the spokes, measured in angstroms.
        </p>""")
    
    propMgr.motorColorComboBox.setWhatsThis(
        """<b>Color</b>
        <p>
        Changes the color of the motor.
        </p>""")
    
    propMgr.directionPushButton.setWhatsThis(
        """<b>Change Direction</b>
        <p>
        Changes direction of the linear motor
        </p>""")
    return

def whatsThis_PlanePropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Plane Property Manager.
    """    
    propMgr.heightDblSpinBox.setWhatsThis(
        """<b>Height</b>
        <p>
        The height of the Plane in angstroms. (up to 200 angstroms)
        </p>""")
    
    propMgr.widthDblSpinBox.setWhatsThis(
        """<b>Width</b>
        <p>
        The width of the Plane in angstroms. (up to 200 angstroms)
        </p>""")
    return
    
def whatsThis_QuteMolPropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the QuteMolX Property Manager.
    """
    propMgr.launchQuteMolButton.setWhatsThis(
        """
        <b>Launch QuteMolX</b>
        <p>
        Pressing this button launches QuteMolX.
        </p>""")
    
    propMgr.axesCombobox.setWhatsThis(
        """
        <b>Render Axes</b>
        <p>
        Allows the user to select between rendering and hiding the 
        DNA axis pseudo atoms
        </p>""")
    
    propMgr.basesCombobox.setWhatsThis(
        """
        <b>Render Bases</b>
        <p>
        Allows the user to select between rendering and hiding the 
        DNA strand bases
        </p>""")
    return

def whatsThis_BuildAtomsPropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the QuteMolX Property Manager.
    """
    propMgr.selectionFilterCheckBox.setWhatsThis(
        """<b>Enable Atom Selection Filter</b>
        <p>
        When checked, the <i>atom selection filter</i> is enabled. 
        Only atom types listed in the <b>Atom Selection Filter List</b> are 
        included in selection operations (i.e. region selections in the 
        <a href=Graphics_Area>graphics area</a>).</p>
        <p>
        While the <i>atom selection filter</i> is enabled, the 
        <b>Atom Selection Filter List</b> is updated by selecting atom types 
        in the <b>Atom Chooser</b>.</p>
        <p>
        <img source=\"ui/actions/Help/HotTip.png\"><br>
        <b>Hot Tip:</b> To specify multiple atom types in the 
        <b>Atom Selection Filter Field</b>, hold down the <b>Shift Key</b> while 
        selecting atom types in the <b>Atom Chooser</b>.
        </p>""")
    
    propMgr.filterlistLE.setWhatsThis(
        """<b>Atom Selection Filter List</b>
        <p>
        When the <b>Enable atom selection filter</b> is checked, this list shows 
        the current atom type(s) to be included in the selection during 
        selection operations. <i>Only atom types in this list are included in 
        selection operations.</i></p>
        <p>
        This list is updated by selecting atom types in the <b>Atom Chooser</b>.</p>
        <p>
        <img source=\"ui/actions/Help/HotTip.png\"><br>
        <b>Hot Tip:</b> To specify multiple atom types, hold down the 
        <b>Shift Key</b> while selecting atom types in the <b>Atom Chooser</b>.
        </p>""")
    
    propMgr.autoBondCheckBox.setWhatsThis(
        """<b>Auto bond</b>
        <p>
        When enabled, additional bonds are formed automatically with the
        deposited atom if possile.
        </p>""")
    
    propMgr.reshapeSelectionCheckBox.setWhatsThis(
        """<b>Dragging reshapes selection</b>
        <p>
        When enabled, selected atoms are "reshaped" when dragged by the mouse.
        </p>
        <p>
        When disabled (default), selected atoms follow the mouse as typical
        when dragged.
        </p>""")
    
    propMgr.waterCheckBox.setWhatsThis(
        """<b><u>Z depth filter</u></b> <b>(water surface)</b>
        <p>
       Enables/disables the Z depth filter for hover highlighting and single
       atom/bond selection. When enabled, a semi-transparent "water surface" 
       is displayed that remains parallel to the screen. This gives the
       illusion that atoms below the surface are under water. Atoms and bonds
       under the water are not highlighted and cannot be selected 
       by clicking on them. This is useful when working on local regions 
       of large structures since only atoms and bonds above the surface 
       are highlighted. This can speed up interactive response times 
       significantly.</p>
       <p>
       <img source=\"ui/actions/Help/HotTip.png\"><br>
       The water surface can be made deeper/shallower by holding
       down the <b>Control + Shift</b> keys together and pushing/pulling the 
       mouse while holding down the middle mouse button.</p>
       <p>
       <b>Note:</b> Region selections are immume to the Z depth filter.
       </p>""")
    
    propMgr.highlightingCheckBox.setWhatsThis(
        """<b>Hover highlighting</b>
        <p>
        Enables/disables <i>hover highlighting</i>. When enabled, atoms and bonds
        under the cursor are highlighted to indicate what would be selected 
        if the user clicks the left mouse button. 
        </p>""")
    
    propMgr.showSelectedAtomInfoCheckBox.setWhatsThis(
        """<b>Show Selected Atoms's Info</b>
        <p>
        When checked an atom's position is displayed as X Y Z coordinates.
        These coordinates can also be adjusted with provided spin boxes.
        </p>""")
    return
    
def whatsThis_PartLibPropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Part Library Property Manager.
    """
    propMgr.previewGroupBox.setWhatsThis(
        """<b>Preview Window</b>
        <p>
        This window displays the selected part chosen from the library.
        The user may also rotate the part and set a hot spot while 
        the part is displayed in the preview window""" )
   
    
    propMgr.partLibGroupBox .setWhatsThis(
        """<b>Part Library</b>
        <p>
        This is a directory of available parts contained 
        in the part library """ )
    return

def whatsThis_PasteItemsPropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Part Library Property Manager.
    """
    propMgr.previewGroupBox.setWhatsThis(
        """<b>Preview Window</b>
        <p>
        This window displays the selected part chosen from the clipboard.
        The user may also rotate the part and set a hot spot while 
        the part is displayed in the preview window""" )
   
    
    propMgr.clipboardGroupBox.setWhatsThis(
        """<b>Clipboard</b>
        <p>
        This is a list of items contained on the Clipboard """ )
    return
    
def WhatsThis_EditDnaDisplayStyle_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Edit DNA Display Style Property 
    Manager.
    """
    propMgr.favoritesComboBox.setWhatsThis(
        """<b>DNA Display Style Favorites</b>
        <p>
        A list of DNA display style favorites added by the user that can be
        applied by pressing the <b>Apply Favorite</b> button. The settings
        are only in effect whenever the <i>Global Display Style</i> is set 
        to DNA Cylinder or to DNA objects that have their display style set
        to DNA Cylinder.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyFavorite.png\"><br>
        The <b>Apply Favorite</b> button must be clicked to apply the 
        current favorite selected from this list. <b>Factory default
        settings</b> resets all color options to their default
        settings.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        The <b>Add Favorite</b> button allows new favorites to
        be added to the list. This saves the current settings
        to a user specified name.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        The <b>Delete Favorite</b> button allows an existing favorite to
        be deleted from the list. <b>Factory default settings</b> can
        never be deleted, however.
            """)
    
    propMgr.applyFavoriteButton.setWhatsThis(
        """<b>Apply Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyFavorite.png\"><br>
        Applies the settings stored in the selected Favorite to the current 
        settings.
        """)
        
    propMgr.addFavoriteButton.setWhatsThis(
        """<b>Add Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        Allows a new Favorite to be added to the list. 
        This saves the current settings to a user specified Favorite name.
        """)
    
    propMgr.deleteFavoriteButton.setWhatsThis(
        """<b>Delete Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        Allows an existing favorite to be deleted from the list. 
        <b>Factory default settings</b> can never be deleted, however.
        """)
    
    propMgr.loadFavoriteButton.setWhatsThis(
        """<b>Load Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/LoadFavorite.png\"><br>
        Allows the user to load a <i>favorites file</i> from disk to be
        added to the favorites list. Favorites files must have a .txt extension.
        """)
    propMgr.saveFavoriteButton.setWhatsThis(
        """<b>Save Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/SaveFavorite.png\"><br>
        Writes the selected favorite (selected in the combobox) to a file that
        can be given to another NE1 user (i.e. as an email attachment). The 
        file is saved with a .txt entension so that it can loaded back using
        the <b>Load Favorite</b> button.
        """)   
    return

def WhatsThis_ColorScheme_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Color Scheme Property 
    Manager.
    """
    propMgr.favoritesComboBox.setWhatsThis(
        """<b>Color Scheme Favorites</b>
        <p>
        A list of color scheme favorites added by the user that can be
        applied to NanoEngineer-1 by pressing the <b>Apply Favorite</b>
        button.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyColorSchemeFavorite.png\"><br>
        The <b>Apply Favorite</b> button must be clicked to apply the 
        current favorite selected from this list. <b>Factory default
        settings</b> resets all color options to their default
        settings.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        The <b>Add Favorite</b> button allows new favorite color schemes to
        be added to the list. This saves the current color settings
        to a user specified name.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        The <b>Delete Favorite</b> button allows an existing favorite to
        be deleted from the list. <b>Factory default settings</b> can
        never be deleted, however.
        """)
    
    propMgr.applyFavoriteButton.setWhatsThis(
        """<b>Apply Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyColorSchemeFavorite.png\"><br>
        Applies the color settings stored in the selected Color Scheme
        Favorite to the current color scheme.
        """)
        
    propMgr.addFavoriteButton.setWhatsThis(
        """<b>Add Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        Allows a new Color Scheme Favorite to be added to the list. 
        This saves the current color settings to a user specified name.
        """)
    
    propMgr.deleteFavoriteButton.setWhatsThis(
        """<b>Delete Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        Allows an existing favorite to be deleted from the list. 
        <b>Factory default settings</b> can never be deleted, however.
        """)
    
    propMgr.loadFavoriteButton.setWhatsThis(
        """<b>Load Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/LoadFavorite.png\"><br>
        Allows the user to load a <i>favorites file</i> from disk to be
        added to the favorites list. Favorites files must have a .txt extension.
        """)
    propMgr.saveFavoriteButton.setWhatsThis(
        """<b>Save Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/SaveFavorite.png\"><br>
        Writes the selected favorite (selected in the combobox) to a file that
        can be given to another NE1 user (i.e. as an email attachment). The 
        file is saved with a .txt entension so that it can loaded back using
        the <b>Load Favorite</b> button.
        """)
    propMgr.backgroundColorComboBox.setWhatsThis(
        """ <b>Background Color </b>
        <p>
        Allows user to change the color of the background.
        </p>""")
    propMgr.hoverHighlightingStyleComboBox.setWhatsThis(
        """ <b>Highlighting Style </b>
        <p>
        Allows user to change the type of pattern the indicates a highlighted object.
        </p>""")
    propMgr.hoverHighlightingColorComboBox.setWhatsThis(
        """ <b>Highlighting Color </b>
        <p>
        Allows user to change the color of the highlight.
        </p>""") 
    propMgr.selectionStyleComboBox.setWhatsThis(
        """ <b>Selection Style </b>
        <p>
        Allows user to change the type of pattern the indicates a selected object.
        </p>""")
    propMgr.selectionColorComboBox.setWhatsThis(
        """ <b>Selction Color </b>
        <p>
        Allows user to change the color of a selected object.
        </p>""")
    propMgr.enableFogCheckBox.setWhatsThis(
        """ <b>Fog </b>
        <p>
        Enable/Disable a fog over the working area.
        </p>""")
    return

def WhatsThis_LightingScheme_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Lighting Scheme Property 
    Manager.
    """
    propMgr.favoritesComboBox.setWhatsThis(
        """<b>Lighting Scheme Favorites</b>
        <p>
        A list of lighting scheme favorites added by the user that can be
        applied to NanoEngineer-1 by pressing the <b>Apply Favorite</b>
        button.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyLightingSchemeFavorite.png\"><br>
        The <b>Apply Favorite</b> button must be clicked to apply the 
        current favorite selected from this list. <b>Factory default
        settings</b> resets all color options to their default
        settings.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        The <b>Add Favorite</b> button allows new favorite color schemes to
        be added to the list. This saves the current color settings
        to a user specified name.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        The <b>Delete Favorite</b> button allows an existing favorite to
        be deleted from the list. <b>Factory default settings</b> can
        never be deleted, however.
        """)
    
    propMgr.applyFavoriteButton.setWhatsThis(
        """<b>Apply Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyLightingSchemeFavorite.png\"><br>
        Applies the lighting settings stored in the selected Lighting Scheme
        Favorite to the current color scheme.
        """)
        
    propMgr.addFavoriteButton.setWhatsThis(
        """<b>Add Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        Allows a new Lighting Scheme Favorite to be added to the list. 
        This saves the current color settings to a user specified name.
        """)
    
    propMgr.deleteFavoriteButton.setWhatsThis(
        """<b>Delete Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        Allows an existing favorite to be deleted from the list. 
        <b>Factory default settings</b> can never be deleted, however.
        """)
    
    propMgr.loadFavoriteButton.setWhatsThis(
        """<b>Load Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/LoadFavorite.png\"><br>
        Allows the user to load a <i>favorites file</i> from disk to be
        added to the favorites list. Favorites files must have a .txt extension.
        """)
    propMgr.saveFavoriteButton.setWhatsThis(
        """<b>Save Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/SaveFavorite.png\"><br>
        Writes the selected favorite (selected in the combobox) to a file that
        can be given to another NE1 user (i.e. as an email attachment). The 
        file is saved with a .txt entension so that it can loaded back using
        the <b>Load Favorite</b> button.
        """)
    propMgr.lightComboBox.setWhatsThis(
        """<b> Light </b>
        <p>
        The current light to modify. NanoEngineer-1 supports up to 3 light 
        sources.
        </p>""")
    propMgr.enableLightCheckBox.setWhatsThis(
        """<b> On Check Box</b>
        <p>
        Enables/disables the current light.
        </p>""")
    propMgr.lightColorComboBox.setWhatsThis(
        """<b> Color </b>
        <p>
        Change color of the current light.
        </p>""")
    propMgr.ambientDoubleSpinBox.setWhatsThis(
        """<b> Ambient </b>
        <p>
        The ambient value (between 0-1) of the current light.
        </p>""")
    propMgr.diffuseDoubleSpinBox.setWhatsThis(
        """<b> Diffuse </b>
        <p>
        The diffuse value (between 0-1) of the current light.
        </p>""")
    propMgr.specularDoubleSpinBox.setWhatsThis(
        """<b> Specular </b>
        <p>
        The specularity value (between 0-1) of the current light.
        </p>""")
    propMgr.xDoubleSpinBox.setWhatsThis(
        """<b> X Position </b>
        <p>
        The X coordinite of the current light position.
        </p>""")
    propMgr.yDoubleSpinBox.setWhatsThis(
        """<b> Y Position </b>
        <p>
        The Y coordinite of the current light position.
        </p>""")
    propMgr.zDoubleSpinBox.setWhatsThis(
        """<b> Z Position </b>
        <p>
        The Z coordinite of the current light position.
        </p>""")
    propMgr.enableMaterialPropertiesCheckBox.setWhatsThis(
        """<b> Material Properties</b>
        <p>
        Enables/Disables the material properties.
        </p>""")
    propMgr.finishDoubleSpinBox.setWhatsThis(
        """<b> Finish </b>
        <p>
        Material finish value (between 0-1)
        </p>""")
    propMgr.shininessDoubleSpinBox.setWhatsThis(
        """<b> Shininess </b>
        <p>
        Material shininess value (between 0-60).
        </p>""")
    propMgr.brightnessDoubleSpinBox.setWhatsThis(
        """<b> Brightness </b>
        <p>
        Material brightness value (between 0-1).
        </p>""")
    return

def WhatsThis_EditProteinDisplayStyle_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Edit Protein Display Style Property 
    Manager.
    """
    propMgr.favoritesComboBox.setWhatsThis(
        """<b>Protein Display Style Favorites</b>
        <p>
        A list of Protein display style favorites added by the user that can be
        applied by pressing the <b>Apply Favorite</b> button. </p>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyFavorite.png\"><br>
        The <b>Apply Favorite</b> button must be clicked to apply the 
        current favorite selected from this list. <b>Factory default
        settings</b> resets all options to their default
        settings.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        The <b>Add Favorite</b> button allows new favorites to
        be added to the list. This saves the current settings
        to a user specified name.</p>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        The <b>Delete Favorite</b> button allows an existing favorite to
        be deleted from the list. <b>Factory default settings</b> can
        never be deleted, however.
            """)
    
    propMgr.applyFavoriteButton.setWhatsThis(
        """<b>Apply Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/ApplyFavorite.png\"><br>
        Applies the settings stored in the selected Favorite to the current 
        settings.
        """)
        
    propMgr.addFavoriteButton.setWhatsThis(
        """<b>Add Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/AddFavorite.png\"><br>
        Allows a new Favorite to be added to the list. 
        This saves the current settings to a user specified Favorite name.
        """)
    
    propMgr.deleteFavoriteButton.setWhatsThis(
        """<b>Delete Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/DeleteFavorite.png\"><br>
        Allows an existing favorite to be deleted from the list. 
        <b>Factory default settings</b> can never be deleted, however.
        """)
    
    propMgr.loadFavoriteButton.setWhatsThis(
        """<b>Load Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/LoadFavorite.png\"><br>
        Allows the user to load a <i>favorites file</i> from disk to be
        added to the favorites list. Favorites files must have a .txt extension.
        """)
    propMgr.saveFavoriteButton.setWhatsThis(
        """<b>Save Favorite </b>
        <p>
        <img source=\"ui/actions/Properties Manager/SaveFavorite.png\"><br>
        Writes the selected favorite (selected in the combobox) to a file that
        can be given to another NE1 user (i.e. as an email attachment). The 
        file is saved with a .txt entension so that it can loaded back using
        the <b>Load Favorite</b> button.
        """)   
    return

def whatsThis_OrderDna_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Color Scheme Property 
    Manager.
    """
    propMgr.includeStrandsComboBox.setWhatsThis(
        """<b>Include strands</b>
        <p>
        Strands to include in the DNA order file.
        """)
    
    propMgr.numberOfBasesLineEdit.setWhatsThis(
        """<b>Total nucleotides</b>
        <p>
        The total number of nucleotides (bases) that will be written to the 
        DNA order file.
        </p>
        """)
    
    propMgr.numberOfXBasesLineEdit.setWhatsThis(
        """<b>Unassigned</b>
        <p>
        The total number of unassigned "X" bases that will be written to the 
        DNA order file. There should be 0 unassigned bases if the file will
        be used to place an order.
        </p>
        """)
    
    propMgr.viewDnaOrderFileButton.setWhatsThis(
        """<b>View DNA Order File</b>
        <p>
        View the DNA Order file in comma-separated values (CVS) format.
        The file is temporary and should be saved via the text editor to a
        permanant name/location.
        </p>
        """)
    return
