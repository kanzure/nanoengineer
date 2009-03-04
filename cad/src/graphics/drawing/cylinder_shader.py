# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
cylinder_shader.py - Cylinder shader GLSL source code.

@author: Russ Fish
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Russ 090106: Design description file created.
  The most detailed level of items will become comments in the GLSL code.
"""

# See the docstring at the beginning of gl_shaders.py for GLSL references.

# ================================================================
# === Description: GLSL shader program for tapered cylinder/cone primitives,
# === including endcaps and optional halos.
#
# This shader raster-converts analytic tapered cylinders, defined by two
# end-points determining an axis line-segment, and two radii at the end-points.
# A constant-radius cylinder is tapered by perspective anyway, so the same
# shader does cones as well as cylinders.
# 
# The rendered cylinders are smooth, with no polygon facets.  Exact shading, Z
# depth, and normals are calculated in parallel in the GPU for each pixel.
# 
# 
# === Terminology:
# 
# In the remainder of this description, the word "cylinder" will be used to
# refer to the generalized family of tapered cylinders with flat ends
# perpendicular to the axis, including parallel cylinders, truncated cones
# (frusta), and pointed cones where the radius at one end is zero.  (If both
# radii are zero, nothing is visible.)
# 
# The two flat circular end surfaces of generalized cylinders are called
# "endcaps" here, and the rounded middle part a "barrel".  Cylinder barrel
# surfaces are ruled surfaces, made up of straight lines that are referred to as
# "barrel lines".
# 
# The barrel lines and axis line of a cylinder intersect at a "convergence
# point" where the tapered radius goes to zero.  This point will be at an
# infinite distance for an untapered cylinder, in which case its location is a
# pure direction vector, with a W coordinate of zero.  Pairs of barrel lines are
# coplanar, not skew, because they all intersect at the convergence point.
# 
# 
# === How the sphere shader works:
# 
# (This is a quick overview, as context for the cylinder shader.  See the the
# description, comments, and source of the sphere vertex shader program for fine
# details of that process that are not repeated here.)
# 
# The vertex shader for spheres doesn't care what OpenGL "unit" drawing pattern
# is used to bound the necessary pixels in the window, since spheres are
# symmetric in every direction.  Unit cubes, tetrahedra, or viewpoint oriented
# billboard quads are all treated the same.
# 
# . Their vertices are scaled by the sphere radius and added to the sphere
#   center point:
#       drawing_vertex = sphere_center + radius * pattern_vertex
#   This is done in eye coordinates, where lengths are still valid.
# 
# . When perspective is on, a rotation is done as well, to keep a billboard
#   drawing pattern oriented directly toward the viewpoint.
# 
# The fragment (pixel) shader for spheres gets a unit ray vector from the
# rasterizer, and 3D eye-space data from the vertex shader specifying the
# viewpoint and the sphere.  The ray gives the direction from the viewpoint
# through a pixel in the window in the vicinity of the sphere.
# 
# . For ray-hit detection, it determines whether the closest point to the sphere
#   center on the ray is within the sphere radius (or surrounding flat halo disk
#   radius) of the sphere center point.
# 
# . When there is a hit, it calculates the front intersection point of the ray
#   with the sphere, the 3D normal vector there, the depth of the projection
#   onto the window pixel, and the shaded pixel color based on the normal,
#   lights, and material properties.
# 
# 
# === Cylinder shaders:
# 
# Tapered cylinders/cones are more complicated than spheres, but still have
# radial symmetry around the axis to work with.  The visible surfaces of a
# cylinder are the portion of the barrel surface towards the viewpoint, and at
# most one endcap.  (*Both* endcaps are hidden by the barrel if the viewpoint is
# anywhere between the endcap planes.)
# 
# 
# === How the cylinder vertex shader works:
# 
# A vertex shader is executed in parallel on each input vertex in the drawing
# pattern.  Spheres have a single center point and radius, but (tapered)
# cylinders have two.  All vertices have copies of the associated "attribute"
# values, the two axis endpoints and associated end cap radii, packaged into two
# 4-vector VBOs for efficiency.
# 
# A particular drawing pattern is assumed as the input to this vertex shader, a
# "unit cylinder" quadrilateral billboard with its cylinder axis aligned along
# the X axis: four vertices with X in {0.0,1.0}, Y in {+1.0,-1.0}, and Z is 1.0.
# 
# The vertex shader identifies the individual vertices and handles them
# individually by knowing where they occur in the input drawing pattern.
# 
# This billboard pattern would emerge unchanged as the output for a unit
# cylinder with the viewpoint above the middle of the cylinder, with 1.0 for
# both end radii, and endpoints at [0.0,0.0] and [0.0,1.0].
# 
# In general, the vertices output from the cylinder vertex shader are based on
# the input vertices, scaled and positioned by the cylinder axis taper radii and
# endpoints.  This makes a *symmetric trapezoid billboard quadrilateral*, whose
# midline swivels around the cylinder axis to face directly toward the viewpoint
# *in eye space coordinates*.  The job of this billboard is to cover all of the
# visible pixels of the cylinder barrel and endcap.
# 
# [Further details are below, in the vertex shader main procedure.]
# 
# 
# === A note about pixel (fragment) shaders in general:
# 
# There are a minimum of 32 "interpolators" that smear the "varying" outputs of
# the vertex shader over the pixels during raster conversion, and pass them as
# inputs to the pixel shaders.  Since there are a lot more pixels than vertices,
# everything possible is factored out of the pixel shaders as an optimization.
# 
# . Division is an expensive operation, so denominators of fractions are often
#   passed as inverses for multiplication.
# 
# . Lengths are often passed and compared in squared form (calculated by the
#   dot-product of a vector with itself) to avoid square roots.
# 
# . Trig functions are expensive, but usually implicit in the results of
#   dot-products and cross-products, which are cheap GPU operations.
# 
# 
# === How the cylinder pixel (fragment) shader works:
# 
# Ray-hit detection is in two parts, the endcaps and the barrel surface.
# 
# Endcap circle ray-hit detection is done first, because if the pixel ray hits
# the endcap, it won't get through to the barrel.
# 
# Barrel surface ray-hit detection is based on comparing the "passing distance",
# between the ray line and the cylinder axis line, with the tapered radius of
# the cylinder at the passing point.
# 
# [Further details are below, in the pixel shader main procedure.]
# ===

# <line 0>
# ================================================================
# Note: if texture_xforms is off, a #define N_CONST_XFORMS array dimension is
# prepended to the following.  The #version statement precedes it.
cylinderVertSrc = """
// Vertex shader program for cylinder primitives.
// 
// See the description at the beginning of this file.

// XXX Start by copying a lot of stuff from the sphere shaders, factor later.

// Debugging aid; fills in *the rest* of the drawing pattern pixels.
// (Will not work on nVidia 7000s where return can not be in a conditional.)
///This fails on MBP/8600. Upper-cased, says 'DISCARD' : undeclared identifier.
///#define discard {gl_FragColor = var_basecolor; return;}

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
// Attributes can not be bool or int.
// Each non-matrix attribute has space for up to 4 floating-point values.
attribute vec4 endpt_rad_0, endpt_rad_1; // Cylinder endpoints and radii, twice.
// The following may be set to constants, when no arrays are provided.
attribute vec4 color;           // Cylinder color and opacity (RGBA).
attribute float transform_id;   // Ignored if -1.  (Attribs cannot be ints.)
attribute vec4 glname_color;    // Mouseover id (glname) as RGBA for drawing.

