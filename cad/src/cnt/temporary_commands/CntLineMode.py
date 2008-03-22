# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad, Mark
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
- User Preferences for different rubberband line display styles 
"""

from temporary_commands.LineMode import LineMode

from graphics.drawing.drawCntLadder import drawCntLadder

from utilities.constants import gray, black, darkred, blue, white

# == GraphicsMode part

class CntLine_GM( LineMode.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of CntLineMode.
    @see: L{CntLineMode} for more comments. 
    @see: InsertCnt_EditCommand where this is used as a GraphicsMode class.
          The default command part in this file is a Default class
          implementation  of self.command (see class CntLineMode)          
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
                #See InsertCnt_EditCommand.createStructure for new 
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
        Draw the CNT rubberband line (a ladder representation)
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
            
            #Draw the chain. 
            
            if self.command.callback_rubberbandLineDisplay() == 'Ladder':
                #Note there needs to be a radio button to switch on the 
                # rubberband ladder display for a dna line. At the moment it is 
                # disabled and is superseded by the ribbons ruberband display. 
                drawCntLadder(self.endPoint1,
                              self.endPoint2, 
                              self.command.getCntRise(),
                              self.glpane.scale,
                              self.glpane.lineOfSight,
                              ladderWidth = self.command.getCntDiameter(),
                              beamThickness = 4.0,
                              beam1Color = gray,
                              beam2Color = gray,
                              stepColor = black )
            elif self.command.callback_rubberbandLineDisplay() ==  'Ribbons':  
                #Default dna rubberband line display style       
                drawCntRibbons(self.endPoint1,
                               self.endPoint2, 
                               self.command.basesPerTurn,
                               self.command.cntRise,
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
class CntLineMode(LineMode): 
    """
    Encapsulates the LineMode functionality.
    Example:
    User is working in selectMolsMode, Now he enters a temporary mode 
    called CntLine mode, where, he clicks two points in the 3Dworkspace 
    and expects to create a CNT using the points he clicked as endpoints. 
    Internally, the program returns to the previous mode after two clicks. 
    The temporary mode sends this information to the method defined in 
    the previous mode called acceptParamsFromTemporaryMode and then the
    previous mode (selectMolsMode) can use it further to create a dna 
    @see: L{LineMode}
    @see: selectMolsMode.provideParamsForTemporaryMode comments for 
          related  TODOs.
    @see: InsertCnt_EditCommand.provideParamsForTemporaryMode
    @see: InsertCnt_EditCommand.getCursorTextForTemporaryMode
    
    NOTE: [2008-01-11]
    The default CntLineMode (command) part is not used as of 2008-01-11
    Instead, the interested commands use its GraphicsMode class. 
    However, its still possible to use and implement the default command 
    part. (The old implementation of generating Cnt using endpoints of a 
    line used this default command class (CntLineMode). so the method in this
    class  such as self.createStructure does nothing . 
    @see: InsertCnt_EditCommand where the GraphicsMode class of this command is 
          used
        
    """
    
    # class constants    
    commandName = 'CNT_LINE_MODE'    
    featurename = "CNT Line Mode"
        # (This featurename is sometimes user-visible,
        #  but is probably not useful. See comments in LineMode
        #  for more info and how to fix. [bruce 071227])
    
            
    GraphicsMode_class = CntLine_GM
        
    def setParams(self, params):
        assert len(params) == 5
        self.mouseClickLimit, \
            self.cntRise, \
            self.callbackMethodForCursorTextString, \
            self.callbackForSnapEnabled, \
            self.callback_rubberbandLineDisplay = params
    
    def createStructure(self):
        """
        Does nothing. 
        @see: CntLineMode_GM.leftUp
        @see: comment at the beginning of the class
        
        """
        pass
    
    
    