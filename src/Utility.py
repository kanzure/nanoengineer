# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
# 10/3 currently being owned by Josh

"""Classes for objects in the model.
This file should have a more descriptive name, but that can wait.

$Id$
"""

from VQT import *
from shape import *
from qt import QPixmap
import sys, os
from debug import print_compact_stack

class Node:
    """
    This is the basic object, inherited by groups, molecules, and jigs.
    """
    def __init__(self, assembly, parent, name=None):
        self.assy = assembly
        self.name = name
        self.dad = parent
        if self.dad: self.dad.addmember(self)
        self.picked = False
        # in addition, each Node should have a bounding box

    # for a leaf node, add it to the dad node just after us
    def addmember(self, obj):
        if obj==self: return
        m = self.dad.members
        i = m.index(self)
        m.insert(i,obj)
        obj.dad = self.dad

    def pick(self):
        """select the object
        """
        if not self.picked:
            self.picked = True

    def unpick(self):
        """unselect the object
        """
        if self.picked:
            self.picked = False

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

    def moveto(self, grp):
        """Move the node to a new parentage in the tree
        """
        if grp == self: return
        self.dad.delmember(self)
        grp.addmember(self)

    def icon(self, treewidget):
        return treewidget.partIcon

    def upMT(self, tw, parent, dnd=True):
        self.tritem = tw.buildNode(self, parent, self.icon(tw), dnd)
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

    def setopen(self):
        self.open = True

    def addmember(self, obj):
        self.members += [obj]
        obj.dad = self
        self.assy.modified = 1
        obj.assy = self.assy

    def delmember(self, obj):
        try:
            self.members.remove(obj)
            self.assy.modified = 1
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
            x.copy(new, offset)
        return new
             
    def kill(self):
        if self.dad:
            self.dad.delmember(self)

    def icon(self, treewidget):
        return treewidget.partIcon

    def upMT(self, tw, parent, dnd=True):
        self.tritem = tw.buildNode(self, parent, self.icon(tw), dnd)
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
        pass

    def dumptree(self, depth=0):
        print depth*"...", self.name
        for x in self.members:
            if x.dad != self: print "bad thread:", x, self, x.dad
            x.dumptree(depth+1)

    def draw(self, o, dispdef):
        for ob in self.members:
            ob.draw(o, dispdef)

    def writemmp(self, atnums, alist, f):
        f.write("group (" + self.name + ")\n")
        for x in self.members:
            x.writemmp(atnums, alist, f)
        f.write("egroup (" + self.name + ")\n")
        
#    def writepov(self, atnums, alist, f, dispdef):
    def writepov(self, f, dispdef):
        for x in self.members:
            print "Utility: writepov() member = ", x.name
            x.povwrite(f, dispdef)

    def __str__(self):
        return "<group " + self.name +">"

class Csys(Node):
    """ Information for coordinate system"""

    def __init__(self, assy, name, scale, w, x = None, y = None, z = None):
        Node.__init__(self, assy, None, name)
        self.scale = scale

        if not x and not y and not z:
            self.quat = Q(w)
        else:
            self.quat = Q(x, y, z, w)

    def icon(self, treewidget):
        return treewidget.csysIcon

    def writemmp(self, atnums, alist, f):
        v = (self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.scale)
        f.write("csys (" + self.name +
                ") (%f, %f, %f, %f) (%f)\n" % v)

    def copy(self, dad=None):
        print "can't copy a csys"
        return self

    def __str__(self):
        return "<csys " + self.name + ">"

class Datum(Node):
    """ A datum point, plane, or line"""

    def __init__(self, assy, name, type, cntr, x = V(0,0,1), y = V(0,1,0)):
        Node.__init__(self, assy, None, name)
        self.type = type
        self.center = cntr
        self.x = x
        self.y = y
        self.rgb = (0,0,255)
        
    def icon(self, treewidget):
        return treewidget.datumIcon

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