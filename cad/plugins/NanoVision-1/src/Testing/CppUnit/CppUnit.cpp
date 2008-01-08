// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <iostream>

//#include <QCoreApplication>

#include <cppunit/BriefTestProgressListener.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/TestResult.h>
#include <cppunit/TestResultCollector.h>
#include <cppunit/TestRunner.h>


/*
 * Usage: CppUnit <suite_name>
 */
int main(int argc, char* argv[]) {

	/*
	QCoreApplication app(argc, argv);
	qDebug("Hello from Qt 4!");
	*/
	
	// Create the event manager and test controller
	CPPUNIT_NS::TestResult controller;

	// Add a listener that collects test results
	CPPUNIT_NS::TestResultCollector result;
	controller.addListener(&result);        

	// Add a listener that prints dots as tests run
	CPPUNIT_NS::BriefTestProgressListener progress;
	controller.addListener(&progress);      

	// Add the top suite to the test runner
	CPPUNIT_NS::TestRunner runner;
	std::string suiteName;
	if (argc == 1)
		suiteName = "All Tests";
	else
		suiteName = argv[1];
	runner.addTest
		(CPPUNIT_NS::TestFactoryRegistry::getRegistry(suiteName).makeTest());
	runner.run(controller);

	// Print test in a compiler compatible format.
	CPPUNIT_NS::CompilerOutputter outputter( &result, std::cerr );
	outputter.write(); 

	return result.wasSuccessful() ? 0 : 1;
}
