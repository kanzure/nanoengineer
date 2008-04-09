
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_Consumer.h"


/* FUNCTION: render */
void HDF5_Consumer::render(int frameSetId, int frameIndex,
						   NXMoleculeSet* newMoleculeSet) {
	
	// Start printing all frames available from the first render() call
	unsigned int frameCount = 0;
	NXMoleculeSet* moleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, _frameIndex);
	while (moleculeSet != 0) {
		printf("\n==========================\n");
		frameCount = entityManager->getFrameCount(frameSetId);
		OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
		printf("%d ", (*moleculeIter)->GetAtom(1)->GetAtomicNum());
		printf("%g ", (*moleculeIter)->GetAtom(1)->GetZ());
		printf("%d ", (*moleculeIter)->NumBonds());
		printf("sC=%d ",
			   entityManager->getDataStoreInfo()->storeIsComplete(frameSetId));
		printf("frame: %d%s/%d\n",
			   _frameIndex+1,
			   (moleculeSet == newMoleculeSet ? "*" : ""),
			   frameCount);

		_frameIndex++;
		moleculeSet =
			entityManager->getRootMoleculeSet(frameSetId, _frameIndex);
	}
	
	// Stop once the data store is complete
	if (entityManager->getDataStoreInfo()->storeIsComplete(frameSetId))
		exit(0);
}


/* FUNCTION: main */
int main(int argc, char* argv[]) {
	QCoreApplication app(argc, argv);

	// Set the entity manager up
	//
	NXEntityManager* entityManager = new NXEntityManager();
		
	NXProperties* properties = new NXProperties();
	properties->setProperty("ImportExport.0.plugin",
							"HDF5_SimResultsImportExport");
	properties->setProperty("ImportExport.0.exportFormats",
							"HDF5 Simulation Results (*.h5 *.nh5)");
	properties->setProperty("ImportExport.0.importFormats",
							"HDF5 Simulation Results (*.h5 *.nh5)");
	entityManager->loadDataImportExportPlugins(properties);
	delete properties;

	// Prime read
	NXCommandResult* commandResult =
		entityManager->importFromFile("Testing/shared.nh5");
	if (commandResult->getResult() != NX_CMD_SUCCESS) {
		printf("%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
		exit(1);
	}

	// Discover a store-not-complete trajectory frame set
	NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
	int trajId = dataStoreInfo->getTrajectoryId("frame-set-1");
	if (dataStoreInfo->storeIsComplete(trajId)) {
		printf("error: data store is complete\n");
		exit(1);
	}

	// Display frames
	HDF5_Consumer* hdf5Consumer = new HDF5_Consumer(entityManager);
	QObject::connect(entityManager,
					 SIGNAL(newFrameAdded(int, int, NXMoleculeSet*)),
					 hdf5Consumer,
					 SLOT(render(int, int, NXMoleculeSet*)));
	
	return app.exec();
}
