# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_FileChooser.py

@author: Mark
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.

History:

"""
import os

from PyQt4.Qt import QLabel
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QFileDialog

from utilities.prefs_constants import getDefaultWorkingDirectory

class PM_FileChooser( QWidget ):
    """
    The PM_FileChooser widget provides a file chooser widget for a
    Property Manager group box. The PM_FileChooser widget is a composite widget
    made from 3 other Qt widgets:
    - a QLabel 
    - a QLineEdit and
    - a QToolButton (with a "..." text label). 
    
    IMAGE(http://www.nanoengineer-1.net/mediawiki/images/e/e2/PM_FileChooser1.jpg)
    
    The user can type the path name of a file into the line edit widget or 
    select a file using Qt's file (chooser) dialog by clicking the "..."
    button. The path name of the selected file will be inserted into the
    line edit widget.
    
    The parent must make the following signal-slot connection to be
    notified when the user has selected a new file via the file chooser dialog:
    
    self.connect(pmFileChooser.lineEdit, SIGNAL("editingFinished()"), self.mySlotMethod)
    
    @cvar defaultText: The default text (path) of the line edit widget.
    @type defaultText: string
    
    @cvar setAsDefault: Determines whether to reset the value of the
                        lineedit to I{defaultText} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: boolean
    
    @cvar labelWidget: The Qt label widget of this PM widget.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    
    @cvar lineEdit: The Qt line edit widget for this PM widget.
    @type lineEdit: U{B{QLineEdit}<http://doc.trolltech.com/4/qlineedit.html>}
    
    @cvar browseButton: The Qt tool button widget for this PM widget.
    @type browseButton: U{B{QToolButton}<http://doc.trolltech.com/4/qtoolbutton.html>}
    """
    
    defaultText = ""
    setAsDefault = True
    hidden       = False
    lineEdit     = None
    browseButton = None
    
    def __init__(self, 
                 parentWidget, 
                 label        = '', 
                 labelColumn  = 0,
                 text         = '', 
                 setAsDefault = True,
                 spanWidth    = False,
                 caption      = "Choose file",
                 directory    = '',
                 filter       = "All Files (*.*)"
                 ):
        """
        Appends a file chooser widget to <parentWidget>, a property manager 
        group box.
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      file chooser lineedit (and "Browse" button). 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the lineedit (and button).
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param text: initial value of LineEdit widget.
        @type  text: string
        
        @param setAsDefault: if True, will restore <val> when the
                    "Restore Defaults" button is clicked.
        @type  setAsDefault: boolean
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: boolean
        
        @param caption: The caption used as the title of the file chooser 
                        dialog. "Choose file" is the default.
        @type  caption: string
        
        @param directory: The directory that the file chooser dialog should 
                          open in when the "..." button is clicked. 
                          If blank or if directory does not exist,
                          the current working directory is used.
        @type  directory: string
        
        @param filter: The file type filters to use for the file chooser dialog.
        @type  filter: string (a semicolon-separated list of file types)
        
        @see: U{B{QLineEdit}<http://doc.trolltech.com/4/qlineedit.html>}
        """
        
        QWidget.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.text         = text
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        self.caption      = caption
        self.directory    = directory
        self.filter       = filter
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
        else:
            self.labelWidget = None
        
        self.lineEdit = QLineEdit()
        self.browseButton = QToolButton()
        
        # Create vertical box layout.
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setMargin(0)
        self.hBoxLayout.setSpacing(2)
        self.hBoxLayout.insertWidget(-1, self.lineEdit)
        self.hBoxLayout.insertWidget(-1, self.browseButton)
        
        # Set (QLineEdit) text
        self.setText(text)
        
        # Set browse button text and make signal-slot connection.
        self.browseButton.setText("...")
        self.connect(self.browseButton, SIGNAL("clicked()"), self.openFileChooserDialog)
        
        # Set default value
        self.defaultText = text
        self.setAsDefault = setAsDefault
        
        parentWidget.addPmWidget(self)
        return
        
    def setText(self, text):
        """
        Set the line edit text.
        
        @param text: The text.
        @type  text: string
        """
        self.lineEdit.setText(text)
        self.text = text
        return
        
    def openFileChooserDialog(self):
        """
        Prompts the user to choose a file from disk and inserts the full path
        into the lineEdit widget.
        """
        
        _dir = getDefaultWorkingDirectory()
        
        if self.directory:
            if os.path.isdir(self.directory):
                _dir = self.directory

        fname = QFileDialog.getOpenFileName(self,
                                   self.caption,
                                   _dir,
                                   self.filter)
        
        if fname:
            self.setText(fname)
            self.lineEdit.emit(SIGNAL("editingFinished()"))
            
        return
    
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)
        return
    
    def hide(self):
        """
        Hides the lineedit and its label (if it has one).
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
        return
    
    def show(self):
        """
        Unhides the lineedit and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()
        return
            
# End of PM_FileChooser ############################