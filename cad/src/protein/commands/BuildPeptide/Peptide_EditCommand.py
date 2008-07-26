# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Piotr, Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-07-24: Created

TODO:
"""

from utilities.Log  import greenmsg
from command_support.EditCommand import EditCommand
from protein.commands.BuildPeptide.PeptideGenerator import PeptideGenerator
from utilities.constants import gensym
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode

_superclass = EditCommand
class Peptide_EditCommand(EditCommand):
    cmd              =  greenmsg("Build Peptide: ")
    sponsor_keyword  =  'Peptide'
    prefix           =  'Peptide'   # used for gensym
    cmdname          = 'Build Peptide'
    commandName      = 'BUILD_PEPTIDE'
    featurename      = 'Build Peptide'
    create_name_from_prefix  =  True 
    
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    structGenerator = PeptideGenerator()
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = True

                   
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
        Build a Peptide sheet from the parameters in the Property Manager.
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
        
        struct = self.structGenerator.make(self.win.assy,
                                           name, 
                                           params, 
                                           -self.win.glpane.pov)
               
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

        propMgr = self.win.createBuildPeptidePropMgr_if_needed(self)

        return propMgr
    
            
    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.Chunk