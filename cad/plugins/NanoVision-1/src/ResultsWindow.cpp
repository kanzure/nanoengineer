// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"


/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager, QWidget* parent)
		: QWidget(parent), Ui_ResultsWindow() {
	this->entityManager = entityManager;
		
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

	QApplication::setOverrideCursor(Qt::WaitCursor);
	
	// Read file
	NXCommandResult* commandResult =
		entityManager->importFromFile(qPrintable(fileName));
	// TODO: delete this commandResult
	QApplication::restoreOverrideCursor();
	
	if (commandResult->getResult() != NX_CMD_SUCCESS) {
		QFileInfo fileInfo(fileName);
		QString message =
			tr("Unable to open file: %1").arg(fileInfo.fileName());
		ErrorDialog errorDialog(message, commandResult);
		errorDialog.exec();
		return false;
		
	} else {
		setCurrentFile(fileName);

/* MDI data window example
	DataWindow *child = new DataWindow;
	workspace->addWindow(child);
	child->show();
*/
/* Floating data window example
	ViewParametersWindow* viewParametersWindow =
		new ViewParametersWindow(this);
	viewParametersWindow->show();
*/

		return true;
	}
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
