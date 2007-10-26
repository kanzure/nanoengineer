# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Mark Sims, Ninad Sathaye
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2007-10-24:
Created. Rewrote almost everything to implement EdiController as a superclass 
thereby deprecating the DnaDuplexGenerator class.

TODO: 
- Need to cleanup docstrings. 
- Methods such as createStructure do nothing. Need to clean this up a bit in 
  this class and in the EditController superclass
- Method editStructure is not implemented. It will be implemented after 
  the DNA object model gets implemented. 
"""
from EditController import EditController

from Utility        import Group
from utilities.Log  import redmsg, greenmsg
from VQT            import Veq, vlen
from DnaDuplex      import B_Dna_PAM3

from GeneratorBaseClass import CadBug, PluginBug, UserError
from DnaDuplexPropertyManager import DnaDuplexPropertyManager

from constants import gensym

from Dna_Constants import getNumberOfBasesFromDuplexLength

class DnaDuplexEditController(EditController):
    """
    DnaDuplexEditController that provides an editController object for 
    generating DNA Duplex 
    """
    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'DNA-'   # used for gensym
    cmdname          = "Duplex"

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    def __init__(self, win, struct = None):
        """
        Contructor for DnaDuplexEditController
        """
        EditController.__init__(self, win)
        self.struct = struct
        

    def runController(self):
        """
        Overrides EditController.runController
        """
        self.create_and_or_show_PM_if_wanted(showPropMgr = True)  
        
    def create_and_or_show_PM_if_wanted(self, showPropMgr = True):
        """
        Create the property manager object if one doesn't already exist 
        and then show the propMgr if wanted by the user. 
        @param showPropMgr: If True, show the property manager 
        @type showPropMgr: boolean
        """
        EditController.create_and_or_show_PM_if_wanted(
            self,
            showPropMgr = showPropMgr)
        
        self.propMgr.updateMessage("Create a DNA by specifying two endpoints " \
                                   "of a line. <br>"\
                                   "Activate the <b> Specify EndPoints </b>"
                                   "button and then specify the two endpoints" \
                                   " from the 3D workspace"
                                   )
        
    def createStructure(self, showPropMgr = True):
        """
        Overrides superclass method. It doesn't do anything for this type
        of editcontroller
        """
        pass

    def ZeditStructure(self):
        """
        Overrides superclass method. It doesn't do anything for this type
        of editcontroller
        """
        pass

    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editController. 
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

        params = self._gatherParameters()

        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        numberOfBases, \
                     dnaForm, \
                     basesPerTurn, \
                     endPoint1, \
                     endPoint2 = params

        if Veq(endPoint1, endPoint2):
            raise CadBug("DNA endpoints cannot be the same point.")

        if numberOfBases < 1:
            msg = redmsg("Cannot to preview/insert a DNA duplex with 0 bases.")
            self.propMgr.updateMessage(msg)
            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None

        if dnaForm == 'B-DNA':
            dna = B_Dna_PAM3()
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
        dnaGroup = Group(self.name, 
                         self.win.assy,
                         self.win.assy.part.topnode,
                         editController = self
                     )
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis
            dna.make(dnaGroup, 
                     numberOfBases, 
                     basesPerTurn, 
                     endPoint1,
                     endPoint2)

            self.win.assy.place_new_geometry(dnaGroup)
            # TODO: Decide whether recentering the view after creating the 
            # structure is needed. 
            ##self.win.glpane.setViewRecenter(fast = True)

            return dnaGroup

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            rawDnaGroup.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")


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
        Overrides EditController._modifystructure. This method removes the old 
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
            
        #@NOTE: Unlike editcontrollers such as PlaneEditController, this 
        #editcontroller actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the DNA object model 
        # will solve this problem. (i.e. reusing the object and just modifying
        #its attributes.  Till that time, we'll continue to use 
        #what the old GeneratorBaseClass use to do ..i.e. remove the item and 
        # create a new one  -- Ninad 2007-10-24
        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
        return 

    def acceptParamsFromTemporaryMode(self, params):
        """
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
	 that the DNADuplxEditController is invoked while in selectMolsMode. 
	 If we decide to define a new DnaMode, then this method needs to go 
	 there. 
	 - Even better if the commandSequencer API starts supporting 
	 sommandSequencer.previousCommand (like it does for previous mode) 
	 where, the previousCommand can be an editController or mode, then 
	 it would be good to define this API method in that mode or 
	 editcontroller class  itself.  So, this method will be directly called 
         by the temporary mode (instead of calling a method in mode which in 
         turn calls this method         
	 -- [Ninad 2007-10-25 comment]	

        """
        self.propMgr.endPoint1 = params[0]
        self.propMgr.endPoint2 = params[1]
        duplexLength = vlen(params[0] - params[1])
        numberOfBases = getNumberOfBasesFromDuplexLength('B-DNA', duplexLength)
        self.propMgr.numberOfBasesSpinBox.setValue(numberOfBases)
        self.propMgr.specifyDnaLineButton.setChecked(False)
        self.preview_or_finalize_structure(previewing = True)


    def enterDnaLineMode(self, isChecked = False):
        """
	Enter the DnaLineMode (a temporary mode). 
        Needs more documentation. 
        @see: self.acceptParamsFromTemporaryMode which documents an 
              example on how the temporary mode is used  and also for 
              remaining tasks.(what needs to hbe done further 
        """
        if isChecked:            	
            commandSequencer = self.win.commandSequencer
            currentCommand = commandSequencer.currentCommand

            if currentCommand.modename != "DNA_LINE_MODE":
                commandSequencer.userEnterTemporaryCommand(
                    'DNA_LINE_MODE')
                return


