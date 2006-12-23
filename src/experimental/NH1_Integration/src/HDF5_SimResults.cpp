
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#include "HDF5_SimResults.h"

namespace ne1 {


/* FUNCTION: H5_ErrorStackWalker */
herr_t H5_ErrorStackWalker(int position, H5E_error_t* errorDesc,
						   void* hdf5Message) {
	if (((std::string*)hdf5Message)->length() == 0)
		((std::string*)hdf5Message)->append(errorDesc->desc);
	
	return 0;
}


/* CONSTRUCTOR */
HDF5_SimResults::HDF5_SimResults() {
	
	// Create new HDF5 types
	//
	bondTypeId = H5Tcreate(H5T_COMPOUND, sizeof(SimResultsBond));
	H5Tinsert(bondTypeId, "atomId_1", HOFFSET(SimResultsBond, atomId_1),
			  H5T_NATIVE_UINT);
	H5Tinsert(bondTypeId, "atomId_2", HOFFSET(SimResultsBond, atomId_2),
			  H5T_NATIVE_UINT);
	H5Tinsert(bondTypeId, "order", HOFFSET(SimResultsBond, order),
			  H5T_NATIVE_FLOAT);
	
	bondsVariableLengthId = H5Tvlen_create(bondTypeId);
	
	// Turn off printing errors to stdout
	H5Eset_auto(0, 0);
	
	fileId = 0;
}


/* DESTRUCTOR */
HDF5_SimResults::~HDF5_SimResults() {
	if (fileId != 0)
		H5Fclose(fileId);
}


/* FUNCTION: openDataStore */
int HDF5_SimResults::openDataStore(const char* directory,
								   std::string& message) {
	int resultCode = 0;
	
	// Build the filepath
	std::string filepath = directory;
	filepath.append("/").append(HDF5_SIM_RESULT_FILENAME);
	
	// See if the file exists and open it
	fileId = H5Fopen(filepath.c_str(), H5F_ACC_RDWR, H5P_DEFAULT);
	if (fileId < 0) {
		// Doesn't exist, create it
		message = "Couldn't open file: ";
		message.append(filepath).append(": ");
		
		// Get error description from HDF5
		std::string hdf5Message;
		herr_t status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(". ");

		fileId =
			H5Fcreate(filepath.c_str(), H5F_ACC_EXCL, H5P_DEFAULT, H5P_DEFAULT);
		if (fileId < 0) {
			message.append("Couldn't create new file either: ");
			
			// Get error description from HDF5
			hdf5Message = "";
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
				
			resultCode = SRDS_UNABLE_TO_OPEN_FILE;
		}
	}
	return resultCode;
}


/* FUNCTION: getName */
int HDF5_SimResults::getName(std::string& name) const {
	return getStringAttribute("/", "Name", name);
}


/* FUNCTION: setName */
int HDF5_SimResults::setName(const std::string& name, std::string& message) {
	return setStringAttribute("/", "Name", name, message);
}


/* FUNCTION: getDescription */
int HDF5_SimResults::getDescription(std::string& description) const {
	return getStringAttribute("/", "Description", description);
}


/* FUNCTION: setDescription */
int HDF5_SimResults::setDescription(const std::string& description,
									std::string& message) {
	return setStringAttribute("/", "Description", description,
							  message);
}


/* FUNCTION: getNotes */
int HDF5_SimResults::getNotes(std::string& notes) const {
	return getStringAttribute("/", "Notes", notes);
}


/* FUNCTION: setNotes */
int HDF5_SimResults::setNotes(const std::string& notes, std::string& message) {
	return setStringAttribute("/", "Notes", notes, message);
}


/* FUNCTION: getTimestep */
int HDF5_SimResults::getTimestep(float& timestep) const {
	return getFloatAttribute("/Parameters", "Timestep", timestep);
}


/* FUNCTION: setTimestep */
int HDF5_SimResults::setTimestep(const float& timestep, std::string& message) {
	return setFloatAttribute("/Parameters", "Timestep", timestep, message);
}


/* FUNCTION: getStartStep */
int HDF5_SimResults::getStartStep(int& startStep) const {
	return getIntAttribute("/Parameters", "StartStep", startStep);
}


/* FUNCTION: setStartStep */
int HDF5_SimResults::setStartStep(const int& startStep, std::string& message) {
	return setIntAttribute("/Parameters", "StartStep", startStep, message);
}


/* FUNCTION: getMaxSteps */
int HDF5_SimResults::getMaxSteps(int& maxSteps) const {
	return getIntAttribute("/Parameters", "MaxSteps", maxSteps);
}


/* FUNCTION: setMaxSteps */
int HDF5_SimResults::setMaxSteps(const int& maxSteps, std::string& message) {
	return setIntAttribute("/Parameters", "MaxSteps", maxSteps, message);
}


/* FUNCTION: getEnvironmentTemperature */
int HDF5_SimResults::getEnvironmentTemperature(float& envTemp) const {
	return getFloatAttribute("/Parameters", "EnvironmentTemperature", envTemp);
}


/* FUNCTION: setEnvironmentTemperature */
int HDF5_SimResults::setEnvironmentTemperature(const float& envTemp,
											   std::string& message) {
	return setFloatAttribute("/Parameters", "EnvironmentTemperature", envTemp,
							 message);
}


/* FUNCTION: getEnvironmentPressure */
int HDF5_SimResults::getEnvironmentPressure(float& envPress) const {
	return getFloatAttribute("/Parameters", "EnvironmentPressure", envPress);
}


/* FUNCTION: setEnvironmentPressure */
int HDF5_SimResults::setEnvironmentPressure(const float& envPress,
											std::string& message) {
	return setFloatAttribute("/Parameters", "EnvironmentPressure", envPress,
							 message);
}


/* FUNCTION: getFilePathKeys */
std::vector<std::string> HDF5_SimResults::getFilePathKeys() const {	
	std::vector<std::string> keys;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, "/InputFilePaths");
	if (groupId > -1) {
		// Get an attribute count
		int attrCount = H5Aget_num_attrs(groupId);
		
		// Build key list
		hid_t attributeId;
		char buffer[64];
		for (int attrIndex = 0; attrIndex < attrCount; attrIndex++) {
			attributeId = H5Aopen_idx(groupId, attrIndex);
			H5Aget_name(attributeId, sizeof(buffer), buffer);
			H5Aclose(attributeId);
			keys.push_back(buffer);
		}
		H5Gclose(groupId);
	}		
	return keys;
}


