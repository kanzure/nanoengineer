# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_LineEdit.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrLineEdit out of PropMgrBaseClass.py into this 
file and renamed it PM_LineEdit.
"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QWidget
from PyQt4.Qt import Qt

class PM_LineEdit( QLineEdit ):
    """
    The PM_LineEdit widget provides a QLineEdit with a QLabel for a 
    Property Manager group box.
    
    @cvar defaultText: The default text of the lineedit.
    @type defaultText: str
    
    @cvar setAsDefault: Determines whether to reset the value of the
                        lineedit to I{defaultText} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar labelWidget: The Qt label widget of this lineedit.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultText = ""
    setAsDefault = True
    hidden       = False
    labelWidget  = None
    
    def __init__(self, 
                 parentWidget, 
                 label        = '', 
                 labelColumn  = 0,
                 text         = '', 
                 setAsDefault = True,
                 spanWidth    = False
                 ):
        """
        Appends a QLineEdit widget to <parentWidget>, a property manager group box.
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      checkbox. 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the checkbox.
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param text: initial value of LineEdit widget.
        @type  text: str
        
        @param setAsDefault: if True, will restore <val> when the
                    "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        
        @see: U{B{QLineEdit}<http://doc.trolltech.com/4/qlineedit.html>}
        """
        
        if 0: # Debugging code
            print "PM_LineEdit.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  text         = ", text
            print "  setAsDefault = ", setAsDefault
            print "  spanWidth    = ", spanWidth
                
        QLineEdit.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
                
        # Set QLineEdit text
        self.setText(text)
        
        # Set default value
        self.defaultText = text
        self.setAsDefault = setAsDefault
        
        #Focus Policy
        self.setFocusPolicy(Qt.ClickFocus)
        
            
        parentWidget.addPmWidget(self)
        
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)
        
    def hide(self):
        """
        Hides the lineedit and its label (if it has one).
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show(self):
        """
        Unhides the lineedit and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()
    
    def _getSequenceEditorStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        The background color for a groupbox is set using getPalette().
        
        @return: The group box style sheet.
        @rtype:  str
        
        """
        styleSheet = \
                   "QLineEdit {border-width: 2px;\
                   border-style: solid; \
                   border-color: darkgreen;\
                   background-color: rgb(255, 255, 255)\
                   }"
        #Not used:
        #  background-color: rgb(217, 255, 216)\ 
      

        return styleSheet
    
    def zfocusInEvent(self, event):
        """
        """
        ##self.setStyleSheet(self._getSequenceEditorStyleSheet()) 
        pass
                    
    def zfocusOutEvent(self, event):
        """
        """  
        self.setStyleSheet("")     
                
            
# End of PM_LineEdit ############################