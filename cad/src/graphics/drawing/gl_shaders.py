# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
gl_shaders.py - OpenGL shader objects.

    For shader concepts and links, see the Wikipedia introductions at:
     http://en.wikipedia.org/wiki/GLSL
     http://en.wikipedia.org/wiki/Graphics_pipeline

    The GLSL quick reference card and language specification in PDF are useful:
     http://www.mew.cx/glsl_quickref.pdf
     http://www.opengl.org/registry/doc/GLSLangSpec.Full.1.20.8.pdf

    For the OpenGL interface, see the API man pages and ARB specifications:
     http://www.opengl.org/sdk/docs/man/
     http://oss.sgi.com/projects/ogl-sample/registry/ARB/vertex_shader.txt
     http://oss.sgi.com/projects/ogl-sample/registry/ARB/fragment_shader.txt
     http://oss.sgi.com/projects/ogl-sample/registry/ARB/shader_objects.txt

    Useful man pages for OpenGL 2.1 are at:
     http://www.opengl.org/sdk/docs/man

    PyOpenGL versions are at:
     http://pyopengl.sourceforge.net/ctypes/pydoc/OpenGL.html

@author: Russ Fish
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Russ 081002: Added some Transform state to GLSphereShaderObject, and code to
  notice when there is not enough constant memory for a matrix block
  there. Added get_texture_xforms() and get_N_CONST_XFORMS() methods.

  Moved GLSphereBuffer to its own file.  Much of its code goes to the new
  superclass, GLPrimitiveBuffer, and its helper classes HunkBuffer and Hunk.
  The setupTransforms() method stays in GLSphereShaderObject.  updateRadii() and
  sendRadii() disappeared, subsumed into the GLPrimitiveBuffer Hunk logic.

  In the sphere vertex shader, I combined center_pt and radius per-vertex
  attributes into one center_rad vec4 attribute, rather than using two vec4's
  worth of VBO memory, and added opacity to the color, changing it from a vec3
  to a vec4.  Drawing pattern vertices are now relative to the center_pt and
  scaled by the radius attributes, handled by the shader.
