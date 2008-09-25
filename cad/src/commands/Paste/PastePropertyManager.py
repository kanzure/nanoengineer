# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PastePropertyManager.py

The PastePropertyManager class provides the Property Manager for the
B{Paste mode}.

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-08-29: Created to support new 'Paste mode'. 
"""

from commands.BuildAtoms.BuildAtomsPropertyManager import BuildAtomsPropertyManager
from PM.PM_Clipboard           import PM_Clipboard
from utilities.Comparison import same_vals

class PastePropertyManager(BuildAtomsPropertyManager):
    """
    The PastePropertyManager class provides the Property Manager for the
    B{Paste mode}. It lists the 'pastable' clipboard items and also shows the 
    current selected item in its 'Preview' box. 
    
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
    title = "Paste Items"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Properties Manager/clipboard-full.png"
    
    def __init__(self, command):
        """
        Constructor for the B{Paste} property manager class that defines 
        its UI.
        
        @param command: The parent mode where this Property Manager is used
        @type  command: L{PasteFromClipboard_Command}    
        """    
        self.clipboardGroupBox = None
        self._previous_model_changed_params = None
        BuildAtomsPropertyManager.__init__(self, command)
        self.updateMessage("Double click on empty space inside the 3D" \
                 "workspace to paste the item shown in "\
                 "the <b> Preview </b> box. Click the check mark to exit Paste"
                 " Items")
        
    def _update_UI_do_updates(self):
        """
        Overrides superclass method.
        @see: PasteFromClipboard_Command.command_update_internal_state() which 
        is called before any command/ PM update UI.
        """    
        currentParams = self._current_model_changed_params()
        
        if same_vals(currentParams, self._previous_model_changed_params):
            return 
        
        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams 
        
        self.update_clipboard_items() 
        # Fixes bugs 1569, 1570, 1572 and 1573. mark 060306.
        # Note and bugfix, bruce 060412: doing this now was also causing 
        # traceback bugs 1726, 1629,
        # and the traceback part of bug 1677, and some related 
        #(perhaps unreported) bugs.
        # The problem was that this is called during pasteBond's addmol 
        #(due to its addchild), before it's finished,
        # at a time when the .part structure is invalid (since the added 
        # mol's .part has not yet been set).
        # To fix bugs 1726, 1629 and mitigate bug 1677, I revised the 
        # interface to MMKit.update_clipboard_items
        # (in the manner which was originally recommented in 
        #call_after_next_changed_members's docstring) 
        # so that it only sets a flag and updates (triggering an MMKit 
        # repaint event), deferring all UI effects to
        # the next MMKit event.
        pass 
    
    def _current_model_changed_params(self):
        """
        Returns a tuple containing the parameters that will be compared
        against the previously stored parameters. This provides a quick test
        to determine whether to do more things in self._update_UI_do_updates()
        @see: self._update_UI_do_updates() which calls this
        @see: self._previous_model_changed_params attr. 
        """
        #As of 2008-09-18, this is used to update the list widget in the PM 
        #that lists the 'pastable' items. 
        return self.command.pastables_list
                
    def _addGroupBoxes(self):
        """
        Add various group boxes to the Paste Property manager.
        """
        self._addPreviewGroupBox()
        self._addClipboardGroupBox()
        
    def _addClipboardGroupBox(self):
        """
        Add the 'Clipboard' groupbox
        """
        if not self.previewGroupBox:
           return
        
        elementViewer = self.previewGroupBox.elementViewer
                
        self.clipboardGroupBox = \
            PM_Clipboard(self, 
                         win = self.command.w, 
                         elementViewer = elementViewer)
               
    
    def connect_or_disconnect_signals(self, isConnect):         
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        
        self.clipboardGroupBox.connect_or_disconnect_signals(isConnect)
            
    def getPastable(self):
        """
        Retrieve the 'pastable' clipboard item. 
        @return: The pastable clipboard item
        @rtype:  L{molecule} or L{Group}
        """
                
        self.command.pastable = self.previewGroupBox.elementViewer.model
                
        return self.command.pastable
    
    def update_clipboard_items(self):
        """
        Update the items in the clipboard groupbox.
        """
        if self.clipboardGroupBox:
            self.clipboardGroupBox.update()    

    def updateMessage(self, msg = ''):
        """
        Update the message box in the property manager with an informative 
        message.
        """  
        if not msg:   
            msg = "Double click on empty space inside the 3D workspace,"\
                " to paste the item shown in the <b> Preview </b> box. <br>" \
                " To return to the previous mode hit, <b>Escape </b> key or press "\
                "<b> Done </b>"

        # Post message.
        self.MessageGroupBox.insertHtmlMessage(msg, minLines = 5)
        
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_PasteItemsPropertyManager
        whatsThis_PasteItemsPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_PasteItemPropertyManager
        ToolTip_PasteItemPropertyManager(self)
    