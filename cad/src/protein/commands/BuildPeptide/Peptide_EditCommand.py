# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Piotr, Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-24: Created

TODO:
"""

from utilities.Log  import greenmsg
from command_support.EditCommand import EditCommand
from protein.commands.BuildPeptide.PeptideGenerator import PeptideGenerator
from utilities.constants import gensym
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from protein.temporary_commands.PeptideLineMode import PeptideLine_GM

_superclass = EditCommand
class Peptide_EditCommand(EditCommand):
    cmd              =  greenmsg("Build Peptide: ")
    sponsor_keyword  =  'Peptide'
    prefix           =  'Peptide'   # used for gensym
    cmdname          = 'Build Peptide'

    commandName      = 'BUILD_PEPTIDE'
    featurename      = "Build Peptide"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_PROTEIN'

    create_name_from_prefix  =  True 
    
    #GraphicsMode_class = SelectChunks_GraphicsMode
    #Graphics Mode set to Peptide graphics mode
    GraphicsMode_class = PeptideLine_GM
    #required by NanotubeLine_GM
    mouseClickPoints = []
    
    structGenerator = PeptideGenerator()
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = True

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for Peptide_EditCommand
        """

        _superclass.__init__(self, commandSequencer)        
        #Maintain a list of peptide segments created while this command was running. 
        self._segmentList = []
        self.struct = struct
        
    
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

        if isinstance(self.graphicsMode, PeptideLine_GM):
            self._setParamsForPeptideLineGraphicsMode()
            self.mouseClickPoints = []
        #Clear the segmentList as it may still be maintaining a list of segments
        #from the previous run of the command. 
        self._segmentList = []
        self._init_gui_flyout_action( 'buildPeptideAction' ) 


    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. This includes closing 
        this mode's property manager, updating the command toolbar ,
        Note: The slot connection/disconnection in property manager and 
        command toolbar is handled in those classes.
        @see: L{self.init_gui}
        """                    
        _superclass.restore_gui(self)

        if isinstance(self.graphicsMode, PeptideLine_GM):
            self.mouseClickPoints = []

        self.graphicsMode.resetVariables()   

        if self.flyoutToolbar:
            self.flyoutToolbar.buildPeptideAction.setChecked(False)

        self._segmentList = []
    
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

        bool_keep = _superclass.keep_empty_group(self, group)
        return bool_keep

        
    def _gatherParameters(self):
        """
        Return the parameters from the property manager.
        """
        return self.propMgr.getParameters()  
    
    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None
    
    def _createStructure(self):        
        """
        Build a Peptide sheet from the parameters in the Property Manager.
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
            
            
        params = self._gatherParameters()
        
        #
        self.win.assy.part.ensure_toplevel_group()
        """
        struct = self.structGenerator.make(self.win.assy,
                                           name, 
                                           params, 
                                           -self.win.glpane.pov)
        """                                   
        from geometry.VQT import V
        pos1 = V(self.mouseClickPoints[0][0], self.mouseClickPoints[0][1], self.mouseClickPoints[0][2])
        pos2 = V(self.mouseClickPoints[1][0], self.mouseClickPoints[1][1], self.mouseClickPoints[1][2])
        struct = self.structGenerator.make_aligned(self.win.assy, name, params[0][0][0], params[0][0][1], params[0][0][2], pos2, pos1)
        self.win.assy.part.topnode.addmember(struct)
        self.win.win_update()
        return struct
        
    
    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. 
        See more comments in this method.
        """
        
        #@NOTE: Unlike editcommands such as Plane_EditCommand or 
        #DnaSegment_EditCommand this  actually removes the structure and
        #creates a new one when its modified. 
        #TODO: Change this implementation to make it similar to whats done 
        #iin DnaSegment resize. (see DnaSegment_EditCommand)
        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
    
    
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
        Remove the segments created while in this command 

        This deletes all the segments created while this command was running
        @see: L{self.cancelStructure}
        """
        segmentList = self._segmentList

        #for segment in segmentList: 
            #can segment be None?  Lets add this condition to be on the safer 
            #side.
        #    if segment is not None: 
        #        segment.kill_with_contents()
        #    self._revertNumber()


        self._segmentList = []	
        self.win.win_update()    
    
    def createStructure(self, showPropMgr = True):
        """
        Overrides superclass method. Creates the structure 

        """        
        assert self.propMgr is not None

        if self.struct is not None:
            self.struct = None

        self.win.assy.part.ensure_toplevel_group()
        self.propMgr.endPoint1 = self.mouseClickPoints[0]
        self.propMgr.endPoint2 = self.mouseClickPoints[1]
        #ntLength = vlen(self.mouseClickPoints[0] - self.mouseClickPoints[1])

        self.preview_or_finalize_structure(previewing = True)

        #Now append this ntSegment  to self._segmentList 
        self._segmentList.append(self.struct)

        #clear the mouseClickPoints list
        self.mouseClickPoints = [] 
        self.graphicsMode.resetVariables()    
        return
    
    def _finalizeStructure(self):
        """
        Finalize the structure. This is a step just before calling Done method.
        to exit out of this command. Subclasses may overide this method
        @see: EditCommand_PM.ok_btn_clicked
        @see: NanotubeSegment_EditCommand where this method is overridden. 
        """
        
        if len(self.mouseClickPoints) == 1:
            return
        else:
            _superclass._finalizeStructure(self)
        return
    
    
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
                                   "peptide chain."
                               )
        return
    
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr

        propMgr = self.win.createBuildPeptidePropMgr_if_needed(self)

        return propMgr
    
            
    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.Chunk

    # Things needed for CntLine_GraphicsMode (NanotubeLine_GM) ======================
    
    def _setParamsForPeptideLineGraphicsMode(self):
        #"""
        #Needed for PeptideLine_GraphicsMode (NanotubeLine_GM). The method names need to
        #be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        #implementation of CntLine mode where it just used to supply some 
        #parameters to the previous mode using the callbacks from the 
        #previousmode. 
        #"""
        self.mouseClickLimit = None
        self.jigList = self.win.assy.getSelectedJigs()
        self.callbackMethodForCursorTextString = self.getCursorText
        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled
        self.callback_rubberbandLineDisplay = self.getDisplayStyleForNtRubberbandLine
        return
    
    def getCursorText(self, endPoint1, endPoint2):
        """
        This is used as a callback method in CntLine mode 
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        if endPoint1 is None or endPoint2 is None:
            return
        
        #if not env.prefs[insertNanotubeEditCommand_showCursorTextCheckBox_prefs_key]:
        #    return '', black
        from utilities.constants import black
        textColor = black
        vec = endPoint2 - endPoint1
        from geometry.VQT import vlen
        peptideLength = vlen(vec)
        params = self._gatherParameters()
        peptideLength = self.structGenerator.get_number_of_res(endPoint1, endPoint2, params[0][0][1], params[0][0][2])
        lengthString = self._getCursorText_length(peptideLength)
        
        
        thetaString = ''
        #Urmi 20080804: not sure if angle will be required later
        #if env.prefs[insertNanotubeEditCommand_cursorTextCheckBox_angle_prefs_key]:
        theta = self.glpane.get_angle_made_with_screen_right(vec)
        thetaString = '%5.2f deg'%theta
            
            
        commaString = ", "
        
        text = lengthString

        if text and thetaString:
            text += commaString

        text += thetaString
        
        return text , textColor
    
    
    def _getCursorText_length(self, peptideLength):
        """
        Returns a string that gives the length of the Nanotube for the cursor 
        text
        """
        peptideLengthString = ''
        
        lengthUnitString = 'AA'
        #change the unit of length to nanometers if the length is > 10A
        #fixes part of bug 2856
        
        peptideLengthString = "%d%s"%(peptideLength, lengthUnitString)
    
        return peptideLengthString
    
    def getDisplayStyleForNtRubberbandLine(self):
        """
        This is used as a callback method in peptideLine mode. 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @note: Placeholder for now
        """
        return 'Ladder'
    
    def isRubberbandLineSnapEnabled(self):
        """
        This returns True or False based on the checkbox state in the PM.

        This is used as a callback method in CntLine mode (NanotubeLine_GM)
        @see: NanotubeLine_GM.snapLineEndPoint where the boolean value returned from
              this method is used
        @return: Checked state of the linesnapCheckBox in the PM
        @rtype: boolean
        @note: placeholder for now
        """
        return True
        