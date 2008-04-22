# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Draws the DNA ribbons where each strand is represented as a ribbon. DNA ribbons
are drawn as sine waves 

@author:    Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
It should support various display styles that match with the display of the 
actual model.
"""

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

from graphics.drawing.drawer import drawArrowHead
from graphics.drawing.drawer import drawline
from graphics.drawing.drawer import drawPoint
from graphics.drawing.drawer import drawsphere

from geometry.VQT import norm, vlen, V, cross, Q
from geometry.VQT import orthodist, angleBetween
from utilities.constants import white, darkgreen, blue
from utilities.constants import diTrueCPK, diTUBES, diLINES

from Numeric import dot
#Constants for drawing the ribbon points as spheres.
SPHERE_RADIUS = 1.0
SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 1.0

#Constants for drawing the second axis end point (as a sphere). 
AXIS_ENDPOINT_SPHERE_COLOR = white
AXIS_ENDPOINT_SPHERE_RADIUS = 1.0
AXIS_ENDPOINT_SPHERE_DRAWLEVEL = 2
AXIS_ENDPOINT_SPHERE_OPACITY = 0.5


def drawDnaRibbons(endCenter1,  
                   endCenter2,
                   basesPerTurn,
                   duplexRise, 
                   glpaneScale,                   
                   lineOfSightVector,
                   displayStyle,
                   ribbon1_start_point = None,
                   ribbon2_start_point = None,
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
                         See also GLpane.displayStyle.
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

    TODO: 
      - See if a direct formula for a helix can be used. May not be necessary 
      -  This method is long mainly because of a number of custom drawing 
         See if that can be refactored e.g. methods like _drawRibbon1/strand1, 
         drawRibbon2 / strand2 etc. 
      - Further optimization / refactoring (low priority) 
    """

    #Try to match the rubberband display style as closely as possible to 
    #either the glapan's current display or the chunk display of the segment 
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

    glDisable(GL_LIGHTING) 
    glPushMatrix()
    glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2]) 
    pointOnAxis = V(0, 0, 0)

    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
    unitDepthVector = cross(unitVectorAlongLength, unitVectorAlongLadderStep) * -1 #bruce 080216

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


    if ribbon1_start_point is not None and ribbon2_start_point is not None:

        ribbon1_point = ribbon1_start_point
        ribbon2_point = ribbon2_start_point

        height_ribbon1, width1_junk = orthodist(endCenter1, 
                                                unitVectorAlongLadderStep, 
                                                ribbon1_point)

        height_ribbon2, width2_junk = orthodist(endCenter1, 
                                                unitVectorAlongLadderStep, 
                                                ribbon2_point )

        ##print "*** height_ribbon1 =", height_ribbon1
        ##print "***vlen(amplitudeVector) =", vlen(amplitudeVector)
        phase_angle_ribbon_1 = asin(height_ribbon1/vlen(amplitudeVector))

        ##print "***phase_angle_ribbon_1 =", phase_angle_ribbon_1*180/pi


        phase_angle_ribbon_2 = asin(height_ribbon2/vlen(amplitudeVector))

        ##print "*** height_ribbon2 =", height_ribbon2

        if phase_angle_ribbon_1*180.0/pi < 0:
            theta_ribbon_1 = (TWICE_PI * x / T) - phase_angle_ribbon_1
        else:
            theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1

        if phase_angle_ribbon_2*180.0/pi < 0:
            theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_1
        else:
            theta_ribbon_2 = (TWICE_PI * x / T) + phase_angle_ribbon_1

        ##theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1
        ##theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2




    else:              
        phase_angle_ribbon_1 = HALF_PI    
        theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1

        phase_angle_ribbon_2 = asin(-6.0/(amplitude))
        ##print "***phase_angle_ribbon_2 =", phase_angle_ribbon_2*180/pi
        theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2    

        #Initialize ribbon1_point and ribbon2_point
        ribbon1_point = pointOnAxis + amplitudeVector * sin(theta_ribbon_1) + \
                      depthVector * cos(theta_ribbon_1)
        ribbon2_point = pointOnAxis - amplitudeVector * sin(theta_ribbon_2) - \
                      depthVector * cos(theta_ribbon_2)



    while x < ribbonLength:          
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       

        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point
        previous_ribbon2_point = ribbon2_point

        theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1
        theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2

        ribbon1_point = pointOnAxis + amplitudeVector * sin(theta_ribbon_1) + \
                      depthVector * cos(theta_ribbon_1)
        ribbon2_point = pointOnAxis - amplitudeVector * sin(theta_ribbon_2) - \
                      depthVector * cos(theta_ribbon_2)


        #Use previous_ribbon1_point and not ribbon1_point. This ensures that 
        # the 'last point' on ribbon1 is not drawn as a sphere but is drawn as 
        #an arrowhead. (that arrow head is drawn later , after the while loop) 
        drawsphere(ribbon1Color, 
                   previous_ribbon1_point, 
                   SPHERE_RADIUS,
                   SPHERE_DRAWLEVEL,
                   opacity = SPHERE_OPACITY)       

        if x != 0.0:
            # For ribbon_2 , don't draw the first sphere (when x = 0) , instead 
            # an arrow head will be drawn for y at x = 0 
            # (see condition x == duplexRise )
            drawsphere(ribbon2Color, 
                       ribbon2_point, 
                       SPHERE_RADIUS,
                       SPHERE_DRAWLEVEL,
                       opacity = SPHERE_OPACITY)

        if x == duplexRise:   
            # For ribbon_2 we need to draw an arrow head for y at x = 0. 
            # To do this, we need the 'next ribbon_2' point in order to 
            # compute the appropriate vectors. So when x = duplexRise, the 
            # previous_ribbon2_point is nothing but y at x = 0. 
            arrowLengthVector2  = norm(ribbon2_point - previous_ribbon2_point )
            arrowHeightVector2  = cross(-lineOfSightVector, arrowLengthVector2)
            drawArrowHead( ribbon2Color, 
                           previous_ribbon2_point,
                           arrowDrawingScale,
                           -arrowHeightVector2, 
                           -arrowLengthVector2)

        #Increment the pointOnAxis and x
        pointOnAxis = pointOnAxis + unitVectorAlongLength * duplexRise        
        x += duplexRise

        if previous_ribbon1_point:
            drawline(ribbon1Color, 
                     previous_ribbon1_point, 
                     ribbon1_point,
                     width = ribbonThickness,
                     isSmooth = True )
            arrowLengthVector1  = norm(ribbon1_point - previous_ribbon1_point)
            arrowHeightVector1 = cross(-lineOfSightVector, arrowLengthVector1)

            drawline(ribbon2Color, 
                     previous_ribbon2_point, 
                     ribbon2_point,
                     width = ribbonThickness,
                     isSmooth = True )            

            drawline(stepColor, ribbon1_point, ribbon2_point)

    #Arrow head for endpoint of ribbon_1. 
    drawArrowHead(ribbon1Color, 
                  ribbon1_point,
                  arrowDrawingScale,
                  arrowHeightVector1, 
                  arrowLengthVector1) 

    #The second axis endpoint of the dna is drawn as a transparent sphere. 
    #Note that the second axis endpoint is NOT NECESSARILY endCenter2 . In fact 
    # those two are equal only at the ladder steps. In other case (when the
    # ladder step is not completed, the endCenter1 is ahead of the 
    #'second axis endpoint of the dna' 
    drawsphere(AXIS_ENDPOINT_SPHERE_COLOR, 
               previousPointOnAxis, 
               AXIS_ENDPOINT_SPHERE_RADIUS,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)


    glPopMatrix()
    glEnable(GL_LIGHTING)

