// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <cassert>
#include "NXSceneGraphTest.h"

using namespace std;
using namespace Nanorex;

CPPUNIT_TEST_SUITE_REGISTRATION(NXSceneGraphTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXSceneGraphTest,
                                      "NXSceneGraphTestSuite");

// -- static data --
int NXSGApplyTesterNode::numApplications(0);
// int NXSGDeleteTesterNode::numDeletes(0);


// -- member functions --

#if 0
void NXSGDeleteTesterNode::deleteRecursive(void)
{
    {
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            childIter != children.end();
            ++childIter)
        {
            NXSGNode *const childPtr = *childIter;
            if(childPtr->decrementRefCount() == 0) {
                childPtr->deleteRecursive();
                ++numDeletes;
            }
        }
        children.clear();
    }
}
#endif


void NXSceneGraphTest::setUp(void)
{
#ifdef NX_DEBUG
	// NXSGNode::ResetIdSource();
#endif
    for(int i=0; i<6; ++i)
        nodes[i] = new NXSGApplyTesterNode;
    nodes[6] = new NXSGApplyBlockerNode;
}

void NXSceneGraphTest::tearDown(void)
{
//     reset();
//     for(int i=0; i<7; ++i) {
//         if(nodes[i] != NULL) {
//             delete nodes[i];
//             nodes[i] = NULL;
//         }
//     }
}

#if 0
void NXSceneGraphTest::reset(void)
{
    for(int i=0; i<7; ++i)
        nodes[i]->reset();
}
#endif

void NXSceneGraphTest::makeTree(NXSGNode* nodes[7])
{
    nodes[0]->addChild(nodes[1]);
    nodes[0]->addChild(nodes[2]);
    nodes[1]->addChild(nodes[3]);
    nodes[1]->addChild(nodes[4]);
    nodes[2]->addChild(nodes[5]);
    nodes[2]->addChild(nodes[6]);
    nodes[0]->addChild(nodes[3]);
    nodes[0]->addChild(nodes[6]);
}

void NXSceneGraphTest::makeInvertedTree(NXSGNode* nodes[7])
{
    nodes[1]->addChild(nodes[0]);
    nodes[2]->addChild(nodes[0]);
    nodes[3]->addChild(nodes[1]);
    nodes[4]->addChild(nodes[1]);
    nodes[5]->addChild(nodes[2]);
    nodes[6]->addChild(nodes[2]);
    nodes[3]->addChild(nodes[0]);
    nodes[6]->addChild(nodes[0]);
}

void NXSceneGraphTest::refCountTest1(void)
{
    // don't know if CppUnit will run this test first
    // re-setup to test initialization
    //tearDown();
    //setUp();
    
    // initially, all nodes should have zero count
    bool initial_zero_refcount = true;
    for(int i=0; i<7; ++i)
        initial_zero_refcount = (initial_zero_refcount &&
                                 (nodes[i]->getRefCount() == 0));
    CPPUNIT_ASSERT(initial_zero_refcount);
    
    nodes[0]->incrementRefCount();
    CPPUNIT_ASSERT(nodes[0]->getRefCount()==1);
    nodes[0]->incrementRefCount();
    CPPUNIT_ASSERT(nodes[0]->getRefCount()==2);
    nodes[0]->decrementRefCount();
    nodes[0]->decrementRefCount();
    CPPUNIT_ASSERT(nodes[0]->getRefCount()==0);
	// CPPUNIT_ASSERT(nodes[1]->decrementRefCount()==0);
    
	for(int i=0; i<7; ++i)
		delete nodes[i];
}

void NXSceneGraphTest::refCountTest2(void)
{
	// reset();
    makeInvertedTree(nodes);
    CPPUNIT_ASSERT(nodes[0]->getRefCount()==4);
    CPPUNIT_ASSERT(nodes[0]->getNumChildren()==0);
    CPPUNIT_ASSERT(nodes[3]->getNumChildren()==2);
    CPPUNIT_ASSERT(nodes[6]->getNumChildren()==2);
    CPPUNIT_ASSERT(nodes[1]->getNumChildren()==1);
    CPPUNIT_ASSERT(nodes[4]->getNumChildren()==1);
	delete nodes[3];
	delete nodes[4];
	delete nodes[5];
	delete nodes[6];
}

void NXSceneGraphTest::childManipTest(void)
{
	// reset();
    // Form the tree
    nodes[0]->addChild(nodes[1]);
    nodes[0]->addChild(nodes[2]);
    CPPUNIT_ASSERT(nodes[0]->getNumChildren()==2);
	CPPUNIT_ASSERT(nodes[1]->getRefCount()==1);
	CPPUNIT_ASSERT(nodes[2]->getRefCount()==1);
	
    nodes[1]->addChild(nodes[3]);
    nodes[1]->addChild(nodes[4]);
    CPPUNIT_ASSERT(nodes[1]->getNumChildren()==2);
	CPPUNIT_ASSERT(nodes[3]->getRefCount()==1);
	CPPUNIT_ASSERT(nodes[4]->getRefCount()==1);
	
    nodes[2]->addChild(nodes[5]);
    nodes[2]->addChild(nodes[6]);
    CPPUNIT_ASSERT(nodes[2]->getNumChildren()==2);
	CPPUNIT_ASSERT(nodes[5]->getRefCount()==1);
	CPPUNIT_ASSERT(nodes[6]->getRefCount()==1);
	
    CPPUNIT_ASSERT(nodes[0]->getRefCount()==0);
    for(int i=1; i<7; ++i)
        CPPUNIT_ASSERT(nodes[i]->getRefCount()==1);
    
    nodes[0]->addChild(nodes[3]);
    nodes[0]->addChild(nodes[6]);
    CPPUNIT_ASSERT(nodes[3]->getRefCount()==2);
    CPPUNIT_ASSERT(nodes[6]->getRefCount()==2);
    CPPUNIT_ASSERT(nodes[0]->getNumChildren()==4);
	
	// removeChild tests
	bool removedNode6FromNode0 = nodes[0]->removeChild(nodes[6]);
	CPPUNIT_ASSERT(removedNode6FromNode0);
	CPPUNIT_ASSERT(nodes[0]->getNumChildren()==3);
	CPPUNIT_ASSERT(nodes[6]->getRefCount()==1);
	
	// invalid child-removal should be trapped
	bool removedNode5FromNode0 = nodes[0]->removeChild(nodes[5]);
	CPPUNIT_ASSERT(!removedNode5FromNode0);
	
	delete nodes[0];
}

