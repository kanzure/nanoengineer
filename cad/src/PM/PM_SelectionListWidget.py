# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_SelectionListWidget.py

@author: Ninad 
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  All rights reserved.

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
  listwidget (example: MotorPM and DnaDuplexPM each will need to define the 
  callback methods. In the current implementation, they just set a 
  'tag instruction' for this widget.)What if propMgr.model_changed also calls a 
  model_changed method defined in this widget? 
"""
from PM.PM_ListWidget import PM_ListWidget
from PyQt4.Qt  import QListWidgetItem
from PyQt4.Qt  import SIGNAL
from PyQt4.Qt  import QPalette
from PyQt4.Qt  import QAbstractItemView
from PyQt4.Qt import Qt
from PM.PM_Colors import getPalette
from widgets.widget_helpers import RGBf_to_QColor

from utilities.constants import yellow, white
from utilities.icon_utilities import geticon
from utilities.debug import print_compact_traceback

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

        #Note: self._tagInstruction and  self._itemDictionary  are instance 
        #variables and not class constants as we 
        #have many PM_SelectionListWidget objects (e.g. in Build Dna mode, we 
        # have Srand and Segment list widgets. Defining self._itemDictionary
        #as a class constant will make class objects share it and create bugs.
        self._tagInstruction = 'TAG_ITEM_IN_GLPANE'
        self._itemDictionary = {}

        #The following flag supresses the itemSelectionChanged signal
        #see self.updateSelection for more comments. 
        self._supress_itemSelectionChanged_signal = False

        #The following flag supresses the itemChanged signal
        #ItemChanged signal is emitted too frequently. We use this to know that
        #the data of an item has changed...example : to know that the renaming
        #operation of the widget is completed. When a widgetItem is renamed, 
        #we want to rename the corresponding object in the glpane (which is 
        #stored as a value in self._itemDictionary) As of 2008-04-16 this signal
        #is the most convienent way to do it (in Qt4.2.3). If this flag 
        #is set to False, it simply returns from the method that gets called 
        #when itemItemChanged signal is sent. The flag is set to True
        #while updating items in self.isertItems. When itemDoubleClicked signal
        #is sent, the flag is explicitely set to False -- Ninad 2008-04-16
        #@see: self.renameItemValue(), 
        #@self.editItem() (This is a QListWidget method)
        self._supress_itemChanged_signal = False

        PM_ListWidget.__init__(self, 
                               parentWidget, 
                               label = '',
                               heightByRows = heightByRows,
                               spanWidth = spanWidth)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

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


    def deleteSelection(self):
        """
        Remove the selected items from the list widget (and 
        self._itemDictionary)
        """
        for key in self.selectedItems():   
            assert self._itemDictionary.has_key(key)
            del self._itemDictionary[key]

    def getItemDictonary(self):
        """
        Returns the dictonary of self's items. 
        @see: MultipleSegments_PropertyManager.listWidget_keyPressEvent_delegate
        for details.
        """
        return self._itemDictionary


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
        change_connect(self, 
                       SIGNAL('itemDoubleClicked ( QListWidgetItem *)'),
                       self.editItem)
        change_connect(self, 
                       SIGNAL('itemChanged ( QListWidgetItem *)'),
                       self.renameItemValue)

        #Not USED -- editing widgets items is not supported
        #change_connect(self, 
                        #SIGNAL('itemDoubleClicked(QListWidgetItem *)'), 
                        #self.editItem)   


    def editItem(self, item):
        """
        Edit the widget item.
        @see: self.insertItems for a comment 
        @see: self.renameItemValue()
        @self.editItem() (This is a QListWidget method
        """
        #explicitely set the flag to False for safety. 
        self._supress_itemChanged_signal = False
        PM_ListWidget.editItem(self, item)


    def renameItemValue(self, item):
        """
        slot method that gets called when itemChanged signal is emitted. 

        Example: 1. User double clicks an item in the strand list widget of the 
        BuildDna mode 2. Edits the name. 3.Hits Enter key or clicks outside the 
        selection to end rename operation. 
        During step1, itemDoubleClicked signal is emitted which calls self.editItem
        and at the end of step3, it emits itemChanged signal which calls this 
        method

        @self.editItem() (This is a QListWidget method)        

        """

        #See a detailed note in self.__init__  where the following flag is 
        #declared. The flag is set to True when 
        if self._supress_itemChanged_signal:
            return


        if self._itemDictionary.has_key(item):
            val = self._itemDictionary[item]

            #Check if the 'val' (obj which this widgetitem represents) has an 
            #attr name. 
            if not hasattr(val, 'name'):
                if not item.text():
                    #don't permit empty names -- doesn't make sense. 
                    item.setText('name')
                return

            #Do the actual renaming of the 'val' 
            if item.text():
                val.name = item.text()
                self.win.win_update()
            else:
                #Don't allow assignment of a blank name
                item.setText(val.name)

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

        @see: self.renameItemValue() for a comment about 
              self._supress_itemChanged_signal

        """       

        #delete unused argument. Should this be provided as an argument in this
        #class method ?  
        del setAsDefault

        #self.__init__ for a comment about this flag
        self._supress_itemChanged_signal = True

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

            #When we support editing list widget items , uncomment out the 
            #following line . See also self.editItems -- Ninad 2008-01-16
            listWidgetItem.setFlags( listWidgetItem.flags()| Qt.ItemIsEditable)

            if hasattr(item.__class__, 'iconPath'):
                try:
                    listWidgetItem.setIcon(geticon(item.iconPath))
                except:
                    #bruce 080829 added this while debugging Zoom in or after Insert Dna in USE_COMMAND_STACK
                    print_compact_traceback()

            self._itemDictionary[listWidgetItem] = item  

        #Reset the flag that temporarily supresses itemChange signal.   
        self._supress_itemChanged_signal = False

    def setColor(self, color):    
        """
        Set the color of the widget to the one given by param color
        @param color: new palette color of self.
        """
        self.setAutoFillBackground(True)
        color = RGBf_to_QColor(color)
        self.setPalette(getPalette( None, 
                                    QPalette.Base,
                                    color))


    def resetColor(self):
        """
        Reset the paletter color of the widget (and set it to white)
        """
        self.setAutoFillBackground(True)
        color = RGBf_to_QColor(white)
        self.setPalette(getPalette( None, 
                                    QPalette.Base,
                                    color))

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
        if self._supress_itemSelectionChanged_signal:
            return

        graphicsMode = self.glpane.graphicsMode

        #Clear the previous tags if any
        self.clearTags()        

        if self._tagInstruction != 'TAG_ITEM_IN_GLPANE':
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

            #Deprecated call of _unpick_all_listWidgetItems_in_glpane 
            #(deprecated on 2008-03-18
            ##self._unpick_all_listWidgetItems_in_glpane()  

            #Now pick the items selected in this list widget 
            self._pick_selected_listWidgetItems_in_glpane()

        #Note: 2008-03-18 Following tag instruction is deprecated sometime ago 
        #LKeeping this code intact for now. 
        if self._tagInstruction != 'PICK_ITEM_IN_GLPANE':
            tagPositions = []
            #Note: method selectedItems() is inherited from QListWidget 
            #see: U{<http://doc.trolltech.com/4.2/qlistwidget.html>} for details
            for key in self.selectedItems():   
                assert self._itemDictionary.has_key(key)
                item = self._itemDictionary[key]     
                if isinstance(item, self.win.assy.DnaSegment):
                    end1, end2 = item.getAxisEndPoints()
                    for endPoint in (end1, end2):
                        if endPoint is not None:
                            tagPositions.append(endPoint)
                elif hasattr(item.__class__, 'posn'):
                    tagPositions.append(item.posn())

            if tagPositions: 
                graphicsMode.drawTags(tagPositions = tagPositions, 
                                      tagColor = yellow)            

        self.glpane.gl_update()

    def _unpick_all_listWidgetItems_in_glpane(self):
        """
        Deselect (unpick) all the items (object) in the GLPane that 
        correspond to the items in this list widget.

        Deprecated as of 2008-03-18. See a comment in self.tagItems
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
        #The following flag supresses the itemSelectionChanged signal , thereby 
        #prevents self.tagItems from calling. This is done because the 
        #items selection was changed from the 3D workspace. After this, the 
        #selection state of the corresponding items in the list widget must be
        #updated. 
        self._supress_itemSelectionChanged_signal = True

        for key, value in self._itemDictionary.iteritems():

            if value in selectedItemList:
                if not key.isSelected():
                    key.setSelected(True)     
            else:
                if key.isSelected():
                    key.setSelected(False) 

        self._supress_itemSelectionChanged_signal = False


    def clear(self):
        """
        Clear everything inside this list widget including the 
        contents of self._itemDictionary and tags if any. 

        Overrides QListWidget.clear()
        """
        self.clearTags()

        #Clear the previous contents of the self._itemDictionary 
        self._itemDictionary.clear()

        #Clear the contents of this list widget, using QListWidget.clear()
        #See U{<http://doc.trolltech.com/4.2/qlistwidget.html>} for details
        PM_ListWidget.clear(self)


    def getPickedItem(self):
        """
        Return the 'real' item picked (selected) inside this selection list 
        widget. The 'real' item is the object whose name appears inside the 
        selection list widget. (it does not return the 'QWidgetItem' but the 
        key.value() that actually stores the NE1 object)

        NOTE: If there are more than one items selected, it returns only the 
              FIRST ITEM in the list. This class is designed to select only 
              a single item at a time , but in case this implementation changes,
              this method should be revised. 
        @see: BuildDna_PropertyManager.assignStrandSequence
        """
        #Using self.selectedItems() doesn't work for some reason! (when you 
        # select item , go to the sequence editor and hit assign button, 
        # it spits an error 

        pickedItem = None
        selectedItemList = self.selectedItems()
        key = selectedItemList[0]
        pickedItem = self._itemDictionary[key]

        return pickedItem


        #for item in self._itemDictionary.values():
            #if item.picked:
                #return item 

        #return None

