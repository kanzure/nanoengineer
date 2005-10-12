# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
chunk.py -- provides class molecule, for a chunk of atoms
which can be moved and selected as a unit.

$Id$

History:

- originally by Josh

- lots of changes, by various developers

- split out of chem.py by bruce circa 041118

- bruce optimized some things, including using 'is' and 'is not' rather than '==', '!='
  for atoms, molecules, elements, parts, assys in many places (not all commented individually); 050513
'''
__author__ = "Josh"

# a lot of what we import from chem might not be needed here in chunk.py,
# but note that as of 050502 they are all imported into chem.py (at end of that file)
# and everything from it is imported into some other modules.
# [bruce comment 050502] ###@@@

from chem import *

from debug import print_compact_stack, print_compact_traceback
from inval import InvalMixin
from changes import SelfUsageTrackingMixin, SubUsageTrackingMixin
    #bruce 050804, so glpanes can know when they need to redraw a chunk's display list,
    # and chunks can know when they need to inval that because something drawn into it
    # would draw differently due to a change in some graphics pref it used
from prefs_constants import atomHotspotColor_prefs_key
import env

_inval_all_bonds_counter = 1 #bruce 050516


# == debug code is near end of file


# == Molecule (i.e. Chunk)

# (Josh wrote:)
# I use "molecule" and "part" interchangeably throughout the program.
# this is the class intended to represent rigid collections of
# atoms bonded together, but it's quite possible to make a molecule
# object with unbonded atoms, and with bonds to atoms in other
# molecules

# [bruce 050315 adds: I've seen "part" used for the assembly, but not for "chunk"
#  (which is the current term for instances of class molecule).
#  Now, however, each assy has one or more Parts, each with its own
#  physical space, containing perhaps many bonded chunks. So any use of
#  "part" to mean "chunk" would be misleading.]

# Huaicai: It's completely possible to create a molecule without any atoms,
# so don't assume it always has atoms.   09/30/04
# (However, as of bruce 041116 we kill any mol which loses all its atoms
# after having had some. This is an experimental change; if it causes
# problems, we should instead do it when we update the model tree or glpane,
# since we need to ensure it's always done by the end of any user event.)

class molecule(Node, InvalMixin, SelfUsageTrackingMixin, SubUsageTrackingMixin):

    # class constants to serve as default values of attributes
    _hotspot = None
    _colorfunc = None
    # this overrides global display (GLPane.display)
    # but is overriden by atom value if not default
    # [bruce 051011 moved it here from __init__, desirable for all undoable attrs]
    display = diDEFAULT
    # this overrides atom colors if set
    color = None
        
    # user_specified_center -- see far below; as of 050526 it's sometimes used, but it's always None

    copyable_attrs = Node.copyable_attrs + ('display', 'color') # this extends the tuple from Node
        # (could add _colorfunc, but better to handle it separately in case this gets used for mmp writing someday,
        #  as of 051003 _colorfunc would anyway not be permitted since state_utils.copy_val doesn't know how to copy it.)
        #e should add user_specified_center once that's in active use
    
    def __init__(self, assembly, name = None):
        self.invalidate_all_bonds() # bruce 050516 -- needed in init to make sure
            # the counter it sets is always set, and always unique
        # note [bruce 041116]:
        # new molecules are NOT automatically added to assembly.
        # this has to be done separately (if desired) by assembly.addmol
        # (or the equivalent).
        # addendum [bruce 050206 -- describing the situation, not endorsing it!]:
        # (and for clipboard mols it should not be done at all!
        #  also not for mols "created in a Group", if any; for those,
        #  probably best to do addmol/moveto like files_mmp does.)
        if not self.mticon:
            self.init_icons()
        self.init_InvalMixin()
        ## dad = None #bruce 050216 removed dad from __init__ args, since no calls pass it
            # and callers need to do more to worry about the location anyway (see comments above) 
        Node.__init__(self, assembly, name or gensym("Chunk."))
        
        # atoms in a dictionary, indexed by atom.key
        self.atoms = {}
        
        # note: motors, grounds (aka "jigs") are stored on atoms, not here;
        # so are bonds, but we have a list of external bonds, self.externs,
        # which is computed by __getattr__ and _recompute_externs; we have
        # several other attributes computed by _get_ or _recompute_ methods
        # using InvalMixin.__getattr__, e.g. center, bbox, basepos, atpos.
        # [bruce 041112]
        
        self.curpos = [] # should always exist; not itself invalidatable,
        # but reset by _recompute_atpos

        # molecule-relative coordinate system, used internally to speed up
        # redrawing after mol is moved or rotated:
        self.basecenter = V(0,0,0) # origin, for basepos, used for redrawing
        self.quat = Q(1, 0, 0, 0) # attitude in space, for basepos
        # note: as of bruce 041112, the old self.center is split into several
        # attributes which are not always the same:
        # - self.center (public, the center for use by UI operations on the mol,
        #   defined by _recompute_center);
        # - self.basecenter (private, for the mol-relative coordinate system,
        #   often equal to self.center but not always);
        # - self.user_specified_center (None or a user-defined center; mostly
        #   not yet implemented; would need to be transformed like an atom posn);
        # - self.average_position (average posn of atoms or singlets; default
        #   value for self.center).
        
        # this set and the molecule in assembly.selmols
        # must remain consistent
        ## self.picked=0 # bruce 050308 removed this, redundant with Node.__init__
        
        # for caching the display as a GL call list
        self.displist = glGenLists(1)
        self.havelist = 0 # note: havelist is not handled by InvalMixin
        self.haveradii = 0 # ditto
        
        # hotspot: default place to bond this molecule when pasted;
        # should be a singlet in this molecule, or None.
        ## old code: self.hotspot = None
        # (As of bruce 050217 (to fix bug 312)
        # this is computed by getattr each time it's needed,
        # using self._hotspot iff it's still valid, forgetting it otherwise.
        # This is needed since code which removes or kills singlets, or transmutes
        # them, does not generally invalidate the hotspot explicitly,
        # but it does copy or keep it
        # (e.g. in mol.copy or merge) even when doing so is questionable.)
        #    BTW, we don't presently save the hotspot in the mmp file,
        # which is a reported bug which we hope to fix soon.
        
        return # from molecule.__init__

    def _um_replace_atkeypos(self, val, model): #bruce 051011 for Undo ####@@@@ call it
        ###e change name of atkeypos to make it obvious it's virtual?
        "[overrides usual setattr called by GenericDiffTracker_API_Mixin for self.atkeypos]"
        # does private things to Atom attributes; see also similar code in self.merge()
        keys, posns = val # a pair of Numeric arrays, containing the keys and posns of the atoms we should have
        atoms_want_and_have = {}
        atoms_missing = {}
        atoms_had = self.atoms
        self.atoms = 333 # not a sequence or dict (force exception if self.atoms used before it's replaced below)
        for key in keys: # atoms we want
            atom = atoms_had.pop(key, None) # have it already?
            if atom is not None:
                atoms_want_and_have[key] = atom
            else:
                # The atom is not in self, but our intended caller (Undo) guarantees it exists,
                # since it knows to create objs before needing them, so find it. It might be in
                # some other chunk, or in no chunk (if just created by Undo).
                from chem import live_atom_for_key
                atoms_missing[key] = live_atom_for_key(key)
        for key, atom in atoms_had.itervalues():
            # We no longer want this atom; set its chunk/posn-related fields to illegal values (to detect bugs);
            # don't use an ordinary atom-removing method (delatom), since that would try to modify self.atoms.
            atom.index = -1
            atom.molecule = None
            atom.xyz = None
            # We don't know yet if some other chunk will want it, so tell model in case no one wants it and it needs deleting.
            model.maybe_discard_atom(atom)
            nim #####@@@@@ worry about effect on atom.picked, or side effects if atom is picked...
        del atoms_had
        # now bring atoms_missing into atoms_want_and_have
        oldmols = {}
        for key, atom in atoms_missing.itervalues():
            # steal this atom for use in self
            oldmol = atom.molecule
            oldmols[id(oldmol)] = oldmol
                # we must call invalidate_atom_lists (below) before anything but this loop could act on oldmol
            atom.molecule = self
            atom.index = -1 # fixed below (this assignment is just to detect bugs)
            atom.xyz = 'no' # this is necessary
            atoms_want_and_have[key] = atom
            #####@@@@@ do something to invalidate its bonds? no need, they store the molecule they're valid for, I think... ###k
        for mol in oldmols.itervalues():
            if isinstance(mol, molecule): # mol might be None if the atom is new
                mol.invalidate_atom_lists()
                # (This should not be needed by anticipated calls from Undo, if no bugs,
                #  since atoms stolen from one mol are added to another, but it's safer to do it.)
        self.atoms = atoms_want_and_have
        self.invalidate_atom_lists()
        self.invalidate_attrs(['atpos'])
        assert len(self.atoms) == len(keys)
        ###e we could optim by just plopping in the posns array as self.atpos and self.curpos
        # and writing new code to do the remainder of _recompute_atpos, but this is simpler for now:
        self.curpos = + posns
        for i in range(len(keys)):
            key = keys[i]
            atom = atoms_want_and_have[key]
            atom.index = i
            assert atom.xyz == 'no'
        # now _recompute_atpos should do the right thing when next used. #k
        return
        
    def break_interpart_bonds(self): #bruce 050308-16 to help fix bug 371; revised 050513
        "[overrides Node method]"
        assert self.part is not None
        # check atom-atom bonds
        for b in self.externs[:]:
            #e should this loop body be a bond method??
            m1 = b.atom1.molecule # one of m1,m2 is self but we won't bother finding out which
            m2 = b.atom2.molecule
            if m1.part is not m2.part:
                assert m1.part is not None and m2.part is not None ###@@@ justified??
                b.bust() 
        # check atom-jig bonds ####@@@@ in the future! Callers also need to handle some jigs specially first, which this would destroy
        ### actually this would be inefficient from this side (it would scan all atoms), so let's let the jigs handle it...
        # tho that won't work when we can later apply this to a subtree... so review it then.
        return
    
    def set_hotspot(self, hotspot, permit_invalid = False): #bruce 050217; 050524 added keyword arg
        # make sure no other code forgot to call us and set it directly
        assert not 'hotspot' in self.__dict__.keys(), "bug in some unknown other code"
        self._hotspot = hotspot
        assert self.hotspot is hotspot or permit_invalid, "getattr bug, or specified hotspot is invalid"
        assert not 'hotspot' in self.__dict__.keys(), "bug in getattr for hotspot"
        return
    
    def _get_hotspot(self): #bruce 050217; used by getattr
        hs = self._hotspot
        if hs is None: return None
        if hs.is_singlet() and hs.molecule is self:
            # hs should be a valid hotspot; if you see no bug, return it
            if hs.killed_with_debug_checks(): # this also checks whether its key is in self.atoms
                # bug detected
                if platform.atom_debug:
                    print "_get_hotspot sees killed singlet still claiming to be in this molecule"
                # fall thru
            else:
                # return a valid hotspot.
                # (Note: if there is no hotspot but exactly one singlet,
                # some callers treat that singlet as the hotspot,
                # but others don't want that feature, so it would be
                # wrong to do that here.)
                return hs
        # hs is not valid (this is often not a bug); forget about it and return None
        self._hotspot = None
        return None
    
    # bruce 041202/050109 revised the icon code; see longer comment about
    # Jig.init_icons for explanation; this might be moved into class Node later
    mticon_names = [
	"moldefault.png",
	"molinvisible.png",
	"molvdw.png",
	"mollines.png",
	"molcpk.png",
	"moltubes.png" ]
    hideicon_names = [
        "moldefault-hide.png",
        "molinvisible-hide.png",
        "molvdw-hide.png",
        "mollines-hide.png",
        "molcpk-hide.png",
        "moltubes-hide.png" ]
    mticon = []
    hideicon = []
    def init_icons(self):
        # see also the same-named, related method in class Jig.
        """each subclass must define mticon = [] and hideicon = [] as class constants...
        but molecule is the only subclass, for now.
        """
        if self.mticon or self.hideicon:
            return
        # the following runs once per Atom session.
        for name in self.mticon_names:
            self.mticon.append( imagename_to_pixmap( name))
        for name in self.hideicon_names:
            self.hideicon.append( imagename_to_pixmap( name))
        return

    def node_icon(self, display_prefs): # bruce 050109 revised this [was seticon]
        if self.hidden:
            return self.hideicon[self.display]
        else:
            return self.mticon[self.display]
    
    def bond(self, at1, at2):
        """Cause atom at1 to be bonded to atom at2.
        Error if at1 is at2 (causes printed warning and does nothing).
        (This should really be a separate function, not a method on molecule,
        since the specific molecule asked to do this need not be either atom's
        molecule, and is not used in the method at all.)
        """
        bond_atoms(at1, at2) #bruce 041109 split out separate function to do it
        ## old code assumed both atoms were in this molecule; often not true!
        ## self.havelist = 0
        return

    # lowest-level structure-changing methods
    
    def addatom(self, atm):
        """Private method;
        should be the only way new atoms can be added to a molecule
        (except for optimized callers like molecule.merge).
           Add an existing atom (with no current molecule, and with a valid literal
        .xyz field) to molecule self, doing necessary invals in self, but not yet
        giving the new atom an index in our curpos, basepos, etc (which will not
        yet include the new atom at all).
           Details of invalidations: Curpos must be left alone (so as not
        to forget the positions of other atoms); the other atom-position arrays
        (atpos, basepos) and atom lists (atlist) are defined to be complete, so
        they're invalidated, and so are whatever other attrs depend on them.
        In the future we might change this function to incrementally grow those
        arrays. This will be transparent to callers since they are now recomputed
        as needed by __getattr__.
           (It's not worth tracking changes to the set of singlets in the mol,
        so instead we recompute self.singlets and self.singlpos as needed.)
        """
        ## atm.invalidate_bonds() # might not be needed
        ## [definitely not after bruce 050516, since changing atm.molecule is enough;
        #   if this is not changing it, then atm was in _nullMol and we don't care
        #   whether its bonds are valid.]
        # make atom know molecule
        assert atm.molecule is None or atm.molecule is _nullMol
        atm.molecule = self
        atm.index = -1 # illegal value
        assert atm.xyz != 'no'
        # make molecule have atom
        self.atoms[atm.key] = atm
        self.invalidate_atom_lists()
        return

    def addcopiedatom(self, atm):
        """private method for mol.copy;
        leaves out asserts which are wrong in that case; caller must do invals
        (it can do invalidate_atom_lists once, for many calls of this)
        """
        atm.molecule = self
        self.atoms[atm.key] = atm
        return
    
    def delatom(self, atm):
        """Private method;
        should be the only way atoms can be removed from a molecule
        (except for optimized callers like molecule.merge).
           Remove atom atm from molecule self, preparing atm for being destroyed
        or for later addition to some other mol, doing necessary invals in self,
        and (for safety and possibly to break cycles of python refs) removing all
        connections from atm back to self.
        """
        ## atm.invalidate_bonds() # not needed after bruce 050516; see comment in addatom
        self.invalidate_atom_lists() # do this first, in case exceptions below

        # make atom independent of molecule
        assert atm.molecule is self
        atm.xyz = atm.posn() # make atom know its position independently of self
        # atm.posn() uses atm.index and atm.molecule, so must be used before
        # those are trashed by the following code:
        atm.index = -1 # illegal value
        global _nullMol
        if _nullMol is None:
            # this caused a bus error when done right after class molecule
            # defined; don't know why (class Node not yet ok??) [bruce 041116]
            _nullMol = molecule("<not an assembly>", 'name-of-_nullMol')
        atm.molecule = _nullMol # not a real mol; absorbs invals without harm
        # (note, we *don't* add atm to _nullMol.atoms, or do invals on it here;
        #  see comment about _nullMol where it's defined)

        # make molecule forget about atom
        del self.atoms[atm.key] # callers can check for KeyError, always an error
        if not self.atoms:
            self.kill() # new feature, bruce 041116, experimental
        return

    # some invalidation methods
    
    def invalidate_atom_lists(self):
        """private method: for now this is the same for addatom and delatom
        so we have common code for it --
        some atom is joining or leaving this mol, do all needed invals
        (or this can be called once if many atoms are joining and/or leaving)
        """
        self.havelist = 0
        self.haveradii = 0
        # bruce 050513 try to optimize this
        # (since it's 25% of time to read atom records from mmp file, 1 sec for 8k atoms)
        ## self.invalidate_attrs(['externs','atlist'])
            # (invalidating externs is needed if atom (when in mol) has bonds
            # going out (extern bonds), or inside it (would be extern if atom
            # moved out), so do it always)
        need = 0
        try:
            del self.externs
        except:
            pass
        else:
            need = 1
        try:
            del self.atlist
        except:
            pass
        else:
            need = 1
        if need:
            # this causes trouble, not yet sure why:
            ## self.changed_attrs(['externs','atlist'])
            ## AssertionError: validate_attr finds no attr 'externs' was saved, in <Chunk 'Ring Gear' (5167 atoms) at 0xd967440>
            # so do this instead:
            self.externs = self.atlist = -1
            self.invalidate_attrs(['externs','atlist'])
        return

    # debugging methods (not fully tested, use at your own risk)
    
    def invalidate_everything(self):
        "debugging method"
        self.invalidate_all_bonds()
        self.havelist = 0
        self.haveradii = 0
        attrs  = self.invalidatable_attrs()
        attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            self.invalidate_attr(attr)
        # (these might be sufficient: ['externs','atlist', 'atpos'])
        return

    def update_everything(self):
        attrs  = self.invalidatable_attrs()
        attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            junk = getattr(self, attr)
        # don't actually remake display list, but next redraw will do that;
        # don't invalidate it (havelist = 0) since our semantics are to only
        # update.
        return
    
    # some more invalidation methods
    
    def setatomposn(self, ind, pos, element): #bruce 041108-10
        """(private method for our atoms to call:)
        Set position in self, of the atom with index ind, to pos.
        Invalidate or incrementally update whatever is required
        in this molecule (but not bonds or jigs, invalled by the atom);
        presently [041110] we incrementally update all atom-position
        arrays which are already present.
           This should be the only way to move an individual atom or singlet,
        since it's the only place that invalidates the position arrays.
        But it is not yet the way movie playing moves atoms,
        even though it's ok for frozen molecules too.
        [As of 050406 it is now done by movie-playing!]
           Don't use this when the entire mol moves in a systematic way
        such that self.basepos remains valid, as in mol.move or mol.rot.
        """
        # Theory:
        #    It's probably worth patching whatever arrays store pos, in any
        # coordinate system (though whether the saving in recomputation is
        # actually worth the time cost in doing the patching is not clear).
        #    We can optimize by stopping when we find a missing array attr,
        # since whatever attrs depend on that must also be missing (or this
        # would indicate a bug in invalidation). This optim is done in this
        # code and also in the InvalMixin routines, and it's the reason
        # for the requirement that (for example) _recompute_singlpos must
        # access self.atpos since _inputs_for_singlpos includes 'atpos'.
        
        # Summary of the influences between invalidatable attributes we handle;
        # the proper "other" ones are invalled automatically by changed_attr:
        # Curpos (not invalidatable);
        # atpos -> basepos -> various non-array attrs;
        # atpos also directly affects other non-array attrs;
        # and havelist (treated specially).
        self.havelist = 0
        # arrays that store pos directly (everything else depends on them):
        self.curpos[ind] = pos
        atpos = self.__dict__.get('atpos')
        if atpos is None: # note: "if atpos" would be false if all entries 0.0!
            # nothing more to do -- everything else depends on atpos
            return
        assert atpos is self.curpos, "atpos should be same object as curpos"
            # (thus no need for "atpos[ind] = pos")
        # Now invalidate whatever depends on atpos, except for basepos
        # (and things only influenced through it),
        # since we will handle basepos ourself and don't want it to be
        # deleted by this!
        self.changed_attr('atpos', skip = ('basepos',) )
        # Now check basepos.
        # We only need to store something in basepos if that exists,
        # and is not the same object as curpos.
        # Note: "if basepos" would be false if all entries were 0.0, and this is
        # usually the case for a 1-atom molecule! [That mistake in the following
        # code caused bug 218, fixed by bruce 041130.]
        basepos = self.__dict__.get('basepos')
        if basepos is not None and (basepos is not self.curpos): #bruce 050513 optim: use 'is not None' (here and below)
            # (actually this would be a noop if the mol was frozen,
            #  even though basepos is curpos then,
            #  since the transform on pos would be the identity then;
            #  but it seems better to not do it twice, anyway)
            basepos[ind] = self.abs_to_base( pos)
        # But some invals are needed either then, or if the mol is frozen:
        if basepos is not None:
            self.changed_attr('basepos')
        return # from setatomposn
    
    # for __getattr__, validate_attr, invalidate_attr, etc, see InvalMixin
    
    # [bruce 041111 says:]
    # These singlet-list and singlet-array attributes are not worth much trouble,
    # since they are never used in ways that need to be very fast,
    # but we do memoize self.singlets, so that findSinglets et. al. needn't
    # recompute it more than once (per call) or worry whether its order is the
    # same each time they recompute it. (I might or might not memoize singlpos
    # too... for now I do, since it's easy and low-cost to do so, but it's
    # not worth incrementally maintaining it in setatomposn or mol.move/rot
    # as was done before.)
    #
    # I am tempted to depend on self.atoms rather than self.atlist in the
    # recomputation method for self.singlets,
    # so I don't force self.atlist to be recomputed in it.
    # This would require changing the convention for what's invalidated by
    # addatom and delatom (they'd call changed_attr('atoms')). But I am
    # slightly worried that some uses of self.singlets might assume every
    # atom in there has a valid .index (into curpos or basepos), so I won't.
    #
    # Note that it would be illegal to pretend we're dependent on self.atlist
    # in _inputs_for_singlets, but to use self.atoms.values() in this code, since
    # this could lead to self.singlets existing while self.atlist did not,
    # making invals of self.atlist, which see it missing so think they needn't
    # invalidate self.singlets, to be wrong. [##e I should make sure to document
    # this problem in general, since it affects all recompute methods that don't
    # always access (and thus force recompute of) all their declared inputs.]
    # [addendum, 050219: not only that, but self.atoms.values() has indeterminate
    #  order, which for all we know might be different each time it's constructed.]
    _inputs_for_singlets = ['atlist']
    def _recompute_singlets(self):
        # (Filter always returns a python list, even if atlist is a Numeric.array
        # [bruce 041207, by separate experiment]. Some callers test the boolean
        # value we compute for self.singlets. Since the elements are pyobjs,
        # this would probably work even if filter returned an array.)
        return filter( lambda atm: atm.element is Singlet, self.atlist )

    _inputs_for_singlpos = ['singlets','atpos']
    def _recompute_singlpos(self):
        self.atpos
        # we must access self.atpos, since we depend on it in our inval rules
        # (if that's too slow, then anyone invalling atpos must inval this too #e)
        if len(self.singlets):
            # (This was apparently None for no singlets -- always a bug,
            #  and caused bug 237 in Extrude entry. [bruce 041206])
            return A( map( lambda atm: atm.posn(), self.singlets ) )
        else:
            return []
        pass
    
    # These 4 attrs are stored in one tuple, so they can be invalidated
    # quickly as a group.
    
    def _get_polyhedron(self):
        return self.poly_eval_evec_axis[0]
    def _get_eval(self):
        return self.poly_eval_evec_axis[1]
    def _get_evec(self):
        return self.poly_eval_evec_axis[2]
    def _get_axis(self):
        return self.poly_eval_evec_axis[3]

    _inputs_for_poly_eval_evec_axis = ['basepos']
    def _recompute_poly_eval_evec_axis(self):
        return shakedown_poly_eval_evec_axis( self.basepos)

    def full_inval_and_update(self): # bruce 041112-17
        """Public method (but should not usually be needed):
        invalidate and then recompute everything about a mol.
        Some old callers of shakedown might need to call this now,
        if there are bugs in the inval/update system for mols.
        And extrude calls it since it uses the deprecated method
        set_basecenter_and_quat.
        """
        # full inval:
        self.havelist = 0
        self.haveradii = 0
        self.invalidate_attrs(['atlist','externs']) # invalidates everything, I think
        assert not self.valid_attrs(), "full_inval_and_update forgot to invalidate something: %r" % self.valid_attrs()
        # full update (but invals bonds):
        self.atpos # this invals all internal bonds (since it revises basecenter); we depend on that
        # self.atpos also recomputes some other things, but not the following -- do them all:
        self.bbox
        self.singlpos
        self.externs
        self.axis
        self.get_sel_radii_squared()
        assert not self.invalid_attrs(), "full_inval_and_update forgot to update something: %r" % self.invalid_attrs()
        return

    # Primitive modifier methods will (more or less by convention)
    # invalidate atlist if they add or remove atoms (or singlets),
    # and atpos if they move existing atoms (or singlets).
    #
    # (We will not bother to have them check whether they
    # are working with singlets, and if not, avoid invalidating
    # variables related to singlets. To add this, we would modify
    # the rules here so that invalidating atlist did not automatically
    # invalidate singlets (the list), etc... doing this right would
    # require a bit of thought, but is easy enough if we need it...
    # note that it would require checking elements when atoms are transmuted,
    # as well as checks for singlets in addatom/delatom/setatomposn.)

    _inputs_for_atlist = [] # only invalidated directly, by addatom/delatom
    _inputs_for_atpos = ['atlist'] # also incrementally modified by setatomposn
        # (Atpos could be invalidated directly, but maybe it never is (not sure);
        #  anyway we don't optim for that.)
    _inputs_for_basepos = ['atpos'] # also invalidated directly, but not often
    
    def _recompute_atpos(self):
        """Common recompute routine for atlist, atpos, basepos. In theory, any
        suffix of [atlist, atpos, basepos] can be invalid, and we could optim
        by recomputing only the invalid ones. In practice, we don't bother, but
        just remake them all whenever someone asks for one. This might be too
        slow if basepos had separate invals. [As of 041117 there is no known
        separate inval of basepos but not atpos, and the only known inval of
        atpos but not atlist is in molecule.unfreeze, which can be ignored.]
           We set atlist to the list of all real atoms (including singlets),
        and atpos to an array of their positions (in the same order).
        We also replace curpos with atpos (whenever both exist, they are
        refs to the same mutable array objects; curpos always exists).
           The order of the elements of atlist, atpos, curpos, and basepos is
        the same, and is arbitrary but important, since we also set each atom's
        .index attribute to its position in these arrays, and we make each atom
        forget its position, instead relying on atm.molecule.curpos[atm.index].
           We set basepos to a copy of atpos transformed into mol-relative coords
        defined by basecenter and quat, which we reset arbitrarily to make that
        convenient. (Other routines can later modify that coordinate system and
        leave either atpos or basepos fixed, as they desire, changing the other
        to match. If they change atpos they must again set curpos to it. They
        must call changed_attr on whichever of basepos or atpos they change,
        and if that's atpos, they should tell it not to invalidate basepos.)
           (Bad feature: we have no protection against redefining basecenter or
        quat at a bad time, when someone is trusting that coordinate system to
        remain fixed, e.g. during molecule.draw. Most callers should consider
        that coordinate system to be transient or private.)
        """
        #    Implem notes: assuming basepos was not invalidated directly, then
        # since atlist and atpos were invalid, there must have been new or
        # deleted atoms compared to the current value of curpos, which is legal
        # (and normal), but means we can't just copy curpos to get atpos.
        #    Note that this can be called for molecules with no atoms; in that
        # case the produced arrays can be [] even though those have different
        # types than when there are atoms. Some other code needs special cases
        # when there are no atoms, due to this.
        
        #    Something must have been invalid to call us, so basepos must be
        # invalid. So we needn't call changed_attr on it.
        assert not self.__dict__.has_key('basepos')
        
        # Optional debug code:
        # This might be called if basepos doesn't exist but atpos does.
        # I don't think that can happen, but if it can, I need to know.
        # So find out which of the attrs we recompute already exist:
        ## print "_recompute_atpos on %r" % self
        if self.assy is None:
            if platform.atom_debug:
                # [bruce comment 050702: this happens if you delete the chunk while dragging it by selatom in build mode]
                print_compact_stack("atom_debug: fyi, recompute atpos called on killed mol %r: " % self)
##        for attr in ['atpos', 'atlist', 'average_position', 'basepos']:
##            ## vq = self.validQ(attr)
##            if self.__dict__.has_key(attr):
##                print "fyi: _recompute_atpos sees %r already existing" % attr
        #
        atlist = self.atoms.values()
        self.atlist = array(atlist, PyObject)
        # we let atlist (as opposed to self.atlist) remain a Python list;
        # probably this doesn't matter
        
        atpos = map( lambda atm: atm.posn(), atlist ) # must be in same order
        # note: atm.posn() uses atm.xyz and maybe atm.index and self.curpos,
        # so we could not change those before we finished computing atpos above
        atpos = A(atpos)
        for atm,i in zip(atlist,range(len(atlist))):
            atm.index = i # a.posn() is now incorrect until we store the new curpos!
            # Let's hope there's no exception until curpos is stored!
            # (So we store it ASAP.)
            atm.xyz = 'no'
        self.curpos = atpos # same object; must invalidate or fix atpos when any
                            # position stored in curpos is changed!
        self.atpos = atpos

        assert len(atpos) == len(atlist)

        self._recompute_average_position() # sets self.average_position from self.atpos
        self.basecenter = + self.average_position # not an invalidatable attribute
            # unary '+' prevents mods to basecenter from affecting average_position;
            # it might not be needed (that depends on numarray += semantics).
        # Note: basecenter is arbitrary, but should be somewhere near the atoms...
        if debug_messup_basecenter:
            # ... so this flag lets us try some other value to test that!!
            blorp = messupKey.next()
            self.basecenter += V(blorp,blorp,blorp)
        self.quat = Q(1,0,0,0) # arbitrary, except we assume this in the next line:
        if self.atoms:
            self.basepos = atpos - self.basecenter # set now so we can assume quat is 1
        else:
            self.basepos = []
            # this has wrong type, so requires special code in mol.move etc

        assert len(self.basepos) == len(atlist)
        
        # note: basepos must be a separate array object (except when mol is frozen),
        # but atpos (when defined) and curpos must always be the same object.
        self.changed_basecenter_or_quat_while_atoms_fixed()
            # (that includes self.changed_attr('basepos'), though an assert above
            # says that that would not be needed in this case.)

        # validate the attrs we set, except for the non-invalidatable ones,
        # which are curpos, basecenter, quat.
        self.validate_attrs(['atpos', 'atlist', 'average_position', 'basepos'])
        return # from _recompute_atpos
    
    # aliases, in case someone needs one of the other things we compute:
    _recompute_atlist    = _recompute_atpos
    _recompute_basepos   = _recompute_atpos
    
    def changed_basecenter_or_quat_while_atoms_fixed(self):
        """Private method:
        Call this if you changed_basecenter_or_quat_while_atoms_fixed, after
        recomputing basepos to be correct in the new coords (or perhaps after
        invalidating basepos -- that use is unanalyzed and untried). This method
        invals other things which depend on the local coordinate system -- the
        internal bonds and havelist; and it calls changed_attr('basepos').
        """ 
        self.invalidate_internal_bonds()
        self.changed_attr('basepos')
        self.havelist = 0
    
    def invalidate_internal_bonds(self):
        self.invalidate_all_bonds() # easiest to just do this

    def invalidate_all_bonds(self): #bruce 050516 optimized this
        global _inval_all_bonds_counter
        _inval_all_bonds_counter += 1
            # it's good that values of this global are not used on more than one chunk,
            # since that way there's no need to worry about whether the bond
            # inval/update code, which should be the only code to look at this counter,
            # needs to worry that its data looks right but is for the wrong chunks.
        self.bond_inval_count = _inval_all_bonds_counter
        return
##        # TOO SLOW for an inval routine; should just incr a version counter
##        for atm in self.atoms.itervalues(): #bruce 050513 use itervalues
##            for bon in atm.bonds:
##                bon.setup_invalidate()
    
    _inputs_for_average_position = ['atpos']
    def _recompute_average_position(self):
        """Average position of the atoms (including singlets); store it,
        so _recompute_atpos can also call it since it needs the same value;
        not sure if it's useful to have a separate recompute method
        for this attribute; but probably yes, so it can run after incremental
        mods to atpos.
        """
        if self.atoms:
            self.average_position = add.reduce(self.atpos)/len(self.atoms)
        else:
            self.atpos # recompute methods must always use all their inputs
            self.average_position = V(0,0,0)
        return

    _inputs_for_bbox = ['atpos']
    def _recompute_bbox(self):
        "Make a new bounding box from the atom positions (including singlets)."
        self.bbox = BBox(self.atpos)

    # Center.
    
    # if we implement self.user_specified_center as user-settable,
    # it also needs to be moved/rotated with the mol, like a datum point
    # rigidly attached to the mol (or like an atom)
    user_specified_center = None # never changed for now
    
    def _get_center(self):
        # _get_center seems better than _recompute_center since this attr
        # is only needed by the UI and this method is fast
        """Return the center to use for rotations and stretches and perhaps some
        other purposes (user-settable, or the average atom position by default)
        """
        if self.user_specified_center is not None: #bruce 050516 bugfix: 'is not None'
            return self.user_specified_center
        return self.average_position

    # What used to be called self.center, used mainly to relate basepos and curpos,
    # is now called self.basecenter and is not a recomputed attribute,
    # though it is chosen and stored by the _recompute_atpos method.
    # See also a comment about this in molecule.__init__. [bruce 041112]

    # Display list:
    # It's not sensible to integrate the display list into this recompute system,
    # since we normally execute it in OpenGL as a side effect of recomputing it.
    # To invalidate it, we just do this directly as a special case, self.havelist = 0,
    # in the low-level modifiers that need to.
    
    # Externs.
    _inputs_for_externs = [] # only invalidated by hand
    def _recompute_externs(self): #bruce 050513 optimized this
        # following code simplified from self.draw()
        externs = []
        for atm in self.atoms.itervalues():
            for bon in atm.bonds:
                ## if bon.other(atm).molecule != self # slower than needed:
                if bon.atom1.molecule is not self or bon.atom2.molecule is not self:
                    # external bond
                    externs.append(bon)
        return externs
    
    def freeze(self):
        """ set the molecule up for minimization or simulation"""
        # bruce 041112 modified this
        ###e bruce 041104 comment: need to stop movie if atpos is invalidated
        #bruce 050515 comment: recent movie optim includes (I think) del atpos but leaving
        # basepos around; this will cause trouble for anything invalidating atpos; #####@@@@@
        # until it's fixed in general (by redefining or better formalizing "frozen" state),
        # I'll at least fix it in unfreeze, below.
        self.update_curpos() # make sure every atom is in curpos
        self.basecenter = V(0,0,0)
        self.quat = Q(1,0,0,0)
        self.basepos = self.curpos # reference == same object
        self.changed_basecenter_or_quat_while_atoms_fixed()
            # that includes self.changed_attr('basepos'), which in this case
            # might be needed, if recomputing atpos also computed things
            # influenced by basepos (but in the wrong local coord system).

    def unfreeze(self):
        """ to be done at the end of minimization or simulation"""
        # bruce 041112 rewrote this
        self.invalidate_attr('basepos') # bruce 050515 bugfix in recent movie-playing optimization
            # [only needed if atpos missing and basepos there, which is the bug, and which this only partly fixes]
        self.invalidate_attr('atpos') # effectively, do a shakedown
          # (reset basepos, basecenter, and quat to usual values, etc)
        assert not self.__dict__.has_key('basepos') # should be deleted when we inval atpos

    def get_dispdef(self, glpane = None):
        "reveal what dispdef we will use to draw this molecule"
        # copied out of molecule.draw by bruce 041109 for use in extrudeMode.py
        if self.display != diDEFAULT:
            disp = self.display
        else:
            if glpane is None:
                # this possibility added by bruce 041207
                glpane = self.assy.o
            disp = glpane.display
        return disp

    def pushMatrix(self): #bruce 050609 duplicated this from some of self.draw()
        """Do glPushMatrix(), and then trasform from world coords to this chunk's private coords.
        See also self.popMatrix().
        Warning: this is partially inlined in self.draw().
        """
        glPushMatrix()
        origin = self.basecenter
        glTranslatef(origin[0], origin[1], origin[2])
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

    def popMatrix(self): #bruce 050609
        "Undo the effect of self.pushMatrix()."
        glPopMatrix()

    def inval_display_list(self): #bruce 050804
        "This is meant to be called when something whose usage we tracked (while making our display list) next changes."
        self.changeapp(0) # that now tells self.glpane to update, if necessary
        #########@@@@@@@@ glpane needs to track changes anyway due to external bonds....
    
    def draw(self, glpane, dispdef):
        """draw all the atoms, using the atom's, molecule's,
        or GLPane's display mode in that order of preference.
        (Note that our dispdef argument is not used at all.)
        Draw each bond only once, even though internal bonds
        will be referenced from two atoms in this molecule.
        (External bonds are drawn once by each molecule they connect.)
        If the molecule itself is selected, draw its bounding box as a
        wireframe; selected atoms are drawn specially by atom.draw.
        """
        if self.hidden: return
        
        self.glpane = glpane # needed for the edit method - Mark [2004-10-13]
        ##e bruce 041109: can't we figure it out from mol.dad?
        # (in getattr or in a special method)
        #bruce 050804: this is now also used in self.changeapp(),
        # since it's faster than self.track_change (whose features are overkill for this),
        # though the fact that only one glpane can be recorded in self
        # is a limitation we'll need to remove at some point.

        #Tried to fix some bugs by Huaicai 09/30/04
        if len(self.atoms) == 0:
            return
            # do nothing for a molecule without any atoms

        self.basepos
        # make sure basepos is up-to-date, so basecenter is not changed
        # during the redraw. #e Ideally we'd have a way to detect or
        # prevent further changes to it during redraw, but this is not
        # needed for now since they should not be possible, and should
        # cause visible bugs if they happen. At least let's verify
        # the mol coord system has not changed by the time we're done:
        should_not_change = ( + self.basecenter, + self.quat )

        #bruce 050804:
        # tell whatever is now drawing our display list
        # (presumably our arg, glpane, but we don't assume this right here)
        # how to find out when our display list next becomes invalid,
        # so it can know it needs to redraw us.
        # (This is probably not actually needed at the moment,
        #  due to a special system used by self.changeapp() in place of self.track_change(),
        #  but it should be harmless.)
        self.track_use()
        
        # put it in its place
        glPushMatrix()

        try: #bruce 041119: do our glPopMatrix no matter what
            # (note: as of 050609, this is an inlined version of part of self.pushMatrix())
            origin = self.basecenter
            glTranslatef(origin[0], origin[1], origin[2])
            q = self.quat
            glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

            if self.picked:
                try:
                    drawlinelist(PickedColor,self.polyhedron or [])
                except:
                    # bruce 041119 debug code;
                    # also "or []" failsafe (above)
                    # in case recompute exception makes it None
                    print_compact_traceback("exception in drawlinelist: ")
                    print "(self.polyhedron is %r)" % self.polyhedron

            disp = self.get_dispdef(glpane) #bruce 041109 split into separate method
            # disp is passed to two methods below... but if we use a cached display
            # list, it's not reflected in that, and we don't check for this here
            # [interjection, much later, 050415 -- now we do check for it];
            # this would cause bugs in redrawing after changing the glpane's display
            # mode, except that doing that calls changeapp() on the required mols,
            # so it's ok in theory. [comment by bruce 041109/041123]

            # cache molecule display as GL list
            
            # [bruce 050415 changed value of self.havelist when it's not 0,
            #  from 1 to (disp,),
            #  to fix bug 452 item 15 (no havelist inval for non-current parts
            #  when global default display mode is changed); this will incidentally
            #  optimize some related behaviors by avoiding some needless havelist invals,
            #  now that we've also removed the now-unneeded changeapp of all mols upon
            #  global dispdef change (in GLPane.setDisplay).]
            # [bruce 050419 also including something for element radius and color prefs,
            #  to fix bugs in updating display when those change (eg bug 452 items 12-A, 12-B).]

            eltprefs = PeriodicTable.color_change_counter, PeriodicTable.rvdw_change_counter
            if self.havelist == (disp, eltprefs): # value must agree with set of havelist, below
                glCallList(self.displist)
            else:
                self.havelist = 0 #bruce 050415; maybe not needed, but seems safer this way
                match_checking_code = self.begin_tracking_usage()
                glNewList(self.displist, GL_COMPILE_AND_EXECUTE)

                # bruce 041028 -- protect against exceptions while making display
                # list, or OpenGL will be left in an unusable state (due to the lack
                # of a matching glEndList) in which any subsequent glNewList is an
                # invalid operation. (Also done in shape.py; not needed in drawer.py.)
                try:
                    self.draw_displist(glpane, disp) # also recomputes self.externs [not anymore -- bruce 050513]
                except:
                    print_compact_traceback("exception in molecule.draw_displist ignored: ")
                    # it might have left the externs incomplete # bruce 041105 night [not anymore -- bruce 050513]
                    ## self.invalidate_attr('externs')
                glEndList()
                self.end_tracking_usage( match_checking_code, self.inval_display_list )
                # This is the only place where havelist is set to anything true;
                # the value it's set to must match the value it's compared with, above.
                # [bruce 050415 revised what it's set to/compared with; details above]
                self.havelist = (disp, eltprefs)
                assert self.havelist, "bug: havelist must be set to a true value here, not %r" % (self.havelist,)
                # always set the self.havelist flag, even if exception happened,
                # so it doesn't keep happening with every redraw of this molecule.
                #e (in future it might be safer to remake the display list to contain
                # only a known-safe thing, like a bbox and an indicator of the bug.)
            assert `should_not_change` == `( + self.basecenter, + self.quat )`, \
                "%r != %r, what's up?" % (should_not_change , ( + self.basecenter, + self.quat))
                # (we use `x` == `y` since x == y doesn't work well for these data types)

#bruce 050610 zapping this, for testing (maybe permanently now that selobj highlighting is useable for this -- once it works ok)####@@@@
##            # redraw selatom, if it's ours (over the same atom, drawn in the usual way)
##            # (this keeps it from affecting the display list, so depositMode.bareMotion
##            #  can change selatom without havelist=0, for a large speedup [bruce 041206])
##            selatom = glpane.selatom
##            if selatom is not None and selatom.molecule is self:
##                try:
##                    color = self._colorfunc(selatom)
##                except: # no such attr [should not happen after 050524], or it's None [usual case], or it has a bug
##                    color = self.color
##                level = self.assy.drawLevel #e or always use best level??
##                selatom.draw_as_selatom(glpane, disp, color, level)
##                    # (fyi, this doesn't use color arg as of 041206)
            pass

            if self.hotspot is not None: # note, as of 050217 that can have side effects in getattr
                if 1: #bruce 050316 always do this; was "if platform.atom_debug:"
                    self.overdraw_hotspot(glpane, disp) # only does anything for pastables as of 050316 (toplevel clipboard items)

        except:
            print_compact_traceback("exception in molecule.draw, continuing: ")
            
        glPopMatrix()

        # Could we return now if display mode "disp" never draws bonds?
        # No -- individual atoms might override that display mode.
        # Someday we might decide to record whether that's true when recomputing externs,
        # and to invalidate it as needed -- since it's rare for atoms to override display modes.
        # Or we might even keep a list of all our atoms which override our display mode. ###e
        # [bruce 050513 comment]
        drawLevel = self.assy.drawLevel
        bondcolor = self.color
        for bon in self.externs:
            bon.draw(glpane, disp, bondcolor, drawLevel)
        return # from molecule.draw()

    def draw_displist(self, glpane, disp): #bruce 050513 optimizing this somewhat

        drawLevel = self.assy.drawLevel
        drawn = {}
        ## self.externs = [] # bruce 050513 removing this
        # bruce 041014 hack for extrude -- use _colorfunc if present [part 1; optimized 050513]
        _colorfunc = self._colorfunc # might be None [as of 050524 we supply a default so it's always there]
        color = self.color # only used if _colorfunc is None
        bondcolor = self.color # never changed
        
        for atm in self.atoms.itervalues(): #bruce 050513 using itervalues here (probably safe, speed is needed)
            try:
                # bruce 041014 hack for extrude -- use _colorfunc if present [part 2; optimized 050513]
                if _colorfunc is not None:
                    try:
                        color = _colorfunc(atm)
                    except: # _colorfunc has a bug; reporting this would be too verbose, sorry #e could report for only 1st atom?
                        color = self.color
                # otherwise color is still set from above
                
                # end bruce hack 041014, except for use of color rather than
                # self.color in atm.draw (but not in bon.draw -- good??)
                atomdisp = atm.draw(glpane, disp, color, drawLevel)
                #bruce 050513 optim: if self and atm display modes don't need to draw bonds,
                # we can skip drawing bonds here without checking whether their other atoms
                # have their own display modes and want to draw them,
                # since we'll notice that when we get to those other atoms
                # (whether in self or some other chunk).
                # (We could ask atm.draw to return a flag saying whether to draw its bonds here.)
                #    To make this safe, we'd need to not recompute externs here,
                # but that should be ok since they're computed separately anyway now.
                # So I'm removing that now, and doing this optim.
                ###e (I might need to specialcase it for singlets so their bond-valence number is still drawn...)
                # [bruce 050513]
                if atomdisp in (diCPK, diLINES, diTUBES): #e should we move this tuple into bonds module or Bond class?
                    for bon in atm.bonds:
                        if bon.key not in drawn:
                            ## if bon.other(atm).molecule != self: could be faster [bruce 050513]:
                            if bon.atom1.molecule is not self or bon.atom2.molecule is not self:
                                pass ## self.externs.append(bon) # bruce 050513 removing this
                            else:
                                # internal bond, not yet drawn
                                drawn[bon.key] = bon
                                bon.draw(glpane, disp, bondcolor, drawLevel)
            except:
                # [bruce 041028 general workaround to make bugs less severe]
                # exception in drawing one atom. Ignore it and try to draw the
                # other atoms. #e In future, draw a bug-symbol in its place.
                print_compact_traceback("exception in drawing one atom or bond ignored: ")
                # (this might mean some externs are missing; never mind that for now.) [bruce 050513 -- not anymore]
                try:
                    print "current atom was:",atm
                except:
                    print "current atom was... exception when printing it, discarded"
                try:
                    atom_source = atm._source # optional atom-specific debug info
                except AttributeError:
                    pass
                else:
                    print "Source of current atom:", atom_source
        return # from molecule.draw_displist()

    def overdraw_hotspot(self, glpane, disp): # bruce 050131 (atom_debug only); [unknown later date] now always active
        """
        If this chunk is a (toplevel) clipboard item with a hotspot
        (i.e. if pasting it onto a bond will work and use its hotspot),
        display its hotspot in a special form.
        As with selatom, we do this outside of the display list.        
        # bruce 050416 warning: the conditions here need to match those in depositMode's
        # methods for mentioning hotspot in statusbar, and for deciding whether a clipboard
        # item is pastable. All this duplicated hardcoded conditioning is bad; needs cleanup. #e
        """
        try:
            # if any of this fails (which is normal), it means don't use this feature for self.
            # We need these checks because some code removes singlets from a chunk (by move or kill)
            # without checking whether they are that chunk's hotspot.
            hs = self.hotspot
            assert hs is not None and hs.is_singlet() and hs.key in self.atoms
##            if hs is glpane.selatom and platform.atom_debug:
##                print "atom_debug: fyi: hs is glpane.selatom"
# will removing this assert fix bug 703 and not cause trouble? bruce 050614 guess -- seems to work.
# All selatom code still needs review and cleanup, though, now that it comes from selobj. ####@@@@
##            assert hs is not glpane.selatom
            assert self in self.assy.shelf.members
        except:
            pass
        else:
            try:
##                from debug_prefs import debug_pref, ColorType #bruce 050614 experimental code, will be revised/renamed
##                color = debug_pref("hotspot color", ColorType(green))
                color = env.prefs[atomHotspotColor_prefs_key] #bruce 050808
                
                level = self.assy.drawLevel #e or always use best level??
                ## code copied from selatom.draw_as_selatom(glpane, disp, color, level)
                pos1 = hs.baseposn()
                drawrad1 = hs.selatom_radius(disp)
                drawsphere(color, pos1, drawrad1, level) # always draw, regardless of disp
            except:
                if 1 or platform.atom_debug: ###@@@ decide which
                    print_compact_traceback("atom_debug: ignoring exception in overdraw_hotspot %r, %r: " % (self,hs))
                pass
            pass
        pass

    def readmmp_info_chunk_setitem( self, key, val, interp ): #bruce 050217, renamed 050421
        """This is called when reading an mmp file, for each "info chunk" record.
        Key is a list of words, val a string; the entire record format
        is presently [050217] "info chunk <key> = <val>".
        Interp is an object to help us translate references in <val>
        into other objects read from the same mmp file or referred to by it.
        See the calls of this method from files_mmp for the doc of interp methods.
           If key is recognized, set the attribute or property
        it refers to to val; otherwise do nothing.
           (An unrecognized key, even if longer than any recognized key,
        is not an error. Someday it would be ok to warn about an mmp file
        containing unrecognized info records or keys, but not too verbosely
        (at most once per file per type of info).)
        """
        if key == ['hotspot']:
            # val should be a string containing an atom number referring to
            # the hotspot to be set for this chunk (which is being read from an mmp file)
            (hs_num,) = val.split()
            hs = interp.atom(hs_num)
            self.set_hotspot(hs) # this assertfails if hotspot is invalid [#k does caller handle that? ####@@@@]
        elif key == ['color']: #bruce 050505
            # val should be 3 decimal ints from 0-255; colors of None are not saved since they're the default
            r,g,b = map(int, val.split())
            color = r/255.0, g/255.0, b/255.0
            self.setcolor(color)
        else:
            if platform.atom_debug:
                print "atom_debug: fyi: info chunk with unrecognized key %r" % (key,)
        return

    def atoms_in_mmp_file_order(self): #bruce 050228
        """Return a list of our atoms, in the same order as they would be written to an mmp file
        (which is the same order in which they occurred in one, *if* they were just read from one).
        We know it's the same order as they'd be written, since self.writemmp() calls this method.
        We know it's the same order they were just read in (if they were just read), since it's
        the order of atom.key, which is assigned successive values (guaranteed to sort in order)
        as atoms are read from the file and created for use in this session.
        """
        pairs = self.atoms.items() # key, val pairs; keys are atom.key,
            # which is an int which counts from 1 as atoms are created in one session,
            # and which is (as of now, 050228) specified to sort in order of creation
            # even if we later change the kind of value it produces.
        pairs.sort()
        res = [atm for key, atm in pairs]
        return res
    
    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        "[overrides Node.writemmp]"
        disp = mapping.dispname(self.display)
        mapping.write("mol (" + mapping.encode_name(self.name) + ") " + disp + "\n")
        self.writemmp_info_leaf(mapping)
        #bruce 050228: write atoms in the same order they were created in,
        # so as to preserve atom order when an mmp file is read and written
        # with no atoms created or destroyed and no chunks reordered, thus
        # making previously-saved movies more likely to retain their validity.
        for atm in self.atoms_in_mmp_file_order():
            atm.writemmp(mapping)
        #bruce 050217 new feature [see also a comment added to files_mmp.py]:
        # also write the hotspot, if there is one.
        hs = self.hotspot # uses getattr to validate it
        if hs:
            # hs is a valid hotspot in this chunk, and was therefore one of the
            # atoms just written above, and therefore should have an encoding
            # already assigned for the current mmp file:
            hs_num = mapping.encode_atom(hs)
            assert hs_num is not None
            mapping.write("info chunk hotspot = %s\n" % hs_num)
        if self.color:
            r = int(self.color[0]*255 + 0.5)
            g = int(self.color[1]*255 + 0.5)
            b = int(self.color[2]*255 + 0.5)
            mapping.write("info chunk color = %d %d %d\n" % (r,g,b))
        return

    # write to a povray file:  draw the atoms and bonds inside a molecule
    def writepov(self, file, disp):
        if self.hidden: return

        if self.display != diDEFAULT: disp = self.display

        drawn = {}
        for atm in self.atoms.values():
            atm.writepov(file, disp, self.color)
            for bon in atm.bonds:
                if bon.key not in drawn:
                    drawn[bon.key] = bon
                    bon.writepov(file, disp, self.color)

    def writemdl(self, alist, f, disp):
        if self.display != diDEFAULT: disp = self.display
        if self.hidden or disp == diINVISIBLE: return
        col = self.color
#        print "chunk: disp =", disp,", color =", self.color
        for a in self.atoms.values(): 
            a.writemdl(alist, f, disp, self.color)
            
    def move(self, offset):
        """Public method: translate self (a molecule) by offset;
        do all necessary invalidations, but optimize those based on the
        molecule's relative structure not having changed or reoriented.
        """
        # code and doc rewritten by bruce 041109.
        # The method is public but its implem is pretty private!
        
        # First make sure self.basepos is up to date! Otherwise
        # self.changed_basecenter_or_quat_to_move_atoms() might not be able to reconstruct it.
        # I don't think this should affect self.bbox, but in case I'm wrong,
        # do this before looking at bbox.
        self.basepos

        # Now, update bbox iff it's already present.
        if self.__dict__.has_key('bbox'):
            # bbox already present -- moving it is faster than recomputing it
            #e (though it might be faster to just delete it, if many moves
            #   will happen before we need it again)
            self.bbox.data += offset

        # Now, do the move. Note that this might destructively modify the object
        # self.basecenter rather than replacing it with a new one.
        self.basecenter += offset
        
        # (note that if we did "self.bbox.data += off" at this point, and
        # self.bbox was not present, it might be recomputed from inconsistent
        # data (depending on details of _recompute_bbox) and then moved;
        # so don't do it here!)

        # Do all necessary invalidations and/or recomputations (except for bbox),
        # treating basepos as definitive and recomputing curpos from it.
        self.changed_basecenter_or_quat_to_move_atoms()
	
    def pivot(self, point, q):
        """Public method: pivot the molecule around point by quaternion q;
        do all necessary invalidations, but optimize those based on the
        molecule's relative structure not having changed. See also self.rot().
        """
        # First make sure self.basepos is up to date! Otherwise
        # self.changed_basecenter_or_quat_to_move_atoms() might not be able to reconstruct it.
        self.basepos

        # Do the motion (might destructively modify basecenter and quat objects)
        r = point - self.basecenter
        self.basecenter += r - q.rot(r)
        self.quat += q
        
        # No good way to rotate a bbox, so just invalidate it.
        self.invalidate_attr('bbox')
        
        # Do all necessary invalidations and/or recomputations (except bbox),
        # treating basepos as definitive and recomputing curpos from it.
        self.changed_basecenter_or_quat_to_move_atoms()

    def rot(self, q):
        """Public method: rotate the molecule around its center by quaternion q;
        do all necessary invalidations, but optimize those based on the
        molecule's relative structure not having changed. See also self.pivot().
        """
        # bruce 041109: the center of rotation is not always self.basecenter,
        # so in general we need to pivot around self.center.
        self.pivot(self.center, q) # not basecenter!
        return
    
    def stretch(self, factor, point = None):
        """Public method: expand the molecule by the given factor
        (keeping point fixed, by default its center).
        Do all necessary invalidations, optimized as convenient
        given the nature of this operation.
        """
        self.basepos # make sure it's up to date
            # (this might recompute basepos using __getattr__; probably not
            #  needed since the += below would do it too, but let's be safe --
            #  no harm since it won't be done twice)
        if point is None: #bruce 050516 bugfix (was "if not point")
            point = self.center # not basecenter!
        factor = float(factor)
        
        #bruce 041119 bugfix in following test of array having elements --
        # use len(), since A([[0.0,0.0,0.0]]) is false!
        if not len(self.basepos):
            # we need this 0 atoms case (though it probably never occurs)
            # since the remaining code won't work for it,
            # since self.basepos has the wrong type then (in fact it's []);
            # note that no changes or invals are needed
            return
        
        # without moving mol in space, change self.basecenter to point
        # and change self.basepos to match:
        self.basepos += (self.basecenter - point)
        self.basecenter = point
            # i.e. self.basecenter = self.basecenter - self.basecenter + point,
            # or self.basecenter -= (self.basecenter - point)
        
        # stretch the mol around the new self.basecenter
        self.basepos *= factor
        # (the above += and *= might destructively modify basepos -- I'm not sure)

        # do the necessary recomputes from new definitive basepos,
        # and invals (incl. bbox, internal bonds)
        self.changed_basepos_basecenter_or_quat_to_move_atoms()

    def changed_basepos_basecenter_or_quat_to_move_atoms(self):
        "(private method) like changed_basecenter_or_quat_to_move_atoms but we also might have changed basepos"
        # Do the needed invals, and recomputation of curpos from basepos
        # (I'm not sure if the order would need review if we revise inval rules):
        self.havelist = 0
            # (not needed for mov or rot, so not done by changed_basecenter_or_quat_to_move_atoms)
        self.changed_attr('basepos') # invalidate whatever depends on basepos ...
        self.invalidate_internal_bonds() # ... including the internal bonds, handled separately
        self.invalidate_attr('bbox') # since not handled by following routine
        self.changed_basecenter_or_quat_to_move_atoms()
            # (misnamed -- in this case we changed basepos too)

    def changed_basecenter_or_quat_to_move_atoms(self): #bruce 041104-041112
        """Private method:
        Call this whenever you have just changed self.basecenter and/or self.quat
        (and/or self.basepos if you call changed_attr on it yourself), and
        you want to move the molecule by changing curpos to match, assuming that
        basepos is still correct in the new local coords basecenter and quat.
           Note that basepos must already exist, since this method can't recompute
        it from curpos in the standard way, since curpos is wrong and basepos is
        correct (not a legal state except within the callers of this method).
           Also do the proper invalidations and/or incremental recomputations,
        except for self.bbox, which the caller must fix or invalidate (either
        before or after calling us). Our invalidations assume that only basecenter
        and/or quat were changed; some callers (which modify basepos) must do
        additional invalidations.
           See also changed_basecenter_or_quat_while_atoms_fixed, quite different.
        """
        assert self.__dict__.has_key('basepos'), \
               "internal error in changed_basecenter_or_quat_to_move_atoms for %r" % (self,)
        
        if not len(self.basepos): #bruce 041119 bugfix -- use len()
            # we need this 0 atoms case (though it probably never occurs)
            # since the remaining code won't work for it,
            # since self.basepos has the wrong type then (in fact it's []);
            # note that no changes or invals are needed for 0 atoms.
            return

        # imitate the recomputes done by _recompute_atpos
        self.curpos = self.basecenter + self.quat.rot(self.basepos) # inlines base_to_abs
        self.atpos = self.curpos
        # no change in atlist; no change needed in our atoms' .index attributes
        # no change here in basepos or bbox (if caller changed them, it should
        # call changed_attr itself, or it should invalidate bbox itself);
        # but changes here in whatever depends on atpos, aside from those.
        self.changed_attr('atpos', skip = ('bbox','basepos'))
        
        # we've moved one end of each external bond, so invalidate them...
        # [bruce 050516 comment (95% sure it's right): note that we don't, and need not, inval internal bonds]
        for bon in self.externs:
            bon.setup_invalidate()
        return

    def base_to_abs(self, anything): # bruce 041115
        """map anything (which is accepted by quat.rot() and numarray.__add__)
        from molecule-relative coords to absolute coords;
        guaranteed to never recompute basepos/atpos or modify the mol-relative
        coordinate system it uses. Inverse of abs_to_base.
        """
        return self.basecenter + self.quat.rot( anything)

    def abs_to_base(self, anything): # bruce 041201
        """map anything (which is accepted by quat.unrot() and
        numarray.__sub__ (#k??)) from absolute coords to mol-relative coords;
        guaranteed to never recompute basepos/atpos or modify the mol-relative
        coordinate system it uses. Inverse of base_to_abs.
        """
        return self.quat.unrot( anything - self.basecenter)

    def set_basecenter_and_quat(self, basecenter, quat):
        """Deprecated public method: change this molecule's basecenter and quat to the specified values,
        as a way of moving the molecule's atoms.
        It's deprecated since basecenter and quat are replaced by in-principle-arbitrary values
        every time certain recomputations are done, but this method is only useful if the caller
        knows what they are, and computes the new ones it wants relative to what they are.
        So it's much better to use mol.pivot instead (or some combo of move, rot, and pivot).
        #"""
        # [written by bruce for extrude; moved into class molecule by bruce 041104]
        # modified from mol.move and mol.rot as of 041015 night
        self.basepos # bruce 050315 bugfix: recompute this if it's currently invalid!
        # make sure mol owns its new basecenter and quat,
        # since it might destructively modify them later!
        self.basecenter = V(0,0,0) + basecenter
        self.quat = Q(1,0,0,0) + quat #e +quat might be correct and faster... don't know; doesn't matter much
        try: del self.bbox #e could optimize if quat is not changing
        except: pass
        self.changed_basecenter_or_quat_to_move_atoms()

    def getaxis(self):
        return self.quat.rot(self.axis)

    def setcolor(self, color):
        """change the molecule's color;
        new color should be None (let atom colors use their element colors)
        or a 3-tuple.
        """
        # None or a 3-tuple; it matters that the 3-tuple is never boolean False,
        # so don't use a Numeric array! As a precaution, let's enforce this now. [bruce 050505]
        if color is not None:
            r,g,b = color
            color = r,g,b
        self.color = color
            # warning: some callers (ChunkProp.py) first trash self.color, then call us to bless it. [bruce 050505 comment]
        self.havelist = 0
        self.changed() #[bruce 050505]

    def setDisplay(self, disp):
        "change the molecule's display mode"
        self.display = disp
        self.havelist = 0
        self.haveradii = 0
        self.changed() # [bruce 050505 revised this]

    def show_invisible_atoms(self):
        """Resets the display mode for each invisible (diINVISIBLE) atom 
        to diDEFAULT display mode, rendering them visible again.
        It returns the number of invisible atoms found.
        """
        n = 0
        for a in self.atoms.itervalues():
            if a.display == diINVISIBLE: 
                a.setDisplay(diDEFAULT)
                n += 1
        return n

    def set_atoms_display(self, display):
        """Changes the display setting to 'display' for all atoms in this chunk.
        It returns the number of atoms which had their display mode changed.
        """
        n = 0
        for a in self.atoms.itervalues():
                if a.display != display:
                    a.setDisplay(display)
                    n += 1
        return n

    glpane = None #bruce 050804
            
    def changeapp(self, atoms):
        """call when you've changed appearance of the molecule
        (but you don't need to call it if only the external bonds look different).
        Arg atoms = 1 means that not only the entire mol appearance,
        but specifically the set of atoms or atomic radii
        (for purposes of selection), have changed.
           Note that changeapp does not itself call self.assy.changed(),
        since that is not always correct to do (e.g., selecting an atom
        should call changeapp(), but not assy.changed(), on its molecule).
        """ 
        self.havelist = 0
        if atoms: #bruce 041207 added this arg and its effect
            self.haveradii = 0 # invalidate self.sel_radii_squared
            # (using self.invalidate_attr would be too slow)
        #bruce 050804 new feature (related to graphics prefs updating, probably more generally useful):
        glpane = self.glpane # the last glpane that drew this chunk, or None if it was never drawn ###IMPLEM
            # (if more than one can ever draw it at once, this code needs to be revised to scan them all ##k)
        if glpane is not None:
            try:
                flag = glpane.wants_gl_update
            except AttributeError:
                pass # this will happen for ThumbViews
                     # until they are fixed to use this system so they get updated when graphics prefs change
            else:
                if flag:
                    glpane.wants_gl_update_was_True() # sets it False and does gl_update
            pass
        return
        
    def getinfo(self):
        # Return information about the selected moledule for the msgbar [mark 2004-10-14]
        
        if self is self.assy.ppm: return
        
        ele2Num = {}
        
        # Determine the number of element types in this molecule.
        for a in self.atoms.values():
            if not ele2Num.has_key(a.element.symbol): ele2Num[a.element.symbol] = 1 # New element found
            else: ele2Num[a.element.symbol] += 1 # Increment element
            
        # String construction for each element to be displayed.
        natoms = len(self.atoms) # number of atoms in the chunk
        nsinglets = 0
        einfo = ""
     
        for item in ele2Num.iteritems():
            if item[0] == "X":  # It is a Singlet
                nsinglets = int(item[1])
                continue
            else: eleStr = "[" + item[0] + ": " + str(item[1]) + "] "
            einfo += eleStr
            
        if nsinglets: # Add singlet info to end of info string
            #bruce 041227 changed term "Singlets" to "Open bonds"
            eleStr = "[Open bonds: " + str(nsinglets) + "]"
            einfo += eleStr
         
        natoms -= nsinglets   # The real number of atoms in this chunk

        minfo =  "Chunk Name: [" + str (self.name) + "]     Total Atoms: " + str(natoms) + " " + einfo
        
        # ppm is self for next mol picked.
        self.assy.ppm = self
                        
        return minfo

    def getstatistics(self, stats):
        """Adds the current chunk, including number of atoms 
        and singlets to part stats.
        """
        stats.nchunks += 1
        stats.natoms += len(self.atoms)
        for a in self.atoms.itervalues():
            if a.element.symbol == "X": stats.nsinglets +=1
 
    def pick(self):
        """select the molecule.
        """
        if not self.picked:
            self.assy.permit_pick_parts() #bruce 050125 added this... hope it's ok! ###k ###@@@
                # (might not be needed for other kinds of leaf nodes... not sure. [bruce 050131])
            Node.pick(self)
            #bruce 050308 comment: Node.pick has ensured that we're in the current selection group,
            # so it's correct to append to selmols, *unless* we recompute it now and get a version
            # which already contains self. So, we'll maintain it iff it already exists.
            # I'll write this code to run even if my other assy/part changes aren't committed yet.
            # This needs a later re-review! same with unpick #####@@@@@
            try:
                import part # see if the code that defines this was committed yet
            except:
                # that code wasn't committed yet
                self.assy.selmols.append(self)
            else:
                # let the Part figure out how best to do this
                ## self.assy.part.selmols_append(self) ## WRONG
                if self.part:
                    self.part.selmols_append(self)
            # bruce 041207 thinks self.havelist = 0 is no longer needed here,
            # since self.draw uses self.picked outside of its display list,
            # so I'm removing that! This might speed up some things.
            ## self.havelist = 0
            # bruce 041227 moved history message from here to one caller, pick_at_event

    def unpick(self):
        """unselect the molecule.
        """
        if self.picked:
            Node.unpick(self)
            # bruce 050308 comment: following probably needs no change for assy/part.
            # But we'll let the Part do it, so it needn't remake selmols if not made.
            # But in case the code for assy.part is not yet committed, check that first:
            try:
                import part # see comments in pick method
            except:
                if self in self.assy.selmols:
                    self.assy.selmols.remove(self)
            else:
                ## self.assy.part.selmols_remove(self) ## WRONG
                if self.part:
                    self.part.selmols_remove(self)
            # bruce 041207 thinks self.havelist = 0 is no longer needed here
            # (see comment in self.pick).
            ## self.havelist = 0

    def kill(self):
        """(Public method)
        Kill a molecule: unpick it, break its external bonds, kill its atoms
        (which should kill any jigs attached only to this mol),
        remove it from its group (if any) and from its assembly (if any);
        make it forget its group and assembly.
        It's legal to kill a mol twice, and common now that emptying a mol
        of all atoms kills it automatically; redundant kills have no effect.
        It's probably legal to reuse a killed mol (if it's added to a new
        assy -- there's no method for this), but this has never been tested.
        """
        ## print "fyi debug: mol.kill on %r" % self
        # Bruce 041116 revised docstring, made redundant kills noticed
        # and fully legal, and made kill forget about dad and assy.
        # Note that _nullMol might be killed every so often.
        # (caller no longer needs to set externs to [] when there are no atoms)
        if self is _nullMol:
            return
        # all the following must be ok for an already-killed molecule!
        self.unpick() #bruce 050214 comment: keep doing this here even though Node.kill now does it too
        for b in self.externs[:]: #bruce 050214 copy list as a precaution
            b.bust()
        self.externs = [] #bruce 041029 precaution against repeated kills
        
        #10/28/04, delete all atoms, so jigs attached can be deleted when no atoms
        #  attaching the jig . Huaicai
        for a in self.atoms.values():
            a.kill()
            # this will recursively kill this chunk! Should be ok,
            # though I ought to rewrite it so that if that does happen here,
            # I don't redo everything and have to worry whether that's safe.
            # [bruce 050214 comment] 
            # [this would also serve to bust the extern bonds, but it seems safer
            #  to do that explicitly and to do it first -- bruce 041109 comment]
        #bruce 041029 precautions:
        if self.atoms:
            print "fyi: bug (ignored): %r mol.kill retains killed atoms %r" % (self,self.atoms)
        self.atoms = {}
        self.invalidate_attr('atlist') # probably not needed; covers atpos
            # and basepos too, due to rules; externs were correctly set to []
        if self.assy:
            # bruce 050308 for assy/part split:
            # do this differently if Node.part code has been committed
            try:
                self.part
            except AttributeError:
                # use pre-050308 code:
                # remove from assy.molecules, if necessary
                try:
                    self.assy.molecules.remove(self)
                    self.assy.changed()
                    #bruce 050206: this should not be reached if we were in the clipboard!
                    # (since there should be an exception from not being in assy.molecules.)
                    # so if we reached it, "safely assert" we were not.
                    if platform.atom_debug and self.in_clipboard():
                        print "atom_debug: bug: killed mol was in clipboard but also in assy.molecules:", self
                except ValueError:
                    #bruce 050206: this might be legal, e.g. if we're in the clipboard.
                    # But it might be important to warn about, if we're not.
                    if platform.atom_debug and not self.in_clipboard():
                        print "atom_debug: possible bug (not sure): killed mol was not in clipboard but not in assy.molecules:", self
                    ## print "fyi: mol.kill: mol %r not in self.assy.molecules" % self #bruce 041029
                    pass
                ## self.assy = None # [done by Node.kill as of 050214]
            else:
                # let the Part handle it
                if self.part:
                    self.part.remove(self)
                    assert self.part is None
        Node.kill(self) #bruce 050214 moved this here, made it unconditional
        return # from molecule.kill

    # New method for finding atoms or singlets under mouse. Helps fix bug 235
    # and many other bugs (mostly never reported). [bruce 041214]
    # (We should use this in extrude, too! #e)

    def findAtomUnderMouse( self, point, matrix, **kws):
        """[Public method, but for a more convenient interface see its caller:]
        For each visible atom or singlet (using current display modes and radii,
        but not self.hidden), determine whether its front surface hits the given
        line (encoded in point and matrix), within the optional near and far
        cutoffs (clipping or water planes, parallel to screen) given in **kws.
           Return a list of pairs (z, atom), where z is the z coordinate where
        the line hits the atom's front surface (treating the surface as a sphere)
        after transformation by matrix (closer atoms must have higher z);
        this list always contains either 0 or 1 pair (but in the future we might
        add options to let it contain more pairs).
           Note that a line might hit an atom on the front and/or back of the
        atom's surface (perhaps only on the back, if a cutoff occurs inside the
        atom!). This implem never includes back-surface hits (though it would be
        easy to add them), since the current drawing code doesn't draw them.
        Someday this implem will be obsolete, replaced by OpenGL-based hit tests.
        (Then atom hits will be obscured by bonds, as they should be, since they
        are already visually obscured by them. #e)
           We have a special kluge for selatom -- see the code. As of 041214,
        it's checked twice, at both the radii it's drawn at.
           We have no option to exclude singlets, since that would be wrong to
        do for individual molecules (it would make them fail to obscure atoms in
        other molecules for selection, even when they are drawn over them).
        See our caller in assembly for that.
        """
        if not self.atoms:
            return []
        #e Someday also check self.bbox as a speedup -- but that might be slower
        #  when there are only a few atoms.
        atpos = self.atpos # a Numeric array; might be recomputed here
        
        # assume line of sight hits water surface (parallel to screen) at point
        # (though the docstring doesn't mention this assumption since it is
        #  probably not required as long as z direction == glpane.out);
        # transform array of atom centers (xy parallel to water, z towards user).
        v = dot( atpos - point, matrix)
        
        # compute xy distances-squared between line of sight and atom centers
        r_xy_2 = v[:,0]**2 + v[:,1]**2
        ## r_xy = sqrt(r_xy_2) # not needed
        
        # Select atoms which are hit by the line of sight (as array of indices).
        # See comments in findAtomUnderMouse_Numeric_stuff for more details.
        # (Optimize for the slowest case: lots of atoms, most fail lineofsight
        # test, but a lot still pass it since we have a thick molecule; do
        # "slab" test separately on smaller remaining set of atoms.)

        # self.sel_radii_squared (not a real attribute, just the way we refer to
        # the value of its get method, in comments like this one)
        # is array over atoms of squares of radii to be
        # used for selection (perhaps equal to display radii, or a bit larger)
        # (using mol's and glpane's current display modes), or -1 for invisible
        # atoms (whether directly diINVISIBLE or by inheriting that from the mol
        # or glpane).
        
        # For atoms with more than one radius (currently just selatom),
        # we patch this to include the largest radius, then tell
        # the subroutine how to also notice the smaller radii. (This avoids
        # flicker of selatom when only its larger radius hits near clipping plane.)
        # (This won't be needed once we switch to OpenGL-based hit detection. #e)
        
        radii_2 = self.get_sel_radii_squared() # might be recomputed now
        assert len(radii_2) == len(self.atoms)
        selatom = self.assy.o.selatom
        unpatched_seli_radius2 = None
        if selatom is not None and selatom.molecule is self:
            # need to patch for selatom, and warn subr of its smaller radii too
            seli = selatom.index
            unpatched_seli_radius2 = radii_2[seli]
            radii_2[seli] = selatom.selatom_radius() ** 2
            # (note: selatom is drawn even if "invisible")
            if unpatched_seli_radius2 > 0.0:
                kws['alt_radii'] = [(seli, unpatched_seli_radius2)]
        try:
            # note: kws here might include alt_radii as produced above
            res = self.findAtomUnderMouse_Numeric_stuff( v, r_xy_2, radii_2, **kws)
        except:
            print_compact_traceback("bug in findAtomUnderMouse_Numeric_stuff: ")
            res = []
        if unpatched_seli_radius2 is not None:
            radii_2[seli] = unpatched_seli_radius2
        return res # from findAtomUnderMouse

    def findAtomUnderMouse_Numeric_stuff(self, v, r_xy_2, radii_2, \
                    far_cutoff = None, near_cutoff = None, alt_radii = [] ):
        "private helper routine for findAtomUnderMouse"
        ## removed support for backs_ok, since atom backs are not drawn
        from Numeric import take, nonzero, compress # and more...
        p1 = (r_xy_2 <= radii_2) # indices of candidate atoms
        if not p1: # i.e. if p1 is an array of all false/0 values [bruce 050516 guess/comment]
            # no atoms hit by line of sight (common when several mols shown)
            return []
        p1inds = nonzero(p1) # indices of the nonzero elements of p1
        # note: now compress(p1, arr, dim) == take(arr, p1inds, dim)
        vp1 = take( v, p1inds, 0) # transformed positions of atoms hit by line of sight
        vp1z = vp1[:,2] # depths (above water = positive) of atoms in p1
        
        # i guess i'll do fewer steps -- no slab test until i get actual hit depths.
        # this is suboptimal if the slab test becomes a good one (likely, in the future).
        
        # atom half-thicknesses at places they're hit
        r_xy_2_p1 = take( r_xy_2, p1inds)
        radii_2_p1 = take( radii_2, p1inds)
        thicks_p1 = sqrt( radii_2_p1 - r_xy_2_p1 )
        # now front surfaces are at vp1z + thicks_p1, backs at vp1z - thicks_p1

        fronts = vp1z + thicks_p1 # arbitrary order (same as vp1)
        ## if backs_ok: backs = vp1z - thicks_p1

        # Note that due to varying radii, the sort orders of atom centers,
        # front surface hits, and back surface hits might all be different.
        # We want the closest hit (front or back) that's not too close
        # (or too far, but we can ignore that until we find the closest one);
        # so in terms of distance from the near_cutoff, we want the smallest one
        # that's still positive, from either array. Since one or both arrays might
        # have no positive elements, it's easiest to just form a list of candidates.
        # This helps handle our selatom kluge (i.e our alt_radii option) too.

        pairs = [] # list of 0 to 2 (z, mainindex) pairs which pass near_cutoff

        if near_cutoff is not None:
            # returned index will be None if there was no positive elt; checked below
            closest_front_p1i = index_of_smallest_positive_elt(near_cutoff - fronts)
            ## if backs_ok: closest_back_p1i = index_of_smallest_positive_elt(near_cutoff - backs)
        else:
            closest_front_p1i = index_of_largest_elt(fronts)
            ## if backs_ok: closest_back_p1i = index_of_largest_elt(backs)

##        if not backs_ok:
##            closest_back_p1i = None
        
        if closest_front_p1i is not None:
            pairs.append( (fronts[closest_front_p1i], p1inds[closest_front_p1i] ) )
##        if closest_back_p1i is not None:
##            pairs.append( (backs[closest_back_p1i], closest_back_p1i) )

        # add selatom if necessary:
        # add in alt_radii (at most one; ok to assume that for now if we have to)
        # (ignore if not near_cutoff, since larger radii obscure smaller ones)
        if alt_radii and near_cutoff:
            for ind, rad2 in alt_radii:
                if p1[ind]:
                    # big radius was hit, need to worry about smaller ones
                    # redo above Numeric steps, just for this atom
                    r_xy_2_0 = r_xy_2[ind]
                    radii_2_0 = rad2
                    if r_xy_2_0 <= radii_2_0:
                        thick_0 = sqrt( radii_2_0 - r_xy_2_0 )
                        zz = v[ind][2] + thick_0
                        if zz < near_cutoff:
                            pairs.append( (zz,ind) )
        
        if not pairs:
            return []
        pairs.sort() # the one we want is at the end (highest z == closest)
        (closest_z, closest_z_ind) = pairs[-1]
        
        # We've narrowed it down to a single candidate, which passes near_cutoff!
        # Does it pass far_cutoff?
        if far_cutoff is not None:
            if closest_z < far_cutoff:
                return []

        atm = self.atlist[ closest_z_ind ]
        
        return [(closest_z, atm)] # from findAtomUnderMouse_Numeric_stuff

    # self.sel_radii_squared is not a real attribute, since invalling it
    # would be too slow. Instead we have these methods:
    
    def get_sel_radii_squared(self):
        #bruce 050419 fix bug 550 by fancifying haveradii
        # in the same way as for havelist (see 'bruce 050415').
        # Note: this must also be invalidated when one atom's display mode changes,
        # and it is, by atom.setDisplay calling changeapp(1) on its chunk.
        disp = self.get_dispdef() ##e should caller pass this instead?
        eltprefs = PeriodicTable.rvdw_change_counter # (color changes don't matter for this, unlike for havelist)
        if self.haveradii != (disp,eltprefs): # value must agree with set, below
            # don't have them, or have them for wrong display mode
            ###e (or, someday, for wrong element-radius prefs)
            try:
                res = self.compute_sel_radii_squared()
            except:
                print_compact_traceback("bug in %r.compute_sel_radii_squared(), using []: " % self)
                res = [] #e len(self.atoms) copies of something would be better
            self.sel_radii_squared_private = res
            self.haveradii = (disp,eltprefs)
        return self.sel_radii_squared_private
    
    def compute_sel_radii_squared(self):
        lis = map( lambda atm: atm.selradius_squared(), self.atlist )
        if not lis:
            return lis
        else:
            return A( lis )
        pass

    # Old methods for finding certain atoms or singlets
    
    # [bruce 041207 comment: these ought to be unified, and perhaps bugfixed.
    #  To help with this, I'm adding comments, listing their callers,
    #  and removing the ones with no callers.
    #  See also some relevant code used in extrudeMode.py,
    #  actually findHandles_exact in handles.py,
    #  which will be useful for postprocessing lists of atoms
    #  found by code like the following.
    # ]

    # point is some point on the line of sight
    # matrix is a rotation matrix with z along the line of sight,
    # positive z out of the plane
    # return positive points only, sorted by distance
    
    # [bruce 041104 observes that we return None or one atom, so the above
    #  comment must be out of date, and the method is also misnamed.]
    
    # [bruce 041207 comments: this is only called from depositMode.bareMotion.
    #  It ignores issues of invisible mols or atoms, relevant to bug 229,
    #  but that's ok since these are best addressed by scanning a list of
    #  candidate atoms. It uses a fixed radius for efficiency; that too can be
    #  fixed by postscanning (extrude has example code for this).
    #  It assumes curpos is up-to-date -- I should make it use atpos instead.
    #  Worst, it only returns one atom, making sensiuble post-scans impossible.
    #  For this reason, it's deprecated.
    # ]
##    def findatoms(self, point, matrix, radius, cutoff):
##        """Using point and matrix (see above comment, and sole caller)
##        to define a "z out-of-screen direction" and a "water xy plane",
##        and assuming a line of sight going through point,
##        find the atoms (including singlets) which are within the given fixed
##        radius of the line of sight, and above the water (shifted by cutoff,
##        positive = closer); return the closest-to-user such atom, or None
##        if there are no such atoms in this chunk.
##           Assumes self.curpos is up to date without checking.
##        Ignores issues of invisible chunk (self) or atoms.
##        Ignores actual atom display mode or display radius (thus deprecated
##         by bruce 041207).
##        """
##        # docstring and all comments by bruce 041207:
##        v = dot(self.curpos-point,matrix)
##        r = sqrt(v[:,0]**2 + v[:,1]**2) # xy distance, used only as a cutoff
##        i = argmax(v[:,2] - 100000.0*(r>radius))
##            # assumes model depth < 100000.0
##            # "max" means it favors points closer to user, since z in mat is out
##        # i is index of closest atom within radius of lineofsight, if any
##        if r[i]>radius: return None # this might assume len(curpos) > 0
##        if v[i,2]<cutoff: return None
##        return self.atlist[i]

## bruce 041207 is commenting out the ones that are not currently used

##    # [note: as of bruce 041111, self.singlets is still memoized,
##    # but self.singlpos is recomputed as needed. This should be
##    # ok since these functions are not used in ways that need to
##    # be fast. Maintaining self.singlpos is not worth the trouble.
##    # I might decide to memoize self.singlpos, but not to incrementally
##    # maintain it when atoms or the whole mol is moved, as was done before.]
##
##    # point is some point on the line of sight
##    # matrix is a rotation matrix with z along the line of sight,
##    # positive z out of the plane
##    # return positive points only, sorted by distance
##    def findSinglets(self, point, matrix, radius, cutoff):
##        if not self.singlets: return None
##        v = dot(self.singlpos-point,matrix)
##        r = sqrt(v[:,0]**2 + v[:,1]**2)
##        i = argmax(v[:,2] - 100000.0*(r>radius))
##        if r[i]>radius: return None
##        if v[i,2]<cutoff: return None
##        return self.singlets[i]

    # Same, but return all that match
    # bruce 041207 comment: this is only used in depositMode.modifyHydrogenate,
    # and that's likely to be revised soon.
    ## bruce 050302 removed this, since it's no longer needed after removing
    ## its sole call, mentioned above (which I removed just now to fix bug 130).
##    def findAllSinglets(self, point, matrix, radius, cutoff):
##        if not self.singlets: return []
##        v = dot(self.singlpos-point,matrix)
##        r = sqrt(v[:,0]**2 + v[:,1]**2)
##        lis = []
##        for i in range(len(self.singlets)):
##            if r[i]<=radius and v[i,2]>=cutoff: lis += [self.singlets[i]]
##        return lis

    # return the singlets in the given sphere (point, radius),
    # sorted by increasing distance from point
    # bruce 041207 comment: this is only used in depositMode.attach.
    def nearSinglets(self, point, radius):
        if not self.singlets: return []
        v = self.singlpos-point
        r = sqrt(v[:,0]**2 + v[:,1]**2 + v[:,2]**2)
        p= r<=radius
        i=argsort(compress(p,r))
        return take(compress(p,self.singlets),i)

    def update_curpos(self):
        "private method: make sure self.curpos includes all atoms"
        self.atpos # recompute atpos if necessary, to update curpos

    # == copy methods (extended/revised by bruce 050524-26)

    def will_copy_if_selected(self, sel):
        return True

    def will_partly_copy_due_to_selatoms(self, sel):
        assert 0, "should never be called, since a chunk does not *refer* to selatoms, or appear in atom.jigs"
        return True # but if it ever is called, answer should be true
    
    def copy_empty_shell_in_mapping(self, mapping):
        """[private method to help the public copy methods, all of which start with this except the deprecated mol.copy]
        Copy this chunk's name (w/o change), properties, etc, but not any of its atoms
        (caller will presumably copy some or all of them separately).
        Don't copy hotspot. New chunk is in same assy but not in any Group or Part.
           #doc: invalidation status of resulting chunk?
        Update orig->copy correspondence in mapping (for self, and in future
        for any copyable subobject which gets copied by this method, if any does).
           Never refuses. Returns copy (a new chunk with no atoms).
        Ok to assume self has never yet been copied.
        """
        numol = molecule(self.assy, self.name)
        self.copy_copyable_attrs_to(numol) # copies .name (redundantly), .hidden, .display, .color...
        mapping.record_copy(self, numol)
        # also copy user-specified axis, center, etc, if we ever have those
        ## numol.setDisplay(self.display)
        numol._colorfunc = self._colorfunc # bruce 041109 for extrudeMode.py; revised 050524
        return numol

    def copy_full_in_mapping(self, mapping): # Chunk method [bruce 050526]
        """#doc;
        overrides Node method;
        only some atom copies get recorded in mapping (if we think it might need them)
        """
        numol = self.copy_empty_shell_in_mapping( mapping)
        # now copy the atoms, all at once (including all their existing singlets, even though those might get revised)
        # note: the following code is very similar to copy_in_mapping_with_specified_atoms, but not identical.
        self.update_curpos() # shouldn't matter whether we do this before or after copy_empty_shell
        pairlis = []
        ndix = {} # maps old-atom key to corresponding new atom
        for a in self.atoms.itervalues():
            na = a.copy_for_mol_copy(numol) # has same .index, meant for new molecule
            pairlis.append((a, na))
            ndix[a.key] = na
        numol.invalidate_atom_lists() # probably needed, since copy_for_mol_copy says it is
        numol.curpos = + self.curpos #050524 moved this before copying of bonds, in case they start caring about atom coords
        self._copy_atoms_handle_bonds_jigs( pairlis, ndix, mapping)
        # note: no way to handle hotspot yet, since how to do that might depend on whether
        # extern bonds are broken... so let's copy an explicit one, and tell the mapping
        # if we have an implicit one... or, register a cleanup function with the mapping.
        copied_hotspot = self.hotspot # might be None (this uses __getattr__ to ensure the stored one is valid)
        if copied_hotspot is not None:
            numol.set_hotspot( ndix[copied_hotspot.key])
        elif len(self.singlets) == 1: #e someday it might also work if there are two singlets on the same base atom!
            # we have an implicit but unambiguous hotspot:
            # might need to make it explicit in the copy [bruce 041123, revised 050524]
            copy_of_hotspot = ndix[self.singlets[0].key]
            mapping.do_at_end( lambda ch = copy_of_hotspot, numol = numol: numol._preserve_implicit_hotspot(ch) )
        return numol # from copy_full_in_mapping

    def _copy_atoms_handle_bonds_jigs(self, pairlis, ndix, mapping):
        """[private helper for some copy methods]
        Given some copied atoms (in a private format in pairlis and ndix),
        ensure their bonds and jigs will be taken care of.
        """
        from bonds import bond_copied_atoms # might be a recursive import if done at toplevel
        origid_to_copy = mapping.origid_to_copy
        extern_atoms_bonds = mapping.extern_atoms_bonds
            #e could be integrated with mapping.do_at_end,
            # but it's probably better not to, so as to specialize it for speed;
            # even so, could clean this up to bond externs as soon as 2nd atom seen
            # (which might be more efficient, though that doesn't matter much
            #  since externs should not be too frequent); could do all this in a Bond method #e
        for (a, na) in pairlis:
            if a.jigs: # a->na mapping might be needed if those jigs are copied, or confer properties on atom a
                origid_to_copy[id(a)] = na # inlines mapping.record_copy for speed
            for b in a.bonds:
                a2key = b.other(a).key
                if a2key in ndix:
                    # internal bond - make the analogous one [this should include all bonds to singlets]
                    #bruce 050524 changes: don't do it twice for the same bond;
                    # and use bond_copied_atoms to copy bond state (e.g. bond-order policy and estimate) from old bond.
                    # [note, this code is being copied into the old .copy() method too, by bruce 050715]
                    if a.key < a2key:
                        # arbitrary condition which is true for exactly one ordering of the atoms;
                        # note both keys are for original atoms (it would also work if both were from
                        # copied atoms, but not if they were mixed)
                        bond_copied_atoms(na, ndix[a2key], b)
                else:
                    # external bond [or at least outside of atoms in pairlis/ndix] - caller will handle it when all chunks
                    # and individual atoms have been copied (copy it if it appears here twice, or break it if once)
                    # [note: similar code will be in atom.copy_in_mapping] 
                    extern_atoms_bonds.append( (a,b) ) # it's ok if this list has several entries for one 'a'
                    origid_to_copy[id(a)] = na
                        # a->na mapping will be needed outside this method, to copy or break this bond
                pass
            pass
        return # from _copy_atoms_handle_bonds_jigs

    def copy_in_mapping_with_specified_atoms(self, mapping, atoms): #bruce 050524-050526
        """Copy yourself in this mapping (for the first and only time),
        but with only some of your atoms (and all their singlets).
        [#e hotspot? fix later if needed, hopefully by replacing that concept
         with a jig (see comment below for ideas).]
        """
        numol = self.copy_empty_shell_in_mapping( mapping)
        all = list(atoms)
        for a in atoms:
            all.extend(a.singNeighbors())
        items = [(atom.key, atom) for atom in all]
        items.sort()
        pairlis = []
        ndix = {}
        if len(items) < len(self.atoms) and not numol.name.endswith('-frag'):
            # rename to indicate that this copy has fewer atoms, in the same way Separate does
            numol.name += '-frag'
                #e want to add a serno to -frag, e.g. -frag1, -frag2?
                # If so, see -copy for how, and need to fix endswith tests for -frag.
        for key, a in items:
            na = a.copy()
            numol.addatom(na)
            pairlis.append((a, na))
            ndix[key] = na
        self._copy_atoms_handle_bonds_jigs( pairlis, ndix, mapping)
        ##e do anything about hotspot? easiest: if we copy it (explicit or implicit) or its base atom, put them in mapping,
        # and register some other func (than the one copy_in_mapping does) to fix it up at the end.
        # Could do this uniformly in copy_empty_shell_in_mapping, and here just be sure to tell mapping.record_copy.
        #
        # (##e But really we ought to simplify all this code by just replacing the hotspot concept
        #  with a "bonding-point jig" or perhaps a bond property. That might be less work! And more useful!
        #  And then one chunk could have several hotspots with different pastable names and paster-jigs!
        #  And the paster-jig could refer to real atoms to be merged with what you paste it on, not only singlets!
        #  Or to terminating groups (like H) to pop off if you use that pasting point (but not if you use some other one).
        #  Maybe even to terminating groups connected to base at more than one place, so you could make multiple bonds at once!
        #  Or instead of a terminating group, it could include a pattern of what it should suggest adding itself to!
        #  Even for one bond, this could help it orient the addition as intended, spatially!)
        return numol
    
    def _preserve_implicit_hotspot( self, hotspot): #bruce 050524 #e could also take base-atom arg to use as last resort
        if len(self.singlets) > 1 and self.hotspot is None:
            numol.set_hotspot( hotspot, permit_invalid = True) # this checks everything before setting it; if invalid, silent noop

    # == old copy method -- should remove ASAP but might still be needed for awhile (as of 050526)
    
    def copy(self, dad=None, offset=V(0,0,0), cauterize = 1):
        """Public method: Copy the molecule to a new molecule.
        Offset tells where it will go relative to the original.
        Unless cauterize = 0, replace bonds out of the molecule
        with singlets in the copy [though that's not very nice when we're
        copying a group of mols all at once ###@@@ bruce 050206 comment],
        and if this causes the hotspot in the copy to become ambiguous,
        set one explicitly. (This has no effect on the
        original mol's hotspot.) If cauterize == 0, the copy has atoms with lower valence
        instead, wherever the original had outgoing bonds (not recommended).
           Note that the copy has the same assembly as self, but is not added
        to that assembly (e.g. to its .molecules list); caller should call
        assy.addmol if desired. Warning: addmol would not notice if the dad
        (passed as an arg) was some Group in that assembly, and might blindly
        reset it to assy.tree! Also, tho we set dad in the copy as asked,
        we don't add the copied mol to dad.members! Bruce 050202-050206 thinks we
        should deprecate passing dad for now, just pass None, and caller
        should use addmol or addmember (but not both) to place the mol somewhere.
        Not sure what happens now; so I made addchild notice the setting of
        dad but lack of being in dad's members list, and tolerate it but complain
        when atom_debug. This should all be cleaned up sometime soon. ###@@@
        """
        # bruce added cauterize feature 041116, and its hotspot behavior 041123.
        # Without hotspot feature, Build mode pasting could have an exception.
        ##print "fyi debug: mol.copy on %r" % self
        # bruce 041116: note: callers seem to be mainly in model tree copy ops
        # and in depositMode.
        # [where do they call addmol? why did extrude's copies break on 041116?]
        from bonds import bond_copied_atoms # might be a recursive import if done at toplevel
        self.update_curpos()
        pairlis = []
        ndix = {}
        newname = mol_copy_name(self.name)
        #bruce 041124 added "-copy<n>" (or renumbered it, if already in name),
        # similar to Ninad's suggestion for improving bug 163's status message
        # by making it less misleading.
        numol = molecule(self.assy, "fakename") # name is set below
        #bruce 050531 kluges to fix bug 660, until we replace or rewrite this method
        # using one of the newer "copy" methods
        self.copy_copyable_attrs_to(numol)
            # copies .name (redundantly), .hidden, .display, .color...
            # and sets .prior_part, which is what should fix bug 660
        numol.name = newname
        #end 050531 kluges
        for a in self.atoms.itervalues():
            na = a.copy_for_mol_copy(numol) # has same .index, meant for new molecule
            pairlis += [(a, na)]
            ndix[a.key] = na
        numol.invalidate_atom_lists()
        extern_atoms_bonds = []
        for (a, na) in pairlis:
            for b in a.bonds:
                a2key = b.other(a).key
                if a2key in ndix:
                    # internal bond - make the analogous one [this should include all preexisting bonds to singlets]
                    #bruce 050715 bugfix (copied from 050524 changes to another routine; also done below for extern_atoms_bonds):
                    # don't do it twice for the same bond (needed by new faster bonding methods),
                    # and use bond_copied_atoms to copy bond state (e.g. bond-order policy and estimate) from old bond.
                    if a.key < a2key:
                        # arbitrary condition which is true for exactly one ordering of the atoms;
                        # note both keys are for original atoms (it would also work if both were from
                        # copied atoms, but not if they were mixed)
                        bond_copied_atoms(na, ndix[a2key], b)
                    ## pre-050715 code: numol.bond(na,ndix[b.other(a).key])
                else:
                    # external bond - after loop done, make a singlet in the copy
                    extern_atoms_bonds.append( (a,b) ) # ok if several times for one 'a'
        if extern_atoms_bonds:
            pass ## print "fyi: mol.copy didn't copy %d extern bonds..." % len(extern_atoms_bonds)
        copied_hotspot = self.hotspot # might be None
        if cauterize:
            # do something about non-copied bonds (might be useful for extrude)
            # [experimental code, bruce 041112]
            if extern_atoms_bonds:
                ## print "... but it will make them into singlets"
                # don't make our hotspot ambiguous, if it wasn't already
                if self.hotspot is None and len(self.singlets) == 1:
                    # we have an implicit but unambiguous hotspot:
                    # make it explicit in the copy [bruce 041123]
                    copied_hotspot = self.singlets[0]
            for a,b in extern_atoms_bonds:
                # compare to code in Bond.unbond():
                x = atom('X', b.ubp(a) + offset, numol)
                na = ndix[a.key]
                #bruce 050715 bugfix: also copy the bond-type (two places in this routine)
                ## numol.bond(na, x)
                bond_copied_atoms( na, x, b)
        if copied_hotspot is not None:
            numol.set_hotspot( ndix[copied_hotspot.key])
        #e also copy (but translate by offset) user-specified axis, center, etc,
        #  if we ever have those
        if self.user_specified_center is not None: #bruce 050516 bugfix: 'is not None'
            numol.user_specified_center = self.user_specified_center + offset
        numol.curpos = self.curpos + offset
            # (if offset was 0, that is still needed to ensure the new curpos
            #  is not the same array object as the old one)
        ## numol.shakedown()
        numol.setDisplay(self.display)
        numol.dad = dad
        if dad and platform.atom_debug: #bruce 050215
            print "atom_debug: mol.copy got an explicit dad (this is deprecated):", dad
        numol._colorfunc = self._colorfunc # bruce 041109 for extrudeMode.py; revised 050524
        return numol

    # ==
    
    def Passivate(self, p=False):
        """[Public method, does all needed invalidations:]
        Passivate the selected atoms in this chunk, or all its atoms if p=True.
        This transmutes real atoms to match their number of real bonds,
        and (whether or not that succeeds) removes all their open bonds.
        """
        # bruce 041215 added docstring, inferred from code; capitalized name
        for a in self.atoms.values():
            if p or a.picked: a.Passivate()

    def Hydrogenate(self):
        """[Public method, does all needed invalidations:]
        Add hydrogen to all unfilled bond sites on carbon
        atoms assuming they are in a diamond lattice.
        For hilariously incorrect results, use on graphite.
        This ought to be an atom method. Huaicai1/19/05: return the number of atoms hydrogenated
        """
        # bruce 041215 suspects docstring is wrong in implying this
        # only affects Carbon ###k
        count = 0
        for a in self.atoms.values():
            count += a.Hydrogenate()
        return count    
            
    def Dehydrogenate(self):
        """[Public method, does all needed invalidations:]
        Remove hydrogen atoms from this chunk.
        Return the number of atoms removed [bruce 041018 new feature].
        """
        count = 0
        for a in self.atoms.values():
            count += a.Dehydrogenate()
        return count
            
    def edit(self):
        cntl = ChunkProp(self) # Renamed MoleculeProp to ChunkProp.  Mark 050929
        cntl.exec_loop()
        self.assy.mt.mt_update()
        ###e bruce 041109 comment: don't we want to repaint the glpane, too?

    def __str__(self):
        return "<Chunk %r>" % self.name # bruce 041124 revised this

    def __repr__(self): #bruce 041117, revised 051011
        # Note: if you extend this, make sure it doesn't recompute anything
        # (like len(self.singlets) would do) or that will confuse debugging
        # by making debug-prints trigger recomputes.
        if self is _nullMol:
            return "<_nullMol>"
        try:
            name = "%r" % self.name
        except:
            name = "(exception in self.name repr)"
        try:
            self.assy
        except:
            return "<Chunk %s at %#x with self.assy not set>" % (name, id(self)) #bruce 051011
        if self.assy is not None:
            return "<Chunk %s (%d atoms) at %#x>" % (name, len(self.atoms), id(self))
        else:
            return "<Chunk %s, KILLED (no assy), at %#x of %d atoms>" % (name, id(self), len(self.atoms)) # note other order
        pass

    def dump(self):
        print self, len(self.atoms), 'atoms,', len(self.singlets), 'singlets'
        for a in self.atlist:
            print a
            for b in a.bonds:
                print b

    def merge(self, mol):
        """merge the given molecule into this one."""
        # rewritten by bruce 041117 for speed (removing invals and asserts);
        # effectively inlines hopmol and its delatom and addatom;
        # no need to find and hop singlet neighbors of atoms in mol
        # since they were already in mol anyway.
        for atm in mol.atoms.values():
            # should be a method in atom:
            atm.xyz = atm.posn()
            atm.index = -1
            atm.molecule = self
            #bruce 050516: changing atm.molecule is now enough in itself
            # to invalidate atm's bonds, since their validity now depends on
            # a counter stored in (and unique to) atm.molecule having
            # a specific stored value; in the new molecule (self) this will
            # have a different value. So I can remove the following code:
##            for bon in atm.bonds:
##                bon.setup_invalidate()
##                # Probably not needed -- will happen when self.atpos is remade.
##                # It's ok that atm is moved already (and it better be,
##                # since even if we did this before moving atm,
##                # the other atom might be moved by now).
        self.atoms.update(mol.atoms)
        self.invalidate_atom_lists()
        # be safe, since we just stole all mol's atoms:
        mol.atoms = {}
        mol.invalidate_atom_lists()
        mol.kill()
        return # from merge

    def get_singlets(self): #bruce 041109 moved here from extrudeMode.py
        "return a sequence of the singlets of molecule self"
        return self.singlets # might be recomputed by _recompute_singlets

    def overlapping_chunk(self, chunk, tol=0.0):
        '''Returns True if any atom of chunk is within the bounding sphere of this chunk's bbox. 
        Otherwise, returns False.  tol is an optional arguement containing an additional
        distance to be added to the bounding sphere in the check.
        '''
        if vlen (self.bbox.center() - chunk.bbox.center()) > \
                    self.bbox.scale() + chunk.bbox.scale() + tol:
            return False
        else:
            return True
    
    def overlapping_atom(self, atom, tol = 0.0):
        '''Returns True if atom is within the bounding sphere of this chunk's bbox. 
        Otherwise, returns False.  tol is an optional arguement containing an 
        additional distance to be added to the bounding sphere in the check.
        '''
        # This currently checks the bounding sphere.
        if vlen (atom.posn() - self.bbox.center()) > self.bbox.scale() + tol:
            return False
        else:
            return True
            
    pass # end of class molecule

# ==

# The molecule _nullMol is never part of an assembly, but serves as the molecule
# for atoms removed from other mols (when killed, or before being added to new
# mols), so it can absorb invalidations which certain dubious code
# (like depositMode via selatom) sends to killed atoms, by operating on them
# (or invalidating bonds containing them) even after they're killed.

# Initing _nullMol here caused a bus error; don't know why (class Node not ready??)
# So we do it when first needed, in delatom, instead. [bruce 041116]
## _nullMol = molecule("<not an assembly>")
_nullMol = None

# ==

def shakedown_poly_eval_evec_axis(basepos):
    """Given basepos (an array of atom positions), compute and return (as the
    elements of a tuple) the bounding polyhedron we should draw around these
    atoms to designate that their molecule is selected, the eigenvalues and
    eigenvectors of the inertia tensor (computed as if all atoms had the same
    mass), and the (heuristically defined) principal axis.
    """
    # bruce 041106 split this out of the old molecule.shakedown() method,
    # replaced molecule attrs with simple variables (the ones we return),
    # and renamed self.eval to evals (just in this function) to avoid
    # confusion with python's built-in function eval.
    
    if not len(basepos): #bruce 041119 bugfix -- use len()
        ## wrong: return None, None, None, V(1,0,0)
        return [], [], [], V(1,0,0) # also a guess, but should be safer
        #e do we need to figure out better values to return for 0 atoms??
    
    # find extrema in many directions
    xtab = dot(basepos, polyXmat)
    mins = minimum.reduce(xtab) - 1.8
    maxs = maximum.reduce(xtab) + 1.8

    polyhedron = makePolyList(cat(maxs,mins))

    # and compute inertia tensor
    tensor = zeros((3,3),Float)
    for p in basepos:
        rsq = dot(p, p)
        m= - multiply.outer(p, p)
        m[0,0] += rsq
        m[1,1] += rsq
        m[2,2] += rsq
        tensor += m
    evals, evec = eigenvectors(tensor)

    # Pick a principal axis: if square or circular, the axle;
    # otherwise the long axis (this is a heuristic)

    # note: bruce 041112 suspects it was a bug in original source
    # to say atpos rather than basepos. Evidence: axis as used
    # in self.getaxis should be in base coords; axis computed
    # below from evec (when > 2 atoms) is in base coords.
    if len(basepos)<=1:
        axis = V(1,0,0)
    elif len(basepos) == 2:
        axis = norm(subtract.reduce(basepos))
    else:
        ug = argsort(evals)
        try:
            if evals[ug[0]]/evals[ug[1]] >0.95:
                axis = evec[ug[2]]
            else: axis = evec[ug[0]]
        except ZeroDivisionError:
            # this happened in bug 452 item 18. I'll make it safe, then (separately)
            # fix the bug which causes it in the first place. [bruce 050321]
            if platform.atom_debug:
                print_compact_traceback("atom_debug: ignoring ZeroDivisionError: ")
            axis = evec[ug[0]]

    return polyhedron, evals, evec, axis # from shakedown_poly_evals_evec_axis

# ==

from bonds import bond_at_singlets # only for the sake of code that tries to import this from here; should be removed ASAP ###@@@

# [bruce 050502 moved bond_at_singlets from here into bonds.py]

def mol_copy_name(name): # bruce 041124
    "turn xxx or xxx-copy<n> into xxx-copy<m> for a new number <m>"
    try:
        parts = name.split("-copy")
        assert parts[-1] and (parts[-1].isdigit()) # often fails, that's ok
    except: # lots of kinds of exceptions are possible, that's ok
        pass
    else:
        # name must look like xxx-copy<n>
        name = "-copy".join(parts[:-1]) # this is the xxx part
    return gensym(name + "-copy") # we assume this adds a number to the end

# == Numeric.array utilities [bruce 041207/041213]

def index_of_smallest_positive_elt(arr, retval_if_none = None):
    # use same kluge value as findatoms (an assumption of max model depth)
    res = argmax( - arr - 100000.0*(arr < 0) )
    if arr[res] > 0.0:
        return res
    else:
        return retval_if_none

def index_of_largest_elt(arr):
    return argmax(arr) #e inline it?

# == debug code

debug_messup_basecenter = 0
    # set this to 1 to change basecenter gratuitously,
    # if you want to verify that this has no visible effect
    # (or find bugs when it does, like in Extrude as of 041118)

# messupKey is only used when debug_messup_basecenter, but it's always set,
# so it's ok to set debug_messup_basecenter at runtime

messupKey = genKey()

# end of chunk.py
