#line 1 "NanorexMMPImportExportTest.rl"
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExportTest.h"
#include <sstream>
#include <cfloat>

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


void NanorexMMPImportExportTest::reset(void)
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


void NanorexMMPImportExportTest::syntaxError(string const& errorMessage)
{
	cerr << lineNum << ": Syntax Error : " << errorMessage << endl;
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

	testStrings.push_back("atom 12  (10) (1,2,3) def  "
	                      "# this one's got a comment \n");
	answers.push_back(AtomTestInfo(12, 10, 1, 2, 3, "def"));
	
	testStrings.push_back("atom    6   (99 ) ( 15632,-2,     -63  ) bas"
	                      "# comment where the '#' touches the style\n");
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
	CPPUNIT_ASSERT(atomIds.size() == testStrings.size());
	CPPUNIT_ASSERT(atomicNums.size() == testStrings.size());
	CPPUNIT_ASSERT(atomLocs.size() == testStrings.size());
	CPPUNIT_ASSERT(atomStyles.size() == testStrings.size());
}


#line 120 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	#line 133 "NanorexMMPImportExportTest.rl"
	
#line 124 "NanorexMMPImportExportTest.cpp"
static const char _atom_decl_line_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 5, 1, 7, 1, 8, 1, 
	9, 1, 10, 1, 11, 1, 14, 2, 
	0, 13, 2, 3, 9, 2, 3, 10, 
	2, 3, 11, 2, 4, 5, 2, 6, 
	12, 3, 4, 6, 12, 4, 6, 12, 
	0, 13, 5, 4, 6, 12, 0, 13
	
};

static const short _atom_decl_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 11, 17, 
	23, 28, 34, 41, 46, 50, 55, 63, 
	65, 72, 77, 85, 87, 94, 99, 107, 
	109, 116, 121, 126, 138, 140, 154, 168, 
	181, 195, 202, 204, 211, 218, 225, 227, 
	234, 241, 248, 250, 257, 264, 271, 277
};

static const char _atom_decl_line_test_trans_keys[] = {
	32, 97, 9, 13, 116, 111, 109, 9, 
	32, 11, 13, 9, 32, 11, 13, 48, 
	57, 9, 32, 11, 13, 48, 57, 9, 
	32, 40, 11, 13, 9, 32, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 48, 
	57, 9, 32, 41, 11, 13, 9, 32, 
	11, 13, 9, 32, 40, 11, 13, 9, 
	32, 43, 45, 11, 13, 48, 57, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	9, 32, 44, 11, 13, 9, 32, 43, 
	45, 11, 13, 48, 57, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 9, 32, 43, 45, 11, 
	13, 48, 57, 48, 57, 9, 32, 41, 
	11, 13, 48, 57, 9, 32, 41, 11, 
	13, 10, 32, 35, 9, 13, 10, 32, 
	35, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 11, 13, 
	48, 57, 48, 57, 9, 32, 41, 11, 
	13, 48, 57, 9, 32, 41, 11, 13, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	9, 32, 41, 11, 13, 48, 57, 9, 
	32, 11, 13, 48, 57, 0
};

static const char _atom_decl_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 2, 4, 4, 3, 
	4, 3, 0, 3, 3, 3, 0, 3, 
	3, 3, 0, 3, 3, 3, 2, 0
};

static const char _atom_decl_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 0, 5, 5, 5, 
	5, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 2, 0
};

static const unsigned char _atom_decl_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 14, 19, 
	24, 29, 34, 40, 45, 49, 54, 61, 
	63, 69, 74, 81, 83, 89, 94, 101, 
	103, 109, 114, 119, 128, 131, 141, 151, 
	160, 170, 176, 178, 184, 190, 196, 198, 
	204, 210, 216, 218, 224, 230, 236, 241
};

static const char _atom_decl_line_test_indicies[] = {
	0, 2, 0, 1, 3, 1, 4, 1, 
	5, 1, 6, 6, 6, 1, 6, 6, 
	6, 7, 1, 8, 8, 8, 9, 1, 
	10, 10, 11, 10, 1, 11, 11, 11, 
	12, 1, 13, 13, 14, 13, 15, 1, 
	13, 13, 14, 13, 1, 16, 16, 16, 
	1, 17, 17, 18, 17, 1, 18, 18, 
	19, 20, 18, 21, 1, 21, 1, 22, 
	22, 23, 22, 24, 1, 22, 22, 23, 
	22, 1, 25, 25, 26, 27, 25, 28, 
	1, 28, 1, 29, 29, 30, 29, 31, 
	1, 29, 29, 30, 29, 1, 32, 32, 
	33, 34, 32, 35, 1, 35, 1, 36, 
	36, 37, 36, 38, 1, 36, 36, 37, 
	36, 1, 40, 39, 41, 39, 1, 40, 
	39, 41, 42, 39, 42, 42, 42, 1, 
	1, 40, 41, 44, 43, 45, 47, 43, 
	46, 47, 47, 47, 1, 40, 48, 41, 
	50, 48, 49, 50, 50, 50, 1, 49, 
	49, 50, 49, 49, 50, 50, 50, 1, 
	52, 51, 53, 50, 51, 49, 50, 50, 
	50, 1, 36, 36, 37, 36, 38, 1, 
	54, 1, 55, 55, 56, 55, 57, 1, 
	55, 55, 56, 55, 57, 1, 29, 29, 
	30, 29, 31, 1, 58, 1, 59, 59, 
	60, 59, 61, 1, 59, 59, 60, 59, 
	61, 1, 22, 22, 23, 22, 24, 1, 
	62, 1, 63, 63, 64, 63, 65, 1, 
	63, 63, 64, 63, 65, 1, 13, 13, 
	14, 13, 15, 1, 8, 8, 8, 9, 
	1, 66, 0
};

static const char _atom_decl_line_test_trans_targs_wi[] = {
	1, 0, 2, 3, 4, 5, 6, 7, 
	8, 46, 8, 9, 10, 11, 12, 45, 
	13, 13, 14, 15, 42, 16, 17, 18, 
	41, 18, 19, 38, 20, 21, 22, 37, 
	22, 23, 34, 24, 25, 26, 33, 27, 
	47, 28, 29, 30, 47, 28, 31, 32, 
	30, 31, 32, 30, 47, 28, 35, 25, 
	26, 36, 39, 21, 22, 40, 43, 17, 
	18, 44, 0
};

static const char _atom_decl_line_test_trans_actions_wi[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	11, 3, 0, 0, 0, 0, 0, 3, 
	13, 0, 0, 0, 0, 0, 0, 15, 
	3, 0, 0, 0, 0, 0, 17, 3, 
	0, 0, 0, 0, 0, 19, 3, 0, 
	23, 0, 0, 41, 50, 41, 7, 35, 
	0, 0, 9, 38, 45, 38, 0, 5, 
	32, 3, 0, 5, 29, 3, 0, 5, 
	26, 3, 21
};

static const char _atom_decl_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 1, 
	0, 0, 1, 0, 0, 0, 0, 0, 
	1, 0, 0, 0, 1, 0, 0, 0, 
	1, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 0, 0, 1, 
	0, 0, 0, 1, 0, 0, 0, 0
};

static const int atom_decl_line_test_start = 1;
static const int atom_decl_line_test_first_final = 47;
static const int atom_decl_line_test_error = 0;

static const int atom_decl_line_test_en_main = 1;

#line 134 "NanorexMMPImportExportTest.rl"
	
#line 285 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_decl_line_test_start;
	}
#line 135 "NanorexMMPImportExportTest.rl"
	
#line 291 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _atom_decl_line_test_trans_keys + _atom_decl_line_test_key_offsets[cs];
	_trans = _atom_decl_line_test_index_offsets[cs];

	_klen = _atom_decl_line_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _atom_decl_line_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _atom_decl_line_test_indicies[_trans];
	cs = _atom_decl_line_test_trans_targs_wi[_trans];

	if ( _atom_decl_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _atom_decl_line_test_actions + _atom_decl_line_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 4:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 5:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 6:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 7:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 8:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 9:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 10:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 11:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 12:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 13:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 14:
#line 115 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 428 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_decl_line_test_actions + _atom_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 441 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	_out: {}
	}
#line 136 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newAtom(int atomId, int atomicNum,
                                         int x, int y, int z,
                                         std::string const& atomStyle)
{
	++atomCount;
	cerr << lineNum << ": atom " << atomId << " (" << atomicNum << ") ("
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


#line 190 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 201 "NanorexMMPImportExportTest.rl"
	
#line 508 "NanorexMMPImportExportTest.cpp"
static const char _bond_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 2, 3, 0
	
};

static const char _bond_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 12, 16, 
	22, 29, 36, 38, 45
};

static const char _bond_line_test_trans_keys[] = {
	32, 98, 9, 13, 111, 110, 100, 97, 
	99, 103, 49, 51, 9, 32, 11, 13, 
	9, 32, 11, 13, 48, 57, 10, 32, 
	35, 9, 13, 48, 57, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 10, 32, 
	35, 9, 13, 48, 57, 0
};

static const char _bond_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 3, 2, 2, 
	3, 3, 2, 3, 0
};

static const char _bond_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 1, 2, 
	2, 2, 0, 2, 0
};

static const char _bond_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 15, 19, 
	24, 30, 36, 39, 45
};

static const char _bond_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 6, 6, 0, 7, 
	7, 7, 0, 7, 7, 7, 8, 0, 
	10, 9, 11, 9, 12, 0, 14, 13, 
	15, 13, 8, 0, 0, 14, 15, 10, 
	9, 11, 9, 12, 0, 0, 0
};

static const char _bond_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 9, 12, 10, 11, 9, 12, 10
};

static const char _bond_line_test_trans_actions_wi[] = {
	11, 0, 0, 0, 0, 0, 9, 0, 
	0, 7, 13, 7, 5, 0, 1, 0
};

static const char _bond_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 0
};

static const char _bond_line_test_eof_actions[] = {
	0, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 0
};

static const int bond_line_test_start = 1;
static const int bond_line_test_first_final = 12;
static const int bond_line_test_error = 0;

static const int bond_line_test_en_main = 1;

#line 202 "NanorexMMPImportExportTest.rl"
	
#line 581 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_line_test_start;
	}
#line 203 "NanorexMMPImportExportTest.rl"
	
#line 587 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _bond_line_test_trans_keys + _bond_line_test_key_offsets[cs];
	_trans = _bond_line_test_index_offsets[cs];

	_klen = _bond_line_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _bond_line_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _bond_line_test_indicies[_trans];
	cs = _bond_line_test_trans_targs_wi[_trans];

	if ( _bond_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _bond_line_test_actions + _bond_line_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 4:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 5:
#line 185 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 686 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_line_test_actions + _bond_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 699 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _bond_line_test_actions + _bond_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 5:
#line 185 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 721 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 204 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newBond(std::string const& bondType,
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


#line 258 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 270 "NanorexMMPImportExportTest.rl"
	
#line 785 "NanorexMMPImportExportTest.cpp"
static const char _bond_direction_line_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 6, 2, 0, 5
};

static const char _bond_direction_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 8, 9, 
	10, 11, 12, 13, 14, 15, 16, 17, 
	21, 27, 33, 39, 46, 51, 53, 60, 
	66
};

static const char _bond_direction_line_test_trans_keys[] = {
	32, 98, 9, 13, 111, 110, 100, 95, 
	100, 105, 114, 101, 99, 116, 105, 111, 
	110, 9, 32, 11, 13, 9, 32, 11, 
	13, 48, 57, 9, 32, 11, 13, 48, 
	57, 9, 32, 11, 13, 48, 57, 10, 
	32, 35, 9, 13, 48, 57, 10, 32, 
	35, 9, 13, -1, 10, 10, 32, 35, 
	9, 13, 48, 57, 9, 32, 11, 13, 
	48, 57, 0
};

static const char _bond_direction_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 2, 
	2, 2, 2, 3, 3, 2, 3, 2, 
	0
};

static const char _bond_direction_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 1, 
	2, 2, 2, 2, 1, 0, 2, 2, 
	0
};

static const char _bond_direction_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 12, 14, 
	16, 18, 20, 22, 24, 26, 28, 30, 
	34, 39, 44, 49, 55, 60, 63, 69, 
	74
};

static const char _bond_direction_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 0, 7, 0, 8, 0, 
	9, 0, 10, 0, 11, 0, 12, 0, 
	13, 0, 14, 0, 15, 0, 16, 16, 
	16, 0, 16, 16, 16, 17, 0, 18, 
	18, 18, 19, 0, 18, 18, 18, 20, 
	0, 22, 21, 23, 21, 24, 0, 22, 
	21, 23, 21, 0, 0, 22, 23, 22, 
	21, 23, 21, 24, 0, 18, 18, 18, 
	19, 0, 0, 0
};

static const char _bond_direction_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 9, 10, 11, 12, 13, 14, 15, 
	16, 17, 18, 23, 19, 20, 24, 21, 
	22
};

static const char _bond_direction_line_test_trans_actions_wi[] = {
	9, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 11, 0, 
	7
};

static const char _bond_direction_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 0, 5, 0, 0, 0, 0, 
	0
};

static const char _bond_direction_line_test_eof_actions[] = {
	0, 9, 9, 9, 9, 9, 9, 9, 
	9, 9, 9, 9, 9, 9, 9, 9, 
	9, 9, 9, 9, 9, 9, 9, 9, 
	0
};

static const int bond_direction_line_test_start = 1;
static const int bond_direction_line_test_first_final = 24;
static const int bond_direction_line_test_error = 0;

static const int bond_direction_line_test_en_main = 1;

#line 271 "NanorexMMPImportExportTest.rl"
	
#line 880 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_direction_line_test_start;
	}
#line 272 "NanorexMMPImportExportTest.rl"
	
#line 886 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _bond_direction_line_test_trans_keys + _bond_direction_line_test_key_offsets[cs];
	_trans = _bond_direction_line_test_index_offsets[cs];

	_klen = _bond_direction_line_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _bond_direction_line_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _bond_direction_line_test_indicies[_trans];
	cs = _bond_direction_line_test_trans_targs_wi[_trans];

	if ( _bond_direction_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _bond_direction_line_test_actions + _bond_direction_line_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 6:
#line 253 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 985 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_direction_line_test_actions + _bond_direction_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 1002 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _bond_direction_line_test_actions + _bond_direction_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 6:
#line 253 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 1024 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 273 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newBondDirection(int atomId1, int atomId2)
{
	cerr << lineNum << ": bond_direction " << atomId1 << " " << atomId2 << endl;
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


#line 328 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 339 "NanorexMMPImportExportTest.rl"
	
#line 1087 "NanorexMMPImportExportTest.cpp"
static const char _info_atom_line_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 6, 2, 0, 5, 2, 1, 
	2, 2, 1, 3, 2, 1, 4, 3, 
	4, 0, 5, 4, 1, 4, 0, 5
	
};

static const unsigned char _info_atom_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 11, 16, 
	17, 18, 19, 23, 34, 48, 62, 75, 
	89, 100, 114, 128, 130, 143, 157
};

static const char _info_atom_line_test_trans_keys[] = {
	32, 105, 9, 13, 110, 102, 111, 9, 
	32, 11, 13, 9, 32, 97, 11, 13, 
	116, 111, 109, 9, 32, 11, 13, 9, 
	32, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 61, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 61, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 61, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 9, 32, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 0
};

static const char _info_atom_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 2, 3, 1, 
	1, 1, 2, 3, 4, 4, 3, 4, 
	3, 4, 4, 2, 3, 4, 0
};

static const char _info_atom_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 5, 5, 5, 5, 
	4, 5, 5, 0, 5, 5, 0
};

static const char _info_atom_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 14, 19, 
	21, 23, 25, 29, 37, 47, 57, 66, 
	76, 84, 94, 104, 107, 116, 126
};

static const char _info_atom_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 6, 0, 6, 6, 
	7, 6, 0, 8, 0, 9, 0, 10, 
	0, 11, 11, 11, 0, 11, 11, 12, 
	11, 12, 12, 12, 0, 13, 13, 16, 
	15, 13, 14, 15, 15, 15, 0, 17, 
	17, 20, 19, 17, 18, 19, 19, 19, 
	0, 18, 18, 19, 18, 18, 19, 19, 
	19, 0, 21, 21, 22, 19, 21, 18, 
	19, 19, 19, 0, 20, 20, 23, 20, 
	23, 23, 23, 0, 25, 24, 26, 28, 
	24, 27, 28, 28, 28, 0, 30, 29, 
	31, 33, 29, 32, 33, 33, 33, 0, 
	0, 30, 31, 32, 32, 33, 32, 32, 
	33, 33, 33, 0, 35, 34, 36, 33, 
	34, 32, 33, 33, 33, 0, 0, 0
};

static const char _info_atom_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 9, 10, 11, 12, 13, 14, 15, 
	16, 13, 14, 15, 16, 13, 16, 17, 
	18, 22, 19, 20, 21, 18, 22, 19, 
	20, 21, 18, 22, 19
};

static const char _info_atom_line_test_trans_actions_wi[] = {
	9, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 17, 1, 14, 
	17, 0, 0, 3, 0, 5, 5, 0, 
	20, 27, 20, 1, 14, 0, 11, 0, 
	0, 3, 7, 23, 7
};

static const char _info_atom_line_test_eof_actions[] = {
	0, 9, 9, 9, 9, 9, 9, 9, 
	9, 9, 9, 9, 9, 9, 9, 9, 
	9, 9, 9, 9, 9, 9, 0
};

static const int info_atom_line_test_start = 1;
static const int info_atom_line_test_first_final = 22;
static const int info_atom_line_test_error = 0;

static const int info_atom_line_test_en_main = 1;

#line 340 "NanorexMMPImportExportTest.rl"
	
#line 1192 "NanorexMMPImportExportTest.cpp"
	{
	cs = info_atom_line_test_start;
	}
#line 341 "NanorexMMPImportExportTest.rl"
	
#line 1198 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _info_atom_line_test_trans_keys + _info_atom_line_test_key_offsets[cs];
	_trans = _info_atom_line_test_index_offsets[cs];

	_klen = _info_atom_line_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _info_atom_line_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _info_atom_line_test_indicies[_trans];
	cs = _info_atom_line_test_trans_targs_wi[_trans];

	if ( _info_atom_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _info_atom_line_test_actions + _info_atom_line_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 1:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 6:
#line 323 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1311 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _info_atom_line_test_actions + _info_atom_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 6:
#line 323 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1334 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 342 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newAtomInfo(std::string const& key,
                                             std::string const& value)
{
	++infoAtomCount;
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


#line 405 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 416 "NanorexMMPImportExportTest.rl"
	
#line 1404 "NanorexMMPImportExportTest.cpp"
static const char _atom_stmt_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 2, 
	0, 16, 2, 0, 19, 2, 0, 20, 
	2, 5, 12, 2, 5, 13, 2, 5, 
	14, 2, 6, 7, 2, 6, 8, 2, 
	6, 9, 2, 8, 15, 2, 17, 0, 
	2, 21, 0, 3, 6, 8, 15, 3, 
	9, 0, 20, 4, 6, 9, 0, 20, 
	4, 8, 15, 0, 16, 5, 6, 8, 
	15, 0, 16
};

static const short _atom_stmt_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 12, 18, 
	24, 29, 35, 42, 47, 51, 56, 64, 
	66, 73, 78, 86, 88, 95, 100, 108, 
	110, 117, 122, 127, 139, 146, 147, 148, 
	149, 153, 159, 165, 170, 176, 183, 188, 
	192, 197, 205, 207, 214, 219, 227, 229, 
	236, 241, 249, 251, 258, 263, 268, 280, 
	281, 282, 283, 289, 293, 299, 306, 313, 
	315, 322, 323, 324, 325, 326, 327, 328, 
	329, 330, 331, 335, 341, 347, 353, 360, 
	365, 367, 374, 380, 381, 382, 383, 387, 
	392, 393, 394, 395, 399, 410, 424, 438, 
	451, 465, 476, 490, 504, 506, 519, 533, 
	535, 549, 563, 576, 590, 597, 599, 606, 
	613, 620, 622, 629, 636, 643, 645, 652, 
	659, 666, 672, 674, 688, 702, 715, 729, 
	736, 738, 745, 752, 759, 761, 768, 775, 
	782, 784, 791, 798, 805, 811, 818
};

static const char _atom_stmt_test_trans_keys[] = {
	10, 32, 97, 9, 13, 116, 111, 109, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 9, 32, 11, 13, 48, 57, 
	9, 32, 40, 11, 13, 9, 32, 11, 
	13, 48, 57, 9, 32, 41, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 9, 
	32, 11, 13, 9, 32, 40, 11, 13, 
	9, 32, 43, 45, 11, 13, 48, 57, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 9, 32, 44, 11, 13, 9, 32, 
	43, 45, 11, 13, 48, 57, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 9, 32, 43, 45, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	41, 11, 13, 48, 57, 9, 32, 41, 
	11, 13, 10, 32, 35, 9, 13, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 97, 98, 105, 
	9, 13, 116, 111, 109, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 9, 
	32, 11, 13, 48, 57, 9, 32, 40, 
	11, 13, 9, 32, 11, 13, 48, 57, 
	9, 32, 41, 11, 13, 48, 57, 9, 
	32, 41, 11, 13, 9, 32, 11, 13, 
	9, 32, 40, 11, 13, 9, 32, 43, 
	45, 11, 13, 48, 57, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 9, 32, 43, 45, 11, 
	13, 48, 57, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 9, 32, 43, 45, 11, 13, 48, 
	57, 48, 57, 9, 32, 41, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 10, 
	32, 35, 9, 13, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	111, 110, 100, 95, 97, 99, 103, 49, 
	51, 9, 32, 11, 13, 9, 32, 11, 
	13, 48, 57, 10, 32, 35, 9, 13, 
	48, 57, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 10, 32, 35, 9, 13, 
	48, 57, 100, 105, 114, 101, 99, 116, 
	105, 111, 110, 9, 32, 11, 13, 9, 
	32, 11, 13, 48, 57, 9, 32, 11, 
	13, 48, 57, 9, 32, 11, 13, 48, 
	57, 10, 32, 35, 9, 13, 48, 57, 
	10, 32, 35, 9, 13, -1, 10, 10, 
	32, 35, 9, 13, 48, 57, 9, 32, 
	11, 13, 48, 57, 110, 102, 111, 9, 
	32, 11, 13, 9, 32, 97, 11, 13, 
	116, 111, 109, 9, 32, 11, 13, 9, 
	32, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 61, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 61, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 61, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 9, 32, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 11, 13, 48, 57, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	41, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 9, 32, 41, 11, 13, 
	48, 57, 9, 32, 11, 13, 48, 57, 
	-1, 10, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 41, 11, 13, 48, 57, 
	48, 57, 9, 32, 41, 11, 13, 48, 
	57, 9, 32, 41, 11, 13, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	41, 11, 13, 48, 57, 9, 32, 11, 
	13, 48, 57, 10, 32, 97, 98, 105, 
	9, 13, 10, 32, 97, 98, 105, 9, 
	13, 0
};

static const char _atom_stmt_test_single_lengths[] = {
	0, 3, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 5, 1, 1, 1, 
	2, 2, 2, 3, 2, 3, 3, 2, 
	3, 4, 0, 3, 3, 4, 0, 3, 
	3, 4, 0, 3, 3, 3, 4, 1, 
	1, 1, 4, 2, 2, 3, 3, 2, 
	3, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 2, 2, 3, 3, 
	2, 3, 2, 1, 1, 1, 2, 3, 
	1, 1, 1, 2, 3, 4, 4, 3, 
	4, 3, 4, 4, 2, 3, 4, 2, 
	4, 4, 3, 4, 3, 0, 3, 3, 
	3, 0, 3, 3, 3, 0, 3, 3, 
	3, 2, 2, 4, 4, 3, 4, 3, 
	0, 3, 3, 3, 0, 3, 3, 3, 
	0, 3, 3, 3, 2, 5, 5
};

static const char _atom_stmt_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 1, 0, 0, 0, 
	1, 2, 2, 1, 2, 2, 1, 1, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 1, 4, 0, 
	0, 0, 1, 1, 2, 2, 2, 0, 
	2, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 2, 2, 2, 1, 
	0, 2, 2, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	5, 5, 5, 5, 2, 1, 2, 2, 
	2, 1, 2, 2, 2, 1, 2, 2, 
	2, 2, 0, 5, 5, 5, 5, 2, 
	1, 2, 2, 2, 1, 2, 2, 2, 
	1, 2, 2, 2, 2, 1, 1
};

static const short _atom_stmt_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 15, 20, 
	25, 30, 35, 41, 46, 50, 55, 62, 
	64, 70, 75, 82, 84, 90, 95, 102, 
	104, 110, 115, 120, 129, 136, 138, 140, 
	142, 146, 151, 156, 161, 166, 172, 177, 
	181, 186, 193, 195, 201, 206, 213, 215, 
	221, 226, 233, 235, 241, 246, 251, 260, 
	262, 264, 266, 272, 276, 281, 287, 293, 
	296, 302, 304, 306, 308, 310, 312, 314, 
	316, 318, 320, 324, 329, 334, 339, 345, 
	350, 353, 359, 364, 366, 368, 370, 374, 
	379, 381, 383, 385, 389, 397, 407, 417, 
	426, 436, 444, 454, 464, 467, 476, 486, 
	489, 499, 509, 518, 528, 534, 536, 542, 
	548, 554, 556, 562, 568, 574, 576, 582, 
	588, 594, 599, 602, 612, 622, 631, 641, 
	647, 649, 655, 661, 667, 669, 675, 681, 
	687, 689, 695, 701, 707, 712, 719
};

static const unsigned char _atom_stmt_test_indicies[] = {
	2, 0, 3, 0, 1, 4, 1, 5, 
	1, 6, 1, 7, 7, 7, 1, 7, 
	7, 7, 8, 1, 9, 9, 9, 10, 
	1, 11, 11, 12, 11, 1, 12, 12, 
	12, 13, 1, 14, 14, 15, 14, 16, 
	1, 14, 14, 15, 14, 1, 17, 17, 
	17, 1, 18, 18, 19, 18, 1, 19, 
	19, 20, 21, 19, 22, 1, 22, 1, 
	23, 23, 24, 23, 25, 1, 23, 23, 
	24, 23, 1, 26, 26, 27, 28, 26, 
	29, 1, 29, 1, 30, 30, 31, 30, 
	32, 1, 30, 30, 31, 30, 1, 33, 
	33, 34, 35, 33, 36, 1, 36, 1, 
	37, 37, 38, 37, 39, 1, 37, 37, 
	38, 37, 1, 41, 40, 42, 40, 1, 
	41, 40, 42, 43, 40, 43, 43, 43, 
	1, 46, 45, 47, 48, 49, 45, 44, 
	50, 44, 51, 44, 52, 44, 53, 53, 
	53, 44, 53, 53, 53, 54, 44, 55, 
	55, 55, 56, 44, 57, 57, 58, 57, 
	44, 58, 58, 58, 59, 44, 60, 60, 
	61, 60, 62, 44, 60, 60, 61, 60, 
	44, 63, 63, 63, 44, 64, 64, 65, 
	64, 44, 65, 65, 66, 67, 65, 68, 
	44, 68, 44, 69, 69, 70, 69, 71, 
	44, 69, 69, 70, 69, 44, 72, 72, 
	73, 74, 72, 75, 44, 75, 44, 76, 
	76, 77, 76, 78, 44, 76, 76, 77, 
	76, 44, 79, 79, 80, 81, 79, 82, 
	44, 82, 44, 83, 83, 84, 83, 85, 
	44, 83, 83, 84, 83, 44, 87, 86, 
	88, 86, 44, 87, 86, 88, 89, 86, 
	89, 89, 89, 44, 90, 44, 91, 44, 
	92, 44, 94, 93, 93, 93, 93, 44, 
	95, 95, 95, 44, 95, 95, 95, 96, 
	44, 98, 97, 99, 97, 100, 44, 102, 
	101, 103, 101, 96, 44, 44, 102, 103, 
	98, 97, 99, 97, 100, 44, 104, 44, 
	105, 44, 106, 44, 107, 44, 108, 44, 
	109, 44, 110, 44, 111, 44, 112, 44, 
	113, 113, 113, 44, 113, 113, 113, 114, 
	44, 115, 115, 115, 116, 44, 115, 115, 
	115, 117, 44, 119, 118, 120, 118, 121, 
	44, 119, 118, 120, 118, 44, 44, 119, 
	120, 119, 118, 120, 118, 121, 44, 115, 
	115, 115, 116, 44, 122, 44, 123, 44, 
	124, 44, 125, 125, 125, 44, 125, 125, 
	126, 125, 44, 127, 44, 128, 44, 129, 
	44, 130, 130, 130, 44, 130, 130, 131, 
	130, 131, 131, 131, 44, 132, 132, 135, 
	134, 132, 133, 134, 134, 134, 44, 136, 
	136, 139, 138, 136, 137, 138, 138, 138, 
	44, 137, 137, 138, 137, 137, 138, 138, 
	138, 44, 140, 140, 141, 138, 140, 137, 
	138, 138, 138, 44, 139, 139, 142, 139, 
	142, 142, 142, 44, 144, 143, 145, 147, 
	143, 146, 147, 147, 147, 44, 149, 148, 
	150, 152, 148, 151, 152, 152, 152, 44, 
	44, 149, 150, 151, 151, 152, 151, 151, 
	152, 152, 152, 44, 154, 153, 155, 152, 
	153, 151, 152, 152, 152, 44, 44, 87, 
	88, 157, 156, 158, 160, 156, 159, 160, 
	160, 160, 44, 87, 161, 88, 163, 161, 
	162, 163, 163, 163, 44, 162, 162, 163, 
	162, 162, 163, 163, 163, 44, 165, 164, 
	166, 163, 164, 162, 163, 163, 163, 44, 
	83, 83, 84, 83, 85, 44, 167, 44, 
	168, 168, 169, 168, 170, 44, 168, 168, 
	169, 168, 170, 44, 76, 76, 77, 76, 
	78, 44, 171, 44, 172, 172, 173, 172, 
	174, 44, 172, 172, 173, 172, 174, 44, 
	69, 69, 70, 69, 71, 44, 175, 44, 
	176, 176, 177, 176, 178, 44, 176, 176, 
	177, 176, 178, 44, 60, 60, 61, 60, 
	62, 44, 55, 55, 55, 56, 44, 1, 
	41, 42, 180, 179, 181, 183, 179, 182, 
	183, 183, 183, 1, 41, 184, 42, 186, 
	184, 185, 186, 186, 186, 1, 185, 185, 
	186, 185, 185, 186, 186, 186, 1, 188, 
	187, 189, 186, 187, 185, 186, 186, 186, 
	1, 37, 37, 38, 37, 39, 1, 190, 
	1, 191, 191, 192, 191, 193, 1, 191, 
	191, 192, 191, 193, 1, 30, 30, 31, 
	30, 32, 1, 194, 1, 195, 195, 196, 
	195, 197, 1, 195, 195, 196, 195, 197, 
	1, 23, 23, 24, 23, 25, 1, 198, 
	1, 199, 199, 200, 199, 201, 1, 199, 
	199, 200, 199, 201, 1, 14, 14, 15, 
	14, 16, 1, 9, 9, 9, 10, 1, 
	203, 202, 204, 205, 206, 202, 44, 46, 
	45, 47, 48, 49, 45, 44, 0
};

static const unsigned char _atom_stmt_test_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 140, 8, 9, 10, 11, 12, 
	139, 13, 13, 14, 15, 136, 16, 17, 
	18, 135, 18, 19, 132, 20, 21, 22, 
	131, 22, 23, 128, 24, 25, 26, 127, 
	27, 141, 122, 123, 0, 28, 28, 29, 
	55, 83, 30, 31, 32, 33, 34, 35, 
	121, 35, 36, 37, 38, 39, 120, 40, 
	40, 41, 42, 117, 43, 44, 45, 116, 
	45, 46, 113, 47, 48, 49, 112, 49, 
	50, 109, 51, 52, 53, 108, 54, 142, 
	103, 104, 56, 57, 58, 59, 65, 60, 
	61, 62, 142, 63, 64, 62, 142, 63, 
	66, 67, 68, 69, 70, 71, 72, 73, 
	74, 75, 76, 77, 82, 78, 79, 142, 
	80, 81, 84, 85, 86, 87, 88, 89, 
	90, 91, 92, 93, 94, 95, 96, 97, 
	94, 95, 96, 97, 94, 97, 98, 99, 
	142, 100, 101, 102, 99, 142, 100, 101, 
	102, 99, 142, 100, 105, 142, 103, 106, 
	107, 105, 106, 107, 105, 142, 103, 110, 
	52, 53, 111, 114, 48, 49, 115, 118, 
	44, 45, 119, 124, 141, 122, 125, 126, 
	124, 125, 126, 124, 141, 122, 129, 25, 
	26, 130, 133, 21, 22, 134, 137, 17, 
	18, 138, 28, 28, 29, 55, 83
};

