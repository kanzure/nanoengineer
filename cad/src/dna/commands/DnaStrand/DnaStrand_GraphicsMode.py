# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""
Graphics mode intended to be used while in DnaStrand_EditCommand.

@author: Ninad
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:
Created 2008-02-14

"""
from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from graphics.drawing.drawDnaRibbons import drawDnaSingleRibbon
from utilities.constants import black


_superclass = BuildDna_GraphicsMode

class DnaStrand_GraphicsMode(BuildDna_GraphicsMode):

    _handleDrawingRequested = True
    cursor_over_when_LMB_pressed = ''

    def Draw_other(self):
        """
        Draw this DnaStrand object and its contents including handles (if any)
        @see:self._drawCursorText()
        @see:self._drawHandles()
        """
        # review: docstring may be wrong now that this method doesn't
        # draw the model [bruce 090310 comment]
        _superclass.Draw_other(self)
        if self._handleDrawingRequested:
            self._drawHandles()

    def _drawHandles(self):
        """
        Draw the handles for the command.struct
        @see: DnaStrand_ResizeHandle.hasValidParamsForDrawing ()
        @see:self._drawCursorText()
        @see:self.Draw_other()
        """
        if self.command and self.command.hasValidStructure():
            for handle in self.command.handles:
                #Check if handle's center (origin) and direction are
                #defined. (ONLY checks if those are not None)
                if handle.hasValidParamsForDrawing():
                    handle.draw()

        if self.command.grabbedHandle is not None:
            params = self.command.getDnaRibbonParams()
            if params:
                end1, end2, basesPerTurn, duplexRise, \
                    ribbon1_start_point, ribbon1_direction, ribbon1Color = params
                drawDnaSingleRibbon(self.glpane,
                               end1,
                               end2,
                               basesPerTurn,
                               duplexRise,
                               self.glpane.scale,
                               self.glpane.lineOfSight,
                               self.glpane.displayMode,
                               ribbon1_start_point = ribbon1_start_point,
                               ribbon1_direction = ribbon1_direction,
                               ribbonThickness = 4.0,
                               ribbon1Color = ribbon1Color,
                               )

            #Draw the text next to the cursor that gives info about
            #number of base pairs etc
            self._drawCursorText()

