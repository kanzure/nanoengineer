# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_connected.py -- operations on the connectivity of bond networks.

$Id$

History:

bruce 050507 made this by collecting appropriate methods (by Josh) from class Part.

bruce 050520 added new code (mostly in a separate new file) for Select Doubly.

bruce 050629 code cleanup.
"""
__author__ = "Josh"

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

    pass # end of class ops_connected_Mixin

# end
