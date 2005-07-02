# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
bond_updater.py

[unfinished]

Recompute structural bond orders when necessary.

$Id$

This is needed for bonds between atoms whose atomtypes make p orbitals
available for bonding, to check whether pi bonds are formed,
whether they're aromatic or double or triple, to check for
radicals (pi systems containing unpaired electrons),
and to notice graphite.

History:

bruce 050627 started this as part of supporting higher-order bonds.
'''

__author__ = 'bruce'


import platform

from op_select_doubly import twoconner

def update_bonds_after_each_event( _changed_structure_atoms):
    """[should be called only from env.post_event_updates]
       This should be called at the end of every user event which might affect
    the atomtypes or bond-sets of any atoms or singlets, which are passed as the
    values of the dict _changed_structure_atoms, which we should not modify
    (and which no other code will modify while we use it). (As it happens,
    the caller will clear that dict after we return.)
       This function will either update, or record as needing update, the
    structural bond orders and associated data for all
    real atoms, real bonds, and open bonds which might be in pi systems
    (or which were, but aren't anymore). [And it might do more. #k if so, #doc that here.]
       Since it must be fast, it won't do work which leads it away from the actual
    atoms it's passed, and it will leave existing bond orders alone whenever they're
    locally consistent with the current atomtypes. That is, it will only act when
    there are local inconsistencies, and it will only fix them when this can be done
    on just the atoms it was passed (or their bonds), and in a reasonably unambiguous way;
    whenever it thinks a more global update it needed, it will record this fact
    (and the affected atoms) so the user can be advised that a global bond-update is needed.
       It will assume that interpart bonds (if any) have already been broken.
    (#e Or we might decide to extend it to break them itself.)
    """
    for atm in _changed_structure_atoms.itervalues():
        #e ignore killed atoms
        # for singlets, just look at their base atoms
        # when info must be recorded for later, do this per-chunk or per-part.
        ##k Do we move existing such info when atoms moved or were killed??
        
        atype = atm.atomtype
        
    if 0 and platform.atom_debug:
        print "atom_debug: update_bonds_after_each_event NIM; "\
              "not yet handling %d atoms or singlets in _changed_structure_atoms." % len(_changed_structure_atoms)
        for atm in _changed_structure_atoms.itervalues():
            print "eg this one",atm # so far, fails to notice atoms created as part of a cookie.
    return

def update_bonds_command(part): # for initial test, put this into debug menu (??)
    """Do a full updating of all possibly-pi bonds in the given part.
    Initial implem keeps no history anywhere, just redoes everything from scratch each time.
    """
    history = part.assy.w.history
    # First, find all the sp2 or sp atoms and open bonds, and understand how they're connected.
    chunks = part.molecules
    nsp2, nsp = 0,0 #####@@@@@ debug only
    openbonds = []
    realatoms = [] #e or dict if we decide to move things out of it as we hit them...
    for chunk in chunks:
        for atom in chunk.atoms.itervalues(): # includes "singlets" (open bonds); these usually have 'sp' hybridization
            # notice sp2 or sp atoms or open bonds; ignore sp3
            atype = atom.atomtype
            ###e should we check numbonds of all atoms??
            spX = atype.spX
            if spX == 3:
                # usual case, should be fast; just ignore this atom
                continue
            if atype.openbond:
                # sort it depending on max (least fancy) spX of itself (usually 1 for 'sp') and atom it's connected to
                bonds = atom.bonds
                if len(bonds) != 1:
                    # some sort of error -- skip it (should never happen)
                    if platform.atom_debug:
                        print "atom_debug: error: update_bonds_command skipping singlet %r with not exactly one bond" % atom
                    continue 
                spX = max(spX, bonds[0].other(atom).atomtype.spX)
                if spX == 3:
                    continue
                openbonds.append(atom)
            else:
                realatoms.append(atom)
            # rest might not be needed
            if spX == 2:
                # sp2 atom or open bond
                # ...
                nsp2 += 1
            else:
                assert spX == 1
                # sp atom or open bond
                # ...
                nsp += 1
        pass
    #e print number of various types of atoms found

    #e we might want to count total number of valence e's, and also collect all open bonds
    # (in each 1-connected part) for merge into pseudorings...
    
    msg = "nsp2 = %d, nsp = %d, nopen = %d" % (nsp2, nsp, len(openbonds))
    print msg
    history.message(msg)
    # scan for connected components of this, and then (in each one) doubly-conn ones but inferring bond order
    # since that scan has to notice atom types anyway, it might be best for above loop to just detect marks from it, not sort by type;
    # but i won't do that, since I want the code to decompose well into layers, where above will become an incremental
    # watcher-for-sp2/sp atoms layer, not always noticing connectedness. So above should record, and then we should rescan.

    # as for isolated sp/sp2 atoms (not connected to any other such atoms), we'll notice them as 1-member connected components
    # and deal with them then.

    # our scan order is this (conncomp means "connected component of sp/sp2 atoms"; bonds only "connect" if between two such atoms)
    # ###@@@ should odd-length sp chains count as "not connecting" the things on either side, since they must consist only of bond2?
    #   what about radicals on either side? I think an unpaired e *could* migrate over that chain... but not all the way across it!
    #   if we take seriously the "extents of radicals" we have to handle that... but for now it's ok if we don't.
    #   so it should be ok if I infer those are bond2 (as special case?) but count them as one pisys for purpose of radicalness.
    #   this requires measuring the sp chain when I first find it. Might be easiest to measure them all initially.
    # - open bonds (covers all conncomps with any open bonds, starting the scan from one of them; doesn't matter if it touches sp2 or sp)
    # - sp2 atoms (that way, a conncomp with no open bonds is scanned from an sp2 atom if poss, not an sp atom perhaps inside a chain)
    # - sp atoms (this handles all conncomps with sp atoms but no sp2 atoms, e.g. circle of =C=, H-C#C-H, N#N, N#C-H, but not O=C=O(?))

    # I am tempted to use some sort of pattern-finder scheme for this, since it's already getting too complex to easily spell it all out
    # by hand, esp. when I keep revising the details. Patterns would include sorting code (to be compiled into initial sorting methods,
    #  or for now interpreted in some simple way by code-layer-objects), and methods to look at the pattern and make a higher level
    # pattern for use by later stages. Example: sp chains turn into single objects. We specify how to find them efficiently
    # (initially scan sp atoms, each one might be anywhere in such a chain, pull those atoms out of the dict of "unparsed LL stuff").
    
    one = xxx()
    for ob in openbonds:
        if one.start_from_openbond(ob):
            print "scanned a conncomp with 1 or more openbonds, one of which is", ob #####@@@@@
    ###@@@ change following so we don't start in the middle of a chain of sp atoms! maybe sort sp2/sp, always start sp2 while we can.
    for other in realatoms:##e or we could be moving marked atoms out of that, as we hit them above -- not sure if that's faster
        if one.start(other): #####@@@@@ need to think whether this one sees enough... what if startatom is inside a ring? or not? etc...
            print "scanned conncomp with no openbonds, including atom",other
    pass

class AtomPattern:
    """#doc
    """
    world = None
    def grab(self, thing):
        self.world.grabfor(thing, self) # ?? #e give it our index for that thing, if we have one?
            # what about arrows? let all LL arrows still work?
    pass

class sp_chain(AtomPattern):
    "#doc... an instance of an sp_chain, which is specific to some set of already seen patterns... self.world I suppose"
    def scan(self, sp_atom):
        """We start scanning with a real sp atom, which might be anywhere in the chain;
        all sp atoms we find might have 2 or 1 bonds (anything else is an error -- treated how?? can it be caught earlier than this?),
        of which 0 to all can be to other sp or sp2 atoms (or open bonds).
        We turn any chain of 1 or more sp atoms (however terminated at each end) into a higher-level object,
        an "sp chain" (represented by this instance of this class, if the scan succeeds),
        which still has bonds to two lower-level objects... all atoms (LL objects) get "marked" as components of this HL object
        so any scan which encounters them (e.g. across a bond) know they're in it, and so highlighting/drawing knows that too.
        """
        # Just scan in each direction as far as we find real sp atoms, and remember what made us stop.
        # Directions come from the two bonds... and do we use real bonds, or higher-level connections from the existing parsed patterns?
        world = self.world
        nn = world.arrowsfrom(sp_atom) # want neighbors, bonds, or directed bonds? For most generality, we want directed bonds (arrows).
            # btw is sp_atom just a thing, or could it be "some arrow to a thing", in which case, this might not return the reverse arrow
            # for that one? I think the latter is also needed but is a separate method.
        assert len(nn) == 1 or len(nn) == 2 # assume this has already been checked by prior patterns, which classified each atom.
        if len(nn) == 2:
            left, right = nn
        else:
            (left,) = nn
            right = None #e or termination code for why we stopped scanning in that direction
        self.scan_one_direction(left)
        self.scan_one_direction(right)
        ###e now figure out what to do based on both ends of this scan.
        # and about the other stub code here:
        # what's the least it can record about the atoms it passes over in the scan
        # - a pointer to this object. meaning just, never mind them, they're part of me now.
        #   we'll do this in general, whenever some LL obj gets included into some HL obj.

        # I think no other info is needed!
        #   except maybe to know which ones are at ends,
        #   but really, that's handled by "mapping arrows" and its not enough to know it for objs (for length-1 chains).
        # - and to remember them as parts of itself, so later it can scan over them *in order* from one end to the other.
        #   there's >1 way to do this; most general is to store dicts of both HL directions inside itself.

        # still need to know exactly what to do in this code... older code uses (priornode, N) for an arrow, passes into neighbors_except...
        # but in general there can be >1 arrow between same objs, so we sometimes want to track arrows separately from objs.
        # still not sure if we generally want our algs to *store* arrows (in localvars) rather than objs... often might be more useful...
        
        pass #stub
    def scan_one_direction(self, arrow):
        """scan in one direction from arrow, and record stuff, and return the end-condition as a short string,
        one of error, sp2, sp3, openbond, nobond, other.
        """
        world = self.world
        while 1:
            if not arrow:#e or some cond of arrow, in case it can be a non-false termination code
                endwhy = 'nobond'
                break
            # now arrow is always a real arrow
            target = world.target(arrow)
            # is that an atom we'l include in our chain? ie an sp atom (w/o errors). Note, "sp atom" is some prior pattern, which has some name.
            # the prior pats we care about are looked up when we're inited or compiled... so some attr remembers it, by this point in the code.
            wantit = world.matchQ(self.sp_pattern, target)
            if not wantit:
                # end condition depends on this atom's type other than sp:
                # error, sp2, sp3. or something else we don't understand. or openbond.
                #e record some stuff
                atype = target.atomtype
                if atype.openbond:
                    endwhy = 'openbond' ###e or does type matter? yes, it matters if it permits sp or not.
                elif atype.spX == 2:
                    endwhy = 'sp2'
                elif atype.spX == 3:
                    endwhy = 'sp3'
                else:
                    endwhy = 'other' #e or 'error'
                # the only impossible one here is 'nobond'
                break
            self.grab(target) # tells self.world that target is part of us, now (do we need to tell it our arrow to target??)
            ###E include this atom in our pattern (which means, enter the arrow to it into a map in our pattern, maybe in both directions)
            #e(or record enough info to compute that later, e.g. give it a numeric index in a table)
            #e also tell the world that we *are* including it (in an "exclusive" way wrt other patterns not lower than us)
            # now figure out how to continue. this target atom points back to prior one (back thru arrow) and *maybe* somewhere else.
            outs = world.otherarrowsfrom(target, arrow) #e api is redundant... not sure that's bad, it's an error check
            assert len(outs) <= 1
            if not outs:
                arrow = None # detect this after we continue the loop
            else:
                arrow = outs[0]
            continue
        # finished the scan (in one direction only), and recorded why (somewhere)
        # and maybe where it ended and the arrow to something outside the chain in that dir
        #e now what?
        # what later code needs to know:
        # - chain length parity, or unknown (if it has open bond on either end)
        # - and therefore how to treat it
        # - and we can infer bond orders now, in some cases.
        # end of chain in each dir can be 4 things: open bond (of various kinds), sp2 atom, sp3 atom, no atom. (or erroneous atom)
        # in some cases we infer everything and become inert; in other cases, we act like one object with HL bonds on either end of the chain
        # (so sp2-scanning code can scan through us in one step, but it does need to ask us for a count of valence electrons in its pisystem).

        # this implies that the scanning then is not using real bonds directly, but (like neighbors_except) it sees something higher level.

        # it's almost like our HL view of LL world is a map on the directed arrows rather than on the objects!
        # like the new objs are wrappers; you could go through them and get back to original arrow (or some other one to same object)
        # and direct pointers to LL objs would still work fine. note that HL arrows to them might "count as replacing >1 LL arrow"
        # in the otherarrowsfrom method. Note that if we replace some arrows and not others, then otherarrowsfrom needs to know the level
        # of arrows it is supposed to return. Being a method on a world, this might be clear.
        return endwhy
    pass
    
class xxx( twoconner): # we'll start this from each open bond. when it reaches another, that's in same conncomp, so pretend a ring.
    # so a cutedge has no open bonds below it and thus has a definite e-parity and inferred bond order when nonradical.
    # and also, for a cutedge we can immediately dive in and infer back inside it, breaking that into smaller no-open-bond
    # systems and inferring their status (I think this has to be effectively recursive, ie not lintime;
    # might be better to do it breadth-first? someday we want it to record enough info to be faster when reseeing the same rings...
    # right now this will happen for a chain of bond2-connected benzenes... actually it might be ok, since it stops at each cutedge.)
    # ... this means: coming out of a cutedge, we know whether other side proves it a radical, and if not, the exact order.
    # (so far this is sp2-only, I haven't thought through sp atoms.)
    """[private]
    Specialized 2-connected-subset-traverser for pi systems -- really only for bonds that might be aromatic, GIVEN INFERRABLE ORDERs.
    Maybe we should infer fixed orders, when possible, during the same traversal that finds 1-conn and 2-conn sets?? ###@@@
    Since otherwise we might see 2-conn sets through bonds which are in fact held to order 1 by e.g. H2C=C< ...
    """
    openstart = None
    def start_from_openbond(self, N1):
        if self.nodenums.get(N1): #e optim: id(N1) would be faster; requires rewrite of all methods
            return False
        self.openstart = N1 # this makes any other open bonds we hit
            # (and btw we only hit ones with pi-capable atomtypes)
            # seem to link back to this one
            ###e but they should link to something else! a special fake atom with a specialized atomtype...
        res = self.start(N1) #e could optim, but no need (tho we might end up rewriting start method anyway)
        self.openstart = None
        assert res == True # for now
        return res
    
    def neighbors_except(self, N, priornode): # overrides superclass method; see also otherarrows method in some pseudocode above...
        """Assume N is an atom whose type permits aromatic bonds (sp2 or sp).
        Find all neighbors across bonds that might be aromatic
        (ie all neighbors also of those atomtypes, since we ignore the issue
        of whether a pi bond is too twisted to form), except priornode.
           Special case: if N is an open bond, then (due to how this should be called)
        we must be scanning its connected component starting from some other open bond self.openstart
        ###k or could that be N??
        in this case pretend N is connected to self.openstart.
        """
        res = []
        for b in N.bonds:
            #e reject bonds held artificially at a fixed integral order (even if >1, I think)
            other = b.other(N)
            if other is priornode: continue
            atype = other.atomtype
            if atype.spX < 3:
                res.append(other)
        # if N is open, then due to how this is called, its only neighbor is priornode,
        # so at this point res is [].
        if not res:
            if N.atomtype.openbond:
                openstart = self.openstart
                assert openstart.atomtype.openbond
                if N is not openstart:
                    # priornode can't be openstart since it can't be an open bond if N is
                    res.append( openstart)
        return res
    def traverse_nonrec(self, diredge, i): # overrides superclass method ###@@@ not yet different
        "non-recursive version of traverse method (see original method in superclass for more extensive comments/docstring)"
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
                ###e this is where retval should also have a number of valence e's and other info, which we should accumulate.
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
                #####@@@@@ debug kluge:
                a0, a1 = diredge[0], diredge[1]
                if a0 is None or a1 is None:
                    pass # print "this diredge has None in it:",diredge - a0 is None when a1 is our start atom
                else:
                    from bonds import find_bond
                    bond = find_bond(a0,a1)
                    print "cutedge found:",bond
                    bond.set_v6(3*6) # make cutedges look different! just so i can see if the right ones are found.
            retval = num, i
            continue
        # done
        return retval
    pass


# sp atoms are like this: not counting circles of only them, chains of them have to end,
# and when they end only one of their two overlayed pi-systems can be connected to.
# So, for even-length chains of them, the orders of the other pisystem (in the "resonance form model") go 0,1,0,1,0,
# so we can ignore it and look at the other pi system, x, 1-x, x, whose orders act just like those for CH units.
# For odd-length chains, *both* orders are forced, one to 0,1,0,1, the other to 1,0,1,0, so it's all double bonds.
# For open bonds on sp's, they might get extended by more sp's to any length, then hooked to graphite or each other...
# so just treat them as if hooked to graphite, at any point inside them, regardless of length.
# This is for C(sp)... for 1-valent sp atoms, we know the full story right away (can't be aromatic I think).
# But that can be noticed by order inference rather than being a special case.

# Does this mean I can "start from each open bond" w/o caring whether it's bonded to an sp or sp2 atom?
# I suspect so... but when backing out, I have to count chainlength of sp's, as well as valence e's, rings seen or not, etc.

# end
