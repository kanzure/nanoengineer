# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_pam.py - PAM3+5 <-> PAM5 conversion operations

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.Log import greenmsg, redmsg, orangemsg

from platform_dependent.PlatformDependent import fix_plurals
import foundation.env as env

from utilities.GlobalPreferences import debug_pref_enable_pam_convert_sticky_ends
from utilities.GlobalPreferences import debug_pref_remove_ghost_bases_from_pam3

from dna.updater.dna_updater_globals import _f_baseatom_wants_pam

from utilities.constants import MODEL_PAM3, MODEL_PAM5

from model.elements import Singlet, Pl5

# ==

class ops_pam_Mixin:
    """
    Mixin class for providing these methods to class Part
    """

    # these commands have toolbuttons:
    
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

    # these commands have no toolbuttons, for now,
    # and probably never should. For debugging (or in case they
    # are occasionally useful to users), they'll probably be given
    # debug menu commands.
    
    def convertPAM3to5_noghosts_Command(self): 
        commandname = "Convert PAM3 to PAM5 no ghosts"
        which_pam = MODEL_PAM5
        self._convert_selection_to_pam_model( which_pam, commandname, make_ghost_bases = False)
        return
    
    ## def convertPAM5to3_leaveghosts_Command(self): 
    ##     commandname = "Convert PAM5 to PAM3 leave ghosts"
    ##     which_pam = MODEL_PAM3
    ##     self._convert_selection_to_pam_model( which_pam, commandname, remove_ghost_bases_from_PAM3 = False)
    ##     return

    ## def makePlaceholderBasesCommand(self): ...
    # this command (to make ghost bases but do nothing else)
    # could be factored out from _convert_selection_to_pam_model below,
    # but not trivially, since all the history messages and
    # some of the return-since-no-work conditions need changes
    
    def _convert_selection_to_pam_model(self,
                                        which_pam,
                                        commandname = "",
                                        make_ghost_bases = True, # only implemented for PAM3, so far
                                        ## remove_ghost_bases_from_PAM3 = True
                                       ): #bruce 080413
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
        ghost_bases = {} # initially only holds PAM5 ghost bases
        
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
            # note: if atom is Pl, its Ss neighbors are treated specially
            # lower down in this method
            if atom.ghost and atom.element.pam == MODEL_PAM5:
                ghost_bases[atom.key] = atom
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

        ladders_needing_ghost_bases = {} # maps ladder to (ladder, list of indices) #bruce 080528
        
        for ladder in ladders:
            # TODO: if ladder can't convert (nim for that kind of ladder),
            # say so as a summary message, and skip it. (But do we know how
            # many atoms in our dict it had? if possible, say that too.)

            # TODO: if ladder doesn't need to convert (already in desired model),
            # skip it.
            
            length = len(ladder)
            index_set = {} # base indexes in ladder of basepairs which touch our dict of atoms
            rails = ladder.all_rails()
            if len(ladder.strand_rails) not in (1, 2):
                continue
            for rail in rails:
                for ind in range(length):
                    atom = rail.baseatoms[ind]
                    if atom.key in atoms:
                        # convert this base pair
                        index_set[ind] = ind
                        pass
                    continue
                continue
            # conceivable that for some ladders we never hit them;
            # for now, warn but skip them in that case
            if not index_set:
                print "unexpected: scanned %r but found nothing to convert (only Pls selected??)" % ladder # env.history?
            else:
                if len(ladder.strand_rails) == 2:
                    number_of_basepairs_to_convert += len(index_set)
                else:
                    number_of_unpaired_bases_to_convert += len(index_set)
                        # note: we do this even if the conversion will fail
                        # (as it does initially for single strand domains),
                        # since the summary error message from that is useful.
                    if make_ghost_bases and ladder.can_make_ghost_bases():
                        # initially, this test rules out free floating single strands;
                        # later we might be able to do this for them, which is why
                        # we do the test using that method rather than directly.
                        ladders_needing_ghost_bases[ladder] = (ladder, index_set.values())
                # see related code in _cmd_convert_to_pam method
                # in DnaLadder_pam_conversion.py
                ladders_to_inval[ladder] = ladder
                if 0 in index_set or (length - 1) in index_set:
                    for ladder2 in ladder.strand_neighbor_ladders():
                        # might contain Nones or duplicate entries
                        if ladder2 is not None:
                            ladders_to_inval[ladder2] = ladder2 # overkill if only one ind above was found
                for rail in rails:
                    baseatoms = rail.baseatoms
                    for ind in index_set:
                        atom = baseatoms[ind]
                        atoms_to_convert[atom.key] = atom # note: we also add ghost base atoms, below
                pass
            continue # next ladder

        if not atoms_to_convert:
            assert not number_of_basepairs_to_convert
            assert not number_of_unpaired_bases_to_convert
            assert not ladders_needing_ghost_bases
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

        # make ghost bases as needed for this conversion (if enabled -- not by default since not yet working ####)
        # (this must not delete any baseatoms in atoms, or run the dna updater
        #  or otherwise put atoms into different ladders, but it can make new
        #  atoms in new chunks, as it does)

        if debug_pref_enable_pam_convert_sticky_ends():
            for ladder, index_list in ladders_needing_ghost_bases.itervalues():
                baseatoms = ladder.make_ghost_bases(index_list) # note: index_list is not sorted; that's ok
                    # note: this makes them in a separate chunk, and returns them
                    # as an atom list, but doesn't add the new chunk to the ladder.
                    # the next dna updater run will fix that (making a new ladder
                    # that includes all atoms in baseatoms and the old ladder).
                for ind in index_list:
                    atom = baseatoms[ind]
                    atoms_to_convert[atom.key] = atom
        
        # cause the dna updater (which would normally run after we return,
        #  but is also explicitly run below) to do the rest of the conversion
        # (and report errors for whatever it can't convert)
        
        for ladder in ladders_to_inval:
            ladder._dna_updater_rescan_all_atoms()

        for atom in atoms_to_convert:
            _f_baseatom_wants_pam[atom] = which_pam

        # run the dna updater explicitly
        
        print "about to run dna updater for", commandname
        self.assy.update_parts() # not a part method
            # (note: this catches dna updater exceptions and turns them into redmsgs.)
        print "done with dna updater for", commandname

        if debug_pref_remove_ghost_bases_from_pam3():
            # note: in commented out calling code above, this was a flag
            # option, remove_ghost_bases_from_PAM3;
            # that will be revived if we have a separate command for this.
            #
            # actually we only remove the ones we noticed as PAM5 above,
            # and succeeded in converting to PAM3.
            good = bad = 0
            for atom in ghost_bases.values(): # must not be itervalues
                if atom.element.pam == MODEL_PAM3:
                    good += 1
                    for n in atom.neighbors():
                        if n.is_ghost():
                            ghost_bases[n.key] = n
                else:
                    bad += 1
                    del ghost_bases[atom.key]
                continue
            if good:
                print "removing %d ghost base(s) we converted to PAM3" % good
            if bad:
                print "leaving %d ghost base(s) we didn't convert to PAM3" % bad
            if not bool(good) == bool(ghost_bases): # should never happen
                print "bug: bool(good) != bool(ghost_bases), for", good, ghost_bases
            del good, bad
            if ghost_bases:
                for atom in ghost_bases.itervalues():
                    atom.kill()
                    # todo: probably should use prekill code to avoid
                    # intermediate bondpoint creation, even though there
                    # are not usually a lot of atoms involved at once
                    continue
                print "about to run dna updater 2nd time for", commandname
                self.assy.update_parts()
                print "done with dna updater 2nd time for", commandname
            pass

        env.history.message( greenmsg( commandname + ": " + "Done." ))

        self.assy.w.win_update()

        return
    
    pass # end of class ops_pam_Mixin

# end

