"""
$Id$

This will start out as just a straight port of class Highlightable from cad/src/testdraw.py,
with the same limitations in API and implem (e.g. it won't work inside display lists).

Later we can revise it as needed.
"""

from basic import *
from basic import _self

from OpenGL.GL import *

from OpenGL.GLU import gluProject, gluUnProject

# modified from testdraw.printfunc:
def print_Expr(*args, **kws): ##e rename to include Action in the name?? #e refile
    "#doc"
    #e might be more useful if it could take argfuncs too (maybe as an option); or make a widget expr for that
    def printer(_guard = None, args = args):
        assert _guard is None # for now
        printfunc(*args, **kws) # defined in Exprs, has immediate effect, tho same name in testdraw is delayed like this print_Expr
    return canon_expr(printer)

# == selobj interface

###e should define a class for the selobj interface; see classes Highlightable and _UNKNOWN_SELOBJ_class for an example --
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
    def ReleasedOn(self, selobj, event, mode): ### will need better args #e rename
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

#e refile recycle_glselect_name in cad/src/env.py, next to alloc_my_glselect_name, or merge this with it somehow
# (and maybe change all that into a gl-displist-context-specific data structure, accessed via a glpane)

def recycle_glselect_name(glpane, glname, newobj): #e refile (see above)
    # 1. [nim] do something to make the old obj using this glname (if any) no longer valid,
    # or tell it the glname's being taken away from it (letting it decide what to do then, eg destroy itself), or so --
    # requires new API (could be optional) in objs that call alloc_my_glselect_name. ##e
    # 2. If the old obj is the glpane's selobj, change that to point to the new obj. [#e might need improvement, see comment]
    # 3. register the new object for this glname.
    import env
    oldobj = env.obj_with_glselect_name.get(glname, None) #e should be an attr of the glpane (or of one it shares displaylists with)
    if oldobj is not None and glpane.selobj is oldobj:
        glpane.selobj = None ###### normally newobj -- SEE IF THIS HELPs THE BUG 061120 956p
        printnim("glpane.selobj = None ###### normally newobj") # worse, i suspect logic bug in the idea of reusing the glname....
            ###k we might need to call some update routine instead, like glpane.set_selobj(newobj),
            # but I'm not sure its main side effect (env.history.statusbar_msg(msg)) is a good idea here,
            # so don't do it for now.
    env.obj_with_glselect_name[glname] = newobj
    return

def selobj_for_glname(glname):#e use above? nah, it also has to store into here
    import env
    return env.obj_with_glselect_name.get(glname, None)

# ==

printdraw = False # debug flag [same name as one in cad/src/testdraw.py]

