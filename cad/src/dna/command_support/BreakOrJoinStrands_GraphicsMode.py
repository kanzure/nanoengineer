# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-07: Created.

TODO:
"""
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from PyQt4.Qt import QFont, QString
import foundation.env as env

from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

_superclass = BuildAtoms_GraphicsMode
class BreakOrJoinstrands_GraphicsMode(BuildAtoms_GraphicsMode):
    """
    Common superclass for GraphicsMode classes of Break and Join Strands 
    commands. 
    @see: BreakStrand_GraphicsMode()
    @see: JoinStrands_GraphicsMode() 
    """
    def _drawLabels(self):
        """
        Overrides superclass method
        @see: self.Draw()
        """
        _superclass._drawLabels(self)        
        draw_dnaBaseNumberLabels(self.glpane)
        
    