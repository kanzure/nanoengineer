    def _C_distorted_things(self):
        """
        Make sure the side effects associated with self.distorted_things are up to date,
        so that can be iterated over, and anything subscribing to its changes has them.
        """
        make sure input changesets are processed by asking for them in some sense
        (this also subs to their invals for next time)
        
        for t in self._xxx: # possibly distorted things, got added to some changeset by inval of motions they care about
            t.actually_distorted(): # _since_when?
                output_set[t] = t

        not sure if we need to subscribe to something more here?

        return output_set # not accurate, we return something that stands for an incremental set....

    




    """
    Turn the possibly distorted bridges into the actually distorted ones.
    Do this by noticing which bridges touch transformnodes whose actual transform data has changed
    (counting only the data in the dynamic transforms on them, I think, not the static ones),
    and for each one, check whether all its transformnodes have the same dynamic transform or not.
    Put the distorted bridges into our output set.
    """
    def xxx(self): # _C_ or something more special? or use a decorator?
        for bridge in input_set: ## get this from where? argument?
            d = bridge.is_dynamically_distorted() # "is"??? seems correct but also seems wrong in principle...
                # also this ought to be constant during the drag... so can't we just notice whether the symbolic transform changed??
                # not quite, since when a rigid motion occurs, the boundary sets dont change but they do get distorted.
                # but can't we track that by having an object just for that boundary,
                # which will be a single object that stands for all the bridges that cross that particular combo of drag-motion-kinds ==
                # symbolic drag transforms? that object tracks the actual data, changes in which distort its members
                # (for the bridging members, it's trivial -- any input change distorts them)
                # (for the non-bridging members, an input change to one dynamic transform symbol only moves them all rigidly --
                #  it has no change-consequence at all except to invalidate their abs atom positions, important when next drawing
                #  their external bonds)

            # ok, we're noticing symbolic transforms instead, on an actual bridge (eg EBSet).

            if d:
                put bridge in output_set
        return something
    


from foundation.state_constants import S_CHILD

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

    # pointer to our current (usually shared) static transform, or None.
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
            # this invalidates subscribers to our dynamic transform id,
            # but doesn't invalidate our overall transform value [###REVIEW: could it do so by using the following code?]
        assert t.is_identity()
            # if it wasn't, we'd also need to invalidate our overall transform value

    ### TODO: setter for static needs to list self inside it, so it can merge with others and affect us
    
    pass



# REVIEW ### how do we know which nodes a static transform is in??? or even, how many nodes? do we need to know them all? guess yes, for merge


def xxx(nodes):
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

    if dt.is_identity():
        nim # optimize for this -- just remove it, no other adjustment needed
    
    # get the affected static transforms and their counts
    statics = {}
    for node in nodes:
        assert node.dynamic_transform is dt
        st = node.static_transform
        statics.setdefault(st, 0)
        statics[st] += 1

    # see which statics straddle the boundary of our set of nodes
    straddlers = {}
    for st, count in statics.iteritems():
        if count < st.nodecount(): # implem
            straddlers[st] = st # or store a number?
        continue
    

    # allocate more TCs (up to the externally known global limit)
    want_TCs = len(xxX)
    
    new_TCs = allocate_transformControls(want_TCs) # implem

    if len(new_TCs) < want_TCs:
        # merge some statics as needed, transforming their CSDL primitives
        print "fyi: want %d new TransformControls, only %d available; merging" % \
              (len(new_TCs), want_TCs)
        nim

    # more... incl actually remove dt from all the nodes (or do that first, above)
    return



### REVIEW / DISCUSS: can we use separate "banks" so that we don't care about sharing TCs across banks?
# That is, the limit is only how many we use within one bank?
# Or is this handled for us (by existing banking code for just that purpose)...
# btw it means we have to keep track of which bank a CSDL is in, and it causes
# trouble if we move it across bank bounaries -- TC merging might be required at that time! maybe not detected until we draw
# (esp if we try to not worry if all affected nodes are hidden, etc).
# anyway we have to tell the allocator about the banks... or give it a callback to tell us about overloads, now or later.
# or do 2pass draw -- 1 draw-prep (report problems we need to solve, like too many TCs, with details of which ones),
# 1b fix them, 2 actually draw.


# If Russ can give me more TCs by doing the merging with identity himself (ie retransforming the vertices)...
# but don't I have to find out and respond somehow? not sure...

# In that case I'd end up fragmenting my usage of them, indefinitely... how would he know which ones to implement in the harder way?
# Decide each frame, implem the least used ones slower??

# but he also has to pass the tc ids in an attr array... not great if they keep changing.




