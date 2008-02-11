# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
from dna_model.DnaStrandOrSegment import DnaStrandOrSegment
from debug import print_compact_stack
from chunk import Chunk
from chem  import Atom
from bonds import Bond
from geometry.VQT import V, norm, vlen
from Dna_Constants import getDuplexRiseFromNumberOfBasePairs

class DnaSegment(DnaStrandOrSegment):
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its DnaAxisChunks and its
    DnaSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its DnaStrand
    atoms are not inside it; they are easily found from the DnaAxisChunks.

    [Note: we might decide to put the DnaStrandChunks inside the
     DnaSegment whose axis they attach to, instead; for more info,
     see docstring of class DnaStrand. bruce comment 080111]

    Note that this object will never show up directly in the Model Tree
    once the DNA Data Model is fully implemented, since it will always
    occur inside a DnaGroup (and since it's not a Block).
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaSegment',)
    
    _duplexRise = None
    _numberOfBasesPerTurn = None
    
    def __init__(self, name, assy, dad, members = (), editCommand = None):        
        self._duplexRise = None
        self._numberOfBasesPerTurn = None
        
        DnaStrandOrSegment.__init__(self, 
                                    name, 
                                    assy, 
                                    dad, 
                                    members = members, 
                                    editCommand = editCommand)
        
    def edit(self):
        """
        Edit this DnaSegment. 
        @see: DnaSegment_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        if commandSequencer.currentCommand.commandName != "DNA_SEGMENT":
            commandSequencer.userEnterTemporaryCommand('DNA_SEGMENT')
            
        assert commandSequencer.currentCommand.commandName == 'DNA_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)

    #Following methods are likely to be revised in a fully functional dna data 
    # model. These methods are mainly created to get working many core UI 
    # operations for Rattlesnake.  -- Ninad 2008-02-01

    def getAxisEndPoints(self):
        """
        Derives and returns the two axis end points based on the atom positions
        of the segment. 
        
        @return: a list containing the two endPoints of the Axis.
        @rtype: list 
        """
        #Temporary implementation that uses chunk class to distinguish an 
        #axis chunk from an ordinary chunk. This method can be revised after
        #Full dna data model implementation -- Ninad 2008-01-21
        endPointList = []
        for m in self.members:
            if isinstance(m, Chunk) and m.isAxisChunk():
                for atm in m.atoms.itervalues():
                    if atm.element.symbol == 'Ae3':                        
                        endPointList.append(atm.posn())
        if len(endPointList) == 2:
            #Figure out which end point is which. endPoint1 will be the endPoint
            #on the left side of the 3D workspace and endPoint2 is the one on 
            #the 'more right hand side' of the 3D workspace.
            #It uses some code from bond_constants.bonded_atoms_summary
            atmPosition1 = endPointList[0]
            atmPosition2 = endPointList[1]
            glpane = self.assy.o
            quat = glpane.quat
            vec = atmPosition2 - atmPosition1
            vec = quat.rot(vec)
            if vec[0] < 0.0:
                atmPosition1, atmPosition2 = atmPosition2, atmPosition1                            
            return atmPosition1, atmPosition2
        elif len(endPointList) > 2:
            print_compact_stack("bug:The axis chunk has more than 2 'Ae' atoms")
        else:
            return None, None
            
    def getAxisVector(self):
        """
        Returns the unit axis vector of the segment (vector between two axis 
        end points)
        """
        endPoint1, endPoint2 = self.getAxisEndPoints()
        if endPoint1 is not None and endPoint2 is not None:
            return norm(endPoint2 - endPoint1)
        else:
            return V(0, 0, 0)
        
    
    def setProps(self, props):
        """
        Sets some properties. These will be used while editing the structure. 
        (but if the structure is read from an mmp file, this won't work. As a 
        fall back, it returns some constant values) 
        @see: DnaDuplex_EditCommand.createStructure which calls this method. 
        @see: self.getProps, DnaSegment_EditCommand.editStructure        
        """        
        self._duplexRise, self._numberOfBasesPerTurn = props
                    
    def getProps(self):
        """
        Returns some properties such as duplexRise. This is a temporary 
        @see: DnaSegment_EditCommand.editStructure where it is used. 
        @see: DnaSegment_PropertyManager.getParameters
        @see: DnaSegmentEditCommand._createStructure        
        """
        
                
        numberOfBasePairs = self.getNumberOfAxisAtoms() 
        
        if self._duplexRise is None:
            self._duplexRise = self._computeDuplexRise() 
            
       
        if self._duplexRise is None:
            #If its still none , hard code it to 3.18 as a precaution. 
            self._duplexRise = 3.18
        
        if self._numberOfBasesPerTurn is None:
            self._numberOfBasesPerTurn = 10                   
                    
        props = (self._duplexRise, self._numberOfBasesPerTurn)
        return props
    
    def _computeDuplexRise(self):
        """
        Compute the duplex rise
        @see: self.getProps
        """
        duplexRise = None
        numberOfAxisAtoms = self.getNumberOfAxisAtoms()   
        if numberOfAxisAtoms:
            numberOfBasePairs = numberOfAxisAtoms            
            duplexLength = self.getSegmentLength()
            duplexRise = getDuplexRiseFromNumberOfBasePairs(numberOfBasePairs,
                                                            duplexLength)
        return duplexRise
    
    def getSegmentLength(self):
        """
        Returns the length of the segment.
        """
        endPoint1, endPoint2 = self.getAxisEndPoints()        
        segmentLength = vlen(endPoint1 - endPoint2)
        return segmentLength
    
           
    def getNumberOfAxisAtoms(self):
        """
        Returns the number of axis atoms present within this dna segment 
        Returns None if more than one axis chunks are present 
        This is a temporary method until dna data model is fully working. 
        @see: DnaSegment_EditCommand.editStructure where it is used. 
        """
        axisChunkList = []
        numberOfAxisAtoms = None
        for m in self.members:
            if isinstance(m, Chunk) and m.isAxisChunk():
                axisChunkList.append(m)
        #@BUG: What if the segment has more than one axis chunks? 
        #We will only print a message for now in the consol
        if len(axisChunkList) == 1:
            axisChunk = axisChunkList[0]
            
            numberOfAxisAtoms = len(axisChunk.atoms.values())
        
        return numberOfAxisAtoms
        
    def isAncestorOf(self, obj):
        """
        Checks whether the object <obj> is contained within the DnaSegment
        
        Example: If the object is an Atom, it checks whether the 
        atom's chunk is a member of this DnaSegment 
        
        @see: DnaSegment_GraphicsMode.leftDrag
        """
        #NOTE: Need to check if the isinstance checks are accptable (apparently
        #don't add any import cycle) Also this method needs to be revised 
        #after we completely switch to dna data model. 
        if isinstance(obj, Atom):       
            chunk = obj.molecule                
            if chunk in self.members:
                return True
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if (chunk1 in self.members) or (chunk2 in self.members):
                return True               
        elif isinstance(obj, Chunk):
            if obj in self.members:
                return True
                
        return False    
        
                
# end
