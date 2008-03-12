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
from icon_utilities import imagename_to_pixmap

from debug import print_compact_stack
from dna.model.Dna_Constants import getComplementSequence

from bond_chains import grow_directional_bond_chain

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
    
    iconPath = "modeltree/Strand.png"
    hide_iconPath = "modeltree/Strand-hide.png"
    
    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)
    
    def edit(self):
        """
        Edit this DnaSegment. 
        @see: DnaSegment_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        if commandSequencer.currentCommand.commandName != "DNA_STRAND":
            commandSequencer.userEnterTemporaryCommand('DNA_STRAND')
            
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
        
                    
    def getStrandChunks(self): 
        pass
        
    def draw_highlighted(self, glpane, color):
        """
        Draw the strand and axis chunks as highlighted. (Calls the related 
        methods in the chunk class)
        @param: GLPane object 
        @param color: The highlight color
        @see: Chunk.draw_highlighted()
        @see: SelectChunks_GraphicsMode.draw_highlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()
        @see: SelectChunks_GraphicsMode._is_dnaGroup_highlighting_enabled()        
        """  
        #Does DnaStrand group has any member other than DnastrandChunks?
        for c in self.members: 
            if isinstance(c, DnaStrandChunk):
                c.draw_highlighted(glpane, color)            
    
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
        
        sequenceString = ''     
        rawAtomList = []
        for c in self.members:
            if isinstance(c, DnaStrandChunk):
                rawAtomList.extend(c.atoms.itervalues())
        
        #see a to do comment about rawAtom list above
        
        sequenceString = ''  
        for atm in self.get_strand_atoms_in_bond_direction(rawAtomList):
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
        
        
    
    def setStrandSequence(self, sequenceString):
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
        
        rawAtomList = []
        for c in self.members:
            if isinstance(c, DnaStrandChunk):
                rawAtomList.extend(c.atoms.itervalues())
                
       
        #May be we set this beginning with an atom marked by the 
        #Dna Atom Marker in dna data model? -- Ninad 2008-01-11
        # [yes, see my longer reply comment above -- Bruce 080117]
        atomList = []           
        for atm in self.get_strand_atoms_in_bond_direction(rawAtomList):
            if not atm.is_singlet():
                atomList.append(atm)
        
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
            strandAtomMate = atm.get_strand_atom_mate()
            complementBaseName= getComplementSequence(str(baseName))
            if strandAtomMate is not None:
                strandAtomMate.setDnaBaseName(str(complementBaseName)) 
    
    def get_strand_atoms_in_bond_direction(self, inputAtomList): 
        """
        Return a list of atoms in a fixed direction -- from 5' to 3'
        
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

        @note: this would return all atoms from an entire strand (chain or ring)
               even if it spanned multiple chunks.
        @TODO:  THIS method is copied over from chunk class. with a minor modification
        To be revised. See self.getStrandSequence() for a comment. 
        """ 
        startAtom = None
        atomList = []
        
        #Choose startAtom randomly (make sure that it's a PAM3 Sugar atom 
        # and not a bondpoint)
        for atm in inputAtomList:
            if atm.element.symbol == 'Ss3':
                startAtom = atm
                break        
        
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
        return atomList   

    pass

# end
