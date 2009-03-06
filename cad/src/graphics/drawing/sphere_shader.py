# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
sphere_shader.py - Sphere shader GLSL source code.

@author: Russ Fish
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Russ 090106: Chopped the GLSL source string blocks out of gl_shaders.py .
"""

# See the docstring at the beginning of gl_shaders.py for GLSL references.

# ================================================================
# == Description: GLSL shader program for sphere primitives,
# == including optional halos.
# 
# This raster-converts analytic spheres, defined by a center point and radius.
# The rendered spheres are smooth, with no polygon facets.  Exact shading, Z
# depth, and normals are calculated in parallel in the GPU for each pixel.
# 
# It sends an eye-space ray from the view point to the sphere at each pixel.
# Some people call that a ray-tracer, but unlike a real ray-tracer it cannot
# send more rays through the scene to intersect other geometry for
# reflection/refraction calculations, nor toward the lights for shadows.
# 
# 
# == How it works:
# 
# A bounding volume of faces may be drawn around the sphere in OpenGL, or
# alternately a 'billboard' face may be drawn in front of the the sphere.  A
# center point and radius are also provided as vertex attributes.  The face(s)
# must cover at least the pixels where the sphere is to be rendered.  Clipping
# and lighting settings are also provided to the fragment (pixel) shader.
# 
# The view point, transformed sphere center point and radius, and a ray vector
# pointing from the view point to the transformed vertex, are output from the
# vertex shader to the fragment shader.  This is handled differently for
# orthographic and perspective projections, but it is all in pre-projection
# gl_ModelViewMatrix 'eye space', with the origin at the eye (camera) location
# and XY coordinates parallel to the screen (window) XY.
# 
# When perspective is on, a rotation is done as well, to keep a billboard
# drawing pattern oriented directly toward the viewpoint.
# 
# A 'halo' radius is also passed to the fragment shader, for highlighting
# selected spheres with a flat disk when the halo drawing-style is selected.
# 
# In between the vertex shader and the fragment shader, the transformed vertex
# ray vector coords get interpolated, so it winds up being a transformed ray
# from the view point, through the pixel on the bounding volume surface.
# 
# The fragment (pixel) shader is called after raster conversion of primitives,
# driven by the fixed-function OpenGL pipeline.  The sphere center and radius
# are passed from the vertex shader as "varying" quantities.  It computes a
# normal-sample of an analytic sphere for shading, or discards the pixel if it
# is outside the sphere.
# 
# In the fragment shader, the sphere radius-hit comparison is done using the
# interpolated points and vectors.  That is, if the ray from the eye through the
# pixel center passes within the sphere radius of the sphere center point, a
# depth and normal on the sphere surface are calculated as a function of the
# distance from the center.  If the ray is outside the sphere radius, it may
# still be within the halo disk radius surrounding the sphere.

# <line 0>
# ================================================================
# Note: if TEXTURE_XFORMS is off, a #define N_CONST_XFORMS array dimension is
# prepended to the following.  The #version statement must precede it.
sphereVertSrc = """
// Vertex shader program for sphere primitives.
// 
// See the description at the beginning of this file.

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int draw_for_mouseover; // 0:use normal color, 1:glname_color.
uniform int drawing_style;      // 0:normal, 1:override_color, 2:pattern, 3:halo
const int DS_NORMAL = 0;
const int DS_OVERRIDE_COLOR = 1;
const int DS_PATTERN = 2;
const int DS_HALO = 3;
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
attribute float transform_id;   // Ignored if -1.  (Attribs cannot be ints.)
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
  float radius = center_rad.w;         // Per-vertex sphere radius.