static const char _atom_stmt_test_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 21, 5, 0, 0, 0, 0, 0, 
	5, 23, 0, 0, 0, 0, 0, 0, 
	25, 5, 0, 0, 0, 0, 0, 27, 
	5, 0, 0, 0, 0, 0, 29, 5, 
	0, 39, 0, 0, 37, 0, 1, 0, 
	0, 0, 0, 0, 0, 0, 0, 21, 
	5, 0, 0, 0, 0, 0, 5, 23, 
	0, 0, 0, 0, 0, 0, 25, 5, 
	0, 0, 0, 0, 0, 27, 5, 0, 
	0, 0, 0, 0, 29, 5, 0, 39, 
	0, 0, 0, 0, 0, 33, 0, 0, 
	0, 31, 69, 31, 5, 0, 1, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 5, 0, 0, 42, 
	0, 9, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 60, 13, 57, 60, 
	0, 0, 15, 0, 17, 17, 0, 63, 
	83, 63, 13, 57, 0, 45, 0, 0, 
	15, 19, 79, 19, 75, 93, 75, 13, 
	57, 0, 0, 15, 66, 88, 66, 0, 
	11, 54, 5, 0, 11, 51, 5, 0, 
	11, 48, 5, 75, 93, 75, 13, 57, 
	0, 0, 15, 66, 88, 66, 0, 11, 
	54, 5, 0, 11, 51, 5, 0, 11, 
	48, 5, 35, 72, 35, 35, 35
};

static const char _atom_stmt_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 3, 0, 0, 3, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 7, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 3, 0, 0, 
	0, 3, 0, 0, 0, 0, 0
};

static const char _atom_stmt_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 37, 37, 37, 37, 37, 37, 
	37, 37, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 35, 0
};

static const int atom_stmt_test_start = 1;
static const int atom_stmt_test_first_final = 141;
static const int atom_stmt_test_error = 0;

static const int atom_stmt_test_en_main = 1;

#line 417 "NanorexMMPImportExportTest.rl"
	
#line 1814 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_stmt_test_start;
	}
#line 418 "NanorexMMPImportExportTest.rl"
	
#line 1820 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _atom_stmt_test_trans_keys + _atom_stmt_test_key_offsets[cs];
	_trans = _atom_stmt_test_index_offsets[cs];

	_klen = _atom_stmt_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _atom_stmt_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _atom_stmt_test_indicies[_trans];
	cs = _atom_stmt_test_trans_targs_wi[_trans];

	if ( _atom_stmt_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _atom_stmt_test_actions + _atom_stmt_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 398 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 400 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 1995 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_stmt_test_actions + _atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 2012 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _atom_stmt_test_actions + _atom_stmt_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 21:
#line 398 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 400 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2038 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 419 "NanorexMMPImportExportTest.rl"
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


#line 560 "NanorexMMPImportExportTest.rl"



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
	
	#line 576 "NanorexMMPImportExportTest.rl"
	
#line 2168 "NanorexMMPImportExportTest.cpp"
static const char _multiple_atom_stmt_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 22, 1, 23, 1, 
	24, 1, 29, 2, 0, 26, 2, 5, 
	12, 2, 5, 13, 2, 5, 14, 2, 
	6, 7, 2, 6, 8, 2, 6, 9, 
	2, 8, 15, 3, 0, 16, 21, 3, 
	0, 16, 25, 3, 0, 19, 27, 3, 
	0, 20, 28, 3, 6, 8, 15, 3, 
	17, 0, 26, 4, 9, 0, 20, 28, 
	5, 6, 9, 0, 20, 28, 5, 8, 
	15, 0, 16, 21, 5, 8, 15, 0, 
	16, 25, 6, 6, 8, 15, 0, 16, 
	21, 6, 6, 8, 15, 0, 16, 25
	
};

static const short _multiple_atom_stmt_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 12, 18, 
	24, 29, 35, 42, 47, 51, 56, 64, 
	66, 73, 78, 86, 88, 95, 100, 108, 
	110, 117, 122, 127, 139, 141, 155, 169, 
	182, 196, 203, 205, 212, 219, 226, 228, 
	235, 242, 249, 251, 258, 265, 272, 278, 
	286, 287, 288, 289, 293, 299, 305, 310, 
	316, 323, 328, 332, 337, 345, 347, 354, 
	359, 367, 369, 376, 381, 389, 391, 398, 
	403, 408, 420, 422, 436, 450, 463, 477, 
	484, 486, 493, 500, 507, 509, 516, 523, 
	530, 532, 539, 546, 553, 559, 560, 561, 
	562, 568, 572, 578, 585, 592, 594, 601, 
	602, 603, 604, 605, 606, 607, 608, 609, 
	610, 614, 620, 626, 632, 639, 644, 646, 
	653, 659, 660, 661, 662, 666, 671, 672, 
	673, 674, 678, 689, 703, 717, 730, 744, 
	755, 769, 783, 785, 798, 812, 821, 823, 
	828
};

static const char _multiple_atom_stmt_test_trans_keys[] = {
	10, 32, 97, 9, 13, 116, 111, 109, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 9, 32, 11, 13, 48, 57, 
	9, 32, 40, 11, 13, 9, 32, 11, 
	13, 48, 57, 9, 32, 41, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 9, 
	32, 11, 13, 9, 32, 40, 11, 13, 
	9, 32, 43, 45, 11, 13, 48, 57, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 9, 32, 44, 11, 13, 9, 32, 
	43, 45, 11, 13, 48, 57, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 9, 32, 43, 45, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	41, 11, 13, 48, 57, 9, 32, 41, 
	11, 13, 10, 32, 35, 9, 13, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 9, 32, 41, 11, 
	13, 48, 57, 48, 57, 9, 32, 41, 
	11, 13, 48, 57, 9, 32, 41, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 44, 11, 13, 48, 
	57, 9, 32, 41, 11, 13, 48, 57, 
	9, 32, 11, 13, 48, 57, 0, 9, 
	32, 97, 98, 105, 11, 13, 116, 111, 
	109, 9, 32, 11, 13, 9, 32, 11, 
	13, 48, 57, 9, 32, 11, 13, 48, 
	57, 9, 32, 40, 11, 13, 9, 32, 
	11, 13, 48, 57, 9, 32, 41, 11, 
	13, 48, 57, 9, 32, 41, 11, 13, 
	9, 32, 11, 13, 9, 32, 40, 11, 
	13, 9, 32, 43, 45, 11, 13, 48, 
	57, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 44, 11, 13, 9, 
	32, 43, 45, 11, 13, 48, 57, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	9, 32, 44, 11, 13, 9, 32, 43, 
	45, 11, 13, 48, 57, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	41, 11, 13, 10, 32, 35, 9, 13, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	41, 11, 13, 48, 57, 9, 32, 41, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 48, 
	57, 9, 32, 11, 13, 48, 57, 111, 
	110, 100, 95, 97, 99, 103, 49, 51, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 10, 32, 35, 9, 13, 48, 
	57, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 10, 32, 35, 9, 13, 48, 
	57, 100, 105, 114, 101, 99, 116, 105, 
	111, 110, 9, 32, 11, 13, 9, 32, 
	11, 13, 48, 57, 9, 32, 11, 13, 
	48, 57, 9, 32, 11, 13, 48, 57, 
	10, 32, 35, 9, 13, 48, 57, 10, 
	32, 35, 9, 13, -1, 10, 10, 32, 
	35, 9, 13, 48, 57, 9, 32, 11, 
	13, 48, 57, 110, 102, 111, 9, 32, 
	11, 13, 9, 32, 97, 11, 13, 116, 
	111, 109, 9, 32, 11, 13, 9, 32, 
	95, 11, 13, 48, 57, 65, 90, 97, 
	122, 9, 32, 61, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 9, 
	32, 61, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 61, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 0, 10, 32, 35, 
	97, 98, 105, 9, 13, -1, 10, 10, 
	32, 97, 9, 13, 0, 10, 32, 35, 
	97, 98, 105, 9, 13, 0
};

static const char _multiple_atom_stmt_test_single_lengths[] = {
	0, 3, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 2, 4, 4, 3, 
	4, 3, 0, 3, 3, 3, 0, 3, 
	3, 3, 0, 3, 3, 3, 2, 6, 
	1, 1, 1, 2, 2, 2, 3, 2, 
	3, 3, 2, 3, 4, 0, 3, 3, 
	4, 0, 3, 3, 4, 0, 3, 3, 
	3, 4, 2, 4, 4, 3, 4, 3, 
	0, 3, 3, 3, 0, 3, 3, 3, 
	0, 3, 3, 3, 2, 1, 1, 1, 
	4, 2, 2, 3, 3, 2, 3, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	2, 2, 2, 2, 3, 3, 2, 3, 
	2, 1, 1, 1, 2, 3, 1, 1, 
	1, 2, 3, 4, 4, 3, 4, 3, 
	4, 4, 2, 3, 4, 7, 2, 3, 
	7
};

static const char _multiple_atom_stmt_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 0, 5, 5, 5, 
	5, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 2, 1, 
	0, 0, 0, 1, 2, 2, 1, 2, 
	2, 1, 1, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	1, 4, 0, 5, 5, 5, 5, 2, 
	1, 2, 2, 2, 1, 2, 2, 2, 
	1, 2, 2, 2, 2, 0, 0, 0, 
	1, 1, 2, 2, 2, 0, 2, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 2, 2, 2, 2, 1, 0, 2, 
	2, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 4, 5, 5, 5, 5, 4, 
	5, 5, 0, 5, 5, 1, 0, 1, 
	1
};

static const short _multiple_atom_stmt_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 15, 20, 
	25, 30, 35, 41, 46, 50, 55, 62, 
	64, 70, 75, 82, 84, 90, 95, 102, 
	104, 110, 115, 120, 129, 132, 142, 152, 
	161, 171, 177, 179, 185, 191, 197, 199, 
	205, 211, 217, 219, 225, 231, 237, 242, 
	250, 252, 254, 256, 260, 265, 270, 275, 
	280, 286, 291, 295, 300, 307, 309, 315, 
	320, 327, 329, 335, 340, 347, 349, 355, 
	360, 365, 374, 377, 387, 397, 406, 416, 
	422, 424, 430, 436, 442, 444, 450, 456, 
	462, 464, 470, 476, 482, 487, 489, 491, 
	493, 499, 503, 508, 514, 520, 523, 529, 
	531, 533, 535, 537, 539, 541, 543, 545, 
	547, 551, 556, 561, 566, 572, 577, 580, 
	586, 591, 593, 595, 597, 601, 606, 608, 
	610, 612, 616, 624, 634, 644, 653, 663, 
	671, 681, 691, 694, 703, 713, 722, 725, 
	730
};

static const unsigned char _multiple_atom_stmt_test_indicies[] = {
	2, 1, 3, 1, 0, 4, 0, 5, 
	0, 6, 0, 7, 7, 7, 0, 7, 
	7, 7, 8, 0, 9, 9, 9, 10, 
	0, 11, 11, 12, 11, 0, 12, 12, 
	12, 13, 0, 14, 14, 15, 14, 16, 
	0, 14, 14, 15, 14, 0, 17, 17, 
	17, 0, 18, 18, 19, 18, 0, 19, 
	19, 20, 21, 19, 22, 0, 22, 0, 
	23, 23, 24, 23, 25, 0, 23, 23, 
	24, 23, 0, 26, 26, 27, 28, 26, 
	29, 0, 29, 0, 30, 30, 31, 30, 
	32, 0, 30, 30, 31, 30, 0, 33, 
	33, 34, 35, 33, 36, 0, 36, 0, 
	37, 37, 38, 37, 39, 0, 37, 37, 
	38, 37, 0, 41, 40, 42, 40, 0, 
	41, 40, 42, 43, 40, 43, 43, 43, 
	0, 0, 41, 42, 45, 44, 46, 48, 
	44, 47, 48, 48, 48, 0, 41, 49, 
	42, 51, 49, 50, 51, 51, 51, 0, 
	50, 50, 51, 50, 50, 51, 51, 51, 
	0, 53, 52, 54, 51, 52, 50, 51, 
	51, 51, 0, 37, 37, 38, 37, 39, 
	0, 55, 0, 56, 56, 57, 56, 58, 
	0, 56, 56, 57, 56, 58, 0, 30, 
	30, 31, 30, 32, 0, 59, 0, 60, 
	60, 61, 60, 62, 0, 60, 60, 61, 
	60, 62, 0, 23, 23, 24, 23, 25, 
	0, 63, 0, 64, 64, 65, 64, 66, 
	0, 64, 64, 65, 64, 66, 0, 14, 
	14, 15, 14, 16, 0, 9, 9, 9, 
	10, 0, 67, 69, 69, 70, 71, 72, 
	69, 68, 73, 68, 74, 68, 75, 68, 
	76, 76, 76, 68, 76, 76, 76, 77, 
	68, 78, 78, 78, 79, 68, 80, 80, 
	81, 80, 68, 81, 81, 81, 82, 68, 
	83, 83, 84, 83, 85, 68, 83, 83, 
	84, 83, 68, 86, 86, 86, 68, 87, 
	87, 88, 87, 68, 88, 88, 89, 90, 
	88, 91, 68, 91, 68, 92, 92, 93, 
	92, 94, 68, 92, 92, 93, 92, 68, 
	95, 95, 96, 97, 95, 98, 68, 98, 
	68, 99, 99, 100, 99, 101, 68, 99, 
	99, 100, 99, 68, 102, 102, 103, 104, 
	102, 105, 68, 105, 68, 106, 106, 107, 
	106, 108, 68, 106, 106, 107, 106, 68, 
	110, 109, 111, 109, 68, 110, 109, 111, 
	112, 109, 112, 112, 112, 68, 68, 110, 
	111, 114, 113, 115, 117, 113, 116, 117, 
	117, 117, 68, 110, 118, 111, 120, 118, 
	119, 120, 120, 120, 68, 119, 119, 120, 
	119, 119, 120, 120, 120, 68, 122, 121, 
	123, 120, 121, 119, 120, 120, 120, 68, 
	106, 106, 107, 106, 108, 68, 124, 68, 
	125, 125, 126, 125, 127, 68, 125, 125, 
	126, 125, 127, 68, 99, 99, 100, 99, 
	101, 68, 128, 68, 129, 129, 130, 129, 
	131, 68, 129, 129, 130, 129, 131, 68, 
	92, 92, 93, 92, 94, 68, 132, 68, 
	133, 133, 134, 133, 135, 68, 133, 133, 
	134, 133, 135, 68, 83, 83, 84, 83, 
	85, 68, 78, 78, 78, 79, 68, 136, 
	68, 137, 68, 138, 68, 140, 139, 139, 
	139, 139, 68, 141, 141, 141, 68, 141, 
	141, 141, 142, 68, 144, 143, 145, 143, 
	146, 68, 148, 147, 149, 147, 142, 68, 
	68, 148, 149, 144, 143, 145, 143, 146, 
	68, 150, 68, 151, 68, 152, 68, 153, 
	68, 154, 68, 155, 68, 156, 68, 157, 
	68, 158, 68, 159, 159, 159, 68, 159, 
	159, 159, 160, 68, 161, 161, 161, 162, 
	68, 161, 161, 161, 163, 68, 165, 164, 
	166, 164, 167, 68, 165, 164, 166, 164, 
	68, 68, 165, 166, 165, 164, 166, 164, 
	167, 68, 161, 161, 161, 162, 68, 168, 
	68, 169, 68, 170, 68, 171, 171, 171, 
	68, 171, 171, 172, 171, 68, 173, 68, 
	174, 68, 175, 68, 176, 176, 176, 68, 
	176, 176, 177, 176, 177, 177, 177, 68, 
	178, 178, 181, 180, 178, 179, 180, 180, 
	180, 68, 182, 182, 185, 184, 182, 183, 
	184, 184, 184, 68, 183, 183, 184, 183, 
	183, 184, 184, 184, 68, 186, 186, 187, 
	184, 186, 183, 184, 184, 184, 68, 185, 
	185, 188, 185, 188, 188, 188, 68, 190, 
	189, 191, 193, 189, 192, 193, 193, 193, 
	68, 195, 194, 196, 198, 194, 197, 198, 
	198, 198, 68, 68, 195, 196, 197, 197, 
	198, 197, 197, 198, 198, 198, 68, 200, 
	199, 201, 198, 199, 197, 198, 198, 198, 
	68, 67, 202, 69, 203, 70, 71, 72, 
	69, 68, 68, 202, 203, 2, 1, 3, 
	1, 0, 67, 202, 69, 203, 70, 71, 
	72, 69, 68, 0
};

static const unsigned char _multiple_atom_stmt_test_trans_targs_wi[] = {
	0, 1, 1, 2, 3, 4, 5, 6, 
	7, 8, 46, 8, 9, 10, 11, 12, 
	45, 13, 13, 14, 15, 42, 16, 17, 
	18, 41, 18, 19, 38, 20, 21, 22, 
	37, 22, 23, 34, 24, 25, 26, 33, 
	27, 143, 28, 29, 30, 143, 28, 31, 
	32, 30, 31, 32, 30, 143, 28, 35, 
	25, 26, 36, 39, 21, 22, 40, 43, 
	17, 18, 44, 144, 0, 47, 48, 93, 
	121, 49, 50, 51, 52, 53, 54, 92, 
	54, 55, 56, 57, 58, 91, 59, 59, 
	60, 61, 88, 62, 63, 64, 87, 64, 
	65, 84, 66, 67, 68, 83, 68, 69, 
	80, 70, 71, 72, 79, 73, 144, 74, 
	75, 76, 144, 74, 77, 78, 76, 77, 
	78, 76, 144, 74, 81, 71, 72, 82, 
	85, 67, 68, 86, 89, 63, 64, 90, 
	94, 95, 96, 97, 103, 98, 99, 100, 
	144, 101, 102, 100, 144, 101, 104, 105, 
	106, 107, 108, 109, 110, 111, 112, 113, 
	114, 115, 120, 116, 117, 144, 118, 119, 
	122, 123, 124, 125, 126, 127, 128, 129, 
	130, 131, 132, 133, 134, 135, 132, 133, 
	134, 135, 132, 135, 136, 137, 144, 138, 
	139, 140, 137, 144, 138, 139, 140, 137, 
	144, 138, 141, 142
};

static const char _multiple_atom_stmt_test_trans_actions_wi[] = {
	35, 0, 1, 0, 0, 0, 0, 0, 
	0, 21, 5, 0, 0, 0, 0, 0, 
	5, 23, 0, 0, 0, 0, 0, 0, 
	25, 5, 0, 0, 0, 0, 0, 27, 
	5, 0, 0, 0, 0, 0, 29, 5, 
	0, 67, 0, 0, 83, 114, 83, 13, 
	55, 0, 0, 15, 64, 102, 64, 0, 
	11, 52, 5, 0, 11, 49, 5, 0, 
	11, 46, 5, 41, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 21, 5, 
	0, 0, 0, 0, 0, 5, 23, 0, 
	0, 0, 0, 0, 0, 25, 5, 0, 
	0, 0, 0, 0, 27, 5, 0, 0, 
	0, 0, 0, 29, 5, 0, 71, 0, 
	0, 83, 121, 83, 13, 55, 0, 0, 
	15, 64, 108, 64, 0, 11, 52, 5, 
	0, 11, 49, 5, 0, 11, 46, 5, 
	0, 0, 0, 33, 0, 0, 0, 31, 
	87, 31, 5, 0, 43, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 5, 0, 0, 75, 0, 9, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 58, 13, 55, 58, 0, 0, 
	15, 0, 17, 17, 0, 61, 96, 61, 
	13, 55, 0, 79, 0, 0, 15, 19, 
	91, 19, 1, 0
};

static const char _multiple_atom_stmt_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 0, 
	3, 0, 0, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 3, 0, 0, 
	0, 3, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 3, 0, 7, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 37, 
	37
};

static const char _multiple_atom_stmt_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	39
};

static const char _multiple_atom_stmt_test_eof_actions[] = {
	0, 35, 35, 35, 35, 35, 35, 35, 
	35, 35, 35, 35, 35, 35, 35, 35, 
	35, 35, 35, 35, 35, 35, 35, 35, 
	35, 35, 35, 35, 35, 35, 35, 35, 
	35, 35, 35, 35, 35, 35, 35, 35, 
	35, 35, 35, 35, 35, 35, 35, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0
};

static const int multiple_atom_stmt_test_start = 143;
static const int multiple_atom_stmt_test_first_final = 143;
static const int multiple_atom_stmt_test_error = 0;

static const int multiple_atom_stmt_test_en_atom_stmt = 144;
static const int multiple_atom_stmt_test_en_main = 143;

#line 577 "NanorexMMPImportExportTest.rl"
	
#line 2614 "NanorexMMPImportExportTest.cpp"
	{
	cs = multiple_atom_stmt_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 578 "NanorexMMPImportExportTest.rl"
	
#line 2624 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 24:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 2645 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _multiple_atom_stmt_test_trans_keys + _multiple_atom_stmt_test_key_offsets[cs];
	_trans = _multiple_atom_stmt_test_index_offsets[cs];

	_klen = _multiple_atom_stmt_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _multiple_atom_stmt_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _multiple_atom_stmt_test_indicies[_trans];
	cs = _multiple_atom_stmt_test_trans_targs_wi[_trans];

	if ( _multiple_atom_stmt_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 551 "NanorexMMPImportExportTest.rl"
	{ //newAtom(atomId, atomicNum, x, y, z, atomStyle);
			// cerr << "calling, p = " << p << endl;
	         {stack[top++] = cs; cs = 144; goto _again;}}
	break;
	case 22:
#line 554 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
	case 25:
#line 532 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "atom_decl_line, p = " << p << endl;
		// newAtom(atomId, atomicNum, x, y, z, atomStyle);
	}}
	break;
	case 26:
#line 536 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "bond_line, p = " << p << endl;
		// newBond(stringVal, intVal);
	}}
	break;
	case 27:
#line 540 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "bond_direction_line, p = " << p << endl;
		// newBondDirection(intVal, intVal2);
	}}
	break;
	case 28:
#line 544 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "info_atom_line, p = " << p << endl;
		// newAtomInfo(stringVal, stringVal2);
	}}
	break;
	case 29:
#line 547 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
#line 2842 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 23:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
#line 2863 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 22:
#line 554 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
#line 2886 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 579 "NanorexMMPImportExportTest.rl"
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


#line 625 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::molLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 636 "NanorexMMPImportExportTest.rl"
	
#line 2943 "NanorexMMPImportExportTest.cpp"
static const char _mol_decl_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	8, 2, 0, 7, 2, 1, 2, 2, 
	1, 3, 2, 1, 4, 3, 4, 0, 
	7, 4, 1, 4, 0, 7
};

static const unsigned char _mol_decl_line_test_key_offsets[] = {
	0, 0, 5, 6, 7, 11, 16, 27, 
	41, 55, 60, 72, 74, 88, 102, 115, 
	129, 142, 156
};

static const char _mol_decl_line_test_trans_keys[] = {
	10, 32, 109, 9, 13, 111, 108, 9, 
	32, 11, 13, 9, 32, 40, 11, 13, 
	9, 32, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 41, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 9, 13, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 0
};

static const char _mol_decl_line_test_single_lengths[] = {
	0, 3, 1, 1, 2, 3, 3, 4, 
	4, 3, 4, 2, 4, 4, 3, 4, 
	3, 4, 0
};

static const char _mol_decl_line_test_range_lengths[] = {
	0, 1, 0, 0, 1, 1, 4, 5, 
	5, 1, 4, 0, 5, 5, 5, 5, 
	5, 5, 0
};

static const char _mol_decl_line_test_index_offsets[] = {
	0, 0, 5, 7, 9, 13, 18, 26, 
	36, 46, 51, 60, 63, 73, 83, 92, 
	102, 111, 121
};

static const char _mol_decl_line_test_indicies[] = {
	2, 1, 3, 1, 0, 4, 0, 5, 
	0, 6, 6, 6, 0, 6, 6, 7, 
	6, 0, 7, 7, 8, 7, 8, 8, 
	8, 0, 9, 9, 10, 12, 9, 11, 
	12, 12, 12, 0, 13, 13, 14, 16, 
	13, 15, 16, 16, 16, 0, 18, 17, 
	19, 17, 0, 18, 17, 19, 20, 17, 
	20, 20, 20, 0, 0, 18, 19, 22, 
	21, 23, 25, 21, 24, 25, 25, 25, 
	0, 18, 26, 19, 28, 26, 27, 28, 
	28, 28, 0, 27, 27, 28, 27, 27, 
	28, 28, 28, 0, 30, 29, 31, 28, 
	29, 27, 28, 28, 28, 0, 15, 15, 
	16, 15, 15, 16, 16, 16, 0, 32, 
	32, 33, 16, 32, 15, 16, 16, 16, 
	0, 0, 0
};

static const char _mol_decl_line_test_trans_targs_wi[] = {
	0, 1, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 16, 17, 8, 9, 16, 
	17, 10, 18, 11, 12, 13, 18, 11, 
	14, 15, 13, 14, 15, 13, 18, 11, 
	8, 9
};

static const char _mol_decl_line_test_trans_actions_wi[] = {
	15, 0, 1, 11, 0, 0, 0, 0, 
	0, 23, 23, 3, 20, 0, 0, 0, 
	5, 0, 17, 0, 0, 26, 33, 26, 
	3, 20, 0, 0, 5, 9, 29, 9, 
	7, 7
};

static const char _mol_decl_line_test_to_state_actions[] = {
	0, 0, 0, 0, 13, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0
};

static const char _mol_decl_line_test_eof_actions[] = {
	0, 15, 15, 15, 15, 15, 15, 15, 
	15, 15, 15, 15, 15, 15, 15, 15, 
	15, 15, 0
};

static const int mol_decl_line_test_start = 1;
static const int mol_decl_line_test_first_final = 18;
static const int mol_decl_line_test_error = 0;

static const int mol_decl_line_test_en_main = 1;

#line 637 "NanorexMMPImportExportTest.rl"
	
#line 3054 "NanorexMMPImportExportTest.cpp"
	{
	cs = mol_decl_line_test_start;
	}
#line 638 "NanorexMMPImportExportTest.rl"
	
#line 3060 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_keys = _mol_decl_line_test_trans_keys + _mol_decl_line_test_key_offsets[cs];
	_trans = _mol_decl_line_test_index_offsets[cs];

	_klen = _mol_decl_line_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _mol_decl_line_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _mol_decl_line_test_indicies[_trans];
	cs = _mol_decl_line_test_trans_targs_wi[_trans];

	if ( _mol_decl_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _mol_decl_line_test_actions + _mol_decl_line_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 1:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 9 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 7:
#line 16 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 8:
#line 621 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3177 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _mol_decl_line_test_actions + _mol_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 6:
#line 11 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
#line 3190 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _mol_decl_line_test_actions + _mol_decl_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 8:
#line 621 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3212 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 639 "NanorexMMPImportExportTest.rl"
}


void
NanorexMMPImportExportTest::newMolecule(string const& name, string const& style)
{
	++molCount;
	currentMolName = name;
	currentMolStyle = style;
}


void
NanorexMMPImportExportTest::newChunkInfo(string const& key,
                                         string const& value)
{
	++infoChunkCount;
	cerr << lineNum << ": info chunk " << key << " = " << value << endl;
	/// @todo
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


#line 757 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 770 "NanorexMMPImportExportTest.rl"
	
#line 3330 "NanorexMMPImportExportTest.cpp"
static const char _group_lines_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 5, 1, 6, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 11, 1, 
	12, 1, 13, 1, 14, 1, 17, 1, 
	18, 1, 21, 1, 22, 1, 28, 1, 
	30, 1, 32, 1, 33, 1, 37, 1, 
	38, 1, 40, 1, 54, 1, 55, 1, 
	62, 1, 63, 2, 0, 50, 2, 0, 
	52, 2, 0, 53, 2, 0, 61, 2, 
	5, 12, 2, 5, 13, 2, 5, 14, 
	2, 6, 7, 2, 6, 8, 2, 6, 
	9, 2, 8, 15, 2, 26, 28, 2, 
	35, 24, 2, 38, 39, 3, 0, 16, 
	48, 3, 0, 19, 51, 3, 0, 20, 
	49, 3, 0, 23, 46, 3, 0, 25, 
	47, 3, 0, 27, 58, 3, 0, 29, 
	43, 3, 0, 29, 60, 3, 0, 31, 
	59, 3, 0, 34, 45, 3, 0, 34, 
	57, 3, 0, 36, 44, 3, 6, 8, 
	15, 3, 17, 0, 50, 3, 41, 0, 
	42, 3, 41, 0, 56, 4, 9, 0, 
	20, 49, 4, 9, 0, 23, 46, 4, 
	9, 0, 25, 47, 4, 9, 0, 29, 
	43, 4, 9, 0, 29, 60, 4, 9, 
	0, 36, 44, 4, 33, 0, 34, 45, 
	4, 33, 0, 34, 57, 5, 6, 9, 
	0, 20, 49, 5, 6, 9, 0, 23, 
	46, 5, 6, 9, 0, 25, 47, 5, 
	6, 9, 0, 29, 43, 5, 6, 9, 
	0, 29, 60, 5, 6, 9, 0, 36, 
	44, 5, 8, 15, 0, 16, 48, 6, 
	6, 8, 15, 0, 16, 48
};

static const short _group_lines_test_key_offsets[] = {
	0, 0, 2, 13, 16, 19, 22, 27, 
	34, 41, 47, 54, 62, 68, 73, 79, 
	88, 92, 100, 106, 115, 119, 127, 133, 
	142, 146, 154, 160, 166, 179, 181, 196, 
	211, 225, 240, 248, 252, 260, 268, 276, 
	280, 288, 296, 304, 308, 316, 324, 332, 
	339, 342, 345, 348, 356, 361, 368, 376, 
	384, 386, 394, 397, 400, 403, 406, 409, 
	412, 415, 418, 421, 426, 433, 440, 447, 
	455, 461, 463, 471, 478, 481, 484, 487, 
	490, 493, 500, 507, 509, 522, 534, 549, 
	564, 570, 584, 599, 602, 605, 608, 611, 
	617, 623, 635, 650, 665, 671, 684, 686, 
	701, 716, 730, 745, 759, 774, 777, 780, 
	783, 788, 796, 799, 802, 805, 810, 822, 
	837, 852, 866, 881, 893, 908, 923, 925, 
	939, 954, 957, 960, 963, 966, 971, 983, 
	998, 1013, 1027, 1042, 1054, 1069, 1084, 1086, 
	1100, 1115, 1118, 1121, 1124, 1127, 1130, 1133, 
	1136, 1139, 1144, 1156, 1171, 1186, 1200, 1215, 
	1227, 1242, 1257, 1259, 1273, 1288, 1291, 1294, 
	1299, 1305, 1317, 1332, 1347, 1353, 1366, 1368, 
	1383, 1398, 1412, 1427, 1441, 1456, 1458, 1460, 
	1467, 1470, 1473, 1476, 1479, 1482, 1489, 1496, 
	1498, 1511, 1523, 1538, 1553, 1559, 1573, 1588, 
	1591, 1594, 1597, 1600, 1606, 1612, 1626, 1641, 
	1656, 1662, 1675, 1677, 1692, 1707, 1721, 1736, 
	1750, 1765, 1781, 1797, 1813, 1829, 1845, 1861, 
	1877, 1893, 1908, 1923, 1929, 1942, 1944, 1960, 
	1976, 1992, 2007, 2023, 2039, 2055, 2071, 2086, 
	2101, 2107, 2109, 2109, 2109, 2121, 2132, 2139
};

static const char _group_lines_test_trans_keys[] = {
	-1, 10, -1, 10, 32, 97, 98, 101, 
	103, 105, 109, 9, 13, -1, 10, 116, 
	-1, 10, 111, -1, 10, 109, -1, 10, 
	32, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 40, 9, 13, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 9, 
	13, -1, 10, 32, 40, 9, 13, -1, 
	10, 32, 43, 45, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, -1, 10, 32, 
	43, 45, 9, 13, 48, 57, -1, 10, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 111, -1, 10, 
	110, -1, 10, 100, -1, 10, 95, 97, 
	99, 103, 49, 51, -1, 10, 32, 9, 
	13, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, -1, 10, 32, 35, 9, 13, 
	48, 57, -1, 10, 100, -1, 10, 105, 
	-1, 10, 114, -1, 10, 101, -1, 10, 
	99, -1, 10, 116, -1, 10, 105, -1, 
	10, 111, -1, 10, 110, -1, 10, 32, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 35, 9, 13, 48, 57, -1, 
	10, 32, 35, 9, 13, -1, 10, -1, 
	10, 32, 35, 9, 13, 48, 57, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	103, -1, 10, 114, -1, 10, 111, -1, 
	10, 117, -1, 10, 112, -1, 10, 32, 
	35, 40, 9, 13, -1, 10, 32, 35, 
	40, 9, 13, -1, 10, -1, 10, 32, 
	41, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	9, 13, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 114, -1, 10, 111, -1, 10, 117, 
	-1, 10, 112, -1, 10, 32, 40, 9, 
	13, -1, 10, 32, 40, 9, 13, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	110, -1, 10, 102, -1, 10, 111, -1, 
	10, 32, 9, 13, -1, 10, 32, 97, 
	99, 111, 9, 13, -1, 10, 116, -1, 
	10, 111, -1, 10, 109, -1, 10, 32, 
	9, 13, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 61, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 61, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 104, -1, 10, 117, 
	-1, 10, 110, -1, 10, 107, -1, 10, 
	32, 9, 13, -1, 10, 32, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 61, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 112, -1, 10, 
	101, -1, 10, 110, -1, 10, 103, -1, 
	10, 114, -1, 10, 111, -1, 10, 117, 
	-1, 10, 112, -1, 10, 32, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 111, -1, 10, 108, -1, 10, 
	32, 9, 13, -1, 10, 32, 40, 9, 
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, -1, 10, 32, 101, 
	103, 9, 13, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 35, 40, 9, 
	13, -1, 10, 32, 35, 40, 9, 13, 
	-1, 10, -1, 10, 32, 41, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 67, 
	86, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 108, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 105, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 112, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 98, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 111, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 97, 9, 13, 45, 46, 48, 
	57, 65, 90, 98, 122, -1, 10, 32, 
	41, 95, 114, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 100, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 41, 95, 105, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 101, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 119, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 68, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 97, 9, 13, 45, 
	46, 48, 57, 65, 90, 98, 122, -1, 
	10, 32, 41, 95, 116, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 97, 9, 13, 45, 
	46, 48, 57, 65, 90, 98, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 9, 13, -1, 10, -1, 10, 32, 
	35, 97, 98, 101, 103, 105, 109, 9, 
	13, -1, 10, 32, 97, 98, 101, 103, 
	105, 109, 9, 13, -1, 10, 32, 101, 
	103, 9, 13, -1, 10, 32, 101, 103, 
	9, 13, 0
};

