// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExportRagelTest.h"
#include "Nanorex/Utility/NXUtility.h"
#include <sstream>
#include <cfloat>

using namespace Nanorex;
using namespace std;

CPPUNIT_TEST_SUITE_REGISTRATION(NanorexMMPImportExportRagelTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NanorexMMPImportExportRagelTest,
                                      "NanorexMMPImportExportRagelTestSuite");

#define VERBOSE

#if defined(VERBOSE)
#define CERR(s) \
{ cerr << (NXUtility::itos(lineNum) + ": ") << s << endl; }
#else
#define CERR(S)
#endif

// -- member functions --

void NanorexMMPImportExportRagelTest::setUp(void)
{
}


void NanorexMMPImportExportRagelTest::tearDown(void)
{
}


void NanorexMMPImportExportRagelTest::reset(void)
{
	atomIds.clear();
	atomicNums.clear();
	atomLocs.clear();
	atomStyles.clear();
	atomProps.clear();
	bonds.clear();
	lineNum = 1;
	
	atomCount = 0;
	molCount = 0;
	groupCount = 0;
	egroupCount = 0;
	
	infoAtomCount = 0;
	infoChunkCount = 0;
	infoOpenGroupCount = 0;
	
	bond1Count = 0;
	bond2Count = 0;
	bond3Count = 0;
	bondaCount = 0;
	bondcCount = 0;
	bondgCount = 0;
}


void NanorexMMPImportExportRagelTest::syntaxError(string const& errorMessage)
{
	cerr << lineNum << ": Syntax Error : " << errorMessage << endl;
}


void
NanorexMMPImportExportRagelTest::atomLineTestSetUp(vector<string>& testStrings,
	vector<AtomTestInfo>& answers)
{
	testStrings.clear();
	answers.clear();
	
	testStrings.push_back("atom 12  (10) (1,2,3) def\n");
	answers.push_back(AtomTestInfo(12, 10, 1, 2, 3, "def"));
	
	testStrings.push_back("atom    6   (99 ) ( 15632,-2,     -63  ) bas  \n");
	answers.push_back(AtomTestInfo(6, 99, 15632, -2, -63, "bas"));
	
	testStrings.push_back("atom 12  (10) (1,2,3) def  "
	                      "# this one's got a comment \n");
	answers.push_back(AtomTestInfo(12, 10, 1, 2, 3, "def"));
	
	testStrings.push_back("atom    6   (99 ) ( 15632,-2,     -63  ) bas"
	                      "# comment where the '#' touches the style\n");
	answers.push_back(AtomTestInfo(6, 99, 15632, -2, -63, "bas"));
}


void NanorexMMPImportExportRagelTest::atomLineTest(void)
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
	CPPUNIT_ASSERT(atomIds.size() == testStrings.size());
	CPPUNIT_ASSERT(atomicNums.size() == testStrings.size());
	CPPUNIT_ASSERT(atomLocs.size() == testStrings.size());
	CPPUNIT_ASSERT(atomStyles.size() == testStrings.size());
}


%%{
# ***** Ragel: atom declaration line test machine *****
	machine atom_decl_line_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := space** atom_decl_line
// @ { newAtom(atomId, atomicNum, x, y, z, atomStyle); }
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		};
	
}%%


void NanorexMMPImportExportRagelTest::atomLineTestHelper(char const *const testInput)
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


void NanorexMMPImportExportRagelTest::newAtom(int atomId, int atomicNum,
                                              int x, int y, int z,
                                              std::string const& atomStyle)
{
	++atomCount;
	CERR("atom " + NXUtility::itos(atomId) + " (" + NXUtility::itos(atomicNum)
	     + ") (" + NXUtility::itos(x) + ',' + NXUtility::itos(y) + ',' +
	     NXUtility::itos(z) + ") " + atomStyle);
	atomIds.push_back(atomId);
	atomicNums.push_back(atomicNum);
	atomLocs.push_back(Position(x,y,z));
	atomStyles.push_back(atomStyle);
	
// properties
	atomProps.push_back(map<string,string>());
	bonds.push_back(map<string, vector<int> >());
}



void NanorexMMPImportExportRagelTest::bondLineTest(void)
{
	char *testInput = NULL;
	
	reset();
	bonds.push_back(map<string, vector<int> >());
	
	testInput = "bonda 1\n";
	bondLineTestHelper(testInput);
	CPPUNIT_ASSERT(bonds.back()["a"][0] == 1);
	
	testInput = "bondc 32    65535  \n";
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
	
main := space** bond_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		};
	
}%%


void NanorexMMPImportExportRagelTest::bondLineTestHelper(char const *const testInput)
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


