# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_DnaSequenceEditor.py

@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2007-11-28: Created. 

TODO:
- Split out find and replace widgets to their own class (low priority)
"""

from PyQt4.Qt import QToolButton
from PyQt4.Qt import QPalette
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QLabel
from PyQt4.Qt import QAction, QMenu

from PM.PM_Colors    import getPalette
from PM.PM_Colors    import sequenceEditStrandMateBaseColor

from PM.PM_DockWidget import PM_DockWidget
from PM.PM_WidgetRow  import PM_WidgetRow
from PM.PM_ToolButton import PM_ToolButton
from PM.PM_ComboBox   import PM_ComboBox
from PM.PM_TextEdit   import PM_TextEdit
from PM.PM_LineEdit   import PM_LineEdit
from PM.PM_PushButton import PM_PushButton

from utilities.icon_utilities import geticon, getpixmap

class Ui_DnaSequenceEditor(PM_DockWidget):
    """
    The Ui_DnaSequenceEditor class defines UI elements for the Sequence Editor
    object. The sequence editor is usually visible while in DNA edit mode.
    It is a DockWidget that is doced at the bottom of the MainWindow
    """
    _title         =  "Sequence Editor"
    _groupBoxCount = 0
    _lastGroupBox = None
    
    def __init__(self, parentWidget):
        """
        Constructor for the Ui_DnaSequenceEditor 
        @param parentWidget: The parentWidget for the sequence editor 

        NOTE: the parentWidget is MainWindow object as of 2007-11-28
        """
        PM_DockWidget.__init__(self, parentWidget, title = self._title)
        
        self.setFixedHeight(90)        
        self._addWhatsThisText()
        
       
    
    def _loadWidgets(self):
        """
        Overrides PM.PM_DockWidget._loadWidgets. Loads the widget in this
        dockwidget.
        """
        self._loadMenuWidgets()
        self._loadTextEditWidget()
    
    
    def _loadMenuWidgets(self):
        """
        Load the various menu widgets (e.g. Open, save sequence options, 
        Find and replace widgets etc. 
        """
        #Note: Find and replace widgets might be moved to their own class.
              
        self.loadSequenceButton = PM_ToolButton(
            self,
            iconPath = "ui/actions/Properties Manager/Open.png")  
        
        self.saveSequenceButton = PM_ToolButton(
            self, 
            iconPath = "ui/actions/Properties Manager/Save_Strand_Sequence.png") 
                                        
        self.loadSequenceButton.setAutoRaise(True)
        self.saveSequenceButton.setAutoRaise(True)
                
        editDirectionChoices = ["5' to 3'", "3' to 5'"]
        self.baseDirectionChoiceComboBox = \
            PM_ComboBox( self,
                         choices = editDirectionChoices,
                         index     = 0, 
                         spanWidth = False )   
        
        #Find and replace widgets --
        self.findLineEdit = \
            PM_LineEdit( self, 
                         label        = "",
                         spanWidth    = False)
        self.findLineEdit.setMaximumWidth(60)
        
        
        self.replaceLineEdit = \
            PM_LineEdit( self, 
                         label        = "",
                         spanWidth    = False)
        self.replaceLineEdit.setMaximumWidth(60)
        
        self.findOptionsToolButton = PM_ToolButton(self)
        self.findOptionsToolButton.setMaximumWidth(12)
        self.findOptionsToolButton.setAutoRaise(True)
        
        self.findOptionsToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        
        self._setFindOptionsToolButtonMenu()
                
        self.findNextToolButton = PM_ToolButton(
            self,
            iconPath = "ui/actions/Properties Manager/Find_Next.png")
        self.findNextToolButton.setAutoRaise(True)
        
        self.findPreviousToolButton = PM_ToolButton(
            self,
            iconPath = "ui/actions/Properties Manager/Find_Previous.png")
        self.findPreviousToolButton.setAutoRaise(True)
        
        self.replacePushButton = PM_PushButton(self, text = "Replace")
        
        self.warningSign = QLabel(self)
        self.warningSign.setPixmap(
            getpixmap('ui/actions/Properties Manager/Warning.png'))
        self.warningSign.hide()
        
        self.phraseNotFoundLabel = QLabel(self)
        self.phraseNotFoundLabel.setText("Sequence Not Found")
        self.phraseNotFoundLabel.hide()
          
        # NOTE: Following needs cleanup in the PM_WidgetRow/ PM_WidgetGrid
        # but this explanation is sufficient  until thats done -- 
        
        # When the widget type starts with the word 'PM_' , the 
        # PM_WidgetRow treats it as a well defined widget and thus doesn't try
        # to create a QWidget object (or its subclasses)
        # This is the reason why qLabels such as self.warningSign and
        # self.phraseNotFoundLabel  are defined as PM_Labels and not 'QLabels'
        # If they were defined as 'QLabel'(s) then PM_WidgetRow would have
        # recreated the label. Since we want to show/hide the above mentioned 
        # labels (and if they were recreated as mentioned above), 
        # we would have needed to define  those something like this:
        # self.phraseNotFoundLabel = widgetRow._widgetList[-2] 
        #Cleanup in PM_widgetGrid could be to check if the widget starts with 
        #'Q'  instead of 'PM_' 
    
        
        #Widgets to include in the widget row. 
        widgetList = [('PM_ToolButton', self.loadSequenceButton, 0),
                      ('PM_ToolButton', self.saveSequenceButton, 1),
                      ('QLabel', "     Sequence direction:", 2),
                      ('PM_ComboBox',  self.baseDirectionChoiceComboBox , 3),
                      ('QLabel', "     Find:", 4),
                      ('PM_LineEdit', self.findLineEdit, 5),
                      ('PM_ToolButton', self.findOptionsToolButton, 6),
                      ('PM_ToolButton', self.findPreviousToolButton, 7),
                      ('PM_ToolButton', self.findNextToolButton, 8), 
                      ('QLabel', "     Replace:", 9),
                      ('PM_TextEdit', self.replaceLineEdit, 10), 
                      ('PM_PushButton', self.replacePushButton, 11),
                      ('PM_Label', self.warningSign, 12),
                      ('PM_Label', self.phraseNotFoundLabel, 13),
                      ('QSpacerItem', 5, 5, 14) ]
        
        widgetRow = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList,
                                 label = "",
                                 spanWidth = True )
    
    def _loadTextEditWidget(self):
        """
        Load the SequenceTexteditWidgets.         
        """        
        self.sequenceTextEdit = \
            PM_TextEdit( self, label = " Sequence: ", spanWidth = False )        
        self.sequenceTextEdit.setCursorWidth(2)
        self.sequenceTextEdit.setWordWrapMode( QTextOption.WrapAnywhere )
        self.sequenceTextEdit.setFixedHeight(20)
        
        #The StrandSequence 'Mate' it is a read only etxtedit that shows
        #the complementary strand sequence.         
        self.sequenceTextEdit_mate = \
            PM_TextEdit(self, label = "", spanWidth = False )        
        palette = getPalette(None, 
                             QPalette.Base, 
                             sequenceEditStrandMateBaseColor)
        self.sequenceTextEdit_mate.setPalette(palette)        
        self.sequenceTextEdit_mate.setFixedHeight(20)
        self.sequenceTextEdit_mate.setReadOnly(True)
        self.sequenceTextEdit_mate.setWordWrapMode(QTextOption.WrapAnywhere)
        
    
    def _getFindLineEditStyleSheet(self):
        """
        Return the style sheet for the findLineEdit. This sets the following 
        properties only:
         - background-color
         
        This style is set whenever the searchStrig can't be found (sets
        a light red color background to the lineedit when this happens)   
        
        @return: The line edit style sheet.
        @rtype:  str
        
        """
        styleSheet = \
                   "QLineEdit {\
                   background-color: rgb(255, 102, 102)\
                   }"
        #Not used:
        #  background-color: rgb(217, 255, 216)\       

        return styleSheet
    
    def _setFindOptionsToolButtonMenu(self):
        """
        Sets the menu for the findOptionstoolbutton that appears a small 
        menu button next to the findLineEdit.
        """
        self.findOptionsMenu = QMenu(self.findOptionsToolButton)
        
        self.caseSensitiveFindAction = QAction(self.findOptionsToolButton)
        self.caseSensitiveFindAction.setText('Match Case')
        self.caseSensitiveFindAction.setCheckable(True)
        self.caseSensitiveFindAction.setChecked(False)
        
        self.findOptionsMenu.addAction(self.caseSensitiveFindAction)
        self.findOptionsMenu.addSeparator()
        
        self.findOptionsToolButton.setMenu(self.findOptionsMenu)
        
    def _addToolTipText(self):
            """
            What's Tool Tip text for widgets in this Property Manager.  
            """ 
            from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_SequenceEditor
            ToolTip_SequenceEditor(self)
               
    def _addWhatsThisText(self):
            """
            What's This text for widgets in this Property Manager.  
    
            """
            from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_SequenceEditor
            whatsThis_SequenceEditor(self)