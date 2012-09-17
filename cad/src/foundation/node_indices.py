# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
node_indices.py

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

Utilities for finding node indices in a tree,
and using them to help move the nodes around.

(And other things useful for fixing bug 296 by moving jigs
after the chunks they connect to, or for related operations
on the node tree.)

Some of this should perhaps become Node and Group methods,
but most of it probably makes sense to leave here in its own module,
so those classes can stay small and to the point.

Module classification: in foundation, since deals with
Node trees in a sufficiently general way. [bruce 071214]
"""

from utilities.constants import common_prefix

from foundation.Group import Group # for isinstance in assertion
##from jigs import Jig # for isinstance [bruce 071214 removed this]

# quick try at fixing bug 296 for josh emergency use!
# doing it all in this file, though ideally some small part of this code
# (the part that says "isinstance", mainly) belongs in utility.py and/or
# jigs.py (but I have local mods in both those files which i am not
# ready to commit yet, thus it's easier for me to not change them now).
# [bruce 050111]

def node_position( node, root, inner_indices = []):
    """
    Given a node which is somewhere in the node-subtree rooted at root, return its "extended index",
    i.e. a list of 0 or more indices of subtrees in their dads,
    from outer to inner (like a URL with components being individual indices).
    If node is root, this extended index will be [].
    If node is *not* found anywhere under root, raise a ValueError whose detail is node's highest existing dad
    (which might be node but will not be root; it might *contain* root if root was not toplevel).
    If node is already None, that's an error (don't call us for that).
    Extend the retval by (a copy of) the given inner_indices, if supplied.
       Note that these extended indices can be used by Python functions like <, >, sort, max, etc;
    the positions that come later in the tree are larger, except that a child node position
    is larger than a parent node position, according to these Python functions.
    #doc better
    """
    if node == root:
        return list(inner_indices)
    if not node.dad:
        raise ValueError, node
    ourindex = node.dad.members.index(node) # error if we're not in it! should never happen
    return node_position( node.dad, root, [ourindex] + inner_indices)

def node_new_index(node, root, after_these):
    """
    If the given node is not already after all the nodes in after_these (a list of nodes),
    return the new position it should have (expressed in terms of current indices --
    the extended index might be different after the original node is moved,
    leaving a hole where the node used to be!). Note that this could be, but is not,
    the next possible index... the best choice is subjective, and this design decision
    of where to move it to is encoded in this function.
       If it does not need to move, return None.
       If it can't be properly moved (because it must come after things which
    are not even in the tree rooted at root), raise ValueError, with detail
    being an error message string explaining the problem.
    """
    if not after_these:
        # this test is needed, so max doesn't get a 0-length sequence
        return None
    try:
        ourpos = node_position(node, root)
    except ValueError:
        raise ValueError, node ###stub; need a better detail
            # (or make subr itself help with that? not sure it can)
    try:
        afterposns = map( lambda node1: node_position(node1, root), after_these)
    except ValueError:
        raise ValueError, node ###stub; need a better detail
    last_after = max(afterposns) # last chunk of the ones node must come after
    if ourpos > last_after:
        res = None
    else:
        ## res = just_after(last_after)
        # instead let's put it at a higher level in the tree...
        # as low as we can so that to get to its chunks, you go back
        # and then down (not up first) (where down = more indices,
        # up = fewer indices, back = last index smaller);
        # and as far back as we can.
        first_after = min(afterposns)
        # As pointed out by Huaicai, diagnosing a bug found by Ninad
        # (see Ninad's comment which reopened bug 296), the following
        # is wrong when first_after == last_after:
        ## grouppos = common_prefix( first_after, last_after )
        # Instead, we should find the innermost group equal to or containing
        # the *groups containing* those leaf node positions:
        grouppos = common_prefix( first_after[:-1], last_after[:-1] )
        # put it in that group, just after the element containing
        # the last of these two posns
        ind = last_after[len(grouppos)] + 1
        res = grouppos + [ind]
        assert is_list_of_ints(res)
    return res

def just_after(extended_index): # not presently used
    """
    return the index of the position (which may not presently exist)
    just after the given one, but at the same level
    """
    assert is_list_of_ints(extended_index)
    assert extended_index, "just_after([]) is not defined"
    return extended_index[0:-1] + [extended_index[-1] + 1]

def fix_one_node(node, root):
    """
    Given node somewhere under root, ask it whether it needs moving
    (to be after some other nodes under root), and if so, move it.
    Return value says whether we moved it.

    Error if it needs moving after some nodes *not* under root;
    in that case, raise ValueError with a suitable error message.

    @param node: a Node which might say it must follow certain other
                 nodes in the internal model tree (by returning them from
                 node.node_must_follow_what_nodes())
    @type: Node

    @param root: top of a Node tree which caller says node is in and belongs in
    @type: Node (usually or always a Group)

    @note: moving this node changes the indices in the tree of many other nodes.

    @return: 1 if we moved it, 0 if we did not. (Numbers, not booleans!)
    """
    after_these = node.node_must_follow_what_nodes()
    newpos = node_new_index( node, root, after_these)
        # might raise ValueError -- that's fine, since it implements
        # the part of our contract related to that (see its & our docstring)
    if newpos is None:
        return 0
    move_one_node(node, root, newpos)
    return 1

def move_one_node(node, root, newpos):
    """
    Move node to newpos as measured under root;
    error if node or newpos is not under root
    (but we don't promise to check whether node is);
    newpos is the old position, but it might not be the new one,
    since removing the node will change indices in the tree.
    """
    assert is_list_of_ints(newpos)
    # First find a node to move it just before,
    # or a group to make it the last child of
    # (one of these is always possible
    # unless the newpos is not valid),
    # so we can use the node or group
    # as a fixed marker, so when we remove node, this marker
    # doesn't move even though indices move.
    try:
        marker = node_at(root, newpos)
        where = 'before'
        if marker == node:
            # we are moving it to where it already is -- the one
            # (known) correct case in which the following code
            # can't work... fortunately it's also easy!
            # It's also never supposed to happen in the initial
            # use of this code (though it's legal for this func in general),
            # so (for now) print an unobtrusive warning.
            # (Later make that atom_debug only. #e)
            print "(fyi: moving node %r to where it already is in model tree)" % (node,)
            return
    except IndexError: # nothing now at that pos (or pos itself doesn't exist)
        marker = node_at(root, newpos[0:-1]) # use group as marker
        where = 'end' # works for a full or empty group
    # now remove node from where it is now
    if node.dad: # guess: this is always true (not sure; doesn't matter)
        node.dad.delmember(node)
    # now put it where it belongs, relative to marker
    if where == 'end':
        assert isinstance(marker, Group)
        marker.addchild(node) # adds at end by default
    else:
        # Warning: marker might or might not be a Group; current addmember can't handle that!
        # (That is, we want what Node.addmember (addsibling) does, never what Group.addmember (addchild) does,
        #  whether or not marker is a Group.)
        # We should (and will [and did]) fix addmember, by splitting it into new methods
        # addchild and addsibling; but until we fix it, use this kluge here:
        ## Node.addmember(marker, node, before=True)
        marker.addsibling( node, before = True) #bruce 050128 fix of reopened bug 296
            # it was reopened by my commit to Utility a few days ago
            # which changed the name of the addmember optional argument. Oops. [bruce 050128]
    return

def is_list_of_ints(thing):
    return type(thing) == type([]) and ((not thing) or \
                (type(min(thing)) == type(1) == type(max(thing))))

def node_at(root, pos):
    """
    Return the node at extended index pos, relative to root,
    or raise IndexError if nothing is there but the group
    containing that position exists,
    or if the index goes too deep
    """
    assert is_list_of_ints(pos)
    if pos == []:
        return root
    ind1, rest = pos[0], pos[1:]
    try:
        child = root.members[ind1]
    except AttributeError: # no .members
        raise IndexError, "tried to index into a leaf node"
    except IndexError: # ind1 out of range
        raise IndexError, "nothing at that position in group"
    return node_at(child, rest)

def fix_one_or_complain(node, root, errmsgfunc): # TODO: rename
    """
    [public]

    Move node to a different position under root, if it says it needs
    to come after certain other nodes under root. See self.fix_one_node
    for details. Return 1 if we moved it, 0 if we did not.

    Unlike fix_one_node (which we call to do most of our work),
    report errors by passing an error message string to errmsgfunc
    rather than by raising ValueError.

    @param node: a Node which might say it must follow certain other
                 nodes in the internal model tree (by returning them from
                 node.node_must_follow_what_nodes())
    @type: Node

    @param root: top of a Node tree which caller says node is in and belongs in
    @type: Node (usually or always a Group)

    @param errmsgfunc: function for error message output; will be passed an
                       error message string if an error occurs

    @note: external code calls this to help place a new Jig, including a Plane
           (a Jig subclass with no atoms). The Plane call is not needed (as long
           as planes have no atoms) but is harmless. [info as of 071214]
    """
    try:
        return fix_one_node(node, root)
    except ValueError, msg:
# removing this assert, since no longer needed, and has import issues
# re package classification: [bruce 071214]
##        # redundant check to avoid disaster from bugs in this new code:
##        assert isinstance(node, Jig), "bug in new code for move_jigs_if_needed -- it wants to delete non-Jig %r!" % node
        if type(msg) != type(""):
            msg = "error moving %r, deleting it instead" % msg #e improve this, or include error msg string in the exception
                # REVIEW: if msg is not a string, why does this code think it is what we were moving?
                # Is it using ValueError for what ought to be a custom exception class? [bruce 071214 Q]
        errmsgfunc(msg)
        node.kill() # delete it
        return 0
    pass

#bruce 051115 removed the following since it's no longer ever called (since workaround_for_bug_296 became a noop)
##def move_jigs_if_needed(root, errmsgfunc): # (this was the entry point for workaround_for_bug_296)
##    """move all necessary jigs under root later in the tree under root;
##    emit error messages for ones needing to go out of tree
##    (by calling errmsgfunc on error msg strings),
##    and delete them entirely;
##    return count of how many were moved (without error).
##    """
##    count = 0
##    for jig in find_all_jigs_under( root):
##        count += fix_one_or_complain(jig, root, errmsgfunc)
##    return count
##
##def find_all_jigs_under( root):
##    res = []
##    def grab_if_jig(node):
##        if isinstance(node, Jig):
##            #e logically we'd test node_must_follow_what_nodes here instead,
##            # but that's slower and not yet needed
##            res.append(node)
##    root.apply2all( grab_if_jig)
##    return res

# end