"""

# Whether to use texture memory for transforms, or a uniform array of mat4s.
texture_xforms = False # True
# Otherwise, use a fixed-sized block of uniform memory for transforms.
# (This is a max, refined using GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB later.)
N_CONST_XFORMS = 270  # (Gets CPU bound at 275.  Dunno why.)
# Used in fine-tuning N_CONST_XFORMS to leave room for other GPU vars and temps.
# If you increase the complexity of the vertex shader program a little bit, and
# rendering slows down by 100x, maybe you ran out of room.  Try increasing this.
VERTEX_SHADER_GPU_VAR_SLACK = 110

# Turns on a debug info message.
CHECK_TEXTURE_XFORM_LOADING = False # True  ## Never check in a True value.
#
# Note: due to an OpenGL or PyOpengl Bug, can't read back huge transform
# textures due to SIGSEGV killing Python in glGetTexImage.
#
# Traceback on MacOS 10.5.2 with 2178 transforms:
#   Exception Type:  EXC_BAD_ACCESS (SIGSEGV)
#   Exception Codes: KERN_INVALID_ADDRESS at 0x00000000251f5000
#   Thread 0 Crashed:
#   0   libSystem.B.dylib   0xffff0884 __memcpy + 228
#   1   libGLImage.dylib    0x913e8ac6 glgProcessPixelsWithProcessor + 326
#   2   GLEngine            0x1e9dbace glGetTexImage_Exec + 1534
#   3   libGL.dylib         0x9170dd4f glGetTexImage + 127
#
# And while we're on the subject, there is a crash that kills Python while
# *writing* matrices to graphics card RAM.  I suspect that libGLImage is running
# out of texture memory space.  I've looked for a method to verify that there is
# enough left, but have not found one.  Killing a bloated FireFox has helped.
#
# Traceback on MacOS 10.5.2 with only 349 transforms requested in this case.
#   Exception Type:  EXC_BAD_ACCESS (SIGSEGV)
#   Exception Codes: KERN_INVALID_ADDRESS at 0x0000000013b88000
#   Thread 0 Crashed:
#   0   libSystem.B.dylib 	0xffff08a0 __memcpy + 256
#   1   libGLImage.dylib  	0x913ea5e9 glgCopyRowsWithMemCopy(
#           GLGOperation const*, unsigned long, GLDPixelMode const*) + 121
#   2   libGLImage.dylib  	0x913e8ac6 glgProcessPixelsWithProcessor + 326
#   3   GLEngine          	0x1ea16198 gleTextureImagePut + 1752
#   4   GLEngine          	0x1ea1f896 glTexSubImage2D_Exec + 1350
#   5   libGL.dylib       	0x91708cdb glTexSubImage2D + 155

from geometry.VQT import A, norm
import utilities.EndUser as EndUser

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.gl_buffers import GLBufferObject

import foundation.env as env
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_SOLID, HHS_HALO
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_SOLID, SS_HALO
from utilities.prefs_constants import haloWidth_prefs_key

import numpy

from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB
#from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_RGBA32F_ARB
from OpenGL.GL import GL_TEXTURE_2D
#from OpenGL.GL import GL_TEXTURE_MAG_FILTER
#from OpenGL.GL import GL_TEXTURE_MIN_FILTER
#from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import GL_VALIDATE_STATUS

#from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindTexture
#from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetInteger
from OpenGL.GL import glGetTexImage
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexSubImage2D

### Substitute the 3.0.0b3 versions, which work on Windows as well as MacOS.
##from OpenGL.GL.ARB.shader_objects import glAttachObjectARB
##from OpenGL.GL.ARB.shader_objects import glCompileShaderARB
##from OpenGL.GL.ARB.shader_objects import glCreateProgramObjectARB
##from OpenGL.GL.ARB.shader_objects import glCreateShaderObjectARB
##from OpenGL.GL.ARB.shader_objects import glGetInfoLogARB
##from OpenGL.GL.ARB.shader_objects import glGetObjectParameterivARB
##from OpenGL.GL.ARB.shader_objects import glGetUniformLocationARB
##from OpenGL.GL.ARB.shader_objects import glGetUniformivARB
##from OpenGL.GL.ARB.shader_objects import glLinkProgramARB
##from OpenGL.GL.ARB.shader_objects import glShaderSourceARB
##from OpenGL.GL.ARB.shader_objects import glUniform1fARB
##from OpenGL.GL.ARB.shader_objects import glUniform1iARB
##from OpenGL.GL.ARB.shader_objects import glUniform3fvARB
##from OpenGL.GL.ARB.shader_objects import glUniform4fvARB
##from OpenGL.GL.ARB.shader_objects import glUniformMatrix4fvARB
##from OpenGL.GL.ARB.shader_objects import glUseProgramObjectARB
##from OpenGL.GL.ARB.shader_objects import glValidateProgramARB
##from OpenGL.GL.ARB.vertex_shader import glGetAttribLocationARB
from graphics.drawing.shader_objects_patch import glAttachObjectARB
from graphics.drawing.shader_objects_patch import glCompileShaderARB
from graphics.drawing.shader_objects_patch import glCreateProgramObjectARB
from graphics.drawing.shader_objects_patch import glCreateShaderObjectARB
from graphics.drawing.shader_objects_patch import glGetInfoLogARB
from graphics.drawing.shader_objects_patch import glGetObjectParameterivARB
from graphics.drawing.shader_objects_patch import glGetUniformLocationARB
from graphics.drawing.shader_objects_patch import glGetUniformivARB
from graphics.drawing.shader_objects_patch import glLinkProgramARB
from graphics.drawing.shader_objects_patch import glShaderSourceARB
from graphics.drawing.shader_objects_patch import glUniform1fARB
from graphics.drawing.shader_objects_patch import glUniform1iARB
from graphics.drawing.shader_objects_patch import glUniform3fvARB
from graphics.drawing.shader_objects_patch import glUniform4fvARB
from graphics.drawing.shader_objects_patch import glUniformMatrix4fvARB
from graphics.drawing.shader_objects_patch import glUseProgramObjectARB
from graphics.drawing.shader_objects_patch import glValidateProgramARB
from graphics.drawing.vertex_shader_patch import glGetAttribLocationARB

_warnedVars = {}

# Drawing_style constants.
DS_NORMAL = 0
DS_OVERRIDE_COLOR = 1
DS_PATTERN = 2
DS_HALO = 3

class GLSphereShaderObject(object):
    """
    An analytic sphere shader.

    This raster-converts analytic spheres, defined by a center point and radius.
    (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
    send rays through the scene for reflection/refraction, nor toward the lights
    to compute shadows.)
    """
    def __init__(self):
        # Cached info for blocks of transforms.
        self.n_transforms = None        # Size of the block.
        self.transform_memory = None    # Texture memory handle.

        # Configure the max constant RAM used for a "uniform" transforms block.
        if not texture_xforms:  # Won't be used if transforms in texture memory.
            global N_CONST_XFORMS
            oldNCX = N_CONST_XFORMS
            maxComponents = glGetInteger(GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB)
            N_CONST_XFORMS = min(
                N_CONST_XFORMS,
                # Each matrix has 16 components. Leave slack for other vars too.
                (maxComponents - VERTEX_SHADER_GPU_VAR_SLACK) / 16)
            if N_CONST_XFORMS <= 0:
                print (
                    "N_CONST_XFORMS not positive, is %d. %d max components." %
                    (N_CONST_XFORMS, maxComponents))

                # Now, we think this means we should use display lists instead.
                # A try clause around the import should disable shaders.
                raise ValueError, "not enough shader constant memory."

            elif N_CONST_XFORMS == oldNCX:
                print ("N_CONST_XFORMS unchanged at %d. %d max components." %
                       (N_CONST_XFORMS, maxComponents))
            else:
                print (
                    "N_CONST_XFORMS changed to %d, was %d. %d max components." %
                       (N_CONST_XFORMS, oldNCX, maxComponents))
                pass
            pass
        
        # Version statement has to come first in GLSL source.
        prefix = """// requires GLSL version 1.10
                    #version 110
                    """
        # Insert preprocessor constants.
        if not texture_xforms:
            prefix += "#define N_CONST_XFORMS %d\n" % N_CONST_XFORMS
            pass
        # Pass the source strings to the shader compiler.
        self.error = False
        self.sphereVerts = self.createShader(GL_VERTEX_SHADER,
                                             prefix + sphereVertSrc)
        self.sphereFrags = self.createShader(GL_FRAGMENT_SHADER, sphereFragSrc)
        if self.error:          # May be set by createShader.
            return              # Can't do anything good after an error.
        # Link the compiled shaders into a shader program.
        self.progObj = glCreateProgramObjectARB()
        glAttachObjectARB(self.progObj, self.sphereVerts)
        glAttachObjectARB(self.progObj, self.sphereFrags)
        try:
            glLinkProgramARB(self.progObj) # Checks status, raises error if bad.
        except:
            print "Shader program link error"
            print glGetInfoLogARB(self.progObj)
            self.error = True
            return              # Can't do anything good after an error.
        
        self.used = False

        # Optional, may be useful for debugging.
        glValidateProgramARB(self.progObj)
        status = glGetObjectParameterivARB(self.progObj, GL_VALIDATE_STATUS)
        if (not status):
            print "Shader program validation error"
            print glGetInfoLogARB(self.progObj)
            self.error = True
            return              # Can't do anything good after an error.

        return

    def createShader(self, shaderType, shaderSrc):
        """
        Create, load, and compile a shader.
        """
        shader = glCreateShaderObjectARB(shaderType)
        glShaderSourceARB(shader, shaderSrc)
        try:
            glCompileShaderARB(shader)    # Checks status, raises error if bad.
        except:
            types = {GL_VERTEX_SHADER:"Vertex", GL_FRAGMENT_SHADER:"Fragment"}
            print "\n%s shader program compilation error" % types[shaderType]
            print glGetInfoLogARB(shader)
            self.error = True
            pass
        return shader

    def configShader(self, glpane):
        """
        Fill in uniform variables in the shader before using to draw.

        @param glpane: The current glpane, containing NE1 graphics context
        information related to the drawing environment.
        """
        # Can't do anything good after an error loading the shader programs.
        if self.error:
            return

        # Shader needs to be active to set uniform variables.
        wasActive = self.used
        if not wasActive:
            self.use(True)
            pass

        # Default override_opacity, multiplies the normal color alpha component.
        glUniform1fARB(self.uniform("override_opacity"), 0.25) #1.0)

        # Russ 081208: Consider caching the glpane pointer.  GLPane_minimal
        # inherits from QGLWidget, which includes the OpenGL graphics context.
        # Currently we share 'display list context' and related information
        # across two kinds of OpenGL contexts, the main GLPane and the
        # ThumbViews used to select atom types, show clipboard parts, and maybe
        # more.  In the future it may be more complicated.  Then we may need to
        # be more specific about accounting for what's in particular contexts.

        # XXX Hook in full NE1 lighting scheme and material settings.
        # Material is [ambient, diffuse, specular, shininess].
        glUniform4fvARB(self.uniform("material"), 1, [0.3, 0.6, 0.5, 20.0])
        glUniform1iARB(self.uniform("perspective"), (1, 0)[glpane.ortho])

        # XXX Try built-in "uniform gl_DepthRangeParameters gl_DepthRange;"
        vdist = glpane.vdist            # See GLPane._setup_projection().
        # See GLPane_minimal.setDepthRange_Normal().
        near = vdist * (glpane.near + glpane.DEPTH_TWEAK)
        far = vdist * glpane.far
        glUniform4fvARB(self.uniform("clip"), 1,
                        [near, far, 0.5*(far + near), 1.0/(far - near)])

        # Pixel width of window for halo drawing calculations.
        self.window_width = glpane.width

        # Single light for now.
        # XXX Get NE1 lighting environment state.
        glUniform4fvARB(self.uniform("intensity"), 1, [1.0, 0.0, 0.0, 0.0])
        light0 = A([-1.0, 1.0, 1.0])
        glUniform3fvARB(self.uniform("light0"), 1, light0)
        # Blinn shading highlight vector, halfway between the light and the eye.
        eye = A([0.0, 0.0, 1.0])
        halfway0 = norm((eye + light0) / 2.0)
        glUniform3fvARB(self.uniform("light0H"), 1, halfway0)

        if not wasActive:
            self.use(False)
        return

    def setupDraw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None, opacity = 1.0):
        """
        Set up for hover-highlighting and selection drawing styles.
        There is similar code in CSDL.draw(), which has similar arguments.

        XXX Does Solid and halo now, need to implement patterned drawing too.
        """
        # Shader needs to be active to set uniform variables.
        wasActive = self.used
        if not wasActive:
            self.use(True)
            pass

        patterned_highlighting = (False and # XXX
                                  patterning and
                                  isPatternedDrawing(highlight = highlighted))
        halo_selection = (selected and
                          env.prefs[selectionColorStyle_prefs_key] == SS_HALO)
        halo_highlighting = (highlighted and
                             env.prefs[hoverHighlightingColorStyle_prefs_key] ==
                             HHS_HALO)

        # Halo drawing style is used for hover-highlighing and halo-selection.
        drawing_style = DS_NORMAL       # Solid drawing by default.
        if halo_highlighting or halo_selection:
            drawing_style = DS_HALO

            # Halo drawing was first implemented with wide-line drawing, which
            # extends to both sides of the polygon edge.  The halo is actually
            # half the wide-line width that is specified by the setting.
            # XXX The setting should be changed to give the halo width instead.
            halo_width = env.prefs[haloWidth_prefs_key] / 2.0

            # The halo width is specified in viewport pixels, as is the window
            # width the viewport transform maps onto.  In post-projection and
            # clipping normalized device coords (+-1), it's a fraction of the
            # window half-width of 1.0 .
            ndc_halo_width = halo_width / (self.window_width / 2.0)
            glUniform1fARB(self.uniform("ndc_halo_width"), ndc_halo_width)

        elif highlighted or selected:
            drawing_style = DS_NORMAL   # Non-halo highlighting or selection.
        glUniform1iARB(self.uniform("drawing_style"), drawing_style)

        # Color for selection or highlighted drawing.
        override_color = None
        if highlighted:
            if highlight_color is None: # Default highlight color.
                override_color = env.prefs[hoverHighlightingColor_prefs_key]
            else:                       # Highlight color passed as an argument.
                override_color = highlight_color
        elif selected:
            override_color = env.prefs[selectionColor_prefs_key]
            pass
        if override_color:
            if len(override_color) == 3:
                override_color += (opacity,)
                pass
            glUniform4fvARB(self.uniform("override_color"), 1, override_color)
            pass

        if not wasActive:
            self.use(False)
            pass
        return

    def setPicking(self, tf):
        """
        Controls glnames-as-color drawing mode for mouseover picking.

        There seems to be no way to access the GL name
        stack in shaders.  Instead, for mouseover, draw shader
        primitives with glnames as colors in glRenderMode(GL_RENDER),
        then read back the pixel color (glname) and depth value.

        @param tf: Boolean, draw glnames-as-color if True. 
        """
        # Shader needs to be active to set uniform variables.
        wasActive = self.used
        if not wasActive:
            self.use(True)
            pass

        glUniform1iARB(self.uniform("draw_for_mouseover"), int(tf))

        if not wasActive:
            self.use(False)
            pass
        return

    def uniform(self, name):
        """
        Return location of a uniform (input) shader variable.
        Raise a ValueError if it isn't found.
        """
        loc = glGetUniformLocationARB(self.progObj, name)
        if loc == -1:
            # The glGetUniformLocationARB man page says:
            #   "name must be an active uniform variable name in program that is
            #    not a structure, an array of structures, or a subcomponent of a
            #    vector or a matrix."
            # 
            # It "returns -1 if the name does not correspond to an active
            # uniform variable in program".  Then getUniform ignores it: "If
            # location is equal to -1, the data passed in will be silently
            # ignored and the specified uniform variable will not be changed."
            # 
            # Lets not be so quiet.
            msg = "Invalid or unused uniform shader variable name '%s'." % name
            if EndUser.enableDeveloperFeatures():
                # Developers want to know of a mismatch between their Python
                # and shader programs as soon as possible.  Not doing so causes
                # logic errors, or at least incorrect assumptions, to silently
                # propagate through the code and makes debugging more difficult.
                assert 0, msg
            else:
                # End users on the other hand, may value program stability more.
                # Just print a warning if the program is released.  Do it only
                # once per session, since this will be in the inner draw loop!
                global _warnedVars
                if name not in _warnedVars:
                    print "Warning:", msg
                    _warnedVars += [name]
                    pass
                pass
            pass
        return loc

    def getUniformInt(self, name):
        """
        Return value of a uniform (input) shader variable.
        """
        return glGetUniformivARB(self.progObj, self.uniform(name))

    def attribute(self, name):
        """
        Return location of an attribute (per-vertex input) shader variable.
        Raise a ValueError if it isn't found.
        """
        loc = glGetAttribLocationARB(self.progObj, name)
        if loc == -1:
            msg = "Invalid or unused attribute variable name '%s'." % name
            if EndUser.enableDeveloperFeatures():
                # Developers want to know of a mismatch between their Python
                # and shader programs as soon as possible.  Not doing so causes
                # logic errors, or at least incorrect assumptions, to silently
                # propagate through the code and makes debugging more difficult.
                assert 0, msg
            else:
                # End users on the other hand, may value program stability more.
                # Just print a warning if the program is released.  Do it only
                # once per session, since this will be in the inner draw loop!
                global _warnedVars
                if name not in _warnedVars:
                    print "Warning:", msg
                    _warnedVars += [name]
                    pass
                pass
            pass
        return loc

    def use(self, on):
        """
        Activate a shader.
        """
        if on:
            glUseProgramObjectARB(self.progObj)
        else:
            glUseProgramObjectARB(0)
            pass
        self.used = on
        return

    def get_texture_xforms(self):
        return texture_xforms

    def get_N_CONST_XFORMS(self):
        return N_CONST_XFORMS

    def setupTransforms(self, transforms):
        """
        Fill a block of transforms.

        Depending on the setting of texture_xforms, the transforms are either in
        texture memory, or else in a uniform array of mat4s ("constant memory".)

        @param transforms: A list of transform matrices, where each transform is
        a flattened list (or Numpy array) of 16 numbers.
        """
        self.use(True)                # Must activate before setting uniforms.
        self.n_transforms = nTransforms = len(transforms)
        glUniform1iARB(self.uniform("n_transforms"), self.n_transforms)

        # The shader bypasses transform logic if n_transforms is 0.
        # (Then sphere center points are in global modeling coordinates.)
        if nTransforms > 0:
            if not texture_xforms:
                # Load into constant memory.  The GL_EXT_bindable_uniform
                # extension supports sharing this array of mat4s through a VBO.
                # XXX Need to bank-switch this data if more than N_CONST_XFORMS.
                C_transforms = numpy.array(transforms, dtype=numpy.float32)
                glUniformMatrix4fvARB(self.uniform("transforms"),
                                      # Don't over-run the array size.
                                      min(len(transforms), N_CONST_XFORMS),
                                      GL_TRUE, # Transpose.
                                      C_transforms)
            else: # texture_xforms
                # Generate a texture ID and bind the texture unit to it.
                self.transform_memory = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self.transform_memory)
                ## These seem to have no effect with a vertex shader.
                ## glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                ## glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                # XXX Needed? glEnable(GL_TEXTURE_2D)

                # Load the transform data into the texture.
                #
                # Problem: SIGSEGV kills Python in gleTextureImagePut under
                # glTexImage2D with more than 250 transforms (16,000 bytes.)
                # Maybe there's a 16-bit signed size calculation underthere, that's
                # overflowing the sign bit... Work around by sending transforms to
                # the texture unit in batches with glTexSubImage2D.)
                glTexImage2D(GL_TEXTURE_2D, 0, # Level zero - base image, no mipmap.
                             GL_RGBA32F_ARB,   # Internal format is floating point.
                             # Column major storage: width = N, height = 4 * RGBA.
                             nTransforms, 4 * 4, 0, # No border.
                             # Data format and type, null pointer to allocate space.
                             GL_RGBA, GL_FLOAT, None)
                # XXX Split this off into a setTransforms method.
                batchSize = 250
                nBatches = (nTransforms + batchSize-1) / batchSize
                for i in range(nBatches):
                    xStart = batchSize * i
                    xEnd = min(nTransforms, xStart + batchSize)
                    xSize = xEnd - xStart
                    glTexSubImage2D(GL_TEXTURE_2D, 0,
                                    # Subimage x and y offsets and sizes.
                                    xStart, 0, xSize, 4 * 4,
                                    # List of matrices is flattened into a sequence.
                                    GL_RGBA, GL_FLOAT, transforms[xStart:xEnd])
                    continue
                # Read back to check proper loading.
                if CHECK_TEXTURE_XFORM_LOADING:
                    mats = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT)
                    nMats = len(mats)
                    print "setupTransforms\n[[",
                    for i in range(nMats):
                        nElts = len(mats[i])
                        perLine = 8
                        nLines = (nElts + perLine-1) / perLine
                        for line in range(nLines):
                            jStart = perLine * line
                            jEnd = min(nElts, jStart + perLine)
                            for j in range(jStart, jEnd):
                                print "%.2f" % mats[i][j],
                                continue
                            if line < nLines-1:
                                print "\n  ",
                                pass
                        if i < nMats-1:
                            print "]\n [",
                            pass
                        continue
                    print "]]"
                pass
            pass
        self.use(False)                # Deactivate again.
        return

    pass # End of class GLSphereShaderObject.

# ================================================================
# Sphere shader source code in GLSL.
#
# See the docstring at the beginning of the file for GLSL references.

# Note: if texture_xforms is off, a #define N_CONST_XFORMS array dimension is
# prepended to the following.  The #version statement must preceed it.
sphereVertSrc = """
// Vertex shader program for sphere primitives.
// 
// This raster-converts analytic spheres, defined by a center point and radius.
// The rendered spheres are smooth, with no polygon facets.  Exact shading,
// depth, and normals are calculated in parallel in the GPU at each pixel.
// 
// It sends an eye-space ray from the view point to the sphere at each pixel.
// Some people call that a ray-tracer, but unlike a real ray-tracer it cannot
// send more rays through the scene to intersect other geometry for
// reflection/refraction calculations, nor toward the lights for shadows.
// 
// How it works:
// 
// A bounding volume of faces may be drawn around the sphere in OpenGL, or
// alternately a 'billboard' face may be drawn in front of the the sphere.  A
// center point and radius are also provided as vertex attributes.  The face(s)
// must cover at least the pixels where the sphere is to be rendered.  Clipping
// and lighting settings are also provided to the fragment (pixel) shader.
// 
// The view point, transformed sphere center point and radius, and a ray vector
// pointing from the view point to the transformed vertex, are output from the
// vertex shader to the fragment shader.  This is handled differently for
// orthographic and perspective projections, but it is all in pre-projection
// gl_ModelViewMatrix 'eye space', with the origin at the eye (camera) location
//  and XY coordinates parallel to the screen (window) XY.
// 
// A 'halo' radius is also passed to the fragment shader, for highlighting
// selected spheres with a flat disk when the halo drawing-style is selected.
// 
// In between the vertex shader and the fragment shader, the transformed vertex
// ray vector coords get interpolated, so it winds up being a transformed ray
// from the view point through the pixel on the bounding volume surface.
// 
// In the fragment shader, the sphere radius comparison is done using these
// points and vectors.  That is, if the ray from the eye through the pixel
// center passes within the sphere radius of the sphere center point, a depth
// and normal on the sphere surface are calculated as a function of the distance
// from the center.  If the ray is outside the sphere radius, it may still be
// within the halo disk radius surrounding the sphere.

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int draw_for_mouseover; // 0:use normal color, 1:glname_color.
uniform int drawing_style;      // 0:normal, 1:override_color, 2:pattern, 3:halo
#define DS_NORMAL 0
#define DS_OVERRIDE_COLOR 1
#define DS_PATTERN 2
#define DS_HALO 3
uniform vec4 override_color;    // Color for selection or highlighted drawing.
uniform int perspective;        // 0:orthographic, 1:perspective.
uniform float ndc_halo_width;   // Halo width in normalized device coords.

