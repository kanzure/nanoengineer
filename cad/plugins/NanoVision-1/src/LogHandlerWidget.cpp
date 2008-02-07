// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "LogHandlerWidget.h"


/* CONSTRUCTOR */
LogHandlerWidget::LogHandlerWidget(NXLogLevel logLevel, QWidget* parent)
		 : QWidget(parent), NXLogHandler(logLevel), Ui_LogHandlerWidget() {
		
	setupUi(this);
}


/* FUNCTION: publish */
void LogHandlerWidget::publish(LogRecord logRecord) {
	if (logRecord.getLogLevel() >= logLevel) {
		mutex.lock();
		QString source =
			logRecord.getSource().length() == 0 ?
				"" : logRecord.getSource().append(": ").c_str();
		QString message =
			QString("%1  [%2]  %3 %4")
				.arg(logRecord.getDateTime()
					.toString("yyyy-MM-dd hh:mm:ss.zzz"))
				.arg(LogLevelNames[logRecord.getLogLevel()])
				.arg(source)
				.arg(logRecord.getMessage().c_str());
		textEdit->append(message);
		mutex.unlock();
	}
}
