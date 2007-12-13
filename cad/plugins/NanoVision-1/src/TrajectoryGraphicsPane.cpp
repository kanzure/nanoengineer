// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "TrajectoryGraphicsPane.h"

TrajectoryGraphicsPane::TrajectoryGraphicsPane(QWidget *parent)
		: QMainWindow(parent), Ui_TrajectoryGraphicsPane() {

	setupUi(this);
	menubar->hide();
	statusbar->hide();
}


TrajectoryGraphicsPane::~TrajectoryGraphicsPane() {
}


