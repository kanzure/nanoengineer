# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
InsertNanotube_PropertyManager.py

@author: Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Mark 2008-03-09: 
- Created. Copied and edited DnaDuplexPropertyManager.py.
"""

__author__ = "Mark"

import foundation.env as env

from cnt.model.Nanotube_Constants import getCntRise, getCntLength
from cnt.commands.InsertNanotube.Chirality import Chirality

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
from PM.PM_CoordinateSpinBoxes import PM_CoordinateSpinBoxes
from PM.PM_CheckBox   import PM_CheckBox

from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM
from geometry.VQT import V
from math import pi

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton

from model.bonds import CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH

ntBondLengths = [CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH]

#@from gui.WhatsThisText_for_PropertyManagers import whatsThis_InsertNanotube_PropertyManager

class InsertNanotube_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The InsertNanotube_PropertyManager class provides a Property Manager 
    for the B{Build > Nanotube > CNT} command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Insert Nanotube"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/InsertNanotube.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Nanotube property manager.
        """
        self.endPoint1 = None
        self.endPoint2 = None
        
        self.ntChirality = Chirality() # Returns a 5x5 CNT (default).
        self.n, self.m = self.ntChirality.getChirality()
        self._ntType  = self.ntChirality.getType()
        self._bond_length = self.ntChirality.getBondLength()
        self._ntRise   = self.ntChirality.getRise()
        self._ntLength = self.ntChirality.getLength(numberOfCells = 0)
    
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
         
                
        change_connect( self.ntTypeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self._ntTypeComboBoxChanged )
        
        #change_connect( self.ntRiseDoubleSpinBox,
        #              SIGNAL("valueChanged(double)"),
        #              self.ntRiseChanged )
        
        change_connect(self.chiralityNSpinBox,
                       SIGNAL("valueChanged(int)"),
                       self._chiralityFixup)
        
        change_connect(self.chiralityMSpinBox,
                       SIGNAL("valueChanged(int)"),
                       self._chiralityFixup)
        
        change_connect(self.bondLengthDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self.bondLengthChanged)
  
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """   
        if self.editCommand:
            self.editCommand.preview_or_finalize_structure(previewing = False)
            ##env.history.message(self.editCommand.logMessage)        
        self.win.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        if self.editCommand:
            self.editCommand.cancelStructure()            
        self.win.toolsCancel()
        
    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager.
        Overrides MotorPropertyManager._update_widgets_in_PM_before_show. 
        The various  widgets , (e.g. spinboxes) will get values from the 
        structure for which this propMgr is constructed for 
        (self.editcCntroller.struct)
        
        @see: MotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show where it is called. 
        """       
        pass     
        
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

        self.exitEditCommandAction.setChecked(True)
        subControlAreaActionList.append(self.exitEditCommandAction)

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
        Add the Insert Nanotube Property Manager group boxes.
        """        
       
        self._pmGroupBox1 = PM_GroupBox( self, title = "Endpoints" )
        self._loadGroupBox1( self._pmGroupBox1 )
        self._pmGroupBox1.hide()
        
        self._pmGroupBox2 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox2( self._pmGroupBox2 )
        
        self._pmGroupBox3 = PM_GroupBox( self, title = "Nanotube Distortion" )
        self._loadGroupBox3( self._pmGroupBox3 )
        self._pmGroupBox3.hide() #@ Temporary.
        
        self._pmGroupBox4 = PM_GroupBox( self, title = "Multi-Walled CNTs" )
        self._loadGroupBox4( self._pmGroupBox4 )
        self._pmGroupBox4.hide() #@ Temporary.
        
        self._pmGroupBox5 = PM_GroupBox( self, title = "Advanced Options" )
        self._loadGroupBox5( self._pmGroupBox5 )
        self._pmGroupBox5.hide() #@ Temporary.
       
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """
        #Following toolbutton facilitates entering a temporary NanotubeLineMode
        #to create a CNT using endpoints of the specified line. 
        self.specifyCntLineButton = PM_ToolButton(
            pmGroupBox, 
            text = "Specify Endpoints",
            iconPath  = "ui/actions/Properties Manager"\
            "/Pencil.png",
            spanWidth = True                        
        )
        self.specifyCntLineButton.setCheckable(True)
        self.specifyCntLineButton.setAutoRaise(True)
        self.specifyCntLineButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)
    
        #EndPoint1 and endPoint2 coordinates. These widgets are hidden 
        # as of 2007- 12 - 05
        self._endPoint1SpinBoxes = PM_CoordinateSpinBoxes(pmGroupBox, 
                                                label = "End Point 1")
        self.x1SpinBox = self._endPoint1SpinBoxes.xSpinBox
        self.y1SpinBox = self._endPoint1SpinBoxes.ySpinBox
        self.z1SpinBox = self._endPoint1SpinBoxes.zSpinBox
        
        self._endPoint2SpinBoxes = PM_CoordinateSpinBoxes(pmGroupBox, 
                                                label = "End Point 2")
        self.x2SpinBox = self._endPoint2SpinBoxes.xSpinBox
        self.y2SpinBox = self._endPoint2SpinBoxes.ySpinBox
        self.z2SpinBox = self._endPoint2SpinBoxes.zSpinBox
        
        self._endPoint1SpinBoxes.hide()
        self._endPoint2SpinBoxes.hide()
       
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box 2.
        """

        _ntTypeChoices = ['Carbon', 
                          'Boron Nitride']
        self.ntTypeComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Type:", 
                         choices       =  _ntTypeChoices,
                         setAsDefault  =  True)
        
        self.ntRiseDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Rise:",
                              value         =  self._ntRise,
                              setAsDefault  =  True,
                              minimum       =  2.0,
                              maximum       =  4.0,
                              decimals      =  3,
                              singleStep    =  0.01 )
        
        self.ntRiseDoubleSpinBox.hide()
        
        # Nanotube Length
        self.ntLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Nanotube Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.ntLengthLineEdit.setDisabled(True)
        self.ntLengthLineEdit.hide()
        
        # Nanotube Radius
        self.ntRadiusLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Nanotube Radius: ",
                         setAsDefault  =  False)

        self.ntRadiusLineEdit.setDisabled(True)
        self.updateNtRadius()
                
        self.chiralityNSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label        = "Chirality (n) :", 
                        value        = self.n, 
                        setAsDefault = True )
        
        self.chiralityMSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label        = "Chirality (m) :", 
                        value        = self.m, 
                        setAsDefault = True )
                
        self.bondLengthDoubleSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Bond Length :", 
                              value        = CC_GRAPHITIC_BONDLENGTH, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 3.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        self.bondLengthDoubleSpinBox.hide()
        
        endingChoices = ["None", "Hydrogen", "Nitrogen"]
        
        self.endingsComboBox= \
            PM_ComboBox( pmGroupBox,
                         label        = "Endings :", 
                         choices      = endingChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )
        
    def _loadGroupBox3(self, inPmGroupBox):
        """
        Load widgets in group box 3.
        """
        
        self.zDistortionDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Z-distortion :", 
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = 0.0, 
                              maximum      = 10.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        self.xyDistortionDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "XY-distortion :", 
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = 0.0, 
                              maximum      = 2.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        self.twistSpinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Twist :", 
                        value        = 0, 
                        setAsDefault = True,
                        minimum      = 0, 
                        maximum      = 100, # What should maximum be?
                        suffix       = " deg/A" )
        
        self.bendSpinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Bend :", 
                        value        = 0, 
                        setAsDefault = True,
                        minimum      = 0, 
                        maximum      = 360,
                        suffix       = " deg" )

    def _loadGroupBox4(self, inPmGroupBox):
        """
        Load widgets in group box 4.
        """
        
        # "Number of Nanotubes" SpinBox
        self.mwntCountSpinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Number :", 
                        value        = 1, 
                        setAsDefault = True,
                        minimum      = 1, 
                        maximum      = 10,
                        suffix       = " nanotubes" )
        
        self.mwntCountSpinBox.setSpecialValueText("SWNT")
            
        # "Spacing" lineedit.
        self.mwntSpacingDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Spacing :", 
                              value        = 2.46, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 10.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
    def _loadGroupBox5(self, pmGroupBox):
        """
        Load widgets in group box 5.
        """
        self._rubberbandLineGroupBox = PM_GroupBox(
            pmGroupBox,
            title = 'Rubber band Line:')
        
        ntLineChoices = ['Ladder']
        self.ntRubberBandLineDisplayComboBox = \
            PM_ComboBox( self._rubberbandLineGroupBox ,     
                         label         =  " Display As:", 
                         choices       =  ntLineChoices,
                         setAsDefault  =  True)
        
        self.lineSnapCheckBox = \
            PM_CheckBox(self._rubberbandLineGroupBox ,
                        text         = 'Enable line snap' ,
                        widgetColumn = 1,
                        state        = Qt.Checked
                        )

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the Insert Nanotube Property Manager.  
        """
        pass
    
    def ntRiseChanged( self, rise ): 
        """
        Slot for the B{Rise} spinbox.
        """
        #@ Consider moving this code into chiralityFixup(). --Mark
        self.editCommand.ntRise = rise
        self._ntRise = rise
        return
    
    def bondLengthChanged(self, bondLength):
        """
        Slot for the B{Bond Length} spinbox.
        """
        #@ Consider moving this code into chiralityFixup(). --Mark
        #@self.editCommand.ntRise = rise
        self._bond_length = bondLength
        self.updateNtRadius()
        return
    
    def getParameters(self):
        """
        Return the parameters from this property manager to be used to create
        the nanotube. 
        
        @return: A tuple containing the nanotube parameters.
        @rtype: tuple
        
        @see: L{InsertNanotube_EditCommand._gatherParameters} where this is used 
        """
        
        ntType = str(self.ntTypeComboBox.currentText())
        n = self.chiralityNSpinBox.value()
        m = self.chiralityMSpinBox.value()
        _bond_length = self.bondLengthDoubleSpinBox.value()
        
        zdist = self.zDistortionDoubleSpinBox.value()
        xydist = self.xyDistortionDoubleSpinBox.value()
        mwnt_spacing = self.mwntSpacingDoubleSpinBox.value()

        twist = pi * self.twistSpinBox.value() / 180.0
        bend = pi * self.bendSpinBox.value() / 180.0
        endings = self.endingsComboBox.currentText()
        if endings == "Capped" and not debug_flags.atom_debug:
            raise Exception('Nanotube endcaps not implemented yet.')
        numwalls = self.mwntCountSpinBox.value()
        
        # First endpoint (origin) of nanotube
        x1 = self.x1SpinBox.value()
        y1 = self.y1SpinBox.value()
        z1 = self.z1SpinBox.value()

        # Second endpoint (direction vector/axis) of nanotube.
        x2 = self.x2SpinBox.value()
        y2 = self.y2SpinBox.value()
        z2 = self.z2SpinBox.value()

        if not self.endPoint1:
            self.endPoint1 = V(x1, y1, z1)
        if not self.endPoint2:
            self.endPoint2 = V(x2, y2, z2)
        
        return (self.ntChirality, ntType, n, m, _bond_length, endings,
                zdist, xydist, twist, bend, 
                numwalls, mwnt_spacing,
                self.endPoint1, self.endPoint2)
    
    def _ntTypeComboBoxChanged( self, inIndex ):
        """
        Slot for the Type combobox. It is called whenever the
        Type choice is changed.

        @param inIndex: The new index.
        @type  inIndex: int
        """
        type  =  self.ntTypeComboBox.currentText()

        if type not in ("Carbon", "Boron Nitride"):
            msg = redmsg("ntTypeComboBoxChanged(): \
                         Error - unknown nanotube type. Index = "+ inIndex)
            env.history.message(msg)
        
        self.bondLengthDoubleSpinBox.setValue(ntBondLengths[inIndex])
        
    def _chiralityFixup(self, spinBoxValueJunk = None):
        """
        Slot for several validators for different parameters.
        This gets called each time a user types anything into a widget or 
        changes a spinbox.
        
        @param spinBoxValueJunk: This is the Spinbox value from the valueChanged
                                 signal. It is not used. We just want to know
                                 that the spinbox value has changed.
        @type  spinBoxValueJunk: double or None  
        """
                
        if not hasattr(self, 'n'):
            print_compact_traceback("Bug: no attr 'n' ") # mark 2007-05-24
            return
        
        n_previous = int(self.n)
        m_previous = int(self.m)
        n = self.chiralityNSpinBox.value()
        m = self.chiralityMSpinBox.value()
        # Two restrictions to maintain
        # n >= 2
        # 0 <= m <= n
        if n < 2:
            n = 2
        if m != self.m:
            # The user changed m. If m became larger than n, make n bigger.
            if m > n:
                n = m
        elif n != self.n:
            # The user changed n. If n became smaller than m, make m smaller.
            if m > n:
                m = n
        
        self.n = n
        self.m = m
        
        self.chiralityNSpinBox.setValue(n)
        self.chiralityMSpinBox.setValue(m)
        self.ntRiseDoubleSpinBox.setValue(getCntRise(self._ntType, n, m))
        self.updateNtRadius()
    
    def updateNtRadius(self):
        """
        Update the nanotube Radius lineEdit widget.
        """
        self.ntChirality.update(self.n, self.m, 
                                 self._ntType, 
                                 self._bond_length)
        radiusText = "%-7.4f Angstroms" %  (self.ntChirality.getRadius())
        self.ntRadiusLineEdit.setText(radiusText)
        
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        #@whatsThis_InsertNanotube_PropertyManager(self)
        return 

