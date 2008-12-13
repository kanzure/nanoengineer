# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ToolTipText_for_MainWindow.py

This file provides functions for setting the Tool tip text
for widgets in the Property Managers.

@version:$Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
def ToolTip_CookiePropertyManager(propMgr):
    """
    "Tool Tip" text for widgets in the BuildCrystal Property Manager.
    """

    propMgr.addLayerButton.setToolTip("Add Layer")

    propMgr.latticeCBox.setToolTip("Select Lattice Type")

    propMgr.rotateGridByAngleSpinBox.setToolTip("Set Angle")

    propMgr.rotGridAntiClockwiseButton.setToolTip("Rotate Counter Clockwise")

    propMgr.rotGridClockwiseButton.setToolTip("Rotate Clockwise")

    propMgr.layerCellsSpinBox.setToolTip("Number of Lattice Cells")

    propMgr.dispModeComboBox.setToolTip("Display Style")   

    propMgr.layerThicknessLineEdit.setToolTip(\
        "Thickness of Layer in Angstroms is Displayed")

    propMgr.gridLineCheckBox.setToolTip("Show Grid")

    propMgr.fullModelCheckBox.setToolTip("Show Model")

    propMgr.snapGridCheckBox.setToolTip("Snap to Grid")

    propMgr.freeViewCheckBox.setToolTip("Free View") 


def ToolTip_RotaryMotorPropertyManager(propMgr):

    """
    "Tool Tip" text for widgets in the Rotary Motor Property Manager.
    """

    propMgr.torqueDblSpinBox.setToolTip("Motor torque")

    propMgr.initialSpeedDblSpinBox.setToolTip("Initial speed")

    propMgr.finalSpeedDblSpinBox.setToolTip("Final speed")

    propMgr.dampersCheckBox.setToolTip("Turn motor dampers on/off")

    propMgr.enableMinimizeCheckBox.setToolTip("Enable motor during" \
                                              " minimizations")

    propMgr.motorLengthDblSpinBox.setToolTip("Set motor length")

    propMgr.motorRadiusDblSpinBox.setToolTip("Set motor radius")

    propMgr.spokeRadiusDblSpinBox.setToolTip("Set spoke radius")

    propMgr.motorColorComboBox.setToolTip("Change motor color")

    propMgr.directionPushButton.setToolTip("Set rotation direction")


def ToolTip_LinearMotorPropertyManager(propMgr):

    """
    Tool Tip text for widgets in the Linear Motor Property Manager.
    """

    propMgr.forceDblSpinBox.setToolTip("Specify motor force")

    propMgr.enableMinimizeCheckBox.setToolTip("Enabled motor during" \
                                              " minimizations")

    propMgr.stiffnessDblSpinBox.setToolTip("Specify stiffness")

    propMgr.motorLengthDblSpinBox.setToolTip("Set motor length")

    propMgr.motorWidthDblSpinBox.setToolTip("Set motor width")

    propMgr.spokeRadiusDblSpinBox.setToolTip("Set motor radius")

    propMgr.motorColorComboBox.setToolTip("Change motor color")

    propMgr.directionPushButton.setToolTip("Set motor direction")  

def ToolTip_GrapheneGeneratorPropertyManager(propMgr):

    """
    "Tool Tip" text for widgets in the Graphene Property Manager.
    """

    propMgr.heightField.setToolTip("The Height in Angstroms")

    propMgr.widthField.setToolTip("The Width in Angstroms")

    propMgr.bondLengthField.setToolTip("Adjust Bond Length")

    propMgr.endingsComboBox.setToolTip("Set Sheet Endings")  

def ToolTip_NanotubeGeneratorPropertyManager(propMgr):

    """
    "ToolTip" text for widgets in the Nanotube Property Manager.
    """

    propMgr.chiralityNSpinBox.setToolTip("Chirality (n)")

    propMgr.chiralityMSpinBox.setToolTip("Chirality (m)")

    propMgr.typeComboBox.setToolTip("Select Tube Type")

    propMgr.endingsComboBox.setToolTip("Select Tube Endings")

    propMgr.lengthField.setToolTip("Length of the Nanotube in Angstroms")

    propMgr.bondLengthField.setToolTip("Length Between Atoms in Angstroms")

    propMgr.twistSpinBox.setToolTip("Twist")

    propMgr.zDistortionField.setToolTip("Z-distortion")

    propMgr.bendSpinBox.setToolTip("Bend Tube")

    propMgr.xyDistortionField.setToolTip("XY-distortion")

    propMgr.mwntCountSpinBox.setToolTip("Number of Tubes")

    propMgr.mwntSpacingField.setToolTip("Spacing Between Multiple Tubes")

