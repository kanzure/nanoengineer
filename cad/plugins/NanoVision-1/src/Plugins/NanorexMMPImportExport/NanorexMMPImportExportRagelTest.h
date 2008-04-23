// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NANOREXMMPIMPORTEXPORTRAGELTEST_H
#define NANOREXMMPIMPORTEXPORTRAGELTEST_H

#include <cppunit/extensions/HelperMacros.h>
#include <vector>
#include <stack>
#include <string>
#include "iterator.h"

#include "RagelIstreamPtr.h"

/* CLASS: NanorexMMPImportExportRagelTest */
class NanorexMMPImportExportRagelTest: public CPPUNIT_NS::TestFixture {
	
	CPPUNIT_TEST_SUITE(NanorexMMPImportExportRagelTest);
	CPPUNIT_TEST(atomLineTest);
	CPPUNIT_TEST(bondLineTest);
	CPPUNIT_TEST(bondDirectionTest);
	CPPUNIT_TEST(infoAtomTest);
	// CPPUNIT_TEST(atomStmtTest);
	CPPUNIT_TEST(multipleAtomStmtTest);
	CPPUNIT_TEST(molLineTest);
	CPPUNIT_TEST(csysLineTest);
	CPPUNIT_TEST(groupLineTest);
	CPPUNIT_TEST(uncheckedParseTest);
	CPPUNIT_TEST(checkedParseTest);
	CPPUNIT_TEST(charBufParseTest);
	CPPUNIT_TEST(fileParseTest);
	CPPUNIT_TEST_SUITE_END();
	
private:
	
	struct Position {
		int x, y, z;
		Position(int _x, int _y, int _z) : x(_x), y(_y), z(_z) {}
		~Position() {}
		bool operator == (Position const& p)
		{ return x==p.x && y==p.y && z==p.z; }
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
	void atomStmtTest(void);
	void multipleAtomStmtTest(void);
	void molLineTest(void);
	void csysLineTest(void);
	void groupLineTest(void);
	void uncheckedParseTest(void);
	void checkedParseTest(void);
	void fileParseTest(void);
	
private:
	
	// scratch variables to hold values extracted by parser
	int intVal, intVal2;
	int x, y, z;
	double doubleVal;
	std::string stringVal, stringVal2;
	int atomId, atomicNum;
	std::string atomStyle;
	char const *charStringWithSpaceStart, *charStringWithSpaceStop;
	char const *lineStart;
	int lineNum;	
	
	// variables used in atom_decl_line tests
	std::vector<int> atomIds, atomicNums;
	std::vector<Position> atomLocs;
	std::vector<std::string> atomStyles;
	std::vector<std::map<std::string, std::string> > atomProps;
	
	// variables used in bond_line tests
	std::vector<std::map<std::string, std::vector<int> > > bonds;
	
	// variables used in bond_direction tests
	int bondDirectionStartId, bondDirectionStopId;
	
	// variables used in mol_decl_line tests
	std::string currentMolName, currentMolStyle;
	
	// variables used in csys_line tests
	std::string csysViewName;
	double csysQw, csysQx, csysQy, csysQz;
	double csysScale, csysZoomFactor;
	double csysPovX, csysPovY, csysPovZ;
	
	// variables used in group tests
	std::vector<std::string> groupNameStack;
	std::string currentGroupName, currentGroupStyle;
	
	double kelvinTemp;
	int atomCount, molCount, groupCount, egroupCount;
	int infoAtomCount, infoChunkCount, infoOpenGroupCount;
	int bond1Count, bond2Count, bond3Count, bondaCount, bondcCount, bondgCount;
	
	// -- helper members --
	
	void reset(void);
	void syntaxError(std::string const& errorMessage);
	
	void atomLineTestSetUp(std::vector<std::string>& testStrings,
	                       std::vector<AtomTestInfo>& answers);
	void atomLineTestHelper(char const *const testInput);
	
	void bondLineTestHelper(char const *const testInput);
	void bondDirectionTestHelper(char const *const testInput);
	void infoAtomTestHelper(char const *const testInput);
	void atomStmtTestHelper(char const *const testInput);
	void multipleAtomStmtTestHelper(char const *const testInput);
	void molLineTestHelper(char const *const testInput);
	void csysLineTestHelper(char const *const testInput);
	void cppunit_assert_csys(std::string const& name,
	                         double const& qw, double const& qx,
	                         double const& qy, double const& qz,
	                         double const& scale,
	                         double const& povX, double const& povY,
	                         double const& povZ, double const& zoomFactor);
	void groupLineTestHelper(char const *const testInput);
	void uncheckedParseTestHelper(char const *const testInput);
	void checkedParseTestHelper(char const *const testInput);
	
	void charBufParseTest(void);
	void charBufParseTestVanillin(void);
	void charBufParseTestHelper(char const *const testInput);
	
	void fileParseTestH2O(void);
	void fileParseTestHOOH(void);
	void fileParseTestChlorophyll(void);
	void fileParseTestVanillin(void);
	void fileParseTestNanocar(void);
	void fileParseTestHelper(RagelIstreamPtr& p, RagelIstreamPtr& pe);
	
	void newAtom(int atomId, int atomicNum,
	             int x, int y, int z,
	             std::string const& atomStyle);
	void newAtomInfo(std::string const& key, std::string const& value);
	
	void newBond(std::string const& bondType, int targetAtomId);
	void newBondDirection(int atomId1, int atomId2);
	
	void newMolecule(std::string const& name, std::string const& style);
	void newChunkInfo(std::string const& key, std::string const& value);
	
	void newViewDataGroup(void);
	void newNamedView(std::string const& name,
	                  double const& qw, double const& qx, double const& qy, double const& qz,
	                  double const& scale,
	                  double const& povX, double const& povY, double const& povZ,
	                  double const& zoomFactor);
	void newMolStructGroup(std::string const& name,
	                       std::string const& classification);
	void newClipboardGroup(void);
	void endGroup(std::string const& name);
	void newOpenGroupInfo(std::string const& key, std::string const& value);
	
	void end1(void);
	
	void checkCounts(int atomCountRef, int molCountRef,
	                 int groupCountRef, int egroupCountRef,
	                 int bond1CountRef, int bond2CountRef, int bond3CountRef,
	                 int bondaCountRef, int bondcCountRef, int bondgCountRef,
	                 int infoAtomCountRef, int infoChunkCountRef,
	                 int infoOpenGroupCountRef);
	
	
	// void endViewDataGroup(void);
	// void endMolStructGroup(std::string const& name);
	// void endClipboardGroup(void);
	
#if 0
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
#endif
	
};

#endif // NANOREXMMPIMPORTEXPORTRAGELTEST_H
