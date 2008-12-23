# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Urmi, Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from temporary_commands.LineMode.Line_Command import Line_Command
from temporary_commands.LineMode.Line_GraphicsMode import Line_GraphicsMode

from graphics.drawing.drawPeptideTrace import drawPeptideTrace, drawPeptideTrace_orig

from utilities.constants import gray, black, darkred, blue, white

from protein.commands.InsertPeptide.PeptideGenerator import PeptideGenerator, get_unit_length

# == GraphicsMode part

class PeptideLine_GraphicsMode( Line_GraphicsMode ):
    """
    Custom GraphicsMode used while interactively drawing a peptide chain for
    the "Insert Peptide" command.
    @see: InsertPeptide_EditCommand where this class is used.
                  
    """    
    # The following valuse are used in drawing the 'sphere' that represent the 
    #first endpoint of the line. See Line_GraphicsMode.Draw for details. 
    endPoint1_sphereColor = white 
    endPoint1_sphereOpacity = 1.0
    
    text = ''

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
            endPoint2  = Line_GraphicsMode.snapLineEndPoint(self)
        else:
            endPoint2 = self.endPoint2
            
        return endPoint2
        
      
    def Draw(self):
        """
        Draw the Nanotube rubberband line (a ladder representation)
        """
        Line_GraphicsMode.Draw(self)        
        if self.endPoint2 is not None and \
           self.endPoint1 is not None:
            
            # Generate a special chunk that contains only alpha carbon atoms
            # that will be used to draw the peptide backbone trace.
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