// Varying outputs, interpolated in the pipeline to the fragment (pixel) shader.
// The varying qualifier can be used only with float, floating-point vectors,
// matrices, or arrays of these.  Structures cannot be varying.
//
// The nVidia 7000 series (and maybe other older graphics chips), has 32
// interpolators for varyings, but they are organized as 8 vec4s, so we have to
// pack some things together.  Enumerated as slot-number(n-elements) below.
varying vec4 var_pack1;       // 1(4), var_ray_vec + var_visible_endcap.
vec3 var_ray_vec; // Vertex direction vector (pixel sample vec in frag shader.)
int var_visible_endcap;      // 0:first endcap visible, 1:second endcap.

varying vec4 var_pack2;       // 2(4), var_view_pt + var_visibility_type.
vec3 var_view_pt;             // Transformed view point.
int var_visibility_type;      // What is visible from the viewpoint.
const int VISIBLE_NOTHING = 0;
const int VISIBLE_BARREL_ONLY = 1;
const int VISIBLE_ENDCAP_ONLY = 2;
const int VISIBLE_ENDCAP_AND_BARREL = 3;

// Cylinder data.
varying vec3 var_endpts[2];   // 3,4(3) Transformed cylinder endpoints.

varying vec4 var_pack3;       // 5(4) var_radii[2] + var_halo_radii[2];
float var_radii[2];           // Transformed cylinder radii.
float var_halo_radii[2];      // Halo radii at transformed endpt Z depth.

varying vec4 var_basecolor;   // 6(4) Vertex color.

// Debugging data.
varying vec2 var_input_xy;   // 7(2) Drawing pattern billboard vertex.

