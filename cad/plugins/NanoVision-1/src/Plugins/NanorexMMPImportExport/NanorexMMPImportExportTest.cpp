#line 1 "NanorexMMPImportExportTest.rl"
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


#line 128 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	#line 141 "NanorexMMPImportExportTest.rl"
	
#line 132 "NanorexMMPImportExportTest.cpp"
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

#line 142 "NanorexMMPImportExportTest.rl"
	
#line 293 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_decl_line_test_start;
	}
#line 143 "NanorexMMPImportExportTest.rl"
	
#line 299 "NanorexMMPImportExportTest.cpp"
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
#line 123 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 436 "NanorexMMPImportExportTest.cpp"
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
#line 449 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	_out: {}
	}
#line 144 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newAtom(int atomId, int atomicNum,
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


#line 199 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 210 "NanorexMMPImportExportTest.rl"
	
#line 517 "NanorexMMPImportExportTest.cpp"
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

#line 211 "NanorexMMPImportExportTest.rl"
	
#line 590 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_line_test_start;
	}
#line 212 "NanorexMMPImportExportTest.rl"
	
#line 596 "NanorexMMPImportExportTest.cpp"
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
#line 194 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 695 "NanorexMMPImportExportTest.cpp"
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
#line 708 "NanorexMMPImportExportTest.cpp"
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
#line 194 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 730 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 213 "NanorexMMPImportExportTest.rl"
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
	
	CERR("bond" + bondType + " " + NXUtility::itos(targetAtomId));
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


#line 267 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 279 "NanorexMMPImportExportTest.rl"
	
#line 794 "NanorexMMPImportExportTest.cpp"
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

#line 280 "NanorexMMPImportExportTest.rl"
	
#line 889 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_direction_line_test_start;
	}
#line 281 "NanorexMMPImportExportTest.rl"
	
#line 895 "NanorexMMPImportExportTest.cpp"
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
#line 262 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 994 "NanorexMMPImportExportTest.cpp"
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
#line 1011 "NanorexMMPImportExportTest.cpp"
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
#line 262 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 1033 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 282 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newBondDirection(int atomId1, int atomId2)
{
	CERR("bond_direction " + NXUtility::itos(atomId1) + " " +
	     NXUtility::itos(atomId2));
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


#line 338 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 349 "NanorexMMPImportExportTest.rl"
	
#line 1097 "NanorexMMPImportExportTest.cpp"
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

#line 350 "NanorexMMPImportExportTest.rl"
	
#line 1202 "NanorexMMPImportExportTest.cpp"
	{
	cs = info_atom_line_test_start;
	}
#line 351 "NanorexMMPImportExportTest.rl"
	
#line 1208 "NanorexMMPImportExportTest.cpp"
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
#line 333 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1321 "NanorexMMPImportExportTest.cpp"
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
#line 333 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1344 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 352 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newAtomInfo(std::string const& key,
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


#line 415 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 426 "NanorexMMPImportExportTest.rl"
	
#line 1414 "NanorexMMPImportExportTest.cpp"
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

#line 427 "NanorexMMPImportExportTest.rl"
	
#line 1824 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_stmt_test_start;
	}
#line 428 "NanorexMMPImportExportTest.rl"
	
#line 1830 "NanorexMMPImportExportTest.cpp"
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
#line 408 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 410 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2005 "NanorexMMPImportExportTest.cpp"
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
#line 2022 "NanorexMMPImportExportTest.cpp"
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
#line 408 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 410 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2048 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 429 "NanorexMMPImportExportTest.rl"
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


#line 559 "NanorexMMPImportExportTest.rl"



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
	
	#line 575 "NanorexMMPImportExportTest.rl"
	
#line 2179 "NanorexMMPImportExportTest.cpp"
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
	755, 769, 783, 785, 798, 812, 817
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
	9, 32, 11, 13, 48, 57, 0, 10, 
	32, 97, 98, 105, 9, 13, 116, 111, 
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
	65, 90, 97, 122, 10, 32, 97, 9, 
	13, 0, 10, 32, 97, 98, 105, 9, 
	13, 0
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
	4, 4, 2, 3, 4, 3, 6
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
	5, 5, 0, 5, 5, 1, 1
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
	671, 681, 691, 694, 703, 713, 718
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
	10, 0, 67, 70, 69, 71, 72, 73, 
	69, 68, 74, 68, 75, 68, 76, 68, 
	77, 77, 77, 68, 77, 77, 77, 78, 
	68, 79, 79, 79, 80, 68, 81, 81, 
	82, 81, 68, 82, 82, 82, 83, 68, 
	84, 84, 85, 84, 86, 68, 84, 84, 
	85, 84, 68, 87, 87, 87, 68, 88, 
	88, 89, 88, 68, 89, 89, 90, 91, 
	89, 92, 68, 92, 68, 93, 93, 94, 
	93, 95, 68, 93, 93, 94, 93, 68, 
	96, 96, 97, 98, 96, 99, 68, 99, 
	68, 100, 100, 101, 100, 102, 68, 100, 
	100, 101, 100, 68, 103, 103, 104, 105, 
	103, 106, 68, 106, 68, 107, 107, 108, 
	107, 109, 68, 107, 107, 108, 107, 68, 
	111, 110, 112, 110, 68, 111, 110, 112, 
	113, 110, 113, 113, 113, 68, 68, 111, 
	112, 115, 114, 116, 118, 114, 117, 118, 
	118, 118, 68, 111, 119, 112, 121, 119, 
	120, 121, 121, 121, 68, 120, 120, 121, 
	120, 120, 121, 121, 121, 68, 123, 122, 
	124, 121, 122, 120, 121, 121, 121, 68, 
	107, 107, 108, 107, 109, 68, 125, 68, 
	126, 126, 127, 126, 128, 68, 126, 126, 
	127, 126, 128, 68, 100, 100, 101, 100, 
	102, 68, 129, 68, 130, 130, 131, 130, 
	132, 68, 130, 130, 131, 130, 132, 68, 
	93, 93, 94, 93, 95, 68, 133, 68, 
	134, 134, 135, 134, 136, 68, 134, 134, 
	135, 134, 136, 68, 84, 84, 85, 84, 
	86, 68, 79, 79, 79, 80, 68, 137, 
	68, 138, 68, 139, 68, 141, 140, 140, 
	140, 140, 68, 142, 142, 142, 68, 142, 
	142, 142, 143, 68, 145, 144, 146, 144, 
	147, 68, 149, 148, 150, 148, 143, 68, 
	68, 149, 150, 145, 144, 146, 144, 147, 
	68, 151, 68, 152, 68, 153, 68, 154, 
	68, 155, 68, 156, 68, 157, 68, 158, 
	68, 159, 68, 160, 160, 160, 68, 160, 
	160, 160, 161, 68, 162, 162, 162, 163, 
	68, 162, 162, 162, 164, 68, 166, 165, 
	167, 165, 168, 68, 166, 165, 167, 165, 
	68, 68, 166, 167, 166, 165, 167, 165, 
	168, 68, 162, 162, 162, 163, 68, 169, 
	68, 170, 68, 171, 68, 172, 172, 172, 
	68, 172, 172, 173, 172, 68, 174, 68, 
	175, 68, 176, 68, 177, 177, 177, 68, 
	177, 177, 178, 177, 178, 178, 178, 68, 
	179, 179, 182, 181, 179, 180, 181, 181, 
	181, 68, 183, 183, 186, 185, 183, 184, 
	185, 185, 185, 68, 184, 184, 185, 184, 
	184, 185, 185, 185, 68, 187, 187, 188, 
	185, 187, 184, 185, 185, 185, 68, 186, 
	186, 189, 186, 189, 189, 189, 68, 191, 
	190, 192, 194, 190, 193, 194, 194, 194, 
	68, 196, 195, 197, 199, 195, 198, 199, 
	199, 199, 68, 68, 196, 197, 198, 198, 
	199, 198, 198, 199, 199, 199, 68, 201, 
	200, 202, 199, 200, 198, 199, 199, 199, 
	68, 2, 1, 3, 1, 0, 67, 70, 
	69, 71, 72, 73, 69, 68, 0
};

static const unsigned char _multiple_atom_stmt_test_trans_targs_wi[] = {
	0, 1, 1, 2, 3, 4, 5, 6, 
	7, 8, 46, 8, 9, 10, 11, 12, 
	45, 13, 13, 14, 15, 42, 16, 17, 
	18, 41, 18, 19, 38, 20, 21, 22, 
	37, 22, 23, 34, 24, 25, 26, 33, 
	27, 141, 28, 29, 30, 141, 28, 31, 
	32, 30, 31, 32, 30, 141, 28, 35, 
	25, 26, 36, 39, 21, 22, 40, 43, 
	17, 18, 44, 142, 0, 47, 47, 48, 
	93, 121, 49, 50, 51, 52, 53, 54, 
	92, 54, 55, 56, 57, 58, 91, 59, 
	59, 60, 61, 88, 62, 63, 64, 87, 
	64, 65, 84, 66, 67, 68, 83, 68, 
	69, 80, 70, 71, 72, 79, 73, 142, 
	74, 75, 76, 142, 74, 77, 78, 76, 
	77, 78, 76, 142, 74, 81, 71, 72, 
	82, 85, 67, 68, 86, 89, 63, 64, 
	90, 94, 95, 96, 97, 103, 98, 99, 
	100, 142, 101, 102, 100, 142, 101, 104, 
	105, 106, 107, 108, 109, 110, 111, 112, 
	113, 114, 115, 120, 116, 117, 142, 118, 
	119, 122, 123, 124, 125, 126, 127, 128, 
	129, 130, 131, 132, 133, 134, 135, 132, 
	133, 134, 135, 132, 135, 136, 137, 142, 
	138, 139, 140, 137, 142, 138, 139, 140, 
	137, 142, 138
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
	11, 46, 5, 41, 0, 0, 1, 0, 
	0, 0, 0, 0, 0, 0, 0, 21, 
	5, 0, 0, 0, 0, 0, 5, 23, 
	0, 0, 0, 0, 0, 0, 25, 5, 
	0, 0, 0, 0, 0, 27, 5, 0, 
	0, 0, 0, 0, 29, 5, 0, 71, 
	0, 0, 83, 121, 83, 13, 55, 0, 
	0, 15, 64, 108, 64, 0, 11, 52, 
	5, 0, 11, 49, 5, 0, 11, 46, 
	5, 0, 0, 0, 33, 0, 0, 0, 
	31, 87, 31, 5, 0, 43, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 5, 0, 0, 75, 0, 
	9, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 58, 13, 55, 58, 0, 
	0, 15, 0, 17, 17, 0, 61, 96, 
	61, 13, 55, 0, 79, 0, 0, 15, 
	19, 91, 19
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
	0, 0, 0, 0, 0, 37, 37
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
	0, 0, 0, 0, 0, 0, 39
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
	0, 0, 0, 0, 0, 0, 0
};

static const int multiple_atom_stmt_test_start = 141;
static const int multiple_atom_stmt_test_first_final = 141;
static const int multiple_atom_stmt_test_error = 0;

static const int multiple_atom_stmt_test_en_atom_stmt = 142;
static const int multiple_atom_stmt_test_en_main = 141;

#line 576 "NanorexMMPImportExportTest.rl"
	
#line 2615 "NanorexMMPImportExportTest.cpp"
	{
	cs = multiple_atom_stmt_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 577 "NanorexMMPImportExportTest.rl"
	
#line 2625 "NanorexMMPImportExportTest.cpp"
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
#line 2646 "NanorexMMPImportExportTest.cpp"
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
#line 550 "NanorexMMPImportExportTest.rl"
	{ //newAtom(atomId, atomicNum, x, y, z, atomStyle);
			// cerr << "calling, p = " << p << endl;
	         {stack[top++] = cs; cs = 142; goto _again;}}
	break;
	case 22:
#line 553 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
	case 25:
#line 542 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 26:
#line 543 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 27:
#line 544 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 28:
#line 545 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 29:
#line 546 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
#line 2835 "NanorexMMPImportExportTest.cpp"
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
#line 2856 "NanorexMMPImportExportTest.cpp"
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
#line 553 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
#line 2879 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 578 "NanorexMMPImportExportTest.rl"
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


#line 624 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::molLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 635 "NanorexMMPImportExportTest.rl"
	
#line 2936 "NanorexMMPImportExportTest.cpp"
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

#line 636 "NanorexMMPImportExportTest.rl"
	
#line 3047 "NanorexMMPImportExportTest.cpp"
	{
	cs = mol_decl_line_test_start;
	}
#line 637 "NanorexMMPImportExportTest.rl"
	
#line 3053 "NanorexMMPImportExportTest.cpp"
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
#line 620 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3170 "NanorexMMPImportExportTest.cpp"
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
#line 3183 "NanorexMMPImportExportTest.cpp"
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
#line 620 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3205 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 638 "NanorexMMPImportExportTest.rl"
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
	CERR("info chunk " << key << " = " << value);
	/// @todo
}


void NanorexMMPImportExportTest::groupLineTest(void)
{
	// clear group-name stack
	while(!groupNameStack.empty())
		groupNameStack.pop_back();
	
	char const *testInput = NULL;
	
	// #if 0
	testInput = "group (FirstGroup) #FirstGroupStyle\n";
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
		"group (group 1_1) #def\n"
		"egroup (group 1_1)\n"
		"group (amines)\n"
		"group (histamines) def\n"
		"group ( histhistamines\t) \t#def\t\n"
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


#line 756 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 769 "NanorexMMPImportExportTest.rl"
	
#line 3323 "NanorexMMPImportExportTest.cpp"
static const char _group_lines_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 5, 1, 6, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 11, 1, 
	12, 1, 13, 1, 14, 1, 17, 1, 
	18, 1, 21, 1, 22, 1, 26, 1, 
	29, 1, 31, 1, 32, 1, 36, 1, 
	37, 1, 39, 1, 53, 1, 54, 1, 
	61, 1, 62, 2, 0, 49, 2, 0, 
	51, 2, 0, 52, 2, 0, 60, 2, 
	5, 12, 2, 5, 13, 2, 5, 14, 
	2, 6, 7, 2, 6, 8, 2, 6, 
	9, 2, 8, 15, 2, 34, 24, 2, 
	37, 38, 3, 0, 16, 47, 3, 0, 
	19, 50, 3, 0, 20, 48, 3, 0, 
	23, 45, 3, 0, 25, 46, 3, 0, 
	27, 57, 3, 0, 28, 42, 3, 0, 
	28, 59, 3, 0, 30, 58, 3, 0, 
	33, 44, 3, 0, 33, 56, 3, 0, 
	35, 43, 3, 6, 8, 15, 3, 17, 
	0, 49, 3, 40, 0, 41, 3, 40, 
	0, 55, 4, 9, 0, 20, 48, 4, 
	9, 0, 23, 45, 4, 9, 0, 25, 
	46, 4, 9, 0, 35, 43, 4, 32, 
	0, 33, 44, 4, 32, 0, 33, 56, 
	5, 6, 9, 0, 20, 48, 5, 6, 
	9, 0, 23, 45, 5, 6, 9, 0, 
	25, 46, 5, 6, 9, 0, 35, 43, 
	5, 8, 15, 0, 16, 47, 6, 6, 
	8, 15, 0, 16, 47
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
	617, 629, 644, 659, 665, 667, 681, 696, 
	699, 702, 705, 710, 718, 721, 724, 727, 
	732, 744, 759, 774, 788, 803, 815, 830, 
	845, 847, 861, 876, 879, 882, 885, 888, 
	893, 905, 920, 935, 949, 964, 976, 991, 
	1006, 1008, 1022, 1037, 1040, 1043, 1046, 1049, 
	1052, 1055, 1058, 1061, 1066, 1078, 1093, 1108, 
	1122, 1137, 1149, 1164, 1179, 1181, 1195, 1210, 
	1213, 1216, 1221, 1227, 1239, 1254, 1269, 1275, 
	1288, 1290, 1305, 1320, 1334, 1349, 1363, 1378, 
	1380, 1382, 1389, 1392, 1395, 1398, 1401, 1404, 
	1411, 1418, 1420, 1433, 1445, 1460, 1475, 1481, 
	1495, 1510, 1513, 1516, 1519, 1522, 1528, 1534, 
	1548, 1563, 1578, 1584, 1586, 1600, 1615, 1631, 
	1647, 1663, 1679, 1695, 1711, 1727, 1743, 1758, 
	1773, 1779, 1781, 1797, 1813, 1829, 1844, 1860, 
	1876, 1892, 1908, 1923, 1938, 1944, 1946, 1946, 
	1946, 1958, 1969, 1976
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
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 110, -1, 10, 102, -1, 10, 
	111, -1, 10, 32, 9, 13, -1, 10, 
	32, 97, 99, 111, 9, 13, -1, 10, 
	116, -1, 10, 111, -1, 10, 109, -1, 
	10, 32, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 104, -1, 
	10, 117, -1, 10, 110, -1, 10, 107, 
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
	57, 65, 90, 97, 122, -1, 10, 112, 
	-1, 10, 101, -1, 10, 110, -1, 10, 
	103, -1, 10, 114, -1, 10, 111, -1, 
	10, 117, -1, 10, 112, -1, 10, 32, 
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
	97, 122, -1, 10, 111, -1, 10, 108, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
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
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, -1, 10, -1, 10, 
	32, 101, 103, 9, 13, -1, 10, 103, 
	-1, 10, 114, -1, 10, 111, -1, 10, 
	117, -1, 10, 112, -1, 10, 32, 35, 
	40, 9, 13, -1, 10, 32, 35, 40, 
	9, 13, -1, 10, -1, 10, 32, 41, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 67, 86, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 108, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 105, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 112, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 98, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 111, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 97, 9, 13, 45, 
	46, 48, 57, 65, 90, 98, 122, -1, 
	10, 32, 41, 95, 114, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 100, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 9, 13, -1, 10, -1, 10, 32, 
	41, 95, 105, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 101, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 119, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	68, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 97, 9, 13, 45, 46, 48, 57, 
	65, 90, 98, 122, -1, 10, 32, 41, 
	95, 116, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 97, 9, 13, 45, 46, 48, 57, 
	65, 90, 98, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, -1, 10, 32, 35, 97, 98, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	32, 97, 98, 101, 103, 105, 109, 9, 
	13, -1, 10, 32, 101, 103, 9, 13, 
	-1, 10, 32, 101, 103, 9, 13, 0
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
	4, 5, 5, 4, 2, 4, 5, 3, 
	3, 3, 3, 6, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 2, 
	2, 5, 3, 3, 3, 3, 3, 5, 
	5, 2, 5, 4, 5, 5, 4, 4, 
	5, 3, 3, 3, 3, 4, 4, 6, 
	5, 5, 4, 2, 4, 5, 6, 6, 
	6, 6, 6, 6, 6, 6, 5, 5, 
	4, 2, 6, 6, 6, 5, 6, 6, 
	6, 6, 5, 5, 4, 2, 0, 0, 
	10, 9, 5, 5
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
	4, 5, 5, 1, 0, 5, 5, 0, 
	0, 0, 1, 1, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	0, 1, 1, 4, 5, 5, 1, 4, 
	0, 5, 5, 5, 5, 5, 5, 0, 
	0, 1, 0, 0, 0, 0, 0, 1, 
	1, 0, 4, 4, 5, 5, 1, 5, 
	5, 0, 0, 0, 0, 1, 1, 4, 
	5, 5, 1, 0, 5, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 5, 5, 
	1, 0, 5, 5, 5, 5, 5, 5, 
	5, 5, 5, 5, 1, 0, 0, 0, 
	1, 1, 1, 1
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
	574, 583, 594, 605, 611, 614, 624, 635, 
	639, 643, 647, 652, 660, 664, 668, 672, 
	677, 686, 697, 708, 718, 729, 738, 749, 
	760, 763, 773, 784, 788, 792, 796, 800, 
	805, 814, 825, 836, 846, 857, 866, 877, 
	888, 891, 901, 912, 916, 920, 924, 928, 
	932, 936, 940, 944, 949, 958, 969, 980, 
	990, 1001, 1010, 1021, 1032, 1035, 1045, 1056, 
	1060, 1064, 1069, 1075, 1084, 1095, 1106, 1112, 
	1122, 1125, 1136, 1147, 1157, 1168, 1178, 1189, 
	1192, 1195, 1202, 1206, 1210, 1214, 1218, 1222, 
	1229, 1236, 1239, 1249, 1258, 1269, 1280, 1286, 
	1296, 1307, 1311, 1315, 1319, 1323, 1329, 1335, 
	1346, 1357, 1368, 1374, 1377, 1387, 1398, 1410, 
	1422, 1434, 1446, 1458, 1470, 1482, 1494, 1505, 
	1516, 1522, 1525, 1537, 1549, 1561, 1572, 1584, 
	1596, 1608, 1620, 1631, 1642, 1648, 1651, 1652, 
	1653, 1665, 1676, 1683
};

