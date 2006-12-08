
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


/* FUNCTION: getSetFilePath */
void HDF5_SimResultsTest::getSetFilePath() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::string filePath;
	status = simResults->getFilePath("SimSpec", filePath);
	CPPUNIT_ASSERT(status != 0);

	std::vector<std::string> keys = simResults->getFilePathKeys();
	CPPUNIT_ASSERT(keys.size() == 0);
	
	status = simResults->setFilePath("SimSpec", "simspec.xml", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getFilePath("SimSpec", filePath);
	CPPUNIT_ASSERT((status == 0) && (filePath == "simspec.xml"));
	
	status = simResults->setFilePath("SimFlow", "simflow.tcl", message);
	CPPUNIT_ASSERT(status == 0);
	
	keys = simResults->getFilePathKeys();
	CPPUNIT_ASSERT(keys.size() == 2);
	CPPUNIT_ASSERT(keys[0] == "SimSpec");
	CPPUNIT_ASSERT(keys[1] == "SimFlow");
	
	delete simResults;
}


/* FUNCTION: getSetRunResult */
void HDF5_SimResultsTest::getSetRunResult() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	int result;
	std::string failureDesc;
	status = simResults->getRunResult(result, failureDesc);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setRunResult(0, 0, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getRunResult(result, failureDesc);
	CPPUNIT_ASSERT((status == 0) && (result == 0));
	
	status = simResults->setRunResult(2, "It blew up.", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getRunResult(result, failureDesc);
	CPPUNIT_ASSERT((status == 0) &&
				   (result == 2) && (failureDesc == "It blew up."));
	
	delete simResults;
}


/* FUNCTION: getSetStepCount */
void HDF5_SimResultsTest::getSetStepCount() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	int stepCount;
	status = simResults->getStepCount(stepCount);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setStepCount(100, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getStepCount(stepCount);
	CPPUNIT_ASSERT((status == 0) && (stepCount == 100));
	
	delete simResults;
}


/* FUNCTION: getSetStartTime */
void HDF5_SimResultsTest::getSetStartTime() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	time_t startTime;
	status = simResults->getStartTime(startTime);
	CPPUNIT_ASSERT(status != 0);
	
	time(&startTime);
	status = simResults->setStartTime(startTime, message);
	CPPUNIT_ASSERT(status == 0);
	
	time_t retrievedStartTime;
	status = simResults->getStartTime(retrievedStartTime);
	CPPUNIT_ASSERT((status == 0) && (retrievedStartTime == startTime));
	
	delete simResults;
}


/* FUNCTION: getSetCPU_RunningTime */
void HDF5_SimResultsTest::getSetCPU_RunningTime() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	float runningTime;
	status = simResults->getCPU_RunningTime(runningTime);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setCPU_RunningTime(100.1f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getCPU_RunningTime(runningTime);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(100.1, runningTime, 0.01);
	
	delete simResults;
}


/* FUNCTION: getSetWallRunningTime */
void HDF5_SimResultsTest::getSetWallRunningTime() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	float runningTime;
	status = simResults->getWallRunningTime(runningTime);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setWallRunningTime(110.1f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getWallRunningTime(runningTime);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(110.1, runningTime, 0.01);
	
	delete simResults;
}


/* FUNCTION: addGetRemoveFrameSet */
void HDF5_SimResultsTest::addGetRemoveFrameSet() {
	int status;
	std::string message;
	
	simResults = new ne1::HDF5_SimResults();
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
	
	std::vector<std::string> frameSetNames = simResults->getFrameSetNames();
	CPPUNIT_ASSERT(frameSetNames.size() == 0);

	status = simResults->addFrameSet("frame-set-1", message);
	CPPUNIT_ASSERT(status == 0);
	status = simResults->addFrameSet("frame-set-2", message);
	CPPUNIT_ASSERT(status == 0);
	
	frameSetNames = simResults->getFrameSetNames();
	CPPUNIT_ASSERT(frameSetNames.size() == 2);
	CPPUNIT_ASSERT(frameSetNames[0] == "frame-set-1");
	CPPUNIT_ASSERT(frameSetNames[1] == "frame-set-2");
	
	delete simResults;
}
