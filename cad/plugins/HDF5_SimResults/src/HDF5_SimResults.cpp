
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include <string.h>
#include "Nanorex/HDF5_SimResults.h"

namespace Nanorex {


/* FUNCTION: H5_ErrorStackWalker */
herr_t H5_ErrorStackWalker(int position, H5E_error_t* errorDesc,
						   void* hdf5Message) {
	if (((std::string*)hdf5Message)->length() == 0)
		((std::string*)hdf5Message)->append(errorDesc->desc);
	
	return 0;
}


/* CONSTRUCTOR */
HDF5_SimResults::HDF5_SimResults() {
	H5open();
	
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
	if (fileId != 0) {
		closeDatasets();
		H5Fclose(fileId);
	}
	H5close();
}


/* FUNCTION: closeDatasets */
void HDF5_SimResults::closeDatasets() {
	std::map<std::string, FrameSetInfo>::iterator iter =
		frameSetInfoMap.begin();
	while (iter != frameSetInfoMap.end()) {
		H5Dclose(((*iter).second).timestampsDatasetId);
		H5Dclose(((*iter).second).atomIdsDatasetId);
		H5Dclose(((*iter).second).atomicNumbersDatasetId);
		H5Dclose(((*iter).second).atomPositionsDatasetId);
		H5Dclose(((*iter).second).atomVelocitiesDatasetId);
		H5Dclose(((*iter).second).bondsDatasetId);
		H5Dclose(((*iter).second).measurementsDatasetId);
		iter++;
	}
}


/* FUNCTION: openDataStore */
int HDF5_SimResults::openDataStore(const char* directory,
								   std::string& message) {
	int resultCode = 0;
	
	if (directory != 0) {
		dataStoreDirectory = directory;
		
	} else {
		resultCode = SRDS_UNABLE_TO_OPEN_FILE;
		message = "Null passed for directory.";
		
		// Abort
		return resultCode;
	}
	
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
		
	} else {
		openDatasets();
	}
	return resultCode;
}


/* FUNCTION: synchronize */
void HDF5_SimResults::synchronize() {
	closeDatasets();
	H5Fclose(fileId);
	std::string datastoreFilename = dataStoreDirectory;
	datastoreFilename.append("/").append(HDF5_SIM_RESULT_FILENAME);
	fileId = H5Fopen(datastoreFilename.c_str(), H5F_ACC_RDWR, H5P_DEFAULT);
	openDatasets();
}


/* FUNCTION: flush */
void HDF5_SimResults::flush() {
	int resultCode = H5Fflush(fileId, H5F_SCOPE_GLOBAL);
	if (resultCode)
		;//message = "Couldn't flush HDF5 file.";
}


