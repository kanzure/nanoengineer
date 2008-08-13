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
    The PM_ComboBox widget provides a combobox with a text label for a 
    Property Manager group box. The text label can be positioned on either 
    the left or right side of the combobox.
    
    A combobox is a combined button and popup list that provides a means of 
    presenting a list of options to the user in a way that takes up the 
    minimum amount of screen space.
    
    Also, a combobox is a selection widget that displays the current item, 
    and can pop up a list of selectable items. A combobox may be editable, 
    allowing the user to modify each item in the list.
    
    Comboboxes can contain pixmaps as well as strings; the insertItem() 
    and changeItem() functions are suitably overloaded. 
    For editable comboboxes, the function clearEdit() is provided, to 
    clear the displayed string without changing the combobox's contents.
    
    There are two signals emitted if the current item of a combobox changes, 
    currentIndexChanged() and activated(). currentIndexChanged() is always 
    emitted regardless if the change was done programmatically or by user 
    interaction, while activated() is only emitted when the change is caused 
    by user interaction. The highlighted() signal is emitted when the user 
    highlights an item in the combobox popup list. All three signals exist 
    in two versions, one with a 
    U{B{QString}<http://doc.trolltech.com/4/qstring.html>} 
    argument and one with an int argument. 
    If the user selectes or highlights a pixmap, only the int signals are 
    emitted. Whenever the text of an editable combobox is changed the 
    editTextChanged() signal is emitted.
    
    When the user enters a new string in an editable combobox, the widget may 
    or may not insert it, and it can insert it in several locations. 
    The default policy is is AtBottom but you can change this using 
    setInsertPolicy().
    
    It is possible to constrain the input to an editable combobox using 
    U{B{QValidator}<http://doc.trolltech.com/4/qvalidator.html>}
    ; see setValidator(). By default, any input is accepted.
    
    A combobox can be populated using the insert functions, insertStringList()
    and insertItem() for example. Items can be changed with changeItem(). 
    An item can be removed with removeItem() and all items can be removed 
    with clear(). The text of the current item is returned by currentText(), 
    and the text of a numbered item is returned with text(). The current item 
    can be set with setCurrentIndex(). The number of items in the combobox is 
    returned by count(); the maximum number of items can be set with 
    setMaxCount(). You can allow editing using setEditable(). For editable 
    comboboxes you can set auto-completion using setCompleter() and whether 
    or not the user can add duplicates is set with setDuplicatesEnabled().
    
    PM_ComboBox uses the model/view framework for its popup list and to store
    its items. By default a QStandardItemModel stores the items and a 
    QListView subclass displays the popuplist. You can access the model and 
    view directly (with model() and view()), but PM_ComboBox also provides 
    functions to set and get item data (e.g., setItemData() and itemText()). 
    You can also set a new model and view (with setModel() and setView()). 
    For the text and icon in the combobox label, the data in the model that 
    has the Qt.DisplayRole and Qt.DecorationRole is used.

    @cvar defaultChoices: The default choices of the combobox.
    @type defaultChoices: list
                          
    @cvar defaultIndex: The default index of the combobox.
    @type defaultIndex: int
    
    @cvar setAsDefault: Determines whether to reset the choices to 
                        I{defaultChoices} and currentIndex to I{defaultIndex}
                        when the user clicks the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar labelWidget: The Qt label widget of this combobox.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    
    @see: U{B{QComboBox}<http://doc.trolltech.com/4/qcombobox.html>}
    """
    
    defaultIndex   = 0
    defaultChoices = []
    setAsDefault   = True
    labelWidget    = None    
    
    def __init__(self, 
                 parentWidget, 
                 label        = '', 
                 labelColumn  = 0,
                 choices      = [],
                 index        = 0, 
                 setAsDefault = True,
                 spanWidth    = False
                 ):
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
        
        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default False)
        
        @see: U{B{QComboBox}<http://doc.trolltech.com/4/qcombobox.html>}
        """
        
        if 0: # Debugging code
            print "PM_ComboBox.__init__():"
            print "  label        =", label
            print "  choices      =", choices
            print "  index        =", index
            print "  setAsDefault =", setAsDefault
            print "  spanWidth    =", spanWidth
        
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
        self.defaultIndex   = index
        self.defaultChoices = choices
        self.setAsDefault   = setAsDefault
        
        parentWidget.addPmWidget(self)
            
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.clear() # Generates signals!
            for choice in self.defaultChoices:
                self.addItem(choice)
            self.setCurrentIndex(self.defaultIndex)
        
    def hide(self):
        """
        Hides the combobox and its label (if it has one).
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show(self):
        """
        Unhides the combobox and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()
            
            
    def setCurrentIndex(self, val, blockSignals = False):
        """
        Overrides the superclass method. 
        
        @param blockSignals: Many times, the caller just wants to setCurrentIndex 
                             and don't want to send valueChanged signal. 
                             If this flag is set to True, the currentIdexChanged
                             signal won't be emitted.  The default value is 
                             False.
        @type  blockSignals: bool 
        
        @see: DnaDisplayStyle_PropertyManager.updateDnaDisplayStyleWidgets()
        """
        #If blockSignals flag is True, the valueChanged signal won't be emitted 
        #This is done by self.blockSignals method below.  -- Ninad 2008-08-13
        self.blockSignals(blockSignals)
        
        QComboBox.setCurrentIndex(self, val)
        
        #Make sure to always 'unblock' signals that might have been temporarily
        #blocked before calling superclass.setValue. 
        self.blockSignals(False)
        

# End of PM_ComboBox ############################