void NanorexMMPImportExportRagelTest::newBond(std::string const& bondType,
                                              int targetAtomId)
{
	if(bondType == "1")
		++bond1Count;
	else if(bondType == "2")
		++bond2Count;
	else if(bondType == "3")
		++bond3Count;
	else if(bondType == "a")
		++bondaCount;
	else if(bondType == "c")
		++bondcCount;
	else if(bondType == "g")
		++bondgCount;
	
	CERR("bond" + bondType + " " + NXUtility::itos(targetAtomId));
// currentBondType = bondType;
// targetAtomIds.push_back(targetAtomId);
	bonds.back()[bondType].push_back(targetAtomId);
}


void NanorexMMPImportExportRagelTest::bondDirectionTest(void)
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
	
main := space** bond_direction_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		};
	
}%%


void
NanorexMMPImportExportRagelTest::bondDirectionTestHelper(char const *const testInput)
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


void NanorexMMPImportExportRagelTest::newBondDirection(int atomId1, int atomId2)
{
	CERR("bond_direction " + NXUtility::itos(atomId1) + " " +
	     NXUtility::itos(atomId2));
	bondDirectionStartId = atomId1;
	bondDirectionStopId = atomId2;
}


void NanorexMMPImportExportRagelTest::infoAtomTest(void)
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
	
main := space**
		info_atom_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		};
	
}%%


void NanorexMMPImportExportRagelTest::infoAtomTestHelper(char const *const testInput)
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


void NanorexMMPImportExportRagelTest::newAtomInfo(std::string const& key,
	std::string const& value)
{
	++infoAtomCount;
// string key1 = key;
// stripTrailingWhiteSpaces(key1);
// string value1 = value;
// stripTrailingWhiteSpaces(value1);
	CERR("info atom '" + key + "' = '" + value + "'");
// infoAtomKeys.push_back(key);
// infoAtomValues.push_back(value);
	atomProps.back().insert(make_pair(key, value));
}


void NanorexMMPImportExportRagelTest::atomStmtTest(void)
{
	reset();
	
	char const *testInput = NULL;
	
// cerr << "Performing atom_stmt test" << endl;
	
	testInput =
		"atom 15 (6)  (50, -50, 600) style with spaces  \n"
		"\n"
		"\n"
		"info atom atomtype   =  sp3\n"
		"bonda 2 \n"
		"\n"
		"bond1 4 6 7\n";
	atomStmtTestHelper(testInput);
	
	CPPUNIT_ASSERT(atomIds.size() == 1);
	CPPUNIT_ASSERT(atomIds.back() == 15);
	CPPUNIT_ASSERT(atomicNums.back() == 6);
	CPPUNIT_ASSERT(atomLocs.back() == Position(50, -50, 600));
	CPPUNIT_ASSERT(atomStyles.back() == "style with spaces");
	CPPUNIT_ASSERT(atomProps.back()["atomtype"] == "sp3");
	CPPUNIT_ASSERT(bonds.back()["a"][0] == 2);
	CPPUNIT_ASSERT(bonds.back()["1"][0] == 4);
	CPPUNIT_ASSERT(bonds.back()["1"][1] == 6);
	CPPUNIT_ASSERT(bonds.back()["1"][2] == 7);
}


%%{
# ***** Ragel: atom_stmt test machine *****
	machine atom_stmt_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
main := WHITESPACE* atom_decl_line
// %{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
		(WHITESPACE*  (atom_decl_line | atom_attrib_line))*
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		};
	
}%%


void NanorexMMPImportExportRagelTest::atomStmtTestHelper(char const *const testInput)
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


