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

from VQT import *
from shape import *
from qt import QPixmap
import sys, os
from PartProp import *
from GroupProp import *
from debug import print_compact_stack
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
    to be typical of "leaf Nodes" -- most of them are overridden by Group,
    only some of them by other Node subclasses. [bruce 050108 revised that... ####k ####@@@@ check it]
    """

    # leaf nodes have an immutable 0-length sequence of members [bruce 050108]
    # (this simplifies some definitions here) ###@@@ at least temporarily... remove if no longer needed.
    members = ()
    
    def openable(self):
        """whether tree widgets should permit the user to open/close their view
        of this node (typically by displaying some sort of toggle icon for that state)
        (note, if this is True then this does not specify whether the node view is initially open... #doc what does)
        [some subclasses should override this]
        """
        # if we decide this depends on the tree widget or on something about it,
        # we'll have to pass in some args... don't do that unless/until we need to.
        return False ###@@@ might be better to measure the members list??

    def renameable(self):
        """whether tree widgets should permit the user to rename this node
        [some subclasses should override this]
        [#doc how the rename is supported by the node!]
        """
        return True

    def enable_drag(self): # the dnd option to buildNode, drag aspect
        """#doc this
        [some subclasses should override this]
        """
        return True
    
    def enable_drop(self): # the dnd option to buildNode, drop aspect
        """#doc this
        [some subclasses should override this]
        """
        return True

    def node_icon(self, open = False):
        """#doc this
        [some subclasses should override this]
        """
        return self.icon ###@@@ not sure if this is correct even for leaf nodes, might need seticon
        pass ###stub
    
    # methods before this are by bruce 050108 and should be reviewed when my rewrite is done ###@@@
        
    name = "" # for use before __init__ runs (used in __str__ of subclasses)
    
    def __init__(self, assembly, parent, name=None): ###@@@ fix inconsistent arg order
        self.assy = assembly
        self.name = name or "" # assumed to be a string by some code
        self.dad = parent # another Node (which must be a Group), or None ###k ###@@@
        if self.dad:
            self.dad.addmember(self)
        self.picked = False # whether it's selected
            # (for highlighting in all views, and being affected by operations)
        self.hidden = False # whether to make it temporarily invisible in the glpane
        self.icon = None ###@@@ to be removed? or, default retval from node_icon?

    def buildNode(self, obj, parent, icon, dnd=True, rename=True): ###@@@ bad here, move to mtree.py... with its calls??
        """ build a display node in the tree widget
        corresponding to obj (and return it)
        """
        node = QListViewItem(parent, obj.name)
        node.object = obj
        node.setPixmap(0, icon)
        node.setDragEnabled(dnd)
        node.setDropEnabled(dnd)
        node.setRenameEnabled(0,rename)
        return node
        
    # for a leaf node, add it to the dad node just after us
    def addmember(self, node, before=False):
        """add leaf node after (default) or before self
        """
        if node == self: return
#        print "Utility.Node.addmember: adding node [",node.name,"] after/before [",self.name,"]"
        m = self.dad.members
        if before: i = m.index(self) # Insert node before self
        else: i = m.index(self) + 1 # Insert node after self
        m.insert(i, node)
        node.dad = self.dad
        
    def whosurdaddy(self):
        """returns the name of self's daddy
        """
        daddy = str(self.dad.name)
        return daddy

    def pick(self):
        """select the object
        """
        if not self.picked:
            self.picked = True
            # If the picked item is on the clipboard, update the pasteCombobox on the Build dashboard
            if self.dad.name == "Clipboard": self.assy.o.mode.UpdateDashboard()

    def unpick(self):
        """unselect the object
        """
        if self.picked:
            self.picked = False

    def hide(self):
        self.hidden = True
        self.seticon()
        self.unpick()
        
    def unhide(self):
        self.hidden = False
        self.seticon()

    def apply2all(self, fn):
        fn(self)

    def apply2tree(self, fn):
        pass

    def apply2picked(self, fn):
        if self.picked: fn(self)

    def hindmost(self):
        if self.picked: 
            return self
        return None

    def ungroup(self):
        pass

    def kill(self):
        self.dad.delmember(self)
        # If a member of the clipboard, update the pasteCombobox on the Build dashboard
        if self.dad.name == "Clipboard": self.assy.o.mode.UpdateDashboard() 

    def is_ascendant(self, obj):
        """Is node in the subtree of nodes headed by self?
        """
        pass

    def moveto(self, node, before=False):
        """Move self to a new location in the model tree, before or after node
        """
#        print "Utility.Node.moveto: Moving self [", self.name,"] after/before node [",node.name, "]. Before =[",before,"]"
        
        if node == self: return
            
        # Mark comments 041210
        # For DND, self is the selected item and obj is the item we dropped on. 
        # If self is a group, we need to check if obj is a child of self. If so, return since we can't do that.
        if self.is_ascendant(node): return
#        if isinstance(self, Group): # If self is a Group...
#            dad = obj.dad
#            while dad:
#                if dad == self: return # If self is a dad, grandad, etc. of obj, return.
#                dad = dad.dad

        self.dad.delmember(self)
        node.addmember(self, before)

    def nodespicked(self):
        if self.picked: return True ###@@@ bruce 050108 comment: this is inconsistent, another version of this returns a number.
        else: return False
        
    def seticon(self):
        pass

    ## Note the icon() method is removed and replaced with the icon
    ## member variable. This can simply be set externally to change
    ## the node's icon.
    def upMT(self, parent, dnd=True):
        if not self.icon: self.seticon()
        self.tritem = self.buildNode(self, parent, self.icon, dnd)
        return self.tritem
    
    def setProp(self, tw):
        tw.setSelected(self.tritem, self.picked)

    def edit(self):
        pass

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

    def openable(self): # overrides Node.openable()
        "whether tree widgets should permit the user to open/close their view of this node"
        # if we decide this depends on the tree widget or on something about it,
        # we'll have to pass in some args... don't do that unless/until we need to.
        return True

    def renameable(self):
        "whether tree widgets should permit the user to rename this node"
        rename = True # true for most Groups
        ###@@@ these kluges (taken from the deprecated self.buildNode) should be replaced by new subclasses of Group
        if self.name == "Clipboard": rename = False # Do not allow the clipboard to be renamed
        if self.name == self.assy.name: rename = False # Do not allow the part node to be renamed
        return rename

    def enable_drag(self): # the dnd option to buildNode, drag aspect
        return True
    
    def enable_drop(self): # the dnd option to buildNode, drop aspect
        return True

    # methods before this are by bruce 050108 and should be reviewed when my rewrite is done ###@@@
    
    def __init__(self, name, assembly,  parent, list = []):
        Node.__init__(self, assembly, parent, name)
        self.members = []
        for ob in list: self.addmember(ob)
        self.open = True

    def buildNode(self, obj, parent, icon, dnd=True, rename=True):
        """ build a Group node in the tree widget
        corresponding to obj (and return it)
        """
        if self.name == "Clipboard": rename = False # Do not allow the clipboard to be renamed
        if self.name == self.assy.name: rename = False # Do not allow the part node to be renamed
        node = Node.buildNode(self, obj, parent, icon, dnd, rename)
        return node

# bruce 050108 removed all uses of setopen, since it should be defined
# on tree items, not nodes        
##    def setopen(self):
##        self.open = True
        
    def addmember(self, node, top=False):
        """add leaf node to bottom (default) or top of self
        """
        if not node: return
#        print "Utility.Group.addmember: adding node [",node.name,"] to the bottom/top of group [",self.name,"]"
        self.assy.changed()
        if top: self.members.insert(0, node) # Insert node at the very top
        else: self.members += [node] # Add node to the bottom
        node.dad = self
        node.assy = self.assy

    def delmember(self, obj):
        obj.unpick() #bruce 041029 fix bug 145
        self.assy.changed()
        try:
            self.members.remove(obj)
        except: pass

    def pick(self):
        """select the object
        """
        self.picked = True
        for ob in self.members:
            ob.pick()
        
        if self.name == self.assy.name: msg = "Part Name: [" + self.name +"]"
        elif self.name == "Clipboard": msg = "Clipboard"
        else: msg = "Group Name: [" + self.name +"]"
        self.assy.w.history.message( msg )

    def unpick(self):
        """unselect the object
        """
        self.picked = False
        for ob in self.members:
            ob.unpick()
            
    def hide(self):
        for ob in self.members:
            ob.hide()

    def unhide(self):
        for ob in self.members:
            ob.unhide()
                
    def apply2all(self, fn):
        fn(self)
        for ob in self.members:
            ob.apply2all(fn)

    def apply2tree(self, fn):
        fn(self)
        for ob in self.members:
            ob.apply2tree(fn)
             
    def apply2picked(self, fn):
        if self.picked: fn(self)
        else:
            for ob in self.members[:]:
                ob.apply2picked(fn)

    def hindmost(self):
        """Thinking of nodes as subtrees of the model tree, return the smallest
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

    def ungroup(self):
        if self.dad:
            if self.name == self.assy.name: return
            for x in self.members[:]:
                x.moveto(self.dad)
            self.kill()

    def copy(self, dad):
        self.assy.w.history.message("Groups cannot be copied")
        return 0
             
    def kill(self):
        if self.dad:
            self.dad.delmember(self)

    def is_ascendant(self, node):
        """returns True if self is an ascendant of node
        """
        while node:
            if node == self: return True
            node = node.dad
        return False
        
    def nodespicked(self):
        npick = 0
        for x in self.members: 
            npick = npick + x.nodespicked()
        return npick
        
    def seticon(self):
        if self.name == self.assy.name: ###@@@ kluge, use subclassing
            self.icon = imagename_to_pixmap("part.png")
        else:
            self.icon = imagename_to_pixmap("group-collapsed.png")
        
    def xxx_node_upMT(self, parent, dnd=True): ###@@@ copied here so i can see them side by side
        if not self.icon: self.seticon()
        self.tritem = self.buildNode(self, parent, self.icon, dnd)
        return self.tritem
    
    def upMT(self, parent, dnd=True):
        if not self.icon: self.seticon()
        self.tritem = self.buildNode(self, parent, self.icon, dnd)
        # mark comments 041209
        # Fixed bug 140 by reversing order nodes are built.
        for x in self.members[::-1]: # Reversed order (fixed bug 140) - Mark [04-12-09]
            x.upMT(self.tritem, dnd)
        return self.tritem
    
    def setProp(self, tw):
        """set the properties in the model tree widget to match
        those in the tree datastructure
        """
        tw.setOpen(self.tritem, self.open)
        tw.setSelected(self.tritem, self.picked)

        for ob in self.members:
            ob.setProp(tw)

    def edit(self):
        if self.name == self.assy.name: cntl = PartProp(self.assy) # Part prop
        elif self.name == "Clipboard": return
        else: cntl = GroupProp(self) # Normal group prop
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


class Csys(Node):
    """ Information for coordinate system"""

    def __init__(self, assy, name, scale, w, x = None, y = None, z = None):
        Node.__init__(self, assy, None, name)
        self.scale = scale
        self.csysIcon = imagename_to_pixmap("csys.png") ###@@@ can we just set self.icon?

        if not x and not y and not z:
            self.quat = Q(w)
        else:
            self.quat = Q(x, y, z, w)
#        print "Utility: self.quat =",self.quat

    def buildNode(self, obj, parent, icon, dnd=False, rename=False):
        """ build a Csys node in the tree widget
        corresponding to obj (and return it)
        """
        node = Node.buildNode(self, obj, parent, icon, dnd, rename)
        return node
        
    def seticon(self):
        self.icon = self.csysIcon

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


class Datum(Node):
    """ A datum point, plane, or line"""

    def __init__(self, assy, name, type, cntr, x = V(0,0,1), y = V(0,1,0)):
        Node.__init__(self, assy, None, name)
        self.type = type
        self.center = cntr
        self.x = x
        self.y = y
        self.rgb = (0,0,255)
        self.datumIcon = imagename_to_pixmap("datumplane.png") ###@@@ can we just set self.icon?

    def buildNode(self, obj, parent, icon, dnd=False, rename=False):
        """ build a Datum node in the tree widget
        corresponding to obj (and return it)
        """
        node = Node.buildNode(self, obj, parent, icon, dnd, rename)
        return node
               
    def seticon(self):
        self.icon = self.datumIcon
        
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

# rest of file added by bruce 050108, needs review when done ###@@@

# specialized kinds of Groups:

class AssemblyNode(Group):
    """A specialized Group for holding the entire assembly's Node tree.
    This is what the pre-050108 code made or imitated in modelTree as a Group called ROOT. ###k i think
    This will be revised soon, because
    (1) the assembly itself might as well be this Node,
    (2)  the toplevel members of an assembly will differ from what they are now.
    """
    def xxx():pass
    pass

class ClipboardShelfGroup(Group): ###@@@ use this!
    """A specialized Group for holding the Clipboard. [This will be revised... ###@@@]
    """
    def node_icon(self, open):
        del open
        full = (len(self.members) > 0)
        if full:
            kluge_icon = imagename_to_pixmap("clipboard-full.png")
            res = imagename_to_pixmap("clipboard-full.png")
        else:
            kluge_icon = imagename_to_pixmap("clipboard-gray.png")
            res = imagename_to_pixmap("clipboard-empty.png")
        # kluge: guess: makes paste tool look enabled or disabled ###@@@ clean this up somehow
        self.assy.w.editPasteAction.setIconSet(QIconSet(kluge_icon))
        return res
    pass

class xxx:pass

# end

