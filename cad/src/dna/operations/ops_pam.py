# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_pam.py - PAM3+5 <-> PAM5 conversion operations

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.Log import greenmsg, redmsg, orangemsg

from platform.PlatformDependent import fix_plurals
import foundation.env as env

from dna.updater.dna_updater_globals import _f_baseatom_wants_pam

from utilities.constants import MODEL_PAM3, MODEL_PAM5

class ops_pam_Mixin:
    """
    Mixin class for providing these methods to class Part
    """
    
    def convertPAM3to5Command(self):
        commandname = "Convert PAM3 to PAM5"
        which_pam = MODEL_PAM5
        self._convert_selection_to_pam_model( which_pam, commandname)
        return
    
    def convertPAM5to3Command(self):
        commandname = "Convert PAM5 to PAM3"
        which_pam = MODEL_PAM3
        self._convert_selection_to_pam_model( which_pam, commandname)
        return

    def _convert_selection_to_pam_model(self, which_pam, commandname = ""): #bruce 080413
        """
        Convert the selected atoms (including atoms into selected chunks),
        which don't have errors (in the atoms or their dnaladders), into
        the specified pam model (some, none, or all might already be
        in that pam model), along with all atoms in the same basepairs,
        but only for kinds of ladders for which conversion is yet
        implemented. Print summaries to history.

        This is a user operation, so the dna updater has run
        and knows which atoms are errors, knows ladders of atoms, etc.
        We take advantage of that to simplify the implementation.
        """
        if not commandname:
            commandname = "Convert to %s" % which_pam # kluge, doesn't matter yet
                
        # find all selected atoms (including those in selected chunks)
        atoms = dict(self.selatoms)
        for chunk in self.selmols:
            atoms.update(chunk.atoms)

        if not atoms:
            env.history.message( greenmsg(commandname + ": ") + redmsg("Nothing selected.") )
            return
        
        # expand them to cover whole basepairs -- use ladders to help?
        # (the atoms with errors are not in valid ladders, so that
        #  is also an easy way to exclude those)

        num_atoms_with_good_ladders = 0
        ladders = {}
        
        for atom in atoms.itervalues():
            try:
                ladder = atom.molecule.ladder 
            except AttributeError: # for .ladder
                continue # not the right kind of atom, etc
            if not ladder or not ladder.valid:
                continue
            if ladder.error:
                continue
            if not ladder.strand_rails: # bare axis
                continue
            num_atoms_with_good_ladders += 1
            ladders[ladder] = ladder
            # future bugfix: if atom is Pl, put neighbor Ss's into another atoms dict
            # and both their ladders into this ladders dict, then add that
            # atoms dict into atoms below ### FIX
            continue

        orig_len_atoms = len(atoms) # for history messages, in case we add some

        # now iterate on the ladders, scanning their atoms to find the ones
        # in atoms, noting every touched baseindex

        # BUG: this does not notice Pls which are in atoms without either neighbor Ss being in atoms.
        # Future: fix by noticing them above in atom loop; see comment there.

        atoms_to_convert = {}
        ladders_to_inval = {}

        number_of_basepairs_to_convert = 0
        number_of_unpaired_bases_to_convert = 0
        
        for ladder in ladders:
            # TODO: if ladder can't convert (nim for that kind of ladder),
            # say so as a summary message, and skip it. (But do we know how
            # many atoms in our dict it had? if possible, say that too.)

            # TODO: if ladder doesn't need to convert (already in desired model),
            # skip it.
            
            length = len(ladder)
            inds = {} # base indexes in ladder of basepairs which touch our dict of atoms
            rails = ladder.all_rails()
            if len(ladder.strand_rails) not in (1, 2):
                continue
            for rail in rails:
                for ind in range(length):
                    atom = rail.baseatoms[ind]
                    if atom.key in atoms:
                        # convert this base pair
                        inds[ind] = ind
                        pass
                    continue
                continue
            if len(ladder.strand_rails) == 2:
                number_of_basepairs_to_convert += len(inds)
            else:
                number_of_unpaired_bases_to_convert += len(inds)
            # conceivable that for some ladders we never hit them;
            # for now, warn but skip them in that case
            if not inds:
                print "unexpected: scanned %r but found nothing to convert (only Pls selected??)" % ladder # env.history?
            else:
                # see related code in _cmd_convert_to_pam method
                # in DnaLadder_pam_conversion.py
                ladders_to_inval[ladder] = ladder
                if 0 in inds or (length - 1) in inds:
                    for ladder2 in ladder.strand_neighbor_ladders():
                        # might contain Nones or duplicate entries
                        if ladder2 is not None:
                            ladders_to_inval[ladder2] = ladder2 # overkill if only one ind above was found
                for rail in rails:
                    baseatoms = rail.baseatoms
                    for ind in inds:
                        atom = baseatoms[ind]
                        atoms_to_convert[atom.key] = atom
                pass
            continue # next ladder

        if not atoms_to_convert:
            assert not number_of_basepairs_to_convert
            assert not number_of_unpaired_bases_to_convert
            if num_atoms_with_good_ladders < orig_len_atoms:
                # warn if we're skipping some atoms [similar code occurs twice in this method]
                msg = "%d atom(s) skipped, since not in valid, error-free DnaLadders"
                env.history.message( greenmsg(commandname + ": ") + orangemsg("Warning: " + fix_plurals(msg)))
            env.history.message( greenmsg(commandname + ": ") + redmsg("Nothing found to convert.") )
            return
        
        # print a message about what we found to convert
        what1 = what2 = ""
        if number_of_basepairs_to_convert:
            what1 = fix_plurals( "%d basepair(s)" % number_of_basepairs_to_convert )
        if number_of_unpaired_bases_to_convert:
            # doesn't distinguish sticky ends from free-floating single strands (fix?)
            what2 = fix_plurals( "%d unpaired base(s)" % number_of_unpaired_bases_to_convert )
        if what1 and what2:
            what = what1 + " and " + what2
        else:
            what = what1 + what2
        
        env.history.message( greenmsg(commandname + ": ") + "Will convert %s ..." % what )

        # warn if we're skipping some atoms [similar code occurs twice in this method]
        if num_atoms_with_good_ladders < orig_len_atoms:
            msg = "%d atom(s) skipped, since not in valid, error-free DnaLadders"
            env.history.message( orangemsg("Warning: " + fix_plurals(msg)))

        print "%s will convert %d atoms, touching %d ladders" % \
              ( commandname, len(atoms_to_convert), len(ladders_to_inval) )

        for ladder in ladders_to_inval:
            ladder._dna_updater_rescan_all_atoms()

        for atom in atoms_to_convert:
            _f_baseatom_wants_pam[atom] = which_pam

        print "about to run dna updater for", commandname
        self.assy.update_parts() # not a part method
            # (note: this catches dna updater exceptions and turns them into redmsgs.)
        print "done with dna updater for", commandname

        env.history.message( greenmsg( commandname + ": " + "Done." ))

        self.assy.w.win_update()

        return
    
    pass # end of class ops_pam_Mixin

# end

