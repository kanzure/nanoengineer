# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
EditNanotube_PropertyManager.py

@author: Ninad, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See EditNanotube_EditCommand for details. 
"""
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox      import PM_GroupBox

from command_support.DnaOrCnt_PropertyManager   import DnaOrCnt_PropertyManager

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_LineEdit import PM_LineEdit

from geometry.VQT import V, vlen

from utilities.debug import print_compact_stack
from utilities.prefs_constants import editNanotubeEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import editNanotubeEditCommand_showCursorTextCheckBox_prefs_key
from widgets.prefs_widgets    import connect_checkbox_with_boolean_pref


_superclass = DnaOrCnt_PropertyManager

class EditNanotube_PropertyManager( DnaOrCnt_PropertyManager ):
    """
    The NanotubeSegmenta_PropertyManager class provides a Property Manager 
    for the EditNanotube_EditCommand. 

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
    iconPath      =  "ui/actions/Command Toolbar/BuildNanotube/EditNanotube.png"

    def __init__( self,  command ):
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
        
        _superclass.__init__( self, command)

        
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
    
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
        
        change_connect(self.nameLineEdit,
                       SIGNAL("editingFinished()"),
                       self._nameChanged)
        
        change_connect(self.showCursorTextCheckBox, 
                       SIGNAL('stateChanged(int)'), 
                       self._update_state_of_cursorTextGroupBox)
        return
        
    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        This method also retrives the name information from the 
        command's structure for its name line edit field. 
        @see: EditNanotube_EditCommand.getStructureName()
        @see: self.close()
        """
        _superclass.show(self)
        #if self.command is not None:
            #name = self.command.getStructureName()
            #if name is not None:
                #self.nameLineEdit.setText(name)
    
    def close(self):
        """
        Close this property manager. 
        Also sets the name of the self.command's structure to the one 
        displayed in the line edit field.
        @see self.show()
        @see: EditNanotube_EditCommand.setStructureName
        """
        if self.command is not None:
            name = str(self.nameLineEdit.text())
            self.command.setStructureName(name)
        _superclass.close(self)
        
    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Overrides 
        DnaOrCnt_PropertyManager._connect_showCursorTextCheckBox
        """
        connect_checkbox_with_boolean_pref(
            self.showCursorTextCheckBox , 
            editNanotubeEditCommand_showCursorTextCheckBox_prefs_key)


    def _params_for_creating_cursorTextCheckBoxes(self):
        """
        Returns params needed to create various cursor text checkboxes connected
        to prefs_keys  that allow custom cursor texts. 
        @return: A list containing tuples in the following format:
                ('checkBoxTextString' , preference_key). PM_PrefsCheckBoxes 
                uses this data to create checkboxes with the the given names and
                connects them to the provided preference keys. (Note that 
                PM_PrefsCheckBoxes puts thes within a GroupBox)
        @rtype: list
        @see: PM_PrefsCheckBoxes
        @see: self._loadDisplayOptionsGroupBox where this list is used. 
        @see: Superclass method which is overridden here --
        DnaOrCnt_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = \
               [  #Format: (" checkbox text", prefs_key)
                  
                  ("Nanotube length",
                   editNanotubeEditCommand_cursorTextCheckBox_length_prefs_key)
                 ]

        return params
        
    def setParameters(self, params):
        """
        This is called when entering "Nanotube Segment Properties 
        (i.e. "Edit properties...") to retrieve and set parameters of the
        nanotube segment that might be modified during this command and
        are needed to regenerate the nanotube segment.
        
        @param params: The parameters of the nanotube segment.
                       These parameters are retreived via 
                       L{NanotubeSegment.getProps()}, called from 
                       L{EditNanotube_EditCommand.editStructure()}.
                       
                       Parameters:
                       - n, m (chirality)
                       - type (i.e. carbon or boron nitride)
                       - endings (none, hydrogen, nitrogen)
                       - endpoints (endPoint1, endPoint2)
        @type params: list (n, m), type, endings, (endPoint1, endPoint2)

        @note: Any widgets in the property manager that display these
        parameters should be updated here. 
        
        @see: L{NanotubeSegment.getProps()}
        
        TODO:
        - Make this a EditCommand_PM API method? 
        - See also the routines GraphicsMode.setParams or object.setProps
        ..better to name them all in one style?  
        """
        (self.n, self.m), self.type, self.endings,\
            (self.endPoint1, self.endPoint2) = params
        
        # This is needed to update the endpoints since the Nanotube segment
        # may have been moved (i.e. translated or rotated). In that case,
        # the endpoints are not updated, so we recompute them here.
        nanotubeChunk = self.command.struct.members[0]
        self.endPoint1, self.endPoint2, radius = \
            self.command.struct.nanotube.computeEndPointsFromChunk(nanotubeChunk)
        
        if 0:
            print "\n--------------"
            print "setParameters():"
            print "Struct=", self.command.struct
            print "N, M:", self.n, self.m
            print "type:", self.type
            print "endings:", self.endings
            print "pt1, pt2:", self.endPoint1, self.endPoint2
        
    def getParameters(self):
        """
        Get the parameters that the edit command will use to determine if
        any have changed. If any have, then the nanotube will be modified.
        """
        if 0:
            print "\n--------------"
            print "getParameters():"
            print "Struct=", self.command.struct
            print "N, M:", self.n, self.m
            print "type:", self.type
            print "endings:", self.endings
            print "pt1, pt2:", self.endPoint1, self.endPoint2
        
        return (self.n, self.m, 
                self.type,
                self.endings,
                self.endPoint1, self.endPoint2)
        
    def _update_widgets_in_PM_before_show(self):
        """
        This is called only when user is editing an existing structure. 
        Its different than self.update_widgets_in_pm_before_show. (that method 
        is called just before showing the property manager) 
        @see: EditNanotube_EditCommand.editStructure()
        
        """
        if self.command and self.command.hasValidStructure():
            
            self.nanotube = self.command.struct.nanotube
            
            self.n, self.m = self.nanotube.getChirality()
            self.type = self.nanotube.getType()
            self.endings = self.nanotube.getEndings()
            self.endPoint1, self.endPoint2 = self.nanotube.getEndPoints()
            pass
        
        # Note that _update_widgets_in_PM_before_show() is called in 
        # self.show, before you connect the signals. So, for the 
        # 'first show' we will need to manually set the value of any
        # widgets that need updated. But later, when a different 
        # NanotubeSegment is clicked, (while still in 
        # EditNanotube_EditCommand, the propMgr will already be connected 
        # so any calls in that case is redundant.
        self.updateNameField()
        self.updateLength()
        self.updateNanotubeDiameter()
        self.updateChirality()

        return
    
    def _update_UI_do_updates(self):
        """
        Overrides superclass method. 
        
        @see: Command_PropertyManager._update_UI_do_updates()
        """
        self._update_widgets_in_PM_before_show()
        
        if self.command.struct:
            msg = "Editing structure <b>%s</b>." % \
                self.command.getStructureName()
        else:
            msg = "Select a nanotube to edit."
        self.updateMessage(msg)
        return
        
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
        
        self._displayOptionsGroupBox = PM_GroupBox( self, 
                                                    title = "Display Options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 4.
        """
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                         label         =  "Name:",
                         text          =  "",
                         setAsDefault  =  False)
    
        # Nanotube Length
        self.ntLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.ntLengthLineEdit.setDisabled(True)  
        
        # Nanotube Radius
        self.ntDiameterLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Nanotube Diameter: ",
                         setAsDefault  =  False)

        self.ntDiameterLineEdit.setDisabled(True)
        
        # Nanotube chirality. These are disabled (read-only) for now. --Mark
        self.chiralityNSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label        = "Chirality (n) :", 
                        minimum      =  2,
                        maximum      =  100,
                        setAsDefault = True )
        self.chiralityNSpinBox.setDisabled(True)
        
        self.chiralityMSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label        = "Chirality (m) :", 
                        minimum      =  0,
                        maximum      =  100,
                        setAsDefault = True )
        self.chiralityMSpinBox.setDisabled(True)
    
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
    
    def _nameChanged(self):
        """
        Slot for "Name" field.
        
        @TODO: Include a validator for the name field.
        """
        
        _name = str(self.nameLineEdit.text())
        
        if not _name: # Minimal test. Need to implement a validator.
            self.updateNameField()
            return
        
        self.command.setStructureName(_name)
        msg = "Editing structure <b>%s</b>." % _name
        self.updateMessage(msg)
        
        return
    
    def updateNameField(self):
        """
        Update the name field showing the name of the currently selected protein.
        clear the combobox list.
        """
        
        if self.command.hasValidStructure():
            self.nameLineEdit.setEnabled(True)
            self.nameLineEdit.setText(self.command.getStructureName())
        else:
            self.nameLineEdit.setDisabled(True)
            self.nameLineEdit.setText("")
        return
    
    def updateLength( self ):
        """
        Update the nanotube Length lineEdit widget.
        """
        if self.command.hasValidStructure():
            _nanotubeLength = vlen(self.endPoint1 - self.endPoint2)
            _lengthText = "%-7.4f Angstroms" % (_nanotubeLength)
        else:
            _lengthText = ""
        self.ntLengthLineEdit.setText(_lengthText)
        return
    
    def updateNanotubeDiameter(self):
        """
        Update the nanotube Diameter lineEdit widget.
        """
        if self.command.hasValidStructure():
            _diameterText = "%-7.4f Angstroms" %  (self.nanotube.getDiameter())
        else:
            _diameterText = ""
        self.ntDiameterLineEdit.setText(_diameterText)
        return
    
    def updateChirality( self ):
        """
        Update the nanotube chirality spinboxes (read-only).
        """
        if self.command.hasValidStructure():
            n, m = self.nanotube.getChirality()
        else:
            n = 0
            m = 0
        self.chiralityNSpinBox.setValue(n)
        self.chiralityMSpinBox.setValue(m)
        return
    
    pass # End of EditNanotube_PropertyManager class
        