# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
glprefs.py - class GLPrefs encapsulates prefs affecting all Chunk display lists

@author: Brad G, Bruce, Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py.

090303 bruce refactored this and related code, pulling in shader prefs.
"""

from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import haloWidth_prefs_key

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice
from utilities.debug_prefs import Choice_boolean_False
from utilities.debug_prefs import Choice_boolean_True

import foundation.env as env

from graphics.drawing.c_renderer import quux_module_import_succeeded

# ==

_choices = [Choice_boolean_False, Choice_boolean_True]

# ==

class GLPrefs: # rename?? can't rename module to GLPrefs.py, might confuse svn on Macs
    """
    This has not yet been split into its abstract and concrete classes,
    but is best described by specifying both aspects:
    
    Abstract: instances contain cached values of preferences or other settings
    which affect overall appearance of a GLPane, or content of most or all of
    its Chunks' display lists. There are public attributes for the prefs values,
    and public methods for setting up debug_prefs and updating cached prefs
    values. The update method should be called near the beginning of paintGL
    in order that the other methods and attributes have up to date values.
    Chunks can extract a change indicator (by calling materialprefs_summary)
    which combines all prefs values in which any changes need to invalidate
    all Chunk display lists.

    Concrete: the prefs/settings values are derived from specific env.prefs
    keys and/or debug_prefs. Only one instance is needed, and any number of
    GLPanes (or other "graphics environments") can use it (in current code,
    all GLPane_minimals and nothing else uses it).
    """
    # grantham 20051118; revised by bruce 051126, 090303

    # class constants and initial values of instance variables

    # Prefs related to experimental native C renderer (quux module in
    # cad/src/experimental/pyrex-opengl)
    #
    # [note: as of 090114, this hasn't been maintained for a long time,
    #  but it might still mostly work, so we'll keep it around for now
    #  as potentially useful example code]
    
    use_c_renderer = use_c_renderer_default = False
    use_c_renderer_prefs_key = "use_c_renderer_rev2"
    
    # ColorSorter control prefs (some)

    #russ 080403: Added drawing variant selection for unbatched spheres.
    use_drawing_variant = use_drawing_variant_default = 1 # DrawArrays from CPU RAM.
    use_drawing_variant_prefs_key = "use_drawing_variant"

    #russ 080819: Added.
    _use_sphere_shaders = use_sphere_shaders_default = True #bruce 090225 revised
    use_sphere_shaders_prefs_key = "v1.2/GLPane: use_sphere_shaders"

    #russ 090116: Added.
    _use_cylinder_shaders = use_cylinder_shaders_default = True #bruce 090303 revised
    use_cylinder_shaders_prefs_key = "v1.2/GLPane: use_cylinder_shaders"

    #russ 090223: Added.
    _use_cone_shaders = use_cone_shaders_default = True #bruce 090225 revised
    use_cone_shaders_prefs_key = "v1.2/GLPane: use_cone_shaders"

    # Russ 081002: Added.
    _use_batched_primitive_shaders = use_batched_primitive_shaders_default = True #bruce 090225 revised
    use_batched_primitive_shaders_prefs_key = "v1.2/GLPane: use_batched_primitive_shaders"

    # ==

    def __init__(self):
        self._setup()
        self.update()
        return

    # == setup methods

    def _setup(self):
        """
        Call this once at startup to make sure the appropriate
        debug_prefs (if any) and env.prefs default values are defined.

        If these are all changed into prefs_constants prefs
        rather than debug_prefs, this function won't be needed.
        """
        self._setup_c_renderer_prefs()

        # material prefs don't need setup since they're all in prefs_constants
        # which we import. They don't have class constant default values above
        # since they are all set in self.update() which this method calls.

        ##  self.override_material_specular = None
        ##     # Set 4-element sequence to override material specular component.
        ##  self.override_shininess = None
        ##     # If exists, overrides shininess.
        ##  self.override_light_specular = None
        ##     # Set to 4-element sequence to override light specular component.

        self._setup_shader_prefs()

        return
    
    def _setup_c_renderer_prefs(self):
        # 20060313 grantham Added use_c_renderer debug pref, can
        # take out when C renderer used by default.

        # REVIEW: is this still next-session, or does it work fine for same session now?
        # Guess: works for same-session after today's refactoring (once it works again at all).
        # [bruce 090304]
        
        if quux_module_import_succeeded:
            initial_choice = _choices[self.use_c_renderer_default]
            self.use_c_renderer = (
                debug_pref("GLPane: use native C renderer? (next session)", #bruce 090303 revised text
                           initial_choice,
                           prefs_key = self.use_c_renderer_prefs_key))
                #bruce 060323 removed non_debug = True for A7 release, and changed
                # its prefs_key so developers start over with the default value.

        return

    def _setup_shader_prefs(self):
        #russ 080819: Added.
        initial_choice = _choices[self.use_sphere_shaders_default]
        self.use_sphere_shaders_pref = debug_pref(
            "GLPane: use sphere-shaders? (next session)", initial_choice,
            non_debug = True,
            prefs_key = self.use_sphere_shaders_prefs_key)
        #russ 90116: Added.
        initial_choice = _choices[self.use_cylinder_shaders_default]
        self.use_cylinder_shaders_pref = debug_pref(
            "GLPane: use cylinder-shaders? (next session)", initial_choice,
            non_debug = True,
            prefs_key = self.use_cylinder_shaders_prefs_key)
        #russ 90223: Added.
        initial_choice = _choices[self.use_cone_shaders_default]
        self.use_cone_shaders_pref = debug_pref(
            "GLPane: use cone-shaders? (next session)", initial_choice,
            non_debug = True,
            prefs_key = self.use_cone_shaders_prefs_key)
        # Russ 081002: Added.
        initial_choice = _choices[
            self.use_batched_primitive_shaders_default]
        self.use_batched_primitive_shaders_pref = debug_pref(
            "GLPane: use batched primitive shaders? (next session)", initial_choice,
            non_debug = True,
            prefs_key = self.use_batched_primitive_shaders_prefs_key)

        #russ 080403: Added drawing variant selection for unbatched spheres
        # (update, bruce 090304: mainly of historical interest or for testing,
        #  but does matter on older machines that can't use shaders;
        #  could be extended to affect other primitives, but hasn't been
        #  as of 090304)
        variants = [
            "0. OpenGL 1.0 - glBegin/glEnd tri-strips vertex-by-vertex.",
            "1. OpenGL 1.1 - glDrawArrays from CPU RAM.",
            "2. OpenGL 1.1 - glDrawElements indexed arrays from CPU RAM.",
            "3. OpenGL 1.5 - glDrawArrays from graphics RAM VBO.",
            "4. OpenGL 1.5 - glDrawElements, verts in VBO, index in CPU.",
            "5. OpenGL 1.5 - VBO/IBO buffered glDrawElements.",
         ]
        self.use_drawing_variant = debug_pref(
            "GLPane: drawing method (unbatched spheres)",
            Choice(names = variants,
                   values = range(len(variants)),
                   defaultValue = self.use_drawing_variant_default),
            prefs_key = self.use_drawing_variant_prefs_key)
        return

    # ==
    
    def update(self): #bruce 051126, revised 090303
        """
        Update attributes from current drawing-related prefs stored in prefs db
        cache. This should be called at the start of each complete redraw, or
        whenever the user changes these global prefs values (whichever is more
        convenient).

        It is ok to call this more than once at those times --
        this will be a slight slowdown but cause no other harm. (Current code
        does this because more than one glpane can share one GLPrefs object,
        and because of a kluge which requires GLPane itself to update it twice.)

        (Note: When this is called during redraw, its prefs db accesses (like
        any others) record those prefs as potentially affecting what should be
        drawn, so that subsequent changes to those prefs values cause an
        automatic gl_update.)

        Using these attributes in drawing code (rather than directly accessing
        prefs db cache) is desirable for efficiency, since direct access to
        prefs db cache is a bit slow.  (Our drawing code still does that in
        other places -- those might also benefit from this system, though this
        will someday be moot when low-level drawing code gets rewritten in C.)
        """
        self._update_c_renderer_prefs()
        self._update_material_prefs()
        self._update_shader_prefs()
        return

    def _update_c_renderer_prefs(self):
        self.use_c_renderer = (
            quux_module_import_succeeded and
            env.prefs.get(self.use_c_renderer_prefs_key,
                          self.use_c_renderer_default)
         )

        if self.use_c_renderer:
            import quux
            quux.shapeRendererSetMaterialParameters(self.specular_whiteness,
                                                    self.specular_brightness,
                                                    self.specular_shininess )
            pass
        return

    def _update_material_prefs(self):
        self.enable_specular_highlights = not not env.prefs[
            material_specular_highlights_prefs_key] # boolean
        
        if self.enable_specular_highlights:
            self.override_light_specular = None # used in glpane
            # self.specular_shininess: float; shininess exponent for all
            # specular highlights
            self.specular_shininess = float(
                env.prefs[material_specular_shininess_prefs_key])
            # self.specular_whiteness: float; whiteness for all material
            # specular colors
            self.specular_whiteness = float(
                env.prefs[material_specular_finish_prefs_key])
            # self.specular_brightness: float; for all material specular colors
            self.specular_brightness = float(
                env.prefs[material_specular_brightness_prefs_key])
        else:
            self.override_light_specular = (0.0, 0.0, 0.0, 0.0) # used in glpane
            # Set these to reasonable values, though these attributes are
            # presumably never used in this case.  Don't access the prefs db in
            # this case, since that would cause UI prefs changes to do
            # unnecessary gl_updates.  (If we ever add a scenegraph node which
            # can enable specular highlights but use outside values for these
            # parameters, then to make it work correctly we'll need to revise
            # this code.)
            self.specular_shininess = 20.0
            self.specular_whiteness = 1.0
            self.specular_brightness = 1.0
            pass
        return

    def _update_shader_prefs(self):

        # Russ 080915: Extracted from GLPrefs.update() to break an import cycle.
        #
        # bruce 090303 renamed this from updatePrefsVars, refactored it
        # from a global function to a method of this class, and heavily
        # revised related code.
        
        # implem note: this is slightly faster than directly calling debug_pref
        # (though that needs to be done the first time, via _setup_shader_prefs);
        # and as of 090303 the split between this and _setup_shader_prefs is
        # confined to this module, so if we change some of these to non-debug_prefs
        # no external code should need to be changed. [bruce 090303 comment]
        
        self._use_sphere_shaders = env.prefs.get(
            self.use_sphere_shaders_prefs_key,
            self.use_sphere_shaders_default)

        self._use_cylinder_shaders = env.prefs.get(
            self.use_cylinder_shaders_prefs_key,
            self.use_cylinder_shaders_default)

        self._use_cone_shaders = env.prefs.get(
            self.use_cone_shaders_prefs_key,
            self.use_cone_shaders_default)

        self._use_batched_primitive_shaders = env.prefs.get(
            self.use_batched_primitive_shaders_prefs_key,
            self.use_batched_primitive_shaders_default)

        self.use_drawing_variant = env.prefs.get(
            self.use_drawing_variant_prefs_key,
            self.use_drawing_variant_default)

        return

    # ==
    
    def materialprefs_summary(self): #bruce 051126  #### TODO: RENAME
        """
        Return a Python data object summarizing our prefs which affect chunk
        display lists, so that memoized display lists should become invalid (due
        to changes in this object) if and only if this value becomes different.

        @note: only valid if self.update() has been called recently.
        """
        #### todo: optimization: condense into a single change indicator counter,
        # by comparing the tuple ourselves. Or (perhaps more optimal
        # when we're shared by several GLPanes), make sure all callers do that.

        res = (self.enable_specular_highlights,)
        if self.enable_specular_highlights:
            res = res + ( self.specular_shininess,
                          self.specular_whiteness,
                          self.specular_brightness )

        res += ( self.use_c_renderer,
                 self.use_drawing_variant,
                 self._use_sphere_shaders,
                 self._use_cylinder_shaders,
                 self._use_cone_shaders,
                 self._use_batched_primitive_shaders,
               )

        # russ 080530: Selection style preference controls select_dl contents.
        res += (env.prefs[selectionColorStyle_prefs_key],)
        res += (env.prefs[selectionColor_prefs_key],)
        res += (env.prefs[haloWidth_prefs_key],)

        return res

    # ==

    def sphereShader_desired(self): #bruce 090303
        """
        Based only on preferences, is it desired to use shaders
        for spheres in CSDLs?

        @note: only valid if self.update() has been called recently.
            This is ensured by current code by calling this via enable_shaders
            which is called only in configure_enabled_shaders, which is only
            called after its caller (GLPane in one call of paintGL)
            has called self.update.
        """
        return self._use_batched_primitive_shaders and self._use_sphere_shaders

    def cylinderShader_desired(self): #bruce 090303
        """
        Based only on preferences, is it desired to use shaders
        for cylinders in CSDLs?

        @note: only valid if self.update() has been called recently.
        """
        return self._use_batched_primitive_shaders and self._use_cylinder_shaders

    def coneShader_desired(self): #bruce 090303
        """
        Based only on preferences, is it desired to use shaders
        for cones in CSDLs?

        @note: only valid if self.update() has been called recently.
        """
        # this is intentionally not symmetric with cylinderShader_desired(),
        # since we want turning off cylinder shader pref to turn off all uses
        # of the cylinder shader, including cones.
        return self._use_batched_primitive_shaders and self._use_cylinder_shaders and \
               self._use_cone_shaders

    pass # end of class glprefs

# end
