# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrand.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:
- See comments in self.getStrandSequence(), self.get_strand_atoms_in_bond_direction()
"""

import re

from dna.model.DnaStrandOrSegment import DnaStrandOrSegment
from dna.model.DnaLadderRailChunk import DnaStrandChunk
from utilities.icon_utilities import imagename_to_pixmap

from utilities.debug import print_compact_stack, print_compact_traceback
from dna.model.Dna_Constants import getComplementSequence

from operations.bond_chains import grow_directional_bond_chain
from dna.model.Dna_Constants import MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL
from utilities.constants import MODEL_PAM3
from utilities.constants import MODEL_PAM5


class DnaStrand(DnaStrandOrSegment):
    """
    Model object which represents a Dna Strand inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring. These include
    its DnaStrandChunks, and its DnaStrandMarkers, exactly one of which is
    its controlling marker.

    [Note: we might decide to put the DnaStrandChunks inside the
     DnaSegment whose axis they attach to (as is done in DnaDuplex_EditCommand
     as of 080111), instead. This is purely an implementation issue but
     has implications for selection and copying code. bruce comment 080111]
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaStrand',)    

    iconPath = "ui/modeltree/Strand.png"
    hide_iconPath = "ui/modeltree/Strand-hide.png"

    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)

    #Define highlighting policy for this object (whether it should responf to 
    #highlighting). It returns True by default. For some commands it might 
    #be switched off (usually by the user but can be done internally as well)
    #see self.getHighlightPolicy() for details
    _highlightPolicy = True

    def edit(self):
        """
        Edit this DnaStrand. 
        @see: DnaStrand_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('DNA_STRAND')
        assert commandSequencer.currentCommand.commandName == 'DNA_STRAND'
        commandSequencer.currentCommand.editStructure(self)

    def node_icon(self, display_prefs):
        """
        Model Tree node icon for the dna group node
        @see: Group.all_content_is_hidden() 
        """
        del display_prefs # unused

        if self.all_content_is_hidden():    
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)  
        
    def getColor(self):
        """
        Returns the color of an arbitrary internal strand chunk. It iterates 
        over the strand chunk list until it gets a valid color. If no color
        is assigned to any of its strand chunks, it simply returns None. 
        """
        
        color = None
        for m in self.members:
            if isinstance(m, DnaStrandChunk):
                color = m.color
                if color is not None:
                    break

        return color
        
    def setColor(self, color):
        """
        Public method provided for convenience. Delegates the color 
        assignment task to self.setStrandColor()
        @see: DnaOrCntPropertyManager._changeStructureColor()
        """
        self.setStrandColor(color)

    def setStrandColor(self, color):
        """
        Set the color of the all the strand chunks within this strand group to 
        the given color 
        @param color: The new color of the strand chunks
        @see: BuildAtoms_GraphicsMode._singletLeftUp_joinstrands()
        @see: BuildAtoms_GraphicsMode._singletLeftUp()
        @see: self.setColor()
        """
        m = None
        for m in self.members:
            if isinstance(m, DnaStrandChunk):
                m.setcolor(color)


    def isEmpty(self):
        """
        Returns True if there are no strand chunks as its members 
        @see: DnaGroup.getStrands where this test is used. 
        """
        if len(self.getStrandChunks()) == 0:
            return True

    def get_strand_end_base_atoms(self):
        """
        Returns a tuple containing the end base atoms of a strand in the 
        following order : (5' end base atom, 3' end base atom). If any or both
        of these doesn't exist it returns 'None' in place of that non existent
        atom
        """
        member = None
        for member in self.members:
            if isinstance(member, DnaStrandChunk):
                break
        if not isinstance(member, DnaStrandChunk):
            # no DnaStrandChunk members (should not happen)
            return (None, None)

        end_baseatoms = member.wholechain.end_baseatoms()

        if not end_baseatoms:
            # ring
            return (None, None)

        three_prime_end_base_atom = None
        five_prime_end_base_atom = None
        for atm in end_baseatoms:
            if atm is not None:
                rail = atm.molecule.get_ladder_rail()
                bond_direction = 1 
                    # absoulute bond direction here (1 == 5'->3') 
                    # instead of rail.bond_direction(), piotr 0803278 
                next_strand_atom = atm.strand_next_baseatom(bond_direction)
                previous_strand_atom = atm.strand_next_baseatom(-bond_direction)

                if next_strand_atom is None and previous_strand_atom:
                    three_prime_end_base_atom = atm         
                if previous_strand_atom is None and next_strand_atom:
                    five_prime_end_base_atom = atm

                if next_strand_atom is None and previous_strand_atom is None:
                    #We have a case where the current strand atom has no
                    #strand atoms bonded. So simply return it twice.
                    five_prime_end_base_atom = atm
                    three_prime_end_base_atom = atm 

        # chain
        return (five_prime_end_base_atom, three_prime_end_base_atom)

    def get_three_prime_end_base_atom(self):
        """
        Returns the three prime end base atom of this strand. If one doesn't
        exist, returns None 
        @see: self.get_strand_end_base_atoms()
        """
        endbaseAtoms = self.get_strand_end_base_atoms()        
        return endbaseAtoms[1]  

    def get_five_prime_end_base_atom(self):
        """
        Returns the five prime end base atom of this strand. If one doesn't
        exist, returns None 
        @see: self.get_strand_end_base_atoms()
        """
        endbaseAtoms = self.get_strand_end_base_atoms()        
        return endbaseAtoms[0] 


    def get_DnaSegment_with_content_atom(self, strand_atom):
        """
        Returns a DnaSegment which is has the given strand atom as its 
        'logical content' .
        """
        segment = None
        if strand_atom:
            axis_atom = strand_atom.axis_neighbor()
            if axis_atom:
                segment = axis_atom.molecule.parent_node_of_class(
                    self.assy.DnaSegment)
        return segment

    def get_DnaSegment_axisEndAtom_connected_to(self, strand_atom):
        """
        Returns end axis atom of a DnaSegment connected to the given 
        strand base atom. Returns None if the axis atom is not an 'end' atom
        of a wholechain         
        """
        axisEndAtom = None
        #Safety check. strand_atom could be None
        if strand_atom:
            axis_atom = strand_atom.axis_neighbor()
            axis_rail = axis_atom.molecule.get_ladder_rail()
            if axis_atom in axis_rail.wholechain_end_baseatoms():
                axisEndAtom = axis_atom

        #Alternative implementation
        ##dnaSegment = self.get_DnaSegment_with_content_atom(strand_atom)
        ##axisEndAtom1, axisEndAtom2 = dnaSegment.getAxisEndAtoms()

        return axisEndAtom

    def get_all_content_chunks(self):
        """
        Return all the chunks including 
        A) the chunks within the DnaSegments that this DnaStrand 'touches' 
        (passes through).
        B) Its own member chunks (DnaStrandChunks)

        @see: SelectChunks_GraphicsMode.getMovablesForLeftDragging() where this 
              is used
        """
        #ONLY WORKS in DNA DATA model. pre dna data model is unsupported
        all_content_chunk_list = []

        for member in self.members:
            if isinstance(member, DnaStrandChunk):
                ladder = member.ladder
                all_content_chunk_list.extend(ladder.all_chunks())

        return all_content_chunk_list

    def getDnaSegment_at_three_prime_end(self): 
        """
        Returns DnaSegment at the three prime end. i.e. the stand end base atom
        (at the three prime end) is a 'logical content' of the DnaSegment
        logical content means that the atom.molecule is not a direct member
        of DnaSegment group, but is connected to an axis atom whose chunk
        is a member of that DnaSegment. 
        """
        dnaSegment = None
        atom = self.get_three_prime_end_base_atom()
        if atom:
            dnaSegment = self.get_DnaSegment_with_content_atom(atom)

        return dnaSegment

    def getDnaSegment_at_five_prime_end(self):
        """
        Returns DnaSegment at the five prime end. i.e. the stand end base atom
        (at the three prime end) is a 'logical content' of the DnaSegment
        """
        dnaSegment = None
        atom = self.get_five_prime_end_base_atom()
        if atom:
            dnaSegment = self.get_DnaSegment_with_content_atom(atom)

        return dnaSegment

    def getStrandEndAtomAtPosition(self, position):
        """
        Returns an end baseatom of this strand at the specified position. 
        Returns None if no atom center is found at <position>
        @param position: The point at which the caller needs to find the 
                         strand end baseatom. 
        @type position: B{A}
        """
        strandEndAtom = None
        endAtom1, endAtom2 = self.get_strand_end_base_atoms()    
        for atm in (endAtom1, endAtom2):
            if atm is not None and same_vals(position,  atm.posn()):
                strandEndAtom = atm
                break
        return strandEndAtom

    def getNumberOfBases(self):
        """
        @return: The total number of baseatoms of this DnaStrand
        @rtype:  int
        """
        numberOfBases = 0

        strand_wholechain = self.get_strand_wholechain()
        if strand_wholechain:
            numberOfBases = len(strand_wholechain.get_all_baseatoms())

        return numberOfBases

    def get_DnaStrandChunks_sharing_basepairs(self):
        """
        Returns a list of strand chunk that have atleast one complementary 
        strand baseatom with self. 
        @see: ops_select_Mixin.expandDnaComponentSelection()
        @see: ops_select_Mixin._expandDnaStrandSelection()
        @see:ops_select_Mixin._contractDnaStrandSelection()
        @see: ops_select_Mixin._contractDnaSegmentSelection()
        @see: SelectChunks_GraphicsMode.chunkLeftDouble()
        """
        #REVIEW-- method needs optimization -- Ninad 2008-04-12
        complementary_strand_chunks = []
        
        for c in self.getStrandChunks():
            ladder = c.ladder
            for strandChunk in ladder.strand_chunks():
                if not strandChunk is c:
                    if strandChunk not in complementary_strand_chunks:
                        complementary_strand_chunks.append(strandChunk)
                                
        return complementary_strand_chunks
    
    def is_PAM3_DnaStrand(self):
        """
        Returns true if all the baseatoms in the DnaLadders of this strand
        are PAM3 baseatoms (axis or strands) Otherwise returns False
        @see: DnaStrand_EditCommand.model_changed()
        @see: DnaStrand_EditCommand.hasResizableStructure()
        @see: DnaSegment.is_PAM3_DnaSegment() (similar implementation)
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
            if isinstance(member, DnaStrandChunk):
                ladder = member.ladder
                if ladder not in ladderList:
                    ladderList.append(ladder)
        
        return ladderList
    
    def get_wholechain(self):
        """
        Return the 'wholechain' of this DnaStrand. Method provided for 
        convenience.
        Delegates this to self.get_strand_wholechain()
        """
        return self.get_strand_wholechain()
    
    def get_strand_wholechain(self):
        """
        @return: the 'wholechain' of this DnaStrand
                 (same as wholechain of each of its DnaStrandChunks),
                 or None if it doesn't have one
                 (i.e. if it's empty -- should never happen
                 if called on a live DnaStrand not modified since
                 the last dna updater run).

        @note: the return value contains the same chunks which
               get selected when the user clicks on a strand group
               in the model tree.

        @see: Wholechain
        @see: get_segment_wholechain
        """
        for member in self.members:
            if isinstance(member, DnaStrandChunk):
                return member.wholechain
        return None

    def getStrandChunks(self): 
        """
        Return a list of all strand chunks
        """
        strandChunkList = []
        for m in self.members:
            if isinstance(m, self.assy.Chunk) and m.isStrandChunk():
                strandChunkList.append(m)
        return strandChunkList

    def _get_commandNames_honoring_highlightPolicy(self):
        """
        Return a tuple containing the command names that honor the 
        self._highlightPolicy of this object.
        @see: self.getHighlightPolicy()
        """
        commandNames_that_honor_highlightPolicy = ('BUILD_DNA', 
                                                   'DNA_STRAND', 
                                                   'DNA_SEGMENT')
        return commandNames_that_honor_highlightPolicy 

    def setHighlightPolicy(self, highlight = True):
        """
        Set the highlighting flag that decides whether to highlight 'self' when 
        self is the object under cursor. This is set as a property of self 
        that helps enabling or disabling highlighting while in a particular 
        command. Note that NE1 honors this property of the object overriding the 
        'hover_highligiting_enabled' flag of the current command/ Graphics mode

        Example: While in BuildDna_EditCommand and some of its its subcommands, 
                 the user may wish to switch off highlighting for a particular
                 DNA strand as it gets in the way. (example the huge scaffold 
                 strand). The user may do so my going into the strand edit 
                 command and checking the option 'Don't highlight while in Dna.'
                 This tells the structure not to get highlighted while in 
                 BuildDna mode and some of its subcommands (the structure can 
                 decide for which commands it should switch its highlighting 
                 off. Note that the other strands will still respond to the
                 hover highlighting. In all other commands, this object 
                 (dnaStrand) will still respond to highlighting. 
        @see: self.getHighlightPolicy()
        @see: self._get_commandNames_honoring_highlightPolicy()
        @see: DnaStrand_PropertyManager.change_struct_highlightPolicy()
        """
        #@NOTE: This property is a temporary implementation for to be used by
        #Mark and Tom for the DNA Four hole tile project (the highlighting
        #for scaffold gets in their way as it takes long time.. so they need 
        #to switch it off for the bug scaffold strand) If we think its a good 
        #feature overall, then it can become an API method. More thought needs
        #to be put on whether its structure that checks the current command 
        #to decide whether it needs to be highlighted (like the check done in
        #self.draw_highlighted() or its the command that sets the flag for 
        #each and every structure. The former approach is followed right now
        #(see self.getHighlightPolicy for details) and it looks like a better
        #approach
        #Also note that this state is not saved to the mmp file. (we can do that
        #if we decide to make it a general API method) -- Ninad 2008-03-14
        self._highlightPolicy = highlight            

    def getHighlightPolicy(self):
        """
        Returns the highlighting state of the object. Note that it doesn't 
        always mean that the object won't get highlighted if this returns False
        In fact, this state will be used only in certain commands. 
        @see self.setHighlightPolicy
        """
        commandSequencer = self.assy.w.commandSequencer
        currentCommandName = commandSequencer.currentCommand.commandName        
        if currentCommandName in self._get_commandNames_honoring_highlightPolicy():            
            highlighting_wanted = self._highlightPolicy
        else:
            highlighting_wanted = True

        return highlighting_wanted


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
        highlighting_wanted = self.getHighlightPolicy()

        if highlighting_wanted:
            #Does DnaStrand group has any member other than DnastrandChunks?
            for c in self.members: 
                if isinstance(c, DnaStrandChunk):
                    c.draw_highlighted(glpane, color)            

    def getStrandSequenceAndItsComplement(self):
        """
        Returns the strand sequence  and the sequence of the complementary 
        strands of the for the DnaStrandChunks within this
        DnaStrand group. If the complementary strand base atom is not found 
        (e.g. a single stranded DNA), it returns the corresponding sequence
        character (for the complementary sequence) as '*' meaning its 
        missing.

        @return: strand Sequence string
        @rtype: str

        @TODO: REFACTOR this. See how to split out common part of 
        this method and self.getStrandSequence() Basically we could have simply
        replaced self.getStrandSequence with this method , but keeping
        self.getStrandSequence has an advantage that we don't compute the 
        complement sequence (not sure if that would improve performance but,
        in theory, that will improve it.) One possibility is to pass an argument 
        compute_complement_sequence = True' to this method. 
        """
        # TODO: Is there a way to make use of DnaStrandMarkers to get the strand
        #       atoms in bond direction for this DnaStrandGroup??
        #       [A: they are not needed for that, but they could be used
        #        to define an unambiguous sequence origin for a ring.]
        #       
        #       OR: does self.members alway return DnaStrandChunks in the 
        #       direction of bond direction? [A. no.]
        #       
        #       While the above questions remain unanswered, the following 
        #       makes use of a method self.get_strand_atoms_in_bond_direction 
        #       This method is mostly copied here from chunk class with some 
        #       modifications ... i.e. it accepts an atomList and uses a random 
        #       start atom within that list to find out the connected atoms 
        #       in the bond direction. Actually, sending the list 
        #       with *all atoms* of the strand isn't really necessary. All we are 
        #       interested in is a start Ss atom and bond direction which can 
        #       ideally be obtained by using even a single DnaStrandChunk within 
        #       this DnaStrand Group. For a short time, we will pass the whole 
        #       atom list. Will definitely be revised and refactored within the
        #       coming days (need to discuss with Bruce) -- Ninad 2008-03-01

        
        

        #see a to do comment about rawAtom list above

        sequenceString = ''  
        complementSequenceString = ''
        
        atomList = self.get_strand_atoms_in_bond_direction()
        for atm in atomList:

            baseName = str(atm.getDnaBaseName())
            complementBaseAtom = atm.get_strand_atom_mate()

            if baseName:
                sequenceString = sequenceString + baseName
            else:
                #What if baseName is not assigned due to some error?? Example
                #while reading in an mmp file. 
                #As a fallback, we should assign unassigned base letter 'X'
                #to all the base atoms that don't have a baseletter defined
                #also, make sure that the atom is not a bondpoint. 
                if atm.element.symbol != 'X':                    
                    baseName = 'X'
                    sequenceString = sequenceString + baseName

            complementBaseName = ''
            if complementBaseAtom:
                complementBaseName = getComplementSequence(baseName)

            else:
                #This means the complementary strand base atom is not present.
                #(its a single stranded dna) .So just indicate the complementary
                #sequence as '*' which means its missing.
                if atm.element.symbol != 'X':
                    complementBaseName = MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL                
            if complementBaseName:            
                complementSequenceString = complementSequenceString + \
                                         complementBaseName 

        return (sequenceString, complementSequenceString)

    def getStrandSequence(self):
        """
        Returns the strand sequence for the DnaStrandChunks within this
        DnaStrand group.

        @return: strand Sequence string
        @rtype: str
        """
        # TODO: Is there a way to make use of DnaStrandMarkers to get the strand
        #       atoms in bond direction for this DnaStrandGroup??
        #       [A: they are not needed for that, but they could be used
        #        to define an unambiguous sequence origin for a ring.]
        #       
        #       OR: does self.members alway return DnaStrandChunks in the 
        #       direction of bond direction? [A. no.]
        #       
        #       While the above questions remain unanswered, the following 
        #       makes use of a method self.get_strand_atoms_in_bond_direction 
        #       This method is mostly copied here from chunk class with some 
        #       modifications ... i.e. it accepts an atomList and uses a random 
        #       start atom within that list to find out the connected atoms 
        #       in the bond direction. Actually, sending the list 
        #       with *all atoms* of the strand isn't really necessary. All we are 
        #       interested in is a start Ss atom and bond direction which can 
        #       ideally be obtained by using even a single DnaStrandChunk within 
        #       this DnaStrand Group. For a short time, we will pass the whole 
        #       atom list. Will definitely be revised and refactored within the
        #       coming days (need to discuss with Bruce) -- Ninad 2008-03-01

        
        #see a to do comment about rawAtom list above

        sequenceString = ''  
        atomList = self.get_strand_atoms_in_bond_direction()
        for atm in atomList:
            baseName = str(atm.getDnaBaseName())
            if baseName:
                sequenceString = sequenceString + baseName
            else:
                #What if baseName is not assigned due to some error?? Example
                #while reading in an mmp file. 
                #As a fallback, we should assign unassigned base letter 'X'
                #to all the base atoms that don't have a baseletter defined
                #also, make sure that the atom is not a bondpoint. 
                if atm.element.symbol != 'X':                    
                    baseName = 'X'
                    sequenceString = sequenceString + baseName
        
        return sequenceString

    def setStrandSequence(self, sequenceString, complement = True):
        """
        Set the strand sequence i.e.assign the baseNames for the PAM atoms in 
        this strand AND the complementary baseNames to the PAM atoms of the 
        complementary strand ('mate strand')
        @param sequenceString: The sequence to be assigned to this strand chunk
        @type sequenceString: str
        """      
        #TO BE REVISED SEE A TODO COMMENT AT THE TOP
        
        sequenceString = str(sequenceString)
        #Remove whitespaces and tabs from the sequence string
        sequenceString = re.sub(r'\s', '', sequenceString)

        #May be we set this beginning with an atom marked by the 
        #Dna Atom Marker in dna data model? -- Ninad 2008-01-11
        # [yes, see my longer reply comment above -- Bruce 080117]
        atomList = []     
        rawAtomList = self.get_strand_atoms_in_bond_direction()
        
        atomList = filter(lambda atm: not atm.is_singlet(), rawAtomList)
        
        for atm in atomList:   
            atomIndex = atomList.index(atm)
            if atomIndex > (len(sequenceString) - 1):
                #In this case, set an unassigned base ('X') for the remaining 
                #atoms
                baseName = 'X'
            else:
                baseName = sequenceString[atomIndex]

            atm.setDnaBaseName(baseName)

            #Also assign the baseNames for the PAM atoms on the complementary 
            #('mate') strand.
            if complement:
                
                strandAtomMate = atm.get_strand_atom_mate()
                complementBaseName= getComplementSequence(str(baseName))
                if strandAtomMate is not None:
                    strandAtomMate.setDnaBaseName(str(complementBaseName)) 

        # piotr 080319:
        # Redraw the chunks in DNA display style
        # to reflect the sequence changes.
        from utilities.constants import diDNACYLINDER
        for c in self.members: 
            if isinstance(c, DnaStrandChunk):
                if c.get_dispdef() == diDNACYLINDER:
                    c.inval_display_list() # redraw the chunk
                    # do the same for all complementary chunks
                    prev_cc = None
                    for atom in c.atoms.itervalues():
                        atm_mate = atom.get_strand_atom_mate()
                        if atm_mate:
                            cc = atm_mate.molecule
                            if cc!=prev_cc and isinstance(cc, DnaStrandChunk):
                                prev_cc = cc
                                if cc.get_dispdef() == diDNACYLINDER:
                                    cc.inval_display_list()

    def get_strand_atoms_in_bond_direction(self, 
                                           inputAtomList = (), 
                                           filterBondPoints = False): 
        """
        Return a list of atoms in a fixed direction -- from 5' to 3'
        
        @param inputAtomList: An optional argument. If its not provided, this
               method will return a list of all atoms within the strand, 
               in the strand's bond direction. Otherwise, it will just return 
               the list <inputAtomList> whose atoms are ordered in the strand's
               bond direction. 
        @type inputAtomList: list  (with default value as an empty tuple)

        @note: this is a stub and we can modify it so that
        it can accept other direction i.e. 3' to 5' , as an argument.

        BUG: ? : This also includes the bondpoints (X)  .. I think this is 
        from the atomlist returned by bond_chains.grow_directional_bond_chain.
        The caller -- self.getStrandSequence uses atom.getDnaBaseName to
        retrieve the DnaBase name info out of atom. So this bug introduces 
        no harm (as dnaBaseNames are not assigned for bondpoints).

        [I think at most one atom at each end can be a bondpoint,
         so we could revise this code to remove them before returning.
         bruce 080205]

        @warning: for a ring, this uses an arbitrary start atom in self
                  (so it is not yet useful in that case). ### VERIFY

        @warning: this only works for PAM3 chunks (not PAM5).
                  [piotr 080411 modified it to work with PAM5, but only 
                   sugar atoms and bondpoints will be returned]

        @note: 
        @note: this would return all atoms from an entire strand (chain or ring)
               even if it spanned multiple chunks.
        @TODO:  THIS method is copied over from chunk class. with a minor modification
        To be revised. See self.getStrandSequence() for a comment. 
        """         
        rawAtomList = []
        if inputAtomList:
            rawAtomList = inputAtomList
        else:
            for c in self.members:
                if isinstance(c, DnaStrandChunk):
                    rawAtomList.extend(c.atoms.itervalues())
                
                
        startAtom = None
        atomList = []

        #Choose startAtom randomly (make sure that it's a PAM3 Sugar atom 
        # and not a bondpoint)
        for atm in rawAtomList:
            if atm.element.symbol == 'Ss3':
                startAtom = atm
                break        
            elif atm.element.pam == MODEL_PAM5: 
                # piotr 080411
                # If inputAtomList contains PAM5 atoms, process it independently.
                atomList = self._get_pam5_strand_atoms_in_bond_direction( 
                    inputAtomList = rawAtomList)
                return atomList
            
        if startAtom is None:
            print_compact_stack("bug: no PAM3 Sugar atom (Ss3) found: " )
            return []

        #Build one list in each direction, detecting a ring too 

        #ringQ decides whether the first returned list forms a ring. 
        #This needs a better name in bond_chains.grow_directional_bond_chain
        ringQ = False        
        atomList_direction_1 = []
        atomList_direction_2 = []     

        b = None  
        bond_direction = 0
        for bnd in startAtom.directional_bonds():
            if not bnd.is_open_bond(): # (this assumes strand length > 1)
                #Determine the bond_direction from the 'startAtom'
                direction = bnd.bond_direction_from(startAtom)
                if direction in (1, -1):                    
                    b = bnd
                    bond_direction = direction
                    break

        if b is None or bond_direction == 0:
            return []         

        #Find out the list of new atoms and bonds in the direction 
        #from bond b towards 'startAtom' . This can either be 3' to 5' direction 
        #(i.e. bond_direction = -1 OR the reverse direction 
        # Later, we will check  the bond direction and do appropriate things. 
        #(things that will decide which list (atomList_direction_1 or 
        #atomList_direction_2) should  be prepended in atomList so that it has 
        #atoms ordered from 5' to 3' end. 

        # 'atomList_direction_1' does NOT include 'startAtom'.
        # See a detailed explanation below on how atomList_direction_a will be 
        # used, based on bond_direction
        ringQ, listb, atomList_direction_1 = grow_directional_bond_chain(b, startAtom)

        del listb # don't need list of bonds

        if ringQ:
            # The 'ringQ' returns True So its it's a 'ring'.
            #First add 'startAtom' (as its not included in atomList_direction_1)
            atomList.append(startAtom)
            #extend atomList with remaining atoms
            atomList.extend(atomList_direction_1)            
        else:       
            #Its not a ring. Now we need to make sure to include atoms in the 
            #direction_2 (if any) from the 'startAtom' . i.e. we need to grow 
            #the directional bond chain in the opposite direction. 

            other_atom = b.other(startAtom)
            if not other_atom.is_singlet():  
                ringQ, listb, atomList_direction_2 = grow_directional_bond_chain(b, other_atom)
                assert not ringQ #bruce 080205
                del listb
                #See a detailed explanation below on how 
                #atomList_direction_2 will be used based on 'bond_direction'
                atomList_direction_2.insert(0, other_atom)

            atomList = [] # not needed but just to be on a safer side.

            if bond_direction == 1:
                # 'bond_direction' is the direction *away from* startAtom and 
                # along the bond 'b' declared above. . 

                # This can be represented by the following sketch --
                # (3'end) <--1 <-- 2 <-- 3 <-- 4 <-- (5' end)

                # Let startAtom be '2' and bond 'b' be directional bond between 
                # 1 and 2. In this case, the direction of bond *away* from 
                # '2' and along 2  = bond direction of bond 'b' and thus 
                # atoms traversed along bond_direction = 1 lead us to 3' end. 

                # Now, 'atomList_direction_1'  is computed by 'growing' (expanding)
                # a bond chain  in the direction that goes from bond b 
                # *towards* startAtom. That is, in this case it is the opposite 
                # direction of one specified by 'bond_direction'.  The last atom
                # in atomList_direction_1 is the (5' end) atom.
                # Note that atomList_direction_1 doesn't include 'startAtom'
                # Therefore, to get atomList ordered from 5'to 3' end we must
                #reverse atomList_direction_1 , then append startAtom to the 
                #atomList (as its not included in atomList_direction_1) and then 
                #extend atoms from atomList_direction_2. 

                #What is atomList_direction_2 ?  It is the list of atoms 
                #obtained by growing bond chain from bond b, in the direction of 
                #atom 1 (atom 1 is the 'other atom' of the bond) . In this case 
                #these are the atoms in the direction same as 'bond_direction'
                #starting from atom 1. Thus the atoms in the list are already 
                #arranged from 5' to 3' end. (also note that after computing 
                #the atomList_direction_2, we also prepend 'atom 1' as the 
                #first atom in that list. See the code above that does that.                 
                atomList_direction_1.reverse()                
                atomList.extend(atomList_direction_1)
                atomList.append(startAtom)
                atomList.extend(atomList_direction_2)                

            else:     
                #See a detailed explanation above. 
                #Here, bond_direction == -1. 

                # This can be represented by the following sketch --
                # (5'end) --> 1 --> 2 --> 3 --> 4 --> (3' end)

                #bond b is the bond betweern atoms 1 and 2. 
                #startAtom remains the same ..i.e. atom 2. 

                #As you can notice from the sketch, the bond_direction is 
                #direction *away* from 2, along bond b and it leads us to 
                # 5' end. 

                #based on how atomList_direction_2 (explained earlier), it now 
                #includes atoms begining at 1 and ending at 5' end. So 
                #we must reverse atomList_direction_2 now to arrange them 
                #from 5' to 3' end. 
                atomList_direction_2.reverse()
                atomList.extend(atomList_direction_2)
                atomList.append(startAtom)
                atomList.extend(atomList_direction_1)

        #TODO: could zap first and/or last element if they are bondpoints 
        #[bruce 080205 comment]  
       
        
        if filterBondPoints:            
            atomList = filter(lambda atm: not atm.is_singlet(), atomList)
                        
        return atomList   


    def _get_pam5_strand_atoms_in_bond_direction(self, inputAtomList = ()): 
        """
        Return a list of sugar atoms in a fixed direction -- from 5' to 3'
        
        @param inputAtomList: An optional argument. If its not provided, this
               method will return a list of all atoms within the strand, 
               in the strand's bond direction. Otherwise, it will just return 
               the list <inputAtomList> whose atoms are ordered in the strand's
               bond direction. 
        @type inputAtomList: list  (with default value as an empty tuple)

        @note: this is a stub and we can modify it so that
        it can accept other direction i.e. 3' to 5' , as an argument.

        [I think at most one atom at each end can be a bondpoint,
         so we could revise this code to remove them before returning.
         bruce 080205]

        piotr 080411: This is a helper method for  
        'get_strand_atoms_in_bond_direction'. It is called for PAM5
        models and should be replaced by a properly modified caller method.
        Only bondpoints ('X') and sugar atoms ('Ss3', Ss5') are preserved.

        @warning: for a ring, this uses an arbitrary start atom in self
                  (so it is not yet useful in that case). ### VERIFY

        @note: this would return all atoms from an entire strand (chain or ring)
               even if it spanned multiple chunks.

        @TODO:  THIS method is copied over from chunk class. with a minor modification
        To be revised. See self.getStrandSequence() for a comment. 
        """ 
        startAtom = None
        atomList = []
        
        rawAtomList = []
        if inputAtomList:
            rawAtomList = inputAtomList
        else:
            for c in self.members:
                if isinstance(c, DnaStrandChunk):
                    rawAtomList.extend(c.atoms.itervalues())
                    

        #Choose startAtom randomly (make sure that it's a Sugar atom 
        # and not a bondpoint)
        for atm in rawAtomList:
            if atm.element.symbol == 'Ss3' or \
               atm.element.symbol == 'Ss5':
                startAtom = atm
                break        

        if startAtom is None:
            print_compact_stack("bug: no Sugar atom (Ss3 or Ss5) found: " )
            return []

        #Build one list in each direction, detecting a ring too 

        #ringQ decides whether the first returned list forms a ring. 
        #This needs a better name in bond_chains.grow_directional_bond_chain
        ringQ = False        
        atomList_direction_1 = []
        atomList_direction_2 = []     

        b = None  
        bond_direction = 0
        for bnd in startAtom.directional_bonds():
            if not bnd.is_open_bond(): # (this assumes strand length > 1)
                #Determine the bond_direction from the 'startAtom'
                direction = bnd.bond_direction_from(startAtom)
                if direction in (1, -1):                    
                    b = bnd
                    bond_direction = direction
                    break

        if b is None or bond_direction == 0:
            return []         

        #Find out the list of new atoms and bonds in the direction 
        #from bond b towards 'startAtom' . This can either be 3' to 5' direction 
        #(i.e. bond_direction = -1 OR the reverse direction 
        # Later, we will check  the bond direction and do appropriate things. 
        #(things that will decide which list (atomList_direction_1 or 
        #atomList_direction_2) should  be prepended in atomList so that it has 
        #atoms ordered from 5' to 3' end. 

        # 'atomList_direction_1' does NOT include 'startAtom'.
        # See a detailed explanation below on how atomList_direction_a will be 
        # used, based on bond_direction
        ringQ, listb, atomList_direction_1 = grow_directional_bond_chain(b, startAtom)

        del listb # don't need list of bonds

        if ringQ:
            # The 'ringQ' returns True So its it's a 'ring'.
            #First add 'startAtom' (as its not included in atomList_direction_1)
            atomList.append(startAtom)
            #extend atomList with remaining atoms
            atomList.extend(atomList_direction_1)            
        else:       
            #Its not a ring. Now we need to make sure to include atoms in the 
            #direction_2 (if any) from the 'startAtom' . i.e. we need to grow 
            #the directional bond chain in the opposite direction. 

            other_atom = b.other(startAtom)
            if not other_atom.is_singlet():  
                ringQ, listb, atomList_direction_2 = grow_directional_bond_chain(b, other_atom)
                assert not ringQ #bruce 080205
                del listb
                #See a detailed explanation below on how 
                #atomList_direction_2 will be used based on 'bond_direction'
                atomList_direction_2.insert(0, other_atom)

            atomList = [] # not needed but just to be on a safer side.

            if bond_direction == 1:
                # 'bond_direction' is the direction *away from* startAtom and 
                # along the bond 'b' declared above. . 

                # This can be represented by the following sketch --
                # (3'end) <--1 <-- 2 <-- 3 <-- 4 <-- (5' end)

                # Let startAtom be '2' and bond 'b' be directional bond between 
                # 1 and 2. In this case, the direction of bond *away* from 
                # '2' and along 2  = bond direction of bond 'b' and thus 
                # atoms traversed along bond_direction = 1 lead us to 3' end. 

                # Now, 'atomList_direction_1'  is computed by 'growing' (expanding)
                # a bond chain  in the direction that goes from bond b 
                # *towards* startAtom. That is, in this case it is the opposite 
                # direction of one specified by 'bond_direction'.  The last atom
                # in atomList_direction_1 is the (5' end) atom.
                # Note that atomList_direction_1 doesn't include 'startAtom'
                # Therefore, to get atomList ordered from 5'to 3' end we must
                #reverse atomList_direction_1 , then append startAtom to the 
                #atomList (as its not included in atomList_direction_1) and then 
                #extend atoms from atomList_direction_2. 

                #What is atomList_direction_2 ?  It is the list of atoms 
                #obtained by growing bond chain from bond b, in the direction of 
                #atom 1 (atom 1 is the 'other atom' of the bond) . In this case 
                #these are the atoms in the direction same as 'bond_direction'
                #starting from atom 1. Thus the atoms in the list are already 
                #arranged from 5' to 3' end. (also note that after computing 
                #the atomList_direction_2, we also prepend 'atom 1' as the 
                #first atom in that list. See the code above that does that.                 
                atomList_direction_1.reverse()                
                atomList.extend(atomList_direction_1)
                atomList.append(startAtom)
                atomList.extend(atomList_direction_2)                

            else:     
                #See a detailed explanation above. 
                #Here, bond_direction == -1. 

                # This can be represented by the following sketch --
                # (5'end) --> 1 --> 2 --> 3 --> 4 --> (3' end)

                #bond b is the bond betweern atoms 1 and 2. 
                #startAtom remains the same ..i.e. atom 2. 

                #As you can notice from the sketch, the bond_direction is 
                #direction *away* from 2, along bond b and it leads us to 
                # 5' end. 

                #based on how atomList_direction_2 (explained earlier), it now 
                #includes atoms begining at 1 and ending at 5' end. So 
                #we must reverse atomList_direction_2 now to arrange them 
                #from 5' to 3' end. 
                atomList_direction_2.reverse()
                atomList.extend(atomList_direction_2)
                atomList.append(startAtom)
                atomList.extend(atomList_direction_1)

        # Note: the bondpoint atoms are NOT included.
        # ONLY consecutive sugar stoms are returned.
        # piotr 080411

        # extract only sugar atoms or bondpoints
        # the bondpoints are extracted to make the method compatible
        # with get_strand_atoms_in_bond_direction
        def filter_sugars(atm):
            return atm.element.symbol == 'Ss3' or \
                   atm.element.symbol == 'Ss5' or \
                   atm.element.symbol == 'X'

        atomList = filter(filter_sugars, atomList)
        return atomList   

    pass

# end
