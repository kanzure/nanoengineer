
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#ifndef NE1_HDF5_SIMRESULTSTEST_H
#define NE1_HDF5_SIMRESULTSTEST_H

#include <string>

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/HDF5_SimResults.h"
using namespace Nanorex;


/* CLASS: HDF5_SimResultsTest */
class HDF5_SimResultsTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(HDF5_SimResultsTest);
	
	CPPUNIT_TEST(openDataStore);
	CPPUNIT_TEST(getSetName);
	CPPUNIT_TEST(getSetDescription);
	CPPUNIT_TEST(getSetNotes);

	CPPUNIT_TEST(getSetParameters);
	CPPUNIT_TEST(getSetFilePath);
	
	CPPUNIT_TEST(getSetRunResult);
	CPPUNIT_TEST(getSetStartTime);
	CPPUNIT_TEST(getSetCPU_RunningTime);
	CPPUNIT_TEST(getSetWallRunningTime);
	CPPUNIT_TEST(getSetResults);
	
	CPPUNIT_TEST(getAddRemoveFrameSet);
	CPPUNIT_TEST(getSetAggregationMode);
	CPPUNIT_TEST(getSetStepsPerFrame);
	
	CPPUNIT_TEST(getAddRemoveFrame);
	CPPUNIT_TEST(getSetAtomIds);
	CPPUNIT_TEST(getSetAtomicNumbers);
	CPPUNIT_TEST(getSetAtomPositions);
	CPPUNIT_TEST(getSetAtomVelocities);
	CPPUNIT_TEST(getSetBonds);
	CPPUNIT_TEST(getSetTotalEnergy);
	CPPUNIT_TEST(getSetIdealTemperature);
	CPPUNIT_TEST(getSetPressure);
	
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void openDataStore();
		void getSetName();
		void getSetDescription();
		void getSetNotes();
		
		void getSetParameters();
		void getSetFilePath();
		
		void getSetRunResult();
		void getSetStartTime();
		void getSetCPU_RunningTime();
		void getSetWallRunningTime();
		void getSetResults();
		
		void getAddRemoveFrameSet();
		void getSetAggregationMode();
		void getSetStepsPerFrame();
		
		void getAddRemoveFrame();
		void getSetAtomIds();
		void getSetAtomicNumbers();
		void getSetAtomPositions();
		void getSetAtomVelocities();
		void getSetBonds();
		void getSetTotalEnergy();
		void getSetIdealTemperature();
		void getSetPressure();
		
	private:
		HDF5_SimResults* simResults;
};

#endif
