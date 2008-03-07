# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
- User Preferences for different rubberband line display styles 
"""

from LineMode import LineMode

from graphics.drawing.drawDnaLadder import drawDnaLadder
from graphics.drawing.drawDnaRibbons import drawDnaRibbons

from constants import black, darkred, blue, white

# == GraphicsMode part

class DnaLine_GM( LineMode.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of DnaLineMode.
    @see: L{DnaLineMode} for more comments. 
    @see: DnaDuplex_EditCommand where this is used as a GraphicsMode class.
          The default command part in this file is a Default class
          implementation  of self.command (see class DnaLineMode)          
    """    
    # The following valuse are used in drawing the 'sphere' that represent the 
    #first endpoint of the line. See LineMode.Draw for details. 
    endPoint1_sphereColor = white 
    endPoint1_sphereOpacity = 1.0
    
    text = ''
    
    def __init__(self, command):
        """
        """
        LineMode.GraphicsMode_class.__init__(self, command)
    
    def leftUp(self, event):
        """
        Left up method
        """
        if  self.command.mouseClickLimit is None:
            if len(self.command.mouseClickPoints) == 2:
                self.endPoint2 = None
                                
                self.command.createStructure()
                #DISABLED AS OF 2008-01-11. (Implementation changed --
                #See DnaDuplex_EditCommand.createStructure for new 
                #implementaion)
                ##self.command.callback_addSegments()
                
                self.glpane.gl_update()            
            return
    
    def snapLineEndPoint(self):
        """
        Snap the line to the specified constraints. 
        To be refactored and expanded. 
        @return: The new endPoint2 i.e. the moving endpoint of the rubberband 
                 line . This value may be same as previous or snapped so that it
                 lies on a specified vector (if one exists)                 
        @rtype: B{A}
        """
                
        if self.command.callbackForSnapEnabled() == 1:
            endPoint2  = LineMode.GraphicsMode_class.snapLineEndPoint(self)
        else:
            endPoint2 = self.endPoint2
            
        return endPoint2
        
      
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
        if self.endPoint2 is not None and \
           self.endPoint1 is not None: 
            
            #Draw the ladder. 
            #Convention:
            # The red band(beam) of the 
            # ladder is always the 'leading edge' of the ladder. i.e. the red 
            # band arrow head is always at the moving end of the mouse 
            #(endpoint2). 
            
            # A General Note/ FYI to keep in mind: 
            # Consider a double stranded DNA and focus on the 'twin peaks' 
            #(say, two consecutive helices in the middle of the dna duplex)
            # From the "mountain" with twin peaks that is the minor groove,
            # the DNA flows downhill 5' to 3' 
            # Or in other words, 
            # - For the 'mountain peak' on the right , 
            #    the 5' to 3' flows downhill, from left to right. 
            # - For the 'mountain peak' on the left, 
            #   the 3' to 5' flows downhill, from right to left
            #            
            # Thus, the red beam of the ladder, can either become the 
            # 'left mountain' or the 'right mountain' depending on the 
            # orientation while drawing the ladder
            
            if self.command.callback_rubberbandLineDisplay() == 'Ladder':
                #Note there needs to be a radio button to switch on the 
                # rubberband ladder display for a dna line. At the moment it is 
                # disabled and is superseded by the ribbons ruberband display. 
                drawDnaLadder(self.endPoint1,
                              self.endPoint2, 
                              self.command.duplexRise,
                              self.glpane.scale,
                              self.glpane.lineOfSight,
                              beamThickness = 4.0,
                              beam1Color = darkred,
                              beam2Color = blue,
                              stepColor = black )
            elif self.command.callback_rubberbandLineDisplay() ==  'Ribbons':  
                #Default dna rubberband line display style       
                drawDnaRibbons(self.endPoint1,
                               self.endPoint2, 
                               self.command.basesPerTurn,
                               self.command.duplexRise,
                               self.glpane.scale,
                               self.glpane.lineOfSight,
                               self.glpane.displayMode,
                               ribbonThickness = 4.0,
                               ribbon1Color = darkred,
                               ribbon2Color = blue,
                               stepColor = black )   
            else:
                pass
            
            #Draw the text next to the cursor that gives info about 
            #number of base pairs etc
            if self.command:
                self.text = self.command.callbackMethodForCursorTextString(
                    self.endPoint1, 
                    self.endPoint2)
                self.glpane.renderTextNearCursor(self.text)
        

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
    @see: DnaDuplex_EditCommand.provideParamsForTemporaryMode
    @see: DnaDuplex_EditCommand.getCursorTextForTemporaryMode
    
    NOTE: [2008-01-11]
    The default DnaLineMode (command) part is not used as of 2008-01-11
    Instead, the interested commands use its GraphicsMode class. 
    However, its still possible to use and implement the default command 
    part. (The old implementation of generating Dna using endpoints of a 
    line used this default command class (DnaLineMode). so the method in this
    class  such as self.createStructure does nothing . 
    @see: DnaDuplex_EditCommand where the GraphicsMode class of this command is 
          used
        
    """
    
    # class constants    
    commandName = 'DNA_LINE_MODE'    
    featurename = "DNA Line Mode"
        # (This featurename is sometimes user-visible,
        #  but is probably not useful. See comments in LineMode
        #  for more info and how to fix. [bruce 071227])
    
            
    GraphicsMode_class = DnaLine_GM
        
    def setParams(self, params):
        assert len(params) == 5
        self.mouseClickLimit, \
            self.duplexRise, \
            self.callbackMethodForCursorTextString, \
            self.callbackForSnapEnabled, \
            self.callback_rubberbandLineDisplay = params
    
    def createStructure(self):
        """
        Does nothing. 
        @see: DnaLineMode_GM.leftUp
        @see: comment at the beginning of the class
        
        """
        pass
    
    
    