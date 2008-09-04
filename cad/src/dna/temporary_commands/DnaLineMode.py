# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
- User Preferences for different rubberband line display styles 
"""

from temporary_commands.Line.LineMode import LineMode
from temporary_commands.Line.LineMode import LineMode_GM

from graphics.drawing.drawDnaLadder import drawDnaLadder
from graphics.drawing.drawDnaRibbons import drawDnaRibbons

from utilities.constants import black, white

import foundation.env as env

from utilities.prefs_constants import dnaDefaultStrand1Color_prefs_key
from utilities.prefs_constants import dnaDefaultStrand2Color_prefs_key

# == GraphicsMode part

_superclass_for_GM = LineMode_GM
class DnaLine_GM( LineMode_GM ):
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
        _superclass_for_GM.__init__(self, command)
        
    
    def leftUp(self, event):
        """
        Left up method
        """
        if self.isSpecifyPlaneToolActive():
            _superclass_for_GM.leftUp(self, event)
            return 
        
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
            endPoint2  = _superclass_for_GM.snapLineEndPoint(self)
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
        
        #@see: LineMode_GM class definition about this flag. Basically we supress
        #cursor text drawing in the superclass and draw later in this method
        #after everyting is drawn.
        self._ok_to_render_cursor_text = False
        _superclass_for_GM.Draw(self) 
        self._ok_to_render_cursor_text = True
        
        #This fixes NFR bug  2803
        #Don't draw the Dna rubberband line if the cursor is over the confirmation
        #corner. But make sure to call superclass.Draw method before doing this 
        #check because we need to draw the rest of the model in the graphics 
        #mode!. @see: LineMode_GM.Draw
        handler = self.o.mouse_event_handler
        if handler is not None and handler is self._ccinstance:
            return
        
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
                              beam1Color = env.prefs[dnaDefaultStrand1Color_prefs_key],
                              beam2Color = env.prefs[dnaDefaultStrand2Color_prefs_key],
                              )
            elif self.command.callback_rubberbandLineDisplay() ==  'Ribbons':  
                #Default dna rubberband line display style       
                drawDnaRibbons(self.glpane,
                               self.endPoint1,
                               self.endPoint2, 
                               self.command.basesPerTurn,
                               self.command.duplexRise,
                               self.glpane.scale,
                               self.glpane.lineOfSight,
                               self.glpane.displayMode,
                               ribbonThickness = 4.0,
                               ribbon1Color = env.prefs[dnaDefaultStrand1Color_prefs_key],
                               ribbon2Color = env.prefs[dnaDefaultStrand2Color_prefs_key],
                               )   
            else:
                pass
            
            self._drawCursorText()
            
                    

# == Command part
class DnaLineMode(LineMode): # not used as of 080111, see docstring
    """
    [no longer used as of 080111, see details below]
    Encapsulates the LineMode functionality.
    @see: L{LineMode}
    @see: DnaDuplex_EditCommand.getCursorText
    
    NOTE: [2008-01-11]
    The default DnaLineMode (command) part is not used as of 2008-01-11
    Instead, the interested commands use its GraphicsMode class. 
    However, it's still possible to use and implement the default command 
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
    from utilities.constants import CL_UNUSED
    command_level = CL_UNUSED
            
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
    
    
    
