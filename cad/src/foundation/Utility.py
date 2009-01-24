# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Utility.py -- class Node (superclass for all model-tree objects),
Group [now defined in Group.py, no longer imported here],
and a few related classes or functions, defining a uniform
API to permit all Node subclasses to be shown in the model tree,
and methods for manipulation of Node trees. (Most Node subclasses
are defined in other files. Notable ones are molecule and Jig.)

(Note: all non-leaf nodes in a node tree must be instances of Group.)

See also: class Node_api (which is only the part
of the API needed by the ModelTree).

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History: 

Originally by Josh; gradually has been greatly extended by Bruce,
but the basic structure of Nodes and Groups has not been changed.

Bruce 071110 split Group.py out of Utility.py. (And may soon
split out Node and/or LeafNode as well.)

Bruce 080305 added some abstract classes between Node and Group
in the inheritance hierarchy (defined in this module for now).
"""

from utilities.debug import print_compact_stack
from utilities import debug_flags
import foundation.env as env
from utilities.constants import genKey
from foundation.state_utils import copy_val, StateMixin
from utilities.Log import redmsg, orangemsg
from foundation.state_constants import S_PARENT, S_DATA, S_CHILD

from utilities.icon_utilities import imagename_to_pixmap

from foundation.Assembly_API import Assembly_API

from widgets.simple_dialogs import grab_text_line_using_dialog

_DEBUG_UNDOABLE_ATTRS = False

# ==

# Unique id for all Nodes -- might generalize to other objects too.
# Unlike python builtin id(node), this one will never be reused
# when an old node dies.

nodekey = genKey(start = 1)
    # note: atoms are not nodes, so possible overlap of
    # atom.key and node._id should be ok for now.

def node_id(node):
    """
    session-unique id for a Node (never reused)
    (legal to call for None, then returns None)
    """
    if node is None:
        return None
    assert isinstance(node, Node) #e might relax this later
    try:
        node._id # make sure it exists already
    except AttributeError:
        node._id = nodekey.next()
    return node._id

def node_name(node):
    """
    use this in error or debug messages for safety, rather than node.name
    """
    if node is None:
        return "<None>"
    try:
        return node.name
    except AttributeError:
        return "<node has no .name>"
    pass

_will_kill_count = 1
    # Note: this must start > 0, even though it's incremented when next used
    # [bruce 060327]

# ==

class Node( StateMixin):
    """
    Superclass for model components which can be displayed in the Model Tree.
    This is inherited by Groups, molecules (Chunks), Jigs, and some more
    specialized subclasses. The method implementations in class Node are
    designed to be typical of "leaf Nodes" -- many of them are overridden
    by Group, and some of them by other Node subclasses.
    """

    # default values of per-subclass constants
    # (see also attribute declarations, below)

    featurename = "" # wiki help featurename for Node subclass [bruce 051201]

    const_pixmap = None 
        #bruce 090119 API revision (presence of default value of const_pixmap,
        # use of boolean test on it)
    
    # default values of instance variables

    name = "" # for use before __init__ runs (used in __str__ of subclasses)

    picked = False # whether it's selected
        # (for highlighting in all views, and being affected by operations)
    hidden = False # whether to make it temporarily invisible in the glpane
        # (note: self.hidden is defined, but always False, for Groups;
        #  it might be set for any leaf node whether or not that node is ever
        #  actually shown in the glpane.)
    open = False # defined on all Nodes, to make it easier to count open nodes
        # in a tree (this will never become True except for Groups)
        # (when more than one tree widget can show the same node, .open will
        #  need replacement with treewidget-specific state #e)

    # Note: node.members is not defined unless node.is_group() is true,
    # i.e. unless that node inherits from Group. Given that condition,
    # it is always defined, whether or not node.openable() and/or node.open.
    # (And those are both always defined on all nodes.)
    # [bruce 080107 comment]

    dad = None
    part = None #bruce 050303
    prior_part = None #bruce 050527
    disabled_by_user_choice = False
        # [bruce 050505 made this the default on all Nodes, though only Jigs
        #  use the attr so far; see also is_disabled]

    is_movable = False #mark 060120

    # attribute declarations (per-subclass constants used for copy and undo)

    copyable_attrs = ('name', 'hidden', 'open', 'disabled_by_user_choice')
        #bruce 050526
        # (see also __declare_undoable_attrs [bruce 060223])
        # subclasses need to extend this
        # TODO: could someday use these to help make mmp writing and reading
        # more uniform, if we also listed the ones handled specially
        # (so we can handle only the others in the new uniform way)

    _s_attr_dad = S_PARENT
    _s_attr_picked = S_DATA
    _s_categorize_picked = 'selection'
    _s_attr_part = S_CHILD
        # has to be child to be found
        # (another way would be assy._s_scan_children);
        # not S_CACHE since Parts store some defining state
    #e need anything to reset prior_part to None? yes, do it in _undo_update.
    _s_attr_assy = S_PARENT
        # assy can't be left out, since on some or all killed nodes it's
        # foolishly set to None, which is a change we need to undo when we
        # revive them. TODO: stop doing that, have a killed flag instead.

    def _undo_update(self): #bruce 060223
        # no change to .part, since that's declared as S_CHILD
        self.prior_part = None
        del self.prior_part # save RAM
        StateMixin._undo_update(self)
        return

    def __init__(self, assy, name, dad = None):
        """
        Make a new node (Node or any subclass), in the given Assembly (assy)
        (I think assy must always be supplied, but I'm not sure),
        with the given name (or "" if the supplied name is None),
        and with the optionally specified dad (a Group node or None),
        adding it to that dad as a new member (unless it's None or not
        specified, which is typical).
        All args are supplied positionally, even the optional one.

        Warning: arg order was revised by bruce 050216 to be more consistent
        with subclasses, but Group's arg order was and still is inconsistent
        with all other Node classes' arg order.
        """
        #bruce 050205 added docstring; bruce 050216 revised it
        #bruce 050216 fixed inconsistent arg order
        # [re other leaf nodes -- Group is not yet fixed], made name required

        self.name = name or "" # assumed to be a string by some code

        # assy must be None or an Assembly or a certain string
        if assy is not None and \
           not isinstance(assy, Assembly_API) and \
           assy != '<not an assembly>':
            assert 0, "node.assy must be an Assembly"
                # no need to mention the private possibilities in the error msg
        # verify assy is not None (not sure if that's allowed in principle,
        # but I think it never happens) [050223]
        if assy is None:
            #bruce 071026 always print this, not only when atom_debug
            print_compact_stack("note: Node or Group constructed with assy = None: ")
        self.assy = assy
        if dad: # dad must be another Node (which must be a Group), or None
            dad.addchild(self)
                #bruce 050206 changed addmember to addchild, thus enforcing
                # dad correctness
                # warning [bruce 050316]: this might call inherit_part;
                # subclasses must be ready for this by the time their inits call
                # ours, e.g. a Group must have a members list by then.
            assert self.dad is dad # addchild should have done this
        if self.__declare_undoable_attrs is not None: #bruce 060223 (temporary kluge)
            # it's None except the first time in each Node subclass;
            # is there a faster test? (Guess: boolean test is slower.)
            self.__declare_undoable_attrs()
        return

    def short_classname(self): #bruce 080319
        """
        return self's classname, with package/module names removed
        (e.g. "DnaStrand" rather than "dna.model.DnaStrand.DnaStrand")
        """
        # could be more general, e.g. a helper function
        # todo: use this in a lot more places that inline this
        # (but in __repr__ a helper function would be safer than a method)
        return self.__class__.__name__.split('.')[-1]

    def __repr__(self): #bruce 060220, revised 080118, refactored 090107
        """
        [subclasses can override this, and often do]
        """
        classname = self.short_classname()
        try:
            name_msg = ", name = %r" % (self.name,)
        except:
            name_msg = " (exception in `self.name`)"
        return "<%s at %#x%s>" % (classname, id(self), name_msg)

    def set_assy(self, assy): #bruce 051227, Node method [used in PartLibrary_Command]
        """
        Change self.assy from its current value to assy,
        cleanly removing self from the prior self.assy if that is not assy.
        """
        if self.assy is not assy:
            oldassy = self.assy
            if oldassy is not None:
                assert oldassy != '<not an assembly>'
                    # simplest to just require this;
                    # nodes constructed that way shouldn't be moved
                assert isinstance(oldassy, Assembly_API)
                # some of the above conds might not be needed, or might be
                # undesirable; others should be moved into following subr
                self.remove_from_parents()
                assert self.assy is None
            # now ok to replace self.assy, which is None or (ignoring
            # the above assert) '<not an assembly>'
            # (safety of latter case unverified, but I think it will
            # never happen, even without the assert that disallows it)
            assert self.assy is None
            self.assy = assy
            assert self.part is None
            assert self.dad is None
        return

    def get_featurename(self): #bruce 051201
        """
        Return the wiki-help featurename for this object's class,
        or '' if there isn't one.
        """
        # TODO: add superclass-override checks and an "Undocumented Node"
        # default value, like in Command.get_featurename, except permit
        # specific classes to turn it off, at least for use in the MT cmenu,
        # like they do now by leaving it as "". [bruce 071227 comment]
        return self.__class__.featurename
            # that's intended to be a per-subclass constant...
            # so enforce that until we need to permit it to be otherwise

    def _um_initargs(self): #bruce 051013 [in class Node]
        # [as of 060209 this is probably well-defined and correct
        #  (for most subclasses), but not presently used]
        # [update 071109: since then it may well have come into use]
        """
        Return args and kws suitable for __init__.

        [Overrides an undo-related superclass method;
         see its docstring for details.]
        """
        return (self.assy, self.name), {}
            # self.dad (like most inter-object links) is best handled separately

    def _um_existence_permitted(self):
        #bruce 051005 [###@@@ as of 060209 it seems likely this should go away,
        #  but I'm not sure]
        """
        [overrides UndoStateMixin method]

        Return True iff it looks like we should be considered to exist 
        in self.assy's model of undoable state.

        Returning False does not imply anything's wrong, or that we should
        be or should have been killed/destroyed/deleted/etc --
        just that changes in us should be invisible to Undo.
        """
        return self.assy is not None and \
               self.part is not None and \
               self.dad is not None
            ###e and we're under root? does that method exist?
            # (or should viewpoint objects count here?)

    def __declare_undoable_attrs(self): #bruce 060223
        """
        [private method for internal use by Node.__init__ only;
         temporary kluge until individual _s_attr decls are added]

        Scan the perhaps-someday-to-be-deprecated per-class list,
        copyable_attrs, and add _s_attr decls for the attrs listed in them
        to self.__class__ (Node or any of its subclasses).

        Don't override any such decls already present, if possible
        [not sure if you can tell which class added them #k].

        Should be run only once per Node subclass, but needs an example object
        (self) to run on. Contains its own kluge to help cause it to be run only
        once.
        """
        subclass = self.__class__
        if _DEBUG_UNDOABLE_ATTRS:
            print "debug: running __declare_undoable_attrs in", subclass
        for attr in subclass.copyable_attrs:
            name = "_s_attr_" + attr
            if hasattr(subclass, name):
                if _DEBUG_UNDOABLE_ATTRS:
                    print " debug: not overwriting manual decl of %r as %r" % \
                          (name, getattr(subclass, name))
            else:
                setattr( subclass, name, S_DATA)
                    # or S_REFS? If it needs to be S_CHILD, add an individual
                    # decl to override it.
        # prevent further runs on same subclass (in cooperation with the sole
        # calling code)
        subclass.__declare_undoable_attrs = None
            # important to do this in subclass, not in self or Node
        return

    def parent_node_of_class(self, clas):
        """
        If self has a parent Node in the current part
        (or a grandparent node, etc, but not self)
        which is an instance of clas,
        return the innermost such node; otherwise return None.

        @rtype: a Group (an instance of clas), or None

        @param clas: a class (only useful if it's Group or a subclass of Group)

        @see: get_topmost_subnodes_of_class (method in Group and Part)

        @note: for advice on avoiding import cycles when passing a class,
               see docstring of Group.get_topmost_subnodes_of_class.
        """
        #bruce 071206; revised 080808
        part = self.part
        node = self.dad
        while node and node.part is part:
            if isinstance( node, clas):
                # assert not too high in internal MT
                assy = self.assy
                assert node.assy is assy
                assert node is not assy.shelf
                assert node is not assy.root
                # but i think it's ok if node is assy.tree!
                return node
            node = node.dad
        return None

    def containing_groups(self, within_same_part = False):
        """
        Return a list of the 0 or more group nodes which contain this node,
        in innermost to outermost order, not including self.assy.root.

        @param within_same_part: if true, only return groups in the same Part
                                 as self (i.e. don't return assy.shelf).
        """
        #bruce 080507, revised 080626
        # review: would this be safe for a node in a thumbview?
        res = []
        group = self.dad
        limit = self.assy.root
        while group is not None and group is not limit:
            if within_same_part and group is self.assy.shelf:
                # review: use is_selection_group_container in that test?
                break
            res.append(group)
            group = group.dad
        return res

    def containing_nodes(self): #bruce 080507
        """
        Return a list of the 1 or more nodes which contain self
        (including self in the result),
        in innermost to outermost order, not including self.assy.root.

        @warning: it's an error for self to *be* self.assy.root.
        """
        assert self is not self.assy.root
        return [self] + self.containing_groups()

    def node_depth(self): #bruce 080116
        """
        Return self's depth in its node tree
        (defined as the number of groups it's inside,
        directly or indirectly, *including* the assy.root group
        which is not visible in the model tree, and including
        all other special groups such as assy.shelf).

        If self has no .dad (node tree parent),
        which means it's either assy.root or is not in the
        assy's node tree, its depth is 0. The only node in the
        assy's node tree with a depth of 0 is assy.root.

        Note that arbitrarily deep node trees can legally exist
        outside of any assy (e.g. if some code creates a Group
        but doesn't add it into assy yet).
        """
        if self.dad:
            return 1 + self.dad.node_depth()
        return 0

    def node_depth_under_parent(self, parent): #bruce 080116; untested, not yet used
        """
        @param parent: optional parent node; if provided,
                       return -1 if self is not under or equal to parent,
                       and otherwise return self's depth
                       under parent, which is 0 if self is parent, 1 if self
                       is a direct child of parent, etc.
        @type parent: Node (need not be a Group)
        """
        if self is parent:
            return 0
        if not self.dad:
            return -1
        pdepth = self.dad.node_depth_under_parent(parent)
        if pdepth == -1:
            return pdepth
        return pdepth + 1

    def set_disabled_by_user_choice(self, val):
        #bruce 050505 as part of fixing bug 593
        self.disabled_by_user_choice = val
        self.changed()

    def changed(self): 
        """
        Call this whenever something in the node changes
        which would affect what gets written to an mmp file
        when the node gets written.
           Try to call it exactly when needed, since calling it
        when not needed leads to the user being told there are
        unsaved changes, and asked to confirm discards of the model
        upon loading a new one, even when there are no actual changes.
           But if you're not sure, calling it when not needed is better
        than not calling it when needed.
        """
        #bruce 050505; not yet uniformly used (most code calls part.changed or
        #assy.changed directly)
        if self.part is not None:
            self.part.changed()
                #e someday we'll do self.changed which will do dad.changed....
        elif self.assy is not None:
            pass
                # I'm not sure if it would be correct to call assy.changed
                # in this case (when there's no .part set)
                # [bruce 060227 comment]
        return

    def is_group(self): #bruce 050216; docstring revised 071024
        """
        Is self a Group node (i.e. an instance of Group or a subclass)?

        Usage note: assuming something is known to be a Node,
        something.is_group() is preferable to isinstance(something, Group),
        due to its flexibility in case of future semantics changes,
        and to the fact that it doesn't require an import of Utility.
        (Also, this method would work if Utility was reloaded, but isinstance
         would not. This doesn't yet matter in practice since there are
         probably other big obstacles to reloading Utility during debugging.)

        However, isinstance(obj, Group_API) (NIM) might be even better,
        since it works for any type of obj, and some of our code is
        polymorphic enough for that to matter. So don't go converting
        isinstance(something, Group) to something.is_group() whereever
        possible, just yet.

        WARNING: future changes may require us to disambiguate whether
        this refers to an "internal Group" or to "something that acts in the
        model tree as a Group". The former (lower-level) meaning is the intended
        one, but some calls may need to be changed to a new method corresponding
        to the other meaning, if these aspects of a Node diverge.

        [overridden in Group]
        """
        return False # for a leaf node

    def isEmpty(self):
        """
        Subclasses should override this method. (especially Group subclasses)
        Default implementation returns False (non empty node) 
        @see: DnaGroup.isEmpty()
        """
        return False

    def readmmp_info_leaf_setitem( self, key, val, interp ):
        """
        This is called when reading an mmp file, for each "info leaf" record
        which occurs right after this node is read and no other node has been
        read. (If this node is a group, we're called after it's closed, but
        groups should ignore this record.)
           Key is a list of words, val a string; the entire record format
        is presently [050421] "info leaf <key> = <val>".
        Interp is an object to help us translate references in <val>
        into other objects read from the same mmp file or referred to by it.
        See the calls of this method from files_mmp for the doc of interp
        methods.
           If key is recognized, set the attribute or property it refers to to
        val; otherwise do nothing (or for subclasses of Node which handle
        certain keys specially, call the same method in the superclass
        for other keys).
           (An unrecognized key, even if longer than any recognized key,
        is not an error. Someday it would be ok to warn about an mmp file
        containing unrecognized info records or keys, but not too verbosely
        (at most once per file per type of info).)
        """
        # logic bug: new mmp records for leaf nodes, skipped by old reading code,
        # cause their info leaf records to erroneously get applied to the previous
        # leaf node that the old code was able to read. [bruce 071109 comment]
        if self.is_group():
            if debug_flags.atom_debug:
                print "atom_debug: mmp file error, ignored: " \
                      "a group got info leaf %r = ..." % (key,)
            return
        if key == ['hidden']:
            # val should be "True" or "False" (unrecognized vals are treated as False)
            val = (val == 'True')
            self.hidden = val
        elif key == ['disabled']: #bruce 050422
            # val should be "True" or "False" (unrecognized vals are treated as False)
            val = (val == 'True')
            self.disabled_by_user_choice = val
        elif key == ['forwarded']: #bruce 050422
            # this happens just after we read this leaf node (self)
            # from an mmp file, and means we should move it from where it was
            # just placed (at the end of some Group still being read)
            # to a previous location indicated by val, and available via interp.
            interp.move_forwarded_node( self, val)
        else:
            if debug_flags.atom_debug:
                msg = "atom_debug: fyi: info leaf (in Node) with " \
                    "unrecognized key %r (not an error)" % (key,)
                print msg
        return

    def is_disabled(self): 
        """
        Should this node look disabled when shown in model tree
        (but remain fully functional for selection)?
        """
        #bruce 050421 experiment related to bug 451-9 
        #e what Jig method does belongs here... [050505 comment]
        return False 

    def redmsg(self, msg): 
        #bruce 050203
        # revised 050901 to work even after assy set to None in Node.kill
        env.history.message( redmsg( msg ))

    def is_top_of_selection_group(self): 
        """
        Whether this node is the top of a "selection group".
        (Note: this can be true of leaf nodes as well as group nodes,
         in spite of the name.)
        We enforce a rule that limits the selection to being entirely within
        one selection group at a time, since many operations on mixes
        of nodes from different selection groups are unsafe.
        [As of 050131, should be True of the PartGroup and any "clipboard item";
         this implem is not complete, so it's overridden by PartGroup.]
        """
        #bruce 050131 for Alpha [#e rename is_selection_group?]
        # [#e rename concept "selectable set"?]
        ###@@@ [General discussion of implem of selection groups, 050201:
        # in hindsight the implem should just store the selgroup
        # in each node, and maintain this when dad changes, like for .assy.
        # In fact, for Beta the selgroup probably *will* be the value of .assy,
        # which will be different for each clipboard item; or it might be a
        # separate field like .selgroup or .space or .part, depending on what
        # we end up calling "the part or any clipboard item, ie anything you
        # want to show in the glpane at once, and think of as being in one
        # physical space, where collisions and bonds are possible".]
        #
        # Following implem is correct for most nodes --
        # determine whether self is a "clipboard item".
        # [It could even work if we someday introduce "Groups of clipboard
        #  items".]
        # But it's wrong for PartGroup itself (thus is overridden by it).
        return self.dad and self.dad.is_selection_group_container()

    def is_higher_than_selection_group(self): #bruce 080222
        """
        Whether this node is higher than any node which satisfies
        node.is_top_of_selection_group(). True only of assy.shelf
        and assy.root in the current arrangement of an Assembly.
        """
        # This implem is not ideal -- it knows too much about assy.
        # Probably it'd be better to ask self.assy if self has this property
        # within it. [todo: refactor it like that]
        return (self is self.assy.shelf or self is self.assy.root)

    no_selgroup_is_ok = False
        #bruce 050612 class constant, could be overridden in some subclasses
        # [not presently needed, but tested]

    def change_current_selgroup_to_include_self(self): #bruce 050131 for Alpha
        """
        #doc
        """
        # This might not be fast enough, so when there's time,
        # replace it with one that optims by stopping when dad is picked.
        foundselgroup, ours = self.find_selection_group_or_picked_dad()
        if not foundselgroup:
            # found a "picked dad"
            assert ours.picked
            return # no need to change (important optimization for recursive picking in groups)
        if ours is None:
            # this might happen for non-bugs since changed_dad calls it for
            # picked nodes, but it makes sense to skeptically review any way
            # that can happen, so the debug print is good even if it's not
            # always a bug [bruce comment 050310]
            if self.no_selgroup_is_ok:
                return #bruce 050602
            if debug_flags.atom_debug:
                print "atom_debug: bug(?): change_current_selgroup_to_include_self " \
                      "on node with no selgroup; ignored"
            return
        # ours is this node's selgroup, and might or might not already be the
        # current one in self.assy
        prior = self.assy.current_selgroup_iff_valid()
            # might be None but otherwise is always valid; no side effects [revised 050310]
        if ours is not prior:
            self.assy.set_current_selgroup( ours)
                # this unpicks everything not in 'ours' and warns if it unpicked anything
        return

    def find_selection_group(self): #bruce 050131 for Alpha 
        #####@@@@@ needs update/review for being called on deleted nodes; pass assy?
        """
        Return the selection group to which this node belongs, or None if none
        (as of 050131 that should happen only for Clipboard or Root).
        """
        node = self
        while node is not None:
            if node.is_top_of_selection_group():
                break
            node = node.dad # might be None
                # always is None eventually, so loop always terminates by then
        return node # might be None

    def find_selection_group_or_picked_dad(self): #bruce 050131 for Alpha
        """
        Return (True, selgroup) where selgroup (maybe None) would be returned
        by find_selection_group, or (False, picked_dad) if you hit a "picked
        dad of self" (implying that self's selection group, whatever it is, is
        the current one, assuming no bugs in our new invariants). Prefer the
        picked_dad retval since it's faster.
        """
        node = self
        while node is not None:
            if node.is_top_of_selection_group():
                break
            node = node.dad # might be None
                # always is None eventually, so loop always terminates by then
            if node is not None:
                # don't try this test for node is self, since it's not a "dad of self"
                if node.picked:
                    return False, node                
        return True, node # might be None

    def show_in_model_tree(self): #bruce 050127 
        """
        Should this node be shown in the model tree widget?
        True for most nodes. Can be overridden by subclasses.
        [Added so that Datum Plane nodes won't be shown. Initially,
         it might not work much more generally than that.]
        """
        ###e needs renaming, sounds like "scroll to make visible" [050310]
        #bruce 050417 warning: I think I never ended up honoring this. Not sure. 
        #bruce 050527: It's not honored now, anyway. ### REVIEW: keep or discard?
        return True

    def haspicked(self): #bruce 050126
        """
        @return: whether node's subtree has any picked members.
        @rtype: boolean
        
        This is faster than counting them with nodespicked or "maxing" them
        with hindmost, at least when anything is picked; just as slow when
        nothing is (still requires a full scan). [#e should we memoize
        hindmost data??]
        
        [overridden in Group, but this docstring applies to both methods
         together; should not be overridden elsewhere.]
        """
        return self.picked

    def permits_ungrouping(self): #bruce 050126 for Node; earlier for Group
        """
        [Leaf nodes can never (yet) be ungrouped. See Group.permits_ungrouping
        docstring for the general definition of this method.]
        """
        return False

    def MT_kids(self, display_prefs = {}): 
        """
        For doc, see Group.MT_kids()

        [some subclasses should override this, especially Group]
        """
        #bruce 050109; 080108 renamed from kids to MT_kids; revised semantics
        # review: must this be [] rather than ()? 
        # Some calling code might add it to another list...
        return [] 

    def openable(self):
        """
        Say whether tree widgets should permit the user to open/close their
        view of this node (typically by displaying some sort of toggle icon
        for that state). (Note, if this is True then this does not specify
        whether the node view is initially open... #doc what does.)

        [Some subclasses should override this; if they add nonmember MT_kids
        but don't override this, those MT_kids will probably never be shown,
        but that might be undefined and depend on the model tree widget --
        it's better to follow the rule of never having MT_kids unless you are
        openable.]
        """
        # + If we decide this depends on the tree widget or on something about
        # it, we'll have to pass in some args... don't do that unless/until we
        # need to.
        # + One reason we don't measure len(self.MT_kids()) to decide on the
        # default value for this, is that some nodes might not want to compute
        # self.MT_kids() until/unless it's needed, in case doing so is
        # expensive. For example, Qt's dirview example (also in PyQt
        # examples3) computes MT_kids only when a node (representing a
        # filesystem directory) is actually opened.
        return False

    # REVIEW: API and method/attr names related to "rename" needs review,
    # since the text shown by some nodes in a tree widget (in the future)
    # might not be "their name". [bruce 050128]

    def rename_enabled(self):
        """
        Should tree widgets permit the user to rename this node?
        (If so, they will call self.try_rename(newname) to actually request
        renaming for a specific new name.)

        [some subclasses should override this and/or try_rename]
        """
        return True

    def try_rename(self, name):
        """
        Given a new name for self, store it or reject it.
        Specifically, do one of these actions:
        - transform it into an acceptable name, store that in the node,
          do needed invals, and return (True, stored name);
        - or, reject it, and return (False, reason it's not ok).
          (The reason should be a string suitable for error messages.)
        """        
        # todo: some of TreeWidget.slot_itemRenamed should be moved into a new
        # caller of this in Node, so other Qt widgets can also safely try to
        # rename Nodes. [bruce 050527 comment]
        # names containing ')' work now, so we permit them here [bruce 050618]
        
        if not self.rename_enabled():
            return (False, "renaming this node is not permitted")
        #mark 051005 --  now name can be a python string or a QString
        try: 
            n = str(name)
        except:
            return (False, "illegal string")
        name = n.strip() # remove whitespace from both ends
        if not name:
            return (False, "blank name is not permitted")

        # accept the new name.
##        self._um_will_change_attr('name') #bruce 051005; this might need 
##            # to be called from a property-setter method for completeness
        self.name = name
        if self.assy:
            self.assy.changed()
        ###e should inval any observers (i.e. model tree) -- 
        # not yet needed, I think [bruce 050119]
        return (True, name)
    
    def rename_using_dialog(self):
        """        
        Rename this node using a popup dialog, whn, user chooses to do
        so either from the MT or from the 3D workspace. 
        
        """
        #This method is moved (with some modifications) from modelTreeGui.py so as
        #to facilitate renaming nodes from the 3D workspace as well.
        #The method was originally written by Bruce  -- Ninad 2008-11-17
        
        # Don't allow renaming while animating (b/w views). 
        
        assy = self.assy
        win = assy.win
        glpane = assy.glpane
        
        if glpane.is_animating:
            return
        # Note: see similar code in setModelData in an outtakes class.
        # REVIEW: why is renaming the toplevel node not permitted?
        # Because we'll lose the name when opening the file?
        oldname = self.name
        ok = self.rename_enabled()
        # Various things below can set ok to False (if it's not already)
        # and set text to the reason renaming is not ok (for use in error messages).
        # Or they can put the new name in text, leave ok True, and do the renaming.
        if not ok:
            text = "Renaming this node is not permitted."
                #e someday we might want to call try_rename on fake text
                # to get a more specific error message... for now it doesn't have one.
        else:
            ok, text = grab_text_line_using_dialog(
                            title = "Rename",
                            label = "new name for node [%s]:" % oldname,
                            iconPath = "ui/actions/Edit/Rename.png",
                            default = oldname )
        if ok:
            ok, text = self.try_rename(text)
        if ok:
            msg = "Renamed node [%s] to [%s]" % (oldname, text) ##e need quote_html??
            env.history.statusbar_msg(msg)
            win.mt.mt_update() #e might be redundant with caller; if so, might be a speed hit
        else:
            msg = "Can't rename node [%s]: %s" % (oldname, text) # text is reason why not
            env.history.statusbar_msg(msg)
        return

    def drag_move_ok(self): # renamed/split from drag_enabled; docstring revised 050201
        """
        Say whether a drag_move which includes this node can be started (for
        "drag and drop").
        
        It's ok if only some drop-targets (nodes or inter-node gaps) can
        accept this node; we'll ask the targets if they'll take a specific
        drag_moved list of nodes (which includes this node).
        
        A tree widget asked to drag_move some selected nodes might filter them
        by drag_move_ok to get the ones to actually move, or it might refuse
        the whole operation unless all are ok to move -- that's a UI decision,
        not a node semantics decision.

        [some subclasses should override this]
        """
        return True

    def drag_copy_ok(self): # renamed/split from drag_enabled; docstring revised 050201
        #bruce 050527 comment: this API needs revision, since the decision for 
        # jigs depends on what other nodes are included.
        # And we should revise it more, so we can construct a Copier object, let it "prep",
        # and use it for not only filtering out some nodes (like this does)
        # but getting the summary msg for the drag graphic, etc. #####@@@@@
        """
        Say whether a drag_copy which includes this node can be started (for
        "drag and drop"). Same comments as for drag_move_ok apply.

        [some subclasses should override this]
        """
        return True

    def drop_on_should_autogroup(self, drag_type, nodes): #bruce 071025
        """
        Say whether Model Tree DND drops onto this node (self),
        of the given drag_type and list of nodes,
        should automatically group the dropped nodes.

        @note: this is called even if there is only one node,
        so if you want to group only when there's more than one,
        return len(nodes) > 1 rather than just True.

        @param drag_type: 'move' or 'copy'

        @param nodes: Python list of nodes being DND'd onto self.

        [overridden in some subclasses]
        """
        return False

    def MT_DND_can_drop_inside(self): #bruce 080317
        """
        Are ModelTree Drag and Drop operations permitted to drop nodes
        inside self?

        [overridden in Group and again in some of its subclasses]
        """
        return False
    
    def node_icon(self, display_prefs):
        """
        #doc this - should return a cached icon

        [all Node subclasses should either override this
         or define a class or instance value for const_pixmap attribute]
        """
        if self.const_pixmap:
            return self.const_pixmap 
                # let simple nodes just set this in __init__ (or as a 
                # class constant) and be done with it [bruce 060523/090119]
        else:
            msg = "bug: Node subclass %s forgot to override node_icon method " \
                  "or set self.const_pixmap" % self.__class__.__name__
            fake_filename = msg
            return imagename_to_pixmap( fake_filename)
                # should print msg, at most once per class
                # (some people might consider this a kluge)
        pass

    # most methods before this are by bruce [050108 or later] 
    # and should be reviewed when my rewrite is done ###@@@

    def addsibling(self, node, before = False):
        """
        Add the given node after (default) or before self, in self's Group.
        Node should not already be in any Group, since it is not removed from one.
        (Some existing code violates this; this is probably ok if node's old Group
        is never again used, but that practice should be deprecated, and then
        this method should detect the error of node.dad already being set,
        or perhaps be extended to remove node from its dad.)

        [Special case: legal and no effect if node is self. But this should be
        made into an error, since it violates the rule that node is not presently
        in any Group!]

        [It is unlikely that any subclass should override this, since its
        semantics should not depend on anything about self, only (perhaps)
        on things about its Group, i.e. self.dad.]

        [Before bruce 050113 this was called Node.addmember, but it had different
        semantics from Group.addmember, so I split that into two methods.]
        """
        if node is self:
            # bruce comment 010510: looks like an error, and not nearly the
            # only one possible... maybe we should detect more errors too,
            # and either work around them (as this does) or report them.
            #bruce comment 050216: probably no longer needed since probably done in addchild
            return
        if before:
            self.dad.addchild( node, before = self) # Insert node before self
        else:
            self.dad.addchild( node, after = self) # Insert node after self
        return

    def addmember(self, node, before_or_top = False):
        """
        [Deprecated public method; overridden in Group with different behavior:]

        Like addsibling or addchild, depending on whether self is
        a leaf node or a Group. (Also misnamed, since a sibling is not a member.)

        Any call to addmember whose node is known to be always a Group
        can be replaced with addchild (default option values are compatible),
        except that if a named option is supplied, it must be renamed.

        Any call whose node is *never* a Group can be changed to addsibling.

        Any call whose node is sometimes a Group and sometimes not might need
        to call this method, or might have a bug because it does, if the calling
        code was written with the wrong assumption about node's Groupness!

        [We might un-deprecate this by redefining it as what to do when you drop
        node onto self during drag-and-drop, but really that should be its own
        separate method, even if it's pretty similar to this one. This is one is
        used by a lot of old code as if it was always one or the other of the
        two methods it can call! This was sometimes justified but in other cases
        was wrong and caused bugs.]
        """
        ###REVIEW: how should each call of this behave if node is a group that
        # acts like a leaf node for some purposes, e.g. DnaGroup? @@@@
        # [bruce 080303 comment]

        # for a leaf node, add it to the dad node just after us;
        # note that Group implem has different behavior.
        # [bruce 071110 revised, as part of splitting Group into its own module]
        self.addsibling( node, before = before_or_top)
        return

    def genvisibleleaves(self, include_parents = False): #bruce 060220
        """
        Assuming self is visible in the MT (ignoring scrolling), return a
        generator which yields the set of self and/or its children which have
        no visible children (i.e. which are leaf nodes, or empty Group nodes
        (good??), or closed Group nodes).

        By default, skip anything which has children we'll yield, but if
        include_parents is True, include them anyway.

        [Note that this uses .open which might be considered
        model-tree-specific state -- if we ever let two MTs show the model
        hierarchy at once, this will need an argument which is the
        openness-dict, or need to become an MT method.]
        """
        # Note: this is not presently used, but should be used, since it helped
        # implement the MT arrow key bindings, which are desirable but were left
        # out in the port to Qt4, even though their implem has nothing to do
        # with Qt except for receiving the arrow key events.
        # [bruce 071206 comment]
        if self.is_group() and self.open and self.openable(): 
            #bruce 080108 added .openable cond (guess)
            visible_kids = self.MT_kids() #bruce 080108 .members -> .MT_kids()
            if visible_kids:
                if include_parents:
                    yield self
                    #e Do we want another option, for yielding parents before
                    # vs. after their kids? I don't yet know of a use for it
                    # ('before' is what we want for MT arrow keys, whether
                    # moving up or down, since for 'up' we reverse this entire
                    # sequence).
                for m in visible_kids:
                    for s in m.genvisibleleaves(include_parents = include_parents):
                        yield s
                return
        yield self
        return

    def pick(self):
        """
        select the object

        [extended in many subclasses, notably in Group]

        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        ###@@@ I don't know whether that new rule is yet followed by
        # external code [bruce 050124].
        #bruce 050131 for Alpha: I tried to make sure it is; at least
        # it's now followed in "pick" methods.
        if not self.picked:
            if self.part is None:
                #bruce 080314 check for this
                print "likely to cause bugs: .part is None in .pick for %r" % self
            self.picked = True
            # bruce 050125: should we also call self.assy.permit_picked_parts() 
            # here? ###@@@ [not just in chunk.pick]
            #bruce 050131 for Alpha: I'm guessing we don't need to, for jigs 
            # or groups, since they don't get into assy.molecules or selmols.
            # Whether doing it anyway would be good or bad, I don't know,
            # so no change for now.
            self.changed_selection() #bruce 060227
            self.change_current_selgroup_to_include_self()
                # note: stops at a picked dad, so should be fast enough during recursive use
        
    def ModelTree_plain_left_click(self): #bruce 080213 addition to Node API
        """
        Subclasses which want side effects from a plain, direct left click
        in a model tree widget (after the usual effect of self.pick)
        should implement those by overriding this method.

        (Note that .pick, unlike this method, can also be called due to
        selecting a Group, select all, context menu, or even Undo.)
        """
        pass

    def ModelTree_context_menu_section(self): #bruce 080225 addition to Node API
        """
        Return a menu_spec list to be included in the Model Tree's context
        menu for this node, when this is the only selected node
        (which implies the context menu is specifically for this node).

        Default implementation returns []. Subclasses which want to extend this
        should in most cases first call the superclass version of this method,
        and then append their menu item tuples to the end of the list it returns,
        and return that. But in principle they could prepend or insert new items
        between specific items in the superclass value, or even remove superclass
        items, add wrappers to their methods, etc.

        @see: makemenu_helper, for documentation of the menu_spec format.
        """
        return []

    def unpick(self):
        """
        unselect the object, and all its ancestor nodes.

        [extended in many subclasses, notably in Group]

        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        ###@@@ I don't know whether that new rule is yet followed by external
        # code [bruce 050124].
        if self.picked:
            self.picked = False
            self.changed_selection() #bruce 060227
        # bruce 050126 change: also set *all its ancestors* to be unpicked.
        # this is required to strictly enforce the rule
        # "selected groupnode implies all selected members".
        # We'd do this inside the 'if' -- but only once we're sure all other code
        # no longer bypasses this method and sets node.picked = False directly;
        # this way, if that happens, we might happen to fix up the situation later.
        if self.dad and self.dad.picked:
            self.dad.unpick_top() # use the method, in case a Group subclass overrides it

    def changed_selection(self): #bruce 060227
        """
        Record the fact that the selection state of self or its contents
        (Group members or Chunk atoms) might have changed.
        """
        if self.assy is not None:
            self.assy.changed_selection()
        return

    def unpick_all_except(self, node):
        """
        unpick all of self and its subtree except whatever is inside node and
        its subtree; return value says whether anything was actually unpicked
        """
        # this implem should work for Groups too, since self.unpick does.
        if self is node:
            return False
        res = self.picked # since no retval from unpick_top; this is a 
            # correct one if our invariants are always true
        self.unpick_top()
        res2 = self.unpick_all_members_except( node)
        # btw, during recursive use of this method,
        # unpick_top (either the Node or Group implem)
        # will see self.dad is not picked
        # and not need to keep calling unpick_top
        return res or res2

    def unpick_all_members_except(self, node):
        """
        [#doc; overridden in Group] 
        
        return value says whether anything was actually unpicked
        """
        return False

    def unpick_top(self): #bruce 050124 #bruce 050131 making it correct for chunk and jig
        """
        unselect the object -- but (unlike Group.unpick) don't change
        the selection state of its members. But do unselect all its ancestor nodes.
        [unlike unpick, this is generally NOT extended in subclasses, except in Group.]
        """
        # this implem is only correct for leaf nodes:
        self.unpick() # before 050131 was Node.unpick(self), which was wrong for chunk and jig.

    def is_glpane_content_itself(self): #bruce 080319
        """
        Is self (not counting its content) normally shown in the glpane
        due to its class or nature (ignoring anything transient like
        display style settings or current part)?

        And if so, should its not being picked prevent Groups
        containing it from being picked due to all their other
        glpane content being picked, when they occur inside certain
        kinds of Groups on which this can be called? (This is a moot
        point for most kinds of nodes based on planned usage of this
        method as of 080319, but might matter later.)

        @rtype: boolean

        @see: methods (on other classes) with "movable" in their name.

        [many subclasses must override this; not all yet do, but this
         does not yet cause harm due to how this so far needs to be used,
         as of 080319. For current usage, Chunk must override this,
         and DnaMarker must return false for it. For correctness,
         many other jigs, including ChainAtomMarker by default,
         ought to return True for it, but this may be NIM.]
        """
        # See comment on Jig method for effect of this being False
        # when self is visible in GLPane, and discussion. [bruce 080319]

        # Note: some code which tests for "Chunk or Jig" might do better
        # to test for this method's return value. [bruce circa 080319]
        
        # REVIEW: rename to indicate "3d" or something else about the physical
        # model, rather than "glpane"? It's not about graphical display, but
        # about selection semantics based on what's part of the 3d model on
        # which selection operates. [bruce 090123 comment]

        return False

    def pick_if_all_glpane_content_is_picked(self): #bruce 080319
        """
        For documentation, see the Group implementation of this method.

        @return: whether self contains any (or is, itself) "glpane content".

        @see: Group.pick_if_all_glpane_content_is_picked

        @note: has no side effect when self is a leaf node, since if it
               should pick self, self is already picked.

        [must be overridden by Group; should not need to be overridden
         by any other subclasses]
        """
        return self.is_glpane_content_itself() # correct for leaf nodes

    def call_on_topmost_unpicked_nodes_of_certain_classes(self, func, classes): #bruce 080319
        """
        Call func on the topmost unpicked subnodes of self (i.e. self
        or its members at any level) which have one of the given classes.

        (The "topmost such nodes" means the ones that are not contained in other
        such nodes. I.e. if we call func on a node, we never call it on
        a member of that node at any level.)
        """
        if self.picked:
            return
        call_on_self = False
        for clas in classes:
            if isinstance(self, clas):
                # review: can isinstance just be passed a list or tuple?
                # (in Pythons as old as the ones we still support)
                call_on_self = True
                break
            continue
        if call_on_self:
            func(self)
        elif self.is_group():
            for m in self.members:
                m.call_on_topmost_unpicked_nodes_of_certain_classes(func, classes)
        return

    _old_dad = None ###k not yet used? 
    
    #####@@@@@ review got to here, except: to chgdad added only cmts plus
    #####docstring plus new name

    def changed_dad(self):
        """
        [private method]

        Must be called after self.dad might have changed, before again exposing
        modified node to the public. Keeps some things up to date continuously;
        records info to permit updating other things later.
        """
        node = self
        
        ## from changes import changed #bruce 050303, removed 050909
        ## not needed as of 050309:
        ## changed.dads.record(node) 
        ##     # make sure node's Part will be updated later if needed 
        ##     # [bruce 050303]

        assert node.dad is not None 
            #k not sure if good to need this, but seems to fit existing calls...
            # that might change [050205 comment]
            
            #e if no dad: assy, space, selgroup is None.... or maybe keep
            # prior ones around until new real dad, not sure

        assert node.assy is node.dad.assy or node.assy is None, \
               "node.assy is not node.dad.assy or None: " \
               "node %r, .assy %r, .dad %r, .dad.assy %r" % \
               (node, node.assy, node.dad, node.dad.assy )
            # bruce 050308/080218, since following assy code & part code
            # has no provision yet for coexisting assemblies
        
        node.assy = node.dad.assy 
            # this might change soon, or might not... but if it's valid at
            # all, it needs to be propogated down! we leave it like this for
            # now only in case it's ever being used to init the assy field
            # from None.
        
        #bruce 050308: continually let assigned node.dad.part get inherited 
        # by unassigned node.part (recursively)
        if node.dad.part is not None:
            if node.part is None:
                # Note, this is the usual way that newly made nodes
                # acquire their .part for the first time!
                # They might be this node or one of its kids
                # (if they were added to a homeless Group, which is this node).
                #
                # update, bruce 080314: it is also ok for newly made nodes
                # to call .inherit_part directly in their constructor,
                # which means this call will do nothing. This is necessary
                # before they call things that want them to have a .part,
                # like .pick. Doing this fixed a bug in DnaLadderRailChunk.
                node.inherit_part(node.dad.part) # recurses only into kids with no .parts
        else:
            #bruce 050527 new feature: dad can also inherit from kid, but only prior_part
            if node.dad.prior_part is None: # as well as node.dad.part, already checked
                node.copy_prior_part_to(node.dad)
        if node.picked:
            # bruce 050131 for Alpha:
            # worry about whether node is in a different selection group than before;
            # don't know if this ever happens, but let's try to cooperate if it does:
            node.change_current_selgroup_to_include_self()
                # note: this has no effect if node doesn't have a selgroup
        if node.dad.picked:
            node.pick() 
            #bruce 050126 - maintain the new invariant! (two methods need this)
            
            # Warning: this might make some callers need to update glpane who
            # didn't need to before. possible bugs from this are not yet
            # analyzed.
            
            # Note 050206: the clipboard can't be selected, and if it could
            # be, our invariants would be inconsistent if it had more than one
            # item! (Since all items would be selected but only one selgroup
            # should be.) So, this line never picks a clipboard item as a
            # whole.
        return

    def inherit_part(self, part): #bruce 050308
        """
        #doc (see Group method docstring)

        [overridden in Group]
        """
        # this implem is sufficient only for leaf nodes
        assert self.part is None
        part.add(self)
        assert self.part is part

    def all_content_is_hidden(self): #ninad 080129
        """
        Returns whether this node, including all its contents, is hidden
        (not shown in GLPane, and shown with inverted icon in Model Tree).
        The default implementation for Node returns the value of self.hidden.
        But for Group, this method (all_content_is_hidden) should be overridden
        to return True only when all members of the Group are hidden.
        @see: Group.all_content_is_hidden (which overrides this method)
        """
        #bruce 080205 renamed this from isHidden to all_content_is_hidden,
        # to avoid confusion with the QWidget method isHidden (also used
        # in our code)
        return self.hidden

    def hide(self):
        if not self.hidden:
            self.changed() #bruce 050512 part of fixing bug 614
        self.hidden = True
        self.unpick()

    def Hide(self): 
        """
        Hide self, and update the MT and GLPane accordingly.
        """
        # note: this is called from a node's (Jig) "Hide" context menu item
        # (in the GLPane, not MT). mark 060312.
        self.hide()
        if self is self.assy.o.selobj:
            # Without this, self will remain highlighted until the mouse moves.
            self.assy.o.selobj = None
        self.assy.w.win_update()

    def unhide(self):
        if self.hidden:
            self.changed() #bruce 050512 part of fixing bug 614
        self.hidden = False

    def apply2all(self, fn):
        """
        Apply fn to self and (as overridden in Group) all its members;
        see Group.apply2all docstring for details.
        [overridden in Group]
        """
        fn(self)
        return

    def apply_to_groups(self, fn):
        """
        Like apply2all, but only applies fn to all Group nodes (at or under self).

        @note: this *does* apply fn to leaf-like Groups such as DnaStrand,
               and to any groups inside them (even though they are not
               user-visible in the model tree).
        
        [overridden in Group]
        """
        pass

    def apply2picked(self, fn):
        """
        Apply fn to the topmost picked nodes under (or equal to) self,
        but don't scan below picked nodes.

        See Group.apply2picked docstring for details.
        [overridden in Group]
        """
        if self.picked:
            fn(self)
        return

    def hindmost(self):
        """
        [docstring is meant for both Node and Group methods taken together:]

        Thinking of nodes as subtrees of the model tree, return the smallest
        subtree of self which contains all picked nodes in this subtree, or None
        if there are no picked nodes in this subtree. Note that the result does
        not depend on the order of traversal of the members of a Group.
        """
        if self.picked: 
            return self
        return None

    def ungroup(self):
        """
        If this Node is a Group, dissolve it, letting its members
        join its dad, if this is possible and if it's permitted as a
        user-requested operation. See our Group implem for details.
        """
        #bruce 050121 inferred docstring from 2 implems and 1 call
        return

    # == copy methods -- by default, Nodes can't be copied, so all
    # == copyable Node subclasses should override these methods.

    def will_copy_if_selected(self, sel, realCopy): 
        """
        Will this node copy itself when asked (via copy_in_mapping or
        postcopy_in_mapping [#doc which one!]) because it's selected in sel,
        which is being copied as a whole?
        
        [Node types which implement an appropriate copy method should override
        this method.]
        
        If the realCopy boolean is set (indicating this is a real copy
        operation and not just a test), and if this node will not copy, it may
        want to print a warning.
        """
        #bruce 050525; wware 060329 added realCopy arg
        if realCopy:
            #bruce 060329 added this default message, since it's correct if
            #the whole realCopy scheme is, though I'm dubious about the whole
            #scheme.
            msg = "Node [%s] won't be copied." % (self.name)
            env.history.message(orangemsg(msg))
        return False # conservative answer

    def will_partly_copy_due_to_selatoms(self, sel):
        """
        For nodes which say True to .confers_properties_on(atom) for one or
        more atoms which are part of a selection being copied, but when this
        node is not selected, will it nonetheless copy all or part of itself,
        when its copy_partial_in_mapping method is called, so that the copied
        atoms still have the property it confers?
        
        [Node types which implement an appropriate copy method should override
        this method too.]
        """
        return False # conservative answer

    def confers_properties_on(self, atom):
        """
        Does this Jig (or any node of a type that might appear in atom.jigs)
        confer a property on atom, so that it should be partly copied, if
        possible (by self.copy_partial_in_mapping) when atom is?

        Note: only Anchor overrides this (as of 070608), and the only new
        kinds of Nodes that might need to override it would be Jigs designed
        to alter the rendering or simulation properties of all their atoms, as
        a substitute for directly storing those properties on the atoms. If in
        doubt, don't override it.
        """
        return False # default value for most jigs and (for now) all other Nodes

    def copy_full_in_mapping(self, mapping): # Node method
        """
        If self can be fully copied, this method (as overridden in self's
        subclass) should do so, recording in mapping how self and all its
        components (eg chunk atoms, group members) get copied, and returning
        the copy of self, which must be created in mapping.assy (which may
        differ from self.assy).
        
        If self will refuse to be fully copied, this method should return
        None. [###k does it need to record that in mapping, too?? not for
        now.]
        
        It can assume self and all its components have not been copied yet
        (except for shared components like bonds #k #doc). It can leave out
        some mapping records for components, if it knows nothing will need to
        know them (e.g. atoms only need them regarding some bonds and jigs).
        
        For references to things which might not have been copied yet, or
        might never be copied (e.g. atom refs in jigs), this method can make
        an incomplete copy and record a method in mapping to fix it up at the
        end. But it must decide now whether self will agree or refuse to be
        copied (using mapping.sel if necessary to know what is being copied in
        all).
        
        [All copyable subclasses should override this method.]
        """
        return None # conservative version

    copy_partial_in_mapping = copy_full_in_mapping 
        # equivalent for all jigs which need it, as of 050526
        # [method name added 050704]
        #
        # Note (bruce 060523): this might be wrong for jigs that overrode
        # copy_full_in_mapping, but since copy_partial_in_mapping is not
        # presently called, I won't bother to clean it up for now.

    def copy_in_mapping_with_specified_atoms(self, mapping, atoms): 
        #bruce circa 050525; docstring revised 050704
        """
        #doc; must honor mapping.assy; certain subclasses should override
        [e.g. chunk]; for use in copying selected atoms
        """
        return None

    def copy_copyable_attrs_to(self, target, own_mutable_state = True): 
        """
        Copy all copyable attrs (as defined by a typically-subclass-specific
        constant tuple which lists their names, self.copyable_attrs) 
        from self to target (presumably a Node of the same subclass as self, 
        but this is not checked, and violating it might not be an error, 
        in principle; in particular, as of 051003 target is explicitly permitted
        to be a methodless attribute-holder).
        
        Target and self need not be in the same assy (i.e. need not have the 
        same .assy attribute), and when this situation occurs, it must not be 
        disturbed (e.g. setting target.assy = self.assy would be a bug).
        
        This method doesn't do any invals or updates in target.
        
        This is not intended to be a full copy of self, since copyable_attrs 
        (in current client code) should not contain object-valued attrs like 
        Group.members, Node.dad, or Chunk.atoms, but only "parameter-like" 
        attributes. It's meant to be used as a helper function for making full
        or partial copies of self, and related purposes. The exact set of 
        attributes to include can be chosen somewhat arbitrarily by each
        subclass, but any which are left out will have to be handled separately
        by the copy methods; in practice, new attributes in subclasses should
        almost always be declared in copyable_attrs.
        
        As of 051003, this method (implem and spec) has been extended to 
        "deep copy" any mutable objects found in attribute values (of the
        standard kinds defined by state_utils.copy_val), so that no mutable
        state is shared between copies and originals. This can be turned off
        by passing own_mutable_state = False, which is a useful optimization
        if serial copies are made and intermediate copies won't be kept.
        
        This is intended as a private helper method for subclass-specific copy
        methods, which may need to do further work to make these attribute-
        copies fully correct -- for example, modifying the values of id- or
        (perhaps) name-like attributes, or doing appropriate invals or updates
        in target.
        
        [subclasses probably never need to extend this method]
        """
        #bruce 050526; behavior and docstring revised 051003
        # REVIEW/TODO: rename this to be private, if indeed it is
        for attr in self.copyable_attrs:
            assert attr != 'assy' # todo: optim by doing this once per class
            val = getattr(self, attr)
            if own_mutable_state:
                val = copy_val(val)
            setattr(target, attr, val) 
                # note: waste of RAM: this turns some default class attrs
                # into unneeded instance attrs (nevermind for now;
                # but note that some classes copy some attrs outside of this
                # method for this reason)
        if isinstance(target, Node):
            # having this condition permits target being just a
            # methodless attribute-holder [new feature, bruce 051003]
            self.copy_prior_part_to( target)
        return

    def copyable_attrs_dict(self):
        """
        Returns a new dictionary containing copied values of attributes
        listed in self.copyable_attrs.
        """
        res = {}
        for attr in self.copyable_attrs:
            val = getattr(self, attr)
            val = copy_val(val)
            res[attr] = val
        return res

    def attr_update(self, dict1):
        """
        Updates the attribute values from dict1 to self
        """
        for attr, val in dict1.iteritems():
            setattr(self, attr, val)

    def copy_prior_part_to(self, target): #bruce 050527
        """
        If target (presumed to be a Node) has no part or prior_part, set its
        prior_part from self, for sake of initial views of new Parts
        containing target, if any such new Parts are yet to be made.
        """
        if target.part is None and target.prior_part is None:
            if self.part is not None:
                target.prior_part = self.part
            else:
                target.prior_part = self.prior_part
        return

    def own_mutable_copyable_attrs(self):
        """
        [WARNING: this docstring is out of date as of 051003]

        If any copyable_attrs of self are mutable and might be shared with
        another copy of self (by self.copy_copyable_attrs_to(target) -- where
        this method might then be called on self or target or both), replace
        them with copies so that they are no longer shared and can safely be
        independently changed.
        
        [some subclasses must extend this]
        """
        #bruce 051003 revision: now that copy_copyable_attrs_to deepcopies
        #mutable parameter values, this method will only need overriding for
        #mutable state of types that method can't handle or which for some
        #other reason is not declared in self.copyable_attrs.
        
        ##e note: docstring and perhaps method name should be changed; most
        #calls should remain, but all overridings of this method (and/or
        #related decls of mutable_attrs) should be reviewed for removal. [as
        #of 060523, the only override is in jig_Gamess.py, and it could
        #probably be removed but that requires analysis.]
        pass

##    def copy(self, dad):
##        # just for backwards compatibility until old code is changed [050527]
##        # This method should be removed soon; AFAIK the only caller
##        # is _pasteJig, which never works [bruce 090113 comment]
##        self.redmsg("This cannot yet be copied")
##        if debug_flags.atom_debug:
##            print_compact_stack("atom_debug: who's still calling this " \
##                "deprecated method? this is:\n ")
##        return None # bruce 050131 changed this from "return 0"

    # ==

    def kill_with_contents(self):
        """
        Kill this Node including the 'logical contents' of the node. i.e. 
        the contents of the node that are self.members as well as non-members. 
        Example: A DnaSegment's logical contents are AxisChunks and StrandChunks.
        Out of these, only AxisChunks are the direct members of the DnaSegment
        but the StrandChunks are logical contents of it (non-members).
        So, some callers may specifically want to delete self along with its
        members and logical contents. These callers should use this method.
        The default implementation just calls self.kill().
        @see: dna_model.DnaSegment.kill_with_contents  which overrides this 
              method. 
        @see: EditCommand._removeStructure() which calls this Node API method
        @see: InsertDna_EditCommand._removeSegments()
        """
        #NOTE: This method was defined on 2008-02-22 to support dna_updater
        #implementation in InsertDna_EditCommand. 
        #This method is called in EditCommands instead of calling widely used 
        #'kill' method.(Example: we are not modifying DnaSegment.kill to delete 
        #even the non-members of DnaSegment, to avoid potential internal bugs) 
        self.kill()    

    def kill(self): # see also self.destroy()
        """
        Remove self from its parents and (maybe) destroy enough of its content
        that it takes little room (but be Undoable).
        
        [subclasses should extend this, but should call this Node method at
         the end of their own kill methods]
        """
        ###@@@ bruce 050214 changes and comments:
        #
        #e needs docstring; as of now, intended to be called at end (not start
        # middle or never) of all subclass kill methods; ok to call twice on a
        # node (i.e. to call on an already-killed node); subclass methods
        # should preserve this property
        #
        # also modified the Group.kill method, which extends this method
##        self._f_prekill() #bruce 060327 ##k not positive this is needed in Node
##            # (rather than just Group and Chunk being enough)
##        ###@@@ defect in this (important): jigs dying due to one or all
##        # their atoms dying will run this and mess up the counter.
        self.remove_from_parents()

    _f_will_kill = 0

    def _f_prekill(self): 
        """
        [private helper method for Node.kill and its subclass implems]

        Set self._f_will_kill = ++ _will_kill_count on self, all child nodes,
        and all other owned subobjects that self.kill() would kill, but only
        when it's not already set on self (to avoid exponential runtime in
        Node tree depth, when recursive kill calls this), and only on Node
        classes which might own objects which need it (currently Atoms and
        maybe Bonds and conceivably Parts).
        
        This flag tells Atoms being killed not to create new bondpoints on
        their neighbors when those are also being killed, which is a big
        optimization. It can do other similar things if we discover them -- in
        general, it means "I'm also being killed so don't spend lots of time
        healing my wounds when you're being killed".
        
        @note: Undo will revive killed objects, so kill needs to remove this
        flag from them when it returns, and Undo might assert that it's not
        set on revived objects.
        
        @note: We increment a counter when setting this, so as not to have to
        worry about whether leftover sets of it will cause trouble. This might
        make some of what's said above (about unsetting it) unnecessary.
        [subclasses should not extend this, but should extend _f_set_will_kill
        instead; at least Group and Chunk need to do that]
        """    
        #bruce 060327 in Node (mainly to speed up Delete of chunks, also
        #(short term purpose) to reduce memory leaks)
        global _will_kill_count
        if self._f_will_kill < _will_kill_count:
            _will_kill_count += 1
            self._f_set_will_kill( _will_kill_count) 
                # sets it to this value (with no checks) on self, children, atoms
        return

    def _f_set_will_kill(self, val): #bruce 060327 in Node
        """
        [private helper method for _f_prekill; see its docstring for details;
        subclasses with owned objects should extend this]
        """
        self._f_will_kill = val

    glname = 0 
        # required class constant in case of repeated calls of self.destroy()
        # [bruce 060322]

    def destroy(self):
        """
        delete cyclic refs (so python refdecr can free self)
        and refs to large RAM-consuming attrs; and more
        [#doc, see code comments]
        """
        self.kill() #bruce 060117 guess at implem
        #bruce 060117 draft, experimental, not yet widely used; 
        # obs comment: not sure if it should differ from kill [but see below]
        
        #bruce 060322 comments:        
        # Bugs: arbitrary-order calls (vs other obj destroy methods) are
        # probably not yet safe (for planned future calls of this method, to
        # plug memory leaks).
        # Note: a potential difference of destroy from kill -- after kill, a
        # Node might be revived by Undo; after destroy, it won't be. Things
        # like its entry in various global dicts for change-tracking, glname,
        # undo objkey, etc, should either be weak or should be explicitly
        # removed by destroy. This is nim, but is important for plugging
        # memory leaks. These comments apply to the destroy methods of all
        # model objects and their child or helper objects, not only to Nodes.
        # ###@@@ #e
        # We want this dealloc_my_glselect_name, but first we have to review
        # all calls to Node.destroy to verify it's not called when it
        # shouldn't be (e.g. when that node might still be revived by Undo).
        # ###@@@ BTW, as of 060322 the appropriate init, alloc, and draw code
        # for glname is only done (or needed) in Jig.
        ## self.assy.dealloc_my_glselect_name( self, self.glname ) 
        ##     # only ok for some subclasses; some have ._glname instead
        ##e more is needed too... see Atom and Bond methods
        # do we want this:
        ## self.__dict__.clear() ###k is this safe???
        return

    def remove_from_parents(self):
        #bruce 051227 split this out of Node.kill for use in new Node.set_assy
        """
        Remove self from its parents of various kinds
        (part, dad, assy, selection) without otherwise altering it.
        """
        ###@@@ bruce 050214 changes and comments:
        # added condition on self.dad existing, before delmember
        # added unpick (*after* dad.delmember)
        # added self.assy = None
##        self._um_deinit() #bruce 051005 #k this is not good enough unless 
##            # this is always called when a node is lost from the MT!
        if self.dad:
            self.dad.delmember(self)
                # this does assy.changed (if assy), dad = None, and unpick,
                # but the unpick might be removed someday, so we do it below too
                # [bruce 050214]
        self.unpick() # must come after delmember (else would unpick dad) and
            # before forgetting self.assy
        self.reset_subtree_part_assy()

    def reset_subtree_part_assy(self): #bruce 051227 split this out
        """
        Cleanly reset self.part and self.assy to None, in self and its node-subtree
        (removing self and kids from those containers in whatever ways are needed).
        Assume self is not picked.

        [Subclasses (especially Group) must extend this as needed.]
        """
        assert not self.picked
        if self.part: 
            #bruce 050303; bruce 051227 moved from start of routine (before
            # delmember) to here (after unpick), not sure ok
            self.part.remove(self)
        env.node_departing_assy(self, self.assy) #bruce 060315 for Undo
        self.assy = None #bruce 050214 added this ###k review more
            #bruce 060315 comments about this old code:
            # reasons to set assy to None:
            # - helps avoid cycles when destroying Nodes
            # - logical part of set_assy (but could wait til new assy is stored)
            # reasons not to:
            # - Undo-tracked changes might like to use it to find the right
            #   AssyUndoArchive to tell about the change
            #   (can we fix that by telling it right now? Not sure... in theory,
            #   more than one assy could claim it if we Undo in some!)
            # - we might avoid needing to scan it and store it as undoable state
            # - some bugs are caused by code that tries to find win, glpane, etc
            #   from assy
            # tentative conclusion:
            # - don't stop doing this for A7
            # - but tell Undo about the change, as part of letting it know which
            #   atoms are changing (namely, all those still in this Node, if 
            #   it's a chunk -- perhaps this will usually be no atoms?);
            #   other changes on atoms can safely only tell the assy they refer
            #   to (via atom.molecule.assy) (or no assy if that's None).

    def is_ascendant(self, node): # implem corrected by bruce 050121; was "return None"
        """
        Is node in the subtree of nodes headed by self?
        [Optimization of Group.is_ascendant for leaf nodes;
        see its docstring for more info.]
        """
        return self is node # only correct for self being a leaf node

    def moveto(self, node, before = False):
        """
        DEPRECATED. Use node.addchild(self) or node.addsibling(self) instead.

        Move self to a new location in the model tree, before or after node
        according to the <before> flag, or if node is a Group, somewhere
        inside it (reinterpreting 'before' flag as 'top' flag, to decide where
        inside it). Special case: if self is node, return with no effect
        (even if node is a Group).
        """
        #todo: rename for DND, and clean up; has several external calls
        # (but as of 080317, no longer used in MT DND)

        ###REVIEW: how should each call of this behave if node is a group that
        # acts like a leaf node for some purposes, e.g. DnaGroup? @@@@
        # [bruce 080303 comment]

        #bruce 050110 updated docstring to fit current code.
        # (Note that this makes it even more clear, beyond what's said in addmember
        #  docstrings, that addmember interface mixes two things that ought to be
        #  separated.)

        #bruce 050205 change: just go directly to addmember, after my addchild
        # upgrades today. note, this 'before' is a positional arg for the
        # before_or_top flag, not the named arg 'before' of addchild!
        # BTW we *do* need to call addmember (with its dual personality
        # depending on node being a leaf or not) for now, while DND uses
        # "drop onto a leaf node" to mean what "drop under it" ought to mean.

        node.addmember(self, before_or_top = before)
            # note: this needs to be addmember, not addchild or addsibling
        return

    def nodespicked(self):
        """
        Return the number of nodes currently selected in this subtree.

        [subclasses must override this!]

        Warning (about current subclass implementations [050113]):
        scans the entire tree... calling this on every node in the tree
        might be slow (every node scanned as many times as it is deep in the tree).
        """
        if self.picked:
            return 1 # number, not boolean!
        else:
            return 0

    def edit(self): # REVIEW [bruce 090106]: should this method be renamed editProperties?
                    # (Would that name apply even when it enters a command?
                    #  BTW should the same API method even be used in those two cases?)
                    # To rename it, search for 'def edit', '.edit' (whole word), "edit method".
                    # But note that not all of those methods are on subclasses of Node.
        """
        [should be overridden in most subclasses]

        If this kind of Node has properties that can be edited
        with some sort of interactive dialog, do that
        (put up the dialog, wait for user to dismiss it, change the properties
        as requested, and do all needed invals or updates),
        and then return None (regardless of Cancel, Apply, Revert, etc).
           Or if it or its properties can be edited by a Command,
        enter that command and return None.
           If this kind of Node *doesn't* support editing of properties,
        return a suitable text string for use in an error message.
        (In that case, editProperties_enabled should also be overridden,
         and if it is, probably this method will never get called.)
        """
        #bruce 050121 inferred docstring from all 7 implems and 1 call.
        # Also added feature of refusing and returning error message, used in 2 implems so far.
        #bruce 050425 revised this error message.
        #bruce 090106 revised error message again, and added "Command"
        # part of docstring, guessing this from the implem in NanotubeSegment.
        return "Edit Properties is not available for %s." % self.short_classname()

    def editProperties_enabled(self): #bruce 050121 added this feature #bruce 090106 renamed
        """
        Subclasses should override this and make it return False
        if their edit method would refuse to edit their properties.
        """
        # i don't know if they all do that yet...
        #e should we check here to see if they override Node.edit?? nah.
        return True # wrong for an abstract Node, but there is no such thing!

    def dumptree(self, depth = 0): # just for debugging
        print depth * "...", self.name

    def node_must_follow_what_nodes(self): 
        #bruce 050422 made Node and Jig implems of this from function of same name
        """
        [should be overridden by Jig]

        If this node is a leaf node which must come after some other leaf nodes
        due to limitations in the mmp file format, then return a list of those nodes
        it must follow; otherwise return (). For all Groups, return ().

        Note:

        If we upgrade the mmp file format to permit forward refs to atoms
        (not just to whole leaf nodes, as it does now),
        then this function could legally return () for all nodes
        (unless by then there are nodes needing prior-refs to things other than atoms).

        However, it probably shouldn't, since it is also used for placement of nodes
        which refer to other nodes in a logical relative position in the model tree.
        """
        return () #bruce 071214 optim: return (), not []

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """
        Write this Node to an mmp file, as controlled by mapping,
        which should be an instance of writemmp_mapping.

        [subclasses must override this if they need to be writable into an mmp file;
         we print a debug warning if they don't (and something tries to write them).]
        """
        # bruce 050322 revising this; this implem used to be the normal way
        # to write Jigs; now it's basically an error to call this implem,
        # but it's harmless -- it puts a comment in the mmp file and prints a debug warning.
        line = "# not yet implemented: mmp record for %r" % self.__class__.__name__
        mapping.write(line + '\n')
        if debug_flags.atom_debug:
            print "atom_debug:", line
        return

    def writemmp_info_leaf(self, mapping): #bruce 050421
        """
        leaf node subclasses should call this in their writemmp methods,
        after writing enough that the mmp file reader will have created a Node for them
        and added it to its current group (at the end is always safe, if they write no sub-nodes)

        [could be overridden by subclasses with more kinds of "info leaf" keys to write]
        """
        assert not self.is_group()
        if self.hidden:
            mapping.write("info leaf hidden = True\n")
        if self.disabled_by_user_choice: 
            # [bruce 050505 revised this so all Nodes have the attribute, 
            #  tho so far only Jigs use it]
            mapping.write("info leaf disabled = True\n") #bruce 050422
        return

    def writemdl(self, alist, f, dispdef): 
        #bruce 050430 added Node default method to fix bug reported by Ninad for A5
        pass

    def writepov(self, file, dispdef): #bruce 050208 added Node default method
        pass

    def draw(self, glpane, dispdef):
        """
        @see: self.draw_after_highlighting()
        """
        pass

    def draw_after_highlighting(self, 
                                glpane, 
                                dispdef, 
                                pickCheckOnly = False):
        """
        Things to draw after highlighting. Subclasses can override this 
        method. Default implementation draws nothing and returns False
        (which is correct for most kinds of Nodes, at present).
        
        Draw the part of self's graphical appearance (or that of its members
        if its a Group) that needs to be drawn AFTER the main drawing 
        code has completed its highlighting/stenciling for selobj.
        
        @param pickCheckOnly: [needs documentation of its effect]
                              (for example use, see this method in class Plane)
        @type pickCheckOnly: boolean
        
        @return: A boolean flag 'anythingDrawn' that tells whether this method
        drew something. 
        @rtype: boolean
        
        @see: GraphicsMode.Draw_after_highlighting() which returns this method
        @see: Group.draw_after_highlighting()
        @see: Plane.draw_after_highlighting()     
        """
        #Ninad 2008-06-20: This is a new API method that completely 
        #replaces the implementation originally in method Utility._drawESPImage().
        #Also did many bug fixes in the original implementation. 
        #
        ###TODO: The return value anythingDrawn is retained from the old 
        # implementation, as some other code in SelectGraphicsMode._calibrateZ 
        # apparently uses it. Need to check if that code is used anywhere.
        # [bruce 080917 adds: Yes, it's used in jigGLSelect and
        #  get_jig_under_cursor, which are still needed for now,
        #  though they should be removed someday. That is probably the
        #  only ultimate use of this return value (not sure).]
        anythingDrawn = False
        return anythingDrawn

    def draw_in_abs_coords(self, glpane, color): 
        #bruce 050729 to fix some bugs caused by Huaicai's jig-selection code
        """
        Default implementation of draw_in_abs_coords. Some implem is needed
        by any nodes or other drawable objects which get registered with
        self.assy.alloc_my_glselect_name and thereby need to provide Selobj_API.

        [Subclasses which are able to use color for highlighting in Build mode,
         or which want to look different when highlighted in Build mode,
         or which are ever drawn in non-absolute modelview coordinates,
         or for which glpane.displayMode is not what would be passed to their draw method,
         should override this method.]
        """
        dispdef = glpane.displayMode
        del color
        self.draw(glpane, dispdef)
        return

    def killed(self): #bruce 050729 to fix some bugs caused by Huaicai's jig-selection code
        alive = self.dad is not None and self.assy is not None
        return not alive # probably not correct, but should be good enough for now

    def getinfo(self):
        pass

    def init_statistics(self, stats):
        """
        Initialize statistics for this Node
        """
        # Currently, this is only used by "part" and "group" nodes.
        # See PartProp.__init__() or GroupProp.__init__().
        # Mark 050911.
        stats.nchunks = 0
        stats.natoms = 0
        stats.nsinglets = 0
        stats.nrmotors = 0
        stats.nlmotors = 0
        stats.nanchors = 0
        stats.nstats = 0
        stats.nthermos = 0
        stats.ngamess = 0
        stats.num_espimage = 0
        stats.num_gridplane = 0
        stats.num_mdistance = 0
        stats.num_mangle = 0
        stats.num_mdihedral = 0
        stats.ngroups = -1 # Must subtract self.

    def getstatistics(self, stats):
        pass

    def break_interpart_bonds(self): 
        #bruce 050308 for assy/part split, and to fix bug 371 and related bugs for Jigs
        """
        Break all illegal bonds (atom-atom or atom-Jig or (in future) anything similar)
        between this node and other nodes in a different Part.
        [Note that as of 050513 and earlier, all atom-Jig interpart bonds
         are permitted; but we let the Jig decide that.] 
        Error if this node or nodes it bonds to have no .part.
        Subclasses with bonds must override this method as appropriate.
           It's ok if some kinds of nodes do this more fancily than mere "breakage",
        e.g. if some Jigs break into pieces so they can keep connecting
        to the same atoms without having any inter-Part bonds,
        as long as, after this is run on all nodes in any subtree using apply2all,
        no inter-part bonds are left, and it works whether or not newly
        created nodes (created by this method while apply2all runs)
        have this method called on them or not.
           The Group implem does *not* call this on its members --
        use apply2all for that.
        [As of 050308, this is overridden only in class Chunk and
         class Jig and/or its subclasses.]
        """
        pass

    def move(self, offset): #bruce 070501 added this to Node API
        """
        If self has any geometry in 3d space, and if this operation makes
        sense for self's class, translate self in 3d space by the vector offset;
        do all necessary invalidations, but try to optimize those based on
        self's relative structure not having changed or reoriented.
        See also self.rot() and self.pivot().

        @param offset: vector by which to translate self in 3d space
        @type  offset: L{VQT.V}

        @note: there is not yet a Node API method to find out whether
               this method is a noop. However, the Node API defines
               a class constant attribute, is_movable, which is
               closely related to that. See also "getSelectedMovables".

        [most subclasses with content in 3d space should override this method]
        """
        return # correct for many kinds of nodes

    def rot(self, quat):
        #bruce 080305 added this to Node API (already on many subclasses)
        """
        If self has any geometry in 3d space, and if this operation makes
        sense for self's class, rotate self around its center of rotation
        (defined differently by different subclasses) by quaternion I{quat};
        do all necessary invalidations, but optimize those based on
        self's relative structure not having changed. See also self.pivot()
        and self.move().

        @param quat: The quaternion to rotate self by.
        @type  quat: L{VQT.Q}

        @note: there is not yet a Node API method to retrieve self's
               center of rotation, or to find out whether it has one,
               or to find out whether this method is a noop.

        [most subclasses with content in 3d space should override this method]
        """
        return # correct for many kinds of nodes

    def pivot(self, point, quat):
        #bruce 080305 added this to Node API (already on some subclasses)
        """
        If self has any geometry in 3d space, and if this operation makes
        sense for self's class, rotate self around point by quaternion quat;
        do all necessary invalidations, but optimize those based on
        self's relative structure not having changed. See also self.rot()
        and self.move().

        @param point: The point to rotate self around.
        @type  point: L{VQT.V}

        @param quat: The quaternion to rotate self by, around I{point}.
        @type  quat: L{VQT.Q}

        @note: some subclasses define self.rot but not self.pivot.

        @note: there is not yet a Node API method to find out whether
               this method is a noop.

        [most subclasses with content in 3d space should override this method]
        """
        return # correct for many kinds of nodes

    def pickatoms(self):
        #bruce 070501 added this to Node API (was defined only in Chunk)
        """
        Pick the atoms owned by self which are not already picked, and which the selection filter
        permits the user to pick (select). Return the number of newly picked atoms.
        [subclasses that can contain atoms must override this method]
        """
        return 0 # correct for most kinds of nodes

    def contains_atom(self, atom):
        #bruce 080305 added this to Node API
        # (was defined only in Chunk and in a class outside the Node hierarchy)
        """
        Does self contain the given atom (a real atom or bondpoint)?

        [subclasses that can contain atoms must override this method]
        """
        return False # correct for nodes that can't contain atoms

    def get_atom_content(self, flags = -1): #bruce 080306
        """
        Return your current (up to date) atom content
        which intersects the given content flags.

        @param flags: the subset of content flags we should update and return
        @type flags: an "or" of content flag bits [#doc where they are defined]

        @return: current atom content of self
        @rtype: an "or" of content flag bits

        [subclasses which can have any atom content need to override
         this method]
        """
        # default implem, for nodes which can never have atom content
        return 0

    def _f_updated_atom_content(self): #bruce 080306
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.

        [Subclasses which can contain atoms need to override this method.]
        """
        # default implem, for nodes which can never have atom content
        # (note, this default definition is needed on Node, since it's called
        #  on all members of a Group, whether or not they can contain atoms)
        return 0 

    # an old todo comment:
    #in addition, each Node should have the following methods:
    # draw, cut, copy, paste

    pass # end of class Node

# ==

class NodeWith3DContents(Node): #bruce 080305
    # REVIEW: which methods can safely assert that subclass must implement?
    """
    Abstract class for Node subclasses which can have contents
    with 3D position (possibly appearing in the graphics area
    and/or affecting a simulation).

    Notable subclasses (some indirect) include Chunk, Group, Jig.
    """
    def break_interpart_bonds(self):
        """
        [overrides Node method; subclasses must override this method]
        """
        pass ### assert 0, "subclass must implement"        
    def move(self, offset):
        """
        [overrides Node method; subclasses must override this method]
        """
        pass ### assert 0, "subclass must implement"
    def rot(self, quat):
        """
        [overrides Node method; subclasses must override this method]
        """
        assert 0, "subclass must implement"
    def pivot(self, point, quat):
        """
        [overrides Node method; subclasses must override this method]
        """
        assert 0, "subclass must implement"
    # def draw_in_abs_coords?
    pass

# ==

class SimpleCopyMixin(Node):
    # This will probably just become the default implems for these methods in
    # Node, rather than its own class... but first, test it in Comment and
    # View. When it's stable, also see if the copy methods in Jig and even
    # Chunk can make use of these methods somehow (perhaps with these modified
    # to call new optional subclass methods). [bruce 060523]
    
    # Note: there's no reason to put this in its own file different than Node,
    # because it needs no imports of its own, and anything that imports it
    # also has to import Node. [bruce 071026 comment]
    # status [bruce 080313 comment]: used only by Comment, NamedView, PovrayScene.
    # See also def copy_..._mapping methods in other classes.
    """
    Node subclasses that want to be copyable via their _s_attr or
    copyable_attrs decls, and that don't need any optimizations for atoms or
    bonds or for avoiding full copy_val of all attrs, and that don't need any
    special cases like worrying about refs to other copied things needing to
    be transformed through the mapping (i.e. for which all copyable attrs are
    pure data, not node or atom refs), can mix in this class, BEFORE Node,
    provided they contain a correct definition of _um_initargs for use in
    creating the copy-stub, and don't interfere with the attrs of self stored
    by this class, self._orig and self._mapping.
    """
    def will_copy_if_selected(self, sel, realCopy): # in class SimpleCopyMixin
        """
        [overrides Node method]
        """
        return True

    def copy_full_in_mapping(self, mapping): # in class SimpleCopyMixin
        # warning: most of this code is copied from the Jig method.
        clas = self.__class__
        method = self._um_initargs # fyi: for Node, the returned args are assy, name
        args, kws = method()
        # replace self.assy with mapping.assy in args 
        # [new requirement of this method API, bruce 070430]
        newargs = list(args)
        for i in range(len(args)):
            if args[i] is self.assy:
                newargs[i] = mapping.assy
        args = tuple(newargs)
        new = clas(*args, **kws)
        # store special info to help _copy_fixup_at_end
        # (note: these attrnames don't start with __ since name-mangling would prevent
        #  subclasses from overriding _copy_fixup_at_end or this method;
        #  that means all subclasses have to take care not to use those attrnames!
        #  It might be better to let them be "manually name-mangled". ##e FIX)
        new._orig = self
        new._mapping = mapping
        new.name = "[being copied]" # should never be seen
        mapping.do_at_end( new._copy_fixup_at_end)
        #k any need to call mapping.record_copy?? probably not for now,
        # but maybe later if these nodes can be ref'd by others
        # (or maybe the general copy code that calls this will take care of that then).
        return new

    def _copy_fixup_at_end(self): # in class SimpleCopyMixin
        # warning: most of this code is copied from the Jig method.
        """
        [Private method]
        This runs at the end of a copy operation to copy attributes from the old node
        (which could have been done at the start but might as well be done now for most of them).
        Self is the copy, self._orig is the original.
        """
        orig = self._orig
        del self._orig
        mapping = self._mapping # REVIEW: is keeping this reference until we return necessary?
        del self._mapping
        copy = self
        orig.copy_copyable_attrs_to(copy) # this uses copy_val on all attrs
        return

    pass # end of class SimpleCopyMixin

# ==

def topmost_nodes( nodes): #bruce 050303
    """
    Given 0 or more nodes (as a python sequence), return a list
    of the given nodes that are not descendants of other given nodes.

    @see: related method hindmost and function topmost_selected_nodes,
          but those only work for the set of selected nodes.
    
    @warning: current implementation is quadratic time in len(retval)
    """
    res = {} # from id(node) to node
    for node in nodes:
        assert node is not None # incorrect otherwise -- None won't have .is_ascendant method
        dad = node 
            # not node.dad, that way we remove dups as well (might never be needed, but good)
        while dad is not None:
            if id(dad) in res:
                break
            dad = node.dad
        if dad is None:
            # node and its dads (all levels) were not in res
            # add node, but also remove any members that are below it (how?)
            #e (could be more efficient if we sorted nodes by depth in tree,
            #  or perhaps even sorted the tree-paths from root to each node)
            for other in res.values():
                if node.is_ascendant(other):
                    del res[id(other)]
            res[id(node)] = node
    return res.values()

# end
