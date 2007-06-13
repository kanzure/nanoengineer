# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

$Id$

History:

Jeff 2007-05-29: Based on Mark Sims' GrapheneGeneratorDialog.py, v1.17

            Convention of variables' names:

                   variable's role     prefix      example
                  -----------------   --------    ---------
                - incoming parameter    in...      inData
                                                   inObjectPointer

                - outgoing parameter               outBufferPointer
                  or function return    out...     outCalculation
                   
                - static variable       s...       sDefaultValue

                - local variable        the...     theUserName
                                                   theTempValue

"""
        
__author__ = "Jeff"

import sys
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from PropMgrBaseClass import *
from PropMgr_Constants import *
from bonds import CC_GRAPHITIC_BONDLENGTH

class AtomPropMgr(object, PropMgrBaseClass):
    """ Implements user interface to specify properties of an atom """

    # <title> - the title that appears in the property manager header.
    title = "Atom Generator"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Toolbars/Smart/Deposit_Atoms.png"

    # Static variables (name prefixed with 's') are used to assure consistency 
    # between related widget and simplify code revision.
    # For example, the unit for coordinates is specified by sCoordinateUnit; all
    # widgets related to coordinates should refer to sCoordinateUnit rather than
    # hardcoding the unit for each coordinate widget.  The advantage is if a 
    # later revision uses different unit (or chosen possibly via a user
    # preference), all related widgets would follow the new choice for units.
    #    Jeff 20070530
    sMinCoordinateValue   =  -10.0
    sMaxCoordiinateValue  =  10.0
    sStepCoordinateValue  =  1.0
    sCoordinateUnit       =  'Angstrom'
    sCoordinateUnits      =  sCoordinateUnit + 's'
    sAvailableElements    =  ["H","O","C","S"]

    def __init__(self):
        """Construct the Atom Property Manager.
        """
        PropMgrBaseClass.__init__( self, self.propmgr_name )
        self.setPropMgrIcon( self.iconPath )
        self.setPropMgrTitle( self.title )
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        
        msg = "Edit the Atom parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert the atom \
        into the model."
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  False )
        
    def addGroupBoxes(self):
        """Add the 1 groupbox for the Atom Property Manager.
        """
        self.addGroupBoxSpacer()
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Atom Parameters", # Jeff 2007-05-30
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
        self.testGroupBox2 = PropMgrGroupBox( self, 
                                              title="Test Widgets2",
                                              titleButton=True)
        self.loadTestWidgets2(self.testGroupBox2)
              
    def loadGroupBox1(self, inPmGroupBox):
        """Load widgets in groupbox 1.
        """
        # These redundant local variables were necessary 
        # to avoid "Attribute Error" when static variables
        # are sent to object constructors (e.g., PropMgrSpinBox)
        #coorMin    =  sMinCoordinateValue
        #coorMax    =  sMaxCoordinateValue
        #coorStep   =  sStepCoordinateValue
        #coorUnits  =  sCoordinateUnits
        coorMin    =  -10
        coorMax    =  10
        coorStep   =  1.0
        coorUnits  =  'Angstroms'

        # User input to specify what type of element/atom to generate
        elementComboBoxItems  =  self.sAvailableElements
        self.elementComboBox  =  \
            PropMgrComboBox( inPmGroupBox,
                             label         =  "Elements :",
                             choices       =  elementComboBoxItems,
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  False )
        
        # User input to specify x-coordinate of the generated atom's position
        self.xCoordinateField  =  \
            PropMgrDoubleSpinBox( inPmGroupBox,
                                  label         =  "x :",
                                  val           =  0.0,
                                  setAsDefault  =  True,
                                  min           =  coorMin,
                                  max           =  coorMax,
                                  singleStep    =  coorStep,
                                  #min           =  sMinCoordinateValue,
                                  #max           =  sMaxCoordinateValue,
                                  #singleStep    =  sStepCoordinateValue,
                                  decimals      =  1,
                                  #suffix        =  ' ' + sCoordinateUnits )
                                  suffix        =  ' ' + coorUnits)

        # User input to specify y-coordinate of the generated atom's position
        self.yCoordinateField  =  \
            PropMgrDoubleSpinBox( inPmGroupBox,
                                  label         =  "y :",
                                  val           =  0.0,
                                  setAsDefault  =  True,
                                  min           =  coorMin,
                                  max           =  coorMax,
                                  singleStep    =  coorStep,
                                  #min           =  sMinCoordinateValue,
                                  #max           =  sMaxCoordinateValue,
                                  #singleStep    =  sStepCoordinateValue,
                                  decimals      =  1,
                                  #suffix        =  ' ' + sCoordinateUnits )
                                  suffix        =  ' ' + coorUnits )

        # User input to specify z-coordinate of the generated atom's position
        self.zCoordinateField = \
            PropMgrDoubleSpinBox( inPmGroupBox,
                                  label         =  "z :",
                                  val           =  0.0,
                                  setAsDefault  =  True,
                                  min           =  coorMin,
                                  max           =  coorMax,
                                  singleStep    =  coorStep,
                                  #min           =  sMinCoordinateValue,
                                  #max           =  sMaxCoordinateValue,
                                  #singleStep    =  sStepCoordinateValue,
                                  decimals      =  1,
                                  #suffix        =  ' ' + sCoordinateUnits )
                                  suffix        =  ' ' + coorUnits )
        
    def loadTestWidgets1(self, pmGroupBox):
        """Adds widgets to <pmGroupBox>.
        Used for testing purposes. Mark 2007-05-24
        """
        
        # I intend to create a special PropMgr to display all widget types
        # for testing purposes. For now, I just add them to the end of the
        # Atom Sheet property manager. Mark 2007-05-22
        
        
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
        """Load widgets in groupbox 1.
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
           Jeff 2007-05-30
        """
        
        self.xCoordinateField.setWhatsThis("""<b>x</b>
        <p>The x-coordinate of the Atom in Angstroms.</p>""")
        #<p>The x-coordinate (up to </p>""" + self.sMaxCoordinateValue + self.sCoordinateUnits \
        #+ """) of the Atom in """ + self.sCoordinateUnits + '.')
        
        self.yCoordinateField.setWhatsThis("""<b>y</b>
        <p>The y-coordinate of the Atom in Angstroms.</p>""")
        #<p>The y-coordinate (up to </p>""" + self.sMaxCoordinateValue + self.sCoordinateUnits \
        #+ """) of the Atom in """ + self.sCoordinateUnits + '.')
        
        self.zCoordinateField.setWhatsThis("""<b>z</b>
        <p>The y-coordinate of the Atom in Angstroms.</p>""")
        #<p>The z-coordinate (up to </p>""" + self.sMaxCoordinateValue + self.sCoordinateUnits \
        #+ """) of the Atom in """ + self.sCoordinateUnits + '.')
        
