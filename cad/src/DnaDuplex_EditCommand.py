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
from EditCommand import EditCommand



from dna_model.DnaSegment import DnaSegment


from utilities.Log  import redmsg, greenmsg
from VQT            import V, Veq, vlen
from DnaDuplex      import B_Dna_PAM3
from DnaDuplex      import B_Dna_PAM5

from GeneratorBaseClass import  PluginBug, UserError
from DnaDuplexPropertyManager import DnaDuplexPropertyManager

from constants import gensym


from Dna_Constants import getNumberOfBasePairsFromDuplexLength, getDuplexRise
from Dna_Constants import getDuplexLength


from DnaLineMode import DnaLine_GM


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
    prefix           =  'Segment-'   # used for gensym
    cmdname          = "Duplex"
    commandName       = 'DNA_DUPLEX'
    featurename       = 'Build Dna Duplex'
   
    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False
    
    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    #Graphics Mode set to DnaLine graphics mode
    GraphicsMode_class = DnaLine_GM
    
    #required by DnaLine_GM
    mouseClickPoints = []
    #This is the callback method that the previous command 
    #(which is BuildDna_Editcommand as of 2008-01-11) provides. When user exits
    #this command and returns back to the previous one (BuildDna_EditCommand),
    #it calls this method and provides a list of segments created while this 
    #command was  running (self._segmentList). 
    callback_addSegments  = None
    
    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None
    
    _segmentList = []

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for DnaDuplex_EditCommand
        """
        EditCommand.__init__(self, commandSequencer)
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
        EditCommand.init_gui(self)        
        
        
        if isinstance(self.graphicsMode, DnaLine_GM):
            self._setParamsForDnaLineGraphicsMode()
            self.mouseClickPoints = []
            
        prevMode = self.commandSequencer.prevMode 
        if prevMode.commandName == 'BUILD_DNA':
            params = prevMode.provideParamsForTemporaryMode(self.commandName)
            self.callback_addSegments = params
            
            #Following won't be necessary after Command Toolbar is 
            #properly integrated into the Command/CommandSequencer API
            try:
                self.flyoutToolbar = prevMode.flyoutToolbar
            except AttributeError:
                self.flyoutToolbar = None
            
            
            if self.flyoutToolbar:
                if not self.flyoutToolbar.dnaDuplexAction.isChecked():
                    self.flyoutToolbar.dnaDuplexAction.setChecked(True)
                
        
        self._segmentList = []
                    

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. This includes closing 
        this mode's property manager, updating the command toolbar ,
        Note: The slot connection/disconnection in property manager and 
        command toolbar is handled in those classes.
        @see: L{self.init_gui}
        """
                    
        EditCommand.restore_gui(self)
        
        if isinstance(self.graphicsMode, DnaLine_GM):
            self.mouseClickPoints = []
     
        self.graphicsMode.resetVariables()
        
        #See BuildDna_EditCommand.callback_addSegments
        self.callback_addSegments(self._segmentList)
        
        if self.flyoutToolbar:
            self.flyoutToolbar.dnaDuplexAction.setChecked(False)
        
        self._segmentList = []
                
        
    
    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None     

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
        
        numberOfBasePairs = getNumberOfBasePairsFromDuplexLength('B-DNA', 
                                                                 duplexLength)
        
        self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)
        
        
        self.preview_or_finalize_structure(previewing = True)
        
        #Unpick the dna segments created earlier (while this command was still 
        #running. )
        for segment in self._segmentList:
            segment.unpick()
            
        #Select the newly created structure
        self.struct.pick()        
        
        #Now append the new structure in self._segmentList (this list of 
        #segments
        #will be provided to the previous command (BuildDna_EditCommand)
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
        propMgr = DnaDuplexPropertyManager(self.win, self)
        return propMgr


    def _createStructure(self):
        """
        creates and returns the structure (in this case a L{Group} object that 
        contains the DNA strand and axis chunks. 
        @return : group containing that contains the DNA strand and axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """
        return self._createSegment()


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
        EditCommand.cancelStructure(self)
        self._removeSegments()
    
    def _removeSegments(self):
        """
        Remove the segments in self._segmentList. This deletes all the segments
        created while this command was running
        @see: L{self.cancelStructure}
        """
        if self._segmentList:
            for segment in self._segmentList:   
                segment.kill()       
                self._revertNumber()
            
            self._segmentList = []
            self.win.win_update() 
    
    def _removeStructure(self):
        if self.struct in self._segmentList:
            self._segmentList.remove(self.struct)            
        EditCommand._removeStructure(self)
        

    def NOT_USED_acceptParamsFromTemporaryMode(self, commandName, params):
        """
        THIS METHOD IS NOT USED AS OF 2008-01-11 AND WILL BE REMOVED AFTER 
        MORE TESTING. 
        
        NOTE: This also needs to be a general API method. There are situations 
        when user enters a temporary mode , does somethoing there and 
        returns back to  the previous mode he was in. He also needs some data 
        that he gathered in that temporary mode so as to use it in the original 
        mode he was working on. Here is a good example: 
	-  User is working in selectMolsMode, Now he enters a temporary mode 
	called DnaLine mode, where, he clicks two points in the 3Dworkspace 
	and expects to create a DNA using the points he clicked as endpoints. 
	Internally, the program returns to the previous mode after two clicks. 
	The temporary mode sends this information to the method defined in 
	the previous mode called acceptParamsFromTemporaryMode and then the
	previous mode (selectMolsMode) can use it further to create a dna 
	@see: DnaLineMode
	@see: selectMolsMode.acceptParamsFromTemporaryMode where this is called
	TODO: 
	- This needs to be a more general method in mode API. 
	- Right now it is used only for creating a DNA line. It is assumed
	 that the DNADuplexEditCommand is invoked while in selectMolsMode. 
	 If we decide to define a new DnaMode, then this method needs to go 
	 there. 
	 - Even better if the commandSequencer API starts supporting 
	 commandSequencer.previousCommand (like it does for previous mode) 
	 where, the previousCommand can be an editCommand or mode, then 
	 it would be good to define this API method in that mode or 
	 editCommand class  itself.  So, this method will be directly called 
         by the temporary mode (instead of calling a method in mode which in 
         turn calls this method         
	 -- [Ninad 2007-10-25 comment]	

        """
        if len(params) < 2:
            return
        self.propMgr.endPoint1 = params[0]
        self.propMgr.endPoint2 = params[1]
        duplexLength = vlen(params[0] - params[1])
        
        numberOfBasePairs = getNumberOfBasePairsFromDuplexLength('B-DNA', 
                                                                 duplexLength)
        
        self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)
        self.propMgr.specifyDnaLineButton.setChecked(False)
        self.preview_or_finalize_structure(previewing = True)
    

    def _createSegment(self):
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
                     endPoint1, \
                     endPoint2 = params
        
        #If user enters the number of basepairs and hits preview i.e. endPoint1
        #and endPoint2 are not entered by the user and thus have default value 
        #of V(0, 0, 0), then enter the endPoint1 as V(0, 0, 0) and compute
        #endPoint2 using the duplex length. 
        #Do not use '==' equality check on vectors! its a bug. Use same_vals 
        # or Veq instead. 
        if Veq(endPoint1 , endPoint2) and Veq(endPoint1, V(0, 0, 0)):
            endPoint2 = endPoint1 + \
                      self.win.glpane.right*getDuplexLength('B-DNA', 
                                                            numberOfBases)
            

        if numberOfBases < 1:
            msg = redmsg("Cannot to preview/insert a DNA duplex with 0 bases.")
            self.propMgr.updateMessage(msg)
            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None

        if dnaForm == 'B-DNA':
            if dnaModel == 'PAM-3':
                dna = B_Dna_PAM3()
            elif dnaModel == 'PAM-5':
                dna = B_Dna_PAM5()
            else:
                print "bug: unknown dnaModel type: ", dnaModel
        else:
            raise PluginBug("Unsupported DNA Form: " + dnaForm)

        self.dna  =  dna  # needed for done msg

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
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()
        if 1:
            dnaSegment = DnaSegment(self.name, 
                         self.win.assy,
                         self.win.assy.part.topnode,
                         editCommand = self  )
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis
            dna.make(dnaSegment, 
                     numberOfBases, 
                     basesPerTurn, 
                     endPoint1,
                     endPoint2)
        

            return dnaSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            dnaSegment.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")

        
    
    def provideParamsForTemporaryMode(self, temporaryModeName):
        """
        NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs to send some data from 
	previous mode to the temporary mode .	 
	@see: B{DnaLineMode}
	@see: self.acceptParamsFromTemporaryMode 
        """
        assert temporaryModeName == 'DNA_LINE_MODE'
        
        mouseClickLimit = None
        duplexRise =  getDuplexRise('B-DNA')
        jigList = self.win.assy.getSelectedJigs()
 
        callback_cursorText = self.getCursorTextForTemporaryMode
        callback_snapEnabled = self.isRubberbandLineSnapEnabled
        callback_rubberbandLineDisplay = self.getDisplayStyleForRubberbandLine
        return (mouseClickLimit, 
                duplexRise, 
                callback_cursorText, 
                callback_snapEnabled, 
                callback_rubberbandLineDisplay )
    
    def getCursorTextForTemporaryMode(self, endPoint1, endPoint2):
        """
        This is used as a callback method in DnaLine mode 
        @see: DnaLineMode.setParams, DnaLineMode_GM.Draw
        """
        duplexLength = vlen(endPoint2 - endPoint1)
        numberOfBasePairs = getNumberOfBasePairsFromDuplexLength('B-DNA', 
                                                                 duplexLength)
        duplexLengthString = str(round(duplexLength, 3))
        text =  str(numberOfBasePairs)+ "b, "+ duplexLengthString 
        
        #@TODO: The following updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString -- Ninad 2007-12-20
        self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)
        
        return text 
    
    
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
        self.duplexRise =  getDuplexRise('B-DNA')
        self.jigList = self.win.assy.getSelectedJigs()
 
        self.callbackMethodForCursorTextString = \
            self.getCursorTextForTemporaryMode
        
        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled
        
        self.callback_rubberbandLineDisplay = \
            self.getDisplayStyleForRubberbandLine

       
        
            
