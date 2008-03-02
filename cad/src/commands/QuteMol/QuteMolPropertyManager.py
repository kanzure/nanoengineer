# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
QuteMolPropertyManager.py

A Property Manager command supporting external rendering by QuteMolX.

@author: Mark
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:

mark 20071202: Created.
"""

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_ToolButton    import PM_ToolButton
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_Dialog        import PM_Dialog

from PM.PM_Constants     import pmRestoreDefaultsButton, pmPreviewButton

import env

from utilities.Log import greenmsg
from qutemol import launch_qutemol, write_qutemol_files
from files_pdb import EXCLUDE_HIDDEN_ATOMS
from files_pdb import EXCLUDE_DNA_AXIS_BONDS
from files_pdb import EXCLUDE_DNA_AXIS_ATOMS

class QuteMolPropertyManager(PM_Dialog):
    """
    The QuteMolPropertyManager class provides a Property Manager for 
    QuteMolX, allowing its launch for external rendering of the model.
    """
    
    # The title that appears in the Property Manager header.
    title = "QuteMolX"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Properties Manager/QuteMol.png"
    
    # DNA Display choices.
    _axes_display_choices = [ "Render axes", 
                              "Hide axes" ]
    
    _bases_display_choices = [ "Render bases", 
                               "Hide bases" ]
                               #"Color bases black",
                               #"Color bases by type" ]
                       
    # PDB exclude flags = _axesFlags | _basesFlags
    _axesFlags  = EXCLUDE_HIDDEN_ATOMS
    _basesFlags = EXCLUDE_HIDDEN_ATOMS
    
    def __init__(self, win):
        """
        Construct the QuteMolX Property Manager.
        
        @param win: The main window.
        @type  win: QMainWindow
        """
        self.win = win
        self.pw  = None
        
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        
        msg = "Select a QuteMolX rendering style and click the \
        <b>Launch QuteMolX</b> button when ready."
        
        # This causes the "Message" box to be displayed as well.
        self.updateMessage(msg)
        
        # Hide Preview and Restore defaults button for Alpha9.
        self.hideTopRowButtons(pmRestoreDefaultsButton | pmPreviewButton)

    def _addGroupBoxes(self):
        """
        Add the 1st group box to the Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox(self, title = "DNA Display Options")
        self._loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PM_GroupBox(self, title = "Launch")
        self._loadGroupBox2(self.pmGroupBox2)
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in 1st group box.
        
        @param pmGroupBox: The 1st group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """
        
        self.axesCombobox = PM_ComboBox( 
            pmGroupBox,
            label        = 'Axes: ', 
            choices      = self._axes_display_choices, 
            index        = 0, 
            setAsDefault = True,
            spanWidth    = False )
        
        self.basesCombobox = PM_ComboBox( 
            pmGroupBox,
            label        = 'Bases: ', 
            choices      = self._bases_display_choices, 
            index        = 0, 
            setAsDefault = True,
            spanWidth    = False )
        
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in 2nd group box.
        
        @param pmGroupBox: The 1st group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """
        
        self.launchQuteMolButton = PM_ToolButton(
            pmGroupBox, 
            text      = "Launch QuteMolX",
            iconPath  = "ui/actions/Properties Manager/QuteMol.png",
            spanWidth = True )           

        self.launchQuteMolButton.setCheckable(True)
        self.launchQuteMolButton.setAutoRaise(True)
        self.launchQuteMolButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)
        
    def _addWhatsThisText(self):
        """
        "What's This" text for widgets in this Property Manager.
        """
        from gui.WhatsThisText_for_PropertyManagers import whatsThis_QuteMolPropertyManager
        whatsThis_QuteMolPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from gui.ToolTipText_for_PropertyManagers import ToolTip_QuteMolPropertyManager
        ToolTip_QuteMolPropertyManager(self)
    
    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show)
        """
        PM_Dialog.show(self)
        self.connect_or_disconnect_signals(isConnect = True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """   
        #First exit temporary modes (e.g. Pan mode) if any.
        currentCommand = self.win.commandSequencer.currentCommand 
        if not currentCommand.command_has_its_own_gui:
            currentCommand.Done()
        self.connect_or_disconnect_signals(False)
        PM_Dialog.close(self) 
        
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """
        self.accept() 
        self.close() # Close the property manager.        

        # The following reopens the property manager of the mode after 
        # when the PM of the reference geometry is closed. -- Ninad 20070603 
        # Note: the value of self.modePropertyManager can be None
        # @see: anyMode.propMgr
        #
        # (Note: once we have a real command sequencer, it will be
        #  handling this kind of thing itself, and the situation
        #  in which the currentCommand does not correspond to
        #  the current PM (as is true here while this separate PM
        #  is open, since it's not currentCommand.propMgr)
        #  will be deprecated or impossible. [bruce 071011 comment])
        self.modePropertyManager = self.win.currentCommand.propMgr

        if self.modePropertyManager:
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        self.reject() 
        self.close() 

        # The following reopens the property manager of the command after
        # the PM of the reference geometry editCommand (i.e. Plane) is closed.
        # Note: the value of self.modePropertyManager can be None.
        # See anyMode.propMgr
        # (See similar code in ok_btn_clicked [bruce 071011 comment])
        self.modePropertyManager = self.win.currentCommand.propMgr

        if self.modePropertyManager:
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return
    
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
        
        change_connect(self.axesCombobox,
                     SIGNAL("currentIndexChanged(const QString&)"),
                     self.changeAxesDisplay)
        
        change_connect(self.basesCombobox,
                     SIGNAL("currentIndexChanged(const QString&)"),
                     self.changeBasesDisplay)
        
        change_connect(self.launchQuteMolButton, 
                       SIGNAL("toggled(bool)"), 
                       self.launchQuteMol)
    
    def updateMessage(self, msg = ''):
        """
        Updates the message box with an informative message
        @param msg: Message to be displayed in the Message groupbox of 
                        the property manager
        @type  msg: string
        """
        self.MessageGroupBox.insertHtmlMessage(msg, 
                                               setAsDefault = False,
                                               minLines     = 5)
    
    def changeAxesDisplay(self, optionText):
        """
        Slot to change the axes display style.
        
        @param optionText: The text of the combobox option selected.
        @type  optionText: str        
        """
        
        if optionText == self._axes_display_choices[0]:
            self._axesFlags = EXCLUDE_HIDDEN_ATOMS
            # Cannot display axes if axis atoms are excluded.
            self.basesCombobox.setCurrentIndex(0)
        elif optionText == self._axes_display_choices[1]:
            self._axesFlags = EXCLUDE_HIDDEN_ATOMS | EXCLUDE_DNA_AXIS_BONDS
        else:
            print "Unknown axes display option: ", optionText
            
        #print "Axes display option=", optionText
        #print "Axes Flags=", self._axesFlags
    
    def changeBasesDisplay(self, optionText):
        """
        Slot to change the bases display style.
        
        @param optionText: The text of the combobox option selected.
        @type  optionText: str
        """
        if optionText == self._bases_display_choices[0]:
            self._basesFlags = EXCLUDE_HIDDEN_ATOMS
        elif optionText == self._bases_display_choices[1]:
            self._basesFlags = EXCLUDE_HIDDEN_ATOMS | EXCLUDE_DNA_AXIS_ATOMS
            # Cannot display axesif axis atoms are excluded.
            self.axesCombobox.setCurrentIndex(1)
        else:
            print "Unknown bases display option: ", optionText
            
        #print "Bases display option=", optionText
        #print "Bases Flags=", self._basesFlags
    
    def launchQuteMol(self, val):
        """
        Slot for 'Launch QuteMolX' button.
        Opens the QuteMolX rendering program and loads a copy of the current 
        model.

        Method:

        1. Write a PDB file of the current part.
        2. Write an atom attributes table text file containing atom radii and
           color information.
        3. Launches QuteMolX (with the PDB file as an argument). 

        """    
        cmd = greenmsg("QuteMolX : ")
        
        excludeFlags = self._axesFlags | self._basesFlags
        #print "Exclude flags=", excludeFlags
        
        pdb_file = write_qutemol_files(self.win.assy, excludeFlags)
        # Launch QuteMolX. It will verify the plugin.
        errorcode, msg = launch_qutemol(pdb_file) 
        # errorcode is ignored. 
        env.history.message(cmd + msg)
