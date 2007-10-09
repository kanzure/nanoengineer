# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
LinearMotorEditcontroller.py

@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 2007-10-09: Created.
"""

import env
from utilities.Log import redmsg, greenmsg, orangemsg
from jigs_motors import LinearMotor
from jigs import atom_limit_exceeded_and_confirmed

from EditController import EditController
from LinearMotorPropertyManager import LinearMotorPropertyManager

class LinearMotorEditController(EditController):
    """
    The LinearMotorEditController class  provides an editController Object.
    The editController, depending on what client code needs it to do, may create
    a new linear motor or it may be used for an existing linear motor. 
    """
    cmd = greenmsg("Linear Motor: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it from the prefix.
    create_name_from_prefix = False 
    sponsor_keyword = 'Linear Motor'
    propMgr = None
    
    def __init__(self, win, struct = None):
        """
        Constructs an Edit Controller Object. The editController, 
        depending on what client code needs it to do, may create a new 
        Linear motor or it may be used for an existing linear motor. 
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param struct: The model object (in this case a 'linear motor') that the
                       this EditController may create and/or edit
                       If struct object is specified, it means this 
                       editController will be used to edit that struct. 
        @type  struct: L{LinearMotor} or None
        
        @see: L{LinearMotor.__init__}
        """ 
        EditController.__init__(self, win)
        self.struct = struct
    
    def _gatherParameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        torque = self.propMgr.torqueDblSpinBox.value()
        initial_speed = self.propMgr.initialSpeedDblSpinBox.value()
        final_speed = self.propMgr.finalSpeedDblSpinBox.value()
        dampers_state = self.propMgr.dampersCheckBox.isChecked()
        enable_minimize_state = self.propMgr.enableMinimizeCheckBox.isChecked()
        color = self.struct.color      
        atoms = self.win.assy.selatoms_list()
                    
                  
        return (torque, 
                initial_speed, 
                final_speed, 
                dampers_state, 
                enable_minimize_state, 
                color, 
                atoms)
    
    def _createStructure(self, params = None):
        """
        Create a Plane object. (The model object which this edit controller 
        creates) 
        """
        assert not self.struct       
        
        atoms = self.win.assy.selatoms_list()
        
        atomNumberRequirementMet, logMessage = \
                                  self._checkMotorAtomLimits(len(atoms))
        
        if atomNumberRequirementMet:
            motor = LinearMotor(self.win.assy)
            motor.findCenterAndAxis(atoms, self.win.glpane)
                
        return motor
  
    def _modifyStructure(self, params):
        """
        Modifies the structure (Plane) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Plane created using this PlaneEditController) 
        @type  params: tuple
        """
        assert self.struct
        assert params 
        assert len(params) == 7             
        
        torque, initial_speed, final_speed, \
        dampers_state, enable_minimize_state, \
        color, atoms  = params
        
        atoms = self.win.assy.selatoms_list()
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
        self.struct.torque = torque
        self.struct.initial_speed = initial_speed
        self.struct.speed = final_speed
        self.struct.dampers_enabled = dampers_state
        self.struct.enable_minimize = enable_minimize_state
        self.struct.color = color
        #Not sure if it is safe to do self.struct.atoms = atoms
        #Instead using 'setShaft method -- ninad 2007-10-09
        self.struct.setShaft(atoms)
        
        
        self.struct.findCenterAndAxis(atoms, self.win.glpane)
        
        attachedAtomNames = []
        for atm in atoms:            
            attachedAtomNames.append(str(atm))
            
        self.propMgr.selectedAtomsListWidget.insertItems(row = 0, 
                                                         items = attachedAtomNames)
        
        self.win.win_update() # Update model tree
        self.win.assy.changed()     
    
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editController. 
        """
        assert not self.propMgr
        
        propMgr = LinearMotorPropertyManager(self.win, self)
        
        return propMgr
    ##=====================================##
    
    def _checkMotorAtomLimits(self, numberOfAtoms):
        """
        """
        logMessage = ""
        isAtomRequirementMet = False
        
        if numberOfAtoms == 0:
            logMessage = "Warning: No Atoms are selected"
            isAtomRequirementMet = False
            return (isAtomRequirementMet, logMessage) 
        
        # wware 051216, bug 1114, need >= 2 atoms for rotary motor
        if numberOfAtoms < 2:
            msg = redmsg("You must select at least two atoms to create"\
                         " a Rotary Motor.")
            env.history.message(self.cmd + msg)
            logMessage = msg
            isAtomRequirementMet = False
            return (isAtomRequirementMet, logMessage)
            
        # Print warning if over 200 atoms are selected.
        # The warning should be displayed in a MessageGroupBox. Mark 2007-05-28
        if atom_limit_exceeded_and_confirmed(self.win, 
                                             numberOfAtoms, 
                                             limit = 200):
            logMessage = "Warning: Motor is attached to more than 200 atoms. "\
                       "This may result in a performance degradation"
            isAtomRequirementMet = True
            return (isAtomRequirementMet, logMessage)
        
        if numberOfAtoms > 2 and numberOfAtoms < 200:
            isAtomRequirementMet = True
            logMessage = ""
            return (isAtomRequirementMet, logMessage)
        
    