# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_PropertyManagers.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in all NE1 Property Managers only. 

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text 
for widgets in the Main Window.

@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

"""

def whatsThis_DnaDuplexPropertyManager(propMgr):
    """
    Whats This text for the DnaDuplex Property Manager
    @see: B{DnaDuplexPropertyManager._addWhatsThisText}
    """
    
    propMgr.conformationComboBox.setWhatsThis(
        """"<b>Conformation</b>
        <p>DNA exists in several possible conformations,
        with A-DNA, B-DNA, and Z-DNA being the most common. <br>
        Only B-DNA is currently supported in "\
        NanoEngineer-1.
        </p>""")
    
    return # End of whatsThis_DnaDuplexPropertyManager
        
def whatsThis_MovePropertyManager(propMgr):
    """
    U{What's This text for widgets in the Move Property Manager.
    """

    # Translate group box widgets ################################

    propMgr.translateComboBox.setWhatsThis(
        """<b>Translation Options</b>
        <p>This menu provides different options for translating the
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
        <p>Translates the selection freely within the plane of the screen.
        </p>""")

    propMgr.transXButton.setWhatsThis(
        """<b>X Translation</b>
        <p>Constrains translation of the selection to the X axis.
        </p>""")

    propMgr.transYButton.setWhatsThis(
        """<b>Y Translation</b>
        <p>Constrains translation of the selection to the Y axis.
        </p>""")

    propMgr.transZButton.setWhatsThis(
        """<b>Z Translation</b>
        <p>Constrains translation of the selection to the Z axis.
        </p>""")

    propMgr.transAlongAxisButton.setWhatsThis(
        """<b>Axial Translation/Rotation</b>
        <p>Constrains both translation and rotation of the selection along
        the central axis of the selected object(s). This is especially
        useful for translating and rotating DNA duplexes along their
        own axis.
        </p>""")

    # By Delta XYZ widgets

    propMgr.moveDeltaXSpinBox.setWhatsThis(
        """<b>Delta X</b>
        <p>The X offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveDeltaYSpinBox.setWhatsThis(
        """<b>Delta Y</b>
        <p>The Y offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveDeltaZSpinBox.setWhatsThis(
        """<b>Delta Z</b>
        <p>The Z offset distance the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.transDeltaPlusButton.setWhatsThis(
        """<b>Delta +</b>
        <p>Moves the current selection by an offset
        specified by the Delta X, Y and Z spinboxes.
        </p>""")

    propMgr.transDeltaPlusButton.setToolTip(
        "Move selection by + (plus) delta XYZ")

    propMgr.transDeltaMinusButton.setWhatsThis(
        """<b>Delta -</b>
        <p>Moves the current selection by an offset opposite of that 
        specified by the Delta X, Y and Z spinboxes.
        </p>""")

    propMgr.transDeltaMinusButton.setToolTip(
        "Move selection by - (minus) delta XYZ")

    # To XYZ Position widgets

    propMgr.moveXSpinBox.setWhatsThis(
        """<b>X</b>
        <p>The X coordinate the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveYSpinBox.setWhatsThis(
        """<b>Y</b>
        <p>The Y coordinate the selection is moved when 
        clicking the +/- Delta buttons.
        </p>""")

    propMgr.moveZSpinBox.setWhatsThis(
        """<b>Z</b>
        <p>The Z coordinate the selection is moved when 
        clicking the <b>Move to Absolute Position</b> button.
        </p>""")

    propMgr.moveAbsoluteButton.setWhatsThis(
        """<b>Move to Absolute Position</b>
        <p>Moves the current selection to the position
        specified by the X, Y and Z spinboxes. The selection's centroid
        is used compute how the selection is moved.
        </p>""")

    propMgr.moveAbsoluteButton.setToolTip(
        "Move selection to absolute XYZ position")

    # Rotate group box widgets ############################

    propMgr.rotateComboBox.setWhatsThis(
        """<b>Rotate Options</b>
        <p>This menu provides different options for rotating the
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
        <p>Rotates the selection freely about its centroid.
        </p>""")

    propMgr.rotateXButton.setWhatsThis(
        """<b>X Rotation</b>
        <p>Constrains rotation of the selection to the X axis.
        </p>""")

    propMgr.rotateYButton.setWhatsThis(
        """<b>Y Rotation</b>
        <p>Constrains rotation of the selection to the Y axis.
        </p>""")

    propMgr.rotateZButton.setWhatsThis(
        """<b>Z Rotation</b>
        <p>Constrains rotation of the selection to the Z axis.
    </p>""")

    propMgr.rotAlongAxisButton.setWhatsThis(
        """<b>Axial Translation/Rotation</b>
        <p>Constrains both translation and rotation of the selection along
        the central axis of the selected object(s). This is especially
        useful for translating and rotating DNA duplexes along their
        own axis.
        </p>""")

    propMgr.rotateAsUnitCB.setWhatsThis(
        """<b>Rotate as unit</b>
        <p>When <b>checked</b>, the selection is rotated as a unit about its
        collective centroid.<br>
        When <b>unchecked</b>, the selected objects are rotated about their 
        own individual centroids.
        </p>""")

    # By Specified Angle widgets

    propMgr.rotateXButton.setWhatsThis(
        """<b>Rotate about X axis</b>
        <p>Constrains rotation about the X axis.
        </p>""")

    propMgr.rotateXButton.setToolTip(
        "Rotate about X axis")

    propMgr.rotateYButton.setWhatsThis(
        """<b>Rotate about Y axis</b>
        <p>Constrains rotation about the Y axis.
        </p>""")

    propMgr.rotateYButton.setToolTip(
        "Rotate about Y axis")

    propMgr.rotateZButton.setWhatsThis(
        """<b>Rotate about Z axis</b>
        <p>Constrains rotation about the Z axis.
        </p>""")

    propMgr.rotateZButton.setToolTip(
        "Rotate about Z axis")

    propMgr.rotateThetaSpinBox.setWhatsThis(
        """<b>Rotation angle</b>
        <p>Specifies the angle of rotation.
        </p>""")

    propMgr.rotateThetaSpinBox.setToolTip(
        "Angle of rotation")

    # These next two aren't working. 
    # I don't understand why not. Mark 2007-06-25.
    propMgr.rotateThetaPlusButton.setWhatsThis(
        """<b>Rotate</b>
        <p>Rotates the selection by the specified angle.
        </p>""")

    propMgr.rotateThetaMinusButton.setWhatsThis(
        """<b>Rotate (minus)</b>
        <p>Rotates the selection by the specified angle 
        (in the opposite direction).
        </p>""")
    
    return # End of whatsThis_DnaDuplexPropertyManager