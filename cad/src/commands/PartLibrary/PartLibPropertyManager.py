#Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PartLibPropertyManager.py 

The PartLibPropertyManager class provides the Property Manager for the 
B{Partlib mode}. It lists the parts in the partlib and also shows the 
current selected part in its 'Preview' box. 

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History: 
ninad 2007-09-06 Created to support the Partlib mode. This could be a temporary 
                 implementation. See Note below. 

NOTE:
In a future release, B{partlib} needs its own widget in the MainWindow like seen 
in popular cad softwares. (it probably shouldn't be in a Property manager). 
"""

from commands.Paste.PastePropertyManager import PastePropertyManager
from PM.PM_PartLib import PM_PartLib
from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_PartLibPropertyManager

class PartLibPropertyManager(PastePropertyManager):
    """
    The PartLibPropertyManager class provides the Property Manager for the
    B{Partlib mode}. It lists the parts in the partlib and also shows the 
    current selected part in its 'Preview' box. 
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
    
    # The title that appears in the Property Manager header        
    title = "Part Library"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Insert/Part_Library.png"
    
    def __init__(self, command):
        """
        Constructor for the PartLibProperty Manager. 
        
        @param command: The parent mode where this Property Manager is used
        @type  command: L{PartLibPropertyManager} 
        """
        self.partLibGroupBox = None
        
        PastePropertyManager.__init__(self, command)
        self.updateMessage(
        """The part library contains structures and molecules
        that can be added to a project by selecting from the directory
        and double clicking in the 3D graphics area.""")
        
    def _update_UI_do_updates(self):
        """
        @see: Command_PropertyManager._update_UI_do_updates()
        """
        #This does nothing in this propMGr at present. 
        return
            
    def _addGroupBoxes(self):
        """
        Add various group boxes to this Property manager.
        """
        self._addPreviewGroupBox()
        self._addPartLibGroupBox()
    
    def _addPartLibGroupBox(self):
        """
        Add the part library groupbox to this property manager
        """
        if not self.previewGroupBox:
           return
        
        elementViewer = self.previewGroupBox.elementViewer
        self.partLibGroupBox = PM_PartLib(self, 
                                          win = self.command.w,
                                          elementViewer = elementViewer)
        
        
    def connect_or_disconnect_signals(self, isConnect):         
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        self.partLibGroupBox.connect_or_disconnect_signals(isConnect)
        
    
    def getPastablePart(self):
        """
        Returns the Pastable part and its hotspot (if any)
        @return: (L{Part}, L{Atom})
        """        
        return self.partLibGroupBox.newModel, \
               self.previewGroupBox.elementViewer.hotspotAtom

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        whatsThis_PartLibPropertyManager(self)
        return
        
    
                   
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_PartLibPropertyManager
        ToolTip_PartLibPropertyManager(self)
    
