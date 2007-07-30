# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_PushButton.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrPushButton out of PropMgrBaseClass.py into this
file and renamed it PM_PushButton.
"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QWidget

class PM_PushButton( QPushButton ):
    """
    The PM_PushButton widget provides a QPushButton with a 
    QLabel for a Property Manager group box.
    
    @cvar defaultText: The default text of the push button.
    @type defaultText: str
    
    @cvar setAsDefault: Determines whether to reset the value of the
                        push button to I{defaultText} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar hidden: Hide flag.
    @type hidden: bool
    
    @cvar labelWidget: The Qt label widget of this push button.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultText = ""
    setAsDefault = True
    hidden       = False
    labelWidget  = None
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  labelColumn  = 0,
                  text         = '', 
                  setAsDefault = True,
                  spanWidth    = False ):
        """
        Appends a QPushButton (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      checkbox. 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the list widget.
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param text: The button's text.
        @type  text: str
        
        @param setAsDefault: if True, will restore <text> as the button's text
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        
        @see: U{B{QPushButton}<http://doc.trolltech.com/4/qpushbutton.html>}
        """
        
        if 0: # Debugging code
            print "PM_PushButton.__init__():"
            print "  label        = ",label
            print "  labelColumn  = ",label
            print "  text         = ", text
            print "  setAsDefault = ", setAsDefault
            print "  spanWidth    = ", spanWidth
        
        QPushButton.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
        
        # Set text
        self.setText(text)
        
        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault
        
        parentWidget.addPmWidget(self)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)
            
    def collapse( self ):
        """
        Hides the push button and its label (if it has one) when its group box 
        is collapsed.
        """
        QWidget.hide(self) 
        if self.labelWidget :
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Displays the push button and its label (if it has one) when its group 
        box is expanded, unless the push button was "permanently" hidden via
        L{hide()}. In that case, the push button will remain hidden until 
        L{show()} is called.
        """
        if self.hidden: return
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
        
    def hide( self ):
        """
        Hides the push button and its label (if it has one). If hidden, the 
        push button will not be displayed when its group box is expanded.
        Call L{show()} to unhide the push button.
        
        @see: L{show}
        """
        self.hidden = True
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show( self ):
        """
        Unhide the push button and its label (if it has one). The push button
        will remain (temporarily) hidden if its group box is collapsed, 
        but will be displayed again when the group box is expanded.
        
        @see: L{hide}
        """
        self.hidden = False
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_PushButton ############################