def ToolTip_InsertDna_PropertyManager(propMgr):
    """
    "ToolTip" text for the DnaDuplex Property Manager
    """

    propMgr.conformationComboBox.setToolTip("Only B-DNA is currently "\
                                            "supported in NanoEngineer-1")

    propMgr.dnaModelComboBox.setToolTip("Selects Between Model Types")

    propMgr.numberOfBasePairsSpinBox.setToolTip("Number of Base Pairs")

    propMgr.basesPerTurnDoubleSpinBox.setToolTip("Bases Per Turn")

    propMgr.duplexLengthLineEdit.setToolTip("Duplex Length")

    propMgr.dnaRubberBandLineDisplayComboBox.setToolTip("Display as Ribbon or "\
                                                        "Ladder")

    propMgr.lineSnapCheckBox.setToolTip("Enable Line Snap")
    
def ToolTip_InsertPeptide_PropertyManager(propMgr):
    """
    "ToolTip" text for the Peptide Generator Property Manager
    """
    return

def ToolTip_BuildAtomsPropertyManager(propMgr):
    """
    "ToolTip" text for widgets in the QuteMolX Property Manager.
    """
    propMgr.selectionFilterCheckBox.setToolTip("Atom Selection Filter")

    propMgr.filterlistLE.setToolTip("Atom Selection Filter List")
    
    propMgr.reshapeSelectionCheckBox.setToolTip("Enable/disable reshaping the selection while dragging selected atom")

    propMgr.autoBondCheckBox.setToolTip("Enable/disable atomic auto-bonding")

    propMgr.waterCheckBox.setToolTip("Enable/disable water surface")

    propMgr.highlightingCheckBox.setToolTip("Enable/disable hover highlighting")

    propMgr.showSelectedAtomInfoCheckBox.setToolTip("Show Atom Info")

def ToolTip_MoviePropertyManager(propMgr):
    """
    "ToolTip" text for widgets in the Movie Property Manager.
    """
    propMgr.frameNumberSpinBox.setToolTip("Advance to Frame")

    propMgr.movieLoop_checkbox.setToolTip("Loop Movie")

    propMgr.frameSkipSpinBox.setToolTip("Skip Frames")

    propMgr.fileOpenMovieAction.setToolTip("Open Movie")

    propMgr.fileSaveMovieAction.setToolTip("Save Movie")

    propMgr.moviePlayRevAction.setToolTip("Reverse")

    propMgr.moviePlayAction.setToolTip("Forward")

    propMgr.moviePauseAction.setToolTip("Pause")

    propMgr.movieMoveToEndAction.setToolTip("Last Frame")

    propMgr.movieResetAction.setToolTip("Reset Movie")

    propMgr.frameNumberSlider.setToolTip("Advance Frame")

def ToolTip_SequenceEditor(propMgr):
    """
    "ToolTip" text for widgets in the DNA Sequence Editor.
    """
    propMgr.loadSequenceButton.setToolTip("Load Sequence")

    propMgr.sequenceTextEdit.setToolTip("Edit Sequence")

    propMgr.saveSequenceButton.setToolTip("Save Sequence")

    propMgr.baseDirectionChoiceComboBox.setToolTip("Strand Directon")

    propMgr.findLineEdit.setToolTip("Find Sequence")

    propMgr.findPreviousToolButton.setToolTip("Find Previous")

    propMgr.findNextToolButton.setToolTip("Find Next")

    propMgr.replacePushButton.setToolTip("Replace")

    propMgr.sequenceTextEdit_mate.setToolTip("Mate Sequence")

def ToolTip_MovePropertyManager(propMgr):
    """
    "ToolTip" text for widgets in the Move Property Manager.
    """

    # Translate group box widgets 

    propMgr.translateComboBox.setToolTip("Translation Options")

    propMgr.transFreeButton.setToolTip("Unconstrained Translation")

    propMgr.transXButton.setToolTip("X Translation (X)")

    propMgr.transYButton.setToolTip("Y Translation (Y)")

    propMgr.transZButton.setToolTip("Z Translation (Z)")

    propMgr.transAlongAxisButton.setToolTip("Axial Translation/Rotation (A)")

    propMgr.moveFromToButton.setToolTip("Translate between two defined points")

    # By Delta XYZ widgets

    propMgr.moveDeltaXSpinBox.setToolTip("Delta X")

    propMgr.moveDeltaYSpinBox.setToolTip("Delta Y")

    propMgr.moveDeltaZSpinBox.setToolTip("Delta Z")

    propMgr.transDeltaPlusButton.setToolTip(
        "Move selection by + (plus) delta XYZ")

    propMgr.transDeltaMinusButton.setToolTip(
        "Move selection by - (minus) delta XYZ")

    # To XYZ Position widgets

    propMgr.moveXSpinBox.setToolTip("X Coordinate")

    propMgr.moveYSpinBox.setToolTip("Y Coordinate")

    propMgr.moveZSpinBox.setToolTip("Z Coordinate")

    propMgr.moveAbsoluteButton.setToolTip(
        "Move selection to absolute XYZ position")

    # Rotate group box widgets 

    propMgr.rotateComboBox.setToolTip("Rotate Options")

    # Free Drag widgets.

    propMgr.rotateFreeButton.setToolTip("Unconstrained Rotation")

    propMgr.rotateXButton.setToolTip("X Rotation (X)")

    propMgr.rotateYButton.setToolTip("Y Rotation (Y)")

    propMgr.rotateZButton.setToolTip("Z Rotation (Z)")

    propMgr.rotAlongAxisButton.setToolTip("Axial Translation/Rotation (A)")

    propMgr.rotateAsUnitCB.setToolTip("Rotate As Unit")

    # By Specified Angle widgets


    propMgr.rotateThetaSpinBox.setToolTip("Angle of rotation")

    propMgr.rotateThetaPlusButton.setToolTip("Rotate")

    propMgr.rotateThetaMinusButton.setToolTip("Rotate (minus)")

