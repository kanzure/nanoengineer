# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See NanotubeSegment_EditCommand for details. 
"""
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox      import PM_GroupBox

from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_LineEdit import PM_LineEdit

from geometry.VQT import V, vlen

class NanotubeSegment_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The NanotubeSegmenta_PropertyManager class provides a Property Manager 
    for the NanotubeSegment_EditCommand. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Nanotube Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/Nanotube.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Cnt Segment Properties property manager.
        """
        
        #For model changed signal
        self.previousSelectionParams = None
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        
        # Initialized here. Their values will be set in
        # _update_widgets_in_PM_before_show()
        self.endPoint1 = V(0, 0, 0)
        self.endPoint2 = V(0, 0, 0)
        
        EditCommand_PM.__init__( self, 
                                    win,
                                    editCommand)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmWhatsThisButton)
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        This method also retrives the name information from the 
        editCommand's structure for its name line edit field. 
        @see: NanotubeSegment_EditCommand.getStructureName()
        @see: self.close()
        """
        EditCommand_PM.show(self)
        if self.editCommand is not None:
            name = self.editCommand.getStructureName()
            if name is not None:
                self.nameLineEdit.setText(name)
    
    def close(self):
        """
        Close this property manager. 
        Also sets the name of the self.editCommand's structure to the one 
        displayed in the line edit field.
        @see self.show()
        @see: NanotubeSegment_EditCommand.setStructureName
        """
        if self.editCommand is not None:
            name = str(self.nameLineEdit.text())
            self.editCommand.setStructureName(name)
        EditCommand_PM.close(self)
        
    def setParameters(self, params):
        """
        This is usually called when you are editing an existing structure. 
        Some property manager ui elements then display the information 
        obtained from the object being edited. 
        TODO:
        - Make this a EditCommand_PM API method? 
        - See also the routines GraphicsMode.setParams or object.setProps
        ..better to name them all in one style?  
        """
        self.nanotube = params #@ BUG
        
    def getParameters(self):
        """
        Get the parameters that the edit command will use to determine if
        any have changed. If any have, then the nanotube will be modified.
        """
        return (self.n, self.m, 
                self.type, 
                self.endPoint1, self.endPoint2)
    
    def _update_widgets_in_PM_before_show(self):
        """
        This is called only when user is editing an existing structure. 
        Its different than self.update_widgets_in_pm_before_show. (that method 
        is called just before showing the property manager) 
        @see: NanotubeSegment_EditCommand.editStructure()
        
        """
        if self.editCommand is not None and self.editCommand.hasValidStructure():
            self.n, self.m = self.editCommand.struct.nanotube.getChirality()
            self.type = self.editCommand.struct.nanotube.getType()
            self.endPoint1, self.endPoint2 = self.editCommand.struct.nanotube.getEndPoints()
            # Note that _update_widgets_in_PM_before_show() is called in 
            # self.show, before you connect the signals. So, for the 
            # 'first show' we will need to manually set the value of any
            # widgets that need updated. But later, when a different 
            # NanotubeSegment is clicked, (while still in 
            # NanotubeSegment_EditCommand, the propMgr will already be connected 
            # so any calls in that case is redundant.
            self.updateLength()
        
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 4.
        """
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                         label         =  "Segment name:",
                         text          =  "",
                         setAsDefault  =  False)
    
        # Nanotube Length
        self.ntLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.ntLengthLineEdit.setDisabled(True)  
    
    def _addWhatsThisText(self):
        """
        Add what's this text. 
        """
        pass
    
    def _addToolTipText(self):
        """
        Add Tooltip text
        """
        pass
    
    def updateLength( self ):
        """
        Update the nanotube Length lineEdit widget.
        """
        nanotubeLength = vlen(self.endPoint1 - self.endPoint2)
        text = "%-7.4f Angstroms" % (nanotubeLength)
        self.ntLengthLineEdit.setText(text)
        return
    
        