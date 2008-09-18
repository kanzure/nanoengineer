# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Highlightable.py - general-purpose expr for mouse-responsive drawable objects

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

This will start out as just a straight port of class Highlightable from cad/src/testdraw.py,
with the same limitations in API and implem (e.g. it won't work inside display lists).

Later we can revise it as needed.

==

Notable bug (really in check_target_depth in GLPane, not this file): highlighted-object-finder
can be fooled by nearby depths due to check_target_depth_fudge_factor of 0.0001. This caused
a bug in demo_drag.py which is so far only worked around, not really fixed. [070115 comment]

Another bug involves Highlightable's use inside display lists, and is described elsewhere,
probably in the BUGS file.

And on 071102 I noticed another bug, probably related: the checkboxes in the
lower right "control corner" don't highlight or operate after the main window
(and thus glpane) is resized, until we next reload testdraw. But the "action buttons"
next to them continue to work then. I don't know why they'd behave differently.
"""

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import GL_PROJECTION_MATRIX
from OpenGL.GL import glGetDoublev
from OpenGL.GL import GL_MODELVIEW_MATRIX
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPushMatrix
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glLoadMatrixd
from OpenGL.GL import glPopMatrix

from OpenGL.GLU import gluProject, gluUnProject

from utilities import debug_flags

from geometry.VQT import A
from geometry.VQT import vlen
from geometry.VQT import V
from utilities.constants import noop
from utilities.constants import green
from utilities.debug import print_compact_traceback

from exprs.Exprs import or_Expr, canon_expr
from exprs.Exprs import printfunc
from exprs.Exprs import is_expr_Instance_or_None
from exprs.StatePlace import set_default_attrs
from exprs.attr_decl_macros import Option, ArgOrOption, Arg
from exprs.instance_helpers import InstanceOrExpr, DelegatingMixin, ModelObject, DelegatingInstanceOrExpr
from exprs.ExprsConstants import ORIGIN
from exprs.widget2d import Widget2D
from exprs.Set import Action
from exprs.py_utils import printnim
from exprs.__Symbols__ import _self, Anything

from graphics.drawables.DragHandler import DragHandler_API
    #bruce 070602 moved this from exprs/Highlightable.py to DragHandler.py, and renamed it

from graphics.drawables.Selobj import Selobj_API # for the "selobj interface" (subject to renaming)

# ==

# modified from testdraw.printfunc:
def print_Expr(*args, **kws): ##e rename to include Action in the name?? #e refile
    "#doc"
    #e might be more useful if it could take argfuncs too (maybe as an option); or make a widget expr for that
    def printer(_guard = None, args = args):
        assert _guard is None # for now
        printfunc(*args, **kws) # defined in Exprs, has immediate effect, tho same name in testdraw is delayed like this print_Expr
    return canon_expr(printer)

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

# maybe todo: refile recycle_glselect_name next to alloc_my_glselect_name (assy method), or merge this with it somehow
# (and maybe change all that into a gl-displist-context-specific data structure, accessed via a glpane)

def recycle_glselect_name(glpane, glname, newobj): #e refile (see above)
    # 1. [nim] do something to make the old obj using this glname (if any) no longer valid,
    # or tell it the glname's being taken away from it (letting it decide what to do then, eg destroy itself), or so --
    # requires new API (could be optional) in objs that call alloc_my_glselect_name. ##e
    # 2. If the old obj is the glpane's selobj, change that to point to the new obj. [#e might need improvement, see comment]
    # 3. register the new object for this glname.
    oldobj = glpane.object_for_glselect_name(glname, None)
    if oldobj is not None and glpane.selobj is oldobj:
        glpane.selobj = None ###### normally newobj -- SEE IF THIS HELPs THE BUG 061120 956p
        printnim("glpane.selobj = None ###### normally newobj") # worse, i suspect logic bug in the idea of reusing the glname....
            ###k we might need to call some update routine instead, like glpane.set_selobj(newobj),
            # but I'm not sure its main side effect (env.history.statusbar_msg(msg)) is a good idea here,
            # so don't do it for now.
    ## env.obj_with_glselect_name[glname] = newobj
    glpane.assy._glselect_name_dict.obj_with_glselect_name[glname] #bruce 080917 revised; ### TODO: fix private access, by
        # moving this method into class GLPane and/or class Assembly & class glselect_name_dict
    return

##def selobj_for_glname(glname):#e use above? nah, it also has to store into here
##    import foundation.env as env
##    return env.obj_with_glselect_name.get(glname, None)

# ==

def copy_pyopengl_matrix( matrix): #bruce 070704
    try:
        # this works when it's a Numeric array (as it is in some Mac PyOpenGLs)
        return + matrix  #k let's hope this is a deep copy!
    except TypeError:
        # this happens when it's a 'c_double_Array_4_Array_4' object (some sort of ctypes array, I assume)
        # which is what Mac Gold PyOpenGL returns for matrices. My initial web research reveals clues
        # about copying this into a Numeric array, but not yet a good method, nor a way to copy it into
        # another object of the same type, which is what's needed here.
##        print "following exception was in copy_pyopengl_matrix( %r):" % (matrix,)
##        raise
        #
        # Hmm, something on the web says "Since the ctype does support slicing", so I'll try that:
        return matrix[:] # works! (### REVIEW: Would it work for a Numeric array too? If so, should just use it always.)
    pass

# ==

debug_saved_coords = False #070317

class _CoordsysHolder(InstanceOrExpr): # split out of class Highlightable, 070317
    """
    Abstract superclass [private] for Instances which can capture the current OpenGL drawing coordinates,
    restore them later, and do OpenGL state queries within them.
       Superclass of Highlightable [though maybe it could just own one of us in an attr, instead?? ##e];
    and of SavedCoordsys, for holding a saved static coordsys.
       WARNING: implem and API may change once we introduce "draw decorators" to fix Highlightable/DisplayListChunk bugs.
    """
    projection = Option(bool, False) # whether to save projection matrix too... would be default True except inefficient

    def _init_instance(self):
        super(_CoordsysHolder, self)._init_instance()
        # == per_frame_state
        set_default_attrs( self.per_frame_state,
                           saved_modelview_matrix = None,
                           saved_projection_matrix = None
                           ) #k safe? (why not?) #e can't work inside display lists
        return # from _init_instance

    def run_OpenGL_in_local_coords(self, func): #061206
        """
        Run the OpenGL code in func in self's local coordinate system (and with its GL context current),
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
            self.env.glpane.makeCurrent() # as of 070305 we might run this outside of paintGL, so this might be needed
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

    def save_coords(self): #e make private? most calls go thru save_coords_if_safe -- not quite all do.
        # weirdly, this seems to cause bugs if done in the other order (if self.projection is False but not checked here)...
        # could it change the current matrix?? or be wrong when the wrong matrix is current???
        if self.projection:
            glMatrixMode(GL_PROJECTION) #k needed?
            self.per_frame_state.saved_projection_matrix = glGetDoublev( GL_PROJECTION_MATRIX ) # needed by draw_in_abs_coords
            glMatrixMode(GL_MODELVIEW)
        if debug_saved_coords:
            old = self.per_frame_state.saved_modelview_matrix
            if old is not None:
                old = + old
        self.per_frame_state.saved_modelview_matrix = new = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
        if debug_saved_coords and old != new:
            print "debug_saved_coords: %r changes saved coords" % self
        # these comments are about the implem of save_coords -- need review, which are obs and which should be moved? ###
        #
        ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
        #
        # addendum 061121: if saved coords are usage tracked (which was never intended), then right here we invalidate whatever used it
        # (but nothing used it yet, the first time we draw), but in draw_in_abs_coords we use it, so if we ever redraw
        # after that (as we will - note, nothing yet clears/replaces this per_frame_state every frame),
        # then that invals the highlighted thing... i can imagine this creating extra invals, esp since the change
        # occurs during usage tracking of a computation (invalling it the first time), which then uses the same thing.
        # I don't quite see the exact cause, but I certainly see that it's not an intended use of this system.
        # (#e sometime I should think it through, understand what's legal and not legal, and add specific checks and warnings.)
        #  Meanwhile, since all per_frame state is not intended to be usage-tracked, just recorded for ordinary untracked
        # set and get, I'll just change it to have that property. And review glpane_state too.
        ###@@@ [this, and 061120 cmts/stringlits]
        return

    def save_coords_if_safe(self): #070401 [#e rename?]
        """
        call self.save_coords if the glpane drawing phase indicates
        the results should be valid for highlighting
        """
        if not self.env.glpane.current_glselect:
            self.save_coords()
            # Historical note: using this cond apparently fixes the projection = True bug (even when used in DrawInCorner_projection),
            # based on tests and debug prints of 070405. The cond itself was added long before. See testexpr_9cx / testexpr_9cy.
            # It's not really known if that's all that fixed it; on 070118 I said:
            #   I don't know why/how/ifreally it got fixed, but maybe it did,
            #   since I did a few things to highlighting code since that time,
            #   including not using that z-offset kluge in the depth test,
            #   changing to GL_LEQUAL (with different Overlay order), maybe more.
            #
            # For details of debug prints, see cvs rev 1.66. They show that glpane.drawing_phase is 'main' here
            # and 'glselect' when this cond is false, at least when self.projection is true and when using those testexprs.
        return
        
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
        """
        call glLoadMatrixd(matrix( if it looks like matrix has
        the right type; print a warning otherwise.
        """
        # as of initial commit, 061214 359, the crash bug never recurred but neither did I see any prints from this,
        # so it remains untested as a bugfix, tho it's tested as a matrix-loader.
        if matrix is None:
            print "in %r, saved %s is None, not using it" % (self, name,) # thus perhaps avoiding a crash bug
                # I predict I'll see this where i would have otherwise crashed;
                ### print until i'm sure the bug is fixed
                # text searches for this print statement might find it more easily if we add this text to the comment:
                # "saved modelview_matrix is None, not using it" [bait for a text search -- the real print statement has %s in it]
            return
        # I would like a matrix typecheck here, but the type depends on the PyOpenGL implementation
        # (for more info see the comments in the new function copy_pyopengl_matrix),
        # so I don't know how to do it correctly in all cases. The following code is what worked
        # in an older PyOpenGL, but the AttributeError inside it shows what happened in a newer one,
        # i.e. in the Mac "Gold" PyOpenGL for A9.1. [bruce 070703]
        ##try:
        ##    matrix.shape != (4,4)
        ##except:
        ##    print_compact_traceback("bug in matrix.shape check: ")
        ##        ## AttributeError: 'c_double_Array_4_Array_4' object has no attribute 'shape'
        ##    print "not using wrong type of %s, which is %r" % (name, matrix)
        ##    return
        ##if matrix.shape != (4,4):
        ##    print "not using misshappen %s, which is %r" % (name, matrix)
        ##    return
        glLoadMatrixd(matrix) # crashes Python if matrix has wrong type or shape, it seems [guess for now]
        return
        
    def end_using_saved_coords(self):
        if self.projection:
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def current_event_mousepoint(self, center = None, radius = None, plane = None, depth = None, _wXY = None):
        #061206; 070203 added 'plane' and revised docstring; 070226 added _wXY; 070314 added depth
        #e rename? #e add variant to get the drag-startpoint too #e cache the result
        #e is this the right class for it? self is only used for glpane and local coords,
        # but "run_OpenGL_in_local_coords" is only implementable in this class for the moment.
        """
        Return the 3d point (in self's local coordinates) corresponding to the mouse position
        of the current mouse event (error if no current mouse event which stores the necessary info for this),
        interpreting its depth based on the arguments/options.
           If no options are passed, then the event's depth is defined (for now) by the depth buffer pixel clicked on,
        unless the click was in empty space, in which case the plane of the center of view [partly nim] is used.
        (This is partly nim as of 070203 since the actual cov is not used; local V(0,0,0) is used to approximate it.)
           If center is passed, it is used in place of the center of view to determine depth of empty-space clicks.
        (The behavior when center is not passed is equivalent to passing the "center of view" (in local coordinates) as center.)
           If radius [nim] and center are passed, then clicks in empty space only use center if they are close enough to it
        (within distance radius in center's plane) -- this imitates mouse hits on a screen-parallel circular disk
        defined by center and radius. If the disk is missed, the center of view is used as before.
           If plane is passed, all the above data is ignored (depth buffer, center of view, center, radius).
        If plane is a plane [nim], the hit is assumed to lie within it; if a point, the hit lies within the screen-parallel
        plane containing that point. Alternatively, an OpenGL depth value can be passed, and the hit lies at that depth.
           Private option for use by other methods: _wXY overrides the window coords of the mouse event,
        so you can get things like the corners/edges/center of a screen rectangle projected (ortho or perspective as approp)
        to the same depth as a point (passed in plane), assuming you know about glpane.width and .height.
           WARNING [partly obs]: this is so far implemented for click (press) but not drag or release; it remains to be seen
        exactly what it will do for drag when the depth under the mouse is varying during the drag. ##k
        [later: it is used for drag successfully in demo_drag.py, but in a way which can be confused by seeing
         depth of dragobj vs depth of background objs.]
           WARNING: this only works on widgets which store, or can reconstruct, their local coordinate system
        used to draw them in the just-drawn frame. Only some kinds can (for now only Highlightable), and only if
        they were actually drawn in the just-drawn frame (if they weren't, we might give wrong results rather than
        detecting the error). See more caveat comments in the current implementing submethod (run_OpenGL_in_local_coords).
           Terminology note: point implies 3d; pos might mean 2d, especially in the context of a 2d mouse.
        So it's named mousepoint rather than mousepos.
           Delegation usage note: this can be called on self, if self delegates to a Highlightable (perhaps indirectly)
        and uses the same local coordinate system as that Highlightable.
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
        def func(center = center, radius = radius, plane = plane, depth0 = depth, _wXY =_wXY):
            "[local helper func, to be passed to self.run_OpenGL_in_local_coords]"
            # will the arg dflts fix this bug when I drag off the edge of the object?
            #   UnboundLocalError: local variable 'center' referenced before assignment
            farQ, abs_hitpoint, wX, wY, depth, farZ = info
            if _wXY is not None:
                ### this case is UNTESTED, NOT YET USED
                wX, wY = _wXY
            if depth0 is not None:
                depth = depth0
                farQ = False
            elif plane is not None:
                center = plane # assume it's a point --
                    # passing an actual plane is nim (btw, we don't even have a standard way of passing one)
                radius = None
                farQ = True
                # now we can use the remaining code
                #e [code cleanup needed: call a routine split from the following instead,
                # in case more options we'd have to turn off here are added later into the following code.]
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
                    # in mymousepoints could probably do it -- except that code uses glpane.lineOfSight
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

        return funcres # from current_event_mousepoint

    def gluProject(self, point): #070226; probably to be moved to more kinds of objects but implemented differently, eventually
        """
        Return the same (wX, wY, depth) that gluProject would or should return
        if run in local model coords (and gl state for drawing) of this object,
        on point (which should be an x,y,z-tuple or Numeric array in the same coords).
           This may or may not actually run gluProject depending on the implementation
        [as of 070226 it always does, and has ###BUGS inside display lists after trackballing].
           WARNING: Proper behavior inside a display list is not yet defined; maybe it will have to assume
        something about the list's initial coords... or the caller will have to pass those...
        or self will have to know how to ask a parent DisplayListChunk for those. ##e
        """
        ###UNTESTED, NOT YET USED
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( lambda p = point: gluProject(p[0],p[1],p[2]) )
        assert ran_already_flag # it ran immediately
        wX, wY, depth = funcres
        return wX, wY, depth

    def gluUnProject(self, wX, wY, depth): #070226
        """
        Act like gluUnProject... for more info (and bugs) see docstring for gluProject.
        """
        ###UNTESTED, NOT YET USED
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( lambda: gluUnProject(wX, wY, depth) )
        assert ran_already_flag
        x,y,z = funcres
        return V(x,y,z)
    
    def screenrect(self, point = ORIGIN):#070226 ##e rename? btw what interface are this and current_event_mousepoint part of?
        """
        Return the 4 corners (in local model coords) of a screen rectangle, projected to the same depth as point
        (which is also in local model coords; if left out it's their origin).
        """
        #e should add option to directly pass depth
        # we don't call self.gluProject etc since we don't want to internally call self.run_OpenGL_in_local_coords 5 times!
        def func():
            p = point
            xjunk, yjunk, depth = gluProject(p[0],p[1],p[2]) # get depth of point
            glpane = self.env.glpane
            w = glpane.width
            h = glpane.height
            #e should we add one (or half) to those?? ie is true x range more like 0,w or -0.5, w + 0.5 or 0, w+1??
            # (x,y) might be (in ccw order around the screenrect, starting from botleft to botright):
            res = map( lambda (wX, wY): A(gluUnProject(wX, wY, depth)),
                       ((0,0), (w,0), (w,h), (0,h)) )
            return res # from func
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( func )
        assert ran_already_flag
        return funcres

    def copy_saved_coordsys_from(self, other): #070328 moved here from subclass SavedCoordsys, and renamed from copy_from
        if 'kluge 070328':
            other0 = other # for error messages only
            while not isinstance(other, _CoordsysHolder):
                try:
                    other1 = other._delegate # might fail, but if it does, this method was doomed to fail anyway (in current implem)
                    assert other1 is not None
                    other = other1
                except:
                    print_compact_traceback("bug in %r.copy_saved_coordsys_from(%r): no _delegate in %r: " % (self, other0, other))
                        #e may need better error message if it fails
                    return
        projection_matrix = other.per_frame_state.saved_projection_matrix
        modelview_matrix = other.per_frame_state.saved_modelview_matrix
        if projection_matrix is not None:
            projection_matrix = copy_pyopengl_matrix( projection_matrix)
        if modelview_matrix is not None:
            modelview_matrix = copy_pyopengl_matrix( modelview_matrix)
        self.per_frame_state.saved_projection_matrix = projection_matrix
        self.per_frame_state.saved_modelview_matrix = modelview_matrix

    pass # end of class _CoordsysHolder

class SavedCoordsys(_CoordsysHolder): #070317
    """
    One of these can be told to save a static copy of the coordsys from any instance of a _CoordsysHolder subclass,
    or to save one from the current GL state, and then to make use of it in some of the same ways Highlightable can do. #doc better
    """
    def copy_from(self, other): #070328 moved the method body to superclass & renamed it there.
            #e Its fate here (both method & class existence) is undecided.
            # guess: a better structure is for a saved coordsys to be a *member* of class _CoordsysHolder, not a subclass.
        self.copy_saved_coordsys_from(other)
    pass

# ==

printdraw = False # debug flag [same name as one in cad/src/testdraw.py]

class Highlightable(_CoordsysHolder, DelegatingMixin, DragHandler_API, Selobj_API):
    #070317 split out superclass _CoordsysHolder
    #e rename to Button? make variant called Draggable?
    """
    Highlightable(plain, highlighted = None, pressed_in = None, pressed_out = None)
    [###WRONG, those are not named options -- fix docstring, or change them to options??]
    renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight [#k or just highlight??]
    [and has more, so as to be Button #doc #e rename #e split out draggable of some sort]
    """
    # WARNING: the abstract methods in superclass DragHandler_API will be inherited (if not overridden),
    # even if they are defined in the delegate. [in theory; unconfirmed.] This is good in this case. [061127 comment]
    
    #060722;
    # revised for exprs module, 061115 [not done]
    # note: uses super InstanceOrExpr rather than Widget2D so as not to prevent delegation of lbox attrs (like in Overlay)
    
    # args (which specify what it looks like in various states)
    plain = ArgOrOption(Widget2D) # Arg -> ArgOrOption 070304 -- but is it still required? it ought to be... but it's not.... ###e
    delegate = _self.plain # always use this one for lbox attrs, etc
        # Note that subclasses of Highlightable generally need to override plain, not delegate,
        # and also have to remember to override it with an Instance, not just an expr.
        # This is basically a flaw in using subclassing (or in our subclass interface, but it's not easily fixable here)
        # vs. delegation to normally-made Highlightables. [070326 comment]
    highlighted = ArgOrOption(Widget2D, plain)
        # fyi: leaving this out is useful for things that just want a glname to avoid mouseover stickiness
        # implem note: this kind of _self-referential dflt formula is not tested, but ought to work;
        # btw it might not need _self, not sure, but likely it does --
        # that might depend on details of how Arg macro uses it ###k
    # these next args are really meant for Button -- maybe we split this into two variants, Button and Draggable
    pressed_in = ArgOrOption(Widget2D, or_Expr(_self.pressed, highlighted))
        #e might be better to make it plain (or highlighted) but with an outline, or so...)
    pressed_out = ArgOrOption(Widget2D, or_Expr(_self.pressed, plain))
        # ... good default for a Button, assuming we won't operate then -- but bad default for a draggable --
        # but not only this, but everything about how to detect a "selobj" under mouse, should be changed for that [070213 comment]

    # options
    pressed = Option(Widget2D, None, doc = "if provided, pressed is the default for both pressed_in and pressed_out")#070224
    sbar_text = Option(str, "") # mouseover text for statusbar
    #e on_enter, on_leave -- see comment below
    behavior = Option(Anything,
                      doc = "an Instance whose on_press/on_drag/on_release* methods we use, unless overridden by specific options")#070316
    on_press = Option(Action)
    on_drag = Option(Action)
    on_release = Option(Action,
                           doc = "mouse-up action; can be overridden by on_release_in and/or on_release_out"
                         ) # 070209 added this general release action, for when in or out doesn't matter
    on_release_in = Option(Action, on_release,
                           doc = "mouse-up action for use if mouse is over highlighted object when it's released")
    on_release_out = Option(Action, on_release,
                           doc = "mouse-up action for use if mouse is NOT over highlighted object when it's released")
    ###e should we add on_click, to be run at the same time as on_release but only if on_drag was never called? [070324 idea]
    on_doubleclick = Option(Action, # 070324 new feature
                            doc = "mouse-down action for the 2nd click in a double click; on_release won't run for it")
        ###BUG (likely): on_release won't run, nor on_press, but on_drag probably will, if you drag before releasing that click!
        # (Unless Qt suppresses drag events in that situation -- unknown.###TEST)
        # But my guess is, most on_drag methods will fail in that case! ####FIX, here or in testmode or in selectMode
    cmenu_maker = Option(ModelObject) # object which should make a context menu, by our calling obj.make_selobj_cmenu_items if it exists
    # note: inherits projection Option from superclass _CoordsysHolder [###UNTESTED]
##    projection = Option(bool, False) # whether to save projection matrix too... would be default True except that breaks us. ###BUG
##        # guess: it might mess up the glselect use of the projection matrix. (since ours maybe ought to be multiplied with it or so)

    def _init_instance(self):
        super(Highlightable, self)._init_instance()

        # == transient_state
        
        set_default_attrs( self.transient_state, in_drag = False) # doc = "whether mouse is currently down (after a mousedown on self)"
            # Q 070210: would in_drag = State(...) be equivalent?
            # Guess: yes (but with more general access syntax) -- this is just an old form; not sure! ##k

            # note 070210: sometimes I've mistakenly thought that meant in_bareMotion [not a serious name-suggestion],
            # i.e. whether mouse is over self or not. We might need that, and/or action options to run when it changes,
            # perhaps called on_enter and on_leave. Right now I don't think we get notified about those events! ###e
            
            # note: set_default_attrs sets only the attrs which are not yet defined
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

        glpane = self.env.glpane
        if self.glpane_state.glname is None or 'TRY ALLOCATING A NEW NAME EACH TIME 061120 958p':
            # allocate a new glname for the first time (specific to this ipath)
            glname = glpane.alloc_my_glselect_name( glname_handler) #bruce 080917 revised
            self.glpane_state.glname = glname
        else:
            # reuse old glname for new self
            if 0:
                # when we never reused glname for new self, we could do this:
                glname = glpane.alloc_my_glselect_name( glname_handler)
                self.glpane_state.glname = glname
                    #e if we might never be drawn, we could optim by only doing this on demand
            else:
                # but now that we might be recreated and want to reuse the same glname for a new self, we have to do this:
                glname = self.glpane_state.glname
                recycle_glselect_name(self.env.glpane, glname, glname_handler)
            pass

        assert is_expr_Instance_or_None( self.plain ), "%r.plain must be an Instance or None, not %r" % (self, self.plain)
            # catch bugs in subclasses which override our formula for self.plain [070326]
        
        return # from _init_instance in Highlightable
    
    def draw(self):
        glpane = self.env.glpane
        self.save_coords_if_safe()
        if self.glname != self.glpane_state.glname:
            print "bug: in %r, self.glname %r != self.glpane_state.glname %r" % \
                  (self, self.glname, self.glpane_state.glname) #070213 -- since similar bug was seen for _index_counter in class World
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
            self.drawkid( draw_this) ## draw_this.draw() # split out draw_this, 070104
        except: ##k someday this try/except might be unneeded due to drawkid
            print_compact_traceback("exception during pressed_out or plain draw, ignored: ")#061120 
            print "fyi: the object we wanted to draw when we got that exception was:",
            print "%r" % (draw_this,)
            pass # make sure we run the PopName
        PopName(self.glname)
        return

    def draw_in_abs_coords(self, glpane, color):
        """
        #doc;
        called from GLPane using an API it specifies; see also
        run_OpenGL_in_local_coords for more general related feature
        """
        # [this API comes from GLPane behavior:
        # - why does it pass color? historical: so we can just call our own draw method, with that arg (misguided even so??)
        # - what about coords? it has no way to know old ones, so we have no choice but to know or record them...
        # ]
        #
        # WARNING: This implem won't work when we can be inside a display list which is drawn in its own relative coords.
        # For latest info on what to do about that, see '061206 coordinate systems' on bruce's g5.

        # print "calling draw_in_abs_coords in",self # this does get called even when projection=True makes it seem to not work.
        # but mousing around over it does cause repeated draws, unlike when it works. Both as if it drew in wrong place.

        # Note: I'm guessing it's better to not call kid.draw() via self.drawkid( kid), in this method -- not sure. ###k [070210]
        
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

    def __repr__THAT_CAUSES_INFRECUR(self):
        # this causes infrecur, apparently because self.sbar_text indirectly calls __repr__ (perhaps while reporting some bug??);
        # so I renamed it to disable it and rely on the super version.
        sbar_text = self.sbar_text or ""
        if sbar_text:
            sbar_text = " %r" % sbar_text
        return "<%s%s at %#x>" % (self.__class__.__name__, sbar_text, id(self)) ##e improve by merging in a super version ##e zap %#x
        ## [Highlightable.py:260] [ExprsMeta.py:250] [ExprsMeta.py:318] [ExprsMeta.py:366] [Exprs.py:184] [Highlightable.py:260] ...
    
    def mouseover_statusbar_message(self): # called in GLPane.set_selobj
        """
        #doc
        [an optional method in NE1's "selobj interface"]
        """
        ###e NEEDED: we need to pick up info from the mode about the hitpoint used to pick this selobj,
        # since we may also use it to determine sbar_text, or to determine what to offer in a cmenu
        # if one is requested at this point. (In the cmenu case, the point used to choose the selobj
        # is better to use than the current mousepoint, though ideally they would not differ.) [070205]
        #
        # Note: a test shows self.env.glpane.modkeys is set as expected here (to None, 'Shift', 'Control' or 'Shift+Control'),
        # but changing a modkey doesn't call this method again, as it would need to if the message we return
        # could depend on the modkeys. That is reasonably considered to be a ###BUG. [070224]
        return str(self.sbar_text) or "%r" % (self,) #e note: that str() won't be needed once the type-coercion in Option works

    def highlight_color_for_modkeys(self, modkeys):
        """
        #doc;
        modkeys is e.g. "Shift+Control", taken from glpane.modkeys
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
##            owner = selobj_for_glname(glname)
            owner = glpane.assy.object_for_glselect_name(glname) #bruce 080917 revised
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
        import foundation.env as env
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None.
    
    ### [probably obs cmt:] grabbed from Button, maybe not yet fixed for here
            
    altkey = False # [070224] a new public Instance attr, boolean, meaningful only during press/drag/release --
        # True iff alt/option/middlebutton was down when drag started. WARNING: NOT CHANGE TRACKED. 
        # (Note: the code here does not enforce its not changing during a drag,
        #  but I think glpane.fix_buttons does.)
    
    _glpane_button = None # private helper attr for altkey

    def _update_altkey(self):
        """
        [private helper method for public read-only Instance attr self.altkey]
        """
        self._glpane_button = self.env.glpane.button or self._glpane_button # persistence needed to handle None in ReleasedOn
        self.altkey = (self._glpane_button == 'MMB')
        return
    
    def leftClick(self, point, event, mode):
        # print "HL leftClick: glpane.button = %r" % (self.env.glpane.button,) # 'MMB' or 'LMB'
        self._update_altkey()
        # Note: it's probably the case that glpane.modkeys is one of None, 'Shift', 'Control' or 'Shift+Control',
        # in this and in other event methods,
        # but that as of 070224 this is never called when Option/Alt key (or middle mouse button) is pressed.
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
        # print "HL DraggedOn: glpane.button = %r" % (self.env.glpane.button,) # 'MMB' or 'LMB'
        self._update_altkey()
        # obs cmt: only ok for Button so far
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
        # print "HL ReleasedOn: glpane.button = %r" % (self.env.glpane.button,) # always None.
        self._update_altkey()
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

    def leftDouble(self, event, mode):
        # print "fyi: Highlightable %r got leftDouble" % self
        # Note: if something (this code, or its on_doubleclick option)
        # decides to do on_press sometimes, it ought to reset the flag mode.ignore_next_leftUp_event
        # (assuming mode is the graphicsMode, as I think it probably is & should be -- bruce 071022)
        # which was just set by testmode.leftDouble, which otherwise prevents calling self.ReleasedOn.
        # But if that something is the contents of on_doubleclick, how is that possible?!?
        # The only solution I can think of is for on_drag and on_release to get replaced by on_double_drag and
        # on_double_release in those cases (and to rename on_doubleclick to on_double_click).Hmm.... ###REVIEW SOON
        # 
        # Note: this is called on the press of the 2nd click in a double click (when self is the drag_handler),
        # not on the release.
        #
        # Note: I don't know whether it's guaranteed that no significant mouse motion occurred during the doubleclick
        # (or even that the two clicks occurred in the same Qt widget -- btw, when they didn't, it can be due to mouse motion,
        #  or to a widget being hidden or shown).
        self._do_action('on_doubleclick') #k is this all we need?? what about update_selobj? inval/gl_update?
        return
    
    def _do_action(self, name, motion = False, glpane_bindings = {}):
        """
        [private, should only be called with one of our action-option names,
        like on_press or on_release_in (not on_release)]

        Do all actions defined for name: those from self.behavior, and those
        from our own options (in that order).

        @note: prior to 080129, an action option on self would override
        an action defined in self.behavior. Now it post-extends it instead.
        AFAIK this never mattered until now.
        """
##      if not motion:
##          # debug print temporarily reenabled for sake of DnaSegment_EditCommand.py
##          # since this is not getting called for on_release, don't know why
##          # [bruce 080129]
##          print "_do_action for %r in %r" % (name, self)
        assert name.startswith('on_')
        actions = []
        # action from self.behavior
        behavior = self.behavior
        if behavior:
            # note: behavior shouldn't be another Highlightable, but a DragBehavior
            action = getattr(behavior, name, None)
##            if behavior:
##                if not action:
##                    print "%r: behavior %r but no action for %r" % (self, behavior, name)
##                else:
##                    print "%r: behavior %r has action %r for %r" % (self, behavior, action, name)
            if action:
                actions.append(action)
        # action from an option of self
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
            actions.append(action)
        del action
        # do the actions
        if actions:
            if glpane_bindings: # new feature 061205 - dynamic bindings of specific attrnames in glpane
                glpane = self.env.glpane
                for k,v in glpane_bindings.iteritems(): # these k should only be hardcoded in this class, not caller-supplied
                    assert not hasattr(glpane, k) #e might revise to let it be a default value in the class, or more
                    setattr(glpane, k, v)
                        #e or could call glpane.somedict.update(glpane_bindings) -- maybe more controlled if it keeps them in a dict
            try:
                for action in actions:
                    action()
            finally:
                if glpane_bindings:
                    for k in glpane_bindings.iterkeys():
                        delattr(glpane, k)
        return

    def inval(self, mode): ###k needed??
        """
        we might look different now;
        make sure display lists that might contain us are remade [stub],
        and glpanes are updated
        """
        ### 061120 guess: prob not needed in theory, and de-optim, but conservative, and otherwise harmless.
        # the fact that it comes before the side effect routines in its callers
        # ought to be ok unless they do recursive event processing. still, why not do it after instead? not sure... ##e
        # plan: try doing it after as last resort bugfix; otoh if bugs gone, try never doing it.
        
        ## exprs_globals.havelist = False
        ## mode.o.gl_update()
        self.KLUGE_gl_update()
        return

    def make_selobj_cmenu_items(self, menu_spec): # 070204 new feature, experimental
        """
        Add self-specific context menu items to [mutable] <menu_spec> list when self is the selobj.
        [For more examples, see this method as implemented in chem.py, jigs*.py in cad/src.]
        """
        obj = self.cmenu_maker # might be None or a ModelObject
        method = getattr(obj, 'make_selobj_cmenu_items', None)
        if 'debug070314':
            item = ('debug: self is %r' % self, noop, 'disabled')
            menu_spec.append(item)
            if obj is not None and obj is not self:
                item = ('debug: cmenu_maker is %r' % (obj,), noop, 'disabled')
                menu_spec.append(item)
            pass
        if method is not None:
            try:
                method(menu_spec, self)
                    # 070205 revised API: pass self, so method can ask it about the event, e.g. current_event_mousepoint
                    # (###e CLEANUP NEEDED: this should be cleaned up so most cmenu methods don't need to accept and ignore that arg --
                    # maybe it should be stored in dynenv, eg glpane, or maybe make current_event_mousepoint itself dynenv-accessible.)
            except:
                print "bah" ###e traceback
                print_compact_traceback("exception seen by selobj %r in %r.make_selobj_cmenu_items(): " % (self, obj) )
        else:
            # remove soon, or improve -- classname??        
            item = ('no cmenu provided by this selobj', noop, 'disabled')
            menu_spec.append(item)
        return

    pass # end of class Highlightable

Button = Highlightable # [maybe this should be deprecated, but it's still in use, and maybe it should instead be a variant subclass]

# ==

class _UNKNOWN_SELOBJ_class(Selobj_API): #061218 
    """
    [private helper, for a kluge]
    """
    def handles_updates(self): #k guessing this one might be needed
        return True
    # these methods were found by experiment to be needed
    def selobj_still_ok(self, glpane):
        return (self is getattr(glpane.graphicsMode, 'UNKNOWN_SELOBJ'))
            # goal: True in the same graphicsMode instance that we were created for, False otherwise
    highlight_color_for_modkeys = noop #e will it need to be a method which returns a color? I doubt it.
    leftClick = noop
    # this is in case we didn't find one that's needed:
    def __getattr__(self, attr): # in class _UNKNOWN_SELOBJ_class
        if attr.startswith("__"):
            raise AttributeError, attr
        if debug_flags.atom_debug:###
            print "_UNKNOWN_SELOBJ_class returns noop for attr %r" % attr
        setattr(self, attr, noop) # optim
        return noop # fake bound method
    # we might need methods for other MouseSensor_interface methods:
    # (note, MouseSensor_interface is a proposed rename of part of Selobj_API)
    # draw_in_abs_coords
    # leftClick
    # mouseover_statusbar_message
    # highlight_color_for_modkeys
    # selobj_still_ok
    # etc
    pass

def _setup_UNKNOWN_SELOBJ_on_graphicsMode(graphicsMode): #061218, revised 071010
    """
    [private helper, for a kluge -- see comment where called]
    """
    # The only call as of 071010 is in exprs/test.py which sets it on testmode, and says:
    #   fixes "highlight sync bug" in which click on checkbox, then rapid motion away from it,
    #   then click again, could falsely click the same checkbox twice.
    # I can't recall exactly how that fix worked. About how glpane.selobj ever becomes equal to this,
    # there is code in SelectAtoms_GraphicsMode and SelectChunks_GraphicsMode
    # which does that, in update_selobj.
    # TODO: document how this works sometime, and figure out whether it should be set up
    # per-Command or per-graphicsMode. Either way we'll need a class constant to request it,
    # since right now nothing can set it up except in testmode. For now I'll treat it as per-command
    # since that seems best regarding the uniqueness... but this change is NIM. [bruce 071010]

    # bruce 071017 commenting out this isinstance assert, to help chop up the
    # import cycle graph, though it's legitimate in theory. A better fix would
    # be to split GraphicsMode into an API module (from which we'd import here)
    # and the implementation of basicGraphicsMode and GraphicsMode (which would
    # import a lot of other things).
    #
    ## from GraphicsMode import anyGraphicsMode # ok?
    ## assert isinstance(graphicsMode, anyGraphicsMode)
    #
    # bruce 071028 reinstating it in a harmless form:
    from command_support.GraphicsMode_API import GraphicsMode_API
    assert isinstance(graphicsMode, GraphicsMode_API)
    
    if not hasattr(graphicsMode, 'UNKNOWN_SELOBJ'):
        # note: this means each graphicsMode ends up with a unique UNKNOWN_SELOBJ,
        # which is considered still ok only within the same graphicsMode, due to the
        # comparison done in _UNKNOWN_SELOBJ_class.selobj_still_ok.
        # See comments in update_selobj routines about graphicsMode vs currentCommand for this
        # uniqueness and/or decision to use it -- it's just a guess to use graphicsMode for both.
        # [bruce 071010]
        graphicsMode.UNKNOWN_SELOBJ = _UNKNOWN_SELOBJ_class()
    return

# ==

class BackgroundObject(DelegatingInstanceOrExpr): #070322 [renamed from _BackgroundObject, and moved here from demo_drag.py, 070323]
    """
    ###doc.
    One way to describe it: analogous to DrawInCorner, but draws
    "normally but into the role of receiving events for clicks on the background"
    """
    delegate = Arg(Highlightable,
                   doc = "a Highlightable (or something that delegates to one) which can process background drag events")
    hide = Option(bool, False,
                  doc = "if true, don't draw delegate, but still let it receive background events")
    def draw(self):
        if not self.hide:
            self.drawkid(self._delegate)
        else:
            self._delegate.save_coords() ###KLUGE, unsafe in general, though correct when it's a Highlightable --
                # but without this, we get this debug print on every draw (for obvious reasons):
                ## ;;in <Highlightable#44572(i)>, saved modelview_matrix is None, not using it
        graphicsMode = self.env.glpane.graphicsMode # kluge?? maybe not, not sure
        command = graphicsMode.command # [seems best to go through graphicsMode to get to command -- bruce 071010]
        # tell event handlers that run after the present rendered frame to send press/drag/release events on empty space
        # to self._delegate
        command._background_object = self._delegate # see testmode.py comments for doc of _background_object (#doc here later)
        return
    pass # end of class BackgroundObject

# fyi, here are some slightly older comments about how to solve the problem which is now solved by BackgroundObject() --
# the plan they describe is almost the same as what I did, but the part about "the dynenv binding for event-handler obj
# at the time" is not part of what I did yet.
#
# Q: What about empty space events?
# A: if done the same way, something needs to "draw empty space" so it can see dynenv event binding at the time
# and know what testmode should send those events to. Maybe related to "drawing the entire model"??
# Sounds like a kluge, but otherwise, something needs to register itself with testmode as the recipient of those events.
# In fact, those are the same: "draw empty space" can work by doing exactly that with the dynenv binding for event-handler obj
# at the time. Not sure if this generalizes to anything else... anyway, drawing the world can do this if we ask it to, maybe...
# not sure that's a good idea, what if we draw it twice? anyway, shouldn't it have more than one component we can draw?
# model, different parts, MT, etc... maybe we can add another one for empty space.
# [end of older comments]

# end
