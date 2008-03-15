// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "AboutBox.h"


/* CONSTRUCTORS */
AboutBox::AboutBox(QWidget *parent) : QDialog(parent) {
		
	setupUi(this);
	setWindowFlags(Qt::Dialog | Qt::Tool);
}

