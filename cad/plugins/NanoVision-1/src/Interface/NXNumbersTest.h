// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_NUMBERSTEST_H
#define NX_NUMBERSTEST_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Interface/NXNumbers.h"

using namespace Nanorex;


/* CLASS: NXNumbersTest */
class NXNumbersTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(NXNumbersTest);
	CPPUNIT_TEST(toCharTest);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void toCharTest();
};

#endif
