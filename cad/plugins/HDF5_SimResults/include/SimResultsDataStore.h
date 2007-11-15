
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#ifndef NE1_SIMRESULTSDATASTORE_H
#define NE1_SIMRESULTSDATASTORE_H

#include <string>
#include <vector>

#define SRDS_UNABLE_TO_OPEN_FILE			1
#define SRDS_UNABLE_TO_COMPLETE_OPERATION	2
#define SRDS_NON_EXISTENT_FRAMESET			3
#define SRDS_EMPTY_FRAMESET					4
#define SRDS_INVALID_FRAMEINDEX				5
#define SRDS_NON_EXISTENT_DATASET			6

namespace ne1 {


/* STRUCT: SimResultsBond */
/**
 * A chemical bond. See SimResultsDataStore for context.
 */
typedef struct SimResultsBond {
	unsigned int atomId_1, atomId_2;
	float order;
} SimResultsBond;


/* CLASS: SimResultsDataStore */
/**
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

	
	/* METHOD: synchronize */
	/**
	 * Forces the datastore to be re-read from disk. Use to get the latest data
	 * written to the datastore.
	 */
	virtual void synchronize() = 0;
	
	
	/*
	 * Name
	 */
	/** Retrieves the simulation name.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getName(std::string& name) const = 0;
	
	/** Sets the simulation name.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setName(const std::string& name, std::string& message) = 0;
	
	
	/*
	 * Description
	 */
	/** Retrieves the simulation description.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getDescription(std::string& description) const = 0;
	
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
	/** Retrieves the user's notes for these simulation results.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getNotes(std::string& notes) const = 0;
	
	/** Sets the user's notes for these simulation results.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setNotes(const std::string& notes, std::string& message) = 0;
		
	
	/*
	 * Timestep
	 */
	/** Retrieves the simulation timestep in seconds.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getTimestep(float& timestep) const = 0;
	
	/** Sets the simulation timestep.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setTimestep(const float& timestep, std::string& message) = 0;
	
	
	/*
	 * StartStep
	 */
	/** Retrieves the simulation starting step number.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getStartStep(int& startStep) const = 0;
	
	/** Sets the simulation starting step number.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setStartStep(const int& startStep, std::string& message) = 0;
	

	/*
	 * MaxSteps
	 */
	/** Retrieves the maximum number of steps to simulate.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getMaxSteps(int& maxSteps) const = 0;
	
	/** Sets the maximum number of steps to simulate.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setMaxSteps(const int& maxSteps, std::string& message) = 0;
	
	
	/*
	 * EnvironmentTemperature
	 */
	/** Retrieves the simulation environment temperature in Kelvin.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getEnvironmentTemperature(float& envTemp) const = 0;
	
	/** Sets the simulation environment temperature.
	 *
	 * @param envTemp in Kelvin
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setEnvironmentTemperature(const float& envTemp,
										  std::string& message) = 0;

	/*
	 * EnvironmentPressure
	 */
	/** Retrieves the simulation environment pressure in Pascals.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getEnvironmentPressure(float& envPress) const = 0;
	
	/** Sets the simulation environment pressure.
	 *
	 * @param envTemp in Pascals
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setEnvironmentPressure(const float& envPress,
									   std::string& message) = 0;

	
	/*
	 * FilePath
	 */
	/**
	 * Returns a vector of file path keys. These file paths are for simulation
	 * specification files, simulation workflow scripts, template files, etc.
	 *
	 */
	virtual std::vector<std::string> getFilePathKeys() const = 0;

	/** Retrieves the file path associated with the given key.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getFilePath(const char* key, std::string& filePath) const = 0;

	/** Associates the given file path with the given key.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFilePath(const char* key, const char* filePath,
							std::string& message) = 0;


	/*
	 * RunResult
	 */
	/**
	 * Retrieves the simulation run's result and failure message if the
	 * simulation failed.
	 *
	 * @param result	0=success, 1=still running, 2=failure, 3=aborted
	 * @param failureDescription	description of the failure/abortion if
	 *								result=2/3
	 * @return			0=successful or non-zero if no value was found.
	 */
	virtual int getRunResult(int& result,
							 std::string& failureDescription) const = 0;

