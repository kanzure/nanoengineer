# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildAtoms_Command.py 

The 'Command' part of the BuildAtoms Mode (BuildAtoms_basicCommand and 
BuildAtoms_basicGraphicsMode are the two split classes of the old 
depositMode)  It provides the command object for its GraphicsMode class. 
The Command class defines anything related to the 'command half' of the mode -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

                        
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

TODO: [as of 2008-01-04]
- Flyout toolbar related code needs to go in a file like Ui_BuildAtomsFlyout. 
  This will also need further cleanup to be done during the Command Toolbar 
  code cleanup 
- For all qactions on the flyout toolbar:
  - move what's this text declarations to whatsThisForAtomsCommandToolbar()
  - move tooltip text declarations to toolTipsForAtomsCommandToolbar()
- Do we need to make change bond and delete bond as separate commands? 
  Not needed immediately but worth doing this in future. 
- Items mentioned in Build_GraphicsMode.py 

History:
See history for depositMode.py 
Ninad 2008-01-04: Created new Command and GraphicsMode classes from 
                  the old class depositMode and moved the 
                  Command related methods into this class from 
                  depositMode.py
"""

from PyQt4 import QtGui
from PyQt4.Qt import QSize
from PyQt4.Qt import SIGNAL
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

import foundation.env as env
import foundation.changes as changes

from utilities.icon_utilities import geticon

from utilities.debug import print_compact_stack
from utilities.debug import print_compact_traceback
from model.elements import Singlet

from utilities.prefs_constants import buildModeHighlightingEnabled_prefs_key
from utilities.prefs_constants import keepBondsDuringTransmute_prefs_key

from commands.BuildAtoms.BuildAtomsPropertyManager import BuildAtomsPropertyManager
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_basicCommand

from command_support.GraphicsMode_API import GraphicsMode_API
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode

from utilities.Log import orangemsg
_superclass = SelectAtoms_basicCommand

class BuildAtoms_basicCommand(SelectAtoms_basicCommand):
    """
    """
    commandName = 'DEPOSIT'
    msg_commandName = "Build Mode" 
    default_mode_status_text = "Mode: Build Atoms"
    featurename = "Build Atoms Mode"    
   
    highlight_singlets = True     
    water_enabled = False # Fixes bug 1583. mark 060301.    
    # methods related to entering this mode         
    dont_update_gui = True
    
    #graphicsMode will be set in BuildAtoms_Command.__init__ . 
    graphicsMode = None
    
    
    def __init__(self, commandSequencer):
        _superclass.__init__(self, commandSequencer)        
            
        #Initialize some more attributes. 
        self._pastable_atomtype = None
        
        #The following flag, if set to True, doesn't allow converting
        #bonds between the selected atoms to the bondtyp specified in the 
        #flyout toolbar. This is used only while activating the 
        #bond tool. See self._convert_bonds_bet_selected_atoms() for details
        self._supress_convert_bonds_bet_selected_atoms = False
        
        self.hover_highlighting_enabled = \
            env.prefs[buildModeHighlightingEnabled_prefs_key]
        
    def Enter(self):      
        self._init_flyoutActions()        
        _superclass.Enter(self) 
        
    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command toolbar, connecting widget 
        slots etc. 
        
        Called once each time the mode is entered; should be called only by code 
        in modes.py
        
        @see: L{self.restore_gui}
        """
        
        #GUI actions that need to be disabled (for some reason) while in 
        #this command can be disabled by calling enable_gui_action with a proper
        #boolean flag. Note that this method is also called in restore_gui
        #which toggles the disabled actions 
        self.enable_gui_actions(False)
        
        self.dont_update_gui = True # redundant with Enter, 
        #I think; changed below
        # (the possible orders of calling all these mode entering/exiting
        #  methods is badly in need of documentation, if not cleanup...
        #  [says bruce 050121, who is to blame for this])
        
        #important to check for old propMgr object. Reusing propMgr object 
        #significantly improves the performance.
        if not self.propMgr:
            self.propMgr = BuildAtomsPropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- niand 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        self.propMgr.show()
        
        self.updateCommandToolbar(bool_entering = True)
        
        if self.depositAtomsAction.isChecked():
            self.activateAtomsTool()
        elif self.transmuteBondsAction.isChecked():
            self.activateBondsTool()
            
        self.w.toolsDepositAtomAction.setChecked(True)          
                
        self.connect_or_disconnect_signals(True)      
        
        self.dont_update_gui = False
        
        self.propMgr.updateMessage()
        
        # The caller will now call update_gui(); we rely on that [bruce 050122]
        return
    
    
    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command toolbar, 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.w.toolsDepositAtomAction.setChecked(False)
        self.connect_or_disconnect_signals(False)
        self.enable_gui_actions(True)
        self.updateCommandToolbar(bool_entering = False)
        self.propMgr.close()
        
    def enable_gui_actions(self, bool):
        """
        Enable or disable some gui actions depending on 
        whether user is entering or leaving the mode
        """
        #UPDATE 2008-07-16: commenting out the call that disables 
        #all structure generator actions while in Build Chunks command. 
        #This was needed long ago perhaps before year 2007 and some tests 
        #indicate that this is no longer needed. May be the disabling 
        #other structure builders was intentionally done to ask user to finish 
        #what he was doing but that was not consistent throughout the 
        #program and is creating confusion. So simply allow entering different 
        #commands from Build > Chunks mode. -[ Ninad comment]
        #==========================
        ###self.w.buildDnaAction.setEnabled(bool)
        ###self.w.buildNanotubeAction.setEnabled(bool)
        ###self.w.nanotubeGeneratorAction.setEnabled(bool)
        ###self.w.insertGrapheneAction.setEnabled(bool)
        ###self.w.toolsCookieCutAction.setEnabled(bool)
        ####@@This should also contain HeteroJunctionAction. (in general Plugin 
        ####actions)
        #============================
        pass

    def connect_or_disconnect_signals(self, connect): 
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        
        
        #Atom, Bond Tools Groupbox
        change_connect(self.bondToolsActionGroup,
                       SIGNAL("triggered(QAction *)"), 
                       self.changeBondTool)
                
        
        change_connect(self.transmuteAtomsAction,
                        SIGNAL("triggered()"),self.transmutePressed)
                       
                
        change_connect(self.exitModeAction, SIGNAL("triggered()"), 
                       self.w.toolsDone)
        
        change_connect(self.subControlActionGroup, 
                       SIGNAL("triggered(QAction *)"),
                       self.updateCommandToolbar)
        
        change_connect(self.transmuteBondsAction, 
                       SIGNAL("triggered()"), 
                       self.activateBondsTool)
        
        change_connect(self.depositAtomsAction, 
                       SIGNAL("triggered()"), 
                       self.activateAtomsTool)
        
        #Connect or disconnect signals in property manager      
        self.propMgr.connect_or_disconnect_signals(connect)  
        
        #Connect or disconnect the property mgr widget that enables/disables
        #the 'water'. This is done here instead of doing it in 
        #propMgr.connect_or_disconnect because this widget needs to talk with 
        #the graphicsMode of this command (i.e. of the propMgr's .parentMode),
        # so better it be here and do it safely. [ninad]
        # [bruce 080710 adds: ideally the water enabled flag would be maintained
        #  in the command (as all state ought to be) and only used by the
        #  graphicsMode.]
        if hasattr(self.graphicsMode, 'setWater'):
            change_connect(self.propMgr.waterCheckBox,
                            SIGNAL("toggled(bool)"),
                            self.graphicsMode.setWater)
        else:
            print_compact_stack("bug: BuildAtoms graphicsmode has no attribute"\
                                "setWater , ignoring")
            
        if hasattr(self.graphicsMode, 'set_hoverHighlighting'):
            change_connect(self.propMgr.highlightingCheckBox,
                            SIGNAL("toggled(bool)"),
                            self.graphicsMode.set_hoverHighlighting)
        else:
            print_compact_stack("bug: BuildAtoms graphicsmode has no attribute"\
                                "set_hoverHighlighting , ignoring")
    
    def changeBondTool(self, action):
        """
        Change the bond tool (e.g. single, double, triple, aromatic 
        and graphitic) depending upon the checked action.
        @param: action is the checked bond tool action in the 
        bondToolsActionGroup
        """       
        bondTypeString = ''
        delete_bonds_bet_selected_atoms = False
        state = action.isChecked()
        if action ==  self.bond1Action:
            self.graphicsMode.setBond1(state)
            bondTypeString = 'single bonds.'
        elif action == self.bond2Action:
            self.graphicsMode.setBond2(state)
            bondTypeString = 'double bonds.'
        elif action == self.bond3Action:
            self.graphicsMode.setBond3(state)
            bondTypeString = 'triple bonds.'
        elif action == self.bondaAction:
            self.graphicsMode.setBonda(state)
        elif action == self.bondgAction:
            self.graphicsMode.setBondg(state)
            bondTypeString = 'graphitic bonds.'
        elif action == self.cutBondsAction:
            delete_bonds_bet_selected_atoms = True
            self.graphicsMode.update_cursor()
            self.propMgr.updateMessage()
        
        #When the bond tool is changed, also make sure to apply the new 
        #bond tool, to the bonds between the selected atoms if any.        
        self._convert_bonds_bet_selected_atoms(
            delete_bonds_bet_selected_atoms = delete_bonds_bet_selected_atoms,
            bondTypeString = bondTypeString
        )
        
    def _convert_bonds_bet_selected_atoms(self, 
                                          delete_bonds_bet_selected_atoms = False,
                                          bondTypeString = ''):
        """
        Converts the bonds between the selected atoms to one specified by
        self.graphicsMode..bondclick_v6. Example: When user selects all atoms in 
        a nanotube and clicks 'graphitic' bond button, it converts all the 
        bonds between the selected atoms to graphitic bonds. 
        @see: self.activateBondsTool()
        @see: self.changeBondTool()
        @see: bond_utils.apply_btype_to_bond()
        @see: BuildAtoms_GraphicsMode.bond_change_type()
        """
        #Method written on 2008-05-04 to support NFR bug 2832. This need to 
        #be reviewed for further optimization (not urgent) -- Ninad
        #This flag is set while activating the bond tool. 
        #see self.activateBondsTool()
        if self._supress_convert_bonds_bet_selected_atoms:
            return
        
        #For the history message
        converted_bonds = 0
        non_converted_bonds = 0
        deleted_bonds = 0
        #We wil check the bond dictionary to see if a bond between the 
        #selected atoms is already operated on.
        bondDict = {}
        #MAke sure that the bond tool on command toolbar is active
        if self.isBondsToolActive():
            bondList = [] 
            #all selected atoms 
            atoms = self.win.assy.selatoms.values()
            for a in atoms:
                for b in a.bonds[:]:
                    #If bond 'b' is already in the bondDict, skip this 
                    #iteration.
                    if bondDict.has_key(id(b)):
                        continue
                    else:
                        bondDict[id(b)] = b
                    #neigbor atom of the atom 'a'    
                    neighbor = b.other(a)
                    
                    if neighbor.element != Singlet and neighbor.picked:  
                        if delete_bonds_bet_selected_atoms:
                            b.bust()
                            deleted_bonds += 1
                        else:
                            bond_type_changed = self.graphicsMode.bond_change_type(
                                b, 
                                allow_remake_bondpoints = True,
                                supress_history_message = True
                            )
                            if bond_type_changed:
                                converted_bonds += 1
                            else:
                                non_converted_bonds += 1
                            
            msg = ''                        
            if delete_bonds_bet_selected_atoms:                
                msg = "Deleted %d bonds between selected atoms"%deleted_bonds
            else:
                if bondTypeString:                        
                    msg = "%d bonds between selected atoms "\
                        "converted to %s" %(converted_bonds, 
                                            bondTypeString)
                    msg2 = ''
                    if non_converted_bonds:
                        msg2 = orangemsg(" [Unable to convert %d "\
                                         "bonds to %s]"%(non_converted_bonds, 
                                                         bondTypeString))
                    if msg2:
                        msg += msg2
            if msg:
                env.history.message(msg)
                
            self.glpane.gl_update()

    def update_gui(self): #bruce 050121 heavily revised this 
        #[called by basicMode.UpdateDashboard]
        """
        #doc...
        can be called many times during the mode;
        should be called only by code in modes.py
        """
