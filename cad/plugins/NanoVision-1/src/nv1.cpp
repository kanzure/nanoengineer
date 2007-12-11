// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.


#include "nv1.h"


/* CONSTRUCTOR */
nv1::nv1() {
	QWidget* mdiArea = new QWidget();
	setCentralWidget(mdiArea);

	createActions();
	createMenus();
	createToolBars();
	createStatusBar();

	readSettings();

	setCurrentFile("");
}


/* DESTRUCTOR */
nv1::~nv1() {
}


/* FUNCTION: closeEvent */
void nv1::closeEvent(QCloseEvent *event) {
	writeSettings();
	event->accept();
}


/* FUNCTION: open */
void nv1::open() {
	QString fileName = QFileDialog::getOpenFileName(this);
	if (!fileName.isEmpty())
		loadFile(fileName);
}


/* FUNCTION: about */
void nv1::about() {
	QMessageBox::about(this,
					   tr("About NanoVision-1"),
	                   tr("Nanorex NanoVision-1 0.1.0\n"
	                      "Copyright 2007 Nanorex, Inc.\n"
						  "See LICENSE file for details."));
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
	connect(exitAction, SIGNAL(triggered()), this, SLOT(close()));

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


/* FUNCTION: loadFile */
void nv1::loadFile(const QString &fileName) {
	QFile file(fileName);
	if (!file.open(QFile::ReadOnly | QFile::Text)) {
		QMessageBox::warning(this, tr("NanoVision-1"),
		                     tr("Cannot read file %1:\n%2.")
		                     .arg(fileName)
		                     .arg(file.errorString()));
		return;
	}

	QApplication::setOverrideCursor(Qt::WaitCursor);
	// Read file
	QApplication::restoreOverrideCursor();

	setCurrentFile(fileName);
	statusBar()->showMessage(tr("File loaded"), 2000);
}


/* FUNCTION: setCurrentFile */
void nv1::setCurrentFile(const QString &fileName) {
	curFile = fileName;

	QString shownName;
	if (curFile.isEmpty())
		shownName = "";
	else
		shownName = strippedName(curFile);

	setWindowTitle(tr("%1[*] - %2").arg(shownName).arg(tr("NanoVision-1")));
}


/* FUNCTION: strippedName */
QString nv1::strippedName(const QString &fullFileName) {
	return QFileInfo(fullFileName).fileName();
}
