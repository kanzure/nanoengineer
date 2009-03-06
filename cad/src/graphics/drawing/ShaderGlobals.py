# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ShaderGlobals.py - "global state" about a kind of shader in a GL resource context

@author: Russ, Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

Russ developed some of this code in other files, mainly setup_draw.py,
glprefs.py, and drawing_globals.py.

Bruce 090303 refactored it out of those files to create this class
and its subclasses. Motivations: permit all prefs changes during a session,
and general modularity and cleanup.
"""

from OpenGL.GL import glBegin
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import glEnd
from OpenGL.GL import glEndList
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import glGenLists
from OpenGL.GL import glGetString

from OpenGL.GL import glNewList
from OpenGL.GL import GL_QUADS
from OpenGL.GL import glVertex3fv

from geometry.VQT import A

from utilities.debug import print_compact_traceback


# ==

class ShaderGlobals:
    """
    Subclasses collect the methods associated with one kind of shader.
    Instances are for a specific OpenGL "resource context".

    Covered here:
    - access to debug_prefs for whether to try to use this kind of shader
      - flags about what warnings/errors have been printed in this session
      - higher-level methods for whether to use shaders in specific ways
    - status of trying to initialize this shader in this resource context
    - the shader itself (note: if it exists, it knows whether it had an error)
    - the associated GLPrimitiveBuffer
    """

    # class constants (don't depend on subclass (kind of shader) or resource context)

    shaderCubeVerts = [ # not used
        (-1.0, -1.0, -1.0),
        ( 1.0, -1.0, -1.0),
        (-1.0,  1.0, -1.0),
        ( 1.0,  1.0, -1.0),
        (-1.0, -1.0,  1.0),
        ( 1.0, -1.0,  1.0),
        (-1.0,  1.0,  1.0),
        ( 1.0,  1.0,  1.0),
     ]
    shaderCubeIndices = [ # not used
        [0, 1, 3, 2], # -Z face.
        [4, 5, 7, 6], # +Z face.
        [0, 1, 5, 4], # -Y face.
        [2, 3, 7, 6], # +Y face.
        [0, 2, 6, 4], # -X face.
        [1, 3, 7, 5], # +X face.
     ]

    # instance variable default values
    
    shader = None # a public attribute, None or a GLShaderObject

    primitiveBuffer = None

    _tried_shader_init = False # don't try it twice in the same session
        ##### fix: shouldn't use shader source code, do that later at runtime;
        # but for now, constructing a shader also loads its source code,
        # and we have no provision to change that later even if it depends on prefs.
        # This also relates to the Q of whether shader.error can be set on construction -- it means it can.
        # Several other comments here are about this. Fixing it is high priority
        # after this refactoring. [bruce 090304]

    # access methods

    def shader_available(self):
        """
        @return: whether our shader is available for use (ignoring preferences).

        @note: this just returns (self.shader and not self.shader.error); all of
            those are public attributes, but using this method is preferred
            over testing them directly, so it's less likely you'll forget to
            test shader.error.
        """
        return self.shader and not self.shader.error
    
    # init or setup methods

    def setup_if_needed_and_not_failed(self): 
        """
        This must be called when the correct GL context is current,
        and only if this kind of shader is now desired for drawing.
        
        But it can be called many times per session (e.g. at start
        of each drawing frame which wants to use this shader).

        If this kind of shader needs setup (i.e. was not setup
        successfully in this session) and didn't fail to be setup,
        set it up now. Print message on any error.

        Caller can determine whether this worked (now or later)
        by a boolean test on self.shader_available().

        @see: self.shader_available().
        """
        if not self.shader and not self._tried_shader_init:
            self._tried_shader_init = True # set early in case of exceptions
                # note: in future, if we support reloading shader source code,
                # we'll need to reset this flag (and self.shader) to try new
                # source code.
            try:
                self._try_shader_init()
            except:
                print_compact_traceback(
                    "Error initializing %s shaders (or primitiveBuffers): " % self.primtype
                )
                self.shader = None # precaution
                pass
            if not self.shader_available():
                # Note: it's possible that self.shader but also
                # self.shader.error, e.g. due to a GLSL syntax error or
                # version error. When source code can be reloaded later,
                # due to changes in preferences which affect it,
                # we may want to set an additional error flag for creation
                # errors (to prevent us from even trying to load new code),
                # to distinguish them from code-loading errors (after which
                # it's ok to try again to load new code).
                print "Shader setup failed:", self
                    # precaution in case more specific message was not printed
                print " To work around this error, we'll use non-shader drawing for %ss." % self.primtype
                print " You can avoid trying to load GLSL shaders each time NE1 starts up"
                print " by unsetting appropriate GLPane debug_prefs. Or, updating your"
                print " graphics card drivers might make shaders work, speeding up graphics."
                print
            pass
        return

    def _try_shader_init(self):
        """
        This runs at most once, when this kind of shader is first needed.
        It should try to set up this kind of shader in this GL resource context,
        and if this works, set self.shader to the shader.
        
        When anything goes wrong it should simply print an error
        and return without setting self.shader (or setting both that
        and self.shader.error).

        It's ok for this to raise an exception, though when practical
        it's preferable to print an error and exit normally (so the
        error message can be more specific and understandable).
        
        (If we ever have more than one GL resource context, we'll want
        to factor it into the part that doesn't depend on context
        (to avoid redundant error messages) and the part that does.)
        """
        if glGetString(GL_EXTENSIONS).find("GL_ARB_shader_objects") >= 0:
            print "note: this session WILL try to use %s-shaders" % self.primtype
            pass
        else:
            # REVIEW:
            # Could we support shaders with the older GL_ARB_vertex_program and
            # GL_ARB_fragment_program with some work?  Get assembly-like vertex
            # and fragment programs from the GLSL source using an option of the
            # nVidia Cg compiler.  Needs some loading API changes too...
            # [Russ comment, late 2008]
            print "note: this session WOULD try to use %s-shaders,\n" % self.primtype, \
                "but GL_EXTENSION GL_ARB_shader_objects is not supported.\n"
            return
        
        shader_class = self.get_shader_class()
        self.shader = shader_class()
        if not self.shader.error: # see also shader_available
            # Note: self.shader.error is possible at this stage; see above.
            print "%s shader initialization is complete." % self.primtype

            primitiveBuffer_class = self.get_primitiveBuffer_class()
            self.primitiveBuffer = primitiveBuffer_class( self)
            print "%s primitive buffer initialization is complete." % self.primtype
            print

        return

    # ==

    def _setup_shaderCubeList(self): # not used
        self.shaderCubeList = glGenLists(1)
        glNewList(self.shaderCubeList, GL_COMPILE)
        verts = self.shaderCubeVerts
        indices = self.shaderCubeIndices
        glBegin(GL_QUADS)
        for i in range(6):
            for j in range(4):
                glVertex3fv(A(verts[indices[i][j]]))
                continue
            continue
        glEnd()
        glEndList()

    pass # end of class ShaderGlobals

# ==

class SphereShaderGlobals(ShaderGlobals):
    """
    """

    # class constants (don't depend on resource context)

    primtype = "sphere"

    # Special billboard drawing pattern for the sphere shader.
    # Use with shaders where drawing patterns are applied in eye (camera)
    # coordinates.  The billboard stays between the eye and the primitive.
    billboardVerts = [
        (-1.0, -1.0,  1.0),
        ( 1.0, -1.0,  1.0),
        (-1.0,  1.0,  1.0),
        ( 1.0,  1.0,  1.0),
     ]
    billboardIndices = [ 
        [0, 1, 3, 2] # +Z face.
     ]

    def get_shader_class(self):
        # done at runtime, so import error won't prevent startup #### refile this comment
        from graphics.drawing.gl_shaders import GLSphereShaderObject
        return GLSphereShaderObject

    def get_primitiveBuffer_class(self):
        from graphics.drawing.GLSphereBuffer import GLSphereBuffer
        return GLSphereBuffer

    pass

# ==

class CylinderShaderGlobals(ShaderGlobals):
    """
    """
    # class constants (don't depend on resource context)

    primtype = "cylinder"

    # Special billboard drawing pattern for the cylinder shader.
    billboardVerts = [
        (0.0, -1.0,  1.0),
        (1.0, -1.0,  1.0),
        (1.0,  1.0,  1.0),
        (0.0,  1.0,  1.0),
     ]
    billboardIndices = [
        [0, 1, 2, 3] # +Z face.
     ]

    def get_shader_class(self):
        from graphics.drawing.gl_shaders import GLCylinderShaderObject
        return GLCylinderShaderObject

    def get_primitiveBuffer_class(self):
        from graphics.drawing.GLCylinderBuffer import GLCylinderBuffer
        return GLCylinderBuffer

    pass

# end
