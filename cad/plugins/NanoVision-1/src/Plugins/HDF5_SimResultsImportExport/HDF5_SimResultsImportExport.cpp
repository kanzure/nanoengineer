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

	// Open the actual data store.
	int status;
	string message;
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
		QString hdf5Filename(filename.c_str());
		hdf5Filename.append("/").append(HDF5_SIM_RESULT_FILENAME);
		status = simResults->openDataStore(filename.c_str(), message);
		if (status)
			populateCommandResult(result, message.c_str());
	}
	
	unsigned int atomCount = 0;
	unsigned int bondCount = 0;
	if (result->getResult() == NX_CMD_SUCCESS) {
		// Retrieve stored counts
		simResults->getFrameAtomIdsCount("frame-set-1", atomCount);
		simResults->getFrameBondsCount("frame-set-1", 0, bondCount);
	}
	
	unsigned int atomIds[atomCount];
	unsigned int atomicNumbers[atomCount];
	float positions[atomCount*3];
	void* bonds = (void*)malloc(bondCount*sizeof(SimResultsBond));

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
	if (result->getResult() == NX_CMD_SUCCESS) {
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
			atom->SetVector(positions[index*3 + 0], positions[index*3 + 1],
							positions[index*3 + 2]);
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
	if ((frameIndex == 0) && (result->getResult() == NX_CMD_SUCCESS)) {
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
	if ((simResults != 0) && (dataStoreInfo->isLastFrame()))
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
