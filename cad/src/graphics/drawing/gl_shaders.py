# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
gl_shaders.py - OpenGL shader objects.

    Useful man pages for OpenGL 2.1 are at:
    http://www.opengl.org/sdk/docs/man

    PyOpenGL versions are at:
    http://pyopengl.sourceforge.net/ctypes/pydoc/OpenGL.html

@author: Russ Fish
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
from geometry.VQT import V, Q, A, norm, vlen, angleBetween
import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_buffers import GLBufferObject

import numpy

from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_COMPILE_STATUS
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_UNSIGNED_INT
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import GL_VALIDATE_STATUS

from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glVertexPointer

from OpenGL.GL.ARB.shader_objects import glAttachObjectARB
from OpenGL.GL.ARB.shader_objects import glCompileShaderARB
from OpenGL.GL.ARB.shader_objects import glCreateProgramObjectARB
from OpenGL.GL.ARB.shader_objects import glCreateShaderObjectARB
from OpenGL.GL.ARB.shader_objects import glGetInfoLogARB
from OpenGL.GL.ARB.shader_objects import glGetObjectParameterivARB
from OpenGL.GL.ARB.shader_objects import glGetUniformLocationARB
from OpenGL.GL.ARB.shader_objects import glLinkProgramARB
from OpenGL.GL.ARB.shader_objects import glShaderSourceARB
from OpenGL.GL.ARB.shader_objects import glUniform1fARB
from OpenGL.GL.ARB.shader_objects import glUniform1iARB
from OpenGL.GL.ARB.shader_objects import glUniform3fvARB
from OpenGL.GL.ARB.shader_objects import glUniform4fvARB
from OpenGL.GL.ARB.shader_objects import glUseProgramObjectARB
from OpenGL.GL.ARB.shader_objects import glValidateProgramARB

from OpenGL.GL.ARB.vertex_program import glDisableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glEnableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

from OpenGL.GL.ARB.vertex_shader  import glBindAttribLocationARB

class GLSphereShaderObject(object):
    """
    Create a sphere shader.
    """

    def __init__(self):
        # The batched sphere shader has per-vertex attribute inputs.
        self.center_pt_attrib = 1       # GLSL: attribute vec3 center_pt;
        self.radius_attrib = 2          # GLSL: attribute float radius;
        self.color_attrib = 3           # GLSL: attribute vec3 color;
        
        self.sphereVerts = self.createShader(GL_VERTEX_SHADER, sphereVertSrc)
        self.sphereFrags = self.createShader(GL_FRAGMENT_SHADER, sphereFragSrc)
        self.progObj = glCreateProgramObjectARB()

        glBindAttribLocationARB(self.progObj, self.center_pt_attrib, "center_pt")
        glBindAttribLocationARB(self.progObj, self.radius_attrib, "radius")
        glBindAttribLocationARB(self.progObj, self.color_attrib, "color")

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
        return

    def createShader(self, shaderType, shaderSrc):
        """
        Create, load, and compile a shader.
        """
        shader = glCreateShaderObjectARB(shaderType);
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
        Fill in uniform variables in the shader.
        """
        # Shader needs to be active to set uniform variables.
        wasActive = self.used
        if not wasActive:
            self.use(True)

        # XXX Hook in full NE1 lighting scheme and material settings.
        # Material is [ambient, diffuse, specular, shininess].
        glUniform4fvARB(self.uniform("material"), 1, [0.1, 0.5, 0.5, 35.0])
        glUniform1iARB(self.uniform("perspective"), (1, 0)[glpane.ortho])
        vdist = glpane.vdist                    # See GLPane._setup_projection().
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
        """
        return glGetUniformLocationARB(self.progObj, name)

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
    def __init__(self, centers, radii, colors = None):
        """
        centers is a list of points.
        radii is a single number, or a list of numbers.
        colors (optional) is a list of [R, G, B] lists.
        The lengths of centers, radii, and colors lists must match.
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
        
    def draw(self, color = None):
        """
        Draw the buffered geometry, binding vertex attribute values for the
        sphere shaders.
        """
        shader = drawing_globals.sphereShader

        glEnableClientState(GL_VERTEX_ARRAY)
        self.verts_vbo.bind()       # Vertex coordinate data vbo.
        glVertexPointer(3, GL_FLOAT, 0, None)

        center_pt_attrib = shader.center_pt_attrib
        glEnableVertexAttribArrayARB(center_pt_attrib)
        self.centers_vbo.bind()    # Sphere center_ pt per-vertex attribute vbo.
        glVertexAttribPointerARB(center_pt_attrib, 3, GL_FLOAT, 0, 0, None)

        radius_attrib = shader.radius_attrib
        if not self.radArray:
            # Single radius for the whole batch.
            glVertexAttrib1f(radius_attrib, self.radius)
        else:
            # Per-vertex radii.
            glEnableVertexAttribArrayARB(radius_attrib)
            self.radii_vbo.bind()   # Sphere radius per-vertex attribute vbo.
            glVertexAttribPointerARB(radius_attrib, 1, GL_FLOAT, 0, 0, None)
            pass

        color_attrib = shader.color_attrib
        if not self.colorArray:
            # Single color for the whole batch.
            glVertexAttrib3f(color_attrib, color)
        else:
            glEnableVertexAttribArrayARB(color_attrib)
            self.colors_vbo.bind()  # Sphere color per-vertex attribute vbo.
            glVertexAttribPointerARB(color_attrib, 3, GL_FLOAT, 0, 0, None)
            pass

        shader.use(True)            # Turn on the sphere shader.
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
        return

    pass # End of class GLSphereBuffer.

# Sphere shaders.
sphereVertSrc = """
// Vertex shader program for sphere primitives.
//
// This raster-converts analytic spheres, defined by a center point and radius.
// (Some people call that a ray-tracer, but unlike a real ray-tracer it can't
// send rays through the scene for reflection/refraction, nor toward the lights
// to compute shadows.)

// requires GLSL version 1.10
#version 110

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int perspective;        // perspective=1 orthographic=0

// Attribute variables, which are bound to VBO arrays for the vertex coming in.
attribute vec3 center_pt;       // Per-vertex sphere center point.
// The following may be set to constants, when no arrays are provided.
attribute float radius;         // Per-vertex sphere radius.
attribute vec3 color;           // Per-vertex sphere color.

// Varying outputs, through the pipeline to the fragment (pixel) shader.
varying vec3 var_basecolor;     // Vertex color, interpolated to pixels.
varying vec3 var_vert;          // Viewing direction vector.
varying vec3 var_center;        // Transformed sphere var_center.
varying vec3 var_eye;           // Var_eye point (different for perspective.)
varying float var_radius_squared;  // Transformed sphere radius, squared.

void main(void) {
  // Transform through the modeling and viewing matrix to "eye" space.
  vec4 eye_vert = gl_ModelViewMatrix * gl_Vertex;
  gl_ClipVertex = eye_vert;     // For user clipping planes.

  // Fragment (pixel) color will be interpolated from the vertex colors.
  var_basecolor = color;

  // Center point in eye space.
  vec4 eye_center = gl_ModelViewMatrix * vec4(center_pt, 1.0);
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
