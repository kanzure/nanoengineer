// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef VIEWPARAMETERSWINDOW_H
#define VIEWPARAMETERSWINDOW_H

#include <QWidget>
#include <QDialog>

#include "ui_ViewParametersWindow.h"


/* CLASS: ViewParametersWindow */
class ViewParametersWindow : public QDialog, private Ui_ViewParametersWindow {
	Q_OBJECT

public:
	ViewParametersWindow(QWidget *parent = 0);
	~ViewParametersWindow();
};

#endif
