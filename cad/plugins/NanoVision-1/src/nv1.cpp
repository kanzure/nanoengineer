// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "nv1.h"


/* CONSTRUCTOR */
nv1::nv1(NXEntityManager* entityManager, LogHandlerWidget* logHandlerWidget)
		: QMainWindow() {
	this->entityManager = entityManager;
	
	setWindowIcon(QPixmap(":/Icons/eye-icon.png"));
	setWindowTitle(tr("NanoVision-1"));
	
	mainWindowTabs = new MainWindowTabWidget(this);
	setCentralWidget(mainWindowTabs);	
	
	resultsWindow = new ResultsWindow(entityManager, this);
	mainWindowTabs->vboxLayout->removeWidget(mainWindowTabs->widget);
	delete mainWindowTabs->widget;
	mainWindowTabs->vboxLayout->addWidget(resultsWindow);
	resultsWindow->hide();

	createActions();
	createMenus();
	createToolBars();
	updateMenus();
	createStatusBar();

	readSettings();
	
	// Setup log dock widget
	QDockWidget* dock = new QDockWidget(tr("Log"), this);
	dock->setAllowedAreas(Qt::BottomDockWidgetArea);
	dock->setWidget(logHandlerWidget);
	addDockWidget(Qt::BottomDockWidgetArea, dock);
}


/* DESTRUCTOR */
nv1::~nv1() {
}


/* FUNCTION: processCommandLine */
void nv1::processCommandLine(int argc, char *argv[]) {

	NXCommandLine commandLine;
	if ((commandLine.SplitLine(argc, argv) > 0) &&
		(commandLine.HasSwitch("-f"))) {
		string filename = commandLine.GetArgument("-f", 0);
		
		string processType, processInit;
		JobHandle* jobHandle = 0;
		if (commandLine.GetArgumentCount("-p") == 2) {
			processType = commandLine.GetArgument("-p", 0);
			processInit = commandLine.GetArgument("-p", 1);
			if (processType == "GMX")
				jobHandle = new GROMACS_JobHandle(processInit, this);
		}
		
		QString message = tr("Opening file: %1").arg(filename.c_str());
		if (jobHandle != 0)
			message =
				tr("%1 with job handle info: %2 %3")
					.arg(message).arg(processType.c_str())
					.arg(processInit.c_str());
		NXLOG_INFO("nv1", qPrintable(message));
		
		if (resultsWindow->loadFile(filename.c_str())) {
			statusBar()->showMessage(tr("File loaded"), 2000);
			resultsWindow->show();
		}
	}
}


/* FUNCTION: closeEvent */
void nv1::closeEvent(QCloseEvent *event) {
	if (resultsWindow != 0)
		delete resultsWindow;
		
	writeSettings();
	event->accept();
}


/* FUNCTION: open */
void nv1::open() {
	QString importFileTypes = entityManager->getImportFileTypes().c_str();
	QString fileName =
		QFileDialog::getOpenFileName(this, tr("Open File"), "",
									 importFileTypes + ";;All Types (*)");
	if (!fileName.isEmpty()) {
		if (resultsWindow->loadFile(fileName)) {
			statusBar()->showMessage(tr("File loaded"), 2000);
			resultsWindow->show();
		}
	}
}


/* FUNCTION: about */
void nv1::about() {
	QMessageBox::about(this,
	                   tr("About NanoVision-1"),
	                   tr("Nanorex NanoVision-1 0.1.0\n"
	                      "Copyright 2008 Nanorex, Inc.\n"
	                      "See LICENSE file for details."));
}


/* FUNCTION: updateMenus */
void nv1::updateMenus() {
	bool hasResultsWindow = resultsWindow->isVisible();
	closeAction->setEnabled(hasResultsWindow);
	closeAllAction->setEnabled(hasResultsWindow);
	tileAction->setEnabled(hasResultsWindow);
	cascadeAction->setEnabled(hasResultsWindow);
	arrangeAction->setEnabled(hasResultsWindow);
	nextAction->setEnabled(hasResultsWindow);
	previousAction->setEnabled(hasResultsWindow);
	separatorAction->setVisible(hasResultsWindow);
}


/* FUNCTION: updateWindowMenu */
void nv1::updateWindowMenu() {
	windowMenu->clear();
	windowMenu->addAction(closeAction);
	windowMenu->addAction(closeAllAction);
	windowMenu->addSeparator();
	windowMenu->addAction(tileAction);
	windowMenu->addAction(cascadeAction);
	windowMenu->addAction(arrangeAction);
	windowMenu->addSeparator();
	windowMenu->addAction(nextAction);
	windowMenu->addAction(previousAction);
	windowMenu->addAction(separatorAction);

	QList<QWidget*> windows = resultsWindow->workspace->windowList();
	separatorAction->setVisible(!windows.isEmpty());

	for (int index = 0; index < windows.size(); ++index) {
		DataWindow* window = qobject_cast<DataWindow*>(windows.at(index));

		QString windowTitle;
		if (window == 0) {
			windowTitle = "--";
			NXLOG_DEBUG("nv1::updateWindowMenu()", "window is null");
		} else
			windowTitle = window->windowTitle();
		
		QString text;
		if (index < 9)
			text = tr("&%1 %2").arg(index + 1).arg(windowTitle);
		else
			text = tr("%1 %2").arg(index + 1).arg(windowTitle);

		QAction *action  = windowMenu->addAction(text);
		action->setCheckable(true);
		action->setChecked(window == resultsWindow->activeDataWindow());
		connect(action, SIGNAL(triggered()), resultsWindow->windowMapper, 
				SLOT(map()));
		resultsWindow->windowMapper->setMapping(action, window);
	}
}


