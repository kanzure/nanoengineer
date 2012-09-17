# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
WhatsThisText_for_CommandToolbars.py

This file provides functions for setting the "What's This" text
for widgets (typically QActions) in the Command Toolbar.

@author: Mark
@version:$Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.whatsthis_utilities import fix_whatsthis_text_and_links

# Try to keep this list in order (by appearance in Command Toolbar). --Mark

# Command Toolbar Menus (i.e. Build, Tools, Move and Simulation ######

def whatsThisTextForCommandToolbarBuildButton(button):
    """
    "What's This" text for the Build button (menu).
    """
    button.setWhatsThis(
        """<b>Build</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/ControlArea/Build.png\"><br>
        The <b>Build Command Set</b> for modeling and editing structures
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
        <img source=\"ui/actions/Command Toolbar/ControlArea/Insert.png\"><br>
        The <b>Insert Command Set</b> which includes commands for inserting
        various things into the current part.
        </p>""")
    return

def whatsThisTextForCommandToolbarToolsButton(button):
    """
    Menu of Build tools.
    """
    button.setWhatsThis(
        """<b>Tools</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/ControlArea/Tools.png\"><br>
        The <b>Tools Command Set</b> which includes specialized tools for
        model editing.
        </p>""")
    return

def whatsThisTextForCommandToolbarMoveButton(button):
    """
    "What's This" text for the Move button (menu).
    """
    button.setWhatsThis(
        """<b>Move</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/ControlArea/Move.png\"><br>
        The <b>Move Command Set</b> which includes specialized rotation and
        translation commands that operate on the current selection.
        </p>""")
    return

def whatsThisTextForCommandToolbarSimulationButton(button):
    """
    "What's This" text for the Simulation button (menu).
    """
    button.setWhatsThis(
        """<b>Simulation</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/ControlArea/Simulation.png\"><br>
        The <b>Simulation Command Set</b> which includes commands for setting up,
        launching and playing back movies of molecular dynamics simulations.
        </p>""")
    return

# Build command toolbars ####################

def whatsThisTextForAtomsCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Build Atoms Command Toolbar.

    @note: This is a placeholder function. Currenly, all the tooltip text is
           defined in BuildAtoms_Command.py.
    """

    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Atoms</b>
        <p>
        Exits the <b>Build Atoms</b> command set.
        </p>""")

    commandToolbar.atomsToolAction.setWhatsThis(
        """<b>Atoms Tool</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/AtomsTool.png\"><br>
        Activates <i>Atoms Tool Mode</i> for depositing and/or selecting atoms.
        Double-click to insert a new atom into the model by itself.
        Single-click on <a href=Bondpoints>bondpoints</a> to insert and bond
        a new atom to an existing atom.
        </p>""")

    commandToolbar.transmuteAtomsAction.setWhatsThis(
        """<b>Transmute Atoms</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/TransmuteAtoms.png\"><br>
        Transmutes the selected atoms to the active element type. The active
        element type in set using the <b>Atom Chooser</b> in the
        <a href=Property_Manager>property manager</a>.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> Use the <b>Selection Filter</b> to limit selects to
        specific atom types in the <a href=Graphics_Area>raphics area</a>
        <a href=Command_Toolbar>command toolbar</a>.
        </p>""")

    commandToolbar.bondsToolAction.setWhatsThis(
        """<b>Bonds Tool</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/BondsTool.png\"><br>
        Enters <i>Bonds Tool Mode</i> for changing bonds (i.e. the bond order)
        or deleting bonds. Singe-clicking bonds will transmute them into the
        active bond type. The active bond type in set by selecting one of
        the bond types (i.e. single, double, triple, etc.) in the flyout area
        of the <a href=Command_Toolbar>command toolbar</a>.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds at the same
        time. To do this, select all the atoms with bonds you want to transmute,
        then click on the bond type in the
        <a href=Command_Toolbar>command toolbar</a>.
        </p>""")

    commandToolbar.bond1Action.setWhatsThis(
        """<b>Single Bond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/SingleBond.png\"><br>
        Sets the active bond type to <b>single</b>. Singe-clicking a
        highlighted bond transmutes it into a single bond.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds into single
        bonds at the same time. To do this, select all the atoms with bonds
        you want to transmute, then click on this button. <b>Note:</b> <i>Only
        selected atoms with bonds between them will be transmuted.</i>
        </p>""")

    commandToolbar.bond2Action.setWhatsThis(
        """<b>Double Bond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/DoubleBond.png\"><br>
        Sets the active bond type to <b>double</b>. Singe-clicking a
        highlighted bond transmutes it into a double bond.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds into double
        bonds at the same time. To do this, select all the atoms with bonds
        you want to transmute, then click on this button. <b>Note:</b> <i>Only
        selected atoms with bonds between them will be transmuted.</i>
        </p>""")

    commandToolbar.bond3Action.setWhatsThis(
        """<b>Triple Bond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/TripleBond.png\"><br>
        Sets the active bond type to <b>triple</b>. Singe-clicking a
        highlighted bond transmutes it into a triple bond.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds into triple
        bonds at the same time. To do this, select all the atoms with bonds
        you want to transmute, then click on this button. <b>Note:</b> <i>Only
        selected atoms with bonds between them will be transmuted.</i>
        </p>""")

    commandToolbar.bondaAction.setWhatsThis(
        """<b>Aromatic Bond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/AromaticBond.png\"><br>
        Sets the active bond type to <b>aromatic</b>. Singe-clicking a
        highlighted bond transmutes it into an aromatic bond.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds into aromatic
        bonds at the same time. To do this, select all the atoms with bonds
        you want to transmute, then click on this button. <b>Note:</b> <i>Only
        selected atoms with bonds between them will be transmuted.</i>
        </p>""")

    commandToolbar.bondgAction.setWhatsThis(
        """<b>Graphitic Bond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/GraphiticBond.png\"><br>
        Sets the active bond type to <b>graphitic</b>. Singe-clicking a
        highlighted bond transmutes it into a graphitic bond.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> It is possible to transmute multiple bonds into graphitic
        bonds at the same time. To do this, select all the atoms with bonds
        you want to transmute, then click on this button. <b>Note:</b> <i>Only
        selected atoms with bonds between them will be transmuted.</i>
        </p>""")

    commandToolbar.cutBondsAction.setWhatsThis(
        """<b>Cut Bonds</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildAtoms/CutBonds.png\"><br>
        Activates cut bonds mode. Singe-clicking a highlighted bond deletes it.
        </p>""")

    # Convert all "img" tags in the button's "What's This" text
    # into abs paths (from their original rel paths).
    # Partially fixes bug 2943. --mark 2008-12-07
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroup)
    fix_whatsthis_text_and_links(commandToolbar.bondToolsActionGroup)
    return

def whatsThisTextForProteinCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build Protein Command Toolbar
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Protein</b>
        <p>
        Exits the <b>Build Protein</b> command set.
        </p>""")

    commandToolbar.modelProteinAction.setWhatsThis(
        """<b>Model Protein</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/ModelProtein.png\"><br>
        Enter protein modeling mode. Protein modeling sub-commands are
        displayed to the right in the flyout area of the
        <a href=Command_Toolbar>command toolbar</a>.
        </p>""")

    commandToolbar.simulateProteinAction.setWhatsThis(
        """<b>Simulate Protein with Rosetta</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/Simulate.png\"><br>
        Enter protein simulation mode using Rosetta. Rosetta simulation
        sub-commands are displayed to the right in the flyout area of the
        <a href=Command_Toolbar>command toolbar</a>.</p>
        <p>
        Rosetta is a collection of computational tools for the prediction and
        design of protein structures and protein-protein interactions.</p>
        <p>
        <a href=Rosetta_for_NanoEngineer-1>
        Click here for more information about Rosetta for NanoEngineer-1</a>
        </p>""")

    commandToolbar.buildPeptideAction.setWhatsThis(
        """<b>Insert Peptide</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildProtein/InsertPeptide.png\"><br>
        Insert a peptide chain by clicking two endpoints in the
        <a href=Graphics_Area>graphics area</a>. The user can also specify
        different conformation options (i.e. Alpha helix, Beta sheet, etc.)
        in the <a href=Property_Manager>property manager</a>.
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
        <b>Global Display Style</b> is set to <b>Protein</b>.
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

    # Convert all "img" tags in the button's "What's This" text
    # into abs paths (from their original rel paths).
    # Partially fixes bug 2943. --mark 2008-12-07
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroup)
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroupForModelProtein)
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroupForSimulateProtein)
    return