// Vertex shader main procedure.
void main(void) {

  // Fragment (pixel) color will be interpolated from the vertex colors.
  if (draw_for_mouseover == 1)
    var_basecolor = glname_color;
  else if (drawing_style == DS_OVERRIDE_COLOR)
    // Solid highlighting or selection.
    var_basecolor = override_color;
  else
    var_basecolor = color;

#if 0 /// 1 // Debugging vertex shader: identify billboard vertices by color.
  // X in the billboard drawing pattern is red (0 to 1), Y (+-1) is green.
  var_basecolor = vec4(gl_Vertex.x, gl_Vertex.y + 1.0 / 2.0, 0.0, 1.0);
#endif
  var_input_xy = gl_Vertex.xy;
  
  // The endpoints and radii are combined in one attribute: endpt_rad.
  vec4 endpts[2];
  float radii[2];
  int i;
  endpts[0] = vec4(endpt_rad_0.xyz, 1.0);
  endpts[1] = vec4(endpt_rad_1.xyz, 1.0);
  radii[0] = endpt_rad_0.w;      // Per-vertex cylinder radii.
  radii[1] = endpt_rad_1.w;

//[ ----------------------------------------------------------------
// Per-primitive transforms.
  mat4 xform;
  if (n_transforms > 0 && int(transform_id) > -1) {
    // Apply a transform, indexed by a transform slot ID vertex attribute.

#ifdef N_CONST_XFORMS
    // Get transforms from a fixed-sized block of uniform (constant) memory.
    // The GL_EXT_bindable_uniform extension allows sharing this through a VBO.
    for (i = 0; i <= 1; i++)
      endpts[i] = transforms[int(transform_id)] * endpts[i];

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
    for (i = 0; i <= 1; i++)
      endpts[i] = xform * endpts[i];
#endif // texture_xforms.
  }
//] ----------------------------------------------------------------

  // Endpoints and radii in eye space coordinates.
  float billboard_radii[2];   // Either non-haloed, or larger for halos.
  float max_billboard_radius = 0.0;
  for (i = 0; i <= 1; i++) {
    vec4 eye_endpt4 = gl_ModelViewMatrix * endpts[i];
    var_endpts[i] = eye_endpt4.xyz / eye_endpt4.w;

    // Scaled cylinder radii in eye space.  (Assume uniform scale on all axes.)
    vec4 eye_radius4 = gl_ModelViewMatrix *
      vec4(max(.001, radii[i]), 0.0, 0.0, 0.0); // Russ 090220: zero radius bug.
    float eye_radius = length(vec3(eye_radius4));

    // The non-halo radius.
    /// GLSL bug?  Chained assignment of indexed array elements is broken???
    /// var_radii[i] = billboard_radii[i] = eye_radius;
    var_radii[i] = eye_radius;
    billboard_radii[i] = eye_radius;

    // For halo drawing, scale up drawing primitive vertices to cover the halo.
    if (drawing_style == DS_HALO) {

      // Take eye-space radius to post-projection units at the endpt depth.
      // Projection matrix does not change the view alignment, just the scale.
      vec4 post_proj_radius4 = gl_ProjectionMatrix *
                               vec4(eye_radius, 0.0, var_endpts[i].z, 1.0);
      float post_proj_radius = post_proj_radius4.x / post_proj_radius4.w;

      // Ratio to increase the eye space radius for the halo.
      float radius_ratio = (post_proj_radius + ndc_halo_width)/post_proj_radius;

      // Eye space halo radius for use in the pixel shader.
      /// GLSL bug?  Chained assignment of indexed array elements is broken???
      /// var_halo_radii[i] = billboard_radii[i] = radius_ratio * eye_radius;
      var_halo_radii[i] = radius_ratio * eye_radius;
      billboard_radii[i] = var_halo_radii[i];
    }
    max_billboard_radius = max(max_billboard_radius, billboard_radii[i]);
  }

  if (perspective == 1) {
    // In eye space, the origin is at the eye point, by definition.
    var_view_pt = vec3(0.0);
  } else {
    // Without perspective, look from the 2D pixel position, in the -Z dir.
    var_ray_vec = vec3(0.0, 0.0, -1.0);
  }

  //=== Vertex shader details 
  // [See context and general description above, at the beginning of the file.]
  // 
  // Consider a square truncated pyramid, a tapered box with 6 quadrilateral
  // faces, tightly surrounding the tapered cylinder.  It has 2 square faces
  // containing circular endcaps, and 4 symmetric trapezoids (tapered rectangles
  // with 2 parallel edges) tangent to cylinder barrel-lines along their
  // midlines and connecting the endcap squares.
  //===

  // The cylinder axis and the taper interpolated along it, in eye space units.
  vec3 axis_line_vec = var_endpts[1] - var_endpts[0];
  vec3 axis_line_dir = normalize(axis_line_vec);
  float axis_length = length(axis_line_vec);
  float axis_radius_taper = (var_radii[1] - var_radii[0]) / axis_length;

  //===
  // . The shader determines our position vs. the endcap planes by projecting
  //   the viewpoint onto the cylinder axis line, and comparing to the locations
  //   along the axis line of the cylinder endpoints.
  //===

  float vp_axis_proj_len; // Used for perspective only.
  bool vp_between_endcaps;
  if (perspective == 1) {

    // (Note: axis_line_dir vector is normalized, viewpt to endpt vec is not.)
    vp_axis_proj_len = dot(axis_line_dir, var_view_pt - var_endpts[0]);
    vp_between_endcaps = vp_axis_proj_len >= 0.0 &&       // First endpoint.
                         vp_axis_proj_len <= axis_length; // Second endpoint.
    // (Only valid when NOT between endcap planes, where no endcap is visible.)
    var_visible_endcap = int(vp_axis_proj_len >= 0.0);

  } else {

    // In orthogonal projection, if the axis is very nearly in the XY plane, the
    // endcaps are nearly edge-on and are ignored.  Otherwise, the one with the
    // greater Z is the visible one.
    vp_between_endcaps = abs(var_endpts[1].z - var_endpts[0].z) < 0.001;
    var_visible_endcap = int(var_endpts[1].z > var_endpts[0].z);

  }

  //===
  // . The viewpoint is inside the barrel surface if the distance to its
  //   projection onto the cylinder axis is less than the cylinder radius,
  //   extrapolated along the axis, at that projection point.
  //===

  bool vp_in_barrel;
  vec3 endpt_toward_vp_dir[2], endpt_across_vp_dir[2];
  if (perspective == 1) {

    vec3 vp_axis_proj_pt = var_endpts[0] + vp_axis_proj_len * axis_line_dir;
    float vp_axis_dist = length(vp_axis_proj_pt - var_view_pt);
    float vp_cyl_radius = vp_axis_proj_len * axis_radius_taper;
    vp_in_barrel = vp_axis_dist < vp_cyl_radius;

    // Directions relative to the viewpoint, perpendicular to the cylinder axis
    // at the endcaps, for constructing swiveling trapezoid billboard vertices.
    for (i = 0; i <= 1; i++) {
     if (vp_axis_dist < 0.001) {
        // Special case when looking straight down the axis.
        endpt_across_vp_dir[i] = vec3(1.0, 0.0, 0.0);
        endpt_toward_vp_dir[i] = vec3(0.0, 1.0, 0.0);
      } else {
        vec3 vp_endpt_dir = normalize(var_endpts[i] - var_view_pt);

        // Perpendicular to axis at the endpt, in the axis and viewpt plane.
        endpt_across_vp_dir[i] = normalize(cross(axis_line_dir, vp_endpt_dir));

        // Perpendicular to both the axis and the endpt_across_vp directions.
        endpt_toward_vp_dir[i] = normalize(cross(axis_line_dir,
                                           endpt_across_vp_dir[i]));
      }
    }
    
  } else {

    // In orthogonal projection, the barrel surface is hidden from view if the
    // far endcap is not larger than the near one, and the XY offset of the axis
    // is not larger than the difference in the endcap radii.
#ifdef FULL_SUBSCRIPTING
    int near_end = var_visible_endcap;
    int far_end = 1-near_end;
    float radius_diff = var_radii[near_end] - var_radii[far_end];
    float axis_offset = length(var_endpts[near_end].xy-var_endpts[far_end].xy);
#else
    // GLSL bug on GeForce 7600: Expand to use constant subscripts instead.
    // C6016: Profile requires arrays with non-constant indexes to be uniform
    float radius_diff;
    float axis_offset;
    if (var_visible_endcap == 1) {
      // near_end == 1, far_end == 0.
      radius_diff = var_radii[1] - var_radii[0];
      axis_offset = length(var_endpts[1].xy-var_endpts[0].xy);
    } else {
      // near_end == 0, far_end == 1.
      radius_diff = var_radii[0] - var_radii[1];
      axis_offset = length(var_endpts[0].xy-var_endpts[1].xy);
    }
#endif
    vp_in_barrel =  radius_diff >= 0.0 && axis_offset <= radius_diff;

    // Directions relative to the view dir, perpendicular to the cylinder axis,
    // for constructing swiveling trapezoid billboard vertices.
    if (axis_offset < 0.001) {
      // Special case looking straight down the axis, close to the -Z direction.
      endpt_across_vp_dir[0] = endpt_across_vp_dir[1] = vec3(0.0, 1.0, 0.0);
      endpt_toward_vp_dir[0] = endpt_toward_vp_dir[1] = vec3(1.0, 0.0, 0.0);
    } else {
      // Perpendicular to cylinder axis and the view direction, in the XY plane.
      endpt_across_vp_dir[0] = endpt_across_vp_dir[1] = 
        normalize(cross(axis_line_dir, var_ray_vec));

      // Perpendicular to both the cylinder axis and endpt_across_vp directions.
      endpt_toward_vp_dir[0] = endpt_toward_vp_dir[1] = 
        normalize(cross(axis_line_dir, endpt_across_vp_dir[0]));
    }

  }

  ///  vp_in_barrel = vp_between_endcaps = false; /// Single case for debugging.

  //===
  // The output vertices for the billboard quadrilateral are based on the
  // vertices of the tapered box, with several cases:
  // 
  // . NE1 does not draw the interior (back sides) of atom and bond surfaces.
  //   When the viewpoint is both (1) between the endcap planes, *and* (2)
  //   inside the barrel surface as well, we draw nothing at all.
  //===

  // Output vertex in eye space for now, will be projected into clipping coords.
  vec3 billboard_vertex;  

  if (vp_between_endcaps && vp_in_barrel) {
    var_visibility_type = VISIBLE_NOTHING;
    billboard_vertex = vec3(0.0, 0.0, -1.0); // Could be anything (nonzero?)
  }

  //===
  // . When the viewpoint is inside the extension of the barrel surface, only
  //   one endcap is visible, so the output billboard is the square endcap face
  //   whose normal (along the cylinder axis) is toward the viewpoint.
  //===

  else if (vp_in_barrel) {
    // Just the single visible endcap in this case.
    var_visibility_type = VISIBLE_ENDCAP_ONLY;
#ifdef FULL_SUBSCRIPTING
    vec3 scaled_across = billboard_radii[var_visible_endcap]
                         * endpt_across_vp_dir[var_visible_endcap];
    vec3 scaled_toward = billboard_radii[var_visible_endcap]
                         * endpt_toward_vp_dir[var_visible_endcap];

    // The unit rectangle drawing pattern is 0 to 1 in X, elsewhere
    // corresponding to the direction along the cylinder axis, but here we are
    // looking only at the endcap square, and so adjust to +-1 in X.
    billboard_vertex = var_endpts[var_visible_endcap]
      + (gl_Vertex.x * 2.0 - 1.0) * scaled_across
      + gl_Vertex.y * scaled_toward;
#else
    // GLSL bug on GeForce 7600: Expand to use constant subscripts instead.
    // C6016: Profile requires arrays with non-constant indexes to be uniform

    // The unit rectangle drawing pattern is 0 to 1 in X, elsewhere
    // corresponding to the direction along the cylinder axis, but here we are
    // looking only at the endcap square, and so adjust to +-1 in X.
    if (var_visible_endcap == 1) {
      vec3 scaled_across = billboard_radii[1] * endpt_across_vp_dir[1];
      vec3 scaled_toward = billboard_radii[1] * endpt_toward_vp_dir[1];
      billboard_vertex = var_endpts[1]
        + (gl_Vertex.x * 2.0 - 1.0) * scaled_across
        + gl_Vertex.y * scaled_toward;
    } else {
      vec3 scaled_across = billboard_radii[0] * endpt_across_vp_dir[0];
      vec3 scaled_toward = billboard_radii[0] * endpt_toward_vp_dir[0];
      billboard_vertex = var_endpts[0]
        + (gl_Vertex.x * 2.0 - 1.0) * scaled_across
        + gl_Vertex.y * scaled_toward;
    }
#endif
  }

  //===
  // . When the viewpoint is between the endcap planes, the output billboard is
  //   only a barrel face trapezoid (made of vertices from the two edges of the
  //   endcap squares that are toward the viewpoint) because the endcaps are
  //   hidden by the barrel.  We swivel the pyramid on its axis to align a
  //   barrel face with the viewpoint vector; we only need one barrel face
  //   because it hides all the others.
  //===

  else if (vp_between_endcaps) {
    var_visibility_type = VISIBLE_BARREL_ONLY;
#ifdef FULL_SUBSCRIPTING
    // Connecting two endcaps, X identifies which one this vertex comes from.
    int endcap = int(gl_Vertex.x);
    vec3 scaled_across = billboard_radii[endcap] * endpt_across_vp_dir[endcap];
    vec3 scaled_toward = billboard_radii[endcap] * endpt_toward_vp_dir[endcap];
    billboard_vertex = var_endpts[endcap]
      + scaled_toward  // Offset to the pyramid face closer to the viewpoint.
      + gl_Vertex.y * scaled_across;  // Offset to either side of the axis.
#else
    // GLSL bug on GeForce 7600: Expand to use constant subscripts instead.
    // C6016: Profile requires arrays with non-constant indexes to be uniform

    // Connecting two endcaps, X identifies which one this vertex comes from.
    if (int(gl_Vertex.x) == 1) {
      vec3 scaled_across = billboard_radii[1] * endpt_across_vp_dir[1];
      vec3 scaled_toward = billboard_radii[1] * endpt_toward_vp_dir[1];
      billboard_vertex = var_endpts[1]
        + scaled_toward  // Offset to the pyramid face closer to the viewpoint.
        + gl_Vertex.y * scaled_across;  // Offset to either side of the axis.
    } else {
      vec3 scaled_across = billboard_radii[0] * endpt_across_vp_dir[0];
      vec3 scaled_toward = billboard_radii[0] * endpt_toward_vp_dir[0];
      billboard_vertex = var_endpts[0]
        + scaled_toward  // Offset to the pyramid face closer to the viewpoint.
        + gl_Vertex.y * scaled_across;  // Offset to either side of the axis.
    }
#endif
  }

  //===
  // . When *both a barrel and an endcap* are visible, an endcap square face and
  //   a barrel face are combined into a single trapezoid by ignoring the shared
  //   edge between them, replacing an 'L' shaped combination with a diagonal
  //   '\'.
  // 
  //   - A subtlety: the max of the two cylinder radii is used for the endcap
  //     square size, because the far end of the cylinder barrel may have a
  //     larger radius than the endcap circle toward us, and we want to cover it
  //     too.  (Tighter bounding trapezoids are probably possible, but likely
  //     more work to compute, and would make no difference most of the time
  //     since ray-hit pixel discard is quick.)
  //===

  else {
    // Connect the outer edge of the visible endcap face with the inner edge of
    // the hidden endcap face at the other end of the cylinder barrel.
    var_visibility_type = VISIBLE_ENDCAP_AND_BARREL;
    int endcap = int(gl_Vertex.x);
#ifdef FULL_SUBSCRIPTING
    vec3 scaled_across = (gl_Vertex.y * max_billboard_radius)
                         * endpt_across_vp_dir[endcap];
    vec3 scaled_toward = max_billboard_radius * endpt_toward_vp_dir[endcap];

    // On the near face of the pyramid toward the viewpt, for the no-endcap end.
    vec3 near_edge_midpoint = var_endpts[endcap] + scaled_toward;
    vec3 near_edge_vertex = near_edge_midpoint + scaled_across;

    float halo_width = var_halo_radii[endcap]-var_radii[endcap];
#else
    // GLSL bug on GeForce 7600: Expand to use constant subscripts instead.
    // C6016: Profile requires arrays with non-constant indexes to be uniform
    vec3 endcap_across, endcap_toward, endcap_endpt;
    float halo_width;
    if (endcap == 1) {
      endcap_across = endpt_across_vp_dir[1];
      endcap_toward = endpt_toward_vp_dir[1];
      endcap_endpt = var_endpts[1];
      halo_width = var_halo_radii[1]-var_radii[1];
    } else {
      endcap_across = endpt_across_vp_dir[0];
      endcap_toward = endpt_toward_vp_dir[0];
      endcap_endpt = var_endpts[0];
      halo_width = var_halo_radii[0]-var_radii[0];
    }
      
    vec3 scaled_across = (gl_Vertex.y * max_billboard_radius) * endcap_across;
    vec3 scaled_toward = max_billboard_radius * endcap_toward;

    // On the near face of the pyramid toward the viewpt, for the no-endcap end.
    vec3 near_edge_midpoint = endcap_endpt + scaled_toward;
    vec3 near_edge_vertex = near_edge_midpoint + scaled_across;
#endif

    if (endcap != var_visible_endcap) {
      billboard_vertex = near_edge_vertex;

      if (drawing_style == DS_HALO) {  // Halo on the non-endcap cylinder end.
        // Extend the billboard axis length a little bit for a barrel-end halo.
        billboard_vertex += axis_line_dir * // Axis direction (unit vector).
          (float(endcap*2 - 1)              // Endcap 0:backward, 1:forward.
           * halo_width                     // Eye space halo width.
           * (axis_length /                 // Longer when view is more end-on.
              max(0.1 * axis_length, length(axis_line_vec.xy))));
      }
    } else {

      // This is a vertex of the visible endcap.  Push it away from the viewpt,
      // across the cylinder endcap by TWICE the radius, to the far face.
      vec3 away_vec = -(scaled_toward + scaled_toward);
      if (perspective == 0) {

        // Orthogonal: parallel projection.
        billboard_vertex = near_edge_vertex + away_vec;

      } else {

        // In perspective, we have to go a little bit wider, projecting the near
        // endcap-edge vertex width onto the far edge line.  Otherwise, slivers
        // of the edges of the cylinder barrel are sliced away by the billboard
        // edge.  Use the ratio of the distances from the viewpoint to the
        // midpoints of the far and near edges for widening.  This is right when
        // the endcap is edge-on and face-on, and conservative in between.
        vec3 far_edge_midpoint = near_edge_midpoint + away_vec;
        float ratio = length(far_edge_midpoint - var_view_pt) /
                      length(near_edge_midpoint - var_view_pt);
        billboard_vertex = far_edge_midpoint + ratio * scaled_across;
      }
    }
  }

  if (perspective == 1) {
    // With perspective, look from the origin, toward the vertex (pixel) points.
    var_ray_vec = normalize(billboard_vertex);
  } else {
    // Without perspective, look from the 2D pixel position, in the -Z dir.
    var_view_pt = vec3(billboard_vertex.xy, 0.0);  
  }

  // Transform the billboard vertex through the projection matrix, making clip
  // coordinates for the next stage of the pipeline.
  gl_Position = gl_ProjectionMatrix * vec4(billboard_vertex, 1.0);

  // Pack some varyings for nVidia 7000 series and similar graphics chips. 
  var_pack1 = vec4(var_ray_vec, float(var_visible_endcap));
  var_pack2 = vec4(var_view_pt, float(var_visibility_type));
  var_pack3 = vec4(var_radii[0], var_radii[1],
                   var_halo_radii[0], var_halo_radii[1]);
}
"""

# <line 0>
# ================================================================
# Note: a prefix with the #version statement is prepended to the following,
# together with an optional #define line.
cylinderFragSrc = """
// Fragment (pixel) shader program for cylinder primitives.
// 
// See the description at the beginning of this file.

