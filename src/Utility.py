# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""
Classes for objects in the model,
with a uniform API to permit them to be shown in the model tree.

This file mainly defines superclass Node and its subclass Group;
other files define other subclasses of Node, such as molecule and Jig.

This file should have a more descriptive name, but that can wait.

[Temporarily owned by Bruce circa 050105; might be extensively revised.]

$Id$
"""
__author__ = "Josh"

# [some changes and docstrings by bruce]

from VQT import *
from shape import *
from qt import QPixmap
import sys, os
from PartProp import *
from GroupProp import *
from debug import print_compact_stack, print_compact_traceback
import platform
from changes import changed #bruce 050303


# utility function: global cache for QPixmaps (needed by most Node subclasses)

_pixmap_image_path = None
_pixmaps = {}

def imagename_to_pixmap(imagename): #bruce 050108
    """Given the basename of a file in our cad/images directory,
    return a QPixmap created from that file. Cache these
    (in our own Python directory, not Qt's QPixmapCache)
    so that at most one QPixmap is made from each file.
    """
    global _pixmap_image_path, _pixmaps
    try:
        return _pixmaps[imagename]
    except KeyError:
        if not _pixmap_image_path:
            # This runs once per Atom session (unless this directory is missing).
            #
            # (We don't run it until needed, in case something modifies
            #  sys.argv[0] during init (we want the modified form in that case).
            #  As of 050108 this is not known to ever happen. Another reason:
            #  if we run it when this module is imported, we get the error message
            #  "QPaintDevice: Must construct a QApplication before a QPaintDevice".)
            #
            # We assume sys.argv[0] looks like .../cad/src/xxx.py
            # and we want .../cad/images.
            from os.path import dirname, abspath
            cadpath = dirname(dirname(abspath(sys.argv[0]))) # ../cad
            _pixmap_image_path = os.path.join(cadpath, "images")
            assert os.path.isdir(_pixmap_image_path), "missing pixmap directory: \"%s\"" % _pixmap_image_path
        iconpath = os.path.join( _pixmap_image_path, imagename)
        icon = QPixmap(iconpath)
            # missing file prints a warning but doesn't cause an exception,
            # just makes a null icon [i think #k]
        _pixmaps[imagename] = icon
        return icon
    pass

# unique id for all Nodes -- might generalize to other objects too.
# unlike python builtin id(node), will never be reused when an old node dies.

## this failed due to a recursive import error (chem imports * from Utility);
## a fix would be to move genKey to constants.py; I'll do that later.
## from chem import genKey
# for now, just copy the definition:
def genKey(): # copied from chem.py, bruce 050304, as temp kluge
    """ produces generators that count indefinitely """
    i=0
    while 1:
        i += 1
        yield i

nodekey = genKey()
    # note: atoms are not nodes, so possible overlap of
    # atom.key and node._id should be ok for now.

def node_id(node):
    "session-unique id for a Node (never reused) (legal to call for None, then returns None)"
    if node == None:
        return None
    assert isinstance(node, Node) #e might relax this later
    try:
        node._id # make sure it exists already
    except AttributeError:
        node._id = nodekey.next()
    return node._id

# superclass of all Nodes

def node_name(node): # use in error or debug messages for safety, rather than node.name
    if node == None: return "<None>"
    try:
        return node.name
    except AttributeError:
        return "<node has no .name>"
    pass

class Node:
    """
    This is the basic object, inherited by groups, molecules, jigs,
    and some more specialized subclasses. The methods of Node are designed
    to be typical of "leaf Nodes" -- many of them are overridden by Group,
    and some of them by other Node subclasses.
    """
        
    name = "" # for use before __init__ runs (used in __str__ of subclasses)

    # default values of instance variables
    picked = False # whether it's selected
        # (for highlighting in all views, and being affected by operations)
    hidden = False # whether to make it temporarily invisible in the glpane
        # (note: self.hidden is defined, but always False, for Groups;
        #  it might be set for any leaf node whether or not that node is ever actually
        #  shown in the glpane.)
    open = False # bruce 050125; kluge to make it easier to count open nodes in a tree
        # (this will never become True except for Groups)
        # (when more than one tree widget can show the same node, .open will need replacement
        #  with treewidget-specific state #e)
    dad = None
    part = None #bruce 050303

    def __init__(self, assy, name, dad = None): #bruce 050216 fixed inconsistent arg order, made name required
        """Make a new node (Node or any subclass), in the given assembly (assy)
        (I think assy must always be supplied, but I'm not sure),
        with the given name (or "" if the supplied name is None),
        and with the optionally specified dad (a Group node or None),
        adding it to that dad as a new member (unless it's None or not specified, which is typical).
        All args are supplied positionally, even the optional one.
           Warning: arg order was revised by bruce 050216 to be more consistent with subclasses,
        but Group's arg order was and still is inconsistent with all other Node classes' arg order.
        """
        #bruce 050205 added docstring; bruce 050216 revised it
        self.name = name or "" # assumed to be a string by some code
        
##        #bruce 050205 new fields to help fix clipboard/DND bugs -- not yet used, but will be used soon
##        # (and which anticipate some planned Beta features):
##        self.space = None # not a node (what it is is explained separately or not yet);
##            # more like an assy or "subassy";
##            # addmember might change this to dad.assy
##        self.selgroup = -1 # cached find_selection_group() retval, a Node or None, -1 means invalid #e or use getattr? or maintain?
##        #end bruce 050205 new fields

        # assy -- as temporary kluge, permitted to be a Part as well [bruce 050223]
        from assembly import assembly # the class
        if assy and not isinstance(assy, assembly) and not assy == '<not an assembly>':
            try:
                #bruce 050223 probably a temporary debug kluge, though it might turn out we prefer to store a Part anyway, not sure...
                # permit this to be a Part and use its assy, but warn about this
                from part import Part
                assert isinstance(assy, Part)
                part = assy
                assy = part.assy
                if platform.atom_debug:
                    print_compact_stack("atom_debug: Node or Group constructed with Part %r instead of assy %r; fix sometime!" % (part,assy))
            except:
                print_compact_traceback("bug in Node.__init__ assy check, hopefully ignored: ")
                print "assy is %r" % (assy,)
        # verify assy is not None (not sure if that's allowed in principle, but I think it never happens) [050223]
        if not assy:
            if platform.atom_debug: # might not yet be safe to print self, esp if it's a subclass
                print_compact_stack("atom_debug: Node or Group constructed with null assy = %r" % assy)
        self.assy = assy
        if dad: # dad must be another Node (which must be a Group), or None
            dad.addchild(self) #bruce 050206 changed addmember to addchild, enforcing dad correctness
                # warning [bruce 050316]: this might call inherit_part; subclasses must be ready for this
                # by the time their inits call ours, e.g. a Group must have a members list by then.
            assert self.dad == dad
        return

    def is_group(self): #bruce 050216
        """Is self a Group node (i.e. an instance of Group or a subclass)?
        This is almost as deprecated as isinstance(self, Group),
        but not quite, since this would work if Utility was reloaded but that would not!
        (This doesn't yet matter in practice since there are probably other big obstacles
         to reloading Utility during debugging.)
        [overridden in Group]
        """
        return False # for a leaf node

    def is_disabled(self): #bruce 050421 experiment related to bug 451-9
        "Should this node look disabled when shown in model tree (but remain fully functional for selection)?"
        return False 
    
    def redmsg(self, msg): #bruce 050203
        from HistoryWidget import redmsg
        ###@@@ we ought to make this work even after assy set to None in Node.kill!
        self.assy.w.history.message( redmsg( msg ))

##    def select_enabled(self): #obs, better to just override self.pick() [bruce 050206]
##        """Whether model tree should permit selection of this node (and all its members).
##        [To be overridden by Nodes it would be unsafe for the user to *ever* select.
##         Warning: internal code should not select them either, but this might not be enforced.]
##        """
##        return True # for most nodes

    def has_home(self): #bruce 050303; depends on assy more than I'd like, but seems needed for some purposes
        """Is this node a valid tree-member of its assy? (I.e. not yet deleted from its assy's node-tree.)
        [Some node methods require this to be true, with exceptions otherwise;
         so all node methods may assume it (whenever it might matter)
         unless their docstrings say otherwise.]
        """
        # this implem ought to work even if we have more than one assy someday
        node = self
        while node.dad:
            if not node in node.dad.members:
                print_compact_stack("error (ignored): some node is not in it's dad's members list: ")
                node.dad = None
                return False
            node = node.dad # never None, we just checked it above
        return node.assy and node == node.assy.root ###e this is the part that knows too much about an assy. should ask it instead.
##    
##        # first try was:
##        #e if nodes forget about .assy (as will be easiest when we support more than one assy at a time),
##        # then it might be better to say "valid member of *any* assy", and go up dad chain to look for one,
##        # presuming you find a node with explicit assy at the top. (if not, it's homeless, thus invalid.)
##        if not self.assy:
##            return False
##        return self.assy.root.is_ascendant(self)
##            # this doesn't check for nodes being members of their dads! so some bugs might fool it.
    
    def is_top_of_selection_group(self): #bruce 050131 for Alpha [#e rename is_selection_group?] [#e rename concept "selectable set"?]
        """Whether this node is the top of a "selection group".
        (This can be true of leaf nodes as well as group nodes, in spite of the name.)
        We enforce a rule that limits the selection to being entirely within
        one selection group at a time, since many operations on mixes
        of nodes from different selection groups are unsafe.
        [As of 050131, should be True of the PartGroup and any "clipboard item";
         this implem is not complete, so it's overridden by PartGroup.]
        """
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
        # [It could even work if we someday introduce "Groups of clipboard items".]
        # But it's wrong for PartGroup itself (thus is overridden by it).
        return self.dad and self.dad.is_selection_group_container()

    def change_current_selgroup_to_include_self(self): #bruce 050131 for Alpha
        "#doc"
        # This might not be fast enough, so when there's time,
        # replace it with one that optims by stopping when dad is picked.
        foundselgroup, ours = self.find_selection_group_or_picked_dad()
        if not foundselgroup:
            # found a "picked dad"
            assert ours.picked
##            if platform.atom_debug:
##                print "atom_debug: fyi: change_current_selgroup_to_include_self returns early with picked dad %r" % node_name(ours)
            return # no need to change (important optimization for recursive picking in groups)
        if not ours:
            # this might happen for non-bugs since changed_dad calls it for picked nodes,
            # but it makes sense to skeptically review any way that can happen,
            # so the debug print is good even if it's not always a bug [bruce comment 050310]
            if platform.atom_debug:
                print "atom_debug: bug(?): change_current_selgroup_to_include_self on node with no selgroup; ignored"
            return
        # ours is this node's selgroup, and might or might not already be the current one in self.assy
        prior = self.assy.current_selgroup_iff_valid() # might be None but otherwise is always valid; no side effects [revised 050310]
        if ours != prior:
##            if platform.atom_debug:
##                print "change_current_selgroup_to_include_self: prior %r != ours %r" % \
##                      (node_name(prior), node_name(ours))
            self.assy.set_current_selgroup( ours)
                # this unpicks everything not in 'ours' and warns if it unpicked anything
        return

    ## bruce 050310 revising this and moving it into an assy method
##    def current_selection_group(self): #bruce 050131 for Alpha
##        # warning, this is also the name of an assy instance var -- that one should have a private name
##        try:
##            maybe = self.assy.current_selection_group
##            if maybe == None: return None
##            if maybe.assy != self.assy:
##                return None
##            if not maybe.is_top_of_selection_group():
##                return None
##            if not self.assy.root.is_ascendant(maybe):
##                return None
##        except:
##            print_compact_traceback("exception in current_selection_group() ignored, returning None: ")
##            return None
##        return maybe

    def find_selection_group(self): #bruce 050131 for Alpha #####@@@@@ needs update/review for being called on deleted nodes; pass assy?
        """Return the selection group to which this node belongs, or None if none
        (as of 050131 that should happen only for Clipboard or Root).
        """
        node = self
        while node:
            if node.is_top_of_selection_group():
                break
            node = node.dad # might be None; always is eventually, so loop always terminates by then
        return node # might be None

    def find_selection_group_or_picked_dad(self): #bruce 050131 for Alpha
        """Return (True, selgroup) where selgroup (maybe None) would be returned by find_selection_group,
        or (False, picked_dad) if you hit a "picked dad of self" (implying that self's selection group,
        whatever it is, is the current one, assuming no bugs in our new invariants).
        Prefer the picked_dad retval since it's faster.
        """
        node = self
        while node:
            if node.is_top_of_selection_group():
                break
            node = node.dad # might be None; always is eventually, so loop always terminates by then
            if node:
                # don't try this test for node == self, since it's not a "dad of self"
                if node.picked:
                    return False, node                
        return True, node # might be None
            
    def show_in_model_tree(self): #bruce 050127 ###e needs renaming, sounds like "scroll to make visible" [050310]
        #bruce 050417 warning: I think I never ended up honoring this. Not sure.
        """Should this node be shown in the model tree widget?
        True for most nodes. Can be overridden by subclasses.
        [Added so that Datum Plane nodes won't be shown. Initially,
         it might not work much more generally than that.]
        """
        return True
    
    def haspicked(self): #bruce 050126
        """Whether node's subtree has any picked members.
        Faster than counting them with nodespicked or "maxing" them with hindmost,
        at least when anything is picked; just as slow when nothing is (still requires
        a full scan). [#e should we memoize hindmost data??]
        [overridden in Group, but this docstring applies to both methods together;
         should not be overridden elsewhere.]
        """
        return self.picked

    def permits_ungrouping(self): #bruce 050126 for Node; earlier for Group
        """[Leaf nodes can never (yet) be ungrouped. See Group.permits_ungrouping
        docstring for the general definition of this method.]
        """
        return False
    
    def kids(self, display_prefs): #bruce 050109
        """#doc; see Group.kids()
        [some subclasses should override this, especially Group]
        """
        return []
    
    def openable(self):
        """Say whether tree widgets should permit the user to open/close their view
        of this node (typically by displaying some sort of toggle icon for that state).
        (Note, if this is True then this does not specify whether the node view is
        initially open... #doc what does.)
        [Some subclasses should override this; if they add kids but don't
        override this, those kids will probably never be shown, but that might
        be undefined and depend on the model tree widget -- it's better to follow
        the rule of never having kids unless you are openable.]
        """
        # + If we decide this depends on the tree widget or on something about it,
        # we'll have to pass in some args... don't do that unless/until we need to.
        # + One reason we don't measure len(self.kids()) to decide on the default
        # value for this, is that some nodes might not want to compute self.kids()
        # until/unless it's needed, in case doing so is expensive. For example,
        # Qt's dirview example (also in PyQt examples3) computes kids only when
        # a node (representing a filesystem directory) is actually opened.
        return False

    ###e API and method/attr names related to "rename" needs review, since the text
    # shown by some nodes in a tree widget (in the future) might not be "their name".
    # [bruce 050128]
    
    def rename_enabled(self):
        """Should tree widgets permit the user to rename this node?
        (If so, they will call self.try_rename(newname) to actually request
        renaming for a specific new name.)
        [some subclasses should override this and/or try_rename]
        """
        return True

    def try_rename(self, name):
        """Given a new name for self, store it or reject it.
        Specifically, do one of these actions:
        - transform it into an acceptable name, store that in the node,
          do needed invals, and return (True, stored name);
        - or, reject it, and return (False, reason it's not ok).
          (The reason should be a string suitable for error messages.)
        """
        if not self.rename_enabled():
            return (False, "renaming this node is not permitted")
        name = name.strip() # remove whitespace from both ends
        if not name:
            return (False, "blank name is not permitted")
        # accept the new name.
        self.name = name
        if self.assy:
            self.assy.changed()
        ###e should inval any observers (i.e. model tree) -- not yet needed, I think [bruce 050119]
        return (True, name)
        
    def drag_move_ok(self): # renamed/split from drag_enabled; docstring revised 050201 #####@@@@@ honor it!
        """Say whether a drag_move which includes this node can be started (for "drag and drop").
        It's ok if only some drop-targets (nodes or inter-node gaps) can accept this node;
        we'll ask the targets if they'll take a specific drag_moved list of nodes (which includes this node).
           A tree widget asked to drag_move some selected nodes might filter them by drag_move_ok
        to get the ones to actually move, or it might refuse the whole operation unless all are ok to move --
        that's a UI decision, not a node semantics decision.
        [some subclasses should override this]
        """
        return True
        
    def drag_copy_ok(self): # renamed/split from drag_enabled; docstring revised 050201 #####@@@@@ honor it!
        """Say whether a drag_copy which includes this node can be started (for "drag and drop").
        Same comments as for drag_move_ok apply.
        [some subclasses should override this]
        """
        return True
    
    def drop_on_ok(self, drag_type, nodes):
        """Say whether "drag and drop" can drop the given set of nodes onto this node,
        when they are dragged in the given way ('move' or 'copy' -- nodes arg has the originals).
        (Typically this node (if it says ok) would insert the moved or copied nodes inside itself
        as new members, but what it actually does with them is up to it;
        as an initial kluge before we support dropping into gaps (if we ever don't),
        dropping onto a leaf node might simulate dropping into the same-level gap below it
        (i.e. make a sibling, like addmember does).
        [some subclasses should override this]
        """
        #bruce 050216 add exception for cycle-forming request ###@@@ needs testing
        # (to fix bug 360 item 6 comment 9, which had been fixed in the old MT's DND code too)
        if drag_type == 'move':
            for node in nodes:
                if (node != self and node.is_ascendant(self)) or (node == self and node.is_group()):
                    print "fyi: refusing drag-move since it would form a cycle"
                        #e should change retval-spec and get this into a redmsg
                    return False
        return True #e probably change to False for leaf nodes, once we support dropping into gaps

    def drop_on(self, drag_type, nodes): ###@@@ needs a big cleanup
        """After a "drag and drop" of type 'move' or 'copy' (according to drag_type),
        perform the drop of the given list of nodes onto this node.
        Exactly how to do this depends on whether this node is a leaf or group;
        subclasses can override this to change the UI behavior.
        (As of 050307, only the Clipboard override this.)
        Return value: if this operation creates new nodes
        (normal for copy, but also happens in some cases for move),
        return them in a list; otherwise return [].
        """
        #e rewrite to use copy_nodes (nim)? (also rewrite the assy methods? not for alpha)
        res = [] #bruce 050203: return any new nodes this creates (toplevel nodes only, for copied groups)
        #bruce 050216: order is correct if you're dropping on a group, but (for the ops used below)
        # wrong if you're dropping on a node. This needs a big cleanup, but for now, use this kluge:
        if not isinstance(self, Group):
            nodes = nodes[::-1] # reverse order if self is a leaf node
        if drag_type == 'move':
            for node in nodes[:]:
                node.moveto(self) ###k guess/stub; works
        else:
            for node in nodes[:]:
                nc = node.copy(None) # note: before 050215 we passed dad=self -- weird, but due to other weirdness in copy, didn't matter
                if nc: # can be None if the copy is refused (since nim for that Node subclass, as for Group as of 050203)
                    res.append(nc)
                    self.addmember(nc) # self is sometimes a Group, so this does need to be addmember (not addchild or addsibling)
        #bruce 050308 quick inefficient fix for assy/part split... ####@@@@ review for optimization
        self.assy.update_parts()
##        #bruce 050203: adding a quick bugfix for clipboard-DND bugs
##        # which was written 050202 and intended for Alpha-1, but didn't make it in.
##        # In the future this might be optimized to only call update_mols when necessary,
##        # and/or some of what update_mols does might be done more incrementally and more generally.
##        self.assy.update_mols()
##        #end bruce 050203 addition
        return res

    #bruce 050203: these drop_unders were not used for Alpha-1 -- no time to support dropping into gaps.
    # (they are not yet fully implemented, either.)

    def drop_under_ok(self, drag_type, nodes, after = None): #####@@@@@ honor it!
        """Say whether it's ok to drag these nodes (using drag_type)
        into a child-position under self,
        either after the given child 'after'
        or (by default) as the new first child.
           Tree widgets can use this to offer drop-points shown in gaps
        between existing adjacent nodes.
        [some subclasses should override this]
        """
        return hasattr(self, 'addchild') # i.e. whether it's a Group!

    def drop_under(self, drag_type, nodes, after = None): #e move to Group, implem subrs, use #####@@@@@
        "#doc"
        if drag_type == 'copy':
            nodes = copy_nodes(nodes) # make a homeless copy of the set (someday preserving inter-node bonds, etc) #####@@@@@ IMPLEM
        for node in nodes:
            self.addchildren(nodes, after = after) #####@@@@@ IMPLEM (and make it not matter if they are homeless? for addchild)
        return

    def node_icon(self, display_prefs):
        """#doc this
        [all Node subclasses should override this]
        """
        msg = "bug - Node subclass %s forgot to override node_icon method" % self.__class__.__name__
        fake_filename = msg
        return imagename_to_pixmap( fake_filename)
            # should print msg, at most once per class
            # (some people might consider this a kluge)
    
    # most methods before this are by bruce [050108 or later] and should be reviewed when my rewrite is done ###@@@

    def addsibling(self, node, before = False):
        """Add the given node after (default) or before self, in self's Group.
        Node should not already be in any Group, since it is not removed from one.
        (Some existing code violates this; this is probably ok if node's old Group
        is never again used, but that practice should be deprecated, and then
        this method should detect the error of node.dad already being set,
        or perhaps be extended to remove node from its dad.)
        [Special case: legal and no effect if node == self. But this should be
        made into an error, since it violates the rule that node is not presently
        in any Group!]
        [It is unlikely that any subclass should override this, since its
        semantics should not depend on anything about self, only (perhaps)
        on things about its Group, i.e. self.dad.]
        [Before bruce 050113 this was called Node.addmember, but it had different
        semantics from Group.addmember, so I split that into two methods.]
        """
        if node == self:
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
        """[Deprecated public method:]
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
        if isinstance(self, Group):
            # (use isinstance (rather than overriding in a subclass)
            #  to emphasize the reason this method needs to be deprecated!)
            self.addchild( node, top = before_or_top)
        else:
            # for a leaf node, add it to the dad node just after us
            self.addsibling( node, before = before_or_top)
        return
        
    def pick(self):
        """select the object
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        ###@@@ I don't know whether that new rule is yet followed by external code [bruce 050124].
        #bruce 050131 for Alpha: I tried to make sure it is; at least it's now followed in "pick" methods.
        if not self.picked:
            self.picked = True
            # bruce 050125: should we also call self.assy.permit_picked_parts() here? ###@@@ [not just in chunk.pick]
            #bruce 050131 for Alpha: I'm guessing we don't need to, for jigs or groups,
            # since they don't get into assy.molecules or selmols.
            # Whether doing it anyway would be good or bad, I don't know,
            # so no change for now.
            self.change_current_selgroup_to_include_self()
                # note: stops at a picked dad, so should be fast enough during recursive use
        # we no longer call mode.UpdateDashboard() from here;
        # clipboard selection no longer affects Build mode dashboard. [bruce 050124]

    def unpick(self):
        """unselect the object, and all its ancestor nodes.
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        ###@@@ I don't know whether that new rule is yet followed by external code [bruce 050124].
        if self.picked:
            self.picked = False
        # bruce 050126 change: also set *all its ancestors* to be unpicked.
        # this is required to strictly enforce the rule
        # "selected groupnode implies all selected members".
        # We'd do this inside the 'if' -- but only once we're sure all other code
        # no longer bypasses this method and sets node.picked = False directly;
        # this way, if that happens, we might happen to fix up the situation later.
        if self.dad and self.dad.picked:
            self.dad.unpick_top() # use the method, in case a Group subclass overrides it

    def unpick_all_except(self, node):
        """unpick all of self and its subtree except whatever is inside node and its subtree;
        return value says whether anything was actually unpicked
        """
        # this implem should work for Groups too, since self.unpick does.
        if self == node:
            return False
        res = self.picked # since no retval from unpick_top; this is a correct one if our invariants are always true
        self.unpick_top()
        res2 = self.unpick_all_members_except( node)
        # btw, during recursive use of this method,
        # unpick_top (either the Node or Group implem)
        # will see self.dad is not picked
        # and not need to keep calling unpick_top
        return res or res2

    def unpick_all_members_except(self, node):
        "[#doc; overridden in Group] return value says whether anything was actually unpicked"
        return False
    
    def pick_top(self): #bruce 050124
        #e ###@@@ needs fixing or zapping, because:
        # as of 050131, this is: illegal (since it violates an invariant),
        # incorrectly implemented (since it doesn't do leaf-specific pick funcs,
        # though this could probably be easily fixed just as I'll fix unpick_top),
        # and never called (since sole caller's group_select_kids is always True).
        """select the object -- but (unlike Group.pick) don't change selection state
        of its members. Note that this violates the principle "selected groupnode
        implies all selected members". This means it should be used either never
        or rarely (as of 050126 I don't know which).
        [unlike pick, this is generally NOT extended in subclasses]
        """
        Node.pick(self)

    def unpick_top(self): #bruce 050124 #bruce 050131 making it correct for chunk and jig
        """unselect the object -- but (unlike Group.unpick) don't change
        the selection state of its members. But do unselect all its ancestor nodes.
        [unlike unpick, this is generally NOT extended in subclasses, except in Group.]
        """
        # this implem is only correct for leaf nodes:
        self.unpick() # before 050131 was Node.unpick(self), which was wrong for chunk and jig.

    _old_dad = None ###k not yet used? #####@@@@@ review got to here, except: to chgdad added only cmts plus docstring plus new name

    def in_clipboard(self): #bruce 050205 temporary ###@@@ [should use a more general concept of assy.space]
        """For a leaf node: Are we definitely inside some clipboard item?
        For a Group node: Would new members added to us be, or be inside, a clipboard item?
        (I.e., in both cases, are we the Clipboard or in its tree?)
        [This only works as long as self.assy.shelf is the Clipboard and works like it does now, 050205.
         It's only useful as long as the rest of the code has special cases for clipboard vs main part --
         hopefully not for much longer. In other words, this method is "deprecated at birth".]
        """
        try:
            return self.assy.shelf.is_ascendant(self)
        except:
            return False # assume not, if e.g. we have no assy, it has no shelf, etc
    
    def changed_dad(self):
        """[private method]
        Must be called after self.dad might have changed, before again exposing
        modified node to the public. Keeps some things up to date continuously;
        records info to permit updating other things later.
        """
        node = self
        ## not needed as of 050309:
        ## changed.dads.record(node) # make sure node's Part will be updated later if needed [bruce 050303]
        assert node.dad #k not sure if good to need this, but seems to fit existing calls... that might change [050205 comment]
            #e if no dad: assy, space, selgroup is None.... or maybe keep prior ones around until new real dad, not sure
        assert node.assy == node.dad.assy or node.assy == None
            # bruce 050308, since following assy code & part code has no provision yet for coexisting assemblies
        node.assy = node.dad.assy # this might change soon, or might not... but if it's valid at all, it needs to be propogated down!
            # we leave it like this for now only in case it's ever being used to init the assy field from None.
        #bruce 050308: continually let assigned node.dad.part get inherited by unassigned node.part (recursively)
        if node.dad.part and not node.part:
            # note, this is the usual way that newly made nodes acquire their .part for the first time!
            # they might be this node or one of its kids (if they were added to a homeless Group, which is this node).
            node.inherit_part(node.dad.part) # recurses only into kids with no .parts
        if node.picked:
            # bruce 050131 for Alpha:
            # worry about whether node is in a different selection group than before;
            # don't know if this ever happens, but let's try to cooperate if it does:
            node.change_current_selgroup_to_include_self()
                # note: this has no effect if node doesn't have a selgroup
        if node.dad.picked:
            node.pick() #bruce 050126 - maintain the new invariant! (two methods need this)
            # warning: this might make some callers need to update glpane who didn't need to before.
            # possible bugs from this are not yet analyzed.
            # Note 050206: the clipboard can't be selected, and if it could be, our invariants would be inconsistent
            # if it had more than one item! (Since all items would be selected but only one selgroup should be.)
            # So, this line never picks a clipboard item as a whole.
        return

    def inherit_part(self, part): #bruce 050308
        "#doc [overridden in Group]"
        assert not self.part
        part.add(self)
        assert self.part == part # correct only for leaf nodes
    
    def changed_dad_comments(): "never called, just some semi-obs comments I need here for awhile"
        # new features 050205 for Alpha (to help fix DND/clipboard bugs):
        # Figure out whether our molecules need to be added to / removed from assy.molecules,
        # or more generally (someday), whether we exited and/or entered a "space"
        # which wants to keep track of what's inside it (etc).

        # Did we leave assy.tree? Let's assume we were in it if _old_dad was None ... what maintains assy.molecules now?
        # assy.__init__ sets to []
        # assy.addmol "add a chunk to assy" - adds to .mols and does other things
        ##### *including tree.addmember* so what if already added elsewhere? ####@@@@ review for possible bugs in calls of that
        # - it's called in a few special places that make mols when operating on selected stuff!
        # - in files_mmp: assy.addmol(mol); mol.moveto(group) -- this might solve the issues about addmol vs groups.
        # - ...
        # (when they don't have a group to put them in)
        # bugs if sel in clipboard.... #fix later.. just make those ops deselect clipboard... for beta work in proper space...
        #  tho if we only do .mols that is better than nothing ie a true partial bugfix.
        # sanitize_for_clipboard_0
        # chunk's mol.kill [so i reviewed it now, revised its debug code]
        # ... this is all, so DND into group in tree must now ... only work if you were already in tree, since no addmol.
        # ... and addmol is not good for adding things to assy... but some of it is needed (more than just .molecules), in theory...

        # ... I ended up not yet supporting this in changed_dad, but just having some or all DND moves call assy.update_mols!
        # Maybe I'll make assy methods cut/copy/delete_sel do this too, not sure.

        # end of bruce new features 050205 for Alpha
        # [they are all comments! well, those are useful too... and less likely to cause new bugs (soon anyway) than actual code!]
    
    def hide(self):
        self.hidden = True
        self.unpick()
        
    def unhide(self):
        self.hidden = False

    def apply2all(self, fn):
        """Apply fn to self and (as overridden in Group) all its members;
        see Group.apply2all docstring for details.
        """
        fn(self)

    def apply2tree(self, fn): ###@@@ should rename (both defs)
        """Like apply2all, but only applies fn to all Group nodes (at or under self)."""
        pass

    def apply2picked(self, fn):
        """Apply fn to the topmost picked nodes under (or equal to) self,
        but don't scan below picked nodes. See Group.apply2picked docstring for details.
        """
        if self.picked: fn(self)

    def hindmost(self):
        """[docstring is meant for both Node and Group methods taken together:]
        Thinking of nodes as subtrees of the model tree, return the smallest
        subtree of self which contains all picked nodes in this subtree, or None
        if there are no picked nodes in this subtree. Note that the result does
        not depend on the order of traversal of the members of a Group.
        """
        if self.picked: 
            return self
        return None

    def ungroup(self):
        """If this Node is a Group, dissolve it, letting its members
        join its dad, if this is possible and if it's permitted as a
        user-requested operation. See our Group implem for details.
        """
        #bruce 050121 inferred docstring from 2 implems and 1 call
        return

    def kill(self):
        ###@@@ bruce 050214 changes and comments:
        #e needs docstring;
        #  as of now, intended to be called at end (not start middle or never) of all subclass kill methods
        #  ok to call twice on a node (i.e. to call on an already-killed node); subclass methods should preserve this property
        # added condition on self.dad existing, before delmember
        # added unpick (*after* dad.delmember)
        # added self.assy = None
        # also modified the Group.kill method, which extends this method
        if self.part: #bruce 050303
            self.part.remove(self)
        if self.dad:
            self.dad.delmember(self)
                # this does assy.changed (if assy), dad = None, and unpick,
                # but the unpick might be removed someday, so we do it below too
                # [bruce 050214]
        self.unpick() # must come after delmember (else would unpick dad) and before forgetting self.assy
        self.assy = None #bruce 050214 added this ###k review more

    def is_ascendant(self, node): # implem corrected by bruce 050121; was "return None"
        """Is node in the subtree of nodes headed by self?
        [Optimization of Group.is_ascendant for leaf nodes; see its docstring for more info.]
        """
        return self == node # only correct for self being a leaf node

    def moveto(self, node, before=False): #e should be renamed for d&d, and cleaned up; has several external calls
        """Move self to a new location in the model tree, before or after node,
        or if node is a Group, somewhere inside it (reinterpreting 'before' flag
        as 'top' flag, to decide where inside it). Special case: if self == node,
        return with no effect (even if node is a Group).
        """
        #bruce 050110 updated docstring to fit current code.
        # (Note that this makes it even more clear, beyond what's said in addmember
        #  docstrings, that addmember interface mixes two things that ought to be
        #  separated.)
        
        #bruce 050205 change: just go directly to addmember, after my addchild upgrades today.
        # note, this 'before' is a positional arg for the before_or_top flag,
        # not the named arg 'before' of addchild! Btw we *do* need to call addmember
        # (with its dual personality dependending on node being leaf or not)
        # for now, while DND uses drop_on groups to mean drop_under them.
        node.addmember(self, before_or_top = before) # this needs to be addmember, not addchild or addsibling

    def nodespicked(self):
        """Return the number of nodes currently selected in this subtree.
        [subclasses must override this!]
        Warning (about current subclass implementations [050113]):
        scans the entire tree... calling this on every node in the tree
        might be slow (every node scanned as many times as it is deep in the tree).
        """
        if self.picked:
            return 1 # number, not boolean!
        else:
            return 0

    def edit(self): #e should be renamed to edit_props (in several files)
        """[should be overridden in most subclasses]
        If this kind of Node has properties that can be edited
        with some sort of interactive dialog, do that
        (put up the dialog, wait for user to dismiss it, change the properties
        as requested, and do all needed invals or updates),
        and then return None (regardless of Cancel, Apply, Revert, etc).
           If this kind of Node *doesn't* support editing of properties,
        return a suitable text string for use in an error message.
        """
        # bruce 050121 inferred docstring from all 7 implems and 1 call.
        # Also added feature of refusing and returning error message, used in 2 implems so far.
        return "Nodes of class %s don't provide a property-editing dialog." % self.__class__.__name__

    def edit_props_enabled(self): #bruce 050121 added this feature
        """Subclasses should override this and make it return False
        if their edit method would refuse to put up an editing dialog.
        """
        # i don't know if they all do that yet...
        #e should we check here to see if they override Node.edit?? nah.
        return True # wrong for an abstract Node, but there is no such thing!
    
    def dumptree(self, depth=0):
        print depth*"...", self.name

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """Write this Node to an mmp file, as controlled by mapping,
        which should be an instance of files_mmp.writemmp_mapping.
        [subclasses must override this to be written into an mmp file;
         we print a debug warning if they don't.]
        """
        # bruce 050322 revising this; this implem used to be the normal way
        # to write Jigs; now it's basically an error to call this implem,
        # but it's harmless -- it puts a comment in the mmp file and prints a debug warning.
        line = "# not yet implemented: mmp record for %r" % self.__class__.__name__
        mapping.write(line + '\n')
        if platform.atom_debug:
            print "atom_debug:", line
        return
        ## old code, now cleaned up and turned into Jig.writemmp:
##        # bruce comment 050108/050210: this is used for Jigs. It uses __repr__ nonstandardly!
##        f.write(self.__repr__(atnums))
        
#    def writemdl(self, alist, f, dispdef):
#        pass

    def writepov(self, file, dispdef): #bruce 050208 added Node default method
        pass

    def draw(self, o, dispdef):
        pass
        
    def getinfo(self):
        pass

    def getstatistics(self, stats):
        pass

    def break_interpart_bonds(self): #bruce 050308 for assy/part split, and to fix bug 371 and related bugs for Jigs
        """Break all bonds (atom-atom or atom-Jig or (in future) anything similar)
        between this node and other nodes in a different Part.
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
        [As of 030508, this is overridden only in class molecule and
         class Jig and/or its subclasses.]
        """#####@@@@@doit in molecule and Jig and subclasses
        pass

    # end of class Node

    
    #in addition, each Node should have the following methods:
    # draw, cut, copy, paste


class Group(Node):
    """The tree node class for the tree.
    Its members can be Groups, jigs, or molecules.
    """
    
    def __init__(self, name, assy,  dad, list = []): ###@@@ review inconsistent arg order
        self.members = [] # must come before Node.__init__ [bruce 050316]
        self.__cmfuncs = [] # funcs to call right after the next time self.members is changed
        Node.__init__(self, assy, name, dad)
        self.open = True
        for ob in list: self.addchild(ob)

    def is_group(self):
        """[overrides Node method; see its docstring]"""
        return True
    
    def drag_move_ok(self): return True # same as for Node
    def drag_copy_ok(self): return True # for my testing... maybe make it False for Alpha though ###e ####@@@@ 050201
    def is_selection_group_container(self): #bruce 050131 for Alpha
        """Whether this group causes each of its direct members to be treated
        as a "selection group" (see another docstring for what that means,
        but note that it can be true of leaf nodes too, in spite of the name).
        [Intended to be overridden only by the Clipboard.]
        """
        return False # for most groups

    def haspicked(self): # bruce 050126
        """Whether node's subtree has any picked members.
        [See comments in Node.haspicked docstring.]
        """
        if self.picked: return True
        for m in self.members:
            if m.haspicked(): return True
        return False
    
    def changed_members(self): #bruce 050121 new feature, now needed by depositMode
        """Whenever something changes self.members in any way (insert, delete, reorder),
        it MUST call this method to inform us (but only *after* it makes the change);
        we'll inform other interested parties, if any.
        (To tell us you're an interested party, use call_after_next_changed_members.)
           Notes: This need not be called after changes in membership *within* our members,
        only after direct changes to our members list. Our members list is public, but
        whether it's incrementally changed (the same mutable list object) or replaced is
        not defined (and for whatever wants to change it, either one is acceptable).
        It is deprecated for anything other than a Group (or subclass) method to directly
        change self.members, but if it does, calling this immediately afterwards is required.
        [As of 050121 I don't know for sure if all code yet follows this rule, but I think it does. ##k]
        """
        if self.part:
            self.part.changed() # does assy.changed too
        elif self.assy:
            self.assy.changed()
            # it is ok for something in part.changed() or assy.changed() to modify self.__cmfuncs
        cm = self.__cmfuncs
        if cm:
            self.__cmfuncs = [] # must do this first in case func appends to it
            for func in cm:
                try:
                    func(self)
                        # pass self, in case it's different from the object
                        # they subscribed to (due to kluge_change_class)
                except:
                    print_compact_traceback("error in some cmfunc, ignored by %r: " % self)
        return

    def call_after_next_changed_members(self, func, only_if_new = False):
        """Call func once, right after the next time anything changes self.members.
        At that time, pass it one argument, self; ignore its retval; print error message
        (in debug version only) if it has exceptions.
           If our members are taken over by another Group instance (see kluge_change_class),
        then it, not us, will call func and be the argument passed to func.
           Typically, func should be an "invalidation function", recording the need to
        update something; when that update later occurs, it uses self.members and again
        supplies a func to this method. (If every call of func did an update and gave us
        a new func to record, this might be inefficient when self.members is changed many
        times in a row; nevertheless this is explicitly permitted, which means that we
        explicitly permit func, when called from our code, to itself call this method,
        supplying either the same func or a new one.)
        """
        if only_if_new and (func in self.__cmfuncs):
            return
        self.__cmfuncs.append( func) # might occur during use of same func!
    
    def openable(self): # overrides Node.openable()
        "whether tree widgets should permit the user to open/close their view of this node"
        # if we decide this depends on the tree widget or on something about it,
        # we'll have to pass in some args... don't do that unless/until we need to.
        return True

## no need for this, can be same as what we inherit
##    def rename_enabled(self):
##        "whether tree widgets should permit the user to rename this node"
##        rename = True # true for most Groups
##        ###@@@ these kluges (taken from the deprecated self.buildNode) should be replaced by new subclasses of Group
##        if self.name == "Clipboard": rename = False # Do not allow the clipboard to be renamed
##        if self.name == self.assy.name: rename = False # Do not allow the part node to be renamed
##        return rename

## no need for these, same as what we inherit; but we might generalize them to give info about what types can be dragged or dropped
##    def drag_enabled(self): # something related to drag and drop, drag aspect ###k what exactly?
##        return True
##    
##    def drop_enabled(self): # something related to drag and drop, drop aspect ###k what exactly?
##        return True

    # methods before this are by bruce 050108 and should be reviewed when my rewrite is done ###@@@

    def kluge_change_class(self, subclass):
        #bruce 050109 ###@@@ temporary [until files_mmp & assy make this kind of assy.root, shelf, tree on their own]
        """Return a new Group with this one's members but of the specified subclass
        (and otherwise just like this Group, which must be in class Group itself,
        not a subclass). This won't be needed once class assembly is fixed to make
        the proper subclasses directly.
        """
        assert self.__class__ == Group
        new = subclass(self.name, self.assy, self.dad) # no members yet
        assert isinstance(new, Group) # (but usually it's also some subclass of Group, unlike self)
        if self.dad:
            # don't use addmember, it tells the assy it changed
            # (and doesn't add new in right place either) --
            # just directly patch dad's members list to replace self with new
            ind = self.dad.members.index(self)
            self.dad.members[ind] = new
                # don't tell dad its members changed, until new is finished (below)
            self.dad = None # still available in new.dad if we need it
        new.members = self.members # let new steal our members directly
        new.__cmfuncs = self.__cmfuncs # and take responsibility for our members changing...
        self.__cmfuncs = []
        # self should no longer be used; enforce this
        self.members = 333 # not a sequence
        self.node_icon = "<bug if this is called>"
        for mem in new.members:
            mem.dad = new
            # bruce 050205:
            # should we now call mem.changed_dad()? reasons yes: new's new class might differ in rules for selgroup or space
            # (e.g. be the top of a selgroup) and change_dad might be noticing and responding to that change,
            # so this might turn out to be required if something has cached that info in mem already.
            # reasons no: ... some vague uneasiness. Oh, it might falsely tell assy it changed, but I think our caller
            # handles that. So yes wins, unless bugs show up!
            # BUT: don't do this until we're all done (so new is entirely valid).
            ## mem.changed_dad()
        for attr in ['open','hidden','picked']:
            # not name, assy, dad (done in init or above), selgroup, space (done in changed_dad)
            try:
                val = getattr(self, attr)
            except AttributeError:
                pass # .open will go away soon;
                # others are probably always defined but I'm not sure
                # (and should not care here, as long as I get them all)
            else:
                setattr(new, attr, val)
        for mem in new.members:
            mem.changed_dad() # reason is explained above [bruce 050205]
        new.dad.changed_members() # since new class is different from self.class, this might be needed ###@@@ is it ok?
        return new

# bruce 050108 removed all uses of setopen, since it should be defined
# on tree items, not nodes        
##    def setopen(self):
##        self.open = True

    # bruce 050113 deprecated addmember and confined it to Node; see its docstring.

    def addchild(self, newchild, _guard_ = 050201, top = False, after = None, before = None): # [renamed from addmember - bruce 050113]
        """Add the given node, newchild, to the end (aka. bottom) of this Group's members list,
        or to the specified place (top aka. beginning, or after some child or index,
        or before some child or index) if one of the named arguments is given.
        Ok even if newchild is already a member of self, in same or different
        location than requested (it will be moved), or a member of some other Group
        (it will be removed). (Behavior with more than one named argument is undefined.)
           Note: the existence of this method (as an attribute) might be used as a check
        for whether a Node can be treated like a Group [as of 050201].
           Special case: legal and no effect if newchild is None or 0 (or anything false);
        this turns out to be needed by assy.copy_sel/Group.copy or Jig.copy! [050131 comment]
        [Warning (from when this was called addmember):
         semantics (place of insertion, and optional arg name/meaning)
         are not consistent with Node.addmember; see my comments in its docstring.
         -- bruce 050110]
        [note, 050315: during low-level node-tree methods like addchild and delmember,
         and also during pick and unpick methods,
         there is no guarantee that the Part structure of our assy's node tree is correct,
         so checkparts should not be called, and assy.part should not be asked for;
         in general, these methods might need to know that each node has a part (perhaps None),
         but they should treat the mapping from nodes to parts as completely arbitrary,
         except for calling inherit_part to help maintain it.]
        """
        #bruce 050110/050206 updated docstring based on current code
        # Note: Lots of changes implemented at home 050201-050202 but not committed until
        # 050206 (after Alpha out); most dates 050201-050202 below are date of change at home.
        #bruce 050201 added _guard_, after, before
        assert _guard_ == 050201
        if not newchild:
            #bruce 050201 comment: sometimes newchild was the number 0,
            # since Group.copy returned that as a failure code!!!
            # Or it can be None (Jig.copy, or Group.copy after I changed it).
            return

        #bruce 050205:
        # adding several safety checks (and related new feature of auto-delmember)
        # for help with MT DND; they're a good idea anyway.
        # See also today's changes to changed_dad().
        if newchild.dad and not (newchild in newchild.dad.members):
            # This is really a bug or a very deprecated behavior, but we tolerate it for now.
            # Details: some node-creating methods like molecule.copy and/or Group.copy
            # have the unpleasant habit of setting dad in the newly made node
            # without telling the dad! This almost certainly means the other
            # dad-related aspects of the node are wrong... probably best to just pretend
            # those methods never did that. Soon after Alpha we should fix them all and then
            # make this a detected error and no longer tolerate it.
            if platform.atom_debug:
                msg = "atom_debug: addchild setting newchild.dad to None since newchild not in dad's members: %s, %s" % (self,newchild)
                print_compact_stack(msg)
            newchild.dad = None
        if newchild.is_ascendant(self):
            #bruce 050205 adding this for safety (should prevent DND-move cycles as a last resort, tho might lose moved nodes)
            if platform.atom_debug:
                # this msg covers newchild==self too since that's a length-1 cycle
                print "atom_debug: addchild refusing to form a cycle, doing nothing; this indicates a bug in the caller:",self,newchild
            return
        if newchild.dad:
            # first cleanly remove newchild from its prior home.
            # (Callers not liking this can set newchild.dad = None before calling us.
            #  But doing so (or not liking this) is deprecated.)
            if newchild.dad == self:
                # this might be wanted (as a way of moving a node within self.members)
                # (and a caller might request it by accident when moving a node from a general position,
                #  so we want to cooperate), but the general-case code won't work
                # if the before or after options were used, whether as nodes (if the node used as a marker is newchild itself)
                # or as indices (since removal of newchild will change indices of subsequent nodes).
                # So instead, if those options were used, we fix them to work.
                # We print a debug msg just as fyi; that can be removed once this is stable and tested.
                if platform.atom_debug and 0:
                    # i'll remove this msg soon after i first see it.
                    print "atom_debug: fyi: addchild asked to move newchild within self.members, might need special cases",self,newchild
                    print "...options: top = %r, after = %r, before = %r" % (top , after , before)
                if type(before) == type(1):
                     # indices will change, use real nodes instead
                     # (ok even if real node is 'newchild'! we detect that below)
                    before = self.members[before]
                if type(after) == type(1):
                    after = self.members[after]
                if before == newchild or after == newchild:
                    # this is a noop, and it's basically a valid request, so just do it now (i.e. return immediately);
                    # note that general-case code would fail since these desired-position-markers
                    # would be gone once we remove newchild from self.members.
                    return
                # otherwise (after our fixes above) the general-case code should be ok.
                # Fall thru to removing newchild from prior home (in this case, self),
                # before re-adding it in a new place.
            # remove newchild from its prior home (which may or may not be self):
            newchild.dad.delmember(newchild) # this sets newchild.dad to None, but doesn't mess with its .part, .assy, etc
        # Only now will we actually insert newchild into self.
        # [end of this part of bruce 050205 changes]
        
        ## self.assy.changed() # now done by changed_members below
            #e (and what about informing the model tree, if it's displaying us?
            #   probably we need some subscription-to-changes or modtime system...)
        if top:
            self.members.insert(0, newchild) # Insert newchild at the very top
        elif after != None: # 0 has different meaning than None!
            if type(after) != type(0):
                after = self.members.index(after) # raises ValueError if not found, that's fine
            if after == -1:
                self.members += [newchild] # Add newchild to the bottom (.insert at -1+1 doesn't do what we want for this case)
            else:
                self.members.insert(after+1, newchild) # Insert newchild after the given position #k does this work for negative indices?
        elif before != None:
            if type(before) != type(0):
                before = self.members.index(before) # raises ValueError if not found, that's fine
            self.members.insert(before, newchild) # Insert newchild before the given position #k does this work for negative indices?
        else:
            self.members.append(newchild) # Add newchild to the bottom, i.e. end (default case)
        newchild.dad = self
        newchild.changed_dad()
        newchild.dad.changed_members() # must be done *after* they change and *after* changed_dad has made them acceptable for new dad
        # note: if we moved newchild from one place to another in self,
        # changed_members is called twice, once after deletion and once after re-insertion.
        # probably ok, but I should #doc this in the related subscriber funcs
        # so callers are aware of it. [bruce 050205]
        return

    def delmember(self, obj):
        if obj.dad != self: # bruce 050205 new feature -- check for this (but do nothing about it)
            if platform.atom_debug:
                print_compact_stack( "atom_debug: fyi: delmember finds obj.dad != self: ") #k does this ever happen?
        obj.unpick() #bruce 041029 fix bug 145 [callers should not depend on this happening! see below]
            #k [bruce 050202 comment, added 050205]: review this unpick again sometime, esp re DND drag_move
            # (it might be more relevant for addchild than for here; more likely it should be made not needed by callers)
            # [bruce 050203 review: still needed, to keep killed obj out of selmols,
            #  unless we revise things enough to let us invalidate selmols here, or the like;
            #  and [050206] we should, since this side effect is sometimes bad
            #  (though I forget which recent case of it bugged me a lot).]
        ## self.assy.changed() # now done by changed_members below
        try:
            self.members.remove(obj)
        except:
            # relying on this being permitted is deprecated [bruce 050121]
            if platform.atom_debug:
                print_compact_stack( "atom_debug: fyi: delmember finds obj not in members list: ") #k does this ever happen?
            return
        obj.dad = None # bruce 050205 new feature
        self.changed_members() # must be done *after* they change
        return

    def pick(self):
        """select the Group -- and all its members! [see also pick_top]
        [overrides Node.pick]
        """
        Node.pick(self)
            # bruce 050131 comment: important for speed to do Node.pick first,
            # so ob.pick() sees it's picked when its subr scans up the tree
        for ob in self.members:
            ob.pick()
        # bruce 050131 comment:
        # I'm very skeptical of doing this history.message
        # recursively, but I'm not changing it for Alpha
        msg = self.description_for_history() # bruce 050121 let subclass decide on this
##        if self.name == self.assy.name: msg = "Part Name: [" + self.name +"]"
##        elif self.name == "Clipboard": msg = "Clipboard"
##        else: msg = "Group Name: [" + self.name +"]"
        self.assy.w.history.message( msg )
        return

    def description_for_history(self):
        """Return something to print in the history whenever we are selected
        [some subclasses should override this]
        """
        return "Group Name: [" + self.name +"]"
    
    def unpick(self):
        """unselect the Group -- and all its members! [see also unpick_top]
        """
        Node.unpick(self)
        for ob in self.members:
            ob.unpick()

    def unpick_top(self): #bruce 050131 for Alpha: bugfix
        "[Group implem -- go up but don't go down]" #redoc, and clean it all up
        Node.unpick(self)

    def unpick_all_members_except(self, node): #bruce 050131 for Alpha
        "[private method; #doc; overrides Node method]"
        #e should probably inline into unpick_all_except and split that for Node/Group
        res = False
        for ob in self.members:
            res1 = ob.unpick_all_except( node)
            res = res or res1
            # note: the above is *not* equivalent (in side effects)
            # to res = res or ob.unpick_all_except( node)!
        return res

    def inherit_part(self, part): #bruce 050308
        "#doc [overrides Node method]"
        Node.inherit_part(self, part)
        for m in self.members:
            if not m.part:
                m.inherit_part(part)
        return

    def hide(self):
        for ob in self.members:
            ob.hide()

    def unhide(self):
        for ob in self.members:
            ob.unhide()
                
    def apply2all(self, fn):
        """Apply fn to self and (as overridden here in Group) all its members.
        It's safe for fn to modify self.members list (since we scan a copy),
        but if members of not-yet-scanned nodes are modified, that will affect
        what nodes are reached by our scan, since each nodes' members list is
        copied only when we reach it. For example, if fn moves a node to a later
        subtree, then the same apply2all scan will reach the same node again
        in its new position.
        """
        fn(self)
        for ob in self.members[:]:
            ob.apply2all(fn)

    def apply2tree(self, fn): #e rename?
        """Like apply2all, but only applies fn to all Group nodes (at or under self)."""
        fn(self)
        for ob in self.members[:]:
            ob.apply2tree(fn)
             
    def apply2picked(self, fn):
        """Apply fn to the topmost picked nodes under (or equal to) self.
        That is, scan the tree of self and its members (to all levels including leaf nodes),
        applying fn to all picked nodes seen, but not scanning into the members of picked nodes.
        Thus, for any node, fn is never applied to both that node and any of its ancestors.
        For effect of fn modifying a members list, see comments in apply2all docstring.
        [An example of (i hope) a safe way of modifying it, as of 050121, is in Group.ungroup.]
        """
        if self.picked: fn(self)
        else:
            for ob in self.members[:]:
                ob.apply2picked(fn)

    def hindmost(self): ###@@@ should rename
        """[docstring is meant for both Node and Group methods taken together:]
        Thinking of nodes as subtrees of the model tree, return the smallest
        subtree of self which contains all picked nodes in this subtree, or None
        if there are no picked nodes in this subtree. Note that the result does
        not depend on the order of traversal of the members of a Group.
        """ #bruce 041208 added docstring, inferred from code
        if self.picked: return self
        node = None
        for x in self.members:
            h = x.hindmost()
            if node and h: return self
            node = node or h
        return node
 
    def permits_ungrouping(self): #bruce 050121
        """Should the user interface permit users to dissolve this Group
        using self.ungroup?
        [Some subclasses should override this.]
        """
        return True # yes, for normal groups.
    
    def ungroup(self):
        """If this Node is a Group, dissolve it, letting its members
        join its dad, if this is possible and if it's permitted as a
        user-requested operation. [bruce 050121 thinks this should be
        split into whether this is permitted, and doing it whether or
        not it's permitted; the present method is really a UI operation
        rather than a structural primitive.]
        [overrides Node.ungroup]
        """
        #bruce 050121 inferred docstring from 2 implems and 1 call
        #bruce 050121 revised: use permits_ungrouping;
        # add kids in place of self within dad (rather than at end)
        if self.dad and self.permits_ungrouping():
            ## if self.name == self.assy.name: return
            ## (that's now covered by permits_ungrouping)
            for x in self.members[:]:
                ## x.moveto(self.dad) #e should probably put them before self in there
                self.delmember(x)
                self.addsibling(x, before = True)
                    # put them before self, to preserve order [bruce 050126]
            self.kill()

##    #bruce 050131 implemented this since it seems safe now... ###@@@ test it
##    # but it's NOT YET USED -- it's replaced by the following older method
##    # which refuses to copy Groups, since it's past the Alpha new-feature deadline.
##    #bruce 050214 comment: this might be safe, but is not yet good enough,
##    # e.g. it doesn't handle bonds between copied chunks... probably better to redo all copying
##    # as a 2-pass algorithm, and until then, leave groups uncopyable.
##    def copy(self, dad):
##        assert 0, "this is not yet used!"
##        ###@@@ need to review all copy methods for inconsistent semantics
##        # (internal like mol.copy, or menu-event-handlers?)
##        if self.__class__ != Group:
##            return None
##        res = Group( self.name, self.assy, None) #e should we use chem.gensym(self.name)?
##            # dad None here, for Alpha, to work with assy.copy_sel as of 050131
##        for x in self.members:
##            res.addchild(x.copy(res))
##                # .copy doesn't do addchild itself, returns None for Jigs; addchild tolerates both offenses
##        return res

##    #bruce 050131 note: this older method intentionally replaces the previous copy method! (for Alpha)
    def copy(self, dad):
        ###@@@ need to review all copy methods for inconsistent semantics
        # (internal like mol.copy, or menu-event-handlers?)
        self.redmsg("Groups cannot yet be copied")
            ###@@@ should remove that limitation
        return None # bruce 050131 changed this from "return 0"
    
    def kill(self):
        #bruce 050214: called Node.kill instead of inlining it; enhanced Node.kill;
        # and fixed bug 381 by killing all members first.
        for m in self.members[:]:
            m.kill()
        Node.kill(self)

    def is_ascendant(self, node):
            #e rename nodetree_contains? is_ancestor? (tho true of self too)
            #e or just contains? (no, not obvious arg is a node)
        """[overrides Node.is_ascendant, which is a very special case of the same semantics]
        Returns True iff self is an ascendant of node,
        i.e. if the subtree of nodes headed by self contains node.
        (node must be a Node or None (for None we return False);
         thus it's legal to call this for node being any node's dad.)
        """
        while node:
            if node == self: return True
            node = node.dad
        return False
        
    def nodespicked(self):
        """Return the number of nodes currently selected in this subtree.
        [Overrides Node.nodespicked()]
        Warning (about current implementation [050113]):
        scans the entire tree... calling this on every node in the tree
        might be slow (every node scanned as many times as it is deep in the tree).
        """
        npick = Node.nodespicked(self)
            # bruce 050126 bugfix: was 0 (as if this was called leavespicked)
        for ob in self.members: 
            npick += ob.nodespicked()
        return npick
        
    def node_icon(self, display_prefs):
        open = display_prefs.get('open', False)
        if open:
            return imagename_to_pixmap("group-expanded.png")
        else:
            return imagename_to_pixmap("group-collapsed.png")

    def kids(self, display_prefs): #bruce 050109
        """[Overrides Node.kids()]
        Return the ordered list of our kids which should be displayed in a model
        tree widget which is using (for this node itself) the given display prefs
        (which might include the boolean pref 'open', default False, telling us
         whether the tree widget plans to show our kids or not).
        (Don't include inter-kid gaps for drag&drop explicitly; see another method
         for that. ###nim)
        Subclasses can override this; this version is valid for any Group whose .members
        don't need filtering or updating, or augmenting (like PartGroup does as of 050109).
         [Note that it is (probably) perfectly ok for subclasses to have a set of kids which is
        not related to their members, provided callers (tree widgets) never assume node.dad
        corresponds to the parent relation in their own tree of display items. I don't know
        how well the existing caller (modelTree.py) follows this so far. -- bruce 050113]
        """
        if not self.openable() or not display_prefs.get('open',False):
            ###@@@ I suspect this check should always be done in the tree widget,
            # so we don't have to do it in Group methods. [bruce 050113]
            return []
        # Historical note: self.members used to be stored in reversed order, but
        # Mark fixed that some time ago. Some callers in modelTree needed reversed
        # members list, after that, not because it was stored in reverse order as
        # it had been, but because modeltree methods added tree items in reverse
        # order (which I fixed yesterday).
        # [bruce 050110 inference from addmember implems/usage]
        return list(self.members)
    
    def edit(self):
        "[this is overridden in some subclasses of Group]"
        cntl = GroupProp(self) # Normal group prop
        cntl.exec_loop()
        self.assy.mt.mt_update()

    def dumptree(self, depth=0):
        print depth*"...", self.name
        for x in self.members:
            if x.dad != self: print "bad thread:", x, self, x.dad
            x.dumptree(depth+1)

    def draw(self, o, dispdef):
        if self.hidden: return
        for ob in self.members:
            ob.draw(o, dispdef)
            
    def getstatistics(self, stats):
        """add group to part stats
        """
        stats.ngroups += 1
        for ob in self.members:
            ob.getstatistics(stats)
  
    def writemmp(self, mapping): #bruce 050322 revised interface
        mapping.write("group (" + self.name + ")\n")
        for x in self.members:
            x.writemmp(mapping)
        mapping.write("egroup (" + self.name + ")\n")
        
    def writepov(self, f, dispdef):
        if self.hidden: return
        for x in self.members: x.writepov(f, dispdef)

    def writemdl(self, alist, f, dispdef):
        if self.hidden: return
        for x in self.members: x.writemdl(alist, f, dispdef)
            
    def __str__(self):
        return "<group " + self.name +">"

    pass # end of class Group


# everything below here is fairly specialized and probably belongs in other files.
# [bruce 050121 comment]


class DataNode(Node):
    "class for Csys and Datum nodes"
    ## def rename_enabled(self): return False
    ##   (removed by bruce 050127 -- this exception apparently no longer desired, at least for Csys)
    
    def drag_enabled(self): return False #e might want to permit drag-copy-state of Csys (home view state)
    def drop_enabled(self): return False #e might want to permit drop-set-state of Csys
    def node_icon(self, display_prefs):
        return self.const_icon # set in their init methods
    pass


class Csys(DataNode):
    """ Information for coordinate system"""

    def __init__(self, assy, name, scale, pov, zoomFactor, w, x = None, y = None, z = None):
        self.const_icon = imagename_to_pixmap("csys.png")
        Node.__init__(self, assy, name)
        self.scale = scale
        assert type(pov) == type(V(1, 0, 0))
        self.pov = V(pov[0], pov[1], pov[2])
        self.zoomFactor = zoomFactor
        
        if not x and not y and not z:
            self.quat = Q(w)
        else:
            self.quat = Q(x, y, z, w)
            
        return

    def show_in_model_tree(self):
        #bruce 050128; nothing's wrong with showing them, except that they are unselectable
        # and useless for anything except being renamed by dblclick (which can lead to bugs
        # if the names are still used when files_mmp reads the mmp file again). For Beta we plan
        # to make them useful and safe, and then make them showable again.
        "[overrides Node method]"
        return False

    def writemmp(self, mapping):
        v = (self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.scale,
             self.pov[0], self.pov[1], self.pov[2], self.zoomFactor)
        mapping.write("csys (" + self.name +
                ") (%f, %f, %f, %f) (%f) (%f, %f, %f) (%f)\n" % v)

    def copy(self, dad=None):
        #bruce 050420 -- revise this (it was a stub) for sake of Part view propogation upon topnode ungrouping;
        # note that various Node.copy methods are not yet consistent, and I'm not fixing this now.
        # (When I do, I think they will not accept "dad" but will accept a "mapping", and will never rename the copy.)
        # The data copied is the same as what can be passed to init and what writemmp writes.
        # Note that the copy needs to have the same exact name, not a variant (since the name
        # is meaningful for the internal uses of this object, in the present implem).
        assert dad == None
        if "a kluge is ok since I'm in a hurry":
            # the data in this Csys might not be up-to-date, since the glpane "caches it"
            # (if we're the Home or Last View of its current Part)
            # and doesn't write it back after every user event!
            # probably it should... but until it does, do it now, before copying it!
            self.assy.o.saveLastView()                
        if 0 and platform.atom_debug:
            print "atom_debug: copying csys:", self
        return Csys( self.assy, self.name, self.scale, self.pov, self.zoomFactor, self.quat )

    def __str__(self):
        #bruce 050420 comment: this is inadequate, but before revising it
        # I'd have to verify it's not used internally, like Jig.__str__ used to be!!
        return "<csys " + self.name + ">"
        
    pass # end of class Csys


# bruce 050417: removing class Datum (and ignoring its mmp record "datum"),
# since it has no useful effect (and not writing it will not even be
# noticed by old code reading our mmp files). But the code should be kept around,
# since we might reuse some of it when we someday have real "datum planes".
# More info about this can be found in other comments/emails.
##class Datum(DataNode):
##    """ A datum point, plane, or line"""
##    
##    def __init__(self, assy, name, type, cntr, x = V(0,0,1), y = V(0,1,0)):
##        self.const_icon = imagename_to_pixmap("datumplane.png")
##        Node.__init__(self, assy, name)
##        self.type = type
##        self.center = cntr
##        self.x = x
##        self.y = y
##        self.rgb = (0,0,255)
##
##    def show_in_model_tree(self): #bruce 050127
##        "[overrides Node method]"
##        return False
##        
##    def writemmp(self, mapping):
##        mapping.write("datum (" + self.name + ") " +
##                "(%d, %d, %d) " % self.rgb +
##                self.type + " " +
##                "(%f, %f, %f) " % tuple(self.center) +
##                "(%f, %f, %f) " % tuple(self.x) +
##                "(%f, %f, %f)\n" % tuple(self.y))
##
##    def __str__(self):
##        return "<datum " + self.name + ">"
##
##    def copy(self, dad, offset):
##        #bruce 050417 comment: this should not have "offset" arg,
##        # since Node.copy doesn't, so if a Datum object gets into main part MT
##        # (which only happens if you construct a nonstandard mmp file by hand,
##        #  but could also happen if we used them more generally in future code)
##        # and user tries to copy it in MT (using this code), we get a traceback.
##        # This means that Datum objects (stored using their current mmp record)
##        # will never be safe to include in assy.tree of mmp files which should
##        # be readable by old code, and they have no meaningful effect in their
##        # standard location (assy.viewdata), so we might as well deprecate their
##        # mmp record, discard it whenever read by new code and never write it
##        # into mmp files, and start from scratch when we want real "datum planes".
##        new = Datum(self.assy, self.name, self.type,
##                    self.center+offset, self.x, self.y)
##        new.rgb = self.rgb
##        new.dad = dad
##        return new
##
##    pass # end of class Datum

# rest of file added by bruce 050108/050109, needs review when done ###@@@

# specialized kinds of Groups:

class PartGroup(Group):
    """A specialized Group for holding the entire "main model" of an assembly,
    with provisions for including the "assy.viewdata" elements as initial kids, but not in self.members
    (which is a kluge, and hopefully can be removed reasonably soon, though perhaps not for Alpha).
    """
    _initialkids = [] #bruce 050302
    # These revised definitions are the non-kluge reason we need this subclass: ###@@@ also some for menus...
    def is_top_of_selection_group(self): return True #bruce 050131 for Alpha
    def rename_enabled(self): return False
    def drag_move_ok(self): return False
    # ... but drag_copy is permitted! (someday, when copying groups is permitted)
    # drop methods should be the same as for any Group
    def permits_ungrouping(self): return False
    def node_icon(self, display_prefs):
        # same whether closed or open
        return imagename_to_pixmap("part.png")
##    # And this temporary kluge makes it possible to use this subclass where it's
##    # needed, without modifying assembly.py or files_mmp.py:
##    def kluge_set_initial_nonmember_kids(self, lis): #bruce 050302 comment: no longer used, for now
##        """[This kluge lets the csys and datum plane model tree items
##        show up in the PartGroup, without their nodes being in its members list,
##        since other code wants their nodes to remain in assy.viewdata, but they can
##        only have one .dad at a time. Use of it means you can't assume node.dad
##        corresponds to model tree item parent!]
##        """
##        lis = filter( lambda node: node.show_in_model_tree(), lis)
##            # bruce 050127; for now this is the only place that honors node.show_in_model_tree()!
##        self._initialkids = list(lis)
    def kids(self, display_prefs):
        "overrides Group.kids"
        if not self.openable() or not display_prefs.get('open',False):
            return []
        regularkids = Group.kids(self, display_prefs)
        return list(self._initialkids + regularkids)
    def edit(self):
        cntl = PartProp(self.assy)
            #bruce comment 050420: PartProp is passed assy and gets its stats from assy.tree.
            # This needs revision if it should someday be available for Parts on the clipboard.
        cntl.exec_loop()
        self.assy.mt.mt_update()
    def description_for_history(self):
        """[overridden from Group method]"""
        return "Part Name: [" + self.name +"]"
    pass

class ClipboardShelfGroup(Group):
    """A specialized Group for holding the Clipboard (aka Shelf). [This will be revised... ###@@@]
    """
##    def select_enabled(self): return False #bruce 050131 for Alpha -- not yet used, maybe not needed
    def pick(self): #bruce 050131 for Alpha
        # I might just do this and not bother honoring select_enabled; don't know yet.
        msg = "Clipboard can't be selected or dragged. (Individual clipboard items can be.)"
        ## bruce 050316: no longer do this: self.redmsg( msg)
        self.assy.w.history.transient_msg( msg)
    def is_selection_group_container(self): return True #bruce 050131 for Alpha
    def rename_enabled(self): return False
    def drag_move_ok(self): return False
    def drag_copy_ok(self): return False
    ## def drop_enabled(self): return True # not needed since default; drop on clipboard makes a new clipboard item
    def drop_on(self, drag_type, nodes):
        #bruce 050203: nodes dropped onto the clipboard come from one "space"
        # and ought to stay that way by default; user can drag them one-at-a-time if desired.
        # (In theory this grouping need only be done for the subsets of them which are bonded;
        #  for now that's too hard -- maybe not for long, similar to bug 371.)
        if len(nodes) > 1 and drag_type == 'move': ####@@@@ desired for copy too, but below implem would be wrong for that...
            name = self.assy.name_autogrouped_nodes_for_clipboard( nodes, howmade = drag_type )
            new = Group(name, self.assy, None) ###k review last arg ####@@@@
            parts = {} # maps id(part) to part for all nonnull parts in nodes
                #bruce 050420: fix an unreported bug related to bug 556, but for dragged nodes which get auto-grouped.
                # If the nodes all have same .part (of those which have a .part) (I believe they will always all have
                # the same nonnull part, but I'm testing this to be robust), add new group to that part too;
                # this part will be replaced later by update_parts, but serves to pass on these node's view in glpane
                # to the new part. (The replacement might be "needless" if we were dragging *all* nodes from
                # that part, but we're not bothering here to make its topnode correct -- and we surely couldn't
                # if we're only dragging *some* nodes from it.)
            for node in nodes[:]: #bruce 050216 don't reverse the order, it's already correct
                part = node.part
                if part:
                    parts[id(part)] = part
                del part
                node.unpick() #bruce 050216; don't know if needed or matters; 050307 moved from after to before moveto
                node.moveto(new) ####@@@@ guess, same as in super.drop_on (move here, regardless of drag_type? no, not correct!)
            if len(parts) == 1:
                part = parts.values()[0]
                part.add(new) #bruce 050420, explained in comment above
                if 0 and platform.atom_debug:
                    print "atom_debug: added autogroup to shared part of its nodes"
            nodes = [new] # a new length-1 list of nodes
            self.assy.w.history.message( "(fyi: Grouped some nodes to keep them in one clipboard item)" ) ###e improve text
        return Group.drop_on(self, drag_type, nodes)
    def permits_ungrouping(self): return False
    ##bruce 050316: does always being openable work around the bugs in which this node is not open when it should be?
    ###e btw we need to make sure it becomes open whenever it contains the current part. ####@@@@
##    def openable(self): # overrides Node.openable()
##        "whether tree widgets should permit the user to open/close their view of this node"
##        non_empty = (len(self.members) > 0)
##        return non_empty
    def node_icon(self, display_prefs):
        del display_prefs # unlike most Groups, we don't even care about 'open'
        non_empty = (len(self.members) > 0)
        if non_empty:
            kluge_icon = imagename_to_pixmap("clipboard-full.png")
            res = imagename_to_pixmap("clipboard-full.png")
        else:
            kluge_icon = imagename_to_pixmap("clipboard-gray.png")
            res = imagename_to_pixmap("clipboard-empty.png")
        # kluge: guess: makes paste tool look enabled or disabled
        ###@@@ clean this up somehow?? believe it or not, it might actually be ok...
        self.assy.w.editPasteAction.setIconSet(QIconSet(kluge_icon))
        return res
    def edit(self):
        return "The Clipboard does not yet provide a property-editing dialog."
    def edit_props_enabled(self):
        return False
    def description_for_history(self):
        """[overridden from Group method]"""
        return "Clipboard"
    pass

class RootGroup(Group):
    """A specialized Group for holding the entire model tree's toplevel nodes,
    which (by coincidence? probably more like a historical non-coincidence)
    imitates the assy.root member of the pre-050109 code. [This will be revised... ###@@@]
    [btw i don't know for sure that this is needed at all...]
    ###obs doc, but reuse some of it:
    This is what the pre-050108 code made or imitated in modelTree as a Group called ROOT. ###k i think
    This will be revised soon, because
    (1) the assembly itself might as well be this Node,
    (2)  the toplevel members of an assembly will differ from what they are now.
    """
##    def select_enabled(self): return False #bruce 050131 for Alpha -- should never matter
    def pick(self): #bruce 050131 for Alpha
        self.redmsg( "Internal error: tried to select assy.root (ignored)" )
    #e does this need to differ from a Group? maybe in some dnd/rename attrs...
    # or maybe not, since only its kids are shown ###@@@
    # (we do use the fact that it differs in class from a Group
    #  as a signal that we might need to replace it... not sure if this is needed)
    pass

# the next few functions belong in assembly.py and/or in a different form

def kluge_patch_assy_toplevel_groups(assy, assert_this_was_not_needed = False): #bruce 050109
    ####@@@@ should be turned into mods to assembly.py, or a method in it
    """This kluge is needed until we do the same thing inside assy
    or whatever makes the toplevel groups in it (eg files_mmp).
    Call it as often as you want (at least once before updating model tree
    if assy might be newly loaded); it only changes things when it needs to
    (once for each newly loaded file or inited assy, basically);
    in theory it makes assy "look right in the model tree"
    without changing what will be saved in an mmp file,
    or indeed what will be seen by any other old code looking at
    the 3 attrs of assy this function replaces (shelf, tree, root).
    Note: if any of them is None, or not an instance object, we'll get an exception here.
    """
    #bruce 050131 for Alpha:
    # this is now also called in assembly.__init__ and in readmmp,
    # not only from the mtree.
    
    oldmod = assy_begin_suspend_noticing_changes(assy)
    # does doing it this soon help? don't know why, was doing before root mod...
    # now i am wondering if i was wrong and bug of wrongly reported assy mod
    # got fixed even by just doing this down below, just before remaking root.
    # anyway that bug *is* fixed now, so ok for now, worry about it later. ###@@@
    fixroot = 0
    try:
        if assy.shelf.__class__ == Group:
            assy.shelf = assy.shelf.kluge_change_class( ClipboardShelfGroup)
            fixroot = 1
        if assy.tree.__class__ == Group:
            assy.tree = assy.tree.kluge_change_class( PartGroup)
            ##bruce 050302 removing use of 'viewdata' here,
            # since its elements are no longer shown in the modelTree,
            # and I might as well not figure them out re assy/part split until we want
            # them back and know how we want them to behave regarding parts.
##            lis = list(assy.viewdata.members)
##            # are these in the correct order (CSys XY YZ ZX)? I think so. [bruce 050110]
##            assy.tree.kluge_set_initial_nonmember_kids( lis )
            fixroot = 1
        if assy.root.__class__ == Group or fixroot:
            fixroot = 1 # needed for the "assert_this_was_not_needed" check
            ## sanitize_for_clipboard has been replaced by update_parts done by callers [050309]:
##            for m in assy.shelf.members:
##                assy.sanitize_for_clipboard( m) # needed for when Groups in clipboard are read from mmp files
            #e make new Root Group in there too -- and btw, use it in model tree widgets for the entire tree...
            # would it work better to use kluge_change_class for this?
            # academic Q, since it would not be correct, members are not revised ones we made above.
            assy.root = RootGroup("ROOT", assy, None, [assy.tree, assy.shelf]) #k ok to not del them from the old root??
            ###@@@ BUG (suspected caused here): fyi: too early for this status msg: (fyi: part now has unsaved changes)
            # is it fixed now by the begin/end funcs? at leastI don't recall seeing it recently [bruce 050131]
            ## removed this, 050310: assy.current_selection_group = assy.tree #bruce 050131 for Alpha
            assy.root.unpick() #bruce 050131 for Alpha, not yet 100% sure it's safe or good, but probably it prevents bugs
            ## revised this, 050310:
            ## assy.current_selection_group = assy.tree # do it both before and after unpick (though in theory either alone is ok)
            ## assy.current_selgroup_changed()
            ## assy.set_current_selgroup( assy.tree) -- no, checks are not needed and history message is bad
            assy.init_current_selgroup() #050315
    finally:
        assy_end_suspend_noticing_changes(assy,oldmod)
        if fixroot and assert_this_was_not_needed: #050315
            if platform.atom_debug:
                print_compact_stack("atom_debug: fyi: kluge_patch_assy_toplevel_groups sees fixroot and assert_this_was_not_needed: ")
    return

# these should also become assy methods, I guess
# (they depend on assy._modified working as it did on 050109)
# [writen by bruce 050110]

def assy_begin_suspend_noticing_changes(assy):
    oldmod = assy._modified
    assy._modified = 1
    return oldmod # this must be passed to the 'end' function
    # also, if this is True, caller can safely not worry about
    # calling "end" of this, i suppose; best not to depend on that

def assy_end_suspend_noticing_changes(assy, oldmod):
    assy._modified = oldmod
    return

# ==

##descendents? spelling..
def topmost_nodes( nodes): #bruce 050303
    """Given 0 or more nodes (as a python sequence), return a list
    of the given nodes that are not descendents of other given nodes.
    [See also hindmost and topmost_selected_nodes, but those only work for
    the set of selected nodes.]
       WARNING: current implem is quadratic time in len(retval).
    """
    res = {} # from id(node) to node
    for node in nodes:
        assert node # incorrect otherwise, false values won't have .is_ascendant method
        dad = node # not node.dad, that way we remove dups as well (might never be needed, but good)
        while dad:
            if id(dad) in res:
                break
            dad = node.dad
        if not dad:
            # node and its dads (all levels) were not in res
            # add node, but also remove any members that are below it (how?)
            #e (could be more efficient if we sorted nodes by depth in tree,
            #  or perhaps even sorted the tree-paths from root to each node)
            for other in res.values():
                if node.is_ascendant(other):
                    del res[id(other)]
            res[id(node)] = node
    return res.values()

# ==

# this might be obs as of 050303 don't yet know

# bruce 050225.
#e someday we'll have a superclass, for "operation tracker/guider/stagers" or so...
# and for serving as a history-object afterwards.

class MovingNodes:
    """Class for organizing one multi-node move operation.
    Can be extended for nodetree-types with more structure that needs to be maintained
    (we do this in part.py for nodetrees with nodes divided into parts, and inter-node
    bonds which should not be inter-part bonds).
       To do a move of a set of nodes, create this object,
    call its begin method (maybe do those steps together),
    do the actual node-moving by means of addchild operations
    (thus rearranging the node-tree to accomplish the raw move),
    making sure those ops call our track_changed_dad method [###e and for which nodes, exactly?],
    and finally call this object's end method
    to do things which subclasses might need to extend, e.g.
    to maintain the mapping from nodes to parts (based on the changed tree structure),
    and to break any bonds between nodes that are now in different parts,
    and to help parts keep their own lists of their nodes, selected nodes, etc.
       What this superclass provides is the structure for tracking all this
    and some help to subclasses for analyzing the nodesets.
    """
    def __init__(self, *_begin_args, **_begin_kws): #e superclass method?
        if _begin_args or _begin_kws:
            self.begin(*_begin_args, **_begin_kws)
    def begin(self, nodes):
        "prepare the given set of toplevel nodes to be moved (along with their entire subtrees)"
        self.fixnodes = {}
        map( self.track_changed_dad, nodes) # should not be needed -- do an assert instead? no, not clear they all have to move
        pass
    def track_changed_dad(self, node): # not needed if we do it in the begin method and its nodes were complete and no new nodes made
        self.fixnodes[id(node)] = node
        pass
    def end(self):
        "clean up extended structure after the node-motion is complete" #e with both old and new trees as arguments?
        #e or, one tree, and old and new 'dad attrs' and 'members attrs' (ie old and new tree structures)? in fact, map btwn those?
        # use fixnodes...
        pass
    pass
    
# end
