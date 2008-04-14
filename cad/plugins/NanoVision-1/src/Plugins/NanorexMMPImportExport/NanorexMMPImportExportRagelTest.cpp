#line 1 "NanorexMMPImportExportRagelTest.rl"
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


#line 130 "NanorexMMPImportExportRagelTest.rl"



void NanorexMMPImportExportRagelTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	#line 143 "NanorexMMPImportExportRagelTest.rl"
	
#line 134 "NanorexMMPImportExportRagelTest.cpp"
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

#line 144 "NanorexMMPImportExportRagelTest.rl"
	
#line 295 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = atom_decl_line_test_start;
	}
#line 145 "NanorexMMPImportExportRagelTest.rl"
	
#line 301 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 4:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 5:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 6:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 7:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 8:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 9:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 10:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 11:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 12:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 13:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 14:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 438 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _atom_decl_line_test_actions + _atom_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 451 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	_out: {}
	}
#line 146 "NanorexMMPImportExportRagelTest.rl"
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


#line 201 "NanorexMMPImportExportRagelTest.rl"



void NanorexMMPImportExportRagelTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 212 "NanorexMMPImportExportRagelTest.rl"
	
#line 519 "NanorexMMPImportExportRagelTest.cpp"
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

#line 213 "NanorexMMPImportExportRagelTest.rl"
	
#line 592 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = bond_line_test_start;
	}
#line 214 "NanorexMMPImportExportRagelTest.rl"
	
#line 598 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 4:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 5:
#line 196 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 697 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _bond_line_test_actions + _bond_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 710 "NanorexMMPImportExportRagelTest.cpp"
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
#line 196 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 732 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 215 "NanorexMMPImportExportRagelTest.rl"
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


#line 269 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 281 "NanorexMMPImportExportRagelTest.rl"
	
#line 796 "NanorexMMPImportExportRagelTest.cpp"
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

#line 282 "NanorexMMPImportExportRagelTest.rl"
	
#line 891 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = bond_direction_line_test_start;
	}
#line 283 "NanorexMMPImportExportRagelTest.rl"
	
#line 897 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 6:
#line 264 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 996 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _bond_direction_line_test_actions + _bond_direction_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 1013 "NanorexMMPImportExportRagelTest.cpp"
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
#line 264 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 1035 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 284 "NanorexMMPImportExportRagelTest.rl"
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


#line 340 "NanorexMMPImportExportRagelTest.rl"



void NanorexMMPImportExportRagelTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 351 "NanorexMMPImportExportRagelTest.rl"
	
#line 1099 "NanorexMMPImportExportRagelTest.cpp"
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

#line 352 "NanorexMMPImportExportRagelTest.rl"
	
#line 1204 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = info_atom_line_test_start;
	}
#line 353 "NanorexMMPImportExportRagelTest.rl"
	
#line 1210 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 1:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 6:
#line 335 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1323 "NanorexMMPImportExportRagelTest.cpp"
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
#line 335 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1346 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 354 "NanorexMMPImportExportRagelTest.rl"
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


#line 417 "NanorexMMPImportExportRagelTest.rl"



void NanorexMMPImportExportRagelTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 428 "NanorexMMPImportExportRagelTest.rl"
	
#line 1416 "NanorexMMPImportExportRagelTest.cpp"
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

#line 429 "NanorexMMPImportExportRagelTest.rl"
	
#line 1826 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = atom_stmt_test_start;
	}
#line 430 "NanorexMMPImportExportRagelTest.rl"
	
#line 1832 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 410 "NanorexMMPImportExportRagelTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 412 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2007 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _atom_stmt_test_actions + _atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 2024 "NanorexMMPImportExportRagelTest.cpp"
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
#line 410 "NanorexMMPImportExportRagelTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 412 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2050 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 431 "NanorexMMPImportExportRagelTest.rl"
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


#line 561 "NanorexMMPImportExportRagelTest.rl"



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
	
	#line 577 "NanorexMMPImportExportRagelTest.rl"
	
#line 2181 "NanorexMMPImportExportRagelTest.cpp"
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

#line 578 "NanorexMMPImportExportRagelTest.rl"
	
#line 2617 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = multiple_atom_stmt_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 579 "NanorexMMPImportExportRagelTest.rl"
	
#line 2627 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 2648 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 552 "NanorexMMPImportExportRagelTest.rl"
	{ //newAtom(atomId, atomicNum, x, y, z, atomStyle);
// cerr << "calling, p = " << p << endl;
	         {stack[top++] = cs; cs = 142; goto _again;}}
	break;
	case 22:
#line 555 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
	case 25:
#line 544 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 26:
#line 545 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 27:
#line 546 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 28:
#line 547 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 29:
#line 548 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
#line 2837 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 23:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
#line 2858 "NanorexMMPImportExportRagelTest.cpp"
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
#line 555 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
			
		}
	break;
#line 2881 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 580 "NanorexMMPImportExportRagelTest.rl"
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


