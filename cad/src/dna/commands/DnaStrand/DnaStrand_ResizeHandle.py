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
   
from constants              import  yellow, purple, darkgreen

from geometry.VQT import V
from exprs.DraggableHandle import DraggableHandle_AlongLine

class DnaStrand_ResizeHandle(DraggableHandle_AlongLine):
    """
    Provides a resize handle for editing the length of an existing Dna Strand. 
    """
    
    #Handle color will be changed depending on whether the the handle is grabbed
    #So this is a 'State variable and its value is used in 'appearance' 
    #(given as an optional argument to 'Sphere')
    handleColor = State( Color, purple)
    
    #Appearance of the handle. (note that it uses all the code from exprs module
    # and needs more documentation there). 
    #See exprs.Rect.Sphere for definition of a drawable 'Sphere' object.
    
    appearance = Overlay(
            Sphere(1.2, handleColor, center = ORIGIN + _self.direction*3*DX), 
            Cylinder((ORIGIN, ORIGIN + _self.direction*2*DX), 0.5 ,handleColor))
    
    #Handle appearance when highlighted   
    appearance_highlighted = Option(
        Drawable,
        Overlay(
            Sphere(1.2, yellow, center = ORIGIN + _self.direction*3*DX),
            Cylinder((ORIGIN,  ORIGIN + _self.direction*2*DX), 0.5 , yellow)),
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
    currentPosition = _self.origin + _self.direction*_self.height_ref.value
    
    
    #Fixed end of the structure (self.command.struct) ..meaning that end won't 
    #move while user grabbs and draggs this handle (attached to a the other 
    #'moving endPoint) . This variable is used to specify endPoint1 of the 
    #structure while modifyin it.  See DnaSegment_EditCommand.modifyStructure 
    #and self.on_release for details.
    fixedEndOfStructure = Option(Point, 
                                 V(0, 0, 0))
    
    
       
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
        self.handleColor = darkgreen
        
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
        @see: B{DnaStrand_EditCommand.modifyStructure}
        @see: self.on_press
        @see: B{SelectChunks.GraphicsMode.leftUp}
        @see: B{DragHandle_API}
        """
        self.handleColor = purple
        if self.command and hasattr(self.command, 'modifyStructure'): 
            self.command.modifyStructure()
            #Clear the grabbed handle attribute (the handle is no longer 
            #grabbed)
            self.command.grabbedHandle = None

