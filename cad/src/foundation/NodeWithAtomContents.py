# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
NodeWithAtomContents.py -- abstract class for Node subclasses which
can contain Atoms.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 080305 added some abstract classes between Node and Group
in the inheritance hierarchy, of which is this one.

Bruce 080306 added atom content access & maintenance methods.
"""

from foundation.Utility import NodeWith3DContents

_superclass = NodeWith3DContents

class NodeWithAtomContents(NodeWith3DContents):
    # REVIEW: which methods can safely assert that subclass must implement?
    """
    Abstract class for Node subclasses which can contain Atoms.

    Notable subclasses include Chunk and Group.
    """
    def pickatoms(self):
        """
        [overrides Node method; subclasses must override this method]
        """
        pass ### assert 0, "subclass must implement"

    def contains_atom(self, atom):
        """
        [overrides Node method; subclasses must override this method]
        """
        assert 0, "subclass must implement"

    # == atom content access & maintenance methods [bruce 080306]

    # initial values of instance variables

    # atom content bits, minimum possible value and maximum possible value
    #
    # (When the min and max bits at the same position differ, the corresponding
    #  atom content bit is not known, and will be recomputed as needed, and
    #  stored in both instance variables. The initial values correspond to all
    #  content bits being uncertain.)

    _min_atom_content = 0 # instance variable value is always >= 0
    _max_atom_content = -1 # instance variable value might be < 0 or not

    # access

    def get_atom_content(self, flags = -1):
        """
        [overrides Node method]
        """
        min_content = self._min_atom_content & flags
        max_content = self._max_atom_content & flags
##        print "get_atom_content(%r) needs %#x, sees %#x/%#x" % \
##              (self, flags, self._min_atom_content, self._max_atom_content )
        if min_content != max_content:
            min_content = self._f_updated_atom_content() & flags
                # note: we update all of its bits, regardless of flags --
                # this might be inefficient in some cases by descending
                # into subnodes we don't care about, but on the whole
                # it seems likely to be faster, since this method
                # might be called for several disjoint flags in succession
##        print "get_atom_content(%r) returns %#x" % (self, min_content)
        return min_content

    # recomputation

    def _f_updated_atom_content(self):
        """
        Recompute, record, and return our atom content,
        optimizing this if it's exactly known on self or on any node-subtrees.

        [Overrides Node method. Subclasses whose kids are not exactly
         self.members must override or extend this further.]
        """
        min_content = self._min_atom_content
        if min_content == self._max_atom_content:
            return min_content # assume these attrs are always correct
        atom_content = self._ac_recompute_atom_content()
        assert atom_content >= 0, \
               "illegal atom content %#x computed in %r._ac_recompute_atom_content()" % \
               ( atom_content, self )
        self._min_atom_content = atom_content
        self._max_atom_content = atom_content
##        print "_f_updated_atom_content(%r) returns %#x" % (self, atom_content)
        return atom_content

    def _ac_recompute_atom_content(self):
        """
        [All subclasses must override this method.]
        """
        # NOTE: this would be named _recompute_atom_content,
        # except for a conflict with Chunk superclass InvalMixin
        # which reserves all names starting with _recompute_ for use
        # with its special rules. This should somehow be fixed or
        # worked around, e.g., use a less generic prefix in InvalMixin
        # or at least provide an "out" like defining
        # _inputs_for_xxx = _NOT_FOR_INVALMIXIN before the _recompute_
        # method. (There's a case like that in class Atom as well,
        # but it seems to cause no harm.) Right now there is no time
        # for that given that renaming this method will also work. # CLEAN UP
        # [bruce 080306]
        assert 0, "subclass must implement"

    # invalidation

    def invalidate_atom_content(self, flags = -1):
        """
        Your kids are changing internally and/or being removed/added
        more than the caller wants to keep track of, so just make
        all the given content flags uncertain (and do necessary
        propogated invalidations, including to the model tree).
        """
        # this should be optimized, but the following is correct
        # and exercises the other methods. (And for repeated invals
        # with the same flags, those calls will not recurse, and a
        # simple check here of the need to call them could prevent
        # them both [###todo].)
        self.maybe_remove_some_atom_content(flags)
        self.maybe_add_some_atom_content(flags)
        return

    def _undo_update(self): #bruce 080310
        self.invalidate_atom_content()
        _superclass._undo_update(self)
        return

    # incremental update

    def remove_some_atom_content(self, flags):
        """
        One of your kids is, or might be (it makes no difference which one
        in the "remove" case), removing some "atom content" of the given type
        (due to changes in itself, or being removed as your kid).
        Record and propogate the change, doing mt_update if required.

        @see: add_some_atom_content, maybe_add_some_atom_content

        [unlikely to be overridden in subclasses; if it is,
         override its alias maybe_remove_some_atom_content too]
        """
        # possible optimization (only worth the unclarity if this is ever
        # noticeable on a profile): just iterate up the dad chain, i.e.
        # inline the recursive calls of this method on self.dad.
        # much of this would then be doable in Pyrex.
        new = old = self._min_atom_content
        assert new >= 0
        new &= (~flags)
        assert new >= 0
        ## if (old, new) != (0, 0):
        ##     print "removed %#x from %#x to get %#x" % (flags, old, new)
        removed = old - new # often 0, so we optimize for that
            # note: subtraction makes sense for boolean flag words in this case
            # (though not in general) since new is a subset of old
        assert removed >= 0
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

    maybe_remove_some_atom_content = remove_some_atom_content

    def maybe_add_some_atom_content(self, flags):
        """
        One of your kids *might be* adding some "atom content" of the given type
        (due to changes in itself, or being added as your kid).
        Record and propogate the change, doing mt_update if required.

        @see: add_some_atom_content, remove_some_atom_content

        [unlikely to be overridden in subclasses]
        """
        # note: see possible optimization comment in remove_some_atom_content
        new = old = self._max_atom_content
        new |= flags
        ## if (old, new) != (-1, -1):
        ##     print "added %#x to %#x to get %#x" % (flags, old, new)
        added = new - old # often 0, so we optimize for that
            # note: subtraction makes sense for boolean flag words in this case
            # (though not in general) since new is a superset of old
        if added:
            self._max_atom_content = new
            dad = self.dad # usually present, optim for that
            if dad:
                # note: no atom content is contributed
                # directly by self -- it all comes from Atoms
                # and those are not Nodes.
                dad.maybe_add_some_atom_content(added)
                    #bruce 080311 fix bug 2657: add -> maybe_add
            ### TODO: mt_update, if needed
        return

    def add_some_atom_content(self, flags):
        """
        One of your kids *is* adding some "atom content" of the given type
        (due to changes in itself, or being added as your kid).
        Record and propogate the change, doing mt_update if required.

        @note: unlike maybe_add_some_atom_content, in this case we can add bits
               to self._min_atom_content as well as self._max_atom_content.

        @see: maybe_add_some_atom_content, remove_some_atom_content

        [unlikely to be overridden in subclasses]
        """
        # note: see possible optimization comment in remove_some_atom_content
        assert flags >= 0

        new_max = old_max = self._max_atom_content
        new_max |= flags
        ## if (old_max, new_max) != (-1, -1):
        ##     print "max: added %#x to %#x to get %#x" % (flags, old_max, new_max)
        added_max = new_max - old_max # often 0, so we optimize for that

        new_min = old_min = self._min_atom_content
        new_min |= flags
        assert new_min >= 0
        ## if (old_min, new_min) != (-1, -1):
        ##     print "min: added %#x to %#x to get %#x" % (flags, old_min, new_min)
        added_min = new_min - old_min # often 0, so we optimize for that

        if added_max or added_min:
            self._max_atom_content = new_max
            self._min_atom_content = new_min
            dad = self.dad # usually present, optim for that
            if dad:
                dad.add_some_atom_content(added_max | added_min)
            ### TODO: mt_update, if needed
        return

    pass # end of class NodeWithAtomContents

# end
