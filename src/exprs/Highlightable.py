"""
$Id$

This will start out as just a straight port of class Highlightable from cad/src/testdraw.py,
with the same limitations in API and implem (e.g. it won't work inside display lists).

Later we can revise it as needed.
"""

from basic import *
from basic import _self

from OpenGL.GL import *

# modified from testdraw.printfunc:
def print_Expr(*args, **kws): #e might be more useful if it could take argfuncs too (maybe as an option); or make a widget expr for that
    def printer(_guard = None, args = args):
        assert _guard is None # for now
        printfunc(*args, **kws) # defined in Exprs, has immediate effect, tho same name in testdraw is delayed like this print_Expr
    return canon_expr(printer)

# == selobj interface

###e should define this; see class Highlightable --
# draw_in_abs_coords,
# ClickedOn/leftClick,
# mouseover_statusbar_message
# highlight_color_for_modkeys
# selobj_still_ok, maybe more

# == drag handler interface

# Note: class DragHandler (like some other things defined in this file)
# is also defined in cad/src/testdraw.py, and used there,
# but having this duplicate def should not cause interference.
##e Nonetheless, when things are stable enough, we should clean up and only one of them should remain.

class DragHandler: # implemented in selectMode.py; see leftClick, needed to use this, in this file and in selectMode.py
    "document the drag_handler interface, and provide default method implems" # example subclass: class Highlightable
    ### how does this relate to the selobj interface? often the same object, but different API;
    # drag_handlers are retvals from a selobj method
    def handles_updates(self):
        """Return True if you will do mt and glpane updates as needed,
        False if you want client mode to guess when to do them for you
        (it will probably guess: do both, on mouse down, drag, up;
         but do neither, on baremotion == move, except when selobj changes)
        """
        return False # otherwise subclass is likely to forget to do them
    def DraggedOn(self, event, mode): ### might need better args (the mouseray, as two points? offset? or just ask mode  #e rename
        pass
    def ReleasedOn(self, selobj, mode): ### will need better args ### NOT YET CALLED [guess 061115: this is obs, it is called] #e rename
        pass
    pass

# ==

#e turn these into glpane methods someday, like all the other gl calls; what they do might need to get fancier

def PushName(glname, drawenv = 'fake'):
    glPushName(glname)
    # glpane._glnames was needed by some experimental code in Invisible; see also *_saved_names (several files); might be revived:
    ## glpane = _kluge_glpane()
    ## glpane._glnames.append(glname)
            ###e actually we'll want to pass it to something in env, in case we're in a display list ####@@@@
    return

def PopName(glname, drawenv = 'fake'):
    glPopName() ##e should protect this from exceptions
            #e (or have a WE-wrapper to do that for us, for .draw() -- or just a helper func, draw_and_catch_exceptions)
    ## glpane = _kluge_glpane()
    ## popped = glpane._glnames.pop()
    ## assert glname == popped
    return

# ==

# 061115

def StatePlace(kind, ipath_expr): # experimental; sort of a sister to Arg/Option/Instance; likely to get revised a lot
    """turn into a formula (for use in class assignment)
    which will eval to a permanent reference to a (found or created) attrholder
    for storing state of the given kind, at the given ipath (value of ipath_expr),
    relative to the env of the Instance this is used in.
    """
    return call_Expr( StatePlace_helper, _self, kind, ipath_expr )

def StatePlace_helper( self, kind, ipath): # could become a method in InstanceOrExpr, if we revise StatePlace macro accordingly
    key = (kind,ipath) ##e kind should change which state obj we access, not just be in the key
    state = self.env.state
        # I must have the name wrong [where i am 061115 late] --
        ## AttributeError: 'NoneType' object has no attribute 'state'
        ##  [lvals.py:160] [Exprs.py:193] [Exprs.py:413] [Highlightable.py:89] [Delegator.py:10]

    res = state.setdefault(key, None) 
        # I wanted to use {} as default and wrap it with attr interface before returning, e.g. return AttrDict(res),
        # but I can't find code for AttrDict right now, and I worry its __setattr__ is inefficient, so this is easier:
    if res is None:
        res = attrholder()
        state[key] = res
    return res

def set_default_attrs(obj, **kws): #e refile in py_utils
    "for each attr=val pair in **kws, if attr is not set in obj, set it (using hasattr and setattr on obj)"
    for k, v in kws:
        if not hasattr(obj, k):
            setattr(obj, k, v)
        continue
    return

