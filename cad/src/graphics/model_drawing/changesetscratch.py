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




