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

from math import asin
from Numeric import sin,  pi
ONE_RADIAN = 180.0 / pi
HALF_PI  = pi/2.0
TWICE_PI = 2*pi

from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef

from drawer import drawArrowHead
from drawer import drawline
from drawer import drawPoint
from drawer import drawsphere

from geometry.VQT import norm, vlen, V, cross
from constants import white

def drawDnaRibbons(endCenter1,  
                   endCenter2,
                   basesPerTurn,
                   duplexRise, 
                   glpaneScale,
                   lineOfSightVector,
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
      - Should this method be moved to something like 'dna_drawer.py' ? 
    """
    #Should this method be moved to DnaLineMode class or a new dna_drawer.py?
    #Okay if it stays here in drawer.py    
    ribbonLength = vlen(endCenter1 - endCenter2)
    
    #Don't draw the vertical line (step) passing through the startpoint unless 
    #the ribbonLength is atleast equal to the duplexRise. 
    # i.e. do the drawing only when there are atleast two ladder steps. 
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
   
    #Following limits the arrowHead Size to the given value. When you zoom out, 
    #the rest of ladder drawing becomes smaller (expected) and the following
    #check ensures that the arrowheads are drawn proportinately. 
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
        # (i.e.peak to peak distance between consecutive crests)
              
    amplitude = peakDeviationFromCenter
    amplitudeVector = unitVectorAlongLadderStep * amplitude
              
    phase_angle_ribbon_1 = HALF_PI    
    theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1
    
    phase_angle_ribbon_2 = asin(-6.0/(amplitude))
    theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2    
    
    #Initialize ribbon1_point and ribbon2_point
    ribbon1_point = pointOnAxis + amplitudeVector * sin(theta_ribbon_1)    
    ribbon2_point = pointOnAxis - amplitudeVector * sin(theta_ribbon_2)
    
    #Constants for drawing the ribbon points as spheres.
    SPHERE_RADIUS = 1.0
    SPHERE_DRAWLEVEL = 2
    SPHERE_OPACITY = 1.0
    
    #Constants for drawing the second axis end point (as a sphere). 
    AXIS_ENDPOINT_SPHERE_COLOR = white
    AXIS_ENDPOINT_SPHERE_RADIUS = 1.0
    AXIS_ENDPOINT_SPHERE_DRAWLEVEL = 2
    AXIS_ENDPOINT_SPHERE_OPACITY = 0.5
    
    while x < ribbonLength:          
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       
        
        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point
        previous_ribbon2_point = ribbon2_point
        
        theta_ribbon_1 = (TWICE_PI * x / T) + phase_angle_ribbon_1
        theta_ribbon_2 = (TWICE_PI * x / T) - phase_angle_ribbon_2
        
        ribbon1_point = previousPointOnAxis + amplitudeVector * sin(theta_ribbon_1)
        ribbon2_point = previousPointOnAxis - amplitudeVector * sin(theta_ribbon_2)
        
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
            # an arrow head will be drawnfor y at x = 0 
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
            
        #Increament the pointOnAxis and x
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
    