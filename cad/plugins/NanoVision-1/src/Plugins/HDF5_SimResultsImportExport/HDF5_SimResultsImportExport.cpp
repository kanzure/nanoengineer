// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExport.h"


/* CONSTRUCTOR */
HDF5_SimResultsImportExport::HDF5_SimResultsImportExport() {
}


/* DESTRUCTOR */
HDF5_SimResultsImportExport::~HDF5_SimResultsImportExport() {
}


/* FUNCTION: importFromFile */
NXCommandResult* HDF5_SimResultsImportExport::importFromFile
		(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
		 const string& filename, int frameSetId, int frameIndex) {

	H5Eset_auto(0, 0); // Turn off HDF5 messages to stdout

	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Create or retrieve the HDF5 data store object
	//
	HDF5_SimResults* simResults = 0;
	if (frameIndex == 0) {
		simResults = new HDF5_SimResults();
		dataStoreInfo->setHandle(frameSetId, simResults);
		
	} else
		simResults = (HDF5_SimResults*)(dataStoreInfo->getHandle(frameSetId));
		
	if (simResults == 0)
		populateCommandResult(result,
							  "exportToFile: Could not instantiate or retrieve "
                              "the HDF5_SimResults object.");

	// Open the actual data store.
	int status;
	string message, hdf5FileDirectory;
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
		hdf5FileDirectory = getHDF5fileDirectory(filename);
		status = simResults->openDataStore(hdf5FileDirectory.c_str(), message);
		if (status)
			populateCommandResult(result, message.c_str());
	} else
		simResults->synchronize();
	
	// See if the requested frame exists (yet) and abort if it doesn't
	// signaling to delete the frame for the given frameIndex.
	int frameCount = 0;
	simResults->getFrameCount("frame-set-1", frameCount);
	if (frameCount == 0) {
		dataStoreInfo->setLastFrame(frameSetId, true);
		return result;
	}
	
	// If this is the first ca	ll to import the data store, retrieve the meta
	// information about the data store, and other data.
	if ((frameIndex == 0) && (frameSetId == 0) &&
		(result->getResult() == NX_CMD_SUCCESS)) {
		populateDataStoreInfo(dataStoreInfo, simResults, hdf5FileDirectory,
							  frameSetId);
	}
	
	// Retrieve stored counts and run status
	//
	unsigned int atomCount = 0;
	unsigned int bondCount = 0;
	if (result->getResult() == NX_CMD_SUCCESS) {
		simResults->getFrameAtomIdsCount("frame-set-1", atomCount);
		simResults->getFrameBondsCount("frame-set-1", 0, bondCount);
		
		int frameCount = 0;
		simResults->getFrameCount("frame-set-1", frameCount);
		dataStoreInfo->setLastFrame(frameSetId, frameIndex > frameCount - 2);
//printf("HDF5_SimResultsImportExport::importFromFile: setLastFrame(frameSetId=%d, frameIndex=%d > frameCount=%d - 2)\n", frameSetId, frameIndex, frameCount);fflush(0);
		
		int runResult = -1; // 0=success, 1=still running, 2=failure, 3=aborted
		string failureDescription;
		simResults->getRunResult(runResult, failureDescription);
		if (runResult == 1) {
			dataStoreInfo->setStoreComplete(frameSetId, false);
printf("HDF5: setstorecomplete(false)\n");fflush(0);
		} else {
			if (((frameIndex != 0) || (frameSetId != 0)) &&
				!dataStoreInfo->storeIsComplete(frameSetId)) {
				// The data store just completed, read the results summary info
				NXProperties* properties = getResultsSummary(simResults);
				dataStoreInfo->setResultsSummary(properties);
			}
			dataStoreInfo->setStoreComplete(frameSetId, true);
printf("HDF5: setStoreComplete(true)\n");
		}
	}
	
	unsigned int atomIds[atomCount];
	unsigned int atomicNumbers[atomCount];
	float positions[atomCount*3];
	void* bonds = 0;
	if (bondCount != 0)
		bonds = (void*)malloc(bondCount*sizeof(SimResultsBond));

	// Retrieve atom data
	if (result->getResult() == NX_CMD_SUCCESS) {
		status = simResults->getFrameAtomIds("frame-set-1", atomIds, message);
		if (status == 0) {
			status =
				simResults->getFrameAtomicNumbers("frame-set-1", atomicNumbers,
												  message);
			if (status == 0) {
				status =
					simResults->getFrameAtomPositions("frame-set-1", frameIndex,
													  atomCount, positions,
													  message);
				if (status)
					populateCommandResult(result, message.c_str());
			} else
				populateCommandResult(result, message.c_str());
		} else
			populateCommandResult(result, message.c_str());
	}
	
	// Retrieve bond data
	if ((result->getResult() == NX_CMD_SUCCESS) && (bondCount != 0)) {
		status = simResults->getFrameBonds("frame-set-1", 0, bonds, message);
		if (status)
			populateCommandResult(result, message.c_str());
	}	

	// Create a molecule and store the atoms and bonds.
	if (result->getResult() == NX_CMD_SUCCESS) {
		OBAtom* atom;
		OBBond* bond;
		SimResultsBond simResultsBond;
		OBMol* molecule = moleculeSet->newMolecule();
		unsigned int index = 0;
		for (index = 0; index < atomCount; index++) {
			atom = molecule->NewAtom();
			atom->SetIdx(atomIds[index]);
			atom->SetAtomicNum(atomicNumbers[index]);
			/// @todo Change the scale factors from 10 to 1.0e-9 after bug #2790
			/// is fixed
			// convert coords to Angstroms
			atom->SetVector(positions[index*3 + 0] * 10.0,
			                positions[index*3 + 1] * 10.0,
			                positions[index*3 + 2] * 10.0);
			NXAtomData *atomData = new NXAtomData(atomicNumbers[index]);
			atomData->setRenderStyleCode("def");
			atom->SetData(atomData);
		}
		for (index = 0; index < bondCount; index++) {
			simResultsBond = ((SimResultsBond*)bonds)[index];
			bond = molecule->NewBond();
			bond->SetBegin(molecule->GetAtom(simResultsBond.atomId_1));
			bond->SetEnd(molecule->GetAtom(simResultsBond.atomId_2));
			bond->SetBondOrder(simResultsBond.order);
		}
	}
	
	if (bonds != 0)
		free(bonds);
	
	return result;
}