static const char _group_lines_test_single_lengths[] = {
	0, 2, 9, 3, 3, 3, 3, 3, 
	3, 4, 3, 4, 4, 3, 4, 5, 
	2, 4, 4, 5, 2, 4, 4, 5, 
	2, 4, 4, 4, 5, 2, 5, 5, 
	4, 5, 4, 2, 4, 4, 4, 2, 
	4, 4, 4, 2, 4, 4, 4, 3, 
	3, 3, 3, 6, 3, 3, 4, 4, 
	2, 4, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 4, 
	4, 2, 4, 3, 3, 3, 3, 3, 
	3, 5, 5, 2, 5, 4, 5, 5, 
	4, 4, 5, 3, 3, 3, 3, 4, 
	4, 4, 5, 5, 4, 5, 2, 5, 
	5, 4, 5, 4, 5, 3, 3, 3, 
	3, 6, 3, 3, 3, 3, 4, 5, 
	5, 4, 5, 4, 5, 5, 2, 4, 
	5, 3, 3, 3, 3, 3, 4, 5, 
	5, 4, 5, 4, 5, 5, 2, 4, 
	5, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 4, 5, 5, 4, 5, 4, 
	5, 5, 2, 4, 5, 3, 3, 3, 
	4, 4, 5, 5, 4, 5, 2, 5, 
	5, 4, 5, 4, 5, 2, 2, 5, 
	3, 3, 3, 3, 3, 5, 5, 2, 
	5, 4, 5, 5, 4, 4, 5, 3, 
	3, 3, 3, 4, 4, 6, 5, 5, 
	4, 5, 2, 5, 5, 4, 5, 4, 
	5, 6, 6, 6, 6, 6, 6, 6, 
	6, 5, 5, 4, 5, 2, 6, 6, 
	6, 5, 6, 6, 6, 6, 5, 5, 
	4, 2, 0, 0, 10, 9, 5, 5
};

static const char _group_lines_test_range_lengths[] = {
	0, 0, 1, 0, 0, 0, 1, 2, 
	2, 1, 2, 2, 1, 1, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 1, 4, 0, 5, 5, 
	5, 5, 2, 1, 2, 2, 2, 1, 
	2, 2, 2, 1, 2, 2, 2, 2, 
	0, 0, 0, 1, 1, 2, 2, 2, 
	0, 2, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 2, 2, 2, 2, 
	1, 0, 2, 2, 0, 0, 0, 0, 
	0, 1, 1, 0, 4, 4, 5, 5, 
	1, 5, 5, 0, 0, 0, 0, 1, 
	1, 4, 5, 5, 1, 4, 0, 5, 
	5, 5, 5, 5, 5, 0, 0, 0, 
	1, 1, 0, 0, 0, 1, 4, 5, 
	5, 5, 5, 4, 5, 5, 0, 5, 
	5, 0, 0, 0, 0, 1, 4, 5, 
	5, 5, 5, 4, 5, 5, 0, 5, 
	5, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 4, 5, 5, 5, 5, 4, 
	5, 5, 0, 5, 5, 0, 0, 1, 
	1, 4, 5, 5, 1, 4, 0, 5, 
	5, 5, 5, 5, 5, 0, 0, 1, 
	0, 0, 0, 0, 0, 1, 1, 0, 
	4, 4, 5, 5, 1, 5, 5, 0, 
	0, 0, 0, 1, 1, 4, 5, 5, 
	1, 4, 0, 5, 5, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 5, 5, 
	5, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 5, 5, 5, 5, 
	1, 0, 0, 0, 1, 1, 1, 1
};

static const short _group_lines_test_index_offsets[] = {
	0, 0, 3, 14, 18, 22, 26, 31, 
	37, 43, 49, 55, 62, 68, 73, 79, 
	87, 91, 98, 104, 112, 116, 123, 129, 
	137, 141, 148, 154, 160, 170, 173, 184, 
	195, 205, 216, 223, 227, 234, 241, 248, 
	252, 259, 266, 273, 277, 284, 291, 298, 
	304, 308, 312, 316, 324, 329, 335, 342, 
	349, 352, 359, 363, 367, 371, 375, 379, 
	383, 387, 391, 395, 400, 406, 412, 418, 
	425, 431, 434, 441, 447, 451, 455, 459, 
	463, 467, 474, 481, 484, 494, 503, 514, 
	525, 531, 541, 552, 556, 560, 564, 568, 
	574, 580, 589, 600, 611, 617, 627, 630, 
	641, 652, 662, 673, 683, 694, 698, 702, 
	706, 711, 719, 723, 727, 731, 736, 745, 
	756, 767, 777, 788, 797, 808, 819, 822, 
	832, 843, 847, 851, 855, 859, 864, 873, 
	884, 895, 905, 916, 925, 936, 947, 950, 
	960, 971, 975, 979, 983, 987, 991, 995, 
	999, 1003, 1008, 1017, 1028, 1039, 1049, 1060, 
	1069, 1080, 1091, 1094, 1104, 1115, 1119, 1123, 
	1128, 1134, 1143, 1154, 1165, 1171, 1181, 1184, 
	1195, 1206, 1216, 1227, 1237, 1248, 1251, 1254, 
	1261, 1265, 1269, 1273, 1277, 1281, 1288, 1295, 
	1298, 1308, 1317, 1328, 1339, 1345, 1355, 1366, 
	1370, 1374, 1378, 1382, 1388, 1394, 1405, 1416, 
	1427, 1433, 1443, 1446, 1457, 1468, 1478, 1489, 
	1499, 1510, 1522, 1534, 1546, 1558, 1570, 1582, 
	1594, 1606, 1617, 1628, 1634, 1644, 1647, 1659, 
	1671, 1683, 1694, 1706, 1718, 1730, 1742, 1753, 
	1764, 1770, 1773, 1774, 1775, 1787, 1798, 1805
};

static const unsigned char _group_lines_test_trans_targs_wi[] = {
	244, 244, 1, 244, 245, 2, 3, 48, 
	76, 91, 109, 165, 2, 1, 244, 244, 
	4, 1, 244, 244, 5, 1, 244, 244, 
	6, 1, 244, 244, 7, 7, 1, 244, 
	244, 7, 7, 8, 1, 244, 244, 9, 
	9, 47, 1, 244, 244, 9, 10, 9, 
	1, 244, 244, 10, 10, 11, 1, 244, 
	244, 12, 13, 12, 46, 1, 244, 244, 
	12, 13, 12, 1, 244, 244, 14, 14, 
	1, 244, 244, 14, 15, 14, 1, 244, 
	244, 15, 16, 43, 15, 17, 1, 244, 
	244, 17, 1, 244, 244, 18, 19, 18, 
	42, 1, 244, 244, 18, 19, 18, 1, 
	244, 244, 19, 20, 39, 19, 21, 1, 
	244, 244, 21, 1, 244, 244, 22, 23, 
	22, 38, 1, 244, 244, 22, 23, 22, 
	1, 244, 244, 23, 24, 35, 23, 25, 
	1, 244, 244, 25, 1, 244, 244, 26, 
	27, 26, 34, 1, 244, 244, 26, 27, 
	26, 1, 244, 244, 28, 29, 28, 1, 
	244, 244, 28, 29, 30, 28, 30, 30, 
	30, 1, 244, 244, 29, 244, 244, 31, 
	29, 33, 31, 32, 33, 33, 33, 1, 
	244, 244, 31, 29, 33, 31, 32, 33, 
	33, 33, 1, 244, 244, 32, 33, 32, 
	32, 33, 33, 33, 1, 244, 244, 31, 
	29, 33, 31, 32, 33, 33, 33, 1, 
	244, 244, 26, 27, 26, 34, 1, 244, 
	244, 36, 1, 244, 244, 26, 27, 26, 
	37, 1, 244, 244, 26, 27, 26, 37, 
	1, 244, 244, 22, 23, 22, 38, 1, 
	244, 244, 40, 1, 244, 244, 22, 23, 
	22, 41, 1, 244, 244, 22, 23, 22, 
	41, 1, 244, 244, 18, 19, 18, 42, 
	1, 244, 244, 44, 1, 244, 244, 18, 
	19, 18, 45, 1, 244, 244, 18, 19, 
	18, 45, 1, 244, 244, 12, 13, 12, 
	46, 1, 244, 244, 9, 9, 47, 1, 
	244, 244, 49, 1, 244, 244, 50, 1, 
	244, 244, 51, 1, 244, 244, 58, 52, 
	52, 52, 52, 1, 244, 244, 53, 53, 
	1, 244, 244, 53, 53, 54, 1, 244, 
	244, 55, 56, 55, 57, 1, 244, 244, 
	55, 56, 55, 54, 1, 244, 244, 56, 
	244, 244, 55, 56, 55, 57, 1, 244, 
	244, 59, 1, 244, 244, 60, 1, 244, 
	244, 61, 1, 244, 244, 62, 1, 244, 
	244, 63, 1, 244, 244, 64, 1, 244, 
	244, 65, 1, 244, 244, 66, 1, 244, 
	244, 67, 1, 244, 244, 68, 68, 1, 
	244, 244, 68, 68, 69, 1, 244, 244, 
	70, 70, 75, 1, 244, 244, 70, 70, 
	71, 1, 244, 244, 72, 73, 72, 74, 
	1, 244, 244, 72, 73, 72, 1, 244, 
	244, 73, 244, 244, 72, 73, 72, 74, 
	1, 244, 244, 70, 70, 75, 1, 244, 
	244, 77, 1, 244, 244, 78, 1, 244, 
	244, 79, 1, 244, 244, 80, 1, 244, 
	244, 81, 1, 244, 244, 82, 83, 84, 
	82, 1, 244, 244, 82, 83, 84, 82, 
	1, 244, 244, 83, 244, 244, 85, 88, 
	86, 85, 86, 86, 86, 1, 244, 244, 
	85, 86, 85, 86, 86, 86, 1, 244, 
	244, 87, 88, 90, 87, 89, 90, 90, 
	90, 1, 244, 244, 87, 88, 90, 87, 
	89, 90, 90, 90, 1, 244, 244, 88, 
	83, 88, 1, 244, 244, 89, 90, 89, 
	89, 90, 90, 90, 1, 244, 244, 87, 
	88, 90, 87, 89, 90, 90, 90, 1, 
	244, 244, 92, 1, 244, 244, 93, 1, 
	244, 244, 94, 1, 244, 244, 95, 1, 
	244, 244, 96, 97, 96, 1, 244, 244, 
	96, 97, 96, 1, 244, 244, 97, 98, 
	97, 98, 98, 98, 1, 244, 244, 99, 
	100, 108, 99, 107, 108, 108, 108, 1, 
	244, 244, 99, 100, 108, 99, 107, 108, 
	108, 108, 1, 244, 244, 101, 102, 101, 
	1, 244, 244, 101, 102, 103, 101, 103, 
	103, 103, 1, 244, 244, 102, 244, 244, 
	104, 102, 106, 104, 105, 106, 106, 106, 
	1, 244, 244, 104, 102, 106, 104, 105, 
	106, 106, 106, 1, 244, 244, 105, 106, 
	105, 105, 106, 106, 106, 1, 244, 244, 
	104, 102, 106, 104, 105, 106, 106, 106, 
	1, 244, 244, 107, 108, 107, 107, 108, 
	108, 108, 1, 244, 244, 99, 100, 108, 
	99, 107, 108, 108, 108, 1, 244, 244, 
	110, 1, 244, 244, 111, 1, 244, 244, 
	112, 1, 244, 244, 113, 113, 1, 244, 
	244, 113, 114, 129, 145, 113, 1, 244, 
	244, 115, 1, 244, 244, 116, 1, 244, 
	244, 117, 1, 244, 244, 118, 118, 1, 
	244, 244, 118, 119, 118, 119, 119, 119, 
	1, 244, 244, 120, 123, 122, 120, 121, 
	122, 122, 122, 1, 244, 244, 120, 123, 
	122, 120, 121, 122, 122, 122, 1, 244, 
	244, 121, 122, 121, 121, 122, 122, 122, 
	1, 244, 244, 120, 123, 122, 120, 121, 
	122, 122, 122, 1, 244, 244, 123, 124, 
	123, 124, 124, 124, 1, 244, 244, 125, 
	126, 128, 125, 127, 128, 128, 128, 1, 
	244, 244, 125, 126, 128, 125, 127, 128, 
	128, 128, 1, 244, 244, 126, 244, 244, 
	127, 128, 127, 127, 128, 128, 128, 1, 
	244, 244, 125, 126, 128, 125, 127, 128, 
	128, 128, 1, 244, 244, 130, 1, 244, 
	244, 131, 1, 244, 244, 132, 1, 244, 
	244, 133, 1, 244, 244, 134, 134, 1, 
	244, 244, 134, 135, 134, 135, 135, 135, 
	1, 244, 244, 136, 139, 138, 136, 137, 
	138, 138, 138, 1, 244, 244, 136, 139, 
	138, 136, 137, 138, 138, 138, 1, 244, 
	244, 137, 138, 137, 137, 138, 138, 138, 
	1, 244, 244, 136, 139, 138, 136, 137, 
	138, 138, 138, 1, 244, 244, 139, 140, 
	139, 140, 140, 140, 1, 244, 244, 141, 
	142, 144, 141, 143, 144, 144, 144, 1, 
	244, 244, 141, 142, 144, 141, 143, 144, 
	144, 144, 1, 244, 244, 142, 244, 244, 
	143, 144, 143, 143, 144, 144, 144, 1, 
	244, 244, 141, 142, 144, 141, 143, 144, 
	144, 144, 1, 244, 244, 146, 1, 244, 
	244, 147, 1, 244, 244, 148, 1, 244, 
	244, 149, 1, 244, 244, 150, 1, 244, 
	244, 151, 1, 244, 244, 152, 1, 244, 
	244, 153, 1, 244, 244, 154, 154, 1, 
	244, 244, 154, 155, 154, 155, 155, 155, 
	1, 244, 244, 156, 159, 158, 156, 157, 
	158, 158, 158, 1, 244, 244, 156, 159, 
	158, 156, 157, 158, 158, 158, 1, 244, 
	244, 157, 158, 157, 157, 158, 158, 158, 
	1, 244, 244, 156, 159, 158, 156, 157, 
	158, 158, 158, 1, 244, 244, 159, 160, 
	159, 160, 160, 160, 1, 244, 244, 161, 
	162, 164, 161, 163, 164, 164, 164, 1, 
	244, 244, 161, 162, 164, 161, 163, 164, 
	164, 164, 1, 244, 244, 162, 244, 244, 
	163, 164, 163, 163, 164, 164, 164, 1, 
	244, 244, 161, 162, 164, 161, 163, 164, 
	164, 164, 1, 244, 244, 166, 1, 244, 
	244, 167, 1, 244, 244, 168, 168, 1, 
	244, 244, 168, 169, 168, 1, 244, 244, 
	169, 170, 169, 170, 170, 170, 1, 244, 
	244, 171, 172, 180, 171, 179, 180, 180, 
	180, 1, 244, 244, 171, 172, 180, 171, 
	179, 180, 180, 180, 1, 244, 244, 173, 
	174, 173, 1, 244, 244, 173, 174, 175, 
	173, 175, 175, 175, 1, 244, 244, 174, 
	244, 244, 176, 174, 178, 176, 177, 178, 
	178, 178, 1, 244, 244, 176, 174, 178, 
	176, 177, 178, 178, 178, 1, 244, 244, 
	177, 178, 177, 177, 178, 178, 178, 1, 
	244, 244, 176, 174, 178, 176, 177, 178, 
	178, 178, 1, 244, 244, 179, 180, 179, 
	179, 180, 180, 180, 1, 244, 244, 171, 
	172, 180, 171, 179, 180, 180, 180, 1, 
	0, 244, 181, 246, 246, 182, 246, 247, 
	183, 184, 199, 183, 182, 246, 246, 185, 
	182, 246, 246, 186, 182, 246, 246, 187, 
	182, 246, 246, 188, 182, 246, 246, 189, 
	182, 246, 246, 190, 191, 192, 190, 182, 
	246, 246, 190, 191, 192, 190, 182, 246, 
	246, 191, 246, 246, 193, 196, 194, 193, 
	194, 194, 194, 182, 246, 246, 193, 194, 
	193, 194, 194, 194, 182, 246, 246, 195, 
	196, 198, 195, 197, 198, 198, 198, 182, 
	246, 246, 195, 196, 198, 195, 197, 198, 
	198, 198, 182, 246, 246, 196, 191, 196, 
	182, 246, 246, 197, 198, 197, 197, 198, 
	198, 198, 182, 246, 246, 195, 196, 198, 
	195, 197, 198, 198, 198, 182, 246, 246, 
	200, 182, 246, 246, 201, 182, 246, 246, 
	202, 182, 246, 246, 203, 182, 246, 246, 
	204, 205, 204, 182, 246, 246, 204, 205, 
	204, 182, 246, 246, 205, 217, 230, 206, 
	205, 206, 206, 206, 182, 246, 246, 207, 
	208, 216, 207, 215, 216, 216, 216, 182, 
	246, 246, 207, 208, 216, 207, 215, 216, 
	216, 216, 182, 246, 246, 209, 210, 209, 
	182, 246, 246, 209, 210, 211, 209, 211, 
	211, 211, 182, 246, 246, 210, 246, 246, 
	212, 210, 214, 212, 213, 214, 214, 214, 
	182, 246, 246, 212, 210, 214, 212, 213, 
	214, 214, 214, 182, 246, 246, 213, 214, 
	213, 213, 214, 214, 214, 182, 246, 246, 
	212, 210, 214, 212, 213, 214, 214, 214, 
	182, 246, 246, 215, 216, 215, 215, 216, 
	216, 216, 182, 246, 246, 207, 208, 216, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	207, 208, 216, 218, 207, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 219, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	207, 208, 216, 220, 207, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 221, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	207, 208, 216, 222, 207, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 223, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	207, 208, 216, 224, 207, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 225, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	226, 227, 216, 226, 215, 216, 216, 216, 
	182, 246, 246, 226, 227, 216, 226, 215, 
	216, 216, 216, 182, 246, 246, 228, 229, 
	228, 182, 246, 246, 228, 229, 211, 228, 
	211, 211, 211, 182, 246, 246, 229, 246, 
	246, 207, 208, 216, 231, 207, 215, 216, 
	216, 216, 182, 246, 246, 207, 208, 216, 
	232, 207, 215, 216, 216, 216, 182, 246, 
	246, 207, 208, 216, 233, 207, 215, 216, 
	216, 216, 182, 246, 246, 234, 208, 216, 
	234, 215, 216, 216, 216, 182, 246, 246, 
	234, 208, 235, 216, 234, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 236, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	207, 208, 216, 237, 207, 215, 216, 216, 
	216, 182, 246, 246, 207, 208, 216, 238, 
	207, 215, 216, 216, 216, 182, 246, 246, 
	239, 240, 216, 239, 215, 216, 216, 216, 
	182, 246, 246, 239, 240, 216, 239, 215, 
	216, 216, 216, 182, 246, 246, 209, 241, 
	209, 182, 246, 246, 241, 243, 243, 0, 
	245, 2, 181, 3, 48, 76, 91, 109, 
	165, 2, 1, 244, 245, 2, 3, 48, 
	76, 91, 109, 165, 2, 1, 0, 247, 
	183, 184, 199, 183, 182, 246, 247, 183, 
	184, 199, 183, 182, 0
};

static const unsigned char _group_lines_test_trans_actions_wi[] = {
	53, 65, 0, 53, 157, 0, 0, 0, 
	41, 0, 95, 33, 0, 0, 53, 65, 
	0, 0, 53, 65, 0, 0, 53, 65, 
	0, 0, 53, 65, 0, 0, 0, 53, 
	65, 0, 0, 0, 0, 53, 65, 19, 
	19, 3, 0, 53, 65, 0, 0, 0, 
	0, 53, 65, 0, 0, 0, 0, 53, 
	65, 0, 0, 0, 3, 0, 53, 65, 
	0, 0, 0, 0, 53, 65, 21, 21, 
	0, 53, 65, 0, 0, 0, 0, 53, 
	65, 0, 0, 0, 0, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 23, 0, 
	3, 0, 53, 65, 0, 23, 0, 0, 
	53, 65, 0, 0, 0, 0, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 25, 
	0, 3, 0, 53, 65, 0, 25, 0, 
	0, 53, 65, 0, 0, 0, 0, 0, 
	0, 53, 65, 0, 0, 53, 65, 0, 
	27, 0, 3, 0, 53, 65, 0, 27, 
	0, 0, 53, 101, 0, 0, 0, 0, 
	53, 101, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 101, 0, 53, 247, 149, 
	149, 80, 149, 11, 80, 80, 80, 0, 
	53, 101, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 241, 89, 
	89, 13, 89, 0, 13, 13, 13, 0, 
	53, 65, 0, 27, 0, 3, 0, 53, 
	65, 0, 0, 53, 65, 9, 77, 9, 
	3, 0, 53, 65, 9, 77, 9, 3, 
	0, 53, 65, 0, 25, 0, 3, 0, 
	53, 65, 0, 0, 53, 65, 9, 74, 
	9, 3, 0, 53, 65, 9, 74, 9, 
	3, 0, 53, 65, 0, 23, 0, 3, 
	0, 53, 65, 0, 0, 53, 65, 9, 
	71, 9, 3, 0, 53, 65, 9, 71, 
	9, 3, 0, 53, 65, 0, 0, 0, 
	3, 0, 53, 65, 19, 19, 3, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 31, 
	31, 31, 31, 0, 53, 65, 0, 0, 
	0, 53, 65, 0, 0, 0, 0, 53, 
	153, 29, 29, 29, 3, 0, 53, 59, 
	0, 0, 0, 0, 0, 53, 59, 0, 
	53, 153, 29, 29, 29, 3, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 53, 65, 
	0, 0, 3, 0, 53, 65, 0, 0, 
	0, 0, 53, 105, 0, 0, 0, 7, 
	0, 53, 105, 0, 0, 0, 0, 53, 
	105, 0, 53, 105, 0, 0, 0, 7, 
	0, 53, 65, 0, 0, 3, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 195, 43, 43, 43, 
	43, 0, 53, 137, 0, 0, 0, 0, 
	0, 53, 137, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 0, 53, 65, 
	0, 0, 0, 0, 0, 0, 0, 53, 
	65, 83, 83, 80, 83, 11, 80, 80, 
	80, 0, 53, 65, 0, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 137, 0, 
	0, 0, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 65, 15, 
	15, 13, 15, 0, 13, 13, 13, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 37, 37, 37, 0, 53, 65, 
	0, 0, 0, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 53, 65, 83, 
	83, 80, 83, 11, 80, 80, 80, 0, 
	53, 65, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 125, 0, 0, 0, 
	0, 53, 125, 0, 0, 0, 0, 0, 
	0, 0, 0, 53, 125, 0, 53, 223, 
	86, 86, 80, 86, 11, 80, 80, 80, 
	0, 53, 125, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 53, 65, 0, 13, 
	0, 0, 13, 13, 13, 0, 53, 180, 
	17, 17, 13, 17, 0, 13, 13, 13, 
	0, 53, 65, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 65, 15, 15, 13, 
	15, 0, 13, 13, 13, 0, 53, 65, 
	0, 0, 53, 65, 0, 0, 53, 65, 
	0, 0, 53, 65, 0, 0, 0, 53, 
	65, 0, 0, 0, 0, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 0, 0, 
	0, 53, 65, 83, 83, 80, 83, 11, 
	80, 80, 80, 0, 53, 65, 0, 0, 
	13, 0, 0, 13, 13, 13, 0, 53, 
	65, 0, 13, 0, 0, 13, 13, 13, 
	0, 53, 65, 15, 15, 13, 15, 0, 
	13, 13, 13, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 53, 205, 86, 
	86, 80, 86, 11, 80, 80, 80, 0, 
	53, 109, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 109, 0, 53, 65, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 165, 17, 17, 13, 17, 0, 13, 
	13, 13, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 0, 0, 
	0, 53, 65, 83, 83, 80, 83, 11, 
	80, 80, 80, 0, 53, 65, 0, 0, 
	13, 0, 0, 13, 13, 13, 0, 53, 
	65, 0, 13, 0, 0, 13, 13, 13, 
	0, 53, 65, 15, 15, 13, 15, 0, 
	13, 13, 13, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 53, 217, 86, 
	86, 80, 86, 11, 80, 80, 80, 0, 
	53, 117, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 117, 0, 53, 65, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 175, 17, 17, 13, 17, 0, 13, 
	13, 13, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 0, 0, 
	0, 53, 65, 83, 83, 80, 83, 11, 
	80, 80, 80, 0, 53, 65, 0, 0, 
	13, 0, 0, 13, 13, 13, 0, 53, 
	65, 0, 13, 0, 0, 13, 13, 13, 
	0, 53, 65, 15, 15, 13, 15, 0, 
	13, 13, 13, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 53, 235, 86, 
	86, 80, 86, 11, 80, 80, 80, 0, 
	53, 145, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 145, 0, 53, 65, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 190, 17, 17, 13, 17, 0, 13, 
	13, 13, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 53, 65, 
	0, 0, 0, 0, 0, 0, 0, 53, 
	65, 83, 83, 80, 83, 11, 80, 80, 
	80, 0, 53, 65, 0, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 113, 0, 
	0, 0, 0, 53, 113, 0, 0, 0, 
	0, 0, 0, 0, 0, 53, 113, 0, 
	53, 211, 86, 86, 80, 86, 11, 80, 
	80, 80, 0, 53, 113, 0, 0, 13, 
	0, 0, 13, 13, 13, 0, 53, 65, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 170, 17, 17, 13, 17, 0, 13, 
	13, 13, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 65, 15, 
	15, 13, 15, 0, 13, 13, 13, 0, 
	0, 62, 0, 57, 68, 0, 57, 161, 
	0, 41, 39, 0, 0, 57, 68, 0, 
	0, 57, 68, 0, 0, 57, 68, 0, 
	0, 57, 68, 0, 0, 57, 68, 0, 
	0, 57, 200, 43, 43, 43, 43, 0, 
	57, 141, 0, 0, 0, 0, 0, 57, 
	141, 0, 57, 68, 0, 0, 0, 0, 
	0, 0, 0, 0, 57, 68, 0, 0, 
	0, 0, 0, 0, 0, 57, 68, 83, 
	83, 80, 83, 11, 80, 80, 80, 0, 
	57, 68, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 57, 141, 0, 0, 0, 
	0, 57, 68, 0, 13, 0, 0, 13, 
	13, 13, 0, 57, 68, 15, 15, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	0, 0, 57, 68, 0, 0, 57, 68, 
	0, 0, 57, 68, 0, 0, 57, 68, 
	92, 92, 92, 0, 57, 68, 0, 0, 
	0, 0, 57, 68, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 57, 68, 83, 
	83, 80, 83, 11, 80, 80, 80, 0, 
	57, 68, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 57, 129, 0, 0, 0, 
	0, 57, 129, 0, 0, 0, 0, 0, 
	0, 0, 0, 57, 129, 0, 57, 229, 
	86, 86, 80, 86, 11, 80, 80, 80, 
	0, 57, 129, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 57, 68, 0, 13, 
	0, 0, 13, 13, 13, 0, 57, 185, 
	17, 17, 13, 17, 0, 13, 13, 13, 
	0, 57, 68, 0, 13, 0, 0, 13, 
	13, 13, 0, 57, 68, 15, 15, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	83, 83, 80, 80, 83, 11, 80, 80, 
	80, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 13, 15, 0, 13, 13, 
	13, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 13, 15, 0, 13, 13, 
	13, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 13, 15, 0, 13, 13, 
	13, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 15, 0, 13, 13, 13, 
	0, 57, 68, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 57, 133, 0, 0, 
	0, 0, 57, 133, 0, 0, 0, 0, 
	0, 0, 0, 0, 57, 133, 0, 57, 
	68, 83, 83, 80, 80, 83, 11, 80, 
	80, 80, 0, 57, 68, 15, 15, 13, 
	13, 15, 0, 13, 13, 13, 0, 57, 
	68, 15, 15, 13, 13, 15, 0, 13, 
	13, 13, 0, 57, 68, 15, 15, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	0, 0, 13, 13, 0, 0, 13, 13, 
	13, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 13, 15, 0, 13, 13, 
	13, 0, 57, 68, 15, 15, 13, 13, 
	15, 0, 13, 13, 13, 0, 57, 68, 
	15, 15, 13, 15, 0, 13, 13, 13, 
	0, 57, 68, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 57, 121, 0, 0, 
	0, 0, 57, 121, 0, 45, 0, 0, 
	157, 0, 0, 0, 0, 41, 0, 95, 
	33, 0, 0, 51, 157, 0, 0, 0, 
	41, 0, 95, 33, 0, 0, 0, 161, 
	0, 41, 39, 0, 0, 55, 161, 0, 
	41, 39, 0, 0, 0
};

static const unsigned char _group_lines_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 0, 0, 1, 0, 0, 0, 0, 
	0, 1, 0, 0, 0, 1, 0, 0, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	1, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 1, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 0, 5, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 35, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 47, 47, 98, 0, 98, 0
};

static const unsigned char _group_lines_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 49, 0, 49, 0
};

static const unsigned char _group_lines_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 45, 0, 0, 0, 0, 0
};

static const short _group_lines_test_eof_trans[] = {
	0, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 0, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 299, 299, 299, 299, 299, 299, 
	299, 299, 0, 0, 0, 399, 0, 400
};

static const int group_lines_test_start = 242;
static const int group_lines_test_first_final = 242;
static const int group_lines_test_error = 0;

static const int group_lines_test_en_group_scanner = 244;
static const int group_lines_test_en_mini_group_scanner = 246;
static const int group_lines_test_en_main = 242;

#line 771 "NanorexMMPImportExportTest.rl"
	
#line 4380 "NanorexMMPImportExportTest.cpp"
	{
	cs = group_lines_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 772 "NanorexMMPImportExportTest.rl"
	
#line 4390 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _group_lines_test_actions + _group_lines_test_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 40:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 4411 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _group_lines_test_trans_keys + _group_lines_test_key_offsets[cs];
	_trans = _group_lines_test_index_offsets[cs];

	_klen = _group_lines_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _group_lines_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
_eof_trans:
	cs = _group_lines_test_trans_targs_wi[_trans];

	if ( _group_lines_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _group_lines_test_actions + _group_lines_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 51 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 31:
#line 56 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 32:
#line 60 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 33:
#line 61 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 34:
#line 67 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 35:
#line 71 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 36:
#line 81 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 37:
#line 755 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 246; goto _again;} }
	break;
	case 41:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 42:
#line 103 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 43:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 44:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 46:
#line 93 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 47:
#line 94 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 95 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 96 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 50:
#line 97 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 98 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 101 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p+1;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 54:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 55:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;}	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
	case 56:
#line 752 "NanorexMMPImportExportTest.rl"
	{act = 16;}
	break;
	case 57:
#line 743 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 58:
#line 744 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 59:
#line 745 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 60:
#line 746 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 61:
#line 752 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 62:
#line 752 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 63:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 16:
	{{p = ((te))-1;}/*cerr << "Ignored line, p = " << p << endl;*/}
	break;
	default: break;
	}
	}
	break;
#line 4753 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _group_lines_test_actions + _group_lines_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 38:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 39:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 4782 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _group_lines_test_eof_trans[cs] > 0 ) {
		_trans = _group_lines_test_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	const char *__acts = _group_lines_test_actions + _group_lines_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 37:
#line 755 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 246; goto _again;} }
	break;
#line 4805 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 773 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newViewDataGroup(void)
{
	++groupCount;
	cerr << lineNum << ": group (View Data)" << endl;
	currentGroupName = "View Data";
	groupNameStack.push_back(currentGroupName);
}

#if 0
void NanorexMMPImportExportTest::endViewDataGroup(void)
{
	cerr << lineNum << ": endgroup (View Data)" << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}
#endif

void
NanorexMMPImportExportTest::newMolStructGroup(std::string const& name,
                                              std::string const& style)
{
	++groupCount;
	cerr << lineNum << ": group (" << name << ") " << style << endl;
	currentGroupName = name;
	groupNameStack.push_back(currentGroupName);
	currentGroupStyle = style;
}