	/** Sets the simulation run's result and failure message.
	 * 
	 * @param code		0=success, 1=still running, 2=failure, 3=aborted
	 * @param failureDescription	description of the failure/abortion if
	 *								result=2/3
	 * @param message	description of the error when a non-zero value is returned
	 * @return			0=successful or non-zero error code
	 */
	virtual int setRunResult(const int& code, const char* failureDescription,
							 std::string& message) = 0;
	

	/*
	 * StepCount
	 */
	/** Retrieves the number of steps successfully simulated.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getStepCount(int& stepCount) const = 0;

	/** Sets the number of steps successfully simulated.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setStepCount(const int& stepCount, std::string& message) = 0;

	
	/*
	 * StartTime
	 */
	/** Retrieves the simulation start time.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getStartTime(time_t& startTime) const = 0;

	/** Sets the simulation start time.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setStartTime(const time_t& startTime, std::string& message) = 0;
	
	
	/*
	 * CPU_RunningTime
	 */
	/** Retrieves the simulation CPU running time in seconds.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getCPU_RunningTime(float& cpuRunningTime) const = 0;
	
	/** Sets the simulation CPU running time.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setCPU_RunningTime(const float& cpuRunningTime,
								   std::string& message) = 0;
	
	/*
	 * WallRunningTime
	 */
	/** Retrieves the simulation wall running time in seconds.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getWallRunningTime(float& wallRunningTime) const = 0;
	
	/** Sets the simulation CPU running time.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setWallRunningTime(const float& wallRunningTime,
								   std::string& message) = 0;
	
	/*
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
	*/

	
	/*
	 * FrameSet
	 */
	/**
	 * Returns a vector of frame-set names. These frame-set names are used to
	 * get/set frame data.
	 */
	virtual std::vector<std::string> getFrameSetNames() const = 0;
	
	/**
	 * Adds a frame-set with the given name. If a frame-set with the given name
	 * already exists, the call fails.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int addFrameSet(const char* name, std::string& message) = 0;

	/**
	 * Removes the frame-set with the given name.
	 *
	def removeFrameSet(self, name):
	 */
	

	/*
	 * AggregationMode
	 */
	/** Retrieves the aggregation mode of the frame-set with the given name.
	 *
	 * @param mode [IN]	0=per-time-step values are averaged (default),
	 *					1=last per-time-step value is used
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getAggregationMode(const char* frameSetName,
								   int& mode) const = 0;
	/**
	 * Sets the aggregation mode of the frame-set with the given name. If a
	 * frame-set with the given name doesn't exist, the call fails.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setAggregationMode(const char* frameSetName, const int& mode,
								   std::string& message) = 0;
	
	
	/*
	 * StepsPerFrame
	 */
	/**
	 * Retrieves the steps-per-frame for the frame-set with the given name.
	 *
	 * @return 0=successful or non-zero if no value was found.
	 */
	virtual int getStepsPerFrame(const char* frameSetName,
								 int& stepsPerFrame) const = 0;
	/**
	 * Sets the steps-per-frame for the frame-set with the given name. If a
	 * frame-set with the given name doesn't exist, the call fails.
	 *
	 * @param message description of the error when a non-zero value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setStepsPerFrame(const char* frameSetName,
								 const int& stepsPerFrame,
								 std::string& message) = 0;

	/*
	 * Frame
	 */
	/**
	 * Retrieves the number of frames in a frame-set.
	 *
	 * @param frameCount	[OUT] the number of frames in the specified
	 *						frame-set. This is a signed integer so that users
	 *						can encode information in its negative value realm.
	 */
	virtual void getFrameCount(const char* frameSetName,
							   int& frameCount) = 0;
	
