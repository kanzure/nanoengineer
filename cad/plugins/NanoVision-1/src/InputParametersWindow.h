// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef INPUTPARAMETERSWINDOW_H
#define INPUTPARAMETERSWINDOW_H

#include <string>
#include <vector>
using namespace std;

#include <QWidget>
#include <QDialog>

#include "Nanorex/Utility/NXProperties.h"
using namespace Nanorex;

#include "DataWindow.h"
#include "ui_InputParametersWindow.h"


/* CLASS: InputParametersWindow */
class InputParametersWindow
		: public DataWindow, private Ui_InputParametersWindow {
	Q_OBJECT

	public:
		InputParametersWindow(const QString& filename, NXProperties* properties,
							  QWidget *parent = 0);
		~InputParametersWindow();
};

#endif
