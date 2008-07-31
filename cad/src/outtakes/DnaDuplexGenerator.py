# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplexGenerator.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenerator.py.
"""

from foundation.Group import Group
from utilities.Log  import redmsg, greenmsg
from geometry.VQT import V, Veq
from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM3

from command_support.GeneratorBaseClass import GeneratorBaseClass
from utilities.exception_classes import CadBug, PluginBug, UserError
from dna.commands.BuildDuplex.DnaDuplexPropertyManager import DnaDuplexPropertyManager

############################################################################
    
# DnaDuplexPropertyManager must come BEFORE GeneratorBaseClass in this list
class DnaDuplexGenerator(DnaDuplexPropertyManager, GeneratorBaseClass):

    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'DNA-'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        DnaDuplexPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)
        self._random_data = []
    
    # ##################################################
    # How to build this kind of structure, along with
    # any necessary helper functions.

    def gather_parameters(self):
        """
        Return the parameters from the property manager UI.
        
        @return: All the parameters:
                 - numberOfBases
                 - dnaForm
                 - basesPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """        
        numberOfBases = self.numberOfBasesSpinBox.value()
        dnaForm  = str(self.conformationComboBox.currentText())
        basesPerTurn = self.basesPerTurnDoubleSpinBox.value()
        
        # First endpoint (origin) of DNA duplex
        x1 = self.x1SpinBox.value()
        y1 = self.y1SpinBox.value()
        z1 = self.z1SpinBox.value()
        
        # Second endpoint (direction vector/axis) of DNA duplex.
        x2 = self.x2SpinBox.value()
        y2 = self.y2SpinBox.value()
        z2 = self.z2SpinBox.value()
        
        endPoint1 = V(x1, y1, z1)
        endPoint2 = V(x2, y2, z2)

        return (numberOfBases, 
                dnaForm,
                basesPerTurn,
                endPoint1, 
                endPoint2)
    
    def build_struct(self, name, params, position):
        """
        Build the DNA helix based on parameters in the UI.
        
        @param name: The name to assign the node in the model tree.
        @type  name: str
        
        @param params: The list of parameters gathered from the PM.
        @type  params: tuple
        
        @param position: The position in 3d model space at which to
                         create the DNA strand. This is always 0, 0, 0.
        @type position:  position
        """
        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        numberOfBases, \
        dnaForm, \
        basesPerTurn, \
        endPoint1, \
        endPoint2 = params
        
        if Veq(endPoint1, endPoint2):
            raise CadBug("DNA endpoints cannot be the same point.")
        
        if numberOfBases < 1:
            msg = redmsg("Cannot to preview/insert a DNA duplex with 0 bases.")
            self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None

        if dnaForm == 'B-DNA':
            dna = B_Dna_PAM3()
        else:
            raise PluginBug("Unsupported DNA Form: " + dnaForm)
        
        self.dna  =  dna  # needed for done msg
        
        # Create the model tree group node. 
        dnaGroup = Group(self.name, 
                         self.win.assy,
                         self.win.assy.part.topnode)
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis
            dna.make(dnaGroup, 
                     numberOfBases, 
                     basesPerTurn, 
                     endPoint1,
                     endPoint2)
            
            return dnaGroup
        
        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            rawDnaGroup.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")
        
        pass
    
    ###################################################
    # The done message
    #@ THIS SHOULD BE REMOVED. Mark

    def done_msg(self):
        
        if not self.dna: # Mark 2007-06-01
            return "No DNA added."

        return "Done creating a strand of %s." % (self.dna.form)
    

