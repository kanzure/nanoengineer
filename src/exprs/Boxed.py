"""
Boxed.py -- example of high-level layout expr

$Id$
"""

from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

import Center
reload_once(Center)
from Center import Center

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

import draggable
reload_once(draggable)
from draggable import DraggableObject, SimpleDragBehavior

class Boxed(InstanceMacro): # 070316 slightly revised
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are pixelgap = 4 (in pixels), borderwidth = 4 (in pixels), bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
       WARNING: some deprecated but commonly used options are given in model units, not in pixels (probably a design flaw).
    """
    # WARNING: would not work if it inherited from Widget2D,
    # since it would pick up Widget2D default values for lbox attrs like btop. [unconfirmed but likely; 061127 comment]

    # args
    thing = Arg(Widget2D)
    
    # options
    borderwidth = Option(int, 4) # 070305 new feature -- specified in pixels
    borderthickness = Option(Width, borderwidth * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS); commonly used, but deprecated as of 070305
        # (warning: borderthickness is still used as an internal formula when not supplied)
        # (WARNING: supplying both forms is an error, but is not detected;
        #  this might cause bugs that are hard for the user to figure out
        #  if the different option forms were used in successive customizations of the same expr)
    
    pixelgap = Option(int, 4) # 070305 new feature [#e rename gap? bordergap? (change all gap options to being in pixels?)]
        # (maybe not yet tested with nonzero passed-in values)
    gap = Option(Width, pixelgap * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS), commonly used, but deprecated as of 070305
        # (see also the comments for borderthickness)
        # (warning: gap is still used as an internal formula when not supplied)
    
    bordercolor = Option(Color, white)
    
    # internal formulae
    extra1 = gap + borderthickness
    ww = thing.width  + 2 * extra1 #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    hh = thing.height + 2 * extra1
    rectframe = RectFrame( ww, hh, thickness = borderthickness, color = bordercolor)
    # appearance
    _value = Overlay( Translate( rectframe,
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                      thing)
    pass

# ==

class DraggablyBoxed(Boxed): # 070316; works 070317 [testexpr_36] before ww,hh State or resizable, and again (_36b) after them
    # inherit args, options, formulae from Boxed
    thing = _self.thing ###k WONT WORK unless we kluge ExprsMeta to remove this assignment from the namespace -- which we did.
        ###e not sure this is best syntax though. attr = _super.attr implies it'd work inside larger formulae, but it can't;
        # attr = Boxed.attr might be ok, whether it can work is not reviewed; it too might imply what _super does, falsely I think.
    extra1 = _self.extra1 
    rectframe = _self.rectframe # a pure expr
    # new option
    resizable = Option(bool, False, doc = "whether to make it resizable at lower right")
        # works 070317 10pm (testexpr_36b) except for 4 ###BUGS:
        # - wrong corner resizes (top right)
        # - resizer doesn't move
        # - negative sizes allowed
        # - no clipping to interior of rectframe
        # also, ###UNTESTED in rotated coordsys.
        # also the resizer is ugly.
    # state
        # WARNING: due to ipath persistence, if you revise dflt_expr you apparently need to restart ne1 to see the change.
##    ww = State(Width, thing.width  + 2 * extra1) # replaces non-state formula in superclass -- seems to work
##    hh = State(Width, thing.height + 2 * extra1)
##        # now we just need a way to get a stateref to, effectively, the 3-tuple (ww,hh,set-value-discarder) ... instead, use whj:
    whj = State(Vector, V_expr(thing.width  + 2 * extra1, thing.height + 2 * extra1, 0)) #e not sure this is sound in rotated coordsys
    translation = State(Vector, ORIGIN)
    # override super formulae
    ww = whj[0] # seems to work
    hh = whj[1]
    # appearance
    rectframe_h = Instance( Highlightable(
        ## rectframe(bordercolor=green),####### cust is just to see if it works -- it doesn't, i guess i sort of know why
        ##bug: __call__ of <getattr_Expr#8243: (S._self, <constant_Expr#8242: 'rectframe'>)> with: () {'bordercolor': (0.0, 1.0, 0.0)}
        ##AssertionError: getattr exprs are not callable 
        rectframe,
        #e different colored hover-highlighted version?? for now, just use sbar_text to know you're there.
        sbar_text = "draggable box frame", # this disappears on press -- is that intended? ###k
        behavior = SimpleDragBehavior(
            # arg1: the highlightable
            _self.rectframe_h,
            # arg2: a write-capable reference to _self.translation
            ## fails - evalled at compile time, not an expr: LvalueFromObjAndAttr( _self, 'translation'),
                ###BUG: why didn't anything complain when that bug caused the state value to be an add_Expr, not a number-array?
            call_Expr( LvalueFromObjAndAttr, _self, 'translation'),
                #e alternate forms for this that we might want to make work:
                #  - getattr_StateRef(_self, 'translation') # simple def of the above
                #  - StateRef_for( _self.translation ) # turns any lvalue into a stateref! Name is not good enough, though.
         )
     ))
    resizer = Instance( Highlightable(
        Center(Rect(extra1, extra1)), #e also try BottomRight
        Center(Rect(extra1, extra1, white)),
        sbar_text = "resize the box frame",
        behavior = SimpleDragBehavior( _self.resizer, call_Expr( LvalueFromObjAndAttr, _self, 'whj') )
     ))
    drawme = Instance( Overlay(
        thing,
        Translate( rectframe_h,
                   - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ),
        If( resizable,
            Translate( resizer, V_expr( thing.bright + extra1, - thing.bbottom - extra1))
         )
     ))
    _value = Translate( drawme, ## DisplistChunk( drawme), ###k this DisplistChunk might break the Highlightable in rectframe_h #####
                        translation
                       )
    pass

# end
