# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GLCylinderBuffer.py -- Subclass of GLPrimitiveBuffer for cylinder primitives.

@author: Russ
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:
Originally written by Russ Fish; designed together with Bruce Smith.

Russ 090118: Cloned from GLSphereBuffer.py .

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

class GLCylinderBuffer(GLPrimitiveBuffer):
    """
    Encapsulate VBO/IBO handles for a batch of cylinders.
    See doc for common code in the base class, GLPrimitiveBuffer.

    Draws a bounding-box of quads (or a single billboard quad) to a custom
    cylinder shader for each cylinder, along with control attribute data.
    """
    def __init__(self):
        # Tell GLPrimitiveBuffer the drawing pattern for cylinder VBOs/IBOs.
        shader = drawing_globals.cylinderShader
        super(GLCylinderBuffer, self).__init__(
            shader, GL_QUADS,
            drawing_globals.cylinderBillboardVerts,
            drawing_globals.cylinderBillboardIndices)

        # Per-vertex attribute hunk VBOs that are specific to the cylinder
        # shader.  Combine endpoints and radii into two vec4's.  It would be
        # nicer to use a twice-4-element mat2x4 attribute VBO, but it would have
        # to be sent as two attribute slots anyway, because OpenGL only allows
        # "size" to be 1 to 4 in glVertexAttribPointer.
        nVerts = self.nVertices
        self.endptRad0Hunks = HunkBuffer(shader, "endpt_rad_0",
                                         self.nVertices, 4)
        self.endptRad1Hunks = HunkBuffer(shader, "endpt_rad_1",
                                         self.nVertices, 4)
        self.hunkBuffers += [self.endptRad0Hunks, self.endptRad1Hunks] 

        return

    def addCylinders(self, endpts, radii, colors, transform_ids, glnames):
        """
        Cylinder endpts must be a list of tuples of 2 VQT points.

        Lists or single values may be given for the attributes of the cylinders
        (radii, colors, transform_ids, and selection glnames).  A single value
        is replicated for the whole batch.  The lengths of attribute lists must
        match the endpoints list.

        radii and colors are required.  Cylinder radii are single numbers
        (untapered) or tuples of 2 numbers (tapered).  Colors are tuples of
        components: (R, G, B) or (R, G, B, A).

        transform_ids may be None for endpts in global modeling coordinates.

        glnames may be None if mouseover drawing will not be done.  glnames are
        32-bit integers, allocated sequentially and associated with selected
        objects in a global object dictionary

        The return value is a list of allocated primitive IDs for the cylinders.
        """
        nCylinders = len(endpts)

        for endptTuple in endpts:
            assert type(endptTuple) == type(())
            assert len(endptTuple) == 2

        if type(radii) == type(()):
            # A tuple of two numbers.
            assert len(radii) == 2
            radii = (float(radii[0]), float(radii[1]))
        elif type(radii) != type([]):
            # Not a list, better be a single number.
            radii = (float(radii), float(radii))

        if type(radii) == type([]):
            assert len(radii) == nCylinders
        else:
            radii = nCylinders * [radii]
            pass
        
        if type(colors) == type([]):
            assert len(colors) == nCylinders
            colors = [self.color4(colors) for color in colors]
        else:
            colors = nCylinders * [self.color4(colors)]
            pass

        if type(transform_ids) == type([]):
            assert len(transform_ids) == nCylinders
        else:
            if transform_ids is None:
                 # This bypasses transform logic in the shader for this cylinder.
                transform_ids = -1
                pass
            transform_ids = nCylinders * [transform_ids]
            pass

        if type(glnames) == type([]):
            assert len(glnames) == nCylinders
        else:
            if glnames is None:
                glnames = 0
                pass
            glnames = nCylinders * [glnames]
            pass

        newIDs = self.newPrimitives(nCylinders)
        for (newID, endpt2, radius2, color, transform_id, glname) in \
            zip(newIDs, endpts, radii, colors, transform_ids, glnames):

            # Combine each center and radius into one vertex attribute.
            endptRad0 = [V(endpt2[0][0], endpt2[0][1], endpt2[0][2], radius2[0])]
            endptRad1 = [V(endpt2[1][0], endpt2[1][1], endpt2[1][2], radius2[1])]
            self.endptRad0Hunks.setData(newID, endptRad0)
            self.endptRad1Hunks.setData(newID, endptRad1)
            self.colorHunks.setData(newID, color)
            self.transform_id_Hunks.setData(newID, transform_id)
            # Break the glname into RGBA pixel color components, 0.0 to 1.0 .
            # (Per-vertex attributes are all multiples (1-4) of Float32.)
            rgba = [(glname >> bits & 0xff) / 255.0 for bits in range(24,-1,-8)] 
            self.glname_color_Hunks.setData(newID, rgba)
            continue

        return newIDs

    pass # End of class GLCylinderBuffer.
