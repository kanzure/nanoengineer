
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
	
	std::string name;
	status = simResults->getName(name);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setName("Hydrocarbon deposition", message);
	CPPUNIT_ASSERT(status == 0);

	status = simResults->getName(name);
	CPPUNIT_ASSERT((status == 0) && (name == "Hydrocarbon deposition"));

	delete simResults;
}


/* FUNCTION: getSetDescription */
void HDF5_SimResultsTest::getSetDescription() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string description;
	status = simResults->getDescription(description);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setDescription
		("A nice informative description.", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getDescription(description);
	CPPUNIT_ASSERT((status == 0) &&
				   (description == "A nice informative description."));
	
	delete simResults;
}


/* FUNCTION: getSetNotes */
void HDF5_SimResultsTest::getSetNotes() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string notes;
	status = simResults->getNotes(notes);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setNotes("User's notes", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getNotes(notes);
	CPPUNIT_ASSERT((status == 0) && (notes == "User's notes"));
	
	delete simResults;
}


/* FUNCTION: getSetTimestep */
void HDF5_SimResultsTest::getSetTimestep() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	float timestep;
	status = simResults->getTimestep(timestep);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setTimestep(1.234f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getTimestep(timestep);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(1.234, timestep, 0.0001);
	delete simResults;
}


/* FUNCTION: getSetStartStep */
void HDF5_SimResultsTest::getSetStartStep() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	int startStep;
	status = simResults->getStartStep(startStep);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setStartStep(5, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getStartStep(startStep);
	CPPUNIT_ASSERT((status == 0) && (startStep == 5));
	delete simResults;
}


/* FUNCTION: getSetMaxSteps */
void HDF5_SimResultsTest::getSetMaxSteps() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	int maxSteps;
	status = simResults->getMaxSteps(maxSteps);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setMaxSteps(10, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getMaxSteps(maxSteps);
	CPPUNIT_ASSERT((status == 0) && (maxSteps == 10));
	delete simResults;
}


/* FUNCTION: getSetEnvironmentTemperature */
void HDF5_SimResultsTest::getSetEnvironmentTemperature() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	float envTemp;
	status = simResults->getEnvironmentTemperature(envTemp);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setEnvironmentTemperature(5.678f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getEnvironmentTemperature(envTemp);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(5.678, envTemp, 0.0001);
	delete simResults;
}


/* FUNCTION: getSetEnvironmentPressure */
void HDF5_SimResultsTest::getSetEnvironmentPressure() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	float envPress;
	status = simResults->getEnvironmentPressure(envPress);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setEnvironmentPressure(9.101f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getEnvironmentPressure(envPress);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(9.101, envPress, 0.0001);
	delete simResults;
}
