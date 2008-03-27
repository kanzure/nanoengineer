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


#line 85 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomLineTestHelper(char const *const testInput)
{
	char const *p = testInput;
	char const *pe = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	// cerr << "atomLineTestHelper (debug): *(pe-1) = (int) " << (int) *(pe-1) << endl;
	
	#line 98 "NanorexMMPImportExportTest.rl"
	
#line 90 "NanorexMMPImportExportTest.cpp"
static const char _atom_decl_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 6, 1, 7, 1, 
	8, 1, 9, 1, 10, 1, 12, 1, 
	13, 2, 2, 8, 2, 2, 9, 2, 
	2, 10, 2, 5, 11, 3, 4, 5, 
	11, 3, 5, 11, 12
};

static const unsigned char _atom_decl_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 10, 15, 
	20, 24, 29, 35, 39, 42, 46, 53, 
	55, 61, 65, 72, 74, 80, 84, 91, 
	93, 99, 103, 108, 120, 122, 135, 148, 
	153, 165, 171, 173, 179, 185, 191, 193, 
	199, 205, 211, 213, 219, 225, 231, 236, 
	248, 248
};

static const char _atom_decl_line_test_trans_keys[] = {
	32, 97, 9, 13, 116, 111, 109, 32, 
	9, 13, 32, 9, 13, 48, 57, 32, 
	9, 13, 48, 57, 32, 40, 9, 13, 
	32, 9, 13, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 41, 9, 13, 32, 
	9, 13, 32, 40, 9, 13, 32, 43, 
	45, 9, 13, 48, 57, 48, 57, 32, 
	44, 9, 13, 48, 57, 32, 44, 9, 
	13, 32, 43, 45, 9, 13, 48, 57, 
	48, 57, 32, 44, 9, 13, 48, 57, 
	32, 44, 9, 13, 32, 43, 45, 9, 
	13, 48, 57, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 41, 9, 13, 10, 
	32, 35, 9, 13, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	-1, 10, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 9, 
	13, 9, 32, 45, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 32, 41, 9, 
	13, 48, 57, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 41, 9, 13, 48, 
	57, 32, 44, 9, 13, 48, 57, 48, 
	57, 32, 44, 9, 13, 48, 57, 32, 
	44, 9, 13, 48, 57, 32, 44, 9, 
	13, 48, 57, 48, 57, 32, 44, 9, 
	13, 48, 57, 32, 44, 9, 13, 48, 
	57, 32, 41, 9, 13, 48, 57, 32, 
	9, 13, 48, 57, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 9, 13, 0
};

static const char _atom_decl_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 1, 1, 
	2, 1, 2, 2, 1, 2, 3, 0, 
	2, 2, 3, 0, 2, 2, 3, 0, 
	2, 2, 3, 4, 2, 5, 5, 3, 
	4, 2, 0, 2, 2, 2, 0, 2, 
	2, 2, 0, 2, 2, 2, 1, 4, 
	0, 3
};

static const char _atom_decl_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 0, 4, 4, 1, 
	4, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 2, 4, 
	0, 1
};

static const unsigned char _atom_decl_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 13, 17, 
	21, 25, 29, 34, 38, 41, 45, 51, 
	53, 58, 62, 68, 70, 75, 79, 85, 
	87, 92, 96, 101, 110, 113, 123, 133, 
	138, 147, 152, 154, 159, 164, 169, 171, 
	176, 181, 186, 188, 193, 198, 203, 207, 
	216, 217
};

static const char _atom_decl_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 0, 6, 6, 7, 
	0, 8, 8, 9, 0, 10, 11, 10, 
	0, 11, 11, 12, 0, 13, 14, 13, 
	15, 0, 13, 14, 13, 0, 16, 16, 
	0, 17, 18, 17, 0, 18, 19, 20, 
	18, 21, 0, 21, 0, 22, 23, 22, 
	24, 0, 22, 23, 22, 0, 25, 26, 
	27, 25, 28, 0, 28, 0, 29, 30, 
	29, 31, 0, 29, 30, 29, 0, 32, 
	33, 34, 32, 35, 0, 35, 0, 36, 
	37, 36, 38, 0, 36, 37, 36, 0, 
	40, 39, 41, 39, 0, 40, 39, 41, 
	42, 39, 42, 42, 42, 0, 0, 43, 
	41, 45, 44, 46, 47, 42, 44, 42, 
	42, 42, 0, 49, 48, 41, 47, 42, 
	48, 42, 42, 42, 0, 49, 50, 41, 
	50, 0, 47, 47, 47, 42, 47, 42, 
	42, 42, 0, 36, 37, 36, 38, 0, 
	51, 0, 52, 53, 52, 54, 0, 52, 
	53, 52, 54, 0, 29, 30, 29, 31, 
	0, 55, 0, 56, 57, 56, 58, 0, 
	56, 57, 56, 58, 0, 22, 23, 22, 
	24, 0, 59, 0, 60, 61, 60, 62, 
	0, 60, 61, 60, 62, 0, 13, 14, 
	13, 15, 0, 8, 8, 9, 0, 40, 
	39, 41, 42, 39, 42, 42, 42, 0, 
	0, 49, 50, 41, 50, 0, 0
};

static const char _atom_decl_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 46, 8, 9, 10, 11, 12, 45, 
	13, 13, 14, 15, 42, 16, 17, 18, 
	41, 18, 19, 38, 20, 21, 22, 37, 
	22, 23, 34, 24, 25, 26, 33, 27, 
	47, 28, 29, 48, 30, 49, 28, 32, 
	30, 49, 31, 35, 25, 26, 36, 39, 
	21, 22, 40, 43, 17, 18, 44
};

static const char _atom_decl_line_test_trans_actions_wi[] = {
	23, 0, 0, 0, 0, 0, 0, 0, 
	11, 3, 0, 0, 0, 0, 0, 3, 
	13, 0, 0, 0, 0, 0, 0, 15, 
	3, 0, 0, 0, 0, 0, 17, 3, 
	0, 0, 0, 0, 0, 19, 3, 0, 
	21, 0, 9, 21, 37, 41, 34, 9, 
	9, 21, 0, 0, 5, 31, 3, 0, 
	5, 28, 3, 0, 5, 25, 3
};

static const char _atom_decl_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 1, 
	0, 0, 1, 0, 0, 0, 0, 0, 
	1, 0, 0, 0, 1, 0, 0, 0, 
	1, 0, 0, 7, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 0, 0, 1, 
	0, 0, 0, 1, 0, 0, 0, 7, 
	0, 0
};

static const char _atom_decl_line_test_eof_actions[] = {
	0, 23, 23, 23, 23, 23, 23, 23, 
	23, 23, 23, 23, 23, 23, 23, 23, 
	23, 23, 23, 23, 23, 23, 23, 23, 
	23, 23, 23, 23, 23, 23, 23, 23, 
	23, 23, 23, 23, 23, 23, 23, 23, 
	23, 23, 23, 23, 23, 23, 23, 0, 
	0, 0
};

static const int atom_decl_line_test_start = 1;
static const int atom_decl_line_test_first_final = 47;
static const int atom_decl_line_test_error = 0;

static const int atom_decl_line_test_en_main = 1;

#line 99 "NanorexMMPImportExportTest.rl"
	
#line 256 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_decl_line_test_start;
	}
#line 100 "NanorexMMPImportExportTest.rl"
	
#line 262 "NanorexMMPImportExportTest.cpp"
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
	case 1:
#line 35 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 2:
#line 43 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 4:
#line 70 "NanorexMMPImportExportTest.rl"
	{stringVal = stringVal + (*p); }
	break;
	case 5:
#line 71 "NanorexMMPImportExportTest.rl"
	{ /*stripTrailingWhiteSpaces(stringVal);*/ }
	break;
	case 6:
#line 26 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 7:
#line 31 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 8:
#line 34 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 9:
#line 35 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 10:
#line 36 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 11:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 12:
#line 52 "NanorexMMPImportExportTest.rl"
	{
		stripTrailingWhiteSpaces(atomStyle); 
		newAtom(atomId, atomicNum, x, y, z, atomStyle);
	}
	break;
	case 13:
#line 80 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 392 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_decl_line_test_actions + _atom_decl_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 0:
#line 34 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 3:
#line 69 "NanorexMMPImportExportTest.rl"
	{stringVal.clear();}
	break;
