
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#ifndef NE1_SIMRESULTSDATASTORE_H
#define NE1_SIMRESULTSDATASTORE_H

#include <string>

#define SRDS_UNABLE_TO_OPEN_FILE			1
#define SRDS_UNABLE_TO_COMPLETE_OPERATION	2

namespace ne1 {


/* STRUCT: SimResultsBond
 *
 * A chemical bond. See SimResultsDataStore for context.
 */
typedef struct SimResultsBond {
	
	unsigned int atomId_1, atomId_2;
	float order;
} SimResultsbond;


/* CLASS: SimResultsDataStore
 *
 * Encapsulates a simulation results data store.
 *
 * <b>Atom Records Alignment</b>
 * The arrays of atom identifiers, positions, and velocities within a given
 * frame are aligned. So the contents at index X of all three arrays correspond
 * to the same atom.
 *
 * <b>Extension Data</b>
 * Extension data can be stored in each frame. Such data could be used to plot
 * graphs, for example. Extension data exists as named floating point numbers,
 * integers, floating point number arrays, and integer arrays inside a named
 * data-set.	
 */
class SimResultsDataStore {
  public:
	virtual ~SimResultsDataStore();

	/* METHOD: openDataStore */
	/**
	 * Opens the simulation results data store, found in the given directory,
	 * for read/write access.
	 *
	 * @param directory the directory where the simulation results files are
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int openDataStore(const char* directory, std::string& message) = 0;

	
	/*
	 * Name
	 */
	/** Returns the simulation name. */
	virtual std::string getName() const = 0;
	
	/** Sets the simulation name.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setName(const std::string& name, std::string& message) = 0;
	
	
	/*
	 * Description
	 */
	/** Returns the simulation description. */
	virtual std::string getDescription() const = 0;
	
	/** Sets the simulation description.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setDescription(const std::string& description,
							   std::string& message) = 0;

	/*
	 * Notes
	 */
	/** Returns the user's notes for these simulation results. */
	virtual std::string getNotes() const = 0;
	
