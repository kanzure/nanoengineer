// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "DataWindow.h"


/* CONSTRUCTOR */
DataWindow::DataWindow(QWidget *parent) : QWidget(parent) {
	//setAttribute(Qt::WA_DeleteOnClose);

	static int sequenceNumber = 1;
	QString curFile = tr("document%1").arg(sequenceNumber++);
	setWindowTitle(curFile);
}


/* FUNCTION: closeEvent */
void DataWindow::closeEvent(QCloseEvent *event) {
	event->accept();
}
