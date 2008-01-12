// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXLoggerTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(NXLoggerTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXLoggerTest, "NXLoggerTestSuite");


/* FUNCTION: setUp */
void NXLoggerTest::setUp() {
}


/* FUNCTION: tearDown */
void NXLoggerTest::tearDown() {
}


/* FUNCTION: toCharTest */
void NXLoggerTest::basicTest() {
	NXLogger* logger = new NXLogger();
	logger->addHandler(new NXConsoleLogHandler(LogLevel_Info));
	logger->log(LogLevel_Info, "src", "msg");
	
	CPPUNIT_ASSERT(true);
}
