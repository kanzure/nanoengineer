# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BreakStrands_PropertyManager.py

 The BreakStrands_PropertyManager class provides a Property Manager 
    for the B{Break Strands} command on the flyout toolbar in the 
    Build > Dna mode. 

@author: Ninad
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.


TODO: as of 2008-02-13:
- Remove 'Cancel' button -- This needs to be supported in transient done-cancel
button code (confirmation_corner)
- methods such as ok_btn_clicked need cleanup in the superclass. This workis 
pending because of some remaining things in GBC cleanup (such as 
NanotubeGenerator etc) 
"""
import sys
from DebugMenuMixin import DebugMenuMixin
from PM.PM_Dialog import PM_Dialog
from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton

class JoinStrands_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The JoinStrands_PropertyManager class provides a Property Manager 
    for the B{Join Strands} command on the flyout toolbar in the 
    Build > Dna mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Join Strands"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Join_Strands.png"
    
    
    def __init__( self, parentCommand ):
        """
        Constructor for the property manager.
        """

        self.parentMode = parentCommand
        self.w = self.parentMode.w
        self.win = self.parentMode.w
        self.pw = self.parentMode.pw        
        self.o = self.win.glpane                 
                    
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmWhatsThisButton)
        
                
        if sys.platform == 'darwin':
            leftMouseButtonString = 'mouse button'
        else:
            leftMouseButtonString = 'left mouse button'
                
        msg = ("<b>Join Strands:</b>"\
            "<br> Move cursor over a 3' end, hold down the %s and release it " \
            "when the cursor is over a 5' end") %(leftMouseButtonString)
        
        
        self.updateMessage(msg)
        
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """      
        self.win.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """  
        #TODO: Cancel button needs to be removed. See comment at the top
        self.win.toolsDone()
        
        
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """  
        pass
    
    
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    