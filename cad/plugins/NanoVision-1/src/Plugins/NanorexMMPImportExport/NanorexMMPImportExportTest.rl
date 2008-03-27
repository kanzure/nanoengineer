// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExportTest.h"
#include <sstream>

using namespace std;

CPPUNIT_TEST_SUITE_REGISTRATION(NanorexMMPImportExportTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NanorexMMPImportExportTest,
                                      "NanorexMMPImportExportTestSuite");


// -- member functions --

void NanorexMMPImportExportTest::setUp(void)
{
}


void NanorexMMPImportExportTest::tearDown(void)
{
}


void
NanorexMMPImportExportTest::atomLineTestSetUp(vector<string>& testStrings,
                                              vector<AtomTestInfo>& answers)
{
	testStrings.clear();
	answers.clear();
	
	testStrings.push_back("atom 12  (10) (1,2,3) def\n ");
	answers.push_back(AtomTestInfo(12, 10, 1, 2, 3, "def"));

	testStrings.push_back("atom    6   (99 ) ( 15632,-2,     -63  ) bas  \n ");
	answers.push_back(AtomTestInfo(6, 99, 15632, -2, -63, "bas"));
}


void NanorexMMPImportExportTest::atomLineTest(void)
{
	vector<string> testStrings;
	vector<AtomTestInfo> answers;
	atomLineTestSetUp(testStrings, answers);
	
	for(int i = 0; i < (int) testStrings.size(); ++i) {
		atomLineTestHelper(testStrings[i].c_str());
		
		CPPUNIT_ASSERT(atomIds.back() == answers[i].id);
		CPPUNIT_ASSERT(atomicNums.back() = answers[i].atomicNum);
		CPPUNIT_ASSERT(atomLocs.back().x == answers[i].pos.x);
		CPPUNIT_ASSERT(atomLocs.back().y == answers[i].pos.y);
		CPPUNIT_ASSERT(atomLocs.back().z == answers[i].pos.z);
		// cerr << "style comparison: " << currentAtomStyle << " =?= " << answers[i].style << endl; 
		CPPUNIT_ASSERT(atomStyles.back() == answers[i].style);
	}
	
	atomLineTestTearDown();
}


void NanorexMMPImportExportTest::atomLineTestTearDown(void)
{
	atomIds.clear();
	atomicNums.clear();
	atomLocs.clear();
	atomStyles.clear();
	atomProps.clear();
	bonds.clear();
}


%%{
# ***** Ragel: atom declaration line test machine *****
	machine atom_decl_line_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := atom_decl_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		};
	
}%%


void NanorexMMPImportExportTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	%% machine atom_decl_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportTest::newAtom(int atomId, int atomicNum,
                                         int x, int y, int z,
                                         std::string const& atomStyle)
{
	// cerr << "newAtom: atom (" << atomId << ") (" << x << ',' << y << ',' << z
	// 	<< ") " << atomStyle << endl;
	atomIds.push_back(atomId);
	atomicNums.push_back(atomicNum);
	atomLocs.push_back(Position(x,y,z));
	atomStyles.push_back(atomStyle);
	
	// properties
	atomProps.push_back(map<string,string>());
	bonds.push_back(map<string, vector<int> >());
}



void NanorexMMPImportExportTest::bondLineTest(void)
{
	char *testInput = NULL;
	
	bonds.clear();
	bonds.push_back(map<string, vector<int> >());
	
	testInput = "bonda 1\n";
	bondLineTestHelper(testInput);
	CPPUNIT_ASSERT(bonds.back()["a"][0] == 1);

	testInput = "bondc 32    65535  \n ";
	bondLineTestHelper(testInput);
	CPPUNIT_ASSERT(bonds.back()["c"][0] == 32);
	CPPUNIT_ASSERT(bonds.back()["c"][1] == 65535);
	
	bonds.clear();
}


%%{
# ***** Ragel: bond declaration line test machine *****
	machine bond_line_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := bond_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		};
	
}%%


void NanorexMMPImportExportTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;

	%% machine bond_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportTest::newBond(std::string const& bondType,
                                         int targetAtomId)
{
	// cerr << "newBond: bond" << bondType << " " << targetAtomId << endl;
	// currentBondType = bondType;
	// targetAtomIds.push_back(targetAtomId);
	bonds.back()[bondType].push_back(targetAtomId);
}


