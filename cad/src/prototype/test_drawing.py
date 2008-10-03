# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
test_drawing.py -- Replaces GLPane.paintGL() to try various OpenGL rendering
models, determine whether the performance bottleneck is in OpenGL, Qt, or
somewhere else, and find a better alternative.

It simply renders an array of n^2 unit spheres, n by n.  Spin them around with
the NE1 rotate control, getting frames per second off the MacOS OpenGl Profiler
or the internal FPS counter (enable printFames.)

You won't get redraws, and hence frame counts printed, unless you are generating
a steady stream of mouse events with the left mouse button pressed.  It's more
interesting to put NE1 in pan or rotate mode so you can see the redraws.

With a low number of spheres, the frame rate is bottlenecked by Qt.  You'll know
that's the case because as you increase the number of spheres, the frame rate
doesn't go down at first.  Eventually, something in the graphics card becomes
the bottleneck.  These tests were done as a series of explorations into finding
and avoiding those bottlenecks.

To turn it on, enable TEST_DRAWING at the start of
graphics/widgets/GLPane_rendering_methods.py .
"""

from geometry.VQT import Q, V

ALWAYS_GL_UPDATE = True  # Always redraw as often as possible.
SPIN = True # spin the view...
_SPINQUAT = Q(V(1,0,0),V(0,0,1))/90.0 # ... by 1 degree per frame

DRAWSPHERE_DETAIL_LEVEL = 2

AVAILABLE_TEST_CASES_DICT = {
    # (testCase: description for combobox item text)
    1: "",
    2: "",
    3: "",
    3.1: "",
    3.2: "",
    3.3: "",
    3.4: "",
    4: "",
    5: "",
    6: "",
    7: "",
    8: "",
    8.1: "",
    8.2: "",
 }
AVAILABLE_TEST_CASES_ITEMS = AVAILABLE_TEST_CASES_DICT.items()
AVAILABLE_TEST_CASES_ITEMS.sort()

# Draw an array of nSpheres x nSpheres, with divider gaps every 10 and 100.
# 10, 25, 50, 100, 132, 200, 300, 400, 500...

#testCase = 1; nSpheres = 132
#testCase = 8; nSpheres = 50; chunkLength = 24
#testCase = 8; nSpheres = 132; chunkLength = 24
testCase = 8.1; nSpheres = 50; chunkLength = 24
#testCase = 8.1; nSpheres = 75; chunkLength = 24
#testCase = 8.1; nSpheres = 100; chunkLength = 200
#testCase = 8.1; nSpheres = 100; chunkLength = 50
### Hangs #testCase = 8.1; nSpheres = 100; chunkLength = 24
#testCase = 8.2; nSpheres = chunkLength = 10
#testCase = 8.2; nSpheres = 50; chunkLength = 250
#testCase = 8.2; nSpheres = 100; chunkLength = 200
#testCase = 8.2; nSpheres = 100; chunkLength = 50

# Longish chunks for test case 3.4 (with transforms)
#nSpheres = 132; transformChunkLength = 1000
#
# 16x16 sphere array, chunked by columns for vertex shader debugging display.
#nSpheres = transformChunkLength = 16
#
# Short chunks ok w/ texture_xforms = 1, but too many chunks for N_CONST_XFORMS.
#nSpheres = 132; transformChunkLength = 70 # 249 chunks.
#nSpheres = 132; transformChunkLength = 50 # 349 chunks.
#nSpheres = 132; transformChunkLength = 20 # 872 chunks.
#nSpheres = 132; transformChunkLength = 10 # 1743 chunks.
#nSpheres = 132; transformChunkLength = 8 # 2178 chunks.
#
#nSpheres = 300; transformChunkLength = 8 # 11250 chunks.
#nSpheres = 400; transformChunkLength = 8 # 20000 chunks.
#nSpheres = 500; transformChunkLength = 8 # 31250 chunks.

printFrames = True # False    # Prints frames-per-second if set.

from geometry.VQT import V, Q, A, norm, vlen, angleBetween

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.GLSphereBuffer import GLSphereBuffer

from graphics.drawing.DrawingSet import DrawingSet
from graphics.drawing.TransformControl import TransformControl
from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_workers import drawsphere_worker_loop
from graphics.drawing.gl_buffers import GLBufferObject
from graphics.drawing.gl_Scale import glScale

import numpy

from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_COMPILE_AND_EXECUTE
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_STENCIL_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_UNSIGNED_INT
from OpenGL.GL import GL_VERTEX_ARRAY

from OpenGL.GL import glCallList
from OpenGL.GL import glClear
from OpenGL.GL import glClearColor
from OpenGL.GL import glColor3i
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEndList
from OpenGL.GL import glFlush
from OpenGL.GL import glGenLists
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glNewList
from OpenGL.GL import glNormalPointer
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glSecondaryColor3fv
from OpenGL.GL import glTranslatef
from OpenGL.GL import glVertexPointer

from OpenGL.GL.ARB.vertex_program import glDisableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glEnableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

from time import time
from math import sin, pi, fmod

def delete_caches():
    """
    External code which modifies certain parameters (e.g. testCase, nSpheres)
    can call this to remove our caches, so the change takes effect.
    """
    #bruce 080930; not sure it contains enough to make runtime change of testCase fully correct;
    # should it contain _USE_SHADERS?
    # Ideally we'd refactor this whole file so each testCase was its own class,
    # with instances containing the cached objects and draw methods.
    global test_csdl, test_dl, test_dls, test_ibo, test_vbo, test_spheres, test_DrawingSet
    global frame_count, last_frame, last_time, C_array, start_pos

    test_csdl = None
    test_dl = None
    test_dls = None
    test_ibo = None
    test_vbo = None
    test_spheres = None
    test_DrawingSet = None

    frame_count = 0
    last_frame = 0
    last_time = time()

    C_array = None

    # Start at the lower-left corner, offset so the whole pattern comes
    # up centered on the origin.
    start_pos = V(-(nSpheres-1)/2.0, -(nSpheres-1)/2.0, 0)

    return

delete_caches() # initialize globals


# From drawsphere_worker_loop().
def sphereLoc(x, y):                    # Assume int x, y in the sphere array.
    return start_pos + V( x + x/10 + x/100, y + y/10 + y/100, 0)

def rainbow(t):
    # Colors progress from red to blue.
    if t < .25:
        # 0 to .25, red to yellow (ramp up green).
        return [1.0, 4 * t, 0.0]
    elif t < .5:
        # .25 to .5, yellow to green (ramp down red).
        return [4 * (.5 - t), 1.0, 0.0]
    elif t < .75:
        # .5 to .75, green to cyan (ramp up blue).
        return [0.0, 1.0, 4 * (t - .5)]
    else:
        # .75 to 1, cyan to blue (ramp down green).
        return [0.0, 4 * (1.0 - t), 1.0]


_USE_SHADERS = True # change to false if loading them fails the first time

def test_drawing(glpane):
    """
    When TEST_DRAWING is enabled at the beginning of graphics/widgets/glPane.py,
    this file is loaded and GLPane.paintGL() calls the test_drawing() function
    instead of the usual body of paintGL().
    """
    # Load the sphere shaders if needed.
    global _USE_SHADERS
    if _USE_SHADERS:
        if not hasattr(drawing_globals, "sphereShader"):
            print "Loading sphere shaders."

            try:
                from graphics.drawing.gl_shaders import GLSphereShaderObject
                drawing_globals.sphereShader = GLSphereShaderObject()

                print "Sphere-shader initialization is complete.\n"
            except:
                _USE_SHADERS = False
                print "Exception while loading sphere shaders, will reraise and not try again"
                raise
            pass

    global frame_count, last_frame, last_time, start_pos
    frame_count += 1
    now = time()
    if printFrames and int(now) > int(last_time):
        print "  %4.1f fps" % ((frame_count - last_frame) / (now - last_time))
        last_frame = frame_count
        last_time = now
        pass

    glpane.scale = nSpheres * .6
    glpane._setup_modelview()
    glpane._setup_projection()
    ##glpane._compute_frustum_planes()

    glClearColor(64.0, 64.0, 64.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT )
    ##glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    glMatrixMode(GL_MODELVIEW)

    global test_csdl, test_dl, test_dls, test_ibo, test_vbo, test_spheres
    global test_DrawingSet

    # See below for test case descriptions and timings on a MacBook Pro.
    # The Qt event toploop in NE1 tops out at about 60 frames-per-second.

    # NE1 with test toploop, single CSDL per draw (test case 1)
    # . 17,424 spheres (132x132, through the color sorter) 4.8 FPS
    #   Russ 080919: More recently, 12.2 FPS.
    # . Level 2 spheres have 9 triangles x 20 faces, 162 distinct vertices, 
    #   visited on the average 2.3 times, giving 384 tri-strip vertices.
    # . 17,424 spheres is 6.7 million tri-strip vertices.  (6,690,816)
    if testCase == 1:
        if test_csdl is None:
            print ("Test case 1, %d^2 spheres\n  %s." %
                   (nSpheres, "ColorSorter"))

            test_csdl = ColorSortedDisplayList()
            ColorSorter.start(test_csdl)
            drawsphere([0.5, 0.5, 0.5], # color
                       [0.0, 0.0, 0.0], # pos
                       .5, # radius
                       DRAWSPHERE_DETAIL_LEVEL,
                       testloop = nSpheres )
            ColorSorter.finish()
            pass
        else:
            test_csdl.draw()
        pass

    # NE1 with test toploop, single display list per draw (test case 2)
    # . 10,000 spheres (all drawing modes) 17.5 FPS
    # . 17,424 spheres (132x132, manual display list) 11.1 FPS
    # . 40,000 spheres (mode 5 - VBO/IBO spheres from DL's) 2.2 FPS
    # . 40,000 spheres (mode 6 - Sphere shaders from DL's) 2.5 FPS
    # . 90,000 spheres (all drawing modes) 1.1 FPS
    elif testCase == 2:
        if test_dl is None:
            print ("Test case 2, %d^2 spheres\n  %s." %
                   (nSpheres, "One display list calling primitive dl's"))

            test_dl = glGenLists(1)
            glNewList(test_dl, GL_COMPILE_AND_EXECUTE)
            drawsphere_worker_loop(([0.0, 0.0, 0.0], # pos
                                    .5, # radius
                                    DRAWSPHERE_DETAIL_LEVEL,
                                    nSpheres ))
            glEndList()
            pass
        else:
            glColor3i(127, 127, 127)
            glCallList(test_dl)
        pass

    # NE1 with test toploop, one big chunk VBO/IBO of box quads (test case 3)
    # .  17,424 spheres (1 box/shader draw call) 43.7 FPS
    # .  17,424 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 57.7 FPS
    # .  40,000 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 56.7 FPS
    # .  90,000 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 52.7 FPS
    # . 160,000 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 41.4 FPS
    # . 250,000 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 27.0 FPS
    elif int(testCase) == 3:
        doTransforms = False
        if test_spheres is None:
            print ("Test case 3, %d^2 spheres\n  %s." %
                   (nSpheres, "One big VBO/IBO chunk buffer"))
            if testCase == 3.1:
                print ("Sub-test 3.1, animate partial updates.")
            elif testCase == 3.2:
                print ("Sub-test 3.2, animate partial updates" +
                       " w/ C per-chunk array buffering.")
            elif testCase == 3.3:
                print ("Sub-test 3.3, animate partial updates" +
                       " w/ Python array buffering.")
            # . 3.4 - Big batch draw, with transforms indexed by IDs added.
            #   (Second FPS number with debug colors in the vertex shader off.)
            #   - 90,000 (300x300) spheres, texture_xforms = 1, 26(29) FPS
            #   - 90,000 (300x300) spheres, N_CONST_XFORMS = 250, 26(29) FPS
            #   - 90,000 (300x300) spheres, N_CONST_XFORMS = 275, 0.3(0.6) FPS
            #     (What happens after 250?  CPU usage goes from 40% to 94%.)
            #   -160,000 (400x400) spheres, texture_xforms = 1, 26 FPS
            #   -250,000 (500x500) spheres, texture_xforms = 1, 26 FPS
            elif testCase == 3.4:
                print ("Sub-test 3.4, add transforms indexed by IDs.")
                from graphics.drawing.gl_shaders import texture_xforms
                from graphics.drawing.gl_shaders import N_CONST_XFORMS
                if texture_xforms:
                    print "Transforms in texture memory."
                else:
                    print "%d transforms in uniform memory." % N_CONST_XFORMS
                    pass
                doTransforms = True
                pass

            centers = []
            radius = .5
            radii = []
            colors = []
            if not doTransforms:
                transformIDs = None
            else:
                transformIDs = []
                transformChunkID = -1   # Allocate IDs sequentially from 0.
                # For this test, allow arbitrarily chunking the primitives.
                primCounter = transformChunkLength
                transforms = []      # Accumulate transforms as a list of lists.

                # Initialize transforms with an identity matrix.
                # Transforms here are lists (or Numpy arrays) of 16 numbers.
                identity = ([1.0] + 4*[0.0]) * 3 + [1.0]
                pass
            for x in range(nSpheres):
                for y in range(nSpheres):
                    centers += [sphereLoc(x, y)]
                    
                    # Sphere radii progress from 3/4 to full size.
                    t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                    thisRad = radius * (.75 + t*.25)
                    radii += [thisRad]

                    # Colors progress from red to blue.
                    colors += [rainbow(t)]

                    # Transforms go into a texture memory image if needed.
                    # Per-primitive Transform IDs go into an attribute VBO.
                    if doTransforms:
                        primCounter = primCounter + 1
                        if primCounter >= transformChunkLength:
                            # Start a new chunk, allocating a transform matrix.
                            primCounter = 0
                            transformChunkID += 1
                            if 0: # 1
                                # Debug hack: Label mat[0,0] with the chunk ID.
                                # Vertex shader debug code shows these in blue.
                                # If viewed as geometry, it will be a slight
                                # stretch of the array in the X direction.
                                transforms += [
                                    [1.0+transformChunkID/100.0] + identity[1:]]
                            elif 0: # 1
                                # Debug hack: Fill mat with mat.element pattern.
                                transforms += [
                                    [transformChunkID +
                                     i/100.0 for i in range(16)]]
                            else:
                                transforms += [identity]
                                pass
                            pass
                        # All of the primitives in a chunk have the same ID.
                        transformIDs += [transformChunkID]
                        pass

                    continue
                continue
            test_spheres = GLSphereBuffer(centers, radii, colors, transformIDs)
            if doTransforms:
                print ("%d primitives in %d transform chunks of size <= %d" %
                       (nSpheres * nSpheres, len(transforms),
                        transformChunkLength))
                shader = drawing_globals.sphereShader
                shader.setupTransforms(transforms)
            pass
        else:
            shader = drawing_globals.sphereShader
            shader.configShader(glpane)

            # Update portions for animation.
            pulse = time() - last_time  # 0 to 1 in each second.

            # Test animating updates on 80% of the radii in 45% of the columns.

            # . 3.1 - Update radii Python array per-column, send to graphics RAM.
            #   -  2,500 (50x50)   spheres 55 FPS
            #   - 10,000 (100x100) spheres 35 FPS
            #   - 17,424 (132x132) spheres 22.2 FPS
            #   - 40,000 (200x200) spheres 12.4 FPS
            #   - 90,000 (300x300) spheres  6.0 FPS
            if testCase == 3.1:
                # Not buffered, send each column change.
                radius = .5
                margin = nSpheres/10
                for x in range(margin, nSpheres, 2):
                    radii = []
                    for y in range(margin, nSpheres-margin):
                        t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                        # Sphere radii progress from 3/4 to full size.
                        thisRad = radius * (.75 + t*.25)
                        phase = pulse + float(x+y)/nSpheres
                        radii += 8 * [thisRad-.1 + .1*sin(phase * 2*pi)]
                        continue
                    C_radii = numpy.array(radii, dtype=numpy.float32)
                    offset = x*nSpheres + margin
                    test_spheres.radii_vbo.update(offset * 8, C_radii)
                    continue
                pass

            # . 3.2 - Numpy buffered in C array, subscript assignments to C.
            #   -  2,500 (50x50)   spheres 48 FPS
            #   - 10,000 (100x100) spheres 17.4 FPS
            #   - 17,424 (132x132) spheres 11.2 FPS
            #   - 40,000 (200x200) spheres  5.5 FPS
            #   - 90,000 (300x300) spheres  2.5 FPS
            elif testCase == 3.2:
                # Buffered per-chunk at the C array level.
                radius = .5
                margin = nSpheres/10
                global C_array
                if C_array is None:
                    # Replicate.
                    C_array = numpy.zeros((8 * (nSpheres-(2*margin)),),
                                          dtype=numpy.float32)
                    pass
                for x in range(margin, nSpheres, 2):
                    count = 0
                    for y in range(margin, nSpheres-margin):
                        t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                        # Sphere radii progress from 3/4 to full size.
                        thisRad = radius * (.75 + t*.25)
                        phase = pulse + float(x+y)/nSpheres
                        C_array[count*8:(count+1)*8] = \
                            thisRad-.1 + .1*sin(phase * 2*pi)
                        count += 1
                        continue
                    offset = x*nSpheres + margin
                    test_spheres.radii_vbo.update(offset * 8, C_array)
                    continue
                pass

            # . 3.3 - updateRadii in Python array, copy via C to graphics RAM.
            #   -  2,500 (50x50)   spheres 57 FPS
            #   - 10,000 (100x100) spheres 32 FPS
            #   - 17,424 (132x132) spheres 20 FPS
            #   - 40,000 (200x200) spheres 10.6 FPS
            #   - 90,000 (300x300) spheres  4.9 FPS
            elif testCase == 3.3:
                # Buffered at the Python level, batch the whole-array update.
                radius = .5
                margin = nSpheres/10
                for x in range(margin, nSpheres, 2):
                    radii = []
                    for y in range(margin, nSpheres-margin):
                        t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                        # Sphere radii progress from 3/4 to full size.
                        thisRad = radius * (.75 + t*.25)
                        phase = pulse + float(x+y)/nSpheres
                        radii += [thisRad-.1 + .1*sin(phase * 2*pi)]
                        continue

                    test_spheres.updateRadii( # Update, but don't send yet.
                        x*nSpheres + margin, radii, send = False)
                    continue
                test_spheres.sendRadii()
                pass

            # Options: color = [0.0, 1.0, 0.0], transform_id = 1, radius = 1.0
            test_spheres.draw() 
        pass

    # NE1 with test toploop, separate sphere VBO/IBO box/shader draws (test case 4)
    # . 17,424 spheres (132x132 box/shader draw quads calls) 0.7 FPS
    elif testCase == 4:
        if test_ibo is None:
            print ("Test case 4, %d^2 spheres\n  %s." %
                   (nSpheres,
                    "Separate VBO/IBO shader/box buffer sphere calls, no DL"))

            # Collect transformed bounding box vertices and offset indices.
            # Start at the lower-left corner, offset so the whole pattern comes
            # up centered on the origin.
            cubeVerts = drawing_globals.shaderCubeVerts
            cubeIndices = drawing_globals.shaderCubeIndices

            C_indices = numpy.array(cubeIndices, dtype=numpy.uint32)
            test_ibo = GLBufferObject(
                GL_ELEMENT_ARRAY_BUFFER_ARB, C_indices, GL_STATIC_DRAW)
            test_ibo.unbind()

            C_verts = numpy.array(cubeVerts, dtype=numpy.float32)
            test_vbo = GLBufferObject(
                GL_ARRAY_BUFFER_ARB, C_verts, GL_STATIC_DRAW)
            test_vbo.unbind()
            pass
        else:
            drawing_globals.sphereShader.configShader(glpane)

            glEnableClientState(GL_VERTEX_ARRAY)

            test_vbo.bind()             # Vertex data comes from the vbo.
            glVertexPointer(3, GL_FLOAT, 0, None)

            drawing_globals.sphereShader.use(True)
            glDisable(GL_CULL_FACE)

            glColor3i(127, 127, 127)
            test_ibo.bind()             # Index data comes from the ibo.
            for x in range(nSpheres):
                for y in range(nSpheres):
                    # From drawsphere_worker_loop().
                    pos = start_pos + (x+x/10+x/100) * V(1, 0, 0) + \
                          (y+y/10+y/100) * V(0, 1, 0)
                    radius = .5

                    glPushMatrix()
                    glTranslatef(pos[0], pos[1], pos[2])
                    glScale(radius,radius,radius)

                    glDrawElements(GL_QUADS, 6 * 4, GL_UNSIGNED_INT, None)

                    glPopMatrix()
                    continue
                continue

            drawing_globals.sphereShader.use(False)
            glEnable(GL_CULL_FACE)

            test_ibo.unbind()
            test_vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
        pass

    # NE1 with test toploop, 
    # One DL around separate VBO/IBO shader/box buffer sphere calls (test case 5)
    # . 17,424 spheres (1 box/shader DL draw call) 9.2 FPS
    elif testCase == 5:
        if test_dl is None:
            print ("Test case 5, %d^2 spheres\n  %s." %
                   (nSpheres,
                    "One DL around separate VBO/IBO shader/box buffer sphere calls"))

            # Collect transformed bounding box vertices and offset indices.
            # Start at the lower-left corner, offset so the whole pattern comes
            # up centered on the origin.
            cubeVerts = drawing_globals.shaderCubeVerts
            cubeIndices = drawing_globals.shaderCubeIndices

            C_indices = numpy.array(cubeIndices, dtype=numpy.uint32)
            test_ibo = GLBufferObject(
                GL_ELEMENT_ARRAY_BUFFER_ARB, C_indices, GL_STATIC_DRAW)
            test_ibo.unbind()

            C_verts = numpy.array(cubeVerts, dtype=numpy.float32)
            test_vbo = GLBufferObject(
                GL_ARRAY_BUFFER_ARB, C_verts, GL_STATIC_DRAW)
            test_vbo.unbind()

            # Wrap a display list around the draws.
            test_dl = glGenLists(1)
            glNewList(test_dl, GL_COMPILE_AND_EXECUTE)

            glEnableClientState(GL_VERTEX_ARRAY)

            test_vbo.bind()             # Vertex data comes from the vbo.
            glVertexPointer(3, GL_FLOAT, 0, None)

            drawing_globals.sphereShader.use(True)
            glDisable(GL_CULL_FACE)

            glColor3i(127, 127, 127)
            test_ibo.bind()             # Index data comes from the ibo.
            for x in range(nSpheres):
                for y in range(nSpheres):
                    # From drawsphere_worker_loop().
                    pos = start_pos + (x+x/10+x/100) * V(1, 0, 0) + \
                          (y+y/10+y/100) * V(0, 1, 0)
                    radius = .5

                    glPushMatrix()
                    glTranslatef(pos[0], pos[1], pos[2])
                    glScale(radius,radius,radius)

                    glDrawElements(GL_QUADS, 6 * 4, GL_UNSIGNED_INT, None)

                    glPopMatrix()
                    continue
                continue

            drawing_globals.sphereShader.use(False)
            glEnable(GL_CULL_FACE)

            test_ibo.unbind()
            test_vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)

            glEndList()
        else:
            glColor3i(127, 127, 127)
            glCallList(test_dl)
            pass
        pass

    # NE1 with test toploop, 
    # N column DL's around VBO/IBO shader/box buffer sphere calls (test case 6)
    # .   2,500 (50x50)   spheres 58 FPS
    # .  10,000 (100x100) spheres 57 FPS
    # .  17,424 (132x132) spheres 56 FPS
    # .  40,000 (200x200) spheres 50 FPS
    # .  90,000 (300x300) spheres 28 FPS
    # . 160,000 (400x400) spheres 16.5 FPS
    # . 250,000 (500x500) spheres  3.2 FPS
    elif testCase == 6:
        if test_dls is None:
            print ("Test case 6, %d^2 spheres\n  %s." %
                   (nSpheres,
                    "N col DL's around VBO/IBO shader/box buffer sphere calls"))
            
            # Wrap n display lists around the draws (one per column.)
            test_dls = glGenLists(nSpheres) # Returns ID of first DL in the set.
            test_spheres = []
            for x in range(nSpheres):
                centers = []
                radius = .5
                radii = []
                colors = []
                # Each column is relative to its bottom sphere location.  Start
                # at the lower-left corner, offset so the whole pattern comes up
                # centered on the origin.
                start_pos = V(0, 0, 0)  # So it doesn't get subtracted twice.
                pos = sphereLoc(x, 0) - V(nSpheres/2.0, nSpheres/2.0, 0)
                for y in range(nSpheres):
                    centers += [sphereLoc(0, y)]
                    
                    # Sphere radii progress from 3/4 to full size.
                    t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                    thisRad = radius * (.75 + t*.25)
                    radii += [thisRad]

                    # Colors progress from red to blue.
                    colors += [rainbow(t)]
                    continue
                test_sphere = GLSphereBuffer(centers, radii, colors)
                test_spheres += [test_sphere]

                glNewList(test_dls + x, GL_COMPILE_AND_EXECUTE)
                glPushMatrix()
                glTranslatef(pos[0], pos[1], pos[2])

                test_sphere.draw()

                glPopMatrix()
                glEndList()
                continue
            pass
        else:
            shader = drawing_globals.sphereShader
            shader.configShader(glpane) # Turn the lights on.
            for x in range(nSpheres):
                glCallList(test_dls + x)
                continue
            pass
        pass

    # NE1 with test toploop, 
    # N column VBO sets of shader/box buffer sphere calls (test case 7)
    # .   2,500 (50x50)   spheres 50 FPS
    # .  10,000 (100x100) spheres 30.5 FPS
    # .  17,424 (132x132) spheres 23.5 FPS
    # .  40,000 (200x200) spheres 16.8 FPS
    # .  90,000 (300x300) spheres 10.8 FPS
    # . 160,000 (400x400) spheres  9.1 FPS
    # . 250,000 (500x500) spheres  7.3 FPS
    elif testCase == 7:
        if test_spheres is None:
            print ("Test case 7, %d^2 spheres\n  %s." %
                   (nSpheres, "Per-column VBO/IBO chunk buffers"))
            test_spheres = []
            for x in range(nSpheres):
                centers = []
                radius = .5
                radii = []
                colors = []
                for y in range(nSpheres):
                    centers += [sphereLoc(x, y)]
                    
                    # Sphere radii progress from 3/4 to full size.
                    t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                    thisRad = radius * (.75 + t*.25)
                    radii += [thisRad]

                    # Colors progress from red to blue.
                    colors += [rainbow(t)]
                    continue
                test_spheres += [GLSphereBuffer(centers, radii, colors)]
                continue
            pass
        else:
            shader = drawing_globals.sphereShader
            shader.configShader(glpane)
            for chunk in test_spheres:
                chunk.draw()
        pass

    # NE1 with test toploop, 
    # Short chunk VBO sets of shader/box buffer sphere calls (test case 8)
    # .     625 (25x25)   spheres 30 FPS,     79 chunk buffers of length 8.
    # .   2,500 (50x50)   spheres 13.6 FPS,  313 chunk buffers of length 8.
    # .  10,000 (100x100) spheres  6.4 FPS,  704 chunk buffers of length 8.
    # .  10,000 (100x100) spheres  3.3 FPS, 1250 chunk buffers of length 8.
    # .  17,424 (132x132) spheres  2.1 FPS, 2178 chunk buffers of length 8.
    # .   2,500 (50x50)   spheres 33.5 FPS,  105 chunk buffers of length 24.
    # .  17,424 (132x132) spheres  5.5 FPS,  726 chunk buffers of length 24.
    # Subcase 8.1: CSDLs in a DrawingSet.  (Initial pass-through version.)
    # .   2,500 (50x50)   spheres 36.5 FPS,  105 chunk buffers of length 24.
    # .   5,625 (75x75)   spheres 16.1 FPS,  235 chunk buffers of length 24.
    # .  10,000 (100x100) spheres  0.5 FPS?!, 414 chunk buffers of length 24.
    #      Has to be <= 250 chunks for constant memory transforms?
    # .  10,000 (100x100) spheres 11.8 FPS, 50 chunk buffers of length 200.
    #      After a minute of startup.
    # .  10,000 (100x100) spheres 9.3 FPS, 200 chunk buffers of length 50.
    #      After a few minutes of startup.
    # Subcase 8.2: CSDLs in a DrawingSet with transforms. (Pass-through.)
    # .  10,000 (100x100) spheres  11.5 FPS, 50 chunk buffers of length 200.
    # .  10,000 (100x100) spheres   FPS, 200 chunk buffers of length 50.
    elif int(testCase) == 8:
        doTransforms = False
        if test_spheres is None:
            # Setup.
            print ("Test case 8, %d^2 spheres\n  %s, length %d." %
                   (nSpheres, "Short VBO/IBO chunk buffers", chunkLength))
            if testCase == 8.1:
                print ("Sub-test 8.1, chunks are in CSDL's in a DrawingSet.")
                test_DrawingSet = DrawingSet()
            elif testCase == 8.2:
                print ("Sub-test 8.2, rotate with TransformControls.")
                test_DrawingSet = DrawingSet()
                doTransforms = True
                pass
            if doTransforms:
                # Provide several TransformControls to test separate action.
                global numTCs, TCs
                numTCs = 3
                TCs = [TransformControl() for i in range(numTCs)]
                pass

            def sphereCSDL(centers, radii, colors):
                if not doTransforms:
                    csdl = ColorSortedDisplayList() # Transformless.
                else:
                    # Test pattern for TransformControl usage - vertical columns
                    # of TC domains, separated by X coord of first center point.
                    # Chunking will be visible when transforms are changed.
                    xCoord = centers[0][0] - start_pos[0] # Negate centering X.
                    xPercent = (xCoord / 
                                (nSpheres + nSpheres/10 + nSpheres/100 - 1 + (nSpheres <= 1)))
                    xTenth = int(xPercent * 10 + .5)
                    csdl = ColorSortedDisplayList(TCs[xTenth % numTCs])
                    pass

                ColorSorter.start(csdl)
                for (color, center, radius) in zip(colors, centers, radii):
                    drawsphere(color, center, radius, DRAWSPHERE_DETAIL_LEVEL)
                    continue
                ColorSorter.finish()

                test_DrawingSet.addCSDL(csdl)
                return csdl
            chunkFn = {8: GLSphereBuffer, 8.1: sphereCSDL, 8.2: sphereCSDL}

            test_spheres = []
            radius = .5
            centers = []
            radii = []
            colors = []
            for x in range(nSpheres):
                for y in range(nSpheres):
                    centers += [sphereLoc(x, y)]
                    
                    # Sphere radii progress from 3/4 to full size.
                    t = float(x+y)/(nSpheres+nSpheres) # 0 to 1 fraction.
                    thisRad = radius * (.75 + t*.25)
                    radii += [thisRad]

                    # Colors progress from red to blue.
                    colors += [rainbow(t)]

                    # Put out short chunk buffers.
                    if len(centers) >= chunkLength:
                        test_spheres += [
                            chunkFn[testCase](centers, radii, colors) ]
                        centers = []
                        radii = []
                        colors = []
                    continue
                continue
            # Remainder fraction buffer.
            if len(centers):
                test_spheres += [chunkFn[testCase](centers, radii, colors)]
                pass
            print "%d chunk buffers" % len(test_spheres)
            pass
        else: # Run.
            shader = drawing_globals.sphereShader
            shader.configShader(glpane)
            if testCase == 8:
                for chunk in test_spheres:
                    chunk.draw()
                    continue
                pass
            elif testCase == 8.1:
                test_DrawingSet.draw()
            elif testCase == 8.2:
                # Animate TCs, rotating them slowly.
                slow = 10.0 # Seconds.
                angle = 2*pi * fmod(time(), slow) / slow
                # Leave the first one as identity, and rotate the others in
                # opposite directions around the X axis.
                TCs[1].identTranslateRotate(V(0, 0, 0), Q(V(1, 0, 0), angle * 2))
                TCs[2].identTranslateRotate(V(0, 0, 0), Q(V(1, 0, 0), -angle))

                test_DrawingSet.draw()
                pass

            pass
        pass

    glMatrixMode(GL_MODELVIEW)
    glFlush()
    
    if ALWAYS_GL_UPDATE:
        glpane.gl_update()
    
    if SPIN:
        ## glpane.quat += _SPINQUAT
            # that version has cumulative numerical error, causing an exception every few seconds:
            ##  File "/Nanorex/Working/trunk/cad/src/geometry/VQT.py", line 448, in __iadd__
            ##    self.normalize()
            ##  File "/Nanorex/Working/trunk/cad/src/geometry/VQT.py", line 527, in normalize
            ##    s = ((1.0 - w**2)**0.5) / length
            ##ValueError: negative number cannot be raised to a fractional power
        glpane.quat = glpane.quat + _SPINQUAT
        pass
    
    return