#if 0
void NanorexMMPImportExportTest::endMolStructGroup(std::string const& name)
{
	// comparing for errors should be done by parser application
	// here we are only testing to see if the tokens are being recognized
	cerr << lineNum << ": endgroup (" << name << ")  "
		<< "[stack-top = " << groupNameStack.back() << ']' << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}
#endif

void NanorexMMPImportExportTest::newClipboardGroup(void)
{
	++groupCount;
	cerr << lineNum << ": group (Clipboard)" << endl;
	currentGroupName = "Clipboard";
	groupNameStack.push_back(currentGroupName);
}


#if 0
void NanorexMMPImportExportTest::endClipboardGroup(void)
{
	cerr << lineNum << ": endgroup (Clipboard)" << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}
#endif


void NanorexMMPImportExportTest::endGroup(string const& name)
{
	++egroupCount;
	// comparing for errors should be done by parser application
	// here we are only testing to see if the tokens are being recognized
	cerr << lineNum << ": endgroup (" << name << ")  "
		<< "[stack-top = " << groupNameStack.back() << ']' << endl;
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}


void
NanorexMMPImportExportTest::newOpenGroupInfo(string const& key,
                                             string const& value)
{
	++infoOpenGroupCount;
	cerr << lineNum << ": info opengroup " << key << " = " << value << endl;
	/// @todo
}


void NanorexMMPImportExportTest::end1(void)
{
	cerr << lineNum << ": end1" << endl;
}


void NanorexMMPImportExportTest::uncheckedParseTest(void)
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


#line 916 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::uncheckedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 929 "NanorexMMPImportExportTest.rl"
	
#line 4954 "NanorexMMPImportExportTest.cpp"
static const char _unchecked_parse_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 28, 1, 31, 1, 33, 1, 
	34, 1, 41, 1, 43, 1, 57, 1, 
	58, 2, 0, 30, 2, 0, 53, 2, 
	0, 55, 2, 0, 56, 2, 5, 12, 
	2, 5, 13, 2, 5, 14, 2, 6, 
	7, 2, 6, 8, 2, 6, 9, 2, 
	8, 15, 2, 36, 24, 2, 41, 42, 
	3, 0, 16, 51, 3, 0, 19, 54, 
	3, 0, 20, 52, 3, 0, 23, 49, 
	3, 0, 25, 50, 3, 0, 27, 38, 
	3, 0, 29, 39, 3, 0, 29, 46, 
	3, 0, 32, 40, 3, 0, 35, 48, 
	3, 0, 37, 47, 3, 6, 8, 15, 
	3, 17, 0, 53, 3, 44, 0, 45, 
	4, 9, 0, 20, 52, 4, 9, 0, 
	23, 49, 4, 9, 0, 25, 50, 4, 
	9, 0, 29, 39, 4, 9, 0, 29, 
	46, 4, 9, 0, 37, 47, 4, 34, 
	0, 35, 48, 5, 6, 9, 0, 20, 
	52, 5, 6, 9, 0, 23, 49, 5, 
	6, 9, 0, 25, 50, 5, 6, 9, 
	0, 29, 39, 5, 6, 9, 0, 29, 
	46, 5, 6, 9, 0, 37, 47, 5, 
	8, 15, 0, 16, 51, 6, 6, 8, 
	15, 0, 16, 51
};

static const short _unchecked_parse_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 14, 
	19, 24, 25, 26, 27, 31, 36, 37, 
	38, 39, 44, 46, 51, 52, 53, 54, 
	55, 60, 65, 76, 90, 104, 109, 121, 
	126, 127, 128, 129, 134, 139, 140, 141, 
	142, 143, 148, 153, 154, 155, 156, 157, 
	158, 159, 160, 161, 166, 171, 173, 175, 
	177, 191, 205, 218, 232, 245, 259, 261, 
	263, 274, 277, 280, 283, 288, 295, 302, 
	308, 315, 323, 329, 334, 340, 349, 353, 
	361, 367, 376, 380, 388, 394, 403, 407, 
	415, 421, 427, 440, 442, 457, 472, 486, 
	501, 509, 513, 521, 529, 537, 541, 549, 
	557, 565, 569, 577, 585, 593, 600, 603, 
	606, 609, 617, 622, 629, 637, 645, 647, 
	655, 658, 661, 664, 667, 670, 673, 676, 
	679, 682, 687, 694, 701, 708, 716, 722, 
	724, 732, 739, 742, 745, 748, 751, 754, 
	761, 768, 770, 783, 795, 810, 825, 831, 
	845, 860, 863, 866, 869, 872, 878, 884, 
	896, 911, 926, 932, 945, 947, 962, 977, 
	991, 1006, 1020, 1035, 1038, 1041, 1044, 1049, 
	1057, 1060, 1063, 1066, 1071, 1083, 1098, 1113, 
	1127, 1142, 1154, 1169, 1184, 1186, 1200, 1215, 
	1218, 1221, 1224, 1227, 1232, 1244, 1259, 1274, 
	1288, 1303, 1315, 1330, 1345, 1347, 1361, 1376, 
	1379, 1382, 1385, 1388, 1391, 1394, 1397, 1400, 
	1405, 1417, 1432, 1447, 1461, 1476, 1488, 1503, 
	1518, 1520, 1534, 1549, 1552, 1555, 1560, 1566, 
	1578, 1593, 1608, 1614, 1627, 1629, 1644, 1659, 
	1673, 1688, 1702, 1717, 1719, 1719, 1731
};

static const char _unchecked_parse_test_trans_keys[] = {
	10, 32, 103, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	40, 11, 13, 9, 32, 86, 11, 13, 
	105, 101, 119, 9, 32, 11, 13, 9, 
	32, 68, 11, 13, 97, 116, 97, 9, 
	32, 41, 11, 13, 10, 35, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 40, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 41, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 41, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 9, 13, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 101, 9, 13, 110, 100, 
	49, 10, 32, 35, 9, 13, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 67, 11, 
	13, 108, 105, 112, 98, 111, 97, 114, 
	100, 9, 32, 41, 11, 13, 10, 32, 
	35, 9, 13, -1, 10, -1, 10, -1, 
	10, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, -1, 
	10, 32, 97, 98, 101, 103, 105, 109, 
	9, 13, -1, 10, 116, -1, 10, 111, 
	-1, 10, 109, -1, 10, 32, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, -1, 
	10, 32, 43, 45, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	35, 9, 13, -1, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	100, -1, 10, 95, 97, 99, 103, 49, 
	51, -1, 10, 32, 9, 13, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, -1, 
	10, 32, 35, 9, 13, 48, 57, -1, 
	10, 100, -1, 10, 105, -1, 10, 114, 
	-1, 10, 101, -1, 10, 99, -1, 10, 
	116, -1, 10, 105, -1, 10, 111, -1, 
	10, 110, -1, 10, 32, 9, 13, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 35, 40, 9, 
	13, -1, 10, 32, 35, 40, 9, 13, 
	-1, 10, -1, 10, 32, 41, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 110, -1, 10, 
	102, -1, 10, 111, -1, 10, 32, 9, 
	13, -1, 10, 32, 97, 99, 111, 9, 
	13, -1, 10, 116, -1, 10, 111, -1, 
	10, 109, -1, 10, 32, 9, 13, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 61, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 104, -1, 10, 117, -1, 10, 110, 
	-1, 10, 107, -1, 10, 32, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 112, -1, 10, 101, -1, 10, 
	110, -1, 10, 103, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 111, 
	-1, 10, 108, -1, 10, 32, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 97, 98, 101, 103, 105, 
	109, 9, 13, -1, 10, 32, 97, 98, 
	101, 103, 105, 109, 9, 13, 0
};

static const char _unchecked_parse_test_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 3, 3, 
	3, 1, 1, 1, 2, 3, 1, 1, 
	1, 3, 2, 3, 1, 1, 1, 1, 
	3, 3, 3, 4, 4, 3, 4, 3, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 3, 2, 2, 2, 
	4, 4, 3, 4, 3, 4, 2, 2, 
	9, 3, 3, 3, 3, 3, 3, 4, 
	3, 4, 4, 3, 4, 5, 2, 4, 
	4, 5, 2, 4, 4, 5, 2, 4, 
	4, 4, 5, 2, 5, 5, 4, 5, 
	4, 2, 4, 4, 4, 2, 4, 4, 
	4, 2, 4, 4, 4, 3, 3, 3, 
	3, 6, 3, 3, 4, 4, 2, 4, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 4, 4, 2, 
	4, 3, 3, 3, 3, 3, 3, 5, 
	5, 2, 5, 4, 5, 5, 4, 4, 
	5, 3, 3, 3, 3, 4, 4, 4, 
	5, 5, 4, 5, 2, 5, 5, 4, 
	5, 4, 5, 3, 3, 3, 3, 6, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 4, 4, 
	5, 5, 4, 5, 2, 5, 5, 4, 
	5, 4, 5, 2, 0, 10, 9
};

static const char _unchecked_parse_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 1, 1, 
	1, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 0, 1, 0, 0, 0, 0, 
	1, 1, 4, 5, 5, 1, 4, 1, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	0, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	5, 5, 5, 5, 5, 5, 0, 0, 
	1, 0, 0, 0, 1, 2, 2, 1, 
	2, 2, 1, 1, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 1, 4, 0, 5, 5, 5, 5, 
	2, 1, 2, 2, 2, 1, 2, 2, 
	2, 1, 2, 2, 2, 2, 0, 0, 
	0, 1, 1, 2, 2, 2, 0, 2, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 2, 2, 2, 2, 1, 0, 
	2, 2, 0, 0, 0, 0, 0, 1, 
	1, 0, 4, 4, 5, 5, 1, 5, 
	5, 0, 0, 0, 0, 1, 1, 4, 
	5, 5, 1, 4, 0, 5, 5, 5, 
	5, 5, 5, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	0, 0, 0, 0, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 1, 1, 4, 
	5, 5, 1, 4, 0, 5, 5, 5, 
	5, 5, 5, 0, 0, 1, 1
};

static const short _unchecked_parse_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 18, 
	23, 28, 30, 32, 34, 38, 43, 45, 
	47, 49, 54, 57, 62, 64, 66, 68, 
	70, 75, 80, 88, 98, 108, 113, 122, 
	127, 129, 131, 133, 138, 143, 145, 147, 
	149, 151, 156, 161, 163, 165, 167, 169, 
	171, 173, 175, 177, 182, 187, 190, 193, 
	196, 206, 216, 225, 235, 244, 254, 257, 
	260, 271, 275, 279, 283, 288, 294, 300, 
	306, 312, 319, 325, 330, 336, 344, 348, 
	355, 361, 369, 373, 380, 386, 394, 398, 
	405, 411, 417, 427, 430, 441, 452, 462, 
	473, 480, 484, 491, 498, 505, 509, 516, 
	523, 530, 534, 541, 548, 555, 561, 565, 
	569, 573, 581, 586, 592, 599, 606, 609, 
	616, 620, 624, 628, 632, 636, 640, 644, 
	648, 652, 657, 663, 669, 675, 682, 688, 
	691, 698, 704, 708, 712, 716, 720, 724, 
	731, 738, 741, 751, 760, 771, 782, 788, 
	798, 809, 813, 817, 821, 825, 831, 837, 
	846, 857, 868, 874, 884, 887, 898, 909, 
	919, 930, 940, 951, 955, 959, 963, 968, 
	976, 980, 984, 988, 993, 1002, 1013, 1024, 
	1034, 1045, 1054, 1065, 1076, 1079, 1089, 1100, 
	1104, 1108, 1112, 1116, 1121, 1130, 1141, 1152, 
	1162, 1173, 1182, 1193, 1204, 1207, 1217, 1228, 
	1232, 1236, 1240, 1244, 1248, 1252, 1256, 1260, 
	1265, 1274, 1285, 1296, 1306, 1317, 1326, 1337, 
	1348, 1351, 1361, 1372, 1376, 1380, 1385, 1391, 
	1400, 1411, 1422, 1428, 1438, 1441, 1452, 1463, 
	1473, 1484, 1494, 1505, 1508, 1509, 1521
};

static const unsigned char _unchecked_parse_test_trans_targs_wi[] = {
	1, 1, 2, 1, 0, 3, 0, 4, 
	0, 5, 0, 6, 0, 7, 7, 8, 
	7, 0, 7, 7, 8, 7, 0, 8, 
	8, 9, 8, 0, 10, 0, 11, 0, 
	12, 0, 13, 13, 13, 0, 13, 13, 
	14, 13, 0, 15, 0, 16, 0, 17, 
	0, 17, 17, 18, 17, 0, 19, 62, 
	0, 19, 19, 20, 19, 0, 21, 0, 
	22, 0, 23, 0, 24, 0, 25, 25, 
	26, 25, 0, 25, 25, 26, 25, 0, 
	26, 26, 27, 26, 27, 27, 27, 0, 
	28, 28, 29, 61, 28, 60, 61, 61, 
	61, 0, 28, 28, 29, 61, 28, 60, 
	61, 61, 61, 0, 31, 30, 55, 30, 
	0, 31, 30, 55, 56, 30, 56, 56, 
	56, 0, 31, 31, 32, 31, 0, 33, 
	0, 34, 0, 35, 0, 36, 35, 54, 
	35, 0, 36, 36, 37, 36, 0, 38, 
	0, 39, 0, 40, 0, 41, 0, 41, 
	41, 42, 41, 0, 42, 42, 43, 42, 
	0, 44, 0, 45, 0, 46, 0, 47, 
	0, 48, 0, 49, 0, 50, 0, 51, 
	0, 51, 51, 52, 51, 0, 244, 52, 
	53, 52, 0, 0, 244, 53, 0, 36, 
	54, 0, 31, 55, 31, 57, 55, 59, 
	57, 58, 59, 59, 59, 0, 31, 57, 
	55, 59, 57, 58, 59, 59, 59, 0, 
	58, 58, 59, 58, 58, 59, 59, 59, 
	0, 31, 57, 55, 59, 57, 58, 59, 
	59, 59, 0, 60, 60, 61, 60, 60, 
	61, 61, 61, 0, 28, 28, 29, 61, 
	28, 60, 61, 61, 61, 0, 0, 19, 
	62, 245, 245, 63, 245, 246, 64, 65, 
	110, 138, 153, 171, 227, 64, 63, 245, 
	245, 66, 63, 245, 245, 67, 63, 245, 
	245, 68, 63, 245, 245, 69, 69, 63, 
	245, 245, 69, 69, 70, 63, 245, 245, 
	71, 71, 109, 63, 245, 245, 71, 72, 
	71, 63, 245, 245, 72, 72, 73, 63, 
	245, 245, 74, 75, 74, 108, 63, 245, 
	245, 74, 75, 74, 63, 245, 245, 76, 
	76, 63, 245, 245, 76, 77, 76, 63, 
	245, 245, 77, 78, 105, 77, 79, 63, 
	245, 245, 79, 63, 245, 245, 80, 81, 
	80, 104, 63, 245, 245, 80, 81, 80, 
	63, 245, 245, 81, 82, 101, 81, 83, 
	63, 245, 245, 83, 63, 245, 245, 84, 
	85, 84, 100, 63, 245, 245, 84, 85, 
	84, 63, 245, 245, 85, 86, 97, 85, 
	87, 63, 245, 245, 87, 63, 245, 245, 
	88, 89, 88, 96, 63, 245, 245, 88, 
	89, 88, 63, 245, 245, 90, 91, 90, 
	63, 245, 245, 90, 91, 92, 90, 92, 
	92, 92, 63, 245, 245, 91, 245, 245, 
	93, 91, 95, 93, 94, 95, 95, 95, 
	63, 245, 245, 93, 91, 95, 93, 94, 
	95, 95, 95, 63, 245, 245, 94, 95, 
	94, 94, 95, 95, 95, 63, 245, 245, 
	93, 91, 95, 93, 94, 95, 95, 95, 
	63, 245, 245, 88, 89, 88, 96, 63, 
	245, 245, 98, 63, 245, 245, 88, 89, 
	88, 99, 63, 245, 245, 88, 89, 88, 
	99, 63, 245, 245, 84, 85, 84, 100, 
	63, 245, 245, 102, 63, 245, 245, 84, 
	85, 84, 103, 63, 245, 245, 84, 85, 
	84, 103, 63, 245, 245, 80, 81, 80, 
	104, 63, 245, 245, 106, 63, 245, 245, 
	80, 81, 80, 107, 63, 245, 245, 80, 
	81, 80, 107, 63, 245, 245, 74, 75, 
	74, 108, 63, 245, 245, 71, 71, 109, 
	63, 245, 245, 111, 63, 245, 245, 112, 
	63, 245, 245, 113, 63, 245, 245, 120, 
	114, 114, 114, 114, 63, 245, 245, 115, 
	115, 63, 245, 245, 115, 115, 116, 63, 
	245, 245, 117, 118, 117, 119, 63, 245, 
	245, 117, 118, 117, 116, 63, 245, 245, 
	118, 245, 245, 117, 118, 117, 119, 63, 
	245, 245, 121, 63, 245, 245, 122, 63, 
	245, 245, 123, 63, 245, 245, 124, 63, 
	245, 245, 125, 63, 245, 245, 126, 63, 
	245, 245, 127, 63, 245, 245, 128, 63, 
	245, 245, 129, 63, 245, 245, 130, 130, 
	63, 245, 245, 130, 130, 131, 63, 245, 
	245, 132, 132, 137, 63, 245, 245, 132, 
	132, 133, 63, 245, 245, 134, 135, 134, 
	136, 63, 245, 245, 134, 135, 134, 63, 
	245, 245, 135, 245, 245, 134, 135, 134, 
	136, 63, 245, 245, 132, 132, 137, 63, 
	245, 245, 139, 63, 245, 245, 140, 63, 
	245, 245, 141, 63, 245, 245, 142, 63, 
	245, 245, 143, 63, 245, 245, 144, 145, 
	146, 144, 63, 245, 245, 144, 145, 146, 
	144, 63, 245, 245, 145, 245, 245, 147, 
	150, 148, 147, 148, 148, 148, 63, 245, 
	245, 147, 148, 147, 148, 148, 148, 63, 
	245, 245, 149, 150, 152, 149, 151, 152, 
	152, 152, 63, 245, 245, 149, 150, 152, 
	149, 151, 152, 152, 152, 63, 245, 245, 
	150, 145, 150, 63, 245, 245, 151, 152, 
	151, 151, 152, 152, 152, 63, 245, 245, 
	149, 150, 152, 149, 151, 152, 152, 152, 
	63, 245, 245, 154, 63, 245, 245, 155, 
	63, 245, 245, 156, 63, 245, 245, 157, 
	63, 245, 245, 158, 159, 158, 63, 245, 
	245, 158, 159, 158, 63, 245, 245, 159, 
	160, 159, 160, 160, 160, 63, 245, 245, 
	161, 162, 170, 161, 169, 170, 170, 170, 
	63, 245, 245, 161, 162, 170, 161, 169, 
	170, 170, 170, 63, 245, 245, 163, 164, 
	163, 63, 245, 245, 163, 164, 165, 163, 
	165, 165, 165, 63, 245, 245, 164, 245, 
	245, 166, 164, 168, 166, 167, 168, 168, 
	168, 63, 245, 245, 166, 164, 168, 166, 
	167, 168, 168, 168, 63, 245, 245, 167, 
	168, 167, 167, 168, 168, 168, 63, 245, 
	245, 166, 164, 168, 166, 167, 168, 168, 
	168, 63, 245, 245, 169, 170, 169, 169, 
	170, 170, 170, 63, 245, 245, 161, 162, 
	170, 161, 169, 170, 170, 170, 63, 245, 
	245, 172, 63, 245, 245, 173, 63, 245, 
	245, 174, 63, 245, 245, 175, 175, 63, 
	245, 245, 175, 176, 191, 207, 175, 63, 
	245, 245, 177, 63, 245, 245, 178, 63, 
	245, 245, 179, 63, 245, 245, 180, 180, 
	63, 245, 245, 180, 181, 180, 181, 181, 
	181, 63, 245, 245, 182, 185, 184, 182, 
	183, 184, 184, 184, 63, 245, 245, 182, 
	185, 184, 182, 183, 184, 184, 184, 63, 
	245, 245, 183, 184, 183, 183, 184, 184, 
	184, 63, 245, 245, 182, 185, 184, 182, 
	183, 184, 184, 184, 63, 245, 245, 185, 
	186, 185, 186, 186, 186, 63, 245, 245, 
	187, 188, 190, 187, 189, 190, 190, 190, 
	63, 245, 245, 187, 188, 190, 187, 189, 
	190, 190, 190, 63, 245, 245, 188, 245, 
	245, 189, 190, 189, 189, 190, 190, 190, 
	63, 245, 245, 187, 188, 190, 187, 189, 
	190, 190, 190, 63, 245, 245, 192, 63, 
	245, 245, 193, 63, 245, 245, 194, 63, 
	245, 245, 195, 63, 245, 245, 196, 196, 
	63, 245, 245, 196, 197, 196, 197, 197, 
	197, 63, 245, 245, 198, 201, 200, 198, 
	199, 200, 200, 200, 63, 245, 245, 198, 
	201, 200, 198, 199, 200, 200, 200, 63, 
	245, 245, 199, 200, 199, 199, 200, 200, 
	200, 63, 245, 245, 198, 201, 200, 198, 
	199, 200, 200, 200, 63, 245, 245, 201, 
	202, 201, 202, 202, 202, 63, 245, 245, 
	203, 204, 206, 203, 205, 206, 206, 206, 
	63, 245, 245, 203, 204, 206, 203, 205, 
	206, 206, 206, 63, 245, 245, 204, 245, 
	245, 205, 206, 205, 205, 206, 206, 206, 
	63, 245, 245, 203, 204, 206, 203, 205, 
	206, 206, 206, 63, 245, 245, 208, 63, 
	245, 245, 209, 63, 245, 245, 210, 63, 
	245, 245, 211, 63, 245, 245, 212, 63, 
	245, 245, 213, 63, 245, 245, 214, 63, 
	245, 245, 215, 63, 245, 245, 216, 216, 
	63, 245, 245, 216, 217, 216, 217, 217, 
	217, 63, 245, 245, 218, 221, 220, 218, 
	219, 220, 220, 220, 63, 245, 245, 218, 
	221, 220, 218, 219, 220, 220, 220, 63, 
	245, 245, 219, 220, 219, 219, 220, 220, 
	220, 63, 245, 245, 218, 221, 220, 218, 
	219, 220, 220, 220, 63, 245, 245, 221, 
	222, 221, 222, 222, 222, 63, 245, 245, 
	223, 224, 226, 223, 225, 226, 226, 226, 
	63, 245, 245, 223, 224, 226, 223, 225, 
	226, 226, 226, 63, 245, 245, 224, 245, 
	245, 225, 226, 225, 225, 226, 226, 226, 
	63, 245, 245, 223, 224, 226, 223, 225, 
	226, 226, 226, 63, 245, 245, 228, 63, 
	245, 245, 229, 63, 245, 245, 230, 230, 
	63, 245, 245, 230, 231, 230, 63, 245, 
	245, 231, 232, 231, 232, 232, 232, 63, 
	245, 245, 233, 234, 242, 233, 241, 242, 
	242, 242, 63, 245, 245, 233, 234, 242, 
	233, 241, 242, 242, 242, 63, 245, 245, 
	235, 236, 235, 63, 245, 245, 235, 236, 
	237, 235, 237, 237, 237, 63, 245, 245, 
	236, 245, 245, 238, 236, 240, 238, 239, 
	240, 240, 240, 63, 245, 245, 238, 236, 
	240, 238, 239, 240, 240, 240, 63, 245, 
	245, 239, 240, 239, 239, 240, 240, 240, 
	63, 245, 245, 238, 236, 240, 238, 239, 
	240, 240, 240, 63, 245, 245, 241, 242, 
	241, 241, 242, 242, 242, 63, 245, 245, 
	233, 234, 242, 233, 241, 242, 242, 242, 
	63, 0, 245, 243, 244, 0, 246, 64, 
	243, 65, 110, 138, 153, 171, 227, 64, 
	63, 245, 246, 64, 65, 110, 138, 153, 
	171, 227, 64, 63, 0
};

static const unsigned char _unchecked_parse_test_trans_actions_wi[] = {
	1, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 39, 39, 39, 
	39, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 116, 0, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 41, 41, 
	41, 41, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	81, 81, 81, 78, 81, 13, 78, 78, 
	78, 0, 0, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 120, 0, 0, 0, 
	0, 120, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 57, 0, 0, 
	0, 0, 1, 0, 43, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 128, 0, 
	0, 0, 0, 0, 128, 0, 0, 57, 
	0, 0, 120, 0, 205, 84, 84, 78, 
	84, 13, 78, 78, 78, 0, 120, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	0, 0, 15, 0, 0, 15, 15, 15, 
	0, 167, 19, 19, 15, 19, 0, 15, 
	15, 15, 0, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 17, 17, 17, 15, 
	17, 0, 15, 15, 15, 0, 0, 116, 
	0, 55, 66, 0, 55, 148, 0, 0, 
	0, 45, 0, 90, 35, 0, 0, 55, 
	66, 0, 0, 55, 66, 0, 0, 55, 
	66, 0, 0, 55, 66, 0, 0, 0, 
	55, 66, 0, 0, 0, 0, 55, 66, 
	21, 21, 5, 0, 55, 66, 0, 0, 
	0, 0, 55, 66, 0, 0, 0, 0, 
	55, 66, 0, 0, 0, 5, 0, 55, 
	66, 0, 0, 0, 0, 55, 66, 23, 
	23, 0, 55, 66, 0, 0, 0, 0, 
	55, 66, 0, 0, 0, 0, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 25, 
	0, 5, 0, 55, 66, 0, 25, 0, 
	0, 55, 66, 0, 0, 0, 0, 0, 
	0, 55, 66, 0, 0, 55, 66, 0, 
	27, 0, 5, 0, 55, 66, 0, 27, 
	0, 0, 55, 66, 0, 0, 0, 0, 
	0, 0, 55, 66, 0, 0, 55, 66, 
	0, 29, 0, 5, 0, 55, 66, 0, 
	29, 0, 0, 55, 96, 0, 0, 0, 
	0, 55, 96, 0, 0, 0, 0, 0, 
	0, 0, 0, 55, 96, 0, 55, 229, 
	140, 140, 78, 140, 13, 78, 78, 78, 
	0, 55, 96, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 66, 0, 15, 
	0, 0, 15, 15, 15, 0, 55, 223, 
	87, 87, 15, 87, 0, 15, 15, 15, 
	0, 55, 66, 0, 29, 0, 5, 0, 
	55, 66, 0, 0, 55, 66, 11, 75, 
	11, 5, 0, 55, 66, 11, 75, 11, 
	5, 0, 55, 66, 0, 27, 0, 5, 
	0, 55, 66, 0, 0, 55, 66, 11, 
	72, 11, 5, 0, 55, 66, 11, 72, 
	11, 5, 0, 55, 66, 0, 25, 0, 
	5, 0, 55, 66, 0, 0, 55, 66, 
	11, 69, 11, 5, 0, 55, 66, 11, 
	69, 11, 5, 0, 55, 66, 0, 0, 
	0, 5, 0, 55, 66, 21, 21, 5, 
	0, 55, 66, 0, 0, 55, 66, 0, 
	0, 55, 66, 0, 0, 55, 66, 0, 
	33, 33, 33, 33, 0, 55, 66, 0, 
	0, 0, 55, 66, 0, 0, 0, 0, 
	55, 144, 31, 31, 31, 5, 0, 55, 
	60, 0, 0, 0, 0, 0, 55, 60, 
	0, 55, 144, 31, 31, 31, 5, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	0, 55, 66, 0, 0, 0, 0, 55, 
	66, 0, 0, 5, 0, 55, 66, 0, 
	0, 0, 0, 55, 100, 0, 0, 0, 
	9, 0, 55, 100, 0, 0, 0, 0, 
	55, 100, 0, 55, 100, 0, 0, 0, 
	9, 0, 55, 66, 0, 0, 5, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 182, 47, 47, 
	47, 47, 0, 55, 132, 0, 0, 0, 
	0, 0, 55, 132, 0, 55, 66, 0, 
	0, 0, 0, 0, 0, 0, 0, 55, 
	66, 0, 0, 0, 0, 0, 0, 0, 
	55, 66, 81, 81, 78, 81, 13, 78, 
	78, 78, 0, 55, 66, 0, 0, 15, 
	0, 0, 15, 15, 15, 0, 55, 132, 
	0, 0, 0, 0, 55, 66, 0, 15, 
	0, 0, 15, 15, 15, 0, 55, 66, 
	17, 17, 15, 17, 0, 15, 15, 15, 
	0, 55, 66, 0, 0, 55, 66, 0, 
	0, 55, 66, 0, 0, 55, 66, 0, 
	0, 55, 66, 41, 41, 41, 0, 55, 
	66, 0, 0, 0, 0, 55, 66, 0, 
	0, 0, 0, 0, 0, 0, 55, 66, 
	81, 81, 78, 81, 13, 78, 78, 78, 
	0, 55, 66, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 124, 0, 0, 
	0, 0, 55, 124, 0, 0, 0, 0, 
	0, 0, 0, 0, 55, 124, 0, 55, 
	211, 84, 84, 78, 84, 13, 78, 78, 
	78, 0, 55, 124, 0, 0, 15, 0, 
	0, 15, 15, 15, 0, 55, 66, 0, 
	15, 0, 0, 15, 15, 15, 0, 55, 
	172, 19, 19, 15, 19, 0, 15, 15, 
	15, 0, 55, 66, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 66, 17, 17, 
	15, 17, 0, 15, 15, 15, 0, 55, 
	66, 0, 0, 55, 66, 0, 0, 55, 
	66, 0, 0, 55, 66, 0, 0, 0, 
	55, 66, 0, 0, 0, 0, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	0, 55, 66, 0, 0, 0, 0, 0, 
	0, 0, 55, 66, 81, 81, 78, 81, 
	13, 78, 78, 78, 0, 55, 66, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	55, 66, 0, 15, 0, 0, 15, 15, 
	15, 0, 55, 66, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 55, 66, 0, 
	0, 0, 0, 0, 0, 0, 55, 187, 
	84, 84, 78, 84, 13, 78, 78, 78, 
	0, 55, 104, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 104, 0, 55, 
	66, 0, 15, 0, 0, 15, 15, 15, 
	0, 55, 152, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	0, 55, 66, 0, 0, 0, 0, 0, 
	0, 0, 55, 66, 81, 81, 78, 81, 
	13, 78, 78, 78, 0, 55, 66, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	55, 66, 0, 15, 0, 0, 15, 15, 
	15, 0, 55, 66, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 55, 66, 0, 
	0, 0, 0, 0, 0, 0, 55, 199, 
	84, 84, 78, 84, 13, 78, 78, 78, 
	0, 55, 112, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 112, 0, 55, 
	66, 0, 15, 0, 0, 15, 15, 15, 
	0, 55, 162, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	0, 55, 66, 0, 0, 0, 0, 0, 
	0, 0, 55, 66, 81, 81, 78, 81, 
	13, 78, 78, 78, 0, 55, 66, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	55, 66, 0, 15, 0, 0, 15, 15, 
	15, 0, 55, 66, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 55, 66, 0, 
	0, 0, 0, 0, 0, 0, 55, 217, 
	84, 84, 78, 84, 13, 78, 78, 78, 
	0, 55, 136, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 55, 136, 0, 55, 
	66, 0, 15, 0, 0, 15, 15, 15, 
	0, 55, 177, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 55, 66, 0, 0, 
	55, 66, 0, 0, 55, 66, 0, 0, 
	0, 55, 66, 0, 0, 0, 0, 55, 
	66, 0, 0, 0, 0, 0, 0, 0, 
	55, 66, 81, 81, 78, 81, 13, 78, 
	78, 78, 0, 55, 66, 0, 0, 15, 
	0, 0, 15, 15, 15, 0, 55, 108, 
	0, 0, 0, 0, 55, 108, 0, 0, 
	0, 0, 0, 0, 0, 0, 55, 108, 
	0, 55, 193, 84, 84, 78, 84, 13, 
	78, 78, 78, 0, 55, 108, 0, 0, 
	15, 0, 0, 15, 15, 15, 0, 55, 
	66, 0, 15, 0, 0, 15, 15, 15, 
	0, 55, 157, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 55, 66, 0, 15, 
	0, 0, 15, 15, 15, 0, 55, 66, 
	17, 17, 15, 17, 0, 15, 15, 15, 
	0, 0, 63, 0, 0, 0, 148, 0, 
	0, 0, 0, 45, 0, 90, 35, 0, 
	0, 53, 148, 0, 0, 0, 45, 0, 
	90, 35, 0, 0, 0
};

static const unsigned char _unchecked_parse_test_to_state_actions[] = {
	0, 49, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 49, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 49, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	0, 3, 0, 0, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 7, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 37, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 49, 93, 0
};

static const unsigned char _unchecked_parse_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 51, 0
};

static const short _unchecked_parse_test_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 90, 90, 90, 90, 90, 
	90, 90, 90, 0, 0, 0, 388
};

static const int unchecked_parse_test_start = 1;
static const int unchecked_parse_test_first_final = 244;
static const int unchecked_parse_test_error = 0;

