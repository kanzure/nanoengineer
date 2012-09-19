# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
mt_statistics.py - count types of nodes, when making MT context menu commands

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce wrote these long ago within the model tree code

Bruce 081216 split this out of ModelTree.py
"""

from model.chunk import Chunk
from model.jigs import Jig
from foundation.Group import Group

class all_attrs_act_as_counters: #bruce 081216 renamed from statsclass
    # todo: rename, and move to its own utility module?
    """
    class for holding and totalling counts of whatever you want, in named attributes
    """
    def __getattr__(self, attr): # in class all_attrs_act_as_counters
        if not attr.startswith('_'):
            return 0 # no need to set it
        raise AttributeError, attr
    def __iadd__(self, other):
        """
        this implements self += other for objects of this class,
        which adds corresponding counter-attributes separately
        """
        for attr in other.__dict__.keys():
            setattr( self, attr, getattr( self, attr) + getattr( other, attr) )
        return self ###k why would this retval be needed??
            # what could it mean in general for += to return something else?
            # i don't know, but without it,
            # the effect of allstats += somestats is apparently to set allstats to None!
            # I need to check out the python doc for __iadd__. [bruce 050125]
    def __str__(self): # mainly for debugging
        res1 = ""
        keys = self.__dict__.keys()
        keys.sort()
        for attr in keys:
            if res1:
                res1 += ", "
            ###k why was there a global here called res?? or was there? maybe exception got discarded.
            res1 += "%s = %d" % (attr, getattr(self, attr))
        return "<stats (%d attrs): %s>" % (len(keys), res1)
    __repr__ = __str__ #k needed?
    pass

def mt_accumulate_stats(node, stats): #bruce 081216 renamed from accumulate_stats
    """
    When making a context menu from a nodeset (of "topselected nodes"),
    this is run once on every topselected node (note: they are all picked)
    and once on every node under those (whether or not they are picked).
    """
    # todo (refactoring): could be a method on our own subclass of all_attrs_act_as_counters
    stats.n += 1

    stats.ngroups += int(isinstance(node, Group))
    if (isinstance(node, Chunk)):
        stats.nchunks += 1
        # note: chunkHasOverlayText is only a hint, so it's possible
        # this has false positives, even though it becomes accurate
        # every time node is drawn. (If it's visible in MT but hidden
        # in glpane, I think nothing will update it.) [bruce 090112 comment]
        if (node.chunkHasOverlayText and not node.showOverlayText):
            stats.canShowOverlayText += 1
        if (node.chunkHasOverlayText and node.showOverlayText):
            stats.canHideOverlayText += 1
    stats.njigs += int(isinstance(node, Jig))
    # maybe todo: also show counts of all other subclasses of Node?

    stats.npicked += int(node.picked)
    stats.nhidden += int(node.hidden)
    stats.nopen += int(node.open)
    return

# end
