# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
InsertNanotube_EditCommand.py
InsertNanotube_EditCommand that provides an editCommand object for 
generating a nanotube (CNT or BNNT).  This command should be invoked only from 
NanotubeProperties_EditCommand

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

from command_support.GeneratorBaseClass import PluginBug, UserError
from cnt.commands.InsertNanotube.InsertNanotube_PropertyManager import InsertNanotube_PropertyManager

from utilities.constants import gensym

from cnt.temporary_commands.NanotubeLineMode import NanotubeLine_GM


class InsertNanotube_EditCommand(EditCommand):
    """
    InsertNanotube_EditCommand that provides an editCommand object for 
    generating carbon or boron nitride nanotube. 

    This command should be invoked only from InsertNanotube_EditCommand 

    User can create as many nanotubes as he/she needs just by specifying 
    two end points for each nanotube. This uses NanotubeLineMode_GM  class as its
    GraphicsMode 
    """
    cmd              =  greenmsg("Insert Nanotube: ")
    sponsor_keyword  =  'Nanotube'
    prefix           =  'Nanotube'   # used for gensym
    cmdname          = "Insert Nanotube"
    commandName      = 'INSERT_NANOTUBE'
    featurename      = 'Insert Nanotube'

    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    #Graphics Mode set to CntLine graphics mode
    GraphicsMode_class = NanotubeLine_GM

    #required by NanotubeLine_GM
    mouseClickPoints = []
    #This is the callback method that the previous command 
    #(which is InsertNanotube_Editcommand as of 2008-01-11) provides. When user exits
    #this command and returns back to the previous one (InsertNanotube_EditCommand),
    #it calls this method and provides a list of segments created while this 
    #command was  running. (the segments are stored within a temporary cnt group
    #see self._fallbackNanotubeGroup
    callback_addSegments  = None

    #This is set to InsertNanotube_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for InsertNanotube_EditCommand
        """

        EditCommand.__init__(self, commandSequencer)        

        #_fallbackNanotubeGroup stores the NanotubeSegments created while in 
        #this command. This temporary ntGroup is created IF AND ONLY IF 
        #InsertNanotube_EditCommand is unable to access the ntGroup object of the 
        #parent InsertNanotube_EditCommand. (so if this group gets created, it should
        #be considered as a bug. While exiting the command the list of segments 
        #of this group is given to the InsertNanotube_EditCommand where they get 
        #their new parent. @see self.restore_gui
        self._fallbackNanotubeGroup = None

        #_parentNanotubeGroup is the cntgroup of InsertNanotube_EditCommand 
        self._parentNanotubeGroup = None

        #Maintain a list of segments created while this command was running. 
        #Note that the segments , when created will be added directly to the 
        # self._parentNanotubeGroup (or self._fallbackNanotubeGroup if there is a bug) 
        # But self._parentNanotubeGroup (which must be = the ntGroup of 
        # InsertNanotube_EditCommand.) may already contain NanotubeSegments (added earlier)
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
        InsertNanotube_EditCommand 
        @see: self.restore_gui
        @see: InsertNanotube_EditCommand.callback_addSegments()
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


        if isinstance(self.graphicsMode, NanotubeLine_GM):
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
            #new implementation (which uses the ntGroup object of 
            #InsertNanotube_EditCommand is still being tested) -- Ninad 2008-02-24

            #Following won't be necessary after Command Toolbar is 
            #properly integrated into the Command/CommandSequencer API
            try:
                self.flyoutToolbar = prevMode.flyoutToolbar
                #Need a better way to deal with changing state of the 
                #corresponding action in the flyout toolbar. To be revised 
                #during command toolbar cleanup 
                self.flyoutToolbar.insertNanotubeAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None


            if self.flyoutToolbar:
                if not self.flyoutToolbar.insertNanotubeAction.isChecked():
                    self.flyoutToolbar.insertNanotubeAction.setChecked(True)
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

        if isinstance(self.graphicsMode, NanotubeLine_GM):
            self.mouseClickPoints = []

        self.graphicsMode.resetVariables()   

        if self.flyoutToolbar:
            self.flyoutToolbar.insertNanotubeAction.setChecked(False)

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
            #in InsertNanotube_EditCommand. 
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
        ntLength = vlen(self.mouseClickPoints[0] - self.mouseClickPoints[1])

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


        #Now append this ntSegment  to self._segmentList 
        self._segmentList.append(self.struct)

        #clear the mouseClickPoints list
        self.mouseClickPoints = [] 
        self.graphicsMode.resetVariables()


    def _createPropMgrObject(self):
        """
        Creates a property manager object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = InsertNanotube_PropertyManager(self.win, self)
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
        #PM (and hitting preview) while in InsertNanotube command. 
        #In the mean time, I think this solution will always work. 
        if len(self.mouseClickPoints) == 1:
            return
        else:
            EditCommand._finalizeStructure(self)
        

    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: The nanotube, which contains all the attrs.
        @rtype:  Nanotube
        """        

        return self.propMgr.getParameters()       

    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Cnt, Nanotube etc) . .
        See more comments in the method.
        @see: a note in self._createSegment() about use of ntSegment.setProps 
        """    
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
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
        
        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # Nanotube group will be placed), if the topnode is not a group, make it
        # a 'Group' (applicable to Clipboard parts). See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()

        if self._parentNanotubeGroup is None:
            print_compact_stack("bug: Parent NanotubeGroup in InsertNanotube_EditCommand"\
                                "is None. This means the previous command "\
                                "was not 'InsertNanotube_EditCommand' Ignoring for now")
            if self._fallbackNanotubeGroup is None:
                self._createFallbackNanotubeGroup()

            ntGroup = self._fallbackNanotubeGroup
        else:
            ntGroup = self._parentNanotubeGroup

        ntSegment = NanotubeSegment(self.name, 
                                    self.win.assy,
                                    ntGroup,
                                    editCommand = self)
        try:
            # Make the nanotube. <ntGroup> will contain one chunk:
            #  - Axis (Segment)
            # No error checking here; do all error checking in _gatherParameters().
            nanotube = self._gatherParameters()
            position = V(0.0, 0.0, 0.0)
            self.nanotube  =  nanotube  # needed for done msg #@
            ntChunk = nanotube.build(self.name, self.win.assy, position)
            
            ntSegment.addchild(ntChunk)

            #set some properties such as ntRise and its two endpoints.
            #This information will be stored on the NanotubeSegment object so that
            #it can be retrieved while editing this object. 
            
            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() (which in turn calls self._createSegment() 
            #in this case) If in the near future, we actually permit modifying a
            #structure (such as a nanotube) without actually recreating the  
            #entire structure, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            #props = (nanotube.getRise(), nanotube.endPoint1, nanotube.endPoint2) #@ - use getEndPoints()?
            props =(nanotube.getChirality(),
                    nanotube.getType(),
                    nanotube.getEndings(),
                    nanotube.getEndPoints())
            
            ntSegment.setProps(props)

            return ntSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            self._segmentList.remove(ntSegment)
            ntSegment.kill_with_contents()
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
        assert temporaryModeName == 'NANOTUBE_LINE_MODE'

        mouseClickLimit = None
        ntRise =  self.nanotube.ntRise()

        callback_cursorText = self.getCursorTextForTemporaryMode
        callback_snapEnabled = self.isRubberbandLineSnapEnabled
        callback_rubberbandLineDisplay = self.getDisplayStyleForNtRubberbandLine
        
        return (mouseClickLimit, 
                ntRise, 
                callback_cursorText, 
                callback_snapEnabled, 
                callback_rubberbandLineDisplay )

    def getCursorTextForTemporaryMode(self, endPoint1, endPoint2):
        """
        This is used as a callback method in CntLine mode 
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        ntLength = vlen(endPoint2 - endPoint1)
        text = '%5.3f A' % ntLength
        return text 

    def isRubberbandLineSnapEnabled(self):
        """
        This returns True or False based on the checkbox state in the PM.

        This is used as a callback method in CntLine mode (NanotubeLine_GM)
        @see: NanotubeLine_GM.snapLineEndPoint where the boolean value returned from
              this method is used
        @return: Checked state of the linesnapCheckBox in the PM
        @rtype: boolean
        """
        return self.propMgr.lineSnapCheckBox.isChecked()

    def getDisplayStyleForNtRubberbandLine(self):
        """
        This is used as a callback method in ntLine mode. 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        return self.propMgr.ntRubberBandLineDisplayComboBox.currentText()
    
    # Things needed for CntLine_GraphicsMode (NanotubeLine_GM) ======================

    def _setParamsForCntLineGraphicsMode(self):
        """
        Needed for CntLine_GraphicsMode (NanotubeLine_GM). The method names need to
        be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        implementation of CntLine mode where it just used to supply some 
        parameters to the previous mode using the callbacks from the 
        previousmode. 
        """
        self.mouseClickLimit = None
        self.nanotube = self.propMgr.nanotube
        self.ntType = self.nanotube.getType()
        self.n, self.m = self.nanotube.getChirality()
        self.ntRise = self.nanotube.getRise()
        self.ntDiameter = self.nanotube.getDiameter()

        self.jigList = self.win.assy.getSelectedJigs()

        self.callbackMethodForCursorTextString = \
            self.getCursorTextForTemporaryMode

        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled

        self.callback_rubberbandLineDisplay = \
            self.getDisplayStyleForNtRubberbandLine