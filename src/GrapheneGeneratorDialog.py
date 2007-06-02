# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

$Id$

History:

Mark 2007-05-17: This used to be generated from its .ui file. Now it uses PropMgrBaseClass
  to construct its property manager dialog.

"""
        
__author__ = "Mark"

import sys
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from PropMgrBaseClass import *
from PropMgr_Constants import *
from bonds import CC_GRAPHITIC_BONDLENGTH

class GraphenePropMgr(object, PropMgrBaseClass):
    
    # <title> - the title that appears in the property manager header.
    title = "Graphene Sheet"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Graphene.png"
    
    def __init__(self):
        """Construct the Graphene Property Manager.
        """
        PropMgrBaseClass.__init__(self, self.propmgr_name)
        self.setPropMgrIcon(self.iconPath)
        self.setPropMgrTitle(self.title)
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        
        msg = "Edit the Graphene sheet parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=True)
        
    def addGroupBoxes(self):
        """Add the 1 groupbox for the Graphene Property Manager.
        """
        self.addGroupBoxSpacer()
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Graphene Parameters",
                                           titleButton=True)
        self.loadGroupBox1(self.pmGroupBox1)
        
        AddTestGroupBox = False # For testing. Mark 2007-05-24
        
        if not AddTestGroupBox: # Add test widgets to their own groupbox.
            return
        
        self.addGroupBoxSpacer()
        self.testGroupBox1 = PropMgrGroupBox(self, 
                                           title="Test Widgets1",
                                           titleButton=True)
        self.loadTestWidgets1(self.testGroupBox1)
        
        self.addGroupBoxSpacer()
        self.testGroupBox2 = PropMgrGroupBox(self, 
                                           title="Test Widgets2",
                                           titleButton=True)
        self.loadTestWidgets2(self.testGroupBox2)
              
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        self.heightField = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Height :", 
                                val=20.0, setAsDefault=True,
                                min=1.0, max=50.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
        self.widthField = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Width :", 
                                val=20.0, setAsDefault=True,
                                min=1.0, max=50.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
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
        
    def loadTestWidgets1(self, pmGroupBox):
        """Adds widgets to <pmGroupBox>.
        Used for testing purposes. Mark 2007-05-24
        """
        
        # I intend to create a special PropMgr to display all widget types
        # for testing purposes. For now, I just add them to the end of the
        # Graphene Sheet property manager. Mark 2007-05-22
        
        
        self.spinBox = PropMgrSpinBox(pmGroupBox, 
                                      label="Spinbox :", 
                                      val=5, setAsDefault=True,
                                      min=2, max=10, 
                                      suffix=' things',
                                      spanWidth=True)
            
        self.doubleSpinBox = \
                PropMgrDoubleSpinBox(pmGroupBox, 
                                    #label="Spanning DoubleSpinBox :",
                                    label="", # No label
                                    val=5.0, setAsDefault=True,
                                    min=1.0, max=10.0, 
                                    singleStep=1.0, decimals=1, 
                                    suffix=' Suffix',
                                    spanWidth=True)
            
        # Add a prefix example.
        self.doubleSpinBox.setPrefix("Prefix ")
            
        choices = ["First", "Second", "Third (Default)", "Forth"]
        self.comboBox= \
                PropMgrComboBox(pmGroupBox,
                                label='Choices : ', 
                                choices=choices, 
                                idx=2, setAsDefault=True,
                                spanWidth=True)
        
        self.textEdit = PropMgrTextEdit(pmGroupBox, 
                                        label="TextEdit :", 
                                        spanWidth=False)
        
        self.spanTextEdit = PropMgrTextEdit(pmGroupBox, 
                                        label="", 
                                        spanWidth=True)
            
        self.groupBox = PropMgrGroupBox(pmGroupBox, 
                                        title="Group Box Title",
                                        titleButton=False)
            
        self.comboBox2= \
                PropMgrComboBox(self.groupBox,
                                label="Choices :", 
                                choices=choices, 
                                idx=2, setAsDefault=True,
                                spanWidth=False)
        
        self.pushButton1 = \
            PropMgrPushButton(pmGroupBox,
                              label="",
                              text="PushButton1")
        
        self.pushButton2 = \
            PropMgrPushButton(pmGroupBox,
                              label="",
                              text="PushButton2",
                              spanWidth=True)
    
    def loadTestWidgets2(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        self.lineEdit1 = \
            PropMgrLineEdit(pmGroupBox, 
                            label="Name :",
                            text="RotaryMotor-1",
                            setAsDefault=True,
                            spanWidth=False)
        
        self.lineEdit2 = \
            PropMgrLineEdit(pmGroupBox, 
                            label="Span Width LineEdit :",
                            text="RotaryMotor-1",
                            setAsDefault=False,
                            spanWidth=True)
        
        self.checkBox1 = \
            PropMgrCheckBox(pmGroupBox,
                              label="CheckBox :",
                              isChecked=True,
                              setAsDefault=True,
                              spanWidth=False)
        self.checkBox2 = \
            PropMgrCheckBox(pmGroupBox,
                              label="SpanWidth CheckBox :",
                              isChecked=False,
                              setAsDefault=False,
                              spanWidth=True)
        
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager.
        """
        
        self.heightField.setWhatsThis("""<b>Height</b>
        <p>The height (up to 50 Angstroms) of the graphite sheet 
        in angstroms.</p>""")
        
        self.widthField.setWhatsThis("""<b>Width</b>
        <p>The width (up to 50 Angstroms) of the graphene sheet 
        in angstroms.</p>""")
        
        self.bondLengthField.setWhatsThis("""<b>Bond length</b>
        <p>You can change the bond lengths (1.0-3.0 Angstroms) in the
        graphene sheet. We believe the default value is accurate for sp
        <sup>2</sup>-hybridized carbons.</p>""")
        
        self.endingsComboBox.setWhatsThis("""<b>Endings</b>
        <p>Graphene sheets can be unterminated (dangling
        bonds), or terminated with hydrogen atoms or nitrogen atoms.</p>""")
        