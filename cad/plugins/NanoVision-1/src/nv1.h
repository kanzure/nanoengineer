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
#include "Nanorex/Interface/NXGraphicsManager.h"
using namespace Nanorex;

#include "AboutBox.h"
#include "ResultsWindow.h"
#include "LogHandlerWidget.h"
#include "JobSelectorDialog.h"
#include "PreferencesDialog.h"
#include "MainWindowTabWidget.h"
#include "JobManagement/JobMonitor.h"
#include "JobManagement/GROMACS_JobMonitor.h"


/* CLASS: nv1 */
class nv1 : public QMainWindow {
	Q_OBJECT

public:
	nv1(NXEntityManager* entityManager,
	    NXGraphicsManager *graphicsManager,
	    LogHandlerWidget* logHandlerWidget);
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
	void raiseLogDockWidget();

private slots:
	void open();
    void close();
	void about();
	void updateWindowMenu();
	void abortJob(const QString& id);
	void checkForActiveJobs(string& filename, string& processType,
							string& processInit, bool notify = false);
	void openActiveJobs();
	void showPreferences();
	void toggleLogWindow();
	void fixHDF5_DataStore();

private:
	NXEntityManager* entityManager;
	NXGraphicsManager *graphicsManager;
	
	QToolBar* fileToolBar;
	QToolBar* jobsToolBar;
	QDockWidget* logDockWidget;

	MainWindowTabWidget* mainWindowTabs;
	ResultsWindow* resultsWindow;
	
	QMenu* fileMenu;
	QMenu* viewMenu;
	QMenu* toolsMenu;
	QMenu* jobsMenu;
	QMenu* windowMenu;
	QMenu* helpMenu;

	// File
	QAction* openAction;
    QAction* closeAction;
    QAction* exitAction;
	
	// View
	QAction* logWindowAction;
	
	// Tools
	//
	// Job Management
	QAction* openJobsAction;
	QAction* abortJobAction;
	
	QAction* fixHDF5_DataStoreAction;
	QAction* preferencesAction;
	
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
    
    // Currently opened file
    QString currentFileName;
	
	void createActions();
	void createMenus();
	void createToolBars();
	void createStatusBar();
	void readSettings();
	void writeSettings();
};

#endif
