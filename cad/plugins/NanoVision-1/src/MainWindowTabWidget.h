// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef MAINWINDOWTABWIDGET_H
#define MAINWINDOWTABWIDGET_H

#include <QWidget>

#include <ui_MainWindowTabWidget.h>


/* CLASS MainWindowTabWidget */
class MainWindowTabWidget : public QWidget, public Ui_MainWindowTabWidget {
	Q_OBJECT

public:
	MainWindowTabWidget(QWidget *parent = 0);
	~MainWindowTabWidget();

};

#endif
