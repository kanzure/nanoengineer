
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Encapsulates all the particulars of a simulation.
The L{SimSpecification} class is essentially a hierarchical parameter set that
describes a cross-package compatible simulation specification.
All reusable configuration is captured here including motion paths
and jigs.

The object model makes use of
L{Parameter} objects to store most of the data. Parameter objects encapsulate
information necessary for viewing and editing single parameters via some GUI.
Parameter objects are instantiated via a ParameterFactory based on a given key
which maps to a unique parameter in the SimSpecification keyname-space. See
L{Parameter.ParameterFactory} for a description of the reserved keynames.

The following is the object model of the SimSpecification module:
IMAGE_1

The following is an example SimSpecification as it would appear in XML::
	<simSpecification name="Dual-H abstraction">
	  <description>
	    Abstraction of two hydrogens from the DC10 deposition tooltip.
	  </description>

	  <parameter key="timestep"               value="0.1e-15" />
	  <parameter key="startStep"              value="0" />
	  <parameter key="maxSteps"               value="10000" />
	  <parameter key="stepsPerFrame"          value="10" />
	  <parameter key="environmentTemperature" value="300.0" />
	  <parameter key="environmentPressure"    value="100000.0" />

	  <input name="abstractor">
	    <parameter key="file" value="abstractor.mmp" />
	  </input>
	  <input name="seed">
	    <parameter key="file" value="diamond-fragment.mmp" />
	  </input>

	  <motionPath name="MotionPath1">
	    <interval>
	      <parameter key="start" value="0.0" />
	      <parameter key="end"   value="180.0e-15" />
	      <velocity>
	        <parameter key="fixed" value="true" />
	      </velocity>
	    </interval>
	    <interval>
	      <parameter key="start" value="180e-15" />
	      <parameter key="end"   value="2345e-15" />
	      <linearforce>
	        <parameter key="speed"         value="200.0" />
	        <parameter key="componentsXYZ" value="0.0 -5.0e-9 0.0" />
	      </linearforce>
	    </interval>
	  </motionPath>

	  <motionPath name="Anchor1">
	    <interval>
	      <parameter name="start" value="0.0" />
	      <parameter name="end"   value="3300.0e-15" />
	      <velocity>
	        <parameter key="fixed" value="true" />
	      </velocity>
	    </interval>
	  </motionPath>

	  <operation name="Force Field/Quantum Chemistry">
	    <parameter key="action" value="dynamics" />
		
	    <method name="ND-1">
	      <parameter key="engine"                 value="NanoDynamics-1" />
	      <parameter key="atomSet"                value="BulkAtomSet1" />
	    </method>

	    <method name="GAMESS">
	      <parameter key="engine"                 value="GAMESS" />
	      <parameter key="atomSet"                value="Tooltip1" />
	      <parameter key="method"                 value="Hartree-Fock" />
	      <parameter key="basisSet"               value="3-21G" />
	      <parameter key="functional"             value="" />
	      <parameter key="multiplicity"           value="auto" />
	      <parameter key="integrator"             value="coarse" />
	      <parameter key="energyAccuracty"        value="1.0e-5" />
	      <parameter key="maxConvergenceAttempts" value="10" />
	      <parameter key="unscripted"             value="no" />
	      <parameter key="applyFrom"              value="0.0" />
	      <parameter key="applyTo"                value="20.0e-12" />
	    </method>

	    <constraint>
	      <parameter key="motion"  value="MotionPath1" />
	      <parameter key="atomSet" value="DC10" />
	    </constraint>
	    <constraint>
	      <parameter key="motion"  value="Anchor1" />
	      <parameter key="atomSet" value="H-abstractor" />
	    </constraint>

	    <measurement>
	      <parameter key="measure" value="Thermo1" />
	      <parameter key="atomSet" value="H-abstractor" />
	    </measurement>
	  </operation>

	  <preSimulationChecks>
	    <parameter key="all" value="false" />
	    <parameter key="detectUnMinimized" value="true" />
	    <parameter key="checkJigSanity" value="true" />
	    <parameter key="detectUnusedJigs" value="false" />
	    <parameter key="detectReactionPoints" value="true" />
	    <parameter key="checkSpinMultiplicity" value="true" />
	  </preSimulationChecks>
	</simSpecification>

Packages may add their own custom parameters and they will be stored along
with the reserved-key parameters. Custom parameters can be specified with
the information necessary for viewing and editing them via some GUI. Here
is what a fully defined parameter would look like in XML::
	<parameter key="simFlowScript" value="/Users/bh/tooltip_action.tcl">
	  <label>Workflow script</label>
	  <widget>filechooser</widget>
		<extension>.tcl</extension>
	  <tooltip>Simulation workflow script file</tooltip>
	</parameter>
"""

from Parameter import ParameterSet

class SimInput(ParameterSet):
	"""Simulation input files. See L{SimSpecification} for context."""
	
	
	def __init__(self, name):
		"""Constructs a SimInput with the given name."""
		groupName = "Input files"
		
		
	def getName(self):
		"""Returns this SimInput's name."""
		pass
	def setName(self, name):
		"""Sets this SimInput's name."""
		pass


