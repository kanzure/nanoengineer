// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXStringTokenizerTest.h"


CPPUNIT_TEST_SUITE_REGISTRATION(NXStringTokenizerTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXStringTokenizerTest, "NXStringTokenizerTestSuite");

/* FUNCTION: setUp */
void NXStringTokenizerTest::setUp() {
}


/* FUNCTION: tearDown */
void NXStringTokenizerTest::tearDown() {
}


/* FUNCTION: tokenization */
void NXStringTokenizerTest::tokenization() {
	std::string inString = "a,b,c";
	Nanorex::NXStringTokenizer tokenizer(inString, ",");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "a");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "b");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "c");
	CPPUNIT_ASSERT(!tokenizer.hasMoreTokens());

	inString = ",a;b,c;";
	tokenizer = Nanorex::NXStringTokenizer(inString, ",;");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "a");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "b");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "c");
	CPPUNIT_ASSERT(!tokenizer.hasMoreTokens());

	inString = ",,a;b;;";
	tokenizer = Nanorex::NXStringTokenizer(inString, ",;");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "a");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "b");
	CPPUNIT_ASSERT(tokenizer.getNextToken() == "");
	CPPUNIT_ASSERT(!tokenizer.hasMoreTokens());
}
