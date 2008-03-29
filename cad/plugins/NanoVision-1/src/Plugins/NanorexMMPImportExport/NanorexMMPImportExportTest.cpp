#line 1 "NanorexMMPImportExportTest.rl"
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


#line 85 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	#line 98 "NanorexMMPImportExportTest.rl"
	
#line 89 "NanorexMMPImportExportTest.cpp"
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
	109, 116, 121, 126, 138, 140, 153, 166, 
	178, 191, 198, 200, 207, 214, 221, 223, 
	230, 237, 244, 246, 253, 260, 267, 273
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
	97, 122, -1, 10, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	45, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 11, 13, 48, 57, 48, 57, 
	9, 32, 41, 11, 13, 48, 57, 9, 
	32, 41, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 48, 57, 9, 
	32, 44, 11, 13, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 48, 57, 9, 32, 
	44, 11, 13, 48, 57, 9, 32, 44, 
	11, 13, 48, 57, 9, 32, 41, 11, 
	13, 48, 57, 9, 32, 11, 13, 48, 
	57, 0
};

static const char _atom_decl_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 2, 5, 5, 4, 
	5, 3, 0, 3, 3, 3, 0, 3, 
	3, 3, 0, 3, 3, 3, 2, 0
};

static const char _atom_decl_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 0, 4, 4, 4, 
	4, 2, 1, 2, 2, 2, 1, 2, 
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
	1, 40, 41, 44, 43, 45, 46, 47, 
	43, 47, 47, 47, 1, 40, 48, 41, 
	49, 50, 48, 50, 50, 50, 1, 49, 
	49, 49, 50, 49, 50, 50, 50, 1, 
	52, 51, 53, 49, 50, 51, 50, 50, 
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

#line 99 "NanorexMMPImportExportTest.rl"
	
#line 250 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_decl_line_test_start;
	}
#line 100 "NanorexMMPImportExportTest.rl"
	
#line 256 "NanorexMMPImportExportTest.cpp"
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
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 47 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 4:
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 5:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 6:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 7:
#line 26 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 8:
#line 31 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 9:
#line 34 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 10:
#line 35 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 11:
#line 36 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 12:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 13:
#line 52 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(atomStyle); 
		newAtom(atomId, atomicNum, x, y, z, atomStyle);
		// cerr << "p = " << p << endl;
	}
	break;
	case 14:
#line 80 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 397 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_decl_line_test_actions + _atom_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 38 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 410 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	_out: {}
	}
#line 101 "NanorexMMPImportExportTest.rl"
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


#line 154 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;

	#line 165 "NanorexMMPImportExportTest.rl"
	
#line 476 "NanorexMMPImportExportTest.cpp"
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

#line 166 "NanorexMMPImportExportTest.rl"
	
#line 549 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_line_test_start;
	}
#line 167 "NanorexMMPImportExportTest.rl"
	
#line 555 "NanorexMMPImportExportTest.cpp"
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
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 69 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 4:
#line 75 "NanorexMMPImportExportTest.rl"
	{ stringVal = (*p); }
	break;
	case 5:
#line 149 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 654 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_line_test_actions + _bond_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 38 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
#line 667 "NanorexMMPImportExportTest.cpp"
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
#line 149 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 689 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 168 "NanorexMMPImportExportTest.rl"
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


#line 209 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 221 "NanorexMMPImportExportTest.rl"
	
#line 740 "NanorexMMPImportExportTest.cpp"
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

#line 222 "NanorexMMPImportExportTest.rl"
	
#line 835 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_direction_line_test_start;
	}
#line 223 "NanorexMMPImportExportTest.rl"
	
#line 841 "NanorexMMPImportExportTest.cpp"
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
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 44 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 80 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 6:
#line 204 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 940 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_direction_line_test_actions + _bond_direction_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 38 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 43 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 957 "NanorexMMPImportExportTest.cpp"
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
#line 204 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 979 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 224 "NanorexMMPImportExportTest.rl"
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


#line 279 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 290 "NanorexMMPImportExportTest.rl"
	
#line 1042 "NanorexMMPImportExportTest.cpp"
static const char _info_atom_line_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 6, 2, 0, 5, 2, 1, 
	2, 2, 1, 3, 2, 1, 4, 3, 
	4, 0, 5, 4, 1, 4, 0, 5
	
};

static const unsigned char _info_atom_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 11, 16, 
	17, 18, 19, 23, 34, 47, 60, 72, 
	85, 96, 109, 122, 124, 136, 149
};

static const char _info_atom_line_test_trans_keys[] = {
	32, 105, 9, 13, 110, 102, 111, 9, 
	32, 11, 13, 9, 32, 97, 11, 13, 
	116, 111, 109, 9, 32, 11, 13, 9, 
	32, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 45, 61, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 45, 61, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 45, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 45, 61, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 9, 32, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 9, 32, 45, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 0
};

static const char _info_atom_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 2, 3, 1, 
	1, 1, 2, 3, 5, 5, 4, 5, 
	3, 5, 5, 2, 4, 5, 0
};

static const char _info_atom_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 4, 4, 4, 4, 
	4, 4, 4, 0, 4, 4, 0
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
	11, 12, 12, 12, 0, 13, 13, 14, 
	16, 15, 13, 15, 15, 15, 0, 17, 
	17, 18, 20, 19, 17, 19, 19, 19, 
	0, 18, 18, 18, 19, 18, 19, 19, 
	19, 0, 21, 21, 18, 22, 19, 21, 
	19, 19, 19, 0, 20, 20, 23, 20, 
	23, 23, 23, 0, 25, 24, 26, 27, 
	28, 24, 28, 28, 28, 0, 30, 29, 
	31, 32, 33, 29, 33, 33, 33, 0, 
	0, 30, 31, 32, 32, 32, 33, 32, 
	33, 33, 33, 0, 35, 34, 36, 32, 
	33, 34, 33, 33, 33, 0, 0, 0
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

#line 291 "NanorexMMPImportExportTest.rl"
	
#line 1146 "NanorexMMPImportExportTest.cpp"
	{
	cs = info_atom_line_test_start;
	}
#line 292 "NanorexMMPImportExportTest.rl"
	
#line 1152 "NanorexMMPImportExportTest.cpp"
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
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 92 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 89 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 6:
#line 274 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1265 "NanorexMMPImportExportTest.cpp"
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
#line 274 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1288 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 293 "NanorexMMPImportExportTest.rl"
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


#line 355 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 366 "NanorexMMPImportExportTest.rl"
	
