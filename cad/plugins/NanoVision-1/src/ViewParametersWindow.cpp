// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ViewParametersWindow.h"


/* CONSTRUCTOR */
ViewParametersWindow::ViewParametersWindow(QWidget *parent)
		: QWidget(parent), Ui_ViewParametersWindow() {

	setupUi(this);
	textEdit->setHtml("<b>InputParameters</b><br>&nbsp;&nbsp;Temperature: 300 K");
}


/* DESTRUCTOR */
ViewParametersWindow::~ViewParametersWindow() {
}


