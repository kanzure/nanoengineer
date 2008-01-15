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


/* FUNCTION: consoleHandlerTest */
void NXLoggerTest::consoleHandlerTest() {
	printf("\n");
	NXLogger* logger = new NXLogger();
	logger->addHandler(new NXConsoleLogHandler(NXLogLevel_Info));
	logger->log(NXLogLevel_Info, "src", "msg");
	NXLOG_DEBUG("foo", "bar");
	NXLOG_CONFIG("cpu", "fast");
	NXLOG_INFO("app", "started");
	NXLOG_WARNING("app", "in trouble");
	NXLOG_SEVERE("app", "exiting");
	delete logger;
	CPPUNIT_ASSERT(true);
}


/* FUNCTION: fileHandlerTest */
void NXLoggerTest::fileHandlerTest() {
	printf("\n");
	NXLogger* logger = new NXLogger();
	logger->addHandler(new NXFileLogHandler("NXLoggerTest.log",
					   NXLogLevel_Info));
	logger->log(NXLogLevel_Info, "src", "msg");
	delete logger;
	CPPUNIT_ASSERT(true);
}
