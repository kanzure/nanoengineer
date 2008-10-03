# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLSphereBuffer.py -- Subclass of GLPrimitiveBuffer for sphere primitives.

@author: Russ
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Originally written by Russ Fish; designed together with Bruce Smith.

================================================================

See design comments on:
* GL contexts, CSDLs and DrawingSet in DrawingSet.py
* TransformControl in TransformControl.py
* VBOs, IBOs, and GLPrimitiveBuffer in GLPrimitiveBuffer.py
* GLPrimitiveSet in GLPrimitiveSet in GLPrimitiveSet.py
"""

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.GLPrimitiveBuffer import GLPrimitiveBuffer, HunkBuffer

from geometry.VQT import V
import numpy

from OpenGL.GL import GL_QUADS

class GLSphereBuffer(GLPrimitiveBuffer):
    """
    Encapsulate VBO/IBO handles for a batch of spheres.
    See doc for common code in the base class, GLPrimitiveBuffer.

    Draws a bounding-box of quads to a custom sphere shader for each sphere.
    """
    def __init__(self):
        # Tell GLPrimitiveBuffer the drawing pattern for sphere VBOs/IBOs.
        super(GLSphereBuffer, self).__init__(
            GL_QUADS,
            drawing_globals.shaderCubeVerts,
            drawing_globals.shaderCubeIndices)

        # Per-vertex attribute hunk VBOs that are specific to the sphere shader.
        # Combine centers and radii into a 4-element vec4 attribute VBO.  (Each
        # attribute slot takes 4 floats, no matter how many of them are used.)
        self.ctrRadHunks = HunkBuffer("center_rad", self.nVertices, 4)
        self.hunkBuffers += [self.ctrRadHunks]

        return

    def addSpheres(self, centers, radii, colors, transform_ids):
        """
        Sphere centers must be a list of VQT points.

        Lists or single values may be given for the radii, colors, and
        transform_ids of the spheres.  A single value is replicated for the
        whole batch.

        Colors are tuples of components: (R, G, B) or (R, G, B, A).

        transform_ids may be None for centers in global modeling coordinates.

        The lengths of centers, radii, colors and transform_id lists must match.

        The return value is a list of allocated primitive IDs for the spheres.
        """
        nSpheres = len(centers)

        if type(radii) == type([]):
            assert len(radii) == nSpheres
        else:
            radii = nSpheres * [float(radii)]
            pass
        
        if type(colors) == type([]):
            assert len(colors) == nSpheres
            colors = [self.color4(colors) for color in colors]
        else:
            colors = nSpheres * [self.color4(colors)]
            pass

        if type(transform_ids) == type([]):
            assert len(transform_ids) == nSpheres
        else:
            if transform_ids is None:
                 # This disables transform logic in the shader.
                transform_ids = 0
                pass
            transform_ids = nSpheres * [transform_ids]
            pass

        newIDs = self.newPrimitives(nSpheres)
        for (newID, ctr, radius, color, transform_id) in \
            zip(newIDs, centers, radii, colors, transform_ids):

            # Combine the center and radius into one vertex attribute.
            ctrRad = V(ctr[0], ctr[1], ctr[2], radius)
            self.ctrRadHunks.setData(newID, ctrRad)
            self.colorHunks.setData(newID, color)
            self.transform_id_Hunks.setData(newID, transform_id)
            continue

        return newIDs

    pass # End of class GLSphereBuffer.
