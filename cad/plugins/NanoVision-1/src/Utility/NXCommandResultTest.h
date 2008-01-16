// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_COMMANDRESULTTEST_H
#define NX_COMMANDRESULTTEST_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"

using namespace Nanorex;


/* CLASS: NXCommandResultTest */
class NXCommandResultTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(NXCommandResultTest);
	CPPUNIT_TEST(basicTest);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void basicTest();
};

#endif
