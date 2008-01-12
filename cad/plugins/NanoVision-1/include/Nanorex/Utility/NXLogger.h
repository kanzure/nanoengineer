// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_LOGGER_H
#define NX_LOGGER_H

#include <list>
#include <string>

#include <QDateTime>

namespace Nanorex {

typedef enum LogLevel {
	LogLevel_Debug,		// General debugging.
	LogLevel_Config,	// Debugging configurations (graphics depth, os, etc.)
	LogLevel_Info,		// Information interesting to the user.
	LogLevel_Warning,	// Important things the user should know.
	LogLevel_Severe		// Things that should stop the user before continuing.
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
		LogRecord(LogLevel logLevel, const std::string& source,
				  const std::string& message) {
			this->logLevel = logLevel;
			this->source = source;
			this->message = message;
			dateTime = QDateTime::currentDateTime();
		}
		
		LogLevel getLogLevel() { return logLevel; }
		QDateTime getDateTime() { return dateTime; }
		std::string getSource() { return source; }
		std::string getMessage() { return message; }
		
	private:
		LogLevel logLevel;
		QDateTime dateTime;
		std::string source;
		std::string message;
};


/* CLASS: NXLogHandler */
class NXLogHandler {
	public:
		NXLogHandler(LogLevel logLevel) { this->logLevel = logLevel; }
		virtual ~NXLogHandler() { }
		
		virtual void publish(LogRecord logRecord) = 0;
	
	private:
		LogLevel logLevel;
};


/* CLASS: NXLogger */
/**
 * @ingroup NanorexUtility
 */
class NXLogger {
	public:
		void log(LogLevel logLevel, const std::string& source,
				 const std::string& message) {
			std::list<NXLogHandler*>::iterator iter = logHandlers.begin();
			while (iter != logHandlers.end()) {
				(*iter)->publish(LogRecord(logLevel, source, message));
				iter++;
			}
		}
		void log(LogLevel logLevel, const std::string& message) {
			log(logLevel, std::string(""), message);
		}
		
		void addHandler(NXLogHandler* logHandler) {
			logHandlers.push_back(logHandler);
		}

	private:
		std::list<NXLogHandler*> logHandlers;
};


class NXConsoleLogHandler : public NXLogHandler {
	public:
		NXConsoleLogHandler(LogLevel logLevel) : NXLogHandler(logLevel) { }
		void publish(LogRecord logRecord) {
			printf("%s [%-7s] %s %s\n",
				   qPrintable(logRecord.getDateTime()
				   				.toString("yyyy-MM-dd hh:mm:ss.zzz")),
				   LogLevelNames[logRecord.getLogLevel()],
				   (logRecord.getSource().length() == 0 ?
				   		"" : logRecord.getSource().append(":").c_str()),
				   logRecord.getMessage().c_str());
		}
};

} // Nanorex::

#endif