class Highlightable(InstanceOrExpr, DelegatingMixin, DragHandler): #e rename to Button? make variant called Draggable?
    """Highlightable(plain, highlighted = None, pressed_in = None, pressed_out = None)
    renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight [#k or just highlight??]
    [and has more, so as to be Button #doc #e rename #e split out draggable of some sort]
    """
    # WARNING: the abstract methods in superclass DragHandler will be inherited (if not overridden),
    # even if they are defined in the delegate. [in theory; unconfirmed.] This is good in this case. [061127 comment]
    
    #060722;
    # revised for exprs module, 061115 [not done]
    # note: uses super InstanceOrExpr rather than Widget2D so as not to prevent delegation of lbox attrs (like in Overlay)
    
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
    on_drag = Option(Action)
    on_release_in = Option(Action)
    on_release_out = Option(Action)
    projection = Option(bool, False) # whether to save projection matrix too... would be default True except that breaks us. ###BUG
        # guess: it might mess up the glselect use of the projection matrix. (since ours maybe ought to be multiplied with it or so)

    def _init_instance(self):
        super(Highlightable, self)._init_instance()

        # == transient_state
        
        set_default_attrs( self.transient_state, in_drag = False) # sets only the attrs which are not yet defined
            ###e should make an abbrev for that attr as HL.in_drag -- maybe use State macro for it? read only is ok, maybe good.
            ###e should add an accessible tracked attr for detecting whether we're over self, too. What to call it?
            # [061212 comments, also paraphrased near testexpr_9fx4]
        
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

        if self.glpane_state.glname is None or 'TRY ALLOCATING A NEW NAME EACH TIME 061120 958p':
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
        
        set_default_attrs( self.per_frame_state,
                           saved_modelview_matrix = None,
                           saved_projection_matrix = None
                           ) #k safe? (why not?) #e can't work inside display lists
        
        return # from _init_instance
    
    def draw(self):
        if not self.env.glpane.current_glselect: # see if this cond fixes the projection=True bug (when not in DrawInCorner1 anyway)
            self.save_coords()
        else:
            if self.projection: # since this debug print is only needed when investigating the bug _9cx in using that option
                print "%r (projection=%r) not saving due to current_glselect" % (self, self.projection)####
            # these comments are about the implem of save_coords -- need review, which are obs and which should be moved? ###
            #
            ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
            #
            # addendum 061121: if this is usage tracked (which was never intended), then right here we invalidate whatever used it
            # (but nothing used it yet, the first time we draw), but in draw_in_abs_coords we use it, so if we ever redraw
            # after that (as we will - note, nothing yet clears/replaces this per_frame_state every frame),
            # then that invals the highlighted thing... i can imagine this creating extra invals, esp since the change
            # occurs during usage tracking of a computation (invalling it the first time), which then uses the same thing.
            # I don't quite see the exact cause, but I certainly see that it's not an intended use of this system.
            # (#e sometime I should think it through, understand what's legal and not legal, and add specific checks and warnings.)
            #  Meanwhile, since all per_frame state is not intended to be usage-tracked, just recorded for ordinary untracked
            # set and get, I'll just change it to have that property. And review glpane_state too.
            ###@@@ [this, and 061120 cmts/stringlits]
        PushName(self.glname)
        try:
            draw_this = "<not yet set>" # for debug prints
            if self.transient_state.in_drag:
                if printdraw: print "pressed_out.draw",self
                draw_this = self.pressed_out #e actually this might depend on mouseover, or we might not draw anything then...
                    # but this way, what we draw when mouse is over is a superset of what we draw in general,
                    # easing eventual use of highlightables inside display lists. See other drawing done later when we're highlighted
                    # (ie when mouse is over us)... [cmt revised 061115]
                # Note, 061115: we don't want to revise this to be the rule for self.delegate --
                # we want to always delegate things like lbox attrs to self.plain, so our look is consistent.
                # But it might be useful to define at least one co-varying attr (self.whatwedraw?), and draw it here. ####e
            else:
                ## print "plain.draw",self
                draw_this = self.plain
            draw_this.draw() # split out draw_this, 070104
        except:
            print_compact_traceback("exception during pressed_out or plain draw, ignored: ")#061120
            print "fyi: the object we wanted to draw when we got that exception was:",
            print "%r" % (draw_this,)
            pass # make sure we run the PopName
        PopName(self.glname)
        return

    def pre_draw_in_abs_coords(self, glpane): #bruce 061218 new feature of selobj interface,
        # used to stop highlightables from moving slightly when they highlight, esp when off-center in perspective view
        glDepthFunc(GL_LEQUAL)
        return
    
    def draw_in_abs_coords(self, glpane, color):
        "#doc; called from GLPane using an API it specifies; see also run_OpenGL_in_local_coords for more general related feature"
        # [this API comes from GLPane behavior:
        # - why does it pass color? historical: so we can just call our own draw method, with that arg (misguided even so??)
        # - what about coords? it has no way to know old ones, so we have no choice but to know or record them...
        # ]
        #
        # WARNING: This implem won't work when we can be inside a display list which is drawn in its own relative coords.
        # For latest info on what to do about that, see '061206 coordinate systems' on bruce's g5.

        # print "calling draw_in_abs_coords in",self # this does get called even when projection=True makes it seem to not work.
        # but mousing around over it does cause repeated draws, unlike when it works. Both as if it drew in wrong place.
        
        self.begin_using_saved_coords()
        try:
            if self.transient_state.in_drag:
                if printdraw: print "pressed_in.draw",self
                self.pressed_in.draw() #e actually might depend on mouseover, or might not draw anything then...
            else:
                if printdraw: print "highlighted.draw",self
                self.highlighted.draw()
        finally:
            #061206 added try/finally as a precaution.
            ##e Future: maybe we should not reraise (or pass on) an exception here??
            # GLPane's call is not well protected from an exception here, though it ought to be!
            self.end_using_saved_coords()
        return # from draw_in_abs_coords

    def post_draw_in_abs_coords(self, glpane): #bruce 061218 new feature of selobj interface
        glDepthFunc(GL_LESS) # the default state in OpenGL and in NE1
        return

    def run_OpenGL_in_local_coords(self, func): #061206
        """Run the OpenGL code in func in self's local coordinate system (and with its GL context current),
        and not while compiling any display list. If we run func immediately (always true in present implem),
        return (True, func-retval); otherwise return (False, not-yet-defined-info-about-how-or-why-we-delayed-func).
           Intended to be called from user mouse event handlers (not sure if ok for key or wheel events ##k).
        Maybe we'll also sometimes call it from later parts of a rendering loop, after the main drawing part;
        see below for caveats related to that.
           For now, this is defined to run func immediately (thus it's illegal to call this if you're
        presently compiling a display list -- but this error might not yet be detected, unless func does
        something explicitly illegal then).
           More subtlely, the current implem may only work when self was (1) in fact drawn (rather than being
        not drawn, due to being hidden, culled at a high level since obscured or outside the view frustum, etc)
        in the most recently drawn frame, (2) drawn outside of a display list, rather than as part of one we ran,
        when it was drawn then. That's because this implem works by caching a matrix containing
        the local coords as a side effect of self being drawn. [#e For info on fixing that, see code comments.]
           WARNINGS:
           - The current implem assumes no widget expr modifies the OpenGL projection matrix. This will change someday,
        and we'll probably need to save and restore both matrices. #e
        [as of 061208 we tried that, but it may have broken highlightable, not for sbar text but for color change...
         could it relate to glselect?? hmm... i'm adding a flag so i can test this.]
           - This does not reproduce all OpenGL state that was used to draw self, but only its local modelview matrix.
           - This does not ensure that any display lists that might be called by func (or by self.draw) are up to date!
           #e Later we might revise this API so it adds self, func to a dict and runs func later in the
        rendering loop. Then it might be legal to call this while compiling a display list (though it might
        not be directly useful; for a related feature see draw_later [nim?]). We might add args about whether
        delayed call is ok, properties of func relevant to when to delay it too, etc.
           See also draw_in_abs_coords, which is sort of like a special case of this, but not enough for it to
        work by calling this.
        """
        #e When this needs to work with display lists, see '061206 coordinate systems' on bruce's g5.
        #e We should probably move this to a mixin for all widget exprs that save their coordinates,
        # either as this current implem does, or by saving their position in a scenegraph/displaylist tree
        # and being able to do a fake redraw that gets back to the same coords.
        run_immediately = True
        if run_immediately:
            self.env.glpane.makeCurrent() # probably not needed
            self.begin_using_saved_coords()
            try:
                res = func()
            finally:
                self.end_using_saved_coords()
            pass
        else:
            assert 0, "nim"
            res = None
        return run_immediately, res # from run_OpenGL_in_local_coords

    def save_coords(self):
        # weirdly, this seems to cause bugs if done in the other order (if self.projection is False but not checked here)...
        # could it change the current matrix?? or be wrong when the wrong matrix is current???
        if self.projection:
            glMatrixMode(GL_PROJECTION) ###k guess 061210 at possible _9cx bugfix -- needed?? anyway, these guesses didn't fix the bug.
            self.per_frame_state.saved_projection_matrix = glGetDoublev( GL_PROJECTION_MATRIX ) # needed by draw_in_abs_coords
            glMatrixMode(GL_MODELVIEW)
        self.per_frame_state.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
        
    def begin_using_saved_coords(self):
        # fyi: examples of glLoadMatrix (and thus hopefully the glGet for that) can be found in these places on bruce's G4:
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/OpenGLContext/renderpass.py
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/VisionEgg/Core.py
        projection_matrix = self.per_frame_state.saved_projection_matrix
        modelview_matrix = self.per_frame_state.saved_modelview_matrix
            #k make sure we can access these (to get the most likely exceptions out of the way) (also shorten the remaining code)
        if self.projection:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            self.safe_glLoadMatrixd( projection_matrix, "projection_matrix")
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        self.safe_glLoadMatrixd( modelview_matrix, "modelview_matrix")
            # safe -> thus perhaps avoiding a crash bug [the one I had recently? 061214 Q]
        return

    def safe_glLoadMatrixd(self, matrix, name): # note: doesn't use self, ought to refile in draw_utils.py or a glpane proxy ###e
        "call glLoadMatrixd(matrix( if it looks like matrix has the right type; print a warning otherwise."
        # as of initial commit, 061214 359, the crash bug never recurred but neither did I see any prints from this,
        # so it remains untested as a bugfix, tho it's tested as a matrix-loader.
        if matrix is None:
            print "saved %s is None, not using it" % (name,) # thus perhaps avoiding a crash bug
                # I predict I'll see this where i would have otherwise crashed;
                ### print until i'm sure the bug is fixed
            return
        try:
            matrix.shape != (4,4)
        except:
            #e print exception type? more than one type is possible in theory
            print "not using wrong type of %s, which is %r" % (name, matrix)
            return
        if matrix.shape != (4,4):
            print "not using misshappen %s, which is %r" % (name, matrix)
            return
        glLoadMatrixd(matrix) # crashes Python if matrix has wrong type or shape, it seems [guess for now]
        return
        
    def end_using_saved_coords(self):
        if self.projection:
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def current_event_mousepoint(self, center = None, radius = None): #061206
        #e rename? #e add variant to get the drag-startpoint too #e cache the result #e is this the right class for it?
        """Return the 3d point (in self's local coordinates) corresponding to the mouse position
        of the current mouse event (error if no current mouse event which stores the necessary info for this);
        this is defined (for now) based on the depth buffer pixel clicked on,
        or is (by default) in the plane of the center-of-view if the depth is too large (meaning the mouse was over empty space).
           If center and radius are passed, they change the way a click over empty space is handled,
        to approximate what would happen if self was drawn as a screen-parallel circle (not a sphere)
        with the given center and radius (both in local coordinates). If only center is passed, it's the same as if
        center and a very large (infinite) radius is passed. The default behavior (when center is not passed)
        is equivalent to passing the "center of view" (in local coordinates) as center. [all this about center and radius is nim ##e]
           WARNING: this is so far implemented for click (press) but not drag or release; it remains to be seen
        exactly what it will do for drag when the depth under the mouse is varying during the drag. ##k
           WARNING: this only works on widgets which store, or can reconstruct, their local coordinate system
        used to draw them in the just-drawn frame. Only some kinds can (for now only Highlightable), and only if
        they were actually drawn in the just-drawn frame (if they weren't, we might give wrong results rather than
        detecting the error). See more caveat comments in the current implementing submethod (run_OpenGL_in_local_coords).
           Terminology note: point implies 3d; pos might mean 2d, especially in the context of a 2d mouse.
        So it's named mousepoint rather than mousepos.
        """
        glpane = self.env.glpane
        try:
            # during leftClick, this has been computed for us:
            info = glpane._leftClick_gl_event_info # this will fail if we're called during the wrong kind of user event
        except AttributeError:
            # during drag, it's often not needed, so compute it only if we need it -- which we do right now.
            # (WARNING: if we decide to cache it somewhere, don't do it in glpane._leftClick_gl_event_info or we'll cause bugs,
            #  since that would not get delattr'd at the end of the drag-event, so it might confuse something which saw it later
            #  (tho in practice that's unlikely since the next leftClick to a Highlightable would overwrite it).
            #  But I bet we won't need to cache it -- maybe this routine will be called by some standard attr's
            #  recompute method, so that attr will cache it.)
            #
            # Note: we could clean up/safen this system, and remove that warning above, if we just controlled a single dict or
            # attrholder in glpane, and cleared it each time; it could be full of per-user-event info of all kinds,
            # including some cached here -- or by its own recompute methods. We could have one for per-extended-drag info
            # and one for per-drawn-frame info. ###DOIT sometime
            mode = glpane._kluge_drag_mode
            event = glpane._kluge_drag_event
            gl_event_info = mode.dragstart_using_GL_DEPTH( event, more_info = True) # same as what mode did itself, for a leftClick
            #print "during drag got this info:",gl_event_info
            info = gl_event_info
        def func(center = center, radius = radius):
            # will the arg dflts fix this bug when I drag off the edge of the object?
            #   UnboundLocalError: local variable 'center' referenced before assignment
            farQ, abs_hitpoint, wX, wY, depth, farZ = info
            if not farQ:
                point = A(gluUnProject(wX, wY, depth))
            else:
                if center is None:
                    center = V(0,0,0) #e stub (not enough info) --
                        # we need the center of view in local coords (tho this substitute is not terrible!),
                        # e.g. turn abs_hitpoint into local coords (how?) or into x,y,depth... maybe selectMode will need
                        # to put more info into _leftClick_gl_event_info before we can do this. ###e
                ## point = center #e stub (since i'm lazy) --
                    # the rest of the work here is straightforward:
                    # just intersect the mouseray (gotten using mymousepoints or equiv) with the center/radius sphere
                    # (really with a screen-parallel plane through center) to decide what to do. In fact, the same code used
                    # in mymousepoints (in cad/src/testdraw.py) could probably do it -- except that code uses glpane.lineOfSight
                    # which might be in abs coords. (I'm not sure! Need to review that in GLPane.__getattr__. ###k)
                # Hmm, a simpler way might be to get center's depth using gluProject, then use that depth in gluUnProject
                # to get the mousepoint at the same depth, which is the intersection asked for above, then compare distance
                # to radius.
                xjunk, yjunk, center_depth = gluProject(center[0],center[1],center[2]) #k is there a "gluProjectv"?
                intersection = A(gluUnProject(wX, wY, center_depth))
                if radius is not None and radius < vlen(intersection - center):
                    # intersection is too far from center to count -- redo with cov instead of center
                    pass # that's nim for now ####e
                point = intersection
            # point is a Numeric array, and we needn't copy it for safety since it was constructed anew in each case above
            return point # from func
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( func)
        assert ran_already_flag # it ran immediately
        # semi-obs comment from when I had this method in Widget but had run_OpenGL_in_local_coords in Highlightable, causing a bug:
            # note: run_OpenGL_in_local_coords only works (or is only defined) for some kinds of widgets, presently Highlightable.
            # Since it's not defined on other widgets, it will also delegate from them to a Highlightable if they delegate to one,
            # but this is often accidental (adding a Translate wrapper would break it), so it's not good to rely on it unless you
            # doc that. WORSE, if a transforming widget delegates other attrs (like that method) to a Highlightable inside,
            # IT WILL MAKE THIS SILENTLY GIVE WRONG RESULTS (in the wrong coords). This should be fixed by preventing this
            # from delegating through transforms (or maybe though anything), but that makes some upcoming code harder,
            # needlessly for now, so it's postponed. ##e
            # [##k this delegation is also untested, but then, so is everything else about this, as of 061206 9pm.]
        ###BUG: that comment warns about problems that are NOT obs, namely, delegation through a transform (like Translate)
        # to this routine. Probably we should define it on IorE, and ensure that it only delegates when justified, #####e DOIT
        # i.e. not in transforms, which need their own class so they can define this method as an error
        # (unless they can delegate it and then fix the result, which might be ok and useful).
        #
        # The bug was, I defined this in Widget, used it in a thing I expected to delegate twice to reach Highlightable,
        # but none of that stuff inherited Widget so it went all the way thru that into Rect to run this, then didn't
        # find the submethod inside Highlightable since delegation (its defect) had skipped it! [digr: Note: if that defect of
        # delegation bothers us in specific cases, a workaround is to pass self as explicit last arg to methods
        # that might get delegated to, but that want to call submethods on the original object!! ###e]

        return funcres

    def __repr__THAT_CAUSES_INFRECUR(self):
        # this causes infrecur, apparently because self.sbar_text indirectly calls __repr__ (perhaps while reporting some bug??);
        # so I renamed it to disable it and rely on the super version.
        sbar_text = self.sbar_text or ""
        if sbar_text:
            sbar_text = " %r" % sbar_text
        return "<%s%s at %#x>" % (self.__class__.__name__, sbar_text, id(self)) ##e improve by merging in a super version ##e zap %#x
        ## [Highlightable.py:260] [ExprsMeta.py:250] [ExprsMeta.py:318] [ExprsMeta.py:366] [Exprs.py:184] [Highlightable.py:260] ...
    
    def mouseover_statusbar_message(self): # called in GLPane.set_selobj
        return str(self.sbar_text) or "%r" % (self,) #e note: that str() won't be needed once the type-coercion in Option works

    def highlight_color_for_modkeys(self, modkeys):
        """#doc; modkeys is e.g. "Shift+Control", taken from glpane.modkeys
        """
        return green
            # KLUGE: The specific color we return doesn't matter, but it matters that it's not None, to GLPane --
            # otherwise it sets selobj to None and draws no highlight for it.
            # (This color will be received by draw_in_abs_coords, but our implem of that ignores it.)
    
    ###@@@ got to here, roughly, in a complete review of porting this code from the old system into the exprs module
        
    def selobj_still_ok(self, glpane):
        ###e needs to compare glpane.part to something in selobj [i.e. self, i guess? 061120 Q],
        # and worry whether selobj is killed, current, etc
        # (it might make sense to see if it's created by current code, too;
        #  but this might be too strict: self.__class__ is Highlightable )
        # actually it ought to be ok for now:
        res = self.__class__ is Highlightable # i.e. we didn't reload this module since self was created
        if res:
            #061120 see if this helps -- do we still own this glname?
            our_selobj = self
            glname = self.glname
            owner = selobj_for_glname(glname)
            if owner is not our_selobj:
                res = False
                # owner might be None, in theory, but is probably a replacement of self at same ipath
                # do debug prints
                print "%r no longer owns glname %r, instead %r does" % (self, glname, owner) # [perhaps never seen as of 061121]
                our_ipath = self.ipath
                owner_ipath = getattr(owner, 'ipath', '<missing>')
                if our_ipath != owner_ipath:
                    # [perhaps never seen as of 061121]
                    print "WARNING: ipath for that glname also changed, from %r to %r" % (our_ipath, owner_ipath)
                pass
            pass
            # MORE IS PROBABLY NEEDED HERE: that check above is about whether this selobj got replaced locally;
            # the comments in the calling code are about whether it's no longer being drawn in the current frame;
            # I think both issues are valid and need addressing in this code or it'll probably cause bugs. [061120 comment] ###BUG
        import env
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None.
    
    ### grabbed from Button, maybe not yet fixed for here
    def leftClick(self, point, event, mode):
