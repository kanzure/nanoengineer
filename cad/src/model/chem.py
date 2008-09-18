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

- class Chunk (then called class molecule) was moved into new file chunk.py circa 041118

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

- bruce 080327 splitting out PAM_Atom_methods

TODO:

Subclasses of Atom (e.g. for PAM3 pseudoatoms or even strand atoms) are being
considered. One issue to check is whether Undo hardcodes the classname 'Atom'
and will need fixing to work properly for subclasses with different names.
[bruce 071101 comment]
"""

import math
import string

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawpolycone
from graphics.drawing.CS_draw_primitives import drawwiresphere

from model.elements import Singlet
from model.elements import Hydrogen
from model.elements import PeriodicTable
from model.elements import Pl5

from model.atomtypes import AtomType #bruce 080327

from model.bond_constants import V_SINGLE
from model.bond_constants import min_max_valences_from_v6
from model.bond_constants import valence_to_v6
from model.bond_constants import ideal_bond_length

from model.bonds import bonds_mmprecord, bond_copied_atoms, bond_atoms

import model.global_model_changedicts as global_model_changedicts

from geometry.VQT import V, Q, A, norm, cross, twistor, vlen, orthodist
from geometry.VQT import atom_angle_radians
from Numeric import dot

from graphics.rendering.mdl.mdldata import marks, links, filler
from graphics.rendering.povray.povheader import povpoint

from utilities.debug import reload_once_per_event
from utilities.debug import print_compact_stack, print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_False, Choice

from utilities.Printing import Vector3ToString
from utilities.Log import orangemsg, redmsg, greenmsg

from utilities.constants import atKey
    # generator for atom.key attribute, also used for fake atoms.
    # [moved from here to constants.py to remove import cycle, bruce 080510]
    # As of bruce 050228, we now make use of the fact that this produces keys
    # which sort in the same order as atoms are created (e.g. the order they're
    # read from an mmp file), so we now require this in the future even if the
    # key type is changed. [Note: this comment appears in two files.]

from utilities.constants import gensym
from utilities.constants import intRound

from utilities.constants import diDEFAULT
from utilities.constants import diBALL
from utilities.constants import diTrueCPK
from utilities.constants import diTUBES
from utilities.constants import diINVISIBLE

from utilities.constants import remap_atom_dispdefs #revised, bruce 080324

from utilities.constants import dispLabel
from utilities.constants import default_display_mode
from utilities.constants import TubeRadius

from utilities.constants import BONDPOINT_LEFT_OUT
from utilities.constants import BONDPOINT_UNCHANGED
# from utilities.constants import BONDPOINT_ANCHORED
from utilities.constants import BONDPOINT_REPLACED_WITH_HYDROGEN

from utilities.constants import ATOM_CONTENT_FOR_DISPLAY_STYLE

from utilities.constants import pink, yellow
from utilities.constants import ErrorPickedColor

from utilities.prefs_constants import selectionColor_prefs_key

from utilities.GlobalPreferences import bondpoint_policy

from utilities.GlobalPreferences import disable_do_not_draw_open_bonds
from utilities.GlobalPreferences import usePyrexAtomsAndBonds
from utilities.GlobalPreferences import dna_updater_is_enabled

from utilities.prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from utilities.prefs_constants import arrowsOnThreePrimeEnds_prefs_key

from utilities.prefs_constants import showValenceErrors_prefs_key
from utilities.prefs_constants import dnaDisplayMinorGrooveErrorIndicators_prefs_key
from utilities.prefs_constants import dnaMinorGrooveErrorIndicatorColor_prefs_key

from utilities.prefs_constants import cpkScaleFactor_prefs_key
from utilities.prefs_constants import diBALL_AtomRadius_prefs_key

from utilities.prefs_constants import dnaMinMinorGrooveAngle_prefs_key
from utilities.prefs_constants import dnaMaxMinorGrooveAngle_prefs_key
from utilities.prefs_constants import dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import useCustomColorForThreePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandFivePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import useCustomColorForFivePrimeArrowheads_prefs_key

from graphics.drawables.Selobj import Selobj_API

from utilities import debug_flags

from platform_dependent.PlatformDependent import fix_plurals

import foundation.env as env

from foundation.state_utils import StateMixin
from foundation.state_utils import register_instancelike_class
from foundation.state_utils import copy_val

from foundation.state_constants import S_CHILDREN, S_PARENT, S_DATA, S_CACHE
from foundation.state_constants import UNDO_SPECIALCASE_ATOM, ATOM_CHUNK_ATTRIBUTE_NAME

from foundation.changedicts import register_changedict, register_class_changedicts

import foundation.undo_archive as undo_archive
from foundation.undo_archive import register_undo_updater

from foundation.inval import InvalMixin

import foundation.Utility as Utility
from model.jigs import Jig

from dna.operations.crossovers import crossover_menu_spec

from model.PAM_Atom_methods import PAM_Atom_methods

from graphics.drawing.special_drawing import USE_CURRENT
from graphics.drawing.special_drawing import SPECIAL_DRAWING_STRAND_END

# ==

DEBUG_1779 = False # do not commit with True, but leave the related code in for now [bruce 060414]

BALL_vs_CPK = 0.25 # ratio of default diBALL radius to default diTrueCPK radius [renamed from CPKvdW by bruce 060607]

# ==

# define AtomDict and AtomBase differently depending on whether we are
# using Pyrex Atoms and Bonds (atombase.pyx):

_using_pyrex_atoms = False

if usePyrexAtomsAndBonds(): #bruce 080220 revised this
    # usePyrexAtomsAndBonds tests that we want to, and can, import all
    # necessary symbols from atombase
    from atombase import AtomDictBase, AtomBase
    class AtomDict(AtomDictBase):
        def __init__(self):
            AtomDictBase.__init__(self)
            self.key = atKey.next()
            return
        pass
    print "Using atombase.pyx in chem.py"
    _using_pyrex_atoms = True
else:
    def AtomDict():
        return { }
    class AtomBase:
        def __init__(self):
            pass
        def __getattr__(self, attr): # in class AtomBase
            raise AttributeError, attr
        pass
    pass

# == class Atom (and support code)

def _undo_update_Atom_jigs(archive, assy):
    """
    [register this to run after all Jigs, atoms, and bonds are updated,
    as cache-invalidator for a.jigs and b.pi_bond_obj]

    @warning: as of 060414 this also does essential undo updates unrelated to jigs.
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
        Utility._will_kill_count += 1
    mols = assy.allNodes(assy.Chunk) # note: this covers all Parts, whereas assy.molecules only covers the current Part.
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

# changedicts for class Atom, used by Undo and by dna updater
# [definitions moved from this file to global_model_changedicts.py, bruce 080510]

# These global dicts all map atom.key -> atom, for atoms which change in various ways (different for each dict).
# The dicts themselves (as opposed to their contents) never change (so other modules can permanently import them),
# but they are periodically processed and cleared.
# For efficiency, they're global and not weak-valued,
# so it's important to delete items from them when destroying atoms
# (which is itself nim, or calls to it are; destroying assy needs to do that ### TODO).

# obsolete comment:
# ###@@@ Note: These are not yet looked at, but the code to add atoms into them is supposedly completed circa bruce 060322.
# update 071106: some of them are looked at (and have been since Undo worked), but maybe not all of them.


from model.global_model_changedicts import _changed_parent_Atoms
    # record atoms w/ changed assy or molecule or liveness/killedness
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


from model.global_model_changedicts import _changed_structure_Atoms
    # tracks changes to element, atomtype, bond set, bond direction (not bond order #k)
    # WARNING: there is also a related but different global dict
    # earlier than this one in the same file (global_model_changedicts.py),
    # whose spelling differs only in 'A' vs 'a' in Atoms, and in having no initial underscore,
    # namely, changed_structure_atoms.
    #
    # This confusion should be cleaned up sometime, by letting that one just be a subscriber to this one,
    # and if efficiency demands it, first splitting this one into the part equivalent to that one, and the rest.
    #
    # Ways this one has more atoms added to it than that one does:
    # jigs, info, kill, bond direction. (See also the comment where the other one is defined.)
    # See also: _changed_parent_Atoms, which also covers kill (probably in a better way).
    #
    # related attributes: bonds, element, atomtype, info, jigs # (not only '.jigs =', but '.jigs.remove' or '.jigs.append')
    # (we include info since it's used for repeat-unit correspondences in extrude; this is questionable)
    # (we include jigs since they're most like a form of structure, and in future might have physical effects,
    #  and since the jigs for pi bonds are structural)

register_changedict( _changed_structure_Atoms, '_changed_structure_Atoms', ('bonds', 'element', 'atomtype', 'info', 'jigs') )


from model.global_model_changedicts import _changed_posn_Atoms
    # tracks changes to atom._posn (not clear what it'll do when we can treat baseposn as defining state)
    # related attributes: _posn

register_changedict( _changed_posn_Atoms, '_changed_posn_Atoms', ('_posn',) )


from model.global_model_changedicts import _changed_picked_Atoms
    # tracks changes to atom.picked (for live or dead atoms)
    # (not to _pick_time etc, we don't cover that in Undo)
    # related attributes: picked
    # WARNING: name is private, but it's directly accessed in ops_select.py

register_changedict( _changed_picked_Atoms, '_changed_picked_Atoms', ('picked',) )


from model.global_model_changedicts import _changed_otherwise_Atoms
    # tracks all other model changes to Atoms (display style, dnaBaseName)
    # related attributes: display, _dnaBaseName

register_changedict( _changed_otherwise_Atoms, '_changed_otherwise_Atoms', ('display', '_dnaBaseName') )


# Notes (design scratch):
# for which Atom attrs is the attr value mutable in practice? bonds, jigs, maybe _posn (probably not).
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
    """
    Prepare to kill some set of atoms (known to the caller) more efficiently than otherwise.
    Return a value which the caller should pass to the _prekill method on all (and ONLY) those atoms,
    before killing them.

    [#e Note: If we can ever kill atoms and chunks in the same operation, we'll need to revise some APIs
    so they can all use the same value of _will_kill_count, if we want to make that most efficient.]
    """
    ###e this should be merged with similar code in class Node
    Utility._will_kill_count += 1
    return Utility._will_kill_count
    
