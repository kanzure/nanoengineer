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
    "Tool Tip" text for widgets in the Crystal (Cookie) Property Manager.
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

    propMgr.torqueDblSpinBox.setToolTip("Motor Torque")

    propMgr.initialSpeedDblSpinBox.setToolTip("Initial Speed")

    propMgr.finalSpeedDblSpinBox.setToolTip("Final Speed")

    propMgr.dampersCheckBox.setToolTip("Turn Motor Dampers ON/OFF")

    propMgr.enableMinimizeCheckBox.setToolTip("Motor is Enabled During" \
                                              " Minimizations")

    propMgr.motorLengthDblSpinBox.setToolTip("Set Motor Length")

    propMgr.motorRadiusDblSpinBox.setToolTip("Set Motor Radius")

    propMgr.spokeRadiusDblSpinBox.setToolTip("Set Spoke Radius")

    propMgr.colorPushButton.setToolTip("Change Color")

    propMgr.directionPushButton.setToolTip("Rotation Direction")


def ToolTip_LinearMotorPropertyManager(propMgr):

    """
    Tool Tip text for widgets in the Linear Motor Property Manager.
    """

    propMgr.forceDblSpinBox.setToolTip("Motor Force")

    propMgr.enableMinimizeCheckBox.setToolTip("Motor is Enabled During" \
                                              " Minimizations")

    propMgr.stiffnessDblSpinBox.setToolTip("Stiffness")

    propMgr.motorLengthDblSpinBox.setToolTip("Motor Length")

    propMgr.motorWidthDblSpinBox.setToolTip("Motor Width")

    propMgr.spokeRadiusDblSpinBox.setToolTip("Motor Radius")

    propMgr.colorPushButton.setToolTip("Change Color")

    propMgr.directionPushButton.setToolTip("Motor Direction")  

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

def ToolTip_DnaDuplexPropertyManager(propMgr):
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

def ToolTip_BuildAtomsPropertyManager(propMgr):
    """
    "ToolTip" text for widgets in the QuteMolX Property Manager.
    """
    propMgr.selectionFilterCheckBox.setToolTip("Selection Filter")

    propMgr.filterlistLE.setToolTip("Selection Filter Field")

    propMgr.autoBondCheckBox.setToolTip("Autobond ON/OFF")

    propMgr.waterCheckBox.setToolTip("Water ON/OFF")

    propMgr.highlightingCheckBox.setToolTip("Highlighting ON/OFF")

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

    propMgr.sequenceTextEdit_mate.setToolTip("Mate")

def ToolTip_MovePropertyManager(propMgr):
    """
    "ToolTip" text for widgets in the Move Property Manager.
    """

    # Translate group box widgets 

    propMgr.translateComboBox.setToolTip("Translation Options")

    propMgr.transFreeButton.setToolTip("Unconstrained Translation")

    propMgr.transXButton.setToolTip("X Translation")

    propMgr.transYButton.setToolTip("Y Translation")

    propMgr.transZButton.setToolTip("Z Translation")

    propMgr.transAlongAxisButton.setToolTip("Axial Translation/Rotation")

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

    propMgr.rotateXButton.setToolTip("X Rotation")

    propMgr.rotateYButton.setToolTip("Y Rotation")

    propMgr.rotateZButton.setToolTip("Z Rotation")

    propMgr.rotAlongAxisButton.setToolTip("Axial Translation/Rotation")

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
        

