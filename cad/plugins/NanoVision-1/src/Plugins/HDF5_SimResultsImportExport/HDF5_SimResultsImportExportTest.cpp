// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExportTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(HDF5_SimResultsImportExportTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(HDF5_SimResultsImportExportTest, "HDF5_SimResultsImportExportTestSuite");


/* FUNCTION: setUp */
void HDF5_SimResultsImportExportTest::setUp() {
	logger = new NXLogger();
	//logger->addHandler(new NXConsoleLogHandler(NXLogLevel_Info));
	entityManager = new NXEntityManager();
		
	NXProperties* properties = new NXProperties();
	properties->setProperty("NXEntityManager.importExport.0.plugin",
							"libHDF5_SimResultsImportExport");
	properties->setProperty("NXEntityManager.importExport.0.importFormats",
							"nh5");
	properties->setProperty("NXEntityManager.importExport.0.exportFormats",
							"nh5");
	entityManager->loadDataImportExportPlugins(properties);
	delete properties;
}


/* FUNCTION: tearDown */
void HDF5_SimResultsImportExportTest::tearDown() {
	delete entityManager;
	delete logger;
}


/* FUNCTION: basicExportTest */
void HDF5_SimResultsImportExportTest::basicExportTest() {

	// Create a water molecule
	//
	NXMoleculeSet* rootMoleculeSet = entityManager->getRootMoleculeSet();
	OBMol* molecule = rootMoleculeSet->newMolecule();
	OBAtom* atomO = molecule->NewAtom();
	atomO->SetAtomicNum(etab.GetAtomicNum("O")); // Oxygen
	atomO->SetVector(0.00000000, 0.00000000, 0.37000000); // Angstroms
	OBAtom* atomH1 = molecule->NewAtom();
	atomH1->SetAtomicNum(etab.GetAtomicNum("H")); // Hydrogen
	atomH1->SetVector(0.78000000, 0.00000000, -0.18000000);
	OBAtom* atomH2 = molecule->NewAtom();
	atomH2->SetAtomicNum(etab.GetAtomicNum("H")); // Hydrogen
	atomH2->SetVector(-0.78000000, 0.00000000, -0.18000000);
	OBBond* bond = molecule->NewBond();
	bond->SetBegin(atomO);
	bond->SetEnd(atomH1);
	bond = molecule->NewBond();
	bond->SetBegin(atomO);
	bond->SetEnd(atomH2);
	
	// Write it as frame 0 with the HDF5_SimResultsImportExport plugin
	NXDataStoreInfo* dataStoreInfo = new NXDataStoreInfo();
	dataStoreInfo->setLastFrame(false);
	NXCommandResult* commandResult =
		entityManager->exportToFile(rootMoleculeSet, dataStoreInfo, "nh5",
									"testHDF5store", 0);
	if (commandResult->getResult() != NX_CMD_SUCCESS)
		printf("\n%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
	CPPUNIT_ASSERT(commandResult->getResult() == NX_CMD_SUCCESS);
	
	// Tweak the molecule a bit and add it as frame 1
	molecule->GetFirstAtom()->SetVector(0.12000000, 0.34000000, 0.37000000);
	dataStoreInfo->setLastFrame(true);
	commandResult =
		entityManager->exportToFile(rootMoleculeSet, dataStoreInfo, "nh5",
									"testHDF5store", 1);
	if (commandResult->getResult() != NX_CMD_SUCCESS)
		printf("\n%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
	CPPUNIT_ASSERT(commandResult->getResult() == NX_CMD_SUCCESS);
}