	/** Retrieves a malloc'd array of frame times (in seconds) for a frame-set.
	 *
	 * @param frameSetName	[IN] the name of the frame-set to retieve frame
	 *						times from
	 * @param frameTimes	[OUT] a malloc'd float array with sufficient
	 *						space to store the frame-set times
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameTimes(const char* frameSetName, float* frameTimes,
							  std::string& message) = 0;

	/** Retrieves the frame time for a specific frame
	 *
	 * @param frameSetName	[IN] the name of the frame-set to retieve frame
	 *						times from
	 * @param frameIndex	[IN] the index of the frame to retrieve the time
	 *						from
	 * @param time			[OUT] the frame's timestamp in seconds
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameTime(const char* frameSetName, const int& frameIndex,
							 float& time, std::string& message) = 0;
	
	/** Adds a frame to the specified frame-set.
	 *
	 * @param time			[IN] the frame's time in seconds
	 * @param frameIndex	[OUT] the frame index of the newly added frame
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int addFrame(const char* frameSetName, const float& time,
						 int& frameIndex, std::string& message) = 0;

	/*
	def removeFrame(self, frameSetName, frameIndex):
		"""Removes a frame from the specified frame-set."""
		pass
	 */
	
	
	/*
	 * AtomIds
	 */
	/** Retrieves the number of atom ids for the frame-set. */
	virtual void getFrameAtomIdsCount(const char* frameSetName,
									  unsigned int& atomIdsCount) = 0;
	
	/** Retrieves an array of atom identifiers for the frame-set. */
	virtual int getFrameAtomIds(const char* frameSetName,
								unsigned int* atomIds,
								std::string& message) = 0;

	/** Sets the array of atom identifiers for the specified frame-set.
	 *
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameAtomIds(const char* frameSetName,
								const unsigned int* atomIds,
								const unsigned int& atomIdsCount,
								std::string& message) = 0;
	/*
	 * AtomicNumbers
	 */
	/** Retrieves an array of atomic numbers for the frame-set. */
	virtual int getFrameAtomicNumbers(const char* frameSetName,
									  unsigned int* atomicNumbers,
									  std::string& message) = 0;
	