// Uniform variables, which are constant inputs for the whole shader execution.
uniform int debug_code;         // 0:none, 1: show billboard outline.
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
// The varying qualifier can be used only with float, floating-point vectors,
// matrices, or arrays of these.  Structures cannot be varying.
//
// The nVidia 7000 series (and maybe other older graphics chips), has 32
// interpolators for varyings, but they are organized as 8 vec4s, so we have to
// pack some things together.  Enumerated as slot-number(n-elements) below.
varying vec4 var_pack1;       // 1(4), var_ray_vec + var_visible_endcap.
vec3 var_ray_vec;       // Pixel sample vector (vertex dir vec in vert shader.)
int var_visible_endcap;       // 0:first endcap visible, 1:second endcap.

varying vec4 var_pack2;       // 2(4), var_view_pt + var_visibility_type.
vec3 var_view_pt;             // Transformed view point.
int var_visibility_type;      // What is visible from the viewpoint.
const int VISIBLE_NOTHING = 0;
const int VISIBLE_BARREL_ONLY = 1;
const int VISIBLE_ENDCAP_ONLY = 2;
const int VISIBLE_ENDCAP_AND_BARREL = 3;

// Cylinder data.
varying vec3 var_endpts[2];   // 3,4(3) Transformed cylinder endpoints.

