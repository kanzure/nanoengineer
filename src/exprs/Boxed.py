'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *

# How to support higher-level definitions of exprheads?

# One style would be to let people set up rules using 'def', like they might guess.

# The only thing clearly impossible to support, this way, without big kluges,
# would be customization without supplying args, e.g. Boxed(thickness = 5),
# or automatic use of the name 'Boxed' when looking up env defaults.
# Those could probably be added later by saying Boxed = xxx(Boxed) lower down.

# What could probably be supported includes arbitrary options (mixed in by building exprs to use them)
# and letting Python do the lexical symbol creation and replacement (via def).
# It will only work when this replacement is ok to do fully at parsing time
# (not always true, but often enough to be useful).
# The post-wrapping trick (Boxed = xxx(Boxed)) might handle that too.

# It's still necessary to be careful, when using this style -- the only thing resolved
# when the def runs is the exprs used as arguments -- nothing is instantiated,
# and we're not even in a specific env for understanding exprs,
# so we don't even know types, let alone per-frame data.

# [later: the big confusions or problems in this try1 were:
#  - how to resolve thing to an instance -- i ended up probably wanting to require supply of an index-path, to make an instance;
#  - how to prefix attrnames for use in formula rhses;
#    - how to make formulas only once [maybe not mentioned in comments in try1 below]
#  and they led me to decide to package this into a class.
# ]

def Boxed_try1(thing, **opts):
    defaults = dict(borderthickness = 4, gap = 4, bordercolor = white)
    ## combine opts, and defaults ...
    thing = Instance(thing) ###k like type coercion, but a kind of "resolving" instead... (??)
        ###k I'm not sure how this can work -- Instance runs now, so it can do little more than build an expr to record its existence,
        # so what is it that takes a whole expr (our retval) with some refs to a single Instance expr,
        # and knows that that whole expr, each time it's instantiated, is the "unit for Instance"?
        # It has to be an added wrapper on the whole expr which lexically communicates with Instance, I think --
        # and we have to follow a convention that never lets Instance be "free" (as in a free variable)
        # in any expr passed as an arg. I think this requires an explicit wrapper on our return value,
        # and/or a post-wrapper on Boxed, and also (for error detection) a check for "free Instance"
        # in all our arguments.
        ###e rename, to something more active, and to avoid name conflict with class,
        # and to not make it sound like the instance is made right now. ShareInstances?
        ### also should we introduce a label for the "free variable"?
        #  Should we be a helper method in a class, so both post-wrapping and arg processing and API conversion
        # can be done by the class? (probably.) That way we can also write code (in other methods?)
        # which only runs in each instance, and some of it can be recompute rules (though formulas should be ok too, I hope).
        #  In other words, we're turning right into a "python coded" rather than "expr-described" structure,
        # just because we needed an arg thing, and needed access to its per-instance interface.
        # But we can still use a high-level expr to describe the equivalent form.
    ww = thing.width + 2 * gap + 2 * borderthickness # a formula... but where do the symbols come from?
    hh = thing.height + 2 * gap + 2 * borderthickness
    # how do the option symbols in the following get bound to their values, which are formulas? They need an 'xxx.' prefix.
    return Overlay( RectFrame(ww, hh, thickness = borderthickness, color = bordercolor), thing, align = Center )

# [later: this time, I decided to declare arg & option types... some above problems remain, plus when/how to give formulas.]