/* FUNCTION: createActions */
void nv1::createActions() {

	openAction =
		new QAction(QIcon(":/Icons/File/Open.png"), tr("&Open..."), this);
	openAction->setShortcut(tr("Ctrl+O"));
	openAction->setStatusTip(tr("Open an existing file"));
	connect(openAction, SIGNAL(triggered()), this, SLOT(open()));

	exitAction = new QAction(tr("E&xit"), this);
	exitAction->setShortcut(tr("Ctrl+Q"));
	exitAction->setStatusTip(tr("Exit NanoVision-1"));
	connect(exitAction, SIGNAL(triggered()), qApp, SLOT(closeAllWindows()));

	closeAction = new QAction(tr("Cl&ose"), this);
	closeAction->setShortcut(tr("Ctrl+F4"));
	closeAction->setStatusTip(tr("Close the active window"));
 	connect(closeAction, SIGNAL(triggered()),
 	        resultsWindow->workspace, SLOT(closeActiveWindow()));

	closeAllAction = new QAction(tr("Close &All"), this);
	closeAllAction->setStatusTip(tr("Close all the windows"));
 	connect(closeAllAction, SIGNAL(triggered()),
 	        resultsWindow->workspace, SLOT(closeAllWindows()));

	tileAction = new QAction(tr("&Tile"), this);
	tileAction->setStatusTip(tr("Tile the windows"));
	connect(tileAction, SIGNAL(triggered()), resultsWindow->workspace,
			SLOT(tile()));

	cascadeAction = new QAction(tr("&Cascade"), this);
	cascadeAction->setStatusTip(tr("Cascade the windows"));
 	connect(cascadeAction, SIGNAL(triggered()), resultsWindow->workspace, 
 			SLOT(cascade()));

	arrangeAction = new QAction(tr("Arrange &icons"), this);
	arrangeAction->setStatusTip(tr("Arrange the icons"));
 	connect(arrangeAction, SIGNAL(triggered()), resultsWindow->workspace, 
 			SLOT(arrangeIcons()));

	nextAction = new QAction(tr("Ne&xt"), this);
	nextAction->setStatusTip(tr("Move the focus to the next window"));
 	connect(nextAction, SIGNAL(triggered()),
 	        resultsWindow->workspace, SLOT(activateNextWindow()));

	previousAction = new QAction(tr("Pre&vious"), this);
	previousAction->setStatusTip(tr("Move the focus to the previous "
	                                "window"));
 	connect(previousAction, SIGNAL(triggered()),
 	        resultsWindow->workspace, SLOT(activatePreviousWindow()));

	separatorAction = new QAction(this);
	separatorAction->setSeparator(true);

	aboutAction = new QAction(tr("&About"), this);
	aboutAction->setStatusTip(tr("Show NanoVision-1's About box"));
	connect(aboutAction, SIGNAL(triggered()), this, SLOT(about()));
}


/* FUNCTION: createMenus */
void nv1::createMenus() {
	fileMenu = menuBar()->addMenu(tr("&File"));
	fileMenu->addAction(openAction);
	fileMenu->addSeparator();
	fileMenu->addAction(exitAction);

	processMenu = menuBar()->addMenu(tr("&Job Management"));
	
	windowMenu = menuBar()->addMenu(tr("&Window"));
	updateWindowMenu();
	connect(windowMenu, SIGNAL(aboutToShow()), this, SLOT(updateWindowMenu()));

	menuBar()->addSeparator();

	helpMenu = menuBar()->addMenu(tr("&Help"));
	helpMenu->addAction(aboutAction);
}


/* FUNCTION: createToolBars */
void nv1::createToolBars() {
	fileToolBar = addToolBar(tr("File"));
	fileToolBar->addAction(openAction);
}


/* FUNCTION: createStatusBar */
void nv1::createStatusBar() {
	statusBar()->showMessage(tr("Ready"));
}


/* FUNCTION: readSettings */
void nv1::readSettings() {
	QSettings settings(QSettings::IniFormat, QSettings::UserScope,
					   "Nanorex", "NanoVision-1");
	QPoint pos = settings.value("Layout/Position", QPoint(200, 200)).toPoint();
	QSize size = settings.value("Layout/Size", QSize(400, 400)).toSize();
	resize(size);
	move(pos);
}


/* FUNCTION: writeSettings */
void nv1::writeSettings() {
	QSettings settings(QSettings::IniFormat, QSettings::UserScope,
					   "Nanorex", "NanoVision-1");
	settings.setValue("Layout/Position", pos());
	settings.setValue("Layout/Size", size());
}
