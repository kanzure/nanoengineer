// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_LOGGER_H
#define NX_LOGGER_H

#include <stdio.h>

#include <list>
#include <string>

#include <QMutex>
#include <QDateTime>
//#include <QMutexLocker>

namespace Nanorex {

typedef enum NXLogLevel {
	NXLogLevel_Debug,	// General debugging.
	NXLogLevel_Config,	// Debugging configurations (graphics depth, os, etc.)
	NXLogLevel_Info,	// Information interesting to the user.
	NXLogLevel_Warning,	// Important things the user should know.
	NXLogLevel_Severe	// Things that should stop the user before continuing.
};

static char LogLevelNames[][8] = {
	"DEBUG", "CONFIG", "INFO", "WARNING", "SEVERE"
};


/* CLASS: LogRecord */
/**
 * Used internally by NXLogHandler and NXLogger.
 */
class LogRecord {
	public:
		LogRecord(NXLogLevel logLevel, const std::string& source,
				  const std::string& message) {
			this->logLevel = logLevel;
			this->source = source;
			this->message = message;
			dateTime = QDateTime::currentDateTime();
		}
		
		NXLogLevel getLogLevel() { return logLevel; }
		QDateTime getDateTime() { return dateTime; }
		std::string getSource() { return source; }
		std::string getMessage() { return message; }
		
	private:
		NXLogLevel logLevel;
		QDateTime dateTime;
		std::string source;
		std::string message;
};


/* CLASS: NXLogHandler */
/**
 * Base class for NXLogger log entry emission handlers.
 * @ingroup NanorexUtility, Logging
 */
class NXLogHandler {
	public:
		NXLogHandler(NXLogLevel logLevel) { this->logLevel = logLevel; }
		virtual ~NXLogHandler() { }
		
		virtual void publish(LogRecord logRecord) = 0;
	
	protected:
		NXLogLevel logLevel;
};


/* CLASS: NXLogger */
/**
 * A simple logging mechanism.
 * @ingroup NanorexUtility, Logging
 */
class NXLogger {
	public:
		NXLogger() { ThisInstance = this; }
		~NXLogger() {
			log(NXLogLevel_Info,
				"NXLogger",
				"*********** Log End *************");
			
			// Delete handlers
			std::list<NXLogHandler*>::iterator iter = logHandlers.begin();
			while (iter != logHandlers.end()) {
				delete (*iter);
				iter++;
			}
		}
		
		void log(NXLogLevel logLevel, const std::string& source,
				 const std::string& message) {
			mutex.lock();
			LogRecord logRecord(logLevel, source, message);
			std::list<NXLogHandler*>::iterator iter = logHandlers.begin();
			while (iter != logHandlers.end()) {
				(*iter)->publish(logRecord);
				iter++;
			}
			mutex.unlock();
		}
		
		void addHandler(NXLogHandler* logHandler) {
			logHandlers.push_back(logHandler);
			logHandler->publish(LogRecord(NXLogLevel_Info,
										 "NXLogger",
										 "*********** Log Start ***********"));
		}
		
		static NXLogger* Instance() { return ThisInstance; }

	private:
		QMutex mutex;
		std::list<NXLogHandler*> logHandlers;
		static NXLogger* ThisInstance;
};


// Convenience macros
#define NXLOG_DEBUG(source, message) { \
	Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance(); \
	if (logger != 0) \
		logger->log(Nanorex::NXLogLevel_Debug, source, message); \
};

#define NXLOG_CONFIG(source, message) { \
	Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance(); \
	if (logger != 0) \
		logger->log(Nanorex::NXLogLevel_Config, source, message); \
};

#define NXLOG_INFO(source, message) { \
	Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance(); \
	if (logger != 0) \
    logger->log(Nanorex::NXLogLevel_Info, (source), (message)); \
};

#define NXLOG_WARNING(source, message) { \
	Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance(); \
	if (logger != 0) \
		logger->log(Nanorex::NXLogLevel_Warning, source, message); \
};

#define NXLOG_SEVERE(source, message) { \
	Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance(); \
	if (logger != 0) \
		logger->log(Nanorex::NXLogLevel_Severe, source, message); \
};


/* CLASS: NXConsoleLogHandler */
/**
 * Emits log entries to the console.
 * @ingroup NanorexUtility, Logging
 */
class NXConsoleLogHandler : public NXLogHandler {
	public:
		NXConsoleLogHandler(NXLogLevel logLevel) : NXLogHandler(logLevel) { }
		void publish(LogRecord logRecord) {
			if (logRecord.getLogLevel() >= logLevel) {
				//mutex.lock();
				printf("%s  [%-7s]  %s %s\n",
					   qPrintable(logRecord.getDateTime()
									.toString("yyyy-MM-dd hh:mm:ss.zzz")),
					   LogLevelNames[logRecord.getLogLevel()],
					   (logRecord.getSource().length() == 0 ?
							"" : logRecord.getSource().append(":").c_str()),
					   logRecord.getMessage().c_str());
				fflush(0);
				//mutex.unlock();
			}
		}

	private:
		QMutex mutex;
};


/* CLASS: NXFileLogHandler */
/**
 * Emits log entries to a specified file.
 * @ingroup NanorexUtility, Logging
 */
class NXFileLogHandler : public NXLogHandler {
	public:
		NXFileLogHandler(const std::string& filename, NXLogLevel logLevel) :
				NXLogHandler(logLevel) {
			filehandle = fopen(filename.c_str(), "w");
			if (filehandle != 0) {
				fprintf(filehandle,
						"%s  NXFileLogHandler started. Writing to: %s\n",
						qPrintable(QDateTime::currentDateTime()
							.toString("yyyy-MM-dd hh:mm:ss.zzz")),
						filename.c_str());
				printf("NXFileLogHandler started. Writing to: %s\n",
					   filename.c_str());
			} else
				printf("NXFileLogHandler could not open file for writing: %s\n",
					   filename.c_str());
		}
		~NXFileLogHandler() {
			if (filehandle != 0)
				fclose(filehandle);
		}
		void publish(LogRecord logRecord) {
			if ((filehandle != 0) && (logRecord.getLogLevel() >= logLevel)) {
				//mutex.lock();
				fprintf(filehandle,"%s  [%-7s]  %s %s\n",
						qPrintable(logRecord.getDateTime()
							.toString("yyyy-MM-dd hh:mm:ss.zzz")),
						LogLevelNames[logRecord.getLogLevel()],
						(logRecord.getSource().length() == 0 ?
							"" : logRecord.getSource().append(":").c_str()),
						logRecord.getMessage().c_str());
				//mutex.unlock();
			}
		}

	private:
		QMutex mutex;
		FILE* filehandle;
};

} // Nanorex::

#endif
