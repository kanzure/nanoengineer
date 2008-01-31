// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef OPENBABELIMPORTEXPORTTEST_H
#define OPENBABELIMPORTEXPORTTEST_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Interface/NXEntityManager.h"

using namespace Nanorex;


/* CLASS: OpenBabelImportExportTest */
class OpenBabelImportExportTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(OpenBabelImportExportTest);
	CPPUNIT_TEST(basicExportTest);
	CPPUNIT_TEST(basicImportTest);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void basicExportTest();
		void basicImportTest();

	private:
		NXEntityManager* entityManager;
		NXLogger* logger;
};

#endif