varying vec4 var_pack3;       // 5(4) var_radii[2] + var_halo_radii[2];
float var_radii[2];           // Transformed cylinder radii.
float var_halo_radii[2];      // Halo radii at transformed endpt Z depth.

varying vec4 var_basecolor;   // 6(4) Vertex color.

// Debugging data.
varying vec2 var_input_xy;    // 7(2) Drawing pattern billboard vertex.

// Line functions; assume line direction vectors are normalized (unit vecs.)
vec3 pt_proj_onto_line(in vec3 point, in vec3 pt_on_line, in vec3 line_dir) {
  // Add the projection along the line direction, to a base point on the line.
  return pt_on_line + dot(line_dir, point - pt_on_line) * line_dir;
}
float pt_dist_from_line(in vec3 point, in vec3 pt_on_line, in vec3 line_dir) {
  // (The length of of the cross-product is the sine of the angle between two
  // vectors, times the lengths of the vectors.  Sine is opposite / hypotenuse.)
  return length(cross(point - pt_on_line, line_dir));
}
float pt_dist_sq_from_line(in vec3 point, in vec3 pt_on_line, in vec3 line_dir){
  // Avoid a sqrt when we are just going to square the length anyway.
  vec3 crossprod = cross(point - pt_on_line, line_dir);
  return dot(crossprod, crossprod);
}