##        if 1:
##            print_compact_stack("fyi: on_press called: ")#061218 debug hl sync bug
        # print "mode._drag_handler_gl_event_info = %r" % (mode._drag_handler_gl_event_info,)
            # farQ, hitpoint, wX, wY, depth, farZ -- for use in gluUnProject in local coords (see also run_OpenGL_in_local_coords)
            # note: point == hitpoint.
        # point is in global coords, not ours; sometimes useful, but save enough info to compute the local version too.
        # But don't precompute it -- let the action ask for it if desired. That optim doesn't matter for this leftClick method,
        # but it might matter for the drag methods which use the same API to pass optional info to their actions.
        self.transient_state.in_drag = True
        self.inval(mode) #k needed?
        glpane_bindings = dict( _leftClick_global_point = point, _leftClick_gl_event_info = mode._drag_handler_gl_event_info )
            # WARNING: the keys in that dict will be set as attrs in the main GLPane object.
        self._do_action('on_press', glpane_bindings = glpane_bindings )
        mode.update_selobj(event) #061120 to see if it fixes bugs (see discussion in comments)
        self.inval(mode) #k needed? (done in two places per method, guess is neither is needed)
        return self # in role of drag_handler
    
    def DraggedOn(self, event, mode):
        # only ok for Button so far
        #e might need better args (the mouseray, as two points?) - or get by callback
        # print "draggedon called, need to update_selobj, current selobj %r" % mode.o.selobj
            # retested this 061204 in testexpr_10c; it gets called, but only during drag (motion when mouse is down);
            # the update_selobj is safe, won't trigger redraw unless selobj has changed. will when it does (off or on the object);
            # didn't test highlight behavior (tho it works in other tests), since _10c doesn't use it.
        glpane_bindings = dict( _kluge_drag_event = event, _kluge_drag_mode = mode ) #061207
        self._do_action('on_drag', motion = True, glpane_bindings = glpane_bindings)
        mode.update_selobj(event)
        #e someday, optim by passing a flag, which says "don't do glselect or change stencil buffer if we go off of it",
        # valid if no other objects are highlightable during this drag (typical for buttons). Can't do that yet,
        # since current GLPane code has to fully redraw just to clear the highlight, and it clears stencil buffer then too.

        # for dnd-like moving draggables, we'll have to modify the highlighting alg so the right kinds of things highlight
        # during a drag (different than what highlights during baremotion). Or we might decide that this routine has to
        # call back to the env, to do highlighting of the kind it wants [do, or provide code to do as needed??],
        # since only this object knows what kind that is.
        return
    
    def ReleasedOn(self, selobj, event, mode): ### may need better args
        ### written as if for Button, might not make sense for draggables
        self.transient_state.in_drag = False
        self.inval(mode) #k needed? (done in two places per method, guess is neither is needed)
        our_selobj = self #e someday this might be some other object created by self to act as the selobj
        try:
            # KLUGE 061116, handle case of us being replaced (instances remade)
            # between the mode or glpane seeing the selobj and us testing whether it's us
            if selobj and (selobj is not our_selobj) and getattr(selobj,'ipath','nope') == our_selobj.ipath:
                assert our_selobj.glname == selobj.glname, "glnames differ" # should be the same, since stored in glpane state at ipath
                print "kluge, fyi: pretending old selobj %r is our_selobj (self) %r" % (selobj, our_selobj)
                    # NOTE: our_selobj (self) is OLDER than the "old selobj" (selobj) passed to us!
                    # Evidence: the sernos in this print:
                    ## kluge, fyi: pretending old selobj <Highlightable#2571(i) at 0x10982b30>
                    ##  is our_selobj (self) <Highlightable#2462(i) at 0x1092bad0>
                    # I guess that's because the one first seen by mouseover was saved as selobj in glpane;
                    # then it was replaced by one that drew highlighting;
                    # then by the time this runs it was replaced again;
                    # but WE ARE NOT THE LATEST ONE AT THAT IPATH,
                    # but rather, the first saved one!
                    # THIS COULD CAUSE BUGS if we are replaced on purpose with one which does different things!
                    # But that's not supposed to happen, so rather than finding the latest one and having it do the work
                    # (which is possible in theory -- look it up by glname),
                    # I'll just ignore this issue, leave in the debug print, and expect the print
                    # (and even the need for this kluge check code) to go away as soon as I optim
                    # by not remaking instances on every redraw. [061116]
                selobj = our_selobj
            pass
        except:
            print_compact_traceback( "bug: exception in ReleasedOn ignored: ")
            pass
        if selobj is our_selobj: 
            self._do_action('on_release_in')
        else:
            self._do_action('on_release_out')
        ## mode.update_selobj(event) #k not sure if needed -- if it is, we'll need the 'event' arg
        ## printnim("does ReleasedOn and also leftClick need the event arg so it can update_selobj so some bugs can be fixed??") ######
            ##bug guess 061120 - i think it does. try it. any other files affected?? if maybe for leftClick, rename it PressedOn??
            ###BUG? don't know if it matters as of 061121; was doing it since before bugs finally got fixed.
            # Maybe selectMode did it before calling us, btw. #k
        #e need update?
        mode.update_selobj(event) #061120 to see if it fixes bugs (see discussion in comments)
        self.inval(mode) #k needed? (done in two places per method, guess is neither is needed)
        return
    
    def _do_action(self, name, motion = False, glpane_bindings = {}):
        "[private, should only be called with one of our action-option names]"