#line 409 "NanorexMMPImportExportTest.cpp"
		}
	}

	if ( cs == 0 )
		goto _out;
	if ( ++p != pe )
		goto _resume;
	_test_eof: {}
	if ( p == eof )
	{
	const char *__acts = _atom_decl_line_test_actions + _atom_decl_line_test_eof_actions[cs];
	unsigned int __nacts = (unsigned int) *__acts++;
	while ( __nacts-- > 0 ) {
		switch ( *__acts++ ) {
	case 13:
#line 80 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in atom_decl_line_test"
		                               " state machine");
		}
	break;
#line 431 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 101 "NanorexMMPImportExportTest.rl"
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


#line 154 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::bondLineTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;

	#line 165 "NanorexMMPImportExportTest.rl"
	
#line 493 "NanorexMMPImportExportTest.cpp"
static const char _bond_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5
};

static const char _bond_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 14, 25, 
	30, 37, 44, 46, 53, 64, 71
};

static const char _bond_line_test_trans_keys[] = {
	32, 98, 9, 13, 111, 110, 100, 95, 
	48, 57, 65, 90, 97, 122, 32, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 9, 13, 48, 57, 10, 32, 
	35, 9, 13, 48, 57, 10, 32, 35, 
	9, 13, 48, 57, -1, 10, 10, 32, 
	35, 9, 13, 48, 57, 32, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 9, 13, 48, 57, 0
};

static const char _bond_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 3, 1, 
	3, 3, 2, 3, 3, 3, 0
};

static const char _bond_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 3, 4, 2, 
	2, 2, 0, 2, 4, 2, 0
};

static const char _bond_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 15, 23, 
	27, 33, 39, 42, 48, 56, 62
};

static const char _bond_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 6, 6, 0, 7, 
	8, 8, 7, 8, 8, 8, 0, 7, 
	7, 9, 0, 11, 10, 12, 10, 13, 
	0, 15, 14, 16, 14, 9, 0, 0, 
	17, 16, 11, 10, 12, 10, 13, 0, 
	7, 8, 8, 7, 8, 8, 8, 0, 
	15, 14, 16, 14, 9, 0, 0, 0
};

static const char _bond_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	12, 8, 9, 13, 10, 11, 9, 13, 
	10, 14
};

static const char _bond_line_test_trans_actions_wi[] = {
	11, 0, 0, 0, 0, 0, 0, 0, 
	7, 0, 9, 9, 9, 3, 0, 0, 
	0, 0
};

static const char _bond_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 5, 0, 
	1, 0, 0, 0, 0, 0, 0
};

static const char _bond_line_test_eof_actions[] = {
	0, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 0, 0
};

static const int bond_line_test_start = 1;
static const int bond_line_test_first_final = 13;
static const int bond_line_test_error = 0;

static const int bond_line_test_en_main = 1;

#line 166 "NanorexMMPImportExportTest.rl"
	
#line 572 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_line_test_start;
	}
#line 167 "NanorexMMPImportExportTest.rl"
	
#line 578 "NanorexMMPImportExportTest.cpp"
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
	case 1:
#line 35 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 55 "NanorexMMPImportExportTest.rl"
	{stringVal = stringVal + (*p); }
	break;
	case 4:
#line 67 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 5:
#line 149 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in bond_line_test "
		                               "state machine");
		}
	break;
#line 673 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_line_test_actions + _bond_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 0:
#line 34 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 2:
#line 54 "NanorexMMPImportExportTest.rl"
	{/*stringVal.clear();*/ stringVal = (*p); }
	break;
#line 690 "NanorexMMPImportExportTest.cpp"
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
#line 712 "NanorexMMPImportExportTest.cpp"
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


#line 209 "NanorexMMPImportExportTest.rl"



void
NanorexMMPImportExportTest::bondDirectionTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 221 "NanorexMMPImportExportTest.rl"
	
#line 763 "NanorexMMPImportExportTest.cpp"
static const char _bond_direction_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5
};

static const char _bond_direction_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 8, 9, 
	10, 11, 12, 13, 14, 15, 16, 17, 
	20, 25, 30, 35, 42, 47, 49, 56, 
	61, 66
};

static const char _bond_direction_line_test_trans_keys[] = {
	32, 98, 9, 13, 111, 110, 100, 95, 
	100, 105, 114, 101, 99, 116, 105, 111, 
	110, 32, 9, 13, 32, 9, 13, 48, 
	57, 32, 9, 13, 48, 57, 32, 9, 
	13, 48, 57, 10, 32, 35, 9, 13, 
	48, 57, 10, 32, 35, 9, 13, -1, 
	10, 10, 32, 35, 9, 13, 48, 57, 
	32, 9, 13, 48, 57, 10, 32, 35, 
	9, 13, 0
};

static const char _bond_direction_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 1, 1, 1, 1, 1, 
	1, 1, 1, 3, 3, 2, 3, 1, 
	3, 0
};

static const char _bond_direction_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 1, 
	2, 2, 2, 2, 1, 0, 2, 2, 
	1, 0
};

static const char _bond_direction_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 12, 14, 
	16, 18, 20, 22, 24, 26, 28, 30, 
	33, 37, 41, 45, 51, 56, 59, 65, 
	69, 74
};

static const char _bond_direction_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 0, 7, 0, 8, 0, 
	9, 0, 10, 0, 11, 0, 12, 0, 
	13, 0, 14, 0, 15, 0, 16, 16, 
	0, 16, 16, 17, 0, 18, 18, 19, 
	0, 18, 18, 20, 0, 22, 21, 23, 
	21, 24, 0, 22, 21, 23, 21, 0, 
	0, 25, 23, 22, 21, 23, 21, 24, 
	0, 18, 18, 19, 0, 22, 21, 23, 
	21, 0, 0, 0
};

static const char _bond_direction_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 9, 10, 11, 12, 13, 14, 15, 
	16, 17, 18, 23, 19, 20, 24, 21, 
	22, 25
};

static const char _bond_direction_line_test_trans_actions_wi[] = {
	11, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 3, 0, 0, 9, 0, 
	7, 9
};

static const char _bond_direction_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 1, 0, 5, 0, 0, 0, 0, 
	0, 0
};

static const char _bond_direction_line_test_eof_actions[] = {
	0, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	11, 11, 11, 11, 11, 11, 11, 11, 
	0, 0
};

static const int bond_direction_line_test_start = 1;
static const int bond_direction_line_test_first_final = 24;
static const int bond_direction_line_test_error = 0;

static const int bond_direction_line_test_en_main = 1;

#line 222 "NanorexMMPImportExportTest.rl"
	
#line 858 "NanorexMMPImportExportTest.cpp"
	{
	cs = bond_direction_line_test_start;
	}
#line 223 "NanorexMMPImportExportTest.rl"
	
#line 864 "NanorexMMPImportExportTest.cpp"
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
	case 1:
#line 35 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 4:
#line 76 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 5:
#line 204 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 959 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _bond_direction_line_test_actions + _bond_direction_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 0:
#line 34 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 2:
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
#line 976 "NanorexMMPImportExportTest.cpp"
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
	case 5:
#line 204 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "bond_direction_line_test state machine");
		}
	break;
#line 998 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 224 "NanorexMMPImportExportTest.rl"
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


#line 278 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::infoAtomTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = NULL;
	int cs;
	
	#line 289 "NanorexMMPImportExportTest.rl"
	
#line 1061 "NanorexMMPImportExportTest.cpp"
static const char _info_atom_line_test_actions[] = {
	0, 1, 0, 1, 1, 1, 2, 1, 
	3, 1, 4, 1, 5, 1, 6, 1, 
	7, 2, 1, 2, 2, 4, 5, 2, 
	5, 6
};

static const unsigned char _info_atom_line_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 10, 14, 
	15, 16, 17, 20, 30, 42, 55, 59, 
	62, 72, 85, 98, 103, 105, 117, 129, 
	134
};

static const char _info_atom_line_test_trans_keys[] = {
	32, 105, 9, 13, 110, 102, 111, 32, 
	9, 13, 32, 97, 9, 13, 116, 111, 
	109, 32, 9, 13, 32, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 61, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 32, 
	61, 9, 13, 32, 9, 13, 32, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 9, 13, -1, 
	10, 9, 32, 45, 95, 11, 13, 48, 
	57, 65, 90, 97, 122, 9, 32, 45, 
	95, 11, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 9, 13, 0
};

static const char _info_atom_line_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 2, 1, 
	1, 1, 1, 2, 4, 5, 2, 1, 
	2, 5, 5, 3, 2, 4, 4, 3, 
	0
};

static const char _info_atom_line_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 1, 0, 
	0, 0, 1, 4, 4, 4, 1, 1, 
	4, 4, 4, 1, 0, 4, 4, 1, 
	0
};

static const char _info_atom_line_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 13, 17, 
	19, 21, 23, 26, 33, 42, 52, 56, 
	59, 66, 76, 86, 91, 94, 103, 112, 
	117
};

