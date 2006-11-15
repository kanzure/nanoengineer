"""
$Id$

This will start out as just a straight port of class Highlightable from cad/src/testdraw.py,
with the same limitations in API and implem (e.g. it won't work inside display lists).

Later we can revise it as needed.
"""


# == selobj interface

###e should define this; see class Highlightable --
# draw_in_abs_coords,
# ClickedOn/leftClick,
# mouseover_statusbar_message
# highlight_color_for_modkeys
# selobj_still_ok, maybe more

# == drag handler interface

class DragHandler:
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
    def ReleasedOn(self, selobj, mode): ### will need better args ### NOT YET CALLED  #e rename
        pass
    pass

# ==

def PushName(glname, drawenv = 'fake'):
    glPushName(glname)
    glpane = _kluge_glpane()
    glpane._glnames.append(glname)
            ###e actually we'll want to pass it to something in env, in case we're in a display list ####@@@@
    return

def PopName(glname, drawenv = 'fake'):
    glPopName() ##e should protect this from exceptions
            #e (or have a WE-wrapper to do that for us, for .draw() -- or just a helper func, draw_and_catch_exceptions)
    glpane = _kluge_glpane()
    popped = glpane._glnames.pop()
    assert glname == popped
    return

# ==

class Highlightable(DelegatingWidgetExpr, DragHandler):#060722
    "Highlightable(plain, highlight) renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight"
    # Works, except I suspect the docstring is inaccurate when it says "plain plus highlight" (rather than just highlight), 
    # and there's an exception if you try to ask selectMode for a cmenu for this object, or if you just click on it
    # (I can guess why -- it's a selobj-still-valid check I vaguely recall, selobj_still_ok):
    #   atom_debug: ignoring exception: exceptions.AttributeError: killed
    #   [modes.py:928] (i.e. selobj_still_ok) [Delegator.py:10] [inval.py:192] [inval.py:309]
    #
##    __init__ = WidgetExpr.__init__ # otherwise Delegator's comes first and init() never runs
    def init(self, args = None):
        "args are what it looks like when plain, highlighted, pressed_in, pressed_out (really this makes sense mostly for Button)"
        self.transient_state = self # kluge, memory leak
        self.transient_state.in_drag = False # necessary (hope this is soon enough)
        if args is None:
            args = self.args # kluge, unless we do away with self.args as being too specific to which superclass we're talking about
        def getargs(plain, highlighted = None, pressed_in = None, pressed_out = None):
            "fill in our default args"
            if not highlighted:
                highlighted = plain # useful for things that just want a glname to avoid mouseover stickiness
            # this next stuff is really meant for Button -- maybe we split into two kinds, Button and Draggable
            if not pressed_in:
                pressed_in = highlighted # might be better to make it plain (or highlighted) but with an outline, or so...
            if not pressed_out:
                pressed_out = plain # assuming we won't operate then
            return plain, highlighted, pressed_in, pressed_out
        args = getargs(*args)
        self.plain, self.highlighted, self.pressed_in, self.pressed_out = args
        # get glname, register self (or a new obj we make for that purpose #e), define necessary methods
        glname_handler = self # self may not be the best object to register here, though it works for now
        self.glname = env.alloc_my_glselect_name(glname_handler)
            #e if we might never be drawn, we could optim by only doing this on demand
    def draw(self):
        self.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
            ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
            #e [if this (or any WE) is really a map from external state to drawables,
            #   we'd need to store self.glname and self.saved_modelview_matrix in corresponding external state]
        #e do we need to save glnames? not in present system where only one can be active. ###@@@
        PushName(self.glname)
        if self.transient_state.in_drag:
            if printdraw: print "pressed_out.draw",self
            self.pressed_out.draw() #e actually might depend on mouseover, or might not draw anything then...
        else:
            ## print "plain.draw",self
            self.plain.draw()
        PopName(self.glname)
    def draw_in_abs_coords(self, glpane, color):
        # [this API comes from GLPane behavior
        # - why does it pass color? historical: so we can just call our own draw method, with that arg (misguided even so??)
        # - what about coords? it has no way to know old ones, so we have no choice but to know or record them...
        # ]
        # restore coords [note: it won't be so simple if we're inside a display list which is drawn in its own relative coords...]
        ##glMatrixMode(GL_MODELVIEW) #k prob not needed
        glPushMatrix()
        glLoadMatrixd(self.saved_modelview_matrix)
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
    def __repr__(self):
        sbar_text = self.kws.get('sbar_text') or ""
        if sbar_text:
            sbar_text = " %r" % sbar_text
        return "<%s%s at %#x>" % (self.__class__.__name__, sbar_text, id(self))
    def mouseover_statusbar_message(self): # called in GLPane.set_selobj
        return self.kws.get('sbar_text') or "%r" % (self,)
    def highlight_color_for_modkeys(self, modkeys):
        """#doc; modkeys is e.g. "Shift+Control", taken from glpane.modkeys
        """
        return green
            # The specific color we return doesn't matter, but it matters that it's not None, to GLPane --
            # otherwise it sets selobj to None and draws no highlight for it.
            # (This color will be received by draw_in_abs_coords, but our implem of that ignores it.)
    def selobj_still_ok(self, glpane):
        ###e needs to compare glpane.part to something in selobj, and worry whether selobj is killed, current, etc
        # (it might make sense to see if it's created by current code, too;
        #  but this might be too strict: self.__class__ is Highlightable )
        # actually it ought to be ok for now:
        res = self.__class__ is Highlightable # i.e. we didn't reload this module since self was created
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None.
    ### grabbed from Button, maybe not yet fixed for here
    def leftClick(self, point, mode):
        self.transient_state.in_drag = True
        self.inval(mode)
        self.do_action('on_press')
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
            self.do_action('on_release_in')
        else:
            self.do_action('on_release_out')
        ## mode.update_selobj(event) #k not sure if needed -- if it is, we'll need the 'event' arg
        #e need update?
        return
    
    def do_action(self, name):
        # print "do_action",name 
        action = self.kws.get(name)
        if action:
            action()
        return

    def inval(self, mode):
        """we might look different now;
        make sure display lists that might contain us are remade [stub],
        and glpanes are updated
        """
        vv.havelist = 0
        mode.o.gl_update()
        return
    
    pass # end of class Highlightable (a widgetexpr, and one kind of DragHandler)

Button = Highlightable

