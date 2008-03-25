# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
files_mmp_writing.py -- overall control of writing MMP files;
provides class writemmp_mapping and functions writemmpfile_assy
and writemmpfile_part.

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080304 split this out of files_mmp.py.

Note:

A lot of mmp writing code is defined in other files,
notably (but not only) for the classes Chunk, Atom, and Jig.

===

Notes by bruce 050217 about mmp file format version strings:

Specific mmp format versions used so far:

[developers: maintain this list!]

<no mmpformat record> -- before 050130 (shortly before Alpha-1 released)

  (though the format had several versions before then,
   not all upward-compatible)

'050130' -- the mmpformat record, using this format-version "050130",
were introduced just before Alpha-1 release, at or shortly after
the format was changed so that two (rather than one) NamedView (Csys) records
were stored, one for Home View and one for Last View

'050130 required; 050217 optional' -- introduced by bruce on 050217,
when the info record was added, for info chunk hotspot.
(The optional part needs incrementing whenever more kinds of info records
are interpretable, at least once per "release".)

'050130 required; 050421 optional' -- bruce, adding new info records,
namely "info leaf hidden" and "info opengroup open";
and adding "per-part views" in the initial data group,
whose names are HomeView%d and LastView%d. All these changes are
backward-compatible -- old code will ignore the new records.

'050130 required; 050422 optional' -- bruce, adding forward_ref,
info leaf forwarded, and info leaf disabled.

'050502 required' -- bruce, now writing bond2, bond3, bonda, bondg
for higher-valence bonds appearing in the model (if any). (The code
that actually writes these is not in this file.)

Actually, "required" is conservative -- these are only "required" if
higher-valence bonds are present in the model being written.

