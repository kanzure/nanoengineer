# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
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

070205 replacing world.nodelist with some more controlled access methods:
- world.list_all_objects_of_type(DNA_Cylinder)
- world.number_of_objects (of all types)

"""

from exprs.Exprs import getattr_Expr, not_Expr
from exprs.instance_helpers import InstanceOrExpr
from exprs.attr_decl_macros import State, Instance
from exprs.__Symbols__ import Anything, _self
from exprs.StatePlace import set_default_attrs
from exprs.py_utils import sorted_by

from exprs.Highlightable import SavedCoordsys #070401

# I'm not sure whether this unfinished new code should be finished and used -- for now, comment it out [070206]
#####e redesign and refile this type stuff (it's wrong in basic nature, terminology, rep, version control; undecided re pure exprs)
##
##def obj_i_type(obj): #070205 late
##    """For an arbitrary Python object, but especially an Instance, return a representation of its type
##    (known as an Instance Type or i_type, even if it doesn't come from an Instance),
##    as a model object or part of one (not necessarily closely related to Python's concept of its type).
##       WARNING: it's not yet clear whether an Instance's type can vary with time. ###k
##       WARNING: it's not yet clear what this should return for a pure expr. Maybe just 'Expr'??
##    But that's not good enough, since we'll need to understand types of exprs in relation to what instances they'd make...
##       Note: the returned type-representation's own python type is not publicly defined,
##    but the returned objects can be compared with our associated helper functions, or with python == and !=,
##    and printed, and stored as pure python data, and hashed (so they're useable as dict keys).
##    """
##    try:
##        #e should first verify it's an Instance, to be safe; then we could also use .type instead
##        res = obj._i_type # works for Instances [nim right now]
##            # (so might .type, but we're not free to use an attrname like that on arbitrary objects)
##            # Note: many InstanceMacros and similar wrappers delegate this to the object they wrap. This is essential.
##        assert _possible_true_Instance_type(res)
##    except AttributeError:
##        res = type(obj) ####k ???
##        assert not _possible_true_Instance_type(res)
##    return res
##
##def _possible_true_Instance_type( i_type):
##    """[private]
##    classify all objects into whether they might be types of actual Instances (return True)
##    or types of other things (return False).
##    """
##    return not callable(i_type) ###k
##
##def i_type_predicate(i_type):
##    """Given an Instance Type [bad term -- ambiguous -- ###FIX],
##    turn it into a predicate which is true for objects of that type and false otherwise
##    """
##    if _possible_true_Instance_type( i_type):
##        def pred(thing, i_type = i_type): #k I'm guessing this i_type = i_type kluge is still needed, at least in Python 2.3
##            return getattr(thing, '_i_type', None) == i_type # from inner func
##                ##### WRONG as soon as we recognize type inclusion (model obj subclassing)
##    else:
##        def pred(thing, i_type = i_type):
##            return isinstance(thing, i_type) ###k REVIEW
##    return pred
##
##nim _i_type in IorE - justuse classname for now, but only if not delegating, i guess... ######NIM
##            ###BUG: mere name is too loose, someday

def model_type_predicate( model_type): #070206
    "#doc"
    if type(model_type) == type(""):
        # assume it should exactly match the string passed to World.make_and_add and stored in thing.model_type by a kluge [070206]
        def pred(thing, model_type = model_type):
            # assume thing is an Instance, thus has the attr _i_model_type
            res = (thing._i_model_type == model_type)
            # print "model_type_predicate(%r)(%r) = %r" % (model_type, thing, res)
            return res
        pass
    else:
        # assume model_type is an IorE subclass; use the last component of its name, by convention
        name = model_type.__name__
            # note: not self.__class__.__name__ -- that would be about the class's class, ExprsMeta!
        name = name.split('.')[-1]
        assert type(name) == type("") # otherwise we might have infrecur of this case
        pred = model_type_predicate( name)
    return pred

# ==

