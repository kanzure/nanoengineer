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
		                               "mol_decl_line_test state machine");
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
		                               "mol_decl_line_test state machine");
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


#line 691 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::csysLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 704 "NanorexMMPImportExportRagelTest.rl"
	
#line 3272 "NanorexMMPImportExportRagelTest.cpp"
static const char _csys_line_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 5, 1, 7, 1, 8, 1, 
	9, 1, 10, 1, 11, 1, 12, 1, 
	13, 1, 14, 1, 15, 1, 16, 1, 
	17, 1, 20, 1, 21, 1, 24, 1, 
	25, 1, 29, 1, 30, 1, 31, 1, 
	32, 1, 33, 1, 34, 1, 35, 1, 
	36, 1, 37, 1, 38, 1, 40, 1, 
	42, 1, 43, 1, 47, 1, 48, 1, 
	50, 1, 65, 1, 66, 2, 0, 39, 
	2, 0, 61, 2, 0, 63, 2, 0, 
	64, 2, 5, 15, 2, 5, 16, 2, 
	5, 17, 2, 6, 7, 2, 8, 30, 
	2, 8, 31, 2, 8, 32, 2, 8, 
	33, 2, 8, 34, 2, 8, 35, 2, 
	8, 36, 2, 8, 37, 2, 8, 38, 
	2, 9, 10, 2, 9, 11, 2, 9, 
	12, 2, 11, 18, 2, 11, 29, 2, 
	45, 27, 2, 48, 49, 3, 0, 19, 
	59, 3, 0, 22, 62, 3, 0, 23, 
	60, 3, 0, 26, 57, 3, 0, 28, 
	58, 3, 0, 39, 53, 3, 0, 41, 
	54, 3, 0, 44, 56, 3, 0, 46, 
	55, 3, 9, 11, 18, 3, 9, 11, 
	29, 3, 20, 0, 61, 3, 51, 0, 
	52, 4, 12, 0, 23, 60, 4, 12, 
	0, 26, 57, 4, 12, 0, 28, 58, 
	4, 12, 0, 41, 54, 4, 12, 0, 
	46, 55, 4, 43, 0, 44, 56, 5, 
	9, 12, 0, 23, 60, 5, 9, 12, 
	0, 26, 57, 5, 9, 12, 0, 28, 
	58, 5, 9, 12, 0, 41, 54, 5, 
	9, 12, 0, 46, 55, 5, 11, 18, 
	0, 19, 59, 6, 9, 11, 18, 0, 
	19, 59
};

static const short _csys_line_test_key_offsets[] = {
	0, 0, 1, 2, 3, 4, 9, 20, 
	34, 48, 53, 61, 63, 71, 76, 84, 
	86, 94, 99, 107, 109, 117, 122, 130, 
	132, 140, 145, 150, 158, 160, 168, 173, 
	178, 186, 188, 196, 201, 209, 211, 219, 
	224, 232, 234, 242, 247, 252, 260, 262, 
	270, 275, 280, 282, 291, 295, 297, 304, 
	313, 317, 319, 326, 335, 339, 341, 348, 
	357, 361, 363, 370, 379, 383, 385, 392, 
	401, 405, 407, 414, 423, 427, 429, 436, 
	445, 449, 451, 458, 467, 471, 473, 480, 
	493, 507, 509, 521, 524, 527, 530, 535, 
	542, 549, 555, 562, 570, 576, 581, 587, 
	596, 600, 608, 614, 623, 627, 635, 641, 
	650, 654, 662, 668, 674, 687, 689, 704, 
	719, 733, 748, 756, 760, 768, 776, 784, 
	788, 796, 804, 812, 816, 824, 832, 840, 
	847, 850, 853, 856, 864, 869, 876, 884, 
	892, 894, 902, 905, 908, 911, 914, 917, 
	920, 923, 926, 929, 934, 941, 948, 955, 
	963, 969, 971, 979, 986, 989, 992, 995, 
	1001, 1013, 1028, 1043, 1049, 1058, 1062, 1071, 
	1077, 1086, 1090, 1099, 1105, 1114, 1118, 1127, 
	1133, 1142, 1146, 1155, 1161, 1167, 1176, 1180, 
	1189, 1195, 1201, 1210, 1214, 1223, 1229, 1238, 
	1242, 1251, 1257, 1266, 1270, 1279, 1285, 1291, 
	1300, 1304, 1313, 1319, 1325, 1327, 1337, 1343, 
	1347, 1355, 1365, 1371, 1375, 1383, 1393, 1399, 
	1403, 1411, 1421, 1427, 1431, 1439, 1449, 1455, 
	1459, 1467, 1477, 1483, 1487, 1495, 1505, 1511, 
	1515, 1523, 1533, 1539, 1543, 1551, 1561, 1567, 
	1571, 1579, 1593, 1608, 1611, 1614, 1617, 1620, 
	1623, 1630, 1637, 1639, 1652, 1664, 1679, 1694, 
	1700, 1714, 1729, 1732, 1735, 1738, 1741, 1747, 
	1753, 1765, 1780, 1795, 1801, 1814, 1816, 1831, 
	1846, 1860, 1875, 1889, 1904, 1907, 1910, 1913, 
	1918, 1926, 1929, 1932, 1935, 1940, 1952, 1967, 
	1982, 1996, 2011, 2023, 2038, 2053, 2055, 2069, 
	2084, 2087, 2090, 2093, 2096, 2101, 2113, 2128, 
	2143, 2157, 2172, 2184, 2199, 2214, 2216, 2230, 
	2245, 2248, 2251, 2254, 2257, 2260, 2263, 2266, 
	2269, 2274, 2286, 2301, 2316, 2330, 2345, 2357, 
	2372, 2387, 2389, 2403, 2418, 2421, 2424, 2429, 
	2435, 2447, 2462, 2477, 2483, 2496, 2498, 2513, 
	2528, 2542, 2557, 2571, 2586, 2588, 2588, 2601
};

static const char _csys_line_test_trans_keys[] = {
	99, 115, 121, 115, 9, 32, 40, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 41, 95, 
	11, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, 9, 32, 41, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	9, 32, 40, 11, 13, 9, 32, 43, 
	45, 11, 13, 48, 57, 48, 57, 9, 
	32, 44, 46, 11, 13, 48, 57, 9, 
	32, 44, 11, 13, 9, 32, 43, 45, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	44, 46, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 9, 32, 43, 45, 11, 
	13, 48, 57, 48, 57, 9, 32, 44, 
	46, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 9, 32, 43, 45, 11, 13, 
	48, 57, 48, 57, 9, 32, 41, 46, 
	11, 13, 48, 57, 9, 32, 41, 11, 
	13, 9, 32, 40, 11, 13, 9, 32, 
	43, 45, 11, 13, 48, 57, 48, 57, 
	9, 32, 41, 46, 11, 13, 48, 57, 
	9, 32, 41, 11, 13, 9, 32, 40, 
	11, 13, 9, 32, 43, 45, 11, 13, 
	48, 57, 48, 57, 9, 32, 44, 46, 
	11, 13, 48, 57, 9, 32, 44, 11, 
	13, 9, 32, 43, 45, 11, 13, 48, 
	57, 48, 57, 9, 32, 44, 46, 11, 
	13, 48, 57, 9, 32, 44, 11, 13, 
	9, 32, 43, 45, 11, 13, 48, 57, 
	48, 57, 9, 32, 41, 46, 11, 13, 
	48, 57, 9, 32, 41, 11, 13, 9, 
	32, 40, 11, 13, 9, 32, 43, 45, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	41, 46, 11, 13, 48, 57, 9, 32, 
	41, 11, 13, 10, 32, 35, 9, 13, 
	-1, 10, 9, 32, 41, 69, 101, 11, 
	13, 48, 57, 43, 45, 48, 57, 48, 
	57, 9, 32, 41, 11, 13, 48, 57, 
	9, 32, 41, 69, 101, 11, 13, 48, 
	57, 43, 45, 48, 57, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	44, 69, 101, 11, 13, 48, 57, 43, 
	45, 48, 57, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 69, 
	101, 11, 13, 48, 57, 43, 45, 48, 
	57, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 41, 69, 101, 11, 
	13, 48, 57, 43, 45, 48, 57, 48, 
	57, 9, 32, 41, 11, 13, 48, 57, 
	9, 32, 41, 69, 101, 11, 13, 48, 
	57, 43, 45, 48, 57, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	44, 69, 101, 11, 13, 48, 57, 43, 
	45, 48, 57, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 44, 69, 
	101, 11, 13, 48, 57, 43, 45, 48, 
	57, 48, 57, 9, 32, 44, 11, 13, 
	48, 57, 9, 32, 44, 69, 101, 11, 
	13, 48, 57, 43, 45, 48, 57, 48, 
	57, 9, 32, 44, 11, 13, 48, 57, 
	9, 32, 95, 11, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 9, 32, 41, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	97, 98, 99, 101, 103, 105, 109, 9, 
	13, -1, 10, 116, -1, 10, 111, -1, 
	10, 109, -1, 10, 32, 9, 13, -1, 
	10, 32, 9, 13, 48, 57, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 44, 9, 
	13, -1, 10, 32, 43, 45, 9, 13, 
	48, 57, -1, 10, 48, 57, -1, 10, 
	32, 41, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 35, 
	9, 13, -1, 10, 32, 35, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 111, -1, 10, 110, -1, 10, 100, 
	-1, 10, 95, 97, 99, 103, 49, 51, 
	-1, 10, 32, 9, 13, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, -1, 10, 
	32, 35, 9, 13, 48, 57, -1, 10, 
	100, -1, 10, 105, -1, 10, 114, -1, 
	10, 101, -1, 10, 99, -1, 10, 116, 
	-1, 10, 105, -1, 10, 111, -1, 10, 
	110, -1, 10, 32, 9, 13, -1, 10, 
	32, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 32, 35, 9, 
	13, -1, 10, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 115, -1, 10, 121, 
	-1, 10, 115, -1, 10, 32, 40, 9, 
	13, -1, 10, 32, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 40, 9, 
	13, -1, 10, 32, 43, 45, 9, 13, 
	48, 57, -1, 10, 48, 57, -1, 10, 
	32, 44, 46, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, -1, 10, 32, 
	43, 45, 9, 13, 48, 57, -1, 10, 
	48, 57, -1, 10, 32, 44, 46, 9, 
	13, 48, 57, -1, 10, 32, 44, 9, 
	13, -1, 10, 32, 43, 45, 9, 13, 
	48, 57, -1, 10, 48, 57, -1, 10, 
	32, 44, 46, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, -1, 10, 32, 
	43, 45, 9, 13, 48, 57, -1, 10, 
	48, 57, -1, 10, 32, 41, 46, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 40, 9, 13, -1, 
	10, 32, 43, 45, 9, 13, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	46, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, -1, 10, 32, 40, 9, 
	13, -1, 10, 32, 43, 45, 9, 13, 
	48, 57, -1, 10, 48, 57, -1, 10, 
	32, 44, 46, 9, 13, 48, 57, -1, 
	10, 32, 44, 9, 13, -1, 10, 32, 
	43, 45, 9, 13, 48, 57, -1, 10, 
	48, 57, -1, 10, 32, 44, 46, 9, 
	13, 48, 57, -1, 10, 32, 44, 9, 
	13, -1, 10, 32, 43, 45, 9, 13, 
	48, 57, -1, 10, 48, 57, -1, 10, 
	32, 41, 46, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 46, 9, 13, 48, 
	57, -1, 10, 32, 41, 9, 13, -1, 
	10, 32, 35, 9, 13, -1, 10, -1, 
	10, 32, 41, 69, 101, 9, 13, 48, 
	57, -1, 10, 43, 45, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 69, 
	101, 9, 13, 48, 57, -1, 10, 43, 
	45, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 44, 69, 101, 9, 13, 48, 
	57, -1, 10, 43, 45, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 44, 69, 
	101, 9, 13, 48, 57, -1, 10, 43, 
	45, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 41, 69, 101, 9, 13, 48, 
	57, -1, 10, 43, 45, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 69, 
	101, 9, 13, 48, 57, -1, 10, 43, 
	45, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 44, 69, 101, 9, 13, 48, 
	57, -1, 10, 43, 45, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 44, 69, 
	101, 9, 13, 48, 57, -1, 10, 43, 
	45, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 9, 13, 48, 57, -1, 
	10, 32, 44, 69, 101, 9, 13, 48, 
	57, -1, 10, 43, 45, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 9, 
	13, 48, 57, -1, 10, 32, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 103, -1, 10, 114, -1, 10, 
	111, -1, 10, 117, -1, 10, 112, -1, 
	10, 32, 35, 40, 9, 13, -1, 10, 
	32, 35, 40, 9, 13, -1, 10, -1, 
	10, 32, 41, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 9, 13, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 114, -1, 10, 111, -1, 
	10, 117, -1, 10, 112, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 40, 9, 
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
	97, 122, -1, 10, -1, 10, 32, 35, 
	97, 98, 99, 101, 103, 105, 109, 9, 
	13, -1, 10, 32, 97, 98, 99, 101, 
	103, 105, 109, 9, 13, 0
};

static const char _csys_line_test_single_lengths[] = {
	0, 1, 1, 1, 1, 3, 3, 4, 
	4, 3, 4, 0, 4, 3, 4, 0, 
	4, 3, 4, 0, 4, 3, 4, 0, 
	4, 3, 3, 4, 0, 4, 3, 3, 
	4, 0, 4, 3, 4, 0, 4, 3, 
	4, 0, 4, 3, 3, 4, 0, 4, 
	3, 3, 2, 5, 2, 0, 3, 5, 
	2, 0, 3, 5, 2, 0, 3, 5, 
	2, 0, 3, 5, 2, 0, 3, 5, 
	2, 0, 3, 5, 2, 0, 3, 5, 
	2, 0, 3, 5, 2, 0, 3, 3, 
	4, 2, 10, 3, 3, 3, 3, 3, 
	3, 4, 3, 4, 4, 3, 4, 5, 
	2, 4, 4, 5, 2, 4, 4, 5, 
	2, 4, 4, 4, 5, 2, 5, 5, 
	4, 5, 4, 2, 4, 4, 4, 2, 
	4, 4, 4, 2, 4, 4, 4, 3, 
	3, 3, 3, 6, 3, 3, 4, 4, 
	2, 4, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 4, 
	4, 2, 4, 3, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 4, 
	5, 2, 5, 4, 5, 2, 5, 4, 
	5, 2, 5, 4, 4, 5, 2, 5, 
	4, 4, 5, 2, 5, 4, 5, 2, 
	5, 4, 5, 2, 5, 4, 4, 5, 
	2, 5, 4, 4, 2, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 4, 5, 3, 3, 3, 3, 3, 
	5, 5, 2, 5, 4, 5, 5, 4, 
	4, 5, 3, 3, 3, 3, 4, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 3, 3, 3, 3, 
	6, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 2, 0, 11, 10
};