##        if not motion:
##            print "_do_action",name
        assert name.startswith('on_')
        action = getattr(self, name) # will always be defined, since Option will give it a default value if necessary
            ###BUG 061205: seems to not be defined in a certain bug where I supplied it a formula whose computing has an error!
            # and as a result it gets delegated. Guess: the exception makes it seem missing to the delegation code --
            # because the exception also happens to be an AttributeError! (It does, in that bug: formula was _self.on_drag_bg
            # and that attr was not defined in that object.)
            #
            # ... Unfortunately I can't think of a trivial fix to prevent delegation...
            # I guess I could manually grab the class property and call its __get__ protocol... not too hard, try it sometime. ##e
            # Ah, found one: for an error in the recompute like that, turn it into my own exception (in lvals.py)
            # so it can't imitate another one -- at least not an AttributeError which causes delegation!
            # Ok, that's coded (for AttributeError only) and does prevent that error from causing delegation, makes it easier
            # to debug. Good. Not much need to try the other fix above.

            ###e should be None or a callable supplied to the expr, for now; later will be None or an Action
        if action:
            if glpane_bindings: # new feature 061205 - dynamic bindings of specific attrnames in glpane
                glpane = self.env.glpane
                for k,v in glpane_bindings.iteritems(): # these k should only be hardcoded in this class, not caller-supplied
                    assert not hasattr(glpane, k) #e might revise to let it be a default value in the class, or more
                    setattr(glpane, k, v)
                        #e or could call glpane.somedict.update(glpane_bindings) -- maybe more controlled if it keeps them in a dict
            try:
                action()
            finally:
                if glpane_bindings:
                    for k in glpane_bindings.iterkeys():
                        delattr(glpane, k)
        return

    def inval(self, mode):
        """we might look different now;
        make sure display lists that might contain us are remade [stub],
        and glpanes are updated
        """
        ### 061120 guess: prob not needed in theory, and de-optim, but conservative, and otherwise harmless.
        # the fact that it comes before the side effect routines in its callers
        # ought to be ok unless they do recursive event processing. still, why not do it after instead? not sure... ##e
        # plan: try doing it after as last resort bugfix; otoh if bugs gone, try never doing it.
        
        ## vv.havelist = 0
        mode.o.gl_update()
        return
    
    pass # end of class Highlightable

