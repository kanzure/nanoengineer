# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_connected.py -- operations on the connectivity of bond networks.

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050507 made this by collecting appropriate methods (by Josh) from class Part.

bruce 050520 added new code (mostly in a separate new file) for Select Doubly.

bruce 050629 code cleanup.
"""

from utilities.Log import greenmsg, redmsg
import foundation.env as env

class ops_connected_Mixin:
    "Mixin for providing Select Connected and Select Doubly methods to class Part"
    
    #mark 060128 made this more general by adding the atomlist arg.
    def selectConnected(self, atomlist = None):
        """
        Selects any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        
        @param atomlist: If supplied, use this list of atoms to select connected
                         atoms instead of the currently selected atoms.
        @type  atomlist: List of atoms.
        
        @attention: Only correctly reports the number newly selected atoms.
        """
        ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        
        cmd = greenmsg("Select Connected: ")
        
        if atomlist is None and not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        if atomlist is None: # test for None since atomlist can be an empty list.
            atomlist = self.selatoms.values()
            
        catoms = self.getConnectedAtoms(atomlist)
        if not len(catoms): 
            return
        
        natoms = 0
        for atom in catoms[:]:
            if not atom.picked:
                atom.pick()
                if atom.picked:
                    # Just in case a selection filter was applied to this atom.
                    natoms += 1
            else:
                natoms += 1 # Counts atom that is already picked.
        
        from platform_dependent.PlatformDependent import fix_plurals
        info = fix_plurals( "%d new atom(s) selected." % natoms)
        env.history.message( cmd + info)
        self.o.gl_update()
        
    def unselectConnected(self, atomlist=None):
        """
        Unselect any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        If <atomlist> is supplied, use it instead of the currently selected atoms.
        """
        cmd = greenmsg("Unselect Connected: ")
        
        if atomlist is None and not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        if atomlist is None: # test for None since atomlist can be an empty list.
            atomlist = self.selatoms.values()
            
        catoms = self.getConnectedAtoms(atomlist)
        if not len(catoms): return
        
        natoms = 0
        for atom in catoms[:]:
            if atom.picked:
                atom.unpick()
                if not atom.picked:
                    # Just in case a selection filter was applied to this atom.
                    natoms += 1 
        
        from platform_dependent.PlatformDependent import fix_plurals
        info = fix_plurals( "%d atom(s) unselected." % natoms)
        env.history.message( cmd + info)
        self.o.gl_update()
        
    def deleteConnected(self, atomlist=None): # by mark
        """
        Delete any atom that can be reached from any currently
        selected atom through a sequence of bonds, and that is acceptable to the current selection filter.
        If <atomlist> is supplied, use it instead of the currently selected atoms.
        """
        
        cmd = greenmsg("Delete Connected: ")
        
        if atomlist is None and not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        if atomlist is None: # test for None since atomlist can be an empty list.
            atomlist = self.selatoms.values()
            
        catoms = self.getConnectedAtoms(atomlist)
        if not len(catoms): return
        
        natoms = 0
        for atom in catoms[:]:
            if atom.killed():
                continue
                    #bruce 060331 precaution, to avoid counting bondpoints twice
                    # (once when atom is them, once when they die when we kill their base atom)
                    # if they can be in the passed-in list or the getConnectedAtoms retval
                    # (I don't know if they can be)
            if atom.is_singlet():
                continue #bruce 060331 precaution, related to above but different (could conceivably have valence errors w/o it)
            if atom.filtered():
                continue #bruce 060331 fix a bug (don't know if reported) by doing 'continue' rather than 'return'.
                # Note, the motivation for 'return' might have been (I speculate) to not traverse bonds through filtered atoms
                # (so as to only delete a connected set of atoms), but the old code's 'return' was not a correct
                # implementation of that, in general; it might even have deleted a nondeterministic set of atoms,
                # depending on python dict item order and/or their order of deposition or their order in the mmp file.
            natoms += 1
            atom.kill()
        
        from platform_dependent.PlatformDependent import fix_plurals
        info = fix_plurals( "%d connected atom(s) deleted." % natoms)
            #bruce 060331 comment: this message is sometimes wrong, since caller has deleted some atoms on click 1 of
            # a double click, and then calls us on click 2 to delete the atoms connected to the neighbors of those.
            # To fix this, the caller ought to pass us the number of atoms it deleted, for us to add to our number,
            # or (better) we ought to return the number we delete so the caller can print the history message itself.
        env.history.message( cmd + info)
        ## self.o.gl_update()
        self.w.win_update() #bruce 060331 possible bugfix (bug is unconfirmed) -- update MT too, in case some chunk is gone now
        return
        
    def selectDoubly(self):
        """
        Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        ###@@@ same comment about interspace bonds as in selectConnected
        
        cmd = greenmsg("Select Doubly: ")
        
        if not self.selatoms:
            msg = redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        
        alreadySelected = len(self.selatoms.values())
        from operations.op_select_doubly import select_doubly # new code, bruce 050520
        #e could also reload it now to speed devel!
        select_doubly(self.selatoms.values()) #e optim
        totalSelected = len(self.selatoms.values())
        
        from platform_dependent.PlatformDependent import fix_plurals
        info = fix_plurals("%d new atom(s) selected (besides the %d initially selected)." % \
                               (totalSelected - alreadySelected, alreadySelected) )
        env.history.message( cmd + info)
                
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()
        return

    # == helpers for SelectConnected (for SelectDoubly, see separate file imported above)
    
    def getConnectedAtoms(self, atomlist, singlet_ok = False, _return_marked = False):
        """
        Return a list of atoms reachable from all the atoms in atomlist,
        not following bonds which are "not really connected" (e.g. pseudo-DNA strand-axis bonds).
        Normally never returns singlets. Optional arg <singlet_ok> permits returning singlets.
        [Private option _return_marked just returns the internal marked dictionary
         (including singlets regardless of other options).]
        """
            
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
                    really_connected = True # will be changed to False for certain bonds below.
                    if not self.o.tripleClick:
                        # New feature:
                        # Don't consider PAM strand-axis bonds as really connected unless
                        # the user did a triple-click (on a PAM atom).
                        # (initial kluge for trying it out -- needs cleanup, generalization, 
                        # optim (use element attrs, not lists [done now]), control by option
                        # of this method, and needs to also affect
                        # neighbors_of_last_deleted_atom() in selectMode.py ###e) [bruce 070411]
                        #
                        ###e really_connected should probably be an attr of each bond,
                        # renamed to b.connected, computed from its elements, via a global helper
                        # function in bond_constants.py which computes it for a pair of atoms.
                        # Someday we might have other kinds of non-connected bonds,
                        # e.g. hydrogen bonds, or higher-level analogues of that. [bruce 070411]
                        #
                        # update:
                        # Revised for new role 'unpaired-base' -- just select connected sets of
                        # the same role, or connected bondpoints. (We have to include those even
                        # though they're not selectable, since we have an option to include them.)
                        # (Future: maybe we could generalize this to "same role or any connected
                        #  chemical atoms", but then chemical atoms could bridge otherwise-disconnected
                        #  sets of different non-None roles. Doesn't matter yet, since chemical atoms
                        #  (besides X) bonded to PAM atoms are not yet supported.)
                        # [bruce 080117]
                        if at1.element.role != at2.element.role:
                            if not at1.is_singlet() and not at2.is_singlet():
                                really_connected = False
                    if really_connected:
                        if id(at1) not in marked: #e could also check for singlets here...
                            marked[id(at1)] = at1
                            newtodo.append(at1)
                        if id(at2) not in marked:
                            marked[id(at2)] = at2
                            newtodo.append(at2)
            todo = newtodo

        if _return_marked:
            return marked # KLUGE [bruce 070411], should split out a separate method instead
                # (but this form is safer for now -- cvs merge conflicts/errors are less likely this way)
        
        alist = []
        
        for atom in marked.itervalues():
            if singlet_ok:
                alist.append(atom)
            elif not atom.is_singlet():
                alist.append(atom)
                
        return alist
        

    def getConnectedSinglets(self, atomlist):
        """
        Return a list of singlets reachable from all the atoms in atomlist.
        """
        marked = self.getConnectedAtoms( atomlist, _return_marked = True )
            # use private option of sibling method, to incorporate the new details
            # of its functionality (i.e. its meaning of "connected"/"reachable")
            # [bruce 070411]
        
        slist = []
        
        for atom in marked.itervalues():
            if atom.is_singlet():
                slist.append(atom)
                
        return slist

    
    pass # end of class ops_connected_Mixin

# end
