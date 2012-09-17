# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL

TODO:
To be revised. This handle can't be dragged. (need modifications in
DragBehavior_AlongCircle). Also the handle appearance
needs to be changed.

"""
from exprs.attr_decl_macros import Option
from exprs.attr_decl_macros import State
from exprs.Set              import Action
from exprs.__Symbols__      import _self

from exprs.Overlay          import Overlay
from exprs.ExprsConstants   import Drawable
from exprs.ExprsConstants   import Color
from exprs.ExprsConstants   import ORIGIN, DX , DY

from exprs.dna_ribbon_view  import Cylinder
from exprs.Rect             import Sphere

import foundation.env as env
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.constants import white, purple

from geometry.VQT import V
from exprs.DraggableHandle_AlongCircle import DraggableHandle_AlongCircle

#Use this flag to test some 'fancy handle drawings' (the default apaprearance is
#'sphere'
DEBUG_FANCY_HANDLES = True


class RotationHandle(DraggableHandle_AlongCircle):
    """
    Provides a resize handle for editing the length of an existing DnaSegment.
    """
    #Handle color will be changed depending on whether the the handle is grabbed
    #So this is a 'State variable and its value is used in 'appearance'
    #(given as an optional argument to 'Sphere')
    handleColor = State( Color, purple)

    if DEBUG_FANCY_HANDLES:

        appearance = Overlay(
            Sphere(1.2, handleColor, center = ORIGIN + _self.axis*3*DX),
            Cylinder((ORIGIN, ORIGIN + _self.axis*2*DX), 0.5 ,handleColor))

        HHColor = env.prefs[hoverHighlightingColor_prefs_key]
        appearance_highlighted = Option(
            Drawable,
            Overlay(
                Sphere(1.2, HHColor, center = ORIGIN + _self.axis*3*DX),
                Cylinder((ORIGIN,  ORIGIN + _self.axis*2*DX), 0.5 , HHColor)),
                doc = "handle appearance when highlighted")
    else:

        #Appearance of the handle. (note that it uses all the code from exprs module
        # and needs more documentation there).
        #See exprs.Rect.Sphere for definition of a drawable 'Sphere' object.
        appearance1 = Option( Drawable,
                             Sphere(1.2, handleColor),
                             doc = "handle appearance when not highlighted")

        #Handle appearance when highlighted
        appearance_highlighted1 = Option( Drawable,
                                         Sphere(1.2, yellow),
                                         doc = "handle appearance when highlighted")

    #Stateusbar text. Variable needs to be renamed in superclass.
    sbar_text = Option(str,
                       "Drag the handle to rotate the segment around axis",
                       doc = "Statusbar text on mouseover")

    #Command object specified as an 'Option' during instantiation of the class
    #see DnaSegment_EditCommand class definition.
    command =  Option(Action,
                      doc = 'The Command which instantiates this handle')



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
        self.handleColor = purple
        if self.command:
            #Clear the grabbed handle attribute (the handle is no longer
            #grabbed)
            self.command.grabbedHandle = None

