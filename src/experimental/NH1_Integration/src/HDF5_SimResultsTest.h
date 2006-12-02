
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#ifndef NE1_HDF5_SIMRESULTSTEST_H
#define NE1_HDF5_SIMRESULTSTEST_H

#include <string>

#include <cppunit/extensions/HelperMacros.h>

#include "HDF5_SimResults.h"


/* CLASS: HDF5_SimResultsTest */
class HDF5_SimResultsTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(HDF5_SimResultsTest);
	CPPUNIT_TEST(openDataStore);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void openDataStore();

	private:
};

#endif
