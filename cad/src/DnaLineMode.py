# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
- The DNA rubberband line drawn as a ladder needs to be always parallel to 
  the screen 
- User Preferences for different rubberband line display styles 
"""

from LineMode import LineMode

from drawer import drawLadder
##from drawer import drawArrowHead

from constants import black, red, blue

# == GraphicsMode part

class DnaLine_GM( LineMode.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of DnaLineMode.
    @see: L{DnaLineMode} for more comments. 
    """    
    def __init__(self, command):
        """
        """
        LineMode.GraphicsMode_class.__init__(self, command)
      
    def Draw(self):
        """
        Draw the DNA rubberband line (a ladder representation)
        """
        #The rubberband line display needs to be a user preference.
        #Example: There could be 3 radio buttons in the duplex PM that allows 
        #you to draw the rubberband line as a simple line, a line with points 
        #that indicate duplexrise, a dna ladder with arrow heads. Drawing it as 
        #a ladder with arrow heads for the beams is the current implementation 
        # -Ninad 2007-10-30
        
        LineMode.GraphicsMode_class.Draw(self)
        if self.endPoint2 and self.endPoint1:              
            drawLadder(self.endPoint1,
                       self.endPoint2, 
                       self.command.duplexRise,
                       beam1Color = red,
                       beam2Color = blue,
                       stepColor = black    
                    )  
            ##if 0:
                ##drawArrowHead()               

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
    
    GraphicsMode_class = DnaLine_GM
        
    def setParams(self, params):
        assert len(params) == 2
        self.mouseClickLimit, self.duplexRise = params