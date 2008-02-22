// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "GROMACS_JobMonitor.h"


/* CONSTRUCTOR */
GROMACS_JobMonitor::GROMACS_JobMonitor(const string& initString)
		: JobMonitor(initString) {
}


/* DESTRUCTOR */
GROMACS_JobMonitor::~GROMACS_JobMonitor() {
}


/* FUNCTION: run */
void GROMACS_JobMonitor::run() {
	
	string title = string("GROMACS process ") + initString;
	emit startedMonitoring(initString, title);
	
	monitor = true;
	while (monitor) {
		printf("%s ", initString);
		sleep(1);
	}
	
	emit jobAborted(initString);
}


/* FUNCTION: abortJob */
void GROMACS_JobMonitor::abortJob() {
	monitor = false;
}


