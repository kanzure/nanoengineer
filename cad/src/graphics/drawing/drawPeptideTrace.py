# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

Creates a schematic "trace" drawing for PeptideBuilder.

@author:    Piotr
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
$Id:$
@license:   GPL
"""

import foundation.env as env
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef

from graphics.drawing.CS_draw_primitives import drawline, drawsphere
from graphics.drawing.drawers import drawPoint
from graphics.drawing.drawers import drawCircle


from geometry.VQT import norm, vlen, V, cross
from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key
from utilities.constants import blue, gray

from protein.commands.InsertPeptide.PeptideGenerator import get_unit_length

def drawPeptideTrace(alphaCarbonProteinChunk):
    """
    Draws a protein backbone trace using atoms stored in 
    I{alphaCarbonProteinChunk}.
    
    @param alphaCarbonProteinChunk: a special (temporary) chunk that contains 
                                    only the alpha carbon atoms in the peptide 
                                    backbone
    @param alphaCarbonProteinChunk: Chunk
    
    @see PeptideLine_GraphicsMode.Draw(), PeptideGenerator.make_aligned()
    """

    if alphaCarbonProteinChunk and alphaCarbonProteinChunk.atoms:
        last_pos = None
        atomitems = alphaCarbonProteinChunk.atoms.items()
        atomitems.sort() 
        alphaCarbonAtomsList = [atom for (key, atom) in atomitems] 
        
        for atom in alphaCarbonAtomsList:
            drawsphere(blue, atom.posn(), 0.2, 1)
            if last_pos:
                drawline(gray, last_pos, atom.posn(), width=2)
            last_pos = atom.posn()
            pass
        pass
    return

# drawPeptideTrace_orig is the original function for drawing a peptide
# trace. This function is deprecated and marked for removal. I'm keeping it
# here for reference for the time being.
# --Mark 2008-12-23
def drawPeptideTrace_orig(endCenter1,  
                          endCenter2,
                          phi, 
                          psi,
                          glpaneScale,
                          lineOfSightVector,
                          beamThickness = 2.0,
                          beam1Color = None, 
                          beam2Color = None,
                          stepColor  = None
                          ):
    """
    Draws the Peptide in a schematic display.
    
    @param endCenter1: Nanotube center at end 1
    @type endCenter1: B{V}
    
    @param endCenter2: Nanotube center at end 2
    @type endCenter2: B{V}
    
    @param phi: Peptide phi angle
    @type phi: float
    
    @param psi: Peptide psi angle
    @type psi: float
    
    @param glpaneScale: GLPane scale used in scaling arrow head drawing 
    @type glpaneScale: float
    
    @param lineOfSightVector: Glpane lineOfSight vector, used to compute the 
                              the vector along the ladder step. 
    @type: B{V} 
    
    @param beamThickness: Thickness of the two ladder beams
    @type beamThickness: float
    
    @param beam1Color: Color of beam1
    @param beam2Color: Color of beam2
    
    @see: B{DnaLineMode.Draw } (where it is used) for comments on color 
          convention

    @deprecated: Use drawPeptideTrace() instead.
    """   

    ladderWidth = 3.0
    
    ladderLength = vlen(endCenter1 - endCenter2)
    
    cntRise = get_unit_length(phi, psi)
    
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
    return