//[ ----------------------------------------------------------------
// Per-primitive transforms.
  mat4 xform;
  if (n_transforms > 0 && int(transform_id) > -1) {
    // Apply a transform, indexed by a transform slot ID vertex attribute.

#ifdef N_CONST_XFORMS
    // Get transforms from a fixed-sized block of uniform (constant) memory.
    // The GL_EXT_bindable_uniform extension allows sharing this through a VBO.
    center = transforms[int(transform_id)] * center;
#else  // TEXTURE_XFORMS
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
#endif // TEXTURE_XFORMS
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

  // For halo drawing, scale up drawing primitive vertices to cover the halo.
  float drawing_radius = eye_radius;    // The non-halo radius.
  if (drawing_style == DS_HALO) {
    // Take eye-space radius to post-projection units at the center pt depth.
    // The projection matrix does not change the view alignment, just the scale.
    vec4 post_proj_radius4 =
      gl_ProjectionMatrix * vec4(eye_radius, 0.0, var_center_pt.z, 1.0);
    float post_proj_radius = post_proj_radius4.x / post_proj_radius4.w;

    // Ratio to increase the eye space radius for the halo.
    float radius_ratio = (post_proj_radius + ndc_halo_width) / post_proj_radius;

    // Eye space halo radius for use in the pixel shader.
    drawing_radius = radius_ratio * eye_radius;
    var_halo_rad_sq = drawing_radius * drawing_radius; // Square roots are slow.
  }

  // The drawing vertices are in unit coordinates, relative to the center point.
  // Scale by the radius and add to the center point in eye space.
  vec3 eye_vert_pt;
  if (perspective == 1) {
    // When perspective is on, a small rotation is done as well, to keep a
    // billboard drawing pattern oriented directly toward the viewpoint.
    vec3 new_z = - normalize(var_center_pt);
    vec3 new_x = normalize(cross(vec3(0.0, 1.0, 0.0), new_z));
    vec3 new_y = cross(new_z, new_x);
    mat3 rotate = mat3(new_x, new_y, new_z);
    eye_vert_pt = var_center_pt + drawing_radius * (rotate * gl_Vertex.xyz);

    // With perspective, look from the origin, toward the vertex (pixel) points.
    // In eye space, the origin is at the eye point, by definition.
    var_view_pt = vec3(0.0);
    var_ray_vec = normalize(eye_vert_pt);

  } else {
    eye_vert_pt = var_center_pt + drawing_radius * gl_Vertex.xyz;

    // Without perspective, look from the 2D pixel position, in the -Z dir.
    var_view_pt = vec3(eye_vert_pt.xy, 0.0);  
    var_ray_vec = vec3(0.0, 0.0, -1.0);
  }

  // Transform the drawing vertex through the projection matrix, making clip
  // coordinates for the next stage of the pipeline.
  gl_Position = gl_ProjectionMatrix * vec4(eye_vert_pt, 1.0);
}
"""

# <line 0>
# ================================================================
# Note: a prefix with the #version statement is prepended to the following,
# together with an optional #define line.
sphereFragSrc = """
// Fragment (pixel) shader program for sphere primitives.
//
// See the description at the beginning of this file.

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int draw_for_mouseover; // 0: use normal color, 1: glname_color.
uniform int drawing_style;      // 0:normal, 1:override_color, 2:pattern, 3:halo
const int DS_NORMAL = 0;
const int DS_OVERRIDE_COLOR = 1;
const int DS_PATTERN = 2;
const int DS_HALO = 3;
uniform vec4 override_color;    // Color for selection or highlighted drawing.
uniform float override_opacity; // Multiplies the normal color alpha component.

// Lighting properties for the material.
uniform vec4 material; // Properties: [ambient, diffuse, specular, shininess].

uniform int perspective;
uniform vec4 clip;              // [near, far, middle, depth_inverse]
uniform float DEPTH_TWEAK;      // Offset for highlight over-drawing.

// A fixed set of lights.
uniform vec4 intensity;    // Set an intensity component to 0 to ignore a light.
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
  // the sample ray line passes closest to the center of the sphere.
  // . Vector between the transformed view point and the sphere center.
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
  // Subtract DEPTH_TWEAK to pull Z toward us during highlighted drawing.
  if (drawing_style != DS_NORMAL)
    gl_FragDepth -= DEPTH_TWEAK;

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
