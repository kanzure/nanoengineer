# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ColorSorter.py - sort primitives and store them in a ColorSortedDisplayList

@author: Grantham, Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

This was originally written by Brad Grantham (as part of drawer.py)
as a GL optimization to minimize calls on apply_material, 
by sorting primitives into display lists based on color.

Later, it was repurposed by Russ to support runtime-determined drawing styles
and to permit some primitives to be drawn using GLSL shaders.

For early details see drawer.py history. More recent details are here
(though some of them cover the time before drawer.py was split
and might be redundant with drawer.py history):

080210 russ Split the single display-list into two second-level lists (with and
without color) and a set of per-color sublists so selection and hover-highlight
can over-ride Chunk base colors.  ColorSortedDisplayList is now a class in the
parent's displist attr to keep track of all that stuff.

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080313 russ Added triangle-strip icosa-sphere constructor, "getSphereTriStrips".

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py

081003 russ Added sphere shader-primitive support to CSDLs.

081126 russ Added CSDL shader hover-highlight support, including glname drawing.

090119 russ Added cylinder shader-primitive support.

090220 bruce split class ColorSortedDisplayList into its own file

REVIEW [bruce 090114; some of this now belongs in ColorSortedDisplayList.py]:

* there are a lot of calls of glGenLists(1) that would be VRAM memory leaks
if they didn't deallocate any prior display list being stored in the same attribute
as the new one. I *think* they are not leaks, since self._reset is called
before them, and it calls self.deallocate_displists, but it would be good 
to confirm this by independent review, and perhaps to assert that all 
re-allocated DL id attributes are zero (and zero them in deallocate_displists),
to make this very clear.

* see my comments dated 090114 about cleaning up .dl, .selected, .selectPick,
and activate (and related comments in CrystalShape.py and chunk.py).

TODO:

