# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from LineMode import LineMode

from drawer import drawline, drawsphere
from constants import black

from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix


# == GraphicsMode part

class DnaLine_GM( LineMode.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of DnaLineMode.
    @see: L{DnaLineMode} for more comments. 
    """    
      
    def Draw_NOT_IMPLEMENTED_YET(self):
        """
        """
        LineMode.GraphicsMode_class.Draw(self)
        #if 0:
            #if self.currentPoint:
                #glPushMatrix()  
                #if self.movingPoint:
                    #drawsphere(STARTPOINT_SPHERE_COLOR, 
                               #self.movingPoint, 
                               #STARTPOINT_SPHERE_RADIUS,
                               #STARTPOINT_SPHERE_DRAWLEVEL,
                               #opacity = STARTPOINT_SPHERE_OPACITY
                               #)            
                #drawline(black, 
                     #self.movingPoint, 
                     #self.currentPoint, 
                     #dashEnabled = True)            
                #glPopMatrix()
    
    

# == Command part

class DnaLineMode(LineMode): 
    """
    Encapsulates the LineMode functionality.
    Example:
    User is working in selectMolsMode, Now he enters a temporary mode 
    called DnaLine mode, where, he clicks two points in the 3Dworkspace 
    and expects to create a DNA using the points he clicked as endpoints. 
    Internally, the program returns to the previous mode after two clicks. 
    The temporary mode sends this information to the method defined in 
    the previous mode called acceptParamsFromTemporaryMode and then the
    previous mode (selectMolsMode) can use it further to create a dna 
    @see: L{LineMode}
    @see: selectMolsMode.provideParamsForTemporaryMode comments for 
          related  TODOs.
    """
    
    # class constants
    
    modename = 'DNA_LINE_MODE'
    default_mode_status_text = ""
    hover_highlighting_enabled = True
    
    mouseClickPoints = []
    GraphicsMode_class = DnaLine_GM