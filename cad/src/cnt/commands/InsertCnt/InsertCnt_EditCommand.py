# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
InsertCnt_EditCommand.py
InsertCnt_EditCommand that provides an editCommand object for 
generating a carbon nanotube (CNT).  This command should be invoked only from 
CntProperties_EditCommand

@author: Mark Sims, Ninad Sathaye
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
- Mark 2008-03-8: This file created from a copy of DnaDuplex_EditCommand.py
and edited.

TODO: (list copied and kept from DnaDuplex_EditCommand.py --Mark)
- Need to cleanup docstrings. 
- Methods such as createStructure need some cleanup in 
  this class and in the EditCommand superclass
- Method editStructure is not implemented. It will be implemented after 
  the DNA object model gets implemented. 
- Editing existing structures is not done correctly (broken) after converting 
  this editController into a command. This is a temporary effect. Once the dna 
  data model is fully implemented, the dna group will supply the endPoints 
  necessary to correctly edit the dna structure ad this problem will
  be fixed -- Ninad 2007-12-20
"""
from command_support.EditCommand import EditCommand

from cnt.model.NanotubeSegment import NanotubeSegment
from cnt.model.NanotubeGroup import NanotubeGroup
from utilities.debug import print_compact_stack

from utilities.Log  import redmsg, greenmsg
from geometry.VQT import V, Veq, vlen
from cnt.commands.InsertCnt.Nanotube import Cnt

from command_support.GeneratorBaseClass import PluginBug, UserError
from cnt.commands.InsertCnt.InsertCnt_PropertyManager import InsertCnt_PropertyManager

from utilities.constants import gensym

from cnt.model.Nanotube_Constants import getNumberOfCellsFromCntLength
from cnt.model.Nanotube_Constants import getCntRise, getCntLength

from cnt.temporary_commands.NanotubeLineMode import CntLine_GM


class InsertCnt_EditCommand(EditCommand):
    """
    InsertCnt_EditCommand that provides an editCommand object for 
    generating carbon or boron nitride nanotube. 

    This command should be invoked only from InsertCnt_EditCommand 

    User can create as many nanotubes as he/she needs just by specifying 
    two end points for each nanotube. This uses NanotubeLineMode_GM  class as its
    GraphicsMode 
    """
    cmd              =  greenmsg("Insert CNT: ")
    sponsor_keyword  =  'CNT'
    prefix           =  'Cnt'   # used for gensym
    cmdname          = "Insert CNT"
    commandName      = 'INSERT_CNT'
    featurename      = 'Insert CNT'

    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    #Graphics Mode set to CntLine graphics mode
    GraphicsMode_class = CntLine_GM

    #required by CntLine_GM
    mouseClickPoints = []
    #This is the callback method that the previous command 
    #(which is InsertCnt_Editcommand as of 2008-01-11) provides. When user exits
    #this command and returns back to the previous one (InsertCnt_EditCommand),
    #it calls this method and provides a list of segments created while this 
    #command was  running. (the segments are stored within a temporary cnt group
    #see self._fallbackNanotubeGroup
    callback_addSegments  = None

    #This is set to InsertCnt_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for InsertCnt_EditCommand
        """

        EditCommand.__init__(self, commandSequencer)        

        #_fallbackNanotubeGroup stores the NanotubeSegments created while in 
        #this command. This temporary cntGroup is created IF AND ONLY IF 
        #InsertCnt_EditCommand is unable to access the cntGroup object of the 
        #parent InsertCnt_EditCommand. (so if this group gets created, it should
        #be considered as a bug. While exiting the command the list of segments 
        #of this group is given to the InsertCnt_EditCommand where they get 
        #their new parent. @see self.restore_gui
        self._fallbackNanotubeGroup = None

        #_parentNanotubeGroup is the cntgroup of InsertCnt_EditCommand 
        self._parentNanotubeGroup = None

        #Maintain a list of segments created while this command was running. 
        #Note that the segments , when created will be added directly to the 
        # self._parentNanotubeGroup (or self._fallbackNanotubeGroup if there is a bug) 
        # But self._parentNanotubeGroup (which must be = the cntGroup of 
        # InsertCnt_EditCommand.) may already contain NanotubeSegments (added earlier)
        # so, we can not use group.steal_members() in case user cancels the 
        #structure creation (segment addition). 
        self._segmentList = []

        self.struct = struct

    def _createFallbackNanotubeGroup(self):
        """
        Creates a temporary NanotubeGroup object in which all the NanotubeSegments 
        created while in this command will be added as members. 
        While exiting this command, these segments will be added first taken 
        away from the temporary group and then added to the NanotubeGroup of
        InsertCnt_EditCommand 
        @see: self.restore_gui
        @see: InsertCnt_EditCommand.callback_addSegments()
        """
        if self._fallbackNanotubeGroup is None:
            self.win.assy.part.ensure_toplevel_group()
            self._fallbackNanotubeGroup = \
                NanotubeGroup("Fallback Cnt", 
                              self.win.assy,
                              self.win.assy.part.topnode )


    def init_gui(self):
        """
        Do changes to the GUI while entering this command. This includes opening 
        the property manager, updating the command toolbar , connecting widget 
        slots (if any) etc. Note: The slot connection in property manager and 
        command toolbar is handled in those classes. 

        Called once each time the command is entered; should be called only 
        by code in modes.py

        @see: L{self.restore_gui}
        """
        EditCommand.init_gui(self)        


        if isinstance(self.graphicsMode, CntLine_GM):
            self._setParamsForCntLineGraphicsMode()
            self.mouseClickPoints = []

        #Clear the segmentList as it may still be maintaining a list of segments
        #from the previous run of the command. 
        self._segmentList = []

        prevMode = self.commandSequencer.prevMode 
        if prevMode.commandName == 'BUILD_NANOTUBE':
            params = prevMode.provideParamsForTemporaryMode(self.commandName)
            self.callback_addSegments, self._parentNanotubeGroup = params
            
            #@TODO: self.callback_addSegments is not used as of 2008-02-24 
            #due to change in implementation. Not removing it for now as the 
            #new implementation (which uses the cntGroup object of 
            #InsertCnt_EditCommand is still being tested) -- Ninad 2008-02-24

            #Following won't be necessary after Command Toolbar is 
            #properly integrated into the Command/CommandSequencer API
            try:
                self.flyoutToolbar = prevMode.flyoutToolbar
                #Need a better way to deal with changing state of the 
                #corresponding action in the flyout toolbar. To be revised 
                #during command toolbar cleanup 
                self.flyoutToolbar.insertCntAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None


            if self.flyoutToolbar:
                if not self.flyoutToolbar.insertCntAction.isChecked():
                    self.flyoutToolbar.insertCntAction.setChecked(True)
        else:
            #Should this be an assertion? Should we always kill _parentNanotubeGroup
            #if its not None? ..not a good idea. Lets just make it to None. 
            self._parentNanotubeGroup = None             
            self._createFallbackNanotubeGroup()

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. This includes closing 
        this mode's property manager, updating the command toolbar ,
        Note: The slot connection/disconnection in property manager and 
        command toolbar is handled in those classes.
        @see: L{self.init_gui}
        """                    
        EditCommand.restore_gui(self)

        if isinstance(self.graphicsMode, CntLine_GM):
            self.mouseClickPoints = []

        self.graphicsMode.resetVariables()   

        if self.flyoutToolbar:
            self.flyoutToolbar.insertCntAction.setChecked(False)

        self._parentNanotubeGroup = None 
        self._fallbackNanotubeGroup = None
        self._segmentList = []


    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None   
    
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that cnt_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        if not bool_keep: 
            #Don't delete any CntSegements or NanotubeGroups at all while 
            #in InsertCnt_EditCommand. 
            #Reason: See BreakStrand_Command.keep_empty_group. In addition to 
            #this, this command can create multiple NanotubeSegments Although those 
            #won't be empty, it doesn't hurt in waiting for this temporary 
            #command to exit before deleting any empty groups.             
            if isinstance(group, self.assy.NanotubeSegment) or \
                 isinstance(group, self.assy.NanotubeGroup):
                bool_keep = True
        
        return bool_keep


    def create_and_or_show_PM_if_wanted(self, showPropMgr = True):
        """
        Create the property manager object if one doesn't already exist 
        and then show the propMgr if wanted by the user. 
        @param showPropMgr: If True, show the property manager 
        @type showPropMgr: boolean
        """
        EditCommand.create_and_or_show_PM_if_wanted(
            self,
            showPropMgr = showPropMgr)

        self.propMgr.updateMessage("Specify two points in the 3D Graphics " \
                                   "Area to define the endpoints of the "\
                                   "nanotube."
                               )

    def createStructure(self, showPropMgr = True):
        """
        Overrides superclass method. Creates the structure (NanotubeSegment) 

        """        
        assert self.propMgr is not None

        if self.struct is not None:
            self.struct = None

        self.win.assy.part.ensure_toplevel_group()
        self.propMgr.endPoint1 = self.mouseClickPoints[0]
        self.propMgr.endPoint2 = self.mouseClickPoints[1]
        cntLength = vlen(self.mouseClickPoints[0] - self.mouseClickPoints[1])

        #@numberOfCells = getNumberOfCellsFromCntLength(cntLength)
        #@self.propMgr.numberOfCellsSpinBox.setValue(numberOfCells)

        self.preview_or_finalize_structure(previewing = True)

        #Unpick the cnt segments (while this command was still 
        #running. ) This is necessary , so that when you strat drawing 
        #rubberband line, it matches the display style of the glpane. 
        #If something was selected, and while in NanotubeLineMode you changed the
        #display style, it will be applied only to the selected chunk. 
        #(and the glpane's display style will not change. This , in turn 
        #won't change the display of the rubberband line being drawn. 
        #Another bug: What if something else in the glpane is selected? 
        #complete fix would be to call unpick_all_in_the_glpane. But 
        #that itself is undesirable. Okay for now -- Ninad 2008-02-20
        #UPDATE 2008-02-21: The following code is commented out. Don't 
        #change the selection state of the 
        ##if self._fallbackNanotubeGroup is not None:
            ##for segment in self._fallbackNanotubeGroup.members:
                ##segment.unpick()


        #Now append this cntSegment  to self._segmentList 
        self._segmentList.append(self.struct)

        #clear the mouseClickPoints list
        self.mouseClickPoints = [] 
        self.graphicsMode.resetVariables()


    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = InsertCnt_PropertyManager(self.win, self)
        return propMgr


    def _createStructure(self):
        """
        creates and returns the structure (in this case a L{Group} object that 
        contains the nanotube. 
        @return : group containing the carbon nanotube chunks.
        @rtype: L{Group}  
        @note: This needs to return a CNT object once that model is implemented        
        """
        return self._createSegment()
    
    def _finalizeStructure(self):
        """
        Finalize the structure. This is a step just before calling Done method.
        to exit out of this command. Subclasses may overide this method
        @see: EditCommand_PM.ok_btn_clicked
        @see: NanotubeSegment_EditCommand where this method is overridden. 
        """
        #The following can happen in this case: User creates first nanotube, 
        #Now clicks inside 3D workspace to define the first point of the 
        #next nanotube. Now moves the mouse to draw cnt rubberband line. 
        #and then its 'Done' When it does that, it has modified the 
        #'number of base pairs' value in the PM and then it uses that value 
        #to modify self.struct ...which is the first segment user created!
        #In order to avoid this, either self.struct should be set to None after
        #its appended to the segment list (in self.createStructure) 
        #Or it should compute the number of base pairs each time instead of 
        #relying on the corresponding value in the PM. The latter is not 
        #advisable if we support modifying the number of base pairs from the 
        #PM (and hitting preview) while in InsertCnt command. 
        #In the mean time, I think this solution will always work. 
        if len(self.mouseClickPoints) == 1:
            return
        else:
            EditCommand._finalizeStructure(self)
        

    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfCells
                 - cntType
                 - cellsPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """        

        return self.propMgr.getParameters()       

    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Cnt, Nanotube etc) . .
        See more comments in the method.
        @see: a note in self._createSegment() about use of cntSegment.setProps 
        """    
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the CNT object model 
        # will solve this problem. (i.e. reusing the object and just modifying
        #its attributes.  Till that time, we'll continue to use 
        #what the old GeneratorBaseClass use to do ..i.e. remove the item and 
        # create a new one  -- Ninad 2007-10-24

        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
        return 

    def cancelStructure(self):
        """
        Overrides Editcommand.cancelStructure ..calls _removeSegments which 
        deletes all the segments created while this command was running
        @see: B{EditCommand.cancelStructure}
        """

        EditCommand.cancelStructure(self)
        self._removeSegments()

    def _removeSegments(self):
        """
        Remove the segments created while in this command self._fallbackNanotubeGroup 
        (if one exists its a bug).

        This deletes all the segments created while this command was running
        @see: L{self.cancelStructure}
        """

        segmentList = []

        if self._parentNanotubeGroup is not None:
            segmentList = self._segmentList
        elif self._fallbackNanotubeGroup is not None:
            segmentList = self._fallbackNanotubeGroup.get_segments()
            

        for segment in segmentList: 
            #can segment be None?  Lets add this condition to be on the safer 
            #side.
            if segment is not None: 
                segment.kill_with_contents()
            self._revertNumber()
        
        if self._fallbackNanotubeGroup is not None:
            self._fallbackNanotubeGroup.kill()
            self._fallbackNanotubeGroup = None
            

        self._segmentList = []	
        self.win.win_update()

    def _createSegment(self):
        """
        Creates and returns the structure (in this case a L{Group} object that 
        contains the nanotube chunk. 
        @return : group containing the nanotube chunk.
        @rtype: L{Group}  
        @note: This needs to return a CNT object once that model is implemented        
        """

        # No error checking here; do all error checking in _gatherParameters().
        params = self._gatherParameters()

        
        cnt = Cnt()
        self.cnt  =  cnt  # needed for done msg

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # Cnt group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()

        if self._parentNanotubeGroup is None:
            print_compact_stack("bug: Parent NanotubeGroup in InsertCnt_EditCommand"\
                                "is None. This means the previous command "\
                                "was not 'InsertCnt_EditCommand' Ignoring for now")
            if self._fallbackNanotubeGroup is None:
                self._createFallbackNanotubeGroup()

            cntGroup = self._fallbackNanotubeGroup
        else:
            cntGroup = self._parentNanotubeGroup

        cntSegment = NanotubeSegment(self.name, 
                                     self.win.assy,
                                     cntGroup,
                                     editCommand = self  )
        try:
            # Make the nanotube. <cntGroup> will contain one chunk:
            #  - Axis (Segment)
            position = V(0.0, 0.0, 0.0)
            cntChunk = cnt.build(self.name, self.win.assy, params, position)
            
            cntSegment.addchild(cntChunk)

            #set some properties such as cntRise and number of cells per turn
            #This information will be stored on the NanotubeSegment object so that
            #it can be retrieved while editing this object. 
            #This works with or without cnt_updater. Now the question is 
            #should these props be assigned to the NanotubeSegment in 
            #insertCnt.make() itself ? This needs to be answered while modifying
            #make() method to fit in the cnt data model. --Ninad 2008-03-05
            
            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() (which in turn calls self._createSegment() 
            #in this case) If in the near future, we actually permit modifying a
            #structure (such as cnt) without actually recreating the whole 
            #structure, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            #@props = (cntRise, cellsPerTurn)

            #@cntSegment.setProps(props)

            return cntSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            self._segmentList.remove(cntSegment)
            cntSegment.kill_with_contents()
            raise PluginBug("Internal error while trying to create Nanotube.")

    def provideParamsForTemporaryMode(self, temporaryModeName):
        """
        NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs to send some data from 
	previous mode to the temporary mode .	 
	@see: B{NanotubeLineMode}
	@see: self.acceptParamsFromTemporaryMode 
        """
        assert temporaryModeName == 'CNT_LINE_MODE'

        mouseClickLimit = None
        cntRise =  self.getCntRise()

        callback_cursorText = self.getCursorTextForTemporaryMode
        callback_snapEnabled = self.isRubberbandLineSnapEnabled
        callback_rubberbandLineDisplay = self.getDisplayStyleForRubberbandLine
        
        return (mouseClickLimit, 
                cntRise, 
                callback_cursorText, 
                callback_snapEnabled, 
                callback_rubberbandLineDisplay )

    def getCursorTextForTemporaryMode(self, endPoint1, endPoint2):
        """
        This is used as a callback method in CntLine mode 
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        cntLength = vlen(endPoint2 - endPoint1)
        text = '%5.3f A' % cntLength
        return text 

    def isRubberbandLineSnapEnabled(self):
        """
        This returns True or False based on the checkbox state in the PM.

        This is used as a callback method in CntLine mode (CntLine_GM)
        @see: CntLine_GM.snapLineEndPoint where the boolean value returned from
              this method is used
        @return: Checked state of the linesnapCheckBox in the PM
        @rtype: boolean
        """
        return self.propMgr.lineSnapCheckBox.isChecked()

    def getDisplayStyleForRubberbandLine(self):
        """
        This is used as a callback method in CntLine mode . 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        return self.propMgr.cntRubberBandLineDisplayComboBox.currentText()

    def getCntRise(self):
        """
        This is used as a callback method in CntLine mode. 
        @return: The current nanotube rise. 
        @rtype: float
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        return self.propMgr.cntRiseDoubleSpinBox.value()
    
    def getCntDiameter(self):
        """
        This is used as a callback method in CntLine mode. 
        @return: The current nanotube diameter. 
        @rtype: float
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        return self.propMgr.cntChirality.getRadius() * 2.0


    #Things needed for CntLine_GraphicsMode (CntLine_GM)======================

    def _setParamsForCntLineGraphicsMode(self):
        """
        Needed for CntLine_GraphicsMode (CntLine_GM). The method names need to
        be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        implementation of CntLine mode where it just used to supply some 
        parameters to the previous mode using the callbacks from the 
        previousmode. 
        """
        self.mouseClickLimit = None
        self.cntType = self.propMgr.typeComboBox.currentText()
        self.n = self.propMgr.chiralityNSpinBox.value()
        self.m = self.propMgr.chiralityMSpinBox.value()
        self.cntRise = getCntRise(self.cntType, self.n, self.m)
        self.cntDiameter = self.propMgr.cntChirality.getRadius() * 2.0
        print "cntDiameter=", self.cntDiameter
        #self.cellsPerTurn = self.propMgr.cellsPerTurnDoubleSpinBox.value()
        self.jigList = self.win.assy.getSelectedJigs()

        self.callbackMethodForCursorTextString = \
            self.getCursorTextForTemporaryMode

        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled

        self.callback_rubberbandLineDisplay = \
            self.getDisplayStyleForRubberbandLine
        
        self.cntDiameter = self.propMgr.cntChirality.getRadius() * 2.0