// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NANOREXMMPIMPORTEXPORTTEST_H
#define NANOREXMMPIMPORTEXPORTTEST_H

#include <cppunit/extensions/HelperMacros.h>
#include <vector>
#include <stack>
#include <string>
#include "iterator.h"

#include "NanorexMMPImportExport.h"
#include <Nanorex/Interface/NXMoleculeSet.h>

/* CLASS: NanorexMMPImportExportTest */
class NanorexMMPImportExportTest: public CPPUNIT_NS::TestFixture {
	
	CPPUNIT_TEST_SUITE(NanorexMMPImportExportTest);
	CPPUNIT_TEST(atomHTest);
	CPPUNIT_TEST_SUITE_END();
	
public:
	void setUp(void);
	void tearDown(void);
		
private:
	NanorexMMPImportExport importer;
	NXMoleculeSet *molSetPtr;
	
	void atomHTest(void);
};

#endif // NANOREXMMPIMPORTEXPORTTEST_H