def ToolTip_QuteMolPropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the QuteMolX Property Manager.
    """
    propMgr.launchQuteMolButton.setToolTip("Launch QuteMolX")

    propMgr.axesCombobox.setToolTip("Render Axes")

    propMgr.basesCombobox.setToolTip("Render Bases")

def ToolTip_PartLibPropertyManager(propMgr) :
    """
    Add "What's This" text for widgets in the Part Library Property Manager.
    """
    propMgr.previewGroupBox.setToolTip("Preview Window")
    
    propMgr.partLibGroupBox.setToolTip("Part Library")
        

def ToolTip_PasteItemPropertyManager(propMgr) :
    """
    Add "What's This" text for widgets in the Paste Items Property Manager.
    """
    propMgr.previewGroupBox.setToolTip("Preview Window")
    
    propMgr.clipboardGroupBox.setToolTip("Clipboard")
    
def ToolTip_EditProteinDisplayStyle_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Edit DNA Display Style Property Manager.
    """
    return
    
def ToolTip_EditDnaDisplayStyle_PropertyManager(propMgr):
    """
    Add "What's This" text for widgets in the Edit DNA Display Style Property Manager.
    """
    propMgr.favoritesComboBox.setToolTip("List of Favorites")
    propMgr.dnaRenditionComboBox.setToolTip("Change DNA Rendition")
    propMgr.dnaComponentComboBox.setToolTip("Change Component Display Settings")
    propMgr.standLabelColorComboBox.setToolTip("Change Strand Label Color")
    propMgr.axisShapeComboBox.setToolTip("Change Axis Shape")
    propMgr.axisScaleDoubleSpinBox.setToolTip("Change Axis Scale")
    propMgr.axisColorComboBox.setToolTip("Change Axis Color")
    propMgr.axisEndingStyleComboBox.setToolTip("Change Axis Ending Style")
    propMgr.strandsShapeComboBox.setToolTip("Change Strands Shape")
    propMgr.strandsScaleDoubleSpinBox.setToolTip("Change Strands Scale")
    propMgr.strandsColorComboBox.setToolTip("Change Strands Color")
    propMgr.strandsArrowsComboBox.setToolTip("Change Strands Arrows")
    propMgr.strutsShapeComboBox.setToolTip("Change Struts Shape")
    propMgr.strutsScaleDoubleSpinBox.setToolTip("Change Struts Scale" )
    propMgr.strutsColorComboBox.setToolTip("Change Struts Color")
    propMgr.nucleotidesShapeComboBox.setToolTip("Change Nucleotides Shape")
    propMgr.nucleotidesScaleDoubleSpinBox.setToolTip("Change Nucleotides Scale")
    propMgr.nucleotidesColorComboBox.setToolTip("Change Nucleotides Color")
    propMgr.dnaStyleBasesDisplayLettersCheckBox.setToolTip("Display DNA Bases")
    return


def ToolTip_ColorScheme_PropertyManager(propMgr):
    """
    Add tooltip text for widgets in the Color Scheme Property Manager.
    """
    propMgr.favoritesComboBox.setToolTip("List of favorites")
    propMgr.backgroundColorComboBox.setToolTip("Change background color")
    propMgr.hoverHighlightingStyleComboBox.setToolTip("Change hover highlighting style")
    propMgr.hoverHighlightingColorComboBox.setToolTip("Change hover highlighting color") 
    propMgr.selectionStyleComboBox.setToolTip("Change selection style")
    propMgr.selectionColorComboBox.setToolTip("Change selection color")
    return

def ToolTip_LightingScheme_PropertyManager(propMgr):
    """
    Add tooltip text for widgets in the Lighting Scheme Property 
    Manager.
    """
    return
