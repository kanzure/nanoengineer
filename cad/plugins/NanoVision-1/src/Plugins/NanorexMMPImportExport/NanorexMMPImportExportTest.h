// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NANOREXMMPIMPORTEXPORTTEST_H
#define NANOREXMMPIMPORTEXPORTTEST_H

#include <cppunit/extensions/HelperMacros.h>
#include <vector>
#include <string>


/* CLASS: NanorexMMPImportExportTest */
class NanorexMMPImportExportTest: public CPPUNIT_NS::TestFixture {
	
	CPPUNIT_TEST_SUITE(NanorexMMPImportExportTest);
	CPPUNIT_TEST(atomLineTest);
	CPPUNIT_TEST(bondLineTest);
	CPPUNIT_TEST(bondDirectionTest);
	CPPUNIT_TEST(infoAtomTest);
	CPPUNIT_TEST(atomStmtTest);
	CPPUNIT_TEST_SUITE_END();
	
private:
	
	struct Position {
		int x, y, z;
		Position(int _x, int _y, int _z) : x(_x), y(_y), z(_z) {}
		~Position() {}
	};
	
	struct AtomTestInfo {
		int id, atomicNum;
		Position pos;
		std::string style;
		AtomTestInfo(int _id, int _atomicNum, int _x, int _y, int _z,
		             std::string const& _style)
			: id(_id), atomicNum(_atomicNum),
			pos(_x,_y,_z), style(_style)
		{
		}
		~AtomTestInfo() {}
	};
	
public:
	void setUp(void);
	void tearDown(void);
	
	void atomLineTest(void);
	void bondLineTest(void);
	void bondDirectionTest(void);
	void infoAtomTest(void);
	
	/// @todo
	void atomStmtTest(void);
	
	
private:
	
	// scratch variables to hold values extracted by parser
	int intVal, intVal2;
	int x, y, z;
	std::string stringVal, stringVal2;
	int atomId, atomicNum;
	std::string atomStyle;
	
	// variables used in atom_decl_line tests
	std::vector<int> atomIds, atomicNums;
	std::vector<Position> atomLocs;
	std::vector<std::string> atomStyles;
	std::vector<std::map<std::string, std::string> > atomProps;
	
	// variables used in bond_line tests
	std::vector<std::map<std::string, std::vector<int> > > bonds;
	
	// variables used in bond_direction tests
	int bondDirectionStartId, bondDirectionStopId;
	
	// variables used in info_atom tests
	// std::vector<std::string> infoAtomKeys, infoAtomValues;
	
	// variables used in atom_stmt test
	
	
	// -- helper members --
	
	void atomLineTestSetUp(std::vector<std::string>& testStrings,
	                       std::vector<AtomTestInfo>& answers);
	void atomLineTestHelper(char const *const testInput);
	void atomLineTestTearDown(void);
	
	void bondLineTestHelper(char const *const testInput);
	void bondDirectionTestHelper(char const *const testInput);
	void infoAtomTestHelper(char const *const testInput);
	void atomStmtTestHelper(char const *const testInput);
	
	void newAtom(int atomId, int atomicNum,
	             int x, int y, int z,
	             std::string const& atomStyle);
	void newBond(std::string const& bondType, int targetAtomId);
	void newBondDirection(int atomId1, int atomId2);
	void newAtomInfo(std::string const& key, std::string const& value);
	
	void stripTrailingWhiteSpaces(std::string& s) {
		// std::cerr << "s = '" << s << "', s[end] = " << *s.rbegin()
		// 	<< " (int) " << int(*s.rbegin());
		std::string::const_reverse_iterator endCharIter = s.rbegin();
		int num_ws = 0;
		while(isspace(*endCharIter) && endCharIter != s.rend()) {
			++num_ws;
			++endCharIter;
		}
		s.resize((int)s.size()-num_ws);
		// std::cerr << ",  @end  s = '" << s << "'" << std::endl;
	}
	
	
};

#endif // NANOREXMMPIMPORTEXPORTTEST_H