class Atom( PAM_Atom_methods, AtomBase, InvalMixin, StateMixin, Selobj_API):
    #bruce 050610 renamed this from class atom, but most code still uses "atom" for now
    # (so we have to assign atom = Atom, after this class definition, until all code has been revised)
    # update, bruce 071113: I am removing that assignment below. See comment there.
    #bruce 080327 moved a lot of PAM-specific methods to mixin PAM_Atom_methods.
    """
    An Atom instance represents one real atom, or one "singlet"
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
    _dnaBaseName = "" #bruce 080319 revised this; WARNING: accessed directly in DnaLadderRailChunk
    ghost = False #bruce 080529
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
        # note: self.molecule is initially None. Later it's self's chunk.
        # If self is then killed, it's _nullMol. Some buglike behavior might effectively
        # kill or never-make-fully-alive self's chunk, without removing self from it
        # (especially in nonstandardly-handled assys like the ones for the partlib).
        # Finally, undoing to before self was created will cause its .molecule to become None again.
        # In that state there is no direct way to figure out self's assy,
        # but it might have one, since it might be in its undo_archive and be able
        # to come back to life that way, by Redo. Or the redo stack might get cleared,
        # but self might still be listed in some dicts in that undo_archive (not sure),
        # and maybe in various global dicts (changedicts, glname dict, dna updater error dict, etc).
        # This makes it hard to destroy self and all its storage, when self's assy is destroyed.
        # To fix this, we might keep a dict in assy of all atoms ever in it,
        # and/or keep a permanent _f_assy field in self. Not yet decided. Making _nullMol per-assy
        # would not help unless we can always use it rather than None, but that's hard because
        # atoms initially don't know assy, and Undo probably assumes the initial state of .molecule
        # is None. So a lot of code would need analysis to fix that, whereas a new one-purpose
        # system to know self's assy would be simpler. But it takes RAM and might not really be needed.
        # The main potential need is to handle atoms found in changedicts with .molecule of None or _nullMol,
        # to ask their assy if it's destroyed (updater should ignore atom) or not (updater should handle
        # atom if it handles killed atoms). But do updaters ever need to handle killed atoms?
        # [bruce 080219 comment]

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
    _s_attr__dnaBaseName = S_DATA #bruce 080319
    # decided to leave out _s_attr_ghost, for now [bruce 080530]:
    ## _s_attr_ghost = S_DATA #bruce 080529; might not be needed (since no ops change this except on newly made atoms, so far)
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

    # The attributes _PAM3plus5_Pl_Gv_data and _f_Pl_posn_is_definitive
    # are only used by methods in our mixin superclass PAM_Atom_methods,
    # except for some of our foundational methods like Atom.copy()
    # (and soon, writemmp and a method for reading an info record),
    # but since anything here uses them, we define them here. [bruce 080523]

    _PAM3plus5_Pl_Gv_data = None
        # "+5 data", stored only on Ss3, Ss5 (PAM strand sugar atoms).
        #
        # This is now copyable as of 080523.
        # It needs to be savable in mmp file [coded, but mmpformat is not, and mmpread is not ###]
        #
        # It should be undoable in theory, but this would be slow and the bugs
        # it might cause to leave it out seem very unlikely, so it's not
        # undoable for now -- this will need to change if we implement
        # "minimize PAM3+5 as PAM5", since then a single undoable operation
        # (the minimize) can change the +5 data without ever converting it
        # to PAM5 in an in-between undo snapshot.

    _f_Pl_posn_is_definitive = True
        # friend attribute for temporary use by PAM3plus5 code on Pl atoms;
        # no need to be undoable or copyable or savable, since should always
        # be True during an Undo snapshot or copy or save operation.

    # these are needed for repeated destroy: [bruce 060322]
    _glname = 0 # made this private, bruce 080220
    if not _using_pyrex_atoms:
        key = 0   # BAD FOR PYREX ATOMS - class variable vs. instance variable

    _will_kill = 0 #bruce 060327

    _f_dna_updater_should_reposition_baggage = False #bruce 080404
    
    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  (in this case its gives the path of an 'atom' icon')
    # see PM.PM_SelectionListWidget.insertItems for an example use of this
    # attribute. 
    iconPath = "ui/modeltree/Single_Atom.png"

    # Text to be drawn floating over the atom.  Note, you must also
    # set chunk.chunkHasOverlayText for this to be used.  Do this by
    # just calling setOverlayText().
    overlayText = None

    # piotr 080822: The pdb_info dictionary stores information
    # read from PDB file (or equivalent information generated by 
    # Peptide Builder).
    # piotr 080828: Changed the default value of pdb_info to None and
    # moved it to here from __init__
    pdb_info = None

    # def __init__  is just below a couple undo-update methods

    def _undo_update(self):
        if self._f_dna_updater_should_reposition_baggage:
            del self._f_dna_updater_should_reposition_baggage
                # expose class default of False
            # ###REVIEW: will this come late enough to fix any explicit
            # sets by other undo effects? I think so, since it's only
            # set by user ops or creating bonds or transmuting atoms.
            # But Bond._changed_atoms runs at some point during Undo,
            # and if that comes later than this, it'll be a ###BUG.
            # And it might well be, so this needs analysis or testing.
            # If it's a bug, do this in a later pass over atoms, I guess.
            # [bruce 080404]
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
        self.molecule._f_lost_externs = True
        self.molecule._f_gained_externs = True
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
        """
        Create an Atom of element sym
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

        # done later, since our assy is not yet known: [bruce 080220]
        ## self._glname = assy.alloc_my_glselect_name( self)
        
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

        #bruce 080327 revised this to not use try/except routinely
        # (possible optimization, and for clarity)
        
        atype = None # might be changed during following if/else chain

        if type(sym) == type(""):
            # this is normal, since sym is usually an element symbol like 'C'
            self.element = PeriodicTable.getElement(sym)
        elif isinstance(sym, Atom):
            self.element = sym.element
            atype = sym.atomtype
        elif isinstance(sym, AtomType):
            self.element = sym.element
            atype = sym
        else:
            # note: passing an Element object would probably make sense
            # to allow, but is nim. [bruce 080514 comment]
            assert 0, "can't initialize Atom.element from %r" % (sym,)
        
        #e could assert self.element is now an Elem, but don't bother -- if not, we'll find out soon enough
        
        if atype is not None:
            assert atype.element is self.element # trivial in one of these cases, should improve #e
        
        # this atomtype atype (or the default one, if atype is None)
        # will be stored at the end of this init method.
        
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
            # Note: for info about what self.molecule is set to
            # when it's not self's chunk, see the long comment below the
            # undo declaration for the .molecule attribute
            # (i.e. the assignment of class attr _s_attr_molecule, above).
            # [bruce 080219 comment]
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

    _f_assy = None # friend attribute for classes Atom, Chunk, perhaps Bond,
        # and perhaps Undo and updaters [bruce 080220]
    
    def _f_set_assy(self, assy): #bruce 080220
        """
        [friend method for anything that can change our assy or be the first
         to realize what it is.]
        
        Set a new or different value of self._f_assy.
        Do necessary internal updates.

        @warning: NOT YET CALLED ENOUGH to be sure all atoms have _f_assy set
                  which have a well-defined assy. If that is needed by anything
                  that might run on non-live atoms, we'll have to find more places
                  to set it so we can be sure it's known for them.

        @note: self._f_assy might be None, or a different assy.
               (But I don't know if the "different assy" case
                ever occurs in practice, or if it works fully.)

        @note: as an important optimization, callers should only call this
               if assy is not self._f_assy.

        @note: the caller may or may not have already changed self.molecule
               to be consistent with assy, so we can't assume it's consistent.
               This could probably be changed if necessary.
        """
        assert assy is not None
        # (in fact it has to be an assembly object, but no assert is needed
        #  since the methods calls below will fail if it's not;
        #  but at least during devel we'll assert it's not the fake one from _nullMol:)
        assert type(assy) is not type("")
            # make sure we're not given a fake assy from _nullMol.
            # If we ever are, we'll need a special case in the caller.
        
        # leave old assy, if any
        if self._f_assy is not None:
            print "%r._f_set_assy: leaving old assy %r, for new one %r. Implem of this case is untested." % \
                  (self, self._f_assy, assy)
            self._f_assy.dealloc_my_glselect_name( self, self._glname)

        # join new assy
        self._glname = assy.alloc_my_glselect_name( self)
            # needed before drawing self or its bonds,
            # so those must ask for it via self.get_glname(glpane),
            # which calls this method if necessary to set it
            # [bruce 050610, revised 080220]
        self._f_assy = assy
        
        return

    def _assy_may_have_changed(self): #bruce 080220; UNTESTED & not yet used, see comment
        """
        [private method, for _undo_update or similar code]
        See if our assy changed, and if so, call _f_set_assy.
        """
        # Note:
        # This method is probably not needed, since if Undo changes
        # self.molecule, it must change it to a value it had before,
        # when last alive. (If atoms were moved between assys which
        # both supported Undo, they could end up in both at once;
        # therefore they can't be. If they are moved between assys
        # but only the new one supports Undo, I think this reasoning
        # remains valid.)
        # So I did not yet figure out where to add a call to it for
        # Undo (I'm not sure if .molecule has changed when _undo_update
        # is called, since IIRC it's changed in a special case step in
        # undo). So, it is not yet being called, and it's UNTESTED.
        # [bruce 080220/080223]
        chunk = self.molecule
        if chunk is not None and not chunk.isNullChunk():
            assy = chunk.assy
            if self._f_assy is not assy:
                self._f_set_assy(assy)
        return
    
    def _undo_aliveQ(self, archive): #bruce 060406
        """
        Would this (Atom) object be picked up as a child object in a (hypothetical) complete scan of children
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
    # Revision for dna data model, bruce 080320: remove entries that
    # transmute *to* deprecated PAM elements when dna updater is active.
    # As of now, all entries go either to or from deprecated elements
    # (or both), but some will be retained since they are
    # "from deprecate to non-deprecated". But they won't normally show up
    # to users since they only show up on applicable elements.
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
    _transmuteContextMenuEntries_for_dna_updater = None # replaced at runtime, within class
    def _init_transmuteContextMenuEntries_for_dna_updater(self): #bruce 080320
        """
        [private helper]

        Remove entries going *to* deprecated PAM elements
        from class constant _transmuteContextMenuEntries
        to initialize class constant
        _transmuteContextMenuEntries_for_dna_updater.
        """
        assert self._transmuteContextMenuEntries_for_dna_updater is None
        input = self._transmuteContextMenuEntries
        output = {} # modified below
        testing = False
        if testing:
            input['C'] = ['Si'] # works
        for fromSymbol in input.keys():
            fromElement = PeriodicTable.getElement(fromSymbol)
            # don't disallow "from" a deprecated element --
            # it might help users fix their input errors!
            ## if fromElement.deprecated_to:
            ##     continue
            for toSymbol in input[fromSymbol]:
                toElement = PeriodicTable.getElement(toSymbol)
                if toElement.deprecated_to:
                    continue
                if testing:
                    print "\nfyi: retaining transmute entry: %r -> %r" % (fromSymbol, toSymbol)
                output.setdefault(fromSymbol, [])
                output[fromSymbol].append(toSymbol)
                continue
            continue
        self.__class__._transmuteContextMenuEntries_for_dna_updater = output
        if testing:
            print "\nfyi: _transmuteContextMenuEntries_for_dna_updater =", output
        return
    def make_selobj_cmenu_items(self, menu_spec):
        """
        Add self-specific context menu items to <menu_spec> list when self is the selobj,
        in modes that support it (e.g. depositMode and selectMode and subclasses).
        """
        if self.element.pam:
            #bruce 080401
            pam_atom_entries = self._pam_atom_cmenu_entries()
            if pam_atom_entries:
                menu_spec.extend(pam_atom_entries)
            pass
        transmute_entries = self._transmuteContextMenuEntries # non-updater version
        if dna_updater_is_enabled():
            # bruce 080320: use only entries not involving deprecated PAM elements
            transmute_entries = self._transmuteContextMenuEntries_for_dna_updater
            if transmute_entries is None:
                self._init_transmuteContextMenuEntries_for_dna_updater()
                transmute_entries = self._transmuteContextMenuEntries_for_dna_updater
                assert transmute_entries is not None
            pass
        fromSymbol = self.element.symbol
        if (transmute_entries.has_key(fromSymbol)):
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
                    ms1 = crossover_menu_spec(self, selatoms)
                    if ms1:
                        menu_spec.append(None) # separator
                        menu_spec.extend(ms1)
            menu_spec.append(None) # separator
            for toSymbol in transmute_entries[fromSymbol]:
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
            from foundation.undo_archive import _undo_debug_obj # don't do this at toplevel
            if self is _undo_debug_obj:
                checked = 'checked'
            else:
                checked = None
            item = ('_undo_debug_obj = %r' % self, self.set_as_undo_debug_obj, checked)
            menu_spec.append(item)
        return

    def nodes_containing_selobj(self): #bruce 080507
        """
        @see: interface class Selobj_API for documentation
        """
        # include a lot of safety conditions in case of calls
        # on out of date selobj...
        if self.killed():
            # note: includes check of chunk is None or chunk.isNullChunk()
            return []
        chunk = self.molecule
        return chunk.containing_nodes()
        
    def set_as_undo_debug_obj(self):
        undo_archive._undo_debug_obj = self
        undo_archive._undo_debug_message( '_undo_debug_obj = %r' % self )
        return

    def setOverlayText(self, text):
        self.overlayText = text
        self.molecule.chunkHasOverlayText = True
    
    def __getattr__(self, attr): # in class Atom
        assert attr != 'xyz' # temporary: catch bugs in bruce 060308 rewrite
        try:
            return AtomBase.__getattr__(self, attr)
        except AttributeError:
            return InvalMixin.__getattr__(self, attr)

    def destroy(self): #bruce 060322 (not yet called) ###@@@
        """
        [see comments in Node.destroy or perhaps StateMixin.destroy]
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
        if self._glname: #bruce 080917 revised this entire statement (never tested, before or after)
            assy = self._f_assy ###k
            if assy:
                assy.dealloc_my_glselect_name( self, self._glname )
            # otherwise no need, I think (since changing assy deallocates it too)
            del self._glname
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
        """
        Unset self.atomtype, so that it will be guessed when next used
        from the number of bonds at that time.
        """
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

        @warning: This is only correct for a new atom if it has
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
        """
        Return the absolute position of this atom in space.
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
        """
        Return our posn, as the simulator should see it -- same as posn except for Singlets,
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
        """
        Like posn, but return the mol-relative position.
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
        """
        set this atom's absolute position,
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
    
    def adjBaggage(self, atom, nupos):
        """
        We're going to move atom, a neighbor of yours, to nupos,
        so adjust the positions of your singlets (and other baggage) to match.
        """
        ###k could this be called for atom being itself a singlet,
        # when dragging a singlet? [bruce 050502 question]
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
        baggage, nonbaggage = self.baggage_and_other_neighbors()
        if atom in baggage:
            #bruce 060629 for safety (don't know if ever needed)
            # make sure atom counts as nonbaggage
            baggage.remove(atom)
            nonbaggage.append(atom)
        ## nonbaggage = self.realNeighbors()
        old = V(0,0,0)
        new = V(0,0,0)
        for atom_nb in nonbaggage:
            old += atom_nb.posn() - apo
            if atom_nb is atom:
                new += nupos-apo
            else:
                new += atom_nb.posn() - apo
        if nonbaggage:
            # slight safety tweaks to old code, though we're about to add new
            # code to second-guess it [bruce 060629]
            old = norm(old) #k not sure if these norms make any difference
            new = norm(new)
            if old and new:
                q = Q(old, new)
                for atom_b in baggage: ## was self.singNeighbors()
                    atom_b.setposn(q.rot(atom_b.posn() - apo) + apo)
                        # similar to code in drag_selected_atom, but not identical
            #bruce 060629 for bondpoint problem
            self.reposition_baggage(baggage, (atom, nupos))
        return
    
    def __repr__(self):
        return self.element.symbol_for_printing + str(self.key)

    def __str__(self):
        return self.element.symbol_for_printing + str(self.key)

    def prin(self):
        """
        for debugging
        """
        lis = map((lambda b: b.other(self).element.symbol), self.bonds)
        print self.element.name, lis

    _f_valid_neighbor_geom = False # privately, also used as valid_data tuple
        # this is reset to False by some Atom methods, and when any bond of self
        # is invalidated, which covers (I think) motion or element change of a
        # neighbor atom.
    _f_checks_neighbor_geom = False # kluge: set in _changed_structure based on element
    bond_geometry_error_string = ""

    def _f_invalidate_neighbor_geom(self): # bruce 080214
        """
        Cause self.bond_geometry_error_string to be recomputed
        when self.check_bond_geometry() is next called.
        [friend method for classes Atom & Bond]
        """
        self._f_valid_neighbor_geom = False

        # too slow to also do this:
        ## self.molecule.changeapp(0)
        #
        # Note: in theory we should now do self.molecule.changeapp(0).
        # In practice this is too slow -- it would remake chunk display lists
        # whenever they were dragged (on every mouse motion), even if a lot of
        # chunks are being dragged together.
        #
        # Possible solutions:
        #
        # - short term mitigation: do a changeapp later, when something else calls
        #   check_bond_geometry. This seems to happen at the end of the drag
        #   or shortly after (not sure why). Note, this may be an illegal or lost
        #   call of changeapp, since it can happen when drawing that same chunk.
        #   ### REVIEW THIS... could we replace it with an incr of a counter in
        #   the chunk, added to havelist data... or just put that inside changeapp
        #   itself, so calls of changeapp at any time are permitted...??)
        #
        # - long term: when dragging selections rigidly, optimize by knowing
        #   what needs recomputing due to "crossing the boundary" (between
        #   selected and non-selected).
        #
        # - short term kluge: when drawing an external bond, have it overdraw the
        #   error atoms with error indicators for this purpose. Since those bonds
        #   are always drawn, let them be the only indicator of this error for
        #   atoms that have any external bonds (otherwise we'd fail to turn off
        #   error indicators soon enough when errors in a chunk were fixed by
        #   dragging that chunk). For an interior atom, if a neighbor moves (other
        #   than during rigid motion of their shared chunk), that will invalidate
        #   its chunk's display list, ensuring it gets redrawn right away,
        #   so no other inval is needed. AFAIK this is complete and correct.
        #
        # I'll do only the "short term kluge" solution, for now. [bruce 080214]
        return
    
    def check_bond_geometry(self, external = -1): # bruce 080214
        # todo: probably should move this method within class
        """
        Check the geometry of our bonds, and update
        self.bond_geometry_error_string with current data.
        Also return it for convenience, as modified by the
        <external> option. (For no error which should be displayed
        for that value of <external>, it's "".)

        Be fast if nothing relevant has changed.

        @param external: If -1 (default), return the new or
                         changed value of self.bond_geometry_error_string.
                         If False, only return that value if
                         self._f_draw_bond_geometry_error_indicator_externally
                         is False, otherwise return "".
                         This returns the error indication to use when drawing
                         this atom itself into a chunk display list.
                         If True, only return that value if
                         self._f_draw_bond_geometry_error_indicator_externally
                         is True, otherwise return "".
                         This returns the error indication to use when drawing
                         external bonds connected to this atom (which are not
                         drawn into a chunk display list).

        @return: new or unchanged value of self.bond_geometry_error_string,
                 unless external is passed (see that param's doc for more info).
        """