static const unsigned char _group_lines_test_trans_targs_wi[] = {
	232, 232, 1, 232, 233, 2, 3, 48, 
	76, 91, 103, 159, 2, 1, 232, 232, 
	4, 1, 232, 232, 5, 1, 232, 232, 
	6, 1, 232, 232, 7, 7, 1, 232, 
	232, 7, 7, 8, 1, 232, 232, 9, 
	9, 47, 1, 232, 232, 9, 10, 9, 
	1, 232, 232, 10, 10, 11, 1, 232, 
	232, 12, 13, 12, 46, 1, 232, 232, 
	12, 13, 12, 1, 232, 232, 14, 14, 
	1, 232, 232, 14, 15, 14, 1, 232, 
	232, 15, 16, 43, 15, 17, 1, 232, 
	232, 17, 1, 232, 232, 18, 19, 18, 
	42, 1, 232, 232, 18, 19, 18, 1, 
	232, 232, 19, 20, 39, 19, 21, 1, 
	232, 232, 21, 1, 232, 232, 22, 23, 
	22, 38, 1, 232, 232, 22, 23, 22, 
	1, 232, 232, 23, 24, 35, 23, 25, 
	1, 232, 232, 25, 1, 232, 232, 26, 
	27, 26, 34, 1, 232, 232, 26, 27, 
	26, 1, 232, 232, 28, 29, 28, 1, 
	232, 232, 28, 29, 30, 28, 30, 30, 
	30, 1, 232, 232, 29, 232, 232, 31, 
	29, 33, 31, 32, 33, 33, 33, 1, 
	232, 232, 31, 29, 33, 31, 32, 33, 
	33, 33, 1, 232, 232, 32, 33, 32, 
	32, 33, 33, 33, 1, 232, 232, 31, 
	29, 33, 31, 32, 33, 33, 33, 1, 
	232, 232, 26, 27, 26, 34, 1, 232, 
	232, 36, 1, 232, 232, 26, 27, 26, 
	37, 1, 232, 232, 26, 27, 26, 37, 
	1, 232, 232, 22, 23, 22, 38, 1, 
	232, 232, 40, 1, 232, 232, 22, 23, 
	22, 41, 1, 232, 232, 22, 23, 22, 
	41, 1, 232, 232, 18, 19, 18, 42, 
	1, 232, 232, 44, 1, 232, 232, 18, 
	19, 18, 45, 1, 232, 232, 18, 19, 
	18, 45, 1, 232, 232, 12, 13, 12, 
	46, 1, 232, 232, 9, 9, 47, 1, 
	232, 232, 49, 1, 232, 232, 50, 1, 
	232, 232, 51, 1, 232, 232, 58, 52, 
	52, 52, 52, 1, 232, 232, 53, 53, 
	1, 232, 232, 53, 53, 54, 1, 232, 
	232, 55, 56, 55, 57, 1, 232, 232, 
	55, 56, 55, 54, 1, 232, 232, 56, 
	232, 232, 55, 56, 55, 57, 1, 232, 
	232, 59, 1, 232, 232, 60, 1, 232, 
	232, 61, 1, 232, 232, 62, 1, 232, 
	232, 63, 1, 232, 232, 64, 1, 232, 
	232, 65, 1, 232, 232, 66, 1, 232, 
	232, 67, 1, 232, 232, 68, 68, 1, 
	232, 232, 68, 68, 69, 1, 232, 232, 
	70, 70, 75, 1, 232, 232, 70, 70, 
	71, 1, 232, 232, 72, 73, 72, 74, 
	1, 232, 232, 72, 73, 72, 1, 232, 
	232, 73, 232, 232, 72, 73, 72, 74, 
	1, 232, 232, 70, 70, 75, 1, 232, 
	232, 77, 1, 232, 232, 78, 1, 232, 
	232, 79, 1, 232, 232, 80, 1, 232, 
	232, 81, 1, 232, 232, 82, 83, 84, 
	82, 1, 232, 232, 82, 83, 84, 82, 
	1, 232, 232, 83, 232, 232, 85, 88, 
	86, 85, 86, 86, 86, 1, 232, 232, 
	85, 86, 85, 86, 86, 86, 1, 232, 
	232, 87, 88, 90, 87, 89, 90, 90, 
	90, 1, 232, 232, 87, 88, 90, 87, 
	89, 90, 90, 90, 1, 232, 232, 88, 
	83, 88, 1, 232, 232, 89, 90, 89, 
	89, 90, 90, 90, 1, 232, 232, 87, 
	88, 90, 87, 89, 90, 90, 90, 1, 
	232, 232, 92, 1, 232, 232, 93, 1, 
	232, 232, 94, 1, 232, 232, 95, 1, 
	232, 232, 95, 96, 95, 1, 232, 232, 
	96, 97, 96, 97, 97, 97, 1, 232, 
	232, 98, 99, 102, 98, 101, 102, 102, 
	102, 1, 232, 232, 98, 99, 102, 98, 
	101, 102, 102, 102, 1, 232, 232, 99, 
	100, 99, 1, 232, 232, 100, 232, 232, 
	101, 102, 101, 101, 102, 102, 102, 1, 
	232, 232, 98, 99, 102, 98, 101, 102, 
	102, 102, 1, 232, 232, 104, 1, 232, 
	232, 105, 1, 232, 232, 106, 1, 232, 
	232, 107, 107, 1, 232, 232, 107, 108, 
	123, 139, 107, 1, 232, 232, 109, 1, 
	232, 232, 110, 1, 232, 232, 111, 1, 
	232, 232, 112, 112, 1, 232, 232, 112, 
	113, 112, 113, 113, 113, 1, 232, 232, 
	114, 117, 116, 114, 115, 116, 116, 116, 
	1, 232, 232, 114, 117, 116, 114, 115, 
	116, 116, 116, 1, 232, 232, 115, 116, 
	115, 115, 116, 116, 116, 1, 232, 232, 
	114, 117, 116, 114, 115, 116, 116, 116, 
	1, 232, 232, 117, 118, 117, 118, 118, 
	118, 1, 232, 232, 119, 120, 122, 119, 
	121, 122, 122, 122, 1, 232, 232, 119, 
	120, 122, 119, 121, 122, 122, 122, 1, 
	232, 232, 120, 232, 232, 121, 122, 121, 
	121, 122, 122, 122, 1, 232, 232, 119, 
	120, 122, 119, 121, 122, 122, 122, 1, 
	232, 232, 124, 1, 232, 232, 125, 1, 
	232, 232, 126, 1, 232, 232, 127, 1, 
	232, 232, 128, 128, 1, 232, 232, 128, 
	129, 128, 129, 129, 129, 1, 232, 232, 
	130, 133, 132, 130, 131, 132, 132, 132, 
	1, 232, 232, 130, 133, 132, 130, 131, 
	132, 132, 132, 1, 232, 232, 131, 132, 
	131, 131, 132, 132, 132, 1, 232, 232, 
	130, 133, 132, 130, 131, 132, 132, 132, 
	1, 232, 232, 133, 134, 133, 134, 134, 
	134, 1, 232, 232, 135, 136, 138, 135, 
	137, 138, 138, 138, 1, 232, 232, 135, 
	136, 138, 135, 137, 138, 138, 138, 1, 
	232, 232, 136, 232, 232, 137, 138, 137, 
	137, 138, 138, 138, 1, 232, 232, 135, 
	136, 138, 135, 137, 138, 138, 138, 1, 
	232, 232, 140, 1, 232, 232, 141, 1, 
	232, 232, 142, 1, 232, 232, 143, 1, 
	232, 232, 144, 1, 232, 232, 145, 1, 
	232, 232, 146, 1, 232, 232, 147, 1, 
	232, 232, 148, 148, 1, 232, 232, 148, 
	149, 148, 149, 149, 149, 1, 232, 232, 
	150, 153, 152, 150, 151, 152, 152, 152, 
	1, 232, 232, 150, 153, 152, 150, 151, 
	152, 152, 152, 1, 232, 232, 151, 152, 
	151, 151, 152, 152, 152, 1, 232, 232, 
	150, 153, 152, 150, 151, 152, 152, 152, 
	1, 232, 232, 153, 154, 153, 154, 154, 
	154, 1, 232, 232, 155, 156, 158, 155, 
	157, 158, 158, 158, 1, 232, 232, 155, 
	156, 158, 155, 157, 158, 158, 158, 1, 
	232, 232, 156, 232, 232, 157, 158, 157, 
	157, 158, 158, 158, 1, 232, 232, 155, 
	156, 158, 155, 157, 158, 158, 158, 1, 
	232, 232, 160, 1, 232, 232, 161, 1, 
	232, 232, 162, 162, 1, 232, 232, 162, 
	163, 162, 1, 232, 232, 163, 164, 163, 
	164, 164, 164, 1, 232, 232, 165, 166, 
	174, 165, 173, 174, 174, 174, 1, 232, 
	232, 165, 166, 174, 165, 173, 174, 174, 
	174, 1, 232, 232, 167, 168, 167, 1, 
	232, 232, 167, 168, 169, 167, 169, 169, 
	169, 1, 232, 232, 168, 232, 232, 170, 
	168, 172, 170, 171, 172, 172, 172, 1, 
	232, 232, 170, 168, 172, 170, 171, 172, 
	172, 172, 1, 232, 232, 171, 172, 171, 
	171, 172, 172, 172, 1, 232, 232, 170, 
	168, 172, 170, 171, 172, 172, 172, 1, 
	232, 232, 173, 174, 173, 173, 174, 174, 
	174, 1, 232, 232, 165, 166, 174, 165, 
	173, 174, 174, 174, 1, 0, 232, 175, 
	234, 234, 176, 234, 235, 177, 178, 193, 
	177, 176, 234, 234, 179, 176, 234, 234, 
	180, 176, 234, 234, 181, 176, 234, 234, 
	182, 176, 234, 234, 183, 176, 234, 234, 
	184, 185, 186, 184, 176, 234, 234, 184, 
	185, 186, 184, 176, 234, 234, 185, 234, 
	234, 187, 190, 188, 187, 188, 188, 188, 
	176, 234, 234, 187, 188, 187, 188, 188, 
	188, 176, 234, 234, 189, 190, 192, 189, 
	191, 192, 192, 192, 176, 234, 234, 189, 
	190, 192, 189, 191, 192, 192, 192, 176, 
	234, 234, 190, 185, 190, 176, 234, 234, 
	191, 192, 191, 191, 192, 192, 192, 176, 
	234, 234, 189, 190, 192, 189, 191, 192, 
	192, 192, 176, 234, 234, 194, 176, 234, 
	234, 195, 176, 234, 234, 196, 176, 234, 
	234, 197, 176, 234, 234, 198, 199, 198, 
	176, 234, 234, 198, 199, 198, 176, 234, 
	234, 199, 206, 218, 200, 199, 200, 200, 
	200, 176, 234, 234, 201, 202, 205, 201, 
	204, 205, 205, 205, 176, 234, 234, 201, 
	202, 205, 201, 204, 205, 205, 205, 176, 
	234, 234, 202, 203, 202, 176, 234, 234, 
	203, 234, 234, 204, 205, 204, 204, 205, 
	205, 205, 176, 234, 234, 201, 202, 205, 
	201, 204, 205, 205, 205, 176, 234, 234, 
	201, 202, 205, 207, 201, 204, 205, 205, 
	205, 176, 234, 234, 201, 202, 205, 208, 
	201, 204, 205, 205, 205, 176, 234, 234, 
	201, 202, 205, 209, 201, 204, 205, 205, 
	205, 176, 234, 234, 201, 202, 205, 210, 
	201, 204, 205, 205, 205, 176, 234, 234, 
	201, 202, 205, 211, 201, 204, 205, 205, 
	205, 176, 234, 234, 201, 202, 205, 212, 
	201, 204, 205, 205, 205, 176, 234, 234, 
	201, 202, 205, 213, 201, 204, 205, 205, 
	205, 176, 234, 234, 201, 202, 205, 214, 
	201, 204, 205, 205, 205, 176, 234, 234, 
	215, 216, 205, 215, 204, 205, 205, 205, 
	176, 234, 234, 215, 216, 205, 215, 204, 
	205, 205, 205, 176, 234, 234, 216, 217, 
	216, 176, 234, 234, 217, 234, 234, 201, 
	202, 205, 219, 201, 204, 205, 205, 205, 
	176, 234, 234, 201, 202, 205, 220, 201, 
	204, 205, 205, 205, 176, 234, 234, 201, 
	202, 205, 221, 201, 204, 205, 205, 205, 
	176, 234, 234, 222, 202, 205, 222, 204, 
	205, 205, 205, 176, 234, 234, 222, 202, 
	223, 205, 222, 204, 205, 205, 205, 176, 
	234, 234, 201, 202, 205, 224, 201, 204, 
	205, 205, 205, 176, 234, 234, 201, 202, 
	205, 225, 201, 204, 205, 205, 205, 176, 
	234, 234, 201, 202, 205, 226, 201, 204, 
	205, 205, 205, 176, 234, 234, 227, 228, 
	205, 227, 204, 205, 205, 205, 176, 234, 
	234, 227, 228, 205, 227, 204, 205, 205, 
	205, 176, 234, 234, 202, 229, 202, 176, 
	234, 234, 229, 231, 231, 0, 233, 2, 
	175, 3, 48, 76, 91, 103, 159, 2, 
	1, 232, 233, 2, 3, 48, 76, 91, 
	103, 159, 2, 1, 0, 235, 177, 178, 
	193, 177, 176, 234, 235, 177, 178, 193, 
	177, 176, 0
};

static const unsigned char _group_lines_test_trans_actions_wi[] = {
	53, 65, 0, 53, 154, 0, 0, 0, 
	41, 0, 92, 33, 0, 0, 53, 65, 
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
	0, 0, 53, 98, 0, 0, 0, 0, 
	53, 98, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 98, 0, 53, 222, 146, 
	146, 80, 146, 11, 80, 80, 80, 0, 
	53, 98, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 216, 89, 
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
	150, 29, 29, 29, 3, 0, 53, 59, 
	0, 0, 0, 0, 0, 53, 59, 0, 
	53, 150, 29, 29, 29, 3, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 0, 
	53, 65, 0, 0, 0, 0, 53, 65, 
	0, 0, 3, 0, 53, 65, 0, 0, 
	0, 0, 53, 102, 0, 0, 0, 7, 
	0, 53, 102, 0, 0, 0, 0, 53, 
	102, 0, 53, 102, 0, 0, 0, 7, 
	0, 53, 65, 0, 0, 3, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 182, 43, 43, 43, 
	43, 0, 53, 134, 0, 0, 0, 0, 
	0, 53, 134, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 0, 0, 53, 65, 
	0, 0, 0, 0, 0, 0, 0, 53, 
	65, 83, 83, 80, 83, 11, 80, 80, 
	80, 0, 53, 65, 0, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 134, 0, 
	0, 0, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 65, 15, 
	15, 13, 15, 0, 13, 13, 13, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 0, 0, 53, 65, 
	0, 0, 0, 0, 0, 0, 0, 53, 
	65, 83, 83, 80, 83, 11, 80, 80, 
	80, 0, 53, 65, 0, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 122, 0, 
	0, 0, 0, 53, 122, 0, 53, 65, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 65, 15, 15, 13, 15, 0, 13, 
	13, 13, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 53, 65, 0, 0, 53, 
	65, 0, 0, 0, 53, 65, 0, 0, 
	0, 0, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 0, 53, 65, 0, 
	0, 0, 0, 0, 0, 0, 53, 65, 
	83, 83, 80, 83, 11, 80, 80, 80, 
	0, 53, 65, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 53, 65, 0, 13, 
	0, 0, 13, 13, 13, 0, 53, 65, 
	15, 15, 13, 15, 0, 13, 13, 13, 
	0, 53, 65, 0, 0, 0, 0, 0, 
	0, 0, 53, 192, 86, 86, 80, 86, 
	11, 80, 80, 80, 0, 53, 106, 0, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 106, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 162, 17, 
	17, 13, 17, 0, 13, 13, 13, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 0, 53, 65, 0, 
	0, 0, 0, 0, 0, 0, 53, 65, 
	83, 83, 80, 83, 11, 80, 80, 80, 
	0, 53, 65, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 53, 65, 0, 13, 
	0, 0, 13, 13, 13, 0, 53, 65, 
	15, 15, 13, 15, 0, 13, 13, 13, 
	0, 53, 65, 0, 0, 0, 0, 0, 
	0, 0, 53, 204, 86, 86, 80, 86, 
	11, 80, 80, 80, 0, 53, 114, 0, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 114, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 172, 17, 
	17, 13, 17, 0, 13, 13, 13, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 0, 53, 65, 0, 
	0, 0, 0, 0, 0, 0, 53, 65, 
	83, 83, 80, 83, 11, 80, 80, 80, 
	0, 53, 65, 0, 0, 13, 0, 0, 
	13, 13, 13, 0, 53, 65, 0, 13, 
	0, 0, 13, 13, 13, 0, 53, 65, 
	15, 15, 13, 15, 0, 13, 13, 13, 
	0, 53, 65, 0, 0, 0, 0, 0, 
	0, 0, 53, 210, 86, 86, 80, 86, 
	11, 80, 80, 80, 0, 53, 142, 0, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	53, 142, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 177, 17, 
	17, 13, 17, 0, 13, 13, 13, 0, 
	53, 65, 0, 0, 53, 65, 0, 0, 
	53, 65, 0, 0, 0, 53, 65, 0, 
	0, 0, 0, 53, 65, 0, 0, 0, 
	0, 0, 0, 0, 53, 65, 83, 83, 
	80, 83, 11, 80, 80, 80, 0, 53, 
	65, 0, 0, 13, 0, 0, 13, 13, 
	13, 0, 53, 110, 0, 0, 0, 0, 
	53, 110, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 110, 0, 53, 198, 86, 
	86, 80, 86, 11, 80, 80, 80, 0, 
	53, 110, 0, 0, 13, 0, 0, 13, 
	13, 13, 0, 53, 65, 0, 13, 0, 
	0, 13, 13, 13, 0, 53, 167, 17, 
	17, 13, 17, 0, 13, 13, 13, 0, 
	53, 65, 0, 13, 0, 0, 13, 13, 
	13, 0, 53, 65, 15, 15, 13, 15, 
	0, 13, 13, 13, 0, 0, 62, 0, 
	57, 68, 0, 57, 158, 0, 41, 39, 
	0, 0, 57, 68, 0, 0, 57, 68, 
	0, 0, 57, 68, 0, 0, 57, 68, 
	0, 0, 57, 68, 0, 0, 57, 187, 
	43, 43, 43, 43, 0, 57, 138, 0, 
	0, 0, 0, 0, 57, 138, 0, 57, 
	68, 0, 0, 0, 0, 0, 0, 0, 
	0, 57, 68, 0, 0, 0, 0, 0, 
	0, 0, 57, 68, 83, 83, 80, 83, 
	11, 80, 80, 80, 0, 57, 68, 0, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	57, 138, 0, 0, 0, 0, 57, 68, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	57, 68, 15, 15, 13, 15, 0, 13, 
	13, 13, 0, 57, 68, 0, 0, 57, 
	68, 0, 0, 57, 68, 0, 0, 57, 
	68, 0, 0, 57, 68, 37, 37, 37, 
	0, 57, 68, 0, 0, 0, 0, 57, 
	68, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 57, 68, 83, 83, 80, 83, 
	11, 80, 80, 80, 0, 57, 68, 0, 
	0, 13, 0, 0, 13, 13, 13, 0, 
	57, 126, 0, 0, 0, 0, 57, 126, 
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
	13, 13, 13, 0, 57, 130, 0, 0, 
	0, 0, 57, 130, 0, 57, 68, 83, 
	83, 80, 80, 83, 11, 80, 80, 80, 
	0, 57, 68, 15, 15, 13, 13, 15, 
	0, 13, 13, 13, 0, 57, 68, 15, 
	15, 13, 13, 15, 0, 13, 13, 13, 
	0, 57, 68, 15, 15, 13, 15, 0, 
	13, 13, 13, 0, 57, 68, 0, 0, 
	13, 13, 0, 0, 13, 13, 13, 0, 
	57, 68, 15, 15, 13, 13, 15, 0, 
	13, 13, 13, 0, 57, 68, 15, 15, 
	13, 13, 15, 0, 13, 13, 13, 0, 
	57, 68, 15, 15, 13, 13, 15, 0, 
	13, 13, 13, 0, 57, 68, 15, 15, 
	13, 15, 0, 13, 13, 13, 0, 57, 
	68, 0, 0, 13, 0, 0, 13, 13, 
	13, 0, 57, 118, 0, 0, 0, 0, 
	57, 118, 0, 45, 0, 0, 154, 0, 
	0, 0, 0, 41, 0, 92, 33, 0, 
	0, 51, 154, 0, 0, 0, 41, 0, 
	92, 33, 0, 0, 0, 158, 0, 41, 
	39, 0, 0, 55, 158, 0, 41, 39, 
	0, 0, 0
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
	0, 35, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 47, 47, 
	95, 0, 95, 0
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
	49, 0, 49, 0
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
	0, 0, 0, 0, 0, 0, 45, 0, 
	0, 0, 0, 0
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
	1, 1, 1, 1, 1, 1, 1, 0, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 283, 283, 
	283, 283, 283, 283, 283, 283, 0, 0, 
	0, 369, 0, 370
};

static const int group_lines_test_start = 230;
static const int group_lines_test_first_final = 230;
static const int group_lines_test_error = 0;

static const int group_lines_test_en_group_scanner = 232;
static const int group_lines_test_en_mini_group_scanner = 234;
static const int group_lines_test_en_main = 230;

#line 770 "NanorexMMPImportExportTest.rl"
	
#line 4311 "NanorexMMPImportExportTest.cpp"
	{
	cs = group_lines_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 771 "NanorexMMPImportExportTest.rl"
	
#line 4321 "NanorexMMPImportExportTest.cpp"
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
	case 39:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 4342 "NanorexMMPImportExportTest.cpp"
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
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal/*, stringVal2*/); }
	break;
	case 29:
#line 51 "NanorexMMPImportExportTest.rl"
	{ lineStart = p; }
	break;
	case 30:
#line 56 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 31:
#line 60 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 32:
#line 61 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 33:
#line 67 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 34:
#line 71 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 35:
#line 81 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 36:
#line 754 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 234; goto _again;} }
	break;
	case 40:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 41:
#line 102 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 42:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 43:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 44:
#line 91 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 45:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
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
#line 100 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 53:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 54:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
	case 55:
#line 751 "NanorexMMPImportExportTest.rl"
	{act = 16;}
	break;
	case 56:
#line 742 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 57:
#line 743 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 58:
#line 744 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 59:
#line 745 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 60:
#line 751 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 61:
#line 751 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 62:
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
#line 4680 "NanorexMMPImportExportTest.cpp"
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
	case 37:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 38:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 4709 "NanorexMMPImportExportTest.cpp"
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
	case 36:
#line 754 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 234; goto _again;} }
	break;