static const char _csys_line_test_range_lengths[] = {
	0, 0, 0, 0, 0, 1, 4, 5, 
	5, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 2, 1, 2, 1, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 1, 0, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 5, 
	5, 0, 1, 0, 0, 0, 1, 2, 
	2, 1, 2, 2, 1, 1, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 1, 4, 0, 5, 5, 
	5, 5, 2, 1, 2, 2, 2, 1, 
	2, 2, 2, 1, 2, 2, 2, 2, 
	0, 0, 0, 1, 1, 2, 2, 2, 
	0, 2, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 2, 2, 2, 2, 
	1, 0, 2, 2, 0, 0, 0, 1, 
	4, 5, 5, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 1, 2, 
	1, 2, 1, 1, 0, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 5, 5, 0, 0, 0, 0, 0, 
	1, 1, 0, 4, 4, 5, 5, 1, 
	5, 5, 0, 0, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 0, 1, 
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

static const short _csys_line_test_index_offsets[] = {
	0, 0, 2, 4, 6, 8, 13, 21, 
	31, 41, 46, 53, 55, 62, 67, 74, 
	76, 83, 88, 95, 97, 104, 109, 116, 
	118, 125, 130, 135, 142, 144, 151, 156, 
	161, 168, 170, 177, 182, 189, 191, 198, 
	203, 210, 212, 219, 224, 229, 236, 238, 
	245, 250, 255, 258, 266, 270, 272, 278, 
	286, 290, 292, 298, 306, 310, 312, 318, 
	326, 330, 332, 338, 346, 350, 352, 358, 
	366, 370, 372, 378, 386, 390, 392, 398, 
	406, 410, 412, 418, 426, 430, 432, 438, 
	447, 457, 460, 472, 476, 480, 484, 489, 
	495, 501, 507, 513, 520, 526, 531, 537, 
	545, 549, 556, 562, 570, 574, 581, 587, 
	595, 599, 606, 612, 618, 628, 631, 642, 
	653, 663, 674, 681, 685, 692, 699, 706, 
	710, 717, 724, 731, 735, 742, 749, 756, 
	762, 766, 770, 774, 782, 787, 793, 800, 
	807, 810, 817, 821, 825, 829, 833, 837, 
	841, 845, 849, 853, 858, 864, 870, 876, 
	883, 889, 892, 899, 905, 909, 913, 917, 
	923, 932, 943, 954, 960, 968, 972, 980, 
	986, 994, 998, 1006, 1012, 1020, 1024, 1032, 
	1038, 1046, 1050, 1058, 1064, 1070, 1078, 1082, 
	1090, 1096, 1102, 1110, 1114, 1122, 1128, 1136, 
	1140, 1148, 1154, 1162, 1166, 1174, 1180, 1186, 
	1194, 1198, 1206, 1212, 1218, 1221, 1230, 1236, 
	1240, 1247, 1256, 1262, 1266, 1273, 1282, 1288, 
	1292, 1299, 1308, 1314, 1318, 1325, 1334, 1340, 
	1344, 1351, 1360, 1366, 1370, 1377, 1386, 1392, 
	1396, 1403, 1412, 1418, 1422, 1429, 1438, 1444, 
	1448, 1455, 1465, 1476, 1480, 1484, 1488, 1492, 
	1496, 1503, 1510, 1513, 1523, 1532, 1543, 1554, 
	1560, 1570, 1581, 1585, 1589, 1593, 1597, 1603, 
	1609, 1618, 1629, 1640, 1646, 1656, 1659, 1670, 
	1681, 1691, 1702, 1712, 1723, 1727, 1731, 1735, 
	1740, 1748, 1752, 1756, 1760, 1765, 1774, 1785, 
	1796, 1806, 1817, 1826, 1837, 1848, 1851, 1861, 
	1872, 1876, 1880, 1884, 1888, 1893, 1902, 1913, 
	1924, 1934, 1945, 1954, 1965, 1976, 1979, 1989, 
	2000, 2004, 2008, 2012, 2016, 2020, 2024, 2028, 
	2032, 2037, 2046, 2057, 2068, 2078, 2089, 2098, 
	2109, 2120, 2123, 2133, 2144, 2148, 2152, 2157, 
	2163, 2172, 2183, 2194, 2200, 2210, 2213, 2224, 
	2235, 2245, 2256, 2266, 2277, 2280, 2281, 2294
};

static const short _csys_line_test_indicies[] = {
	1, 0, 2, 0, 3, 0, 4, 0, 
	4, 4, 5, 4, 0, 5, 5, 6, 
	5, 6, 6, 6, 0, 7, 7, 8, 
	10, 7, 9, 10, 10, 10, 0, 11, 
	11, 12, 14, 11, 13, 14, 14, 14, 
	0, 15, 15, 16, 15, 0, 16, 16, 
	17, 17, 16, 18, 0, 19, 0, 20, 
	20, 21, 22, 20, 19, 0, 23, 23, 
	24, 23, 0, 25, 25, 26, 26, 25, 
	27, 0, 28, 0, 29, 29, 30, 31, 
	29, 28, 0, 32, 32, 33, 32, 0, 
	34, 34, 35, 35, 34, 36, 0, 37, 
	0, 38, 38, 39, 40, 38, 37, 0, 
	41, 41, 42, 41, 0, 43, 43, 44, 
	44, 43, 45, 0, 46, 0, 47, 47, 
	48, 49, 47, 46, 0, 50, 50, 51, 
	50, 0, 52, 52, 53, 52, 0, 53, 
	53, 54, 54, 53, 55, 0, 56, 0, 
	57, 57, 58, 59, 57, 56, 0, 60, 
	60, 61, 60, 0, 62, 62, 63, 62, 
	0, 63, 63, 64, 64, 63, 65, 0, 
	66, 0, 67, 67, 68, 69, 67, 66, 
	0, 70, 70, 71, 70, 0, 72, 72, 
	73, 73, 72, 74, 0, 75, 0, 76, 
	76, 77, 78, 76, 75, 0, 79, 79, 
	80, 79, 0, 81, 81, 82, 82, 81, 
	83, 0, 84, 0, 85, 85, 86, 87, 
	85, 84, 0, 88, 88, 89, 88, 0, 
	90, 90, 91, 90, 0, 91, 91, 92, 
	92, 91, 93, 0, 94, 0, 95, 95, 
	96, 97, 95, 94, 0, 98, 98, 99, 
	98, 0, 101, 100, 102, 100, 0, 0, 
	101, 102, 95, 95, 96, 103, 103, 95, 
	97, 0, 104, 104, 105, 0, 105, 0, 
	95, 95, 96, 95, 105, 0, 85, 85, 
	86, 106, 106, 85, 87, 0, 107, 107, 
	108, 0, 108, 0, 85, 85, 86, 85, 
	108, 0, 76, 76, 77, 109, 109, 76, 
	78, 0, 110, 110, 111, 0, 111, 0, 
	76, 76, 77, 76, 111, 0, 67, 67, 
	68, 112, 112, 67, 69, 0, 113, 113, 
	114, 0, 114, 0, 67, 67, 68, 67, 
	114, 0, 57, 57, 58, 115, 115, 57, 
	59, 0, 116, 116, 117, 0, 117, 0, 
	57, 57, 58, 57, 117, 0, 47, 47, 
	48, 118, 118, 47, 49, 0, 119, 119, 
	120, 0, 120, 0, 47, 47, 48, 47, 
	120, 0, 38, 38, 39, 121, 121, 38, 
	40, 0, 122, 122, 123, 0, 123, 0, 
	38, 38, 39, 38, 123, 0, 29, 29, 
	30, 124, 124, 29, 31, 0, 125, 125, 
	126, 0, 126, 0, 29, 29, 30, 29, 
	126, 0, 20, 20, 21, 127, 127, 20, 
	22, 0, 128, 128, 129, 0, 129, 0, 
	20, 20, 21, 20, 129, 0, 13, 13, 
	14, 13, 13, 14, 14, 14, 0, 130, 
	130, 131, 14, 130, 13, 14, 14, 14, 
	0, 132, 134, 133, 132, 136, 135, 137, 
	138, 139, 140, 141, 142, 143, 135, 133, 
	132, 134, 144, 133, 132, 134, 145, 133, 
	132, 134, 146, 133, 132, 134, 147, 147, 
	133, 132, 134, 147, 147, 148, 133, 132, 
	134, 149, 149, 150, 133, 132, 134, 151, 
	152, 151, 133, 132, 134, 152, 152, 153, 
	133, 132, 134, 154, 155, 154, 156, 133, 
	132, 134, 154, 155, 154, 133, 132, 134, 
	157, 157, 133, 132, 134, 158, 159, 158, 
	133, 132, 134, 159, 160, 161, 159, 162, 
	133, 132, 134, 162, 133, 132, 134, 163, 
	164, 163, 165, 133, 132, 134, 163, 164, 
	163, 133, 132, 134, 166, 167, 168, 166, 
	169, 133, 132, 134, 169, 133, 132, 134, 
	170, 171, 170, 172, 133, 132, 134, 170, 
	171, 170, 133, 132, 134, 173, 174, 175, 
	173, 176, 133, 132, 134, 176, 133, 132, 
	134, 177, 178, 177, 179, 133, 132, 134, 
	177, 178, 177, 133, 132, 181, 180, 182, 
	180, 133, 132, 181, 180, 182, 183, 180, 
	183, 183, 183, 133, 132, 181, 182, 132, 
	185, 184, 186, 188, 184, 187, 188, 188, 
	188, 133, 132, 181, 189, 182, 191, 189, 
	190, 191, 191, 191, 133, 132, 134, 190, 
	191, 190, 190, 191, 191, 191, 133, 132, 
	193, 192, 194, 191, 192, 190, 191, 191, 
	191, 133, 132, 134, 177, 178, 177, 179, 
	133, 132, 134, 195, 133, 132, 134, 196, 
	197, 196, 198, 133, 132, 134, 196, 197, 
	196, 198, 133, 132, 134, 170, 171, 170, 
	172, 133, 132, 134, 199, 133, 132, 134, 
	200, 201, 200, 202, 133, 132, 134, 200, 
	201, 200, 202, 133, 132, 134, 163, 164, 
	163, 165, 133, 132, 134, 203, 133, 132, 
	134, 204, 205, 204, 206, 133, 132, 134, 
	204, 205, 204, 206, 133, 132, 134, 154, 
	155, 154, 156, 133, 132, 134, 149, 149, 
	150, 133, 132, 134, 207, 133, 132, 134, 
	208, 133, 132, 134, 209, 133, 132, 134, 
	211, 210, 210, 210, 210, 133, 132, 134, 
	212, 212, 133, 132, 134, 212, 212, 213, 
	133, 132, 215, 214, 216, 214, 217, 133, 
	132, 219, 218, 220, 218, 213, 133, 132, 
	219, 220, 132, 215, 214, 216, 214, 217, 
	133, 132, 134, 221, 133, 132, 134, 222, 
	133, 132, 134, 223, 133, 132, 134, 224, 
	133, 132, 134, 225, 133, 132, 134, 226, 
	133, 132, 134, 227, 133, 132, 134, 228, 
	133, 132, 134, 229, 133, 132, 134, 230, 
	230, 133, 132, 134, 230, 230, 231, 133, 
	132, 134, 232, 232, 233, 133, 132, 134, 
	232, 232, 234, 133, 132, 236, 235, 237, 
	235, 238, 133, 132, 236, 235, 237, 235, 
	133, 132, 236, 237, 132, 236, 235, 237, 
	235, 238, 133, 132, 134, 232, 232, 233, 
	133, 132, 134, 239, 133, 132, 134, 240, 
	133, 132, 134, 241, 133, 132, 134, 241, 
	242, 241, 133, 132, 134, 242, 243, 242, 
	243, 243, 243, 133, 132, 134, 244, 245, 
	247, 244, 246, 247, 247, 247, 133, 132, 
	134, 248, 249, 251, 248, 250, 251, 251, 
	251, 133, 132, 134, 252, 253, 252, 133, 
	132, 134, 253, 254, 254, 253, 255, 133, 
	132, 134, 256, 133, 132, 134, 257, 258, 
	259, 257, 256, 133, 132, 134, 260, 261, 
	260, 133, 132, 134, 262, 263, 263, 262, 
	264, 133, 132, 134, 265, 133, 132, 134, 
	266, 267, 268, 266, 265, 133, 132, 134, 
	269, 270, 269, 133, 132, 134, 271, 272, 
	272, 271, 273, 133, 132, 134, 274, 133, 
	132, 134, 275, 276, 277, 275, 274, 133, 
	132, 134, 278, 279, 278, 133, 132, 134, 
	280, 281, 281, 280, 282, 133, 132, 134, 
	283, 133, 132, 134, 284, 285, 286, 284, 
	283, 133, 132, 134, 287, 288, 287, 133, 
	132, 134, 289, 290, 289, 133, 132, 134, 
	290, 291, 291, 290, 292, 133, 132, 134, 
	293, 133, 132, 134, 294, 295, 296, 294, 
	293, 133, 132, 134, 297, 298, 297, 133, 
	132, 134, 299, 300, 299, 133, 132, 134, 
	300, 301, 301, 300, 302, 133, 132, 134, 
	303, 133, 132, 134, 304, 305, 306, 304, 
	303, 133, 132, 134, 307, 308, 307, 133, 
	132, 134, 309, 310, 310, 309, 311, 133, 
	132, 134, 312, 133, 132, 134, 313, 314, 
	315, 313, 312, 133, 132, 134, 316, 317, 
	316, 133, 132, 134, 318, 319, 319, 318, 
	320, 133, 132, 134, 321, 133, 132, 134, 
	322, 323, 324, 322, 321, 133, 132, 134, 
	325, 326, 325, 133, 132, 134, 327, 328, 
	327, 133, 132, 134, 328, 329, 329, 328, 
	330, 133, 132, 134, 331, 133, 132, 134, 
	332, 333, 334, 332, 331, 133, 132, 134, 
	335, 336, 335, 133, 132, 338, 337, 339, 
	337, 133, 132, 338, 339, 132, 134, 332, 
	333, 340, 340, 332, 334, 133, 132, 134, 
	341, 341, 342, 133, 132, 134, 342, 133, 
	132, 134, 332, 333, 332, 342, 133, 132, 
	134, 322, 323, 343, 343, 322, 324, 133, 
	132, 134, 344, 344, 345, 133, 132, 134, 
	345, 133, 132, 134, 322, 323, 322, 345, 
	133, 132, 134, 313, 314, 346, 346, 313, 
	315, 133, 132, 134, 347, 347, 348, 133, 
	132, 134, 348, 133, 132, 134, 313, 314, 
	313, 348, 133, 132, 134, 304, 305, 349, 
	349, 304, 306, 133, 132, 134, 350, 350, 
	351, 133, 132, 134, 351, 133, 132, 134, 
	304, 305, 304, 351, 133, 132, 134, 294, 
	295, 352, 352, 294, 296, 133, 132, 134, 
	353, 353, 354, 133, 132, 134, 354, 133, 
	132, 134, 294, 295, 294, 354, 133, 132, 
	134, 284, 285, 355, 355, 284, 286, 133, 
	132, 134, 356, 356, 357, 133, 132, 134, 
	357, 133, 132, 134, 284, 285, 284, 357, 
	133, 132, 134, 275, 276, 358, 358, 275, 
	277, 133, 132, 134, 359, 359, 360, 133, 
	132, 134, 360, 133, 132, 134, 275, 276, 
	275, 360, 133, 132, 134, 266, 267, 361, 
	361, 266, 268, 133, 132, 134, 362, 362, 
	363, 133, 132, 134, 363, 133, 132, 134, 
	266, 267, 266, 363, 133, 132, 134, 257, 
	258, 364, 364, 257, 259, 133, 132, 134, 
	365, 365, 366, 133, 132, 134, 366, 133, 
	132, 134, 257, 258, 257, 366, 133, 132, 
	134, 250, 251, 250, 250, 251, 251, 251, 
	133, 132, 134, 367, 368, 251, 367, 250, 
	251, 251, 251, 133, 132, 134, 369, 133, 
	132, 134, 370, 133, 132, 134, 371, 133, 
	132, 134, 372, 133, 132, 134, 373, 133, 
	132, 375, 374, 376, 377, 374, 133, 132, 
	379, 378, 380, 381, 378, 133, 132, 379, 
	380, 132, 134, 382, 383, 384, 382, 384, 
	384, 384, 133, 132, 134, 382, 384, 382, 
	384, 384, 384, 133, 132, 134, 385, 386, 
	388, 385, 387, 388, 388, 388, 133, 132, 
	134, 389, 383, 391, 389, 390, 391, 391, 
	391, 133, 132, 379, 383, 380, 383, 133, 
	132, 134, 390, 391, 390, 390, 391, 391, 
	391, 133, 132, 134, 392, 393, 391, 392, 
	390, 391, 391, 391, 133, 132, 134, 394, 
	133, 132, 134, 395, 133, 132, 134, 396, 
	133, 132, 134, 397, 133, 132, 134, 398, 
	399, 398, 133, 132, 134, 400, 401, 400, 
	133, 132, 134, 401, 402, 401, 402, 402, 
	402, 133, 132, 134, 403, 404, 406, 403, 
	405, 406, 406, 406, 133, 132, 134, 407, 
	408, 410, 407, 409, 410, 410, 410, 133, 
	132, 412, 411, 413, 411, 133, 132, 412, 
	411, 413, 414, 411, 414, 414, 414, 133, 
	132, 412, 413, 132, 416, 415, 417, 419, 
	415, 418, 419, 419, 419, 133, 132, 412, 
	420, 413, 422, 420, 421, 422, 422, 422, 
	133, 132, 134, 421, 422, 421, 421, 422, 
	422, 422, 133, 132, 424, 423, 425, 422, 
	423, 421, 422, 422, 422, 133, 132, 134, 
	409, 410, 409, 409, 410, 410, 410, 133, 
	132, 134, 426, 427, 410, 426, 409, 410, 
	410, 410, 133, 132, 134, 428, 133, 132, 
	134, 429, 133, 132, 134, 430, 133, 132, 
	134, 431, 431, 133, 132, 134, 431, 432, 
	433, 434, 431, 133, 132, 134, 435, 133, 
	132, 134, 436, 133, 132, 134, 437, 133, 
	132, 134, 438, 438, 133, 132, 134, 438, 
	439, 438, 439, 439, 439, 133, 132, 134, 
	440, 443, 442, 440, 441, 442, 442, 442, 
	133, 132, 134, 444, 447, 446, 444, 445, 
	446, 446, 446, 133, 132, 134, 445, 446, 
	445, 445, 446, 446, 446, 133, 132, 134, 
	448, 449, 446, 448, 445, 446, 446, 446, 
	133, 132, 134, 447, 450, 447, 450, 450, 
	450, 133, 132, 452, 451, 453, 455, 451, 
	454, 455, 455, 455, 133, 132, 457, 456, 
	458, 460, 456, 459, 460, 460, 460, 133, 
	132, 457, 458, 132, 134, 459, 460, 459, 
	459, 460, 460, 460, 133, 132, 462, 461, 
	463, 460, 461, 459, 460, 460, 460, 133, 
	132, 134, 464, 133, 132, 134, 465, 133, 
	132, 134, 466, 133, 132, 134, 467, 133, 
	132, 134, 468, 468, 133, 132, 134, 468, 
	469, 468, 469, 469, 469, 133, 132, 134, 
	470, 473, 472, 470, 471, 472, 472, 472, 
	133, 132, 134, 474, 477, 476, 474, 475, 
	476, 476, 476, 133, 132, 134, 475, 476, 
	475, 475, 476, 476, 476, 133, 132, 134, 
	478, 479, 476, 478, 475, 476, 476, 476, 
	133, 132, 134, 477, 480, 477, 480, 480, 
	480, 133, 132, 482, 481, 483, 485, 481, 
	484, 485, 485, 485, 133, 132, 487, 486, 
	488, 490, 486, 489, 490, 490, 490, 133, 
	132, 487, 488, 132, 134, 489, 490, 489, 
	489, 490, 490, 490, 133, 132, 492, 491, 
	493, 490, 491, 489, 490, 490, 490, 133, 
	132, 134, 494, 133, 132, 134, 495, 133, 
	132, 134, 496, 133, 132, 134, 497, 133, 
	132, 134, 498, 133, 132, 134, 499, 133, 
	132, 134, 500, 133, 132, 134, 501, 133, 
	132, 134, 502, 502, 133, 132, 134, 502, 
	503, 502, 503, 503, 503, 133, 132, 134, 
	504, 507, 506, 504, 505, 506, 506, 506, 
	133, 132, 134, 508, 511, 510, 508, 509, 
	510, 510, 510, 133, 132, 134, 509, 510, 
	509, 509, 510, 510, 510, 133, 132, 134, 
	512, 513, 510, 512, 509, 510, 510, 510, 
	133, 132, 134, 511, 514, 511, 514, 514, 
	514, 133, 132, 516, 515, 517, 519, 515, 
	518, 519, 519, 519, 133, 132, 521, 520, 
	522, 524, 520, 523, 524, 524, 524, 133, 
	132, 521, 522, 132, 134, 523, 524, 523, 
	523, 524, 524, 524, 133, 132, 526, 525, 
	527, 524, 525, 523, 524, 524, 524, 133, 
	132, 134, 528, 133, 132, 134, 529, 133, 
	132, 134, 530, 530, 133, 132, 134, 530, 
	531, 530, 133, 132, 134, 531, 532, 531, 
	532, 532, 532, 133, 132, 134, 533, 534, 
	536, 533, 535, 536, 536, 536, 133, 132, 
	134, 537, 538, 540, 537, 539, 540, 540, 
	540, 133, 132, 542, 541, 543, 541, 133, 
	132, 542, 541, 543, 544, 541, 544, 544, 
	544, 133, 132, 542, 543, 132, 546, 545, 
	547, 549, 545, 548, 549, 549, 549, 133, 
	132, 542, 550, 543, 552, 550, 551, 552, 
	552, 552, 133, 132, 134, 551, 552, 551, 
	551, 552, 552, 552, 133, 132, 554, 553, 
	555, 552, 553, 551, 552, 552, 552, 133, 
	132, 134, 539, 540, 539, 539, 540, 540, 
	540, 133, 132, 134, 556, 557, 540, 556, 
	539, 540, 540, 540, 133, 559, 560, 558, 
	0, 559, 136, 135, 558, 137, 138, 139, 
	140, 141, 142, 143, 135, 133, 561, 136, 
	135, 137, 138, 139, 140, 141, 142, 143, 
	135, 133, 0
};

static const short _csys_line_test_trans_targs_wi[] = {
	0, 2, 3, 4, 5, 6, 7, 8, 
	9, 87, 88, 8, 9, 87, 88, 9, 
	10, 11, 12, 12, 13, 14, 83, 13, 
	14, 14, 15, 16, 16, 17, 18, 79, 
	17, 18, 18, 19, 20, 20, 21, 22, 
	75, 21, 22, 22, 23, 24, 24, 25, 
	26, 71, 25, 26, 26, 27, 28, 29, 
	29, 30, 31, 67, 30, 31, 31, 32, 
	33, 34, 34, 35, 36, 63, 35, 36, 
	36, 37, 38, 38, 39, 40, 59, 39, 
	40, 40, 41, 42, 42, 43, 44, 55, 
	43, 44, 44, 45, 46, 47, 47, 48, 
	49, 51, 48, 49, 49, 357, 50, 52, 
	53, 54, 56, 57, 58, 60, 61, 62, 
	64, 65, 66, 68, 69, 70, 72, 73, 
	74, 76, 77, 78, 80, 81, 82, 84, 
	85, 86, 8, 9, 358, 89, 358, 90, 
	359, 91, 136, 164, 251, 266, 284, 340, 
	92, 93, 94, 95, 96, 97, 135, 97, 
	98, 99, 100, 101, 134, 102, 102, 103, 
	104, 131, 105, 106, 107, 130, 107, 108, 
	127, 109, 110, 111, 126, 111, 112, 123, 
	113, 114, 115, 122, 116, 358, 117, 118, 
	119, 358, 117, 120, 121, 119, 120, 121, 
	119, 358, 117, 124, 114, 115, 125, 128, 
	110, 111, 129, 132, 106, 107, 133, 137, 
	138, 139, 140, 146, 141, 142, 143, 358, 
	144, 145, 143, 358, 144, 147, 148, 149, 
	150, 151, 152, 153, 154, 155, 156, 157, 
	158, 163, 159, 160, 358, 161, 162, 165, 
	166, 167, 168, 169, 170, 171, 249, 250, 
	170, 171, 249, 250, 171, 172, 173, 174, 
	174, 175, 176, 245, 175, 176, 176, 177, 
	178, 178, 179, 180, 241, 179, 180, 180, 
	181, 182, 182, 183, 184, 237, 183, 184, 
	184, 185, 186, 186, 187, 188, 233, 187, 
	188, 188, 189, 190, 191, 191, 192, 193, 
	229, 192, 193, 193, 194, 195, 196, 196, 
	197, 198, 225, 197, 198, 198, 199, 200, 
	200, 201, 202, 221, 201, 202, 202, 203, 
	204, 204, 205, 206, 217, 205, 206, 206, 
	207, 208, 209, 209, 210, 211, 213, 210, 
	211, 211, 358, 212, 214, 215, 216, 218, 
	219, 220, 222, 223, 224, 226, 227, 228, 
	230, 231, 232, 234, 235, 236, 238, 239, 
	240, 242, 243, 244, 246, 247, 248, 170, 
	171, 252, 253, 254, 255, 256, 257, 358, 
	258, 259, 257, 358, 258, 259, 260, 263, 
	261, 262, 263, 264, 265, 262, 264, 265, 
	262, 263, 267, 268, 269, 270, 271, 272, 
	271, 272, 273, 274, 275, 282, 283, 274, 
	275, 282, 283, 276, 358, 277, 278, 279, 
	358, 277, 280, 281, 279, 280, 281, 279, 
	358, 277, 274, 275, 285, 286, 287, 288, 
	289, 304, 320, 290, 291, 292, 293, 294, 
	295, 296, 297, 298, 295, 296, 297, 298, 
	295, 298, 299, 300, 358, 301, 302, 303, 
	300, 358, 301, 302, 303, 300, 358, 301, 
	305, 306, 307, 308, 309, 310, 311, 312, 
	313, 314, 311, 312, 313, 314, 311, 314, 
	315, 316, 358, 317, 318, 319, 316, 358, 
	317, 318, 319, 316, 358, 317, 321, 322, 
	323, 324, 325, 326, 327, 328, 329, 330, 
	331, 332, 333, 334, 331, 332, 333, 334, 
	331, 334, 335, 336, 358, 337, 338, 339, 
	336, 358, 337, 338, 339, 336, 358, 337, 
	341, 342, 343, 344, 345, 346, 347, 354, 
	355, 346, 347, 354, 355, 348, 358, 349, 
	350, 351, 358, 349, 352, 353, 351, 352, 
	353, 351, 358, 349, 346, 347, 356, 0, 
	358, 358
};

static const short _csys_line_test_trans_actions_wi[] = {
	67, 0, 0, 0, 0, 0, 0, 131, 
	189, 15, 128, 0, 41, 0, 17, 0, 
	0, 98, 98, 11, 13, 101, 11, 0, 
	43, 0, 98, 98, 11, 13, 104, 11, 
	0, 45, 0, 98, 98, 11, 13, 107, 
	11, 0, 47, 0, 98, 98, 11, 13, 
	110, 11, 0, 49, 0, 0, 98, 98, 
	11, 13, 113, 11, 0, 51, 0, 0, 
	98, 98, 11, 13, 116, 11, 0, 53, 
	0, 98, 98, 11, 13, 119, 11, 0, 
	55, 0, 98, 98, 11, 13, 122, 11, 
	0, 57, 0, 0, 98, 98, 11, 13, 
	125, 11, 0, 59, 0, 77, 0, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 19, 140, 75, 0, 86, 0, 
	197, 0, 0, 0, 63, 0, 143, 37, 
	0, 0, 0, 0, 0, 23, 3, 0, 
	0, 0, 0, 0, 3, 25, 0, 0, 
	0, 0, 0, 0, 27, 3, 0, 0, 
	0, 0, 0, 29, 3, 0, 0, 0, 
	0, 0, 31, 3, 0, 149, 0, 0, 
	185, 267, 185, 15, 128, 0, 0, 17, 
	137, 261, 137, 0, 9, 95, 3, 0, 
	9, 92, 3, 0, 9, 89, 3, 0, 
	0, 0, 35, 0, 0, 0, 33, 193, 
	33, 3, 0, 80, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 3, 0, 0, 153, 0, 7, 0, 
	0, 0, 0, 0, 131, 189, 15, 128, 
	0, 41, 0, 17, 0, 0, 98, 98, 
	11, 13, 101, 11, 0, 43, 0, 98, 
	98, 11, 13, 104, 11, 0, 45, 0, 
	98, 98, 11, 13, 107, 11, 0, 47, 
	0, 98, 98, 11, 13, 110, 11, 0, 
	49, 0, 0, 98, 98, 11, 13, 113, 
	11, 0, 51, 0, 0, 98, 98, 11, 
	13, 116, 11, 0, 53, 0, 98, 98, 
	11, 13, 119, 11, 0, 55, 0, 98, 
	98, 11, 13, 122, 11, 0, 57, 0, 
	0, 98, 98, 11, 13, 125, 11, 0, 
	59, 0, 169, 0, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 19, 
	140, 0, 0, 0, 0, 0, 65, 226, 
	65, 65, 0, 177, 0, 0, 0, 0, 
	0, 131, 131, 15, 128, 0, 0, 17, 
	19, 19, 0, 0, 0, 0, 61, 61, 
	0, 0, 0, 131, 131, 15, 128, 0, 
	0, 0, 17, 0, 173, 0, 0, 134, 
	249, 134, 15, 128, 0, 0, 17, 21, 
	216, 21, 19, 19, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	131, 15, 128, 131, 0, 0, 17, 0, 
	19, 19, 0, 134, 231, 134, 15, 128, 
	0, 157, 0, 0, 17, 21, 201, 21, 
	0, 0, 0, 0, 0, 0, 131, 15, 
	128, 131, 0, 0, 17, 0, 19, 19, 
	0, 134, 243, 134, 15, 128, 0, 165, 
	0, 0, 17, 21, 211, 21, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	131, 15, 128, 131, 0, 0, 17, 0, 
	19, 19, 0, 134, 255, 134, 15, 128, 
	0, 181, 0, 0, 17, 21, 221, 21, 
	0, 0, 0, 0, 0, 131, 131, 15, 
	128, 0, 0, 0, 17, 0, 161, 0, 
	0, 134, 237, 134, 15, 128, 0, 0, 
	17, 21, 206, 21, 19, 19, 0, 0, 
	83, 73
};

static const short _csys_line_test_to_state_actions[] = {
	0, 69, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 146, 0
};

static const short _csys_line_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 71, 0
};

static const short _csys_line_test_eof_actions[] = {
	0, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 67, 67, 67, 67, 67, 67, 67, 
	67, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0
};

static const short _csys_line_test_eof_trans[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 133, 133, 133, 133, 
	133, 133, 133, 133, 0, 0, 0, 562
};

static const int csys_line_test_start = 1;
static const int csys_line_test_first_final = 357;
static const int csys_line_test_error = 0;

static const int csys_line_test_en_group_scanner = 358;
static const int csys_line_test_en_main = 1;

#line 705 "NanorexMMPImportExportRagelTest.rl"
	
#line 4474 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = csys_line_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 706 "NanorexMMPImportExportRagelTest.rl"
	
#line 4484 "NanorexMMPImportExportRagelTest.cpp"
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
	_acts = _csys_line_test_actions + _csys_line_test_from_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 50:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 4505 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

	_keys = _csys_line_test_trans_keys + _csys_line_test_key_offsets[cs];
	_trans = _csys_line_test_index_offsets[cs];

	_klen = _csys_line_test_single_lengths[cs];
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

	_klen = _csys_line_test_range_lengths[cs];
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
	_trans = _csys_line_test_indicies[_trans];
_eof_trans:
	cs = _csys_line_test_trans_targs_wi[_trans];

	if ( _csys_line_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _csys_line_test_actions + _csys_line_test_trans_actions_wi[_trans];
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
#line 53 "NanorexMMPImportExportRagelTest.rl"
	{stringVal.clear(); /*stringVal = stringVal + fc;*/ doubleVal = HUGE_VAL;}
	break;
	case 7:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{stringVal = stringVal + (*p);}
	break;
	case 8:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{doubleVal = atof(stringVal.c_str());}
	break;
	case 9:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 10:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 11:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 12:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 13:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 14:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 20:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 22:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 23:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 24:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 26:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 27:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 28:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 29:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{csysViewName = stringVal;}
	break;
	case 30:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{csysQw=doubleVal;}
	break;
	case 31:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{csysQx=doubleVal;}
	break;
	case 32:
#line 42 "NanorexMMPImportExportRagelTest.rl"
	{csysQy=doubleVal;}
	break;
	case 33:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{csysQz=doubleVal;}
	break;
	case 34:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{csysScale=doubleVal;}
	break;
	case 35:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{csysPovX=doubleVal;}
	break;
	case 36:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{csysPovY=doubleVal;}
	break;
	case 37:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{csysPovZ=doubleVal;}
	break;
	case 38:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{csysZoomFactor=doubleVal;}
	break;
	case 39:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{ newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
	break;
	case 40:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 41:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 42:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 43:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 44:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 45:
#line 98 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 46:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 47:
#line 687 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "csys_line_test state machine");
		}
	break;
	case 51:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 52:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{act = 12;}
	break;
	case 53:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 54:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 55:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 57:
#line 120 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 58:
#line 121 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 59:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 60:
#line 123 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 61:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 62:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 63:
#line 128 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 64:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 65:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 66:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 12:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 4856 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

_again:
	_acts = _csys_line_test_actions + _csys_line_test_to_state_actions[cs];
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
	case 25:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 48:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 49:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 4885 "NanorexMMPImportExportRagelTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	if ( _csys_line_test_eof_trans[cs] > 0 ) {
		_trans = _csys_line_test_eof_trans[cs] - 1;
		goto _eof_trans;
	}
	const char *__acts = _csys_line_test_actions + _csys_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 47:
#line 687 "NanorexMMPImportExportRagelTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "csys_line_test state machine");
		}
	break;
#line 4911 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 707 "NanorexMMPImportExportRagelTest.rl"
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


#line 856 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 869 "NanorexMMPImportExportRagelTest.rl"
	
#line 5060 "NanorexMMPImportExportRagelTest.cpp"
static const char _group_lines_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 5, 1, 7, 1, 8, 1, 
	9, 1, 10, 1, 11, 1, 12, 1, 
	13, 1, 14, 1, 15, 1, 16, 1, 
	17, 1, 20, 1, 21, 1, 24, 1, 
	25, 1, 31, 1, 32, 1, 33, 1, 
	34, 1, 35, 1, 36, 1, 37, 1, 
	38, 1, 39, 1, 40, 1, 42, 1, 
	44, 1, 46, 1, 47, 1, 51, 1, 
	52, 1, 54, 1, 69, 1, 70, 1, 
	77, 1, 78, 2, 0, 65, 2, 0, 
	67, 2, 0, 68, 2, 0, 76, 2, 
	5, 15, 2, 5, 16, 2, 5, 17, 
	2, 6, 7, 2, 8, 32, 2, 8, 
	33, 2, 8, 34, 2, 8, 35, 2, 
	8, 36, 2, 8, 37, 2, 8, 38, 
	2, 8, 39, 2, 8, 40, 2, 9, 
	10, 2, 9, 11, 2, 9, 12, 2, 
	11, 18, 2, 11, 31, 2, 29, 42, 
	2, 49, 27, 2, 52, 53, 3, 0, 
	19, 63, 3, 0, 22, 66, 3, 0, 
	23, 64, 3, 0, 26, 61, 3, 0, 
	28, 62, 3, 0, 30, 73, 3, 0, 
	41, 57, 3, 0, 43, 58, 3, 0, 
	43, 75, 3, 0, 45, 74, 3, 0, 
	48, 60, 3, 0, 48, 72, 3, 0, 
	50, 59, 3, 9, 11, 18, 3, 9, 
	11, 31, 3, 20, 0, 65, 3, 55, 
	0, 56, 3, 55, 0, 71, 4, 12, 
	0, 23, 64, 4, 12, 0, 26, 61, 
	4, 12, 0, 28, 62, 4, 12, 0, 
	43, 58, 4, 12, 0, 43, 75, 4, 
	12, 0, 50, 59, 4, 47, 0, 48, 
	60, 4, 47, 0, 48, 72, 5, 9, 
	12, 0, 23, 64, 5, 9, 12, 0, 
	26, 61, 5, 9, 12, 0, 28, 62, 
	5, 9, 12, 0, 43, 58, 5, 9, 
	12, 0, 43, 75, 5, 9, 12, 0, 
	50, 59, 5, 11, 18, 0, 19, 63, 
	6, 9, 11, 18, 0, 19, 63
};

static const short _group_lines_test_key_offsets[] = {
	0, 0, 2, 14, 17, 20, 23, 28, 
	35, 42, 48, 55, 63, 69, 74, 80, 
	89, 93, 101, 107, 116, 120, 128, 134, 
	143, 147, 155, 161, 167, 180, 182, 197, 
	212, 226, 241, 249, 253, 261, 269, 277, 
	281, 289, 297, 305, 309, 317, 325, 333, 
	340, 343, 346, 349, 357, 362, 369, 377, 
	385, 387, 395, 398, 401, 404, 407, 410, 
	413, 416, 419, 422, 427, 434, 441, 448, 
	456, 462, 464, 472, 479, 482, 485, 488, 
	494, 506, 521, 536, 542, 551, 555, 564, 
	570, 579, 583, 592, 598, 607, 611, 620, 
	626, 635, 639, 648, 654, 660, 669, 673, 
	682, 688, 694, 703, 707, 716, 722, 731, 
	735, 744, 750, 759, 763, 772, 778, 784, 
	793, 797, 806, 812, 818, 820, 830, 836, 
	840, 848, 858, 864, 868, 876, 886, 892, 
	896, 904, 914, 920, 924, 932, 942, 948, 
	952, 960, 970, 976, 980, 988, 998, 1004, 
	1008, 1016, 1026, 1032, 1036, 1044, 1054, 1060, 
	1064, 1072, 1086, 1101, 1104, 1107, 1110, 1113, 
	1116, 1123, 1130, 1132, 1145, 1157, 1172, 1187, 
	1193, 1207, 1222, 1225, 1228, 1231, 1234, 1240, 
	1246, 1258, 1273, 1288, 1294, 1307, 1309, 1324, 
	1339, 1353, 1368, 1382, 1397, 1400, 1403, 1406, 
	1411, 1419, 1422, 1425, 1428, 1433, 1445, 1460, 
	1475, 1489, 1504, 1516, 1531, 1546, 1548, 1562, 
	1577, 1580, 1583, 1586, 1589, 1594, 1606, 1621, 
	1636, 1650, 1665, 1677, 1692, 1707, 1709, 1723, 
	1738, 1741, 1744, 1747, 1750, 1753, 1756, 1759, 
	1762, 1767, 1779, 1794, 1809, 1823, 1838, 1850, 
	1865, 1880, 1882, 1896, 1911, 1914, 1917, 1922, 
	1928, 1940, 1955, 1970, 1976, 1989, 1991, 2006, 
	2021, 2035, 2050, 2064, 2079, 2081, 2083, 2090, 
	2093, 2096, 2099, 2102, 2105, 2112, 2119, 2121, 
	2134, 2146, 2161, 2176, 2182, 2196, 2211, 2214, 
	2217, 2220, 2223, 2229, 2235, 2249, 2264, 2279, 
	2285, 2298, 2300, 2315, 2330, 2344, 2359, 2373, 
	2388, 2404, 2420, 2436, 2452, 2468, 2484, 2500, 
	2516, 2531, 2546, 2552, 2565, 2567, 2583, 2599, 
	2615, 2630, 2646, 2662, 2678, 2694, 2709, 2724, 
	2730, 2743, 2745, 2745, 2745, 2758, 2770, 2777
};

