// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "GROMACS_JobMonitor.h"


/* CONSTRUCTOR */
GROMACS_JobMonitor::GROMACS_JobMonitor(const QString& initString)
		: JobMonitor(initString) {
}


/* DESTRUCTOR */
GROMACS_JobMonitor::~GROMACS_JobMonitor() {
}


/* FUNCTION: run
 *
 * Note: initString is the GROMACS process id (pid.)
 */
void GROMACS_JobMonitor::run() {
	
	QString title = tr("GROMACS process %1").arg(initString);
	QString debugMessage =
		tr("Emitting startedMonitoring(GMX, %1, %2)").arg(initString).arg(title);
	NXLOG_DEBUG("GROMACS_JobMonitor", qPrintable(debugMessage));
	emit startedMonitoring("GMX", initString, title);
	
	bool _aborted = aborted = false;
	bool monitorError = false;
	bool stillRunning = true;
	int status;
	static int bufferSize = 64;
	char buffer[bufferSize];
	QString pid = initString;
	QString command = QString("ps -A | grep %1").arg(pid);
	FILE* commandPipe;
	while (stillRunning && !_aborted && !monitorError) {
		commandPipe = popen(qPrintable(command), "r");
		if (commandPipe == 0) {
			QString logMessage = tr("Command failed: %1").arg(command);
			NXLOG_SEVERE("GROMACS_JobMonitor::run", qPrintable(logMessage));
			monitorError = true;
			continue;
		}

		stillRunning = false;
		while (fgets(buffer, bufferSize, commandPipe) != 0) {
			string bufferString = buffer;
			while ((bufferString.length() > 0) && (bufferString[0] == ' '))
				bufferString = bufferString.substr(1);
			if (bufferString.compare(0, pid.length(), qPrintable(pid)) == 0)
				stillRunning = true;
		}

		status = pclose(commandPipe);
		if (status == -1)
			NXLOG_DEBUG("GROMACS_JobMonitor::run", "close pipe failed");
		
		if (stillRunning) {
			sleep(1);
			jobControlMutex.lock();
			_aborted = aborted;
			jobControlMutex.unlock();
		}
	}
	
	if (_aborted) {
		debugMessage = tr("Emitting jobAborted(%1)").arg(initString);
		NXLOG_DEBUG("GROMACS_JobMonitor", qPrintable(debugMessage));
		emit jobAborted(initString);
		
	} else if (monitorError) {
		;// TODO: handle this
		
	} else {
		debugMessage = tr("Emitting jobFinished(%1)").arg(initString);
		NXLOG_DEBUG("GROMACS_JobMonitor", qPrintable(debugMessage));
		emit jobFinished(initString);
	}
}


/* FUNCTION: CheckJobActive */
bool GROMACS_JobMonitor::CheckJobActive(const QString& pid) {
	// TODO: Implement
	return true;
}


/* FUNCTION: abortJob */
void GROMACS_JobMonitor::abortJob() {
	QMutexLocker locker(&jobControlMutex);
	
	QString command = QString("kill -15 %1").arg(initString);
	int status = system(qPrintable(command));
	if (status == 0)
		aborted = true;
}


