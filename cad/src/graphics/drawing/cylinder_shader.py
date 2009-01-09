# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
cylinder_shader.py - Cylinder shader GLSL source code.

@author: Russ Fish
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Russ 090106: Design description file created.
  The most detailed level of items will become comments in the GLSL code.
"""

# See the docstring at the beginning of gl_shaders.py for GLSL references.

# ================================================================
# == Description: GLSL shader program for tapered cylinder/cone primitives,
# == including endcaps and optional halos.
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
# == Terminology:
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
# == How the sphere shader works:
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
# == Cylinder shaders:
# 
# Tapered cylinders/cones are more complicated than spheres, but still have
# radial symmetry to work with.  The visible surfaces of a cylinder are the
# portion of the barrel surface towards the viewpoint, and at most one endcap.
# (*Both* endcaps are hidden by the barrel if the viewpoint is anywhere between
# the endcap planes.)
# 
# 
# == How the cylinder vertex shader works:
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
# cylinder with the viewpoint above the middle of a cylinder, with 1.0 for both
# end radii, and endpoints at [0.0,0.0] and [0.0,1.0].
# 
# In general, the vertices output from the cylinder vertex shader are based on
# the input vertices, scaled and positioned by the cylinder axis taper radii and
# endpoints.  This makes a *symmetric trapezoid billboard quadrilateral*, whose
# midline swivels around the cylinder axis to face directly toward the viewpoint
# *in eye space coordinates*.  The job of this billboard is to cover all of the
# visible pixels of the cylinder barrel and endcap.
# 
# Consider a square truncated pyramid, a tapered box with 6 quadrilateral faces,
# tightly surrounding the tapered cylinder.  It has 2 square faces containing
# circular endcaps, and 4 symmetric trapezoids (tapered rectangles with 2
# parallel edges) tangent to cylinder barrel-lines along their midlines and
# connecting the endcap squares.
# 
# The output vertices for the billboard quadrilateral are based on the vertices
# of the tapered box, with several cases:
# 
# . NE1 doesn't draw the interior (back sides) of atom and bond surfaces.  When
#   the viewpoint is both (1) between the endcap planes, *and* (2) inside the
#   barrel surface as well, we draw nothing at all.
# 
#   - The shader determines our position vs. the endcap planes by projecting the
#     viewpoint onto the cylinder axis line, and comparing to the locations
#     along the axis line of the cylinder endpoints.
# 
#   - The viewpoint is inside the barrel surface if the distance to its
#     projection onto the cylinder axis is less than the cylinder radius,
#     extrapolated along the axis, at that projection point.
# 
# . When the viewpoint is inside the extension of the barrel surface, only one
#   endcap is visible, so the output billboard is the square endcap face whose
#   normal (along the cylinder axis) is toward the viewpoint.
# 
# . When the viewpoint is between the endcap planes, the output billboard is
#   only a barrel face trapezoid (made of vertices from the two edges of the
#   endcap squares that are toward the viewpoint) because the endcaps are hidden
#   by the barrel.  We swivel the pyramid on its axis to align a barrel face
#   with the viewpoint vector; we only need one barrel face because it hides the
#   others.
# 
# . When *both a barrel and an endcap* are visible, an endcap square face and a
#   barrel face are combined into a single trapezoid by ignoring the shared edge
#   between them, replacing an "L" shaped combination with a diagonal "\".
# 
#   - A subtlety: the max of the two cylinder radii is used for the endcap
#     square size, because the far end of the cylinder barrel may have a larger
#     radius than the endcap circle toward us, and we want to cover it too.
#     (Tighter bounding trapezoids are probably possible, but likely more work
#     to compute, and would make no difference most of the time since ray-hit
#     pixel discard is quick.)
# 
# 
# == A note about pixel (fragment) shaders in general:
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
# == How the cylinder pixel (fragment) shader works:
# 
# Ray-hit detection is in two parts, the endcaps and the barrel surface.
# 
# Endcap circle ray-hit detection is done first, because if the pixel ray hits
# the endcap, it won't get through to the barrel.
# 
# . The endcap ray-hit test is similar to the sphere shader hit test, in that a
#   center point and a radius are given, so calculate the distance that the ray
#   passes from the endcap center point similarly.
# 
# . The difference is that the endcaps are flat circles, not spheres, projecting
#   to an elliptical shape in general.  We deal with that by intersecting the
#   ray with the endcap plane and comparing the distance in the plane.  (Tweaked
#   for halos as in the sphere shader.)
# 
# . When there is a ray hit with the endcap, the normal vector is the axis
#   vector between the two cylinder axis endpoints, pointing outward.
# 
# Barrel surface ray-hit detection is based on comparing the "passing distance",
# between the the ray line and the cylinder axis line, with the tapered radius
# of the cylinder at the passing point.
# 
# . The ray and axis lines in general don't intersect.  The closest two points
#   where a pair of skew lines pass are their intersections with the line that
#   crosses perpendicular to both of them.  The direction vector of this
#   passing-line is the cross-product of the two line directions.  Project a
#   point on each line onto the passing-line direction with a dot-product, and
#   take the distance between them with another dot-product.
# 
# . Interpolate the tapered radius along the axis line, to the point closest to
#   the ray on the cylinder axis line, and compare with the passing distance.
# 
# We already know that the viewpoint is not within the cylinder (above, in the
# vertex shader), so if the ray from the viewpoint to the pixel passes within
# the cylinder radius of the axis line, it has to come in from outside,
# intersecting the extended barrel of the cylinder.  We will have a hit if the
# projection of this intersection point onto the axis line lies between the
# endpoints of the cylinder.
# 
# The pixel-ray goes from the viewpoint toward the pixel we are shading,
# intersecting the cylinder barrel, passing closest to the axis-line inside the
# barrel, and intersecting the barrel again on the way out.  We want the
# ray-line vs. barrel-line intersection that is closest to the viewpoint.
# (Note: The two intersection points and the ray passing-point will all be the
# same point when the ray is tangent to the cylinder.)
# 
# . First, we find a point on the barrel line that contains the intersection, in
#   the cross-section plane of the cylinder.  This crossing-plane is
#   perpendicular to the axis line and contains the two closest passing points,
#   as well as the passing-line perpendicular to the axis of the cylinder.
# 
#   If the radii are the same at both ends of the cylinder, the barrel-lines are
#   parallel.  The projection of the ray-line, along a ray-plane *parallel to
#   the cylinder axis* into the crossing-plane, is perpendicular to the
#   passing-line at the ray passing-point, both of which we already have.
# 
#   If the cylinder radii differ, instead project the viewpoint and the ray-line
#   direction vector into the cross-plane *toward the convergence-point*,
#   scaling by the taper of the cylinder along the axis.  [This is the one place
#   where tapered cylinders and cones are handled differently.]
# 
#   - Note: If we project parallel to the axis without tapering toward the
#     convergence-point, we're working in a plane parallel to the cylinder axis,
#     which intersects a tapered cylinder or cone in a hyperbola.  Intersecting
#     a ray with a hyperbola is hard.  Instead, we arrange to work in a plane
#     that includes the convergence point, so the intersection of the plane with
#     the cylinder is two straight lines.  Lines are easy.
# 
#   - The ray-line and the convergence-point determine a ray-plane, with the
#     projected ray-line at the intersection of the ray-plane with the
#     cross-plane.  If the ray-line goes through (i.e. within one pixel of) the
#     convergence-point, we instead discard the pixel.  Right at the tip of a
#     cone, the normal sample is very unstable, so we can't do valid shading
#     there anyway.
# 
#   - We calculate a *different 2D ray-line passing-point*, and hence
#     passing-line, for tapered cylinders and cones.  It's the closest point, on
#     the *projected* ray-line in the cross-plane, to the cylinder axis
#     passing-point (which doesn't move.)
# 
#     Note: The original passing-point is still *also* on the projected
#     ray-line, but not midway between the projected barrel-line intersections
#     anymore.  In projecting the ray-line into the crossing-plane within the
#     ray-plane, the passing-line twists around the cylinder axis.  You can see
#     this from the asymmetry of the tapering barrel-lines in 3D.  The
#     ray-line/barrel-line intersection further from the convergence-point has
#     to travel further to the crossing-plane than the nearer one.  (Of course,
#     we don't *know* those points yet, we're in the process of computing one of
#     them...)
# 
#   [Now we're back to common procedure for tapered and untapered cylinders.]
# 
#   - In the cross-plane, the projected ray-line intersects the circular cross
#     section of the cylinder at two points, going through the ray
#     passing-point, and cutting off a chord of the line and an arc of the
#     circle.  Two barrel lines go through the intersection points, along the
#     surface of the cylinder and also in the ray-plane.  Each of them contains
#     one of the intersection points between the ray and the cylinder.
# 
#     . The chord of the projected ray-line is perpendicularly bisected by the
#       passing-line, making a right triangle in the cross-plane.
# 
#     . The passing-distance is the length of the base of the triangle on the
#       passing-line, adjacent to the cylinder axis point.
# 
#     . The cylinder cross-section circle radius, tapered along the cylinder to
#       the cross-plane, is the length of the hypotenuse, between the axis point
#       and the first intersection point of the ray chord with the circle.
# 
#     . The length of the right triangle side opposite the axis, along the chord
#       of the ray-line toward the viewpoint, is given by the Pythagorean
#       Theorem.  This locates the third vertex of the triangle in the
#       cross-plane and the ray-plane.
# 
#     . The barrel line we want passes through the cross-plane at that point as
#       well as the convergence-point (which is at infinity in the direction of
#       the axis for an untapered cylinder.)
#   
# . Intersect the 3D ray-line with the barrel line in the ray-plane, giving the
#   3D ray-cylinder intersection point.  Note: this is not in general contained
#   in the 2D crossing-plane, depending on the location of the viewpoint.
# 
#   - The intersection point may be easily calculated by interpolating two
#     points on the ray line (e.g. the viewpoint and the ray passing-point.)
#     The interpolation coefficients are the ratios of their projection
#     distances to the barrel line.  (More dot-products.)
# 
# . Project the intersection point onto the axis line to determine whether we
#   hit the cylinder between the endcap planes.  If so, calculate the
#   barrel-line normal.
# 
#   - The normal at the intersection point (and all along the same barrel line)
#     is *perpendicular to the barrel line* (not the cylinder axis), in the
#     radial plane containing the cylinder axis and the barrel line.
# 
#   - The cross-product of the axis-intersection vector (from the intersection
#     point toward the axis passing-point), with the barrel-line direction
#     vector (from the first cylinder endpoint toward the second) makes a vector
#     tangent to the cross-plane circle, pointed along the arc toward the
#     passing-line.
# 
#   - The cross-product of the tangent-vector, with the barrel-line direction
#     vector, makes the normal to the cylinder along the barrel line.

# ================================================================
cylinderVertSrc = """
// Vertex shader program for cylinder primitives.
// 
// See the description at the beginning of this file.

// requires GLSL version 1.10
#version 110

...

"""

# ================================================================
cylinderFragSrc = """
// Fragment (pixel) shader program for cylinder primitives.
// 
// See the description at the beginning of this file.

// requires GLSL version 1.10
#version 110

...

"""
