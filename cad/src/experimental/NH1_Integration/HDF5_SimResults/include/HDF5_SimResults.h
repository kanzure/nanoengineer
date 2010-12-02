
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#ifndef NE1_HDF5_SIMRESULTS_H
#define NE1_HDF5_SIMRESULTS_H

#include <stdlib.h>
#include <map>

#include "hdf5.h"

#include "SimResultsDataStore.h"

#define HDF5_SIM_RESULT_FILENAME	"sim_results.h5"
#define GROUP_NAME_SIZE_HINT		64

#define USE_CHUNKING				1
#define USE_SHUFFLING				1
#define USE_COMPRESSION				1
#define COMPRESSION_LVL				6

#define TOTAL_ENERGY_MSRMT			0
#define IDEAL_TEMPERATURE_MSRMT		1
#define PRESSURE_MSRMT				2

namespace ne1 {


/* CLASS: FrameSetInfo */
/**
 * Used internally to HDF5_SimResults.
 */
class FrameSetInfo {
	public:
		FrameSetInfo() {
			currentFrameIndex = 0;
			timestampsDatasetId = 0;
			atomIdsDatasetId = 0;
			atomicNumbersDatasetId = 0;
			atomPositionsDatasetId = 0;
			atomVelocitiesDatasetId = 0;
			bondsDatasetId = 0;
			measurementsDatasetId = 0;
		}
	
		int currentFrameIndex;
		hid_t timestampsDatasetId;
		hid_t atomIdsDatasetId;
		hid_t atomicNumbersDatasetId;
		hid_t atomPositionsDatasetId;
		hid_t atomVelocitiesDatasetId;
		hid_t bondsDatasetId;
		hid_t measurementsDatasetId;
};
	

/* CLASS: HDF5_SimResults */
/**
 * HDF5 implementation of SimResultsDataStore.
 *
 * Hierarchy:
 \code
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
					Timestamps - dataset
					AtomIds - dataset, AtomicNumbers - dataset
					AtomPositions, AtomVelocities - dataset
					Bonds - dataset
					Measurements - dataset
\endcode
 */
class HDF5_SimResults : public SimResultsDataStore {
	public:
		HDF5_SimResults();
		~HDF5_SimResults();
		
		int openDataStore(const char* directory, std::string& message);
		void synchronize();
		
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
		
		int getAggregationMode(const char* frameSetName, int& mode) const;
		int setAggregationMode(const char* frameSetName, const int& mode,
							   std::string& message);
		
		int getStepsPerFrame(const char* frameSetName,
							 int& stepsPerFrame) const;
		int setStepsPerFrame(const char* frameSetName,
							 const int& stepsPerFrame,
							 std::string& message);
		
		
		void getFrameCount(const char* frameSetName, int& frameCount);
		int getFrameTimes(const char* frameSetName, float* frameTimes,
						  std::string& message);
		int getFrameTime(const char* frameSetName, const int& frameIndex,
						 float& time, std::string& message);
		int addFrame(const char* frameSetName, const float& time,
					 int& frameIndex, std::string& message);
		
		void getFrameAtomIdsCount(const char* frameSetName,
								  unsigned int& atomIdsCount);
		int getFrameAtomIds(const char* frameSetName,
							unsigned int* atomIds,
							std::string& message);
		int setFrameAtomIds(const char* frameSetName,
							const unsigned int* atomIds,
							const unsigned int& atomIdsCount,
							std::string& message);
		
		int getFrameAtomicNumbers(const char* frameSetName,
								  unsigned int* atomicNumbers,
								  std::string& message);
		int setFrameAtomicNumbers(const char* frameSetName,
								  const unsigned int* atomicNumbers,
								  const unsigned int& atomicNumbersCount,
								  std::string& message);
		
		int getFrameAtomPositions(const char* frameSetName,
								  const int& frameIndex,
								  const unsigned int& atomCount,
								  float* positions,
								  std::string& message);
		int setFrameAtomPositions(const char* frameSetName,
								  const int& frameIndex,
								  const float* positions,
								  const unsigned int& atomCount,
								  std::string& message);
		
