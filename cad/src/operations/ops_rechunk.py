# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
ops_rechunk.py -- operations for changing the way atoms are divided
into chunks, without altering the atoms or bonds themselves.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050507 made this by collecting appropriate methods from class Part.
"""

from utilities.Log import greenmsg, redmsg
from platform_dependent.PlatformDependent import fix_plurals
from model.chunk import Chunk
from utilities.constants import gensym
from utilities.prefs_constants import assignColorToBrokenDnaStrands_prefs_key
from dna.model.Dna_Constants import getNextStrandColor
import foundation.env as env
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from utilities.debug import print_compact_stack
from simulation.sim_commandruns import adjustSinglet

class ops_rechunk_Mixin:
    """
    Mixin class for providing "chunking" (i.e. atom grouping) methods to
    class Part.
    """

    #m modifySeparate needs to be changed to modifySplit.  Need to coordinate
    # this with Bruce since this is called directly from some mode modules.
    # Mark 050209
    #
    # separate selected atoms into a new Chunk
    # (one new mol for each existing one containing any selected atoms)
    # do not break bonds
    def modifySeparate(self, new_old_callback = None):
        """
        For each Chunk (named N) containing any selected atoms,
        move the selected atoms out of N (but without breaking any bonds)
        into a new Chunk which we name N-frag. If N is now empty, remove it.

        @param new_old_callback: If provided, then each time we create a new
            (and nonempty) fragment N-frag, call new_old_callback with the
            2 args N-frag and N (that is, with the new and old molecules).
        @type  new_old_callback: function

        @warning: we pass the old mol N to that callback, even if it has no
                  atoms and we deleted it from this assembly.
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
            numol = Chunk(self.assy, gensym(mol.name + "-frag", self.assy)) # (in modifySeparate)
            for a in mol.atoms.values():
                if a.picked:
                    # leave the moved atoms picked, so still visible
                    a.hopmol(numol)
            if numol.atoms:
                numol.setDisplayStyle(mol.display) # Fixed bug 391.  Mark 050710
                numol.setcolor(mol.color, repaint_in_MT = False)
                    #bruce 070425, fix Extrude bug 2331 (also good for Separate in general), "nice to have" for A9
                self.addmol(numol) ###e move it to just after the one it was made from? or, end of same group??
                numolist+=[numol]
                if new_old_callback:
                    new_old_callback(numol, mol) # new feature 040929
        msg = fix_plurals("Created %d new chunk(s)" % len(numolist))
        env.history.message(cmd + msg)
        self.w.win_update() #e do this in callers instead?


    #merge selected molecules together  ###@@@ no update -- does caller do it?? [bruce 050223]
    def merge(self):
        """
        Merges selected atoms into a single chunk, or merges the selected
        chunks into a single chunk.

        @note: If the selected atoms belong to the same chunk, nothing happens.
        """
        #mark 050411 changed name from weld to merge (Bug 515)
        #bruce 050131 comment: might now be safe for clipboard items
        # since all selection is now forced to be in the same one;
        # this is mostly academic since there's no pleasing way to use it on them,
        # though it's theoretically possible (since Groups can be cut and maybe copied).

        cmd = greenmsg("Combine Chunks: ")

        if self.selatoms:
            self.makeChunkFromSelectedAtoms()
            return

        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to merge")
            env.history.message(cmd + msg)
            return
        self.changed() #bruce 050131 bugfix or precaution
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)

    def makeChunkFromSelectedAtoms(self):
        """
        Create a new chunk from the selected atoms.
        """

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
        numol = Chunk(self.assy, gensym("Chunk", self.assy))
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

    def makeChunkFromAtomList(self,
                              atomList,
                              name = None,
                              group = None,
                              color = None):
        """
        Creates a new chunk from the given atom list.

        @param atomList: List of atoms from which to create the chunk.
        @type  atomList: list

        @param name: Name of new chunk. If None, we'll assign one.
        @type  name: str

        @param group: The group to add the new chunk to. If None, the new chunk
                      is added to the bottom of the model tree.
        @type  group: L{Group}

        @param color: Color of new chunk. If None, no chunk color is assigned
                      (chunk atoms will be drawn in their element colors).
        @type  color: tuple

        @return: The new chunk.
        @rtype:  L{Chunk}

        """
        assert atomList

        if name:
            newChunk = Chunk(self.assy, name)
        else:
            newChunk = Chunk(self.assy, gensym("Chunk", self.assy))

        for a in atomList:
            a.hopmol(newChunk)

        if group is not None:
            group.addchild(newChunk) #bruce 080318 addmember -> addchild
        else:
            self.addnode(newChunk)

        newChunk.setcolor(color, repaint_in_MT = False)

        return newChunk

    def makeStrandChunkFromBrokenStrand(self, x1, x2): # by Mark
        """
        Makes a new strand chunk using the two singlets just created by
        busting the original strand, which is now broken. If the original
        strand was a ring, no new chunk is created.

        The new strand chunk, which includes the atoms between the 3' end of
        the original strand and the new 5' end (i.e. the break point), is
        added to the same DNA group as the original strand and assigned a
        different color.

        @param x1: The first of two singlets created by busting a strand
                   backbone bond. It is either the 3' or 5' open bond singlet,
                   but we don't know yet.
        @type  x1: L{Atom}

        @param x2: The second of two singlets created by busting a backbone
                   backbone bond. It is either the 3' or 5' open bond singlet,
                   but we don't know yet.
        @type  x2: L{Atom}

        @return: The new strand chunk. Returns B{None} if no new strand chunk
                 is created, as is the case of a ring.
        @rtype:  L{Chunk}
        """
        minimize = debug_pref("Adjust broken strand bondpoints using minimizer?",
                          #bruce 080415 revised text (to not use the developer-
                          # jargon-only term "singlet"), changed prefs_key,
                          # and removed non_debug = True, for .rc2 release,
                          # since the repositioning bug this worked around
                          # is now fixed.
                         Choice_boolean_False,
                         prefs_key = True,
                    )

        _five_prime_atom = None
        _three_prime_atom = None

        for singlet in (x1, x2):
            adjustSinglet(singlet, minimize = minimize)
            open_bond = singlet.bonds[0]
            if open_bond.isFivePrimeOpenBond():
                _five_prime_atom = open_bond.other(singlet)
            else:
                _three_prime_atom = open_bond.other(singlet)

        # Make sure we have exactly one 3' and one 5' singlet.
        # If not, there is probably a direction error on the open bond(s)
        # that x1 and/or x2 are members of.
        if not _five_prime_atom:
            print_compact_stack("No 5' bondpoint.")
            return None
        if not _three_prime_atom:
            print_compact_stack("No 3' bondpoint.")
            return None

        atomList = self.o.assy.getConnectedAtoms([_five_prime_atom])

        if _three_prime_atom in atomList:
            # The strand was a closed loop strand, so we're done.
            return None # Since no new chunk was created.

        # See self.ensure_toplevel_group() docstring for explanation.
        self.ensure_toplevel_group()
        _group_five_prime_was_in = _five_prime_atom.molecule.dad
        if env.prefs[assignColorToBrokenDnaStrands_prefs_key]:
            _new_strand_color = getNextStrandColor(_five_prime_atom.molecule.color)
        else:
            _new_strand_color = _five_prime_atom.molecule.color
        return self.makeChunkFromAtomList(atomList,
                                          group = _group_five_prime_was_in,
                                          name = gensym("Strand"),
                                              # doesn't need "DnaStrand" or self.assy,
                                              # since not normally seen by users
                                              # [bruce 080407 comment]
                                          color = _new_strand_color)

    pass # end of class ops_rechunk_Mixin

# end