##        # TODO: update this while dragging a chunk, for that chunk's
##        # external bonds; right now it only updates when the drag is done.
##        # (Not sure if that's due to a lack of inval or a lack of calling this.
##        #  Or more likely it's a LOGIC BUG -- this does changeapp, but that is needed
##        #  when this is invalled, if it would happen when we recompute!
##        #  In fact, it might be illegal to do it here (since we might be drawing
##        #  that very same chunk).
        current_data = (self.molecule.bond_inval_count,) # must never equal False
        if self._f_valid_neighbor_geom != current_data:
            # need to recompute/update
            self._f_valid_neighbor_geom = current_data
            try:
                error_string = self._recompute_bond_geometry_error_string()
            except:
                error_string = \
                    "exception in _recompute_bond_geometry_error_string"
                        # only seen in case of bugs
                msg = "\n*** BUG: %s: " % error_string
                print_compact_stack(msg)                
            if error_string != self.bond_geometry_error_string:
                # error string changed
                if (not error_string) != (not self.bond_geometry_error_string):
                    # even its set- or cleared-ness changed
                    ## self.molecule.changeapp(0) # in case of error color, etc
                        # this might not be safe, and is not sufficient,
                        # so don't do it at all. (For more info see comment in
                        # _f_invalidate_neighbor_geom.)
                    if debug_pref("report bond_geometry_error_string set or clear?",
                                  Choice_boolean_False,
                                  prefs_key = True ):
                        print "fyi: check_bond_geometry(%r) set or cleared error string %r" % (self, error_string)
                self.bond_geometry_error_string = error_string
            pass
        if self.bond_geometry_error_string:
            # make sure drawing code knows whether to draw the error indicator
            # into the chunk display list or not (for explanation, see comment
            # in _f_invalidate_neighbor_geom)
            draw_externally = not not self.has_external_bonds()
            self._f_draw_bond_geometry_error_indicator_externally = draw_externally # this attr might never be used
            if external == -1 or external == draw_externally:
                return self.bond_geometry_error_string
        return ""

    _f_draw_bond_geometry_error_indicator_externally = True

    def has_external_bonds(self): # bruce 080214 # should refile within this class
        """
        Does self have any external bonds?
        (i.e. bonds to atoms in different chunks)
        """
        for bond in self.bonds:
            if bond.atom1.molecule is not bond.atom2.molecule:
                ## todo: def bond.is_external()?
                return True
        return False
    
    def _recompute_bond_geometry_error_string(self): # bruce 080214
        # todo: should refactor, put some in AxisAtom section, or atomtype
        """
        Recompute and return an error string about our bond geometry,
        which is "" if there is no error.
        """
        if not self._f_checks_neighbor_geom:
            # optimize elements that don't do checks at all
            return ""
        if self.element.symbol in ('Ax3', 'Ax5', 'Ae3', 'Ae5'): # not correct for Gv5!
            # Prototype implem for just these elements.
            # (Ideally, the specific code for this would be in the atomtype.)
            if len(self.bonds) != self.atomtype.valence: # differs for Ax and Ae
                return "valence error"
            strand_neighbors = self.strand_neighbors()
            if not len(strand_neighbors) in (1, 2):
                # this is an error even if pref_permit_bare_axis_atoms() is true
                if not strand_neighbors:
                    return "bare axis"
                else:
                    return "more than 2 strand neighbors"
            if len(strand_neighbors) == 2:
                # check minor groove angle
                # REVIEW: when this error happens, can we or dna updater
                # propogate it throughout base pair?
                ss1, ss2 = strand_neighbors
                angle = atom_angle_radians( ss1, self, ss2 ) * 180/math.pi
                angle = intRound(angle)
                ## low, high = 130, 155
                low = env.prefs[dnaMinMinorGrooveAngle_prefs_key]
                high = env.prefs[dnaMaxMinorGrooveAngle_prefs_key]
                ### TODO: make sure changing those invalidates enough
                # to recompute this, and redraw if needed. BUG until done.
                # Probably easiest to refactor: separate recomputing the angle
                # (inval code same as now) from testing it against limits
                # (done each time we draw it). The latter would be part of
                # drawing code, and would test all related prefs, and capture
                # their usage as for other drawing prefs. [bruce 080326]
                if not (low <= angle <= high): 
                    error = "minor groove angle %d degrees (should be %d-%d)" % \
                            (angle, low, high)
                    return error
        return ""

    _BOND_GEOM_ERROR_RADIUS_MULTIPLIER = 1.5 # not sure this big is good
        # (or that a solid sphere is the best error indicator)
    
    def overdraw_bond_geometry_error_indicator(self, glpane, dispdef):
        #bruce 080214, revised 080406
        """
        ###doc
        """
        assert self._f_draw_bond_geometry_error_indicator_externally # for now
        assert self.bond_geometry_error_string # make private??
        
        disp = dispdef ### REVIEW -- is it ok if diDEFAULT is passed?? does that happen?
        pos = self.posn() # assume in abs coords
        pickedrad = 2 ### STUB, WRONG -- unless we want it to stay extra big; maybe we do...
            # (but, inconsistent with the value used for interior atoms
            #  by another call of this method; but this kind of error is rare
            #  on interior atoms, maybe nonexistent when dna updater is active)
        self.draw_error_wireframe_if_needed( glpane, disp, pos, pickedrad,
            external = True,
            prefs_key = dnaDisplayMinorGrooveErrorIndicators_prefs_key,
            color_prefs_key = dnaMinorGrooveErrorIndicatorColor_prefs_key
         )
        return

    def get_glname(self, glpane): #bruce 080220
        """
        Return our OpenGL GLSELECT name, allocating it now
        (in self._f_set_assy, using glpane for its assy)
        if necessary.
        """
        glname = self._glname # made this private, 080220
        if not glname:
            # Note: testing for this here seems correct, and might even be more
            # principled than in Chunk.addatom (where I iniiially tried testing
            # for self._f_assy, an equivalent test for now, 080220), and is
            # surely more efficient, and is easier since addatom is inlined a
            # lot. BUT this place alone is not enough to guarantee self._f_assy
            # gets set for all atoms that have one. See comment about that in
            # self._f_set_assy(). [bruce 080220]
            assert self._f_assy is None
            if glpane.assy is not self.molecule.assy:
                print "\nbug?: glpane %r .assy %r is not %r.molecule %r .assy %r" % \
                      (glpane, glpane.assy, self, self.molecule, self.molecule.assy )
            assy = glpane.assy
                # todo: in principle we'd prefer self.molecule.assy if it's always set;
                # but unless we add code to look for it carefully and fall back to
                # glpane.assy, that's less safe, so use this for now. This is the only
                # reason we need glpane as an argument, btw. The glname doesn't depend
                # on it and will never need to AFAIK.
            self._f_set_assy( assy) # this sets self._glname (and nothing else does)
                # note: it's not clearly better to set _f_assy than to just set _glname
                # directly here. This will change if more things use _f_assy, but then
                # other places to set it will also be needed.
            glname = self._glname
            assert glname
            ## print "fyi: set glname during draw of %r, assy = %r, glpane = %r" % \
            ##       (self, assy, glpane)
            pass
        return glname

    def draw(self, glpane, dispdef, col, level, special_drawing_handler = None, special_drawing_prefs = USE_CURRENT):
        """
        Draw this atom (self), using an appearance which depends on
        whether it is picked (selected)
        and its display mode (possibly inherited from dispdef).
        An atom's display mode overrides the inherited one from
        the molecule or glpane, but a molecule's color (passed as col)
        overrides the atom's element-dependent color.

        Also draws picked-atom wireframe, but doesn't draw any bonds.
        [Caller must draw bonds separately.]
        
        @return: the display mode we used (whether self's or inherited),
                 or will use (if our drawing is handled by
                 special_drawing_handler).

        @param col: the molecule color to use, or None to use per-atom colors.
                    (Should not be a boolean-false color -- black is ok if
                     passed as (0,0,0), but not if passed as V(0,0,0).)

        @note: This method no longer treats glpane.selatom specially
        (caller can draw selatom separately, on top of the regular atom).
        """
        assert not self.__killed

        # figure out display style to use
        disp, drawrad = self.howdraw(dispdef)
        
        # review: future: should we always compute _draw_atom_style here,
        # just once, so we can avoid calling it multiple times inside
        # various methods we call?

        if special_drawing_handler and (
            self._draw_atom_style(special_drawing_handler = special_drawing_handler) ==
            'special_drawing_handler'
           ):
            # defer all drawing of self to special_drawing_handler [bruce 080605]
            def func(special_drawing_prefs, args = (glpane, dispdef, col, level)):
                self.draw(*args, **dict(special_drawing_prefs = special_drawing_prefs))
            special_drawing_handler.draw_by_calling_with_prefsvalues(
                SPECIAL_DRAWING_STRAND_END, func )
            return disp
        
        # if we didn't defer, we shouldn't use special_drawing_handler at all
        del special_drawing_handler

        glname = self.get_glname(glpane)

        # note use of basepos (in atom.baseposn) since it's being drawn under
        # rotation/translation of molecule
        pos = self.baseposn()
        
        if disp == diTUBES:
            pickedrad = drawrad * 1.8 # this code snippet is now shared between draw and draw_in_abs_coords [bruce 060315]
        else:
            pickedrad = drawrad * 1.1
        
        color = col or self.drawing_color()

        glPushName( glname) #bruce 050610 (for comments, see same code in Bond.draw)
            # (Note: these names won't be nested, since this method doesn't draw bonds;
            #  if it did, they would be, and using the last name would be correct,
            #  which is what's done (in GLPane.py) as of 050610.)
        ColorSorter.pushName(glname)
        try:
            if disp in (diTrueCPK, diBALL, diTUBES):
                self.draw_atom_sphere(color, pos, drawrad, level, dispdef,
                                      special_drawing_prefs = special_drawing_prefs )
            self.draw_wirespheres(glpane, disp, pos, pickedrad,
                                  special_drawing_prefs = special_drawing_prefs )
        except:
            ColorSorter.popName()
            glPopName()
            print_compact_traceback("ignoring exception when drawing atom %r: " % self)
        else:
            ColorSorter.popName()
            glPopName()

        return disp # from Atom.draw. [bruce 050513 added retval to help with an optim]

    def drawing_color(self, molcolor = None): #bruce 070417; revised, 080406
        # BUG: most calls have the bug of letting molcolor override this. ###FIX
        """
        Return the color in which to draw self, and certain things that touch self.
        This is molcolor or self.element.color by default
        (where molcolor is self.molecule.drawing_color() if not supplied).
        """
        if molcolor is None:
            molcolor = self.molecule.drawing_color()
        color = molcolor
        if color is None:
            color = self.element.color
