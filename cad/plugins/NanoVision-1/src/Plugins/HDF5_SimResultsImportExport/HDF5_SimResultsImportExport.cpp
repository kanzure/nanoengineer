// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExport.h"


/* FUNCTION: instantiate */
DLLEXPORT NXPlugin* instantiate() {
	return new HDF5_SimResultsImportExport();
}



/* CONSTRUCTOR */
HDF5_SimResultsImportExport::HDF5_SimResultsImportExport() {
}


/* DESTRUCTOR */
HDF5_SimResultsImportExport::~HDF5_SimResultsImportExport() {
}


/* FUNCTION: importFromFile */
NXCommandResult* HDF5_SimResultsImportExport::importFromFile
		(NXMoleculeSet* moleculeSet, const string& filename) {
	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	string message = "Reading: ";
	message.append(filename);
	NXLOG_INFO("HDF5_SimResultsImportExport", message.c_str());


	return result;
}


/* FUNCTION: exportToFile */
NXCommandResult* HDF5_SimResultsImportExport::exportToFile
		(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
		 const std::string& filename, unsigned int frameIndex) {
		
	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Create or retrieve the HDF5 data store object
	//
	HDF5_SimResults* simResults = 0;
	if (frameIndex == 0)
		simResults = new HDF5_SimResults();
		if (!dataStoreInfo->isLastFrame())
			dataStoreInfo->setHandle(simResults);
	else
		simResults = (HDF5_SimResults*)(dataStoreInfo->getHandle());
		
	if (simResults == 0)
		populateCommandResult(result,
							  "exportToFile: Could not instantiate or retrieve the HDF5_SimResults object.");

	// Create the actual data store. We assume that checks for existing data
	// stores with the same name have already been done, and so clobber any
	// existing files.
	int status;
	string message;
	if ((result->getResult() == NX_CMD_SUCCESS) && (frameIndex == 0)) {
		QDir pwd;
		pwd.mkdir(filename.c_str());
		QString hdf5Filename(filename.c_str());
		hdf5Filename.append("/").append(HDF5_SIM_RESULT_FILENAME);
		QFile::remove(hdf5Filename);
		status = simResults->openDataStore(filename.c_str(), message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
	
	// Add a frame set
	if (result->getResult() == NX_CMD_SUCCESS) {
		status = simResults->addFrameSet("frame-set-1", message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
	
	// Add a frame
	int index;
	if (result->getResult() == NX_CMD_SUCCESS) {
		status = simResults->addFrame("frame-set-1", 0.0, index, message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
	
	unsigned int moleculeCount = 0;
	unsigned int atomCount = 0;
	unsigned int bondCount = 0;
	if (result->getResult() == NX_CMD_SUCCESS) {
		if (frameIndex == 0) {
			// One pass through the molecule set to get atom and bond counts
			moleculeSet->getCounts(moleculeCount, atomCount, bondCount);
			
		} else {
			// Retrieve stored counts
			simResults->getFrameAtomIdsCount("frame-set-1", atomCount);
		}
	}
	
	unsigned int atomIds[atomCount];
	unsigned int atomicNumbers[atomCount];
	float positions[atomCount*3];

	// One pass through the molecule set to populate the arrays.
	unsigned int atomIndex = 0;
	if (result->getResult() == NX_CMD_SUCCESS) {
		exportToFileHelper(moleculeSet, atomIndex, atomIds, atomicNumbers,
						   positions, result);
	}
	
	// Write frame set info
	if ((result->getResult() == NX_CMD_SUCCESS) && (frameIndex == 0)) {
		status =
			simResults->setFrameAtomIds("frame-set-1", atomIds, atomCount,
										message);
		if (status == 0) {
			status =
				simResults->setFrameAtomicNumbers
					("frame-set-1", atomicNumbers, atomCount, message);
			if (status)
				populateCommandResult(result, message.c_str());
		} else
			populateCommandResult(result, message.c_str());
	}
	
	// Write the frame
	if (result->getResult() == NX_CMD_SUCCESS) {
		status =
			simResults->setFrameAtomPositions("frame-set-1", frameIndex,
											  positions, atomCount, message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
										  
	// Close data store if this was the last frame.
	if ((simResults != 0) && (dataStoreInfo->isLastFrame()))
		delete simResults;
		
	return result;
}


/* FUNCTION: exportToFileHelper */
void HDF5_SimResultsImportExport::exportToFileHelper
		(NXMoleculeSet* moleculeSet, unsigned int atomIndex,
		 unsigned int* atomIds, unsigned int* atomicNumbers,
		 float* positions, NXCommandResult* result) {
		
	OBAtomIterator atomIter;
	OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
	while (moleculeIter != moleculeSet->moleculesEnd()) {
		atomIter = (*moleculeIter)->BeginAtoms();
		while (((*atomIter) != 0) &&
				(atomIter != (*moleculeIter)->EndAtoms())) {
			atomIds[atomIndex] = (*atomIter)->GetIdx();
			atomicNumbers[atomIndex] = (*atomIter)->GetAtomicNum();
			positions[atomIndex*3 + 0] = (*atomIter)->GetX();
			positions[atomIndex*3 + 1] = (*atomIter)->GetY();
			positions[atomIndex*3 + 2] = (*atomIter)->GetZ();
			atomIndex++;
			atomIter++;
		}
		moleculeIter++;
	}
	NXMoleculeSetIterator moleculeSetIter = moleculeSet->childrenBegin();
	while (moleculeSetIter != moleculeSet->childrenEnd()) {
		exportToFileHelper(*moleculeSetIter, atomIndex, atomIds, atomicNumbers,
						   positions, result);
		moleculeSetIter++;
	}
}


/* FUNCTION: populateCommandResult */
void HDF5_SimResultsImportExport::populateCommandResult
		(NXCommandResult* result, const string& message) {
	result->setResult(NX_PLUGIN_REPORTS_ERROR);
	vector<QString> resultVector;
	resultVector.push_back("HDF5_SimResultsImportExport");
	resultVector.push_back(message.c_str());
	result->setParamVector(resultVector);
}
