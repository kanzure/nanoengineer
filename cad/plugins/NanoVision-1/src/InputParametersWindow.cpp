// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "InputParametersWindow.h"


/* CONSTRUCTOR */
InputParametersWindow::InputParametersWindow(const QString& filename,
											 NXProperties* properties,
											 QWidget *parent)
		: DataWindow(parent), Ui_InputParametersWindow() {
	
	setupUi(this);
	QString title = tr("Input Parameters - %1").arg(filename);
	setWindowTitle(title);
	setWindowFlags(Qt::Dialog | Qt::Tool);
	
	if (properties == NULL) {
		textEdit->insertHtml(tr("<i><b>Input Parameters</b><br>No input parameters found.</i>"));
		
	} else {
		QString html =
			QString("<i><b>Input Parameters</b></i><br><table border=0 cellspacing=0 cellpadding=0>");
		vector<string> keys = properties->getPropertyKeys();
		vector<string>::iterator iter = keys.begin();
		string key, value, units;
		while (iter != keys.end()) {
			key = *iter;
			value = properties->getProperty(*iter);
			formatParameter(key, value, units);
			html.append
				(tr("<tr><td align=right><b>%1: </b></td>%2 %3</tr>")
					.arg(key.c_str()).arg(value.c_str()).arg(units.c_str()));
			iter++;
		}
		html.append("</table>");
		textEdit->setHtml(html);
	}
}


/* DESTRUCTOR */
InputParametersWindow::~InputParametersWindow() {
}

