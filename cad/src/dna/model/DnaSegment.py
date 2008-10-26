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
from utilities.Comparison     import same_vals
from utilities.constants import MODEL_PAM3

from dna.model.Dna_Constants    import getNumberOfBasePairsFromDuplexLength

_superclass = DnaStrandOrSegment
class DnaSegment(DnaStrandOrSegment):
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its DnaAxisChunks and its
    DnaSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its DnaStrand
    atoms are not inside it; they are easily found from the DnaAxisChunks.
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
        
    iconPath = "ui/modeltree/DnaSegment.png"
    hide_iconPath = "ui/modeltree/DnaSegment-hide.png"
    
    def __init__(self, name, assy, dad, members = (), editCommand = None):
        
        self._duplexRise = 3.18 #Default value.
        self._basesPerTurn = 10 #Default value
        
        _superclass.__init__(self, 
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
        commandSequencer.userEnterCommand('DNA_SEGMENT')
        assert commandSequencer.currentCommand.commandName == 'DNA_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)
        
    def draw_highlighted(self, glpane, color):
        """
        Draw the strand and axis chunks as highlighted. (Calls the related 
        methods in the chunk class)
        @param: GLPane object 
        @param color: The highlight color
        @see: Chunk.draw_highlighted()
        @see: SelectChunks_GraphicsMode.draw_highlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()        
        """            
        #Note: As of 2008-04-07, there is no 'highlightPolicy' for 
        #a DnaSegment like in DnaStrand. 
        #(Not needed but can be easily implemented)
        
        for c in self.members: 
            if isinstance(c, DnaAxisChunk):
                c.draw_highlighted(glpane, color)   
                
    
    def getNumberOfBasePairs(self):  
        #@REVIEW: Is it okay to simply return the number of axis atoms within 
        #the segment (like done below)? But what if there is a bare axis atom 
        #within the segment?In any case, the way we compute the numberOfBase 
        #pairs is again an estimatebased on the duplex length! (i.e. it doesn't 
        #count the individual base-pairs. BTW, a segment may even have a single 
        #strand,so the word basepair is not always correct. -- Ninad 2008-04-08
        numberOfBasePairs = self.getNumberOfAxisAtoms()
            
        return numberOfBasePairs
        
    
    def getNumberOfAxisAtoms(self): 
        """
        Returns the number of axis atoms present within this dna segment 
        Returns None if more than one axis chunks are present 
        This is a temporary method until dna data model is fully working. 
        @see: DnaSegment_EditCommand.editStructure() where it is used. 
        """
        #THIS WORKS ONLY WITH DNA DATA MODEL. pre-dna data model implementation
        #rfor this method not supported -- Ninad 2008-04-08
        numberOfAxisAtoms = 0        
        for m in self.members:
            if isinstance(m, DnaAxisChunk):
                numberOfAxisAtoms += len(m.get_baseatoms())
                       
        return numberOfAxisAtoms
    
    def isEmpty(self):
        """
        Returns True if there are no axis chunks as its members.
        """
        for m in self.members:
            if isinstance(m, DnaAxisChunk):
                return False
            
        return True

    #Following methods are likely to be revised in a fully functional dna data 
    # model. These methods are mainly created to get working many core UI 
    # operations for Rattlesnake.  -- Ninad 2008-02-01
    
    def kill(self):
        """
        Overrides superclass method. For a Dnasegment , as of 2008-04-09,
        the default implementation is that deleting a segment will delete 
        the segment along with its logical contents (see bug 2749).
        It is tempting to call self.kill_with_contents , BUT DON'T CALL IT HERE!
        ...as kill_with_contents  is used elsewhere (before bug 2749 NFR was
        suggested and it calls self.kill() at the end. So that will create 
        infinite recursions. 
        @TODO: code cleanup/ refactoring to resolve kill_with_content issue
        """
        
        #The following block is copied over from self.kill_with_contents()
        #It implements behavior suggested in bug 2749 (deleting a segment will 
        #delete the segment along with its logical contents )
        #See method docsting above on why we shouldn't call that method instead
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
                    
        DnaStrandOrSegment.kill(self)
           
     
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
        
        @see: A note in self.kill() about NFR bug 2749
        
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
        
    def get_DnaSegments_reachable_thru_crossovers(self):
        """
        Return a list of DnaSegments that are reachable through the crossovers.
        
        @see: ops_select_Mixin.expandDnaComponentSelection()
        @see: ops_select_Mixin.contractDnaComponentSelection()
        @see: ops_select_Mixin._expandDnaStrandSelection()
        @see:ops_select_Mixin._contractDnaStrandSelection()
        @see: ops_select_Mixin._contractDnaSegmentSelection()
        @see: DnaStrand.get_DnaStrandChunks_sharing_basepairs()
        @see: DnaSegment.get_DnaSegments_reachable_thru_crossovers()
        @see: NFR bug 2749 for details.
        @see: SelectChunks_GraphicsMode.chunkLeftDouble()
        """
        neighbor_segments = []
        content_strand_chunks = self.get_content_strand_chunks()
        for c in content_strand_chunks:
            strand_rail = c.get_ladder_rail()
            for atm in strand_rail.neighbor_baseatoms:
                if not atm:
                    continue               
                axis_neighbor = atm.axis_neighbor()
                if not axis_neighbor:
                    continue
                dnaSegment = axis_neighbor.molecule.parent_node_of_class(DnaSegment)
                if dnaSegment and dnaSegment is not self:
                    if dnaSegment not in neighbor_segments:
                        neighbor_segments.append(dnaSegment)
                        
        return neighbor_segments
    
    def get_content_strand_chunks(self):
        """
        """
        content_strand_chunks = []
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                ladder = member.ladder
                content_strand_chunks.extend(ladder.strand_chunks())
                
        return content_strand_chunks
            
    
    def getAllAxisAtoms(self):
        allAtomList = []
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                allAtomList.extend(member.atoms.values())
                
        return allAtomList
    
    def get_all_content_strand_atoms(self):
        """
        Return a list of all strand atoms contained within this DnaSegment
        """
        ladders = self.getDnaLadders()        
        
        strand_rails = []        
        for ladder in ladders:
            strand_rails.extend(ladder.strand_rails)
            
        strand_atoms = []
        for rail in strand_rails:
            strand_atoms.extend(rail.baseatoms)
        return strand_atoms
    
    def get_all_content_three_prime_ends(self):
        """
        Return a list of all the three prime end base atoms, contained within
        this DnaSegment
        @see:self.get_all_content_strand_atoms()
        @see:self.get_all_content_five_prime_ends()
        """
        strand_atoms = self.get_all_content_strand_atoms()
        
        three_prime_end_atoms = filter(lambda atm: atm.isThreePrimeEndAtom(), 
                                       strand_atoms)
        return three_prime_end_atoms
    
    
    def get_all_content_five_prime_ends(self):
        """
        Return a list of all the five prime end base atoms, contained within
        this DnaSegment
        @see:self.get_all_content_strand_atoms()
        @see:self.get_all_content_three_prime_ends()
        """
        strand_atoms = self.get_all_content_strand_atoms()
        
        five_prime_end_atoms = filter(lambda atm: atm.isFivePrimeEndAtom(), 
                                       strand_atoms)
        return five_prime_end_atoms
           
  
    def is_PAM3_DnaSegment(self):
        """
        Returns true if all the baseatoms in the DnaLadders of this segment
        are PAM3 baseatoms (axis or strands) Otherwise returns False
        @see: DnaSegment_EditCommand.model_changed()
        @see: DnaSegment_EditCommand.isResizableStructure()
        """          
        is_PAM3 = False      
        
        ladderList = self.getDnaLadders()        
        if len(ladderList) == 0:
            is_PAM3 = False
            
        for ladder in ladderList:
            pam_model = ladder.pam_model()
            if pam_model == MODEL_PAM3:
                is_PAM3 = True
            else:
                is_PAM3 = False
                break
        
        return is_PAM3
     
    def getDnaLadders(self):
        """
        Returns a list of all DnaLadders within this segment
        """
        ladderList = []
        
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                ladder = member.ladder
                if ladder not in ladderList:
                    ladderList.append(ladder)
        
        return ladderList
    
    def get_wholechain(self):
        """
        Return the 'wholechain' of this DnaSegment. Method provided for 
        convenience.
        Delegates this to self.get_segment_wholechain()
        """
        return self.get_segment_wholechain()
    
    def get_segment_wholechain(self):
        """
        @return: the 'wholechain' of this DnaSegment
                 (same as wholechain of each of its DnaAxisChunks),
                 or None if it doesn't have one
                 (i.e. if it's empty -- should never happen
                 if called on a live DnaSegment not modified since
                 the last dna updater run).
        
        @see: Wholechain
        @see: get_strand_wholechain
        """
        for member in self.members:
            if isinstance(member, DnaAxisChunk):
                return member.wholechain
        return None

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
    
    def getAxisEndAtomAtPosition(self, position):
        """
        Given a position, return the axis end atom at that position (if it 
        exists)
        """
        axisEndAtom = None
        endAtom1, endAtom2 = self.getAxisEndAtoms()    
        for atm in (endAtom1, endAtom2):
            if atm is not None and same_vals(position,  atm.posn()):
                axisEndAtom = atm
                break
        return axisEndAtom   
    
    def getOtherAxisEndAtom(self, axisEndAtom):
        """
        Return the axis end atom at the opposite end 
        @param axisEndAtom: Axis end atom at a given end. We will use this to 
                           find the axis end atom at the opposite end.
        """
        #@TODO: 
        #1. Optimize this further?
        #2. Can a DnaSegment have more than two axis end atoms? 
        #I guess 'No' . so okay to do the following -- Ninad 2008-03-24
        other_axisEndAtom = None
        endAtom1, endAtom2 = self.getAxisEndAtoms()
        for atm in (endAtom1, endAtom2):
            if atm is not None and not atm is axisEndAtom:
                other_axisEndAtom = atm
        
        return other_axisEndAtom
                    
            
    def getAxisEndAtoms(self):
        """
        THIS RETURNS AXIS END ATOMS ONLY FOR DNA DATA MODEL. 
        DOESN'T ANYMORE SUPPORT THE PRE DATA MODEL CASE -- 2008-03-24
        """        
        #pre dna data model
        ##return self._getAxisEndAtoms_preDataModel()
        
        #post dna data model
        return self._getAxisEndAtoms_postDataModel()
    
    def _getAxisEndAtoms_postDataModel(self):
        """
        """
        atm1, atm2 = self.get_axis_end_baseatoms()
        #Figure out which end point (atom) is which. endPoint1 will be the 
        #endPoint
        #on the left side of the 3D workspace and endPoint2 is the one on 
        #the 'more right hand side' of the 3D workspace.
        #It uses some code from bond_constants.bonded_atoms_summary
        # [following code is also duplicated in a method below]
        if atm1 and atm2:
            atmPosition1 = atm1.posn()
            atmPosition2 = atm2.posn()
            
            glpane = self.assy.o
            quat = glpane.quat
            vec = atmPosition2 - atmPosition1
            vec = quat.rot(vec)
            if vec[0] < 0.0:
                atm1, atm2 = atm2, atm1
            elif vec[0] == 0.0 and vec[1] < 0.0:
                atm1, atm2 = atm2, atm1
                                            
        return atm1, atm2
    
        
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
        
    def getAxisVector(self, atomAtVectorOrigin = None):
        """
        Returns the unit axis vector of the segment (vector between two axis 
        end points)
        """
        endPoint1, endPoint2 = self.getAxisEndPoints()
        
        if endPoint1 is None or endPoint2 is None:
            return V(0, 0, 0)
        
        
        if atomAtVectorOrigin is not None:
            #If atomAtVectorOrigin is specified, we will return a vector that
            #starts at this atom and ends at endPoint1 or endPoint2 . 
            #Which endPoint to choose will be dicided by the distance between
            #atomAtVectorOrigin and the respective endPoints. (will choose the 
            #frthest endPoint
            origin = atomAtVectorOrigin.posn()
            if vlen(endPoint2 - origin ) > vlen(endPoint1 - origin):
                return norm(endPoint2 - endPoint1)
            else:
                return norm(endPoint1 - endPoint2)
       
        
        return norm(endPoint2 - endPoint1)
        
    
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
        props = (self.getBasesPerTurn(), 
                 self.getDuplexRise() )
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
            
            
    def setColor(self, color):
        """
        Public method provided for convenience. Delegates the color 
        assignment task to self.setStrandColor()
        @see: DnaOrCntPropertyManager._changeStructureColor()
        """
        self.setSegmentColor(color)

    def setSegmentColor(self, color):
        """
        Set the color of the all the axis chunks within this DNA segment group
        to  the given color 
        @see: self.setColor()
        """
        m = None
        for m in self.members:
            if isinstance(m, DnaAxisChunk):
                m.setcolor(color)
                
    def getColor(self):
        """
        Returns the color of an arbitrary internal axis chunk. It iterates 
        over the axisChunk list until it gets a valid color. If no color
        is assigned to any of its axis chunks, it simply returns None. 
        """
        
        color = None
        for m in self.members:
            if isinstance(m, DnaAxisChunk):
                color = m.color
                if color is not None:
                    break

        return color
                
     
    def writemmp_other_info_opengroup(self, mapping): 
        """
        """
        #This method is copied over from NanotubeSegment class . 
        #Retaining comments by Bruce in that method. Method added to write
        #bases per turn and related info to the mmp file. -- Ninad 2008-06-26
        
        
        #bruce 080507 refactoring (split this out of Group.writemmp)
        # (I think the following condition is always true, but I didn't
        #  prove this just now, so I left in the test for now.)
        encoded_classifications = self._encoded_classifications()
        
        if encoded_classifications == "DnaSegment":
            
            # Write the parameters into an info record so we can read and 
            #restore them in the next session. 
            mapping.write("info opengroup dnaSegment-parameters = %0.3f, %0.3f \n" % (self.getBasesPerTurn(),
                            self.getDuplexRise()))
            pass
        return

    def readmmp_info_opengroup_setitem( self, key, val, interp ):
        """
        [extends superclass method]
        """
        #bruce 080507 refactoring (split this out of the superclass method)
        if key == ['dnaSegment-parameters']:
            # val includes all the parameters, separated by commas.
            basesPerTurn, duplexRise = val.split(",")
            self.setBasesPerTurn(float(basesPerTurn))
            self.setDuplexRise(float(duplexRise))
            
        else:
            _superclass.readmmp_info_opengroup_setitem( self, key, val, interp)
        return
    
                   
    
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
        del display_prefs # unused
        
        if self.all_content_is_hidden():    
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)        
                
# end
