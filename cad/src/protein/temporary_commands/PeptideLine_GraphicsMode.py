# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Urmi, Mark
@version:   $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL
"""

from utilities.constants import gray, black, darkred, blue, white

from graphics.drawing.drawPeptideTrace import drawPeptideTrace ##, drawPeptideTrace_orig

from temporary_commands.LineMode.Line_Command import Line_Command
from temporary_commands.LineMode.Line_GraphicsMode import Line_GraphicsMode

from protein.commands.InsertPeptide.PeptideGenerator import PeptideGenerator, get_unit_length
    # note: it would be better to move those into some other file
    # so we didn't need to import them from another command
    # (potential import cycle if that command ever needs to refer to this one)
    # [bruce 090310 comment]

# ==

_superclass_for_GM = Line_GraphicsMode

class PeptideLine_GraphicsMode( Line_GraphicsMode ):
    """
    Custom GraphicsMode used while interactively drawing a peptide chain for
    the "Insert Peptide" command.
    @see: InsertPeptide_EditCommand where this class is used.

    """
    # The following valuse are used in drawing the 'sphere' that represent the
    #first endpoint of the line. See Line_GraphicsMode.Draw_other for details.
    endPoint1_sphereColor = white
    endPoint1_sphereOpacity = 1.0

    text = ""

    structGenerator = PeptideGenerator()

    def leftUp(self, event):
        """
        Left up method.
        """
        if  self.command.mouseClickLimit is None:
            if len(self.command.mouseClickPoints) == 2:
                self.endPoint2 = None

                self.command.createStructure()
                self.glpane.gl_update()
            pass
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

    def Draw_other(self):
        """
        """
        _superclass_for_GM.Draw_other(self)

        if self.endPoint2 is not None and \
           self.endPoint1 is not None:

            # Generate a special chunk that contains only alpha carbon atoms
            # that will be used to draw the peptide backbone trace.
            # [by Mark, I guess?]

            # Note: this chunk is used only for its (ordered) atom positions;
            # it's not drawn in the usual way, and it's not part of the model.
            # So this belongs in Draw_other, not Draw_model.
            #
            ### REVIEW: this is probably very slow, compared to just generating
            # the positions and passing a position-list to drawPeptideTrace.
            # It's conceivable it also introduces bugs to do it this way
            # (depending on whether making this chunk has any side effects
            #  on assy) -- I don't know of any, but didn't look closely.
            #
            # [bruce comments 090310]

            alphaCarbonProteinChunk = \
                                    self.structGenerator.make_aligned(
                                        self.win.assy, "", 0,
                                        self.command.phi,
                                        self.command.psi,
                                        self.endPoint1,
                                        self.endPoint2,
                                        fake_chain = True)

            drawPeptideTrace(alphaCarbonProteinChunk)

            # The original way of drawing the peptide trace.
            # This function is deprecated and marked for removal.
            # --Mark 2008-12-23
            #drawPeptideTrace_orig(self.endPoint1,
                                  #self.endPoint2,
                                  #135,
                                  #-135,
                                  #self.glpane.scale,
                                  #self.glpane.lineOfSight,
                                  #beamThickness = 4.0
                                  #)

            pass
        return

    pass # end of class PeptideLine_GraphicsMode

# end
