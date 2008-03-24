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
	bool emittedJobAborted = false;
	bool monitorError = false;
	bool stillRunning = true;
	QString pid = initString;
	while (stillRunning && /*!_aborted &&*/ !monitorError) {
		sleep(1);
		
		CheckJobActive(pid, stillRunning, monitorError);
		
		jobControlMutex.lock();
		_aborted = aborted;
		jobControlMutex.unlock();
	}
	
	if (_aborted && !emittedJobAborted) {
		debugMessage = tr("Emitting jobAborted(%1)").arg(initString);
		NXLOG_DEBUG("GROMACS_JobMonitor", qPrintable(debugMessage));
		emit jobAborted(initString);
		emittedJobAborted = true;
		
	} else if (monitorError) {
		;// TODO: handle this
		
	} else {
		debugMessage = tr("Emitting jobFinished(%1)").arg(initString);
		NXLOG_DEBUG("GROMACS_JobMonitor", qPrintable(debugMessage));
		emit jobFinished(initString);
	}
}


/* FUNCTION: CheckJobActive */
void GROMACS_JobMonitor::CheckJobActive(const QString& pid, bool& stillRunning,
										bool& monitorError) {
	monitorError = false;
#if defined(WIN32)
	QString command =
		QString("%1/ps %2")
			.arg(QCoreApplication::applicationDirPath()).arg(pid);
#else
	QString command = QString("ps %1").arg(pid);
#endif
	FILE* commandPipe;

	commandPipe = popen(qPrintable(command), "r");
	if (commandPipe == 0) {
		QString logMessage = tr("Command failed: %1").arg(command);
		NXLOG_SEVERE("GROMACS_JobMonitor::CheckJobActive",
					 qPrintable(logMessage));
		monitorError = true;
		return; // Abort function
	}

	stillRunning = false;
	static int bufferSize = 64;
	char buffer[bufferSize];
printf("%s output:\n", qPrintable(command));
	while (fgets(buffer, bufferSize, commandPipe) != 0) {
printf("\t%s\n", buffer);
		string bufferString = buffer;
		
		// Remove spaces from beginning of line
		while ((bufferString.length() > 0) && (bufferString[0] == ' '))
			bufferString = bufferString.substr(1);
		
		if (bufferString.compare(0, pid.length(), qPrintable(pid)) == 0)
			stillRunning = true;
	}

	int status = pclose(commandPipe);
	if (status == -1)
		NXLOG_DEBUG("GROMACS_JobMonitor::run", "close pipe failed");
}


/* FUNCTION: abortJob */
#if defined(WIN32)
#include "windows.h"
#endif

void GROMACS_JobMonitor::abortJob() {
	QMutexLocker locker(&jobControlMutex);
	
#if defined(WIN32)
	WCHAR mutexName[32];
	swprintf(mutexName, L"GMX_SIGTERM_Signal%d", initString.toInt());
wprintf(L">>> mutexName=%s\n", mutexName);

	HANDLE mutex = NULL;
	mutex =
    	CreateMutex( 
        	NULL,				// default security attributes
			FALSE,				// initially not owned
			mutexName);			// mutex name

	if (mutex != NULL) {
printf(">>> mutex created, not owned\n");
		// Once we can't lock the mutex it means that the GMX process has locked
		// it and has thereby acknowledged its existence and the SIGTERM signal.
		bool mutexLocked = false;
		while (!mutexLocked) {
			DWORD result =
				WaitForSingleObject( 
					mutex,		// handle to mutex
					0);			// don't wait, just test
					
			if (result == WAIT_OBJECT_0) {
printf(">>> Got mutex\n"); fflush(0);
				ReleaseMutex(mutex);
				
			} else {
printf(">>> mutex locked - GMX acks\n");fflush(0);
				aborted = true;
				mutexLocked = true;
			}
			sleep(1);
		}
		CloseHandle(mutex);
		
	} else {
printf(">>> couldn't create mutex\n");
	}
#else
	QString command = QString("kill -15 %1").arg(initString);
	int status = system(qPrintable(command));
	if (status == 0)
		aborted = true;
#endif
}