/* FUNCTION: getFilePath */
int HDF5_SimResults::getFilePath(const char* key, std::string& filePath) const {
	return getStringAttribute("/InputFilePaths", key, filePath);
}

	
/* FUNCTION: setFilePath */
int HDF5_SimResults::setFilePath(const char* key, const char* filePath,
								 std::string& message) {
	return setStringAttribute("/InputFilePaths", key, filePath, message);
}


/* FUNCTION: getRunResult */
int HDF5_SimResults::getRunResult(int& result,
								  std::string& failureDescription) const {
	int status = getIntAttribute("/Results", "RunResult", result);
	
	if ((status == 0) && ((result == 2) || (result == 3)))
		getStringAttribute("/Results", "RunResultMessage", failureDescription);
	
	return status;
}


/* FUNCTION: setRunResult */
int HDF5_SimResults::setRunResult(const int& code,
								  const char* failureDescription,
								  std::string& message) {
	int status = setIntAttribute("/Results", "RunResult", code, message);
	if ((status == 0) && ((code == 2) || (code == 3)))
		status =
			setStringAttribute("/Results", "RunResultMessage",
							   failureDescription, message);
	return status;
}


/* FUNCTION: getStepCount */
int HDF5_SimResults::getStepCount(int& stepCount) const {
	return getIntAttribute("/Results", "StepCount", stepCount);
}


/* FUNCTION: setStepCount */
int HDF5_SimResults::setStepCount(const int& stepCount, std::string& message) {
	return setIntAttribute("/Results", "StepCount", stepCount, message);
}


/* FUNCTION: getStartTime */
int HDF5_SimResults::getStartTime(time_t& startTime) const {
	return getTimeAttribute("/Results", "StartTime", startTime);
}


/* FUNCTION: setStartTime */
int HDF5_SimResults::setStartTime(const time_t& startTime,
								  std::string& message) {
	return setTimeAttribute("/Results", "StartTime", startTime, message);
}


/* FUNCTION: getCPU_RunningTime */
int HDF5_SimResults::getCPU_RunningTime(float& cpuRunningTime) const {
	return getFloatAttribute("/Results", "CPU_RunningTime", cpuRunningTime);
}


/* FUNCTION: setCPU_RunningTime */
int HDF5_SimResults::setCPU_RunningTime(const float& cpuRunningTime,
										std::string& message) {
	return setFloatAttribute("/Results", "CPU_RunningTime", cpuRunningTime,
							 message);
}


/* FUNCTION: getWallRunningTime */
int HDF5_SimResults::getWallRunningTime(float& wallRunningTime) const {
	return getFloatAttribute("/Results", "WallRunningTime", wallRunningTime);
}


/* FUNCTION: setWallRunningTime */
int HDF5_SimResults::setWallRunningTime(const float& wallRunningTime,
										std::string& message) {
	return setFloatAttribute("/Results", "WallRunningTime", wallRunningTime,
							 message);
}


/* FUNCTION: getFrameSetNames */
std::vector<std::string> HDF5_SimResults::getFrameSetNames() const {
    herr_t status;
	std::vector<std::string> keys;
	
	hid_t groupId = H5Gopen(fileId, "/Results/FrameSets");
	if (groupId > -1) {
		hsize_t numObjects;
		status = H5Gget_num_objs(groupId, &numObjects);
		if (status > -1) {
			char objectName[64];
			H5G_stat_t objectInfo;
			for (hsize_t index = 0; index < numObjects; index++) {
				H5Gget_objname_by_idx(groupId, index, objectName,
									  sizeof(objectName));
				H5Gget_objinfo(groupId, objectName, 0, &objectInfo);
				if (objectInfo.type == H5G_GROUP)
					keys.push_back(objectName);
			}
		}
		H5Gclose(groupId);
	}
	return keys;
}


