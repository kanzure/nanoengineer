# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

History:

Mark 2007-05-18: Implemented Nanotube generator dialog using PropMgrBaseClass.
"""

import math

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import SIGNAL

from Utility import geticon, getpixmap
from PropMgrBaseClass import PropMgrBaseClass
from PropMgrBaseClass import PropMgrGroupBox
from PropMgrBaseClass import PropMgrComboBox
from PropMgrBaseClass import PropMgrDoubleSpinBox
from PropMgrBaseClass import PropMgrSpinBox
from bonds import CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH
from debug import print_compact_traceback

ntBondLengths = [CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH]

class NanotubePropMgr(object, PropMgrBaseClass):
    
    # <title> - the title that appears in the property manager header.
    title = "Nanotube"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Nanotube.png"
    
    def __init__(self):
        """Construct the Graphene Property Manager.
        """
        PropMgrBaseClass.__init__(self, self.propmgr_name)
        self.setPropMgrIcon(self.iconPath)
        self.setPropMgrTitle(self.title)
        self.addGroupBoxes()
        self.add_whats_this_text()
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

        
    def addGroupBoxes(self):
        """Add the 3 groupboxes for the Nanotube Property Manager.
        """
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Nanotube Parameters",
                                           titleButton=True)
        self.loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PropMgrGroupBox(self, 
                                           title="Nanotube Distortion",
                                           titleButton=True)
        self.loadGroupBox2(self.pmGroupBox2)
        
        self.pmGroupBox3 = PropMgrGroupBox(self, 
                                           title="Multi-Walled Nanotubes",
                                           titleButton=True)
        self.loadGroupBox3(self.pmGroupBox3)
        
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        memberChoices = ["Carbon", "Boron Nitride"]
        self.typeComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Type :", 
                            choices=memberChoices, 
                            idx=0, setAsDefault=True,
                            spanWidth=False)
        
        self.connect(self.typeComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.nt_type_changed)
            
        self.lengthField = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Length :", 
                                val=20.0, setAsDefault=True,
                                min=1.0, max=1000.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
        self.n = 5
        
        self.chiralityNSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Chirality (n) :", 
                            val=self.n, setAsDefault=True)
        
        self.connect(self.chiralityNSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.chirality_fixup)
        
        self.m = 5
        
        self.chiralityMSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Chirality (m) :", 
                            val=self.m, setAsDefault=True)
        
        self.connect(self.chiralityMSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.chirality_fixup)
        
        self.bondLengthField = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Bond Length :", 
                                val=CC_GRAPHITIC_BONDLENGTH, setAsDefault=True,
                                min=1.0, max=3.0, 
                                singleStep=0.1, decimals=3, 
                                suffix=' Angstroms')
        
        endingChoices = ["None", "Hydrogen", "Nitrogen"]
        self.endingsComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Endings :", 
                            choices=endingChoices, 
                            idx=0, setAsDefault=True,
                            spanWidth=False)
        
    def loadGroupBox2(self, pmGroupBox):
        """Load widgets in groubox 2.
        """
        
        self.zDistortionField = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Z-distortion :", 
                                val=0.0, setAsDefault=True,
                                min=0.0, max=10.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
        self.xyDistortionField = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="XY-distortion :", 
                                val=0.0, setAsDefault=True,
                                min=0.0, max=2.0, 
                                singleStep=0.1, decimals=1, 
                                suffix=' Angstroms')
        
        
        self.twistSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Twist :", 
                            val=0, setAsDefault=True,
                            min=0, max=100, # What should max be?
                            suffix=" deg/A")
        
        self.bendSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Bend :", 
                            val=0, setAsDefault=True,
                            min=0, max=360,
                            suffix=" deg")
    
    def loadGroupBox3(self, pmGroupBox):
        """Load widgets in groubox 3.
        """
        
        # "Number of Nanotubes" SpinBox
        self.mwntCountSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Number :", 
                            val=1, setAsDefault=True,
                            min=1, max=10,
                            suffix=' nanotubes')
        
        self.mwntCountSpinBox.setSpecialValueText("SWNT")
            
        # "Spacing" lineedit.
        self.mwntSpacingField = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Spacing :", 
                                val=2.46, setAsDefault=True,
                                min=1.0, max=10.0, 
                                singleStep=0.1, decimals=2, 
                                suffix=' Angstroms')
    
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager.
        """
        
        self.chiralityNSpinBox.setWhatsThis("""<b>Chirality (n)</b>
        <p>Specifies <i>n</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation R = na1 + ma2 .</p>""")
        
        self.chiralityMSpinBox.setWhatsThis("""<b>Chirality (m)</b>
        <p>Specifies <i>m</i> of the chiral vector
        (n, m), where n and m are integers of the vector equation R = na1 + ma2 .</p>""")
                
        self.typeComboBox.setWhatsThis("""<b>Type</b>
        <p>Specifies the type of nanotube to generate.</p>
        <p>Selecting
        <b>Carbon</b> creates a carbon nanotube (CNT) made entirely of carbon atoms.
        <p>Selecting <b>Boron nitride</b> creates a
        boron nitride (BN) nanotube made of boron and nitrogen atoms.</p>""")
        
        self.endingsComboBox.setWhatsThis("""<b>Endings</b>
        <p>Specify how to deal with bondpoints on the
        two ends of the nanotube.</p>
        <p>Selecting <b>None</b> does nothing, leaving bondpoints on the ends.</p>
        <p>Selecting <b>Hydrogen
        </b>terminates the bondpoints using hydrogen atoms.</p>
        <p>Selecting <b>Nitrogen </b>transmutes atoms with bondpoints into
        nitrogen atoms.</p>""")
        
        self.lengthField.setWhatsThis("""<b>Length</b>
        <p>Specify the length of the nanotube in angstroms.</p>""")
        
        self.bondLengthField.setWhatsThis("""<b>Bond Length</b>
        <p>Specify the bond length between atoms in
        angstroms.</p>""")
        
        self.twistSpinBox.setWhatsThis("""<b>Twist</b>
        <p>Introduces a twist along the length of the nanotube
        specified in degrees/angstrom.</p>""")
        
        self.zDistortionField.setWhatsThis("""<b>Z-distortion</b>
        <p>Distorts the bond length between atoms
        along the length of the nanotube by this amount in angstroms.</p>""")
        
        self.bendSpinBox.setWhatsThis("""<b>Bend</b>
        <p>Bend the nanotube by the specified number of degrees.</p>""")
        
        self.xyDistortionField.setWhatsThis("""<b>XY-distortion</b>
        <p>Distorts the tube's cross-section so
        that the width in the X direction is this many angstroms greater than the width in the Y direction. Some distortion  of bond
        lengths results.</p>""")
        
        self.mwntCountSpinBox.setWhatsThis("""<b>Number of Nanotubes</b>
        <p>Specifies the number or Multi-Walled
        Nanotubes. Multi-Walled nanotubes (MWNT) consist of many concentric tubes wrapped one inside another.</p>
        <p>The specified
        chirality applies only to the innermost nanotube. The others, being larger, will have larger chiralities.
        </p>""")
        
        self.mwntSpacingField.setWhatsThis("""<b>Spacing</b>
        <p>Specify the spacing between nanotubes in angstroms.</p>""")     
        
    def chirality_fixup(self):
        '''Slot for several validators for different parameters.
        This gets called each time a user types anything into a widget or changes a spinbox.
        '''
        
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
        """Slot for Nanotube Type combobox.
        Update the bond length field when the type changes.
        """
        self.bondLengthField.setValue(ntBondLengths[idx])
