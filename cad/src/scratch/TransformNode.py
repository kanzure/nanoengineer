# Copyright 2009 Nanorex, Inc.  See LICENSE file for details.
"""
TransformNode.py -- mutable transform classes, shared by TransformNodes

NOT YET USED as of 090204... declared obsolete as of bruce 090225:

- much of the specific code is obsolete, since we abandoned the idea of a
  number-capped TransformControl object (no need to merge TCs when too many
  are used)

- the concept of a separated dynamic and static transform, and letting
  them be pointers to separate objects, potentially shared, is a good one,
  which will be used in some form if we ever optimize rigid drag of
  multiple chunks bridges by external bonds (as I hope we will),
  but there is no longer time to implement it in this form (new superclass
  for Chunk), before the next release, since it impacts too much else about
  a Chunk. If we implement that soon, it will be in some more klugy form
  which modifies Chunk to a lesser degree.

Therefore, this file (and TransformState which it uses) are now scratch files.
However, I'm leaving some comments that refer to TransformNode in place
(in still-active files), since they also help point out the code which any
other attempt to optimize rigid drags would need to modify. In those comments,
dt and st refer to dynamic transform and static transform, as used herein.

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.
"""



from foundation.state_constants import S_CHILD

from graphics.drawing.TransformControl import TransformControl

Node3D

_DEBUG = True # for now

class TransformNode(Node3D): # review superclass and its name
    """
    A Node3D which can be efficiently moved (in position and orientation)
    by modifying a contained transform. Children and control points may store
    relative and/or absolute coordinates, but the relative ones are considered
    fundamental by most operations which modify the transform (so the absolute
    ones must be invalidated or recomputed, and modifying the transform moves
    the node). (But certain operations can explicitly cause data to flow the
    other way, i.e. modify the transform and relative coordinates in such a way
    that the absolute position and coordinates remain unchanged.)

    The transform is actually the composition of two "transform components":
    an optional outer "dynamic transform" (used for efficient dragging of sets
    of TransformNodes) and an inner "static transform" (often non-identity for
    long periods, so we needn't remake or transform all affected CSDLs after
    every drag operation).

    Each transform component can be shared with other nodes. That is, several
    nodes can refer to the same mutable transform, so that changes to it affect
    all of them.

    The way self's overall transform is represented by these component
    transforms can change (by replacing one of them with a copy, and/or merging
    the dynamic transform into the static transform), without changing the
    overall transform value. We optimize for the lack of absolute position
    change in such cases.
    """

    # pointer to our current (usually shared) dynamic transform, or None.
    # (Note: this affects rendering by making sure self is in a DrawingSet
    #  which will be drawn within GL state which includes this transform.)
    dynamic_transform = None
    _s_attr_dynamic_transform = S_CHILD
        # (_s_attr: perhaps unnecessary, since no Undo checkpoints during drag)

    # pointer to our current (usually shared) static transform, or None
    # (note: affects rendering by means of an associated TransformControl,
    #  which transforms the relative coordinates used to make self's CSDLs
    #  into absolute coordinates (not counting dynamic_transform) used to draw
    #  self)
    static_transform = None
    _s_attr_static_transform = S_CHILD

    # REVIEW: does the static_transform contain its TransformControl?
    # I now think it's contained, and that we won't allocate an ST unless a
    # TC is available, and that we'll use None for the "identity ST". ####

    ### REVIEW: should we limit the set of static transforms for all purposes (incl Undo)
    # due to a limitation on the number of TransformControls which arises from the rendering implementation?
    # If we do that, should we also remake CSDLs, or just transform them (presumably no difference in end result)?
    # Note: transforming them is what requires them to have mutable TC refs -- a change to their current API. ###

    def set_dynamic_transform(self, t): # review: use a setter? the initial assert might not be appropriate then...
        #### FIX: I don't like having a setter but also allowing direct sets, like we use in other code.
        #### pick one way and always use that way. Make sure setting it does proper invals, checking t.is_identity() or t is None.
        # If I want to put off letting nodes be new-style classes, then make raw version private and use setter explicitly...
        # but I can't put that off for long, if I also want these things to act like state -- actually I can if setters do inval manually...
        # but what about usage tracking? I'd need getters which do that manually... ##### DECIDE
        # (about new-style nodes -- as of 090206 I think I've revised enough code to make them ok, but this is untested.)
        """
        """
        assert not self.dynamic_transform
        self.dynamic_transform = t
            ##### TODO: MAKE SURE this invalidates subscribers to self.dynamic_transform (our dynamic transform id),
            # but doesn't invalidate our overall transform value [###REVIEW: could it do so by using the following code?]
        assert t.is_identity()
            # if it wasn't, we'd also need to invalidate our overall transform value
        return

    ### TODO: setter for static needs to list self inside it, so it can merge with others and affect us

    def set_static_transform(self, st):
        self.static_transform.del_node(self)
        self.static_transform = st ##### TODO: MAKE SURE this invalidates subscribers to self.static_transform
        st.add_node(self)
        return

    def bridging_objects(self):
        """
        Return the list of objects which "bridge" more than one TransformNode
        including this one, and whose TransformNodes presently have different
        dynamic_transforms (not all the same one) (regardless of the current
        transform values of those dynamic transforms).
        """
        res = []
        for obj in self.potential_bridging_objects():
            if obj.is_currently_bridging_dynamic_transforms():
                res.append(obj)
        return res

    def potential_bridging_objects(self):
        """
        Return a list of objects whose coordinates depend on the value of
        self's dynamic_transform and also on the value of one or more
        other nodes' dynamic_transforms (though we don't remove the ones
        for which the other nodes depend on the *same* dynamic transform).

        (These are the objects which might get distorted due to a change
        in self's dynamic transform value, if the other nodes have different
        dynamic transforms at the time.)

        [subclasses should override as needed; overridden in class Chunk]
        """
        # note: implem is per-subclass, for now; might generalize later
        # so this class maintains a set of them -- depends on whether
        # subclasses maintain distinct custom types, as Chunk may do
        # when it has error indicators implemented similarly to ExternalBondSet;
        # right now, I don't know if they'll be kept in the same dict as it is
        # or not.
        return ()

    pass


