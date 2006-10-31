'''
Column.py  [module might be renamed if we add Row, etc, to same file]

$Id$
'''

from basic import * # autoreload of basic is done before we're imported

import draw_utils
reload_once(draw_utils)

from draw_utils import *

import instance_helpers
reload_once(instance_helpers)

from instance_helpers import GlueCodeMemoizer, Instance, DelegatingInstance

from widget2d import Widget2D #####@@@@@ replace with layout, make reloadable

# ==

class CLE(GlueCodeMemoizer): # not reviewed recently
    """Column list element:
    - handles 0 or more actual rows, perhaps varying in time, as described by one formula arg to Column
    - for each instance that formula evals to, this adds type-specific glue code (memoized for that instance) and delegates to it,
      also making the result available as the value of self.delegate
    - also contains the type-specific glue code ### as methods or classes?
    """
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

class CW(DelegatingInstance):
    #e make sure arg has a layout box -- can't we do this by some sort of type coercion? for now, just assume it does.
    # that means it'll have height, since all lboxes have that even if it's not fundamental.
    # all we might need to add is empty = False.
    empty = False #k might work
    pass


class CL(Instance): ###e needs merge into below
    def _init_instance(self):
        self.cles = map(CLE, self.args)
    #e gap formulas, coords/scenegraph/indices/env/spacers/empty
    pass

class CL(Instance):
    """[private to Column]
    Handle a List expr instance given to Column, directly or indirectly in its nested-list argument values.
    Specifically, use CLE to treat list elements as contributing sometimes-empty sequences of column elements.
    """
    # == define the kids [note: the attrname 'kids' is just a convention, i think #e]
    def _CK_kids(self): # compute the set of kid-keys -- in order (required in this class, though not in general)
        return range(len(self.args))
            # if you want to access a memoized version of this, try self.kids.keys() -- but will it be in order?? #####k
            #e implem dictlike.keys_in_order() for that? note: not always the same (in general) as .keys_sorted()!
    def _CV_kids(self, i): # compute the kid value for a given kid-key
        ###WRONG: needs index, and CLE is really _arg or _kid [061018]
        return CLE(self.instantiate(self.args[i]))
            ###k self.instantiate(expr) -> instance, env defaults to self.env... but what index? NEED TO PASS INDEX.
        # about fixing this -- do we understand the arg, and use it, seply? understand in filled expr, use in instance...
        # self.understand(expr)?? or code in _init_expr? or self.arg_expr[i] defined as understood self.arg[i]??
        # what about optval exprs? what about locally constructed exprs, with CLE or Overlay... do we understand whole or arg-part?

    # self.elts is a list of all kids, in order
    #e [optim, someday: make it a lazy-element list, or revise above to define one directly]
    def _C_elts(self):
        return [self.kids[i] for i in self._CK_kids()] #e or, dictmap(self.kids, range(len(self.args))) -- assuming result is a list!
            # WARNING: only works since _CK_kids retval is properly ordered, though it needn't be for its defined use (to help make self.kids).
            # Note: this scheme as a whole is overkill, but as an example for more complex widget expr kidsets, it's useful.

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
        return Spacer((0,self.gap)) # this is only constant at a given time -- self.gap itself can be a formula (vary with time), that's ok
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
        self._value = CLE(list(self.args))
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
    
 ## understood_expr._make_in(env.place, index)
 understood_expr._make_in(env, index_path)
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
        return understood_expr._make_in(self.env, index_path)
    # standard compute rules for kids - set up set of kid indices, and func from index to code (aka expr), lexmods. let recompute rules do the rest.
    def _in_kids_i_C_val(self, i): ##???
        # get code, get lexmods, call make_kid...
        pass
    pass

# end
