# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Chunk_mmp_methods.py -- Chunk mixin for methods related to mmp format
(reading or writing)

@author: Josh, Bruce
@version; $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Written over several years as part of chunk.py.

Bruce 090123 split these methods out of class Chunk in chunk.py.
(For prior svn history, see chunk.py -- this is too small
to be worth dragging along all that history via svn copy.)

TODO: 

Someday, refactor into a separate chunk-mmp-handling object.

Also review whether atoms_in_mmp_file_order belongs here,
and/or should be renamed to not be mmp-specific.

Also review whether two private methods defined in Chunk_Dna_methods,
and used only here, belong here (they are _readmmp_info_chunk_setitem_Dna
and _writemmp_info_chunk_before_atoms_Dna, and are specific to
both dna code for chunk, and mmp code).
"""

from utilities import debug_flags

class Chunk_mmp_methods:
    """
    Mixin (meant only for use by class Chunk) with all
    mmp-related methods for class Chunk.
    """
    # Note: we can't inherit Chunk's main superclass here, even though doing
    # so would make pylint much happier; see comment near beginning of class
    # Chunk_Dna_methods for why. [bruce 090123 comment]
    def readmmp_info_chunk_setitem( self, key, val, interp ): #bruce 050217, renamed 050421
        """
        This is called when reading an mmp file, for each "info chunk" record.
        Key is a list of words, val a string; the entire record format
        is presently [050217] "info chunk <key> = <val>".
        Interp is an object to help us translate references in <val>
        into other objects read from the same mmp file or referred to by it.
        See the calls of this method from files_mmp for the doc of interp methods.
           If key is recognized, set the attribute or property
        it refers to to val; otherwise do nothing.
           (An unrecognized key, even if longer than any recognized key,
        is not an error. Someday it would be ok to warn about an mmp file
        containing unrecognized info records or keys, but not too verbosely
        (at most once per file per type of info).)
        """
        didit = self._readmmp_info_chunk_setitem_Dna( key, val, interp)
        if didit:
            pass # e.g. for display_as_pam, save_as_pam
        elif key == ['hotspot']:
            # val should be a string containing an atom number referring to
            # the hotspot to be set for this chunk (which is being read from
            # an mmp file)
            (hs_num,) = val.split()
            hs = interp.atom(hs_num)
            self.set_hotspot(hs) 
                # this assertfails if hotspot is invalid 
                # [review: does caller handle that?]
        elif key == ['color']: #bruce 050505
            # val should be 3 decimal ints from 0-255;
            # colors of None are not saved since they're the default
            r, g, b = map(int, val.split())
            color = r/255.0, g/255.0, b/255.0
            self.setcolor(color, repaint_in_MT = False)
        else:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info chunk with unrecognized key %r" % (key,)
        return

    def atoms_in_mmp_file_order(self, mapping = None):
        """
        Return a list of our atoms, in the same order as they would be written
        to an mmp file produced for the given mapping (none by default)
        (which is the same order in which they occurred in one,
         *if* they were just read from one, at least for this class's
         implem of this method).

        We know it's the same order as they'd be written, since self.writemmp()
        calls this method. (Subclasses are permitted to override this method
         in order to revise the order. This can help optimize mmp writing and
         reading. It does have effects in the code when the atoms are read,
         but these are usually unimportant.)

        We know it's the same order they were just read in (if they were just
        read), since it's the order of atom.key, which is assigned successive
        values (guaranteed to sort in order) as atoms are read from the file
        and created for use in this session.

        @param mapping: writemmp_mapping being used for the writing process,
                        or None if this is not being used for mmp writing.
                        This can affect the set of atoms (and in principle,
                        their order) due to conversions requested by the
                        mapping, e.g. PAM3 -> PAM5.
        @type mapping: an instance of class writemmp_mapping, or None.

        [subclasses can override this, as described above]
    
        @note: this method is also used for non-mmp (but file-format- related)
        uses, but is still here in the mmp-specific mixin class because it has
        an mmp-related argument and is overridden by the mmp code of a
        subclass of Chunk.
        """
        #bruce 050228; revised docstring and added mapping arg, 080321
        del mapping
        # as of 060308 atlist is also sorted (so equals res), but we don't want
        # to recompute it and atpos and basepos just due to calling this. Maybe
        # that's silly and this should just return self.atlist,
        # or at least optim by doing that when it's in self.__dict__. ##e
        pairs = self.atoms.items() # key, val pairs; keys are atom.key,
            # which is an int which counts from 1 as atoms are created in one
            # session, and which is (as of now, 050228) specified to sort in
            # order of creation even if we later change the kind of value it
            # produces.
        pairs.sort()
        res = [atom for key, atom in pairs]
        return res

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """
        [overrides Node.writemmp]
        """
        disp = mapping.dispname(self.display)
        mapping.write("mol (" + mapping.encode_name(self.name) + ") " + disp + "\n")
        self.writemmp_info_leaf(mapping)
        self.writemmp_info_chunk_before_atoms(mapping)
        #bruce 050228: write atoms in the same order they were created in,
        # so as to preserve atom order when an mmp file is read and written
        # with no atoms created or destroyed and no chunks reordered, thus
        # making previously-saved movies more likely to retain their validity.
        # (Due to the .dpb format not storing its own info about atom identity.)
        #bruce 080327 update:
        # Note: these "atoms" can be of class Atom or class Fake_Pl.
        #bruce 080328: for some of the atoms, let subclasses write all
        # their bonds separately, in a more compact form.
        compact_bond_atoms = \
                           self.write_bonds_compactly_for_these_atoms(mapping)
        for atom in self.atoms_in_mmp_file_order(mapping):
            atom.writemmp(mapping,
                          dont_write_bonds_for_these_atoms = compact_bond_atoms)
                # note: this writes internal and/or external bonds,
                # after their 2nd atom is written, unless both their
                # atoms are in compact_bond_atoms. It also writes
                # bond_directions records as needed for the bonds
                # it writes.
        if compact_bond_atoms: # (this test is required)
            self.write_bonds_compactly(mapping)
        self.writemmp_info_chunk_after_atoms(mapping)
        return

    def writemmp_info_chunk_before_atoms(self, mapping): #bruce 080321
        """
        Write whatever info chunk records need to be written before our atoms
        (since their value, during mmp read, might be needed when reading the
        atoms or their bonds).

        [subclasses should extend this as needed]
        """
        self._writemmp_info_chunk_before_atoms_Dna( mapping)
        return

    def write_bonds_compactly_for_these_atoms(self, mapping): #bruce 080328
        """
        If self plans to write some of its atoms' bonds compactly
        when self.write_bonds_compactly is called
        (possibly based on options in mapping),
        then return a dictionary of atom.key  -> atom for those
        atoms. Otherwise return {}.

        [subclasses that can do this should override this method
         and write_bonds_compactly in corresponding ways.]
        """
        del mapping
        return {}

    def writemmp_info_chunk_after_atoms(self, mapping): #bruce 080321 split this out
        """
        Write whatever info chunk records should be written after our atoms
        and our internal bonds, or any other info chunk records not written
        by writemmp_info_chunk_before_atoms.

        [subclasses should override this as needed]
        """
        #bruce 050217 new feature [see also a comment added to files_mmp.py]:
        # also write the hotspot, if there is one.
        hs = self.hotspot # uses getattr to validate it
        if hs:
            # hs is a valid hotspot in this chunk, and was therefore one of the
            # atoms just written by the caller, and therefore should have an
            # encoding already assigned for the current mmp file:
            hs_num = mapping.encode_atom(hs)
            assert hs_num is not None
            mapping.write("info chunk hotspot = %s\n" % hs_num)
        if self.color:
            r = int(self.color[0]*255 + 0.5)
            g = int(self.color[1]*255 + 0.5)
            b = int(self.color[2]*255 + 0.5)
            mapping.write("info chunk color = %d %d %d\n" % (r, g, b))
        return

    def write_bonds_compactly(self, mapping): #bruce 080328
        """
        If self returned (or would return) some atoms from
        self.write_bonds_compactly_for_these_atoms(mapping),
        then write all bonds between atoms in that set
        into mapping in a compact form.

        @note: this should only be called if self did, or would,
               return a nonempty set of atoms from that method,
               self.write_bonds_compactly_for_these_atoms(mapping).

        [subclasses that can do this should override this method
         and write_bonds_compactly_for_these_atoms in corresponding ways.]
        """
        assert 0, "subclasses which need this must override it"

    pass # end of class Chunk_mmp_methods

# end