Button = Highlightable

class _UNKNOWN_SELOBJ_class: #061218 
    "[private helper, for a kluge]"
    def handles_updates(self): #k guessing this one might be needed
        return True
    # these methods were found by experiment to be needed
    def selobj_still_ok(self, glpane):
        return (self is getattr(glpane.mode, 'UNKNOWN_SELOBJ')) # goal: True in the mode that defines us, False otherwise
    highlight_color_for_modkeys = noop #e will it need to be a method which returns a color? I doubt it.
    leftClick = noop
    # this is in case we didn't find one that's needed:
    def __getattr__(self, attr):
        if attr.startswith("__"):
            raise AttributeError, attr
        if platform.atom_debug:###
            print "_UNKNOWN_SELOBJ_class returns noop for attr %r" % attr
        setattr(self, attr, noop) # optim
        return noop # fake bound method
    pass
# draw_in_abs_coords,
# ClickedOn/leftClick,
# mouseover_statusbar_message
# highlight_color_for_modkeys
# selobj_still_ok, maybe more

def _setup_UNKNOWN_SELOBJ(mode): #061218
    "[private helper, for a kluge -- see comment where called]"
    if not hasattr(mode, 'UNKNOWN_SELOBJ'):
        mode.UNKNOWN_SELOBJ = _UNKNOWN_SELOBJ_class()
    return

# == NO CURRENT CODE IS BELOW HERE (I think)


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

# see also:
## ToggleShow-outtakes.py: 48:         on_press = ToggleAction(stateref)

# end
