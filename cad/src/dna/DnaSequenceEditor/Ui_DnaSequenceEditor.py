# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_DnaSequenceEditor.py

@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2007-11-28: Created. 

TODO:
- NFR: Add "Position" field.
- NFR: Add "Accept" and "Cancel" checkboxes to take/abort the new sequence.
- NFR: Support both "Insert" and "Overtype" modes in sequence field.
- Split out find and replace widgets to their own class (low priority)
- Create superclass that both the DNA and Protein sequence editors can use.

BUGS:

Bug 2956: Problems related to changing strand direction to "3' to 5'" direction:
  - Complement sequence field is offset from the sequence field when typing 
    overhang characters.
  - The sequence field overhang coloring is not correct.
  
"""

from PyQt4.Qt import QToolButton
from PyQt4.Qt import QPalette
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QLabel, QString
from PyQt4.Qt import QAction, QMenu
from PyQt4.Qt import Qt

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
from utilities.debug import print_compact_traceback

_superclass = PM_DockWidget
class Ui_DnaSequenceEditor(PM_DockWidget):
    """
    The Ui_DnaSequenceEditor class defines UI elements for the Sequence Editor
    object. The sequence editor is usually visible while in while editing
    a DnaStrand.
    
    It is a DockWidget that is docked at the bottom of the MainWindow.
    """
    _title         =  "Sequence Editor"
    _groupBoxCount = 0
    _lastGroupBox = None

    def __init__(self, win):
        """
        Constructor for the Ui_DnaSequenceEditor 
        @param win: The parentWidget (MainWindow) for the sequence editor 
        """
        
        self.win = win
        # Should parentWidget for a docwidget always be win? 
        #Not necessary but most likely it will be the case.        
        parentWidget = win 
        
        _superclass.__init__(self, parentWidget, title = self._title)
        
        #A flag used to restore the state of the Reports dock widget 
        #(which can be accessed through View  >  Reports) see self.show() and
        #self.closeEvent() for more details. 
        self._reportsDockWidget_closed_in_show_method = False
        self.setFixedHeight(90)
        return

    def show(self):
        """
        Shows the sequence editor. While doing this, it also closes the reports
        dock widget (if visible) the state of the reports dockwidget will be
        restored when the sequence editor is closed. 
        @see:self.closeEvent()
        """
        self._reportsDockWidget_closed_in_show_method = False
        #hide the history widget first
        #(It will be shown back during self.close)
        #The history widget is hidden or shown only when both 
        # 'View > Full Screen' and View > Semi Full Screen actions 
        # are *unchecked*
        #Thus show or close methods won't do anything to history widget
        # if either of the above mentioned actions is checked.
        if self.win.viewFullScreenAction.isChecked() or \
           self.win.viewSemiFullScreenAction.isChecked():
            pass
        else:
            if self.win.reportsDockWidget.isVisible():
                self.win.reportsDockWidget.close()
                self._reportsDockWidget_closed_in_show_method = True

        _superclass.show(self)
        return
        
    def closeEvent(self, event):
        """
        Overrides close event. Makes sure that the visible state of the reports
        widgetis restored when the sequence editor is closed. 
        @see: self.show()
        """
        _superclass.closeEvent(self, event)
       
        if self.win.viewFullScreenAction.isChecked() or \
           self.win.viewSemiFullScreenAction.isChecked():
            pass
        else:
            if self._reportsDockWidget_closed_in_show_method:
                self.win.viewReportsAction.setChecked(True) 
                self._reportsDockWidget_closed_in_show_method = False
        return

    def _loadWidgets(self):
        """
        Overrides PM.PM_DockWidget._loadWidgets. Loads the widget in this
        dockwidget.
        """
        self._loadMenuWidgets()
        self._loadTextEditWidget()
        return
    
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

        # Only supporting 5' to 3' direction until bug 2956 is fixed.
        # Mark 2008-12-19
        editDirectionChoices = ["5' to 3'"] # , "3' to 5'"]
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
        return

    def _loadTextEditWidget(self):
        """
        Load the SequenceTexteditWidgets.         
        """        
        self.sequenceTextEdit = \
            PM_TextEdit( self, 
                         label = " Sequence: ", 
                         spanWidth = False,
                         permit_enter_keystroke = False)        
        self.sequenceTextEdit.setCursorWidth(2)
        self.sequenceTextEdit.setWordWrapMode( QTextOption.WrapAnywhere )
        self.sequenceTextEdit.setFixedHeight(20)

        #The StrandSequence 'Mate' it is a read only etxtedit that shows
        #the complementary strand sequence.         
        self.sequenceTextEdit_mate = \
            PM_TextEdit(self, 
                        label = "", 
                        spanWidth = False,
                        permit_enter_keystroke = False
                        )        
        palette = getPalette(None, 
                             QPalette.Base, 
                             sequenceEditStrandMateBaseColor)
        self.sequenceTextEdit_mate.setPalette(palette)        
        self.sequenceTextEdit_mate.setFixedHeight(20)
        self.sequenceTextEdit_mate.setReadOnly(True)
        self.sequenceTextEdit_mate.setWordWrapMode(QTextOption.WrapAnywhere)

        #Important to make sure that the horizontal and vertical scrollbars 
        #for these text edits are never displayed. 
        for textEdit in (self.sequenceTextEdit, self.sequenceTextEdit_mate):
            textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return

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
        styleSheet = "QLineEdit {"\
                   "background-color: rgb(255, 102, 102)"\
                   "}"
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
        return

    def _addToolTipText(self):
        """
            What's Tool Tip text for widgets in this Property Manager.  
            """ 
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_DnaSequenceEditor
        ToolTip_DnaSequenceEditor(self)
        return

    def _addWhatsThisText(self):
        """
            What's This text for widgets in this Property Manager.  

            """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_DnaSequenceEditor
        whatsThis_DnaSequenceEditor(self)
        return
    