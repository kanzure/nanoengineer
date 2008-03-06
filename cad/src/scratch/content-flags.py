"""
temporary scratch file, OWNED BY BRUCE
(but if it has any imports it's fine if a file move tool rewrites them)

$Id$
"""

class Node:

    def get_atom_content(self, flags = -1):
        """
        Return your current (up to date) atom content
        which intersects the given content flags.

        @param flags:
        @type flags: an "or" of content flag bits

        @return: 
        @rtype: an "or" of content flag bits

        [subclasses which can have any atom content need to override
         this method]
        """
        # default implem, for nodes which can never have atom content
        return 0

    def _updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.
        
        [Subclasses which can contain atoms need to override this method.]
        """
        # default implem, for nodes which can never have atom content
        # (note, this default definition is needed on Node, since it's called
        #  on all members of a Group, whether or not they can contain atoms)
        return 0 

    pass



class NodeWithAtomContents(Node):

    _min_atom_content = 0
    _max_atom_content = -1 # all bits set

    def get_atom_content(self, flags = -1):
        """
        [overrides Node method]
        """
        min_content = self._min_atom_content & flags
        max_content = self._max_atom_content & flags
        if min_content != max_content:
            min_content = self._updated_atom_content() & flags
                # note: we update all of its bits, regardless of flags --
                # this might be inefficient in some cases by descending
                # into subnodes we don't care about, but on the whole
                # it seems likely to be faster, since this method
                # might be called for several disjoint flags in succession
        return min_content

    def _updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.

        [Overrides Node method. All subclasses must override this method.]
        """
        assert 0, "subclass must implement"

    def remove_some_atom_content(self, flags):
        """
        One of your kids is removing some "atom content" of the given type.
        Record and propogate the change, doing mt_update if required.
        """
        new = old = self._min_atom_content
        new &= (~flags)
        print "removed %#x from %#x to get %#x" % (flags, old, new) ###k
        removed = old - new # often 0, so we optimize for that
        if removed:
            self._min_atom_content = new
            dad = self.dad # usually present, optim for that
            if dad:
                # note: no atom content is contributed
                # directly by self -- it all comes from Atoms
                # and those are not Nodes.
                dad.remove_some_atom_content(removed)
            ### TODO: mt_update, if we are currently shown in the model tree, in a way this should change
        return
    
    def add_some_atom_content(self, flags):
        """
        One of your kids is adding some "atom content" of the given type.
        Record and propogate the change, doing mt_update if required.
        """
        # note: see implem comment in remove_some_atom_content.
        new = old = self._max_atom_content
        new |= flags
        print "added %#x to %#x to get %#x" % (flags, old, new) ###k
        added = new - old # often 0, so we optimize for that
        if added:
            self._max_atom_content = new
            dad = self.dad # usually present, optim for that
            if dad:
                # note: no atom content is contributed
                # directly by self -- it all comes from Atoms
                # and those are not Nodes.
                dad.add_some_atom_content(added)
            # todo: mt_update, if needed
        return

    pass


class Group(NodeWithAtomContents):
    
    def _updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.

        [Overrides Node method. Subclasses whose kids are not exactly
         self.members must override or extend this further.]
        """
        min_content = self._min_atom_content
        if min_content == self._max_atom_content:
            return min_content # assume these attrs are always correct
        atom_content = 0
        for member in self.members:
            atom_content |= (member._updated_atom_content())
        self._min_atom_content = atom_content
        self._max_atom_content = atom_content
        return atom_content

    pass

class Chunk(NodeWithAtomContents):

    def _updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.

        [Overrides Node method. Subclasses whose atoms are stored differently
         may need to override this further.]
        """
        } iterate over atoms

    pass

# end

        
    
