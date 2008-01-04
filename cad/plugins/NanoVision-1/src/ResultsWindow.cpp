// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"


/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(QWidget *parent)
		: QWidget(parent), Ui_ResultsWindow() {
		
	setupUi(this);

	workspace = new QWorkspace();
 	connect(workspace, SIGNAL(windowActivated(QWidget *)),
 	        this, SLOT(parent->updateMenus()));
	windowMapper = new QSignalMapper(this);
	connect(windowMapper, SIGNAL(mapped(QWidget *)),
	        workspace, SLOT(setActiveWindow(QWidget *)));
	
	splitter->insertWidget(1, workspace);
	delete widget;
}


/* DESTRUCTOR */
ResultsWindow::~ResultsWindow() {
	workspace->closeAllWindows();
	if (activeDataWindow()) {
		; // Can't delete?
	}
}


/* FUNCTION: loadFile */
bool ResultsWindow::loadFile(const QString &fileName) {
	QFile file(fileName);
	if (!file.open(QFile::ReadOnly | QFile::Text)) {
		QMessageBox::warning(this, tr("NanoVision-1"),
		                     tr("Cannot read file %1:\n%2.")
		                     .arg(fileName)
		                     .arg(file.errorString()));
		return false;
	}

	QApplication::setOverrideCursor(Qt::WaitCursor);
	// Read file
	QApplication::restoreOverrideCursor();

	setCurrentFile(fileName);
     
	DataWindow *child = new DataWindow;
	workspace->addWindow(child);
	child->show();

	ViewParametersWindow* viewParametersWindow =
		new ViewParametersWindow(this);
	viewParametersWindow->show();

	return true;
}


/* FUNCTION: userFriendlyCurrentFile */
QString ResultsWindow::userFriendlyCurrentFile() {
	return strippedName(curFile);
}


/* FUNCTION: setCurrentFile */
void ResultsWindow::setCurrentFile(const QString &fileName) {
	curFile = QFileInfo(fileName).canonicalFilePath();
	setWindowTitle(userFriendlyCurrentFile() + "[*]");
}


/* FUNCTION: strippedName */
QString ResultsWindow::strippedName(const QString &fullFileName) {
	return QFileInfo(fullFileName).fileName();
}


/* FUNCTION: activeDataWindow */
DataWindow* ResultsWindow::activeDataWindow() {
	return qobject_cast<DataWindow *>(workspace->activeWindow());
}


/* FUNCTION: createResultsWindow */
DataWindow* ResultsWindow::createDataWindow() {
	DataWindow* window = new DataWindow;
	workspace->addWindow(window);

	return window;
}
