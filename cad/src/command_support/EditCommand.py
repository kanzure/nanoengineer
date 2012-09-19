# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
EditCommand.py

@author: Bruce Smith, Mark Sims, Ninad Sathaye, Will Ware
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

- Originally created as 'GeometryGeneratorBaseClass'. It shared common code with
GeneratorBaseClass but had some extra features to support creation and edition
of a 'Plane' [June-Sept 2007]. It was split out of ReferenceGeometry.py
- Before 2007-12-28, Editcommand was known as 'EditController'


Ninad 2007-09-17: Code cleanup to split ui part out of this class.
Ninad 2007-10-05: Major changes. Refactored GeometryGeneratorBaseClass
                  and surrounding code. Also renamed GeometryGeneratorBaseClass
                  to EditCommand, similar changes in surrounding code
Ninad 2007-10-24: Changes to convert the old structure generators
                  such as DnaGenerator / DnaDuplexGenerator to use the
                  EditCommand class (and their PMs to use EditCommand_PM)
Ninad 2007-12-26: Converted editControllers into Commands on commandSequencer

TODO:
- Need to cleanup docstrings.
- In subclasses such as InsertDna_EditCommand, the method createStructure do
  nothing (user is not immediately creating a structure) .
  Need to clean this up a bit in this class and in the  surrounding code
- New subclass InsertDna_EditCommand adds the structure as a node in the MT
  in its _createStructure method. This should also be implemented for
  following sublasses:  Plane_EditCommand, LineEditCommand, motor
  editcommand classes.
