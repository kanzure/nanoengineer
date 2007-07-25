# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

$Id$

History:

Mark 2007-05-17: This used to be generated from its .ui file. Now it uses PropMgrBaseClass
  to construct its property manager dialog.
Mark 2007-07-24: GrapheneGeneratorDialog now uses new PM module.

"""
        
__author__ = "Mark"

from Utility import geticon, getpixmap
from bonds import CC_GRAPHITIC_BONDLENGTH

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_TextEdit      import PM_TextEdit
from PM.PM_PushButton    import PM_PushButton
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_CheckBox      import PM_CheckBox

class GrapheneGeneratorDialog(PM_Dialog):
    """
    The GrapheneGeneratorDialog class provides a Property Manager dialog for the
    "Build Graphene (Sheet)" command.
    """
    # The title that appears in the property manager header.
    title = "Graphene Sheet"
    # The name of this property manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Graphene.png"
    
    def __init__(self):
        """
        Construct the "Build Graphene" Property Manager.
        """
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        self.addGroupBoxes() 
        self.add_whats_this_text()
        
        msg = "Edit the Graphene sheet parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=True)
        
    def addGroupBoxes(self):
        """
        Add the group boxes to the Graphene Property Manager dialog.
        """
        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title          = "Graphene Parameters",
                         addTitleButton = True )
        
        self.loadGroupBox1(self.pmGroupBox1)
        
        AddTestGroupBoxes = False # For testing. Mark 2007-05-24
        
        if not AddTestGroupBoxes: # Add test widgets to their own groupbox.
            return
        
        self.testGroupBox1 = \
            PM_GroupBox( self, 
                         title          = "Test Widgets1",
                         addTitleButton = True )
        
        self.loadTestWidgets1(self.testGroupBox1)
        
        self.testGroupBox2 = \
            PM_GroupBox( self, 
                         title          = "Test Widgets2",
                         addTitleButton = True )
        
        self.loadTestWidgets2(self.testGroupBox2)
              
    def loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in groubox 1.
        """
        
        self.heightField = \
            PM_DoubleSpinBox( pmGroupBox, 
                              label        = "Height :", 
                              value        = 20.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 50.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms' )
        
        self.widthField = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Width :", 
                              value        = 20.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 50.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms')
        
        self.bondLengthField = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Bond Length :", 
                              value        = CC_GRAPHITIC_BONDLENGTH, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 3.0, 
                              singleStep   = 0.1, 
                              decimals     = 3, 
                              suffix       = ' Angstroms')
        
        endingChoices = ["None", "Hydrogen", "Nitrogen"]
        
        self.endingsComboBox= \
            PM_ComboBox( pmGroupBox,
                         label        = "Endings :", 
                         choices      = endingChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )
        
    def loadTestWidgets1(self, pmGroupBox):
        """
        Adds widgets to <pmGroupBox>.
        Used for testing purposes. Mark 2007-05-24
        """
        
        # I intend to create a special PropMgr to display all widget types
        # for testing purposes. For now, I just add them to the end of the
        # Graphene Sheet property manager. Mark 2007-05-22
        
        self.spinBox = \
            PM_SpinBox( pmGroupBox, 
                            label        = "Spinbox :", 
                            value        = 5, 
                            setAsDefault = True,
                            minimum      = 2, 
                            maximum      = 10, 
                            suffix       = ' things',
                            spanWidth    = True )
            
        self.doubleSpinBox = \
                PM_DoubleSpinBox( pmGroupBox, 
                                  #label="Spanning DoubleSpinBox :",
                                  label        = "", # No label
                                  value        = 5.0, 
                                  setAsDefault = True,
                                  minimum      = 1.0, 
                                  maximum      = 10.0, 
                                  singleStep   = 1.0, 
                                  decimals     = 1, 
                                  suffix       = ' Suffix',
                                  spanWidth    = True )
            
        # Add a prefix example.
        self.doubleSpinBox.setPrefix("Prefix ")
            
        choices = [ "First", "Second", "Third (Default)", "Forth" ]
        
        self.comboBox= \
            PM_ComboBox( pmGroupBox,
                         label        = 'Choices : ', 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = True )
        
        self.textEdit = \
            PM_TextEdit( pmGroupBox, 
                         label     = "TextEdit :", 
                         spanWidth = False )
        
        
        self.spanTextEdit = \
            PM_TextEdit( pmGroupBox, 
                         label     = "", 
                         spanWidth = True )
        
        
        self.groupBox = \
            PM_GroupBox( pmGroupBox, 
                         title          = "Group Box Title",
                         addTitleButton = False )
            
        self.comboBox2= \
            PM_ComboBox( self.groupBox,
                         label        = "Choices :", 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.groupBox2 = \
            PM_GroupBox( pmGroupBox, 
                         title          = "Group Box Title",
                         addTitleButton = False)
            
        self.comboBox3= \
            PM_ComboBox( self.groupBox2,
                         label        = "Choices :", 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = False)
        
        self.pushButton1 = \
            PM_PushButton( pmGroupBox,
                           label = "",
                           text  = "PushButton1")
        
        self.pushButton2 = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "PushButton2",
                           spanWidth = True )
    
    def loadTestWidgets2(self, pmGroupBox):
        """
        Load widgets in groubox 1.
        """
        
        self.lineEdit1 = \
            PM_LineEdit( pmGroupBox, 
                         label        = "Name :",
                         text         = "RotaryMotor-1",
                         setAsDefault = True,
                         spanWidth    = False)
        
        self.lineEdit2 = \
            PM_LineEdit( pmGroupBox, 
                         label        = "Span Width LineEdit :",
                         text         = "RotaryMotor-1",
                         setAsDefault = False,
                         spanWidth    = True)
        
        self.checkBox1 = \
            PM_CheckBox( pmGroupBox,
                         label        = "CheckBox :",
                         isChecked    = True,
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.checkBox2 = \
            PM_CheckBox( pmGroupBox,
                         label        = "SpanWidth CheckBox :",
                         isChecked    = False,
                         setAsDefault = False,
                         spanWidth    = True )
        
    def add_whats_this_text(self):
        """
        What's This text for some of the widgets in the Property Manager.
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
        
