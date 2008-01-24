// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef HDF5_SIMRESULTSIMPORTEXPORT_H
#define HDF5_SIMRESULTSIMPORTEXPORT_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/HDF5_SimResults.h"
#include "Nanorex/Interface/NXEntityManager.h"

using namespace Nanorex;


/* CLASS: HDF5_SimResultsImportExportTest */
class HDF5_SimResultsImportExportTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(HDF5_SimResultsImportExportTest);
	CPPUNIT_TEST(basicExportTest);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void basicExportTest();

	private:
		NXEntityManager* entityManager;
		NXLogger* logger;
};

#endif
