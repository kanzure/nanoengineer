"""

world.py -- prototype Model Data Set owning/storing object, not yet very general.

$Id$

070201 Moved here from demo_drag.py.
Class & file likely to be renamed -- but not to DataSet since that's different --
it's a subset of refs to data already in the model.

Some relevant discussion remains in demo_drag.py.

Note: for our use in dna_ribbon_view.py we said:
  #e generalize World to the DataSet variant that owns the data,
  # maybe ModelData (not sure which file discusses all that about DataSet), refile it... it supports ops, helps make tool ui ###e
"""


from basic import *
from basic import _self, _this, _my


class World(ModelObject):  ###WARNING: this is now also used (and commented on) in dna_ribbon_view.py; see there for refiling advice###e
    "#doc -- has a list of Instances it draws, and a clear command for them"
    nodelist = State(list_Expr, []) # self.nodelist is public for set (self.nodelist = newval), but not for append or other mods
        # since not changetracked -- can it be?###@@@
        ###e 070201 does it still need to be public for set? i expect not, see following, but need to review; our clear cmd still sets...
    def append_node(self, node):#070201 new feature
        self.nodelist = self.nodelist + [node] # kluge: make sure it gets change-tracked. Inefficient when long!
        return
    def draw(self):
        # draw all the nodes
        # [optim idea 070103 late: have caller put this in a DisplistChunk; will it actually work?
        #  the hope is, yes for animating rotation, with proper inval when nodelist changes. It ought to work! Try it. It works!]
        for node in self.nodelist:
            # print "%r is drawing %r at %r" % (self, node, node.pos) # suspicious: all have same pos ... didn't stay true, nevermind
            node.draw() # this assumes the items in the list track their own posns, which might not make perfect sense;
                # otoh if they didn't we'd probably replace them with container objs for our view of them, which did track their pos;
                # so it doesn't make much difference in our code. we can always have a type "Vertex for us" to coerce them to
                # which if necessary adds the pos which only we see -- we'd want this if one Vertex could be in two Worlds at diff posns.
                # (Which is likely, due to Configuration Management.)
            if 0 and node is self.nodelist[-1]:
                print "drew last node in list, %r, ipath[0] %r, pos %r" % (node, node.ipath[0], node.pos)
        ###e see comment above: "maybe World needs to wrap all it draws with glue to add looks and behavior to it"
        return

##    _index_counter = State(int, 1000) # moved here from demo_drag 070202
##        ####k i think this should not be usage-tracked!!! think abt that... then see if true (probably not)

    _index_counter = 1000 # (an easier way to make it not tracked [070202])
    
    def make_and_add(self, expr): # moved here from demo_drag 070202 ###@@@ CALL ME from dna_ribbon
        node = self.make(expr)
            ### NOTE: index should really be determined by where we add it in world, or changed when we do that;
            # for now, that picks a unique index (using a counter in transient_state)
        
        ## self.nodelist.append(node)
        ## self.nodelist = self.nodelist + [node] # kluge: make sure it gets change-tracked. Inefficient when long!
        self.append_node(node) #070201 new feature
        
        ##e let new node be dragged, and use Command classes above for newmaking and dragging
        return node
    
    def make(self, expr): # moved here from demo_drag 070202
        index = None
        #e rename? #e move to some superclass 
        #e worry about lexenv, eg _self in the expr, _this or _my in it... is expr hardcoded or from an arg?
        #e revise implem in other ways eg eval vs instantiate
        #e default unique index?? (unique in the saved stateplace, not just here)
        # (in fact, is reuse of index going to occur from a Command and be a problem? note *we* are acting as command...
        #e use in other recent commits that inlined it
        if index is None:
            # usual case I hope (due to issues mentioned above [maybe here or maybe in demo_drag.py]): allocate one
            index = self._index_counter
            index = index + 1
            self._index_counter = index
            ###e LOGIC ISSUE: should assert the resulting ipath has never been used,
            # or have a more fundamental mechanism to guarantee that
        env = self.env # maybe wrong, esp re _self
        ipath = (index, self.ipath)
        return env.make(expr, ipath) # note: does eval before actual make

    # ==
    
    def _cmd_Clear(self): #070106 experimental naming convention for a "cmd method" -- a command on this object (requiring no args/opts, by default)
        if self.nodelist:
            # avoid gratuitous change-track by only doing it if it does something (see also _cmd_Clear_nontrivial)
            # NOTE: this cond is probably not needed, since (IIRC) LvalForState only invalidates if a same_vals comparison fails. ###k
            self.nodelist = []
        return
    # related formulae for that command
    # (names are related by convention, only used in this file, so far; prototype for wider convention, but not yet well thought through)
    _cmd_Clear_nontrivial = not_Expr( not_Expr( nodelist)) #KLUGE: need a more direct boolean coercion (not that it's really needed at all)
        # can be used to enable (vs disable) a button or menu item for this command on this object
    _cmd_Clear_legal = True # whether giving the command to this object from a script would be an error
    _cmd_Clear_tooltip = "clear the dots" # a command button or menu item could use this as its tooltip ###e is this client-specific??

    def _cmd_Make(self):
        print "world make is nim" ###
    _cmd_Make_tooltip = "make something [nim]" ###e when we know the source of what to make, it can also tell us this tooltip

    pass # end of class World

# == comments from class World's original context

# for a quick implem, how does making a new node actually work? Let's assume the instance gets made normally,
# and then a side effect adds it to a list (leaving it the same instance). Ignore issues of "whether it knows its MT-parent" for now.
# We know it won't get modified after made, since the thing that modifies it (the command) is not active and not reused.
# (It might still exist enough to be revivable if we Undoed to the point where it was active, if it was a wizard... that's good!
#  I think that should work fine even if one command makes it, some later ones modify it, etc...)

# so we need a world object whose state contains a list of Vertex objects. And a non-stub Vertex object (see above I hope).

# end
