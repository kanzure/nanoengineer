# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplex_EditCommand.py
DnaDuplex_EditCommand that provides an editCommand object for 
generating DNA Duplex .  This command should be invoked only from 
BuildDna_EditCommand

@author: Mark Sims, Ninad Sathaye
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2007-10-24:
Created. Rewrote almost everything to implement EdiController as a superclass 
thereby deprecating the DnaDuplexGenerator class.

Ninad 2007-12-20: Converted this editController as a command on the 
                  commandSequencer.

TODO: 
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

import foundation.env as env
from command_support.EditCommand import EditCommand

from dna.model.DnaSegment import DnaSegment
from dna.model.DnaGroup import DnaGroup
from utilities.debug import print_compact_stack

from utilities.Log  import redmsg, greenmsg
from geometry.VQT import V, Veq, vlen
from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM3
from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM5

from command_support.GeneratorBaseClass import PluginBug, UserError
from dna.commands.BuildDuplex.DnaDuplexPropertyManager import DnaDuplexPropertyManager

from utilities.constants import gensym
from utilities.constants import black

from dna.model.Dna_Constants import getNumberOfBasePairsFromDuplexLength
from dna.model.Dna_Constants import getDuplexLength

from dna.commands.BuildDuplex.DnaDuplex_GraphicsMode import DnaDuplex_GraphicsMode

from utilities.prefs_constants import dnaDuplexEditCommand_cursorTextCheckBox_angle_prefs_key
from utilities.prefs_constants import dnaDuplexEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import dnaDuplexEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key
from utilities.prefs_constants import dnaDuplexEditCommand_cursorTextCheckBox_numberOfTurns_prefs_key
from utilities.prefs_constants import dnaDuplexEditCommand_showCursorTextCheckBox_prefs_key


_superclass = EditCommand