static const char _info_atom_line_test_indicies[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 0, 6, 7, 6, 
	0, 8, 0, 9, 0, 10, 0, 11, 
	11, 0, 11, 12, 11, 12, 12, 12, 
	0, 14, 13, 15, 12, 13, 12, 12, 
	12, 0, 17, 16, 15, 18, 12, 16, 
	12, 12, 12, 0, 17, 18, 17, 0, 
	19, 19, 0, 19, 20, 19, 20, 20, 
	20, 0, 22, 21, 23, 24, 20, 21, 
	20, 20, 20, 0, 26, 25, 27, 24, 
	20, 25, 20, 20, 20, 0, 26, 28, 
	27, 28, 0, 0, 29, 27, 24, 24, 
	24, 20, 24, 20, 20, 20, 0, 15, 
	15, 15, 12, 15, 12, 12, 12, 0, 
	26, 28, 27, 28, 0, 0, 0
};

static const char _info_atom_line_test_trans_targs_wi[] = {
	0, 1, 2, 3, 4, 5, 6, 7, 
	8, 9, 10, 11, 12, 13, 14, 22, 
	13, 14, 15, 16, 17, 18, 23, 20, 
	21, 18, 23, 20, 19, 24
};

static const char _info_atom_line_test_trans_actions_wi[] = {
	15, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 3, 17, 5, 3, 
	3, 0, 0, 0, 9, 20, 23, 11, 
	9, 9, 13, 0, 0, 13
};

static const char _info_atom_line_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 0, 0, 0, 
	7, 0, 0, 0, 0, 0, 0, 0, 
	0
};

static const char _info_atom_line_test_eof_actions[] = {
	0, 15, 15, 15, 15, 15, 15, 15, 
	15, 15, 15, 15, 15, 15, 15, 15, 
	15, 15, 15, 15, 15, 15, 15, 0, 
	0
};

static const int info_atom_line_test_start = 1;
static const int info_atom_line_test_first_final = 23;
static const int info_atom_line_test_error = 0;

static const int info_atom_line_test_en_main = 1;

#line 290 "NanorexMMPImportExportTest.rl"
	
#line 1171 "NanorexMMPImportExportTest.cpp"
	{
	cs = info_atom_line_test_start;
	}
#line 291 "NanorexMMPImportExportTest.rl"
	
#line 1177 "NanorexMMPImportExportTest.cpp"
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
	case 1:
#line 70 "NanorexMMPImportExportTest.rl"
	{stringVal = stringVal + (*p); }
	break;
	case 2:
#line 71 "NanorexMMPImportExportTest.rl"
	{ /*stripTrailingWhiteSpaces(stringVal);*/ }
	break;
	case 4:
#line 80 "NanorexMMPImportExportTest.rl"
	{stringVal2 = stringVal2 + (*p); }
	break;
	case 5:
#line 81 "NanorexMMPImportExportTest.rl"
	{ /*stripTrailingWhiteSpaces(stringVal2);*/ }
	break;
	case 6:
#line 85 "NanorexMMPImportExportTest.rl"
	{
		stripTrailingWhiteSpaces(stringVal);
		stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 7:
#line 273 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1282 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _info_atom_line_test_actions + _info_atom_line_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 0:
#line 69 "NanorexMMPImportExportTest.rl"
	{stringVal.clear();}
	break;
	case 3:
#line 79 "NanorexMMPImportExportTest.rl"
	{stringVal2.clear();}
	break;
#line 1299 "NanorexMMPImportExportTest.cpp"
		}
	}

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
	case 7:
#line 273 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "info_atom_line_test state machine");
		}
	break;
#line 1321 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 292 "NanorexMMPImportExportTest.rl"
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
	
	cerr << "Performing atom_stmt test" << endl;
	
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


#line 344 "NanorexMMPImportExportTest.rl"