void NanorexMMPImportExportRagelTest::multipleAtomStmtTest(void)
{
	reset();
	
	char const *testInput = NULL;
	
// cerr << "Performing atom_stmt test" << endl;
// #if 0
	testInput = "";
	multipleAtomStmtTestHelper(testInput);
	CPPUNIT_ASSERT(atomIds.size() == 0);
	CPPUNIT_ASSERT(atomicNums.size() == 0);
	
	testInput = "\n";
	multipleAtomStmtTestHelper(testInput);
	CPPUNIT_ASSERT(atomIds.size() == 0);
	CPPUNIT_ASSERT(atomicNums.size() == 0);
	
	testInput =
		"\n"
		"   \t  \n";
	multipleAtomStmtTestHelper(testInput);
	CPPUNIT_ASSERT(atomIds.size() == 0);
	CPPUNIT_ASSERT(atomicNums.size() == 0);
	
// single line
	lineNum = 1;
	testInput =
		"atom 15 (6)  (50, -50, 600) style with spaces  \n"
		"info atom atomtype   =  sp3\n"
		"bonda 2 \n"
		"\n"
		"bond1 4 6 7\n"
		"\n";
	
	multipleAtomStmtTestHelper(testInput);
	
	CPPUNIT_ASSERT(atomIds.size() == 1);
	CPPUNIT_ASSERT(atomIds.back() == 15);
	CPPUNIT_ASSERT(atomicNums.back() == 6);
	CPPUNIT_ASSERT(atomLocs.back() == Position(50, -50, 600));
	CPPUNIT_ASSERT(atomStyles.back() == "style with spaces");
	CPPUNIT_ASSERT(atomProps.back()["atomtype"] == "sp3");
	CPPUNIT_ASSERT(bonds.back()["a"][0] == 2);
	CPPUNIT_ASSERT(bonds.back()["1"][0] == 4);
	CPPUNIT_ASSERT(bonds.back()["1"][1] == 6);
	CPPUNIT_ASSERT(bonds.back()["1"][2] == 7);
// #endif
	
// two lines
	lineNum = 1;
	testInput =
		"atom 1 (9) (-2, 4, 1000) custom style  \n"
		" \n"
		"\t\n"
		"atom  3  (  87 )  ( -10  ,-2,  32)  ball and stick\n"
		"\n"
		"\t\n"
		"bond1 \t1 2\n"
		"\n"
		"atom 4 (6\t) (0,0,0) def\n"
		"bondg \t1 22 333\n"
		"\n"
		"bondc 33   2 \n"
		"\n"
		;
	
	multipleAtomStmtTestHelper(testInput);
	
// include contribs from previous test - data structures haven't been cleared
	CPPUNIT_ASSERT(atomIds.size() == 4);
	CPPUNIT_ASSERT(atomicNums.size() == 4);
	CPPUNIT_ASSERT(atomLocs.size() == 4);
	CPPUNIT_ASSERT(atomProps.size() == 4);
	CPPUNIT_ASSERT(bonds.size() == 4);
	
	CPPUNIT_ASSERT(atomIds[1] == 1);
	CPPUNIT_ASSERT(atomicNums[1] == 9);
	CPPUNIT_ASSERT(atomLocs[1] == Position(-2, 4, 1000));
	CPPUNIT_ASSERT(atomStyles[1] == "custom style");
	CPPUNIT_ASSERT(bonds[1].size() == 0);
	
	CPPUNIT_ASSERT(atomIds[2] == 3);
	CPPUNIT_ASSERT(atomicNums[2] == 87);
	CPPUNIT_ASSERT(atomLocs[2] == Position(-10, -2, 32));
	CPPUNIT_ASSERT(atomStyles[2] == "ball and stick");
	CPPUNIT_ASSERT(bonds[2].size() == 1);
	
	CPPUNIT_ASSERT(atomIds[3] == 4);
	CPPUNIT_ASSERT(atomicNums[3] == 6);
	CPPUNIT_ASSERT(bonds[3].size() == 2);
	CPPUNIT_ASSERT(bonds[3]["g"].size() == 3);
	CPPUNIT_ASSERT(bonds[3]["g"][0] == 1);
	CPPUNIT_ASSERT(bonds[3]["g"][1] == 22);
	CPPUNIT_ASSERT(bonds[3]["g"][2] == 333);
	CPPUNIT_ASSERT(bonds[3]["c"].size() == 2);
	CPPUNIT_ASSERT(bonds[3]["c"][0] == 33);
	CPPUNIT_ASSERT(bonds[3]["c"][1] == 2);
	
}


%%{
# ***** Ragel: atom_stmt test machine (zero or more lines) *****
	machine multiple_atom_stmt_test;
	include utilities "utilities.rl";
	include atom "atom.rl";
	
atom_stmt := |*
#EOL => { cerr << "EOL, p = " << p << endl; };
		WHITESPACE* atom_decl_line;
	WHITESPACE* bond_line;
	WHITESPACE* bond_direction_line;
	WHITESPACE* info_atom_line;
	WHITESPACE* 0 => {fret;};
	*|;
	
main := (WHITESPACE** atom_decl_line
         @ { //newAtom(atomId, atomicNum, x, y, z, atomStyle);
// cerr << "calling, p = " << p << endl;
	         fcall atom_stmt;})*
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		};
	
}%%


void
NanorexMMPImportExportRagelTest::
multipleAtomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	char const *ts, *te;
	int top, act, stack[1024];
	
	%% machine multiple_atom_stmt_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportRagelTest::molLineTest(void)
{
	char const *testInput = NULL;
	
	testInput = "mol (Nanorex1) style1\n";
	molLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentMolName == "Nanorex1");
	CPPUNIT_ASSERT(currentMolStyle == "style1");
	
// spaces and tabs
	testInput =
		"   mol (  Nanorex2  )   style with   lotsa         spaces"
		"\tand \t\ttabs  \n";
	molLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentMolName == "Nanorex2");
	CPPUNIT_ASSERT(currentMolStyle ==
	               "style with   lotsa         spaces\tand \t\ttabs");
	
// mol names with spaces
	testInput = "mol ( name with spaces and\ttabs\t) style\t3 \n";
	molLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentMolName == "name with spaces and\ttabs");
	CPPUNIT_ASSERT(currentMolStyle == "style\t3");
	