def recycle_glselect_name(glpane, glname, newobj): #e refile next to alloc_my_glselect_name in cad/src/env.py, or merge this with it somehow
    # 1. [nim] do something to make the old obj using this glname (if any) no longer valid,
    # or tell it the glname's being taken away from it (letting it decide what to do then, eg destroy itself), or so --
    # requires new API (could be optional) in objs that call alloc_my_glselect_name. ##e
    # 2. If the old obj is the glpane's selobj, change that to point to the new obj! MIGHT BE REQUIRED. ###BUG UNTIL DONE
    # 3. register the new object for this glname.
    import env
    oldobj = env.obj_with_glselect_name.get(glname, None) #e should be an attr of the glpane (or of one it shares displaylists with)
    if oldobj is not None and glpane.selobj is oldobj:
        glpane.selobj = newobj
            ###k we might need to call some update routine instead, like glpane.set_selobj(newobj),
            # but I'm not sure its main side effect (env.history.statusbar_msg(msg)) is a good idea here,
            # so don't do it for now.
    env.obj_with_glselect_name[glname] = newobj
    return

# ==

printdraw = False # debug flag [same name as one in cad/src/testdraw.py]

class Highlightable(InstanceOrExpr, DelegatingMixin, DragHandler): #e rename to Button? make variant called Draggable?
    """Highlightable(plain, highlighted = None, pressed_in = None, pressed_out = None)
    renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight
    [and has more, so as to be Button #doc #e rename #e split out draggable of some sort]
    """
    #060722;
    # revised for exprs module, 061115 [not done]
    # note: uses super InstanceOrExpr rather than Widget2D so as not to prevent delegation of lbox attrs (like in Overlay)
    #
    # old comment from testdraw.py, as of 061115 I don't even know if it was obs when there:
    # Works, except I suspect the docstring is inaccurate when it says "plain plus highlight" (rather than just highlight), 
    # and there's an exception if you try to ask selectMode for a cmenu for this object, or if you just click on it
    # (I can guess why -- it's a selobj-still-valid check I vaguely recall, selobj_still_ok):
    #   atom_debug: ignoring exception: exceptions.AttributeError: killed
    #   [modes.py:928] (i.e. selobj_still_ok) [Delegator.py:10] [inval.py:192] [inval.py:309]
    
    # args (which specify what it looks like in various states)
    plain = Arg(Widget2D)
    delegate = _self.plain # always use this one for lbox attrs, etc
    highlighted = Arg(Widget2D, _self.plain)
        # fyi: leaving this out is useful for things that just want a glname to avoid mouseover stickiness
        # implem note: this kind of _self-referential dflt formula is not tested, but ought to work;
        # btw it might not need _self, not sure, but likely it does --
        # that might depend on details of how Arg macro uses it ###k
    # these next args are really meant for Button -- maybe we split this into two variants, Button and Draggable
    pressed_in = Arg(Widget2D, _self.highlighted)
        #e might be better to make it plain (or highlighted) but with an outline, or so...)
    pressed_out = Arg(Widget2D, _self.plain)
        # ... good default, assuming we won't operate then

    # options
    sbar_text = Option(str, "") # mouseover text for statusbar
    on_press = Option(Action)
    on_release_in = Option(Action)
    on_release_out = Option(Action)
    
    # refs to places to store state of different kinds, all of which is specific to this Instance (or more precisely to its ipath)
    ##e [these will probably turn out to be InstanceOrExpr default formulae]
    transient_state = StatePlace('transient', _self.ipath) # state which matters during a drag; scroll-position state; etc
    glpane_state = StatePlace('glpane', _self.ipath) # state which is specific to a given glpane
    per_frame_state = StatePlace('per_frame', _self.ipath) # state which is only needed while drawing one frame (someday, cleared often)
    
    # abbrevs for read-only state
    glname = glpane_state.glname

    def _init_instance(self):
        super(Highlightable, self)._init_instance()

        # == transient_state
        
        set_default_attrs( self.transient_state, in_drag = False) # sets only the attrs which are not yet defined
        # some comments from pre-exprs-module, not reviewed:
            ## in_drag = False # necessary (hope this is soon enough)
        # some comments from now, 061115:
            # but we might like formulas (eg in args) to refer to _self.in_drag and have that delegate into this...
            # and we might like external stuff to see things like this, and of course to pass arb actions
            # (not all this style is fully designed, esp how to express actions on external state --
            #  i guess that state should have a name, then we have an action object, when run it has side effect to modify it
            #  so no issue of that thing not knowing to run it, as there would be from a "formula contribution to an external lval";
            #  but from within here, the action is just a callable to call with whatever args it asks for, perhaps via formulae.
            #  it could be a call_Expr to eval!)

        # == glpane_state
        
        set_default_attrs( self.glpane_state, glname = None) # glname, if we have one

        # allocate glname if necessary, and register self (or a new obj we make for that purpose #e) under glname
        # (kicking out prior registered obj if necessary)
        # [and be sure we define necessary methods in self or the new obj]
        glname_handler = self # self may not be the best object to register here, though it works for now

        if self.glpane_state.glname is None:
            # allocate a new glname for the first time (specific to this ipath)
            import env
            self.glpane_state.glname = env.alloc_my_glselect_name( glname_handler)
        else:
            # reuse old glname for new self
            if 0:
                # when we never reused glname for new self, we could do this:
                self.glpane_state.glname = env.alloc_my_glselect_name( glname_handler)
                    #e if we might never be drawn, we could optim by only doing this on demand
            else:
                # but now that we might be recreated and want to reuse the same glname for a new self, we have to do this:
                glname = self.glpane_state.glname
                recycle_glselect_name(self.env.glpane, glname, glname_handler)
            pass

        # == per_frame_state
        
        set_default_attrs( self.per_frame_state, saved_modelview_matrix = None) #k safe? (why not?) #e can't work inside display lists
        
        return # from _init_instance
    
    def draw(self):
        self.per_frame_state.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
            ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
        PushName(self.glname)
        if self.transient_state.in_drag:
            if printdraw: print "pressed_out.draw",self
            self.pressed_out.draw() #e actually this might depend on mouseover, or we might not draw anything then...
                # but this way, what we draw when mouse is over is a superset of what we draw in general,
                # easing eventual use of highlightables inside display lists. See other drawing done later when we're highlighted
                # (ie when mouse is over us)... [cmt revised 061115]
            # Note, 061115: we don't want to revise this to be the rule for self.delegate --
            # we want to always delegate things like lbox attrs to self.plain, so our look is consistent.
            # But it might be useful to define at least one co-varying attr (self.whatwedraw?), and draw it here. ####e
        else:
            ## print "plain.draw",self
            self.plain.draw()
        PopName(self.glname)
        return

    def draw_in_abs_coords(self, glpane, color):
        # [this API comes from GLPane behavior:
        # - why does it pass color? historical: so we can just call our own draw method, with that arg (misguided even so??)
        # - what about coords? it has no way to know old ones, so we have no choice but to know or record them...
        # ]
        # restore coords [note: it won't be so simple if we're inside a display list which is drawn in its own relative coords...]
        ##glMatrixMode(GL_MODELVIEW) #k prob not needed
        glPushMatrix()
        glLoadMatrixd(self.per_frame_state.saved_modelview_matrix)
        # examples of glLoadMatrix (and thus hopefully the glGet for that) can be found in these places on bruce's G4:
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/OpenGLContext/renderpass.py
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/VisionEgg/Core.py
        if self.transient_state.in_drag:
            if printdraw: print "pressed_in.draw",self
            self.pressed_in.draw() #e actually might depend on mouseover, or might not draw anything then...
        else:
            if printdraw: print "highlighted.draw",self
            self.highlighted.draw()
        glPopMatrix()
        return

    def __repr__THAT_CAUSES_INFRECUR(self):
        # this causes infrecur, apparently because self.sbar_text indirectly calls __repr__ (perhaps while reporting some bug??);
        # so I renamed it to disable it and rely on the super version.
        sbar_text = self.sbar_text or ""
        if sbar_text:
            sbar_text = " %r" % sbar_text
        return "<%s%s at %#x>" % (self.__class__.__name__, sbar_text, id(self)) ##e improve by merging in a super version
        ## [Highlightable.py:260] [ExprsMeta.py:250] [ExprsMeta.py:318] [ExprsMeta.py:366] [Exprs.py:184] [Highlightable.py:260] ...
    
    def mouseover_statusbar_message(self): # called in GLPane.set_selobj
        return self.sbar_text or "%r" % (self,)
    
    ###@@@ got to here, roughly
    
    def highlight_color_for_modkeys(self, modkeys):
        """#doc; modkeys is e.g. "Shift+Control", taken from glpane.modkeys
        """
        return green
            # KLUGE: The specific color we return doesn't matter, but it matters that it's not None, to GLPane --
            # otherwise it sets selobj to None and draws no highlight for it.
            # (This color will be received by draw_in_abs_coords, but our implem of that ignores it.)
    def selobj_still_ok(self, glpane):
        ###e needs to compare glpane.part to something in selobj, and worry whether selobj is killed, current, etc
        # (it might make sense to see if it's created by current code, too;
        #  but this might be too strict: self.__class__ is Highlightable )
        # actually it ought to be ok for now:
        res = self.__class__ is Highlightable # i.e. we didn't reload this module since self was created
        import env
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None.
    ### grabbed from Button, maybe not yet fixed for here
    def leftClick(self, point, mode):
        self.transient_state.in_drag = True
        self.inval(mode)
        self._do_action('on_press')
        return self # in role of drag_handler
    def DraggedOn(self, event, mode):
        # only ok for Button so far
        #e might need better args (the mouseray, as two points?) - or get by callback
        # print "draggedon called, need to update_selobj, current selobj %r" % mode.o.selobj
        mode.update_selobj(event)
        #e someday, optim by passing a flag, which says "don't do glselect or change stencil buffer if we go off of it",
        # valid if no other objects are highlightable during this drag (typical for buttons). Can't do that yet,
        # since current GLPane code has to fully redraw just to clear the highlight, and it clears stencil buffer then too.

        # for dnd-like moving draggables, we'll have to modify the highlighting alg so the right kinds of things highlight
        # during a drag (different than what highlights during baremotion). Or we might decide that this routine has to
        # call back to the env, to do highlighting of the kind it wants [do, or provide code to do as needed??],
        # since only this object knows what kind that is.
        return
    
    def ReleasedOn(self, selobj, mode): ### will need better args
        ### written as if for Button, might not make sense for draggables
        self.transient_state.in_drag = False
        self.inval(mode)
        if selobj is self: #k is this the right selobj? NO! or, maybe -- this DH is its own selobj and vice versa
            self._do_action('on_release_in')
        else:
            self._do_action('on_release_out')
        ## mode.update_selobj(event) #k not sure if needed -- if it is, we'll need the 'event' arg
        #e need update?
        return
    
    def _do_action(self, name):
        "[private, should only be called with one of our action-option names]"
        print "_do_action",name ###
        assert name.startswith('on_')
        ## action = self.kws.get(name)
        action = getattr(self, name) # will always be defined, since Option will give it a default value if necessary
        # should be None or a callable supplied to the expr, for now; later will be None or an Action
        if action:
            action()
        return

    def inval(self, mode):
        """we might look different now;
        make sure display lists that might contain us are remade [stub],
        and glpanes are updated
        """
        ## vv.havelist = 0
        mode.o.gl_update()
        return
    
    pass # end of class Highlightable (a widgetexpr, and one kind of DragHandler)

