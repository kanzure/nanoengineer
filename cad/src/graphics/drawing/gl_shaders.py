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
"""

# Whether to use texture memory for transforms, or a uniform array of mat4s.
texture_xforms = True # False
# Otherwise, use a fixed-sized block of uniform memory for transforms.
N_CONST_XFORMS = 250  # (Gets CPU bound at 275.  Dunno why.)

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

from geometry.VQT import A
import utilities.EndUser as EndUser

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.gl_buffers import GLBufferObject

import numpy

from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
#from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_RGBA32F_ARB
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TEXTURE_2D
#from OpenGL.GL import GL_TEXTURE_MAG_FILTER
#from OpenGL.GL import GL_TEXTURE_MIN_FILTER
#from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_INT
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import GL_VALIDATE_STATUS

#from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindTexture
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetTexImage
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexSubImage2D
from OpenGL.GL import glVertexPointer

from OpenGL.GL.ARB.shader_objects import glAttachObjectARB
from OpenGL.GL.ARB.shader_objects import glCompileShaderARB
from OpenGL.GL.ARB.shader_objects import glCreateProgramObjectARB
from OpenGL.GL.ARB.shader_objects import glCreateShaderObjectARB
from OpenGL.GL.ARB.shader_objects import glGetInfoLogARB
from OpenGL.GL.ARB.shader_objects import glGetObjectParameterivARB
from OpenGL.GL.ARB.shader_objects import glGetUniformLocationARB
from OpenGL.GL.ARB.shader_objects import glGetUniformivARB
from OpenGL.GL.ARB.shader_objects import glLinkProgramARB
from OpenGL.GL.ARB.shader_objects import glShaderSourceARB
from OpenGL.GL.ARB.shader_objects import glUniform1iARB
from OpenGL.GL.ARB.shader_objects import glUniform3fvARB
from OpenGL.GL.ARB.shader_objects import glUniform4fvARB
from OpenGL.GL.ARB.shader_objects import glUniformMatrix4fvARB
from OpenGL.GL.ARB.shader_objects import glUseProgramObjectARB
from OpenGL.GL.ARB.shader_objects import glValidateProgramARB

from OpenGL.GL.ARB.vertex_program import glDisableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glEnableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glVertexAttrib1fARB
from OpenGL.GL.ARB.vertex_program import glVertexAttrib3fARB
from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

from OpenGL.GL.ARB.vertex_shader import glGetAttribLocationARB

_warnedVars = {}

class GLSphereShaderObject(object):
    """
    An analytic sphere shader.

    This raster-converts analytic spheres, defined by a center point and radius.
    (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
    send rays through the scene for reflection/refraction, nor toward the lights
    to compute shadows.)
    """

    def __init__(self):
        # Version statement has to come first in GLSL source.
        prefix = """// requires GLSL version 1.10
                    #version 110
                    """
        # Insert preprocessor constants.
        if not texture_xforms:
            prefix += "#define N_CONST_XFORMS %d\n" % N_CONST_XFORMS
            pass
        # Pass the source strings to the shader compiler.
        self.sphereVerts = self.createShader(GL_VERTEX_SHADER,
                                             prefix + sphereVertSrc)
        self.sphereFrags = self.createShader(GL_FRAGMENT_SHADER, sphereFragSrc)
        # Link the compiled shaders into a shader program.
        self.progObj = glCreateProgramObjectARB()
        glAttachObjectARB(self.progObj, self.sphereVerts)
        glAttachObjectARB(self.progObj, self.sphereFrags)
        glLinkProgramARB(self.progObj)  # Checks status, raises error if bad.
        self.used = False

        # Optional, may be useful for debugging.
        glValidateProgramARB(self.progObj)
        status = glGetObjectParameterivARB(self.progObj, GL_VALIDATE_STATUS)
        if (not status):
            from OpenGL import error
            raise error.GLError("Shader program validation error",
                                description = glGetInfoLogARB(self.progObj))

        # The batched sphere shader has per-vertex attribute inputs.  To avoid
        # alias collisions with built-in attributes, let the linker assign
        # attribute numbers rather than specifying with glBindAttribLocationARB.
        self.center_pt_attrib = glGetAttribLocationARB(
            self.progObj, "center_pt")      # vec3.
        self.radius_attrib = glGetAttribLocationARB(
            self.progObj, "radius")         # float.
        self.color_attrib = glGetAttribLocationARB( # XXX Use gl_Color.
            self.progObj, "color")          # vec3.
        # Allow putting transforms into texture or uniform (constant) memory
        # slots, indexed by a transform ID associated with each vertex.
        # (Attribute variables are not allowed to be int or bool.)
        self.transform_id_attrib = glGetAttribLocationARB(
            self.progObj, "transform_id")   # float.
        
        return

    def createShader(shaderType, shaderSrc):
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
        return shader

    def configShader(self, glpane):
        """
        Fill in uniform variables in the shader before using to draw.
        """
        # Shader needs to be active to set uniform variables.
        wasActive = self.used
        if not wasActive:
            self.use(True)

        # XXX Hook in full NE1 lighting scheme and material settings.
        # Material is [ambient, diffuse, specular, shininess].
        glUniform4fvARB(self.uniform("material"), 1, [0.1, 0.5, 0.5, 35.0])
        glUniform1iARB(self.uniform("perspective"), (1, 0)[glpane.ortho])

        # XXX Try built-in "uniform gl_DepthRangeParameters gl_DepthRange;"
        vdist = glpane.vdist            # See GLPane._setup_projection().
        # See GLPane_minimal.setDepthRange_Normal().
        from graphics.widgets.GLPane_minimal import DEPTH_TWEAK 
        near = vdist * (glpane.near + DEPTH_TWEAK)
        far = vdist * glpane.far
        glUniform4fvARB(self.uniform("clip"), 1,
                        [near, far, 0.5*(far + near), 1.0/(far - near)])

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

    pass # End of class GLShaderObject.

class GLSphereBuffer:
    """
    Encapsulate VBO/IBO handles for a batch of spheres.

    Sphere centers must be an array of VQT points.  A single radius may be given
    for the whole batch of spheres, or a list of per-sphere radii.

    An optional array of colors (as [R, G, B] lists) may be buffered per-sphere,
    or a single unstored color value may be bound at drawing time as a constant
    OpenGL vertexAttibute value.

    Draws a bounding-box of quads to a custom sphere shader for each sphere.
    Vertex and index VBO/IBOs are filled using copies of shaderCubeVerts and
    shaderCubeIndices from drawing_globals. Vertex attribute VBOs contain the
    sphere center points, and optional per-sphere radius and color attributes.
    """
    def __init__(self, centers, radii, colors = None, transform_ids = None):
        """
        centers is a list of points.
        radii is a single number, or a list of numbers.
        colors (optional) is a list of [R, G, B] lists.
        transforms (optional) is a list of transform slot IDs.
        The lengths of centers, radii, colors and transformID lists must match.
        """
        self.nSpheres = len(centers)
        self.radArray = type(radii) == type([])
        if self.radArray:
            assert len(radii) == self.nSpheres
            radiusValues = radii
        else:
            # Remember a single radius attribute to bind for drawing.
            self.radius = radii
            radiusValues = len(centers) * [radii]

        cubeVerts = drawing_globals.shaderCubeVerts
        self.nCubeVerts = len(cubeVerts)

        # For indexed glDrawElements, indices are a list of faces,
        # each of which is a list of vertex subscripts.
        # The vertex shader only sees the vertices once, even if it
        # is indexed multiple times.
        cubeIndices = drawing_globals.shaderCubeIndices
        self.nCubeIndices = len(cubeIndices) * len(cubeIndices[0])
        indexOffset = 0
        self.ibo_indices = []
        # Cache the python arrays for batched updates.
        self.Py_verts = []
        self.Py_centers = []
        self.Py_radii = []
        self.Py_colors = []
        self.Py_transform_ids = []

        # Cached info for blocks of transforms.
        self.n_transforms = None        # Size of the block.
        self.transform_memory = None    # Texture memory handle.

        # Collect transformed bounding box vertices, offset indices, and
        # per-vertex radius attributes for buffering.
        for (spherePos, radius) in zip(centers, radiusValues):

            # 8 verts/cube, indexed by 6 faces w/ 4 quad vertex indices.
            # (Maybe this could be done faster with OpenGL feedback mode...)
            self.Py_verts += [spherePos + radius * A(vert)
                          for vert in cubeVerts]

            # Offset the indices to point to the right transformed vertices.
            for face in cubeIndices:
                self.ibo_indices += [idx + indexOffset for idx in face]
            indexOffset += self.nCubeVerts

            # Replicate centers and radii for the 8 verts per cube.
            self.Py_centers += (self.nCubeVerts *
                                 [spherePos[0], spherePos[1], spherePos[2]])
            if self.radArray:
                self.Py_radii += self.nCubeVerts * [radius]
                pass
            continue
        assert not self.radArray or len(self.Py_radii) == len(self.Py_verts)

        # Collect optional replicated per-vertex color values.
        self.colorArray = colors is not None
        if self.colorArray:
            assert len(colors) == self.nSpheres
            for color in colors:        # [R, G, B] lists.
                self.Py_colors += self.nCubeVerts * color
                continue
            assert len(self.Py_colors) == 3 * len(self.Py_verts)
            pass

        # Collect optional replicated per-vertex transform_id values.
        self.transform_id_Array = transform_ids is not None
        if self.transform_id_Array:
            assert len(transform_ids) == self.nSpheres
            for transform_id in transform_ids: # Integers.
                self.Py_transform_ids += self.nCubeVerts * [transform_id]
                continue
            assert len(self.Py_transform_ids) == len(self.Py_verts)
            pass

        # Push the values into IBOs/VBOs in the graphics card memory.
        self.C_indices = numpy.array(self.ibo_indices, dtype=numpy.uint32)
        self.verts_ibo = GLBufferObject(
            GL_ELEMENT_ARRAY_BUFFER_ARB, self.C_indices, GL_STATIC_DRAW)
        self.verts_ibo.unbind()

        self.C_verts = numpy.array(self.Py_verts, dtype=numpy.float32)
        self.verts_vbo = GLBufferObject(
            GL_ARRAY_BUFFER_ARB, self.C_verts, GL_STATIC_DRAW)
        self.verts_vbo.unbind()

        self.C_centers = numpy.array(self.Py_centers, dtype=numpy.float32)
        self.centers_vbo = GLBufferObject(
            GL_ARRAY_BUFFER_ARB, self.C_centers, GL_STATIC_DRAW)
        self.centers_vbo.unbind()

        if self.radArray:
            self.C_radii = numpy.array(self.Py_radii, dtype=numpy.float32)
            self.radii_vbo = GLBufferObject(
                GL_ARRAY_BUFFER_ARB, self.C_radii, GL_STATIC_DRAW)
            self.radii_vbo.unbind()
            pass

        if self.colorArray:
            self.C_colors = numpy.array(self.Py_colors, dtype=numpy.float32)
            self.colors_vbo = GLBufferObject(
                GL_ARRAY_BUFFER_ARB, self.C_colors, GL_STATIC_DRAW)
            self.colors_vbo.unbind()
            pass

        if self.transform_id_Array:
            # Warning: if you make transform_id an int rather than a float, it
            # slows down the vertex shader at least 10x!  That means explicitly
            # converting the value in the shader when needed: int(transform_id).
            self.C_transform_ids = numpy.array(self.Py_transform_ids,
                                               dtype=numpy.float32)
            self.transform_ids_vbo = GLBufferObject(
                GL_ARRAY_BUFFER_ARB, self.C_transform_ids, GL_STATIC_DRAW)
            self.transform_ids_vbo.unbind()
            pass

        return

    def setupTransforms(self, transforms):
        """
        Fill a block of transforms.

        Depending on the setting of texture_xforms, the transforms are either in
        texture memory, or else in a uniform array of mat4s ("constant memory".)

        @param transforms: A list of transform matrices, where each transform is
        a flattened list (or Numpy array) of 16 numbers.
        """
        shader = drawing_globals.sphereShader
        shader.use(True)                # Must activate before setting uniforms.
        self.n_transforms = nTransforms = len(transforms)
        glUniform1iARB(shader.uniform("n_transforms"), self.n_transforms)
        if texture_xforms:
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
        else:
            C_transforms = numpy.array(transforms, dtype=numpy.float32)
            # Load into constant memory.  The GL_EXT_bindable_uniform extension
            # supports sharing this array of mat4s through a VBO.
            # XXX Need to bank-switch this data if more than N_CONST_XFORMS.
            glUniformMatrix4fvARB(shader.uniform("transforms"),
                                  # Don't over-run the array size.
                                  min(len(transforms), N_CONST_XFORMS),
                                  GL_TRUE, # Transpose.
                                  C_transforms)
            pass
        shader.use(False)                # Deactivate again.
        return

    def updateRadii(self, offset, radii, send = True):
        """
        Replace a sequence of radii.

        Values are sent to graphics card RAM by default.
        Defer sending with send = False for many simultaneous updates.
        """
        if self.radArray:
            # Replicate radii for the 8 verts per cube.
            values = []
            for radius in radii:
                values += self.nCubeVerts * [radius]
                pass
            repOff1 = offset * self.nCubeVerts
            repOff2 = (offset+len(radii)) * self.nCubeVerts
            assert len(values) == repOff2 - repOff1
            self.Py_radii[repOff1:repOff2] = values

            # It may be faster to send one subrange, but not *many* subranges.
            if send:
                self.sendRadii()
            pass
        return
        
    def sendRadii(self):
        """
        Batched update: send the python array via C to the graphic card.
        """
        if self.radArray:
            # A possible optimization would be to remember what part is changed.
            self.C_radii = numpy.array(self.Py_radii, dtype=numpy.float32)
            self.radii_vbo.updateAll(self.C_radii)
            pass
        return
        
    def draw(self, radius = None, color = None, transform_id = None):
        """
        Draw the buffered geometry, binding vertex attribute values for the
        sphere shaders.

        Optional radius, color and transform_id args over-ride array values.
        """
        shader = drawing_globals.sphereShader
        shader.use(True)            # Turn on the sphere shader.

        glEnableClientState(GL_VERTEX_ARRAY)
        self.verts_vbo.bind()       # Vertex coordinate data vbo.
        glVertexPointer(3, GL_FLOAT, 0, None)

        center_pt_attrib = shader.center_pt_attrib
        glEnableVertexAttribArrayARB(center_pt_attrib)
        self.centers_vbo.bind()    # Sphere center_ pt per-vertex attribute vbo.
        glVertexAttribPointerARB(center_pt_attrib, 3, GL_FLOAT, 0, 0, None)

        radius_attrib = shader.radius_attrib
        if radius is not None:
            # Single radius for the whole batch.
            glVertexAttrib1fARB(radius_attrib, radius)
        elif self.radArray:
            # Per-vertex radii.
            glEnableVertexAttribArrayARB(radius_attrib)
            self.radii_vbo.bind()   # Sphere radius per-vertex attribute vbo.
            glVertexAttribPointerARB(radius_attrib, 1, GL_FLOAT, 0, 0, None)
            pass
        else:  # Default radius from constructor.
            glVertexAttrib1fARB(radius_attrib, self.radius)

        color_attrib = shader.color_attrib
        if color is not None:
            # Single color for the whole batch.
            glVertexAttrib3fARB(color_attrib, color[0], color[1], color[2])
        elif self.colorArray:
            glEnableVertexAttribArrayARB(color_attrib)
            self.colors_vbo.bind()  # Sphere color per-vertex attribute vbo.
            glVertexAttribPointerARB(color_attrib, 3, GL_FLOAT, 0, 0, None)
            pass
        else:  # Default color (bright red.)
            glVertexAttrib3fARB(color_attrib, [1.0, 0.0, 0.0])

        transform_id_attrib = shader.transform_id_attrib
        if transform_id is not None:
            # Single transform ID for the whole batch.
            glVertexAttrib1fARB(transform_id_attrib, transform_id)
        elif self.transform_id_Array:
            # Sphere transform_id per-vertex attribute vbo.
            glEnableVertexAttribArrayARB(transform_id_attrib)
            self.transform_ids_vbo.bind()
            glVertexAttribPointerARB(
                transform_id_attrib, 1, GL_FLOAT, 0, 0, None)
            pass
        else:  # Single transform_id for the whole batch, default to 0.
            glVertexAttrib1fARB(transform_id_attrib, 0)
            pass
        if texture_xforms:
            # Activate a texture unit for transforms.
            ## XXX Not necessary for custom shader programs.
            ##glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.transform_memory)

            # Set the sampler to the handle for the active texture image (0).
            ## XXX Not needed if only one texture is being used?
            ##glActiveTexture(GL_TEXTURE0)
            ##glUniform1iARB(shader.uniform("transforms"), 0)
            pass        

        glDisable(GL_CULL_FACE)

        self.verts_ibo.bind()       # Vertex index data ibo.
        glDrawElements(GL_QUADS, self.nCubeIndices * self.nSpheres,
                       GL_UNSIGNED_INT, None)

        shader.use(False)           # Turn off the sphere shader.
        glEnable(GL_CULL_FACE)

        self.verts_ibo.unbind()   # Deactivate ibo: GL_ELEMENT_ARRAY_BUFFER_ARB.
        self.verts_vbo.unbind()     # Deactivate all vbo's: GL_ARRAY_BUFFER_ARB.

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableVertexAttribArrayARB(center_pt_attrib)
        if self.radArray:
            glDisableVertexAttribArrayARB(radius_attrib)
            pass
        if self.colorArray:
            glDisableVertexAttribArrayARB(color_attrib)
            pass
        if self.transform_id_Array:
            glDisableVertexAttribArrayARB(transform_id_attrib)
            pass
        return

    pass # End of class GLSphereBuffer.


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
// (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
// send rays through the scene for reflection/refraction, nor toward the lights
// to compute shadows.)
// 
// How it works:
// 
// A bounding volume of OpenGL faces is drawn around the sphere.  A center point
// and radius are also provided as vertex attributes.  It doesn't matter what
// the shape of the bounding volume is, as long as it covers at least the pixels
// where the sphere is to be rendered.  Clipping and lighting settings are also
// provided to the fragment (pixel) shader.
// 
// The eye position, and ray vectors pointing from the eye to the transformed
// vertex and the center of the sphere, are output from the vertex shader to the
// fragment shader.  This is handled differently for orthographic and
// perspective projections, but it's all in pre-projection gl_ModelViewMatrix
// space.
// 
// In between the vertex shader and the fragment shader, the transformed vertex
// vector coords get interpolated, so it winds up being a transformed ray from
// the eye point to the pixel on the bounding volume surface.
// 
// In the fragment shader, the sphere radius comparison is done using these
// points and vectors.  That is, if the pixel is within the sphere radius of the
// sphere center point, a depth and normal are calculated as a function of the
// distance from the center.

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int perspective;        // perspective=1 orthographic=0

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
attribute vec3 center_pt;       // Per-vertex sphere center point.
// The following may be set to constants, when no arrays are provided.
attribute float radius;         // Per-vertex sphere radius.
attribute vec3 color;           // Per-vertex sphere color.
attribute float transform_id;   // Ignored if zero.  (Attribs can't be ints.)

// Varying outputs, through the pipeline to the fragment (pixel) shader.
varying vec3 var_basecolor;     // Vertex color, interpolated to pixels.
varying vec3 var_vert;          // Viewing direction vector.
varying vec3 var_center;        // Transformed sphere var_center.
varying vec3 var_eye;           // Var_eye point (different for perspective.)
varying float var_radius_squared;  // Transformed sphere radius, squared.

void main(void) {
  // Fragment (pixel) color will be interpolated from the vertex colors.
  var_basecolor = color;

  vec4 vertex = gl_Vertex;
  vec4 center = vec4(center_pt, 1.0);
  mat4 xform;
  if (n_transforms > 0) {
    // Apply a transform, indexed by a transform slot ID vertex attribute.

#ifdef N_CONST_XFORMS 
    // Get transforms from a fixed-sized block of uniform (constant)  memory.
    // The GL_EXT_bindable_uniform extension allows sharing this through a VBO.
    vertex = transforms[int(transform_id)] * vertex;
    center = transforms[int(transform_id)] * center;

#else  // texture_xforms.
    // Assemble the 4x4 matrix from a column of vec4s stored in texture memory.
    // Map the 4 rows and N columns onto the (0...1, 0...1) texture coord range.
    // The first texture coordinate goes across the width of N matrices.
    float mat = transform_id / float(n_transforms - 1);  // (0...N-1)=>(0...1) .
    // The second tex coord goes down the height of four vec4s for the matrix.
# if 0 // 1   /// Never check in a 1 value.
    xform = mat4(1.0); /// Testing, override texture xform with identity matrix.
# else
    xform = mat4(texture2D(transforms, vec2(0.0/3.0, mat)),
                 texture2D(transforms, vec2(1.0/3.0, mat)), 
                 texture2D(transforms, vec2(2.0/3.0, mat)), 
                 texture2D(transforms, vec2(3.0/3.0, mat)));
# endif
    vertex = xform * vertex;
    center = xform * center;
#endif // texture_xforms.

  }

#if 0 // 1   /// Never check in a 1 value.
  // Debugging display: set the colors of a 16x16 sphere array.
  // test_drawing.py sets the transform_id's.  Assume here that
  // nSpheres = transformChunkLength = 16, so each column is one transform.

  // The center_pt coord attrib gives the subscripts of the sphere in the array.
  int offset = int(n_transforms)/2; // Undo the array centering from data setup.
  int col = int(center_pt.x) + offset;  // X picks the columns.
  int row = int(center_pt.y) + offset;  // Y picks the rows.
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
    // The test identity matrix has 1's in rows 0, 5, 10, and 15, as it should.
    data = xform[row/4][row - (row/4)*4];  // % is unimplimented.
  else  // Display transform IDs.
    data = transform_id / float(n_transforms);

  // Default - Column-major indexing: red is column index, green is row index.
  var_basecolor = vec3(float(col)/float(n_transforms),
                       float(row)/float(n_transforms),
                       data);
  ///if (data == 0.0) var_basecolor = vec3(1.0, 1.0, 1.0);  // Zeros in white.
  if (data > 0.0) var_basecolor = vec3(data, data, data);  // Fractions in gray.
  // Matrix labels (1 + xform/100) in blue.
  if (data > 1.0) var_basecolor = vec3(0.0, 0.0, (data - 1.0) * 8.0);
    
  /// When debugging, don't use the xform'ed vertex, which could be all zeros.
  // Transform the vertex through the modeling and viewing matrix to 'eye' space.
  vec4 eye_vert = gl_ModelViewMatrix * gl_Vertex; /// vertex;
  gl_ClipVertex = eye_vert;     // For user clipping planes.
#else

  // Transform the vertex through the modeling and viewing matrix to 'eye' space.
  vec4 eye_vert = gl_ModelViewMatrix * vertex;
  gl_ClipVertex = eye_vert;     // For user clipping planes.
#endif

  // Center point in eye space.
  vec4 eye_center = gl_ModelViewMatrix * center;
  var_center = vec3(eye_center) / eye_center.w;

  // Scaled radius in eye space.  (Assume uniform scale on all axes.)
  vec4 eye_radius = gl_ModelViewMatrix * vec4(radius, 0, 0, 0);
  var_radius_squared = length(eye_radius);
  var_radius_squared *= var_radius_squared; // So we don't need to do square roots.

  // (Perspective is a uniform, so all shader processors take the same branch.)
  if (perspective == 1) {
    // With perspective, look from the origin, toward the vertex (pixel) points.
    var_eye = vec3(0,0,0);
    var_vert = normalize(vec3(eye_vert) / eye_vert.w);
  } else {
    // Without perspective, look from 2D pixel position, in the -Z direction.
    var_eye = vec3((eye_vert.xy / eye_vert.w), 0.0);  
    var_vert = vec3(0.0, 0.0, -1.0);
  }

  // Transform to screen coords.
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
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
varying vec3 var_eye;
varying vec3 var_vert;
varying vec3 var_center;
varying float var_radius_squared;
varying vec3 var_basecolor;

uniform vec4 material; // Properties: [ambient, diffuse, specular, shininess].

void main(void) {
  // Vertex direction vectors were interpolated into pixel sample vectors.
  vec3 pixel_vec = normalize(var_vert);  // Interpolation denormalizes vectors.
  vec3 center_vec = var_center - var_eye;
   
  // Length of the projection of the center_vec onto the pixel_vec.
  float proj_len = dot(pixel_vec, center_vec);
  float center_vec_len_squared = dot(center_vec, center_vec);
  // Compare intersection distance (squared) to radius and center_vec length.
  float disc = proj_len*proj_len + var_radius_squared - center_vec_len_squared;
  if (disc <= 0.0)
    discard;   // Pixel sample missed the sphere.

  // Depth of nearest intersection of pixel sample vector with the sphere.
  float tnear = proj_len - sqrt(disc);
  if (tnear < 0.0)
    discard;   // Intersection is behind the view point.

  // Intersection point and normal of the pixel sample vector with the sphere.
  vec3 sample = var_eye + tnear * pixel_vec;
  vec3 normal = normalize(sample - var_center);

  // Distance to the sphere sample is the fragment depth, transformed into
  // normalized device coordinates.  (Inverse of clip depth to avoid divide.)
  if (perspective == 1) {
    // perspective: 0.5 + (mid + (far * near / sample.z)) / depth
    gl_FragDepth = 0.5 + (clip[2] + (clip[1] * clip[0] / sample.z)) * clip[3];
  } else {
    // ortho: 0.5 + (-middle - sample.z) / depth
    gl_FragDepth = 0.5 + (-clip[2] - sample.z) * clip[3];
  }

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

  float ambient = material[0];
  gl_FragColor = vec4(var_basecolor * vec3(diffuse) + vec3(ambient + specular),
                      1.0);
}
"""
