// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef RESULTSSUMMARYWINDOW_H
#define RESULTSSUMMARYWINDOW_H

#include <string>
#include <vector>
using namespace std;

#include <QWidget>
#include <QDialog>

#include "Nanorex/Utility/NXProperties.h"
using namespace Nanorex;

#include "DataWindow.h"
#include "ui_ResultsSummaryWindow.h"


/* CLASS: ResultsSummaryWindow */
class ResultsSummaryWindow
		: public QDialog, private Ui_ResultsSummaryWindow {
	Q_OBJECT

public:
	ResultsSummaryWindow(NXProperties* properties, QWidget *parent = 0);
	~ResultsSummaryWindow();
};

#endif
