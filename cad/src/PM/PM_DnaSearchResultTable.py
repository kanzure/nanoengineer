# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
This class provides a table widget to display search results for a DnaStrand or
DnaSegment. It displays node name in one column and number of nucleotides 
in the other. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:


TODO:
Created between Nov 8-12, 2008 for Mark's consulting work. Needs cleanup

"""
from utilities.debug import print_compact_traceback
from PyQt4.Qt import Qt, SIGNAL
from PyQt4.Qt import QLabel
from PyQt4.Qt import QTableWidgetItem
from utilities.icon_utilities import geticon
from PM.PM_TableWidget import PM_TableWidget
from PM.PM_Colors import pmGrpBoxColor
from PM.PM_Colors import pmGrpBoxBorderColor
from widgets.widget_helpers import QColor_to_Hex

_superclass = PM_TableWidget
class PM_DnaSearchResultTable(PM_TableWidget):    
    def __init__(self, 
                 parentWidget, 
                 win,
                 items = [],
                 label          = '', 
                 labelColumn  = 1,
                 setAsDefault  = True,
                 spanWidth = True
                 ):
        """
        """
        self.win = win
        self.glpane = self.win.glpane
        self._suppress_itemChanged_signal = False
        self._suppress_itemSelectionChanged_signal = False
        self._itemDictionary = {} 
        
        _superclass.__init__(self, 
                             parentWidget, 
                             label = label, 
                             labelColumn = labelColumn,
                             setAsDefault = setAsDefault,
                             spanWidth = spanWidth )
        
        self.setColumnCount(2)
        self.setFixedHeight(200)
        self.setSortingEnabled(True)
                
        ##self.setAutoFillBackground(True)
        ##self.setStyleSheet(self._getStyleSheet())        
        self.insertItems(0, items)          
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect                

        change_connect(self,
                       SIGNAL('itemSelectionChanged()'), 
                       self.tagItems)
        
                
        
    def insertItems(self, row, items):
        """
        Insert the <items> specified items in this list widget. 
        The list widget shows item name string , as a QListwidgetItem. 

        This QListWidgetItem object defines a 'key' of a dictionary 
        (self._itemDictionary) and the 'value' of this key is the object 
        specified by the 'item' itself.         
        Example: self._itemDictionary['C6'] = instance of class Atom. 

        @param row: The row number for the item. 
        @type row: int

        @param items: A list of objects. These objects are treated as values in 
                      the self._itemDictionary
        @type items: list 

        @param setAsDefault: Not used here. See PM_ListWidget.insertItems where 
                             it is used.

        @see: self.renameItemValue() for a comment about 
              self._suppress_itemChanged_signal

        """       

       

        #self.__init__ for a comment about this flag
        self._suppress_itemChanged_signal = True

        #Clear the previous contents of the self._itemDictionary 
        self._itemDictionary.clear()

        #Clear the contents of this list widget, using QListWidget.clear()
        #See U{<http://doc.trolltech.com/4.2/qlistwidget.html>} for details
        self.clear()
        
        seq = ['Node name', 'Number of bases']
        self.setHorizontalHeaderLabels(seq)
        self.setRowCount(len(items))
        
        idx = 0
        self.setSortingEnabled(False)
        for item in items:
            if hasattr(item.__class__, 'name'):
                itemName = item.name
            else:
                itemName = str(item)
                            
            numberOfBasesString = ''
            
            if isinstance(item, self.win.assy.DnaStrand):
                numberOfBasesString = str(len(item.getAllAtoms()))
            
            elif isinstance(item, self.win.assy.DnaSegment):
                numberOfBasesString = str(item.getNumberOfBasePairs())
            
            tableWidgetItem = QTableWidgetItem(itemName)
            ###When we support editing list widget items , uncomment out the 
            ###following line . See also self.editItems -- Ninad 2008-01-16
            ##tableWidgetItem.setFlags( tableWidgetItem.flags()| Qt.ItemIsEditable)

            if hasattr(item.__class__, 'iconPath'):
                try:
                    tableWidgetItem.setIcon(geticon(item.iconPath))
                except:
                    print_compact_traceback()

            self._itemDictionary[tableWidgetItem] = item 
            
            self.setItem(idx, 0, tableWidgetItem)
            
            tableWidgetItem_column_2 = QTableWidgetItem(numberOfBasesString)
            tableWidgetItem_column_2.setFlags(Qt.ItemIsEnabled)
            
            self.setItem(idx, 1, tableWidgetItem_column_2)
            
            idx += 1

        #Reset the flag that temporarily suppresses itemChange signal.   
        self._suppress_itemChanged_signal = False
        self.setSortingEnabled(True)
        
    def tagItems(self):
        """
        For the selected items in the table widget,  select the 
        corresponding item in the GLPane.
        """   
        if self._suppress_itemSelectionChanged_signal:
            return

        #Unpick all list widget items in the 3D workspace
        #if no modifier key is pressed. Earlier implementation 
        #used to only unpick items that were also present in the list 
        #widgets.But if we have multiple list widgets, example like
        #in Build DNA  mode, it can lead to confusion like in Bug 2681           
        #NOTE ABOUT A NEW POSSIBLE BUG: 
        #self.glpan.modkeys not changed when focus is inside the 
        #Property manager? Example: User holds down Shift key and starts 
        #selecting things inside  -- Ninad 2008-03-18

        if self.glpane.modkeys is None:
            self.win.assy.unpickall_in_GLPane()

        #Deprecated call of _unpick_all_widgetItems_in_glpane 
        #(deprecated on 2008-03-18
        ##self._unpick_all_widgetItems_in_glpane()  

        #Now pick the items selected in this list widget 
        self._pick_selected_widgetItems_in_glpane()

        self.glpane.gl_update()
        
        
    def _pick_selected_widgetItems_in_glpane(self):
        """
        If some items in the list widgets are selected (in the widget) 
        also select (pick) them from the glpane(3D workspace) 
        """ 
        for key in self.selectedItems():    
            column = self.column(key)
            if column == 0:
                actual_key = key
            else:
                row = self.row(key)
                actual_key = self.item(row, 0)
            assert self._itemDictionary.has_key(actual_key)
            item = self._itemDictionary[actual_key]
            if not item.picked:
                item.pick() 

    def updateSelection(self, selectedItemList):
        """
        Update the selected items in this selection list widget. The items 
        given by the parameter selectedItemList will get selected. 

        This suppresses the 'itemSelectionChanged signal because the items 
        are already selected in the 3D workspace and we just want to select
        the corresponding items (QWidgetListItems) in this list widget.

        @param selectedItemList:  List of items provided by the client 
                                 that need to be selected in this list widget
        @type  selectedItemList: list
        @see: B{BuildDna_PropertyManager.model_changed}
        """
        #The following flag suppresses the itemSelectionChanged signal , thereby 
        #prevents self.tagItems from calling. This is done because the 
        #items selection was changed from the 3D workspace. After this, the 
        #selection state of the corresponding items in the list widget must be
        #updated. 
        self._suppress_itemSelectionChanged_signal = True
        
        for key, value in self._itemDictionary.iteritems(): 
            if value in selectedItemList:
                if not key.isSelected():
                    key.setSelected(True)     
            else:
                if key.isSelected():
                    key.setSelected(False) 

        self._suppress_itemSelectionChanged_signal = False
        
        
    def _zzgetStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
         - background color
        
        @return: The group box style sheet.
        @rtype:  str
        """
        
        styleSheet = \
                   "QTableWidget QTableButton::section{"\
                   "border: 2px outset #%s; "\
                   "background: #%s; "\
                   "}" % ( QColor_to_Hex(pmGrpBoxBorderColor), 
                           QColor_to_Hex(pmGrpBoxColor)
                           )
        return styleSheet    