#line 1357 "NanorexMMPImportExportTest.cpp"
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
	3, 6, 8, 15, 3, 9, 0, 20, 
	4, 6, 9, 0, 20, 4, 8, 15, 
	0, 16, 5, 6, 8, 15, 0, 16
	
};

static const short _atom_stmt_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 11, 17, 
	23, 28, 34, 41, 46, 50, 55, 63, 
	65, 72, 77, 85, 87, 94, 99, 107, 
	109, 116, 121, 126, 138, 143, 144, 145, 
	146, 152, 156, 162, 169, 176, 177, 178, 
	179, 183, 188, 189, 190, 191, 195, 206, 
	219, 232, 244, 257, 268, 281, 294, 296, 
	308, 321, 323, 330, 331, 332, 333, 334, 
	335, 336, 337, 338, 339, 343, 349, 355, 
	361, 368, 373, 375, 382, 388, 390, 403, 
	416, 428, 441, 448, 450, 457, 464, 471, 
	473, 480, 487, 494, 496, 503, 510, 517, 
	523, 528
};

static const char _atom_stmt_test_trans_keys[] = {
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
	97, 122, 32, 98, 105, 9, 13, 111, 
	110, 100, 95, 97, 99, 103, 49, 51, 
	9, 32, 11, 13, 9, 32, 11, 13, 
	48, 57, 10, 32, 35, 9, 13, 48, 
	57, 10, 32, 35, 9, 13, 48, 57, 
	110, 102, 111, 9, 32, 11, 13, 9, 
	32, 97, 11, 13, 116, 111, 109, 9, 
	32, 11, 13, 9, 32, 95, 11, 13, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	45, 61, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 9, 32, 45, 61, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 45, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 45, 61, 
	95, 11, 13, 48, 57, 65, 90, 97, 
	122, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	9, 32, 45, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 10, 32, 35, 9, 13, 
	48, 57, 100, 105, 114, 101, 99, 116, 
	105, 111, 110, 9, 32, 11, 13, 9, 
	32, 11, 13, 48, 57, 9, 32, 11, 
	13, 48, 57, 9, 32, 11, 13, 48, 
	57, 10, 32, 35, 9, 13, 48, 57, 
	10, 32, 35, 9, 13, -1, 10, 10, 
	32, 35, 9, 13, 48, 57, 9, 32, 
	11, 13, 48, 57, -1, 10, 10, 32, 
	35, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 45, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
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
	13, 48, 57, 32, 98, 105, 9, 13, 
	32, 98, 105, 9, 13, 0
};

static const char _atom_stmt_test_single_lengths[] = {
	0, 2, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 3, 1, 1, 1, 
	4, 2, 2, 3, 3, 1, 1, 1, 
	2, 3, 1, 1, 1, 2, 3, 5, 
	5, 4, 5, 3, 5, 5, 2, 4, 
	5, 2, 3, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 2, 2, 2, 2, 
	3, 3, 2, 3, 2, 2, 5, 5, 
	4, 5, 3, 0, 3, 3, 3, 0, 
	3, 3, 3, 0, 3, 3, 3, 2, 
	3, 3
};

static const char _atom_stmt_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 1, 0, 0, 0, 
	1, 1, 2, 2, 2, 0, 0, 0, 
	1, 1, 0, 0, 0, 1, 4, 4, 
	4, 4, 4, 4, 4, 4, 0, 4, 
	4, 0, 2, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 1, 2, 2, 2, 
	2, 1, 0, 2, 2, 0, 4, 4, 
	4, 4, 2, 1, 2, 2, 2, 1, 
	2, 2, 2, 1, 2, 2, 2, 2, 
	1, 1
};

static const short _atom_stmt_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 14, 19, 
	24, 29, 34, 40, 45, 49, 54, 61, 
	63, 69, 74, 81, 83, 89, 94, 101, 
	103, 109, 114, 119, 128, 133, 135, 137, 
	139, 145, 149, 154, 160, 166, 168, 170, 
	172, 176, 181, 183, 185, 187, 191, 199, 
	209, 219, 228, 238, 246, 256, 266, 269, 
	278, 288, 291, 297, 299, 301, 303, 305, 
	307, 309, 311, 313, 315, 319, 324, 329, 
	334, 340, 345, 348, 354, 359, 362, 372, 
	382, 391, 401, 407, 409, 415, 421, 427, 
	429, 435, 441, 447, 449, 455, 461, 467, 
	472, 477
};

static const unsigned char _atom_stmt_test_indicies[] = {
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
	44, 45, 46, 44, 43, 47, 43, 48, 
	43, 49, 43, 51, 50, 50, 50, 50, 
	43, 52, 52, 52, 43, 52, 52, 52, 
	53, 43, 55, 54, 56, 54, 57, 43, 
	59, 58, 60, 58, 53, 43, 61, 43, 
	62, 43, 63, 43, 64, 64, 64, 43, 
	64, 64, 65, 64, 43, 66, 43, 67, 
	43, 68, 43, 69, 69, 69, 43, 69, 
	69, 70, 69, 70, 70, 70, 43, 71, 
	71, 72, 74, 73, 71, 73, 73, 73, 
	43, 75, 75, 76, 78, 77, 75, 77, 
	77, 77, 43, 76, 76, 76, 77, 76, 
	77, 77, 77, 43, 79, 79, 76, 80, 
	77, 79, 77, 77, 77, 43, 78, 78, 
	81, 78, 81, 81, 81, 43, 83, 82, 
	84, 85, 86, 82, 86, 86, 86, 43, 
	88, 87, 89, 90, 91, 87, 91, 91, 
	91, 43, 43, 88, 89, 90, 90, 90, 
	91, 90, 91, 91, 91, 43, 93, 92, 
	94, 90, 91, 92, 91, 91, 91, 43, 
	43, 59, 60, 55, 54, 56, 54, 57, 
	43, 95, 43, 96, 43, 97, 43, 98, 
	43, 99, 43, 100, 43, 101, 43, 102, 
	43, 103, 43, 104, 104, 104, 43, 104, 
	104, 104, 105, 43, 106, 106, 106, 107, 
	43, 106, 106, 106, 108, 43, 110, 109, 
	111, 109, 112, 43, 110, 109, 111, 109, 
	43, 43, 110, 111, 110, 109, 111, 109, 
	112, 43, 106, 106, 106, 107, 43, 1, 
	40, 41, 114, 113, 115, 116, 117, 113, 
	117, 117, 117, 1, 40, 118, 41, 119, 
	120, 118, 120, 120, 120, 1, 119, 119, 
	119, 120, 119, 120, 120, 120, 1, 122, 
	121, 123, 119, 120, 121, 120, 120, 120, 
	1, 36, 36, 37, 36, 38, 1, 124, 
	1, 125, 125, 126, 125, 127, 1, 125, 
	125, 126, 125, 127, 1, 29, 29, 30, 
	29, 31, 1, 128, 1, 129, 129, 130, 
	129, 131, 1, 129, 129, 130, 129, 131, 
	1, 22, 22, 23, 22, 24, 1, 132, 
	1, 133, 133, 134, 133, 135, 1, 133, 
	133, 134, 133, 135, 1, 13, 13, 14, 
	13, 15, 1, 8, 8, 8, 9, 1, 
	136, 137, 138, 136, 43, 44, 45, 46, 
	44, 43, 0
};

