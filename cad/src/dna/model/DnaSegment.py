# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py 


*DnaSegment has the following direct members --
       -- DnaAxisChunks, 
       -- DnaSegmentMarkers
*It can also have following logical contents --
      -- DnaStrandChunks  (can be accessed using DnaAxisChunk.ladder) 
      -- DnaStrandMarkers
      -- may be some more?

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
import foundation.env as env
from dna.model.DnaStrandOrSegment import DnaStrandOrSegment
from dna.model.DnaLadderRailChunk import DnaAxisChunk

from utilities.debug import print_compact_stack, print_compact_traceback
from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond
from geometry.VQT import V, norm, vlen
from dna.model.Dna_Constants import getDuplexRiseFromNumberOfBasePairs

from utilities.icon_utilities import imagename_to_pixmap

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
    [WRONG as of before 080318 -- behavior has been revised]
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaSegment',)
    
    _duplexRise = None
    _basesPerTurn = None
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
        
        self._duplexRise = 3.18 #Default value.
        self._basesPerTurn = 10 #Default value
        
        DnaStrandOrSegment.__init__(self, 
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
     
    def kill_with_contents(self):  
        """
        Kill this Node including the 'logical contents' of the node. i.e. 
        the contents of the node that are self.members as well as non-members. 
        Example: A DnaSegment's logical contents are AxisChunks and StrandChunks 
        Out of these, only AxisChunks are the direct members of the DnaSegment
        but the 'StrandChunks are logical contents of it (non-members) . 
        So, some callers may specifically want to delete self along with its 
        members and logical contents. These callers should use this method. 
        The default implementation just calls self.kill()
        @see: B{Node.DnaSegment.kill_with_contents}  which is overridden here
              method. 
        @see: EditCommand._removeStructure() which calls this Node API method
        @see: DnaDuplex_EditCommand._removeSegments()
        @see: dna_model.DnaLadder.kill_strand_chunks() for a comment.
        
        """   
        for member in self.members:            
            if isinstance(member, DnaAxisChunk):                
                ladder = member.ladder
                try:
                    #See a note in dna_model.kill_strand_chunks. Should we 
                    #instead call ladder.kill() and thus kill bothstrand 
                    #and axis chunks. ?
                    ladder.kill_strand_chunks()
                except:
                    print_compact_traceback("bug in killing the ladder chunk")
        
        DnaStrandOrSegment.kill_with_contents(self)
    
    def get_all_content_chunks(self):
        """
        Return all the chunks contained within this DnaSegment. This includes 
        the chunks which are members of the DnaSegment groups and also the ones
        which are not 'members' but are 'logical contents' of this DnaSegment
        e.g. in dna data model, the DnaSegment only has DnaAxisChunks as its 
        members. But the DnaStrand chunks to which these axis atoms are
        connected can be treated as logical contents of the DnaSegment. 
        This method returns all such chunks (including the direct members) 
        @see: DnaSegment_GraphicsMode.leftDrag() where this list is used to 
              drag the whole DnaSegment including the logical contents. 
        
        """
        all_content_chunk_list = []
                    
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                ladder = member.ladder
                all_content_chunk_list.extend(ladder.all_chunks())
            elif isinstance(member, Chunk):
                if member.isAxisChunk() or member.isStrandChunk():
                    #This code will only be called when dna_updater is disabled
                    #the conditional check should be removed post dna_data model
                    all_content_chunk_list.append(member)
        
        return all_content_chunk_list 
    
    
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
            print_compact_stack("bug: The axis chunk has more than 2 'Ae3' atoms: ")
        else:
            return None, None
        
        return endAtomList
    
    
    def getStrandEndAtomsFor(self, strand):
        """
        TODO: To be revised/ removed post dna data model. 
        returns the strand atoms connected to the ends of the 
        axis atoms. The list could return 1 or 2 strand atoms. The caller 
        should check for the correctness. 
        @see: DnaStrand_EditCommand.updateHandlePositions()
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
        @see: DnaStrand_EditCommand.updateHandlePositions()
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
        
        # find an arbitrary DnaAxisChunk among our members
        # (not the best way in theory, once we have proper attrs set,
        #  namely our controlling marker)
        member = None
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                break
        if not isinstance(member, DnaAxisChunk):
            # no DnaAxisChunk members (should not happen)
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
        @see: DnaDuplex_EditCommand.createStructure which calls this method. 
        @see: self.getProps, DnaSegment_EditCommand.editStructure        
        """        
        
        duplexRise, basesPerTurn = props                
        self.setDuplexRise(duplexRise) 
        self.setBasesPerTurn(basesPerTurn)
        
                    
    def getProps(self):
        """
        Returns some properties such as duplexRise. This is a temporary 
        @see: DnaSegment_EditCommand.editStructure where it is used. 
        @see: DnaSegment_PropertyManager.getParameters
        @see: DnaSegmentEditCommand._createStructure        
        """                                    
        props = (self.getDuplexRise(), self.getBasesPerTurn())
        return props
    
    def getDuplexRise(self):
        return self._duplexRise
    
    def setDuplexRise(self, duplexRise):
        if duplexRise:
            self._duplexRise = duplexRise   
    
    def getBasesPerTurn(self):
        return self._basesPerTurn
            
    def setBasesPerTurn(self, basesPerTurn):
        if basesPerTurn:
            self._basesPerTurn = basesPerTurn
                   
    
    def _computeDuplexRise(self):
        """
        Compute the duplex rise
        @see: self.getProps
        
        TODO: THIS METHOD IS DEPRECATED AS OF 2008-03-05 AND IS SCHEDULED
        FOR REMOVAL. IT MIGHT HAVE BUGS. 
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
        @see: DnaSegment_EditCommand.editStructure where it is used. 
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
        Checks whether the object <obj> is contained within the DnaSegment
        
        Example: If the object is an Atom, it checks whether the 
        atom's chunk is a member of this DnaSegment (chunk.dad is self)
        
        It also considers all the logical contents of the DnaSegment to determine
        whetehr self is an ancestor. (returns True even for logical contents)
        
                
        @see: self.get_all_content_chunks()
        @see: DnaSegment_GraphicsMode.leftDrag
        
        @Note: when dna data model is fully implemented, the code below that is 
        flaged 'pre-Dna data model' and thus the method should be revised 
        """
        
        #start of POST DNA DATA MODEL IMPLEMENTATION ===========================
        c = None
        if isinstance(obj, Atom):       
           c = obj.molecule                 
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if chunk1 is chunk2:
                c = chunk1
        elif isinstance(obj, Chunk):
            c = obj
        
        if c is not None:
            if c in self.get_all_content_chunks():
                return True        
        #end of POST DNA DATA MODEL IMPLEMENTATION =============================    
        
        #start of PRE- DNA DATA MODEL IMPLEMENTATION ===========================
        
        #NOTE: Need to check if the isinstance checks are acceptable (apparently
        #don't add any import cycle) Also this method needs to be revised 
        #after we completely switch to dna data model. 
        if isinstance(obj, Atom):       
            chunk = obj.molecule                
            if chunk.dad is self:
                return True
            else:
                ladder = getattr(chunk, 'ladder', None)
                if ladder:
                    pass
                
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if (chunk1.dad is self) or (chunk2.dad is self):
                return True               
        elif isinstance(obj, Chunk):
            if obj.dad is self:
                return True
        #end of PRE- DNA DATA MODEL IMPLEMENTATION ===========================
                
        return False
    
    def node_icon(self, display_prefs):
        open = display_prefs.get('open', False)
        if open:
            return imagename_to_pixmap("modeltree/DnaSegment.png")
        else:
            return imagename_to_pixmap("modeltree/DnaSegment.png")
        
                
# end
