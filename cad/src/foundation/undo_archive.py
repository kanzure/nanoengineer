# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
undo_archive.py - Collect and organize a set
of checkpoints of model state and diffs between them,
providing undo/redo ops which apply those diffs to the model state.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

[060223: out of date status info from this docstring was
 mostly moved to undo_archive-doc.text,
 not in cvs; can clean up and commit later #e]
"""

import time
from utilities import debug_flags
from utilities.debug import print_compact_traceback, print_compact_stack, safe_repr
from utilities.debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True
import foundation.env as env

import foundation.state_utils as state_utils
from foundation.state_utils import objkey_allocator, obj_classifier, diff_and_copy_state
from foundation.state_utils import transclose, StatePlace, StateSnapshot

from foundation.state_constants import _UNSET_
from foundation.state_constants import UNDO_SPECIALCASE_ATOM, UNDO_SPECIALCASE_BOND
from foundation.state_constants import ATOM_CHUNK_ATTRIBUTE_NAME

from utilities.prefs_constants import historyMsgSerialNumber_prefs_key
from foundation.changes import register_postinit_object
import foundation.changedicts as changedicts # warning: very similar to some local variable names

destroy_bypassed_redos = True # whether to destroy the Redo stack to save RAM,
    # when redos become inaccessible since a new operation is done after an Undo.
    # (The reason you might *not* want to is if you wanted to give UI access
    #  to "abandoned alternate futures". We have no plans to do that,
    #  but the low-level Undo code would support it just fine.)
    # [As of 060301 this was not yet implemented, but the flag shows where to
    #  implement it. As of 060309 this is partly implemented.]

debug_undo2 = False # do not commit with true

debug_change_indicators = False # do not commit with true

# ==

_undo_debug_obj = None
    # a developer can set this to an undoable object
    # (in a debugger or perhaps using a debug menu op (nim))
    # to print history messages about what we do to this
    # specific object

_nullMol = None

def set_undo_nullMol(null_mol):
    global _nullMol
    assert _nullMol is None
    _nullMol = null_mol

def _undo_debug_message( msg):
    from utilities.Log import _graymsg, quote_html
    ## env.history.message_no_html( _graymsg( msg ))
    ## -- WRONG, message_no_html would mess up _graymsg
    env.history.message( _graymsg( quote_html( msg )))

# ==

def mmp_state_from_assy(archive, assy,
                        initial = False,
                        use_060213_format = False,
                        **options): #bruce 060117 prototype-kluge
    """
    Return a data-like python object encoding all the undoable state in assy
    (or in nE-1 while it's using assy)
    (it might contain refs to permanent objects like elements or atomtypes,
    and/or contain Numeric arrays)
    """
    if use_060213_format:
        # [guess as of 060329: initial arg doesn't matter for this
        #  scanning method, or, we never scan it before fully initialized anyway]
        return mmp_state_by_scan(archive, assy, **options)
        ## return ('scan_whole', mmp_state_by_scan(archive, assy, **options) )

    assert 0 # 060301, zapped even the commented-out alternative, 060314

def mmp_state_by_scan(archive, assy, exclude_layers = ()):
    #060329/060404 added exclude_layers option
    """
    [#doc better:]
    Return a big StateSnapshot object listing all the undoable data
    reachable from assy, except the data deemed to be in layers
    listed in exclude_layers (e.g. atoms and bonds and certain sets of those),
    in a data-like form (but including live objrefs), mostly equivalent to
    a list of objkey/attr/value triples,
    suitable for mashing it back into assy
    (i.e. mainly and whatever undoable objs it contains), at a later time.

    You can pass exclude_layers = ('atoms') to skip the atom-layer attrs
    of Chunks (though not yet of Jigs),
    and the entire contents of Atoms & Bonds.
    """
    #e misnamed, since other things refer to this as the non-mmp option
    scanner = archive.obj_classifier
    start_objs = [assy] #k need any others?
    viewdict = {}
    # kluge: defer collection of view-related objects and discard them,
    # but don't bother deferring selection-related objects,
    # since for now there aren't any (and looking for them would
    # slow us down until atoms are processed separately in a faster way).
    childobj_dict = scanner.collect_s_children(
                        start_objs,
                        deferred_category_collectors = {'view': viewdict},
                        exclude_layers = exclude_layers
                    )

    if 0 and env.debug():
        print "debug: didn't bother scanning %d view-related objects:" % \
              len(viewdict), viewdict.values() # works [060227]; LastView

    #e figure out which ones are new or gone? not needed until we're
    # differential, unless this is a good place to be sure the gone ones
    # are properly killed (and don't use up much RAM). if that change anything
    # we might have to redo the scan until nothing is killed, since subobjects
    # might die due to this.

    state = scanner.collect_state( childobj_dict,
                                   archive.objkey_allocator,
                                   exclude_layers = exclude_layers )

    state._childobj_dict = childobj_dict
        #060408 this replaces the _lastscan kluge from ~060407
        # (still a kluge, but less bad);
        # it's used (via a reference stored temporarily in the archive
        # by a method-like helper function) by archive.childobj_liveQ,
        # and discarded from archive before it becomes invalid,
        # and discarded from the state we're returning when its StatePlace
        # is asked to give it up by steal_lastsnap, which means it's
        # becoming mutable (so _childobj_dict would also become invalid).

    return state # a StateSnapshot

# ==

# assy methods, here so reload works
# [but as of 060407, some or all of them should not be assy methods anyway,
#  it turns out]

def assy_become_state(self, stateplace, archive):
    #e should revise args, but see also the last section
    # which uses 'self' a lot [060407 comment]
    """
    [self is an assy]
    replace our state with some new state (in an undo-private format)
    saved earlier by an undo checkpoint,
    using archive to interpret it if necessary
    """
    #bruce 060117 kluge for non-modular undo;
    # should be redesigned to be more sensible
    assert isinstance(stateplace, StatePlace), \
           "should be a StatePlace: %r" % (stateplace,)

    if debug_change_indicators:
        print "assy_become_state begin, chg ctrs =", \
              archive.assy.all_change_indicators()

    try:
        assy_become_scanned_state(archive, self, stateplace)
            # that either does self.update_parts()
            # or doesn't need it done (or both)
    except:
        #060410 protect against breaking the session (though exceptions in
        # there can end up breaking it anyway, a bit more slowly)
        ###e bring in redmsg code for "see traceback in console",
        # in undo_manager.py, do_main_menu_op
        ###e and generalize that to a helper function to use for
        # most of our debug prints
        msg = "bug: exception while restoring state after Undo or Redo: "
        print_compact_traceback( msg)

    self.changed() #k needed? #e not always correct! (if we undo or redo to
        # where we saved the file)
        #####@@@@@ review after scan_whole 060213
    # the following stuff looks like it belongs in some sort of
    # _undo_update method for class assy,
    # or one of the related kinds of methods,
    # like registered undo updaters ####@@@@ [060407 comment]
    assert self.part # update_parts was done already
    self.o.set_part( self.part) # try to prevent exception in GLPane.py:1637
    self.w.win_update() # precaution; the mt_update might be needed
    if debug_change_indicators:
        print "assy_become_state end, chg ctrs =", \
              archive.assy.all_change_indicators()
    return

def assy_clear(self): #bruce 060117 draft
    """
    [self is an assy]
    become empty of undoable state (as if just initialized)
    """
    # [note: might be called as assy.clear() or self.clear() in this file.]
    self.tree.destroy() # not sure if these work very well yet;
        # maybe tolerable until we modularize our state-holding objects

        #bruce 060322 comments [MOSTLY WRONG but useful anyway, as explained in next lines]:
        # - as I wrote the following, I was thinking that this was an old method of assy, so they might be partly misguided.
        #   I'm not even sure it's ever called, and if it is, it might not be tantamount to assy.destroy as I think I was assuming.
        # - it's unclear whether general semantics of .destroy would condone this destroying their children (as it now does);
        #   guess: desirable to destroy solely-owned children or (more generally) children all of whose parents are destroyed,
        #   but not others (e.g. not Node.part unless all its Nodes are -- note, btw, Part.destroy is not a true destroy method in
        #   semantics).
        # - current implem is not enough (re refs from undo archive). Furthermore, letting the archive handle it might be best,
        #   but OTOH we don't want to depend on their being one, so some more general conventions for destroy (of objs with children)
        #   might actually be best.
        # - ###@@@ why doesn't this destroy self.um if it exists??? guess: oversight; might not matter a lot
        #   since i think the next one destroys it (need to verify). [MISGUIDED, see above]
    self.shelf.destroy()
    self.root = None # memory leak?
    self.tree = self.shelf = None
    self._last_current_selgroup = None # guess, to avoid traceback
    #e viewdata?
    #e selection?
    #e parts?
    #e glpane state?
    #e effect on MT?
    #e selatom?
    #e mode?
    #e current_movie?
    #e filename?
    #e modified?
    self.changed()
    return

# ==

def assy_become_scanned_state(archive, assy, stateplace):
    """
    [obs docstring?: stateplace is returned by mmp_state_by_scan,
    and is therefore presumably a StateSnapshot or StatePlace object]
    """
    # TODO: guess as of 060407: this should someday be an archive method,
    # or more specifically a method of AssyUndoArchive,
    # with some of the helpers being stateplace or state methods.

    assert assy is archive.assy
        # in future, maybe an archive can support more than one assy
        # at a time (so this will need to be more general); who knows

    # note [060407] (obs now): the following mashes *all* attrs, changed or not.
    # If we want to make Undo itself faster (as opposed to making checkpoints
    # faster), we have to only mash the changed ones (and maybe do only the
    # needed updates as well).
    # update 060409: The debug_pref else clause tries to do this...
    # and is now the official code for this.

    if not debug_pref("use differential mash_attrs?", Choice_boolean_True):
        # i think it's ok to decide this independently each time...
        # NOTE: this case is deprecated; it ought to work, and might be useful
        # for debugging, but is no longer tested or supported [060409]
        # (it might have problems if the atom.mol = None in differential
        #  case is bad in this case which needs _nullMol for some reason)
        attrdicts = stateplace.get_attrdicts_for_immediate_use_only()

        modified = {} # key->obj for objects we modified

        # these steps are in separate functions for clarity,
        # and so they can be profiled individually
        mash_attrs( archive, attrdicts, modified, 'fake invalmols, bug if used')
        fix_all_chunk_atomsets( attrdicts, modified)
        _call_undo_update( modified)
        call_registered_undo_updaters( archive)
        final_post_undo_updates( archive)
    else:
        # NOTE: This is the only tested and supported case as of 060409.
        #
        # We ask stateplace to pull lastsnap to itself
        # (like the above does now) (??)
        # but to tell us a smaller set of attrdicts
        # containing only objects we need to change.
        #
        # I think that this revision in the algorithm (i.e. changing it
        # to use differential mash_attrs) means that some implicit assumptions
        # which are true now, but are only required by some of the code,
        # have become required by more of the code -- namely, an assumption
        # about the stateplace which has lastsnap being the same one
        # that matches the current model state (as it was last mashed
        # into or checkpointed out of).

        # WARNING: the following has an implicit argument which is
        # "which stateplace has the lastsnap". (More info above.)
        attrdicts = stateplace.get_attrdicts_relative_to_lastsnap()
            # for this new differential scheme to be correct, we had to
            # ditch the prior code's support for dflt vals for attrs...

        modified = {}
            # key->obj for objects we modified and which are still alive
            # (the only objs we modify that are not still alive are newly
            # dead atoms, whose .molecule we set to None,
            # and perhaps newly dead chunks, removing atoms and invalidating
            # (see comments in _fix_all_chunk_atomsets_differential))

        # these steps are in separate functions for clarity, and so they can be
        # profiled individually
        ## oldmols = {}
            # kluge [later: I'm not sure if 'kluge' refers to this assignment,
            #  or to its being commented out!],
            # described elsewhere -- search for 'oldmols' and this date 060409
        invalmols = {}
        mash_attrs( archive, attrdicts, modified, invalmols,
                    differential = True )
        _fix_all_chunk_atomsets_differential( invalmols)
        _call_undo_update( modified)
            # it needs to only call it for live objects! so we only pass them.
        call_registered_undo_updaters( archive)
        final_post_undo_updates( archive)

    return # from assy_become_scanned_state

def mash_attrs( archive, attrdicts, modified, invalmols, differential = False ):
    #060409 added differential = True support
    """
    [private helper for assy_become_scanned_state:]
    Mash new (or old) attrvals into live objects, using setattr or
    _undo_setattr_;
    record which objects are modified in the given dict, using objkey->obj
    (this will cover all reachable objects in the entire state,
     even if only a few *needed* to be modified,
     in the present implem [still true even with differential atom/bond scan,
     as of 060406] [NOT TRUE ANYMORE if differential passed; 060409])

    @param invalmols: a dictionary mapping id(mol) -> mol, to which we should
                      add any mol (i.e. any object we find or store in
                      atom.molecule for some atom we're modifying) from whose
                      .atoms dict we successfully remove atom, or to whose
                      .atoms dict we add atom. We assume mol.atoms maps atom.key
                      to atom. By "atom" we mean an instance of a class whose
                      _s_undo_specialcase == UNDO_SPECIALCASE_ATOM.

    @type invalmols: a mutable dictionary which maps id(mol) -> mol, where
                     mol can be any object found or stored as atom.molecule,
                     which has an .atoms dict (i.e. a Chunk).
    """
    # use undotted localvars, for faster access in inner loop:
    modified_get = modified.get
    obj4key = archive.obj4key
    classifier = archive.obj_classifier
    reset_obj_attrs_to_defaults = classifier.reset_obj_attrs_to_defaults
    attrcodes_with_undo_setattr = classifier.attrcodes_with_undo_setattr
    from foundation.state_utils import copy_val as copy
        # OPTIM: ideally, copy_val might depend on attr (and for some attrs
        # is not needed at all), i.e. we should grab one just for each attr
        # farther inside this loop, and have a loop variant without it
        # (and with the various kinds of setattr/inval replacements too --
        #  maybe even let each attr have its own loop if it wants,
        #  with atoms & bonds an extreme case)
    for attrcode, dict1 in attrdicts.items():
        ##e review: items might need to be processed in a specific order
        attr, acode = attrcode
        might_have_undo_setattr = attrcodes_with_undo_setattr.has_key(attrcode)
            #060404; this matters now (for hotspot)
        for key, val in dict1.iteritems(): # maps objkey to attrval
            obj = modified_get(key)
            if obj is None:
                # first time we're touching this object -- if differential,
                # we might have seen it before but we never got a val other
                # than _UNSET_ for it
                obj = obj4key[key]
                    # TODO: optim: for differential it'd be faster to always
                    # do it this way here; for non-diff this helps us know
                    # when to reset attrs
                if not differential:
                    modified[key] = obj
                    ##@@ unclear whether we sometimes need this in
                    # differential case, but probably we do
                    # [... now i think we don't]
                    reset_obj_attrs_to_defaults(obj)
                        # Note: it's important that that didn't mess with attrs
                        # whose _undo_setattr_xxx we might call, in case that
                        # wants to see the old value. As an initial kluge,
                        # we assert this combination never occurs (in other
                        # code, once per class). When necessary, we'll fix
                        # that by sophisticating this code. [bruce 060404]
                pass
            if differential and archive.attrcode_is_Atom_chunk(attrcode):
                ## was: differential and attrcode == ('molecule', 'Atom'):
                attrname = attrcode[0] # this is 'molecule' as of 071114,
                    # or more generally it's ATOM_CHUNK_ATTRIBUTE_NAME,
                    # but it's correct to grab it from attrcode this way
                _mash_attrs_Atom_chunk(key, obj, attrname, val, modified, invalmols)
                continue
            if differential and val is _UNSET_:
                # this differential case can't support attrs with dflts at all,
                # so they're turned off now [060409]
                ## dflts = classifier.classify_instance(obj).attrcode_defaultvals
                continue # because no need to setattr.
                    # However, we *do* need to do the Atom.molecule kluge
                    # (above) first (which skips this code via 'continue'
                    # if it happens). And we probably also need to update
                    # modified first (as we do before that).
            modified[key] = obj # redundant if not differential (nevermind)
            val = copy(val)
                # TODO: possible future optim: let some attrs declare that this
                # copy is not needed for them [MIGHT BE A BIG OPTIM]
            if might_have_undo_setattr: # optim: this flag depends on attr name
                # note: '_undo_setattr_' is hardcoded in several places
                setattr_name = '_undo_setattr_' + attr
                    # only support attr-specific setattrs for now,
                    # for speed and subclass simplicity
                try:
                    method = getattr(obj, setattr_name)
                        # OPTIM: possible future optim:
                        # store unbound method for this class and attr
                except AttributeError:
                    pass # fall thru, use normal setattr
                else:
                    if obj is _undo_debug_obj:
                        msg = "undo/redo: %r.%s = %r, using _undo_setattr_" % \
                              (obj, attr, val)
                        _undo_debug_message( msg)
                    try:
                        method(val, archive) # note: val might be _Bugval
                    except:
                        # catch exceptions (so single-object bugs don't break
                        # Undo for the rest of the session);
                        # continue with restoring other state,
                        # or at least other attrs
                        msg = "exception in %s for %s; continuing: " % \
                              (setattr_name, safe_repr(obj))
                        print_compact_traceback( msg) #060410
                        # possible TODO items:
                        # - also emit redmsg if not seen_before for this attr
                        #   (or attrcode?) and this undo op;
                        # - revise all these debug prints to use safe_repr
                        # - have an outer exception catcher which still protects
                        #   the session, since if this one is uncaught, we get a
                        #   redmsg about bug in undo, and after that, we keep
                        #   getting checkpoint tracebacks;
                        #   see other comments of this date, or referring to
                        #   redmsg, print_compact_traceback, seen_before
                    continue
            # else, or if we fell through:
            if obj is _undo_debug_obj:
                _undo_debug_message("undo/redo: %r.%s = %r" % (obj, attr, val))
            setattr(obj, attr, val) ##k might need revision in case:
                # dflt val should be converted to missing val, either as optim
                # or as requirement for some attrs (atomtype?) #####@@@@@
                # dflt vals were not stored, to save space, so missing keys
                # should be detected and something done about them ...
                # this is done for objects we modify, but what about reachable
                # objs with all default values?
                # either look for those on every value we copy and store,
                # or make sure every obj has one attr with no default value
                # or whose actual value is never its default value.
                # This seems true of all our current objs,
                # so I'll ignore this issue for now!
                # ###k (also this remains unreviewed for issues of
                # which objs "exist" and which don't... maybe it only matters
                # as space optim...)
            # SOMEDAY: check if val is _Bugval, maybe print error message
            # or delete it or both (can share code with deleting it if it's
            # attr-specific dflt, once we clean up decls so different dflts
            # mean different attrdicts) [bruce 060311 comment]
            continue
        continue
    return # from mash_attrs

# ==

def _mash_attrs_Atom_chunk(key, obj, attrname, val, modified, invalmols):
    """
    Special case for differential mash_attrs when changing an
    Atom.molecule attribute. (Private helper function for mash_attrs.)

    @param key: the index of obj in modified. (For more info, see calling code.)
                Warning: not the same as obj.key.

    @param obj: an atom (i.e. an instance of a class whose _s_undo_specialcase
                attribute equals UNDO_SPECIALCASE_ATOM).

    @param attrname: 'molecule', or whatever attribute name we change it to.

    @param val: the new value we should store into obj.molecule.

    @param modified: same as in mash_attrs.

    @param invalmols: same as in mash_attrs.
    """
    #bruce 071114 split this out of mash_attrs,
    # with slight changes to comments and attrname
    # (which used to be hardcoded as 'molecule',
    #  and is still hardcoded as obj.molecule gets and sets,
    #  and as method names containing 'molecule' in comments).

    assert attrname == 'molecule', "oops, you better revise " \
           "obj.molecule gets/sets in this function"
    assert attrname == ATOM_CHUNK_ATTRIBUTE_NAME # that should match too

    # obj is an Atom and we're changing its .molecule.
    # This is a kluge to help update mol.atoms for its old and
    # new mol.
    #
    # We might be able to do this with Atom._undo_setattr_molecule
    # (though I recall rejecting that approach in the past,
    # for non-differential mash_attrs, but I forget why),
    # but for efficiency and simplicity we do it with this
    # specialcase kluge, which comes in two parts -- this one
    # for removal [of atom from old mol, i guess as of 071113],
    # and the other one below, findable by searching for the
    # ' "add to new mol.atoms" part of the kluge '.
    # [comment revised, bruce 071114]

    mol = obj.molecule
    # mol might be _UNSET_, None, or _nullMol, in which case,
    # we should do nothing, or perhaps it might be a real mol
    # but with obj not in mol.atoms, which might deserve a
    # debug print, but we should still do nothing --
    # simplest implem of all this is just to not be bothered
    # by not finding .atoms, or obj.key inside it.
    try:
        del mol.atoms[obj.key]
    except:
        if mol is not None and mol is not _nullMol and env.debug():
            # remove when works!
            print_compact_traceback(
                "debug fyi: expected exception in del " \
                "mol.atoms[obj.key] for mol %r obj %r" % \
                                    (mol, obj) )
        pass
    else:
        # this is only needed if the del succeeds (even if it fails
        # for a real mol, due to a bug), since only then did we
        # actually change mol
        invalmols[id(mol)] = mol
    if val is _UNSET_:
        # I'm not fully comfortable with leaving invalid mol refs in
        # dead atoms, so I make this exception to the general rule
        # in this case. (If we later add back
        # Atom._undo_setattr_molecule, this would mess it up, but
        # hopefully it would take over this kluge's job entirely.)
        ## val = None -- this caused e.g.
        ##   exception in _undo_update for X21; skipping it:
        ##   exceptions.AttributeError:
        ##   'NoneType' object has no attribute 'havelist'
        ## which calls into question calling _undo_update on dead
        ## objs, or more likely, this one's implem,
        ## but maybe it's fine (not reviewed now) and this is why
        ## we have _nullMol, so store that instead of None.
        ## val = _nullMol
        ## (Let's hope this can only happen when
        ##  _nullMol is not None!!! Hmm, not true! Fix it here,
        ##  or let _undo_update init _nullMol and store it??
        ##  Neither: store None, and let _undo_update do no
        ##  invals at all in that case. Come to think of it,
        ##  the non-differential mash_attrs probably only called
        ##  _undo_update on live objects!! Should we?
        ##  #####@@@@@ issue on bonds too
        val = None
        obj.molecule = val
        # but we *don't* do modified[key] = obj, since
        # we only want that for live objects
        if obj is _undo_debug_obj:
            msg = "undo/redo: %r.%s = %r, and removed it " \
                  "from %r.atoms" % \
                  (obj, attrname, val, mol)
            _undo_debug_message( msg)
        pass
    else:
        # this is the "add to new mol.atoms" part of the kluge.
        # obj is always a live atom (I think), so val should
        # always be a real Chunk with .atoms.
        mol = val
        obj.molecule = mol
        mol.atoms[obj.key] = obj
        invalmols[id(mol)] = mol
        modified[key] = obj
        if obj is _undo_debug_obj:
            msg = "undo/redo: %r.%s = %r, and added it " \
                  "to .atoms" % \
                  (obj, attrname, mol)
            _undo_debug_message( msg)
        pass
    # this was part of try1 of fixing mol.atoms,
    # but it had an unfixable flaw of being non-incremental,
    # as well as minor flaws with _UNSET_:
##    # kluge to help fix_all_chunk_atomsets in differential case
##    oldmols = differential['oldmols'] # part of the kluge
##    mol = obj.molecule
##    oldmols[id(mol)] = mol
    return

# ==

def fix_all_chunk_atomsets( attrdicts, modified):
    #060409 NOT called for differential mash_attrs;
    # for that see _fix_all_chunk_atomsets_differential
    """
    [private helper for assy_become_scanned_state:]
    Given the set of live atoms (deduced from attrdicts)
    and their .molecule attributes (pointing from each atom to its
     owning chunk, which should be a live chunk),
    replace each live chunk's .atoms attr (dict from atom.key to atom,
    for all its atoms) with a recomputed value, and do all(??)
    necessary invals.

    WARNING: CURRENT IMPLEM MIGHT ONLY BE CORRECT IF ALL LIVE CHUNKS
    HAVE ATOMS. [which might be a bug, not sure ##@@@@]
    """
    modified_get = modified.get
#bruce 060314 this turned out not to be useful; leave it as an example
# until analoguous stuff gets created (since the principle of organization
# is correct, except for being nonmodular)
##    if 1:
##        ####@@@@ KLUGE: somehow we happen to know that we need to process mols_with_invalid_atomsets here,
##        # before running any obj._undo_update functions (at least for certain classes).
##        # We can know this since we're really (supposed to be) a method on AssyUndoArchive (so we know all about
##        # the kinds of data in assys). [bruce 060313]
##        for chunk in archive.mols_with_invalid_atomsets.values():
##            # chunk had one or more atoms leave it or join it, during the setattrs above
##            # (actually, during some _undo_setattr_molecule on those atoms; they kept its .atoms up to date,
##            #  but saved invals for here, for efficiency)
##            chunk.invalidate_atom_lists()
##                # this effectively inlines that part of chunk.addatom and delatom not done by atom._undo_setattr_molecule
##                # (we could just add chunk into modified (localvar), but this is more efficient (maybe))
    # that has replaced .molecule for lots of atoms; need to fix the .atoms dicts of those mols [060314]
##    mols = oldmols or {} #060409 kluge [; note, if caller passes {} this uses a copy instead, but that's ok.]
####    if oldmols and env.debug():
####        print "got oldmols = %r" % (oldmols,) #### contains _UNSET_, not sure how that's possible ... i guess from new atoms?? no...
####        # anyway, nevermind, just zap it.
##    if oldmols:
##        from model.chunk import _nullMol
##        for badmol in (None, _nullMol, _UNSET_):
##            # I don't know why these can be in there, but at least _nullMol can be; for now just work around it. ###@@@
##            if env.debug():
##                if mols.has_key(id(badmol)):
##                    print "debug: zapping %r from oldmols" % (badmol,)
##            oldmols.pop(id(badmol),None)
##        if env.debug():
##            print "debug: repaired oldmols is", oldmols
##        pass
##    ## mols = {}
    mols = {}

    molcode = (ATOM_CHUNK_ATTRIBUTE_NAME, 'Atom') # KLUGE; we want attrcode for Atom.molecule;
        # instead we should just get the clas for Atom and ask it!
        ### how will I know if this breaks? debug code for it below
        # can't be left in...
    assert 0, "this code is no longer valid, since Atom might have subclasses soon (with different names)"
        # not worth the effort to port it re those changes,
        # since it never runs anymore [bruce 071114]

    moldict = attrdicts.get(molcode, {})
        # Note: the value {} can happen, when no Chunks (i.e. no live atoms)
        # were in the state!
        # (this is a dict from atoms' objkeys to their mols,
        #  so len is number of atoms in state;
        #  i think they are all *found* atoms but as of 060330
        #  they might not be all *live* atoms,
        #  since dead mol._hotspot can be found and preserved.
        #  [no longer true, 060404])
    # warning: moldict is not a dict of mols, it's a dict from
    # atom-representatives to those atoms' mols;
    # it contains entries for every atom represented in the state
    # (i.e. only for our, live atoms, if no bugs)
    if 0 and env.debug():
        ###@@@ disable when works; reenable whenever acode scheme changes
        print "debug: len(moldict) == %d; if this is always 0 we have a bug, " \
              "but 0 is ok when no atoms in state" % (len(moldict))
    for atom_objkey, mol in moldict.iteritems():
        mols[id(mol)] = mol
    ######@@@@@@ 060409 BUG in differential case: mols doesn't include
    # chunks that lost atoms but didn't gain any!
    # (though moldict does include the atoms which they lost.)
    # (could we resolve it by recording diffs in number of atoms per
    #  chunk, so we'd know when to recompute set of atoms??
    #  or is it better just to somehow record the old vals of atom.molecule
    #  that we change in mash_attrs? caller could pass that in.)
    # Ok, we're having caller pass in oldmols, for now.
    for badmol in (None, _nullMol):
        if mols.has_key(id(badmol)):
            # should only happen if undoable state contains killed or
            # still-being-born atoms; I don't know if it can
            # (as of 060317 tentative fix to bug 1633 comment #1, it can --
            #  _hotspot is S_CHILD but can be killed [wrong now...])
            # 060404: this is no longer true, so zap the
            #  ' and badmol is None:' from the following:
            if env.debug():
                print "debug: why does some atom in undoable state " \
                      "have .molecule = %r?" % (badmol,)
            del mols[id(badmol)]
            # but we also worry below about the atoms that had it
            # (might not be needed for _nullMol; very needed for None)
    for mol in mols.itervalues():
        mol.atoms = {}
    for atom_objkey, mol in moldict.iteritems():
        if mol not in (None, _nullMol):
            atom = modified_get(atom_objkey)
            mol.atoms[ atom.key ] = atom # WARNING: this inlines some of
                # Chunk.addatom; note: atom.key != atom_objkey
    for mol in mols.itervalues():
        try: # try/except is just for debugging
            mol.invalidate_atom_lists() # inlines some more of Chunk.addatom
        except:
            msg = "bug: why does this happen, for mol %r atoms %r? " % \
                  (mol, mol.atoms)
            print_compact_traceback( msg)
    return # from fix_all_chunk_atomsets

def _fix_all_chunk_atomsets_differential(invalmols):
    """
    Fix or properly invalidate the passed chunks, whose .atoms dicts
    the caller has directly modified (by adding or removing atoms which entered
    or left those chunks) without doing any invalidations or other changes.

    @param invalmols: a dict mapping id(mol) -> mol
                      where mol can be anything found or stored in atom.molecule
                      which has an .atoms dict of the same kind as Chunk.
                      (As of 071114, such a mol is always a Chunk.)
    """
    for mol in invalmols.itervalues():
        if mol is not _nullMol:
            # we exclude _nullMol in case it has an invalidate_atom_lists method
            # that we shouldn't call
            # [implem revised, bruce 071105; should be equivalent to prior code]
            try:
                method = \
                    mol._f_invalidate_atom_lists_and_maybe_deallocate_displist
                    #bruce 071105 changing this to call this new method
                    # _f_invalidate_atom_lists_and_maybe_deallocate_displist
                    # rather than just invalidate_atom_lists.
                    # Unfortunately it has no clear specification in the API
                    # so we can't give it a general name. Ideally we'd have a
                    # separate scan to call something like undo_update_dead
                    # on all newly dead objects, but for now, that's not easy to
                    # add (since I'd have to analyze the code to figure out
                    # where), and I only need it for chunks for one purpose.
            except:
                ## if mol is None or mol is _UNSET_:
                    # not sure which of these can happen;
                    # not worth finding out right now
                if mol is _UNSET_:
                    # actually i think that's the only one that can happen
                    print "fyi: mol is _UNSET_ in _fix_all_chunk_atomsets_differential"
                        #bruce 071114 - caller looks like it prevents this, let's find out
                        # (if not, fix the docstrings I just added which imply this!)
                    continue
                msg = "bug (or fyi if this is None or _nullMol), " \
                      "for mol %r: " % (mol,)
                print_compact_traceback( msg)
            else:
                method() # WARNING: inlines some of Chunk.addatom
                    # I think we can call this on newly dead Chunks;
                    # I'm not 100% sure that's ok, but I can't see a
                    # problem in the method and I didn't find a bug in
                    # testing. [060409]
    return

def _call_undo_update(modified):
    #060409 for differential mash_attrs, it's safe, but are the objs it's
    # called on enough? #####@@@@@
    """
    [private helper for assy_become_scanned_state:]
    Call the _undo_update method of every object we might have modified and
    which is still alive (i.e. which is passed in the <modified> arg),
    which has that method.

    [Note: caller (in differential mash_attrs case)
     presently only modifies dead objects in one special case
     (atom.molecule = None), but even if that changes, _undo_update should
     only be called on live objects; it might be useful to have other
     _undo_xxx methods called on newly dead objects, or on dead ones
     being brought back to life (before mash_attrs happens on them). #e]
    """
    # OPTIM: two big missing optims:
    # - realizing we only modified a few objects, not all of them in the state
    #   (up to the caller) [this is now implemented as of 060409]
    # - knowing that some classes don't define this method,
    #   and not scanning their instances looking for it
    for key, obj in modified.iteritems():
        ###e zap S_CACHE attrs? or depend on update funcs to
        # zap/inval/update them? for now, the latter. Review this later. ###@@@
        try:
            method = obj._undo_update
            ##e btw, for chunk, it'll be efficient to know which attrs
            # need which updating... which means, track attrs used, now!
            ##e in fact, it means, do attrs in layers and do the updates
            # of objs for each layer. if inval-style, that's fine.
            # objs can also reg themselves to be updated again
            # in later layers. [need to let them do that]
            # not yet sure how to declare attrlayers... maybe
            # test-driven devel will show me a simple way.
        except AttributeError:
            pass
        else:
            try:
                method()
            except:
                msg = "exception in _undo_update for %s; skipping it: " % \
                      safe_repr(obj)
                print_compact_traceback( msg)
                #e should also print once-per-undo-op history message;
                # maybe env.seen_before plus a user-op counter
                # can be packaged into a once-er-user-op-message
                # helper function?
                # [060410 suggestion; search for other places to do it]
            pass
        continue
    return # from _call_undo_update

updaters_in_order = []

def call_registered_undo_updaters(archive):
    #060409 seems likely to be safe/sufficient for differential mash_attrs,
    # but too slow ###@@@
    """
    [private helper for assy_become_scanned_state:]
    Call the registered undo updaters (on the overall model state, not the ones
    on individual changed objects, which should already have been called),
    in the proper order.
    [#doc more?]
    """
    assy = archive.assy
    for func in updaters_in_order:
        try:
            func(archive, assy)
        except:
            msg = "exception in some registered updater %s; skipping it: " % \
                  safe_repr(func)
            print_compact_traceback( msg)
        continue
    return # from call_registered_undo_updaters

def final_post_undo_updates(archive):
    #060409 seems likely to be safe/sufficient for differential mash_attrs ##k
    """
    [private helper for assy_become_scanned_state:]
    #doc
    """
    assy = archive.assy
    #e now inval things in every Part, especially selatoms, selmols,
    # molecules, maybe everything it recomputes [###k is this nim or not?]
    for node in assy.topnodes_with_own_parts():
        node.part._undo_update_always() # KLUGE, since we're supposed to call
            # this on every object that defines it
    assy.update_parts()
        # I thought "we don't need this, since [true] we're about to do it
        #  as a pre-checkpoint update", but although we are, we need this
        # one anyway, since it calls assy.changed() and we have to get that
        # over with before restoring the change counters after Undo/Redo.
        # [060406]
    if 1:
        #060302 4:45pm fix some unreported bugs about undo when hover
        # highlighting is active -> inappropriate highlighting
        win = env.mainwindow()
        glpane = win.glpane
        glpane.selatom = glpane.selobj = None
            # this works; but is there a better way (like some GLPane method)?
            # if there is, not sure it's fully safe!
            # [there is set_selobj, but its updates might be unsafe for
            #  this -- not reviewed, but seems likely. -- bruce 060726]
            #e Also, ideally glpane should do this itself in
            #  _undo_update_always, which we should call.
    return # from final_post_undo_updates

# ==

# [comment during development:]
# We'll still try to fit into the varid/vers scheme for multiple
# out of order undo/redo, since we think this is highly desirable
# for A7 at least for per-part Undo. But varids are only needed
# for highlevel things with separate ops offered.
# So a diff is just a varid-ver list and a separate operation...
# which can ref shared checkpoints if useful. It can ref both
# cps and do the diff lazily if you want. It's an object,
# which can reveal these things... it has facets... all the
# same needs come up again... maybe it's easier to let the facets
# be flyweight and ref shared larger pieces and just remake themselves?

_cp_counter = 0

class Checkpoint:
    """
    Represents a slot to be filled (usually long after object is first created)
    with a snapshot of the model's undoable state. API permits snapshot data (self.state) to be
    filled in later, or (if implem supports) defined by a diff from the state of another checkpoint.

    Some things done in the calling code (esp. fill_checkpoint) will probably be moved into methods of this class eventually.

    Self.state will not exist until the state-data is fully defined (unless a future revision supports its being
    some sort of lazily-valued expr which indicates a lazily filled diff and a prior checkpoint).

    Self.complete is a boolean which is True once the snapshot contents are fully defined. As of 060118 this is
    the same as hasattr(self, 'state'), but if self.state can be lazy then it might exist with self.complete still being false.

    The main varid_ver might exist right away, but the ones that depend on the difference with prior state won't exist
    until the set of differences is known.

    Note: it is good to avoid letting a checkpoint contain a reference to its assy or archive or actual model objects,
    since those would often be cyclic refs or refs to garbage, and prevent Python from freeing things when it should.
    """
    def __init__(self, assy_debug_name = None):
        # in the future there might be a larger set of varid_ver pairs based on the data changes, but for now there's
        # one main one used for the entire undoable state, with .ver also usable for ordering checkpoints; this will be retained;
        # cp.varid will be the same for any two checkpoints that need to be compared (AFAIK).
        self.varid = make_assy_varid(assy_debug_name)
        global _cp_counter
        _cp_counter += 1
        self.cp_counter = _cp_counter ###k not yet used; might help sort Redos, but more likely we'll use some metainfo
        ## self.ver = 'ver-' + `_cp_counter` # this also helps sort Redos
        self.ver = None # not yet known (??)
        self.complete = False # public for get and set
        if debug_undo2:
            print "debug_undo2: made cp:", self
        return
    def store_complete_state(self, state):
        self.state = state # public for get and set and hasattr; won't exist at first
        self.complete = True
        return
    def __repr__(self):
        self.update_ver_kluge()
        if self.complete:
            return "<Checkpoint %r varid=%r, ver=%r, state id is %#x>" % (self.cp_counter, self.varid, self.ver, id(self.state))
        else:
            #e no point yet in hasattr(self, 'state') distinction, since always false as of 060118
            assert not hasattr(self, 'state')
            return "<Checkpoint %r varid=%r, ver=%r, incomplete state>" % (self.cp_counter, self.varid, self.ver)
        pass
    def varid_ver(self): ###@@@ this and the attrs it returns will be WRONG when there's >1 varid_ver pair
        """Assuming there is one varid for entire checkpoint, return its varid_ver pair.
        Hopefully this API and implem will need revision for A7 since assumption will no longer be true.
        """
        self.update_ver_kluge()
        if self.ver is None:
            if debug_flags.atom_debug:
                print "atom_debug: warning, bug?? self.ver is None in varid_ver() for", self ###@@@
        return self.varid, self.ver
    def update_ver_kluge(self):
        try:
            mi = self.metainfo # stored by outside code (destined to become a method) when we're finalized
        except:
            pass
        else:
            self.ver = mi.assy_change_indicators
        return
    def next_history_serno(self):#060301
        try:
            mi = self.metainfo # stored by outside code (destined to become a method) when we're finalized
        except:
            return -1
        else:
            return mi.next_history_serno
        pass

    pass # end of class Checkpoint

class SimpleDiff:
    """
    Represent a diff defined as going from checkpoint 0 to checkpoint 1
    (in that order, when applied);
    also considered to be an operation for applying that diff in that direction.
    Also knows whether that direction corresponds to Undo or Redo,
    and might know some command_info about the command that adds changes to this diff
    (we assume only one command does that, i.e. this is a low-level unmerged diff and commands are fully tracked/checkpointed),
    and (maybe, in future) times diff was created and last applied, and more.
       Neither checkpoint needs to have its state filled in yet, except for our apply_to method.
    Depending on how and when this is used they might also need their varid_ver pairs for indexing.
    [Note: error of using cp.state too early, for some checkpoint cp, are detected by that attr not existing yet.]
    """
    default_opts = dict()
    default_command_info = dict(cmdname = "operation", n_merged_changes = 0)
        # client code will directly access/modify self.command_info['n_merged_changes'] [060312], maybe other items;
        # but to save ram, we don't do _offered = False or _no_net_change = False, but let client code use .get() [060326]
    suppress_storing_undo_redo_ops = False
    assert_no_changes = False
    destroyed = False
    def __init__(self, cp0, cp1, direction = 1, **options):
        """direction +1 means forwards in time (apply diff for redo), -1 means backwards (apply diff for undo),
        though either way we have to keep enough info for both redo and undo;
        as of 060126 there are no public options, but one private one for use by self.reverse_order().
        """
        self.cps = cp0, cp1
        self.direction = direction
        self.options = options # self.options is for use when making variants of self, like reverse_order
        self.opts = dict(self.default_opts)
        self.opts.update(options) # self.opts is for extracting actual option values to use (could be done lazily) [not yet used]
        self.key = id(self) #e might be better to not be recycled, but this should be ok for now
        # self.command_info: make (or privately be passed) a public mutable dict of command metainfo,
        # with keys such as cmd_name (#e and history sernos? no, those should be in checkpoint metainfo),
        # shared between self and self.reverse_order() [060126]
        self.command_info = self.options.get('_command_info_dict', dict(self.default_command_info) )
        self.options['_command_info_dict'] = self.command_info # be sure to pass the same shared dict to self.reverse_order()
        return
    def finalize(self, assy):
        ####@@@@ 060123 notyetcalled; soon, *this* is what should call fill_checkpoint on self.cps[1]!
        # let's finish this, 060210, so it can be tested, then done differently in BetterDiff
        """Caller, which has been letting model changes occur which are meant to be recorded in this diff,
        has decided it's time to finalize this diff by associating current model state with self.cps[1]
        and recording further changes in a new diff, which we(?) will create and return (or maybe caller will do that
        after we're done, not sure; hopefully caller will, and it'll also cause changetracking to go there --
        or maybe it needs to have already done that??).
           But first we'll store whatever we need to about the current model state, in self and/or self.cps.
        So, analyze the low-level change records to make compact diffs or checkpoint saved state,
        and record whatever else needs to be recorded... also make up new vers for whatever varids we think changed
        (the choice of coarseness of which is a UI issue) and record those in this diff and also in whatever model-related place
        records the "current varid_vers" for purposes of making undo/redo available ops for menus.
        """
        assert self.direction == 1
        #e figure out what changed in model, using scan of it, tracking data already in us, etc
        #####@@@@@ call fill_checkpoint
        #e make up vers for varids changed
        # *this* is what should call fill_checkpoint on self.cps[1]!
    def RAM_guess_when_finalized(self): #060323
        """Return a rough guess about the RAM usage to be attributed to keeping this Undoable op on the Undo stack.
        This must be called only when this diff has been finalized and is still undoable.
        Furthermore, as a temporarily kluge, it might be necessary to call it only once and/or in the proper Undo stack order.
        """
        # Current implem is basically one big kluge, starting with non-modularity of finding the DiffObj to ask.
        # When the Undo stack becomes a graph (or maybe even per-Part stacks), we'll have to replace this completely.
        assert self.direction == -1 # we should be an Undo diff
        s1 = self.cps[1].state
        s0 = self.cps[0].state
        return s0._relative_RAM(s1)
    def reverse_order(self):#####@@@@@ what if merged??
        return self.__class__(self.cps[1], self.cps[0], - self.direction, **self.options)
    def you_have_been_offered(self): #bruce 060326 re bug 1733
        """You (self) have been offered in the UI (or made the Undo toolbutton become enabled),
        so don't change your mind and disappear, even if it turns out you get merged
        with future ops (due to lack of autocp) and you represent no net changes;
        instead, just let this affect your menu_desc. One important reason for this is
        that without it, a user hitting Undo could inadvertently Undo the *prior* item
        on the Undo stack, since only at that point would it become clear that you contained
        no net changes.
        """
        self.command_info['_offered'] = True # this alone is not enough. we need a real change counter difference
        # or we have no way to get stored and indexed. Well, we have one (for awhile anyway -- that's why we got offered),
        # but we also need a real diff, or they'll get reset... we may even need a real but distinct change counter for this
        # since in future we might reset some chg counters if their type of diff didn't occur.
        # (Or would it be correct to treat this as a model change? no, it would affect file-mod indicator... should it??? yes...)
        # What we ended up doing is a special case when deciding how to store the diff... search for _offered to find it.
        return
    def menu_desc(self):#####@@@@@ need to merge self with more diffs, to do this?? -- yes, redo it inside the MergingDiff ##e
        main = self.optype() # "Undo" or "Redo"
        include_history_sernos = not not env.prefs[historyMsgSerialNumber_prefs_key] #060309; is this being checked at the right time??
        if include_history_sernos:
            hist = self.history_serno_desc()
        else:
            hist = ""
        if self.command_info['n_merged_changes']:
            # in this case, put "changes" before hist instead of cmdname after it
            # (maybe later it'll be e.g. "selection changes")
            ##e should we also always put hist in parens?...
            # now, hist also sees this flag and has special form BUT ONLY WHILE BEING COLLECTED... well, it could use parens always...
            ##e in case of only one cmd so far, should we not do this different thing at all?
            # (not sure, it might help you realize autocp is disabled)
            changes_desc = self.changes_desc()
            if changes_desc:
                main += " %s" % (changes_desc,)
        if hist:
            # this assumes op_name is present; if not, might be better to remove '.' and maybe use parens around numbers...
            # but i think it's always present (not sure) [060301]
            main += " %s" % (hist,)
        if not self.command_info['n_merged_changes']:
            op_name = self.cmdname()
            if op_name:
                main += " %s" % (op_name,)
        else:
            # [bruce 060326 re bug 1733:]
            # merged changes might end up being a noop, but if they were offered in the UI, we can't retract that
            # or we'll have bug 1733, or worse, user will Undo the prior op without meaning to. So special code elsewhere
            # detects this, keeps the diff in the undo stack, and stores the following flag:
            if self.command_info.get('_no_net_change', False):
                main += " (no net change)"
        return main
    def history_serno_desc(self): #060301; split out 060312
        "describe history serno range, if we have one; always return a string, maybe null string; needs to work when last serno unknown"
        if self.direction == 1:
            start_cp, end_cp = self.cps
        else:
            end_cp, start_cp = self.cps
        s1 = start_cp.next_history_serno()
        s2 = end_cp.next_history_serno()
        if s2 == -1: #060312 guess for use when current_diff.command_info['n_merged_changes'], and for direction == -1
            if not self.command_info['n_merged_changes'] and env.debug():
                print "debug: that's weird, command_info['n_merged_changes'] ought to be set in this case"
            return "(%d.-now)" % (s1,)

        n = s2 - s1
        if n < 0:
            print "bug in history serno order", s1, s2, self.direction, self
            # this 's1,s2 = s2,s1', the only time it happened, just made it more confusing to track down the bug, so zap it [060312]
            pass
##            n = -n
##            s1,s2 = s2,s1
        range0 = s1
        range1 = s2 - 1
        if n == 0:
            ## hist = ""
            #060304 we need to know which history messages it came *between*. Not sure what syntax should be...
            # maybe 18 1/2 for some single char that looks like 1/2?
            ## hist = "%d+" % range1 # Undo 18+ bla... dubious... didn't look understandable.
            hist = "(after %d.)" % range1 # Undo (after 18.) bla
            if debug_pref("test unicode one-half in Undo menutext", Choice_boolean_False): #060312
                hist = u"%d\xbd" % range1 # use unicode "1/2" character instead ( without u"", \xbd error, \x00bd wrong )
        elif n == 1:
            assert range0 == range1
            hist = "%d." % range1
        else:
            hist = "%d.-%d." % (range0, range1) #bruce 060326 added the first '.' of the two, for uniformity
        if self.command_info['n_merged_changes'] and hist and hist[0] != '(' and hist[-1] != ')':
            return "(%s)" % (hist,)
        return hist
    def cmdname(self):
        return self.command_info['cmdname']
    def changes_desc(self):#060312
        return "changes" #e (maybe later it'll be e.g. "selection changes")
    def varid_vers(self):#####@@@@@ need to merge self with more diffs, to do this??
        "list of varid_ver pairs for indexing"
        return [self.cps[0].varid_ver()]
    def apply_to(self, archive):###@@@ do we need to merge self with more diffs, too? [see class MergingDiff]
        "apply this diff-operation to the given model objects"
        cp = self.cps[1]
        assert cp.complete
        assy = archive.assy
        #bruce 060407 revised following call, no longer goes thru an assy method
        assy_become_state(assy, cp.state, archive)
            ###e this could use a print_compact_traceback with redmsg...
            # note: in present implem this might effectively redundantly do some of restore_view() [060123]
            # [as of 060407 i speculate it doesn't, but sort of by accident, i.e. due to defered category collection of view objs]
        cp.metainfo.restore_view(assy)
            # note: this means Undo restores view from beginning of undone command,
            # and Redo restores view from end of redone command.
            #e (Also worry about this when undoing or redoing a chain of commands.)
            # POSSIBLE KLUGE: with current [not anymore] implem,
            # applying a chain of several diffs could be done by applying the last one.
            # The current code might perhaps do this (and thus become wrong in the future)
            # when the skipped diffs are empty or have been merged -- I don't know.
            # This will need fixing once we're merging any nonempty diffs. ##@@ [060123]
            # Update 060407: I don't think this is an issue now (for some time), since we traverse diffs on the stack
            # to reach checkpoints, and then tell those "restore the state you saved",
            # and those do this by merging a chain of diffs but that's their business.
        cp.metainfo.restore_assy_change_indicators(assy) # change current-state varid_vers records
        archive.set_last_cp_after_undo(cp) #060301
        return
    def optype(self):
        return {1: "Redo", -1: "Undo"}[self.direction]
    def __repr__(self):
        if self.destroyed:
            return "<destroyed SimpleDiff at %#x>" % id(self) #untested [060301]
        return "<%s key %r type %r from %r to %r>" % (self.__class__.__name__, self.key, self.optype(), self.cps[0], self.cps[1])
    def destroy(self):
        self.destroyed = True
        self.command_info = self.opts = self.options = self.cps = None
        # no cycles, i think, but do the above just in case
        ###e now, don't we need to remove ourself from archive.stored_ops?? ###@@@
    pass # end of class SimpleDiff

# ==

# commenting out SharedDiffopData and BetterDiff 060301 1210pm
# since it looks likely SimpleDiff will use differentially-defined states without even knowing it,
# just by having states in the checkpoints which know it themselves.

##class SharedDiffopData: ##@@ stub, apparently, as of 060216;....

# ==

_last_real_class_for_name = {}

def undo_classname_for_decls(class1):
    """
    Return Undo's concept of a class's name for use in declarations,
    given either the class or the name string. For dotted classnames (of builtin objects)
    this does not include the '.' even if class1.__name__ does (otherwise the notation
    "classname.attrname" would be ambiguous). Note that in its internal object analysis tables,
    classnames *do* include the '.' if they have one (if we have any tables of names,
    as opposed to tables of classes).
    """
    try:
        res = class1.__name__ # assume this means it's a class
    except AttributeError:
        res = class1 # assume this means it's a string
    else:
        res = res.split('.')[-1] # turn qt.xxx into xxx
        assert not '.' in res # should be impossible here
        #e should assert it's really a class -- need to distinguish new-style classes here??
        _last_real_class_for_name[res] = class1 ##k not sure if this is enough to keep that up to date
    assert type(res) == type("name")
    assert not '.' in res, 'dotted classnames like %r are not allowed, since then "classname.attrname" would be ambiguous' % (res,)
    return res

class _testclass: pass

assert undo_classname_for_decls(_testclass) == "_testclass"
assert undo_classname_for_decls("_testclass") == "_testclass"


_classname_for_nickname = {}

def register_class_nickname(name, class1): # not used as of before 080702, but should be kept
    """
    Permit <name>, in addition to class1.__name__ (or class1 itself if it's a string),
    to be used in declarations involving class1 to the Undo system.
       This should be used only (or mainly) when the actual class name is deprecated and the class is slated
    to be renamed to <name> in the future, to permit declarations to use the preferred name in advance.
    Internally (for purposes of state decls), the Undo system will still identify all classes by their value of __name__
    (or its last component [I think], if __name__ contains a '.' like for some built-in or extension classes).
    """
    assert not '.' in name
    realname = undo_classname_for_decls(class1)
    _classname_for_nickname[name] = realname
    return

#e refile, in this file or another? not sure.

def register_undo_updater( func, updates = (), after_update_of = () ):
    # Note: as of 060314, this was nim, with its effect kluged elsewhere.
    # But a month or two before 071106 that changed; ericm made it active
    # in order to remove an import cycle.
    """
    Register <func> to be called on 2 args (archive, assy) every time some AssyUndoArchive mashes some
    saved state into the live objects of the current state (using setattr) and needs to fix things that might
    have been messed up by that or might no longer be consistent.
       The optional arguments <updates> and <after_update_of> affect the order in which the registered funcs
    are run, as described below. If not given for some func, its order relative to the others is arbitrary
    (and there is no way for the others to ask to come before or after it, even if they use those args).
       The ordering works as follows: to "fully update an attr" means that Undo has done everything it might
    need to do to make the values (and presence or absense) of that attr correct, in all current objects of
    that attr's class (including objects Undo needs to create as part of an Undo or Redo operation).
       The things it might need to do are, in order: its own setattrs (or delattrs?? ###k) on that attr;
    that class's _undo_update function; and any <funcs> registered with this function (register_undo_updater)
    which list that attr or its class(??) in their optional <updates> argument (whose syntax is described below).
       That defines the work Undo needs to do, and some of the ordering requirements on that work. The only other
    requirement is that each registered <func> which listed some attrs or classes in its optional
    <after_update_of> argument can't be run until those attrs or classes have been fully updated.
    (To "fully update a class", listed in <after_update_of>, means to update every attr in it which has been
    declared to Undo, except any attrs listed individually in the <updates> argument. [###k not sure this is right or practical])
       (If these requirements introduce a circularity, that's a fatal error we'll detect at runtime.)
       The syntax of <updates> and <after_update_of> is a sequence of classes, classnames, or "classname.attrname"
    strings. (Attrname strings can't be given without classnames, even if only one class has a declared attribute
    of that name.)
       Classnames don't include module names (except for builtin objects whose __class__._name__ includes them).
    All classes of the same name are considered equivalent. (As of 060223 the system isn't designed
    to support multiple classes of the same name, but it won't do anything to stop you from trying. In the future
    we might add explicit support for runtime reloading of classes and upgrading of their instances to the new versions
    of the same classes.)
       Certain classes have nicknames (like 'Chunk' for class molecule,
    before it was renamed) which can be used here because they've been
    specifically registered as permitted, using register_class_nickname.
       [This docstring was written before the code was, and when only one <func> was being registered so far,
    so it's subject to revision from encountering reality (or to being out of date if that revision hasn't
    happened yet). ###k]
    """
    global updaters_in_order
    # the following single line implements a simpler registration than
    # the one envisioned by the pseudocode, but adequate for current
    # usage.
    updaters_in_order += [func]
    ## print "register_undo_updater ought to register %r but it's nim, or maybe only use of the registration is nim" % func
    # pseudocode
    if "pseudocode":
        from utilities.constants import noop
        somethingYouHaveToDo = progress_marker = canon = this_bfr_that = noop
    task = somethingYouHaveToDo(func)
    for name in updates:
        name = progress_marker(canon(name), 'target')
        this_bfr_that(task, name)
    for name in after_update_of:
        name = progress_marker(canon(name), 'requirement')
        # elsewhere we'll set up "attr (as target) comes before class comes before attr (as requirement)" and maybe
        # use different sets of attrs on each side (S_CACHE or not)
        this_bfr_that(name, task)
    return

""" example:
register_undo_updater( _undo_update_Atom_jigs,
                       updates = ('Atom.jigs', 'Bond.pi_bond_obj'),
                       after_update_of = ('Assembly', Node, 'Atom.bonds') # Node also covers its subclasses Chunk and Jig.
                           # We don't care if Atom is updated except for .bonds, nor whether Bond is updated at all,
                           # which is good because *we* are presumably a required part of updating both of those classes!
                    )
"""

# ==

# These three functions go together as one layer of the API for using checkpoints.
# They might be redundant with what's below or above them (most likely above, i.e.
# they probably ought to be archive methods),
# but for now it's clearest to think about them in this separate layer.

def make_empty_checkpoint(assy, cptype = None):
    """
    Make a new Checkpoint object, with no state.
    Sometime you might want to call fill_checkpoint on it,
    though in the future there will be more incremental options.
    """
    cp = Checkpoint(assy_debug_name = assy._debug_name)
        # makes up cp.ver -- would we ideally do that here, or not?
    cp.cptype = cptype #e put this inside constructor? (i think it's always None or 'initial', here)
    cp.assy_change_indicators = None # None means they're not yet known
    return cp

def current_state(archive, assy, **options):
    """
    Return a data-like representation of complete current state of the given assy;
    initial flag [ignored as of bfr 060407] means it might be too early (in assy.__init__) to measure this
    so just return an "empty state".
       On exception while attempting to represent current state, print debug error message
    and return None (which is never used as return value on success).
       Note [060407 ###k]: this returns a StateSnapshot, not a StatePlace.
    """
    try:
        #060208 added try/except and this debug_pref
        pkey = "simulate one undo checkpoint bug"
        if debug_pref("simulate bug in next undo checkpoint", Choice_boolean_False, prefs_key = pkey):
            env.prefs[pkey] = False
            assert 0, "this simulates a bug in this undo checkpoint"
        data = mmp_state_from_assy(archive, assy, **options)
        assert isinstance( data, StateSnapshot) ###k [this is just to make sure i am right about it -- i'm not 100% sure it's true - bruce 060407]
    except:
        print_compact_traceback("bug while determining state for undo checkpoint %r; subsequent undos might crash: " % options )
            ###@@@ need to improve situation in callers so crash warning is not needed (mark checkpoint as not undoable-to)
            # in the meantime, it might not be safe to print a history msg now (or it might - not sure); I think i'll try:
        from utilities.Log import redmsg # not sure this is ok to do when this module is imported, tho probably it is
        env.history.message(redmsg("Bug: Internal error while storing Undo checkpoint; it might not be safe to Undo to this point."))
        data = None
    return data

def fill_checkpoint(cp, state, assy): #e later replace calls to this with cp method calls
    """
    @type assy: assembly.assembly
    """
    if not isinstance(state, StatePlace):
        if env.debug():
            print "likely bug: not isinstance(state, StatePlace) in fill_cp, for", state #060407
    env.change_counter_checkpoint() ###k here?? store it??
    assert cp is not None
    assert not cp.complete
    cp.store_complete_state(state)
    # Note: we store assy.all_change_indicators() in two places, cp and cp.metainfo, both of which are still used as of 060227.
    # Each of them is used in more than one place in this file, I think (i.e. 4 uses in all, 2 for each).
    # This ought to be fixed but I'm not sure how is best, so leaving both places active for now. [bruce 060227]
    cp.assy_change_indicators = assy.all_change_indicators() #060121, revised to use all_ 060227
    cp.metainfo = checkpoint_metainfo(assy) # also stores redundant assy.all_change_indicators() [see comment above]
        # this is only the right time for this info if the checkpoint is filled at the right time.
        # We'll assume we fill one for begin and end of every command and every entry/exit into recursive event processing
        # and that ought to be enough. Then if several diffs get merged, we have lots of cp's to combine this info from...
        # do we also need to save metainfo at specific diff-times *between* checkpoints? Not sure yet -- assume no for now;
        # if we need this someday, consider "internal checkpoints" instead, since we might need to split the diffsequence too.
    return

# ==

class checkpoint_metainfo:
    """
    Hold the metainfo applicable at some moment in the undoable state...
    undecided whether one checkpoint and/or diff might have more than one of these.
    E.g. for a diff we might have this at start of first command in it, at first and last diff in it, and at end of command;
    for checkpoint we might have it for when we finalize it.

    Don't hold any ref to assy or glpane itself!
    """
    def __init__(self, assy):
        """
        @type assy: assembly.assembly
        """
        self.set_from(assy) #e might not always happen at init??
    def set_from(self, assy):
        try:
            glpane = assy.o # can fail even at end of assy.__init__, but when it does, assy.w.glpane does too
        except:
            self.view = "initial view not yet set - stub, will fail if you undo to this point"
            if env.debug():#060301 - does this ever happen (i doubt it) ###@@@ never happens; someday analyze why not [060407]
                print "debug:", self.view
        else:
            self.view = glpane.current_view_for_Undo(assy) # Csys object (for now), with an attribute pointing out the current Part
            ###e should this also save the current mode, considered as part of the view??? [060301]
        self.time = time.time()
        #e cpu time?
        #e glpane.redraw_counter? (sp?)
        self.assy_change_indicators = assy.all_change_indicators()
        # history serno that will be used next
        self.next_history_serno = env.last_history_serno + 1 # [060301]
            ###e (also worry about transient_msgs queued up, re this)
        #e current cmd on whatever stack of those we have? re recursive events if this matters? are ongoing tasks relevant??
        #e current part or selgroup or its index [#k i think this is set in current_view_for_Undo]
        return
    def restore_view(self, assy):
        "restore the view & current part from self (called at end of an Undo or Redo command)"
            # also selection? _modified? window_caption (using some new method on assy that knows it needs to do that)?
        glpane = assy.o
        glpane.set_view_for_Undo(assy, self.view)
            # doesn't animate, for now -- if it does, do we show structure change before, during, or after?
            #e sets current selgroup; doesn't do update_parts; does it (or caller) need to?? ####@@@@
        #e caller should do whatever updates are needed due to this (e.g. gl_update)
    def restore_assy_change_indicators(self, assy):
        #e ... and not say it doesn't if the only change is from a kind that is not normally saved.
        if debug_change_indicators:
            print "restore_assy_change_indicators begin, chg ctrs =", assy.all_change_indicators()
        assy.reset_changed_for_undo( self.assy_change_indicators) # never does env.change_counter_checkpoint() or the other one
        if debug_change_indicators:
            print "restore_assy_change_indicators end, chg ctrs =", assy.all_change_indicators()
    pass

# ==

from idlelib.Delegator import Delegator
# print "Delegator",Delegator,type(Delegator),`Delegator`

class MergingDiff(Delegator): ###@@@ this is in use, but has no effect [as of bfr 060326].
    """
    A higher-level diff, consisting of a diff with some merging options
    which cause more diffs to be applied with it
    """
    # When this actually merges, it needs to override menu_desc & cp's, too. ####@@@@
    def __init__(self, diff, flags = None, archive = None):
        Delegator.__init__(self, diff) # diff is now self.delegate; all its attrs should be constant since they get set on self too
        self.flags = flags
        self.archive = archive # this ref is non-cyclic, since this kind of diff doesn't get stored anywhere for a long time
    def apply_to(self, archive):
        res = self.delegate.apply_to(archive)
        # print "now we should apply the diffs we would merge with", self #####@@@@@
        return res
    # def __del__(self):
    #     print "bye!" # this proves it's readily being deleted...
    pass

# ==

class AssyUndoArchive: # modified from UndoArchive_older and AssyUndoArchive_older # TODO: maybe assy.changed will tell us...
    """
    #docstring is in older code... maintains a series (or graph) of checkpoints and diffs connecting them....
     At most times, we have one complete ('filled') checkpoint, and a subsequent incomplete one (subject to being modified
    by whatever changes other code might next make to the model objects).
     Even right after an undo or redo, we'll have a checkpoint
    that we just forced the model to agree with, and another one to hold whatever changes the user might make next
    (if they do anything other than another immediate undo or redo). (Hopefully we'll know whether that other one has
    actually changed or not, but in initial version of this code we might have to guess; maybe assy.changed will tell us.)
     If user does an undo, and then wants to change the view before deciding whether to redo, we'd better not make that
    destroy their ability to redo! So until we support out-of-order undo/redo and a separate undo stack for view changes
    (as it should appear in the UI for this), we won't let view changes count as a "new do" which would eliminate the redo stack.

    Each AssyUndoArchive is created by an AssyUndoManager, in a 1 to 1
    relationship.  An AssyUndoManager is created by an assembly, also
    in a 1 to 1 relationship, although the assembly may choose to not
    create an AssyUndoManager.  So, there is essentially one
    AssyUndoArchive per assembly, if it chooses to have one.
    """

    next_cp = None
    current_diff = None
    format_options = dict(use_060213_format = True)
        # Note: this is never changed and use_060213_format = False is not supported, but preserve this until we have another format option
        # that varies, in case we need one for diffing some attrs in special ways. Note: use_060213_format appears in state_utils.py too.
        # [bruce 060314]

    copy_val = state_utils.copy_val #060216, might turn out to be a temporary kluge ###@@@

    _undo_archive_initialized = False

    def __init__(self, assy):
        """
        @type assy: assembly.assembly
        """
        self.assy = assy # represents all undoable state we cover (this will need review once we support multiple open files)

        self.obj_classifier = obj_classifier()

        self.objkey_allocator = oka = objkey_allocator()
        self.obj4key = oka.obj4key # public attr, maps keys -> objects
            ####@@@@ does this need to be the same as atom keys? not for now, but maybe yes someday... [060216]

        self.stored_ops = {} # map from (varid, ver) pairs to lists of diff-ops that implement undo or redo from them;
            # when we support out of order undo in future, this will list each diff in multiple places
            # so all applicable diffs will be found when you look for varid_ver pairs representing current state.
            # (Not sure if that system will be good enough for permitting enough out-of-order list-modification ops.)

        self.subbing_to_changedicts_now = False # whether this was initially False or True wouldn't matter much, I think...
        self._changedicts = [] # this gets extended in self._archive_meet_class;
            #060404 made this a list of (changedict, ourdict) pairs, not just a list of changedicts
            # list of pairs of *external* changedicts we subscribe to -- we are not allowed to directly modify them! --
            #  and ourdicts for them, the appropriate one of self.all_changed_Atoms or self.all_changed_Bonds)
            # (in fact it might be better to just list their cdp's rather than the dicts themselves; also more efficient ##e)
        ## self.all_changed_objs = {} # this one dict subscribes to all changes on all attrs of all classes of object (for now)
        self.all_changed_Atoms = {} # atom.key -> atom, for all changed Atoms (all attrs lumped together; this could be changed)
        self.all_changed_Bonds = {} # id(bond) -> bond, for all changed Bonds (all attrs)
        self.ourdicts = (self.all_changed_Atoms, self.all_changed_Bonds,) #e use this more
        # rest of init is done later, by self.initial_checkpoint, when caller is more ready [060223]
        ###e not sure were really initialized enough to return... we'll see
        return

    def sub_or_unsub_changedicts(self, subQ): #060329, rewritten 060330
        if self.subbing_to_changedicts_now != subQ:
            del self.subbing_to_changedicts_now # we'll set it to a new value (subQ) at the end;
                # it's a bug if something wants to know it during this method, so the temporary del is to detect that
            ourdicts = self.ourdicts
            if subQ:
                for ourdict in ourdicts:
                    if ourdict:
                        print "bug: archive's changedict should have been empty but contains:", ourdict
            cd_ods = self._changedicts[:]
            for changedict, ourdict in cd_ods:
                self.sub_or_unsub_to_one_changedict(subQ, changedict, ourdict)
                continue
                #e other things to do in some other method with each changedict:
                # or update?
                # cdp.process_changes()
            if not subQ:
                for ourdict in ourdicts:
                    ourdict.clear() # not sure we need this, but if we're unsubbing we're missing future changes
                        # so we might as well miss the ones we were already told about (might help to free old objects?)
            assert map(id, cd_ods) == map(id, self._changedicts) # since new cds during that loop are not supported properly by it
                # note, this is comparing ids of tuples, but since the point is that we didn't change _changedicts,
                # that should be ok. We can't use == since when we get to the dicts in the tuples, we have to compare ids.
            self.subbing_to_changedicts_now = subQ
        return

    def sub_or_unsub_to_one_changedict(self, subQ, changedict, ourdict):
        subkey = id(self)
        cdp = changedicts._cdproc_for_dictid[id(changedict)]
        if subQ:
            cdp.subscribe(subkey, ourdict)
        else:
            cdp.unsubscribe(subkey)
        return

    def _clear(self):
        """
        [private helper method for self.clear_undo_stack()]
        Clear our main data stores, which are set up in __init__,
        and everything referring to undoable objects or objkeys.
        (But don't clear our obj_classifier.)

        Then take an initial checkpoint of all reachable data.
        """
        self.current_diff.destroy()
        self.current_diff = None
        self.next_cp = None
        self.stored_ops = {}
        self.objkey_allocator.clear() # after this, all existing keys (in diffs or checkpoints) are nonsense...
        # ... so we'd better get rid of them (above and here):
        self._undo_archive_initialized = False
        self.initial_checkpoint() # should we clean up the code by making this the only way to call initial_checkpoint?
        return

    def initial_checkpoint(self):
        """
        Make an initial checkpoint, which consists mainly of
        taking a complete snapshot of all undoable state
        reachable from self.assy.
        """
        # WARNING: this is called twice by our undo_manager's clear_undo_stack
        # method (though only once by self's method of that name)
        # the first time it runs, but only once each subsequent time.
        # (The first call is direct, when the undo_manager is not initialized;
        #  the second call always occurs, via self.clear_undo_stack, calling
        #  self._clear, which calls this method.)
        #
        # If the assy has lots of data by that time, it will thus be fully
        # scanned twice, which is slow.
        #
        # Older comments imply that this situation arose unintentionally
        # and was not realized at first. In principle, two calls of this are not
        # needed, but in practice, it's not obvious how to safely remove
        # one of them. See the clear_undo_stack docstring for advice about
        # not wasting runtime due to this, which is now followed in our
        # callers. [bruce 080229 comment]

        assert not self._undo_archive_initialized
        assy = self.assy
        cp = make_empty_checkpoint(assy, 'initial') # initial checkpoint
        #e the next three lines are similar to some in self.checkpoint --
        # should we make self.set_last_cp() to do part of them? compare to do_op's effect on that, when we code that. [060118] [060301 see also set_last_cp_after_undo]
        cursnap = current_state(self, assy, initial = True, **self.format_options)
             # initial = True is ignored; obs cmt: it's a kluge to pass initial; revise to detect this in assy itself
        state = StatePlace(cursnap) #####k this is the central fix of the initial-state kluge [060407]
        fill_checkpoint(cp, state, assy)
        if self.pref_report_checkpoints():
            self.debug_histmessage("(initial checkpoint: %r)" % cp)
        self.last_cp = self.initial_cp = cp
##        self.last_cp_arrival_reason = 'initial' # why we got to the situation of model state agreeing with this, when last we did
            #e note, self.last_cp will be augmented by a desc of varid_vers pairs about cur state;
            # but for out of order redo, we get to old varid_vers pairs but new cp's; maybe there's a map from one to the other...
            ###k was this part of UndoManager in old code scheme? i think it was grabbed out of actual model objects in UndoManager.
        self.sub_or_unsub_changedicts(False) # in case we've been called before (kluge)
        self._changedicts = [] # ditto
        self.sub_or_unsub_changedicts(True)
        self.setup_changedicts() # do this after sub_or_unsub, to test its system for hearing about redefined classes later [060330]
        self._undo_archive_initialized = True # should come before _setup_next_cp
        self._setup_next_cp() # don't know cptype yet (I hope it's 'begin_cmd'; should we say that to the call? #k)
        ## self.notify_observers() # current API doesn't permit this to do anything during __init__, since subs is untouched then
        return

    def setup_changedicts(self):
        assert not self._changedicts, "somehow setup_changedicts got called twice, since we already have some, "\
               "and calling code didn't kluge this to be ok like it does in initial_checkpoint in case it's called from self._clear"
        register_postinit_object( '_archive_meet_class', self )
            # this means we are ready to receive callbacks (now and later) on self._archive_meet_class,
            # telling us about new classes whose instances we might want to changetrack
        return

    def _archive_meet_class(self, class1):
        """
        [private]
        class1 is a class whose instances we might want to changetrack.
        Learn how, and subscribe to the necessary changedicts.
        """
        ### TODO: if we've been destroyed, we ought to raise an exception
        # to get us removed from the pairmatcher that calls this method --
        # maybe a special exception that's not an error in its eyes.
        # In current code, instead, we'll raise AttributeError on _changedicts
        # or maybe on its extend method. [I ought to verify this is working.]
        changedicts0 = changedicts._changedicts_for_classid[ id(class1) ]
            # maps name to dict, but names are only unique per-class
        changedicts_list = changedicts0.values() # or .items()?
            # someday we'll want to use the dictnames, i think...
            # for now we don't need them
        ## self._changedicts.extend( changedicts_list ) -- from when ourdict
        ##   was not in there (zap this commented out line soon)
        ourdicts = {UNDO_SPECIALCASE_ATOM: self.all_changed_Atoms,
                    UNDO_SPECIALCASE_BOND: self.all_changed_Bonds}
            # note: this is a dict, but self.ourdicts is a list

##        specialcase_type = class1.__name__
##        assert specialcase_type in ('Atom', 'Bond')
##            # only those two classes are supported, for now

        # Each changetracked class has to be handled by specialcase code
        # of a type we recognize. For now there are two types, for use by
        # subclasses of Atom & Bond.
        # [Before 071114 only those two exact classes were supported.]
        #
        # This also tells us which specific set of registered changedicts
        # to monitor for changes to instances of that class.
        # (In the future we might just ask the class for those changedicts.)
        assert hasattr(class1, '_s_undo_specialcase')
        specialcase_type = class1._s_undo_specialcase
        assert specialcase_type in (UNDO_SPECIALCASE_ATOM,
                                    UNDO_SPECIALCASE_BOND)

        ourdict = ourdicts[specialcase_type]
        for cd in changedicts_list:
            self._changedicts.append( (cd, ourdict) )
            # no reason to ever forget about changedicts, I think
            # (if this gets inefficient, it's only for developers who often
            #  reload code modules -- I think; review this someday ##k)
        if self.subbing_to_changedicts_now:
            for name, changedict in changedicts0.items():
                del name
                self.sub_or_unsub_to_one_changedict(True, changedict, ourdict)
                    #e Someday, also pass its name, so sub-implem can know what
                    # we think about changes in it? Maybe; but more likely,
                    # ourdict already was chosen using the name, if name needs
                    # to be used at all.
                continue

        # optimization: ask these classes for their state_attrs decls now,
        # so later inner loops can assume the attrdicts exist.
        ###e WARNING: this won't be enough to handle new classes created at
        # runtime, while this archive continues to be in use,
        # if they contain _s_attr decls for new attrs! For that, we'd also
        # need to add the new attrs to existing attrdicts in state or diff
        # objects (perhaps lazily as we encounter them, by testing
        # len(attrdicts) (?) or some version counter).

        self.obj_classifier.classify_class( class1)

        return

    def childobj_oursQ(self, obj):
        """
        Is the given object (allowed to be an arbitrary Python object,
         including None, a list, etc)
        known to be one of *our* undoable state-holding objects?
        (Also True in present implem if obj has ever been one of ours;
         this needs review if this distinction ever matters,
         i.e. if objs once ours can later become not ours,
         without being destroyed.)

        WARNING: this is intended only for use on child-scanned
        (non-change-tracked) objects
        (i.e. all but Atoms or Bonds, as of 060406);
        it's not reliable when used on change-tracked objects when deciding
        for the first time whether to consider them ours; instead, as part
        of that decision, they might query this for child-scanned objects
        which own them, e.g. atoms might query it for atom.molecule.
        """
        #e possible optim: store self.objkey_allocator._key4obj.has_key
        # as a private attr of self
        return self.objkey_allocator._key4obj.has_key(id(obj))

    def new_Atom_oursQ(self, atom): #060405; rewritten 060406
        """
        Is a newly seen Atom object one of ours?
        [it's being seen in a changed-object set;
        the implem might assume that, I'm not sure]
        """
        #e we might optim by also requiring it to be alive;
        # review callers if this might be important
        ##e maybe we should be calling a private Atom method for this;
        # not sure, since we'd need to pass self for self.childobj_oursQ
        return self.childobj_oursQ( atom.molecule )
            # should be correct even if atom.molecule is None or _nullMol
            # (says False then)

    def new_Bond_oursQ(self, bond): #060405
        """
        Is a newly seen Bond object one of ours?
        (optional: also ok to return False if it's not alive)
        """
        ##e maybe we should be calling a private Bond method for this
        if not self.trackedobj_liveQ(bond):
            return False # seems reasonable (for any kind of object)...
                # should review/doc/comment in caller ###e
        # motivation for the above:
        # surviving that test implies a1 & a2 are not None,
        # and bond is in a1.bonds etc
        a1 = bond.atom1
        a2 = bond.atom2
        return self.new_Atom_oursQ(a1) or self.new_Atom_oursQ(a2)
            # Notes:
            # - either of these conditions ought to imply the other one;
            #   'or' is mainly used to make bugs more likely noticed;
            #   I'm not sure which of 'or' and 'and' is more robust
            #   (if no bugs, they're equivalent, and so is using only one cond).
            #   ONCE THIS WORKS, I SHOULD PROBABLY CHANGE FROM 'or' TO 'and'
            #   (and retest) FOR ROBUSTNESS. ######@@@@@@
            # - the atoms might not be "new", but (for a new bond of ours)
            #   they're new enough for that method to work.

    def attrcode_is_Atom_chunk(self, attrcode): #bruce 071114
        """
        Say whether an attrcode should be treated as Atom.molecule,
        or more precisely, as pointing to the owning chunk
        of an "atom", i.e. an instance of a class whose
        _s_undo_specialcase attribute is UNDO_SPECIALCASE_ATOM.
        """
        res = self.obj_classifier.dict_of_all_Atom_chunk_attrcodes.has_key(attrcode)
        # make sure this is equivalent to the old hardcoded version (temporary):
        assert res == (attrcode == (ATOM_CHUNK_ATTRIBUTE_NAME, 'Atom'))
            # remove when works -- will become wrong when we add Atom subclasses
        return res

    def childobj_liveQ(self, obj):
        """
        Is the given object (allowed to be an arbitrary Python object,
         including None, a list, etc) (?? or assumed ourQ??)
        a live child-scanned object in the last-scanned state
        (still being scanned, in fact), assuming it's a child-scanned object?

        WARNING: it's legal to call this for any object, but for a
        non-child-scanned but undoable-state-holding object
        which is one of ours (i.e. an Atom or Bond as of 060406),
        the return value is undefined.

        WARNING: it's not legal to call this except during a portion of
        scate-scanning which briefly sets self._childobj_dict
        to a correct value, which is a dict from id(obj) -> obj for all
        live child objects as detected earlier in the scan.

        [#e Note: if we generalize the scanning to have ordered layers
         of objects, then this dict might keep accumulating newly found
         live objects (during a single scan), so that each layer can use
         it to know which objects in the prior layer are alive.
         Right now we use it that way but with two hardcoded layers,
         "child objects" and "change-tracked objects".]
        """
        # Note: this rewritten implem is still a kluge, but not as bad
        # as ~060407's. self._childobj_dict is stored by caller (several call
        # levels up), then later set to None before it becomes invalid.
        # [060408]
        return self._childobj_dict.has_key(id(obj))

    def trackedobj_liveQ(self, obj):
        """
        Assuming obj is a legitimate object of a class we change-track
        (but not necessarily that we're the archive that tracks that instance,
         or that any archive does),
        but *not* requiring that we've already allocated an objkey for it
        (even if it's definitely ours),
        then ask its class-specific implem of _undo_aliveQ to do the following:
        - if it's one of ours, return whether it's alive
          (in the sense of being part of the *current* state of the model
           handled by this archive, where "current" means according to the
           archive (might differ from model if archive is performing an undo
            to old state(??)));
        - if it's not one of ours, return either False, or whether it's alive
          in its own archive's model (if it has one)
          (which of these to do is up to the class-specific implems,
           and our callers must tolerate either behavior).

        Never raise an exception; on errors, print message and return False.
        ###e maybe doc more from Atom._undo_aliveQ docstring?

        Note: we can assume that the caller is presently performing either a
        checkpoint, or a move to an old checkpoint,
        and that self knows the liveQ status of all non-tracked objects,
        and is askable via childobj_liveQ.

        (#e Someday we might generalize this so there is some order among
         classes, and then we can assume it knows the liveQ status of all
         instances of prior classes in the order.)
        """
        try:
            return obj._undo_aliveQ(self)
        except:
            msg = "exception in _undo_aliveQ for %s; assuming dead: " % \
                  safe_repr(obj)
            print_compact_traceback( msg)
            return False

    def get_and_clear_changed_objs(self, want_retval = True):
        """
        Clear, and (unless want_retval is false) return copies of,
        the changed-atoms dict (key -> atom) and changed-bonds dict (id -> bond).
        """
        for changedict, ourdict_junk in self._changedicts:
            cdp = changedicts._cdproc_for_dictid[id(changedict)]
            cdp.process_changes() # this is needed to add the latest changes to our own local changedict(s)
        if want_retval:
            res = dict(self.all_changed_Atoms), dict(self.all_changed_Bonds) #e should generalize to a definite-order list, or name->dict
        else:
            res = None
        self.all_changed_Atoms.clear()
        self.all_changed_Bonds.clear()
        return res

    def destroy(self): #060126 precaution
        """
        free storage, make doing of our ops illegal
        (noop with bug warning; or maybe just exception)
        """
        if self.pref_report_checkpoints():
            self.debug_histmessage("(destroying: %r)" % self)
        self.sub_or_unsub_changedicts(False)
            # this would be wrong, someone else might be using them!
            ##for cd,odjunk in self._changedicts:
            ##    cd.clear()
            # it's right to clear our own, but that's done in the method we just called.
        del self._changedicts
        self.next_cp = self.last_cp = self.initial_cp = None
        self.assy = None
        self.stored_ops = {} #e more, if it can contain any cycles -- design was that it wouldn't, but true situation not reviewed lately [060301]
        self.current_diff = None #e destroy it first?
        self.objkey_allocator.destroy()
        self.objkey_allocator = None
        return

    def __repr__(self):
        return "<AssyUndoArchive at %#x for %r>" % (id(self), self.assy) # if destroyed, assy will be None

    # ==

    def _setup_next_cp(self):
        """
        [private method, mainly for begin_cmd_checkpoint:]
        self.last_cp is set; make (incomplete) self.next_cp, and self.current_diff to go between them.
        Index it... actually we probably can't fully index it yet if that depends on its state-subset vers.... #####@@@@@
        """
        assert self._undo_archive_initialized
        assert self.next_cp is None
        self.next_cp = make_empty_checkpoint(self.assy) # note: we never know cptype yet, tho we might know what we hope it is...
        self.current_diff = SimpleDiff(self.last_cp, self.next_cp) # this is a slot for the actual diff, whose content is not yet known
            # this attr is where change-trackers would find it to tell it what changed (once we have any)
            # assume it's too early for indexing this, or needing to -- that's done when it's finalized
        return

    def set_last_cp_after_undo(self, cp): # 060301
        """
        We're doing an Undo or Redo command which has just caused actual current state (and its change_counters) to equal cp.state.
        Therefore, self.last_cp is no longer relevant, and that attr should be set to cp so further changes are measured relative to that
        (and self.current_diff and next_cp should be freshly made, forking off from it -- or maybe existing self.next_cp can be recycled for this;
        also we might need some of the flags in self.current_diff... but not the changes, I think, which either don't exist yet or are
        caused by tracking changes applied by the Undo op itself).
           (Further modelstate changes by this same Undo/Redo command are not expected and might cause bugs -- if they result in a diff,
        it would be a separate undoable diff and would prevent Redo from being available. So we might want to assert that doesn't happen,
        but if such changes *do* happen it's the logically correct consequence, so we don't want to try to alter that consequence.)
        """
        assert self._undo_archive_initialized
        assert self.last_cp is not None
        assert self.next_cp is not None
        assert self.current_diff is not None
        assert cp is not None
        assert self.last_cp is not cp # since it makes no sense if it is, though it ought to work within this routine

        # Clear the changed-object sets (maintained by change-tracking, for Atoms & Bonds), since whatever's in them will just slow down
        # the next checkpoint, but nothing needs to be in them since we're assuming the model state and archived state are identical
        # (caller has just stored archived state into model). (This should remove a big slowdown of the first operation after Undo or Redo.) [bruce 060407]
        self.clear_changed_object_sets()

        # not sure this is right, but it's simplest that could work, plus some attempts to clean up unused objects:
        self.current_diff.destroy() # just to save memory; might not be needed (probably refdecr would take care of it) since no ops stored from it yet
        self.last_cp.end_of_undo_chain_for_awhile = True # not used by anything, but might help with debugging someday; "for awhile" because we might Redo to it
        self.last_cp = cp
            ###@@@ we might need to mark cp for later freeing of its old Redo stack if we depart from it other than by another immediate Undo or Redo...
            # tho since we might depart from somewhere else on that stack, never mind, we should instead
            # just notice the departure and find the stuff to free at that time.
        # next_cp can be recycled since it's presently empty, I think, or if not, it might know something useful ####@@@@ REVIEW
        self.current_diff = SimpleDiff(self.last_cp, self.next_cp)
        self.current_diff.assert_no_changes = True # fyi: used where we check assy_change_indicators
        return

    def clear_changed_object_sets(self): #060407
        self.get_and_clear_changed_objs(want_retval = False)

    def clear_undo_stack(self): #bruce 060126 to help fix bug 1398 (open file left something on Undo stack) [060304 removed *args, **kws]
        # note: see also: comments in self.initial_checkpoint,
        # and in undo_manager.clear_undo_stack
        assert self._undo_archive_initialized
            # note: the same-named method in undo_manager instead calls
            # initial_checkpoint the first time
        if self.current_diff: #k probably always true; definitely required for it to be safe to do what follows.
            self.current_diff.suppress_storing_undo_redo_ops = True # note: this is useless if the current diff turns out to be empty.

            if 1: #060304 try to actually free storage; I think this will work even with differential checkpoints...
                self._clear()

##                #obs comments? [as of 060304]
##                #e It might be nice to also free storage for all prior checkpoints and diffs
##                # (by erasing them from stored_ops and from any other refs to them),
##                # but I'm worried about messing up too many things
##                # (since this runs from inside some command whose diff-recording is ongoing).
##                # If we decide to do that, do it after the other stuff here, to all cp's/diffs before last_cp. #e
##                # This shouldn't make much difference in practice
##                # (for existing calls of this routine, from file open & file close), so don't bother for now.
##                #
##                # In order to only suppress changes before this method is called, rather than subsequent ones too,
##                # we also do a special kind of checkpoint here.
##                self.checkpoint( cptype = "clear")
##                #
##                self.initial_cp = self.last_cp # (as of 060126 this only affects debug_undo2 prints)
            pass
        return

    def pref_report_checkpoints(self): #bruce 060127 revised meaning and menutext, same prefs key
        """
        whether to report all checkpoints which see any changes from the prior one
        """
        res = debug_pref("undo/report changed checkpoints", Choice_boolean_False,
                         prefs_key = "_debug_pref_key:" + "undo/report all checkpoints")
        return res

    def debug_histmessage(self, msg):
        env.history.message(msg, quote_html = True, color = 'gray')

    def update_before_checkpoint(self): # see if this shows up in any profiles [split this out 060309]
        "#doc"
        ##e these need splitting out (and made registerable) as "pre-checkpoint updaters"... note, they can change things,
        # ie update change_counters, but that ought to be ok, as long as they can't ask for a recursive checkpoint,
        # which they won't since only UI event processors ever ask for those. [060301]

        self.assy.update_parts() # make sure assy has already processed changes (and assy.changed has been called if it will be)
            #bruce 060127, to fix bug 1406 [definitely needed for 'end...' cptype; not sure about begin, clear]
            # note: this has been revised from initial fix committed for bug 1406, which was in assembly.py and
            # was only for begin and end cp's (but was active even if undo autocp pref was off).

        #bruce 060313: we no longer need to update mol.atpos for every chunk. See comments in chunk.py docstring about atom.index.
        # [removed commented-out code for it, 060314]

# this was never tested -- it would be needed for _s_attr__hotspot,
# but I changed to _s_attr_hotspot and _undo_setattr_hotspot instead [060404]
##        chunks = self.assy.allNodes(Chunk) # note: this covers all Parts, whereas assy.molecules only covers the current Part
##        for chunk in chunks:
##            chunk.hotspot # make sure _hotpot is valid (not killed) or None [060404]
##                # this is required for Undo Atom change-tracking to work properly, so that dead atoms (as value of _hotspot)
##                # never need to be part of the undoable state.
##                # (Needless to say, this should be made more modular by being somehow declared in class Chunk,
##                #  perhaps giving it a special _undo_getattr__hotspot or so (though support for that is nim, i think). ###e)

        return

    def checkpoint(self, cptype = None, cmdname_for_debug = "", merge_with_future = False ): # called from undo_manager
        """
        When this is called, self.last_cp should be complete, and self.next_cp should be incomplete,
        with its state defined as equalling the current state, i.e. as a diff (which is collecting current changes) from last_cp,
        with that diff being stored in self.current_diff.
        And this diff might or might not be presently empty. (#doc distinction between changes we record but don't count as nonempty,
        like current view, vs those we undo but would not save in a file (selection), vs others.)
           We should finalize self.next_cp with the current state, perhaps optimizing this if its defining diff is empty,
        and then shift next_cp into last_cp and a newly created checkpoint into next_cp, recreating a situation like the initial one.
           In other words, make sure the current model state gets stored as a possible point to undo or redo to.
           Note [060301]: similar but different cp-shifting might occur when an Undo or Redo command is actually done.
        Thus, if this is the end-checkpoint after an Undo command, it might find last_cp being the cp "undone to" by that command
        (guess as of 060301 1159am, nim #k ###@@@).
        """
        if not self._undo_archive_initialized:
            if env.debug():
                print_compact_stack("debug note: undo_archive not yet initialized (maybe not an error)")
            return

##        if 0: # bug 1440 debug code 060320, and 1747 060323
##            print_compact_stack("undo cp, merge=%r: " % merge_with_future)

        if not merge_with_future:
            #060312 added 'not merge_with_future' cond as an optim; seems ok even if this would set change_counters,
            # since if it needs to run, we presume the user ops will run it on their own soon enough and do another
            # checkpoint.
            self.update_before_checkpoint()

        assert cptype
        assert self.last_cp is not None
        assert self.next_cp is not None
        assert self.current_diff is not None

        # Finalize self.next_cp -- details of this code probably belong at a lower level related to fill_checkpoint #e
        ###e specifically, this needs moving into the new method (to be called from here)
        ## self.current_diff.finalize(...)

        # as of sometime before 060309, use_diff is only still an option for debugging/testing purposes:
        use_diff = debug_pref("use differential undo?", Choice_boolean_True, prefs_key = 'A7-devel/differential undo')
                ## , non_debug = True) #bruce 060302 removed non_debug
            # it works, 122p 060301, so making it default True and non_debug.
            # (It was supposed to traceback when undoing to initial_state, but it didn't,
            #  so I'm "not looking that gift horse in the mouth" right now. ###@@@)
            #k see also comments mentioning 'differential'

        # maybe i should clean up the following code sometime...
        debug3 = 0 and env.debug() # for now [060301] if 0 060302; this is here (not at top of file) so runtime env.debug() affects it
        if debug3:
            print "\ncp", self.assy.all_change_indicators(), env.last_history_serno + 1
        if merge_with_future:
            #060309, partly nim; 060312 late night, might be done!
            if 0 and env.debug():
                print "debug: skipping undo checkpoint"
            ### Here's the plan [060309 855pm]:
            # in this case, used when auto-checkpointing is disabled, it's almost like not doing a checkpoint,
            # except for a few things:
            # + we update_parts (etc) (done above) to make sure change counters are accurate
            #   (#e optim: let caller flag say if that's needed)
            # - we make sure that change counter info (or whatever else is needed)
            #   will be available to caller's remake_UI_menuitems method
            #   - that might include what to say in Undo, like "undo to what history serno for checkpoint or disabling", or in Redo
            #   - #e someday the undo text might include info on types of changes, based on which change counters got changed
            #   - ideally we do that by making current_diff know about it... not sure if it gets stored but still remains current...
            #     if so, and if it keeps getting updated in terms of end change counters, do we keep removing it and restoring it???
            #     or can we store it on a "symbolic index" meaning "current counters, whatever they may be"??? ###
            #   - but i think a simpler way is just to decide here what those menu items should be, and store it specially, for undo,
            #     and just trash redo stack on real change but let the ui use the stored_ops in usual way otherwise, for Redo.
            #     Note that Redo UI won't be updated properly until we implement trashing the redo stack, in that case!
            # - we trash the redo stack based on what changed, same as usual (nim, this case and other case, as of 060309 852p).
            if self.last_cp.assy_change_indicators == self.assy.all_change_indicators():
                pass # nothing new; Undo being enabled can be as normal, based on last_cp #####@@@@@
            else:
                # a change -- Undo should from now on always be enabled, and should say "to last manual cp" or
                # "to when we disabled autocp"
                ####k Note: we need to only pay attention to changes that should be undoable, not e.g. view changes,
                # in the counters used above for these tests! Otherwise we'd enable Undo action
                # and destroy redo stack when we shouldn't. I think we're ok on this for now, but only because
                # calls to the view change counter are nim. ####@@@@ [060312 comment]
                if destroy_bypassed_redos:
                    self.clear_redo_stack( from_cp = self.last_cp, except_diff = self.current_diff ) # it's partly nim as of 060309
                        # this is needed both to save RAM and (only in this merge_with_future case) to disable the Redo menu item
                # set some flags about that, incl text based on what kind of thing has changed
                self.current_diff.command_info['n_merged_changes'] += 1 # this affects find_undoredos [060312 10:16pm]
                    # starts out at 0 for all diffs; never set unless diff w/ changes sticks around for more
                    ####@@@@ this number will be too big until we store those different change_counters and compare to *them* instead;
                    # just store them right now, and comparison above knows to look for them since n_merged_changes > 0;
                    # but there's no hurry since the menu text is fine as it is w/o saying how many cmds ran ###e
                ##e this would be a good time to stash the old cmdname in the current_diff.command_info(sp?)
                # and keep the list of all of them which contributed to the changes,
                # for possible use in coming up with menu_desc for merged changes
                # (though change_counters might be just as good or better)
            pass
        else:
            if 0 and env.debug():
                print "debug: NOT skipping undo checkpoint" # can help debug autocp/manualcp issues [060312]
            # entire rest of method
            if self.last_cp.assy_change_indicators == self.assy.all_change_indicators():
                # no change in state; we still keep next_cp (in case ctype or other metainfo different) but reuse state...
                # in future we'll still need to save current view or selection in case that changed and mmpstate didn't ####@@@@
                if debug_undo2 or debug3:
                    print "checkpoint type %r with no change in state" % cptype, self.assy.all_change_indicators(), env.last_history_serno + 1
                    if env.last_history_serno + 1 != self.last_cp.next_history_serno():
                        print "suspicious: env.last_history_serno + 1 (%d) != self.last_cp.next_history_serno() (%d)" % \
                              ( env.last_history_serno + 1 , self.last_cp.next_history_serno() )
                really_changed = False
                state = self.last_cp.state
                #060301 808p part of bugfix for "bug 3" [remove this cmt in a few days];
                # necessary when use_diff, no effect when not
            else:
                # possible change in state;
                # false positives are not common enough to optimize for, but common enough to try to avoid/workaround bugs in

                ## assert not self.current_diff.assert_no_changes...
                # note, its failure might no longer indicate a bug if we have scripting and a script can say,
                # inside one undoable operation, "undo to point P, then do op X".
                if self.current_diff.assert_no_changes: #060301
                    msg = "apparent bug in Undo: self.current_diff.assert_no_changes is true, but change_counters were changed "\
                          "from %r to %r" % (self.last_cp.assy_change_indicators, self.assy.all_change_indicators())
                    # we don't yet know if there's a real diff, so if this happens, we might move it later down, inside 'if really_changed'.
                    print msg
                    from utilities.Log import redmsg # not sure this is ok to do when this module is imported, tho probably it is
                    env.history.message(redmsg(msg))

                if debug_undo2:
                    print "checkpoint %r at change %r, last cp was at %r" % (cptype, \
                                    self.assy.all_change_indicators(), self.last_cp.assy_change_indicators)
                if not use_diff:
                    # note [060407]: this old code predates StatePlace, and hasn't been tested recently, so today's initial-state cleanup
                    # might break it, since current_state really returns cursnap, a StateSnapshot, but last_cp.state will be a StatePlace,
                    # unless something about 'not use_diff' makes it be a StateSnapshot, which is possible and probably makes sense.
                    # But a lot of new asserts of isinstance(state, StatePlace) will probably break in that case,
                    # so reviving the 'not use_diff' (as a debug_pref option) might be useful for debugging but would be a bit of a job.
                    state = current_state(self, self.assy, **self.format_options) ######@@@@@@ need to optim when only some change_counters changed!
                    really_changed = (state != self.last_cp.state) # this calls StateSnapshot.__ne__ (which calls __eq__) [060227]
                    if not really_changed and env.debug():
                        print "debug: note: detected lack of really_changed using (state != self.last_cp.state)"
                            ###@@@ remove when works and no bugs then
                else:
                    #060228
                    assert self.format_options == dict(use_060213_format = True), "nim for mmp kluge code" #e in fact, remove that code when new bugs gone
                    state = diff_and_copy_state(self, self.assy, self.last_cp.state)
#obs, it's fixed now [060301]
##                        # note: last_cp.state is no longer current after an Undo!
##                        # so this has a problem when we're doing the end-cmd checkpoint after an Undo command.
##                        # goal: diffs no longer form a simple chain... rather, it forks.
##                        # hmm. we diff against the cp containing the current state! (right?) ### [060301]
                    really_changed = state.really_changed
                    if not really_changed and debug3: # see if this is printed for bug 3, 060301 8pm [it is]
                        print "debug: note: detected lack of really_changed in diff_and_copy_state"
                        ###@@@ remove when works and no bugs then
                        # ok, let's get drastic (make debug pref if i keep it for long):
                        ## state.print_everything() IMPLEM  ####@@@@
                        print "state.lastsnap.attrdicts:", state.lastsnap.attrdicts # might be huge; doesn't contain ids of mutables
                    elif debug3: # condition on rarer flag soon,
                        # or have better debug pref for undo stats summary per chgcounter'd cp ###e doit
                        print "debug: note: real change found by diff_and_copy_state"
                if not really_changed and self.current_diff.command_info.get('_offered', False):
                    # [bruce 060326 to fix bug 1733:]
                    ###e should explain; comments elsewhere from this day and bug have some explanation of this
                    really_changed = True # pretend there was a real change, so we remain on undo stack, and don't reset change counters
                    self.current_diff.command_info['_no_net_change'] = True # but make sure menu_desc is able to know what's going on
                if not really_changed:
                    # Have to reset changed_counters, or undo stack becomes disconnected, since it uses them as varid_vers.
                    # Not needed in other case above since they were already equal.
                    # Side benefit: will fix file-modified indicator too (though in some cases its transient excursion to "modified" during
                    #  a drag, and back to "unmodified" at the end, might be disturbing). Bug: won't yet fix that if sel changed, model didn't.
                    #####e for that, need to reset each one separately based on what kind of thing changed. ####@@@@ doit!
                    self.assy.reset_changed_for_undo( self.last_cp.assy_change_indicators)
            if really_changed:
                self.current_diff.empty = False # used in constructing undo menu items ####@@@@ DOIT!
                if destroy_bypassed_redos:
                    # Destroy the Redo stack to save RAM, since we just realized we had a "newdo".
                    # WARNING: ####@@@@ In the future this will need to be more complicated, e.g. if the new change
                    # was on one of those desired sub-stacks (for view or sel changes) in front of the main one (model changes),
                    # or in one Part when those have separate stacks, etc...
                    # Design scratch, current code: the stuff to destroy (naively) is everything linked to from self.last_cp
                    # except self.current_diff / self.next_cp, *i think*. [060301, revised 060326]
                    self.clear_redo_stack( from_cp = self.last_cp, except_diff = self.current_diff ) # it's partly nim as of 060309
            else:
                # not really_changed
                # guess: following line causes bug 3 when use_diff is true
                if not use_diff:
                    state = self.last_cp.state
                        # note: depending on how this is reached, it sets state for first time or replaces it with an equal value
                        # (which is good for saving space -- otherwise we'd retain two equal but different huge state objects)
                else:
                    pass # in this case there's no motivation, and (guess) it causes "bug 3", so don't do it,
                        # but do set state when assy_change_indicators says no change [done] 060301 8pm
                self.current_diff.empty = True
                self.current_diff.suppress_storing_undo_redo_ops = True # (this is not the only way this flag can be set)
                    # I'm not sure this is right, but as long as varid_vers are the same, or states equal, it seems to make sense... #####@@@@@
            fill_checkpoint(self.next_cp, state, self.assy) # stores self.assy.all_change_indicators() onto it -- do that here, for clarity?
                #e This will be revised once we incrementally track some changes - it won't redundantly grab unchanged state,
                # though it's likely to finalize and compress changes in some manner, or grab changed parts of the state.
                # It will also be revised if we compute diffs to save space, even for changes not tracked incrementally.
                #e also store other metainfo, like time of completion, cmdname of caller, history serno, etc (here or in fill_checkpoint)

            if not self.current_diff.empty and self.pref_report_checkpoints():
                if cptype == 'end_cmd':
                    cmdname = self.current_diff.cmdname()
                else:
                    cmdname = cmdname_for_debug # a guess, used only for debug messages -- true cmdname is not yet known, in general
                if cmdname:
                    desc = "(%s/%s)" % (cptype, cmdname)
                else:
                    desc = "(%s)" % cptype
                self.debug_histmessage( "(undo checkpoint %s: %r)" % (desc, self.next_cp) )
                del cmdname, desc

            if not self.current_diff.suppress_storing_undo_redo_ops:
                redo_diff = self.current_diff
                undo_diff = redo_diff.reverse_order()
                self.store_op(redo_diff)
                self.store_op(undo_diff)
                # note, we stored those whether or not this was a begin or end checkpoint;
                # figuring out which ones to offer, merging them, etc, might take care of that, or we might change this policy
                # and only store them in certain cases, probably if this diff is begin-to-end or the like;
                # and any empty diff always gets merged with followon ones, or not offered if there are none. ######@@@@@@

            # Shift checkpoint variables
            self.last_cp = self.next_cp
            self.next_cp = None # in case of exceptions in rest of this method
            self.last_cp.cptype = cptype #k is this the only place that knows cptype, except for 'initial'?
    ##        self.last_cp_arrival_reason = cptype # affects semantics of Undo/Redo user-level ops
    ##            # (this is not redundant, since it might differ if we later revisit same cp as self.last_cp)
            self._setup_next_cp() # sets self.next_cp and self.current_diff
        return

    def clear_redo_stack( self, from_cp = None, except_diff = None ): #060309 (untested)
        "#doc"
        #e scan diff+1s from from_cp except except_diff, thinking of diffs as edges, cp's or their indices as nodes.
        # can we do it by using find_undoredos with an arg for the varid_vers to use instead of current ones?

        # use that transclose utility... on the nodes, i guess, but collect the edges as i go
        # (nodes are state_versions, edges are diffs)
        # (transclose needs dict keys for these nodes... the nodes are data-like so they'll be their own keys)

        assert from_cp is not None # and is a checkpoint?
        # but it's ok if except_diff is None
        state_version_start = self.state_version_of_cp(from_cp)
        # toscan = { state_version_start: state_version_start } # TypeError: dict objects are unhashable
        def dictkey(somedict):
            """
            Return a copy of somedict's data suitable for use as the key in another dict.
            (If somedict was an immutable dict object of some sort,
            this could just return it directly.)
            """
            items = somedict.items()
            items.sort() # a bit silly since in present use there is always just one item, but this won't run super often, i hope
                # (for that matter, in present use that item's key is always the same...)
            # return items # TypeError: list objects are unhashable
            return tuple(items)
        toscan = { dictkey(state_version_start): state_version_start }
        diffs_to_destroy = {}
        def collector(state_version, dict1):
            ops = self._raw_find_undoredos( state_version)
            for op in ops:
                if op.direction == 1 and op is not except_diff: # redo, not undo
                    # found an edge to destroy, and its endpoint node to further explore
                    diffs_to_destroy[op.key] = op
                    state_version_endpoint = self.state_version_of_cp( op.cps[1])
                    dict1[ dictkey(state_version_endpoint)] = state_version_endpoint
            return # from collector
        transclose( toscan, collector) # retval is not interesting to us; what matters is side effect on diffs_to_destroy
        if diffs_to_destroy:
            ndiffs = len(diffs_to_destroy)
            len1 = len(self.stored_ops)
            if env.debug():
                print "debug: clear_redo_stack found %d diffs to destroy" % ndiffs
            for diff in diffs_to_destroy.values():
                diff.destroy() #k did I implem this fully?? I hope so, since clear_undo_stack probably uses it too...
                # the thing to check is whether they remove themselves from stored_ops....
            diffs_to_destroy = None # refdecr them too, before saying we're done (since the timing of that is why we say it)
            toscan = state_version_start = from_cp = None
            len2 = len(self.stored_ops)
            savings = len1 - len2 # always 0 for now, since we don't yet remove them, so don't print non-debug msg when 0 (for now)
            if ndiffs and (savings < 0 or env.debug()):
                print "  debug: clear_redo_stack finished; removed %d entries from self.stored_ops" % (savings,) ###k bug if 0 (always is)
        else:
            if 0 and env.debug():
                print "debug: clear_redo_stack found nothing to destroy"
        return

    def current_command_info(self, *args, **kws): ##e should rename add_... to make clear it's not finding and returning it
        assert not args
        if not self._undo_archive_initialized:
            if env.debug():
                print_compact_stack("debug note: undo_archive not yet initialized (maybe not an error)")
            return
        self.current_diff.command_info.update(kws) # recognized keys include cmd_name
            ######@@@@@@ somewhere in... what? a checkpoint? a diff? something larger? (yes, it owns diffs, in 1 or more segments)
            # it has 1 or more segs, each with a chain of alternating cps and diffs.
            # someday even a graph if different layers have different internal cps. maybe just bag of diffs
            # and overall effect on varidvers, per segment. and yes it's more general than just for undo; eg affects history.
        return

    def do_op(self, op): ###@@@ 345pm some day bfr 060123 - figure out what this does if op.prior is not current, etc;
                # how it relates to whether assy changed since last_cp set; etc.
        """
        Assuming caller has decided it's safe, good, etc, in the case of out-of-order undo,
        do one of the diff-ops we're storing
        (ie apply it to model to change its state in same direction as in this diff),
        and record this as a change to current varid_ver pairs
        (not yet sure if those are stored here or in model or both, or of details for overall vs state-subset varids).
           If this is exactly what moves model state between preexisting checkpoints (i.e. not out-of-order),
        change overall varid_ver (i.e. our analog of an "undo stack pointer") to reflect that;
        otherwise [nim as of 060118] make a new checkpoint, ver, and diff to stand for the new state, though some state-subset
        varid_vers (from inside the diff) will usually be reused. (Always, in all cases I know how to code yet; maybe not for list ops.)
        """
        assert self._undo_archive_initialized
        # self.current_diff is accumulating changes that occur now,
        # including the ones we're about to do by applying self to assy.
        # Make sure it is not itself later stored (redundantly) as a diff that can be undone or redone.
        # (If it was stored, then whenever we undid a change, we'd have two copies of the same change stored as potential Undos.)

        self.current_diff.suppress_storing_undo_redo_ops = True  # [should this also discard self.last_cp as irrelevant??? then apply_to can set it? 060301 Q ###@@@]

        # Some code (find_undoredos) might depend on self.assy.all_change_indicators() being a valid
        # representative of self.assy's state version;
        # during op.apply_to( archive) that becomes false (as changes occur in archive.assy), but apply_to corrects this at the end
        # by restoring self.assy.all_change_indicators() to the correct old value from the end of the diff.

        # The remaining comments might be current, but they need clarification. [060126 comment]

        # in present implem [060118], we assume without checking that this op is not being applied out-of-order,
        # and therefore that it always changes the model state between the same checkpoints that the diff was made between
        # (or that it can ignore and/or discard any way in which the current state disagrees with the diff's start-checkpoint-state).

#bruce 060314 not useful now, but leave the code as example (see longer comment elsewhere):
##        self.mols_with_invalid_atomsets = {} ##@@ KLUGE to put this here -- belongs in become_state or so, but that's
##            # not yet a method of self! BTW, this might be wrong once we merge -- need to review it then. [bruce 060313]

        op.apply_to( self) # also restores view to what it was when that change was made [as of 060123]
            # note: actually affects more than just assy, perhaps (ie glpane view state...)
            #e when diffs are tracked, worry about this one being tracked
            #e apply_to itself should also track how this affects varid_vers pairs #####@@@@@

#ditto:
##        del self.mols_with_invalid_atomsets # this will have been used by updaters sometime inside op.apply_to

        #060123 202p following [later removed] is wrong since this very command (eg inside some menu item)
        # is going to do its own end-checkpoint.
        # the diffs done by the above apply_to are going to end up in the current diff...
        # what we need to do here is quite unrelated to self.last_cp -- know the varid_vers pairs, used in making undo/redo menuitems.
        # (and i bet last_cp_arrival_reason is similarly wrongheaded
        # and applies instead to (if anything) the "current state" of varid_vers pairs)
        # ... but how do we track the current state's varid_ver pairs? in our own checkpoint filler?
        # at two times:
        # - when random code makes random changes it probably needs to track them... this can be done when those chgs are
        #   packed into a diff, since we're saying "make sure it looks like we just applied this diff as if by redoing this op"
        #   (including having same effect on varid_vers as that would have)
        # - when it makes those while applying a diff, then at least the direct ones inside the diff can have them set to old vals
        #   (tho if updates to restore consistency also run, not sure they fit in -- but in single-varid system that's moot)
        return

    def state_version(self):
        ## assy_varid = make_assy_varid(self.assy._debug_name)
        # kluge: optim of above:
        assy_varid = ASSY_VARID_STUB
        assy_ver = self.assy.all_change_indicators() # note: this is about totally current state, not any diff or checkpoint;
            # it will be wrong while we're applying an old diff and didn't yet update assy.all_change_indicators() at the end
        return {assy_varid: assy_ver} # only one varid for now (one global undo stack) [i guess this is still true with 3 change counters... 060227]

    def state_version_of_cp(self, cp): #060309 ###k maybe this should be (or is already) a cp method...
        return {ASSY_VARID_STUB: cp.assy_change_indicators}

    def find_undoredos(self, warn_when_change_indicators_seem_wrong = True):
        """
        Return a list of undo and/or redo operations
        that apply to the current state; return merged ops if necessary.

        @param warn_when_change_indicators_seem_wrong: see code and comments.
        """
        #e also pass state_version? for now rely on self.last_cp or some new state-pointer...
        if not self._undo_archive_initialized:
            return []

        if warn_when_change_indicators_seem_wrong:
            # try to track down some of the bugs... if this is run when untracked changes occurred (and no checkpoint),
            # it would miss everything. If this sometimes happens routinely when undo stack *should* be empty but isn't,
            # it could explain dificulty in reproducing some bugs. [060216]
            # update, bruce 071025: I routinely see this warning under certain conditions, which I forget.
            # I don't think I experience bugs then, though.
            if self.last_cp.assy_change_indicators != self.assy.all_change_indicators():
                print "WARNING: find_undoredos sees self.last_cp.assy_change_indicators != self.assy.all_change_indicators()", \
                      self.last_cp.assy_change_indicators, self.assy.all_change_indicators()
            pass

        if self.current_diff.command_info['n_merged_changes']:
            # if the current_diff has any changes at all (let alone merged ones, or more precisely, those intending
            # to merge with yet-unhappened ones, because autocheckpointing is disabled), it's the only applicable one,
            # in the current [060312] single-undo-stack, no-inserted-view-ops scheme. The reason we check specifically
            # for merged changes (not any old changes) is that there's no record of any other kind of changes in current_diff,
            # and when other kinds get noticed in there they immediately cause it to be replaced by a new (empty) current_diff.
            # So there's no way and no point, and the reason there's no need is that non-current diffs get indexed
            # so they can be found in stored_ops by _raw_find_undoredos.
            return [self.current_diff.reverse_order()] ####k ####@@@@ ??? [added this 060312; something like it seems right]

        state_version = self.state_version()
        ## state_version = dict([self.last_cp.varid_ver()]) ###@@@ extend to more pairs
        # that's a dict from varid to ver for current state;
        # this code would be happy with the items list but future code will want the dict #e

        res = self._raw_find_undoredos( state_version) #060309 split that out, moved its debug code back here & revised it

        if not res and debug_undo2 and (self.last_cp is not self.initial_cp):
            print "why no stored ops for this? (claims to not be initial cp)", state_version # had to get here somehow...

        if debug_undo2:
            print "\nfind_undoredos dump of found ops, before merging:"
            for op in res:
                print op
            print "end of oplist\n"
        # Need to filter out obsolete redos (not sure about undos, but I guess not) ... actually some UIs might want to offer them,
        # so i'd rather let caller do that (plus it has the separated undo/redo lists).
        # But then to save time, let caller discard what it filters out, and let it do the merging only on what's left --
        # i.e. change docstring and API so caller merges, not this routine (not sure of this yet) #####@@@@@.
        ######@@@@@@ need to merge
        ##k need to store_op at end-checkpoint! right now we store at all cps... will that be ok? probably good...
        ## (or begin, if end missed -- do that by auto-end? what about recursion?
        #   let recursion also end, then begin anew... maybe merge... see more extensive comments mentioning word "cyberspace",
        #   maybe in a notesfile or in code)
        return res

    def _raw_find_undoredos(self, state_version):
        "#doc"
        res = {}
        for var, ver in state_version.items():
            lis = self.stored_ops.get( (var, ver), () )
            for op in lis: #e optim by storing a dict so we can use update here? doesn't matter for now
                if not op.destroyed:
                    ####e cond only needed because destroy doesn't yet unstore them;
                    # but don't bother unstoring them here, it would miss some
                    res[op.key] = op
        # this includes anything that *might* apply... filter it... not needed for now with only one varid in the system. ###@@@
        return res.values()

    def store_op(self, op):
        assert self._undo_archive_initialized
        for varver in op.varid_vers():
            ops = self.stored_ops.setdefault(varver, [])
            ops.append(op)
        return

    def _n_stored_vals(self): #060309, unfinished, CALL IT as primitive ram estimate #e add args for variants of what it measures ####@@@@
        res = 0
        for oplist in self.stored_ops.itervalues():
            for op in oplist:
                res += op._n_stored_vals() ###IMPLEM
        return res

    def wrap_op_with_merging_flags(self, op, flags = None):
        "[see docstring in undo_manager]"
        return MergingDiff(op, flags = flags, archive = self) # stub

    pass # end of class AssyUndoArchive

ASSY_VARID_STUB = 'assy' # kluge [060309]: permit optims from this being constant, as long as this doesn't depend on assy, etc;
    # all uses of this except in make_assy_varid() are wrong in principle, so fix them when that kluge becomes invalid.

def make_assy_varid(assy_debug_name):
    """
    make the varid for changes to the entire assy,
    for use when we want a single undo stack for all its Parts
    """
    ## return 'varid_stub_' + (assy_debug_name or "") #e will come from assy itself
    return ASSY_VARID_STUB # stub, but should work

# end
