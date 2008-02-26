// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "InputParametersWindow.h"


/* CONSTRUCTOR */
InputParametersWindow::InputParametersWindow(NXProperties* properties,
											 QWidget *parent)
		: QDialog(parent), Ui_InputParametersWindow() {

	setupUi(this);
	setWindowFlags(Qt::Dialog | Qt::Tool);
	
	textEdit->insertHtml("<b><i>InputParameters</i></b><br>");
    if(properties == NULL) return;
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
InputParametersWindow::~InputParametersWindow() {
}