/* FUNCTION: addFrameSet */
int HDF5_SimResults::addFrameSet(const char* name, std::string& message) {
    herr_t status;
	bool pathExists = false;
	int resultCode = 0;
	
	message = "Unable to add FrameSet: /Results/FrameSets/";
	message.append(name).append(": ");
	
	// Make sure Group path leading up to the Group we want to add exists
	//
	hid_t groupId = H5Gopen(fileId, "/Results");
	if (groupId > -1) {
		H5Gclose(groupId);
		pathExists = true;
		
	} else {
		groupId =
			H5Gcreate(fileId, "/Results", GROUP_NAME_SIZE_HINT);
		if (groupId > -1) {
			H5Gclose(groupId);
			pathExists = true;
		
		} else {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
	}
	
	if (pathExists) {
		pathExists = false;
		groupId = H5Gopen(fileId, "/Results/FrameSets");
		if (groupId > -1) {
			H5Gclose(groupId);
			pathExists = true;
			
		} else {
			groupId =
				H5Gcreate(fileId, "/Results/FrameSets", GROUP_NAME_SIZE_HINT);
			if (groupId > -1) {
				H5Gclose(groupId);
				pathExists = true;
				
			} else {
				// Get error description from HDF5
				std::string hdf5Message;
				status =
					H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
				if (status > -1)
					message.append(hdf5Message).append(".");
				resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			}
		}
	}
	
	if (pathExists) {
		// Create the frame set Group
		std::string frameSetGroup = "/Results/FrameSets/";
		frameSetGroup.append(name);
		groupId =
			H5Gcreate(fileId, frameSetGroup.c_str(), GROUP_NAME_SIZE_HINT);
		if (groupId > -1) {
			H5Gclose(groupId);
			FrameSetInfo frameSetInfo;
			frameSetInfoMap[std::string(name)] = frameSetInfo;
			
		} else {			
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
	}
	return resultCode;
}


/* FUNCTION: getAggregationMode */
int HDF5_SimResults::getAggregationMode(const char* frameSetName,
										int& mode) const {
	std::string groupName = "/Results/FrameSets/";
	groupName.append(frameSetName);
	
	return getIntAttribute(groupName.c_str(), "AggregationMode", mode);
}


/* FUNCTION: setAggregationMode */
int HDF5_SimResults::setAggregationMode(const char* frameSetName,
										const int& mode,
										std::string& message) {

	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	
	if (resultCode == 0) {
		std::string groupName = "/Results/FrameSets/";
		groupName.append(frameSetName);
		resultCode =
			setIntAttribute(groupName, "AggregationMode", mode, message);
	}
	return resultCode;
}


/* FUNCTION: getStepsPerFrame */
int HDF5_SimResults::getStepsPerFrame(const char* frameSetName,
									  int& stepsPerFrame) const {
	std::string groupName = "/Results/FrameSets/";
	groupName.append(frameSetName);
	
	return getIntAttribute(groupName.c_str(), "StepsPerFrame", stepsPerFrame);
									  }


/* FUNCTION: setStepsPerFrame */
int HDF5_SimResults::setStepsPerFrame(const char* frameSetName,
									  const int& stepsPerFrame,
									  std::string& message) {
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	
	if (resultCode == 0) {
		std::string groupName = "/Results/FrameSets/";
		groupName.append(frameSetName);
		resultCode =
			setIntAttribute(groupName, "StepsPerFrame", stepsPerFrame, message);
	}
	return resultCode;
}


/* FUNCTION: getFrameCount */
void HDF5_SimResults::getFrameCount(const char* frameSetName,
									int& frameCount) {
	frameCount = 0;
	
	// Check if the frame-set has been added
	std::string message;
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode == 0) {
			frameCount = frameSetInfoMap[frameSetName].currentFrameIndex + 1;
		}
	}
}


/* FUNCTION: getFrameTimes */
int HDF5_SimResults::getFrameTimes(const char* frameSetName, float* frameTimes,
								   std::string& message) {
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode == 0) {
			FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
			int frameCount = frameSetInfo.currentFrameIndex + 1;			
			for (int index = 0;
				 (index < frameCount) && (resultCode == 0);
				 index++)
				resultCode =
					readTimestamp(index, frameTimes[index],
								  frameSetInfo.timestampsDatasetId,
								  frameSetInfo.timestampsDataspaceId,
								  message);
		}
	}
	return resultCode;
}