/* FUNCTION: openDatasets */
void HDF5_SimResults::openDatasets() {
	FrameSetInfo frameSetInfo;
	frameSetInfo.timestampsDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/Timestamps");
	if (frameSetInfo.timestampsDatasetId < 0)
		frameSetInfo.timestampsDatasetId = 0;
	
	// Determine current frame index
	hid_t dataspaceId = H5Dget_space(frameSetInfo.timestampsDatasetId);
	int frameCount = H5Sget_simple_extent_npoints(dataspaceId);
	H5Sclose(dataspaceId);
	frameCount--; // frame indexes start at 0
	if (frameCount < 0)
		frameCount = 0;	
	frameSetInfo.currentFrameIndex = frameCount;
		
	frameSetInfo.atomIdsDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/AtomIds");
	if (frameSetInfo.atomIdsDatasetId < 0)
		frameSetInfo.atomIdsDatasetId = 0;
	frameSetInfo.atomicNumbersDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/AtomicNumbers");
	if (frameSetInfo.atomicNumbersDatasetId < 0)
		frameSetInfo.atomicNumbersDatasetId = 0;
	frameSetInfo.atomPositionsDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/AtomPositions");
	if (frameSetInfo.atomPositionsDatasetId < 0)
		frameSetInfo.atomPositionsDatasetId = 0;
	frameSetInfo.atomVelocitiesDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/AtomVelocities");
	if (frameSetInfo.atomVelocitiesDatasetId < 0)
		frameSetInfo.atomVelocitiesDatasetId = 0;
	frameSetInfo.bondsDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/Bonds");
	if (frameSetInfo.bondsDatasetId < 0)
		frameSetInfo.bondsDatasetId = 0;
	frameSetInfo.measurementsDatasetId =
		H5Dopen(fileId, "/Results/FrameSets/frame-set-1/Measurements");
	if (frameSetInfo.measurementsDatasetId < 0)
		frameSetInfo.measurementsDatasetId = 0;
	
	frameSetInfoMap[std::string("frame-set-1")] = frameSetInfo;
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


/* FUNCTION: getIntParameterKeys */
std::vector<std::string> HDF5_SimResults::getIntParameterKeys() const {
	return getGroupKeys("/Parameters-Ints");
}


/* FUNCTION: getIntParameter */
int HDF5_SimResults::getIntParameter(const std::string& key, int& value) const {
	return getIntAttribute("/Parameters-Ints", key, value);
}


/* FUNCTION: setIntParameter */
int HDF5_SimResults::setIntParameter(const std::string& key, int value,
									 std::string& message) {
	return setIntAttribute("/Parameters-Ints", key, value, message);
}


/* FUNCTION: getFloatParameterKeys */
std::vector<std::string> HDF5_SimResults::getFloatParameterKeys() const {
	return getGroupKeys("/Parameters-Floats");
}


/* FUNCTION: getFloatParameter */
int HDF5_SimResults::getFloatParameter(const std::string& key,
									   float& value) const {
	return getFloatAttribute("/Parameters-Floats", key, value);
}


/* FUNCTION: setFloatParameter */
int HDF5_SimResults::setFloatParameter(const std::string& key, float value,
									   std::string& message) {
	return setFloatAttribute("/Parameters-Floats", key, value, message);
}


/* FUNCTION: getStringParameterKeys */
std::vector<std::string> HDF5_SimResults::getStringParameterKeys() const {
	return getGroupKeys("/Parameters-Strings");
}


/* FUNCTION: getStringParameter */
int HDF5_SimResults::getStringParameter(const std::string& key,
										std::string& value) const {
	return getStringAttribute("/Parameters-Strings", key, value);
}


/* FUNCTION: setStringParameter */
int HDF5_SimResults::setStringParameter(const std::string& key,
										const std::string& value,
										std::string& message) {
	return setStringAttribute("/Parameters-Strings", key, value, message);
}


/* FUNCTION: getFilePathKeys */
std::vector<std::string> HDF5_SimResults::getFilePathKeys() const {
	return getGroupKeys("/InputFilePaths");
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



/* FUNCTION: getIntResultKeys */
std::vector<std::string> HDF5_SimResults::getIntResultKeys() const {
	return getGroupKeys("/Results-Ints");
}


/* FUNCTION: getIntResult */
int HDF5_SimResults::getIntResult(const std::string& key, int& value) const {
	return getIntAttribute("/Results-Ints", key, value);
}


/* FUNCTION: setIntResult */
int HDF5_SimResults::setIntResult(const std::string& key, int value,
									 std::string& message) {
	return setIntAttribute("/Results-Ints", key, value, message);
}


/* FUNCTION: getFloatResultKeys */
std::vector<std::string> HDF5_SimResults::getFloatResultKeys() const {
	return getGroupKeys("/Results-Floats");
}


/* FUNCTION: getFloatResult */
int HDF5_SimResults::getFloatResult(const std::string& key,
									   float& value) const {
	return getFloatAttribute("/Results-Floats", key, value);
}


/* FUNCTION: setFloatResult */
int HDF5_SimResults::setFloatResult(const std::string& key, float value,
									   std::string& message) {
	return setFloatAttribute("/Results-Floats", key, value, message);
}


/* FUNCTION: getStringResultKeys */
std::vector<std::string> HDF5_SimResults::getStringResultKeys() const {
	return getGroupKeys("/Results-Strings");
}


/* FUNCTION: getStringResult */
int HDF5_SimResults::getStringResult(const std::string& key,
										std::string& value) const {
	return getStringAttribute("/Results-Strings", key, value);
}


/* FUNCTION: setStringResult */
int HDF5_SimResults::setStringResult(const std::string& key,
										const std::string& value,
										std::string& message) {
	return setStringAttribute("/Results-Strings", key, value, message);
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
		if (resultCode == 0)
			frameCount = frameSetInfoMap[frameSetName].currentFrameIndex + 1;
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
								  message);
		}
	}
	return resultCode;
}


/* FUNCTION: getFrameTime */
int HDF5_SimResults::getFrameTime(const char* frameSetName,
								  const int& frameIndex,
								  float& time, std::string& message) {
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
		resultCode =
			readTimestamp(frameIndex, time,
						  frameSetInfo.timestampsDatasetId,
						  message);
	}
	return resultCode;
}


/* FUNCTION: addFrame */
int HDF5_SimResults::addFrame(const char* frameSetName, const float& time,
							  int& frameIndex, std::string& message) {
	int resultCode;
	
	// We flush buffers here assuming that the previous frame must be mostly
	// complete if the caller is adding a new frame.
	//
	resultCode = H5Fflush(fileId, H5F_SCOPE_GLOBAL);
	if (resultCode)
		message = "Couldn't flush HDF5 file.";
	
	
	// Check if the frame-set has been added
	resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
		
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode != 0) {
			// Create it
			//
			hid_t datasetId;
			std::string datasetMessage;
			resultCode =
				createTimestampsDataset(frameSetName, datasetId,
										datasetMessage);
			
			if (resultCode != 0) {
				message = "Unable to add Frame to /Results/FrameSets/";
				message.append(frameSetName).append(": ");
				message.append(datasetMessage);
				
			} else {
				frameSetInfo.timestampsDatasetId = datasetId;
			}
			
		} else {
			frameSetInfo.currentFrameIndex++;
		}
		
		if (resultCode == 0) { // Timestamp dataset exists
			resultCode =
				writeTimestamp(frameSetInfo.currentFrameIndex, time,
							   frameSetInfo.timestampsDatasetId, message);
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
										  "AtomIds",
										  message);
		if (resultCode == 0) {
			hid_t dataspaceId = H5Dget_space(frameSetInfo.atomIdsDatasetId);
			atomIdsCount = H5Sget_simple_extent_npoints(dataspaceId);
			H5Sclose(dataspaceId);
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
										  "AtomIds",
										  message);
		if (resultCode == 0) {
			herr_t status;
			
			// Read the atom identifiers
			status =
				H5Dread(frameSetInfo.atomIdsDatasetId, H5T_NATIVE_UINT,
						H5S_ALL, H5S_ALL, H5P_DEFAULT,
						atomIds);
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
									 const unsigned int* atomIds,
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
										  "AtomIds",
										  message);
		if (resultCode == 0) {
			message = "Atom ids have already been set.";
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			
		} else {
			hid_t datasetId;
			resultCode =
				writeAtomUInts(frameSetName, "AtomIds", atomIds,
							   atomIdsCount, datasetId, message);
			if (resultCode == 0)
				frameSetInfo.atomIdsDatasetId = datasetId;
		}
	}
	return resultCode;
}
	

