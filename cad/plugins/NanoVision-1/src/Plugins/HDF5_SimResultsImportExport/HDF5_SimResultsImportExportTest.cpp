// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExportTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(HDF5_SimResultsImportExportTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(HDF5_SimResultsImportExportTest,
                                      "HDF5_SimResultsImportExportTestSuite");


/* FUNCTION: setUp */
void HDF5_SimResultsImportExportTest::setUp() {
	logger = new NXLogger();
	//logger->addHandler(new NXConsoleLogHandler(NXLogLevel_Info));
	entityManager = new NXEntityManager();
		
	NXProperties* properties = new NXProperties();
	properties->setProperty("PluginsSearchPath", "../lib");
	properties->setProperty("ImportExport.0.plugin",
							"HDF5_SimResultsImportExport");
	properties->setProperty("ImportExport.0.exportFormats",
							"HDF5 Simulation Results (*.h5 *.nh5)");
	properties->setProperty("ImportExport.0.importFormats",
							"HDF5 Simulation Results (*.h5 *.nh5)");
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

	// Create a water molecule for frame 0
	//
	int frameSetId = entityManager->addFrameSet();
	int frameIndex = entityManager->addFrame(frameSetId);
	NXMoleculeSet* rootMoleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
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

	// Create a distorted water molecule for frame 1
	//
	frameIndex = entityManager->addFrame(frameSetId);
	rootMoleculeSet = entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	molecule = rootMoleculeSet->newMolecule();
	atomO = molecule->NewAtom();
	atomO->SetAtomicNum(etab.GetAtomicNum("O")); // Oxygen
	atomO->SetVector(0.10000000, 0.20000000, 0.37000000); // Angstroms
	atomH1 = molecule->NewAtom();
	atomH1->SetAtomicNum(etab.GetAtomicNum("H")); // Hydrogen
	atomH1->SetVector(0.78000000, 0.10000000, -0.18000000);
	atomH2 = molecule->NewAtom();
	atomH2->SetAtomicNum(etab.GetAtomicNum("H")); // Hydrogen
	atomH2->SetVector(-0.78000000, 0.10000000, -0.18000000);
	bond = molecule->NewBond();
	bond->SetBegin(atomO);
	bond->SetEnd(atomH1);
	bond = molecule->NewBond();
	bond->SetBegin(atomO);
	bond->SetEnd(atomH2);
	
	// Write it with the HDF5_SimResultsImportExport plugin
	NXCommandResult* commandResult =
		entityManager->exportToFile("testHDF5store.nh5", frameSetId, -1);
	if (commandResult->getResult() != NX_CMD_SUCCESS)
		printf("\n%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
	CPPUNIT_ASSERT(commandResult->getResult() == NX_CMD_SUCCESS);
}


/* FUNCTION: basicImportTest */
void HDF5_SimResultsImportExportTest::basicImportTest() {

	// Read with the HDF5_SimResultsImportExport plugin
	NXCommandResult* commandResult =
		entityManager->importFromFile("testHDF5store.nh5");
	if (commandResult->getResult() != NX_CMD_SUCCESS)
		printf("\n%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
	CPPUNIT_ASSERT(commandResult->getResult() == NX_CMD_SUCCESS);
	
	NXMoleculeSet* rootMoleculeSet = entityManager->getRootMoleculeSet(0, 0);
	CPPUNIT_ASSERT(rootMoleculeSet != 0);
	OBMolIterator moleculeIter = rootMoleculeSet->moleculesBegin();
	CPPUNIT_ASSERT((*moleculeIter)->GetAtom(1)->GetAtomicNum() == 8);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.37, (*moleculeIter)->GetAtom(1)->GetZ(),
								 0.001);
	CPPUNIT_ASSERT((*moleculeIter)->NumBonds() == 2);
	
	rootMoleculeSet = entityManager->getRootMoleculeSet(0, 1);
	CPPUNIT_ASSERT(rootMoleculeSet != 0);
	moleculeIter = rootMoleculeSet->moleculesBegin();
	CPPUNIT_ASSERT((*moleculeIter)->GetAtom(2)->GetAtomicNum() == 1);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.1, (*moleculeIter)->GetAtom(2)->GetY(),
								 0.001);
	CPPUNIT_ASSERT((*moleculeIter)->NumBonds() == 2);
}
