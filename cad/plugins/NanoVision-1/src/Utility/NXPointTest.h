// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_POINTTEST_H
#define NX_POINTTEST_H

#include <cppunit/extensions/HelperMacros.h>

#include "Nanorex/Utility/NXPoint.h"

using namespace Nanorex;

class NXPointTest : public CPPUNIT_NS::TestFixture {
    
    CPPUNIT_TEST_SUITE(NXPointTest);
    CPPUNIT_TEST(accessTest);
    CPPUNIT_TEST(dataTest);
    CPPUNIT_TEST(sizeTest);
    CPPUNIT_TEST(zeroTest);
    CPPUNIT_TEST(incrementTest);
    CPPUNIT_TEST(decrementTest);
    CPPUNIT_TEST(scalingTest);
    CPPUNIT_TEST(invScalingTest);
    CPPUNIT_TEST(dotTest);
    CPPUNIT_TEST(squared_normTest);
    CPPUNIT_TEST(normTest);
    CPPUNIT_TEST(normalizeSelfTest);
    CPPUNIT_TEST(normalizedTest);
    CPPUNIT_TEST(crossTest);
    CPPUNIT_TEST_SUITE_END();
    
public:
    void setUp(void) {}
    void tearDown(void) {}
    
    void accessTest(void);
    void dataTest(void);
    void sizeTest(void);
    void zeroTest(void);
    void incrementTest(void);
    void decrementTest(void);
    void scalingTest(void);
    void invScalingTest(void);
    void dotTest(void);
    void squared_normTest(void);
    void normTest(void);
    void normalizeSelfTest(void);
    void normalizedTest(void);
    void crossTest(void);
};

#endif // NX_POINTTEST_H
