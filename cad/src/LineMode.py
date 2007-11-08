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
    """    
    
    #Initial values of instance variables --
    
    #The first end point of the line being drawn. 
    #It gets initialized during left down --
    endPoint1 = None 
    #The second endpoint of the line. This gets constantly updated as you 
    # free drag the mouse (bare motion) 
    endPoint2 = None

    def leftDown(self, event):
        """
        Event handler for LMB press event.
        """        
        #The endPoint1 and self.endPoint2 are the mouse points at the 'water' 
        #surface. Soon, support will be added so that these are actually points 
        #on a user specified reference plane. Also, once any temporary mode 
        # begins supporting highlighting, we can also add feature to use 
        # coordinates of a highlighted object (e.g. atom center) as endpoints 
        # of the line
        farQ_junk, self.endPoint1 = self.dragstart_using_GL_DEPTH( event)  
        self.command.mouseClickPoints.append(self.endPoint1)
        return
    
    def bareMotion(self, event):
        """
        Event handler for simple drag event. (i.e. the free drag without holding
        down any mouse button)
        """       
        if len(self.command.mouseClickPoints) > 0:
            self.endPoint2 = self.dragto( self.endPoint1, event)
            self.glpane.gl_update()        
        return
    
    def Draw(self):
        """
        Draw method for this temporary mode. 
        """
        TemporaryCommand_Overdrawing.GraphicsMode_class.Draw(self)
        if self.endPoint2:
            glPushMatrix()  
            if self.endPoint1:
                drawsphere(STARTPOINT_SPHERE_COLOR, 
                           self.endPoint1, 
                           STARTPOINT_SPHERE_RADIUS,
                           STARTPOINT_SPHERE_DRAWLEVEL,
                           opacity = STARTPOINT_SPHERE_OPACITY
                           )            
            drawline(black, 
                 self.endPoint1, 
                 self.endPoint2, 
                 dashEnabled = True)            
            glPopMatrix()
    
    def leftUp(self, event):
        """
        Event handler for Left Mouse button left-up event
        """
               
        assert len(self.command.mouseClickPoints) <= self.command.mouseClickLimit
                        
        if len(self.command.mouseClickPoints) == self.command.mouseClickLimit:
            self.endPoint2 = None
            self.glpane.gl_update()
            self.command.Done()            
            return
         
    def update_cursor_for_no_MB(self): 
        """
        Update the cursor for this mode.
        """
        self.glpane.setCursor(self.win.SelectAtomsCursor)
    
    def resetVariables(self):
        """
        Reset instance variables. Typically used by self.command when the 
        command is exited without the graphics mode knowing about it before hand
        Example: You entered line mode, started drawing line, and hit Done 
        button. This exits the Graphics mode (without the 'leftup' which usually
        terminates the command *from Graphics mode') . In the above case, the 
        command.restore_gui needs to tell its graphics mode about what just 
        happened , so that all the assigned values get cleared and ready to use
        next time this graphicsMode is active.
        """
        self.endPoint1 = None
        self.endPoint2 = None
            
            
# == Command part

class LineMode(TemporaryCommand_Overdrawing): 
    """
    Encapsulates the LineMode tool functionality.
    """
    # class constants
    
    modename = 'LineMode'
    default_mode_status_text = ""
    hover_highlighting_enabled = True
    GraphicsMode_class = LineMode_GM
    
    # Initial vale for the instance variable. (Note that although it is assigned 
    # an empty tuple, later it is assigned a list.) Empty tuple is just for 
    # the safer implementation than an empty list. Also, it is not 'None' 
    # because in LineMode_GM.bareMotion, it does a check using
    # len(mouseClickPoints)
    mouseClickPoints = ()
    
    def init_gui(self):
        """
        """
        prevMode = self.commandSequencer.prevMode        
        #clear the list (for safety) which may still have old data in it
        self.mouseClickPoints = []
        
        self.glpane.gl_update()
        
        if hasattr(prevMode, 'provideParamsForTemporaryMode'):
            params = prevMode.provideParamsForTemporaryMode(self.modename)
            self.setParams(params)
        return   
    
    def setParams(self, params):
        """
        Assign values obtained from the previouse mode to the instance variables
        of this command object. 
        """
        self.mouseClickLimit = params        
        
    def restore_gui(self):
        """
        """
        prevMode = self.commandSequencer.prevMode
        if hasattr(prevMode, 'acceptParamsFromTemporaryMode'): 
            prevMode.acceptParamsFromTemporaryMode(
                self.modename, 
                self.mouseClickPoints)
            #clear the list
            self.mouseClickPoints = []       
        
        self.graphicsMode.resetVariables()
       
        return
    