/* FUNCTION: populateDataStoreInfo */
void HDF5_SimResultsImportExport::populateDataStoreInfo
		(NXDataStoreInfo* dataStoreInfo, HDF5_SimResults* simResults,
		 const string& hdf5FileDirectory, int frameSetId) {
	
	dataStoreInfo->setIsSimulationResults(true);
	
	// Input parameters
	NXProperties* properties = new NXProperties();
	vector<string> keys = simResults->getIntParameterKeys();
	vector<string>::iterator iter = keys.begin();
	int intValue;
	while (iter != keys.end()) {
		simResults->getIntParameter(*iter, intValue);
		properties->setProperty(*iter, NXUtility::itos(intValue));
		iter++;
	}
	keys = simResults->getFloatParameterKeys();
	iter = keys.begin();
	float floatValue;
	char charBuffer[16];
	while (iter != keys.end()) {
		simResults->getFloatParameter(*iter, floatValue);
		NXRealUtils::ToChar(floatValue, charBuffer, 5);
		properties->setProperty(*iter, charBuffer);
		iter++;
	}
	keys = simResults->getStringParameterKeys();
	iter = keys.begin();
	string stringValue;
	while (iter != keys.end()) {
		simResults->getStringParameter(*iter, stringValue);
		properties->setProperty(*iter, stringValue);
		iter++;
	}
	dataStoreInfo->setInputParameters(properties);

	// Input files
	keys = simResults->getFilePathKeys();
	iter = keys.begin();
	while (iter != keys.end()) {
		dataStoreInfo->addInputStructure(hdf5FileDirectory + "/" + *iter);
		iter++;
	}
	
	// Results summary
	properties = getResultsSummary(simResults);
	dataStoreInfo->setResultsSummary(properties);

	dataStoreInfo->addTrajectory("frame-set-1", frameSetId);
}