#line 4732 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 772 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::newViewDataGroup(void)
{
	++groupCount;
	CERR("group (View Data)");
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
NanorexMMPImportExportTest::newMolStructGroup(std::string const& name)
{
	++groupCount;
	CERR("group (" + name + ") ");
	currentGroupName = name;
	groupNameStack.push_back(currentGroupName);
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
	CERR("group (Clipboard)");
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
	CERR("egroup (" + name + ")  " + "[stack-top = " + groupNameStack.back()
	     + ']');
	currentGroupName = groupNameStack.back();
	groupNameStack.pop_back();
}


void
NanorexMMPImportExportTest::newOpenGroupInfo(string const& key,
                                             string const& value)
{
	++infoOpenGroupCount;
	CERR("info opengroup " + key + " = " + value);
	/// @todo
}


void NanorexMMPImportExportTest::end1(void)
{
	CERR("end1");
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


#line 913 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::uncheckedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 926 "NanorexMMPImportExportTest.rl"
	
#line 4879 "NanorexMMPImportExportTest.cpp"
static const char _unchecked_parse_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 30, 1, 32, 1, 33, 1, 
	40, 1, 42, 1, 56, 1, 57, 2, 
	0, 29, 2, 0, 52, 2, 0, 54, 
	2, 0, 55, 2, 5, 12, 2, 5, 
	13, 2, 5, 14, 2, 6, 7, 2, 
	6, 8, 2, 6, 9, 2, 8, 15, 
	2, 35, 24, 2, 40, 41, 3, 0, 
	16, 50, 3, 0, 19, 53, 3, 0, 
	20, 51, 3, 0, 23, 48, 3, 0, 
	25, 49, 3, 0, 27, 37, 3, 0, 
	28, 38, 3, 0, 28, 45, 3, 0, 
	31, 39, 3, 0, 34, 47, 3, 0, 
	36, 46, 3, 6, 8, 15, 3, 17, 
	0, 52, 3, 43, 0, 44, 4, 9, 
	0, 20, 51, 4, 9, 0, 23, 48, 
	4, 9, 0, 25, 49, 4, 9, 0, 
	36, 46, 4, 33, 0, 34, 47, 5, 
	6, 9, 0, 20, 51, 5, 6, 9, 
	0, 23, 48, 5, 6, 9, 0, 25, 
	49, 5, 6, 9, 0, 36, 46, 5, 
	8, 15, 0, 16, 50, 6, 6, 8, 
	15, 0, 16, 50
};

static const short _unchecked_parse_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 14, 
	19, 24, 25, 26, 27, 31, 36, 37, 
	38, 39, 44, 46, 51, 52, 53, 54, 
	55, 60, 71, 85, 99, 104, 109, 110, 
	111, 112, 117, 122, 123, 124, 125, 126, 
	131, 136, 137, 138, 139, 140, 141, 142, 
	143, 144, 149, 154, 156, 158, 160, 173, 
	187, 189, 191, 202, 205, 208, 211, 216, 
	223, 230, 236, 243, 251, 257, 262, 268, 
	277, 281, 289, 295, 304, 308, 316, 322, 
	331, 335, 343, 349, 355, 368, 370, 385, 
	400, 414, 429, 437, 441, 449, 457, 465, 
	469, 477, 485, 493, 497, 505, 513, 521, 
	528, 531, 534, 537, 545, 550, 557, 565, 
	573, 575, 583, 586, 589, 592, 595, 598, 
	601, 604, 607, 610, 615, 622, 629, 636, 
	644, 650, 652, 660, 667, 670, 673, 676, 
	679, 682, 689, 696, 698, 711, 723, 738, 
	753, 759, 773, 788, 791, 794, 797, 800, 
	806, 818, 833, 848, 854, 856, 870, 885, 
	888, 891, 894, 899, 907, 910, 913, 916, 
	921, 933, 948, 963, 977, 992, 1004, 1019, 
	1034, 1036, 1050, 1065, 1068, 1071, 1074, 1077, 
	1082, 1094, 1109, 1124, 1138, 1153, 1165, 1180, 
	1195, 1197, 1211, 1226, 1229, 1232, 1235, 1238, 
	1241, 1244, 1247, 1250, 1255, 1267, 1282, 1297, 
	1311, 1326, 1338, 1353, 1368, 1370, 1384, 1399, 
	1402, 1405, 1410, 1416, 1428, 1443, 1458, 1464, 
	1477, 1479, 1494, 1509, 1523, 1538, 1552, 1567, 
	1569, 1569, 1581
};

static const char _unchecked_parse_test_trans_keys[] = {
	10, 32, 103, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	40, 11, 13, 9, 32, 86, 11, 13, 
	105, 101, 119, 9, 32, 11, 13, 9, 
	32, 68, 11, 13, 97, 116, 97, 9, 
	32, 41, 11, 13, 10, 35, 10, 32, 
	103, 9, 13, 114, 111, 117, 112, 9, 
	32, 40, 11, 13, 9, 32, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 9, 13, 
	10, 32, 101, 9, 13, 110, 100, 49, 
	10, 32, 35, 9, 13, 10, 32, 103, 
	9, 13, 114, 111, 117, 112, 9, 32, 
	40, 11, 13, 9, 32, 67, 11, 13, 
	108, 105, 112, 98, 111, 97, 114, 100, 
	9, 32, 41, 11, 13, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, -1, 10, 
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
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 110, 
	-1, 10, 102, -1, 10, 111, -1, 10, 
	32, 9, 13, -1, 10, 32, 97, 99, 
	111, 9, 13, -1, 10, 116, -1, 10, 
	111, -1, 10, 109, -1, 10, 32, 9, 
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
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
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 112, -1, 10, 101, 
	-1, 10, 110, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 9, 13, -1, 
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
	10, 111, -1, 10, 108, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, 32, 35, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 97, 98, 101, 
	103, 105, 109, 9, 13, -1, 10, 32, 
	97, 98, 101, 103, 105, 109, 9, 13, 
	0
};

static const char _unchecked_parse_test_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 3, 3, 
	3, 1, 1, 1, 2, 3, 1, 1, 
	1, 3, 2, 3, 1, 1, 1, 1, 
	3, 3, 4, 4, 3, 3, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 3, 
	3, 1, 1, 1, 1, 1, 1, 1, 
	1, 3, 3, 2, 2, 2, 3, 4, 
	2, 2, 9, 3, 3, 3, 3, 3, 
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
	4, 5, 5, 4, 2, 4, 5, 3, 
	3, 3, 3, 6, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 2, 
	0, 10, 9
};

static const char _unchecked_parse_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 1, 1, 
	1, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 0, 1, 0, 0, 0, 0, 
	1, 4, 5, 5, 1, 1, 0, 0, 
	0, 1, 1, 0, 0, 0, 0, 1, 
	1, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 1, 0, 0, 0, 5, 5, 
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
	4, 5, 5, 1, 0, 5, 5, 0, 
	0, 0, 1, 1, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 4, 5, 5, 5, 
	5, 4, 5, 5, 0, 5, 5, 0, 
	0, 1, 1, 4, 5, 5, 1, 4, 
	0, 5, 5, 5, 5, 5, 5, 0, 
	0, 1, 1
};

static const short _unchecked_parse_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 18, 
	23, 28, 30, 32, 34, 38, 43, 45, 
	47, 49, 54, 57, 62, 64, 66, 68, 
	70, 75, 83, 93, 103, 108, 113, 115, 
	117, 119, 124, 129, 131, 133, 135, 137, 
	142, 147, 149, 151, 153, 155, 157, 159, 
	161, 163, 168, 173, 176, 179, 182, 191, 
	201, 204, 207, 218, 222, 226, 230, 235, 
	241, 247, 253, 259, 266, 272, 277, 283, 
	291, 295, 302, 308, 316, 320, 327, 333, 
	341, 345, 352, 358, 364, 374, 377, 388, 
	399, 409, 420, 427, 431, 438, 445, 452, 
	456, 463, 470, 477, 481, 488, 495, 502, 
	508, 512, 516, 520, 528, 533, 539, 546, 
	553, 556, 563, 567, 571, 575, 579, 583, 
	587, 591, 595, 599, 604, 610, 616, 622, 
	629, 635, 638, 645, 651, 655, 659, 663, 
	667, 671, 678, 685, 688, 698, 707, 718, 
	729, 735, 745, 756, 760, 764, 768, 772, 
	778, 787, 798, 809, 815, 818, 828, 839, 
	843, 847, 851, 856, 864, 868, 872, 876, 
	881, 890, 901, 912, 922, 933, 942, 953, 
	964, 967, 977, 988, 992, 996, 1000, 1004, 
	1009, 1018, 1029, 1040, 1050, 1061, 1070, 1081, 
	1092, 1095, 1105, 1116, 1120, 1124, 1128, 1132, 
	1136, 1140, 1144, 1148, 1153, 1162, 1173, 1184, 
	1194, 1205, 1214, 1225, 1236, 1239, 1249, 1260, 
	1264, 1268, 1273, 1279, 1288, 1299, 1310, 1316, 
	1326, 1329, 1340, 1351, 1361, 1372, 1382, 1393, 
	1396, 1397, 1409
};

static const unsigned char _unchecked_parse_test_trans_targs_wi[] = {
	1, 1, 2, 1, 0, 3, 0, 4, 
	0, 5, 0, 6, 0, 7, 7, 8, 
	7, 0, 7, 7, 8, 7, 0, 8, 
	8, 9, 8, 0, 10, 0, 11, 0, 
	12, 0, 13, 13, 13, 0, 13, 13, 
	14, 13, 0, 15, 0, 16, 0, 17, 
	0, 17, 17, 18, 17, 0, 19, 56, 
	0, 19, 19, 20, 19, 0, 21, 0, 
	22, 0, 23, 0, 24, 0, 24, 24, 
	25, 24, 0, 25, 25, 26, 25, 26, 
	26, 26, 0, 27, 27, 28, 55, 27, 
	54, 55, 55, 55, 0, 27, 27, 28, 
	55, 27, 54, 55, 55, 55, 0, 29, 
	28, 53, 28, 0, 29, 29, 30, 29, 
	0, 31, 0, 32, 0, 33, 0, 34, 
	33, 52, 33, 0, 34, 34, 35, 34, 
	0, 36, 0, 37, 0, 38, 0, 39, 
	0, 39, 39, 40, 39, 0, 40, 40, 
	41, 40, 0, 42, 0, 43, 0, 44, 
	0, 45, 0, 46, 0, 47, 0, 48, 
	0, 49, 0, 49, 49, 50, 49, 0, 
	232, 50, 51, 50, 0, 0, 232, 51, 
	0, 34, 52, 0, 29, 53, 54, 54, 
	55, 54, 54, 55, 55, 55, 0, 27, 
	27, 28, 55, 27, 54, 55, 55, 55, 
	0, 0, 19, 56, 233, 233, 57, 233, 
	234, 58, 59, 104, 132, 147, 159, 215, 
	58, 57, 233, 233, 60, 57, 233, 233, 
	61, 57, 233, 233, 62, 57, 233, 233, 
	63, 63, 57, 233, 233, 63, 63, 64, 
	57, 233, 233, 65, 65, 103, 57, 233, 
	233, 65, 66, 65, 57, 233, 233, 66, 
	66, 67, 57, 233, 233, 68, 69, 68, 
	102, 57, 233, 233, 68, 69, 68, 57, 
	233, 233, 70, 70, 57, 233, 233, 70, 
	71, 70, 57, 233, 233, 71, 72, 99, 
	71, 73, 57, 233, 233, 73, 57, 233, 
	233, 74, 75, 74, 98, 57, 233, 233, 
	74, 75, 74, 57, 233, 233, 75, 76, 
	95, 75, 77, 57, 233, 233, 77, 57, 
	233, 233, 78, 79, 78, 94, 57, 233, 
	233, 78, 79, 78, 57, 233, 233, 79, 
	80, 91, 79, 81, 57, 233, 233, 81, 
	57, 233, 233, 82, 83, 82, 90, 57, 
	233, 233, 82, 83, 82, 57, 233, 233, 
	84, 85, 84, 57, 233, 233, 84, 85, 
	86, 84, 86, 86, 86, 57, 233, 233, 
	85, 233, 233, 87, 85, 89, 87, 88, 
	89, 89, 89, 57, 233, 233, 87, 85, 
	89, 87, 88, 89, 89, 89, 57, 233, 
	233, 88, 89, 88, 88, 89, 89, 89, 
	57, 233, 233, 87, 85, 89, 87, 88, 
	89, 89, 89, 57, 233, 233, 82, 83, 
	82, 90, 57, 233, 233, 92, 57, 233, 
	233, 82, 83, 82, 93, 57, 233, 233, 
	82, 83, 82, 93, 57, 233, 233, 78, 
	79, 78, 94, 57, 233, 233, 96, 57, 
	233, 233, 78, 79, 78, 97, 57, 233, 
	233, 78, 79, 78, 97, 57, 233, 233, 
	74, 75, 74, 98, 57, 233, 233, 100, 
	57, 233, 233, 74, 75, 74, 101, 57, 
	233, 233, 74, 75, 74, 101, 57, 233, 
	233, 68, 69, 68, 102, 57, 233, 233, 
	65, 65, 103, 57, 233, 233, 105, 57, 
	233, 233, 106, 57, 233, 233, 107, 57, 
	233, 233, 114, 108, 108, 108, 108, 57, 
	233, 233, 109, 109, 57, 233, 233, 109, 
	109, 110, 57, 233, 233, 111, 112, 111, 
	113, 57, 233, 233, 111, 112, 111, 110, 
	57, 233, 233, 112, 233, 233, 111, 112, 
	111, 113, 57, 233, 233, 115, 57, 233, 
	233, 116, 57, 233, 233, 117, 57, 233, 
	233, 118, 57, 233, 233, 119, 57, 233, 
	233, 120, 57, 233, 233, 121, 57, 233, 
	233, 122, 57, 233, 233, 123, 57, 233, 
	233, 124, 124, 57, 233, 233, 124, 124, 
	125, 57, 233, 233, 126, 126, 131, 57, 
	233, 233, 126, 126, 127, 57, 233, 233, 
	128, 129, 128, 130, 57, 233, 233, 128, 
	129, 128, 57, 233, 233, 129, 233, 233, 
	128, 129, 128, 130, 57, 233, 233, 126, 
	126, 131, 57, 233, 233, 133, 57, 233, 
	233, 134, 57, 233, 233, 135, 57, 233, 
	233, 136, 57, 233, 233, 137, 57, 233, 
	233, 138, 139, 140, 138, 57, 233, 233, 
	138, 139, 140, 138, 57, 233, 233, 139, 
	233, 233, 141, 144, 142, 141, 142, 142, 
	142, 57, 233, 233, 141, 142, 141, 142, 
	142, 142, 57, 233, 233, 143, 144, 146, 
	143, 145, 146, 146, 146, 57, 233, 233, 
	143, 144, 146, 143, 145, 146, 146, 146, 
	57, 233, 233, 144, 139, 144, 57, 233, 
	233, 145, 146, 145, 145, 146, 146, 146, 
	57, 233, 233, 143, 144, 146, 143, 145, 
	146, 146, 146, 57, 233, 233, 148, 57, 
	233, 233, 149, 57, 233, 233, 150, 57, 
	233, 233, 151, 57, 233, 233, 151, 152, 
	151, 57, 233, 233, 152, 153, 152, 153, 
	153, 153, 57, 233, 233, 154, 155, 158, 
	154, 157, 158, 158, 158, 57, 233, 233, 
	154, 155, 158, 154, 157, 158, 158, 158, 
	57, 233, 233, 155, 156, 155, 57, 233, 
	233, 156, 233, 233, 157, 158, 157, 157, 
	158, 158, 158, 57, 233, 233, 154, 155, 
	158, 154, 157, 158, 158, 158, 57, 233, 
	233, 160, 57, 233, 233, 161, 57, 233, 
	233, 162, 57, 233, 233, 163, 163, 57, 
	233, 233, 163, 164, 179, 195, 163, 57, 
	233, 233, 165, 57, 233, 233, 166, 57, 
	233, 233, 167, 57, 233, 233, 168, 168, 
	57, 233, 233, 168, 169, 168, 169, 169, 
	169, 57, 233, 233, 170, 173, 172, 170, 
	171, 172, 172, 172, 57, 233, 233, 170, 
	173, 172, 170, 171, 172, 172, 172, 57, 
	233, 233, 171, 172, 171, 171, 172, 172, 
	172, 57, 233, 233, 170, 173, 172, 170, 
	171, 172, 172, 172, 57, 233, 233, 173, 
	174, 173, 174, 174, 174, 57, 233, 233, 
	175, 176, 178, 175, 177, 178, 178, 178, 
	57, 233, 233, 175, 176, 178, 175, 177, 
	178, 178, 178, 57, 233, 233, 176, 233, 
	233, 177, 178, 177, 177, 178, 178, 178, 
	57, 233, 233, 175, 176, 178, 175, 177, 
	178, 178, 178, 57, 233, 233, 180, 57, 
	233, 233, 181, 57, 233, 233, 182, 57, 
	233, 233, 183, 57, 233, 233, 184, 184, 
	57, 233, 233, 184, 185, 184, 185, 185, 
	185, 57, 233, 233, 186, 189, 188, 186, 
	187, 188, 188, 188, 57, 233, 233, 186, 
	189, 188, 186, 187, 188, 188, 188, 57, 
	233, 233, 187, 188, 187, 187, 188, 188, 
	188, 57, 233, 233, 186, 189, 188, 186, 
	187, 188, 188, 188, 57, 233, 233, 189, 
	190, 189, 190, 190, 190, 57, 233, 233, 
	191, 192, 194, 191, 193, 194, 194, 194, 
	57, 233, 233, 191, 192, 194, 191, 193, 
	194, 194, 194, 57, 233, 233, 192, 233, 
	233, 193, 194, 193, 193, 194, 194, 194, 
	57, 233, 233, 191, 192, 194, 191, 193, 
	194, 194, 194, 57, 233, 233, 196, 57, 
	233, 233, 197, 57, 233, 233, 198, 57, 
	233, 233, 199, 57, 233, 233, 200, 57, 
	233, 233, 201, 57, 233, 233, 202, 57, 
	233, 233, 203, 57, 233, 233, 204, 204, 
	57, 233, 233, 204, 205, 204, 205, 205, 
	205, 57, 233, 233, 206, 209, 208, 206, 
	207, 208, 208, 208, 57, 233, 233, 206, 
	209, 208, 206, 207, 208, 208, 208, 57, 
	233, 233, 207, 208, 207, 207, 208, 208, 
	208, 57, 233, 233, 206, 209, 208, 206, 
	207, 208, 208, 208, 57, 233, 233, 209, 
	210, 209, 210, 210, 210, 57, 233, 233, 
	211, 212, 214, 211, 213, 214, 214, 214, 
	57, 233, 233, 211, 212, 214, 211, 213, 
	214, 214, 214, 57, 233, 233, 212, 233, 
	233, 213, 214, 213, 213, 214, 214, 214, 
	57, 233, 233, 211, 212, 214, 211, 213, 
	214, 214, 214, 57, 233, 233, 216, 57, 
	233, 233, 217, 57, 233, 233, 218, 218, 
	57, 233, 233, 218, 219, 218, 57, 233, 
	233, 219, 220, 219, 220, 220, 220, 57, 
	233, 233, 221, 222, 230, 221, 229, 230, 
	230, 230, 57, 233, 233, 221, 222, 230, 
	221, 229, 230, 230, 230, 57, 233, 233, 
	223, 224, 223, 57, 233, 233, 223, 224, 
	225, 223, 225, 225, 225, 57, 233, 233, 
	224, 233, 233, 226, 224, 228, 226, 227, 
	228, 228, 228, 57, 233, 233, 226, 224, 
	228, 226, 227, 228, 228, 228, 57, 233, 
	233, 227, 228, 227, 227, 228, 228, 228, 
	57, 233, 233, 226, 224, 228, 226, 227, 
	228, 228, 228, 57, 233, 233, 229, 230, 
	229, 229, 230, 230, 230, 57, 233, 233, 
	221, 222, 230, 221, 229, 230, 230, 230, 
	57, 0, 233, 231, 232, 0, 234, 58, 
	231, 59, 104, 132, 147, 159, 215, 58, 
	57, 233, 234, 58, 59, 104, 132, 147, 
	159, 215, 58, 57, 0
};

