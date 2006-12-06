
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#ifndef NE1_HDF5_SIMRESULTS_H
#define NE1_HDF5_SIMRESULTS_H

#include <stdlib.h>
#include <string>

#include "hdf5.h"

#include "SimResultsDataStore.h"

#define HDF5_SIM_RESULT_FILENAME "sim_results.h5"

namespace ne1 {


/* CLASS: HDF5_SimResults
 *
 * HDF5 implementation of SimResultsDataStore.
 *
 * Hierarchy:
	/
		Name, Description, Notes
	
		Parameters/
			StartStep, MaxSteps
			Timestep, EnvironmentTemperature, EnvironmentPressure
	
		InputFilePaths/
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
		int setTimestep(float timestep, std::string& message);
		
		int getStartStep(int& startStep) const;
		int setStartStep(int startStep, std::string& message);
		
		int getMaxSteps(int& maxSteps) const;
		int setMaxSteps(int maxSteps, std::string& message);
		
		int getEnvironmentTemperature(float& envTemp) const;
		int setEnvironmentTemperature(float envTemp, std::string& message);
		
		int getEnvironmentPressure(float& envPress) const;
		int setEnvironmentPressure(float envPress, std::string& message);
		
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
};

} // ne1::

#endif
