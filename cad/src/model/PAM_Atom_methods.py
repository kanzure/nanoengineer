# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Bruce, Mark, Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080327 split out of chem.py class Atom,
in which these methods had been written

TODO:

fix the import cycle with chem.py due to _changed_otherwise_Atoms and atKey

REVIEW whether any of these methods are sometimes called on non-PAM atoms,
always doing nothing or returning a null value, e.g. getDnaBaseName.

also refactor some code that remains in chem.py but has
PAM-element-specific sections, like the transmute context menu
entries for PAM elements, and some bond_geometry_error_string things
(which needs a separate refactoring first, for other reasons)
"""

from model.elements import Pl5

from utilities.debug import print_compact_stack

from utilities.constants import Pl_STICKY_BOND_DIRECTION, MODEL_PAM5

from model.bond_constants import DIRBOND_CHAIN_MIDDLE
from model.bond_constants import DIRBOND_CHAIN_END
from model.bond_constants import DIRBOND_NONE
from model.bond_constants import DIRBOND_ERROR

from utilities import debug_flags

##from geometry.VQT import V

##from foundation.state_constants import S_CHILDREN

VALID_ELEMENTS_FOR_DNABASENAME = ('Ss5', 'Ss3', 'Sh5', 'Se3', 'Sj5', 'Sj3',)
    # TODO: use a boolean element attribute instead.
    # review: not the same as role == 'strand'... but is it if we exclude Pl?

# ==

class PAM_Atom_methods:
    """
    Intended only as a pre-mixin for class Atom.
    """
    # Someday will be refactored into subclasses of Atom.
    # Then those can be moved inside the dna package.
    # (Maybe this could be moved there right now?)

    # ===
    #
    # The Atom methods below this point might be moved into subclasses for
    # specific types of atoms.
    #
    # (Some of these methods might need trivial default defs on class Atom
    #  until old code is fully revised to only call them on the subclasses.)
    #
    # Several general methods above also have special cases that might be
    # revised to be in subclass methods that extend them. These include:
    #
    #  drawing_color
    #  _draw_atom_style
    #  draw_atom_sphere
    #  draw_wirespheres
    #  max_pixel_radius
    #  writemmp
    #  readmmp_info_atom_setitem
    #  getInformationString
    #
    # (But some of these might be purely graphical, perhaps usable by more than
    # one subclass, and might thus remain in the superclass, or in a separately
    # refactored Atom drawing controller class.)
    #
    # [bruce 071113 comment, and reordered existing methods to move these here]
    #
    # ===

    # default values of instance variables (some not needed):
    
    _dna_updater__error = "" # intentionally not undoable/copyable
    
    # this is now higher up, with an undo _s_attr decl:
    ## _dnaBaseName = "" #bruce 080319 revised

    ## _dnaStrandId_for_generators -- set when first demanded, or can be explicitly set
    ## using setDnaStrandId_for_generators().

    _fake_Pls = None # see comments where used

    # not: _s_attr__nonlive_Pls = S_CHILDREN

    # == methods for either strand or axis PAM atoms

    def dna_updater_error_string(self,
                                 include_propogated_error_details = True,
                                 newline = '\n'
                                 ): #bruce 080206; 080214 also covers check_bond_geometry
        """
        Return "" if self has no dna updater error (recorded by the dna updater
        in the private attribute self._dna_updater__error), or an error string
        if it does.

        By default, the error string is expanded to show the source
        of propogated errors from elsewhere in self's basepair (assuming the updater
        has gotten through the step of propogating them, which it does immediately
        after assigning/updating all the direct per-atom error strings).

        Any newlines in the error string (which only occur if it was expanded)
        are replaced with the optional newline argument (by default, left unchanged).

        @param include_propogated_error_details: see main docstring
        @type include_propogated_error_details: boolean
        
        @param newline: see main docstring
        @type newline: string

        @see: helper functions like _atom_set_dna_updater_error which should
              eventually become friend methods in a subclass of Atom.
        """
        if self.check_bond_geometry():
            # bruce 080214; initial kluge -- if this happens, ignore the rest (non-ideal)
            return self.check_bond_geometry() # (redoing this is fast)
        if not self._dna_updater__error:
            # report errors from self's DnaLadder, if it has one
            ladder = getattr(self.molecule, 'ladder', None) # kluge for .ladder
            if ladder and ladder.error:
                return ladder.error
            return ""
        # otherwise report error from self
        from dna.updater.fix_bond_directions import PROPOGATED_DNA_UPDATER_ERROR
        from dna.updater.fix_bond_directions import _f_detailed_dna_updater_error_string
            # note: use a runtime import for these, until this method can be
            # moved to a subclass of Atom defined in dna_model;
            # even so, this may cause an import cycle issue; ### REVIEW
            # if so, move the imported things into their own file
        res = self._dna_updater__error
        if include_propogated_error_details and \
           res == PROPOGATED_DNA_UPDATER_ERROR:
            res = _f_detailed_dna_updater_error_string(self)
        res = res.replace('\n', newline) # probably only needed in then clause
        return res

    def _pam_atom_cmenu_entries(self): #bruce 080401
        """
        Return a menu_spec list of context menu entries specific to self being
        a PAM atom, or None.
        """
        assert self.element.pam
        ladder = self.molecule.ladder
        res = []
        if ladder: # in case dna updater failed or is not enabled
            conversion_menu_spec = ladder.conversion_menu_spec(self) # IMPLEM in DnaLadder
            if conversion_menu_spec:
                if res: # never happens yet
                    res.append(None)
                res.extend(conversion_menu_spec)
            # more?
            pass
        return res
    
    # == end of methods for either strand or axis PAM atoms
    
    # == PAM strand atom methods (some are more specific than that,
    # e.g. not on Pl or only on Pl)
    
    def setDnaBaseName(self, dnaBaseName): # Mark 2007-08-16
        #bruce 080319 revised, mainly to support undo/copy
        """
        Set the Dna base letter. This is only valid for PAM atoms in the list
        VALID_ELEMENTS_FOR_DNABASENAME, i.e. strand sugar atoms,
        presently defined as ('Ss5', 'Ss3', 'Sh5', 'Se3', 'Sj5', 'Sj3').
        
        @param dnaBaseName: The DNA base letter. This must be "" or one letter
                            (this requirement is only partially enforced here).
        @type  dnaBaseName: str
        
        @raise: AssertionError, if self is not a strand sugar atom or if we
                notice the value is not permitted.
        """
        assert type(dnaBaseName) == type("") #bruce 080326
        
        assert self.element.symbol in VALID_ELEMENTS_FOR_DNABASENAME, \
            "Can only assign dnaBaseNames to PAM strand sugar atoms. " \
            "Attempting to assign dnaBaseName %r to %r of element %r." \
            % (dnaBaseName, self, self.element.name)

        if dnaBaseName == 'X':
            dnaBaseName = ""

        assert len(dnaBaseName) <= 1, \
               "dnaBaseName must be empty or a single letter, not %r" % \
               (dnaBaseName,) #bruce 080326

        # todo: check that it's a letter
        # maybe: canonicalize the case; if not, make sure it doesn't matter

        if self._dnaBaseName != dnaBaseName:
            self._dnaBaseName = dnaBaseName
            from model.chem import _changed_otherwise_Atoms # import cycle, would fail if at toplevel; fix sometime
            _changed_otherwise_Atoms[self.key] = self #bruce 080319
            # todo: in certain display styles, self.molecule.changeapp(0)
            self.changed() # bruce 080319
        return
    
    def getDnaBaseName(self):
        """
        Returns the value of attr I{_dnaBaseName}.
        
        @return: The DNA base name, or None if the attr I{_dnaBaseName} does 
                 not exist.
        @rtype:  str
        """
        # Note: bruce 080311 revised all direct accesses of atom._dnaBaseName
        # to go through this method, and renamed it to be private.
        # (I also stopped storing it in mmp file when value is X, unassigned.
        #  This is desirable to save space and speed up save and load.
        #  If some users of this method want the value on certain atoms
        #  to always exist, this method should be revised to look at
        #  the element type and return 'X' instead of "" for appropriate
        #  elements.)
        
        #UPDATE: The following is now revised per above coment. i.e. if it 
        #can't find a baseName for a valid element symbol (see list below)
        #it makes the dnaBaseName as 'X' (unassigned base) . This is useful 
        #while reading in the strand sequence. See chunk.getStrandSequence()
        #or DnaStrand.getStrandSequence() for an example. --Ninad 2008-03-12

        valid_element_symbols = VALID_ELEMENTS_FOR_DNABASENAME
        allowed_on_this_element = (self.element.symbol in valid_element_symbols)
        
        baseNameString = self.__dict__.get('_dnaBaseName', "") # modified below

        if not allowed_on_this_element:
            #bruce 080319 change: enforce this never existing on disallowed
            # element (probably just a clarification, since setting code was
            # probably already enforcing this)
            baseNameString = ""
        else:
            if not baseNameString:
                baseNameString = 'X' # unassigned base
            pass

        if len(baseNameString) > 1:
            #bruce 080326 precaution, should never happen
            baseNameString = ""
        
        return baseNameString
    
    def get_strand_atom_mate(self):
        """
        Returns the 'mate' of this dna pseudo atom (the atom on another strand 
        to which this atom is "base-paired"), or None if it has no mate.
        @return: B{Atom} (PAM atom) 
        """
        #Note: This method was created to support assignment of strand sequence 
        #to strand chunks. This should be moved to dna_model and
        #can be revised further. -- Ninad 2008-01-14
        # (I revised it slightly, to support all kinds of single stranded
        #  regions. -- Bruce 080117)
        if self.element.role != 'strand':
            # REVIEW: return None, or raise exception? [bruce 080117 Q]
            return None
        
        #First find the connected axis neighbor 
        axisAtom = self.axis_neighbor()
        if axisAtom is None:
            # single stranded region without Ax; no mate
            return None
        #Now find the strand atoms connected to this axis atom
        strandAtoms = axisAtom.strand_neighbors()
        
        #... and we want the mate atom of self
        for atm in strandAtoms:
            if atm is not self:
                return atm
        # if we didn't return above, there is no mate
        # (single stranded region with Ax)
        return None
    
    def setDnaStrandId_for_generators(self, dnaStrandId_for_generators): # Mark 2007-09-04
        # Note: this (and probably its calls) needs revision
        # for the dna data model. Ultimately its only use will be
        # to help when reading pre-data-model mmp files. Presently
        # it's only called when reading "info atom dnaStrandName"
        # records. Those might be saved on the wrong atomtypes
        # by current dna updater code, but the caller tolerates
        # exceptions here (but complains using a history summary).
        # [bruce 080225/080311 comment]
        """
        Set the Dna strand name. This is only valid for PAM atoms in the list
        'Se3', 'Pe5', 'Pl5' (all deprecated when the dna updater is active).
        
        @param dnaStrandId_for_generators: The DNA strand id used by the 
               dna generator 
                                        
        @type  dnaStrandId_for_generators: str
        
        @raise: AssertionError if self is not a Se3 or Pe5 or Pl5 atom.
        @see: self.getDnaStrandId_for_generators() for more comments.
        """
        assert self.element.symbol in ('Se3', 'Pe5', 'Pl5'), \
            "Can only assign dnaStrandNames to Se3, Pe5, or Pl5 (PAM) atoms. " \
            "Attempting to assign dnaStrandName %r to %r of element %r." \
            % (dnaStrandId_for_generators, self, self.element.name)
        
        # Make sure dnaStrandId_for_generators has all valid characters.
        #@ Need to allow digits and letters. Mark 2007-09-04
        """
        for c in dnaStrandId_for_generators:
            if not c in string.letters:
                assert 0, "Strand id for generatos %r has an invalid "\
                "character (%r)." \
                       % (dnaStrandId_for_generators, c)
            """
                
        self._dnaStrandId_for_generators = dnaStrandId_for_generators
        
    def getDnaStrandId_for_generators(self):
        """
        Returns the value of attr I{_dnaStrandId_for_generators}, or "" 
        if it doesn't exist.
        
        @return: The DNA strand id used by dna generator, or "" if the attr 
                 I{_dnaStrandId_for_generators} does not exist.
        @rtype:  str
        """
        # Note: this (and probably its calls) need revision for the
        # dna data model. [bruce 080225/080311 comment]
        # Note: bruce 080311 revised all direct accesses of atom._dnaStrandId_for_generators
        # to go through this method, and renamed it to make it private.
        
        #UPDATE renamed previous attr dnastrandName to 
        # dnaStrandId_for_generators based on a discussion with Bruce. 
        #It was renamed to this new name 
        #in order to avoid confusion with the dna strand name which can 
        #be acceesed as node.name.  The new name 'dnaStrandId_for_generators'
        #and this comment makes it clear enough that this will only be used
        #by generators ... i.e. while creating a duplex from scratch by reading 
        #in the standard mmp files in cad/plugins/PAM*/*.mmp. See 
        #DnaDuplex._regroup to see how this is used.  -- Ninad 2008-03-12 
        
        return self.__dict__.get('_dnaStrandId_for_generators', "")
        
    def directional_bond_chain_status(self): # bruce 071016, revised 080212
        """
        Return a tuple (statuscode, bond1, bond2)
        indicating the status of self's bonds with respect to chains
        of directional bonds. The possible return values are:

        DIRBOND_CHAIN_MIDDLE, bond1, bond2 -- inside a chain involving these two bonds
          (note: there might be other directional bonds (open bonds) which should be ignored)

        DIRBOND_CHAIN_END, bond1, None -- at the end of a chain, which ends with this bond
        
        DIRBOND_NONE, None, None -- not in a chain

        DIRBOND_ERROR, None, None -- local error in directional bond structure,
          so caller should treat this as not being in a chain

        Note that all we consider is whether a bond is directional, not whether
        a direction is actually set (except for atoms with more than one open bond,
        to disambiguate bare chain ends).

        Similarly, when two bonds have directions set, we don't consider whether
        their directions are consistent. (One reason is that we need to grow
        a chain that covers both bonds so the user can set the entire
        chain's direction. REVIEW: better to stop at such errors, so only
        a consistent part of the chain would be changed at once??)

        But if self is monovalent (e.g. a bondpoint) and its neighbor is not,
        we consider its neighbor's status in determining its own.
        
        Note that when drawing a bond, each of its atoms can have an
        almost-independent directional_bond_chain_status (due to the
        possibility of erroneous structures), so both of its atoms
        need their directional_bond_chain_status checked for errors.
        """
        # note: I think this implem is correct with or without open bonds
        # being directional [bruce 071016] [revised 080212 to make more true]
        if not self.element.bonds_can_be_directional:
            # optimization
            return DIRBOND_NONE, None, None
        if len(self.bonds) == 1:
            # Special cases. This then-clause covers all situations for
            # self being monovalent, except a few that I think never happen.
            # (But if they do, fall through to general case below.)
            bond = self.bonds[0]
            neighbor = bond.other(self)
            if len(neighbor.bonds) > 1:
                # Monovalents defer to non-monovalent neighbors
                # (note: this applies to bondpoints (after mark 071014 changes)
                #  or to "strand termination atoms".)
                # Those neighbors may decide bond is not in their chain due
                # to their other bonds.
                statuscode, bond1, bond2 = neighbor.directional_bond_chain_status()
                if statuscode == DIRBOND_NONE or statuscode == DIRBOND_ERROR:
                    return statuscode, None, None
                elif statuscode == DIRBOND_CHAIN_MIDDLE:
                    # it matters whether we're in the neighbor's chain
                    if bond is bond1 or bond is bond2:
                        return DIRBOND_CHAIN_END, bond, None
                    else:
                        # we're attached to the chain but not in it.
                        # REVIEW: return DIRBOND_ERROR in some cases??
                        # (For example, when an atom has ._dna_updater__error set on it?)
                        # Note that for open bonds on bare strands, this happens routinely.
                        return DIRBOND_NONE, None, None # DIRBOND_ERROR?
                    pass
                elif statuscode == DIRBOND_CHAIN_END:
                    # it matters whether the neighbor's chain includes us.
                    # (for bare strand ends with two open bonds, this is up
                    #  to that neighbor even if arbitrary, as of 080212)
                    if bond is bond1:
                        return DIRBOND_CHAIN_END, bond, None
                    else:
                        return DIRBOND_NONE, None, None # DIRBOND_ERROR?
                    pass
                else:
                    assert 0, "%r got unrecognized statuscode %r from %r.directional_bond_chain_status" % \
                           (self, statuscode, neighbor)
                    return DIRBOND_ERROR, None, None
                pass
            else:
                # two connected monovalent atoms, one maybe-directional bond...
                # for now, proceed with no special case. If this ever happens, review it.
                # (e.g. we might consider it an error.)
                pass
            pass
        dirbonds = self.directional_bonds()
        num = len(dirbonds)
        if num == 2:
            # it doesn't matter how many of them are open bonds, in this case
            return DIRBOND_CHAIN_MIDDLE, dirbonds[0], dirbonds[1]
        elif num == 1:
            # whether or not it's an open bond
            return DIRBOND_CHAIN_END, dirbonds[0], None
        elif num == 0:
            return DIRBOND_NONE, None, None
        else:
            # more than 2 -- see if some of them can be ignored
            # [behavior at ends of bare strands was revised 080212]
            real_dirbonds = filter( lambda bond: not bond.is_open_bond(), dirbonds )
            num_real = len(real_dirbonds)
            if num_real == 2:
                # This works around the situation in which a single strand (not at the end)
                # has open bonds where axis atoms ought to be, by ignoring those open bonds.
                # (Note that they count as directional, even though if they became real
                #  they would not be directional since one atom would be Ax.)
                # POSSIBLE BUG: the propogate caller can reach this, if it can start on an
                # ignored open bond. Maybe we should require that it is not offered in the UI
                # in this case, by having it check this method before deciding. ### REVIEW
                return DIRBOND_CHAIN_MIDDLE, real_dirbonds[0], real_dirbonds[1]
            else:
                # we need to look at bond directions actually set
                # (on open bonds anyway), to decide what to do.
                #
                # WARNING: this happens routinely at the end of a "bare strand" (no axis atoms),
                # since it has one real and two open bonds, all directional.
                # 
                # We might fix this by:
                # - making that situation never occur [unlikely]
                # - making bonds know whether they're directional even if they're open (bond subclass)
                # - atom subclass for bondpoints
                # - notice whether a direction is set on just one open bond [done below, 080212];
                # - construct open bonds on directional elements so the right number are set
                #   [dna updater does that now, but a user bond dir change can make it false before calling us]
                # - (or preferably, marked as directional bonds without a direction being set)
                # REVIEW: return an error message string?
                # [bruce 071112, 080212 updated comment]
                if num_real < 2:
                    # new code (bugfix), bruce 080212 -- look at bonds with direction set
                    # (assume dna updater has made the local structure make sense)
                    # (only works if cmenu won't set dir on open bond to make 3 dirs set ### FIX)
                    # kluge (bug): assume all real bonds have dir set. Easily fixable in the lambda if necessary.
                    dirbonds_set = filter( lambda bond: bond._direction, dirbonds ) #k non-private method?
                    if len(dirbonds_set) == 2:
                        return DIRBOND_CHAIN_MIDDLE, dirbonds_set[0], dirbonds_set[1]
                if debug_flags.atom_debug:
                    print "DIRBOND_ERROR noticed on", self
                return DIRBOND_ERROR, None, None
        pass
    
    def strand_end_bond(self): #bruce 070415, revised 071016 ### REVIEW: rename?
        """
        For purposes of possibly drawing self as an arrowhead,
        determine whether self is on the end of a chain of directional bonds
        (regardless of whether they have an assigned direction).
        But if self is a bondpoint attached to a chain of directional real bonds,
        treat it as not part of a bond chain, even if it's directional.
        [REVIEW: is that wise, if it has a direction set (which is probably an error)?]

        @return: None, or the sole directional bond on self (if it
                 might be correct to use that for drawing self as an
                 arrowhead).

        TODO: need a more principled separation of responsibilities
        between self and caller re "whether it might be correct to
        draw self as an arrowhead" -- what exactly is it our job to
        determine?

        REVIEW: also return an error code, for drawing red arrowheads
        in the case of certain errors?
        """
        if not self.element.bonds_can_be_directional:
            return None # optimization
        statuscode, bond1, bond2 = self.directional_bond_chain_status()
        if statuscode == DIRBOND_CHAIN_END:
            assert bond1
            assert bond2 is None
            return bond1
        else:
            return None
        pass
    
    def directional_bonds(self): #bruce 070415
        """
        Return a list of our directional bonds. Its length might be 0, 1, or 2,
        or in the case of erroneous structures [or some legal ones as of
        mark 071014 changes], 3 or more.
        """
        ### REVIEW: should this remain as a separate method, now that its result
        # can't be used naively?
        return filter(lambda bond: bond.is_directional(), self.bonds)

    def bond_directions_are_set_and_consistent(self): #bruce 071204 # REVIEW uses - replace with self._dna_updater__error??
        """
        Does self (a strand atom, base or base linker)
        have exactly two bond directions set, not inconsistently?

        @note: still used, but in some ways superceded by dna updater
               and the error code it can set.
        """
        count_plus, count_minus = 0, 0 # for all bonds
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir == 1:
                count_plus += 1
            elif dir == -1:
                count_minus += 1
        return (count_plus, count_minus) == (1, 1)

    def desired_new_real_bond_direction(self): #bruce 080213
        """
        Something is planning to make a new real directional bond
        involving self, and will modify self's open bonds and/or
        their bond directions, but not self's existing real bonds
        or their bond directions. What bond direction (away from self)
        should it give the new real bond?
        """
        count_plus, count_minus = 0, 0 # for real bonds only
        for bond in self.bonds:
            if not bond.is_open_bond(): # (could optim, doesn't matter)
                dir = bond.bond_direction_from(self)
                if dir == 1:
                    count_plus += 1
                elif dir == -1:
                    count_minus += 1
        counts = (count_plus, count_minus)
        if counts == (1, 0):
            return -1
        elif counts == (0, 1):
            return 1
        else:
            # Usually or always an error given how we are called,
            # but let the caller worry about this.
            # (Non-error cases are conceivable, e.g. within a dna generator,
            #  or if isolated single bases are being bonded by the user.)
            return 0
        pass
    
    def fix_open_bond_directions(self, bondpoint, want_dir): #bruce 080213
        """
        Something is planning to make a new real directional bond
        involving self, and will give it the bond direction want_dir
        (measured away from self). If bondpoint is not None, it plans
        to make this bond using that bondpoint (usually removing it).
        Otherwise... which bondpoint will it remove, if any?? ###REVIEW CALLERS

        If possible and advisable, fix all our open bond directions
        to best fit this situation -- i.e.:

        * make the direction from self to bondpoint equal want_dir
        (if bondpoint is not None);

        * if want_dir is not 0, remove equal directions from other
        open bonds of self to make the resulting situation consistent
        (do this even if you have to pick one arbitrarily? yes for now);

        * if want_dir is 0, do nothing (don't move any direction set on
        bondpoint to some other open bond of self, because this only
        happens on error (due to how we are called) and we should do
        as little as possible here, letting dna updater and/or user
        see and fix the error).

        @note: it's ok for this method to be slow.
        """
        debug = debug_flags.atom_debug
        if debug:
            print "debug fyi: fix_open_bond_directions%r" % ((self, bondpoint, want_dir),)

        if bondpoint:
            bondpoint_bond = bondpoint.bonds[0]
            # redundant: assert bond.other(bondpoint) is self
            bondpoint_bond.set_bond_direction_from( self, want_dir)
        else:
            bondpoint_bond = None
            # print this until I see whether & how this happens:
            msg = "not sure what fix_open_bond_directions%r should do since bondpoint is None" % \
                  ((self, bondpoint, want_dir),)
                # not sure, because we might want to deduct want_dir from the desired total direction
                # we need to achieve on the other bonds, depending on what caller will do.
                # (If caller will pick one arbitrarily, we need to know which one that is now!)
            if debug_flags.atom_debug:
                print_compact_stack(msg + ": ")
            else:
                print msg + " (set debug flag to see stack)"
        
        if not self.bond_directions_are_set_and_consistent():
            if debug:
                print "debug fyi: fix_open_bond_directions%r needs to fix other open bonds" % \
                      ((self, bondpoint, want_dir),)
            # Note: not doing the following would cause undesirable messages,
            # including history messages from the dna updater,
            # but AFAIK would cause no other harm when the dna updater is turned on
            # (since the updater would fix the errors itself if this could have fixed them).
            if want_dir:
                num_fixed = [0]
                fixable_open_bonds = filter( lambda bond:
                                                 bond.is_open_bond() and
                                                 bond is not bondpoint_bond and
                                                 bond.bond_direction_from(self) != 0 ,
                                             self.bonds )
                def number_with_direction( bonds, dir1 ):
                    "return the number of bonds in bonds which have the given direction from self"
                    return len( filter ( lambda bond: bond.bond_direction_from(self) == dir1 , bonds ))
                def fix_one( bonds, dir1):
                    "fix one of those bonds (by clearing its direction)"
                    bond_to_fix = filter ( lambda bond: bond.bond_direction_from(self) == dir1 , bonds )[0]
                    if debug:
                        print "debug fyi: fix_open_bond_directions(%r) clearing %r of direction %r" % \
                              (self, bond_to_fix, dir1)
                    bond_to_fix.clear_bond_direction()
                    num_fixed[0] += 1
                    assert num_fixed[0] <= len(self.bonds) # protect against infloop
                for dir_to_fix in (1, -1): # or, only fix bonds of direction want_dir?
                    while ( number_with_direction( self.bonds, dir_to_fix ) > 1 and
                            number_with_direction( fixable_open_bonds, dir_to_fix ) > 0 ) :
                        fix_one( fixable_open_bonds, dir_to_fix )
                    continue
            # if this didn't fix everything, let the dna updater complain
            # (i.e. we don't need to ourselves)
            pass
            
        return # from fix_open_bond_directions
    
    def next_atom_in_bond_direction(self, bond_direction): #bruce 071204
        """
        Assuming self is in a chain of directional bonds
        with consistently set directions,
        return the next atom (of any kind, including bondpoints)
        in that chain, in the given bond_direction.

        If the chain does not continue in the given direction, return None.

        If the assumptions are false, no error is detected, and no
        exception is raised, but either None or some neighbor atom
        might be returned.

        @note: does not verify that bond directions are consistent.
        Result is not deterministic if two bonds from self have
        same direction from self (depends on order of self.bonds).
        """
        assert bond_direction in (-1, 1)
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir == bond_direction:
                return bond.other(self)
        # todo: could assert self is a termination atom or bondpoint,
        # or if not, that self.bond_directions_are_set_and_consistent()
        # (if we do, revise docstring)
        return None

    def Pl_preferred_Ss_neighbor(self): # bruce 080118, revised 080401
        """
        For self a Pl atom (PAM5), return the Ss neighbor
        it prefers to be grouped with (e.g. in the same chunk,
        or when one of its bonds is broken) if it has a choice.

        (If it has no Ss atom, print bug warning and return None.)

        @warning: the bond direction constant hardcoded into this method
        is an ARBITRARY GUESS as of 080118. Also it ought to be defined
        in some dna-related constants file (once this method is moved
        to a dna-related subclass of Atom).
        """
        assert self.element is Pl5
        candidates = [
            # note: these might be None, or conceivably a non-Ss atom
            self.next_atom_in_bond_direction( Pl_STICKY_BOND_DIRECTION),
            self.next_atom_in_bond_direction( - Pl_STICKY_BOND_DIRECTION)
         ]
        candidates = [c
                      for c in candidates
                      if c is not None and \
                        c.element.symbol.startswith("Ss")
                          # KLUGE, matches Ss3 or Ss5
                      ]
            # note: this cond excludes X (good), Pl (bug if happens, but good).
            # It also excludes Sj and Hp (bad), but is only used from dna updater
            # so that won't be an issue. Non-kluge variant would test for
            # "a strand base atom".
        candidates_PAM5 = [c for c in candidates if c.element.pam == MODEL_PAM5]
            # Try these first, so we prefer Ss5 over Ss3 if both are present,
            # regardless of bond direction. [bruce 080401]
        for candidate in candidates_PAM5 + candidates:
            # all necessary tests were done above
            return candidate
        print "bug: Pl with no Ss: %r" % self
            # only a true statement (that this is a bug) when dna updater
            # is enabled, but that's ok since we're only used then
        return None
    
    def axis_neighbor(self): #bruce 071203; bugfix 080117 for single strand
        """
        Assume self is a PAM strand sugar atom; return the single neighbor of
        self which is a PAM axis atom, or None if there isn't one
        (indicating that self is part of a single stranded region).

        @note: before the dna updater is turned on by default, this may or may
        not return None for the single-stranded case, since there is no
        enforcement of one way of representing single strands. After it is
        turned on, it is likely that it will always return None for free-
        floating single strands, but this is not fully decided. For "sticky
        ends" it will return an axis atom, since they will be represented
        internally as double strands with one strand marked as unreal.
        """
        axis_neighbors = filter( lambda atom: atom.element.role == 'axis',
                                 self.neighbors())
        if axis_neighbors:
            assert len(axis_neighbors) == 1, \
                   "%r.axis_neighbor() finds more than one: %r" % \
                   (self, axis_neighbors)
                # stub, since the updater checks needed to ensure this
                # are NIM as of 071203
            return axis_neighbors[0]
        return None

    def Pl_neighbors(self): #bruce 080122
        """
        Assume self is a PAM strand sugar atom; return the neighbors of self
        which are PAM Pl (pseudo-phosphate) atoms (or any variant thereof,
         which sometimes interposes between strand base sugar pseudoatoms).
        """
        res = filter( lambda atom: atom.element is Pl5,
                      self.neighbors())
        return res

    def strand_base_neighbors(self): #bruce 071204 (nim, not yet needed; #e maybe rename)
        """
        Assume self is a PAM strand sugar atom; return a list of the neighboring
        PAM strand sugar atoms (even if PAM5 linker atoms separate them from
        self).
        """
        # review: should the return value also say in which direction each one lies,
        # whether in terms of bond_direction or base_index_direction?       
        assert 0, "nim"

    def strand_next_baseatom(self, bond_direction = None): #bruce 071204
        """
        Assume self is a PAM strand sugar atom, and bond_direction is -1 or 1.
        Find the next PAM strand sugar atom (i.e. base atom) in the given
        bond direction, or None if it is missing (since the strand ends),
        or if any bond directions are unset or inconsistent,
        or if any other structural error causes difficulty,
        or if ._dna_updater__error is set in either self or in the atom
        we might otherwise return (even if that error was propogated
         from elsewhere in that atom's basepair, rather than being a
         problem with that atom itself).
        """
        # note: API might be extended to permit passing a baseindex direction
        # instead, and working on either strand or axis baseatoms.
        assert bond_direction in (-1, 1)
        if self._dna_updater__error: #bruce 080131 new feature (part 1 of 3)
            return None
        atom1 = self.next_atom_in_bond_direction(bond_direction) # might be None or a bondpoint
        if atom1 is None:
            return None
        if atom1._dna_updater__error: #bruce 080131 new feature (part 2 of 3)
            return None
        # REVIEW: the following should probably test element.role == 'strand',
        # but that includes Se3 and Sh3 end-atoms, unlike this list.
        # Not an issue when dna updater is on and working,
        # but if it's disabled to work with an old file, that change
        # might cause bugs. But I don't feel fully comfortable with
        # making this depend at runtime on dna_updater_is_enabled()
        # (not sure why). So leave it alone for now. [bruce 080320]
        symbol = atom1.element.symbol # KLUGE -- should use another element attr, or maybe Atom subclass
        if symbol[0:2] not in ('Ss', 'Sj', 'Hp', 'Pl'): # base or base linker atoms (#todo: verify or de-kluge)
            return None
        if symbol.startswith('Pl'): # base linker atom
            # move one more atom to find the one to return
            atom1 = atom1.next_atom_in_bond_direction(bond_direction) # might be None or a bondpoint
            assert atom1 is not self
                # (false would imply one bond had two directions,
                #  or two bonds between same two atoms)
            if atom1 is None:
                return None
            if atom1._dna_updater__error: #bruce 080131 new feature (part 3 of 3)
                return None
            if atom1.element.symbol[0:2] not in ('Ss', 'Sj', 'Hp'):
                return None
            pass
        return atom1

    def _f_get_fake_Pl(self, direction): #bruce 080327
        """
        [friend method for PAM3+5 -> PAM5 conversion code]

        Find or make, and return, a cached fake Pl5 atom
        with a properly allocated and unchanging atom.key,
        to be used in the PAM5 form of self if self does not
        have a real Pl atom in the given bond_direction.

        The atom we return might be used only for mmp writing
        of a converted form, without making any changes in the model,
        or it might become a live atom and get used in the model.
        To make it a live atom, special methods must be called [nim]
        which remove it from being able to be returned by this method.

        If self does have a real such Pl atom, the atom we
        might otherwise return might still exist, but this
        method won't be called to ask for it. It may or may
        not detect that case. If it detects it, it will
        treat it as an error. However, it's not an error for
        the cached atom to survive during the time a live Pl
        atom takes it place, and to be reused if that live
        Pl atom ever dies. OTOH, the cached Pl atom might have
        formerly been a live Pl atom in the same place
        (i.e. bonded to self in the given bond_direction),
        killed when self was converted to PAM3.

        The 3d position (atom.posn()) of the returned atom
        is arbitrary, and can be changed by the caller for its
        own purposes. Absent structure changes to self, the
        identity, key, and 3d position of the returned atom
        won't be changed between calls of this method
        by the code that implements the service of which this
        method is part of the interface.
        """
        fake_Pls = self._fake_Pls # None, or a 2-element list
            # Note: this list is NOT part of the undoable state, nor are the
            # fake atoms within it.
            #
            # REVIEW: should these have anything to do with storing Pl-posn "+5" data?
            # is that data in the undoable state? I think it is, and these are not,
            # so they probably don't help store it.
            
        if not fake_Pls:
            fake_Pls = self._fake_Pls = [None, None]
        assert direction in (1, -1)
        index = (direction == 1) # arbitrary ### clean up dup code when we have some
        Pl = fake_Pls[index]
        from dna.model.pam_conversion_mmp import Fake_Pl # import cycle??? guess no...
        if Pl is None:
            Pl = fake_Pls[index] = Fake_Pl(self, direction)
                ## not: self.__class__(Pl5, V(0,0,0))
        # obs cmt: maybe: let Pl be live, and if so, verify its bonding with self??
        assert isinstance(Pl, Fake_Pl)
        # nonsense: ## assert Pl.killed() # for now
        return Pl
    
    # == end of PAM strand atom methods
    
    # == PAM axis atom methods
    
    def strand_neighbors(self): #bruce 071203
        """
        Assume self is a PAM axis atom; return the neighbors of self
        which are PAM strand sugar atoms. There are always exactly one or
        two of these [NIM] after the dna updater has run.
        """
        # [stub -- need more error checks in following (don't return Pl).
        #  but this is correct if structures have no errors.]
        res = filter( lambda atom: atom.element.role == 'strand',
                      self.neighbors())
        ##assert len(res) in (1, 2), \
        ##       "error: axis atom %r has %d strand_neighbors (should be 1 or 2)"\
        ##       % (self, len(res))
        # happens in mmkit - leave it as just a print at least until we implem "delete bare atoms" -
        if not ( len(res) in (1, 2) ):
            print "error: axis atom %r has %d strand_neighbors " \
                  "(should be 1 or 2)" % (self, len(res))
        return res

    def axis_neighbors(self): #bruce 071204
        # (used on axis atoms, not sure if used on strand atoms)
        return filter( lambda atom: atom.element.role == 'axis',
                       self.neighbors())

    # == end of PAM axis atom methods
    
    pass # end of class PAM_Atom_methods

# end
