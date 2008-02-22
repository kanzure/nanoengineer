// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef GROMACS_JOBMONITOR_H
#define GROMACS_JOBMONITOR_H

#include <QObject>

#include <string>
using namespace std;

#include "JobMonitor.h"


/* CLASS: GROMACS_JobMonitor */
class GROMACS_JobMonitor : public JobMonitor {

	Q_OBJECT

	public:
		GROMACS_JobMonitor(const string& initString);
		~GROMACS_JobMonitor();
		
		void run();
		
	signals:
		void startedMonitoring(const string& id, const string& title);
		void jobFinished(const string& id);
		void jobAborted(const string& id);
	
	public slots:
		void abortJob();
		
	private:
		bool monitor;
};

#endif
