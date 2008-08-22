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
    commandToolbar.convertPAM3to5Action.setToolTip("Convert PAM3 to PAM5")
    commandToolbar.convertPAM5to3Action.setToolTip("Convert PAM5 to PAM3")
    commandToolbar.orderDnaAction.setToolTip("Order DNA")
        
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