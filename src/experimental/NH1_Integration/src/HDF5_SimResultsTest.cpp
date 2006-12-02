
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
	ne1::HDF5_SimResults* simResults = new ne1::HDF5_SimResults();
	
	std::string message;
	int status = simResults->openDataStore("dir", message);
	CPPUNIT_ASSERT(status == 0);
}
