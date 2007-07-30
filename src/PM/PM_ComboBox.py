# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ComboBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrComboBox out of PropMgrBaseClass.py into this file
and renamed it PM_ComboBox.
"""

from PyQt4.Qt import QComboBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

class PM_ComboBox( QComboBox ):
    """
    The PM_ComboBox widget provides a QComboBox with a 
    QLabel for a Property Manager group box.
    
    @cvar defaultChoices: The default choices of the combobox.
    @type defaultChoices: list
                          
    @cvar defaultIndex: The default index of the combobox.
    @type defaultIndex: int
    
    @cvar setAsDefault: Determines whether to reset the choices to 
                        I{defaultChoices} and currentIndex to I{defaultIndex}
                        when the user clicks the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar hidden: Hide flag.
    @type hidden: bool
    
    @cvar labelWidget: The Qt label widget of this combobox.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultIndex   = 0
    defaultChoices = []
    setAsDefault   = True
    hidden         = False
    labelWidget    = None    
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  labelColumn  = 0,
                  choices      = [],
                  index        = 0, 
                  setAsDefault = True,
                  spanWidth    = False ):
        """
        Appends a QComboBox widget (with a QLabel widget) to <parentWidget>, 
        a property manager group box.
        
        Arguments:
        
        @param parentWidget: the group box containing this PM widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left of (or above) this PM widget.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
                
        @param choices: list of combo box choices (strings).
        @type  choices: list
        
        @param index: initial index (choice) of combobox. (0=first item)
        @type  index: int (default 0)
        
        @param setAsDefault: if True, will restore <index> as the current index
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool (default True)
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default False)
        
        @see: U{B{QComboBox}<http://doc.trolltech.com/4/qcombobox.html>}
        """
        
        if 0: # Debugging code
            print "PM_ComboBox.__init__():"
            print "  label=",label
            print "  choices =", choices
            print "  index =", index
            print "  setAsDefault =", setAsDefault
            print "  spanWidth =", spanWidth
        
        QComboBox.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
                       
        # Load QComboBox widget choices and set initial choice (index).
        for choice in choices:
            self.addItem(choice)
        self.setCurrentIndex(index)
        
        # Set default index
        self.defaultIndex=index
        self.defaultChoices=choices
        self.setAsDefault = setAsDefault
        
        parentWidget.addPmWidget(self)
            
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.clear() # Generates signals!
            for choice in self.defaultChoices:
                self.addItem(choice)
            self.setCurrentIndex(self.defaultIndex)
            
    def collapse( self ):
        """
        Hides the combobox and its label (if it has one) when its group box 
        is collapsed.
        """
        QWidget.hide(self) 
        if self.labelWidget :
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Displays the combobox and its label (if it has one) when its group 
        box is expanded, unless the combobox was "permanently" hidden via
        L{hide()}. In that case, the combobox will remain hidden until 
        L{show()} is called.
        """
        if self.hidden: return
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
        
    def hide( self ):
        """
        Hides the combobox and its label (if it has one). If hidden, the 
        combobox will not be displayed when its group box is expanded.
        Call L{show()} to unhide the combobox.
        
        @see: L{show}
        """
        self.hidden = True
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show( self ):
        """
        Unhide the combobox and its label (if it has one). The combobox
        will remain (temporarily) hidden if its group box is collapsed, 
        but will be displayed again when the group box is expanded.
        
        @see: L{hide}
        """
        self.hidden = False
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_ComboBox ############################