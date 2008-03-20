// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXEntityManagerTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(NXEntityManagerTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXEntityManagerTest,
                                      "NXEntityManagerTestSuite");


/* FUNCTION: setUp */
void NXEntityManagerTest::setUp() {
	entityManager = new NXEntityManager();
}


/* FUNCTION: tearDown */
void NXEntityManagerTest::tearDown() {
	delete entityManager;
}


/* FUNCTION: moleculeSetTraversalTest
 *
 * Tests the creation and (depth-first) traversal of the following molecule set
 * tree:
 *
 * root
 *   |-- child        iter1
 *   |-- child        iter1
 *         |-- child  iter2
 *         |-- child  iter2
 */
void NXEntityManagerTest::moleculeSetTraversalTest() {
	
	// Get the root molecule set
	int frameSetId = entityManager->addFrameSet();
	int frameIndex = entityManager->addFrame(frameSetId);
	NXMoleculeSet* rootMoleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	CPPUNIT_ASSERT(rootMoleculeSet != 0);
	CPPUNIT_ASSERT(rootMoleculeSet->childCount() == 0);
	
	// Add children to the root molecule set
	//
	rootMoleculeSet->addChild(new NXMoleculeSet());
	CPPUNIT_ASSERT(rootMoleculeSet->childCount() == 1);
	
	NXMoleculeSet* child = new NXMoleculeSet();
	rootMoleculeSet->addChild(child);
	child->addChild(new NXMoleculeSet());
	child->addChild(new NXMoleculeSet());
	CPPUNIT_ASSERT(child->childCount() == 2);

	// Iterate over the children
	NXMoleculeSetIterator iter1 = rootMoleculeSet->childrenBegin();
	CPPUNIT_ASSERT(iter1 != rootMoleculeSet->childrenEnd());
	iter1++;
	CPPUNIT_ASSERT(iter1 != rootMoleculeSet->childrenEnd());
	NXMoleculeSetIterator iter2 = (*iter1)->childrenBegin();
	CPPUNIT_ASSERT(iter2 != (*iter1)->childrenEnd());
	iter2++;
	CPPUNIT_ASSERT(iter2 != (*iter1)->childrenEnd());
	iter2++;
	CPPUNIT_ASSERT(iter2 == (*iter1)->childrenEnd());
	iter1++;
	CPPUNIT_ASSERT(iter1 == rootMoleculeSet->childrenEnd());
}


/* FUNCTION: moleculeTraversalTest
 *
 * Tests the creation and (depth-first) traversal of the molecules in the
 * following molecule set tree:
 *
 * root (2 molecules)
 *   |-- child
 *   |-- childMoleculeSet1 (2 molecules)
 *         |-- childMoleculeSet2 (2 molecules)
 *         |-- child
 */
void NXEntityManagerTest::moleculeTraversalTest() {

	// Create a tree of molecules in molecule sets
	//
	int frameSetId = entityManager->addFrameSet();
	int frameIndex = entityManager->addFrame(frameSetId);
	NXMoleculeSet* rootMoleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	OBMol* molecule = rootMoleculeSet->newMolecule();
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    (molecule->GetData(NXMoleculeDataType)))->GetIdx() == 0);
	rootMoleculeSet->newMolecule();
	
	rootMoleculeSet->addChild(new NXMoleculeSet());
	NXMoleculeSet* childMoleculeSet1 = new NXMoleculeSet();
	rootMoleculeSet->addChild(childMoleculeSet1);
	molecule = childMoleculeSet1->newMolecule();
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    (molecule->GetData(NXMoleculeDataType)))->GetIdx() == 2);
	childMoleculeSet1->newMolecule();
	
	NXMoleculeSet* childMoleculeSet2 = new NXMoleculeSet();
	childMoleculeSet1->addChild(childMoleculeSet2);
	molecule = childMoleculeSet2->newMolecule();
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    (molecule->GetData(NXMoleculeDataType)))->GetIdx() == 4);
	childMoleculeSet2->newMolecule();	
	
	childMoleculeSet1->addChild(new NXMoleculeSet());
	
	// Traverse all the molecules starting at the root molecule set
	//
	// root
	OBMolIterator iter1 = rootMoleculeSet->moleculesBegin();
	CPPUNIT_ASSERT(iter1 != rootMoleculeSet->moleculesEnd());
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 0);
	iter1++;
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 1);
	iter1++;
	CPPUNIT_ASSERT(iter1 == rootMoleculeSet->moleculesEnd());
	
	NXMoleculeSetIterator moleculeSetIter1 = rootMoleculeSet->childrenBegin();
	iter1 = (*moleculeSetIter1)->moleculesBegin();
	CPPUNIT_ASSERT(iter1 == (*moleculeSetIter1)->moleculesEnd());
	
	// childMoleculeSet1
	moleculeSetIter1++;
	iter1 = (*moleculeSetIter1)->moleculesBegin();
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 2);
	iter1++;
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 3);
	iter1++;
	CPPUNIT_ASSERT(iter1 == (*moleculeSetIter1)->moleculesEnd());
	
	// childMoleculeSet2
	NXMoleculeSetIterator moleculeSetIter2 =
		(*moleculeSetIter1)->childrenBegin();
	iter1 = (*moleculeSetIter2)->moleculesBegin();
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 4);
	iter1++;
	CPPUNIT_ASSERT(((NXMoleculeData*)
				    ((*iter1)->GetData(NXMoleculeDataType)))->GetIdx() == 5);
	iter1++;
	CPPUNIT_ASSERT(iter1 == (*moleculeSetIter2)->moleculesEnd());
	
	moleculeSetIter2++;
	iter1 = (*moleculeSetIter2)->moleculesBegin();
	CPPUNIT_ASSERT(iter1 == (*moleculeSetIter2)->moleculesEnd());	
}


