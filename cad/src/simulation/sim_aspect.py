# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
sim_aspect.py -- represent a "simulatable aspect" (portion) of one Part,
and help with its simulation

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce, probably sometime in 2005, wrote this within runSim.py

Bruce 080321 split this into its own file
"""

from model.chem import AtomDict

from model.elements import Singlet

from utilities.constants import BONDPOINT_LEFT_OUT

from utilities.GlobalPreferences import bondpoint_policy

# has some non-toplevel imports too

# ==

debug_sim_aspect = 0 # DO NOT COMMIT with 1
    # renamed from debug_sim when this file split out of runSim.py

# ==

#obs comment:
###@@@ this will be a subclass of SimRun, like Movie will be... no, that's wrong.
# Movie will be subclass of SimResults, or maybe not since those need not be a class
# it's more like an UnderstoodFile and also an UndoableContionuousOperation...
# and it needn't mix with simruns not related to movies.
# So current_movie maybe split from last_simrun? might fix some bugs from aborted simruns...
# for prefs we want last_started_simrun, for movies we want last_opened_movie (only if valid? not sure)...

def atom_is_anchored(atom):
    """
    is an atom anchored in space, when simulated?
    """
    ###e refile as atom method?
    #e permit filtering set of specific jigs (instances) that can affect it?
    #e really a Part method??
    res = False
    for jig in atom.jigs:
        if jig.anchors_atom(atom): # as of 050321, true only for Anchor jigs
            res = True # but continue, so as to debug this new method anchors_atom for all jigs
    return res

class sim_aspect:
    """
    Class for a "simulatable aspect" (portion, more or less) of a Part.
    For now, there's only one kind (a subset of atoms, some fixed in position),
    so we won't split out an abstract class for now.
    Someday there might be other kinds, e.g. with some chunks treated
    as rigid bodies or jigs, with the sim not told about all their atoms.
    """
    # Note: as of 051115 this is used for Adjust Selection and/or Adjust All
    # and/or possibly Minimize, but not for Run Dynamics [using modern names
    # for these features, 080321, but not reverifying current usage];
    # verified by debug_sim_aspect output.
    # WARNING: this class also assumes internally that those are its only uses,
    # by setting mapping.min = True.
    def __init__(self, part, atoms,
                 cmdname_for_messages = "Minimize",
                 anchor_all_nonmoving_atoms = False
                ):
        #bruce 051129 passing cmdname_for_messages
        #bruce 080513 passing anchor_all_nonmoving_atoms
        """
        atoms is a list of atoms within the part (e.g. the selected ones,
        for Minimize Selection); we copy it in case caller modifies it later.
        [Note that this class has no selection object and does not look at
        (or change) the "currently selected" state of any atoms,
        though some of its comments are worded as if it did.]
           We become a simulatable aspect for simulating motion of those atoms
        (and of any singlets bonded to them, since user has no way to select
        those explicitly),
        starting from their current positions, with a "boundary layer" of other
        directly bonded atoms (if any) held fixed during the simulation.
        [As of 050408 this boundary will be changed from thickness 1 to thickness 2
         and its own singlets, if any, will also be anchored rather than moving.
         This is because we're approximating letting the entire rest of the Part
         be anchored, and the 2nd layer of atoms will constrain bond angles on the
         first layer, so leaving it out would be too different from what we're
         approximating.]
        (If any given atoms have Anchor jigs, those atoms are also treated as
        boundary atoms and their own bonds are only explored to an additional depth
        of 1 (in terms of bonds) to extend the boundary.
        So if the user explicitly selects a complete boundary of Anchored atoms,
        only their own directly bonded real atoms will be additionally anchored.)
           All atoms not in our list or its 2-thick boundary are ignored --
        so much that our atoms might move and overlap them in space.
           We look at jigs which attach to our atoms,
        but only if we know how to sim them -- we might not, if they also
        touch other atoms. For now, we only look at Anchor jigs (as mentioned
        above) since this initial implem is only for Minimize. When we have
        Simulate Selection, this will need revisiting. [Update: we also look at
        other jigs, now that we have Enable In Minimize for motors.]
           If we ever need to emit history messages
        (e.g. warnings) we'll do it using a global history variable (NIM)
        or via part.assy. For now [050406] none are emitted.
        """
        if debug_sim_aspect: #bruce 051115 added this
            print "making sim_aspect for %d atoms (maybe this only counts real atoms??)" % len(atoms) ###@@@ only counts real atoms??
        self.part = part
        self.cmdname_for_messages = cmdname_for_messages
        # (note: the following atomdicts are only used in this method
        #  so they don't really need to be attributes of self)
        self._moving_atoms = AtomDict()
        self._boundary1_atoms = AtomDict()
        self._boundary2_atoms = AtomDict()
        self._boundary3_atoms = AtomDict()
        assert atoms, "no atoms in sim_aspect"
        for atom in atoms:
            assert atom.molecule.part == part
            assert atom.element is not Singlet # when singlets are selectable, this whole thing needs rethinking
            if atom_is_anchored(atom):
                self._boundary1_atoms[atom.key] = atom
            else:
                self._moving_atoms[atom.key] = atom
            # pretend that all singlets of selected atoms were also selected
            # (but were not anchored, even if atom was)
            for sing in atom.singNeighbors():
                self._moving_atoms[sing.key] = sing
            ### REVIEW: also include all atoms in the same PAM basepair as atom??
        del atoms
        if anchor_all_nonmoving_atoms:
            #bruce 080513 new feature:
            # add all remaining atoms or singlets in part to _boundary1_atoms
            # (the other boundary dicts are left empty;
            #  they are used in later code but this causes no harm)
            for mol in part.molecules:
                for atom in mol.atoms.itervalues():
                    if atom.key not in self._moving_atoms:
                        # no need to check whether it's already in _boundary1_atoms
                        self._boundary1_atoms[atom.key] = atom
            pass
        else:
            # now find the boundary1 of the _moving_atoms
            for moving_atom in self._moving_atoms.values():
                for atom2 in moving_atom.realNeighbors():
                    # (not covering singlets is just an optim, since they're already in _moving_atoms)
                    # (in fact, it's probably slower than excluding them here! I'll leave it in, for clarity.)
                    if atom2.key not in self._moving_atoms:
                        self._boundary1_atoms[atom2.key] = atom2 # might already be there, that's ok
            # now find the boundary2 of the _boundary1_atoms;
            # treat singlets of boundary1 as ordinary boundary2 atoms (unlike when we found boundary1);
            # no need to re-explore moving atoms since we already covered their real and singlet neighbors
            for b1atom in self._boundary1_atoms.values():
                for atom2 in b1atom.neighbors():
                    if (atom2.key not in self._moving_atoms) and \
                       (atom2.key not in self._boundary1_atoms):
                        self._boundary2_atoms[atom2.key] = atom2 # might be added more than once, that's ok
            # now find the boundary3 of the boundary2 atoms
            # (not just PAM atoms, since even regular atoms might need this due to torsion terms)
            # [finding boundary3 is a bugfix, bruce 080507]
            for b2atom in self._boundary2_atoms.values():
                for atom3 in b2atom.neighbors():
                    if (atom3.key not in self._moving_atoms) and \
                       (atom3.key not in self._boundary1_atoms) and \
                       (atom3.key not in self._boundary2_atoms):
                        self._boundary3_atoms[atom3.key] = atom3 # might be added more than once, that's ok
            pass

        # remove singlets which we don't want to simulate
        # [bruce 080507 new feature, not fully implemented or tested]
        def fix_dict_for_singlets( dict1):
            """
            Remove atoms from dict1 which are bondpoints we want to leave out
            of this minimization or simulation.
            """
            for atom in dict1.values():
                if atom.element is Singlet:
                    policy = bondpoint_policy(atom, True)
                    if policy == BONDPOINT_LEFT_OUT:
                        ### todo: keep a count of these, or even a list
                        del dict1[atom.key]
                        # BUG: the necessary consequences of doing this
                        # (e.g. not expecting its coordinates to be present
                        #  in sim results frames or files, for some ways of
                        #  reading them, but updating their positions when
                        #  reading those files anyway, using reposition_bondpoints)
                        # are NIM as of 080603.
                        pass
                    # todo: also record lists of bondpoints to handle later
                    # in various ways, or a list of atoms whose bondpoints need repositioning
                    pass
                continue
            return
        fix_dict_for_singlets(self._moving_atoms)
        fix_dict_for_singlets(self._boundary1_atoms)
        fix_dict_for_singlets(self._boundary2_atoms)
        fix_dict_for_singlets(self._boundary3_atoms)

        # Finally, come up with a global atom order, and enough info to check our validity later if the Part changes.
        # We include all atoms (real and singlet, moving and boundary) in one list, sorted by atom key,
        # so later singlet<->H conversion by user wouldn't affect the order.
        items = self._moving_atoms.items() + \
                self._boundary1_atoms.items() + \
                self._boundary2_atoms.items() + \
                self._boundary3_atoms.items()
        items.sort()
        self._atoms_list = [atom for key, atom in items]
            # make that a public attribute? nah, use an access method
        for i in range(1, len(self._atoms_list)):
            assert self._atoms_list[i-1] is not self._atoms_list[i]
            # since it's sorted, that proves no atom or singlet appears twice
        # anchored_atoms alone (for making boundary jigs each time we write them out)
        items = self._boundary1_atoms.items() + self._boundary2_atoms.items() + self._boundary3_atoms.items()
        items.sort()
        self.anchored_atoms_list = [atom for key, atom in items]
        #e validity checking info is NIM, except for the atom lists themselves
        return

    def atomslist(self):
        return list(self._atoms_list)

    def natoms_moving(self):
        return len(self._atoms_list) - len(self.anchored_atoms_list)

    def natoms_fixed(self):
        return len(self.anchored_atoms_list)

    def nsinglets_H(self):
        """
        return number of singlets to be written as H for the sim
        """
        singlets = filter( lambda atom: atom.is_singlet(), self._atoms_list )
        return len(singlets)

    def nsinglets_leftout(self):
        """
        return number of singlets to be entirely left out of the sim input file
        """
        ### @@@ this is currently WRONG for some bondpoint_policy values;
        # REVIEW ALL USES [bruce 080507/080603 comment]

        # review: should this just be the number that were in _moving_atoms
        # (guess yes), or in other dicts too? [bruce 080507 Q]

        return 0 # for now

    def writemmpfile(self, filename, **mapping_options):
        #bruce 050404 (for most details).
        # Imitates some of Part.writemmpfile aka files_mmp_writing.writemmpfile_part.
        #e refile into files_mmp so the mmp format code is in the same place? maybe just some of it.
        # in fact the mmp writing code for atoms and jigs is not in files_mmp anyway! tho the reading code is.
        """
        write our data into an mmp file; only include just enough info to run the sim
        [###e Should we make this work even if the atoms have moved but not restructured since we were made? I think yes.
         That means the validity hash is really made up now, not when we're made.]
        """
        ## do we need to do a part.assy.update_parts() as a precaution?? if so, have to do it earlier, not now.
        from files.mmp.files_mmp_writing import writemmp_mapping
        assy = self.part.assy
        fp = open(filename, "w")
        mapping_options['min'] = True # pass min = True
        mapping = writemmp_mapping(assy, **mapping_options)
        assert mapping.min
        assert mapping.sim
            #e rename min option? (for minimize; implies sim as well;
            #   affects mapping attrnames in chem.py atom.writemmp)
            #bruce 051031 comment: it seems wrong that this class assumes min = True
            # (rather than being told this in __init__). ###@@@
        mapping.set_fp(fp)
        # note that this mmp file doesn't need any grouping or chunking info at all.
        try:
            mapping.write_header() ###e header should differ in this case
            ## node.writemmp(mapping)
            self.write_atoms(mapping)
            self.write_anchors(mapping)
            self.write_minimize_enabled_jigs(mapping)
            mapping.write("end mmp file for %s (%s)\n" % (self.cmdname_for_messages, assy.name) ) #bruce 051129 revised this
                # sim & cad both ignore text after 'end'
                #bruce 051115: fixed this file comment, since this code is also used for Minimize All.
        except:
            mapping.close(error = True)
            raise
        else:
            mapping.close()
        return
    def write_atoms(self, mapping):
        for atom in self._atoms_list: # includes both real atoms and singlets, both moving and anchored, all sorted by key
            atom.writemmp( mapping) # mapping.sim means don't include any info not relevant to the sim
                # Note: this method knows whether & how to write a Singlet as an H (repositioned)!
                # Note: this writes bonds, but only after their 2nd atom gets written.
                # therefore it will end up only writing bonds for which both atoms get written.
                # That should be ok (within Adjust Selection) since atoms with two few bonds
                # will be anchored. [bruce 080321 comment]
    def write_anchors(self, mapping):
        from model.jigs import fake_Anchor_mmp_record
        atoms = self.anchored_atoms_list
        nfixed = len(atoms)
        max_per_jig = 20
        for i in range(0, nfixed, max_per_jig): # starting indices of jigs for fixed atoms
            indices = range( i, min( i + max_per_jig, nfixed ) )
            if debug_sim_aspect:
                print "debug_sim_aspect: writing Anchor for these %d indices: %r" % (len(indices), indices)
            # now write a fake Anchor which has just the specified atoms
            these_atoms = [atoms[i] for i in indices]
            line = fake_Anchor_mmp_record( these_atoms, mapping) # includes \n at end
            mapping.write(line)
            if debug_sim_aspect:
                print "debug_sim_aspect: wrote %r" % (line,)
        return

    def write_minimize_enabled_jigs(self, mapping): # Mark 051006
        """
        Writes any jig to the mmp file which has the attr "enable_minimize" = True
        """
        assert mapping.min #bruce 051031; detected by writemmp call, below; this scheme is a slight kluge

        from model.jigs import Jig
        def func_write_jigs(nn):
            if isinstance(nn, Jig) and nn.enable_minimize:
                #bruce 051031 comment: should we exclude the ones written by write_anchors?? doesn't matter for now. ####@@@@
                if debug_sim_aspect:
                    print "The jig [", nn.name, "] was written to minimize MMP file.  It is enabled for minimize."
                nn.writemmp(mapping)
            return # from func_write_jigs only

        self.part.topnode.apply2all( func_write_jigs)
        return

    pass # end of class sim_aspect

# end