Unfortunately, we don't yet have any way to say that to old code reading the file.
(This would require declaring these new bond records in the file, using a "declare"
record known by older reading-code, and telling it (as part of the declaration,
something formal that meant) "if you see these new record types and don't understand
them, then you miss some essential bond info of the kind carried by bond1 which you
do understand". In other words, "error if you see bond2 (etc), don't understand it,
but do understand (and care about) bond1".)

'050502 required; 050505 optional' -- bruce, adding "info chunk color".

'050502 required; 050511 optional' -- bruce, adding "info atom atomtype".

Strictly speaking, these are required in the sense that the atoms in the file
will seem to have the wrong number of bonds if these are not understood. But since
the file would still be usable to old code, and no altered file would be better
for old code, we call these new records optional.

'050502 required; 050618 preferred' -- bruce, adding url-encoding of '(', ')',
and '%' in node names (so ')' is legal in them, fixing part of bug 474).
I'm calling it optional, since old code could read new files with only the
harmless cosmetic issue of the users seeing the encoded node-names.

I also decided that "preferred" is more understandable than "optional".
Nothing yet uses that word (except the user who sees this format in the
Part Properties dialog), so no harm is caused by changing it.

'050502 required; 050701 preferred' -- bruce, adding gamess jig and info gamess records.

'050502 required; 050706 preferred' -- bruce, increased precision of Linear Motor force & stiffness

'050920 required' -- bruce, save carbomeric bonds as their own bond type bondc, not bonda as before

'050920 required; 051102 preferred' -- bruce, adding "info leaf enable_in_minimize"

'050920 required; 051103 preferred' -- this value existed for some time; unknown whether the prior one actually existed or not

'050920 required; 060421 preferred' -- bruce, adding "info leaf dampers_enabled"

'050920 required; 060522 preferred' -- bruce, adding "comment" and "info leaf commentline <encoding>" [will be in Alpha8]

'050920 required; 070415 preferred' -- bruce, adding "bond_direction" record

'050920 required; 080115 preferred' -- bruce, adding group classifications DnaGroup, DnaSegment, DnaStrand, Block

'050920 required; 080321 preferred' -- bruce, adding info chunk display_as_pam, save_as_pam

===

General notes about when and how to change the mmp format version:
see a separate file, files_mmp_format_version.txt,
which may be in the same directory as this source file.
"""

MMP_FORMAT_VERSION_TO_WRITE = '050920 required; 080321 preferred'
    # this semi-formally indicates required & ideal reader versions...
    # for notes about when/how to revise this, see general notes referred to
    # at end of module docstring.

from utilities import debug_flags

from utilities.debug import print_compact_traceback

from utilities.constants import get_dispName_for_writemmp

# ==

class writemmp_mapping: #bruce 050322, to help with minimize selection and other things
    """
    Provides an object for accumulating data while writing an mmp file.
    Specifically, the object stores options which affect what's written
    [any option is allowed, so specific mmp writing methods can check it w/o this class needing to know about it],
    accumulates an encoding of atoms as numbers,
    has helper methods for using that encoding,
    writing some parts of the file;
    in future this will be able to write forward refs for jigs and save
    the unwritten jigs they refer to until they're written at the end.
    """
    
    fp = None

    def __init__(self, assy, **options):
        """
        #doc; assy is used for some side effects (hopefully that can be cleaned up).
        """
        self.assy = assy
        self.atnums = atnums = {}
        atnums['NUM'] = 0 # kluge from old code, kept for now
            #e soon change atnums to store strings, and keep 'NUM' as separate instvar
        self.options = options # as of 050422, one of them is 'leave_out_sim_disabled_nodes'; as of 051209 one is 'dict_for_stats'
        self.sim = options.get('sim', False) # simpler file just for the simulator?
        self.min = options.get('min', False) # even more simple, just for minimize?
        self.save_as_pam = options.get('save_as_pam', "") # by default, do no conversion either way
        if self.min:
            self.sim = True
        self.for_undo = options.get('for_undo', False)
        if self.for_undo:
            # Writemmp methods should work differently in several ways when we're using self to record "undo state";
            # they can also store info into the following attributes to help the corresponding reading methods.
            # (We might revise this to use a mapping subclass, but for now, I'm guessing the init arg support might be useful.)
            # (Later we're likely to split this into more than one flag, to support writing binary mmp files,
            #  differential mmp files, and/or files containing more info such as selection.)
            # [bruce 060130]
            self.aux_list = []
            self.aux_dict = {}
        self.forwarded_nodes_after_opengroup = {}
        self.forwarded_nodes_after_child = {}
        return
    
    def set_fp(self, fp):
        """
        set file pointer to write to (don't forget to call write_header after this!)
        """
        self.fp = fp
        return
    
    def write(self, lines):
        """
        write one or more \n-terminates lines (passed as a single string) to our file pointer
        """
        #e future versions might also hash these lines, to help make a movie id
        self.fp.write(lines)
        return
    
    def encode_name(self, name): #bruce 050618 to fix part of bug 474 (by supporting ')' in node names)
        "encode name suitable for being terminated by ')', as it is in the current mmp format"
        #e could extend to encode unicode chars as well
        #e could extend to encode newlines, tho we don't generally want to allow newlines in names anyway
        # The encoding used is %xx for xx the 2-digit hex ASCII code of the encoded character (like in URLs).
        # E.g. "%#x" % ord("%") => 0x25
        name = name.replace('%','%25') # this has to be done first; the other chars can be in any order
        name = name.replace('(', '%28') # not needed except to let parens in mmp files be balanced (for the sake of text editors)
        name = name.replace(')', '%29') # needed
        return name
    
    def close(self, error = False):
        if error:
            try:
                self.write("\n# error while writing file; stopping here, might be incomplete\n")
                #e maybe should include an optional error message from the caller
                #e maybe should write something formal and/or incorrect so file can't be read w/o noticing this error
            except:
                print_compact_traceback("exception writing to mmp file, ignored: ")
        self.fp.close()
        return
    
    def write_header(self):
        assy = self.assy
        # The MMP File Format is initialized here, just before we write the file.
        # Mark 050130
        # [see also the general notes and history of the mmpformat,
        # in a comment or docstring near the top of this file -- bruce 050217]
        assy.mmpformat = MMP_FORMAT_VERSION_TO_WRITE
            #bruce 050322 comment: this side effect is questionable when self.sim or self.min is True
        self.fp.write("mmpformat %s\n" % assy.mmpformat)
        
        if self.min:
            self.fp.write("# mmp file written by Adjust or Minimize; can't be read before Alpha5\n")
        elif self.sim:
            self.fp.write("# mmp file written by Simulate; can't be read before Alpha5\n")
        
        if not self.min:
            self.fp.write("kelvin %d\n" % assy.temperature)
        # To be added for Beta.  Mark 05-01-16
        ## f.write("movie_id %d\n" % assy.movieID)
        return
    
    def encode_next_atom(self, atom):
        """
        Assign the next sequential number (for use only in this writing of this mmp file)
        to the given atom; return the number AS A STRING and also store it herein for later use.
        Error if this atom was already assigned a number.
        """
        # code moved here from old atom.writemmp in chem.py
        atnums = self.atnums
        assert atom.key not in atnums # new assertion, bruce 030522
        atnums['NUM'] += 1 # old kluge, to be removed
        num = atnums['NUM']
        atnums[atom.key] = num
        assert str(num) == self.encode_atom(atom)
        return str(num)
    
    def encode_atom(self, atom):
        """
        Return an encoded reference to this atom (a short string, actually
        a printed int as of 050322, guaranteed true i.e. not "")
        for use only in the mmp file contents we're presently creating,
        or None if no encoding has yet been assigned to this atom for this
        file-writing event.

        This has no side effects -- to allocate new encodings, use
        encode_next_atom instead.

        Note: encoding is valid only for one file-writing-event,
        *not* for the same filename if it's written to again later
        (in principle, not even if the file contents are unchanged, though in
        practice, for other reasons, we try to make the encoding deterministic).
        """
        if atom.key in self.atnums:
            return str(self.atnums[atom.key])
        else:
            return None
        pass
    
    def dispname(self, display):
        """
        (replaces disp = dispNames[self.display] in older code)
        """
        if self.sim:
            disp = "-" # assume sim ignores this field
        else:
            ## disp = dispNames[display]
            disp = get_dispName_for_writemmp(display) #bruce 080324 revised
        return disp
    
    # bruce 050422: support for writing forward-refs to nodes, and later writing the nodes at the right time
    # (to be used for jigs which occur before their atoms in the model tree ordering)
    # 1. methods for when the node first wishes it could be written out
    
    past_sim_part_of_file = False # set to True by external code (kluge?)
    
    def not_yet_past_where_sim_stops_reading_the_file(self):
        return not self.past_sim_part_of_file
    
    def node_ref_id(self, node):
        return id(node)
    
    def write_forwarded_node_after_nodes( self, node, after_these, force_disabled_for_sim = False ):
        """
        Due to the mmp file format, node says it must come after the given nodes in the file,
        and optionally also after where the sim stops reading the file.
        Write it out in a nice place in the tree (for sake of old code which doesn't know it should
        be moved back into its original place), as soon in the file as is consistent with these conditions.
        In principle this might be "now", but that's an error -- that is, caller is required
        to only call us if it has to. (We might find a way to relax that condition, but that's harder
        than it sounds.)
        """
        # It seems too hard to put it in as nice a place as the old code did,
        # and be sure it's also a safe place... so let's just put it after the last node in after_these,
        # or in some cases right after where the sim stops reading (but in a legal place re shelf group structure).
        from foundation.node_indices import node_position, node_at
        root = self.assy.root # one group containing everything in the entire file
            # this should be ok even if "too high" (as when writing a single part),
            # but probably only due to how we're called ... not sure.
        if force_disabled_for_sim:
            if self.options.get('leave_out_sim_disabled_nodes',False):
                return # best to never write it in this case!
            # assume we're writing the whole assy, so in this case, write it no sooner than just inside the shelf group.
            after_these = list(after_these) + [self.assy.shelf] # for a group, being after it means being after its "begin record"
        try:
            afterposns = map( lambda node1: node_position(node1, root), after_these)
        except:
            #bruce 080325
            msg = "ignoring exception in map of node_position; won't write forwarded %r: " % node
            print_compact_traceback(msg)
            return
        after_this_pos = max(afterposns)
        after_this_node = node_at(root, after_this_pos)
        if after_this_node.is_group():
            assert after_this_node is self.assy.shelf, \
                   "forwarding to after end of a group is not yet properly implemented: %r" % after_this_node
                # (not even if we now skipped to end of that group (by pushing to 'child' not 'opengroup'),
                #  since ends aren't ordered like starts, so max was wrong in that case.)
            self.push_node(node, self.forwarded_nodes_after_opengroup, after_this_node)
        else:
            self.push_node(node, self.forwarded_nodes_after_child, after_this_node)
        return
    
    def push_node(self, node, dict1, key):
        list1 = dict1.setdefault(key, []) #k syntax #k whether pyobjs ok as keys
        list1.append(node)
        return
    
    # 2. methods for actually writing it out, when it finally can be
    
    def pop_forwarded_nodes_after_opengroup(self, og):
        return self.pop_nodes( self.forwarded_nodes_after_opengroup, og)
    
    def pop_forwarded_nodes_after_child(self, ch):
        return self.pop_nodes( self.forwarded_nodes_after_child, ch)
    
    def pop_nodes( self, dict1, key):
        list1 = dict1.pop(key, [])
        return list1
    
    def write_forwarded_node_for_real(self, node):
        self.write_node(node)
        #e also write some forward anchor... not sure if before or after... probably "after child" or "after node" (or leaf if is one)
        assert not node.is_group() # for now; true since we're only used on jigs; desirable since "info leaf" only works in this case
        self.write_info_leaf( 'forwarded', self.node_ref_id(node) )
        return
    
    def write_info_leaf( self, key, val):
        """
        write an info leaf record for key and val.
        @warning: writes str(val) for any python type of val.
        """
        val = str(val)
        assert '\n' not in val
        self.write( "info leaf %s = %s\n" % (key, val) )
        return
    
    def write_node(self, node):
        node.writemmp(self)
        return
    
    pass # end of class writemmp_mapping

# ==

# bruce 050322 revised to use mapping; 050325 split, removed assy.alist set
def writemmpfile_assy(assy, filename, addshelf = True): #e should merge with writemmpfile_part
    """
    Write everything in this assy (chunks, jigs, Groups,
    for both tree and shelf unless addshelf = False)
    into a new MMP file of the given filename.
    Should be called via the assy method writemmpfile.
    Should properly save entire file regardless of current part
    and without changing current part.
    """
    #bruce 050325 renamed this from writemmp
    # to avoid confusion with Node.writemmp.
    # Also, there's now an assy method which calls it
    # and a sister function for Parts which has a Part method.
    
    ##Huaicai 1/27/05, save the last view before mmp file saving
    #bruce 050419 revised to save into glpane's current part
    assy.o.saveLastView()

    assy.update_parts() #bruce 050325 precaution
    
    fp = open(filename, "w")

    mapping = writemmp_mapping(assy) ###e should pass sim or min options when used that way...
    mapping.set_fp(fp)

    try:
        mapping.write_header()
        assy.construct_viewdata().writemmp(mapping)
        assy.tree.writemmp(mapping)
        
        mapping.write("end1\n")
        mapping.past_sim_part_of_file = True
        
        if addshelf:
            assy.shelf.writemmp(mapping)
        
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()
    return # from writemmpfile_assy

# ==

def writemmpfile_part(part, filename, **mapping_options):
    """
    Write an mmp file for a single Part.
    """
    # todo: should merge with writemmpfile_assy
    # and/or with def writemmpfile in class sim_aspect
    #bruce 051209 added mapping_options
    # as of 050412 this didn't yet turn singlets into H;
    # but as of long before 051115 it does (for all calls -- so it would not be good to use for Save Selection!)
    part.assy.o.saveLastView() ###e should change to part.glpane? not sure... [bruce 050419 comment]
        # this updates assy.part namedView records, but we don't currently write them out below
    node = part.topnode
    assert part is node.part
    part.assy.update_parts() #bruce 050325 precaution
    if part is not node.part and debug_flags.atom_debug:
        print "atom_debug: bug?: part changed during writemmpfile_part, using new one"
    part = node.part
    assy = part.assy
    #e assert node is tree or shelf member? is there a method for that already? is_topnode?
    fp = open(filename, "w")
    mapping = writemmp_mapping(assy, **mapping_options)
    mapping.set_fp(fp)
    try:
        mapping.write_header() ###e header should differ in this case
        ##e header or end comment or both should say which Part we wrote
        node.writemmp(mapping)
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()
    return # from writemmpfile_part

# end

