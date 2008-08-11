# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@version: $Id$
@copyright:2008 Nanorex, Inc.  See LICENSE file for details.

History:
2008-05-09 Created

TODO: as of 2008-01-18
- See MultipleDnaSegmentResize_EditCommand for details. 
- need to implement model_changed method 
"""
from PyQt4.Qt import Qt, SIGNAL
from PM.PM_GroupBox      import PM_GroupBox
from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_ToolButton    import PM_ToolButton
from PM.PM_WidgetRow     import PM_WidgetRow
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from utilities.constants import lightred_1, lightgreen_2
from geometry.VQT import V
from utilities.debug import print_compact_stack
from utilities       import debug_flags
from utilities.Comparison import same_vals

from utilities.Log import redmsg

_superclass = EditCommand_PM
class MultipleDnaSegmentResize_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    
    title         =  "Resize Dna Segments"
    pmName        =  title
    iconPath      =  "ui/actions/Properties Manager/Resize_Multiple_Segments.png"
    
    isAlreadyConnected = False
    isAlreadyDisconnected = False
    
    def __init__( self, win, command ):
        """
        Constructor for the Build DNA property manager.
        """
        
        #For model changed signal    
        #@see: self.model_changed() and self._current_model_changed_params 
        #for example use
        self._previous_model_changed_params = None
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        
        self.endPoint1 = V(0, 0, 0)
        self.endPoint2 = V(0, 0, 0)
                
        self._numberOfBases = 0 
        self._conformation = 'B-DNA'
        self.duplexRise = 3.18
        self.basesPerTurn = 10
        self.dnaModel = 'PAM3'
        
        _superclass.__init__( self, 
                                    win,
                                    command)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        msg = "Use resize handles to resize the segments."
        self.updateMessage(msg)   
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a 
        #temporary mode  entering such a temporary mode keeps the signals of 
        #PM from the previous mode connected (
        #but while exiting that temporary mode and reentering the 
        #previous mode, it atucally reconnects the signal! This gives rise to 
        #lots  of bugs. This needs more general fix in Temporary mode API. 
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py
                
        if isConnect and self.isAlreadyConnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to connect widgets"\
                                    "in this PM that are already connected." )
            return 
        
        if not isConnect and self.isAlreadyDisconnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to disconnect widgets"\
                                    "in this PM that are already disconnected.")
            return
        
        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect
        
        if isConnect:
            change_connect = self.win.connect     
        else:
            change_connect = self.win.disconnect 
          
        self.segmentListWidget.connect_or_disconnect_signals(isConnect) 
        change_connect(self.addSegmentsToolButton, 
                        SIGNAL("toggled(bool)"), 
                        self.activateAddSegmentsTool)
        change_connect(self.removeSegmentsToolButton, 
                        SIGNAL("toggled(bool)"), 
                        self.activateRemoveSegmentsTool)
        
    def model_changed(self): 
        """
        @see: DnaSegment_EditCommand.model_changed()
        @see: DnaSegment_EditCommand.hasResizableStructure()
        @see: self._current_model_changed_params()
        """
        
        currentParams = self._current_model_changed_params()
        
        #Optimization. Return from the model_changed method if the 
        #params are the same. 
        if same_vals(currentParams, self._previous_model_changed_params):
            return 
        
        number_of_segments, isStructResizable, why_not = currentParams
        
        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams
        
        if not isStructResizable:
            if not number_of_segments == 0:
                #disable all widgets                
                self._pmGroupBox1.setEnabled(False)
            msg = redmsg("DnaSegment is not resizable. Reason: %s"%(why_not))
            self.updateMessage(msg)
        else:
            if not self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(True)
            msg = "Use resize handles to resize the segments"
            self.updateMessage(msg)
                    
        self.updateListWidgets() 
        ##self.command.updateHandlePositions()
            
                
    def _current_model_changed_params(self):
        """
        Returns a tuple containing the parameters that will be compared
        against the previously stored parameters. This provides a quick test
        to determine whether to do more things in self.model_changed()
        @see: self.model_changed() which calls this
        @see: self._previous_model_changed_params attr. 
        """
        params = None
        
        if self.command:
            #update the list first. 
            self.command.updateResizeSegmentList()
            number_of_segments = len(self.command.getResizeSegmentList())     
            isStructResizable, why_not = self.command.hasResizableStructure()
            params = (number_of_segments, isStructResizable, why_not)
        
        return params 
    
    def isAddSegmentsToolActive(self): 
        """
        Returns True if the add segments tool (which adds the segments to the 
        list of segments to be resized) is active
        """
            
        if self.addSegmentsToolButton.isChecked():
            #For safety
            if not self.removeSegmentsToolButton.isChecked():         
                return True   
            
        return False
            
    
    def isRemoveSegmentsToolActive(self):
        """
        Returns True if the remove segments tool (which removes the segments 
        from the list of segments to be resized) is active
        """
        if self.removeSegmentsToolButton.isChecked():
            if not self.addSegmentsToolButton.isChecked():
                #For safety
                return True               
        return False
    
    def activateAddSegmentsTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments 
        to be resized) so as to indicate that the add dna segments tool is 
        active 
        @param enable: If True, changes the appearance of list widget to 
                       indicate that the add segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(True)
            if self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(False)
            self.segmentListWidget.setColor(lightgreen_2)            
        else:
            if self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(True)
            self.segmentListWidget.resetColor()
                
    def activateRemoveSegmentsTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments 
        to be resized) so as to indicate that the REMOVE dna segments tool is 
        active 
        @param enable: If True, changes the appearance of list widget to 
                       indicate that the REMOVE segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(True)
            if self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(False)
            
            self.segmentListWidget.setColor(lightred_1)            
        else:
            if self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(True)
            self.segmentListWidget.resetColor()
            
    def removeListWidgetItems(self):
        """
        Removes selected atoms from the resize dna segment list widget 
        Example: User selects a bunch of items in the list widget and hits 
        delete key  to remove the selected items from the list
        IMPORTANT NOTE: This method does NOT delete the correspoinging model 
        item in the GLPane (i.e. corresponding dnasegment). It just 'removes'
        the item from the list widget (indicating its no longer being resized) 
        This is intentional. 
        """
        self.segmentListWidget.deleteSelection()
        itemDict = self.segmentListWidget.getItemDictonary()           
        self.command.setResizeStructList(itemDict.values())
        self.updateListWidgets()            
        self.win.win_update()
        

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Segments for Resizing" )
        self._loadGroupBox1( self._pmGroupBox1 )
        

    def _loadGroupBox1(self, pmGroupBox):
        """
        load widgets in groupbox1
        """
        self.segmentListWidget = PM_SelectionListWidget(
            pmGroupBox,
            self.win,
            label = "",
            heightByRows = 12)
      
        self.segmentListWidget.setFocusPolicy(Qt.StrongFocus)
        self.segmentListWidget.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)       
        
        self.addSegmentsToolButton = PM_ToolButton(
                        pmGroupBox, 
                        text = "Add segments to the list",
                        iconPath  = "ui/actions/Properties Manager"\
                        "/AddSegment_To_ResizeSegmentList.png",
                        spanWidth = True  )
        self.addSegmentsToolButton.setCheckable(True)
        self.addSegmentsToolButton.setAutoRaise(True)
        
        self.removeSegmentsToolButton = PM_ToolButton(
                        pmGroupBox, 
                        text = "Remove segments from the list",
                        iconPath  = "ui/actions/Properties Manager"\
                        "/RemoveSegment_From_ResizeSegmentList.png",
                        spanWidth = True  )
        self.removeSegmentsToolButton.setCheckable(True)
        self.removeSegmentsToolButton.setAutoRaise(True)
        
        #Widgets to include in the widget row. 
        widgetList = [
            ('QLabel', "  Add/Remove Segments:", 0),
            ('QSpacerItem', 5, 5, 1),
            ('PM_ToolButton', self.addSegmentsToolButton, 2),
             ('QSpacerItem', 5, 5, 3),
            ('PM_ToolButton', self.removeSegmentsToolButton, 4),                      
            ('QSpacerItem', 5, 5, 5) ]
        
        widgetRow = PM_WidgetRow(pmGroupBox,
                                 title     = '',
                                 widgetList = widgetList,
                                 label = "",
                                 spanWidth = True )
        
        
    def _addWhatsThisText(self):
        """
        Add what's this text. 
        Abstract method.
        """
        pass
    
    def show(self):
        """
        Overrides the superclass method
        @see: self._deactivateAddRemoveSegmentsTool
        """
        _superclass.show(self)
        ##self.updateListWidgets()       
        self._deactivateAddRemoveSegmentsTool()
        
    def _deactivateAddRemoveSegmentsTool(self):
        """
        Deactivate tools that allow adding or removing the segments to the 
        segment list in the Property manager. This can be simply done by 
        resetting the state of toolbuttons to False. 
        Example: toolbuttons that add or remove 
        segments to the segment list in the Property manager. When self.show
        is called these need to be unchecked. 
        @see: self.isAddSegmentsToolActive()
        @see:self.isRemoveSegmentsToolActive()
        @see: self.show()
        """
        self.addSegmentsToolButton.setChecked(False)
        self.removeSegmentsToolButton.setChecked(False)
        
        
    def listWidgetHasFocus(self):
        """
        Checkes if the list widget that lists dnasegments to be resized has the 
        Qt focus. This is used to just remove items from the list widget 
        (without actually 'deleting' the corresponding Dnasegment in the GLPane)
        @see: MultipleDnaSegment_GraphicsMode.keyPressEvent() where it is called
        """
        if self.segmentListWidget.hasFocus():
            return True        
        return False
    
       
    def setParameters(self, params):
        pass
    
    def getParameters(self):
        return ()
    
    def updateListWidgets(self):
        self.updateSegmentListWidget()
    
    def updateSegmentListWidget(self):
        """
        Update the list of segments shown in the segments list widget
        @see: self.updateListWidgets, self.updateStrandListWidget
        """
        segmentList = []
        
        segmentList = self.command.getResizeSegmentList()                        
               
        self.segmentListWidget.insertItems(
            row = 0,
            items = segmentList)