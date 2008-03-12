// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsSummaryWindow.h"


/* CONSTRUCTOR */
ResultsSummaryWindow::ResultsSummaryWindow(const QString& filename,
										   NXDataStoreInfo* dataStoreInfo,
										   QWidget *parent)
		: DataWindow(parent), Ui_ResultsSummaryWindow() {
	this->dataStoreInfo = dataStoreInfo;

	setupUi(this);
	QString title = tr("Results Summary - %1").arg(filename);
	setWindowTitle(title);
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
	NXProperties* properties = dataStoreInfo->getResultsSummary();
	if (properties == NULL) {
		textEdit->insertHtml(tr("<i><b>Results Summary</b><br>No results summary found.</i>"));
		
	} else {
		QString html =
			QString("<i><b>Results Summary</b></i><br><table border=0 cellspacing=0 cellpadding=0>");
		vector<string> keys = properties->getPropertyKeys();
		vector<string>::iterator iter = keys.begin();
		string key, value, units;
		while (iter != keys.end()) {
			key = *iter;
			value = properties->getProperty(*iter);
			if (value != "") {
				formatParameter(key, value, units);
				html.append
					(tr("<tr><td align=right><b>%1: </b></td>%2 %3</tr>")
					 .arg(key.c_str()).arg(value.c_str()).arg(units.c_str()));
			}
			iter++;
		}
		html.append("</table>");
		textEdit->clear();
		textEdit->setHtml(html);
	}
}