##        if not self.isCurrentCommand():
##            print "update_gui returns since not self.isCurrentCommand"
##            return #k can this ever happen? yes, when the mode is entered!
##            # this was preventing the initial update_gui in _enterMode from 
              ##running...
        
        # avoid unwanted recursion [bruce 041124]
        # [bruce 050121: this is not needed for reason it was before,
        #  but we'll keep it (in fact improve it) in case it's needed now
        #  for new reasons -- i don't know if it is, but someday it might be]
        
        
        if self.dont_update_gui:
            # Getting msg after depositing an atom, then selecting a bondpoint 
            # and "Select Hotspot and Copy" from the GLPane menu.
            # Is it a bug??? Mark 051212.
            # bruce 060412 replies: I don't know; it might be. Perhaps we should
            # do what MMKit does as of today,
            # and defer all UpdateDashboard actions until another event handler
            # (here, or better in basicMode).
            # But for now I'll disable the debug print and we can defer this 
            # issue unless it becomes suspected
            # in specific bugs.
            return
        # now we know self.dont_update_gui == False, so ok that we reset it to 
        # that below (I hope)
        self.dont_update_gui = True
        try:
            self.update_gui_0()
        except:
            print_compact_traceback("exception from update_gui_0: ")
        self.dont_update_gui = False
        
        return

    def update_gui_0(self): 
        """
        Overridden in some subclasses. Default implementation does nothing
        @see: B{PasteMode}
        """        
        pass
    
    def viewing_main_part(self): #bruce 050416 ###e should refile into assy
        return self.o.assy.current_selgroup_iff_valid() is self.o.assy.tree
    
    def select_chunk_of_highlighted_atom(self): 
        """Select the chunk containing the highlighted atom or singlet"""
        if self.o.selatom:
            self.o.assy.permit_pick_parts()
            # was unpickparts; I think this is the intent (and the effect, 
            # before now) [bruce 060721]
            self.o.assy.unpickall_in_GLPane() 
            self.o.selatom.molecule.pick()
            self.w.win_update()
        
    def makeMenus(self): #bruce 050705 revised this to support bond menus
        """
        Create context menu for this command. (Build Atoms mode)
        """
        selatom, selobj = self.graphicsMode.update_selatom_and_selobj( None)
            # bruce 050612 added this [as an update_selatom call] -- 
            #not needed before since bareMotion did it (I guess).
            # [replaced with update_selatom_and_selobj, bruce 050705]
        
        self.Menu_spec = []
        ###e could include disabled chunk & selatom name at the top, whether 
        ##selatom is singlet, hotspot, etc.
        
        # figure out which Set Hotspot menu item to include, and whether to 
        #disable it or leave it out
        if self.viewing_main_part():
            text, meth = ('Set Hotspot and Copy', 
                          self.graphicsMode.setHotSpot_mainPart)
                # bruce 050121 renamed this from "Set Hotspot" to "Set Hotspot 
                # and Copy as Pastable".
                # bruce 050511 shortened that to "Set Hotspot and Copy".
                # If you want the name to be shorter, then change the method
                # to do something simpler! Note that the locally set hotspot
                # matters if we later drag this chunk to the clipboard.
                # IMHO, the complexity is a sign that the design
                # should not yet be considered finished!
        else:
            text, meth = ('Set Hotspot of clipboard item', 
                          self.graphicsMode.setHotSpot_clipitem)
                ###e could check if it has a hotspot already, if that one is 
                ##  different, etc
                ###e could include atom name in menu text... Set Hotspot to X13
        if selatom is not None and selatom.is_singlet():
            item = (text, meth)
        elif selatom is not None:
            item = (text, meth, 'disabled')
        else:
            item = None
        if item:
            self.Menu_spec.append(item)
        
        # Add the trans-deposit menu item.
        if selatom is not None and selatom.is_singlet():
            self.Menu_spec.append(( 
                'Trans-deposit previewed item', 
                lambda dragatom=selatom: self.graphicsMode.transdepositPreviewedItem(dragatom) ))

        # figure out Select This Chunk item text and whether to include it
        ##e (should we include it for internal bonds, too? not for now, maybe 
        ## not ever. [bruce 050705])
        if selatom is not None:
            name = selatom.molecule.name
            item = ('Select Chunk %r' % name, 
                    self.select_chunk_of_highlighted_atom)
                #e maybe should disable this or change to checkmark item (with 
                #unselect action) if it's already selected??
            self.Menu_spec.append(item)

        ##e add something similar for bonds, displaying their atoms, and the 
        ##bonded chunk or chunks?

        if selatom is not None:
            #k is 2nd cond redundant with is_singlet()?
            is_singlet = selatom.is_singlet() and len(selatom.bonds) == 1 
        else:
            is_singlet = False

        # add submenu to change atom hybridization type [initial kluge]
        atomtypes = (selatom is None) and ['fake'] or selatom.element.atomtypes
            # kluge: ['fake'] is so the idiom "x and y or z" can pick y;
            # otherwise we'd use [] for 'y', but that doesn't work since it's 
            #false.