// no mol style which should default to "def"
	testInput = "mol (Untitled)\n";
	molLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentMolName == "Untitled");
	CPPUNIT_ASSERT(currentMolStyle == "def");
	
}


%%{
	machine mol_decl_line_test;
	include utilities "utilities.rl";
	include molecule "molecule.rl";
	
main := mol_decl_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "mol_decl_line_test state machine");
		};
}%%


void NanorexMMPImportExportRagelTest::molLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	%% machine mol_decl_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void
NanorexMMPImportExportRagelTest::newMolecule(string const& name, string const& style)
{
	++molCount;
	currentMolName = name;
	currentMolStyle = style;
	CERR("mol (" + name + ") " + style);
}


void
NanorexMMPImportExportRagelTest::newChunkInfo(string const& key,
                                              string const& value)
{
	++infoChunkCount;
	CERR("info chunk " << key << " = " << value);
/// @todo
}


void NanorexMMPImportExportRagelTest::csysLineTest(void)
{
	char const *testInput = NULL;
	
	testInput = "csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) "
		"(10.000000) (0.000000, 0.000000, 0.000000) (1.000000)\n";
	csysLineTestHelper(testInput);
	cppunit_assert_csys("HomeView", 1.0, 0.0, 0.0, 0.0,
	                    10.0, 0.0, 0.0, 0.0, 1.0);
	
	testInput = "csys (Last View) (\t1.000000, 0.000000  , 0.200000, 0.030000\t)"
		"( 27.182818)(-3.805800, -0.970371, -0.587506) (1.780000) "
		"# with a comment\n";
	csysLineTestHelper(testInput);
	cppunit_assert_csys("Last View", 1.0, 0.0, 0.2, 0.03, 27.182818,
	                    -3.805800, -0.970371, -0.587506, 1.78);
}


%%{
	machine csys_line_test;
	include group "group.rl";
	
main := csys_line
		$lerr { CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "csys_line_test state machine");
		};
}%%


void
NanorexMMPImportExportRagelTest::csysLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	%% machine csys_line_test;
	%% write data;
	%% write init;
	%% write exec;
}


void
NanorexMMPImportExportRagelTest::
cppunit_assert_csys(string const& name,
                    double const& qw, double const& qx, double const& qy, double const& qz,
                    double const& scale,
                    double const& povX, double const& povY, double const& povZ,
                    double const& zoomFactor)
{
	CPPUNIT_ASSERT(csysViewName == name);
	CPPUNIT_ASSERT(csysQw == qw);
	CPPUNIT_ASSERT(csysQx == qx);
	CPPUNIT_ASSERT(csysQy == qy);
	CPPUNIT_ASSERT(csysQz == qz);
	CPPUNIT_ASSERT(csysScale == scale);
	CPPUNIT_ASSERT(csysPovX == povX);
	CPPUNIT_ASSERT(csysPovY == povY);
	CPPUNIT_ASSERT(csysPovZ == povZ);
	CPPUNIT_ASSERT(csysZoomFactor == zoomFactor);
}


void
NanorexMMPImportExportRagelTest::
newNamedView(std::string const& name,
             double const& qw, double const& qx, double const& qy, double const& qz,
             double const& scale,
             double const& povX, double const& povY, double const& povZ,
             double const& zoomFactor)
{
	csysViewName = name;
	csysQw = qw;
	csysQx = qx;
	csysQy = qy;
	csysQz = qz;
	csysScale = scale;
	csysPovX = povX;
	csysPovY = povY;
	csysPovZ = povZ;
	csysZoomFactor = zoomFactor;
	
	CERR("csys (" + name + ") " +
	     '(' + NXUtility::dtos(qw) + ',' + NXUtility::dtos(qx) + ',' +
	     NXUtility::dtos(qz) + ',' + NXUtility::dtos(qz) + ") " +
	     '(' + NXUtility::dtos(scale) + ") " +
	     '(' + NXUtility::dtos(povX) + ',' + NXUtility::dtos(povY) + ',' +
	     NXUtility::dtos(povZ) + ") " +
	     '(' + NXUtility::dtos(zoomFactor) + ')');
}


