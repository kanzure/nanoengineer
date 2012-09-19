# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
objectBrowse.py

@author: Will
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Will wrote this and used it for debugging.

Bruce 071107 split it out of debug.py.
(It has an undefined reference, but presumably worked,
and is referenced by qt4transition.qt4die.
Therefore I didn't move it into outtakes or scratch.)
"""

import sys, types

### BUG: undefined variable Finder

# ==

def standardExclude(attr, obj):
    # EricM commented out these two imports in Will's code,
    # since they caused trouble for his import analysis
    # and we couldn't tell what they were for
    # (though I'm guessing from the comment below that the intent was
    # to get these imports over with before turning on some sort of debug
    # output that occurred during subsequent imports).
    # [bruce 071107 comment]

    ##from MWsemantics import MWsemantics
    ##from GLPane import GLPane
    # I am rarely interested in peeking inside these, and they create
    # tons of output.
    return False

class ObjectDescender:
    def __init__(self, maxdepth, outf = sys.stdout):
        self.already = [ ]
        self.maxdepth = maxdepth
        self.outf = outf

    def exclude(self, attr, obj):
        return False
    def showThis(self, attr, obj):
        return True

    def prefix(self, depth, pn):
        return ((depth * "\t") + ".".join(pn) + ": ")

    def handleLeaf(self, v, depth, pn):
        def trepr(v):
            if v == None:
                return "None"
            elif type(v) == types.InstanceType:
                def classWithBases(cls):
                    r = cls.__name__
                    for b in cls.__bases__:
                        r += ":" + classWithBases(b)
                    return r
                # r = v.__class__.__name__
                r = "<" + classWithBases(v.__class__) + ">"
            else:
                r = repr(type(v))
            return "%s at %x" % (r, id(v))
        if type(v) in (types.ListType, types.TupleType):
            self.outf.write(self.prefix(depth, pn) + trepr(v))
            if len(v) == 0:
                self.outf.write(" (empty)")
            self.outf.write("\n")
        elif type(v) in (types.StringType, types.IntType,
                         types.FloatType, types.ComplexType):
            self.outf.write(self.prefix(depth, pn) + repr(v) + "\n")
        else:
            self.outf.write(self.prefix(depth, pn) + trepr(v) + "\n")

    def getAttributes(self, obj):
        lst = dir(obj)
        if hasattr(obj, "__dict__"):
            for x in obj.__dict__.keys():
                if x not in lst:
                    lst.append(x)
        def no_double_underscore(x):
            return not x.startswith('__')
        lst = filter(no_double_underscore, lst)
        lst.sort()
        return lst

    def descend(self, obj, depth = 0, pathname=[ ], excludeClassVars = False):
        if obj in self.already:
            return
        self.already.append(obj)
        if depth == 0:
            self.handleLeaf(obj, depth, pathname)
        if depth >= self.maxdepth:
            return
        if type(obj) in (types.ListType, types.TupleType):
            lst = [ ]
            if len(pathname) > 0:
                lastitem = pathname[-1]
                pathname = pathname[:-1]
            else:
                lastitem = ""
            for i in range(len(obj)):
                x = obj[i]
                if not self.exclude(i, x):
                    y = pathname + [ lastitem + ("[%d]" % i) ]
                    lst.append((i, x, y))
            for i, v, pn in lst:
                if self.showThis(i, v):
                    self.handleLeaf(v, depth+1, pn)
            for i, v, pn in lst:
                self.descend(v, depth+1, pn)
        elif type(obj) in (types.DictType,):
            keys = obj.keys()
            lst = [ ]
            if len(pathname) > 0:
                lastitem = pathname[-1]
                pathname = pathname[:-1]
            else:
                lastitem = ""
            for k in keys:
                x = obj[k]
                if not self.exclude(k, x):
                    y = pathname + [ lastitem + ("[%s]" % repr(k)) ]
                    lst.append((k, x, y))
            for k, v, pn in lst:
                if self.showThis(k, v):
                    self.handleLeaf(v, depth+1, pn)
            for k, v, pn in lst:
                self.descend(v, depth+1, pn)
        elif (hasattr(obj, "__class__") or
            type(obj) in (types.InstanceType, types.ClassType,
                          types.ModuleType, types.FunctionType)):
            ckeys = [ ]
            if True:
                # Look at instance variables, ignore class variables and methods
                if hasattr(obj, "__class__"):
                    ckeys = self.getAttributes(obj.__class__)
            else:
                # Look at all variables and methods
                ckeys = ( )
            keys = self.getAttributes(obj)
            if excludeClassVars:
                keys = filter(lambda x: x not in ckeys, keys)
            lst = [ ]
            for k in keys:
                x = getattr(obj, k)
                if not self.exclude(k, x):
                    lst.append((k, x, pathname + [ k ]))
            for k, v, pn in lst:
                if self.showThis(k, v):
                    self.handleLeaf(v, depth+1, pn)
            for k, v, pn in lst:
                self.descend(v, depth+1, pn)

def objectBrowse(obj, maxdepth = 1, exclude = standardExclude, showThis = None, outf = sys.stdout):
    od = ObjectDescender(maxdepth = maxdepth, outf = outf)
    if showThis != None:
        od.showThis = showThis
    od.exclude = exclude
    od.descend(obj, pathname=['arg'])

def findChild(obj, showThis, maxdepth = 8):
    # Drill down deeper because we're being more selective
    def prefix(depth, pn):
        # no indentation
        return (".".join(pn) + ": ")
    f = Finder(maxdepth = maxdepth)
    f.showThis = showThis
    f.prefix = prefix
    f.descend(obj, pathname=['arg'])

# python -c "import debug; debug.testDescend()"
def testDescend():
    class Foo:
        pass
    x = Foo()
    y = Foo()
    z = Foo()
    x.a = 3.14159
    x.b = "When in the course of human events"
    x.c = y
    x.d = [3,1,4,1,6]
    y.a = 2.71828
    y.b = "Apres moi, le deluge"
    y.c = z
    z.a = [x, y, z]
    z.b = range(12)
    x.e = {'y': y, 'z': z}
    objectBrowse(x)
    def test(name, val):
        return name == "a"
    findChild(x, test)

# end
