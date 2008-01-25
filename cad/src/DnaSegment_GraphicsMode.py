# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created 2008-01-25

TODO: as of 2008-01-25
Implement graphics handles (actually the handles will be defined in self.command
and here we will call its draw method and define what happens when 
the handle is selected or dragged etc. 

"""


from BuildDna_GraphicsMode import BuildDna_GraphicsMode
from dna_model.DnaSegment import DnaSegment

##from drawer import drawsphere
from constants import darkred

SPHERE_RADIUS = 2.0
SPHERE_DRAWLEVEL = 2

_superclass = BuildDna_GraphicsMode

class DnaSegment_GraphicsMode(BuildDna_GraphicsMode):
    """
    Graphics mode for DnaSegment_EditCommand. 
    """
    _sphereColor = darkred
    _sphereOpacity = 0.5
    
    
    def Draw(self):
        """
        """
        _superclass.Draw(self)
        
        self._drawHandles()
        
        
    
    def _drawHandles(self):
        """
        """
        if 0: #DEBUG ONLY. 
            if self.command and self.command.struct:
                if isinstance(self.command.struct, DnaSegment):
                    for handle in self.command.handles:
                        handle.draw()
                
                if 0:
                    pass
                    #endPoint1, endPoint2 = self.command.struct.getAxisEndPoints()                
                    #drawsphere(self._sphereColor, 
                               #endPoint1, 
                               #SPHERE_RADIUS,
                               #SPHERE_DRAWLEVEL,
                               #opacity = self._sphereOpacity
                               #)      
                    #drawsphere(self._sphereColor, 
                               #endPoint2, 
                               #SPHERE_RADIUS,
                               #SPHERE_DRAWLEVEL,
                               #opacity = self._sphereOpacity
                               #)   
