// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef NV1_H
#define NV1_H

#include <map>
#include <string>
using namespace std;

#include <QtGui>
#include <QMainWindow>
#include <QFileDialog>
#include <QCloseEvent>

#include "Nanorex/Utility/NXCommandLine.h"
#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "ResultsWindow.h"
#include "LogHandlerWidget.h"
#include "JobSelectorDialog.h"
#include "MainWindowTabWidget.h"
#include "JobManagement/JobMonitor.h"
#include "JobManagement/GROMACS_JobMonitor.h"


/* CLASS: nv1 */
class nv1 : public QMainWindow {
	Q_OBJECT

public:
	nv1(NXEntityManager* entityManager, LogHandlerWidget* logHandlerWidget);
	~nv1();
	
	void processCommandLine(int argc, char *argv[]);
	void loadFile(const string& filename, const string& processType,
				  const string& processInit);

protected:
	void closeEvent (QCloseEvent *event);

public slots:
	void updateMenus();
	void addMonitoredJob(const QString& processType, const QString& id,
						 const QString& title);
	void removeMonitoredJob(const QString& id);

private slots:
	void open();
    void close();
	void about();
	void updateWindowMenu();
	void abortJob(const QString& id);
	void checkForActiveJobs(string& filename, string& processType,
							string& processInit);

private:
	NXEntityManager* entityManager;
	
	QMenu* fileMenu;
	QMenu* processMenu;
	QMenu* windowMenu;
	QMenu* helpMenu;
	
	QToolBar* fileToolBar;

	MainWindowTabWidget* mainWindowTabs;
	ResultsWindow* resultsWindow;
	
	// File
	QAction* openAction;
    QAction* closeAction;
    QAction* exitAction;
	
	// Job Management
	QAction* abortJobAction;
	
	// Window
    QAction* windowCloseAction;
	QAction* windowCloseAllAction;
	QAction* windowTileAction;
	QAction* windowCascadeAction;
	QAction* windowArrangeAction;
	QAction* windowNextAction;
	QAction* windowPreviousAction;
	QAction* windowSeparatorAction;
	
	// Help
	QAction* aboutAction;
	
	map<QString, JobMonitor*> jobMonitors;
    
    // currently opened file
    QString fileName;
	
	void createActions();
	void createMenus();
	void createToolBars();
	void createStatusBar();
	void readSettings();
	void writeSettings();
};

#endif
