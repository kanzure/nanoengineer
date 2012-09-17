# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Draws the CNT in a ladder display.

@author:    Ninad, Mark
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""
import foundation.env as env
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef

from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.drawers import drawPoint
from graphics.drawing.drawers import drawCircle

from geometry.VQT import norm, vlen, V, cross
from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key

def drawNanotubeLadder(endCenter1,
                  endCenter2,
                  cntRise,
                  glpaneScale,
                  lineOfSightVector,
                  ladderWidth = 6.8, # default diameter for 5x5 CNT
                  beamThickness = 2.0,
                  beam1Color = None,
                  beam2Color = None,
                  stepColor = None
                  ):
    """
    Draws the CNT in a ladder display.

    @param endCenter1: Nanotube center at end 1
    @type endCenter1: B{V}

    @param endCenter2: Nanotube center at end 2
    @type endCenter2: B{V}

    @param cntRise: Center to center distance between consecutive steps
    @type cntRise: float

    @param glpaneScale: GLPane scale used in scaling arrow head drawing
    @type glpaneScale: float

    @param lineOfSightVector: Glpane lineOfSight vector, used to compute the
                              the vector along the ladder step.
    @type: B{V}

    @param ladderWidth: width of the ladder
    @type ladderWidth: float

    @param beamThickness: Thickness of the two ladder beams
    @type beamThickness: float

    @param beam1Color: Color of beam1
    @param beam2Color: Color of beam2

    @see: B{DnaLineMode.Draw } (where it is used) for comments on color
          convention
    """

    ladderLength = vlen(endCenter1 - endCenter2)

    # Don't draw the vertical line (step) passing through the startpoint unless
    # the ladderLength is atleast equal to the cntRise.
    # i.e. do the drawing only when there are atleast two ladder steps.
    # This prevents a 'revolving line' effect due to the single ladder step at
    # the first endpoint
    if ladderLength < cntRise:
        return

    unitVector = norm(endCenter2 - endCenter1)

    if beam1Color is None:
        beam1Color = env.prefs[DarkBackgroundContrastColor_prefs_key]

    if beam2Color is None:
        beam2Color = env.prefs[DarkBackgroundContrastColor_prefs_key]

    if stepColor is None:
        stepColor = env.prefs[DarkBackgroundContrastColor_prefs_key]


    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2])
    pointOnAxis = V(0, 0, 0)

    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVector)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)

    ladderBeam1Point = pointOnAxis + \
                       unitVectorAlongLadderStep * 0.5 * ladderWidth
    ladderBeam2Point = pointOnAxis - \
                       unitVectorAlongLadderStep * 0.5 * ladderWidth

    # Following limits the arrowHead Size to the given value. When you zoom out,
    # the rest of ladder drawing becomes smaller (expected) and the following
    # check ensures that the arrowheads are drawn proportinately.  (Not using a
    # 'constant' to do this as using glpaneScale gives better results)
    if glpaneScale > 40:
        arrowDrawingScale = 40
    else:
        arrowDrawingScale = glpaneScale

    x = 0.0
    while x < ladderLength:
        drawPoint(stepColor, pointOnAxis)
        drawCircle(stepColor, pointOnAxis, ladderWidth * 0.5, unitVector)

        previousPoint = pointOnAxis
        previousLadderBeam1Point = ladderBeam1Point
        previousLadderBeam2Point = ladderBeam2Point

        pointOnAxis = pointOnAxis + unitVector * cntRise		
        x += cntRise

        ladderBeam1Point = previousPoint + \
                           unitVectorAlongLadderStep * 0.5 * ladderWidth
        ladderBeam2Point = previousPoint - \
                           unitVectorAlongLadderStep * 0.5 * ladderWidth

        if previousLadderBeam1Point:
            drawline(beam1Color,
                     previousLadderBeam1Point,
                     ladderBeam1Point,
                     width = beamThickness,
                     isSmooth = True )

            drawline(beam2Color,
                     previousLadderBeam2Point,
                     ladderBeam2Point,
                     width = beamThickness,
                     isSmooth = True )

            #drawline(stepColor, ladderBeam1Point, ladderBeam2Point)

    glPopMatrix()
    glEnable(GL_LIGHTING)