/* FUNCTION: getFrameTime */
int HDF5_SimResults::getFrameTime(const char* frameSetName,
								  const int& frameIndex,
								  float& time, std::string& message) {
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode == 0) {
			FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
			// Check that the given frameIndex is valid
			if (frameSetInfo.currentFrameIndex >= frameIndex) {
				resultCode =
				readTimestamp(frameIndex, time,
							  frameSetInfo.timestampsDatasetId,
							  frameSetInfo.timestampsDataspaceId,
							  message);
				
			} else {
				message = "Invalid frameIndex.";
				resultCode = SRDS_INVALID_FRAMEINDEX;
			}
		}
	}
	return resultCode;
}


/* FUNCTION: addFrame */
int HDF5_SimResults::addFrame(const char* frameSetName, const float& time,
							  int& frameIndex, std::string& message) {
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
		
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode != 0) {
			// Create it
			//
			hid_t datasetId, dataspaceId;
			std::string datasetMessage;
			resultCode =
				createTimestampsDataset(frameSetName,
										datasetId, dataspaceId,
										datasetMessage);
			
			if (resultCode != 0) {
				message = "Unable to add Frame to /Results/FrameSets/";
				message.append(frameSetName).append(": ");
				message.append(datasetMessage);
				
			} else {
				frameSetInfo.timestampsDatasetId = datasetId;
				frameSetInfo.timestampsDataspaceId = dataspaceId;
			}
			
		} else {
			frameSetInfo.currentFrameIndex++;
		}
		
		if (resultCode == 0) { // Timestamp dataset exists
			resultCode =
				writeTimestamp(frameSetInfo.currentFrameIndex, time,
							   frameSetInfo.timestampsDatasetId,
							   frameSetInfo.timestampsDataspaceId, message);
			if (resultCode < 0)
				frameSetInfo.currentFrameIndex--;
		}
		frameIndex = frameSetInfo.currentFrameIndex;
	}
	return resultCode;
}


/* FUNCTION: getFrameAtomIdsCount */
void HDF5_SimResults::getFrameAtomIdsCount(const char* frameSetName,
										   unsigned int& atomIdsCount) {
	atomIdsCount = 0;
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	std::string message;
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		// Check if the atomIds have already been set
		resultCode =
			checkFrameSetDatasetExistence(frameSetName,
										  frameSetInfo.atomIdsDatasetId,
										  frameSetInfo.atomIdsDataspaceId,
										  "AtomPositions",
										  message);
		if (resultCode == 0) {
			atomIdsCount =
				H5Sget_simple_extent_npoints(frameSetInfo.atomIdsDataspaceId);
		}
	}
}


/* FUNCTION: getFrameAtomIds */
int HDF5_SimResults::getFrameAtomIds(const char* frameSetName,
									 unsigned int* atomIds,
									 std::string& message) {
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		// Check if the atomIds have already been set
		resultCode =
			checkFrameSetDatasetExistence(frameSetName,
										  frameSetInfo.atomIdsDatasetId,
										  frameSetInfo.atomIdsDataspaceId,
										  "AtomPositions",
										  message);
		if (resultCode == 0) {
			herr_t status;
			
			// Get the filespace
			hid_t filespace = H5Dget_space(frameSetInfo.atomIdsDatasetId);
			
			// Read the atom identifiers
			status =
				H5Dread(frameSetInfo.atomIdsDatasetId, H5T_NATIVE_UINT,
						frameSetInfo.atomIdsDataspaceId, filespace, H5P_DEFAULT,
						atomIds);
			H5Sclose(filespace);
			
			if (status < 0) {
				message = "Unable to read atom ids: ";
				
				// Get error description from HDF5
				std::string hdf5Message;
				status =
					H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
				if (status > -1)
					message.append(hdf5Message).append(".");
				resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			}
		}
	}
	return resultCode;
}