void NXSceneGraphTest::applyTest1(void)
{
    // static count variable should initially be zero
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==0);
    bool ok;
    // first test NXSGApplyTesterNode
    NXSGApplyTesterNode *applyTesterNode = new NXSGApplyTesterNode;
    ok = applyTesterNode->apply();
    assert(NXSGApplyTesterNode::GetNumApplications()==1);
    ok = applyTesterNode->applyRecursive();
    assert(NXSGApplyTesterNode::GetNumApplications()==2);
    NXSGApplyTesterNode::ResetNumApplications();
    delete applyTesterNode;
    
	// reset();
    makeTree(nodes);
    ok = nodes[0]->applyRecursive();
    // because nodes[6] is a blocker, ok == false and 6 applications
    CPPUNIT_ASSERT(!ok);
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==6);
    
	CPPUNIT_ASSERT(nodes[0]->removeChild(nodes[3]));
	CPPUNIT_ASSERT(nodes[0]->removeChild(nodes[6]));
    NXSGApplyTesterNode *lastNode = new NXSGApplyTesterNode;
	NXSGNode node6Guard;
	node6Guard.addChild(nodes[6]); // prevents deletion due to next line
	CPPUNIT_ASSERT(nodes[2]->removeChild(nodes[6]));
	CPPUNIT_ASSERT(nodes[6]->getRefCount()==1);
	CPPUNIT_ASSERT(nodes[2]->addChild(lastNode));
    // does apply recursive work?
    NXSGApplyTesterNode::ResetNumApplications();
    assert(NXSGApplyTesterNode::GetNumApplications()==0);
    ok = nodes[0]->applyRecursive();
    CPPUNIT_ASSERT(ok);
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==7);
    
    // add more edges
    NXSGApplyTesterNode::ResetNumApplications();
    nodes[0]->addChild(nodes[3]);
    nodes[0]->addChild(lastNode);
    ok = nodes[0]->applyRecursive();
    CPPUNIT_ASSERT(ok);
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==9);
	
	// restore state before surgery performed to include lastNode before deleting it
	CPPUNIT_ASSERT(lastNode->getRefCount()==2);
	CPPUNIT_ASSERT(nodes[2]->removeChild(lastNode));
	CPPUNIT_ASSERT(nodes[2]->addChild(nodes[6]));
	CPPUNIT_ASSERT(node6Guard.removeChild(nodes[6]));
	CPPUNIT_ASSERT(nodes[0]->removeChild(lastNode));
	// this deletes lastNode because reference-count would have become zero
	
	delete nodes[0];
}

void NXSceneGraphTest::applyTest2(void)
{
    // test with inverted tree
	// reset();
    makeInvertedTree(nodes);
    NXSGApplyTesterNode::ResetNumApplications();
    assert(NXSGApplyTesterNode::GetNumApplications()==0);
    bool ok = nodes[3]->applyRecursive();
    CPPUNIT_ASSERT(ok);
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==4);
    
    NXSGApplyTesterNode::ResetNumApplications();
    assert(NXSGApplyTesterNode::GetNumApplications()==0);
    // top level blocks so no apply() should get called
    ok = nodes[6]->applyRecursive();
    CPPUNIT_ASSERT(!ok);
    CPPUNIT_ASSERT(NXSGApplyTesterNode::GetNumApplications()==0);
	
	delete nodes[3];
	delete nodes[4];
	delete nodes[5];
	delete nodes[6];
}

#if 0
void NXSceneGraphTest::deleteRecursiveTest(void)
{
    // build custom tree with delete-test nodes
    NXSGNode *_nodes[7];
    for(int i=0; i<7; ++i)
        _nodes[i] = new NXSGDeleteTesterNode;
    makeTree(_nodes);
    // static delete-counter variable should initially be zero
    CPPUNIT_ASSERT(NXSGDeleteTesterNode::GetNumDeletes()==0);
    _nodes[0]->deleteRecursive();
    // _nodes[0] shouldn't be 'deleted', only its children
    CPPUNIT_ASSERT(NXSGDeleteTesterNode::GetNumDeletes()==6);
    // all _nodes should have zero ref-count from 'deletion'
    for(int i=0; i<7; ++i) {
        CPPUNIT_ASSERT(_nodes[i]->getRefCount() == 0);
        delete _nodes[i];
    }
}
#endif


void NXSceneGraphTest::isLeafTest(void)
{
	// reset();
    makeTree(nodes);
    for(int i=0; i<3; ++i)
        CPPUNIT_ASSERT(!nodes[i]->isLeaf());
    for(int i=3; i<7; ++i)
        CPPUNIT_ASSERT(nodes[i]->isLeaf());
	delete nodes[0];
}