/* FUNCTION: getFrameAtomicNumbers */
int HDF5_SimResults::getFrameAtomicNumbers(const char* frameSetName,
										   unsigned int* atomicNumbers,
										   std::string& message) {
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
						   // Check if the atomIds have already been set
		resultCode =
		checkFrameSetDatasetExistence(frameSetName,
									  frameSetInfo.atomicNumbersDatasetId,
									  "AtomNumbers",
									  message);
		if (resultCode == 0) {
			herr_t status;
			
			// Read the atomic numbers
			status =
				H5Dread(frameSetInfo.atomicNumbersDatasetId, H5T_NATIVE_UINT,
						H5S_ALL, H5S_ALL, H5P_DEFAULT,
						atomicNumbers);
			if (status < 0) {
				message = "Unable to read atomic numbers: ";
				
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


/* FUNCTION: setFrameAtomicNumbers */
int HDF5_SimResults::setFrameAtomicNumbers(const char* frameSetName,
										   const unsigned int* atomicNumbers,
										   const unsigned int& atomicNumbersCount,
										   std::string& message) {
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		
		// Check if the atomic numbers have already been set (can only set them
		// once).
		resultCode =
		checkFrameSetDatasetExistence(frameSetName,
									  frameSetInfo.atomicNumbersDatasetId,
									  "AtomicNumbers",
									  message);
		if (resultCode == 0) {
			message = "Atomic numbers have already been set.";
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			
		} else {
			hid_t datasetId;
			resultCode =
				writeAtomUInts(frameSetName, "AtomicNumbers", atomicNumbers,
							   atomicNumbersCount, datasetId, message);
			if (resultCode == 0)
				frameSetInfo.atomicNumbersDatasetId = datasetId;
		}
	}
	return resultCode;
}


/* FUNCTION: getFrameAtomPositions */
int HDF5_SimResults::getFrameAtomPositions(const char* frameSetName,
										   const int& frameIndex,
										   const unsigned int& atomCount,
										   float* positions,
										   std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the atom positions dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.atomPositionsDatasetId,
				 "AtomPositions",
				 message);
	}
	
	if (resultCode == 0) {
		resultCode =
			read3SpaceAtomFloats(frameIndex, atomCount, positions,
								 frameSetInfo.atomPositionsDatasetId,
								 message);
	}
	return resultCode;
}


/* FUNCTION: setFrameAtomPositions */
int HDF5_SimResults::setFrameAtomPositions(const char* frameSetName,
										   const int& frameIndex,
										   const float* positions,
										   const unsigned int& atomCount,
										   std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the atom positions dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.atomPositionsDatasetId,
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
					 message);
		}
	}
	
	if (resultCode == 0) {
		resultCode =
			write3SpaceAtomFloats(frameIndex, atomCount, positions,
								  frameSetInfo.atomPositionsDatasetId,
								  message);
	}
	return resultCode;
}


/* FUNCTION: getFrameAtomVelocities */
int HDF5_SimResults::getFrameAtomVelocities(const char* frameSetName,
											const int& frameIndex,
											const unsigned int& atomCount,
											float* velocities,
											std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the atom velocities dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.atomVelocitiesDatasetId,
				 "AtomVelocities",
				 message);
	}
	
	if (resultCode == 0) {
		resultCode =
			read3SpaceAtomFloats(frameIndex, atomCount, velocities,
								 frameSetInfo.atomVelocitiesDatasetId,
								 message);
	}
	return resultCode;
}


/* FUNCTION: setFrameAtomVelocities */
int HDF5_SimResults::setFrameAtomVelocities(const char* frameSetName,
											const int& frameIndex,
											const float* velocities,
											const unsigned int& atomCount,
											std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the atom velocities dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.atomVelocitiesDatasetId,
				 "AtomVelocities",
				 message);
		
		if (resultCode != 0) {
			// Create it
			resultCode =
				create3D_AtomFloatsDataset
					(frameSetName,
					 "AtomVelocities",
					 atomCount,
					 frameSetInfo.atomVelocitiesDatasetId,
					 message);
		}
	}
	
	if (resultCode == 0) {
		resultCode =
			write3SpaceAtomFloats(frameIndex, atomCount, velocities,
								  frameSetInfo.atomVelocitiesDatasetId,
								  message);
	}
	return resultCode;
}