void NanorexMMPImportExportTest::bondDirectionTest(void)
{
	char const *testInput = NULL;
	
	testInput = "bond_direction 10 12\n";
	bondDirectionTestHelper(testInput);
	CPPUNIT_ASSERT(bondDirectionStartId == 10);
	CPPUNIT_ASSERT(bondDirectionStopId  == 12);
	
	testInput = "bond_direction    1000                 812  \n";
	bondDirectionTestHelper(testInput);
	CPPUNIT_ASSERT(bondDirectionStartId == 1000);
	CPPUNIT_ASSERT(bondDirectionStopId  == 812);
}


%%{
# ***** Ragel: bond_direction line test machine *****
	machine bond_direction_line_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := bond_direction_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		};
	
}%%


void
NanorexMMPImportExportTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	%% machine bond_direction_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportTest::newBondDirection(int atomId1, int atomId2)
{
	// cerr << "newBondDirection: bond_direction " << atomId1 << " " << atomId2 << endl;
	bondDirectionStartId = atomId1;
	bondDirectionStopId = atomId2;
}


void NanorexMMPImportExportTest::infoAtomTest(void)
{
	char const *testInput = NULL;
	atomProps.push_back(map<string,string>());
	
	testInput = "info atom hybridization = sp3\n";
	infoAtomTestHelper(testInput);
	CPPUNIT_ASSERT(atomProps.back()["hybridization"] == "sp3");
	
	// spaces
	testInput = "info      atom     company      = Nanorex   \n";
	infoAtomTestHelper(testInput);
	CPPUNIT_ASSERT(atomProps.back()["company"] == "Nanorex");
	
	// spaces in keys and values
	testInput = "info atom key with spaces     =  value with spaces\n";
	infoAtomTestHelper(testInput);
	// cerr << "infoAtomTest: COMPARING '" << infoAtomKeys.back() << "' and '"
	// 	<< infoAtomValues.back() << "'" << endl;
	CPPUNIT_ASSERT(atomProps.back()["key with spaces"] == "value with spaces");
	
	testInput =	"   info  atom "
		"spaces at the beginning   =    and spaces at    the end     \n";
	infoAtomTestHelper(testInput);
	CPPUNIT_ASSERT(atomProps.back()["spaces at the beginning"] ==
	               "and spaces at    the end");
	
	atomProps.clear();
}


%%{
# ***** Ragel: info_atom_line test machine *****
	machine info_atom_line_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := info_atom_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		};
	
}%%


void NanorexMMPImportExportTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	%% machine info_atom_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportTest::atomStmtTest(void)
{
	atomIds.clear();
	atomicNums.clear();
	atomLocs.clear();
	atomProps.clear();
	atomStyles.clear();
	bonds.clear();
	
	char const *testInput = NULL;
	
	// cerr << "Performing atom_stmt test" << endl;
	
	testInput =
		"atom 15 (6)  (50, -50, 600) style with spaces  \n"
		"info atom atomtype   =  sp3\n"
		"bonda 2 \n"
		"bond1 4 6 7\n";
	atomStmtTestHelper(testInput);
	
	CPPUNIT_ASSERT(atomIds.back() == 15);
	CPPUNIT_ASSERT(atomicNums.back() == 6);
	CPPUNIT_ASSERT(atomLocs.back().x == 50);
	CPPUNIT_ASSERT(atomLocs.back().y == -50);
	CPPUNIT_ASSERT(atomLocs.back().z == 600);
	CPPUNIT_ASSERT(atomStyles.back() == "style with spaces");
	CPPUNIT_ASSERT(atomProps.back()["atomtype"] == "sp3");
	CPPUNIT_ASSERT(bonds.back()["a"][0] == 2);
	CPPUNIT_ASSERT(bonds.back()["1"][0] == 4);
	CPPUNIT_ASSERT(bonds.back()["1"][1] == 6);
	CPPUNIT_ASSERT(bonds.back()["1"][2] == 7);
	
	// cleanup as with atom-line test
	atomLineTestTearDown();
}


%%{
# ***** Ragel: atom_stmt test machine *****
	machine atom_stmt_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := atom_stmt
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		};
	
}%%


void NanorexMMPImportExportTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	%% machine atom_stmt_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportTest::newAtomInfo(std::string const& key,
                                             std::string const& value)
{
	// string key1 = key;
	// stripTrailingWhiteSpaces(key1);
	// string value1 = value;
	// stripTrailingWhiteSpaces(value1);
	// cerr << "newAtomInfo: " << key << " = " << value << endl;
	// infoAtomKeys.push_back(key);
	// infoAtomValues.push_back(value);
	atomProps.back().insert(make_pair(key, value));
}

