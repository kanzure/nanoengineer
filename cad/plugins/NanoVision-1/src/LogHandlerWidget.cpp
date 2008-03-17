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
		//mutex.lock();
		QString color = "";
		QString bgcolor = "";
		if (logRecord.getLogLevel() == 3)
			bgcolor = "yellow";
		if (logRecord.getLogLevel() == 4) {
			color = "white";
			bgcolor = "red";
		}
		QString level =
			QString("%1").arg(LogLevelNames[logRecord.getLogLevel()], 7);
		level.replace(QString(" "), QString("&nbsp;"));
		QString source =
			logRecord.getSource().length() == 0 ?
				"" : logRecord.getSource().append(": ").c_str();
		QString message =
			QString("<table border=0 cellspacing=0 cellpadding=0><tr><td><font color=grey>%1 </font></td><td bgcolor=%2><font type=courier color=%3> [<code>%4</code>] %5 %6</font></td></tr></table>")
				.arg(logRecord.getDateTime()
					.toString("yyyy-MM-dd hh:mm:ss.zzz"))
				.arg(bgcolor).arg(color)
				.arg(level)
				.arg(source)
				.arg(logRecord.getMessage().c_str());
		textEdit->insertHtml(message);
		
		if (logRecord.getLogLevel() > 2)
			emit raiseWidget();
		
		//mutex.unlock();
	}
}