##        # see if warning color is needed
##        if self.check_bond_geometry(): #bruce 080214 (minor groove angle)
##            ### REVIEW: should this be done for interior atoms? maybe only for some calls of this method??
##            color = orange
##        elif self._dna_updater__error: #bruce 080130
##            color = orange
        return color

    # bruce 070409 split this out of draw_atom_sphere; 
    # 070424 revised return value (None -> "")
    def _draw_atom_style(self, special_drawing_handler = None, special_drawing_prefs = None):
        """
        [private helper method for L{draw_atom_sphere}, and perhaps related
        methods like L{draw_wirespheres}]

        Return a short hardcoded string (known to L{draw_atom_sphere}) saying
        in what style to draw the atom's sphere.

        @param special_drawing_handler: if not None, an object to which all drawing
                                   which is dependent on special_drawing_prefs
                                   needs to be deferred. In this method, this
                                   argument is used only for tests
                                   which let us tell the caller whether we need
                                   to defer to it.

        @param special_drawing_prefs: an object that knows how to find out
                                   how to draw strand ends. Never passed
                                   along with special_drawing_handler -- only passed
                                   if we're doing drawing which was *already*
                                   deferred do that.
        
        @return: Returns one of the following values:
                 - "" (Not None) means to draw an actual sphere.
                 - "special_drawing_handler" means to defer drawing to the special_drawing_handler.
                 - "arrowhead-in" means to draw a 5' arrowhead.
                 - "arrowhead-out" means to draw a 3' arrowhead.
                 - "do not draw" means don't draw anything.
                 - "bondpoint-stub" means to draw a stub.
                 - 'five_prime_end_atom' means draw 5' end base atom in a special 
                   color if arrows are not drawn at 5' end
                 - 'three_prime_end_atom' means draw 3' end base atom in a special 
                   color if arrows are not drawn at 3' end

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

            # figure out whether to defer drawing to special_drawing_handler [bruce 080605]
            if self.isFivePrimeEndAtom() or \
               self.isThreePrimeEndAtom() or \
               self.strand_end_bond() is not None:
                if special_drawing_handler and \
                   special_drawing_handler.should_defer( SPECIAL_DRAWING_STRAND_END):
                    # tell caller to defer drawing self to special_drawing_handler
                    return 'special_drawing_handler'
                else:
                    # draw using the values in special_drawing_prefs
                    res = self._draw_atom_style_using_special_drawing_prefs( special_drawing_prefs )
                    if res:
                        return res
                pass
            pass
        return "" # from _draw_atom_style

    def _draw_atom_style_using_special_drawing_prefs(self, special_drawing_prefs):
        """
        [private helper for _draw_atom_style]
        """
        #bruce 080605 split this out, revised it
        assert special_drawing_prefs, "need special_drawing_prefs"
            # note: for optimal redraw (by avoiding needless remakes of some
            # display lists), only access each of the values this can provide
            # when that value is actually needed to do the drawing.
        
        if self.isFivePrimeEndAtom() and not special_drawing_prefs[arrowsOnFivePrimeEnds_prefs_key]:
            # (this happens even if self.isThreePrimeEndAtom() is also true
            #  (which may happen for a length-1 PAM3 strand);
            #  I guess that's either ok or good [bruce 080605 comment])
            return 'five_prime_end_atom'
        elif self.isThreePrimeEndAtom() and not special_drawing_prefs[arrowsOnThreePrimeEnds_prefs_key]:
            return 'three_prime_end_atom'
        
        bond = self.strand_end_bond()
            # never non-None if self has two bonds with directions set
            # (assuming no errors) -- i.e. for -Ss3-X, only non-None
            # for the X, never for the Ss3
            # [bruce 080604 quick analysis, should re-review]
        if bond is not None:
            # Determine how singlets of strand open bonds should be drawn.
            # draw_bond_main() takes care of drawing bonds accordingly.
            # - mark 2007-10-20.
            if bond.isFivePrimeOpenBond() and special_drawing_prefs[arrowsOnFivePrimeEnds_prefs_key]:
                return 'arrowhead-in'
            elif bond.isThreePrimeOpenBond() and special_drawing_prefs[arrowsOnThreePrimeEnds_prefs_key]:
                return 'arrowhead-out'
            else:
                return 'do not draw'
            #e REVIEW: does Bond.draw need to be updated due to this, if "draw bondpoints as stubs" is True?
            #e REVIEW: Do we want to draw even an isolated Pe (with bondpoint) as a cone, in case it's in MMKit,
            #  since it usually looks like a cone when it's correctly used? Current code won't do that.
            #e Maybe add option to draw the dir == 0 case too, to point out you ought to propogate the direction
            pass
        return ""

    def draw_atom_sphere(self,
                         color,
                         pos,
                         drawrad,
                         level,
                         dispdef,
                         abs_coords = False,
                         special_drawing_prefs = USE_CURRENT
                        ):
        """
        #doc

        @param dispdef: can be None if not known to caller

        @param special_drawing_handler: see _draw_atom_style for related doc
        
        @param special_drawing_prefs: see _draw_atom_style for doc

        @return: None
        """
        #bruce 060630 split this out for sharing with draw_in_abs_coords
        style = self._draw_atom_style( special_drawing_prefs = special_drawing_prefs)
        if style == 'do not draw':
            if disable_do_not_draw_open_bonds(): ##  or self._dna_updater__error:
                # (first cond is a debug_pref for debugging -- bruce 080122)
##                # (the other cond [bruce 080130] should be a more general
##                #  structure error flag...)
                style = ''
##                color = orange
            else:
                return
##        if self.check_bond_geometry(external = False): #bruce 080214 (needed?)
##            color = orange
##        elif self._dna_updater__error: #bruce 080130; needed both here and in self.drawing_color()
##            color = orange
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
            rad = other.highlighting_radius(dispdef) # ok to pass None
            out = norm(pos - otherpos)
            buried = max(0, rad - vlen(pos - otherpos))
            inpos = pos - 0.015 * out
            outpos = pos + (buried + 0.015) * out # be sure we're visible outside a big other atom
            drawcylinder(color, inpos, outpos, drawrad, 1) #e see related code in Bond.draw; drawrad is slightly more than the bond rad
        elif style.startswith('arrowhead-'):
            #arrowColor will be changed later
            arrowColor = color                    
            # two options, bruce 070415:
            # - arrowhead-in means pointing in along the strand_end_bond
            # - arrowhead-out means pointing outwards from the strand_end_bond
            if style == 'arrowhead-in':
                bond = self.strand_end_bond()
                other = bond.other(self)
                otherdir = 1 
                #Following implements custom arrowhead colors for the 3' and 5' end
                #(can be changed using Preferences > Dna page) Feature implemented 
                #for Rattlesnake v1.0.1
                bool_custom_arrowhead_color = special_drawing_prefs[
                    useCustomColorForFivePrimeArrowheads_prefs_key]                
                if bool_custom_arrowhead_color and not abs_coords:
                    arrowColor = special_drawing_prefs[
                        dnaStrandFivePrimeArrowheadsCustomColor_prefs_key]
                
            elif style == 'arrowhead-out':
                bond = self.strand_end_bond()
                other = bond.other(self)
                otherdir = -1
                #Following implements custom arrowhead colors for the 3' and 5' end
                #(can be changed using Preferences > Dna page) Feature implemented 
                #for Rattlesnake v1.0.1
                bool_custom_arrowhead_color = special_drawing_prefs[
                    useCustomColorForThreePrimeArrowheads_prefs_key]                
                if bool_custom_arrowhead_color and not abs_coords:
                    arrowColor = special_drawing_prefs[
                        dnaStrandThreePrimeArrowheadsCustomColor_prefs_key]
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
            
            drawpolycone(arrowColor,
                         [[pos[0] - 2 * axis[0], 
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
                        [arrowRadius, arrowRadius, 0, 0] # Radius array
                       )
        elif style == 'five_prime_end_atom':
            sphereColor = color
            bool_custom_color = special_drawing_prefs[
                    useCustomColorForFivePrimeArrowheads_prefs_key]                
            if bool_custom_color and not abs_coords:
                sphereColor = special_drawing_prefs[
                    dnaStrandFivePrimeArrowheadsCustomColor_prefs_key]
                    
            drawsphere(sphereColor, pos, drawrad, level)
        elif style == 'three_prime_end_atom':
            sphereColor = color
            bool_custom_color = special_drawing_prefs[
                    useCustomColorForThreePrimeArrowheads_prefs_key]                
            if bool_custom_color and not abs_coords:
                sphereColor = special_drawing_prefs[
                    dnaStrandThreePrimeArrowheadsCustomColor_prefs_key]
            drawsphere(sphereColor, pos, drawrad, level)
        else:
            if style:
                print "bug (ignored): unknown _draw_atom_style return value for %r: %r" % (self, style,)
            if 0: #### experiment, unfinished [bruce 080917]
                verts = [b.center for b in self.bonds]
                if len(verts) == 4:
                    drawtetrahedron(color, verts)
                elif len(verts) == 3:
                    drawtriangle(color, verts)
                pass ###
            else:
                drawsphere(color, pos, drawrad, level)
        return # from draw_atom_sphere
    
    def draw_wirespheres(self, glpane, disp, pos, pickedrad, special_drawing_prefs = USE_CURRENT):
        #bruce 060315 split this out of self.draw so I can add it to draw_in_abs_coords
        if self._draw_atom_style(special_drawing_prefs = special_drawing_prefs).startswith('arrowhead-'):
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
                # russ 080530: Changed to pref from PickedColor constant (blue).
                color = env.prefs[selectionColor_prefs_key]
            drawwiresphere(color, pos, pickedrad) ##e worry about glname hit test if atom is invisible? [bruce 050825 comment]
        #bruce 050806: check valence more generally, and not only for picked atoms.
        self.draw_error_wireframe_if_needed(glpane, disp, pos, pickedrad,
                                          external = False,
                                          prefs_key = showValenceErrors_prefs_key )
        return

    def draw_error_wireframe_if_needed(self, glpane, disp, pos, pickedrad,
                                     external = -1,
                                     prefs_key = None,
                                     color_prefs_key = None ):
        #bruce 080406 split this out, added options
        """
        ###doc

        @param external: see docstring of self.check_bond_geometry
        """
        if disp == diINVISIBLE: #bruce 050825 added this condition to fix bug 870
            return
        # The calling code in draw_wirespheres only checks for number of bonds.
        # Now that we have higher-order bonds, we also need to check valence more generally.
        # The check for glpane class is a kluge to prevent this from showing in thumbviews: should remove ASAP.
        #####@@@@@ need to do this in atom.getinfo().
        #e We might need to be able to turn this [what?] off by a preference setting; or, only do it in Build mode.
        # Don't check prefs until we know we need them, to avoid needless
        # gl_update when user changes prefs value.
        if not glpane.should_draw_valence_errors():
            return
        if not self.bad_valence(external = external):
            return
        if prefs_key is not None and not env.prefs[prefs_key]:
            return
        if color_prefs_key is not None:
            color = env.prefs[color_prefs_key]
        else:
            color = pink
        drawwiresphere(color, pos, pickedrad * 1.08) # experimental, but works well enough for A6.
        #e we might want to not draw this when self.bad() but draw that differently,
        # and optim this when atomtype is initial one (or its numbonds == valence).
        return

    def draw_overlap_indicator(self, prior_atoms_too_close = ()): # bruce 080411
        """
        Draw an indicator around self which indicates that it is too close
        to the atoms in the list prior_atoms_too_close (perhaps empty).

        In the initially implemented calling code, this will be called
        multiple times per atom -- on the average, about once for each
        other atom it's too close to, but possibly as much as twice
        per other close atom. More specifically: for each pair of too-close
        atoms, and for each ordering of that pair as a1, a2,
        this will be called exactly once on a1 with a2 an element of
        prior_atoms_too_close. If a1 was scanned first, it will
        receive a2 alone in that list; otherwise it might receive
        other atoms in that list in the same call.

        This means that if the distance tolerance should depend on the
        elements or bonding status (or any other property) of a pair
        of too-close atoms, this can be implemented in this method
        by only drawing the indicator around seld if one of the atoms
        in the argument is in fact too close to self, considering
        that property of the pair of atoms.

        (This could be optimized, but only by using new code in the caller.)
        """
        color = yellow # ??
        pos = self.posn()
        pickedrad = self.drawing_radius(picked_radius = True)
        draw_at_these_radii = []
        for other in prior_atoms_too_close:
            otherrad = other.drawing_radius(picked_radius = True)
            maxrad = max(otherrad, pickedrad)
            if maxrad not in draw_at_these_radii:
                draw_at_these_radii.append(maxrad)
        for maxrad in draw_at_these_radii:
            # this is to make it easier to see a small atom (e.g. a bondpoint)
            # buried inside another one.
            radius = maxrad * 1.12
            drawwiresphere(color, pos, radius)
        return
        
    def max_pixel_radius(self): #bruce 070409
        """
        Return an estimate (upper bound) of the maximum distance
        from self's center to any pixel drawn for self.
        """
        res = self.highlighting_radius() + 0.2
        if self._draw_atom_style(special_drawing_prefs = USE_CURRENT).startswith('arrowhead-'):
            res *= 3
        return res
    
    def bad(self): #bruce 041217 experiment; note: some of this is inlined into self.getinfo()
        """
        is this atom breaking any rules?
        @note: this is used to change the color of the atom.picked wireframe
        @note: not all kinds of rules are covered.
        @see: _dna_updater__error (not covered by this; maybe it should be)
        """
        if self.element is Singlet:
            # should be correct, but this case won't be used as of 041217 [probably no longer needed even if used -- 050511]
            numbonds = 1
        else:
            numbonds = self.atomtype.numbonds
        return numbonds != len(self.bonds) ##REVIEW: this doesn't check bond valence at all... should it??

    def bad_valence(self, external = -1):
        #bruce 050806; should review uses (or inlinings) of self.bad() to see if they need this too ##REVIEW
        #bruce 080406 added external option
        """
        is this atom's valence clearly wrong, considering
        valences presently assigned to its bonds?

        @param external: see docstring of self.check_bond_geometry().
        """
        # WARNING: keep the code of self.bad_valence() and self.bad_valence_explanation() in sync! 
        #e we might optimize this by memoizing it (in a public attribute), and letting changes to any bond invalidate it.
        # REVIEW: see comments in bad_valence_explanation
        # NOTE: to include check_bond_geometry, we might need an "external" arg to pass it
        bonds = self.bonds
        if self.element is Singlet:
            ok = (len(bonds) == 1)
            return not ok # any bond order is legal on an open bond, for now
        if self.atomtype.numbonds != len(bonds):
            ok = False
            return not ok
        minv, maxv = self.min_max_actual_valence()
            # min and max reasonable interpretations of actual valence, based on bond types
        want_valence = self.atomtype.valence
        ok = (minv <= want_valence <= maxv)
        if not ok:
            return True
        #bruce 080406 new feature: include dna updater errors in this indicator
        # (superseding the orange color-override, which has UI issues)
        if self._dna_updater__error:
            # note: doesn't cover duplex errors or bond geometry errors
            return True
        if self.check_bond_geometry(external = external):
            return True
        return False

    def bad_valence_explanation(self): #bruce 050806; revised 060703 ####@@@@ use more widely
        """
        Return the reason self's valence is bad (as a short text string
        suitable for use as part of a statusbar string), or "" if it's not bad.

        [TODO: Some callers might want an even shorter string; if so, we'll add
         an option to ask for that, and perhaps implement it by stripping off
         " -- " and whatever follows that.]
        """
        # WARNING: keep the code of self.bad_valence() and self.bad_valence_explanation() in sync!
        # note: this is used in statusbar, not tooltip (as of 080406)
        ### TODO: REVIEW and unify: all uses of this, .bad, .bad_valence,
        # dna updater error methods,
        # geometry errors (check_bond_geometry -- nontrivial re external bonds),
        # duplex errors, Atom methods getinfo, getInformationString
        bonds = self.bonds
        if self.element is Singlet:
            ok = (len(bonds) == 1)
            return (not ok) and "internal error: open bond with wrong number of bonds" or ""
        if self.atomtype.numbonds != len(bonds):
            ok = False
            return (not ok) and "wrong number of bonds" or ""
        minv, maxv = self.min_max_actual_valence()
            # min and max reasonable interpretations of actual valence, based on bond types
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
        if self._dna_updater__error:
            #bruce 080406
            # don't return self.dna_updater_error_string(),
            # it might be too long for statusbar
            # (also it's not reviewed for whether it contains
            #  only legal characters for statusbar)
            return "PAM DNA error; see tooltip"
        bges = self.check_bond_geometry()
            # note: external option is not needed here,
            # in spite of being needed in self.bad_valence()
        if bges:
            return bges ### REVIEW: whether it has enough context, or is too long
        return ""

    def min_max_actual_valence(self): #bruce 051215 split this out of .bad and .bad_valence
        """
        Return the pair (minv, maxv) of the min and max reasonable
        values for the sum of all bond orders for all of the bonds to
        self, based on bond types.  Single, double, and triple bonds
        give exact floating point values, while aromatic and graphitic
        allow ranges.  This allows complex resonance structures to be
        deemed ok even without an exact match.

        Note: these are actual float bond orders, NOT v6 values.
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

    def is_ghost(self): #bruce 080529
        """
        """
        if self.ghost:
            return True # only set on Ss3 or Ss5 pseudoatoms
        elif self.element is Singlet and len(self.bonds) == 1:
            return self.bonds[0].other(self).is_ghost()
        elif self.element is Pl5:
            # we're a ghost if all Ss neighbors are ghosts
            for n in self.strand_neighbors():
                if not n.ghost:
                    return False
                continue
            return True
        return False
    
    def overdraw_with_special_color(self, color, level = None, factor = 1.0):
        """
        Draw this atom slightly larger than usual with the given
        special color and optional drawlevel, in abs coords.

        @param factor: if provided, multiply our usual slightly larger radius by factor.
        """
        #bruce 050324; meant for use in Fuse Chunks mode;
        # also could perhaps speed up Extrude's singlet-coloring #e
        if level is None:
            level = self.molecule.assy.drawLevel
        pos = self.posn() # note, unlike for draw_as_selatom, this is in main model coordinates
        drawrad = self.highlighting_radius() # slightly larger than normal drawing radius
        drawrad *= factor #bruce 080214 new feature
        ## drawsphere(color, pos, drawrad, level) # always draw, regardless of display mode
        self.draw_atom_sphere(color, pos, drawrad, level, None,
                              abs_coords = True,
                              special_drawing_prefs = USE_CURRENT
                              )
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
            drawrad = self.radius_for_chunk_highlighting()
            # review: does this need to be bigger when self.bond_geometry_error_string
            # to make tooltip work on self?
        else:
            drawrad = self.highlighting_radius() # slightly larger than normal drawing radius
            if self.bond_geometry_error_string:
                drawrad *= self._BOND_GEOM_ERROR_RADIUS_MULTIPLIER * 1.02
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
            # note: the following inlines self.drawing_radius(picked_Radius = True),
            # but makes further use of intermediate values which that method
            # computes but does not return, so merging them would require a
            # variant method that returned more values. [bruce 080411 comment]
            dispdef = self.molecule.get_dispdef() #e could optimize, since sometimes computed above -- but doesn't matter.
            disp, drawrad = self.howdraw(dispdef)
            if disp == diTUBES:
                pickedrad = drawrad * 1.8 # this code snippet is now shared between several places [bruce 060315/080411]
            else:
                pickedrad = drawrad * 1.1
            pos = self.baseposn()
            self.draw_wirespheres(glpane, disp, pos, pickedrad)
        except:
            print_compact_traceback("exception in draw_wirespheres part of draw_in_abs_coords ignored: ")
            pass
        self.molecule.popMatrix()
        return
    
    def drawing_radius(self, picked_radius = False):
        """
        Return the current drawing radius of the atom. It determines it using 
        the following order -- Returns drawing radius based on atom's current 
        display. If the atom's display is 'default display'it then looks for 
        the chunk's display. If even the chunk's display is default display, 
        it returns the GLPane's current display. Note that these things are 
        done in self.molecule.get_dispdef() and self.howdraw().

        @param picked_radius: instead of the drawing radius, return the larger
                              radius used by the selected-atom wireframe.
                              (Note: not all effects on that radius are
                               implemented yet.)
        @type: bool
        
        @see: DnaSegment_EditCommand._determine_resize_handle_radius() that 
        uses this method to draw the resize handles.
        
        @see: self.howdraw()
        @see: Chunk.get_dispdef()
        """
        # note: this is inlined into draw_in_abs_coords, and possibly elsewhere
        dispdef = self.molecule.get_dispdef()
        disp, drawrad = self.howdraw(dispdef)
        if picked_radius:
            #bruce 080411 added this option
            if disp == diTUBES:
                pickedrad = drawrad * 1.8
            else:
                pickedrad = drawrad * 1.1
            return pickedrad
        return drawrad
    
    def highlighting_radius(self, dispdef = None):
        #bruce 041207; ninad & bruce 080807 renamed it from selatom_radius
        # maybe: integrate with draw_as_selatom
        """
        @return: the radius to use for highlighting this atom (self),
                 in the given display style (by default, in the style
                 it would currently be drawn in). This is larger than
                 self's drawing_radius.

        @see: radius_for_chunk_highlighting
        """
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

    def radius_for_chunk_highlighting(self, dispdef = None):
        #ninad070213 for chunk highlighting
        #bruce 080807 renamed it from selatom_small_radius
        """
        @see: highlighting_radius
        """
        if dispdef is None:
            dispdef = self.molecule.get_dispdef()
        disp, drawrad = self.howdraw(dispdef)
        if self.element is Singlet:
            drawrad *= 1.02
                # increased radius might not be needed, if we would modify the
                # OpenGL depth threshhold criterion used by GL_DEPTH_TEST
                # to overwrite when depths are equal [bruce 041206]
        # review: the following code has no effect; what was its intent?
        # [bruce 080214 comment]
        else:
            if disp == diTUBES:
                drawrad *= 1.0
               
        return drawrad
        
    def setDisplayStyle(self, disp): #bruce 080910 renamed from setDisplay
        """
        set self's display style
        """
        disp = remap_atom_dispdefs.get(disp, disp) #bruce 060607
            # note: error message from rejecting disp, if any,
            # should be done somewhere else, not here
            # (since doing it per atom would be too verbose).
        # Review: could we make the following conditional on
        # self.display != disp? Possible reasons we couldn't:
        # if any callers first set self.disp, then called this method to bless
        # that. I reviewed all the calls and I think this change would be safe,
        # so I am trying it below -- if it causes some chunks to not changeapp,
        # out of those touched by a large selection of atoms, it might be a
        # useful optimization. [bruce 080305 optimization]
        if self.display == disp:
            return
        self.revise_atom_content(
            ATOM_CONTENT_FOR_DISPLAY_STYLE[self.display],
            ATOM_CONTENT_FOR_DISPLAY_STYLE[disp]
         ) #bruce 080307; see also Chunk._ac_recompute_atom_content
        self.display = disp
        _changed_otherwise_Atoms[self.key] = self #bruce 060322
        self.molecule.changeapp(1)
        self.changed() # bruce 041206 bugfix (unreported bug); revised, bruce 050509
        
        # bruce 041109 comment:
        # Atom.setDisplayStyle changes appearance of this atom's bonds,
        # so: do we need to invalidate the bonds? No, they don't store display
        # info, and the geometry related to bond.setup_invalidate has not changed.
        # What about the mols on both ends of the bonds? The changeapp() handles
        # that for internal bonds, and external bonds are redrawn every time so
        # no invals are needed if their appearance changes.
        
        return

    def revise_atom_content(self, old, new): #bruce 080306/080307
        """
        We're changing self's atom content from old to new.
        Invalidate or update self.molecule's knowledge of its atom content
        as needed.
        """
        if not self.molecule:
            return # needed?
        if old & ~new:
            self.molecule.remove_some_atom_content(old & ~new)
        if new & ~old:
            self.molecule.add_some_atom_content(new & ~old)
        return

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
            #bruce 050419 disable this since always happens for Element Color Prefs dialog:
            ## if debug_flags.atom_debug: 
            ##     print "bug warning: dispdef == diDEFAULT in Atom.howdraw for %r" % self
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
        if self.element is Singlet and self.bonds:
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

    def is_hidden(self, glpane = None): #bruce 080521
        """
        Return whether self should be considered hidden
        by other things (like Jigs) whose drawing should depend on that.
        Take into account everything checked by self.visible(), but also
        (unlike it) self.molecule.hidden and (if glpane is passed)
        whether self == glpane.selobj.
        """
        if self.picked:
            return False
        if glpane is not None and self is glpane.selobj:
            return False
        if self.molecule.hidden:
            return True
        return not self.visible()
    
    # == file input/output methods (ideally to be refactored out of this class)
    
    def writemmp(self, mapping, dont_write_bonds_for_these_atoms = ()):
        """
        Write the mmp atom record for self,
        the bond records for whatever bonds have then had both atoms
        written (internal and external bonds are treated identically),
        and any bond_direction records needed for the bonds we wrote.

        Let mapping options influence what is written for any of those
        records.

        @param mapping: an instance of class writemmp_mapping. Can't be None.

        @param dont_write_bonds_for_these_atoms: a dictionary (only keys matter)
                                                 or sequence of atom.keys;
                                                 we will not write any bonds
                                                 whose atoms' keys are both in
                                                 that dictionary or sequence,
                                                 nor any dnaBaseName for those
                                                 atoms, nor (KLUGE) any rung
                                                 bonds for those atoms.
                                                 
        @note: compatible with Node.writemmp, though we're not a subclass of
               Node, except for additional optional args.

        @see: Fake_Pl.writemmp
        """
        # WARNING: has common code with Fake_Pl.writemmp

        # figure out what to do if self is a bondpoint [revised, bruce 080603]
        policy = BONDPOINT_UNCHANGED # simplifies code for non-Singlet cases
        if self.element is Singlet:
            policy = bondpoint_policy(self, mapping.sim)
            if policy == BONDPOINT_LEFT_OUT:
                # note: this is probably correct for this code considered alone
                # (since it probably needs to not call encode_next_atom, and doesn't),
                # but some necessary consequences of leaving this atom out
                # are probably NIM. For more info see other comments in,
                # and/or around other calls of, bondpoint_policy.
                #
                # review: want summary message about number of bondpoints left out?
                # guess: no, at least not once it happens by default.
                return
            elif policy == BONDPOINT_UNCHANGED:
                pass # handled correctly by the code for general elements, below
            elif policy == BONDPOINT_REPLACED_WITH_HYDROGEN:
                pass # this is tested again below and handled separately
            else:
                # e.g. BONDPOINT_ANCHORED (can't yet happen)
                assert 0, "not yet implemented: bondpoint_policy of %r" % (policy,)
            pass
        
        num_str = mapping.encode_next_atom(self) # (note: pre-050322 code used an int here)
        disp = mapping.dispname(self.display) # note: affected by mapping.sim flag
        posn = self.posn() # might be revised below
        eltnum = self.element.eltnum # might be revised below
        
        if policy == BONDPOINT_REPLACED_WITH_HYDROGEN: # condition revised, bruce 080603
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
                pass
            pass

        #bruce 080521 refactored the code for printing atom coordinates
        # (and fixed a rounding bug, described in encode_atom_coordinates)
        xs, ys, zs = mapping.encode_atom_coordinates( posn )
        print_fields = (num_str, eltnum, xs, ys, zs, disp)
        mapping.write("atom %s (%d) (%s, %s, %s) %s\n" % print_fields)
        
        if self.key not in dont_write_bonds_for_these_atoms:
            # write dnaBaseName info record [mark 2007-08-16]
            # but not for atoms whose bonds will be written compactly,
            # since the dnaBaseName is too, for them [bruce 080328]
            dnaBaseName = self.getDnaBaseName()
            if dnaBaseName and dnaBaseName != 'X':
                #bruce 080319 optimization -- never write this when it's 'X',
                # since it's assumed to be 'X' when not present (for valid atoms).
                mapping.write( "info atom dnaBaseName = %s\n" % dnaBaseName )

        if self.ghost:
            mapping.write( "info atom ghost = True\n" ) #bruce 080529
        
        # Write dnaStrandName info record (only for Pe atoms). Mark 2007-09-04
        # Note: maybe we should disable this *except* for Pe atoms
        # (hoping Mark's comment was right), so it stops happening for files
        # written with the dna updater active, as a step towards deprecating it.
        # Review soon. [bruce 080311 comment]
        #See self.getDnaStrandId_for_generators() for comments about this
        #attr. Basically, its used only while creating a new duplex from scratch
        #(while reading in the reference base mmp files in the plugins dir) 
        dnaStrandId_for_generators = self.getDnaStrandId_for_generators()
        if dnaStrandId_for_generators:
            mapping.write( "info atom dnaStrandId_for_generators = %s\n" %
                           dnaStrandId_for_generators )
        
        #bruce 050511: also write atomtype if it's not the default
        atype = self.atomtype_iff_set()
        if atype is not None and atype is not self.element.atomtypes[0]:
            mapping.write( "info atom atomtype = %s\n" % atype.name )

        # also write PAM3+5 data when present [bruce 080523]
        if self._PAM3plus5_Pl_Gv_data is not None:
            self._writemmp_PAM3plus5_Pl_Gv_data( mapping)
                # this writes "info atom +5data = ..."
        
        # write only the bonds which have now had both atoms written
        # (including internal and external bonds, not treated differently)
        #bruce 050502: write higher-valence bonds using their new mmp records,
        # one line per type of bond (only written if we need to write any bonds
        # of that type)
        bldict = {}
            # maps valence to list of 0 or more atom-encodings for
            # bonds of that valence we need to write
        ## bl = [] # (note: in pre-050322 code bl held ints, not strings)
        bonds_with_direction = []
        for b in self.bonds:
            oa = b.other(self)
            if self.key in dont_write_bonds_for_these_atoms and (
               oa.key in dont_write_bonds_for_these_atoms or
               b.is_rung_bond()):
                # Note: checking oa.key is fine, but b.is_rung_bond is a KLUGE:
                # we know all current subclasses that pass nonempty
                # dont_write_bonds_for_these_atoms also take care of writing
                # rung bonds themselves. This is not presently a bug, but needs
                # to be cleaned up, for clarity and before any other chunk
                # subclasses besides DnaLadderRailChunk make use of this feature.
                # [bruce 080328]
                continue
            #bruce 050322 revised this:
            oa_code = mapping.encode_atom(oa)
                # None, or true and prints as "atom number string"
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
            #bruce 070415
            mapping.write( bond.mmprecord_bond_direction(self, mapping) + "\n") 
        
        return # from writemmp

    def readmmp_info_atom_setitem( self, key, val, interp ):
        """
        Reads an atom info record from the MMP file.
        
        @see: The docstring of an analogous method, such as
              L{Node.readmmp_info_leaf_setitem()}.
        """
        if key == ['atomtype']: #bruce 050511
            # val should be the name of one of self.element's atomtypes
            # (not an error if unrecognized)
            try:
                atype = self.element.find_atomtype(val)
            except:
                # didn't find it.
                # (todo: find_atomtype ought to have a different API, so a
                #  real error could be distinguished from not finding val.)
                if debug_flags.atom_debug:
                    print "atom_debug: fyi: " \
                          "info atom atomtype (in class Atom) with " \
                          "unrecognized atomtype %r (not an error)" % (val,)
                pass
            else:
                self.set_atomtype_but_dont_revise_singlets( atype)
                    # don't add bondpoints (aka singlets), since this
                    # mmp record comes before the bonds, including bonds
                    # to bondpoints
        
        elif key == ['dnaBaseName']: # Mark 2007-08-16
            try:
                self.setDnaBaseName(val)
            except Exception, e:
                #bruce 080304 revised printed error, added history summary
                print "Error in mmp record, info atom dnaBaseName: %s" \
                      " (continuing)" % (e,)
                msg = "Error: illegal DNA base name on [N] atom(s) " \
                      "(see console prints for details)"
                summary_format = redmsg( msg )
                env.history.deferred_summary_message(summary_format)
                pass
        
        elif key == ['ghost']: #bruce 080529
            if val == "True":
                self.ghost = True
        
        elif key == ['dnaStrandId_for_generators']: # Mark 2007-09-04
            try:
                #@see: self.getDnaStrandId_for_generators() for comments
                #about this attr
                self.setDnaStrandId_for_generators(val)
            except Exception, e:
                #bruce 080304 revised printed error, added history summary
                print "Error in mmp record, info atom dnaStrandId_for_generators: %s" \
                      " (continuing)" % (e,)
                msg = "Error: illegal DNA strand id (used by dna generator) on [N] atom(s) " \
                      "(see console prints for details)"
                summary_format = redmsg( msg )
                env.history.deferred_summary_message(summary_format)
                pass

        elif key == ['+5data']: #bruce 080523
            try:
                self._readmmp_3plus5_data(key, val, interp)
            except:
                msg = "error in reading info atom +5data = %s\n" % (val,) + \
                      "for %r (ignored)" % self
                if debug_flags.atom_debug:
                    print_compact_traceback( msg + ": ")
                else:
                    print msg
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
        # piotr 080711 : Changed atom name alignment to start from column 14.
        # This should make our files more compatible with software that
        # is very strict about PDB format compliance.
        atomRecord += " %-3s" % self.element.symbol
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
        # piotr 080711: Use "1" as a residue number, as certain programs
        # may have difficulties readin the file if this field is empty.
        atomRecord += "%4d" % int(1)
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
        # piotr 080711: Output the element symbol here, as well (but
        # truncate it to two characters).
        atomRecord += "%2s" % self.element.symbol[:2].upper()
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
        xyz = map(float, A(self.posn()))
        rgb = map(int,A(color)*255)
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
    
    def getInformationString(self, mention_ghost = True):
        """
        If a standard atom, return a string like C26(sp2) with atom name and
        atom hybridization type, but only include the type if more than one is 
        possible for the atom's element and the atom's type is not the default 
        type for that element.
        
        If a PAM Ss (strand sugar) atom, returns a string like Ss28(A) with atom name
        and dna base letter.
        """
        res = str(self)
        if self.atomtype is not self.element.atomtypes[0]:
            res += "(%s)" % self.atomtype.name
        if self.getDnaBaseName():
            res += "(%s)" % self.getDnaBaseName()
        if mention_ghost and self.is_ghost():
            res += " (placeholder base)"
        return res

    def getToolTipInfo(self,
                       isAtomPosition, 
                       isAtomChunkInfo,
                       isAtomMass, 
                       atomDistPrecision):
        """
        Returns this atom's basic info string for the dynamic tooltip
        """
        atom = self

        atomStr        = atom.getInformationString( mention_ghost = False)
        elementNameStr = " [" + atom.element.name + "]"

        atomInfoStr = atomStr + elementNameStr

        if atom.display:
            # show display style of atoms that have one [bruce 080206]
            atomInfoStr += "<br>" + "display style: %s" % atom.atom_dispLabel() 

        if atom.is_ghost():
            atomInfoStr += "<br>" + "(placeholder base)"
        
        # report dna updater errors in atom or its DnaLadder
        msg = atom.dna_updater_error_string(newline = '<br>')
        if msg:
            atomInfoStr += "<br>" + orangemsg(msg)

        if debug_pref("DNA: show wholechain baseindices in atom tooltips?",
                      Choice_boolean_False,
                      prefs_key = True ): #bruce 080421 (not in rc2)
            try:
                wholechain = atom.molecule.wholechain
                    # only works for some atoms; might be None
            except AttributeError:
                wholechain = None
            if wholechain: # also check whether it's valid??
                try:
                    baseatom = atom
                    if baseatom.element is Singlet:
                        baseatom = baseatom.singlet_neighbor() #bruce 080603 bugfix
                    if baseatom.element is Pl5:
                        baseatom = baseatom.Pl_preferred_Ss_neighbor() #bruce 080603 bugfix
                    rail = atom.molecule.get_ladder_rail()
                    whichrailjunk, baseindex = atom.molecule.ladder.whichrail_and_index_of_baseatom(baseatom)
                    bi_min, bi_max = wholechain.wholechain_baseindex_range()
                    bi_rail0, bi_rail1 = wholechain.wholechain_baseindex_range_for_rail(rail)
                    bi_baseatom = wholechain.wholechain_baseindex(rail, baseindex)
                    msg = "wholechain baseindices: (%d, %d), (%d, %d), %d" % \
                          (bi_min, bi_max, bi_rail0, bi_rail1, bi_baseatom)
                    atomInfoStr += "<br>" + greenmsg(msg)
                except:
                    print_compact_traceback("exception in show wholechain baseindices: ")
                    pass
                pass
            pass
        
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
    
    def checkpick(self, p1, v1, disp, r = None, iPic = None):
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
        make this atom selected
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
        Make this atom (self) unselected, if the selection filter
        permits this or if filtered = False.
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
                #bruce 050309 catch exceptions, and do this before picked = 0
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
    
    def copy(self): #bruce 041116, revised bruce 080319 to not copy default-valued attrs
        """
        Public method: copy the atom self, with no special assumptions,
        and return the copy (a new atom);
        new atom is not initially in any chunk,
        but could be added to one using Chunk.addatom.
        """
        nuat = Atom(self, self.posn(), None)
            #bruce 050524: pass self so its atomtype is copied
        
        # optimization: assume the class defaults for the following copied
        # attrs are all boolean false [verified by test], and the legal
        # nondefault values are all boolean true (believed) -- this optimizes
        # the following tests for whether they need to be set in nuat
        # [bruce 080319]
        
        if self.display:
            nuat.display = self.display
        if self.info:
            nuat.info = self.info #bruce 041109; revised 050524;
                # needed by extrude and other future things
        if self._dnaBaseName:
            nuat._dnaBaseName = self._dnaBaseName #bruce 080319
        if self.ghost:
            # (note: can be set on PAM strand baseatoms,
            #  but not on Pl atoms or bondpoints)
            nuat.ghost = self.ghost #bruce 080529
        # Note: the following attributes are used only by methods in our
        # mixin superclass, PAM_Atom_methods, except for a few foundational
        # methods in this class. If we introduce per-element subclasses of
        # this class, these would only need to be copied in the subclass
        # corresponding to PAM_Atom_methods. [bruce 080523]
        if not self._f_Pl_posn_is_definitive:
            print "bug? copying %r in which ._f_Pl_posn_is_definitive is not set" % self
        if self._PAM3plus5_Pl_Gv_data is not None:
            nuat._PAM3plus5_Pl_Gv_data = copy_val(self._PAM3plus5_Pl_Gv_data)

        if (self.overlayText):
            nuat.overlayText = self.overlayText

        # no need in new atoms for anything like
        # _changed_otherwise_Atoms[nuat.key] = nuat
        # [bruce 060322 guess ###@@@ #k]
        
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
        usually replace it with a singlet (which is returned).

        Details:

        Remove bond b from self (error if b not in self.bonds).

        Note that bonds are compared with __eq__, not 'is', by 'in' and 'remove'.
        Only call this when b will be destroyed, or "recycled" (by bond.rebond);
        thus no need to invalidate the bond b itself -- caller must do whatever
        inval of bond b is needed (which is nothing, if it will be destroyed).

        Then replace bond b in self.bonds with a new bond to a new singlet,
        unless self or the old neighbor atom is a singlet, or unless make_bondpoint
        is false.

        Return the new singlet, or None if one was not created.

        Do all necessary invalidations, including self._changed_structure(),
        EXCEPT:
        - of Chunk._f_lost_externs flags (since some callers don't need this
          even when self is an external bond);
        - of b.

        If self is a singlet, kill it (singlets must always have one bond).
        
        @note: As of 041109 (still true 080701), this is called only from
               Atom.kill of the other atom, and from bond.bust, and from
               bond.rebond.

        @note: As of 050727, newly created open bonds have same bond type as the
               removed bond.
        """
        self._changed_structure()
        
        b.invalidate_bonded_mols() #e would be more efficient if callers did this
        
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
                # don't kill it, in this case [bruce 041115; I don't know if this ever happens]
                from dna.updater.dna_updater_globals import get_dnaladder_inval_policy, DNALADDER_INVAL_IS_NOOP_BUT_OK
                    # can't be a toplevel import for now
                if get_dnaladder_inval_policy() == DNALADDER_INVAL_IS_NOOP_BUT_OK:
                    pass # this now happens routinely during PAM conversion [bruce 080413]
                else:
                    # I don't recall ever seeing this otherwise, but it's good
                    # to keep checking for it [bruce 080413]
                    print "fyi: bug: unbond on a singlet %r finds unexpected bonds left over in it, %r" % (self, self.bonds)
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
        if at2.element.role == 'handle': #bruce 080516 kluge
            # (Ultimately we'd want bond.bust to decide this based on both
            #  atomtypes or on asking each atom about the other's type.
            #  For now, only this case matters (for element Ah5).
            if self.molecule is not None:
                # update valence error indicator appearance on self
                self.molecule.changeapp(0)
            return None
        if 1:
            #bruce 060327 optim of Chunk.kill: if we're being killed right now, don't make a new bondpoint
            if self._will_kill == Utility._will_kill_count:
                if DEBUG_1779:
                    print "DEBUG_1779: self._will_kill %r == Utility._will_kill_count %r" % \
                      ( self._will_kill , Utility._will_kill_count )
                return None
        if self.__killed:
            #bruce 080208 new debug print (should never happen)
            msg = "bug: killed atom %r still had bond %r, being unbonded now" % \
                  ( self, b )
            print msg
            return None
        if DEBUG_1779:
            print "DEBUG_1779: Atom.unbond on %r is making X" % self
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
        if self.molecule.assy is not numol.assy: #bruce 080219 debug code, might be slow, might print routinely ##
            msg = "\nBUG?: hopmol(%r, %r) but self.molecule %r .assy %r != numol.assy %r" % \
                  (self, numol, self.molecule, self.molecule.assy, numol.assy)
            print_compact_stack(msg + ": ") #bruce 080411

        # We only have to set this in the chunk, not clear it, as it
        # is cleared by the display routine when needed.
        if (self.overlayText):
            numol.chunkHasOverlayText = True

        self.molecule.delatom(self) # this also invalidates our bonds
        numol.addatom(self)
        for atom in self.singNeighbors():
            assert self.element is not Singlet # (only if we have singNeighbors!)
                # (since hopmol would infrecur if two singlets were bonded)
            atom.hopmol(numol)
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
        return filter(lambda atom: atom.element is not Singlet, self.neighbors())
    
    def singNeighbors(self): #e when we have only one branch again, rename this singletNeighbors or bondpointNeighbors
        """
        return a list of the singlets bonded to this atom
        """
        return filter(lambda atom: atom.element is Singlet, self.neighbors())
    
    def baggage_and_other_neighbors(self): #bruce 051209
        """
        Return a list of the baggage bonded to this atom (monovalent neighbors which should be dragged along with it),
        and a list of the others (independent neighbors). Special case: in H2 (for example) there is no baggage
        (so that there is some way to stretch the H-H bond); but singlets are always baggage, even in HX.
        """
        nn = self.neighbors()
        if len(nn) == 1:
            # special case: no baggage unless neighbor is a Singlet
            if nn[0].element is Singlet:
                return nn, []
            else:
                return [], nn
        baggage = []
        other = []
        for atom in nn:
            if len(atom.bonds) == 1:
                baggage.append(atom)
            else:
                other.append(atom)
        return baggage, other

    def baggageNeighbors(self): #bruce 051209
        baggage, other_unused = self.baggage_and_other_neighbors()
        return baggage

    def bondpoint_most_perpendicular_to_line(self, vector): #bruce 080529
        """
        Return one of our bondpoints whose spatial direction from self
        is farthest from the line through self defined by vector,
        or None if self has no bondpoints.
        """
        candidates = []
        for bond in self.bonds:
            other = bond.other(self)
            if not other.element is Singlet:
                continue
            other_vector = norm( other.posn() - self.posn() )
            closeness_to_line = abs( dot( other_vector, vector) )
                # scale depends on vlen(vector), but that doesn't matter here
            candidates.append( (closeness_to_line, other) )
        if candidates:
            candidates.sort() # closest one is last, farthest is first
            return candidates[0][1]
        return None
    
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
        chunk = self.molecule
        if chunk is None:
            return #k needed??
        chunk.changed()
        return

    def killed(self): #bruce 041029; totally revised 050702; revised 080227
        """
        (Public method)
        Report whether an atom has been killed.
        """
        # Note: some "friend code" inlines an old incomplete version of
        # this method for speed (and omits the debug code). To find it,
        # search for _Atom__killed (the mangled version of __killed).
        # [bruce 071018/080227 comment]
        #
        # Note: (theory about an Undo bug in dna updater, bruce 080227):
        # Undo can be too lazy to set __killed, but then it clears .molecule.
        # And, break_interpart_bonds can then dislike .molecule being None
        # and set it back to _nullMol. So test for these values too. 
        chunk = self.molecule
        res = self.__killed or chunk is None or chunk.isNullChunk()
        if debug_flags.atom_debug: # this cond is for speed
            better_alive_answer = chunk is not None and self.key in chunk.atoms and not chunk.isNullChunk()
                ##e and chunk is not killed??
            if (not not better_alive_answer) != (not self.__killed):
                #bruce 060414 re bug 1779, but it never printed for it (worth keeping in for other bugs)
                #bruce 071018 fixed typo of () after debug_flags.atom_debug -- could that be why it never printed it?!?
                print "debug: better_alive_answer is %r but (not self.__killed) is %r" % (better_alive_answer , not self.__killed)
        return res
    
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
                chunk = self.molecule
                assert chunk is None or chunk.isNullChunk()
                # thus don't do this: assert not self.key in chunk.assy.selatoms
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
        [public method]
        kill self: unpick it, remove it from its jigs, remove its bonds,
        then remove it from its chunk. Do all necessary invalidations.
        
        (Note that molecules left with no atoms, by this or any other op,
         will immediately kill themselves.)
        """        
        if DEBUG_1779:
            print "DEBUG_1779: Atom.kill on %r" % self
        if self.__killed:
            if not self.element is Singlet:
                print_compact_stack("fyi: atom %r killed twice; ignoring:\n" % self)
            else:
                # Note: killing a selected chunk, using Delete key, kills a lot of
                # singlets twice; I guess it's because we kill every atom
                # and singlet in chunk, but also kill singlets of killed atoms.
                # So I'll declare this legal, for singlets only. [bruce 041115]
                pass
            return

        self.atomtype
            #bruce 080208 bugfix of bugs which complain about
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
        # unpick self
        try:
            self.unpick(filtered = False)
                #bruce 060331 adding filtered = False (and implementing it in unpick) to fix bug 1796
        except:
            print_compact_traceback("fyi: Atom.kill: ignoring error in unpick: ")
            pass
        # bruce 041115 reordered everything that follows, so it's safe to use
        # delatom (now at the end, after things which depend on self.molecule),
        # since delatom resets self.molecule to None.
        
        # remove from jigs
        for j in self.jigs[:]:
            try:
                j.remove_atom(self)
                    # note: this might kill the jig (if it has no atoms left),
                    # and/or it might remove j from self.jigs, but it will never
                    # recursively kill this atom, so it should be ok
                    # [bruce 050215 comment]
            except:
                # does this ever still happen? TODO: if so, document when & why.
                print_compact_traceback("fyi: Atom.kill: ignoring error in remove_atom %r from jig %r: " % (self, j) )
        self.jigs = [] # mitigate repeated kills
        _changed_structure_Atoms[self.key] = self #k not sure if needed; if it is, also covers .bonds below #bruce 060322
        
        # remove bonds
        selfmol = self.molecule
        for b in self.bonds[:]:
            other = b.other(self)
            if DEBUG_1779:
                print "DEBUG_1779: Atom.kill on %r is calling unbond on %r" % (self, b)
            if other.molecule is not selfmol: #bruce 080701
                other.molecule._f_lost_externs = True
                selfmol._f_lost_externs = True
            other.unbond(b)
                # note: this can create a new singlet on other, if other is a real atom,
                # which requires computing b.ubp, which uses self.posn()
                # or self.baseposn(); or it can kill other if it's a singlet.
                # In some cases this is optimized to avoid creating singlets
                # when killing lots of atoms at once; search for "prekill".
                # It also invalidates chunk externs lists if necessary
                # (but not their _f_lost_externs flags).
        self.bonds = [] # mitigate repeated kills

        # only after disconnected from everything else, remove self from its chunk
        try:
            selfmol.delatom(self)
                # delatom also kills our chunk (self.molecule) if it becomes empty
        except KeyError:
            print "fyi: Atom.kill: atom %r not in its molecule (killed twice?)" % self
            pass
        return # from Atom.kill
        
    def filtered(self): # mark 060303
        """
        Returns True if self is not the element type/name currently listed in
        the Select Atoms filter combobox.
        """
        if self.is_singlet():
            return False # Fixes bug 1608 [mark 060303]
        
        if self.molecule.assy.w.selection_filter_enabled:
            for e in self.molecule.assy.w.filtered_elements:
                if e is self.element:
                    return False
            return True
            
        return False

    def Hydrogenate(self):
        """
        [Public method; does all needed invalidations:]
        If this atom is a singlet, change it to a hydrogen,
        and move it so its distance from its neighbor is correct
        (regardless of prior distance, but preserving prior direction).
        [#e sometimes it might be better to fix the direction too, like in depositMode...]

        @return: If hydrogenate succeeds, the int 1, otherwise, 0.
        @rtype: int
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
        """
        Given one of our neighbor atoms (real or singlet)
        [neighborness not verified! only posn is used, not the bond --
         this might change when we have bond-types #e]
        and assuming it should remain fixed and our bond to it should
        remain in the same direction, and pretending (with no side effects)
        that our element is pretend_I_am if this is given,
        what position should we ideally have
        so that our bond to neighbor has the correct length?

        @see: methods Bond.ubp, Atom.snuggle, move_closest_baggage_to

        @warning: does not use getEquilibriumDistanceForBond/bond_params
        """
        # review: should this use bond_params (which calls
        # getEquilibriumDistanceForBond when available)?
        # [bruce 080404 comment]
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
        """
        [Public method; does all needed invalidations:]
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
            # different chunk (since it needs to be in our neighbor atom's chunk)
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

    def snuggle(self):
        """
        self is a bondpoint and the simulator has moved it out to the radius of
        an H (or moved it to a nonsensical position, and/or not moved it at all,
        if it's next to a PAM atom). Move it to a reasonable position.

        self.molecule may or may not be still in frozen mode. If self's neighbor
        is a PAM atom, the dna updater may or may not have ever run on it,
        and/or have run since it was last modified.

        Do all needed invals.

        @warning: if you are moving several atoms at once, first move them all,
        then snuggle them all, since snuggling self is only correct after
        self's real neighbor has already been moved to its final position.
        [Ignorance of this issue was the cause of bug 1239.]

        @see: methods Bond.ubp, Atom.ideal_posn_re_neighbor,
              move_closest_baggage_to
        """
        #bruce 051221 revised docstring re bug 1239
        #bruce 080501 revised behavior for PAM atoms
        if not self.bonds:
            #bruce 050428: a bug, but probably just means we're a killed singlet.
            # The caller should be fixed, and maybe is_singlet should check this
            # too, but for now let's also make it harmless here:
            if debug_flags.atom_debug:
                print_compact_stack( "atom_debug: bug (ignored): snuggling a killed singlet of atomkey %r: " %
                                     self.key ) #bruce 051221 revised this; untested
            return
        #bruce 050406 revised docstring to say chunk needn't be frozen.
        # note that this could be rewritten to call ideal_posn_re_neighbor,
        # but we'll still use it since it's better tested and faster.
        other = self.bonds[0].other(self)
        op = other.posn()
        sp = self.posn()
        np = op + norm(sp - op) * other.atomtype.rcovalent
        self.setposn(np) # bruce 041112 rewrote last line
        if other.element.pam: #bruce 080501 bugfix/nfr for v1.0.1
            # print "fyi: fixing posn of %r on %r" % (self, other) # seems to work
            other.reposition_baggage_using_DnaLadder( dont_use_ladder = True,
                                                      only_bondpoints = True )
            pass
        return

    def move_closest_baggage_to(self,
                                newpos,
                                baggage = None,
                                remove = False,
                                min_bond_length = 0.1 ):
        """
        Find the atom in baggage (self.baggageNeighbors() by default)
        which is closest *in direction from self* to newpos,
        and then move it to newpos, correcting its distance from self
        based on its and self's atomtypes (using newpos only for direction)
        unless an option (nim) is set to false.

        Return the atom moved, or None if no atom could be found to move.

        If remove is true, baggage must have been passed, and we also remove
        the moved atom (if any) from baggage (modifying it destructively).

        @param newpos: desired position to move an atom to; used only for its
                       direction from self (by default)

        @param baggage: a sequence (mutable if remove is false), or None

        @param remove: whether to remove the moved atom from baggage (which
                       must be a mutable sequence if we do)

        @param min_bond_length: minimum allowed distance from self to moved atom
        
        @return: the atom we moved, or None if we found no atom to move.
        """
        #bruce 080404
        if baggage is None:
            assert not remove
            baggage = self.baggageNeighbors() # or singNeighbors??
        if not baggage:
            return None # can't move anything
        # todo: assert baggage is a list (which we can remove from if remove is true)

        # figure out which atom in baggage to move
        selfpos = self.posn()
        newpos_direction = norm(newpos - selfpos)
        sortme = [] # rename?
        for atom in baggage:
            atom_direction = norm(atom.posn() - selfpos)
            dist = vlen(atom_direction - newpos_direction)
            sortme.append( (dist, atom) )
        sortme.sort()
        moveme = sortme[0][1]
        
        # maybe: don't move if already at newpos? only matters if that case
        # often happens (on atoms which didn't already inval their chunks
        # due to whatever caused this to be called), which I doubt (at least
        # for its initial use in reposition_baggage_using_DnaLadder).
        # note: that optim could probably be done by testing sortme[0][0]
        # for being close to zero. But worry about corrections for distance
        # on both newpos vs newpos_direction, and below.

        # fix distance
        want_length = ideal_bond_length(self, moveme)
            # note: depends on moveme.atomtype (and therefore, possibly,
            # on which element of baggage is chosen to be moveme)
        if want_length < min_bond_length:
            if debug_flags.atom_debug:
                print "fyi, in move_closest_baggage_to: " \
                      "ideal_bond_length(%r, %r) == %r < min_bond_length == %r" % \
                      (self, moveme, want_length, min_bond_length)
            want_length = min_bond_length
            pass
        fixed_newpos = selfpos + newpos_direction * want_length
        
        moveme.setposn(fixed_newpos)
        
        if remove:
            baggage.remove(moveme)
        
        return moveme

    def Passivate(self): ###@@@ not yet modified for atomtypes since it's not obvious what it should do! [bruce 050511]
        """
        [Public method, does all needed invalidations:]
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
        for atom in self.singNeighbors():
            atom.kill()
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
    
    def singlet_neighbor(self):
        """
        Assume self is a bondpoint (aka singlet).
        Such an atom should be bonded to exactly one neighbor, a real atom
        (i.e. non-bondpoint).
        Return that neighbor atom, after checking some assertions.
        """
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
        from model.bond_constants import V_ZERO_VALENCE, BOND_VALENCES
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
        """
        [Public method]

        Compute and return the best choice of atomtype for this atom's element
        (or for the passed element <elt>, if any)
        and number of bonds (including open bonds),
        breaking ties by favoring <atype_now> (if provided),
        otherwise favoring atomtypes which come earlier
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
        """
        Say whether this atom's element has any atomtype which would
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

    def _changed_structure(self):
        # WARNING: this has some external calls. See docstring. [bruce 080404 comment]
        #bruce 050627; docstring revised and some required calls added, 050725; revised 051011
        """
        [friend method, mostly used privately. Should be renamed with _f_ prefix.
         OR, maybe it's really a public method and should be renamed with no _
         like the method on Jig.]

        This must be called by all low-level methods which change this atom's or bondpoint's element, atomtype,
        or set of bonds. It doesn't need to be called for changes to neighbor atoms, or for position changes,
        or for changes to chunk membership of this atom, or when this atom is killed (but it will be called indirectly
        when this atom is killed, when the bonds are broken, unless this atom has no bonds). Calling it when not needed
        is ok, but might slow down later update functions by making them inspect this atom for important changes.
        (For example, calling it on a PAM atom invalidates that atom's entire DnaLadder.)

        All user events which can call this (indirectly) should also call env.do_post_event_updates() when they're done.
        """
        ####@@@@ I suspect it is better to also call this for all killed atoms or bondpoints, but didn't do this yet. [bruce 050725]
        ## before 051011 this used id(self) for key
        #e could probably optim by importing this dict at toplevel, or perhaps even assigning a lambda in place of this method
        global_model_changedicts.changed_structure_atoms[ self.key ] = self
        _changed_structure_Atoms[ self.key ] = self #bruce 060322
            # (see comment at _changed_structure_Atoms about how these two dicts are related)
        self._f_valid_neighbor_geom = False
        self._f_checks_neighbor_geom = (self.element.role == 'axis')
        return

    def _f_changed_some_bond_direction(self): #bruce 080210
        """
        [friend method]
        One of our bonds changed its bond direction.
        Do necessarily invals on self (other than Undo
        or changeapp, handled by our caller in the bond).
        """
        _changed_structure_Atoms[ self.key ] = self
        return
    
    # debugging methods (not yet fully tested; use at your own risk)
    
    def invalidate_everything(self): # for an atom, remove it and then readd it to its chunk
        """
        debugging method
        """
        if len(self.molecule.atoms) <= 1:
            print "warning: invalidate_everything on the lone atom %r in chunk %r does nothing" % (self, self.molecule)
            print " since otherwise it might kill that chunk as a side effect!"
        else:
            #bruce 080318 bugfix: don't do this if only one atom; revise print above to say so
            # note: delatom invals self.bonds
            self.molecule.delatom(self) # note: this kills the chunk if it becomes empty!
            self.molecule.addatom(self)
        return

    def update_everything(self):
        """
        debugging method
        """
        # too verbose, don't do this [bruce 080318]:
        ## print "Atom.update_everything() does nothing"
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
        """
        [Public method, does all needed invalidations:]
        With no checks except that the operation is legal,
        kill all bondpoints, change elt and atomtype
        (both must be provided and must match), and make new bondpoints.
        """
        for atom in self.singNeighbors():
            atom.kill() # (since atom is a bondpoint, this kill doesn't replace it with a bondpoint)
        self.mvElement(elt, atomtype)
        self.make_enough_bondpoints()
        return # from direct_Transmute

    def reposition_baggage(self, baggage = None, planned_atom_nupos = None):
        """
        Your baggage atoms (or the given subset of them) might no longer
        be sensibly located, since you and/or some neighbor atoms have moved
        (or are about to move, re planned_atom_nupos as explained below),
        so fix up their positions based on your other neighbors' positions,
        using old baggage positions only as hints.

        BUT one of your other neighbors (but not self) might be about to move
        (rather than already having moved) -- if so,

          planned_atom_nupos = (that neighbor, its planned posn),
        
        and use that posn instead of its actual posn to decide what to do.

        @warning: we assume baggage is a subset of self.baggageNeighbors(),
                  but we don't check this except when ATOM_DEBUG is set.
        """
        #bruce 060629 for bondpoint problem
        try:
            import operations.reposition_baggage as reposition_baggage # don't make this a toplevel import
            reload_once_per_event(reposition_baggage) # this can be removed when devel is done, but doesn't need to be
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
        for atom in self.singNeighbors():
            atom.kill() # (since atom is a bondpoint, this kill doesn't replace it with a bondpoint)
        self.make_enough_bondpoints()
        return
    
    def remake_baggage_UNFINISHED(self):
        #bruce 051209 -- pseudocode; has sample calls, desirable but commented out, since it's unfinished ###@@@
        bn = self.baggageNeighbors()
        for atom in bn:
            if not atom.is_singlet():
                pass ###e record element and position
                atom.mvElement(Singlet) ####k ??? #####@@@@@ kluge to kill it w/o replacing w/ singlet; better to just tell kill that
            atom.kill() # (since atom is a singlet, this kill doesn't replace it with a singlet)
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
            chunk = self.molecule
            for dp in atype.bondvectors:
                x = Atom('X', pos + r * dp, chunk)
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
                if not (a1.atomtype.is_linear() and atype.potential_pi_bond()):
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
                if (atype.potential_pi_bond() and
                    a1.atomtype.potential_pi_bond()): # for now, same behavior for sp2 or sp atoms [revised 050630]
                    pass # no extra spin
                else:
                    spin = spin + Q(r, math.pi/3.0) # 60 degrees of extra spin
            else: spin = Q(1,0,0,0)
            chunk = self.molecule
            if 1: # see comment below [bruce 050614]
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
                x = Atom('X', xpos, chunk)
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
        chunk = self.molecule
        for q in atype.quats[1:]:
            q = rq + q - rq + tw
            x = Atom('X', pos + q.rot(r), chunk)
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
            chunk = self.molecule
            x = Atom('X', opos, chunk)
            bond_atoms(self, x)
        return

    pass # end of class Atom

# ==

register_instancelike_class( Atom) # ericm & bruce 080225

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
##register_instancelike_class( Atom2)

# ==

def oneUnbonded(elem, assy, pos, atomtype = None, Chunk_class = None):
    """
    Create one unbonded atom, of element elem
    and (if supplied) the given atomtype
    (otherwise the default atomtype for elem),
    at position pos, in its own new chunk,
    with enough bondpoints to have no valence error.

    @param Chunk_class: constructor for the returned atom's new chunk
                        (assy.Chunk by default)

    @return: one newly created Atom object, already placed into a new
             chunk which has been added to the model using addnode
    """
    #bruce 080520 added Chunk_class option
    #bruce 050510 added atomtype option
    # bruce 041215 moved this from chunk.py to chem.py, and split part of it
    # into the new atom method make_bondpoints_when_no_bonds, to help fix bug 131.
    if Chunk_class is None:
        Chunk_class = assy.Chunk
    chunk = Chunk_class(assy, 'bug') # name is reset below!
    atom = Atom(elem.symbol, pos, chunk)
    # bruce 041124 revised name of new chunk, was gensym('Chunk.');
    # no need for gensym since atom key makes the name unique, e.g. C1.
    atom.set_atomtype_but_dont_revise_singlets(atomtype) # ok to pass None, type name, or type object; this verifies no change in elem
        # note, atomtype might well already be the value we're setting; if it is, this should do nothing
    ## chunk.name = "Chunk-%s" % str(atom)
    chunk.name = gensym("Chunk", assy) #bruce 080407 per Mark NFR desire
    atom.make_bondpoints_when_no_bonds() # notices atomtype
    assy.addnode(chunk)
    return atom

# ==

def move_alist_and_snuggle(alist, newPositions):
    """
    Move the atoms in alist to the new positions in the given array or sequence
    (which must have the same length);
    then for any singlets in alist, correct their positions using Atom.snuggle.

    @warning: it would be wrong to call this on several alists in a row if they might overlap
    or were connected by bonded atoms, for the same reason that the snuggle has to be done in a separate loop
    (see snuggle docstring for details, re bug 1239).

    @warning: I'm not sure if it does all required invals; it doesn't do gl_update.
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
