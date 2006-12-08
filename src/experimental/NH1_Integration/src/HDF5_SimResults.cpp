
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
	
	// See if the group exists and open it
	hid_t groupId = H5Gopen(fileId, groupName.c_str());
	if (groupId < 0) {
		// Doesn't exist, create it
		groupId = H5Gcreate(fileId, groupName.c_str(), GROUP_NAME_SIZE_HINT);
	}
	
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
			H5Acreate(groupId, attributeName.c_str(), stringType, dataspaceId,
					  H5P_DEFAULT);
	
	// Write the attribute
	char* valueChars = (char*)(malloc((value.length()+1)*sizeof(char)));
	strcpy(valueChars, value.c_str());
	status = H5Awrite(attributeId, stringType, &valueChars);
	free(valueChars);
	if (status < 0) {
		message = "Unable to set ";
		message.append(groupName).append("/").append(attributeName);
		message.append("=").append(value).append(": ");
		
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
			H5Acreate(groupId, attributeName.c_str(), H5T_NATIVE_INT,
					  dataspaceId, H5P_DEFAULT);
	
	// Write the attribute
	status = H5Awrite(attributeId, H5T_NATIVE_INT, &value);
	if (status < 0) {
		message = "Unable to set ";
		message.append(groupName).append("/").append(attributeName);
		char buffer[20];
		sprintf(buffer, "%d", value);
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
			H5Acreate(groupId, attributeName.c_str(), H5T_NATIVE_FLOAT,
					  dataspaceId, H5P_DEFAULT);
	
	// Write the attribute
	status = H5Awrite(attributeId, H5T_NATIVE_FLOAT, &value);
	if (status < 0) {
		message = "Unable to set ";
		message.append(groupName).append("/").append(attributeName);
		char buffer[20];
		sprintf(buffer, "%f", value);
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
