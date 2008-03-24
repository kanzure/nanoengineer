// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef GROMACS_JOBMONITOR_H
#define GROMACS_JOBMONITOR_H

#include <string>
using namespace std;

#include <QObject>
#include <QString>
#include <QCoreApplication>

#include "Nanorex/Utility/NXLogger.h"
using namespace Nanorex;

#include "JobMonitor.h"


/* CLASS: GROMACS_JobMonitor */
class GROMACS_JobMonitor : public JobMonitor {

	Q_OBJECT

	public:
		GROMACS_JobMonitor(const QString& initString);
		~GROMACS_JobMonitor();
		
		void run();
		static void CheckJobActive(const QString& pid, bool& stillRunning,
								   bool& monitorError);
		
	signals:
		void startedMonitoring(const QString& processType, const QString id,
							   const QString title);
		void jobFinished(const QString& id);
		void jobAborted(const QString& id);
	
	public slots:
		void abortJob();
		
	private:
		bool aborted;
		QMutex jobControlMutex;
};

#endif
