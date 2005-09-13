# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_rechunk.py -- operations for changing the way atoms are divided
into chunks, without altering the atoms or bonds themselves.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce 050913 used env.history in some places.
"""

from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from chunk import molecule
from jigs import gensym # [I think this code, when in part.py, was using jigs.gensym rather than chem.gensym [bruce 050507]] 
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
        numolist=[]
        for mol in self.molecules[:]: # new mols are added during the loop!
            numol = molecule(self.assy, gensym(mol.name + "-frag"))
            for a in mol.atoms.values():
                if a.picked:
                    # leave the moved atoms picked, so still visible
                    a.hopmol(numol)
            if numol.atoms:
                numol.setDisplay(mol.display) # Fixed bug 391.  Mark 050710
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
        
        cmd = greenmsg("Merge: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to merge")
            env.history.message(cmd + msg)
            return
        self.changed() #bruce 050131 bugfix or precaution
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)

    pass # end of class ops_rechunk_Mixin

# end
