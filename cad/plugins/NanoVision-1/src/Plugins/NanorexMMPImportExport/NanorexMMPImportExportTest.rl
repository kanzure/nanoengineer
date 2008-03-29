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
	
	testStrings.push_back("atom 12  (10) (1,2,3) def\n");
	answers.push_back(AtomTestInfo(12, 10, 1, 2, 3, "def"));

	testStrings.push_back("atom    6   (99 ) ( 15632,-2,     -63  ) bas  \n");
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
}


void NanorexMMPImportExportTest::reset(void)
{
	atomIds.clear();
	atomicNums.clear();
	atomLocs.clear();
	atomStyles.clear();
	atomProps.clear();
	bonds.clear();
	lineNum = 1;
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
	cerr << lineNum << ": atom (" << atomId << ") ("
		<< x << ',' << y << ',' << z << ") " << atomStyle << endl;
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
	cerr << lineNum << ": bond" << bondType << " " << targetAtomId << endl;
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
	
main := space** bond_direction_line
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
	cerr << "newBondDirection: bond_direction " << atomId1 << " " << atomId2 << endl;
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
	
main := space**
		info_atom_line
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


void NanorexMMPImportExportTest::newAtomInfo(std::string const& key,
                                             std::string const& value)
{
	// string key1 = key;
	// stripTrailingWhiteSpaces(key1);
	// string value1 = value;
	// stripTrailingWhiteSpaces(value1);
	cerr << lineNum << ": info atom '" << key << "' = '" << value << "'" << endl;
	// infoAtomKeys.push_back(key);
	// infoAtomValues.push_back(value);
	atomProps.back().insert(make_pair(key, value));
}


void NanorexMMPImportExportTest::atomStmtTest(void)
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
	
main := space** atom_decl_line
		// %{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
		(space** atom_attrib_line)*
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


void NanorexMMPImportExportTest::multipleAtomStmtTest(void)
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
		"\n";
	// "atom 555 (555) (555,555,555)  style555\n";
	
	multipleAtomStmtTestHelper(testInput);
	
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
		EOL* nonNEWLINEspace* atom_decl_line => 
	{ // cerr << "atom_decl_line, p = " << p << endl;
		// newAtom(atomId, atomicNum, x, y, z, atomStyle);
			};
		EOL* nonNEWLINEspace* bond_line =>
	{ // cerr << "bond_line, p = " << p << endl;
		// newBond(stringVal, intVal);
			};
		EOL* nonNEWLINEspace* bond_direction_line =>
	{ // cerr << "bond_direction_line, p = " << p << endl;
		// newBondDirection(intVal, intVal2);
			};
		EOL* nonNEWLINEspace* info_atom_line =>
	{ // cerr << "info_atom_line, p = " << p << endl;
		// newAtomInfo(stringVal, stringVal2);
			};
		EOL* nonNEWLINEspace* 0 => {fret;};
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
NanorexMMPImportExportTest::
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


void NanorexMMPImportExportTest::molLineTest(void)
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
		                               "multiple_atom_stmt_test state machine");
		};
}%%


void NanorexMMPImportExportTest::molLineTestHelper(char const *const testInput)
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
NanorexMMPImportExportTest::newMolecule(string const& name, string const& style)
{
	currentMolName = name;
	currentMolStyle = style;
}


void NanorexMMPImportExportTest::groupLineTest(void)
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
	CPPUNIT_ASSERT(currentGroupStyle == "FirstGroupStyle");
	
	testInput = "group ( Group name with spaces   ) Group s\ttyle with spaces \n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 2);
	CPPUNIT_ASSERT(groupNameStack.back() == "Group name with spaces");
	CPPUNIT_ASSERT(currentGroupStyle == "Group s\ttyle with spaces");
	
	testInput = "group ( Group that has a name but no style)   \n";
	groupLineTestHelper(testInput);
	CPPUNIT_ASSERT(groupNameStack.size() == 3);
	CPPUNIT_ASSERT(groupNameStack.back() == "Group that has a name but no style");
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
		"group (amines) amineStyle\n"
		"group (histamines) def\n"
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
	include utilities "utilities.rl";
	include group "group.rl";
	
group_scanner :=
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
	
main := any* >{ /*cerr << "scanner call: p = " << p << endl;*/ fhold; fcall group_scanner; };
	
#main := WHITESPACE**
#		(group_mol_struct_stmt_begin_line |
#		 group_mol_struct_stmt_end_line )
#		$lerr { cerr << "Error encountered in "
#				"group_lines_test state machine" << endl;
#		};
	
#( group_view_data_stmt_begin_line $(group,2) |
#		  group_clipboard_stmt_begin_line $(group,2) |
#		  group_mol_struct_stmt_begin_line $(group,1) );
}%%


void
NanorexMMPImportExportTest::groupLineTestHelper(char const *const testInput)
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


void NanorexMMPImportExportTest::newViewDataGroup(void)
{
	cerr << lineNum << ": group (View Data)" << endl;
	currentGroupName = "View Data";
	groupNameStack.push_back(currentGroupName);
}


void NanorexMMPImportExportTest::endViewDataGroup(void)
{
	cerr << lineNum << ": endgroup (View Data)" << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}


void
NanorexMMPImportExportTest::newMolStructGroup(std::string const& name,
                                              std::string const& style)
{
// 	istringstream nameStream(name);
// 	string token1(""), token2("");
// 	nameStream >> token1 >> token2;
// 	if(token1 == "View" && token2 == "Data")
// 		newViewDataGroup();
// 	
// 	else if(token1 == "Clipboard" && token2 == "")
// 		newClipboardGroup();
// 	
// 	else {
		cerr << lineNum << ": group (" << name << ") " << style << endl;
		currentGroupName = name;
		groupNameStack.push_back(currentGroupName);
		currentGroupStyle = style;
	// }
}


void NanorexMMPImportExportTest::endMolStructGroup(std::string const& name)
{
	// comparing for errors should be done by parser application
	// here we are only testing to see if the tokens are being recognized
// 	istringstream nameStream(name);
// 	string token1(""), token2("");
// 	nameStream >> token1 >> token2;
// 	if(token1 == "View" && token2 == "Data")
// 		endViewDataGroup();
// 	
// 	else if(token1 == "Clipboard" && token2 == "")
// 		endClipboardGroup();
// 	
// 	else {
		cerr << lineNum << ": endgroup (" << name << ")  "
			<< "[stack-top = " << groupNameStack.back() << ']' << endl;
		currentGroupName = groupNameStack.back();
		groupNameStack.pop_back();
	//	}
}


void NanorexMMPImportExportTest::newClipboardGroup(void)
{
	cerr << lineNum << ": group (Clipboard)" << endl;
	currentGroupName = "Clipboard";
	groupNameStack.push_back(currentGroupName);
}


void NanorexMMPImportExportTest::endClipboardGroup(void)
{
	cerr << lineNum << ": endgroup (Clipboard)" << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}


void NanorexMMPImportExportTest::endGroup(string const& name)
{
	// comparing for errors should be done by parser application
	// here we are only testing to see if the tokens are being recognized
	cerr << lineNum << ": endgroup (" << name << ")  "
		<< "[stack-top = " << groupNameStack.back() << ']' << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}