static const unsigned char _unchecked_parse_test_trans_actions_wi[] = {
	1, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 39, 39, 39, 
	39, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 114, 0, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 79, 79, 79, 76, 79, 
	13, 76, 76, 76, 0, 0, 0, 0, 
	15, 0, 0, 15, 15, 15, 0, 118, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 55, 
	0, 0, 0, 0, 1, 0, 41, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	126, 0, 0, 0, 0, 0, 126, 0, 
	0, 55, 0, 0, 118, 0, 0, 0, 
	15, 0, 0, 15, 15, 15, 0, 17, 
	17, 17, 15, 17, 0, 15, 15, 15, 
	0, 0, 114, 0, 53, 64, 0, 53, 
	146, 0, 0, 0, 43, 0, 88, 35, 
	0, 0, 53, 64, 0, 0, 53, 64, 
	0, 0, 53, 64, 0, 0, 53, 64, 
	0, 0, 0, 53, 64, 0, 0, 0, 
	0, 53, 64, 21, 21, 5, 0, 53, 
	64, 0, 0, 0, 0, 53, 64, 0, 
	0, 0, 0, 53, 64, 0, 0, 0, 
	5, 0, 53, 64, 0, 0, 0, 0, 
	53, 64, 23, 23, 0, 53, 64, 0, 
	0, 0, 0, 53, 64, 0, 0, 0, 
	0, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 25, 0, 5, 0, 53, 64, 
	0, 25, 0, 0, 53, 64, 0, 0, 
	0, 0, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 27, 0, 5, 0, 53, 
	64, 0, 27, 0, 0, 53, 64, 0, 
	0, 0, 0, 0, 0, 53, 64, 0, 
	0, 53, 64, 0, 29, 0, 5, 0, 
	53, 64, 0, 29, 0, 0, 53, 94, 
	0, 0, 0, 0, 53, 94, 0, 0, 
	0, 0, 0, 0, 0, 0, 53, 94, 
	0, 53, 205, 138, 138, 76, 138, 13, 
	76, 76, 76, 0, 53, 94, 0, 0, 
	15, 0, 0, 15, 15, 15, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 199, 85, 85, 15, 85, 0, 
	15, 15, 15, 0, 53, 64, 0, 29, 
	0, 5, 0, 53, 64, 0, 0, 53, 
	64, 11, 73, 11, 5, 0, 53, 64, 
	11, 73, 11, 5, 0, 53, 64, 0, 
	27, 0, 5, 0, 53, 64, 0, 0, 
	53, 64, 11, 70, 11, 5, 0, 53, 
	64, 11, 70, 11, 5, 0, 53, 64, 
	0, 25, 0, 5, 0, 53, 64, 0, 
	0, 53, 64, 11, 67, 11, 5, 0, 
	53, 64, 11, 67, 11, 5, 0, 53, 
	64, 0, 0, 0, 5, 0, 53, 64, 
	21, 21, 5, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 33, 33, 33, 33, 0, 
	53, 64, 0, 0, 0, 53, 64, 0, 
	0, 0, 0, 53, 142, 31, 31, 31, 
	5, 0, 53, 58, 0, 0, 0, 0, 
	0, 53, 58, 0, 53, 142, 31, 31, 
	31, 5, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 0, 53, 64, 0, 0, 
	0, 0, 53, 64, 0, 0, 5, 0, 
	53, 64, 0, 0, 0, 0, 53, 98, 
	0, 0, 0, 9, 0, 53, 98, 0, 
	0, 0, 0, 53, 98, 0, 53, 98, 
	0, 0, 0, 9, 0, 53, 64, 0, 
	0, 5, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	170, 45, 45, 45, 45, 0, 53, 130, 
	0, 0, 0, 0, 0, 53, 130, 0, 
	53, 64, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 64, 0, 0, 0, 0, 
	0, 0, 0, 53, 64, 79, 79, 76, 
	79, 13, 76, 76, 76, 0, 53, 64, 
	0, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 130, 0, 0, 0, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 64, 17, 17, 15, 17, 0, 
	15, 15, 15, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	0, 0, 53, 64, 0, 0, 0, 0, 
	0, 0, 0, 53, 64, 79, 79, 76, 
	79, 13, 76, 76, 76, 0, 53, 64, 
	0, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 122, 0, 0, 0, 0, 53, 
	122, 0, 53, 64, 0, 15, 0, 0, 
	15, 15, 15, 0, 53, 64, 17, 17, 
	15, 17, 0, 15, 15, 15, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 53, 
	64, 0, 0, 53, 64, 0, 0, 0, 
	53, 64, 0, 0, 0, 0, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	0, 53, 64, 0, 0, 0, 0, 0, 
	0, 0, 53, 64, 79, 79, 76, 79, 
	13, 76, 76, 76, 0, 53, 64, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	53, 64, 0, 15, 0, 0, 15, 15, 
	15, 0, 53, 64, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 53, 64, 0, 
	0, 0, 0, 0, 0, 0, 53, 175, 
	82, 82, 76, 82, 13, 76, 76, 76, 
	0, 53, 102, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 53, 102, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 150, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	0, 53, 64, 0, 0, 0, 0, 0, 
	0, 0, 53, 64, 79, 79, 76, 79, 
	13, 76, 76, 76, 0, 53, 64, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	53, 64, 0, 15, 0, 0, 15, 15, 
	15, 0, 53, 64, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 53, 64, 0, 
	0, 0, 0, 0, 0, 0, 53, 187, 
	82, 82, 76, 82, 13, 76, 76, 76, 
	0, 53, 110, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 53, 110, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 160, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	0, 53, 64, 0, 0, 0, 0, 0, 
	0, 0, 53, 64, 79, 79, 76, 79, 
	13, 76, 76, 76, 0, 53, 64, 0, 
	0, 15, 0, 0, 15, 15, 15, 0, 
	53, 64, 0, 15, 0, 0, 15, 15, 
	15, 0, 53, 64, 17, 17, 15, 17, 
	0, 15, 15, 15, 0, 53, 64, 0, 
	0, 0, 0, 0, 0, 0, 53, 193, 
	82, 82, 76, 82, 13, 76, 76, 76, 
	0, 53, 134, 0, 0, 15, 0, 0, 
	15, 15, 15, 0, 53, 134, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 165, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 53, 64, 0, 0, 
	53, 64, 0, 0, 53, 64, 0, 0, 
	0, 53, 64, 0, 0, 0, 0, 53, 
	64, 0, 0, 0, 0, 0, 0, 0, 
	53, 64, 79, 79, 76, 79, 13, 76, 
	76, 76, 0, 53, 64, 0, 0, 15, 
	0, 0, 15, 15, 15, 0, 53, 106, 
	0, 0, 0, 0, 53, 106, 0, 0, 
	0, 0, 0, 0, 0, 0, 53, 106, 
	0, 53, 181, 82, 82, 76, 82, 13, 
	76, 76, 76, 0, 53, 106, 0, 0, 
	15, 0, 0, 15, 15, 15, 0, 53, 
	64, 0, 15, 0, 0, 15, 15, 15, 
	0, 53, 155, 19, 19, 15, 19, 0, 
	15, 15, 15, 0, 53, 64, 0, 15, 
	0, 0, 15, 15, 15, 0, 53, 64, 
	17, 17, 15, 17, 0, 15, 15, 15, 
	0, 0, 61, 0, 0, 0, 146, 0, 
	0, 0, 0, 43, 0, 88, 35, 0, 
	0, 51, 146, 0, 0, 0, 43, 0, 
	88, 35, 0, 0, 0
};

static const unsigned char _unchecked_parse_test_to_state_actions[] = {
	0, 47, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 47, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 47, 0, 0, 
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
	0, 37, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	47, 91, 0
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
	0, 49, 0
};

static const short _unchecked_parse_test_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 74, 
	74, 74, 74, 74, 74, 74, 74, 0, 
	0, 0, 356
};

static const int unchecked_parse_test_start = 1;
static const int unchecked_parse_test_first_final = 232;
static const int unchecked_parse_test_error = 0;

static const int unchecked_parse_test_en_group_scanner = 233;
static const int unchecked_parse_test_en_main = 1;

#line 927 "NanorexMMPImportExportTest.rl"
	
#line 5715 "NanorexMMPImportExportTest.cpp"
	{
	cs = unchecked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 928 "NanorexMMPImportExportTest.rl"
	
#line 5725 "NanorexMMPImportExportTest.cpp"
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
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 5746 "NanorexMMPImportExportTest.cpp"
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
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal/*, stringVal2*/); }
	break;
	case 29:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
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
#line 902 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 233; goto _again;} }
	break;
	case 38:
#line 905 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 233; goto _again;} }
	break;
	case 39:
#line 910 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 233; goto _again;} }
	break;
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 44:
#line 102 "NanorexMMPImportExportTest.rl"
	{act = 11;}
	break;
	case 45:
#line 89 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 46:
#line 90 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 47:
#line 91 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 48:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
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
#line 100 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 56:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 57:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 11:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 6055 "NanorexMMPImportExportTest.cpp"
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
	case 40:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 41:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 6084 "NanorexMMPImportExportTest.cpp"
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
#line 929 "NanorexMMPImportExportTest.rl"
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


#line 990 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::checkedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 1003 "NanorexMMPImportExportTest.rl"
	
#line 6160 "NanorexMMPImportExportTest.cpp"
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
	52, 1, 54, 1, 55, 1, 57, 1, 
	58, 1, 59, 1, 61, 1, 62, 1, 
	68, 1, 69, 1, 82, 1, 83, 2, 
	0, 53, 2, 0, 78, 2, 0, 80, 
	2, 0, 81, 2, 5, 12, 2, 5, 
	13, 2, 5, 14, 2, 6, 7, 2, 
	6, 8, 2, 6, 9, 2, 8, 21, 
	2, 8, 41, 2, 9, 42, 2, 18, 
	83, 2, 19, 83, 2, 20, 83, 2, 
	22, 83, 2, 26, 83, 2, 27, 83, 
	2, 28, 29, 2, 30, 83, 2, 31, 
	83, 2, 33, 34, 2, 33, 83, 2, 
	34, 35, 2, 35, 83, 2, 36, 83, 
	2, 37, 83, 2, 41, 44, 2, 41, 
	83, 2, 42, 83, 2, 44, 42, 2, 
	44, 83, 2, 49, 83, 2, 61, 83, 
	2, 62, 83, 2, 70, 0, 3, 0, 
	16, 79, 3, 0, 17, 77, 3, 0, 
	24, 76, 3, 0, 40, 74, 3, 0, 
	45, 75, 3, 0, 47, 65, 3, 0, 
	51, 66, 3, 0, 51, 71, 3, 0, 
	56, 67, 3, 0, 60, 73, 3, 0, 
	64, 72, 3, 6, 8, 21, 3, 6, 
	8, 41, 3, 6, 9, 42, 3, 15, 
	0, 78, 3, 18, 0, 81, 3, 19, 
	0, 81, 3, 20, 0, 81, 3, 22, 
	0, 81, 3, 26, 0, 81, 3, 27, 
	0, 78, 3, 27, 0, 81, 3, 30, 
	0, 81, 3, 31, 0, 81, 3, 33, 
	0, 81, 3, 33, 34, 83, 3, 34, 
	35, 83, 3, 35, 0, 81, 3, 36, 
	0, 81, 3, 37, 0, 81, 3, 41, 
	0, 81, 3, 41, 44, 83, 3, 42, 
	0, 81, 3, 44, 42, 83, 3, 49, 
	0, 81, 3, 61, 0, 81, 3, 62, 
	0, 81, 3, 63, 43, 32, 4, 9, 
	0, 17, 77, 4, 9, 0, 40, 74, 
	4, 9, 0, 64, 72, 4, 22, 0, 
	24, 76, 4, 33, 34, 0, 81, 4, 
	34, 35, 0, 81, 4, 37, 0, 40, 
	74, 4, 41, 44, 0, 81, 4, 42, 
	0, 45, 75, 4, 44, 42, 0, 81, 
	4, 59, 0, 60, 73, 4, 62, 0, 
	64, 72, 5, 6, 9, 0, 17, 77, 
	5, 6, 9, 0, 40, 74, 5, 6, 
	9, 0, 64, 72, 5, 8, 21, 0, 
	24, 76, 5, 9, 42, 0, 45, 75, 
	6, 6, 8, 21, 0, 24, 76, 6, 
	6, 9, 42, 0, 45, 75
};

static const short _checked_parse_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 14, 
	19, 20, 21, 22, 26, 31, 32, 33, 
	34, 39, 41, 46, 47, 48, 49, 50, 
	55, 66, 80, 94, 99, 104, 105, 106, 
	107, 112, 117, 118, 119, 120, 121, 122, 
	127, 132, 133, 134, 135, 136, 137, 138, 
	139, 140, 145, 147, 149, 151, 153, 166, 
	180, 182, 184, 196, 207, 209, 210, 211, 
	212, 216, 222, 228, 233, 239, 246, 251, 
	255, 260, 268, 270, 277, 282, 290, 292, 
	299, 304, 312, 314, 321, 326, 331, 343, 
	345, 359, 373, 386, 400, 407, 409, 416, 
	423, 430, 432, 439, 446, 453, 455, 462, 
	469, 476, 482, 483, 484, 485, 491, 495, 
	501, 508, 515, 517, 524, 525, 526, 527, 
	528, 529, 530, 531, 532, 533, 537, 543, 
	549, 555, 562, 567, 569, 576, 582, 583, 
	584, 585, 586, 587, 593, 599, 601, 613, 
	624, 638, 652, 657, 670, 684, 685, 686, 
	687, 688, 693, 704, 718, 732, 737, 739, 
	752, 766, 767, 768, 769, 773, 780, 781, 
	782, 783, 787, 798, 812, 826, 839, 853, 
	864, 875, 889, 903, 905, 918, 932, 933, 
	934, 935, 936, 940, 951, 965, 979, 992, 
	1006, 1017, 1028, 1042, 1056, 1058, 1071, 1085, 
	1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 
	1097, 1108, 1122, 1136, 1149, 1163, 1174, 1188, 
	1202, 1204, 1217, 1231, 1232, 1233, 1237, 1242, 
	1253, 1267, 1281, 1286, 1298, 1300, 1314, 1328, 
	1341, 1355, 1368, 1382, 1384, 1387, 1390, 1393, 
	1398, 1405, 1412, 1418, 1425, 1433, 1439, 1444, 
	1450, 1459, 1463, 1471, 1477, 1486, 1490, 1498, 
	1504, 1513, 1517, 1525, 1531, 1537, 1550, 1552, 
	1567, 1582, 1596, 1611, 1619, 1623, 1631, 1639, 
	1647, 1651, 1659, 1667, 1675, 1679, 1687, 1695, 
	1703, 1710, 1713, 1716, 1719, 1727, 1732, 1739, 
	1747, 1755, 1757, 1765, 1768, 1771, 1774, 1777, 
	1780, 1783, 1786, 1789, 1792, 1797, 1804, 1811, 
	1818, 1826, 1832, 1834, 1842, 1849, 1852, 1855, 
	1858, 1861, 1864, 1871, 1878, 1880, 1893, 1905, 
	1920, 1935, 1941, 1955, 1970, 1973, 1976, 1979, 
	1982, 1988, 2000, 2015, 2030, 2036, 2038, 2052, 
	2067, 2070, 2073, 2076, 2081, 2089, 2092, 2095, 
	2098, 2103, 2115, 2130, 2145, 2159, 2174, 2186, 
	2198, 2213, 2228, 2230, 2244, 2259, 2262, 2265, 
	2268, 2271, 2276, 2288, 2303, 2318, 2332, 2347, 
	2359, 2371, 2386, 2401, 2403, 2417, 2432, 2435, 
	2438, 2441, 2444, 2447, 2450, 2453, 2456, 2461, 
	2473, 2488, 2503, 2517, 2532, 2544, 2559, 2574, 
	2576, 2590, 2605, 2608, 2611, 2616, 2622, 2634, 
	2649, 2664, 2670, 2683, 2685, 2700, 2715, 2729, 
	2744, 2758, 2773, 2773, 2785
};

static const char _checked_parse_test_trans_keys[] = {
	10, 32, 103, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	86, 11, 13, 105, 101, 119, 9, 32, 
	11, 13, 9, 32, 68, 11, 13, 97, 
	116, 97, 9, 32, 41, 11, 13, 10, 
	35, 10, 32, 103, 9, 13, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 41, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 9, 13, 10, 32, 101, 9, 13, 
	110, 100, 49, 10, 32, 35, 9, 13, 
	10, 32, 101, 9, 13, 103, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 67, 11, 13, 108, 105, 112, 98, 
	111, 97, 114, 100, 9, 32, 41, 11, 
	13, 10, 35, -1, 10, -1, 10, -1, 
	10, 9, 32, 95, 11, 13, 45, 46, 
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
	9, 32, 40, 11, 13, 9, 32, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 95, 11, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	41, 95, 11, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 9, 
	13, -1, 10, 9, 32, 95, 11, 13, 
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
	32, 40, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, -1, 10, 
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
	97, 122, -1, 10, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 104, -1, 10, 
	117, -1, 10, 110, -1, 10, 107, -1, 
	10, 32, 9, 13, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 61, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 61, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
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
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 97, 98, 101, 103, 105, 109, 9, 
	13, 10, 32, 35, 97, 98, 101, 103, 
	105, 109, 9, 13, 0
};

static const char _checked_parse_test_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 3, 3, 
	1, 1, 1, 2, 3, 1, 1, 1, 
	3, 2, 3, 1, 1, 1, 1, 3, 
	3, 4, 4, 3, 3, 1, 1, 1, 
	3, 3, 1, 1, 1, 1, 1, 3, 
	3, 1, 1, 1, 1, 1, 1, 1, 
	1, 3, 2, 2, 2, 2, 3, 4, 
	2, 2, 10, 9, 2, 1, 1, 1, 
	2, 2, 2, 3, 2, 3, 3, 2, 
	3, 4, 0, 3, 3, 4, 0, 3, 
	3, 4, 0, 3, 3, 3, 4, 2, 
	4, 4, 3, 4, 3, 0, 3, 3, 
	3, 0, 3, 3, 3, 0, 3, 3, 
	3, 2, 1, 1, 1, 4, 2, 2, 
	3, 3, 2, 3, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 2, 2, 2, 
	2, 3, 3, 2, 3, 2, 1, 1, 
	1, 1, 1, 4, 4, 2, 4, 3, 
	4, 4, 3, 3, 4, 1, 1, 1, 
	1, 3, 3, 4, 4, 3, 2, 3, 
	4, 1, 1, 1, 2, 5, 1, 1, 
	1, 2, 3, 4, 4, 3, 4, 3, 
	3, 4, 4, 2, 3, 4, 1, 1, 
	1, 1, 2, 3, 4, 4, 3, 4, 
	3, 3, 4, 4, 2, 3, 4, 1, 
	1, 1, 1, 1, 1, 1, 1, 2, 
	3, 4, 4, 3, 4, 3, 4, 4, 
	2, 3, 4, 1, 1, 2, 3, 3, 
	4, 4, 3, 4, 2, 4, 4, 3, 
	4, 3, 4, 2, 3, 3, 3, 3, 
	3, 3, 4, 3, 4, 4, 3, 4, 
	5, 2, 4, 4, 5, 2, 4, 4, 
	5, 2, 4, 4, 4, 5, 2, 5, 
	5, 4, 5, 4, 2, 4, 4, 4, 
	2, 4, 4, 4, 2, 4, 4, 4, 
	3, 3, 3, 3, 6, 3, 3, 4, 
	4, 2, 4, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	4, 4, 2, 4, 3, 3, 3, 3, 
	3, 3, 5, 5, 2, 5, 4, 5, 
	5, 4, 4, 5, 3, 3, 3, 3, 
	4, 4, 5, 5, 4, 2, 4, 5, 
	3, 3, 3, 3, 6, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 4, 
	5, 5, 2, 4, 5, 3, 3, 3, 
	3, 3, 4, 5, 5, 4, 5, 4, 
	4, 5, 5, 2, 4, 5, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 4, 
	5, 5, 4, 5, 4, 5, 5, 2, 
	4, 5, 3, 3, 3, 4, 4, 5, 
	5, 4, 5, 2, 5, 5, 4, 5, 
	4, 5, 0, 10, 9
};

static const char _checked_parse_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	1, 0, 1, 0, 0, 0, 0, 1, 
	4, 5, 5, 1, 1, 0, 0, 0, 
	1, 1, 0, 0, 0, 0, 0, 1, 
	1, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 0, 0, 0, 0, 5, 5, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 2, 2, 1, 2, 2, 1, 1, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 1, 4, 0, 
	5, 5, 5, 5, 2, 1, 2, 2, 
	2, 1, 2, 2, 2, 1, 2, 2, 
	2, 2, 0, 0, 0, 1, 1, 2, 
	2, 2, 0, 2, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 2, 2, 
	2, 2, 1, 0, 2, 2, 0, 0, 
	0, 0, 0, 1, 1, 0, 4, 4, 
	5, 5, 1, 5, 5, 0, 0, 0, 
	0, 1, 4, 5, 5, 1, 0, 5, 
	5, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 4, 5, 5, 5, 5, 4, 
	4, 5, 5, 0, 5, 5, 0, 0, 
	0, 0, 1, 4, 5, 5, 5, 5, 
	4, 4, 5, 5, 0, 5, 5, 0, 
	0, 0, 0, 0, 0, 0, 0, 1, 
	4, 5, 5, 5, 5, 4, 5, 5, 
	0, 5, 5, 0, 0, 1, 1, 4, 
	5, 5, 1, 4, 0, 5, 5, 5, 
	5, 5, 5, 0, 0, 0, 0, 1, 
	2, 2, 1, 2, 2, 1, 1, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 1, 4, 0, 5, 
	5, 5, 5, 2, 1, 2, 2, 2, 
	1, 2, 2, 2, 1, 2, 2, 2, 
	2, 0, 0, 0, 1, 1, 2, 2, 
	2, 0, 2, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 2, 2, 2, 
	2, 1, 0, 2, 2, 0, 0, 0, 
	0, 0, 1, 1, 0, 4, 4, 5, 
	5, 1, 5, 5, 0, 0, 0, 0, 
	1, 4, 5, 5, 1, 0, 5, 5, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 4, 
	5, 5, 0, 5, 5, 0, 0, 0, 
	0, 1, 4, 5, 5, 5, 5, 4, 
	4, 5, 5, 0, 5, 5, 0, 0, 
	0, 0, 0, 0, 0, 0, 1, 4, 
	5, 5, 5, 5, 4, 5, 5, 0, 
	5, 5, 0, 0, 1, 1, 4, 5, 
	5, 1, 4, 0, 5, 5, 5, 5, 
	5, 5, 0, 1, 1
};