void NanorexMMPImportExportRagelTest::groupLineTest(void)
{
// clear group-name stack
	while(!groupNameStack.empty())
		groupNameStack.pop_back();
	
	char const *testInput = NULL;
	
// #if 0
	testInput = "group (FirstGroup) FirstGroupStyle\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 1);
	CPPUNIT_ASSERT(groupNameStack.back() == "FirstGroup");
// CPPUNIT_ASSERT(currentGroupStyle == "FirstGroupStyle");
	
	testInput = "group ( Group name with spaces   ) \n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 2);
	CPPUNIT_ASSERT(groupNameStack.back() == "Group name with spaces");
// CPPUNIT_ASSERT(currentGroupStyle == "Group s\ttyle with spaces");
	
	testInput = "group ( Group that has a name but no style)   \n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 3);
// CPPUNIT_ASSERT(groupNameStack.back() == "Group that has a name but no style");
// #endif
	
	testInput = "group   \t  (View \t  Data\t)\n";
// testInput = "group   \t  (\tClipboard\t)\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 4);
	CPPUNIT_ASSERT(groupNameStack.back() == "View Data");
	
	testInput = "egroup (View   Data\t)\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentGroupName == "View Data");
	CPPUNIT_ASSERT(groupNameStack.size() == 3);
	
	testInput = "\tegroup\t\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentGroupName == "Group that has a name but no style");
	CPPUNIT_ASSERT(groupNameStack.size() == 2);
	
	testInput = "   egroup   (  mismatched group------name_)  \n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 1);
	
	testInput = "egroup  ( FirstGroup   \t ) \t\t\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(currentGroupName == "FirstGroup");
	CPPUNIT_ASSERT(groupNameStack.empty());
	
// Set of statements one after another
	lineNum = 0;
	testInput =
		"group (group 1)\n"
		"group (group 1_1) def\n"
		"egroup (group 1_1)\n"
		"group (amines)\n"
		"group (histamines) #def\n"
		"group ( histhistamines\t) \tdef\t\n"
		"egroup\n"
		"group (histhistamines siblings)\n"
		"egroup (histhistamines siblings)\n"
		"egroup (Ok so I have lost track of which group  )  \n"
		"egroup (gotcha now I am ending amines) \n"
		"egroup (This closes the top-level duh)\n"
		"\n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.empty());
}


