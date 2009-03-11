# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad, Mark
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
- User Preferences for different rubberband line display styles 
"""

from utilities.constants import gray, black, darkred, blue, white

from graphics.drawing.drawNanotubeLadder import drawNanotubeLadder

from temporary_commands.LineMode.Line_Command import Line_Command
from temporary_commands.LineMode.Line_GraphicsMode import Line_GraphicsMode

# == GraphicsMode part

_superclass_for_GM = Line_GraphicsMode

class NanotubeLine_GM( Line_GraphicsMode ):
    """
    Custom GraphicsMode for use as a component of NanotubeLineMode.
    @see: L{NanotubeLineMode} for more comments. 
    @see: InsertNanotube_EditCommand where this is used as a GraphicsMode class.
          The default command part in this file is a Default class
          implementation  of self.command (see class NanotubeLineMode)          
    """    
    # The following valuse are used in drawing the 'sphere' that represent the 
    # first endpoint of the line. See Line_GraphicsMode.Draw_other for details. 
    endPoint1_sphereColor = white 
    endPoint1_sphereOpacity = 1.0
    
    text = ''
    
        
    def leftUp(self, event):
        """
        Left up method
        """
        if  self.command.mouseClickLimit is None:
            if len(self.command.mouseClickPoints) == 2:
                self.endPoint2 = None
                                
                self.command.createStructure()
                #DISABLED AS OF 2008-01-11. (Implementation changed --
                #See InsertNanotube_EditCommand.createStructure for new 
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
            endPoint2 = _superclass_for_GM.snapLineEndPoint(self)
        else:
            endPoint2 = self.endPoint2
            
        return endPoint2
    
    def Draw_other(self):
        """
        Draw the Nanotube rubberband line (a ladder representation)
        """
        _superclass_for_GM.Draw_other(self)
        if self.endPoint2 is not None and \
           self.endPoint1 is not None:
            
            # Draw the ladder.
            drawNanotubeLadder(
                self.endPoint1,
                self.endPoint2, 
                self.command.nanotube.getRise(),
                self.glpane.scale,
                self.glpane.lineOfSight,
                ladderWidth = self.command.nanotube.getDiameter(),
                beamThickness = 4.0,
             )
        return

    pass # end of class NanotubeLine_GM

# == Command part

class NanotubeLineMode(Line_Command): # not used as of 080111, see docstring
    """
    [no longer used as of 080111, see details below]
    Encapsulates the Line_Command functionality.
    @see: L{Line_Command}
    @see: InsertNanotube_EditCommand.getCursorText()
    
    NOTE: [2008-01-11]
    The default NanotubeLineMode (command) part is not used as of 2008-01-11
    Instead, the interested commands use its GraphicsMode class. 
    However, its still possible to use and implement the default command 
    part. (The old implementation of generating Cnt using endpoints of a 
    line used this default command class (NanotubeLineMode). so the method in this
    class  such as self.createStructure does nothing . 
    @see: InsertNanotube_EditCommand where the GraphicsMode class of this command is 
          used
        
    """
    
    # class constants    
    commandName = 'NANOTUBE_LINE_MODE'    
    featurename = "Nanotube Line Mode"
        # (This featurename is sometimes user-visible,
        #  but is probably not useful. See comments in Line_Command
        #  for more info and how to fix. [bruce 071227])
    from utilities.constants import CL_UNUSED
    command_level = CL_UNUSED
            
    GraphicsMode_class = NanotubeLine_GM
        
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
        @see: NanotubeLineMode_GM.leftUp
        @see: comment at the beginning of the class
        
        """
        return
    
    pass

# end

    