static const int unchecked_parse_test_en_group_scanner = 245;
static const int unchecked_parse_test_en_main = 1;

#line 930 "NanorexMMPImportExportTest.rl"
	
#line 5846 "NanorexMMPImportExportTest.cpp"
	{
	cs = unchecked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 931 "NanorexMMPImportExportTest.rl"
	
#line 5856 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _unchecked_parse_test_actions + _unchecked_parse_test_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 5877 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _unchecked_parse_test_trans_keys + _unchecked_parse_test_key_offsets[cs];
	_trans = _unchecked_parse_test_index_offsets[cs];

	_klen = _unchecked_parse_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _unchecked_parse_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
_eof_trans:
	cs = _unchecked_parse_test_trans_targs_wi[_trans];

	if ( _unchecked_parse_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _unchecked_parse_test_actions + _unchecked_parse_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 905 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 39:
#line 908 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 40:
#line 913 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 44:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 103 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 46:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 47:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 49:
#line 93 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 50:
#line 94 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 95 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 96 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 97 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 98 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 101 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p+1;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 57:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 58:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;}	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 6190 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _unchecked_parse_test_actions + _unchecked_parse_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 41:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 6219 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _unchecked_parse_test_eof_trans[cs] > 0 ) {
		_trans = _unchecked_parse_test_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	}

	_out: {}
	}
#line 932 "NanorexMMPImportExportTest.rl"
}


/// Test the checked pattern matchers to see if local error actions introduced
/// interfere with the regular functioning
void NanorexMMPImportExportTest::checkedParseTest(void)
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


#line 993 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::checkedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 1006 "NanorexMMPImportExportTest.rl"
	
#line 6295 "NanorexMMPImportExportTest.cpp"
static const char _checked_parse_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	15, 1, 18, 1, 19, 1, 20, 1, 
	22, 1, 23, 1, 25, 1, 26, 1, 
	27, 1, 30, 1, 31, 1, 33, 1, 
	35, 1, 36, 1, 37, 1, 38, 1, 
	39, 1, 41, 1, 42, 1, 44, 1, 
	46, 1, 48, 1, 49, 1, 50, 1, 
	51, 1, 52, 1, 54, 1, 56, 1, 
	57, 1, 59, 1, 60, 1, 61, 1, 
	63, 1, 64, 1, 70, 1, 71, 1, 
	84, 1, 85, 2, 0, 55, 2, 0, 
	80, 2, 0, 82, 2, 0, 83, 2, 
	5, 12, 2, 5, 13, 2, 5, 14, 
	2, 6, 7, 2, 6, 8, 2, 6, 
	9, 2, 8, 21, 2, 8, 41, 2, 
	9, 42, 2, 18, 85, 2, 19, 85, 
	2, 20, 85, 2, 22, 85, 2, 26, 
	85, 2, 27, 85, 2, 28, 29, 2, 
	30, 85, 2, 31, 85, 2, 33, 34, 
	2, 33, 85, 2, 34, 35, 2, 35, 
	85, 2, 36, 85, 2, 37, 85, 2, 
	41, 44, 2, 41, 85, 2, 42, 85, 
	2, 44, 42, 2, 44, 85, 2, 49, 
	85, 2, 50, 85, 2, 63, 85, 2, 
	64, 85, 2, 72, 0, 3, 0, 16, 
	81, 3, 0, 17, 79, 3, 0, 24, 
	78, 3, 0, 40, 76, 3, 0, 45, 
	77, 3, 0, 47, 67, 3, 0, 53, 
	68, 3, 0, 53, 73, 3, 0, 58, 
	69, 3, 0, 62, 75, 3, 0, 66, 
	74, 3, 6, 8, 21, 3, 6, 8, 
	41, 3, 6, 9, 42, 3, 15, 0, 
	80, 3, 18, 0, 83, 3, 19, 0, 
	83, 3, 20, 0, 83, 3, 22, 0, 
	83, 3, 26, 0, 83, 3, 27, 0, 
	80, 3, 27, 0, 83, 3, 30, 0, 
	83, 3, 31, 0, 83, 3, 33, 0, 
	83, 3, 33, 34, 85, 3, 34, 35, 
	85, 3, 35, 0, 83, 3, 36, 0, 
	83, 3, 37, 0, 83, 3, 41, 0, 
	83, 3, 41, 44, 85, 3, 42, 0, 
	83, 3, 44, 42, 85, 3, 49, 0, 
	83, 3, 50, 0, 83, 3, 63, 0, 
	83, 3, 64, 0, 83, 3, 65, 43, 
	32, 4, 9, 0, 17, 79, 4, 9, 
	0, 40, 76, 4, 9, 0, 53, 68, 
	4, 9, 0, 53, 73, 4, 9, 0, 
	66, 74, 4, 22, 0, 24, 78, 4, 
	33, 34, 0, 83, 4, 34, 35, 0, 
	83, 4, 37, 0, 40, 76, 4, 41, 
	44, 0, 83, 4, 42, 0, 45, 77, 
	4, 44, 42, 0, 83, 4, 50, 0, 
	53, 68, 4, 50, 0, 53, 73, 4, 
	61, 0, 62, 75, 4, 64, 0, 66, 
	74, 5, 6, 9, 0, 17, 79, 5, 
	6, 9, 0, 40, 76, 5, 6, 9, 
	0, 53, 68, 5, 6, 9, 0, 53, 
	73, 5, 6, 9, 0, 66, 74, 5, 
	8, 21, 0, 24, 78, 5, 9, 42, 
	0, 45, 77, 6, 6, 8, 21, 0, 
	24, 78, 6, 6, 9, 42, 0, 45, 
	77
};

static const short _checked_parse_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 14, 
	19, 20, 21, 22, 26, 31, 32, 33, 
	34, 39, 41, 46, 47, 48, 49, 50, 
	55, 60, 71, 85, 99, 104, 116, 121, 
	122, 123, 124, 129, 134, 135, 136, 137, 
	138, 139, 144, 149, 150, 151, 152, 153, 
	154, 155, 156, 157, 162, 164, 166, 168, 
	170, 184, 198, 211, 225, 238, 252, 254, 
	256, 268, 279, 281, 282, 283, 284, 288, 
	294, 300, 305, 311, 318, 323, 327, 332, 
	340, 342, 349, 354, 362, 364, 371, 376, 
	384, 386, 393, 398, 403, 415, 417, 431, 
	445, 458, 472, 479, 481, 488, 495, 502, 
	504, 511, 518, 525, 527, 534, 541, 548, 
	554, 555, 556, 557, 563, 567, 573, 580, 
	587, 589, 596, 597, 598, 599, 600, 601, 
	602, 603, 604, 605, 609, 615, 621, 627, 
	634, 639, 641, 648, 654, 655, 656, 657, 
	658, 659, 665, 671, 673, 685, 696, 710, 
	724, 729, 742, 756, 757, 758, 759, 760, 
	765, 770, 781, 795, 809, 814, 826, 828, 
	842, 856, 869, 883, 896, 910, 911, 912, 
	913, 917, 924, 925, 926, 927, 931, 942, 
	956, 970, 983, 997, 1008, 1019, 1033, 1047, 
	1049, 1062, 1076, 1077, 1078, 1079, 1080, 1084, 
	1095, 1109, 1123, 1136, 1150, 1161, 1172, 1186, 
	1200, 1202, 1215, 1229, 1230, 1231, 1232, 1233, 
	1234, 1235, 1236, 1237, 1241, 1252, 1266, 1280, 
	1293, 1307, 1318, 1332, 1346, 1348, 1361, 1375, 
	1376, 1377, 1381, 1386, 1397, 1411, 1425, 1430, 
	1442, 1444, 1458, 1472, 1485, 1499, 1512, 1526, 
	1528, 1531, 1534, 1537, 1542, 1549, 1556, 1562, 
	1569, 1577, 1583, 1588, 1594, 1603, 1607, 1615, 
	1621, 1630, 1634, 1642, 1648, 1657, 1661, 1669, 
	1675, 1681, 1694, 1696, 1711, 1726, 1740, 1755, 
	1763, 1767, 1775, 1783, 1791, 1795, 1803, 1811, 
	1819, 1823, 1831, 1839, 1847, 1854, 1857, 1860, 
	1863, 1871, 1876, 1883, 1891, 1899, 1901, 1909, 
	1912, 1915, 1918, 1921, 1924, 1927, 1930, 1933, 
	1936, 1941, 1948, 1955, 1962, 1970, 1976, 1978, 
	1986, 1993, 1996, 1999, 2002, 2005, 2008, 2015, 
	2022, 2024, 2037, 2049, 2064, 2079, 2085, 2099, 
	2114, 2117, 2120, 2123, 2126, 2132, 2138, 2150, 
	2165, 2180, 2186, 2199, 2201, 2216, 2231, 2245, 
	2260, 2274, 2289, 2292, 2295, 2298, 2303, 2311, 
	2314, 2317, 2320, 2325, 2337, 2352, 2367, 2381, 
	2396, 2408, 2420, 2435, 2450, 2452, 2466, 2481, 
	2484, 2487, 2490, 2493, 2498, 2510, 2525, 2540, 
	2554, 2569, 2581, 2593, 2608, 2623, 2625, 2639, 
	2654, 2657, 2660, 2663, 2666, 2669, 2672, 2675, 
	2678, 2683, 2695, 2710, 2725, 2739, 2754, 2766, 
	2781, 2796, 2798, 2812, 2827, 2830, 2833, 2838, 
	2844, 2856, 2871, 2886, 2892, 2905, 2907, 2922, 
	2937, 2951, 2966, 2980, 2995, 2995, 3007
};

static const char _checked_parse_test_trans_keys[] = {
	10, 32, 103, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	86, 11, 13, 105, 101, 119, 9, 32, 
	11, 13, 9, 32, 68, 11, 13, 97, 
	116, 97, 9, 32, 41, 11, 13, 10, 
	35, 10, 32, 103, 9, 13, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 40, 11, 13, 9, 32, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 9, 13, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 101, 9, 
	13, 110, 100, 49, 10, 32, 35, 9, 
	13, 10, 32, 101, 9, 13, 103, 114, 
	111, 117, 112, 9, 32, 40, 11, 13, 
	9, 32, 67, 11, 13, 108, 105, 112, 
	98, 111, 97, 114, 100, 9, 32, 41, 
	11, 13, 10, 35, -1, 10, -1, 10, 
	-1, 10, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	-1, 10, 32, 35, 97, 98, 101, 103, 
	105, 109, 9, 13, 10, 32, 35, 97, 
	98, 101, 103, 105, 109, 9, 13, -1, 
	10, 116, 111, 109, 9, 32, 11, 13, 
	9, 32, 11, 13, 48, 57, 9, 32, 
	11, 13, 48, 57, 9, 32, 40, 11, 
	13, 9, 32, 11, 13, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	41, 11, 13, 9, 32, 11, 13, 9, 
	32, 40, 11, 13, 9, 32, 43, 45, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 9, 32, 43, 45, 11, 13, 
	48, 57, 48, 57, 9, 32, 44, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	9, 32, 43, 45, 11, 13, 48, 57, 
	48, 57, 9, 32, 41, 11, 13, 48, 
	57, 9, 32, 41, 11, 13, 10, 32, 
	35, 9, 13, 10, 32, 35, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 11, 13, 48, 57, 48, 
	57, 9, 32, 41, 11, 13, 48, 57, 
	9, 32, 41, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 48, 57, 
	9, 32, 44, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 9, 32, 41, 
	11, 13, 48, 57, 9, 32, 11, 13, 
	48, 57, 111, 110, 100, 95, 97, 99, 
	103, 49, 51, 9, 32, 11, 13, 9, 
	32, 11, 13, 48, 57, 10, 32, 35, 
	9, 13, 48, 57, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 10, 32, 35, 
	9, 13, 48, 57, 100, 105, 114, 101, 
	99, 116, 105, 111, 110, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 9, 
	32, 11, 13, 48, 57, 9, 32, 11, 
	13, 48, 57, 10, 32, 35, 9, 13, 
	48, 57, 10, 32, 35, 9, 13, -1, 
	10, 10, 32, 35, 9, 13, 48, 57, 
	9, 32, 11, 13, 48, 57, 103, 114, 
	111, 117, 112, 10, 32, 35, 40, 9, 
	13, 10, 32, 35, 40, 9, 13, -1, 
	10, 9, 32, 41, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 9, 
	13, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 114, 111, 117, 112, 
	9, 32, 40, 11, 13, 9, 32, 40, 
	11, 13, 9, 32, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 9, 13, 10, 32, 
	35, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 110, 102, 
	111, 9, 32, 11, 13, 9, 32, 97, 
	99, 111, 11, 13, 116, 111, 109, 9, 
	32, 11, 13, 9, 32, 95, 11, 13, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	61, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 9, 32, 61, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 9, 
	32, 61, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 9, 32, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 104, 117, 110, 107, 
	9, 32, 11, 13, 9, 32, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 61, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 61, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 61, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 9, 32, 95, 11, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 112, 101, 110, 
	103, 114, 111, 117, 112, 9, 32, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 61, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 61, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 61, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 9, 32, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, 111, 
	108, 9, 32, 11, 13, 9, 32, 40, 
	11, 13, 9, 32, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 9, 13, 10, 32, 
	35, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 116, -1, 10, 111, -1, 10, 
	109, -1, 10, 32, 9, 13, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 40, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, -1, 
	10, 32, 9, 13, -1, 10, 32, 40, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, -1, 10, 32, 
	43, 45, 9, 13, 48, 57, -1, 10, 
	48, 57, -1, 10, 32, 44, 9, 13, 
	48, 57, -1, 10, 32, 44, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	111, -1, 10, 110, -1, 10, 100, -1, 
	10, 95, 97, 99, 103, 49, 51, -1, 
	10, 32, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, 100, 
	-1, 10, 105, -1, 10, 114, -1, 10, 
	101, -1, 10, 99, -1, 10, 116, -1, 
	10, 105, -1, 10, 111, -1, 10, 110, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 35, 9, 13, 
	48, 57, -1, 10, 32, 35, 9, 13, 
	-1, 10, -1, 10, 32, 35, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 103, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 35, 40, 9, 13, -1, 
	10, 32, 35, 40, 9, 13, -1, 10, 
	-1, 10, 32, 41, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 9, 13, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 114, -1, 10, 111, 
	-1, 10, 117, -1, 10, 112, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 40, 
	9, 13, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	9, 13, -1, 10, 32, 35, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 110, -1, 10, 102, -1, 
	10, 111, -1, 10, 32, 9, 13, -1, 
	10, 32, 97, 99, 111, 9, 13, -1, 
	10, 116, -1, 10, 111, -1, 10, 109, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 104, -1, 10, 117, -1, 
	10, 110, -1, 10, 107, -1, 10, 32, 
	9, 13, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 61, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 61, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	112, -1, 10, 101, -1, 10, 110, -1, 
	10, 103, -1, 10, 114, -1, 10, 111, 
	-1, 10, 117, -1, 10, 112, -1, 10, 
	32, 9, 13, -1, 10, 32, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 61, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 111, -1, 10, 
	108, -1, 10, 32, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 97, 
	98, 101, 103, 105, 109, 9, 13, 10, 
	32, 35, 97, 98, 101, 103, 105, 109, 
	9, 13, 0
};

static const char _checked_parse_test_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 3, 3, 
	1, 1, 1, 2, 3, 1, 1, 1, 
	3, 2, 3, 1, 1, 1, 1, 3, 
	3, 3, 4, 4, 3, 4, 3, 1, 
	1, 1, 3, 3, 1, 1, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 2, 2, 2, 2, 
	4, 4, 3, 4, 3, 4, 2, 2, 
	10, 9, 2, 1, 1, 1, 2, 2, 
	2, 3, 2, 3, 3, 2, 3, 4, 
	0, 3, 3, 4, 0, 3, 3, 4, 
	0, 3, 3, 3, 4, 2, 4, 4, 
	3, 4, 3, 0, 3, 3, 3, 0, 
	3, 3, 3, 0, 3, 3, 3, 2, 
	1, 1, 1, 4, 2, 2, 3, 3, 
	2, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 2, 2, 2, 2, 3, 
	3, 2, 3, 2, 1, 1, 1, 1, 
	1, 4, 4, 2, 4, 3, 4, 4, 
	3, 3, 4, 1, 1, 1, 1, 3, 
	3, 3, 4, 4, 3, 4, 2, 4, 
	4, 3, 4, 3, 4, 1, 1, 1, 
	2, 5, 1, 1, 1, 2, 3, 4, 
	4, 3, 4, 3, 3, 4, 4, 2, 
	3, 4, 1, 1, 1, 1, 2, 3, 
	4, 4, 3, 4, 3, 3, 4, 4, 
	2, 3, 4, 1, 1, 1, 1, 1, 
	1, 1, 1, 2, 3, 4, 4, 3, 
	4, 3, 4, 4, 2, 3, 4, 1, 
	1, 2, 3, 3, 4, 4, 3, 4, 
	2, 4, 4, 3, 4, 3, 4, 2, 
	3, 3, 3, 3, 3, 3, 4, 3, 
	4, 4, 3, 4, 5, 2, 4, 4, 
	5, 2, 4, 4, 5, 2, 4, 4, 
	4, 5, 2, 5, 5, 4, 5, 4, 
	2, 4, 4, 4, 2, 4, 4, 4, 
	2, 4, 4, 4, 3, 3, 3, 3, 
	6, 3, 3, 4, 4, 2, 4, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 4, 4, 2, 4, 
	3, 3, 3, 3, 3, 3, 5, 5, 
	2, 5, 4, 5, 5, 4, 4, 5, 
	3, 3, 3, 3, 4, 4, 4, 5, 
	5, 4, 5, 2, 5, 5, 4, 5, 
	4, 5, 3, 3, 3, 3, 6, 3, 
	3, 3, 3, 4, 5, 5, 4, 5, 
	4, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 0, 10, 9
};

static const char _checked_parse_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	1, 0, 1, 0, 0, 0, 0, 1, 
	1, 4, 5, 5, 1, 4, 1, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	0, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 0, 0, 0, 
	5, 5, 5, 5, 5, 5, 0, 0, 
	1, 1, 0, 0, 0, 0, 1, 2, 
	2, 1, 2, 2, 1, 1, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 1, 4, 0, 5, 5, 
	5, 5, 2, 1, 2, 2, 2, 1, 
	2, 2, 2, 1, 2, 2, 2, 2, 
	0, 0, 0, 1, 1, 2, 2, 2, 
	0, 2, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 2, 2, 2, 2, 
	1, 0, 2, 2, 0, 0, 0, 0, 
	0, 1, 1, 0, 4, 4, 5, 5, 
	1, 5, 5, 0, 0, 0, 0, 1, 
	1, 4, 5, 5, 1, 4, 0, 5, 
	5, 5, 5, 5, 5, 0, 0, 0, 
	1, 1, 0, 0, 0, 1, 4, 5, 
	5, 5, 5, 4, 4, 5, 5, 0, 
	5, 5, 0, 0, 0, 0, 1, 4, 
	5, 5, 5, 5, 4, 4, 5, 5, 
	0, 5, 5, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	0, 1, 1, 4, 5, 5, 1, 4, 
	0, 5, 5, 5, 5, 5, 5, 0, 
	0, 0, 0, 1, 2, 2, 1, 2, 
	2, 1, 1, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	1, 4, 0, 5, 5, 5, 5, 2, 
	1, 2, 2, 2, 1, 2, 2, 2, 
	1, 2, 2, 2, 2, 0, 0, 0, 
	1, 1, 2, 2, 2, 0, 2, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 2, 2, 2, 2, 1, 0, 2, 
	2, 0, 0, 0, 0, 0, 1, 1, 
	0, 4, 4, 5, 5, 1, 5, 5, 
	0, 0, 0, 0, 1, 1, 4, 5, 
	5, 1, 4, 0, 5, 5, 5, 5, 
	5, 5, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 5, 5, 5, 5, 
	4, 4, 5, 5, 0, 5, 5, 0, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 1, 1
};

static const short _checked_parse_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 18, 
	23, 25, 27, 29, 33, 38, 40, 42, 
	44, 49, 52, 57, 59, 61, 63, 65, 
	70, 75, 83, 93, 103, 108, 117, 122, 
	124, 126, 128, 133, 138, 140, 142, 144, 
	146, 148, 153, 158, 160, 162, 164, 166, 
	168, 170, 172, 174, 179, 182, 185, 188, 
	191, 201, 211, 220, 230, 239, 249, 252, 
	255, 267, 278, 281, 283, 285, 287, 291, 
	296, 301, 306, 311, 317, 322, 326, 331, 
	338, 340, 346, 351, 358, 360, 366, 371, 
	378, 380, 386, 391, 396, 405, 408, 418, 
	428, 437, 447, 453, 455, 461, 467, 473, 
	475, 481, 487, 493, 495, 501, 507, 513, 
	518, 520, 522, 524, 530, 534, 539, 545, 
	551, 554, 560, 562, 564, 566, 568, 570, 
	572, 574, 576, 578, 582, 587, 592, 597, 
	603, 608, 611, 617, 622, 624, 626, 628, 
	630, 632, 638, 644, 647, 656, 664, 674, 
	684, 689, 698, 708, 710, 712, 714, 716, 
	721, 726, 734, 744, 754, 759, 768, 771, 
	781, 791, 800, 810, 819, 829, 831, 833, 
	835, 839, 846, 848, 850, 852, 856, 864, 
	874, 884, 893, 903, 911, 919, 929, 939, 
	942, 951, 961, 963, 965, 967, 969, 973, 
	981, 991, 1001, 1010, 1020, 1028, 1036, 1046, 
	1056, 1059, 1068, 1078, 1080, 1082, 1084, 1086, 
	1088, 1090, 1092, 1094, 1098, 1106, 1116, 1126, 
	1135, 1145, 1153, 1163, 1173, 1176, 1185, 1195, 
	1197, 1199, 1203, 1208, 1216, 1226, 1236, 1241, 
	1250, 1253, 1263, 1273, 1282, 1292, 1301, 1311, 
	1314, 1318, 1322, 1326, 1331, 1337, 1343, 1349, 
	1355, 1362, 1368, 1373, 1379, 1387, 1391, 1398, 
	1404, 1412, 1416, 1423, 1429, 1437, 1441, 1448, 
	1454, 1460, 1470, 1473, 1484, 1495, 1505, 1516, 
	1523, 1527, 1534, 1541, 1548, 1552, 1559, 1566, 
	1573, 1577, 1584, 1591, 1598, 1604, 1608, 1612, 
	1616, 1624, 1629, 1635, 1642, 1649, 1652, 1659, 
	1663, 1667, 1671, 1675, 1679, 1683, 1687, 1691, 
	1695, 1700, 1706, 1712, 1718, 1725, 1731, 1734, 
	1741, 1747, 1751, 1755, 1759, 1763, 1767, 1774, 
	1781, 1784, 1794, 1803, 1814, 1825, 1831, 1841, 
	1852, 1856, 1860, 1864, 1868, 1874, 1880, 1889, 
	1900, 1911, 1917, 1927, 1930, 1941, 1952, 1962, 
	1973, 1983, 1994, 1998, 2002, 2006, 2011, 2019, 
	2023, 2027, 2031, 2036, 2045, 2056, 2067, 2077, 
	2088, 2097, 2106, 2117, 2128, 2131, 2141, 2152, 
	2156, 2160, 2164, 2168, 2173, 2182, 2193, 2204, 
	2214, 2225, 2234, 2243, 2254, 2265, 2268, 2278, 
	2289, 2293, 2297, 2301, 2305, 2309, 2313, 2317, 
	2321, 2326, 2335, 2346, 2357, 2367, 2378, 2387, 
	2398, 2409, 2412, 2422, 2433, 2437, 2441, 2446, 
	2452, 2461, 2472, 2483, 2489, 2499, 2502, 2513, 
	2524, 2534, 2545, 2555, 2566, 2567, 2579
};

