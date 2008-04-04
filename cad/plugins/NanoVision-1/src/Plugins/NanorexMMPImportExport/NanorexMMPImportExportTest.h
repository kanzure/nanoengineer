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
// 	CPPUNIT_TEST(atomHTest);
// 	CPPUNIT_TEST(HTest);
// 	CPPUNIT_TEST(H2OTest);
// 	CPPUNIT_TEST(H2O2Test);
// 	CPPUNIT_TEST(chlorophyllTest);
// 	CPPUNIT_TEST(vanillinTest);
// 	CPPUNIT_TEST(nanocarTest);
	CPPUNIT_TEST(benzeneTest);
	CPPUNIT_TEST_SUITE_END();
	
public:
	void setUp(void);
	void tearDown(void);
		
private:
	void atomHTest(void);
	void HTest(void);
	void H2OTest(void);
	void H2O2Test(void);
	void chlorophyllTest(void);
	void vanillinTest(void);
	void benzeneTest(void);
	void nanocarTest(void);
};

#endif // NANOREXMMPIMPORTEXPORTTEST_H
