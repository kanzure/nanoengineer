// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "HDF5_SimResultsImportExportTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(HDF5_SimResultsImportExportTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(HDF5_SimResultsImportExportTest, "HDF5_SimResultsImportExportTestSuite");


/* FUNCTION: setUp */
void HDF5_SimResultsImportExportTest::setUp() {
	logger = new NXLogger();
	logger->addHandler(new NXConsoleLogHandler(NXLogLevel_Info));
	entityManager = new NXEntityManager();
}


/* FUNCTION: tearDown */
void HDF5_SimResultsImportExportTest::tearDown() {
	delete entityManager;
	delete logger;
}


/* FUNCTION: basicTest */
void HDF5_SimResultsImportExportTest::basicTest() {
	NXProperties* properties = new NXProperties();
	properties->setProperty("NXEntityManager.importExport.0.plugin",
							"../../../lib/libHDF5_SimResultsImportExport");
	properties->setProperty("NXEntityManager.importExport.0.importFormats",
							"nh5");
	properties->setProperty("NXEntityManager.importExport.0.exportFormats",
							"nh5");
	entityManager->loadDataImportExportPlugins(properties);
	CPPUNIT_ASSERT(true);
}
