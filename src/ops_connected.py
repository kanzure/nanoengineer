# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_connected.py -- operations on the connectivity of bond networks.

$Id$

History:

bruce 050507 made this by collecting appropriate methods (by Josh) from class Part.

bruce 050520 added new code (mostly in a separate new file) for Select Doubly.

bruce 050629 code cleanup.
"""
__author__ = ["Josh", "bruce"]

from HistoryWidget import greenmsg, redmsg

class ops_connected_Mixin:
    "Mixin for providing Select Connected and Select Doubly methods to class Part"
    
    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        if not self.selatoms:
            self.w.history.message(redmsg("Select Connected: No atom(s) selected."))
            return
        self.w.history.message(greenmsg("Select Connected:"))
        
        alreadySelected = len(self.selatoms.values())
        self.marksingle()
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d connected atom(s) selected." % totalSelected)
        
        if totalSelected > alreadySelected:
            ## Otherwise, that just means no new atoms selected, so no update necessary    
            #self.w.win_update()
            self.o.gl_update()
        
    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """ ###@@@ same comment about interspace bonds as in selectConnected
        if not self.selatoms:
            self.w.history.message(redmsg("Select Doubly: No atom(s) selected."))
            return
            
        self.w.history.message(greenmsg("Select Doubly:"))
        
        alreadySelected = len(self.selatoms.values())
        from op_select_doubly import select_doubly # new code, bruce 050520
        #e could also reload it now to speed devel!
        select_doubly(self.selatoms.values()) #e optim
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d new doubly connected atom(s) selected (besides the %d initially selected)." % \
                               (totalSelected - alreadySelected, alreadySelected) ) ###e improve msg; note (s) is not in fix_plurals
                
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()
        return

    # == helpers for SelectConnected (for SelectDoubly, see separate file imported above)
    
    #bruce 050629 fixing bug 714 by rewriting this to make it non-recursive
    # (tho it's still non-interruptable), and fixing some other bug by making it
    # use its own dict for intermediate state, rather than atom.picked (so it works with Selection Filter).
    def marksingle(self):
        "select all atoms connected by a sequence of bonds to an already selected one"
        marked = {} # maps id(atom) -> atom, for processed atoms
        todo = self.selatoms.values() # list of atoms we must still mark and explore (recurse on all unmarked neighbors)
        # from elements import Singlet
        for atom in todo:
            marked[id(atom)] = atom # since marked means "it's been appended to the todo list"
        while todo:
            newtodo = []
            for atom in todo:
                assert id(atom) in marked
                #e could optim by skipping singlets, here or before appending them.
                #e in fact, we could skip all univalent atoms here, but (for non-singlets)
                # only if they were not initially picked, so nevermind that optim for now.
                for b in atom.bonds:
                    at1, at2 = b.atom1, b.atom2 # simplest to just process both atoms, rather than computing b.other(atom)
                    if id(at1) not in marked: #e could also check for singlets here...
                        marked[id(at1)] = at1
                        newtodo.append(at1)
                    if id(at2) not in marked:
                        marked[id(at2)] = at2
                        newtodo.append(at2)
            todo = newtodo
        for atom in marked.itervalues():
            atom.pick()
            # note: this doesn't actually select it unless it's not a singlet and its element passes the Selection Filter.
        return
    
    pass # end of class ops_connected_Mixin

# end
