# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
chem.py -- class Atom, and related code. An instance of Atom represents one
atom, pseudoatom, or bondpoint in 3d space, with a list of bonds and
jigs, and an optional display mode.

@author: Josh
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

- originally by Josh

- lots of changes, by various developers

- class molecule, for chunks, was moved into new file chunk.py circa 041118

- elements.py was split out of this module on 041221

- class Bond and associated code moved into new file bonds.py by bruce 050502

- bruce optimized some things, including using 'is' and 'is not' rather than
  '==' and '!=' for atoms, molecules, elements, parts, assys, atomtypes in many
  places (not all commented individually); 050513

- bruce 050610 renamed class atom to class Atom; for now, the old name still
  works. The name should gradually be changed in all code (as of now it is not
  changed anywhere, not even in this file except for creating the class), and
  then the old name should be removed. ###@@@

- bruce 050610 changing how atoms are highlighted during Build mode mouseover.
  ###@@@ might not be done

- bruce 050920 removing laxity in valence checking for carbomeric bonds, now
  that mmp file supports them.

- bruce 060308 rewriting Atom and Chunk so that atom positions are always stored
  in the atom (eliminating Atom.xyz and Chunk.curpos, adding Atom._posn,
  eliminating incremental update of atpos/basepos). One motivation is to make it
  simpler to rewrite high-frequency methods in Pyrex.

TODO:

