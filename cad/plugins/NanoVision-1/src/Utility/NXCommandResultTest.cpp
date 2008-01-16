// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXCommandResultTest.h"

CPPUNIT_TEST_SUITE_REGISTRATION(NXCommandResultTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXCommandResultTest, "NXCommandResultTestSuite");


/* FUNCTION: setUp */
void NXCommandResultTest::setUp() {
}


/* FUNCTION: tearDown */
void NXCommandResultTest::tearDown() {
}


/* FUNCTION: basicTest */
void NXCommandResultTest::basicTest() {
	NXCommandResult* commandResult = new NXCommandResult();
	QString translation = GetNV1ResultCodeString(commandResult);
	CPPUNIT_ASSERT(translation == "Internal error: NXCommandResult not populated.");
}