#line 626 "NanorexMMPImportExportRagelTest.rl"



void NanorexMMPImportExportRagelTest::molLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 637 "NanorexMMPImportExportRagelTest.rl"
	
#line 2938 "NanorexMMPImportExportRagelTest.cpp"
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

#line 638 "NanorexMMPImportExportRagelTest.rl"
	
#line 3049 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = mol_decl_line_test_start;
	}
#line 639 "NanorexMMPImportExportRagelTest.rl"
	
#line 3055 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 1:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 7:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 8:
#line 622 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3172 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _mol_decl_line_test_actions + _mol_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 6:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
#line 3185 "NanorexMMPImportExportRagelTest.cpp"
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
#line 622 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3207 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 640 "NanorexMMPImportExportRagelTest.rl"
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


#line 759 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 772 "NanorexMMPImportExportRagelTest.rl"
	
#line 3326 "NanorexMMPImportExportRagelTest.cpp"
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

#line 773 "NanorexMMPImportExportRagelTest.rl"
	
#line 4376 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = group_lines_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 774 "NanorexMMPImportExportRagelTest.rl"
	
#line 4386 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 4407 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 31:
#line 56 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 32:
#line 60 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 33:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 34:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 35:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 36:
#line 81 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 37:
#line 757 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 246; goto _again;} }
	break;
	case 41:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 42:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{act = 11;}
	break;
	case 43:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 44:
#line 90 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 46:
#line 92 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 47:
#line 93 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 95 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 50:
#line 96 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 97 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 100 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 54:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 55:
#line 1 "NanorexMMPImportExportRagelTest.rl"
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
	case 56:
#line 754 "NanorexMMPImportExportRagelTest.rl"
	{act = 16;}
	break;
	case 57:
#line 745 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 58:
#line 746 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 59:
#line 747 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 60:
#line 748 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 61:
#line 754 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 62:
#line 754 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 63:
#line 1 "NanorexMMPImportExportRagelTest.rl"
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
#line 4749 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _group_lines_test_actions + _group_lines_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 38:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 39:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 4778 "NanorexMMPImportExportRagelTest.cpp"
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
#line 757 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 246; goto _again;} }
	break;
#line 4801 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 775 "NanorexMMPImportExportRagelTest.rl"
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


#line 922 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::uncheckedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 935 "NanorexMMPImportExportRagelTest.rl"
	
#line 4954 "NanorexMMPImportExportRagelTest.cpp"
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

#line 936 "NanorexMMPImportExportRagelTest.rl"
	
#line 5846 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = unchecked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 937 "NanorexMMPImportExportRagelTest.rl"
	
#line 5856 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 5877 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 911 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 39:
#line 914 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 40:
#line 919 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 245; goto _again;} }
	break;
	case 44:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 45:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{act = 11;}
	break;
	case 46:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 47:
#line 90 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 49:
#line 92 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 50:
#line 93 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 95 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 96 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 97 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 100 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 57:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 58:
#line 1 "NanorexMMPImportExportRagelTest.rl"
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
#line 6190 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _unchecked_parse_test_actions + _unchecked_parse_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 41:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 42:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 6219 "NanorexMMPImportExportRagelTest.cpp"
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
#line 938 "NanorexMMPImportExportRagelTest.rl"
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


#line 999 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::checkedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 1012 "NanorexMMPImportExportRagelTest.rl"
	
#line 6295 "NanorexMMPImportExportRagelTest.cpp"
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

#line 1013 "NanorexMMPImportExportRagelTest.rl"
	
#line 7659 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = checked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1014 "NanorexMMPImportExportRagelTest.rl"
	
#line 7669 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 7690 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 16:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 17:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 18:
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed integer"); }
	break;
	case 19:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed atomic number"); }
	break;
	case 20:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed coordinates"); }
	break;
	case 21:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
/*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 22:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed atom-style specification"); }
	break;
	case 23:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 24:
#line 62 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 25:
#line 69 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 26:
#line 70 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-specification - " + stringVal); }
	break;
	case 27:
#line 76 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-target atom id"); }
	break;
	case 28:
#line 80 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 29:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 30:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 31:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 32:
#line 101 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 33:
#line 104 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 34:
#line 106 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting '=' after key"); }
	break;
	case 35:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 36:
#line 17 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed molecule name"); }
	break;
	case 37:
#line 22 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed molecule style"); }
	break;
	case 38:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 39:
#line 27 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* style is optional */ }
	break;
	case 40:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 41:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 42:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 43:
#line 52 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 44:
#line 58 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expected '=' in assignment"); }
	break;
	case 45:
#line 63 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 46:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 47:
#line 28 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 48:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting the 'group (View Data)' statement"); }
	break;
	case 49:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed group-name"); }
	break;
	case 50:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 51:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 52:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{lineStart = p;}
	break;
	case 53:
