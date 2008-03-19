// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef LOGHANDLERWIDGET_H
#define LOGHANDLERWIDGET_H

#include <QWidget>
#include <QTextEdit>
#include <QHBoxLayout>
#include <QMessageBox>

#include "Nanorex/Utility/NXLogger.h"
using namespace Nanorex;

#include "ui_LogHandlerWidget.h"


/* CLASS: LogHandlerWidget */
class LogHandlerWidget : public QWidget, public NXLogHandler,
						 private Ui_LogHandlerWidget {
	Q_OBJECT
	
	public:
		LogHandlerWidget(NXLogLevel logLevel, QWidget* parent = 0);
		~LogHandlerWidget() { }
			
		void publish(LogRecord logRecord);
		
		QSize sizeHint() const;
	
	signals:
		void raiseWidget();
		
	private:
		//QMutex mutex;
};

#endif
