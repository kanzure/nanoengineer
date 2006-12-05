
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#include "HDF5_SimResultsTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(HDF5_SimResultsTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(HDF5_SimResultsTest, "HDF5_SimResultsTestSuite");

/* FUNCTION: setUp */
void HDF5_SimResultsTest::setUp() {
}


/* FUNCTION: tearDown */
void HDF5_SimResultsTest::tearDown() {
}


/* FUNCTION: openDataStore */
void HDF5_SimResultsTest::openDataStore() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	
	status = simResults->openDataStore("non-existent-directory", message);
	CPPUNIT_ASSERT(status == SRDS_UNABLE_TO_OPEN_FILE);

	status = simResults->openDataStore("Testing/bad-hdf5-file", message);
	CPPUNIT_ASSERT(status == SRDS_UNABLE_TO_OPEN_FILE);
	
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);

	delete simResults;
}


/* FUNCTION: getSetName */
void HDF5_SimResultsTest::getSetName() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->setName("Hydrocarbon deposition", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string name = simResults->getName();
	CPPUNIT_ASSERT(name == "Hydrocarbon deposition");
	
	delete simResults;
}


/* FUNCTION: getSetDescription */
void HDF5_SimResultsTest::getSetDescription() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->setDescription
		("A nice informative description.", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string description = simResults->getDescription();
	CPPUNIT_ASSERT(description == "A nice informative description.");
	
	delete simResults;
}


/* FUNCTION: getSetNotes */
void HDF5_SimResultsTest::getSetNotes() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->setNotes("User's notes", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string notes = simResults->getNotes();
	CPPUNIT_ASSERT(notes == "User's notes");
	
	delete simResults;
}
