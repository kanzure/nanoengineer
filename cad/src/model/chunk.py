# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
chunk.py -- provides class Chunk [formerly known as class molecule],
for a bunch of atoms (not necessarily bonded together) which can be moved
and selected as a unit.

@author: Josh, Bruce, others
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

originally by Josh

lots of changes, by various developers

split out of chem.py by bruce circa 041118

bruce 050513 optimized some things, including using 'is' and 'is not' rather than
'==', '!=' for atoms, molecules, elements, parts, assys in many places (not
all commented individually)

bruce 060308 rewriting Atom and Chunk so that atom positions are always stored
in the atom (eliminating Atom.xyz and Chunk.curpos, adding Atom._posn,
eliminating incremental update of atpos/basepos). Motivation is to make it
simpler to rewrite high-frequency methods in Pyrex.

bruce 060313 splitting _recompute_atlist out of _recompute_atpos, and planning
to remove atom.index from undoable state. Rules for atom.index (old, reviewed
now and reconfirmed): owned by atom.molecule; value doesn't matter unless
atom.molecule and its .atlist exist (but is set to -1 otherwise when this is
convenient, to help catch bugs); must be correct whenever atom.molecule.atlist
exists (and is reset when it's made); correct means it's an index for that
atom into .atlist, .atpos, .basepos, whichever of those exist at the time
(atlist always does). This means a chunk's addatom, delatom, and _undo_update
need to invalidate its .atlist, and means there's no need to store atom.index
as undoable state (making diffs more compact), or to update a chunk's .atpos
(or even .atlist) when making an undo checkpoint.

(It would be nice for Undo to not store copies of changed .atoms dicts of
chunks too, but that's harder. ###e)

[update, bruce 060411: I did remove atom.index from undoable state, as well as
chunk.atoms, and I made atoms always store their own absposns. I forgot to
summarize the new rules here -- maybe I did somewhere else. Looking at the
code now, atoms still try to get baseposns from their chunk, which still
computes that before drawing them; moving a chunk probably invalidates atpos
and basepos (guess, but _recompute_atpos inval decl code would seem wrong
otherwise) and drawing it then recomputes them -- or maybe not, since it's
only when remaking display list that it should need to. Sometime I should
review this and see if there is some obvious optimization needed.]

bruce 080305 changed superclass from Node to NodeWithAtomContents

bruce 090115 split Chunk_Dna_methods from here into a new mixin class

bruce 090100 split Chunk_mmp_methods from here into a new mixin class

bruce 090100 split Chunk_drawing_methods from here into a new mixin class
"""

import Numeric # for sqrt

from Numeric import array
from Numeric import add
from Numeric import dot
from Numeric import PyObject
from Numeric import argsort
from Numeric import compress
from Numeric import nonzero
from Numeric import take
from Numeric import argmax


from utilities.Comparison import same_vals

from utilities.constants import gensym, genKey
from utilities.constants import diDEFAULT
from utilities.constants import diINVISIBLE
from utilities.constants import diDNACYLINDER
from utilities.constants import diPROTEIN
from utilities.constants import ATOM_CONTENT_FOR_DISPLAY_STYLE
from utilities.constants import noop

from utilities.debug import print_compact_stack
## from utilities.debug import compact_stack
from utilities.debug import print_compact_traceback
from utilities.debug import safe_repr

from utilities import debug_flags

from utilities.GlobalPreferences import pref_show_node_color_in_MT
from utilities.icon_utilities import imagename_to_pixmap

from geometry.BoundingBox import BBox
from geometry.VQT import V, Q, A, vlen

import foundation.env as env

from foundation.NodeWithAtomContents import NodeWithAtomContents
from foundation.inval import InvalMixin
from foundation.changes import SelfUsageTrackingMixin, SubUsageTrackingMixin
    #bruce 050804, so glpanes can know when they need to redraw a chunk's display list,
    # and chunks can know when they need to inval that because something drawn into it
    # would draw differently due to a change in some graphics pref it used
from foundation.state_constants import S_REF, S_CHILDREN_NOT_DATA
from foundation.undo_archive import set_undo_nullMol

from graphics.display_styles.displaymodes import get_display_mode_handler
from graphics.drawables.Selobj import Selobj_API # REVIEW: here or Chunk_drawing_methods?

from model.bonds import bond_copied_atoms
from model.chem import Atom # for making bondpoints, and a prefs function
from model.elements import PeriodicTable
from model.elements import Singlet
from model.ExternalBondSet import ExternalBondSet
from model.global_model_changedicts import _changed_parent_Atoms

from model.Chunk_Dna_methods import Chunk_Dna_methods
from model.Chunk_drawing_methods import Chunk_drawing_methods
from model.Chunk_mmp_methods import Chunk_mmp_methods

from commands.ChunkProperties.ChunkProp import ChunkProp

# ==

_inval_all_bonds_counter = 1 # private global counter [bruce 050516]

# == some debug code is near end of file


# == Molecule (i.e. Chunk)

# Historical note:
#
# (Josh wrote:)
# I use "molecule" and "part" interchangeably throughout the program.
# this is the class intended to represent rigid collections of
# atoms bonded together, but it's quite possible to make a molecule
# object with unbonded atoms, and with bonds to atoms in other
# molecules
#
# [bruce 050315 adds: I've seen "part" used for the assembly, but not for "chunk"
#  (which is the current term for instances of class molecule aka Chunk).
#  Now, however, each assy has one or more Parts, each with its own
#  physical space, containing perhaps many bonded chunks. So any use of
#  "part" to mean "chunk" would be misleading.]

# Note: we immediately kill any Chunk which loses all its atoms after having
# had some. If this ever causes problems (unlikely -- it's been done since
# 041116), we should instead do it when we update the model tree or glpane,
# since we need to ensure it's always done by the end of any user event.

_superclass = NodeWithAtomContents #bruce 080305 revised this

class Chunk(Chunk_Dna_methods, Chunk_drawing_methods, Chunk_mmp_methods,
            NodeWithAtomContents, 
            InvalMixin,
            SelfUsageTrackingMixin, SubUsageTrackingMixin,
            Selobj_API ):
    """
    A set of atoms treated as a unit.
    """
    #bruce 071114 renamed this from class molecule -> class Chunk

    # class constants to serve as default values of attributes, and _s_attr
    # decls for some of them

    _hotspot = None

    _s_attr_hotspot = S_REF 
        #bruce 060404 revised this in several ways; 
        # bug 1633 (incl. all subbugs) will need retesting.
        # Note that this declares hotspot, not _hotspot, so that undo state
        # never contains dead atoms. This is only ok because we provide
        # _undo_setattr_hotspot as well.
        #
        # Note that we don't put this (or Jig.atoms) into the 'atoms'
        # _s_attrlayer, since we still need to scan them as data.
        #
        # Here are some old comments from when this declared _hotspot, still
        # relevant: todo: warn somehow if you hit a StateMixin object in S_REF
        # but didn't store state for it (as could happen when we declared
        # _hotspot as data, not child, and it could be a dead atom); ideally
        # we'd add debug code to detect the original error (declaring
        # hotspot), due to presence of a _get_hotspot method; maybe we'd have
        # an optional method (implemented by InvalMixin) to say whether an
        # attr is legal for an undoable state decl. But (060404) there needs
        # to be an exception, e.g. when _undo_setattr_hotspot exists, like
        # now.

    _colorfunc = None
    _dispfunc = None

    is_movable = True #mark 060120 
        # [no need for _s_attr decl, since constant for this class -- bruce guess 060308]

    # Undoable/copyable attrs: 
    # (no need for _s_attr decls since copyable_attrs provides them)

    # self.display overrides global display (GLPane.display)
    # but is overriden by atom value if not default

    display = diDEFAULT

    # this overrides atom colors if set
    color = None

    # user_specified_center -- as of 050526 it's sometimes used
    # [but only in commented-out code as of 090113], but it's always None.
    #
    # note: if we implement self.user_specified_center as user-settable,
    # it also needs to be moved/rotated with the mol, like a datum point
    # rigidly attached to the mol (or like an atom)

    ## user_specified_center = None # never changed for now, so not in copyable_attrs

    copyable_attrs = _superclass.copyable_attrs + \
                   ('display', 'color', 'protein') + \
                   Chunk_Dna_methods._dna_copyable_attrs
        # this extends the copyable_attrs tuple from Node
        # (could add _colorfunc, but better to handle it separately in case this
        #  gets used for mmp writing someday. as of 051003 _colorfunc would
        #  anyway not be permitted since state_utils.copy_val doesn't know
        #  how to copy it.)
        #e should add user_specified_center once that's in active use

    #bruce 060313 no longer need to store diffs of our .atoms dict!
    # But still need to scan them as children (for now -- maybe not for much longer).
    # Do we implement _s_scan_children, or declare .atoms as S_CHILDREN_NOT_DATA??
    # I think the latter is simpler, so I'll try it. 
    ## _s_attr_atoms = S_CHILDREN
    _s_attr_atoms = S_CHILDREN_NOT_DATA
    _s_attrlayer_atoms = 'atoms' #bruce 060404

    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  (in this case its gives the path of an 'chunk icon')
    # see PM.PM_SelectionListWidget.insertItems for an example use of this
    # attribute.
    iconPath = "ui/modeltree/Chunk.png"

    # no need to _s_attr_ decl basecenter and quat -- they're officially
    # arbitrary, and get replaced when things get recomputed
    # [that's the theory, anyway... bruce 060223]

    # flags to tell us that our ExternalBondSets need updating
    # (they might have lost or gained external bonds between specific
    #  chunk pairs, of self and some other chunk). Note that this can happen
    # even if self.externs remains unchanged, if one of it's bonds' other atoms
    # changes parent. Here are the reasons these need to be set, and where we do that:
    # - changes inside a bond:
    #   - make it: Bond.__init__
    #   - delete it or change one of its atoms: each caller of Atom.unbond
    #   - change atoms by Undo/Redo: Atom._undo_update (since its list of bonds
    #      changes); note that Bond._undo_udpate doesn't have enough info to do
    #      this, since it doesn't know the old atom if one got replaced
    # - changes to an atom's parent chunk (.molecule):
    #   Chunk.invalidate_atom_lists (also called by Chunk._undo_update)
    # [bruce 080702]
    _f_lost_externs = False
    _f_gained_externs = False

    # Set this to True if any of the atoms in this chunk have their
    # overlayText set to anything other than None.  This keeps us from
    # having to test that for every single atom in every single chunk
    # each time the screen is rerendered. It is not reset to False
    # except when no atoms happen to have overlayText when self is rendered --
    # in other words, it's only a hint -- false positives are permitted.
    chunkHasOverlayText = False
    
    showOverlayText = False 
        # whether the user wishes to see the overlay text on this chunk
        # (used in Chunk_drawing_methods)

    protein = None # this is set to an object of class Protein in some chunks
    
    glpane = None #bruce 050804 ### TODO: RENAME (last glpane we displayed on??)
        # (also used/set in Chunk_drawing_methods)

    # ==

    # note: def __init__ occurs below a few undo-related methods. TODO: move them below it.

    def _undo_update(self): #bruce 060223 (initial super-conservative overkill version -- i hope)
        """
        [guess at API, might be revised/renamed]
        This is called when Undo has set some of our attributes, using setattr,
        in case we need to invalidate or update anything due to that.
        Note: it is only called if we are now alive (reachable in the model
        state). See also _f_invalidate_atom_lists_and_maybe_deallocate_displist,
        which is called (later) whether we are now alive or dead.
        """
        assert self.assy is not None #bruce 080227 guess (from docstring) 
            # [can fail, 080325, tom bug when updater turned on after separate @@@]
        # One thing we know is required: if self.atoms changes, invalidate self.atlist.
        # This permits us to not store atom.index as undoable state, and to not update
        # self.atpos before undo checkpoints. [bruce 060313]
        self.invalidate_everything() # this is probably overkill, but its call 
            # of self.invalidate_atom_lists() is certainly needed

        self._colorfunc = None
        del self._colorfunc #bruce 060308 precaution; might fix (or
            # cause?) some "Undo in Extrude" bugs

        self._dispfunc = None
        del self._dispfunc

        _superclass._undo_update(self)
            # (Q: what's the general rule for whether to call our superclass
            #  implem before or after running our own code in this method?
            #  A: guess: this method is more like destroy than create, so do
            #  high-level (subclass) code first. If it turns out this method
            #  has some elements of both destroy and create, perhaps do only
            #  the destroy-like elements before the superclass implem.)
        return

    def _undo_setattr_hotspot(self, hotspot, archive): 
        """
        [undo API method]
        
        Undo is mashing changed state into lots of objects' attrs at once;
        this lets us handle that specially, just for self.hotspot, but in 
        unknown order (for now) relative either to our attrs or other objects.
        """
        #bruce 060404; 060410 use store_if_invalid to fix new bug 1829
        self.set_hotspot( hotspot, store_if_invalid = True)

    # ==

    def __init__(self, assy, name = None):
        self._invalidate_all_bonds() 
            # bruce 050516 -- needed in __init__ to make sure
            # the counter it sets is always set, and always unique
        # Note [bruce 041116]:
        # new chunks are NOT automatically added to assy.
        # This has to be done separately (if desired) by assy.addmol
        # (or the equivalent).
        # addendum [bruce 050206 -- describing the situation, not endorsing it!]:
        # (and for clipboard chunks it should not be done at all!
        #  also not for chunks "created in a Group", if any; for those,
        #  probably best to do addmol/moveto like [some code] does.)
        if not self.mticon:
            self.init_icons()
        self.init_InvalMixin()
        ## dad = None
            #bruce 050216 removed dad from __init__ args, since no calls 
            # pass it and callers need to do more to worry about the 
            # location anyway (see comments above) 
        _superclass.__init__(self, assy, name or gensym("Chunk", assy))

        # atoms in a dictionary, indexed by atom.key
        self.atoms = {}

        # note: Jigs are stored on atoms, not directly in Chunk;
        # so are bonds, but we have a list of external bonds, self.externs,
        # which is computed by __getattr__ and _recompute_externs; we have
        # several other attributes computed by _get_ or _recompute_ methods
        # using InvalMixin.__getattr__, e.g. center, bbox, basepos, atpos.
        # [bruce 041112]

        # Chunk-relative coordinate system, used internally to speed up
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

        self.havelist = 0 # note: havelist is not handled by InvalMixin
        self.haveradii = 0 # ditto

        # hotspot: default place to bond this Chunk when pasted;
        # should be a singlet in this Chunk, or None.
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

        # REVIEW: do any of our memo_dict, glname, glpane attributes belong in
        # class Chunk_drawing_methods? See comments there about future
        # refactoring and its effect on various attributes. 
        # [bruce 090123 comment]

        self.memo_dict = {}
            # for use by anything that wants to store its own memo data on us,
            # using a key it's sure is unique [bruce 060608] 
            # (when we eventually have a real destroy method, it should zap
            # this; maybe this will belong on class Node #e)
        
        #glname is needed for highlighting the chunk as an independent object
        #NOTE: See a comment in self.highlight_color_for_modkeys() for more info.
        if not self.isNullChunk():
            self.glname = self.assy.alloc_my_glselect_name(self) #bruce 080917 revised
            ### REVIEW: is this ok or fixed if this chunk is moved to a new assy
            # (if that's possible)? [bruce 080917 Q]

        # keep track of other chunks we're bonded to; lazily updated
        # [bruce 080702]
        self._bonded_chunks = {}

        self._init_Chunk_drawing_methods()
        
        return # from Chunk.__init__

    # ==

    def isNullChunk(self): # by Ninad
        """
        @return: whether chunk is a "null object" (used as atom.molecule for some
        killed atoms).

        This is overridden in subclass _nullMol_Chunk ONLY.

        @see: _nullMol_Chunk.isNullChunk()
        """
        return False

    def make_glpane_cmenu_items(self, contextMenuList, command): # by Ninad
        """
        Make glpane context menu items for this chunk (and append them to
        contextMenuList), some of which may be specific to the given command
        (presumably the current command) based on its having a commandName
        for which we have special-case code.
        """
        # Note: See make_selobj_cmenu_items in other classes. This method is very
        # similar to that method. But it's not named the same because the chunk
        # may not be a glpane.selobj (as it may get highlighted in SelectChunks
        # mode even when, for example, the cursor is over one of its atoms 
        # (i.e. selobj = an Atom). So ideally, that method and this one should be
        # unified somehow. This method exists only in class Chunk and is called
        # only by certain commands. [comment originally by Ninad, revised by Bruce]

        assert command is not None
        
        #Start Standard context menu items rename and delete [by Ninad]

        parent_node_classes = (self.assy.DnaStrandOrSegment, 
                               self.assy.NanotubeSegment)
            ### TODO: refactor to not hardcode these classes,
            # but to have a uniform way to find the innermost node
            # visible in the MT, which is the node to be renamed.
        
            ### Also REVIEW whether what this finds (node_to_rename) is always
            # the same as the unit of hover highlighting, and if not, whether
            # it should be, and if so, whether the same code can be used to
            # determine the highlighted object and the object to rename or
            # delete. [bruce 081210 comments]
        
        parent_node = None
        
        for cls in parent_node_classes:
            parent_node = self.parent_node_of_class(cls)
            if parent_node:
                break

        node_to_rename = parent_node or self
        del parent_node
        
        name = node_to_rename.name
        
        item = (("Rename %s..." % name),
                node_to_rename.rename_using_dialog )
        contextMenuList.append(item)

        def delnode_cmd(node_to_rename = node_to_rename):
            node_to_rename.assy.changed() #bruce 081210 bugfix, not sure if needed
            node_to_rename.assy.win.win_update() #bruce 081210 bugfix
            node_to_rename.kill_with_contents()
            return
        
        del node_to_rename
        
        item = (("Delete %s" % name), delnode_cmd )
        contextMenuList.append(item)
        #End Standard context menu items rename and delete

        # Protein-related items
        #Urmi 20080730: edit properties for protein for context menu in glpane
        if command.commandName in ('SELECTMOLS', 'BUILD_PROTEIN'):
            if self.isProteinChunk():
                try:
                    protein = self.protein
                except:
                    print_compact_traceback("exception in protein class")
                    return 
                    ### REVIEW: is this early return appropriate? [bruce 090115 comment]
                if protein is not None:
                    item = (("%s" % (self.name)),
                            noop, 'disabled')
                    contextMenuList.append(item)
                    item = (("Edit Protein Properties..."), 
                            (lambda _arg = self.assy.w, protein = protein:
                             protein.edit(_arg))
                             )
                    contextMenuList.append(item)
                    pass
                pass
            pass
        
        # Nanotube-related items
        if command.commandName in ('SELECTMOLS', 'BUILD_NANOTUBE', 'EDIT_NANOTUBE'):
            if self.isNanotubeChunk():
                try:
                    segment = self.parent_node_of_class(self.assy.NanotubeSegment)
                except:
                    # A graphene sheet or a simple chunk that thinks it's a nanotube.

                    # REVIEW: the above comment (and this code) must be wrong,
                    # because parent_node_of_class never has exceptions unless
                    # it has bugs. So I'm adding this debug print. The return
                    # statement below was already there. If the intent
                    # was to return when segment is None, that was not there
                    # and is not there now, and needs adding separately.
                    # [bruce 080723 comment and debug print]
                    print_compact_traceback("exception in %r.parent_node_of_class: " % self)
                    return
                    ### REVIEW: is this early return appropriate? [bruce 090115 comment]
                if segment is not None:
                    # Self is a member of a Nanotube group, so add this 
                    # info to a disabled menu item in the context menu.
                    item = (("%s" % (segment.name)),
                            noop, 'disabled')
                    contextMenuList.append(item)

                    item = (("Edit Nanotube Properties..."), 
                            segment.edit)
                    contextMenuList.append(item)
                    pass
                pass
            pass
        
        # Dna-related items
        if command.commandName in ('SELECTMOLS', 'BUILD_DNA', 'DNA_SEGMENT', 'DNA_STRAND'):
            self._make_glpane_cmenu_items_Dna(contextMenuList)
        
        return # from make_glpane_cmenu_items

    def nodes_containing_selobj(self): #bruce 080508 bugfix
        """
        @see: interface class Selobj_API for documentation
        """
        # safety check in case of calls on out of date selobj:
        if self.killed():
            return []
        return self.containing_nodes()

    def _update_bonded_chunks(self): #bruce 080702
        """
        Make sure our map from (other chunk -> ExternalBondSet for self and it)
        (stored in self._bonded_chunks) is up to date, and that those
        ExternalBondSets have the correct subsets of our external bonds.
        Use the flags self._f_lost_externs and self._f_gained_externs to know
        what needs checking, and reset them.
        """
        maybe_empty = []
        if self._f_lost_externs:
            for ebset in self._bonded_chunks.itervalues():
                ebset.remove_incorrect_bonds()
                if ebset.empty():
                    maybe_empty.append(ebset)
                        # but don't yet remove it from self._bonded_chunks --
                        # we might still add bonds below
            self._f_lost_externs = False
        if self._f_gained_externs:
            for bond in self.externs: # this might recompute self.externs
                otherchunk = bond.other_chunk(self)
                ebset = self._bonded_chunks.get(otherchunk) # might be None
                if ebset is None:
                    ebset = otherchunk._bonded_chunks.get( self) # might be None
                    if ebset is None:
                        ebset = ExternalBondSet( self, otherchunk)
                        otherchunk._bonded_chunks[ self] = ebset
                    else:
                        # ebset was memoized in otherchunk but not in self -- 
                        # this should never happen
                        # (since the only way to make one is the above case,
                        #  which ends up storing it in both otherchunk and self,
                        #  and the only way to remove one removes it from both)
                        print "likely bug: ebset %r was in %r but not in %r" % \
                              (ebset, otherchunk, self)
                    self._bonded_chunks[ otherchunk] = ebset
                    pass
                ebset.add_bond( bond) # ok if bond is already there
            self._f_gained_externs = False
        # if some of our ExternalBondSets are now empty, destroy them
        # (this removes them from *both* their chunks, not only from self)
        for ebset in maybe_empty:
            if ebset.empty():
                ebset.destroy()
        return

    def _destroy_bonded_chunks(self):
        for ebset in self._bonded_chunks.values():
            ebset.destroy()
        self._bonded_chunks = {} # precaution (should be already true)
        return

    def _f_remove_ExternalBondSet(self, ebset):
        otherchunk = ebset.other_chunk(self)
        del self._bonded_chunks[otherchunk]
        
    def edit(self):
        ### REVIEW: model tree has a special case for isProteinChunk;
        # should we pull that in here too? Guess yes.
        # (Note, there are several other uses of isProteinChunk
        #  that might also be worth refactoring.) [bruce 090106 comment]
        if self.isStrandChunk():
            self._editProperties_DnaStrandChunk()
        else:
            cntl = ChunkProp(self)
            cntl.exec_()
            self.assy.mt.mt_update()
            ### REVIEW [bruce 041109]: don't we want to repaint the glpane, too?

    def getProps(self): # probably by Ninad
        """
        To be revised post dna data model. Used in EditCommand class and its 
        subclasses.
        """
        return ()

    def setProps(self, params): # probably by Ninad
        """
        To be revised post dna data model.
        """
        del params

    #START of Nanotube chunk specific code ========================

    def isNanotubeChunk(self): # probably by Mark
        """
        Returns True if *all atoms* in this chunk are either:
        - carbon (sp2) and either all hydrogen or nitrogen atoms or bondpoints
        - boron and either all hydrogen or nitrogen atoms or bondpoints

        @warning: This is a very loose test. It will return True if self is a
        graphene sheet, benzene ring, etc. Use at your own risk.
        """
        found_carbon_atom = False # CNT
        found_boron_atom = False  # BNNT

        for atom in self.atoms.itervalues():
            if atom.element.symbol == 'C':
                if atom.atomtype.is_planar():
                    found_carbon_atom = True
                else:
                    return False
            elif atom.element.symbol == 'B':
                found_boron_atom = True
            elif atom.element.symbol == 'N':
                pass
            elif atom.element.symbol == 'H':
                pass
            elif atom.is_singlet():
                pass
            else:
                # other kinds of atoms are not allowed
                return False

            if found_carbon_atom and found_boron_atom:
                return False
            continue

        return True  

    def getNanotubeSegment(self): # ninad 080205
        """
        Return the NanotubeSegment of this chunk if it has one. 
        """
        return self.parent_node_of_class(self.assy.NanotubeSegment)

    #END of Nanotube chunk specific code ========================

    def _f_invalidate_atom_lists_and_maybe_deallocate_displist(self): #e rename, see below
        """
        [friend method to be called by _fix_all_chunk_atomsets_differential
         in undo_archive; called at least
         whenever Undo makes a chunk dead w/o calling self.kill,
         which it does when undoing chunk creation or redoing chunk deletion;
         also called on many other changes by undo or redo, for either alive
         or dead chunks.]
        """
        self.invalidate_atom_lists()
        
        #bruce 071105 created this method and made undo call it
        # instead of just calling invalidate_atom_lists directly,
        # so the code below is new. It's needed to make sure that
        # undo of chunk creation, or redo of chunk kill, deallocates
        # its display list. See comment next to call about a more
        # general mechanism (nim) that would be better in the undo
        # interface to us than this friend method.
        
        # REVIEW: would a better name and more general description be something
        # like "undo has modified your atoms dict, do necessary invals and 
        # deallocates"? I think it would; so I'll split it into two methods, 
        # one to keep here and one to move into Chunk_drawing_methods for now.
        # [bruce 090123]
        
        self._deallocate_displist_if_needed()
        return
    
    # ==

    def contains_atom(self, atom): #bruce 070514
        """
        Does self contain the given atom (a real atom or bondpoint)?
        """
        #e the same-named method would be useful in Node, Selection, etc, someday
        return atom.molecule is self

    def break_interpart_bonds(self): #bruce 050308-16 to help fix bug 371; revised 050513
        """
        [overrides Node method]
        """
        assert self.part is not None
        # check atom-atom bonds
        for b in self.externs[:]:
            #e should this loop body be a bond method??
            m1 = b.atom1.molecule # one of m1, m2 is self but we won't bother finding out which
            m2 = b.atom2.molecule
            try:
                bad = (m1.part is not m2.part)
            except: # bruce 060411 bug-safety
                if m1 is None:
                    m1 = b.atom1.molecule = _get_nullMol()
                    print "bug: %r.atom1.molecule was None (changing it to _nullMol)" % b
                if m2 is None:
                    m2 = b.atom2.molecule = _get_nullMol()
                    print "bug: %r.atom2.molecule was None (changing it to _nullMol)" % b
                bad = True
            if bad:
                # bruce 060412 print -> print_compact_stack
                # e.g. this will happen if above code sets a mol to _nullMol
                #bruce 080227 revised following debug prints; maybe untested
                #bruce 080410 making them print, not print_compact_stack, temporarily;
                # they are reported to happen with paste chunk with hotspot onto open bond
                if m1.part is None:
                    msg = "possible bug: %r .atom1 == %r .mol == %r .part is None" % \
                        ( b, b.atom1, m1 )
                    if debug_flags.atom_debug:
                        print_compact_stack( "\n" + msg + ": " )
                    else:
                        print msg
                if m2.part is None:
                    msg = "possible bug: %r .atom2 == %r .mol == %r .part is None" % \
                        ( b, b.atom2, m2 )
                    if debug_flags.atom_debug:
                        print_compact_stack( "\n" + msg + ": " )
                    else:
                        print msg
                b.bust() 
        # someday, maybe: check atom-jig bonds ... but callers need to handle
        # some jigs specially first, which this would destroy...
        # actually this would be inefficient from this side (it would scan
        # all atoms), so let's let the jigs handle it... though that won't work
        # when we can later apply this to a subtree... so review it then.
        return

    def set_hotspot(self, hotspot, silently_fix_if_invalid = False, store_if_invalid = False):
        #bruce 050217; 050524 added keyword arg; 060410 renamed it & more
        
        # first make sure no other code forgot to call us and set it directly
        assert not 'hotspot' in self.__dict__.keys(), "bug in some unknown other code"
        if self._hotspot is not hotspot:
            self.changed() 
                #bruce 060324 fix bug 1532, and an unreported bug where this
                #didn't mark file as modified
        self._hotspot = hotspot
        if not store_if_invalid: 
            # (when that's true, it's important not to recompute self.hotspot,
            #  even in an assertion)
            # now recompute self.hotspot from the new self._hotspot (to check
            # whether it's valid)
            self.hotspot # note: this has side effects we depend on!
            assert self.hotspot is hotspot or silently_fix_if_invalid, \
                   "getattr bug, or specified hotspot %s is invalid" % \
                   safe_repr(hotspot)
        assert not 'hotspot' in self.__dict__.keys(), \
               "bug in getattr for hotspot or in set_hotspot"
        return

    def _get_hotspot(self): #bruce 050217; used by getattr
        hs = self._hotspot
        if hs is None:
            return None
        if hs.is_singlet() and hs.molecule is self:
            # hs should be a valid hotspot; if you see no bug, return it
            if hs.killed_with_debug_checks(): # this also checks whether its key is in self.atoms
                # bug detected
                if debug_flags.atom_debug:
                    print "_get_hotspot sees killed singlet still claiming to be in this Chunk"
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

    # Lists of icon basenames (relative to cad/src/ui/modeltree)
    # in same order as dispNames / dispLabel. Each list has an entry
    # for each atom display style. One list is for normal use,
    # one for hidden chunks.
    #
    # Note: these lists should *not* include icons for ChunkDisplayMode
    # subclasses such as DnaCylinderChunks. See 'def node_icon' below
    # for the code that handles those. [bruce comment 080213]

    mticon_names = [
        "Default.png",
        "Invisible.png",
        "CPK.png",
        "Lines.png",
        "Ball_and_Stick.png",
        "Tubes.png"]

    hideicon_names = [
        "Default-hide.png",
        "Invisible-hide.png",
        "CPK-hide.png",
        "Lines-hide.png",
        "Ball_and_Stick-hide.png",
        "Tubes-hide.png"]

    mticon = []
    hideicon = []
    
    def init_icons(self):
        # see also the same-named, related method in class Jig.
        """
        each subclass must define mticon = [] and hideicon = [] as class constants...
        but Chunk is the only subclass, for now.
        """
        if self.mticon or self.hideicon:
            return
        # the following runs once per NE1 session.
        for name in self.mticon_names:
            self.mticon.append( imagename_to_pixmap( "modeltree/" + name))
        for name in self.hideicon_names:
            self.hideicon.append( imagename_to_pixmap( "modeltree/" + name))
        return
    
    def node_icon(self, display_prefs): 
        if self.isProteinChunk():
            # Special case for protein icon (for MT only). 
            # (For PM_SelectionListWidget, the attr iconPath was modified in
            #  isProteinChunk() in separate code.) --Mark 2008-12-16.
            hd = get_display_mode_handler(diPROTEIN)
            if hd:
                return hd.get_icon(self.hidden)
        try:
            if self.hidden:
                return self.hideicon[self.display]
            else:
                return self.mticon[self.display]
        except IndexError:
            # KLUGE: detect self.display being a ChunkDisplayMode [bruce 060608]
            hd = get_display_mode_handler(self.display)
            if hd:
                return hd.get_icon(self.hidden)
            # else, some sort of bug
            return imagename_to_pixmap("modeltree/junk.png")
        pass

    # lowest-level structure-changing methods

    def addatom(self, atom):
        """
        Private method;
        should be the only way new atoms can be added to a Chunk
        (except for optimized callers like Chunk.merge, and others with comments
         saying they inline it).
        
        Add an existing atom (with no current Chunk, and with a valid literal
        .xyz field) to the Chunk self, doing necessary invals in self, but not yet
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
        ## atom.invalidate_bonds() # might not be needed
        ## [definitely not after bruce 050516, since changing atom.molecule is enough;
        #   if this is not changing it, then atom was in _nullMol and we don't care
        #   whether its bonds are valid.]
        # make atom know self as its .molecule
        assert atom.molecule is None or atom.molecule is _nullMol
#bruce 080220 new feature -- but now being done elsewhere (more efficient,
# and useless here unless also done in all inlined versions, which is hard):
##        if atom._f_assy is not self.assy:
##            atom._f_set_assy(self.assy)
        atom.molecule = self
        _changed_parent_Atoms[atom.key] = atom #bruce 060322
        atom.index = -1 # illegal value
        # make Chunk self have atom
        self.atoms[atom.key] = atom
        self.invalidate_atom_lists()
        return

    def delatom(self, atom):
        """
        Private method;
        should be the only way atoms can be removed from a Chunk
        (except for optimized callers like Chunk.merge).
        
        Remove atom from the Chunk self, preparing atom for being destroyed
        or for later addition to some other mol, doing necessary invals in self,
        and (for safety and possibly to break cycles of python refs) removing all
        connections from atom back to self.
        """
        ## atom.invalidate_bonds() # not needed after bruce 050516; see comment in addatom
        self.invalidate_atom_lists() # do this first, in case exceptions below

        # make atom independent of self
        assert atom.molecule is self
        atom.index = -1 # illegal value
        # inlined _get_nullMol:
        global _nullMol
        if _nullMol is None:
            # this caused a bus error when done right after class Chunk
            # defined; don't know why (class Node not yet ok??) [bruce 041116]
            ## _nullMol = Chunk("<not an assembly>", 'name-of-_nullMol')
            # this newer method might or might not have that problem
            _nullMol = _make_nullMol()
        atom.molecule = _nullMol # not a real mol; absorbs invals without harm
        _changed_parent_Atoms[atom.key] = atom #bruce 060322
        # (note, we *don't* add atom to _nullMol.atoms, or do invals on it here;
        #  see comment about _nullMol where it's defined)

        # make self forget about atom
        del self.atoms[atom.key] # callers can check for KeyError, always an error
        if not self.atoms:
            self.kill() # new feature, bruce 041116, experimental
        return

    # some invalidation methods

    def invalidate_atom_lists(self, invalidate_atom_content = True):
        """
        private method (but also called directly from undo_archive):
        for now this is the same for addatom and delatom
        so we have common code for it --
        some atom is joining or leaving this mol, do all needed invals
        (or this can be called once if many atoms are joining and/or leaving)
        """
        # Note: as of 060409 I think Undo/Redo can call this on newly dead Chunks
        # (from _fix_all_chunk_atomsets_differential, as of 071105 via the new
        #  method _f_invalidate_atom_lists_and_maybe_deallocate_displist);
        # I'm not 100% sure that's ok, but I can't see a problem in the method
        # and I didn't find a bug in testing. [bruce 060409]

        self.havelist = 0
        self.haveradii = 0
        self._f_lost_externs = True
        self._f_gained_externs = True

        if invalidate_atom_content:
            self.invalidate_atom_content() #bruce 080306

        # bruce 050513 try to optimize this
        # (since it's 25% of time to read atom records from mmp file, 1 sec for 8k atoms)
        ## self.invalidate_attrs(['externs', 'atlist'])
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
                # this is what makes it ok for atom indices to be invalid, as
                # they are when self.atoms changes, until self.atlist is next
                # recomputed [bruce 060313 comment]
        except:
            pass
        else:
            need = 1
        if need:
            # this causes trouble, not yet sure why:
            ## self.changed_attrs(['externs', 'atlist'])
            ## AssertionError: validate_attr finds no attr 'externs' was saved, 
            ## in <Chunk 'Ring Gear' (5167 atoms) at 0xd967440>
            # so do this instead:
            self.externs = self.atlist = -1
            self.invalidate_attrs(['externs', 'atlist'])
        return

    def _ac_recompute_atom_content(self): #bruce 080306
        """
        Recompute and return (but do not record) our atom content,
        optimizing this if it's exactly known on any node-subtrees.

        @see: Atom.setDisplayStyle, Atom.revise_atom_content

        [Overrides superclass method. Subclasses whose atoms are stored differently
         may need to override this further.]
        """
        atom_content = 0
        for atom in self.atoms.itervalues():
            ## atom_content |= (atom._f_updated_atom_content())
                # IMPLEM that method on class Atom (look up from self.display)?
                # no, probably best to inline it here instead:
            atom_content |= ATOM_CONTENT_FOR_DISPLAY_STYLE[atom.display]
                # possible optimizations, if needed:
                # - could use 1<<(atom.display) and then postprocess
                # to add AC_HAS_INDIVIDUAL_DISPLAY_STYLE, if we wanted to inline
                # the definition of ATOM_CONTENT_FOR_DISPLAY_STYLE
                # - could skip bondpoints
                # - could skip all diDEFAULT atoms [###doit]
        return atom_content

    def invalidate_everything(self):
        """
        Invalidate all invalidatable attrs of self.
        (Used in _undo_update and in some debugging methods.)
        """
        self._invalidate_all_bonds()
        self.invalidate_atom_lists() # _undo_update depends on us calling this
        attrs  = self.invalidatable_attrs()
        # now this is done in that method: 
        ## attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            self.invalidate_attr(attr)
        # (these might be sufficient: ['externs', 'atlist', 'atpos'])
        return

    # debugging methods (not fully tested, use at your own risk)

    def update_everything(self):
        attrs  = self.invalidatable_attrs()
        # now this is done in that method: 
        ## attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            junk = getattr(self, attr)
        # don't actually remake display list, but next redraw will do that;
        # don't invalidate it (havelist = 0) since our semantics are to only
        # update.
        return

    # some more invalidation methods

    def changed_atom_posn(self): #bruce 060308
        """
        One of self's atoms changed position; 
        invalidate whatever we might own that depends on that.
        """
        # initial implem might be too conservative; should optimize, perhaps
        # recode in a new Pyrex ChunkBase. Some code is copied from
        # now-obsolete setatomposn; some of its comments might apply here as
        # well.
        self.changed()
        self.havelist = 0
        self.invalidate_attr('atpos') #e should optim this 
            ##k verify this also invals basepos, or add that to the arg of this call
        return

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
        """
        Recompute self.singlets, a list of self's bondpoints.
        """
        # (Filter always returns a python list, even if atlist is a Numeric.array
        # [bruce 041207, by separate experiment]. Some callers test the boolean
        # value we compute for self.singlets. Since the elements are pyobjs,
        # this would probably work even if filter returned an array.)
        return filter( lambda atom: atom.element is Singlet, self.atlist )

    _inputs_for_singlpos = ['singlets', 'atpos']
    def _recompute_singlpos(self):
        """
        Recompute self.singlpos, a Numeric array of self's bondpoint positions
        (in absolute coordinates).
        """
        self.atpos
        # we must access self.atpos, since we depend on it in our inval rules
        # (if that's too slow, then anyone invalling atpos must inval this too #e)
        if len(self.singlets):
            return A( map( lambda atom: atom.posn(), self.singlets ) )
        else:
            return []
        pass

    # These 4 attrs are stored in one tuple, so they can be invalidated
    # quickly as a group.

    def _get_polyhedron(self): # self.polyhedron
        return self.poly_evals_evecs_axis[0]
#bruce 060119 commenting these out since they are not used,
# though if we want them it's fine to add them back.
#bruce 060608 renamed them with plural 's'.
##    def _get_evals(self): # self.evals
##        return self.poly_evals_evecs_axis[1]
##    def _get_evecs(self): # self.evecs
##        return self.poly_evals_evecs_axis[2]
    def _get_axis(self): # self.axis
        return self.poly_evals_evecs_axis[3]

    _inputs_for_poly_evals_evecs_axis = ['basepos']
    def _recompute_poly_evals_evecs_axis(self):
        return shakedown_poly_evals_evecs_axis( self.basepos)

    def full_inval_and_update(self): # bruce 041112-17
        """
        Public method (but should not usually be needed):
        invalidate and then recompute everything about a mol.
        Some old callers of shakedown might need to call this now,
        if there are bugs in the inval/update system for mols.
        And extrude calls it since it uses the deprecated method
        set_basecenter_and_quat.
        """
        # full inval:
        self.havelist = 0
        self.haveradii = 0
        self.invalidate_attrs(['atlist', 'externs']) # invalidates everything, I think
        assert not self.valid_attrs(), \
               "full_inval_and_update forgot to invalidate something: %r" % self.valid_attrs()
        # full update (but invals bonds):
        self.atpos # this invals all internal bonds (since it revises basecenter); we depend on that
        # self.atpos also recomputes some other things, but not the following -- do them all:
        self.bbox
        self.singlpos
        self.externs
        self.axis
        self.get_sel_radii_squared()
        assert not self.invalid_attrs(), \
               "full_inval_and_update forgot to update something: %r" % self.invalid_attrs()
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

    def _recompute_atlist(self): #bruce 060313 split out of _recompute_atpos
        """
        Recompute self.atlist, a list or Numeric array of this chunk's atoms
        (including bondpoints), ordered by atom.key.
        Also set atom.index on each atom in the list, to its index in the list.
        """
        atomitems = self.atoms.items()
        atomitems.sort() 
            # in order of atom keys; probably doesn't yet matter, but makes order deterministic
        atlist = [atom for (key, atom) in atomitems]
        self.atlist = array(atlist, PyObject) #review: untested whether making it an array is good or bad
        for atom, i in zip(atlist, range(len(atlist))):
            atom.index = i 
        return        

    _inputs_for_atpos = ['atlist'] # also incrementally modified by setatomposn [not anymore, 060308]
        # (Atpos could be invalidated directly, but maybe it never is (not sure);
        #  anyway we don't optim for that.)
    _inputs_for_basepos = ['atpos'] # also invalidated directly, but not often

    def _recompute_atpos(self): 
        """
        recompute self.atpos and self.basepos and more;
        also change self's local coordinate system (used for basepos)
        [#doc more]
        """
        #bruce 060308 major rewrite
        #bruce 060313 splitting _recompute_atlist out of _recompute_atpos
        
        # Something must have been invalid to call us, so basepos must be
        # invalid. So we needn't call changed_attr on it.
        assert not self.__dict__.has_key('basepos')
        if self.assy is None:
            if debug_flags.atom_debug:
                # [bruce comment 050702: this happens if you delete the chunk
                # while dragging it by selatom in build mode]
                msg = "atom_debug: fyi, recompute atpos called on killed mol %r" % self
                print_compact_stack(msg + ": ")
        # Optional debug code:
        # This might be called if basepos doesn't exist but atpos does.
        # I don't think that can happen, but if it can, I need to know.
        # So find out which of the attrs we recompute already exist:
        ## print "_recompute_atpos on %r" % self
##        for attr in ['atpos', 'average_position', 'basepos']:
##            ## vq = self.validQ(attr)
##            if self.__dict__.has_key(attr):
##                print "fyi: _recompute_atpos sees %r already existing" % attr

        atlist = self.atlist # might call _recompute_atlist
        atpos = map( lambda atom: atom.posn(), atlist ) 
            # atpos, basepos, and atlist must be in same order
        atpos = A(atpos)
        # we must invalidate or fix self.atpos when any of our atoms' positions is changed!
        self.atpos = atpos

        assert len(atpos) == len(atlist)

        self._recompute_average_position() # sets self.average_position from self.atpos
        self.basecenter = + self.average_position # not an invalidatable attribute
            # unary '+' prevents mods to basecenter from affecting
            # average_position; it might not be needed (that depends on
            # Numeric.array += semantics).
        # Note: basecenter is arbitrary, but should be somewhere near the
        # atoms... except see set_basecenter_and_quat, used in extrudeMode --
        # it may be that it's not really arbitrary due to kluges in how that's
        # used [still active as of 070411].
        if debug_messup_basecenter:
            # ... so this flag lets us try some other value to test that!!
            blorp = messupKey.next()
            self.basecenter += V(blorp, blorp, blorp)
        self.quat = Q(1,0,0,0)
            # arbitrary value, except we assume it has this specific value to
            # simplify/optimize the next line
        if self.atoms:
            self.basepos = atpos - self.basecenter
                # set now (rather than when next needed) so it's still safe to
                # assume self.quat == Q(1,0,0,0)
        else:
            self.basepos = []
            # this has wrong type, so requires special code in mol.move etc
            ###k Could we fix that by just assigning atpos to it (no elements, 
            # so should be correct)?? [bruce 060119 question]

        assert len(self.basepos) == len(atlist)

        # note: basepos must be a separate (unshared) array object
        # (except when mol is frozen [which is no longer supported as of 060308]);
        # as of 060308 atpos (when defined) is a separate array object, 
        # since curpos no longer exists.
        self._changed_basecenter_or_quat_while_atoms_fixed()
            # (that includes self.changed_attr('basepos'), though an assert above
            # says that that would not be needed in this case.)

        # validate the attrs we set, except for the non-invalidatable ones,
        # which are curpos, basecenter, quat.
        self.validate_attrs(['atpos', 'average_position', 'basepos'])
        return # from _recompute_atpos

    # aliases, in case someone needs one of the other things we compute
    # (but not average_position, that has its own recompute method):
    _recompute_basepos   = _recompute_atpos

    def _changed_basecenter_or_quat_while_atoms_fixed(self):
        """
        [private method]
        If you change self.basecenter or self.quat while intending
        self's atoms to remain fixed in absolute space (rather than 
        moving along with those changes), first recompute self.basepos
        to be correct in the new local coordinates (or perhaps just
        invalidate self.basepos -- that use is unanalyzed and untried),
        then call this method to do necessary invals.
                
        This method invals other things (besides self.basepos) which depend 
        on self's local coordinate system -- i.e. self's internal bonds 
        and self.havelist; and it calls changed_attr('basepos').
        """ 
        self._invalidate_internal_bonds()
        self.changed_attr('basepos')
        self.havelist = 0

    def _invalidate_internal_bonds(self):
        self._invalidate_all_bonds() # easiest to just do this

    def _invalidate_all_bonds(self): #bruce 050516 optimized this
        global _inval_all_bonds_counter
        _inval_all_bonds_counter += 1
            # note: it's convenient that individual values of this global
            # counter are not used on more than one chunk, since that way
            # there's no need to worry about whether the bond inval/update
            # code, which should be the only code to look at this counter,
            # needs to worry that its data looks right but is for the wrong
            # chunks.
        self._f_bond_inval_count = _inval_all_bonds_counter
        return

    _inputs_for_average_position = ['atpos']
    def _recompute_average_position(self):
        """
        Compute or recompute self.average_position,
        the average position of the atoms (including singlets); store it,
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

    def _get_center_weight(self):#bruce 070411
        """
        Compute self.center_weight, the weight that should be given to self.center
        for making group centers as weighted averages of chunk centers.
        """
        return len(self.atoms)

    _inputs_for_bbox = ['atpos']
    def _recompute_bbox(self):
        """
        Recompute self.bbox, an axis-aligned bounding box (in absolute 
        coordinates) made from all of self's atom positions (including
        bondpoints), plus a fudge factor to account for atom radii.
        """
        self.bbox = BBox(self.atpos)

    # Center.

    def _get_center(self):
        # _get_center seems better than _recompute_center since this attr
        # is only needed by the UI and this method is fast
        """
        Compute self.center on demand, which is the center to use for rotations
        and stretches and perhaps some other purposes. Presently, this is
        always the average position of all atoms in self (including bondpoints).
        """
        ## if self.user_specified_center is not None:
        ##     return self.user_specified_center
        return self.average_position

    # What used to be called self.center, used mainly to relate basepos and curpos,
    # is now called self.basecenter and is not a recomputed attribute,
    # though it is chosen and stored by the _recompute_atpos method.
    # See also a comment about this in Chunk.__init__. [bruce 041112]

    # Externs
    _inputs_for_externs = [] # only invalidated by hand
    def _recompute_externs(self):
        """
        Recompute self.externs, the list of external bonds of self.
        """
        externs = []
        for atom in self.atoms.itervalues():
            for bond in atom.bonds:
                if bond.atom1.molecule is not self or \
                   bond.atom2.molecule is not self:
                    externs.append(bond)
        return externs

    # ==
    
    def get_dispdef(self, glpane = None):
        """
        @return: the display style we will use to draw self
        
        @see: getDisplayStyle
        """        
        # REVIEW: does this belong in class Chunk_drawing_methods? 
        # (Probably yes, once that's a cooperating class, with perhaps
        #  more than one instance for self, each with its own self.glpane?
        #  But note that this method itself doesn't access self.glpane.)
        #
        # And, how should it be refactored so each type of chunk 
        # (protein, dna, etc) has its own drawing code, including its own way
        # of interpreting display style settings (which themselves need a lot
        # of refactoring and generalization)? 
        # 
        # [bruce 091223 comments]
        
        if self.display != diDEFAULT:
            disp = self.display
        else:
            if glpane is None:
                glpane = self.assy.o
            disp = glpane.displayMode

        if disp == diDNACYLINDER and not self.isDnaChunk():
            # piotr 080409 fix bug 2785, revised by piotr 080709
            if self.isProteinChunk(): 
                disp = diPROTEIN
            else:
                disp = glpane.lastNonReducedDisplayMode

        if disp == diPROTEIN and not self.isProteinChunk():
            # piotr 080709
            if self.isDnaChunk():
                disp = diDNACYLINDER
            else:
                disp = glpane.lastNonReducedDisplayMode
                    
        return disp

    def inval_display_list(self): #bruce 050804
        """
        [public, though external uses are suspicious re modularity,
         and traditionally have been coded as changeapp calls instead]
        
        This is meant to be called when something whose usage we tracked
        (while making our display list) next changes.
        """
        # REVIEW: how does this relate to class Chunk_drawing_methods? Guess:
        # when that becomes a cooperating object, each one subscribes to this
        # somehow. [bruce 091223 comment]
        self.changeapp(0) # that now tells self.glpane to update, if necessary
        ###@@@ glpane needs to track changes anyway due to external bonds....
        # [not sure of status of this comment; as of bruce 060404]

    # ==

    def writepov(self, file, disp):
        """
        Draw self (if visible) into an open povray file
        (which already has whatever headers & macros it needs),
        using the given display mode unless self overrides it.
        """
        if self.hidden:
            return

        if self.display != diDEFAULT:
            disp = self.display

        drawn = self.part.repeated_bonds_dict
            # bruce 070928 bugfix: use repeated_bonds_dict
            # instead of a per-chunk dict, so we don't
            # draw external bonds twice
        for atom in self.atoms.values():
            atom.writepov(file, disp, self.color)
            for bond in atom.bonds:
                if id(bond) not in drawn:
                    drawn[id(bond)] = bond
                    bond.writepov(file, disp, self.color)
                    
        # piotr 080521
        # write POV-Ray file for the ChunkDisplayMode
        hd = get_display_mode_handler(disp)
        if hd:
            hd._writepov(self, file)
            
    def writemdl(self, alist, f, disp):
        if self.display != diDEFAULT:
            disp = self.display
        if self.hidden or disp == diINVISIBLE:
            return
        # review: use self.color somehow?
        for a in self.atoms.values(): 
            a.writemdl(alist, f, disp, self.color)

    # ==
            
    def move(self, offset):
        """
        Public method:
        translate self (a Chunk) by offset;
        do all necessary invalidations, but optimize those based on self's
        relative structure not having changed or reoriented.
        """
        # code and doc rewritten by bruce 041109.
        # The method is public but its implem is pretty private!

        # First make sure self.basepos is up to date! Otherwise
        # self._changed_basecenter_or_quat_to_move_atoms() might not be able to reconstruct it.
        # I don't think this should affect self.bbox, but in case I'm wrong,
        # do this before looking at bbox.
        self.basepos

        # Now, update bbox iff it's already present.
        if self.__dict__.has_key('bbox'):
            # bbox already present -- moving it is faster than recomputing it
            #e (though it might be faster to just delete it, if many moves
            #   will happen before we need it again)
            # TODO: refactor this to use a move method in bbox.
            if self.bbox.data:
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
        self._changed_basecenter_or_quat_to_move_atoms()

    def pivot(self, point, q):
        """
        Public method: pivot the Chunk self around point by quaternion q;
        do all necessary invalidations, but optimize those based on
        self's relative structure not having changed. See also self.rot().
        """
        # First make sure self.basepos is up to date! Otherwise
        # self._changed_basecenter_or_quat_to_move_atoms() might not be able to reconstruct it.
        self.basepos

        # Do the motion (might destructively modify basecenter and quat objects)
        r = point - self.basecenter
        self.basecenter += r - q.rot(r)
        self.quat += q

        # No good way to rotate a bbox, so just invalidate it.
        self.invalidate_attr('bbox')

        # Do all necessary invalidations and/or recomputations (except bbox),
        # treating basepos as definitive and recomputing curpos from it.
        self._changed_basecenter_or_quat_to_move_atoms()

    def rot(self, q):
        """
        Public method: rotate self around its center by quaternion q;
        do all necessary invalidations, but optimize those based on
        self's relative structure not having changed. See also self.pivot().
        """
        # bruce 041109: the center of rotation is not always self.basecenter,
        # so in general we need to pivot around self.center.
        self.pivot(self.center, q) # not basecenter!
        return

    def stretch(self, factor, point = None):
        """
        Public method: expand self by the given factor
        (keeping point fixed -- by default, point is self.center).
        
        Do all necessary invalidations, optimized for this operation.
        """
        self.basepos # recompute if necessary

        # note: use len(), since A([[0.0,0.0,0.0]]) is false!
        if not len(self.basepos):
            # precaution (probably never occurs):
            # special case for no atoms, since 
            # remaining code won't work for it,
            # since self.basepos has the wrong type then (it's []).
            # Note that no changes or invals are needed in this case.
            return

        factor = float(factor)

        if point is None:
            point = self.center # not basecenter!

        # without moving self in space, change self.basecenter to point
        # and change self.basepos to match (so the stretch around point
        # can be done in a simple way, lower down)
        self.basepos += (self.basecenter - point)
        self.basecenter = point
            # i.e. self.basecenter = self.basecenter - self.basecenter + point,
            # or self.basecenter -= (self.basecenter - point)

        # stretch self around the new self.basecenter
        self.basepos *= factor
        # (warning: the above += and *= might destructively modify basepos -- I'm not sure)

        # do necessary recomputes from the new definitive basepos,
        # and invals (including bbox, internal bonds)
        self._changed_basepos_basecenter_or_quat_to_move_atoms()

    def _changed_basepos_basecenter_or_quat_to_move_atoms(self):
        """
        like _changed_basecenter_or_quat_to_move_atoms,
        but we also might have changed basepos
        """
        # Do the needed invals, and recomputation of curpos from basepos
        # (I'm not sure if the order would need review if we revise inval rules):
        self.havelist = 0
            # (not needed for mov or rot, so not done by _changed_basecenter_or_quat_to_move_atoms)
        self.changed_attr('basepos') # invalidate whatever depends on basepos ...
        self._invalidate_internal_bonds() # ... including the internal bonds, handled separately
        self.invalidate_attr('bbox') # since not handled by following routine
        self._changed_basecenter_or_quat_to_move_atoms()
            # (misnamed -- in this case we changed basepos too)

    def _changed_basecenter_or_quat_to_move_atoms(self): #bruce 041104-041112
        """
        Call this whenever you have just changed self.basecenter and/or self.quat
        (and/or self.basepos if you call changed_attr on it yourself), and
        you want to move the Chunk self (in 3d model space)
        by changing curpos to match, assuming that
        basepos is still correct in the new local coords basecenter and quat.
           Note that basepos must already exist, since this method can't recompute
        it from curpos in the standard way, since curpos is wrong and basepos is
        correct (not a legal state except within the callers of this method).
           Also do the proper invalidations and/or incremental recomputations,
        except for self.bbox, which the caller must fix or invalidate (either
        before or after calling us). Our invalidations assume that only basecenter
        and/or quat were changed; some callers (which modify basepos) must do
        additional invalidations.
        @see: _changed_basecenter_or_quat_while_atoms_fixed (quite different)
        """
        assert self.__dict__.has_key('basepos'), \
               "internal error in _changed_basecenter_or_quat_to_move_atoms for %r" % (self,)

        if not len(self.basepos): #bruce 041119 bugfix -- use len()
            # we need this 0 atoms case (though it probably never occurs)
            # since the remaining code won't work for it,
            # since self.basepos has the wrong type then (in fact it's []);
            # note that no changes or invals are needed for 0 atoms.
            return

        # record the fact that the model will have changed by the time we return
        # [bruce 071102 -- fixes bug 2576 and perhaps analogous bugs;
        #  note that traditionally these calls have been left up to the
        #  user event handlers, so most of the Node changing methods that
        #  ought to do them probably don't do them.]
        self.changed() # Node method

        # imitate the recomputes done by _recompute_atpos
        self.atpos = self.basecenter + self.quat.rot(self.basepos) # inlines base_to_abs
        self._set_atom_posns_from_atpos( self.atpos) #bruce 060308
        # no change in atlist; no change needed in our atoms' .index attributes
        # no change here in basepos or bbox (if caller changed them, it should
        # call changed_attr itself, or it should invalidate bbox itself);
        # but changes here in whatever depends on atpos, aside from those.
        self.changed_attr('atpos', skip = ('bbox', 'basepos'))

        # we've moved one end of each external bond, so invalidate them...
        # [bruce 050516 comment (95% sure it's right): 
        #  note that we don't, and need not, inval internal bonds]
        for bond in self.externs:
            bond.setup_invalidate()
        return

    def _set_atom_posns_from_atpos(self, atpos): #bruce 060308; revised 060313
        """
        Set our atom's positions en masse from the given array, doing no chunk
        or bond invals (caller must do whichever invals are needed, which
        depends on how the positions changed). The array must be in the same
        order as self.atpos (its typical value, but we won't depend on that
        and won't access or modify self.atpos) and self.atlist (which must
        already exist).
        """
        assert self.__dict__.has_key('atlist')
        atlist = self.atlist
        assert len(atlist) == len(atpos)
        for i in xrange(len(atlist)):
            atlist[i]._f_setposn_no_chunk_or_bond_invals( atpos[i] )
        return

    def base_to_abs(self, anything): # bruce 041115
        """
        map anything (which is accepted by quat.rot() and Numeric.array's '+'
        method) from Chunk-relative coords to absolute coords; guaranteed to
        never recompute basepos/atpos or modify the mol-relative coordinate
        system it uses. Inverse of abs_to_base.
        """
        return self.basecenter + self.quat.rot( anything)

    def abs_to_base(self, anything): # bruce 041201
        """
        map anything (which is accepted by quat.unrot() and Numeric.array's
        '-' method) from absolute coords to mol-relative coords; guaranteed to
        never recompute basepos/atpos or modify the mol-relative coordinate
        system it uses. Inverse of base_to_abs.
        """
        return self.quat.unrot( anything - self.basecenter)

    def set_basecenter_and_quat(self, basecenter, quat):
        """
        Deprecated public method: 
        
        Change self's basecenter and quat to the specified values,
        as a way of moving self's atoms.
        
        It's deprecated since basecenter and quat are replaced by
        in-principle-arbitrary values every time certain recomputations are
        done after self's geometry might have changed, but this method is only
        useful if the caller knows what they are, and computes the new ones it
        wants relative to what they are, which in practice means the caller
        must be able to prevent modifications to self during an entire period
        when it wants to be able to call this method repeatedly on self. So
        it's much better to use self.pivot instead (or some combo of move,
        rot, and pivot methods).
        """
        # [written by bruce for extrude; moved into class Chunk by bruce 041104]
        # modified from mol.move and mol.rot as of 041015 night
        self.basepos # recompute basepos if it's currently invalid
        # make sure mol owns its new basecenter and quat,
        # since it might destructively modify them later!
        self.basecenter = V(0,0,0) + basecenter
        self.quat = Q(1,0,0,0) + quat 
            # review: +quat might be correct and faster... don't know; doesn't matter much
        self.bbox = None
        del self.bbox #e could optimize if quat is not changing
        self._changed_basecenter_or_quat_to_move_atoms()

    def getaxis(self):
        """
        Return self's axis, in absolute coordinates.
        
        @note: several Nodes have this method, but it's not (yet) formally
               a Node API method.
        @see: self.axis (in self-relative coordinates)
        """
        return self.quat.rot(self.axis)

    def setcolor(self, color, repaint_in_MT = True):
        """
        Change self's color to the specified color. A color of None
        means self's atoms will be drawn with their element colors.

        @param color: None, or a standard color 3-tuple.

        @param repaint_in_MT: True by default; callers can optimize by passing
                              False if they know self is too new to have ever
                              been drawn into any model tree widget.
        """
        #bruce 080507 added repaint_in_MT option
        # color is None or a 3-tuple; it matters that the 3-tuple is never boolean False,
        # so don't use a Numeric array! As a precaution, enforce this now. [bruce 050505]
        if color is not None:
            r,g,b = color
            color = r,g,b
        self.color = color
            # warning: some callers (ChunkProp.py) first replace self.color, 
            # then call us to bless the new value. Therefore the following is
            # needed even if self.color didn't change here. [bruce 050505 comment]
        self.havelist = 0
        self.changed()
        if repaint_in_MT and pref_show_node_color_in_MT():
            #bruce 080507, mainly for testing new method repaint_some_nodes
            self.assy.win.mt.repaint_some_nodes([self])
        return

    def setDisplayStyle(self, disp): #bruce 080910 renamed from setDisplay
        """
        Set self's display style.
        """
        if self.display == disp:
            #bruce 080305 optimization; looks safe after review of all calls;
            # important (due to avoiding inlined changeapp and display list
            # remake) if user selects several chunks and changes them all
            # at once, and some are already set to disp. Also done in class Atom.
            return

        self.display = disp
        # inlined self.changeapp(1):
        self.havelist = 0
        self.haveradii = 0
        self.changed()
        return

    def getDisplayStyle(self):
        """
        Return the display style setting on self. 
        
        Note that this might be diDEFAULT -- that setting makes self get drawn
        as if it had a display style inherited from self's graphical environment
        (for now, its glpane), but an inherited style is never returned
        from this method (unless it also happens to be explicitly set on self).
        
        (Use get_dispdef to obtain the display style that will be used to draw
        self, which might be set on self or inherited from self's environment.)
        
        @note: the display style used to draw self can differ from  
        self.display not only if that's diDEFAULT, but due to some special cases 
        in get_dispdef based on what kind of chunk self is.
        
        @see: L{get_dispdef()}
        """
        return self.display
    
    def show_invisible_atoms(self): # by Mark ### TODO: RENAME
        """
        Reset the display style of each invisible (diINVISIBLE) atom 
        in self to diDEFAULT, thus making it visible again.
        
        @return: number of invisible atoms in self (which are all made visible)
        """
        n = 0
        for a in self.atoms.itervalues():
            if a.display == diINVISIBLE:
                a.setDisplayStyle(diDEFAULT)
                n += 1
        return n

    def set_atoms_display(self, display):
        """
        Change the display style setting for all atoms in self to the one
        specified by 'display'.
        
        @param display: display style setting to apply to all atoms in self
                        (can be diDEFAULT or diINVISIBLE or various other values)
                        
        @return: number of atoms in self whose display style setting changed
        """
        n = 0
        for a in self.atoms.itervalues():
            if a.display != display:
                a.setDisplayStyle(display)
                    # REVIEW: does this always succeed? 
                    # If not, should we increment n then? [bruce 090108 questions]
                n += 1
        return n

    def changeapp(self, atoms):
        """
        Call this when you've changed the graphical appearance of self.
        
        (But there is no need to call it if only self's external bonds 
         look different, or (at present) just for a change to self.picked.)
        
        @param atoms: (required) True means that not only the graphical
                      appearance of self,  but also specifically the set of 
                      atoms of self or their atomic radii (for purposes of 
                      hover-highlighting(?) or selection), have changed.
        @type atoms: boolean
        
        @note: changeapp does not itself call self.assy.changed(),
               since that is not always correct to do (e.g., selecting an atom
               should call changeapp(), but not assy.changed(), on
               atom.molecule).
        
        @see: changed_selected_atoms
        """ 
        ### REVIEW and document: need this be called when changing self's color?
        self.havelist = 0
        if atoms: #bruce 041207 added this arg and its effect
            self.haveradii = 0 # invalidate self.sel_radii_squared
            # (using self.invalidate_attr would be too slow)
        #bruce 050804 new feature
        # (related to graphics prefs updating,
        # probably more generally useful):
        # REVIEW: do some inlines of changeapp need to do this too?
        # If they did, would that catch the redraws that currently
        # only Qt knows we need to do? [bruce 080305 question]
        glpane = self.glpane 
            # the last glpane that drew this chunk, or None if it was never
            # drawn (if more than one can ever draw it at once, this code
            # needs to be revised to scan them all ##k)
        if glpane is not None:
            try:
                flag = glpane.wants_gl_update
            except AttributeError:
                # this will happen for ThumbViews, until they are fixed to use
                # this system so they get updated when graphics prefs change
                pass
            else:
                if flag:
                    glpane.wants_gl_update_was_True() # sets it False and does gl_update
            pass
        return

    def changed_selected_atoms(self): #bruce 090119
        """
        Invalidate whatever is needed due to something having
        changed the selectness of some of self's atoms.
        
        @note: this is a low-level method, called by Atom.pick/unpick etc,
               so most new code need never call this.
        """
        self.changeapp(1) 
            # * for atom appearance (since selected atom wireframes are part of
            #   the main chunk display list)
            # * for selatom radius (affected by selectedness for invisible atoms)
        self.changed_selection() # reports an undoable change to selection
        
    def natoms(self): #bruce 060215
        """
        Return number of atoms (real atoms or bondpoints) in self.
        """
        return len(self.atoms)
    
    def getToolTipInfo(self):
        """
        Return the tooltip string for this chunk
        """
        info = self._getToolTipInfo_Dna()
        if info:
            return info # in future, we might combine it with other info
        return ""
        
    def getinfo(self): # mark 2004-10-14
        """
        Return information about the selected chunk for the msgbar
        """
        if self is self.assy.ppm: 
            return

        ele2Num = {}

        # Determine the number of element types in this Chunk.
        for a in self.atoms.values():
            if not ele2Num.has_key(a.element.symbol):
                ele2Num[a.element.symbol] = 1 # New element found
            else: 
                ele2Num[a.element.symbol] += 1 # Increment element

        # String construction for each element to be displayed.
        natoms = self.natoms() # number of atoms in the chunk
        nsinglets = 0
        einfo = ""

        for item in ele2Num.iteritems():
            if item[0] == "X":  # Singlet
                nsinglets = int(item[1])
                continue
            else: 
                eleStr = "[" + item[0] + ": " + str(item[1]) + "] "
            einfo += eleStr

        if nsinglets:
            eleStr = "[Open bonds: " + str(nsinglets) + "]"
            einfo += eleStr

        natoms -= nsinglets # compute number of real atoms in this chunk

        minfo =  "Chunk Name: [" + str (self.name) + "]     Total Atoms: " + str(natoms) + " " + einfo

        # set ppm to self for next mol picked.
        self.assy.ppm = self

        return minfo

    def getstatistics(self, stats):
        """
        Adds the current chunk, including number of atoms 
        and singlets, to part stats.
        """
        stats.nchunks += 1
        stats.natoms += self.natoms()
        for a in self.atoms.itervalues():
            if a.element.symbol == "X": 
                stats.nsinglets += 1

    def pickatoms(self): # mark 060211. 
        """
        Pick the atoms of self not already picked (selected).
        Return the number of newly picked atoms.
        [overrides Node method]
        """
        # todo: Could use a complementary unpickatoms() method. [mark 060211]
        # [fyi, that doesn't refer to the one in ops_select --bruce]
        self.assy.permit_pick_atoms()
        npicked = 0
        for a in self.atoms.itervalues():
            if not a.is_singlet():
                if not a.picked:
                    a.pick()
                    if a.picked: 
                        # in case not picked due to selection filter
                        npicked += 1
        return npicked

    def pick(self):
        """
        select self

        [extends Node method]
        """
        if not self.picked:
            if self.assy is not None:
                self.assy.permit_pick_parts()
                #bruce 050125 added this... hope it's ok! ###k ###@@@
                # (might not be needed for other kinds of leaf nodes... 
                #  not sure. [bruce 050131])
            _superclass.pick(self)
            #bruce 050308 comment: _superclass.pick (Node.pick) has ensured
            #that we're in the current selection group, so it's correct to
            #append to selmols, *unless* we recompute it now and get a version
            #which already contains self. So, we'll maintain it iff it already
            #exists. Let the Part figure out how best to do this. 
            # [bruce 060130 cleaned this up, should be equivalent]
            if self.part:
                self.part.selmols_append(self)
            
            self._selectedness_drawing_effects(True)
            pass
        return

    def unpick(self):
        """
        unselect self

        [extends Node method]
        """
        if self.picked:
            _superclass.unpick(self)
            if self.part:
                self.part.selmols_remove(self)
            self._selectedness_drawing_effects(False)
            pass
        return

    def getAxis_of_self_or_eligible_parent_node(self, atomAtVectorOrigin = None):
        """
        Return the axis of a parent node such as a DnaSegment or a Nanotube 
        Segment or the dna segment of a DnaStrand. If one doesn't exist, 
        return self's axis. Also return the node from which the returned
        axis was found.
        
        @param atomAtVectorOrigin: If the atom at vector origin is specified, 
            the method will try to return the axis vector with the vector
            start point at this atom's center. [REVIEW: What does this mean??]
        @type atomAtVectorOrigin: B{Atom}
        
        @return: (axis, node used to get that axis)
        """
        #@TODO: refactor this. Method written just before FNANO08 for a critical
        #NFR. (this code is not a part of Rattlesnake rc2)
        #- Ninad 2008-04-17
        
        #bruce 090115 partly refactored it, but more would be better.
        # REVIEW: I don't understand any meaning in what the docstring says about
        # atomAtVectorOrigin. What does it actually do? [bruce 090115 comment]
        
        axis, node = self._getAxis_of_self_or_eligible_parent_node_Dna(
            atomAtVectorOrigin = atomAtVectorOrigin )
        if axis is not None:
            return axis, node

        nanotube = self.parent_node_of_class(self.assy.NanotubeSegment)
        if nanotube:
            axisVector = nanotube.getAxisVector(atomAtVectorOrigin = atomAtVectorOrigin)
            if axisVector is not None:
                return axisVector, nanotube

        #If no eligible parent node with an axis is found, return self's axis.
        return self.getaxis(), self


    def is_glpane_content_itself(self): #bruce 080319
        """
        @see: For documentation, see Node method docstring.

        @rtype: boolean

        [overrides Node method]
        """
        # Note: this method is misnamed, since it's not about graphics drawing
        # or the GLPane as an implementation of that; it's a selection-
        # semantics method. (See comment on Node def for more info.) So it
        # should not be moved to Chunk_drawing_methods. [bruce 090123 comment]
        return True

    def kill(self):
        """
        (Public method)
        Kill a Chunk: unpick it, break its external bonds, kill its atoms
        (which should kill any jigs attached only to this mol),
        remove it from its group (if any) and from its assembly (if any);
        make it forget its group and assembly.
        It's legal to kill a mol twice, and common now that emptying a mol
        of all atoms kills it automatically; redundant kills have no effect.
        It's probably legal to reuse a killed mol (if it's added to a new
        assy -- there's no method for this), but this has never been tested.

        [extends Node method]
        """
        self._destroy_bonded_chunks()
        ## print "fyi debug: mol.kill on %r" % self
        # Bruce 041116 revised docstring, made redundant kills noticed
        # and fully legal, and made kill forget about dad and assy.
        # Note that _nullMol might be killed every so often.
        # (caller no longer needs to set externs to [] when there are no atoms)
        if self is _nullMol:
            return
        # all the following must be ok for an already-killed Chunk!
        self._f_prekill() #bruce 060327, needed here even though _superclass.kill might do it too
        ## self.unpick()
            #bruce 050214 comment [superseded, see below]: keep doing unpick
            # here, even though _superclass.kill now does it too.
            #update, bruce 080310: doing this here looks like a bug if self.dad
            # is selected but not being killed -- a situation that never arises
            # from a user op of "kill selection", but that might happen when the
            # dna updater kills a chunk, e.g. due to merging it. So, don't do it
            # here. Superclass method avoids the issue by doing it only after
            # self.dad becomes None. If this doesn't work, we'll need to define
            # and call here self._unpick_during_kill rather than just self.kill.
        for b in self.externs[:]: #bruce 050214 copy list as a precaution
            b.bust()
        self.externs = [] #bruce 041029 precaution against repeated kills

        #10/28/04, delete all atoms, so jigs attached can be deleted when no atoms
        #  attaching the jig . Huaicai
        for a in self.atoms.values():
            a.kill()
            # WARNING: this will recursively kill self (when its last atom is
            # killed as this loop ends, or perhaps earlier if a bondpoint comes
            # last in the values list)! Should be ok,
            # though I ought to rewrite it so that if that does happen here,
            # I don't redo everything and have to worry whether that's safe.
            # [bruce 050214 comment] 
            # [this would also serve to bust the extern bonds, but it seems safer
            #  to do that explicitly and to do it first -- bruce 041109 comment]
        #bruce 041029 precautions:
        if self.atoms:
            print "fyi: bug (ignored): %r mol.kill retains killed atoms %r" % (self, self.atoms)
        self.atoms = {}
        self.invalidate_attr('atlist') # probably not needed; covers atpos
            # and basepos too, due to rules; externs were correctly set to []
        if self.assy:
            # bruce 050308 for assy/part split: [bruce 051227 removing obsolete code]
            # let the Part handle it
            if self.part:
                self.part.remove(self)
                assert self.part is None
        _superclass.kill(self) #bruce 050214 moved this here, made it unconditional
        self._kill_displists()
        return # from Chunk.kill

    def _f_set_will_kill(self, val): #bruce 060327 in Chunk
        """
        [extends private superclass method; see its docstring for details]
        """
        _superclass._f_set_will_kill( self, val)
        for a in self.atoms.itervalues():
            a._f_will_kill = val # inlined a._f_prekill(val), for speed
            ##e want to do it on their bonds too??
        return

    # New method for finding atoms or singlets under mouse. Helps fix bug 235
    # and many other bugs (mostly never reported). [bruce 041214]
    # (We should use this in extrude, too! #e)

    def findAtomUnderMouse( self, point, matrix, **kws):
        """
        [Public method, but for a more convenient interface see its caller:]
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
        # See comments in _findAtomUnderMouse_Numeric_stuff for more details.
        # (Optimize for the slowest case: lots of atoms, most fail lineofsight
        # test, but a lot still pass it since we have a thick Chunk; do
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
            radii_2[seli] = selatom.highlighting_radius() ** 2
            # (note: selatom is drawn even if "invisible")
            if unpatched_seli_radius2 > 0.0:
                kws['alt_radii'] = [(seli, unpatched_seli_radius2)]
        try:
            # note: kws here might include alt_radii as produced above
            res = self._findAtomUnderMouse_Numeric_stuff( v, r_xy_2, radii_2, **kws)
        except:
            print_compact_traceback("bug in _findAtomUnderMouse_Numeric_stuff: ")
            res = []
        if unpatched_seli_radius2 is not None:
            radii_2[seli] = unpatched_seli_radius2
        return res # from findAtomUnderMouse

    def _findAtomUnderMouse_Numeric_stuff(self, v, r_xy_2, radii_2,
                                          far_cutoff = None, 
                                          near_cutoff = None, 
                                          alt_radii = ()
                                         ):
        """
        private helper routine for findAtomUnderMouse
        """
        ## removed support for backs_ok, since atom backs are not drawn
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
        thicks_p1 = Numeric.sqrt( radii_2_p1 - r_xy_2_p1 )
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
                        thick_0 = Numeric.sqrt( radii_2_0 - r_xy_2_0 )
                        zz = v[ind][2] + thick_0
                        if zz < near_cutoff:
                            pairs.append( (zz, ind) )

        if not pairs:
            return []
        pairs.sort() # the one we want is at the end (highest z == closest)
        (closest_z, closest_z_ind) = pairs[-1]

        # We've narrowed it down to a single candidate, which passes near_cutoff!
        # Does it pass far_cutoff?
        if far_cutoff is not None:
            if closest_z < far_cutoff:
                return []

        atom = self.atlist[ closest_z_ind ]

        return [(closest_z, atom)] # from _findAtomUnderMouse_Numeric_stuff

    # self.sel_radii_squared is not a real attribute, since invalling it
    # would be too slow. Instead we have these methods:

    def get_sel_radii_squared(self):
        #bruce 050419 fix bug 550 by fancifying haveradii
        # in the same way as for havelist (see 'bruce 050415').
        # Note: this must also be invalidated when one atom's display mode changes,
        # and it is, by atom.setDisplayStyle calling changeapp(1) on its chunk.
        disp = self.get_dispdef() ##e should caller pass this instead?
        eltprefs = PeriodicTable.rvdw_change_counter 
            # (color changes don't matter for this, unlike for havelist)
        radiusprefs = Atom.selradius_prefs_values() 
            #bruce 060317 -- include this in the tuple below, to fix bug 1639
        if self.haveradii != (disp, eltprefs, radiusprefs): # value must agree with set, below
            # don't have them, or have them for wrong display mode, or for
            # wrong element-radius prefs
            try:
                res = self.compute_sel_radii_squared()
            except:
                print_compact_traceback("bug in %r.compute_sel_radii_squared(), using []: " % self)
                res = [] #e len(self.atoms) copies of something would be better
            self.sel_radii_squared_private = res
            self.haveradii = (disp, eltprefs, radiusprefs)
        return self.sel_radii_squared_private

    def compute_sel_radii_squared(self):
        lis = map( lambda atom: atom.selradius_squared(), self.atlist )
        if not lis:
            return lis
        else:
            return A( lis )
        pass
    
    def nearSinglets(self, point, radius): # todo: rename
        """
        return the bondpoints in the given sphere (point, radius),
        sorted by increasing distance from point
        """
        # note: only used in AtomTypeDepositionTool (Build Atoms mode)
        # (note: findHandles_exact in handles.py may be related code)
        if not self.singlets:
            return []
        singlpos = self.singlpos # do this in advance, to help with debugging
        v = singlpos - point
        try:
            #bruce 051129 add try/except and printout to help debug bug 829
            r = Numeric.sqrt(v[:,0]**2 + v[:,1]**2 + v[:,2]**2) # this line had OverflowError in bug 829
            p = (r <= radius)
            i = argsort(compress(p, r))
            return take(compress(p, self.singlets), i)
        except:
            print_compact_traceback("exception in nearSinglets (data printed below): ")
            print "if that was bug 829, this data (point, singlpos, v) might be relevant:"
            print "point =", point
            print "singlpos =", singlpos
            print "v =", v
            return [] # safe value for caller

    # == copy methods (extended/revised by bruce 050524-26)

    def will_copy_if_selected(self, sel, realCopy):
        return True

    def will_partly_copy_due_to_selatoms(self, sel):
        assert 0, "should never be called, since a chunk does not " \
                  "*refer* to selatoms, or appear in atom.jigs"
        return True # but if it ever is called, answer should be true

    def _copy_optional_attrs_to(self, numol):
        #bruce 090112 split this out of two methods.
        # Note: we don't put these in copyable_attrs, since
        # copy_copyable_attrs_to wasted RAM when they have their 
        # default values (and perhaps for other reasons??).
        # Review: add a method like this to Node API, to be called
        # inside default def of copy_copyable_attrs_to??
        if self.chunkHasOverlayText:
            numol.chunkHasOverlayText = True
        if self.showOverlayText:
            numol.showOverlayText = True
        if self._colorfunc is not None: #bruce 060411 added condition
            numol._colorfunc = self._colorfunc 
        if self._dispfunc is not None:
            numol._dispfunc = self._dispfunc
        # future: also copy user-specified axis, center, etc, if we have those
        # (but see existing copy code for self.user_specified_center)
        return
        
    def _copy_empty_shell_in_mapping(self, mapping): 
        """
        [private method to help the public copy methods, all of which
         start with this except the deprecated mol.copy]

        Copy this chunk's name (w/o change), properties, etc,
        but not any of its atoms
        (caller will presumably copy some or all of them separately).
        Don't copy hotspot.
        New chunk is in mapping.assy (NOT necessarily the same as self.assy)
        but not in any Group or Part.
        #doc: invalidation status of resulting chunk?
        Update orig->copy correspondence in mapping (for self, and in future
        for any copyable subobject which gets copied by this method, if any
        does).
        Never refuses. Returns copy (a new chunk with no atoms).
        Ok to assume self has never yet been copied.
        """
        #bruce 070430 revised to honor mapping.assy
        numol = self.__class__(mapping.assy, self.name)
            #bruce 080316 Chunk -> self.__class__ (part of fixing this for Extrude of DnaGroup)
        self.copy_copyable_attrs_to(numol) 
            # copies .name (redundantly), .hidden, .display, .color...
        self._copy_optional_attrs_to(numol)
        mapping.record_copy(self, numol)
        return numol

    def copy_full_in_mapping(self, mapping): # in class Chunk 
        """
        #doc;
        overrides Node method;
        only some atom copies get recorded in mapping (if we think it might need them)
        """
        # bruce 050526; 060308 major rewrite
        numol = self._copy_empty_shell_in_mapping( mapping)
        # now copy the atoms, all at once (including all their existing 
        # singlets, even though those might get revised)
        # note: the following code is very similar to 
        # copy_in_mapping_with_specified_atoms, but not identical.
        pairlis = []
        ndix = {} # maps old-atom key to corresponding new atom
        nuatoms = {}
        for a in self.atlist: 
            # note: self.atlist is now in order of atom.key;
            # it might get recomputed right now (along with atpos & basepos if so)
            na = a.copy()
            # inlined addatom, optimized (maybe put this in a new variant of obs copy_for_mol_copy?)
            na.molecule = numol # no need for _changed_parent_Atoms[na.key] = na #bruce 060322
            nuatoms[na.key] = na
            pairlis.append((a, na))
            ndix[a.key] = na
        numol.invalidate_atom_lists()
        numol.atoms = nuatoms
        # note: we don't bother copying atlist, atpos, basepos,
        # since it's hard to do correctly (e.g. not copying everything
        # which depends on them would cause inval bugs), and it's wasted work
        # for callers which plan to move all the atoms after 
        # the copy
        self._copy_atoms_handle_bonds_jigs( pairlis, ndix, mapping)
        # note: no way to handle hotspot yet, since how to do that might depend on whether
        # extern bonds are broken... so let's copy an explicit one, and tell the mapping
        # if we have an implicit one... or, register a cleanup function with the mapping.
        copied_hotspot = self.hotspot 
            # might be None (this uses __getattr__ to ensure the stored one is valid)
        if copied_hotspot is not None:
            numol.set_hotspot( ndix[copied_hotspot.key])
        elif len(self.singlets) == 1: 
            #e someday it might also work if there are two singlets on the same base atom!
            # we have an implicit but unambiguous hotspot:
            # might need to make it explicit in the copy [bruce 041123, revised 050524]
            copy_of_hotspot = ndix[self.singlets[0].key]
            mapping.do_at_end( lambda ch = copy_of_hotspot, numol = numol:
                               numol._f_preserve_implicit_hotspot(ch) )
        return numol # from copy_full_in_mapping

    def _copy_atoms_handle_bonds_jigs(self, pairlis, ndix, mapping):
        """
        [private helper for some copy methods]
        Given some copied atoms (in a private format in pairlis and ndix),
        ensure their bonds and jigs will be taken care of.
        """
        del self # doesn't use self
        origid_to_copy = mapping.origid_to_copy
        extern_atoms_bonds = mapping.extern_atoms_bonds
            # maybe: could be integrated with mapping.do_at_end,
            # but it's probably better not to, so as to specialize it for speed;
            # even so, could clean this up to bond externs as soon as 2nd atom seen
            # (which might be more efficient, though that doesn't matter much
            #  since externs should not be too frequent); 
            # could do all this in a Bond method
        for (a, na) in pairlis:
            if a.jigs: 
                # a->na mapping might be needed if those jigs are copied,
                # or confer properties on atom a
                origid_to_copy[id(a)] = na # inlines mapping.record_copy for speed
            for b in a.bonds:
                a2key = b.other(a).key
                if a2key in ndix:
                    # internal bond - make the analogous one 
                    # [this should include all bonds to singlets]
                    #bruce 050524 changes: don't do it twice for the same bond;
                    # and use bond_copied_atoms to copy bond state (e.g. 
                    # bond-order policy and estimate) from old bond.
                    # [note: also done in copy_single_chunk]
                    if a.key < a2key:
                        # arbitrary condition which is true for exactly one
                        # ordering of the atoms; note both keys are for
                        # original atoms (it would also work if both were from
                        # copied atoms, but not if they were mixed)
                        bond_copied_atoms(na, ndix[a2key], b, a)
                else:
                    # external bond [or at least outside of atoms in
                    # pairlis/ndix] -- caller will handle it when all chunks
                    # and individual atoms have been copied (copy it if it 
                    # appears here twice, or break it if once)
                    # [note: similar code will be in atom.copy_in_mapping] 
                    extern_atoms_bonds.append( (a,b) ) 
                        # it's ok if this list has several entries for one 'a'
                    origid_to_copy[id(a)] = na
                        # a->na mapping will be needed outside this method,
                        # to copy or break this bond
                pass
            pass
        return # from _copy_atoms_handle_bonds_jigs

    def copy_in_mapping_with_specified_atoms(self, mapping, atoms): #bruce 050524-050526
        """
        Copy yourself in this mapping (for the first and only time),
        but with only some of your atoms (and all their singlets).
        [#e hotspot? fix later if needed, hopefully by replacing that concept
         with a jig (see comment below for ideas).]
        """
        numol = self._copy_empty_shell_in_mapping( mapping)
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
        ##e do anything about hotspot? easiest: if we copy it (explicit or 
        # implicit) or its base atom, put them in mapping,
        # and register some other func (than the one copy_in_mapping does) 
        # to fix it up at the end.
        # Could do this uniformly in _copy_empty_shell_in_mapping, 
        # and here just be sure to tell mapping.record_copy.
        #
        # (##e But really we ought to simplify all this code by just 
        #  replacing the hotspot concept with a "bonding-point jig" 
        #  or perhaps a bond property. That might be less work! And more useful!
        #  And then one chunk could have several hotspots with different
        #  pastable names and paster-jigs!
        #  And the paster-jig could refer to real atoms to be merged
        #  with what you paste it on, not only singlets!
        #  Or to terminating groups (like H) to pop off if you use 
        #  that pasting point (but not if you use some other one).
        #  Maybe even to terminating groups connected to base at more
        #  than one place, so you could make multiple bonds at once!
        #  Or instead of a terminating group, it could include a pattern
        #  of what it should suggest adding itself to!
        #  Even for one bond, this could help it orient 
        #  the addition as intended, spatially!)
        return numol

    def _f_preserve_implicit_hotspot( self, hotspot): 
        #bruce 050524 #e could also take base-atom arg to use as last resort
        if len(self.singlets) > 1 and self.hotspot is None:
            self.set_hotspot( hotspot, silently_fix_if_invalid = True) 
                # this checks everything before setting it; if invalid, silent noop

    # == 

##    def copy(self, dad = None, offset = V(0,0,0), cauterize = 1): #bruce 080314
##        """
##        Public method. DEPRECATED, see code comments for details.
##        Deprecated alias for copy_single_chunk (also deprecated but still in use).
##        """
##        cs = compact_stack("\n*** print once: called deprecated Chunk.copy from: ")
##        if not env.seen_before(cs):
##            print cs
##        return self.copy_single_chunk( dad, offset, cauterize)

    def copy_single_chunk(self, dad = None, offset = V(0,0,0), cauterize = 1):
        """
        Public method. DEPRECATED, see code comments for details.

        Copy the Chunk self to a new Chunk.
        Offset tells where it will go relative to the original.
        Unless cauterize = 0, replace bonds out of self (to atoms in other Chunks)
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
        should use one of addmol or addchild or addsibling to place the mol somewhere.
        Not sure what happens now; so I made addchild notice the setting of
        dad but lack of being in dad's members list, and tolerate it but complain
        when atom_debug. This should all be cleaned up sometime soon. ###@@@
        """
        #bruce 080314 renamed, added even more deprecated alias method under
        # the prior name (copy) (see also Node.copy, NamedView.copy), fixed all uses
        # to call the new name. The uses are mainly in pasting and setHotSpot.
        # It's almost certain that Extrude no longer calls this.
        # The new name includes "single" to emphasize the reason this method is
        # inherently defective and therefore deprecated -- that in copying only
        # one chunk, unaware of a larger set of things being copied, it can't
        # help but break its inter-chunk bonds.
        #
        # older comments:
        # 
        # This is the old copy method -- should remove ASAP but might still be needed
        # for awhile (as of 050526)... actually we'll keep it for awhile,
        # since it's used in many places and ways in depositMode and
        # extrudeMode... it'd be nice to rewrite it to call general copier...
        #
        # NOTE: to copy several chunks and not break interchunk bonds, don't use this --
        # use either copied_nodes_for_DND or copy_nodes_in_order as appropriate
        # (or other related routines we might add near them in the future),
        # then do a few more things to fix up their output -- see their existing calls
        # for details. [bruce 070412/070525 comment]
        #
        #bruce 060308 major rewrite, and no longer permit args to vary from defaults

        assert cauterize == 1
        assert same_vals( offset, V(0,0,0) )
        assert dad is None

        # bruce added cauterize feature 041116, and its hotspot behavior 041123.
        # Without hotspot feature, Build mode pasting could have an exception.
        ##print "fyi debug: mol.copy on %r" % self
        # bruce 041116: note: callers seem to be mainly in model tree copy ops
        # and in depositMode.
        # [where do they call addmol? why did extrude's copies break on 041116?]

        pairlis = []
        ndix = {}
        newname = mol_copy_name(self.name, self.assy)
        #bruce 041124 added "-copy<n>" (or renumbered it, if already in name),
        # similar to Ninad's suggestion for improving bug 163's status message
        # by making it less misleading.
        numol = Chunk(self.assy, "fakename") # name is set below
        #bruce 050531 kluges to fix bug 660, until we replace or rewrite this method
        # using one of the newer "copy" methods
        self.copy_copyable_attrs_to(numol)
            # copies .name (redundantly), .hidden, .display, .color...
            # and sets .prior_part, which is what should fix bug 660
        self._copy_optional_attrs_to(numol)
        numol.name = newname
        #end 050531 kluges
        nuatoms = {}
        for a in self.atlist: 
            # 060308 changed similarly to copy_full_in_mapping (shares some code with it)
            na = a.copy()
            na.molecule = numol # no need for _changed_parent_Atoms[na.key] = na #bruce 060322
            nuatoms[na.key] = na
            pairlis.append((a, na))
            ndix[a.key] = na
        numol.invalidate_atom_lists()
        numol.atoms = nuatoms
        extern_atoms_bonds = []
        for (a, na) in pairlis:
            for b in a.bonds:
                a2key = b.other(a).key
                if a2key in ndix:
                    # internal bond - make the analogous one
                    # (this should include all preexisting bonds to singlets)
                    #bruce 050715 bugfix (copied from 050524 changes to another 
                    # routine; also done below for extern_atoms_bonds):
                    # don't do it twice for the same bond 
                    # (needed by new faster bonding methods),
                    # and use bond_copied_atoms to copy bond state 
                    # (e.g. bond-order policy and estimate) from old bond.
                    if a.key < a2key:
                        # arbitrary condition which is true for exactly
                        # one ordering of the atoms;
                        # note both keys are for original atoms 
                        # (it would also work if both were from
                        #  copied atoms, but not if they were mixed)
                        bond_copied_atoms(na, ndix[a2key], b, a)
                else:
                    # external bond - after loop done, make a singlet in the copy
                    extern_atoms_bonds.append( (a,b) ) # ok if several times for one 'a'
        ## if extern_atoms_bonds:
        ##     print "fyi: mol.copy didn't copy %d extern bonds..." % len(extern_atoms_bonds)
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
            for a, b in extern_atoms_bonds:
                # compare to code in Bond.unbond():
                x = Atom('X', b.ubp(a) + offset, numol)
                na = ndix[a.key]
                #bruce 050715 bugfix: also copy the bond-type (two places in this routine)
                bond_copied_atoms( na, x, b, a)
        if copied_hotspot is not None:
            numol.set_hotspot( ndix[copied_hotspot.key])
        # future: also copy (but translate by offset) user-specified 
        # axis, center, etc, if we ever have those
        ## if self.user_specified_center is not None: #bruce 050516 bugfix: 'is not None'
        ##     numol.user_specified_center = self.user_specified_center + offset
        numol.setDisplayStyle(self.display) 
            # REVIEW: why is this not redundant? (or is it?) [bruce 090112 question]
        numol.dad = dad
        if dad and debug_flags.atom_debug: #bruce 050215
            print "atom_debug: mol.copy got an explicit dad (this is deprecated):", dad
        return numol
    
    # ==

    def Passivate(self, p = False):
        """
        [Public method, does all needed invalidations:]
        Passivate the selected atoms in this chunk, or all its atoms if p = True.
        This transmutes real atoms to match their number of real bonds,
        and (whether or not that succeeds) removes all their open bonds.
        """
        # todo: move this into the operations code for its caller
        for a in self.atoms.values():
            if p or a.picked: 
                a.Passivate()

    def Hydrogenate(self):
        """
        [Public method, does all needed invalidations:]
        Add hydrogen to all unfilled bond sites on carbon
        atoms assuming they are in a diamond lattice.
        For hilariously incorrect results, use on graphite.
        @warning: can create overlapping H atoms on diamond.
        """
        # review: probably docstring is wrong in implying this
        # only affects Carbon
        # todo: move this into the operations code for its caller
        count = 0
        for a in self.atoms.values():
            count += a.Hydrogenate()
        return count
    
    def Dehydrogenate(self):
        """
        [Public method, does all needed invalidations:]
        Remove hydrogen atoms from this chunk.
        @return: number of atoms removed.
        """
        # todo: move this into the operations code for its caller
        count = 0
        for a in self.atoms.values():
            count += a.Dehydrogenate() 
                # review: bug if done to H-H?
        return count
    
    # ==
    
    def __str__(self):
        # bruce 041124 revised this; again, 060411 
        # (can I just zap it so __repr__ is used?? Try this after A7. ##e)
        return "<%s %r>" % (self.__class__.__name__, self.name)

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
        classname = self.__class__.__name__ # not always Chunk!
        if self.assy is not None:
            return "<%s %s (%d atoms) at %#x>" % (classname, name, len(self.atoms), id(self))
        else:
            return "<%s %s, KILLED (no assy), at %#x of %d atoms>" % \
                   (classname, name, id(self), len(self.atoms)) # note other order
        pass

    def merge(self, mol):
        """
        merge the given Chunk into this one.
        """
        if mol is self: # Can't merge self. Mark 2007-10-21
            return
        # rewritten by bruce 041117 for speed (removing invals and asserts);
        # effectively inlines hopmol and its delatom and addatom;
        # no need to find and hop singlet neighbors of atoms in mol
        # since they were already in mol anyway.
        for atom in mol.atoms.values():
            # should be a method in atom:
            atom.index = -1
            atom.molecule = self
            _changed_parent_Atoms[atom.key] = atom #bruce 060322
            #bruce 050516: changing atom.molecule is now enough in itself
            # to invalidate atom's bonds, since their validity now depends on
            # a counter stored in (and unique to) atom.molecule having
            # a specific stored value; in the new Chunk (self) this will
            # have a different value. So I can remove the following code:
##            for bond in atom.bonds:
##                bond.setup_invalidate()
        self.atoms.update(mol.atoms)
        self.invalidate_atom_lists()
        # be safe, since we just stole all mol's atoms:
        mol.atoms = {}
        mol.invalidate_atom_lists()
        mol.kill()
        return # from merge

    def overlapping_chunk(self, chunk, tol = 0.0):
        """
        Returns True if any atom of chunk is within the bounding sphere of
        this chunk's bbox. Otherwise, returns False.

        @param tol: (optional) an additional distance to be added to the
                    radius of the bounding sphere in the check.
        @type tol: float
        """
        if vlen (self.bbox.center() - chunk.bbox.center()) > \
           self.bbox.scale() + chunk.bbox.scale() + tol:
            return False
        else:
            return True

    def overlapping_atom(self, atom, tol = 0.0):
        """
        Returns True if atom is within the bounding sphere of this chunk's bbox. 
        Otherwise, returns False.

        @param tol: (optional) an additional distance to be added to the
                    radius of the bounding sphere in the check.
        @type tol: float
        """
        if vlen (atom.posn() - self.bbox.center()) > self.bbox.scale() + tol:
            return False
        else:
            return True

    def isProteinChunk(self):
        """
        Returns True if the chunk is a protein object.
        """
        if self.protein is None:
            return False
        else:
            # This only adds the icon to the PM_SelectionListWidget.
            # To add the protein icon for the model tree, the node_icon() 
            # method was modified. --Mark 2008-12-16.
            if self.hidden:
                self.iconPath = "ui/modeltree/Protein-hide.png"
            else:
                self.iconPath = "ui/modeltree/Protein.png"
            return True
        
    pass # end of class Chunk

# ==

# The chunk _nullMol is never part of an assembly, but serves as the chunk
# for atoms removed from other chunks (when killed, or before being added to new
# chunks), so it can absorb invalidations which certain dubious code
# (like depositMode via selatom) sends to killed atoms, by operating on them
# (or invalidating bonds containing them) even after they're killed.

# Initing _nullMol here caused a bus error; don't know why (class Node not ready??)
# So we do it when first needed, in delatom, instead. [bruce 041116]
## _nullMol = Chunk("<not an assembly>")

def _get_nullMol():
    """
    return _nullMol, after making sure it's initialized
    """
    # inlined into delatom
    global _nullMol
    if _nullMol is None:
        _nullMol = _make_nullMol()
    return _nullMol

_nullMol = None

def _make_nullMol(): #bruce 060331 split out and revised this, to mitigate bugs similar to bug 1796
    """
    [private]
    Make and return (what the caller should store as) the single _nullMol object.
    """
    ## return Chunk("<not an assembly>", 'name-of-_nullMol')
    null_mol = _nullMol_Chunk("<not an assembly>", 'name-of-_nullMol')
    set_undo_nullMol(null_mol)
    return null_mol

class _nullMol_Chunk(Chunk):
    """
    [private]
    subclass for _nullMol
    """
    def changed_selection(self): # in class _nullMol_Chunk
        msg = "bug: _nullMol.changed_selection() should never be called"
        if env.debug():
            print_compact_stack(msg + ": ")
        else:
            print msg
        return

    def isNullChunk(self): # by Ninad, implementing old suggestion by Bruce for is_nullMol
        """
        @return: whether chunk is a "null object" (used as atom.molecule for some
        killed atoms).

        Overrides Chunk method.

        This method helps replace comparisons to _nullMol (helps with imports, 
        replaces set_undo_nullMol, permits per-assy _nullMol if desired)
        """
        return True

    pass # end of class _nullMol

# ==

from geometry.geometryUtilities import selection_polyhedron, inertia_eigenvectors, compute_heuristic_axis

def shakedown_poly_evals_evecs_axis(basepos):
    """
    Given basepos (an array of atom positions), compute and return (as the
    elements of a tuple) the bounding polyhedron we should draw around these
    atoms to designate that their Chunk is selected, the eigenvalues and
    eigenvectors of the inertia tensor (computed as if all atoms had the same
    mass), and the (heuristically defined) principal axis.
    """
    #bruce 041106 split this out of the old Chunk.shakedown() method,
    # replaced Chunk attrs with simple variables (the ones we return),
    # and renamed self.eval to evals (just in this function) to avoid
    # confusion with python's built-in function eval.
    #bruce 060119 split it into smaller routines in new file geometry.py.

    polyhedron = selection_polyhedron(basepos)

    evals, evecs = inertia_eigenvectors(basepos)
        # These are no longer saved as chunk attrs (since they were not used),
        # but compute_heuristic_axis would compute this anyway,
        # so there's no cost to doing it here and remaining compatible
        # with the pre-060119 version of this routine. This would also permit
        # a future optimization in computing other kinds of axes for the same
        # chunk (by passing different options to compute_heuristic_axis),
        # as we may want to do in viewParallelTo and viewNormalTo
        # (see also the comments about those in compute_heuristic_axis).

    axis = compute_heuristic_axis( 
        basepos, 
        'chunk',
        evals_evecs = (evals, evecs),
        aspect_threshhold = 0.95,
        near1 = V(1,0,0), 
        near2 = V(0,1,0), 
        dflt = V(1,0,0) # prefer axes parallel to screen in default view
     )

    assert axis is not None
    axis = A(axis) ##k if this is in fact needed, we should probably 
        # do it inside compute_heuristic_axis for sake of other callers
    assert type(axis) is type(V(0.1, 0.1, 0.1)) 
        # this probably doesn't check element types (that's probably ok)

    return polyhedron, evals, evecs, axis # from shakedown_poly_evals_evecs_axis

# ==

def mol_copy_name(name, assy = None):
    """
    turn xxx or xxx-copy or xxx-copy<n> into xxx-copy<m> for a new number <m>
    """
    # bruce 041124; added assy arg, 080407; rewrote/bugfixed, 080723
    
    # if name looks like xxx-copy or xxx-copy<nnn>, remove the -copy<nnn> part
    parts = name.split("-copy")
    if len(parts) > 1:
        nnn = parts[-1]
        if not nnn or nnn.isdigit():
            name = "-copy".join(parts[:-1]) # everything but -copy<nnn>
            # (note: this doesn't contain '-copy' unless original name
            #  contained it twice)
        pass
    
    return gensym(name + "-copy", assy) # (in mol_copy_name)
        # note: we assume this adds a number to the end

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

# end
