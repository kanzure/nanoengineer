# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
SelectAtoms_Command.py 

The 'Command' part of the SelectAtoms Mode (SelectAtoms_basicCommand and 
SelectAtoms_basicGraphicsMode are the two split classes of the old 
selectAtomsMode)  It provides the command object for its GraphicsMode class. 
The Command class defines anything related to the 'command half' of the mode -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py 
- Other items listed in Select_Command.py

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectAtomsMode and moved the 
                          Command related methods into this class from 
                          selectAtomsMode.py

"""
from utilities import debug_flags
from utilities.debug import print_compact_traceback
from utilities.debug import reload_once_per_event

from commands.Select.Select_Command import Select_basicCommand
from command_support.GraphicsMode_API import GraphicsMode_API
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode

class SelectAtoms_basicCommand(Select_basicCommand):
    """
    SelectAtoms_basicCommand
    The 'Command' part of the SelectAtoms Mode (SelectAtoms_basicCommand and 
    SelectAtoms_basicGraphicsMode are the two split classes of the old 
    selectAtomsMode)  It provides the command object for its GraphicsMode class. 
    The Command class defines anything related to the 'command half' of the 
    mode -- 
    For example: 
    - Anything related to its current Property Manager, its settings or state
    - The model operations the command does (unless those are so simple
      that the mouse event bindings in the _GM half can do them directly
      and the code is still clean, *and* no command-half subclass needs
      to override them).
    """
    commandName = 'SELECTATOMS'
    featurename = "Select Atoms Mode"
    from utilities.constants import CL_ABSTRACT
    command_level = CL_ABSTRACT #??
    
    # Don't highlight singlets in selectAtomsMode. Fixes bug 1540.mark 060220.
    highlight_singlets = False         
        
    def Enter(self): 
        Select_basicCommand.Enter(self)        
        
        self.w.win_update()
            #k needed? I doubt it, I bet caller of Enter does it
            # [bruce comment 050517]
        return
    
    call_makeMenus_for_each_event = True     
    
    def makeMenus(self): 
        selatom, selobj = self.graphicsMode.update_selatom_and_selobj(None)

        self.Menu_spec = []

        # Local minimize [now called Adjust Atoms in history/Undo,
        #Adjust <what> here and in selectMode -- mark & bruce 060705]
        # WARNING: This code is duplicated in depositMode.makeMenus(). 
        #--mark 060314.
        if selatom is not None and \
           not selatom.is_singlet() and \
           self.w.simSetupAction.isEnabled():
            
            # see comments in depositMode version
            self.Menu_spec.append((
                "Adjust atom %s" % selatom, 
                lambda e1 = None, a = selatom: self.localmin(a, 0) ))
            
            self.Menu_spec.append((
                "Adjust 1 layer", 
                lambda e1 = None, a = selatom: self.localmin(a, 1) ))
            
            self.Menu_spec.append((
                "Adjust 2 layers", 
                lambda e1 = None, a = selatom: self.localmin(a, 2) ))

        # selobj-specific menu items. [revised by bruce 060405; 
        #for more info see the same code in depositMode]
        if selobj is not None and hasattr(selobj, 'make_selobj_cmenu_items'):
            try:
                selobj.make_selobj_cmenu_items(self.Menu_spec)
            except:
                print_compact_traceback("bug: exception (ignored) in "
                                        "make_selobj_cmenu_items "
                                        "for %r: " % selobj)

        # separator and other mode menu items.
        if self.Menu_spec:
            self.Menu_spec.append(None)

        # Enable/Disable Jig Selection.
        # This is duplicated in depositMode.makeMenus() and 
        # SelectChunks_Command.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [("Enable Jig Selection",  
                                     self.graphicsMode.toggleJigSelection, 
                                     'checked')])
        else:
            self.Menu_spec.extend( [("Enable Jig Selection", 
                                     self.graphicsMode.toggleJigSelection, 
                                     'unchecked')])

        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ("Edit Color Scheme...", self.w.colorSchemeCommand),
        ])

        return # from makeMenus
    
    # Local minimize [now called Adjust Atoms in history/Undo, Adjust <what> 
    #in menu commands -- mark & bruce 060705]
    def localmin(self, atom, nlayers): #bruce 051207 #e might generalize to 
                                       #take a list or pair of atoms, other 
                                       #options
        if debug_flags.atom_debug:
            print "debug: reloading sim_commandruns on each use, for development"\
                  "[localmin %s, %d]" % (atom, nlayers)
            import simulation.sim_commandruns as sim_commandruns
            reload_once_per_event(sim_commandruns) #bruce 060705 revised this
        if 1:
            # this does not work, 
            #I don't know why, should fix sometime: [bruce 060705]
            self.set_cmdname("Adjust Atoms") # for Undo (should we be more 
                                             #specific, like the menu text was? 
                                             #why didn't that get used?)
        from simulation.sim_commandruns import LocalMinimize_function # should not be toplevel
        LocalMinimize_function( [atom], nlayers )
        return


class SelectAtoms_Command(SelectAtoms_basicCommand):
    """
    SelectAtoms_Command  
    @see: B{SelectAtoms_basicCommand}
    @see: cad/doc/splitting_a_mode.py
    """
    GraphicsMode_class = SelectAtoms_GraphicsMode
    
    def __init__(self, commandSequencer):
        SelectAtoms_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)

