// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef JOBMONITOR_H
#define JOBMONITOR_H

#include <QObject>
#include <QThread>
#include <QString>


/* CLASS: JobMonitor */
class JobMonitor : public QThread {

	Q_OBJECT
	
	public:
		JobMonitor(const QString& initString);
		virtual ~JobMonitor();
		
	signals:
		void startedMonitoring(const QString& processType, const QString& id,
							   const QString& title);
		void jobFinished(const QString& id);
		void jobAborted(const QString& id);
	
	public slots:
		virtual void abortJob() = 0;
		
	protected:
		QString initString;
};

#endif
