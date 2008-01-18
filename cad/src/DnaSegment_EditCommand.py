# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO: As of 2008-01-18
Several Things. This class is just a stub and all it does is enter the command 
and show property manager. Nothing else is implemented.
"""

from EditCommand import EditCommand 
from DnaLineMode import DnaLine_GM


class DnaSegment_EditCommand(EditCommand):
    cmd              =  'Dna Segment'
    sponsor_keyword  =  'DNA'
    prefix           =  'Segment '   # used for gensym
    cmdname          = "DNA_SEGMENT"
    commandName       = 'DNA_SEGMENT'
    featurename       = 'Build DNA_SEGMENT'
   
    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False
    
    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    #Graphics Mode set to DnaLine graphics mode
    GraphicsMode_class = DnaLine_GM
    
    #required by DnaLine_GM
    mouseClickPoints = []
    
    
    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None
    
        
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createDnaSegmentPropMgr_if_needed(self)
        return propMgr
    
    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfBases
                 - dnaForm
                 - basesPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """     
        return None

    
    