class Action(ParameterSet):
	"""
	An external effect applied to a set of atoms.
	See L{SimSpecification} for context.
	
	This is an abstract/interface class and should not be instantiated.
	"""
	pass


class Velocity(Action):
	"""
	A fixed velocity applied to a set of atoms.
	See L{SimSpecification} for context.
	"""
	
	
	def __init__(self):
		"""Constructs a Velocity object."""
		groupName = "Velocity"


class LinearForce(Action):
	"""
	A force applied to a set of atoms.
	See L{SimSpecification} for context.
	"""
	
	
	def __init__(self):
		"""Constructs a LinearForce object."""
		groupName = "Linear force"


class Torque(Action):
	"""
	A rotary force applied to a set of atoms.
	See L{SimSpecification} for context.
	"""
	
	
	def __init__(self):
		"""Constructs a Torque object."""
		groupName = "Torque"
	

class Interval(ParameterSet):
	"""
	A span of time and associated Action.
	See L{SimSpecification} for context.
	"""
	
	
	def __init__(self):
		"""Constructs an Interval object."""
		groupName = "Interval"
	
	
	def getAction(self):
		"""Returns the Action subclass for this interval."""
		pass
	def setAction(self, Action):
		"""
		Sets the Action subclass for this interval. Clobbers any existing
		Action.
		"""
		pass


class MotionPath(ParameterSet):
	"""
	A description of motion during simulation.
	See L{SimSpecification} for context.
	"""
	
	
	def __init__(self, name):
		"""Constructs a MotionPath with the given name."""
		groupName = "Motion path"
		
		
	def getName(self):
		"""Returns this MotionPath's name."""
		pass
	def setName(self, name):
		"""Sets this MotionPath's name."""
		pass
	
	
	def getIntervalArray(self):
		"""Returns this MotionPath's Interval as an array."""
		pass
	def addInterval(self, interval):
		"""Adds the given Interval and returns an Interval index."""
		pass
	def deleteInterval(self, intervalIndex):
		"""Deletes the Interval with the given index from this MotionPath."""
		pass


class Method(ParameterSet):
	"""A simulation scheme. See L{SimSpecification} for context."""
	
	
	def __init__(self):
		"""Constructs a Method object."""
		groupName = "Method"


class Constraint(ParameterSet):
	"""Application of a Motion path on an atom set."""
	
	
	def __init__(self):
		"""Constructs a Constraint object."""
		groupName = "Constraint"


class Measurement(ParameterSet):
	"""Application of a Measure on an atom set."""
	
	
	def __init__(self):
		"""Constructs a Measurement object."""
		groupName = "Measurement"


class Operation(ParameterSet):
	"""Describes the components of the actual simulation process."""
	
	
	def __init__(self):
		"""Constructs an Operation object."""
		groupName = "Operation"
	
		
class SimSpecification(ParameterSet):
	"""
	Encapsulates all the particulars of a simulation such as input files,
	entity traversal, level of theory, calculation, motion, and results.
	"""


	def __init__(self, name):
		"""Constructs a SimSpecification with the given name."""
		groupName = "Simulation specification"
		
		
	def loadFromFile(self, filepath):
		"""
		Loads this SimSpecification from the given filepath.
		@return: (0=successful or non-zero error code), (error description)
		"""
		pass
	
	
	def writeToFile(self, filepath):
		"""
		Writes this SimSpecification to the given filepath.
		@return: (0=successful or non-zero error code), (error description)
		"""
		pass
	
	
	def getName(self):
		"""Returns this SimSpecification's name."""
		pass
	def setName(self, name):
		"""Sets this SimSpecification's name."""
		pass
	
	
	def getDescription(self):
		"""Returns this SimSpecification's description."""
		pass
	def setDescription(self):
		"""Sets this SimSpecification's description."""
		pass
	
	
	def getParameter(self, key):
		"""
		Returns the Parameter with the given key. A blank Parameter is returned
		if no Parameter with the given key has been set.
		"""
		pass
	def getParameterArray(self):
		"""Returns this object's Parameters in an array."""
		pass
	def setParameter(self, Parameter):
		"""
		Sets the given parameter. Any existing Parameter with the same key will
		be clobbered.
		"""
		pass
	
	
	def getSimInputArray(self):
		"""Returns this SimSpecification's SimInputs in an array."""
		pass
	def addSimInput(self, Input):
		"""
		Adds the given SimInput. Any existing SimInput with the same
		name will be clobbered.
		"""
		pass
	
	
	def getMotionPathArray(self):
		"""Returns this SimSpecification's MotionPaths in an array."""
		pass
	def addMotionPath(self, MotionPath):
		"""
		Adds the given MotionPath. Any existing MotionPath with the same
		name will be clobbered.
		"""
		pass
	
	
	def getOperation(self):
		"""Returns this SimSpecification's Operation."""
		pass
	def setOperation(self, Operation):
		"""
		Sets the given Operation. Any existing Operation will be clobbered.
		"""
		pass
	
	
	def getPreSimulationChecks(self):
		"""
		Returns this SimSpecification's pre-simulation check Parameters in an
		array.
		"""
		pass
	def addPreSimulationCheck(self, Parameter):
		"""
		Adds the given pre-simulation check Parameter. Any existing pre-check
		with the same key will be clobbered.
		"""
		pass
