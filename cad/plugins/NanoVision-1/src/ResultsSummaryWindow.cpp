// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsSummaryWindow.h"


/* CONSTRUCTOR */
ResultsSummaryWindow::ResultsSummaryWindow(NXDataStoreInfo* dataStoreInfo,
										   QWidget *parent)
		: QDialog(parent), Ui_ResultsSummaryWindow() {
	this->dataStoreInfo = dataStoreInfo;

	setupUi(this);
	setWindowFlags(Qt::Dialog | Qt::Tool);
	printSummary();
}


/* DESTRUCTOR */
ResultsSummaryWindow::~ResultsSummaryWindow() {
}


/* FUNCTION: refresh */
void ResultsSummaryWindow::refresh() {
	printSummary();
}


/* FUNCTION: printSummary */
void ResultsSummaryWindow::printSummary() {
	textEdit->clear();
	textEdit->insertHtml("<b><i>Results Summary</i></b><br>");
	NXProperties* properties = dataStoreInfo->getResultsSummary();
    if (properties == NULL) return;
	vector<string> keys = properties->getPropertyKeys();
	vector<string>::iterator iter = keys.begin();
	QString line;
	while (iter != keys.end()) {
		line =
			QObject::tr("&nbsp;&nbsp;<b>%1:</b> %2<br>")
				.arg((*iter).c_str())
				.arg(properties->getProperty((*iter)));
		textEdit->insertHtml(line);
		iter++;
	}
	textEdit->insertHtml("0=success, 1=still running, 2=failure, 3=aborted");
}

