# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_rechunk.py -- operations for changing the way atoms are divided
into chunks, without altering the atoms or bonds themselves.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce 050913 used env.history in some places.
"""

from utilities.Log import greenmsg, redmsg
from PlatformDependent import fix_plurals
from chunk import molecule
from constants import gensym
import env

class ops_rechunk_Mixin:
    "Mixin class for providing these methods to class Part"

    #m modifySeparate needs to be changed to modifySplit.  Need to coordinate
    # this with Bruce since this is called directly from some mode modules.
    # Mark 050209
    #
    # separate selected atoms into a new molecule
    # (one new mol for each existing one containing any selected atoms)
    # do not break bonds
    def modifySeparate(self, new_old_callback = None):
        """For each molecule (named N) containing any selected atoms,
           move the selected atoms out of N (but without breaking any bonds)
           into a new molecule which we name N-frag.
           If N is now empty, remove it.
           If new_old_callback is provided, then each time we create a new
           (and nonempty) fragment N-frag, call new_old_callback with the
           2 args N-frag and N (that is, with the new and old molecules).
           Warning: we pass the old mol N to that callback,
           even if it has no atoms and we deleted it from this assembly.
        """
        # bruce 040929 wrote or revised docstring, added new_old_callback feature
        # for use from Extrude.
        # Note that this is called both from a tool button and for internal uses.
        # bruce 041222 removed side effect on selection mode, after discussion
        # with Mark and Josh. Also added some status messages.
        # Questions: is it good to refrain from merging all moved atoms into one
        # new mol? If not, then if N becomes empty, should we rename N-frag to N?
        
        cmd = greenmsg("Separate: ")
        
        if not self.selatoms: # optimization, and different status msg
            msg =  redmsg("No atoms selected")
            env.history.message(cmd + msg)
            return
        if 1:
            #bruce 060313 mitigate bug 1627, or "fix it by doing something we'd rather not always have to do" --
            # create (if necessary) a new toplevel group right now (before addmol does), avoiding a traceback
            # when all atoms in a clipboard item part consisting of a single chunk are selected for this op,
            # and the old part.topnode (that chunk) disappears from loss of atoms before we add the newly made chunk
            # containing those same atoms.
            # The only things wrong with this fix are:
            # - It's inefficient (so is the main algorithm, and it'd be easy to rewrite it to be faster, as explained below).
            # - The user ends up with a new Group even if one would theoretically not have been needed.
            #   But that's better than a traceback and disabled session, so for A7 this fix is fine.
            # - The same problem might arise in other situations (though I don't know of any), so ideally we'd
            #   have a more general fix.
            # - It's nonmodular for this function to have to know anything about Parts.
            ##e btw, a simpler way to do part of the following is "part = self". should revise this when time to test it. [bruce 060329]
            someatom = self.selatoms.values()[0] # if atoms in multiple parts could be selected, we'd need this for all their mols
            part = someatom.molecule.part
            part.ensure_toplevel_group()
            # this is all a kluge; a better way would be to rewrite the main algorithm to find the mols
            # with selected atoms, only make numol for those, and add it (addmol) before transferring all the atoms to it.
            pass 
        numolist=[]
        for mol in self.molecules[:]: # new mols are added during the loop!
            numol = molecule(self.assy, gensym(mol.name + "-frag")) # (in modifySeparate)
            for a in mol.atoms.values():
                if a.picked:
                    # leave the moved atoms picked, so still visible
                    a.hopmol(numol)
            if numol.atoms:
                numol.setDisplay(mol.display) # Fixed bug 391.  Mark 050710
                numol.setcolor(mol.color) #bruce 070425, fix Extrude bug 2331 (also good for Separate in general), "nice to have" for A9
                self.addmol(numol) ###e move it to just after the one it was made from? or, end of same group??
                numolist+=[numol]
                if new_old_callback:
                    new_old_callback(numol, mol) # new feature 040929
        msg = fix_plurals("Created %d new chunk(s)" % len(numolist))
        env.history.message(cmd + msg)
        self.w.win_update() #e do this in callers instead?

    #merge selected molecules together  ###@@@ no update -- does caller do it?? [bruce 050223]
    def merge(self):
        #mark 050411 changed name from weld to merge (Bug 515)
        #bruce 050131 comment: might now be safe for clipboard items
        # since all selection is now forced to be in the same one;
        # this is mostly academic since there's no pleasing way to use it on them,
        # though it's theoretically possible (since Groups can be cut and maybe copied).
        
        cmd = greenmsg("Combine Chunks: ")

        if self.selatoms:
            self.makeChunkFromAtoms()
            return
            
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to merge")
            env.history.message(cmd + msg)
            return
        self.changed() #bruce 050131 bugfix or precaution
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)
    
    def makeChunkFromAtoms(self):
        ''' Create a new chunk from the selected atoms'''
        
        #ninad 070411 moved the original method out of 'merge' method to 
        #facilitate implementation of 'Create New Chunk 
        #from selected atoms' feature
        
        cmd = greenmsg("Create New Chunk: ")
        if not self.selatoms:
            msg1 = "Create New Chunk: "
            msg2 = redmsg('Select some atoms first to create a new chunk')
            env.history.message(msg1+msg2)
            return
        
        #ninad070411 : Following checks if the selected molecules 
        #belong to more than one chunk. If they don't (i.e. if they are a part of
        # a sinle chunk, it returns from the method with proper histry msg
        
        molList = []
        for atm in self.selatoms.values():
            if not len(molList) > 1:
                mol =  atm.molecule            
                if mol not in molList:
                    molList.append(mol)     
            
        if len(molList) < 2:
            msg1 = "Create New Chunk: "
            msg2 = redmsg('Not created as the selected atoms are part of the \
            same chunk.')
            env.history.message(msg1+msg2)
            return
                    
        #bruce 060329 new feature: work on atoms too (put all selected atoms into a new chunk)
        self.ensure_toplevel_group() # avoid bug for part containing just one chunk, all atoms selected
        numol = molecule(self.assy, gensym("Chunk"))
        natoms = len(self.selatoms)
        for a in self.selatoms.values():
            # leave the moved atoms picked, so still visible
            a.hopmol(numol)
        self.addmol(numol)
            #e should we add it in the same groups (and just after the chunks) which these atoms used to belong to?
            # could use similar scheme to placing jigs...
        msg = fix_plurals("made chunk from %d atom(s)" % natoms) # len(numol.atoms) would count bondpoints, this doesn't
        msg = msg.replace('chunk', numol.name)
        env.history.message(cmd + msg)
        self.w.win_update()
        

    pass # end of class ops_rechunk_Mixin

# end
