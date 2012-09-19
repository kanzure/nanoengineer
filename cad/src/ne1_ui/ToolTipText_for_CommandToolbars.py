# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
ToolTipText_for_CommandToolbars.py

This file provides functions for setting the "Tooltip" text
for widgets (typically QActions) in the Command Toolbar.

@author: Mark
@version:$Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""

# Try to keep this list in order (by appearance in Command Toolbar). --Mark

# Build command toolbars ####################

def toolTipTextForAtomsCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Build Atoms Command Toolbar.

    @note: This is a placeholder function. Currenly, all the tooltip text is
           defined in BuildAtoms_Command.py.
    """
    return

def toolTipTextForDnaCommandToolbar(commandToolbar):
    """
    "ToolTip" text for the Build DNA Command Toolbar
    """
    commandToolbar.dnaDuplexAction.setToolTip("Insert DNA")
    commandToolbar.breakStrandAction.setToolTip("Break Strands")
    commandToolbar.joinStrandsAction.setToolTip("Join Strands")
    commandToolbar.dnaOrigamiAction.setToolTip("Origami")
    commandToolbar.convertDnaAction.setToolTip("Convert DNA")
    commandToolbar.orderDnaAction.setToolTip("Order DNA")
    commandToolbar.editDnaDisplayStyleAction.setToolTip("Edit DNA Display Style")

    return

def toolTipTextForProteinCommandToolbar(commandToolbar):
    """
    "ToolTip" text for the Build Protein Command Toolbar
    """
    commandToolbar.modelProteinAction.setToolTip("Model Protein")
    commandToolbar.simulateProteinAction.setToolTip("Simulate Protein using Rosetta")

    commandToolbar.buildPeptideAction.setToolTip("Insert Peptide")
    commandToolbar.compareProteinsAction.setToolTip("Compare Proteins")
    commandToolbar.displayProteinStyleAction.setToolTip("Edit Protein Display Style")

    commandToolbar.rosetta_fixedbb_design_Action.setToolTip("Fixed Backbone Protein Sequence Design")
    commandToolbar.rosetta_backrub_Action.setToolTip("Backrub Motion")
    commandToolbar.editResiduesAction.setToolTip("Edit Residues")
    commandToolbar.rosetta_score_Action.setToolTip("Compute Rosetta Score")
    return

def toolTipTextForNanotubeCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Build Nanotube Command Toolbar.
    """
    commandToolbar.insertNanotubeAction.setToolTip("Insert Nanotube")
    return

def toolTipTextForCrystalCommandToolbar(commandToolbar):
    """
    "Tool Tip" text for widgets in the Build Crystal Command Toolbar.
    """
    commandToolbar.polygonShapeAction.setToolTip( "Polygon (P)")
    commandToolbar.circleShapeAction.setToolTip( "Circle (C)")
    commandToolbar.squareShapeAction.setToolTip( "Square (S)")
    commandToolbar.rectCtrShapeAction.setToolTip( "Rectangular (R)")
    commandToolbar.rectCornersShapeAction.setToolTip( "Rectangle Corners (Shift+R)")
    commandToolbar.triangleShapeAction.setToolTip( "Triangle (T)")
    commandToolbar.diamondShapeAction.setToolTip( "Diamond (D)")
    commandToolbar.hexagonShapeAction.setToolTip( "Hexagon (H)")
    commandToolbar.lassoShapeAction.setToolTip( "Lasso (L)")
    return

# Move command toolbar ####################

def toolTipTextForMoveCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Move Command Toolbar.
    """
    return

def toolTipTextForMovieCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Movie Command Toolbar.
    """
    return