uniform int n_transforms;
#ifdef N_CONST_XFORMS
  // Transforms are in uniform (constant) memory. 
  uniform mat4 transforms[N_CONST_XFORMS]; // Must dimension at compile time.
#else
  // Transforms are in texture memory, indexed by a transform slot ID attribute.
  // Column major, one matrix per column: width=N cols, height=4 rows of vec4s.
  // GL_TEXTURE_2D is bound to transform matrices, tex coords in (0...1, 0...1).
  uniform sampler2D transforms;
#endif

// Attribute variables, which are bound to VBO arrays for each vertex coming in.
attribute vec4 center_rad;      // Sphere center point and radius.
// The following may be set to constants, when no arrays are provided.
attribute vec4 color;           // Sphere color and opacity (RGBA).
attribute float transform_id;   // Ignored if zero.  (Attribs cannot be ints.)
attribute vec4 glname_color;    // Mouseover id (glname) as RGBA for drawing.

// Varying outputs, interpolated in the pipeline to the fragment (pixel) shader.
varying vec3 var_ray_vec; // Vertex dir vec (pixel sample vec in frag shader.)
varying vec3 var_center_pt;     // Transformed sphere center point.
varying vec3 var_view_pt;       // Transformed view point.
varying float var_radius_sq;    // Transformed sphere radius, squared.
varying float var_halo_rad_sq;  // Halo rad sq at transformed center_pt Z depth.
varying vec4 var_basecolor;     // Vertex color.

