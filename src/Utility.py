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

# superclass of all Nodes

class Node:
    """
    This is the basic object, inherited by groups, molecules, jigs,
    and some more specialized subclasses. The methods of Node are designed
    to be typical of "leaf Nodes" -- many of them are overridden by Group,
    and some of them by other Node subclasses.
    """
        
    name = "" # for use before __init__ runs (used in __str__ of subclasses)
    
    def __init__(self, assembly, parent, name=None): ###@@@ fix inconsistent arg order
        self.assy = assembly
        self.name = name or "" # assumed to be a string by some code
        self.dad = parent # another Node (which must be a Group), or None
        if self.dad:
            self.dad.addmember(self)
        self.picked = False # whether it's selected
            # (for highlighting in all views, and being affected by operations)
        self.hidden = False # whether to make it temporarily invisible in the glpane
            # (note: self.hidden is defined, but always False, for Groups;
            #  it might be set for any leaf node whether or not that node is ever actually
            #  shown in the glpane.)
        self.open = False # bruce 050125; kluge to make it easier to count open nodes in a tree
            # (this will never become True except for Groups)
            # (when more than one tree widget can show the same node, .open will need replacement
            #  with treewidget-specific state #e)
        return
    
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

    def rename_enabled(self):
        """whether tree widgets should permit the user to rename this node,
        (they will call try_rename to actually request renaming for a specific new name)
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
        
    def drag_enabled(self):
        """#doc this - whether a drag of this node can be started (for "drag and drop") ##k
        [some subclasses should override this]
        """
        return True
    
    def drop_enabled(self):
        """#doc this - whether "drag and drop" can drop something onto this node ##k
        [some subclasses should override this]
        """
        return True

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
            return
        ###@@@ the following should really use a new method on Group (or a new option to addchild)
        # and it ought to remove the node from old loc, and check for cycle_creation using is_ascendant.
        m = self.dad.members
        if before: i = m.index(self) # Insert node before self
        else: i = m.index(self) + 1 # Insert node after self
        m.insert(i, node)
        node.dad = self.dad
        self.dad.changed_members()
        return
        # bruce comment 010510: this method does not remove it from other Groups it might be in
        # (i.e. from prior node.dad if that's not None).
        # If those are never again used, that won't matter. If they are, bugs might ensue,
        # because they might assume the members' dads point to themselves -- I'm not sure.
    
    def addmember(self, node, before_or_top = False):
        """
        [Deprecated:] Like addsibling or addchild, depending on whether self is
        a leaf node or a Group. (Also misnamed, since a sibling is not a member.)
        [We might un-deprecate this by redefining it as what to do when you drop
        node onto self during drag-and-drop, but really that should be its own
        separate method, even if it's pretty similar to this one. This is one is
        used by a lot of old code as if it was always one or the other of the
        two methods it can call!]
        """
        if isinstance(self, Group):
            # (use isinstance (rather than overriding in a subclass)
            #  to emphasize the reason this method needs to be deprecated!)
            self.addchild( node, top = before_or_top)
        else:
            # for a leaf node, add it to the dad node just after us
            self.addsibling( node, before = before_or_top)
        return
        
##    def whosurdaddy(self): ###@@@ this will be replaced by using methods in subclasses of Group for self.dad
##        """returns the name of self's daddy
##        """
##        daddy = self.dad
##        try:
##            name = daddy.name
##        except AttributeError: #bruce 050109 bugfix
##            name = ""
##        name = str(name) #k needed??
##        return name

    def pick(self):
        """select the object
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        ###@@@ I don't know whether that new rule is yet followed by external code [bruce 050124].
        if not self.picked:
            self.picked = True
            # bruce 050125: should we also call self.assy.permit_picked_parts() here? #####@@@@@
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

    def pick_top(self): #bruce 050124
        """select the object -- but (unlike Group.pick) don't change selection state
        of its members. Note that this violates the principle "selected groupnode
        implies all selected members". This means it should be used either never
        or rarely (as of 050126 I don't know which).
        [unlike pick, this is generally NOT extended in subclasses]
        """
        Node.pick(self)

    def unpick_top(self): #bruce 050124
        """unselect the object -- but (unlike Group.unpick) don't change
        the selection state of its members. But do unselect all its ancestor nodes.
        [unlike unpick, this is generally NOT extended in subclasses]
        """
        Node.unpick(self)
    
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
        self.dad.delmember(self)
        # If a member of the clipboard, update the pasteCombobox on the Build dashboard
        ## this has been replaced by a side effect of delmember for subscribers like depmode
        ## if self.dad.name == "Clipboard": self.assy.o.mode.UpdateDashboard() 

    def is_ascendant(self, node): # implem corrected by bruce 050121; was "return None"
        """Is node in the subtree of nodes headed by self?
        [Optimization of Group.is_ascendant; see its docstring for more info.]
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
        
        if node == self: return # not needed -- optimization of is_ascendant special case
            
        # Mark comments 041210
        # For DND, self is the selected item and obj is the item we dropped on. 
        # If self is a group, we need to check if obj is a child of self. If so, return since we can't do that.
        if self.is_ascendant(node): return
        self.dad.delmember(self)
        node.addmember(self, before)

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

    def edit_props_enabled(self): #bruce 050121 added this feature ###@@@ should use it when making cmenu to disable the menu item
        """Subclasses should override this and make it return False
        if their edit method would refuse to put up an editing dialog.
        """
        # i don't know if they all do that yet...
        ##e should we check here to see if they override Node.edit??
        return True # wrong for an abstract Node, but there is no such thing!
    
    def dumptree(self, depth=0):
        print depth*"...", self.name

    def writemmp(self, atnums, alist, f):
        if platform.atom_debug:
            print "fyi: Node.writemmp ran" # can this ever happen? maybe for a jig? uses __repr__ nonstandardly! ###@@@ [bruce 050108]
        f.write(self.__repr__(atnums))
        
#    def writemdl(self, atnum, alist, f, dispdef):
#        pass

    def draw(self, o, dispdef):
        pass
        
    def getinfo(self):
        pass

    def getstatistics(self, stats):
        pass

    # end of class Node

    
    #in addition, each Node should have the following methods:
    # draw, cut, copy, paste


class Group(Node):
    """The tree node class for the tree.
    Its members can be Groups, jigs, or molecules.
    """
    
    def __init__(self, name, assembly,  parent, list = []): ###@@@ review inconsistent arg order
        Node.__init__(self, assembly, parent, name)
        self.__cmfuncs = [] # funcs to call right after the next time self.members is changed
        self.members = []
        for ob in list: self.addmember(ob)
        self.open = True

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
        if self.assy:
            self.assy.changed()
            # it is ok for something in assy.changed() to modify self.__cmfuncs
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

    def kluge_change_class(self, subclass): #bruce 050109 ###@@@ temporary
        """Return a new Group with this one's members but of the specified subclass
        (and otherwise just like this Group, which must be in class Group itself,
        not a subclass). This won't be needed once class assembly is fixed to make
        the proper subclasses directly.
        """
        assert self.__class__ == Group
        new = subclass(self.name, self.assy, self.dad) # no members yet
        assert isinstance(new, Group)
        if self.dad:
            # don't use addmember, it tells the assy it changed
            # (and doesn't add new in right place either)
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
        for attr in ['open','hidden','picked']:
            try:
                val = getattr(self, attr)
            except AttributeError:
                pass # .open will go away soon;
                # others are probably always defined but I'm not sure
                # (and should not care here, as long as I get them all)
            else:
                setattr(new, attr, val)
        new.dad.changed_members() # since new class is different from self.class, this might be needed ####@@@@ is it ok?
        return new

# bruce 050108 removed all uses of setopen, since it should be defined
# on tree items, not nodes        
##    def setopen(self):
##        self.open = True

    # bruce 050113 deprecated addmember and confined it to Node; see its docstring.
        
    def addchild(self, node, top = False): # [renamed from addmember - bruce 050113]
        """add the given node to the bottom (default) or top of this Group's members
        [node should not already be in another Group, since it's not removed from one]
        [special case: legal and no effect if node is None; don't know if this is needed]
        [Warning (from when this was called addmember):
         semantics (place of insertion, and optional arg name/meaning)
         are not consistent with Node.addmember; see my comments in its docstring.
         -- bruce 050110]
        """
        #bruce 050110 updated docstring based on current code
        if not node: return
        ## self.assy.changed() # now done by changed_members below
            ###@@@ needed in addsibling too! (unless self.changed gets defined.)
            # (and what about informing the model tree, if it's displaying us?
            #  probably we need some subscription-to-changes or modtime system...)
        if top: self.members.insert(0, node) # Insert node at the very top
        else: self.members += [node] # Add node to the bottom
        node.dad = self
        node.assy = self.assy
        self.changed_members() # must be done *after* they change

    def delmember(self, obj):
        obj.unpick() #bruce 041029 fix bug 145
        ## self.assy.changed() # now done by changed_members below
        try:
            self.members.remove(obj)
        except:
            # relying on this being permitted is deprecated;
            # therefore we don't bother to avoid our other side effects in this case [bruce 050121]
            if platform.atom_debug:
                print "atom_debug: fyi: delmember finds obj not in members list" #k does this ever happen?
            pass
        self.changed_members() # must be done *after* they change

    def pick(self):
        """select the Group -- and all its members! [see also pick_top]
        [overrides Node.pick]
        """
        Node.pick(self)
        for ob in self.members: ###@@@ picking kids too might become conditional, or go away entirely...
            ob.pick()

        msg = self.description_for_history() # bruce 050121 let subclass decide on this
##        if self.name == self.assy.name: msg = "Part Name: [" + self.name +"]"
##        elif self.name == "Clipboard": msg = "Clipboard"
##        else: msg = "Group Name: [" + self.name +"]"
        self.assy.w.history.message( msg )

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
                ## x.moveto(self.dad) #e should probably put them after self in there
                self.delmember(x)
                self.addsibling(x)
            self.kill()

    def copy(self, dad):
        ###@@@ need to review all copy methods for inconsistent semantics
        # (internal like mol.copy, or menu-event-handlers?)
        self.assy.w.history.message("Groups cannot be copied")
            ###@@@ should remove that limitation
        return 0
             
    def kill(self): ###@@@ should merge with Node.kill
        if self.dad:
            self.dad.delmember(self)

    def is_ascendant(self, node): #e rename nodetree_contains?
        """Returns True iff self is an ascendant of node,
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
        npick = 0
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
  
    def writemmp(self, atnums, alist, f):
        f.write("group (" + self.name + ")\n")
        for x in self.members:
            x.writemmp(atnums, alist, f)
        f.write("egroup (" + self.name + ")\n")
        
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
    def rename_enabled(self): return False
    def drag_enabled(self): return False #e might want to permit drag-copy-state of Csys (home view state)
    def drop_enabled(self): return False #e might want to permit drop-set-state of Csys
    def node_icon(self, display_prefs):
        return self.const_icon # set in their init methods
    pass


class Csys(DataNode):
    """ Information for coordinate system"""

    def __init__(self, assy, name, scale, w, x = None, y = None, z = None):
        self.const_icon = imagename_to_pixmap("csys.png")
        Node.__init__(self, assy, None, name)
        self.scale = scale
        
        if not x and not y and not z:
            self.quat = Q(w)
        else:
            self.quat = Q(x, y, z, w)
        return

    def writemmp(self, atnums, alist, f):
        v = (self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.scale)
        f.write("csys (" + self.name +
                ") (%f, %f, %f, %f) (%f)\n" % v)

    def copy(self, dad=None):
        print "can't copy a csys"
        return self

    def __str__(self):
        return "<csys " + self.name + ">"
        
    pass # end of class Csys


class Datum(DataNode):
    """ A datum point, plane, or line"""

    def __init__(self, assy, name, type, cntr, x = V(0,0,1), y = V(0,1,0)):
        self.const_icon = imagename_to_pixmap("datumplane.png")
        Node.__init__(self, assy, None, name)
        self.type = type
        self.center = cntr
        self.x = x
        self.y = y
        self.rgb = (0,0,255)
        
    def writemmp(self, atnums, alist, f):
        f.write("datum (" + self.name + ") " +
                "(%d, %d, %d) " % self.rgb +
                self.type + " " +
                "(%f, %f, %f) " % tuple(self.center) +
                "(%f, %f, %f) " % tuple(self.x) +
                "(%f, %f, %f)\n" % tuple(self.y))

    def __str__(self):
        return "<datum " + self.name + ">"

    def copy(self, dad, offset):
        new = Datum(self.assy, self.name, self.type,
                    self.center+offset, self.x, self.y)
        new.rgb = self.rgb
        new.dad = dad
        return new

    pass # end of class Datum

# rest of file added by bruce 050108/050109, needs review when done ###@@@

# specialized kinds of Groups:

class PartGroup(Group):
    """A specialized Group for holding the entire "main model" of an assembly,
    with provisions for including the "data" elements as initial kids, but not in self.members
    (which is a kluge, and hopefully can be removed reasonably soon, though perhaps not for Alpha).
    """
    # These revised definitions are the non-kluge reason we need this subclass: ###@@@ also some for menus...
    def rename_enabled(self): return False
    def drag_enabled(self): return False #e could be made ok for copying whole thing... maybe strip the data objs tho, or upon drop
    ## def drop_enabled(self): return False # bruce thinks dropping on it can add a child... did this prevent that?? ###k
    def permits_ungrouping(self): return False
    def node_icon(self, display_prefs):
        # same whether closed or open
        return imagename_to_pixmap("part.png")
    # And this temporary kluge makes it possible to use this subclass where it's
    # needed, without modifying assembly.py or fileIO.py:
    def kluge_set_initial_nonmember_kids(self, lis):
        """[This kluge lets the csys and datum plane model tree items
        show up in the PartGroup, without their nodes being in its members list,
        since other code wants their nodes to remain in assy.data, but they can
        only have one .dad at a time. Use of it means you can't assume node.dad
        corresponds to model tree item parent!]
        """
        self._initialkids = list(lis)
    def kids(self, display_prefs):
        "overrides Group.kids"
        if not self.openable() or not display_prefs.get('open',False):
            return []
        regularkids = Group.kids(self, display_prefs)
        return list(self._initialkids + regularkids)
    def edit(self):
        cntl = PartProp(self.assy)
        cntl.exec_loop()
        self.assy.mt.mt_update()
    def description_for_history(self):
        """[overridden from Group method]"""
        return "Part Name: [" + self.name +"]"
    pass

class ClipboardShelfGroup(Group):
    """A specialized Group for holding the Clipboard (aka Shelf). [This will be revised... ###@@@]
    """
    def rename_enabled(self): return False
    def drag_enabled(self): return False ###k
    ## def drop_enabled(self): return False ###k bruce thinks drop on clipboard can add an item to it
    def permits_ungrouping(self): return False
    def node_icon(self, display_prefs):
        del display_prefs # unlike most Groups, we don't even care about 'open'
        full = (len(self.members) > 0)
        if full:
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
    #e does this need to differ from a Group? maybe in some dnd/rename attrs...
    # or maybe not, since only its kids are shown ###@@@
    # (we do use the fact that it differs in class from a Group
    #  as a signal that we might need to replace it... not sure if this is needed)
    pass

# the next few functions belong in assembly.py and/or in a different form

def kluge_patch_assy_toplevel_groups(assy): #bruce 050109 ... ###@@@ should be turned into mods to assembly.py...
    """This kluge is needed until we do the same thing inside assy
    or whatever makes the toplevel groups in it (eg fileIO).
    Call it as often as you want (at least once before updating model tree
    if assy might be newly loaded); it only changes things when it needs to
    (once for each newly loaded file or inited assy, basically);
    in theory it makes assy "look right in the model tree"
    without changing what will be saved in an mmp file,
    or indeed what will be seen by any other old code looking at
    the 3 attrs of assy this function replaces (shelf, tree, root).
    Note: if any of them is None, or not an instance object, we'll get an exception here.
    """
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
            lis = list(assy.data.members)
            # are these in the correct order (CSys XY YZ ZX)? I think so. [bruce 050110]
            assy.tree.kluge_set_initial_nonmember_kids( lis )
            fixroot = 1
        if assy.root.__class__ == Group or fixroot:
            #e make new Root Group in there too -- and btw, use it in model tree widgets for the entire tree...
            # would it work better to use kluge_change_class for this?
            # academic Q, since it would not be correct, members are not revised ones we made above.
            assy.root = RootGroup("ROOT", assy, None, [assy.tree, assy.shelf]) #k ok to not del them from the old root??
            ####@@@@ BUG (suspected caused here): fyi: too early for this status msg: (fyi: part now has unsaved changes)
            # is it fixed now by the begin/end funcs?
    finally:
        assy_end_suspend_noticing_changes(assy,oldmod)
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

# end