Button = Highlightable

# == old comments, might be useful (e.g. the suggested formulas involving in_drag)

# I don't think Local and If can work until we get WEs to pass an env into their subexprs, as we know they need to do ####@@@@

# If will eval its cond in the env, and delegate to the right argument -- when needing to draw, or anything else
# Sensor is like Highlightable and Button code above
# Overlay is like Row with no offsetting
# Local will set up more in the env for its subexprs
# Will they be fed the env only as each method in them gets called? or by "pre-instantiation"?

##def Button(plain, highlighted, pressed_inside, pressed_outside, **actions):
##    # this time around, we have a more specific API, so just one glname will be needed (also not required, just easier, I hope)
##    return Local(__, Sensor( # I think this means __ refers to the Sensor() -- not sure... (not even sure it can work perfectly)
##        0 and Overlay( plain,
##                 If( __.in_drag, pressed_outside),
##                 If( __.mouseover, If( __.in_drag, pressed_inside, highlighted )) ),
##            # what is going to sort out the right pieces to draw in various lists?
##            # this is like "difference in what's drawn with or without this flag set" -- which is a lot to ask smth to figure out...
##            # so it might be better to just admit we're defining multiple different-role draw methods. Like this: ###@@@
##        DrawRoles( ##e bad name
##            plain, dict(
##                in_drag = pressed_outside, ### is this a standard role or what? do we have general ability to invent kinds of extras?
##                mouseover = If( __.in_drag, pressed_inside, highlighted ) # this one is standard, for a Sensor (its own code uses it)
##            )),
##        # now we tell the Sensor how to behave
##        **actions # that simple? are the Button actions so generic? I suppose they might be. (But they'll get more args...)
##    ))