void main(void) { // Vertex shader procedure.

  // Fragment (pixel) color will be interpolated from the vertex colors.
  if (draw_for_mouseover == 1)
    var_basecolor = glname_color;
  else if (drawing_style == DS_OVERRIDE_COLOR)
    // Solid highlighting or selection.
    var_basecolor = override_color;
  else
    var_basecolor = color;
  
  // The center point and radius are combined in one attribute: center_rad.
  vec4 center = vec4(center_rad.xyz, 1.0);
  float radius = center_rad.w;         // per-vertex sphere radius.

//[ ----------------------------------------------------------------
// Per-primitive transforms.
  mat4 xform;
  if (n_transforms > 0 && int(transform_id) > -1) {
    // Apply a transform, indexed by a transform slot ID vertex attribute.

#ifdef N_CONST_XFORMS
    // Get transforms from a fixed-sized block of uniform (constant) memory.
    // The GL_EXT_bindable_uniform extension allows sharing this through a VBO.
    center = transforms[int(transform_id)] * center;
#else  // texture_xforms.
# if 0 // 1   /// Never check in a 1 value.
    xform = mat4(1.0); /// Testing, override texture xform with identity matrix.
# else
    // Assemble the 4x4 matrix from a column of vec4s stored in texture memory.
    // Map the 4 rows and N columns onto the (0...1, 0...1) texture coord range.
    // The first texture coordinate goes across the width of N matrices.
    float mat = transform_id / float(n_transforms - 1);  // (0...N-1)=>(0...1) .
    // The second tex coord goes down the height of four vec4s for the matrix.
    xform = mat4(texture2D(transforms, vec2(0.0/3.0, mat)),
                 texture2D(transforms, vec2(1.0/3.0, mat)), 
                 texture2D(transforms, vec2(2.0/3.0, mat)), 
                 texture2D(transforms, vec2(3.0/3.0, mat)));
# endif
    center = xform * center;
#endif // texture_xforms.
  }
//] ----------------------------------------------------------------

//[ ================================================================
// Debugging output.
#if 0 // 1   /// Never check in a 1 value.
  // Debugging display: set the colors of a 16x16 sphere array.
  // test_drawing.py sets the transform_ids.  Assume here that
  // nSpheres = transformChunkLength = 16, so each column is one transform.

  // The center_rad coord attrib gives the subscripts of the sphere in the array.
  int offset = int(n_transforms)/2; // Undo the array centering from data setup.
  int col = int(center_rad.x) + offset;  // X picks the columns.
  int row = int(center_rad.y) + offset;  // Y picks the rows.
  if (col > 10) col--;                  // Skip the gaps.
  if (row > 10) row--;

# ifdef N_CONST_XFORMS
  // Not allowed: mat4 xform = mat4(transforms[int(transform_id)]);
  xform = mat4(transforms[int(transform_id)][0],
               transforms[int(transform_id)][1],
               transforms[int(transform_id)][2],
               transforms[int(transform_id)][3]);
# endif

  float data;
  if (true) // false  // Display matrix data.
    // This produces all zeros from a texture-map matrix.
    // The test identity matrix has 1s in rows 0, 5, 10, and 15, as it should.
    data = xform[row/4][row - (row/4)*4];  // % is unimplimented.
  else  // Display transform IDs.
    data = transform_id / float(n_transforms);

  // Default - Column-major indexing: red is column index, green is row index.
  var_basecolor = vec4(float(col)/float(n_transforms),
                       float(row)/float(n_transforms),
                       data, 1.0);
  ///if (data == 0.0) var_basecolor = vec4(1.0); // Zeros in white.
  if (data > 0.0)
    var_basecolor = vec4(data, data, data, 1.0); // Fractions in gray.
  // Matrix labels (1 + xform/100) in blue.
  if (data > 1.0) var_basecolor = vec4(0.0, 0.0, (data - 1.0) * 8.0, 1.0);
#endif
//] ================================================================

  // Center point in eye space coordinates.
  vec4 eye_center4 = gl_ModelViewMatrix * center;
  var_center_pt = eye_center4.xyz / eye_center4.w;

  // Scaled radius in eye space.  (Assume uniform scale on all axes.)
  vec4 eye_radius4 = gl_ModelViewMatrix * vec4(radius, 0.0, 0.0, 0.0);
  float eye_radius = length(vec3(eye_radius4));
  var_radius_sq = eye_radius * eye_radius; // Square roots are slow.

  // The drawing vertices are in unit coordinates, relative to the center point.
  // Scale by the radius and add to the center point in eye space.
  vec3 eye_vert_pt = var_center_pt + eye_radius * gl_Vertex.xyz;

  if (perspective == 1) {
    // With perspective, look from the origin, toward the vertex (pixel) points.
    // In eye space, the origin is at the eye point, by definition.
    var_view_pt = vec3(0.0, 0.0, 0.0);
    var_ray_vec = normalize(eye_vert_pt);
  } else {
    // Without perspective, look from the 2D pixel position, in the -Z dir.
    var_view_pt = vec3(eye_vert_pt.xy, 0.0);  
    var_ray_vec = vec3(0.0, 0.0, -1.0);
  }

  // Take the eye-space radius to post-projection units at the center pt depth.
  // (The pojection matrix doesn't change the view alignment, just the scale.)
  vec4 post_proj_radius4 =
    gl_ProjectionMatrix * vec4(eye_radius, 0.0, var_center_pt.z, 1.0);
  float post_proj_radius = post_proj_radius4.x / post_proj_radius4.w;

  // Ratio to increase the eye space radius for the halo.
  float radius_ratio = (post_proj_radius + ndc_halo_width) / post_proj_radius;
  
  // Eye space halo radius for use in the pixel shader.
  float eye_halo_radius = radius_ratio * eye_radius;
  var_halo_rad_sq = eye_halo_radius * eye_halo_radius; // Square roots are slow.

  // For halo drawing, scale up drawing primitive vertices to cover the halo.
  if (drawing_style == DS_HALO)
    eye_vert_pt = var_center_pt + eye_halo_radius * gl_Vertex.xyz;

  // Transform the drawing vertex through the projection matrix, making clip
  // coordinates for the next stage of the pipeline.
  gl_Position = gl_ProjectionMatrix * vec4(eye_vert_pt, 1.0);
}
"""

sphereFragSrc = """
// Fragment (pixel) shader program for sphere primitives.
// 
// Compute raster-scanned normal samples of analytic spheres for shading, or
// reject the pixel if it is more than the radius away from the center point.
// The center and radius are passed from the vertex shader.
// 
// Called after raster conversion of primitives, driven by the fixed-function
// pipeline, with optional vertex and geometry shader programs.