static const char _atom_stmt_test_trans_targs_wi[] = {
	1, 0, 2, 3, 4, 5, 6, 7, 
	8, 95, 8, 9, 10, 11, 12, 94, 
	13, 13, 14, 15, 91, 16, 17, 18, 
	90, 18, 19, 87, 20, 21, 22, 86, 
	22, 23, 83, 24, 25, 26, 82, 27, 
	96, 77, 78, 0, 28, 29, 37, 30, 
	31, 32, 33, 59, 34, 35, 36, 97, 
	57, 58, 36, 97, 57, 38, 39, 40, 
	41, 42, 43, 44, 45, 46, 47, 48, 
	49, 50, 51, 48, 49, 50, 51, 48, 
	51, 52, 53, 97, 54, 55, 56, 53, 
	97, 54, 55, 56, 53, 97, 54, 60, 
	61, 62, 63, 64, 65, 66, 67, 68, 
	69, 70, 71, 76, 72, 73, 97, 74, 
	75, 79, 96, 77, 80, 81, 79, 80, 
	81, 79, 96, 77, 84, 25, 26, 85, 
	88, 21, 22, 89, 92, 17, 18, 93, 
	28, 29, 37
};

static const char _atom_stmt_test_trans_actions_wi[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	21, 5, 0, 0, 0, 0, 0, 5, 
	23, 0, 0, 0, 0, 0, 0, 25, 
	5, 0, 0, 0, 0, 0, 27, 5, 
	0, 0, 0, 0, 0, 29, 5, 0, 
	39, 0, 0, 37, 0, 0, 0, 0, 
	0, 0, 33, 0, 0, 0, 31, 69, 
	31, 5, 0, 1, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 60, 
	13, 57, 60, 0, 0, 15, 0, 17, 
	17, 0, 63, 80, 63, 13, 57, 0, 
	45, 0, 0, 15, 19, 76, 19, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 5, 0, 0, 42, 0, 
	9, 72, 90, 72, 13, 57, 0, 0, 
	15, 66, 85, 66, 0, 11, 54, 5, 
	0, 11, 51, 5, 0, 11, 48, 5, 
	35, 35, 35
};

static const char _atom_stmt_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 3, 0, 
	7, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	0, 0
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
	37, 37, 37, 37, 37, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	35, 0
};

static const int atom_stmt_test_start = 1;
static const int atom_stmt_test_first_final = 96;
static const int atom_stmt_test_error = 0;

static const int atom_stmt_test_en_main = 1;

#line 367 "NanorexMMPImportExportTest.rl"
	
#line 1654 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_stmt_test_start;
	}
#line 368 "NanorexMMPImportExportTest.rl"
	
#line 1660 "NanorexMMPImportExportTest.cpp"
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
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 44 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 47 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 92 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 26 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 11:
#line 31 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 34 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 35 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 36 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 52 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(atomStyle); 
		newAtom(atomId, atomicNum, x, y, z, atomStyle);
		// cerr << "p = " << p << endl;
	}
	break;
	case 17:
#line 69 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 75 "NanorexMMPImportExportTest.rl"
	{ stringVal = (*p); }
	break;
	case 19:
#line 80 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 89 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 348 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 350 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 1839 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_stmt_test_actions + _atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 38 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 43 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 1856 "NanorexMMPImportExportTest.cpp"
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
#line 348 "NanorexMMPImportExportTest.rl"
	{newAtom(atomId, atomicNum, x, y, z, atomStyle);}
	break;
	case 22:
#line 350 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 1882 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 369 "NanorexMMPImportExportTest.rl"
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


#line 510 "NanorexMMPImportExportTest.rl"



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
	
	#line 526 "NanorexMMPImportExportTest.rl"
	
#line 2012 "NanorexMMPImportExportTest.cpp"
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
	110, 117, 122, 127, 139, 141, 154, 167, 
	179, 192, 199, 201, 208, 215, 222, 224, 
	231, 238, 245, 247, 254, 261, 268, 274, 
	283, 285, 286, 287, 288, 292, 298, 304, 
	309, 315, 322, 327, 331, 336, 344, 346, 
	353, 358, 366, 368, 375, 380, 388, 390, 
	397, 402, 407, 419, 421, 434, 447, 459, 
	472, 479, 481, 488, 495, 502, 504, 511, 
	518, 525, 527, 534, 541, 548, 554, 555, 
	556, 557, 563, 567, 573, 580, 587, 589, 
	596, 597, 598, 599, 600, 601, 602, 603, 
	604, 605, 609, 615, 621, 627, 634, 639, 
	641, 648, 654, 655, 656, 657, 661, 666, 
	667, 668, 669, 673, 684, 697, 710, 722, 
	735, 746, 759, 772, 774, 786, 799, 804
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
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 45, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
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
	48, 57, 0, 10, 32, 35, 97, 98, 
	105, 9, 13, -1, 10, 116, 111, 109, 
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
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 45, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
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
	9, 32, 11, 13, 48, 57, 110, 102, 
	111, 9, 32, 11, 13, 9, 32, 97, 
	11, 13, 116, 111, 109, 9, 32, 11, 
	13, 9, 32, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 9, 32, 45, 61, 
	95, 11, 13, 48, 57, 65, 90, 97, 
	122, 9, 32, 45, 61, 95, 11, 13, 
	48, 57, 65, 90, 97, 122, 9, 32, 
	45, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 45, 61, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 9, 32, 
	45, 95, 11, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 97, 9, 13, 0, 10, 32, 35, 
	97, 98, 105, 9, 13, 0
};

