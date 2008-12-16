# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
chunk.py -- provides class Chunk [formerly known as class molecule],
for a bunch of atoms (not necessarily bonded together) which can be moved
and selected as a unit.

@author: Josh
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

originally by Josh

lots of changes, by various developers

split out of chem.py by bruce circa 041118

bruce optimized some things, including using 'is' and 'is not' rather than '==', '!='
for atoms, molecules, elements, parts, assys in many places (not all commented individually); 050513

bruce 060308 rewriting Atom and Chunk so that atom positions are always stored in the atom
(eliminating Atom.xyz and Chunk.curpos, adding Atom._posn, eliminating incremental update of atpos/basepos).
Motivation is to make it simpler to rewrite high-frequency methods in Pyrex. 

bruce 060313 splitting _recompute_atlist out of _recompute_atpos, and planning to remove atom.index from
undoable state. Rules for atom.index (old, reviewed now and reconfirmed): owned by atom.molecule; value doesn't matter
unless atom.molecule and its .atlist exist (but is set to -1 otherwise when this is convenient, to help catch bugs);
must be correct whenever atom.molecule.atlist exists (and is reset when it's made); correct means it's an index for
that atom into .atlist, .atpos, .basepos, whichever of those exist at the time (atlist always does).
This means a chunk's addatom, delatom, and _undo_update need to invalidate its .atlist,
and means there's no need to store atom.index as undoable state (making diffs more compact),
or to update a chunk's .atpos (or even .atlist) when making an undo checkpoint.

(It would be nice for Undo to not store copies of changed .atoms dicts of chunks too, but that's harder. ###e)

[update, bruce 060411: I did remove atom.index from undoable state, as well as chunk.atoms, and I made atoms always store
their own absposns. I forgot to summarize the new rules here -- maybe I did somewhere else. Looking at the code now,
atoms still try to get baseposns from their chunk, which still computes that before drawing them; moving a chunk
probably invalidates atpos and basepos (guess, but _recompute_atpos inval decl code would seem wrong otherwise)
and drawing it then recomputes them -- or maybe not, since it's only when remaking display list that it should need to.
Sometime I should review this and see if there is some obvious optimization needed.]

bruce 080305 changed superclass from Node to NodeWithAtomContents
"""

drawbonds = True # False  ## Debug/test switch.  Never check in a False value.

import math # only used for pi, everything else is from Numeric [as of before 071113]
import re
import Numeric
from Numeric import array
from Numeric import add
from Numeric import dot
from Numeric import PyObject
from Numeric import argsort
from Numeric import compress
from Numeric import take
from Numeric import argmax

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glCallList
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glPopName
from OpenGL.GL import glPushName

# (chem is used here only for class Atom, as of 080510)
import model.chem as chem

from model.global_model_changedicts import _changed_parent_Atoms

from geometry.VQT import V, Q, A, vlen

from foundation.NodeWithAtomContents import NodeWithAtomContents

from utilities.Log import graymsg

from utilities.debug import print_compact_stack
from utilities.debug import compact_stack
from utilities.debug import print_compact_traceback
from utilities.debug import safe_repr

from foundation.inval import InvalMixin
from foundation.changes import SelfUsageTrackingMixin, SubUsageTrackingMixin
    #bruce 050804, so glpanes can know when they need to redraw a chunk's display list,
    # and chunks can know when they need to inval that because something drawn into it
    # would draw differently due to a change in some graphics pref it used
from utilities.prefs_constants import bondpointHotspotColor_prefs_key
import foundation.env as env
from foundation.undo_archive import set_undo_nullMol
from utilities.Comparison import same_vals
##from foundation.state_utils import copy_val
from graphics.display_styles.displaymodes import get_display_mode_handler

from foundation.state_constants import S_REF, S_CHILDREN_NOT_DATA

from utilities import debug_flags

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

from utilities.icon_utilities import imagename_to_pixmap

import model.bonds as bonds # TODO: import specific functions, since no longer an import cycle

from model.ExternalBondSet import ExternalBondSet

from model.elements import Singlet

from geometry.BoundingBox import BBox
from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList
from graphics.drawing.TransformControl import TransformControl

##from drawer import drawlinelist

##from constants import PickedColor
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key

from utilities.constants import gensym, genKey

from utilities.constants import default_display_mode

from utilities.constants import diDEFAULT
from utilities.constants import diINVISIBLE
from utilities.constants import diBALL
from utilities.constants import diLINES
from utilities.constants import diTUBES
from utilities.constants import diTrueCPK
from utilities.constants import diDNACYLINDER
from utilities.constants import diPROTEIN

from utilities.constants import MAX_ATOM_SPHERE_RADIUS 
from utilities.constants import BBOX_MIN_RADIUS

from utilities.constants import white

from utilities.constants import ATOM_CONTENT_FOR_DISPLAY_STYLE
from utilities.constants import noop

from utilities.constants import MODEL_PAM3, MODEL_PAM5

from utilities.GlobalPreferences import use_frustum_culling #piotr 080402
from utilities.GlobalPreferences import pref_show_node_color_in_MT

from model.elements import PeriodicTable

from commands.ChunkProperties.ChunkProp import ChunkProp

from dna.model.Dna_Constants import getComplementSequence

from operations.bond_chains import grow_directional_bond_chain

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_lighting import apply_material
from graphics.drawing.gl_lighting import startPatternedDrawing
from graphics.drawing.gl_lighting import endPatternedDrawing

from graphics.drawables.Selobj import Selobj_API

from graphics.drawing.special_drawing import SPECIAL_DRAWING_STRAND_END
from graphics.drawing.special_drawing import SpecialDrawing_ExtraChunkDisplayList
from graphics.drawing.special_drawing import Chunk_SpecialDrawingHandler

_inval_all_bonds_counter = 1 #bruce 050516


# == debug code is near end of file


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

# Note: as of bruce 041116 we kill any mol which loses all its atoms
# after having had some. This is an experimental change; if it causes
# problems, we should instead do it when we update the model tree or glpane,
# since we need to ensure it's always done by the end of any user event.)

_superclass = NodeWithAtomContents #bruce 080305 revised this

class Chunk(NodeWithAtomContents, InvalMixin,
            SelfUsageTrackingMixin, SubUsageTrackingMixin,
            Selobj_API):
    """
    A set of atoms treated as a unit.
    """
    #bruce 071114 renamed this from class molecule -> class Chunk

    # class constants to serve as default values of attributes, and _s_attr decls for some of them

    _hotspot = None

    _s_attr_hotspot = S_REF #bruce 060404 revised this in several ways; bug 1633 (incl. all subbugs) will need retesting.
        # Note that this declares hotspot, not _hotspot, so that undo state never contains dead atoms.
        # This is only ok because we provide _undo_setattr_hotspot as well.
        #
        # Note that we don't put this (or Jig.atoms) into the 'atoms' _s_attrlayer, since we still need to scan them as data.
        #
        # Here are some old comments from when this declared _hotspot, still relevant:
        #e we need to warn somehow if you hit a StateMixin object in S_REF but didn't store state for it
        # (as could happen when we declared _hotspot as data, not child, and it could be a dead atom);
        #e ideally we'd add debug code to detect the original error (declaring hotspot),
        # due to presence of a _get_hotspot method; maybe we'd have an optional method (implemented by InvalMixin)
        # to say whether an attr is legal for an undoable state decl. But (060404) there needs to be an exception,
        # e.g. when _undo_setattr_hotspot exists, like now.

    _colorfunc = None
    _dispfunc = None

    is_movable = True #mark 060120 [no need for _s_attr decl, since constant for this class -- bruce guess 060308]

    # Undoable/copyable attrs: (no need for _s_attr decls since copyable_attrs provides them)

    # self.display overrides global display (GLPane.display)
    # but is overriden by atom value if not default

    display = diDEFAULT

    # this overrides atom colors if set
    color = None

    # user_specified_center -- as of 050526 it's sometimes used, but it's always None.
    #
    # note: if we implement self.user_specified_center as user-settable,
    # it also needs to be moved/rotated with the mol, like a datum point
    # rigidly attached to the mol (or like an atom)

    user_specified_center = None # never changed for now, so not in copyable_attrs

    # PAM3+5 attributes (these only affect PAM atoms in self, if any):
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
    # [bruce 080321 for PAM3+5] ### TODO: use for conversion, and prevent ladder merge when different

    display_as_pam = "" # PAM model to use for displaying and editing PAM atoms in self (not set means use user pref)

    save_as_pam = "" # PAM model to use for saving self (not normally set; not set means use save-op params)

    copyable_attrs = _superclass.copyable_attrs + ('display', 'color',
                                                   'display_as_pam', 'save_as_pam')
        # this extends the tuple from Node
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

    # no need to _s_attr_ decl basecenter and quat -- they're officially arbitrary, and get replaced when things get recomputed
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

    # Set this to True if any of the atoms in this chunk has their
    # overlayText set to anything other than None.  This keeps us from
    # having to test that for every single atom in every single chunk
    # each time the screen is rerendered.
    chunkHasOverlayText = False

    # Set to True if the user wishes to see the overlay text on this
    # chunk.
    showOverlayText = False

    protein = None
    
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
        assert self.assy is not None #bruce 080227 guess (from docstring) [can fail, 080325, tom bug when updater turned on after separate @@@]
        # One thing we know is required: if self.atoms changes, invalidate self.atlist.
        # This permits us to not store atom.index as undoable state, and to not update self.atpos before undo checkpoints.
        # [bruce 060313]
        self.invalidate_everything() # this is probably overkill, but its call of self.invalidate_atom_lists() is certainly needed

        self._colorfunc = None
        del self._colorfunc #bruce 060308 precaution; might fix (or cause?) some "Undo in Extrude" bugs

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

    def _undo_setattr_hotspot(self, hotspot, archive): #bruce 060404; 060410 use store_if_invalid to fix new bug 1829
        """
        Undo is mashing changed state into lots of objects' attrs at once;
        this lets us handle that specially, just for self.hotspot, but in unknown order (for now)
        relative either to our attrs or other objects.
        """
        self.set_hotspot( hotspot, store_if_invalid = True)

    def _enable_deallocate_displist(self):
        # to avoid duplicating this code; TODO: inline this method when it soon returns a constant True
        res = debug_pref("GLPane: deallocate OpenGL display lists of killed chunks?",
                         Choice_boolean_True,
                         prefs_key = True,
                         non_debug = True )
        return res

    # ==

    def __init__(self, assy, name = None):
        self.invalidate_all_bonds() # bruce 050516 -- needed in init to make sure
            # the counter it sets is always set, and always unique
        # note [bruce 041116]:
        # new chunks are NOT automatically added to assy.
        # this has to be done separately (if desired) by assy.addmol
        # (or the equivalent).
        # addendum [bruce 050206 -- describing the situation, not endorsing it!]:
        # (and for clipboard chunks it should not be done at all!
        #  also not for chunks "created in a Group", if any; for those,
        #  probably best to do addmol/moveto like [some code] does.)
        if not self.mticon:
            self.init_icons()
        self.init_InvalMixin()
        ## dad = None #bruce 050216 removed dad from __init__ args, since no calls pass it
            # and callers need to do more to worry about the location anyway (see comments above) 
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

        self.memo_dict = {}
            # for use by anything that wants to store its own memo data on us, using a key it's sure is unique [bruce 060608]
            # (when we eventually have a real destroy method, it should zap this; maybe this will belong on class Node #e)

        # self.displist is allocated on demand by _get_displist [bruce 070523]

        #glname is needed for highlighting the chunk as an independent object
        #NOTE: See a comment in self.highlight_color_for_modkeys() for more info.
        if not self.isNullChunk():
            self.glname = self.assy.alloc_my_glselect_name(self) #bruce 080917 revised
            ### REVIEW: is this ok or fixed if this chunk is moved to a new assy
            # (if that's possible)? [bruce 080917 Q]

        self.extra_displists = {} # precaution, probably not needed

        # keep track of other chunks we're bonded to; lazily updated
        # [bruce 080702]
        self._bonded_chunks = {}

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

    def make_glpane_context_menu_items(self, contextMenuList, command = None):
        """
        """
        # TODO: See make_selobj_cmenu_items in other classes. This method is very
        # similar to that method. But it's not named the same because the chunk
        # may not be a glpane.selobj (as it may get highlighted in SelectChunks
        # mode even when, for example, the cursor is over one of its atoms 
        # (i.e. selobj = an Atom). So ideally, that old method should be renamed
        # to this one. [Ninad]
        if command is None:
            return
        
        #Start Standard context menu items rename and delete [by Ninad]
        
        ### TODO: refactor to not hardcode these classes,
        # but to have a uniform way to find the innermost node
        # visible in the MT, to be renamed.
        ### Also REVIEW whether this is always the same as the unit
        # of hover highlighting, and if not, whether it should be,
        # and if so, whether the same code can be used to determine
        # the highlighted object and the object to rename or delete.
        # [bruce 081210 comments]
        
        parent_node_classes = (self.assy.DnaStrandOrSegment, 
                               self.assy.NanotubeSegment)
        
        parent_node = None
        
        for cls in parent_node_classes:
            parent_node = self.parent_node_of_class(cls)
            if parent_node:
                break

        node_to_rename = parent_node or self
        name = node_to_rename.name
        
        item = (("Rename %s..." % name),
                node_to_rename.rename_using_dialog )
        contextMenuList.append(item)

        def delnode_cmd(node_to_rename = node_to_rename):
            node_to_rename.assy.changed() #bruce 081210 bugfix, not sure if needed
            node_to_rename.assy.win.win_update() #bruce 081210 bugfix
            node_to_rename.kill_with_contents()
            return
        
        item = (("Delete %s" % name), delnode_cmd )
        contextMenuList.append(item)
        #End Standard context menu items rename and delete

        def addDnaGroupMenuItems(dnaGroup):
            if dnaGroup is None:
                return
            item = (("DnaGroup: [%s]" % dnaGroup.name), noop, 'disabled')
            contextMenuList.append(item)	    
            item = (("Edit DnaGroup Properties..."), 
                    dnaGroup.edit) 
            contextMenuList.append(item)
            return
        
        #Urmi 20080730: edit properties for protein for context menu in gl pane
        if command.commandName in ('SELECTMOLS', 'MODEL_AND_SIMULATE_PROTEIN'):
            if self.isProteinChunk():
                try:
                    protein = self.protein
                except:
                    print_compact_traceback("exception in protein class")
                    return
                if protein is not None:
                    item = (("%s" % (self.name)),
                            noop, 'disabled')
                    contextMenuList.append(item)
                    item = (("Edit Protein Properties..."), 
                            (lambda _arg = self.assy.w, protein = protein:
                             protein.edit(_arg))
                             )
                    contextMenuList.append(item)
                    
        if command.commandName in ('SELECTMOLS', 'BUILD_NANOTUBE', 'NANOTUBE_SEGMENT'):
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
                if segment is not None:
                    # Self is a member of a Nanotube group, so add this 
                    # info to a disabled menu item in the context menu.
                    item = (("%s" % (segment.name)),
                            noop, 'disabled')
                    contextMenuList.append(item)

                    item = (("Edit Nanotube Properties..."), 
                            segment.edit)
                    contextMenuList.append(item)

        if command.commandName in ('SELECTMOLS', 'BUILD_DNA', 'DNA_SEGMENT', 'DNA_STRAND'):
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
                    #within a Dnagroup. Lets assume that this is possible. 
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
                
                addDnaGroupMenuItems(dnaGroup)
                
                # add menu commands from our DnaLadder [bruce 080407]
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
                    if segment.picked:       
                        selectedDnaSegments = self.assy.getSelectedDnaSegments()
                        if len(selectedDnaSegments) > 0:
                            item = (("Resize Selected DnaSegments "\
                                     "(%d)..."%len(selectedDnaSegments)), 
                                    self.assy.win.resizeSelectedDnaSegments)
                            contextMenuList.append(item)
                            contextMenuList.append(None)
                    if self.ladder:
                        menu_spec = self.ladder.dnaladder_menu_spec(self)
                        if menu_spec:
                            contextMenuList.extend(menu_spec)
                            
                    addDnaGroupMenuItems(dnaGroup)

        return # from make_glpane_context_menu_items

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
                if not self._bonded_chunks.has_key( otherchunk):
                    if not otherchunk._bonded_chunks.has_key( self):
                        ebset = ExternalBondSet( self, otherchunk)
                        otherchunk._bonded_chunks[ self] = ebset
                    else:
                        # was there but not here -- should never happen
                        # (since the only way to make one is the above case,
                        #  which ends up storing it in both otherchunk and self,
                        #  and the only way to remove one removes it from both)
                        ebset = otherchunk._bonded_chunks[ self]
                        print "likely bug: ebset %r was in %r but not in %r" % \
                              (ebset, otherchunk, self)
                    self._bonded_chunks[ otherchunk] = ebset
                else:
                    ebset = self._bonded_chunks[ otherchunk]
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
    
    # START of Dna-Strand-or-Axis chunk specific code ==========================

    # Note: all these methods will be removed from class Chunk once the
    # dna data model is always active. [bruce 080205 comment]

    # Assign a strand sequence (or get that information from a chunk) 
    # MEANT ONLY FOR THE DNA CHUNK. THESE METHODS NEED TO BE MOVED TO AN 
    # APPROPRIATE FILE IN The dna_model PACKAGE -- Ninad 2008-01-11
    # [And revised to use DnaMarkers for sequence alignment as Ninad suggests below.
    #  The sequence methods will end up as methods of DnaStrand with
    #  possible helper methods on objects it owns, like DnaStrandChunk
    #  (whose bases are in a known order) or DnaMarker or internal objects
    #  they refer to. -- Bruce 080117/080205 comment]

    def getStrandSequence(self):
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


    def setStrandSequence(self, sequenceString):
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
            complementBaseName= getComplementSequence(str(baseName))
            if strandAtomMate is not None:
                strandAtomMate.setDnaBaseName(str(complementBaseName))  
    def edit(self):
        #Following must be revised (moved to appropriate class)
        #post dna_model implementation .
        if self.isStrandChunk():
            commandSequencer = self.assy.w.commandSequencer
            commandSequencer.userEnterCommand('DNA_STRAND')                
            assert commandSequencer.currentCommand.commandName == 'DNA_STRAND'
            commandSequencer.currentCommand.editStructure(self)
        else:
            cntl = ChunkProp(self) # Renamed MoleculeProp to ChunkProp.  Mark 050929
            cntl.exec_()
            self.assy.mt.mt_update()
            ###e bruce 041109 comment: don't we want to repaint the glpane, too?

    def getProps(self):
        """
        To be revised post dna data model. Used in EditConmmand class and its 
        subclasses.
        """
        return ()

    def setProps(self, params):
        """
        To be revised post dna data model
        """
        del params

    def isStrandChunk(self): # Ninad circa 080117, revised by Bruce 080117
        """
        Returns True if *all atoms* in this chunk are PAM 'strand' atoms
        or 'unpaired-base' atoms (or bondpoints), and at least one is a
        'strand' atom.

        Also resets self.iconPath (based on self.hidden) if it returns True.

        This is a temporary method that can be removed once dna_model is fully
        functional.
        @see: BuildDna_PropertyManager.updateStrandListWidget where this is used
              to filter out strand chunks to put those into the strandList 
              widget.        
        """
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
        or or bondpoints, and at least one is an
        'axis' atom.
        This is a temporary method that can be removed once dna_model is fully
        functional.
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

    #START of Nanotube chunk specific code ========================

    def isNanotubeChunk(self):
        """
        Returns True if *all atoms* in this chunk are either:
        - carbon (sp2) and either all hydrogen or nitrogen atoms or bondpoints
        - boron and either all all hydrogen or nitrogen atoms or bondpoints

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

    def getNanotubeGroup(self): # ninad 080205
        """
        Return the NanotubeGroup of this chunk if it has one. 
        """
        return self.parent_node_of_class(self.assy.NanotubeGroup)

    #END of Nanotube chunk specific code ========================


    # Methods relating to our OpenGL display list, self.displist.
    #
    # (Note: most of these methods could be moved with few changes to a
    # new mixin class concerned with maintaining self.displist for any
    # sort of object that needs one. If that's done, see also
    # GLPane_mixin_for_DisplayListChunk for useful features of other kinds
    # to integrate into that code. [bruce 071103 comment])

    def _get_displist(self):
        """
        initialize and return self.displist
        [must only be called when an appropriate GL context is current]
        """
        #bruce 070523 change: do this on demand, not in __init__, to see if it fixes bug 2402
        # in which this displist can be 0 on Linux (when entering Extrude).
        # Theory: you should allocate it only when you know you're in a good GL context
        # and are ready to draw, which is most safely done when you are first drawing,
        # so allocating it on demand is the easiest way to do that. Theory about bug 2042:
        # maybe some Qt drawing was changing the GL context in an unpredictable way;
        # we were not even making glpane (or a thumbview) current before allocating this, until now.
        #
        # Note: we use _get_displist rather than _recompute_displist so we don't need to teach
        # full_inval_and_update to ignore 'displist' as a special case. WARNING: for this method
        # it's appropriate to set self.displist as well as returning it, but for most uses of
        # _get_xxx methods, setting it would be wrong.
        self.displist = ColorSortedDisplayList()      # russ 080225: Moved state into a class.
        return self.displist

    # new feature [bruce 071103]:
    # deallocate display lists of killed chunks.
    # TODO items re this:
    # - doc the fact that self.displist can be different when chunk kill is undone
    # - worry about ways chunks can miss out on this:
    #   - created, then undo that
    #   - no redraw, e.g. for a thumbview in a dialog that gets deleted...
    #     maybe ok if user ever shows it again, but what if they never do?
    # - probably ok, but need to test:
    #   - close file, or open new file
    #   - when changing to a new partlib part, old ones getting deleted
    #   - create chunk, undo, redo, etc or then kill it
    #   - kill chunk, undo, redo, undo, etc or then kill it

    def _deallocate_displist(self): #bruce 071103
        """
        [private method; must only be called when our displist's GL context is current]
        Deallocate our OpenGL display list, and record that we did so.
        """
        if self.__dict__.has_key('displist'):
            # Note: we can't use hasattr for that test, since it would
            # allocate self.displist (by calling _get_displist) if we
            # don't have one yet.
            #russ 080225: Moved deallocation into ColorSortedDisplayList class for ColorSorter.
            top = self.displist.dl
            self.displist.deallocate_displists()
            for extra_displist in self.extra_displists.values():
                extra_displist.deallocate_displists()
            self.extra_displists = {}
            if debug_pref("GLPane: print deleted display lists", Choice_boolean_False): #bruce 071205 made debug pref
                print "fyi: deleted OpenGL display list %r belonging to %r" % (top, self)
                # keep this print around until this feature is tested on all platforms
            self.displist = None
            del self.displist
                # this del is necessary, so _get_displist will be called if another
                # display list is needed (e.g. if a killed chunk is revived by Undo)
            self.havelist = 0
            self.glpane = None
        pass

    def deallocate_displist_later(self): #bruce 071103
        """
        At the next convenient time when our OpenGL context is current,
        if self.ok_to_deallocate_displist(),
        call self._deallocate_displist().
        """
        self.call_when_glcontext_is_next_current( self._deallocate_displist_if_ok )
        return

    def _deallocate_displist_if_ok(self): #bruce 071103
        if self.ok_to_deallocate_displist():
            self._deallocate_displist()
        return

    def ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).
        """
        return len(self.atoms) == 0
            # self.killed() might also be correct,
            # but would be redundant with this anyway

    def _gl_context_if_any(self): #bruce 071103
        """
        If self has yet been drawn into an OpenGL context,
        return a GLPane_minimal object which corresponds to it;
        otherwise return None. (Note that self can be drawn
        into at most one OpenGL context during its lifetime,
        except for contexts which share display list names.)
        """
        # (I'm not sure whether use of self.glpane is a kluge.
        #  I guess it would not be if we formalized what it already means.)
        return self.__dict__.get('glpane', None)

    def call_when_glcontext_is_next_current(self, func): #bruce 071103
        """
        """
        glpane = self._gl_context_if_any()
        if glpane:
            glpane.call_when_glcontext_is_next_current(func)
        return

    def _f_invalidate_atom_lists_and_maybe_deallocate_displist(self):
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
        if self._enable_deallocate_displist():
            need_to_deallocate = self.ok_to_deallocate_displist()
            if need_to_deallocate:
                ## print "undo or redo calling deallocate_displist_later on %r" % self
                self.deallocate_displist_later()
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
        # make sure no other code forgot to call us and set it directly
        assert not 'hotspot' in self.__dict__.keys(), "bug in some unknown other code"
        if self._hotspot is not hotspot:
            self.changed() #bruce 060324 fix bug 1532, and an unreported bug where this didn't mark file as modified
        self._hotspot = hotspot
        if not store_if_invalid: # (when that's true, it's important not to recompute self.hotspot, even in an assertion)
            # now recompute self.hotspot from the new self._hotspot (to check whether it's valid)
            self.hotspot # this has side effects we depend on!
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
    def node_icon(self, display_prefs): # bruce 050109 revised this [was seticon]; revised again 060608
        # Special case for protein icon. This only adds the icon to the MT.
        # To add the protein icon for PM_SelectionListWidget, the attr iconPath
        # was modified in isProteinChunk(). --Mark 2008-12-16.
        if self.isProteinChunk():
            hd = get_display_mode_handler(diPROTEIN)
            if hd:
                return hd.get_icon(self.hidden)
        try:
            if self.hidden:
                return self.hideicon[self.display]
            else:
                return self.mticon[self.display]
                
        except IndexError:
            # probably one of those new-fangled ChunkDisplayModes [bruce 060608]
            hd = get_display_mode_handler(self.display)
            if hd:
                return hd.get_icon(self.hidden)
            # hmm, some sort of bug
            return imagename_to_pixmap("modeltree/junk.png")
        pass
    def bond(self, at1, at2):
        """
        Cause atom at1 to be bonded to atom at2.
        Error if at1 is at2 (causes printed warning and does nothing).
        (This should really be a separate function, not a method on Chunk,
        since the specific Chunk asked to do this need not be either atom's
        Chunk, and is not used in the method at all.)
        """
        bonds.bond_atoms(at1, at2) #bruce 041109 split out separate function to do it
        ## old code assumed both atoms were in this Chunk; often not true!
        ## self.havelist = 0
        return

    # lowest-level structure-changing methods

    def addatom(self, atom):
        """
        Private method;
        should be the only way new atoms can be added to a Chunk
        (except for optimized callers like Chunk.merge, and others with comments saying they inline it).
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
                # this is what makes it ok for atom indices to be invalid, as they are when self.atoms changes,
                # until self.atlist is next recomputed [bruce 060313 comment]
        except:
            pass
        else:
            need = 1
        if need:
            # this causes trouble, not yet sure why:
            ## self.changed_attrs(['externs', 'atlist'])
            ## AssertionError: validate_attr finds no attr 'externs' was saved, in <Chunk 'Ring Gear' (5167 atoms) at 0xd967440>
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
        self.invalidate_all_bonds()
        self.invalidate_atom_lists() # _undo_update depends on us calling this
        attrs  = self.invalidatable_attrs()
        # now this is done in that method: attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            self.invalidate_attr(attr)
        # (these might be sufficient: ['externs', 'atlist', 'atpos'])
        return

    # debugging methods (not fully tested, use at your own risk)

    def update_everything(self):
        attrs  = self.invalidatable_attrs()
        # now this is done in that method: attrs.sort() # be deterministic even if it hides bugs for some orders
        for attr in attrs:
            junk = getattr(self, attr)
        # don't actually remake display list, but next redraw will do that;
        # don't invalidate it (havelist = 0) since our semantics are to only
        # update.
        return

    # some more invalidation methods

    def changed_atom_posn(self): #bruce 060308
        """
        Some atom we own changed position; invalidate whatever we might own that depends on that.
        """
        # initial implem might be too conservative; should optimize, perhaps recode in a new Pyrex ChunkBase.
        # Some code is copied from now-obsolete setatomposn; some of its comments might apply here as well.
        self.changed()
        self.havelist = 0
        self.invalidate_attr('atpos') #e should optim this ##k verify this also invals basepos, or add that to the arg of this call
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
        # (Filter always returns a python list, even if atlist is a Numeric.array
        # [bruce 041207, by separate experiment]. Some callers test the boolean
        # value we compute for self.singlets. Since the elements are pyobjs,
        # this would probably work even if filter returned an array.)
        return filter( lambda atom: atom.element is Singlet, self.atlist )

    _inputs_for_singlpos = ['singlets', 'atpos']
    def _recompute_singlpos(self):
        self.atpos
        # we must access self.atpos, since we depend on it in our inval rules
        # (if that's too slow, then anyone invalling atpos must inval this too #e)
        if len(self.singlets):
            # (This was apparently None for no singlets -- always a bug,
            #  and caused bug 237 in Extrude entry. [bruce 041206])
            return A( map( lambda atom: atom.posn(), self.singlets ) )
        else:
            return []
        pass

    # These 4 attrs are stored in one tuple, so they can be invalidated
    # quickly as a group.

    def _get_polyhedron(self):
        return self.poly_evals_evecs_axis[0]
#bruce 060119 commenting these out since they are not used, though if we want them it's fine to add them back.
#bruce 060608 renamed them with plural 's'.
##    def _get_evals(self):
##        return self.poly_evals_evecs_axis[1]
##    def _get_evecs(self):
##        return self.poly_evals_evecs_axis[2]
    def _get_axis(self):
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

    def _recompute_atlist(self): #bruce 060313 splitting _recompute_atlist out of _recompute_atpos
        """
        [recompute the list of this chunk's atoms, in order of atom.key
        (and store atom.index to match, if it still exists)]
        """
        atomitems = self.atoms.items()
        atomitems.sort() # make them be in order of atom keys; probably doesn't yet matter but makes order deterministic
        atlist = [atom for (key, atom) in atomitems] #k syntax
        self.atlist = array(atlist, PyObject) #k it's untested whether making it an array is good or bad
        for atom, i in zip(atlist, range(len(atlist))):
            atom.index = i 
        return        

    _inputs_for_atpos = ['atlist'] # also incrementally modified by setatomposn [not anymore, 060308]
        # (Atpos could be invalidated directly, but maybe it never is (not sure);
        #  anyway we don't optim for that.)
    _inputs_for_basepos = ['atpos'] # also invalidated directly, but not often

    def _recompute_atpos(self): #bruce 060308 major rewrite;  #bruce 060313 splitting _recompute_atlist out of _recompute_atpos
        """
        recompute self.atpos and self.basepos and more;
        also change self's local coordinate system (used for basepos)
        [#doc more]
        """
        #    Something must have been invalid to call us, so basepos must be invalid. So we needn't call changed_attr on it.
        assert not self.__dict__.has_key('basepos')
        if self.assy is None:
            if debug_flags.atom_debug:
                # [bruce comment 050702: this happens if you delete the chunk while dragging it by selatom in build mode]
                print_compact_stack("atom_debug: fyi, recompute atpos called on killed mol %r: " % self)
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
        atpos = map( lambda atom: atom.posn(), atlist ) # atpos, basepos, and atlist must be in same order
        atpos = A(atpos)
        # we must invalidate or fix self.atpos when any of our atoms' positions is changed!
        self.atpos = atpos

        assert len(atpos) == len(atlist)

        self._recompute_average_position() # sets self.average_position from self.atpos
        self.basecenter = + self.average_position # not an invalidatable attribute
            # unary '+' prevents mods to basecenter from affecting average_position;
            # it might not be needed (that depends on Numeric.array += semantics).
        # Note: basecenter is arbitrary, but should be somewhere near the atoms...
        # except see set_basecenter_and_quat, used in extrudeMode -- it may be that it's not really arbitrary
        # due to kluges in how that's used [still active as of 070411].
        if debug_messup_basecenter:
            # ... so this flag lets us try some other value to test that!!
            blorp = messupKey.next()
            self.basecenter += V(blorp, blorp, blorp)
        self.quat = Q(1,0,0,0)
            # arbitrary value, except we assume it has this specific value to simplify/optimize the next line
        if self.atoms:
            self.basepos = atpos - self.basecenter
                # set now (rather than when next needed) so it's still safe to assume self.quat == Q(1,0,0,0)
        else:
            self.basepos = []
            # this has wrong type, so requires special code in mol.move etc
            ###k Could we fix that by just assigning atpos to it (no elements, so should be correct)?? [bruce 060119 question]

        assert len(self.basepos) == len(atlist)

        # note: basepos must be a separate (unshared) array object
        # (except when mol is frozen [which is no longer supported as of 060308]);
        # as of 060308 atpos (when defined) is a separate array object, since curpos no longer exists.
        self.changed_basecenter_or_quat_while_atoms_fixed()
            # (that includes self.changed_attr('basepos'), though an assert above
            # says that that would not be needed in this case.)

        # validate the attrs we set, except for the non-invalidatable ones,
        # which are curpos, basecenter, quat.
        self.validate_attrs(['atpos', 'average_position', 'basepos'])
        return # from _recompute_atpos

    # aliases, in case someone needs one of the other things we compute
    # (but not average_position, that has its own recompute method):
    _recompute_basepos   = _recompute_atpos

    def changed_basecenter_or_quat_while_atoms_fixed(self):
        """
        Private method:
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
        Make a new bounding box from the atom positions (including singlets).
        """
        self.bbox = BBox(self.atpos)

    # Center.

    def _get_center(self):
        # _get_center seems better than _recompute_center since this attr
        # is only needed by the UI and this method is fast
        """
        Return the center to use for rotations and stretches and perhaps some
        other purposes (user-settable, or the average atom position by default)
        """
        if self.user_specified_center is not None: #bruce 050516 bugfix: 'is not None'
            return self.user_specified_center
        return self.average_position

    # What used to be called self.center, used mainly to relate basepos and curpos,
    # is now called self.basecenter and is not a recomputed attribute,
    # though it is chosen and stored by the _recompute_atpos method.
    # See also a comment about this in Chunk.__init__. [bruce 041112]

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
        for atom in self.atoms.itervalues():
            for bond in atom.bonds:
                ## if bond.other(atom).molecule != self # slower than needed:
                if bond.atom1.molecule is not self or bond.atom2.molecule is not self:
                    # external bond
                    externs.append(bond)
        return externs

    def freeze(self):
        """
        set self up for minimization or simulation
        """
        return #bruce 060308 removing this
                # (it wasn't working beyond the first frame anyway; it will be superceded by Pyrex optims;
                #  only call is in movie.py)

    def unfreeze(self):
        """
        to be done at the end of minimization or simulation
        """
        return #bruce 060308 removing this (see comments in freeze)

    def get_dispdef(self, glpane = None):
        """
        reveal what dispdef we will use to draw this Chunk
        """
        # copied out of Chunk.draw by bruce 041109 for use in extrudeMode.py
        if self.display != diDEFAULT:
            disp = self.display
        else:
            if glpane is None:
                # this possibility added by bruce 041207
                glpane = self.assy.o
            disp = glpane.displayMode

        # piotr 080409: fixed bug 2785
        # If the chunk is not DNA and global display mode == diDNACYLINDER
        # use default_display_mode instead.
        # (Warning: default_display_mode is no longer the same as the default
        #  global display style. Is it still correct here? Needs analysis
        #  and cleanup. [bruce 080606 comment])
        if disp == diDNACYLINDER:
            if not self.isDnaChunk(): # non-DNA chunk
                if self.isProteinChunk(): 
                    # piotr 080709 -- If the chunk is a protein, use 
                    # diPROTEIN style.
                    disp = diPROTEIN
                else:
                    # Otherwise, use last non-reduced global display mode.
                    disp = glpane.lastNonReducedDisplayMode

        # piotr 080709: If the chunk is not a protein chunk and global
        # display mode == diPROTEIN, use default_display_mode instead.
        if disp == diPROTEIN:
            if not self.isProteinChunk():
                # If this is a DNA chunk, use diDNACYLINDER display mode.
                if self.isDnaChunk():
                    disp = diDNACYLINDER
                else:
                    # Otherwise, use last non-reduced global display mode.
                    disp = glpane.lastNonReducedDisplayMode
                    
        return disp

    def pushMatrix(self): #bruce 050609 duplicated this from some of self.draw()
        """
        Do glPushMatrix(), and then transform from world coords to this chunk's private coords.
        See also self.popMatrix().
        """
        glPushMatrix()
        self.applyMatrix()
        return

    # Russ 080922: Pulled out of self.pushMatrix to fit with exception logic in self.draw().
    def applyMatrix(self):
        # Russ 080922: If there is a transform in the CSDL, use it.
        tc = self.displist.transformControl
        if tc is not None:
            tc.applyTransform()
        else:
            origin = self.basecenter
            glTranslatef(origin[0], origin[1], origin[2])
            q = self.quat
            glRotatef(q.angle*180.0/math.pi, q.x, q.y, q.z)
            pass
        return

    def popMatrix(self): #bruce 050609
        """
        Undo the effect of self.pushMatrix().
        """
        glPopMatrix()

    def inval_display_list(self): #bruce 050804
        """
        This is meant to be called when something whose usage we tracked
        (while making our display list) next changes.
        """
        self.changeapp(0) # that now tells self.glpane to update, if necessary
        ###@@@ glpane needs to track changes anyway due to external bonds.... [not sure of status of this comment; as of bruce 060404]

    _havelist_inval_counter = 0

    def draw(self, glpane, dispdef):
        """
        Draw all the atoms, using the atom's, self's,
        or GLPane's display mode in that order of preference.
        (Note that our dispdef argument is not used at all.)
        Draw each bond only once, even though internal bonds
        will be referenced from two atoms in this Chunk.
        (External bonds are drawn once by each Chunk they connect.)
        If the Chunk itself is selected, draw its bounding box as a
        wireframe; selected atoms are drawn specially by atom.draw.
        """

        # piotr 080331 moved this assignment before visibility 
        # and frustum culling tests 
        self.glpane = glpane # needed for the edit method - Mark [2004-10-13]
            # (and now also needed by BorrowerChunk during draw_dispdef's call of _dispfunc [bruce 060411])
            #
            ##e bruce 041109: couldn't we figure out self.glpane on the fly from self.dad?
            # (in getattr or in a special method)
            #bruce 050804: self.glpane is now also used in self.changeapp(),
            # since it's faster than self.track_change (whose features are overkill for this),
            # though the fact that only one glpane can be recorded in self
            # is a limitation we'll need to remove at some point.

        if not self.atoms:
            # do nothing for a Chunk without any atoms
            # [to fix bugs -- Huaicai 09/30/04]
            # (moved before frustum test, bruce 080411)
            return

        # Indicate overlapping atoms, if that pref is enabled.
        # We do this outside of the display list so we can still use that
        # for most of the drawing (for speed). We do it even for atoms
        # in hidden chunks, even in display modes that don't draw atoms,
        # etc. (But not for frustum culled atoms, since the indicators
        # would also be off-screen.) [bruce 080411 new feature]

        indicate_overlapping_atoms = self.part and self.part.indicate_overlapping_atoms
            # note: using self.part for this is a slight kluge;
            # see the comments where this variable is defined in class Part.

        if self.hidden and not indicate_overlapping_atoms:
            # (usually do this now, to avoid overhead of frustum test;
            #  if indicate_overlapping_atoms is true, we'll test self.hidden
            #  again below, to make sure we still skip other drawing)
            return

        # Frustum culling test # piotr 080331
        # piotr 080401: Do not return yet, because external bonds 
        # may be still drawn.
        # piotr 080402: Added a correction for the true maximum
        # DNA CPK atom radius.
        # Maximum VdW atom radius in PAM3/5 = 5.0 * 1.25 + 0.2 = 6.2
        # = MAX_ATOM_SPHERE_RADIUS
        # The default radius used by BBox is equal to sqrt(3*(1.8)^2) =
        # = 3.11 A, so the difference = approx. 3.1 A = BBOX_MIN_RADIUS
        # The '0.5' is another 'fuzzy' safety margin, added here just 
        # to be sure that all objects are within the sphere.
        # piotr 080403: moved the correction here from GLPane.py
        is_chunk_visible = glpane.is_sphere_visible(self.bbox.center(), 
                                                    self.bbox.scale() + (MAX_ATOM_SPHERE_RADIUS - BBOX_MIN_RADIUS) + 0.5)

        if indicate_overlapping_atoms and is_chunk_visible:
            self._indicate_overlapping_atoms()

        if self.hidden:
            # catch the case where indicate_overlapping_atoms skipped this test earlier
            return

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

        drawLevel = self.assy.drawLevel # this might recompute it
            # (if that happens and grabs the pref value, I think this won't subscribe our display list to it,
            #  since we're outside the begin/end for that, and that's good, since we include this in havelist
            #  instead, which avoids some unneeded redrawing, e.g. if pref changed and changed back while
            #  displaying a different Part. [bruce 060215])
            # update, bruce 080930: that point is probably moot, since drawLevel is part of havelist.

        disp = self.get_dispdef(glpane) 
            # piotr 080401: Moved it here, because disp is required by 
            # _draw_external_bonds.

        if is_chunk_visible:
            # piotr 080401: If the chunk is culled, skip drawing, but still draw 
            # external bonds (unless a separate debug pref is set.) 
            # The frustum culling test is now performed individually for every
            # external bond. 

            #This is needed for chunk highlighting
            ### REVIEW: this is our first use of "nested glnames". The hover
            # highlighting code in GLPane was written with the assumption
            # that we never use them, and the effects of using them on it
            # have not been reviewed. Conceivably it might slow it down
            # (by making some of its optims work less well, e.g. due to
            # overlapping highlight regions between self and its draw-children
            # with their own glnames (atoms and bonds), or cause bugs, though
            # I think both of those are unlikely, so this review is not urgent.
            # [bruce 080411 comment]
            glPushName(self.glname)

            # put it in its place
            glPushMatrix()

            try: #bruce 041119: do our glPopMatrix no matter what
                self.applyMatrix() # Russ 080922: This used to be inlined here.

                # Moved to above - piotr 080401
                # But what if there is an exception in self.get_dispdef ?
                # disp = self.get_dispdef(glpane)

    ##            delegate_selection_wireframe = False
                delegate_draw_atoms = False
                delegate_draw_chunk = False
                hd = None
                if 1:
                    #bruce 060608 look for a display mode handler for this chunk
                    # (whether it's a whole-chunk mode, or one we'll pass to the
                    #  atoms as we draw them (nim)).
                    hd = get_display_mode_handler(disp)
                    # see if it's a chunk-only handler. If so, we don't draw
                    # atoms or chunk selection wireframe ourselves -- instead,
                    # we delegate those tasks to it
                    if hd:
                        chunk_only = hd.chunk_only
    ##                    delegate_selection_wireframe = chunk_only
                        delegate_draw_atoms = chunk_only
                        delegate_draw_chunk = chunk_only
                            #e maybe later, we'll let hd tell us each of these,
                            # based on the chunk state.
                    pass

                #bruce 060608 moved drawing of selection wireframe from here to
                # after the new increment of _havelist_inval_counter
                # (and split it into a new submethod), even though it's done
                # outside of the display list. This was necessary for
                # _f_drawchunk_selection_frame's use of memoized data to work.            
                ## self._draw_selection_frame(glpane, delegate_selection_wireframe, hd)

                # cache chunk display (other than selection wireframe or hover
                # highlighting) as OpenGL display list

                # [bruce 050415 changed value of self.havelist when it's not 0,
                #  from 1 to (disp,),
                #  to fix bug 452 item 15 (no havelist inval for non-current
                #  parts when global default display mode is changed); this
                #  will incidentally optimize some related behaviors by avoiding
                #  some needless havelist invals, now that we've also removed
                #  the now-unneeded changeapp of all chunks upon global dispdef
                #  change (in GLPane.setGlobalDisplayStyle).]
                # [bruce 050419 also including something for element radius and
                #  color prefs, to fix bugs in updating display when those
                #  change (eg bug 452 items 12-A, 12-B).]

                eltprefs = PeriodicTable.color_change_counter, PeriodicTable.rvdw_change_counter
                matprefs = drawing_globals.glprefs.materialprefs_summary() #bruce 051126
                #bruce 060215 adding drawLevel to havelist
                if self.havelist == (disp, eltprefs, matprefs, drawLevel): # value must agree with set of havelist, below
                    # our main display list is still valid -- use it
                    # Russ 081128: Switch from draw_dl() to draw() with selection arg.
                    self.displist.draw(selected = self.picked)
                    for extra_displist in self.extra_displists.itervalues():
                        # [bruce 080604 new feature]
                        # note: similar code in else clause, differs re wantlist
                        extra_displist.draw_but_first_recompile_if_needed(glpane, selected = self.picked)
                        # todo: pass wantlist? yes in theory, but not urgent.
                        continue
                    pass
                else:
                    # our main display list (and all extra lists) needs to be remade
                    if 1:
                        #bruce 060608: record info to help per-chunk display modes
                        # figure out whether they need to invalidate their memo data.
                        if not self.havelist:
                            # only count when it was set to 0 externally, not just when it doesn't match and we reset it below.
                            # (Note: current code will also increment this every frame, when wantlist is false.
                            #  I'm not sure what to do about that. Could we set it here to False rather than 0, so we can tell?? ##e)
                            self._havelist_inval_counter += 1
                        ##e in future we might also record eltprefs, matprefs, drawLevel (since they're stored in .havelist)
                    self.havelist = 0 #bruce 051209: this is now needed
                    try:
                        wantlist = not env.mainwindow().movie_is_playing #bruce 051209
                            # warning: use of env.mainwindow is a KLUGE
                    except:
                        print_compact_traceback("exception (a bug) ignored: ")
                        wantlist = True
                    self.extra_displists = {} # we'll make new ones as needed
                    if wantlist:
                        ##print "Regenerating display list for %s" % self.name
                        match_checking_code = self.begin_tracking_usage()
                        #russ 080225: Moved glNewList into ColorSorter.start for displist re-org.
                        #russ 080225: displist side effect allocates a ColorSortedDisplayList.
                        #russ 080305: Chunk may already be selected, tell the CSDL.
                        ColorSorter.start(self.displist, self.picked)

                    # bruce 041028 -- protect against exceptions while making display
                    # list, or OpenGL will be left in an unusable state (due to the lack
                    # of a matching glEndList) in which any subsequent glNewList is an
                    # invalid operation. (Also done in shape.py; not needed in drawer.py.)
                    try:
                        self._draw_for_main_display_list(
                            glpane, disp,
                            (hd, delegate_draw_atoms, delegate_draw_chunk),
                            wantlist)
                    except:
                        print_compact_traceback("exception in Chunk._draw_for_main_display_list ignored: ")

                    if wantlist:
                        ColorSorter.finish()
                        #russ 080225: Moved glEndList into ColorSorter.finish for displist re-org.

                        self.end_tracking_usage( match_checking_code, self.inval_display_list )
                        # This is the only place where havelist is set to anything true;
                        # the value it's set to must match the value it's compared with, above.
                        # [bruce 050415 revised what it's set to/compared with; details above]
                        self.havelist = (disp, eltprefs, matprefs, drawLevel)
                        assert self.havelist, (
                            "bug: havelist must be set to a true value here, not %r"
                            % (self.havelist,))
                        # always set the self.havelist flag, even if exception happened,
                        # so it doesn't keep happening with every redraw of this Chunk.
                        #e (in future it might be safer to remake the display list to contain
                        # only a known-safe thing, like a bbox and an indicator of the bug.)

                    # draw the extra_displists (only needed if wantlist? not sure, so do always;
                    #  guess: there will be none of them unless wantlist is set, so it doesn't matter)
                    for extra_displist in self.extra_displists.itervalues():
                        extra_displist.draw_but_first_recompile_if_needed(glpane,
                                                                          selected = self.picked,
                                                                          wantlist = wantlist)
                        
                    pass # end of the case where our "main display list (and all extra lists) needs to be remade"

                # REVIEW: is it ok that self.glname is exposed for the following
                # renderOverlayText drawing? Guess: yes, even though it means mouseover
                # of the text will cause a redraw, and access to chunk context menu.
                # If it turns out that that redraw also visually highlights the chunk,
                # we might reconsider, but even that might be ok.
                # [bruce 081211 comments]
                if (self.chunkHasOverlayText and self.showOverlayText):
                    self.renderOverlayText(glpane)
                
                #@@ninad 070219 disabling the following--
                #self._draw_selection_frame(glpane, delegate_selection_wireframe, hd) #bruce 060608 moved this here

                # piotr 080320
                if hd:
                    hd._f_drawchunk_realtime(glpane, self)

                if self.hotspot is not None: # note, as of 050217 that can have side effects in getattr
                    self.overdraw_hotspot(glpane, disp) # only does anything for pastables as of 050316 (toplevel clipboard items)

                # russ 080409 Array to string formatting is slow, avoid it
                # when not needed.  Use !=, not ==, to compare Numeric arrays.
                # (!= returns V(0,0,0), a False boolean value, when equal.)
                if (should_not_change[0] != self.basecenter or
                    should_not_change[1] != self.quat):
                    assert `should_not_change` == `( + self.basecenter, + self.quat )`, \
                           "%r != %r, what's up?" % (should_not_change,
                                                     ( + self.basecenter, + self.quat))

                pass # end of drawing within self's local coordinate frame

            except:
                print_compact_traceback("exception in Chunk.draw, continuing: ")

            glPopMatrix()

            glPopName() # pops self.glname

            pass # end of 'if is_chunk_visible:'

        self._draw_outside_local_coords(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk.draw()

    def renderOverlayText(self, glpane):
        gotone = False
        for atom in self.atoms.itervalues():
            text = atom.overlayText
            if (text):
                gotone = True
                pos = atom.baseposn()
                radius = atom.drawing_radius() * 1.01
                pos = pos + glpane.out * radius
                glpane.renderTextAtPosition(pos, text)
        if (not gotone):
            self.chunkHasOverlayText = False

    def _draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible):
        #bruce 080520 split this out
        """
        Do the part of self.draw that goes outside self's
        local coordinate system and outside its display list.

        [Subclasses can extend this if needed.]
        """
        draw_external_bonds = True # piotr 080401
            # Added for the additional test - the external bonds could be still
            # visible even if the chunk is culled.

        # For extra performance, the user may skip drawing external bonds
        # entirely if the frustum culling is enabled. This may have some side
        # effects: problems in highlighting external bonds or missing 
        # external bonds if both chunks are culled. piotr 080402
        if debug_pref("GLPane: skip all external bonds for culled chunks",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True): 
            # the debug pref has to be checked first
            if not is_chunk_visible: # the chunk is culled piotr 080401
                # so don't draw external bonds at all
                draw_external_bonds = False

        # draw external bonds.

        # Could we skip this if display mode "disp" never draws bonds?
        # No -- individual atoms might override that display mode.
        # Someday we might decide to record whether that's true when recomputing externs,
        # and to invalidate it as needed -- since it's rare for atoms to override display modes.
        # Or we might even keep a list of all our atoms which override our display mode. ###e
        # [bruce 050513 comment]
        if draw_external_bonds and self.externs:
            self._draw_external_bonds(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk._draw_outside_local_coords()

    def _draw_external_bonds(self, glpane, disp, drawLevel, is_chunk_visible = True):
        """
        Draw self's external bonds (if debug_prefs and frustum culling permit).
        """
        if not drawbonds:
            return
        #bruce 080215 split this out, added one debug_pref
        
        # decide whether to draw any external bonds at all
        # (possible optim: decide once per redraw, cache in glpane)
        
        # piotr 080320: if this debug_pref is set, the external bonds 
        # are hidden whenever the mouse is dragged. this speeds up interactive 
        # manipulation of DNA segments by a factor of 3-4x in tubes
        # or ball-and-sticks display styles.
        # this extends the previous condition to suppress the external
        # bonds during animation.
        suppress_external_bonds = (
           (getattr(glpane, 'in_drag', False) # glpane.in_drag undefined in ThumbView
            and
            debug_pref("GLPane: suppress external bonds when dragging?",
                           Choice_boolean_False,
                           non_debug = True,
                           prefs_key = True
                           ))
           or 
           (self.assy.o.is_animating # review: test in self.assy.o or glpane?
            and
            debug_pref("GLPane: suppress external bonds when animating?",
                           Choice_boolean_False,
                           non_debug = True,
                           prefs_key = True
                           ))
         )
        
        if suppress_external_bonds:
            return
        
        # external bonds will be drawn (though some might be culled).
        # make sure the info needed to draw them is up to date.
        
        self._update_bonded_chunks()
        
        bondcolor = self.drawing_color()
        selColor = env.prefs[selectionColor_prefs_key]
        
        # decide whether external bonds should be frustum-culled.
        frustum_culling_for_external_bonds = \
            not is_chunk_visible and use_frustum_culling()
            # piotr 080401: Added the 'is_chunk_visible' parameter default to True
            # to indicate if the chunk is culled or not. Assume that if the chunk
            # is not culled, we have to draw the external bonds anyway. 
            # Otherwise, there is a significant performance hit for frustum
            # testing the visible bonds. 

        # find or set up repeated_bonds_dict
        
        # Note: to prevent objects (either external bonds themselves,
        # or ExternalBondSet objects) from being drawn twice,
        # [new feature, bruce 070928 bugfix and optimization]
        # we use a dict recreated each time their part gets drawn,
        # in case of multiple views of the same part in one glpane;
        # ideally the draw methods would be passed a "model-draw-frame"
        # instance (associated with the part) to make this clearer.
        # If we can ever draw one chunk more than once when drawing one part,
        # we'll need to modify this scheme, e.g. by optionally passing
        # that kind of object -- in general, a "drawing environment"
        # which might differ on each draw call of the same object.)
        model_draw_frame = self.part # kluge, explained above
            # note: that's the same as each bond's part.
        repeated_bonds_dict = model_draw_frame and model_draw_frame.repeated_bonds_dict
        del model_draw_frame
        if repeated_bonds_dict is None:
            # (Note: we can't just test "not repeated_bonds_dict",
            #  in case it's {}.)
            # This can happen when chunks are drawn in other ways than
            # via Part.draw (e.g. as Extrude mode repeat units),
            # or [as revised 080314] due to bugs in which self.part is None;
            # we need a better fix for this, but for now,
            # just don't use the dict. As a kluge to avoid messing up
            # the loop below, just use a junk dict instead.
            # [bruce 070928 fix new bug 2548]
            # (This kluge means that external bonds drawn by e.g. Extrude
            # will still be subject to the bug of being drawn twice.
            # The better fix is for Extrude to set up part.repeated_bonds_dict
            # when it draws its extra objects. We need a bug report for that.)
            repeated_bonds_dict = {} # KLUGE

        if debug_pref("GLPane: use ExternalBondSets for drawing?", #bruce 080707
                      Choice_boolean_False,
                          # won't be default True until it's not slower, & tested
                      non_debug = True,
                      prefs_key = True ):
            objects_to_draw = self._bonded_chunks.itervalues()
            use_outer_colorsorter = False
        else:
            objects_to_draw = self.externs
            use_outer_colorsorter = True
        
        # actually draw them

        if use_outer_colorsorter:
            ColorSorter.start(None)
                # [why is this needed? bruce 080707 question]
        
        for bond in objects_to_draw:
            # note: bond might be a Bond, or an ExternalBondSet
            if id(bond) not in repeated_bonds_dict:
                # BUG: disp and bondcolor depend on self, so the bond appearance
                # may depend on which chunk draws it first (i.e. on their Model
                # Tree order). How to fix this is the subject of a current design
                # discussion. [bruce 070928 comment]
                repeated_bonds_dict[id(bond)] = bond
                if frustum_culling_for_external_bonds:
                    # bond frustum culling test piotr 080401
                    ### REVIEW: efficient under all settings of debug_prefs?? [bruce 080702 question]
                    c1, c2, radius = bond.bounding_lozenge()
                    if not glpane.is_lozenge_visible(c1, c2, radius):
                        continue # skip the bond drawing if culled
                if bond.should_draw_as_picked():
                    color = selColor #bruce 080430 cosmetic improvement
                else:
                    color = bondcolor
                bond.draw(glpane, disp, color, drawLevel)
            continue
        
        if use_outer_colorsorter:
            ColorSorter.finish()
        
        return # from _draw_external_bonds

##    def _draw_selection_frame(self, glpane, delegate_selection_wireframe, hd): #bruce 060608 split this out of self.draw
##        "[private submethod of self.draw]"
##        if self.picked:
##            if not delegate_selection_wireframe:
##                try:
##                    drawlinelist(PickedColor, self.polyhedron or [])
##                except:
##                    # bruce 041119 debug code;
##                    # also "or []" failsafe (above)
##                    # in case recompute exception makes it None
##                    print_compact_traceback("exception in drawlinelist: ")
##                    print "(self.polyhedron is %r)" % self.polyhedron
##            else:
##                hd._f_drawchunk_selection_frame(glpane, self, PickedColor, highlighted = False)
##            pass
##        return

    def _indicate_overlapping_atoms(self): #bruce 080411
        """
        Draw indicators around all atoms that overlap (or are too close to)
        other atoms (in self or in other chunks).
        """
        model_draw_frame = self.part # kluge, explained elsewhere in this file
        if not model_draw_frame:
            return
        neighborhoodGenerator = model_draw_frame._f_state_for_indicate_overlapping_atoms
        for atom in self.atoms.itervalues():
            pos = atom.posn()
            prior_atoms_too_close = neighborhoodGenerator.region(pos)
            if prior_atoms_too_close:
                # This atom overlaps the prior atoms.
                # Draw an indicator around it,
                # and around the prior ones if they don't have one yet.
                # (That can be true even if there is more than one of them,
                #  if the prior ones were not too close to each other,
                #  so for now, just draw it on the prior ones too, even
                #  though this means drawing it twice for each atom.)
                #
                # Pass an arg which indicates the atoms for which one or more
                # was too close. See draw_overlap_indicator docstring for more
                # about how that can be used, given our semi-symmetrical calls.
                for prior_atom in prior_atoms_too_close:
                    prior_atom.draw_overlap_indicator((atom,))
                atom.draw_overlap_indicator(prior_atoms_too_close)
            neighborhoodGenerator.add(atom)
            continue
        return

    def _draw_for_main_display_list(self, glpane, disp0, hd_info, wantlist):
        """
        [private submethod of self.draw]

        Draw the contents of our main display list, which the caller
        has already opened for compile and execute (or the equivalent,
        if it's a ColorSortedDisplayList object) if wantlist is true,
        or doesn't want to open otherwise (so we do immediate mode
        drawing then).

        Also (if self attrs permit and wantlist argument is true)
        capture functions for deferred drawing into new instances
        of appropriate subclasses of ExtraChunkDisplayList added to
        self.extra_displists, so that some aspects of our atoms and bonds
        can be drawn from separate display lists, to avoid remaking our
        main one whenever those need to change.
        """
        if wantlist and \
            hasattr(glpane, 'graphicsMode') and \
            debug_pref("use special_drawing_handlers?",
                                   Choice_boolean_True, #bruce 080606 enable by default for v1.1
                                   non_debug = True,    # (but leave it visible in case of bugs)
                                   prefs_key = True):
            # set up the right kind of special_drawing_handler for self;
            # this will be passed to the draw calls of our atoms and bonds
            # [new feature, bruce 080605]
            #
            # bugfix [bruce 080606 required for v1.1, for dna in partlib view]:
            # hasattr test, since ThumbView has no graphicsMode.
            # (It ought to, but that's a refactoring too big for this release,
            #  and giving it a fake one just good enough for this purpose doesn't
            #  seem safe enough.)
            special_drawing_classes = { # todo: move into a class constant
                SPECIAL_DRAWING_STRAND_END: SpecialDrawing_ExtraChunkDisplayList,
             }
            self.special_drawing_handler = \
                    Chunk_SpecialDrawingHandler( self, special_drawing_classes )
        else:
            self.special_drawing_handler = None
        del wantlist

        #bruce 050513 optimizing this somewhat; 060608 revising it
        if debug_pref("GLPane: report remaking of chunk display lists?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True ): #bruce 080214
            print "debug fyi: remaking display lists for chunk %r" % self
            summary_format = graymsg( "debug fyi: remade display lists for [N] chunk(s)" )
            env.history.deferred_summary_message(summary_format)

        hd, delegate_draw_atoms, delegate_draw_chunk = hd_info

        # draw something for the chunk as a whole
        if delegate_draw_chunk:
            hd._f_drawchunk(self.glpane, self)
        else:
            self.standard_draw_chunk(glpane, disp0)

        # draw the individual atoms and internal bonds (if desired)
        if delegate_draw_atoms:
            pass # nothing for this is implemented, or yet needed [as of bruce 060608]
        else:
            self.standard_draw_atoms(glpane, disp0)
        return

    def highlight_color_for_modkeys(self, modkeys):
        """
        This is used to return a highlight color for the chunk highlighting. 
        See a comment in this method below
        """
        #NOTE: before 2008-03-13, the chunk highlighting was achieved by 
        #using the atoms and bonds within the chunk. The Atom and Bond classes
        #have their own glselect name, so the code was able to recognize them 
        #as highlightable objects and then depending upon the graphics mode 
        #the user was in, it used to highlight the whole chunk by accessing the
        #chunk using, for instance, atom.molecule. although this is still 
        #implemented, for certain display styles such as DnaCylinderChunks, the 
        #atoms and bonds are never drawn. So there is no way to access the 
        #chunk! To fix this, we need to make chunk a highlightable object. 
        #This is done by making sure that the chunk gets a glselect name and 
        #by defining this API method - Ninad 2008-03-13

        return env.prefs[hoverHighlightingColor_prefs_key]

    def draw_highlighted(self, glpane, color):
        """
        Draws this chunk as highlighted with the specified color. 
        In future 'draw_in_abs_coords' defined on some node classes
        could be merged into this method (for highlighting various objects).

        @param: GLPane object
        @param color: The highlight color
        @see: dna_model.DnaGroup.draw_highlighted
        @see: SelectChunks_GraphicsMode.drawHighlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()

        """

        #This was originally a sub-method in 
        #SelectChunks_GraphicsMode.drawHighlightedChunks. Moved here 
        #(Chunk.draw_highlighted on 2008-02-26

        # Early frustum clipping test. piotr 080331
        # Could it cause any trouble by not drawing the external bonds?
        if not glpane.is_sphere_visible(self.bbox.center(), self.bbox.scale()):
            return

        # Note: bool_fullBondLength represent whether full bond length is to be
        # drawn. It is used only in select Chunks mode while highlighting the 
        # whole chunk and when the atom display is Tubes display -- ninad 070214
        # UPDATE: Looks like this flag is always True in this method. 
        # may be an effect of an earlier refactoring (note that original comment 
        # as above was written over an year ago). -- Ninad 2008-02-26
        bool_fullBondLength = True

        draw_bonds_only_once = debug_pref(
            "GLPane: drawHighlightedChunk draw bonds only once?",
            Choice_boolean_True )
            # turn off to test effect of this optimization;
            # when testing is done, hardcode this as True
            # [bruce 080217]

            # [note, bruce 080314: this optimization got much less effective
            #  after this code was turned into a Chunk method, since it no
            #  longer prevents external bonds from being drawn twice,
            #  which is probably common when highlighting DNA. To fix,
            #  a dictionary of already drawn bonds should be passed in
            #  or found somewhere. See references in this module to
            #  self.part.repeated_bonds_dict for related code (but to use
            #  that dict directly, different caller setup would be required
            #  than is done now).]

        drawn_bonds = {}

        if drawing_globals.allow_color_sorting and drawing_globals.use_color_sorted_dls:

            # russ 080530: Support for patterned highlighting drawing modes.
            patterned = startPatternedDrawing(highlight = True)

            # Russ 081212: Switch from glCallList to CSDL.draw for shader prims.
            if self.__dict__.has_key('displist'):
                apply_material(color)
                self.pushMatrix()
                for csdl in ([self.displist] +
                             [ed.csdl for ed in self.extra_displists.values()]):
                    csdl.draw(highlighted = True, highlight_color = color)
                self.popMatrix()
                pass

            # piotr 080521: Get display mode for drawing external bonds and/or
            # the "realtime" objects.
            disp = self.get_dispdef(glpane)

            #russ 080302: Draw external bonds.
            if self.externs:
                # From Chunk.draw().
                drawLevel = self.assy.drawLevel
                # From Chunk._draw_external_bonds
                ColorSorter.start(None)
                for bond in self.externs:
                    bond.draw(glpane, disp, color, drawLevel)
                    continue
                ColorSorter.finish()
                pass
            pass

            # piotr 080521
            # Highlight "realtime" objects (e.g. 2D DNA cylinder style).
            hd = get_display_mode_handler(disp)
            if hd:
                hd._f_drawchunk_realtime(glpane, self, highlighted = True)
                pass

            # russ 080530: Support for patterned highlighting drawing modes.
            if patterned:
                endPatternedDrawing(highlight = True)
            
        else:
            if self.get_dispdef() == diDNACYLINDER or \
               self.get_dispdef() == diPROTEIN:
                #If the chunk is drawn with the DNA cylinder display style, 
                #then do not use the following highlighting code (which 
                #highlights individual bonds and atoms) . When color sorter
                #is enabled by default, the following code (else condition)
                #can be removed. The DnaCylinder display , use the 
                #display list and such chunks will be highlighted only when
                #the color sorter and use displist debug pref are enabled. 
                # --Ninad 2008-03-13
                # piotr 080709: Added a condition check for reduced protein
                # display style.
                return

            for atom in self.atoms.itervalues():
                # draw atom and its (not yet drawn) bonds
                atom.draw_in_abs_coords(glpane, 
                                        color, 
                                        useSmallAtomRadius = True)
                for bond in atom.bonds:
                    if draw_bonds_only_once:
                        if drawn_bonds.has_key(id(bond)):
                            continue # to next bond
                        drawn_bonds[id(bond)] = bond
                        pass
                    bond.draw_in_abs_coords(glpane,
                                            color, 
                                            bool_fullBondLength)
                    continue
                continue
            pass

        if 0: ## Debugging print.
            print ("Highlighting %s, dl's %r" %
                   (self.name,
                    # Best to list in order of allocation by glGenLists.
                    ([dl for color, dl in self.displist.per_color_dls],
                     self.displist.color_dl,
                     self.displist.nocolor_dl,
                     self.displist.selected_dl)))
            if self.extra_displists:
                print " note: %s also has extra_displists %r; printing their dls is nim" % \
                      (self.name, self.extra_displists.values())
            pass

        return

    def standard_draw_chunk(self, glpane, disp0, highlighted = False):
        """
        [private submethod of self.draw:]
        
        Draw the standard representation of this chunk as a whole
        (except for chunk selection wireframe),
        as if self's display mode was disp0;
        this occurs inside our local coordinate system and display-list-making,
        and it doesn't occur if chunk drawing is delegated to our display mode.

        @note: as of 080605 nothing is ever drawn for a chunk as a whole,
               so this method does nothing (in this class or any subclass).
               That might change, e.g. if we made chunks able to show their
               axes, name, bbox, etc.
        """
        #bruce 060608 split this out of _draw_for_main_display_list
        return

    def drawing_color(self): #bruce 080210 split this out, used in Atom.drawing_color
        """
        Return the color tuple to use for drawing self, or None if
        per-atom colors should be used.
        """
        if self.picked and not (drawing_globals.allow_color_sorting and drawing_globals.use_color_sorted_dls):
            #bruce disable this case when using drawing_globals.use_color_sorted_dls
            # since they provide a better way (fixes "stuck green" bug.)

            #ninad070405 Following draws the chunk as a colored selection 
            #(if selected)
            #bruce 080210 possible appearance change:
            # this now also affects Atom.drawing_color
            # (but it's unclear whether that ever affects color
            #  of external bonds -- apparently not, in my tests)
            color = env.prefs[selectionColor_prefs_key]
        else:
            color = self.color # None or a color
        color = self.modify_color_for_error(color)
            # no change in color if no error
        return color

    def modify_color_for_error(self, color):
        """
        [overridden in some subclasses]
        """
        return color

    def standard_draw_atoms(self, glpane, disp0): #bruce 060608 split this out of _draw_for_main_display_list
        """
        [private submethod of self.draw:]
        
        Draw all our atoms and all their internal bonds, in the standard way,
        *including* atom selection wireframes, as if self's display mode was disp0;
        this occurs inside our local coordinate system and display-list-making;
        it doesn't occur if atom drawing is delegated to our display mode.
        """
        drawLevel = self.assy.drawLevel
        drawn = {}
        ## self.externs = [] # bruce 050513 removing this
        # bruce 041014 hack for extrude -- use _colorfunc if present [part 1; optimized 050513]
        _colorfunc = self._colorfunc # might be None [as of 050524 we supply a default so it's always there]
        _dispfunc = self._dispfunc #bruce 060411 hack for BorrowerChunk, might be more generally useful someday

        atomcolor = self.drawing_color() # None or a color
            # bruce 080210 bugfix (predicted) [part 1 of 2]:
            # use this even when _colorfunc is being used
            # (so chunk colors work in Extrude; IIRC there was a bug report on that)
            # [UNTESTED whether that bug exists and whether this fixes it]

        bondcolor = atomcolor # never changed below

        for atom in self.atoms.itervalues(): #bruce 050513 using itervalues here (probably safe, speed is needed)
            try:
                color = atomcolor # might be modified before use
                disp = disp0 # might be modified before use
                # bruce 041014 hack for extrude -- use _colorfunc if present [part 2; optimized 050513]
                if _colorfunc is not None:
                    try:
                        color = _colorfunc(atom) # None or a color
                    except:
                        print_compact_traceback("bug in _colorfunc for %r and %r: " % (self, atom)) #bruce 060411 added errmsg
                        _colorfunc = None # report the error only once per displist-redraw
                        color = None
                    else:
                        if color is None:
                            color = atomcolor
                                # bruce 080210 bugfix (predicted) [part 2 of 2]
                        #bruce 060411 hack for BorrowerChunk; done here and in this way in order to not make
                        # ordinary drawing inefficient, and to avoid duplicating this entire method:
                        if _dispfunc is not None:
                            try:
                                disp = _dispfunc(atom)
                            except:
                                print_compact_traceback("bug in _dispfunc for %r and %r: " % (self, atom))
                                _dispfunc = None # report the error only once per displist-redraw
                                disp = disp0 # probably not needed
                                pass
                            pass
                        pass
                    pass
                # otherwise color and disp remain unchanged

                # end bruce hack 041014, except for use of color rather than
                # self.color in atom.draw (but not in bond.draw -- good??)

                atomdisp = atom.draw(
                    glpane, disp, color, drawLevel,
                    special_drawing_handler = self.special_drawing_handler
                 )

                #bruce 050513 optim: if self and atom display modes don't need to draw bonds,
                # we can skip drawing bonds here without checking whether their other atoms
                # have their own display modes and want to draw them,
                # since we'll notice that when we get to those other atoms
                # (whether in self or some other chunk).
                # (We could ask atom.draw to return a flag saying whether to draw its bonds here.)
                #    To make this safe, we'd need to not recompute externs here,
                # but that should be ok since they're computed separately anyway now.
                # So I'm removing that now, and doing this optim.
                ###e (I might need to specialcase it for singlets so their bond-valence number is still drawn...)
                # [bruce 050513]
                #bruce 080212: this optim got a lot less effective since a few CPK bonds
                # are now also drawn (though most are not).

                if atomdisp in (diBALL, diLINES, diTUBES, diTrueCPK, diDNACYLINDER):
                    # todo: move this tuple into bonds module or Bond class
                    for bond in atom.bonds:
                        if id(bond) not in drawn:
                            ## if bond.other(atom).molecule != self: could be faster [bruce 050513]:
                            if bond.atom1.molecule is not self or bond.atom2.molecule is not self:
                                pass ## self.externs.append(bond) # bruce 050513 removing this
                            else:
                                # internal bond, not yet drawn
                                drawn[id(bond)] = bond
                                bond.draw(glpane, disp, bondcolor, drawLevel,
                                          special_drawing_handler = self.special_drawing_handler
                                          )  
            except:
                # [bruce 041028 general workaround to make bugs less severe]
                # exception in drawing one atom. Ignore it and try to draw the
                # other atoms. #e In future, draw a bug-symbol in its place.
                print_compact_traceback("exception in drawing one atom or bond ignored: ")
                # (this might mean some externs are missing; never mind that for now.) [bruce 050513 -- not anymore]
                try:
                    print "current atom was:", atom
                except:
                    print "current atom was... exception when printing it, discarded"
                try:
                    atom_source = atom._source # optional atom-specific debug info
                except AttributeError:
                    pass
                else:
                    print "Source of current atom:", atom_source
        return # from standard_draw_atoms (submethod of _draw_for_main_display_list)

    def overdraw_hotspot(self, glpane, disp): #bruce 050131
        """
        If this chunk is a (toplevel) clipboard item with a hotspot
        (i.e. if pasting it onto a bond will work and use its hotspot),
        display its hotspot in a special form.
        As with selatom, we do this outside of the display list.        
        """
        if self._should_draw_hotspot(glpane):
            hs = self.hotspot
            try:
                color = env.prefs[bondpointHotspotColor_prefs_key] #bruce 050808

                level = self.assy.drawLevel #e or always use best level??
                ## code copied from selatom.draw_as_selatom(glpane, disp, color, level)
                pos1 = hs.baseposn()
                drawrad1 = hs.highlighting_radius(disp)
                ## drawsphere(color, pos1, drawrad1, level) # always draw, regardless of disp
                hs.draw_atom_sphere(color, pos1, drawrad1, level, None, abs_coords = False)
                    #bruce 070409 bugfix (draw_atom_sphere); important if it's really a cone
            except:
                print_compact_traceback("atom_debug: ignoring exception in overdraw_hotspot %r, %r: " % (self, hs))
                pass
            pass
        return

    def _should_draw_hotspot(self, glpane): #bruce 080723 split this out, cleaned it up
        """
        Determine whether self has a valid hotspot and wants to draw it specially.
        """
        # bruce 050416 warning: the conditions here need to match those in depositMode's
        # methods for mentioning hotspot in statusbar, and for deciding whether a clipboard
        # item is pastable. All this duplicated hardcoded conditioning is bad; needs cleanup. #e
        
        # We need these checks because some code removes singlets from a chunk (by move or kill)
        # without checking whether they are that chunk's hotspot.

        # review/cleanup: some of these checks might be redundant with checks
        # in the get method run by accessing self.hotspot.
            
        hs = self.hotspot ### todo: move lower, after initial tests

        wanted = (self in self.assy.shelf.members) or glpane.always_draw_hotspot
            #bruce 060627 added always_draw_hotspot re bug 2028
        if not wanted:
            return False

        if hs is None:
            return False
        if not hs.is_singlet():
            return False
        if not hs.key in self.atoms:
            return False
        return True

    # == methods related to mmp format (reading or writing)

    def readmmp_info_chunk_setitem( self, key, val, interp ): #bruce 050217, renamed 050421
        """
        This is called when reading an mmp file, for each "info chunk" record.
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
            self.setcolor(color, repaint_in_MT = False)
        elif key == ['display_as_pam']:
            # val should be one of the strings "", MODEL_PAM3, MODEL_PAM5;
            # if not recognized, use ""
            if val not in ("", MODEL_PAM3, MODEL_PAM5):
                print "fyi: info chunk display_as_pam with unrecognized value %r" % (val,) # deferred_summary_message?
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
                print "fyi: info chunk save_as_pam with unrecognized value %r" % (val,) # deferred_summary_message?
                val = ""
            self.save_as_pam = val
        else:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info chunk with unrecognized key %r" % (key,)
        return

    def atoms_in_mmp_file_order(self, mapping = None):
        """
        Return a list of our atoms, in the same order as they would be written
        to an mmp file produced for the given mapping (none by default)
        (which is the same order in which they occurred in one,
         *if* they were just read from one, at least for this class's
         implem of this method).

        We know it's the same order as they'd be written, since self.writemmp()
        calls this method. (Subclasses are permitted to override this method
         in order to revise the order. This can help optimize mmp writing and
         reading. It does have effects in the code when the atoms are read,
         but these are usually unimportant.)

        We know it's the same order they were just read in (if they were just
        read), since it's the order of atom.key, which is assigned successive
        values (guaranteed to sort in order) as atoms are read from the file
        and created for use in this session.

        @param mapping: writemmp_mapping being used for the writing process,
                        or None if this is not being used for mmp writing.
                        This can affect the set of atoms (and in principle,
                        their order) due to conversions requested by the
                        mapping, e.g. PAM3 -> PAM5.
        @type mapping: an instance of class writemmp_mapping, or None.

        [subclasses can override this, as described above]
        """
        #bruce 050228; revised docstring and added mapping arg, 080321
        del mapping
        # as of 060308 atlist is also sorted (so equals res), but we don't want
        # to recompute it and atpos and basepos just due to calling this. Maybe
        # that's silly and this should just return self.atlist,
        # or at least optim by doing that when it's in self.__dict__. ##e
        pairs = self.atoms.items() # key, val pairs; keys are atom.key,
            # which is an int which counts from 1 as atoms are created in one
            # session, and which is (as of now, 050228) specified to sort in
            # order of creation even if we later change the kind of value it
            # produces.
        pairs.sort()
        res = [atom for key, atom in pairs]
        return res

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """
        [overrides Node.writemmp]
        """
        disp = mapping.dispname(self.display)
        mapping.write("mol (" + mapping.encode_name(self.name) + ") " + disp + "\n")
        self.writemmp_info_leaf(mapping)
        self.writemmp_info_chunk_before_atoms(mapping)
        #bruce 050228: write atoms in the same order they were created in,
        # so as to preserve atom order when an mmp file is read and written
        # with no atoms created or destroyed and no chunks reordered, thus
        # making previously-saved movies more likely to retain their validity.
        # (Due to the .dpb format not storing its own info about atom identity.)
        #bruce 080327 update:
        # Note: these "atoms" can be of class Atom or class Fake_Pl.
        #bruce 080328: for some of the atoms, let subclasses write all
        # their bonds separately, in a more compact form.
        compact_bond_atoms = \
                           self.write_bonds_compactly_for_these_atoms(mapping)
        for atom in self.atoms_in_mmp_file_order(mapping):
            atom.writemmp(mapping,
                          dont_write_bonds_for_these_atoms = compact_bond_atoms)
                # note: this writes internal and/or external bonds,
                # after their 2nd atom is written, unless both their
                # atoms are in compact_bond_atoms. It also writes
                # bond_directions records as needed for the bonds
                # it writes.
        if compact_bond_atoms: # (this test is required)
            self.write_bonds_compactly(mapping)
        self.writemmp_info_chunk_after_atoms(mapping)
        return

    def writemmp_info_chunk_before_atoms(self, mapping): #bruce 080321
        """
        Write whatever info chunk records need to be written before our atoms
        (since their value, during mmp read, might be needed when reading the
        atoms or their bonds).

        [subclasses should override this as needed]
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

    def write_bonds_compactly_for_these_atoms(self, mapping): #bruce 080328
        """
        If self plans to write some of its atoms' bonds compactly
        when self.write_bonds_compactly is called
        (possibly based on options in mapping),
        then return a dictionary of atom.key  -> atom for those
        atoms. Otherwise return {}.

        [subclasses that can do this should override this method
         and write_bonds_compactly in corresponding ways.]
        """
        del mapping
        return {}

    def writemmp_info_chunk_after_atoms(self, mapping): #bruce 080321 split this out
        """
        Write whatever info chunk records should be written after our atoms
        and our internal bonds, or any other info chunk records not written
        by writemmp_info_chunk_before_atoms.

        [subclasses should override this as needed]
        """
        #bruce 050217 new feature [see also a comment added to files_mmp.py]:
        # also write the hotspot, if there is one.
        hs = self.hotspot # uses getattr to validate it
        if hs:
            # hs is a valid hotspot in this chunk, and was therefore one of the
            # atoms just written by the caller, and therefore should have an
            # encoding already assigned for the current mmp file:
            hs_num = mapping.encode_atom(hs)
            assert hs_num is not None
            mapping.write("info chunk hotspot = %s\n" % hs_num)
        if self.color:
            r = int(self.color[0]*255 + 0.5)
            g = int(self.color[1]*255 + 0.5)
            b = int(self.color[2]*255 + 0.5)
            mapping.write("info chunk color = %d %d %d\n" % (r, g, b))
        return

    def write_bonds_compactly(self, mapping): #bruce 080328
        """
        If self returned (or would return) some atoms from
        self.write_bonds_compactly_for_these_atoms(mapping),
        then write all bonds between atoms in that set
        into mapping in a compact form.

        @note: this should only be called if self did, or would,
               return a nonempty set of atoms from that method,
               self.write_bonds_compactly_for_these_atoms(mapping).

        [subclasses that can do this should override this method
         and write_bonds_compactly_for_these_atoms in corresponding ways.]
        """
        assert 0, "subclasses which need this must override it"

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
        col = self.color
        for a in self.atoms.values(): 
            a.writemdl(alist, f, disp, self.color)

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
        # self.changed_basecenter_or_quat_to_move_atoms() might not be able to reconstruct it.
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
        self.changed_basecenter_or_quat_to_move_atoms()

    def pivot(self, point, q):
        """
        Public method: pivot the Chunk self around point by quaternion q;
        do all necessary invalidations, but optimize those based on
        self's relative structure not having changed. See also self.rot().
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
        """
        (private method) like changed_basecenter_or_quat_to_move_atoms but we also might have changed basepos
        """
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
        """
        Private method:
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

        # record the fact that the model will have changed by the time we return
        # [bruce 071102 -- fixes bug 2576 and perhaps analogous bugs;
        #  note that traditionally these calls have been left up to the
        #  user event handlers, so most of the Node changing methods that
        #  ought to do them probably don't do them.]
        self.changed() # Node method

        # imitate the recomputes done by _recompute_atpos
        self.atpos = self.basecenter + self.quat.rot(self.basepos) # inlines base_to_abs
        self.set_atom_posns_from_atpos( self.atpos) #bruce 060308
        # no change in atlist; no change needed in our atoms' .index attributes
        # no change here in basepos or bbox (if caller changed them, it should
        # call changed_attr itself, or it should invalidate bbox itself);
        # but changes here in whatever depends on atpos, aside from those.
        self.changed_attr('atpos', skip = ('bbox', 'basepos'))

        # we've moved one end of each external bond, so invalidate them...
        # [bruce 050516 comment (95% sure it's right): note that we don't, and need not, inval internal bonds]
        for bond in self.externs:
            bond.setup_invalidate()
        return

    def set_atom_posns_from_atpos(self, atpos): #bruce 060308; revised 060313
        """
        Set our atom's positions en masse from the given array, doing no chunk or bond invals
        (caller must do whichever invals are needed, which depends on how the positions changed).
        The array must be in the same order as self.atpos (its typical value, but we won't depend
        on that and won't access or modify self.atpos) and self.atlist (which must already exist).
        """
        assert self.__dict__.has_key('atlist')
        atlist = self.atlist
        assert len(atlist) == len(atpos)
        for i in xrange(len(atlist)):
            atlist[i]._setposn_no_chunk_or_bond_invals( atpos[i] )
        return

    def base_to_abs(self, anything): # bruce 041115
        """
        map anything (which is accepted by quat.rot() and Numeric.array's '+' method)
        from Chunk-relative coords to absolute coords;
        guaranteed to never recompute basepos/atpos or modify the mol-relative
        coordinate system it uses. Inverse of abs_to_base.
        """
        return self.basecenter + self.quat.rot( anything)

    def abs_to_base(self, anything): # bruce 041201
        """
        map anything (which is accepted by quat.unrot() and Numeric.array's '-' method)
        from absolute coords to mol-relative coords;
        guaranteed to never recompute basepos/atpos or modify the mol-relative
        coordinate system it uses. Inverse of base_to_abs.
        """
        return self.quat.unrot( anything - self.basecenter)

    def set_basecenter_and_quat(self, basecenter, quat):
        """
        Deprecated public method: change this Chunk's basecenter and quat to the specified values,
        as a way of moving the Chunk's atoms.
        It's deprecated since basecenter and quat are replaced by in-principle-arbitrary values
        every time certain recomputations are done, but this method is only useful if the caller
        knows what they are, and computes the new ones it wants relative to what they are.
        So it's much better to use mol.pivot instead (or some combo of move, rot, and pivot).
        """
        # [written by bruce for extrude; moved into class Chunk by bruce 041104]
        # modified from mol.move and mol.rot as of 041015 night
        self.basepos # bruce 050315 bugfix: recompute this if it's currently invalid!
        # make sure mol owns its new basecenter and quat,
        # since it might destructively modify them later!
        self.basecenter = V(0,0,0) + basecenter
        self.quat = Q(1,0,0,0) + quat #e +quat might be correct and faster... don't know; doesn't matter much
        self.bbox = None
        del self.bbox #e could optimize if quat is not changing
        self.changed_basecenter_or_quat_to_move_atoms()

    def getaxis(self):
        return self.quat.rot(self.axis)

    def setcolor(self, color, repaint_in_MT = True):
        """
        change self's color to the specified color. A color of None
        means self's atoms are drawn with their element colors.

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
            # warning: some callers (ChunkProp.py) first trash self.color, then call us to bless it. [bruce 050505 comment]
        self.havelist = 0
        self.changed()
        if repaint_in_MT and pref_show_node_color_in_MT():
            #bruce 080507, mainly for testing new method repaint_some_nodes
            self.assy.win.mt.repaint_some_nodes([self])
        return

    def setDisplayStyle(self, disp): #bruce 080910 renamed from setDisplay
        # TODO: optimize when self.display == disp, since I just reviewed
        # all calls and this looks safe. (Ditto with Atom version of this
        # method.) [bruce comment 080305 @@@@]
        """
        Set self's display style.
        """
        if self.display == disp:
            #bruce 080305 optimization; looks safe after review of all calls;
            # important (due to avoiding inlined changeapp and display list
            # remake) if user selects several chunks and changes them all
            # at once, and some are already set to disp.
            return

        self.display = disp
        # inlined self.changeapp(1):
        self.havelist = 0
        self.haveradii = 0
        self.changed()
        return

    def getDisplayStyle(self):
        """
        Return the display style set on self (and not the one supplied from 
        self's environment (i.e. the glpane) when self's display style is set to 
        to diDEFAULT).
        
        Use get_dispdef to obtain the display style set by self or self's 
        environment when self's display style is set to diDEFAULT.
        
        @note: self's display style used to draw self can differ from  
        self.display not only if it's diDEFAULT, but due to some special cases 
        in get_dispdef based on the type of chunk.
        
        @see: L{get_dispdef()}
        """
        return self.display
    
    def show_invisible_atoms(self):
        """
        Resets the display mode for each invisible (diINVISIBLE) atom 
        to diDEFAULT display mode, making them visible again.
        It returns the number of invisible atoms found.
        """
        n = 0
        for a in self.atoms.itervalues():
            if a.display == diINVISIBLE: 
                a.setDisplayStyle(diDEFAULT)
                n += 1
        return n

    def set_atoms_display(self, display):
        """
        Changes the display setting to 'display' for all atoms in this chunk.
        It returns the number of atoms which had their display mode changed.
        """
        n = 0
        for a in self.atoms.itervalues():
            if a.display != display:
                a.setDisplayStyle(display)
                n += 1
        return n

    glpane = None #bruce 050804

    def changeapp(self, atoms):
        """
        call when you've changed appearance of self
        (but you don't need to call it if only the external bonds look different).
        Arg atoms = 1 means that not only the entire mol appearance,
        but specifically the set of atoms or atomic radii
        (for purposes of selection), have changed.
           Note that changeapp does not itself call self.assy.changed(),
        since that is not always correct to do (e.g., selecting an atom
        should call changeapp(), but not assy.changed(), on its chunk aka .molecule).
        """ 
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
        glpane = self.glpane # the last glpane that drew this chunk, or None if it was never drawn
            # (if more than one can ever draw it at once, this code needs to be revised to scan them all ##k)
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

    def natoms(self): #bruce 060215
        """
        Return number of atoms (real atoms or bondpoints) in self.
        """
        return len(self.atoms)
    
    def getToolTipInfo(self):
        """
        Return the tooltip string for this chunk
        """
        #As of 2008-11-09, this is only implemented for a DnaStrand.
        strand =  self.getDnaStrand()
        toolTipInfoString = ''
        if strand:
            toolTipInfoString = strand.getDefaultToolTipInfo()   
            return toolTipInfoString
        
        segment = self.getDnaSegment()
        if segment:
            toolTipInfoString = segment.getDefaultToolTipInfo()
                    
        return toolTipInfoString
                    

    def getinfo(self):
        # Return information about the selected chunk for the msgbar [mark 2004-10-14]

        if self is self.assy.ppm: return

        ele2Num = {}

        # Determine the number of element types in this Chunk.
        for a in self.atoms.values():
            if not ele2Num.has_key(a.element.symbol): ele2Num[a.element.symbol] = 1 # New element found
            else: ele2Num[a.element.symbol] += 1 # Increment element

        # String construction for each element to be displayed.
        natoms = self.natoms() # number of atoms in the chunk
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

        natoms -= nsinglets   # The number of real atoms in this chunk

        minfo =  "Chunk Name: [" + str (self.name) + "]     Total Atoms: " + str(natoms) + " " + einfo

        # ppm is self for next mol picked.
        self.assy.ppm = self

        return minfo

    def getstatistics(self, stats):
        """
        Adds the current chunk, including number of atoms 
        and singlets to part stats.
        """
        stats.nchunks += 1
        stats.natoms += self.natoms()
        for a in self.atoms.itervalues():
            if a.element.symbol == "X": stats.nsinglets +=1

    def pickatoms(self): # mark 060211. Could use a complementary unpickatoms() method. [not referring to the one in ops_select --bruce]
        """
        Pick the atoms of self not already picked. Return the number of newly picked atoms.
        [overrides Node method]
        """
        self.assy.permit_pick_atoms()
        npicked = 0
        for a in self.atoms.itervalues():
            if not a.is_singlet():
                if not a.picked:
                    a.pick()
                    if a.picked: 
                        # Just in case it didn't get picked due to a selection filter.
                        npicked += 1
        return npicked

    def pick(self):
        """
        select self

        [extends Node method]
        """
        if not self.picked:
            if 0: #bruce 080502 debug code for rapid click bug; keep this for awhile
                print_compact_stack( "debug fyi: chunk.pick picks %r: " % self)

            if self.assy is not None:
                self.assy.permit_pick_parts() #bruce 050125 added this... hope it's ok! ###k ###@@@
                # (might not be needed for other kinds of leaf nodes... not sure. [bruce 050131])
            _superclass.pick(self)
            #bruce 050308 comment: _superclass.pick (Node.pick) has ensured that we're in the current selection group,
            # so it's correct to append to selmols, *unless* we recompute it now and get a version
            # which already contains self. So, we'll maintain it iff it already exists.
            # Let the Part figure out how best to do this.
            # [bruce 060130 cleaned this up, should be equivalent]
            if self.part:
                self.part.selmols_append(self)

            ##Earlier comment from Bruce (when chunk was selected as a 'wireframe' 
            ##instead of a colored selection -- ninad 070406)
            # bruce 041207 thinks self.havelist = 0 is no longer needed here,
            # since self.draw uses self.picked outside of its display list,
            # so I'm removing that! This might speed up some things.

            #@@@ ninad 070406: enabled reset of 'havelist' to permit chunk picking 
            #as a colored selection. (the selected chunk is shown in 'green color')
            #earlier I was using the same code as used for highlighting a chunk 
            #but it was slow. Enabling the 'havelist reset' speeds up the selection 
            #based on my tests. (Selecting chunks in Pump.mmp is about 
            #1.5 seconds faster using display list than drawing using the code that 
            #is used to highlight the chunk.)
            #Note: There needs to be a user preference that will allow user to 
            # select the chunk as a wireframe --  ninad

            if (drawing_globals.allow_color_sorting and drawing_globals.use_color_sorted_dls):
                # russ 080303: Back again to display lists, this time color-sorted.
                self.displist.selectPick(True)
                    # shouldn't be needed for self.extra_displists, due to how they're drawn
            else:
                self.havelist = 0
            pass

        return

    def unpick(self):
        """
        unselect self

        [extends Node method]
        """
        if self.picked:
            _superclass.unpick(self)
            # bruce 050308 comment: following probably needs no change for assy/part.
            # But we'll let the Part do it, so it needn't remake selmols if not made.
            # But in case the code for assy.part is not yet committed, check that first:
            # [bruce 060130 cleaned this up, should be equivalent]            
            if self.part:
                self.part.selmols_remove(self)

            ##Earlier comment from Bruce (when chunk was selected as a 'wireframe' 
            ##instead of a colored selection -- ninad 070406)
            # bruce 041207 thinks self.havelist = 0 is no longer needed here
            # (see comment in self.pick).

            #@@@ ninad 070406: enabled 'havelist reset' to permit chunk unpicking 
            #which was selected as a colored selection
            #(the selected chunk is shown in 'green color').
            # See also comments in 'def pick'... this sped up deselection
            # of the same example mentioned there by about 1.5-2 seconds.

            if (drawing_globals.allow_color_sorting and
                drawing_globals.use_color_sorted_dls):
                # russ 080303: Back again to display lists, this time color-sorted.
                self.displist.selectPick(False)
                    # shouldn't be needed for self.extra_displists, due to how they're drawn
            else:
                self.havelist = 0
            pass

        return

    def getAxis_of_self_or_eligible_parent_node(self, atomAtVectorOrigin = None):
        """
        Return the axis of a parent node such as a DnaSegment or a Nanotube 
        segment or a dna segment of a DnaStrand. If one doesn't exist, 
        return the self's axis.
        @param atomAtVectorOrigin: If the atom at vector origin is specified, 
            the method will try to return the axis vector with the vector
            start point at the this atom's center. 
        @type atomAtVectorOrigin: B{Atom}
        @see:
        """
        #@TODO: refactor this. MEthod written just before FNANO08 for a critical
        #NFR. (this code is not a part of Rattlesnake rc2)
        #- Ninad 2008-04-17
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

        nanotube = self.parent_node_of_class(self.assy.NanotubeSegment)
        if nanotube:
            axisVector = nanotube.getAxisVector(atomAtVectorOrigin = atomAtVectorOrigin)
            if axisVector is not None:
                return axisVector, nanotube

        #If no eligible parent node with an axis is found, return self's 
        #axis.
        return self.getaxis(), self


    def is_glpane_content_itself(self): #bruce 080319
        # note: some code which tests for "Chunk or Jig" might do better
        # to test for this method's return value.
        """
        @see: For documentation, see Node method docstring.

        @rtype: boolean

        [overrides Node method]
        """
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
        self._prekill() #bruce 060327, needed here even though _superclass.kill might do it too
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
        if self._enable_deallocate_displist():
            self.deallocate_displist_later() #bruce 071103
        return # from Chunk.kill

    def _set_will_kill(self, val): #bruce 060327 in Chunk
        """
        [extends private superclass method; see its docstring for details]
        """
        _superclass._set_will_kill( self, val)
        for a in self.atoms.itervalues():
            a._will_kill = val # inlined a._prekill(val), for speed
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
        # See comments in findAtomUnderMouse_Numeric_stuff for more details.
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
            res = self.findAtomUnderMouse_Numeric_stuff( v, r_xy_2, radii_2, **kws)
        except:
            print_compact_traceback("bug in findAtomUnderMouse_Numeric_stuff: ")
            res = []
        if unpatched_seli_radius2 is not None:
            radii_2[seli] = unpatched_seli_radius2
        return res # from findAtomUnderMouse

    def findAtomUnderMouse_Numeric_stuff(self, v, r_xy_2, radii_2,
                                         far_cutoff = None, near_cutoff = None, alt_radii = [] ):
        """
        private helper routine for findAtomUnderMouse
        """
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

        return [(closest_z, atom)] # from findAtomUnderMouse_Numeric_stuff

    # self.sel_radii_squared is not a real attribute, since invalling it
    # would be too slow. Instead we have these methods:

    def get_sel_radii_squared(self):
        #bruce 050419 fix bug 550 by fancifying haveradii
        # in the same way as for havelist (see 'bruce 050415').
        # Note: this must also be invalidated when one atom's display mode changes,
        # and it is, by atom.setDisplayStyle calling changeapp(1) on its chunk.
        disp = self.get_dispdef() ##e should caller pass this instead?
        eltprefs = PeriodicTable.rvdw_change_counter # (color changes don't matter for this, unlike for havelist)
        radiusprefs = chem.Atom.selradius_prefs_values() #bruce 060317 -- include this in the tuple below, to fix bug 1639
        if self.haveradii != (disp, eltprefs, radiusprefs): # value must agree with set, below
            # don't have them, or have them for wrong display mode, or for wrong element-radius prefs            
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

    # Old methods for finding certain atoms or singlets
    # [bruce 060313 removed even the commented-out forms, last present in rev. 1.109]
    #
    # [bruce 041207 comment: these [removed old methods] ought to be unified, and perhaps bugfixed.
    #  To help with this, I'm adding comments, listing their callers,
    #  and removing the ones with no callers.
    #  See also some relevant code used in extrudeMode.py,
    #  actually findHandles_exact in handles.py,
    #  which will be useful for postprocessing lists of atoms
    #  found by code like the following.
    # ]
    ## ....

    # return the singlets in the given sphere (point, radius),
    # sorted by increasing distance from point
    # bruce 041207 comment: this is only used in depositMode.attach.
    def nearSinglets(self, point, radius):
        if not self.singlets:
            return []
        singlpos = self.singlpos #bruce 051129 ensure this is computed in its own line, for sake of traceback linenos
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
        assert 0, "should never be called, since a chunk does not *refer* to selatoms, or appear in atom.jigs"
        return True # but if it ever is called, answer should be true

    def copy_empty_shell_in_mapping(self, mapping): #bruce 070430 revised to honor mapping.assy
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
        numol = self.__class__(mapping.assy, self.name)
            #bruce 080316 Chunk -> self.__class__ (part of fixing this for Extrude of DnaGroup)
        self.copy_copyable_attrs_to(numol) # copies .name (redundantly), .hidden, .display, .color...
        if (self.chunkHasOverlayText):
            numol.chunkHasOverlayText = True
        if (self.showOverlayText):
            numol.showOverlayText = True
        mapping.record_copy(self, numol)
        # also copy user-specified axis, center, etc, if we ever have those
        ## numol.setDisplayStyle(self.display)
        if self._colorfunc is not None: #bruce 060411 added condition; note, this code snippet occurs in two methods
            numol._colorfunc = self._colorfunc # bruce 041109 for extrudeMode.py; revised 050524
        if self._dispfunc is not None:
            numol._dispfunc = self._dispfunc
        return numol

    def copy_full_in_mapping(self, mapping): # Chunk method [bruce 050526] #bruce 060308 major rewrite
        """
        #doc;
        overrides Node method;
        only some atom copies get recorded in mapping (if we think it might need them)
        """
        numol = self.copy_empty_shell_in_mapping( mapping)
        # now copy the atoms, all at once (including all their existing singlets, even though those might get revised)
        # note: the following code is very similar to copy_in_mapping_with_specified_atoms, but not identical.
        pairlis = []
        ndix = {} # maps old-atom key to corresponding new atom
        nuatoms = {}
        for a in self.atlist: # this is now in order of atom.key; it might get recomputed right now (along with atpos & basepos if so)
            na = a.copy()
            # inlined addatom, optimized (maybe put this in a new variant of obs copy_for_mol_copy?)
            na.molecule = numol # no need for _changed_parent_Atoms[na.key] = na #bruce 060322
            nuatoms[na.key] = na
            pairlis.append((a, na))
            ndix[a.key] = na
        numol.invalidate_atom_lists()
        numol.atoms = nuatoms
##        if 0:
##            # I'm not sure how to make this correct, since it doesn't copy everything recomputed
##            # when we recompute atlist/atpos/basepos; beside's it's often wasted work since caller plans to
##            # move all the atoms after the copy, or so... so nevermind.
##            numol.atlist = copy_val(self.atlist)
##            numol.atpos = copy_val(self.atpos) # use copy_val in case length is 0 and type is unusual
##            numol.basepos = copy_val(self.basepos)

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
        """
        [private helper for some copy methods]
        Given some copied atoms (in a private format in pairlis and ndix),
        ensure their bonds and jigs will be taken care of.
        """
        from model.bonds import bond_copied_atoms # might be a recursive import if done at toplevel
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
                        bond_copied_atoms(na, ndix[a2key], b, a)
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
        """
        Copy yourself in this mapping (for the first and only time),
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
            #numol.set_hotspot( hotspot, silently_fix_if_invalid = True) #Huaicai 10/13/05: fix bug 1061 by changing 'numol' to 'self'
            self.set_hotspot( hotspot, silently_fix_if_invalid = True) # this checks everything before setting it; if invalid, silent noop

    # == 

    def copy(self, dad = None, offset = V(0,0,0), cauterize = 1): #bruce 080314
        """
        Public method. DEPRECATED, see code comments for details.
        Deprecated alias for copy_single_chunk (also deprecated but still in use).
        """
        cs = compact_stack("\n*** print once: called deprecated Chunk.copy from: ")
        if not env.seen_before(cs):
            print cs
        return self.copy_single_chunk( dad, offset, cauterize)

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

        from model.bonds import bond_copied_atoms # might be a recursive import if done at toplevel
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
        if (self.chunkHasOverlayText):
            numol.chunkHasOverlayText = True
        if (self.showOverlayText):
            numol.showOverlayText = True
        numol.name = newname
        #end 050531 kluges
        nuatoms = {}
        for a in self.atlist: # 060308 changed similarly to copy_full_in_mapping (shares some code with it)
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
                    # internal bond - make the analogous one [this should include all preexisting bonds to singlets]
                    #bruce 050715 bugfix (copied from 050524 changes to another routine; also done below for extern_atoms_bonds):
                    # don't do it twice for the same bond (needed by new faster bonding methods),
                    # and use bond_copied_atoms to copy bond state (e.g. bond-order policy and estimate) from old bond.
                    if a.key < a2key:
                        # arbitrary condition which is true for exactly one ordering of the atoms;
                        # note both keys are for original atoms (it would also work if both were from
                        # copied atoms, but not if they were mixed)
                        bond_copied_atoms(na, ndix[a2key], b, a)
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
            for a, b in extern_atoms_bonds:
                # compare to code in Bond.unbond():
                x = chem.Atom('X', b.ubp(a) + offset, numol)
                na = ndix[a.key]
                #bruce 050715 bugfix: also copy the bond-type (two places in this routine)
                ## numol.bond(na, x)
                bond_copied_atoms( na, x, b, a)
        if copied_hotspot is not None:
            numol.set_hotspot( ndix[copied_hotspot.key])
        #e also copy (but translate by offset) user-specified axis, center, etc,
        #  if we ever have those
        if self.user_specified_center is not None: #bruce 050516 bugfix: 'is not None'
            numol.user_specified_center = self.user_specified_center + offset
        numol.setDisplayStyle(self.display)
        numol.dad = dad
        if dad and debug_flags.atom_debug: #bruce 050215
            print "atom_debug: mol.copy got an explicit dad (this is deprecated):", dad
        if self._colorfunc is not None: #bruce 060411 added condition; note, this code snippet occurs in two methods
            numol._colorfunc = self._colorfunc # bruce 041109 for extrudeMode.py; revised 050524
        if self._dispfunc is not None:
            numol._dispfunc = self._dispfunc
        return numol # assy

    # ==

    def Passivate(self, p = False):
        """
        [Public method, does all needed invalidations:]
        Passivate the selected atoms in this chunk, or all its atoms if p = True.
        This transmutes real atoms to match their number of real bonds,
        and (whether or not that succeeds) removes all their open bonds.
        """
        # bruce 041215 added docstring, inferred from code; capitalized name
        for a in self.atoms.values():
            if p or a.picked: a.Passivate()

    def Hydrogenate(self):
        """
        [Public method, does all needed invalidations:]
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
        """
        [Public method, does all needed invalidations:]
        Remove hydrogen atoms from this chunk.
        Return the number of atoms removed [bruce 041018 new feature].
        """
        count = 0
        for a in self.atoms.values():
            count += a.Dehydrogenate()
        return count



    def __str__(self):
        # bruce 041124 revised this; again, 060411 (can I just zap it so __repr__ is used?? Try this after A7. ##e)
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
            return "<%s %s, KILLED (no assy), at %#x of %d atoms>" % (classname, name, id(self), len(self.atoms)) # note other order
        pass

    def dump(self):
        print self, len(self.atoms), 'atoms,', len(self.singlets), 'singlets'
        for a in self.atlist:
            print a
            for b in a.bonds:
                print b

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

    def get_singlets(self): #bruce 041109 moved here from extrudeMode.py
        "return a sequence of the singlets of Chunk self"
        return self.singlets # might be recomputed by _recompute_singlets

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

    def isDnaChunk(self):
        """
        Returns True is the chunk is a DNA object (either strand or axis).
        """
        return self.isAxisChunk() or \
               self.isStrandChunk()
    
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

##Chunk = molecule #bruce 051227 permit this synonym; for A8 we'll probably rename the class this way
##
##del molecule #bruce 071113 along with revising all uses to refer to Chunk (except the classname itself)
##
### Note: we can't rename the class until all string literals 'molecule' are reviewed. [has been done now]

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
    def changed_selection(self):
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

    axis = compute_heuristic_axis( basepos, 'chunk',
                                   evals_evecs = (evals, evecs), aspect_threshhold = 0.95,
                                   near1 = V(1,0,0), near2 = V(0,1,0), dflt = V(1,0,0) # prefer axes parallel to screen in default view
                                   )

    assert axis is not None
    axis = A(axis) ##k if this is in fact needed, we should probably do it inside compute_heuristic_axis for sake of other callers
    assert type(axis) is type(V(0.1, 0.1, 0.1)) # this probably doesn't check element types (that's probably ok)

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
