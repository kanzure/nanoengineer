# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODO: 
Attributes such as height_ref need to be renamed. But this should really be done
in the superclass exprs.DraggableHandle_AlongLine. 
"""

from geometry.VQT import V

from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.constants import olive

import foundation.env as env

from exprs.attr_decl_macros import Option
from exprs.attr_decl_macros import State
from exprs.Set              import Action
from exprs.__Symbols__      import _self
from exprs.Overlay          import Overlay
from exprs.ExprsConstants   import Drawable
from exprs.ExprsConstants   import Color
from exprs.ExprsConstants   import Point
from exprs.ExprsConstants   import ORIGIN
from exprs.ExprsConstants   import StateRef
from exprs.Rect             import Sphere
from exprs.Arrow            import Arrow
from exprs.DraggableHandle  import DraggableHandle_AlongLine
from exprs.dna_ribbon_view  import Cylinder


class DnaSegment_ResizeHandle(DraggableHandle_AlongLine):
    """
    Provides a resize handle for editing the length of an existing DnaSegment. 
    """
    
    #Handle color will be changed depending on whether the the handle is grabbed
    #So this is a 'State variable and its value is used in 'appearance' 
    #(given as an optional argument to 'Sphere')
    handleColor = State( Color, olive)
    
    #The state ref that determines the radius (of the sphere) of this handle. 
    #See DnaSegment_EditCommand._determine_resize_handle_radius() for more 
    #details
    sphereRadius = Option(StateRef, 1.2)
    
    discRadius = Option(StateRef, 1.2)
    
    discThickness = Option(StateRef, 1.2)
    
    #Stateusbar text. Variable needs to be renamed in superclass. 
    sbar_text = Option(str, 
                       "Drag the handle to resize the segment", 
                       doc = "Statusbar text on mouseover")
    
    #Command object specified as an 'Option' during instantiation of the class
    #see DnaSegment_EditCommand class definition. 
    command =  Option(Action, 
                      doc = 'The Command which instantiates this handle')
    
    #Current position of the handle. i.e. it is the position of the handle 
    #under the mouse. (its differert than the 'orifinal position) 
    #This variable is used in self.command.graphicsMode to draw a rubberband 
    #line  and also to specify the endPoint2 of the structure while modifying 
    #it. See DnaSegment_EditCommand.modifyStructure for details. 
    currentPosition = _self.origin + _self.direction * _self.height_ref.value
        
    
    #Fixed end of the structure (self.command.struct) ..meaning that end won't 
    #move while user grabbs and draggs this handle (attached to a the other 
    #'moving endPoint) . This variable is used to specify endPoint1 of the 
    #structure while modifyin it.  See DnaSegment_EditCommand.modifyStructure 
    #and self.on_release for details.
    fixedEndOfStructure = Option(Point, V(0, 0, 0))
    
    #If this is false, the 'highlightable' object i.e. this handle 
    #won't be drawn. See DraggableHandle.py for the declararion of 
    #the delegate(that defines a Highlightable) We define a If_Exprs to check 
    #whether to draw the highlightable object. 
    should_draw = State(bool, True) 
    
    
    pt = _self.direction * _self.discThickness
    appearance = Overlay(
        Sphere(_self.sphereRadius, 
               handleColor, 
               center = ORIGIN), 
        
        Cylinder((ORIGIN + pt, ORIGIN - pt),
                 radius = _self.discRadius,
                 color = handleColor, 
                 opacity = 0.5),
            
        Arrow( 
            color = handleColor, 
            arrowBasePoint = ORIGIN + _self.direction * 2.0 * _self.sphereRadius,
            tailPoint = ORIGIN, 
            tailRadius = _self.sphereRadius * 0.3,
            tailRadiusLimits = (0.36, 3.0),
            scale = _self.command.glpane.scale, 
            glpane = _self.command.glpane,
            scale_to_glpane = True )                   
            )

    HHColor = env.prefs[hoverHighlightingColor_prefs_key]
    appearance_highlighted = Option(
        Drawable,
        Overlay(
            Sphere(_self.sphereRadius,                       
                   HHColor, 
                   center = ORIGIN),
            
            Cylinder((ORIGIN + pt, ORIGIN - pt),
                 radius = _self.discRadius,
                 color = HHColor),
                   
            Arrow( 
                color = HHColor, 
                arrowBasePoint = ORIGIN + _self.direction * 2.0 * _self.sphereRadius, 
                tailPoint = ORIGIN, 
                tailRadius = _self.sphereRadius * 0.3,
                tailRadiusLimits = (0.36, 3.0),
                scale = _self.command.glpane.scale,
                glpane = _self.command.glpane, 
                scale_to_glpane = True
            )
            ))
        
    def on_press(self):  
        """
        Actions when handle is pressed (grabbed, during leftDown event)
        @see: B{SelectChunks.GraphicsMode.leftDown}
        @see: B{DnaSegment_EditCommand.grabbedHandle}
        @see: B{DnaSegment_GraphicsMode.Draw} (which uses some attributes of 
             the current grabbed handle of the command. 
        @see: B{DragHandle_API}
        """
        #Change the handle color when handle is grabbed. See declaration of 
        #self.handleColor in the class definition. 
        self.handleColor = env.prefs[selectionColor_prefs_key]
        
        #assign 'self' as the curent grabbed handle of the command. 
        self.command.grabbedHandle = self
    
    def on_drag(self):
        """
        Method called while dragging this handle .
        @see: B{DragHandle_API}
        """            
        #Does nothing at the moment. 
        pass
    
    def on_release(self):
        """
        This method gets called during leftUp (when the handle is released)
        @see: B{DnaSegment_EditCommand.modifyStructure}
        @see: self.on_press
        @see: B{SelectChunks.GraphicsMode.leftUp}
        @see: B{DragHandle_API}
        """
        self.handleColor = olive
        if self.command and hasattr(self.command, 'modifyStructure'): 
            self.command.modifyStructure()
            #Clear the grabbed handle attribute (the handle is no longer 
            #grabbed)
            self.command.grabbedHandle = None
            
    def hasValidParamsForDrawing(self):
        """
        Returns True if the handles origin and direction are not 'None'. 
        
        @see: DnaSesgment_GraphicsMode._draw_handles() where the caller
              uses this to decide whether this handle can be drawn without 
              a problem. 
        """
        #NOTE: Better to do it in the drawing code of this class? 
        #But it uses a delegate to draw stuff (see class Highlightable)
        #May be we should pass this method to that delegate as an optional 
        #argument -- Ninad 2008-04-02
        
        #NOTES: See also:
        #delegate in class DraggableHandle defined as --
        #delegate = If_Exprs(_self.should_draw, Highlightable(....))
        if self.origin is None:
            self.should_draw = False
        else:
            self.should_draw = True
        
        return self.should_draw