	/** Sets the user's notes for these simulation results.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setNotes(const std::string& notes, std::string& message) = 0;
		
	
	/*
	def getTimestep(self):
		"""Returns the simulation timestep in seconds."""
		pass
	def setTimestep(self, timestep):
		"""
		Sets the simulation timestep.
		@param timestep: duration in seconds
		"""
		pass
	
	
	def getStartStep(self):
		"""Returns the simulation starting step number."""
		pass
	def setStartStep(self, startStep):
		"""Sets the simulation starting step number."""
		pass
	
	
	def getMaxSteps(self):
		"""Returns the maximum number of steps to simulate."""
		pass
	def setMaxSteps(self, maxSteps):
		"""Sets the maximum number of steps to simulate."""
		pass
		
	
	def getEnvironmentTemperature(self):
		"""Returns the simulation environment temperature in Kelvin."""
		pass
	def setEnvironmentTemperature(self, temperature):
		"""
		Sets the simulation environment temperature.
		@param temperature: in Kelvin
		"""
		pass
	
	
	def getEnvironmentPressure(self):
		"""Returns the simulation environment pressure in Pascals."""
		pass
	def setEnvironmentPressure(self, pressure):
		"""
		Sets the simulation environment pressure.
		@param pressure: in Pascals
		"""
		pass
	
	
	def getFilePathKeys(self):
		"""
		Returns an array of file path keys. These file paths are for simulation
		specification files, simulation workflow scripts, template files, etc.
		"""
		pass
	def getFilePath(self, key):
		"""Returns the file path associated with the given key."""
		pass
	def setFilePath(self, key, filePath):
		"""Associates the given file path with the given key."""
		pass
	
	
	def getRunResult(self):
		"""
		Returns the simulation run's result and failure message if the
		simulation failed.
		@return: (0=success, 1=still running, 2=failure, 3=aborted),
				 (failure message)
		"""
		pass
	def setRunResult(self, code, message):
		"""
		Sets the simulation run's result and failure message.
		@param code: 0=success, 1=still running, 2=failure, 3=aborted
		@param message: description of a simulation failure
		"""
		pass
	
	
	def getStepCount(self):
		"""Returns the number of steps successfully simulated."""
		pass
	def setStepCount(self, count):
		"""Sets the number of steps successfully simulated."""
		pass

	
	def getStartTime(self):
		"""
		Returns the simulation start time.
		@return: a U{datetime<http://docs.python.org/lib/datetime-datetime.html>}
				 object set to the simulation's start time
		"""
		pass
	def setStartTime(self, startTime):
		"""
		Sets the simulation start time.
		@param startTime: a U{datetime<http://docs.python.org/lib/datetime-datetime.html>}
						  object set to the simulation's start time
		"""
		pass
	
	
	def getCPU_RunningTime(self):
		"""Returns the simulation CPU running time in seconds."""
		pass
	def setCPU_RunningTime(self, cpuRunningTime):
		"""
		Set the simulation CPU running time.
		@param cpuRunningTime: in seconds
		"""
		pass
	
	
	def getWallRunningTime(self):
		"""Returns the simulation wall running time in seconds."""
		pass
	def setWallRunningTime(self, wallRunningTime):
		"""
		Sets the simulation wall running time.
		@param wallRunningTime: in seconds
		"""
		pass
	
	
	def getExtDataNames(self):
		"""Returns an array of extension data-set names."""
		pass
	def getExtDataKeys(self, extDataSetName):
		"""
		Returns an array of extension data-set keys for a given extension
		data-set.
		"""
		pass
	def getExtDataFloat(self, extDataSetName, key):
		"""
		Returns a floating point value stored in the extension data-set with the
		given key.
		"""
		pass
	def getExtDataInt(self, extDataSetName, key):
		"""
		Returns an integer value stored in the extension data-set with the
		given key.
		"""
		pass
	def getExtDataFloatArray(self, extDataSetName, key):
		"""
		Returns an array of floating point values stored in the extension
		data-set with the given key.
		"""
		pass
	def getExtDataIntArray(self, extDataSetName, key):
		"""
		Returns an array of integers stored in the extension data-set with the
		given key.
		"""
		pass
	def setExtDataFloat(self, extDataSetName, key, value):
		"""
		Sets a floating point value stored in the extension data-set with the
		given key.
		"""
		pass
	def setExtDataInt(self, extDataSetName, key, value):
		"""
		Sets an integer value stored in the extension data-set with the
		given key.
		"""
		pass
	def setExtDataFloatArray(self, extDataSetName, key, floatArray):
		"""
		Sets an array of floating point values stored in the extension data-set
		with the given key.
		"""
		pass
	def setExtDataIntArray(self, extDataSetName, key, intArray):
		"""
		Sets an array of integers stored in the extension data-set
		with the given key.
		"""
		pass

	
	def getFrameSetNames(self):
		"""
		Returns an array of frame-set names. These frame-set names are used to
		get/set frame data.
		"""
		pass
	def addFrameSet(self, name):
		"""
		Adds a frame-set with the given name.
		"""
		pass
	get/setAggregationMode(self, name, mode)
		@param aggregationMode: 0=per-time-step values are averaged (default),
								1=last per-time-step value is used
	get/setStepsPerFrame(self, name, stepsPerFrame)
		pass
	def removeFrameSet(self, name):
		"""Removes the frame-set with the given name."""
		pass
	
	
	def getFrameCount(self, frameSetName):
		"""Returns the number of frames in a frame-set."""
		pass
	def getFrameTimes(self, frameSetName):
		"""Returns an array of frame times (in seconds) for a frame-set."""
		pass
	def getFrameTime(self, frameSetName, frameIndex):
		"""Returns a specific frame time (in seconds) for a frame-set."""
		pass
	def addFrame(self, frameSetName, time):
		"""
		Adds a frame to the specified frame-set.
		@param time: the frame's time in seconds
		"""
		pass
	def removeFrame(self, frameSetName, frameIndex):
		"""Removes a frame from the specified frame-set."""
		pass
	
	
	def getFrameAtomIds(self, frameSetName):
		"""Returns an array of atom identifiers for a frame-set."""
		pass
	def setFrameAtomIds(self, frameSetName, atomIds):
		"""Sets the array of atom identifiers for a frame-set."""
		pass
	
	
	def getFrameAtomPositions(self, frameSetName, frameIndex):
		"""
		Returns an array of Cartesian atom positions for a specified frame. Each
		position is an array of length 3 corresponding to x, y, z coordinates in
		meters.
		"""
		pass
	def setFrameAtomPositions(self, frameSetName, frameIndex, positions):
		"""
		Sets the array of Cartesian atom positions for a specified frame.
		@param positions: an array of arrays of length 3 corresponding to
						  x, y, z coordinates for each atom in meters
		"""
		pass
	
	
	def getFrameAtomVelocities(self, frameSetName, frameIndex):
		"""
		Returns an array of atom velocities for a specified frame. Each velocity
		is an array of length 3 corresponding to the x, y, z components of the
		atom's velocity in m/s.
		"""
		pass
	def setFrameAtomVelocities(self, frameSetName, frameIndex, velocities):
		"""
		Sets the array of atom velocities for a specified frame.
		@param velocities: an array of arrays of length 3 corresponding to the
						   x, y, z components for each atom's velocity in m/s
		"""
		pass
	
	
	def getFrameBonds(self, frameSetName, frameIndex):
		"""Returns an array of SimResultsBond objects for a specified frame."""
		pass
	def setFrameBonds(self, frameSetName, frameIndex, bonds):
		"""Sets the array of SimResultsBond objects for a specified frame."""
		pass
	
	
	def getFrameTotalEnergy(self, frameSetName, frameIndex):
		"""Returns the total energy for the specified frame in Joules."""
		pass
	def setFrameTotalEnergy(self, frameSetName, frameIndex, totalEnergy):
		"""
		Sets the total energy for the specified frame.
		@param totalEnergy: in Joules
		"""
		pass
	
	
	def getFrameIdealTemperature(self, frameSetName, frameIndex):
		"""Returns the ideal temperature for the specified frame in Kelvin."""
		pass
	def setFrameIdealTemperature(self, frameSetName, frameIndex, temperature):
		"""
		Sets the ideal temperature for the specified frame.
		@param temperature: in Kelvin
		"""
		pass
	
	
	def getFramePressure(self, frameSetName, frameIndex):
		"""Returns the pressure for the specified frame in Pascals."""
		pass
	def setFramePressure(self, frameSetName, frameIndex, pressure):
		"""
		Sets the pressure for the specified frame.
		@param pressure: in Pascals
		"""
		pass
	
	
	def getFrameExtDataNames(self, frameSetName):
		"""Returns an array of extension data-set names for a given frame-set."""
		pass
	def getFrameExtDataKeys(self, frameSetName, extDataSetName):
		"""
		Returns an array of extension data-set keys for a given extension
		data-set.
		"""
		pass
	def getFrameExtDataFloat(self, frameSetName, frameIndex, extDataSetName,
							 key):
		"""
		Returns a floating point value stored in the specified frame for the
		given key.
		"""
		pass
	def getFrameExtDataInt(self, frameSetName, frameIndex, extDataSetName, key):
		"""
		Returns an integer value stored in the specified frame for the given
		key.
		"""
		pass
	def getFrameExtDataFloatArray(self, frameSetName, frameIndex,
								  extDataSetName, key):
		"""
		Returns an array of floating point values stored in the specified frame
		for the given key.
		"""
		pass
	def getFrameExtDataIntArray(self, frameSetName, frameIndex, extDataSetName,
								key):
		"""
		Returns an array of integers stored in the specified frame for the given
		key.
		"""
		pass
	def setFrameExtDataFloat(self, frameSetName, frameIndex, extDataSetName,
							 key, value):
		"""
		Sets a floating point value stored in the specified frame for the given
		key.
		"""
		pass
	def setFrameExtDataInt(self, frameSetName, frameIndex, extDataSetName, key,
						   value):
		"""
		Sets an integer value stored in the specified frame for the given
		key.
		"""
		pass
	def setFrameExtDataFloatArray(self, frameSetName, frameIndex,
								  extDataSetName, key, floatArray):
		"""
		Sets an array of floating point values stored in the specified
		frame for the given key.
		"""
		pass
	def setFrameExtDataIntArray(self, frameSetName, frameIndex, extDataSetName,
								key, intArray):
		"""
		Sets an array of integers stored in the specified frame for the given
		key.
		"""
		pass
 */
};

} // ne1::

#endif
