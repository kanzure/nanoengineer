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
bool NXNumbersTest::toCharTest() {
	char buffer[5];
	NXNumbers::ToChar(12.123456789, buffer, 4 /* precision */);
	CPPUNIT_ASSERT(strcmp(buffer, "12.1234") == 0);
}
