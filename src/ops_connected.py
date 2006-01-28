# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_connected.py -- operations on the connectivity of bond networks.

$Id$

History:

bruce 050507 made this by collecting appropriate methods (by Josh) from class Part.

bruce 050520 added new code (mostly in a separate new file) for Select Doubly.

bruce 050629 code cleanup.

bruce 050913 used env.history in some places.
"""

__author__ = ["Josh", "bruce"]

from HistoryWidget import greenmsg, redmsg
import env

class ops_connected_Mixin:
    "Mixin for providing Select Connected and Select Doubly methods to class Part"
    
    #mark 060128 made this more general by adding the atomlist arg.
    def selectConnected(self, atomlist=None):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        If <atomlist> is supplied, use it instead of the currently selected atoms.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        
        cmd = greenmsg("Select Connected: ")
        
        if not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        if not atomlist:
            atomlist = self.selatoms.values()
            
        alreadySelected = len(self.selatoms.values())
        self.marksingle(atomlist)
        totalSelected = len(self.selatoms.values())
        
        from platform import fix_plurals
        info = fix_plurals( "%d connected atom(s) selected." % totalSelected)
        env.history.message( cmd + info)
        
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
        
        cmd = greenmsg("Select Doubly: ")
        
        if not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        alreadySelected = len(self.selatoms.values())
        from op_select_doubly import select_doubly # new code, bruce 050520
        #e could also reload it now to speed devel!
        select_doubly(self.selatoms.values()) #e optim
        totalSelected = len(self.selatoms.values())
        
        from platform import fix_plurals
        info = fix_plurals("%d new atom(s) selected (besides the %d initially selected)." % \
                               (totalSelected - alreadySelected, alreadySelected) )
        env.history.message( cmd + info)
                
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()
        return

    # == helpers for SelectConnected (for SelectDoubly, see separate file imported above)
    
    #bruce 050629 fixing bug 714 by rewriting this to make it non-recursive
    # (tho it's still non-interruptable), and fixing some other bug by making it
    # use its own dict for intermediate state, rather than atom.picked (so it works with Selection Filter).
    #mark 060128 made this more general by adding the atomlist arg.
    def marksingle(self, atomlist):
        '''select all the atoms reachable through
        any sequence of bonds to the atoms in atomlist
        '''
        marked = {} # maps id(atom) -> atom, for processed atoms
        todo = atomlist
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