/* FUNCTION: setFrameAtomIds */
int HDF5_SimResults::setFrameAtomIds(const char* frameSetName,
									 unsigned int* atomIds,
									 const unsigned int& atomIdsCount,
									 std::string& message) {
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists

		// Check if the atomIds have already been set (can only set them once).
		resultCode =
			checkFrameSetDatasetExistence(frameSetName,
										  frameSetInfo.atomIdsDatasetId,
										  frameSetInfo.atomIdsDataspaceId,
										  "AtomPositions",
										  message);
		if (resultCode == 0) {
			message = "Atom ids have already been set.";
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			
		} else {
			resultCode = 0;
			herr_t status;
			
			// Create the dataspace
			hsize_t dims[1] = { atomIdsCount };
			hid_t dataspaceId =
				H5Screate_simple(1,		// rank
								 dims,	// dimensions
								 NULL);	// max dimensions
			
			// Modify dataset creation properties, i.e. enable chunking,
			// compression
			hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
			if (USE_CHUNKING) {
				hsize_t chunkDims[1] = { atomIdsCount };
				status = H5Pset_chunk(datasetParams, 1 /* rank */, chunkDims);
			}
			if (USE_SHUFFLING) {
				status = H5Pset_shuffle(datasetParams);
			}
			if (USE_COMPRESSION) {
				status = H5Pset_deflate(datasetParams, COMPRESSION_LVL);
			}
			
			// Create a new dataset within the file using datasetParams creation
			// properties.
			std::string groupName = "/Results/FrameSets/";
			groupName.append(frameSetName).append("/AtomIds");
			hid_t datasetId =
				H5Dcreate(fileId, groupName.c_str(), H5T_NATIVE_UINT,
						  dataspaceId, datasetParams);
			H5Pclose(datasetParams);
			if (datasetId < 0) {
				message =
					"Unable to create the atom ids dataset for /Results/FrameSets/";
				message.append(frameSetName).append(": ");
				
				// Get error description from HDF5
				std::string hdf5Message;
				status =
					H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
				if (status > -1)
					message.append(hdf5Message).append(".");
				resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
				
			} else {
				// Write the atom identifiers
				hid_t filespace = H5Dget_space(datasetId);
				status =
					H5Dwrite(datasetId, H5T_NATIVE_UINT, dataspaceId, filespace,
							 H5P_DEFAULT, atomIds);
				H5Sclose(filespace);
				if (status == 0) {
					frameSetInfo.atomIdsDatasetId = datasetId;
					frameSetInfo.atomIdsDataspaceId = dataspaceId;
					
				} else {
					H5Dclose(datasetId);
					H5Sclose(dataspaceId);
				}
			}
		}
	}
	return resultCode;
}


/* FUNCTION: setFrameAtomPositions */
int HDF5_SimResults::setFrameAtomPositions(const char* frameSetName,
										   const int& frameIndex,
										   float* positions,
										   const unsigned int& atomCount,
										   std::string& message) {
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode == 0) {
			
			// Check if the requested frame has already been added
			if (frameIndex > frameSetInfo.currentFrameIndex) {
				message = "Requested frame hasn't been added.";
				resultCode = SRDS_INVALID_FRAMEINDEX;
				
			} else {
				// Check if the atom positions dataset has been created
				resultCode =
					checkFrameSetDatasetExistence
						(frameSetName,
						 frameSetInfo.atomPositionsDatasetId,
						 frameSetInfo.atomPositionsDataspaceId,
						 "AtomPositions",
						 message);
				
				if (resultCode != 0) {
					// Create it
					resultCode =
						create3D_AtomFloatsDataset
							(frameSetName,
							 "AtomPositions",
							 atomCount,
							 frameSetInfo.atomPositionsDatasetId,
							 frameSetInfo.atomPositionsDataspaceId,
							 message);
				}
			}
		}
	}
	
	if (resultCode == 0) {
		//resultCode = write3SpaceAtomFloats();
	}
	return resultCode;
}


/******************************************************************************/


/* FUNCTION: checkFrameSetDatasetExistence
*
* Assumes the frame-set exists, ie, doesn't check for it.
*
* @param message Set to a description of the problem if non-zero is returned
* @return zero=AtomPositions dataset exists, non-zero=AtomPositions dataset
*			doesn't exist
*/
int HDF5_SimResults::checkFrameSetDatasetExistence(const char* frameSetName,
												   hid_t& datasetId,
												   hid_t& dataspaceId,
												   const char* datasetName,
												   std::string& message) {
	int resultCode = 0;
	
	// Check if the AtomPositions dataset has been created
	if (datasetId == 0) {
		
		// Check if some other object created the dataset			
		std::string fullDatasetName = "/Results/FrameSets/";
		fullDatasetName.append(frameSetName).append("/").append(datasetName);
		datasetId = H5Dopen(fileId, fullDatasetName.c_str());
		if (datasetId > -1) {
			// Exists
			dataspaceId = H5Dget_space(datasetId);
			
		} else {
			datasetId = dataspaceId = 0;
			message = "Dataset: ";
			message.append(fullDatasetName).append(" doesn't exist.");
			resultCode = SRDS_NON_EXISTENT_DATASET;
		}
	}
	return resultCode;
}


/* FUNCTION: checkTimestampsExistence
 *
 * Assumes the frame-set exists, ie, doesn't check for it.
 *
 * @param message Set to a description of the problem if non-zero is returned
 * @return zero=Timestamps dataset exists, non-zero=Timestamps dataset doesn't
 *			exist
 */
int HDF5_SimResults::checkTimestampsExistence(const char* frameSetName,
											  std::string& message) {
	int resultCode = 0;
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the Timestamps dataset has been created
	if (frameSetInfo.timestampsDatasetId == 0) {
		
		// Check if some other object created the dataset			
		std::string datasetName = "/Results/FrameSets/";
		datasetName.append(frameSetName).append("/Timestamps");
		hid_t datasetId = H5Dopen(fileId, datasetName.c_str());
		if (datasetId > -1) {
			// Exists
			frameSetInfo.timestampsDatasetId = datasetId;
			frameSetInfo.timestampsDataspaceId = H5Dget_space(datasetId);
			frameSetInfo.currentFrameIndex =
				H5Sget_simple_extent_npoints
					(frameSetInfo.timestampsDataspaceId);
			// Current frame index starts at zero, so if there's two frames,
			// the current frame index is 1.
			if (frameSetInfo.currentFrameIndex > 0)
				frameSetInfo.currentFrameIndex--;
			
		} else {
			message = "Frame-set: ";
			message.append(frameSetName).append(" has no frames.");
			resultCode = SRDS_EMPTY_FRAMESET;
		}
	}
	return resultCode;
}