/* FUNCTION: getFrameBonds
int HDF5_SimResults::getFrameBonds(const char* frameSetName,
								   const int& frameIndex,
								   unsigned int& bondCount,
								   void* bonds,
								   std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the bonds dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.bondsDatasetId,
				 "Bonds", message);
		
		if (resultCode == 0) {
			herr_t	status;
			
			// Select a hyperslab.
			hid_t filespace = H5Dget_space(frameSetInfo.bondsDatasetId);
			hsize_t slabStart[2] = { 0, frameIndex };
			hsize_t slabStride[2] = { 1, 1 };
			hsize_t slabCount[2] = { 1, 1 };
			status =
				H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
									slabStart, slabStride, slabCount, NULL);	
			
			// Create memory dataspace
			hsize_t dataDims[] = { 1 };       
			hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
			
			// Read data
			hvl_t data[1];
			status =
				H5Dread(frameSetInfo.bondsDatasetId, bondsVariableLengthId,
						memoryspace, filespace, H5P_DEFAULT, data);
			if (status < 0) {
				message = "Unable to read bonds: ";
				
				// Get error description from HDF5
				std::string hdf5Message;
				status =
					H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
				if (status > -1)
					message.append(hdf5Message).append(".");
				resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
				
			} else {
unsigned int bondIndex;
SimResultsBond bond;
for (bondIndex = 0; bondIndex < data[0].len; bondIndex++) {
	bond = ((SimResultsBond*)data[0].p)[bondIndex];
	printf("<%d %d %g>  ", bond.atomId_1, bond.atomId_2, bond.order);fflush(0);
}
				bondCount = data[0].len;
				bonds = data[0].p;
			}
			H5Sclose(memoryspace);
			H5Sclose(filespace);
		}
	}
	return resultCode;
}
*/


/* FUNCTION: getFrameBondsCount */
void HDF5_SimResults::getFrameBondsCount(const char* frameSetName,
										 const int& frameIndex,
										 unsigned int& bondCount) {
	bondCount = 0;
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	std::string message;
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the bonds dataset has been created
		resultCode =
		checkFrameSetDatasetExistence
		(frameSetName, frameSetInfo.bondsDatasetId, "Bonds", message);
		
		if (resultCode == 0) {
			herr_t	status;
			
			// Select a hyperslab.
			hid_t filespace = H5Dget_space(frameSetInfo.bondsDatasetId);
			hsize_t slabStart[2] = { 0, frameIndex };
			hsize_t slabStride[2] = { 1, 1 };
			hsize_t slabCount[2] = { 1, 1 };
			status =
				H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
									slabStart, slabStride, slabCount, NULL);
			
			// Create memory dataspace
			hsize_t dataDims[] = { 1 };       
			hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
			
			// Read data
			hvl_t data[1];
			status =
				H5Dread(frameSetInfo.bondsDatasetId, bondsVariableLengthId,
						memoryspace, filespace, H5P_DEFAULT, data);
			if (status > -1) {
				bondCount = data[0].len;
				status =
					H5Dvlen_reclaim(bondsVariableLengthId, memoryspace,
									H5P_DEFAULT, data);
			}
			H5Sclose(memoryspace);
			H5Sclose(filespace);
		}
	}
}


/* FUNCTION: getFrameBonds */
int HDF5_SimResults::getFrameBonds(const char* frameSetName,
								   const int& frameIndex,
								   void* bonds,
								   std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the bonds dataset has been created
		resultCode =
		checkFrameSetDatasetExistence
		(frameSetName,
		 frameSetInfo.bondsDatasetId,
		 "Bonds", message);
		
		if (resultCode == 0) {
			herr_t	status;
			
			// Select a hyperslab.
			hid_t filespace = H5Dget_space(frameSetInfo.bondsDatasetId);
			hsize_t slabStart[2] = { 0, frameIndex };
			hsize_t slabStride[2] = { 1, 1 };
			hsize_t slabCount[2] = { 1, 1 };
			status =
				H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
									slabStart, slabStride, slabCount, NULL);
			
			// Create memory dataspace
			hsize_t dataDims[] = { 1 };       
			hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
			
			// Read data
			hvl_t data[1];
			status =
				H5Dread(frameSetInfo.bondsDatasetId, bondsVariableLengthId,
						memoryspace, filespace, H5P_DEFAULT, data);
			if (status < 0) {
				message = "Unable to read bonds: ";
				
				// Get error description from HDF5
				std::string hdf5Message;
				status =
					H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
				if (status > -1)
					message.append(hdf5Message).append(".");
				resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
				
			} else {
				unsigned int bondIndex;
				SimResultsBond bond;
				for (bondIndex = 0; bondIndex < data[0].len; bondIndex++) {
					bond = ((SimResultsBond*)data[0].p)[bondIndex];
					((SimResultsBond*)bonds)[bondIndex] = bond;
				}
				status =
					H5Dvlen_reclaim(bondsVariableLengthId, memoryspace,
									H5P_DEFAULT, data);
			}
			H5Sclose(memoryspace);
			H5Sclose(filespace);
		}
	}
	return resultCode;
}


/* FUNCTION: setFrameBonds */
int HDF5_SimResults::setFrameBonds(const char* frameSetName,
								   const int& frameIndex,
								   const void* bonds,
								   const unsigned int& bondCount,
								   std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the bonds dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.bondsDatasetId,
				 "Bonds",
				 message);
		
		if (resultCode != 0) {
			// Create it
			resultCode =
				createBondsDataset(frameSetName, bondCount,
								   frameSetInfo.bondsDatasetId, message);
		}
	}
	
	if (resultCode == 0) {
		resultCode =
			writeBonds(frameIndex, bondCount, bonds,
					   frameSetInfo.bondsDatasetId, message);
	}
	return resultCode;
}


