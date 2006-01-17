# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
undo_archive.py

Collect and organize a set of checkpoints of model state and diffs between them,
providing undo/redo ops which apply those diffs to the model state.

$Id$
'''
__author__ = 'bruce'

#bruce 060117 newer simpler code, less modular, will be generalized along lines of older code which is not in cvs right now

from files_mmp import writemmp_mapping

import time

def mmpstring_from_assy(assy): #bruce 060117 prototype-kluge
    """return a data-like python object encoding all the undoable state in assy
    (or in nE-1 while it's using assy)
    (it might contain refs to permanent objects like elements or atomtypes, and/or contain Numeric arrays)
    [modified from files_mmp.writemmpfile_assy]
    """
    return 'stub data' ########@@@@@@@@ kluge for commit

    assy.o.saveLastView()

    assy.update_parts() ### better if we could assume this is done already; also worry about all other updates, like bonds
    
    fp = open("/tmp/fff", "w")########@@@@@@@@ KLUGE, fix

    mapping = writemmp_mapping(assy) ###e should pass options
    mapping.set_fp(fp)

    try:
        mapping.write_header()
        assy.construct_viewdata().writemmp(mapping)
        assy.tree.writemmp(mapping)
        
        mapping.write("end1\n")
        mapping.past_sim_part_of_file = True
        
        if addshelf:
            assy.shelf.writemmp(mapping)
        
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()

    fp = open("/tmp/fff", "r")
    data = fp.read()
    fp.close()
    
    return data #e soon will modify to not use disk, and return a different kind of py object

# we'll still try to fit into the varid/vers scheme for multiple out of order undo/redo,
# since we think this is highly desirable for A7 at least for per-part Undo.
# but varids are only needed for highlevel things with separate ops offered.
# so a diff is just a varid-ver list and a separate operation...
# which can ref shared checkpoints if useful. it can ref both cps and do the diff lazily if you want.
# it's an object, which can reveal these things...
# it has facets... all the same needs come up again...
# maybe it's easier to let the facets be flyweight and ref shared larger pieces and just remake themselves?

class Checkpoint:
    def __init__(self, ver = None, state = None):
        if ver is None:
            ver = 'ver-' + `time.time()` #####@@@@@ wrong! unique int!
        self.ver = ver
        self.state = state # permit storing this later (public attribute for set) (also public for get, see SimpleDiff.apply_to)
        self.varid = 'varid_stub'
    def varid_ver(self):
        """Assuming there is one varid for entire checkpoint, return its varid_ver pair.
        Hopefully this API and implem will need revision for A7 since assumption will no longer be true.
        """
        return self.varid, self.ver
    pass

class SimpleDiff:
    "diff defined as going from checkpoint 0 to checkpoint 1 (in that order, when applied)"
    default_opts = dict(op_name = "")
    def __init__(self, cp0, cp1, direction = 1, **options):
        "direction is a sign, 1 means forwards in time (redo diff), -1 means backwards (undo diff); options include opname"
        self.cps = cp0, cp1
        self.direction = direction
        self.options = options
        self.opts = dict(self.default_opts).update(options) # use these for actual values to use (could be done lazily)
    def reverse_order(self):
        return self.__class__(self.cps[1], self.cps[0], - self.direction, **self.options)
    def menu_desc(self):
        main = {1: "Redo", -1: "Undo"}[self.direction]
        op_name = self.opts['op_name']
        if op_name:
            main = "%s %s" % (main, op_name)
        return main
    def varid_vers(self):
        "list of varid_ver pairs for indexing"
        return [self.cps[0].varid_ver()]
    def last_cp(self):
        "...Hopefully this API and implem will need revision for A7 ..."
        return self.cps[1]
    def apply_to(self, assy):
        "apply this diff-operation to the given model objects"
        self.assy.become_state(self.cps[1].state) ###IMPLEM become_state, or maybe even have this make a new assy?? try not to...
    pass

def make_checkpoint(assy):
    data = mmpstring_from_assy(assy)
    return Checkpoint(None, data) # makes up ver -- iedally we'd do that here, make cp without data, let difftracking add to it...

class AssyUndoArchive: # modified from UndoArchive_older and AssyUndoArchive_older
    def __init__(self, assy):
        self.assy = assy
        self.stored_ops = {} # see older class's docstring for this ###doc
        self.last_cp = make_checkpoint(self.assy) # initial checkpoint
            #e note, self.last_cp will be augmented by a desc of varid_vers pairs about cur state; 
            # but for out of order redo, we get to old varid_vers pairs but new cp's; maybe there's a map from one to the other...
            ###k was this part of UndoManager in old code scheme? i think it was grabbed out of actual model objects in UndoManager.
    def checkpoint(self):
        cp = make_checkpoint(self.assy)
        #e could compare this and last cp for being identical (here, or as we make the diff in next subr)
        redo_diff = SimpleDiff(self.last_cp, cp) #e will be done incrementally by tracking in A7-i-hope version
        undo_diff = redo_diff.reverse_order()
        self.store_op(redo_diff)
        self.store_op(undo_diff)
        self.last_cp = cp
    def do_op(self, op):
        "do one of the diff-ops we're storing (apply it to state, correct stored varid_ver pairs)"
        op.apply_to(self.assy)
            # note: actually affects more than just assy, perhaps (ie glpane view state...)
            #e when diffs are tracked, worry about this one being tracked
            #e should track how this affects varid_vers pairs
        self.last_cp = op.last_cp()
    pass


# end