%%{
# ***** Ragel: group lines test machine *****
	
	machine group_lines_test;
#include utilities "utilities.rl";
	include group "group.rl";
	
mini_group_scanner :=
		|*
		WHITESPACE* egroup_line;
	WHITESPACE* group_view_data_stmt_begin_line @(group,2) => {/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
	WHITESPACE* group_clipboard_stmt_begin_line @(group,2) => {/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
	WHITESPACE* group_mol_struct_stmt_begin_line @(group,1) => {/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
	
#WHITESPACE* group_view_data_stmt_end_line @(group,2) => {/*cerr << "view_data end, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
#WHITESPACE* group_clipboard_stmt_end_line @(group,2) => {/*cerr << "clipboard end, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
#WHITESPACE* group_mol_struct_stmt_end_line @(group,1) => {/*cerr << "mol_struct end, p = '" << p << "' [" << strlen(p) << ']' << endl;*/};
	
	WHITESPACE* IGNORED_LINE => {/*cerr << "Ignored line, p = " << p << endl;*/};
	*|;
	
main := any* >{ /*cerr << "scanner call: p = " << p << endl;*/ fhold; fcall mini_group_scanner; };
	
}%%


void
NanorexMMPImportExportRagelTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	%% machine group_lines_test;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportRagelTest::newViewDataGroup(void)
{
	++groupCount;
	CERR("group (View Data)");
	currentGroupName = "View Data";
	groupNameStack.push_back(currentGroupName);
}


#if 0
void NanorexMMPImportExportRagelTest::endViewDataGroup(void)
{
cerr << lineNum << ": endgroup (View Data)" << endl;
currentGroupName = groupNameStack.back();
groupNameStack.pop_back();
}
#endif


void
NanorexMMPImportExportRagelTest::
newMolStructGroup(std::string const& name,
                  std::string const& classification)
{
	++groupCount;
	CERR("group (" + name + ") " + classification);
	currentGroupName = name;
	groupNameStack.push_back(currentGroupName);
}


#if 0
void NanorexMMPImportExportRagelTest::endMolStructGroup(std::string const& name)
{
// comparing for errors should be done by parser application
// here we are only testing to see if the tokens are being recognized
cerr << lineNum << ": endgroup (" << name << ")  "
<< "[stack-top = " << groupNameStack.back() << ']' << endl;
currentGroupName = groupNameStack.back();
groupNameStack.pop_back();
}
#endif


void NanorexMMPImportExportRagelTest::newClipboardGroup(void)
{
	++groupCount;
	CERR("group (Clipboard)");
	currentGroupName = "Clipboard";
	groupNameStack.push_back(currentGroupName);
}


#if 0
void NanorexMMPImportExportRagelTest::endClipboardGroup(void)
{
cerr << lineNum << ": endgroup (Clipboard)" << endl;
currentGroupName = groupNameStack.back();
groupNameStack.pop_back();
}
#endif


void NanorexMMPImportExportRagelTest::endGroup(string const& name)
{
	++egroupCount;
// comparing for errors should be done by parser application
// here we are only testing to see if the tokens are being recognized
	CERR("egroup (" + name + ")  " + "[stack-top = " + groupNameStack.back()
	       + ']');
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}


void
NanorexMMPImportExportRagelTest::newOpenGroupInfo(string const& key,
	string const& value)
{
	++infoOpenGroupCount;
	CERR("info opengroup " + key + " = " + value);
/// @todo
}


void NanorexMMPImportExportRagelTest::end1(void)
{
	CERR("end1");
}


void NanorexMMPImportExportRagelTest::uncheckedParseTest(void)
{
	char const *testInput = NULL;
	
	reset();
	
	testInput =
		"group (View Data)\n"
		"csys <coordinate-system-info>\n"
		"egroup (View\tData) # comment to make life tough \n"
		"group (nitrogen compounds)\n"
		"mol (ammonia) no molecule style \n"
		"atom 1 (1) (1,1,1) def\n"
		"atom 2 (7) (0,0,0) bas\n"
		"bond1 1\n"
		"atom 3 (1) (1,1,-1) cpk\n"
		"bond1 2\n"
		"atom 4 (1) (-1,1,1) lin\n"
		"bond1 2\n"
		"egroup\n"
		"  end1  \n"
		"group (Clipboard)  \n"
		"<clipboard statements to be ignored>\n"
		"<more statements to be ignored>\n"
		"egroup\n"
		"end  \n"
		" <this line should be ignored>"
		;
	
	uncheckedParseTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 0);
	CPPUNIT_ASSERT(currentMolName == "ammonia");
	CPPUNIT_ASSERT(currentMolStyle == "no molecule style");
}


%%{
	machine unchecked_parse_test;
	include group "group.rl";
	
main := WHITESPACE*
		group_view_data_stmt_begin_line
		@ { /*cerr << "*p=" << *p << endl;*/ fhold; fcall group_scanner; }
	WHITESPACE*
		group_mol_struct_stmt_begin_line
		@ { fhold; fcall group_scanner; }
	WHITESPACE*
		end1_line
		WHITESPACE*
		group_clipboard_stmt_begin_line
		@ { fhold; fcall group_scanner; }
	any*
		;
}%%


void
NanorexMMPImportExportRagelTest::uncheckedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	%% machine unchecked_parse_test;
	%% write data;
	%% write init;
	%% write exec;
}


/// Test the checked pattern matchers to see if local error actions introduced
/// interfere with the regular functioning
void NanorexMMPImportExportRagelTest::checkedParseTest(void)
{
	char const *testInput = NULL;
	
	reset();
	
	testInput =
		"group (View Data)\n"
		"#csys <coordinate-system-info>\n"
		"egroup (View\tData) # comment to make life tough \n"
		"group (nitrogen compounds)\n"
		"mol (ammonia) no molecule style \n"
		"atom 1 (1) (1,1,1) def\n"
		"atom 2 (7) (0,0,0) bas\n"
		"bond1 1\n"
		"atom 3 (1) (1,1,-1) cpk\n"
		"bond1 2\n"
		"atom 4 (1) (-1,1,1) lin\n"
		"bond1 2\n"
		"egroup\n"
		"  end1  \n"
		"group (Clipboard)  \n"
		"<clipboard statements to be ignored>\n"
		"<more statements to be ignored>\n"
		"egroup\n"
		"end  \n"
		" <this line should be ignored>"
		;
	
	checkedParseTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 0);
	CPPUNIT_ASSERT(currentMolName == "ammonia");
	CPPUNIT_ASSERT(currentMolStyle == "no molecule style");
}


%%{
	machine checked_parse_test;
	include checked_group "checked_group.rl";
	
main := WHITESPACE**
		checked_group_view_data_stmt_begin_line
		@ { cerr << "*p=" << *p << endl;
			fhold;
			fcall checked_group_scanner;
		}
	WHITESPACE**
		checked_group_mol_struct_stmt_begin_line
		@ { fhold; fcall checked_group_scanner; }
	WHITESPACE**
		checked_end1_line
		WHITESPACE**
		checked_group_clipboard_stmt_begin_line
		@ { fhold; fcall checked_group_scanner; }
	any*
		;
}%%


void
NanorexMMPImportExportRagelTest::checkedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	%% machine checked_parse_test;
	%% write data;
	%% write init;
	%% write exec;
}


