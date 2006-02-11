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
    def selectConnected(self, atomlist=None, op='Select'):
        """Select, unselect or delete any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        
        If <atomlist> is supplied, use it instead of the currently selected atoms.
        
        <op> is an operator flag, where:
        'Select' = select all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        'Unselect' = unselect all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        'Delete' = delete all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        
        if op == 'Select': # Default
            cmd = greenmsg("Select Connected: ")
        elif op == 'Unselect':
            cmd = greenmsg("Unselect Connected: ")
        elif op == 'Delete':
            cmd = greenmsg("Delete Connected: ")
        else:
            print "Error in selectConnected(): Invalid op =", op
            #& I know there is a debug method that I should be using here.  Bruce, can you remind me?  mark 060210.
            return
        
        if atomlist is None and not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        if atomlist is None: # test for None since atomlist can be an empty list.
            atomlist = self.selatoms.values()
            
        natoms = self.marksingle(atomlist, op)
        if not natoms: return
        
        from platform import fix_plurals
        if op == 'Unselect':
            info = fix_plurals( "%d atom(s) unselected." % natoms)
        elif op == 'Delete':
            info = fix_plurals( "%d connected atom(s) deleted." % natoms)
        else: # Default
            info = fix_plurals( "%d connected atom(s) selected." % natoms)
            
        env.history.message( cmd + info)
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
    def marksingle(self, atomlist, op='Select'):
        '''Select, unselect or delete all the atoms reachable through any sequence of bonds to the atoms 
        in <atomlist> based on the operator flag <op>, where:
        
        'Select' = select all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        'Unselect' = unselect all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        'Delete' = delete all the atoms reachable through any sequence of bonds to the atoms in atomlist.
        
        Returns the number of newly selected, unselected or deleted atoms.
        '''
        marked = {} # maps id(atom) -> atom, for processed atoms
        todo = atomlist # list of atoms we must still mark and explore (recurse on all unmarked neighbors)
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
        
        n = 0
        
        for atom in marked.itervalues():
            if op == 'Unselect':
                if atom.picked:
                    n += 1
                    atom.unpick()
            elif op == 'Delete':
                n += 1
                if atom:
                    atom.kill()
            else:
                if not atom.picked:
                    n += 1
                    atom.pick()
            # note: this doesn't actually select it unless it's not a singlet and its element passes the Selection Filter.
        return n
    
    pass # end of class ops_connected_Mixin

# end