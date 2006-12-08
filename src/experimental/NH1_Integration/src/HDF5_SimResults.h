
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#ifndef NE1_HDF5_SIMRESULTS_H
#define NE1_HDF5_SIMRESULTS_H

#include <stdlib.h>

#include "hdf5.h"

#include "SimResultsDataStore.h"

#define HDF5_SIM_RESULT_FILENAME	"sim_results.h5"
#define GROUP_NAME_SIZE_HINT		64

namespace ne1 {


/* CLASS: HDF5_SimResults
 *
 * HDF5 implementation of SimResultsDataStore.
 *
 * Hierarchy:
	/
		Name, Description, Notes - attributes
	
		Parameters/ - attributes
			StartStep, MaxSteps
			Timestep, EnvironmentTemperature, EnvironmentPressure
	
		InputFilePaths/
			key = filePath attributes
	
		Results/ - attributes
			RunResult
			StepCount
			StartTime
			CPU_RunningTime, WallRunningTime
	
			ExtensionData/
				name/
					key=int-attribute, float-attribute
					key=int-array-dataset, float-array-dataset
	
			FrameSets/
				name/
					AggregationMode, StepsPerFrame - attributes
					FrameTimes - dataset
					AtomIds - dataset
					AtomPositions, AtomVelocities - dataset
					Bonds - dataset
					Measurements - dataset
 */
class HDF5_SimResults : public SimResultsDataStore {
	public:
		HDF5_SimResults();
		~HDF5_SimResults();
		
		int openDataStore(const char* directory, std::string& message);
		
		int getName(std::string& name) const;
		int setName(const std::string& name, std::string& message);
		
		int getDescription(std::string& description) const;
		int setDescription(const std::string& description,
						   std::string& message);
		
		int getNotes(std::string& notes) const;
		int setNotes(const std::string& notes, std::string& message);
		
		
		int getTimestep(float& timestep) const;
		int setTimestep(const float& timestep, std::string& message);
		
		int getStartStep(int& startStep) const;
		int setStartStep(const int& startStep, std::string& message);
		
		int getMaxSteps(int& maxSteps) const;
		int setMaxSteps(const int& maxSteps, std::string& message);
		
		int getEnvironmentTemperature(float& envTemp) const;
		int setEnvironmentTemperature(const float& envTemp,
									  std::string& message);
		
		int getEnvironmentPressure(float& envPress) const;
		int setEnvironmentPressure(const float& envPress, std::string& message);
		
		
		std::vector<std::string> getFilePathKeys() const;
		int getFilePath(const char* key, std::string& filePath) const;
		int setFilePath(const char* key, const char* filePath,
						std::string& message);
		
		
		int getRunResult(int& result, std::string& failureDescription) const;
		int setRunResult(const int& code, const char* failureDescription,
						 std::string& message);
		
		int getStepCount(int& stepCount) const;
		int setStepCount(const int& stepCount, std::string& message);
		
		int getStartTime(time_t& startTime) const;
		int setStartTime(const time_t& startTime, std::string& message);
		
		int getCPU_RunningTime(float& cpuRunningTime) const;
		int setCPU_RunningTime(const float& cpuRunningTime,
							   std::string& message);
		
		int getWallRunningTime(float& wallRunningTime) const;
		int setWallRunningTime(const float& wallRunningTime,
							   std::string& message);
		
		
		std::vector<std::string> getFrameSetNames() const;
		int addFrameSet(const char* name, std::string& message);
		
	private:
		// HDF5 type identifiers
		hid_t bondTypeId;
		hid_t bondsVariableLengthId;
		
		hid_t fileId;	// HDF5 file identifier
		
		int getStringAttribute(const std::string& groupName,
							   const std::string& attributeName,
							   std::string& attributeValue) const;
		int setStringAttribute(const std::string& groupName,
							   const std::string& attributeName,
							   const std::string& value,
							   std::string& message);
		int getIntAttribute(const std::string& groupName,
							const std::string& attributeName,
							int& attributeValue) const;
		int setIntAttribute(const std::string& groupName,
							const std::string& attributeName,
							const int& value,
							std::string& message);
		int getFloatAttribute(const std::string& groupName,
							  const std::string& attributeName,
							  float& attributeValue) const;
		int setFloatAttribute(const std::string& groupName,
							  const std::string& attributeName,
							  const float& value,
							  std::string& message);
		int getTimeAttribute(const std::string& groupName,
							 const std::string& attributeName,
							 time_t& attributeValue) const;
		int setTimeAttribute(const std::string& groupName,
							 const std::string& attributeName,
							 const time_t& value,
							 std::string& message);
};

} // ne1::

#endif
