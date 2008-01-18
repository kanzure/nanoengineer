// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExport.h"


/* FUNCTION: instantiate */
DLLEXPORT Nanorex::NXPlugin* instantiate() {
	return new HDF5_SimResultsImportExport();
}



/* CONSTRUCTOR */
HDF5_SimResultsImportExport::HDF5_SimResultsImportExport() {
}


/* DESTRUCTOR */
HDF5_SimResultsImportExport::~HDF5_SimResultsImportExport() {
}


/* FUNCTION: importFromFile */
Nanorex::NXCommandResult* HDF5_SimResultsImportExport::importFromFile
		(Nanorex::NXMSInt moleculeSetId, const std::string& filename) {
	Nanorex::NXCommandResult* result = new Nanorex::NXCommandResult();
	result->setResult(Nanorex::NX_CMD_SUCCESS);

	string message = "Reading: ";
	message.append(filename);
	NXLOG_INFO("HDF5_SimResultsImportExport", message.c_str());


	return result;
}


/* FUNCTION: exportToFile */
Nanorex::NXCommandResult* HDF5_SimResultsImportExport::exportToFile
		(Nanorex::NXMSInt moleculeSetId, const std::string& filename) {
	Nanorex::NXCommandResult* result = new Nanorex::NXCommandResult();
	result->setResult(Nanorex::NX_CMD_SUCCESS);


	return result;
}