Change ColorSorter into a normal class with distinct instances.
Give it a stack of instances rather than its current _suspend system.
Maybe, refactor some more things between ColorSorter and ColorSortedDisplayList
(which also needs renaming). [bruce 090220/090224 comment]
"""

from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glColor3fv
from OpenGL.GL import glDepthMask
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glPopName
from OpenGL.GL import glPushName
from OpenGL.GL import GL_SRC_ALPHA

from OpenGL.GL import GL_TRUE

from geometry.VQT import A


from utilities.debug import print_compact_stack

from graphics.drawing.c_renderer import quux_module_import_succeeded
if quux_module_import_succeeded:
    import quux

from graphics.drawing.c_renderer import ShapeList_inplace

from graphics.drawing.CS_workers import drawcylinder_worker
from graphics.drawing.CS_workers import drawline_worker
from graphics.drawing.CS_workers import drawpolycone_multicolor_worker
from graphics.drawing.CS_workers import drawpolycone_worker
from graphics.drawing.CS_workers import drawsphere_worker
from graphics.drawing.CS_workers import drawsphere_worker_loop
from graphics.drawing.CS_workers import drawsurface_worker
from graphics.drawing.CS_workers import drawwiresphere_worker
from graphics.drawing.CS_workers import drawtriangle_strip_worker

from graphics.drawing.gl_lighting import apply_material

# ==

_DEBUG = False

# ==

import graphics.drawing.drawing_globals as drawing_globals # only used for glprefs

class _fake_GLPane: #bruce 090220
    permit_shaders = False
        # not sure if this matters -- maybe it does for immediate-mode spheres?
    transforms = () # or make this [] if necessary, but value should never change
    glprefs = drawing_globals.glprefs #bruce 090304
    pass

_the_fake_GLPane = _fake_GLPane()
    # as of 090304 we use this as the non-sorting value of
    # ColorSorter.glpane, rather than None like before

class ColorSorter:
    """
    State Sorter specializing in color (really any object that can be
    passed to apply_material, which on 20051204 is only color 4-tuples)

    Invoke start() to begin sorting.
    
    Call finish() to complete sorting; pass draw_now = True to also draw
    all sorted objects at that time.

    Call schedule() with any function and parameters to be sorted by color.
    If not sorting, schedule() will invoke the function immediately.  If
    sorting, then the function will not be called until "finish()" or later.

    In any function which will take part in sorting which previously did
    not, create a worker function from the old function except the call to
    apply_material.  Then create a wrapper which calls
    ColorSorter.schedule with the worker function and its params.

    Also an app can call schedule_sphere and schedule_cylinder to
    schedule a sphere or a cylinder.  Right now this is the only way
    to directly access the native C++ rendering engine.
    """
    __author__ = "grantham@plunk.org"

    # For now, these are class globals.  As long as OpenGL drawing is
    # serialized and Sorting isn't nested, this is okay.
    #
    # [update, bruce 090220: it's now nested, so this should be changed.
    #  for now, we kluge it with _suspend/_unsuspend_if_needed methods.
    #  Note that this makes ColorSorter.start/finish slower than if we had
    #  a stack of ColorSorter instances, which is what we *should* do.]
    # 
    # When/if
    # OpenGL drawing becomes multi-threaded, sorters will have to
    # become instances.  This is probably okay because objects and
    # materials will probably become objects of their own about that
    # time so the whole system will get a redesign and
    # reimplementation.

    _suspended_states = [] #bruce 090220

    def _init_state(): # staticmethod
        """
        Initialize all state variables.except _suspended_states.
        
        @note: this is called immediately after defining this class,
               and in _suspend.
        """
        # Note: all state variables (except _suspended_states) must be
        # initialized here, saved in _suspend, and restored in
        # _unsuspend_if_needed.
    
        ColorSorter.sorting = False # Guard against nested sorting

        ColorSorter._sorted = 0     # Number of calls to _add_to_sorter since last _printstats

        ColorSorter._immediate = 0  # Number of calls to _invoke_immediately since last _printstats

        ColorSorter._gl_name_stack = [0] # internal record of GL name stack; 0 is a sentinel

        ColorSorter._parent_csdl = None  # Passed from start() to finish()

        ColorSorter.glpane = _the_fake_GLPane #bruce 090220/090304

        ColorSorter._initial_transforms = None #bruce 090220

        ColorSorter._permit_shaders = True
            # modified in ColorSorter.start based on glpane;
            # note that it has no effect on use of specific shaders
            # unless a corresponding shader_desired function in ColorSorter.glpane.glprefs
            # returns true (due to how it's used in this code)
            # [bruce 090224, revised 090303]

        # following are guesses by bruce 090220:
        ColorSorter.sorted_by_color = None
        ColorSorter._cur_shapelist = None
        ColorSorter.sphereLevel = -1
        
        return

    _init_state = staticmethod(_init_state)

    def _suspend(): # staticmethod
        """
        Save our state so we can reentrantly start.
        """
        # ColorSorter._suspended_states is a list of suspended states.
        class _attrholder:
            pass
        state = _attrholder()

        if len(ColorSorter._gl_name_stack) > 1:
            print "fyi: name stack is non-null when suspended -- bug?", ColorSorter._gl_name_stack #####
        
        state.sorting = ColorSorter.sorting
        state._sorted = ColorSorter._sorted
        state._immediate = ColorSorter._immediate
        state._gl_name_stack = ColorSorter._gl_name_stack
        state._parent_csdl = ColorSorter._parent_csdl
        state.glpane = ColorSorter.glpane
        state._initial_transforms = ColorSorter._initial_transforms
        state._permit_shaders = ColorSorter._permit_shaders
        state.sorted_by_color = ColorSorter.sorted_by_color
        state._cur_shapelist = ColorSorter._cur_shapelist
        state.sphereLevel = ColorSorter.sphereLevel
        
        ColorSorter._suspended_states += [state]
        ColorSorter._init_state()
        return
    
    _suspend = staticmethod(_suspend)

    def _unsuspend_if_needed(): # staticmethod
        """
        If we're suspended, unsuspend.
        Otherwise, reinit state as a precaution.
        """
        if ColorSorter._suspended_states:
            state = ColorSorter._suspended_states.pop()

            ColorSorter.sorting = state.sorting
            ColorSorter._sorted = state._sorted
            ColorSorter._immediate = state._immediate
            ColorSorter._gl_name_stack = state._gl_name_stack
            ColorSorter._parent_csdl = state._parent_csdl
            ColorSorter.glpane = state.glpane
            ColorSorter._initial_transforms = state._initial_transforms
            ColorSorter._permit_shaders = state._permit_shaders
            ColorSorter.sorted_by_color = state.sorted_by_color
            ColorSorter._cur_shapelist = state._cur_shapelist
            ColorSorter.sphereLevel = state.sphereLevel
            pass
        else:
            #bruce 090220 guess precaution
            assert len(ColorSorter._gl_name_stack) == 1, \
                   "should be length 1: %r" % (ColorSorter._gl_name_stack,)
            ColorSorter._init_state()
        
        return
    
    _unsuspend_if_needed = staticmethod(_unsuspend_if_needed)

    # ==

    def _relative_transforms(): # staticmethod #bruce 090220
        """
        Return a list or tuple (owned by caller) of the additional transforms
        we're presently inside, relative to when start() was called.
        
        Also do related sanity checks (as assertions).
        """
        t1 = ColorSorter._initial_transforms
        n1 = len(t1)

        t2 = ColorSorter.glpane.transforms # should be same or more
        n2 = len(t2)

        if n1 < n2:
            assert t1 == t2[:n1]
            return tuple(t2[n1:])
        else:
            assert n1 <= n2
            return ()
        pass
    
    _relative_transforms = staticmethod(_relative_transforms)

    def _debug_transforms(): # staticmethod #bruce 090220
        return [ColorSorter._initial_transforms,
                ColorSorter._relative_transforms()]

    _debug_transforms = staticmethod(_debug_transforms)

    def _transform_point(point): # staticmethod #bruce 090223
        """
        Apply our current relative transforms to the given point.

        @return: the transformed point.
        """
        for t in ColorSorter._relative_transforms():
            point = t.applyToPoint(point)
                ### todo (not urgent): implem in TransformControl,
                # document it there as part of TransformControl_API,
                # make a class of that name, inherit it from Chunk
        return point

    _transform_point = staticmethod(_transform_point)

    # if necessary, we'll also implement _transform_vector

    def _warn_transforms_nim(funcname): # staticmethod #bruce 090223
        print_compact_stack("bug: use of _relative_transforms nim in %s: " % funcname)
        return

    _warn_transforms_nim = staticmethod(_warn_transforms_nim)
        
    # ==
    
    def pushName(glname):
        """
        Record the current pushed GL name, which must not be 0.
        """
        #bruce 060217 Added this assert.
        assert glname, "glname of 0 is illegal (used as sentinel)"
        ColorSorter._gl_name_stack.append(glname)

    pushName = staticmethod(pushName)


    def popName():
        """
        Record a pop of the GL name.
        """
        del ColorSorter._gl_name_stack[-1]

    popName = staticmethod(popName)


    def _printstats():
        """
        Internal function for developers to call to print stats on number of
        sorted and immediately-called objects.
        """
        print ("Since previous 'stats', %d sorted, %d immediate: " %
               (ColorSorter._sorted, ColorSorter._immediate))
        ColorSorter._sorted = 0
        ColorSorter._immediate = 0

    _printstats = staticmethod(_printstats)


    def _add_to_sorter(color, func, params):
        """
        Internal function that stores 'scheduled' operations for a later
        sort, between a start/finish
        """
        ColorSorter._sorted += 1
        color = tuple(color)
        if not ColorSorter.sorted_by_color.has_key(color):
            ColorSorter.sorted_by_color[color] = []
        ColorSorter.sorted_by_color[color].append(
            (func, params, ColorSorter._gl_name_stack[-1]))

    _add_to_sorter = staticmethod(_add_to_sorter)


    def schedule(color, func, params): # staticmethod
        if ColorSorter.sorting:

            ColorSorter._add_to_sorter(color, func, params)

        else:

            ColorSorter._immediate += 1 # for benchmark/debug stats, mostly

            # 20060216 We know we can do this here because the stack is
            # only ever one element deep
            name = ColorSorter._gl_name_stack[-1]
            if name:
                glPushName(name)
            ## Don't check in immediate drawing, e.g. preDraw_glselect_dict.
            ## else:
            ##   print "bug_1: attempt to push non-glname", name

            #Apply appropriate opacity for the object if it is specified
            #in the 'color' param. (Also do necessary things such as 
            #call glBlendFunc it. -- Ninad 20071009

            if len(color) == 4:
                opacity = color[3]
            else:
                opacity = 1.0

            if opacity >= 0.0 and opacity != 1.0:	
                glDepthMask(GL_FALSE)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            elif opacity == -1: 
                # piotr 080429: I replaced the " < 0" condition with " == -1"
                # The opacity flag is now used to signal either "unshaded
                # colors" (opacity == -1) or "multicolor object" (opacity == -2)
                glDisable(GL_LIGHTING)          # Don't forget to re-enable it!
                glColor3fv(color[:3])
                pass

            apply_material(color)
            func(params)                # Call the draw worker function.

            if opacity > 0.0 and opacity != 1.0:
                glDisable(GL_BLEND)
                glDepthMask(GL_TRUE)
            elif opacity == -1: 
                # piotr 080429: See my comment above.
                glEnable(GL_LIGHTING)

            if name:
                glPopName()
        return

    schedule = staticmethod(schedule)

    # ==
    
    def schedule_sphere(color, pos, radius, detailLevel,
                        opacity = 1.0, testloop = 0):
        """
        Schedule a sphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if _DEBUG and ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            print "bare_prim sphere:", ColorSorter._gl_name_stack[-1], \
                  color, pos, radius, ColorSorter._debug_transforms()

        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            pos = ColorSorter._transform_point(pos)
        
        if ColorSorter.glpane.glprefs.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_sphere(
                lcolor, pos, radius, ColorSorter._gl_name_stack[-1])
            # 20060208 grantham - I happen to know that one detailLevel
            # is chosen for all spheres, I just record it over and
            # over here, and use the last one for the render
            if (ColorSorter.sphereLevel > -1 and
                ColorSorter.sphereLevel != detailLevel):
                raise ValueError, \
                      "unexpected different sphere LOD levels within same frame"
            ColorSorter.sphereLevel = detailLevel
            pass
        else: 
            # Non-C-coded material rendering (might be sorted and/or use shaders)
            sphereBatches = ColorSorter._permit_shaders and \
                            ColorSorter.glpane.glprefs.sphereShader_desired()
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color	
                pass

            if sphereBatches and ColorSorter._parent_csdl: # Russ 080925: Added.
                # Collect lists of primitives in the CSDL, rather than sending
                # them down through the ColorSorter schedule methods into DLs.
                assert ColorSorter.sorting # since _parent_csdl is present
                ColorSorter._parent_csdl.addSphere(
                    pos, radius, lcolor,
                    # glnames come from ColorSorter.pushName()
                    ColorSorter._gl_name_stack[-1])
            else:
                vboLevel = ColorSorter.glpane.glprefs.use_drawing_variant
                    # vboLevel sets drawing strategy for unbatched spheres
                detailLevel = (vboLevel, detailLevel)
                    # KLUGE, explained in a comment inside drawsphere_worker
                if testloop > 0:
                    worker = drawsphere_worker_loop
                else:
                    worker = drawsphere_worker
                ColorSorter.schedule(
                    lcolor, worker, (pos, radius, detailLevel, testloop))
            pass
        return

    schedule_sphere = staticmethod(schedule_sphere)


    def schedule_wiresphere(color, pos, radius, detailLevel = 1):
        """
        Schedule a wiresphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if _DEBUG and ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            print "bare_prim wiresphere:", ColorSorter._gl_name_stack[-1], \
                  color, pos, radius, ColorSorter._debug_transforms()

        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            pos = ColorSorter._transform_point(pos)
            ### TODO: for this primitive more than most, it's also necessary to
            # transform the local coordinate system orientation
            # used to align the wiresphere.

        if ColorSorter.glpane.glprefs.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_wiresphere function."
            ColorSorter._cur_shapelist.add_wiresphere(
                lcolor, pos, radius, ColorSorter._gl_name_stack[-1])
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawwiresphere_worker,
                                 # Use constant-color line drawing.
                                 (color, pos, radius, detailLevel))

    schedule_wiresphere = staticmethod(schedule_wiresphere)


    def schedule_cylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0):
        """
        Schedule a cylinder for rendering whenever ColorSorter thinks is
        appropriate.

        @param pos1: axis endpoint 1
        @type pos1: Numeric array (list or tuple won't always work)

        @param pos2: axis endpoint 2
        @type pos2: Numeric array

        @note: you can pass a tuple of two radii (in place of radius)
            to make this a tapered cylinder. When cylinder shaders are active
            and supported, this will use them, otherwise it will use a polycone.
        """
        # check type of radius in the same way for all calls [bruce 090225]
        if type(radius) == type(()):
            # radius must be a tuple of 2 radii (length not checked here)
            ColorSorter._schedule_tapered_cylinder(color, pos1, pos2, radius, capped, opacity)
            return
        
        radius = float(radius)
        
        if _DEBUG and ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            print "bare_prim cylinder:", ColorSorter._gl_name_stack[-1], \
                  color, pos1, pos2, radius, capped, ColorSorter._debug_transforms()

        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant

            # note: if drawing a cylinder requires an implicit coordinate system
            # rather than just the axis endpoints (e.g. if it has a polygonal
            # cross-section or a surface texture), we'd also need to pick a
            # disambiguating point on the barrel here, outside this condition,
            # and include it in what we transform, inside this condition.
            # This need may be present now if we use this case for non-shader
            # cylinders (since they have polygonal cross-section). ##### REVIEW
            pos1 = ColorSorter._transform_point(pos1)
            pos2 = ColorSorter._transform_point(pos2)

        if ColorSorter.glpane.glprefs.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_cylinder(
                lcolor, pos1, pos2, radius,
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            # Russ 090119: Added.
            cylinderBatches = (ColorSorter._permit_shaders and
                               ColorSorter.glpane.glprefs.cylinderShader_desired() )
            if cylinderBatches and ColorSorter._parent_csdl:
                # Note: capped is not used; a test indicates it's always on
                # (at least in the tapered case). [bruce 090225 comment]
                assert ColorSorter.sorting # since _parent_csdl is present
                # note: radius can legally be a number, or a tuple of two radii,
                # but the tuple case never gets this far -- it's diverted above
                # into _schedule_tapered_cylinder.
                ColorSorter._parent_csdl.addCylinder(
                    (pos1, pos2), radius, lcolor,
                    # glnames come from ColorSorter.pushName()
                    ColorSorter._gl_name_stack[-1])
            else:
                ColorSorter.schedule(lcolor,
                                 drawcylinder_worker,
                                 (pos1, pos2, radius, capped))

    schedule_cylinder = staticmethod(schedule_cylinder)


    def _schedule_tapered_cylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0):
        """
        Schedule a tapered cylinder for rendering whenever ColorSorter thinks is
        appropriate.

        @param pos1: axis endpoint 1
        @type pos1: Numeric array (list or tuple won't always work)

        @param pos2: axis endpoint 2
        @type pos2: Numeric array

        @note: When cylinder shaders are active and supported, this will use
            them, otherwise it will use a polycone.

        @note: this is for internal use only; it does less checking that it
            might need to do if there was a public function drawtaperedcylinder
            that called it.
        """
        #bruce 090225 made this by copying and modifying schedule_cylinder.
        r1, r2 = map(float, radius)
        
        if _DEBUG and ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            print "bare_prim tapered cylinder:", ColorSorter._gl_name_stack[-1], \
                  color, pos1, pos2, radius, capped, ColorSorter._debug_transforms()

        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            # (see also comments in schedule_cylinder)
            pos1 = ColorSorter._transform_point(pos1)
            pos2 = ColorSorter._transform_point(pos2)

        if len(color) == 3:
            lcolor = (color[0], color[1], color[2], opacity)
        else:
            lcolor = color

        use_cylinder_shader = (ColorSorter._permit_shaders and
                               ColorSorter.glpane.glprefs.coneShader_desired() )
        if use_cylinder_shader and ColorSorter._parent_csdl:
            assert ColorSorter.sorting
            ColorSorter._parent_csdl.addCylinder(
                # Note: capped is not used; a test indicates it's always on
                # (at least in the tapered case). [bruce 090225 comment]
                (pos1, pos2), radius, lcolor,
                # glnames come from ColorSorter.pushName()
                ColorSorter._gl_name_stack[-1])
        else:
            # Note: capped is not used in this case either; a test indicates
            # it's effectively always on. (If it wasn't, we could try fixing
            # that by repeating pos1 and pos2 in pos_array, with 0 radius.)
            # [bruce 090225 comment]
            vec = pos2 - pos1
            pos_array = [pos1 - vec, pos1, pos2, pos2 + vec]
            rad_array = [r1, r1, r2, r2]
            ColorSorter.schedule(lcolor, drawpolycone_worker,
                                 (pos_array, rad_array))

    _schedule_tapered_cylinder = staticmethod(_schedule_tapered_cylinder)


    def schedule_polycone(color, pos_array, rad_array,
                          capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.

        @note: this never uses shaders, even if it could. For a simple cone
            or tapered cylinder, you can pass a tuple of 2 radii to drawcylinder
            which will use shaders when available.
        """        
        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            pos_array = [ColorSorter._transform_point(A(pos)) for pos in pos_array]

        if ColorSorter.glpane.glprefs.use_c_renderer and ColorSorter.sorting and 0: #bruce 090225 'and 0'
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone_multicolor function."
            ColorSorter._cur_shapelist.add_polycone(
                lcolor, pos_array, rad_array,
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawpolycone_worker,
                                 (pos_array, rad_array))

    schedule_polycone = staticmethod(schedule_polycone)


    def schedule_polycone_multicolor(color, pos_array, color_array, rad_array,
                                     capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.

        piotr 080311: this variant accepts a color array as an additional
        parameter
        """
        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            pos_array = [ColorSorter._transform_point(A(pos)) for pos in pos_array]

        if ColorSorter.glpane.glprefs.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone function."
            ColorSorter._cur_shapelist.add_polycone_multicolor(
                lcolor, pos_array, color_array, rad_array, 
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor,
                                 drawpolycone_multicolor_worker,
                                 (pos_array, color_array, rad_array))

    schedule_polycone_multicolor = staticmethod(schedule_polycone_multicolor)


    def schedule_surface(color, pos, radius, tm, nm):
        """
        Schedule a surface for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            if ColorSorter._relative_transforms():
                ColorSorter._warn_transforms_nim("schedule_surface")

        if len(color) == 3:		
            lcolor = (color[0], color[1], color[2], 1.0)
        else:
            lcolor = color		    
        ColorSorter.schedule(lcolor, drawsurface_worker, (pos, radius, tm, nm))

    schedule_surface = staticmethod(schedule_surface)


    def schedule_line(color, endpt1, endpt2, dashEnabled,
                      stipleFactor, width, isSmooth):
        """
        Schedule a line for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            endpt1 = ColorSorter._transform_point(endpt1)
            endpt2 = ColorSorter._transform_point(endpt2)
        
        #russ 080306: Signal "unshaded colors" for lines by an opacity of -1.
        color = tuple(color) + (-1,)
        ColorSorter.schedule(color, drawline_worker,
                             (endpt1, endpt2, dashEnabled,
                              stipleFactor, width, isSmooth))

    schedule_line = staticmethod(schedule_line)


    def schedule_triangle_strip(color, triangles, normals, colors):
        """
        Schedule a line for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            # todo: use different flag than .reentrant
            if ColorSorter._relative_transforms():
                ColorSorter._warn_transforms_nim("schedule_triangle_strip")

        ColorSorter.schedule(color, drawtriangle_strip_worker,
                             (triangles, normals, colors))

    schedule_triangle_strip = staticmethod(schedule_triangle_strip)

    # ==
    
    def start(glpane, csdl, pickstate = None): # staticmethod
        """
        Start sorting - objects provided to "schedule" and primitives such as
        "schedule_sphere" and "schedule_cylinder" will be stored for a sort at
        the time "finish" is called.

        glpane is used for its transform stack. It can be None, but then
        we will not notice whether primitives we collect are inside
        any transforms beyond the ones current when we start,
        and we will also never permit shaders if it's None.

        csdl is a ColorSortedDisplayList or None, in which case immediate
        drawing is done.

        pickstate (optional) indicates whether the parent is currently selected.
        """
        #russ 080225: Moved glNewList here for displist re-org.
        # (bruce 090114: removed support for use_color_sorted_vbos)
        #bruce 090220: support _parent_csdl.reentrant
        #bruce 090220: added new required first argument glpane

        if ColorSorter._parent_csdl and ColorSorter._parent_csdl.reentrant:
            assert ColorSorter.sorting
            ColorSorter._suspend()
        
        assert not ColorSorter.sorting, \
               "Called ColorSorter.start but already sorting?!"
        ColorSorter.sorting = True

        assert ColorSorter._parent_csdl is None #bruce 090105
        ColorSorter._parent_csdl = csdl  # used by finish()

        assert ColorSorter.glpane is _the_fake_GLPane
        if glpane is None:
            glpane = _the_fake_GLPane
            assert not glpane.transforms
        ColorSorter.glpane = glpane
        ColorSorter._initial_transforms = list(glpane.transforms)
        ColorSorter._permit_shaders = glpane and glpane.permit_shaders
        if _DEBUG:
            print "CS.initial transforms:", ColorSorter._debug_transforms()

        if csdl is not None:
            csdl.start(pickstate)
                #bruce 090224 refactored this into csdl.start

        if ColorSorter.glpane.glprefs.use_c_renderer:
            ColorSorter._cur_shapelist = ShapeList_inplace()
            ColorSorter.sphereLevel = -1
        else:
            ColorSorter.sorted_by_color = {}

    start = staticmethod(start)

    # ==
    
    def finish(draw_now = None): # staticmethod
        """
        Finish sorting -- objects recorded since "start" will be sorted;
        if draw_now is True, they'll also then be drawn.

        If there's no parent CSDL, we're in all-in-one-display-list mode,
        which is still a big speedup over plain immediate-mode drawing.
        In that case, draw_now must be True since it doesn't make sense
        to not draw (the drawing has already happened).
        """
        # TODO: refactor by moving some of this into methods in CSDL
        # (specifically, in ColorSorter._parent_csdl). [bruce 090224 comment]
        
        assert ColorSorter.sorting #bruce 090220, appears to be true from this code
        assert ColorSorter.glpane is not None #bruce 090220
        assert ColorSorter.glpane is not _the_fake_GLPane #bruce 090304
        
        if not ColorSorter._parent_csdl:
            #bruce 090220 revised, check _parent_csdl rather than sorting
            # (since sorting is always true); looks right but not fully analyzed
            assert draw_now, "finish(draw_now = False) makes no sense unless ColorSorter._parent_csdl"
            ### WARNING: DUPLICATE CODE with end of this method
            # (todo: split out some submethods to clean up)
            ColorSorter.sorting = False
            ColorSorter._unsuspend_if_needed()
            return                      # Plain immediate-mode, nothing to do.

        if draw_now is None:
            draw_now = False # not really needed
            print_compact_stack( "temporary warning: draw_now was not explicitly passed, using False: ") ####
            #### before release, leaving it out can mean False without a warning,
            # since by then it ought to be the "usual case". [bruce 090219]
            pass

        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        debug_which_renderer = debug_pref(
            "debug print which renderer",
            Choice_boolean_False) #bruce 060314, imperfect but tolerable

        parent_csdl = ColorSorter._parent_csdl
        ColorSorter._parent_csdl = None
            # this must be done sometime before we return;
            # it can be done here, since nothing in this method after this
            # should use it directly or add primitives to it [bruce 090105]
        if ColorSorter.glpane.glprefs.use_c_renderer:
            # WARNING: this case has not been maintained for a long time
            # [bruce 090219 comment]
            quux.shapeRendererInit()
            if debug_which_renderer:
                #bruce 060314 uncommented/revised the next line; it might have
                # to come after shapeRendererInit (not sure); it definitely has
                # to come after a graphics context is created and initialized.
                # 20060314 grantham - yes, has to come after
                # quux.shapeRendererInit .
                enabled = quux.shapeRendererGetInteger(quux.IS_VBO_ENABLED)
                print ("using C renderer: VBO %s enabled" %
                       (('is NOT', 'is')[enabled]))
            quux.shapeRendererSetUseDynamicLOD(0)
            if ColorSorter.sphereLevel != -1:
                quux.shapeRendererSetStaticLODLevels(ColorSorter.sphereLevel, 1)
            quux.shapeRendererStartDrawing()
            ColorSorter._cur_shapelist.draw()
            quux.shapeRendererFinishDrawing()
            ColorSorter.sorting = False

            # So chunks can actually record their shapelist
            # at some point if they want to
            # ColorSorter._cur_shapelist.petrify()
            # return ColorSorter._cur_shapelist      

        else:
            if debug_which_renderer:
                print "using Python renderer"

            if parent_csdl is None:
                # Either all in one display list, or immediate-mode drawing.
                ### REVIEW [bruce 090114]: are both possibilities still present, 
                # now that several old options have been removed?
                ColorSorter._draw_sorted( ColorSorter.sorted_by_color)
                pass
            else: #russ 080225
                parent_csdl.finish( ColorSorter.sorted_by_color)
                    #bruce 090224 refactored this into parent_csdl
                pass
            
            ColorSorter.sorted_by_color = None
            pass

        ### WARNING: DUPLICATE CODE with another return statement in this method

        ColorSorter.sorting = False

        if draw_now:
            # Draw the newly-built display list, and any shader primitives as well.
            if parent_csdl is not None:
                parent_csdl.draw(
                    # Use either the normal-color display list or the selected one.
                    selected = parent_csdl.selected)
        
        ColorSorter._unsuspend_if_needed()
        return

    finish = staticmethod(finish)


    def _draw_sorted(sorted_by_color):   #russ 080320: factored out of finish().
        """
        Traverse color-sorted lists, invoking worker procedures.
        """
        ### REVIEW: still needed? does this have some duplicated code with
        # parent_csdl.finish? If so, has this been maintained as that's been
        # modified? [bruce 090224 questions]
        
        glEnable(GL_LIGHTING)

        for color, funcs in sorted_by_color.iteritems():

            opacity = color[3]
            if opacity == -1:
                #piotr 080429: Opacity == -1 signals the "unshaded color".
                # Also, see my comment in "schedule".
                glDisable(GL_LIGHTING) # reenabled below
                glColor3fv(color[:3])
            else:
                apply_material(color)
                pass

            for func, params, name in funcs:
                if name:
                    glPushName(name)
                else:
                    pass ## print "bug_4: attempt to push non-glname", name
                func(params)            # Call the draw worker function.
                if name:
                    glPopName()
                    pass
                continue

            if opacity == -1:
                glEnable(GL_LIGHTING)

            continue
        return

    _draw_sorted = staticmethod(_draw_sorted)

    pass # end of class ColorSorter

ColorSorter._init_state()
    # (this would be called in __init__ if ColorSorter was a normal class.)

# end
