
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
	/SimResults
		Attributes:
			Strings: Name, Description, Notes
			Ints: StartStep, MaxSteps
			Floats: Timestep, EnvironmentTemperature, EnvironmentPressure
	
		InputFilePaths/
 */
class HDF5_SimResults : public SimResultsDataStore {
	public:
		HDF5_SimResults();
		~HDF5_SimResults();
		
		int openDataStore(const char* directory, std::string& message);
		
		std::string getName() const;
		int setName(const std::string& name, std::string& message);
		
		std::string getDescription() const;
		int setDescription(const std::string& description,
						   std::string& message);
		
		std::string getNotes() const;
		int setNotes(const std::string& notes, std::string& message);
		
	private:
		// HDF5 type identifiers
		hid_t bondTypeId;
		hid_t bondsVariableLengthId;
		
		hid_t fileId;	// HDF5 file identifier
		
		std::string getStringAttribute(const std::string& groupName,
									   const std::string& attributeName) const;
		int setStringAttribute
			(const std::string& groupName, const std::string& attributeName,
			 const std::string& value, std::string& message);
};

} // ne1::

#endif