class World(InstanceOrExpr): #070205 revised, public nodelist -> private _nodeset
    """maintains the set of objects in the model; provides general operations on them
    """
    #k is this 070401 change ok: ModelObject -> InstanceOrExpr? At least it doesn't seem to have caused trouble.
    ###e Q: Is it ok for this to inherit _CoordsysHolder and have .draw save the coords? Or to own one of those to hold them?
    # The goal is for some external thing to be able to copy the coords we will draw a newly made thing under.
    # that's partly misguided given that we might in theory draw things in more than one place
    # and/or in a different place than in the prior frame. The external thing that wants to do this
    # is self._newobj.copy_saved_coordsys_from( self.world) in class PalletteWell.on_press as of 070401.
    # It wants to use the right coordsys to turn a mouseray into that obj's initial position in the World. Hmm.
    #    A: In principle, if we're drawing the world twice (eg in stereo), we'd better be able to tell from a mouseray
    # used to put something into it, which world-instance we're putting it into! and each of those needs to know
    # where mouse events would drop things (based on where it was last drawn -- no ambiguity there).
    # So it's correct for something to save that and reveal it -- it just needs to be a world-drawn-instance
    # which would somehow show up (as selobj?) when interpreting that mouseray. For now, it's ok to kluge this
    # by assuming this class is taking the role of world-drawn-instance and being drawn only once. Alternatively,
    # we could say that the recipient of the mouseray should also be told what background it's over (whether or not it
    # hit the background or some object drawn over it) (this might be "one of several background objects" for stereo)
    # so it would know how to find "absolute model coords" in a canonical way. Or a third way is for the World client code
    # to include an invisible object drawn just to capture the coords. In the multi-world-drawn-instance case, we'd have to combine
    # this object with our knowledge of which worldinstance was drawn, by storing the drawn coords under the crossproduct
    # of that and the object...
    # ... Trying one of these solutions with self._coordsys_holder below. Seems to work & fix the pallette bug. Comment needs cleanup.
    # [070401]
    #
    ###FLAW: logically, this should store exprs needed to remake its instances, merely caching the instances,
    # but in fact, stores the instances themselves. This will make save/load harder, and means instances survive code-reloading.
    # Probably it should be fixed before trying to do save/load. [070206 comment]

    _nodeset = State(Anything, {}) # self._nodeset is private; it's changetracked but only when entirely replaced (not just modified!)
        # (###e optim: can that be fixed? we need a way to access the LvalForState and inval it)
        ###e we'll need to put that State on a different state-layer (i.e. kind of StatePlace) when we start saving/loading this

    _coordsys_holder = Instance(SavedCoordsys()) #070401 -- see long comment above, about _CoordsysHolder

    def _init_instance(self):
        super(World, self)._init_instance()
        set_default_attrs( self.untracked_model_state, _index_counter = 4000) #070213; could State() do this for us instead? #e

    def _C_number_of_objects(self):
        """Compute self.number_of_objects, defined as the total number of objects explicitly stored in self,
        of all types, in all Parts and configurations (but not including objects removed by Undo but present in Undo history).
           WARNING: Parts, configurations, and Undo are nim for this class as of 070206.
           Note: probably not very useful, due to that lack of qualification by anything.
        Perhaps useful to know whether self is entirely empty,
        or as a ballpark estimate of how much data it might contain.
        """
        return len(self._nodeset)

    def list_all_objects_of_type(self, model_type):
        """Return a nominally read-only list of all objects in self of the given model_type (or IorE class, as a special case),
        in a deterministic order not yet decided on (might be creation order, world-index order, MT order).
        [Current implem uses creation order as an Instance, as told by _e_serno; this order will become unideal as new kinds of
         object ops are added, like potential objs or moving them from other worlds (if possible). ##e 070206]
        ##e needs options for "not just this config", "not just this Part" (and revised implem, once we support configs or Parts)
        #e optim: extend API to be able to specify ordering -- otherwise it has to be sorted twice (here, and often in caller).
        """
        type_predicate = model_type_predicate( model_type) # this permits model_type to be an IorE subclass (or its name)
            ###BAD: not enough kinds of type exprs can be passed, and error checking on model_type (not being garbage) is nim
        return filter( type_predicate, self._sorted_objects ) ##e optim: filter first (or keep them already type-separated), then sort

    def _append_node(self, index, node):#070201 new feature ###e SHOULD RENAME [070205]
        "not sure if this should be private... API revised 070205, ought to rename it more (and #doc it)"