class Boxed_try2(Widget2D):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are borderthickness = 4, gap = 4, bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
    """
    # arguments
    _args = (
        ('thing', Widget2D),
            # how do we say to resolve it to an instance? is that implicit? if so, how do we say not to? ####@@@@
            # should we specify order and other info separately? (then it's easier for a subclass to override some of it...
            #  and some of it can be specified in same way as for options.
            # we could even say, put an option name in the arglist if you want it to be specifiable either way.
            # but then we'd need a separate arg-defaults dict and arg-types dict -- or per-attr decls, perhaps more flexible.
        )
    _args = ('thing') #k but how to permit defaults? by specifying them separately?
    _ARGTYPE_thing = Widget2D
    _RESOLVE_thing = True ###k or can that be determined by what our formulas access about it? (how deeply they go??) I doubt it.
    
    # option names and default values
    _options = dict(borderthickness = 4, gap = 4, bordercolor = white)
        #e _default_options might differ from _default_formulas, if option defaults can be overridden by the env.
        # but then, why call formulas "defaults"?
    
    # option types are not needed in this case, since the way we use them will coerce them as needed.
    # if they were needed, you could give them like this (with their values allowed to be formulas evalled at runtime):
    ## _option_types = dict(borderthickness = Width, gap = Width, bordercolor = Color) # not needed in this simple case

    # internal computations
    
    #e the following doesn't work, due to namespace needed for rhs symbols:
    _formulas = dict( ww = thing.width + 2 * gap + 2 * borderthickness, hh = thing.height + 2 * gap + 2 * borderthickness )
    # so try this:
    o = self._options_symbol ###k not so fast -- no such thing as "self" yet!
        # (Should I use _self as a symbol for the instance, once it exists?)
    if 'this looks ok':
        #k or would it be better if these were inside a method, with _self as an arg, or self as an arg?
        # the method name could mean it runs when we instantiate, rather than on every frame... like _init_instance or _init_formulas.
        thing = _self.thing
        gap = _self.gap
        borderthickness = _self.borderthickness
        bordercolor = _self.bordercolor
    
    thing
    gap
    borderthickness
    bordercolor
    
    _formulas = dict( ww = thing.width + 2 * gap + 2 * borderthickness, hh = thing.height + 2 * gap + 2 * borderthickness )

    ww = _self.ww
    hh = _self.hh
    
    # equivalent value ~== rule-expansion -- also a formula in this case...
    # (in some cases, ie the ones coded at a lower level, it needs to be an overriding of methods like draw)
    #e this also needs its symbols in some better namespace -- even just to import this file!
    _value = Overlay( RectFrame(ww, hh, thickness = borderthickness, color = bordercolor), thing, align = Center )
    pass

class Boxed_try3(Widget2D):
    "#doc is above"
    # arguments
    _args = ('thing')
    _ARGTYPE_thing = Widget2D
    #k resolve this arg? ###@@@
    # options (name, maybe default, maybe type)
    _options = dict(borderthickness = 4, gap = 4, bordercolor = white) # values could be formulas using _self
        # [later note: this is basically a constant FormulaSet described by a dict.]
    def _init_instance(self):
        "..."
        # what we have available at this point:
        # formulas for options
        self.borderthickness # a symbol? or a value? neither -- someone can pass a formula, so that's what we have.
        self.gap
        self.bordercolor
        # formulas for args:
        self.thing # is this an instance, like the option value formulas are? in fact, are they?? ####@@@@
            # (consider transient state, random choices, and perhaps, in how many places things are drawn re highlighting)

        ### could we refer to an instance made from the arg, or the pure expr arg, by using different xxx in xxx.thing?
        # problem: in e.g. Cube, we might need to control *which* instance we want, if we make several.
        # Can we handle that by supplying an instance-index whenever we want to refer to an instance,
        # and not supplying one when we want to refer to the expr == their class? THAT MIGHT MAKE SENSE.
        # Then the expr is like a big dict of instances, most not made, and we can refer to that
        # (passing it on, perhaps with an implicit delving into subspace of index-paths)
        # or to specific instances within it -- but the latter only by supplying an index.
        # I don't like having to supply one, but something has to, and this might make the situation clearer.... not sure. ####@@@@

        # Related: self.kids, and ways to refer to that, and supply code and indices to it, and perhaps ways to declare it --
        # we could "declare the kids" just as we declare the args and their types.
        # Compare to latest ideas about declaring Column kids. (I mean about creating them.) ####e
        
        pass
    pass

# see also lots of notesfile at this point...

# == status next day 061018: what it feels like is that the biggest undecided thing is how to create kids & refer to them.

# even so, let's just try again:

# (digr: besides Cube,
#  another useful eg is Checkerboard, with separate red & black decorations, both iterated w/in same face-index scheme)

class Boxed_try4(Widget2D):
    "#doc is above"
    # arguments
    _args = ('thing')
    _TYPE_thing = Widget2D
    #k resolve this arg? ###@@@
    ###e say Widget2D.instance as the type??
    # options (name, maybe default, maybe type)
    _options = dict(borderthickness = 4, gap = 4, bordercolor = white) # values could be formulas using _self
        # [later note: this is basically a constant FormulaSet described by a dict.]

    # what is left to do after this?
    # - make thing an instance
    #   - specify its index, for transient state & perhaps other decoration (the Cube eg is a much harder test of how we do this)
    # + compute ww and hh from that instance:
    #   - create formulas at class-def time,
    #   - which instantiate when self does
    #   - and which do inval/update per-frame or less often
    # + define equivalent value (for drawing in OpenGL or POVRay; in other contexts, for all uses, e.g. simulation):
    #   - _value = Overlay( RectFrame(ww, hh, thickness = borderthickness, color = bordercolor), thing, align = Center )
    #   - needs to grab those rhs values as attrs from some object -- maybe _self or self depending on when we do it

    # decisions re above: do these things in per-instance methods, compute methods, or per-class methods or constants?

    # make thing an instance of our arg.
    #####@@@@@@@ PROBLEM: doesn't this contradict the arg decl above, which already assigns to self.thing? #####@@@@@
    # Thus we seem to need to specify a code-wrapper around that value, sort of like a type decl...
    # Can we use as the type, Instance(Widget2D)?
    # Or does Widget2D *imply* Instance? Is that how it works for types like Color & Width? (can you even tell?) ####@@@@
    # Not exactly, I think... hard to say, since an instance is around somewhere, but the direct attr is just the current value.
    # I suppose the current value can *be* an instance, for widgets, even though it has time-varying contents...
    # If that's the system, then how do we say to pass in a Widget Expr rather than a Widget (which is an Instance by implication)??
    
    ###@@@ how hard would it be to make thing an instance in the same way Column does for its elements?
    _CK_kids = (1,) # a formula -- can you tell? (what if it's callable?? this one isn't...) ####@@@@
    _CV_kids = 'pseudocode: instantiate thing' ###k this is normally a method taking an index arg... can it too be a formula?? ####k
    _C_thing = _self.kids[1] # (a formula which indexes a getattr)
    ##e another way would be to use _init_instance to assign self.thing,
    ##e or to let _C_thing directly instantiate thing, as formula or method:
    _C_thing = bla # superseded by above worry about conflict with _TYPE_thing
    
    
    # internal formulas, using new notation in Rect.py.
    # A problem with that notation -- the constrast between _C_ and _self. which seem like they refer to the same thing.
    # Maybe they can be made more similar, and _self shorter... but they can't be identical (one has a '.').
    # Also should _C_ for compute be _F_ for formula, or maybe _S_ for self?
    # I think the method version should be the same prefix, so one overrides the other.
    # Note also that formulas (or compute methods) might come more dynamically from FormulaSet objects or delegates... ###@@@
    _C_extra = 2 * _self.gap + 2 * _self.borderthickness
    _C_ww = _self.thing.width  + _self.extra
    _C_hh = _self.thing.height + _self.extra

    # equivalent value for all uses
    #####@@@@@ should this be a _C_ formula? Guess: yes, at least if it can vary.... and if self.value works to grab current ref obj.
    ###@@@ kluges: _S means _self
    _value = Overlay( RectFrame( _S.ww, _S.hh, thickness = _S.borderthickness, color = _S.bordercolor),
                      _S.thing,
                      align = Center )
    pass # end of class Boxed

# ==

# Would it be useful to try to define several simple things all at once?

# Boxed, Rect, Cube, ToggleShow, Column/Row

# classify them:
# - 2d layout:
#   - Column/Row, Boxed, Checkerboard
# - has kids:
#   - Column
#   - all macros (since _value is a kid, perhaps of null or constant index)
#   - If [and its kids have to be lazy]
#   - Cube, Checkerboard
# - macro:
#   - ToggleShow, Boxed, MT
# - has state:
#   - ToggleShow
# - simple leaf:
#   - Rect
# - complicated options:
#   - Grid
# - complicated visible structure
#   - Cube, Grid, Checkerboard, MT
# - 3d layout
#   - Cube
# - iterator
#   - Cube, Checkerboard

# first: Column, Boxed, Rect, If

