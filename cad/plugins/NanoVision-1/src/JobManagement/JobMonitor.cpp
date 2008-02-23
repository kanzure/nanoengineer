
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "JobMonitor.h"


/* CONSTRUCTOR */
JobMonitor::JobMonitor(const QString& initString) : QThread() {
	this->initString = initString;
}


/* DESTRUCTOR */
JobMonitor::~JobMonitor() {
}

