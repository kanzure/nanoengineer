# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Draws the DNA ribbons where each strand is represented as a ribbon. DNA ribbons
are drawn as sine waves 

@author:    Ninad
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
It should support various display styles that match with the display of the 
actual model.
"""
import foundation.env as env

from math import asin, acos
from Numeric import sin, cos, pi
ONE_RADIAN = 180.0 / pi
HALF_PI  = pi/2.0
TWICE_PI = 2*pi

from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef

from graphics.drawing.drawers import drawArrowHead
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.drawers import drawPoint
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.drawers import drawtext

from geometry.VQT import norm, vlen, V, cross, Q
from geometry.VQT import orthodist, angleBetween
from utilities.constants import white, blue
from utilities.constants import diTrueCPK, diTUBES, diLINES

from Numeric import dot


from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key

#Constants for drawing the ribbon points as spheres.
SPHERE_RADIUS = 1.0
SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 1.0

#Constants for drawing the second axis end point (as a sphere). 
AXIS_ENDPOINT_SPHERE_COLOR = white
AXIS_ENDPOINT_SPHERE_RADIUS = 1.0
AXIS_ENDPOINT_SPHERE_DRAWLEVEL = 2
AXIS_ENDPOINT_SPHERE_OPACITY = 0.5


def draw_debug_text(glpane, point, text): #bruce 080422, should refile
    """
    """
    from geometry.VQT import V
    from utilities.constants import white, red
    
    if point is None:
        point = - glpane.pov
    # todo: randomize offset using hash of text
    offset = glpane.right * glpane.scale / 2.0 + \
             glpane.up    * glpane.scale / 2.0
               # todo: correct for aspect ratio, use min scale in each dimension
    offset2 = V( - offset[0], offset[1], 0.0 ) / 3.0
    drawline( white, point, point + offset, width = 2)
    drawline( white, point - offset2, point + offset2 )
    point_size = 12
    drawtext( text, red, point + offset, point_size, glpane )
    return

# This needs to include axial offset from caller.
def _compute_ribbon_point(origin,
                          basesPerTurn, 
                          duplexRise, 
                          unitVectorAlongLength,
                          unitVectorAlongLadderStep,
                          unitDepthVector,
                          peakDeviationFromCenter,
                          numberOfBasesDrawn , 
                          theta_offset
                          ):
    """
    """
    ##handedness = -1    
    ##theta_offset = 0.0
    #turn_angle = twistPerBase
    ##turn_angle = (handedness * 2 * pi) / basesPerTurn
    turn_angle = (2 * pi) / basesPerTurn
##    axial_offset = unitVectorAlongLength * duplexRise 
    cY = unitVectorAlongLadderStep 
    cZ = unitDepthVector

    theta = turn_angle * numberOfBasesDrawn + theta_offset # in radians
    y = cos(theta) * peakDeviationFromCenter 
    z = sin(theta) * peakDeviationFromCenter
##    vx = axial_offset # a Vector
    p = origin + y * cY + z * cZ
    return p

def drawDnaSingleRibbon(glpane,
                        endCenter1,  
                        endCenter2,
                        basesPerTurn,
                        duplexRise, 
                        # maybe: don't pass these three args, get from glpane
                        # instead? [bruce 080422 comment]
                        glpaneScale,
                        lineOfSightVector,
                        displayStyle,
                        ribbon1_start_point = None,
                        ribbon1_direction = None,
                        peakDeviationFromCenter = 9.5,
                        ribbonThickness = 2.0,
                        ribbon1Color = None, 
                        stepColor = None):
    
    """
    @see: drawDnaRibbons (method in this file)
    @see: DnaStrand_GraphicsMode._drawHandles()
    """

    if 0:
        # debug code, useful to see where the argument points are located
        # [bruce 080422]
        draw_debug_text(glpane, endCenter1, "endCenter1")
        draw_debug_text(glpane, endCenter2, "endCenter2")
        draw_debug_text(glpane, ribbon1_start_point, "ribbon1_start_point")
    
    #Try to match the rubberband display style as closely as possible to 
    #either the glpane's current display or the chunk display of the segment 
    #being edited. The caller should do the job of specifying the display style
    #it desires. As of 2008-02-20, this method only supports following display 
    #styles --Tubes, Ball and Stick, CPK and lines. the sphere radius 
    #for ball and stick or CPK is calculated approximately. 

    if displayStyle == diTrueCPK:
        SPHERE_RADIUS = 3.5
        ribbonThickness = 2.0
    elif displayStyle == diTUBES:
        SPHERE_RADIUS = 0.01
        ribbonThickness = 5.0
    elif displayStyle == diLINES:
        #Lines display and all other unsupported display styles
        SPHERE_RADIUS = 0.01
        ribbonThickness = 1.0
    else:
        #ball and stick display style. All other unsupported displays 
        #will be rendered in ball and stick display style
        SPHERE_RADIUS = 1.0
        ribbonThickness = 3.0
    
    if stepColor is None:
        stepColor = env.prefs[DarkBackgroundContrastColor_prefs_key] 

    ribbonLength = vlen(endCenter1 - endCenter2)

    #Don't draw the vertical line (step) passing through the startpoint unless 
    #the ribbonLength is at least equal to the duplexRise. 
    # i.e. do the drawing only when there are at least two ladder steps.
    # This prevents a 'revolving line' effect due to the single ladder step at
    # the first endpoint. It also means the dna duplex axis can be determined
    # below from the two endpoints.
    if ribbonLength < duplexRise:
        return

    unitVectorAlongLength = norm(endCenter2 - endCenter1)

    glDisable(GL_LIGHTING)
    ##glPushMatrix()
    ##glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2]) 
    ##pointOnAxis = V(0, 0, 0)
    pointOnAxis = endCenter1

    axial_shift = V(0.0, 0.0, 0.0) # might be changed below
    
    # [these might be discarded and recomputed just below;
    #  the case where they aren't is (and I think was) untested.
    #  -- bruce 080422 comment]
    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
    unitDepthVector = cross(unitVectorAlongLength, unitVectorAlongLadderStep)
       ## * -1 

    if ribbon1_start_point is not None:
        # [revise the meaning of these values to give the coordinate system
        #  with the right phase in which to draw the ribbon.
        #  bruce 080422 bugfix]
        vectorAlongLadderStep0 = ribbon1_start_point - endCenter1
            # note: this might not be perpendicular to duplex axis.
            # fix by subtracting off the parallel component.
            # but add the difference back to every point below.
        vectorAlongLadderStep = vectorAlongLadderStep0 - \
            dot( unitVectorAlongLength,
                 vectorAlongLadderStep0 ) * unitVectorAlongLength
        axial_shift = (vectorAlongLadderStep0 - vectorAlongLadderStep)
            # note: even using this, there is still a small glitch in the
            # location of the first drawn sphere vs. the ribbon point... don't
            # know why. [bruce 080422]
        unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
        unitDepthVector = cross(unitVectorAlongLength,
                                unitVectorAlongLadderStep) ## * -1 
        pass
    del vectorAlongLadderStep
    
    ###===
    #Following limits the arrowHead Size to the given value. When you zoom out, 
    #the rest of ladder drawing becomes smaller (expected) and the following
    #check ensures that the arrowheads are drawn proportionately. 
    # (Not using a 'constant' to do this as using glpaneScale gives better 
    #results)
    if glpaneScale > 40:
        arrowDrawingScale = 40
    else:
        arrowDrawingScale = glpaneScale

    #Formula .. Its a Sine Wave.
    # y(x) = A.sin(2*pi*f*x + phase_angle)  ------[1]
    # where --
    #      f = 1/T 
    #      A = Amplitude of the sine wave (or 'peak deviation from center') 
    #      y = y coordinate  of the sine wave -- distance is in Angstroms
    #      x = the x coordinate
    # phase_angle is computed for each wave. We know y at x =0. For example, 
    # for ribbon_1, , at x = 0, y = A. Putting these values in equation [1] 
    # we get the phase_angle.

    x = 0.0
    T =  duplexRise * basesPerTurn 
        # The 'Period' of the sine wave
        # (i.e. peak to peak distance between consecutive crests)

    numberOfBasesDrawn = 0
    theta_offset = 0

##    phase_angle_ribbon_1 = HALF_PI
##    theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1

    #Initialize ribbon1_point
    # [note: might not be needed, since identical to first point
    #  computed during loop, but present code uses it to initialize
    #  previous_ribbon1_point during loop [bruce 080422 comment]]
    ribbon1_point = _compute_ribbon_point(pointOnAxis + axial_shift,
                                         basesPerTurn, 
                                         duplexRise, 
                                         unitVectorAlongLength,
                                         unitVectorAlongLadderStep,
                                         unitDepthVector,
                                         peakDeviationFromCenter,
                                         numberOfBasesDrawn, 
                                         theta_offset
                                     )

    while x < ribbonLength:  
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       

        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point

        ribbon1_point = _compute_ribbon_point(pointOnAxis + axial_shift,
                                             basesPerTurn, 
                                             duplexRise, 
                                             unitVectorAlongLength,
                                             unitVectorAlongLadderStep,
                                             unitDepthVector,
                                             peakDeviationFromCenter,
                                             numberOfBasesDrawn, 
                                             theta_offset
                                         )
        
        
        if x == duplexRise and ribbon1_direction == -1:   
                # For ribbon_2 we need to draw an arrow head for y at x = 0. 
                # To do this, we need the 'next ribbon_2' point in order to 
                # compute the appropriate vectors. So when x = duplexRise, the 
                # previous_ribbon2_point is nothing but y at x = 0. 
                arrowLengthVector2  = norm(ribbon1_point -
                                           previous_ribbon1_point )
                arrowHeightVector2  = cross(-lineOfSightVector,
                                            arrowLengthVector2)
                drawArrowHead( ribbon1Color, 
                               previous_ribbon1_point,
                               arrowDrawingScale,
                               -arrowHeightVector2, 
                               -arrowLengthVector2)
        
        # Draw sphere over previous_ribbon1_point and not ribbon1_point.
        # This is so we don't draw a sphere over the last point on ribbon1
        # (instead, it is drawn as an arrowhead after the while loop).
        drawsphere(ribbon1Color, 
                   previous_ribbon1_point, 
                   SPHERE_RADIUS,
                   SPHERE_DRAWLEVEL,
                   opacity = SPHERE_OPACITY)
        
        drawline(stepColor, pointOnAxis, ribbon1_point)

        #Increment the pointOnAxis and x
        pointOnAxis = pointOnAxis + unitVectorAlongLength * duplexRise        
        x += duplexRise
        numberOfBasesDrawn += 1

        if previous_ribbon1_point:
            drawline(ribbon1Color, 
                     previous_ribbon1_point, 
                     ribbon1_point,
                     width = ribbonThickness,
                     isSmooth = True )
            arrowLengthVector1  = norm(ribbon1_point - previous_ribbon1_point)
            arrowHeightVector1 = cross(-lineOfSightVector, arrowLengthVector1)
            pass

        continue # while x < ribbonLength

    if ribbon1_direction == 1:
        #Arrow head for endpoint of ribbon_1. 
        drawArrowHead(ribbon1Color, 
                      ribbon1_point,
                      arrowDrawingScale,
                      arrowHeightVector1, 
                      arrowLengthVector1) 
        
    

    #The second axis endpoint of the dna is drawn as a transparent sphere. 
    #Note that the second axis endpoint is NOT NECESSARILY endCenter2 . In fact 
    # those two are equal only at the ladder steps. In other case (when the
    # ladder step is not completed), the endCenter1 is ahead of the 
    #'second axis endpoint of the dna' 
    drawsphere(AXIS_ENDPOINT_SPHERE_COLOR, 
               previousPointOnAxis, 
               AXIS_ENDPOINT_SPHERE_RADIUS,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)

    ##glPopMatrix()
    glEnable(GL_LIGHTING)
    return # from drawDnaSingleRibbon


def drawDnaRibbons(glpane,
                   endCenter1,  
                   endCenter2,
                   basesPerTurn,
                   duplexRise, 
                   glpaneScale,                   
                   lineOfSightVector,
                   displayStyle,
                   ribbon1_start_point = None,
                   ribbon2_start_point = None,
                   ribbon1_direction = None,
                   ribbon2_direction = None,
                   peakDeviationFromCenter = 9.5,
                   ribbonThickness = 2.0,
                   ribbon1Color = None, 
                   ribbon2Color = None,
                   stepColor = None):
    """
    Draw DNA ribbons where each strand is represented as a ribbon. DNA ribbons
    are drawn as sine waves with appropriate phase angles, with the phase
    angles computed in this method.

    @param endCenter1: Axis end 1
    @type  endCenter1: B{V}
    @param endCenter2: Axis end 2
    @type  endCenter2: B{V}
    @param basesPerTurn: Number of bases in a full turn.
    @type  basesPerTurn: float
    @param duplexRise: Center to center distance between consecutive steps
    @type  duplexRise: float
    @param glpaneScale: GLPane scale used in scaling arrow head drawing 
    @type  glpaneScale: float
    @param lineOfSightVector: Glpane lineOfSight vector, used to compute the 
                              the vector along the ladder step. 
    @type: B{V}    
    @param displayStyle: Rubberband display style (specified as an integer)
                         see comment in the method below. 
                         See also GLPane.displayMode.
    @type  displayStyle: int
    @param peakDeviationFromCenter: Distance of a peak from the axis 
                                    Also known as 'Amplitude' of a sine wave. 
    @type peakDeviationFromCenter: float
    @param ribbonThickness: Thickness of each of the the two ribbons
    @type ribbonThickness: float
    @param ribbon1Color: Color of ribbon1
    @param ribbon2Color: Color of ribbon2
    @see: B{DnaLineMode.Draw } (where it is used) for comments on color 
          convention

    TODO: as of 2008-04-22
      - Need more documentation
      -  This method is long mainly because of a number of custom drawing 
         See if that can be refactored e.g. methods like _drawRibbon1/strand1, 
         drawRibbon2 / strand2 etc. 
      - Further optimization / refactoring (low priority) 
    """

    #Try to match the rubberband display style as closely as possible to 
    #either the glpane's current display or the chunk display of the segment 
    #being edited. The caller should do the job of specifying the display style
    #it desires. As of 2008-02-20, this method only supports following display 
    #styles --Tubes, Ball and Stick, CPK and lines. the sphere radius 
    #for ball and stick or CPK is calculated approximately. 

    if displayStyle == diTrueCPK:
        SPHERE_RADIUS = 3.5
        ribbonThickness = 2.0
    elif displayStyle == diTUBES:
        SPHERE_RADIUS = 0.01
        ribbonThickness = 5.0
    elif displayStyle == diLINES:
        #Lines display and all other unsupported display styles
        SPHERE_RADIUS = 0.01
        ribbonThickness = 1.0
    else:
        #ball and stick display style. All other unsupported displays 
        #will be rendered in ball and stick display style
        SPHERE_RADIUS = 1.0
        ribbonThickness = 3.0
        
    



    ribbonLength = vlen(endCenter1 - endCenter2)

    #Don't draw the vertical line (step) passing through the startpoint unless 
    #the ribbonLength is at least equal to the duplexRise. 
    # i.e. do the drawing only when there are at least two ladder steps. 
    # This prevents a 'revolving line' effect due to the single ladder step at 
    # the first endpoint 
    if ribbonLength < duplexRise:
        return

    unitVectorAlongLength = norm(endCenter2 - endCenter1)
     
    ###===
    pointOnAxis = endCenter1

    axial_shift_1 = V(0.0, 0.0, 0.0) # might be changed below
    axial_shift_2 = V(0.0, 0.0, 0.0)
    
    # [these might be discarded and recomputed just below;
    #  the case where they aren't is (and I think was) untested.
    #  -- bruce 080422 comment]
    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
    unitDepthVector = cross(unitVectorAlongLength,
                            unitVectorAlongLadderStep) ## * -1 
    
    numberOfBasesDrawn = 0
    theta_offset = 0
    x = 0
    ###
    #Formula .. Its a Sine Wave.
    # y(x) = A.sin(2*pi*f*x + phase_angle)  ------[1]
    # where --
    #      f = 1/T 
    #      A = Amplitude of the sine wave (or 'peak deviation from center') 
    #      y = y coordinate  of the sine wave -- distance is in Angstroms
    #      x = the x coordinate
    # phase_angle is computed for each wave. We know y at x =0. For example, 
    # for ribbon_1, , at x = 0, y = A. Putting these values in equation [1] 
    # we get the phase_angle. Similarly, for ribbon_2, at x = 0, y = -6 
    # Putting these values will give use the phase_angle_2. 
    # Note that for ribbon2_point, we subtract the value of equation [1] from 
    # the point on axis. 

    x = 0.0
    T =  duplexRise * basesPerTurn 
        # The 'Period' of the sine wave
        # (i.e. peak to peak distance between consecutive crests)

    amplitude = peakDeviationFromCenter
    amplitudeVector = unitVectorAlongLadderStep * amplitude
    depthVector = unitDepthVector * amplitude
        # Note: to reduce the effect of perspective view on rung direction,
        # we could multiply depthVector by 0.1 or 0.01. But this would lessen
        # the depth realism of line/sphere intersections. [bruce 080216]
    ###
    

    if ribbon1_start_point is not None:
        ribbon1_point = ribbon1_start_point        
    else:
        if ribbon2_start_point is not None:
            ribbon1_point = _get_ribbon_point_on_other_ribbon(
                ribbon2_start_point,
                ribbon2_direction,
                endCenter1,
                unitVectorAlongLength) 
            
        else:
            phase_angle_ribbon_1 = HALF_PI    
            theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1
            
            #Initialize ribbon1_point and ribbon2_point
            ribbon1_point = pointOnAxis + \
                            amplitudeVector * sin(theta_ribbon_1) + \
                            depthVector * cos(theta_ribbon_1)
            ribbon1_direction = +1
            
    drawDnaSingleRibbon(glpane,
                        endCenter1,  
                        endCenter2,
                        basesPerTurn,
                        duplexRise, 
                        # maybe: don't pass these three args, get from glpane
                        # instead? [bruce 080422 comment]
                        glpaneScale,
                        lineOfSightVector,
                        displayStyle,
                        ribbon1_start_point = ribbon1_point,
                        ribbon1_direction = ribbon1_direction,
                        peakDeviationFromCenter = peakDeviationFromCenter,
                        ribbonThickness = ribbonThickness,
                        ribbon1Color = ribbon1Color, 
                        stepColor = stepColor)

    if ribbon2_start_point is not None:
        ribbon2_point = ribbon2_start_point        
    else:
        if ribbon1_start_point is not None:
            ribbon2_point = _get_ribbon_point_on_other_ribbon(
                ribbon1_start_point,
                ribbon1_direction,
                endCenter1,
                unitVectorAlongLength)
            
        else:
            phase_angle_ribbon_2 = asin(-6.0/(amplitude))
            theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2    
            ribbon2_point = pointOnAxis - \
                            amplitudeVector * sin(theta_ribbon_2) + \
                            depthVector * cos(theta_ribbon_2)
            ribbon2_direction = -1
            
    drawDnaSingleRibbon(glpane,
                        endCenter1,  
                        endCenter2,
                        basesPerTurn,
                        duplexRise, 
                        # maybe: don't pass these three args, get from glpane
                        # instead? [bruce 080422 comment]
                        glpaneScale,
                        lineOfSightVector,
                        displayStyle,
                        ribbon1_start_point = ribbon2_point,
                        ribbon1_direction = ribbon2_direction,
                        peakDeviationFromCenter = peakDeviationFromCenter,
                        ribbonThickness = ribbonThickness,
                        ribbon1Color = ribbon2Color, 
                        stepColor = stepColor)
    
    del vectorAlongLadderStep
    
    return

def _get_ribbon_point_on_other_ribbon(ribbon_start_point,
                                      ribbon_direction,
                                      endCenter1,
                                      unitVectorAlongLength):
    """
    Given a ribbon point, return the ribbon point on the other strand (ribbon).
    """
    other_ribbon_point = V(0, 0, 0)
    
    #Theta = 133 degree is the angle between strand1atom-axis-strand2atom
    #It is negative if the bond direction is negative (-1)
    theta = 133.0*pi/180            
    if ribbon_direction == -1:
        theta = -theta
        
    quat = Q(unitVectorAlongLength, theta)
    other_ribbon_point = quat.rot(ribbon_start_point - endCenter1)  + endCenter1
    
    return other_ribbon_point

# end