static const char _group_lines_test_trans_keys[] = {
	-1, 10, -1, 10, 32, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	116, -1, 10, 111, -1, 10, 109, -1, 
	10, 32, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 111, -1, 
	10, 110, -1, 10, 100, -1, 10, 95, 
	97, 99, 103, 49, 51, -1, 10, 32, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 100, -1, 10, 
	105, -1, 10, 114, -1, 10, 101, -1, 
	10, 99, -1, 10, 116, -1, 10, 105, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	32, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 115, -1, 10, 121, -1, 10, 115, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 46, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 46, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 46, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 46, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 103, 
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
	10, -1, 10, -1, 10, 32, 101, 103, 
	9, 13, -1, 10, 103, -1, 10, 114, 
	-1, 10, 111, -1, 10, 117, -1, 10, 
	112, -1, 10, 32, 35, 40, 9, 13, 
	-1, 10, 32, 35, 40, 9, 13, -1, 
	10, -1, 10, 32, 41, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 114, -1, 10, 
	111, -1, 10, 117, -1, 10, 112, -1, 
	10, 32, 40, 9, 13, -1, 10, 32, 
	40, 9, 13, -1, 10, 32, 67, 86, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 35, 9, 13, -1, 10, 32, 
	35, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, -1, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 95, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 108, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 105, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 112, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 98, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 111, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 97, 9, 13, 45, 46, 48, 57, 
	65, 90, 98, 122, -1, 10, 32, 41, 
	95, 114, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 100, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 9, 13, 
	-1, 10, 32, 35, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, -1, 
	10, 32, 41, 95, 105, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 101, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 119, 9, 13, 45, 
	46, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 68, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 97, 9, 13, 45, 46, 
	48, 57, 65, 90, 98, 122, -1, 10, 
	32, 41, 95, 116, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 97, 9, 13, 45, 46, 
	48, 57, 65, 90, 98, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 35, 
	9, 13, -1, 10, 32, 35, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, -1, 10, 32, 35, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	32, 97, 98, 99, 101, 103, 105, 109, 
	9, 13, -1, 10, 32, 101, 103, 9, 
	13, -1, 10, 32, 101, 103, 9, 13, 
	0
};

static const char _group_lines_test_single_lengths[] = {
	0, 2, 10, 3, 3, 3, 3, 3, 
	3, 4, 3, 4, 4, 3, 4, 5, 
	2, 4, 4, 5, 2, 4, 4, 5, 
	2, 4, 4, 4, 5, 2, 5, 5, 
	4, 5, 4, 2, 4, 4, 4, 2, 
	4, 4, 4, 2, 4, 4, 4, 3, 
	3, 3, 3, 6, 3, 3, 4, 4, 
	2, 4, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 4, 
	4, 2, 4, 3, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 4, 
	5, 2, 5, 4, 5, 2, 5, 4, 
	5, 2, 5, 4, 4, 5, 2, 5, 
	4, 4, 5, 2, 5, 4, 5, 2, 
	5, 4, 5, 2, 5, 4, 4, 5, 
	2, 5, 4, 4, 2, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 6, 4, 2, 4, 6, 4, 2, 
	4, 4, 5, 3, 3, 3, 3, 3, 
	5, 5, 2, 5, 4, 5, 5, 4, 
	4, 5, 3, 3, 3, 3, 4, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 3, 3, 3, 3, 
	6, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 4, 5, 5, 
	4, 5, 4, 5, 5, 2, 4, 5, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 4, 5, 5, 4, 5, 4, 5, 
	5, 2, 4, 5, 3, 3, 3, 4, 
	4, 5, 5, 4, 5, 2, 5, 5, 
	4, 5, 4, 5, 2, 2, 5, 3, 
	3, 3, 3, 3, 5, 5, 2, 5, 
	4, 5, 5, 4, 4, 5, 3, 3, 
	3, 3, 4, 4, 6, 5, 5, 4, 
	5, 2, 5, 5, 4, 5, 4, 5, 
	6, 6, 6, 6, 6, 6, 6, 6, 
	5, 5, 4, 5, 2, 6, 6, 6, 
	5, 6, 6, 6, 6, 5, 5, 4, 
	5, 2, 0, 0, 11, 10, 5, 5
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
	1, 0, 2, 2, 0, 0, 0, 1, 
	4, 5, 5, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 1, 2, 
	1, 2, 1, 1, 0, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 2, 1, 1, 2, 2, 1, 1, 
	2, 5, 5, 0, 0, 0, 0, 0, 
	1, 1, 0, 4, 4, 5, 5, 1, 
	5, 5, 0, 0, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 0, 1, 
	1, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 1, 4, 5, 5, 
	5, 5, 4, 5, 5, 0, 5, 5, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 4, 5, 5, 5, 5, 4, 5, 
	5, 0, 5, 5, 0, 0, 1, 1, 
	4, 5, 5, 1, 4, 0, 5, 5, 
	5, 5, 5, 5, 0, 0, 1, 0, 
	0, 0, 0, 0, 1, 1, 0, 4, 
	4, 5, 5, 1, 5, 5, 0, 0, 
	0, 0, 1, 1, 4, 5, 5, 1, 
	4, 0, 5, 5, 5, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 5, 5, 
	5, 5, 1, 4, 0, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 5, 1, 
	4, 0, 0, 0, 1, 1, 1, 1
};

static const short _group_lines_test_index_offsets[] = {
	0, 0, 3, 15, 19, 23, 27, 32, 
	38, 44, 50, 56, 63, 69, 74, 80, 
	88, 92, 99, 105, 113, 117, 124, 130, 
	138, 142, 149, 155, 161, 171, 174, 185, 
	196, 206, 217, 224, 228, 235, 242, 249, 
	253, 260, 267, 274, 278, 285, 292, 299, 
	305, 309, 313, 317, 325, 330, 336, 343, 
	350, 353, 360, 364, 368, 372, 376, 380, 
	384, 388, 392, 396, 401, 407, 413, 419, 
	426, 432, 435, 442, 448, 452, 456, 460, 
	466, 475, 486, 497, 503, 511, 515, 523, 
	529, 537, 541, 549, 555, 563, 567, 575, 
	581, 589, 593, 601, 607, 613, 621, 625, 
	633, 639, 645, 653, 657, 665, 671, 679, 
	683, 691, 697, 705, 709, 717, 723, 729, 
	737, 741, 749, 755, 761, 764, 773, 779, 
	783, 790, 799, 805, 809, 816, 825, 831, 
	835, 842, 851, 857, 861, 868, 877, 883, 
	887, 894, 903, 909, 913, 920, 929, 935, 
	939, 946, 955, 961, 965, 972, 981, 987, 
	991, 998, 1008, 1019, 1023, 1027, 1031, 1035, 
	1039, 1046, 1053, 1056, 1066, 1075, 1086, 1097, 
	1103, 1113, 1124, 1128, 1132, 1136, 1140, 1146, 
	1152, 1161, 1172, 1183, 1189, 1199, 1202, 1213, 
	1224, 1234, 1245, 1255, 1266, 1270, 1274, 1278, 
	1283, 1291, 1295, 1299, 1303, 1308, 1317, 1328, 
	1339, 1349, 1360, 1369, 1380, 1391, 1394, 1404, 
	1415, 1419, 1423, 1427, 1431, 1436, 1445, 1456, 
	1467, 1477, 1488, 1497, 1508, 1519, 1522, 1532, 
	1543, 1547, 1551, 1555, 1559, 1563, 1567, 1571, 
	1575, 1580, 1589, 1600, 1611, 1621, 1632, 1641, 
	1652, 1663, 1666, 1676, 1687, 1691, 1695, 1700, 
	1706, 1715, 1726, 1737, 1743, 1753, 1756, 1767, 
	1778, 1788, 1799, 1809, 1820, 1823, 1826, 1833, 
	1837, 1841, 1845, 1849, 1853, 1860, 1867, 1870, 
	1880, 1889, 1900, 1911, 1917, 1927, 1938, 1942, 
	1946, 1950, 1954, 1960, 1966, 1977, 1988, 1999, 
	2005, 2015, 2018, 2029, 2040, 2050, 2061, 2071, 
	2082, 2094, 2106, 2118, 2130, 2142, 2154, 2166, 
	2178, 2189, 2200, 2206, 2216, 2219, 2231, 2243, 
	2255, 2266, 2278, 2290, 2302, 2314, 2325, 2336, 
	2342, 2352, 2355, 2356, 2357, 2370, 2382, 2389
};

static const short _group_lines_test_indicies[] = {
	0, 2, 1, 0, 4, 3, 5, 6, 
	7, 8, 9, 10, 11, 3, 1, 0, 
	2, 12, 1, 0, 2, 13, 1, 0, 
	2, 14, 1, 0, 2, 15, 15, 1, 
	0, 2, 15, 15, 16, 1, 0, 2, 
	17, 17, 18, 1, 0, 2, 19, 20, 
	19, 1, 0, 2, 20, 20, 21, 1, 
	0, 2, 22, 23, 22, 24, 1, 0, 
	2, 22, 23, 22, 1, 0, 2, 25, 
	25, 1, 0, 2, 26, 27, 26, 1, 
	0, 2, 27, 28, 29, 27, 30, 1, 
	0, 2, 30, 1, 0, 2, 31, 32, 
	31, 33, 1, 0, 2, 31, 32, 31, 
	1, 0, 2, 34, 35, 36, 34, 37, 
	1, 0, 2, 37, 1, 0, 2, 38, 
	39, 38, 40, 1, 0, 2, 38, 39, 
	38, 1, 0, 2, 41, 42, 43, 41, 
	44, 1, 0, 2, 44, 1, 0, 2, 
	45, 46, 45, 47, 1, 0, 2, 45, 
	46, 45, 1, 0, 49, 48, 50, 48, 
	1, 0, 49, 48, 50, 51, 48, 51, 
	51, 51, 1, 0, 49, 50, 0, 53, 
	52, 54, 56, 52, 55, 56, 56, 56, 
	1, 0, 49, 57, 50, 59, 57, 58, 
	59, 59, 59, 1, 0, 2, 58, 59, 
	58, 58, 59, 59, 59, 1, 0, 61, 
	60, 62, 59, 60, 58, 59, 59, 59, 
	1, 0, 2, 45, 46, 45, 47, 1, 
	0, 2, 63, 1, 0, 2, 64, 65, 
	64, 66, 1, 0, 2, 64, 65, 64, 
	66, 1, 0, 2, 38, 39, 38, 40, 
	1, 0, 2, 67, 1, 0, 2, 68, 
	69, 68, 70, 1, 0, 2, 68, 69, 
	68, 70, 1, 0, 2, 31, 32, 31, 
	33, 1, 0, 2, 71, 1, 0, 2, 
	72, 73, 72, 74, 1, 0, 2, 72, 
	73, 72, 74, 1, 0, 2, 22, 23, 
	22, 24, 1, 0, 2, 17, 17, 18, 
	1, 0, 2, 75, 1, 0, 2, 76, 
	1, 0, 2, 77, 1, 0, 2, 79, 
	78, 78, 78, 78, 1, 0, 2, 80, 
	80, 1, 0, 2, 80, 80, 81, 1, 
	0, 83, 82, 84, 82, 85, 1, 0, 
	87, 86, 88, 86, 81, 1, 0, 87, 
	88, 0, 83, 82, 84, 82, 85, 1, 
	0, 2, 89, 1, 0, 2, 90, 1, 
	0, 2, 91, 1, 0, 2, 92, 1, 
	0, 2, 93, 1, 0, 2, 94, 1, 
	0, 2, 95, 1, 0, 2, 96, 1, 
	0, 2, 97, 1, 0, 2, 98, 98, 
	1, 0, 2, 98, 98, 99, 1, 0, 
	2, 100, 100, 101, 1, 0, 2, 100, 
	100, 102, 1, 0, 104, 103, 105, 103, 
	106, 1, 0, 104, 103, 105, 103, 1, 
	0, 104, 105, 0, 104, 103, 105, 103, 
	106, 1, 0, 2, 100, 100, 101, 1, 
	0, 2, 107, 1, 0, 2, 108, 1, 
	0, 2, 109, 1, 0, 2, 109, 110, 
	109, 1, 0, 2, 110, 111, 110, 111, 
	111, 111, 1, 0, 2, 112, 113, 115, 
	112, 114, 115, 115, 115, 1, 0, 2, 
	116, 117, 119, 116, 118, 119, 119, 119, 
	1, 0, 2, 120, 121, 120, 1, 0, 
	2, 121, 122, 122, 121, 123, 1, 0, 
	2, 124, 1, 0, 2, 125, 126, 127, 
	125, 124, 1, 0, 2, 128, 129, 128, 
	1, 0, 2, 130, 131, 131, 130, 132, 
	1, 0, 2, 133, 1, 0, 2, 134, 
	135, 136, 134, 133, 1, 0, 2, 137, 
	138, 137, 1, 0, 2, 139, 140, 140, 
	139, 141, 1, 0, 2, 142, 1, 0, 
	2, 143, 144, 145, 143, 142, 1, 0, 
	2, 146, 147, 146, 1, 0, 2, 148, 
	149, 149, 148, 150, 1, 0, 2, 151, 
	1, 0, 2, 152, 153, 154, 152, 151, 
	1, 0, 2, 155, 156, 155, 1, 0, 
	2, 157, 158, 157, 1, 0, 2, 158, 
	159, 159, 158, 160, 1, 0, 2, 161, 
	1, 0, 2, 162, 163, 164, 162, 161, 
	1, 0, 2, 165, 166, 165, 1, 0, 
	2, 167, 168, 167, 1, 0, 2, 168, 
	169, 169, 168, 170, 1, 0, 2, 171, 
	1, 0, 2, 172, 173, 174, 172, 171, 
	1, 0, 2, 175, 176, 175, 1, 0, 
	2, 177, 178, 178, 177, 179, 1, 0, 
	2, 180, 1, 0, 2, 181, 182, 183, 
	181, 180, 1, 0, 2, 184, 185, 184, 
	1, 0, 2, 186, 187, 187, 186, 188, 
	1, 0, 2, 189, 1, 0, 2, 190, 
	191, 192, 190, 189, 1, 0, 2, 193, 
	194, 193, 1, 0, 2, 195, 196, 195, 
	1, 0, 2, 196, 197, 197, 196, 198, 
	1, 0, 2, 199, 1, 0, 2, 200, 
	201, 202, 200, 199, 1, 0, 2, 203, 
	204, 203, 1, 0, 206, 205, 207, 205, 
	1, 0, 206, 207, 0, 2, 200, 201, 
	208, 208, 200, 202, 1, 0, 2, 209, 
	209, 210, 1, 0, 2, 210, 1, 0, 
	2, 200, 201, 200, 210, 1, 0, 2, 
	190, 191, 211, 211, 190, 192, 1, 0, 
	2, 212, 212, 213, 1, 0, 2, 213, 
	1, 0, 2, 190, 191, 190, 213, 1, 
	0, 2, 181, 182, 214, 214, 181, 183, 
	1, 0, 2, 215, 215, 216, 1, 0, 
	2, 216, 1, 0, 2, 181, 182, 181, 
	216, 1, 0, 2, 172, 173, 217, 217, 
	172, 174, 1, 0, 2, 218, 218, 219, 
	1, 0, 2, 219, 1, 0, 2, 172, 
	173, 172, 219, 1, 0, 2, 162, 163, 
	220, 220, 162, 164, 1, 0, 2, 221, 
	221, 222, 1, 0, 2, 222, 1, 0, 
	2, 162, 163, 162, 222, 1, 0, 2, 
	152, 153, 223, 223, 152, 154, 1, 0, 
	2, 224, 224, 225, 1, 0, 2, 225, 
	1, 0, 2, 152, 153, 152, 225, 1, 
	0, 2, 143, 144, 226, 226, 143, 145, 
	1, 0, 2, 227, 227, 228, 1, 0, 
	2, 228, 1, 0, 2, 143, 144, 143, 
	228, 1, 0, 2, 134, 135, 229, 229, 
	134, 136, 1, 0, 2, 230, 230, 231, 
	1, 0, 2, 231, 1, 0, 2, 134, 
	135, 134, 231, 1, 0, 2, 125, 126, 
	232, 232, 125, 127, 1, 0, 2, 233, 
	233, 234, 1, 0, 2, 234, 1, 0, 
	2, 125, 126, 125, 234, 1, 0, 2, 
	118, 119, 118, 118, 119, 119, 119, 1, 
	0, 2, 235, 236, 119, 235, 118, 119, 
	119, 119, 1, 0, 2, 237, 1, 0, 
	2, 238, 1, 0, 2, 239, 1, 0, 
	2, 240, 1, 0, 2, 241, 1, 0, 
	243, 242, 244, 245, 242, 1, 0, 247, 
	246, 248, 249, 246, 1, 0, 247, 248, 
	0, 2, 250, 251, 252, 250, 252, 252, 
	252, 1, 0, 2, 250, 252, 250, 252, 
	252, 252, 1, 0, 2, 253, 254, 256, 
	253, 255, 256, 256, 256, 1, 0, 2, 
	257, 251, 259, 257, 258, 259, 259, 259, 
	1, 0, 247, 251, 248, 251, 1, 0, 
	2, 258, 259, 258, 258, 259, 259, 259, 
	1, 0, 2, 260, 261, 259, 260, 258, 
	259, 259, 259, 1, 0, 2, 262, 1, 
	0, 2, 263, 1, 0, 2, 264, 1, 
	0, 2, 265, 1, 0, 2, 266, 267, 
	266, 1, 0, 2, 268, 269, 268, 1, 
	0, 2, 269, 270, 269, 270, 270, 270, 
	1, 0, 2, 271, 272, 274, 271, 273, 
	274, 274, 274, 1, 0, 2, 275, 276, 
	278, 275, 277, 278, 278, 278, 1, 0, 
	280, 279, 281, 279, 1, 0, 280, 279, 
	281, 282, 279, 282, 282, 282, 1, 0, 
	280, 281, 0, 284, 283, 285, 287, 283, 
	286, 287, 287, 287, 1, 0, 280, 288, 
	281, 290, 288, 289, 290, 290, 290, 1, 
	0, 2, 289, 290, 289, 289, 290, 290, 
	290, 1, 0, 292, 291, 293, 290, 291, 
	289, 290, 290, 290, 1, 0, 2, 277, 
	278, 277, 277, 278, 278, 278, 1, 0, 
	2, 294, 295, 278, 294, 277, 278, 278, 
	278, 1, 0, 2, 296, 1, 0, 2, 
	297, 1, 0, 2, 298, 1, 0, 2, 
	299, 299, 1, 0, 2, 299, 300, 301, 
	302, 299, 1, 0, 2, 303, 1, 0, 
	2, 304, 1, 0, 2, 305, 1, 0, 
	2, 306, 306, 1, 0, 2, 306, 307, 
	306, 307, 307, 307, 1, 0, 2, 308, 
	311, 310, 308, 309, 310, 310, 310, 1, 
	0, 2, 312, 315, 314, 312, 313, 314, 
	314, 314, 1, 0, 2, 313, 314, 313, 
	313, 314, 314, 314, 1, 0, 2, 316, 
	317, 314, 316, 313, 314, 314, 314, 1, 
	0, 2, 315, 318, 315, 318, 318, 318, 
	1, 0, 320, 319, 321, 323, 319, 322, 
	323, 323, 323, 1, 0, 325, 324, 326, 
	328, 324, 327, 328, 328, 328, 1, 0, 
	325, 326, 0, 2, 327, 328, 327, 327, 
	328, 328, 328, 1, 0, 330, 329, 331, 
	328, 329, 327, 328, 328, 328, 1, 0, 
	2, 332, 1, 0, 2, 333, 1, 0, 
	2, 334, 1, 0, 2, 335, 1, 0, 
	2, 336, 336, 1, 0, 2, 336, 337, 
	336, 337, 337, 337, 1, 0, 2, 338, 
	341, 340, 338, 339, 340, 340, 340, 1, 
	0, 2, 342, 345, 344, 342, 343, 344, 
	344, 344, 1, 0, 2, 343, 344, 343, 
	343, 344, 344, 344, 1, 0, 2, 346, 
	347, 344, 346, 343, 344, 344, 344, 1, 
	0, 2, 345, 348, 345, 348, 348, 348, 
	1, 0, 350, 349, 351, 353, 349, 352, 
	353, 353, 353, 1, 0, 355, 354, 356, 
	358, 354, 357, 358, 358, 358, 1, 0, 
	355, 356, 0, 2, 357, 358, 357, 357, 
	358, 358, 358, 1, 0, 360, 359, 361, 
	358, 359, 357, 358, 358, 358, 1, 0, 
	2, 362, 1, 0, 2, 363, 1, 0, 
	2, 364, 1, 0, 2, 365, 1, 0, 
	2, 366, 1, 0, 2, 367, 1, 0, 
	2, 368, 1, 0, 2, 369, 1, 0, 
	2, 370, 370, 1, 0, 2, 370, 371, 
	370, 371, 371, 371, 1, 0, 2, 372, 
	375, 374, 372, 373, 374, 374, 374, 1, 
	0, 2, 376, 379, 378, 376, 377, 378, 
	378, 378, 1, 0, 2, 377, 378, 377, 
	377, 378, 378, 378, 1, 0, 2, 380, 
	381, 378, 380, 377, 378, 378, 378, 1, 
	0, 2, 379, 382, 379, 382, 382, 382, 
	1, 0, 384, 383, 385, 387, 383, 386, 
	387, 387, 387, 1, 0, 389, 388, 390, 
	392, 388, 391, 392, 392, 392, 1, 0, 
	389, 390, 0, 2, 391, 392, 391, 391, 
	392, 392, 392, 1, 0, 394, 393, 395, 
	392, 393, 391, 392, 392, 392, 1, 0, 
	2, 396, 1, 0, 2, 397, 1, 0, 
	2, 398, 398, 1, 0, 2, 398, 399, 
	398, 1, 0, 2, 399, 400, 399, 400, 
	400, 400, 1, 0, 2, 401, 402, 404, 
	401, 403, 404, 404, 404, 1, 0, 2, 
	405, 406, 408, 405, 407, 408, 408, 408, 
	1, 0, 410, 409, 411, 409, 1, 0, 
	410, 409, 411, 412, 409, 412, 412, 412, 
	1, 0, 410, 411, 0, 414, 413, 415, 
	417, 413, 416, 417, 417, 417, 1, 0, 
	410, 418, 411, 420, 418, 419, 420, 420, 
	420, 1, 0, 2, 419, 420, 419, 419, 
	420, 420, 420, 1, 0, 422, 421, 423, 
	420, 421, 419, 420, 420, 420, 1, 0, 
	2, 407, 408, 407, 407, 408, 408, 408, 
	1, 0, 2, 424, 425, 408, 424, 407, 
	408, 408, 408, 1, 427, 428, 426, 429, 
	431, 430, 429, 433, 432, 434, 435, 432, 
	430, 429, 431, 436, 430, 429, 431, 437, 
	430, 429, 431, 438, 430, 429, 431, 439, 
	430, 429, 431, 440, 430, 429, 442, 441, 
	443, 444, 441, 430, 429, 446, 445, 447, 
	448, 445, 430, 429, 446, 447, 429, 431, 
	449, 450, 451, 449, 451, 451, 451, 430, 
	429, 431, 449, 451, 449, 451, 451, 451, 
	430, 429, 431, 452, 453, 455, 452, 454, 
	455, 455, 455, 430, 429, 431, 456, 450, 
	458, 456, 457, 458, 458, 458, 430, 429, 
	446, 450, 447, 450, 430, 429, 431, 457, 
	458, 457, 457, 458, 458, 458, 430, 429, 
	431, 459, 460, 458, 459, 457, 458, 458, 
	458, 430, 429, 431, 461, 430, 429, 431, 
	462, 430, 429, 431, 463, 430, 429, 431, 
	464, 430, 429, 431, 465, 466, 465, 430, 
	429, 431, 467, 468, 467, 430, 429, 431, 
	468, 470, 471, 469, 468, 469, 469, 469, 
	430, 429, 431, 472, 473, 475, 472, 474, 
	475, 475, 475, 430, 429, 431, 476, 477, 
	479, 476, 478, 479, 479, 479, 430, 429, 
	481, 480, 482, 480, 430, 429, 481, 480, 
	482, 483, 480, 483, 483, 483, 430, 429, 
	481, 482, 429, 485, 484, 486, 488, 484, 
	487, 488, 488, 488, 430, 429, 481, 489, 
	482, 491, 489, 490, 491, 491, 491, 430, 
	429, 431, 490, 491, 490, 490, 491, 491, 
	491, 430, 429, 493, 492, 494, 491, 492, 
	490, 491, 491, 491, 430, 429, 431, 478, 
	479, 478, 478, 479, 479, 479, 430, 429, 
	431, 495, 496, 479, 495, 478, 479, 479, 
	479, 430, 429, 431, 472, 473, 475, 497, 
	472, 474, 475, 475, 475, 430, 429, 431, 
	495, 496, 479, 498, 495, 478, 479, 479, 
	479, 430, 429, 431, 495, 496, 479, 499, 
	495, 478, 479, 479, 479, 430, 429, 431, 
	495, 496, 479, 500, 495, 478, 479, 479, 
	479, 430, 429, 431, 495, 496, 479, 501, 
	495, 478, 479, 479, 479, 430, 429, 431, 
	495, 496, 479, 502, 495, 478, 479, 479, 
	479, 430, 429, 431, 495, 496, 479, 503, 
	495, 478, 479, 479, 479, 430, 429, 431, 
	495, 496, 479, 504, 495, 478, 479, 479, 
	479, 430, 429, 431, 505, 506, 479, 505, 
	478, 479, 479, 479, 430, 429, 431, 507, 
	508, 479, 507, 478, 479, 479, 479, 430, 
	429, 510, 509, 511, 509, 430, 429, 510, 
	509, 511, 483, 509, 483, 483, 483, 430, 
	429, 510, 511, 429, 431, 472, 473, 475, 
	512, 472, 474, 475, 475, 475, 430, 429, 
	431, 495, 496, 479, 513, 495, 478, 479, 
	479, 479, 430, 429, 431, 495, 496, 479, 
	514, 495, 478, 479, 479, 479, 430, 429, 
	431, 515, 496, 479, 515, 478, 479, 479, 
	479, 430, 429, 431, 516, 477, 517, 479, 
	516, 478, 479, 479, 479, 430, 429, 431, 
	495, 496, 479, 518, 495, 478, 479, 479, 
	479, 430, 429, 431, 495, 496, 479, 519, 
	495, 478, 479, 479, 479, 430, 429, 431, 
	495, 496, 479, 520, 495, 478, 479, 479, 
	479, 430, 429, 431, 521, 522, 479, 521, 
	478, 479, 479, 479, 430, 429, 431, 523, 
	524, 479, 523, 478, 479, 479, 479, 430, 
	429, 526, 525, 527, 525, 430, 429, 526, 
	525, 527, 483, 525, 483, 483, 483, 430, 
	429, 526, 527, 528, 529, 427, 4, 3, 
	426, 5, 6, 7, 8, 9, 10, 11, 
	3, 1, 530, 4, 3, 5, 6, 7, 
	8, 9, 10, 11, 3, 1, 427, 433, 
	432, 434, 435, 432, 430, 531, 433, 432, 
	434, 435, 432, 430, 0
};

