# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Graphene_EditCommand.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-22: Ported the old graphene generator to the Editcommand API

TODO:
- Needs cleanup after command sequencer refactoring. The graphene generator
was ported to EditCommand API to help the commandSequencer refactoring project. 
"""


from utilities.Log  import greenmsg
from command_support.EditCommand import EditCommand
from commands.InsertGraphene.GrapheneGenerator import GrapheneGenerator
from utilities.constants import gensym
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode

_superclass = EditCommand
class Graphene_EditCommand(EditCommand):
    cmd              =  greenmsg("Build Graphene: ")
    prefix           =  'Graphene'   # used for gensym
    cmdname          = 'Build Graphene'

    commandName      = 'BUILD_GRAPHENE'
    featurename      = "Build Graphene"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING # for now; later might be subcommand of Build Nanotube??

    create_name_from_prefix  =  True 
    
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    def _gatherParameters(self):
        """
        Return the parameters from the property manager.
        """
        return self.propMgr.getParameters()  
    
    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None
    
    def _createStructure(self):        
        """
        Build a graphene sheet from the parameters in the Property Manager.
        """
        
        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
            
            
        params = self._gatherParameters()
        
        #
        self.win.assy.part.ensure_toplevel_group()
        
        structGenerator = GrapheneGenerator()
        
        struct = structGenerator.make(self.win.assy,                                      
                                      name, 
                                      params, 
                                      editCommand = self)
        
       
        self.win.assy.part.topnode.addmember(struct)
        self.win.win_update()
        return struct
        
    
    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. 
        See more comments in this method.
        """
        
        #@NOTE: Unlike editcommands such as Plane_EditCommand or 
        #DnaSegment_EditCommand this  actually removes the structure and
        #creates a new one when its modified. 
        #TODO: Change this implementation to make it similar to whats done 
        #iin DnaSegment resize. (see DnaSegment_EditCommand)
        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
    
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr

        propMgr = self.win.createBuildGraphenePropMgr_if_needed(self)

        return propMgr
    
            
    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.Chunk
        
        
    
    
    
    
    