##        self._nodeset = dict(self._nodeset)
##            ###KLUGE: copy it first, to make sure it gets change-tracked. Inefficient when long!
            ###BUG in the above:
            # doesn't work, since the change to it is not tracked, since the old and new values compare equal! (guess)
            #k note that LvalForState may also not keep a deep enough copy of the old value in doing the compare,
            # to not be fooled by the direct modification of the dict (in the sense of that mod escaping its notice, even later)!
            # (i'm not sure -- needs review, e.g. about whether bugs of this kind will go undetected and be too hard to catch)
##        self._nodeset[index] = node
        newset = dict(self._nodeset)
        newset[index] = node
        self._nodeset = newset # this ought to compare different and cause changetracking (assuming the index was in fact new)
        ###e OPTIM IDEA: can we modify it, then set it to itself? No, because LvalForState will compare saved & new value --
        # the same mutable object! We need to fix that, but a workaround is to set it to None and then set it to itself again.
        # That ought to work fine. ####TRYIT but then fix LvalForState so we can tell it we modified its mutable contents. [070228]
        return

    def _C__sorted_objects(self):
        """compute private self._sorted_objects (a list, ordered by something not yet decided,
         probably creation time; probably should be the same order used by list_all_objects_of_type)
        """
        res = self._nodeset.values()
        res = sorted_by( res, lambda obj: obj._e_serno )
            ###KLUGE: use _e_serno in place of .creation_order, not yet defined --
            # works now, but wrong in general due to potential objects or moved-from-elsewhere objects.
            # (Q: Would index-in-world be ordered the same way? A: Yes for now, but not good to require this in the future.)
        return res

    def draw(self):
        # draw all the nodes [#e 070228 ###e in future we're more likely to draw X(node) for X supplied from caller & subset of nodes]
        # [optim idea 070103 late: have caller put this in a DisplayListChunk; will it actually work?
        #  the hope is, yes for animating rotation, with proper inval when nodelist changes. It ought to work! Try it. It works!]
        self._coordsys_holder.save_coords_if_safe() #070401
        for node in self._sorted_objects:
            # print "%r is drawing %r at %r" % (self, node, node.pos) # suspicious: all have same pos ... didn't stay true, nevermind
            self.drawkid( node) ## node.draw()
                # this assumes the items in the list track their own posns, which might not make perfect sense;
                # otoh if they didn't we'd probably replace them with container objs for our view of them, which did track their pos;
                # so it doesn't make much difference in our code. we can always have a type "Vertex for us" to coerce them to
                # which if necessary adds the pos which only we see -- we'd want this if one Vertex could be in two Worlds at diff posns.
                # (Which is likely, due to Configuration Management.)
            if 0 and node is self._sorted_objects[-1]:
                print "drew last node in list, %r, ipath[0] %r, pos %r" % (node, node.ipath[0], node.pos)
        ###e see comment above: "maybe World needs to wrap all it draws with glue to add looks and behavior to it"
        return

    def make_and_add(self, expr, type = None): #070206 added type option -- required for now (temporary); semantics not fully defined
        """Make a new model object instance from expr, add it to the world at a local index we choose, and return it.
        This is the main public method for making new model objects.
           [As a temporary ###KLUGE (070206), the type needs to be passed, for purposes of methods like self.list_all_objects_of_type.
        This will no longer be needed once we can reliably infer the type (including supertypes) from the made instance of expr.
        But that probably requires altering delegation to specify which attrs to delegate (based on which interface they're part of),
        including a new attr for model object type. ###e Even once that's done, the caller may want to pass type-like info, perhaps
        "tags" -- e.g. one current caller passes type = "dot" which could not be inferred from expr it passes. ###e Callers may also
        want to pass desired relations, like a parent object, for convenience, or to influence details of how we make and index
        the new instance. ##e callers will also want to wrap objects with type-nicknames (see code comment for details).
           [WARNING: the API may be revised to also return the index. Or, we might store that in object, or store a back-dict here.]
        """
        index, node = self._make(expr)
            # that picks a unique index (using a counter in transient_state); I think that's ok
            # (but its change/usage tracking needs review ####k)
        self._append_node(index, node) # revised 070205
        if 'model_type_on_object_kluge_070206': ###KLUGE -- store type on object (simulates later inferring it from object)
            # update 070213: the right thing to do is probably not this, but to wrap the object itself with a type-nickname
            # (before passing it to us), so not only this world (self), but everything that sees it (MT default label, commands/ops,
            # selobj checks, etc), can react to its type-nickname.
            if type is not None:
                # node._i_model_type is defined on all Instances, and node should be one