static const short _checked_parse_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 18, 
	23, 25, 27, 29, 33, 38, 40, 42, 
	44, 49, 52, 57, 59, 61, 63, 65, 
	70, 78, 88, 98, 103, 108, 110, 112, 
	114, 119, 124, 126, 128, 130, 132, 134, 
	139, 144, 146, 148, 150, 152, 154, 156, 
	158, 160, 165, 168, 171, 174, 177, 186, 
	196, 199, 202, 214, 225, 228, 230, 232, 
	234, 238, 243, 248, 253, 258, 264, 269, 
	273, 278, 285, 287, 293, 298, 305, 307, 
	313, 318, 325, 327, 333, 338, 343, 352, 
	355, 365, 375, 384, 394, 400, 402, 408, 
	414, 420, 422, 428, 434, 440, 442, 448, 
	454, 460, 465, 467, 469, 471, 477, 481, 
	486, 492, 498, 501, 507, 509, 511, 513, 
	515, 517, 519, 521, 523, 525, 529, 534, 
	539, 544, 550, 555, 558, 564, 569, 571, 
	573, 575, 577, 579, 585, 591, 594, 603, 
	611, 621, 631, 636, 645, 655, 657, 659, 
	661, 663, 668, 676, 686, 696, 701, 704, 
	713, 723, 725, 727, 729, 733, 740, 742, 
	744, 746, 750, 758, 768, 778, 787, 797, 
	805, 813, 823, 833, 836, 845, 855, 857, 
	859, 861, 863, 867, 875, 885, 895, 904, 
	914, 922, 930, 940, 950, 953, 962, 972, 
	974, 976, 978, 980, 982, 984, 986, 988, 
	992, 1000, 1010, 1020, 1029, 1039, 1047, 1057, 
	1067, 1070, 1079, 1089, 1091, 1093, 1097, 1102, 
	1110, 1120, 1130, 1135, 1144, 1147, 1157, 1167, 
	1176, 1186, 1195, 1205, 1208, 1212, 1216, 1220, 
	1225, 1231, 1237, 1243, 1249, 1256, 1262, 1267, 
	1273, 1281, 1285, 1292, 1298, 1306, 1310, 1317, 
	1323, 1331, 1335, 1342, 1348, 1354, 1364, 1367, 
	1378, 1389, 1399, 1410, 1417, 1421, 1428, 1435, 
	1442, 1446, 1453, 1460, 1467, 1471, 1478, 1485, 
	1492, 1498, 1502, 1506, 1510, 1518, 1523, 1529, 
	1536, 1543, 1546, 1553, 1557, 1561, 1565, 1569, 
	1573, 1577, 1581, 1585, 1589, 1594, 1600, 1606, 
	1612, 1619, 1625, 1628, 1635, 1641, 1645, 1649, 
	1653, 1657, 1661, 1668, 1675, 1678, 1688, 1697, 
	1708, 1719, 1725, 1735, 1746, 1750, 1754, 1758, 
	1762, 1768, 1777, 1788, 1799, 1805, 1808, 1818, 
	1829, 1833, 1837, 1841, 1846, 1854, 1858, 1862, 
	1866, 1871, 1880, 1891, 1902, 1912, 1923, 1932, 
	1941, 1952, 1963, 1966, 1976, 1987, 1991, 1995, 
	1999, 2003, 2008, 2017, 2028, 2039, 2049, 2060, 
	2069, 2078, 2089, 2100, 2103, 2113, 2124, 2128, 
	2132, 2136, 2140, 2144, 2148, 2152, 2156, 2161, 
	2170, 2181, 2192, 2202, 2213, 2222, 2233, 2244, 
	2247, 2257, 2268, 2272, 2276, 2281, 2287, 2296, 
	2307, 2318, 2324, 2334, 2337, 2348, 2359, 2369, 
	2380, 2390, 2401, 2402, 2414
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
	1, 28, 28, 29, 28, 1, 31, 31, 
	32, 31, 32, 32, 32, 30, 33, 33, 
	34, 36, 33, 35, 36, 36, 36, 1, 
	37, 37, 38, 40, 37, 39, 40, 40, 
	40, 30, 42, 41, 43, 41, 1, 45, 
	44, 46, 44, 1, 47, 1, 48, 1, 
	49, 1, 51, 49, 52, 49, 50, 54, 
	53, 55, 53, 1, 56, 1, 57, 1, 
	58, 1, 59, 1, 60, 1, 60, 60, 
	61, 60, 1, 61, 61, 62, 61, 1, 
	63, 1, 64, 1, 65, 1, 66, 1, 
	67, 1, 68, 1, 69, 1, 70, 1, 
	70, 70, 71, 70, 1, 73, 74, 72, 
	72, 73, 74, 50, 51, 52, 1, 42, 
	43, 39, 39, 40, 39, 39, 40, 40, 
	40, 30, 75, 75, 76, 40, 75, 39, 
	40, 40, 40, 1, 19, 20, 21, 1, 
	78, 77, 1, 80, 79, 81, 82, 83, 
	84, 85, 86, 87, 79, 77, 90, 89, 
	91, 92, 93, 94, 95, 96, 97, 89, 
	88, 88, 98, 91, 99, 88, 100, 88, 
	101, 88, 102, 102, 102, 88, 104, 104, 
	104, 105, 103, 106, 106, 106, 107, 88, 
	109, 109, 110, 109, 108, 110, 110, 110, 
	111, 108, 112, 112, 113, 112, 114, 108, 
	112, 112, 113, 112, 108, 115, 115, 115, 
	88, 116, 116, 117, 116, 88, 117, 117, 
	118, 119, 117, 120, 88, 120, 88, 121, 
	121, 122, 121, 123, 88, 121, 121, 122, 
	121, 88, 124, 124, 125, 126, 124, 127, 
	88, 127, 88, 128, 128, 129, 128, 130, 
	88, 128, 128, 129, 128, 88, 131, 131, 
	132, 133, 131, 134, 88, 134, 88, 136, 
	136, 137, 136, 138, 135, 136, 136, 137, 
	136, 135, 140, 139, 141, 139, 88, 144, 
	143, 145, 146, 143, 146, 146, 146, 142, 
	88, 140, 141, 148, 147, 149, 151, 147, 
	150, 151, 151, 151, 88, 144, 152, 145, 
	154, 152, 153, 154, 154, 154, 142, 153, 
	153, 154, 153, 153, 154, 154, 154, 142, 
	156, 155, 157, 154, 155, 153, 154, 154, 
	154, 88, 136, 136, 137, 136, 138, 135, 
	158, 88, 159, 159, 160, 159, 161, 135, 
	159, 159, 160, 159, 161, 135, 128, 128, 
	129, 128, 130, 88, 162, 88, 163, 163, 
	164, 163, 165, 88, 163, 163, 164, 163, 
	165, 88, 121, 121, 122, 121, 123, 88, 
	166, 88, 167, 167, 168, 167, 169, 88, 
	167, 167, 168, 167, 169, 88, 112, 112, 
	113, 112, 114, 108, 106, 106, 106, 107, 
	88, 170, 88, 171, 88, 172, 88, 175, 
	174, 174, 174, 174, 173, 176, 176, 176, 
	88, 178, 178, 178, 179, 177, 181, 180, 
	182, 180, 183, 88, 185, 184, 186, 184, 
	179, 177, 88, 188, 187, 181, 180, 182, 
	180, 183, 88, 189, 88, 190, 88, 191, 
	88, 192, 88, 193, 88, 194, 88, 195, 
	88, 196, 88, 197, 88, 198, 198, 198, 
	88, 198, 198, 198, 200, 199, 201, 201, 
	201, 202, 199, 201, 201, 201, 204, 203, 
	206, 205, 207, 205, 208, 203, 206, 205, 
	207, 205, 88, 88, 206, 207, 206, 205, 
	207, 205, 208, 203, 201, 201, 201, 202, 
	199, 209, 88, 210, 88, 211, 88, 212, 
	88, 213, 88, 215, 214, 216, 217, 214, 
	88, 219, 218, 220, 221, 218, 88, 88, 
	219, 220, 223, 223, 224, 225, 223, 225, 
	225, 225, 222, 223, 223, 225, 223, 225, 
	225, 225, 222, 226, 226, 227, 229, 226, 
	228, 229, 229, 229, 88, 230, 230, 224, 
	232, 230, 231, 232, 232, 232, 222, 219, 
	233, 220, 233, 88, 231, 231, 232, 231, 
	231, 232, 232, 232, 222, 234, 234, 235, 
	232, 234, 231, 232, 232, 232, 88, 236, 
	88, 237, 88, 238, 88, 239, 88, 239, 
	239, 240, 239, 88, 241, 241, 242, 241, 
	242, 242, 242, 222, 243, 243, 244, 246, 
	243, 245, 246, 246, 246, 88, 247, 247, 
	248, 250, 247, 249, 250, 250, 250, 222, 
	252, 251, 253, 251, 88, 88, 252, 253, 
	249, 249, 250, 249, 249, 250, 250, 250, 
	222, 254, 254, 255, 250, 254, 249, 250, 
	250, 250, 88, 256, 88, 257, 88, 258, 
	88, 259, 259, 259, 88, 259, 259, 260, 
	261, 262, 259, 88, 263, 88, 264, 88, 
	265, 88, 266, 266, 266, 88, 266, 266, 
	268, 266, 268, 268, 268, 267, 270, 270, 
	273, 272, 270, 271, 272, 272, 272, 269, 
	274, 274, 277, 276, 274, 275, 276, 276, 
	276, 269, 275, 275, 276, 275, 275, 276, 
	276, 276, 267, 278, 278, 279, 276, 278, 
	275, 276, 276, 276, 269, 281, 281, 282, 
	281, 282, 282, 282, 280, 281, 281, 282, 
	281, 282, 282, 282, 283, 285, 284, 286, 
	288, 284, 287, 288, 288, 288, 283, 290, 
	289, 291, 293, 289, 292, 293, 293, 293, 
	283, 88, 290, 291, 292, 292, 293, 292, 
	292, 293, 293, 293, 283, 295, 294, 296, 
	293, 294, 292, 293, 293, 293, 283, 297, 
	88, 298, 88, 299, 88, 300, 88, 301, 
	301, 301, 88, 303, 303, 304, 303, 304, 
	304, 304, 302, 307, 307, 310, 309, 307, 
	308, 309, 309, 309, 306, 311, 311, 314, 
	313, 311, 312, 313, 313, 313, 306, 312, 
	312, 313, 312, 312, 313, 313, 313, 302, 
	315, 315, 316, 313, 315, 312, 313, 313, 
	313, 306, 318, 318, 319, 318, 319, 319, 
	319, 317, 318, 318, 319, 318, 319, 319, 
	319, 320, 322, 321, 323, 325, 321, 324, 
	325, 325, 325, 320, 327, 326, 328, 330, 
	326, 329, 330, 330, 330, 320, 88, 332, 
	331, 329, 329, 330, 329, 329, 330, 330, 
	330, 320, 334, 333, 335, 330, 333, 329, 
	330, 330, 330, 320, 336, 88, 337, 88, 
	338, 88, 339, 88, 340, 88, 341, 88, 
	342, 88, 343, 88, 344, 344, 344, 88, 
	346, 346, 347, 346, 347, 347, 347, 345, 
	348, 348, 351, 350, 348, 349, 350, 350, 
	350, 88, 352, 352, 355, 354, 352, 353, 
	354, 354, 354, 345, 353, 353, 354, 353, 
	353, 354, 354, 354, 345, 356, 356, 357, 
	354, 356, 353, 354, 354, 354, 88, 359, 
	359, 360, 359, 360, 360, 360, 358, 362, 
	361, 363, 365, 361, 364, 365, 365, 365, 
	88, 367, 366, 368, 370, 366, 369, 370, 
	370, 370, 358, 88, 372, 371, 369, 369, 
	370, 369, 369, 370, 370, 370, 358, 374, 
	373, 375, 370, 373, 369, 370, 370, 370, 
	88, 376, 88, 377, 88, 378, 378, 378, 
	88, 379, 379, 380, 379, 88, 380, 380, 
	381, 380, 381, 381, 381, 88, 383, 383, 
	384, 386, 383, 385, 386, 386, 386, 382, 
	387, 387, 388, 390, 387, 389, 390, 390, 
	390, 382, 392, 391, 393, 391, 88, 396, 
	395, 397, 398, 395, 398, 398, 398, 394, 
	88, 392, 393, 400, 399, 401, 403, 399, 
	402, 403, 403, 403, 88, 396, 404, 397, 
	406, 404, 405, 406, 406, 406, 394, 405, 
	405, 406, 405, 405, 406, 406, 406, 394, 
	408, 407, 409, 406, 407, 405, 406, 406, 
	406, 88, 389, 389, 390, 389, 389, 390, 
	390, 390, 88, 410, 410, 411, 390, 410, 
	389, 390, 390, 390, 382, 1, 98, 81, 
	1, 78, 412, 77, 1, 78, 413, 77, 
	1, 78, 414, 77, 1, 78, 415, 415, 
	77, 417, 419, 418, 418, 420, 416, 1, 
	78, 421, 421, 422, 77, 424, 426, 425, 
	427, 425, 423, 424, 426, 427, 427, 428, 
	423, 424, 426, 429, 430, 429, 431, 423, 
	424, 426, 429, 430, 429, 423, 1, 78, 
	432, 432, 77, 1, 78, 433, 434, 433, 
	77, 1, 78, 434, 435, 436, 434, 437, 
	77, 1, 78, 437, 77, 1, 78, 438, 
	439, 438, 440, 77, 1, 78, 438, 439, 
	438, 77, 1, 78, 441, 442, 443, 441, 
	444, 77, 1, 78, 444, 77, 1, 78, 
	445, 446, 445, 447, 77, 1, 78, 445, 
	446, 445, 77, 1, 78, 448, 449, 450, 
	448, 451, 77, 1, 78, 451, 77, 453, 
	455, 454, 456, 454, 457, 452, 453, 455, 
	454, 456, 454, 452, 1, 140, 458, 459, 
	458, 77, 461, 144, 462, 463, 464, 462, 
	464, 464, 464, 460, 1, 140, 459, 1, 
	148, 465, 466, 468, 465, 467, 468, 468, 
	468, 77, 461, 144, 469, 463, 471, 469, 
	470, 471, 471, 471, 460, 461, 472, 470, 
	471, 470, 470, 471, 471, 471, 460, 1, 
	156, 473, 474, 471, 473, 470, 471, 471, 
	471, 77, 453, 455, 454, 456, 454, 457, 
	452, 1, 78, 475, 77, 453, 455, 476, 
	477, 476, 478, 452, 453, 455, 476, 477, 
	476, 478, 452, 1, 78, 445, 446, 445, 
	447, 77, 1, 78, 479, 77, 1, 78, 
	480, 481, 480, 482, 77, 1, 78, 480, 
	481, 480, 482, 77, 1, 78, 438, 439, 
	438, 440, 77, 1, 78, 483, 77, 1, 
	78, 484, 485, 484, 486, 77, 1, 78, 
	484, 485, 484, 486, 77, 424, 426, 429, 
	430, 429, 431, 423, 1, 78, 421, 421, 
	422, 77, 1, 78, 487, 77, 1, 78, 
	488, 77, 1, 78, 489, 77, 491, 492, 
	494, 493, 493, 493, 493, 490, 1, 78, 
	495, 495, 77, 497, 499, 498, 498, 500, 
	496, 1, 181, 501, 502, 501, 503, 77, 
	497, 185, 504, 505, 504, 500, 496, 1, 
	188, 506, 1, 181, 501, 502, 501, 503, 
	77, 1, 78, 507, 77, 1, 78, 508, 
	77, 1, 78, 509, 77, 1, 78, 510, 
	77, 1, 78, 511, 77, 1, 78, 512, 
	77, 1, 78, 513, 77, 1, 78, 514, 
	77, 1, 78, 515, 77, 1, 78, 516, 
	516, 77, 518, 519, 516, 516, 520, 517, 
	518, 519, 521, 521, 522, 517, 524, 525, 
	521, 521, 526, 523, 524, 206, 527, 528, 
	527, 529, 523, 1, 206, 527, 528, 527, 
	77, 1, 206, 528, 524, 206, 527, 528, 
	527, 529, 523, 518, 519, 521, 521, 522, 
	517, 1, 78, 530, 77, 1, 78, 531, 
	77, 1, 78, 532, 77, 1, 78, 533, 
	77, 1, 78, 534, 77, 1, 215, 535, 
	536, 537, 535, 77, 1, 219, 538, 539, 
	540, 538, 77, 1, 219, 539, 30, 543, 
	542, 544, 545, 542, 545, 545, 545, 541, 
	30, 543, 542, 545, 542, 545, 545, 545, 
	541, 1, 78, 546, 547, 549, 546, 548, 
	549, 549, 549, 77, 30, 543, 550, 544, 
	552, 550, 551, 552, 552, 552, 541, 1, 
	219, 553, 539, 553, 77, 30, 543, 551, 
	552, 551, 551, 552, 552, 552, 541, 1, 
	78, 554, 555, 552, 554, 551, 552, 552, 
	552, 77, 1, 78, 556, 77, 1, 78, 
	557, 77, 1, 78, 558, 77, 1, 78, 
	559, 77, 1, 78, 559, 560, 559, 77, 
	30, 543, 561, 562, 561, 562, 562, 562, 
	541, 1, 78, 563, 564, 566, 563, 565, 
	566, 566, 566, 77, 30, 543, 567, 568, 
	570, 567, 569, 570, 570, 570, 541, 1, 
	252, 571, 572, 571, 77, 1, 252, 572, 
	30, 543, 569, 570, 569, 569, 570, 570, 
	570, 541, 1, 78, 573, 574, 570, 573, 
	569, 570, 570, 570, 77, 1, 78, 575, 
	77, 1, 78, 576, 77, 1, 78, 577, 
	77, 1, 78, 578, 578, 77, 1, 78, 
	578, 579, 580, 581, 578, 77, 1, 78, 
	582, 77, 1, 78, 583, 77, 1, 78, 
	584, 77, 1, 78, 585, 585, 77, 587, 
	588, 585, 589, 585, 589, 589, 589, 586, 
	591, 593, 592, 596, 595, 592, 594, 595, 
	595, 595, 590, 591, 593, 597, 600, 599, 
	597, 598, 599, 599, 599, 590, 587, 588, 
	598, 599, 598, 598, 599, 599, 599, 586, 
	591, 593, 601, 602, 599, 601, 598, 599, 
	599, 599, 590, 604, 606, 605, 607, 605, 
	607, 607, 607, 603, 609, 610, 605, 607, 
	605, 607, 607, 607, 608, 609, 285, 611, 
	612, 614, 611, 613, 614, 614, 614, 608, 
	609, 290, 615, 616, 618, 615, 617, 618, 
	618, 618, 608, 1, 290, 616, 609, 610, 
	617, 618, 617, 617, 618, 618, 618, 608, 
	609, 295, 619, 620, 618, 619, 617, 618, 
	618, 618, 608, 1, 78, 621, 77, 1, 
	78, 622, 77, 1, 78, 623, 77, 1, 
	78, 624, 77, 1, 78, 625, 625, 77, 
	627, 629, 628, 630, 628, 630, 630, 630, 
	626, 632, 634, 633, 637, 636, 633, 635, 
	636, 636, 636, 631, 632, 634, 638, 641, 
	640, 638, 639, 640, 640, 640, 631, 627, 
	629, 639, 640, 639, 639, 640, 640, 640, 
	626, 632, 634, 642, 643, 640, 642, 639, 
	640, 640, 640, 631, 645, 647, 646, 648, 
	646, 648, 648, 648, 644, 650, 651, 646, 
	648, 646, 648, 648, 648, 649, 650, 322, 
	652, 653, 655, 652, 654, 655, 655, 655, 
	649, 650, 327, 656, 657, 659, 656, 658, 
	659, 659, 659, 649, 1, 332, 660, 650, 
	651, 658, 659, 658, 658, 659, 659, 659, 
	649, 650, 334, 661, 662, 659, 661, 658, 
	659, 659, 659, 649, 1, 78, 663, 77, 
	1, 78, 664, 77, 1, 78, 665, 77, 
	1, 78, 666, 77, 1, 78, 667, 77, 
	1, 78, 668, 77, 1, 78, 669, 77, 
	1, 78, 670, 77, 1, 78, 671, 671, 
	77, 673, 675, 674, 676, 674, 676, 676, 
	676, 672, 1, 78, 677, 680, 679, 677, 
	678, 679, 679, 679, 77, 673, 675, 681, 
	684, 683, 681, 682, 683, 683, 683, 672, 
	673, 675, 682, 683, 682, 682, 683, 683, 
	683, 672, 1, 78, 685, 686, 683, 685, 
	682, 683, 683, 683, 77, 688, 690, 689, 
	691, 689, 691, 691, 691, 687, 1, 362, 
	692, 693, 695, 692, 694, 695, 695, 695, 
	77, 688, 367, 696, 697, 699, 696, 698, 
	699, 699, 699, 687, 1, 372, 700, 688, 
	690, 698, 699, 698, 698, 699, 699, 699, 
	687, 1, 374, 701, 702, 699, 701, 698, 
	699, 699, 699, 77, 1, 78, 703, 77, 
	1, 78, 704, 77, 1, 78, 705, 705, 
	77, 1, 78, 706, 707, 706, 77, 1, 
	78, 707, 708, 707, 708, 708, 708, 77, 
	710, 712, 711, 713, 715, 711, 714, 715, 
	715, 715, 709, 710, 712, 716, 717, 719, 
	716, 718, 719, 719, 719, 709, 1, 392, 
	720, 721, 720, 77, 723, 396, 724, 725, 
	726, 724, 726, 726, 726, 722, 1, 392, 
	721, 1, 400, 727, 728, 730, 727, 729, 
	730, 730, 730, 77, 723, 396, 731, 725, 
	733, 731, 732, 733, 733, 733, 722, 723, 
	734, 732, 733, 732, 732, 733, 733, 733, 
	722, 1, 408, 735, 736, 733, 735, 732, 
	733, 733, 733, 77, 1, 78, 718, 719, 
	718, 718, 719, 719, 719, 77, 710, 712, 
	737, 738, 719, 737, 718, 719, 719, 719, 
	709, 739, 1, 80, 79, 81, 82, 83, 
	84, 85, 86, 87, 79, 77, 90, 89, 
	91, 92, 93, 94, 95, 96, 97, 89, 
	740, 0
};

static const short _checked_parse_test_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 0, 18, 56, 18, 18, 
	19, 20, 21, 22, 23, 24, 0, 24, 
	25, 26, 27, 54, 55, 26, 27, 54, 
	55, 27, 28, 53, 28, 28, 29, 30, 
	31, 32, 0, 33, 52, 33, 33, 34, 
	35, 36, 37, 38, 39, 40, 41, 42, 
	43, 44, 45, 46, 47, 48, 49, 50, 
	0, 410, 51, 26, 27, 57, 411, 58, 
	412, 235, 236, 281, 309, 324, 336, 394, 
	411, 59, 59, 60, 61, 106, 134, 149, 
	161, 219, 411, 62, 63, 64, 65, 411, 
	65, 66, 67, 105, 411, 67, 68, 69, 
	70, 71, 104, 72, 72, 73, 74, 101, 
	75, 76, 77, 100, 77, 78, 97, 79, 
	80, 81, 96, 81, 82, 93, 83, 411, 
	84, 85, 92, 86, 411, 87, 411, 86, 
	411, 87, 88, 89, 411, 87, 90, 91, 
	89, 90, 91, 89, 411, 87, 94, 84, 
	85, 95, 98, 80, 81, 99, 102, 76, 
	77, 103, 107, 108, 109, 411, 110, 116, 
	111, 411, 111, 112, 113, 411, 114, 115, 
	113, 411, 114, 114, 411, 117, 118, 119, 
	120, 121, 122, 123, 124, 125, 126, 411, 
	127, 128, 133, 411, 129, 130, 411, 131, 
	132, 135, 136, 137, 138, 139, 140, 411, 
	141, 142, 140, 411, 141, 142, 411, 143, 
	146, 144, 145, 146, 147, 148, 145, 147, 
	148, 146, 145, 146, 150, 151, 152, 153, 
	154, 154, 155, 156, 157, 159, 160, 156, 
	157, 159, 160, 157, 411, 158, 156, 157, 
	162, 163, 164, 165, 166, 182, 199, 167, 
	168, 169, 170, 411, 171, 411, 172, 173, 
	174, 175, 172, 173, 174, 175, 172, 175, 
	411, 176, 177, 411, 178, 411, 179, 180, 
	181, 178, 411, 179, 180, 181, 178, 411, 
	179, 183, 184, 185, 186, 187, 411, 187, 
	188, 411, 411, 189, 190, 191, 192, 189, 
	190, 191, 192, 189, 192, 411, 193, 194, 
	411, 195, 411, 196, 197, 198, 195, 411, 
	196, 197, 198, 196, 411, 195, 411, 196, 
	200, 201, 202, 203, 204, 205, 206, 207, 
	208, 411, 208, 209, 210, 211, 212, 213, 
	210, 211, 212, 213, 210, 213, 411, 213, 
	214, 215, 411, 216, 217, 218, 215, 411, 
	216, 217, 218, 216, 411, 215, 411, 216, 
	220, 221, 222, 222, 223, 224, 411, 225, 
	226, 233, 234, 225, 226, 233, 234, 227, 
	411, 228, 411, 227, 411, 228, 229, 230, 
	411, 228, 231, 232, 230, 231, 232, 230, 
	411, 228, 225, 226, 237, 238, 239, 240, 
	57, 0, 240, 411, 241, 242, 280, 57, 
	0, 242, 411, 243, 244, 245, 246, 279, 
	247, 247, 248, 249, 276, 250, 251, 252, 
	275, 252, 253, 272, 254, 255, 256, 271, 
	256, 257, 268, 258, 57, 0, 259, 411, 
	260, 267, 261, 262, 57, 0, 261, 262, 
	263, 264, 262, 265, 266, 264, 265, 266, 
	411, 264, 262, 269, 259, 260, 270, 273, 
	255, 256, 274, 277, 251, 252, 278, 282, 
	283, 284, 57, 0, 411, 285, 291, 286, 
	57, 0, 286, 411, 287, 288, 289, 290, 
	288, 289, 289, 292, 293, 294, 295, 296, 
	297, 298, 299, 300, 301, 57, 0, 411, 
	302, 303, 308, 57, 0, 411, 304, 305, 
	306, 307, 310, 311, 312, 313, 314, 315, 
	316, 317, 315, 316, 317, 57, 318, 411, 
	321, 319, 320, 321, 322, 323, 320, 322, 
	323, 321, 320, 321, 325, 326, 327, 328, 
	329, 329, 330, 331, 332, 334, 335, 331, 
	332, 334, 335, 332, 333, 331, 332, 337, 
	338, 339, 340, 341, 357, 374, 342, 343, 
	344, 345, 57, 0, 411, 346, 57, 0, 
	347, 411, 348, 349, 350, 347, 348, 349, 
	350, 347, 350, 57, 0, 351, 411, 352, 
	57, 0, 411, 353, 354, 355, 356, 353, 
	354, 355, 356, 353, 354, 358, 359, 360, 
	361, 362, 57, 0, 362, 411, 363, 57, 
	0, 364, 411, 365, 366, 367, 364, 365, 
	366, 367, 364, 367, 57, 0, 368, 411, 
	369, 57, 0, 411, 370, 371, 372, 373, 
	370, 371, 372, 373, 371, 370, 371, 375, 
	376, 377, 378, 379, 380, 381, 382, 383, 
	57, 0, 383, 411, 384, 385, 386, 387, 
	388, 385, 386, 387, 388, 385, 388, 57, 
	0, 388, 411, 389, 390, 391, 392, 393, 
	390, 391, 392, 393, 391, 390, 391, 395, 
	396, 397, 397, 398, 399, 57, 0, 400, 
	411, 401, 408, 409, 400, 401, 408, 409, 
	402, 403, 57, 0, 402, 403, 404, 405, 
	403, 406, 407, 405, 406, 407, 411, 405, 
	403, 400, 401, 410, 411
};

