# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL


"""


from temporary_commands.Line.LineMode import LineMode

from graphics.drawing.drawPeptideTrace import drawPeptideTrace, drawPeptideTrace_new

from utilities.constants import gray, black, darkred, blue, white

from protein.commands.BuildPeptide.PeptideGenerator import PeptideGenerator, get_unit_length

# == GraphicsMode part

class PeptideLine_GM( LineMode.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of PeptideLineMode.
    @see: L{PeptideLineMode} for more comments. 
    @see: Peptide_EditCommand where this is used as a GraphicsMode class.
                  
    """    
    # The following valuse are used in drawing the 'sphere' that represent the 
    #first endpoint of the line. See LineMode.Draw for details. 
    endPoint1_sphereColor = white 
    endPoint1_sphereOpacity = 1.0
    
    text = ''

    structGenerator = PeptideGenerator()

    def __init__(self, command):
        """
        """
        LineMode.GraphicsMode_class.__init__(self, command)
    
    def leftUp(self, event):
        """
        Left up method
        """
        if  self.command.mouseClickLimit is None:
            if len(self.command.mouseClickPoints) == 2:
                self.endPoint2 = None
                                
                self.command.createStructure()
                self.glpane.gl_update()            
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
            endPoint2  = LineMode.GraphicsMode_class.snapLineEndPoint(self)
        else:
            endPoint2 = self.endPoint2
            
        return endPoint2
        
      
    def Draw(self):
        """
        Draw the Nanotube rubberband line (a ladder representation)
        """
        LineMode.GraphicsMode_class.Draw(self)        
        if self.endPoint2 is not None and \
           self.endPoint1 is not None: 
            #Urmi 20080804: In absence of a better representation, this is a 
            #placeholder for now. May be Piotr can implement a better representation
            #for drawing protein secondary structure
            # Draw the ladder. 
            
            #print "command = ", self.command
            #print "phi = ", self.command.phi
            
            mol = self.structGenerator.make_aligned(self.win.assy, "", 0, 
                                                    self.command.phi, 
                                                    self.command.phi, 
                                                    self.endPoint1, 
                                                    self.endPoint2, 
                                                    fake_chain=True)
            
            drawPeptideTrace_new(mol)
            
            """
            drawPeptideTrace(self.endPoint1,
                          self.endPoint2, 
                          135,
                          -135,
                          self.glpane.scale,
                          self.glpane.lineOfSight,
                          beamThickness = 4.0 
                          ) 
            """

