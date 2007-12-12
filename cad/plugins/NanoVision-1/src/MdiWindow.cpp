// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "MdiWindow.h"


/* CONSTRUCTOR */
MdiWindow::MdiWindow(QWidget *parent)
		: QWidget(parent) {
	setAttribute(Qt::WA_DeleteOnClose);
}


/* DESTRUCTOR */
MdiWindow::~MdiWindow() {
}


/* FUNCTION: loadFile */
bool MdiWindow::loadFile(const QString &fileName) {
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
QString MdiWindow::userFriendlyCurrentFile() {
	return strippedName(curFile);
}


/* FUNCTION: closeEvent */
void MdiWindow::closeEvent(QCloseEvent *event) {
	event->accept();
}


/* FUNCTION: setCurrentFile */
void MdiWindow::setCurrentFile(const QString &fileName) {
	curFile = QFileInfo(fileName).canonicalFilePath();
	setWindowTitle(userFriendlyCurrentFile() + "[*]");
}


/* FUNCTION: strippedName */
QString MdiWindow::strippedName(const QString &fullFileName) {
	return QFileInfo(fullFileName).fileName();
}