static const char _multiple_atom_stmt_test_single_lengths[] = {
	0, 3, 1, 1, 1, 2, 2, 2, 
	3, 2, 3, 3, 2, 3, 4, 0, 
	3, 3, 4, 0, 3, 3, 4, 0, 
	3, 3, 3, 4, 2, 5, 5, 4, 
	5, 3, 0, 3, 3, 3, 0, 3, 
	3, 3, 0, 3, 3, 3, 2, 7, 
	2, 1, 1, 1, 2, 2, 2, 3, 
	2, 3, 3, 2, 3, 4, 0, 3, 
	3, 4, 0, 3, 3, 4, 0, 3, 
	3, 3, 4, 2, 5, 5, 4, 5, 
	3, 0, 3, 3, 3, 0, 3, 3, 
	3, 0, 3, 3, 3, 2, 1, 1, 
	1, 4, 2, 2, 3, 3, 2, 3, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 2, 2, 2, 2, 3, 3, 2, 
	3, 2, 1, 1, 1, 2, 3, 1, 
	1, 1, 2, 3, 5, 5, 4, 5, 
	3, 5, 5, 2, 4, 5, 3, 7
};

static const char _multiple_atom_stmt_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 0, 4, 4, 4, 
	4, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 2, 1, 
	0, 0, 0, 0, 1, 2, 2, 1, 
	2, 2, 1, 1, 1, 2, 1, 2, 
	1, 2, 1, 2, 1, 2, 1, 2, 
	1, 1, 4, 0, 4, 4, 4, 4, 
	2, 1, 2, 2, 2, 1, 2, 2, 
	2, 1, 2, 2, 2, 2, 0, 0, 
	0, 1, 1, 2, 2, 2, 0, 2, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 2, 2, 2, 2, 1, 0, 
	2, 2, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 4, 4, 4, 4, 
	4, 4, 4, 0, 4, 4, 1, 1
};

static const short _multiple_atom_stmt_test_index_offsets[] = {
	0, 0, 5, 7, 9, 11, 15, 20, 
	25, 30, 35, 41, 46, 50, 55, 62, 
	64, 70, 75, 82, 84, 90, 95, 102, 
	104, 110, 115, 120, 129, 132, 142, 152, 
	161, 171, 177, 179, 185, 191, 197, 199, 
	205, 211, 217, 219, 225, 231, 237, 242, 
	251, 254, 256, 258, 260, 264, 269, 274, 
	279, 284, 290, 295, 299, 304, 311, 313, 
	319, 324, 331, 333, 339, 344, 351, 353, 
	359, 364, 369, 378, 381, 391, 401, 410, 
	420, 426, 428, 434, 440, 446, 448, 454, 
	460, 466, 468, 474, 480, 486, 491, 493, 
	495, 497, 503, 507, 512, 518, 524, 527, 
	533, 535, 537, 539, 541, 543, 545, 547, 
	549, 551, 555, 560, 565, 570, 576, 581, 
	584, 590, 595, 597, 599, 601, 605, 610, 
	612, 614, 616, 620, 628, 638, 648, 657, 
	667, 675, 685, 695, 698, 707, 717, 722
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
	0, 0, 41, 42, 45, 44, 46, 47, 
	48, 44, 48, 48, 48, 0, 41, 49, 
	42, 50, 51, 49, 51, 51, 51, 0, 
	50, 50, 50, 51, 50, 51, 51, 51, 
	0, 53, 52, 54, 50, 51, 52, 51, 
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
	74, 69, 68, 68, 70, 71, 75, 68, 
	76, 68, 77, 68, 78, 78, 78, 68, 
	78, 78, 78, 79, 68, 80, 80, 80, 
	81, 68, 82, 82, 83, 82, 68, 83, 
	83, 83, 84, 68, 85, 85, 86, 85, 
	87, 68, 85, 85, 86, 85, 68, 88, 
	88, 88, 68, 89, 89, 90, 89, 68, 
	90, 90, 91, 92, 90, 93, 68, 93, 
	68, 94, 94, 95, 94, 96, 68, 94, 
	94, 95, 94, 68, 97, 97, 98, 99, 
	97, 100, 68, 100, 68, 101, 101, 102, 
	101, 103, 68, 101, 101, 102, 101, 68, 
	104, 104, 105, 106, 104, 107, 68, 107, 
	68, 108, 108, 109, 108, 110, 68, 108, 
	108, 109, 108, 68, 112, 111, 113, 111, 
	68, 112, 111, 113, 114, 111, 114, 114, 
	114, 68, 68, 112, 113, 116, 115, 117, 
	118, 119, 115, 119, 119, 119, 68, 112, 
	120, 113, 121, 122, 120, 122, 122, 122, 
	68, 121, 121, 121, 122, 121, 122, 122, 
	122, 68, 124, 123, 125, 121, 122, 123, 
	122, 122, 122, 68, 108, 108, 109, 108, 
	110, 68, 126, 68, 127, 127, 128, 127, 
	129, 68, 127, 127, 128, 127, 129, 68, 
	101, 101, 102, 101, 103, 68, 130, 68, 
	131, 131, 132, 131, 133, 68, 131, 131, 
	132, 131, 133, 68, 94, 94, 95, 94, 
	96, 68, 134, 68, 135, 135, 136, 135, 
	137, 68, 135, 135, 136, 135, 137, 68, 
	85, 85, 86, 85, 87, 68, 80, 80, 
	80, 81, 68, 138, 68, 139, 68, 140, 
	68, 142, 141, 141, 141, 141, 68, 143, 
	143, 143, 68, 143, 143, 143, 144, 68, 
	146, 145, 147, 145, 148, 68, 150, 149, 
	151, 149, 144, 68, 68, 150, 151, 146, 
	145, 147, 145, 148, 68, 152, 68, 153, 
	68, 154, 68, 155, 68, 156, 68, 157, 
	68, 158, 68, 159, 68, 160, 68, 161, 
	161, 161, 68, 161, 161, 161, 162, 68, 
	163, 163, 163, 164, 68, 163, 163, 163, 
	165, 68, 167, 166, 168, 166, 169, 68, 
	167, 166, 168, 166, 68, 68, 167, 168, 
	167, 166, 168, 166, 169, 68, 163, 163, 
	163, 164, 68, 170, 68, 171, 68, 172, 
	68, 173, 173, 173, 68, 173, 173, 174, 
	173, 68, 175, 68, 176, 68, 177, 68, 
	178, 178, 178, 68, 178, 178, 179, 178, 
	179, 179, 179, 68, 180, 180, 181, 183, 
	182, 180, 182, 182, 182, 68, 184, 184, 
	185, 187, 186, 184, 186, 186, 186, 68, 
	185, 185, 185, 186, 185, 186, 186, 186, 
	68, 188, 188, 185, 189, 186, 188, 186, 
	186, 186, 68, 187, 187, 190, 187, 190, 
	190, 190, 68, 192, 191, 193, 194, 195, 
	191, 195, 195, 195, 68, 197, 196, 198, 
	199, 200, 196, 200, 200, 200, 68, 68, 
	197, 198, 199, 199, 199, 200, 199, 200, 
	200, 200, 68, 202, 201, 203, 199, 200, 
	201, 200, 200, 200, 68, 2, 1, 3, 
	1, 0, 67, 70, 69, 71, 72, 73, 
	74, 69, 68, 0
};