/* FUNCTION: setFrameTotalEnergy
int HDF5_SimResults::setFrameTotalEnergy(const char* frameSetName,
										 const int& frameIndex,
										 const float& totalEnergy,
										 std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the measurements dataset has been created
		resultCode =
			checkFrameSetDatasetExistence
				(frameSetName,
				 frameSetInfo.measurementsDatasetId,
				 "Measurements",
				 message);
		
		if (resultCode != 0) {
			// Create it
			resultCode =
				createMeasurementsDataset
					(frameSetName, frameSetInfo.measurementsDatasetId,
					 message);
		}
	}
	
	if (resultCode == 0) {
		resultCode =
			writeMeasurement(frameIndex, TOTAL_ENERGY_MSRMT, totalEnergy,
							 frameSetInfo.measurementsDatasetId, message);
	}
	return resultCode;
}
*/


/* FUNCTION: getFrameTotalEnergy */
int HDF5_SimResults::getFrameTotalEnergy(const char* frameSetName,
										 const int& frameIndex,
										 float& totalEnergy,
										 std::string& message) {
	
	return readMeasurement(frameSetName, frameIndex, TOTAL_ENERGY_MSRMT,
						   frameSetInfoMap[frameSetName].measurementsDatasetId,
						   totalEnergy, message);
}


/* FUNCTION: setFrameTotalEnergy */
int HDF5_SimResults::setFrameTotalEnergy(const char* frameSetName,
										 const int& frameIndex,
										 const float& totalEnergy,
										 std::string& message) {
	
	return writeMeasurement(frameSetName, frameIndex, TOTAL_ENERGY_MSRMT,
							totalEnergy,
							frameSetInfoMap[frameSetName].measurementsDatasetId,
							message);
}


/* FUNCTION: getFrameIdealTemperature */
int HDF5_SimResults::getFrameIdealTemperature(const char* frameSetName,
											  const int& frameIndex,
											  float& idealTemperature,
											  std::string& message) {
	
	return readMeasurement(frameSetName, frameIndex, IDEAL_TEMPERATURE_MSRMT,
						   frameSetInfoMap[frameSetName].measurementsDatasetId,
						   idealTemperature, message);
}


/* FUNCTION: setFrameIdealTemperature */
int HDF5_SimResults::setFrameIdealTemperature(const char* frameSetName,
											  const int& frameIndex,
											  const float& idealTemperature,
											  std::string& message) {
	
	return writeMeasurement(frameSetName, frameIndex, IDEAL_TEMPERATURE_MSRMT,
							idealTemperature,
							frameSetInfoMap[frameSetName].measurementsDatasetId,
							message);
}


/* FUNCTION: getFramePressure */
int HDF5_SimResults::getFramePressure(const char* frameSetName,
									  const int& frameIndex,
									  float& pressure,
									  std::string& message) {
	
	return readMeasurement(frameSetName, frameIndex, PRESSURE_MSRMT,
						   frameSetInfoMap[frameSetName].measurementsDatasetId,
						   pressure, message);
}


/* FUNCTION: setFramePressure */
int HDF5_SimResults::setFramePressure(const char* frameSetName,
									  const int& frameIndex,
									  const float& pressure,
									  std::string& message) {
	
	return writeMeasurement(frameSetName, frameIndex, PRESSURE_MSRMT,
							pressure,
							frameSetInfoMap[frameSetName].measurementsDatasetId,
							message);
}


/******************************************************************************/


/*
 * FUNCTION: checkFrameExistence
 */
int HDF5_SimResults::checkFrameExistence(const char* frameSetName,
										 const int& frameIndex,
										 std::string& message) {
		
	// Check if the frame-set has been added
	int resultCode = checkFrameSetExistence(frameSetName, message);
	if (resultCode == 0) { // Frame-set exists
		
		// Check if Timestamps dataset has been added
		resultCode = checkTimestampsExistence(frameSetName, message);
		if (resultCode == 0) {
			
			// Check if the requested frame has already been added
			if (frameIndex > frameSetInfoMap[frameSetName].currentFrameIndex) {
				message = "Requested frame hasn't been added.";
				resultCode = SRDS_INVALID_FRAMEINDEX;
			}
		}
	}
	return resultCode;
}


/* FUNCTION: checkFrameSetDatasetExistence
 *
 * Assumes the frame-set exists, ie, doesn't check for it.
 *
 * @param message Set to a description of the problem if non-zero is returned
 * @return zero=dataset exists, non-zero=dataset doesn't exist
 */
