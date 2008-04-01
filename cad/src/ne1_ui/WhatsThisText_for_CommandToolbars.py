# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_CommandToolbars.py

This file provides functions for setting the "What's This" text
for widgets (typically QActions) in the Command Toolbar.

@author: Mark
@version:$Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""

# Try to keep this list in order (by appearance in Command Toolbar). --Mark

# Command Toolbar Menus (i.e. Build, Tools, Move and Simulation ######

def whatsThisTextForCommandToolbarBuildButton(button):
    """
    "What's This" text for the Build button (menu).
    """
    button.setWhatsThis(
        """<b>Build</b>
        <p>
        whats this text for the Build button (menu).
        </p>""")
    return

def whatsThisTextForCommandToolbarToolsButton(button):
    """
    "What's This" text for the Tools button (menu).
    """
    button.setWhatsThis(
        """<b>Tools</b>
        <p>
        whats this text for the Tools button (menu).
        </p>""")
    return

def whatsThisTextForCommandToolbarMoveButton(button):
    """
    "What's This" text for the Move button (menu).
    """
    button.setWhatsThis(
        """<b>Move</b>
        <p>
        whats this text for the Move button (menu).
        </p>""")
    return

def whatsThisTextForCommandToolbarSimulationButton(button):
    """
    "What's This" text for the Simulation button (menu).
    """
    button.setWhatsThis(
        """<b>Simulation</b>
        <p>
        whats this text for Simulation button (menu).
        </p>""")
    return

# Build command toolbars ####################

def whatsThisTextForAtomsCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Build Atoms Command Toolbar.
    
    @note: This is a placeholder function. Currenly, all the tooltip text is 
           defined in BuildAtoms_Command.py.
    """
    return

def whatsThisTextForDnaCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build DNA Command Toolbar
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
    "What's This" text for widgets in the Build Nanotube Command Toolbar.
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
    "What's This" text for widgets in the Move Command Toolbar.
    """
    return

def whatsThisTextForMovieCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Movie Command Toolbar.
    """
    return
