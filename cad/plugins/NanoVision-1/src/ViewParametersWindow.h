// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef VIEWPARAMETERSWINDOW_H
#define VIEWPARAMETERSWINDOW_H

#include <QWidget>

#include "ui_ViewParametersWindow.h"

class ViewParametersWindow : public QWidget, private Ui_ViewParametersWindow {
	Q_OBJECT

public:
	ViewParametersWindow(QWidget *parent = 0);

	~ViewParametersWindow();

};

#endif
