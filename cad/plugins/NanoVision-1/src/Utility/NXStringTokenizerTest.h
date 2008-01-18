// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_STRINGTOKENIZERTEST_H
#define NX_STRINGTOKENIZERTEST_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <vector>
#include <string>

#include <cppunit/extensions/HelperMacros.h>

#include <Nanorex/Utility/NXStringTokenizer.h>


/* CLASS: NXStringTokenizerTest */
class NXStringTokenizerTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(NXStringTokenizerTest);
	CPPUNIT_TEST(tokenization);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void tokenization();

	private:
};

#endif
