'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *
from basic import _self

from widget2d import Widget2D #####@@@@@ make reloadable

## Overlay = RectFrame = stub # doesn't work, they get called when we import
Stub = Widget2D
Overlay = RectFrame = Center = Stub###@@@

# ==

class Boxed(Widget2D):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are borderthickness = 4, gap = 4, bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
    """
    # arguments
    _args = ('thing')
    _TYPE_thing = Widget2D # automatically instantiated, since we don't say otherwise [#e but how would we say otherwise?]
    # options (name, maybe default, maybe type)
    _options = dict(borderthickness = 4, gap = 4, bordercolor = white) # values could be formulas using _self; computed vals are public(?)
        # [later note: this is basically a constant FormulaSet described by a dict.]
    # internal formulas (computed vals are not public, at least not by default, though for now this is probably not enforced)
    # trying out various syntaxes:
    if 1:
        _ = _self #e can this be done globally, or will it mess up certain IDE debuggers? Guess: it won't, since they'll do it only in __main__. ##k
        #k do i like this _.xxx syntax? Not much...
        extra = 2 * _.gap + 2 * _.borderthickness
        ww = _.thing.width  + _.extra
        hh = _.thing.height + _.extra
    if 0:
        extra = 2 * _self.gap + 2 * _self.borderthickness
        ww = _self.thing.width  + _self.extra
        hh = _self.thing.height + _self.extra
    if 0:
        ###e Would I be allowed to say right here, from __Symbols__ import borderthickness, thing, extra,
        # and then have those syms stand for _self attrs in the following? Would i want to? The formulas become so much clearer!
        # but the pysymbols would then be unwantedly defined inside the methods, right? I guess not, only in the class. Hmm.
        # Oh, but then it can't work, eg the first formula *replaces* extra with that formula... OTOH, can a metaclass fix that?
        # Guess: a metaclass might be able to fix it. The formula-clarity might justify the violation of POLS.
        # That might be mitigated by renaming __Symbols__ somehow, or cloning it to make a variant just for _self attrs. ####k
        # Uh oh, a meta prob can't do it -- these stmts are evalled in a namespace and they do assign to it;
        # I don't think we have any way to replace that ns with a smarter thing, *or* that python can tolerate a smarter thing
        # that modifies assignment (though maybe it can for set just not for get, not sure).
        # OTOH, the result of letting the ns get modified normally is that it contains a graph of exprs with shared subexprs...
        # and most of those are the values of certain attrs. Can't we disentangle that graph and memoize each shared subexpr
        # using the attr it's assigned to, or a new one if needed? Guess: yes, and "formulaness" means lack of infrecur,
        # and the initial import then just serves to permit forward refs to work. So this idea is still on the table.
        from __Symbols__ import borderthickness, thing, extra
        extra = 2 * gap + 2 * borderthickness
        ww = thing.width  + extra
        hh = thing.height + extra
    if 0:
        from _Self import borderthickness, thing, extra # ???
    if 0:
        # Not only that (above), the import of extra is not needed (no fwd ref is used).
        # The ones needed are option/arg names, not internals.
        # What if those args all got declared by direct assignment of some sort? Then we'd need no import at all,
        # provided the disentanglement still worked!
        thing = Arg(Widget2D) # something that makes a unique object that says "arg" and maybe says its type or optional default
            # note, you'd still have to declare the order, unless we kluged that by having Arg remember the order of exec,
            # which might be tolerable -- why not?
            # (For super inheritance, we'd keep order of old args, add new at end. We'd permit _argorder to revise the order.)
        borderthickness = Option(4) #k can default imply type like this? or can we just let type be missing?
        gap = Option(4)
        bordercolor = Option(white)
        extra = 2 * gap + 2 * borderthickness
        ww = thing.width  + extra
        hh = thing.height + extra
        zz = 5 # this would not even be incorrect! it can be allowed to be a constant. (I think.)
        # possible:
        # - We might let ArgOption or OptionArg be something that can be supplied positionally or named;
        # but that might be a confusing term if it sounds like OptionalArg, which any arg with a default value can be.
        # - We might let things like this work in some cases: thing = Arg(number) + 1.
        # I think it's unambiguous since positional means input-only;
        # for Options it won't work (inside/outside vals would need to differ, but can't, I think).

    # equivalent value for all uses (like a macro expansion for Boxed(widget, opts))
    _value = Overlay( RectFrame( _.ww, _.hh, thickness = _.borderthickness, color = _.bordercolor),
                      _.thing, ##e is it ok that the alignment of thing will be lost, re the outside? it's not ideal. how to fix??
                      align = Center )
    pass # end of class Boxed

# end
