// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPHTEST_H
#define NX_SCENEGRAPHTEST_H

#include <cppunit/extensions/HelperMacros.h>

// class NXSceneGraphTest;

#include "Nanorex/Interface/NXSceneGraph.h"

// using namespace Nanorex;

namespace Nanorex {

/* CLASS: NXSGApplyTesterNode */
/**
 * Tests the apply() tree by incrementing a global count variable
 */
class NXSGApplyTesterNode : public NXSGNode {
public:
    NXSGApplyTesterNode() {}
    ~NXSGApplyTesterNode() {}
    bool apply(void) const { ++numApplications; return true; }
    static int const& GetNumApplications(void) { return numApplications; }
    static void ResetNumApplications(void) { numApplications = 0; }
private:
    static int numApplications;
};

/* CLASS: NXSGApplyBlockerNode */
/**
 * Its apply() does nothing and always returns false to block the execution
 */
class NXSGApplyBlockerNode : public NXSGNode {
public:
    NXSGApplyBlockerNode() {}
    ~NXSGApplyBlockerNode() {}
    bool apply(void) const { return false; }
};


#if 0
/* CLASS: NXSGDeleteTesterNode */
/**
 * Overrides the deleteRecursive() method to count number of delete-s instead
 * of actually deleting nodes
 */
class NXSGDeleteTesterNode : public NXSGNode {
public:
    NXSGDeleteTesterNode() {}
    ~NXSGDeleteTesterNode() {}
    static int const& GetNumDeletes(void) { return numDeletes; }
    static void ResetNumDeletes(void) { numDeletes = 0; }
    void deleteRecursive(void);
private:
    static int numDeletes;
};
#endif


/* CLASS: NXSceneGraphTest */
/**
 * Tests the scene-graph API
 */
class NXSceneGraphTest: public CPPUNIT_NS::TestFixture {
    
    CPPUNIT_TEST_SUITE(NXSceneGraphTest);
    CPPUNIT_TEST(refCountTest1);
	CPPUNIT_TEST(refCountTest2);
	CPPUNIT_TEST(childManipTest);
    CPPUNIT_TEST(applyTest1);
	CPPUNIT_TEST(applyTest2);
	// CPPUNIT_TEST(deleteRecursiveTest);
    CPPUNIT_TEST(isLeafTest);
    CPPUNIT_TEST_SUITE_END();
    
public:
    void setUp();
    void tearDown();
    
	// void reset();
    static void makeTree(NXSGNode* nodes[7]);
    static void makeInvertedTree(NXSGNode* nodes[7]);
    
    // tests increment, decrement, accessor
    void refCountTest1();
	void refCountTest2();
	void childManipTest();
    void applyTest1();
	void applyTest2();
	// void deleteRecursiveTest();
    void isLeafTest();
    
private:
    NXSGNode *nodes[7];
};

} // namespace Nanorex

#endif // NX_SCENEGRAPHTEST_H