/* FUNCTION: checkFrameSetExistence */
int HDF5_SimResults::checkFrameSetExistence(const char* frameSetName,
											std::string& message) {
	int resultCode = 0;
	
	// First check in cache
	if (frameSetInfoMap.count(std::string(frameSetName)) == 0) {
		// Check if the frame-set was added from some other object
		std::string groupName = "/Results/FrameSets/";
		groupName.append(frameSetName);
		hid_t groupId = H5Gopen(fileId, groupName.c_str());
		if (groupId > -1) {
			// Exists
			H5Gclose(groupId);
			FrameSetInfo frameSetInfo;
			frameSetInfoMap[std::string(frameSetName)] = frameSetInfo;
			
		} else {
			message = "Frame-set: ";
			message.append(frameSetName).append(" doesn't exist.");
			resultCode = SRDS_NON_EXISTENT_FRAMESET;
		}
	}
	return resultCode;
}


/* FUNCTION: create3D_AtomFloatsDataset
*
* Assumes the frame-set already exists, ie, doesn't check if it exists.
*/
int HDF5_SimResults::create3D_AtomFloatsDataset(const char* frameSetName,
												const char* dataSetName,
												const unsigned int& atomCount,
												hid_t& datasetId,
												hid_t& dataspaceId,
												std::string& message) {
    herr_t status;
	int resultCode = 0;
	
	// Create the dataspace
    hsize_t	dims[3] = { atomCount, 3, 1 };
    hsize_t	maxDims[3] = { atomCount, 3, H5S_UNLIMITED };
    dataspaceId = H5Screate_simple(3 /* rank */, dims, maxDims);
	
    // Modify dataset creation properties, i.e. enable chunking, compression
    hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
	if (USE_CHUNKING) {
		hsize_t	chunkDims[3] = { atomCount, 3, 1 };
		status = H5Pset_chunk(datasetParams, 3 /* rank */, chunkDims);
	}
	if (USE_SHUFFLING) {
		status = H5Pset_shuffle(datasetParams);
	}
	if (USE_COMPRESSION) {
		status = H5Pset_deflate(datasetParams, COMPRESSION_LVL);
	}
	
    // Create a new dataset within the file using datasetParams creation
	// properties.
	std::string fullDatasetName = "/Results/FrameSets/";
	fullDatasetName.append(frameSetName).append("/").append(dataSetName);
    datasetId =
		H5Dcreate(fileId, fullDatasetName.c_str(), H5T_NATIVE_FLOAT,
				  dataspaceId, datasetParams);
    H5Pclose(datasetParams);
	
	if (datasetId < 0) {
		message = "Unable to create dataset: ";
		message.append(fullDatasetName).append(": ");
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	return resultCode;
}
	

/* FUNCTION: createTimestampsDataset
 *
 * Assumes the frame-set already exists, ie, doesn't check if it exists.
 */
int HDF5_SimResults::createTimestampsDataset(const char* frameSetName,
											 hid_t& datasetId,
											 hid_t& dataspaceId,
											 std::string& message) {
    herr_t status;
	int resultCode = 0;

	// Create the dataspace
    hsize_t	dims[1] = { 1 };
    hsize_t	maxDims[1] = { H5S_UNLIMITED };
    dataspaceId = H5Screate_simple(1 /* rank */, dims, maxDims);
	
    // Modify dataset creation properties, i.e. enable chunking, compression
    hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
	if (USE_CHUNKING) {
		hsize_t	chunkDims[1] = { 1 };
		status = H5Pset_chunk(datasetParams, 1 /* rank */, chunkDims);
	}
	if (USE_SHUFFLING) {
		status = H5Pset_shuffle(datasetParams);
	}
	if (USE_COMPRESSION) {
		status = H5Pset_deflate(datasetParams, COMPRESSION_LVL);
	}
	
    // Create a new dataset within the file using datasetParams creation
	// properties.
	std::string datasetName = "/Results/FrameSets/";
	datasetName.append(frameSetName).append("/Timestamps");
    datasetId =
		H5Dcreate(fileId, datasetName.c_str(), H5T_NATIVE_FLOAT,
				  dataspaceId, datasetParams);
    H5Pclose(datasetParams);
	
	if (datasetId < 0) {
		message = "Unable to create dataset: ";
		message.append(datasetName).append(": ");
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	return resultCode;
}


/* FUNCTION: writeTimestamp */
int HDF5_SimResults::writeTimestamp(int frame, const float& time,
									hid_t datasetId, hid_t dataspaceId,
									std::string& message) {
    herr_t	status;
	int resultCode = 0;
	float data[1] = { time };
	
	// Extend the dataset.
    hsize_t	dims[1] = { frame + 1 };
	status = H5Dextend(datasetId, dims);
	
	// Select a hyperslab.
	hid_t filespace = H5Dget_space(datasetId);
	hsize_t slabStart[1] = { frame };
	hsize_t slabStride[1] = { 1 };
	hsize_t slabCount[1] = { 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	
	// Write the data to the hyperslab.
	status =
		H5Dwrite(datasetId, H5T_NATIVE_FLOAT, dataspaceId, filespace,
				 H5P_DEFAULT, data);
    H5Sclose(filespace);
	
	if (status < 0) {
		message = "Unable to write timestamp: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	return resultCode;
}


/* FUNCTION: readTimestamp */
int HDF5_SimResults::readTimestamp(int frame, float& time,
								   hid_t datasetId, hid_t dataspaceId,
								   std::string& message) const {
    herr_t	status;
	int resultCode = 0;
	
	// Get the filespace
	hid_t filespace = H5Dget_space(datasetId);
	
	// Select a hyperslab.
	hsize_t slabStart[1] = { frame };
	hsize_t slabStride[1] = { 1 };
	hsize_t slabCount[1] = { 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	// Read data
	float data[1];
	status =
		H5Dread(datasetId, H5T_NATIVE_FLOAT, dataspaceId, filespace,
				H5P_DEFAULT, data);
    H5Sclose(filespace);
	
	if (status < 0) {
		message = "Unable to read timestamp: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		
	} else {
		time = data[0];
	}
	return resultCode;
}


/* FUNCTION: getStringAttribute */
int HDF5_SimResults::getStringAttribute(const std::string& groupName,
										const std::string& attributeName,
										std::string& attributeValue) const {
	int resultCode = 1;
    herr_t status;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId > -1) {
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId > -1) {
			// Create the type
			hid_t stringType = H5Tcopy(H5T_C_S1);
			status = H5Tset_size(stringType, H5T_VARIABLE);
			
			// Read the attribute
			char* value;
			status = H5Aread(attributeId, stringType, &value);
			if (status > -1) {
				attributeValue = value;
				free(value);
				resultCode = 0;
			}
		}
		H5Aclose(attributeId);
	}
	H5Gclose(groupId);
	
	return resultCode;
}


/* FUNCTION: setStringAttribute */
int HDF5_SimResults::setStringAttribute(const std::string& groupName,
										const std::string& attributeName,
										const std::string& value,
										std::string& message) {
	int resultCode = 0;
    herr_t status;
	
	// Prepare error message
	message = "Unable to set ";
	message.append(groupName).append("/").append(attributeName);
	message.append("=").append(value).append(": ");
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId < 0) {
		// Doesn't exist, create it
		groupId = H5Gcreate(fileId, groupName.c_str(), GROUP_NAME_SIZE_HINT);
		if (groupId < 0) {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
	}
	
	if (resultCode == 0) {
		// Create the type
		hid_t stringType = H5Tcopy(H5T_C_S1);
		status = H5Tset_size(stringType, H5T_VARIABLE);
		
		// Create the dataspace
		hid_t dataspaceId = H5Screate(H5S_SCALAR);
		
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId < 0)
			// Doesn't exist, create it
			attributeId =
				H5Acreate(groupId, attributeName.c_str(), stringType,
						  dataspaceId, H5P_DEFAULT);
		
		// Write the attribute
		char* valueChars = (char*)(malloc((value.length()+1)*sizeof(char)));
		strcpy(valueChars, value.c_str());
		status = H5Awrite(attributeId, stringType, &valueChars);
		free(valueChars);
		if (status < 0) {		
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
		H5Aclose(attributeId);
		H5Sclose(dataspaceId);
		H5Gclose(groupId);
	}
	return resultCode;
}


/* FUNCTION: getIntAttribute */
int HDF5_SimResults::getIntAttribute(const std::string& groupName,
									 const std::string& attributeName,
									 int& attributeValue) const {
	int resultCode = 1;
    herr_t status;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId > -1) {
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId > -1) {
			// Read the attribute
			int value;
			status = H5Aread(attributeId, H5T_NATIVE_INT, &value);
			if (status > -1) {
				attributeValue = value;
				resultCode = 0;
			}
		}
		H5Aclose(attributeId);
	}
	H5Gclose(groupId);
	
	return resultCode;
}


/* FUNCTION: setIntAttribute */
int HDF5_SimResults::setIntAttribute(const std::string& groupName,
									 const std::string& attributeName,
									 const int& value,
									 std::string& message) {
	int resultCode = 0;
    herr_t status;
	
	// Prepare error message
	message = "Unable to set ";
	message.append(groupName).append("/").append(attributeName);
	char buffer[20];
	sprintf(buffer, "%d", value);
	message.append("=").append(buffer).append(": ");
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId < 0) {
		// Doesn't exist, create it
		groupId = H5Gcreate(fileId, groupName.c_str(), GROUP_NAME_SIZE_HINT);
		if (groupId < 0) {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
	}
	
	if (resultCode == 0) {
		// Create the dataspace
		hid_t dataspaceId = H5Screate(H5S_SCALAR);
		
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId < 0)
			// Doesn't exist, create it
			attributeId =
				H5Acreate(groupId, attributeName.c_str(), H5T_NATIVE_INT,
						  dataspaceId, H5P_DEFAULT);
		
		// Write the attribute
		status = H5Awrite(attributeId, H5T_NATIVE_INT, &value);
		if (status < 0) {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
		H5Aclose(attributeId);
		H5Sclose(dataspaceId);
		H5Gclose(groupId);
	}
	return resultCode;
}


/* FUNCTION: getFloatAttribute */
int HDF5_SimResults::getFloatAttribute(const std::string& groupName,
									   const std::string& attributeName,
									   float& attributeValue) const {
	int resultCode = 1;
    herr_t status;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId > -1) {
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId > -1) {
			// Read the attribute
			float value;
			status = H5Aread(attributeId, H5T_NATIVE_FLOAT, &value);
			if (status > -1) {
				attributeValue = value;
				resultCode = 0;
			}
		}
		H5Aclose(attributeId);
	}
	H5Gclose(groupId);
	
	return resultCode;
}