static const short _group_lines_test_trans_targs_wi[] = {
	332, 1, 332, 2, 333, 3, 48, 76, 
	163, 178, 196, 252, 4, 5, 6, 7, 
	8, 9, 47, 9, 10, 11, 12, 13, 
	46, 14, 14, 15, 16, 43, 17, 18, 
	19, 42, 19, 20, 39, 21, 22, 23, 
	38, 23, 24, 35, 25, 26, 27, 34, 
	28, 332, 29, 30, 31, 332, 29, 32, 
	33, 31, 32, 33, 31, 332, 29, 36, 
	26, 27, 37, 40, 22, 23, 41, 44, 
	18, 19, 45, 49, 50, 51, 52, 58, 
	53, 54, 55, 332, 56, 57, 55, 332, 
	56, 59, 60, 61, 62, 63, 64, 65, 
	66, 67, 68, 69, 70, 75, 71, 72, 
	332, 73, 74, 77, 78, 79, 80, 81, 
	82, 83, 161, 162, 82, 83, 161, 162, 
	83, 84, 85, 86, 86, 87, 88, 157, 
	87, 88, 88, 89, 90, 90, 91, 92, 
	153, 91, 92, 92, 93, 94, 94, 95, 
	96, 149, 95, 96, 96, 97, 98, 98, 
	99, 100, 145, 99, 100, 100, 101, 102, 
	103, 103, 104, 105, 141, 104, 105, 105, 
	106, 107, 108, 108, 109, 110, 137, 109, 
	110, 110, 111, 112, 112, 113, 114, 133, 
	113, 114, 114, 115, 116, 116, 117, 118, 
	129, 117, 118, 118, 119, 120, 121, 121, 
	122, 123, 125, 122, 123, 123, 332, 124, 
	126, 127, 128, 130, 131, 132, 134, 135, 
	136, 138, 139, 140, 142, 143, 144, 146, 
	147, 148, 150, 151, 152, 154, 155, 156, 
	158, 159, 160, 82, 83, 164, 165, 166, 
	167, 168, 169, 332, 170, 171, 169, 332, 
	170, 171, 172, 175, 173, 174, 175, 176, 
	177, 174, 176, 177, 174, 175, 179, 180, 
	181, 182, 183, 184, 183, 184, 185, 186, 
	187, 194, 195, 186, 187, 194, 195, 188, 
	332, 189, 190, 191, 332, 189, 192, 193, 
	191, 192, 193, 191, 332, 189, 186, 187, 
	197, 198, 199, 200, 201, 216, 232, 202, 
	203, 204, 205, 206, 207, 208, 209, 210, 
	207, 208, 209, 210, 207, 210, 211, 212, 
	332, 213, 214, 215, 212, 332, 213, 214, 
	215, 212, 332, 213, 217, 218, 219, 220, 
	221, 222, 223, 224, 225, 226, 223, 224, 
	225, 226, 223, 226, 227, 228, 332, 229, 
	230, 231, 228, 332, 229, 230, 231, 228, 
	332, 229, 233, 234, 235, 236, 237, 238, 
	239, 240, 241, 242, 243, 244, 245, 246, 
	243, 244, 245, 246, 243, 246, 247, 248, 
	332, 249, 250, 251, 248, 332, 249, 250, 
	251, 248, 332, 249, 253, 254, 255, 256, 
	257, 258, 259, 266, 267, 258, 259, 266, 
	267, 260, 332, 261, 262, 263, 332, 261, 
	264, 265, 263, 264, 265, 263, 332, 261, 
	258, 259, 268, 0, 332, 334, 269, 334, 
	270, 335, 271, 286, 272, 273, 274, 275, 
	276, 277, 334, 278, 279, 277, 334, 278, 
	279, 280, 283, 281, 282, 283, 284, 285, 
	282, 284, 285, 282, 283, 287, 288, 289, 
	290, 291, 292, 291, 292, 293, 304, 317, 
	294, 295, 302, 303, 294, 295, 302, 303, 
	296, 334, 297, 298, 299, 334, 297, 300, 
	301, 299, 300, 301, 299, 334, 297, 294, 
	295, 305, 306, 307, 308, 309, 310, 311, 
	312, 313, 314, 313, 314, 315, 334, 316, 
	318, 319, 320, 321, 321, 322, 323, 324, 
	325, 326, 327, 326, 327, 328, 334, 329, 
	331, 331, 332, 334
};

static const short _group_lines_test_trans_actions_wi[] = {
	77, 0, 89, 0, 222, 0, 0, 0, 
	65, 0, 152, 37, 0, 0, 0, 0, 
	0, 23, 3, 0, 0, 0, 0, 0, 
	3, 25, 0, 0, 0, 0, 0, 0, 
	27, 3, 0, 0, 0, 0, 0, 29, 
	3, 0, 0, 0, 0, 0, 31, 3, 
	0, 158, 0, 0, 210, 312, 210, 15, 
	134, 0, 0, 17, 143, 306, 143, 0, 
	9, 101, 3, 0, 9, 98, 3, 0, 
	9, 95, 3, 0, 0, 0, 35, 0, 
	0, 0, 33, 218, 33, 3, 0, 83, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 3, 0, 0, 
	162, 0, 7, 0, 0, 0, 0, 0, 
	137, 214, 15, 134, 0, 41, 0, 17, 
	0, 0, 104, 104, 11, 13, 107, 11, 
	0, 43, 0, 104, 104, 11, 13, 110, 
	11, 0, 45, 0, 104, 104, 11, 13, 
	113, 11, 0, 47, 0, 104, 104, 11, 
	13, 116, 11, 0, 49, 0, 0, 104, 
	104, 11, 13, 119, 11, 0, 51, 0, 
	0, 104, 104, 11, 13, 122, 11, 0, 
	53, 0, 104, 104, 11, 13, 125, 11, 
	0, 55, 0, 104, 104, 11, 13, 128, 
	11, 0, 57, 0, 0, 104, 104, 11, 
	13, 131, 11, 0, 59, 0, 182, 0, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 19, 146, 0, 0, 0, 
	0, 0, 67, 260, 67, 67, 0, 198, 
	0, 0, 0, 0, 0, 137, 137, 15, 
	134, 0, 0, 17, 19, 19, 0, 0, 
	0, 0, 61, 61, 0, 0, 0, 137, 
	137, 15, 134, 0, 0, 0, 17, 0, 
	186, 0, 0, 140, 288, 140, 15, 134, 
	0, 0, 17, 21, 245, 21, 19, 19, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 137, 15, 134, 137, 
	0, 0, 17, 0, 19, 19, 0, 140, 
	270, 140, 15, 134, 0, 166, 0, 0, 
	17, 21, 230, 21, 0, 0, 0, 0, 
	0, 0, 137, 15, 134, 137, 0, 0, 
	17, 0, 19, 19, 0, 140, 282, 140, 
	15, 134, 0, 174, 0, 0, 17, 21, 
	240, 21, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 137, 15, 134, 137, 
	0, 0, 17, 0, 19, 19, 0, 140, 
	300, 140, 15, 134, 0, 206, 0, 0, 
	17, 21, 255, 21, 0, 0, 0, 0, 
	0, 137, 137, 15, 134, 0, 0, 0, 
	17, 0, 170, 0, 0, 140, 276, 140, 
	15, 134, 0, 0, 17, 21, 235, 21, 
	19, 19, 0, 0, 86, 81, 0, 92, 
	0, 226, 65, 63, 0, 0, 0, 0, 
	0, 67, 265, 67, 67, 0, 202, 0, 
	0, 0, 0, 0, 137, 137, 15, 134, 
	0, 0, 17, 19, 19, 0, 0, 0, 
	0, 149, 149, 0, 0, 0, 0, 0, 
	137, 137, 15, 134, 0, 0, 0, 17, 
	0, 190, 0, 0, 140, 294, 140, 15, 
	134, 0, 0, 17, 21, 250, 21, 19, 
	19, 134, 17, 17, 17, 17, 17, 17, 
	17, 19, 19, 0, 0, 0, 194, 0, 
	134, 17, 17, 19, 0, 17, 17, 17, 
	17, 19, 19, 0, 0, 0, 178, 0, 
	69, 0, 75, 79
};

static const short _group_lines_test_to_state_actions[] = {
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 39, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 71, 71, 155, 0, 155, 0
};

static const short _group_lines_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 73, 0, 73, 0
};

static const short _group_lines_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 69, 0, 0, 0, 0, 0
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
	1, 1, 1, 1, 0, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 430, 430, 430, 430, 430, 430, 
	430, 430, 0, 0, 0, 531, 0, 532
};

static const int group_lines_test_start = 330;
static const int group_lines_test_first_final = 330;
static const int group_lines_test_error = 0;

static const int group_lines_test_en_group_scanner = 332;
static const int group_lines_test_en_mini_group_scanner = 334;
static const int group_lines_test_en_main = 330;

#line 870 "NanorexMMPImportExportRagelTest.rl"
	
#line 6269 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = group_lines_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 871 "NanorexMMPImportExportRagelTest.rl"
	
#line 6279 "NanorexMMPImportExportRagelTest.cpp"
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
	case 54:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 6300 "NanorexMMPImportExportRagelTest.cpp"
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
	_trans = _group_lines_test_indicies[_trans];
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
#line 53 "NanorexMMPImportExportRagelTest.rl"
	{stringVal.clear(); /*stringVal = stringVal + fc;*/ doubleVal = HUGE_VAL;}
	break;
	case 7:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{stringVal = stringVal + (*p);}
	break;
	case 8:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{doubleVal = atof(stringVal.c_str());}
	break;
	case 9:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 10:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 11:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 12:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 13:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 14:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 20:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 22:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 23:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 24:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 26:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 27:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 28:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 29:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 30:
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 31:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{csysViewName = stringVal;}
	break;
	case 32:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{csysQw=doubleVal;}
	break;
	case 33:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{csysQx=doubleVal;}
	break;
	case 34:
#line 42 "NanorexMMPImportExportRagelTest.rl"
	{csysQy=doubleVal;}
	break;
	case 35:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{csysQz=doubleVal;}
	break;
	case 36:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{csysScale=doubleVal;}
	break;
	case 37:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{csysPovX=doubleVal;}
	break;
	case 38:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{csysPovY=doubleVal;}
	break;
	case 39:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{csysPovZ=doubleVal;}
	break;
	case 40:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{csysZoomFactor=doubleVal;}
	break;
	case 41:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{ newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
	break;
	case 42:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 43:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 44:
#line 78 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 45:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 46:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 47:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 48:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 49:
#line 98 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 50:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 51:
#line 854 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 334; goto _again;} }
	break;
	case 55:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 56:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{act = 12;}
	break;
	case 57:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 58:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 59:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 60:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 61:
#line 120 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 62:
#line 121 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 63:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 64:
#line 123 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 65:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 66:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 67:
#line 128 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 68:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 69:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 70:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 12:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
	case 71:
#line 851 "NanorexMMPImportExportRagelTest.rl"
	{act = 17;}
	break;
	case 72:
#line 842 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 73:
#line 843 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 74:
#line 844 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 75:
#line 845 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 76:
#line 851 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 77:
#line 851 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 78:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 17:
	{{p = ((te))-1;}/*cerr << "Ignored line, p = " << p << endl;*/}
	break;
	default: break;
	}
	}
	break;
#line 6705 "NanorexMMPImportExportRagelTest.cpp"
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
	case 25:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 52:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 53:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 6734 "NanorexMMPImportExportRagelTest.cpp"
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
	case 51:
#line 854 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 334; goto _again;} }
	break;
#line 6757 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 872 "NanorexMMPImportExportRagelTest.rl"
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


#line 1019 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::uncheckedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 1032 "NanorexMMPImportExportRagelTest.rl"
	
#line 6910 "NanorexMMPImportExportRagelTest.cpp"
static const char _unchecked_parse_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 11, 1, 
	12, 1, 13, 1, 14, 1, 15, 1, 
	16, 1, 17, 1, 20, 1, 21, 1, 
	24, 1, 25, 1, 29, 1, 31, 1, 
	32, 1, 33, 1, 34, 1, 35, 1, 
	36, 1, 37, 1, 38, 1, 39, 1, 
	40, 1, 42, 1, 45, 1, 47, 1, 
	48, 1, 55, 1, 57, 1, 72, 1, 
	73, 2, 0, 44, 2, 0, 68, 2, 
	0, 70, 2, 0, 71, 2, 5, 15, 
	2, 5, 16, 2, 5, 17, 2, 6, 
	7, 2, 8, 32, 2, 8, 33, 2, 
	8, 34, 2, 8, 35, 2, 8, 36, 
	2, 8, 37, 2, 8, 38, 2, 8, 
	39, 2, 8, 40, 2, 9, 10, 2, 
	9, 11, 2, 9, 12, 2, 11, 18, 
	2, 11, 31, 2, 50, 27, 2, 55, 
	56, 3, 0, 19, 66, 3, 0, 22, 
	69, 3, 0, 23, 67, 3, 0, 26, 
	64, 3, 0, 28, 65, 3, 0, 30, 
	52, 3, 0, 41, 60, 3, 0, 43, 
	53, 3, 0, 43, 61, 3, 0, 46, 
	54, 3, 0, 49, 63, 3, 0, 51, 
	62, 3, 9, 11, 18, 3, 9, 11, 
	31, 3, 20, 0, 68, 3, 58, 0, 
	59, 4, 12, 0, 23, 67, 4, 12, 
	0, 26, 64, 4, 12, 0, 28, 65, 
	4, 12, 0, 43, 53, 4, 12, 0, 
	43, 61, 4, 12, 0, 51, 62, 4, 
	48, 0, 49, 63, 5, 9, 12, 0, 
	23, 67, 5, 9, 12, 0, 26, 64, 
	5, 9, 12, 0, 28, 65, 5, 9, 
	12, 0, 43, 53, 5, 9, 12, 0, 
	43, 61, 5, 9, 12, 0, 51, 62, 
	5, 11, 18, 0, 19, 66, 6, 9, 
	11, 18, 0, 19, 66
};

static const short _unchecked_parse_test_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 14, 
	19, 24, 25, 26, 27, 31, 36, 37, 
	38, 39, 44, 49, 54, 55, 56, 57, 
	58, 63, 68, 79, 93, 107, 112, 124, 
	129, 130, 131, 132, 137, 142, 143, 144, 
	145, 146, 151, 156, 157, 158, 159, 160, 
	161, 162, 163, 164, 169, 174, 176, 178, 
	180, 194, 208, 221, 235, 248, 262, 264, 
	266, 278, 281, 284, 287, 292, 299, 306, 
	312, 319, 327, 333, 338, 344, 353, 357, 
	365, 371, 380, 384, 392, 398, 407, 411, 
	419, 425, 431, 444, 446, 461, 476, 490, 
	505, 513, 517, 525, 533, 541, 545, 553, 
	561, 569, 573, 581, 589, 597, 604, 607, 
	610, 613, 621, 626, 633, 641, 649, 651, 
	659, 662, 665, 668, 671, 674, 677, 680, 
	683, 686, 691, 698, 705, 712, 720, 726, 
	728, 736, 743, 746, 749, 752, 758, 770, 
	785, 800, 806, 815, 819, 828, 834, 843, 
	847, 856, 862, 871, 875, 884, 890, 899, 
	903, 912, 918, 924, 933, 937, 946, 952, 
	958, 967, 971, 980, 986, 995, 999, 1008, 
	1014, 1023, 1027, 1036, 1042, 1048, 1057, 1061, 
	1070, 1076, 1082, 1084, 1094, 1100, 1104, 1112, 
	1122, 1128, 1132, 1140, 1150, 1156, 1160, 1168, 
	1178, 1184, 1188, 1196, 1206, 1212, 1216, 1224, 
	1234, 1240, 1244, 1252, 1262, 1268, 1272, 1280, 
	1290, 1296, 1300, 1308, 1318, 1324, 1328, 1336, 
	1350, 1365, 1368, 1371, 1374, 1377, 1380, 1387, 
	1394, 1396, 1409, 1421, 1436, 1451, 1457, 1471, 
	1486, 1489, 1492, 1495, 1498, 1504, 1510, 1522, 
	1537, 1552, 1558, 1571, 1573, 1588, 1603, 1617, 
	1632, 1646, 1661, 1664, 1667, 1670, 1675, 1683, 
	1686, 1689, 1692, 1697, 1709, 1724, 1739, 1753, 
	1768, 1780, 1795, 1810, 1812, 1826, 1841, 1844, 
	1847, 1850, 1853, 1858, 1870, 1885, 1900, 1914, 
	1929, 1941, 1956, 1971, 1973, 1987, 2002, 2005, 
	2008, 2011, 2014, 2017, 2020, 2023, 2026, 2031, 
	2043, 2058, 2073, 2087, 2102, 2114, 2129, 2144, 
	2146, 2160, 2175, 2178, 2181, 2186, 2192, 2204, 
	2219, 2234, 2240, 2253, 2255, 2270, 2285, 2299, 
	2314, 2328, 2343, 2345, 2345, 2358
};

static const char _unchecked_parse_test_trans_keys[] = {
	10, 32, 103, 9, 13, 114, 111, 117, 
	112, 9, 32, 40, 11, 13, 9, 32, 
	40, 11, 13, 9, 32, 86, 11, 13, 
	105, 101, 119, 9, 32, 11, 13, 9, 
	32, 68, 11, 13, 97, 116, 97, 9, 
	32, 41, 11, 13, 10, 32, 35, 9, 
	13, 10, 32, 103, 9, 13, 114, 111, 
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
	13, 10, 32, 103, 9, 13, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 67, 11, 13, 108, 105, 112, 98, 
	111, 97, 114, 100, 9, 32, 41, 11, 
	13, 10, 32, 35, 9, 13, -1, 10, 
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
	-1, 10, -1, 10, 32, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	116, -1, 10, 111, -1, 10, 109, -1, 
	10, 32, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 111, -1, 
	10, 110, -1, 10, 100, -1, 10, 95, 
	97, 99, 103, 49, 51, -1, 10, 32, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 100, -1, 10, 
	105, -1, 10, 114, -1, 10, 101, -1, 
	10, 99, -1, 10, 116, -1, 10, 105, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	32, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 115, -1, 10, 121, -1, 10, 115, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 46, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 46, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 46, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 46, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 103, 
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
	10, -1, 10, 32, 35, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	32, 97, 98, 99, 101, 103, 105, 109, 
	9, 13, 0
};

static const char _unchecked_parse_test_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 3, 3, 
	3, 1, 1, 1, 2, 3, 1, 1, 
	1, 3, 3, 3, 1, 1, 1, 1, 
	3, 3, 3, 4, 4, 3, 4, 3, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 3, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 3, 2, 2, 2, 
	4, 4, 3, 4, 3, 4, 2, 2, 
	10, 3, 3, 3, 3, 3, 3, 4, 
	3, 4, 4, 3, 4, 5, 2, 4, 
	4, 5, 2, 4, 4, 5, 2, 4, 
	4, 4, 5, 2, 5, 5, 4, 5, 
	4, 2, 4, 4, 4, 2, 4, 4, 
	4, 2, 4, 4, 4, 3, 3, 3, 
	3, 6, 3, 3, 4, 4, 2, 4, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 3, 4, 4, 2, 
	4, 3, 3, 3, 3, 4, 4, 5, 
	5, 4, 5, 2, 5, 4, 5, 2, 
	5, 4, 5, 2, 5, 4, 5, 2, 
	5, 4, 4, 5, 2, 5, 4, 4, 
	5, 2, 5, 4, 5, 2, 5, 4, 
	5, 2, 5, 4, 4, 5, 2, 5, 
	4, 4, 2, 6, 4, 2, 4, 6, 
	4, 2, 4, 6, 4, 2, 4, 6, 
	4, 2, 4, 6, 4, 2, 4, 6, 
	4, 2, 4, 6, 4, 2, 4, 6, 
	4, 2, 4, 6, 4, 2, 4, 4, 
	5, 3, 3, 3, 3, 3, 5, 5, 
	2, 5, 4, 5, 5, 4, 4, 5, 
	3, 3, 3, 3, 4, 4, 4, 5, 
	5, 4, 5, 2, 5, 5, 4, 5, 
	4, 5, 3, 3, 3, 3, 6, 3, 
	3, 3, 3, 4, 5, 5, 4, 5, 
	4, 5, 5, 2, 4, 5, 3, 3, 
	3, 3, 3, 4, 5, 5, 4, 5, 
	4, 5, 5, 2, 4, 5, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 4, 
	5, 5, 4, 5, 4, 5, 5, 2, 
	4, 5, 3, 3, 3, 4, 4, 5, 
	5, 4, 5, 2, 5, 5, 4, 5, 
	4, 5, 2, 0, 11, 10
};

static const char _unchecked_parse_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 1, 1, 
	1, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 1, 1, 0, 0, 0, 0, 
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
	2, 2, 0, 0, 0, 1, 4, 5, 
	5, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 2, 1, 2, 1, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 1, 0, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 2, 
	1, 1, 2, 2, 1, 1, 2, 5, 
	5, 0, 0, 0, 0, 0, 1, 1, 
	0, 4, 4, 5, 5, 1, 5, 5, 
	0, 0, 0, 0, 1, 1, 4, 5, 
	5, 1, 4, 0, 5, 5, 5, 5, 
	5, 5, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 5, 5, 5, 5, 
	4, 5, 5, 0, 5, 5, 0, 0, 
	0, 0, 1, 4, 5, 5, 5, 5, 
	4, 5, 5, 0, 5, 5, 0, 0, 
	0, 0, 0, 0, 0, 0, 1, 4, 
	5, 5, 5, 5, 4, 5, 5, 0, 
	5, 5, 0, 0, 1, 1, 4, 5, 
	5, 1, 4, 0, 5, 5, 5, 5, 
	5, 5, 0, 0, 1, 1
};

static const short _unchecked_parse_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 18, 
	23, 28, 30, 32, 34, 38, 43, 45, 
	47, 49, 54, 59, 64, 66, 68, 70, 
	72, 77, 82, 90, 100, 110, 115, 124, 
	129, 131, 133, 135, 140, 145, 147, 149, 
	151, 153, 158, 163, 165, 167, 169, 171, 
	173, 175, 177, 179, 184, 189, 192, 195, 
	198, 208, 218, 227, 237, 246, 256, 259, 
	262, 274, 278, 282, 286, 291, 297, 303, 
	309, 315, 322, 328, 333, 339, 347, 351, 
	358, 364, 372, 376, 383, 389, 397, 401, 
	408, 414, 420, 430, 433, 444, 455, 465, 
	476, 483, 487, 494, 501, 508, 512, 519, 
	526, 533, 537, 544, 551, 558, 564, 568, 
	572, 576, 584, 589, 595, 602, 609, 612, 
	619, 623, 627, 631, 635, 639, 643, 647, 
	651, 655, 660, 666, 672, 678, 685, 691, 
	694, 701, 707, 711, 715, 719, 725, 734, 
	745, 756, 762, 770, 774, 782, 788, 796, 
	800, 808, 814, 822, 826, 834, 840, 848, 
	852, 860, 866, 872, 880, 884, 892, 898, 
	904, 912, 916, 924, 930, 938, 942, 950, 
	956, 964, 968, 976, 982, 988, 996, 1000, 
	1008, 1014, 1020, 1023, 1032, 1038, 1042, 1049, 
	1058, 1064, 1068, 1075, 1084, 1090, 1094, 1101, 
	1110, 1116, 1120, 1127, 1136, 1142, 1146, 1153, 
	1162, 1168, 1172, 1179, 1188, 1194, 1198, 1205, 
	1214, 1220, 1224, 1231, 1240, 1246, 1250, 1257, 
	1267, 1278, 1282, 1286, 1290, 1294, 1298, 1305, 
	1312, 1315, 1325, 1334, 1345, 1356, 1362, 1372, 
	1383, 1387, 1391, 1395, 1399, 1405, 1411, 1420, 
	1431, 1442, 1448, 1458, 1461, 1472, 1483, 1493, 
	1504, 1514, 1525, 1529, 1533, 1537, 1542, 1550, 
	1554, 1558, 1562, 1567, 1576, 1587, 1598, 1608, 
	1619, 1628, 1639, 1650, 1653, 1663, 1674, 1678, 
	1682, 1686, 1690, 1695, 1704, 1715, 1726, 1736, 
	1747, 1756, 1767, 1778, 1781, 1791, 1802, 1806, 
	1810, 1814, 1818, 1822, 1826, 1830, 1834, 1839, 
	1848, 1859, 1870, 1880, 1891, 1900, 1911, 1922, 
	1925, 1935, 1946, 1950, 1954, 1959, 1965, 1974, 
	1985, 1996, 2002, 2012, 2015, 2026, 2037, 2047, 
	2058, 2068, 2079, 2082, 2083, 2096
};