Subclasses of Atom (e.g. for PAM3 pseudoatoms or even strand atoms) are being
considered. One issue to check is whether Undo hardcodes the classname 'Atom'
and will need fixing to work properly for subclasses with different names.
[bruce 071101 comment]
"""

import math
import string

from Numeric import dot
from OpenGL.GL import glPushName
from OpenGL.GL import glPopName

from drawer import ColorSorter
from drawer import drawcylinder
from drawer import drawsphere
from drawer import drawwiresphere
from elements import Singlet
from elements import Hydrogen
from elements import PeriodicTable

from bonds import bonds_mmprecord, bond_copied_atoms, bond_atoms

import global_model_changedicts

# note: chunk and chem form a two element import cycle.
import chunk

from geometry.VQT import V, Q, A, norm, cross, twistor, vlen, orthodist
from geometry.VQT import atom_angle_radians

from mdldata import marks, links, filler
from povheader import povpoint
from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True, Choice
from changedicts import register_changedict, register_class_changedicts

from utilities.Printing import Vector3ToString

from constants import genKey

from constants import diDEFAULT
from constants import diBALL
from constants import diTrueCPK
from constants import diTUBES
from constants import diINVISIBLE

from constants import dispLabel
from constants import default_display_mode
from constants import TubeRadius

from constants import pink
from constants import orange

from constants import ErrorPickedColor
from constants import PickedColor

from GlobalPreferences import disable_do_not_draw_open_bonds

from bond_constants import V_SINGLE
from bond_constants import min_max_valences_from_v6
from bond_constants import valence_to_v6

from bond_constants import DIRBOND_CHAIN_MIDDLE
from bond_constants import DIRBOND_CHAIN_END
from bond_constants import DIRBOND_NONE
from bond_constants import DIRBOND_ERROR

from prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from prefs_constants import showValenceErrors_prefs_key
from prefs_constants import cpkScaleFactor_prefs_key
from prefs_constants import diBALL_AtomRadius_prefs_key

from state_constants import S_CHILDREN, S_PARENT, S_DATA, S_CACHE
from state_constants import UNDO_SPECIALCASE_ATOM, ATOM_CHUNK_ATTRIBUTE_NAME

from Selobj import Selobj_API

# more imports below

# ==

try:
    if not debug_pref('Enable pyrex atoms next time', Choice_boolean_False, prefs_key = True):
        raise ImportError
    from atombase import AtomDictBase, AtomBase
    class AtomDict(AtomDictBase):
        def __init__(self):
            AtomDictBase.__init__(self)
            self.key = atKey.next()
            return
        pass
    print 'Use Pyrex atoms'
except ImportError:
    def AtomDict():
        return { }
    class AtomBase:
        def __init__(self):
            pass
        def __getattr__(self, attr): # in class AtomBase
            raise AttributeError, attr
        pass
    pass

# ==

from utilities.Log import orangemsg
import debug
from debug import print_compact_stack, print_compact_traceback, compact_stack

from utilities import debug_flags # for atom_debug; note that uses of atom_debug should all grab it
  # from debug_flags.atom_debug since it can be changed at runtime

from PlatformDependent import fix_plurals
import env
from state_utils import StateMixin #bruce 060223
from undo_archive import register_undo_updater

debug_1779 = False # do not commit with True, but leave the related code in for now [bruce 060414]

# ==

from displaymodes import remap_atom_dispdefs
    # (moved from chem to displaymodes to break import cycle, bruce 071102)

BALL_vs_CPK = 0.25 # ratio of default diBALL radius to default diTrueCPK radius [renamed from CPKvdW by bruce 060607]

atKey = genKey(start = 1) # generator for atom.key attribute.
    # As of bruce 050228, we now make use of the fact that this produces keys
    # which sort in the same order as atoms are created (e.g. the order they're
    # read from an mmp file), so we now require this in the future even if the
    # key type is changed.

# == Atom

from inval import InvalMixin #bruce 050510

def _undo_update_Atom_jigs(archive, assy):
    """
    [register this to run after all Jigs, atoms, and bonds are updated,
    as cache-invalidator for a.jigs and b.pi_bond_obj]
    [WARNING: as of 060414 this also does essential undo updates unrelated to jigs]
    """
    del archive
    if 1:
        # bruce 060414 fix bug 1779 (more efficient than doing something in Atom._undo_update, for every atom)
        # KLUGE: assume this always runs (true as of 060414), not only if there are jigs or under some other "when needed" conds.
        # Note: it would be best to increment this counter at the start and end of every user op, but there's not yet any central place
        # for code to run at times like that (except some undo-related code which runs at other times too).
        #
        # A more principled and safer fix would be either for kill functions participating in "prekill" to take
        # an argument, unique per prekill/kill event, or to ensure the global counter (acting as if it was that argument)
        # was unique by again incrementing it after the kill call returns within the same code that had initiated the prekill.
        import Utility
        Utility._will_kill_count += 1
    from jigs import Jig
    mols = assy.allNodes(chunk.Chunk) # note: this covers all Parts, whereas assy.molecules only covers the current Part.
    jigs = assy.allNodes(Jig)
        # Note: if we wanted to avoid those imports of Chunk and Jig,
        # then what we really want instances of is:
        # - for Chunk, whatever can be stored in atom.molecule
        #   (and will thus include that atom in its .atoms dict);
        # - for Jig, whatever can be referenced by atom.jigs.
        # In both cases there could be API superclasses for these
        # aspects of Nodehood.
    for m in mols:
        for a in m.atoms.itervalues():
            if a.jigs:
                _changed_structure_Atoms[a.key] = a #bruce 060322; try to only do this to atoms that need it
                #k tracking this change is probably not needed by Undo but might be needed by future non-Undo subscribers
                # to that dict; Undo itself needs to remember to clear its subscribed cache of it after this ###@@@DOIT
                a.jigs = [] #e or del it if we make that optim in Jig (and review whether this needs to occur outside 'if a.jigs')
            for b in a.bonds:
                #k maybe the S_CACHE decl will make this unnecessary? Not sure... maybe not, and it's safe.
                b.pi_bond_obj = None
                # I hope refdecr is enough to avoid a memory leak; if not, give that obj a special destroy for us to call here.
                # That obj won't remove itself from a.jigs on refdecr (no __del__); but it would in current implem of .destroy.
                del b.pi_bond_obj # save RAM
    for j in jigs:
        for a in j.atoms:
            a.jigs.append(j)
            _changed_structure_Atoms[a.key] = a #bruce 060322; see comment about same statement above
    for j in jigs:
        for a in j.atoms[:]:
            j.moved_atom(a)
                # strictly speaking, this is beyond our scope, but Atom._undo_update can't do it since a.jigs isn't set.
                # Also, whatever this does should really just be done by Jig._undo_update. So make that true, then remove this. ###@@@
            if j.killed(): #bruce 080120 added this (precaution)
                break
            j.changed_structure(a) #bruce 080120, might be needed by DnaMarker
            if j.killed():
                break
            continue # next atom
        continue # next jig
            
    return

# WARNING: register_undo_updater does not yet pay attention to its arguments
# except for the update function itself, so it's not yet suitable for use
# with more than one registered function if their relative order matters.
# [bruce 071003 comment]
register_undo_updater( _undo_update_Atom_jigs,
                       updates = ('Atom.jigs', 'Bond.pi_bond_obj'),
                       after_update_of = ('Assembly', 'Node', 'Atom.bonds') # Node also covers its subclasses Chunk and Jig.
                           # We don't care if Atom is updated except for .bonds, nor whether Bond is updated at all,
                           # which is good because *we* are presumably a required part of updating both of those classes!
                       # FYI, we use 'Assembly' (string) rather than Assembly (class) to avoid a recursive import problem,
                       # and also to avoid an inappropriate import dependency (low-level -> high-level).
                    )

# ==

# These global dicts all map atom.key -> atom, for atoms which change in various ways (different for each dict).
# The dicts themselves (as opposed to their contents) never change (so other modules can permanently import them),
# but they are periodically processed and cleared.
# For efficiency, they're global and not weak-valued,
# so it's important to delete items from them when destroying atoms
# (which is itself nim, or calls to it are; destroying assy needs to do that ### TODO). 
# (There's no need yet to use try/except to support reloads of this module by not replacing these dicts then.)

# ###@@@ Note: These are not yet looked at, but the code to add atoms into them is supposedly completed circa bruce 060322.
# update 071106: some of them are looked at (and have been since Undo worked), but maybe not all of them.


_changed_parent_Atoms = {} # record atoms w/ changed assy or molecule or liveness/killedness
    # (an atom's assy is atom.molecule.assy; no need to track changes here to the mol's .part or .dad)
    # related attributes: __killed, molecule ###@@@ declare these??
    # not yet sure if that should be per-attr or not, re subclasses...
    # WARNING: name is private, but it's directly accessed in many places in
    # chunk.py [bruce 071106 comment]
    
register_changedict( _changed_parent_Atoms, '_changed_parent_Atoms', ('__killed', ATOM_CHUNK_ATTRIBUTE_NAME) )
    #k or must we say _Atom__killed??
    # (It depends on whether that routine knows how to mangle it itself.)
    # (As of long before 071018 that arg of register_changedict (related_attrs)
    #  is not yet used.)


_changed_structure_Atoms = {} # tracks changes to element, atomtype, bond set (not bond order #k)
    # WARNING: there is also a related but different global dict in global_model_changedicts.py,
    # whose spelling differs only in 'A' vs 'a' in Atoms, and in having no initial underscore,
    # namely, changed_structure_atoms.
    #
    # This confusion should be cleaned up sometime, by letting that one just be a subscriber to this one,
    # and if efficiency demands it, first splitting this one into the part equivalent to that one, and the rest.
    #
    # Ways this one has more atoms added to it than that one does:
    # jigs, info, kill. (See also the comment where the other one is defined.)
    # See also: _changed_parent_Atoms, which also covers kill (probably in a better way).
    #
    # related attributes: bonds, element, atomtype, info, jigs # (not only '.jigs =', but '.jigs.remove' or '.jigs.append')
    # (we include info since it's used for repeat-unit correspondences in extrude; this is questionable)
    # (we include jigs since they're most like a form of structure, and in future might have physical effects,
    #  and since the jigs for pi bonds are structural)

register_changedict( _changed_structure_Atoms, '_changed_structure_Atoms', ('bonds', 'element', 'atomtype', 'info', 'jigs') )


_changed_posn_Atoms = {} # tracks changes to atom._posn (not clear what it'll do when we can treat baseposn as defining state)
    # related attributes: _posn

register_changedict( _changed_posn_Atoms, '_changed_posn_Atoms', ('_posn',) )


_changed_picked_Atoms = {} # tracks changes to atom.picked (for live or dead atoms)
    # (not to _pick_time etc, we don't cover that in Undo)
    # related attributes: picked
    # WARNING: name is private, but it's directly accessed in
    # ops_select.py [bruce 071106 comment]

register_changedict( _changed_picked_Atoms, '_changed_picked_Atoms', ('picked',) )


_changed_otherwise_Atoms = {} # tracks all other model changes to Atoms (display mode is the only one so far)
    # related attributes: display

register_changedict( _changed_otherwise_Atoms, '_changed_otherwise_Atoms', ('display',) )


# Notes (design scratch): for which Atom attrs is the value mutable in practice? bonds, jigs, maybe _posn (probably not).
# the rest could be handled by a setter in a new-style class, or by AtomBase
# and i wonder if it's simpler to just have one dict for all attrs... certainly it's simpler, so is it ok?
# The reason we have multiple dicts is so undo diff scanning is faster when (e.g.) lots of atoms change in _posn
# and nothing else (as after Minimize or movie playing or (for now) chunk moving).

_Atom_global_dicts = [_changed_parent_Atoms, _changed_structure_Atoms, _changed_posn_Atoms,
                      _changed_picked_Atoms, _changed_otherwise_Atoms]
    # See also some code below class Atom, which registers these changedicts as being used with that class.
    # That code has to occur after the class is defined, but we permit the above per-changedict registrations
    # to come first so that they can help document the dicts near the top of the file.
    # The dicts themselves needn't come first, since they're only looked up as module globals (or from external modules),
    # but it's easier to read the code if they do.
    

# ==

def Atom_prekill_prep(): #bruce 060328
    """Prepare to kill some set of atoms (known to the caller) more efficiently than otherwise.
    Return a value which the caller should pass to the _prekill method on all (and ONLY) those atoms,
    before killing them.
       [#e Note: If we can ever kill atoms and chunks in the same operation, we'll need to revise some APIs
    so they can all use the same value of _will_kill_count, if we want to make that most efficient.]
    """
    ###e this should be merged with similar code in class Node
    import Utility
    Utility._will_kill_count += 1
    return Utility._will_kill_count
    
class Atom(AtomBase, InvalMixin, StateMixin, Selobj_API):
    #bruce 050610 renamed this from class atom, but most code still uses "atom" for now
    # (so we have to assign atom = Atom, after this class definition, until all code has been revised)
    # update, bruce 071113: I am removing that assignment below. See comment there.
    """An Atom instance represents one real atom, or one "singlet"
    (a place near a real atom where another atom could bond to it).
       At any time, each atom has an element, a position in space,
    a list of bond objects it's part of, a list of jigs it's part of,
    and a reference to exactly one molecule object ("chunk") which
    owns it; all these attributes can change over time.
       It also has a never-changing key used as its key in self.molecule.atoms,
    a selection state, a display mode (which overrides that of its molecule),
    and (usually) some attributes added externally by its molecule, notably
    self.index. The attributes .index and .xyz are essentially for the
    private use of the owning molecule; see the methods posn and baseposn
    for details. Other code might add other attributes to an atom; some of
    those might be copied in the private method Atom.copy_for_mol_copy() [now removed].
    """
    # bruce 041109-16 wrote docstring
    # default values of instance variables:
    __killed = 0 # note: this is undoable state, declared below
    picked = False
        # self.picked defines whether the atom is selected; see also assembly.selatoms
        # (note that Nodes also have .picked, with the same meaning, but atoms
        #  are not Nodes)
    display = diDEFAULT # rarely changed for atoms
    _modified_valence = False #bruce 050502
    info = None #bruce 050524 optim (can remove try/except if all atoms have this)
    ## atomtype -- set when first demanded, or can be explicitly set using set_atomtype or set_atomtype_but_dont_revise_singlets
    index = -1 #bruce 060311 add this as a precaution re bug 1661, and since it seems necessary in principle,
        # given that we store it as undoable state, but (I guess, re that bug) don't always set it very soon
        # after making an atom; -1 is also the correct value for an atom in a chunk but not yet indexed therein;
        # in theory the value doesn't matter at all for a chunkless atom, but a removed atom (see Chunk.delatom) will have -1 here,
        # so imitating that seems most correct.
        
    # _s_attr decls for state attributes -- children, parents, refs, bulky data, optional data [bruce 060223]

    _s_undo_specialcase = UNDO_SPECIALCASE_ATOM
        # This tells Undo what specialcase code to use for this class
        # (and any subclasses we might add). It also tells it which
        # changedicts to look at.
        # TODO:
        # - That whole system of Undo changedicts
        # could be refactored and improved, so that we'd instead point
        # to a changedict-containing object which knew which attribute
        # each one was for, as well as knowing this specialcase-type.
        # That object would be a "description of this class for
        # purposes of Undo" (except for the _s_attr decls, which might
        # as well remain as they are).
        # - Ultimately, Undo shouldn't need specialcases at all;
        # right now it needs them since we don't have enough control,
        # when registering updaters that involve several specific
        # classes, of their calling order.
        # (And maybe other minor reasons I forget now, but I think
        #  that's the only major one.)
        # - Meanwhile, it would be good to automatically ensure that
        # the related_attrs lists passed to register_changedicts
        # cover all the undoable state attrs in all the classes
        # that use those changedicts. Otherwise it means changes to
        # some attr are not noticed by Undo (or, that they are,
        # but we forgot to declare which changedict notices them
        # in the related_attrs list for that changedict).
        # [bruce 071114]

    _s_attr_bonds = S_CHILDREN

    _s_attr_molecule = S_PARENT # note: most direct sets of self.molecule are in chunk.py

    assert ATOM_CHUNK_ATTRIBUTE_NAME == 'molecule'
        # must match this _s_attr_molecule decl attr name,
        # and all the atom.molecule refs in all files [bruce 071114]
    
    _s_attr_jigs = S_CACHE # first i said S_REFS, but this is more efficient, and helps handle pi_bond_sp_chain.py's Jigs.
        # [not sure if following comment written 060223 is obs as of 060224:]
        # This means that restored state will unset the .jigs attr, for *all* atoms (???), and we'll have to recompute them somehow.
        # The alg is easy (scan all jigs), but exactly how to organize it needs to be thought about.
        # Is it worth thinking of Atom.jigs in general (not just re Undo) as a recomputable attribute?
        # We could revise the incremental updaters to not worry if it's missing,
        # and put in a __getattr__ which redid the entire model's atoms when it ran on any atom.
        # (Just scan all jigs, and assume all atoms' .jigs are either missing or correct, and ignore correct ones.)
        # But that approach would be wrong for pi_bond_sp_chain.py's Jigs since they would not be scanned (efficiently).
        # So for them, they have to insist that if they exist, the atoms know about them. (Using a sister attr to .jigs?)
        # (Or do we teach atoms how to look for them on nearby bonds? That's conceivable.)
        # ... or if these fields are derived specifically from the atomsets of Jigs, then do we know which atoms to touch
        # based on the manner in which Undo altered certain Jigs (i.e. does our update routine start by knowing the set of
        # old and new values of all changed atomsets in Jigs)?? Certainly we could teach the diff-applyer to make that info
        # available (using suitable attr decls so it knew it needed to)... but I don't yet see how this can work for pi_bond Jigs
        # and for incremental Undo.

    #e we might want to add type decls for the bulky data (including the objrefs above), so it can be stored in compact arrays:

#bruce 060322 zapping _s_attr_key = S_DATA decl -- should be unnecessary since .key never changes. ####@@@@ TEST
# NOTE: for using this for binary mmp files, it might be necessary -- review that when we have them. ###@@@
##    _s_attr_key = S_DATA # this is not yet related to Undo's concept of objkey (I think #k) [bruce 060223]

    # storing .index as Undo state is no longer needed [bruce 060313]
        # note: a long comment removed on 070518 explained that when we had it,
        # it was only valid since chunk's atom order is deterministic

    _s_attr__posn = S_DATA #bruce 060308 rewrite
    _s_attr_element = S_DATA

    # we'll want an "optional" decl on the following, so they're reset to class attr (or unset) when they equal it:
    _s_attr_picked = S_DATA
    _s_categorize_picked = 'selection' ##k this is noticed and stored, but I don't think it yet has any effect (??) [bruce 060313]
    _s_attr_display = S_DATA
    _s_attr_info = S_DATA
    _s_attr__Atom__killed = S_DATA # Declaring (name-mangled) __killed seems needed just like for any other attribute...
        # (and without it, reviving a dead atom triggered an assertfail, unsurprisingly)
    
    #e declare these later when i revise code to unset/redflt them most of the time: ###@@@
    ## _picked_time = _picked_time_2 = -1
    
    # note: atoms don't yet have individual colors, labels, names...
    
    ###e need atomtype - hard part is when it's unset, might have to revise how we handle that, e.g. derive it from _hyb;
    # actually, for pure scan, why is 'unset' hard to handle? i bet it's not. It just has no default value.
    # It's down here under the 'optional' data since we should derive it from _hyb which is usually 'default for element'.
    
    _s_attr_atomtype = S_DATA

    # these are needed for repeated destroy [bruce 060322]
    glname = 0
    if not debug_pref('Enable pyrex atoms next time', Choice_boolean_False, prefs_key=True):
        key = 0   # BAD FOR PYREX ATOMS - class variable vs. instance variable

    _will_kill = 0 #bruce 060327
    
    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  (in this case its gives the path of an 'atom' icon')
    # see PM.PM_SelectionListWidget.insertItems for an example use of this
    # attribute. 
    iconPath = "ui/modeltree/Single_Atom.png"

    # def __init__  is just below a couple undo-update methods

    def _undo_update(self):
        if self.molecule is None:
            # new behavior as of 060409, needed to interact well with differential mash_attrs...
            # i'm not yet fully comfortable with this (maybe we really need _nullMol in here??) ###@@@
            print "bug (ignored): _undo_update on dead atom", self
            return
        #bruce 060224 conservative guess -- invalidate everything we can find any other code in this file invalidating 
        for b in self.bonds:
            b.setup_invalidate()
            b.invalidate_bonded_mols()
        self.molecule.invalidate_attr('singlets')
        self.molecule.invalidate_attr('externs') #bruce 070602: fix Undo bug after Make Crossover (crossovers.py) --
            # the bug was that bonds being (supposedly) deleted during this undo state-mashing would remain in mol.externs
            # and continue to get drawn. I don't know why it didn't happen if bonds were also created on the same atoms
            # (or perhaps on any atoms in the same chunk), but presumably that happened to invalidate externs in some other way.
            # As for why the bug went uncaught until now, maybe no other operation creates external bonds without also
            # deleting bonds on the same atoms (which evidently prevents the bug, as mentioned). For details of what was
            # tried and how it affected what happened, see crossovers.py cvs history circa now.
        self._changed_structure()
        self.changed()
        posn = self.posn()
        self.setposn_batch( posn - V(1,1,1) ) # i hope it doesn't optimize for posn being unchanged! just in case, set wrong then right
        self.setposn_batch( posn )
        # .picked might change... always recompute selatoms in external code ####@@@@
        self.molecule.changeapp(1)
        # anything needed for InvalMixin stuff?? #e ####@@@@
        #
        # can't do this yet:
        ## for jig in self.jigs[:]:
        ##    jig.moved_atom(self)   ####@@@@ need to do this later?
        StateMixin._undo_update(self)

    def __init__(self, sym, where, mol = None): #bruce 060612 let mol be left out
        """Create an Atom of element sym
        (e.g. 'C' -- sym can be an element, atomtype, or element-symbol, or another atom to copy these from)
        at location 'where' (e.g. V(36, 24, 36))
        belonging to molecule mol (can be None or missing).
        Atom initially has no real or open bonds, and default hybridization type.
        """
        # note: it's not necessary to track changes to self's attrs (in e.g. _changed_parent_Atoms) during __init__. [bruce 060322]
        AtomBase.__init__(self)
        self.key = atKey.next()
            # unique key for hashing and/or use as a dict key;
            # also used in str(self)
        _changed_parent_Atoms[self.key] = self # since this dict tracks all new atoms (i.e. liveness of atoms) (among other things)
        self.glname = env.alloc_my_glselect_name( self) #bruce 050610
        # self.element is an Elem object which specifies this atom's element
        # (this will be redundant with self.atomtype when that's set,
        #  but at least for now we keep it as a separate attr,
        #  both because self.atomtype is not always set,
        #  and since a lot of old code wants to use self.element directly)

        # figure out atomtype to assume; atype = None means default atomtype for element will be set.
        
        # [bruce 050707 revised this; previously the default behavior was to set no atomtype now
        #  (picking one when first asked for), not to set the default atomtype now. This worked ok
        #  when the atomtype guessed later was also the default one, but not once that was changed
        #  to guess it based on the number of bonds (when first asked for), since some old code
        #  would ask for it before creating all the bonds on a new atom. Now, the "guessing atomtype
        #  from bonds" behavior is still needed in some cases, and is best asked for by leaving it unset,
        #  but that is done by a special method or init arg ###doc, since it should no longer be what this init
        #  method normally does. BTW the docstring erroneously claimed we were already setting default atomtype.]
        atype = None
        try:
            self.element = sym.element
                # permit sym to be another atom or an atomtype object -- anything that has .element
            #e could assert self.element is now an Elem, but don't bother -- if not, we'll find out soon enough
        except:
            # this is normal, since sym is usually an element symbol like 'C'
            self.element = PeriodicTable.getElement(sym)
        else:
            # sym was an atom or atomtype; use its atomtype for this atom as well (in a klugy way, sorry)
            try:
                atype = sym.atomtype # works if sym was an atom
            except:
                atype = sym
            assert atype.element is self.element # trivial in one of these cases, should improve #e
        # this atomtype (or the default one, if atype is None) will be stored at the end of this init method.
        
        # 'where' is atom's absolute location in model space,
        # until replaced with 'no' by various private methods in Atom or Chunk, indicating
        # the location should be found using the formula in self.posn();
        # or it can be passed as 'no' by caller of __init__
        
        if 1: #bruce 060308 rewrote this part:
            assert where != 'no'
            assert type(where) is type(V(0,0,0))
            self._posn = + where
            _changed_posn_Atoms[self.key] = self #bruce 060322
            
        # list of bond objects
        self.bonds = []
        # list of jigs (###e should be treated analogously to self.bonds)
        self.jigs = []

        # pointer to molecule containing this atom
        # (note that the assembly is not explicitly stored
        #  and that the index is only set later by methods in the molecule)
        self.molecule = None # checked/replaced by mol.addatom
        if mol is not None:
            mol.addatom(self)
        else:
            # this now happens in mol.copy as of 041113
            # print "fyi: creating atom with mol == None"
            pass
        # (optional debugging code to show which code creates bad atoms:)
        ## if debug_flags.atom_debug:
        ##     self._source = compact_stack()
        self.set_atomtype_but_dont_revise_singlets( atype)
        return # from Atom.__init__

    def _undo_aliveQ(self, archive): #bruce 060406
        """Would this (Atom) object be picked up as a child object in a (hypothetical) complete scan of children
        (including change-tracked objects) by the given undo_archive (or, optional to consider, by some other one)?
        The caller promises it will only call this when it's just done ... ###doc
        """
        # This implem is only correct because atoms can only appear in the archive's current state
        # if they are owned by chunks which appear there.
        # (That's only true because we fix or don't save invalid _hotspots, since those can be killed bondpoints.)
        mol = self.molecule
        return archive.childobj_liveQ(mol) and mol.atoms.has_key(self.key)

    def _f_jigs_append(self, jig, changed_structure = True):
        """
        [friend method for class Jig]
        
        Append a jig to self.jigs, and perform necessary invalidations.
        
        @param changed_structure: if true (the default, though whether that's
        needed has not been reviewed), record this as a change to this
        atom's structure for purposes of Undo and updaters.
        """
        #bruce 071025 made this from code in class Jig;
        #bruce 071128 added changed_structure option
        self.jigs.append(jig)
        #k not sure if following is needed -- bruce 060322
        if changed_structure:
            _changed_structure_Atoms[self.key] = self
        return

    def _f_jigs_remove(self, jig, changed_structure = True):
        """
        [friend method for class Jig]
        
        Remove a jig from self.jigs, and perform necessary invalidations.
        
        @param changed_structure: if true (the default, though whether that's
        needed has not been reviewed), record this as a change to this
        atom's structure for purposes of Undo and updaters.

        @note: if jig is not in self.jigs, complain (when debug_flags.atom_debug),
        but tolerate this.
        (It's probably an error, but of unknown commonness or seriousness.)
        """
        #bruce 071025 made this from code in class Jig;
        #bruce 071128 added changed_structure option
        try:
            self.jigs.remove(jig)
        except:
            # Q: does this ever still happen? TODO: if so, document when & why.
            # Note that, in theory, it could happen for several reasons,
            # not just the expected one (jig not in a list).
            # new feature 071025 -- if it's not that, raise a new exception.
            # (We could also only catch ValueError here -- might be more sensible.
            #  First verify it's the right one for .remove not finding something!)
            assert type(self.jigs) is type([])
            if debug_flags.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception in _f_jigs_remove (Jig.remove_atom): ")
        else:
            #k not sure if following is needed -- bruce 060322
            if changed_structure:
                _changed_structure_Atoms[self.key] = self
        return

    # For each entry in this dictionary, add a context menu command on atoms of the key element type
    # allowing transmutation to each of the element types in the value list.
    # (bruce 070412 addition: if the selected atoms are all one element, and
    #  one of those is the context menu target, make this command apply to all
    #  those selected atoms.
    #  [Q: should it apply to the subset of the same element, if that's not all?
    #   Guess: yes. That further enhancement is NIM for now.])
    _transmuteContextMenuEntries = {
        'Ae3': ['Ax3'],
        'Ax3': ['Ae3'],
        'Se3': ['Ss3', 'Sh3'],
        'Pl3': ['Pe5', 'Sh3'], # Unused in PAM3
        'Sh3': ['Ss3', 'Se3'],
        'Sj3': ['Ss3'],
        'Ss3': ['Sj3', 'Hp3'],
        'Hp3': ['Ss3'],
        'Ae5': ['Ax5'],
        'Ax5': ['Ae5'],
        'Pe5': ['Pl5', 'Sh5'],
        'Pl5': ['Pe5', 'Sh5'],
        'Sh5': ['Pe5', 'Pl5'],
        'Sj5': ['Ss5'],
        'Ss5': ['Sj5', 'Hp5'],
        'Hp5': ['Ss5'], #bruce 070412 added Ss <-> Hp; not sure if that's enough entries for Hp
        }
    def make_selobj_cmenu_items(self, menu_spec):
        """Add self-specific context menu items to <menu_spec> list when self is the selobj,
        in modes that support it (e.g. depositMode and selectMode and subclasses).
        """
        fromSymbol = self.element.symbol
        if (self._transmuteContextMenuEntries.has_key(fromSymbol)):
            #bruce 070412 (enhancing EricM's recent new feature):
            # If unpicked, do it for just this atom;
            # If picked, do it for all picked atoms, but only if they are all the same element.
            # (But if they're not, still offer to do it for just this atom, clearly saying so if possible.)
            if self.picked:
                selatoms = self.molecule.assy.selatoms # there ought to be more direct access to this
                doall = True
                for atom in selatoms.itervalues():
                    if atom.element.symbol != fromSymbol:
                        doall = False
                        break
                    continue
                # Note: both doall and self.picked and len(selatoms) are used below,
                # to determine the proper menu item name and command.
                # Note: as a kluge which is important for speed,
                # we don't actually make a selatoms list here as part of the command,
                # since this menu item won't usually be the one chosen,
                # and it can find the selatoms again.
                #
                # higher-level entry for Pl, first [bruce 070522, 070601]:
                if fromSymbol == 'Pl5' and doall and len(selatoms) == 2:
##                    import crossovers
##                    try:
##                        reload(crossovers)### REMOVE WHEN DEVEL IS DONE; for debug only; will fail in a built release
##                    except:
##                        print "can't reload crossovers"
                    from crossovers import crossover_menu_spec
                    ms1 = crossover_menu_spec(self, selatoms)
                    if ms1:
                        menu_spec.append(None) # separator
                        menu_spec.extend(ms1)
            menu_spec.append(None) # separator
            for toSymbol in self._transmuteContextMenuEntries[fromSymbol]:
                newElement = PeriodicTable.getElement(toSymbol)
                if self.picked and len(selatoms) > 1:
                    if doall:
                        cmdname = "Transmute selected atoms to %s" % toSymbol
                            #e could also say the number of atoms
                        command = ( lambda arg1 = None, arg2 = None,
                                    atom = self, newElement = newElement: atom.Transmute_selection(newElement) )
                            # Kluge: locate that command method on atom, used for access to selatoms,
                            # even though it's not defined to operate on atom (tho it does in this case).
                            # One motivation is to ease the upcoming emergency merge by not modifying more files/code
                            # than necessary.
                    else:
                        cmdname = "Transmute this atom to %s" % toSymbol
                            #e could also say fromSymbol, tho it appears elsewhere in the menu
                        command = ( lambda arg1 = None, arg2 = None,
                                    atom = self, newElement = newElement: atom.Transmute(newElement) )
                else:
                    cmdname = "Transmute to %s" % toSymbol
                    command = ( lambda arg1 = None, arg2 = None,
                                atom = self, newElement = newElement: atom.Transmute(newElement) )
                menu_spec.append((cmdname, command))
                continue
        if debug_flags.atom_debug:
            from undo_archive import _undo_debug_obj
            if self is _undo_debug_obj:
                checked = 'checked'
            else:
                checked = None
            item = ('_undo_debug_obj = %r' % self, self.set_as_undo_debug_obj, checked)
            menu_spec.append(item)
        return

    def set_as_undo_debug_obj(self):
        import undo_archive
        undo_archive._undo_debug_obj = self
        undo_archive._undo_debug_message( '_undo_debug_obj = %r' % self )
        return
    
    def __getattr__(self, attr): # in class Atom
        assert attr != 'xyz' # temporary: catch bugs in bruce 060308 rewrite
        try:
            return AtomBase.__getattr__(self, attr)
        except AttributeError:
            return InvalMixin.__getattr__(self, attr)

    def destroy(self): #bruce 060322 (not yet called) ###@@@
        """[see comments in Node.destroy or perhaps StateMixin.destroy]
        Note: it should be legal to call this multiple times, in any order w/ other objs' destroy methods.
        SEMANTICS ARE UNCLEAR -- whether it should destroy bonds in self.bonds (esp in light of rebond method).
        See comments in assy_clear by bruce 060322 (the "misguided" ones, written as if that was assy.destroy, which it's not).
        """
        # If this proves inefficient, we can dispense with most of it, since glselect dict can be made weak-valued
        # (and will probably need to be anyway, for mmkit library part atoms),
        # and change-tracking dicts (_Atom_global_dicts) are frequently cleared, and subscribers will ignore objects
        # from destroyed assys. So it's only important here if we destroy atoms before their assy is destroyed
        # (e.g. when freeing from redo or old undo diffs), and it's probably not enough for that anyway (not thought through).
        # Ideally we'd remove cycles, not worry about transient refs in change-trackers, make change-trackers robust
        # to being told about destroyed atoms, and that would be enough. Not yet sure whether that's practical.
        # [bruce 060327 comment]
        env.dealloc_my_glselect_name( self, self.glname )
        key = self.key
        for dict1 in _Atom_global_dicts:
            #e even this might be done by StateMixin if we declare these dicts to it for the class
            # (but we'd have to tell it what key we use in them, e.g. provide a method or attr for that
            #  (like .key? no, needs _s_ prefix to avoid accidental definition))
            dict1.pop(key, None) # remove self, if it's there
            ###e we need to also tell the subscribers to those dicts that we're being destroyed, I think
        # is the following in a superclass (StateMixin) method?? ###k
        self.__dict__.clear() ###k is this safe???
        ## self.bonds = self.jigs = self.molecule = self.atomtype = self.element = self.info = None # etc...
        return
    
    def unset_atomtype(self): #bruce 050707
        "Unset self.atomtype, so that it will be guessed when next used from the number of bonds at that time."
        try:
            del self.atomtype
        except:
            # assume already deleted
            pass
        return
    
    def atomtype_iff_set(self):
        return self.__dict__.get('atomtype', None)
    
    _inputs_for_atomtype = []
    def _recompute_atomtype(self): # used automatically by __getattr__
        """
        Something needs this atom's atomtype but it doesn't yet have one.
        Give it our best guess of type, for whatever current bonds it has.
        """
        return self.reguess_atomtype()

    def reguess_atomtype(self, elt = None):
        """
        Compute and return the best guess for this atom's atomtype
        given its current element (or the passed one),
        and given its current real bonds and open bond user-assigned types
        (but don't save this, and don't compare it to the current self.atomtype).

        WARNING: This is only correct for a new atom if it has
        already been given all its bonds (real or open).
        """
        #bruce 050702 revised this; 050707 using it much less often (only on special request ###doc what)
        ###@@@ Bug: This does not yet [050707] guess correctly for all bond patterns; e.g. it probably never picks N/sp2(graphitic).
        # That means there is presently no way to save and reload that atomtype in an mmp file, and only a "direct way"
        # (specifying it as an atomtype, not relying on inferring from bonds) would work unless this bug is fixed here.
        ###@@@ (need to report this bug)
        if self.__killed:
            # bruce 071018 new bug check and new mitigation (return default atomtype)
            print_compact_stack( "bug: reguess_atomtype of killed atom %s (returning default): " % self)
            return self.element.atomtypes[0]
        if len(self.bonds) == 0:## and debug_flags.atom_debug:
            # [bruce 071018 check this always, to see if skipping killed atoms
            #  in update_bonds_after_each_event has fixed this bug for good]
            # (I think the following cond (using self.element rather than elt)
            # is correct even when elt is passed -- bruce 050707)
            if self.element.atomtypes[0].numbonds != 0: # not a bug for noble gases!
                if 1: ## or env.once_per_event("reguess_atomtype warning"): #bruce 060720, only warn once per user event
                    print_compact_stack(
                        ## "atom_debug: warning (once per event): reguess_atomtype(%s) sees %s with no bonds -- probably a bug: " % \
                        "warning: reguess_atomtype(%s) sees non-killed %s with no bonds -- probably a bug: " % \
                        (elt, self) )
        return self.best_atomtype_for_numbonds(elt = elt)

    def set_atomtype_but_dont_revise_singlets(self, atomtype): ####@@@@ should merge with set_atomtype; perhaps use more widely
        """
        #doc;
        atomtype is None means use default atomtype
        """
        atomtype = self.element.find_atomtype( atomtype) # handles all forms of the request; exception if none matches
        assert atomtype.element is self.element # [redundant with find_atomtype]
        self.atomtype = atomtype
        self._changed_structure() #bruce 050627; note: as of 050707 this is always called during Atom.__init__
        ###e need any more invals or updates for this method?? ###@@@
        return
        
    def set_atomtype(self, atomtype, always_remake_bondpoints = False):
        """
        [public method; not super-fast]
        Set this atom's atomtype as requested, and do all necessary invalidations or updates,
        including remaking our singlets as appropriate, and [###@@@ NIM] invalidating or updating bond valences.
           It's ok to pass None (warning: this sets default atomtype even if current one is different!),
        atomtype's name (specific to self.element) or fullname, or atomtype object. ###@@@ also match to fullname_for_msg()??? ###e
        The atomtype's element must match the current value of self.element --
        we never change self.element (for that, see mvElement).
           Special case: if new atomtype would be same as existing one (and that is already set), do nothing
        (rather than killing and remaking singlets, or even correcting their positions),
        unless always_remake_bondpoints is true. [not sure if this will be used in atomtype-setting menu-cmds ###@@@]
        """
        # Note: mvElement sets self.atomtype directly; if it called this method, we'd have infrecur!
        atomtype = self.element.find_atomtype( atomtype) # handles all forms of the request; exception if none matches
        assert atomtype.element is self.element # [redundant with find_atomtype] #e or transmute if not??
        if always_remake_bondpoints or (self.atomtype_iff_set() is not atomtype):
            self.direct_Transmute( atomtype.element, atomtype ) ###@@@ not all its needed invals/updates are implemented yet
            # note: self.atomtype = atomtype is done in direct_Transmute when it calls mvElement
        return
    
    def setAtomType(self, atomtype, always_remake_bondpoints = False):
        """
        Same as self.set_atomtype(), provided for convenience.
        """
        self.set_atomtype(atomtype, always_remake_bondpoints)
        
    def getAtomType(self):
        """
        Returns the atomtype.
        
        @return: The atomtype.
        @rtype:  L{AtomType}
        """
        return self.atomtype
    
    def getAtomTypeName(self):
        """
        Returns the name of this atom's atomtype.
        
        @return: The atomtype name.
        @rtype:  str
        """
        return self.atomtype.name

    def posn(self):
        """Return the absolute position of the atom in space.
        [Public method; should be ok to call for any atom at any time.]
        """
        #bruce 041104,041112 revised docstring
        #bruce 041130 made this return copies of its data, using unary '+',
        # to ensure caller's version does not change if the atom's version does,
        # or vice versa. Before this change, some new code to compare successive
        # posns of the same atom was getting a reference to the curpos[index]
        # array element, even though this was part of a longer array, so it
        # always got two refs to the same mutable data (which compared equal)!
        #bruce 060308 rewrote the following        
        res = + self._posn
        try:
            #bruce 060208: try to protect callers against almost-overflowing values stored by buggy code
            # (see e.g. bugs 1445, 1459)
            res * 1000
        except:
            # note: print_compact_traceback is not informative -- the call stack might be, tho it's long.
            print_compact_stack("bug: atom position overflow for %r; setting position to 0,0,0: " % self)
            ##e history message too? only if we can prevent lots of them from coming out at once.
            res = V(0,0,0) ##e is there any better choice of position for this purpose? e.g. a small random one, so it's unique?
            self.setposn(res) # I hope this is safe here... we need the invals it does.
        return res
    
    def sim_posn(self): #bruce 060111
        """Return our posn, as the simulator should see it -- same as posn except for Singlets,
        which should pretend to be H and correct their distance from base atom accordingly.
        Should work even for killed atoms (e.g. singlets with no bonds).
           Note that if this is used on a corrected singlet position derived from a simulated H position
        (as in the 060111 approximate fix of bug 1297), it's only approximate, since the actual H position
        might not have been exactly its equilibrium position.
        """
        if self.element is Singlet and len(self.bonds) == 1:
            oa = self.bonds[0].other(self) # like self.singlet_neighbor() but fewer asserts
            return self.ideal_posn_re_neighbor( oa, pretend_I_am = Hydrogen ) # see also self.writemmp()
        return self.posn()

    def baseposn(self): #bruce 041107; rewritten 041201 to help fix bug 204; optimized 050513
        """Like posn, but return the mol-relative position.
        Semi-private method -- should always be legal, but assumes you have
        some business knowing about the mol-relative coordinate system, which is
        somewhat private since it's semi-arbitrary and is changed by some
        recomputation methods. Before 041201 that could include this one,
        if it recomputed basepos! But as of that date we'll never compute
        basepos or atpos if they're invalid.
        """
        #comment from 041201:
        #e Does this mean we no longer use basepos for drawing? Does that
        # matter (for speed)? We still use it for things like mol.rot().
        # We could inline the old baseposn into mol.draw, for speed.
        # BTW would checking for basepos here be worth the cost of the check? (guess: yes.) ###e
        # For speed, I'll inline this here: return self.molecule.abs_to_base( self.posn())
        #new code from 050513:
        mol = self.molecule
        basepos = mol.__dict__.get('basepos') #bruce 050513
        if basepos is not None: ##[bruce 060308 zapped:]## and self.xyz == 'no': #bruce 050516 bugfix: fix sense of comparison to 'no'
            return basepos[self.index]
                # note: since mol.basepos exists, mol.atlist does, so self.index is a valid index into both of them
                # [bruce 060313 comment]
        # fallback to slower code from 041201:
        return mol.quat.unrot(self.posn() - mol.basecenter) # this inlines mol.abs_to_base( self.posn() ) [bruce 060411 comment]

    def setposn(self, pos):
        """set the atom's absolute position,
        adjusting or invalidating whatever is necessary as a result.
        (public method; ok for atoms in frozen molecules too)
        """
        # fyi: called from depositMode, but not (yet?) from movie-playing. [041110]
        # [bruce 050406: now this is called from movie playing, at least for now.
        #  It's also been called (for awhile) from reading xyz files from Minimize.]
        # bruce 041130 added unary '+' (see Atom.posn comment for the reason).
        #bruce 060308 rewrite
        self._setposn_no_chunk_or_bond_invals(pos)
        mol = self.molecule
        if mol is not None:
            mol.changed_atom_posn()
        
        # also invalidate the bonds or jigs which depend on our position.
        #e (should this be a separate method -- does anything else need it?)
        # note: the comment mentions jigs, but this code doesn't alert them to the move. Bug?? [bruce 070518 question]
        for b in self.bonds:
            b.setup_invalidate()
        return # from setposn

    setposn_batch = setposn #bruce 060308 rewrite of setposn

    def _setposn_no_chunk_or_bond_invals(self, pos): #bruce 060308 (private for Chunk and Atom)
        self._posn = + pos
        _changed_posn_Atoms[self.key] = self #bruce 060322
        if self.jigs: #bruce 050718 added this, for bonds code
            for jig in self.jigs[:]:
                jig.moved_atom(self)
                #e note: this does nothing for most kinds of jigs,
                # so in theory we might optim by splitting self.jigs into two lists;
                # however, there are other change methods for atoms in jigs (maybe changed_structure?),
                # so it's not clear how many different lists are needed, so it's unlikely the complexity is justified.
        return # from setposn_no_chunk_or_bond_invals
    
    def adjBaggage(self, atom, nupos): #bruce 051209 revised meaning and name from adjSinglets
        """We're going to move atom, a neighbor of yours, to nupos,
        so adjust the positions of your singlets (and other baggage) to match.
        """
        ###k could this be called for atom being itself a singlet, when dragging a singlet? [bruce 050502 question]
        apo = self.posn()
        # find the delta quat for the average non-baggage bond and apply
        # it to the baggage
        #bruce 050406 comment: this first averages the bond vectors,
        # old and new, then rotates old to match new. This is not
        # correct, especially if old or new (average) is near V(0,0,0).
        # The real problem is harder -- find a quat which best moves
        # atom as desired without moving the other neighbors.
        # Fixing this might fix some reported bugs with dragging atoms
        # within their chunks in Build mode. Better yet might be to
        # use old singlet posns purely as hints, recomputing new ones
        # from scratch (hints are useful to disambiguate this). ###@@@
        baggage, other = self.baggage_and_other_neighbors()
        if atom in baggage: #bruce 060629 for safety (don't know if ever needed)
            baggage.remove(atom)
            other.append(atom)
        n = other
        ## n = self.realNeighbors()
        old = V(0,0,0)
        new = V(0,0,0)
        for at in n:
            old += at.posn()-apo
            if at is atom:
                new += nupos-apo
            else:
                new += at.posn()-apo
        if n:
            # slight safety tweaks to old code, though we're about to add new code to second-guess it [bruce 060629]
            old = norm(old) #k not sure if these norms make any difference
            new = norm(new)
            if old and new:
                q = Q(old,new)
                for at in baggage: ## was self.singNeighbors()
                    at.setposn(q.rot(at.posn()-apo)+apo) # similar to code in drag_selected_atom, but not identical
            #bruce 060629 for bondpoint problem
            self.reposition_baggage(baggage, (atom,nupos))
        return
    
    def __repr__(self):
        return self.element.symbol_for_printing + str(self.key)

    def __str__(self):
        return self.element.symbol_for_printing + str(self.key)

    def prin(self):
        """for debugging
        """
        lis = map((lambda b: b.other(self).element.symbol), self.bonds)
        print self.element.name, lis

    def draw(self, glpane, dispdef, col, level):
        """Draw this atom depending on whether it is picked
        and its display mode (possibly inherited from dispdef).
        An atom's display mode overrides the inherited one from
        the molecule or glpane, but a molecule's color overrides the atom's
        element-dependent one. No longer treats glpane.selatom specially
        (caller can draw selatom separately, on top of the regular atom).
           Also draws picked-atom wireframe, but doesn't draw any bonds.
        [Caller must draw bonds separately.]
           Return value gives the display mode we used (our own or inherited).
        """
        assert not self.__killed
        disp = default_display_mode # to be returned in case of early exception

        # note use of basepos (in atom.baseposn) since it's being drawn under
        # rotation/translation of molecule
        pos = self.baseposn()
        disp, drawrad = self.howdraw(dispdef)
        if disp == diTUBES:
            pickedrad = drawrad * 1.8 # this code snippet is now shared between draw and draw_in_abs_coords [bruce 060315]
        else:
            pickedrad = drawrad * 1.1
        color = col or self.drawing_color()

        glname = self.glname
        glPushName( glname) #bruce 050610 (for comments, see same code in Bond.draw)
            # (Note: these names won't be nested, since this method doesn't draw bonds;
            #  if it did, they would be, and using the last name would be correct,
            #  which is what's done (in GLPane.py) as of 050610.)
        ColorSorter.pushName(glname)
        try:
            if disp in [diTrueCPK, diBALL, diTUBES]:
                self.draw_atom_sphere(color, pos, drawrad, level, dispdef)
            self.draw_wirespheres(glpane, disp, pos, pickedrad)
        except:
            ColorSorter.popName()
            glPopName()
            print_compact_traceback("ignoring exception when drawing atom %r: " % self)
        else:
            ColorSorter.popName()
            glPopName()
        
        return disp # from Atom.draw. [bruce 050513 added retval to help with an optim]

    def drawing_color(self, molcolor = None): #bruce 070417 [most calls have the bug of letting molcolor override this ###FIX]
        """
        Return the color in which to draw self, and certain things that touch self.
        This is molcolor or self.element.color by default
        (where molcolor is self.molecule.color if not supplied),
        but some preferences can override that with a warning or error color
        for atoms with something wrong with them.
        """
        if molcolor is None:
            molcolor = self.molecule.color
        color = molcolor
        if color is None:
            color = self.element.color
        # see if warning color is needed
        if self._dna_updater__error: #bruce 080130
            color = orange
# older code, never used:
##        #e see if warning color is needed
##        if self.element.symbol == 'Ax':
##            pass
##            ## color = orange # kluge for testing
##            #e should we just use self.bad for this? not for this initial test anyway.
##            #e call a method of the element or atomtype for this special case code??
##            # get neighbors that are Ss or Sj,
##            # get arb Ss neighbors of those,
##            #  i.e. find the pattern self-Ss|Sj-Ss (but optimize)
##            ## ... self.Ax_strands() ...
##            # get bond direction vectors (bond.bond_direction_vector()...), check antiparallel,
##            # check minor groove using cross... how do we write "methods on patterns of atomtypes"? on pattern classes?
        return color

    # bruce 070409 split this out of draw_atom_sphere; 
    # 070424 revised return value (None -> "")
    def _draw_atom_style(self): 
        """
        [private helper method for L{draw_atom_sphere}, and perhaps related
        methods like L{draw_wirespheres}]

        Return a short hardcoded string (known to L{draw_atom_sphere}) saying
        in what style to draw the atom's sphere.
        
        @return: Returns one of the following values:
                 - "" (Not None) means to draw an actual sphere.
                 - "arrowhead-in" means to draw a 5' arrowhead.
                 - "arrowhead-out" means to draw a 3' arrowhead.
                 - "do not draw" means don't draw anything.
                 - "bondpoint-stub" means to draw a stub.

        @note: We check not only the desirability of the special cases, but all 
        their correctness conditions, making sure that those don't depend on
        the other parameters of L{draw_atom_sphere} (like abs_coords),
        and making it easier for L{draw_atom_sphere} to fallback to its default 
        style when those conditions fail.
        """

        # WARNING: various routines make use of this return value in different ways,
        # but these ways are not independent (e.g. one might draw a cone and one might estimate its size),
        # so changes in any of the uses need to be reviewed for possibly needing changes in the others. [bruce 070409]
        if self.element is Singlet and len(self.bonds) == 1:
            # self is a bondpoint
            if debug_pref("draw bondpoints as stubs", Choice_boolean_False, prefs_key = True):
                # current implem has cosmetic bugs (details commented there), so don't say non_debug = True
                return 'bondpoint-stub' #k this might need to correspond with related code in Bond.draw
        if self.element.bonds_can_be_directional: #bruce 070415, correct end-arrowheads
            # note: as of mark 071014, this can happen for self being a Singlet
            bond = self.strand_end_bond()
            if bond is not None:
                bool_arrowsOnFivePrimeEnds = env.prefs[arrowsOnFivePrimeEnds_prefs_key]
                bool_arrowsOnThreePrimeEnds = env.prefs[arrowsOnThreePrimeEnds_prefs_key]
                # Determine how singlets of strand open bonds should be drawn.
                # draw_bond_main() takes care of drawing bonds accordingly.
                # - mark 2007-10-20.
                if bond.isFivePrimeOpenBond() and bool_arrowsOnFivePrimeEnds:
                    return 'arrowhead-in'
                elif bond.isThreePrimeOpenBond() and bool_arrowsOnThreePrimeEnds:
                    return 'arrowhead-out'
                else:
                    return 'do not draw'
                #e REVIEW: does Bond.draw need to be updated due to this, if "draw bondpoints as stubs" is True?
                #e REVIEW: Do we want to draw even an isolated Pe (with bondpoint) as a cone, in case it's in MMKit,
                #  since it usually looks like a cone when it's correctly used? Current code won't do that.
                #e Maybe add option to draw the dir == 0 case too, to point out you ought to propogate the direction
        return ""

    def draw_atom_sphere(self, color, pos, drawrad, level, dispdef, abs_coords = False):
        """
        #doc
        [dispdef can be None if not known to caller]
        """
        #bruce 060630 split this out for sharing with draw_in_abs_coords
        style = self._draw_atom_style()
        if style == 'do not draw':
            if disable_do_not_draw_open_bonds() or self._dna_updater__error:
                # (first cond is a debug_pref for debugging -- bruce 080122)
                # (the other cond [bruce 080130] should be a more general
                #  structure error flag...)
                style = ''
                color = orange
            else:
                return
        if self._dna_updater__error: #bruce 080130; needed both here and in self.drawing_color()
            color = orange
        if style == 'bondpoint-stub':
            #bruce 060629/30 experiment -- works, incl for highlighting,
            # and even fixes the bondpoint-buried-in-big-atom bugs,
            # but sometimes the bond cyls project out beyond the bp cyls
            # after repositioning bondpoints, or for N(sp2(graphitic)),
            # and it looks bad for double bonds,
            # and sometimes the highlighting cylfaces mix with the non-highlighted ones,
            # as if same depth value. ###@@@
            other = self.singlet_neighbor()
            if abs_coords:
                otherpos = other.posn()
            else:
                otherpos = other.baseposn()
                    # note: this is only correct since self and other are guaranteed to belong to the same chunk --
                    # if they didn't, their baseposns (pos and otherpos) would be in different coordinate systems.
            rad = other.selatom_radius(dispdef) # ok to pass None
            out = norm(pos - otherpos)
            buried = max(0, rad - vlen(pos - otherpos))
            inpos = pos - 0.015 * out
            outpos = pos + (buried + 0.015) * out # be sure we're visible outside a big other atom
            drawcylinder(color, inpos, outpos, drawrad, 1) #e see related code in Bond.draw; drawrad is slightly more than the bond rad
        elif style.startswith('arrowhead-'):
            # two options, bruce 070415:
            # - arrowhead-in means pointing in along the strand_end_bond
            # - arrowhead-out means pointing outwards from the strand_end_bond
            if style == 'arrowhead-in':
                bond = self.strand_end_bond()
                other = bond.other(self)
                otherdir = 1
            elif style == 'arrowhead-out':
                bond = self.strand_end_bond()
                other = bond.other(self)
                otherdir = -1
            else:
                assert 0
            if abs_coords:
                otherpos = other.posn()
            elif self.molecule is other.molecule:
                otherpos = other.baseposn() # this would be wrong if it's in a different chunk!
            else:
                otherpos = self.molecule.abs_to_base(other.posn())
                    ###BUG: this becomes wrong if the chunks move relative to each other! But we don't get updated then. ###FIX
                ## color = gray # to indicate the direction is suspicious and might become invalid (for now)
            out = norm(otherpos - pos) * otherdir
            
            # Set the axis and arrow radius.
            if self.element is Singlet:
                assert Singlet.bonds_can_be_directional #bruce 071105
                # mark 071014 (prior code was equivalent to else case)
                if dispdef == diTUBES:
                    axis = out * drawrad * 1.5
                    arrowRadius = drawrad * 3
                elif dispdef == diBALL:
                    axis = out * drawrad * 1.9
                    arrowRadius = drawrad * 4.5
                else:
                    axis = out * drawrad * 2
                    arrowRadius = drawrad * 5.8
            else:
                axis = out * drawrad
                arrowRadius = drawrad * 2
                    
            # the following cone dimensions enclose the original sphere (and therefore the bond-cylinder end too)
            # (when axis and arrowRadius have their default values above -- not sure if this remains true after [mark 071014]):
            # cone base at pos - axis, radius = 2 * drawrad, cone midplane (radius = drawrad) at pos + axis,
            # thus cone tip at pos + 3 * axis.
            # WARNING: this cone would obscure the wirespheres, except for special cases in self.draw_wirespheres().
            # If you make the cone bigger you might need to change that code too.

            drawsphere(color, pos, drawrad, 0) #KLUGE (harmless but slow) to set color and also to verify cone encloses sphere

            from drawer import glePolyCone
            glePolyCone([[pos[0] - 2 * axis[0], 
                          pos[1] - 2 * axis[1],
                          pos[2] - 2 * axis[2]],
                         [pos[0] - axis[0], 
                          pos[1] - axis[1], 
                          pos[2] - axis[2]],
                         [pos[0] + 3 * axis[0], 
                          pos[1] + 3 * axis[1],
                          pos[2] + 3 * axis[2]],
                         [pos[0] + 5 * axis[0], 
                          pos[1] + 5 * axis[1],
                          pos[2] + 5 * axis[2]]], # Point array (the two end
                                                  # points not drawn)
                        None, # Color array (None means use current color)
                        [arrowRadius, arrowRadius, 0, 0] # Radius array
                       )
        else:
            if style:
                print "bug (ignored): unknown _draw_atom_style return value for %r: %r" % (self, style,)
            drawsphere(color, pos, drawrad, level)
        return
    
    def draw_wirespheres(self, glpane, disp, pos, pickedrad):
        #bruce 060315 split this out of self.draw so I can add it to draw_in_abs_coords
        if self._draw_atom_style().startswith('arrowhead-'):
            # compensate for the cone (drawn by draw_atom_sphere in this case) being bigger than the sphere [bruce 070409]
            pickedrad *= debug_pref("Pe pickedrad ratio", Choice([1.8, 1.9, 1.7, 1.0])) ####
        if self.picked: # (do this even if disp == diINVISIBLE or diLINES [bruce comment 050825])
            #bruce 041217 experiment: show valence errors for picked atoms by
            # using a different color for the wireframe.
            # (Since Transmute operates on picked atoms, and leaves them picked,
            #  this will serve to show whatever valence errors it causes. And
            #  showing it only for picked atoms makes it not mess up any images,
            #  even though there's not yet any way to turn this feature off.)
            if self.bad():
                color = ErrorPickedColor
            else:
                color = PickedColor
            drawwiresphere(color, pos, pickedrad) ##e worry about glname hit test if atom is invisible? [bruce 050825 comment]
        #bruce 050806: check valence more generally, and not only for picked atoms.
        if disp != diINVISIBLE: #bruce 050825 added this condition to fix bug 870
            # The above only checks for number of bonds.
            # Now that we have higher-order bonds, we also need to check valence more generally.
            # The check for glpane class is a kluge to prevent this from showing in thumbviews: should remove ASAP.
            #####@@@@@ need to do this in atom.getinfo().
            #e We might need to be able to turn this off by a preference setting; or, only do it in Build mode.
            if glpane.should_draw_valence_errors() and self.bad_valence() and env.prefs[ showValenceErrors_prefs_key ]:
                # Note: the env.prefs check should come last, or changing the pref would gl_update when it didn't need to.
                # [bruce 060315 comment]
                drawwiresphere(pink, pos, pickedrad * 1.08) # experimental, but works well enough for A6.
                #e we might want to not draw this when self.bad() but draw that differently,
                # and optim this when atomtype is initial one (or its numbonds == valence).
        return

    def max_pixel_radius(self): #bruce 070409
        "Return an estimate (upper bound) of the maximum distance from self's center to any pixel drawn for self."
        res = self.selatom_radius() + 0.2
        if self._draw_atom_style().startswith('arrowhead-'):
            res *= 3
        return res
    
    def bad(self): #bruce 041217 experiment; note: some of this is inlined into self.getinfo()
        "is this atom breaking any rules? [note: this is used to change the color of the atom.picked wireframe]"
        if self.element is Singlet:
            # should be correct, but this case won't be used as of 041217 [probably no longer needed even if used -- 050511]
            numbonds = 1
        else:
            numbonds = self.atomtype.numbonds
        return numbonds != len(self.bonds) ##REVIEW: this doesn't check bond valence at all... should it??

    def bad_valence(self): #bruce 050806; should review uses (or inlinings) of self.bad() to see if they need this too ##REVIEW
        "is this atom's valence clearly wrong, considering valences presently assigned to its bonds?"
        # WARNING: keep the code of self.bad_valence() and self.bad_valence_explanation() in sync! 
        #e we might optimize this by memoizing it (in a public attribute), and letting changes to any bond invalidate it.
        bonds = self.bonds
        if self.element is Singlet:
            ok = (len(bonds) == 1)
            return not ok # any open bond valence is legal, for now
        if self.atomtype.numbonds != len(bonds):
            ok = False
            return not ok
        minv, maxv = self.min_max_actual_valence() # min and max reasonable interpretations of actual valence, based on bond types
        want_valence = self.atomtype.valence
        ok = (minv <= want_valence <= maxv)
        return not ok

    def bad_valence_explanation(self): #bruce 050806; revised 060703 ####@@@@ use more widely
        """
        Return the reason self's valence is bad (as a short text string), or '' if it's not bad.

        [TODO: Some callers might want an even shorter string; if so, we'll add an option to ask for that,
         and perhaps implement it by stripping off " -- " and whatever follows that.]
        """
        # WARNING: keep the code of self.bad_valence() and self.bad_valence_explanation() in sync! 
        bonds = self.bonds
        if self.element is Singlet:
            ok = (len(bonds) == 1)
            return (not ok) and "internal error: open bond with wrong number of bonds" or ""
        if self.atomtype.numbonds != len(bonds):
            ok = False
            return (not ok) and "wrong number of bonds" or ""
        minv, maxv = self.min_max_actual_valence() # min and max reasonable interpretations of actual valence, based on bond types
        want_valence = self.atomtype.valence
        ok = (minv <= want_valence <= maxv)
        if not ok:
            if len(self.element.atomtypes) > 1:
                ordiff = " or different atomtype"
            else:
                ordiff = ""
            if maxv < want_valence:
                return "valence too small -- need higher bond orders" + ordiff
            elif minv > want_valence:
                return "valence too large -- need lower bond orders" + ordiff
            else:
                return "internal error in valence-checking code"
        else:
            return ""
        pass

    def min_max_actual_valence(self): #bruce 051215 split this out of .bad and .bad_valence
        """
        Return the pair (minv, maxv) of the min and max reasonable interpretations of self's current valence,
        based on bond types.

        Note: these are actual valence numbers (ints or floats, but single bond is 1.0), NOT v6 values.
        """
        minv = maxv = 0
        for bond in self.bonds:
            minv1, maxv1 = min_max_valences_from_v6(bond.v6)
            minv += minv1
            maxv += maxv1
        return minv, maxv

    def deficient_valence(self): #bruce 051215
        """
        If this atom clearly wants more valence (based on existing bond types),
        return the minimum amount it needs (as an int or float valence number, NOT as a v6).
        Otherwise return 0.
        """
        minv_junk, maxv = self.min_max_actual_valence()
        want_valence = self.atomtype.valence
        if maxv < want_valence:
            return want_valence - maxv
        return 0

    def deficient_v6(self): #bruce 051215
        return valence_to_v6(self.deficient_valence())
    
    def mouseover_statusbar_message(self):
        msg = self.getInformationString()
        more = self.bad_valence_explanation()
        if more:
            msg += " (%s)" % more
        return msg

    def overdraw_with_special_color(self, color, level = None):
        """
        Draw this atom slightly larger than usual with the given
        special color and optional drawlevel, in abs coords.
        """
        #bruce 050324; meant for use in Fuse Chunks mode;
        # also could perhaps speed up Extrude's singlet-coloring #e
        if level is None:
            level = self.molecule.assy.drawLevel
        pos = self.posn() # note, unlike for draw_as_selatom, this is in main model coordinates
        drawrad = self.selatom_radius() # slightly larger than normal drawing radius
        ## drawsphere(color, pos, drawrad, level) # always draw, regardless of display mode
        self.draw_atom_sphere(color, pos, drawrad, level, None, abs_coords = True)
            #bruce 070409 bugfix (draw_atom_sphere); important if it's really a cone
        return
    

    def draw_in_abs_coords(self, glpane, color, useSmallAtomRadius = False): #bruce 050610
        ###@@@ needs to be told whether or not to "draw as selatom"; now it does [i.e. it's misnamed]
        """
        Draw this atom in absolute (world) coordinates,
        using the specified color (ignoring the color it would naturally be drawn with).
        See code comments about radius and display mode (current behavior might not be correct or optimal).
           This is only called for special purposes related to mouseover-highlighting,
        and should be renamed to reflect that, since its behavior can and should be specialized
        for that use. (E.g. it doesn't happen inside display lists; and it need not use glName at all.)
           In this case (Atom) [bruce 050708 new feature], this method (unlike the main draw method) will also
        draw self's bond, provided self is a singlet with a bond which gets drawn, , so that for an "open bond"
        it draws the entire thing (bond plus the "open end"). Corresponding to this, the bond will borrow the glname
        of self whenever it draws itself (with any method). (This only works because bonds have at most one singlet.)
        """
        if self.__killed:
            return # I hope this is always ok...
        level = self.molecule.assy.drawLevel # this doesn't work if atom has been killed!
        pos = self.posn()
        ###@@@ remaining code might or might not be correct (issues: larger radius, display-mode independence)
        
        if useSmallAtomRadius:
            drawrad = self.selatom_small_radius()
        else:
            drawrad = self.selatom_radius() # slightly larger than normal drawing radius
        ## drawsphere(color, pos, drawrad, level)
        self.draw_atom_sphere(color, pos, drawrad, level, None, abs_coords = True)
            # always draw, regardless of display mode
            #bruce 050825 comment: it's probably incorrect to do this even for invisible atoms.
            # This probably caused the "highlighting part" of bug 870, but bug 870 has been fixed
            # by other changes today, but this still might cause other bugs of highlighting
            # otherwise-invisible atoms. Needs review. ###@@@
            # (Indirectly related: drawwiresphere acts like drawsphere for hit-test purposes.)
        if len(self.bonds) == 1 and self.element is Singlet: #bruce 050708 new feature - bond is part of self for highlighting
            dispdef = self.molecule.get_dispdef()
                #bruce 050719 question: is it correct to ignore .display of self and its base atom? ###@@@
                #bruce 060630 guess answer: yes, since howdraw covers it.
            disp, drawradjunk = self.howdraw(dispdef) # (this arg is required)
            if disp in (diBALL, diTUBES):
                self.bonds[0].draw_in_abs_coords(glpane, color)
        #bruce 060315 try to fix disappearing hover highlight when mouse goes over one of our wirespheres.
        # We have to do it in the same coordinate system as the original wirespheres were drawn.
        # (This will only work well if there is also a depth offset, or (maybe) an increased line thickness.
        #  I think there's a depth offset in the calling code, and it does seem to work. Note that it needs
        #  testing for rotated chunks, since until you next modify them, the wirespheres are also drawn rotated.)
        self.molecule.pushMatrix()
        try:
            dispdef = self.molecule.get_dispdef() #e could optimize, since sometimes computed above -- but doesn't matter.
            pos = self.baseposn()
            disp, drawrad = self.howdraw(dispdef)
            if disp == diTUBES:
                pickedrad = drawrad * 1.8 # this code snippet is now shared between draw and draw_in_abs_coords [bruce 060315]
            else:
                pickedrad = drawrad * 1.1
            self.draw_wirespheres(glpane, disp, pos, pickedrad)
        except:
            print_compact_traceback("exception in draw_wirespheres part of draw_in_abs_coords ignored: ")
            pass
        self.molecule.popMatrix()
        return

    def selatom_radius(self, dispdef = None): #bruce 041207, should integrate with draw_as_selatom
        if dispdef is None:
            dispdef = self.molecule.get_dispdef()
        disp, drawrad = self.howdraw(dispdef)
        if self.element is Singlet:
            drawrad *= 1.02
                # increased radius might not be needed, if we would modify the
                # OpenGL depth threshhold criterion used by GL_DEPTH_TEST
                # to overwrite when depths are equal [bruce 041206]
        else:
            if disp == diTUBES:
                drawrad *= 1.7
            else:
                drawrad *= 1.02
        return drawrad


    def selatom_small_radius(self, dispdef = None): #ninad070213 for chunk highlighting
        if dispdef is None:
            dispdef = self.molecule.get_dispdef()
        disp, drawrad = self.howdraw(dispdef)
        if self.element is Singlet:
            drawrad *= 1.02
                # increased radius might not be needed, if we would modify the
                # OpenGL depth threshhold criterion used by GL_DEPTH_TEST
                # to overwrite when depths are equal [bruce 041206]
        else:
            if disp == diTUBES:
                drawrad *= 1.0
               
        return drawrad
        
    def setDisplay(self, disp):
        disp = remap_atom_dispdefs.get(disp, disp) #bruce 060607; error message, if any, should not be done per-atom, ie not here
        #e could we make the following conditional on self.display != disp? I don't know. [bruce 060607 comment]
        self.display = disp
        _changed_otherwise_Atoms[self.key] = self #bruce 060322
        self.molecule.changeapp(1)
        self.changed() # bruce 041206 bugfix (unreported bug); revised, bruce 050509
        # bruce 041109 comment:
        # Atom.setDisplay changes appearance of this atom's bonds,
        # so: do we need to invalidate the bonds? No, they don't store display
        # info, and the geometry related to bond.setup_invalidate has not changed.
        # What about the mols on both ends of the bonds? The changeapp() handles
        # that for internal bonds, and external bonds are redrawn every time so
        # no invals are needed if their appearance changes.

    def howdraw(self, dispdef): # warning: if you add env.prefs[] lookups to this routine, modify selradius_prefs_values!
        """
        Tell how to draw the atom depending on its display mode (possibly
        inherited from dispdef, usually the molecule's effective dispdef).
        An atom's display mode overrides the inherited
        one from the molecule or glpane, but a molecule's color overrides the
        atom's element-dependent one (color is handled in Atom.draw, not here,
        so this is just FYI).
           Return display mode and radius to use, in a tuple (disp, rad).
        For display modes in which the atom is not drawn, such as diLINES or
        diINVISIBLE, we return the same radius as in diBALL; it's up to the
        caller to check the disp we return and decide whether/how to use this
        radius (e.g. it might be used for atom selection in diLINES mode, even
        though the atoms are not shown).
        """
        if dispdef == diDEFAULT: #bruce 041129 permanent debug code, re bug 21
            if debug_flags.atom_debug and 0: #bruce 050419 disable this since always happens for Element Color Prefs dialog
                print "bug warning: dispdef == diDEFAULT in Atom.howdraw for %r" % self
            dispdef = default_display_mode # silently work around that bug [bruce 041206]
        if self.element is Singlet:
            try:
                disp, rad_unused = self.bonds[0].other(self).howdraw(dispdef)
            except:
                # exceptions here (e.g. from bugs causing unbonded singlets)
                # cause too much trouble in other places to be permitted
                # (e.g. in selradius_squared and recomputing the array of them)
                # [bruce 041215]
                disp = default_display_mode
        else:
            if self.display == diDEFAULT:
                disp = dispdef
            else:
                disp = self.display
        
        # Compute "rad"
        if disp == diTUBES: 
            rad = TubeRadius * 1.1
        else:
            #bruce 060307 moved all this into else clause; this might prevent some needless (and rare)
            # gl_updates when all is shown in Tubes but prefs for other dispmodes are changed.
            rad = self.element.rvdw # correct value for diTrueCPK (formerly, default); modified to produce values for other dispmodes
            if disp == diTrueCPK:
                rad = rad * env.prefs[cpkScaleFactor_prefs_key] 
            if disp != diTrueCPK:
                rad = rad * BALL_vs_CPK # all other dispmode radii are based on diBALL radius
            if disp == diBALL:
                rad = rad * env.prefs[diBALL_AtomRadius_prefs_key] 
        return (disp, rad)

    def selradius_prefs_values(): # staticmethod in Atom #bruce 060317 for bug 1639 (and perhaps an analogue for other prefs)
        """
        Return a tuple of all prefs values that are ever used in computing
        any atom's selection radius (by selradius_squared).
        """
        return ( env.prefs[cpkScaleFactor_prefs_key] , env.prefs[diBALL_AtomRadius_prefs_key] ) # both used in howdraw

    selradius_prefs_values = staticmethod( selradius_prefs_values)

    def selradius_squared(self): # warning: if you add env.prefs[] lookups to this routine, modify selradius_prefs_values!
        """
        Return square of desired "selection radius",
        or -1.0 if atom should not be selectable (e.g. invisible).
        This might depend on whether atom is selected (and that
        might even override the effect of invisibility); in fact
        this is the case for this initial implem.
        It also depends on the current display mode of
        self, its mol, and its glpane.
        Ignore self.molecule.hidden and whether self == selatom.
        Note: self.visible() should agree with self.selradius_squared() >= 0.0.
        """
        #bruce 041207. Invals for this are subset of those for changeapp/havelist.
        disp, rad = self.howdraw( self.molecule.get_dispdef() )
        if disp == diINVISIBLE and not self.picked:
            return -1.0
        else:
            return rad ** 2

    def visible(self, dispdef = None): #bruce 041214
        """
        Say whether this atom is currently visible, for purposes of selection.
        Note that this depends on self.picked, and display modes of self, its
        chunk, and its glpane, unless you pass disp (for speed) which is treated
        as the chunk's (defined or inherited) display mode.
        Ignore self.molecule.hidden and whether self == selatom.
        Return a correct value for singlets even though no callers [as of 041214]
        would care what we returned for them.
        Note: self.visible() should agree with self.selradius_squared() >= 0.0.
        """
        if self.picked:
            return True # even for invisible atoms
        if self.element is Singlet:
            disp = self.bonds[0].other(self).display
        else:
            disp = self.display
        if disp == diDEFAULT: # usual case; use dispdef
            # (note that singlets are assumed to reside in same chunks as their
            # real neighbor atoms, so the same dispdef is valid for them)
            if dispdef is None:
                disp = self.molecule.get_dispdef()
            else:
                disp = dispdef
        return not (disp == diINVISIBLE)

    # == file input/output methods (ideally to be refactored out of this class)
    
    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """
        [compatible with Node.writemmp, though we're not a subclass of Node]
        """
        num_str = mapping.encode_next_atom(self) # (note: pre-050322 code used an int here)
        disp = mapping.dispname(self.display) # note: affected by mapping.sim flag
        posn = self.posn() # might be revised below
        eltnum = self.element.eltnum # might be revised below
        if mapping.sim and self.element is Singlet:
            # special case for singlets in mmp files meant only for simulator:
            # pretend we're a Hydrogen, and revise posn and eltnum accordingly
            # (for writing only, not stored in our attrs)
            # [bruce 050404 to help fix bug 254]
            eltnum = Hydrogen.eltnum
            posn = self.ideal_posn_re_neighbor( self.singlet_neighbor(), pretend_I_am = Hydrogen ) # see also self.sim_posn()
            disp = "openbond" # kluge, meant as a comment in the file #bruce 051115 changed this from "singlet" to "openbond"
            #bruce 051209 for history message in runSim (re bug 254):
            stats = mapping.options.get('dict_for_stats')
            if stats is not None: # might be {}
                nsinglets_H = stats.setdefault('nsinglets_H', 0)
                nsinglets_H += 1
                stats['nsinglets_H'] = nsinglets_H
        xyz = posn * 1000
            # note, xyz has floats, rounded below (watch out for this
            # if it's used to make a hash) [bruce 050404 comment]
        print_fields = (num_str, eltnum,
           int(xyz[0]), int(xyz[1]), int(xyz[2]), disp)
        mapping.write("atom %s (%d) (%d, %d, %d) %s\n" % print_fields)
        # mark 2007-08-16: write dnaBaseName info record.
        dnaBaseName = self.getDnaBaseName()
        if dnaBaseName:
            mapping.write( "info atom dnaBaseName = %s\n" % dnaBaseName )
        # Write dnaStrandName info record (only for Pe atoms). Mark 2007-09-04
        dnaStrandName = self.getDnaStrandName()
        if dnaStrandName:
            mapping.write( "info atom dnaStrandName = %s\n" % dnaStrandName )
        #bruce 050511: also write atomtype if it's not the default
        atype = self.atomtype_iff_set()
        if atype is not None and atype is not self.element.atomtypes[0]:
            mapping.write( "info atom atomtype = %s\n" % atype.name )
        # write only the bonds which have now had both atoms written
        #bruce 050502: write higher-valence bonds using their new mmp records,
        # one line per type of bond (only if we need to write any bonds of that type)
        bldict = {} # maps valence to list of 0 or more atom-encodings for bonds of that valence we need to write
        ## bl = [] # (note: in pre-050322 code bl held ints, not strings)
        bonds_with_direction = []
        for b in self.bonds:
            oa = b.other(self)
            #bruce 050322 revised this:
            oa_code = mapping.encode_atom(oa) # None, or true and prints as "atom number string"
            if oa_code:
                # we'll write this bond, since both atoms have been written
                valence = b.v6
                bl = bldict.setdefault(valence, [])
                bl.append(oa_code)
                if b._direction:
                    bonds_with_direction.append(b)
        bondrecords = bldict.items()
        bondrecords.sort() # by valence
        for valence, atomcodes in bondrecords:
            assert len(atomcodes) > 0
            mapping.write( bonds_mmprecord( valence, atomcodes ) + "\n")
        for bond in bonds_with_direction:
            mapping.write( bond.mmprecord_bond_direction(self, mapping) + "\n") #bruce 070415
        return

    def readmmp_info_atom_setitem( self, key, val, interp ): #bruce 050511
        """
        Reads an atom info record from the MMP file.
        
        @see: The docstring of an analogous method, such as
              L{Node.readmmp_info_leaf_setitem()}.
        """
        if key == ['atomtype']:
            # val should be the name of one of self.element's atomtypes (not an error if unrecognized)
            try:
                atype = self.element.find_atomtype(val)
            except:
                # didn't find it. (#e We ought to have a different API so a real error could be distinguished from that.)
                if debug_flags.atom_debug:
                    print "atom_debug: fyi: info atom atomtype (in class Atom) with unrecognized atomtype %r (not an error)" % (val,)
                pass
            else:
                self.set_atomtype_but_dont_revise_singlets( atype)
                    # don't add singlets, since this mmp record comes before the bonds, including bonds to singlets
        
        elif key == ['dnaBaseName']: # Mark 2007-08-16
            try:
                self.setDnaBaseName(val)
            except:
                print "Found Atom info record with problem: "\
                      "dnaBaseName = %r, "\
                      "atom = %r (continuing)" % (val, self.element.name)
                pass
        
        elif key == ['dnaStrandName']: # Mark 2007-09-04
            try:
                self.setDnaStrandName(val)
            except:
                print "Found Atom info record with problem: "\
                      "dnaStrandName = %r, "\
                      "atom = %r (continuing)" % (val, self.element.name)
                pass
                 
        else:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info atom (in class Atom) with "\
                      "unrecognized key %r (not an error)" % (key,)
        return
    
    def writepov(self, file, dispdef, col):
        """
        write to a povray file:  draw a single atom
        """
        color = col or self.drawing_color()
        disp, rad = self.howdraw(dispdef)
        if disp in [diTrueCPK, diBALL]:
            file.write("atom(" + povpoint(self.posn()) +
                       "," + str(rad) + "," +
                       Vector3ToString(color) + ")\n")
        if disp == diTUBES:
            ###e this should be merged with other case, and should probably
            # just use rad from howdraw [bruce 041206 comment]
            file.write("atom(" + povpoint(self.posn()) +
                       "," + str(rad) + "," +
                       Vector3ToString(color) + ")\n")
        return

    def writepdb(self, file, atomSerialNumber, chainId):
        # REFACTORING DESIRED: most of this ought to be split out
        # into a helper function or wrapper class in files_pdb.py.
        # (And similarly with writepov, writemdl, writemmp, etc.)
        # [bruce 080122 comment]
        """
        Write a PDB ATOM record for this atom into I{file}.
        
        @param file: The PDB file to write the ATOM record to.
        @type  file: file
        
        @param atomSerialNumber: A unique number for this atom.
        @type  atomSerialNumber: int
        
        @param chainId: The chain id. It is a single character. See the PDB
                        documentation for the ATOM record more information.
        @type  chainId: str
        
        @note: If you edit the ATOM record, be sure to to test QuteMolX.
                    
        @see: U{B{ATOM Record Format}<http://www.wwpdb.org/documentation/format23/sect9.html#ATOM>}
        """
        space = " "
        # Begin ATOM record ----------------------------------
        # Column 1-6: "ATOM  " (str)
        atomRecord = "ATOM  "
        # Column 7-11: Atom serial number (int)
        atomRecord += "%5d" % atomSerialNumber
        # Column 12: Whitespace (str)
        atomRecord += "%1s" % space
        # Column 13-16 Atom name (str)
        atomRecord += "%-4s" % self.element.symbol
        # Column 17: Alternate location indicator (str) *unused*
        atomRecord += "%1s" % space
        # Column 18-20: Residue name - unused (str)
        atomRecord += "%3s" % space
        # Column 21: Whitespace (str)
        atomRecord += "%1s" % space
        # Column 22: Chain identifier - single letter (str) 
        # This has been tested with 35 chunks and still works in QuteMolX.
        atomRecord += "%1s" % chainId.upper()
        # Column 23-26: Residue sequence number (int) *unused*.
        atomRecord += "%4s" % space
        # Column 27: Code for insertion of residues (AChar) *unused*
        atomRecord += "%1s" % space
        # Column 28-30: Whitespace (str)
        atomRecord += "%3s" % space
        # Get atom XYZ coordinate
        _xyz = self.posn()
        # Column 31-38: X coord in Angstroms (float 8.3)
        atomRecord += "%8.3f" % float(_xyz[0])
        # Column 39-46: Y coord in Angstroms (float 8.3)
        atomRecord += "%8.3f" % float(_xyz[1])
        # Column 47-54: Z coord in Angstroms (float 8.3)
        atomRecord += "%8.3f" % float(_xyz[2])
        # Column 55-60: Occupancy (float 6.2) *unused*
        atomRecord += "%6s" % space
        # Column 61-66: Temperature factor. (float 6.2) *unused*
        atomRecord += "%6s" % space
        # Column 67-76: Whitespace (str)
        atomRecord += "%10s" % space
        # Column 77-78: Element symbol, right-justified (str) *unused*
        atomRecord += "%2s" % space
        # Column 79-80: Charge on the atom (str) *unused*
        atomRecord += "%2s\n" % space
        # End ATOM record ----------------------------------
        
        file.write(atomRecord)

        return
    
    def writemdl(self, alist, f, dispdef, col):
        """
        write to a MDL file
        """
        # By Chris Phoenix and Mark for John Burch [04-12-03]
        color = col or self.drawing_color()
        disp, radius = self.howdraw(dispdef)
        xyz=map(float, A(self.posn()))
        rgb=map(int,A(color)*255)
        atnum = len(alist) # current atom number        
        alist.append([xyz, radius, rgb])
        
        # Write spline info for this atom
        atomOffset = 80*atnum
        (x,y,z) = xyz
        for spline in range(5):
            f.write("CPs=8\n")
            for point in range(8):
                index = point+spline*8
                (px,py,pz)=marks[index]
                px = px*radius + x; py = py*radius + y; pz = pz*radius + z
                if point == 7:
                    flag = "3825467397"
                else:
                    flag = "3825467393"
                f.write("%s 0 %d\n%f %f %f\n%s%s"%
                           (flag, index+19+atomOffset, px, py, pz,
                            filler, filler))
        
        for spline in range(8):
            f.write("CPs=5\n")
            for point in range(5):
                index = point+spline*5
                f.write("3825467393 1 %d\n%d\n%s%s"%
                           (index+59+atomOffset, links[index]+atomOffset,
                            filler, filler))
        return

    # ==
    
    def getinfo(self): # [mark 2004-10-14]
        """
        Return information about the selected atom for the msgbar
        """
        # bruce 041217 revised XYZ format to %.2f, added bad-valence info
        # (for the same atoms as self.bad(), but in case conditions are added to
        #  that, using independent code).
        # bruce 050218 changing XYZ format to %.3f (after earlier discussion with Josh).
        
        if self is self.molecule.assy.ppa2:
            return
            
        xyz = self.posn()

        atype_string = ""
        if len(self.element.atomtypes) > 1: #bruce 050511
            atype_string = "(%s) " % self.atomtype.name

        ainfo = ("Atom %s %s[%s] [X = %.3f] [Y = %.3f] [Z = %.3f]" % \
            ( self, atype_string, self.element.name, xyz[0], xyz[1], xyz[2] ))
        
        # ppa2 is the previously picked atom.  ppa3 is the atom picked before ppa2.
        # They are both reset to None when entering SELATOMS mode.
        # Include the distance between self and ppa2 in the info string.
        if self.molecule.assy.ppa2:
            try:
                ainfo += (". Distance between %s-%s is %.3f Angstroms." % \
                    (self, self.molecule.assy.ppa2, vlen(self.posn()-self.molecule.assy.ppa2.posn()))) # fix bug 366-2 ninad060721
            except:
                print_compact_traceback("bug, fyi: ignoring exception in atom distance computation: ") #bruce 050218
                pass
            
            # Include the angle between self, ppa2 and ppa3 in the info string.
            if self.molecule.assy.ppa3:
                try:
                    # bruce 050218 protecting angle computation from exceptions
                    # (to reduce severity of undiagnosed bug 361).
                    #bruce 050906 splitting angle computation into separate function.
                    ###e its inaccuracy for angles near 0 and 180 degrees should be fixed!
                    ang = atom_angle_radians( self, self.molecule.assy.ppa2, self.molecule.assy.ppa3 ) * 180/math.pi
                    ainfo += (" Angle for %s-%s-%s is %.2f degrees." %\
                        (self, self.molecule.assy.ppa2, self.molecule.assy.ppa3, ang))
                except:
                    print_compact_traceback("bug, fyi: ignoring exception in atom angle computation: ") #bruce 050218
                    pass
            
            # ppa3 is ppa2 for next atom picked.
            self.molecule.assy.ppa3 = self.molecule.assy.ppa2 
        
        # ppa2 is self for next atom picked.
        self.molecule.assy.ppa2 = self
            
        if len(self.bonds) != self.atomtype.numbonds:
            # I hope this can't be called for singlets! [bruce 041217]
            ainfo += fix_plurals(" (has %d bond(s), should have %d)" % \
                                          (len(self.bonds), self.atomtype.numbonds))
        elif self.bad_valence(): #bruce 050806
            msg = self.bad_valence_explanation()
            ainfo += " (%s)" % msg
        
        return ainfo
    
    def getInformationString(self):
        """
        If a standard atom, return a string like C26(sp2) with atom name and
        atom hybridization type, but only include the type if more than one is 
        possible for the atom's element and the atom's type is not the default 
        type for that element.
        
        If a PAM Ss or Sj atom, returns a string like Ss28(A) with atom name
        and dna base name.

        If a PAM-5 Pe atom, include the DNA strand name. (Note that Pe is a
        deprecated element, so this feature will soon be useless.)
        """
        res = str(self)
        if self.atomtype is not self.element.atomtypes[0]:
            res += "(%s)" % self.atomtype.name
        if self.getDnaBaseName():
            res += "(%s)" % self.dnaBaseName
        if self.getDnaStrandName():
            res += "(%s)" % self.dnaStrandName
        return res

    def getToolTipInfo(self, glpane,
                       isAtomPosition, isAtomChunkInfo,
                       isAtomMass, atomDistPrecision):
        """
        Returns atom's basic info string for the dynamic tooltip
        """
        # CLEANUP NEEDED: # atom self glpane.selobj
        # I think glpane.selobj in this method is supposed to be self
        # and should be replaced with self (if this guess is confirmed).
        # [bruce 080130/080206 comment]

        atom = glpane.selobj # should replace with self [bruce 080206]

        atomStr        = atom.getInformationString()
        elementNameStr = " [" + atom.element.name + "]"

        atomInfoStr = atomStr + elementNameStr

        if atom.display:
            # show display style of atoms that have one [bruce 080206]
            atomInfoStr += "<br>" + "display style: %s" % atom.atom_dispLabel() 

        if atom._dna_updater__error: #bruce 080130
            msg = atom.dna_updater_error_string(newline = '<br>')
            atomInfoStr += "<br>" + orangemsg(msg)
        
        if isAtomPosition:
            xyz = atom.posn()
            xPosn = str(round(xyz[0], atomDistPrecision))
            yPosn = str(round(xyz[1], atomDistPrecision))
            zPosn = str(round(xyz[2], atomDistPrecision))
            atomposn = ("<font color=\"#0000FF\">X:</font> %s<br><font color=\"#0000FF\">Y:</font> %s<br>"\
            "<font color=\"#0000FF\">Z:</font> %s" %(xPosn, yPosn, zPosn))
            atomInfoStr += "<br>" + atomposn
            
        if isAtomChunkInfo:
            if atom is not None:
                atomChunkInfo = "<font color=\"#0000FF\">Parent Chunk:</font> [" + atom.molecule.name + "]"
                atomInfoStr += "<br>" + atomChunkInfo

        if isAtomMass:
            atomMass = "<font color=\"#0000FF\">Mass: </font>" + str(atom.element.mass) + "  x 10-27 Kg"
            atomInfoStr += "<br>" + atomMass
                
        #if isRVdw:
           # rVdw = "<font color=\"#0000FF\">Vdw:Radius:  </font>" + str(atom.element.rvdw) + "A"
                
        return atomInfoStr

    def atom_dispLabel(self): #bruce 080206
        """
        Return the full name of self's individual (single-atom) display style,
        corresponding to self.display (a small int which encodes it).
        (If self.display is not recognized, just return str(self.display).)
        
        Normally self.display is 0 (diDEFAULT) and this method returns "Default"
        (which means a display style from self's context will be used when
         self is drawn).
        """
        self.display # make sure this is set
        try:
            return dispLabel[self.display]
            # usually "Default" for self.display == diDEFAULT == 0
        except IndexError:
            return str(self.display)
        pass

    # ==
    
    def checkpick(self, p1, v1, disp, r=None, iPic=None):
        """
        Selection function for atoms: [Deprecated! bruce 041214]
        Check if the line through point p1 in direction v1 goes through the
        atom (treated as a sphere with the same radius it would be drawn with,
        which might depend on disp, or with the passed-in radius r if that's
        supplied). If not, or if the atom is a singlet, or if not iPic and the
        atom is already picked, return None. If so, return the distance along
        the ray (from p1 towards v1) of the point closest to the atom center
        (which might be 0.0, which is false!), or None if that distance is < 0.
        """
        #bruce 041206 revised docstring to match code
        #bruce 041207 comment: the only call of checkpick is from assy.findpick
        if self.element is Singlet: return None
        if not r:
            disp, r = self.howdraw(disp)
        # bruce 041214:
        # this is surely bad in only remaining use (depositMode.getCoords):
        ## if self.picked and not iPic: return None 
        dist, wid = orthodist(p1, v1, self.posn())
        if wid > r: return None
        if dist<0: return None
        return dist

    # ==
    
    def pick(self):
        """
        make the atom selected
        """
        if self.element is Singlet:
            return

        if self.filtered():
            return # mark 060303. [note: bruce 060321 has always thought it was nonmodular to check this here]
            #bruce 060331 comment: we can't move this inside the conditional to optimize it, since we want it to affect
            # whether we set picked_time, but we want to set that even for already-picked atoms.
            # (Which are reasons of dubious value if this missed optim is important (don't know if it is), but are real ones.)
            
        self._picked_time = self.molecule.assy._select_cmd_counter #bruce 051031, for ordering selected atoms; two related attrs
        if not self.picked:
            self.picked = True
            _changed_picked_Atoms[self.key] = self #bruce 060321 for Undo (or future general uses)
            self._picked_time_2 = self.molecule.assy._select_cmd_counter #bruce 051031
            self.molecule.assy.selatoms[self.key] = self
                #bruce comment 050308: should be ok even if selatoms recomputed for assy.part
            self.molecule.changeapp(1)
                #bruce 060321 comment: this needs its arg of 1, since self.selradius_squared()
                # can be affected (if self is invisible). Further review might determine this is
                # not required (if it's impossible to ever pick invisible atoms), or we might
                # optim to see if this actually *does* change selradius_squared. Not sure if
                # that potential optim is ever significant.
            # bruce 041227 moved message from here to one caller, pick_at_event
            #bruce 050308 comment: we also need to ensure that it's ok to pick atoms
            # (wrt selwhat), and change current selection group to include self.molecule
            # if it doesn't already. But in practice, all callers might be ensuring these
            # conditions already (this is likely to be true if pre-assy/part code was correct).
            # In particular, atoms are only picked by user in glpane or perhaps by operations
            # on current part, and in both cases the picked atom would be in the current part.
            # If atoms can someday be picked from the mtree (directly or by selecting a jig that
            # connects to them), this will need review.
            self.molecule.changed_selection() #bruce 060227
        return

    _picked_time = _picked_time_2 = -1
    def pick_order(self): #bruce 051031
        """
        Return something which can be sorted to determine the order in which atoms were selected; include tiebreakers.
        Legal to call even if self has never been selected or is not currently selected,
        though results will not be very useful then.
        """
        return (self._picked_time, self._picked_time_2, self.key)
    
    def unpick(self, filtered = True): #bruce 060331 adding filtered = False option, as part of fixing bug 1796
        """
        Make the atom (self) unselected, if the selection filter permits this or if filtered = False.
        """
        # note: this is inlined (perhaps with filtered = False, not sure) into assembly.unpickatoms (in ops_select.py)
        # bruce 041214: singlets should never be picked, so Singlet test is not needed,
        # and besides if a singlet ever *does* get picked (due to a bug) you should let
        # the user unpick it!
        ## if self.element is Singlet: return 
        
        if self.picked:        
            if filtered and self.filtered():
                return  # mark 060303.
                # [note: bruce 060321 has always thought it was nonmodular to check this here]
                # [and as of sometime before 060331 it turns out to cause bug 1796]
                #bruce 060331 moved this inside 'if picked', as a speed optimization
            try:
                #bruce 050309 catch exceptions, and do this before picked=0
                # so that if selatoms is recomputed now, the del will still work
                # (required by upcoming "assy/part split")
                del self.molecule.assy.selatoms[self.key]
            except:
                if debug_flags.atom_debug:
                    print_compact_traceback("atom_debug: Atom.unpick finds atom not in selatoms: ")
            self.picked = False
            _changed_picked_Atoms[self.key] = self #bruce 060321 for Undo (or future general uses)
            # note: no need to change self._picked_time -- that would have no effect unless
            # we later forget to set it when atom is picked, and if that can happen,
            # it's probably better to use a prior valid value than -1. [bruce 051031]
            self.molecule.changeapp(1) #bruce 060321 comment: this needs its arg of 1; see comment in self.pick().
            self.molecule.changed_selection() #bruce 060227
        return
    
    def copy(self): #bruce 041116
        """
        Public method: copy an atom, with no special assumptions;
        new atom is not in any mol but could be added to one using mol.addatom.
        """
        nuat = Atom(self, self.posn(), None) #bruce 050524: pass self so its atomtype is copied
        nuat.display = self.display
            # no need in new atoms for anything like _changed_otherwise_Atoms[nuat.key] = nuat #bruce 060322 guess ###@@@ #k
        nuat.info = self.info # bruce 041109, needed by extrude and other future things; revised 050524
        return nuat

    def set_info(self, newinfo): #bruce 060322
        self.info = newinfo
        _changed_structure_Atoms[self.key] = self
        return
    
    def break_unmade_bond(self, origbond, origatom): #bruce 050524
        """
        Add singlets (or do equivalent invals) as if origbond was copied from origatom
        onto self (a copy of origatom), then broken; uses origatom
        so it can find the other atom and know bond direction in space
        (it assumes self might be translated but not rotated, wrt origatom).
        For now this works like mol.copy used to, but later it might "inval singlets" instead.
        """
        # compare to code in Bond.unbond() (maybe merge it? ####@@@@ need to inval things to redo singlets sometimes?)
        a = origatom
        b = origbond
        numol = self.molecule
        x = Atom('X', b.ubp(a), numol) ###k verify Atom.__init__ makes copy of posn, not stores original (tho orig ok if never mods it)
        na = self ## na = ndix[a.key]
        bond_copied_atoms(na, x, origbond, origatom) # same properties as origbond... sensible in all cases?? ##k
        return
        
    def unbond(self, b, make_bondpoint = True):
        """
        Private method (for use mainly by bonds); remove bond b from self and
        usually replace it with a singlet (which is returned). Details:
           Remove bond b from self (error if b not in self.bonds).
        Note that bonds are compared with __eq__, not 'is', by 'in' and 'remove'.
        Only call this when b will be destroyed, or "recycled" (by bond.rebond);
        thus no need to invalidate the bond b itself -- caller must do whatever
        inval of bond b is needed (which is nothing, if it will be destroyed).
           Then replace bond b in self.bonds with a new bond to a new singlet,
        unless self or the old neighbor atom is a singlet, or unless make_bondpoint
        is false. Return the new singlet, or None if one was not created.
        Do all necessary invalidations of Chunks, and self._changed_structure(),
        BUT NOT OF b (see above). 
           If self is a singlet, kill it (singlets must always have one bond).
           As of 041109, this is called from Atom.kill of the other atom,
        and from bond.bust, and [added by bruce 041109] from bond.rebond.
           As of 050727, newly created open bonds have same bond type as the
        removed bond.
        """
        # [obsolete comment: Caller is responsible for shakedown
        #  or kill (after clearing externs) of affected molecules.]
        
        # code and docstring revised by bruce 041029, 041105-12

        self._changed_structure() #bruce 050725
        
        b.invalidate_bonded_mols() #e more efficient if callers did this
        
        try:
            self.bonds.remove(b)
            # note: _changed_structure is done just above
        except ValueError: # list.remove(x): x not in list
            # this is always a bug in the caller, but we catch it here to
            # prevent turning it into a worse bug [bruce 041028]
            msg = "fyi: Atom.unbond: bond %r should be in bonds %r\n of atom %r, " \
                  "but is not:\n " % (b, self.bonds, self)
            print_compact_traceback(msg)
        # normally replace an atom (bonded to self) with a singlet,
        # but don't replace a singlet (at2) with a singlet,
        # and don't add a singlet to another singlet (self).
        if self.element is Singlet:
            if not self.bonds:
                self.kill() # bruce 041115 added this and revised all callers
            else:
                print "fyi: bug: unbond on a singlet %r finds unexpected bonds left over in it, %r" % (self,self.bonds)
                # don't kill it, in this case [bruce 041115; I don't know if this ever happens]
            return None
        if not make_bondpoint:
            #bruce 070601 new feature
            # WARNING [mild; updated 070602]: I'm not 100% sure this does sufficient invals.
            # I added it for Make Crossover and wondered if it caused the Undo bug
            # triggered by that, but that bug turned out to have a different cause,
            # and this option is still used in that command without triggering that bug.
            # So it can be presumed safe for now.
            return None
        at2 = b.other(self)
        if at2.element is Singlet:
            return None
        if 1:
            #bruce 060327 optim of chunk.kill: if we're being killed right now, don't make a new bondpoint
            import Utility
            if self._will_kill == Utility._will_kill_count:
                if debug_1779:
                    print "debug_1779: self._will_kill %r == Utility._will_kill_count %r" % \
                      ( self._will_kill , Utility._will_kill_count )
                return None
        if self.__killed:
            #bruce 080208 new feature (should never happen)
            msg = "bug: killed atom %r still had bond %r, being unbonded now" % \
                  ( atom, b )
            print msg
            return None
        if debug_1779:
            print "debug_1779: Atom.unbond on %r is making X" % self
        x = Atom('X', b.ubp(self), self.molecule) # invals mol as needed
        #bruce 050727 new feature: copy the bond type from the old bond (being broken) to the new open bond that replaces it
        bond_copied_atoms( self, x, b, self)
        ## self.molecule.bond(self, x) # invals mol as needed
        return x # new feature, bruce 041222

    def get_neighbor_bond(self, neighbor):
        """
        Return the bond to a neighboring atom, or None if none exists.
        """
        for b in self.bonds:
            ## if b.other(self) == neighbor: could be faster [bruce 050513]:
            if b.atom1 is neighbor or b.atom2 is neighbor:
                return b
        return None
            
    def hopmol(self, numol): #bruce 041105-041109 extensively revised this
        """
        If this atom is not already in molecule numol, move it
        to molecule numol. (This only changes the owning molecule -- it doesn't
        change this atom's position in space!) Also move its singlet-neighbors.
        Do all necessary invalidations of old and new molecules,
        including for this atom's bonds (both internal and external),
        since some of those bonds might change from internal to external
        or vice versa, which changes how they need to be drawn.
        """
        # bruce 041222 removed side effect on self.picked
        if self.molecule is numol:
            return
        self.molecule.delatom(self) # this also invalidates our bonds
        numol.addatom(self)
        for atm in self.singNeighbors():
            assert self.element is not Singlet # (only if we have singNeighbors!)
                # (since hopmol would infrecur if two singlets were bonded)
            atm.hopmol(numol)
        return
    
    def neighbors(self):
        """
        return a list of all atoms (including singlets) bonded to this one
        """
        return map((lambda b: b.other(self)), self.bonds)
    
    def realNeighbors(self):
        """
        return a list of the real atoms (not singlets) bonded to this atom
        """
        return filter(lambda atm: atm.element is not Singlet, self.neighbors())
    
    def singNeighbors(self): #e when we have only one branch again, rename this singletNeighbors or bondpointNeighbors
        """
        return a list of the singlets bonded to this atom
        """
        return filter(lambda atm: atm.element is Singlet, self.neighbors())
    
    def baggage_and_other_neighbors(self): #bruce 051209
        """
        Return a list of the baggage bonded to this atom (monovalent neighbors which should be dragged along with it),
        and a list of the others (independent neighbors). Special case: in H2 (for example) there is no baggage
        (so that there is some way to stretch the H-H bond); but singlets are always baggage, even in HX.
        """
        nn = self.neighbors()
        if len(nn) == 1:
            # special case: no baggage unless neighbor is a singlet
            if nn[0].element is Singlet:
                return nn, []
            else:
                return [], nn
        baggage = []
        other = []
        for atm in nn:
            if len(atm.bonds) == 1:
                baggage.append(atm)
            else:
                other.append(atm)
        return baggage, other

    def baggageNeighbors(self): #bruce 051209
        baggage, other_unused = self.baggage_and_other_neighbors()
        return baggage
        
    def deleteBaggage(self): #mark 060129.
        """
        Deletes any monovalent atoms connected to self.  
        """
        for a in self.baggageNeighbors():
            a.kill()

    def mvElement(self, elt, atomtype = None): #bruce 050511 added atomtype arg
        """
        [Public low-level method:]
        Change the element type of this atom to element elt
        (an element object for a real element, not Singlet),
        and its atomtype to atomtype (which if provided must be an atomtype for elt),
        and do the necessary invalidations (including if the
        *prior* element type was Singlet).
           Note: this does not change any atom or singlet positions, so callers
        wanting to correct the bond lengths need to do that themselves.
        It does not even delete or add extra singlets to match the new element
        type; for that, use Atom.Transmute.
        """
        if atomtype is None:
            atomtype = elt.atomtypes[0]
            # Note: we do this even if self.element is elt and self.atomtype is not elt.atomtypes[0] !
            # That is, passing no atomtype is *always* equivalent to passing elt's default atomtype,
            # even if this results in changing this atom's atomtype but not its element.
        assert atomtype.element is elt
        if debug_flags.atom_debug:
            if elt is Singlet: #bruce 041118
                # this is unsupported; if we support it it would require
                # moving this atom to its neighbor atom's chunk, too
                # [btw we *do* permit self.element is Singlet before we change it]
                print "atom_debug: fyi, bug?: mvElement changing %r to a singlet" % self
        if self.atomtype_iff_set() is atomtype:
            assert self.element is elt # i.e. assert that self.element and self.atomtype were consistent
            if debug_flags.atom_debug: #bruce 050509
                print_compact_stack( "atom_debug: fyi, bug?: mvElement changing %r to its existing element and atomtype" % self )
            return #bruce 050509, not 100% sure it's correct, but if not, caller probably has a bug (eg relies on our invals)
        # now we're committed to doing the change
        if (self.element is Singlet) != (elt is Singlet):
            # set of singlets is changing
            #bruce 050224: fix bug 372 by invalidating singlets
            self.molecule.invalidate_attr('singlets')
        self.changed() #bruce 050509
        self.element = elt
        self.atomtype = atomtype
            # note: we have to set self.atomtype directly -- if we used set_atomtype,
            # we'd have infrecur since it calls *us*! [#e maybe this should be revised??]
            # (would it be ok to call set_atomtype_but_dont_revise_singlets?? #k)
        for b in self.bonds:
            b.setup_invalidate()
        self.molecule.changeapp(1)
        # no need to invalidate shakedown-related things, I think [bruce 041112]
        self._changed_structure() #bruce 050627
        return

    def changed(self): #bruce 050509; perhaps should use more widely
        mol = self.molecule
        if mol is None: return #k needed??
        mol.changed()
        return

    def killed(self): #bruce 041029; totally revised by bruce 050702
        """
        (Public method)
        Report whether an atom has been killed.
        """
        # Note: some "friend code" inlines this method for speed
        # (and omits the debug code). To find it, search for _Atom__killed
        # (the mangled version of __killed). [bruce 071018 comment]
        if debug_flags.atom_debug: # this cond is for speed
            mol = self.molecule
            from chunk import _nullMol
            better_alive_answer = mol is not None and self.key in mol.atoms and mol is not _nullMol ##e and mol is not killed???
            if (not not better_alive_answer) != (not self.__killed):
                if debug_flags.atom_debug:
                    #bruce 060414 re bug 1779, but it never printed for it (worth keeping in for other bugs)
                    #bruce 071018 fixed typo of () after debug_flags.atom_debug -- could that be why it never printed it?!?
                    print "debug: better_alive_answer is %r but (not self.__killed) is %r" % (better_alive_answer , not self.__killed)
        return self.__killed
    
    def killed_with_debug_checks(self): # renamed by bruce 050702; was called killed(); by bruce 041029
        """
        (Public method)
        Report whether an atom has been killed,
        but do lots of debug checks and bug-workarounds
        (whether or not ATOM_DEBUG is set).
           Details: For an ordinary atom, return False.
        For an atom which has been properly killed, return True.
        For an atom which has something clearly wrong with it,
        print an error message, try to fix the problem,
        effectively kill it, and return True.
        Don't call this on an atom still being initialized.
        """
        try:
            killed = not (self.key in self.molecule.atoms)
            if killed:
                assert self.__killed == 1
                assert not self.picked
                from chunk import _nullMol
                assert self.molecule is _nullMol or self.molecule is None
                # thus don't do this: assert not self.key in self.molecule.assy.selatoms
                assert not self.bonds
                assert not self.jigs
            else:
                assert self.__killed == 0
            return killed
        except:
            print_compact_traceback("fyi: Atom.killed detects some problem" \
                " in atom %r, trying to work around it:\n " % self )
            try:
                self.__killed = 0 # make sure kill tries to do something
                _changed_parent_Atoms[self.key] = self
                self.kill()
            except:
                print_compact_traceback("fyi: Atom.killed: ignoring" \
                    " exception when killing atom %r:\n " % self )
            return True
        pass # end of Atom.killed_with_debug_checks()

    def _prekill(self, val): #bruce 060328; usually inlined (but was tested when first written)
        self._will_kill = val
        return
        
    def kill(self):
        """
        Public method:
        kill an atom: unpick it, remove it from its jigs, remove its bonds,
        then remove it from its molecule. Do all necessary invalidations.
        (Note that molecules left with no atoms, by this or any other op,
        will themselves be killed.)
        """        
        if debug_1779:
            print "debug_1779: Atom.kill on %r" % self
        if self.__killed:
            if not self.element is Singlet:
                print_compact_stack("fyi: atom %r killed twice; ignoring:\n" % self)
            else:
                # Note: killing a selected mol, using Delete key, kills a lot of
                # singlets twice; I guess it's because we kill every atom
                # and singlet in mol, but also kill singlets of killed atoms.
                # So I'll declare this legal, for singlets only. [bruce 041115]
                pass
            return

        self.atomtype #bruce 080208 bugfix of bugs which complain about
            # "reguess_atomtype of killed atom" in a console print:
            # make sure atomtype is set, since it's needed when neighbor atom
            # makes a bondpoint (since bond recomputes geometry all at once).
            # (I don't know whether it needs to be set *correctly*, so we might
            # optim by setting it to its default, if analysis shows this is ok.
            # But it seems likely that this choice does affect the final
            # position of the created bondpoint on the neighbor.)
            # The reason this bug is rare is that most killed atoms were alive
            # long enough for something to need their atomtype (e.g. to draw
            # their bonds). But when generators immediately kill some atoms
            # they temporarily make or read, we can have this bug.
            # The above is partly guessed; we'll see if this really fixes
            # those bugs.
        
        self.__killed = 1 # do this now, to reduce repeated exceptions (works??)
        _changed_parent_Atoms[self.key] = self
        # unpick
        try:
            self.unpick(filtered = False) #bruce 041029
                #bruce 060331 adding filtered = False (and implementing it in unpick) to fix bug 1796
        except:
            print_compact_traceback("fyi: Atom.kill: ignoring error in unpick: ")
            pass
        # bruce 041115 reordered everything that follows, so it's safe to use
        # delatom (now at the end, after things which depend on self.molecule),
        # since delatom resets self.molecule to None.
        
        # josh 10/26 to fix bug 85 - remove from jigs
        for j in self.jigs[:]: #bruce 050214 copy list as a precaution
            try:
                j.remove_atom(self)
                # [bruce 050215 comment: this might kill the jig (if it has no
                #  atoms left), and/or it might remove j from self.jigs, but it
                #  will never recursively kill this atom, so it should be ok]
            except:
                # does this ever still happen? TODO: if so, document when & why.
                print_compact_traceback("fyi: Atom.kill: ignoring error in remove_atom %r from jig %r: " % (self, j) )
        self.jigs = [] #bruce 041029 mitigate repeated kills
            # [bruce 050215 comment: this should soon no longer be needed, but will be kept as a precaution]
        _changed_structure_Atoms[self.key] = self #k not sure if needed; if it is, also covers .bonds below #bruce 060322
        
        # remove bonds
        for b in self.bonds[:]: #bruce 050214 copy list as a precaution
            n = b.other(self)
            if debug_1779:
                print "debug_1779: Atom.kill on %r is calling unbond on %r" % (self,b)
            n.unbond(b) # note: this can create a new singlet on n, if n is real,
                        # which requires computing b.ubp which uses self.posn()
                        # or self.baseposn(); or it can kill n if it's a singlet.
                        #e We should optim this for killing lots of atoms at once,
                        # eg when killing a chunk, since these new singlets are
                        # wasted then. [bruce 041201]
            # note: as of 041029 unbond also invalidates externs if necessary
            ## if n.element is Singlet: n.kill() -- done in unbond as of 041115
        self.bonds = [] #bruce 041029 mitigate repeated kills

        # only after disconnected from everything else, remove it from its molecule
        try:
            ## del self.molecule.atoms[self.key]
            self.molecule.delatom(self) # bruce 041115
            # delatom also kills the mol if it becomes empty (as of bruce 041116)
        except KeyError:
            print "fyi: Atom.kill: atom %r not in its molecule (killed twice?)" % self
            pass
        return # from Atom.kill
        
    def filtered(self): # mark 060303.
        """
        Returns True if self is not the element type/name currently listed in the Select Atoms filter combobox.
        """
        if self.is_singlet(): return False # Fixes bug 1608.  mark 060303.
        
        if self.molecule.assy.w.selection_filter_enabled:
            for e in self.molecule.assy.w.filtered_elements[:]:
                if e is self.element:
                    return False
            return True
            
        return False

    def Hydrogenate(self):
        """[Public method; does all needed invalidations:]
        If this atom is a singlet, change it to a hydrogen,
        and move it so its distance from its neighbor is correct
        (regardless of prior distance, but preserving prior direction).
        [#e sometimes it might be better to fix the direction too, like in depositMode...]
           If hydrogenate succeeds return number 1, otherwise, 0.
        """
        # Huaicai 1/19/05 added return value.
        if not self.element is Singlet: return 0
        other = self.bonds[0].other(self)
        self.mvElement(Hydrogen)
        #bruce 050406 rewrote the following, so it no longer depends
        # on old pos being correct for self being a Singlet.
        newpos = self.ideal_posn_re_neighbor( other)
        self.setposn(newpos)
        return 1
        
    def ideal_posn_re_neighbor(self, neighbor, pretend_I_am = None): # see also snuggle
        #bruce 050404 to help with bug 254 and maybe Hydrogenate
        """Given one of our neighbor atoms (real or singlet)
        [neighborness not verified! only posn is used, not the bond --
         this might change when we have bond-types #e]
        and assuming it should remain fixed and our bond to it should
        remain in the same direction, and pretending (with no side effects)
        that our element is pretend_I_am if this is given,
        what position should we ideally have
        so that our bond to neighbor has the correct length?
        """
        me = self.posn()
        it = neighbor.posn()
        length = vlen( me - it )
        if not length:
            #e atom_debug warning?
            # choose a better direction? only caller knows what to do, i guess...
            # but [050406] I think an arbitrary one is safer than none!
            ## return me # not great...
            it_to_me_direction = V(1,0,0)
        else:
            it_to_me_direction = norm( me - it )
            it_to_me_direction = norm( it_to_me_direction )
                # for original len close to 0, this might help make new len 1 [bruce 050404]
        if pretend_I_am: #bruce 050511 revised for atomtype
            ## my_elem = pretend_I_am # not needed
            my_atype = pretend_I_am.atomtypes[0] # even if self.element is pretend_I_am
        else:
            ## my_elem = self.element
            my_atype = self.atomtype
        ## its_elem = neighbor.element # not needed
        its_atype = neighbor.atomtype
            # presently we ignore the bond-valence between us and that neighbor atom,
            # even if this can vary for different bonds to it (for the atomtype it has)
        newlen = my_atype.rcovalent + its_atype.rcovalent #k Singlet.atomtypes[0].rcovalent better be 0, check this
        return it + newlen * it_to_me_direction
    
    def Dehydrogenate(self):
        """[Public method; does all needed invalidations:]
        If this is a hydrogen atom (and if it was not already killed),
        kill it and return 1 (int, not boolean), otherwise return 0.
        (Killing it should produce a singlet unless it was bonded to one.)
        """
        # [fyi: some new features were added by bruce, 041018 and 041029;
        #  need for callers to shakedown or kill mols removed, bruce 041116]
        if self.element is Hydrogen and not self.killed():
            #bruce 041029 added self.killed() check above to fix bug 152
            self.kill()
            # note that the new singlet produced by killing self might be in a
            # different mol (since it needs to be in our neighbor atom's mol)
            #bruce 050406 comment: if we reused the same atom (as in Hydrogenate)
            # we'd be better for movies... just reusing its .key is not enough
            # if we've internally stored alists. But, we'd like to fix the direction
            # just like this does for its new singlet... so I'm not changing this for now.
            # Best solution would be a new method for H or X to fix their direction
            # as well as their distance. ###@@@
            return 1
        else:
            return 0
        pass

    def snuggle(self): #bruce 051221 revised docstring re bug 1239
        """self is a singlet and the simulator has moved it out to the
        radius of an H. move it back. the molecule may or may not be still
        in frozen mode. Do all needed invals.
           WARNING: if you are moving several atoms at once, first move them all,
        then snuggle them all, since snuggling self is only correct after self's
        real neighbor has already been moved to its final position. [Ignorance of
        this issue was the cause of bug 1239.]
        """
        if not self.bonds:
            #bruce 050428: a bug, but probably just means we're a killed singlet.
            # The caller should be fixed, and maybe is_singlet should check this too,
            # but for now let's also make it harmless here:
            if debug_flags.atom_debug:
                print_compact_stack( "atom_debug: bug (ignored): snuggling a killed singlet of atomkey %r: " %
                                     self.key )#bruce 051221 revised this; untested
            return
        #bruce 050406 revised docstring to say mol needn't be frozen.
        # note that this could be rewritten to call ideal_posn_re_neighbor,
        # but we'll still use it since it's better tested and faster.
        o = self.bonds[0].other(self)
        op = o.posn()
        sp = self.posn()
        np = norm(sp-op)*o.atomtype.rcovalent + op
        self.setposn(np) # bruce 041112 rewrote last line
        return

    def Passivate(self): ###@@@ not yet modified for atomtypes since it's not obvious what it should do! [bruce 050511]
        """[Public method, does all needed invalidations:]
        Change the element type of this atom to match the number of
        bonds with other real atoms, and delete singlets.
        """
        # bruce 041215 modified docstring, added comments, capitalized name
        el = self.element
        PTsenil = PeriodicTable.getPTsenil()
        line = len(PTsenil)
        for i in range(line):
            if el in PTsenil[i]:
                line = i
                break
        if line == len(PTsenil): return #not in table
        # (note: we depend on singlets not being in the table)
        nrn = len(self.realNeighbors())
        for atm in self.singNeighbors():
            atm.kill()
        try:
            newelt = PTsenil[line][nrn]
        except IndexError:
            pass # bad place for status msg, since called on many atoms at once
        else:
            self.mvElement(newelt)
        # note that if an atom has too many bonds we'll delete the
        # singlets anyway -- which is fine

    def is_singlet(self):
        return self.element is Singlet # [bruce 050502 comment: it's possible self is killed and len(self.bonds) is 0]
    
    def singlet_neighbor(self): #bruce 041109 moved here from extrudeMode.py
        "return the atom self (a known singlet) is bonded to, checking assertions"
        assert self.element is Singlet, "%r should be a singlet but is %s" % (self, self.element.name)
            #bruce 050221 added data to the assert, hoping to track down bug 372 when it's next seen
        obond = self.bonds[0]
        atom = obond.other(self)
        assert atom.element is not Singlet, "bug: a singlet %r is bonded to another singlet %r!!" % (self, atom)
        return atom

    # higher-valence bonds methods [bruce 050502] [bruce 050627 comment: a lot of this might be obsolete. ###@@@]
    
    def singlet_v6(self):
        assert self.element is Singlet, "%r should be a singlet but is %s" % (self, self.element.name)
        assert len(self.bonds) == 1, "%r should have exactly 1 bond but has %d" % (self, len(self.bonds))
        return self.bonds[0].v6

    singlet_valence = singlet_v6 ###@@@ need to decide which name to keep! probably this one, singlet_valence. [050502 430pm]

    def singlet_reduce_valence_noupdate(self, vdelta):
            # this might or might not kill it;
            # it might even reduce valence to 0 but not kill it,
            # letting base atom worry about that
            # (and letting it take advantage of the singlet's position, when it updates things)
        assert self.element is Singlet, "%r should be a singlet but is %s" % (self, self.element.name)
        assert len(self.bonds) == 1, "%r should have exactly 1 bond but has %d" % (self, len(self.bonds))
        self.bonds[0].reduce_valence_noupdate(vdelta, permit_illegal_valence = True) # permits in-between, 0, or negative(?) valence
        return

    def update_valence(self, dont_revise_valid_bondpoints = False):
        """
        warning: following docstring used to be a comment, hasn't been verified recently:
        repositions/alters existing bondpoints, updates bonding pattern, valence errors, etc;
        might reorder bonds, kill bondpoints; but doesn't move the atom and doesn't alter
        existing real bonds or other atoms; it might let atom record how it wants to move,
        when it has a chance and wants to clean up structure, if this can ever be ambiguous
        later, when the current state (including positions of old bondpoints) is gone.

        Update 071019: if dont_revise_valid_bondpoints is passed, then only
        bondpoints with invalid valence (e.g. zero valence) are altered.
        """
        #bruce 050728 revised this and also disabled the debug prints
        #bruce 071019 added dont_revise_valid_bondpoints option
        # (though it's untested, since I ended up fixing a current bug
        #  in a different way; but it looks correct and seems useful
        #  enough to leave).
        from bond_constants import V_ZERO_VALENCE, BOND_VALENCES
        _debug = False ## debug_flags.atom_debug is sometimes useful here
        if self._modified_valence:
            self._modified_valence = False # do this first, so exceptions in the following only happen once
            if _debug:
                print "atom_debug: update_valence starting to updating it for", self
            # the only easy part is to kill bondpoints with illegal valences, and warn if those were not 0.
            zerokilled = badkilled = 0
            for sing in self.singNeighbors(): ###@@@ check out the other calls of this for code that might help us here...
                sv = sing.singlet_valence()
                if sv == V_ZERO_VALENCE:
                    sing.kill()
                    zerokilled += 1
                elif sv not in BOND_VALENCES:
                    # hmm... best to kill it and start over, I think, at least for now
                    sing.kill()
                    badkilled += 1
            if _debug:
                print "atom_debug: update_valence %r killed %d zero-valence and %d bad-valence bondpoints" % \
                      (self, zerokilled, badkilled)
            ###e now fix things up... not sure exactly under what conds, or using what code (but see existing code mentioned above)
            #bruce 050702 working on bug 121, here is a guess: change atomtype to best match new total number of bonds
            # (which we might have changed by killing some bondpoints). But only do this if we did actually kill bondpoints.
            if zerokilled or badkilled:
                self.adjust_atomtype_to_numbonds( dont_revise_bondpoints = dont_revise_valid_bondpoints )
                    ### WARNING: if dont_revise_bondpoints is not set,
                    # adjust_atomtype_to_numbonds can remake bondpoints just
                    # to move them, even if their number was correct. Both the
                    # remaking and the moving can be bad for some callers;
                    # thus the new option. It may need to be used more widely.
                    # [bruce 071019]
            #bruce 050728 temporary fix for bug 823 (in which C(sp2) is left with 2 order1 bondpoints that should be one bondpoint);
            # but in the long run we need a more principled way to decide whether to remake bondpoints or change atomtype
            # when they don't agree:
            if len(self.bonds) != self.atomtype.numbonds and not dont_revise_valid_bondpoints:
                if _debug:
                    print "atom_debug: update_valence %r calling remake_bondpoints"
                self.remake_bondpoints()
        elif _debug:
            print "atom_debug: update_valence thinks it doesn't need to update it for", self
        return

    def adjust_atomtype_to_numbonds(self, dont_revise_bondpoints = False):
        """
        [Public method, does all needed invals, might emit history messages #k]

        If this atom's number of bonds (including open bonds) is better matched
        by some other atomtype of its element than by its current atomtype, or if
        its atomtype is not yet set, then change to the best atomtype and (if atomtype
        was already set) emit a history message about this change.

        The comparison is of current atomtype to self.best_atomtype_for_numbonds().

        The change is done by set_atomtype if number of bonds is correct and
        dont_revise_bondpoints is not passed (since set_atomtype also
        remakes bondpoints in better positions), or by set_atomtype_but_dont_revise_singlets
        otherwise (no attempt is made to correct the number of open bonds in that case).

        [See also self.can_reduce_numbonds().]
        """
        #bruce 050702, part of fixing bug 121 for Alpha6
        #bruce 071019 added dont_revise_bondpoints option
        atype_now = self.atomtype_iff_set()
        best_atype = self.best_atomtype_for_numbonds(atype_now = atype_now)
        if best_atype is atype_now:
            return # never happens if atype_now is None
        if atype_now is not None:
            env.history.message("changing %s atomtype from %s to %s" % (self, atype_now.name, best_atype.name))
            # this will often happen twice, plus a third message from Build that it increased bond order,
            # so i'm likely to decide not to print it
        if (not dont_revise_bondpoints) and best_atype.numbonds == len(self.bonds):
            # right number of open bonds for new atype -- let's move them to better positions when we set it
            self.set_atomtype( best_atype)
        else:
            # wrong number of open bonds -- leave them alone (in number and position);
            # or, dont_revise_bondpoints option was passed
            self.set_atomtype_but_dont_revise_singlets( best_atype)
        return

    def best_atomtype_for_numbonds(self, atype_now = None, elt = None): #bruce 050702; elt arg added 050707
        # see also best_atype in bond_utils.py, which does something different but related [bruce 060523]
        """Compute and return the best guess for this atom's atomtype,
        given its current element (or the passed one),"""
        """[Public method]
           Compute and return the best atomtype for this atom's element (or the passed one if any)
        and number of bonds (including open bonds),
        breaking ties by favoring atype_now (if provided), otherwise favoring atomtypes which come earlier
        in the list of this element's (or elt's) possible atomtypes.
           For comparing atomtypes which err in different directions (which I doubt can ever matter in
        practice, since the range of numbonds of an element's atomtypes will be contiguous),
        we'll say it's better for an atom to have too few bonds than too many.
        In fact, we'll say any number of bonds too few (on the atom, compared to the atomtype)
        is better than even one bond too many.
           This means: the "best" atomtype is the one with the right number of bonds, or the fewest extra bonds,
        or (if all of them have fewer bonds than this atom) with the least-too-few bonds.
           (This method is used in Build mode, and might later be used when reading mmp files or pdb files, or in other ways.
        As of 050707 it's also used in Transmute.)
        [###k Should we also take into account positions of bonds, or their estimated orders, or neighbor elements??]
        """
        if elt is None:
            elt = self.element
        atomtypes = elt.atomtypes
        if len(atomtypes) == 1:
            return atomtypes[0] # optimization
        nbonds = len(self.bonds) # the best atomtype has numbonds == nbonds. Next best, nbonds+1, +2, etc. Next best, -1,-2, etc.
        items = [] 
        for i, atype in zip(range(len(atomtypes)), atomtypes):
            if atype is atype_now: # (if atype_now is None or is not for elt, this is a legal comparison and is always False)
                i = -1 # best to stay the same (as atype_now), or to be earlier in the list of atomtypes, other things being equal
            numbonds = atype.numbonds
            if numbonds < nbonds:
                order = (1, nbonds - numbonds, i) # higher is worse
            else:
                order = (0, numbonds - nbonds, i)
            items.append((order, atype))
        items.sort()
        best_atype = items[0][1]
        return best_atype # might or might not be the same as atype_now

    def can_reduce_numbonds(self): #bruce 050702, part of fixing bug 121
        """Say whether this atom's element has any atomtype which would
        better match this atom if it had one fewer bond.
        Note that this can be true even if that element has only one atomtype
        (when the number of bonds is currently incorrect). 
        """
        nbonds = len(self.bonds)
        # if nbonds < 1 (which will never happen based on how we're presently called),
        # the following code will (correctly) return False, so no special case is needed.
        for atype in self.element.atomtypes:
            if atype.numbonds < nbonds:
                return True
        return False
    
    # ==

    def _changed_structure(self): #bruce 050627; docstring revised and some required calls added, 050725; revised 051011
        """[private method]
           This must be called by all low-level methods which change this atom's or bondpoint's element, atomtype,
        or set of bonds. It doesn't need to be called for changes to neighbor atoms, or for position changes,
        or for changes to chunk membership of this atom, or when this atom is killed (but it will be called indirectly
        when this atom is killed, when the bonds are broken, unless this atom has no bonds). Calling it when not needed
        is ok, but might slow down later update functions by making them inspect this atom for important changes.
           All user events which can call this (indirectly) should also call env.do_post_event_updates() when they're done.
        """
        ####@@@@ I suspect it is better to also call this for all killed atoms or bondpoints, but didn't do this yet. [bruce 050725]
        ## before 051011 this used id(self) for key
        #e could probably optim by importing this dict at toplevel, or perhaps even assigning a lambda in place of this method
        global_model_changedicts.changed_structure_atoms[ self.key ] = self
        _changed_structure_Atoms[ self.key ] = self #bruce 060322
            # (see comment at _changed_structure_Atoms about how these two dicts are related)
        return
    
    # debugging methods (not yet fully tested; use at your own risk)
    
    def invalidate_everything(self): # for an atom, remove it and then readd it to its mol
        "debugging method"
        if len(self.molecule.atoms) == 1:
            print "warning: invalidate_everything on the only atom in mol %r\n" \
                  " might kill mol as a side effect!" % self.molecule
        # note: delatom invals self.bonds
        self.molecule.delatom(self) # note: this kills the mol if it becomes empty!
        self.molecule.addatom(self)
        return

    def update_everything(self):
        print "Atom.update_everything() does nothing"
        return

    #bruce 050511 added atomtype arg  ###@@@ callers should pass atomtype
    def Transmute(self, elt, force = False, atomtype = None): 
        """
        (TODO: clean up this docstring.)
        
        Transmute self into a different element, unless it is a singlet.
        
        If this is a real atom, change its element type to I{elt} (which
        should not be Singlet unless precautions listed below are taken)
        and its atomtype to the I{atomtype} object passed, or if None is
        passed as atomtype, to elt's default atomtype or self's existing one
        (not sure which!###@@@) -- no, to the best one given the number of
        real bonds, or real and open bonds [maybe? 050707] -- and replace
        its bondpoints (if any) with new ones (if any are needed) to match
        the desired number of bonds for the new element/atomtype.
        
        If self is a singlet, don't transmute it. (But this is not an error.)
        
        [As of 050511 before atomtype arg added, new atom type is old one if
        elt is same and old one already correct, else is default atom type. 
        This needs improvement. ###@@@]
        
        Never remove real bonds, even if there are too many. Don't change
        bond lengths (except in new open bonds created when replacing
        bondpoints) or atom positions.
        
        If there are too many real bonds for the new element type, refuse
        to transmute unless force is True.
        
        @param elt: The new element to transmute this atom (self) into, if
                    self is not a bondpoint. elt must not be Singlet unless
                    the caller has checked certain conditions documented below.
        @type  elt: L{Elem}
        
        @param force: If there are too many real bonds for the new element 
                      type, refuse to transmute unless force is True.
        @type  force: bool
        
        @param atomtype: The atomic hybrid of the element to transmute to.
                         If None (the default), the default atomtype is
                         assumed for I{elt}.
        @type  atomtype: L{AtomType}
        
        @note: Does all needed invalidations.

        @note: If elt is Singlet (bondpoint), the caller must be sure that self
               has exactly one bond, that self is in the same chunk as its
               neighbor atom, and that the neighbor atom is not a bondpoint
               (aka singlet), or serious but hard-to-notice bugs will ensue.
               In practice, this is usually only safe when self was a bondpoint
               earlier in the same user operation, and was temporarily transmuted
               to something else, and nothing happened in the meantime that
               could have changed those conditions. The caller must also not
               mind creating an open bond with a nonstandard length, since
               Transmute does not normalize open bond length as is done when
               they are created normally.
        
        @attention: This method begins with a capital letter. So that it 
                    conforms to our coding standards, I will rename it
                    in the near future (and fix callers). - Mark 2007-10-21
                    (But the new name can't be "transmute", since that
                     would be too hard to search for. -- bruce 071101)
        """
        if self.element is Singlet:
            # Note: some callers depend on this being a noop,
            # including the user Transmute operation, which calls this on
            # every atom in a chunk, including bondpoints.
            return
        if atomtype is None:
            if self.element is elt and \
               len(self.bonds) == self.atomtype.numbonds:
                ## this code might be used if we don't always return due to bond valence: ###@@@
                ## atomtype = self.atomtype # use current atomtype if we're correct for it now, even if it's not default atomtype
                # return since elt and desired atomtype are same as now and
                # we're correct
                return 
            else:
                ## atomtype = elt.atomtypes[0] # use default atomtype of elt
                ##print "transmute picking this dflt atomtype", atomtype
                #bruce 050707: use the best atomtype for elt, given the number
                # of real and open bonds
                atomtype = self.reguess_atomtype(elt)
        assert atomtype.element is elt
        # in case a specific atomtype was passed or the default one was chosen,
        # do another check to return early if requested change is a noop and 
        # our bond count is correct
        if self.element is elt and \
           self.atomtype is atomtype and \
           len(self.bonds) == atomtype.numbonds:
            # leave existing bondpoint positions alone in this case 
            # -- not sure this is best! ###@@@ #e review
            ##print "transmute returning since noop to change to these: %r %r" % (elt, atomtype)
            return
        # now we're committed to changing things
        nbonds = len(self.realNeighbors()) ###@@@ should also consider the bond-valence to them...
        if nbonds > atomtype.numbonds:
            # transmuting would break valence rules 
            # [###@@@ should instead use a different atomtype, if possible!]
            ###@@@ but a more normal case for using different one is if existing bond *valence* is too high...
            # note: this msg (or msg-class, exact text can vary) can get 
            # emitted too many times in a row.
            name = atomtype.fullname_for_msg()
            if force:
                msg = "warning: Transmute broke valence rules, " \
                    "made (e.g.) %s with %d bonds" % (name, nbonds)
                env.history.message( orangemsg(msg) )
                # fall through
            else:
                msg = "warning: Transmute refused to make (e.g.)" \
                    " a %s with %d bonds" % (name, nbonds)
                env.history.message( orangemsg(msg) )
                return
        # in all other cases, do the change (even if it's a noop) and also
        # replace all bondpoints with 0 or more new ones
        self.direct_Transmute( elt, atomtype)
        return

    def Transmute_selection(self, elt): #bruce 070412; could use review for appropriate level, error handling, etc
        """
        [this may be a private method for use when making our cmenu;
        if not, it needs more options and a better docstring.]
        Transmute as many as possible of the selected atoms to elt.
        """
        selatoms = self.molecule.assy.selatoms
        atoms = selatoms.values() # not itervalues, too dangerous
        for atom in atoms:
            atom.Transmute(elt)
        return

    def permitted_btypes_for_bond(self, bond): #bruce 060523
        """
        If we are a real atom:
        Given one of our bonds (either real or open),
        and considering as fixed only its and our real bonds' existence
        (not their current bond types or our current atomtype),
        and ignoring everything else about the given bond (like the other atom on it),
        return the set of bond types it could have
        (as a dict from permitted bond v6's to lists of atomtypes that permit them),
        without forcing valence errors on this atom
        (but assuming the other bonds can adjust in btype however needed).
           Only consider disallowing bond types whose order is too high,
        not too low, even though the latter might also be needed in theory
        [I'm not sure -- bruce 060523]).
           If we are a bondpoint:
        return something in the same format which permits all bondtypes.
        """
        bonds = [] # which bonds (besides bond) need to keep existing (with order 1 or higher)?
        nbonds = 0 # how many bonds (including bond, whether or not it's open) need to keep existing?
        for b in self.bonds:
            if b is not bond and not b.is_open_bond():
                bonds.append(b)
            elif b is bond:
                nbonds += 1
        min_other_valence = len(bonds) # probably the only way this bonds list is used
        permitted = {} # maps each permitted v6 to the list of atomtypes which permit it (in same order as self.element.atomtypes)
        is_singlet = self.is_singlet() #k not sure if the cond that uses this is needed
        for atype in self.element.atomtypes:
            if nbonds > atype.numbonds:
                continue # atype doesn't permit enough bonds
            # if we changed self to that atomtype, how high could bond's valence be? (expressed as its permitted valences)
            # Do we take into account min_other_valence, or not? Yes, I think.
            ##k review once this is tried. Maybe debug print whether this matters. #e
            # There are two limits: atype.permitted_v6_list, and atype.valence minus min_other_valence.
            # But the min_other_valence is the max of two things: other real bonds, or required numbonds (for this atype)
            # minus 1 (really, that times the minimum bond order for this atomtype, if that's not 1, but minimum bond order
            # not being 1 is nim in all current code).
            # (BTW, re fixed bug 1944, I don't know why double is in N(sp2)g's permitted_v6_list, and that's wrong
            # and remains unfixed, though our_min_other_valence makes it not matter in this code.)
            for v6 in atype.permitted_v6_list:
                our_min_other_valence = max(min_other_valence, atype.numbonds - 1) #bruce 060524 fix bug 1944
                if is_singlet or v6 <= (atype.valence - our_min_other_valence) * V_SINGLE:
                    permitted.setdefault(v6, []).append(atype)
        return permitted

    def direct_Transmute(self, elt, atomtype): #bruce 050511 split this out of Transmute
        """[Public method, does all needed invalidations:]
        With no checks except that the operation is legal,
        kill all bondpoints, change elt and atomtype
        (both must be provided and must match), and make new bondpoints.
        """
        for atm in self.singNeighbors():
            atm.kill() # (since atm is a bondpoint, this kill doesn't replace it with a bondpoint)
        self.mvElement(elt, atomtype)
        self.make_enough_bondpoints()
        return # from direct_Transmute

    def reposition_baggage(self, baggage = None, planned_atom_nupos = None): #bruce 060629 for bondpoint problem
        """Your baggage atoms (or the given subset of them) might no longer be sensibly located,
        since you and/or some neighbor atoms have moved (or are about to move, re planned_atom_nupos as explained below),
        so fix up their positions based on your other neighbors' positions, using old baggage positions only as hints.
           BUT one of your other neighbors (but not self) might be about to move (rather than already having moved) --
        if so, planned_atom_nupos = (that neighbor, its planned posn),
        and use that posn instead of its actual posn to decide what to do.
           WARNING: we assume baggage is a subset of self.baggageNeighbors(), but don't check this except when ATOM_DEBUG is set.
        """
        try:
            import reposition_baggage
            debug.reload_once_per_event(reposition_baggage) # this can be removed when devel is done, but doesn't need to be
            reposition_baggage.reposition_baggage_0(self, baggage, planned_atom_nupos)
        except:
            # this is always needed, since some of the code for special alignment cases
            # is so rarely exercised that we can't effectively test it
            print_compact_traceback("bug in reposition_baggage; skipping it: ")
            pass
        return
    
    def remake_bondpoints(self):
        """
        [Public method, does all needed invalidations]

        Destroy this real atom's existing bondpoints (if any);
        then call make_enough_bondpoints to add the right number
        of new ones in the best positions.
        """
        for atm in self.singNeighbors():
            atm.kill() # (since atm is a bondpoint, this kill doesn't replace it with a bondpoint)
        self.make_enough_bondpoints()
        return
    
    def remake_baggage_UNFINISHED(self):
        #bruce 051209 -- pseudocode; has sample calls, desirable but commented out, since it's unfinished ###@@@
        bn = self.baggageNeighbors()
        for atm in bn:
            if not atm.is_singlet():
                pass ###e record element and position
                atm.mvElement(Singlet) ####k ??? #####@@@@@ kluge to kill it w/o replacing w/ singlet; better to just tell kill that
            atm.kill() # (since atm is a singlet, this kill doesn't replace it with a singlet)
        self.make_enough_bondpoints() ###e might pass old posns to ask this to imitate them if it can
        pass ###e now transmute the elts back to what they were, if you can, based on nearness
        return

    def make_enough_bondpoints(self):
        """
        [Public method, does all needed invalidations:]

        Add 0 or more bondpoints to this real atom, until it has as many bonds
        as its element and atom type prefers (but at most 4, since we use
        special-case code whose knowledge only goes that high). Add them in
        good positions relative to existing bonds (if any) (which are not
        changed, whether they are real or open bonds).
        """
        #bruce 050510 extending this to use atomtypes; all subrs still need to set singlet valence ####@@@@
        if len(self.bonds) >= self.atomtype.numbonds:
            return # don't want any more bonds
        # number of existing bonds tells how to position new open bonds
        # (for some n we can't make arbitrarily high numbers of wanted open
        # bonds; for other n we can; we can always handle numbonds <= 4)
        n = len(self.bonds)
        if n == 0:
            self.make_bondpoints_when_no_bonds()
        elif n == 1:
            self.make_bondpoints_when_1_bond()
        elif n == 2:
            self.make_bondpoints_when_2_bonds()
        elif n == 3:
            self.make_bondpoints_when_3_bonds() # (makes at most one open bond)
        else:
            pass # no code for adding open bonds to 4 or more existing bonds
        return

    # the make_singlets methods were split out of the private depositMode methods
    # (formerly called bond1 - bond4), to help implement Atom.Transmute [bruce 041215]

    def make_bondpoints_when_no_bonds(self): #bruce 050511 partly revised this for atomtypes
        """
        [public method, but trusts caller about len(self.bonds)]
        see docstring for make_bondpoints_when_2_bonds
        """
        assert len(self.bonds) == 0 # bruce 071019 added this
        atype = self.atomtype
        if atype.bondvectors:
            r = atype.rcovalent
            pos = self.posn()
            mol = self.molecule
            for dp in atype.bondvectors:
                x = Atom('X', pos + r * dp, mol)
                bond_atoms(self, x) ###@@@ set valence? or update it later?
        return
    
    def make_bondpoints_when_1_bond(self): # by josh, with some comments and mods by bruce
        """
        [public method, but trusts caller about len(self.bonds)]
        see docstring for make_bondpoints_when_2_bonds
        """
        assert len(self.bonds) == 1
        assert not self.is_singlet()
        atype = self.atomtype
        if len(atype.quats): #bruce 041119 revised to support "onebond" elements
            # There is at least one other bond we should make (as open bond);
            # compute rq, which rotates this atom's bonding pattern (base and quats)
            # to match the existing bond. (If q is a quat that rotates base to another
            # bond vector (in std position), then rq + q - rq rotates r to another
            # bond vector in actual position.) [comments revised/extended by bruce 050614]
            pos = self.posn()
            s1pos = self.bonds[0].ubp(self)
            r = s1pos - pos # this points towards our real neighbor
            del s1pos # same varname used differently below
            rq = Q(r,atype.base)
            # if the other atom has any other bonds, align 60 deg off them
            # [new feature, bruce 050531: or 0 degrees, for both atomtypes sp2;
            #  should also look through sequences of sp atoms, but we don't yet do so]
            # [bruce 041215 comment: might need revision if numbonds > 4]
            a1 = self.bonds[0].other(self) # our real neighbor
            if len(a1.bonds)>1:
                if not (a1.atomtype.spX == 1 and atype.spX < 3): #bruce 050729 added (and atype.spX < 3) to fix bug 840
                    # figure out how to line up one arbitrary bond from each of self and a1.
                    # a2 = a neighbor of a1 other than self
                    if self is a1.bonds[0].other(a1):
                        a2 = a1.bonds[1].other(a1)
                    else:
                        a2 = a1.bonds[0].other(a1)
                    a2pos = a2.posn()
                else:
                    #bruce 050728 new feature: for new pi bonds to sp atoms, use pi_info to decide where to pretend a2 lies.
                    # If we give up, it's safe to just say a2pos = a1.posn() -- twistor() apparently tolerates that ambiguity.
                    try:
                        # catch exceptions in case for some reason it's too early to compute this...
                        # note that, if we're running in Build mode (which just deposited self and bonded it to a1),
                        # then that new bond and that change to a1 hasn't yet been seen by the bond updating code,
                        # so an old pi_info object might be on the other bonds to a1, and none would be on the new bond a1-self.
                        # But we don't know if this bond is new, so if it has a pi_bond_obj we don't know if that's ok or not.
                        # So to fix a bug this exposed, I'm making bond.rebond warn the pi_bond_obj on its bond, immediately
                        # (not waiting for bond updating code to do it).
                        # [050729: this is no longer needed, now that we destroy old pi_bond_obj (see below), but is still done.]
                        b = self.bonds[0] # if there was not just one bond on self, we'd say find_bond(self,a1)
                        #bruce 050729: it turns out there can be incorrect (out of date) pi_info here,
                        # from when some prior singlets on self were still there -- need to get rid of this and recompute it.
                        # This fixes a bug I found, and am reporting, in my mail (not yet sent) saying bug 841 is Not A Bug.
                        if b.pi_bond_obj is not None:
                            b.pi_bond_obj.destroy()
                        pi_info = b.get_pi_info(abs_coords = True) # without the option, vectors would be in bond's coordsys
                        ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z) = pi_info
                        del ord_pi_y, ord_pi_z
                        # note that we don't know whether we're atom1 or atom2 in that info, but it shouldn't matter
                        # since self is not affecting it so it should not be twisted along b.
                        # So we'll pretend a1py, a1pz are about a1, though they might not be.
                        # We'll use a1pz as the relative place to imagine a1's neighbor, if a1 had been sp2 rather than sp.
                        a2pos = a1.posn() + a1pz
                    except:
                        print_compact_traceback("exception ignored: ")
                        a2pos = a1.posn()
                    pass 
                s1pos = pos+(rq + atype.quats[0] - rq).rot(r) # un-spun posn of one of our new singlets
                spin = twistor(r,s1pos-pos, a2pos-a1.posn())
                    # [bruce 050614 comments]
                    # spin is a quat that says how to twist self along r to line up
                    # the representative bonds perfectly (as projected into a plane perpendicular to r).
                    # I believe we'd get the same answer for either r or -r (since it's a quat, not an angle!).
                    # This won't work if a1 is sp (and a2 therefore projects right on top of a1 as seen along r);
                    # I don't know if it will have an exception or just give an arbitrary result. ##k
                    ##e This should be fixed to look through a chain of sp atoms to the next sp2 atom (if it finds one)
                    # and to know about pi system alignments even if that chain bends
                    # (though for long chains this won't matter much in practice).
                    # Note that we presently don't plan to store pi system alignment in the mmp file,
                    # which means it will be arbitrarily re-guessed for chains of sp atoms as needed.
                    # (I'm hoping other people will be as annoyed by that as I will be, and come to favor fixing it.)
                if atype.spX < 3 and a1.atomtype.spX < 3: # for now, same behavior for sp2 or sp atoms [revised 050630]
                    pass # no extra spin
                else:
                    spin = spin + Q(r, math.pi/3.0) # 60 degrees of extra spin
            else: spin = Q(1,0,0,0)
            mol = self.molecule
            if 1: # see comment below
                from debug_prefs import debug_pref, Choice # bruce 050614
                spinsign = debug_pref("spinsign", Choice([1,-1]))
            for q in atype.quats:
                # the following old code has the wrong sign on spin, thus causing bug 661: [fixed by bruce 050614]
                ##  q = rq + q - rq - spin
                # this would be the correct code:
                ##  q = rq + q - rq + spin
                # but as an example of how to use debug_pref, I'll put in code that can do it either way,
                # with the default pref value giving the correct behavior (moved just above, outside of this loop).
                q = rq + q - rq + spin * spinsign
                xpos = pos + q.rot(r)
                x = Atom('X', xpos, mol)
                bond_atoms(self, x)
        return
        
    def make_bondpoints_when_2_bonds(self):
        """
        [public method, but trusts caller about len(self.bonds)]

        Given an atom with exactly 2 real bonds (and no singlets),
        see if it wants more bonds (due to its atom type),
        and make extra singlets if so, [###@@@ with what valence?]
        in good positions relative to the existing real bonds.
        Precise result might depend on order of existing bonds in self.bonds.
        """
        assert len(self.bonds) == 2 # usually both real bonds; doesn't matter
        atype = self.atomtype
        if atype.numbonds <= 2: return # optimization
        # rotate the atom to match the 2 bonds it already has
        # (i.e. figure out a suitable quat -- no effect on atom itself)
        pos = self.posn()
        s1pos = self.bonds[0].ubp(self)
        s2pos = self.bonds[1].ubp(self)
        r = s1pos - pos
        rq = Q(r,atype.base)
        # this moves the second bond to a possible position;
        # note that it doesn't matter which bond goes where
        q1 = rq + atype.quats[0] - rq
        b2p = q1.rot(r)
        # rotate it into place
        tw = twistor(r, b2p, s2pos - pos)
        # now for all the rest
        # (I think this should work for any number of new bonds [bruce 041215])
        mol = self.molecule
        for q in atype.quats[1:]:
            q = rq + q - rq + tw
            x = Atom('X', pos + q.rot(r), mol)
            bond_atoms(self, x)
        return

    def make_bondpoints_when_3_bonds(self):
        """
        [public method, but trusts caller about len(self.bonds)]
        see docstring for make_bondpoints_when_2_bonds
        """
        assert len(self.bonds) == 3
        atype = self.atomtype
        if atype.numbonds > 3:
            # bruce 041215 to fix a bug (just reported in email, no bug number):
            # Only do this if we want more bonds.
            # (But nothing is done to handle more than 4 desired bonds.
            #  Our element table has a comment claiming that its elements with
            #  numbonds > 4 are not yet used, but nothing makes me confident
            #  that comment is up-to-date.)
            pos = self.posn()
            s1pos = self.bonds[0].ubp(self)
            s2pos = self.bonds[1].ubp(self)
            s3pos = self.bonds[2].ubp(self)
            opos = (s1pos + s2pos + s3pos)/3.0
            try:
                assert vlen(pos - opos) > 0.001
                dir = norm(pos - opos)
            except:
                # [bruce 041215:]
                # fix unreported unverified bug (self at center of its neighbors):
                # [bruce 050716 comment: one time this can happen is when we change atomtype of some C in graphite to sp3]
                if debug_flags.atom_debug:
                    print "atom_debug: fyi: self at center of its neighbors (more or less) while making singlet", self, self.bonds
                dir = norm(cross(s1pos - pos, s2pos - pos))
                    # that assumes s1 and s2 are not opposite each other; #e it would be safer to pick best of all 3 pairs
            opos = pos + atype.rcovalent * dir
            mol = self.molecule
            x = Atom('X', opos, mol)
            bond_atoms(self, x)
        return

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

    # == PAM strand atom methods (some are more specific than that,
    # e.g. not on Pl or only on Pl)
    
    # default values of instance variables (some not needed):
    _dna_updater__error = ""
    ## dnaBaseName -- set when first demanded, or can be explicitly set using setDnaBaseName().
    ## dnaStrandName -- set when first demanded, or can be explicitly set using setDnaStrandName().

    def setDnaBaseName(self, dnaBaseName): # Mark 2007-08-16
        """
        Set the Dna base name. This is only valid for PAM Ss or Sj
        atoms.
        
        @param dnaBaseName: The DNA base name. This is usually a single letter,
                            but it can be more. Only letters are valid.
        @type  dnaBaseName: str
        
        @raise: If self is not Sj or Ss, or if dnaBaseName has an invalid 
                character(s).
        
        """
        assert self.element.symbol in ('Se3', 'Ss3', 'Sj3', 'Ss5', 'Sj5'), \
            "Can only assign dnaBaseNames to Ss or Sj (PAM) atoms. \
            Attempting to assign dnaBaseName %r to element %r." \
            % (dnaBaseName, self.element.name)
        
        # Make sure dnaBaseName has all valid characters.
        
        for c in dnaBaseName:
            if not c in string.letters:
                assert 0, "%r is not a valid dnaBaseName name." % (dnaBaseName)
                
        self.dnaBaseName = dnaBaseName
        
    def getDnaBaseName(self):
        """
        Returns the value of attr I{dnaBaseName}.
        
        @return: The DNA base name, or None if the attr I{dnaBaseName} does 
                 not exist.
        @rtype:  str
        """
        return self.__dict__.get('dnaBaseName', "")
    
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
    
    def setDnaStrandName(self, dnaStrandName): # Mark 2007-09-04
        """
        Set the Dna strand name. This is only valid for PAM-5 Pe atoms.
        
        @param dnaStrandName: The DNA strand name.
        @type  dnaStrandName: str
        
        @raise: If self is not a Pe atom.
        
        """
        assert self.element.symbol in ('Se3', 'Pe5'), \
            "Can only assign dnaStrandNames to Pe (PAM) atoms. \
            Attempting to assign dnaStrandName %r to element %r." \
            % (dnaStrandName, self.element.name)
        
        # Make sure dnaStrandName has all valid characters.
        #@ Need to allow digits and letters. Mark 2007-09-04
        """
        for c in dnaStrandName:
            if not c in string.letters:
                assert 0, "Strand name %r has an invalid character (%r)." \
                       % (dnaStrandName, c)"""
                
        self.dnaStrandName = dnaStrandName
        
    def getDnaStrandName(self):
        """
        Returns the value of attr I{dnaStrandName}.
        
        @return: The DNA strand name, or None if the attr I{dnaStrandName} does 
                 not exist.
        @rtype:  str
        """
        return self.__dict__.get('dnaStrandName', "")
        
    def directional_bond_chain_status(self): # bruce 071016
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
        a direction is actually set. Similarly, when two bonds have directions
        set, we don't consider whether their directions are consistent.

        But if self is monovalent (e.g. a bondpoint) and its neighbor is not,
        we consider its neighbor's status in determining its own.
        
        Note that when drawing a bond, each of its atoms can have an
        almost-independent directional_bond_chain_status (due to the
        possibility of erroneous structures), so both of its atoms
        need their directional_bond_chain_status checked for errors.
        """
        # note: I think this implem is correct with or without open bonds
        # being directional [bruce 071016]
        if not self.element.bonds_can_be_directional:
            # optimization
            return DIRBOND_NONE, None, None
        if len(self.bonds) == 1:
            # Special cases, in all but a few situations that I think will never happen.
            # (But for those, fall thru to general case below.)
            bond = self.bonds[0]
            neighbor = bond.other(self)
            if len(neighbor.bonds) > 1:
                # monovalents defer to non-monovalent neighbors
                # (note: this applies to bondpoints (after mark 071014 changes)
                #  or to "strand termination atoms".)
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
# following debug print code superseded by more accurate code in dna updater,
# so removed from here, two places (it was usually wrong anyway) [bruce 080131]
##                        if debug_flags.atom_debug: #bruce 080117 only when atom_debug
##                            msg =  "warning: %r has one directional bond (%r) " \
##                                "by which it's attached to (but not in) a " \
##                                "directional bond chain containing %r and %r" % \
##                                (self, bond, bond1, bond2)
##                            print msg
                        return DIRBOND_NONE, None, None # DIRBOND_ERROR?
                    pass
                elif statuscode == DIRBOND_CHAIN_END:
                    # it matters whether the neighbor's chain includes us
                    # (though I suspect that it always does include us except in errors).
                    if bond is bond1:
                        return DIRBOND_CHAIN_END, bond, None
                    else:
##                        if debug_flags.atom_debug: #bruce 080117 only when atom_debug
##                            msg = "warning: %r has one directional bond (%r) " \
##                                "by which it's attached to (but not in) the end of a " \
##                                "directional bond chain containing %r" % \
##                                (self, bond, bond1)
##                            print msg
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
            # (WARNING: current behavior is not ideal at ends of bare strands) 
            real_dirbonds = filter( lambda bond: not bond.is_open_bond(), dirbonds )
            num_real = len(real_dirbonds)
            if num_real == 2:
                # This works around the near-term situation in which a single strand
                # has open bonds where axis atoms ought to be, by ignoring those open bonds.
                # POSSIBLE BUG: the propogate caller can reach this, if it can start on an
                # ignored open bond. Maybe we should require that it is not offered in the UI
                # in this case, by having it check this method before deciding. ### REVIEW
                return DIRBOND_CHAIN_MIDDLE, real_dirbonds[0], real_dirbonds[1]
            else:
                # some sort of error, or at least, a situation we can't propogate a chain in.
                # WARNING: this happens routinely at the end of a "bare strand" (no axis atoms),
                # since it has one real and two open bonds, all directional.
                # This situation will probably be deprecated but can happen at present.
                # (REVIEW: in that situation would it be better to return DIRBOND_NONE, None, None?)
                # We might fix this by:
                # - making that situation never occur
                # - making bonds know whether they're directional even if they're open (bond subclass)
                # - atom subclass for bondpoints
                # - notice whether a direction is set on just one open bond;
                #   construct open bonds on directional elements so the right number are set
                #   (or preferably, marked as directional bonds without a direction being set)
                # REVIEW: return an error message string?
                # [bruce 071112 updated comment]
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
        or in the case of erroneous structures [or possibly some legal ones as of
        mark 071014 changes], 3 or more.
        """
        ### REVIEW: should this remain as a separate method, now that its result
        # can't be used naively?
        return filter(lambda bond: bond.is_directional(), self.bonds)

    def bond_directions_are_set_and_consistent(self): #bruce 071204
        """
        Does self (a strand atom, base or base linker)
        have exactly two bond directions set, not inconsistently?
        """
        count_plus, count_minus = 0, 0
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir == 1:
                count_plus += 1
            elif dir == -1:
                count_minus += 1
        return (count_plus, count_minus) == (1, 1)

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

    def Pl_preferred_Ss_neighbor(self): # bruce 080118
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
        assert self.element.symbol.startswith("Pl") # KLUGE
        Pl_STICKY_BOND_DIRECTION = 1 ### @@@@ JUST A GUESS -- 1 or -1;
            # direction from Pl to the Ss it wants to stay with when it can
            #e refile into a dna constants file when we refile this method
        for candidate in ( # these might be None, or conceivably a non-Ss atom
            self.next_atom_in_bond_direction( Pl_STICKY_BOND_DIRECTION),
            self.next_atom_in_bond_direction( - Pl_STICKY_BOND_DIRECTION)
         ):
            if candidate and candidate.element.symbol.startswith("Ss"): # KLUGE
                # note: this cond excludes X (good), Pl (bug if happens, but good).
                # it excludes Sj and Hp (bad), but is only used from dna updater
                # so that won't be an issue. Non-kluge variant would test for
                # "a strand base atom".
                return candidate
        print "bug: Pl with no Ss: %r" % self # only true once dna updater enabled
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
            assert len(axis_neighbors) == 1
                # stub, since the updater checks needed to ensure this are NIM as of 071203
            return axis_neighbors[0]
        return None

    def Pl_neighbors(self): #bruce 080122
        """
        Assume self is a PAM strand sugar atom; return the neighbors of self
        which are PAM Pl (pseudo-phosphate) atoms (or any variant thereof,
         which sometimes interposes between strand base sugar pseudoatoms).
        """
        res = filter( lambda atom: atom.element.symbol.startswith("Pl"), # KLUGE
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

    def dna_updater_error_string(self,
                                 include_propogated_error_details = True,
                                 newline = '\n'
                                 ): #bruce 080206
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
        if not self._dna_updater__error:
            return "" # optimize common case
        from dna_updater.fix_bond_directions import PROPOGATED_DNA_UPDATER_ERROR
        from dna_updater.fix_bond_directions import _f_detailed_dna_updater_error_string
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
    
    pass # end of class Atom

# ==

register_class_changedicts( Atom, _Atom_global_dicts )
    # error if one class has two same-named changedicts (so be careful re module reload)

# removing definition of atom = Atom, since I have just fixed all uses, I hope: [bruce 071113]
## atom = Atom # old name of that class -- must remain here until all code has been revised to use new name [bruce 050610]

# ==

# this can be removed when the code that uses it in bond_updater.py is removed.
# [bruce 071119]
##class Atom2(Atom): #bruce 071116
##    """
##    For development tests only -- a clone of class Atom,
##    for testing the effect of replace_atom_class on live atoms.
##    """
##    # tell undo to treat the class as Atom when grabbing and storing diffs:
##    _s_undo_class_alias = Atom
##    pass

# ==

def oneUnbonded(elem, assy, pos, atomtype = None): #bruce 050510 added atomtype option
    """
    Create one unbonded atom, of element elem
    and (if supplied) the given atomtype
    (otherwise the default atomtype for elem),
    at position pos, in its own new chunk.
    """
    # bruce 041215 moved this from chunk.py to chem.py, and split part of it
    # into the new atom method make_bondpoints_when_no_bonds, to help fix bug 131.
    mol = chunk.Chunk(assy, 'bug') # name is reset below!
    atm = Atom(elem.symbol, pos, mol)
    # bruce 041124 revised name of new mol, was gensym('Chunk.');
    # no need for gensym since atom key makes the name unique, e.g. C1.
    atm.set_atomtype_but_dont_revise_singlets(atomtype) # ok to pass None, type name, or type object; this verifies no change in elem
        # note, atomtype might well already be the value we're setting; if it is, this should do nothing
    mol.name = "Chunk-%s" % str(atm)
    atm.make_bondpoints_when_no_bonds() # notices atomtype
    assy.addmol(mol)
    return atm

# ==

def move_alist_and_snuggle(alist, newPositions):
    """
    Move the atoms in alist to the new positions in the given array or sequence
    (which must have the same length);
    then for any singlets in alist, correct their positions using Atom.snuggle.
       WARNING: it would be wrong to call this on several alists in a row if they might overlap
    or were connected by bonded atoms, for the same reason that the snuggle has to be done in a separate loop
    (see snuggle docstring for details, re bug 1239).
       WARNING: I'm not sure if it does all required invals; it doesn't do gl_update.
    """
    #bruce 051221 split this out of class Movie so its bug1239 fix can be used in jig_Gamess.
    assert len(alist) == len(newPositions)
    singlets = []
    for a, newPos in zip(alist, newPositions):
        #bruce 050406 this needs a special case for singlets, in case they are H in the xyz file
        # (and therefore have the wrong distance from their base atom).
        # Rather than needing to know whether or not they were H during the sim,
        # we can just regularize the singlet-baseatom distance for all singlets.
        # For now I'll just use setposn to set the direction and snuggle to fix the distance.
        #e BTW, I wonder if it should also regularize the distance for H itself? Maybe only if sim value
        # is wildly wrong, and it should also complain. I won't do this for now.
        a.setposn_batch(A(newPos)) #bruce 050513 try to optimize this
        if a.is_singlet(): # same code as in movend()
            singlets.append(a) #bruce 051221 to fix bug 1239: do all snuggles after all moves; see snuggle docstring warning
    for a in singlets:
        a.snuggle() # includes a.setposn; no need for that to be setposn_batch [bruce 050516 comment]
    return

# end
