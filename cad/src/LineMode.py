# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
        
"""

from TemporaryCommand import TemporaryCommand_Overdrawing

from drawer import drawline, drawsphere
from constants import black, darkred

from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix

mouseClickCounter = 0

STARTPOINT_SPHERE_COLOR = darkred
STARTPOINT_SPHERE_RADIUS = 1.0
STARTPOINT_SPHERE_DRAWLEVEL = 2
STARTPOINT_SPHERE_OPACITY = 0.5

# == GraphicsMode part

class LineMode_GM( TemporaryCommand_Overdrawing.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of LineMode.
    
    Its a temporary mode that draws temporary line with mouse click points 
    as endpoints and then returns to the previous mode when the  
    mouseClickLimit specified by the user is reached.
    
    Example use:
    User is working in selectMolsMode, Now he enters a temporary mode 
    called DnaLine mode, where, he clicks two points in the 3Dworkspace 
    and expects to create a DNA using the points he clicked as endpoints. 
    Internally, the program returns to the previous mode after two clicks. 
    The temporary mode sends this information to the method defined in 
    the previous mode called acceptParamsFromTemporaryMode and then the
    previous mode (selectMolsMode) can use it further to create a dna 
    @see: L{DnaLineMode}
    @see: selectMolsMode.provideParamsForTemporaryMode comments for 
        related  TODOs. 
        
    TODO: 
    -Need further documentation. 
    - May be class name needs reconsideration. Looks OK for now. 
    """    
    movingPoint = None
    currentPoint = None

    def leftDown(self, event):
        """
        Event handler for LMB press event.
        """
        
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)  
        self.command.mouseClickPoints.append(self.movingPoint)
        return
    
    def bareMotion(self, event):
        """
        Event handler for simple mouse drag event.
        """
        global mouseClickCounter
        
        if mouseClickCounter > 0:
            self.currentPoint = self.dragto( self.movingPoint, event)
            self.glpane.gl_update()        
        return
    
    def Draw(self):
        """
        Draw method for this temporary mode. 
        """
        TemporaryCommand_Overdrawing.GraphicsMode_class.Draw(self)
        if self.currentPoint:
            glPushMatrix()  
            if self.movingPoint:
                drawsphere(STARTPOINT_SPHERE_COLOR, 
                           self.movingPoint, 
                           STARTPOINT_SPHERE_RADIUS,
                           STARTPOINT_SPHERE_DRAWLEVEL,
                           opacity = STARTPOINT_SPHERE_OPACITY
                           )            
            drawline(black, 
                 self.movingPoint, 
                 self.currentPoint, 
                 dashEnabled = True)            
            glPopMatrix()
    
    def leftUp(self, event):
        """
        Event handler for Left Mouse button left-up event
        """
        global mouseClickCounter
        
        assert mouseClickCounter <= self.command.mouseClickLimit
        
        mouseClickCounter += 1
                
        if mouseClickCounter == self.command.mouseClickLimit:
            mouseClickCounter = 0  
            self.currentPoint = None
            self.glpane.gl_update()
            self.command.Done()            
            return
         
    def update_cursor_for_no_MB(self): 
        """
        Update the cursor for this mode.
        """
        self.glpane.setCursor(self.win.SelectAtomsCursor)
    
            

# == Command part

class LineMode(TemporaryCommand_Overdrawing): 
    """
    Encapsulates the LineMode tool functionality.
    """
    
    # class constants
    
    modename = 'LineMode'
    default_mode_status_text = ""
    hover_highlighting_enabled = True
    
    mouseClickPoints = []
    GraphicsMode_class = LineMode_GM

    def init_gui(self):
        prevMode = self.commandSequencer.prevMode 
        
        if hasattr(prevMode, 'provideParamsForTemporaryMode'):
            self.mouseClickLimit = prevMode.provideParamsForTemporaryMode(self.modename)
        return    
        
    def restore_gui(self):
        prevMode = self.commandSequencer.prevMode
        if hasattr(prevMode, 'acceptParamsFromTemporaryMode'):          
            prevMode.acceptParamsFromTemporaryMode(
                self.modename, 
                self.mouseClickPoints)
            #clear the list
            self.mouseClickPoints = []
        return
    