/* FUNCTION: getResultsSummary */
NXProperties* HDF5_SimResultsImportExport::getResultsSummary
		(HDF5_SimResults* simResults) {
		
	NXProperties* properties = new NXProperties();
	vector<string> keys = simResults->getIntResultKeys();
	vector<string>::iterator iter = keys.begin();
	int intValue;
	while (iter != keys.end()) {
		simResults->getIntResult(*iter, intValue);
		properties->setProperty(*iter, NXUtility::itos(intValue));
		iter++;
	}
	keys = simResults->getFloatResultKeys();
	iter = keys.begin();
	float floatValue;
	char charBuffer[16];
	while (iter != keys.end()) {
		simResults->getFloatResult(*iter, floatValue);
		NXRealUtils::ToChar(floatValue, charBuffer, 5);
		properties->setProperty(*iter, charBuffer);
		iter++;
	}
	keys = simResults->getStringResultKeys();
	iter = keys.begin();
	string stringValue;
	while (iter != keys.end()) {
		simResults->getStringResult(*iter, stringValue);
		properties->setProperty(*iter, stringValue);
		iter++;
	}
	
	simResults->getRunResult(intValue, stringValue);
	properties->setProperty("RunResult", NXUtility::itos(intValue));
	properties->setProperty("RunResultMessage", stringValue);
	return properties;
}
		 

