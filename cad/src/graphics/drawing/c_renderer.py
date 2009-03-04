# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
c_renderer.py - Interface to the experimental C++ renderer:

- quux_module_import_succeeded (boolean)

- classes for the ColorSorter's arrays of C++ primitives to draw;
  does some memoization as a speedup.

WARNING: this has not been maintained for a long time, and has not
been tested after at least two major refactorings, one on 090303.
But it once worked and might be useful as example code, so it's
being kept around for now.

@author: Brad G, Will
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

Brad G wrote much of this in drawer.py.

I think Will modified the quux init code at some point.

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py

090303 Bruce refactored it.
"""

import foundation.env as env #bruce 051126
import utilities.EndUser as EndUser
import sys
import os
import Numeric

# these are used only by the test code at the bottom;
# if these ever cause an import cycle, move that code to a separate module.
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslate
from utilities.Log import redmsg
from utilities.debug import print_compact_stack

# ==

# Machinery to load the C renderer, from either of two places,
# one for developers and one for end users.

if EndUser.getAlternateSourcePath() != None:
    sys.path.append(os.path.join( EndUser.getAlternateSourcePath(),
                                  "experimental/pyrex-opengl"))
else:
    sys.path.append("./experimental/pyrex-opengl")

binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0]))
                           + '/../bin')
if binPath not in sys.path:
    sys.path.append(binPath)

quux_module_import_succeeded = False

try:
    import quux # can't be toplevel
    quux_module_import_succeeded = True
    if "experimental" in os.path.dirname(quux.__file__):
        # Should never happen for end users, but if it does we want to print the
        # warning.
        if env.debug() or not EndUser.enableDeveloperFeatures():
            print "debug: fyi:", \
                  "Loaded experimental version of C rendering code:", \
                  quux.__file__
except:
    quux = None
    quux_module_import_succeeded = False
    if env.debug(): #bruce 060323 added condition
        print "WARNING: unable to import C rendering code (quux module).", \
              "Only Python rendering will be available."
    pass

# ==

class ShapeList_inplace:
    """
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    This has the benefit over ShapeList that shapes aren't first stored in
    lots of Python lists, and then turned into lots of Numeric arrays.
    Instead, it stores directly in a list of fixed-size Numeric arrays.
    It shows some speedup, but not a lot.  And tons of memory is being
    used.  I'm not sure where. -grantham
    """
    __author__ = "grantham@plunk.org"

    _blocking = 512     # balance between memory zeroing and drawing efficiency

    def __init__(self):

        #
        # Lists of lists, each list containing a Numeric array and the
        # number of objects in that array.  E.g. Each element in
        # sphere is [l, n], where l is array((m, 9), 'f'), n is the
        # number of valid 9 element slices in l that represent
        # spheres, and m is equal to or more than n+1.
        #
        self.spheres = []
        self.cylinders = []

        # If this is true, disallow future adds.
        self.petrified = False


    def draw(self):

        """
        Draw all the objects represented in this shape list.
        """

        for (spheres, count) in self.spheres:
            quux.shapeRendererDrawSpheresIlvd(count, spheres)
        for (cylinders, count) in self.cylinders:
            quux.shapeRendererDrawCylindersIlvd(count, cylinders)


    def add_sphere(self, color4, pos, radius, name = 0):
        """
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, \
                  "Tried to add a sphere to a petrified ShapeList_inplace"

        # struct Sphere {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_center[3];
        #     float m_radius;
        # };

        if (len(self.spheres) == 0 or
            self.spheres[-1][1] == ShapeList_inplace._blocking):
            # size of struct Sphere in floats is 9
            block = Numeric.zeros((ShapeList_inplace._blocking, 9), 'f')
            self.spheres.append([block, 0])

        (block, count) = self.spheres[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            pos[0], pos[1], pos[2],
            radius)

        self.spheres[-1][1] += 1


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, \
                  "Tried to add a cylinder to a petrified ShapeList_inplace"

        # struct Cylinder {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_cappedBool;
        #     float m_pos1[3];
        #     float m_pos2[3];
        #     float m_radius; 
        # };

        if (len(self.cylinders) == 0 or
            self.cylinders[-1][1] == ShapeList_inplace._blocking):
            # size of struct Cylinder in floats is 13
            block = Numeric.zeros((ShapeList_inplace._blocking, 13), 'f')
            self.cylinders.append([block, 0])

        (block, count) = self.cylinders[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            float(capped),
            pos1[0], pos1[1], pos1[2],
            pos2[0], pos2[1], pos2[2],
            radius)

        self.cylinders[-1][1] += 1


    def petrify(self):
        """
        Make this object

        Since the last block of shapes might not be full, this
        function copies them to a new block exactly big enough to hold
        the shapes in that block.  The gc has a chance to release the
        old block and reduce memory use.  After this point, shapes
        must not be added to this ShapeList.
        """

        self.petrified = True

        if len(self.spheres) > 0:
            count = self.spheres[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.spheres[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.spheres[-1][0] = newblock

        if len(self.cylinders) > 0:
            count = self.cylinders[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.cylinders[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.cylinders[-1][0] = newblock

    pass

# ==

class ShapeList: # not used as of before 090303
    """
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    Probably better to use "ShapeList_inplace".
    """
    __author__ = "grantham@plunk.org"

    def __init__(self):

        self.memoized = False

        self.sphere_colors = []
        self.sphere_radii = []
        self.sphere_centers = []
        self.sphere_names = []

        self.cylinder_colors = []
        self.cylinder_radii = []
        self.cylinder_pos1 = []
        self.cylinder_pos2 = []
        self.cylinder_cappings = []
        self.cylinder_names = []


    def _memoize(self):

        """
        Internal function that creates Numeric arrays from the data stored
        in add_sphere and add-cylinder.
        """

        self.memoized = True

        # GL Names are uint32.  Numeric.array appears to have only
        # int32.  Winging it...

        self.sphere_colors_array = Numeric.array(self.sphere_colors, 'f')
        self.sphere_radii_array = Numeric.array(self.sphere_radii, 'f')
        self.sphere_centers_array = Numeric.array(self.sphere_centers, 'f')
        self.sphere_names_array = Numeric.array(self.sphere_names, 'i')

        self.cylinder_colors_array = Numeric.array(self.cylinder_colors, 'f')
        self.cylinder_radii_array = Numeric.array(self.cylinder_radii, 'f')
        self.cylinder_pos1_array = Numeric.array(self.cylinder_pos1, 'f')
        self.cylinder_pos2_array = Numeric.array(self.cylinder_pos2, 'f')
        self.cylinder_cappings_array = Numeric.array(self.cylinder_cappings,'f')
        self.cylinder_names_array = Numeric.array(self.cylinder_names, 'i')


    def draw(self):

        """
        Draw all the objects represented in this shape list.
        """

        # ICK - SLOW - Probably no big deal in a display list.

        if len(self.sphere_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawSpheres(len(self.sphere_radii),
                                          self.sphere_centers_array,
                                          self.sphere_radii_array,
                                          self.sphere_colors_array,
                                          self.sphere_names_array)

        if len(self.cylinder_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawCylinders(len(self.cylinder_radii),
                                            self.cylinder_pos1_array,
                                            self.cylinder_pos2_array,
                                            self.cylinder_radii_array,
                                            self.cylinder_cappings_array,
                                            self.cylinder_colors_array,
                                            self.cylinder_names_array)


    def add_sphere(self, color4, pos, radius, name = 0):
        """
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.sphere_colors.append(color4)
        self.sphere_centers.append(list(pos))
        self.sphere_radii.append(radius)
        self.sphere_names.append(name)
        self.memoized = False


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.cylinder_colors.append(color4)
        self.cylinder_radii.append(radius)
        self.cylinder_pos1.append(list(pos1))
        self.cylinder_pos2.append(list(pos2))
        self.cylinder_cappings.append(capped)
        self.cylinder_names.append(name)
        self.memoized = False


    def petrify(self):
        """
        Delete all but the cached Numeric arrays.

        Call this when you're sure you don't have any more shapes to store
        in the shape list and you want to release the python lists of data
        back to the heap.  Additional shapes must not be added to this shape
        list.
        """
        if not self.memoized:
            self._memoize()

        del self.sphere_colors
        del self.sphere_radii
        del self.sphere_centers
        del self.sphere_names

        del self.cylinder_colors
        del self.cylinder_radii
        del self.cylinder_pos1
        del self.cylinder_pos2
        del self.cylinder_cappings
        del self.cylinder_names

    pass

# ==

def test_pyrex_opengl(test_type): # not tested since major refactoring
    try:
        print_compact_stack("selectMode Draw: " )###
        ### BUG: if import quux fails, we get into some sort of infinite
        ###   loop of Draw calls. [bruce 070917 comment]

        #self.w.win_update()
        ## sys.path.append("./experimental/pyrex-opengl") # no longer 
        ##needed here -- always done in drawer.py
        binPath = os.path.normpath(os.path.dirname(
            os.path.abspath(sys.argv[0])) + '/../bin')
        if binPath not in sys.path:
            sys.path.append(binPath)
        import quux
        if "experimental" in os.path.dirname(quux.__file__):
            print "WARNING: Using experimental version of quux module"
        # quux.test()
        quux.shapeRendererInit()
        quux.shapeRendererSetUseDynamicLOD(0)
        quux.shapeRendererStartDrawing()
        if test_type == 1:
            center = Numeric.array((Numeric.array((0, 0, 0), 'f'),
                                    Numeric.array((0, 0, 1), 'f'),
                                    Numeric.array((0, 1, 0), 'f'),
                                    Numeric.array((0, 1, 1), 'f'),
                                    Numeric.array((1, 0, 0), 'f'),
                                    Numeric.array((1, 0, 1), 'f'),
                                    Numeric.array((1, 1, 0), 'f'),
                                    Numeric.array((1, 1, 1), 'f')), 'f')
            radius = Numeric.array((0.2, 0.4, 0.6, 0.8,
                                    1.2, 1.4, 1.6, 1.8), 'f')
            color = Numeric.array((Numeric.array((0, 0, 0, 0.5), 'f'),
                                   Numeric.array((0, 0, 1, 0.5), 'f'),
                                   Numeric.array((0, 1, 0, 0.5), 'f'),
                                   Numeric.array((0, 1, 1, 0.5), 'f'),
                                   Numeric.array((1, 0, 0, 0.5), 'f'),
                                   Numeric.array((1, 0, 1, 0.5), 'f'),
                                   Numeric.array((1, 1, 0, 0.5), 'f'),
                                   Numeric.array((1, 1, 1, 0.5), 'f')), 'f')
            result = quux.shapeRendererDrawSpheres(8, center, radius, color)
        elif test_type == 2:
            # grantham - I'm pretty sure the actual compilation, init,
            # etc happens once
            from bearing_data import sphereCenters, sphereRadii
            from bearing_data import sphereColors, cylinderPos1
            from bearing_data import cylinderPos2, cylinderRadii
            from bearing_data import cylinderCapped, cylinderColors
            glPushMatrix()
            glTranslate(-0.001500, -0.000501, 151.873627)
            result = quux.shapeRendererDrawSpheres(1848, 
                                                   sphereCenters, 
                                                   sphereRadii, 
                                                   sphereColors)
            result = quux.shapeRendererDrawCylinders(5290, 
                                                     cylinderPos1,
                                                     cylinderPos2, 
                                                     cylinderRadii, 
                                                     cylinderCapped, 
                                                     cylinderColors)
            glPopMatrix()
        quux.shapeRendererFinishDrawing()

    except ImportError:
        env.history.message(redmsg(
            "Can't import Pyrex OpenGL or maybe bearing_data.py, rebuild it"))

    return

# end