		int getFrameAtomVelocities(const char* frameSetName,
								   const int& frameIndex,
								   const unsigned int& atomCount,
								   float* velocities,
								   std::string& message);
		int setFrameAtomVelocities(const char* frameSetName,
								   const int& frameIndex,
								   const float* velocities,
								   const unsigned int& atomCount,
								   std::string& message);
		
		void getFrameBondsCount(const char* frameSetName,
								const int& frameIndex,
								unsigned int& bondCount);
		int getFrameBonds(const char* frameSetName,
						  const int& frameIndex,
						  void* bonds,
						  std::string& message);
		int setFrameBonds(const char* frameSetName,
						  const int& frameIndex,
						  const void* bonds,
						  const unsigned int& bondCount,
						  std::string& message);
		
		int getFrameTotalEnergy(const char* frameSetName,
								const int& frameIndex,
								float& totalEnergy,
								std::string& message);
		int setFrameTotalEnergy(const char* frameSetName,
								const int& frameIndex,
								const float& totalEnergy,
								std::string& message);
		
		int getFrameIdealTemperature(const char* frameSetName,
									 const int& frameIndex,
									 float& idealTemperature,
									 std::string& message);
		int setFrameIdealTemperature(const char* frameSetName,
									 const int& frameIndex,
									 const float& idealTemperature,
									 std::string& message);

		int getFramePressure(const char* frameSetName,
							 const int& frameIndex,
							 float& pressure,
							 std::string& message);
		int setFramePressure(const char* frameSetName,
							 const int& frameIndex,
							 const float& pressure,
							 std::string& message);
		
	private:
		// HDF5 type identifiers
		hid_t bondTypeId;
		hid_t bondsVariableLengthId;
		
		hid_t fileId;	// HDF5 file identifier
		
		std::string dataStoreDirectory;
		std::map<std::string, FrameSetInfo> frameSetInfoMap;
		
		void closeDatasets();
		void openDatasets();
		
		
		int checkFrameExistence(const char* frameSetName,
								const int& frameIndex,
								std::string& message);
		int checkFrameSetDatasetExistence(const char* frameSetName,
										  hid_t& datasetId,
										  const char* datasetName,
										  std::string& message);
		int checkTimestampsExistence(const char* frameSetName,
									 std::string& message);
		int checkFrameSetExistence(const char* frameSetName,
								   std::string& message);
		int createMeasurementsDataset(const char* frameSetName,
									  hid_t& datasetId,
									  std::string& message);			
		int createBondsDataset(const char* frameSetName,
							   const unsigned int& bondCount,
							   hid_t& datasetId,
							   std::string& message);
		int create3D_AtomFloatsDataset(const char* frameSetName,
									   const char* dataSetName,
									   const unsigned int& atomCount,
									   hid_t& datasetId,
									   std::string& message);
		int createTimestampsDataset(const char* frameSetName, hid_t& datasetId,
									std::string& message);
		int writeMeasurement(const char* frameSetName,
							 const int& frameIndex,
							 const int& measurementIndex,
							 const float& value,
							 const hid_t& datasetId,
							 std::string& message);
		int writeBonds(const int& frame, const unsigned int& bondCount,
					   const void* bonds, hid_t datasetId,
					   std::string& message);
		int writeAtomUInts(const char* frameSetName,
						   const char* dataSetName,
						   const unsigned int* atomUInts,
						   const unsigned int& atomUIntsCount,
						   hid_t& datasetId,
						   std::string& message);
		int write3SpaceAtomFloats(const int& frame,
								  const unsigned int& atomCount,
								  const float* data,
								  hid_t datasetId,
								  std::string& message);
		int writeTimestamp(const int& frame, const float& time,
						   hid_t datasetId,
						   std::string& message);
		int readMeasurement(const char* frameSetName,
							const int& frameIndex,
							const int& measurementIndex,
							const hid_t& datasetId,
							float& value,
							std::string& message);
		int read3SpaceAtomFloats(const int& frame,
								 const unsigned int& atomCount,
								 float* data,
								 hid_t datasetId,
								 std::string& message);
		int readTimestamp(const int& frame, float& time, hid_t datasetId,
						  std::string& message) const;
			
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
