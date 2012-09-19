# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
Column_old_nim.py

$Id$

070129 moved from Column.py and instance_helpers.py;
this code is old and nim; implem is obs but intent is not (tho not urgent)
"""

from exprs.widget2d import Widget2D
from exprs.instance_helpers import InstanceOrExpr
from exprs.attr_decl_macros import ArgList
from exprs.py_utils import printnim

from exprs.lvals import LvalDict1
from exprs.py_utils import interleave_by_func
from exprs.Rect import Spacer

# undefined global symbol:  fixed_type_instance
# undefined global symbol:  ListInstanceType
# undefined global symbol:  index_path

##from instance_helpers import GlueCodeMemoizer, DelegatingInstance_obs

# moved here from instance_helpers.py 070129 [and sufficiency of imports not tested since then]

class DelegatingInstanceOrExpr_obs(InstanceOrExpr): #061020; as of 061109 this looks obs since the _C_ prefix is deprecated;
    #e use, instead, DelegatingMixin or DelegatingInstanceOrExpr combined with formula on self.delegate
    """#doc: like Delegator, but self.delegate is recomputable from _C_delegate as defined by subclass.
    This is obsolete; use DelegatingMixin instead. [#e need to rewrite GlueCodeMemoizer to not use this; only other uses are stubs.]
    """
    def _C_delegate(self):
        assert 0, "must be overridden by subclass to return object to delegate to at the moment"
    def __getattr__(self, attr): # in class DelegatingInstanceOrExpr_obs
        try:
            return InstanceOrExpr.__getattr__(self, attr) # handles _C_ methods via InvalidatableAttrsMixin
                # note, _C__attr for _attr starting with _ is permitted.
        except AttributeError:
            if attr.startswith('_'):
                raise AttributeError, attr # not just an optim -- we don't want to delegate these.
            return getattr(self.delegate, attr) # here is where we delegate.
    pass

DelegatingInstance_obs = DelegatingInstanceOrExpr_obs #k ok? (for when you don't need the expr behavior, but (i hope) don't mind it either)

#e rewrite this to use DelegatingMixin [later 061212: nevermind, it's probably obs, tho not sure]
class GlueCodeMemoizer( DelegatingInstanceOrExpr_obs): ##e rename WrapperMemoizer? WrappedObjectMemoizer? WrappedInstanceMemoizer? probably yes [061020]
    """Superclass for an InstanceOrExpr which maps instances to memoized wrapped versions of themselves,
    constructed according to the method ###xxx (_make_wrapped_obj?) in each subclass, and delegates to the wrapped versions.
    """
    # renamed to InstanceWrapper from DelegatingObjectMapper -- Wrapper? WrapAdder? Dynamic Wrapper? GlueCodeAdder? InstanceWrapper!
    # but [061020] I keep remembering it as GlueCodeMapper or GlueCodeMemoizer, and GlueCodeMemoizer was an old name for a private superclass!
    # So I'll rename again, to GlueCodeMemoizer for now.
    ###e 061009 -- should be a single class, and renamed;
    # known uses: CLE, value-type-coercers in general (but not all reasonable uses are coercers);
    # in fact [061020], should it be the usual way to find all kids? maybe not, e.g. CL does not use this pattern, it puts CLE around non-fixed arginsts.
    def _C_delegate(self): # renamed from _eval_my_arg
        printnim("self.args[0] needs review for _e_args or setup, in GlueCodeMemoizer; see DelegatingMixin")###e 061106
        arg = self.args[0] # formula instance
        argval = arg.eval() ###k might need something passed to it (but prob not, it's an instance, it has an env)
        ####@@@@ might be arg.value instead; need to understand how it relates to _value in Boxed [061020]
            #### isn't this just get_value? well, not really, since it needs to do usage tracking into the env...
            # maybe that does, if we don't pass another place?? or call its compute_value method??
            # argval might be arg, btw; it's an instance with a fixed type (or perhaps a python constant data value, e.g. None)
        #e might look at type now, be special if not recognized or for None, depending on memo policy for those funny types
        lval = self._dict_of_lvals[argval]
        return lval.get_value()
    def _C__dict_of_lvals(self): #e rename self._dict_of_lvals -- it holds lvals for recomputing/memoizing our glue objects, keyed by inner objects
        ##e assert the value we're about to return will never need recomputing?
        # this method is just a way to init this constant (tho mutable) attr, without overriding _init_instance.
        assert self._e_is_instance
        return LvalDict1( self._recomputer_for_wrapped_version_of_one_instance)
            #e make a variant of LvalDict that accepts _make_wrapped_obj directly?? I think I did, LvalDict2 -- try it here ####@@@@
        ## try this: return LvalDict2( self._make_wrapped_obj ) # then zap _recomputer_for_wrapped_version_of_one_instance ####e
            ##e pass arg to warn if any usage gets tracked within these lvals (since i think none will be)??
            # actually this depends on the subclass's _make_wrapped_obj method.
            # More generally -- we want schemes for requesting warnings if invals occur more often than they would
            # if we depended only on a given set of values. #e
            ####@@@@
    def _make_wrapped_obj( self, fixed_type_instance ):
        """Given an Instance of fixed type, wrap it with appropriate glue code."""
        assert 0, "subclass must implement this"
    def _recomputer_for_wrapped_version_of_one_instance( self, instance):
        """[private]
        This is what we do to _make_wrapped_obj so we can pass it to LvalDict, which wants us to return a recomputer that knows all its args.
        We return something that wants no args when called, but contains instance and can pass it to self._make_wrapped_obj.
        """
        # We use the lambda kluge always needed for closures in Python, with a guard to assert it is never passed any arguments.
        def _wrapped_recomputer(_guard_ = None, instance = instance):
            assert _guard_ is None
            return self._make_wrapped_obj( fixed_type_instance) # _make_wrapped_obj comes from subclass of GlueCodeMemoizer
        return _wrapped_recomputer
    # obs comments about whether _make_wrapped_obj and LvalDict should be packaged into a helper function or class:
    "maintain an auto-extending dict (self._dict_of_lvals) of lvals of mapped objects, indexed by whatever objects are used as keys"
    ###e redoc -- more general? how is it not itself just the LvalDict?
    # i mean, what value does it add to that? just being a superclass??
    # well, it does transform _make_wrapped_obj to _recomputer_for_wrapped_version_of_one_instance --
    # maybe it should turn into a trivial helper function calling LvalDict?? ie to the variant of LvalDict mentioned above??
    pass

# ==

# moved here from Column.py 070129; never finished or tested

class CLE(GlueCodeMemoizer): # not reviewed recently
    """Column list element:
    - handles 0 or more actual rows, perhaps varying in time, as described by one formula arg to Column
    - for each instance that formula evals to, this adds type-specific glue code (memoized for that instance) and delegates to it,
      also making the result available as the value of self.delegate
    - also contains the type-specific glue code ### as methods or classes?
    """
    printnim("CLE not reviewed recently")###k
    def _make_wrapped_obj(self, fixed_type_instance): # _c_ means "informal compute method" (not called in standard way)
        "make a new helper object for any fixed_type_instance, based on its type"
        ###e note, the only real "meat" here is a map from .type to the wrapper class CW/CL (and maybe an error value or None value),
        # so we might want an easier way, so you can just give a dict of types -> classes, or so
        t = fixed_type_instance.type #k
        if t is ListInstanceType:####@@@@
            helper = CL(fixed_type_instance)
        else:
            helper = CW(fixed_type_instance) ###stub, also handle None, error
        return helper
    pass

class CW(DelegatingInstance_obs):
    #e make sure arg has a layout box -- can't we do this by some sort of type coercion? for now, just assume it does.
    # that means it'll have height, since all lboxes have that even if it's not fundamental.
    # all we might need to add is empty = False.
    empty = False #k might work
    pass

class CL(InstanceOrExpr):
    """[private to Column]
    Handle a List expr instance given to Column, directly or indirectly in its nested-list argument values.
    Specifically, use CLE to treat list elements as contributing sometimes-empty sequences of column elements.
    """
    # 061106 possible newer version of the self.elts definition of instantiated args (older one moved to an outtakes file):
    elts = ArgList( CLE) # can it be that simple? and can this replace all references herein to self.args or self.kids? I think so. ####k


    # == figure out what to draw,
    # based on which elements need gaps inserted between them;

    # the main result is self.drawables (the recomputable ordered list of nonempty elements and gaps to draw);

    # the main input is self.elts, a list (not dict) of element-instances,
    # whose values (as determined by the code above) are fixed CLE instances, one per CL argument.

    # (The only reason it can't be a dict is that we use the list-subsequence syntax on it, self.elts[i1:i2],
    #  when we want to move from one place in it to another.
    #  We also might like to use "map" to create it, above... but index is needed, so maybe that's not relevant...
    #  but we might use list extension... OTOH, to be lazy, we might like a compute rule for set of indices, and for kid-code...)
    def nonempty_elts(self, i1 = 0, i2 = -1):
        """Return the current list of nonempty elts, out of the list of all elts
        between the given between-elt indices (but i2 = -1 means include all elts)"""
        if i2 == -1:
            # we use -1, since 0 could be legal, getting an empty list.
            # WARNING: meaning would differ if i2 = -1 was an elt index --
            # in that case, -1 would be equivalent to len - 1, not len.
            i2 = len(self.elts)
        # if elts know their own indices, or (better?) if gaps depend on their id not index,
        # we can just grab & filter the elts themselves:
        return filter(lambda elt: elt.nonempty, self.elts[i1:i2])
    def insert_gaps(self, elts):
        "Given a list of 0 or more of our elts, return a new list with appropriate gap objects inserted between the elements."
        return interleave_by_func(self.elts, self.gapfunc)
    def gapfunc(self, elt1, elt2):
        "find or make a gap object to be drawn between a given two of our elements"
        #e in real life, we'd memoize not on e1 and e2 themselves, but we'd eval their current gap-influencer (perhaps still an instance obj)
        # and memoize on that. this would be to support fancy gaps, actually drawn, with mouse bindings, colored indicators, variable height...
        # ... correction: what we'd memoize on would probably be elt1.last_nonempty_elt and elt2.first_nonempty_elt -- not sure...
        return self._constant_gap #e for now, only constant gap is supported
    def _C__constant_gap(self):
        return Spacer(0,self.gap) # this is only constant at a given time -- self.gap itself can be a formula (vary with time), that's ok
        # note that this spacer can be drawn in more than one place! I guess that's ok since it's not highlightable and has no transparent parts. #k
    #
    def _C_drawables(self):
        "maintain our list of elts and gaps to draw -- the nonempty elts, and gaps between them"
        return self.insert_gaps(self.drawable_elts)
    def _C_drawable_elts(self):
        return self.nonempty_elts()
    #
    def _C_first_nonempty_elt(self): #k needed?
        ne = self.drawable_elts
        if not ne: return None
        return ne[0]
    def _C_last_nonempty_elt(self): #k needed?
        ne = self.drawable_elts
        if not ne: return None
        return ne[-1]
    def _C_nonempty(self):
        # worth _C_ rather than _get_, to memoize it,
        # in case a future optim diffs successive values and avoids inval
        # (if that happens in this lval as opposed to in whoever uses it #k)
        return not not self.drawable_elts
    def _get_empty(self):
        return not self.nonempty
    # == relative coordinates, for redrawing specific parts
    def move_from_top_to_kidindex(self, i2): ###@@@ CALL ME? not quite sure how this is called... esp due to its top-dependence...
        # i2 is an elt-index of an elt we drew, and we want to move from top, to top of that elt; needn't be fast.
        h = 0
        for d in self.drawables:
            if d.index == i2: ###k; what about the spacer? does it have some "default" index, repeated but never equal to i2?
                # move down over accumulated distance before we hit this elt
                self.glpane.move_down(h)
                return
            h += d.height
        assert False, "didn't find index %r" % i2
    # == compute layout-box of whole from lboxes of drawable parts
    def _C_height(self):
        return sum([d.height for d in self.drawables])
    def _C_btop(self):
        if not self.elts:
            return 0
        return self.elts[0].btop # assumes we have some elts; intentionally ignores whether elts[0] is empty, or its bbottom or gap.
    def _C_bbottom(self):
        return self.height - self.btop # an anti-optim no one should mind: depends needlessly on elts[0].btop.
            #e [someday, optim: can we declare that lack of dependence, and explicitly remove the usage-record? doesn't matter in this example.]
    def _C_bleft(self):
        return max([d.bleft for d in self.drawables] or [0])
    def _C_bright(self):
        return max([d.bright for d in self.drawables] or [0])
    # == drawing code
    def draw_from_top_to_bottom(self):
        for d in self.drawables:
            d.draw_from_top_to_bottom()
        return
    pass # end of class CL

class CW_scratch:
    empty = False
    nonempty = True #e it might be nice if we only needed one of these -- not important for now
    def draw_from_top_to_bottom(self):
        self.glpane.move_down(self.btop) # move to origin
        self.draw() # does this leave end pos fixed, or undefined? assume fixed for now. ###k
        self.glpane.move_down(self.bbottom) # move to bottom
    pass

# missing from CL_scratch: creating elt kids. esp with .index; running formulas. not even sure of role of gaplike formulas in CL --
#  does it no longer have any two-way interfaces anywhere??
# missing from recent coding: fill in inval stubs; anything about make, lexenv.

class LayoutWidget2D(Widget2D): pass #####@@@@@ get from layout.py

class Column(LayoutWidget2D):
    """Column(w1, w2, w3) arranges one or more widgets in a vertical column, aligned by their drawing-origins,
    with w1's drawing origin inherited by the entire column.
       The arguments can actually be variable nested lists of widgets; for convenience, None is equivalent to [].
    For example, Column(w1, [w2, w3]) is equivalent to Column(w1, w2, w3), and Column(w1, If(cond, w2, None)) is
    equivalent to If(cond, Column(w1, w2), w1) (except perhaps for efficiency issues).
       The arguments can even contain refs to lists of widgets computed separately [#e syntax for this is not yet devised],
    with lists and sublists in those values properly interpreted as indicating vertical arrangement.
       Gap widgets (simple spacers, by default) are automatically inserted between adjacent drawn widgets;
    in general they can be arbitrary widgets which depend on the ones they're inserted between,
    in appearance and behavior [but this dependence is nim].
       ###e TBD: options for gapfunc or spacing. options for alignment, or for wrapping all elts with something.
    """
    # we work by using helper functions CL, CW, CLE...
    def _init_instance(self):
        self._value = CLE(list(self._e_args)) # 061106 educated guess: self.args -> self._e_args, assuming _value is auto-instantiated
            # or that the below does that -- not reviewed now. #####@@@@@
        printnim("Column _vlaue instantiation not reviewed")

            #k do we need to instantiate this, or is that automatic somehow? guess: we do, though a class assignment of it would not.
        self._value = self.make(self._value)
        #### might be better to assign expr to self._E__value (or _C__value??), letting self._value be automade from that --
        # then it can include '_value' as relative index, too.
        ###e Now we have to make self.draw work, here or in CLE.
    pass


# == junk or scratch below here

# understand understood -- only a big comment, NewInval.py: 275: # env + expr -> understood expr (in that env), an obj with attrs (oresmic?)

if 0:
 understood_expr = env.understand_expr(expr, lexmods = None) # retval contains env + lexmods. we do this inside another understood expr... expr itself has no env.
    # understand_expr can be done by anything with an env (it's delegated to that env), and it's done by a portion of the env, the expr-understander,
    # which includes the lexenv.
    # btw this also handles kluges like [x,y] -> list_Expr(x,y). it might wrap nonobvious python constants with constant_Expr.
    # btw it also does replacements, or binds in enough info to do them lazily.

 ## understood_expr._e_make_in(env.place, index)
 understood_expr._e_make_in(env, index_path)
 #k - where to make things -- a portion of env says that; and how (glp vs pov) -- ditto [ambig with understanding it??];
    # but we also have to supply a local-where, ie an index.
    # and i forget if the various *kinds* of places (datalayers), which use index indeply & could be revised indeply, should be in one env.place thing...
    # this maker, if it makes something with kids, should make lexmods containing the new index prepended onto a path (inside->outside order, functional),
    # perhaps interning the path... and put that in the env to be given to those kids, which is "this instance's env".

class KidMakingUtilsMixin:
    def make_kid(self, expr, index, lexmods = None):
        "for use in certain kinds of compute rules for kids"
        understood_expr = self.env.understand_expr(expr, lexmods = lexmods) # ideally the caller would split this out, if making several kids from this
            ###e to facilitate that, do we offer autoprefixes for understood versions of kid-expr attrs (usually args)? no, too weird to be worth it.
            # or just self.understand? probably. someday, a better formula notation so it's easy to set these things up per-use.
        return understood_expr._e_make_in(self.env, index_path)
    # standard compute rules for kids - set up set of kid indices, and func from index to code (aka expr), lexmods. let recompute rules do the rest.
    def _in_kids_i_C_val(self, i): ##???
        # get code, get lexmods, call make_kid...
        pass
    pass

# end

