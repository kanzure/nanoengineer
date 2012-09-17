# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Node_as_MT_DND_Target.py -- controller for a Node as a Model Tree DND target

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 071025 moved these methods from class Node
and class ClipboardShelfGroup (where I'd written them long ago)
into this new controller class, to remove an import from class Node
to ops_copy. I left behind only a new Node API method this needs
to call, drop_on_should_autogroup.

TODO:

- drop_under is not finished or called (for drop between nodes)

- this uses 3 different ways of asking whether something is a Group!

- there's a longstanding request to revise the position under a group
into which a node gets dropped (from new last child to new first child,
I think). It has a bug number. One motivation is that there is some
place it's not possible to drop a node unless this is revised,
described in the bug report.
"""

from foundation.Group import Group # for isinstance and for autogrouping; could remove by
    # asking the assy (and/or the dropped on node) to do the grouping

from operations.ops_copy import copy_nodes_in_order
from operations.ops_copy import copied_nodes_for_DND

import foundation.env as env

from utilities.GlobalPreferences import pref_drop_onto_Group_puts_nodes_at_top

# ==

class MT_DND_Target_API(object):
    # a stub; intent is to fill it in with default methods
    # (which fail if implems are required)
    # which specify the api used by our subclass below;
    # this doesn't matter much until we get more than one subclass
    # or the api gets more complicated.
    pass

# ==

class Node_as_MT_DND_Target( MT_DND_Target_API):
    """
    Control the use of a node as a Model Tree DND target.
    Can be used as a flyweight class, since it contains no state.
    """
    def __init__(self, node):
        """
        @param node: one node (leaf or Group) currently displayed in the
                     model tree.
        @type node: Node (can be Group or not).
        """
        self.node = node

    def drop_on_ok(self, drag_type, nodes): #bruce 080303 revised return value
        """
        Say whether "drag and drop" should be allowed to drop the given set
        of nodes onto self.node, when they are dragged in the given way
        ('move' or 'copy' -- nodes arg has the originals, not the copies),
        and if not, why not.

        (Typically, self.node (if it says ok by returning True from this method)
        would insert the moved or copied nodes inside itself as new members,
        or below itself as new siblings if it's a leaf node (until we support
        dropping into gaps between nodes for that), if they were actually
        dropped. For that see drop_on.)

        @return: ( ok, whynot ), i.e. (False, whynot) or (True, arbitrary).
        @rtype: 2-tuple of ( boolean, string), with string suitable for use
                in a statusbar message.

        [some subclasses should override this]
        """
        # someday: return ( True, what ) where what describes what we would do,
        # for use in statusbar message while user mouses over a drop point.
        #
        #bruce 050216 add exception for cycle-forming request ### needs testing
        # (to fix bug 360 item 6 comment 9, which had been fixed in the old MT's
        #  DND code too)
        if drag_type == 'move':
            for node in nodes:
                if (node is not self.node and node.is_ascendant(self.node)) or \
                   (node is self.node and node.MT_DND_can_drop_inside()):
                    print "fyi: refusing drag-move since it would form a cycle"
                    whynot = "would form a cycle"
                    return ( False, whynot )
        return ( True, None)
            # someday: probably change to False for leaf nodes, once we support
            # dropping into gaps

    def drop_on(self, drag_type, nodes): ###@@@ needs a big cleanup
        # todo: also return description of what we did (for statusbar text)
        # [bruce 080303 comment]
        """
        After a "drag and drop" of type 'move' or 'copy' (according to
        drag_type), perform the drop of the given list of nodes
        onto self.node. The list always contains the original nodes --
        for drag_type == 'copy', this method should make the copies itself.

        Exactly how to do this depends on whether self.node is a leaf or group;
        subclasses of Node can override this to change the UI behavior.
        (As of 050307, only the Clipboard overrides this. Update 071025:
        that's now done by an 'if' statement in the following method,
        which calls self.node.drop_on_should_autogroup, which is what
        the Clipboard overrides.)

        @return: list of new nodes made by this operation, which is [] if it
                 didn't make any (making them is normal for copy, but can also
                 happen in some cases for move)
        @rtype: list of nodes
        """
        will_drop_inside = self.node.MT_DND_can_drop_inside()
            # if true, nodes or their copies will become new children of self.node;
            # if false, they will become new siblings. [revised, bruce 080317]
        autogroup_at_top = will_drop_inside and \
                           self.node.drop_on_should_autogroup(drag_type, nodes)
        drop_onto_Group_at_top = pref_drop_onto_Group_puts_nodes_at_top() #bruce 080414
        if autogroup_at_top:
            #bruce 050203/080303:
            # nodes dropped onto the clipboard come from one
            # "physical space" (Part) and ought to stay that way by default;
            # user can drag them one-at-a-time if desired. (In theory this
            #  autogrouping need only be done for the subsets of them which
            #  are bonded; for now that's too hard -- maybe not for long,
            #  similar to bug 371. But this simpler behavior might be better
            #  anyway.)
            if drag_type == 'move':
                name = self.node.assy.name_autogrouped_nodes_for_clipboard( nodes, howmade = drag_type )
                new = Group(name, self.node.assy, None)
                for node in nodes[:]: #bruce 050216 don't reverse the order, it's already correct
                    node.unpick() #bruce 050216; don't know if needed or matters; 050307 moved from after to before moveto
                    node.moveto(new) ####@@@@ guess, same as in super.drop_on (move here, regardless of drag_type? no, not correct!)
                nodes = [new] # a new length-1 list of nodes
                env.history.message( "(fyi: Grouped some nodes to keep them in one clipboard item)" ) ###e improve text
            else:
                # the above implem is wrong for copy, so we handle it differently below,
                # when autogroup_at_top and drag_type != 'move'
                pass
            pass
        #e rewrite to use copy_nodes (nim)? (also rewrite the assy methods? not for alpha)

        res = [] #bruce 050203: return any new nodes this creates (toplevel nodes only, for copied groups)

        #bruce 050216: order is correct if you're dropping on a group, but (for the ops used below)
        # wrong if you're dropping on a node. This needs a big cleanup, but for now, use this kluge
        # [revised to fix bug 2403 (most likely, this never worked as intended for copy until now), bruce 070525]:

        if not will_drop_inside:
            # drops on nodes which act like leaf nodes are placed after them,
            # when done by the methods named in the following flags,
            # so to drop several nodes in a row and preserve order,
            # drop them in reverse order -- but *when* we reverse them
            # (as well as which method we use) depends on whether we're
            # doing move or copy, so these flags are used in the right
            # place below.
##            reverse_moveto = True

            reverse_addmember = True # for either addchild or addsibling
            pass
        else:
            # will_drop_inside is True
            #
            # drops on groups which accept drops inside themselves
            # go at the end of their members,
            # when done by those methods, so *don't* reverse node order --
            # UNLESS drop_onto_Group_at_top is set, which means, we put nodes dropped
            # on groups at the beginning of their members list.
            # REVIEW: are there any other things that need to be changed for that? ###

            ## assert not debug_pref_DND_drop_at_start_of_groups()
##            reverse_moveto = drop_onto_Group_at_top

            reverse_addmember = drop_onto_Group_at_top

            #bruce 060203 removing this, to implement one aspect of NFR 932:
            ## self.node.open = True # open groups which have nodes dropped on them [bruce 050528 new feature]
            pass

        if drag_type == 'move':
            # TODO: this code is now the same as the end of the copy case;
            # after the release, clean this up by moving the common code
            # outside of (after) this move/copy 'if' statement.
            # [bruce 080414 comment]

            if reverse_addmember: # [bruce 080414 post-rc0 code cleanup: reverse_moveto -> reverse_addmember]
                nodes = nodes[::-1]
            for node in nodes[:]:
                ## node.moveto(self.node)
                if will_drop_inside:
                    self.node.addchild(node, top = drop_onto_Group_at_top)
                else:
                    self.node.addsibling(node, before = False)
                continue
            pass

        else:
            #bruce 050527 [revised 071025] this uses copied_nodes_for_DND,
            # new code to "copy anything". That code is preliminary
            # (probably not enough history messages, or maybe sometimes
            # too many). It would be better to create the Copier object
            # (done in that subr?) earlier, when the drag is started,
            # for various reasons mentioned elsewhere.
            # update 071025: autogroup_at_top is now set at start of this method
            ## autogroup_at_top = isinstance(self.node, ClipboardShelfGroup)
                #####@@@@@ kluge! replace with per-group variable or func.
                #e or perhaps better, a per-group method to process the nodes list, eg to do the grouping
                # as the comment in copied_nodes_for_DND or its subr suggests.

            nodes = copied_nodes_for_DND(nodes, autogroup_at_top = autogroup_at_top)
                # Note: this ignores order within input list of nodes, using only their MT order
                # to affect the order of copied nodes which it returns. [bruce 070525 comment]
            if not nodes: # might be None
                return res # return copied nodes [bruce 080414 post-rc0 code cleanup: [] -> res]

            res.extend(nodes)

            # note: the following code is the same in the move/copy cases;
            # see above for more about this.
            if reverse_addmember:
                nodes = nodes[::-1]
                    # note: if autogroup_at_top makes len(nodes) == 1, this has no effect,
                    # but it's harmless then, and logically best to do it whenever using
                    # addmember on list elements.
            for node in nodes[:]:
                # node is a "copied node" [bruce 080414 post-rc0 code cleanup: renamed nc -> node]
                ## self.node.addmember(node) # self.node is sometimes a Group,
                ##     # so this does need to be addmember (not addchild or addsibling)
                if will_drop_inside:
                    self.node.addchild(node, top = drop_onto_Group_at_top)
                else:
                    self.node.addsibling(node, before = False)
                continue
            pass

        self.node.assy.update_parts() #e could be optimized to scan only what's needed (same for most other calls of update_parts)

        return res

    # Note: the methods drop_under_ok and drop_under are never called
    # (and drop_under is not fully implemented, as its comments indicate),
    # but they should be kept around -- they are a partly-done implementation
    # of an API extension to support Model Tree DND to points between nodes
    # (as opposed to DND to points on top of single nodes, which is all the MT
    #  can do now). [bruce 050203/070703]
    # Update, bruce 071025: if these methods become real, they might end up as the
    # drop_on methods of a different controller, InterNodeGap_as_MT_DND_Target or so.

    def drop_under_ok(self, drag_type, nodes, after = None): ###@@@ todo: honor it!
        """
        Say whether it's ok to drag these nodes (using drag_type)
        into a child-position under self.node,
        either after the given child 'after'
        or (by default) as the new first child.

        Tree widgets can use this to offer drop-points shown in gaps
        between existing adjacent nodes.
        [some subclasses should override this]
        """
        return self.node.MT_DND_can_drop_inside()

    # See comment above for status of unused method 'drop_under', which should be kept around. [bruce 070703]
    def drop_under(self, drag_type, nodes, after = None): #e move to Group[obs idea?], implem subrs, use ###@@@
        """
        #doc
        """
        if drag_type == 'copy':
            nodes = copy_nodes_in_order(nodes) # make a homeless copy of the set (someday preserving inter-node bonds, etc)
        for node in nodes:
            self.node.addchildren(nodes, after = after) ###@@@ IMPLEM (and make it not matter if they are homeless? for addchild)
        return

    pass

# ==

# not yet used, but might be someday:
#
##from debug_prefs import debug_pref, Choice_boolean_False ##, Choice_boolean_True
##    # this is not really needed, can remove if necessary
##
##def debug_pref_DND_drop_at_start_of_groups():
##    #bruce 070525 -- this is so we can experiment with this NFR someday.
##    # The code that needs to be affected by this is not yet implemented (but has a commented out call to it).
##    # If we implement that and it works and we like it,
##    # we'll change the default, or maybe even hardcode it, or maybe make it an official pref setting.
##    return debug_pref("DND: drop at start of groups?", Choice_boolean_False,
##                      non_debug = True, prefs_key = True)

# end