static const unsigned char _multiple_atom_stmt_test_trans_targs_wi[] = {
	0, 1, 1, 2, 3, 4, 5, 6, 
	7, 8, 46, 8, 9, 10, 11, 12, 
	45, 13, 13, 14, 15, 42, 16, 17, 
	18, 41, 18, 19, 38, 20, 21, 22, 
	37, 22, 23, 34, 24, 25, 26, 33, 
	27, 142, 28, 29, 30, 142, 28, 31, 
	32, 30, 31, 32, 30, 142, 28, 35, 
	25, 26, 36, 39, 21, 22, 40, 43, 
	17, 18, 44, 143, 0, 47, 47, 48, 
	49, 94, 122, 50, 51, 52, 53, 54, 
	55, 93, 55, 56, 57, 58, 59, 92, 
	60, 60, 61, 62, 89, 63, 64, 65, 
	88, 65, 66, 85, 67, 68, 69, 84, 
	69, 70, 81, 71, 72, 73, 80, 74, 
	143, 75, 76, 77, 143, 75, 78, 79, 
	77, 78, 79, 77, 143, 75, 82, 72, 
	73, 83, 86, 68, 69, 87, 90, 64, 
	65, 91, 95, 96, 97, 98, 104, 99, 
	100, 101, 143, 102, 103, 101, 143, 102, 
	105, 106, 107, 108, 109, 110, 111, 112, 
	113, 114, 115, 116, 121, 117, 118, 143, 
	119, 120, 123, 124, 125, 126, 127, 128, 
	129, 130, 131, 132, 133, 134, 135, 136, 
	133, 134, 135, 136, 133, 136, 137, 138, 
	143, 139, 140, 141, 138, 143, 139, 140, 
	141, 138, 143, 139
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
	0, 0, 0, 0, 0, 0, 0, 0, 
	21, 5, 0, 0, 0, 0, 0, 5, 
	23, 0, 0, 0, 0, 0, 0, 25, 
	5, 0, 0, 0, 0, 0, 27, 5, 
	0, 0, 0, 0, 0, 29, 5, 0, 
	71, 0, 0, 83, 121, 83, 13, 55, 
	0, 0, 15, 64, 108, 64, 0, 11, 
	52, 5, 0, 11, 49, 5, 0, 11, 
	46, 5, 0, 0, 0, 33, 0, 0, 
	0, 31, 87, 31, 5, 0, 43, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 5, 0, 0, 75, 
	0, 9, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 58, 13, 55, 58, 
	0, 0, 15, 0, 17, 17, 0, 61, 
	96, 61, 13, 55, 0, 79, 0, 0, 
	15, 19, 91, 19
};

static const char _multiple_atom_stmt_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 3, 
	0, 0, 3, 0, 0, 0, 0, 0, 
	3, 0, 0, 0, 3, 0, 0, 0, 
	3, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 0, 3, 
	0, 0, 0, 3, 0, 0, 0, 0, 
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
	0, 0, 0, 0, 0, 0, 37, 37
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
	0, 0, 0, 0, 0, 0, 0, 39
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
	0, 0, 0, 0, 0, 0, 0, 0
};

static const int multiple_atom_stmt_test_start = 142;
static const int multiple_atom_stmt_test_first_final = 142;
static const int multiple_atom_stmt_test_error = 0;

static const int multiple_atom_stmt_test_en_atom_stmt = 143;
static const int multiple_atom_stmt_test_en_main = 142;

#line 527 "NanorexMMPImportExportTest.rl"
	
#line 2447 "NanorexMMPImportExportTest.cpp"
	{
	cs = multiple_atom_stmt_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 528 "NanorexMMPImportExportTest.rl"
	
#line 2457 "NanorexMMPImportExportTest.cpp"
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
#line 2478 "NanorexMMPImportExportTest.cpp"
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
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 4:
#line 44 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 5:
#line 47 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 7:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 8:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 9:
#line 92 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 10:
#line 26 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 11:
#line 31 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 12:
#line 34 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 13:
#line 35 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 14:
#line 36 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 15:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 16:
#line 52 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(atomStyle); 
		newAtom(atomId, atomicNum, x, y, z, atomStyle);
		// cerr << "p = " << p << endl;
	}
	break;
	case 17:
#line 69 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 18:
#line 75 "NanorexMMPImportExportTest.rl"
	{ stringVal = (*p); }
	break;
	case 19:
#line 80 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 20:
#line 89 "NanorexMMPImportExportTest.rl"
	{
		// stripTrailingWhiteSpaces(stringVal);
		// stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 21:
#line 501 "NanorexMMPImportExportTest.rl"
	{ //newAtom(atomId, atomicNum, x, y, z, atomStyle);
			// cerr << "calling, p = " << p << endl;
			{stack[top++] = cs; cs = 143; goto _again;}}
	break;
	case 22:
#line 504 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
	
}
	break;
	case 25:
#line 482 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "atom_decl_line, p = " << p << endl;
		// newAtom(atomId, atomicNum, x, y, z, atomStyle);
			}}
	break;
	case 26:
#line 486 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "bond_line, p = " << p << endl;
		// newBond(stringVal, intVal);
			}}
	break;
	case 27:
#line 490 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "bond_direction_line, p = " << p << endl;
		// newBondDirection(intVal, intVal2);
			}}
	break;
	case 28:
#line 494 "NanorexMMPImportExportTest.rl"
	{te = p+1;{ // cerr << "info_atom_line, p = " << p << endl;
		// newAtomInfo(stringVal, stringVal2);
			}}
	break;
	case 29:
#line 497 "NanorexMMPImportExportTest.rl"
	{te = p+1;{{cs = stack[--top]; goto _again;}}}
	break;
#line 2679 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _multiple_atom_stmt_test_actions + _multiple_atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 1:
#line 38 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 43 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 23:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
#line 2700 "NanorexMMPImportExportTest.cpp"
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
#line 504 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
	
}
	break;
#line 2723 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 529 "NanorexMMPImportExportTest.rl"
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