/* FUNCTION: setFloatAttribute */
int HDF5_SimResults::setFloatAttribute(const std::string& groupName,
									   const std::string& attributeName,
									   const float& value,
									   std::string& message) {
	int resultCode = 0;
    herr_t status;
	
	// Prepare error message
	message = "Unable to set ";
	message.append(groupName).append("/").append(attributeName);
	char buffer[20];
	sprintf(buffer, "%f", value);
	message.append("=").append(buffer).append(": ");
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId < 0) {
		// Doesn't exist, create it
		groupId = H5Gcreate(fileId, groupName.c_str(), GROUP_NAME_SIZE_HINT);
		if (groupId < 0) {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
	}
		
	if (resultCode == 0) {
		// Create the dataspace
		hid_t dataspaceId = H5Screate(H5S_SCALAR);
		
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId < 0)
			// Doesn't exist, create it
			attributeId =
				H5Acreate(groupId, attributeName.c_str(), H5T_NATIVE_FLOAT,
						  dataspaceId, H5P_DEFAULT);
		
		// Write the attribute
		status = H5Awrite(attributeId, H5T_NATIVE_FLOAT, &value);
		if (status < 0) {
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		}
		H5Aclose(attributeId);
		H5Sclose(dataspaceId);
		H5Gclose(groupId);
	}	
	return resultCode;
}


