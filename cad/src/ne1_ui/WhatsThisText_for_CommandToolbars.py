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
    "What's This" text for widgets in the Build Atoms Command Toolbar.
    
    @note: This is a placeholder function. Currenly, all the tooltip text is 
           defined in BuildAtoms_Command.py.
    """
    return

def whatsThisTextForProteinCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build Protein Command Toolbar
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Protein</b>
        <p>
        Exits <b>Build Protein</b>.
        </p>""")
    
    commandToolbar.modelProteinAction.setWhatsThis(
        """<b>Model Protein</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/BuildPeptide.png\"><br> 
        Enter protein modeling mode. Modeling options are displayed to the right
        in the flyout toolbar.
        </p>""")
    
    commandToolbar.simulateProteinAction.setWhatsThis(
        """<b>Simulate Protein with Rosetta</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Simulate.png\"><br> 
        Enter protein simulation mode using Rosetta. Rosetta is a collection of
        computational tools for the prediction and design of protein structures 
        and protein-protein interactions. A subset of Rosetta simulation options
        are available in NanoEngineer-1, including:
        <lo>
        Option 1
        Option 2
        </lo>
        </p>
        <p><a href=Rosetta_for_NanoEngineer-1> 
        Click here for more information about Rosetta for NanoEngineer-1</a>
        </p>""")
    
    commandToolbar.buildPeptideAction.setWhatsThis(
        """<b>Insert Peptide</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/InsertPeptide.png\"><br> 
        Insert a peptide chain by clicking two endpoints 
        in the 3D graphics area. The user can also specify different
        conformation options (i.e. Alpha helix, Beta sheet, etc.) in the 
        property manager.
        </p>""")
    
    commandToolbar.editRotamersAction.setWhatsThis(
        """<b>Edit Rotamers</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Rotamers.png\"><br> 
        Edit rotamers in a peptide chain.
        </p>""")
    
    commandToolbar.compareProteinsAction.setWhatsThis(
        """<b>Compare Proteins</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Compare.png\"><br> 
        Select two protein structures and compare them visually.
        </p>""")
    
    commandToolbar.displayProteinStyleAction.setWhatsThis(
        """<b>Edit (Protein Display) Style</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/EditProteinDisplayStyle.png\"><br> 
        Edit the Protein Display Style settings used whenever the 
        <b>Global Display Style</b> is set to <i>Protein</i>.
        </p>""")
    
    commandToolbar.rosetta_fixedbb_design_Action.setWhatsThis(
        """<b>Fixed Backbone Protein Sequence Design</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/FixedBackbone.png\"><br> 
        Design an optimized fixed backbone protein sequence using Rosetta.
        </p>""")
    
    commandToolbar.rosetta_backrub_Action.setWhatsThis(
        """<b>Backrub Motion</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Backrub.png\"><br> 
        Design an optimized backbone protein sequence using Rosetta 
        with backrub motion allowed.
        </p>""")
    
    commandToolbar.editResiduesAction.setWhatsThis(
        """<b>Edit Residues</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Residues.png\"><br> 
        Provides an interface to edit residues so that Rosetta can predict
        the optimized sequence of an initial sequence (peptide chain).
        </p>""")
    
    commandToolbar.rosetta_score_Action.setWhatsThis(
        """<b>Compute Rosetta Score</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Score.png\"><br> 
        Produce the Rosetta score, which is useful for predicting errors in a 
        peptide/protein structure. </p>
        <p>
        The Rosetta scoring function is an all-atom force field that focuses 
        on short-range interactions (i.e., van der Waals packing, hydrogen 
        bonding and desolvation) while neglecting long-range electrostatics. 
        </p>""")
    
    return


def whatsThisTextForDnaCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build DNA Command Toolbar
    """
    commandToolbar.exitModeAction.setWhatsThis(
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
    
    commandToolbar.convertDnaAction.setWhatsThis(
        """<b>Convert DNA </b>
        <p>
        Converts the selected DNA from PAM3 to PAM5 or PAM5 to PAM3.
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
        Creates crossovers interactively between two or more selected DNA 
        segments.</p>
        <p>
        To create crossovers, select the DNA segments to be searched for 
        potential crossover sites. Crossover sites, displayed as transparent
        green spheres on the strands, are updated as you move (rotate or 
        translate) a DNA segment. After you are finished moving a DNA segment, 
        crossover sites are shown as a pair of white cylinders.    
        Clicking on a highlighted crossover site creates the crossover.
        </p>""") 
    
    return

def whatsThisTextForNanotubeCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Build Nanotube Command Toolbar.
    """
    commandToolbar.exitModeAction.setWhatsThis(
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
    "Tool Tip" text for widgets in the Build Crystal (crystal) Command Toolbar.
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