	/** Sets the array of atomic numbers for the specified frame-set.
	 *
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameAtomicNumbers(const char* frameSetName,
									  const unsigned int* atomicNumbers,
									  const unsigned int& atomicNumbersCount,
									  std::string& message) = 0;
	
	/*
	 * AtomPositions
	 */
	/**
	 * Retrieves an array of Cartesian atom positions for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set to set atom positions
	 *						for
	 * @param frameIndex	[IN] the index of the frame to set atom positions
	 *						for
	 * @param atomCount		[IN] the number of atoms
	 * @param positions		[OUT] an array of length: 3 x (number of atoms)
	 *						will contain atom positions in meters, layed out
	 *						like atom0.x, atom0.y, atom0.z, atom1.x, atom1.y,
	 *						atom1.z, etc.
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameAtomPositions(const char* frameSetName,
									  const int& frameIndex,
									  const unsigned int& atomCount,
									  float* positions,
									  std::string& message) = 0;
	
	/** Sets the array of Cartesian atom positions for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set to set atom positions
	 *						for
	 * @param frameIndex	[IN] the index of the frame to set atom positions
	 *						for
	 * @param positions		[IN] an array of length: 3 x (number of atoms)
	 *						containing atom positions in meters, layed out like
	 *						atom0.x, atom0.y, atom0.z, atom1.x, atom1.y,
	 *						atom1.z, etc.
	 * @param atomCount		[IN] the number of atoms
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameAtomPositions(const char* frameSetName,
									  const int& frameIndex,
									  const float* positions,
									  const unsigned int& atomCount,
									  std::string& message) = 0;
	/*
	 * AtomVelocities
	 */
	/**
	 * Retrieves an array of atom velocities for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set to set atom
	 *						velocities for
	 * @param frameIndex	[IN] the index of the frame to set atom velocities
	 *						for
	 * @param atomCount		[IN] the number of atoms
	 * @param velocities	[OUT] an array of length: 3 x (number of atoms)
	 *						will contain atom velocities in meters/second, layed
	 *						out like atom0.x, atom0.y, atom0.z, atom1.x,
	 *						atom1.y, atom1.z, etc.
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameAtomVelocities(const char* frameSetName,
									   const int& frameIndex,
									   const unsigned int& atomCount,
									   float* velocities,
									   std::string& message) = 0;
	
	/** Sets the array of atom velocities for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set to set atom
	 *						velocities for
	 * @param frameIndex	[IN] the index of the frame to set atom velocities
	 *						for
	 * @param velocities	[IN] an array of length: 3 x (number of atoms)
	 *						containing atom velocities in meters/second, layed
	 *						out like atom0.x, atom0.y, atom0.z, atom1.x,
	 *						atom1.y, atom1.z, etc.
	 * @param atomCount		[IN] the number of atoms
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameAtomVelocities(const char* frameSetName,
									   const int& frameIndex,
									   const float* velocities,
									   const unsigned int& atomCount,
									   std::string& message) = 0;
	/*
	 * Bonds
	 */
	/**
	 * Retrieves the number of bonds for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set from which to
	 *						retrieve bonds
	 * @param frameIndex	[IN] the index of the frame from which to retrieve
	 *						bonds
	 * @param bondCount		[OUT] the number of bonds
	 */
	 virtual void getFrameBondsCount(const char* frameSetName,
									const int& frameIndex,
									unsigned int& bondCount) = 0;
	/**
	 * Retrieves an array of SimResultsBond structs for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set from which to
	 *						retrieve bonds
	 * @param frameIndex	[IN] the index of the frame from which to retrieve
	 *						bonds
	 * @param bonds			[OUT] a pointer to an array of SimResultsBond
	 *						structs (don't forget to free() it when done with
	 *						it)
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameBonds(const char* frameSetName,
							  const int& frameIndex,
							  void* bonds,
							  std::string& message) = 0;
	
	/** Sets the array of SimResultsBond structs for a specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set in which to set bonds
	 * @param frameIndex	[IN] the index of the frame in which to set bonds
	 * @param bonds			[IN] a pointer to an array of SimResultsBond structs
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameBonds(const char* frameSetName,
							  const int& frameIndex,
							  const void* bonds,
							  const unsigned int& bondCount,
							  std::string& message) = 0;
	/*
	 * TotalEnergy
	 */
	/**
	 * Retrieves the total energy for the specified frame in Joules.
	 *
	 * @param frameSetName	[IN] the name of the frame-set of interest
	 * @param frameIndex	[IN] the index of the frame of interest
	 * @param totalEnergy	[OUT] total energy in Joules
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameTotalEnergy(const char* frameSetName,
									const int& frameIndex,
									float& totalEnergy,
									std::string& message) = 0;
	/**
	 * Sets the total energy for the specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set of interest
	 * @param frameIndex	[IN] the index of the frame of interest
	 * @param totalEnergy	[IN] total energy in Joules
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameTotalEnergy(const char* frameSetName,
									const int& frameIndex,
									const float& totalEnergy,
									std::string& message) = 0;
	/*
	 * IdealTemperature
	 */
	/**
	 * Retrieves the ideal temperature for the specified frame in Kelvin.
	 *
	 * @param frameSetName		[IN] the name of the frame-set of interest
	 * @param frameIndex		[IN] the index of the frame of interest
	 * @param idealTemperature	[OUT] ideal temperature in Kelvin
	 * @param message			[OUT] description of the error when a non-zero
	 *							value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFrameIdealTemperature(const char* frameSetName,
										 const int& frameIndex,
										 float& idealTemperature,
										 std::string& message) = 0;
	/**
	 * Sets the ideal temperature for the specified frame.
	 *
	 * @param frameSetName		[IN] the name of the frame-set of interest
	 * @param frameIndex		[IN] the index of the frame of interest
	 * @param idealTemperature	[IN] ideal temperature in Kelvin
	 * @param message			[OUT] description of the error when a non-zero
	 *							value is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFrameIdealTemperature(const char* frameSetName,
										 const int& frameIndex,
										 const float& idealTemperature,
										 std::string& message) = 0;
	/*
	 * Pressure
	 */
	/**
	 * Retrieves the pressure for the specified frame in Pascals.
	 *
	 * @param frameSetName	[IN] the name of the frame-set of interest
	 * @param frameIndex	[IN] the index of the frame of interest
	 * @param pressure		[OUT] pressure in Pascals
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int getFramePressure(const char* frameSetName,
								 const int& frameIndex,
								 float& pressure,
								 std::string& message) = 0;
	/**
	 * Sets the pressure for the specified frame.
	 *
	 * @param frameSetName	[IN] the name of the frame-set of interest
	 * @param frameIndex	[IN] the index of the frame of interest
	 * @param pressure		[OUT] pressure in Pascals
	 * @param message		[OUT] description of the error when a non-zero value
	 *						is returned
	 * @return 0=successful or non-zero error code
	 */
	virtual int setFramePressure(const char* frameSetName,
								 const int& frameIndex,
								 const float& pressure,
								 std::string& message) = 0;
	
	
	/*
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