#line 575 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::molLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 586 "NanorexMMPImportExportTest.rl"
	
#line 2780 "NanorexMMPImportExportTest.cpp"
static const char _mol_decl_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 7, 2, 
	0, 6, 2, 1, 2, 2, 1, 3, 
	2, 1, 4, 3, 4, 0, 6, 4, 
	1, 4, 0, 6
};

static const unsigned char _mol_decl_line_test_key_offsets[] = {
	0, 0, 5, 6, 7, 11, 16, 27, 
	40, 53, 58, 70, 72, 85, 98, 110, 
	123, 135, 148
};

static const char _mol_decl_line_test_trans_keys[] = {
	10, 32, 109, 9, 13, 111, 108, 9, 
	32, 11, 13, 9, 32, 40, 11, 13, 
	9, 32, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 9, 32, 41, 45, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	9, 32, 41, 45, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	9, 13, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 9, 32, 45, 95, 11, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 9, 32, 45, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 9, 
	32, 41, 45, 95, 11, 13, 48, 57, 
	65, 90, 97, 122, 0
};

static const char _mol_decl_line_test_single_lengths[] = {
	0, 3, 1, 1, 2, 3, 3, 5, 
	5, 3, 4, 2, 5, 5, 4, 5, 
	4, 5, 0
};

static const char _mol_decl_line_test_range_lengths[] = {
	0, 1, 0, 0, 1, 1, 4, 4, 
	4, 1, 4, 0, 4, 4, 4, 4, 
	4, 4, 0
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
	8, 0, 9, 9, 10, 11, 12, 9, 
	12, 12, 12, 0, 13, 13, 14, 15, 
	16, 13, 16, 16, 16, 0, 18, 17, 
	19, 17, 0, 18, 17, 19, 20, 17, 
	20, 20, 20, 0, 0, 18, 19, 22, 
	21, 23, 24, 25, 21, 25, 25, 25, 
	0, 18, 26, 19, 27, 28, 26, 28, 
	28, 28, 0, 27, 27, 27, 28, 27, 
	28, 28, 28, 0, 30, 29, 31, 27, 
	28, 29, 28, 28, 28, 0, 15, 15, 
	15, 16, 15, 16, 16, 16, 0, 32, 
	32, 33, 15, 16, 32, 16, 16, 16, 
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
	13, 0, 1, 0, 0, 0, 0, 0, 
	0, 21, 21, 3, 18, 0, 0, 0, 
	5, 0, 15, 0, 0, 24, 31, 24, 
	3, 18, 0, 0, 5, 9, 27, 9, 
	7, 7
};

static const char _mol_decl_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 11, 0, 0, 11, 0, 0, 11, 
	0, 0, 0
};

static const char _mol_decl_line_test_eof_actions[] = {
	0, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 13, 13, 13, 13, 13, 13, 
	13, 13, 0
};

static const int mol_decl_line_test_start = 1;
static const int mol_decl_line_test_first_final = 18;
static const int mol_decl_line_test_error = 0;

static const int mol_decl_line_test_en_main = 1;

#line 587 "NanorexMMPImportExportTest.rl"
	
#line 2890 "NanorexMMPImportExportTest.cpp"
	{
	cs = mol_decl_line_test_start;
	}
#line 588 "NanorexMMPImportExportTest.rl"
	
#line 2896 "NanorexMMPImportExportTest.cpp"
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
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 92 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 6:
#line 14 "NanorexMMPImportExportTest.rl"
	{
			if(stringVal2 == "")
				stringVal2 = "def";
			newMolecule(stringVal, stringVal2);
		}
	break;
	case 7:
#line 571 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3009 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _mol_decl_line_test_actions + _mol_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 5:
#line 13 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); /* in case there is no 'style' string'*/ }
	break;
#line 3022 "NanorexMMPImportExportTest.cpp"
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
	case 7:
#line 571 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "multiple_atom_stmt_test state machine");
		}
	break;
#line 3044 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 589 "NanorexMMPImportExportTest.rl"
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


#line 706 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::groupLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	char const *ts, *te;
	int cs, stack[128], top, act;
	
	#line 719 "NanorexMMPImportExportTest.rl"
	
#line 3151 "NanorexMMPImportExportTest.cpp"
static const char _group_lines_test_actions[] = {
	0, 1, 1, 1, 2, 1, 3, 1, 
	4, 1, 7, 1, 9, 1, 11, 1, 
	12, 1, 14, 1, 22, 1, 23, 2, 
	0, 21, 2, 1, 2, 2, 1, 3, 
	2, 1, 4, 2, 12, 13, 3, 0, 
	5, 18, 3, 0, 6, 19, 3, 0, 
	8, 20, 3, 0, 10, 17, 3, 15, 
	0, 16, 4, 4, 0, 8, 20, 4, 
	9, 0, 10, 17, 5, 1, 4, 0, 
	8, 20
};

static const short _group_lines_test_key_offsets[] = {
	0, 0, 2, 9, 12, 15, 18, 21, 
	24, 31, 38, 40, 53, 65, 79, 93, 
	99, 112, 126, 129, 132, 135, 138, 144, 
	150, 164, 178, 192, 198, 211, 213, 227, 
	241, 254, 268, 281, 295, 310, 325, 340, 
	355, 370, 385, 400, 415, 429, 443, 449, 
	462, 464, 479, 494, 509, 523, 538, 553, 
	568, 583, 597, 611, 617, 630, 632, 632, 
	632, 639
};

static const char _group_lines_test_trans_keys[] = {
	-1, 10, -1, 10, 32, 101, 103, 9, 
	13, -1, 10, 103, -1, 10, 114, -1, 
	10, 111, -1, 10, 117, -1, 10, 112, 
	-1, 10, 32, 35, 40, 9, 13, -1, 
	10, 32, 35, 40, 9, 13, -1, 10, 
	-1, 10, 32, 41, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	35, 9, 13, -1, 10, 32, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	114, -1, 10, 111, -1, 10, 117, -1, 
	10, 112, -1, 10, 32, 40, 9, 13, 
	-1, 10, 32, 40, 9, 13, -1, 10, 
	32, 67, 86, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 35, 9, 13, -1, 10, 
	32, 35, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, -1, 10, 32, 
	35, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, -1, 10, 32, 41, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 45, 95, 108, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 45, 95, 105, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 45, 95, 112, 9, 13, 48, 57, 
	65, 90, 97, 122, -1, 10, 32, 41, 
	45, 95, 98, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 45, 
	95, 111, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 45, 95, 
	97, 9, 13, 48, 57, 65, 90, 98, 
	122, -1, 10, 32, 41, 45, 95, 114, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 45, 95, 100, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 41, 45, 95, 105, 9, 
	13, 48, 57, 65, 90, 97, 122, -1, 
	10, 32, 41, 45, 95, 101, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 41, 45, 95, 119, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 41, 45, 
	68, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, -1, 10, 32, 41, 45, 95, 
	97, 9, 13, 48, 57, 65, 90, 98, 
	122, -1, 10, 32, 41, 45, 95, 116, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 32, 41, 45, 95, 97, 9, 
	13, 48, 57, 65, 90, 98, 122, -1, 
	10, 32, 41, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, -1, 10, 32, 
	41, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, -1, 10, 32, 35, 9, 
	13, -1, 10, 32, 35, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	-1, 10, 32, 101, 103, 9, 13, -1, 
	10, 32, 101, 103, 9, 13, 0
};

