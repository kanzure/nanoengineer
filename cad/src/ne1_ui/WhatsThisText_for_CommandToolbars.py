# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_CommandToolbars.py

This file provides functions for setting the "What's This" text
for widgets (typically QActions) in the Command Toolbar.

@author: Mark
@version:$Id:$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""

# Try to keep this list in order (by appearance in Command Toolbar). --Mark

# Build command toolbars ####################

def whatsThisTextForAtomsCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Build Atoms Command Toolbar.
    
    @note: This is a placeholder function. Currenly, all the tooltip text is 
           defined in BuildAtoms_Command.py.
    """
    return

def whatsThisTextForDnaCommandToolbar(commandToolbar):
    """
    "ToolTip" text for the Build DNA Command Toolbar
    """
    commandToolbar.exitDnaAction.setWhatsThis(
        """<b>Exit DNA</b>
        <p>
        Exits <b>Build DNA</b>.
        </p>""")
    
    commandToolbar.dnaDuplexAction.setWhatsThis(
        """<b>Insert dsDNA</b>
        <p>
        Insert a double stranded (ds) DNA helix by clicking two
        points in the 3D graphics area.
        </p>""")
    
    commandToolbar.breakStrandAction.setWhatsThis(
        """<b>Break Strands</b>
        <p>
        whats this text here
        </p>""")
    commandToolbar.joinStrandsAction.setWhatsThis(
        """<b>Join Strands</b>
        <p>
        whats this text here
        </p>""")
    commandToolbar.dnaOrigamiAction.setWhatsThis(
        """<b>Origami</b>
        <p>
        whats this text here
        </p>""")
    
    commandToolbar.orderDnaAction.setWhatsThis(
        """<b>Order DNA</b>
        <p>
        whats this text here
        </p>""")
        
    return

def whatsThisTextForNanotubeCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Build Nanotube Command Toolbar.
    """
    commandToolbar.exitNanotubeAction.setWhatsThis(
        """<b>Exit Nanotube</b>
        <p>
        Exits <b>Build Nanotube</b>.
        </p>""")
    
    commandToolbar.insertNanotubeAction.setWhatsThis(
        """<b>Insert Nanotube</b>
        <p>
        whats this text here
        </p>""")
    return

def whatsThisTextForCrystalCommandToolbar(commandToolbar):
    """
    "Tool Tip" text for widgets in the Build Crystal (Cookie) Command Toolbar.
    """
    return

# Move command toolbar ####################

def whatsThisTextForMoveCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Move Command Toolbar.
    """
    return

def whatsThisTextForMovieCommandToolbar(commandToolbar):
    """
    "ToolTip" text for widgets in the Movie Command Toolbar.
    """
    return