static const short _checked_parse_test_indicies[] = {
	2, 0, 3, 0, 1, 4, 1, 5, 
	1, 6, 1, 7, 1, 7, 7, 8, 
	7, 1, 8, 8, 9, 8, 1, 10, 
	1, 11, 1, 12, 1, 13, 13, 13, 
	1, 13, 13, 14, 13, 1, 15, 1, 
	16, 1, 17, 1, 17, 17, 18, 17, 
	1, 20, 21, 19, 23, 22, 24, 22, 
	1, 25, 1, 26, 1, 27, 1, 28, 
	1, 29, 29, 30, 29, 1, 31, 31, 
	32, 31, 1, 34, 34, 35, 34, 35, 
	35, 35, 33, 36, 36, 37, 39, 36, 
	38, 39, 39, 39, 1, 40, 40, 41, 
	43, 40, 42, 43, 43, 43, 33, 45, 
	44, 46, 44, 1, 49, 48, 50, 51, 
	48, 51, 51, 51, 47, 53, 52, 54, 
	52, 1, 55, 1, 56, 1, 57, 1, 
	59, 57, 60, 57, 58, 62, 61, 63, 
	61, 1, 64, 1, 65, 1, 66, 1, 
	67, 1, 68, 1, 68, 68, 69, 68, 
	1, 69, 69, 70, 69, 1, 71, 1, 
	72, 1, 73, 1, 74, 1, 75, 1, 
	76, 1, 77, 1, 78, 1, 78, 78, 
	79, 78, 1, 81, 82, 80, 80, 81, 
	82, 58, 59, 60, 1, 45, 46, 84, 
	83, 85, 87, 83, 86, 87, 87, 87, 
	1, 49, 88, 50, 90, 88, 89, 90, 
	90, 90, 47, 89, 89, 90, 89, 89, 
	90, 90, 90, 47, 92, 91, 93, 90, 
	91, 89, 90, 90, 90, 1, 42, 42, 
	43, 42, 42, 43, 43, 43, 33, 94, 
	94, 95, 43, 94, 42, 43, 43, 43, 
	1, 19, 20, 21, 1, 97, 96, 1, 
	99, 98, 100, 101, 102, 103, 104, 105, 
	106, 98, 96, 109, 108, 110, 111, 112, 
	113, 114, 115, 116, 108, 107, 107, 117, 
	110, 118, 107, 119, 107, 120, 107, 121, 
	121, 121, 107, 123, 123, 123, 124, 122, 
	125, 125, 125, 126, 107, 128, 128, 129, 
	128, 127, 129, 129, 129, 130, 127, 131, 
	131, 132, 131, 133, 127, 131, 131, 132, 
	131, 127, 134, 134, 134, 107, 135, 135, 
	136, 135, 107, 136, 136, 137, 138, 136, 
	139, 107, 139, 107, 140, 140, 141, 140, 
	142, 107, 140, 140, 141, 140, 107, 143, 
	143, 144, 145, 143, 146, 107, 146, 107, 
	147, 147, 148, 147, 149, 107, 147, 147, 
	148, 147, 107, 150, 150, 151, 152, 150, 
	153, 107, 153, 107, 155, 155, 156, 155, 
	157, 154, 155, 155, 156, 155, 154, 159, 
	158, 160, 158, 107, 163, 162, 164, 165, 
	162, 165, 165, 165, 161, 107, 159, 160, 
	167, 166, 168, 170, 166, 169, 170, 170, 
	170, 107, 163, 171, 164, 173, 171, 172, 
	173, 173, 173, 161, 172, 172, 173, 172, 
	172, 173, 173, 173, 161, 175, 174, 176, 
	173, 174, 172, 173, 173, 173, 107, 155, 
	155, 156, 155, 157, 154, 177, 107, 178, 
	178, 179, 178, 180, 154, 178, 178, 179, 
	178, 180, 154, 147, 147, 148, 147, 149, 
	107, 181, 107, 182, 182, 183, 182, 184, 
	107, 182, 182, 183, 182, 184, 107, 140, 
	140, 141, 140, 142, 107, 185, 107, 186, 
	186, 187, 186, 188, 107, 186, 186, 187, 
	186, 188, 107, 131, 131, 132, 131, 133, 
	127, 125, 125, 125, 126, 107, 189, 107, 
	190, 107, 191, 107, 194, 193, 193, 193, 
	193, 192, 195, 195, 195, 107, 197, 197, 
	197, 198, 196, 200, 199, 201, 199, 202, 
	107, 204, 203, 205, 203, 198, 196, 107, 
	207, 206, 200, 199, 201, 199, 202, 107, 
	208, 107, 209, 107, 210, 107, 211, 107, 
	212, 107, 213, 107, 214, 107, 215, 107, 
	216, 107, 217, 217, 217, 107, 217, 217, 
	217, 219, 218, 220, 220, 220, 221, 218, 
	220, 220, 220, 223, 222, 225, 224, 226, 
	224, 227, 222, 225, 224, 226, 224, 107, 
	107, 225, 226, 225, 224, 226, 224, 227, 
	222, 220, 220, 220, 221, 218, 228, 107, 
	229, 107, 230, 107, 231, 107, 232, 107, 
	234, 233, 235, 236, 233, 107, 238, 237, 
	239, 240, 237, 107, 107, 238, 239, 242, 
	242, 243, 244, 242, 244, 244, 244, 241, 
	242, 242, 244, 242, 244, 244, 244, 241, 
	245, 245, 246, 248, 245, 247, 248, 248, 
	248, 107, 249, 249, 243, 251, 249, 250, 
	251, 251, 251, 241, 238, 252, 239, 252, 
	107, 250, 250, 251, 250, 250, 251, 251, 
	251, 241, 253, 253, 254, 251, 253, 250, 
	251, 251, 251, 107, 255, 107, 256, 107, 
	257, 107, 258, 107, 259, 259, 260, 259, 
	107, 261, 261, 262, 261, 107, 263, 263, 
	264, 263, 264, 264, 264, 241, 265, 265, 
	266, 268, 265, 267, 268, 268, 268, 107, 
	269, 269, 270, 272, 269, 271, 272, 272, 
	272, 241, 274, 273, 275, 273, 107, 278, 
	277, 279, 280, 277, 280, 280, 280, 276, 
	107, 274, 275, 282, 281, 283, 285, 281, 
	284, 285, 285, 285, 107, 278, 286, 279, 
	288, 286, 287, 288, 288, 288, 276, 287, 
	287, 288, 287, 287, 288, 288, 288, 276, 
	290, 289, 291, 288, 289, 287, 288, 288, 
	288, 107, 271, 271, 272, 271, 271, 272, 
	272, 272, 241, 292, 292, 293, 272, 292, 
	271, 272, 272, 272, 107, 294, 107, 295, 
	107, 296, 107, 297, 297, 297, 107, 297, 
	297, 298, 299, 300, 297, 107, 301, 107, 
	302, 107, 303, 107, 304, 304, 304, 107, 
	304, 304, 306, 304, 306, 306, 306, 305, 
	308, 308, 311, 310, 308, 309, 310, 310, 
	310, 307, 312, 312, 315, 314, 312, 313, 
	314, 314, 314, 307, 313, 313, 314, 313, 
	313, 314, 314, 314, 305, 316, 316, 317, 
	314, 316, 313, 314, 314, 314, 307, 319, 
	319, 320, 319, 320, 320, 320, 318, 319, 
	319, 320, 319, 320, 320, 320, 321, 323, 
	322, 324, 326, 322, 325, 326, 326, 326, 
	321, 328, 327, 329, 331, 327, 330, 331, 
	331, 331, 321, 107, 328, 329, 330, 330, 
	331, 330, 330, 331, 331, 331, 321, 333, 
	332, 334, 331, 332, 330, 331, 331, 331, 
	321, 335, 107, 336, 107, 337, 107, 338, 
	107, 339, 339, 339, 107, 341, 341, 342, 
	341, 342, 342, 342, 340, 345, 345, 348, 
	347, 345, 346, 347, 347, 347, 344, 349, 
	349, 352, 351, 349, 350, 351, 351, 351, 
	344, 350, 350, 351, 350, 350, 351, 351, 
	351, 340, 353, 353, 354, 351, 353, 350, 
	351, 351, 351, 344, 356, 356, 357, 356, 
	357, 357, 357, 355, 356, 356, 357, 356, 
	357, 357, 357, 358, 360, 359, 361, 363, 
	359, 362, 363, 363, 363, 358, 365, 364, 
	366, 368, 364, 367, 368, 368, 368, 358, 
	107, 370, 369, 367, 367, 368, 367, 367, 
	368, 368, 368, 358, 372, 371, 373, 368, 
	371, 367, 368, 368, 368, 358, 374, 107, 
	375, 107, 376, 107, 377, 107, 378, 107, 
	379, 107, 380, 107, 381, 107, 382, 382, 
	382, 107, 384, 384, 385, 384, 385, 385, 
	385, 383, 386, 386, 389, 388, 386, 387, 
	388, 388, 388, 107, 390, 390, 393, 392, 
	390, 391, 392, 392, 392, 383, 391, 391, 
	392, 391, 391, 392, 392, 392, 383, 394, 
	394, 395, 392, 394, 391, 392, 392, 392, 
	107, 397, 397, 398, 397, 398, 398, 398, 
	396, 400, 399, 401, 403, 399, 402, 403, 
	403, 403, 107, 405, 404, 406, 408, 404, 
	407, 408, 408, 408, 396, 107, 410, 409, 
	407, 407, 408, 407, 407, 408, 408, 408, 
	396, 412, 411, 413, 408, 411, 407, 408, 
	408, 408, 107, 414, 107, 415, 107, 416, 
	416, 416, 107, 417, 417, 418, 417, 107, 
	418, 418, 419, 418, 419, 419, 419, 107, 
	421, 421, 422, 424, 421, 423, 424, 424, 
	424, 420, 425, 425, 426, 428, 425, 427, 
	428, 428, 428, 420, 430, 429, 431, 429, 
	107, 434, 433, 435, 436, 433, 436, 436, 
	436, 432, 107, 430, 431, 438, 437, 439, 
	441, 437, 440, 441, 441, 441, 107, 434, 
	442, 435, 444, 442, 443, 444, 444, 444, 
	432, 443, 443, 444, 443, 443, 444, 444, 
	444, 432, 446, 445, 447, 444, 445, 443, 
	444, 444, 444, 107, 427, 427, 428, 427, 
	427, 428, 428, 428, 107, 448, 448, 449, 
	428, 448, 427, 428, 428, 428, 420, 1, 
	117, 100, 1, 97, 450, 96, 1, 97, 
	451, 96, 1, 97, 452, 96, 1, 97, 
	453, 453, 96, 455, 457, 456, 456, 458, 
	454, 1, 97, 459, 459, 460, 96, 462, 
	464, 463, 465, 463, 461, 462, 464, 465, 
	465, 466, 461, 462, 464, 467, 468, 467, 
	469, 461, 462, 464, 467, 468, 467, 461, 
	1, 97, 470, 470, 96, 1, 97, 471, 
	472, 471, 96, 1, 97, 472, 473, 474, 
	472, 475, 96, 1, 97, 475, 96, 1, 
	97, 476, 477, 476, 478, 96, 1, 97, 
	476, 477, 476, 96, 1, 97, 479, 480, 
	481, 479, 482, 96, 1, 97, 482, 96, 
	1, 97, 483, 484, 483, 485, 96, 1, 
	97, 483, 484, 483, 96, 1, 97, 486, 
	487, 488, 486, 489, 96, 1, 97, 489, 
	96, 491, 493, 492, 494, 492, 495, 490, 
	491, 493, 492, 494, 492, 490, 1, 159, 
	496, 497, 496, 96, 499, 163, 500, 501, 
	502, 500, 502, 502, 502, 498, 1, 159, 
	497, 1, 167, 503, 504, 506, 503, 505, 
	506, 506, 506, 96, 499, 163, 507, 501, 
	509, 507, 508, 509, 509, 509, 498, 499, 
	510, 508, 509, 508, 508, 509, 509, 509, 
	498, 1, 175, 511, 512, 509, 511, 508, 
	509, 509, 509, 96, 491, 493, 492, 494, 
	492, 495, 490, 1, 97, 513, 96, 491, 
	493, 514, 515, 514, 516, 490, 491, 493, 
	514, 515, 514, 516, 490, 1, 97, 483, 
	484, 483, 485, 96, 1, 97, 517, 96, 
	1, 97, 518, 519, 518, 520, 96, 1, 
	97, 518, 519, 518, 520, 96, 1, 97, 
	476, 477, 476, 478, 96, 1, 97, 521, 
	96, 1, 97, 522, 523, 522, 524, 96, 
	1, 97, 522, 523, 522, 524, 96, 462, 
	464, 467, 468, 467, 469, 461, 1, 97, 
	459, 459, 460, 96, 1, 97, 525, 96, 
	1, 97, 526, 96, 1, 97, 527, 96, 
	529, 530, 532, 531, 531, 531, 531, 528, 
	1, 97, 533, 533, 96, 535, 537, 536, 
	536, 538, 534, 1, 200, 539, 540, 539, 
	541, 96, 535, 204, 542, 543, 542, 538, 
	534, 1, 207, 544, 1, 200, 539, 540, 
	539, 541, 96, 1, 97, 545, 96, 1, 
	97, 546, 96, 1, 97, 547, 96, 1, 
	97, 548, 96, 1, 97, 549, 96, 1, 
	97, 550, 96, 1, 97, 551, 96, 1, 
	97, 552, 96, 1, 97, 553, 96, 1, 
	97, 554, 554, 96, 556, 557, 554, 554, 
	558, 555, 556, 557, 559, 559, 560, 555, 
	562, 563, 559, 559, 564, 561, 562, 225, 
	565, 566, 565, 567, 561, 1, 225, 565, 
	566, 565, 96, 1, 225, 566, 562, 225, 
	565, 566, 565, 567, 561, 556, 557, 559, 
	559, 560, 555, 1, 97, 568, 96, 1, 
	97, 569, 96, 1, 97, 570, 96, 1, 
	97, 571, 96, 1, 97, 572, 96, 1, 
	234, 573, 574, 575, 573, 96, 1, 238, 
	576, 577, 578, 576, 96, 1, 238, 577, 
	33, 581, 580, 582, 583, 580, 583, 583, 
	583, 579, 33, 581, 580, 583, 580, 583, 
	583, 583, 579, 1, 97, 584, 585, 587, 
	584, 586, 587, 587, 587, 96, 33, 581, 
	588, 582, 590, 588, 589, 590, 590, 590, 
	579, 1, 238, 591, 577, 591, 96, 33, 
	581, 589, 590, 589, 589, 590, 590, 590, 
	579, 1, 97, 592, 593, 590, 592, 589, 
	590, 590, 590, 96, 1, 97, 594, 96, 
	1, 97, 595, 96, 1, 97, 596, 96, 
	1, 97, 597, 96, 1, 97, 598, 599, 
	598, 96, 1, 97, 600, 601, 600, 96, 
	33, 581, 602, 603, 602, 603, 603, 603, 
	579, 1, 97, 604, 605, 607, 604, 606, 
	607, 607, 607, 96, 33, 581, 608, 609, 
	611, 608, 610, 611, 611, 611, 579, 1, 
	274, 612, 613, 612, 96, 47, 278, 615, 
	616, 617, 615, 617, 617, 617, 614, 1, 
	274, 613, 1, 282, 618, 619, 621, 618, 
	620, 621, 621, 621, 96, 47, 278, 622, 
	616, 624, 622, 623, 624, 624, 624, 614, 
	47, 625, 623, 624, 623, 623, 624, 624, 
	624, 614, 1, 290, 626, 627, 624, 626, 
	623, 624, 624, 624, 96, 33, 581, 610, 
	611, 610, 610, 611, 611, 611, 579, 1, 
	97, 628, 629, 611, 628, 610, 611, 611, 
	611, 96, 1, 97, 630, 96, 1, 97, 
	631, 96, 1, 97, 632, 96, 1, 97, 
	633, 633, 96, 1, 97, 633, 634, 635, 
	636, 633, 96, 1, 97, 637, 96, 1, 
	97, 638, 96, 1, 97, 639, 96, 1, 
	97, 640, 640, 96, 642, 643, 640, 644, 
	640, 644, 644, 644, 641, 646, 648, 647, 
	651, 650, 647, 649, 650, 650, 650, 645, 
	646, 648, 652, 655, 654, 652, 653, 654, 
	654, 654, 645, 642, 643, 653, 654, 653, 
	653, 654, 654, 654, 641, 646, 648, 656, 
	657, 654, 656, 653, 654, 654, 654, 645, 
	659, 661, 660, 662, 660, 662, 662, 662, 
	658, 664, 665, 660, 662, 660, 662, 662, 
	662, 663, 664, 323, 666, 667, 669, 666, 
	668, 669, 669, 669, 663, 664, 328, 670, 
	671, 673, 670, 672, 673, 673, 673, 663, 
	1, 328, 671, 664, 665, 672, 673, 672, 
	672, 673, 673, 673, 663, 664, 333, 674, 
	675, 673, 674, 672, 673, 673, 673, 663, 
	1, 97, 676, 96, 1, 97, 677, 96, 
	1, 97, 678, 96, 1, 97, 679, 96, 
	1, 97, 680, 680, 96, 682, 684, 683, 
	685, 683, 685, 685, 685, 681, 687, 689, 
	688, 692, 691, 688, 690, 691, 691, 691, 
	686, 687, 689, 693, 696, 695, 693, 694, 
	695, 695, 695, 686, 682, 684, 694, 695, 
	694, 694, 695, 695, 695, 681, 687, 689, 
	697, 698, 695, 697, 694, 695, 695, 695, 
	686, 700, 702, 701, 703, 701, 703, 703, 
	703, 699, 705, 706, 701, 703, 701, 703, 
	703, 703, 704, 705, 360, 707, 708, 710, 
	707, 709, 710, 710, 710, 704, 705, 365, 
	711, 712, 714, 711, 713, 714, 714, 714, 
	704, 1, 370, 715, 705, 706, 713, 714, 
	713, 713, 714, 714, 714, 704, 705, 372, 
	716, 717, 714, 716, 713, 714, 714, 714, 
	704, 1, 97, 718, 96, 1, 97, 719, 
	96, 1, 97, 720, 96, 1, 97, 721, 
	96, 1, 97, 722, 96, 1, 97, 723, 
	96, 1, 97, 724, 96, 1, 97, 725, 
	96, 1, 97, 726, 726, 96, 728, 730, 
	729, 731, 729, 731, 731, 731, 727, 1, 
	97, 732, 735, 734, 732, 733, 734, 734, 
	734, 96, 728, 730, 736, 739, 738, 736, 
	737, 738, 738, 738, 727, 728, 730, 737, 
	738, 737, 737, 738, 738, 738, 727, 1, 
	97, 740, 741, 738, 740, 737, 738, 738, 
	738, 96, 743, 745, 744, 746, 744, 746, 
	746, 746, 742, 1, 400, 747, 748, 750, 
	747, 749, 750, 750, 750, 96, 743, 405, 
	751, 752, 754, 751, 753, 754, 754, 754, 
	742, 1, 410, 755, 743, 745, 753, 754, 
	753, 753, 754, 754, 754, 742, 1, 412, 
	756, 757, 754, 756, 753, 754, 754, 754, 
	96, 1, 97, 758, 96, 1, 97, 759, 
	96, 1, 97, 760, 760, 96, 1, 97, 
	761, 762, 761, 96, 1, 97, 762, 763, 
	762, 763, 763, 763, 96, 765, 767, 766, 
	768, 770, 766, 769, 770, 770, 770, 764, 
	765, 767, 771, 772, 774, 771, 773, 774, 
	774, 774, 764, 1, 430, 775, 776, 775, 
	96, 778, 434, 779, 780, 781, 779, 781, 
	781, 781, 777, 1, 430, 776, 1, 438, 
	782, 783, 785, 782, 784, 785, 785, 785, 
	96, 778, 434, 786, 780, 788, 786, 787, 
	788, 788, 788, 777, 778, 789, 787, 788, 
	787, 787, 788, 788, 788, 777, 1, 446, 
	790, 791, 788, 790, 787, 788, 788, 788, 
	96, 1, 97, 773, 774, 773, 773, 774, 
	774, 774, 96, 765, 767, 792, 793, 774, 
	792, 773, 774, 774, 774, 764, 794, 1, 
	99, 98, 100, 101, 102, 103, 104, 105, 
	106, 98, 96, 109, 108, 110, 111, 112, 
	113, 114, 115, 116, 108, 795, 0
};

static const short _checked_parse_test_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 0, 18, 62, 18, 18, 
	19, 20, 21, 22, 23, 24, 25, 24, 
	25, 0, 25, 26, 27, 28, 60, 61, 
	27, 28, 60, 61, 29, 30, 55, 0, 
	29, 30, 55, 56, 30, 30, 31, 32, 
	33, 34, 0, 35, 54, 35, 35, 36, 
	37, 38, 39, 40, 41, 42, 43, 44, 
	45, 46, 47, 48, 49, 50, 51, 52, 
	0, 428, 53, 57, 30, 55, 58, 59, 
	57, 58, 59, 57, 30, 55, 27, 28, 
	63, 429, 64, 430, 247, 248, 293, 321, 
	336, 354, 412, 429, 65, 65, 66, 67, 
	112, 140, 155, 173, 231, 429, 68, 69, 
	70, 71, 429, 71, 72, 73, 111, 429, 
	73, 74, 75, 76, 77, 110, 78, 78, 
	79, 80, 107, 81, 82, 83, 106, 83, 
	84, 103, 85, 86, 87, 102, 87, 88, 
	99, 89, 429, 90, 91, 98, 92, 429, 
	93, 429, 92, 429, 93, 94, 95, 429, 
	93, 96, 97, 95, 96, 97, 95, 429, 
	93, 100, 90, 91, 101, 104, 86, 87, 
	105, 108, 82, 83, 109, 113, 114, 115, 
	429, 116, 122, 117, 429, 117, 118, 119, 
	429, 120, 121, 119, 429, 120, 120, 429, 
	123, 124, 125, 126, 127, 128, 129, 130, 
	131, 132, 429, 133, 134, 139, 429, 135, 
	136, 429, 137, 138, 141, 142, 143, 144, 
	145, 146, 429, 147, 148, 146, 429, 147, 
	148, 429, 149, 152, 150, 151, 152, 153, 
	154, 151, 153, 154, 152, 151, 152, 156, 
	157, 158, 159, 160, 161, 160, 161, 161, 
	162, 163, 164, 171, 172, 163, 164, 171, 
	172, 165, 429, 166, 429, 165, 429, 166, 
	167, 168, 429, 166, 169, 170, 168, 169, 
	170, 168, 429, 166, 163, 164, 174, 175, 
	176, 177, 178, 194, 211, 179, 180, 181, 
	182, 429, 183, 429, 184, 185, 186, 187, 
	184, 185, 186, 187, 184, 187, 429, 188, 
	189, 429, 190, 429, 191, 192, 193, 190, 
	429, 191, 192, 193, 190, 429, 191, 195, 
	196, 197, 198, 199, 429, 199, 200, 429, 
	429, 201, 202, 203, 204, 201, 202, 203, 
	204, 201, 204, 429, 205, 206, 429, 207, 
	429, 208, 209, 210, 207, 429, 208, 209, 
	210, 208, 429, 207, 429, 208, 212, 213, 
	214, 215, 216, 217, 218, 219, 220, 429, 
	220, 221, 222, 223, 224, 225, 222, 223, 
	224, 225, 222, 225, 429, 225, 226, 227, 
	429, 228, 229, 230, 227, 429, 228, 229, 
	230, 228, 429, 227, 429, 228, 232, 233, 
	234, 234, 235, 236, 429, 237, 238, 245, 
	246, 237, 238, 245, 246, 239, 429, 240, 
	429, 239, 429, 240, 241, 242, 429, 240, 
	243, 244, 242, 243, 244, 242, 429, 240, 
	237, 238, 249, 250, 251, 252, 63, 0, 
	252, 429, 253, 254, 292, 63, 0, 254, 
	429, 255, 256, 257, 258, 291, 259, 259, 
	260, 261, 288, 262, 263, 264, 287, 264, 
	265, 284, 266, 267, 268, 283, 268, 269, 
	280, 270, 63, 0, 271, 429, 272, 279, 
	273, 274, 63, 0, 273, 274, 275, 276, 
	274, 277, 278, 276, 277, 278, 429, 276, 
	274, 281, 271, 272, 282, 285, 267, 268, 
	286, 289, 263, 264, 290, 294, 295, 296, 
	63, 0, 429, 297, 303, 298, 63, 0, 
	298, 429, 299, 300, 301, 302, 300, 301, 
	301, 304, 305, 306, 307, 308, 309, 310, 
	311, 312, 313, 63, 0, 429, 314, 315, 
	320, 63, 0, 429, 316, 317, 318, 319, 
	322, 323, 324, 325, 326, 327, 328, 329, 
	327, 328, 329, 63, 330, 429, 333, 331, 
	332, 333, 334, 335, 332, 334, 335, 333, 
	332, 333, 337, 338, 339, 340, 341, 342, 
	341, 342, 342, 343, 344, 345, 352, 353, 
	344, 345, 352, 353, 346, 347, 63, 346, 
	347, 348, 349, 347, 350, 351, 349, 350, 
	351, 429, 349, 347, 344, 345, 355, 356, 
	357, 358, 359, 375, 392, 360, 361, 362, 
	363, 63, 0, 429, 364, 63, 0, 365, 
	429, 366, 367, 368, 365, 366, 367, 368, 
	365, 368, 63, 0, 369, 429, 370, 63, 
	0, 429, 371, 372, 373, 374, 371, 372, 
	373, 374, 371, 372, 376, 377, 378, 379, 
	380, 63, 0, 380, 429, 381, 63, 0, 
	382, 429, 383, 384, 385, 382, 383, 384, 
	385, 382, 385, 63, 0, 386, 429, 387, 
	63, 0, 429, 388, 389, 390, 391, 388, 
	389, 390, 391, 389, 388, 389, 393, 394, 
	395, 396, 397, 398, 399, 400, 401, 63, 
	0, 401, 429, 402, 403, 404, 405, 406, 
	403, 404, 405, 406, 403, 406, 63, 0, 
	406, 429, 407, 408, 409, 410, 411, 408, 
	409, 410, 411, 409, 408, 409, 413, 414, 
	415, 415, 416, 417, 63, 0, 418, 429, 
	419, 426, 427, 418, 419, 426, 427, 420, 
	421, 63, 0, 420, 421, 422, 423, 421, 
	424, 425, 423, 424, 425, 429, 423, 421, 
	418, 419, 428, 429
};

static const short _checked_parse_test_trans_actions_wi[] = {
	0, 0, 1, 71, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 73, 241, 0, 0, 1, 
	79, 0, 0, 0, 0, 81, 81, 0, 
	0, 75, 75, 0, 131, 131, 13, 128, 
	0, 75, 0, 15, 0, 245, 0, 77, 
	77, 437, 77, 0, 0, 1, 83, 0, 
	0, 0, 85, 107, 0, 0, 1, 87, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	89, 253, 0, 134, 469, 134, 13, 128, 
	0, 0, 15, 19, 387, 19, 17, 17, 
	0, 116, 0, 218, 0, 41, 164, 91, 
	79, 373, 61, 105, 0, 1, 0, 41, 
	164, 91, 79, 373, 61, 113, 0, 0, 
	0, 0, 146, 33, 0, 21, 5, 149, 
	35, 0, 0, 0, 0, 5, 23, 0, 
	0, 0, 0, 0, 0, 25, 5, 0, 
	0, 0, 0, 0, 27, 5, 0, 0, 
	0, 0, 152, 0, 29, 5, 0, 229, 
	0, 155, 39, 402, 39, 0, 265, 499, 
	265, 13, 128, 0, 0, 15, 137, 487, 
	137, 0, 11, 125, 5, 0, 11, 122, 
	5, 0, 11, 119, 5, 0, 0, 0, 
	158, 43, 45, 0, 161, 47, 0, 31, 
	277, 31, 5, 47, 301, 47, 0, 110, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 167, 0, 0, 5, 170, 0, 
	0, 221, 0, 9, 0, 0, 0, 0, 
	0, 93, 447, 93, 93, 0, 257, 0, 
	0, 206, 75, 75, 0, 131, 131, 13, 
	128, 0, 0, 15, 0, 17, 17, 0, 
	0, 0, 0, 81, 81, 0, 0, 75, 
	0, 131, 131, 13, 128, 0, 75, 0, 
	15, 0, 249, 0, 209, 77, 442, 77, 
	0, 134, 475, 134, 13, 128, 0, 0, 
	15, 19, 392, 19, 17, 17, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 176, 0, 321, 131, 13, 128, 131, 
	0, 0, 15, 0, 17, 17, 325, 0, 
	0, 182, 134, 457, 134, 13, 128, 0, 
	225, 0, 0, 15, 19, 377, 19, 0, 
	0, 0, 0, 0, 194, 65, 0, 203, 
	345, 131, 13, 128, 269, 0, 0, 15, 
	65, 17, 140, 353, 67, 0, 197, 134, 
	506, 273, 13, 128, 0, 427, 67, 0, 
	15, 0, 237, 19, 493, 143, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 212, 
	95, 0, 131, 13, 128, 131, 0, 0, 
	15, 95, 17, 17, 215, 97, 0, 134, 
	481, 134, 13, 128, 0, 452, 97, 0, 
	15, 0, 261, 19, 397, 19, 0, 0, 
	63, 0, 0, 0, 185, 131, 131, 13, 
	128, 0, 0, 0, 15, 0, 233, 0, 
	188, 59, 417, 59, 0, 134, 463, 134, 
	13, 128, 0, 0, 15, 19, 382, 19, 
	17, 17, 0, 0, 0, 0, 33, 33, 
	33, 281, 0, 21, 5, 35, 35, 35, 
	285, 0, 0, 0, 0, 5, 23, 0, 
	0, 0, 0, 0, 0, 25, 5, 0, 
	0, 0, 0, 0, 27, 5, 0, 0, 
	0, 0, 37, 37, 0, 289, 29, 5, 
	0, 0, 39, 39, 39, 39, 0, 265, 
	265, 13, 128, 0, 0, 15, 293, 137, 
	137, 0, 11, 125, 5, 0, 11, 122, 
	5, 0, 11, 119, 5, 0, 0, 0, 
	45, 45, 297, 43, 45, 0, 47, 47, 
	47, 305, 0, 31, 31, 5, 47, 47, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 49, 49, 309, 0, 0, 
	5, 51, 51, 313, 0, 0, 0, 9, 
	0, 0, 0, 0, 0, 93, 93, 93, 
	0, 0, 0, 75, 75, 357, 75, 0, 
	131, 131, 13, 128, 0, 0, 15, 0, 
	17, 17, 0, 0, 0, 0, 81, 81, 
	0, 0, 75, 0, 131, 131, 13, 128, 
	0, 75, 0, 15, 0, 0, 77, 77, 
	77, 0, 134, 134, 13, 128, 0, 0, 
	15, 361, 19, 19, 17, 17, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 53, 53, 317, 0, 173, 173, 131, 
	407, 13, 128, 131, 0, 0, 15, 0, 
	17, 17, 179, 179, 0, 412, 0, 55, 
	55, 329, 134, 134, 13, 128, 0, 0, 
	0, 15, 19, 19, 0, 0, 0, 0, 
	0, 65, 65, 65, 341, 0, 191, 191, 
	131, 422, 13, 128, 269, 0, 0, 15, 
	65, 17, 140, 200, 200, 67, 432, 0, 
	67, 67, 349, 134, 273, 13, 128, 0, 
	67, 0, 15, 0, 19, 143, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 95, 
	95, 95, 365, 0, 131, 13, 128, 131, 
	0, 0, 15, 95, 17, 17, 97, 97, 
	97, 369, 0, 134, 134, 13, 128, 0, 
	97, 0, 15, 0, 19, 19, 0, 0, 
	63, 0, 0, 0, 57, 57, 131, 333, 
	131, 13, 128, 0, 0, 0, 15, 0, 
	0, 59, 59, 59, 59, 0, 134, 134, 
	13, 128, 0, 0, 15, 337, 19, 19, 
	17, 17, 0, 103
};

static const short _checked_parse_test_to_state_actions[] = {
	0, 99, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 99, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 99, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	3, 0, 0, 3, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 3, 0, 0, 
	0, 3, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 7, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 0, 
	3, 0, 0, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 3, 0, 0, 
	0, 3, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 3, 0, 7, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 99, 99, 0
};

static const short _checked_parse_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 101, 0
};

static const short _checked_parse_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 73, 0, 0, 0, 0, 0, 0, 
	0, 75, 0, 75, 0, 77, 0, 0, 
	0, 0, 85, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 89, 89, 85, 0, 
	0, 77, 77, 0, 75, 0, 73, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 33, 0, 35, 35, 
	35, 35, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 37, 37, 
	0, 39, 0, 0, 39, 39, 0, 37, 
	0, 37, 37, 0, 0, 0, 0, 0, 
	0, 0, 0, 35, 0, 0, 0, 0, 
	45, 0, 47, 0, 47, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 49, 49, 51, 51, 0, 0, 51, 
	49, 0, 0, 0, 0, 0, 0, 0, 
	0, 75, 75, 0, 75, 0, 75, 0, 
	0, 0, 0, 0, 0, 0, 75, 0, 
	75, 0, 77, 0, 0, 77, 77, 0, 
	75, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 53, 173, 173, 53, 173, 
	179, 55, 55, 55, 0, 55, 55, 0, 
	0, 0, 0, 0, 65, 69, 191, 65, 
	69, 200, 67, 0, 67, 0, 67, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 95, 0, 95, 95, 0, 97, 0, 
	97, 0, 97, 0, 0, 0, 0, 0, 
	0, 57, 57, 0, 59, 0, 0, 59, 
	59, 0, 0, 57, 0, 0, 0
};

static const short _checked_parse_test_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 108, 108, 108, 108, 108, 108, 123, 
	108, 128, 128, 128, 128, 108, 108, 108, 
	108, 108, 108, 108, 108, 108, 108, 108, 
	108, 155, 155, 108, 162, 108, 108, 162, 
	162, 108, 155, 108, 155, 155, 108, 108, 
	108, 108, 108, 108, 108, 108, 128, 108, 
	108, 108, 108, 193, 108, 197, 108, 197, 
	108, 108, 108, 108, 108, 108, 108, 108, 
	108, 108, 108, 108, 219, 219, 223, 223, 
	108, 108, 223, 219, 108, 108, 108, 108, 
	108, 108, 108, 108, 242, 242, 108, 242, 
	108, 242, 108, 108, 108, 108, 108, 108, 
	108, 242, 108, 242, 108, 277, 108, 108, 
	277, 277, 108, 242, 108, 108, 108, 108, 
	108, 108, 108, 108, 108, 108, 306, 308, 
	308, 306, 308, 319, 322, 322, 322, 108, 
	322, 322, 108, 108, 108, 108, 108, 341, 
	344, 345, 341, 344, 356, 359, 108, 359, 
	108, 359, 108, 108, 108, 108, 108, 108, 
	108, 108, 108, 108, 384, 108, 384, 384, 
	108, 397, 108, 397, 108, 397, 108, 108, 
	108, 108, 108, 108, 421, 421, 108, 433, 
	108, 108, 433, 433, 108, 108, 421, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 796
};

static const int checked_parse_test_start = 1;
static const int checked_parse_test_first_final = 428;
static const int checked_parse_test_error = 0;

static const int checked_parse_test_en_checked_group_scanner = 429;
static const int checked_parse_test_en_main = 1;

#line 1007 "NanorexMMPImportExportTest.rl"
	