# == old code

# kluge to test state toggling:

if 0:

    def bcolor(env, nextness = 0):
        n = vv.state.setdefault('buttoncolor',0)
        return (green, yellow, red)[(n + nextness) % 3]

    def next_bcolor(env):
        return bcolor(env, 1)

    def toggleit():
        n = vv.state.setdefault('buttoncolor',0)
        n += 1
        n = n % 3
        vv.state['buttoncolor'] = n
        return

    def getit(fakeenv): # note: the bug of saying getit() rather than getit in an expr was hard to catch; will be easier when env is real
        return "use displist? %s" % ('no', 'yes')[not not USE_DISPLAY_LIST_OPTIM]

    def setit(val = None):
        global USE_DISPLAY_LIST_OPTIM
        if val is None:
            # toggle it
            val = not USE_DISPLAY_LIST_OPTIM
        USE_DISPLAY_LIST_OPTIM = not not val
        vv.havelist = 0
        print "set USE_DISPLAY_LIST_OPTIM = %r" % USE_DISPLAY_LIST_OPTIM

    displist_expr_BUGGY = Button(Row(Rect(0.5,0.5,black),TextRect(18, 2, getit)), on_press = setit)
        # works, but has bug: not sensitive to baremotion or click on text if you drag onto it from empty space,
        # only if you drag onto it from the Rect.
        
    displist_expr = Row(
        Button( Rect(0.5,0.5,black), DebugDraw( Rect(0.5,0.5,gray), "grayguy"), on_press = setit),
        TextRect(18, 2, getit))

