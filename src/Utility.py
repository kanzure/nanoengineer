# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

"""Classes for objects in the model.
This file should have a more descriptive name, but that can wait.

[Owned by mark, as of 041210.]

$Id$
"""

from VQT import *
from shape import *
from qt import QPixmap
import sys, os
from PartProp import *
from GroupProp import *
from debug import print_compact_stack

class Node:
    """
    This is the basic object, inherited by groups, molecules, and jigs.
    """
    
    name = "" # for use before __init__ runs (used in __str__ of subclasses)
    
    def __init__(self, assembly, parent, name=None):
        self.assy = assembly
        self.name = name or "" # assumed to be a string by some code
        self.dad = parent
        if self.dad: self.dad.addmember(self)
        self.picked = False
        self.hidden = False
        self.icon = None


        
    def buildNode(self, obj, parent, icon, dnd=True, rename=True):
        """ build a display node in the tree widget
        corresponding to obj (and return it)
        """
        node = QListViewItem(parent, obj.name)
        node.object = obj
        node.setPixmap(0, icon)
        node.setDragEnabled(dnd)
        node.setDropEnabled(dnd)
        node.setRenameEnabled(0,rename)
        
        # in addition, each Node should have a bounding box
        return node
        
    # for a leaf node, add it to the dad node just after us
    def addmember(self, node, before=False):
        """add leaf node after (default) or before self
        """
#        print "Utility.Node.addmember: adding node [",node.name,"] after/before [",self.name,"]"

        if node == self: return
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
        if self.picked: return True
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
        f.write(self.__repr__(atnums))
        
#    def writemdl(self, atnum, alist, f, dispdef):
#        pass

    def draw(self, o, dispdef):
        pass
        
    def getinfo(self):
        pass

    #in addition, each Node should have the following methods:
    # draw, cut, copy, paste

class Group(Node):
    """The tree node class for the tree.
    Its members can be Groups, jigs, or molecules.

    """
    def __init__(self, name, assembly,  parent, list = []):
        Node.__init__(self, assembly, parent, name)
        self.members = []
        for ob in list: self.addmember(ob)
        self.open = True
                
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.partIcon = QPixmap(filePath + "/../images/part.png")
        self.groupCloseIcon = QPixmap(filePath + "/../images/group-collapsed.png")
        # in addition, each Node should have a bounding box

    def buildNode(self, obj, parent, icon, dnd=True, rename=True):
        """ build a Group node in the tree widget
        corresponding to obj (and return it)
        """
        if self.name == "Clipboard": rename = False # Do not allow the clipboard to be renamed
        if self.name == self.assy.name: rename = False # Do not allow the part node to be renamed
        node = Node.buildNode(self, obj, parent, icon, dnd, rename)
        return node
        
    def setopen(self):
        self.open = True
        
    def addmember(self, node, top=False):
        """add leaf node to bottom (default) or top of self
        """
#        print "Utility.Group.addmember: adding node [",node.name,"] to the bottom/top of group [",self.name,"]"
        self.assy.modified = 1
        if top: self.members.insert(0, node) # Insert node at the very top
        else: self.members += [node] # Add node to the bottom
        node.dad = self
        node.assy = self.assy

    def delmember(self, obj):
        obj.unpick() #bruce 041029 fix bug 145
        self.assy.modified = 1
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
        self.assy.w.msgbarLabel.setText( msg )

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

    def copy(self, dad, offset):
        new = Group(self.name + "!", self.assy, dad)
        for x in self.members:
            self.addmember(x.copy(new, offset))
        return new
             
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
        if self.name == self.assy.name:
            self.icon = self.partIcon
        else:
            self.icon = self.groupCloseIcon
        
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
        self.assy.mt.update()

    def dumptree(self, depth=0):
        print depth*"...", self.name
        for x in self.members:
            if x.dad != self: print "bad thread:", x, self, x.dad
            x.dumptree(depth+1)

    def draw(self, o, dispdef):
        if self.hidden: return
        for ob in self.members:
            ob.draw(o, dispdef)

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

class Csys(Node):
    """ Information for coordinate system"""

    def __init__(self, assy, name, scale, w, x = None, y = None, z = None):
        Node.__init__(self, assy, None, name)
        self.scale = scale
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.csysIcon = QPixmap(filePath + "/../images/csys.png")

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
        
    def edit(self):
        pass

class Datum(Node):
    """ A datum point, plane, or line"""

    def __init__(self, assy, name, type, cntr, x = V(0,0,1), y = V(0,1,0)):
        Node.__init__(self, assy, None, name)
        self.type = type
        self.center = cntr
        self.x = x
        self.y = y
        self.rgb = (0,0,255)
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.datumIcon = QPixmap(filePath + "/../images/datumplane.png")

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

    def edit(self):
        pass
        
class InsertHere(Node):
    """ Current insertion point node """

    def __init__(self, assy, name, pos = 0, end = True):
        Node.__init__(self, assy, None, name)
        self.pos = pos
        self.end = end
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.inserthereIcon = QPixmap(filePath + "/../images/inserthere.png")

    def buildNode(self, obj, parent, icon, dnd=True, rename=False):
        """ build an Insert Here node in the tree widget
        to indicate the insertion point in the model tree
        """
        node = Node.buildNode(self, obj, parent, icon, dnd, rename)
        return node
               
    def seticon(self):
        self.icon = self.inserthereIcon

