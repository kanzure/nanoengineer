# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_connected.py -- operations on the connectivity of bond networks.

$Id$

History:

bruce 050507 made this by collecting appropriate methods (by Josh) from class Part.

bruce 050520 added new code (mostly in a separate new file) for Select Doubly.
"""
__author__ = "Josh"

from HistoryWidget import greenmsg, redmsg
## from qt import QApplication, QCursor, Qt

class ops_connected_Mixin:
    "Mixin for providing Select Connected and Select Doubly methods to class Part"
    
    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        if not self.selatoms:
            self.w.history.message(redmsg("Select Connected: No atom(s) selected."))
            return
        
        alreadySelected = len(self.selatoms.values())
        self.marksingle()
        self.w.history.message(greenmsg("Select Connected:"))
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
            
##        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.w.history.message(greenmsg("Select Doubly:"))
        
##        self.w.history.message("Working.  Please wait...")
        alreadySelected = len(self.selatoms.values())
        ### new code, experimental, but seems to work -- bruce 050520
        from op_select_doubly import select_doubly
        #e could also reload it now to speed devel!
        select_doubly(self.selatoms.values()) #e optim
        ### old code:
        ## self.markdouble()
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d new doubly connected atom(s) selected (besides the %d initially selected)." % \
                               (totalSelected - alreadySelected, alreadySelected) ) ###e improve msg; note (s) is not in fix_plurals
        
##        QApplication.restoreOverrideCursor() # Restore the cursor
        
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()
        return

    # == helpers for SelectConnected and [not anymore] SelectDoubly
    
    # select all atoms connected by a sequence of bonds to
    # an already selected one
    def marksingle(self):
        for a in self.selatoms.values():
            self.conncomp(a, 1)
       
    # connected components. DFS is elegant!
    # This is called with go=1 from eached already picked atom
    # its only problem is relatively limited stack in Python
    def conncomp(self, atom, go=0):
        if go or not atom.picked:
            atom.pick()
            for a in atom.neighbors():
                 self.conncomp(a)

##    # select all atoms connected by two disjoint sequences of bonds to
##    # an already selected one. This picks stiff components but doesn't
##    # cross single-bond or single-atom bearings or hinges
##    # does select e.g. hydrogens connected to the component and nothing else
##    # [bruce 050519 comment: this produces incorrect output, and has done so
##    #  since at least Alpha1. And it's very slow for big parts.]
##    def markdouble(self):
##        self.father= {}
##        self.stack = []
##        self.out = []
##        self.dfi={}
##        self.p={}
##        self.i=0
##        for a in self.selatoms.values():
##            if a not in self.dfi:
##                self.father[a]=None
##                self.blocks(a)
##        for (a1,a2) in self.out[-1]:
##            a1.pick()
##            a2.pick()
##        for mol in self.molecules:
##            for a in mol.atoms.values():
##                if len(a.bonds) == 1 and a.neighbors()[0].picked:
##                    a.pick()
##
##    # compared to that, the doubly-connected components algo is hairy.
##    # cf Gibbons: Algorithmic Graph Theory, Cambridge 1985
##    def blocks(self, atom):
##        self.dfi[atom]=self.i
##        self.p[atom] = self.i
##        self.i += 1
##        for a2 in atom.neighbors():
##            if atom.key < a2.key: pair = (atom, a2)
##            else: pair = (a2, atom)
##            if not pair in self.stack: self.stack += [pair]
##            if a2 in self.dfi:
##                if a2 != self.father[atom]:
##                    self.p[atom] = min(self.p[atom], self.dfi[a2])
##            else:
##                self.father[a2] = atom
##                self.blocks(a2)
##                if self.p[a2] >= self.dfi[atom]:
##                    pop = self.stack.index(pair)
##                    self.out += [self.stack[pop:]]
##                    self.stack = self.stack[:pop]
##                self.p[atom] = min(self.p[atom], self.p[a2])

    pass # end of class ops_connected_Mixin

# end