/* FUNCTION: exportToFile */
NXCommandResult* HDF5_SimResultsImportExport::exportToFile
		(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
		 const string& filename, int frameSetId, int frameIndex) {
		
	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Create or retrieve the HDF5 data store object
	//
	HDF5_SimResults* simResults = 0;
	if (frameIndex == 0)
		simResults = new HDF5_SimResults();
		if (!dataStoreInfo->isLastFrame(frameSetId))
			dataStoreInfo->setHandle(frameSetId, simResults);
	else
		simResults = (HDF5_SimResults*)(dataStoreInfo->getHandle(frameSetId));
		
	if (simResults == 0)
		populateCommandResult(result,
							  "exportToFile: Could not instantiate or retrieve"
                              " the HDF5_SimResults object.");

	// Create the actual data store. We assume that checks for existing data
	// stores with the same name have already been done, and so clobber any
	// existing files.
	int status;
	string message;
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
		string directory = getHDF5fileDirectory(filename);
		QDir pwd;
		pwd.mkdir(directory.c_str());
		QString hdf5Filename(directory.c_str());
		hdf5Filename.append("/").append(HDF5_SIM_RESULT_FILENAME);
		QFile::remove(hdf5Filename);
		status = simResults->openDataStore(directory.c_str(), message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
	
	// Add a frame set
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
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
	void* bonds = 0;
	if (frameIndex == 0)
		bonds = (void*)malloc(bondCount*sizeof(SimResultsBond));

	// One pass through the molecule set to populate the arrays.
	unsigned int atomIndex = 0;
	unsigned int bondIndex = 0;
	if (result->getResult() == NX_CMD_SUCCESS) {
		exportToFileHelper(moleculeSet, atomIndex, bondIndex, atomIds,
						   atomicNumbers, positions, bonds, result);
	}
	
	// Write frame set info
	// Note: We assume bonds for a frame set aren't going to change and write
	//       them just to frame 0.
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
		status =
			simResults->setFrameAtomIds("frame-set-1", atomIds, atomCount,
										message);
		if (status == 0) {
			status =
				simResults->setFrameAtomicNumbers
					("frame-set-1", atomicNumbers, atomCount, message);
					
			if (status == 0) {
				status =
					simResults->setFrameBonds("frame-set-1", 0, bonds,
											  bondCount, message);
				if (status)
					populateCommandResult(result, message.c_str());
			} else
				populateCommandResult(result, message.c_str());
		} else
			populateCommandResult(result, message.c_str());
	}
	
	if (bonds != 0)
		free(bonds);

	// Write the frame
	if (result->getResult() == NX_CMD_SUCCESS) {
		status =
			simResults->setFrameAtomPositions("frame-set-1", frameIndex,
											  positions, atomCount, message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
										  
	// Close data store if this was the last frame.
	if ((simResults != 0) && (dataStoreInfo->isLastFrame(frameSetId)))
		delete simResults;
		
	return result;
}


/* FUNCTION: exportToFileHelper */
void HDF5_SimResultsImportExport::exportToFileHelper
		(NXMoleculeSet* moleculeSet, unsigned int atomIndex,
		 unsigned int bondIndex, unsigned int* atomIds,
		 unsigned int* atomicNumbers, float* positions, void* bonds,
		 NXCommandResult* result) {
		
	OBAtomIterator atomIter;
	OBBondIterator bondIter;
	SimResultsBond bond;
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
		// bonds is zero when we're not doing frame zero
		if (bonds != 0) {
			bondIter = (*moleculeIter)->BeginBonds();
			while (((*bondIter) != 0) &&
					(bondIter != (*moleculeIter)->EndBonds())) {
				bond.atomId_1 = (*bondIter)->GetBeginAtomIdx();
				bond.atomId_2 = (*bondIter)->GetEndAtomIdx();
				bond.order = (*bondIter)->GetBondOrder();
				((SimResultsBond*)bonds)[bondIndex] = bond;
				bondIndex++;
				bondIter++;
			}
		}
		moleculeIter++;
	}
	NXMoleculeSetIterator moleculeSetIter = moleculeSet->childrenBegin();
	while (moleculeSetIter != moleculeSet->childrenEnd()) {
		exportToFileHelper(*moleculeSetIter, atomIndex, bondIndex, atomIds,
						   atomicNumbers, positions, bonds, result);
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


/* FUNCTION: getHDF5fileDirectory */
string HDF5_SimResultsImportExport::getHDF5fileDirectory
		(const string& filename) {
	string directory;
	QFileInfo fileInfo(filename.c_str());
	if (fileInfo.suffix() == "h5") {
		// Pass the preceding directory to HDF5_SimResults
		directory = qPrintable(fileInfo.path());
		
	} else {
		// The suffix is ".nh5". This is an alias for a directory of the
		// same name as the filename without the suffix. Later this will
		// become an archive file.
		directory = filename.substr(0, filename.length() - 4);
	}
	return directory;
}


/* FUNCTION: fixDataStore */
NXCommandResult* HDF5_SimResultsImportExport::fixDataStore
		(const string& filename) {

	H5Eset_auto(0, 0); // Turn off HDF5 messages to stdout

	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Retrieve the HDF5 data store object
	//
	HDF5_SimResults* simResults = new HDF5_SimResults();
		
	if (simResults == 0)
		populateCommandResult(result,
							  "fixDataStore: Could not open the HDF5_SimResults object.");

	// Open the actual data store.
	int status;
	string message, hdf5FileDirectory;
	if (result->getResult() == NX_CMD_SUCCESS) {
		hdf5FileDirectory = getHDF5fileDirectory(filename);
		status = simResults->openDataStore(hdf5FileDirectory.c_str(), message);
		if (status)
			populateCommandResult(result, message.c_str());
	
		int runResult = -1; // 0=success, 1=still running, 2=failure, 3=aborted
		string failureDescription;
		simResults->getRunResult(runResult, failureDescription);
		if (runResult == 1) {
			status = simResults->setRunResult(3, "", message);
			if (status != 0) {
				message =
					string("fixDataStore: Couldn't fix data store: ") + message;
				populateCommandResult(result, message);
			}
		}
	}
	return result;
}

Q_EXPORT_PLUGIN2 (HDF5_SimResultsImportExport, HDF5_SimResultsImportExport)
