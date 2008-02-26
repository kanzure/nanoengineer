// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsSummaryWindow.h"


/* CONSTRUCTOR */
ResultsSummaryWindow::ResultsSummaryWindow(NXProperties* properties,
										   QWidget *parent)
		: QDialog(parent), Ui_ResultsSummaryWindow() {
printf("ResultsSummaryWindow::ResultsSummaryWindow\n");fflush(0);

	setupUi(this);
	setWindowFlags(Qt::Dialog | Qt::Tool);
	
printf("\n\nResultsSummaryWindow::ResultsSummaryWindow: %d\n", properties);fflush(0);
	textEdit->insertHtml("<b><i>Results Summary</i></b><br>");
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
}


/* DESTRUCTOR */
ResultsSummaryWindow::~ResultsSummaryWindow() {
}