// Fragment (pixel) shader main procedure.
void main(void) {

  // Unpack varyings that were packed for graphics chips like nVidia 7000s.
  var_ray_vec = var_pack1.xyz;
  var_view_pt = var_pack2.xyz;
  // Varyings are always floats. Because of the interpolation calculations, even
  // though the same integer value goes into this variable at each vertex, the
  // interpolated result is not *exactly* the same integer, so round to nearest.
  var_visible_endcap = int(var_pack1.w + 0.5);
  var_visibility_type = int(var_pack2.w + 0.5);
  var_radii[0] = var_pack3.x; var_radii[1] = var_pack3.y;
  var_halo_radii[0] = var_pack3.z; var_halo_radii[1] = var_pack3.w;

#if 0 /// 1 // Debugging vertex shaders: fill in the drawing pattern.
  gl_FragColor = var_basecolor;
  // Show the visibility type as a fractional shade in blue.
  gl_FragColor.b =  0.25 * var_visibility_type;

  // Sigh.  Must not leave uniforms unused.
  int i = debug_code;
  float x = override_opacity;
  vec4 x4 = material; x4 = intensity; x4 = clip;
  vec3 x3 = light0; x3 = light1; x3 = light2; x3 = light3;
  x3 = light0H; x3 = light1H; x3 = light2H; x3 = light3H;
#else

  // This is all in *eye space* (pre-projection camera coordinates.)
  vec3 ray_hit_pt;      // For ray-hit and depth calculations.
  vec3 normal;          // For shading calculation.
  bool debug_hit = false;
  bool endcap_hit = false;
  bool halo_hit = false;
  vec4 halo_color = override_color;  // Default from uniform variable.

  // Debugging - Optionally halo pixels along the billboard outline, along with
  // the cylinder.  Has to be an overlay rather than a background, unless we
  // abondon use of 'discard' on all of the other hit cases.
  if (debug_code == 1 &&
      (var_input_xy.x <  0.01 || var_input_xy.x > 0.99 ||
       var_input_xy.y < -0.99 || var_input_xy.y > 0.99)) {
    // Draw billboard outline pixel like halo, overrides everything else below.
    debug_hit = true;
    halo_hit = true;
    // X in the billboard drawing pattern is red (0 to 1), Y (+-1) is green.
    halo_color = vec4(var_input_xy.x, var_input_xy.y + 1.0 / 2.0, 0.0, 1.0);
  }
  
  // Nothing to do if the viewpoint is inside the cylinder.
  if (!debug_hit && var_visibility_type == VISIBLE_NOTHING)
    discard; // **Exit**

  // Vertex ray direction vectors were interpolated into pixel ray vectors.
  // These go from the view point, through a sample point on the drawn polygon,
  // *toward* the cylinder (but may miss it and be discarded.)
  vec3 ray_line_dir = normalize(var_ray_vec);// Interpolation denormalizes vecs.

  // The cylinder axis and taper interpolated along it, in eye space units.
  // XXX These are known in the vertex shader; consider making them varying.
  vec3 endpt_0 = var_endpts[0];
  vec3 axis_line_vec = var_endpts[1] - endpt_0;
  vec3 axis_line_dir = normalize(axis_line_vec);
  float axis_length = length(axis_line_vec);
  float axis_radius_taper = (var_radii[1] - var_radii[0]) / axis_length;

  //=== Fragment (pixel) shader details
  // [See context and general description above, at the beginning of the file.]
  // 
  // The ray and axis lines in general do not intersect.  The closest two
  // points where a pair of skew lines pass are their intersections with the
  // line that crosses perpendicular to both of them.  The direction vector of
  // this passing-line is the cross-product of the two line directions.
  // Project a point on each line onto the passing-line direction with a
  // dot-product, and take the distance between them with another dot-product.
  //===

  // With normalized inputs, length is sine of the angle between the vectors.
  vec3 passing_line_crossprod = cross(ray_line_dir, axis_line_dir);
  vec3 passing_line_dir = normalize(passing_line_crossprod);

  // The distance between the passing points is the projection of the vector
  // between two points on the two lines (from cylinder endpoint on the axis
  // line, to viewpoint on the ray line) onto the passing-line direction vector.
  float passing_pt_signed_dist = dot(passing_line_dir, var_view_pt - endpt_0);
  float passing_pt_dist = abs(passing_pt_signed_dist);

  // The vector between the passing points, from the axis to the ray.
  vec3 passing_pt_vec = passing_pt_signed_dist * passing_line_dir;

  // Project the first cylinder endpoint onto the plane containing the ray from
  // the viewpoint, and perpendicular to the passing_line at the ray_passing_pt.
  vec3 ep0_proj_pt = endpt_0 + passing_pt_vec;

  // Project the viewpoint onto a line through the above point, parallel to
  // the cylinder axis, and going through through the ray_passing_pt we want.
  vec3 vp_proj_pt = pt_proj_onto_line(var_view_pt, ep0_proj_pt, axis_line_dir);
  // Distance from the viewpoint to its projection.
  float vp_proj_dist = length(vp_proj_pt - var_view_pt);// Opposite-side length.

  // Now we have a right triangle with the right angle where the viewpoint was
  // projected onto the line, and can compute the ray_passing_pt.
  //  * The hypotenuse is along the ray from the viewpoint to the ray passing
  //    point.
  //  * The sine of the angle at the passing line, between the ray and axis
  //    line directions, is the length of the passing-line cross-product vector.
  //  * The side opposite the passing angle goes from the viewpoint to its
  //    projection.  Its length is vp_proj_dist, and tells us the length of the
  //    hypotenuse.  Recall that sine is opposite over hypotenuse side lengths:
  //      sine = opp/hyp
  //      opp/sine = opp x 1/sine = opp x hyp/opp = hyp
  float vp_passing_dist = vp_proj_dist / length(passing_line_crossprod);// Hyp.
  vec3 ray_passing_pt = var_view_pt + vp_passing_dist * ray_line_dir;

  // Project back to the plane containing the axis for the other passing point.
  vec3 axis_passing_pt = ray_passing_pt - passing_pt_vec;

  //===
  // Endcap circle ray-hit detection is done first, because if the pixel ray
  // hits the endcap, it will not get through to the barrel.
  //===

  // Skip the endcap hit test if no endcap is visible.
  if (//false && /// May skip the endcap entirely to see just the barrel.
      !debug_hit && // Skip when already hit debug billboard-outline pixels.
      var_visibility_type != VISIBLE_BARREL_ONLY) { // (Never VISIBLE_NOTHING.)
    // (VISIBLE_ENDCAP_ONLY or VISIBLE_ENDCAP_AND_BARREL.)

    //===
    // . The endcap ray-hit test is similar to the sphere shader hit test, in
    //   that a center point and a radius are given, so calculate the distance
    //   that the ray passes from the endcap center point similarly.
    // 
    // . The difference is that the endcaps are flat circles, not spheres,
    //   projecting to an elliptical shape in general.  We deal with that by
    //   intersecting the ray with the endcap plane and comparing the distance
    //   in the plane.  (Tweaked for halos as in the sphere shader.)
    //===

#ifdef FULL_SUBSCRIPTING
    vec3 endcap_endpt = var_endpts[var_visible_endcap];
    float endcap_radius = var_radii[var_visible_endcap];
    float endcap_halo_radius = var_halo_radii[var_visible_endcap];
#else
    // GLSL bug on GeForce 7600: Expand to use constant subscripts instead.
    // error C6013: Only arrays of texcoords may be indexed in this profile,
    // and only with a loop index variable
    vec3 endcap_endpt;
    float endcap_radius, endcap_halo_radius;
    if (var_visible_endcap == 1) {
      endcap_endpt = var_endpts[1];
      endcap_radius = var_radii[1];
      endcap_halo_radius = var_halo_radii[1];
    } else {
      endcap_endpt = var_endpts[0];
      endcap_radius = var_radii[0];
      endcap_halo_radius = var_halo_radii[0];
    }
#endif

    // Calculate the intersection of the ray with the endcap plane, based on
    // the projections of the viewpoint and endpoint onto the axis.
    float vp_dist_along_axis = dot(axis_line_dir, var_view_pt);
    float ep_dist_along_axis = dot(axis_line_dir, endcap_endpt);
    float axis_ray_angle_cos = dot(axis_line_dir, ray_line_dir);
    ray_hit_pt = var_view_pt + ray_line_dir *
      ((ep_dist_along_axis - vp_dist_along_axis) / axis_ray_angle_cos);

    // Is the intersection within the endcap radius from the endpoint?
    vec3 closest_vec = ray_hit_pt - endcap_endpt;
    float plane_closest_dist = length(closest_vec);
    if (plane_closest_dist <= endcap_radius) {

      // Hit the endcap.  The normal is the axis direction, pointing outward.
      endcap_hit = true;
      normal = axis_line_dir * float(var_visible_endcap * 2 - 1); // * -1 or +1.

    } else if (drawing_style == DS_HALO &&
               plane_closest_dist <= endcap_halo_radius) {

      // Missed the endcap, but hit an endcap halo.
      halo_hit = endcap_hit = true;

    } else if (var_visibility_type == VISIBLE_ENDCAP_ONLY ) {

      // Early out.  We know only an endcap is visible, and we missed it.
      discard; // **Exit**

    }      
  }

  // Skip the barrel hit test if we already hit an endcap.
  // (Never VISIBLE_NOTHING here.)
  if (!endcap_hit && !debug_hit && var_visibility_type != VISIBLE_ENDCAP_ONLY) {
    // (VISIBLE_BARREL_ONLY, or VISIBLE_ENDCAP_AND_BARREL but missed endcap.)

    //===
    // Barrel surface ray-hit detection is based on comparing the 'passing
    // distance', between the the ray line and the cylinder axis line, with the
    // tapered radius of the cylinder at the passing point.
    // 
    // . Interpolate the tapered radius along the axis line, to the point
    //   closest to the ray on the cylinder axis line, and compare with the
    //   passing distance.
    //===

    float ep0_app_signed_dist = dot(axis_line_dir, axis_passing_pt - endpt_0);
    float passing_radius = var_radii[0] +
                           axis_radius_taper * ep0_app_signed_dist;
    if (passing_pt_dist > passing_radius) {

      // Missed the edge of the barrel, but might still hit a halo on it.
      float halo_radius_taper = (var_halo_radii[1] - var_halo_radii[0])
                                / axis_length;
      float passing_halo_radius = var_halo_radii[0] +
                                  halo_radius_taper * ep0_app_signed_dist;
      halo_hit = drawing_style == DS_HALO &&
                 passing_pt_dist <= passing_halo_radius &&
                 // Only when between the endcap planes.
                 ep0_app_signed_dist >= 0.0 &&
                 ep0_app_signed_dist <= axis_length;
      if (halo_hit) {

        // The ray_passing_pt is beyond the edge of the cylinder barrel, but
        // it is on the passing-line, perpendicular to the ray.  Perfect.
        ray_hit_pt = ray_passing_pt;

      } else {

        // Nothing more to do when we miss the barrel of the cylinder entirely.
        discard; // **Exit**

      }
    }

    if (!halo_hit) { // Barrel/ray intersection.
      //===
      // We already know that the viewpoint is not within the cylinder (the
      // vertex shader would have set VISIBLE_ENDCAP_ONLY), and that the ray
      // from the viewpoint to the pixel passes within the cylinder radius of
      // the axis line, so it has to come in from outside, intersecting the
      // extended barrel of the cylinder.  We will have a hit if the projection
      // of this intersection point onto the axis line lies between the
      // endpoints of the cylinder.
      // 
      // The pixel-ray goes from the viewpoint toward the pixel we are shading,
      // intersects the cylinder barrel, passes closest to the axis-line inside
      // the barrel, and intersects the barrel again on the way out.  We want
      // the ray-line vs. barrel-line intersection that is closer to the
      // viewpoint.  (Note: The two intersection points and the ray
      // passing-point will all be the same point when the ray is tangent to the
      // cylinder.)
      // 
      // . First, we find a point on the barrel line that contains the
      //   intersection, in the cross-section plane of the cylinder.  This
      //   crossing-plane is perpendicular to the axis line and contains the two
      //   closest passing points, as well as the passing-line through them,
      //   perpendicular to the axis of the cylinder.
      // 
      //   If the radii are the same at both ends of the cylinder, the
      //   barrel-lines are parallel.  The projection of the ray-line, along a
      //   ray-plane *parallel to the cylinder axis* into the crossing-plane, is
      //   perpendicular to the passing-line at the ray passing-point, both of
      //   which we already have.
      //===

      // (The 'csp_' prefix is used for objects in the cross-section plane.)
      vec3 csp_proj_view_pt, csp_passing_pt;
      float csp_bl_offset_sign, csp_passing_dist_sq, csp_radius_sq;
      vec3 convergence_pt;  // Only used for tapered cylinders.

      // Untapered cylinders.
      if (abs(var_radii[1] - var_radii[0]) <= 0.001) {
        csp_proj_view_pt = var_view_pt + (ray_passing_pt - vp_proj_pt);
        csp_passing_pt = ray_passing_pt;
        // With untapered parallel projection, the projected viewpoint is always
        // on the same side of the axis as the viewpoint.
        csp_bl_offset_sign = 1.0;

        csp_passing_dist_sq = passing_pt_dist * passing_pt_dist;
        csp_radius_sq = var_radii[0] * var_radii[0];

      } else {  // Tapered cylinders.

        //===
        //   If the cylinder radii differ, instead project the viewpoint and the
        //   ray-line direction vector *toward the convergence-point* into the
        //   cross-section plane, scaling by the taper of the cylinder along the
        //   axis.  [This is the one place where tapered cylinders and cones are
        //   handled differently from untapered cylinders.]
        //   
        //   - Note: If we project parallel to the axis without tapering toward
        //     the convergence-point, we are working in a plane parallel to the
        //     cylinder axis, which intersects a tapered cylinder or cone in a
        //     hyperbola.  Intersecting a ray with a hyperbola is hard.
        //     
        //     Instead, we arrange to work in a ray-plane that includes the
        //     convergence point, as well as the viewpoint and ray direction, so
        //     the intersection of the plane with the cylinder is two straight
        //     lines.  It is much easier to intersect a ray with a line.
        // 
        //   - The ray-line and the convergence-point determine a ray-plane,
        //     with the projected ray-line at the intersection of the ray-plane
        //     with the cross-plane.  If the ray-line goes through (i.e. within
        //     one pixel of) the convergence-point, we instead discard the
        //     pixel.  Right at the tip of a cone, the normal sample is very
        //     unstable, so we can not do valid shading there anyway.
        //===

        // The convergence point is where the radius tapers to zero, along the
        // axis from the first cylinder endpoint. Notice that if the second
        // radius is less than the first, the taper is negative, but we want to
        // go in the positive direction along the axis to the convergence point,
        // and vice versa.
        float ep0_cp_axis_signed_dist = var_radii[0] / -axis_radius_taper;
        convergence_pt = endpt_0 + ep0_cp_axis_signed_dist * axis_line_dir;

        // XXX Approximation; distance should be in NDC (pixel) coords.
        float ray_cpt_dist_sq = pt_dist_sq_from_line(  // Save a sqrt.
          convergence_pt, var_view_pt, ray_line_dir);
        if (ray_cpt_dist_sq <= .00001)
              discard; // **Exit**

        //===
        //   - We calculate a *different 2D ray-line passing-point*, and hence
        //     passing-line, for tapered cylinders and cones.  It is the closest
        //     point, on the *projected* ray-line in the cross-plane, to the
        //     cylinder axis passing-point (which does not move.)
        //     
        //     Note: The original passing-point is still *also* on the projected
        //     ray-line, but not midway between the projected barrel-line
        //     intersections anymore.  In projecting the ray-line into the
        //     crossing-plane within the ray-plane, the passing-line twists
        //     around the cylinder axis.  You can see this from the asymmetry of
        //     the tapering barrel-lines in 3D.  The ray-line/barrel-line
        //     intersection further from the convergence-point has to travel
        //     further to the crossing-plane than the nearer one.  (Of course,
        //     we do not *know* those points yet, we are in the process of
        //     computing one of them.)
        //===

        // Project the viewpoint into the crossing-plane that contains the
        // passing-points, along a line to the convergence point, based on the
        // projection of the viewpoint onto the axis and the positions of the
        // axis_passing_pt and the convergence point along the axis.  We know
        // above that the viewpoint is not already in the crossing-plane, the
        // crossing-plane does not go through the convergence point, and the
        // viewpoint is not on the axis (i.e. inside the cylinder barrel.)
        float cp_axis_loc = dot(axis_line_dir, convergence_pt);
        float vp_axis_rel_loc = dot(axis_line_dir, var_view_pt) - cp_axis_loc;
        float app_axis_rel_loc = dot(axis_line_dir, axis_passing_pt) -
                                 cp_axis_loc;
        // Ratios from similar triangles work with signed distances (relative to
        // the convergence point along the axis, in this case.)
        csp_proj_view_pt = convergence_pt + (var_view_pt - convergence_pt) *
          (app_axis_rel_loc / vp_axis_rel_loc);

        // New passing point in the cross-section plane. 
        vec3 csp_ray_line_dir = normalize(ray_passing_pt - csp_proj_view_pt);
        csp_passing_pt = pt_proj_onto_line(axis_passing_pt,
          csp_proj_view_pt, csp_ray_line_dir);

        // With tapered projection through the convergence point, when the
        // convergence point is *between* the cylinder and the projection of the
        // viewpoint onto the axis line, the projection of the viewpoint
        // *through* the convergence point into the cross-section plane will be
        // on the *opposite side* of the axis from the viewpoint.  So we need a
        // sign bit to choose the other barrel-line point in that case.
        csp_bl_offset_sign =
          sign(vp_axis_rel_loc) != sign(app_axis_rel_loc) ? -1.0: 1.0;

        vec3 csp_passing_vec = csp_passing_pt - axis_passing_pt;
        csp_passing_dist_sq = dot(csp_passing_vec, csp_passing_vec);

        csp_radius_sq = passing_radius * passing_radius;

      } // End of tapered cylinders.

      //===
      //   [Now we are back to common code for tapered and untapered cylinders.]
      // 
      //   - In the cross-plane, the projected ray-line intersects the circular
      //     cross section of the cylinder at two points, going through the ray
      //     passing-point, and cutting off a chord of the line and an arc of
      //     the circle.  Two barrel lines go through the intersection points,
      //     along the surface of the cylinder and also in the ray-plane.  Each
      //     of them contains one of the intersection points between the ray and
      //     the cylinder.
      // 
      //     . The chord of the projected ray-line is perpendicularly bisected
      //       by the passing-line, making a right triangle in the cross-plane.
      // 
      //     . The passing-distance is the length of the base of the triangle on
      //       the passing-line, adjacent to the cylinder axis point.
      // 
      //     . The cylinder cross-section circle radius, tapered along the
      //       cylinder to the cross-plane, is the length of the hypotenuse,
      //       between the axis point and the first intersection point of the
      //       ray chord with the circle.
      // 
      //     . The length of the right triangle side opposite the axis, along
      //       the chord of the ray-line toward the viewpoint, is given by the
      //       Pythagorean Theorem.  This locates the third vertex of the
      //       triangle, in the cross-plane and the ray-plane.
      //===

      vec3 barrel_line_pt = csp_passing_pt +
        (sqrt(csp_radius_sq - csp_passing_dist_sq) * csp_bl_offset_sign) *
        normalize(csp_proj_view_pt - csp_passing_pt);

      //===
      //     . The barrel line we want passes through the cross-plane at that
      //       point as well as the convergence-point (which is at infinity in
      //       the direction of the axis for an untapered cylinder.)
      //===

      vec3 barrel_line_dir = axis_line_dir;  // Untapered.
      if (abs(var_radii[1] - var_radii[0]) > 0.001)
        // Tapered.  Sign of line direction does not affect projecting onto it.
        barrel_line_dir = normalize(convergence_pt - barrel_line_pt);

      //===
      // . Intersect the 3D ray-line with the barrel line in the ray-plane,
      //   giving the 3D ray-cylinder intersection point.  Note: this is not in
      //   general contained in the 2D crossing-plane, depending on the location
      //   of the viewpoint.
      // 
      //   - The intersection point may be easily calculated by interpolating
      //     two points on the ray line (e.g. the viewpoint and the ray
      //     passing-point.)  The interpolation coefficients are the ratios of
      //     their projection distances to the barrel line.  (More
      //     dot-products.)
      //===

      float vp_bl_proj_dist = pt_dist_from_line(
        var_view_pt, barrel_line_pt, barrel_line_dir);

      float bl_rpp_proj_dist = pt_dist_from_line(
        ray_passing_pt, barrel_line_pt, barrel_line_dir);

      ray_hit_pt = mix(var_view_pt, ray_passing_pt,
        vp_bl_proj_dist / (vp_bl_proj_dist + bl_rpp_proj_dist));

      //===
      // . Project the intersection point onto the axis line to determine
      //   whether we hit the cylinder between the endcap planes.  If so,
      //   calculate the barrel-line normal.
      //===

      float ip_axis_proj_len = dot(axis_line_dir, ray_hit_pt - endpt_0);
      if (ip_axis_proj_len < 0.0 || ip_axis_proj_len > axis_length) {

        // We missed the portion of the cylinder barrel between the endcap
        // planes.  A halo may be required past the end.  We find endcap hits
        // *before* the barrel, so we know there is not one providing a halo on
        // this end yet.
        halo_hit = drawing_style == DS_HALO &&
            (ip_axis_proj_len < 0.0 &&
               ip_axis_proj_len >= var_radii[0] - var_halo_radii[0] ||
             ip_axis_proj_len > axis_length &&
               ip_axis_proj_len <= axis_length +
                                   var_halo_radii[1] - var_radii[1]
            );

        if (! halo_hit)
          discard; // **Exit**

      } else {

        //===
        //   - The normal at the intersection point (and all along the same
        //     barrel line) is *perpendicular to the barrel line* (not the
        //     cylinder axis), in the radial plane containing the cylinder axis
        //     and the barrel line.
        // 
        //   - The cross-product of the axis-intersection vector (from the
        //     intersection point toward the axis passing-point), with the
        //     barrel-line direction vector (from the first cylinder endpoint
        //     toward the second) makes a vector tangent to the cross-plane
        //     circle, pointed along the arc toward the passing-line.
        // 
        //   - The cross-product of the tangent-vector, with the barrel-line
        //     direction vector, makes the normal to the cylinder along the
        //     barrel line.
        //===

        vec3 arc_tangent_vec = cross(axis_passing_pt - ray_hit_pt,
                                     barrel_line_dir);
        normal = normalize(cross(arc_tangent_vec, barrel_line_dir));

      } // End of barrel normal calculation.

    } // End of barrel/ray intersection.
  } // End of barrel hit test.

  if (debug_hit) {
    gl_FragDepth = gl_FragCoord.z; // Debug display: Z from billboard polygon.
  } else {
    float sample_z = ray_hit_pt.z;

    // Distance from the view point to the intersection, transformed into
    // normalized device coordinates, sets the fragment depth.  (Note: The
    // clipping box depth is passed as its inverse, to save a divide.)
    if (perspective == 1) {

      // Perspective: 0.5 + (mid + (far * near / sample_z)) / depth
      gl_FragDepth = 0.5 + (clip[2] + (clip[1] * clip[0] / sample_z)) * clip[3];

    } else {

      // Ortho: 0.5 + (-middle - sample_z) / depth
      gl_FragDepth = 0.5 + (-clip[2] - sample_z) * clip[3];
    }
  }
  // Subtract DEPTH_TWEAK to pull Z toward us during highlighted drawing.
  if (drawing_style != DS_NORMAL)
    gl_FragDepth -= DEPTH_TWEAK;

  // Nothing more to do if the intersection point is clipped.
  if (gl_FragDepth < 0.0 || gl_FragDepth > 1.0)
      discard; // **Exit**

  // No shading or lighting on halos.
  if (halo_hit) {
      gl_FragColor = halo_color; // No shading or lighting on halos.
  } else {

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
#endif
}
"""
