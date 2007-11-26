# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_SelectionListWidget.py

@author: Ninad 
@version: $Id$
@copyright: 2007 Nanorex, Inc.  All rights reserved.

TODO:
- Probably need to revise the tag instructions. At the moment it is confusing. 
  If a list widget item is selected from that widget, what should happen to the 
  corresponding item in the GLPane -- Should it get selected? or should it just 
  be  tagged? or do both? Popular cad programs would just tag entities in the 
  glpane. But, in our case (Insert DNA Duplex for Rattlesnake user story V6) 
  we need to also select strands in the glpane when those are selected from the
  list widget. So, in the current implementation, this is handled by a flag 
  'self._tagInstructions'. It is confusing because of the overuse of the 
  term 'select' . I have tried to resolve this by using terms 'pick' and unpick
  and explicitely mentioning 'glpane' . But overall, needs discussion and 
  cleanup. see also: PM_SelectionListWidget.tagItems [-- Ninad 2007-11-12]

- the attr 'iconPath' needs to be defined for various objects. Need a better 
   name?  (Example: see class Atom.iconPath that specifies the atom icon path 
   as a string)

- Review Changes to be done: (Bruce's email)
  As for self._tagInstruction in PM_SelectionListWidget.py 
  -- things will be cleaner if the widget code does not know a lot of details 
  about how to manipulate display and model info in a graphicsMode. Also, 
  there are update issues about storing atom posns in the graphicsMode.list of
  tag posns and then the user moves the atoms. So, what I suggest as a 
  refactoring at some point is for the widget to just be given a callback 
  function, so that whenever the set of selected list items is different, 
  it calls that function with the new list. Then the specific graphicsModes can
  clear whatever they stored last time, then scan that list and do whatever they
  want with it. No graphicsMode knowledge is needed in the widget, and whatever 
  atom posn updates are needed is handled entirely in the graphicsMode -- either
  it updates the list of tag posns whenever model_changed, or it just stores a 
  list of atoms in the first place, not a list of their positions, so it uses up
  to date posns each time it draws.
  **Comments/Questions: Implementation of this callback function 
  -- where should this be  defined? In the propMgr that initializes this list 
  widget? If so, it needs to be defined in each propMgr that will define this 
  listwidget (example: MotorPM and SDnaDuplxPM each will need to define the 
  callback methods. In the current implementation, they just set a 
  'tag instruction' for this widget.)What if propMgr.model_changed also calls a 
  model_changed method defined in this widget? 
"""
from PM_ListWidget import PM_ListWidget
from PyQt4.Qt import QListWidgetItem
from PyQt4.Qt  import SIGNAL
from PyQt4.Qt  import QPalette
from PM_Colors import getPalette
from constants import yellow
from icon_utilities import geticon

TAG_INSTRUCTIONS = ['TAG_ITEM_IN_GLPANE', 
                    'PICK_ITEM_IN_GLPANE',
                    'TAG_AND_PICK_ITEM_IN_GLPANE']

class PM_SelectionListWidget(PM_ListWidget):
    """
    Appends a QListWidget (Qt) widget to the I{parentWidget}, 
    a Property Manager group box. This is a selection list widget, that 
    means if you select the items in this list widget, the corresponding
    item in the GLPane will be tagged or picked or both depending on the 
    'tag instructions' 
    
    @param _tagInstruction: Sets the tag instruction. Based on its value, the 
                            items selected in the List widget will be either 
                            tagged or picked or both in the glpane. 
    @type  _tagInstruction: string
    
    @param _itemDictionary: This QListWidgetItem object defines a 'key' of a
                           dictionary and the 'value' of this key is the object
                           specified by the 'item' itself. Example: 
                           self._itemDictionary['C6'] = instance of class Atom.
    @type  _itemDictionary: dictionary                          
    """
       
    _tagInstruction = 'TAG_ITEM_IN_GLPANE'
    _itemDictionary = {}
    
    def __init__(self, 
                 parentWidget, 
                 win,
                 label = '',
                 color = None,
                 heightByRows = 6, 
                 spanWidth    = False):
        """
        Appends a QListWidget (Qt) widget to the I{parentWidget}, 
        a Property Manager group box. This is a selection list widget, that 
        means if you select the items in this list widget, the corresponding
        item in the GLPane will be tagged or picked or both depending on the 
        'tag instructions' 
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param win: Mainwindow object
        @type win: MWSemantics
        
        @param label: The label that appears to the left or right of the 
                      checkbox. 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the list widget.
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param color: color of the ListWidget
        @type : Array
        
        @param heightByRows: The height of the list widget.
        @type  heightByRows: int
        
        @param spanWidth: If True, the widget and its label will span the width
                          of the group box. Its label will appear directly above
                          the widget (unless the label is empty) and is left 
                          justified.
        @type  spanWidth: bool
        
        @see: U{B{QListWidget}<http://doc.trolltech.com/4/qlistwidget.html>}
        
        """ 
             
        self.win = win
        self.glpane = self.win.glpane
        
        PM_ListWidget.__init__(self, 
                               parentWidget, 
                               label = '',
                               heightByRows = heightByRows,
                               spanWidth = spanWidth)
        
        #Assigning color to the widget -- to be revised. (The color should 
        #change only when the focus is inside this widget -- the color change
        #will also suggest object(s) selected in glpane will be added as 
        #items in this widget (could be a  selective addition depending on 
        # the use) -- Niand 2007-11-12
        if color:
            self.setAutoFillBackground(True)
            self.setPalette(getPalette( None, 
                                       QPalette.Base,
                                       color))
    
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
        
        
    def insertItems(self, row, items, setAsDefault = True):
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
        
        """       
        #delete unused argument. Should this be provided as an argument in this
        #class method ?  
        del setAsDefault
                
        #Clear the previous contents of the self._itemDictionary 
        self._itemDictionary.clear()
        
        #Clear the contents of this list widget, using QListWidget.clear()
        #See U{<http://doc.trolltech.com/4.2/qlistwidget.html>} for details
        self.clear()
        
        for item in items:
            if hasattr(item.__class__, 'name'):
                itemName = item.name
            else:
                itemName = str(item)
             
            listWidgetItem = QListWidgetItem(itemName, self)
            if hasattr(item.__class__, 'iconPath'): 
                listWidgetItem.setIcon(geticon(item.iconPath))
                
            self._itemDictionary[listWidgetItem] = item  
    
    def clearTags(self):
        """
        Clear the previously drawn tags if any.
        """
        self.glpane.graphicsMode.drawTags(tagPositions = ())
    
    def setTagInstruction(self, tagInstruction = 'TAG_ITEM_IN_GLPANE'):
        """
        Sets the client specified tag instruction. 
        If a list widget item is selected from that widget, what should happen 
        to the corresponding item in the GLPane -- 
        Should it get selected? or should it just be  tagged? or do both? This
        is decided using the tag instruction.
        """
        assert tagInstruction in TAG_INSTRUCTIONS
            
        self._tagInstruction = tagInstruction
        
        
    def tagItems(self):
        """
        For the selected items in the list widget, tag and/or select the 
        corresponding item in the GLPane based on the self._tagInstruction
        @see: self.setTagInstruction 
        """    
        graphicsMode = self.glpane.graphicsMode
        
        #Clear the previous tags if any
        self.clearTags()        
        
        if self._tagInstruction != 'TAG_ITEM_IN_GLPANE':
            #Unpick all list widget items in the 3D workspace
            self._unpick_all_listWidgetItems_in_glpane()  
            self._pick_selected_listWidgetItems_in_glpane()
        
        if self._tagInstruction != 'PICK_ITEM_IN_GLPANE':
            tagPositions = []
            #Note: method selectedItems() is inherited from QListWidget 
            #see: U{<http://doc.trolltech.com/4.2/qlistwidget.html>} for details
            for key in self.selectedItems():   
                assert self._itemDictionary.has_key(key)
                item = self._itemDictionary[key]                            
                if hasattr(item.__class__, 'posn'):
                    tagPositions.append(item.posn())
                elif hasattr(item, 'center'):
                    chunkAtomList = item.atoms.values() 
                    #@TODO: The following is only a kludge, just to get things
                    # working while editing a the DnaDuplex. 
                    # Once Dna object model is implemented, this will be 
                    # completely revised. -- Ninad 2007-11-12
                    for atm in chunkAtomList:
                        if atm.element.name in ['PAM3-Axis-End', 'Singlet']:
                            tagPositions.append(atm.posn())
                            break                        
            if tagPositions: 
                graphicsMode.drawTags(tagPositions = tagPositions, 
                                      tagColor = yellow)            
            
        self.glpane.gl_update()
            
    def _unpick_all_listWidgetItems_in_glpane(self):
        """
        Deselect (unpick) all the items (object) in the GLPane that 
        correspond to the items in this list widget.
        """
        for item in self._itemDictionary.values():
            if item.picked:
                item.unpick()
                
    def _pick_selected_listWidgetItems_in_glpane(self):
        """
        If some items in the list widgets are selected (in the widget) 
        also select (pick) them from the glpane(3D workspace) 
        """        
        for key in self.selectedItems():
            assert self._itemDictionary.has_key(key)
            item = self._itemDictionary[key]
            if not item.picked:
                item.pick()         
    
    #Experimental code =========================================
    def insertItems_EXPERIMENTAL(self, row, items, setAsDefault = True):
        """
        instead of clearing the whole dictonary and the list widget items, 
        what if you selectively remove unused items. Would the following 
        be faster?
        """
        if self._itemDictionary.values():
            for item in items:
                if item in self._itemDictionary.values():
                    pass
                else:
                    listWidgetItem = QListWidgetItem(str(item), self)
                    self._itemDictionary[listWidgetItem] = item
            
        self._removeOutdatedItems_EXPERIMENTAL()
           
    #Experimental code =========================================
    def _removeOutdatedItems_EXPERIMENTAL(self, items):
        """
        instead of clearing the whole dictonary and the list widget items, 
        what if you selectively remove unused items. Would the following 
        be faster?
        """
        widgetItemListForRemoval = []
        if self._itemDictionary.keys():
            for key in self._itemDictionary.keys():
                if key.value() not in items:                    
                    rowNumber = self.row(key)
                    itemToRemove = self.takeItem(rowNumber)
                    widgetItemListForRemoval.append(itemToRemove)  
                    
            del widgetItemListForRemoval
                
