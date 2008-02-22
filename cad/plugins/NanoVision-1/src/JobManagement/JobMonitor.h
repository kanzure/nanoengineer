// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef JOBMONITOR_H
#define JOBMONITOR_H

#include <QThread>

#include <string>
using namespace std;


/* CLASS: JobMonitor */
class JobMonitor : public QThread {

	Q_OBJECT
	
	public:
		JobMonitor(const string& initString);
		virtual ~JobMonitor();
		
	signals:
		void startedMonitoring(const string& id, const string& title);
		void jobFinished(const string& id);
		void jobAborted(const string& id);
	
	public slots:
		virtual void abortJob() = 0;
		
	protected:
		string initString;
};

#endif
