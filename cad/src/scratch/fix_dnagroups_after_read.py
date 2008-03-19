

$Id$



def part_fix_dnagroups(part):
    """
    After part has just been read, either before or after
    update_parts and/or the dna updater has first run,
    fix the group structure of its dna-related groups
    (DnaGroup, DnaStrand, DnaSegment).

    As of 080318 this just means we make sure the only members
    of a DnaStrand or DnaSegment (i.e. a DnaStrandOrSegment)
    are chunks (any subclass) and DnaMarker jigs. The dna updater,
    run later, will make sure there is a 1-1 correspondence between
    controlling markers and DnaStrandOrSegments, and (nim?) that only
    DnaLadderRailChunks are left inside DnaStrandOrSegments.
    (It may have a bug in which a DnaStrandOrSegment containing only
    an ordinary chunk with non-PAM atoms would be left in that state.)
    """



def _find_nodes_to_eject(node):
    """
    Given nde
    alg: recurse down; when you hit DnaStrandOrSegment scan it
    and return nodes to move out of it, and caller does that,
    also scans them.

"""

    
    node.members_to_eject



    node.permit_as_member(node, pre_updaters = True) -- super permit, and fits our own criteria

    DnaStrandOrSegment only permits DnaMarker and DnaLadderRailChunk or Chunk

    node.require_as_container? (a class)
    


    def permit_as_member(self, node, pre_updaters = True): # in DnaStrandOrSegment
        """
        """
        # someday, reject if superclass would reject -- so far, it never does
        assy = self.assy
        res = isinstance( node, assy.DnaMarker) or \
              isinstance( node, assy.DnaLadderRailChunk) or \
              pre_updaters and isinstance( node, assy.Chunk)
        return res

    def permit_as_member(self, node, pre_updaters = True): # in Group
        """
        """
        return True

    def _wants_to_be_killed(self, pre_updaters = True): # in DnaStrandOrSegment
        return not self.members

    def _wants_to_be_killed(self, pre_updaters = True): # in Node or Group
        return False

    



    
    def members_not_permitted(self, pre_updaters = True):
        res = [m
               for m in self.members
               if not self.permit_as_member(m, pre_updaters = pre_updaters)]
        return res

    
    def _move_or_eject_members_recursive(self, **opts): # friend method?
        """
        For non-permitted nodes at any level inside self,
        if they can find a home by moving higher within self,
        move them, otherwise remove them from self (so they have no dad)
        and include them in our return value. If self is then sufficiently
        invalid, we might kill self (presumably only if self is empty).
        """
        keep_these = []
        return_these = []
        potential_members = list(self.members)
        while potential_members:
            m = potential_members.pop(0)
            if self.permit_as_member(m, **opts):
                ## later: keep_these.append(m) # check later whether it thinks it's still valid
                ejected = m._move_or_eject_members_recursive(**opts)
                    # note: this might have killed m, even if it didn't eject anything
                    # (which is why we have to eject members, making them homeless,
                    #  not just return them and leave them in place).
                if m._still_valid(**opts): # RENAME
                    keep_these.append(m)
                else:
                    m.kill() # which removes it from self.members BTW
                if ejected:
                    potential_members = ejected + potential_members
                pass
            else:
                } remove m from self.members, how? ###
                return_these.append(m)
            continue
        if self.members != keep_these:
            self.members = keep_these
            self.changed_members() # DOES THIS FIX THE DAD OF THE NEW MEMBERS? I DOUBT IT. ###### BUG - need a replace_members method
                # or could cheat - remove all existing, then addchild of each new one
        return return_these


    def whatever(self, **opts): # in class part
        topnode_orig = part.topnode
        ejected = part.topnode._move_or_eject_members_recursive(**opts)
        if ejected:
            ensure_toplevel_group
            addchildren ejected at end
        if not topnode_orig._still_valid(**opts):
            topnode_orig.kill()
            if ejected and len(part.topnode.members) == 1:
                part.topnode.ungroup()
                

    need simpler & less efficient.

    just move them one at a time.
    in each node, find bad ones, move them out, past it.
    keep rescanning until no change.


    def _move_or_eject_members_recursive( self, **opts): # ok to call this on topnode, i think, but if it makes a group, repeat on that
        """
        Find all non-permitted nodes at any level inside self.
        For each such node, if it can find a home by moving higher within self,
        move it there, otherwise move it outside self, to just after self in
        self.dad (after calling self.part.ensure_toplevel_group() to make sure
         self.dad is in the same part as self). (When moving several nodes
         after self from one source, preserve their relative order. When from
         several sources, keep putting newly moved ones after earlier moved
         ones.)
        
        If this makes self sufficiently invalid to need to be killed,
        it's up to the caller to find out (via xxx) and kill self. ### NIM on m

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
                    ejected_anything = m.is_group() and m._move_or_eject_members_recursive(**opts)
                        # this already added the ejected nodes (if any) into self after m!
                    if ejected_anything:
                        if m._wants_to_be_killed(**opts):
                            m.kill()
                        have_unscanned_members = True
                        # better order, perhaps, but quadratic time or worse:
                        ## break # start over at the beginning until no changes
                continue # next m
            continue # while have_unscanned_members
        return (move_after_this is not self) # whether anything was ejected
