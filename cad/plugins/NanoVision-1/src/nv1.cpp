// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "nv1.h"


/* CONSTRUCTOR */
nv1::nv1() {
	/* For Qt 4.3
	QMdiArea* mdiArea = new QMdiArea();
	setCentralWidget(mdiArea);
	*/

	/* For Qt 4.2 */
	workspace = new QWorkspace();
	setCentralWidget(workspace);
	connect(workspace, SIGNAL(windowActivated(QWidget *)),
	        this, SLOT(updateMenus()));
	windowMapper = new QSignalMapper(this);
	connect(windowMapper, SIGNAL(mapped(QWidget *)),
	        workspace, SLOT(setActiveWindow(QWidget *)));


	createActions();
	createMenus();
	createToolBars();
	createStatusBar();

	readSettings();

	setWindowTitle(tr("NanoVision-1"));
}


/* DESTRUCTOR */
nv1::~nv1() {
}


/* FUNCTION: closeEvent */
void nv1::closeEvent(QCloseEvent *event) {
	workspace->closeAllWindows();
	if (activeResultsWindow()) {
		event->ignore();
	} else {
		writeSettings();
		event->accept();
	}
}


/* FUNCTION: open */
void nv1::open() {
	QString fileName = QFileDialog::getOpenFileName(this);
	if (!fileName.isEmpty()) {
		ResultsWindow* existing = findResultsWindow(fileName);
		if (existing) {
			workspace->setActiveWindow(existing);
			return;
		}

		ResultsWindow* window = createResultsWindow();
		if (window->loadFile(fileName)) {
			statusBar()->showMessage(tr("File loaded"), 2000);
			window->show();
		} else {
			window->close();
		}
	}
}


/* FUNCTION: about */
void nv1::about() {
	QMessageBox::about(this,
	                   tr("About NanoVision-1"),
	                   tr("Nanorex NanoVision-1 0.1.0\n"
	                      "Copyright 2007 Nanorex, Inc.\n"
	                      "See LICENSE file for details."));
}


/* FUNCTION: updateMenus */
void nv1::updateMenus() {
	bool hasResultsWindow = (activeResultsWindow() != 0);
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

	QList<QWidget*> windows = workspace->windowList();
	separatorAction->setVisible(!windows.isEmpty());

	for (int index = 0; index < windows.size(); ++index) {
		ResultsWindow* window = qobject_cast<ResultsWindow*>(windows.at(index));

		QString text;
		if (index < 9) {
			text = tr("&%1 %2").arg(index + 1)
			       .arg(window->userFriendlyCurrentFile());
		} else {
			text = tr("%1 %2").arg(index + 1)
			       .arg(window->userFriendlyCurrentFile());
		}
		QAction *action  = windowMenu->addAction(text);
		action->setCheckable(true);
		action ->setChecked(window == activeResultsWindow());
		connect(action, SIGNAL(triggered()), windowMapper, SLOT(map()));
		windowMapper->setMapping(action, window);
	}
}


/* FUNCTION: createResultsWindow */
ResultsWindow* nv1::createResultsWindow() {
	ResultsWindow* window = new ResultsWindow;
	workspace->addWindow(window);

	return window;
}


/* FUNCTION: createActions */
void nv1::createActions() {

	openAction = new QAction(QIcon(":/fileopen.xpm"), tr("&Open..."), this);
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
	        workspace, SLOT(closeActiveWindow()));

	closeAllAction = new QAction(tr("Close &All"), this);
	closeAllAction->setStatusTip(tr("Close all the windows"));
	connect(closeAllAction, SIGNAL(triggered()),
	        workspace, SLOT(closeAllWindows()));

	tileAction = new QAction(tr("&Tile"), this);
	tileAction->setStatusTip(tr("Tile the windows"));
	connect(tileAction, SIGNAL(triggered()), workspace, SLOT(tile()));

	cascadeAction = new QAction(tr("&Cascade"), this);
	cascadeAction->setStatusTip(tr("Cascade the windows"));
	connect(cascadeAction, SIGNAL(triggered()), workspace, SLOT(cascade()));

	arrangeAction = new QAction(tr("Arrange &icons"), this);
	arrangeAction->setStatusTip(tr("Arrange the icons"));
	connect(arrangeAction, SIGNAL(triggered()), workspace, SLOT(arrangeIcons()));

	nextAction = new QAction(tr("Ne&xt"), this);
	nextAction->setStatusTip(tr("Move the focus to the next window"));
	connect(nextAction, SIGNAL(triggered()),
	        workspace, SLOT(activateNextWindow()));

	previousAction = new QAction(tr("Pre&vious"), this);
	previousAction->setStatusTip(tr("Move the focus to the previous "
	                                "window"));
	connect(previousAction, SIGNAL(triggered()),
	        workspace, SLOT(activatePreviousWindow()));

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
	QSettings settings("Nanorex", "NanoVision-1");
	QPoint pos = settings.value("pos", QPoint(200, 200)).toPoint();
	QSize size = settings.value("size", QSize(400, 400)).toSize();
	resize(size);
	move(pos);
}


/* FUNCTION: writeSettings */
void nv1::writeSettings() {
	QSettings settings("Nanorex", "NanoVision-1");
	settings.setValue("pos", pos());
	settings.setValue("size", size());
}


/* FUNCTION: activeResultsWindow */
ResultsWindow* nv1::activeResultsWindow() {
	return qobject_cast<ResultsWindow *>(workspace->activeWindow());
}


/* FUNCTION: findResultsWindow */
ResultsWindow* nv1::findResultsWindow(const QString &fileName) {
	QString canonicalFilePath = QFileInfo(fileName).canonicalFilePath();

	foreach (QWidget* window, workspace->windowList()) {
		ResultsWindow* resultsWindow = qobject_cast<ResultsWindow*>(window);
		if (resultsWindow->currentFile() == canonicalFilePath)
			return resultsWindow;
	}
	return 0;
}
