# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

"""Classes for objects in the model.
This file should have a more descriptive name, but that can wait.

[No longer owned by bruce, as of 041129.]

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
        
        # in addition, each Node should have a bounding box

    # for a leaf node, add it to the dad node just after us
    def addmember(self, obj):
        if obj==self: return
        m = self.dad.members
        i = m.index(self)
        m.insert(i,obj)
        # bruce 041129 comments:
        # 1. Note that this inserts obj *before* self in the
        # list m, but since the list is backwards relative to what's displayed
        # in the model tree widget, it ends up "just after us" as promised.
        # 2. Is it safe if this is called twice? I see no auto-remove then.
        obj.dad = self.dad

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
        self.unpick()
        
    def unhide(self):
        self.hidden = False

    def apply2all(self, fn):
        fn(self)

    def apply2tree(self, fn):
        pass

    def apply2picked(self, fn):
        if self.picked: fn(self)

    def hindmost(self):
        if self.picked: return self
        return None

    def ungroup(self):
        pass

    def kill(self):
        self.dad.delmember(self)
        # If a member of the clipboard, update the pasteCombobox on the Build dashboard
        if self.dad.name == "Clipboard": self.assy.o.mode.UpdateDashboard() 

    def moveto(self, grp):
        """Move the node to a new parentage in the tree
        """
        if grp == self: return
        self.dad.delmember(self)
        grp.addmember(self)

    def seticon(self):
        pass

    ## Note the icon() method is removed and replaced with the icon
    ## member variable. This can simply be set externally to change
    ## the node's icon.
    def upMT(self, tw, parent, dnd=True):
        if not self.icon: self.seticon()
        self.tritem = tw.buildNode(self, parent, self.icon, dnd)
        return self.tritem
    
    def setProp(self, tw):
        tw.setSelected(self.tritem, self.picked)

    def edit(self):
        pass

    def dumptree(self, depth=0):
        print depth*"...", self.name

    def writemmp(self, atnums, alist, f):
        f.write(self.__repr__(atnums))

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

    def setopen(self):
        self.open = True

    def addmember(self, obj):
        self.members += [obj]
        obj.dad = self
        obj.assy = self.assy

    def delmember(self, obj):
        obj.unpick() #bruce 041029 fix bug 145
        try:
            self.members.remove(obj)
        except: pass

    def pick(self):
        """select the object
        """
        self.picked = True
        for ob in self.members:
            ob.pick()

    def unpick(self):
        """unselect the object
        """
        self.picked = False
        for ob in self.members:
            ob.unpick()

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
        if self.picked: return self
        node = None
        for x in self.members:
            h = x.hindmost()
            if node and h: return self
            node = node or h
        return node

    def ungroup(self):
        if self.dad:
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

    def seticon(self):
        if self.name == self.assy.name:
            self.icon = self.partIcon
        else:
            self.icon = self.groupCloseIcon
        
    def upMT(self, tw, parent, dnd=True):
        if not self.icon: self.seticon()
        self.tritem = tw.buildNode(self, parent, self.icon, dnd)
        for x in self.members:
            x.upMT(tw, self.tritem, dnd)
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
        for x in self.members:
            print "Utility.py: writepov: member name = [",x.name,"]"
            x.writepov(f, dispdef)

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
