# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

$Id$

History:

Mark 2007-05-17: This used to be generated from its .ui file. Now it uses PropMgrBaseClass
  to construct its property manager dialog.

"""
        
__author__ = "Mark"

import sys
from PyQt4 import Qt, QtCore, QtGui
from Utility import geticon, getpixmap
from PyQt4.Qt import *
from PropertyManagerMixin import PropMgrBaseClass
from PropMgr_Constants import *
from bonds import CC_GRAPHITIC_BONDLENGTH

class GraphenePropMgr(object, PropMgrBaseClass):
    
    def __init__(self):
        """Construct the Graphene Property Manager.
        """
        PropMgrBaseClass.__init__(self)
        self.setPropMgrIcon('ui/actions/Tools/Build Structures/Graphene.png')
        self.setPropMgrTitle("Graphene Sheet")
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        self.connect_or_disconnect_signals(connect=True)
        
        msg = "Edit the Graphene sheet parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        self.insertHtmlMsg(msg)
        
    def addGroupBoxes(self):
        """Add the 1 groupbox for the Graphene Property Manager.
        """
        self.addGroupBox1("Parameters")
              
    def addGroupBox1(self, title):
        """Adds a spacer, then it creates layout and widgets for the 
        "DNA Parameters" groupbox.
        """
        
        self.addGroupBoxSpacer()
                
        self.pmGroupBox1 = QtGui.QGroupBox(self)
        self.pmGroupBox1.setObjectName("pmGroupBox1")
        
        self.pmGroupBox1.setAutoFillBackground(True) 
        palette =  self.getGroupBoxPalette()
        self.pmGroupBox1.setPalette(palette)
        
        styleSheet = self.getGroupBoxStyleSheet()        
        self.pmGroupBox1.setStyleSheet(styleSheet)
        
        # Create vertical box layout
        GrpBox1MainVBoxLayout = QtGui.QVBoxLayout(self.pmGroupBox1)
        GrpBox1MainVBoxLayout.setMargin(pmGrpBoxVboxLayoutMargin)
        GrpBox1MainVBoxLayout.setSpacing(pmGrpBoxVboxLayoutSpacing)

        # Title button for groupbox1
        
        self.pmGroupBoxBtn1 = self.getGroupBoxTitleButton(
            title, self.pmGroupBox1)
        
        GrpBox1MainVBoxLayout.addWidget(self.pmGroupBoxBtn1)
        
        # Create grid layout
        GrpBox1GridLayout1 = QtGui.QGridLayout()
        GrpBox1GridLayout1.setMargin(pmGridLayoutMargin)
        GrpBox1GridLayout1.setSpacing(pmGridLayoutSpacing)
        
        # Height Label
        self.height_label = QtGui.QLabel(self.pmGroupBox1)
        self.height_label.setAlignment(Qt.AlignRight|
                                       Qt.AlignTrailing|
                                       Qt.AlignVCenter)
        self.height_label.setObjectName("height_label")
        self.height_label.setText("Height (A) :")
        GrpBox1GridLayout1.addWidget(self.height_label,1,0,1,1)

        # Height LineEdit
        self.height_linedit = QtGui.QLineEdit(self.pmGroupBox1)
        self.height_linedit.setObjectName("height_linedit")
        self.height_linedit.setText("20.0")
        GrpBox1GridLayout1.addWidget(self.height_linedit,1,1,1,1)

        # Width Label
        self.width_label = QtGui.QLabel(self.pmGroupBox1)
        self.width_label.setAlignment(Qt.AlignRight|
                                      Qt.AlignTrailing|
                                      Qt.AlignVCenter)
        self.width_label.setObjectName("width_label")
        self.width_label.setText("Width (A) :")
        GrpBox1GridLayout1.addWidget(self.width_label,2,0,1,1)

        # Width LineEdit
        self.width_linedit = QtGui.QLineEdit(self.pmGroupBox1)
        self.width_linedit.setObjectName("width_linedit")
        self.width_linedit.setText("20.0")
        GrpBox1GridLayout1.addWidget(self.width_linedit,2,1,1,1)

        # Bond Length Label
        self.bond_length_label = QtGui.QLabel(self.pmGroupBox1)
        self.bond_length_label.setAlignment(Qt.AlignRight|
                                            Qt.AlignTrailing|
                                            Qt.AlignVCenter)
        self.bond_length_label.setObjectName("bond_length_label")
        self.bond_length_label.setText("Bond Length (A) :")
        GrpBox1GridLayout1.addWidget(self.bond_length_label,3,0,1,1)

        # Bond Length LineEdit
        self.bond_length_linedit = QtGui.QLineEdit(self.pmGroupBox1)
        self.bond_length_linedit.setObjectName("bond_length_linedit")
        GrpBox1GridLayout1.addWidget(self.bond_length_linedit,3,1,1,1)

        # Endings Label
        self.endings_label = QtGui.QLabel(self.pmGroupBox1)
        self.endings_label.setAlignment(Qt.AlignRight|
                                        Qt.AlignTrailing|
                                        Qt.AlignVCenter)
        self.endings_label.setObjectName("endings_label")
        self.endings_label.setText("Endings :")
        GrpBox1GridLayout1.addWidget(self.endings_label,4,0,1,1)

        # Endings ComboBox
        self.endings_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.endings_combox.setObjectName("endings_combox")
        self.endings_combox.addItem("None")
        self.endings_combox.addItem("Hydrogen")
        self.endings_combox.addItem("Nitrogen")
        GrpBox1GridLayout1.addWidget(self.endings_combox,4,1,1,1)
        
        GrpBox1MainVBoxLayout.addLayout(GrpBox1GridLayout1)
        
        self.pmMainVboxLO.addWidget(self.pmGroupBox1) # Add groupbox
        
        # Last minute stuff.
        
        # Validator for the linedit widgets.
        self.validator = QDoubleValidator(self)
        # Range for linedits: 1 to 1000, 3 decimal places
        self.validator.setRange(1.0, 1000.0, 3)
        self.height_linedit.setValidator(self.validator)
        self.width_linedit.setValidator(self.validator)
        self.bond_length_linedit.setValidator(self.validator)
        self.hstr = self.height_linedit.text()
        self.wstr = self.width_linedit.text()
        self.blstr = self.bond_length_linedit.text()
        self.bond_length_linedit.setText(str(CC_GRAPHITIC_BONDLENGTH))


    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager.
        """
        
        self.height_linedit.setWhatsThis("""<b>Height</b>
        <p>The height of the graphite sheet in angstroms.</p>""")
        
        self.width_linedit.setWhatsThis("""<b>Width</b>
        <p>The width of the graphene sheet in angstroms.</p>""")
        
        self.bond_length_linedit.setWhatsThis("""<b>Bond length</b>
        <p>You can change the bond lengths in the
        graphene sheet. We believe the default value is accurate for sp
        <sup>2</sup>-hybridized carbons.</p>""")
        
        self.endings_combox.setWhatsThis("""<b>Endings</b>
        <p>Graphene sheets can be unterminated (dangling
        bonds), or terminated with hydrogen atoms or nitrogen atoms.</p>""")
        
    def connect_or_disconnect_signals(self, connect=True):
        """Connect/disconnect this pmgr's widgets signals to/from their slots.
        If <connect> is False, disconnect all slots listed.
        """
        
        if connect:
            contype = self.connect
        else:
            contype = self.disconnect
        
        # Groupbox Toggle Buttons.
        contype(self.pmGroupBoxBtn1,SIGNAL("clicked()"),
                self.toggle_pmGroupBox1)
       
        # Groupbox1.
        contype(self.height_linedit,
                SIGNAL("returnPressed()"),
                self.length_fixup)
        contype(self.width_linedit,
                SIGNAL("returnPressed()"),
                self.length_fixup)
        contype(self.bond_length_linedit,
                SIGNAL("returnPressed()"),
                self.length_fixup)
        
    # GroupBox1 slots (and other methods) supporting the DNA Parameters groupbox.
        
    def length_fixup(self):
        '''Slot for various linedit widgets.
        This gets called each time a user types anything into the widget.
        '''
        hstr = double_fixup(self.validator, self.height_linedit.text(), self.hstr)
        self.height_linedit.setText(hstr)
        wstr = double_fixup(self.validator, self.width_linedit.text(), self.wstr)
        self.width_linedit.setText(wstr)
        blstr = double_fixup(self.validator, self.bond_length_linedit.text(), self.blstr)
        self.bond_length_linedit.setText(blstr)
        self.hstr, self.wstr, self.blstr = hstr, wstr, blstr
        
        
    # Collapse/expand toggle slots for groupbox buttons.
    
    def toggle_pmGroupBox1(self):
        self.toggle_groupbox(self.pmGroupBoxBtn1,
                             self.height_label, self.height_linedit,
                             self.width_label, self.width_linedit,
                             self.bond_length_label, self.bond_length_linedit,
                             self.endings_label, self.endings_combox)