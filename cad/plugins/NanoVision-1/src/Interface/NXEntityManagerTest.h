// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGERTEST_H
#define NX_ENTITYMANAGERTEST_H

#include <string>

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Interface/NXEntityManager.h"

using namespace Nanorex;
using namespace OpenBabel;


/* CLASS: NXEntityManagerTest */
class NXEntityManagerTest : public CPPUNIT_NS::TestFixture {

	CPPUNIT_TEST_SUITE(NXEntityManagerTest);
	CPPUNIT_TEST(moleculeSetTraversalTest);
	CPPUNIT_TEST(moleculeTraversalTest);
	//CPPUNIT_TEST(atomTraversalTest1);
	CPPUNIT_TEST(atomTraversalTest2);
	CPPUNIT_TEST_SUITE_END();

	public:
		void setUp();
		void tearDown();

		void moleculeSetTraversalTest();
		void moleculeTraversalTest();
		//void atomTraversalTest1();
		void atomTraversalTest2();

	private:
		NXEntityManager* entityManager;
		
		//std::string atomTraversalTest1Helper(NXMoleculeSet* moleculeSet);
};

#endif
