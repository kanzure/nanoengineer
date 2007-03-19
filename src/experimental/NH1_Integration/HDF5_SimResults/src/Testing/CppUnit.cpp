/*
NanoHive-1 Nanosystems Simulator
Copyright (c) 2006 Nanorex, Inc.  All rights reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

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