static const short _unchecked_parse_test_indicies[] = {
	2, 0, 3, 0, 1, 4, 1, 5, 
	1, 6, 1, 7, 1, 8, 8, 9, 
	8, 1, 10, 10, 11, 10, 1, 11, 
	11, 12, 11, 1, 13, 1, 14, 1, 
	15, 1, 16, 16, 16, 1, 16, 16, 
	17, 16, 1, 18, 1, 19, 1, 20, 
	1, 20, 20, 21, 20, 1, 22, 21, 
	23, 21, 1, 25, 24, 26, 24, 1, 
	27, 1, 28, 1, 29, 1, 30, 1, 
	31, 31, 32, 31, 1, 33, 33, 34, 
	33, 1, 34, 34, 35, 34, 35, 35, 
	35, 1, 36, 36, 37, 39, 36, 38, 
	39, 39, 39, 1, 40, 40, 41, 43, 
	40, 42, 43, 43, 43, 1, 45, 44, 
	46, 44, 1, 45, 44, 46, 47, 44, 
	47, 47, 47, 1, 49, 48, 50, 48, 
	1, 51, 1, 52, 1, 53, 1, 54, 
	53, 55, 53, 1, 57, 56, 58, 56, 
	1, 59, 1, 60, 1, 61, 1, 62, 
	1, 62, 62, 63, 62, 1, 63, 63, 
	64, 63, 1, 65, 1, 66, 1, 67, 
	1, 68, 1, 69, 1, 70, 1, 71, 
	1, 72, 1, 72, 72, 73, 72, 1, 
	74, 73, 75, 73, 1, 1, 74, 75, 
	1, 54, 55, 1, 45, 46, 77, 76, 
	78, 80, 76, 79, 80, 80, 80, 1, 
	45, 81, 46, 83, 81, 82, 83, 83, 
	83, 1, 82, 82, 83, 82, 82, 83, 
	83, 83, 1, 85, 84, 86, 83, 84, 
	82, 83, 83, 83, 1, 42, 42, 43, 
	42, 42, 43, 43, 43, 1, 87, 87, 
	88, 43, 87, 42, 43, 43, 43, 1, 
	1, 22, 23, 89, 91, 90, 89, 93, 
	92, 94, 95, 96, 97, 98, 99, 100, 
	92, 90, 89, 91, 101, 90, 89, 91, 
	102, 90, 89, 91, 103, 90, 89, 91, 
	104, 104, 90, 89, 91, 104, 104, 105, 
	90, 89, 91, 106, 106, 107, 90, 89, 
	91, 108, 109, 108, 90, 89, 91, 109, 
	109, 110, 90, 89, 91, 111, 112, 111, 
	113, 90, 89, 91, 111, 112, 111, 90, 
	89, 91, 114, 114, 90, 89, 91, 115, 
	116, 115, 90, 89, 91, 116, 117, 118, 
	116, 119, 90, 89, 91, 119, 90, 89, 
	91, 120, 121, 120, 122, 90, 89, 91, 
	120, 121, 120, 90, 89, 91, 123, 124, 
	125, 123, 126, 90, 89, 91, 126, 90, 
	89, 91, 127, 128, 127, 129, 90, 89, 
	91, 127, 128, 127, 90, 89, 91, 130, 
	131, 132, 130, 133, 90, 89, 91, 133, 
	90, 89, 91, 134, 135, 134, 136, 90, 
	89, 91, 134, 135, 134, 90, 89, 138, 
	137, 139, 137, 90, 89, 138, 137, 139, 
	140, 137, 140, 140, 140, 90, 89, 138, 
	139, 89, 142, 141, 143, 145, 141, 144, 
	145, 145, 145, 90, 89, 138, 146, 139, 
	148, 146, 147, 148, 148, 148, 90, 89, 
	91, 147, 148, 147, 147, 148, 148, 148, 
	90, 89, 150, 149, 151, 148, 149, 147, 
	148, 148, 148, 90, 89, 91, 134, 135, 
	134, 136, 90, 89, 91, 152, 90, 89, 
	91, 153, 154, 153, 155, 90, 89, 91, 
	153, 154, 153, 155, 90, 89, 91, 127, 
	128, 127, 129, 90, 89, 91, 156, 90, 
	89, 91, 157, 158, 157, 159, 90, 89, 
	91, 157, 158, 157, 159, 90, 89, 91, 
	120, 121, 120, 122, 90, 89, 91, 160, 
	90, 89, 91, 161, 162, 161, 163, 90, 
	89, 91, 161, 162, 161, 163, 90, 89, 
	91, 111, 112, 111, 113, 90, 89, 91, 
	106, 106, 107, 90, 89, 91, 164, 90, 
	89, 91, 165, 90, 89, 91, 166, 90, 
	89, 91, 168, 167, 167, 167, 167, 90, 
	89, 91, 169, 169, 90, 89, 91, 169, 
	169, 170, 90, 89, 172, 171, 173, 171, 
	174, 90, 89, 176, 175, 177, 175, 170, 
	90, 89, 176, 177, 89, 172, 171, 173, 
	171, 174, 90, 89, 91, 178, 90, 89, 
	91, 179, 90, 89, 91, 180, 90, 89, 
	91, 181, 90, 89, 91, 182, 90, 89, 
	91, 183, 90, 89, 91, 184, 90, 89, 
	91, 185, 90, 89, 91, 186, 90, 89, 
	91, 187, 187, 90, 89, 91, 187, 187, 
	188, 90, 89, 91, 189, 189, 190, 90, 
	89, 91, 189, 189, 191, 90, 89, 193, 
	192, 194, 192, 195, 90, 89, 193, 192, 
	194, 192, 90, 89, 193, 194, 89, 193, 
	192, 194, 192, 195, 90, 89, 91, 189, 
	189, 190, 90, 89, 91, 196, 90, 89, 
	91, 197, 90, 89, 91, 198, 90, 89, 
	91, 198, 199, 198, 90, 89, 91, 199, 
	200, 199, 200, 200, 200, 90, 89, 91, 
	201, 202, 204, 201, 203, 204, 204, 204, 
	90, 89, 91, 205, 206, 208, 205, 207, 
	208, 208, 208, 90, 89, 91, 209, 210, 
	209, 90, 89, 91, 210, 211, 211, 210, 
	212, 90, 89, 91, 213, 90, 89, 91, 
	214, 215, 216, 214, 213, 90, 89, 91, 
	217, 218, 217, 90, 89, 91, 219, 220, 
	220, 219, 221, 90, 89, 91, 222, 90, 
	89, 91, 223, 224, 225, 223, 222, 90, 
	89, 91, 226, 227, 226, 90, 89, 91, 
	228, 229, 229, 228, 230, 90, 89, 91, 
	231, 90, 89, 91, 232, 233, 234, 232, 
	231, 90, 89, 91, 235, 236, 235, 90, 
	89, 91, 237, 238, 238, 237, 239, 90, 
	89, 91, 240, 90, 89, 91, 241, 242, 
	243, 241, 240, 90, 89, 91, 244, 245, 
	244, 90, 89, 91, 246, 247, 246, 90, 
	89, 91, 247, 248, 248, 247, 249, 90, 
	89, 91, 250, 90, 89, 91, 251, 252, 
	253, 251, 250, 90, 89, 91, 254, 255, 
	254, 90, 89, 91, 256, 257, 256, 90, 
	89, 91, 257, 258, 258, 257, 259, 90, 
	89, 91, 260, 90, 89, 91, 261, 262, 
	263, 261, 260, 90, 89, 91, 264, 265, 
	264, 90, 89, 91, 266, 267, 267, 266, 
	268, 90, 89, 91, 269, 90, 89, 91, 
	270, 271, 272, 270, 269, 90, 89, 91, 
	273, 274, 273, 90, 89, 91, 275, 276, 
	276, 275, 277, 90, 89, 91, 278, 90, 
	89, 91, 279, 280, 281, 279, 278, 90, 
	89, 91, 282, 283, 282, 90, 89, 91, 
	284, 285, 284, 90, 89, 91, 285, 286, 
	286, 285, 287, 90, 89, 91, 288, 90, 
	89, 91, 289, 290, 291, 289, 288, 90, 
	89, 91, 292, 293, 292, 90, 89, 295, 
	294, 296, 294, 90, 89, 295, 296, 89, 
	91, 289, 290, 297, 297, 289, 291, 90, 
	89, 91, 298, 298, 299, 90, 89, 91, 
	299, 90, 89, 91, 289, 290, 289, 299, 
	90, 89, 91, 279, 280, 300, 300, 279, 
	281, 90, 89, 91, 301, 301, 302, 90, 
	89, 91, 302, 90, 89, 91, 279, 280, 
	279, 302, 90, 89, 91, 270, 271, 303, 
	303, 270, 272, 90, 89, 91, 304, 304, 
	305, 90, 89, 91, 305, 90, 89, 91, 
	270, 271, 270, 305, 90, 89, 91, 261, 
	262, 306, 306, 261, 263, 90, 89, 91, 
	307, 307, 308, 90, 89, 91, 308, 90, 
	89, 91, 261, 262, 261, 308, 90, 89, 
	91, 251, 252, 309, 309, 251, 253, 90, 
	89, 91, 310, 310, 311, 90, 89, 91, 
	311, 90, 89, 91, 251, 252, 251, 311, 
	90, 89, 91, 241, 242, 312, 312, 241, 
	243, 90, 89, 91, 313, 313, 314, 90, 
	89, 91, 314, 90, 89, 91, 241, 242, 
	241, 314, 90, 89, 91, 232, 233, 315, 
	315, 232, 234, 90, 89, 91, 316, 316, 
	317, 90, 89, 91, 317, 90, 89, 91, 
	232, 233, 232, 317, 90, 89, 91, 223, 
	224, 318, 318, 223, 225, 90, 89, 91, 
	319, 319, 320, 90, 89, 91, 320, 90, 
	89, 91, 223, 224, 223, 320, 90, 89, 
	91, 214, 215, 321, 321, 214, 216, 90, 
	89, 91, 322, 322, 323, 90, 89, 91, 
	323, 90, 89, 91, 214, 215, 214, 323, 
	90, 89, 91, 207, 208, 207, 207, 208, 
	208, 208, 90, 89, 91, 324, 325, 208, 
	324, 207, 208, 208, 208, 90, 89, 91, 
	326, 90, 89, 91, 327, 90, 89, 91, 
	328, 90, 89, 91, 329, 90, 89, 91, 
	330, 90, 89, 332, 331, 333, 334, 331, 
	90, 89, 336, 335, 337, 338, 335, 90, 
	89, 336, 337, 89, 91, 339, 340, 341, 
	339, 341, 341, 341, 90, 89, 91, 339, 
	341, 339, 341, 341, 341, 90, 89, 91, 
	342, 343, 345, 342, 344, 345, 345, 345, 
	90, 89, 91, 346, 340, 348, 346, 347, 
	348, 348, 348, 90, 89, 336, 340, 337, 
	340, 90, 89, 91, 347, 348, 347, 347, 
	348, 348, 348, 90, 89, 91, 349, 350, 
	348, 349, 347, 348, 348, 348, 90, 89, 
	91, 351, 90, 89, 91, 352, 90, 89, 
	91, 353, 90, 89, 91, 354, 90, 89, 
	91, 355, 356, 355, 90, 89, 91, 357, 
	358, 357, 90, 89, 91, 358, 359, 358, 
	359, 359, 359, 90, 89, 91, 360, 361, 
	363, 360, 362, 363, 363, 363, 90, 89, 
	91, 364, 365, 367, 364, 366, 367, 367, 
	367, 90, 89, 369, 368, 370, 368, 90, 
	89, 369, 368, 370, 371, 368, 371, 371, 
	371, 90, 89, 369, 370, 89, 373, 372, 
	374, 376, 372, 375, 376, 376, 376, 90, 
	89, 369, 377, 370, 379, 377, 378, 379, 
	379, 379, 90, 89, 91, 378, 379, 378, 
	378, 379, 379, 379, 90, 89, 381, 380, 
	382, 379, 380, 378, 379, 379, 379, 90, 
	89, 91, 366, 367, 366, 366, 367, 367, 
	367, 90, 89, 91, 383, 384, 367, 383, 
	366, 367, 367, 367, 90, 89, 91, 385, 
	90, 89, 91, 386, 90, 89, 91, 387, 
	90, 89, 91, 388, 388, 90, 89, 91, 
	388, 389, 390, 391, 388, 90, 89, 91, 
	392, 90, 89, 91, 393, 90, 89, 91, 
	394, 90, 89, 91, 395, 395, 90, 89, 
	91, 395, 396, 395, 396, 396, 396, 90, 
	89, 91, 397, 400, 399, 397, 398, 399, 
	399, 399, 90, 89, 91, 401, 404, 403, 
	401, 402, 403, 403, 403, 90, 89, 91, 
	402, 403, 402, 402, 403, 403, 403, 90, 
	89, 91, 405, 406, 403, 405, 402, 403, 
	403, 403, 90, 89, 91, 404, 407, 404, 
	407, 407, 407, 90, 89, 409, 408, 410, 
	412, 408, 411, 412, 412, 412, 90, 89, 
	414, 413, 415, 417, 413, 416, 417, 417, 
	417, 90, 89, 414, 415, 89, 91, 416, 
	417, 416, 416, 417, 417, 417, 90, 89, 
	419, 418, 420, 417, 418, 416, 417, 417, 
	417, 90, 89, 91, 421, 90, 89, 91, 
	422, 90, 89, 91, 423, 90, 89, 91, 
	424, 90, 89, 91, 425, 425, 90, 89, 
	91, 425, 426, 425, 426, 426, 426, 90, 
	89, 91, 427, 430, 429, 427, 428, 429, 
	429, 429, 90, 89, 91, 431, 434, 433, 
	431, 432, 433, 433, 433, 90, 89, 91, 
	432, 433, 432, 432, 433, 433, 433, 90, 
	89, 91, 435, 436, 433, 435, 432, 433, 
	433, 433, 90, 89, 91, 434, 437, 434, 
	437, 437, 437, 90, 89, 439, 438, 440, 
	442, 438, 441, 442, 442, 442, 90, 89, 
	444, 443, 445, 447, 443, 446, 447, 447, 
	447, 90, 89, 444, 445, 89, 91, 446, 
	447, 446, 446, 447, 447, 447, 90, 89, 
	449, 448, 450, 447, 448, 446, 447, 447, 
	447, 90, 89, 91, 451, 90, 89, 91, 
	452, 90, 89, 91, 453, 90, 89, 91, 
	454, 90, 89, 91, 455, 90, 89, 91, 
	456, 90, 89, 91, 457, 90, 89, 91, 
	458, 90, 89, 91, 459, 459, 90, 89, 
	91, 459, 460, 459, 460, 460, 460, 90, 
	89, 91, 461, 464, 463, 461, 462, 463, 
	463, 463, 90, 89, 91, 465, 468, 467, 
	465, 466, 467, 467, 467, 90, 89, 91, 
	466, 467, 466, 466, 467, 467, 467, 90, 
	89, 91, 469, 470, 467, 469, 466, 467, 
	467, 467, 90, 89, 91, 468, 471, 468, 
	471, 471, 471, 90, 89, 473, 472, 474, 
	476, 472, 475, 476, 476, 476, 90, 89, 
	478, 477, 479, 481, 477, 480, 481, 481, 
	481, 90, 89, 478, 479, 89, 91, 480, 
	481, 480, 480, 481, 481, 481, 90, 89, 
	483, 482, 484, 481, 482, 480, 481, 481, 
	481, 90, 89, 91, 485, 90, 89, 91, 
	486, 90, 89, 91, 487, 487, 90, 89, 
	91, 487, 488, 487, 90, 89, 91, 488, 
	489, 488, 489, 489, 489, 90, 89, 91, 
	490, 491, 493, 490, 492, 493, 493, 493, 
	90, 89, 91, 494, 495, 497, 494, 496, 
	497, 497, 497, 90, 89, 499, 498, 500, 
	498, 90, 89, 499, 498, 500, 501, 498, 
	501, 501, 501, 90, 89, 499, 500, 89, 
	503, 502, 504, 506, 502, 505, 506, 506, 
	506, 90, 89, 499, 507, 500, 509, 507, 
	508, 509, 509, 509, 90, 89, 91, 508, 
	509, 508, 508, 509, 509, 509, 90, 89, 
	511, 510, 512, 509, 510, 508, 509, 509, 
	509, 90, 89, 91, 496, 497, 496, 496, 
	497, 497, 497, 90, 89, 91, 513, 514, 
	497, 513, 496, 497, 497, 497, 90, 1, 
	516, 515, 517, 1, 93, 92, 515, 94, 
	95, 96, 97, 98, 99, 100, 92, 90, 
	518, 93, 92, 94, 95, 96, 97, 98, 
	99, 100, 92, 90, 0
};

static const short _unchecked_parse_test_trans_targs_wi[] = {
	1, 0, 1, 2, 3, 4, 5, 6, 
	7, 8, 7, 8, 9, 10, 11, 12, 
	13, 14, 15, 16, 17, 18, 19, 62, 
	19, 19, 20, 21, 22, 23, 24, 25, 
	26, 25, 26, 27, 28, 29, 60, 61, 
	28, 29, 60, 61, 30, 31, 55, 56, 
	31, 31, 32, 33, 34, 35, 36, 54, 
	36, 36, 37, 38, 39, 40, 41, 42, 
	43, 44, 45, 46, 47, 48, 49, 50, 
	51, 52, 331, 53, 57, 31, 55, 58, 
	59, 57, 58, 59, 57, 31, 55, 28, 
	29, 332, 63, 332, 64, 333, 65, 110, 
	138, 225, 240, 258, 314, 66, 67, 68, 
	69, 70, 71, 109, 71, 72, 73, 74, 
	75, 108, 76, 76, 77, 78, 105, 79, 
	80, 81, 104, 81, 82, 101, 83, 84, 
	85, 100, 85, 86, 97, 87, 88, 89, 
	96, 90, 332, 91, 92, 93, 332, 91, 
	94, 95, 93, 94, 95, 93, 332, 91, 
	98, 88, 89, 99, 102, 84, 85, 103, 
	106, 80, 81, 107, 111, 112, 113, 114, 
	120, 115, 116, 117, 332, 118, 119, 117, 
	332, 118, 121, 122, 123, 124, 125, 126, 
	127, 128, 129, 130, 131, 132, 137, 133, 
	134, 332, 135, 136, 139, 140, 141, 142, 
	143, 144, 145, 223, 224, 144, 145, 223, 
	224, 145, 146, 147, 148, 148, 149, 150, 
	219, 149, 150, 150, 151, 152, 152, 153, 
	154, 215, 153, 154, 154, 155, 156, 156, 
	157, 158, 211, 157, 158, 158, 159, 160, 
	160, 161, 162, 207, 161, 162, 162, 163, 
	164, 165, 165, 166, 167, 203, 166, 167, 
	167, 168, 169, 170, 170, 171, 172, 199, 
	171, 172, 172, 173, 174, 174, 175, 176, 
	195, 175, 176, 176, 177, 178, 178, 179, 
	180, 191, 179, 180, 180, 181, 182, 183, 
	183, 184, 185, 187, 184, 185, 185, 332, 
	186, 188, 189, 190, 192, 193, 194, 196, 
	197, 198, 200, 201, 202, 204, 205, 206, 
	208, 209, 210, 212, 213, 214, 216, 217, 
	218, 220, 221, 222, 144, 145, 226, 227, 
	228, 229, 230, 231, 332, 232, 233, 231, 
	332, 232, 233, 234, 237, 235, 236, 237, 
	238, 239, 236, 238, 239, 236, 237, 241, 
	242, 243, 244, 245, 246, 245, 246, 247, 
	248, 249, 256, 257, 248, 249, 256, 257, 
	250, 332, 251, 252, 253, 332, 251, 254, 
	255, 253, 254, 255, 253, 332, 251, 248, 
	249, 259, 260, 261, 262, 263, 278, 294, 
	264, 265, 266, 267, 268, 269, 270, 271, 
	272, 269, 270, 271, 272, 269, 272, 273, 
	274, 332, 275, 276, 277, 274, 332, 275, 
	276, 277, 274, 332, 275, 279, 280, 281, 
	282, 283, 284, 285, 286, 287, 288, 285, 
	286, 287, 288, 285, 288, 289, 290, 332, 
	291, 292, 293, 290, 332, 291, 292, 293, 
	290, 332, 291, 295, 296, 297, 298, 299, 
	300, 301, 302, 303, 304, 305, 306, 307, 
	308, 305, 306, 307, 308, 305, 308, 309, 
	310, 332, 311, 312, 313, 310, 332, 311, 
	312, 313, 310, 332, 311, 315, 316, 317, 
	318, 319, 320, 321, 328, 329, 320, 321, 
	328, 329, 322, 332, 323, 324, 325, 332, 
	323, 326, 327, 325, 326, 327, 325, 332, 
	323, 320, 321, 330, 332, 331, 332
};

static const short _unchecked_parse_test_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	43, 43, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 173, 0, 
	0, 1, 0, 0, 0, 0, 0, 65, 
	65, 0, 0, 0, 135, 135, 17, 132, 
	0, 0, 0, 19, 0, 181, 0, 0, 
	0, 1, 0, 0, 0, 0, 81, 0, 
	0, 1, 67, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 189, 0, 138, 270, 138, 17, 
	132, 0, 0, 19, 23, 232, 23, 21, 
	21, 79, 0, 90, 0, 213, 0, 0, 
	0, 69, 0, 147, 39, 0, 0, 0, 
	0, 0, 25, 5, 0, 0, 0, 0, 
	0, 5, 27, 0, 0, 0, 0, 0, 
	0, 29, 5, 0, 0, 0, 0, 0, 
	31, 5, 0, 0, 0, 0, 0, 33, 
	5, 0, 153, 0, 0, 201, 294, 201, 
	17, 132, 0, 0, 19, 141, 288, 141, 
	0, 11, 99, 5, 0, 11, 96, 5, 
	0, 11, 93, 5, 0, 0, 0, 37, 
	0, 0, 0, 35, 209, 35, 5, 0, 
	84, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 5, 0, 
	0, 157, 0, 9, 0, 0, 0, 0, 
	0, 135, 205, 17, 132, 0, 45, 0, 
	19, 0, 0, 102, 102, 13, 15, 105, 
	13, 0, 47, 0, 102, 102, 13, 15, 
	108, 13, 0, 49, 0, 102, 102, 13, 
	15, 111, 13, 0, 51, 0, 102, 102, 
	13, 15, 114, 13, 0, 53, 0, 0, 
	102, 102, 13, 15, 117, 13, 0, 55, 
	0, 0, 102, 102, 13, 15, 120, 13, 
	0, 57, 0, 102, 102, 13, 15, 123, 
	13, 0, 59, 0, 102, 102, 13, 15, 
	126, 13, 0, 61, 0, 0, 102, 102, 
	13, 15, 129, 13, 0, 63, 0, 177, 
	0, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 21, 144, 0, 0, 
	0, 0, 0, 71, 247, 71, 71, 0, 
	193, 0, 0, 0, 0, 0, 135, 135, 
	17, 132, 0, 0, 19, 21, 21, 0, 
	0, 0, 0, 65, 65, 0, 0, 0, 
	135, 135, 17, 132, 0, 0, 0, 19, 
	0, 185, 0, 0, 138, 276, 138, 17, 
	132, 0, 0, 19, 23, 237, 23, 21, 
	21, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 135, 17, 132, 
	135, 0, 0, 19, 0, 21, 21, 0, 
	138, 252, 138, 17, 132, 0, 161, 0, 
	0, 19, 23, 217, 23, 0, 0, 0, 
	0, 0, 0, 135, 17, 132, 135, 0, 
	0, 19, 0, 21, 21, 0, 138, 264, 
	138, 17, 132, 0, 169, 0, 0, 19, 
	23, 227, 23, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 135, 17, 132, 
	135, 0, 0, 19, 0, 21, 21, 0, 
	138, 282, 138, 17, 132, 0, 197, 0, 
	0, 19, 23, 242, 23, 0, 0, 0, 
	0, 0, 135, 135, 17, 132, 0, 0, 
	0, 19, 0, 165, 0, 0, 138, 258, 
	138, 17, 132, 0, 0, 19, 23, 222, 
	23, 21, 21, 0, 87, 0, 77
};

static const short _unchecked_parse_test_to_state_actions[] = {
	0, 73, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 73, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 73, 
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 41, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 73, 150, 0
};

static const short _unchecked_parse_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 75, 0
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
	90, 90, 0, 0, 0, 519
};

static const int unchecked_parse_test_start = 1;
static const int unchecked_parse_test_first_final = 331;
static const int unchecked_parse_test_error = 0;

static const int unchecked_parse_test_en_group_scanner = 332;
static const int unchecked_parse_test_en_main = 1;

#line 1033 "NanorexMMPImportExportRagelTest.rl"
	
#line 7979 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = unchecked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1034 "NanorexMMPImportExportRagelTest.rl"
	
#line 7989 "NanorexMMPImportExportRagelTest.cpp"
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
	case 57:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 8010 "NanorexMMPImportExportRagelTest.cpp"
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
	_trans = _unchecked_parse_test_indicies[_trans];
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
#line 53 "NanorexMMPImportExportRagelTest.rl"
	{stringVal.clear(); /*stringVal = stringVal + fc;*/ doubleVal = HUGE_VAL;}
	break;
	case 7:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{stringVal = stringVal + (*p);}
	break;
	case 8:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{doubleVal = atof(stringVal.c_str());}
	break;
	case 9:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 10:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 11:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 12:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 13:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 14:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 20:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 22:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 23:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 24:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 26:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 27:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 28:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 29:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 30:
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 31:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{csysViewName = stringVal;}
	break;
	case 32:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{csysQw=doubleVal;}
	break;
	case 33:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{csysQx=doubleVal;}
	break;
	case 34:
#line 42 "NanorexMMPImportExportRagelTest.rl"
	{csysQy=doubleVal;}
	break;
	case 35:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{csysQz=doubleVal;}
	break;
	case 36:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{csysScale=doubleVal;}
	break;
	case 37:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{csysPovX=doubleVal;}
	break;
	case 38:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{csysPovY=doubleVal;}
	break;
	case 39:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{csysPovZ=doubleVal;}
	break;
	case 40:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{csysZoomFactor=doubleVal;}
	break;
	case 41:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{ newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
	break;
	case 42:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 43:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 44:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 45:
#line 78 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 46:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 47:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 48:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 49:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 50:
#line 98 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 51:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 52:
#line 1008 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 332; goto _again;} }
	break;
	case 53:
#line 1011 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 332; goto _again;} }
	break;
	case 54:
#line 1016 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 332; goto _again;} }
	break;
	case 58:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 59:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{act = 12;}
	break;
	case 60:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 61:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 62:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 63:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 64:
#line 120 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 65:
#line 121 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 66:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 67:
#line 123 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 68:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 69:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 70:
#line 128 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 71:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 72:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 73:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 12:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 8386 "NanorexMMPImportExportRagelTest.cpp"
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
	case 25:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 55:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 56:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 8415 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1035 "NanorexMMPImportExportRagelTest.rl"
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


#line 1096 "NanorexMMPImportExportRagelTest.rl"



void
NanorexMMPImportExportRagelTest::checkedParseTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 1109 "NanorexMMPImportExportRagelTest.rl"
	
#line 8491 "NanorexMMPImportExportRagelTest.cpp"
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

#line 1110 "NanorexMMPImportExportRagelTest.rl"
	
#line 9855 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = checked_parse_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1111 "NanorexMMPImportExportRagelTest.rl"
	
#line 9865 "NanorexMMPImportExportRagelTest.cpp"
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
#line 9886 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1082 "NanorexMMPImportExportRagelTest.rl"
	{ cerr << "*p=" << *p << endl;
			p--;
			{stack[top++] = cs; cs = 411; goto _again;}
		}
	break;
	case 66:
#line 1088 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 411; goto _again;} }
	break;
	case 67:
#line 1093 "NanorexMMPImportExportRagelTest.rl"
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
#line 10302 "NanorexMMPImportExportRagelTest.cpp"
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
#line 10323 "NanorexMMPImportExportRagelTest.cpp"
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
#line 10430 "NanorexMMPImportExportRagelTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 1112 "NanorexMMPImportExportRagelTest.rl"
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


#line 1192 "NanorexMMPImportExportRagelTest.rl"



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
	
	#line 1279 "NanorexMMPImportExportRagelTest.rl"
	
#line 10561 "NanorexMMPImportExportRagelTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 11, 1, 
	12, 1, 13, 1, 14, 1, 15, 1, 
	16, 1, 17, 1, 20, 1, 21, 1, 
	24, 1, 25, 1, 29, 1, 31, 1, 
	32, 1, 33, 1, 34, 1, 35, 1, 
	36, 1, 37, 1, 38, 1, 39, 1, 
	40, 1, 42, 1, 45, 1, 47, 1, 
	48, 1, 52, 1, 56, 1, 58, 1, 
	73, 1, 74, 2, 0, 44, 2, 0, 
	69, 2, 0, 71, 2, 0, 72, 2, 
	5, 15, 2, 5, 16, 2, 5, 17, 
	2, 6, 7, 2, 8, 32, 2, 8, 
	33, 2, 8, 34, 2, 8, 35, 2, 
	8, 36, 2, 8, 37, 2, 8, 38, 
	2, 8, 39, 2, 8, 40, 2, 9, 
	10, 2, 9, 11, 2, 9, 12, 2, 
	11, 18, 2, 11, 31, 2, 50, 27, 
	2, 52, 0, 2, 56, 57, 3, 0, 
	19, 67, 3, 0, 22, 70, 3, 0, 
	23, 68, 3, 0, 26, 65, 3, 0, 
	28, 66, 3, 0, 30, 53, 3, 0, 
	41, 61, 3, 0, 43, 54, 3, 0, 
	43, 62, 3, 0, 46, 55, 3, 0, 
	49, 64, 3, 0, 51, 63, 3, 9, 
	11, 18, 3, 9, 11, 31, 3, 20, 
	0, 69, 3, 59, 0, 60, 4, 12, 
	0, 23, 68, 4, 12, 0, 26, 65, 
	4, 12, 0, 28, 66, 4, 12, 0, 
	43, 54, 4, 12, 0, 43, 62, 4, 
	12, 0, 51, 63, 4, 48, 0, 49, 
	64, 5, 9, 12, 0, 23, 68, 5, 
	9, 12, 0, 26, 65, 5, 9, 12, 
	0, 28, 66, 5, 9, 12, 0, 43, 
	54, 5, 9, 12, 0, 43, 62, 5, 
	9, 12, 0, 51, 63, 5, 11, 18, 
	0, 19, 67, 6, 9, 11, 18, 0, 
	19, 67
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 105, 110, 111, 
	112, 113, 114, 119, 124, 135, 149, 163, 
	168, 180, 185, 186, 187, 188, 193, 198, 
	199, 200, 201, 202, 207, 212, 213, 214, 
	215, 216, 217, 218, 219, 220, 225, 230, 
	235, 236, 237, 241, 243, 245, 247, 261, 
	275, 288, 302, 315, 329, 331, 332, 333, 
	334, 335, 336, 340, 346, 353, 358, 363, 
	365, 372, 374, 378, 384, 386, 388, 390, 
	392, 394, 398, 403, 404, 405, 406, 407, 
	408, 409, 410, 411, 416, 418, 430, 433, 
	436, 439, 444, 451, 458, 464, 471, 479, 
	485, 490, 496, 505, 509, 517, 523, 532, 
	536, 544, 550, 559, 563, 571, 577, 583, 
	596, 598, 613, 628, 642, 657, 665, 669, 
	677, 685, 693, 697, 705, 713, 721, 725, 
	733, 741, 749, 756, 759, 762, 765, 773, 
	778, 785, 793, 801, 803, 811, 814, 817, 
	820, 823, 826, 829, 832, 835, 838, 843, 
	850, 857, 864, 872, 878, 880, 888, 895, 
	898, 901, 904, 910, 922, 937, 952, 958, 
	967, 971, 980, 986, 995, 999, 1008, 1014, 
	1023, 1027, 1036, 1042, 1051, 1055, 1064, 1070, 
	1076, 1085, 1089, 1098, 1104, 1110, 1119, 1123, 
	1132, 1138, 1147, 1151, 1160, 1166, 1175, 1179, 
	1188, 1194, 1200, 1209, 1213, 1222, 1228, 1234, 
	1236, 1246, 1252, 1256, 1264, 1274, 1280, 1284, 
	1292, 1302, 1308, 1312, 1320, 1330, 1336, 1340, 
	1348, 1358, 1364, 1368, 1376, 1386, 1392, 1396, 
	1404, 1414, 1420, 1424, 1432, 1442, 1448, 1452, 
	1460, 1470, 1476, 1480, 1488, 1502, 1517, 1520, 
	1523, 1526, 1529, 1532, 1539, 1546, 1548, 1561, 
	1573, 1588, 1603, 1609, 1623, 1638, 1641, 1644, 
	1647, 1650, 1656, 1662, 1674, 1689, 1704, 1710, 
	1723, 1725, 1740, 1755, 1769, 1784, 1798, 1813, 
	1816, 1819, 1822, 1827, 1835, 1838, 1841, 1844, 
	1849, 1861, 1876, 1891, 1905, 1920, 1932, 1947, 
	1962, 1964, 1978, 1993, 1996, 1999, 2002, 2005, 
	2010, 2022, 2037, 2052, 2066, 2081, 2093, 2108, 
	2123, 2125, 2139, 2154, 2157, 2160, 2163, 2166, 
	2169, 2172, 2175, 2178, 2183, 2195, 2210, 2225, 
	2239, 2254, 2266, 2281, 2296, 2298, 2312, 2327, 
	2330, 2333, 2338, 2344, 2356, 2371, 2386, 2392, 
	2405, 2407, 2422, 2437, 2451, 2466, 2480, 2495, 
	2497, 2497, 2510
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
	32, 41, 11, 13, 10, 32, 35, 9, 
	13, 10, 32, 103, 9, 13, 114, 111, 
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
	13, 10, 32, 103, 9, 13, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 67, 11, 13, 108, 105, 112, 98, 
	111, 97, 114, 100, 9, 32, 41, 11, 
	13, 10, 32, 35, 9, 13, 10, 32, 
	101, 9, 13, 110, 100, 9, 32, 11, 
	13, -1, 10, -1, 10, -1, 10, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 101, 108, 118, 105, 110, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 10, 32, 35, 9, 13, 48, 
	57, 10, 32, 35, 9, 13, 10, 32, 
	103, 9, 13, -1, 10, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 9, 32, 
	11, 13, 9, 32, 11, 13, 48, 57, 
	48, 57, 48, 57, 48, 57, 48, 57, 
	48, 57, 9, 32, 11, 13, 9, 32, 
	112, 11, 13, 114, 101, 102, 101, 114, 
	114, 101, 100, 10, 32, 35, 9, 13, 
	-1, 10, -1, 10, 32, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	116, -1, 10, 111, -1, 10, 109, -1, 
	10, 32, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 111, -1, 
	10, 110, -1, 10, 100, -1, 10, 95, 
	97, 99, 103, 49, 51, -1, 10, 32, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 100, -1, 10, 
	105, -1, 10, 114, -1, 10, 101, -1, 
	10, 99, -1, 10, 116, -1, 10, 105, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	32, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 115, -1, 10, 121, -1, 10, 115, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 46, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 46, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 46, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 46, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 103, 
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
	10, -1, 10, 32, 35, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	32, 97, 98, 99, 101, 103, 105, 109, 
	9, 13, 0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 3, 3, 1, 1, 
	1, 1, 3, 3, 3, 4, 4, 3, 
	4, 3, 1, 1, 1, 3, 3, 1, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 3, 3, 
	1, 1, 2, 2, 2, 2, 4, 4, 
	3, 4, 3, 4, 2, 1, 1, 1, 
	1, 1, 2, 2, 3, 3, 3, 2, 
	3, 2, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 2, 10, 3, 3, 
	3, 3, 3, 3, 4, 3, 4, 4, 
	3, 4, 5, 2, 4, 4, 5, 2, 
	4, 4, 5, 2, 4, 4, 4, 5, 
	2, 5, 5, 4, 5, 4, 2, 4, 
	4, 4, 2, 4, 4, 4, 2, 4, 
	4, 4, 3, 3, 3, 3, 6, 3, 
	3, 4, 4, 2, 4, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 4, 4, 2, 4, 3, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 4, 5, 2, 5, 4, 5, 
	2, 5, 4, 5, 2, 5, 4, 4, 
	5, 2, 5, 4, 4, 5, 2, 5, 
	4, 5, 2, 5, 4, 5, 2, 5, 
	4, 4, 5, 2, 5, 4, 4, 2, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 4, 5, 3, 3, 
	3, 3, 3, 5, 5, 2, 5, 4, 
	5, 5, 4, 4, 5, 3, 3, 3, 
	3, 4, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 3, 
	3, 3, 3, 6, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 2, 
	0, 11, 10
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 1, 1, 0, 0, 
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
	0, 0, 1, 4, 5, 5, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 1, 2, 1, 2, 1, 1, 0, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 5, 5, 0, 0, 
	0, 0, 0, 1, 1, 0, 4, 4, 
	5, 5, 1, 5, 5, 0, 0, 0, 
	0, 1, 1, 4, 5, 5, 1, 4, 
	0, 5, 5, 5, 5, 5, 5, 0, 
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

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 129, 134, 136, 
	138, 140, 142, 147, 152, 160, 170, 180, 
	185, 194, 199, 201, 203, 205, 210, 215, 
	217, 219, 221, 223, 228, 233, 235, 237, 
	239, 241, 243, 245, 247, 249, 254, 259, 
	264, 266, 268, 272, 275, 278, 281, 291, 
	301, 310, 320, 329, 339, 342, 344, 346, 
	348, 350, 352, 356, 361, 367, 372, 377, 
	380, 386, 389, 393, 398, 400, 402, 404, 
	406, 408, 412, 417, 419, 421, 423, 425, 
	427, 429, 431, 433, 438, 441, 453, 457, 
	461, 465, 470, 476, 482, 488, 494, 501, 
	507, 512, 518, 526, 530, 537, 543, 551, 
	555, 562, 568, 576, 580, 587, 593, 599, 
	609, 612, 623, 634, 644, 655, 662, 666, 
	673, 680, 687, 691, 698, 705, 712, 716, 
	723, 730, 737, 743, 747, 751, 755, 763, 
	768, 774, 781, 788, 791, 798, 802, 806, 
	810, 814, 818, 822, 826, 830, 834, 839, 
	845, 851, 857, 864, 870, 873, 880, 886, 
	890, 894, 898, 904, 913, 924, 935, 941, 
	949, 953, 961, 967, 975, 979, 987, 993, 
	1001, 1005, 1013, 1019, 1027, 1031, 1039, 1045, 
	1051, 1059, 1063, 1071, 1077, 1083, 1091, 1095, 
	1103, 1109, 1117, 1121, 1129, 1135, 1143, 1147, 
	1155, 1161, 1167, 1175, 1179, 1187, 1193, 1199, 
	1202, 1211, 1217, 1221, 1228, 1237, 1243, 1247, 
	1254, 1263, 1269, 1273, 1280, 1289, 1295, 1299, 
	1306, 1315, 1321, 1325, 1332, 1341, 1347, 1351, 
	1358, 1367, 1373, 1377, 1384, 1393, 1399, 1403, 
	1410, 1419, 1425, 1429, 1436, 1446, 1457, 1461, 
	1465, 1469, 1473, 1477, 1484, 1491, 1494, 1504, 
	1513, 1524, 1535, 1541, 1551, 1562, 1566, 1570, 
	1574, 1578, 1584, 1590, 1599, 1610, 1621, 1627, 
	1637, 1640, 1651, 1662, 1672, 1683, 1693, 1704, 
	1708, 1712, 1716, 1721, 1729, 1733, 1737, 1741, 
	1746, 1755, 1766, 1777, 1787, 1798, 1807, 1818, 
	1829, 1832, 1842, 1853, 1857, 1861, 1865, 1869, 
	1874, 1883, 1894, 1905, 1915, 1926, 1935, 1946, 
	1957, 1960, 1970, 1981, 1985, 1989, 1993, 1997, 
	2001, 2005, 2009, 2013, 2018, 2027, 2038, 2049, 
	2059, 2070, 2079, 2090, 2101, 2104, 2114, 2125, 
	2129, 2133, 2138, 2144, 2153, 2164, 2175, 2181, 
	2191, 2194, 2205, 2216, 2226, 2237, 2247, 2258, 
	2261, 2262, 2275
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
	50, 51, 50, 1, 52, 51, 53, 51, 
	1, 55, 54, 56, 54, 1, 57, 1, 
	58, 1, 59, 1, 60, 1, 61, 61, 
	62, 61, 1, 63, 63, 64, 63, 1, 
	64, 64, 65, 64, 65, 65, 65, 1, 
	66, 66, 67, 69, 66, 68, 69, 69, 
	69, 1, 70, 70, 71, 73, 70, 72, 
	73, 73, 73, 1, 75, 74, 76, 74, 
	1, 75, 74, 76, 77, 74, 77, 77, 
	77, 1, 79, 78, 80, 78, 1, 81, 
	1, 82, 1, 83, 1, 84, 83, 85, 
	83, 1, 87, 86, 88, 86, 1, 89, 
	1, 90, 1, 91, 1, 92, 1, 92, 
	92, 93, 92, 1, 93, 93, 94, 93, 
	1, 95, 1, 96, 1, 97, 1, 98, 
	1, 99, 1, 100, 1, 101, 1, 102, 
	1, 102, 102, 103, 102, 1, 104, 103, 
	105, 103, 1, 107, 106, 108, 106, 1, 
	109, 1, 110, 1, 111, 111, 111, 1, 
	1, 104, 105, 1, 84, 85, 1, 75, 
	76, 113, 112, 114, 116, 112, 115, 116, 
	116, 116, 1, 75, 117, 76, 119, 117, 
	118, 119, 119, 119, 1, 118, 118, 119, 
	118, 118, 119, 119, 119, 1, 121, 120, 
	122, 119, 120, 118, 119, 119, 119, 1, 
	72, 72, 73, 72, 72, 73, 73, 73, 
	1, 123, 123, 124, 73, 123, 72, 73, 
	73, 73, 1, 1, 52, 53, 125, 1, 
	126, 1, 127, 1, 128, 1, 129, 1, 
	130, 130, 130, 1, 130, 130, 130, 131, 
	1, 133, 132, 134, 132, 135, 1, 137, 
	136, 138, 136, 1, 137, 139, 32, 139, 
	1, 1, 137, 138, 133, 132, 134, 132, 
	135, 1, 1, 28, 29, 140, 140, 140, 
	1, 140, 140, 140, 141, 1, 142, 1, 
	143, 1, 144, 1, 145, 1, 146, 1, 
	147, 147, 147, 1, 147, 147, 148, 147, 
	1, 149, 1, 150, 1, 151, 1, 152, 
	1, 153, 1, 154, 1, 155, 1, 156, 
	1, 28, 156, 29, 156, 1, 157, 159, 
	158, 157, 161, 160, 162, 163, 164, 165, 
	166, 167, 168, 160, 158, 157, 159, 169, 
	158, 157, 159, 170, 158, 157, 159, 171, 
	158, 157, 159, 172, 172, 158, 157, 159, 
	172, 172, 173, 158, 157, 159, 174, 174, 
	175, 158, 157, 159, 176, 177, 176, 158, 
	157, 159, 177, 177, 178, 158, 157, 159, 
	179, 180, 179, 181, 158, 157, 159, 179, 
	180, 179, 158, 157, 159, 182, 182, 158, 
	157, 159, 183, 184, 183, 158, 157, 159, 
	184, 185, 186, 184, 187, 158, 157, 159, 
	187, 158, 157, 159, 188, 189, 188, 190, 
	158, 157, 159, 188, 189, 188, 158, 157, 
	159, 191, 192, 193, 191, 194, 158, 157, 
	159, 194, 158, 157, 159, 195, 196, 195, 
	197, 158, 157, 159, 195, 196, 195, 158, 
	157, 159, 198, 199, 200, 198, 201, 158, 
	157, 159, 201, 158, 157, 159, 202, 203, 
	202, 204, 158, 157, 159, 202, 203, 202, 
	158, 157, 206, 205, 207, 205, 158, 157, 
	206, 205, 207, 208, 205, 208, 208, 208, 
	158, 157, 206, 207, 157, 210, 209, 211, 
	213, 209, 212, 213, 213, 213, 158, 157, 
	206, 214, 207, 216, 214, 215, 216, 216, 
	216, 158, 157, 159, 215, 216, 215, 215, 
	216, 216, 216, 158, 157, 218, 217, 219, 
	216, 217, 215, 216, 216, 216, 158, 157, 
	159, 202, 203, 202, 204, 158, 157, 159, 
	220, 158, 157, 159, 221, 222, 221, 223, 
	158, 157, 159, 221, 222, 221, 223, 158, 
	157, 159, 195, 196, 195, 197, 158, 157, 
	159, 224, 158, 157, 159, 225, 226, 225, 
	227, 158, 157, 159, 225, 226, 225, 227, 
	158, 157, 159, 188, 189, 188, 190, 158, 
	157, 159, 228, 158, 157, 159, 229, 230, 
	229, 231, 158, 157, 159, 229, 230, 229, 
	231, 158, 157, 159, 179, 180, 179, 181, 
	158, 157, 159, 174, 174, 175, 158, 157, 
	159, 232, 158, 157, 159, 233, 158, 157, 
	159, 234, 158, 157, 159, 236, 235, 235, 
	235, 235, 158, 157, 159, 237, 237, 158, 
	157, 159, 237, 237, 238, 158, 157, 240, 
	239, 241, 239, 242, 158, 157, 244, 243, 
	245, 243, 238, 158, 157, 244, 245, 157, 
	240, 239, 241, 239, 242, 158, 157, 159, 
	246, 158, 157, 159, 247, 158, 157, 159, 
	248, 158, 157, 159, 249, 158, 157, 159, 
	250, 158, 157, 159, 251, 158, 157, 159, 
	252, 158, 157, 159, 253, 158, 157, 159, 
	254, 158, 157, 159, 255, 255, 158, 157, 
	159, 255, 255, 256, 158, 157, 159, 257, 
	257, 258, 158, 157, 159, 257, 257, 259, 
	158, 157, 261, 260, 262, 260, 263, 158, 
	157, 261, 260, 262, 260, 158, 157, 261, 
	262, 157, 261, 260, 262, 260, 263, 158, 
	157, 159, 257, 257, 258, 158, 157, 159, 
	264, 158, 157, 159, 265, 158, 157, 159, 
	266, 158, 157, 159, 266, 267, 266, 158, 
	157, 159, 267, 268, 267, 268, 268, 268, 
	158, 157, 159, 269, 270, 272, 269, 271, 
	272, 272, 272, 158, 157, 159, 273, 274, 
	276, 273, 275, 276, 276, 276, 158, 157, 
	159, 277, 278, 277, 158, 157, 159, 278, 
	279, 279, 278, 280, 158, 157, 159, 281, 
	158, 157, 159, 282, 283, 284, 282, 281, 
	158, 157, 159, 285, 286, 285, 158, 157, 
	159, 287, 288, 288, 287, 289, 158, 157, 
	159, 290, 158, 157, 159, 291, 292, 293, 
	291, 290, 158, 157, 159, 294, 295, 294, 
	158, 157, 159, 296, 297, 297, 296, 298, 
	158, 157, 159, 299, 158, 157, 159, 300, 
	301, 302, 300, 299, 158, 157, 159, 303, 
	304, 303, 158, 157, 159, 305, 306, 306, 
	305, 307, 158, 157, 159, 308, 158, 157, 
	159, 309, 310, 311, 309, 308, 158, 157, 
	159, 312, 313, 312, 158, 157, 159, 314, 
	315, 314, 158, 157, 159, 315, 316, 316, 
	315, 317, 158, 157, 159, 318, 158, 157, 
	159, 319, 320, 321, 319, 318, 158, 157, 
	159, 322, 323, 322, 158, 157, 159, 324, 
	325, 324, 158, 157, 159, 325, 326, 326, 
	325, 327, 158, 157, 159, 328, 158, 157, 
	159, 329, 330, 331, 329, 328, 158, 157, 
	159, 332, 333, 332, 158, 157, 159, 334, 
	335, 335, 334, 336, 158, 157, 159, 337, 
	158, 157, 159, 338, 339, 340, 338, 337, 
	158, 157, 159, 341, 342, 341, 158, 157, 
	159, 343, 344, 344, 343, 345, 158, 157, 
	159, 346, 158, 157, 159, 347, 348, 349, 
	347, 346, 158, 157, 159, 350, 351, 350, 
	158, 157, 159, 352, 353, 352, 158, 157, 
	159, 353, 354, 354, 353, 355, 158, 157, 
	159, 356, 158, 157, 159, 357, 358, 359, 
	357, 356, 158, 157, 159, 360, 361, 360, 
	158, 157, 363, 362, 364, 362, 158, 157, 
	363, 364, 157, 159, 357, 358, 365, 365, 
	357, 359, 158, 157, 159, 366, 366, 367, 
	158, 157, 159, 367, 158, 157, 159, 357, 
	358, 357, 367, 158, 157, 159, 347, 348, 
	368, 368, 347, 349, 158, 157, 159, 369, 
	369, 370, 158, 157, 159, 370, 158, 157, 
	159, 347, 348, 347, 370, 158, 157, 159, 
	338, 339, 371, 371, 338, 340, 158, 157, 
	159, 372, 372, 373, 158, 157, 159, 373, 
	158, 157, 159, 338, 339, 338, 373, 158, 
	157, 159, 329, 330, 374, 374, 329, 331, 
	158, 157, 159, 375, 375, 376, 158, 157, 
	159, 376, 158, 157, 159, 329, 330, 329, 
	376, 158, 157, 159, 319, 320, 377, 377, 
	319, 321, 158, 157, 159, 378, 378, 379, 
	158, 157, 159, 379, 158, 157, 159, 319, 
	320, 319, 379, 158, 157, 159, 309, 310, 
	380, 380, 309, 311, 158, 157, 159, 381, 
	381, 382, 158, 157, 159, 382, 158, 157, 
	159, 309, 310, 309, 382, 158, 157, 159, 
	300, 301, 383, 383, 300, 302, 158, 157, 
	159, 384, 384, 385, 158, 157, 159, 385, 
	158, 157, 159, 300, 301, 300, 385, 158, 
	157, 159, 291, 292, 386, 386, 291, 293, 
	158, 157, 159, 387, 387, 388, 158, 157, 
	159, 388, 158, 157, 159, 291, 292, 291, 
	388, 158, 157, 159, 282, 283, 389, 389, 
	282, 284, 158, 157, 159, 390, 390, 391, 
	158, 157, 159, 391, 158, 157, 159, 282, 
	283, 282, 391, 158, 157, 159, 275, 276, 
	275, 275, 276, 276, 276, 158, 157, 159, 
	392, 393, 276, 392, 275, 276, 276, 276, 
	158, 157, 159, 394, 158, 157, 159, 395, 
	158, 157, 159, 396, 158, 157, 159, 397, 
	158, 157, 159, 398, 158, 157, 400, 399, 
	401, 402, 399, 158, 157, 404, 403, 405, 
	406, 403, 158, 157, 404, 405, 157, 159, 
	407, 408, 409, 407, 409, 409, 409, 158, 
	157, 159, 407, 409, 407, 409, 409, 409, 
	158, 157, 159, 410, 411, 413, 410, 412, 
	413, 413, 413, 158, 157, 159, 414, 408, 
	416, 414, 415, 416, 416, 416, 158, 157, 
	404, 408, 405, 408, 158, 157, 159, 415, 
	416, 415, 415, 416, 416, 416, 158, 157, 
	159, 417, 418, 416, 417, 415, 416, 416, 
	416, 158, 157, 159, 419, 158, 157, 159, 
	420, 158, 157, 159, 421, 158, 157, 159, 
	422, 158, 157, 159, 423, 424, 423, 158, 
	157, 159, 425, 426, 425, 158, 157, 159, 
	426, 427, 426, 427, 427, 427, 158, 157, 
	159, 428, 429, 431, 428, 430, 431, 431, 
	431, 158, 157, 159, 432, 433, 435, 432, 
	434, 435, 435, 435, 158, 157, 437, 436, 
	438, 436, 158, 157, 437, 436, 438, 439, 
	436, 439, 439, 439, 158, 157, 437, 438, 
	157, 441, 440, 442, 444, 440, 443, 444, 
	444, 444, 158, 157, 437, 445, 438, 447, 
	445, 446, 447, 447, 447, 158, 157, 159, 
	446, 447, 446, 446, 447, 447, 447, 158, 
	157, 449, 448, 450, 447, 448, 446, 447, 
	447, 447, 158, 157, 159, 434, 435, 434, 
	434, 435, 435, 435, 158, 157, 159, 451, 
	452, 435, 451, 434, 435, 435, 435, 158, 
	157, 159, 453, 158, 157, 159, 454, 158, 
	157, 159, 455, 158, 157, 159, 456, 456, 
	158, 157, 159, 456, 457, 458, 459, 456, 
	158, 157, 159, 460, 158, 157, 159, 461, 
	158, 157, 159, 462, 158, 157, 159, 463, 
	463, 158, 157, 159, 463, 464, 463, 464, 
	464, 464, 158, 157, 159, 465, 468, 467, 
	465, 466, 467, 467, 467, 158, 157, 159, 
	469, 472, 471, 469, 470, 471, 471, 471, 
	158, 157, 159, 470, 471, 470, 470, 471, 
	471, 471, 158, 157, 159, 473, 474, 471, 
	473, 470, 471, 471, 471, 158, 157, 159, 
	472, 475, 472, 475, 475, 475, 158, 157, 
	477, 476, 478, 480, 476, 479, 480, 480, 
	480, 158, 157, 482, 481, 483, 485, 481, 
	484, 485, 485, 485, 158, 157, 482, 483, 
	157, 159, 484, 485, 484, 484, 485, 485, 
	485, 158, 157, 487, 486, 488, 485, 486, 
	484, 485, 485, 485, 158, 157, 159, 489, 
	158, 157, 159, 490, 158, 157, 159, 491, 
	158, 157, 159, 492, 158, 157, 159, 493, 
	493, 158, 157, 159, 493, 494, 493, 494, 
	494, 494, 158, 157, 159, 495, 498, 497, 
	495, 496, 497, 497, 497, 158, 157, 159, 
	499, 502, 501, 499, 500, 501, 501, 501, 
	158, 157, 159, 500, 501, 500, 500, 501, 
	501, 501, 158, 157, 159, 503, 504, 501, 
	503, 500, 501, 501, 501, 158, 157, 159, 
	502, 505, 502, 505, 505, 505, 158, 157, 
	507, 506, 508, 510, 506, 509, 510, 510, 
	510, 158, 157, 512, 511, 513, 515, 511, 
	514, 515, 515, 515, 158, 157, 512, 513, 
	157, 159, 514, 515, 514, 514, 515, 515, 
	515, 158, 157, 517, 516, 518, 515, 516, 
	514, 515, 515, 515, 158, 157, 159, 519, 
	158, 157, 159, 520, 158, 157, 159, 521, 
	158, 157, 159, 522, 158, 157, 159, 523, 
	158, 157, 159, 524, 158, 157, 159, 525, 
	158, 157, 159, 526, 158, 157, 159, 527, 
	527, 158, 157, 159, 527, 528, 527, 528, 
	528, 528, 158, 157, 159, 529, 532, 531, 
	529, 530, 531, 531, 531, 158, 157, 159, 
	533, 536, 535, 533, 534, 535, 535, 535, 
	158, 157, 159, 534, 535, 534, 534, 535, 
	535, 535, 158, 157, 159, 537, 538, 535, 
	537, 534, 535, 535, 535, 158, 157, 159, 
	536, 539, 536, 539, 539, 539, 158, 157, 
	541, 540, 542, 544, 540, 543, 544, 544, 
	544, 158, 157, 546, 545, 547, 549, 545, 
	548, 549, 549, 549, 158, 157, 546, 547, 
	157, 159, 548, 549, 548, 548, 549, 549, 
	549, 158, 157, 551, 550, 552, 549, 550, 
	548, 549, 549, 549, 158, 157, 159, 553, 
	158, 157, 159, 554, 158, 157, 159, 555, 
	555, 158, 157, 159, 555, 556, 555, 158, 
	157, 159, 556, 557, 556, 557, 557, 557, 
	158, 157, 159, 558, 559, 561, 558, 560, 
	561, 561, 561, 158, 157, 159, 562, 563, 
	565, 562, 564, 565, 565, 565, 158, 157, 
	567, 566, 568, 566, 158, 157, 567, 566, 
	568, 569, 566, 569, 569, 569, 158, 157, 
	567, 568, 157, 571, 570, 572, 574, 570, 
	573, 574, 574, 574, 158, 157, 567, 575, 
	568, 577, 575, 576, 577, 577, 577, 158, 
	157, 159, 576, 577, 576, 576, 577, 577, 
	577, 158, 157, 579, 578, 580, 577, 578, 
	576, 577, 577, 577, 158, 157, 159, 564, 
	565, 564, 564, 565, 565, 565, 158, 157, 
	159, 581, 582, 565, 581, 564, 565, 565, 
	565, 158, 1, 584, 583, 111, 1, 161, 
	160, 583, 162, 163, 164, 165, 166, 167, 
	168, 160, 158, 585, 161, 160, 162, 163, 
	164, 165, 166, 167, 168, 160, 158, 0
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
	79, 83, 79, 79, 80, 81, 82, 392, 
	87, 57, 85, 88, 89, 87, 88, 89, 
	87, 57, 85, 54, 55, 94, 95, 96, 
	97, 98, 99, 100, 101, 102, 103, 104, 
	101, 102, 103, 102, 107, 108, 109, 110, 
	111, 112, 113, 114, 115, 116, 117, 118, 
	119, 120, 121, 122, 123, 393, 124, 393, 
	125, 394, 126, 171, 199, 286, 301, 319, 
	375, 127, 128, 129, 130, 131, 132, 170, 
	132, 133, 134, 135, 136, 169, 137, 137, 
	138, 139, 166, 140, 141, 142, 165, 142, 
	143, 162, 144, 145, 146, 161, 146, 147, 
	158, 148, 149, 150, 157, 151, 393, 152, 
	153, 154, 393, 152, 155, 156, 154, 155, 
	156, 154, 393, 152, 159, 149, 150, 160, 
	163, 145, 146, 164, 167, 141, 142, 168, 
	172, 173, 174, 175, 181, 176, 177, 178, 
	393, 179, 180, 178, 393, 179, 182, 183, 
	184, 185, 186, 187, 188, 189, 190, 191, 
	192, 193, 198, 194, 195, 393, 196, 197, 
	200, 201, 202, 203, 204, 205, 206, 284, 
	285, 205, 206, 284, 285, 206, 207, 208, 
	209, 209, 210, 211, 280, 210, 211, 211, 
	212, 213, 213, 214, 215, 276, 214, 215, 
	215, 216, 217, 217, 218, 219, 272, 218, 
	219, 219, 220, 221, 221, 222, 223, 268, 
	222, 223, 223, 224, 225, 226, 226, 227, 
	228, 264, 227, 228, 228, 229, 230, 231, 
	231, 232, 233, 260, 232, 233, 233, 234, 
	235, 235, 236, 237, 256, 236, 237, 237, 
	238, 239, 239, 240, 241, 252, 240, 241, 
	241, 242, 243, 244, 244, 245, 246, 248, 
	245, 246, 246, 393, 247, 249, 250, 251, 
	253, 254, 255, 257, 258, 259, 261, 262, 
	263, 265, 266, 267, 269, 270, 271, 273, 
	274, 275, 277, 278, 279, 281, 282, 283, 
	205, 206, 287, 288, 289, 290, 291, 292, 
	393, 293, 294, 292, 393, 293, 294, 295, 
	298, 296, 297, 298, 299, 300, 297, 299, 
	300, 297, 298, 302, 303, 304, 305, 306, 
	307, 306, 307, 308, 309, 310, 317, 318, 
	309, 310, 317, 318, 311, 393, 312, 313, 
	314, 393, 312, 315, 316, 314, 315, 316, 
	314, 393, 312, 309, 310, 320, 321, 322, 
	323, 324, 339, 355, 325, 326, 327, 328, 
	329, 330, 331, 332, 333, 330, 331, 332, 
	333, 330, 333, 334, 335, 393, 336, 337, 
	338, 335, 393, 336, 337, 338, 335, 393, 
	336, 340, 341, 342, 343, 344, 345, 346, 
	347, 348, 349, 346, 347, 348, 349, 346, 
	349, 350, 351, 393, 352, 353, 354, 351, 
	393, 352, 353, 354, 351, 393, 352, 356, 
	357, 358, 359, 360, 361, 362, 363, 364, 
	365, 366, 367, 368, 369, 366, 367, 368, 
	369, 366, 369, 370, 371, 393, 372, 373, 
	374, 371, 393, 372, 373, 374, 371, 393, 
	372, 376, 377, 378, 379, 380, 381, 382, 
	389, 390, 381, 382, 389, 390, 383, 393, 
	384, 385, 386, 393, 384, 387, 388, 386, 
	387, 388, 386, 393, 384, 381, 382, 391, 
	393, 393
};

