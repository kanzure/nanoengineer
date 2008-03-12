// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef DATAWINDOW_H
#define DATAWINDOW_H

#include <QtGui>
#include <QWidget>

#include <string>
using namespace std;


/* CLASS: DataWindow */
class DataWindow : public QWidget {
	Q_OBJECT

	public:
		DataWindow(QWidget *parent = 0);
		virtual ~DataWindow() {};
	
	protected:
		void closeEvent(QCloseEvent *event);
		void formatParameter(string& key, string& value, string& units);
};

#endif