def whatsThisTextForDnaCommandToolbar(commandToolbar):
    """
    "What's This" text for the Build DNA Command Toolbar
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit DNA</b>
        <p>
        Exits the <b>Build DNA</b> command set.
        </p>""")

    commandToolbar.dnaDuplexAction.setWhatsThis(
        """<b>Insert DNA</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/InsertDna.png\"><br>
        Insert a DNA duplex by clicking two endpoints in the graphics area.
        </p>""")

    commandToolbar.breakStrandAction.setWhatsThis(
        """<b>Break Strands</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/BreakStrand.png\"><br>
        This command provides an interactive mode where the user can
        break strands by clicking on a bond in a DNA strand. </p>
        <p>
        You can also join strands while in this command by dragging and
        dropping strand arrow heads onto their strand conjugate
        (i.e. 3' on to 5' and vice versa). </p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> Changing the <b>Global display style</b> to <b>CPK</b>
        results in faster interactive graphics while in this command, especially
        for large models.
        </p>""")

    commandToolbar.joinStrandsAction.setWhatsThis(
        """<b>Join Strands</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/JoinStrands.png\"><br>
        This command provides an interactive mode where the user can
        join strands by dragging and dropping strand arrow heads onto their
        strand conjugate (i.e. 3' on to 5' and vice versa). </p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> Changing the <b>Global display style</b> to <b>CPK</b>
        results in faster interactive graphics while in this command, especially
        for large models.
        </p>""")

    commandToolbar.convertDnaAction.setWhatsThis(
        """<b>Convert DNA </b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/ConvertDna.png\"><br>
        Converts the selected DNA from PAM3 to PAM5 or PAM5 to PAM3. The only
        reason to convert to PAM5 is to get more accurate minimizations of DNA
        nanostructures.</p>
        <p>
        Here is the protocol for producing more accurate minimizations:<br>
        1. Make sure the current model is saved.
        2. Select <b>File > Save As...</b> to save the model under a new name (i.e. <i>model_name</i>_minimized).<br>
        3. Select <b>Build > DNA > Convert</b> to convert the entire model from PAM3 to PAM5.<br>
        4. Select <b>Tools > Minimize Energy</b>.<br>
        5. In the Minimize Energy dialog, select <b>GROMACS with ND1 force field</b> as the Physics engine.<br>
        6. Click the <b>Minimize Energy</b> button.<br>
        7. After minimize completes, convert from PAM5 to PAM3.</p>
        <p>
        Next, visually inspect the model for structural distortions such as
        puckering, warping, or other unwanted strained areas that will require
        model changes to correct. Model changes should be made in a version
        of the model that hasn't been minimized. You can either click
        <b>Edit > Undo</b> or save this model and reopen the previous
        version.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> Changing the <b>Global display style</b> to <b>CPK</b> or
        <b>DNA Cylinder</b> may make the model easier to visually inspect.</p>
        <p>
        <a href=PAM3_and_PAM5_Model_Descriptions>Click here for a technical
        overview of the NanoEngineer-1 PAM3 and PAM5 reduced models.</a>
        </p>""")

    commandToolbar.orderDnaAction.setWhatsThis(
        """<b>Order DNA</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/OrderDna.png\"><br>
        Produces a comma-separated value (.CSV) text file containing all
        DNA strand sequences in the model.</p>
        <p>
        <img source=\"ui/whatsthis/HotTip.png\"><br>
        <b>Hot Tip:</b> This file can be used to order
        oligos from suppliers of custom oligonucleotides such as
        Integrated DNA Technologies and Gene Link.
        </p>""")

    commandToolbar.editDnaDisplayStyleAction.setWhatsThis(
        """<b>Edit (DNA Display) Style</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/EditDnaDisplayStyle.png\"><br>
        Edit the DNA Display Style settings used whenever the <b>Global Display
        Style</b> is set to <b>DNA Cylinder</b>. These settings also apply
        to DNA strands and segments that have had their display style set
        to <b>DNA Cylinder</b>.
        </p>""")

    commandToolbar.makeCrossoversAction.setWhatsThis(
        """<b>Make Crossovers</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildDna/MakeCrossovers.png\"><br>
        Creates crossovers interactively between two or more selected DNA
        segments.</p>
        <p>
        To create crossovers, select the DNA segments to be searched for
        potential crossover sites. Transparent green spheres indicating
        potential crossover sites are displayed as you move (rotate or
        translate) a DNA segment. After you are finished moving a DNA segment,
        crossover sites are displayed as a pair of white cylinders that can
        be highlighted/selected. Clicking on a highlighted crossover site
        makes a crossover.
        </p>""")

    # Convert all "img" tags in the button's "What's This" text
    # into abs paths (from their original rel paths).
    # Partially fixes bug 2943. --mark 2008-12-07
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroup)

    return

def whatsThisTextForNanotubeCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Build Nanotube Command Toolbar.
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Nanotube</b>
        <p>
        Exits the <b>Build Nanotube</b> command set.
        </p>""")

    commandToolbar.insertNanotubeAction.setWhatsThis(
        """<b>Insert Nanotube</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildNanotube/InsertNanotube.png\"><br>
        Insert a carbon or boron-nitride nanotube by clicking two endpoints in
        the graphics area.
        </p>""")

    # Convert all "img" tags in the button's "What's This" text
    # into abs paths (from their original rel paths).
    # Partially fixes bug 2943. --mark 2008-12-07
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroup)

    return

def whatsThisTextForCrystalCommandToolbar(commandToolbar):
    """
    "Tool Tip" text for widgets in the Build Crystal (crystal) Command Toolbar.
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Crystal</b>
        <p>
        Exits the <b>Build Crystal</b> command set.
        </p>""")

    commandToolbar.polygonShapeAction.setWhatsThis(
        """<b>Polygon</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Polygon.png\"><br>
        Defines the selection shape as a polygon with the user specifying the
        vertices.</p>
        <p>
        <img source=\"ui/whatsthis/Remember.png\"><br>
        <b>Remember:</b> You must <b>double-click</b> to define the final vertex and close the polygon.
        </p>""")

    commandToolbar.circleShapeAction.setWhatsThis(
        """<b>Circle</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Circle.png\"><br>
        Defines the selection shape as a circle with the user specifying the
        center (first click) and radius (second click).
        </p>""")

    commandToolbar.squareShapeAction.setWhatsThis(
        """<b>Square</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Square.png\"><br>
        Defines the selection shape as a square with the user specifying the
        center (first click) and a corner (second click).
        </p>""")

    commandToolbar.rectCtrShapeAction.setWhatsThis(
        """<b>Rectangle</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/RectCenter.png\"><br>
        Defines the selection shape as a rectangle with the user defining
        the center (first click) and corner (second click).
        </p>""")

    commandToolbar.rectCornersShapeAction.setWhatsThis(
        """<b>Rectangle Corners</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/RectCorners.png\"><br>
        Defines the selection shape as a rectangle with the user specifying
        one corner (first click) and then the opposite corner (second click).
        </p>""")

    commandToolbar.hexagonShapeAction.setWhatsThis(
        """<b>Hexagon</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Hexagon.png\"><br>
        Defines the selection shape as a hexagon with the user specifying the
        center (first click) and corner (second click).
        </p>""")

    commandToolbar.triangleShapeAction.setWhatsThis(
        """<b>Triangle</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Triangle.png\"><br>
        Defines the selection shape as a triangle with the user specifying the
        center (first click) and corner (second click).
        </p>""")

    commandToolbar.diamondShapeAction.setWhatsThis(
        """<b>Diamond</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Diamond.png\"><br>
        Defines the selection shape as a diamond with the user specifying the
        center (first click) and corner (second click).
        </p>""")

    commandToolbar.lassoShapeAction.setWhatsThis(
        """<b>Lasso</b>
        <p>
        <img source=\"ui/actions/Command Toolbar/BuildCrystal/Lasso.png\"><br>
        Defines the selection shape as a freeform lasso. Draw the shape by
        dragging the mouse while holding down the <a href=LMB>LMB</a>.
        </p>""")

    # Convert all "img" tags in the button's "What's This" text
    # into abs paths (from their original rel paths).
    # Partially fixes bug 2943. --mark 2008-12-07
    fix_whatsthis_text_and_links(commandToolbar.subControlActionGroup)

    return

# Move command toolbar ####################

def whatsThisTextForMoveCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Move Command Toolbar.
    """
    commandToolbar.exitModeAction.setWhatsThis(
        """<b>Exit Move</b>
        <p>
        Exits the <b>Move</b> command set.
        </p>""")

    # NOTE: "What's This" descriptions for Translate, Rotate and
    # Align to Common Axis can be found in WhatsThisText_for_MainWindow.py.
    # (and they should remain there until Ui_MoveFlyout is refactored )
    # - Mark 2008-12-02

    return

def whatsThisTextForMovieCommandToolbar(commandToolbar):
    """
    "What's This" text for widgets in the Movie Command Toolbar.
    """
    return