static const char _group_lines_test_single_lengths[] = {
	0, 2, 5, 3, 3, 3, 3, 3, 
	5, 5, 2, 5, 4, 6, 6, 4, 
	5, 6, 3, 3, 3, 3, 4, 4, 
	6, 6, 6, 4, 5, 2, 6, 6, 
	5, 6, 5, 6, 7, 7, 7, 7, 
	7, 7, 7, 7, 6, 6, 4, 5, 
	2, 7, 7, 7, 6, 7, 7, 7, 
	7, 6, 6, 4, 5, 2, 0, 0, 
	5, 5
};

static const char _group_lines_test_range_lengths[] = {
	0, 0, 1, 0, 0, 0, 0, 0, 
	1, 1, 0, 4, 4, 4, 4, 1, 
	4, 4, 0, 0, 0, 0, 1, 1, 
	4, 4, 4, 1, 4, 0, 4, 4, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 4, 4, 4, 4, 1, 4, 
	0, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 4, 1, 4, 0, 0, 0, 
	1, 1
};

static const short _group_lines_test_index_offsets[] = {
	0, 0, 3, 10, 14, 18, 22, 26, 
	30, 37, 44, 47, 57, 66, 77, 88, 
	94, 104, 115, 119, 123, 127, 131, 137, 
	143, 154, 165, 176, 182, 192, 195, 206, 
	217, 227, 238, 248, 259, 271, 283, 295, 
	307, 319, 331, 343, 355, 366, 377, 383, 
	393, 396, 408, 420, 432, 443, 455, 467, 
	479, 491, 502, 513, 519, 529, 532, 533, 
	534, 541
};

static const char _group_lines_test_indicies[] = {
	0, 2, 1, 0, 4, 3, 5, 6, 
	3, 1, 0, 2, 7, 1, 0, 2, 
	8, 1, 0, 2, 9, 1, 0, 2, 
	10, 1, 0, 2, 11, 1, 0, 13, 
	12, 14, 15, 12, 1, 0, 17, 16, 
	18, 19, 16, 1, 0, 17, 18, 0, 
	2, 20, 21, 22, 20, 22, 22, 22, 
	1, 0, 2, 20, 22, 20, 22, 22, 
	22, 1, 0, 2, 23, 24, 25, 26, 
	23, 26, 26, 26, 1, 0, 2, 27, 
	21, 28, 29, 27, 29, 29, 29, 1, 
	0, 17, 21, 18, 21, 1, 0, 2, 
	28, 28, 29, 28, 29, 29, 29, 1, 
	0, 2, 30, 31, 28, 29, 30, 29, 
	29, 29, 1, 0, 2, 32, 1, 0, 
	2, 33, 1, 0, 2, 34, 1, 0, 
	2, 35, 1, 0, 2, 36, 37, 36, 
	1, 0, 2, 38, 39, 38, 1, 0, 
	2, 39, 41, 42, 40, 39, 40, 40, 
	40, 1, 0, 2, 43, 44, 45, 46, 
	43, 46, 46, 46, 1, 0, 2, 47, 
	48, 49, 50, 47, 50, 50, 50, 1, 
	0, 52, 51, 53, 51, 1, 0, 52, 
	51, 53, 54, 51, 54, 54, 54, 1, 
	0, 52, 53, 0, 56, 55, 57, 58, 
	59, 55, 59, 59, 59, 1, 0, 52, 
	60, 53, 61, 62, 60, 62, 62, 62, 
	1, 0, 2, 61, 61, 62, 61, 62, 
	62, 62, 1, 0, 64, 63, 65, 61, 
	62, 63, 62, 62, 62, 1, 0, 2, 
	49, 49, 50, 49, 50, 50, 50, 1, 
	0, 2, 66, 67, 49, 50, 66, 50, 
	50, 50, 1, 0, 2, 43, 44, 45, 
	46, 68, 43, 46, 46, 46, 1, 0, 
	2, 66, 67, 49, 50, 69, 66, 50, 
	50, 50, 1, 0, 2, 66, 67, 49, 
	50, 70, 66, 50, 50, 50, 1, 0, 
	2, 66, 67, 49, 50, 71, 66, 50, 
	50, 50, 1, 0, 2, 66, 67, 49, 
	50, 72, 66, 50, 50, 50, 1, 0, 
	2, 66, 67, 49, 50, 73, 66, 50, 
	50, 50, 1, 0, 2, 66, 67, 49, 
	50, 74, 66, 50, 50, 50, 1, 0, 
	2, 66, 67, 49, 50, 75, 66, 50, 
	50, 50, 1, 0, 2, 76, 77, 49, 
	50, 76, 50, 50, 50, 1, 0, 2, 
	78, 79, 49, 50, 78, 50, 50, 50, 
	1, 0, 81, 80, 82, 80, 1, 0, 
	81, 80, 82, 54, 80, 54, 54, 54, 
	1, 0, 81, 82, 0, 2, 43, 44, 
	45, 46, 83, 43, 46, 46, 46, 1, 
	0, 2, 66, 67, 49, 50, 84, 66, 
	50, 50, 50, 1, 0, 2, 66, 67, 
	49, 50, 85, 66, 50, 50, 50, 1, 
	0, 2, 86, 67, 49, 50, 86, 50, 
	50, 50, 1, 0, 2, 87, 48, 49, 
	88, 50, 87, 50, 50, 50, 1, 0, 
	2, 66, 67, 49, 50, 89, 66, 50, 
	50, 50, 1, 0, 2, 66, 67, 49, 
	50, 90, 66, 50, 50, 50, 1, 0, 
	2, 66, 67, 49, 50, 91, 66, 50, 
	50, 50, 1, 0, 2, 92, 93, 49, 
	50, 92, 50, 50, 50, 1, 0, 2, 
	94, 95, 49, 50, 94, 50, 50, 50, 
	1, 0, 97, 96, 98, 96, 1, 0, 
	97, 96, 98, 54, 96, 54, 54, 54, 
	1, 0, 97, 98, 99, 100, 101, 4, 
	3, 5, 6, 3, 1, 102, 4, 3, 
	5, 6, 3, 1, 0
};

