// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"


/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(QWidget *parent)
		: QWidget(parent), Ui_ResultsWindow() {
		
	setupUi(this);
	setAttribute(Qt::WA_DeleteOnClose);
}


/* DESTRUCTOR */
ResultsWindow::~ResultsWindow() {
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

	return true;
}


/* FUNCTION: userFriendlyCurrentFile */
QString ResultsWindow::userFriendlyCurrentFile() {
	return strippedName(curFile);
}


/* FUNCTION: closeEvent */
void ResultsWindow::closeEvent(QCloseEvent *event) {
	event->accept();
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
