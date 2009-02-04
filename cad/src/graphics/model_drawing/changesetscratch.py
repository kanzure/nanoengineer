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


from foundation.state_utils import StateMixin
from utilities.Comparison import same_vals

_IDENTITY_TRANSLATION = V(0, 0, 0)
_IDENTITY_ROTATION = Q(1, 0, 0, 0)
    # review: let these be class attrs of the types, or of the classes V and Q?
    # REVIEW: does same_vals think 0 and 0.0 are the same? if not, should we use 0.0 here?
    # TEST whether anything looks like identity... note that if initial values use 0 this might be ok

class Transform(StateMixin, object): # review: this class name ok? # review: where to file this? geometry? but it's a model object...
    # todo: if object superclass, register with same_vals? note that this is a state-holding object, not a data one
    """
    A mutable orthonormal 3d transform, represented as a rotation followed by
    a translation (with the rotation and translation being undoable state).

    Changes to the transform value can be subscribed to.
    """
    # review:
    # - should some transforms own TransformControls and keep them up to date?
    #   - or should external client code handle that itself, by subscribing?
    #   (Note that external code has to manage the set of these in a complex way,
    #    in order to conserve the number of TransformControls.)
    # - can you subscribe separately to changes to its translation and rotation?
    #   - if so, are they public usagetracked attrs?
    # - make value accessible as data object? (if so, let it be an attr self.value)
    #   (note: a ref to this would autosubscribe to the two components; or we could cache constructed object)
    # - permit comparison as if we were data? (no, buggy if someone uses '==' when they mean 'is')
    
    # todo:
    # - undoable state for the data, ops to change the data (move, rotate, etc),
    # - make sure the data (or overall value only?) can be subscribed to

    translation = State(Vector3D)
        ### IMPLEM:
        # - how do we make State work here? ###REVIEW how we do it in Test_ConnectWithState, funmode
        #   - and how do we let it be undoable state? compatible with _s_attr decls?? ###
        # - get default value from type;
        # - define these type names
        ### REVIEW:
        # - review type name: Vector vs Vector3 vs Vector3D ? Or just use V and Q?
    rotation = State(Quaternion)

    value = TransformData( translation, rotation) # REVIEW arg order, expr name, whether this formula def is appropriate

    
    # TODO: add formula for matrix?
    # TODO: somehow, integrate with TransformControl (or let this be used as one)
    
    def move(self, vector):
        self.translation = self.translation + vector

    def rotate(self, quat):
        """
        Rotate self around its own current origin.
        """
        self.rotation = self.rotation + quat # review operation order, compare with chunk.py --
            ### also compare default choice of center, THIS MIGHT BE WRONG

    def pivot(self, quat, center = None): ### REVIEW: merge with rotate? probably yes if default center is the same
        """
        Rotate self around a specified center.
        """
        nim, see chunk.py

    def is_identity(self): # review: optimize? special fast case if data never modified?
        return same_vals( (self.translation, self.rotation),
                          (_IDENTITY_TRANSLATION, _IDENTITY_ROTATION) )
    pass


class StaticTransform(Transform):
    def nodecount(self):
        """
        Return the number of nodes we belong to.
        """
        nim
    pass

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