##                if not hasattr(node, '_i_model_type'):
##                    node._i_model_type = None # this is how much of a kluge it is -- we're not even sure which classes need this attr
                if node._i_model_type is not None:
                    assert node._i_model_type == type, "make_and_add type %r inconsistent with existing type %r on %r" % \
                           (type, node._i_model_type, node)
                node._i_model_type = type
            pass
        return node

    def _make(self, expr): # moved here from demo_drag 070202
        """[private]
        Allocate a new index, use it as the localmost component of ipath while making
        [or finding?? I THINK NOT ####k] expr,
        and return (index, new-expr-instance).
           Note that it's up to expr whether to actually make use of the suggested ipath
        in the new instance. The case of one instance stored with different indices in World
        is not reviewed, and not recommended until it is, but it's up to the caller to
        worry about. I don't know it's wrong, just never thought about it and assumed it would not happen
        when analyzing the code.
        """
        index = None
        #e rename? #e move to some superclass
        #e worry about lexenv, eg _self in the expr, _this or _my in it... is expr hardcoded or from an arg?
        #e revise implem in other ways eg eval vs instantiate
        #e default unique index?? (unique in the saved stateplace, not just here)
        # (in fact, is reuse of index going to occur from a Command and be a problem? note *we* are acting as command...
        #e use in other recent commits that inlined it
        if index is None:
            # usual case I hope (due to issues mentioned above [maybe here or maybe in demo_drag.py]): allocate one
            index = self.untracked_model_state._index_counter
            if 'index should be modified [070203]':
                # see comments above dated 070203
                index = index + 1
                self.untracked_model_state._index_counter = index
                    # 070213 changed implem of _index_counter to make sure it's not change/usage-tracked.
                    # (Fyi, I don't know whether or not it was before (using State()), in a way that mattered.
                    #  The tracking danger would be that whenever you make any new object,
                    #  the old objects see that the index they used is different
                    #  and think they too need remaking, or something like that! This needs thinking through
                    #  since it probably covers all make-data, not just the index. All make-data is being snapshotted.
                    #  For that matter, things used by "commands" are in general different than things used to recompute.
                    #  Maybe entire commands need to have tracked usage discarded or kept in a new kind of place. #####FIGURE OUT)
                    #
                    # Note (language design flaw): to set this attr (using current code),
                    # you have to refer to it directly in the stateplace,
                    # rather than using the kind of abbrev that (in Highlightable glname) seems to work for get:
                    #   _index_counter = _self.untracked_model_state._index_counter
                    # This could possibly be fixed in C_rule_for_formula (not sure), or by making the abbrev in a fancier manner.
                    # (If you try to set the abbrev, you get
                    # "AssertionError: subclass [C_rule_for_formula] ... should implement set_for_our_cls".)
                    #
                    ###BUG: even for get, the abbreviated form (self._index_counter) is not updated when the spelled out form is!!
                    # See this debug print from when we tried that here:
                    ## print "after set to %r, self._index_counter = %r, self.untracked_model_state._index_counter = %r" % \
                    ##   (index, self._index_counter, self.untracked_model_state._index_counter )
                    ## # it prints: after set to 4002, self._index_counter = 4001, self.untracked_model_state._index_counter = 4002
                    # This is weird, since Highlightable seems to succeed using a similar glname abbrev for get.
                    # (Unless it doesn't, and I never noticed?? To check, I just added debug code for that -- so far untriggered.)
                pass
            ###e LOGIC ISSUE: should assert the resulting ipath has never been used,
            # or have a more fundamental mechanism to guarantee that
        env = self.env # maybe wrong, esp re _self
        ipath = (index, self.ipath)
        return index, env.make(expr, ipath) # note: does eval before actual make

    # ==

    def _C_mt_kids(self): # 070206 experiment related to ModelTreeNodeInterface (sp?)
        ###e how do we depend on the mt display prefs? note we need to be drawn twice, once in graphics area using .draw
        # and once in MT using the mt_* methods, but with independent envs provided! Self.env might have room in attr namespace,
        # but it has a single origin. Besides there might be two indep MT views or graphics views -- each of those also needs
        # separate envs (of the same kind). But that makes us two instances! I guess we need separate World data obj vs World viewer,
        # to handle that! I'm not even sure it makes sense to put the viewing methods in the same object... but maybe it does
        # with this concept of partial instantiation [nim], in which we could instantiate the viewing layer(?) (interface??) twice,
        # and the data layer just once, letting it (an instance) serve as the expr for instantiating the viewing layer in two places.
        # (But this makes it clear that the env would need to be split into separate parts, one for each partially instantiable
        #  layer -- hopefully these parts would correspond to interfaces (or sets of them), i.e. an interface's attrs would
        #  have to all be instantiated at the same time, and decls would control which ones were instantiated together in which
        #  partial-instantiation layers.)
        #
        # So for now let's pretend self.env can tell us... tho as initial kluge, the global env.prefs (get_pref?) could tell us.
        # But even sooner, just pretend we don't care and always show all the kids.
        return self._sorted_objects

    mt_name = "testmode" #e or maybe something like State(str, "Untitled"), or a stateref # or "Untitled" as it was before 070208
    mt_openable = True
    ## mt_node_id = getattr_Expr( _self, '_e_serno')
    mt_node_id = getattr_Expr( _self, 'ipath') #e optim: should intern the ipath ###e move this to IorE? btw redundant w/ def mt_node_id
        # 070218 -- by test, using ipath (a bugfix) makes world.open persistent (as hoped/predicted);
        # probably doesn't affect open-MT newnode slowness (but now that's fixed in different way in demo_MT)

    # ==

    def _cmd_Clear(self): #070106 experimental naming convention for a "cmd method" -- a command on this object (requiring no args/opts, by default)
        if self._nodeset:
            # avoid gratuitous change-track by only doing it if it does something (see also _cmd_Clear_nontrivial)
            # NOTE: this cond is probably not needed, since (IIRC) LvalForState only invalidates if a same_vals comparison fails. ###k
            self._nodeset = {}
        return
    # related formulae for that command
    # (names are related by convention, only used in this file, so far; prototype for wider convention, but not yet well thought through)
    _cmd_Clear_nontrivial = not_Expr( not_Expr( _nodeset)) #KLUGE: need a more direct boolean coercion (not that it's really needed at all)
        # can be used to enable (vs disable) a button or menu item for this command on this object
    _cmd_Clear_legal = True # whether giving the command to this object from a script would be an error
    _cmd_Clear_tooltip = "clear all objects" # a command button or menu item could use this as its tooltip ###e is this client-specific??

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
