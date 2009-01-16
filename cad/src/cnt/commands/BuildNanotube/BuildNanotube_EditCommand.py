# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildNanotube_EditCommand.py

@author: Ninad
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2008-01-11: Created
"""

from command_support.EditCommand import EditCommand
from utilities.Log  import greenmsg

from ne1_ui.toolbars.Ui_NanotubeFlyout import NanotubeFlyout

from model.chem import Atom 
from model.bonds import Bond

from cnt.commands.BuildNanotube.BuildNanotube_GraphicsMode import BuildNanotube_GraphicsMode
from cnt.commands.BuildNanotube.BuildNanotube_PropertyManager import BuildNanotube_PropertyManager

_superclass = EditCommand
class BuildNanotube_EditCommand(EditCommand):
    """
    BuildNanotube_EditCommand provides a convenient way to insert or edit 
    a Nanotube.
    """

    # class constants
    GraphicsMode_class = BuildNanotube_GraphicsMode
    
    PM_class = BuildNanotube_PropertyManager
    
    #Flyout Toolbar
    FlyoutToolbar_class = NanotubeFlyout
    
    cmd              =  greenmsg("Build Nanotube: ")
    prefix           =  'Nanotube' # used for gensym
    cmdname          = "Build Nanotube"

    commandName       = 'BUILD_NANOTUBE'
    featurename       = "Build Nanotube"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING
    command_should_resume_prevMode = False
    command_has_its_own_PM = True
    create_name_from_prefix  =  True 

    #The following class constant is used in creating dynamic menu items (using self.makeMenus)
    #if this flag is not defined, the menu doesn't get created
    #or use of self.graphicsMode in self.makeMenus throws errors. 
    #See also other examples of its use in older Commands such as 
    #BuildAtoms_Command (earlier depositmode) 
    call_makeMenus_for_each_event = True
    
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        self.w.buildNanotubeAction.setChecked(True)
        return

    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None     
        self.existingStructForEditing = False
        self.propMgr.updateNanotubesListWidget()
        return

    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that cnt_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """

        bool_keep = EditCommand.keep_empty_group(self, group)

        if not bool_keep:     
            if group is self.struct:
                bool_keep = True

        return bool_keep

    def makeMenus(self): 
        """
        Create context menu for this command. (Build Nanotube mode)
        @see: chunk.make_glpane_cmenu_items
        @see: EditNanotube_EditCommand.makeMenus
        """
        if not hasattr(self, 'graphicsMode'):
            return

        selobj = self.glpane.selobj

        if selobj is None:
            self._makeEditContextMenus()
            return

        self.Menu_spec = []

        highlightedChunk = None
        if isinstance(selobj, self.assy.Chunk):
            highlightedChunk = selobj
        if isinstance(selobj, Atom):
            highlightedChunk = selobj.molecule
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2 and chunk1 is not None:
                highlightedChunk = chunk1

        if highlightedChunk is not None:
            highlightedChunk.make_glpane_cmenu_items(self.Menu_spec, self)
        return
