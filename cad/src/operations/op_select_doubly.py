# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
op_select_doubly.py -- workhorse function for the Select Doubly operation.

Needs some comment-cleanup. And some potential optimizations described herein
are worth doing if this op's speed ever matters. And it should now be allowed
to coexist with the Selection Filter. [That is now allowed as of bruce 050629.]

$Id$

History:

bruce 050520 wrote this from scratch, to make Select Doubly fast and correct.
(Before that it was always slow, and was incorrect since at least Alpha1.)

For more detailed history and notes see cvs rev. 1.1 or 1.2 of this file.
(At some point I should edit the comments therein into a new separate text file.)

This algorithm is linear time (in number of bonds 1-connected to initially selected atoms).
For an explanation of why this alg is correct, assuming you already know basically
what it's trying to do and how (which is not documented here, sorry), see a long comment below
(which was shortened in cvs rev 1.3, so see an earlier rev for the proof).
For an overview of how it works, wait until I have more time to document it.

bruce 050629 rewrote two methods to make them non-recursive, to fix bug 725
by not using Python stack when there are lots of atoms traversed.
Some cleanup of this would be useful, and some optims are still possible.
"""
__author__ = "bruce"

class twoconner: #e rename
    """Scan connected parts of a graph to find out which edges are cut-edges for those parts.
    Later, use that info to traverse doubly-connected subgraphs from given nodes.
    Also keep info which would later let you quickly report whether two nodes are 1-connected, if anyone asked.
    (More generally, info which would let you quickly map any node to a fixed representative node in its connected component.)
    (But no method for making this query is implemented yet, and not quite enough info is kept,
     though comments explain how to fix that, which would be easy. #e)
    """
    def __init__(self):
        self.nodenums = {} # haven't yet visited any nodes, not even N1
        self.cutedges = {} # haven't yet proven any edges are cutedges (this holds cutedges as keys, values of 1)
            #e would it be useful to use returning i as value?
            #k still don't know if one edge can get here in both directions
        self.i = 1 # the first nodenum to assign
        #e or could store a list of i values which separate connected components -- probably useful
    def start(self, N1):
        """If we didn't already, traverse the connected component containing N1
        and record all its cutedges in self.cutedges.
        Return True if we had not already traversed N1's connected component (since it's easy) [#e could return i - i1]
        """
        # (Do we need to use diff value of i each time? doesn't matter, i think --
        #  i'll use one in case it helps track connected components later)
        if self.nodenums.get(N1): ###e optim: use id(N1) if N1 is a python object (e.g. an atom)
            return False
        i1 = i = self.i
        priornode = None # a fake node -- not anyone's neighbor
        diredge = (priornode, N1) # the first diredge to traverse
        num, i = self.traverse_nonrec( diredge, i) ### need retval??
        self.i = i
        # print "that conncomp had %d nodes" % (i - i1)
        assert num == i1
        # i - i1 is the number of nodes seen in N1's connected component
        # but the main result at this point is the dict self.cutedges
        return True #e could return i - i1

    def traverse_nonrec(self, diredge, i): #bruce 050629, part of fixing bug 725
        "non-recursive version of traverse method (see original method below for more extensive comments/docstring)"
        stack = [(0, diredge)] # this stack of partly-done traverse calls replaces the Python stack.
        del diredge
        retval = None
        # i changes during the loop but need not appear in the stack
        while stack:
            top = stack.pop()
            if top[0] == 0:
                # start of a simulated traverse call
                zerojunk, diredge = top
                priornode, N = diredge
                num = self.nodenums.setdefault(N, i)
                ## print "nodenums[%r] is %r, setdefault arg was %r" % (N, num, i)
                if num < i:
                    retval = num, i
                    continue #e optim: could have caller do the part up to here
                assert num == i == self.nodenums[N]
                Ni = i
                i += 1
                itinerary = self.neighbors_except(N, priornode) #e could optim when itinerary is empty
                    ###e or better, could optim by not visiting itinerary elts already with nodenums, just grabbing min of those.
                # order is arbitrary, so it doesn't matter that we'll scan itinerary
                # in reverse compared to recursive version; if it did, we'd reverse it here
                todo = (1, itinerary, N, num, Ni, diredge) # some of this might be redundant, e.g. N and diredge
                stack.append(todo)
                retval = None
                continue
            # else, continuation of a simulated traverse call, in the loop on itinerary;
            # if retval is None it's starting the loop, otherwise it just got retval from the recursive traverse call
            onejunk, itinerary, N, num, Ni, diredge = top
            if retval is not None:
                subnum, i = retval
                num = min(num, subnum)
            if itinerary:
                # more to do (or we might be just starting)
                neighbor = itinerary.pop()
                    # note: itinerary is mutable, and comes on and off stack, but that should be ok
                    # since it's never on there in more than one place at once
                # simulate a recursive call of traverse, but first put our own call's continuation state on the stack
                todo = (1, itinerary, N, num, Ni, diredge)
                stack.append(todo) # our own continuation
                todo = (0, (N, neighbor))
                stack.append(todo) # the recursive call (also requires retval = None)
                retval = None
                continue
            # end of the loop in traverse
            if num == Ni:
                self.cutedges[diredge] = 1
            retval = num, i
            continue
        # done
        return retval

    def traverse_OLD_RECURSIVE_VERSION(self, diredge, i):
        # no longer used, but keep for docstring and comments, for now [bruce 050629]
        # to optimize(??), pass the instvars rather than self (like for i), and split diredge in two
        """As this call starts, we're crossing diredge for the first time in either direction,
        but we don't yet know whether we've previously visited the node N at other side or not.
        (When this call ends, we'll be coming back across diredge in the other direction,
        bringing a "lowest number seen during this call" and a new "next number to assign to a node" i.)
           If we have seen that node N we're heading toward,
        make note of its number and bounce back right away (returning that number, and unchanged i).
           If we have never seen it, assign it the number i (which marks it as visited/seen now; do i+=1 for later),
        and for each of its other edges (none of which have been traversed either way, to start with),
        processed sequentially in some order, if by the time we get to that edge we *still* haven't
        traversed it (by coming across it into N from elsewhere, seeing N marked, and bouncing back out across it),
        then traverse it using this method recursively; when that loop is done we can finally return,
        traversing back out of N for the last time, backwards on diredge, and carrying the minimum number
        of all node-numbers seen.
           But one more thing: from all info we have as we return, figure out whether we've just
        noticed a proof that diredge is a cutedge, and record that fact if so. As explained elsewhere,
        all actual cutedges will get noticed this way.
        """
        priornode, N = diredge # why not let diredge be no more than this pair?
        num = self.nodenums.setdefault(N, i) # if visited, num says the number; if not, num is i and N is marked
        if num < i:
            # been there before
            ###k will we notice whether THIS diredge is a cutedge?? Maybe only when we cross it the other way?? (no...)
            return num, i
        # never been there before, so we're here (at N) now, and i is now assigned to it by setdefault
        assert num == i == self.nodenums[N]
        Ni = i # cache the value of self.nodenums[N] (just an optim to avoid looking it up later)
        i += 1
        itinerary = self.neighbors_except(N, priornode) # the neighbors to visit (along the diredges (N, neighbor))
        # As we begin the loop, no edge from N to a neighbor has been traversed either way,
        # but this doesn't mean those neighbors haven't been visited before (using some other edges into and out of them)!
        # And once inside the loop, we can't even say the edges haven't been traversed.
        # Suppose some edge has been traversed (into us and out again) -- will it cause any harm to traverse it again?
        # We'll definitely bounce right back (seeing the node visited), so the Q is, is it correct to record that number then.
        # Not sure yet, but for now assume it is ok! (Since it'll simplify the alg a lot to not record traversed edges.) ###k
        for neighbor in itinerary:
            subnum, i = self.traverse( (N, neighbor), i ) #e optim: faster to pass the pieces of diredge separately
            num = min(num, subnum) # should be ok to start with old value of i in num, returning min node we saw including N ###k
        # == Here is where we record some magic info related to cut edges....
        # for explanation (and proof of this alg's correctness), see the longer version of this comment
        # in cvs rev. 1.1 or 1.2 of this file.
        if num == Ni:
            self.cutedges[diredge] = 1 #k could an edge get entered into this twice (once in each direction)?? ###k [i don't think so]
        return num, i

    def neighbors_except(self, N, priornode): # morally this should be an init param or subclass method (but speed > abstractness here)
        "Return all N's neighbors except priornode (or all of them, if priornode is None) [assume they can be compared using 'is']"
        #e assume N is an atom; this justifies using 'is' and also is why we want to (for speed)
        return filter( lambda neighbor: neighbor is not priornode, N.realNeighbors() )
            #e might optim by chopping monovalent neighbors right here?
            # nontrivial to work out all implications of this... but i bet it's significantly faster,
            # esp. if we'd revise our class atom code to actually store the bonds in separate lists
            # to the monovalent and other neighbors! (And maybe to store neighbors rather than storing bonds? Not sure...)
            # Anyway, we *do* need to chop singlets! And we might as well chop monovalent neighbors if we make sure N1 in .start is never one
            # ie specialcase if it is. ####@@@@ DOIT.

    def apply_to_2connset_nonrec( self, N, func): #bruce 050629, part of fixing bug 725
        """Non-recursive version of apply_to_2connset.
        (Ought to be rewritten to use a non-recursive transcloser helper function
        made from Select Connected code.)
        """
        didem = {N:1} # set to 1 for N's appended to the todo list ##e could optim by using id(N)?
        todo = [N]
        while todo:
            newtodo = []
            for N in todo:
                assert self.nodenums.get(N), "self.nodenums should contain N (%r) but doesn't, or contains false %r" % (N, self.nodenums.get(N))
                assert didem.get(N)
                func(N)
                for neighbor in self.neighbors_except( N, None):
                    if didem.get(neighbor) or (N, neighbor) in self.cutedges or (neighbor, N) in self.cutedges:
                        continue
                    newtodo.append(neighbor)
                    didem[neighbor] = 1
            todo = newtodo
        return

    def apply_to_2connset_OLD_RECURSIVE_VERSION( self, N, func, didem = None):
        # no longer used, but keep for docstring and comments, for now [bruce 050629]
        """Apply func to the 2-connected set including N (or to N alone if all its edges are cutedges).
           Only works if we previously ran self.start(N1) in a way which hits N
        (we assert this, to detect the error).
        [Private: didem can be a dict of N's we already hit, for recursion.
        It would NOT be correct to try to optim select_doubly_f by passing its resdict as our didem dict
        (even if their values were compatible), since we make some assumptions about our didem dict
        which are not true for arbitrary atomsets like (I suspect -- not sure) might be in resdict.
        Or maybe I'm confused and this worry only applies to atomlist and passing resdict would work fine.
        If so, it'd optim this enough to do it sometime, perhaps. ##e]
        """
        assert self.nodenums.get(N), "self.nodenums should contain N (%r) but doesn't, or contains false %r" % (N, self.nodenums.get(N))
        if didem is None:
            didem = {}
        func(N)
        didem[N] = 1
        for neighbor in self.neighbors_except( N, None): #e optim getting that list
            if didem.get(neighbor) or (N, neighbor) in self.cutedges or (neighbor, N) in self.cutedges:
                #e optim(?? or not, if extra memory usage is bad): store it both ways at once (or, sorted way? sounds slow)
                continue #e optim: right here we could check if neighbor was monovalent
            self.apply_to_2connset( neighbor, func, didem)
        return
    pass

def select_doubly_transcloser(atomlist):
    """Return a list of atoms for which there is some ring of bonds
    (ok if that ring hits some atoms twice, but it can't include any bonds twice, even in opposite directions)
    containing both that atom and some atom in atomlist.
    """ #obs comments about func
    resdict = {}
    one = twoconner()
    for atom in atomlist:
        one.start(atom) # returns whether this atom showed it a new connected component, but that is not useful here
    # now it knows which edges are cutedges. This lets us transitively close over the non-cutedges, like this:
    for atom in atomlist: ###e this is what has to optim when func already applied, so *this* is what needs a dict...
        if atom not in resdict:
            one.apply_to_2connset_nonrec( atom, lambda a2: resdict.setdefault(a2,a2)) # doesn't matter if this applies func to atom when it's isolated
    # what about the desire to also apply func to monovalent neighbors?
    # Well, nothing prevents caller's func from doing this on its own!
    # No need to one.destroy() (tho it holds strongrefs to atoms) since no one refers into it, except our localvar.
    return resdict.values()

def select_doubly_func(atom):
    atom.pick()
    for n in atom.realNeighbors():
        if len(n.bonds) == 1: #e BTW, IMHO this is not the best thing to do -- should pick all "pure trees" hanging off this 2connset.
            n.pick()
    return

def select_doubly(atomlist): #e 1st try is slow if you pass it a highly redundant atomlist. Need to track which ones we picked...
    # don't use real picking, in order to be compatible with Selection Filter.
    map( select_doubly_func, select_doubly_transcloser( atomlist) )
    return

# end