class DnaDuplex_EditCommand(EditCommand):
    """
    DnaDuplex_EditCommand that provides an editCommand object for 
    generating DNA Duplex . 

    This command should be invoked only from BuildDna_EditCommand 

    User can create as many Dna duplexes as he/she needs just by specifying 
    two end points for each dna duplex.This uses DnaLineMode_GM  class as its
    GraphicsMode 
    """
    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'DnaSegment'   # used for gensym
    cmdname          = "Duplex"

    commandName       = 'DNA_DUPLEX'
    featurename       = "Build Dna Duplex"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    #Graphics Mode set to DnaLine graphics mode
    GraphicsMode_class = DnaDuplex_GraphicsMode

    #required by DnaLine_GM
    mouseClickPoints = []
    #This is the callback method that the previous command 
    #(which is BuildDna_Editcommand as of 2008-01-11) provides. When user exits
    #this command and returns back to the previous one (BuildDna_EditCommand),
    #it calls this method and provides a list of segments created while this 
    #command was  running. (the segments are stored within a temporary dna group
    #see self._fallbackDnaGroup
    callback_addSegments  = None

    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None



    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for DnaDuplex_EditCommand
        """

        _superclass.__init__(self, commandSequencer)        

        #_fallbackDnaGroup stores the DnaSegments created while in 
        #this command. This temporary dnaGroup is created IF AND ONLY IF 
        #DnaDuplex_EditCommand is unable to access the dnaGroup object of the 
        #parent BuildDna_EditCommand. (so if this group gets created, it should
        #be considered as a bug. While exiting the command the list of segments 
        #of this group is given to the BuildDna_EditCommand where they get 
        #their new parent. @see self.restore_gui
        self._fallbackDnaGroup = None

        #_parentDnaGroup is the dnagroup of BuildDna_EditCommand 
        self._parentDnaGroup = None

        #Maintain a list of segments created while this command was running. 
        #Note that the segments , when created will be added directly to the 
        # self._parentDnaGroup (or self._fallbackDnaGroup if there is a bug) 
        # But self._parentDnaGroup (which must be = the dnaGroup of 
        # BuildDna_EditCommand.) may already contain DnaSegments (added earlier)
        # so, we can not use group.steal_members() in case user cancels the 
        #structure creation (segment addition). 
        self._segmentList = []

        self.struct = struct

    def _createFallbackDnaGroup(self):
        """
        Creates a temporary DnaGroup object in which all the DnaSegments 
        created while in this command will be added as members. 
        While exiting this command, these segments will be added first taken 
        away from the temporary group and then added to the DnaGroup of
        BuildDna_EditCommand 
        @see: self.restore_gui
        @see: BuildDna_EditCommand.callback_addSegments()
        """
        if self._fallbackDnaGroup is None:
            self.win.assy.part.ensure_toplevel_group()
            self._fallbackDnaGroup =  DnaGroup("Fallback Dna", 
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
        _superclass.init_gui(self)        

        if isinstance(self.graphicsMode, DnaDuplex_GraphicsMode):
            self._setParamsForDnaLineGraphicsMode()
            self.mouseClickPoints = []

        #Clear the segmentList as it may still be maintaining a list of segments
        #from the previous run of the command. 
        self._segmentList = []

        parentCommand_if_BUILD_DNA = self._init_gui_flyout_action( 'dnaDuplexAction' )
        if parentCommand_if_BUILD_DNA:
            params = parentCommand_if_BUILD_DNA.provideParamsForTemporaryMode(self.commandName)
            self.callback_addSegments, self._parentDnaGroup = params
            #@TODO: self.callback_addSegments is not used as of 2008-02-24 
            #due to change in implementation. Not removing it for now as the 
            #new implementation (which uses the dnaGroup object of 
            #BuildDna_EditCommand is still being tested) -- Ninad 2008-02-24

            # REVIEW: is the following ever needed? If so, should
            # _init_gui_flyout_action do it itself? [bruce 080726 question]
            if self.flyoutToolbar:
                if not self.flyoutToolbar.dnaDuplexAction.isChecked():
                    self.flyoutToolbar.dnaDuplexAction.setChecked(True)
        else:
            #Should this be an assertion? Should we always kill _parentDnaGroup
            #if its not None? ..not a good idea. Lets just make it to None. 
            self._parentDnaGroup = None             
            self._createFallbackDnaGroup()
            
        self.updateDrawingPlane(plane = None)

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. This includes closing 
        this mode's property manager, updating the command toolbar ,
        Note: The slot connection/disconnection in property manager and 
        command toolbar is handled in those classes.
        @see: L{self.init_gui}
        """                    
        _superclass.restore_gui(self)

        if isinstance(self.graphicsMode, DnaDuplex_GraphicsMode):
            self.mouseClickPoints = []

        self.graphicsMode.resetVariables()   

        if self.flyoutToolbar:
            self.flyoutToolbar.dnaDuplexAction.setChecked(False)

        self._parentDnaGroup = None 
        self._fallbackDnaGroup = None
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
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """

        bool_keep = _superclass.keep_empty_group(self, group)

        if not bool_keep: 
            #Don't delete any DnaSegements or DnaGroups at all while 
            #in DnaDuplex_EditCommand. 
            #Reason: See BreakStrand_Command.keep_empty_group. In addition to 
            #this, this command can create multiple DnaSegments Although those 
            #won't be empty, it doesn't hurt in waiting for this temporary 
            #command to exit before deleting any empty groups.             
            if isinstance(group, self.assy.DnaSegment) or \
               isinstance(group, self.assy.DnaGroup):
                bool_keep = True

        return bool_keep


    def create_and_or_show_PM_if_wanted(self, showPropMgr = True):
        """
        Create the property manager object if one doesn't already exist 
        and then show the propMgr if wanted by the user. 
        @param showPropMgr: If True, show the property manager 
        @type showPropMgr: boolean
        """
        _superclass.create_and_or_show_PM_if_wanted(
            self,
            showPropMgr = showPropMgr)

        self.propMgr.updateMessage("Specify two points in the 3D Graphics " \
                                   "Area to define the endpoints of the "\
                                   "DNA duplex."
                               )

    def createStructure(self, showPropMgr = True):
        """
        Overrides superclass method. Creates the structure (DnaSegment) 

        """        
        assert self.propMgr is not None

        if self.struct is not None:
            self.struct = None

        self.win.assy.part.ensure_toplevel_group()
        self.propMgr.endPoint1 = self.mouseClickPoints[0]
        self.propMgr.endPoint2 = self.mouseClickPoints[1]
        duplexLength = vlen(self.mouseClickPoints[0] - self.mouseClickPoints[1])

        numberOfBasePairs = \
                          getNumberOfBasePairsFromDuplexLength(
                              'B-DNA', 
                              duplexLength,
                              duplexRise = self.duplexRise)

        self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)

        self.preview_or_finalize_structure(previewing = True)

        #Unpick the dna segments (while this command was still 
        #running. ) This is necessary , so that when you strat drawing 
        #rubberband line, it matches the display style of the glpane. 
        #If something was selected, and while in DnaLineMode you changed the
        #display style, it will be applied only to the selected chunk. 
        #(and the glpane's display style will not change. This , in turn 
        #won't change the display of the rubberband line being drawn. 
        #Another bug: What if something else in the glpane is selected? 
        #complete fix would be to call unpick_all_in_the_glpane. But 
        #that itself is undesirable. Okay for now -- Ninad 2008-02-20
        #UPDATE 2008-02-21: The following code is commented out. Don't 
        #change the selection state of the 
        ##if self._fallbackDnaGroup is not None:
            ##for segment in self._fallbackDnaGroup.members:
                ##segment.unpick()


        #Now append this dnaSegment  to self._segmentList 
        self._segmentList.append(self.struct)

        #clear the mouseClickPoints list
        self.mouseClickPoints = [] 
        self.graphicsMode.resetVariables()
        self.win.win_update() #fixes bug 2810

    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = DnaDuplexPropertyManager(self.win, self)
        return propMgr


    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        @see: self.hasValidStructure()
        """
        return self.win.assy.DnaSegment


    def _finalizeStructure(self):
        """
        Finalize the structure. This is a step just before calling Done method.
        to exit out of this command. Subclasses may overide this method
        @see: EditCommand_PM.ok_btn_clicked
        @see: DnaSegment_EditCommand where this method is overridden. 
        """
        #The following can happen in this case: User creates first duplex, 
        #Now clicks inside 3D workspace to define the first point of the 
        #next duplex. Now moves the mouse to draw dna rubberband line. 
        #and then its 'Done' When it does that, it has modified the 
        #'number of base pairs' value in the PM and then it uses that value 
        #to modify self.struct ...which is the first segment user created!
        #In order to avoid this, either self.struct should be set to None after
        #its appended to the segment list (in self.createStructure) 
        #Or it should compute the number of base pairs each time instead of 
        #relying on the corresponding value in the PM. The latter is not 
        #advisable if we support modifying the number of base pairs from the 
        #PM (and hitting preview) while in DnaDuplex command. 
        #In the mean time, I think this solution will always work. 
        if len(self.mouseClickPoints) == 1:
            return
        else:
            _superclass._finalizeStructure(self)


    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfBases
                 - dnaForm
                 - basesPerTurn
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
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        @see: a note in self._createSStructure() about use of dnaSegment.setProps 
        """        
        
        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the DNA object model 
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

        _superclass.cancelStructure(self)
        self._removeSegments()

    def _removeSegments(self):
        """
        Remove the segments created while in this command self._fallbackDnaGroup 
        (if one exists its a bug).

        This deletes all the segments created while this command was running
        @see: L{self.cancelStructure}
        """

        segmentList = []

        if self._parentDnaGroup is not None:
            segmentList = self._segmentList
        elif self._fallbackDnaGroup is not None:
            segmentList = self._fallbackDnaGroup.get_segments()


        for segment in segmentList: 
            #can segment be None?  Lets add this condition to be on the safer 
            #side.
            if segment is not None: 
                segment.kill_with_contents()
            self._revertNumber()

        if self._fallbackDnaGroup is not None:
            self._fallbackDnaGroup.kill()
            self._fallbackDnaGroup = None


        self._segmentList = []	
        self.win.win_update()

    def _createStructure(self):
        """
        Creates and returns the structure (in this case a L{Group} object that 
        contains the DNA strand and axis chunks. 
        @return : group containing that contains the DNA strand and axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """

        params = self._gatherParameters()

        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        numberOfBases, \
                     dnaForm, \
                     dnaModel, \
                     basesPerTurn, \
                     duplexRise, \
                     endPoint1, \
                     endPoint2 = params

        if numberOfBases < 2:
            #Don't create a duplex with only one or 0 bases! 
            #Reset a few variables. This should be done by calling a separate 
            #method on command (there is similar code in self.createStructures)
            #as well. 
            self.mouseClickPoints = []
            self.graphicsMode.resetVariables()

            msg  = redmsg("Cannot preview/insert a DNA duplex with less than 2 base pairs.")
            self.propMgr.updateMessage(msg)

            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None
        else: 
            msg = "Specify two points in the 3D Graphics Area to define the "\
                "endpoints of the DNA duplex"
            self.propMgr.updateMessage(msg)


        #If user enters the number of basepairs and hits preview i.e. endPoint1
        #and endPoint2 are not entered by the user and thus have default value 
        #of V(0, 0, 0), then enter the endPoint1 as V(0, 0, 0) and compute
        #endPoint2 using the duplex length. 
        #Do not use '==' equality check on vectors! its a bug. Use same_vals 
        # or Veq instead. 
        if Veq(endPoint1 , endPoint2) and Veq(endPoint1, V(0, 0, 0)):
            endPoint2 = endPoint1 + \
                      self.win.glpane.right * \
                      getDuplexLength('B-DNA', numberOfBases)

        if dnaForm == 'B-DNA':
            if dnaModel == 'PAM3':
                dna = B_Dna_PAM3()
            elif dnaModel == 'PAM5':
                dna = B_Dna_PAM5()
            else:
                print "bug: unknown dnaModel type: ", dnaModel
        else:
            raise PluginBug("Unsupported DNA Form: " + dnaForm)

        self.dna  =  dna  # needed for done msg

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
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()

        if self._parentDnaGroup is None:
            print_compact_stack("bug: Parent DnaGroup in DnaDuplex_EditCommand"\
                                "is None. This means the previous command "\
                                "was not 'BuildDna_EditCommand' Ignoring for now")
            if self._fallbackDnaGroup is None:
                self._createFallbackDnaGroup()

            dnaGroup = self._fallbackDnaGroup
        else:
            dnaGroup = self._parentDnaGroup


        dnaSegment = DnaSegment(self.name, 
                                self.win.assy,
                                dnaGroup,
                                editCommand = self  )
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis
            dna.make(dnaSegment, 
                     numberOfBases, 
                     basesPerTurn, 
                     duplexRise,
                     endPoint1,
                     endPoint2)

            #set some properties such as duplexRise and number of bases per turn
            #This information will be stored on the DnaSegment object so that
            #it can be retrieved while editing this object. 
            #This works with or without dna_updater. Now the question is 
            #should these props be assigned to the DnaSegment in 
            #dnaDuplex.make() itself ? This needs to be answered while modifying
            #make() method to fit in the dna data model. --Ninad 2008-03-05

            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() If in the near future, we actually permit 
            #modifying a
            #structure (such as dna) without actually recreating the whole 
            #structre, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            props = (duplexRise, basesPerTurn)

            dnaSegment.setProps(props)

            return dnaSegment


        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            dnaSegment.kill_with_contents()
            raise PluginBug("Internal error while trying to create DNA duplex.")


    def getCursorText(self, endPoint1, endPoint2):
        """
        This is used as a callback method in DnaLine mode 
        @see: DnaLineMode.setParams, DnaLineMode_GM.Draw
        """
        if endPoint1 is None or endPoint2 is None:
            return '', black

        if not env.prefs[dnaDuplexEditCommand_showCursorTextCheckBox_prefs_key]:
            return '', black

        text = ''        
        textColor = black

        numberOfBasePairsString = ''
        numberOfTurnsString = ''
        duplexLengthString = ''
        thetaString = ''


        duplexLength = vlen(endPoint2 - endPoint1)

        numberOfBasePairs = getNumberOfBasePairsFromDuplexLength( 
            'B-DNA', 
            duplexLength,
            duplexRise = self.duplexRise)

        numberOfBasePairsString = self._getCursorText_numberOfBasePairs(
            numberOfBasePairs)

        numberOfTurnsString = self._getCursorText_numberOfTurns(
            numberOfBasePairs)

        
        duplexLengthString = self._getCursorText_length(duplexLength)


        if env.prefs[dnaDuplexEditCommand_cursorTextCheckBox_angle_prefs_key]:
            vec = endPoint2 - endPoint1        
            theta = self.glpane.get_angle_made_with_screen_right(vec)
            thetaString = "%5.2f deg"%theta

        commaString = ", "
        text = numberOfBasePairsString 

        if text and numberOfTurnsString:
            text += commaString

        text += numberOfTurnsString

        if text and duplexLengthString:
            text += commaString

        text += duplexLengthString

        if text and thetaString:
            text += commaString

        text += thetaString

        #@TODO: The following updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString -- Ninad 2007-12-20
        self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)

        return text , textColor
        

    def _getCursorText_numberOfBasePairs(self, numberOfBasePairs):
        numberOfBasePairsString = ''

        if env.prefs[
            dnaDuplexEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key]:
            numberOfBasePairsString = "%db"%numberOfBasePairs

        return numberOfBasePairsString

    def _getCursorText_numberOfTurns(self, numberOfBasePairs):
        numberOfTurnsString = '' 
        if env.prefs[dnaDuplexEditCommand_cursorTextCheckBox_numberOfTurns_prefs_key]:
            numberOfTurns = numberOfBasePairs / self.basesPerTurn
            numberOfTurnsString = '(%5.3ft)'%numberOfTurns

        return numberOfTurnsString

    def _getCursorText_length(self, duplexLength):
        duplexLengthString = ''
        if env.prefs[dnaDuplexEditCommand_cursorTextCheckBox_length_prefs_key]:
            lengthUnitString = 'A'
            #change the unit of length to nanometers if the length is > 10A
            #fixes part of bug 2856
            if duplexLength > 10.0:
                lengthUnitString = 'nm'
                duplexLength = duplexLength * 0.1
            duplexLengthString = "%5.3f%s"%(duplexLength, lengthUnitString)
        
        return duplexLengthString

    def _getCursorText_angle(self):
        pass
    
    def listWidgetHasFocus(self):
        """
        Delegates this to self.propMgr. 
        @see: DnaDuplex_PropertyManager.listWidgetHasFocus()
        """
        return self.propMgr.listWidgetHasFocus()
    
    def removeListWidgetItems(self):
        """
        Delegates this to self.propMgr. 
        @see: DnaDuplex_PropertyManager.removeListWidgetItems()
        """
        return self.propMgr.removeListWidgetItems()

    def useSpecifiedDrawingPlane(self):
        """
        Returns True if the drawing plane specified in the Property manager 
        should be used as a placement plane for the Dna duplex. 
        
        @see: self.isSpecifyPlaneToolActive()
        @see: LineMode_GM.bareMotion() to see how this is ultimately used. 
        @see: LineMode_GM.leftDown()
        @see: DnaLine_GM.leftUp()
        """
        if self.propMgr:
            return self.propMgr.useSpecifiedDrawingPlane()
        return False
    
    def updateDrawingPlane(self, plane = None):
        """
        Delegates this to self.propMgr.
        @see: DnaDuplex_GraphicsMode.jigLeftUp
        @see: DnaDuplex_graphicsMode.setDrawingPlane()        
        """
        self.graphicsMode.setDrawingPlane(plane)
        if self.propMgr:
            self.propMgr.updateReferencePlaneListWidget(plane)
        
    def isSpecifyPlaneToolActive(self):
        """
        Returns True if the Specify reference plane radio button is enabled 
        AND there is no reference plane specified on which the Dna duplex 
        will be drawn. (Delegates this to the propMgr.)
        
        @see: DnaDuplex_Graphicsmode.isSpecifyPlaneToolActive()
        @see: self.useSpecifiedDrawingPlane()
        """
        if self.propMgr:
            return self.propMgr.isSpecifyPlaneToolActive()   
        
        return False

    def isRubberbandLineSnapEnabled(self):
        """
        This returns True or False based on the checkbox state in the PM.

        This is used as a callback method in DnaLine mode (DnaLine_GM)
        @see: DnaLine_GM.snapLineEndPoint where the boolean value returned from
              this method is used
        @return: Checked state of the linesnapCheckBox in the PM
        @rtype: boolean
        """
        return self.propMgr.lineSnapCheckBox.isChecked()

    def getDisplayStyleForRubberbandLine(self):
        """
        This is used as a callback method in DnaLine mode . 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @see: DnaLineMode.setParams, DnaLineMode_GM.Draw
        """
        return self.propMgr.dnaRubberBandLineDisplayComboBox.currentText()

    def getDuplexRise(self):
        """
        This is used as a callback method in DnaLine mode . 
        @return: The current duplex rise. 
        @rtype: float
        @see: DnaLineMode.setParams, DnaLineMode_GM.Draw
        """
        return self.propMgr.duplexRiseDoubleSpinBox.value()


    #Things needed for DnaLine_GraphicsMode (DnaLine_GM)======================

    def _setParamsForDnaLineGraphicsMode(self):
        """
        Needed for DnaLine_GraphicsMode (DnaLine_GM). The method names need to
        be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        implementation of DnaLine mode where it just used to supply some 
        parameters to the previous mode using the callbacks from the 
        previousmode. 
        """
        self.mouseClickLimit = None
        # self.duplexRise = getDuplexRise('B-DNA')
        self.duplexRise = self.propMgr.duplexRiseDoubleSpinBox.value()
        self.basesPerTurn = self.propMgr.basesPerTurnDoubleSpinBox.value()
        self.jigList = self.win.assy.getSelectedJigs()

        self.callbackMethodForCursorTextString = \
            self.getCursorText

        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled

        self.callback_rubberbandLineDisplay = \
            self.getDisplayStyleForRubberbandLine
