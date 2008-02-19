// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef VIEWPARAMETERSWINDOW_H
#define VIEWPARAMETERSWINDOW_H

#include <string>
#include <vector>
using namespace std;

#include <QWidget>
#include <QDialog>

#include "Nanorex/Utility/NXProperties.h"
using namespace Nanorex;

#include "ui_ViewParametersWindow.h"


/* CLASS: ViewParametersWindow */
class ViewParametersWindow : public QDialog, private Ui_ViewParametersWindow {
	Q_OBJECT

public:
	ViewParametersWindow(NXProperties* properties, QWidget *parent = 0);
	~ViewParametersWindow();
};

#endif
