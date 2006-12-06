
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
int HDF5_SimResults::setTimestep(float timestep, std::string& message) {
	return setFloatAttribute("/Parameters", "Timestep", timestep, message);
}


/* FUNCTION: getStartStep */
int HDF5_SimResults::getStartStep(int& startStep) const {
	return getIntAttribute("/Parameters", "StartStep", startStep);
}


/* FUNCTION: setStartStep */
int HDF5_SimResults::setStartStep(int startStep, std::string& message) {
	return setIntAttribute("/Parameters", "StartStep", startStep, message);
}


/* FUNCTION: getMaxSteps */
int HDF5_SimResults::getMaxSteps(int& maxSteps) const {
	return getIntAttribute("/Parameters", "MaxSteps", maxSteps);
}


/* FUNCTION: setMaxSteps */
int HDF5_SimResults::setMaxSteps(int maxSteps, std::string& message) {
	return setIntAttribute("/Parameters", "MaxSteps", maxSteps, message);
}


/* FUNCTION: getEnvironmentTemperature */
int HDF5_SimResults::getEnvironmentTemperature(float& envTemp) const {
	return getFloatAttribute("/Parameters", "EnvironmentTemperature", envTemp);
}


/* FUNCTION: setEnvironmentTemperature */
int HDF5_SimResults::setEnvironmentTemperature(float envTemp,
											   std::string& message) {
	return setFloatAttribute("/Parameters", "EnvironmentTemperature", envTemp,
							 message);
}


/* FUNCTION: getEnvironmentPressure */
int HDF5_SimResults::getEnvironmentPressure(float& envPress) const {
	return getFloatAttribute("/Parameters", "EnvironmentPressure", envPress);
}


/* FUNCTION: setEnvironmentPressure */
int HDF5_SimResults::setEnvironmentPressure(float envPress,
											std::string& message) {
	return setFloatAttribute("/Parameters", "EnvironmentPressure", envPress,
							 message);
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
		//
		// The number of bytes to reserve for the names in the group
		int namesSize = 64;
		groupId = H5Gcreate(fileId, groupName.c_str(), namesSize);
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
		//
		// The number of bytes to reserve for the names in the group
		int namesSize = 64;
		groupId = H5Gcreate(fileId, groupName.c_str(), namesSize);
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
		//
		// The number of bytes to reserve for the names in the group
		int namesSize = 64;
		groupId = H5Gcreate(fileId, groupName.c_str(), namesSize);
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


} // ne1::