static const char _group_lines_test_trans_targs_wi[] = {
	64, 1, 64, 2, 65, 3, 18, 4, 
	5, 6, 7, 8, 9, 64, 10, 11, 
	9, 64, 10, 11, 12, 15, 13, 14, 
	15, 16, 17, 14, 16, 17, 14, 15, 
	19, 20, 21, 22, 23, 24, 23, 24, 
	25, 36, 49, 26, 27, 34, 35, 26, 
	27, 34, 35, 28, 64, 29, 30, 31, 
	64, 29, 32, 33, 31, 32, 33, 31, 
	64, 29, 26, 27, 37, 38, 39, 40, 
	41, 42, 43, 44, 45, 46, 45, 46, 
	47, 64, 48, 50, 51, 52, 53, 53, 
	54, 55, 56, 57, 58, 59, 58, 59, 
	60, 64, 61, 63, 63, 0, 64
};

static const char _group_lines_test_trans_actions_wi[] = {
	21, 0, 23, 0, 54, 0, 0, 0, 
	0, 0, 0, 0, 11, 63, 11, 11, 
	0, 50, 0, 0, 0, 0, 0, 29, 
	29, 1, 26, 0, 0, 3, 5, 5, 
	0, 0, 0, 0, 9, 9, 0, 0, 
	0, 0, 0, 29, 29, 1, 26, 0, 
	0, 0, 3, 0, 46, 0, 0, 32, 
	68, 32, 1, 26, 0, 0, 3, 7, 
	58, 7, 5, 5, 26, 3, 3, 3, 
	3, 3, 3, 3, 5, 5, 0, 0, 
	0, 42, 0, 26, 3, 3, 5, 0, 
	3, 3, 3, 3, 5, 5, 0, 0, 
	0, 38, 0, 13, 0, 0, 19
};

static const char _group_lines_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 15, 15, 
	35, 0
};

static const char _group_lines_test_from_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	17, 0
};

static const char _group_lines_test_eof_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 13, 0, 
	0, 0
};

static const char _group_lines_test_eof_trans[] = {
	0, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 0, 0, 
	0, 103
};

static const int group_lines_test_start = 62;
static const int group_lines_test_first_final = 62;
static const int group_lines_test_error = 0;

static const int group_lines_test_en_group_scanner = 64;
static const int group_lines_test_en_main = 62;

#line 720 "NanorexMMPImportExportTest.rl"
	
#line 3458 "NanorexMMPImportExportTest.cpp"
	{
	cs = group_lines_test_start;
	top = 0;
	ts = 0;
	te = 0;
	act = 0;
	}
#line 721 "NanorexMMPImportExportTest.rl"
	
#line 3468 "NanorexMMPImportExportTest.cpp"
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
	case 14:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = p;}
	break;
#line 3489 "NanorexMMPImportExportTest.cpp"
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
#line 24 "NanorexMMPImportExportTest.rl"
	{++lineNum;}
	break;
	case 1:
#line 71 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStart = p-1; }
	break;
	case 2:
#line 72 "NanorexMMPImportExportTest.rl"
	{ charStringWithSpaceStop = p; }
	break;
	case 3:
#line 81 "NanorexMMPImportExportTest.rl"
	{ stringVal.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal.begin());
		}
	break;
	case 4:
#line 92 "NanorexMMPImportExportTest.rl"
	{ stringVal2.resize(charStringWithSpaceStop - charStringWithSpaceStart + 1);
			std::copy(charStringWithSpaceStart, charStringWithSpaceStop+1, stringVal2.begin());
		}
	break;
	case 5:
#line 14 "NanorexMMPImportExportTest.rl"
	{ newViewDataGroup(); }
	break;
	case 6:
#line 39 "NanorexMMPImportExportTest.rl"
	{ newClipboardGroup(); }
	break;
	case 7:
#line 66 "NanorexMMPImportExportTest.rl"
	{ stringVal2.clear(); }
	break;
	case 8:
#line 71 "NanorexMMPImportExportTest.rl"
	{ newMolStructGroup(stringVal, stringVal2); }
	break;
	case 9:
#line 102 "NanorexMMPImportExportTest.rl"
	{ stringVal.clear(); }
	break;
	case 10:
#line 107 "NanorexMMPImportExportTest.rl"
	{ endGroup(stringVal); }
	break;
	case 11:
#line 694 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 64; goto _again;} }
	break;
	case 15:
#line 1 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 16:
#line 691 "NanorexMMPImportExportTest.rl"
	{act = 5;}
	break;
	case 17:
#line 682 "NanorexMMPImportExportTest.rl"
	{te = p+1;}
	break;
	case 18:
#line 683 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "view_data begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 19:
#line 684 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "clipboard begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 20:
#line 685 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "mol_struct begin, p = '" << p << "' [" << strlen(p) << ']' << endl;*/}}
	break;
	case 21:
#line 691 "NanorexMMPImportExportTest.rl"
	{te = p+1;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 22:
#line 691 "NanorexMMPImportExportTest.rl"
	{te = p;p--;{/*cerr << "Ignored line, p = " << p << endl;*/}}
	break;
	case 23:
#line 1 "NanorexMMPImportExportTest.rl"
	{	switch( act ) {
	case 0:
	{{cs = 0; goto _again;}}
	break;
	case 5:
	{{p = ((te))-1;}/*cerr << "Ignored line, p = " << p << endl;*/}
	break;
	default: break;
	}
	}
	break;
#line 3652 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _group_lines_test_actions + _group_lines_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 12:
#line 1 "NanorexMMPImportExportTest.rl"
	{ts = 0;}
	break;
	case 13:
#line 1 "NanorexMMPImportExportTest.rl"
	{act = 0;}
	break;
#line 3669 "NanorexMMPImportExportTest.cpp"
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
	case 11:
#line 694 "NanorexMMPImportExportTest.rl"
	{ /*cerr << "scanner call: p = " << p << endl;*/ p--; {stack[top++] = cs; cs = 64; goto _again;} }
	break;
#line 3692 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 722 "NanorexMMPImportExportTest.rl"
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