static const short _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 43, 43, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 178, 0, 0, 1, 
	0, 0, 0, 0, 0, 65, 65, 0, 
	0, 0, 137, 137, 17, 134, 0, 0, 
	0, 19, 0, 186, 0, 0, 0, 1, 
	0, 0, 0, 0, 83, 0, 0, 1, 
	67, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	194, 0, 0, 1, 0, 0, 0, 0, 
	140, 275, 140, 17, 134, 0, 0, 19, 
	23, 237, 23, 21, 21, 0, 0, 0, 
	0, 0, 0, 0, 73, 152, 73, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 81, 0, 92, 
	0, 218, 0, 0, 0, 69, 0, 149, 
	39, 0, 0, 0, 0, 0, 25, 5, 
	0, 0, 0, 0, 0, 5, 27, 0, 
	0, 0, 0, 0, 0, 29, 5, 0, 
	0, 0, 0, 0, 31, 5, 0, 0, 
	0, 0, 0, 33, 5, 0, 158, 0, 
	0, 206, 299, 206, 17, 134, 0, 0, 
	19, 143, 293, 143, 0, 11, 101, 5, 
	0, 11, 98, 5, 0, 11, 95, 5, 
	0, 0, 0, 37, 0, 0, 0, 35, 
	214, 35, 5, 0, 86, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 5, 0, 0, 162, 0, 9, 
	0, 0, 0, 0, 0, 137, 210, 17, 
	134, 0, 45, 0, 19, 0, 0, 104, 
	104, 13, 15, 107, 13, 0, 47, 0, 
	104, 104, 13, 15, 110, 13, 0, 49, 
	0, 104, 104, 13, 15, 113, 13, 0, 
	51, 0, 104, 104, 13, 15, 116, 13, 
	0, 53, 0, 0, 104, 104, 13, 15, 
	119, 13, 0, 55, 0, 0, 104, 104, 
	13, 15, 122, 13, 0, 57, 0, 104, 
	104, 13, 15, 125, 13, 0, 59, 0, 
	104, 104, 13, 15, 128, 13, 0, 61, 
	0, 0, 104, 104, 13, 15, 131, 13, 
	0, 63, 0, 182, 0, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	21, 146, 0, 0, 0, 0, 0, 71, 
	252, 71, 71, 0, 198, 0, 0, 0, 
	0, 0, 137, 137, 17, 134, 0, 0, 
	19, 21, 21, 0, 0, 0, 0, 65, 
	65, 0, 0, 0, 137, 137, 17, 134, 
	0, 0, 0, 19, 0, 190, 0, 0, 
	140, 281, 140, 17, 134, 0, 0, 19, 
	23, 242, 23, 21, 21, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 137, 17, 134, 137, 0, 0, 19, 
	0, 21, 21, 0, 140, 257, 140, 17, 
	134, 0, 166, 0, 0, 19, 23, 222, 
	23, 0, 0, 0, 0, 0, 0, 137, 
	17, 134, 137, 0, 0, 19, 0, 21, 
	21, 0, 140, 269, 140, 17, 134, 0, 
	174, 0, 0, 19, 23, 232, 23, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 137, 17, 134, 137, 0, 0, 19, 
	0, 21, 21, 0, 140, 287, 140, 17, 
	134, 0, 202, 0, 0, 19, 23, 247, 
	23, 0, 0, 0, 0, 0, 137, 137, 
	17, 134, 0, 0, 0, 19, 0, 170, 
	0, 0, 140, 263, 140, 17, 134, 0, 
	0, 19, 23, 227, 23, 21, 21, 0, 
	89, 79
};

static const short _parse_tester_to_state_actions[] = {
	0, 75, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 75, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 75, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 75, 
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 41, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 155, 0
};

static const short _parse_tester_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 77, 0
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
	158, 158, 158, 158, 158, 158, 158, 0, 
	0, 0, 586
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 392;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 393;
static const int parse_tester_en_main = 1;

#line 1280 "NanorexMMPImportExportRagelTest.rl"
	
#line 11746 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1281 "NanorexMMPImportExportRagelTest.rl"
	
#line 11756 "NanorexMMPImportExportRagelTest.cpp"
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
	case 58:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 11777 "NanorexMMPImportExportRagelTest.cpp"
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
#line 53 "NanorexMMPImportExportRagelTest.rl"
	{stringVal.clear(); /*stringVal = stringVal + fc;*/ doubleVal = HUGE_VAL;}
	break;
	case 7:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{stringVal = stringVal + (*p);}
	break;
	case 8:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{doubleVal = atof(stringVal.c_str());}
	break;
	case 9:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 10:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 11:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 12:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 13:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 14:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 20:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 22:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 23:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 24:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 26:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 27:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 28:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 29:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 30:
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 31:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{csysViewName = stringVal;}
	break;
	case 32:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{csysQw=doubleVal;}
	break;
	case 33:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{csysQx=doubleVal;}
	break;
	case 34:
#line 42 "NanorexMMPImportExportRagelTest.rl"
	{csysQy=doubleVal;}
	break;
	case 35:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{csysQz=doubleVal;}
	break;
	case 36:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{csysScale=doubleVal;}
	break;
	case 37:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{csysPovX=doubleVal;}
	break;
	case 38:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{csysPovY=doubleVal;}
	break;
	case 39:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{csysPovZ=doubleVal;}
	break;
	case 40:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{csysZoomFactor=doubleVal;}
	break;
	case 41:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{ newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
	break;
	case 42:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 43:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 44:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 45:
#line 78 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 46:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 47:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 48:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 49:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 50:
#line 98 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 51:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 52:
#line 1164 "NanorexMMPImportExportRagelTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 53:
#line 1178 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 54:
#line 1181 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 55:
#line 1186 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 59:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 60:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{act = 12;}
	break;
	case 61:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 62:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 63:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 64:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 65:
#line 120 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 66:
#line 121 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 67:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 68:
#line 123 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 69:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 70:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 71:
#line 128 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 72:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 73:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 74:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 12:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 12157 "NanorexMMPImportExportRagelTest.cpp"
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
	case 25:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 56:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 57:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 12186 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1282 "NanorexMMPImportExportRagelTest.rl"
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
	
	#line 1389 "NanorexMMPImportExportRagelTest.rl"
	
#line 12314 "NanorexMMPImportExportRagelTest.cpp"
static const char _parse_tester_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 11, 1, 
	12, 1, 13, 1, 14, 1, 15, 1, 
	16, 1, 17, 1, 20, 1, 21, 1, 
	24, 1, 25, 1, 29, 1, 31, 1, 
	32, 1, 33, 1, 34, 1, 35, 1, 
	36, 1, 37, 1, 38, 1, 39, 1, 
	40, 1, 42, 1, 45, 1, 47, 1, 
	48, 1, 52, 1, 56, 1, 58, 1, 
	73, 1, 74, 2, 0, 44, 2, 0, 
	69, 2, 0, 71, 2, 0, 72, 2, 
	5, 15, 2, 5, 16, 2, 5, 17, 
	2, 6, 7, 2, 8, 32, 2, 8, 
	33, 2, 8, 34, 2, 8, 35, 2, 
	8, 36, 2, 8, 37, 2, 8, 38, 
	2, 8, 39, 2, 8, 40, 2, 9, 
	10, 2, 9, 11, 2, 9, 12, 2, 
	11, 18, 2, 11, 31, 2, 50, 27, 
	2, 52, 0, 2, 56, 57, 3, 0, 
	19, 67, 3, 0, 22, 70, 3, 0, 
	23, 68, 3, 0, 26, 65, 3, 0, 
	28, 66, 3, 0, 30, 53, 3, 0, 
	41, 61, 3, 0, 43, 54, 3, 0, 
	43, 62, 3, 0, 46, 55, 3, 0, 
	49, 64, 3, 0, 51, 63, 3, 9, 
	11, 18, 3, 9, 11, 31, 3, 20, 
	0, 69, 3, 59, 0, 60, 4, 12, 
	0, 23, 68, 4, 12, 0, 26, 65, 
	4, 12, 0, 28, 66, 4, 12, 0, 
	43, 54, 4, 12, 0, 43, 62, 4, 
	12, 0, 51, 63, 4, 48, 0, 49, 
	64, 5, 9, 12, 0, 23, 68, 5, 
	9, 12, 0, 26, 65, 5, 9, 12, 
	0, 28, 66, 5, 9, 12, 0, 43, 
	54, 5, 9, 12, 0, 43, 62, 5, 
	9, 12, 0, 51, 63, 5, 11, 18, 
	0, 19, 67, 6, 9, 11, 18, 0, 
	19, 67
};

static const short _parse_tester_key_offsets[] = {
	0, 0, 5, 6, 7, 8, 9, 10, 
	11, 12, 13, 17, 23, 25, 27, 29, 
	31, 33, 37, 42, 43, 44, 45, 46, 
	47, 48, 49, 55, 61, 62, 63, 64, 
	65, 70, 75, 80, 81, 82, 83, 87, 
	92, 93, 94, 95, 100, 105, 110, 111, 
	112, 113, 114, 119, 124, 135, 149, 163, 
	168, 180, 185, 186, 187, 188, 193, 198, 
	199, 200, 201, 202, 207, 212, 213, 214, 
	215, 216, 217, 218, 219, 220, 225, 230, 
	235, 236, 237, 241, 243, 245, 247, 261, 
	275, 288, 302, 315, 329, 331, 332, 333, 
	334, 335, 336, 340, 346, 353, 358, 363, 
	365, 372, 374, 378, 384, 386, 388, 390, 
	392, 394, 398, 403, 404, 405, 406, 407, 
	408, 409, 410, 411, 416, 418, 430, 433, 
	436, 439, 444, 451, 458, 464, 471, 479, 
	485, 490, 496, 505, 509, 517, 523, 532, 
	536, 544, 550, 559, 563, 571, 577, 583, 
	596, 598, 613, 628, 642, 657, 665, 669, 
	677, 685, 693, 697, 705, 713, 721, 725, 
	733, 741, 749, 756, 759, 762, 765, 773, 
	778, 785, 793, 801, 803, 811, 814, 817, 
	820, 823, 826, 829, 832, 835, 838, 843, 
	850, 857, 864, 872, 878, 880, 888, 895, 
	898, 901, 904, 910, 922, 937, 952, 958, 
	967, 971, 980, 986, 995, 999, 1008, 1014, 
	1023, 1027, 1036, 1042, 1051, 1055, 1064, 1070, 
	1076, 1085, 1089, 1098, 1104, 1110, 1119, 1123, 
	1132, 1138, 1147, 1151, 1160, 1166, 1175, 1179, 
	1188, 1194, 1200, 1209, 1213, 1222, 1228, 1234, 
	1236, 1246, 1252, 1256, 1264, 1274, 1280, 1284, 
	1292, 1302, 1308, 1312, 1320, 1330, 1336, 1340, 
	1348, 1358, 1364, 1368, 1376, 1386, 1392, 1396, 
	1404, 1414, 1420, 1424, 1432, 1442, 1448, 1452, 
	1460, 1470, 1476, 1480, 1488, 1502, 1517, 1520, 
	1523, 1526, 1529, 1532, 1539, 1546, 1548, 1561, 
	1573, 1588, 1603, 1609, 1623, 1638, 1641, 1644, 
	1647, 1650, 1656, 1662, 1674, 1689, 1704, 1710, 
	1723, 1725, 1740, 1755, 1769, 1784, 1798, 1813, 
	1816, 1819, 1822, 1827, 1835, 1838, 1841, 1844, 
	1849, 1861, 1876, 1891, 1905, 1920, 1932, 1947, 
	1962, 1964, 1978, 1993, 1996, 1999, 2002, 2005, 
	2010, 2022, 2037, 2052, 2066, 2081, 2093, 2108, 
	2123, 2125, 2139, 2154, 2157, 2160, 2163, 2166, 
	2169, 2172, 2175, 2178, 2183, 2195, 2210, 2225, 
	2239, 2254, 2266, 2281, 2296, 2298, 2312, 2327, 
	2330, 2333, 2338, 2344, 2356, 2371, 2386, 2392, 
	2405, 2407, 2422, 2437, 2451, 2466, 2480, 2495, 
	2497, 2497, 2510
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
	32, 41, 11, 13, 10, 32, 35, 9, 
	13, 10, 32, 103, 9, 13, 114, 111, 
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
	13, 10, 32, 103, 9, 13, 114, 111, 
	117, 112, 9, 32, 40, 11, 13, 9, 
	32, 67, 11, 13, 108, 105, 112, 98, 
	111, 97, 114, 100, 9, 32, 41, 11, 
	13, 10, 32, 35, 9, 13, 10, 32, 
	101, 9, 13, 110, 100, 9, 32, 11, 
	13, -1, 10, -1, 10, -1, 10, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 9, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 95, 11, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	95, 11, 13, 45, 46, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 95, 11, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 101, 108, 118, 105, 110, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 10, 32, 35, 9, 13, 48, 
	57, 10, 32, 35, 9, 13, 10, 32, 
	103, 9, 13, -1, 10, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 9, 32, 
	11, 13, 9, 32, 11, 13, 48, 57, 
	48, 57, 48, 57, 48, 57, 48, 57, 
	48, 57, 9, 32, 11, 13, 9, 32, 
	112, 11, 13, 114, 101, 102, 101, 114, 
	114, 101, 100, 10, 32, 35, 9, 13, 
	-1, 10, -1, 10, 32, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	116, -1, 10, 111, -1, 10, 109, -1, 
	10, 32, 9, 13, -1, 10, 32, 9, 
	13, 48, 57, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, 48, 57, -1, 
	10, 32, 41, 9, 13, -1, 10, 32, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, -1, 10, 32, 43, 45, 
	9, 13, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 9, 
	13, 48, 57, -1, 10, 32, 41, 9, 
	13, -1, 10, 32, 35, 9, 13, -1, 
	10, 32, 35, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, -1, 10, 
	32, 35, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 95, 9, 13, 45, 46, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 95, 
	9, 13, 45, 46, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 35, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 32, 44, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	44, 9, 13, 48, 57, -1, 10, 32, 
	41, 9, 13, 48, 57, -1, 10, 32, 
	9, 13, 48, 57, -1, 10, 111, -1, 
	10, 110, -1, 10, 100, -1, 10, 95, 
	97, 99, 103, 49, 51, -1, 10, 32, 
	9, 13, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, 32, 35, 9, 13, 48, 
	57, -1, 10, -1, 10, 32, 35, 9, 
	13, 48, 57, -1, 10, 100, -1, 10, 
	105, -1, 10, 114, -1, 10, 101, -1, 
	10, 99, -1, 10, 116, -1, 10, 105, 
	-1, 10, 111, -1, 10, 110, -1, 10, 
	32, 9, 13, -1, 10, 32, 9, 13, 
	48, 57, -1, 10, 32, 9, 13, 48, 
	57, -1, 10, 32, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	-1, 10, 32, 35, 9, 13, 48, 57, 
	-1, 10, 32, 9, 13, 48, 57, -1, 
	10, 115, -1, 10, 121, -1, 10, 115, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 95, 9, 
	13, 45, 46, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 95, 9, 13, 
	45, 46, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 41, 46, 9, 13, 48, 57, 
	-1, 10, 32, 41, 9, 13, -1, 10, 
	32, 40, 9, 13, -1, 10, 32, 43, 
	45, 9, 13, 48, 57, -1, 10, 48, 
	57, -1, 10, 32, 41, 46, 9, 13, 
	48, 57, -1, 10, 32, 41, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 44, 46, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	9, 13, -1, 10, 32, 43, 45, 9, 
	13, 48, 57, -1, 10, 48, 57, -1, 
	10, 32, 44, 46, 9, 13, 48, 57, 
	-1, 10, 32, 44, 9, 13, -1, 10, 
	32, 43, 45, 9, 13, 48, 57, -1, 
	10, 48, 57, -1, 10, 32, 41, 46, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	9, 13, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 43, 45, 9, 13, 48, 
	57, -1, 10, 48, 57, -1, 10, 32, 
	41, 46, 9, 13, 48, 57, -1, 10, 
	32, 41, 9, 13, -1, 10, 32, 35, 
	9, 13, -1, 10, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 41, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 41, 9, 13, 48, 57, 
	-1, 10, 32, 41, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 41, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 44, 69, 101, 9, 13, 
	48, 57, -1, 10, 43, 45, 48, 57, 
	-1, 10, 48, 57, -1, 10, 32, 44, 
	9, 13, 48, 57, -1, 10, 32, 44, 
	69, 101, 9, 13, 48, 57, -1, 10, 
	43, 45, 48, 57, -1, 10, 48, 57, 
	-1, 10, 32, 44, 9, 13, 48, 57, 
	-1, 10, 32, 95, 9, 13, 45, 46, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 95, 9, 13, 45, 46, 48, 
	57, 65, 90, 97, 122, -1, 10, 103, 
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
	10, -1, 10, 32, 35, 97, 98, 99, 
	101, 103, 105, 109, 9, 13, -1, 10, 
	32, 97, 98, 99, 101, 103, 105, 109, 
	9, 13, 0
};

static const char _parse_tester_single_lengths[] = {
	0, 3, 1, 1, 1, 1, 1, 1, 
	1, 1, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 4, 4, 1, 1, 1, 1, 
	3, 3, 3, 1, 1, 1, 2, 3, 
	1, 1, 1, 3, 3, 3, 1, 1, 
	1, 1, 3, 3, 3, 4, 4, 3, 
	4, 3, 1, 1, 1, 3, 3, 1, 
	1, 1, 1, 3, 3, 1, 1, 1, 
	1, 1, 1, 1, 1, 3, 3, 3, 
	1, 1, 2, 2, 2, 2, 4, 4, 
	3, 4, 3, 4, 2, 1, 1, 1, 
	1, 1, 2, 2, 3, 3, 3, 2, 
	3, 2, 2, 2, 0, 0, 0, 0, 
	0, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 2, 10, 3, 3, 
	3, 3, 3, 3, 4, 3, 4, 4, 
	3, 4, 5, 2, 4, 4, 5, 2, 
	4, 4, 5, 2, 4, 4, 4, 5, 
	2, 5, 5, 4, 5, 4, 2, 4, 
	4, 4, 2, 4, 4, 4, 2, 4, 
	4, 4, 3, 3, 3, 3, 6, 3, 
	3, 4, 4, 2, 4, 3, 3, 3, 
	3, 3, 3, 3, 3, 3, 3, 3, 
	3, 3, 4, 4, 2, 4, 3, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 4, 5, 2, 5, 4, 5, 
	2, 5, 4, 5, 2, 5, 4, 4, 
	5, 2, 5, 4, 4, 5, 2, 5, 
	4, 5, 2, 5, 4, 5, 2, 5, 
	4, 4, 5, 2, 5, 4, 4, 2, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 6, 4, 2, 4, 
	6, 4, 2, 4, 4, 5, 3, 3, 
	3, 3, 3, 5, 5, 2, 5, 4, 
	5, 5, 4, 4, 5, 3, 3, 3, 
	3, 4, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 3, 
	3, 3, 3, 6, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	4, 5, 5, 4, 5, 4, 5, 5, 
	2, 4, 5, 3, 3, 3, 3, 3, 
	3, 3, 3, 3, 4, 5, 5, 4, 
	5, 4, 5, 5, 2, 4, 5, 3, 
	3, 3, 4, 4, 5, 5, 4, 5, 
	2, 5, 5, 4, 5, 4, 5, 2, 
	0, 11, 10
};

static const char _parse_tester_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 1, 2, 1, 1, 1, 1, 
	1, 1, 1, 0, 0, 0, 0, 0, 
	0, 0, 1, 1, 0, 0, 0, 0, 
	1, 1, 1, 0, 0, 0, 1, 1, 
	0, 0, 0, 1, 1, 1, 0, 0, 
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
	0, 0, 1, 4, 5, 5, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 1, 
	2, 1, 2, 1, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 1, 2, 1, 2, 1, 1, 0, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 2, 1, 1, 2, 
	2, 1, 1, 2, 5, 5, 0, 0, 
	0, 0, 0, 1, 1, 0, 4, 4, 
	5, 5, 1, 5, 5, 0, 0, 0, 
	0, 1, 1, 4, 5, 5, 1, 4, 
	0, 5, 5, 5, 5, 5, 5, 0, 
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