"""

import foundation.changes as changes
from foundation.FeatureDescriptor import register_abstract_feature_class

from utilities.Comparison import same_vals

from utilities.constants import permit_gensym_to_reuse_name
from utilities.exception_classes import AbstractMethod

from commands.Select.Select_Command import Select_Command


_superclass = Select_Command
class EditCommand(Select_Command):
    """
    EditCommand class that provides a editCommand object.
    The client can call three public methods defined in this class to acheive
    various things.
    1. runCommand -- Used to run this editCommand . Depending upon the
       type of editCommand it is, it does various things. The most common
       thing it does is to create and show  a property manager (PM) The PM
       is used by the editCommand to define the UI for the model
       which this editCommand creates/edits.
       See InsertDna_EditCommand.runCommand for an example
    2. createStructure -- Used directly by the client when it already knows
       input parameters for the structure being generated. This facilitates
       imeediate preview of the model being created when you execute this
       command.
       See self.createStructure  which is the default implementation used
       by many subclasses such as RotaryMotor_EditCommand etc.
    3. editStructure -- Used directly by the client when it needs to edit
       an already created structure.
       See self.editStructure for details.

    TODO: NEED TO IMPROVE DOCSTRING FURTHER
    """
    # see definition details in GeneratorBaseClass;
    # most of these should be overridden by each specific subclass
    cmd      =  ""
    cmdname  =  ""
    _gensym_data_for_reusing_name = None
    commandName = 'EditCommand'
    featurename = "Undocumented Edit Command" # default wiki help featurename
    from utilities.constants import CL_ABSTRACT
    command_level = CL_ABSTRACT
    __abstract_command_class = True

    flyoutToolbar = None

    def __init__(self, commandSequencer):
        """
        Constructor for the class EditCommand.
        """
        self.win = commandSequencer.win
        self.previousParams       =  None
        self.old_props            =  None
        self.logMessage           = ''

        self.struct               =  None
        self.existingStructForEditing  =  False

        Select_Command.__init__(self, commandSequencer)
        return

    #=== START   NEW COMMAND API methods  ======================================



    def command_enter_misc_actions(self):
        pass

    def command_exit_misc_actions(self):
        pass


    def command_will_exit(self):
        """
        Overrides superclass method.
        @see: baseCommand.command_will_exit() for documentation
        """
        if self.commandSequencer.exit_is_forced:
            pass
        elif self.commandSequencer.exit_is_cancel:
            self.cancelStructure()
        else:
            self.preview_or_finalize_structure(previewing = False)

        _superclass.command_will_exit(self)

    def runCommand(self):
        """
        Used to run this editCommand . Depending upon the
        type of editCommand it is, it does various things. The most common
        thing it does is to create and show  a property manager (PM) The PM
        is used by the editCommand to define the UI for the model
        which this editCommand creates/edits.
        See InsertDna_EditCommand.runCommand for an example
        Default implementation, subclasses should override this method.
        NEED TO DOCUMENT THIS FURTHER ?
        """
        self.existingStructForEditing = False
        self.struct = None
        self.createStructure()

    def createStructure(self):
        """
        Default implementation of createStructure method.
        Might be overridden in  subclasses. Creates an instance (object)
        of the structure this editCommand wants to generate. This implements
        a topLevel command that the client can execute to create an object it
        wants.

        Example: If its a plane editCommand, this method will create an
                object of class Plane.

        @see: L{self.editStructure} (another top level command that facilitates
              editing an existing object (existing structure).
        """

        assert not self.struct

        self.struct = self._createStructure()

        if not self.hasValidStructure():
            return

        if self.struct:
            #When a structure is created first, set the self.previousParams
            #to the struture parameters. This makes sure that it doesn't
            # unnecessarily do self._modifyStructure in
            # self.preview_or_finalize_structure  -- Ninad 2007-10-11
            self.previousParams = self._gatherParameters()
            self.preview_or_finalize_structure(previewing = True)


    def editStructure(self, struct = None):
        """
        Default implementation of editStructure method. Might be overridden in
        subclasses. It facilitates editing an existing object
        (existing structure). This implements a topLevel command that the client
        can execute to edit an existing object(i.e. self.struct) that it wants.

        Example: If its a plane edit controller, this method will be used to
                edit an object of class Plane.

        This method also creates a propMgr objects if it doesn't exist and
        shows this property manager

        @see: L{self.createStructure} (another top level command that
              facilitates creation of a model object created by this
              editCommand
        @see: L{Plane.edit} and L{Plane_EditCommand._createPropMgrObject}
        """
        assert struct
        self.struct = struct
        self.existingStructForEditing = True
        self.old_props = self.struct.getProps()

    def hasValidStructure(self):
        """
        Tells the caller if this edit command has a valid structure.

        This is the default implementation, overridden by the subclasses.

        Default implementation:
        This method checks for a few common things and by default, in the end
        returns True. A subclass can first call this superclass method,
        return False if superclass does so, if superclass returns True
        the subclass can then check the additional things

        @see: DnaSegment_EditCommand.hasValidStructure()
        """
        if self.struct is None:
            return False

        structType = self._getStructureType()

        if not isinstance(self.struct, structType):
            return False

        #The following can happen.
        if hasattr(self.struct, 'killed') and self.struct.killed():
            return False

        #Retrn True otherwise. Its now subclass's job to check additional things
        return True

    def _getStructureType(self):
        """
        Subclasses must override this method to define their own structure type.
        Returns the type of the structure this editCommand supports.
        This is used in isinstance test.
        @see: self.hasValidStructure()
        """
        print "bug: EditCommand._getStructureType not overridden in a subclass"
        raise AbstractMethod()


    def _createStructure(self):
        """
        Create the model object which this edit controller  creates)
        Abstract method.
        @see: L{Plane_EditCommand._createStructure}
        """
        raise AbstractMethod()


    def _modifyStructure(self, params):
        """
        Abstract method that modifies the current object being edited.
        @param params: The parameters used as an input to modify the structure
                       (object created using this editCommand)
        @type  params: tuple
        @see: L{Plane_EditCommand._modifyStructure}
        """
        raise AbstractMethod()

    def _gatherParameters(self):
        """
        Abstract method to be overridden by subclasses to return all
        the parameters needed to modify or (re)create the current structure.
        """
        raise AbstractMethod()

    def preview_or_finalize_structure(self, previewing = False):
        """
        Preview or finalize the structure based on the the previewing flag
        @param previewing: If true, the structure will use different cosmetic
                           properties.
        @type  previewing: boolean
        """

        if previewing:
            self._previewStructure()
        else:
            self._finalizeStructure()

        return

    def _previewStructure(self):
        """
        Preview the structure and update the previous parameters attr
        (self.previousParams)
        @see: self.preview_or_finalize_structure
        """

        #For certain edit commands, it is possible that self.struct is
        #not created. If so simply return (don't use assert self.struct)
        ##This is a commented out stub code for the edit controllers
        ##such as DNAEditCommand which take input from the user before
        ##creating the struct. TO BE REVISED -- Ninad20071009
        #The following code is now used.  Need to improve comments and
        # some refactoring -- Ninad 2007-10-24

        if not self.hasValidStructure():
            self.struct = self._createStructure()
            self.previousParams = self._gatherParameters()
            self.win.assy.changed()
            self.win.win_update()
            return

        self.win.assy.current_command_info(cmdname = self.cmdname)

        params = self._gatherParameters()

        if not same_vals( params, self.previousParams):
            self._modifyStructure(params)

        self.logMessage = str(self.cmd + "Previewing " + self.struct.name)
        self.previousParams = params
        self.win.assy.changed()
        self.win.win_update()


    def _finalizeStructure(self):
        """
        Finalize the structure. This is a step just before calling Done method.
        to exit out of this command. Subclasses may overide this method
        @see: EditCommand_PM.ok_btn_clicked
        @see: DnaSegment_EditCommand where this method is overridden.
        """
        if self.struct is None:
            return

        self.win.assy.current_command_info(cmdname = self.cmdname)

        params = self._gatherParameters()

        if not same_vals( params, self.previousParams):
            self._modifyStructure(params)

        if hasattr(self.struct, 'updateCosmeticProps'):
            self.struct.updateCosmeticProps()
            self.logMessage = str(self.cmd + "Created " + self.struct.name)

        #Do we need to set the self.previousParams even when the structure
        #is finalized? I think this is unnecessary but harmless to do.
        self.previousParams = params

        self.win.assy.changed()
        self.win.win_update()


    def cancelStructure(self):
        """
        Delete the old structure generated during preview if user modifies
        some parameters or hits cancel. Subclasses can override this method.
        @see: BuildDna_EditCommand.cancelStructure
        """
        if self.struct is None:
            return

        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        if self.existingStructForEditing:
            if self.old_props:
                self.struct.setProps(self.old_props)
                if hasattr(self.struct, 'updateCosmeticProps'):
                    self.struct.updateCosmeticProps()
                self.win.glpane.gl_update()
        else:
            self._removeStructure()

    def _removeStructure(self):
        """
        Remove this structure.
        @see: L{self.cancelStructure}
        """
        if self.struct is not None:
            self.struct.kill_with_contents()
            self.struct = None
            self._revertNumber()
            self.win.win_update()

    def _revertNumber(self):
        """
        Private method. Called internally when we discard the current structure
        and want to permit a number which was appended to its name to be reused.

        WARNING: the current implementation only works for classes which set
        self.create_name_from_prefix
        to cause our default _build_struct to set the private attr we use
        here, self._gensym_data_for_reusing_name, or which set it themselves
        in the same way (when they call gensym).

        This method is copied over from GeneratorBaseClass._revert_number
        """
        if self._gensym_data_for_reusing_name:
            prefix, name = self._gensym_data_for_reusing_name
                # this came from our own call of gensym, or from a caller's if
                # it decides to set that attr itself when it calls gensym
                # itself.
            permit_gensym_to_reuse_name(prefix, name)
        self._gensym_data_for_reusing_name = None
        return

    pass # end of class EditCommand

register_abstract_feature_class( EditCommand )
    # this is so "export command table" lists it as a separate kind of feature
    # [bruce 080905]

# end