# ==

def merge_dynamic_into_static_transform(nodes):
    """
    Given a set of TransformNodes with the same dynamic transform,
    but perhaps different static transforms, which may or may not be shared
    with nodes not in the set, remove the dynamic transform from all the nodes
    without changing their overall transforms, by merging it into their static
    transforms.

    This requires splitting any static transforms that bridge
    touched and untouched nodes (so we can merge the dynamic transform into
    only the one on the touched nodes), and if we run out of TransformControls
    needed to make more static transforms, merging some static transforms
    into the identity (and either remaking or transforming all our CSDLs,
    or invalidating them so that happens lazily).
    """
    assert nodes
    dt = nodes[0].dynamic_transform
    assert dt is not None

    for node in nodes:
        assert node.dynamic_transform is dt

    for node in nodes:
        node.dynamic_transform = None ### TODO: make this invalidate subscribers to that field

    if dt.is_identity():
        return

    # now, fold the value of dt into the static transforms on nodes,
    # splitting the ones that also cover unaffected nodes.

    # get the affected static transforms and their counts
    statics = {} # maps static transform to number of times we see it in nodes
    for node in nodes:
        st = node.static_transform # might be None
        statics.setdefault(st, 0)
        statics[st] += 1

    # see which statics straddle the boundary of our set of nodes
    # (since we'll need to split each of them in two)
    straddlers = {}
    for st, count in statics.iteritems():
        # count is the number of nodes which have st;
        # does that cover all of st's nodes?
        if st is not None:
            assert count <= st.nodecount()
            if count < st.nodecount():
                straddlers[st] = st # or store a number?
        else:
            straddlers[st] = st # None is always a straddler
        continue

    # allocate more TCs (up to the externally known global limit)
    # for making more static transforms when we split the straddlers
    want_TCs = len(straddlers)
    if want_TCs:
        new_TCs = allocate_TransformControls(want_TCs)

        if len(new_TCs) < want_TCs:
            # There are not enough new TCs to split all the straddlers,
            # so merge some statics as needed, transforming their CSDL primitives
            print "fyi: want %d new TransformControls, only %d available; merging" % \
                  (len(new_TCs), want_TCs)
            print "THIS IS NIM, BUGS WILL ENSUE"
            assert 0
            # (We're hoping that we'll find a way to allocate as many TCs as needed,
            #  so we never need to write this code. OTOH, initially we might need to
            #  make this work in the absence of any TCs, i.e. implem and always use
            #  this code, never allocating STs at all. ###)

        # now split each straddler in two, leaving the original on the "other nodes"
        # (this matters if one of them is a "permanent identity StaticTransform")

        if _DEBUG:
            print "splitting %d straddlers" % want_TCs

        replacements = {} # map old to new, for use on nodes
        for straddler, tc in zip(straddlers, new_TCs):
            # note: straddler might be None
            replacements[straddler] = StaticTransform(straddler, tc)

        for node in nodes:
            st = node.static_transform
            if st in replacements:
                node.set_static_transform(replacements[st]) ### IMPLEM: inval that field but not the overall transform...

    # now push the data from dt into each (owned or new) static transform
    for st in statics.keys():
        if st in replacements:
            st = replacements[st]
        st.applyDataFrom(dt)

    ### more... only if we need to wrap some some specialized code to inval just the right aspects of the nodes ###

    return

def allocate_TransformControls(number):
    res = []
    for i in range(number):
        tc = allocate_TransformControl()
        if tc:
            res.append(tc)
        else:
            break
    return res

def allocate_TransformControl():
    return TransformControl() ### STUB; todo: check tc.transform_id against limit? recycle?

# end
