// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_LOGGERTEST_H
#define NX_LOGGERTEST_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Utility/NXLogger.h"

using namespace Nanorex;


/* CLASS: NXLoggerTest */
class NXLoggerTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(NXLoggerTest);
	CPPUNIT_TEST(consoleHandlerTest);
	CPPUNIT_TEST(fileHandlerTest);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void consoleHandlerTest();
		void fileHandlerTest();
};

#endif
