
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "HDF5_SimResultsTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(HDF5_SimResultsTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(HDF5_SimResultsTest, "HDF5_SimResultsTestSuite");

/* FUNCTION: setUp */
void HDF5_SimResultsTest::setUp() {
	simResults = new ne1::HDF5_SimResults();

	std::string message;
	int status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);
}


/* FUNCTION: tearDown */
void HDF5_SimResultsTest::tearDown() {
	delete simResults;
}


/* FUNCTION: openDataStore */
void HDF5_SimResultsTest::openDataStore() {
	int status;
	std::string message;
	
	delete simResults;
	simResults = new ne1::HDF5_SimResults();
	
	status = simResults->openDataStore("non-existent-directory", message);
	CPPUNIT_ASSERT(status == SRDS_UNABLE_TO_OPEN_FILE);

	status = simResults->openDataStore("Testing/bad-hdf5-file", message);
	CPPUNIT_ASSERT(status == SRDS_UNABLE_TO_OPEN_FILE);
	
	status = simResults->openDataStore("Testing", message);
	CPPUNIT_ASSERT(status == 0);

}


/* FUNCTION: getSetName */
void HDF5_SimResultsTest::getSetName() {
	int status;
	std::string message;
	
	std::string name;
	status = simResults->getName(name);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setName("Hydrocarbon deposition xxx", message);
	CPPUNIT_ASSERT(status == 0);
	status = simResults->setName("Hydrocarbon deposition", message);
	CPPUNIT_ASSERT(status == 0);

	status = simResults->getName(name);
	CPPUNIT_ASSERT((status == 0) && (name == "Hydrocarbon deposition"));
}


