# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGroup.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.Block import Block

from icon_utilities import imagename_to_pixmap

# Following import is disabled. See addSegment method for reason.
## from dna_model.DnaSegment import DnaSegment

class DnaGroup(Block):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    The contents are not directly visible to the user in the model tree,
    except for Blocks (fyi, this behavior comes from our Block superclass,
    which is a kind of Group).
    
    But internally, most of the contents are Nodes which can be stored
    in mmp files, copied, and undo-scanned in the usual ways.

    Specific kinds of Group member contents include:
    - DnaStrands (optionally inside Blocks)
    - DnaSegments (ditto)
    - Blocks (a kind of Group)
    - DnaAtomMarkers (a kind of Jig, probably always inside an owning
      DnaStrand or DnaSegment)
    - specialized chunks for holding PAM atoms:
      - DnaAxisChunk (undecided whether these will live inside DnaSegments
        they belong to, but probably they will)
      - DnaStrandChunk (undecided whether these will live inside their
        DnaStrands, but probably they will)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes.
    """
    
    
    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  
    iconPath = "modeltree/DNA.png"
    
    mmp_record_name = 'DnaGroup'
    #@@@State of the Dna Group in the Model Tree (open or closed) By default
    #this should be 'closed'
    open = False
    
    def node_icon(self, display_prefs):
        """
        Model Tree node icon for the dna group node. 
        """
        #Delete the unused display_prefs parameter
        del display_prefs    
        
        return imagename_to_pixmap(self.iconPath)
       
        
    # example method:
    def get_segments(self):
        """
        Return a list of all our DnaSegment objects.
        """
        return self.get_subnodes_of_class("DnaSegment") # IMPLEM get_subnodes_of_class
    

    def addSegment(self, segment):
        """
        Adds a new segment object for this dnaGroup.
        
        @param segment: The DnaSegment to be added to this DnaGroup object
        @type: B{DnaSegment}  
        """
        # importing DnaSegment created an import cycle which throws error. 
        # So the isinstance check is is disabled for now.
        ## assert isinstance(segment, DnaSegment)
        
        self.addchild(segment)

    def getProps(self):
        """
	Method to support Dna duplex editing. see Group.__init__ for 
	a comment
        
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it supply the Dna Segment list (children) and then add 
        #individual segments when setProps is called?? 
        if self.editCommand:
            props = ()
            return props

    def setProps(self, props):
        """
	Method  to support Dna duplex editing. see Group.__init__ for 
	a comment
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it accept the Dna Segment list and then add individual segments?
        pass
    
    def edit(self):
        """
        @see: Group.edit()
        """
        
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('BUILD_DNA')
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'BUILD_DNA'
        currentCommand.editStructure(self)

# end