/* FUNCTION: atomTraversalTest1
 *
 * This tests traversal over all atoms in a molecule set for the
 * following molecule set tree:
 *
 * root (2 molecules, 2 atoms each)
 *   |-- child
 *   |-- childMoleculeSet1 (2 molecules, 2 atoms each)
 *         |-- childMoleculeSet2 (2 molecules, 2 atoms each)
 *         |-- child
void NXEntityManagerTest::atomTraversalTest1() {

	// Create a tree of molecules with atoms in molecule sets
	//
	int frameSetId = entityManager->addFrameSet();
	int frameIndex = entityManager->addFrame(frameSetId);
	NXMoleculeSet* rootMoleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	NXMolecule* molecule = rootMoleculeSet->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	molecule = rootMoleculeSet->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	
	rootMoleculeSet->addChild(new NXMoleculeSet());
	NXMoleculeSet* childMoleculeSet1 = new NXMoleculeSet();
	rootMoleculeSet->addChild(childMoleculeSet1);
	molecule = childMoleculeSet1->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	molecule = childMoleculeSet1->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	
	NXMoleculeSet* childMoleculeSet2 = new NXMoleculeSet();
	childMoleculeSet1->addChild(childMoleculeSet2);
	molecule = childMoleculeSet2->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	molecule = childMoleculeSet2->newMolecule();
	molecule->NewAtom();
	molecule->NewAtom();
	
	childMoleculeSet1->addChild(new NXMoleculeSet());
	
	// Traverse all the atoms starting from the root molecule set
	std::string summary = atomTraversalTest1Helper(rootMoleculeSet);
	CPPUNIT_ASSERT(summary == "0.1.2.3.4.5.6.7.8.9.10.11.");
}
 */


/* FUNCTION: atomTraversalTest1Helper 
std::string NXEntityManagerTest::atomTraversalTest1Helper
		(NXMoleculeSet* moleculeSet) {
	std::string summary("");

	// Traverse atoms
	NXAtomIterator atomIter = moleculeSet->BeginAtoms();
	while (atomIter != moleculeSet->EndAtoms()) {
		char buffer[5];
		sprintf(buffer, "%d.", (*atomIter)->GetIdx());
		summary.append(buffer);
		atomIter++;
	}

	// Traverse the molecule set's children
	NXMoleculeSetIterator moleculeSetIter = moleculeSet->childrenBegin();
	while (moleculeSetIter != moleculeSet->childrenEnd()) {
		summary.append(atomTraversalTest1Helper(*moleculeSetIter));
		moleculeSetIter++;
	}
	return summary;
}
*/

/* FUNCTION: atomTraversalTest2
 *
 * This tests traversal over all atoms in a molecule.
 */
void NXEntityManagerTest::atomTraversalTest2() {

	// Create a molecule with atoms
	//
	int frameSetId = entityManager->addFrameSet();
	int frameIndex = entityManager->addFrame(frameSetId);
	NXMoleculeSet* rootMoleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	OBMol* molecule = rootMoleculeSet->newMolecule();
	OBAtom* atom = molecule->NewAtom();
	atom = molecule->NewAtom();
	
	// Traverse the molecule's atoms
	OBAtomIterator iter = molecule->BeginAtoms();
	CPPUNIT_ASSERT((*iter)->GetIdx() == 1);
	iter++;
	CPPUNIT_ASSERT((*iter)->GetIdx() == 2);
	iter++;
	/*
	while (iter != molecule->EndAtoms()) {
		printf("#%d ", (*iter));
		iter++;
	}
	*/
	CPPUNIT_ASSERT(*iter == 0);
}
