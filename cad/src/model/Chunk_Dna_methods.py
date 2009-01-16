# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Chunk_Dna_methods.py -- dna-related methods for class Chunk

@author: Bruce, Ninad
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090115 split this out of class Chunk. (Not long or old enough
for svn copy to be worthwhile, so see chunk.py for older svn history.)
"""

import re

from utilities.constants import noop
from utilities.constants import MODEL_PAM3, MODEL_PAM5

from utilities.debug import print_compact_stack

from dna.model.Dna_Constants import getComplementSequence

from operations.bond_chains import grow_directional_bond_chain


class Chunk_Dna_methods: # REVIEW: inherit NodeWithAtomContent to mollify pylint?
    """
    Dna-related methods to be mixed in to class Chunk.
    """
    # Note: some of the methods in this class are never used except on
    # Dna-related subclasses of Chunk, and should be moved into those
    # subclasses. Unfortunately it's not trivial to figure out for which ones
    # that's guaranteed to be the case.
    
    
    # PAM3+5 attributes (these only affect PAM atoms in self, if any):
    #
    # ### REVIEW [bruce 090115]: can some of these be deprecated and removed?
    #
    # self.display_as_pam can be MODEL_PAM3 or MODEL_PAM5 to force conversion on input
    #   to the specified PAM model for display and editing of self, or can be
    #   "" to use global preference settings. (There is no value which always
    #   causes no conversion, but there may be preference settings which disable
    #   ever doing conversion. But in practice, a PAM chunk will be all PAM3 or
    #   all PAM5, so this can be set to the model the chunk uses to prevent
    #   conversion for that chunk.)
    #
    #  The value MODEL_PAM3 implies preservation of PAM5 data when present
    #  (aka "pam3+5" or "pam3plus5"). The allowed values are "", MODEL_PAM3, MODEL_PAM5.
    #
    # self.save_as_pam can be MODEL_PAM3 or MODEL_PAM5 to force conversion on save
    #   to the specified PAM model. When not set, global settings or save
    #   parameters determine which model to convert to, and whether to ever
    #   convert.
    #
    # [bruce 080321 for PAM3+5] ### TODO: use for conversion, and prevent
    # ladder merge when different

    display_as_pam = "" 
        # PAM model to use for displaying and editing PAM atoms in self (not
        # set means use user pref)

    save_as_pam = "" 
        # PAM model to use for saving self (not normally set; not set means
        # use save-op params)
        
    # this mixin's contribution to Chunk.copyable_attrs
    _dna_copyable_attrs = ('display_as_pam', 'save_as_pam', ) 

    
    def invalidate_ladder(self): #bruce 071203
        """
        Subclasses which have a .ladder attribute
        should call its ladder_invalidate_if_not_disabled method.
        """
        return

    def invalidate_ladder_and_assert_permitted(self): #bruce 080413
        """
        Subclasses which have a .ladder attribute
        should call its ladder_invalidate_and_assert_permitted method.
        """
        return

    def in_a_valid_ladder(self): #bruce 071203
        """
        Is this chunk a rail of a valid DnaLadder?
        [subclasses that might be should override]
        """
        return False

    
    def _make_glpane_cmenu_items_Dna(self, contextMenuList): # by Ninad
        """
        Private helper for Chunk.make_glpane_cmenu_items; 
        does the dna-related part.
        """
        #bruce 090115 split this out of Chunk.make_glpane_cmenu_items
        
        def _addDnaGroupMenuItems(dnaGroup):
            if dnaGroup is None:
                return
            item = (("DnaGroup: [%s]" % dnaGroup.name), noop, 'disabled')
            contextMenuList.append(item)   
            item = (("Edit DnaGroup Properties..."), 
                    dnaGroup.edit) 
            contextMenuList.append(item)
            return
        
        if self.isStrandChunk():
            strandGroup = self.parent_node_of_class(self.assy.DnaStrand)

            if strandGroup is None:
                strand = self
            else:
                #dna_updater case which uses DnaStrand object for 
                #internal DnaStrandChunks
                strand = strandGroup                

            dnaGroup = strand.parent_node_of_class(self.assy.DnaGroup)

            if dnaGroup is None:
                #This is probably a bug. A strand should always be contained
                #within a Dnagroup. But we'll assume here that this is possible. 
                item = (("%s" % strand.name), noop, 'disabled')
            else:
                item = (("%s of [%s]" % (strand.name, dnaGroup.name)),
                        noop,
                        'disabled')	
            contextMenuList.append(None) # adds a separator in the contextmenu
            contextMenuList.append(item)	    
            item = (("Edit DnaStrand Properties..."), 
                    strand.edit) 			  
            contextMenuList.append(item)
            contextMenuList.append(None) # separator
            
            _addDnaGroupMenuItems(dnaGroup)
            
            # add menu commands from our DnaLadder [bruce 080407]
            # REVIEW: should these be added regardless of command? [bruce 090115 question]
            # REVIEW: I think self.ladder is not valid except in dna-specific subclasses of Chunk.
            # Probably that means this code should be moved there. [bruce 090115]
            if self.ladder:
                menu_spec = self.ladder.dnaladder_menu_spec(self)
                    # note: this is empty when self (the arg) is a Chunk.
                    # [bruce 080723 refactoring a recent Mark change]
                if menu_spec:
                    # append separator?? ## contextMenuList.append(None)
                    contextMenuList.extend(menu_spec)

        elif self.isAxisChunk():
            segment = self.parent_node_of_class(self.assy.DnaSegment)
            dnaGroup = segment.parent_node_of_class(self.assy.DnaGroup)
            if segment is not None:
                contextMenuList.append(None) # separator
                if dnaGroup is not None:
                    item = (("%s of [%s]" % (segment.name, dnaGroup.name)),
                            noop,
                            'disabled')
                else:
                    item = (("%s " % segment.name),
                            noop,
                            'disabled')

                contextMenuList.append(item)
                item = (("Edit DnaSegment Properties..."), 
                        segment.edit)
                contextMenuList.append(item)
                contextMenuList.append(None) # separator
                # add menu commands from our DnaLadder [bruce 080407]
                # REVIEW: see comments for similar code above. [bruce 090115]
                if segment.picked:       
                    selectedDnaSegments = self.assy.getSelectedDnaSegments()
                    if len(selectedDnaSegments) > 0:
                        item = (("Resize Selected DnaSegments "\
                                 "(%d)..." % len(selectedDnaSegments)), 
                                self.assy.win.resizeSelectedDnaSegments)
                        contextMenuList.append(item)
                        contextMenuList.append(None)
                if self.ladder:
                    menu_spec = self.ladder.dnaladder_menu_spec(self)
                    if menu_spec:
                        contextMenuList.extend(menu_spec)
                        
                _addDnaGroupMenuItems(dnaGroup)
                pass
            pass
        return
    
    
    # START of Dna-Strand-or-Axis chunk specific code ==========================

    # Note: all these methods will be removed from class Chunk once the
    # dna data model is always active. [bruce 080205 comment]

    # Assign a strand sequence (or get that information from a chunk).
    # MEANT ONLY FOR THE DNA CHUNK. THESE METHODS NEED TO BE MOVED TO AN 
    # APPROPRIATE FILE IN The dna_model PACKAGE -- Ninad 2008-01-11
    # [And revised to use DnaMarkers for sequence alignment as Ninad suggests below.
    #  The sequence methods will end up as methods of DnaStrand with
    #  possible helper methods on objects it owns, like DnaStrandChunk
    #  (whose bases are in a known order) or DnaMarker or internal objects
    #  they refer to. -- Bruce 080117/080205 comment]

    def getStrandSequence(self): # probably by Ninad or Mark
        """
        Returns the strand sequence for this chunk (strandChunk)
        @return: strand Sequence string
        @rtype: str
        """
        sequenceString = ""
        for atom in self.get_strand_atoms_in_bond_direction():
            baseName = str(atom.getDnaBaseName())        
            if baseName:
                sequenceString = sequenceString + baseName

        return sequenceString

    def setStrandSequence(self, sequenceString): # probably by Ninad or Mark
        """
        Set the strand sequence i.e.assign the baseNames for the PAM atoms in 
        this strand AND the complementary baseNames to the PAM atoms of the 
        complementary strand ('mate strand')
        @param sequenceString: The sequence to be assigned to this strand chunk
        @type sequenceString: str
        """      
        sequenceString = str(sequenceString)
        #Remove whitespaces and tabs from the sequence string
        sequenceString = re.sub(r'\s', '', sequenceString)

        #May be we set this beginning with an atom marked by the 
        #Dna Atom Marker in dna data model? -- Ninad 2008-01-11
        # [yes, see my longer reply comment above -- Bruce 080117]
        atomList = []           
        for atom in self.get_strand_atoms_in_bond_direction():
            if not atom.is_singlet():
                atomList.append(atom)

        for atom in atomList:   
            atomIndex = atomList.index(atom)
            if atomIndex > (len(sequenceString) - 1):
                #In this case, set an unassigned base ('X') for the remaining 
                #atoms
                baseName = 'X'
            else:
                baseName = sequenceString[atomIndex]

            atom.setDnaBaseName(baseName)

            #Also assign the baseNames for the PAM atoms on the complementary 
            #('mate') strand.
            strandAtomMate = atom.get_strand_atom_mate()
            complementBaseName = getComplementSequence(str(baseName))
            if strandAtomMate is not None:
                strandAtomMate.setDnaBaseName(str(complementBaseName))
        return

    def _editProperties_DnaStrandChunk(self):
        """
        Private helper for Chunk.edit; 
        does the dna-related part.
        """
        # probably by Ninad; split out of Chunk.edit by Bruce 090115
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('DNA_STRAND')                
        assert commandSequencer.currentCommand.commandName == 'DNA_STRAND'
        commandSequencer.currentCommand.editStructure(self)
        return
    

    def isStrandChunk(self): # Ninad circa 080117, revised by Bruce 080117
        """
        Returns True if *all atoms* in this chunk are PAM 'strand' atoms
        or 'unpaired-base' atoms (or bondpoints), and at least one is a
        'strand' atom.

        Also resets self.iconPath (based on self.hidden) if it returns True.

        This method is overridden in dna-specific subclasses of Chunk.
        It is likely that this implementation on Chunk itself could now
        be redefined to just return False, but this has not been analyzed closely.
        
        @see: BuildDna_PropertyManager.updateStrandListWidget where this is used
              to filter out strand chunks to put those into the strandList 
              widget.        
        """
        # This is a temporary method that can be removed once dna_model is fully
        # functional. [That is true now; REVIEW whether it can really be removed,
        # or more precisely, redefined to return False on this class. bruce 090106 addendum]
        found_strand_atom = False
        for atom in self.atoms.itervalues():
            if atom.element.role == 'strand':
                found_strand_atom = True
                # side effect: use strand icon [mark 080203]
                if self.hidden:
                    self.iconPath = "ui/modeltree/Strand-hide.png"
                else:
                    self.iconPath = "ui/modeltree/Strand.png"
            elif atom.is_singlet() or atom.element.role == 'unpaired-base':
                pass
            else:
                # other kinds of atoms are not allowed
                return False
            continue

        return found_strand_atom

    def get_strand_atoms_in_bond_direction(self): # ninad 080205; bruce 080205 revised docstring
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
        """
        startAtom = None
        atomList = []

        #Choose startAtom randomly (make sure that it's a PAM3 Sugar atom 
        # and not a bondpoint)
        for atom in self.atoms.itervalues():
            if atom.element.symbol == 'Ss3':
                startAtom = atom
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

    #END of Dna-Strand chunk specific  code ==================================


    #START of Dna-Axis chunk specific code ==================================

    def isAxisChunk(self):
        """
        Returns True if *all atoms* in this chunk are PAM 'axis' atoms
        or bondpoints, and at least one is an 'axis' atom.

        Overridden in some subclasses.

        @see: isStrandChunk
        """
        found_axis_atom = False
        for atom in self.atoms.itervalues():
            if atom.element.role == 'axis':
                found_axis_atom = True
            elif atom.is_singlet():
                pass
            else:
                # other kinds of atoms are not allowed
                return False
            continue

        return found_axis_atom  

    #END of Dna-Axis chunk specific code ====================================


    #START of Dna-Strand-or-Axis chunk specific code ========================

    def isDnaChunk(self):
        """
        @return: whether self is a DNA chunk (strand or axis chunk)
        @rtype: boolean
        """
        return self.isAxisChunk() or self.isStrandChunk()
    

    def getDnaGroup(self): # ninad 080205
        """
        Return the DnaGroup of this chunk if it has one. 
        """
        return self.parent_node_of_class(self.assy.DnaGroup)
    
    def getDnaStrand(self):
        """
        Returns the DnaStrand(group) node to which this chunk belongs to. 
        
        Returns None if there isn't a parent DnaStrand group.
        
        @see: Atom.getDnaStrand()
        """
        if self.isNullChunk():
            return None
        
        dnaStrand = self.parent_node_of_class(self.assy.DnaStrand)
        
        return dnaStrand
    
    def getDnaSegment(self):
        """
        Returns the DnaStrand(group) node to which this chunk belongs to. 
        
        Returns None if there isn't a parent DnaStrand group.
        
        @see: Atom.getDnaStrand()
        """
        if self.isNullChunk():
            return None
        
        dnaSegment = self.parent_node_of_class(self.assy.DnaSegment)
        
        return dnaSegment

    #END of Dna-Strand-or-Axis chunk specific code ========================

    
    def _readmmp_info_chunk_setitem_Dna( self, key, val, interp ):
        """
        Private helper for Chunk.readmmp_info_chunk_setitem.
        
        @return: whether we handled this info record (depends only on key, 
                 not on success vs error)
        @rtype: boolean
        """
        if key == ['display_as_pam']:
            # val should be one of the strings "", MODEL_PAM3, MODEL_PAM5;
            # if not recognized, use ""
            if val not in ("", MODEL_PAM3, MODEL_PAM5):
                # maybe todo: use deferred_summary_message?
                print "fyi: info chunk display_as_pam with unrecognized value %r" % (val,) 
                val = ""
            #bruce 080523: silently ignore this, until the bug 2842 dust fully
            # settles. This is #1 of 2 changes (in the same commit) which
            # eliminates all ways of setting this attribute, thus fixing
            # bug 2842 well enough for v1.1. (The same change is not needed
            # for save_as_pam below, since it never gets set, or ever did,
            # except when using non-default values of debug_prefs. This means
            # someone setting those prefs could save a file which causes a bug
            # only seen by whoever loads it, but I'll live with that for now.)
            ## self.display_as_pam = val
            pass
        elif key == ['save_as_pam']:
            # val should be one of the strings "", MODEL_PAM3, MODEL_PAM5;
            # if not recognized, use ""
            if val not in ("", MODEL_PAM3, MODEL_PAM5):
                # maybe todo: use deferred_summary_message?
                print "fyi: info chunk save_as_pam with unrecognized value %r" % (val,)
                val = ""
            self.save_as_pam = val
        else:
            return False
        return True
    
    def _writemmp_info_chunk_before_atoms_Dna(self, mapping):
        """
        Private helper for Chunk.writemmp_info_chunk_before_atoms.
        
        @return: None
        """
        if self.display_as_pam:
            # not normally set on most chunks, even when PAM3+5 is in use.
            # future optim (unimportant since not normally set):
            # we needn't write this is self contains no PAM atoms.
            # and if we failed to write it when dna updater was off, that would be ok.
            # so we could assume we don't need it for ordinary chunks
            # (even though that means dna updater errors on atoms would discard it).
            mapping.write("info chunk display_as_pam = %s\n" % self.display_as_pam)
        if self.save_as_pam:
            # not normally set, even when PAM3+5 is in use
            mapping.write("info chunk save_as_pam = %s\n" % self.save_as_pam)
        return

    
    def _getToolTipInfo_Dna(self):
        """
        Return the dna-related part of the tooltip string for this chunk
        """
        # probably by Mark or Ninad
        # Note: As of 2008-11-09, this is only implemented for a DnaStrand.
        #bruce 090115 split this out of Chunk.getToolTipInfo
        strand = self.getDnaStrand()
        if strand:
            return strand.getDefaultToolTipInfo()   
        
        segment = self.getDnaSegment()
        if segment:
            return segment.getDefaultToolTipInfo()
                    
        return ""

    
    def _getAxis_of_self_or_eligible_parent_node_Dna(self, atomAtVectorOrigin = None):
        """
        Private helper for Chunk.getAxis_of_self_or_eligible_parent_node;
        does the dna-related part.
        """
        # by Ninad
        #bruce 090115 split this out of Chunk.getAxis_of_self_or_eligible_parent_node
        dnaSegment = self.parent_node_of_class(self.assy.DnaSegment)
        if dnaSegment and self.isAxisChunk():
            axisVector = dnaSegment.getAxisVector(atomAtVectorOrigin = atomAtVectorOrigin)
            if axisVector is not None:
                return axisVector, dnaSegment

        dnaStrand = self.parent_node_of_class(self.assy.DnaStrand)
        if dnaStrand and self.isStrandChunk():
            arbitraryAtom = self.atlist[0]
            dnaSegment = dnaStrand.get_DnaSegment_with_content_atom(
                arbitraryAtom)
            if dnaSegment:
                axisVector = dnaSegment.getAxisVector(atomAtVectorOrigin = atomAtVectorOrigin)
                if axisVector is not None:
                    return axisVector, dnaSegment

        return None, None
    
    pass # end of class Chunk_Dna_methods

# end
