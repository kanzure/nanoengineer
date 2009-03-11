# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:
2008-08-07: Created.

TODO:
"""

from PyQt4.Qt import QFont, QString

import foundation.env as env

from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode

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
        """
        _superclass._drawLabels(self)        
        draw_dnaBaseNumberLabels(self.glpane)
        
    pass
