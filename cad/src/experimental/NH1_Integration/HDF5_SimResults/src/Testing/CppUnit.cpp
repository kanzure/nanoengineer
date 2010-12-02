
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#pragma warning(disable:4786)
#include <iostream>

#include <cppunit/BriefTestProgressListener.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/TestResult.h>
#include <cppunit/TestResultCollector.h>
#include <cppunit/TestRunner.h>


/*
 * Usage: CppUnit <TestSuitName>
 * Running CppUnit by itself will run all the test suites. Passing the name
 * of a test suite as an argument will only run that test suite.
 */
int main(int argc, char* argv[]) {
	
	// Check that we're being run from the correct directory
	FILE* handle = fopen("Testing/bad-hdf5-file/sim_results.h5", "r");
	if (handle == 0) {
 	   printf("\n\nERROR: Run CppUnit from the HDF5_SimResults/src/ directory.\n");
	   exit(1);
	}
	fclose(handle);
	
	// Delete any existing sim_results.h5 file
	remove("Testing/sim_results.h5");


	// Create the event manager and test controller
	CPPUNIT_NS::TestResult controller;

	// Add a listener that colllects test result
	CPPUNIT_NS::TestResultCollector result;
	controller.addListener( &result );        

	// Add a listener that print dots as test run.
	CPPUNIT_NS::BriefTestProgressListener progress;
	controller.addListener( &progress );      

	// Add the top suite to the test runner
	CPPUNIT_NS::TestRunner runner;
	std::string suiteName;
	if (argc == 1)
		suiteName = "All Tests";
	else
		suiteName = argv[1];
	runner.addTest( CPPUNIT_NS::TestFactoryRegistry::getRegistry(suiteName).makeTest() );
	runner.run( controller );

	// Print test in a compiler compatible format.
	CPPUNIT_NS::CompilerOutputter outputter( &result, std::cerr );
	outputter.write(); 

	return result.wasSuccessful() ? 0 : 1;
}