// requires GLSL version 1.10
#version 110

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int draw_for_mouseover; // 0: use normal color, 1: glname_color.
uniform int drawing_style;      // 0:normal, 1:override_color, 2:pattern, 3:halo
#define DS_NORMAL 0
#define DS_OVERRIDE_COLOR 1
#define DS_PATTERN 2
#define DS_HALO 3
uniform vec4 override_color;    // Color for selection or highlighted drawing.
uniform float override_opacity; // Multiplies the normal color alpha component.

// Lighting properties for the material.
uniform vec4 material; // Properties: [ambient, diffuse, specular, shininess].

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int perspective;
uniform vec4 clip;              // [near, far, middle, depth_inverse]

uniform vec4 intensity;    // Set an intensity component to 0 to ignore a light.

// A fixed set of lights.
uniform vec3 light0;
uniform vec3 light1;
uniform vec3 light2;
uniform vec3 light3;

uniform vec3 light0H;           // Blinn/Phong halfway/highlight vectors.
uniform vec3 light1H;
uniform vec3 light2H;
uniform vec3 light3H;

// Inputs, interpolated by raster conversion from the vertex shader outputs.
varying vec3 var_ray_vec; // Pixel sample vec (vertex dir vec in vert shader.)
varying vec3 var_center_pt;     // Transformed sphere center point.
varying vec3 var_view_pt;       // Transformed view point.
varying float var_radius_sq;    // Transformed sphere radius, squared.
varying float var_halo_rad_sq;  // Halo rad sq at transformed center_pt Z depth.
varying vec4 var_basecolor;     // Vertex color.