#line 7743 "NanorexMMPImportExportTest.cpp"
	{
	cs = checked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1008 "NanorexMMPImportExportTest.rl"
	
#line 7753 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _checked_parse_test_actions + _checked_parse_test_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 71:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 7774 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _checked_parse_test_trans_keys + _checked_parse_test_key_offsets[cs];
	_trans = _checked_parse_test_index_offsets[cs];

	_klen = _checked_parse_test_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _checked_parse_test_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _checked_parse_test_indicies[_trans];
_eof_trans:
	cs = _checked_parse_test_trans_targs_wi[_trans];

	if ( _checked_parse_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _checked_parse_test_actions + _checked_parse_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 16:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 17:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 18:
#line 30 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed integer"); }
	break;
	case 19:
#line 35 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed atomic number"); }
	break;
	case 20:
#line 41 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed coordinates"); }
	break;
	case 21:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
/*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 22:
#line 50 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed atom-style specification"); }
	break;
	case 23:
#line 55 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 24:
#line 62 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 25:
#line 69 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 26:
#line 70 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-specification - " + stringVal); }
	break;
	case 27:
#line 76 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-target atom id"); }
	break;
	case 28:
#line 80 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 29:
#line 88 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 30:
#line 91 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 31:
#line 94 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 32:
#line 101 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 33:
#line 104 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 34:
#line 106 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting '=' after key"); }
	break;
	case 35:
#line 108 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 36:
#line 17 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed molecule name"); }
	break;
	case 37:
#line 22 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed molecule style"); }
	break;
	case 38:
#line 26 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 39:
#line 27 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* style is optional */ }
	break;
	case 40:
#line 34 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 41:
#line 43 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 42:
#line 48 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 43:
#line 52 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 44:
#line 58 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expected '=' in assignment"); }
	break;
	case 45:
#line 63 "NanorexMMPImportExportTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 46:
#line 24 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 47:
#line 28 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 48:
#line 29 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (View Data)' statement"); }
	break;
	case 49:
#line 34 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed group-name"); }
	break;
	case 50:
#line 39 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed group-style"); }
	break;
	case 51:
#line 43 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 52:
#line 43 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 53:
#line 49 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 54:
#line 54 "NanorexMMPImportExportTest.rl"
	{lineStart = p;}
	break;
	case 55:
#line 57 "NanorexMMPImportExportTest.rl"
	{ end1(); }
	break;
	case 56:
#line 58 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 57:
#line 62 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 58:
#line 66 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 59:
#line 67 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 60:
#line 72 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 61:
#line 72 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 62:
#line 78 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 63:
#line 83 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 64:
#line 88 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
	case 65:
#line 92 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 66:
#line 103 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 67:
#line 979 "NanorexMMPImportExportTest.rl"
	{ cerr << "*p=" << *p << endl;
			p--;
			{stack[top++] = cs; cs = 429; goto _again;}
		}
	break;
	case 68:
#line 985 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 429; goto _again;} }
	break;
	case 69:
#line 990 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 429; goto _again;} }
	break;
	case 72:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 73:
#line 109 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 74:
#line 110 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 75:
#line 112 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 76:
#line 113 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 77:
#line 114 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 78:
#line 115 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 79:
#line 116 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 80:
#line 117 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 81:
#line 118 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 82:
#line 121 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 83:
#line 123 "NanorexMMPImportExportTest.rl"
	{te = p+1;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 84:
#line 123 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 85:
#line 123 "NanorexMMPImportExportTest.rl"
	{{p = ((te))-1;}{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
#line 8198 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _checked_parse_test_actions + _checked_parse_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 70:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
#line 8219 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _checked_parse_test_eof_trans[cs] > 0 ) {
		_trans = _checked_parse_test_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	const char *__acts = _checked_parse_test_actions + _checked_parse_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 18:
#line 30 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed integer"); }
	break;
	case 19:
#line 35 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed atomic number"); }
	break;
	case 20:
#line 41 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed coordinates"); }
	break;
	case 22:
#line 50 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed atom-style specification"); }
	break;
	case 26:
#line 70 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-specification - " + stringVal); }
	break;
	case 27:
#line 76 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-target atom id"); }
	break;
	case 30:
#line 91 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 31:
#line 94 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 33:
#line 104 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 34:
#line 106 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting '=' after key"); }
	break;
	case 35:
#line 108 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 36:
#line 17 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed molecule name"); }
	break;
	case 37:
#line 22 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed molecule style"); }
	break;
	case 41:
#line 43 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 42:
#line 48 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 44:
#line 58 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expected '=' in assignment"); }
	break;
	case 48:
#line 29 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (View Data)' statement"); }
	break;
	case 49:
#line 34 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed group-name"); }
	break;
	case 50:
#line 39 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed group-style"); }
	break;
	case 56:
#line 58 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 59:
#line 67 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 63:
#line 83 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 64:
#line 88 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
#line 8330 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 1009 "NanorexMMPImportExportTest.rl"
}


void
NanorexMMPImportExportTest::
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


void NanorexMMPImportExportTest::charBufParseTest(void)
{
	charBufParseTestVanillin();
}


#line 1089 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::charBufParseTestVanillin(void)
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
NanorexMMPImportExportTest::charBufParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[1024], top, act;
	
	#line 1176 "NanorexMMPImportExportTest.rl"
	
#line 8461 "NanorexMMPImportExportTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 28, 1, 31, 1, 33, 1, 
	34, 1, 38, 1, 42, 1, 44, 1, 
	58, 1, 59, 2, 0, 30, 2, 0, 
	54, 2, 0, 56, 2, 0, 57, 2, 
	5, 12, 2, 5, 13, 2, 5, 14, 
	2, 6, 7, 2, 6, 8, 2, 6, 
	9, 2, 8, 15, 2, 36, 24, 2, 
	38, 0, 2, 42, 43, 3, 0, 16, 
	52, 3, 0, 19, 55, 3, 0, 20, 
	53, 3, 0, 23, 50, 3, 0, 25, 
	51, 3, 0, 27, 39, 3, 0, 29, 
	40, 3, 0, 29, 47, 3, 0, 32, 
	41, 3, 0, 35, 49, 3, 0, 37, 
	48, 3, 6, 8, 15, 3, 17, 0, 
	54, 3, 45, 0, 46, 4, 9, 0, 
	20, 53, 4, 9, 0, 23, 50, 4, 
	9, 0, 25, 51, 4, 9, 0, 29, 
	40, 4, 9, 0, 29, 47, 4, 9, 
	0, 37, 48, 4, 34, 0, 35, 49, 
	5, 6, 9, 0, 20, 53, 5, 6, 
	9, 0, 23, 50, 5, 6, 9, 0, 
	25, 51, 5, 6, 9, 0, 29, 40, 
	5, 6, 9, 0, 29, 47, 5, 6, 
	9, 0, 37, 48, 5, 8, 15, 0, 
	16, 52, 6, 6, 8, 15, 0, 16, 
	52
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 102, 107, 108, 
	109, 110, 111, 116, 121, 132, 146, 160, 
	165, 177, 182, 183, 184, 185, 190, 195, 
	196, 197, 198, 199, 204, 209, 210, 211, 
	212, 213, 214, 215, 216, 217, 222, 227, 
	232, 233, 234, 238, 240, 242, 244, 258, 
	272, 285, 299, 312, 326, 328, 329, 330, 
	331, 332, 333, 337, 343, 350, 355, 360, 
	362, 369, 371, 375, 381, 383, 385, 387, 
	389, 391, 395, 400, 401, 402, 403, 404, 
	405, 406, 407, 408, 413, 415, 426, 429, 
	432, 435, 440, 447, 454, 460, 467, 475, 
	481, 486, 492, 501, 505, 513, 519, 528, 
	532, 540, 546, 555, 559, 567, 573, 579, 
	592, 594, 609, 624, 638, 653, 661, 665, 
	673, 681, 689, 693, 701, 709, 717, 721, 
	729, 737, 745, 752, 755, 758, 761, 769, 
	774, 781, 789, 797, 799, 807, 810, 813, 
	816, 819, 822, 825, 828, 831, 834, 839, 
	846, 853, 860, 868, 874, 876, 884, 891, 
	894, 897, 900, 903, 906, 913, 920, 922, 
	935, 947, 962, 977, 983, 997, 1012, 1015, 
	1018, 1021, 1024, 1030, 1036, 1048, 1063, 1078, 
	1084, 1097, 1099, 1114, 1129, 1143, 1158, 1172, 
	1187, 1190, 1193, 1196, 1201, 1209, 1212, 1215, 
	1218, 1223, 1235, 1250, 1265, 1279, 1294, 1306, 
	1321, 1336, 1338, 1352, 1367, 1370, 1373, 1376, 
	1379, 1384, 1396, 1411, 1426, 1440, 1455, 1467, 
	1482, 1497, 1499, 1513, 1528, 1531, 1534, 1537, 
	1540, 1543, 1546, 1549, 1552, 1557, 1569, 1584, 
	1599, 1613, 1628, 1640, 1655, 1670, 1672, 1686, 
	1701, 1704, 1707, 1712, 1718, 1730, 1745, 1760, 
	1766, 1779, 1781, 1796, 1811, 1825, 1840, 1854, 
	1869, 1871, 1871, 1883
};

static const char _parse_tester_trans_keys[] = {
	10, 32, 109, 9, 13, 109, 112, 102, 
	111, 114, 109, 97, 116, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 48, 
	57, 48, 57, 48, 57, 48, 57, 48, 
	57, 9, 32, 11, 13, 9, 32, 114, 
	11, 13, 101, 113, 117, 105, 114, 101, 
	100, 10, 32, 35, 59, 9, 13, 10, 
	32, 103, 107, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	40, 11, 13, 9, 32, 86, 11, 13, 
	105, 101, 119, 9, 32, 11, 13, 9, 
	32, 68, 11, 13, 97, 116, 97, 9, 
	32, 41, 11, 13, 10, 35, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 40, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 41, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 41, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 9, 13, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 101, 9, 13, 110, 100, 
	49, 10, 32, 35, 9, 13, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 67, 11, 
	13, 108, 105, 112, 98, 111, 97, 114, 
	100, 9, 32, 41, 11, 13, 10, 32, 
	35, 9, 13, 10, 32, 101, 9, 13, 
	110, 100, 9, 32, 11, 13, -1, 10, 
	-1, 10, -1, 10, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	101, 108, 118, 105, 110, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 10, 
	32, 35, 9, 13, 48, 57, 10, 32, 
	35, 9, 13, 10, 32, 103, 9, 13, 
	-1, 10, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 9, 32, 11, 13, 9, 
	32, 11, 13, 48, 57, 48, 57, 48, 
	57, 48, 57, 48, 57, 48, 57, 9, 
	32, 11, 13, 9, 32, 112, 11, 13, 
	114, 101, 102, 101, 114, 114, 101, 100, 
	10, 32, 35, 9, 13, -1, 10, -1, 
	10, 32, 97, 98, 101, 103, 105, 109, 
	9, 13, -1, 10, 116, -1, 10, 111, 
	-1, 10, 109, -1, 10, 32, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, -1, 
	10, 32, 43, 45, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	35, 9, 13, -1, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	100, -1, 10, 95, 97, 99, 103, 49, 
	51, -1, 10, 32, 9, 13, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, -1, 
	10, 32, 35, 9, 13, 48, 57, -1, 
	10, 100, -1, 10, 105, -1, 10, 114, 
	-1, 10, 101, -1, 10, 99, -1, 10, 
	116, -1, 10, 105, -1, 10, 111, -1, 
	10, 110, -1, 10, 32, 9, 13, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 35, 40, 9, 
	13, -1, 10, 32, 35, 40, 9, 13, 
	-1, 10, -1, 10, 32, 41, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 110, -1, 10, 
	102, -1, 10, 111, -1, 10, 32, 9, 
	13, -1, 10, 32, 97, 99, 111, 9, 
	13, -1, 10, 116, -1, 10, 111, -1, 
	10, 109, -1, 10, 32, 9, 13, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 61, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 104, -1, 10, 117, -1, 10, 110, 
	-1, 10, 107, -1, 10, 32, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 112, -1, 10, 101, -1, 10, 
	110, -1, 10, 103, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 111, 
	-1, 10, 108, -1, 10, 32, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 97, 98, 101, 103, 105, 
	109, 9, 13, -1, 10, 32, 97, 98, 
	101, 103, 105, 109, 9, 13, 0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 2, 3, 1, 1, 
	1, 1, 3, 3, 3, 4, 4, 3, 
	4, 3, 1, 1, 1, 3, 3, 1, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 3, 3, 
	1, 1, 2, 2, 2, 2, 4, 4, 
	3, 4, 3, 4, 2, 1, 1, 1, 
	1, 1, 2, 2, 3, 3, 3, 2, 
	3, 2, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 2, 9, 3, 3, 
	3, 3, 3, 3, 4, 3, 4, 4, 
	3, 4, 5, 2, 4, 4, 5, 2, 
	4, 4, 5, 2, 4, 4, 4, 5, 
	2, 5, 5, 4, 5, 4, 2, 4, 
	4, 4, 2, 4, 4, 4, 2, 4, 
	4, 4, 3, 3, 3, 3, 6, 3, 
	3, 4, 4, 2, 4, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 4, 4, 2, 4, 3, 3, 
	3, 3, 3, 3, 5, 5, 2, 5, 
	4, 5, 5, 4, 4, 5, 3, 3, 
	3, 3, 4, 4, 4, 5, 5, 4, 
	5, 2, 5, 5, 4, 5, 4, 5, 
	3, 3, 3, 3, 6, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 4, 4, 5, 5, 4, 
	5, 2, 5, 5, 4, 5, 4, 5, 
	2, 0, 10, 9
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 1, 0, 0, 0, 1, 1, 0, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 1, 1, 
	0, 0, 1, 0, 0, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 0, 0, 
	0, 0, 1, 2, 2, 1, 1, 0, 
	2, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 1, 2, 2, 1, 2, 2, 1, 
	1, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 1, 4, 
	0, 5, 5, 5, 5, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 2, 0, 0, 0, 1, 1, 
	2, 2, 2, 0, 2, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 1, 2, 
	2, 2, 2, 1, 0, 2, 2, 0, 
	0, 0, 0, 0, 1, 1, 0, 4, 
	4, 5, 5, 1, 5, 5, 0, 0, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 0, 5, 5, 5, 5, 5, 5, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 0, 5, 5, 5, 5, 5, 5, 
	0, 0, 1, 1
};

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 127, 132, 134, 
	136, 138, 140, 145, 150, 158, 168, 178, 
	183, 192, 197, 199, 201, 203, 208, 213, 
	215, 217, 219, 221, 226, 231, 233, 235, 
	237, 239, 241, 243, 245, 247, 252, 257, 
	262, 264, 266, 270, 273, 276, 279, 289, 
	299, 308, 318, 327, 337, 340, 342, 344, 
	346, 348, 350, 354, 359, 365, 370, 375, 
	378, 384, 387, 391, 396, 398, 400, 402, 
	404, 406, 410, 415, 417, 419, 421, 423, 
	425, 427, 429, 431, 436, 439, 450, 454, 
	458, 462, 467, 473, 479, 485, 491, 498, 
	504, 509, 515, 523, 527, 534, 540, 548, 
	552, 559, 565, 573, 577, 584, 590, 596, 
	606, 609, 620, 631, 641, 652, 659, 663, 
	670, 677, 684, 688, 695, 702, 709, 713, 
	720, 727, 734, 740, 744, 748, 752, 760, 
	765, 771, 778, 785, 788, 795, 799, 803, 
	807, 811, 815, 819, 823, 827, 831, 836, 
	842, 848, 854, 861, 867, 870, 877, 883, 
	887, 891, 895, 899, 903, 910, 917, 920, 
	930, 939, 950, 961, 967, 977, 988, 992, 
	996, 1000, 1004, 1010, 1016, 1025, 1036, 1047, 
	1053, 1063, 1066, 1077, 1088, 1098, 1109, 1119, 
	1130, 1134, 1138, 1142, 1147, 1155, 1159, 1163, 
	1167, 1172, 1181, 1192, 1203, 1213, 1224, 1233, 
	1244, 1255, 1258, 1268, 1279, 1283, 1287, 1291, 
	1295, 1300, 1309, 1320, 1331, 1341, 1352, 1361, 
	1372, 1383, 1386, 1396, 1407, 1411, 1415, 1419, 
	1423, 1427, 1431, 1435, 1439, 1444, 1453, 1464, 
	1475, 1485, 1496, 1505, 1516, 1527, 1530, 1540, 
	1551, 1555, 1559, 1564, 1570, 1579, 1590, 1601, 
	1607, 1617, 1620, 1631, 1642, 1652, 1663, 1673, 
	1684, 1687, 1688, 1700
};

static const short _parse_tester_indicies[] = {
	2, 0, 3, 0, 1, 4, 1, 5, 
	1, 6, 1, 7, 1, 8, 1, 9, 
	1, 10, 1, 11, 1, 12, 12, 12, 
	1, 12, 12, 12, 13, 1, 14, 1, 
	15, 1, 16, 1, 17, 1, 18, 1, 
	19, 19, 19, 1, 19, 19, 20, 19, 
	1, 21, 1, 22, 1, 23, 1, 24, 
	1, 25, 1, 26, 1, 27, 1, 28, 
	27, 29, 30, 27, 1, 28, 31, 32, 
	33, 31, 1, 34, 1, 35, 1, 36, 
	1, 37, 1, 38, 38, 39, 38, 1, 
	40, 40, 41, 40, 1, 41, 41, 42, 
	41, 1, 43, 1, 44, 1, 45, 1, 
	46, 46, 46, 1, 46, 46, 47, 46, 
	1, 48, 1, 49, 1, 50, 1, 50, 
	50, 51, 50, 1, 52, 53, 1, 55, 
	54, 56, 54, 1, 57, 1, 58, 1, 
	59, 1, 60, 1, 61, 61, 62, 61, 
	1, 63, 63, 64, 63, 1, 64, 64, 
	65, 64, 65, 65, 65, 1, 66, 66, 
	67, 69, 66, 68, 69, 69, 69, 1, 
	70, 70, 71, 73, 70, 72, 73, 73, 
	73, 1, 75, 74, 76, 74, 1, 75, 
	74, 76, 77, 74, 77, 77, 77, 1, 
	79, 78, 80, 78, 1, 81, 1, 82, 
	1, 83, 1, 84, 83, 85, 83, 1, 
	87, 86, 88, 86, 1, 89, 1, 90, 
	1, 91, 1, 92, 1, 92, 92, 93, 
	92, 1, 93, 93, 94, 93, 1, 95, 
	1, 96, 1, 97, 1, 98, 1, 99, 
	1, 100, 1, 101, 1, 102, 1, 102, 
	102, 103, 102, 1, 104, 103, 105, 103, 
	1, 107, 106, 108, 106, 1, 109, 1, 
	110, 1, 111, 111, 111, 1, 1, 104, 
	105, 1, 84, 85, 1, 75, 76, 113, 
	112, 114, 116, 112, 115, 116, 116, 116, 
	1, 75, 117, 76, 119, 117, 118, 119, 
	119, 119, 1, 118, 118, 119, 118, 118, 
	119, 119, 119, 1, 121, 120, 122, 119, 
	120, 118, 119, 119, 119, 1, 72, 72, 
	73, 72, 72, 73, 73, 73, 1, 123, 
	123, 124, 73, 123, 72, 73, 73, 73, 
	1, 1, 52, 53, 125, 1, 126, 1, 
	127, 1, 128, 1, 129, 1, 130, 130, 
	130, 1, 130, 130, 130, 131, 1, 133, 
	132, 134, 132, 135, 1, 137, 136, 138, 
	136, 1, 137, 139, 32, 139, 1, 1, 
	137, 138, 133, 132, 134, 132, 135, 1, 
	1, 28, 29, 140, 140, 140, 1, 140, 
	140, 140, 141, 1, 142, 1, 143, 1, 
	144, 1, 145, 1, 146, 1, 147, 147, 
	147, 1, 147, 147, 148, 147, 1, 149, 
	1, 150, 1, 151, 1, 152, 1, 153, 
	1, 154, 1, 155, 1, 156, 1, 28, 
	156, 29, 156, 1, 157, 159, 158, 157, 
	161, 160, 162, 163, 164, 165, 166, 167, 
	160, 158, 157, 159, 168, 158, 157, 159, 
	169, 158, 157, 159, 170, 158, 157, 159, 
	171, 171, 158, 157, 159, 171, 171, 172, 
	158, 157, 159, 173, 173, 174, 158, 157, 
	159, 175, 176, 175, 158, 157, 159, 176, 
	176, 177, 158, 157, 159, 178, 179, 178, 
	180, 158, 157, 159, 178, 179, 178, 158, 
	157, 159, 181, 181, 158, 157, 159, 182, 
	183, 182, 158, 157, 159, 183, 184, 185, 
	183, 186, 158, 157, 159, 186, 158, 157, 
	159, 187, 188, 187, 189, 158, 157, 159, 
	187, 188, 187, 158, 157, 159, 190, 191, 
	192, 190, 193, 158, 157, 159, 193, 158, 
	157, 159, 194, 195, 194, 196, 158, 157, 
	159, 194, 195, 194, 158, 157, 159, 197, 
	198, 199, 197, 200, 158, 157, 159, 200, 
	158, 157, 159, 201, 202, 201, 203, 158, 
	157, 159, 201, 202, 201, 158, 157, 205, 
	204, 206, 204, 158, 157, 205, 204, 206, 
	207, 204, 207, 207, 207, 158, 157, 205, 
	206, 157, 209, 208, 210, 212, 208, 211, 
	212, 212, 212, 158, 157, 205, 213, 206, 
	215, 213, 214, 215, 215, 215, 158, 157, 
	159, 214, 215, 214, 214, 215, 215, 215, 
	158, 157, 217, 216, 218, 215, 216, 214, 
	215, 215, 215, 158, 157, 159, 201, 202, 
	201, 203, 158, 157, 159, 219, 158, 157, 
	159, 220, 221, 220, 222, 158, 157, 159, 
	220, 221, 220, 222, 158, 157, 159, 194, 
	195, 194, 196, 158, 157, 159, 223, 158, 
	157, 159, 224, 225, 224, 226, 158, 157, 
	159, 224, 225, 224, 226, 158, 157, 159, 
	187, 188, 187, 189, 158, 157, 159, 227, 
	158, 157, 159, 228, 229, 228, 230, 158, 
	157, 159, 228, 229, 228, 230, 158, 157, 
	159, 178, 179, 178, 180, 158, 157, 159, 
	173, 173, 174, 158, 157, 159, 231, 158, 
	157, 159, 232, 158, 157, 159, 233, 158, 
	157, 159, 235, 234, 234, 234, 234, 158, 
	157, 159, 236, 236, 158, 157, 159, 236, 
	236, 237, 158, 157, 239, 238, 240, 238, 
	241, 158, 157, 243, 242, 244, 242, 237, 
	158, 157, 243, 244, 157, 239, 238, 240, 
	238, 241, 158, 157, 159, 245, 158, 157, 
	159, 246, 158, 157, 159, 247, 158, 157, 
	159, 248, 158, 157, 159, 249, 158, 157, 
	159, 250, 158, 157, 159, 251, 158, 157, 
	159, 252, 158, 157, 159, 253, 158, 157, 
	159, 254, 254, 158, 157, 159, 254, 254, 
	255, 158, 157, 159, 256, 256, 257, 158, 
	157, 159, 256, 256, 258, 158, 157, 260, 
	259, 261, 259, 262, 158, 157, 260, 259, 
	261, 259, 158, 157, 260, 261, 157, 260, 
	259, 261, 259, 262, 158, 157, 159, 256, 
	256, 257, 158, 157, 159, 263, 158, 157, 
	159, 264, 158, 157, 159, 265, 158, 157, 
	159, 266, 158, 157, 159, 267, 158, 157, 
	269, 268, 270, 271, 268, 158, 157, 273, 
	272, 274, 275, 272, 158, 157, 273, 274, 
	157, 159, 276, 277, 278, 276, 278, 278, 
	278, 158, 157, 159, 276, 278, 276, 278, 
	278, 278, 158, 157, 159, 279, 280, 282, 
	279, 281, 282, 282, 282, 158, 157, 159, 
	283, 277, 285, 283, 284, 285, 285, 285, 
	158, 157, 273, 277, 274, 277, 158, 157, 
	159, 284, 285, 284, 284, 285, 285, 285, 
	158, 157, 159, 286, 287, 285, 286, 284, 
	285, 285, 285, 158, 157, 159, 288, 158, 
	157, 159, 289, 158, 157, 159, 290, 158, 
	157, 159, 291, 158, 157, 159, 292, 293, 
	292, 158, 157, 159, 294, 295, 294, 158, 
	157, 159, 295, 296, 295, 296, 296, 296, 
	158, 157, 159, 297, 298, 300, 297, 299, 
	300, 300, 300, 158, 157, 159, 301, 302, 
	304, 301, 303, 304, 304, 304, 158, 157, 
	306, 305, 307, 305, 158, 157, 306, 305, 
	307, 308, 305, 308, 308, 308, 158, 157, 
	306, 307, 157, 310, 309, 311, 313, 309, 
	312, 313, 313, 313, 158, 157, 306, 314, 
	307, 316, 314, 315, 316, 316, 316, 158, 
	157, 159, 315, 316, 315, 315, 316, 316, 
	316, 158, 157, 318, 317, 319, 316, 317, 
	315, 316, 316, 316, 158, 157, 159, 303, 
	304, 303, 303, 304, 304, 304, 158, 157, 
	159, 320, 321, 304, 320, 303, 304, 304, 
	304, 158, 157, 159, 322, 158, 157, 159, 
	323, 158, 157, 159, 324, 158, 157, 159, 
	325, 325, 158, 157, 159, 325, 326, 327, 
	328, 325, 158, 157, 159, 329, 158, 157, 
	159, 330, 158, 157, 159, 331, 158, 157, 
	159, 332, 332, 158, 157, 159, 332, 333, 
	332, 333, 333, 333, 158, 157, 159, 334, 
	337, 336, 334, 335, 336, 336, 336, 158, 
	157, 159, 338, 341, 340, 338, 339, 340, 
	340, 340, 158, 157, 159, 339, 340, 339, 
	339, 340, 340, 340, 158, 157, 159, 342, 
	343, 340, 342, 339, 340, 340, 340, 158, 
	157, 159, 341, 344, 341, 344, 344, 344, 
	158, 157, 346, 345, 347, 349, 345, 348, 
	349, 349, 349, 158, 157, 351, 350, 352, 
	354, 350, 353, 354, 354, 354, 158, 157, 
	351, 352, 157, 159, 353, 354, 353, 353, 
	354, 354, 354, 158, 157, 356, 355, 357, 
	354, 355, 353, 354, 354, 354, 158, 157, 
	159, 358, 158, 157, 159, 359, 158, 157, 
	159, 360, 158, 157, 159, 361, 158, 157, 
	159, 362, 362, 158, 157, 159, 362, 363, 
	362, 363, 363, 363, 158, 157, 159, 364, 
	367, 366, 364, 365, 366, 366, 366, 158, 
	157, 159, 368, 371, 370, 368, 369, 370, 
	370, 370, 158, 157, 159, 369, 370, 369, 
	369, 370, 370, 370, 158, 157, 159, 372, 
	373, 370, 372, 369, 370, 370, 370, 158, 
	157, 159, 371, 374, 371, 374, 374, 374, 
	158, 157, 376, 375, 377, 379, 375, 378, 
	379, 379, 379, 158, 157, 381, 380, 382, 
	384, 380, 383, 384, 384, 384, 158, 157, 
	381, 382, 157, 159, 383, 384, 383, 383, 
	384, 384, 384, 158, 157, 386, 385, 387, 
	384, 385, 383, 384, 384, 384, 158, 157, 
	159, 388, 158, 157, 159, 389, 158, 157, 
	159, 390, 158, 157, 159, 391, 158, 157, 
	159, 392, 158, 157, 159, 393, 158, 157, 
	159, 394, 158, 157, 159, 395, 158, 157, 
	159, 396, 396, 158, 157, 159, 396, 397, 
	396, 397, 397, 397, 158, 157, 159, 398, 
	401, 400, 398, 399, 400, 400, 400, 158, 
	157, 159, 402, 405, 404, 402, 403, 404, 
	404, 404, 158, 157, 159, 403, 404, 403, 
	403, 404, 404, 404, 158, 157, 159, 406, 
	407, 404, 406, 403, 404, 404, 404, 158, 
	157, 159, 405, 408, 405, 408, 408, 408, 
	158, 157, 410, 409, 411, 413, 409, 412, 
	413, 413, 413, 158, 157, 415, 414, 416, 
	418, 414, 417, 418, 418, 418, 158, 157, 
	415, 416, 157, 159, 417, 418, 417, 417, 
	418, 418, 418, 158, 157, 420, 419, 421, 
	418, 419, 417, 418, 418, 418, 158, 157, 
	159, 422, 158, 157, 159, 423, 158, 157, 
	159, 424, 424, 158, 157, 159, 424, 425, 
	424, 158, 157, 159, 425, 426, 425, 426, 
	426, 426, 158, 157, 159, 427, 428, 430, 
	427, 429, 430, 430, 430, 158, 157, 159, 
	431, 432, 434, 431, 433, 434, 434, 434, 
	158, 157, 436, 435, 437, 435, 158, 157, 
	436, 435, 437, 438, 435, 438, 438, 438, 
	158, 157, 436, 437, 157, 440, 439, 441, 
	443, 439, 442, 443, 443, 443, 158, 157, 
	436, 444, 437, 446, 444, 445, 446, 446, 
	446, 158, 157, 159, 445, 446, 445, 445, 
	446, 446, 446, 158, 157, 448, 447, 449, 
	446, 447, 445, 446, 446, 446, 158, 157, 
	159, 433, 434, 433, 433, 434, 434, 434, 
	158, 157, 159, 450, 451, 434, 450, 433, 
	434, 434, 434, 158, 1, 453, 452, 111, 
	1, 161, 160, 452, 162, 163, 164, 165, 
	166, 167, 160, 158, 454, 161, 160, 162, 
	163, 164, 165, 166, 167, 160, 158, 0
};

static const short _parse_tester_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 18, 19, 20, 21, 22, 
	23, 24, 25, 26, 27, 105, 106, 27, 
	28, 93, 29, 30, 31, 32, 33, 34, 
	33, 34, 35, 36, 37, 38, 39, 40, 
	41, 42, 43, 44, 45, 92, 45, 45, 
	46, 47, 48, 49, 50, 51, 52, 51, 
	52, 53, 54, 55, 90, 91, 54, 55, 
	90, 91, 56, 57, 85, 86, 57, 57, 
	58, 59, 60, 61, 62, 84, 62, 62, 
	63, 64, 65, 66, 67, 68, 69, 70, 
	71, 72, 73, 74, 75, 76, 77, 78, 
	79, 83, 79, 79, 80, 81, 82, 305, 
	87, 57, 85, 88, 89, 87, 88, 89, 
	87, 57, 85, 54, 55, 94, 95, 96, 
	97, 98, 99, 100, 101, 102, 103, 104, 
	101, 102, 103, 102, 107, 108, 109, 110, 
	111, 112, 113, 114, 115, 116, 117, 118, 
	119, 120, 121, 122, 123, 306, 124, 306, 
	125, 307, 126, 171, 199, 214, 232, 288, 
	127, 128, 129, 130, 131, 132, 170, 132, 
	133, 134, 135, 136, 169, 137, 137, 138, 
	139, 166, 140, 141, 142, 165, 142, 143, 
	162, 144, 145, 146, 161, 146, 147, 158, 
	148, 149, 150, 157, 151, 306, 152, 153, 
	154, 306, 152, 155, 156, 154, 155, 156, 
	154, 306, 152, 159, 149, 150, 160, 163, 
	145, 146, 164, 167, 141, 142, 168, 172, 
	173, 174, 175, 181, 176, 177, 178, 306, 
	179, 180, 178, 306, 179, 182, 183, 184, 
	185, 186, 187, 188, 189, 190, 191, 192, 
	193, 198, 194, 195, 306, 196, 197, 200, 
	201, 202, 203, 204, 205, 306, 206, 207, 
	205, 306, 206, 207, 208, 211, 209, 210, 
	211, 212, 213, 210, 212, 213, 210, 211, 
	215, 216, 217, 218, 219, 220, 219, 220, 
	221, 222, 223, 230, 231, 222, 223, 230, 
	231, 224, 306, 225, 226, 227, 306, 225, 
	228, 229, 227, 228, 229, 227, 306, 225, 
	222, 223, 233, 234, 235, 236, 237, 252, 
	268, 238, 239, 240, 241, 242, 243, 244, 
	245, 246, 243, 244, 245, 246, 243, 246, 
	247, 248, 306, 249, 250, 251, 248, 306, 
	249, 250, 251, 248, 306, 249, 253, 254, 
	255, 256, 257, 258, 259, 260, 261, 262, 
	259, 260, 261, 262, 259, 262, 263, 264, 
	306, 265, 266, 267, 264, 306, 265, 266, 
	267, 264, 306, 265, 269, 270, 271, 272, 
	273, 274, 275, 276, 277, 278, 279, 280, 
	281, 282, 279, 280, 281, 282, 279, 282, 
	283, 284, 306, 285, 286, 287, 284, 306, 
	285, 286, 287, 284, 306, 285, 289, 290, 
	291, 292, 293, 294, 295, 302, 303, 294, 
	295, 302, 303, 296, 306, 297, 298, 299, 
	306, 297, 300, 301, 299, 300, 301, 299, 
	306, 297, 294, 295, 304, 306, 306
};

static const unsigned char _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 39, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 121, 0, 0, 1, 
	0, 0, 0, 0, 0, 41, 41, 0, 
	0, 0, 83, 83, 13, 80, 0, 0, 
	0, 15, 0, 125, 0, 0, 0, 1, 
	0, 0, 0, 0, 59, 0, 0, 1, 
	43, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	133, 0, 0, 1, 0, 0, 0, 0, 
	86, 210, 86, 13, 80, 0, 0, 15, 
	19, 172, 19, 17, 17, 0, 0, 0, 
	0, 0, 0, 0, 49, 95, 49, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 57, 0, 68, 
	0, 153, 0, 0, 45, 0, 92, 35, 
	0, 0, 0, 0, 0, 21, 5, 0, 
	0, 0, 0, 0, 5, 23, 0, 0, 
	0, 0, 0, 0, 25, 5, 0, 0, 
	0, 0, 0, 27, 5, 0, 0, 0, 
	0, 0, 29, 5, 0, 101, 0, 0, 
	145, 234, 145, 13, 80, 0, 0, 15, 
	89, 228, 89, 0, 11, 77, 5, 0, 
	11, 74, 5, 0, 11, 71, 5, 0, 
	0, 0, 33, 0, 0, 0, 31, 149, 
	31, 5, 0, 62, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 5, 0, 0, 105, 0, 9, 0, 
	0, 0, 0, 0, 47, 187, 47, 47, 
	0, 137, 0, 0, 0, 0, 0, 83, 
	83, 13, 80, 0, 0, 15, 17, 17, 
	0, 0, 0, 0, 41, 41, 0, 0, 
	0, 83, 83, 13, 80, 0, 0, 0, 
	15, 0, 129, 0, 0, 86, 216, 86, 
	13, 80, 0, 0, 15, 19, 177, 19, 
	17, 17, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 83, 13, 
	80, 83, 0, 0, 15, 0, 17, 17, 
	0, 86, 192, 86, 13, 80, 0, 109, 
	0, 0, 15, 19, 157, 19, 0, 0, 
	0, 0, 0, 0, 83, 13, 80, 83, 
	0, 0, 15, 0, 17, 17, 0, 86, 
	204, 86, 13, 80, 0, 117, 0, 0, 
	15, 19, 167, 19, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 83, 13, 
	80, 83, 0, 0, 15, 0, 17, 17, 
	0, 86, 222, 86, 13, 80, 0, 141, 
	0, 0, 15, 19, 182, 19, 0, 0, 
	0, 0, 0, 83, 83, 13, 80, 0, 
	0, 0, 15, 0, 113, 0, 0, 86, 
	198, 86, 13, 80, 0, 0, 15, 19, 
	162, 19, 17, 17, 0, 65, 55
};

static const unsigned char _parse_tester_to_state_actions[] = {
	0, 51, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 51, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 51, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 51, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 3, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	3, 0, 7, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 37, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 98, 0
};

static const unsigned char _parse_tester_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 0
};

static const short _parse_tester_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	0, 0, 0, 455
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 305;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 306;
static const int parse_tester_en_main = 1;

#line 1177 "NanorexMMPImportExportTest.rl"
	
#line 9376 "NanorexMMPImportExportTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1178 "NanorexMMPImportExportTest.rl"
	
#line 9386 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _parse_tester_actions + _parse_tester_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 44:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 9407 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _parse_tester_trans_keys + _parse_tester_key_offsets[cs];
	_trans = _parse_tester_index_offsets[cs];

	_klen = _parse_tester_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _parse_tester_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _parse_tester_indicies[_trans];
_eof_trans:
	cs = _parse_tester_trans_targs_wi[_trans];

	if ( _parse_tester_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _parse_tester_actions + _parse_tester_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 1061 "NanorexMMPImportExportTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 39:
#line 1075 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 40:
#line 1078 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 41:
#line 1083 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 45:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 46:
#line 103 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 47:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 50:
#line 93 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 94 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 95 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 96 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 97 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 98 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 101 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 57:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p+1;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 58:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 59:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;}	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 9725 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _parse_tester_actions + _parse_tester_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 9754 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _parse_tester_eof_trans[cs] > 0 ) {
		_trans = _parse_tester_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	}

	_out: {}
	}
#line 1179 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::fileParseTest(void)
{
// 	fileParseTestH2O();
// 	fileParseTestHOOH();
// 	fileParseTestChlorophyll();
// 	fileParseTestVanillin();
	fileParseTestNanocar();
}



