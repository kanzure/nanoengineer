// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef RESULTSWINDOW_H
#define RESULTSWINDOW_H

#include <QtGui>
#include <QWidget>
#include <QFile>
#include <QMessageBox>
#include <QApplication>
#include <QCloseEvent>
#include <QFileInfo>
#include <QMainWindow>
#include <QDockWidget>
#include <QWorkspace>

#include "ui_ResultsWindow.h"
#include "DataWindow.h"
#include "ViewParametersWindow.h"
#include "TrajectoryGraphicsPane.h"


/* CLASS: ResultsWindow */
class ResultsWindow : public QWidget, private Ui_ResultsWindow {
	Q_OBJECT
	
public:
	QWorkspace* workspace;
	QSignalMapper* windowMapper;
	
	ResultsWindow(QWidget *parent = 0);
	~ResultsWindow();

	bool loadFile(const QString &fileName);
	QString userFriendlyCurrentFile();
	QString currentFile() {
		return curFile;
	}
	DataWindow* activeDataWindow();

private slots:
	DataWindow* createDataWindow();

private:
	QString curFile;
	
	void setCurrentFile(const QString &fileName);
	QString strippedName(const QString &fullFileName);
};

#endif