static const short _checked_parse_test_trans_actions_wi[] = {
	0, 0, 1, 71, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 73, 234, 0, 0, 1, 
	77, 0, 0, 0, 0, 0, 75, 75, 
	0, 127, 127, 13, 124, 0, 75, 0, 
	15, 0, 238, 0, 0, 1, 79, 0, 
	0, 0, 81, 103, 0, 0, 1, 83, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	85, 246, 0, 17, 17, 0, 112, 0, 
	211, 0, 41, 160, 87, 77, 362, 61, 
	101, 0, 1, 0, 41, 160, 87, 77, 
	362, 61, 109, 0, 0, 0, 0, 142, 
	33, 0, 21, 5, 145, 35, 0, 0, 
	0, 0, 5, 23, 0, 0, 0, 0, 
	0, 0, 25, 5, 0, 0, 0, 0, 
	0, 27, 5, 0, 0, 0, 0, 148, 
	0, 29, 5, 0, 222, 0, 151, 39, 
	381, 39, 0, 258, 456, 258, 13, 124, 
	0, 0, 15, 133, 444, 133, 0, 11, 
	121, 5, 0, 11, 118, 5, 0, 11, 
	115, 5, 0, 0, 0, 154, 43, 45, 
	0, 157, 47, 0, 31, 270, 31, 5, 
	47, 294, 47, 0, 106, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 163, 
	0, 0, 5, 166, 0, 0, 214, 0, 
	9, 0, 0, 0, 0, 0, 89, 416, 
	89, 89, 0, 250, 0, 0, 202, 75, 
	75, 0, 127, 127, 13, 124, 0, 0, 
	15, 0, 17, 17, 0, 0, 0, 0, 
	0, 75, 0, 127, 127, 13, 124, 0, 
	75, 0, 15, 0, 242, 0, 17, 17, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 172, 0, 314, 127, 13, 
	124, 127, 0, 0, 15, 0, 17, 17, 
	318, 0, 0, 178, 130, 426, 130, 13, 
	124, 0, 218, 0, 0, 15, 19, 366, 
	19, 0, 0, 0, 0, 0, 190, 65, 
	0, 199, 338, 127, 13, 124, 262, 0, 
	0, 15, 65, 17, 136, 346, 67, 0, 
	193, 130, 463, 266, 13, 124, 0, 406, 
	67, 0, 15, 0, 230, 19, 450, 139, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 205, 91, 0, 127, 13, 124, 127, 
	0, 0, 15, 91, 17, 17, 208, 93, 
	0, 130, 438, 130, 13, 124, 0, 421, 
	93, 0, 15, 0, 254, 19, 376, 19, 
	0, 0, 63, 0, 0, 0, 181, 127, 
	127, 13, 124, 0, 0, 0, 15, 0, 
	226, 0, 184, 59, 396, 59, 0, 130, 
	432, 130, 13, 124, 0, 0, 15, 19, 
	371, 19, 17, 17, 0, 0, 0, 0, 
	33, 33, 33, 274, 0, 21, 5, 35, 
	35, 35, 278, 0, 0, 0, 0, 5, 
	23, 0, 0, 0, 0, 0, 0, 25, 
	5, 0, 0, 0, 0, 0, 27, 5, 
	0, 0, 0, 0, 37, 37, 0, 282, 
	29, 5, 0, 0, 39, 39, 39, 39, 
	0, 258, 258, 13, 124, 0, 0, 15, 
	286, 133, 133, 0, 11, 121, 5, 0, 
	11, 118, 5, 0, 11, 115, 5, 0, 
	0, 0, 45, 45, 290, 43, 45, 0, 
	47, 47, 47, 298, 0, 31, 31, 5, 
	47, 47, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 49, 302, 
	0, 0, 5, 51, 51, 306, 0, 0, 
	0, 9, 0, 0, 0, 0, 0, 89, 
	89, 89, 0, 0, 0, 75, 75, 350, 
	75, 0, 127, 127, 13, 124, 0, 0, 
	15, 0, 17, 17, 0, 0, 0, 0, 
	0, 75, 0, 127, 127, 13, 124, 0, 
	75, 0, 15, 0, 0, 17, 17, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 53, 53, 310, 0, 169, 169, 
	127, 386, 13, 124, 127, 0, 0, 15, 
	0, 17, 17, 175, 175, 0, 391, 0, 
	55, 55, 322, 130, 130, 13, 124, 0, 
	0, 0, 15, 19, 19, 0, 0, 0, 
	0, 0, 65, 65, 65, 334, 0, 187, 
	187, 127, 401, 13, 124, 262, 0, 0, 
	15, 65, 17, 136, 196, 196, 67, 411, 
	0, 67, 67, 342, 130, 266, 13, 124, 
	0, 67, 0, 15, 0, 19, 139, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	91, 91, 91, 354, 0, 127, 13, 124, 
	127, 0, 0, 15, 91, 17, 17, 93, 
	93, 93, 358, 0, 130, 130, 13, 124, 
	0, 93, 0, 15, 0, 19, 19, 0, 
	0, 63, 0, 0, 0, 57, 57, 127, 
	326, 127, 13, 124, 0, 0, 0, 15, 
	0, 0, 59, 59, 59, 59, 0, 130, 
	130, 13, 124, 0, 0, 15, 330, 19, 
	19, 17, 17, 0, 99
};

static const short _checked_parse_test_to_state_actions[] = {
	0, 95, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 95, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 95, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 3, 0, 0, 3, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 7, 0, 0, 0, 0, 0, 0, 
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
	0, 3, 0, 0, 3, 0, 0, 0, 
	0, 0, 3, 0, 0, 0, 3, 0, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 0, 
	0, 3, 0, 0, 0, 3, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	7, 0, 0, 0, 0, 0, 0, 0, 
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
	0, 0, 95, 95, 0
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
	0, 0, 0, 97, 0
};

static const short _checked_parse_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 73, 0, 0, 0, 0, 0, 0, 
	75, 0, 75, 0, 0, 0, 0, 0, 
	81, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 85, 85, 81, 0, 75, 0, 
	73, 0, 0, 0, 0, 0, 0, 0, 
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
	33, 0, 35, 35, 35, 35, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 37, 37, 0, 39, 0, 0, 
	39, 39, 0, 37, 0, 37, 37, 0, 
	0, 0, 0, 0, 0, 0, 0, 35, 
	0, 0, 0, 0, 45, 0, 47, 0, 
	47, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 49, 51, 
	51, 0, 0, 51, 49, 0, 0, 0, 
	0, 0, 0, 0, 0, 75, 75, 0, 
	75, 0, 75, 0, 0, 0, 0, 0, 
	0, 75, 0, 75, 0, 0, 75, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 53, 169, 169, 53, 169, 175, 55, 
	55, 55, 0, 55, 55, 0, 0, 0, 
	0, 0, 65, 69, 187, 65, 69, 196, 
	67, 0, 67, 0, 67, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 91, 
	0, 91, 91, 0, 93, 0, 93, 0, 
	93, 0, 0, 0, 0, 0, 0, 57, 
	57, 0, 59, 0, 0, 59, 59, 0, 
	0, 57, 0, 0, 0
};

static const short _checked_parse_test_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 89, 89, 89, 89, 89, 
	89, 104, 89, 109, 109, 109, 109, 89, 
	89, 89, 89, 89, 89, 89, 89, 89, 
	89, 89, 89, 136, 136, 89, 143, 89, 
	89, 143, 143, 89, 136, 89, 136, 136, 
	89, 89, 89, 89, 89, 89, 89, 89, 
	109, 89, 89, 89, 89, 174, 89, 178, 
	89, 178, 89, 89, 89, 89, 89, 89, 
	89, 89, 89, 89, 89, 89, 200, 200, 
	204, 204, 89, 89, 204, 200, 89, 89, 
	89, 89, 89, 89, 89, 89, 223, 223, 
	89, 223, 89, 223, 89, 89, 89, 89, 
	89, 89, 223, 89, 223, 89, 89, 223, 
	89, 89, 89, 89, 89, 89, 89, 89, 
	89, 89, 268, 270, 270, 268, 270, 281, 
	284, 284, 284, 89, 284, 284, 89, 89, 
	89, 89, 89, 303, 306, 307, 303, 306, 
	318, 321, 89, 321, 89, 321, 89, 89, 
	89, 89, 89, 89, 89, 89, 89, 89, 
	346, 89, 346, 346, 89, 359, 89, 359, 
	89, 359, 89, 89, 89, 89, 89, 89, 
	383, 383, 89, 395, 89, 89, 395, 395, 
	89, 89, 383, 0, 0, 0, 0, 0, 
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
	0, 0, 0, 0, 741
};

static const int checked_parse_test_start = 1;
static const int checked_parse_test_first_final = 410;
static const int checked_parse_test_error = 0;

static const int checked_parse_test_en_checked_group_scanner = 411;
static const int checked_parse_test_en_main = 1;

#line 1004 "NanorexMMPImportExportTest.rl"
	