/* FUNCTION: getSetDescription */
void HDF5_SimResultsTest::getSetDescription() {
	int status;
	std::string message;
	
	std::string description;
	status = simResults->getDescription(description);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setDescription
		("A nice informative description.", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getDescription(description);
	CPPUNIT_ASSERT((status == 0) &&
				   (description == "A nice informative description."));
}


/* FUNCTION: getSetNotes */
void HDF5_SimResultsTest::getSetNotes() {
	int status;
	std::string message;
	
	std::string notes;
	status = simResults->getNotes(notes);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setNotes("User's notes", message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getNotes(notes);
	CPPUNIT_ASSERT((status == 0) && (notes == "User's notes"));
}


/* FUNCTION: getSetTimestep */
void HDF5_SimResultsTest::getSetTimestep() {
	int status;
	std::string message;
	
	float timestep;
	status = simResults->getTimestep(timestep);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setTimestep(1.234f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getTimestep(timestep);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(1.234, timestep, 0.0001);
}


/* FUNCTION: getSetStartStep */
void HDF5_SimResultsTest::getSetStartStep() {
	int status;
	std::string message;
	
	int startStep;
	status = simResults->getStartStep(startStep);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setStartStep(5, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getStartStep(startStep);
	CPPUNIT_ASSERT((status == 0) && (startStep == 5));
}


/* FUNCTION: getSetMaxSteps */
void HDF5_SimResultsTest::getSetMaxSteps() {
	int status;
	std::string message;
	
	int maxSteps;
	status = simResults->getMaxSteps(maxSteps);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setMaxSteps(10, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getMaxSteps(maxSteps);
	CPPUNIT_ASSERT((status == 0) && (maxSteps == 10));
}


/* FUNCTION: getSetEnvironmentTemperature */
void HDF5_SimResultsTest::getSetEnvironmentTemperature() {
	int status;
	std::string message;
	
	float envTemp;
	status = simResults->getEnvironmentTemperature(envTemp);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setEnvironmentTemperature(5.678f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getEnvironmentTemperature(envTemp);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(5.678, envTemp, 0.0001);
}


/* FUNCTION: getSetEnvironmentPressure */
void HDF5_SimResultsTest::getSetEnvironmentPressure() {
	int status;
	std::string message;
	
	float envPress;
	status = simResults->getEnvironmentPressure(envPress);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setEnvironmentPressure(9.101f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getEnvironmentPressure(envPress);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(9.101, envPress, 0.0001);
}


/* FUNCTION: getSetFilePath */
void HDF5_SimResultsTest::getSetFilePath() {
	int status;
	std::string message;
	
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
}


/* FUNCTION: getSetRunResult */
void HDF5_SimResultsTest::getSetRunResult() {
	int status;
	std::string message;
	
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
}


/* FUNCTION: getSetStepCount */
void HDF5_SimResultsTest::getSetStepCount() {
	int status;
	std::string message;
	
	int stepCount;
	status = simResults->getStepCount(stepCount);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setStepCount(100, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getStepCount(stepCount);
	CPPUNIT_ASSERT((status == 0) && (stepCount == 100));
}


/* FUNCTION: getSetStartTime */
void HDF5_SimResultsTest::getSetStartTime() {
	int status;
	std::string message;
	
	time_t startTime;
	status = simResults->getStartTime(startTime);
	CPPUNIT_ASSERT(status != 0);
	
	time(&startTime);
	status = simResults->setStartTime(startTime, message);
	CPPUNIT_ASSERT(status == 0);
	
	time_t retrievedStartTime;
	status = simResults->getStartTime(retrievedStartTime);
	CPPUNIT_ASSERT((status == 0) && (retrievedStartTime == startTime));
}


/* FUNCTION: getSetCPU_RunningTime */
void HDF5_SimResultsTest::getSetCPU_RunningTime() {
	int status;
	std::string message;
	
	float runningTime;
	status = simResults->getCPU_RunningTime(runningTime);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setCPU_RunningTime(100.1f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getCPU_RunningTime(runningTime);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(100.1, runningTime, 0.01);
}


/* FUNCTION: getSetWallRunningTime */
void HDF5_SimResultsTest::getSetWallRunningTime() {
	int status;
	std::string message;
	
	float runningTime;
	status = simResults->getWallRunningTime(runningTime);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setWallRunningTime(110.1f, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getWallRunningTime(runningTime);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(110.1, runningTime, 0.01);
}


/* FUNCTION: getAddRemoveFrameSet */
void HDF5_SimResultsTest::getAddRemoveFrameSet() {
	int status;
	std::string message;

	std::vector<std::string> frameSetNames = simResults->getFrameSetNames();
	CPPUNIT_ASSERT(frameSetNames.size() == 0);

	status = simResults->addFrameSet("frame-set-1", message);
	CPPUNIT_ASSERT(status == 0);
	status = simResults->addFrameSet("frame-set-1", message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->addFrameSet("frame-set-2", message);
	CPPUNIT_ASSERT(status == 0);
	
	frameSetNames = simResults->getFrameSetNames();
	CPPUNIT_ASSERT(frameSetNames.size() == 2);
	CPPUNIT_ASSERT(frameSetNames[0] == "frame-set-1");
	CPPUNIT_ASSERT(frameSetNames[1] == "frame-set-2");
}


/* FUNCTION: getSetAggregationMode */
void HDF5_SimResultsTest::getSetAggregationMode() {
	int status;
	std::string message;
	
	int mode;
	status = simResults->getAggregationMode("frame-set-X", mode);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->getAggregationMode("frame-set-1", mode);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->setAggregationMode("frame-set-X", 1, message);
	CPPUNIT_ASSERT(status == SRDS_NON_EXISTENT_FRAMESET);
	
	status = simResults->setAggregationMode("frame-set-1", 1, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getAggregationMode("frame-set-1", mode);
	CPPUNIT_ASSERT((status == 0) && (mode == 1));
}


/* FUNCTION: getSetStepsPerFrame */
void HDF5_SimResultsTest::getSetStepsPerFrame() {
	int status;
	std::string message;
	
	int stepsPerFrame;
	status = simResults->getStepsPerFrame("frame-set-X", stepsPerFrame);
	CPPUNIT_ASSERT(status != 0);
	
	status = simResults->getStepsPerFrame("frame-set-1", stepsPerFrame);
	CPPUNIT_ASSERT(status != 0);
	
	status =
		simResults->setStepsPerFrame("frame-set-X", 10, message);
	CPPUNIT_ASSERT(status == SRDS_NON_EXISTENT_FRAMESET);
	
	status = simResults->setStepsPerFrame("frame-set-1", 10, message);
	CPPUNIT_ASSERT(status == 0);
	
	status = simResults->getStepsPerFrame("frame-set-1", stepsPerFrame);
	CPPUNIT_ASSERT((status == 0) && (stepsPerFrame == 10));
}

/* FUNCTION: getAddRemoveFrame */
void HDF5_SimResultsTest::getAddRemoveFrame() {
	int status;
	std::string message;
	
	int frameCount;
	simResults->getFrameCount("frame-set-X", frameCount);
	CPPUNIT_ASSERT(frameCount == 0);
	simResults->getFrameCount("frame-set-1", frameCount);
	CPPUNIT_ASSERT(frameCount == 0);
	
	float* frameTimes;
	status =
		simResults->getFrameTimes("frame-set-X", frameTimes, message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->getFrameTimes("frame-set-1", frameTimes, message);
	CPPUNIT_ASSERT(status != 0);
	
	float frameTime;
	status = simResults->getFrameTime("frame-set-X", 0, frameTime, message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->getFrameTime("frame-set-1", 0, frameTime, message);
	CPPUNIT_ASSERT(status != 0);
	
	int index;
	status = simResults->addFrame("frame-set-X", 0.0, index, message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->addFrame("frame-set-1", 0.0, index, message);
	CPPUNIT_ASSERT((status == 0) && (index == 0));
	status = simResults->addFrame("frame-set-1", 0.5, index, message);
	CPPUNIT_ASSERT((status == 0) && (index == 1));

	simResults->getFrameCount("frame-set-1", frameCount);
	CPPUNIT_ASSERT(frameCount == 2);

	frameTimes = (float*)(malloc(frameCount * sizeof(float)));
	status =
		simResults->getFrameTimes("frame-set-1", frameTimes, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.0, frameTimes[0], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.5, frameTimes[1], 0.001);
	
	status = simResults->getFrameTime("frame-set-1", 0, frameTime, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.0, frameTime, 0.001);
	status = simResults->getFrameTime("frame-set-1", 1, frameTime, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.5, frameTime, 0.001);
	status = simResults->getFrameTime("frame-set-1", 2, frameTime, message);
	CPPUNIT_ASSERT(status != 0);
}


/* FUNCTION: getSetAtomIds */
void HDF5_SimResultsTest::getSetAtomIds() {
	int status;
	std::string message;
	
	unsigned int atomIdsCount = 5;
	simResults->getFrameAtomIdsCount("frame-set-X", atomIdsCount);
	CPPUNIT_ASSERT(atomIdsCount == 0);
	simResults->getFrameAtomIdsCount("frame-set-1", atomIdsCount);
	CPPUNIT_ASSERT(atomIdsCount == 0);
	
	unsigned int atomIds[] = { 0, 1, 2 };
	status = simResults->setFrameAtomIds("frame-set-X", atomIds, 3, message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->setFrameAtomIds("frame-set-1", atomIds, 3, message);
	CPPUNIT_ASSERT(status == 0);
	
	atomIds[0] = 5; atomIds[1] = 6; atomIds[2] = 7;
	status = simResults->getFrameAtomIds("frame-set-1", atomIds, message);
	CPPUNIT_ASSERT((status == 0) && (atomIds[0] == 0) && (atomIds[1] == 1) &&
				   (atomIds[2] == 2));
	
	simResults->getFrameAtomIdsCount("frame-set-1", atomIdsCount);
	CPPUNIT_ASSERT(atomIdsCount == 3);
}


/* FUNCTION: getSetAtomicNumbers */
void HDF5_SimResultsTest::getSetAtomicNumbers() {
	int status;
	std::string message;
	
	unsigned int atomicNumbers[] = { 1, 6, 8 };
	status =
		simResults->setFrameAtomicNumbers
			("frame-set-X", atomicNumbers, 3, message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->setFrameAtomicNumbers
			("frame-set-1", atomicNumbers, 3, message);
	CPPUNIT_ASSERT(status == 0);
	
	atomicNumbers[0] = 5; atomicNumbers[1] = 6; atomicNumbers[2] = 7;
	status =
		simResults->getFrameAtomicNumbers
			("frame-set-1", atomicNumbers, message);
	CPPUNIT_ASSERT((status == 0) && (atomicNumbers[0] == 1) &&
				   (atomicNumbers[1] == 6) && (atomicNumbers[2] == 8));
}


/* FUNCTION: getSetAtomPositions */
void HDF5_SimResultsTest::getSetAtomPositions() {
	int status;
	std::string message;
	
	int nAtoms = 3;
	float positions[nAtoms*3];
	
	//
	status =
		simResults->getFrameAtomPositions("frame-set-X", 0, 3, positions,
										  message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->getFrameAtomPositions("frame-set-1", 0, 3, positions,
										  message);
	CPPUNIT_ASSERT(status != 0);
	
	//
	status =
		simResults->setFrameAtomPositions("frame-set-X", 0, positions, 3,
										  message);
	CPPUNIT_ASSERT(status != 0);
	
	//
	int atomIndex;
	for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
		positions[atomIndex*3+0] = atomIndex * 3.0f;
		positions[atomIndex*3+1] = atomIndex * 3.0f + 1.0f;
		positions[atomIndex*3+2] = atomIndex * 3.0f + 2.0f;
	}
	status =
		simResults->setFrameAtomPositions("frame-set-1", 0, positions, 3,
										  message);
	CPPUNIT_ASSERT(status == 0);
	
	//
	for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
		positions[atomIndex*3+0] = atomIndex * 3.0f + 9.0f;
		positions[atomIndex*3+1] = atomIndex * 3.0f + 10.0f;
		positions[atomIndex*3+2] = atomIndex * 3.0f + 11.0f;
	}
	status =
		simResults->setFrameAtomPositions("frame-set-1", 1, positions, 3,
										  message);
	CPPUNIT_ASSERT(status == 0);
	
	//
	status =
		simResults->getFrameAtomPositions("frame-set-1", 0, 3, positions,
										  message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(1.0, positions[1], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(5.0, positions[5], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(8.0, positions[8], 0.001);
	
	//
	status =
		simResults->getFrameAtomPositions("frame-set-1", 1, 3, positions,
										  message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(10.0, positions[1], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(14.0, positions[5], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(17.0, positions[8], 0.001);
}


/* FUNCTION: getSetAtomVelocities */
void HDF5_SimResultsTest::getSetAtomVelocities() {
	int status;
	std::string message;
	
	int nAtoms = 3;
	float velocities[nAtoms*3];
	int atomIndex;
	for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
		velocities[atomIndex*3+0] = atomIndex * 3.0f;
		velocities[atomIndex*3+1] = atomIndex * 3.0f + 1.0f;
		velocities[atomIndex*3+2] = atomIndex * 3.0f + 2.0f;
	}
	
	status =
		simResults->getFrameAtomVelocities("frame-set-X", 0, 3, velocities,
										   message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->getFrameAtomVelocities("frame-set-1", 0, 3, velocities,
										   message);
	CPPUNIT_ASSERT(status != 0);
	
	status =
		simResults->setFrameAtomVelocities("frame-set-X", 0, velocities, 3,
										   message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->setFrameAtomVelocities("frame-set-1", 0, velocities, 3,
										   message);
	CPPUNIT_ASSERT(status == 0);
	
	for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
		velocities[atomIndex*3+0] = 0.0f;
		velocities[atomIndex*3+1] = 0.0f;
		velocities[atomIndex*3+2] = 0.0f;
	}
	status =
		simResults->getFrameAtomVelocities("frame-set-1", 0, 3, velocities,
										   message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(1.0, velocities[1], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(5.0, velocities[5], 0.001);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(8.0, velocities[8], 0.001);
}


/* FUNCTION: getSetBonds */
void HDF5_SimResultsTest::getSetBonds() {
	int status;
	std::string message;
	
	unsigned int bondCount = 99;
	simResults->getFrameBondsCount("frame-set-X", 0, bondCount);
	CPPUNIT_ASSERT(bondCount == 0);
	simResults->getFrameBondsCount("frame-set-1", 0, bondCount);
	CPPUNIT_ASSERT(bondCount == 0);
	
	void* bonds = (void*)malloc(3*sizeof(ne1::SimResultsBond));
	unsigned int bondIndex;
	ne1::SimResultsBond bond;
	for (bondIndex = 0; bondIndex < 3; bondIndex++) {
		bond.atomId_1 = bondIndex;
		bond.atomId_2 = bondIndex + 1;
		bond.order = bondIndex + 0.5f;
		((ne1::SimResultsBond*)bonds)[bondIndex] = bond;
	}
	status = simResults->setFrameBonds("frame-set-X", 0, bonds, 3, message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->setFrameBonds("frame-set-1", 0, bonds, 3, message);
	CPPUNIT_ASSERT(status == 0);
	free(bonds);

	bonds = (void*)malloc(5*sizeof(ne1::SimResultsBond));
	for (bondIndex = 0; bondIndex < 5; bondIndex++) {
		bond.atomId_1 = 10+bondIndex;
		bond.atomId_2 = 10+bondIndex + 1;
		bond.order = bondIndex + 1.5f;
		((ne1::SimResultsBond*)bonds)[bondIndex] = bond;
	}
	status = simResults->setFrameBonds("frame-set-1", 1, bonds, 5, message);
	CPPUNIT_ASSERT(status == 0);
	
	simResults->getFrameBondsCount("frame-set-1", 0, bondCount);
	CPPUNIT_ASSERT(bondCount == 3);
	simResults->getFrameBondsCount("frame-set-1", 1, bondCount);
	CPPUNIT_ASSERT(bondCount == 5);
	
	status = simResults->getFrameBonds("frame-set-X", 0, bonds, message);
	CPPUNIT_ASSERT(status != 0);
	status = simResults->getFrameBonds("frame-set-1", 0, bonds, message);
	CPPUNIT_ASSERT(status == 0);
	for (bondIndex = 0; bondIndex < 3; bondIndex++) {
		bond = ((ne1::SimResultsBond*)bonds)[bondIndex];
		CPPUNIT_ASSERT(bond.atomId_1 == bondIndex);
		CPPUNIT_ASSERT(bond.atomId_2 == bondIndex + 1);
		CPPUNIT_ASSERT_DOUBLES_EQUAL(bondIndex + 0.5f, bond.order, 0.001);
	}
	status = simResults->getFrameBonds("frame-set-1", 1, bonds, message);
	CPPUNIT_ASSERT(status == 0);
	for (bondIndex = 0; bondIndex < 5; bondIndex++) {
		bond = ((ne1::SimResultsBond*)bonds)[bondIndex];
		CPPUNIT_ASSERT(bond.atomId_1 == 10+bondIndex);
		CPPUNIT_ASSERT(bond.atomId_2 == 10+bondIndex + 1);
		CPPUNIT_ASSERT_DOUBLES_EQUAL(bondIndex + 1.5f, bond.order, 0.001);
	}
}


/* FUNCTION: getSetTotalEnergy */
void HDF5_SimResultsTest::getSetTotalEnergy() {
	int status;
	std::string message;
	
	float totalEnergy;
	status =
		simResults->getFrameTotalEnergy("frame-set-X", 0, totalEnergy, message);
	CPPUNIT_ASSERT(status != 0);
	
	status =
		simResults->setFrameTotalEnergy("frame-set-X", 0, 0.1, message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->setFrameTotalEnergy("frame-set-1", 0, 0.1, message);
	CPPUNIT_ASSERT(status == 0);
	status =
		simResults->setFrameTotalEnergy("frame-set-1", 1, 0.11, message);
	CPPUNIT_ASSERT(status == 0);
	
	status =
		simResults->getFrameTotalEnergy("frame-set-1", 0, totalEnergy, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.1, totalEnergy, 0.001);
	status =
		simResults->getFrameTotalEnergy("frame-set-1", 1, totalEnergy, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.11, totalEnergy, 0.001);
}


/* FUNCTION: getSetIdealTemperature */
void HDF5_SimResultsTest::getSetIdealTemperature() {
	int status;
	std::string message;
	
	float temperature;
	status =
		simResults->getFrameIdealTemperature
			("frame-set-X", 0, temperature, message);
	CPPUNIT_ASSERT(status != 0);
	
	status =
		simResults->setFrameIdealTemperature("frame-set-X", 0, 0.2, message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->setFrameIdealTemperature("frame-set-1", 0, 0.2, message);
	CPPUNIT_ASSERT(status == 0);
	
	status =
		simResults->getFrameIdealTemperature
			("frame-set-1", 0, temperature, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.2, temperature, 0.001);
}


/* FUNCTION: getSetPressure */
void HDF5_SimResultsTest::getSetPressure() {
	int status;
	std::string message;
	
	float pressure;
	status =
		simResults->getFramePressure("frame-set-X", 0, pressure, message);
	CPPUNIT_ASSERT(status != 0);
	
	status =
		simResults->setFramePressure("frame-set-X", 0, 0.3, message);
	CPPUNIT_ASSERT(status != 0);
	status =
		simResults->setFramePressure("frame-set-1", 0, 0.3, message);
	CPPUNIT_ASSERT(status == 0);
	
	status =
		simResults->getFramePressure("frame-set-1", 0, pressure, message);
	CPPUNIT_ASSERT(status == 0);
	CPPUNIT_ASSERT_DOUBLES_EQUAL(0.3, pressure, 0.001);
}