void
NanorexMMPImportExportRagelTest::
checkCounts(int atomCountRef, int molCountRef,
            int groupCountRef, int egroupCountRef,
            int bond1CountRef, int bond2CountRef, int bond3CountRef,
            int bondaCountRef, int bondcCountRef, int bondgCountRef,
            int infoAtomCountRef, int infoChunkCountRef,
            int infoOpenGroupCountRef)
{
	CPPUNIT_ASSERT(atomCount == atomCountRef);
	CPPUNIT_ASSERT(molCount == molCountRef);
	CPPUNIT_ASSERT(groupCount == groupCountRef);
	CPPUNIT_ASSERT(egroupCount == egroupCountRef);
	CPPUNIT_ASSERT(bond1Count == bond1CountRef);
	CPPUNIT_ASSERT(bond2Count == bond2CountRef);
	CPPUNIT_ASSERT(bond3Count == bond3CountRef);
	CPPUNIT_ASSERT(bondaCount == bondaCountRef);
	CPPUNIT_ASSERT(bondcCount == bondcCountRef);
	CPPUNIT_ASSERT(bondgCount == bondgCountRef);
	CPPUNIT_ASSERT(infoAtomCount == infoAtomCountRef);
	CPPUNIT_ASSERT(infoChunkCount == infoChunkCountRef);
	CPPUNIT_ASSERT(infoOpenGroupCount == infoOpenGroupCountRef);
}


void NanorexMMPImportExportRagelTest::charBufParseTest(void)
{
	charBufParseTestVanillin();
}


%%{
	machine parse_tester;
	include group "group.rl";
	
	mmpformat_line =
		'mmpformat'  nonNEWLINEspace+
		digit{6} nonNEWLINEspace+
		'required' nonNEWLINEspace*
		(   ';' nonNEWLINEspace+
		    digit{6} nonNEWLINEspace+
		    'preferred'
		)?
		nonNEWLINEspace*
		EOL;
	
	kelvin_line =
		'kelvin'
		nonNEWLINEspace+
		whole_number % { kelvinTemp = intVal; }
	nonNEWLINEspace*
		EOL;
	
	end_line = 'end' nonNEWLINEspace+;
	
	
main := WHITESPACE*
		mmpformat_line
		WHITESPACE*
		( kelvin_line
		  WHITESPACE*
		)?
		group_view_data_stmt_begin_line
		@ { /*cerr << "*p=" << *p << endl;*/ fhold; fcall group_scanner; }
	WHITESPACE*
		group_mol_struct_stmt_begin_line
		@ { fhold; fcall group_scanner; }
	WHITESPACE*
		end1_line
		WHITESPACE*
		group_clipboard_stmt_begin_line
		@ { fhold; fcall group_scanner; }
	WHITESPACE*
		end_line
		any*
		;
	
}%%


void NanorexMMPImportExportRagelTest::charBufParseTestVanillin(void)
{
	char const *testInput =
		"mmpformat 050502 required; 050706 preferred\n"
		"kelvin 300\n"
		"group (View Data)\n"
		"info opengroup open = True\n"
		"csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)\n"
		"csys (LastView) (0.593283, -0.047584, -0.587604, 0.548154) (5.950136) (2.701500, 2.159000, -0.854500) (1.000000)\n"
		"egroup (View Data)\n"
		"group (vanillin)\n"
		"info opengroup open = True\n"
		"mol (vanillin) def\n"
		"atom 1 (6) (-1533, -113, -98) def\n"
		"info atom atomtype = sp2\n"
		"atom 2 (6) (-2142, -1287, -548) def\n"
		"info atom atomtype = sp2\n"
		"bonda 1\n"
		"atom 3 (6) (-2600, -2232, 373) def\n"
		"info atom atomtype = sp2\n"
		"bonda 2\n"
		"atom 4 (6) (-2448, -2004, 1742) def\n"
		"info atom atomtype = sp2\n"
		"bonda 3\n"
		"atom 5 (6) (-1839, -830, 2191) def\n"
		"info atom atomtype = sp2\n"
		"bonda 4\n"
		"atom 6 (6) (-1382, 116, 1271) def\n"
		"info atom atomtype = sp2\n"
		"bonda 5 1\n"
		"atom 7 (1) (-1176, 625, -817) def\n"
		"bond1 1\n"
		"atom 8 (8) (-2304, -1532, -2019) def\n"
		"bond1 2\n"
		"atom 9 (8) (-3253, -3493, -110) def\n"
		"bond1 3\n"
		"atom 10 (1) (-2806, -2742, 2460) def\n"
		"bond1 4\n"
		"atom 11 (6) (-1673, -578, 3702) def\n"
		"info atom atomtype = sp2\n"
		"bond1 5\n"
		"atom 12 (1) (-907, 1032, 1622) def\n"
		"bond1 6\n"
		"atom 13 (8) (-1099, 529, 4125) def\n"
		"info atom atomtype = sp2\n"
		"bond2 11\n"
		"atom 14 (1) (-1960, -821, -2711) def\n"
		"bond1 8\n"
		"atom 15 (6) (-3745, -4509, 878) def\n"
		"bond1 9\n"
		"atom 16 (1) (-2029, -1316, 4420) def\n"
		"bond1 11\n"
		"atom 17 (1) (-4496, -4053, 1524) def\n"
		"bond1 15\n"
		"atom 18 (1) (-2910, -4860, 1484) def\n"
		"bond1 15\n"
		"atom 19 (1) (-4187, -5350, 345) def\n"
		"bond1 15\n"
		"egroup (vanillin)\n"
		"end1\n"
		"group (Clipboard)\n"
		"info opengroup open = False\n"
		"egroup (Clipboard)\n"
		"end molecular machine part vanillin"
		;
	
	charBufParseTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size()==0);
	CPPUNIT_ASSERT(kelvinTemp == 300);
	checkCounts(19, 1, 3, 3,
	            12, 1, 0, 6, 0, 0,
	            8, 0, 3);
}