/* FUNCTION: getTimeAttribute */
int HDF5_SimResults::getTimeAttribute(const std::string& groupName,
									   const std::string& attributeName,
									   time_t& attributeValue) const {
	int resultCode = 1;
    herr_t status;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId > -1) {
		// See if the attribute exists and open it
		hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
		if (attributeId > -1) {
			// Read the attribute
			time_t value;
			status = H5Aread(attributeId, H5T_UNIX_D32BE, &value);
			if (status > -1) {
				attributeValue = value;
				resultCode = 0;
			}
		}
		H5Aclose(attributeId);
	}
	H5Gclose(groupId);
	
	return resultCode;
}


/* FUNCTION: setTimeAttribute */
int HDF5_SimResults::setTimeAttribute(const std::string& groupName,
									  const std::string& attributeName,
									  const time_t& value,
									  std::string& message) {
	int resultCode = 0;
    herr_t status;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId < 0) {
		// Doesn't exist, create it
		groupId = H5Gcreate(fileId, groupName.c_str(), GROUP_NAME_SIZE_HINT);
	}
	
	// Create the dataspace
	hid_t dataspaceId = H5Screate(H5S_SCALAR);
	
	// See if the attribute exists and open it
	hid_t attributeId = H5Aopen_name(groupId, attributeName.c_str());
	if (attributeId < 0)
		// Doesn't exist, create it
		attributeId =
			H5Acreate(groupId, attributeName.c_str(), H5T_UNIX_D32BE,
					  dataspaceId, H5P_DEFAULT);
	
	// Write the attribute
	status = H5Awrite(attributeId, H5T_UNIX_D32BE, &value);
	if (status < 0) {
		message = "Unable to set ";
		message.append(groupName).append("/").append(attributeName);

		struct tm timestamp;
		char buffer[64];
		timestamp = *localtime(&value);
		strftime(buffer, sizeof(buffer), "%a %Y-%m-%d %H:%M:%S %Z", &timestamp);
		message.append("=").append(buffer).append(": ");

		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	
	// Clean up
	H5Aclose(attributeId);
	H5Sclose(dataspaceId);
	H5Gclose(groupId);
	
	return resultCode;
}

} // ne1::
