"""
temporary scratch file, OWNED BY BRUCE
(but if it has any imports it's fine if a file move tool rewrites them)

$Id$
"""

class Node:

    _min_atom_content = 0
    _max_atom_content = 0
        # NOTE: subclasses which can have atom content must override
        # this default value for _max_atom_content to -1
    
    def remove_some_atom_content(self, flags):
        """
        One of your kids is removing some "atom content" of the given type.
        Record and propogate the change, doing mt_update if required.
        """
        # note: this implem is suitable for all nodes.
        # only some nodes need it, but nothing would be saved
        # by defining it only on those nodes, since it will
        # never be called on the ones that don't need it.
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
            # todo: mt_update, if we are currently shown in the/some model tree, in a way this affects
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
            # todo: mt_update, if we are currently shown in the/some model tree, in a way this affects
        return
    
    def get_atom_content(self, flags = -1):
        """
        Return your current (up to date) atom content
        which intersects the given content flags.

        @param flags:
        @type flags: an "or" of content flag bits

        @return: 
        @rtype: an "or" of content flag bits

        [Subclasses which can have any atom content need to override
         this method.]
        """
        # default implem, for nodes which can never have atom content
        return 0

    def _updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.
        
        [Subclasses which can have any atom content need to override
         this method.]
        """
        # default implem, for nodes which can never have atom content
        return 0 

    pass

class Group(Node):

    # default values of instance variables
    
    _max_atom_content = -1 # overrides default value from Node

    def get_atom_content(self, flags = -1): # WARNING: same code on Group and Chunk
        """
        Return your current (up to date) atom content
        which intersects the given content flags.

        @param flags:
        @type flags: an "or" of content flag bits

        @return: 
        @rtype: an "or" of content flag bits

        [Subclasses which can have any atom content need to override
         this method.]
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

        [Overrides Node method. Subclasses whose kids are not exactly
         self.members must override or extend this further.]
        """
        # todo: optim this on Node, put the following only on Group. Then override on Chunk. ###
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

class Chunk(Node):

    # default values of instance variables
    
    _max_atom_content = -1 # overrides default value from Node

    def get_atom_content(self, flags = -1): # WARNING: same code on Group and Chunk -- common superclass? ####
        """
        Return your current (up to date) atom content
        which intersects the given content flags.

        [Subclasses which can have any atom content need to override
         this method.]

        @param flags:
        @type flags: an "or" of content flag bits

        @return: 
        @rtype: an "or" of content flag bits
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

        [Overrides Node method. Subclasses whose atoms are stored differently
         may need to override this further.]
        """
        } iterate over atoms

    pass

# end

        
    