void main(void) {  // Fragment (pixel) shader procedure.
  // This is all in *eye space* (pre-projection camera coordinates.)

  // Vertex ray direction vectors were interpolated into pixel ray vectors.
  // These go from the view point, through a sample point on the drawn polygon,
  // *toward* the sphere (but may miss it and be discarded.)
  vec3 sample_vec = normalize(var_ray_vec); // Interpolation denormalizes vecs.

  // Project the center point onto the sample ray to find the point where
  // the sample vector passes closest to the center of the sphere.
  // . We have the coordinates of the transformed view point and sphere center.
  // . Vector from the view point to the sphere center.
  vec3 center_vec = var_center_pt - var_view_pt;

  // . The distance from the view point to the sphere center plane, which is
  //   perpendicular to the sample_vec and contains the sphere center point.
  //   (The length of the projection of the center_vec onto the sample_vec.)
  //   (Note: The sample_vec is normalized, and the center_vec is not.)
  float center_plane_dist = dot(center_vec, sample_vec);

  // . The intersection point of the sample_vec and the sphere center plane is
  //   the point closest to the sphere center point in the sample_vec *and* to
  //   the view point in the sphere center plane.
  vec3 closest_pt = var_view_pt + center_plane_dist * sample_vec;

  // How far does the ray pass from the center point in the center plane?
  // (Compare squares to avoid sqrt, which is slow, as long as we can.)
  vec3 closest_vec = closest_pt - var_center_pt;
  float plane_closest_dist_sq = dot(closest_vec, closest_vec);

  // Compare the ray intersection distance to the sphere and halo disk radii.
  float intersection_height = 0.0; // Height above the sphere center plane.
  if (plane_closest_dist_sq > var_radius_sq) {

    // Outside the sphere radius.  Nothing to do if not drawing a halo.
    if (drawing_style != DS_HALO ||
        plane_closest_dist_sq > var_halo_rad_sq) {
      discard;  // **Exit**
    }
    // Hit a halo disk, on the sphere center plane.
    else {
      gl_FragColor = override_color; // No shading or lighting on halos.
      // Not done yet, still have to compute a depth for the halo pixel.
    }

  } else {
    // The ray hit the sphere.  Use the Pythagorian Theorem to find the
    // intersection point between the ray and the sphere, closest to us.
    // 
    // The closest_pt and the center_pt on the sphere center plane, and the
    // intersection point between the ray and the sphere, make a right triangle.
    // The length of the hypotenuse is the distance between the center point and
    // the intersection point, and is equal to the radius of the sphere.
    intersection_height = sqrt(var_radius_sq - plane_closest_dist_sq);
      
    // Nothing more to do if the intersection point is *behind* the view point
    // so we are *inside the sphere.*
    if (intersection_height > center_plane_dist)
      discard; // **Exit**
  }

  // Intersection point of the ray with the sphere, and the sphere normal there.
  vec3 intersection_pt = closest_pt - intersection_height * sample_vec;
  vec3 normal = normalize(intersection_pt - var_center_pt);

  // Distance from the view point to the sphere intersection, transformed into
  // normalized device coordinates, sets the fragment depth.  (Note: The
  // clipping box depth is passed as its inverse, to save a divide.)
  float sample_z = intersection_pt.z;
  if (perspective == 1) {
    // Perspective: 0.5 + (mid + (far * near / sample_z)) / depth
    gl_FragDepth = 0.5 + (clip[2] + (clip[1] * clip[0] / sample_z)) * clip[3];
  } else {
    // Ortho: 0.5 + (-middle - sample_z) / depth
    gl_FragDepth = 0.5 + (-clip[2] - sample_z) * clip[3];
  }

  // No shading or lighting on halos.
  //// The nVidia 7600GS does not allow return in a conditional.
  ////   if (plane_closest_dist_sq > var_radius_sq)
  ////     return;   // **Exit** we are done with a halo pixel.
  //// Instead of an early return for halo pixels, invert the condition
  //// and skip the last part of the fragment shader.
  if (plane_closest_dist_sq <= var_radius_sq) {

    // Shading control, from the material and lights.
    float ambient = material[0];

    // Accumulate diffuse and specular contributions from the lights.
    float diffuse = 0.0;
    diffuse += max(0.0, dot(normal, light0)) * intensity[0];
    diffuse += max(0.0, dot(normal, light1)) * intensity[1];
    diffuse += max(0.0, dot(normal, light2)) * intensity[2];
    diffuse += max(0.0, dot(normal, light3)) * intensity[3];
    diffuse *= material[1]; // Diffuse intensity.

    // Blinn highlight location, halfway between the eye and light vecs.
    // Phong highlight intensity: Cos^n shinyness profile.  (Unphysical.)
    float specular = 0.0;
    float shininess = material[3];
    specular += pow(max(0.0, dot(normal, light0H)), shininess) * intensity[0];
    specular += pow(max(0.0, dot(normal, light1H)), shininess) * intensity[1];
    specular += pow(max(0.0, dot(normal, light2H)), shininess) * intensity[2];
    specular += pow(max(0.0, dot(normal, light3H)), shininess) * intensity[3];
    specular *= material[2]; // Specular intensity.

    // Do not do lighting while drawing glnames, just pass the values through.
    if (draw_for_mouseover == 1)
      gl_FragColor = var_basecolor;
    else if (drawing_style == DS_OVERRIDE_COLOR)
      // Highlighting looks 'special' without shinyness.
      gl_FragColor = vec4(var_basecolor.rgb * vec3(diffuse + ambient),
                          1.0);
    else
      gl_FragColor = vec4(var_basecolor.rgb * vec3(diffuse + ambient) +
                            vec3(specular),   // White highlights.
                          var_basecolor.a * override_opacity);
  }
}
"""