##        if selatom is not None and not selatom.is_singlet():
##            self.Menu_spec.append(( '%s' % selatom.atomtype.fullname_for_msg(),
            ##noop, 'disabled' )) 
        if len(atomtypes) > 1: # i.e. if elt has >1 atom type available! 
            #(then it must not be Singlet, btw)
            # make a submenu for the available types, checkmarking the current 
            #one, disabling if illegal to change, sbartext for why
            # (this code belongs in some more modular place... where exactly?
            #it's part of an atom-type-editor for use in a menu...
            #  put it with Atom, or with AtomType? ###e)
            submenu = []
            for atype in atomtypes:
                submenu.append(( 
                    atype.fullname_for_msg(),
                    lambda arg1=None, 
                    arg2=None, atype=atype: atype.apply_to(selatom),
                    # Notes: the atype=atype is required
                    # -- otherwise each lambda refers to the same
                    # localvar 'atype' -- effectively by reference,
                    # not by value --
                    # even though it changes during this loop!
                    #   Also at least one of the arg1 and arg2 are required, 
                    # otherwise atype ends up being an int,
                    # at least acc'd to exception we get here. Why is Qt passing
                    # this an int? Nevermind for now. ###k
                             (atype is selatom.atomtype) and 'checked' or None,
                             (not atype.ok_to_apply_to(selatom)) and 'disabled' or None
                           ))
            self.Menu_spec.append(( 'Atom Type: %s' % selatom.atomtype.fullname_for_msg(), submenu ))
