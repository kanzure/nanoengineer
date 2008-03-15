// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef ABOUTBOX_H
#define ABOUTBOX_H

#include <QDialog>

#include "ui_AboutBox.h"

class AboutBox : public QDialog, private Ui_AboutBox {
	Q_OBJECT
	
	public:
		AboutBox(QWidget *parent = 0);
};

#endif
