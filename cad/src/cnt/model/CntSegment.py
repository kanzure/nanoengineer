# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CntSegment.py - ... 

@author: Bruce, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
import foundation.env as env
from cnt.model.CntStrandOrSegment import CntStrandOrSegment
from cnt.model.CntLadderRailChunk import CntAxisChunk

from utilities.debug import print_compact_stack, print_compact_traceback
from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond
from geometry.VQT import V, norm, vlen
from cnt.model.Cnt_Constants import getCntRiseFromNumberOfCells

class CntSegment(CntStrandOrSegment):
    """
    Model object which represents a Cnt Segment inside a Cnt Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its CntAxisChunks and its
    CntSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its CntStrand
    atoms are not inside it; they are easily found from the CntAxisChunks.

    [Note: we might decide to put the CntStrandChunks inside the
     CntSegment whose axis they attach to, instead; for more info,
     see docstring of class CntStrand. bruce comment 080111]

    Note that this object will never show up directly in the Model Tree
    once the DNA Data Model is fully implemented, since it will always
    occur inside a CntGroup (and since it's not a Block).
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('CntSegment',)
    
    _cntRise = None
    _cellsPerTurn = None
        # TODO: undo or copy code for those attrs,
        # and updating them when the underlying structure changes.
        # But maybe that won't be needed, if they are replaced
        # by computing them from the atom geometry as needed.
        # [bruce 080227 comment]
        
    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)
    
    def __init__(self, name, assy, dad, members = (), editCommand = None):
        
        self._cntRise = 2.0 #Default value.
        self._cellsPerTurn = 10 #Default value
        
        CntStrandOrSegment.__init__(self, 
                                    name, 
                                    assy, 
                                    dad, 
                                    members = members, 
                                    editCommand = editCommand)
        ###BUG: not all callers pass an editCommand. It would be better
        # to figure out on demand which editCommand would be appropriate.
        # [bruce 080227 comment]
        return
        
    def edit(self):
        """
        Edit this CntSegment. 
        @see: CntSegment_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        if commandSequencer.currentCommand.commandName != "CNT_SEGMENT":
            commandSequencer.userEnterTemporaryCommand('CNT_SEGMENT')
            
        assert commandSequencer.currentCommand.commandName == 'CNT_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)
    

    #Following methods are likely to be revised in a fully functional dna data 
    # model. These methods are mainly created to get working many core UI 
    # operations for Rattlesnake.  -- Ninad 2008-02-01
     
    def kill_with_contents(self):  
        """
        Kill this Node including the 'logical contents' of the node. i.e. 
        the contents of the node that are self.members as well as non-members. 
        Example: A CntSegment's logical contents are AxisChunks and StrandChunks 
        Out of these, only AxisChunks are the direct members of the CntSegment
        but the 'StrandChunks are logical contents of it (non-members) . 
        So, some callers may specifically want to delete self along with its 
        members and logical contents. These callers should use this method. 
        The default implementation just calls self.kill()
        @see: B{Node.CntSegment.kill_with_contents}  which is overridden here
              method. 
        @see: EditCommand._removeStructure() which calls this Node API method
        @see: Cnt_EditCommand._removeSegments()
        @see: dna_model.CntLadder.kill_strand_chunks() for a comment.
        
        """   
        for member in self.members:
            
            if isinstance(member, CntAxisChunk):                
                ladder = member.ladder
                try:
                    #See a note in dna_model.kill_strand_chunks. Should we 
                    #instead call ladder.kill() and thus kill bothstrand 
                    #and axis chunks. ?
                    ladder.kill_strand_chunks()
                except:
                    print_compact_traceback("bug in killing the ladder chunk")
        
        CntStrandOrSegment.kill_with_contents(self)
        
    
    def getAxisEndAtoms(self):
        """
        To be modified post dna data model
        """
        #pre dna data model
        return self._getAxisEndAtoms_preDataModel()
        ##post dna data model ???
        ##return self.get_axis_end_baseatoms()???
        
    
    def _getAxisEndAtoms_preDataModel(self):
        """
        To be removed post dna data model
        """
        endAtomList = []
        for member in self.members:
            if isinstance(member, Chunk) and member.isAxisChunk():
                for atm in member.atoms.itervalues():
                    if atm.element.symbol == 'Ae3':                        
                        endAtomList.append(atm)
                                                    
        if len(endAtomList) == 2:            
            atm1 = endAtomList[0]
            atm2 = endAtomList[1]
            
            #Figure out which end point (atom) is which. endPoint1 will be the 
            #endPoint
            #on the left side of the 3D workspace and endPoint2 is the one on 
            #the 'more right hand side' of the 3D workspace.
            #It uses some code from bond_constants.bonded_atoms_summary
            # [following code is also duplicated in a method below]
            atmPosition1 = atm1.posn()
            atmPosition2 = atm2.posn()
            
            glpane = self.assy.o
            quat = glpane.quat
            vec = atmPosition2 - atmPosition1
            vec = quat.rot(vec)
            if vec[0] < 0.0:
                atm1, atm2 = atm2, atm1
            return atm1, atm2
        elif len(endAtomList) > 2:
            print_compact_stack("bug:The axis chunk has more than 2 'Ae' atoms")
        else:
            return None, None
        
        return endAtomList
    
    
    def getStrandEndAtomsFor(self, strand):
        """
        TODO: To be revised/ removed post dna data model. 
        returns the strand atoms connected to the ends of the 
        axis atoms. The list could return 1 or 2 strand atoms. The caller 
        should check for the correctness. 
        @see: CntStrand_EditCommand.updateHandlePositions()
        """
        assert strand.dad is self
        
        strandNeighbors = []
        strandEndAtomList = []
        
        for axisEndAtom in self.getAxisEndAtoms():
            strandNeighbors = axisEndAtom.strand_neighbors()
            strand_end_atom_found = False
            for atm in strandNeighbors:
                if atm.molecule is strand:
                    strandEndAtomList.append(atm)
                    strand_end_atom_found = True
                    break        
            if not strand_end_atom_found:
                strandEndAtomList.append(None)
      
        return strandEndAtomList
    
    def getStrandEndPointsFor(self, strand):
        """
        TODO: To be revised/ removed post dna data model.
        @see: CntStrand_EditCommand.updateHandlePositions()
        @see: self.getStrandEndAtomsFor()
        """
        strandEndAtoms = self.getStrandEndAtomsFor(strand)
        strandEndPoints = []
        for atm in strandEndAtoms:
            if atm is not None:
                strandEndPoints.append(atm.posn())
            else:
                strandEndPoints.append(None)
                
        return strandEndPoints
  

    def getAxisEndPoints(self):
        """
        Derives and returns the two axis end points based on the atom positions
        of the segment. 

        @note: this method definition doesn't fully make sense, since a segment
               can be a ring.
        
        @return: a list containing the two endPoints of the Axis.
        @rtype: list 
        """
        endpoint1, endpoint2 = self._getAxisEndPoints_preDataModel()
        if endpoint1 is None:
            return self._getAxisEndPoints_postDataModel()
        else:
            return (endpoint1, endpoint2)
        
    def _getAxisEndPoints_preDataModel(self):
        #Temporary implementation that uses chunk class to distinguish an 
        #axis chunk from an ordinary chunk. This method can be revised after
        #Full dna data model implementation -- Ninad 2008-01-21
        # (Note, this seems to assume that the axis is a single chunk.
        #  This may often be true pre-data-model, but I'm not sure --
        #  certainly it's not enforced, AFAIK. This will print_compact_stack
        # when more than one axis chunk is in a segment. [bruce 080212 comment])
        endPointList = []
        for atm in self.getAxisEndAtoms(): 
            if atm is not None:
                endPointList.append(atm.posn())
            else:
                endPointList.append(None)
                                    
        if len(endPointList) == 2:
            atmPosition1 = endPointList[0]
            atmPosition2 = endPointList[1]           
            
            return atmPosition1, atmPosition2
        
        return None, None
        

    def _getAxisEndPoints_postDataModel(self): # bruce 080212
        atom1, atom2 = self.get_axis_end_baseatoms()
        if atom1 is None:
            return None, None
        atmPosition1, atmPosition2 = [atom.posn() for atom in (atom1, atom2)]
        # following code is duplicated from a method above
        glpane = self.assy.o
        quat = glpane.quat
        vec = atmPosition2 - atmPosition1
        vec = quat.rot(vec)
        if vec[0] < 0.0:
            atmPosition1, atmPosition2 = atmPosition2, atmPosition1    
        return atmPosition1, atmPosition2

    def get_axis_end_baseatoms(self): # bruce 080212
        """
        Return a sequence of length 2 of atoms or None:
        for a chain: its two end baseatoms (arbitrary order);
        for a ring: None, None.
        """
        # this implem only works in the dna data model
        
        # find an arbitrary CntAxisChunk among our members
        # (not the best way in theory, once we have proper attrs set,
        #  namely our controlling marker)
        member = None
        for member in self.members:
            if isinstance(member, CntAxisChunk):
                break
        if not isinstance(member, CntAxisChunk):
            # no CntAxisChunk members (should not happen)
            return None, None
        end_baseatoms = member.wholechain.end_baseatoms()
        if not end_baseatoms:
            # ring
            return None, None
        # chain
        return end_baseatoms
        
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
        @see: Cnt_EditCommand.createStructure which calls this method. 
        @see: self.getProps, CntSegment_EditCommand.editStructure        
        """        
        
        cntRise, cellsPerTurn = props                
        self.setCntRise(cntRise) 
        self.setBasesPerTurn(cellsPerTurn)
        
                    
    def getProps(self):
        """
        Returns some properties such as cntRise. This is a temporary 
        @see: CntSegment_EditCommand.editStructure where it is used. 
        @see: CntSegment_PropertyManager.getParameters
        @see: CntSegmentEditCommand._createStructure        
        """                                    
        props = (self.getCntRise(), self.getBasesPerTurn())
        return props
    
    def getCntRise(self):
        return self._cntRise
    
    def setCntRise(self, cntRise):
        if cntRise:
            self._cntRise = cntRise   
    
    def getBasesPerTurn(self):
        return self._cellsPerTurn
            
    def setBasesPerTurn(self, cellsPerTurn):
        if cellsPerTurn:
            self._cellsPerTurn = cellsPerTurn
                   
    
    def _computeCntRise(self):
        """
        Compute the nanotube rise
        @see: self.getProps
        
        TODO: THIS METHOD IS DEPRECATED AS OF 2008-03-05 AND IS SCHEDULED
        FOR REMOVAL. IT MIGHT HAVE BUGS. 
        """
        cntRise = None
        numberOfAxisAtoms = self.getNumberOfAxisAtoms()   
        if numberOfAxisAtoms:
            numberOfBasePairs = numberOfAxisAtoms            
            cntLength = self.getSegmentLength()
            cntRise = getCntRiseFromNumberOfCells(numberOfBasePairs,
                                                  cntLength)
        return cntRise
    
    def getSegmentLength(self):
        """
        Returns the length of the segment.
        """
        endPoint1, endPoint2 = self.getAxisEndPoints()
        if endPoint1 is None:
            #bruce 080212 mitigate a bug
            env.history.orangemsg("Warning: segment length can't be determined")
            return 10
        segmentLength = vlen(endPoint1 - endPoint2)
        return segmentLength
    
           
    def getNumberOfAxisAtoms(self): # review: post dna data model version?
        """
        Returns the number of axis atoms present within this dna segment 
        Returns None if more than one axis chunks are present 
        This is a temporary method until dna data model is fully working. 
        @see: CntSegment_EditCommand.editStructure where it is used. 
        """
        axisChunkList = []
        numberOfAxisAtoms = None
        for m in self.members:
            if isinstance(m, Chunk) and m.isAxisChunk():
                axisChunkList.append(m)
        #@BUG: What if the segment has more than one axis chunks? 
        #We will only print a message for now in the console
        if len(axisChunkList) == 1:
            axisChunk = axisChunkList[0]
            
            numberOfAxisAtoms = len(axisChunk.atoms.values())
        
        return numberOfAxisAtoms
        
    def isAncestorOf(self, obj):
        """
        Checks whether the object <obj> is contained within the CntSegment
        
        Example: If the object is an Atom, it checks whether the 
        atom's chunk is a member of this CntSegment (chunk.dad is self)
        
        @see: CntSegment_GraphicsMode.leftDrag
        """
        #NOTE: Need to check if the isinstance checks are acceptable (apparently
        #don't add any import cycle) Also this method needs to be revised 
        #after we completely switch to dna data model. 
        if isinstance(obj, Atom):       
            chunk = obj.molecule                
            if chunk.dad is self:
                return True
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if (chunk1.dad is self) or (chunk2.dad is self):
                return True               
        elif isinstance(obj, Chunk):
            if obj.dad is self:
                return True
                
        return False    
        
                
# end