##            self.Menu_spec.append(( 'Atom Type', submenu ))

        ###e offer to change element, too (or should the same submenu be used, 
        ##with a separator? not sure)

        # for a highlighted bond, add submenu to change bond type, if atomtypes 
        # would permit that;
        # or a menu item to just display the type, if not. Also add summary info
        # about the bond...
        # all this is returned (as a menu_spec sublist) by one external helper 
        # method.
        
        if is_singlet:
            selbond = selatom.bonds[0]
        else:
            selbond = selobj # might not be a Bond (could be an Atom or None)
        
        try:
            method = selbond.bond_menu_section
        except AttributeError:
            # selbond is not a Bond
            pass
        else:
            glpane = self.o
            quat = glpane.quat
            try:
                menu_spec = method(quat = quat) #e pass some options??
            except:
                print_compact_traceback("exception in bond_menu_section for %r, ignored: " % (selobj,))
            else:
                if menu_spec:
                    self.Menu_spec.extend(menu_spec)
                pass
            pass

        # Local minimize [now called Adjust Atoms in history/Undo, Adjust <what>
        #here and in selectMode -- mark & bruce 060705]
        # WARNING: This code is duplicated in selectMode.makeMenus().
        # mark 060314.
        if selatom is not None and not selatom.is_singlet() and \
           self.w.simSetupAction.isEnabled():
            # if simSetupAction is not enabled, a sim process is running.  
            #Fixes bug 1283. mark 060314.
            ## self.Menu_spec.append(( 'Adjust atom %s' % selatom, 
            ##selatom.minimize_1_atom )) # older pseudocode
            # experimental. if we leave in these options, some of them might 
            # want a submenu.
            # or maybe the layer depth is a dashboard control? or have buttons
            # instead of menu items?
            self.Menu_spec.append(( 'Adjust atom %s' % selatom,
                                    lambda e1=None,
                                    a = selatom: self.localmin(a,0) ))
            self.Menu_spec.append(( 'Adjust 1 layer', 
                                    lambda e1=None,
                                    a = selatom: self.localmin(a,1) ))
            self.Menu_spec.append(( 'Adjust 2 layers', 
                                    lambda e1=None,
                                    a = selatom: self.localmin(a,2) ))
        
        # offer to clean up singlet positions (not sure if this item should be
        # so prominent)
        if selatom is not None and not selatom.is_singlet():
            sings = selatom.singNeighbors() #e when possible, use 
            #baggageNeighbors() here and remake_baggage below. [bruce 051209]
            if sings or selatom.bad():
                if sings:
                    text = 'Reposition bondpoints'
                        # - this might be offered even if they don't need 
                        # repositioning;
                        # not easy to fix, but someday we'll always reposition 
                        # them whenever needed
                        # and this menu command can be removed then.
                        # - ideally we'd reposition H's too (i.e. 
                        #  call remake_baggage below)
                else:
                    text = 'Add bondpoints' # this text is only used if it 
                                            #doesn't have enough
                cmd = (lambda a = selatom: self.RepositionBondpoints_command(a))
                self.Menu_spec.append(( text, cmd ))
                ##e should finish and use remake_baggage (and baggageNeighbors)
        
        # selobj-specific menu items.  
        # This is duplicated in selectMode.makeMenus().
        # [bruce 060405 added try/except, and generalized this from Jig-specific
        # to selobj-specific items,
        #  by replacing isinstance(selobj, Jig) with hasattr(selobj, 
        # 'make_selobj_cmenu_items'),
        #  so any kind of selobj can provide more menu items using this API.
        #  Note that the only way selobj could customize its menu items to the 
        #  calling command or its graphicsMode
        #  would be by assuming that was the currentCommand or its graphicsMode.
        #  Someday we might extend the API
        #  to pass it glpane, so we can support multiple glpanes, each in a 
        # different command and/or graphicsMode. #e]
        if selobj is not None and hasattr(selobj, 'make_selobj_cmenu_items'):
            try:
                selobj.make_selobj_cmenu_items(self.Menu_spec)
            except:
                print_compact_traceback("bug: exception (ignored) in make_selobj_cmenu_items for %r: " % selobj)
        
        # separator and other mode menu items.
        if self.Menu_spec:
            self.Menu_spec.append(None)
            
        # Enable/Disable Jig Selection.  
        # This is duplicated in selectMode.makeMenus() and s
        # electMolsMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  
                                     self.graphicsMode.toggleJigSelection, 
                                     'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  
                                     self.graphicsMode.toggleJigSelection, 
                                     'unchecked')])
            
        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Edit Color Scheme...', self.w.colorSchemeCommand),
            ])

        self.Menu_spec_shift = list(self.Menu_spec) #bruce 060721 experiment; 
            # if it causes no harm, we can
            # replace the self.select item in the copy with one for 
            #shift-selecting the chunk, to fix a bug/NFR 1833 ####@@@@
            # (we should also rename self.select)
        
        return # from makeMenus

    def RepositionBondpoints_command(self, atom):
        del self
        atom.remake_bondpoints()
        atom.molecule.assy.glpane.gl_update() #bruce 080216 bugfix
        return
        
    def isAtomsToolActive(self):
        """
        Tells whether the Atoms Tool is active (boolean)  
        @return: The checked state of B{self.depositAtomsAction}
        """
        #TODO: It relies on self.depositAtomsAction to see if the tool is active
        #There needs to be a better way to tell this. One idea is to 
        #test which graphicsMode / Command is currently being used. 
        #But for that, Bond Tools needs to be a separate command on the 
        #command stack instead of a part of Build Atoms Command. So, in the
        #near future, we need to refactor Build Atoms command to separate out 
        # Atoms and Bonds tools. -- Ninad 2008-01-03 [commented while splitting
        # legacy depositMode class into Command/GM classes]        
        return self.depositAtomsAction.isChecked()
    
    def isBondsToolActive(self):
        """
        Tells whether the Bonds Tool is active (boolean)
        @return: The opposite of the checked state of B{self.depositAtomsAction}
        @see: comment in self.isAtomsToolActive()
        """
        # Note: the intent of self.bondclick_v6 was to be true only when this 
        # should return true,
        # but the Atom tool does not yet conform to that,
        # and the existing code as of 060702 appears to use this condition,
        # so for now [bruce 060702] it's deemed the official condition.
        # But I can't tell for sure whether the other conditions (modkeys, or 
        # commented out access to another button)
        # belong here, so I didn't copy them here but left the code in 
        #bondLeftUp unchanged (at least for A8).
        
        return not self.depositAtomsAction.isChecked()
    
    def isDeleteBondsToolActive(self):
        """
        Tells whether the Delete Bonds tool is active (boolean)
        @see: comment in self.isAtomsToolActive()
        """
        return self.isBondsToolActive() and \
               self.cutBondsAction.isChecked()
    
    #TODO: Move the command toolbar related methods into Ui_BuildAtomsFlyout.py 
    #(not created yet) 
    #This will also need further cleanup to be done during the Command Toolbar 
    #code cleanup 
    
    def _init_flyoutActions(self):
        """
        Define flyout toolbar actions for this mode.
        """
        #@NOTE: In Build mode, some of the actions defined in this method are 
        #also used in Build Atoms PM. (e.g. bond actions) So probably better to 
        #renameit as _init_modeActions. Not doing that change in mmkit code 
        #cleanup commit(other modes still implement a method by same 
        #name)-ninad20070717
                
        self.exitModeAction = NE1_QWidgetAction(self.propMgr, 
                                                win = self.win)
        self.exitModeAction.setText("Exit Chunks")
        self.exitModeAction.setIcon(
            geticon('ui/actions/Toolbars/Smart/Exit.png'))
        self.exitModeAction.setCheckable(True)
        self.exitModeAction.setChecked(True)
        self.exitModeAction.setWhatsThis(
        """<b>Exit Chunks </b>
        <p>
       Exits the Build Atoms Mode
        </p>""")
        
        #Following Actions are added in the Flyout toolbar. 
        #Defining them outside that method as those are being used
        #by the subclasses of deposit mode (testmode.py as of 070410) -- ninad
                
        self.depositAtomsAction = NE1_QWidgetAction(self.w, 
                                                    win = self.w)
        self.depositAtomsAction.setText("Atoms Tool")
        self.depositAtomsAction.setIcon(
            geticon('ui/actions/Toolbars/Smart/Deposit_Atoms.png'))
        self.depositAtomsAction.setCheckable(True)
        self.depositAtomsAction.setChecked(True)
        self.depositAtomsAction.setWhatsThis(
        """<b>Atoms Tool </b>
        <p>
       Turns on the Atoms Tool to deposit atoms from the Molecular
       Modeling Kit into the 3D Workspace
        </p>""")
                
        self.transmuteBondsAction = NE1_QWidgetAction(self.w, 
                                                      win = self.w)
        self.transmuteBondsAction.setText("Bonds Tool")
        self.transmuteBondsAction.setIcon(
            geticon('ui/actions/Toolbars/Smart/Transmute_Bonds.png'))
        self.transmuteBondsAction.setCheckable(True)
        self.transmuteBondsAction.setWhatsThis(
        """<b>Bonds Tool</b>
        <p>
        Turns on the Bonds Tool to change the bonding type of deposited atoms. 
        The user can also remove existing bonds by cutting them.
        </p>""")
        
        self.subControlActionGroup = QtGui.QActionGroup(self.w)
        self.subControlActionGroup.setExclusive(True)   
        self.subControlActionGroup.addAction(self.depositAtomsAction)   
        ##self.subControlActionGroup.addAction(self.propMgr.transmuteAtomsAction)
        self.subControlActionGroup.addAction(self.transmuteBondsAction)
        
        self.bondToolsActionGroup = QtGui.QActionGroup(self.w)
        self.bondToolsActionGroup.setExclusive(True)
                
        self.bond1Action = NE1_QWidgetAction(self.w, 
                                             win = self.w)  
        self.bond1Action.setText("Single")
        self.bond1Action.setIcon(
            geticon("ui/actions/Toolbars/Smart/bond1.png"))
        self.bond1Action.setWhatsThis(
        """<b>Single Bond</b>
        <p>
       Transmutes selected bond to a single bond if permitted 
        </p>""")
            
        self.bond2Action = NE1_QWidgetAction(self.w, 
                                             win = self.w)  
        self.bond2Action.setText("Double")
        self.bond2Action.setIcon(
            geticon("ui/actions/Toolbars/Smart/bond2.png"))
        self.bond2Action.setWhatsThis(
        """<b>Double Bond</b>
        <p>
       Transmutes selected bond to a double bond if permitted 
        </p>""")
        
        self.bond3Action = NE1_QWidgetAction(self.w,
                                             win = self.w)  
        self.bond3Action.setText("Triple")
        self.bond3Action.setIcon(
            geticon("ui/actions/Toolbars/Smart/bond3.png"))
        self.bond3Action.setWhatsThis(
        """<b>Triple Bond</b>
        <p>
       Transmutes selected bond to a triple bond if permitted 
        </p>""")
        
        self.bondaAction = NE1_QWidgetAction(self.w, 
                                             win = self.w)  
        self.bondaAction.setText("Aromatic")
        self.bondaAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/bonda.png"))
        self.bondaAction.setWhatsThis(
        """<b>Aromatic Bond</b>
        <p>
       Transmutes selected bond to an aromatic bond if permitted 
        </p>""")
     
        
        self.bondgAction = NE1_QWidgetAction(self.w,
                                             win = self.w)  
        self.bondgAction.setText("Graphitic")
        self.bondgAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/bondg.png"))
        self.bondgAction.setWhatsThis(
        """<b>Graphitic Bond</b>
        <p>
       Transmutes selected bond to an graphitic bond if permitted 
        </p>""")
        
        self.cutBondsAction = NE1_QWidgetAction(self.w,
                                                win = self.w)  
        self.cutBondsAction.setText("Cut Bonds")
        self.cutBondsAction.setIcon(
            geticon("ui/actions/Tools/Build Tools/Cut_Bonds.png"))
        self.cutBondsAction.setWhatsThis(
        """<b>Cut Bonds</b>
        <p>
       Removes the bond between atoms when selected using the left mouse button 
       </p>""")
        
        
        for action in [self.bond1Action, 
                       self.bond2Action, 
                       self.bond3Action,
                       self.bondaAction,
                       self.bondgAction,
                       self.cutBondsAction  
                       ]:
            self.bondToolsActionGroup.addAction(action)
            action.setCheckable(True)
                    
        
        self.transmuteAtomsAction = NE1_QWidgetAction(self.w, win = self.w)
        self.transmuteAtomsAction.setText("Transmute Atoms")
        self.transmuteAtomsAction.setIcon(
            geticon('ui/actions/Toolbars/Smart/Transmute_Atoms.png'))       
        self.transmuteAtomsAction.setCheckable(False)
        self.transmuteAtomsAction.setWhatsThis(
        """<b>Transmute</b>
        <p>
       Can be used to change the selected atoms into a different element or 
       atom type
       </p>""")
        
    def activateAtomsTool(self):
        """
        Activate the atoms tool of the build chunks mode 
        hide only the Atoms Tools groupbox in the Build chunks Property manager
        and show all others the others.
        """
                
        self.propMgr.bondToolsGroupBox.hide()
        
        for grpbox in self.propMgr.previewGroupBox, self.propMgr.elementChooser:
            grpbox.show()
        
        self.propMgr.pw.propertyManagerScrollArea.ensureWidgetVisible(
            self.propMgr.headerFrame)
        
        self.graphicsMode.update_cursor()
        
        self.w.depositState = 'Atoms'
        
        self.UpdateDashboard()
        
        self.propMgr.updateMessage()
    
        
    def activateBondsTool(self):
        """
        Activate the bond tool of the build chunks mode 
        Show only the Bond Tools groupbox in the Build chunks Property manager
        and hide the others.
        @see:self._convert_bonds_bet_selected_atoms()
        """        
        #Temporarily set the following flag to True while activating the 
        #bond tool. @see:self._convert_bonds_bet_selected_atoms()
        self._supress_convert_bonds_bet_selected_atoms = True
        self.bond1Action.setChecked(True)
        self.changeBondTool(self.bond1Action)
        #Set this flag to False now.
        self._supress_convert_bonds_bet_selected_atoms = False
                        
        for grpbox in self.propMgr.previewGroupBox, self.propMgr.elementChooser:
            grpbox.hide()
                        
        self.propMgr.bondToolsGroupBox.show()
        
        bondToolActions =  self.bondToolsActionGroup.actions()
        for btn in self.propMgr.bondToolButtonRow.buttonGroup.buttons():
            btnId = self.propMgr.bondToolButtonRow.buttonGroup.id(btn)
            action = bondToolActions[btnId]
            action.setCheckable(True)
            btn.setIconSize(QSize(24,24))
            btn.setDefaultAction(action)
        
        self.propMgr.pw.propertyManagerScrollArea.ensureWidgetVisible(
            self.propMgr.headerFrame)
                
        self.propMgr.updateMessage()
    
    
    def getFlyoutActionList(self): 
        """
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 
        CommandToolbar._createFlyoutToolBar method calls this 
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        
        #ninad070330 This implementation may change in future. 
        
        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions. 
        allActionsList = []
        #Action List for  subcontrol Area buttons. 
        #For now this list is just used to set a different palette to thisaction
        #buttons in the toolbar
        subControlAreaActionList =[] 
        
                
        #Append subcontrol area actions to  subControlAreaActionList
        #The 'Exit button' althought in the subcontrol area, would 
        #look as if its in the Control area because of the different color 
        #palette 
        #and the separator after it. This is intentional.
        subControlAreaActionList.append(self.exitModeAction)
        separator1 = QtGui.QAction(self.w)
        separator1.setSeparator(True)
        subControlAreaActionList.append(separator1) 
        
        subControlAreaActionList.append(self.depositAtomsAction)        
        ##subControlAreaActionList.append(self.propMgr.transmuteAtomsAction)
        subControlAreaActionList.append(self.transmuteBondsAction)      
        separator = QtGui.QAction(self.w)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        
        #Also add the subcontrol Area actions to the 'allActionsList'
        for a in subControlAreaActionList:
            allActionsList.append(a)    
        ##actionlist.append(self.w.modifyAdjustSelAction)
        ##actionlist.append(self.w.modifyAdjustAllAction)
        
        #Ninad 070330:
        #Command Actions : These are the actual actions that will respond the 
        #a button pressed in the 'subControlArea (if present). 
        #Each Subcontrol area button can have its own 'command list' 
        #The subcontrol area buuton and its command list form a 'key:value pair 
        #in a python dictionary object
        #In Build mode, as of 070330 we have 3 subcontrol area buttons 
        #(or 'actions)'
        commandActionLists = [] 
        
        #Append empty 'lists' in 'commandActionLists equal to the 
        #number of actions in subControlArea 
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)
        
        #Command list for the subcontrol area button 'Atoms Tool'
        #For others, this list will remain empty for now -- ninad070330 
        depositAtomsCmdLst = []
        depositAtomsCmdLst.append(self.w.modifyHydrogenateAction)
        depositAtomsCmdLst.append(self.w.modifyDehydrogenateAction)
        depositAtomsCmdLst.append(self.w.modifyPassivateAction)
        separatorAfterPassivate = QtGui.QAction(self.w)
        separatorAfterPassivate.setSeparator(True)
        depositAtomsCmdLst.append(separatorAfterPassivate)
        depositAtomsCmdLst.append(self.transmuteAtomsAction)    
        separatorAfterTransmute = QtGui.QAction(self.w)
        separatorAfterTransmute.setSeparator(True)
        depositAtomsCmdLst.append(separatorAfterTransmute)
        depositAtomsCmdLst.append(self.w.modifyDeleteBondsAction)
        depositAtomsCmdLst.append(self.w.modifySeparateAction)
        depositAtomsCmdLst.append(self.w.makeChunkFromSelectedAtomsAction)
                        
        commandActionLists[2].extend(depositAtomsCmdLst)
        
        ##for action in self.w.buildToolsMenu.actions():
            ##commandActionLists[2].append(action)
        
        # Command list for the subcontrol area button 'Bonds Tool'
        # For others, this list will remain empty for now -- ninad070405 
        bondsToolCmdLst = []
        bondsToolCmdLst.append(self.bond1Action)
        bondsToolCmdLst.append(self.bond2Action)
        bondsToolCmdLst.append(self.bond3Action)
        bondsToolCmdLst.append(self.bondaAction)
        bondsToolCmdLst.append(self.bondgAction)
        bondsToolCmdLst.append(self.cutBondsAction)
        commandActionLists[3].extend(bondsToolCmdLst)
                            
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params
    
    def updateCommandToolbar(self, bool_entering = True):
        """
        Update the command toolbar.
        """        
        obj = self
        self.w.commandToolbar.updateCommandToolbar(self.w.toolsDepositAtomAction,
                                                   obj, 
                                                   entering = bool_entering)
        return
    
    #======================    
    # methods related to exiting this mode [bruce 040922 made these from
    # old Done method, and added new code; there was no Flush method]
    def haveNontrivialState(self):
        return False
    
    def StateDone(self):
        return None
    # we never have undone state, but we have to implement this method,
    # since our haveNontrivialState can return True

    def StateCancel(self):
        # to do this correctly, we'd need to remove the atoms we added
        # to the assembly; we don't attempt that yet [bruce 040923,
        # verified with Josh]
        change_desc = "your changes are"
        msg = "%s Cancel not implemented -- %s still there.\n\
        You can only leave this mode via Done." % \
              ( self.msg_commandName, change_desc )
        self.warning( msg, bother_user_with_dialog = 1)
        return True # refuse the Cancel
    
    
    # Now uses superclass method selectAtomsMode.restore_patches(). mark 060207.
    # [not true anymore, evidently -- so what does it use? bruce 071011]
    # [guessing it's more like restore_patches_by_GraphicsMode than _by_Command 
    # -- bruce 071012]
    #    def restore_patches_by_GraphicsMode(self):
    #        self.o.setDisplay(self.saveDisp) #bruce 041129; see notes for 
    #            # bug 133
    #        self.o.selatom = None

    def clear(self):
        self.new = None
    
    #=== Cursor id
    def get_cursor_id_for_active_tool(self):
        """
        Provides a cursor id (int) for updating cursor in graphics mode, 
        based on the checked action in its flyout toolbar. (i.e. based on the 
        active tool)
        @see: BuildAtoms_GraphicsMode.update_cursor_for_no_MB_selection_filter_disabled
        """
        if self.depositAtomsAction.isChecked(): 
            cursor_id = 0
        elif self.bond1Action.isChecked(): 
            cursor_id = 1
        elif self.bond2Action.isChecked(): 
            cursor_id = 2
        elif self.bond3Action.isChecked(): 
            cursor_id = 3
        elif self.bondaAction.isChecked(): 
            cursor_id = 4
        elif self.bondgAction.isChecked(): 
            cursor_id = 5
        elif self.cutBondsAction.isChecked(): 
            cursor_id = 6
        else: 
            cursor_id = 0 
        
        return cursor_id
    
    
    #== Transmute helper methods =======================
    
    def get_atomtype_from_MMKit(self):
        """
        Return the current atomtype selected in the MMKit.
        
        Note: This appears to be very similar (if not completely redundant) to 
        pastable_atomtype() in this file. 
        """
        elm = self.propMgr.elementChooser.getElement()
        atomtype = None
        if len(elm.atomtypes) > 1: 
            try:
                # Obtain the hybrid index from the hybrid button group, not
                # the obsolete hybrid combobox. Fixes bug 2304. Mark 2007-06-20
                hybrid_name = self.propMgr.elementChooser.atomType
                atype = elm.find_atomtype(hybrid_name)
                if atype is not None:
                    atomtype = atype
            except:
                print_compact_traceback("exception (ignored): ") 
            pass
        if atomtype is not None and atomtype.element is elm:
            return atomtype
            
        # For element that doesn't support hybridization
        return elm.atomtypes[0]
    
    def transmutePressed(self):
        """
        Slot for "Transmute" button.
        """
        forceToKeepBonds = env.prefs[keepBondsDuringTransmute_prefs_key]
        atomType = self.get_atomtype_from_MMKit()
        self.w.assy.modifyTransmute(
            self.propMgr.elementChooser.getElementNumber(), 
            force = forceToKeepBonds, 
            atomType=atomType)
    
    def isAutoBondingEnabled(self):
        if self.propMgr and hasattr(self.propMgr, 'autoBondCheckBox'):
            autoBondingEnabled = self.propMgr.autoBondCheckBox.isChecked()
        else:
            autoBondingEnabled = True
            
        return autoBondingEnabled
    
    def pastable_element(self):
        if self.propMgr and hasattr(self.propMgr, 'elementChooser'):
            return self.propMgr.elementChooser.getElement()
        else:
            # we're presumably a subclass with no propMgr or a different one
            from model.elements import Carbon
            return Carbon
        
    def pastable_atomtype(self):
        """
        Return the current pastable atomtype.

        [REVIEW: This appears to be very similar (if not completely redundant) to 
        get_atomtype_from_MMKit() in this file. This is still used as of 071025;
        that one is called only by the slot transmutePressed -- can that still
        be called?]
        """
        #e we might extend this to remember a current atomtype per element
        #... not sure if useful
        current_element = self.pastable_element()
        if len(current_element.atomtypes) > 1:
            if self.propMgr and hasattr(self.propMgr, 'elementChooser'):
                try:
                    hybrid_name = self.propMgr.elementChooser.atomType                
                    atype = current_element.find_atomtype(hybrid_name)
                    if atype is not None:
                        self._pastable_atomtype = atype
                except:
                    print_compact_traceback("exception (ignored): ") 
                pass
            else:
                # we're presumably a subclass with no propMgr or a different one
                pass
        if self._pastable_atomtype is not None and self._pastable_atomtype.element is current_element:
            return self._pastable_atomtype
        self._pastable_atomtype = current_element.atomtypes[0]
        return self._pastable_atomtype
    
    def disable_selection_filter(self):
        """
        Disables the selection filter (if it is active)
        @see: The comment in BuildAtomsPropertyManager.set_selection_filter 
              for things to be done when connectWithState API is functional
              This method is a temporary implementation
        @see: BuildAtoms_GraphicsMode.keyPress() which calls this method when 
              Escape key is pressed. 
        """
        if self.w.selection_filter_enabled:
            # Uncheck (disable) the Atom Selection Filter and activate the 
            # Atom Tool.
            if self.propMgr.selectionFilterCheckBox:
                self.propMgr.selectionFilterCheckBox.setChecked(False) 
            return
        
        return
    
    def setElement(self, elementNumber):
        """
        Set the current (active) element to I{elementNumber}.
        
        @param elementNumber: Element number. (i.e. 6 = Carbon)
        @type  elementNumber: int
        """
        self.propMgr.setElement(elementNumber)
        return
    
class BuildAtoms_Command(BuildAtoms_basicCommand):
    """
    BuildAtoms_Command  
    @see: B{BuildAtoms_basicCommand}
    @see: cad/doc/splitting_a_mode.py
    """
    GraphicsMode_class = BuildAtoms_GraphicsMode
    
     ##### START of code copied from SelectAtoms_Command (except that the 
     ##### superclass name is different. 
    
    def __init__(self, commandSequencer):
        
        BuildAtoms_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        self._post_init_modify_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)
        return

    def _post_init_modify_GraphicsMode(self):
        pass
    
    ##### END of code copied from SelectAtoms_Command

    
