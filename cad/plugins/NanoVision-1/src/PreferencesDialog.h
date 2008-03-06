// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef PREFERENCESDIALOG_H
#define PREFERENCESDIALOG_H

#include <QObject>

#include "ui_PreferencesDialog.h"

class PreferencesDialog : public QDialog, private Ui_PreferencesDialog {
	Q_OBJECT
	
	public:
		PreferencesDialog(QWidget *parent = 0);
		~PreferencesDialog();
};

#endif