void
NanorexMMPImportExportRagelTest::charBufParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[1024], top, act;
	
	%% machine parse_tester;
	%% write data;
	%% write init;
	%% write exec;
}


void NanorexMMPImportExportRagelTest::fileParseTest(void)
{
	fileParseTestH2O();
	fileParseTestHOOH();
	fileParseTestChlorophyll();
	fileParseTestVanillin();
	fileParseTestNanocar();
}



void NanorexMMPImportExportRagelTest::fileParseTestH2O(void)
{
	ifstream infile("../src/Testing/MMP_TestFiles/H2O.mmp", ios::in);
	if(infile) {
		reset();
		RagelIstreamPtr testInput(infile);
		RagelIstreamPtr testInputEnd(infile, 0, ios::end);
		fileParseTestHelper(testInput, testInputEnd);
		CPPUNIT_ASSERT(groupNameStack.empty());
		checkCounts(3, 1, 3, 3,
		            2, 0, 0, 0, 0, 0,
		            0, 0, 3);
	}
}


void NanorexMMPImportExportRagelTest::fileParseTestHOOH(void)
{
	ifstream infile("../src/Testing/MMP_TestFiles/hydrogen_peroxide.mmp", ios::in);
	if(infile) {
		reset();
		RagelIstreamPtr testInput(infile);
		RagelIstreamPtr testInputEnd(infile, 0, ios::end);
		fileParseTestHelper(testInput, testInputEnd);
		CPPUNIT_ASSERT(groupNameStack.empty());
		checkCounts(4, 1, 3, 3,
		            3, 0, 0, 0, 0, 0,
		            0, 0, 3);
	}
}


void NanorexMMPImportExportRagelTest::fileParseTestChlorophyll(void)
{
	ifstream infile("../src/Testing/MMP_TestFiles/chlorophyll.mmp", ios::in);
	if(infile) {
		reset();
		RagelIstreamPtr testInput(infile, 0, ios::beg);
		RagelIstreamPtr testInputEnd(infile, 0, ios::end);
		fileParseTestHelper(testInput, testInputEnd);
		CPPUNIT_ASSERT(groupNameStack.empty());
		checkCounts(133, 1, 3, 3,
		            141, 0, 0, 0, 0, 0,
		            0, 0, 3);
	}
}


void NanorexMMPImportExportRagelTest::fileParseTestVanillin(void)
{
	ifstream infile("../src/Testing/MMP_TestFiles/vanillin.mmp", ios::in);
	if(infile) {
		reset();
		RagelIstreamPtr testInput(infile, 0, ios::beg);
		RagelIstreamPtr testInputEnd(infile, 0, ios::end);
		fileParseTestHelper(testInput, testInputEnd);
		CPPUNIT_ASSERT(groupNameStack.size()==0);
		CPPUNIT_ASSERT(kelvinTemp == 300);
		checkCounts(19, 1, 3, 3,
		            12, 1, 0, 6, 0, 0,
		            8, 0, 3);
	}
}


void NanorexMMPImportExportRagelTest::fileParseTestNanocar(void)
{
	ifstream infile("../src/Testing/MMP_TestFiles/nanocar.mmp", ios::in);
	if(infile) {
		reset();
		RagelIstreamPtr testInput(infile, 0, ios::beg);
		RagelIstreamPtr testInputEnd(infile, 0, ios::end);
		fileParseTestHelper(testInput, testInputEnd);
		CPPUNIT_ASSERT(groupNameStack.size()==0);
		CPPUNIT_ASSERT(kelvinTemp == 300);
		checkCounts(462, 9, 3, 3,
		            111, 0, 16, 72, 0, 425,
		            394, 3, 3);
	}
}


void
NanorexMMPImportExportRagelTest::
fileParseTestHelper(RagelIstreamPtr& p, RagelIstreamPtr& pe)
{
	RagelIstreamPtr eof(p);
	RagelIstreamPtr ts, te;
	int cs, stack[1024], top, act;
	RagelIstreamPtr charStringWithSpaceStart, charStringWithSpaceStop;
	RagelIstreamPtr lineStart;
	
	%% machine parse_tester;
	%% write data;
	%% write init;
	%% write exec;
}

