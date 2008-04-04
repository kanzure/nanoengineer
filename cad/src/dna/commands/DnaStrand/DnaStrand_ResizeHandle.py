# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrand_ResizeHandle.py

@author:    Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

History: 
Created on 2008-02-14

TODO: as of 2008-02-14
- Attributes such as height_ref need to be renamed. But this should really be done
  in the superclass exprs.DraggableHandle_AlongLine. 
- Needs refactoring. Shares common things with DnaSegment_ResizeHandle . 
  Really the only difference is the handle appearance. See if renaming 
  DnaSegment_ResizeHandle and then using it as a common class makes sense. 

"""
from exprs.attr_decl_macros import Option
from exprs.attr_decl_macros import State
from exprs.Set              import Action
from exprs.__Symbols__      import _self

from exprs.Overlay          import Overlay
from exprs.ExprsConstants   import Drawable
from exprs.ExprsConstants   import Color
from exprs.ExprsConstants   import Point
from exprs.ExprsConstants   import ORIGIN, DX 

from exprs.dna_ribbon_view  import Cylinder
from exprs.Rect             import Sphere
   
from utilities.constants import yellow, purple, darkgreen

from geometry.VQT import V
from exprs.DraggableHandle import DraggableHandle_AlongLine
from exprs.ExprsConstants import StateRef

class DnaStrand_ResizeHandle(DraggableHandle_AlongLine):
    """
    Provides a resize handle for editing the length of an existing Dna Strand. 
    """
    
    #Handle color will be changed depending on whether the the handle is grabbed
    #So this is a 'State variable and its value is used in 'appearance' 
    #(given as an optional argument to 'Sphere') 
    handleColor = Option(StateRef, purple)  
    
    
    _currentHandleColor = State(Color, _self.handleColor)
        
    #The state ref that determines the radius (of the sphere) of this handle. 
    #See DnaStrand_EditCommand._determine_resize_handle_radius() for more 
    #details
    sphereRadius = Option(StateRef, 1.5)
        
    #Appearance of the handle. (note that it uses all the code from exprs module
    # and needs more documentation there). 
    #See exprs.Rect.Sphere for definition of a drawable 'Sphere' object.
    
    appearance = Overlay(
            Sphere(_self.sphereRadius, 
                   _self._currentHandleColor, 
                   center = ORIGIN + _self.direction*3.0*_self.sphereRadius),
                   
            Cylinder((ORIGIN, 
                      ORIGIN + _self.direction*2.2*_self.sphereRadius),
                      0.6* _self.sphereRadius,
                      _self._currentHandleColor))
    
    #Handle appearance when highlighted   
    appearance_highlighted = Option(
        Drawable,
        Overlay(
            Sphere(_self.sphereRadius, 
                   yellow, 
                   center = ORIGIN + _self.direction*3.0*_self.sphereRadius),
                   
            Cylinder((ORIGIN,  
                      ORIGIN + _self.direction*2.2*_self.sphereRadius),
                     0.6* _self.sphereRadius , 
                     yellow)),
            doc = "handle appearance when highlighted")
     

    #Stateusbar text. Variable needs to be renamed in superclass. 
    sbar_text = Option(str, 
                       "Drag the handle to resize the strand", 
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
    if _self.origin is not None:
        currentPosition = _self.origin + _self.direction*_self.height_ref.value
    else:
        currentPosition = ORIGIN
        
    
    #Fixed end of the structure (self.command.struct) ..meaning that end won't 
    #move while user grabbs and draggs this handle (attached to a the other 
    #'moving endPoint) . This variable is used to specify endPoint1 of the 
    #structure while modifyin it.  See DnaSegment_EditCommand.modifyStructure 
    #and self.on_release for details.
    fixedEndOfStructure = Option(Point, 
                                 V(0, 0, 0))
    
    #If this is false, the 'highlightable' object i.e. this handle 
    #won't be drawn. See DraggableHandle.py for the declararion of 
    #the delegate(that defines a Highlightable) We define a If_Exprs to check 
    #whether to draw the highlightable object. 
    should_draw = State(bool, True)
    
    def ORIG_NOT_USED_hasValidParamsForDrawing(self):
        """
        NOT USED AS OF 2008-04-02
        Returns True if the handles origin and direction are not 'None'. 
        
        @see: DnaStrand_GraphicsMode._draw_handles() where the caller
              uses this to decide whether this handle can be drawn without 
              a problem. 
        """
        #NOTE: Better to do it in the drawing code of this class? 
        #But it uses a delegate to draw stuff (see class Highlightable)
        #May be we should pass this method to that delegate as an optional 
        #argument -- Ninad 2008-04-02
        if self.origin is None or self.direction is None:
            return  False
       
        return True
    
    
    def hasValidParamsForDrawing(self):
        """
        Returns True if the handles origin and direction are not 'None'. 
        
        @see: DnaStrand_GraphicsMode._draw_handles() where the caller
              uses this to decide whether this handle can be drawn without 
              a problem. 
        
        """
        
        #NOTE: Better to do it in the drawing code of this class? 
        #But it uses a delegate to draw stuff (see class Highlightable)
        #May be we should pass this method to that delegate as an optional 
        #argument -- Ninad 2008-04-02
        
        #@Bug: Create a duplex; Enter Dna strand edit command, 
        # then shorten it such that it removes some bases of the strand from the
        #original duplex. Hit undo; click on the right handle, and shorten it again
        #sometimes it gives a traceback. in drawing the highlightable 
        #this could be because self.should_draw flag is not getting updated.
        
            
        #NOTES: If this method is used, you will also need to define the 
        #delegate in class DraggableHandle as --
        #delegate = If_Exprs(_self.should_draw, Highlightable(....))
        if self.origin is None or self.direction is None:
            self.should_draw = False
        else:
            self.should_draw = True
        
        return self.should_draw
            
       
    def on_press(self):  
        """
        Actions when handle is pressed (grabbed, during leftDown event)
        @see: B{SelectChunks.GraphicsMode.leftDown}
        @see: B{DnaStrand_EditCommand.grabbedHandle} 
        @see: B{DnaStrand_GraphicsMode.Draw} (which uses some attributes of 
             the current grabbed handle of the command. 
        @see: B{DragHandle_API}
        """
        #Change the handle color when handle is grabbed. See declaration of 
        #self.handleColor in the class definition. 
      
        self._currentHandleColor = darkgreen
        
        #assign 'self' as the curent grabbed handle of the command. 
        self.command.grabbedHandle = self
    
    def on_drag(self):
        """
        Method called while dragging this handle .
        @see: B{DragHandle_API}
        """
        pass
        #The following call is disabled. Instead updating this spinbox 
        #is done by the command.getCursorText method . See that method for 
        #details
        ##self.command.update_numberOfBases()
    
    def on_release(self):
        """
        This method gets called during leftUp (when the handle is released)
        @see: B{DnaStrand_EditCommand.modifyStructure}
        @see: self.on_press
        @see: B{SelectChunks.GraphicsMode.leftUp}
        @see: B{DragHandle_API}
        """
        self._currentHandleColor = self.handleColor
        if self.command and hasattr(self.command, 'modifyStructure'): 
            self.command.modifyStructure()
            #Clear the grabbed handle attribute (the handle is no longer 
            #grabbed)
            self.command.grabbedHandle = None
        