static const short _parse_tester_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 13, 15, 
	17, 19, 21, 25, 30, 32, 34, 36, 
	38, 40, 44, 49, 51, 53, 55, 57, 
	59, 61, 63, 69, 75, 77, 79, 81, 
	83, 88, 93, 98, 100, 102, 104, 108, 
	113, 115, 117, 119, 124, 129, 134, 136, 
	138, 140, 142, 147, 152, 160, 170, 180, 
	185, 194, 199, 201, 203, 205, 210, 215, 
	217, 219, 221, 223, 228, 233, 235, 237, 
	239, 241, 243, 245, 247, 249, 254, 259, 
	264, 266, 268, 272, 275, 278, 281, 291, 
	301, 310, 320, 329, 339, 342, 344, 346, 
	348, 350, 352, 356, 361, 367, 372, 377, 
	380, 386, 389, 393, 398, 400, 402, 404, 
	406, 408, 412, 417, 419, 421, 423, 425, 
	427, 429, 431, 433, 438, 441, 453, 457, 
	461, 465, 470, 476, 482, 488, 494, 501, 
	507, 512, 518, 526, 530, 537, 543, 551, 
	555, 562, 568, 576, 580, 587, 593, 599, 
	609, 612, 623, 634, 644, 655, 662, 666, 
	673, 680, 687, 691, 698, 705, 712, 716, 
	723, 730, 737, 743, 747, 751, 755, 763, 
	768, 774, 781, 788, 791, 798, 802, 806, 
	810, 814, 818, 822, 826, 830, 834, 839, 
	845, 851, 857, 864, 870, 873, 880, 886, 
	890, 894, 898, 904, 913, 924, 935, 941, 
	949, 953, 961, 967, 975, 979, 987, 993, 
	1001, 1005, 1013, 1019, 1027, 1031, 1039, 1045, 
	1051, 1059, 1063, 1071, 1077, 1083, 1091, 1095, 
	1103, 1109, 1117, 1121, 1129, 1135, 1143, 1147, 
	1155, 1161, 1167, 1175, 1179, 1187, 1193, 1199, 
	1202, 1211, 1217, 1221, 1228, 1237, 1243, 1247, 
	1254, 1263, 1269, 1273, 1280, 1289, 1295, 1299, 
	1306, 1315, 1321, 1325, 1332, 1341, 1347, 1351, 
	1358, 1367, 1373, 1377, 1384, 1393, 1399, 1403, 
	1410, 1419, 1425, 1429, 1436, 1446, 1457, 1461, 
	1465, 1469, 1473, 1477, 1484, 1491, 1494, 1504, 
	1513, 1524, 1535, 1541, 1551, 1562, 1566, 1570, 
	1574, 1578, 1584, 1590, 1599, 1610, 1621, 1627, 
	1637, 1640, 1651, 1662, 1672, 1683, 1693, 1704, 
	1708, 1712, 1716, 1721, 1729, 1733, 1737, 1741, 
	1746, 1755, 1766, 1777, 1787, 1798, 1807, 1818, 
	1829, 1832, 1842, 1853, 1857, 1861, 1865, 1869, 
	1874, 1883, 1894, 1905, 1915, 1926, 1935, 1946, 
	1957, 1960, 1970, 1981, 1985, 1989, 1993, 1997, 
	2001, 2005, 2009, 2013, 2018, 2027, 2038, 2049, 
	2059, 2070, 2079, 2090, 2101, 2104, 2114, 2125, 
	2129, 2133, 2138, 2144, 2153, 2164, 2175, 2181, 
	2191, 2194, 2205, 2216, 2226, 2237, 2247, 2258, 
	2261, 2262, 2275
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
	50, 51, 50, 1, 52, 51, 53, 51, 
	1, 55, 54, 56, 54, 1, 57, 1, 
	58, 1, 59, 1, 60, 1, 61, 61, 
	62, 61, 1, 63, 63, 64, 63, 1, 
	64, 64, 65, 64, 65, 65, 65, 1, 
	66, 66, 67, 69, 66, 68, 69, 69, 
	69, 1, 70, 70, 71, 73, 70, 72, 
	73, 73, 73, 1, 75, 74, 76, 74, 
	1, 75, 74, 76, 77, 74, 77, 77, 
	77, 1, 79, 78, 80, 78, 1, 81, 
	1, 82, 1, 83, 1, 84, 83, 85, 
	83, 1, 87, 86, 88, 86, 1, 89, 
	1, 90, 1, 91, 1, 92, 1, 92, 
	92, 93, 92, 1, 93, 93, 94, 93, 
	1, 95, 1, 96, 1, 97, 1, 98, 
	1, 99, 1, 100, 1, 101, 1, 102, 
	1, 102, 102, 103, 102, 1, 104, 103, 
	105, 103, 1, 107, 106, 108, 106, 1, 
	109, 1, 110, 1, 111, 111, 111, 1, 
	1, 104, 105, 1, 84, 85, 1, 75, 
	76, 113, 112, 114, 116, 112, 115, 116, 
	116, 116, 1, 75, 117, 76, 119, 117, 
	118, 119, 119, 119, 1, 118, 118, 119, 
	118, 118, 119, 119, 119, 1, 121, 120, 
	122, 119, 120, 118, 119, 119, 119, 1, 
	72, 72, 73, 72, 72, 73, 73, 73, 
	1, 123, 123, 124, 73, 123, 72, 73, 
	73, 73, 1, 1, 52, 53, 125, 1, 
	126, 1, 127, 1, 128, 1, 129, 1, 
	130, 130, 130, 1, 130, 130, 130, 131, 
	1, 133, 132, 134, 132, 135, 1, 137, 
	136, 138, 136, 1, 137, 139, 32, 139, 
	1, 1, 137, 138, 133, 132, 134, 132, 
	135, 1, 1, 28, 29, 140, 140, 140, 
	1, 140, 140, 140, 141, 1, 142, 1, 
	143, 1, 144, 1, 145, 1, 146, 1, 
	147, 147, 147, 1, 147, 147, 148, 147, 
	1, 149, 1, 150, 1, 151, 1, 152, 
	1, 153, 1, 154, 1, 155, 1, 156, 
	1, 28, 156, 29, 156, 1, 157, 159, 
	158, 157, 161, 160, 162, 163, 164, 165, 
	166, 167, 168, 160, 158, 157, 159, 169, 
	158, 157, 159, 170, 158, 157, 159, 171, 
	158, 157, 159, 172, 172, 158, 157, 159, 
	172, 172, 173, 158, 157, 159, 174, 174, 
	175, 158, 157, 159, 176, 177, 176, 158, 
	157, 159, 177, 177, 178, 158, 157, 159, 
	179, 180, 179, 181, 158, 157, 159, 179, 
	180, 179, 158, 157, 159, 182, 182, 158, 
	157, 159, 183, 184, 183, 158, 157, 159, 
	184, 185, 186, 184, 187, 158, 157, 159, 
	187, 158, 157, 159, 188, 189, 188, 190, 
	158, 157, 159, 188, 189, 188, 158, 157, 
	159, 191, 192, 193, 191, 194, 158, 157, 
	159, 194, 158, 157, 159, 195, 196, 195, 
	197, 158, 157, 159, 195, 196, 195, 158, 
	157, 159, 198, 199, 200, 198, 201, 158, 
	157, 159, 201, 158, 157, 159, 202, 203, 
	202, 204, 158, 157, 159, 202, 203, 202, 
	158, 157, 206, 205, 207, 205, 158, 157, 
	206, 205, 207, 208, 205, 208, 208, 208, 
	158, 157, 206, 207, 157, 210, 209, 211, 
	213, 209, 212, 213, 213, 213, 158, 157, 
	206, 214, 207, 216, 214, 215, 216, 216, 
	216, 158, 157, 159, 215, 216, 215, 215, 
	216, 216, 216, 158, 157, 218, 217, 219, 
	216, 217, 215, 216, 216, 216, 158, 157, 
	159, 202, 203, 202, 204, 158, 157, 159, 
	220, 158, 157, 159, 221, 222, 221, 223, 
	158, 157, 159, 221, 222, 221, 223, 158, 
	157, 159, 195, 196, 195, 197, 158, 157, 
	159, 224, 158, 157, 159, 225, 226, 225, 
	227, 158, 157, 159, 225, 226, 225, 227, 
	158, 157, 159, 188, 189, 188, 190, 158, 
	157, 159, 228, 158, 157, 159, 229, 230, 
	229, 231, 158, 157, 159, 229, 230, 229, 
	231, 158, 157, 159, 179, 180, 179, 181, 
	158, 157, 159, 174, 174, 175, 158, 157, 
	159, 232, 158, 157, 159, 233, 158, 157, 
	159, 234, 158, 157, 159, 236, 235, 235, 
	235, 235, 158, 157, 159, 237, 237, 158, 
	157, 159, 237, 237, 238, 158, 157, 240, 
	239, 241, 239, 242, 158, 157, 244, 243, 
	245, 243, 238, 158, 157, 244, 245, 157, 
	240, 239, 241, 239, 242, 158, 157, 159, 
	246, 158, 157, 159, 247, 158, 157, 159, 
	248, 158, 157, 159, 249, 158, 157, 159, 
	250, 158, 157, 159, 251, 158, 157, 159, 
	252, 158, 157, 159, 253, 158, 157, 159, 
	254, 158, 157, 159, 255, 255, 158, 157, 
	159, 255, 255, 256, 158, 157, 159, 257, 
	257, 258, 158, 157, 159, 257, 257, 259, 
	158, 157, 261, 260, 262, 260, 263, 158, 
	157, 261, 260, 262, 260, 158, 157, 261, 
	262, 157, 261, 260, 262, 260, 263, 158, 
	157, 159, 257, 257, 258, 158, 157, 159, 
	264, 158, 157, 159, 265, 158, 157, 159, 
	266, 158, 157, 159, 266, 267, 266, 158, 
	157, 159, 267, 268, 267, 268, 268, 268, 
	158, 157, 159, 269, 270, 272, 269, 271, 
	272, 272, 272, 158, 157, 159, 273, 274, 
	276, 273, 275, 276, 276, 276, 158, 157, 
	159, 277, 278, 277, 158, 157, 159, 278, 
	279, 279, 278, 280, 158, 157, 159, 281, 
	158, 157, 159, 282, 283, 284, 282, 281, 
	158, 157, 159, 285, 286, 285, 158, 157, 
	159, 287, 288, 288, 287, 289, 158, 157, 
	159, 290, 158, 157, 159, 291, 292, 293, 
	291, 290, 158, 157, 159, 294, 295, 294, 
	158, 157, 159, 296, 297, 297, 296, 298, 
	158, 157, 159, 299, 158, 157, 159, 300, 
	301, 302, 300, 299, 158, 157, 159, 303, 
	304, 303, 158, 157, 159, 305, 306, 306, 
	305, 307, 158, 157, 159, 308, 158, 157, 
	159, 309, 310, 311, 309, 308, 158, 157, 
	159, 312, 313, 312, 158, 157, 159, 314, 
	315, 314, 158, 157, 159, 315, 316, 316, 
	315, 317, 158, 157, 159, 318, 158, 157, 
	159, 319, 320, 321, 319, 318, 158, 157, 
	159, 322, 323, 322, 158, 157, 159, 324, 
	325, 324, 158, 157, 159, 325, 326, 326, 
	325, 327, 158, 157, 159, 328, 158, 157, 
	159, 329, 330, 331, 329, 328, 158, 157, 
	159, 332, 333, 332, 158, 157, 159, 334, 
	335, 335, 334, 336, 158, 157, 159, 337, 
	158, 157, 159, 338, 339, 340, 338, 337, 
	158, 157, 159, 341, 342, 341, 158, 157, 
	159, 343, 344, 344, 343, 345, 158, 157, 
	159, 346, 158, 157, 159, 347, 348, 349, 
	347, 346, 158, 157, 159, 350, 351, 350, 
	158, 157, 159, 352, 353, 352, 158, 157, 
	159, 353, 354, 354, 353, 355, 158, 157, 
	159, 356, 158, 157, 159, 357, 358, 359, 
	357, 356, 158, 157, 159, 360, 361, 360, 
	158, 157, 363, 362, 364, 362, 158, 157, 
	363, 364, 157, 159, 357, 358, 365, 365, 
	357, 359, 158, 157, 159, 366, 366, 367, 
	158, 157, 159, 367, 158, 157, 159, 357, 
	358, 357, 367, 158, 157, 159, 347, 348, 
	368, 368, 347, 349, 158, 157, 159, 369, 
	369, 370, 158, 157, 159, 370, 158, 157, 
	159, 347, 348, 347, 370, 158, 157, 159, 
	338, 339, 371, 371, 338, 340, 158, 157, 
	159, 372, 372, 373, 158, 157, 159, 373, 
	158, 157, 159, 338, 339, 338, 373, 158, 
	157, 159, 329, 330, 374, 374, 329, 331, 
	158, 157, 159, 375, 375, 376, 158, 157, 
	159, 376, 158, 157, 159, 329, 330, 329, 
	376, 158, 157, 159, 319, 320, 377, 377, 
	319, 321, 158, 157, 159, 378, 378, 379, 
	158, 157, 159, 379, 158, 157, 159, 319, 
	320, 319, 379, 158, 157, 159, 309, 310, 
	380, 380, 309, 311, 158, 157, 159, 381, 
	381, 382, 158, 157, 159, 382, 158, 157, 
	159, 309, 310, 309, 382, 158, 157, 159, 
	300, 301, 383, 383, 300, 302, 158, 157, 
	159, 384, 384, 385, 158, 157, 159, 385, 
	158, 157, 159, 300, 301, 300, 385, 158, 
	157, 159, 291, 292, 386, 386, 291, 293, 
	158, 157, 159, 387, 387, 388, 158, 157, 
	159, 388, 158, 157, 159, 291, 292, 291, 
	388, 158, 157, 159, 282, 283, 389, 389, 
	282, 284, 158, 157, 159, 390, 390, 391, 
	158, 157, 159, 391, 158, 157, 159, 282, 
	283, 282, 391, 158, 157, 159, 275, 276, 
	275, 275, 276, 276, 276, 158, 157, 159, 
	392, 393, 276, 392, 275, 276, 276, 276, 
	158, 157, 159, 394, 158, 157, 159, 395, 
	158, 157, 159, 396, 158, 157, 159, 397, 
	158, 157, 159, 398, 158, 157, 400, 399, 
	401, 402, 399, 158, 157, 404, 403, 405, 
	406, 403, 158, 157, 404, 405, 157, 159, 
	407, 408, 409, 407, 409, 409, 409, 158, 
	157, 159, 407, 409, 407, 409, 409, 409, 
	158, 157, 159, 410, 411, 413, 410, 412, 
	413, 413, 413, 158, 157, 159, 414, 408, 
	416, 414, 415, 416, 416, 416, 158, 157, 
	404, 408, 405, 408, 158, 157, 159, 415, 
	416, 415, 415, 416, 416, 416, 158, 157, 
	159, 417, 418, 416, 417, 415, 416, 416, 
	416, 158, 157, 159, 419, 158, 157, 159, 
	420, 158, 157, 159, 421, 158, 157, 159, 
	422, 158, 157, 159, 423, 424, 423, 158, 
	157, 159, 425, 426, 425, 158, 157, 159, 
	426, 427, 426, 427, 427, 427, 158, 157, 
	159, 428, 429, 431, 428, 430, 431, 431, 
	431, 158, 157, 159, 432, 433, 435, 432, 
	434, 435, 435, 435, 158, 157, 437, 436, 
	438, 436, 158, 157, 437, 436, 438, 439, 
	436, 439, 439, 439, 158, 157, 437, 438, 
	157, 441, 440, 442, 444, 440, 443, 444, 
	444, 444, 158, 157, 437, 445, 438, 447, 
	445, 446, 447, 447, 447, 158, 157, 159, 
	446, 447, 446, 446, 447, 447, 447, 158, 
	157, 449, 448, 450, 447, 448, 446, 447, 
	447, 447, 158, 157, 159, 434, 435, 434, 
	434, 435, 435, 435, 158, 157, 159, 451, 
	452, 435, 451, 434, 435, 435, 435, 158, 
	157, 159, 453, 158, 157, 159, 454, 158, 
	157, 159, 455, 158, 157, 159, 456, 456, 
	158, 157, 159, 456, 457, 458, 459, 456, 
	158, 157, 159, 460, 158, 157, 159, 461, 
	158, 157, 159, 462, 158, 157, 159, 463, 
	463, 158, 157, 159, 463, 464, 463, 464, 
	464, 464, 158, 157, 159, 465, 468, 467, 
	465, 466, 467, 467, 467, 158, 157, 159, 
	469, 472, 471, 469, 470, 471, 471, 471, 
	158, 157, 159, 470, 471, 470, 470, 471, 
	471, 471, 158, 157, 159, 473, 474, 471, 
	473, 470, 471, 471, 471, 158, 157, 159, 
	472, 475, 472, 475, 475, 475, 158, 157, 
	477, 476, 478, 480, 476, 479, 480, 480, 
	480, 158, 157, 482, 481, 483, 485, 481, 
	484, 485, 485, 485, 158, 157, 482, 483, 
	157, 159, 484, 485, 484, 484, 485, 485, 
	485, 158, 157, 487, 486, 488, 485, 486, 
	484, 485, 485, 485, 158, 157, 159, 489, 
	158, 157, 159, 490, 158, 157, 159, 491, 
	158, 157, 159, 492, 158, 157, 159, 493, 
	493, 158, 157, 159, 493, 494, 493, 494, 
	494, 494, 158, 157, 159, 495, 498, 497, 
	495, 496, 497, 497, 497, 158, 157, 159, 
	499, 502, 501, 499, 500, 501, 501, 501, 
	158, 157, 159, 500, 501, 500, 500, 501, 
	501, 501, 158, 157, 159, 503, 504, 501, 
	503, 500, 501, 501, 501, 158, 157, 159, 
	502, 505, 502, 505, 505, 505, 158, 157, 
	507, 506, 508, 510, 506, 509, 510, 510, 
	510, 158, 157, 512, 511, 513, 515, 511, 
	514, 515, 515, 515, 158, 157, 512, 513, 
	157, 159, 514, 515, 514, 514, 515, 515, 
	515, 158, 157, 517, 516, 518, 515, 516, 
	514, 515, 515, 515, 158, 157, 159, 519, 
	158, 157, 159, 520, 158, 157, 159, 521, 
	158, 157, 159, 522, 158, 157, 159, 523, 
	158, 157, 159, 524, 158, 157, 159, 525, 
	158, 157, 159, 526, 158, 157, 159, 527, 
	527, 158, 157, 159, 527, 528, 527, 528, 
	528, 528, 158, 157, 159, 529, 532, 531, 
	529, 530, 531, 531, 531, 158, 157, 159, 
	533, 536, 535, 533, 534, 535, 535, 535, 
	158, 157, 159, 534, 535, 534, 534, 535, 
	535, 535, 158, 157, 159, 537, 538, 535, 
	537, 534, 535, 535, 535, 158, 157, 159, 
	536, 539, 536, 539, 539, 539, 158, 157, 
	541, 540, 542, 544, 540, 543, 544, 544, 
	544, 158, 157, 546, 545, 547, 549, 545, 
	548, 549, 549, 549, 158, 157, 546, 547, 
	157, 159, 548, 549, 548, 548, 549, 549, 
	549, 158, 157, 551, 550, 552, 549, 550, 
	548, 549, 549, 549, 158, 157, 159, 553, 
	158, 157, 159, 554, 158, 157, 159, 555, 
	555, 158, 157, 159, 555, 556, 555, 158, 
	157, 159, 556, 557, 556, 557, 557, 557, 
	158, 157, 159, 558, 559, 561, 558, 560, 
	561, 561, 561, 158, 157, 159, 562, 563, 
	565, 562, 564, 565, 565, 565, 158, 157, 
	567, 566, 568, 566, 158, 157, 567, 566, 
	568, 569, 566, 569, 569, 569, 158, 157, 
	567, 568, 157, 571, 570, 572, 574, 570, 
	573, 574, 574, 574, 158, 157, 567, 575, 
	568, 577, 575, 576, 577, 577, 577, 158, 
	157, 159, 576, 577, 576, 576, 577, 577, 
	577, 158, 157, 579, 578, 580, 577, 578, 
	576, 577, 577, 577, 158, 157, 159, 564, 
	565, 564, 564, 565, 565, 565, 158, 157, 
	159, 581, 582, 565, 581, 564, 565, 565, 
	565, 158, 1, 584, 583, 111, 1, 161, 
	160, 583, 162, 163, 164, 165, 166, 167, 
	168, 160, 158, 585, 161, 160, 162, 163, 
	164, 165, 166, 167, 168, 160, 158, 0
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
	79, 83, 79, 79, 80, 81, 82, 392, 
	87, 57, 85, 88, 89, 87, 88, 89, 
	87, 57, 85, 54, 55, 94, 95, 96, 
	97, 98, 99, 100, 101, 102, 103, 104, 
	101, 102, 103, 102, 107, 108, 109, 110, 
	111, 112, 113, 114, 115, 116, 117, 118, 
	119, 120, 121, 122, 123, 393, 124, 393, 
	125, 394, 126, 171, 199, 286, 301, 319, 
	375, 127, 128, 129, 130, 131, 132, 170, 
	132, 133, 134, 135, 136, 169, 137, 137, 
	138, 139, 166, 140, 141, 142, 165, 142, 
	143, 162, 144, 145, 146, 161, 146, 147, 
	158, 148, 149, 150, 157, 151, 393, 152, 
	153, 154, 393, 152, 155, 156, 154, 155, 
	156, 154, 393, 152, 159, 149, 150, 160, 
	163, 145, 146, 164, 167, 141, 142, 168, 
	172, 173, 174, 175, 181, 176, 177, 178, 
	393, 179, 180, 178, 393, 179, 182, 183, 
	184, 185, 186, 187, 188, 189, 190, 191, 
	192, 193, 198, 194, 195, 393, 196, 197, 
	200, 201, 202, 203, 204, 205, 206, 284, 
	285, 205, 206, 284, 285, 206, 207, 208, 
	209, 209, 210, 211, 280, 210, 211, 211, 
	212, 213, 213, 214, 215, 276, 214, 215, 
	215, 216, 217, 217, 218, 219, 272, 218, 
	219, 219, 220, 221, 221, 222, 223, 268, 
	222, 223, 223, 224, 225, 226, 226, 227, 
	228, 264, 227, 228, 228, 229, 230, 231, 
	231, 232, 233, 260, 232, 233, 233, 234, 
	235, 235, 236, 237, 256, 236, 237, 237, 
	238, 239, 239, 240, 241, 252, 240, 241, 
	241, 242, 243, 244, 244, 245, 246, 248, 
	245, 246, 246, 393, 247, 249, 250, 251, 
	253, 254, 255, 257, 258, 259, 261, 262, 
	263, 265, 266, 267, 269, 270, 271, 273, 
	274, 275, 277, 278, 279, 281, 282, 283, 
	205, 206, 287, 288, 289, 290, 291, 292, 
	393, 293, 294, 292, 393, 293, 294, 295, 
	298, 296, 297, 298, 299, 300, 297, 299, 
	300, 297, 298, 302, 303, 304, 305, 306, 
	307, 306, 307, 308, 309, 310, 317, 318, 
	309, 310, 317, 318, 311, 393, 312, 313, 
	314, 393, 312, 315, 316, 314, 315, 316, 
	314, 393, 312, 309, 310, 320, 321, 322, 
	323, 324, 339, 355, 325, 326, 327, 328, 
	329, 330, 331, 332, 333, 330, 331, 332, 
	333, 330, 333, 334, 335, 393, 336, 337, 
	338, 335, 393, 336, 337, 338, 335, 393, 
	336, 340, 341, 342, 343, 344, 345, 346, 
	347, 348, 349, 346, 347, 348, 349, 346, 
	349, 350, 351, 393, 352, 353, 354, 351, 
	393, 352, 353, 354, 351, 393, 352, 356, 
	357, 358, 359, 360, 361, 362, 363, 364, 
	365, 366, 367, 368, 369, 366, 367, 368, 
	369, 366, 369, 370, 371, 393, 372, 373, 
	374, 371, 393, 372, 373, 374, 371, 393, 
	372, 376, 377, 378, 379, 380, 381, 382, 
	389, 390, 381, 382, 389, 390, 383, 393, 
	384, 385, 386, 393, 384, 387, 388, 386, 
	387, 388, 386, 393, 384, 381, 382, 391, 
	393, 393
};

static const short _parse_tester_trans_actions_wi[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 43, 43, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 178, 0, 0, 1, 
	0, 0, 0, 0, 0, 65, 65, 0, 
	0, 0, 137, 137, 17, 134, 0, 0, 
	0, 19, 0, 186, 0, 0, 0, 1, 
	0, 0, 0, 0, 83, 0, 0, 1, 
	67, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	194, 0, 0, 1, 0, 0, 0, 0, 
	140, 275, 140, 17, 134, 0, 0, 19, 
	23, 237, 23, 21, 21, 0, 0, 0, 
	0, 0, 0, 0, 73, 152, 73, 5, 
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 81, 0, 92, 
	0, 218, 0, 0, 0, 69, 0, 149, 
	39, 0, 0, 0, 0, 0, 25, 5, 
	0, 0, 0, 0, 0, 5, 27, 0, 
	0, 0, 0, 0, 0, 29, 5, 0, 
	0, 0, 0, 0, 31, 5, 0, 0, 
	0, 0, 0, 33, 5, 0, 158, 0, 
	0, 206, 299, 206, 17, 134, 0, 0, 
	19, 143, 293, 143, 0, 11, 101, 5, 
	0, 11, 98, 5, 0, 11, 95, 5, 
	0, 0, 0, 37, 0, 0, 0, 35, 
	214, 35, 5, 0, 86, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 5, 0, 0, 162, 0, 9, 
	0, 0, 0, 0, 0, 137, 210, 17, 
	134, 0, 45, 0, 19, 0, 0, 104, 
	104, 13, 15, 107, 13, 0, 47, 0, 
	104, 104, 13, 15, 110, 13, 0, 49, 
	0, 104, 104, 13, 15, 113, 13, 0, 
	51, 0, 104, 104, 13, 15, 116, 13, 
	0, 53, 0, 0, 104, 104, 13, 15, 
	119, 13, 0, 55, 0, 0, 104, 104, 
	13, 15, 122, 13, 0, 57, 0, 104, 
	104, 13, 15, 125, 13, 0, 59, 0, 
	104, 104, 13, 15, 128, 13, 0, 61, 
	0, 0, 104, 104, 13, 15, 131, 13, 
	0, 63, 0, 182, 0, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	21, 146, 0, 0, 0, 0, 0, 71, 
	252, 71, 71, 0, 198, 0, 0, 0, 
	0, 0, 137, 137, 17, 134, 0, 0, 
	19, 21, 21, 0, 0, 0, 0, 65, 
	65, 0, 0, 0, 137, 137, 17, 134, 
	0, 0, 0, 19, 0, 190, 0, 0, 
	140, 281, 140, 17, 134, 0, 0, 19, 
	23, 242, 23, 21, 21, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 137, 17, 134, 137, 0, 0, 19, 
	0, 21, 21, 0, 140, 257, 140, 17, 
	134, 0, 166, 0, 0, 19, 23, 222, 
	23, 0, 0, 0, 0, 0, 0, 137, 
	17, 134, 137, 0, 0, 19, 0, 21, 
	21, 0, 140, 269, 140, 17, 134, 0, 
	174, 0, 0, 19, 23, 232, 23, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 137, 17, 134, 137, 0, 0, 19, 
	0, 21, 21, 0, 140, 287, 140, 17, 
	134, 0, 202, 0, 0, 19, 23, 247, 
	23, 0, 0, 0, 0, 0, 137, 137, 
	17, 134, 0, 0, 0, 19, 0, 170, 
	0, 0, 140, 263, 140, 17, 134, 0, 
	0, 19, 23, 227, 23, 21, 21, 0, 
	89, 79
};

static const short _parse_tester_to_state_actions[] = {
	0, 75, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 75, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 75, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 75, 
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 41, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 155, 0
};

static const short _parse_tester_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 77, 0
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
	158, 158, 158, 158, 158, 158, 158, 0, 
	0, 0, 586
};

static const int parse_tester_start = 1;
static const int parse_tester_first_final = 392;
static const int parse_tester_error = 0;

static const int parse_tester_en_group_scanner = 393;
static const int parse_tester_en_main = 1;

#line 1390 "NanorexMMPImportExportRagelTest.rl"
	
#line 13499 "NanorexMMPImportExportRagelTest.cpp"
	{
	cs = parse_tester_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 1391 "NanorexMMPImportExportRagelTest.rl"
	
#line 13509 "NanorexMMPImportExportRagelTest.cpp"
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
	case 58:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = p;}
	break;
#line 13530 "NanorexMMPImportExportRagelTest.cpp"
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
#line 53 "NanorexMMPImportExportRagelTest.rl"
	{stringVal.clear(); /*stringVal = stringVal + fc;*/ doubleVal = HUGE_VAL;}
	break;
	case 7:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{stringVal = stringVal + (*p);}
	break;
	case 8:
#line 55 "NanorexMMPImportExportRagelTest.rl"
	{doubleVal = atof(stringVal.c_str());}
	break;
	case 9:
#line 73 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 10:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 11:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 12:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 13:
#line 29 "NanorexMMPImportExportRagelTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/ }
	break;
	case 14:
#line 34 "NanorexMMPImportExportRagelTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 38 "NanorexMMPImportExportRagelTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 39 "NanorexMMPImportExportRagelTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 50 "NanorexMMPImportExportRagelTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newAtom(atomId, atomicNum, x, y, z, atomStyle); }
	break;
	case 20:
#line 71 "NanorexMMPImportExportRagelTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 77 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal = *p; }
	break;
	case 22:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 23:
#line 102 "NanorexMMPImportExportRagelTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 24:
#line 9 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 26:
#line 16 "NanorexMMPImportExportRagelTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 27:
#line 24 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 28:
#line 35 "NanorexMMPImportExportRagelTest.rl"
	{ newChunkInfo(stringVal, stringVal2); }
	break;
	case 29:
#line 26 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 30:
#line 30 "NanorexMMPImportExportRagelTest.rl"
	{ newViewDataGroup(); }
	break;
	case 31:
#line 37 "NanorexMMPImportExportRagelTest.rl"
	{csysViewName = stringVal;}
	break;
	case 32:
#line 40 "NanorexMMPImportExportRagelTest.rl"
	{csysQw=doubleVal;}
	break;
	case 33:
#line 41 "NanorexMMPImportExportRagelTest.rl"
	{csysQx=doubleVal;}
	break;
	case 34:
#line 42 "NanorexMMPImportExportRagelTest.rl"
	{csysQy=doubleVal;}
	break;
	case 35:
#line 43 "NanorexMMPImportExportRagelTest.rl"
	{csysQz=doubleVal;}
	break;
	case 36:
#line 45 "NanorexMMPImportExportRagelTest.rl"
	{csysScale=doubleVal;}
	break;
	case 37:
#line 47 "NanorexMMPImportExportRagelTest.rl"
	{csysPovX=doubleVal;}
	break;
	case 38:
#line 48 "NanorexMMPImportExportRagelTest.rl"
	{csysPovY=doubleVal;}
	break;
	case 39:
#line 49 "NanorexMMPImportExportRagelTest.rl"
	{csysPovZ=doubleVal;}
	break;
	case 40:
#line 51 "NanorexMMPImportExportRagelTest.rl"
	{csysZoomFactor=doubleVal;}
	break;
	case 41:
#line 54 "NanorexMMPImportExportRagelTest.rl"
	{ newNamedView(csysViewName, csysQw, csysQx, csysQy, csysQz, csysScale,
		                 csysPovX, csysPovY, csysPovZ, csysZoomFactor);
		}
	break;
	case 42:
#line 61 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); }
	break;
	case 43:
#line 67 "NanorexMMPImportExportRagelTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 44:
#line 74 "NanorexMMPImportExportRagelTest.rl"
	{ end1(); }
	break;
	case 45:
#line 78 "NanorexMMPImportExportRagelTest.rl"
	{ lineStart = p; }
	break;
	case 46:
#line 83 "NanorexMMPImportExportRagelTest.rl"
	{ newClipboardGroup(); }
	break;
	case 47:
#line 87 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 48:
#line 88 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal.clear(); }
	break;
	case 49:
#line 94 "NanorexMMPImportExportRagelTest.rl"
	{ endGroup(stringVal); }
	break;
	case 50:
#line 98 "NanorexMMPImportExportRagelTest.rl"
	{lineStart=p;}
	break;
	case 51:
#line 108 "NanorexMMPImportExportRagelTest.rl"
	{ newOpenGroupInfo(stringVal, stringVal2); }
	break;
	case 52:
#line 1164 "NanorexMMPImportExportRagelTest.rl"
	{ kelvinTemp = intVal; }
	break;
	case 53:
#line 1178 "NanorexMMPImportExportRagelTest.rl"
	{ /*cerr << "*p=" << *p << endl;*/ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 54:
#line 1181 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 55:
#line 1186 "NanorexMMPImportExportRagelTest.rl"
	{ p--; {stack[top++] = cs; cs = 393; goto _again;} }
	break;
	case 59:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 60:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{act = 12;}
	break;
	case 61:
#line 116 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 62:
#line 117 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 63:
#line 118 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 64:
#line 119 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
	case 65:
#line 120 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 66:
#line 121 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 67:
#line 122 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 68:
#line 123 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 69:
#line 124 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 70:
#line 125 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 71:
#line 128 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;}
	break;
	case 72:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p+1;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 73:
#line 130 "NanorexMMPImportExportRagelTest.rl"
	{te = p;p--;{ cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}}
	break;
	case 74:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 12:
	{{p = ((te))-1;} cerr << lineNum << ": Syntax error or unsupported statement:\n\t";
			  std::copy(ts, te, std::ostream_iterator<char>(cerr));
			  cerr << endl;
			}
	break;
	default: break;
	}
	}
	break;
#line 13910 "NanorexMMPImportExportRagelTest.cpp"
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
	case 25:
#line 11 "NanorexMMPImportExportRagelTest.rl"
	{ stringVal2.clear(); /* 'style' string optional */ }
	break;
	case 56:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{ts = 0;}
	break;
	case 57:
#line 1 "NanorexMMPImportExportRagelTest.rl"
	{act = 0;}
	break;
#line 13939 "NanorexMMPImportExportRagelTest.cpp"
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
#line 1392 "NanorexMMPImportExportRagelTest.rl"
}

