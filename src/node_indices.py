# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
node_indices.py

Utilities for finding node indices in a tree,
and moving them around.

And other things useful for fixing bug 296 by moving jigs
after the chunks they connect to, or for related operations
on the node tree.

Some of this should become Node and Group methods,
but some of it probably makes sense in its own module like this one.
"""
__author__ = "bruce"

from Utility import *

### quick try at fixing bug 296 for josh emergency use!
# doing it all in this file, though ideally it would involve new code
# in utility and/or gadgets (but I have local mods in both those files which
# i am not ready to commit yet, thus it's easier for me to not change them now).
#  [bruce 050111]

def node_must_follow_what_nodes(node):
    """If this node is a leaf node which must come after some other leaf nodes
    due to limitations in the mmp file format, then return a list of those nodes
    it must follow; otherwise return []. For all Groups, return [].
    If we upgrade the mmp file format to permit forward refs to atoms,
    then this function could return [] for all nodes.
    """
    if isinstance(node, Jig):
        #e should make this a method in Jig, which in Node returns []
        mols = []
        for atm in node.atoms:
            mol = atm.molecule
            if mol not in mols:
                # quadratic time for huge multi-mol jigs, could use dict if that matters
                mols.append(mol)
        return mols
    return []

def node_position( node, root, inner_indices = []):
    """given a node which is somewhere in the node-subtree rooted at root, return its "extended index",
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
    """If the given node is not already after all the nodes in after_these (a list of nodes),
    return the new position it should have (expressed in terms of current indices --
    the extended index might be different after the original node is moved,
    leaving a hole where the node used to be!).
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
    if node > last_after:
        return None
    return just_after(last_after) #e we might instead want to put it at a higher level in the tree...

def just_after(extended_index):
    """return the index of the position (which may not presently exist)
    just after the given one, but at the same level
    """
    assert extended_index, "just_after([]) is not defined"
    return extended_index[0:-1] + [extended_index[-1] + 1]

def fix_one_node(node, root):
    """Given node somewhere under root, see if it needs moving
    (after some other nodes under root), and if so, move it.
    Error if it needs moving after some nodes *not* under root;
    in that case, raise ValueError with a suitable error message.
    Note that moving this node changes the indices in the tree of many other nodes.
    Return 1 if we moved it, 0 if we did not. (Numbers, not booleans!)
    """
    after_these = node_must_follow_what_nodes( node)
    newpos = node_new_index( node, root, after_these) # might raise ValueError, that's fine
    if newpos == None:
        return 0
    move_one_node(node, root, newpos)
    return 1

def move_one_node(node, root, newpos):
    """move node to newpos as measured under root;
    error if node or newpos is not under root
    (but we don't promise to check whether node is);
    newpos is the old position, may not be the new one
    since removing the node will change indices in the tree
    """
    # First find a node to move it just before,
    # or a group to make it the last child of
    # (one of these is always possible
    # unless the newpos is not valid),
    # so we can use the node or group
    # as a fixed marker, so when we remove node, this marker
    # doesn't move even though indices move.
    # That can't be done only when the newpos is in an empty group
    # (or when there is no such pos, but that's an error),
    # in which case, have an exception
    # (since I'm lazy and this case should never arise yet -- to fix
    #  it we need a third option of using the group as the marker).
    try:
        marker = node_at(root, newpos)
        where = 'before'
    except ValueError: # nothing now at that pos
        marker = node_at(root, newpos[0:-1]) # use group as marker
        where = 'end' # works for a full or empty group
    # now remove node from where it is now
    if node.dad: # guess: this is always true (not sure; doesn't matter)
        node.dad.delmember(node)
    # now put it where it belongs, relative to marker
    if where == 'end':
        assert isinstance(marker, Group)
        marker.addmember(node) # adds at end by default
    else:
        # Warning: marker might or might not be a Group; current addmember can't handle that!
        # (That is, we want what Node.addmeber does, never what Group.addmember does,
        #  whether or not marker is a Group.)
        # We should (and will) fix addmember, by splitting it into new methods
        # addchild and addsibling; but until we fix it, use this kluge here:
        Node.addmember(marker, node, before=True)
    return

def node_at(root, pos):
    "return the node at extended index pos, relative to root"
    if pos == []:
        return root
    ind1, rest = pos[0], pos[1:]
    child = root.members[ind1]
    return node_at(child, rest)

def fix_one_or_complain(node, root, msgfunc):
    try:
        return fix_one_node(node, root)
    except ValueError, msg:
        if type(msg) != type(""):
            msg = "error moving %r, deleting it instead" % msg #e improve this, or include error msg string in the exception
        msgfunc(msg)
        return 0
    pass

def fix_all(root, msgfunc):
    """move all necessary jigs under root later in the tree under root;
    emit error messages for ones needing to go out of tree
    (by calling msgfunc on error msg strings),
    and delete them entirely;
    return count of how many were moved (without error).
    """
    count = 0
    for jig in find_all_jigs_under( root):
        count += fix_one_or_complain(jig, root, msgfunc)
    return count

def find_all_jigs_under( root):
    res = []
    def grab_if_jig(node):
        if isinstance(node, Jig):
            #e logically we'd test node_must_follow_what_nodes here instead,
            # but that's slower and not yet needed
            res.append(node)
    root.apply2all( grab_if_jig)
    return res

# end
