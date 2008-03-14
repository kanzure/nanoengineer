# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

History:

Mark 2007-05-18: Implemented Nanotube generator dialog using PropMgrBaseClass.
Mark 2007-08-06: Renamed NanotubeGeneratorDialog to NanotubeGeneratorPropertyManager.
"""

import math

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import SIGNAL

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_SpinBox       import PM_SpinBox

from model.bonds import CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH
from utilities.debug import print_compact_traceback

ntBondLengths = [CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH]

class NanotubeGeneratorPropertyManager(PM_Dialog):
    """
    The NanotubeGeneratorPropertyManager class provides a Property Manager 
    for the "Build > Nanotube" command.
    """
    # The title that appears in the property manager header.
    title = "Nanotube"
    # The name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Nanotube.png"
    
    def __init__(self):
        """Construct the Graphene Property Manager.
        """
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        #@self.addGroupBoxes()
        #@self.add_whats_this_text()
        self.updateMessageGroupBox()
        
    def updateMessageGroupBox(self):
        msg = ""

        # A (4, 4) tube is stable, but a (3, 3) has not been seen in
        # isolation.  Circumference of a (4, 4) tube is about 6.93.
        xOffset = self.n + self.m * math.cos(math.pi/3.0)
        yOffset = self.m * math.sin(math.pi/3.0)
        circumference = math.sqrt(xOffset * xOffset + yOffset * yOffset)
        if (circumference < 6.5):
            msg = "Warning: Small diameter nanotubes may be unstable, \
            and may give unexpected results when minimized.<p>"

        msg = msg + "Edit the Nanotube parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=True)

        
    def _addGroupBoxes(self):
        """
        Add the 3 group boxes to the Nanotube Property Manager dialog.
        """
        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title          = "Nanotube Parameters" )
                
        self.pmGroupBox2 = \
            PM_GroupBox( self, 
                         title          = "Nanotube Distortion" )
                
        self.pmGroupBox3 = \
            PM_GroupBox( self, 
                         title          = "Multi-Walled Nanotubes" )

        # Add group box widgets.
        self._loadGroupBox1(self.pmGroupBox1)
        self._loadGroupBox2(self.pmGroupBox2)
        self._loadGroupBox3(self.pmGroupBox3)
        
    def _loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets in group box 1.
        """
        
        memberChoices = ["Carbon", "Boron Nitride"]
        self.typeComboBox= \
            PM_ComboBox( inPmGroupBox,
                         label        = "Type :", 
                         choices      = memberChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.connect( self.typeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.nt_type_changed)
            
        self.lengthField = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "Length :", 
                              value        = 20.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 1000.0, 
                              singleStep   = 1.0, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        self.n = 5
        
        self.chiralityNSpinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Chirality (n) :", 
                        value        = self.n, 
                        setAsDefault = True )
        
        self.connect(self.chiralityNSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.chirality_fixup)
        
        self.m = 5
        
        self.chiralityMSpinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Chirality (m) :", 
                        value        = self.m, 
                        setAsDefault = True )
        
        self.connect(self.chiralityMSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.chirality_fixup)
        
        self.bondLengthField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Bond Length :", 
                              value        = CC_GRAPHITIC_BONDLENGTH, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 3.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        endingChoices = ["None", "Hydrogen", "Nitrogen"]
        
        self.endingsComboBox= \
            PM_ComboBox( inPmGroupBox,
                         label        = "Endings :", 
                         choices      = endingChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )
        
    def _loadGroupBox2(self, inPmGroupBox):
        """
        Load widgets in group box 2.
        """
        
        self.zDistortionField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Z-distortion :", 
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = 0.0, 
                              maximum      = 10.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
        
        self.xyDistortionField = \
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
    
    def _loadGroupBox3(self, inPmGroupBox):
        """
        Load widgets in group box 3.
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
        self.mwntSpacingField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Spacing :", 
                              value        = 2.46, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 10.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = " Angstroms" )
    
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_NanotubeGeneratorPropertyManager
        whatsThis_NanotubeGeneratorPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_NanotubeGeneratorPropertyManager
        ToolTip_NanotubeGeneratorPropertyManager(self)
        
    def chirality_fixup(self, spinBoxValueJunk = None):
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
        self.chiralityNSpinBox.setValue(n)
        self.chiralityMSpinBox.setValue(m)
        self.m, self.n = m, n
        self.updateMessageGroupBox()

    def nt_type_changed(self, idx):
        """
        Slot for Nanotube Type combobox.
        Update the bond length field when the type changes.
        """
        self.bondLengthField.setValue(ntBondLengths[idx])
