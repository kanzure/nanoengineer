// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExportTest.h"
#include "Nanorex/Utility/NXUtility.h"
#include <sstream>
#include <cfloat>

using namespace Nanorex;
using namespace std;

CPPUNIT_TEST_SUITE_REGISTRATION(NanorexMMPImportExportTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NanorexMMPImportExportTest,
                                      "NanorexMMPImportExportTestSuite");

#if defined(VERBOSE)
#define CERR(s) \
{ cerr << (NXUtility::itos(lineNum) + ": ") << s << endl; }
#else
#define CERR(S)
#endif

// -- member functions --

void NanorexMMPImportExportTest::setUp(void)
{
}


void NanorexMMPImportExportTest::tearDown(void)
{
}


void NanorexMMPImportExportTest::atomHTest(void)
{
	string const testInput =
		"mmpformat 050502 required; 050706 preferred\n"
		"kelvin 300\n"
		"group (View Data)\n"
		"info opengroup open = True\n"
		"csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000)"
		"(0.000000, 0.000000, 0.000000) (1.000000)\n"
		"csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (3.880744)"
		"(0.082000, 0.076500, 0.072500) (1.000000)\n"
		"egroup (View Data)\n"
		"group (Hydrogen atom)\n"
		"mol (Hydrogen) def\n"
		"atom 1 (1) (0, 0, 0) bas\n"
		"egroup\n"
		"end1\n"
		"group (Clipboard)\n"
		"info opengroup open = False\n"
		"egroup (Clipboard)\n"
		"end\n"
		;
	istringstream testInputStream(testInput);
	NXDataStoreInfo dataStoreInfo;
	NXMoleculeSet molSet;
	importer.dataStoreInfo = &dataStoreInfo;
	importer.readMMP(testInputStream, &molSet);
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *Hmol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(Hmol->NumAtoms() == 1);
	CPPUNIT_ASSERT(Hmol->NumBonds() == 0);
	CPPUNIT_ASSERT(dataStoreInfo.hasClipboardStructure());
	NXMoleculeSet *clipboardGroup = dataStoreInfo.getClipboardStructure();
	CPPUNIT_ASSERT(clipboardGroup->childCount() == 0);
	CPPUNIT_ASSERT(clipboardGroup->moleculeCount() == 0);
}
