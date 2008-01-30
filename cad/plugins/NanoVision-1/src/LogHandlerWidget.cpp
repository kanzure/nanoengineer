// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "LogHandlerWidget.h"


/* CONSTRUCTOR */
LogHandlerWidget::LogHandlerWidget(NXLogLevel logLevel, QWidget* parent)
		 : QWidget(parent), NXLogHandler(logLevel), Ui_LogHandlerWidget() {
		
	setupUi(this);
	suppressed = false;
}


void LogHandlerWidget::setSuppressed(bool suppressed) {
	if (!suppressed) {
		textEdit->setText(storedMessages);
		storedMessages = "";
	}
	this->suppressed = suppressed;
}


/* FUNCTION: publish */
void LogHandlerWidget::publish(LogRecord logRecord) {
	mutex.lock();
	QString message =
		QString("%1  [%2]  %3 %4")
			.arg(logRecord.getDateTime().toString("yyyy-MM-dd hh:mm:ss.zzz"))
			.arg(LogLevelNames[logRecord.getLogLevel()], -7)
			.arg(logRecord.getSource().length() == 0 ?
				"" : logRecord.getSource().append(":").c_str())
			.arg(logRecord.getMessage().c_str());
	if (suppressed)
		storedMessages.append(message);
	else
		textEdit->append(message);
	mutex.unlock();
}