#line 58 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 54:
#line 59 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 55:
#line 63 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 56:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 57:
#line 68 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 58:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 59:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 60:
#line 79 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 61:
#line 84 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 62:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
	case 63:
#line 93 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 64:
#line 104 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 65:
#line 985 "NanorexMMPImportExportRagelTest.rl"
	{ cerr << "*p=" << *p << endl;
			p--;
			{stack[top++] = cs; cs = 411; goto _again;}
		}
	break;
	case 66:
#line 991 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 411; goto _again;} }
	break;
	case 67:
#line 996 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 411; goto _again;} }
	break;
	case 70:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 71:
#line 110 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 72:
#line 111 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 73:
#line 113 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": returning from group" << endl; {cs = stack[--top]; goto _again;} }}
	break;
	case 74:
#line 114 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 75:
#line 115 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 76:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 77:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 78:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 79:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 80:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 81:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 82:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
	case 83:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{{p = ((te))-1;}{   cerr << lineNum << ": Error : ";
					std::copy(ts, te, std::ostream_iterator<char>(cerr));
					cerr << endl;
				}}
	break;
#line 8106 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _checked_parse_test_actions + _checked_parse_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 68:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
#line 8127 "NanorexMMPImportExportRagelTest.cpp"
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
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed integer"); }
	break;
	case 19:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed atomic number"); }
	break;
	case 20:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed coordinates"); }
	break;
	case 22:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed atom-style specification"); }
	break;
	case 26:
#line 70 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-specification - " + stringVal); }
	break;
	case 27:
#line 76 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-target atom id"); }
	break;
	case 30:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 31:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Invalid bond-direction specification"); }
	break;
	case 33:
#line 104 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 34:
#line 106 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting '=' after key"); }
	break;
	case 35:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 36:
#line 17 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed molecule name"); }
	break;
	case 37:
#line 22 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed molecule style"); }
	break;
	case 41:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed key"); }
	break;
	case 42:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed value"); }
	break;
	case 44:
#line 58 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expected '=' in assignment"); }
	break;
	case 48:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting the 'group (View Data)' statement"); }
	break;
	case 49:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed group-name"); }
	break;
	case 54:
#line 59 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'end1' statement"); }
	break;
	case 57:
#line 68 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Expecting the 'group (Clipboard)' statement"); }
	break;
	case 61:
#line 84 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'info opengroup' key"); }
	break;
	case 62:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{ syntaxError("Badly formed 'info opengroup' value"); }
	break;
#line 8234 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 1015 "NanorexMMPImportExportRagelTest.rl"
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


#line 1095 "NanorexMMPImportExportRagelTest.rl"



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
	
	#line 1182 "NanorexMMPImportExportRagelTest.rl"
	
#line 8365 "NanorexMMPImportExportRagelTest.cpp"
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

#line 1183 "NanorexMMPImportExportRagelTest.rl"
	
#line 9280 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1184 "NanorexMMPImportExportRagelTest.rl"
	
#line 9290 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 9311 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 1067 "NanorexMMPImportExportRagelTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 39:
#line 1081 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 40:
#line 1084 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 41:
#line 1089 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 45:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 46:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{act = 11;}
	break;
	case 47:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 90 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 50:
#line 92 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 93 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 95 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 96 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 97 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 100 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 57:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 58:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 59:
#line 1 "NanorexMMPImportExportRagelTest.rl"
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
#line 9629 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _parse_tester_actions + _parse_tester_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 42:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 43:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 9658 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1185 "NanorexMMPImportExportRagelTest.rl"
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
	
	#line 1292 "NanorexMMPImportExportRagelTest.rl"
	
#line 9786 "NanorexMMPImportExportRagelTest.cpp"
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

#line 1293 "NanorexMMPImportExportRagelTest.rl"
	
#line 10701 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1294 "NanorexMMPImportExportRagelTest.rl"
	
#line 10711 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 10732 "NanorexMMPImportExportRagelTest.cpp"
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
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{++lineNum;}
	break;
	case 2:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 46 "NanorexMMPImportExportRagelTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 11:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 17:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 19:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 23:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 24:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 25:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 26:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 27:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 28:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 29:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 30:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 31:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 32:
#line 56 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 33:
#line 60 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 34:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 35:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 36:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 37:
#line 81 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 38:
#line 1067 "NanorexMMPImportExportRagelTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 39:
#line 1081 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 40:
#line 1084 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 41:
#line 1089 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 306; goto _again;} }
	break;
	case 45:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 46:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{act = 11;}
	break;
	case 47:
#line 89 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 48:
#line 90 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 49:
#line 91 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 50:
#line 92 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 51:
#line 93 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 53:
#line 95 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 96 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 97 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 100 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 57:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 58:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 59:
#line 1 "NanorexMMPImportExportRagelTest.rl"
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
#line 11050 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _parse_tester_actions + _parse_tester_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 22:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 42:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 43:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 11079 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1295 "NanorexMMPImportExportRagelTest.rl"
}