void NanorexMMPImportExportTest::atomStmtTestHelper(char const *const testInput)
{
	char const *p   = testInput;
	char const *pe  = p + strlen(p);
	char const *eof = 0;
	int cs;
	
	#line 355 "NanorexMMPImportExportTest.rl"
	
#line 1382 "NanorexMMPImportExportTest.cpp"
static const char _atom_stmt_test_actions[] = {
	0, 1, 0, 1, 1, 1, 4, 1, 
	5, 1, 6, 1, 7, 1, 8, 1, 
	9, 1, 10, 1, 11, 1, 12, 1, 
	13, 1, 14, 1, 15, 1, 16, 1, 
	17, 1, 19, 1, 20, 1, 21, 1, 
	22, 1, 23, 2, 0, 2, 2, 1, 
	3, 2, 1, 8, 2, 4, 15, 2, 
	4, 16, 2, 4, 17, 2, 6, 8, 
	2, 8, 1, 2, 8, 6, 2, 8, 
	9, 2, 9, 18, 2, 11, 12, 2, 
	12, 22, 2, 19, 21, 2, 20, 9, 
	2, 20, 21, 3, 1, 3, 8, 3, 
	8, 1, 3, 3, 8, 9, 18, 3, 
	9, 18, 19, 3, 9, 18, 20, 3, 
	20, 8, 9, 3, 20, 21, 9, 4, 
	8, 9, 18, 20, 4, 9, 18, 19, 
	20, 5, 9, 18, 19, 20, 21
};

static const short _atom_stmt_test_key_offsets[] = {
	0, 0, 4, 5, 6, 7, 10, 15, 
	20, 24, 29, 35, 39, 42, 46, 53, 
	55, 61, 65, 72, 74, 80, 84, 91, 
	93, 99, 103, 108, 120, 134, 136, 141, 
	142, 143, 144, 151, 162, 167, 174, 181, 
	190, 192, 193, 194, 195, 198, 202, 203, 
	204, 205, 208, 218, 230, 243, 247, 250, 
	260, 273, 286, 293, 295, 307, 319, 326, 
	337, 349, 361, 373, 385, 397, 409, 421, 
	433, 445, 456, 461, 468, 475, 484, 491, 
	498, 507, 509, 516, 523, 536, 549, 556, 
	568, 582, 596, 610, 623, 636, 649, 658, 
	671, 684, 696, 708, 721, 735, 749, 763, 
	777, 791, 805, 819, 833, 847, 860, 873, 
	882, 895, 908, 917, 930, 943, 952, 954, 
	967, 980, 994, 1008, 1022, 1035, 1049, 1057, 
	1071, 1085, 1099, 1112, 1125, 1139, 1152, 1165, 
	1178, 1190, 1202, 1215, 1221, 1234, 1248, 1258, 
	1271, 1283, 1295, 1307, 1320, 1333, 1346, 1359, 
	1372, 1385, 1398, 1411, 1424, 1436, 1449, 1455, 
	1468, 1482, 1492, 1505, 1519, 1529, 1542, 1555, 
	1568, 1581, 1594, 1606, 1620, 1625, 1638, 1651, 
	1664, 1676, 1689, 1700, 1713, 1721, 1727, 1729, 
	1735, 1741, 1747, 1749, 1755, 1761, 1767, 1769, 
	1775, 1781, 1787, 1792, 1806, 1811, 1820, 1827, 
	1836, 1845, 1852, 1861, 1870, 1879, 1888, 1896, 
	1910, 1920, 1930, 1940
};

static const char _atom_stmt_test_trans_keys[] = {
	32, 97, 9, 13, 116, 111, 109, 32, 
	9, 13, 32, 9, 13, 48, 57, 32, 
	9, 13, 48, 57, 32, 40, 9, 13, 
	32, 9, 13, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 41, 9, 13, 32, 
	9, 13, 32, 40, 9, 13, 32, 43, 
	45, 9, 13, 48, 57, 48, 57, 32, 
	44, 9, 13, 48, 57, 32, 44, 9, 
	13, 32, 43, 45, 9, 13, 48, 57, 
	48, 57, 32, 44, 9, 13, 48, 57, 
	32, 44, 9, 13, 32, 43, 45, 9, 
	13, 48, 57, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 41, 9, 13, 10, 
	32, 35, 9, 13, 10, 32, 35, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 95, 98, 105, 9, 13, 
	48, 57, 65, 90, 97, 122, -1, 10, 
	32, 98, 105, 9, 13, 111, 110, 100, 
	95, 48, 57, 65, 90, 97, 122, 32, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 32, 9, 13, 48, 57, 10, 
	32, 35, 9, 13, 48, 57, 10, 32, 
	35, 9, 13, 48, 57, 10, 32, 35, 
	98, 105, 9, 13, 48, 57, -1, 10, 
	110, 102, 111, 32, 9, 13, 32, 97, 
	9, 13, 116, 111, 109, 32, 9, 13, 
	32, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 61, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 32, 61, 9, 13, 32, 
	9, 13, 32, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 98, 105, 9, 13, -1, 10, 9, 
	32, 45, 95, 11, 13, 48, 57, 65, 
	90, 97, 122, 9, 32, 45, 95, 11, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 9, 13, 48, 57, 32, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 45, 95, 100, 9, 13, 48, 
	57, 65, 90, 97, 122, 32, 45, 95, 
	105, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 45, 95, 114, 9, 13, 48, 
	57, 65, 90, 97, 122, 32, 45, 95, 
	101, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 45, 95, 99, 9, 13, 48, 
	57, 65, 90, 97, 122, 32, 45, 95, 
	116, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 45, 95, 105, 9, 13, 48, 
	57, 65, 90, 97, 122, 32, 45, 95, 
	111, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 45, 95, 110, 9, 13, 48, 
	57, 65, 90, 97, 122, 32, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	32, 9, 13, 48, 57, 10, 32, 35, 
	9, 13, 48, 57, 10, 32, 35, 9, 
	13, 48, 57, 10, 32, 35, 98, 105, 
	9, 13, 48, 57, 10, 32, 35, 9, 
	13, 48, 57, 10, 32, 35, 9, 13, 
	48, 57, 10, 32, 35, 98, 105, 9, 
	13, 48, 57, -1, 10, 10, 32, 35, 
	9, 13, 48, 57, 10, 32, 35, 9, 
	13, 48, 57, 10, 32, 35, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	98, 105, 9, 13, 9, 32, 45, 95, 
	11, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 111, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 45, 95, 110, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 100, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 98, 105, 9, 13, 
	48, 57, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 100, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 105, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 114, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	101, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 99, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 116, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 105, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	111, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 95, 110, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 98, 105, 9, 13, 
	48, 57, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 98, 
	105, 9, 13, 48, 57, 10, 32, 35, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 98, 105, 9, 13, 48, 57, 
	-1, 10, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 110, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 95, 102, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 111, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	97, 9, 13, 48, 57, 65, 90, 98, 
	122, 10, 32, 35, 97, 98, 105, 9, 
	13, 10, 32, 35, 45, 95, 116, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 45, 95, 111, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	45, 95, 109, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 35, 45, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 45, 95, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 35, 
	95, 98, 105, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 111, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 110, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 45, 
	95, 100, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 61, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 32, 
	61, 9, 13, 48, 57, 10, 32, 35, 
	45, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 45, 61, 95, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 35, 61, 98, 105, 9, 13, 
	48, 57, 10, 32, 35, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 100, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 105, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 45, 
	95, 114, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 95, 101, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 45, 95, 99, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 45, 95, 
	116, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 45, 95, 105, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 95, 111, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 110, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 45, 61, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 61, 9, 13, 48, 57, 10, 
	32, 35, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	61, 95, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 35, 61, 98, 105, 
	9, 13, 48, 57, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 45, 61, 95, 9, 
	13, 48, 57, 65, 90, 97, 122, 10, 
	32, 35, 61, 98, 105, 9, 13, 48, 
	57, 10, 32, 35, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 45, 95, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 110, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 102, 9, 13, 48, 
	57, 65, 90, 97, 122, 10, 32, 45, 
	95, 111, 9, 13, 48, 57, 65, 90, 
	97, 122, 10, 32, 45, 95, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 61, 95, 97, 9, 13, 48, 57, 
	65, 90, 98, 122, 32, 61, 97, 9, 
	13, 10, 32, 45, 95, 116, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	45, 95, 111, 9, 13, 48, 57, 65, 
	90, 97, 122, 10, 32, 45, 95, 109, 
	9, 13, 48, 57, 65, 90, 97, 122, 
	10, 32, 45, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 45, 61, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 32, 61, 95, 9, 13, 48, 57, 
	65, 90, 97, 122, 10, 32, 35, 45, 
	95, 9, 13, 48, 57, 65, 90, 97, 
	122, 10, 32, 35, 61, 98, 105, 9, 
	13, 32, 41, 9, 13, 48, 57, 48, 
	57, 32, 41, 9, 13, 48, 57, 32, 
	41, 9, 13, 48, 57, 32, 44, 9, 
	13, 48, 57, 48, 57, 32, 44, 9, 
	13, 48, 57, 32, 44, 9, 13, 48, 
	57, 32, 44, 9, 13, 48, 57, 48, 
	57, 32, 44, 9, 13, 48, 57, 32, 
	44, 9, 13, 48, 57, 32, 41, 9, 
	13, 48, 57, 32, 9, 13, 48, 57, 
	10, 32, 35, 95, 98, 105, 9, 13, 
	48, 57, 65, 90, 97, 122, 32, 98, 
	105, 9, 13, 10, 32, 35, 98, 105, 
	9, 13, 48, 57, 10, 32, 35, 98, 
	105, 9, 13, 10, 32, 35, 98, 105, 
	9, 13, 48, 57, 10, 32, 35, 98, 
	105, 9, 13, 48, 57, 10, 32, 35, 
	98, 105, 9, 13, 10, 32, 35, 98, 
	105, 9, 13, 48, 57, 10, 32, 35, 
	98, 105, 9, 13, 48, 57, 10, 32, 
	35, 98, 105, 9, 13, 48, 57, 10, 
	32, 35, 98, 105, 9, 13, 48, 57, 
	10, 32, 35, 97, 98, 105, 9, 13, 
	10, 32, 35, 95, 98, 105, 9, 13, 
	48, 57, 65, 90, 97, 122, 10, 32, 
	35, 61, 98, 105, 9, 13, 48, 57, 
	10, 32, 35, 61, 98, 105, 9, 13, 
	48, 57, 10, 32, 35, 61, 98, 105, 
	9, 13, 48, 57, 10, 32, 35, 61, 
	98, 105, 9, 13, 0
};

static const char _atom_stmt_test_single_lengths[] = {
	0, 2, 1, 1, 1, 1, 1, 1, 
	2, 1, 2, 2, 1, 2, 3, 0, 
	2, 2, 3, 0, 2, 2, 3, 0, 
	2, 2, 3, 4, 6, 2, 3, 1, 
	1, 1, 1, 3, 1, 3, 3, 5, 
	2, 1, 1, 1, 1, 2, 1, 1, 
	1, 1, 2, 4, 5, 2, 1, 2, 
	5, 5, 5, 2, 4, 4, 3, 3, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 3, 1, 3, 3, 5, 3, 3, 
	5, 2, 3, 3, 5, 5, 5, 4, 
	6, 6, 6, 5, 5, 5, 5, 5, 
	5, 4, 4, 5, 6, 6, 6, 6, 
	6, 6, 6, 6, 6, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 2, 5, 
	5, 6, 6, 6, 5, 6, 6, 6, 
	6, 6, 5, 5, 6, 5, 5, 5, 
	4, 4, 5, 2, 5, 6, 6, 5, 
	4, 4, 4, 5, 5, 5, 5, 5, 
	5, 5, 5, 5, 4, 5, 2, 5, 
	6, 6, 5, 6, 6, 5, 5, 5, 
	5, 5, 4, 6, 3, 5, 5, 5, 
	4, 5, 3, 5, 6, 2, 0, 2, 
	2, 2, 0, 2, 2, 2, 0, 2, 
	2, 2, 1, 6, 3, 5, 5, 5, 
	5, 5, 5, 5, 5, 5, 6, 6, 
	6, 6, 6, 6
};

static const char _atom_stmt_test_range_lengths[] = {
	0, 1, 0, 0, 0, 1, 2, 2, 
	1, 2, 2, 1, 1, 1, 2, 1, 
	2, 1, 2, 1, 2, 1, 2, 1, 
	2, 1, 1, 4, 4, 0, 1, 0, 
	0, 0, 3, 4, 2, 2, 2, 2, 
	0, 0, 0, 0, 1, 1, 0, 0, 
	0, 1, 4, 4, 4, 1, 1, 4, 
	4, 4, 1, 0, 4, 4, 2, 4, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 2, 2, 2, 2, 2, 2, 
	2, 0, 2, 2, 4, 4, 1, 4, 
	4, 4, 4, 4, 4, 4, 2, 4, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 4, 4, 4, 4, 4, 2, 
	4, 4, 2, 4, 4, 2, 0, 4, 
	4, 4, 4, 4, 4, 4, 1, 4, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 4, 2, 4, 4, 2, 4, 
	4, 4, 4, 4, 4, 4, 4, 4, 
	4, 4, 4, 4, 4, 4, 2, 4, 
	4, 2, 4, 4, 2, 4, 4, 4, 
	4, 4, 4, 4, 1, 4, 4, 4, 
	4, 4, 4, 4, 1, 2, 1, 2, 
	2, 2, 1, 2, 2, 2, 1, 2, 
	2, 2, 2, 4, 1, 2, 1, 2, 
	2, 1, 2, 2, 2, 2, 1, 4, 
	2, 2, 2, 1
};

static const short _atom_stmt_test_index_offsets[] = {
	0, 0, 4, 6, 8, 10, 13, 17, 
	21, 25, 29, 34, 38, 41, 45, 51, 
	53, 58, 62, 68, 70, 75, 79, 85, 
	87, 92, 96, 101, 110, 121, 124, 129, 
	131, 133, 135, 140, 148, 152, 158, 164, 
	172, 175, 177, 179, 181, 184, 188, 190, 
	192, 194, 197, 204, 213, 223, 227, 230, 
	237, 247, 257, 264, 267, 276, 285, 291, 
	299, 308, 317, 326, 335, 344, 353, 362, 
	371, 380, 388, 392, 398, 404, 412, 418, 
	424, 432, 435, 441, 447, 457, 467, 474, 
	483, 494, 505, 516, 526, 536, 546, 554, 
	564, 574, 583, 592, 602, 613, 624, 635, 
	646, 657, 668, 679, 690, 701, 711, 721, 
	729, 739, 749, 757, 767, 777, 785, 788, 
	798, 808, 819, 830, 841, 851, 862, 870, 
	881, 892, 903, 913, 923, 934, 944, 954, 
	964, 973, 982, 992, 997, 1007, 1018, 1027, 
	1037, 1046, 1055, 1064, 1074, 1084, 1094, 1104, 
	1114, 1124, 1134, 1144, 1154, 1163, 1173, 1178, 
	1188, 1199, 1208, 1218, 1229, 1238, 1248, 1258, 
	1268, 1278, 1288, 1297, 1308, 1313, 1323, 1333, 
	1343, 1352, 1362, 1370, 1380, 1388, 1393, 1395, 
	1400, 1405, 1410, 1412, 1417, 1422, 1427, 1429, 
	1434, 1439, 1444, 1448, 1459, 1464, 1472, 1479, 
	1487, 1495, 1502, 1510, 1518, 1526, 1534, 1542, 
	1553, 1562, 1571, 1580
};

static const unsigned char _atom_stmt_test_trans_targs_wi[] = {
	1, 2, 1, 0, 3, 0, 4, 0, 
	5, 0, 6, 6, 0, 6, 6, 7, 
	0, 8, 8, 194, 0, 8, 9, 8, 
	0, 9, 9, 10, 0, 11, 12, 11, 
	193, 0, 11, 12, 11, 0, 13, 13, 
	0, 13, 14, 13, 0, 14, 15, 190, 
	14, 16, 0, 16, 0, 17, 18, 17, 
	189, 0, 17, 18, 17, 0, 18, 19, 
	186, 18, 20, 0, 20, 0, 21, 22, 
	21, 185, 0, 21, 22, 21, 0, 22, 
	23, 182, 22, 24, 0, 24, 0, 25, 
	26, 25, 181, 0, 25, 26, 25, 0, 
	195, 27, 29, 27, 0, 195, 27, 29, 
	84, 27, 84, 84, 84, 0, 195, 28, 
	29, 84, 88, 121, 28, 84, 84, 84, 
	0, 0, 196, 29, 30, 31, 41, 30, 
	0, 32, 0, 33, 0, 34, 0, 64, 
	35, 35, 35, 0, 36, 63, 63, 36, 
	63, 63, 63, 0, 36, 36, 37, 0, 
	197, 38, 40, 38, 62, 0, 197, 38, 
	40, 38, 37, 0, 197, 39, 40, 31, 
	41, 39, 37, 0, 0, 196, 40, 42, 
	0, 43, 0, 44, 0, 45, 45, 0, 
	45, 46, 45, 0, 47, 0, 48, 0, 
	49, 0, 50, 50, 0, 50, 51, 50, 
	51, 51, 51, 0, 53, 52, 61, 51, 
	52, 51, 51, 51, 0, 53, 52, 61, 
	54, 51, 52, 51, 51, 51, 0, 53, 
	54, 53, 0, 55, 55, 0, 55, 56, 
	55, 56, 56, 56, 0, 198, 57, 59, 
	60, 56, 57, 56, 56, 56, 0, 198, 
	57, 59, 60, 56, 57, 56, 56, 56, 
	0, 198, 58, 59, 31, 41, 58, 0, 
	0, 196, 59, 60, 60, 60, 56, 60, 
	56, 56, 56, 0, 61, 61, 61, 51, 
	61, 51, 51, 51, 0, 197, 38, 40, 
	38, 62, 0, 36, 63, 63, 36, 63, 
	63, 63, 0, 36, 63, 63, 65, 36, 
	63, 63, 63, 0, 36, 63, 63, 66, 
	36, 63, 63, 63, 0, 36, 63, 63, 
	67, 36, 63, 63, 63, 0, 36, 63, 
	63, 68, 36, 63, 63, 63, 0, 36, 
	63, 63, 69, 36, 63, 63, 63, 0, 
	36, 63, 63, 70, 36, 63, 63, 63, 
	0, 36, 63, 63, 71, 36, 63, 63, 
	63, 0, 36, 63, 63, 72, 36, 63, 
	63, 63, 0, 36, 63, 63, 73, 36, 
	63, 63, 63, 0, 74, 63, 63, 74, 
	63, 63, 63, 0, 74, 74, 75, 0, 
	199, 76, 40, 76, 83, 0, 199, 76, 
	40, 76, 78, 0, 199, 77, 40, 31, 
	41, 77, 78, 0, 200, 79, 81, 79, 
	82, 0, 200, 79, 81, 79, 37, 0, 
	200, 80, 81, 31, 41, 80, 37, 0, 
	0, 196, 81, 200, 79, 81, 79, 82, 
	0, 199, 76, 40, 76, 83, 0, 201, 
	85, 29, 87, 84, 85, 84, 84, 84, 
	0, 201, 85, 29, 87, 84, 85, 84, 
	84, 84, 0, 201, 86, 29, 31, 41, 
	86, 0, 87, 87, 87, 84, 87, 84, 
	84, 84, 0, 201, 85, 29, 87, 84, 
	89, 85, 84, 84, 84, 0, 201, 85, 
	29, 87, 84, 90, 85, 84, 84, 84, 
	0, 201, 85, 29, 87, 84, 91, 85, 
	84, 84, 84, 0, 201, 85, 29, 87, 
	100, 85, 92, 92, 92, 0, 202, 93, 
	29, 97, 99, 93, 99, 99, 99, 0, 
	202, 93, 29, 87, 84, 93, 95, 84, 
	84, 0, 202, 94, 29, 31, 41, 94, 
	37, 0, 202, 93, 29, 87, 84, 93, 
	96, 84, 84, 0, 202, 93, 29, 87, 
	84, 93, 96, 84, 84, 0, 36, 98, 
	97, 99, 98, 99, 99, 99, 0, 36, 
	98, 87, 84, 98, 95, 84, 84, 0, 
	202, 93, 29, 97, 99, 93, 99, 99, 
	99, 0, 202, 93, 29, 97, 99, 101, 
	93, 99, 99, 99, 0, 202, 93, 29, 
	97, 99, 102, 93, 99, 99, 99, 0, 
	202, 93, 29, 97, 99, 103, 93, 99, 
	99, 99, 0, 202, 93, 29, 97, 99, 
	104, 93, 99, 99, 99, 0, 202, 93, 
	29, 97, 99, 105, 93, 99, 99, 99, 
	0, 202, 93, 29, 97, 99, 106, 93, 
	99, 99, 99, 0, 202, 93, 29, 97, 
	99, 107, 93, 99, 99, 99, 0, 202, 
	93, 29, 97, 99, 108, 93, 99, 99, 
	99, 0, 202, 93, 29, 97, 99, 109, 
	93, 99, 99, 99, 0, 203, 110, 29, 
	97, 99, 110, 99, 99, 99, 0, 203, 
	110, 29, 87, 84, 110, 112, 84, 84, 
	0, 203, 111, 29, 31, 41, 111, 75, 
	0, 204, 113, 29, 87, 84, 113, 120, 
	84, 84, 0, 204, 113, 29, 87, 84, 
	113, 115, 84, 84, 0, 204, 114, 29, 
	31, 41, 114, 78, 0, 205, 116, 118, 
	87, 84, 116, 119, 84, 84, 0, 205, 
	116, 118, 87, 84, 116, 95, 84, 84, 
	0, 205, 117, 118, 31, 41, 117, 37, 
	0, 0, 196, 118, 205, 116, 118, 87, 
	84, 116, 119, 84, 84, 0, 204, 113, 
	29, 87, 84, 113, 120, 84, 84, 0, 
	201, 85, 29, 87, 84, 122, 85, 84, 
	84, 84, 0, 201, 85, 29, 87, 84, 
	123, 85, 84, 84, 84, 0, 201, 85, 
	29, 87, 84, 124, 85, 84, 84, 84, 
	0, 206, 125, 29, 87, 84, 125, 84, 
	84, 84, 0, 206, 125, 29, 87, 84, 
	127, 125, 84, 84, 84, 0, 206, 126, 
	29, 46, 31, 41, 126, 0, 201, 85, 
	29, 87, 84, 128, 85, 84, 84, 84, 
	0, 201, 85, 29, 87, 84, 129, 85, 
	84, 84, 84, 0, 201, 85, 29, 87, 
	84, 130, 85, 84, 84, 84, 0, 207, 
	131, 29, 87, 84, 131, 84, 84, 84, 
	0, 207, 131, 29, 87, 179, 131, 179, 
	179, 179, 0, 207, 132, 29, 51, 133, 
	167, 132, 51, 51, 51, 0, 53, 52, 
	61, 51, 134, 52, 51, 51, 51, 0, 
	53, 52, 61, 51, 135, 52, 51, 51, 
	51, 0, 53, 52, 61, 51, 136, 52, 
	51, 51, 51, 0, 53, 52, 61, 147, 
	52, 137, 137, 137, 0, 139, 138, 144, 
	146, 138, 146, 146, 146, 0, 139, 138, 
	61, 54, 51, 138, 140, 51, 51, 0, 
	139, 54, 139, 37, 0, 208, 141, 40, 
	61, 51, 141, 143, 51, 51, 0, 208, 
	141, 40, 61, 54, 51, 141, 140, 51, 
	51, 0, 208, 142, 40, 54, 31, 41, 
	142, 37, 0, 208, 141, 40, 61, 51, 
	141, 143, 51, 51, 0, 36, 145, 144, 
	146, 145, 146, 146, 146, 0, 36, 145, 
	61, 51, 145, 140, 51, 51, 0, 139, 
	138, 144, 146, 138, 146, 146, 146, 0, 
	139, 138, 144, 146, 148, 138, 146, 146, 
	146, 0, 139, 138, 144, 146, 149, 138, 
	146, 146, 146, 0, 139, 138, 144, 146, 
	150, 138, 146, 146, 146, 0, 139, 138, 
	144, 146, 151, 138, 146, 146, 146, 0, 
	139, 138, 144, 146, 152, 138, 146, 146, 
	146, 0, 139, 138, 144, 146, 153, 138, 
	146, 146, 146, 0, 139, 138, 144, 146, 
	154, 138, 146, 146, 146, 0, 139, 138, 
	144, 146, 155, 138, 146, 146, 146, 0, 
	139, 138, 144, 146, 156, 138, 146, 146, 
	146, 0, 158, 157, 144, 146, 157, 146, 
	146, 146, 0, 158, 157, 61, 54, 51, 
	157, 159, 51, 51, 0, 158, 54, 158, 
	75, 0, 209, 160, 40, 61, 51, 160, 
	166, 51, 51, 0, 209, 160, 40, 61, 
	54, 51, 160, 162, 51, 51, 0, 209, 
	161, 40, 54, 31, 41, 161, 78, 0, 
	210, 163, 81, 61, 51, 163, 165, 51, 
	51, 0, 210, 163, 81, 61, 54, 51, 
	163, 140, 51, 51, 0, 210, 164, 81, 
	54, 31, 41, 164, 37, 0, 210, 163, 
	81, 61, 51, 163, 165, 51, 51, 0, 
	209, 160, 40, 61, 51, 160, 166, 51, 
	51, 0, 53, 52, 61, 51, 168, 52, 
	51, 51, 51, 0, 53, 52, 61, 51, 
	169, 52, 51, 51, 51, 0, 53, 52, 
	61, 51, 170, 52, 51, 51, 51, 0, 
	172, 171, 61, 51, 171, 51, 51, 51, 
	0, 172, 171, 61, 54, 51, 173, 171, 
	51, 51, 51, 0, 172, 54, 46, 172, 
	0, 53, 52, 61, 51, 174, 52, 51, 
	51, 51, 0, 53, 52, 61, 51, 175, 
	52, 51, 51, 51, 0, 53, 52, 61, 
	51, 176, 52, 51, 51, 51, 0, 178, 
	177, 61, 51, 177, 51, 51, 51, 0, 
	178, 177, 61, 54, 51, 177, 51, 51, 
	51, 0, 178, 54, 51, 178, 51, 51, 
	51, 0, 211, 52, 29, 61, 51, 52, 
	51, 51, 51, 0, 211, 180, 29, 54, 
	31, 41, 180, 0, 25, 26, 25, 181, 
	0, 183, 0, 25, 26, 25, 184, 0, 
	25, 26, 25, 184, 0, 21, 22, 21, 
	185, 0, 187, 0, 21, 22, 21, 188, 
	0, 21, 22, 21, 188, 0, 17, 18, 
	17, 189, 0, 191, 0, 17, 18, 17, 
	192, 0, 17, 18, 17, 192, 0, 11, 
	12, 11, 193, 0, 8, 8, 194, 0, 
	195, 28, 29, 84, 88, 121, 28, 84, 
	84, 84, 0, 30, 31, 41, 30, 0, 
	197, 39, 40, 31, 41, 39, 37, 0, 
	198, 58, 59, 31, 41, 58, 0, 199, 
	77, 40, 31, 41, 77, 78, 0, 200, 
	80, 81, 31, 41, 80, 37, 0, 201, 
	86, 29, 31, 41, 86, 0, 202, 94, 
	29, 31, 41, 94, 37, 0, 203, 111, 
	29, 31, 41, 111, 75, 0, 204, 114, 
	29, 31, 41, 114, 78, 0, 205, 117, 
	118, 31, 41, 117, 37, 0, 206, 126, 
	29, 46, 31, 41, 126, 0, 207, 132, 
	29, 51, 133, 167, 132, 51, 51, 51, 
	0, 208, 142, 40, 54, 31, 41, 142, 
	37, 0, 209, 161, 40, 54, 31, 41, 
	161, 78, 0, 210, 164, 81, 54, 31, 
	41, 164, 37, 0, 211, 180, 29, 54, 
	31, 41, 180, 0, 0
};

static const unsigned char _atom_stmt_test_trans_actions_wi[] = {
	0, 0, 0, 41, 0, 41, 0, 41, 
	0, 41, 0, 0, 41, 0, 0, 0, 
	41, 23, 23, 3, 41, 0, 0, 0, 
	41, 0, 0, 0, 41, 0, 0, 0, 
	3, 41, 0, 0, 0, 41, 25, 25, 
	41, 0, 0, 0, 41, 0, 0, 0, 
	0, 0, 41, 0, 41, 0, 27, 0, 
	3, 41, 0, 27, 0, 41, 0, 0, 
	0, 0, 0, 41, 0, 41, 0, 29, 
	0, 3, 41, 0, 29, 0, 41, 0, 
	0, 0, 0, 0, 41, 0, 41, 0, 
	31, 0, 3, 41, 0, 31, 0, 41, 
	33, 0, 0, 0, 41, 33, 0, 0, 
	13, 0, 13, 13, 13, 41, 33, 0, 
	0, 13, 13, 13, 0, 13, 13, 13, 
	41, 41, 33, 0, 0, 0, 0, 0, 
	41, 0, 41, 0, 41, 0, 41, 0, 
	0, 0, 0, 41, 0, 9, 9, 0, 
	9, 9, 9, 41, 0, 0, 0, 41, 
	35, 35, 35, 35, 3, 41, 0, 0, 
	0, 0, 0, 41, 0, 0, 0, 0, 
	0, 0, 0, 41, 41, 0, 0, 0, 
	41, 0, 41, 0, 41, 0, 0, 41, 
	0, 0, 0, 41, 0, 41, 0, 41, 
	0, 41, 0, 0, 41, 0, 13, 0, 
	13, 13, 13, 41, 15, 70, 13, 13, 
	70, 13, 13, 13, 41, 0, 13, 13, 
	0, 13, 13, 13, 13, 13, 41, 0, 
	0, 0, 41, 0, 0, 41, 0, 19, 
	0, 19, 19, 19, 41, 79, 76, 21, 
	19, 19, 76, 19, 19, 19, 41, 39, 
	19, 0, 19, 19, 19, 19, 19, 19, 
	41, 39, 0, 0, 0, 0, 0, 41, 
	41, 39, 0, 19, 19, 19, 19, 19, 
	19, 19, 19, 41, 13, 13, 13, 13, 
	13, 13, 13, 13, 41, 35, 35, 35, 
	35, 3, 41, 0, 9, 9, 0, 9, 
	9, 9, 41, 0, 9, 9, 9, 0, 
	9, 9, 9, 41, 0, 9, 9, 9, 
	0, 9, 9, 9, 41, 0, 9, 9, 
	9, 0, 9, 9, 9, 41, 0, 9, 
	9, 9, 0, 9, 9, 9, 41, 0, 
	9, 9, 9, 0, 9, 9, 9, 41, 
	0, 9, 9, 9, 0, 9, 9, 9, 
	41, 0, 9, 9, 9, 0, 9, 9, 
	9, 41, 0, 9, 9, 9, 0, 9, 
	9, 9, 41, 0, 9, 9, 9, 0, 
	9, 9, 9, 41, 0, 9, 9, 0, 
	9, 9, 9, 41, 0, 0, 0, 41, 
	35, 35, 35, 35, 3, 41, 0, 0, 
	0, 0, 0, 41, 0, 0, 0, 0, 
	0, 0, 0, 41, 88, 35, 35, 35, 
	46, 41, 37, 0, 0, 0, 0, 41, 
	37, 0, 0, 0, 0, 0, 0, 41, 
	41, 37, 0, 88, 35, 35, 35, 46, 
	41, 35, 35, 35, 35, 3, 41, 103, 
	99, 73, 13, 13, 99, 13, 13, 13, 
	41, 33, 13, 0, 13, 13, 13, 13, 
	13, 13, 41, 33, 0, 0, 0, 0, 
	0, 41, 13, 13, 13, 13, 13, 13, 
	13, 13, 41, 103, 99, 73, 13, 13, 
	13, 99, 13, 13, 13, 41, 103, 99, 
	73, 13, 13, 13, 99, 13, 13, 13, 
	41, 103, 99, 73, 13, 13, 13, 99, 
	13, 13, 13, 41, 103, 99, 73, 13, 
	13, 99, 13, 13, 13, 41, 103, 99, 
	73, 67, 67, 99, 67, 67, 67, 41, 
	33, 13, 0, 13, 13, 13, 13, 13, 
	13, 41, 33, 0, 0, 0, 0, 0, 
	0, 41, 124, 119, 107, 13, 13, 119, 
	64, 13, 13, 41, 124, 119, 107, 13, 
	13, 119, 64, 13, 13, 41, 0, 13, 
	67, 67, 13, 67, 67, 67, 41, 0, 
	13, 13, 13, 13, 13, 13, 13, 41, 
	103, 99, 73, 67, 67, 99, 67, 67, 
	67, 41, 103, 99, 73, 67, 67, 67, 
	99, 67, 67, 67, 41, 103, 99, 73, 
	67, 67, 67, 99, 67, 67, 67, 41, 
	103, 99, 73, 67, 67, 67, 99, 67, 
	67, 67, 41, 103, 99, 73, 67, 67, 
	67, 99, 67, 67, 67, 41, 103, 99, 
	73, 67, 67, 67, 99, 67, 67, 67, 
	41, 103, 99, 73, 67, 67, 67, 99, 
	67, 67, 67, 41, 103, 99, 73, 67, 
	67, 67, 99, 67, 67, 67, 41, 103, 
	99, 73, 67, 67, 67, 99, 67, 67, 
	67, 41, 103, 99, 73, 67, 67, 67, 
	99, 67, 67, 67, 41, 103, 99, 73, 
	67, 67, 99, 67, 67, 67, 41, 33, 
	13, 0, 13, 13, 13, 13, 13, 13, 
	41, 33, 0, 0, 0, 0, 0, 0, 
	41, 124, 119, 107, 13, 13, 119, 64, 
	13, 13, 41, 33, 13, 0, 13, 13, 
	13, 13, 13, 13, 41, 33, 0, 0, 
	0, 0, 0, 0, 41, 129, 119, 107, 
	13, 13, 119, 95, 13, 13, 41, 82, 
	13, 0, 13, 13, 13, 13, 13, 13, 
	41, 82, 0, 0, 0, 0, 0, 0, 
	41, 41, 82, 0, 129, 119, 107, 13, 
	13, 119, 95, 13, 13, 41, 124, 119, 
	107, 13, 13, 119, 64, 13, 13, 41, 
	103, 99, 73, 13, 13, 13, 99, 13, 
	13, 13, 41, 103, 99, 73, 13, 13, 
	13, 99, 13, 13, 13, 41, 103, 99, 
	73, 13, 13, 13, 99, 13, 13, 13, 
	41, 103, 99, 73, 13, 13, 99, 13, 
	13, 13, 41, 33, 13, 0, 13, 13, 
	13, 13, 13, 13, 13, 41, 33, 0, 
	0, 0, 0, 0, 0, 41, 103, 99, 
	73, 13, 13, 13, 99, 13, 13, 13, 
	41, 103, 99, 73, 13, 13, 13, 99, 
	13, 13, 13, 41, 103, 99, 73, 13, 
	13, 13, 99, 13, 13, 13, 41, 103, 
	99, 73, 13, 13, 99, 13, 13, 13, 
	41, 33, 13, 0, 13, 13, 13, 13, 
	13, 13, 41, 33, 0, 0, 13, 13, 
	13, 0, 13, 13, 13, 41, 15, 70, 
	13, 13, 13, 70, 13, 13, 13, 41, 
	15, 70, 13, 13, 13, 70, 13, 13, 
	13, 41, 15, 70, 13, 13, 13, 70, 
	13, 13, 13, 41, 15, 70, 13, 13, 
	70, 13, 13, 13, 41, 15, 70, 61, 
	61, 70, 61, 61, 61, 41, 0, 13, 
	13, 0, 13, 13, 13, 13, 13, 41, 
	0, 0, 0, 0, 41, 85, 111, 35, 
	13, 13, 111, 49, 13, 13, 41, 0, 
	13, 0, 13, 0, 13, 13, 13, 13, 
	13, 41, 0, 0, 0, 0, 0, 0, 
	0, 0, 41, 85, 111, 35, 13, 13, 
	111, 49, 13, 13, 41, 0, 13, 61, 
	61, 13, 61, 61, 61, 41, 0, 13, 
	13, 13, 13, 13, 13, 13, 41, 15, 
	70, 61, 61, 70, 61, 61, 61, 41, 
	15, 70, 61, 61, 61, 70, 61, 61, 
	61, 41, 15, 70, 61, 61, 61, 70, 
	61, 61, 61, 41, 15, 70, 61, 61, 
	61, 70, 61, 61, 61, 41, 15, 70, 
	61, 61, 61, 70, 61, 61, 61, 41, 
	15, 70, 61, 61, 61, 70, 61, 61, 
	61, 41, 15, 70, 61, 61, 61, 70, 
	61, 61, 61, 41, 15, 70, 61, 61, 
	61, 70, 61, 61, 61, 41, 15, 70, 
	61, 61, 61, 70, 61, 61, 61, 41, 
	15, 70, 61, 61, 61, 70, 61, 61, 
	61, 41, 15, 70, 61, 61, 70, 61, 
	61, 61, 41, 0, 13, 13, 0, 13, 
	13, 13, 13, 13, 41, 0, 0, 0, 
	0, 41, 85, 111, 35, 13, 13, 111, 
	49, 13, 13, 41, 0, 13, 0, 13, 
	0, 13, 13, 13, 13, 13, 41, 0, 
	0, 0, 0, 0, 0, 0, 0, 41, 
	115, 111, 35, 13, 13, 111, 91, 13, 
	13, 41, 37, 13, 0, 13, 0, 13, 
	13, 13, 13, 13, 41, 37, 0, 0, 
	0, 0, 0, 0, 0, 41, 115, 111, 
	35, 13, 13, 111, 91, 13, 13, 41, 
	85, 111, 35, 13, 13, 111, 49, 13, 
	13, 41, 15, 70, 13, 13, 13, 70, 
	13, 13, 13, 41, 15, 70, 13, 13, 
	13, 70, 13, 13, 13, 41, 15, 70, 
	13, 13, 13, 70, 13, 13, 13, 41, 
	15, 70, 13, 13, 70, 13, 13, 13, 
	41, 0, 13, 13, 0, 13, 13, 13, 
	13, 13, 13, 41, 0, 0, 0, 0, 
	41, 15, 70, 13, 13, 13, 70, 13, 
	13, 13, 41, 15, 70, 13, 13, 13, 
	70, 13, 13, 13, 41, 15, 70, 13, 
	13, 13, 70, 13, 13, 13, 41, 15, 
	70, 13, 13, 70, 13, 13, 13, 41, 
	0, 13, 13, 0, 13, 13, 13, 13, 
	13, 41, 0, 0, 13, 0, 13, 13, 
	13, 41, 103, 70, 73, 13, 13, 70, 
	13, 13, 13, 41, 33, 0, 0, 0, 
	0, 0, 0, 41, 0, 31, 0, 3, 
	41, 0, 41, 5, 58, 5, 3, 41, 
	5, 58, 5, 3, 41, 0, 29, 0, 
	3, 41, 0, 41, 5, 55, 5, 3, 
	41, 5, 55, 5, 3, 41, 0, 27, 
	0, 3, 41, 0, 41, 5, 52, 5, 
	3, 41, 5, 52, 5, 3, 41, 0, 
	0, 0, 3, 41, 23, 23, 3, 41, 
	33, 0, 0, 13, 13, 13, 0, 13, 
	13, 13, 41, 0, 0, 0, 0, 41, 
	0, 0, 0, 0, 0, 0, 0, 41, 
	39, 0, 0, 0, 0, 0, 41, 0, 
	0, 0, 0, 0, 0, 0, 41, 37, 
	0, 0, 0, 0, 0, 0, 41, 33, 
	0, 0, 0, 0, 0, 41, 33, 0, 
	0, 0, 0, 0, 0, 41, 33, 0, 
	0, 0, 0, 0, 0, 41, 33, 0, 
	0, 0, 0, 0, 0, 41, 82, 0, 
	0, 0, 0, 0, 0, 41, 33, 0, 
	0, 0, 0, 0, 0, 41, 33, 0, 
	0, 13, 13, 13, 0, 13, 13, 13, 
	41, 0, 0, 0, 0, 0, 0, 0, 
	0, 41, 0, 0, 0, 0, 0, 0, 
	0, 0, 41, 37, 0, 0, 0, 0, 
	0, 0, 0, 41, 33, 0, 0, 0, 
	0, 0, 0, 41, 0
};

static const unsigned char _atom_stmt_test_to_state_actions[] = {
	0, 0, 0, 0, 0, 0, 0, 1, 
	0, 0, 1, 0, 0, 0, 0, 0, 
	1, 0, 0, 0, 1, 0, 0, 0, 
	1, 0, 0, 11, 11, 0, 0, 0, 
	0, 0, 0, 7, 0, 1, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 11, 0, 0, 0, 0, 17, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	7, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 1, 0, 0, 43, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 7, 0, 0, 1, 
	0, 0, 0, 0, 7, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	1, 0, 0, 43, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 11, 11, 0, 0, 0, 
	0, 7, 0, 0, 1, 0, 0, 0, 
	0, 0, 0, 7, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 1, 
	0, 0, 43, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 11, 11, 0, 0, 0, 0, 1, 
	0, 0, 0, 1, 0, 0, 0, 1, 
	0, 0, 0, 11, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 11, 
	0, 0, 0, 0
};

static const unsigned char _atom_stmt_test_eof_actions[] = {
	0, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 41, 41, 41, 41, 41, 
	41, 41, 41, 0, 0, 0, 0, 0, 
	0, 0, 0, 0, 0, 0, 0, 0, 
	0, 0, 0, 0
};

static const int atom_stmt_test_start = 1;
static const int atom_stmt_test_first_final = 195;
static const int atom_stmt_test_error = 0;

static const int atom_stmt_test_en_main = 1;

#line 356 "NanorexMMPImportExportTest.rl"
	
#line 2242 "NanorexMMPImportExportTest.cpp"
	{
	cs = atom_stmt_test_start;
	}
#line 357 "NanorexMMPImportExportTest.rl"
	
#line 2248 "NanorexMMPImportExportTest.cpp"
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
	cs = _atom_stmt_test_trans_targs_wi[_trans];

	if ( _atom_stmt_test_trans_actions_wi[_trans] == 0 )
		goto _again;

	_acts = _atom_stmt_test_actions + _atom_stmt_test_trans_actions_wi[_trans];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 )
	{
		switch ( *_acts++ )
		{
	case 1:
#line 35 "NanorexMMPImportExportTest.rl"
	{intVal = intVal*10 + ((*p)-'0');}
	break;
	case 3:
#line 40 "NanorexMMPImportExportTest.rl"
	{intVal2 = intVal2*10 + ((*p)-'0');}
	break;
	case 4:
#line 43 "NanorexMMPImportExportTest.rl"
	{intVal=-intVal;}
	break;
	case 6:
#line 55 "NanorexMMPImportExportTest.rl"
	{stringVal = stringVal + (*p); }
	break;
	case 8:
#line 70 "NanorexMMPImportExportTest.rl"
	{stringVal = stringVal + (*p); }
	break;
	case 9:
#line 71 "NanorexMMPImportExportTest.rl"
	{ /*stripTrailingWhiteSpaces(stringVal);*/ }
	break;
	case 11:
#line 80 "NanorexMMPImportExportTest.rl"
	{stringVal2 = stringVal2 + (*p); }
	break;
	case 12:
#line 81 "NanorexMMPImportExportTest.rl"
	{ /*stripTrailingWhiteSpaces(stringVal2);*/ }
	break;
	case 13:
#line 26 "NanorexMMPImportExportTest.rl"
	{ atomId = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 14:
#line 31 "NanorexMMPImportExportTest.rl"
	{ atomicNum = intVal; /*cerr << "atomId = " << atomId << endl;*/}
	break;
	case 15:
#line 34 "NanorexMMPImportExportTest.rl"
	{x = intVal; }
	break;
	case 16:
#line 35 "NanorexMMPImportExportTest.rl"
	{y = intVal; }
	break;
	case 17:
#line 36 "NanorexMMPImportExportTest.rl"
	{z = intVal; }
	break;
	case 18:
#line 47 "NanorexMMPImportExportTest.rl"
	{ atomStyle = stringVal;
		    /*cerr << "atom_style = " << stringVal << endl;*/
		}
	break;
	case 19:
#line 52 "NanorexMMPImportExportTest.rl"
	{
		stripTrailingWhiteSpaces(atomStyle); 
		newAtom(atomId, atomicNum, x, y, z, atomStyle);
	}
	break;
	case 20:
#line 67 "NanorexMMPImportExportTest.rl"
	{
		newBond(stringVal, intVal);
	}
	break;
	case 21:
#line 76 "NanorexMMPImportExportTest.rl"
	{
		newBondDirection(intVal, intVal2);
	}
	break;
	case 22:
#line 85 "NanorexMMPImportExportTest.rl"
	{
		stripTrailingWhiteSpaces(stringVal);
		stripTrailingWhiteSpaces(stringVal2);
		newAtomInfo(stringVal, stringVal2);
	}
	break;
	case 23:
#line 339 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2413 "NanorexMMPImportExportTest.cpp"
		}
	}

_again:
	_acts = _atom_stmt_test_actions + _atom_stmt_test_to_state_actions[cs];
	_nacts = (unsigned int) *_acts++;
	while ( _nacts-- > 0 ) {
		switch ( *_acts++ ) {
	case 0:
#line 34 "NanorexMMPImportExportTest.rl"
	{intVal=(*p)-'0';}
	break;
	case 2:
#line 39 "NanorexMMPImportExportTest.rl"
	{intVal2=(*p)-'0';}
	break;
	case 5:
#line 54 "NanorexMMPImportExportTest.rl"
	{/*stringVal.clear();*/ stringVal = (*p); }
	break;
	case 7:
#line 69 "NanorexMMPImportExportTest.rl"
	{stringVal.clear();}
	break;
	case 10:
#line 79 "NanorexMMPImportExportTest.rl"
	{stringVal2.clear();}
	break;
#line 2442 "NanorexMMPImportExportTest.cpp"
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
	case 23:
#line 339 "NanorexMMPImportExportTest.rl"
	{ CPPUNIT_ASSERT_MESSAGE(false,
		                               "Error encountered in "
		                               "atom_stmt_test state machine");
		}
	break;
#line 2464 "NanorexMMPImportExportTest.cpp"
		}
	}
	}

	_out: {}
	}
#line 358 "NanorexMMPImportExportTest.rl"
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