int HDF5_SimResults::checkFrameSetDatasetExistence(const char* frameSetName,
												   hid_t& datasetId,
												   const char* datasetName,
												   std::string& message) {
	int resultCode = 0;
	
	// Check if the AtomPositions dataset has been created
	if (datasetId == 0) {
		
		// Check if some other object created the dataset			
		std::string fullDatasetName = "/Results/FrameSets/";
		fullDatasetName.append(frameSetName).append("/").append(datasetName);
		datasetId = H5Dopen(fileId, fullDatasetName.c_str());
		if (datasetId < 0) {
			datasetId = 0;
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
			hid_t dataspaceId = H5Dget_space(datasetId);
			frameSetInfo.currentFrameIndex =
				H5Sget_simple_extent_npoints(dataspaceId);
			H5Sclose(dataspaceId);
			
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


/* FUNCTION: createMeasurementsDataset */
int HDF5_SimResults::createMeasurementsDataset(const char* frameSetName,
											   hid_t& datasetId,
											   std::string& message) {
    herr_t	status;
	int resultCode = 0;
	
	// Create the dataspace
    hsize_t	dims[2] = { 3, 1 };
    hsize_t	maxDims[2] = { 3, H5S_UNLIMITED };
    hid_t dataspaceId = H5Screate_simple(2 /* rank */, dims, maxDims);
	
    // Modify dataset creation properties, i.e. enable chunking, compression
    hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
	if (USE_CHUNKING) {
		hsize_t	chunkDims[2] = { 3, 1 };
		status = H5Pset_chunk(datasetParams, 2 /* rank */, chunkDims);
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
	fullDatasetName.append(frameSetName).append("/Measurements");
    datasetId =
		H5Dcreate(fileId, fullDatasetName.c_str(), H5T_NATIVE_FLOAT,
				  dataspaceId, datasetParams);
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
	H5Sclose(dataspaceId);
    H5Pclose(datasetParams);
	
	return resultCode;
}


/* FUNCTION: createBondsDataset */
int HDF5_SimResults::createBondsDataset(const char* frameSetName,
										const unsigned int& bondCount,
										hid_t& datasetId,
										std::string& message) {
    herr_t	status;
	int resultCode = 0;

	// Create the dataspace
    hsize_t	dims[2] = { 1, 1 };
    hsize_t	maxDims[2] = { 1, H5S_UNLIMITED };
    hid_t dataspaceId = H5Screate_simple(2 /* rank */, dims, maxDims);
	
    // Modify dataset creation properties, i.e. enable chunking, compression
    hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
	if (USE_CHUNKING) {
		hsize_t	chunkDims[2] = { 1, 1 };
		status = H5Pset_chunk(datasetParams, 2 /* rank */, chunkDims);
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
	fullDatasetName.append(frameSetName).append("/Bonds");
    datasetId =
		H5Dcreate(fileId, fullDatasetName.c_str(), bondsVariableLengthId,
				  dataspaceId, datasetParams);
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
	H5Sclose(dataspaceId);
    H5Pclose(datasetParams);
	
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
												std::string& message) {
    herr_t status;
	int resultCode = 0;
	
	// Create the dataspace
    hsize_t	dims[3] = { atomCount, 3, 1 };
    hsize_t	maxDims[3] = { atomCount, 3, H5S_UNLIMITED };
    hid_t dataspaceId = H5Screate_simple(3 /* rank */, dims, maxDims);
	
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
	H5Sclose(dataspaceId);
    H5Pclose(datasetParams);
	
	return resultCode;
}
	

/* FUNCTION: createTimestampsDataset
 *
 * Assumes the frame-set already exists, ie, doesn't check if it exists.
 */
int HDF5_SimResults::createTimestampsDataset(const char* frameSetName,
											 hid_t& datasetId,
											 std::string& message) {
    herr_t status;
	int resultCode = 0;

	// Create the dataspace
    hsize_t	dims[1] = { 1 };
    hsize_t	maxDims[1] = { H5S_UNLIMITED };
    hid_t dataspaceId = H5Screate_simple(1 /* rank */, dims, maxDims);
	
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
	H5Sclose(dataspaceId);
    H5Pclose(datasetParams);
	
	return resultCode;
}


/* FUNCTION: writeMeasurement
int HDF5_SimResults::writeMeasurement(const int& frame,
									  const int& measurementIndex,
									  const float& value,
									  const hid_t& datasetId,
									  std::string& message) {
    herr_t status;
	int resultCode = 0;

	// Prepare data
	hsize_t dataDims[] = { 1 };       
	float data[] = { value }; 
	
	// Array to store selected points from the file dataspace
	hsize_t coordinates[1][2];
	coordinates[0][0] = measurementIndex; coordinates[0][1] = frame;
	
	// Create memory dataspace
	hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
	
	// Extend the dataset.
    hsize_t	dims[2] = { 3, frame + 1 };
	status = H5Dextend(datasetId, dims);
	
	// Select the point
	hid_t filespace = H5Dget_space(datasetId);
	status =
		H5Sselect_elements(filespace, H5S_SELECT_SET, 1,
						   (const hsize_t**)coordinates);
		
	// Write the data to the point.
	status =
		H5Dwrite(datasetId, H5T_NATIVE_FLOAT, H5S_ALL, filespace,
				 H5P_DEFAULT, data);	
	if (status < 0) {
		message = "Unable to write measurement: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
    H5Sclose(filespace);
	H5Sclose(memoryspace);
	
	return resultCode;
}*/
				 
				 
 /* FUNCTION: writeMeasurement */
 int HDF5_SimResults::writeMeasurement(const char* frameSetName,
									   const int& frameIndex,
									   const int& measurementIndex,
									   const float& value,
									   const hid_t& datasetId,
									   std::string& message) {
	 
	 FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	 
	 // Check if the frame has been added
	 int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	 if (resultCode == 0) {
		 // Check if the measurements dataset has been created
		 resultCode =
		 checkFrameSetDatasetExistence
		 (frameSetName, frameSetInfo.measurementsDatasetId,
		  "Measurements", message);
		 
		 if (resultCode != 0) {
			 // Create it
			 resultCode =
			 createMeasurementsDataset
			 (frameSetName, frameSetInfo.measurementsDatasetId,
			  message);
		 }
	 }
	 
	 if (resultCode == 0) {
		 herr_t status;
		 
		 // Prepare data
		 hsize_t dataDims[] = { 1 };       
		 float data[] = { value }; 
		 
		 // Array to store selected points from the file dataspace
		 hsize_t coordinates[1][2];
		 coordinates[0][0] = measurementIndex;
		 coordinates[0][1] = frameIndex;
		 
		 // Create memory dataspace
		 hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
		 
		 // Extend the dataset.
		 hsize_t	dims[2] = { 3, frameIndex + 1 };
		 status = H5Dextend(datasetId, dims);
		 
		 // Select the point
		 hid_t filespace = H5Dget_space(datasetId);
		 status =
			 H5Sselect_elements(filespace, H5S_SELECT_SET, 1,
								(const hsize_t*)coordinates);
		 
		 // Write the data to the point.
		 status =
			 H5Dwrite(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
					  H5P_DEFAULT, data);	
		 if (status < 0) {
			 message = "Unable to write measurement: ";
			 
			 // Get error description from HDF5
			 std::string hdf5Message;
			 status =
				 H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			 if (status > -1)
				 message.append(hdf5Message).append(".");
			 resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		 }
		 H5Sclose(filespace);
		 H5Sclose(memoryspace);
	 }
	 return resultCode;
 }
				 

/* FUNCTION: writeBonds */
int HDF5_SimResults::writeBonds(const int& frame, const unsigned int& bondCount,
								const void* bonds, hid_t datasetId,
								std::string& message) {
    herr_t	status;
	int resultCode = 0;

	// Prepare data
	hvl_t data[1];
	data[0].p = (void*)bonds;
	data[0].len = bondCount;
	
	// Extend the dataset.
    hsize_t	dims[2] = { 1, frame + 1 };
	status = H5Dextend(datasetId, dims);
	
	// Create memory dataspace
	hsize_t dataDims[] = { 1 };       
	hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
	
	// Select a hyperslab.
	hid_t filespace = H5Dget_space(datasetId);
	hsize_t slabStart[2] = { 0, frame };
	hsize_t slabStride[2] = { 1, 1 };
	hsize_t slabCount[2] = { 1, 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	
	// Write the data to the hyperslab.
	status =
		H5Dwrite(datasetId, bondsVariableLengthId, memoryspace, filespace,
				 H5P_DEFAULT, data);
	if (status < 0) {
		message = "Unable to write bonds: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	H5Sclose(memoryspace);
    H5Sclose(filespace);	
	
	return resultCode;
}


/* FUNCTION: writeAtomUInts */
int HDF5_SimResults::writeAtomUInts(const char* frameSetName,
									const char* dataSetName,
									const unsigned int* atomUInts,
									const unsigned int& atomUIntsCount,
									hid_t& datasetId,
									std::string& message) {
	int resultCode = 0;
	herr_t status;
	
	// Create the dataspace
	hsize_t dims[1] = { atomUIntsCount };
	hid_t dataspaceId =
		H5Screate_simple(1,		// rank
						 dims,	// dimensions
						 NULL);	// max dimensions
	
	// Modify dataset creation properties, i.e. enable chunking,
	// compression
	hid_t datasetParams = H5Pcreate(H5P_DATASET_CREATE);
	if (USE_CHUNKING) {
		hsize_t chunkDims[1] = { atomUIntsCount };
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
	groupName.append(frameSetName).append("/").append(dataSetName);
	datasetId =
		H5Dcreate(fileId, groupName.c_str(), H5T_NATIVE_UINT,
				  dataspaceId, datasetParams);
	if (datasetId < 0) {
		message =
		"Unable to create the dataset for /Results/FrameSets/";
		message.append(frameSetName).append(": ");
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
		
	} else {
		H5Sclose(dataspaceId);
		
		// Write the atom unsigned integers
		status =
			H5Dwrite(datasetId, H5T_NATIVE_UINT, H5S_ALL, H5S_ALL,
					 H5P_DEFAULT, atomUInts);
		if (status != 0) {
			message = "Unable to write atom data: ";
			
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker,
						&hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			
			H5Dclose(datasetId);
		}
	}
	H5Pclose(datasetParams);
	
	return resultCode;
}


/* FUNCTION: write3SpaceAtomFloats */
int HDF5_SimResults::write3SpaceAtomFloats(const int& frame,
										   const unsigned int& atomCount,
										   const float* data, hid_t datasetId,
										   std::string& message) {
    herr_t	status;
	int resultCode = 0;

	// Extend the dataset. This call assures that dataset is at least
	// nAtoms x 3 x (frame+1) in size
	hsize_t	dims[3] = { atomCount, 3, frame + 1 };
	status = H5Dextend(datasetId, dims);
	
	// Select a hyperslab.
	hid_t filespace = H5Dget_space(datasetId);
	hsize_t slabStart[3] = { 0, 0, frame };
	hsize_t slabStride[3] = { 1, 1, 1 };
	hsize_t slabCount[3] = { atomCount, 3, 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	
	// Create memory dataspace
	hsize_t dataDims[] = { atomCount, 3, 1 };       
	hid_t memoryspace = H5Screate_simple(3, dataDims, NULL);
	
	// Write the data to the hyperslab.
	status =
		H5Dwrite(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
				 H5P_DEFAULT, data);
	if (status < 0) {
		message = "Unable to write atom floats: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	H5Sclose(memoryspace);
    H5Sclose(filespace);
	
	return resultCode;
}
	
	
/* FUNCTION: writeTimestamp */
int HDF5_SimResults::writeTimestamp(const int& frame, const float& time,
									hid_t datasetId, std::string& message) {
	herr_t	status;
	int resultCode = 0;
	
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
	
	// Create memory dataspace
	float data[1] = { time };
	hsize_t dataDims[] = { 1 };       
	hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
	
	// Write the data to the hyperslab.
	status =
		H5Dwrite(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
				 H5P_DEFAULT, data);
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
	H5Sclose(memoryspace);
    H5Sclose(filespace);
	
	return resultCode;
}


/* FUNCTION: readMeasurement */
int HDF5_SimResults::readMeasurement(const char* frameSetName,
									 const int& frameIndex,
									 const int& measurementIndex,
									 const hid_t& datasetId,
									 float& value,
									 std::string& message) {
	
	FrameSetInfo& frameSetInfo = frameSetInfoMap[frameSetName];
	
	// Check if the frame has been added
	int resultCode = checkFrameExistence(frameSetName, frameIndex, message);
	if (resultCode == 0) {
		// Check if the measurements dataset has been created
		resultCode =
		checkFrameSetDatasetExistence
		(frameSetName, frameSetInfo.measurementsDatasetId,
		 "Measurements", message);
	}
	
	if (resultCode == 0) {
		herr_t status;
		
		// Prepare data
		hsize_t dataDims[] = { 1 };       
		float data[1]; 
		
		// Array to store selected points from the file dataspace
		hsize_t coordinates[1][2];
		coordinates[0][0] = measurementIndex;
		coordinates[0][1] = frameIndex;
		
		// Create memory dataspace
		hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
		
		// Select the point
		hid_t filespace = H5Dget_space(datasetId);
		status =
			H5Sselect_elements(filespace, H5S_SELECT_SET, 1,
							   (const hsize_t*)coordinates);
		
		// Read the data point
		status =
			H5Dread(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
					H5P_DEFAULT, data);	
		if (status < 0) {
			message = "Unable to read measurement: ";
			
			// Get error description from HDF5
			std::string hdf5Message;
			status =
				H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
			if (status > -1)
				message.append(hdf5Message).append(".");
			resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
			
		} else {
			value = data[0];
		}
		H5Sclose(filespace);
		H5Sclose(memoryspace);
	}
	return resultCode;
}


/* FUNCTION: read3SpaceAtomFloats */
int HDF5_SimResults::read3SpaceAtomFloats(const int& frame,
										  const unsigned int& atomCount,
										  float* data, hid_t datasetId,
										  std::string& message) {
    herr_t	status;
	int resultCode = 0;

	// Get the filespace
	hid_t filespace = H5Dget_space(datasetId);
	
	// Select a hyperslab.
	hsize_t slabStart[3] = { 0, 0, frame };
	hsize_t slabStride[3] = { 1, 1, 1 };
	hsize_t slabCount[3] = { atomCount, 3, 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	
	// Create memory dataspace
	hsize_t dataDims[] = { atomCount, 3, 1 };       
	hid_t memoryspace = H5Screate_simple(3, dataDims, NULL);

	// Read data
	status =
		H5Dread(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
				H5P_DEFAULT, data);
	if (status < 0) {
		message = "Unable to read atom floats: ";
		
		// Get error description from HDF5
		std::string hdf5Message;
		status =
			H5Ewalk(H5E_WALK_UPWARD, H5_ErrorStackWalker, &hdf5Message);
		if (status > -1)
			message.append(hdf5Message).append(".");
		resultCode = SRDS_UNABLE_TO_COMPLETE_OPERATION;
	}
	H5Sclose(memoryspace);
    H5Sclose(filespace);
	
	return resultCode;
}


/* FUNCTION: readTimestamp */
int HDF5_SimResults::readTimestamp(const int& frame, float& time,
								   hid_t datasetId,
								   std::string& message) const {
    herr_t	status;
	int resultCode = 0;
	
	// Select a hyperslab.
	hid_t filespace = H5Dget_space(datasetId);
	hsize_t slabStart[1] = { frame };
	hsize_t slabStride[1] = { 1 };
	hsize_t slabCount[1] = { 1 };
	status =
		H5Sselect_hyperslab(filespace, H5S_SELECT_SET,
							slabStart, slabStride, slabCount, NULL);
	
	// Create memory dataspace
	float data[1];
	hsize_t dataDims[] = { 1 };       
	hid_t memoryspace = H5Screate_simple(1, dataDims, NULL);
	
	// Read data
	status =
		H5Dread(datasetId, H5T_NATIVE_FLOAT, memoryspace, filespace,
				H5P_DEFAULT, data);
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
	H5Sclose(memoryspace);
    H5Sclose(filespace);
	
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

#ifndef _WIN32
		struct tm timestamp;
		char buffer[64];
		timestamp = *localtime(&value);
		strftime(buffer, sizeof(buffer), "%a %Y-%m-%d %H:%M:%S %Z", &timestamp);
		message.append("=").append(buffer).append(": ");
#endif
		
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


/* FUNCTION: getGroupKeys */
std::vector<std::string> HDF5_SimResults::getGroupKeys
		(const std::string& group) const {
	std::vector<std::string> keys;
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, group.c_str());
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

} // Nanorex::
