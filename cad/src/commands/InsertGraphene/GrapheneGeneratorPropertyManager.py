# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Mark
@version:$Id$

History:

Mark 2007-05-17: This used to be generated from its .ui file. Now it uses PropMgrBaseClass
  to construct its property manager dialog.
Mark 2007-07-24: Now uses new PM module.
Mark 2007-08-06: Renamed GrapheneGeneratorDialog to GrapheneGeneratorPropertyManager.
Ninad 2008-07-22/23: ported this to EditCommand API (new superclass 
                   Editcommand_PM)

"""


from model.bonds import CC_GRAPHITIC_BONDLENGTH

from PM.PM_GroupBox       import PM_GroupBox
from PM.PM_DoubleSpinBox  import PM_DoubleSpinBox
from PM.PM_ComboBox       import PM_ComboBox
from command_support.EditCommand_PM import EditCommand_PM
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from PM.PM_Constants     import PM_PREVIEW_BUTTON

_superclass = EditCommand_PM
class GrapheneGeneratorPropertyManager(EditCommand_PM):
    """
    The GrapheneGeneratorPropertyManager class provides a Property Manager
    for the "Build > Graphene (Sheet)" command.
    """
    # The title that appears in the property manager header.
    title = "Graphene Generator"
    # The name of this property manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Graphene.png"
    
    def __init__( self, command ):
        """
        Construct the "Build Graphene" Property Manager.
        """
        _superclass.__init__( self, command )
               
        msg = "Edit the parameters below and click the <b>Preview</b> "\
            "button to preview the graphene sheet. Clicking <b>Done</b> "\
            "inserts it into the model."
        
        self.updateMessage(msg = msg)
        
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_PREVIEW_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
                
    def _addGroupBoxes(self):
        """
        Add the group boxes to the Graphene Property Manager dialog.
        """
        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title = "Graphene Parameters" )
        
        self._loadGroupBox1(self.pmGroupBox1)
              
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in groubox 1.
        """
        
        self.heightField = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Height :", 
                              value        = 20.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 100.0, 
                              singleStep   = 1.0, 
                              decimals     = 3, 
                              suffix       = ' Angstroms')
        self.widthField = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Width :", 
                              value        = 20.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 100.0, 
                              singleStep   = 1.0, 
                              decimals     = 3, 
                              suffix       = ' Angstroms')
        
        self.bondLengthField = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Bond Length :", 
                              value        = CC_GRAPHITIC_BONDLENGTH, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 3.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = ' Angstroms')
        
        endingChoices = ["None", "Hydrogen", "Nitrogen"]
        
        self.endingsComboBox= \
            PM_ComboBox( pmGroupBox,
                         label        = "Endings :", 
                         choices      = endingChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        
    def getParameters(self):
        """
        Return the parameters from this property manager
        to be used to create the graphene sheet.
        @return: A tuple containing the parameters
        @rtype: tuple
        @see: L{Graphene_EditCommand._gatherParameters()} where this is used
        """
        
        height = self.heightField.value()
        width = self.widthField.value()
        bond_length = self.bondLengthField.value()
        endings = self.endingsComboBox.currentIndex()
        
        return (height, width, bond_length, endings)
            
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_GrapheneGeneratorPropertyManager
        whatsThis_GrapheneGeneratorPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_GrapheneGeneratorPropertyManager
        ToolTip_GrapheneGeneratorPropertyManager(self)
        
 
    