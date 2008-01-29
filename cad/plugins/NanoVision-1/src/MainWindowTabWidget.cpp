// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "MainWindowTabWidget.h"


/* CONSTRUCTOR */
MainWindowTabWidget::MainWindowTabWidget(QWidget *parent)
		: QWidget(parent), Ui_MainWindowTabWidget() {
		
	setupUi(this);
	tabWidget->setTabIcon(0, QIcon(QPixmap(":/Icons/home.png")));
	tabWidget->setTabText(0, "");
}


/* DESTRUCTOR */
MainWindowTabWidget::~MainWindowTabWidget() {
}
