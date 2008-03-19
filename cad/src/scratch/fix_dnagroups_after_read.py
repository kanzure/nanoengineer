

$Id$

ready to move these into the target classes


    def _f_move_nonpermitted_members( self, **opts): # in class Group
        """
        [friend method for enforce_permitted_members_in_groups]

        Find all non-permitted nodes at any level inside self.
        For each such node, if it can find a home by moving higher within self,
        move it there, otherwise move it outside self, to just after self in
        self.dad (after calling self.part.ensure_toplevel_group() to make sure
         self.dad is in the same part as self). (When moving several nodes
         after self from one source, try to preserve their relative order.
         When from several sources, keep putting newly moved ones after
         earlier moved ones. This is less important than safety and efficiency.)
        
        If this makes self sufficiently invalid to need to be killed,
        it's up to the caller to find out (via _f_wants_to_be_killed)
        and kill self. We don't do this here in case the caller wants to
        defer it (though as of 080319, they don't).

        @return: whether we ejected any nodes.
        """
        have_unscanned_members = True
        move_after_this = self # a cursor in self.dad, to add new nodes after
        while have_unscanned_members:
            have_unscanned_members = False # might be changed below
            for m in self.members[:]:
                if not self.permit_as_member(m, **opts):
                    # eject m
                    if move_after_this is self:
                        self.part.ensure_toplevel_group() # must do this before first use of self.dad
                    self.dad.addchild(m, after = move_after_this) #k verify it removes m from old home == self
                    move_after_this = m
                else:
                    # keep m, but process it recursively
                    ejected_anything = m.is_group() and m._f_move_nonpermitted_members(**opts)
                        # note: if self cares about deeper (indirect) members,
                        # it would have to pass new opts to indicate this to lower levels.
                        # so far this is not needed.
                        # note: this already added the ejected nodes (if any) into self after m!
                    if ejected_anything:
                        if m._f_wants_to_be_killed(**opts):
                            m.kill()
                        have_unscanned_members = True
                        # we might (or might not) improve the ordering of moved nodes
                        # by starting over here using 'break', but in some cases
                        # this might be much slower (quadratic time or worse),
                        # so don't do it
                continue # next m
            continue # while have_unscanned_members
        
        return (move_after_this is not self) # whether anything was ejected

    def permit_as_member(self, node, pre_updaters = True, **opts): # in DnaStrandOrSegment
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]

        Does self permit node as a direct member,
        when called from enforce_permitted_members_in_groups with
        the same options as we are passed?

        @rtype: boolean

        [overrides Group method]
        """
        # someday, reject if superclass would reject -- so far, it never does
        del opts
        assy = self.assy
        res = isinstance( node, assy.DnaMarker) or \
              isinstance( node, assy.DnaLadderRailChunk) or \
              pre_updaters and isinstance( node, assy.Chunk)
        return res

    def permit_as_member(self, node, pre_updaters = True, **opts): # in Group
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]

        Does self permit node as a direct member,
        when called from enforce_permitted_members_in_groups with
        the same options as we are passed?

        @rtype: boolean

        [overridden in class DnaStrandOrSegment]
        """
        del opts
        return True

    def _f_wants_to_be_killed(self, pre_updaters = True, **opts): # in DnaStrandOrSegment
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]
        
        Does self want to be killed due to members that got ejected
        by _f_move_nonpermitted_members (or due to completely invalid structure
        from before then, and no value in keeping self even temporarily)?

        @rtype: boolean

        [overrides Group method]        
        """
        return not self.members

    def _f_wants_to_be_killed(self, pre_updaters = True, **opts): # in Group
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]
        
        Does self want to be killed due to members that got ejected
        by _f_move_nonpermitted_members (or due to completely invalid structure
        from before then, and no value in keeping self even temporarily)?

        @rtype: boolean

        [overridden in class DnaStrandOrSegment]        
        """
        return False
