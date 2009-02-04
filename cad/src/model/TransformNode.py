# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformNode.py -- mutable transform classes, shared by TransformNodes

NOT YET USED as of 090204

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.
"""



from foundation.state_constants import S_CHILD

Node3D

class TransformNode(Node3D): # review superclass and its name
    """
    A Node3D whose position and orientation is efficiently modifiable
    by modifying a contained transform. Children and control points may store
    relative and/or absolute coordinates, but the relative ones are considered
    fundamental by most operations which modify the transform (so the absolute
    ones must be invalidated or recomputed, and modifying the transform moves
    the node).

    The transform is actually the composition of an optional outer "dynamic
    transform" (used for efficient dragging of sets of TransformNodes)
    and an inner "static transform" (often non-identity for long periods,
    so we needn't remake or transform all affected CSDLs after every drag
    operation).
    
    Each transform component can be shared with other nodes. That is, several
    nodes can refer to the same mutable transform, so that changes to it affect
    all of them.

    The way self's overall transform is represented by these component
    transforms can change (by replacing them with others and/or merging the
    dynamic one into the static one), without changing the overall transform
    value. We optimize for the lack of overall change in such cases.
    """

    # pointer to our current (usually shared) dynamic transform, or None.
    # (note: rendered by putting self in a DrawingSet that will be drawn within
    #  this transform)
    dynamic_transform = None
    _s_attr_dynamic_transform = S_CHILD

    # pointer to our current (usually shared) static transform, or None [### DECIDE -- is none ok? some code below says no].
    # (note: rendered by being applied to the coordinates within all CSDLs
    #  associated with self)
    static_transform = None
    _s_attr_static_transform = S_CHILD

    # REVIEW: does the static_transform contain its TransformControl or is that
    # held externally somewhere? Ideally, it's held externally (if we still need it at all).

    # IMPLEM NOTE: the sharing of static transforms requires
    # one coordinated operation of folding dynamic trans into static, for all nodes at once,
    # since you have to split any shared static touched only in some nodes into two statics,
    # and merge some statics into the identity if you run out of TransformControls.

    ### REVIEW: should we limit the set of static transforms for all purposes (incl Undo)
    # due to a limitation on the number of TransformControls which arises from the rendering implementation?
    # If we do that, should we also remake CSDLs, or just transform them (presumably no difference in end result)?
    # Note: transforming them is what requires them to have mutable TC refs.
    
    def set_dynamic_transform(self, t): # review: use a setter? the initial assert might not be appropriate then...
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
    
    pass


# ==

def merge_dynamic_into_static_transform(nodes):
    """
    Given a set of TransformNodes with the same dynamic transform,
    but perhaps different static transforms, which may or may not be shared
    with nodes not in the set, remove the dynamic transform from all the nodes
    without changing their overall transforms, splitting their static transforms
    as needed, and removing or merging their static transforms as needed to
    observe a global limit on number of static transforms.
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
    statics = {}
    for node in nodes:
        st = node.static_transform
        assert st # assume all nodes have one even if not needed ### REVIEW -- does this make splitting easier/simpler?
        statics.setdefault(st, 0)
        statics[st] += 1

    # see which statics straddle the boundary of our set of nodes
    # (since we'll need to split each of them in two)
    straddlers = {}
    for st, count in statics.iteritems():
        # count is the number of nodes which have st;
        # does that cover all of st's nodes?
        assert count <= st.nodecount()
        if count < st.nodecount():
            straddlers[st] = st # or store a number?
        continue
    
    # allocate more TCs (up to the externally known global limit)
    want_TCs = len(straddlers)
    if want_TCs:
        new_TCs = allocate_TransformControls(want_TCs) # IMPLEM

        if len(new_TCs) < want_TCs:
            # There are not enough new TCs to split all the straddlers,
            # so merge some statics as needed, transforming their CSDL primitives
            print "fyi: want %d new TransformControls, only %d available; merging" % \
                  (len(new_TCs), want_TCs)
            print "THIS IS NIM, BUGS WILL ENSUE"
            assert 0
            # (We're hoping that we'll find a way to allocate as many TCs as needed,
            #  so we never need to write this code.)

        # now split each straddler in two, leaving the original on the "other nodes"
        # (this matters if one of them is a "permanent identity StaticTransform")
        
        replacements = {} # map old to new, for use on nodes
        for straddler, tc in zip(straddlers, new_TCs):
            replacements[straddler] = StaticTransform(straddler, tc)

        for node in nodes:
            st = node.static_transform
            if st in replacements:
                node.set_static_transform(replacements[st])

    # now push the data from dt into each (owned or new) st
    for st in statics.keys():
        if st in replacements:
            st = replacements[st]
        st.applyDataFrom(dt) ### IMPLEM, and use in __init__
            
        ##### REVIEW: how do we prevent someone who is subscribing to a node's total transform value
        ##### from thinking this op just changed that??? ########
        # either this is lower level than change tracking, or we capture and modify the tracking
        # to add notes saying it conformed to certain kinds of changes -- which requires first-class
        # reference to the morphism that represents the change, I think (likely to be represented
        # as a set of changesets and an index into that -- but then would we be deleting this change
        # from some of those side changesets???) ######
        # note that we're tracking a single change [for each node in nodes]... maybe it's not *yet* represented that way,
        # and we can set flags which will alter what happens when trackers learn of it and
        # decide what to subscribe to or what else to do as they inval themselves...
        # i.e. they'll do a lesser inval due to the flags we're setting now. ###
        # but it's not so simple, because the invals go out immediately upon each set to a node.attr above.
        # we might need to capture all of them within a time period (by setting a global in this code, begin/end fashion,
        # by pushing our own change tracker if that's possible-- note, it's more common to push our own usage tracker,
        # so this might be unprecedented or not yet supported) and then send them all out in modified form.
        # BTW we might encapsulate that part inside the node class, if we can fold all the mods we're doing here
        # into one method call onto that class -- remove dt, replace st with copy, fold dt into st.
        # BTW how would we prevent bugs if we catch everything? assert that t. value has not changed, by comparison,
        # when doing some tests (set debug flag to do that assert during certain tests of this code, or during all correctness
        # tests as opposed to performance tests).
        # ...
        # The best way is probably to use low-level-looking untracked access to do the mods,
        # then to explicitly send the tracked changes that we want to. Ideally re bugs, we'd also
        # disable higher level changes during that time (setting a flag on the node to make them an error).
        # And we'd do all that inside a begin/end thing that if we failed out of would clean that up
        # and also send general changes on all the nodes as a precaution.
        #   pool = begin_custom_changes()
        #   pool.own_changes_on(node)...
        #   ### do stuff
        #   pool.changed(X)
        #   pool.end()
        # I am not sure if the changes to st vars could be tracked normally anyway...
        # only if someone wanting to use the transform value (overall or static) didn't track those,
        # which is unlikely if they access it normally -- but ok if they access it through a synthesized slot
        # just for that purpose, since that slot can have special policies for its own usage being tracked,
        # i.e. it can understand that it only "uses an aspect" and can trust invals of that aspect to be complete.
        # (It can even return the same thing as the main slot but doing less tracking than that would do...
        #  but only makes sense if the main slot is private. Hmm, a "formula which explicitly does less usage tracking"...)
        
    # more... 
    return

# end
