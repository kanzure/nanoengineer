# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
test_drawing.py -- Replaces GLPane.paintGL() to try various OpenGL rendering
models, determine whether the performance bottleneck is in OpenGL, Qt, or
somewhere else, and find a better alternative.

It simply renders an array of n^2 unit spheres, n by n.  Spin them around with
the NE1 rotate control, getting frames per second off the MacOS OpenGl Profiler
or the internal FPS counter (enable printFames.)

To turn it on, enable _testing_ at the beginning of graphics/widgets/glPane.py .
"""

# Which rendering mode: 1, 2, 3, 3.1, 3.2, 3.3, 4, 5, 6, 7
testCase = 6

# An array of nSpheres x nSpheres will be drawn, with divider lanes every 10 and 100.
# 10, 50, 100, 132, 200, 300, 400, 500...
nSpheres = 10

printFrames = True # False    # Prints frames-per-second if set.

from geometry.VQT import V, Q, A, norm, vlen, angleBetween

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_shaders import GLSphereBuffer

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
from math import sin, pi

test_csdl = None
test_dl = None
test_dls = None
test_ibo = None
test_vbo = None
test_spheres = None

frame_count = 0
last_frame = 0
last_time = time()

C_array = None

# Start at the lower-left corner, offset so the whole pattern comes
# up centered on the origin.
start_pos = V(-nSpheres/2.0, -nSpheres/2.0, 0)

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


def test_drawing(glpane):
    """
    When _testing_ is enabled at the beginning of graphics/widgets/glPane.py,
    file is loaded and GLPane.paintGL() calls the test_drawing() function
    instead of the usual body of paintGL().
    """
    global frame_count, last_frame, last_time
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

    # See below for test case descriptions and timings on a MacBook Pro.
    # The Qt event toploop in NE1 tops out at about 60 frames-per-second.

    # NE1 with test toploop, single CSDL per draw (test case 1)
    # . 17,424 spheres (132x132, through the color sorter) 4.8 FPS
    # . Level 2 spheres have 9 triangles x 20 faces, 162 distinct vertices, 
    #   visited on the average 2.3 times, giving 384 tri-strip vertices.
    # . 17,424 spheres is 6.7 million tri-strip vertices.  (6,690,816)
    if testCase == 1:
        if test_csdl is None:
            print ("Test case 1, %d^2 spheres\n  %s." %
                   (nSpheres, "ColorSorter"))

            test_csdl = ColorSortedDisplayList()
            ColorSorter.start(test_csdl)
            drawsphere([127, 127, 127], [0.0, 0.0, 0.0], .5, 2,
                       testloop = nSpheres)
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
            drawsphere_worker_loop(([0.0, 0.0, 0.0], .5, 2, nSpheres))
            glEndList()
            pass
        else:
            glColor3i(127, 127, 127)
            glCallList(test_dl)
        pass

    # NE1 with test toploop, one big chunk VBO/IBO of box quads (test case 3)
    # . 17,424 spheres (1 box/shader draw call) 43.7 FPS
    # . 17,424 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 57.7 FPS
    # . 40,00 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 56.7 FPS
    # . 90,00 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 52.7 FPS
    # . 160,00 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 41.4 FPS
    # . 250,00 spheres (1 box/shader draw call w/ rad/ctrpt attrs) 27.0 FPS
    elif int(testCase) == 3:
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
            centers = []
            radius = .5
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
                    continue
                continue
            test_spheres = GLSphereBuffer(centers, radii, colors)
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
            if testCase == 3.3:
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
                global start_pos
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
    elif int(testCase) == 7:
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

    glMatrixMode(GL_MODELVIEW)
    glFlush()
    return