#line 7524 "NanorexMMPImportExportTest.cpp"
	{
	cs = checked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1005 "NanorexMMPImportExportTest.rl"
	
#line 7534 "NanorexMMPImportExportTest.cpp"
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
	case 69:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 7555 "NanorexMMPImportExportTest.cpp"
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
#line 43 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 51:
#line 50 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal/*, stringVal2*/); }
	break;
	case 52:
#line 55 "NanorexMMPImportExportTest.rl"
	{lineStart = p;}
	break;
	case 53:
#line 58 "NanorexMMPImportExportTest.rl"
	{ end1(); }
	break;
	case 54:
#line 59 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 55:
#line 63 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 56:
#line 67 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 57:
#line 68 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 58:
#line 73 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 59:
#line 73 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 60:
#line 79 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 61:
#line 84 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 62:
#line 89 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
	case 63:
#line 93 "NanorexMMPImportExportTest.rl"
	{lineStart=p;}
	break;
	case 64:
#line 104 "NanorexMMPImportExportTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 65:
#line 976 "NanorexMMPImportExportTest.rl"
	{ cerr << "*p=" << *p << endl;
			p--;
			{stack[top++] = cs; cs = 411; goto _again;}
		}
	break;
	case 66:
#line 982 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 411; goto _again;} }
	break;
	case 67:
#line 987 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 411; goto _again;} }
	break;
	case 70:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 71:
#line 110 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 72:
#line 111 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 73:
#line 113 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 74:
#line 114 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 75:
#line 115 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 76:
#line 116 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 77:
#line 117 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 78:
#line 118 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 79:
#line 119 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 80:
#line 122 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 81:
#line 124 "NanorexMMPImportExportTest.rl"
	{te = p+1;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 82:
#line 124 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 83:
#line 124 "NanorexMMPImportExportTest.rl"
	{{p = ((te))-1;}{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
#line 7971 "NanorexMMPImportExportTest.cpp"
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
	case 68:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
#line 7992 "NanorexMMPImportExportTest.cpp"
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
	case 54:
#line 59 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 57:
#line 68 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 61:
#line 84 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 62:
#line 89 "NanorexMMPImportExportTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
#line 8099 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 1006 "NanorexMMPImportExportTest.rl"
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


#line 1086 "NanorexMMPImportExportTest.rl"



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
	
	#line 1173 "NanorexMMPImportExportTest.rl"
	
#line 8230 "NanorexMMPImportExportTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 30, 1, 32, 1, 33, 1, 
	37, 1, 41, 1, 43, 1, 57, 1, 
	58, 2, 0, 29, 2, 0, 53, 2, 
	0, 55, 2, 0, 56, 2, 5, 12, 
	2, 5, 13, 2, 5, 14, 2, 6, 
	7, 2, 6, 8, 2, 6, 9, 2, 
	8, 15, 2, 35, 24, 2, 37, 0, 
	2, 41, 42, 3, 0, 16, 51, 3, 
	0, 19, 54, 3, 0, 20, 52, 3, 
	0, 23, 49, 3, 0, 25, 50, 3, 
	0, 27, 38, 3, 0, 28, 39, 3, 
	0, 28, 46, 3, 0, 31, 40, 3, 
	0, 34, 48, 3, 0, 36, 47, 3, 
	6, 8, 15, 3, 17, 0, 53, 3, 
	44, 0, 45, 4, 9, 0, 20, 52, 
	4, 9, 0, 23, 49, 4, 9, 0, 
	25, 50, 4, 9, 0, 36, 47, 4, 
	33, 0, 34, 48, 5, 6, 9, 0, 
	20, 52, 5, 6, 9, 0, 23, 49, 
	5, 6, 9, 0, 25, 50, 5, 6, 
	9, 0, 36, 47, 5, 8, 15, 0, 
	16, 51, 6, 6, 8, 15, 0, 16, 
	51
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 102, 107, 108, 
	109, 110, 111, 116, 127, 141, 155, 160, 
	165, 166, 167, 168, 173, 178, 179, 180, 
	181, 182, 187, 192, 193, 194, 195, 196, 
	197, 198, 199, 200, 205, 210, 215, 216, 
	217, 221, 223, 225, 227, 240, 254, 256, 
	257, 258, 259, 260, 261, 265, 271, 278, 
	283, 288, 290, 297, 299, 303, 309, 311, 
	313, 315, 317, 319, 323, 328, 329, 330, 
	331, 332, 333, 334, 335, 336, 341, 343, 
	354, 357, 360, 363, 368, 375, 382, 388, 
	395, 403, 409, 414, 420, 429, 433, 441, 
	447, 456, 460, 468, 474, 483, 487, 495, 
	501, 507, 520, 522, 537, 552, 566, 581, 
	589, 593, 601, 609, 617, 621, 629, 637, 
	645, 649, 657, 665, 673, 680, 683, 686, 
	689, 697, 702, 709, 717, 725, 727, 735, 
	738, 741, 744, 747, 750, 753, 756, 759, 
	762, 767, 774, 781, 788, 796, 802, 804, 
	812, 819, 822, 825, 828, 831, 834, 841, 
	848, 850, 863, 875, 890, 905, 911, 925, 
	940, 943, 946, 949, 952, 958, 970, 985, 
	1000, 1006, 1008, 1022, 1037, 1040, 1043, 1046, 
	1051, 1059, 1062, 1065, 1068, 1073, 1085, 1100, 
	1115, 1129, 1144, 1156, 1171, 1186, 1188, 1202, 
	1217, 1220, 1223, 1226, 1229, 1234, 1246, 1261, 
	1276, 1290, 1305, 1317, 1332, 1347, 1349, 1363, 
	1378, 1381, 1384, 1387, 1390, 1393, 1396, 1399, 
	1402, 1407, 1419, 1434, 1449, 1463, 1478, 1490, 
	1505, 1520, 1522, 1536, 1551, 1554, 1557, 1562, 
	1568, 1580, 1595, 1610, 1616, 1629, 1631, 1646, 
	1661, 1675, 1690, 1704, 1719, 1721, 1721, 1733
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
	32, 40, 11, 13, 9, 32, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 9, 13, 
	10, 32, 101, 9, 13, 110, 100, 49, 
	10, 32, 35, 9, 13, 10, 32, 103, 
	9, 13, 114, 111, 117, 112, 9, 32, 
	40, 11, 13, 9, 32, 67, 11, 13, 
	108, 105, 112, 98, 111, 97, 114, 100, 
	9, 32, 41, 11, 13, 10, 32, 35, 
	9, 13, 10, 32, 101, 9, 13, 110, 
	100, 9, 32, 11, 13, -1, 10, -1, 
	10, -1, 10, 9, 32, 95, 11, 13, 
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
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 110, 
	-1, 10, 102, -1, 10, 111, -1, 10, 
	32, 9, 13, -1, 10, 32, 97, 99, 
	111, 9, 13, -1, 10, 116, -1, 10, 
	111, -1, 10, 109, -1, 10, 32, 9, 
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
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
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 112, -1, 10, 101, 
	-1, 10, 110, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 9, 13, -1, 
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
	10, 111, -1, 10, 108, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, 32, 35, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 97, 98, 101, 
	103, 105, 109, 9, 13, -1, 10, 32, 
	97, 98, 101, 103, 105, 109, 9, 13, 
	0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 2, 3, 1, 1, 
	1, 1, 3, 3, 4, 4, 3, 3, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 3, 3, 1, 1, 
	2, 2, 2, 2, 3, 4, 2, 1, 
	1, 1, 1, 1, 2, 2, 3, 3, 
	3, 2, 3, 2, 2, 2, 0, 0, 
	0, 0, 0, 2, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 2, 9, 
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
	3, 3, 3, 3, 4, 4, 5, 5, 
	4, 2, 4, 5, 3, 3, 3, 3, 
	6, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 2, 0, 10, 9
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 0, 1, 4, 5, 5, 1, 1, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	0, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 1, 1, 0, 0, 
	1, 0, 0, 0, 5, 5, 0, 0, 
	0, 0, 0, 0, 1, 2, 2, 1, 
	1, 0, 2, 0, 1, 2, 1, 1, 
	1, 1, 1, 1, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 0, 1, 
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
	0, 0, 0, 0, 1, 4, 5, 5, 
	1, 0, 5, 5, 0, 0, 0, 1, 
	1, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 1, 1
};

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 127, 132, 134, 
	136, 138, 140, 145, 153, 163, 173, 178, 
	183, 185, 187, 189, 194, 199, 201, 203, 
	205, 207, 212, 217, 219, 221, 223, 225, 
	227, 229, 231, 233, 238, 243, 248, 250, 
	252, 256, 259, 262, 265, 274, 284, 287, 
	289, 291, 293, 295, 297, 301, 306, 312, 
	317, 322, 325, 331, 334, 338, 343, 345, 
	347, 349, 351, 353, 357, 362, 364, 366, 
	368, 370, 372, 374, 376, 378, 383, 386, 
	397, 401, 405, 409, 414, 420, 426, 432, 
	438, 445, 451, 456, 462, 470, 474, 481, 
	487, 495, 499, 506, 512, 520, 524, 531, 
	537, 543, 553, 556, 567, 578, 588, 599, 
	606, 610, 617, 624, 631, 635, 642, 649, 
	656, 660, 667, 674, 681, 687, 691, 695, 
	699, 707, 712, 718, 725, 732, 735, 742, 
	746, 750, 754, 758, 762, 766, 770, 774, 
	778, 783, 789, 795, 801, 808, 814, 817, 
	824, 830, 834, 838, 842, 846, 850, 857, 
	864, 867, 877, 886, 897, 908, 914, 924, 
	935, 939, 943, 947, 951, 957, 966, 977, 
	988, 994, 997, 1007, 1018, 1022, 1026, 1030, 
	1035, 1043, 1047, 1051, 1055, 1060, 1069, 1080, 
	1091, 1101, 1112, 1121, 1132, 1143, 1146, 1156, 
	1167, 1171, 1175, 1179, 1183, 1188, 1197, 1208, 
	1219, 1229, 1240, 1249, 1260, 1271, 1274, 1284, 
	1295, 1299, 1303, 1307, 1311, 1315, 1319, 1323, 
	1327, 1332, 1341, 1352, 1363, 1373, 1384, 1393, 
	1404, 1415, 1418, 1428, 1439, 1443, 1447, 1452, 
	1458, 1467, 1478, 1489, 1495, 1505, 1508, 1519, 
	1530, 1540, 1551, 1561, 1572, 1575, 1576, 1588
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
	59, 1, 60, 1, 60, 60, 61, 60, 
	1, 61, 61, 62, 61, 62, 62, 62, 
	1, 63, 63, 64, 66, 63, 65, 66, 
	66, 66, 1, 67, 67, 68, 70, 67, 
	69, 70, 70, 70, 1, 71, 68, 72, 
	68, 1, 74, 73, 75, 73, 1, 76, 
	1, 77, 1, 78, 1, 79, 78, 80, 
	78, 1, 82, 81, 83, 81, 1, 84, 
	1, 85, 1, 86, 1, 87, 1, 87, 
	87, 88, 87, 1, 88, 88, 89, 88, 
	1, 90, 1, 91, 1, 92, 1, 93, 
	1, 94, 1, 95, 1, 96, 1, 97, 
	1, 97, 97, 98, 97, 1, 99, 98, 
	100, 98, 1, 102, 101, 103, 101, 1, 
	104, 1, 105, 1, 106, 106, 106, 1, 
	1, 99, 100, 1, 79, 80, 1, 71, 
	72, 69, 69, 70, 69, 69, 70, 70, 
	70, 1, 107, 107, 108, 70, 107, 69, 
	70, 70, 70, 1, 1, 52, 53, 109, 
	1, 110, 1, 111, 1, 112, 1, 113, 
	1, 114, 114, 114, 1, 114, 114, 114, 
	115, 1, 117, 116, 118, 116, 119, 1, 
	121, 120, 122, 120, 1, 121, 123, 32, 
	123, 1, 1, 121, 122, 117, 116, 118, 
	116, 119, 1, 1, 28, 29, 124, 124, 
	124, 1, 124, 124, 124, 125, 1, 126, 
	1, 127, 1, 128, 1, 129, 1, 130, 
	1, 131, 131, 131, 1, 131, 131, 132, 
	131, 1, 133, 1, 134, 1, 135, 1, 
	136, 1, 137, 1, 138, 1, 139, 1, 
	140, 1, 28, 140, 29, 140, 1, 141, 
	143, 142, 141, 145, 144, 146, 147, 148, 
	149, 150, 151, 144, 142, 141, 143, 152, 
	142, 141, 143, 153, 142, 141, 143, 154, 
	142, 141, 143, 155, 155, 142, 141, 143, 
	155, 155, 156, 142, 141, 143, 157, 157, 
	158, 142, 141, 143, 159, 160, 159, 142, 
	141, 143, 160, 160, 161, 142, 141, 143, 
	162, 163, 162, 164, 142, 141, 143, 162, 
	163, 162, 142, 141, 143, 165, 165, 142, 
	141, 143, 166, 167, 166, 142, 141, 143, 
	167, 168, 169, 167, 170, 142, 141, 143, 
	170, 142, 141, 143, 171, 172, 171, 173, 
	142, 141, 143, 171, 172, 171, 142, 141, 
	143, 174, 175, 176, 174, 177, 142, 141, 
	143, 177, 142, 141, 143, 178, 179, 178, 
	180, 142, 141, 143, 178, 179, 178, 142, 
	141, 143, 181, 182, 183, 181, 184, 142, 
	141, 143, 184, 142, 141, 143, 185, 186, 
	185, 187, 142, 141, 143, 185, 186, 185, 
	142, 141, 189, 188, 190, 188, 142, 141, 
	189, 188, 190, 191, 188, 191, 191, 191, 
	142, 141, 189, 190, 141, 193, 192, 194, 
	196, 192, 195, 196, 196, 196, 142, 141, 
	189, 197, 190, 199, 197, 198, 199, 199, 
	199, 142, 141, 143, 198, 199, 198, 198, 
	199, 199, 199, 142, 141, 201, 200, 202, 
	199, 200, 198, 199, 199, 199, 142, 141, 
	143, 185, 186, 185, 187, 142, 141, 143, 
	203, 142, 141, 143, 204, 205, 204, 206, 
	142, 141, 143, 204, 205, 204, 206, 142, 
	141, 143, 178, 179, 178, 180, 142, 141, 
	143, 207, 142, 141, 143, 208, 209, 208, 
	210, 142, 141, 143, 208, 209, 208, 210, 
	142, 141, 143, 171, 172, 171, 173, 142, 
	141, 143, 211, 142, 141, 143, 212, 213, 
	212, 214, 142, 141, 143, 212, 213, 212, 
	214, 142, 141, 143, 162, 163, 162, 164, 
	142, 141, 143, 157, 157, 158, 142, 141, 
	143, 215, 142, 141, 143, 216, 142, 141, 
	143, 217, 142, 141, 143, 219, 218, 218, 
	218, 218, 142, 141, 143, 220, 220, 142, 
	141, 143, 220, 220, 221, 142, 141, 223, 
	222, 224, 222, 225, 142, 141, 227, 226, 
	228, 226, 221, 142, 141, 227, 228, 141, 
	223, 222, 224, 222, 225, 142, 141, 143, 
	229, 142, 141, 143, 230, 142, 141, 143, 
	231, 142, 141, 143, 232, 142, 141, 143, 
	233, 142, 141, 143, 234, 142, 141, 143, 
	235, 142, 141, 143, 236, 142, 141, 143, 
	237, 142, 141, 143, 238, 238, 142, 141, 
	143, 238, 238, 239, 142, 141, 143, 240, 
	240, 241, 142, 141, 143, 240, 240, 242, 
	142, 141, 244, 243, 245, 243, 246, 142, 
	141, 244, 243, 245, 243, 142, 141, 244, 
	245, 141, 244, 243, 245, 243, 246, 142, 
	141, 143, 240, 240, 241, 142, 141, 143, 
	247, 142, 141, 143, 248, 142, 141, 143, 
	249, 142, 141, 143, 250, 142, 141, 143, 
	251, 142, 141, 253, 252, 254, 255, 252, 
	142, 141, 257, 256, 258, 259, 256, 142, 
	141, 257, 258, 141, 143, 260, 261, 262, 
	260, 262, 262, 262, 142, 141, 143, 260, 
	262, 260, 262, 262, 262, 142, 141, 143, 
	263, 264, 266, 263, 265, 266, 266, 266, 
	142, 141, 143, 267, 261, 269, 267, 268, 
	269, 269, 269, 142, 141, 257, 261, 258, 
	261, 142, 141, 143, 268, 269, 268, 268, 
	269, 269, 269, 142, 141, 143, 270, 271, 
	269, 270, 268, 269, 269, 269, 142, 141, 
	143, 272, 142, 141, 143, 273, 142, 141, 
	143, 274, 142, 141, 143, 275, 142, 141, 
	143, 275, 276, 275, 142, 141, 143, 276, 
	277, 276, 277, 277, 277, 142, 141, 143, 
	278, 279, 281, 278, 280, 281, 281, 281, 
	142, 141, 143, 282, 283, 285, 282, 284, 
	285, 285, 285, 142, 141, 286, 283, 287, 
	283, 142, 141, 286, 287, 141, 143, 284, 
	285, 284, 284, 285, 285, 285, 142, 141, 
	143, 288, 289, 285, 288, 284, 285, 285, 
	285, 142, 141, 143, 290, 142, 141, 143, 
	291, 142, 141, 143, 292, 142, 141, 143, 
	293, 293, 142, 141, 143, 293, 294, 295, 
	296, 293, 142, 141, 143, 297, 142, 141, 
	143, 298, 142, 141, 143, 299, 142, 141, 
	143, 300, 300, 142, 141, 143, 300, 301, 
	300, 301, 301, 301, 142, 141, 143, 302, 
	305, 304, 302, 303, 304, 304, 304, 142, 
	141, 143, 306, 309, 308, 306, 307, 308, 
	308, 308, 142, 141, 143, 307, 308, 307, 
	307, 308, 308, 308, 142, 141, 143, 310, 
	311, 308, 310, 307, 308, 308, 308, 142, 
	141, 143, 309, 312, 309, 312, 312, 312, 
	142, 141, 314, 313, 315, 317, 313, 316, 
	317, 317, 317, 142, 141, 319, 318, 320, 
	322, 318, 321, 322, 322, 322, 142, 141, 
	319, 320, 141, 143, 321, 322, 321, 321, 
	322, 322, 322, 142, 141, 324, 323, 325, 
	322, 323, 321, 322, 322, 322, 142, 141, 
	143, 326, 142, 141, 143, 327, 142, 141, 
	143, 328, 142, 141, 143, 329, 142, 141, 
	143, 330, 330, 142, 141, 143, 330, 331, 
	330, 331, 331, 331, 142, 141, 143, 332, 
	335, 334, 332, 333, 334, 334, 334, 142, 
	141, 143, 336, 339, 338, 336, 337, 338, 
	338, 338, 142, 141, 143, 337, 338, 337, 
	337, 338, 338, 338, 142, 141, 143, 340, 
	341, 338, 340, 337, 338, 338, 338, 142, 
	141, 143, 339, 342, 339, 342, 342, 342, 
	142, 141, 344, 343, 345, 347, 343, 346, 
	347, 347, 347, 142, 141, 349, 348, 350, 
	352, 348, 351, 352, 352, 352, 142, 141, 
	349, 350, 141, 143, 351, 352, 351, 351, 
	352, 352, 352, 142, 141, 354, 353, 355, 
	352, 353, 351, 352, 352, 352, 142, 141, 
	143, 356, 142, 141, 143, 357, 142, 141, 
	143, 358, 142, 141, 143, 359, 142, 141, 
	143, 360, 142, 141, 143, 361, 142, 141, 
	143, 362, 142, 141, 143, 363, 142, 141, 
	143, 364, 364, 142, 141, 143, 364, 365, 
	364, 365, 365, 365, 142, 141, 143, 366, 
	369, 368, 366, 367, 368, 368, 368, 142, 
	141, 143, 370, 373, 372, 370, 371, 372, 
	372, 372, 142, 141, 143, 371, 372, 371, 
	371, 372, 372, 372, 142, 141, 143, 374, 
	375, 372, 374, 371, 372, 372, 372, 142, 
	141, 143, 373, 376, 373, 376, 376, 376, 
	142, 141, 378, 377, 379, 381, 377, 380, 
	381, 381, 381, 142, 141, 383, 382, 384, 
	386, 382, 385, 386, 386, 386, 142, 141, 
	383, 384, 141, 143, 385, 386, 385, 385, 
	386, 386, 386, 142, 141, 388, 387, 389, 
	386, 387, 385, 386, 386, 386, 142, 141, 
	143, 390, 142, 141, 143, 391, 142, 141, 
	143, 392, 392, 142, 141, 143, 392, 393, 
	392, 142, 141, 143, 393, 394, 393, 394, 
	394, 394, 142, 141, 143, 395, 396, 398, 
	395, 397, 398, 398, 398, 142, 141, 143, 
	399, 400, 402, 399, 401, 402, 402, 402, 
	142, 141, 404, 403, 405, 403, 142, 141, 
	404, 403, 405, 406, 403, 406, 406, 406, 
	142, 141, 404, 405, 141, 408, 407, 409, 
	411, 407, 410, 411, 411, 411, 142, 141, 
	404, 412, 405, 414, 412, 413, 414, 414, 
	414, 142, 141, 143, 413, 414, 413, 413, 
	414, 414, 414, 142, 141, 416, 415, 417, 
	414, 415, 413, 414, 414, 414, 142, 141, 
	143, 401, 402, 401, 401, 402, 402, 402, 
	142, 141, 143, 418, 419, 402, 418, 401, 
	402, 402, 402, 142, 1, 421, 420, 106, 
	1, 145, 144, 420, 146, 147, 148, 149, 
	150, 151, 144, 142, 422, 145, 144, 146, 
	147, 148, 149, 150, 151, 144, 142, 0
};

static const short _parse_tester_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 18, 19, 20, 21, 22, 
	23, 24, 25, 26, 27, 99, 100, 27, 
	28, 87, 29, 30, 31, 32, 33, 34, 
	33, 34, 35, 36, 37, 38, 39, 40, 
	41, 42, 43, 44, 45, 86, 45, 45, 
	46, 47, 48, 49, 50, 51, 52, 53, 
	54, 84, 85, 53, 54, 84, 85, 55, 
	83, 55, 55, 56, 57, 58, 59, 60, 
	82, 60, 60, 61, 62, 63, 64, 65, 
	66, 67, 68, 69, 70, 71, 72, 73, 
	74, 75, 76, 77, 81, 77, 77, 78, 
	79, 80, 293, 53, 54, 88, 89, 90, 
	91, 92, 93, 94, 95, 96, 97, 98, 
	95, 96, 97, 96, 101, 102, 103, 104, 
	105, 106, 107, 108, 109, 110, 111, 112, 
	113, 114, 115, 116, 117, 294, 118, 294, 
	119, 295, 120, 165, 193, 208, 220, 276, 
	121, 122, 123, 124, 125, 126, 164, 126, 
	127, 128, 129, 130, 163, 131, 131, 132, 
	133, 160, 134, 135, 136, 159, 136, 137, 
	156, 138, 139, 140, 155, 140, 141, 152, 
	142, 143, 144, 151, 145, 294, 146, 147, 
	148, 294, 146, 149, 150, 148, 149, 150, 
	148, 294, 146, 153, 143, 144, 154, 157, 
	139, 140, 158, 161, 135, 136, 162, 166, 
	167, 168, 169, 175, 170, 171, 172, 294, 
	173, 174, 172, 294, 173, 176, 177, 178, 
	179, 180, 181, 182, 183, 184, 185, 186, 
	187, 192, 188, 189, 294, 190, 191, 194, 
	195, 196, 197, 198, 199, 294, 200, 201, 
	199, 294, 200, 201, 202, 205, 203, 204, 
	205, 206, 207, 204, 206, 207, 204, 205, 
	209, 210, 211, 212, 213, 214, 215, 216, 
	218, 219, 215, 216, 218, 219, 294, 217, 
	215, 216, 221, 222, 223, 224, 225, 240, 
	256, 226, 227, 228, 229, 230, 231, 232, 
	233, 234, 231, 232, 233, 234, 231, 234, 
	235, 236, 294, 237, 238, 239, 236, 294, 
	237, 238, 239, 236, 294, 237, 241, 242, 
	243, 244, 245, 246, 247, 248, 249, 250, 
	247, 248, 249, 250, 247, 250, 251, 252, 
	294, 253, 254, 255, 252, 294, 253, 254, 
	255, 252, 294, 253, 257, 258, 259, 260, 
	261, 262, 263, 264, 265, 266, 267, 268, 
	269, 270, 267, 268, 269, 270, 267, 270, 
	271, 272, 294, 273, 274, 275, 272, 294, 
	273, 274, 275, 272, 294, 273, 277, 278, 
	279, 280, 281, 282, 283, 290, 291, 282, 
	283, 290, 291, 284, 294, 285, 286, 287, 
	294, 285, 288, 289, 287, 288, 289, 287, 
	294, 285, 282, 283, 292, 294, 294
};

static const unsigned char _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 39, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 119, 0, 0, 1, 
	0, 0, 0, 0, 0, 0, 0, 81, 
	81, 13, 78, 0, 0, 0, 15, 123, 
	0, 0, 1, 0, 0, 0, 0, 57, 
	0, 0, 1, 41, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 131, 0, 0, 1, 0, 
	0, 0, 0, 17, 17, 0, 0, 0, 
	0, 0, 0, 0, 47, 93, 47, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 55, 0, 66, 
	0, 151, 0, 0, 43, 0, 90, 35, 
	0, 0, 0, 0, 0, 21, 5, 0, 
	0, 0, 0, 0, 5, 23, 0, 0, 
	0, 0, 0, 0, 25, 5, 0, 0, 
	0, 0, 0, 27, 5, 0, 0, 0, 
	0, 0, 29, 5, 0, 99, 0, 0, 
	143, 210, 143, 13, 78, 0, 0, 15, 
	87, 204, 87, 0, 11, 75, 5, 0, 
	11, 72, 5, 0, 11, 69, 5, 0, 
	0, 0, 33, 0, 0, 0, 31, 147, 
	31, 5, 0, 60, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 5, 0, 0, 103, 0, 9, 0, 
	0, 0, 0, 0, 45, 175, 45, 45, 
	0, 135, 0, 0, 0, 0, 0, 81, 
	81, 13, 78, 0, 0, 15, 17, 17, 
	0, 0, 0, 0, 0, 0, 81, 81, 
	13, 78, 0, 0, 0, 15, 127, 0, 
	17, 17, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 81, 13, 
	78, 81, 0, 0, 15, 0, 17, 17, 
	0, 84, 180, 84, 13, 78, 0, 107, 
	0, 0, 15, 19, 155, 19, 0, 0, 
	0, 0, 0, 0, 81, 13, 78, 81, 
	0, 0, 15, 0, 17, 17, 0, 84, 
	192, 84, 13, 78, 0, 115, 0, 0, 
	15, 19, 165, 19, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 81, 13, 
	78, 81, 0, 0, 15, 0, 17, 17, 
	0, 84, 198, 84, 13, 78, 0, 139, 
	0, 0, 15, 19, 170, 19, 0, 0, 
	0, 0, 0, 81, 81, 13, 78, 0, 
	0, 0, 15, 0, 111, 0, 0, 84, 
	186, 84, 13, 78, 0, 0, 15, 19, 
	160, 19, 17, 17, 0, 63, 53
};

static const unsigned char _parse_tester_to_state_actions[] = {
	0, 49, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 49, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
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
	0, 0, 0, 0, 0, 0, 37, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 96, 0
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
	0, 0, 0, 0, 0, 0, 51, 0
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
	0, 0, 0, 0, 0, 0, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 0, 0, 0, 423
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 293;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 294;
static const int parse_tester_en_main = 1;

#line 1174 "NanorexMMPImportExportTest.rl"
	
#line 9088 "NanorexMMPImportExportTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1175 "NanorexMMPImportExportTest.rl"
	
#line 9098 "NanorexMMPImportExportTest.cpp"
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
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 9119 "NanorexMMPImportExportTest.cpp"
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
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal/*, stringVal2*/); }
	break;
	case 29:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
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
#line 1058 "NanorexMMPImportExportTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 38:
#line 1072 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 39:
#line 1075 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 40:
#line 1080 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 44:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 102 "NanorexMMPImportExportTest.rl"
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
#line 91 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 49:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
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
#line 100 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 57:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
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
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 9433 "NanorexMMPImportExportTest.cpp"
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
	case 41:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 9462 "NanorexMMPImportExportTest.cpp"
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
#line 1176 "NanorexMMPImportExportTest.rl"
}


