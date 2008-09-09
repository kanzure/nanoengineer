# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildAtoms_Command.py 

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

The 'Command' part of the BuildAtoms Mode (BuildAtoms_Command and 
BuildAtoms_basicGraphicsMode are the two split classes of the old 
depositMode). It provides the command object for its GraphicsMode class. 
The Command class defines anything related to the 'command half' of the mode -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

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

Originally as 'depositMode.py' by Josh Hall and then significantly modified by 
several developers. 
In January 2008, the old depositMode class was split into new Command and 
GraphicsMode parts and the these classes were moved into their own module 
[ See BuildAtoms_Command.py and BuildAtoms_GraphicsMode.py]
"""
from PyQt4.Qt import QSize


import foundation.env as env
import foundation.changes as changes
from utilities.debug import print_compact_traceback
from utilities.prefs_constants import buildModeHighlightingEnabled_prefs_key
from utilities.prefs_constants import buildModeWaterEnabled_prefs_key
from utilities.prefs_constants import keepBondsDuringTransmute_prefs_key

from commands.BuildAtoms.BuildAtomsPropertyManager import BuildAtomsPropertyManager
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command

from command_support.GraphicsMode_API import GraphicsMode_API
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from ne1_ui.toolbars.Ui_BuildAtomsFlyout import BuildAtomsFlyout

#for debugging new command stack API 
from utilities.GlobalPreferences import USE_COMMAND_STACK 

_superclass = SelectAtoms_Command

class BuildAtoms_Command(SelectAtoms_Command):
    """
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported. 
    
    #GraphicsMode
    GraphicsMode_class = BuildAtoms_GraphicsMode
    
    #The class constant PM_class defines the class for the Property Manager of 
    #this command. See Command.py for more infor about this class constant 
    PM_class = BuildAtomsPropertyManager
    
    commandName = 'DEPOSIT'
    featurename = "Build Atoms Mode"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING

    highlight_singlets = True         
        
    #graphicsMode will be set in BuildAtoms_Command.__init__ . 
    graphicsMode = None
    
    flyoutToolbar = None
    
    _currentActiveTool = 'ATOMS_TOOL'
    
    def __init__(self, commandSequencer):
        _superclass.__init__(self, commandSequencer)    
                    
        #Initialize some more attributes. 
        self._pastable_atomtype = None
        
        #The following flag, if set to True, doesn't allow converting
        #bonds between the selected atoms to the bondtyp specified in the 
        #flyout toolbar. This is used only while activating the 
        #bond tool. See self._convert_bonds_bet_selected_atoms() for details
        self._supress_convert_bonds_bet_selected_atoms = False
        
    
    #START new command API methods =============================================
    #currently [2008-08-01 ] also called in by self,init_gui and 
    #self.restore_gui.
    
                
    def command_enter_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_flyout()  for documentation
        """
        if self.flyoutToolbar is None:
            self.flyoutToolbar = self._createFlyoutToolBarObject() 
        self.flyoutToolbar.activateFlyoutToolbar()  
        
    def _createFlyoutToolBarObject(self):
        """
        Create a flyout toolbar to be shown when this command is active. 
        Overridden in subclasses. 
        @see: PasteFromClipboard_Command._createFlyouttoolBar()
        @see: self.command_enter_flyout()
        """
        flyoutToolbar = BuildAtomsFlyout(self) 
        return flyoutToolbar        
            
    def command_exit_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_flyout()  for documentation
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.deActivateFlyoutToolbar()
            
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        self.w.toolsDepositAtomAction.setChecked(True)
            
    def command_exit_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_misc_actions()  for documentation
        """
        self.w.toolsDepositAtomAction.setChecked(False)  
        
    #END new command API methods ==============================================
    
    
    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command toolbar, connecting widget 
        slots etc. 
        
        Called once each time the mode is entered; should be called only by code 
        in modes.py
        
        @see: L{self.restore_gui}
        """      
                           
        self.command_enter_misc_actions()
        self.command_enter_PM() 
        self.command_enter_flyout()
        self.propMgr.show()
        return

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command toolbar, 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.command_exit_misc_actions()
        self.command_exit_flyout()
        self.command_exit_PM()
        if self.propMgr:
            self.propMgr.close()

    def enterToolsCommand(self, commandName = ''): #REVIEW
        """
        Enter the given tools subcommand (e.g. Atoms tool or one of the bond 
        tools)
        """
        if not commandName:
            return 
        
        commandSequencer = self.win.commandSequencer
        commandSequencer.userEnterTemporaryCommand( commandName)
        
    def getBondTypeString(self):
        """
        Overridden in subclasses. 
        """
        return ''
    
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

    def toggleShowOverlayText(self):
        if (self.o.selatom):
            chunk = self.o.selatom.molecule
            chunk.showOverlayText = not chunk.showOverlayText
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
            chunk = selatom.molecule
            if (chunk.chunkHasOverlayText):
                if (chunk.showOverlayText):
                    item = ('Hide overlay text on %r' % name, self.toggleShowOverlayText)
                else:
                    item = ('Show overlay text on %r' % name, self.toggleShowOverlayText)
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
    
    def isHighlightingEnabled(self):
        """
        overrides superclass method.  
        Note that this deprecates use of self.hover_highlighiting_enabled
        @see: anyCommand.isHighlightingEnabled()
        """
        return env.prefs[buildModeHighlightingEnabled_prefs_key]
    
    def isWaterSurfaceEnabled(self):
        """
        overrides superclass method.  
        @see: BuildAtoms_Command.isWaterSurfaceEnabled()
        
        """
        return env.prefs[buildModeWaterEnabled_prefs_key]
        
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
        ##return self.depositAtomsAction.isChecked()
        return self._currentActiveTool == 'ATOMS_TOOL'
    
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
        
        ##return not self.depositAtomsAction.isChecked()
        return self._currentActiveTool == 'BONDS_TOOL'
    
    def isDeleteBondsToolActive(self):
        """
        Overridden in subclasses. 
        Tells whether the Delete Bonds tool is active (boolean)
        @see: comment in self.isAtomsToolActive()
        """
        #Note: this method will be removed soon. 
        return False
        
    
    def activateAtomsTool(self):
        """
        Activate the atoms tool of the Build Atoms mode 
        hide only the Atoms Tools groupbox in the Build Atoms Property manager
        and show all others the others.
        """
                
        self._currentActiveTool = 'ATOMS_TOOL'
        
        self.propMgr.bondToolsGroupBox.hide()
        
        for grpbox in self.propMgr.previewGroupBox, self.propMgr.elementChooser:
            grpbox.show()
        
        self.propMgr.pw.propertyManagerScrollArea.ensureWidgetVisible(
            self.propMgr.headerFrame)
        
        self.graphicsMode.update_cursor()
        
        self.w.depositState = 'Atoms'
                
        self.propMgr.updateMessage()
        self.win.win_update()
               

    
    def activateBondsTool(self):
        """
        Activate the bond tool of the Build Atoms mode 
        Show only the Bond Tools groupbox in the Build Atoms Property manager
        and hide the others.
        @see:self._convert_bonds_bet_selected_atoms()
        """        
        
        self._currentActiveTool = 'BONDS_TOOL'
        
                        
        for widget in (self.propMgr.previewGroupBox,                        
                       self.propMgr.elementChooser,
                       self.propMgr.atomChooserComboBox):
            widget.hide()
            
            
                        
        self.propMgr.bondToolsGroupBox.show()
                
        self.propMgr.pw.propertyManagerScrollArea.ensureWidgetVisible(
            self.propMgr.headerFrame)
                
        

        #note: its okay if the check_action is None
        checked_action = self.flyoutToolbar.getCheckedBondToolAction()
        self.changeBondTool(action = checked_action)
        
        bondToolActions =  self.flyoutToolbar.getBondToolActions()
        for btn in self.propMgr.bondToolButtonRow.buttonGroup.buttons():
            btnId = self.propMgr.bondToolButtonRow.buttonGroup.id(btn)
            action = bondToolActions[btnId]
            btn.setIconSize(QSize(24,24))
            btn.setDefaultAction(action)
             
        self.win.win_update()

        
    def changeBondTool(self, action):
        """
        Change the bond tool (e.g. single, double, triple, aromatic 
        and graphitic) depending upon the checked action.
        @param: action is the checked bond tool action in the 
        bondToolsActionGroup
        """   
        bondTool_commandName = 'BOND_TOOL'
        
        if action is not None:
            objectName = action.objectName()
            prefix = 'ACTION_'
            #Note: objectName is a QString to convert it to a python string 
            #first
            objectName = str(objectName)
            if objectName and objectName.startswith(prefix):
                objectName = ''.join(objectName)
                bondTool_commandName = objectName[len(prefix):]
            
        self.enterToolsCommand(bondTool_commandName)
        
        
    #======================    
    # methods related to exiting this mode    
    
    # Now uses superclass method 'restore_patches()'. mark 060207.
    # [not true anymore, evidently -- so what does it use? bruce 071011]
    # [guessing it's more like restore_patches_by_GraphicsMode than _by_Command 
    # -- bruce 071012]
    #    def restore_patches_by_GraphicsMode(self):
    #        self.o.setDisplay(self.saveDisp) #bruce 041129; see notes for 
    #            # bug 133
    #        self.o.selatom = None

    def clear_command_state(self):
        self.new = None
    
    #=== Cursor id
    
    def get_cursor_id_for_active_tool(self):
        """
        Provides a cursor id (int) for updating cursor in graphics mode, 
        based on the checked action in its flyout toolbar. (i.e. based on the 
        active tool)
        @see: BuildAtoms_GraphicsMode.update_cursor_for_no_MB_selection_filter_disabled
        """
        if hasattr(self.flyoutToolbar, 'get_cursor_id_for_active_tool'):
            return self.flyoutToolbar.get_cursor_id_for_active_tool()
        
        return 0    
    
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
    