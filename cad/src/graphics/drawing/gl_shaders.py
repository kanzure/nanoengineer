# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
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
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Russ 081002: Added some Transform state to GLSphereShaderObject, and code to
  notice when there is not enough constant memory for a matrix block
  there. Added get_TEXTURE_XFORMS() and get_N_CONST_XFORMS() methods.

  Moved GLSphereBuffer to its own file.  Much of its code goes to the new
  superclass, GLPrimitiveBuffer, and its helper classes HunkBuffer and Hunk.
  The setupTransforms() method stays in GLSphereShaderObject.  updateRadii() and
  sendRadii() disappeared, subsumed into the GLPrimitiveBuffer Hunk logic.

  In the sphere vertex shader, I combined center_pt and radius per-vertex
  attributes into one center_rad vec4 attribute, rather than using two vec4's
  worth of VBO memory, and added opacity to the color, changing it from a vec3
  to a vec4.  Drawing pattern vertices are now relative to the center_pt and
  scaled by the radius attributes, handled by the shader.

Russ 090116: Factored GLShaderObject out of GLSphereShaderObject, and added
  GLCylinderShaderObject.  The only difference between them at this level is the
  GLSL source passed in during initialization.
"""

# Whether to use texture memory for transforms, or a uniform array of mat4s.
TEXTURE_XFORMS = False # True
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

from graphics.drawing.sphere_shader import sphereVertSrc, sphereFragSrc
from graphics.drawing.cylinder_shader import cylinderVertSrc, cylinderFragSrc

from graphics.drawing.patterned_drawing import isPatternedDrawing

import foundation.env as env

from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_SOLID, HHS_HALO
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_SOLID, SS_HALO
from utilities.prefs_constants import haloWidth_prefs_key

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False, Choice_boolean_True

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
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import GL_VALIDATE_STATUS

from OpenGL.GL import glBindTexture
#from OpenGL.GL import glEnable
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetInteger
from OpenGL.GL import glGetTexImage
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexSubImage2D

### Substitute the PyOpenGL 3.0.0b3 versions, which work on Windows as well as MacOS.
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

class GLShaderObject(object):
    """
    Base class for managing OpenGL shaders.
    """

    # default values of per-subclass constants
    
    _has_uniform_debug_code = False
        # whether this shader has the uniform variable 'debug_code'
        # (a boolean which enables debug behavior)
        # (it might be better to set this by asking OpenGL whether
        #  that uniform exists, after loading the shader source)

    def __init__(self, shaderName, shaderVertSrc, shaderFragSrc):
        # Cached info for blocks of transforms.
        self.n_transforms = None        # Size of the block.
        self.transform_memory = None    # Texture memory handle.

        # Configure the max constant RAM used for a "uniform" transforms block.
        if not TEXTURE_XFORMS:  # Won't be used if transforms in texture memory.
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
        prefix = """// requires GLSL version 1.20
                    #version 120
                    """
        # Insert preprocessor constants.
        if not TEXTURE_XFORMS:
            prefix += "#define N_CONST_XFORMS %d\n" % N_CONST_XFORMS
        else:
            prefix += "" # To keep the shader line numbers unchanged.
            pass

        # GLSL on the nVidia GeForce 7000 only supports constant array
        # subscripts, and subscripting by a loop index variable.
        if not debug_pref("GLPane: shaders with only constant subscripts?",
                      Choice_boolean_True, prefs_key = True):
            prefix += "#define FULL_SUBSCRIPTING"
        else:
            prefix += "" # To keep the shader line numbers unchanged.
            pass

        # Pass the source strings to the shader compiler.
        self.error = False
        self.vertShader = self.createShader(shaderName, GL_VERTEX_SHADER,
                                            prefix + shaderVertSrc)
        self.fragShader = self.createShader(shaderName, GL_FRAGMENT_SHADER,
                                            prefix + shaderFragSrc)
        if self.error:          # May be set by createShader.
            return              # Can't do anything good after an error.
        # Link the compiled shaders into a shader program.
        self.progObj = glCreateProgramObjectARB()
        glAttachObjectARB(self.progObj, self.vertShader)
        glAttachObjectARB(self.progObj, self.fragShader)
        try:
            glLinkProgramARB(self.progObj) # Checks status, raises error if bad.
        except:
            print shaderName, "shader program link error"
            print glGetInfoLogARB(self.progObj)
            self.error = True
            return              # Can't do anything good after an error.
        
        self._active = False

        # Optional, may be useful for debugging.
        glValidateProgramARB(self.progObj)
        status = glGetObjectParameterivARB(self.progObj, GL_VALIDATE_STATUS)
        if (not status):
            print "Shader program validation error"
            print glGetInfoLogARB(self.progObj)
            self.error = True
            return              # Can't do anything good after an error.

        return

    def createShader(self, shaderName, shaderType, shaderSrc):
        """
        Create, load, and compile a shader.
        """
        shader = glCreateShaderObjectARB(shaderType)
        glShaderSourceARB(shader, shaderSrc)
        try:
            glCompileShaderARB(shader)    # Checks status, raises error if bad.
        except:
            self.error = True
            types = {GL_VERTEX_SHADER:"vertex", GL_FRAGMENT_SHADER:"fragment"}
            print ("\n%s %s shader program compilation error" % 
                   (shaderName, types[shaderType]))
            print glGetInfoLogARB(shader)
            pass
        return shader

    def configShader(self, glpane):
        """
        Fill in uniform variables in the shader self, before using it to draw.

        @param glpane: The current glpane, containing NE1 graphics context
            information related to the drawing environment. This is used to
            find proper values for uniform variables we set in the shader.
        """
        # Can't do anything good after an error loading the shader programs.
        if self.error:
            return

        # Shader needs to be active to set uniform variables.
        wasActive = self._active
        if not wasActive:
            self.setActive(True)
            pass

        # Debugging control.
        if self._has_uniform_debug_code:
            glUniform1iARB(
                self._uniform("debug_code"),
                int(debug_pref("GLPane: shader debug graphics?",
                               Choice_boolean_False, prefs_key = True)))

        # Default override_opacity, multiplies the normal color alpha component.
        glUniform1fARB(self._uniform("override_opacity"), 1.0)

        # Russ 081208: Consider caching the glpane pointer.  GLPane_minimal
        # inherits from QGLWidget, which includes the OpenGL graphics context.
        # Currently we share 'display list context' and related information
        # across two kinds of OpenGL contexts, the main GLPane and the
        # ThumbViews used to select atom types, show clipboard parts, and maybe
        # more.  In the future it may be more complicated.  Then we may need to
        # be more specific about accounting for what's in particular contexts.

        # XXX Hook in full NE1 lighting scheme and material settings.
        # Material is [ambient, diffuse, specular, shininess].
        glUniform4fvARB(self._uniform("material"), 1, [0.3, 0.6, 0.5, 20.0])
        glUniform1iARB(self._uniform("perspective"), (1, 0)[glpane.ortho])

        # See GLPane._setup_projection().
        vdist = glpane.vdist
        # See GLPane_minimal.setDepthRange_Normal().
        near = vdist * (glpane.near + glpane.DEPTH_TWEAK)
        far = vdist * glpane.far
        glUniform4fvARB(self._uniform("clip"), 1,
                        [near, far, 0.5*(far + near), 1.0/(far - near)])
        # The effect of setDepthRange_Highlighting() is done as the shaders
        # set the gl_FragDepth during a highlighted drawing style.
        glUniform1fARB(self._uniform("DEPTH_TWEAK"), glpane.DEPTH_TWEAK)

        # Pixel width of window for halo drawing calculations.
        self.window_width = glpane.width

        # Single light for now.
        # XXX Get NE1 lighting environment state.
        glUniform4fvARB(self._uniform("intensity"), 1, [1.0, 0.0, 0.0, 0.0])
        light0 = A([-1.0, 1.0, 1.0])
        glUniform3fvARB(self._uniform("light0"), 1, light0)
        # Blinn shading highlight vector, halfway between the light and the eye.
        eye = A([0.0, 0.0, 1.0])
        halfway0 = norm((eye + light0) / 2.0)
        glUniform3fvARB(self._uniform("light0H"), 1, halfway0)

        if not wasActive:
            self.setActive(False)
        return

    def setupDraw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None, opacity = 1.0):
        """
        Set up for hover-highlighting and selection drawing styles.
        There is similar code in CSDL.draw(), which has similar arguments.

        XXX Does Solid and halo now, need to implement patterned drawing too.
        """
        # Shader needs to be active to set uniform variables.
        wasActive = self._active
        if not wasActive:
            self.setActive(True)
            pass

        patterned_highlighting = (False and # XXX
                                  patterning and
                                  isPatternedDrawing(highlight = highlighted))
           # note: patterned_highlighting variable is not yet used here [bruce 090304 comment]
           
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
            glUniform1fARB(self._uniform("ndc_halo_width"), ndc_halo_width)

        elif highlighted or selected:
            drawing_style = DS_NORMAL   # Non-halo highlighting or selection.
        glUniform1iARB(self._uniform("drawing_style"), drawing_style)

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
            glUniform4fvARB(self._uniform("override_color"), 1, override_color)
            pass

        if not wasActive:
            self.setActive(False)
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
        wasActive = self._active
        if not wasActive:
            self.setActive(True)
            pass

        glUniform1iARB(self._uniform("draw_for_mouseover"), int(tf))

        if not wasActive:
            self.setActive(False)
            pass
        return

    def _uniform(self, name): #bruce 090302 renamed from self.uniform()
        """
        Return location of a uniform (input) shader variable.
        If it's not found, return -1 and warn once per session for end users,
        or raise an AssertionError for developers.
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
        return glGetUniformivARB(self.progObj, self._uniform(name))

    def attributeLocation(self, name): #bruce 090302 renamed from self.attribute()
        """
        Return location of an attribute (per-vertex input) shader variable.
        If it's not found, return -1 and warn once per session for end users,
        or raise an AssertionError for developers.
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

    def setActive(self, on): #bruce 090302 renamed from self.use()
        """
        Activate or deactivate a shader.
        """
        if on:
            glUseProgramObjectARB(self.progObj)
        else:
            glUseProgramObjectARB(0)
            pass
        self._active = on
        return

    def get_TEXTURE_XFORMS(self):
        return TEXTURE_XFORMS

    def get_N_CONST_XFORMS(self):
        return N_CONST_XFORMS

    def setupTransforms(self, transforms):
        # note: this is only called from test_drawing.py (as of before 090302)
        """
        Fill a block of transforms.

        Depending on the setting of TEXTURE_XFORMS, the transforms are either in
        texture memory, or else in a uniform array of mat4s ("constant memory".)

        @param transforms: A list of transform matrices, where each transform is
        a flattened list (or Numpy array) of 16 numbers.
        """
        self.setActive(True)                # Must activate before setting uniforms.
        self.n_transforms = nTransforms = len(transforms)
        glUniform1iARB(self._uniform("n_transforms"), self.n_transforms)

        # The shader bypasses transform logic if n_transforms is 0.
        # (Then location coordinates are in global modeling coordinates.)
        if nTransforms > 0:
            if not TEXTURE_XFORMS:
                # Load into constant memory.  The GL_EXT_bindable_uniform
                # extension supports sharing this array of mat4s through a VBO.
                # XXX Need to bank-switch this data if more than N_CONST_XFORMS.
                C_transforms = numpy.array(transforms, dtype=numpy.float32)
                glUniformMatrix4fvARB(self._uniform("transforms"),
                                      # Don't over-run the array size.
                                      min(len(transforms), N_CONST_XFORMS),
                                      GL_TRUE, # Transpose.
                                      C_transforms)
            else: # TEXTURE_XFORMS
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
        self.setActive(False)                # Deactivate again.
        return

    pass # End of class GLShaderObject.

# ==

class GLSphereShaderObject(GLShaderObject):
    """
    An analytic sphere shader.

    This raster-converts analytic spheres, defined by a center point and radius.
    (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
    send rays through the scene for reflection/refraction, nor toward the lights
    to compute shadows.)
    """
    def __init__(self):
        super(GLSphereShaderObject, self).__init__(
            "Sphere", sphereVertSrc, sphereFragSrc)
        return
    pass # End of class GLSphereShaderObject.

class GLCylinderShaderObject(GLShaderObject):
    """
    An analytic cylinder shader.

    This shader raster-converts analytic tapered cylinders, defined by two
    end-points determining an axis line-segment, and two radii at the
    end-points.  A constant-radius cylinder is tapered by perspective anyway, so
    the same shader does cones as well as cylinders.
    
    The rendered cylinders are smooth, with no polygon facets.  Exact shading, Z
    depth, and normals are calculated in parallel in the GPU for each pixel.

    (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
    send rays through the scene for reflection/refraction, nor toward the lights
    to compute shadows.)
    """
    _has_uniform_debug_code = True
    def __init__(self):
        super(GLCylinderShaderObject, self).__init__(
            "Cylinder", cylinderVertSrc, cylinderFragSrc)
        return
    pass # End of class GLCylinderShaderObject.
