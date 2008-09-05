# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
LinearMotor_EditCommand.py

@author: Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
ninad 2007-10-09: Created.
"""

import foundation.env as env
from utilities.Log   import redmsg, greenmsg, orangemsg
from model.jigs_motors import LinearMotor
from operations.jigmakers_Mixin import atom_limit_exceeded_and_confirmed
from command_support.EditCommand import EditCommand

from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from commands.LinearMotorProperties.LinearMotorPropertyManager import LinearMotorPropertyManager

class LinearMotor_EditCommand(EditCommand):
    """
    The LinearMotor_EditCommand class  provides an editCommand Object.
    The editCommand, depending on what client code needs it to do, may create
    a new linear motor or it may be used for an existing linear motor. 
    """
    
    PM_class = LinearMotorPropertyManager
    
    cmd = greenmsg("Linear Motor: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it from the prefix.
    create_name_from_prefix = False 
    propMgr = None

    #See Command.anyCommand for details about the following flags
    command_should_resume_prevMode = True
    command_has_its_own_PM = True
    
    commandName = 'LINEAR_MOTOR'
    featurename = "Linear Motor"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC

    GraphicsMode_class = SelectAtoms_GraphicsMode    

    def __init__(self, commandSequencer, struct = None):
        """
        Constructs an Edit Controller Object. The editCommand, 
        depending on what client code needs it to do, may create a new 
        Linear motor or it may be used for an existing linear motor. 

        @param win: The NE1 main window.
        @type  win: QMainWindow

        @param struct: The model object (in this case a 'linear motor') that the
                       this EditCommand may create and/or edit
                       If struct object is specified, it means this 
                       editCommand will be used to edit that struct. 
        @type  struct: L{LinearMotor} or None

        @see: L{LinearMotor.__init__}
        """ 
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct

    def Enter(self):
        """
        Enter this command. 
        @see: EditCommand.Enter
        """
        #See EditCommand.Enter for a detailed comment on why self.struct is 
        #set to None while entering this command.
        #May not be needed for RotaryMotor and Linear motor edit commands, 
        # but safe to do it for now -- Ninad 2008-01-14
        if self.struct:
            self.struct = None

        EditCommand.Enter(self)

    def init_gui(self):
        """
        NOT IMPLEMENTED YET.
        TODO: Move calls that create/ show PM  in editCommand.createStructure
              out of that method. (That code was written before converting the 
              editCommands into 'Commands'. After this conversion, a better 
              implementation is necessary, in which PM creation and 
              display will be handled  in init_gui method.
        """
        #Note: This method overrides EditCommand.init_gui. This is just to 
        #prevent the call of self.create_and_or_show_PM_if_wanted. , As that 
        # method is called in self.createStructure. (to be cleaned up)
        pass 

    def restore_gui(self):
        """
        """
        if self.propMgr:
            self.propMgr.close()

    def _gatherParameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        force = self.propMgr.forceDblSpinBox.value()
        stiffness = self.propMgr.stiffnessDblSpinBox.value()
        enable_minimize_state = self.propMgr.enableMinimizeCheckBox.isChecked()
        color = self.struct.color      
        atoms = self.win.assy.selatoms_list()

        return (force, 
                stiffness, 
                enable_minimize_state, 
                color, 
                atoms)

    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return LinearMotor


    def _createStructure(self):
        """
        Create a Plane object. (The model object which this edit controller 
        creates) 
        """
        assert not self.struct       

        atoms = self.win.assy.selatoms_list()

        atomNumberRequirementMet, logMessage = \
                                self._checkMotorAtomLimits(len(atoms))

        if atomNumberRequirementMet:
            self.win.assy.part.ensure_toplevel_group()
            motor = LinearMotor(self.win.assy)
            motor.findCenterAndAxis(atoms, self.win.glpane)
            self.win.assy.place_new_jig(motor)
        else:
            motor = None
            env.history.message(redmsg(logMessage))

        return motor

    def _modifyStructure(self, params):
        """
        Modifies the structure (Plane) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Plane created using this Plane_EditCommand) 
        @type  params: tuple
        """
        assert self.struct
        assert params 
        assert len(params) == 5             

        force, stiffness, enable_minimize_state, \
             color, atoms = params

        numberOfAtoms = len(atoms)

        atomNumberRequirementMet, logMessage = \
                                self._checkMotorAtomLimits(numberOfAtoms)

        if not atomNumberRequirementMet:
            atoms = self.struct.atoms[:]
            logMessage = logMessage + " Motor will remain attached to the"\
                       " atoms listed in the <b>Attached Atoms</b> list in"\
                       " this property manager"
            logMessage = orangemsg(logMessage)            
            self.propMgr.updateMessage(logMessage)
            assert len(atoms) > 0

        self.struct.cancelled = False
        self.struct.force = force
        self.struct.stiffness = stiffness
        self.struct.enable_minimize = enable_minimize_state
        self.struct.color = color
        #Not sure if it is safe to do self.struct.atoms = atoms
        #Instead using 'setShaft method -- ninad 2007-10-09
        self.struct.setShaft(atoms)

        self.struct.findCenterAndAxis(atoms, self.win.glpane)

        self.propMgr.updateAttachedAtomListWidget(atomList = atoms)

        self.win.win_update() # Update model tree
        self.win.assy.changed()     

    
    ##=====================================##

    def _checkMotorAtomLimits(self, numberOfAtoms):
        """
        """
        logMessage = ""
        isAtomRequirementMet = True


        if numberOfAtoms == 0:
            logMessage = "No Atoms selected to create a Linear Motor. " 
            isAtomRequirementMet = False
            return (isAtomRequirementMet, logMessage)        

        if numberOfAtoms >= 2 and numberOfAtoms < 200:
            isAtomRequirementMet = True
            logMessage = ""
            return (isAtomRequirementMet, logMessage)

        # Print warning if over 200 atoms are selected.
        # The warning should be displayed in a MessageGroupBox. Mark 2007-05-28        
        if numberOfAtoms > 200:
            if not atom_limit_exceeded_and_confirmed(self.win, 
                                                     numberOfAtoms, 
                                                     limit = 200):
                logMessage = "Warning: Motor is attached to more than 200 "\
                           "atoms. This may result in a performance degradation"
                isAtomRequirementMet = True
            else:
                logMessage = "%s creation cancelled" % (self.cmdname)
                isAtomRequirementMet = False

            return (isAtomRequirementMet, logMessage)

        return (isAtomRequirementMet, logMessage)



