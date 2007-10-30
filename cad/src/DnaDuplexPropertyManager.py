# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplexPropertyManager.py

@author: Mark Sims
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

Mark 2007-10-18: 
- Created. Major rewrite of DnaGeneratorPropertyManager.py.

Ninad 2007-10-24:
- Another major rewrite to a) use EditController_PM superclass and b) Implement
feature to generate Dna using endpoints of a line.
"""

__author__ = "Mark"

import env

from Dna_Constants import getDuplexRise, getDuplexLength

from utilities.Log import redmsg ##, greenmsg, orangemsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4.Qt import QAction

from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_ToolButton    import PM_ToolButton

from DebugMenuMixin import DebugMenuMixin
from EditController_PM import EditController_PM
from VQT import V

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_Constants     import pmPreviewButton

class DnaDuplexPropertyManager( EditController_PM, DebugMenuMixin ):
    """
    The DnaDuplexPropertyManager class provides a Property Manager 
    for the B{Build > DNA > Duplex} command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Insert DNA Duplex"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/Duplex.png"

    _conformation  = "B-DNA"
    _numberOfBases = 0
    _basesPerTurn  = 10.0
    _duplexRise    = getDuplexRise(_conformation)
    _duplexLength  = getDuplexLength(_conformation, _numberOfBases)

    endPoint1 = None
    endPoint2 = None    

    def __init__( self, win, editController ):
        """
        Constructor for the DNA Duplex property manager.
        """
        EditController_PM.__init__( self, 
                                    win,
                                    editController)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmPreviewButton| \
                                pmWhatsThisButton)

    def getFlyoutActionList(self): 
        """ returns custom actionlist that will be used in a specific mode 
	or editing a feature etc Example: while in movie mode, 
	the _createFlyoutToolBar method calls
	this """	


        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons. 
        #In this mode there is really no subcontrol area. 
        #We will treat subcontrol area same as 'command area' 
        #(subcontrol area buttons will have an empty list as their command area 
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.

        subControlAreaActionList =[] 

        self.exitEditControllerAction.setChecked(True)
        subControlAreaActionList.append(self.exitEditControllerAction)

        separator = QAction(self.w)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 


        allActionsList.extend(subControlAreaActionList)

        #Empty actionlist for the 'Command Area'
        commandActionLists = [] 

        #Append empty 'lists' in 'commandActionLists equal to the 
        #number of actions in subControlArea 
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params




    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self, title = "Endpoints" )
        self._loadGroupBox2( self._pmGroupBox2 )

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """

        self.conformationComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Conformation :", 
                         choices       =  ["B-DNA"],
                         setAsDefault  =  True)

        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBoxChanged )
        
        dnaModelChoices = ['PAM-3', 'PAM-5']
        self.dnaModelComboBox = \
            PM_ComboBox( pmGroupBox,     
                         label         =  "Model :", 
                         choices       =  dnaModelChoices,
                         setAsDefault  =  True)
                                            

        # Strand Length (i.e. the number of bases)
        self.numberOfBasesSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Base Pairs :", 
                        value         =  self._numberOfBases,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )

        self.connect( self.numberOfBasesSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.numberOfBasesChanged )

        self.basesPerTurnDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Bases Per Turn :",
                              value         =  self._basesPerTurn,
                              setAsDefault  =  True,
                              minimum       =  8.0,
                              maximum       =  20.0,
                              decimals      =  2,
                              singleStep    =  0.1 )

        # Duplex Length
        self.duplexLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Duplex Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.duplexLengthLineEdit.setDisabled(True)

    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box 3.
        """
        #Folllowing toolbutton facilitates entering a temporary DnaLineMode
        #to create a DNA using endpoints of the specified line. 
        self.specifyDnaLineButton = PM_ToolButton(
            pmGroupBox, 
            text = "Specify Endpoints",
            iconPath  = "ui/actions/Properties Manager"\
            "/Pencil.png",
            spanWidth = True                        
        )
        self.specifyDnaLineButton.setCheckable(True)
        self.specifyDnaLineButton.setAutoRaise(True)
        self.specifyDnaLineButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)

        self.connect(self.specifyDnaLineButton, 
                     SIGNAL("toggled(bool)"), 
                     self.editController.enterDnaLineMode)

        self._endPoint1GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint1" )
        self._endPoint2GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint2" )

        # Point 1
        self.x1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        self.y1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        self.z1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        # Point 2
        self.x2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  10.0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        self.y2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        self.z2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')

    def _addWhatsThisText( self ):
        """
        What's This text for some of the widgets in the 
        DNA Property Manager.  

        @note: Many PM widgets are still missing their "What's This" text.
        """

        self.conformationComboBox.setWhatsThis("""<b>Conformation</b>
                                               <p>DNA exists in several possible conformations, with A-DNA, B-DNA,
and Z-DNA being the most common. 
<br>
Only B-DNA is currently supported in NanoEngineer-1.</p>""")

    def conformationComboBoxChanged( self, inIndex ):
        """
        Slot for the Conformation combobox. It is called whenever the
        Conformation choice is changed.

        @param inIndex: The new index.
        @type  inIndex: int
        """
        conformation  =  self.conformationComboBox.currentText()

        if conformation == "B-DNA":
            self.basesPerTurnDoubleSpinBox.setValue("10.0")

        elif conformation == "Z-DNA":
            self.basesPerTurnDoubleSpinBox.setValue("12.0")

        else:
            msg = redmsg("conformationComboBoxChanged(): \
                         Error - unknown DNA conformation. Index = "+ inIndex)
            env.history.message(msg)

        self.duplexLengthSpinBox.setSingleStep(getDuplexRise(conformation))

    def numberOfBasesChanged( self, numberOfBases ):
        """
        Slot for the B{Number of Bases" spinbox.
        """
        # Update the Duplex Length lineEdit widget.
        text = str(getDuplexLength(self._conformation, numberOfBases)) \
             + " Angstroms"
        self.duplexLengthLineEdit.setText(text)
        return

    def getParameters(self):
        """
        Return the parameters from this property manager
        to be used to create the DNA duplex. 
        @return: A tuple containing the parameters
        @rtype: tuple
        @see: L{DnaDuplexEditController._gatherParameters} where this is used 
        """
        numberOfBases = self.numberOfBasesSpinBox.value()
        dnaForm  = str(self.conformationComboBox.currentText())
        basesPerTurn = self.basesPerTurnDoubleSpinBox.value()
        
        dnaModel = str(self.dnaModelComboBox.currentText())

        # First endpoint (origin) of DNA duplex
        x1 = self.x1SpinBox.value()
        y1 = self.y1SpinBox.value()
        z1 = self.z1SpinBox.value()

        # Second endpoint (direction vector/axis) of DNA duplex.
        x2 = self.x2SpinBox.value()
        y2 = self.y2SpinBox.value()
        z2 = self.z2SpinBox.value()

        if not self.endPoint1:
            self.endPoint1 = V(x1, y1, z1)
        if not self.endPoint2:
            self.endPoint2 = V(x2, y2, z2)

        return (numberOfBases, 
                dnaForm,
                dnaModel,
                basesPerTurn,
                self.endPoint1, 
                self.endPoint2)

    def updateCommandManager(self, bool_entering = True):
        """
	Update the command manager flyout toolbar 
	"""
        #self.win.buildDnaAction is the action in Build menu in the control 
        # area. So when the Build button is checked, the command manager will 
        # show a custom flyout toolbar. 
        #Note to Eric M:
        # This needs cleanup. It's a temporary implementation --ninad20071025

        action = self.win.buildDnaAction

        obj = self  	    	    
        self.win.commandManager.updateCommandManager(action,
                                                     obj, 
                                                     entering =bool_entering)


