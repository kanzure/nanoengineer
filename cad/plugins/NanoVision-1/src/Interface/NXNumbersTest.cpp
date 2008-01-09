// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXNumbersTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(NXNumbersTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXNumbersTest, "NXNumbersTestSuite");


/* FUNCTION: setUp */
void NXNumbersTest::setUp() {
}


/* FUNCTION: tearDown */
void NXNumbersTest::tearDown() {
}


/* FUNCTION: toCharTest */
void NXNumbersTest::toCharTest() {
	char buffer1[8];
	NXRealUtils::ToChar(12.123456789, buffer1, 6 /* precision */);
	CPPUNIT_ASSERT(strcmp(buffer1, "12.1235") == 0);
}
