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
	NanorexMMPImportExport importer;
	NXDataStoreInfo dataStoreInfo;
	NXMoleculeSet molSet;
	
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


void NanorexMMPImportExportTest::HTest(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo, "H.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *HMol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(HMol->NumAtoms() == 1);
	CPPUNIT_ASSERT(HMol->NumBonds() == 0);
}


void NanorexMMPImportExportTest::H2OTest(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo, "H2O.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *H2OMol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(H2OMol->NumAtoms() == 3);
	CPPUNIT_ASSERT(H2OMol->NumBonds() == 2);
}


void NanorexMMPImportExportTest::H2O2Test(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo,
	                        "hydrogen_peroxide.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *H2O2Mol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(H2O2Mol->NumAtoms() == 4);
	CPPUNIT_ASSERT(H2O2Mol->NumBonds() == 3);
}


void NanorexMMPImportExportTest::chlorophyllTest(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo, "chlorophyll.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *chlorophyllMol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(chlorophyllMol->NumAtoms() == 133);
	CPPUNIT_ASSERT(chlorophyllMol->NumBonds() == 141);
}


void NanorexMMPImportExportTest::vanillinTest(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo, "vanillin.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 1);
	OBMol *vanillinMol = *molSet.moleculesBegin();
	CPPUNIT_ASSERT(vanillinMol->NumAtoms() == 19);
	CPPUNIT_ASSERT(vanillinMol->NumBonds() == 19);
}


void NanorexMMPImportExportTest::nanocarTest(void)
{
	NanorexMMPImportExport importer;
	NXMoleculeSet molSet;
	NXDataStoreInfo dataStoreInfo;
	
	importer.importFromFile(&molSet, &dataStoreInfo, "nanocar.mmp", 0, 0);
	
	CPPUNIT_ASSERT(molSet.childCount() == 0);
	CPPUNIT_ASSERT(molSet.moleculeCount() == 5);
	OBMolIterator nanocarMolIter = molSet.moleculesBegin();
	OBMol *chassisMol = *nanocarMolIter;
	CPPUNIT_ASSERT(chassisMol->NumAtoms() == 100);
	CPPUNIT_ASSERT(chassisMol->NumBonds() == 107);
	++nanocarMolIter;
	OBMol *wheel1Mol= *nanocarMolIter;
	CPPUNIT_ASSERT(wheel1Mol->NumAtoms() == 61);
	CPPUNIT_ASSERT(wheel1Mol->NumBonds() == 92);
	++nanocarMolIter;
	OBMol *wheel2Mol= *nanocarMolIter;
	CPPUNIT_ASSERT(wheel2Mol->NumAtoms() == 61);
	CPPUNIT_ASSERT(wheel2Mol->NumBonds() == 92);
	++nanocarMolIter;
	OBMol *wheel3Mol= *nanocarMolIter;
	CPPUNIT_ASSERT(wheel3Mol->NumAtoms() == 61);
	CPPUNIT_ASSERT(wheel3Mol->NumBonds() == 92);
	++nanocarMolIter;
	OBMol *wheel4Mol= *nanocarMolIter;
	CPPUNIT_ASSERT(wheel4Mol->NumAtoms() == 61);
	CPPUNIT_ASSERT(wheel4Mol->NumBonds() == 92);
	
	CPPUNIT_ASSERT(dataStoreInfo.hasClipboardStructure());
	NXMoleculeSet *clipboardGroup = dataStoreInfo.getClipboardStructure();
	CPPUNIT_ASSERT(clipboardGroup->moleculeCount() == 4);
	CPPUNIT_ASSERT(clipboardGroup->childCount() == 0);
}