if 0:
    
    Column(
      Rect(1.5, 1, red),
      ##Button(Overlay(TextRect(18, 3, "line 1\nline 2...."),Rect(0.5,0.5,black)), on_press = print_Expr("zz")),
          # buggy - sometimes invis to clicks on the text part, but sees them on the black rect part ###@@@
          # (see docstring at top for a theory about the cause)
      
    ##                  Button(TextRect(18, 3, "line 1\nline 2...."), on_press = print_Expr("zztr")), # 
    ##                  Button(Overlay(Rect(3, 1, red),Rect(0.5,0.5,black)), on_press = print_Expr("zzred")), # works
    ##                  Button(Rect(0.5,0.5,black), on_press = print_Expr("zz3")), # works
      Invisible(Rect(0.2,0.2,white)), # kluge to work around origin bug in TextRect ###@@@
      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),
      Rect(1.5, 1, green),
      gap = 0.2
    ## DrawThePart(),
    )

    Column(
        Rotated( Overlay( RectFrame(1.5, 1, 0.1, white),
                          Rect(0.5,0.5,orange),
                          RectFrame(0.5, 0.5, 0.025, ave_colors(0.5,yellow,gray))
                          ) ),
        Pass,
        Overlay( RectFrame(1.5, 1, 0.1, white),
                 Button(
                     FilledSquare(bcolor, bcolor),
                     FilledSquare(bcolor, next_bcolor),
                     FilledSquare(next_bcolor, black),
                     FilledSquare(bcolor, gray),
                     on_release_in = toggleit
                )
        ),
    )

    Closer(Column(
        Highlightable( Rect(2, 3, pink),
                       # this form of highlight (same shape and depth) works from either front or back view
                       Rect(2, 3, orange), # comment this out to have no highlight color, but still sbar_text
                       # example of complex highlighting:
                       #   Row(Rect(1,3,blue),Rect(1,3,green)),
                       # example of bigger highlighting (could be used to define a nearby mouseover-tooltip as well):
                       #   Row(Rect(1,3,blue),Rect(2,3,green)),
                       sbar_text = "big pink rect"
                       ),
        #Highlightable( Rect(2, 3, pink), Closer(Rect(2, 3, orange), 0.1) ) # only works from front
            # (presumably since glpane moves it less than 0.1; if I use 0.001 it still works from either side)
        Highlightable( # rename? this is any highlightable/mouseoverable, cmenu/click/drag-sensitive object, maybe pickable
            Rect(1, 1, pink), # plain form, also determines size for layouts
            Rect(1, 1, orange), # highlighted form (can depend on active dragobj/tool if any, too) #e sbar_text?
            # [now generalize to be more like Button, but consider it a primitive, as said above]
            # handling_a_drag form:
            If( True, ## won't work yet: lambda env: env.this.mouseoverme , ####@@@@ this means the Highlightable -- is that well-defined???
                Rect(1, 1, blue),
                Rect(1, 1, lightblue) # what to draw during the drag
            ),
            sbar_text = "little buttonlike rect"
        )
    ))

## testdraw2_cannib.py: 89:         on_press = ToggleAction(stateref)