void NanorexMMPImportExportTest::fileParseTest(void)
{
	fileParseTestH2O();
	fileParseTestHOOH();
	fileParseTestChlorophyll();
	fileParseTestVanillin();
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
	
	#line 1283 "NanorexMMPImportExportTest.rl"
	
#line 9590 "NanorexMMPImportExportTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 1, 8, 1, 9, 1, 10, 1, 
	11, 1, 12, 1, 13, 1, 14, 1, 
	17, 1, 18, 1, 21, 1, 22, 1, 
	26, 1, 30, 1, 32, 1, 33, 1, 
	37, 1, 41, 1, 43, 1, 57, 1, 
	58, 2, 0, 29, 2, 0, 53, 2, 
	0, 55, 2, 0, 56, 2, 5, 12, 
	2, 5, 13, 2, 5, 14, 2, 6, 
	7, 2, 6, 8, 2, 6, 9, 2, 
	8, 15, 2, 35, 24, 2, 37, 0, 
	2, 41, 42, 3, 0, 16, 51, 3, 
	0, 19, 54, 3, 0, 20, 52, 3, 
	0, 23, 49, 3, 0, 25, 50, 3, 
	0, 27, 38, 3, 0, 28, 39, 3, 
	0, 28, 46, 3, 0, 31, 40, 3, 
	0, 34, 48, 3, 0, 36, 47, 3, 
	6, 8, 15, 3, 17, 0, 53, 3, 
	44, 0, 45, 4, 9, 0, 20, 52, 
	4, 9, 0, 23, 49, 4, 9, 0, 
	25, 50, 4, 9, 0, 36, 47, 4, 
	33, 0, 34, 48, 5, 6, 9, 0, 
	20, 52, 5, 6, 9, 0, 23, 49, 
	5, 6, 9, 0, 25, 50, 5, 6, 
	9, 0, 36, 47, 5, 8, 15, 0, 
	16, 51, 6, 6, 8, 15, 0, 16, 
	51
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 102, 107, 108, 
	109, 110, 111, 116, 127, 141, 155, 160, 
	165, 166, 167, 168, 173, 178, 179, 180, 
	181, 182, 187, 192, 193, 194, 195, 196, 
	197, 198, 199, 200, 205, 210, 215, 216, 
	217, 221, 223, 225, 227, 240, 254, 256, 
	257, 258, 259, 260, 261, 265, 271, 278, 
	283, 288, 290, 297, 299, 303, 309, 311, 
	313, 315, 317, 319, 323, 328, 329, 330, 
	331, 332, 333, 334, 335, 336, 341, 343, 
	354, 357, 360, 363, 368, 375, 382, 388, 
	395, 403, 409, 414, 420, 429, 433, 441, 
	447, 456, 460, 468, 474, 483, 487, 495, 
	501, 507, 520, 522, 537, 552, 566, 581, 
	589, 593, 601, 609, 617, 621, 629, 637, 
	645, 649, 657, 665, 673, 680, 683, 686, 
	689, 697, 702, 709, 717, 725, 727, 735, 
	738, 741, 744, 747, 750, 753, 756, 759, 
	762, 767, 774, 781, 788, 796, 802, 804, 
	812, 819, 822, 825, 828, 831, 834, 841, 
	848, 850, 863, 875, 890, 905, 911, 925, 
	940, 943, 946, 949, 952, 958, 970, 985, 
	1000, 1006, 1008, 1022, 1037, 1040, 1043, 1046, 
	1051, 1059, 1062, 1065, 1068, 1073, 1085, 1100, 
	1115, 1129, 1144, 1156, 1171, 1186, 1188, 1202, 
	1217, 1220, 1223, 1226, 1229, 1234, 1246, 1261, 
	1276, 1290, 1305, 1317, 1332, 1347, 1349, 1363, 
	1378, 1381, 1384, 1387, 1390, 1393, 1396, 1399, 
	1402, 1407, 1419, 1434, 1449, 1463, 1478, 1490, 
	1505, 1520, 1522, 1536, 1551, 1554, 1557, 1562, 
	1568, 1580, 1595, 1610, 1616, 1629, 1631, 1646, 
	1661, 1675, 1690, 1704, 1719, 1721, 1721, 1733
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
	32, 40, 11, 13, 9, 32, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 9, 13, 
	10, 32, 101, 9, 13, 110, 100, 49, 
	10, 32, 35, 9, 13, 10, 32, 103, 
	9, 13, 114, 111, 117, 112, 9, 32, 
	40, 11, 13, 9, 32, 67, 11, 13, 
	108, 105, 112, 98, 111, 97, 114, 100, 
	9, 32, 41, 11, 13, 10, 32, 35, 
	9, 13, 10, 32, 101, 9, 13, 110, 
	100, 9, 32, 11, 13, -1, 10, -1, 
	10, -1, 10, 9, 32, 95, 11, 13, 
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
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 110, 
	-1, 10, 102, -1, 10, 111, -1, 10, 
	32, 9, 13, -1, 10, 32, 97, 99, 
	111, 9, 13, -1, 10, 116, -1, 10, 
	111, -1, 10, 109, -1, 10, 32, 9, 
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	61, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 61, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 61, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
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
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 112, -1, 10, 101, 
	-1, 10, 110, -1, 10, 103, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 9, 13, -1, 
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
	10, 111, -1, 10, 108, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, 32, 35, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 97, 98, 101, 
	103, 105, 109, 9, 13, -1, 10, 32, 
	97, 98, 101, 103, 105, 109, 9, 13, 
	0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 2, 3, 1, 1, 
	1, 1, 3, 3, 4, 4, 3, 3, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 3, 3, 1, 1, 
	2, 2, 2, 2, 3, 4, 2, 1, 
	1, 1, 1, 1, 2, 2, 3, 3, 
	3, 2, 3, 2, 2, 2, 0, 0, 
	0, 0, 0, 2, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 2, 9, 
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
	3, 3, 3, 3, 4, 4, 5, 5, 
	4, 2, 4, 5, 3, 3, 3, 3, 
	6, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 2, 0, 10, 9
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 0, 1, 0, 0, 
	0, 0, 1, 4, 5, 5, 1, 1, 
	0, 0, 0, 1, 1, 0, 0, 0, 
	0, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 1, 1, 0, 0, 
	1, 0, 0, 0, 5, 5, 0, 0, 
	0, 0, 0, 0, 1, 2, 2, 1, 
	1, 0, 2, 0, 1, 2, 1, 1, 
	1, 1, 1, 1, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 1, 0, 1, 
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
	0, 0, 0, 0, 1, 4, 5, 5, 
	1, 0, 5, 5, 0, 0, 0, 1, 
	1, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 1, 1
};

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 127, 132, 134, 
	136, 138, 140, 145, 153, 163, 173, 178, 
	183, 185, 187, 189, 194, 199, 201, 203, 
	205, 207, 212, 217, 219, 221, 223, 225, 
	227, 229, 231, 233, 238, 243, 248, 250, 
	252, 256, 259, 262, 265, 274, 284, 287, 
	289, 291, 293, 295, 297, 301, 306, 312, 
	317, 322, 325, 331, 334, 338, 343, 345, 
	347, 349, 351, 353, 357, 362, 364, 366, 
	368, 370, 372, 374, 376, 378, 383, 386, 
	397, 401, 405, 409, 414, 420, 426, 432, 
	438, 445, 451, 456, 462, 470, 474, 481, 
	487, 495, 499, 506, 512, 520, 524, 531, 
	537, 543, 553, 556, 567, 578, 588, 599, 
	606, 610, 617, 624, 631, 635, 642, 649, 
	656, 660, 667, 674, 681, 687, 691, 695, 
	699, 707, 712, 718, 725, 732, 735, 742, 
	746, 750, 754, 758, 762, 766, 770, 774, 
	778, 783, 789, 795, 801, 808, 814, 817, 
	824, 830, 834, 838, 842, 846, 850, 857, 
	864, 867, 877, 886, 897, 908, 914, 924, 
	935, 939, 943, 947, 951, 957, 966, 977, 
	988, 994, 997, 1007, 1018, 1022, 1026, 1030, 
	1035, 1043, 1047, 1051, 1055, 1060, 1069, 1080, 
	1091, 1101, 1112, 1121, 1132, 1143, 1146, 1156, 
	1167, 1171, 1175, 1179, 1183, 1188, 1197, 1208, 
	1219, 1229, 1240, 1249, 1260, 1271, 1274, 1284, 
	1295, 1299, 1303, 1307, 1311, 1315, 1319, 1323, 
	1327, 1332, 1341, 1352, 1363, 1373, 1384, 1393, 
	1404, 1415, 1418, 1428, 1439, 1443, 1447, 1452, 
	1458, 1467, 1478, 1489, 1495, 1505, 1508, 1519, 
	1530, 1540, 1551, 1561, 1572, 1575, 1576, 1588
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
	59, 1, 60, 1, 60, 60, 61, 60, 
	1, 61, 61, 62, 61, 62, 62, 62, 
	1, 63, 63, 64, 66, 63, 65, 66, 
	66, 66, 1, 67, 67, 68, 70, 67, 
	69, 70, 70, 70, 1, 71, 68, 72, 
	68, 1, 74, 73, 75, 73, 1, 76, 
	1, 77, 1, 78, 1, 79, 78, 80, 
	78, 1, 82, 81, 83, 81, 1, 84, 
	1, 85, 1, 86, 1, 87, 1, 87, 
	87, 88, 87, 1, 88, 88, 89, 88, 
	1, 90, 1, 91, 1, 92, 1, 93, 
	1, 94, 1, 95, 1, 96, 1, 97, 
	1, 97, 97, 98, 97, 1, 99, 98, 
	100, 98, 1, 102, 101, 103, 101, 1, 
	104, 1, 105, 1, 106, 106, 106, 1, 
	1, 99, 100, 1, 79, 80, 1, 71, 
	72, 69, 69, 70, 69, 69, 70, 70, 
	70, 1, 107, 107, 108, 70, 107, 69, 
	70, 70, 70, 1, 1, 52, 53, 109, 
	1, 110, 1, 111, 1, 112, 1, 113, 
	1, 114, 114, 114, 1, 114, 114, 114, 
	115, 1, 117, 116, 118, 116, 119, 1, 
	121, 120, 122, 120, 1, 121, 123, 32, 
	123, 1, 1, 121, 122, 117, 116, 118, 
	116, 119, 1, 1, 28, 29, 124, 124, 
	124, 1, 124, 124, 124, 125, 1, 126, 
	1, 127, 1, 128, 1, 129, 1, 130, 
	1, 131, 131, 131, 1, 131, 131, 132, 
	131, 1, 133, 1, 134, 1, 135, 1, 
	136, 1, 137, 1, 138, 1, 139, 1, 
	140, 1, 28, 140, 29, 140, 1, 141, 
	143, 142, 141, 145, 144, 146, 147, 148, 
	149, 150, 151, 144, 142, 141, 143, 152, 
	142, 141, 143, 153, 142, 141, 143, 154, 
	142, 141, 143, 155, 155, 142, 141, 143, 
	155, 155, 156, 142, 141, 143, 157, 157, 
	158, 142, 141, 143, 159, 160, 159, 142, 
	141, 143, 160, 160, 161, 142, 141, 143, 
	162, 163, 162, 164, 142, 141, 143, 162, 
	163, 162, 142, 141, 143, 165, 165, 142, 
	141, 143, 166, 167, 166, 142, 141, 143, 
	167, 168, 169, 167, 170, 142, 141, 143, 
	170, 142, 141, 143, 171, 172, 171, 173, 
	142, 141, 143, 171, 172, 171, 142, 141, 
	143, 174, 175, 176, 174, 177, 142, 141, 
	143, 177, 142, 141, 143, 178, 179, 178, 
	180, 142, 141, 143, 178, 179, 178, 142, 
	141, 143, 181, 182, 183, 181, 184, 142, 
	141, 143, 184, 142, 141, 143, 185, 186, 
	185, 187, 142, 141, 143, 185, 186, 185, 
	142, 141, 189, 188, 190, 188, 142, 141, 
	189, 188, 190, 191, 188, 191, 191, 191, 
	142, 141, 189, 190, 141, 193, 192, 194, 
	196, 192, 195, 196, 196, 196, 142, 141, 
	189, 197, 190, 199, 197, 198, 199, 199, 
	199, 142, 141, 143, 198, 199, 198, 198, 
	199, 199, 199, 142, 141, 201, 200, 202, 
	199, 200, 198, 199, 199, 199, 142, 141, 
	143, 185, 186, 185, 187, 142, 141, 143, 
	203, 142, 141, 143, 204, 205, 204, 206, 
	142, 141, 143, 204, 205, 204, 206, 142, 
	141, 143, 178, 179, 178, 180, 142, 141, 
	143, 207, 142, 141, 143, 208, 209, 208, 
	210, 142, 141, 143, 208, 209, 208, 210, 
	142, 141, 143, 171, 172, 171, 173, 142, 
	141, 143, 211, 142, 141, 143, 212, 213, 
	212, 214, 142, 141, 143, 212, 213, 212, 
	214, 142, 141, 143, 162, 163, 162, 164, 
	142, 141, 143, 157, 157, 158, 142, 141, 
	143, 215, 142, 141, 143, 216, 142, 141, 
	143, 217, 142, 141, 143, 219, 218, 218, 
	218, 218, 142, 141, 143, 220, 220, 142, 
	141, 143, 220, 220, 221, 142, 141, 223, 
	222, 224, 222, 225, 142, 141, 227, 226, 
	228, 226, 221, 142, 141, 227, 228, 141, 
	223, 222, 224, 222, 225, 142, 141, 143, 
	229, 142, 141, 143, 230, 142, 141, 143, 
	231, 142, 141, 143, 232, 142, 141, 143, 
	233, 142, 141, 143, 234, 142, 141, 143, 
	235, 142, 141, 143, 236, 142, 141, 143, 
	237, 142, 141, 143, 238, 238, 142, 141, 
	143, 238, 238, 239, 142, 141, 143, 240, 
	240, 241, 142, 141, 143, 240, 240, 242, 
	142, 141, 244, 243, 245, 243, 246, 142, 
	141, 244, 243, 245, 243, 142, 141, 244, 
	245, 141, 244, 243, 245, 243, 246, 142, 
	141, 143, 240, 240, 241, 142, 141, 143, 
	247, 142, 141, 143, 248, 142, 141, 143, 
	249, 142, 141, 143, 250, 142, 141, 143, 
	251, 142, 141, 253, 252, 254, 255, 252, 
	142, 141, 257, 256, 258, 259, 256, 142, 
	141, 257, 258, 141, 143, 260, 261, 262, 
	260, 262, 262, 262, 142, 141, 143, 260, 
	262, 260, 262, 262, 262, 142, 141, 143, 
	263, 264, 266, 263, 265, 266, 266, 266, 
	142, 141, 143, 267, 261, 269, 267, 268, 
	269, 269, 269, 142, 141, 257, 261, 258, 
	261, 142, 141, 143, 268, 269, 268, 268, 
	269, 269, 269, 142, 141, 143, 270, 271, 
	269, 270, 268, 269, 269, 269, 142, 141, 
	143, 272, 142, 141, 143, 273, 142, 141, 
	143, 274, 142, 141, 143, 275, 142, 141, 
	143, 275, 276, 275, 142, 141, 143, 276, 
	277, 276, 277, 277, 277, 142, 141, 143, 
	278, 279, 281, 278, 280, 281, 281, 281, 
	142, 141, 143, 282, 283, 285, 282, 284, 
	285, 285, 285, 142, 141, 286, 283, 287, 
	283, 142, 141, 286, 287, 141, 143, 284, 
	285, 284, 284, 285, 285, 285, 142, 141, 
	143, 288, 289, 285, 288, 284, 285, 285, 
	285, 142, 141, 143, 290, 142, 141, 143, 
	291, 142, 141, 143, 292, 142, 141, 143, 
	293, 293, 142, 141, 143, 293, 294, 295, 
	296, 293, 142, 141, 143, 297, 142, 141, 
	143, 298, 142, 141, 143, 299, 142, 141, 
	143, 300, 300, 142, 141, 143, 300, 301, 
	300, 301, 301, 301, 142, 141, 143, 302, 
	305, 304, 302, 303, 304, 304, 304, 142, 
	141, 143, 306, 309, 308, 306, 307, 308, 
	308, 308, 142, 141, 143, 307, 308, 307, 
	307, 308, 308, 308, 142, 141, 143, 310, 
	311, 308, 310, 307, 308, 308, 308, 142, 
	141, 143, 309, 312, 309, 312, 312, 312, 
	142, 141, 314, 313, 315, 317, 313, 316, 
	317, 317, 317, 142, 141, 319, 318, 320, 
	322, 318, 321, 322, 322, 322, 142, 141, 
	319, 320, 141, 143, 321, 322, 321, 321, 
	322, 322, 322, 142, 141, 324, 323, 325, 
	322, 323, 321, 322, 322, 322, 142, 141, 
	143, 326, 142, 141, 143, 327, 142, 141, 
	143, 328, 142, 141, 143, 329, 142, 141, 
	143, 330, 330, 142, 141, 143, 330, 331, 
	330, 331, 331, 331, 142, 141, 143, 332, 
	335, 334, 332, 333, 334, 334, 334, 142, 
	141, 143, 336, 339, 338, 336, 337, 338, 
	338, 338, 142, 141, 143, 337, 338, 337, 
	337, 338, 338, 338, 142, 141, 143, 340, 
	341, 338, 340, 337, 338, 338, 338, 142, 
	141, 143, 339, 342, 339, 342, 342, 342, 
	142, 141, 344, 343, 345, 347, 343, 346, 
	347, 347, 347, 142, 141, 349, 348, 350, 
	352, 348, 351, 352, 352, 352, 142, 141, 
	349, 350, 141, 143, 351, 352, 351, 351, 
	352, 352, 352, 142, 141, 354, 353, 355, 
	352, 353, 351, 352, 352, 352, 142, 141, 
	143, 356, 142, 141, 143, 357, 142, 141, 
	143, 358, 142, 141, 143, 359, 142, 141, 
	143, 360, 142, 141, 143, 361, 142, 141, 
	143, 362, 142, 141, 143, 363, 142, 141, 
	143, 364, 364, 142, 141, 143, 364, 365, 
	364, 365, 365, 365, 142, 141, 143, 366, 
	369, 368, 366, 367, 368, 368, 368, 142, 
	141, 143, 370, 373, 372, 370, 371, 372, 
	372, 372, 142, 141, 143, 371, 372, 371, 
	371, 372, 372, 372, 142, 141, 143, 374, 
	375, 372, 374, 371, 372, 372, 372, 142, 
	141, 143, 373, 376, 373, 376, 376, 376, 
	142, 141, 378, 377, 379, 381, 377, 380, 
	381, 381, 381, 142, 141, 383, 382, 384, 
	386, 382, 385, 386, 386, 386, 142, 141, 
	383, 384, 141, 143, 385, 386, 385, 385, 
	386, 386, 386, 142, 141, 388, 387, 389, 
	386, 387, 385, 386, 386, 386, 142, 141, 
	143, 390, 142, 141, 143, 391, 142, 141, 
	143, 392, 392, 142, 141, 143, 392, 393, 
	392, 142, 141, 143, 393, 394, 393, 394, 
	394, 394, 142, 141, 143, 395, 396, 398, 
	395, 397, 398, 398, 398, 142, 141, 143, 
	399, 400, 402, 399, 401, 402, 402, 402, 
	142, 141, 404, 403, 405, 403, 142, 141, 
	404, 403, 405, 406, 403, 406, 406, 406, 
	142, 141, 404, 405, 141, 408, 407, 409, 
	411, 407, 410, 411, 411, 411, 142, 141, 
	404, 412, 405, 414, 412, 413, 414, 414, 
	414, 142, 141, 143, 413, 414, 413, 413, 
	414, 414, 414, 142, 141, 416, 415, 417, 
	414, 415, 413, 414, 414, 414, 142, 141, 
	143, 401, 402, 401, 401, 402, 402, 402, 
	142, 141, 143, 418, 419, 402, 418, 401, 
	402, 402, 402, 142, 1, 421, 420, 106, 
	1, 145, 144, 420, 146, 147, 148, 149, 
	150, 151, 144, 142, 422, 145, 144, 146, 
	147, 148, 149, 150, 151, 144, 142, 0
};

static const short _parse_tester_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 9, 10, 11, 12, 13, 14, 
	15, 16, 17, 18, 19, 20, 21, 22, 
	23, 24, 25, 26, 27, 99, 100, 27, 
	28, 87, 29, 30, 31, 32, 33, 34, 
	33, 34, 35, 36, 37, 38, 39, 40, 
	41, 42, 43, 44, 45, 86, 45, 45, 
	46, 47, 48, 49, 50, 51, 52, 53, 
	54, 84, 85, 53, 54, 84, 85, 55, 
	83, 55, 55, 56, 57, 58, 59, 60, 
	82, 60, 60, 61, 62, 63, 64, 65, 
	66, 67, 68, 69, 70, 71, 72, 73, 
	74, 75, 76, 77, 81, 77, 77, 78, 
	79, 80, 293, 53, 54, 88, 89, 90, 
	91, 92, 93, 94, 95, 96, 97, 98, 
	95, 96, 97, 96, 101, 102, 103, 104, 
	105, 106, 107, 108, 109, 110, 111, 112, 
	113, 114, 115, 116, 117, 294, 118, 294, 
	119, 295, 120, 165, 193, 208, 220, 276, 
	121, 122, 123, 124, 125, 126, 164, 126, 
	127, 128, 129, 130, 163, 131, 131, 132, 
	133, 160, 134, 135, 136, 159, 136, 137, 
	156, 138, 139, 140, 155, 140, 141, 152, 
	142, 143, 144, 151, 145, 294, 146, 147, 
	148, 294, 146, 149, 150, 148, 149, 150, 
	148, 294, 146, 153, 143, 144, 154, 157, 
	139, 140, 158, 161, 135, 136, 162, 166, 
	167, 168, 169, 175, 170, 171, 172, 294, 
	173, 174, 172, 294, 173, 176, 177, 178, 
	179, 180, 181, 182, 183, 184, 185, 186, 
	187, 192, 188, 189, 294, 190, 191, 194, 
	195, 196, 197, 198, 199, 294, 200, 201, 
	199, 294, 200, 201, 202, 205, 203, 204, 
	205, 206, 207, 204, 206, 207, 204, 205, 
	209, 210, 211, 212, 213, 214, 215, 216, 
	218, 219, 215, 216, 218, 219, 294, 217, 
	215, 216, 221, 222, 223, 224, 225, 240, 
	256, 226, 227, 228, 229, 230, 231, 232, 
	233, 234, 231, 232, 233, 234, 231, 234, 
	235, 236, 294, 237, 238, 239, 236, 294, 
	237, 238, 239, 236, 294, 237, 241, 242, 
	243, 244, 245, 246, 247, 248, 249, 250, 
	247, 248, 249, 250, 247, 250, 251, 252, 
	294, 253, 254, 255, 252, 294, 253, 254, 
	255, 252, 294, 253, 257, 258, 259, 260, 
	261, 262, 263, 264, 265, 266, 267, 268, 
	269, 270, 267, 268, 269, 270, 267, 270, 
	271, 272, 294, 273, 274, 275, 272, 294, 
	273, 274, 275, 272, 294, 273, 277, 278, 
	279, 280, 281, 282, 283, 290, 291, 282, 
	283, 290, 291, 284, 294, 285, 286, 287, 
	294, 285, 288, 289, 287, 288, 289, 287, 
	294, 285, 282, 283, 292, 294, 294
};

static const unsigned char _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 39, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 119, 0, 0, 1, 
	0, 0, 0, 0, 0, 0, 0, 81, 
	81, 13, 78, 0, 0, 0, 15, 123, 
	0, 0, 1, 0, 0, 0, 0, 57, 
	0, 0, 1, 41, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 131, 0, 0, 1, 0, 
	0, 0, 0, 17, 17, 0, 0, 0, 
	0, 0, 0, 0, 47, 93, 47, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 55, 0, 66, 
	0, 151, 0, 0, 43, 0, 90, 35, 
	0, 0, 0, 0, 0, 21, 5, 0, 
	0, 0, 0, 0, 5, 23, 0, 0, 
	0, 0, 0, 0, 25, 5, 0, 0, 
	0, 0, 0, 27, 5, 0, 0, 0, 
	0, 0, 29, 5, 0, 99, 0, 0, 
	143, 210, 143, 13, 78, 0, 0, 15, 
	87, 204, 87, 0, 11, 75, 5, 0, 
	11, 72, 5, 0, 11, 69, 5, 0, 
	0, 0, 33, 0, 0, 0, 31, 147, 
	31, 5, 0, 60, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 5, 0, 0, 103, 0, 9, 0, 
	0, 0, 0, 0, 45, 175, 45, 45, 
	0, 135, 0, 0, 0, 0, 0, 81, 
	81, 13, 78, 0, 0, 15, 17, 17, 
	0, 0, 0, 0, 0, 0, 81, 81, 
	13, 78, 0, 0, 0, 15, 127, 0, 
	17, 17, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 81, 13, 
	78, 81, 0, 0, 15, 0, 17, 17, 
	0, 84, 180, 84, 13, 78, 0, 107, 
	0, 0, 15, 19, 155, 19, 0, 0, 
	0, 0, 0, 0, 81, 13, 78, 81, 
	0, 0, 15, 0, 17, 17, 0, 84, 
	192, 84, 13, 78, 0, 115, 0, 0, 
	15, 19, 165, 19, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 81, 13, 
	78, 81, 0, 0, 15, 0, 17, 17, 
	0, 84, 198, 84, 13, 78, 0, 139, 
	0, 0, 15, 19, 170, 19, 0, 0, 
	0, 0, 0, 81, 81, 13, 78, 0, 
	0, 0, 15, 0, 111, 0, 0, 84, 
	186, 84, 13, 78, 0, 0, 15, 19, 
	160, 19, 17, 17, 0, 63, 53
};

static const unsigned char _parse_tester_to_state_actions[] = {
	0, 49, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 49, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 49, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
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
	0, 0, 0, 0, 0, 0, 37, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 96, 0
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
	0, 0, 0, 0, 0, 0, 51, 0
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
	0, 0, 0, 0, 0, 0, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 142, 142, 142, 142, 
	142, 142, 142, 142, 0, 0, 0, 423
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 293;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 294;
static const int parse_tester_en_main = 1;

#line 1284 "NanorexMMPImportExportTest.rl"
	
#line 10448 "NanorexMMPImportExportTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1285 "NanorexMMPImportExportTest.rl"
	
#line 10458 "NanorexMMPImportExportTest.cpp"
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
	case 43:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 10479 "NanorexMMPImportExportTest.cpp"
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
#line 40 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal/*, stringVal2*/); }
	break;
	case 29:
#line 47 "NanorexMMPImportExportTest.rl"
	{ end1(); }
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
#line 1058 "NanorexMMPImportExportTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 38:
#line 1072 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 39:
#line 1075 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 40:
#line 1080 "NanorexMMPImportExportTest.rl"
	{ p--; {stack[top++] = cs; cs = 294; goto _again;} }
	break;
	case 44:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 102 "NanorexMMPImportExportTest.rl"
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
#line 91 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 49:
#line 92 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
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
#line 100 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 57:
#line 102 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
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
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 10793 "NanorexMMPImportExportTest.cpp"
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
	case 41:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 42:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 10822 "NanorexMMPImportExportTest.cpp"
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
#line 1286 "NanorexMMPImportExportTest.rl"
}