def compute_ribbon_point(endCenter1,
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
    EXPERIMENTAL
    """
    ##handedness = -1    
    ##theta_offset = 0.0
    #turn_angle = twistPerBase
    ##turn_angle = (handedness * 2 * pi) / basesPerTurn
    turn_angle = (2 * pi) / basesPerTurn
    end1 = endCenter1
    axial_offset = unitVectorAlongLength * duplexRise 
    cY = unitVectorAlongLadderStep 
    cZ = unitDepthVector
    p0 = end1

    i = numberOfBasesDrawn
    radius = peakDeviationFromCenter

    theta = turn_angle * i + theta_offset # in radians
    y = cos(theta) * radius 
    z = sin(theta) * radius
    vx = axial_offset # a Vector
    ##p = p0 + vx + y * cY + z * cZ
    p = p0 + y * cY + z * cZ
    return p


def drawDnaSingleRibbon(endCenter1,  
                             endCenter2,
                             basesPerTurn,
                             duplexRise, 
                             glpaneScale,                   
                             lineOfSightVector,
                             displayStyle,
                             ribbon1_start_point = None,
                             peakDeviationFromCenter = 9.5,
                             ribbonThickness = 2.0,
                             ribbon1Color = None, 
                             stepColor = None):
    """
    EXPERIMENTAL. Doesn't work well. 
    @see: DnaStrand_GraphicsMode._drawHandles()
    """

    #Try to match the rubberband display style as closely as possible to 
    #either the glapan's current display or the chunk display of the segment 
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

    glDisable(GL_LIGHTING) 
    ##glPushMatrix()
    ##glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2]) 
    ##pointOnAxis = V(0, 0, 0)
    pointOnAxis = endCenter1

    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
    unitDepthVector = cross(unitVectorAlongLength, unitVectorAlongLadderStep) * -1 #bruce 080216

    #####################################################################
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

    numberOfBasesDrawn = 0
    theta_offset = 0

    if ribbon1_start_point is not None:

        height_ribbon1, width1_junk = orthodist(endCenter1, 
                                                unitVectorAlongLadderStep, 
                                                ribbon1_start_point)


        i = numberOfBasesDrawn
        radius = peakDeviationFromCenter

        y = height_ribbon1
        theta_temp = acos(y/radius)
        turn_angle = (2 * pi) / basesPerTurn

        theta_offset = theta_temp - turn_angle*i 

        ##print "~~~~~~~~~~~~~~~~~~~~"
        ##print "****height_ribbon1 = ", height_ribbon1
        ##print "***original theta offset = ", theta_temp*180/pi       
        ##print "***new thta_offset = ", theta_offset*180.0/pi


        ribbon1_point = compute_ribbon_point(pointOnAxis,
                                             basesPerTurn, 
                                             duplexRise, 
                                             unitVectorAlongLength,
                                             unitVectorAlongLadderStep,
                                             unitDepthVector,
                                             peakDeviationFromCenter,
                                             numberOfBasesDrawn,
                                             theta_offset
                                         )



    else:              
        phase_angle_ribbon_1 = HALF_PI    
        theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1


        #Initialize ribbon1_point and ribbon2_point
        ribbon1_point = compute_ribbon_point(pointOnAxis,
                                             basesPerTurn, 
                                             duplexRise, 
                                             unitVectorAlongLength,
                                             unitVectorAlongLadderStep,
                                             unitDepthVector,
                                             peakDeviationFromCenter,
                                             numberOfBasesDrawn, 
                                             theta_offset
                                         )



    #####################################################################


    while x < ribbonLength:          
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       

        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point


        ribbon1_point = compute_ribbon_point(pointOnAxis,
                                             basesPerTurn, 
                                             duplexRise, 
                                             unitVectorAlongLength,
                                             unitVectorAlongLadderStep,
                                             unitDepthVector,
                                             peakDeviationFromCenter,
                                             numberOfBasesDrawn, 
                                             theta_offset

                                         )


        #Use previous_ribbon1_point and not ribbon1_point. This ensures that 
        # the 'last point' on ribbon1 is not drawn as a sphere but is drawn as 
        #an arrowhead. (that arrow head is drawn later , after the while loop) 
        drawsphere(ribbon1Color, 
                   previous_ribbon1_point, 
                   SPHERE_RADIUS,
                   SPHERE_DRAWLEVEL,
                   opacity = SPHERE_OPACITY)       



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


    #Arrow head for endpoint of ribbon_1. 
    drawArrowHead(ribbon1Color, 
                  ribbon1_point,
                  arrowDrawingScale,
                  arrowHeightVector1, 
                  arrowLengthVector1) 

    #The second axis endpoint of the dna is drawn as a transparent sphere. 
    #Note that the second axis endpoint is NOT NECESSARILY endCenter2 . In fact 
    # those two are equal only at the ladder steps. In other case (when the
    # ladder step is not completed, the endCenter1 is ahead of the 
    #'second axis endpoint of the dna' 
    drawsphere(AXIS_ENDPOINT_SPHERE_COLOR, 
               previousPointOnAxis, 
               AXIS_ENDPOINT_SPHERE_RADIUS,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)


    ##glPopMatrix()
    glEnable(GL_LIGHTING)

######################START EXPERIMENTAL STUFF FOR BRUCE #######################

def EXPERIMENTAL_drawDnaSingleRibbon(endCenter1,  
                        endCenter2,
                        basesPerTurn,
                        duplexRise, 
                        glpaneScale,                   
                        lineOfSightVector,
                        displayStyle,
                        ribbon1_start_point = None,
                        peakDeviationFromCenter = 9.5,
                        ribbonThickness = 2.0,
                        ribbon1Color = None, 
                        stepColor = None):
    """
    EXPERIMENTAL. Doesn't work well. 
    @see: DnaStrand_GraphicsMode._drawHandles()
    """

    #Try to match the rubberband display style as closely as possible to 
    #either the glapan's current display or the chunk display of the segment 
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
    
    pointOnAxis = endCenter1

    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
    unitDepthVector = cross(unitVectorAlongLength, unitVectorAlongLadderStep) * -1 #bruce 080216

    #####################################################################
    #Following limits the arrowHead Size to the given value. When you zoom out, 
    #the rest of ladder drawing becomes smaller (expected) and the following
    #check ensures that the arrowheads are drawn proportionately. 
    # (Not using a 'constant' to do this as using glpaneScale gives better 
    #results)
    if glpaneScale > 40:
        arrowDrawingScale = 40
    else:
        arrowDrawingScale = glpaneScale

    x = 0.0
    amplitude = peakDeviationFromCenter
    amplitudeVector = unitVectorAlongLadderStep * amplitude
    depthVector = unitDepthVector * amplitude
        # Note: to reduce the effect of perspective view on rung direction,
        # we could multiply depthVector by 0.1 or 0.01. But this would lessen
        # the depth realism of line/sphere intersections. [bruce 080216]

    numberOfBasesDrawn = 0

    if ribbon1_start_point is not None:

        height_ribbon1, width1_junk = orthodist(endCenter1, 
                                                unitVectorAlongLadderStep, 
                                                ribbon1_start_point)        

        ribbon1_point = ribbon1_start_point  


    while x < ribbonLength:          
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       

        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point

        ribbon1_point = compute_ribbon_point(pointOnAxis,
                                             endCenter1,
                                             ribbon1_start_point,
                                             basesPerTurn, 
                                             duplexRise, 
                                             unitVectorAlongLength,
                                             numberOfBasesDrawn )


        #Use previous_ribbon1_point and not ribbon1_point. This ensures that 
        # the 'last point' on ribbon1 is not drawn as a sphere but is drawn as 
        #an arrowhead. (that arrow head is drawn later , after the while loop) 
        drawsphere(ribbon1Color, 
                   previous_ribbon1_point, 
                   SPHERE_RADIUS,
                   SPHERE_DRAWLEVEL,
                   opacity = SPHERE_OPACITY)       



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


    #Arrow head for endpoint of ribbon_1. 
    drawArrowHead(ribbon1Color, 
                  ribbon1_point,
                  arrowDrawingScale,
                  arrowHeightVector1, 
                  arrowLengthVector1) 

    #The second axis endpoint of the dna is drawn as a transparent sphere. 
    #Note that the second axis endpoint is NOT NECESSARILY endCenter2 . In fact 
    # those two are equal only at the ladder steps. In other case (when the
    # ladder step is not completed, the endCenter1 is ahead of the 
    #'second axis endpoint of the dna' 
    drawsphere(AXIS_ENDPOINT_SPHERE_COLOR, 
               previousPointOnAxis, 
               AXIS_ENDPOINT_SPHERE_RADIUS,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)

    glEnable(GL_LIGHTING)


def EXPERIMENTAL_compute_ribbon_point(pointOnAxis,
                         endCenter1,
                         ribbon1_start_point,
                         basesPerTurn, 
                         duplexRise, 
                         unitVectorAlongLength,                    
                         numberOfBasesDrawn                          
                         ): 
    
    #pointOnAxis and endCenter1 one of them is reduendent (may as well be a bug)
    #only pointOnAxis is probably what it needs.

    handedness = -1 #Right handed
    twistPerBase = (handedness * 2 * pi) / basesPerTurn

    a = V(0.0, 0.0, -1.0)
    # <a> is the unit vector pointing down the center axis of the default
    # DNA structure which is aligned along the Z axis.

    axis = cross(a, unitVectorAlongLength)
    # <axis> is the axis of rotation.

    theta_2 = angleBetween(a, unitVectorAlongLength)
    # <theta> is the angle (in degress) to rotate about <axis>.
    ##scalar = duplexRise * (numberOfBasesDrawn - 1) * 0.5
    scalar = -duplexRise * (numberOfBasesDrawn)
    rawOffset = unitVectorAlongLength * scalar


    if theta_2 == 0.0 or theta_2 == 180.0:
        axis = V(0, 1, 0)

    rot =  (pi / 180.0) * theta_2  # Convert to radians
    q_orient_1 = Q(axis, rot) # Quat for rotation delta.

    z = - numberOfBasesDrawn*duplexRise
    theta = numberOfBasesDrawn*twistPerBase
    def tfm(v, theta = theta, z1 = z):
        return _rotateTranslateXYZ(v, theta, z1)

    strand_point = V(0, 8.69, 0)
    axis_point = V(0, 0, 0)
    strand_point = tfm(strand_point)
    axis_point = tfm(axis_point)

    #All of the following needs to be reworked. It is WRONG. comment can be deleted
    #after fix -- Ninad 2008 -04- 21
    offset =  q_orient_1.rot(strand_point) - strand_point + rawOffset + pointOnAxis    
    axis_offset = q_orient_1.rot(axis_point) - axis_point + rawOffset + pointOnAxis

    strand_point += offset
    axis_point   += axis_offset

    if 0:
        strand_point =  q_orient_1.rot(strand_point)       
        axis_point = q_orient_1.rot(axis_point) 
        
    ########
    #For debug only
    drawsphere(darkgreen, 
               strand_point, 
               2.0,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)
        #########
    if 0:  
        ##vec_1 = (strand_point - axis_point)
        ##vec_2 = (ribbon1_start_point - pointOnAxis) 

        vec_1 = (strand_point - pointOnAxis)
        vec_2 = (ribbon1_start_point - endCenter1)

        drawline(blue, strand_point, pointOnAxis)
        drawline(darkgreen, ribbon1_start_point, endCenter1)
        drawsphere(darkgreen, 
                   ribbon1_start_point, 
                   2.0,
                   AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
                   opacity = AXIS_ENDPOINT_SPHERE_OPACITY)


        q_orient_2 = Q(vec_1, vec_2)

        if dot(vec_1, cross(vec_2, unitVectorAlongLength)) < 0:
            q_new2 = Q(unitVectorAlongLength, -q_orient_2.angle)
        else:     
            q_new2 = Q(unitVectorAlongLength, q_orient_2.angle) 


        rotOff =  q_new2.rot(strand_point) - strand_point + rawOffset + pointOnAxis
        strand_point += rotOff
        ##strand_point = q_new2.rot(strand_point)  

    return strand_point


def _rotateTranslateXYZ( inXYZ, theta, z):
    """
        Returns the new XYZ coordinate rotated by I{theta} and 
        translated by I{z}.

        @param inXYZ: The original XYZ coordinate.
        @type  inXYZ: V

        @param theta: The base twist angle.
        @type  theta: float

        @param z: The base rise.
        @type  z: float

        @return: The new XYZ coordinate.
        @rtype:  V
        """
    c, s = cos(theta), sin(theta)
    x = c * inXYZ[0] + s * inXYZ[1]
    y = -s * inXYZ[0] + c * inXYZ[1]
    return V(x, y, inXYZ[2] + z)

######################START EXPERIMENTAL STUFF FOR BRUCE #######################