void NanorexMMPImportExportTest::fileParseTestH2O(void)
{
	ifstream infile("H2O.mmp", ios::in);
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


void NanorexMMPImportExportTest::fileParseTestHOOH(void)
{
	ifstream infile("hydrogen_peroxide.mmp", ios::in);
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


void NanorexMMPImportExportTest::fileParseTestChlorophyll(void)
{
	ifstream infile("chlorophyll.mmp", ios::in);
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


void NanorexMMPImportExportTest::fileParseTestVanillin(void)
{
	ifstream infile("vanillin.mmp", ios::in);
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


void NanorexMMPImportExportTest::fileParseTestNanocar(void)
{
	ifstream infile("nanocar.mmp", ios::in);
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
NanorexMMPImportExportTest::
fileParseTestHelper(RagelIstreamPtr& p, RagelIstreamPtr& pe)
{
	RagelIstreamPtr eof(p);
	RagelIstreamPtr ts, te;
	int cs, stack[1024], top, act;
	RagelIstreamPtr charStringWithSpaceStart, charStringWithSpaceStop;
	RagelIstreamPtr lineStart;
	
	#line 1286 "NanorexMMPImportExportTest.rl"
	
#line 9882 "NanorexMMPImportExportTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 28, 1, 31, 1, 33, 1, 
	34, 1, 38, 1, 42, 1, 44, 1, 
	58, 1, 59, 2, 0, 30, 2, 0, 
	54, 2, 0, 56, 2, 0, 57, 2, 
	5, 12, 2, 5, 13, 2, 5, 14, 
	2, 6, 7, 2, 6, 8, 2, 6, 
	9, 2, 8, 15, 2, 36, 24, 2, 
	38, 0, 2, 42, 43, 3, 0, 16, 
	52, 3, 0, 19, 55, 3, 0, 20, 
	53, 3, 0, 23, 50, 3, 0, 25, 
	51, 3, 0, 27, 39, 3, 0, 29, 
	40, 3, 0, 29, 47, 3, 0, 32, 
	41, 3, 0, 35, 49, 3, 0, 37, 
	48, 3, 6, 8, 15, 3, 17, 0, 
	54, 3, 45, 0, 46, 4, 9, 0, 
	20, 53, 4, 9, 0, 23, 50, 4, 
	9, 0, 25, 51, 4, 9, 0, 29, 
	40, 4, 9, 0, 29, 47, 4, 9, 
	0, 37, 48, 4, 34, 0, 35, 49, 
	5, 6, 9, 0, 20, 53, 5, 6, 
	9, 0, 23, 50, 5, 6, 9, 0, 
	25, 51, 5, 6, 9, 0, 29, 40, 
	5, 6, 9, 0, 29, 47, 5, 6, 
	9, 0, 37, 48, 5, 8, 15, 0, 
	16, 52, 6, 6, 8, 15, 0, 16, 
	52
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 102, 107, 108, 
	109, 110, 111, 116, 121, 132, 146, 160, 
	165, 177, 182, 183, 184, 185, 190, 195, 
	196, 197, 198, 199, 204, 209, 210, 211, 
	212, 213, 214, 215, 216, 217, 222, 227, 
	232, 233, 234, 238, 240, 242, 244, 258, 
	272, 285, 299, 312, 326, 328, 329, 330, 
	331, 332, 333, 337, 343, 350, 355, 360, 
	362, 369, 371, 375, 381, 383, 385, 387, 
	389, 391, 395, 400, 401, 402, 403, 404, 
	405, 406, 407, 408, 413, 415, 426, 429, 
	432, 435, 440, 447, 454, 460, 467, 475, 
	481, 486, 492, 501, 505, 513, 519, 528, 
	532, 540, 546, 555, 559, 567, 573, 579, 
	592, 594, 609, 624, 638, 653, 661, 665, 
	673, 681, 689, 693, 701, 709, 717, 721, 
	729, 737, 745, 752, 755, 758, 761, 769, 
	774, 781, 789, 797, 799, 807, 810, 813, 
	816, 819, 822, 825, 828, 831, 834, 839, 
	846, 853, 860, 868, 874, 876, 884, 891, 
	894, 897, 900, 903, 906, 913, 920, 922, 
	935, 947, 962, 977, 983, 997, 1012, 1015, 
	1018, 1021, 1024, 1030, 1036, 1048, 1063, 1078, 
	1084, 1097, 1099, 1114, 1129, 1143, 1158, 1172, 
	1187, 1190, 1193, 1196, 1201, 1209, 1212, 1215, 
	1218, 1223, 1235, 1250, 1265, 1279, 1294, 1306, 
	1321, 1336, 1338, 1352, 1367, 1370, 1373, 1376, 
	1379, 1384, 1396, 1411, 1426, 1440, 1455, 1467, 
	1482, 1497, 1499, 1513, 1528, 1531, 1534, 1537, 
	1540, 1543, 1546, 1549, 1552, 1557, 1569, 1584, 
	1599, 1613, 1628, 1640, 1655, 1670, 1672, 1686, 
	1701, 1704, 1707, 1712, 1718, 1730, 1745, 1760, 
	1766, 1779, 1781, 1796, 1811, 1825, 1840, 1854, 
	1869, 1871, 1871, 1883
};

static const char _parse_tester_trans_keys[] = {
	10, 32, 109, 9, 13, 109, 112, 102, 
	111, 114, 109, 97, 116, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 48, 
	57, 48, 57, 48, 57, 48, 57, 48, 
	57, 9, 32, 11, 13, 9, 32, 114, 
	11, 13, 101, 113, 117, 105, 114, 101, 
	100, 10, 32, 35, 59, 9, 13, 10, 
	32, 103, 107, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	40, 11, 13, 9, 32, 86, 11, 13, 
	105, 101, 119, 9, 32, 11, 13, 9, 
	32, 68, 11, 13, 97, 116, 97, 9, 
	32, 41, 11, 13, 10, 35, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 40, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 41, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 41, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 9, 13, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 101, 9, 13, 110, 100, 
	49, 10, 32, 35, 9, 13, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 67, 11, 
	13, 108, 105, 112, 98, 111, 97, 114, 
	100, 9, 32, 41, 11, 13, 10, 32, 
	35, 9, 13, 10, 32, 101, 9, 13, 
	110, 100, 9, 32, 11, 13, -1, 10, 
	-1, 10, -1, 10, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	101, 108, 118, 105, 110, 9, 32, 11, 
	13, 9, 32, 11, 13, 48, 57, 10, 
	32, 35, 9, 13, 48, 57, 10, 32, 
	35, 9, 13, 10, 32, 103, 9, 13, 
	-1, 10, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 9, 32, 11, 13, 9, 
	32, 11, 13, 48, 57, 48, 57, 48, 
	57, 48, 57, 48, 57, 48, 57, 9, 
	32, 11, 13, 9, 32, 112, 11, 13, 
	114, 101, 102, 101, 114, 114, 101, 100, 
	10, 32, 35, 9, 13, -1, 10, -1, 
	10, 32, 97, 98, 101, 103, 105, 109, 
	9, 13, -1, 10, 116, -1, 10, 111, 
	-1, 10, 109, -1, 10, 32, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, -1, 
	10, 32, 43, 45, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	35, 9, 13, -1, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	100, -1, 10, 95, 97, 99, 103, 49, 
	51, -1, 10, 32, 9, 13, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, 32, 
	35, 9, 13, 48, 57, -1, 10, -1, 
	10, 32, 35, 9, 13, 48, 57, -1, 
	10, 100, -1, 10, 105, -1, 10, 114, 
	-1, 10, 101, -1, 10, 99, -1, 10, 
	116, -1, 10, 105, -1, 10, 111, -1, 
	10, 110, -1, 10, 32, 9, 13, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 35, 40, 9, 
	13, -1, 10, 32, 35, 40, 9, 13, 
	-1, 10, -1, 10, 32, 41, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, 32, 35, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 110, -1, 10, 
	102, -1, 10, 111, -1, 10, 32, 9, 
	13, -1, 10, 32, 97, 99, 111, 9, 
	13, -1, 10, 116, -1, 10, 111, -1, 
	10, 109, -1, 10, 32, 9, 13, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 61, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 104, -1, 10, 117, -1, 10, 110, 
	-1, 10, 107, -1, 10, 32, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 61, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 112, -1, 10, 101, -1, 10, 
	110, -1, 10, 103, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 111, 
	-1, 10, 108, -1, 10, 32, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 97, 98, 101, 103, 105, 
	109, 9, 13, -1, 10, 32, 97, 98, 
	101, 103, 105, 109, 9, 13, 0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 2, 3, 1, 1, 
	1, 1, 3, 3, 3, 4, 4, 3, 
	4, 3, 1, 1, 1, 3, 3, 1, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 3, 3, 
	1, 1, 2, 2, 2, 2, 4, 4, 
	3, 4, 3, 4, 2, 1, 1, 1, 
	1, 1, 2, 2, 3, 3, 3, 2, 
	3, 2, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 2, 9, 3, 3, 
	3, 3, 3, 3, 4, 3, 4, 4, 
	3, 4, 5, 2, 4, 4, 5, 2, 
	4, 4, 5, 2, 4, 4, 4, 5, 
	2, 5, 5, 4, 5, 4, 2, 4, 
	4, 4, 2, 4, 4, 4, 2, 4, 
	4, 4, 3, 3, 3, 3, 6, 3, 
	3, 4, 4, 2, 4, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 4, 4, 2, 4, 3, 3, 
	3, 3, 3, 3, 5, 5, 2, 5, 
	4, 5, 5, 4, 4, 5, 3, 3, 
	3, 3, 4, 4, 4, 5, 5, 4, 
	5, 2, 5, 5, 4, 5, 4, 5, 
	3, 3, 3, 3, 6, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 4, 4, 5, 5, 4, 
	5, 2, 5, 5, 4, 5, 4, 5, 
	2, 0, 10, 9
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 1, 0, 0, 0, 1, 1, 0, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 1, 1, 
	0, 0, 1, 0, 0, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 0, 0, 
	0, 0, 1, 2, 2, 1, 1, 0, 
	2, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 1, 2, 2, 1, 2, 2, 1, 
	1, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 1, 4, 
	0, 5, 5, 5, 5, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 2, 0, 0, 0, 1, 1, 
	2, 2, 2, 0, 2, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 1, 2, 
	2, 2, 2, 1, 0, 2, 2, 0, 
	0, 0, 0, 0, 1, 1, 0, 4, 
	4, 5, 5, 1, 5, 5, 0, 0, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 0, 5, 5, 5, 5, 5, 5, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 0, 5, 5, 5, 5, 5, 5, 
	0, 0, 1, 1
};

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 127, 132, 134, 
	136, 138, 140, 145, 150, 158, 168, 178, 
	183, 192, 197, 199, 201, 203, 208, 213, 
	215, 217, 219, 221, 226, 231, 233, 235, 
	237, 239, 241, 243, 245, 247, 252, 257, 
	262, 264, 266, 270, 273, 276, 279, 289, 
	299, 308, 318, 327, 337, 340, 342, 344, 
	346, 348, 350, 354, 359, 365, 370, 375, 
	378, 384, 387, 391, 396, 398, 400, 402, 
	404, 406, 410, 415, 417, 419, 421, 423, 
	425, 427, 429, 431, 436, 439, 450, 454, 
	458, 462, 467, 473, 479, 485, 491, 498, 
	504, 509, 515, 523, 527, 534, 540, 548, 
	552, 559, 565, 573, 577, 584, 590, 596, 
	606, 609, 620, 631, 641, 652, 659, 663, 
	670, 677, 684, 688, 695, 702, 709, 713, 
	720, 727, 734, 740, 744, 748, 752, 760, 
	765, 771, 778, 785, 788, 795, 799, 803, 
	807, 811, 815, 819, 823, 827, 831, 836, 
	842, 848, 854, 861, 867, 870, 877, 883, 
	887, 891, 895, 899, 903, 910, 917, 920, 
	930, 939, 950, 961, 967, 977, 988, 992, 
	996, 1000, 1004, 1010, 1016, 1025, 1036, 1047, 
	1053, 1063, 1066, 1077, 1088, 1098, 1109, 1119, 
	1130, 1134, 1138, 1142, 1147, 1155, 1159, 1163, 
	1167, 1172, 1181, 1192, 1203, 1213, 1224, 1233, 
	1244, 1255, 1258, 1268, 1279, 1283, 1287, 1291, 
	1295, 1300, 1309, 1320, 1331, 1341, 1352, 1361, 
	1372, 1383, 1386, 1396, 1407, 1411, 1415, 1419, 
	1423, 1427, 1431, 1435, 1439, 1444, 1453, 1464, 
	1475, 1485, 1496, 1505, 1516, 1527, 1530, 1540, 
	1551, 1555, 1559, 1564, 1570, 1579, 1590, 1601, 
	1607, 1617, 1620, 1631, 1642, 1652, 1663, 1673, 
	1684, 1687, 1688, 1700
};

static const short _parse_tester_indicies[] = {
	2, 0, 3, 0, 1, 4, 1, 5, 
	1, 6, 1, 7, 1, 8, 1, 9, 
	1, 10, 1, 11, 1, 12, 12, 12, 
	1, 12, 12, 12, 13, 1, 14, 1, 
	15, 1, 16, 1, 17, 1, 18, 1, 
	19, 19, 19, 1, 19, 19, 20, 19, 
	1, 21, 1, 22, 1, 23, 1, 24, 
	1, 25, 1, 26, 1, 27, 1, 28, 
	27, 29, 30, 27, 1, 28, 31, 32, 
	33, 31, 1, 34, 1, 35, 1, 36, 
	1, 37, 1, 38, 38, 39, 38, 1, 
	40, 40, 41, 40, 1, 41, 41, 42, 
	41, 1, 43, 1, 44, 1, 45, 1, 
	46, 46, 46, 1, 46, 46, 47, 46, 
	1, 48, 1, 49, 1, 50, 1, 50, 
	50, 51, 50, 1, 52, 53, 1, 55, 
	54, 56, 54, 1, 57, 1, 58, 1, 
	59, 1, 60, 1, 61, 61, 62, 61, 
	1, 63, 63, 64, 63, 1, 64, 64, 
	65, 64, 65, 65, 65, 1, 66, 66, 
	67, 69, 66, 68, 69, 69, 69, 1, 
	70, 70, 71, 73, 70, 72, 73, 73, 
	73, 1, 75, 74, 76, 74, 1, 75, 
	74, 76, 77, 74, 77, 77, 77, 1, 
	79, 78, 80, 78, 1, 81, 1, 82, 
	1, 83, 1, 84, 83, 85, 83, 1, 
	87, 86, 88, 86, 1, 89, 1, 90, 
	1, 91, 1, 92, 1, 92, 92, 93, 
	92, 1, 93, 93, 94, 93, 1, 95, 
	1, 96, 1, 97, 1, 98, 1, 99, 
	1, 100, 1, 101, 1, 102, 1, 102, 
	102, 103, 102, 1, 104, 103, 105, 103, 
	1, 107, 106, 108, 106, 1, 109, 1, 
	110, 1, 111, 111, 111, 1, 1, 104, 
	105, 1, 84, 85, 1, 75, 76, 113, 
	112, 114, 116, 112, 115, 116, 116, 116, 
	1, 75, 117, 76, 119, 117, 118, 119, 
	119, 119, 1, 118, 118, 119, 118, 118, 
	119, 119, 119, 1, 121, 120, 122, 119, 
	120, 118, 119, 119, 119, 1, 72, 72, 
	73, 72, 72, 73, 73, 73, 1, 123, 
	123, 124, 73, 123, 72, 73, 73, 73, 
	1, 1, 52, 53, 125, 1, 126, 1, 
	127, 1, 128, 1, 129, 1, 130, 130, 
	130, 1, 130, 130, 130, 131, 1, 133, 
	132, 134, 132, 135, 1, 137, 136, 138, 
	136, 1, 137, 139, 32, 139, 1, 1, 
	137, 138, 133, 132, 134, 132, 135, 1, 
	1, 28, 29, 140, 140, 140, 1, 140, 
	140, 140, 141, 1, 142, 1, 143, 1, 
	144, 1, 145, 1, 146, 1, 147, 147, 
	147, 1, 147, 147, 148, 147, 1, 149, 
	1, 150, 1, 151, 1, 152, 1, 153, 
	1, 154, 1, 155, 1, 156, 1, 28, 
	156, 29, 156, 1, 157, 159, 158, 157, 
	161, 160, 162, 163, 164, 165, 166, 167, 
	160, 158, 157, 159, 168, 158, 157, 159, 
	169, 158, 157, 159, 170, 158, 157, 159, 
	171, 171, 158, 157, 159, 171, 171, 172, 
	158, 157, 159, 173, 173, 174, 158, 157, 
	159, 175, 176, 175, 158, 157, 159, 176, 
	176, 177, 158, 157, 159, 178, 179, 178, 
	180, 158, 157, 159, 178, 179, 178, 158, 
	157, 159, 181, 181, 158, 157, 159, 182, 
	183, 182, 158, 157, 159, 183, 184, 185, 
	183, 186, 158, 157, 159, 186, 158, 157, 
	159, 187, 188, 187, 189, 158, 157, 159, 
	187, 188, 187, 158, 157, 159, 190, 191, 
	192, 190, 193, 158, 157, 159, 193, 158, 
	157, 159, 194, 195, 194, 196, 158, 157, 
	159, 194, 195, 194, 158, 157, 159, 197, 
	198, 199, 197, 200, 158, 157, 159, 200, 
	158, 157, 159, 201, 202, 201, 203, 158, 
	157, 159, 201, 202, 201, 158, 157, 205, 
	204, 206, 204, 158, 157, 205, 204, 206, 
	207, 204, 207, 207, 207, 158, 157, 205, 
	206, 157, 209, 208, 210, 212, 208, 211, 
	212, 212, 212, 158, 157, 205, 213, 206, 
	215, 213, 214, 215, 215, 215, 158, 157, 
	159, 214, 215, 214, 214, 215, 215, 215, 
	158, 157, 217, 216, 218, 215, 216, 214, 
	215, 215, 215, 158, 157, 159, 201, 202, 
	201, 203, 158, 157, 159, 219, 158, 157, 
	159, 220, 221, 220, 222, 158, 157, 159, 
	220, 221, 220, 222, 158, 157, 159, 194, 
	195, 194, 196, 158, 157, 159, 223, 158, 
	157, 159, 224, 225, 224, 226, 158, 157, 
	159, 224, 225, 224, 226, 158, 157, 159, 
	187, 188, 187, 189, 158, 157, 159, 227, 
	158, 157, 159, 228, 229, 228, 230, 158, 
	157, 159, 228, 229, 228, 230, 158, 157, 
	159, 178, 179, 178, 180, 158, 157, 159, 
	173, 173, 174, 158, 157, 159, 231, 158, 
	157, 159, 232, 158, 157, 159, 233, 158, 
	157, 159, 235, 234, 234, 234, 234, 158, 
	157, 159, 236, 236, 158, 157, 159, 236, 
	236, 237, 158, 157, 239, 238, 240, 238, 
	241, 158, 157, 243, 242, 244, 242, 237, 
	158, 157, 243, 244, 157, 239, 238, 240, 
	238, 241, 158, 157, 159, 245, 158, 157, 
	159, 246, 158, 157, 159, 247, 158, 157, 
	159, 248, 158, 157, 159, 249, 158, 157, 
	159, 250, 158, 157, 159, 251, 158, 157, 
	159, 252, 158, 157, 159, 253, 158, 157, 
	159, 254, 254, 158, 157, 159, 254, 254, 
	255, 158, 157, 159, 256, 256, 257, 158, 
	157, 159, 256, 256, 258, 158, 157, 260, 
	259, 261, 259, 262, 158, 157, 260, 259, 
	261, 259, 158, 157, 260, 261, 157, 260, 
	259, 261, 259, 262, 158, 157, 159, 256, 
	256, 257, 158, 157, 159, 263, 158, 157, 
	159, 264, 158, 157, 159, 265, 158, 157, 
	159, 266, 158, 157, 159, 267, 158, 157, 
	269, 268, 270, 271, 268, 158, 157, 273, 
	272, 274, 275, 272, 158, 157, 273, 274, 
	157, 159, 276, 277, 278, 276, 278, 278, 
	278, 158, 157, 159, 276, 278, 276, 278, 
	278, 278, 158, 157, 159, 279, 280, 282, 
	279, 281, 282, 282, 282, 158, 157, 159, 
	283, 277, 285, 283, 284, 285, 285, 285, 
	158, 157, 273, 277, 274, 277, 158, 157, 
	159, 284, 285, 284, 284, 285, 285, 285, 
	158, 157, 159, 286, 287, 285, 286, 284, 
	285, 285, 285, 158, 157, 159, 288, 158, 
	157, 159, 289, 158, 157, 159, 290, 158, 
	157, 159, 291, 158, 157, 159, 292, 293, 
	292, 158, 157, 159, 294, 295, 294, 158, 
	157, 159, 295, 296, 295, 296, 296, 296, 
	158, 157, 159, 297, 298, 300, 297, 299, 
	300, 300, 300, 158, 157, 159, 301, 302, 
	304, 301, 303, 304, 304, 304, 158, 157, 
	306, 305, 307, 305, 158, 157, 306, 305, 
	307, 308, 305, 308, 308, 308, 158, 157, 
	306, 307, 157, 310, 309, 311, 313, 309, 
	312, 313, 313, 313, 158, 157, 306, 314, 
	307, 316, 314, 315, 316, 316, 316, 158, 
	157, 159, 315, 316, 315, 315, 316, 316, 
	316, 158, 157, 318, 317, 319, 316, 317, 
	315, 316, 316, 316, 158, 157, 159, 303, 
	304, 303, 303, 304, 304, 304, 158, 157, 
	159, 320, 321, 304, 320, 303, 304, 304, 
	304, 158, 157, 159, 322, 158, 157, 159, 
	323, 158, 157, 159, 324, 158, 157, 159, 
	325, 325, 158, 157, 159, 325, 326, 327, 
	328, 325, 158, 157, 159, 329, 158, 157, 
	159, 330, 158, 157, 159, 331, 158, 157, 
	159, 332, 332, 158, 157, 159, 332, 333, 
	332, 333, 333, 333, 158, 157, 159, 334, 
	337, 336, 334, 335, 336, 336, 336, 158, 
	157, 159, 338, 341, 340, 338, 339, 340, 
	340, 340, 158, 157, 159, 339, 340, 339, 
	339, 340, 340, 340, 158, 157, 159, 342, 
	343, 340, 342, 339, 340, 340, 340, 158, 
	157, 159, 341, 344, 341, 344, 344, 344, 
	158, 157, 346, 345, 347, 349, 345, 348, 
	349, 349, 349, 158, 157, 351, 350, 352, 
	354, 350, 353, 354, 354, 354, 158, 157, 
	351, 352, 157, 159, 353, 354, 353, 353, 
	354, 354, 354, 158, 157, 356, 355, 357, 
	354, 355, 353, 354, 354, 354, 158, 157, 
	159, 358, 158, 157, 159, 359, 158, 157, 
	159, 360, 158, 157, 159, 361, 158, 157, 
	159, 362, 362, 158, 157, 159, 362, 363, 
	362, 363, 363, 363, 158, 157, 159, 364, 
	367, 366, 364, 365, 366, 366, 366, 158, 
	157, 159, 368, 371, 370, 368, 369, 370, 
	370, 370, 158, 157, 159, 369, 370, 369, 
	369, 370, 370, 370, 158, 157, 159, 372, 
	373, 370, 372, 369, 370, 370, 370, 158, 
	157, 159, 371, 374, 371, 374, 374, 374, 
	158, 157, 376, 375, 377, 379, 375, 378, 
	379, 379, 379, 158, 157, 381, 380, 382, 
	384, 380, 383, 384, 384, 384, 158, 157, 
	381, 382, 157, 159, 383, 384, 383, 383, 
	384, 384, 384, 158, 157, 386, 385, 387, 
	384, 385, 383, 384, 384, 384, 158, 157, 
	159, 388, 158, 157, 159, 389, 158, 157, 
	159, 390, 158, 157, 159, 391, 158, 157, 
	159, 392, 158, 157, 159, 393, 158, 157, 
	159, 394, 158, 157, 159, 395, 158, 157, 
	159, 396, 396, 158, 157, 159, 396, 397, 
	396, 397, 397, 397, 158, 157, 159, 398, 
	401, 400, 398, 399, 400, 400, 400, 158, 
	157, 159, 402, 405, 404, 402, 403, 404, 
	404, 404, 158, 157, 159, 403, 404, 403, 
	403, 404, 404, 404, 158, 157, 159, 406, 
	407, 404, 406, 403, 404, 404, 404, 158, 
	157, 159, 405, 408, 405, 408, 408, 408, 
	158, 157, 410, 409, 411, 413, 409, 412, 
	413, 413, 413, 158, 157, 415, 414, 416, 
	418, 414, 417, 418, 418, 418, 158, 157, 
	415, 416, 157, 159, 417, 418, 417, 417, 
	418, 418, 418, 158, 157, 420, 419, 421, 
	418, 419, 417, 418, 418, 418, 158, 157, 
	159, 422, 158, 157, 159, 423, 158, 157, 
	159, 424, 424, 158, 157, 159, 424, 425, 
	424, 158, 157, 159, 425, 426, 425, 426, 
	426, 426, 158, 157, 159, 427, 428, 430, 
	427, 429, 430, 430, 430, 158, 157, 159, 
	431, 432, 434, 431, 433, 434, 434, 434, 
	158, 157, 436, 435, 437, 435, 158, 157, 
	436, 435, 437, 438, 435, 438, 438, 438, 
	158, 157, 436, 437, 157, 440, 439, 441, 
	443, 439, 442, 443, 443, 443, 158, 157, 
	436, 444, 437, 446, 444, 445, 446, 446, 
	446, 158, 157, 159, 445, 446, 445, 445, 
	446, 446, 446, 158, 157, 448, 447, 449, 
	446, 447, 445, 446, 446, 446, 158, 157, 
	159, 433, 434, 433, 433, 434, 434, 434, 
	158, 157, 159, 450, 451, 434, 450, 433, 
	434, 434, 434, 158, 1, 453, 452, 111, 
	1, 161, 160, 452, 162, 163, 164, 165, 
	166, 167, 160, 158, 454, 161, 160, 162, 
	163, 164, 165, 166, 167, 160, 158, 0
};

static const short _parse_tester_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 18, 19, 20, 21, 22, 
	23, 24, 25, 26, 27, 105, 106, 27, 
	28, 93, 29, 30, 31, 32, 33, 34, 
	33, 34, 35, 36, 37, 38, 39, 40, 
	41, 42, 43, 44, 45, 92, 45, 45, 
	46, 47, 48, 49, 50, 51, 52, 51, 
	52, 53, 54, 55, 90, 91, 54, 55, 
	90, 91, 56, 57, 85, 86, 57, 57, 
	58, 59, 60, 61, 62, 84, 62, 62, 
	63, 64, 65, 66, 67, 68, 69, 70, 
	71, 72, 73, 74, 75, 76, 77, 78, 
	79, 83, 79, 79, 80, 81, 82, 305, 
	87, 57, 85, 88, 89, 87, 88, 89, 
	87, 57, 85, 54, 55, 94, 95, 96, 
	97, 98, 99, 100, 101, 102, 103, 104, 
	101, 102, 103, 102, 107, 108, 109, 110, 
	111, 112, 113, 114, 115, 116, 117, 118, 
	119, 120, 121, 122, 123, 306, 124, 306, 
	125, 307, 126, 171, 199, 214, 232, 288, 
	127, 128, 129, 130, 131, 132, 170, 132, 
	133, 134, 135, 136, 169, 137, 137, 138, 
	139, 166, 140, 141, 142, 165, 142, 143, 
	162, 144, 145, 146, 161, 146, 147, 158, 
	148, 149, 150, 157, 151, 306, 152, 153, 
	154, 306, 152, 155, 156, 154, 155, 156, 
	154, 306, 152, 159, 149, 150, 160, 163, 
	145, 146, 164, 167, 141, 142, 168, 172, 
	173, 174, 175, 181, 176, 177, 178, 306, 
	179, 180, 178, 306, 179, 182, 183, 184, 
	185, 186, 187, 188, 189, 190, 191, 192, 
	193, 198, 194, 195, 306, 196, 197, 200, 
	201, 202, 203, 204, 205, 306, 206, 207, 
	205, 306, 206, 207, 208, 211, 209, 210, 
	211, 212, 213, 210, 212, 213, 210, 211, 
	215, 216, 217, 218, 219, 220, 219, 220, 
	221, 222, 223, 230, 231, 222, 223, 230, 
	231, 224, 306, 225, 226, 227, 306, 225, 
	228, 229, 227, 228, 229, 227, 306, 225, 
	222, 223, 233, 234, 235, 236, 237, 252, 
	268, 238, 239, 240, 241, 242, 243, 244, 
	245, 246, 243, 244, 245, 246, 243, 246, 
	247, 248, 306, 249, 250, 251, 248, 306, 
	249, 250, 251, 248, 306, 249, 253, 254, 
	255, 256, 257, 258, 259, 260, 261, 262, 
	259, 260, 261, 262, 259, 262, 263, 264, 
	306, 265, 266, 267, 264, 306, 265, 266, 
	267, 264, 306, 265, 269, 270, 271, 272, 
	273, 274, 275, 276, 277, 278, 279, 280, 
	281, 282, 279, 280, 281, 282, 279, 282, 
	283, 284, 306, 285, 286, 287, 284, 306, 
	285, 286, 287, 284, 306, 285, 289, 290, 
	291, 292, 293, 294, 295, 302, 303, 294, 
	295, 302, 303, 296, 306, 297, 298, 299, 
	306, 297, 300, 301, 299, 300, 301, 299, 
	306, 297, 294, 295, 304, 306, 306
};

static const unsigned char _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 39, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 121, 0, 0, 1, 
	0, 0, 0, 0, 0, 41, 41, 0, 
	0, 0, 83, 83, 13, 80, 0, 0, 
	0, 15, 0, 125, 0, 0, 0, 1, 
	0, 0, 0, 0, 59, 0, 0, 1, 
	43, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	133, 0, 0, 1, 0, 0, 0, 0, 
	86, 210, 86, 13, 80, 0, 0, 15, 
	19, 172, 19, 17, 17, 0, 0, 0, 
	0, 0, 0, 0, 49, 95, 49, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 57, 0, 68, 
	0, 153, 0, 0, 45, 0, 92, 35, 
	0, 0, 0, 0, 0, 21, 5, 0, 
	0, 0, 0, 0, 5, 23, 0, 0, 
	0, 0, 0, 0, 25, 5, 0, 0, 
	0, 0, 0, 27, 5, 0, 0, 0, 
	0, 0, 29, 5, 0, 101, 0, 0, 
	145, 234, 145, 13, 80, 0, 0, 15, 
	89, 228, 89, 0, 11, 77, 5, 0, 
	11, 74, 5, 0, 11, 71, 5, 0, 
	0, 0, 33, 0, 0, 0, 31, 149, 
	31, 5, 0, 62, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 5, 0, 0, 105, 0, 9, 0, 
	0, 0, 0, 0, 47, 187, 47, 47, 
	0, 137, 0, 0, 0, 0, 0, 83, 
	83, 13, 80, 0, 0, 15, 17, 17, 
	0, 0, 0, 0, 41, 41, 0, 0, 
	0, 83, 83, 13, 80, 0, 0, 0, 
	15, 0, 129, 0, 0, 86, 216, 86, 
	13, 80, 0, 0, 15, 19, 177, 19, 
	17, 17, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 83, 13, 
	80, 83, 0, 0, 15, 0, 17, 17, 
	0, 86, 192, 86, 13, 80, 0, 109, 
	0, 0, 15, 19, 157, 19, 0, 0, 
	0, 0, 0, 0, 83, 13, 80, 83, 
	0, 0, 15, 0, 17, 17, 0, 86, 
	204, 86, 13, 80, 0, 117, 0, 0, 
	15, 19, 167, 19, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 83, 13, 
	80, 83, 0, 0, 15, 0, 17, 17, 
	0, 86, 222, 86, 13, 80, 0, 141, 
	0, 0, 15, 19, 182, 19, 0, 0, 
	0, 0, 0, 83, 83, 13, 80, 0, 
	0, 0, 15, 0, 113, 0, 0, 86, 
	198, 86, 13, 80, 0, 0, 15, 19, 
	162, 19, 17, 17, 0, 65, 55
};

static const unsigned char _parse_tester_to_state_actions[] = {
	0, 51, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 51, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 51, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 51, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 3, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	3, 0, 7, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 37, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 98, 0
};

static const unsigned char _parse_tester_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 0
};

static const short _parse_tester_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	158, 158, 158, 158, 158, 158, 158, 158, 
	0, 0, 0, 455
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 305;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 306;
static const int parse_tester_en_main = 1;

#line 1287 "NanorexMMPImportExportTest.rl"
	
#line 10797 "NanorexMMPImportExportTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1288 "NanorexMMPImportExportTest.rl"
	
#line 10807 "NanorexMMPImportExportTest.cpp"
	{
	int _klen;
	unsigned int _trans;
	const char *_acts;
	unsigned int _nacts;
	const char *_keys;

	if ( p == pe )
		goto _test_eof;
	if ( cs == 0 )
		goto _out;
_resume:
	_acts = _parse_tester_actions + _parse_tester_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 44:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 10828 "NanorexMMPImportExportTest.cpp"
		}
	}

	_keys = _parse_tester_trans_keys + _parse_tester_key_offsets[cs];
	_trans = _parse_tester_index_offsets[cs];

	_klen = _parse_tester_single_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + _klen - 1;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + ((_upper-_lower) >> 1);
			if ( (*p) < *_mid )
				_upper = _mid - 1;
			else if ( (*p) > *_mid )
				_lower = _mid + 1;
			else {
				_trans += (_mid - _keys);
				goto _match;
			}
		}
		_keys += _klen;
		_trans += _klen;
	}

	_klen = _parse_tester_range_lengths[cs];
	if ( _klen > 0 ) {
		const char *_lower = _keys;
		const char *_mid;
		const char *_upper = _keys + (_klen<<1) - 2;
		while (1) {
			if ( _upper < _lower )
				break;

			_mid = _lower + (((_upper-_lower) >> 1) & ~1);
			if ( (*p) < _mid[0] )
				_upper = _mid - 2;
			else if ( (*p) > _mid[1] )
				_lower = _mid + 2;
			else {
				_trans += ((_mid - _keys)>>1);
				goto _match;
			}
		}
		_trans += _klen;
	}

_match:
	_trans = _parse_tester_indicies[_trans];
_eof_trans:
	cs = _parse_tester_trans_targs_wi[_trans];

	if ( _parse_tester_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _parse_tester_actions + _parse_tester_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 0:
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 1061 "NanorexMMPImportExportTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 39:
#line 1075 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 40:
#line 1078 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 41:
#line 1083 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 45:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 46:
#line 103 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 47:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 50:
#line 93 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 94 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 95 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 96 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 97 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 98 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 101 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 57:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p+1;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 58:
#line 103 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}}
	break;
	case 59:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;}	cerr << lineNum << ": Error : ";
				std::copy(ts, te, std::ostream_iterator<char>(cerr));
				cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 11146 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _parse_tester_actions + _parse_tester_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 11175 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _parse_tester_eof_trans[cs] > 0 ) {
		_trans = _parse_tester_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	}

	_out: {}
	}
#line 1289 "NanorexMMPImportExportTest.rl"
}


