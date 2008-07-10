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
        The NanoEngineer-1 <i>Build commands</i> for constructing structures 
        interactively.
        </p>""")
    return

def whatsThisTextForCommandToolbarInsertButton(button):
    """
    "What's This" text for the Insert button (menu).
    """
    button.setWhatsThis(
        """<b>Insert</b>
        <p>
        The NanoEngineer-1 <i>Insert commands</i> for inserting reference
        geometry, part files or other external structures into the current
        model.
        </p>""")
    return

def whatsThisTextForCommandToolbarToolsButton(button):
    """
    Menu of Build tools.
    """
    button.setWhatsThis(
        """<b>Tools</b>
        <p>
        This is a drop down Tool menu. Clicking on the Tool button will add
        these tools to the Command Toolbar.
        </p>""")
    return

def whatsThisTextForCommandToolbarMoveButton(button):
    """
    "What's This" text for the Move button (menu).
    """
    button.setWhatsThis(
        """<b>Move</b>
        <p>
       This is a drop down menu of Move commands. Clicking on the Move button
       will add these commands to the Command Toolbar.
        </p>""")
    return

def whatsThisTextForCommandToolbarSimulationButton(button):
    """
    "What's This" text for the Simulation button (menu).
    """
    button.setWhatsThis(
        """<b>Simulation</b>
        <p>
        This is a drop down menu containing Simulation modes (Run Dynamics
        and Play Movie). The menu also contains the associated simulation jigs.
        Clicking on the Simulation button will add these items to the Command
        Explorer
        </p>""")
    return

# Build command toolbars ####################

def whatsThisTextForAtomsCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Build Chunks Command Toolbar.
    
    @note: This is a placeholder function. Currenly, all the tooltip text is 
           defined in BuildAtoms_Command.py.
    """
    return

def whatsThisTextForProteinCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build Protein Command Toolbar
    """
    commandToolbar.exitProteinAction.setWhatsThis(
        """<b>Exit Protein</b>
        <p>
        Exits <b>Build Protein</b>.
        </p>""")
    
    commandToolbar.buildPeptideAction.setWhatsThis(
        """<b>Insert Peptide</b>
        <p>
        Insert a peptide into the 3D graphics area.
        </p>""")
    commandToolbar.displayProteinStyleAction.setWhatsThis(
        """<b>Edit (Protein Display) Style</b>
        <p>
        Edit the Protein Display Style settings used whenever the <b>Global Display
        Style</b> is set to <i>Protein</i>.
        </p>""")   
    
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
        """<b>Insert DNA</b>
        <p>
        Insert a double stranded (ds) DNA helix by clicking two
        points in the 3D graphics area.
        </p>""")
    
    commandToolbar.breakStrandAction.setWhatsThis(
        """<b>Break Strands</b>
        <p>
        Enters Break Strand Mode where left clicking on a bond between DNA
        pseudo-atoms breaks the bond. 
        </p>""")
    commandToolbar.joinStrandsAction.setWhatsThis(
        """<b>Join Strands</b>
        <p>
        Enters Join Strand Mode where strands may be joined by dragging and 
        dropping strand arrow heads on to their strand conjugate i.e. 3' on to
        5' and vice versa. 
        </p>""")
    commandToolbar.dnaOrigamiAction.setWhatsThis(
        """<b>Origami</b>
        <p>
        Enters DNA Origami mode- currently not implemented 
        </p>""")
    
    commandToolbar.convertPAM3to5Action.setWhatsThis(
        """<b>Convert PAM3 to PAM5</b>
        <p>
        Converts the selected DNA from PAM3 to PAM5. 
        </p>""")
    
    commandToolbar.convertPAM5to3Action.setWhatsThis(
        """<b>Convert PAM5 to PAM3</b>
        <p>
        Converts the selected DNA from PAM5 to PAM3. 
        </p>""")
    
    commandToolbar.orderDnaAction.setWhatsThis(
        """<b>Order DNA</b>
        <p>
        Produces a text file containing the DNA strands and their assigned base
        pair sequences for the all strands in the <b>selected</b> node. 
        </p>""")
        
    commandToolbar.editDnaDisplayStyleAction.setWhatsThis(
        """<b>Edit (DNA Display) Style</b>
        <p>
        Edit the DNA Display Style settings used whenever the <b>Global Display
        Style</b> is set to <i>DNA Cylinder</i>. These settings also apply
        to DNA strands and segments that have had their display style set
        to <i>DNA Cylinder</i>.
        </p>""")    
    
    commandToolbar.makeCrossoversAction.setWhatsThis(
        """<b>Make Crossovers</b>
        <p>
        Enters the interative <b>Make Crossovers</b> command.<br>
        To create crossovers, select the DNA Segments to be searched for 
        potential crossover sites. The crossover sites get updated as you, 
        for instance, rotate a DNA segment around its axis or translate it etc. 
        The crossover sites are shown as transparent green spheres. 
        Clicking on a white colored cylinder pair (if one exists) in the 
        3D-Workspace creates that crossover. 
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
        Displays the Insert Nanotube Property Manager
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
