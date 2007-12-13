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

	// Dock widgets test
	//*
	TrajectoryGraphicsPane* trajectoryGraphicsPane =
		new TrajectoryGraphicsPane(this);
	splitter->insertWidget(1, trajectoryGraphicsPane);
	delete widget;
	QDockWidget* dock = new QDockWidget(tr("dna_motor_results"), trajectoryGraphicsPane);
	dock->setAllowedAreas(Qt::LeftDockWidgetArea);
	ViewParametersWindow* viewParametersWindow = new ViewParametersWindow(dock);
	dock->setWidget(viewParametersWindow);
	trajectoryGraphicsPane->addDockWidget(Qt::LeftDockWidgetArea, dock);
	//*/
	
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
