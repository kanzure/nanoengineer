// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef PREFERENCESDIALOG_H
#define PREFERENCESDIALOG_H

#include <QObject>
#include <QFileDialog>

#include "UserSettings.h"
#include "ui_PreferencesDialog.h"

class PreferencesDialog : public QDialog, private Ui_PreferencesDialog {
	Q_OBJECT
	
	public:
		PreferencesDialog(QWidget *parent = 0);
		~PreferencesDialog();
		
	public slots:
		void accept();
		
	private slots:
		void logToFileCheckBoxChanged(int state);
		void logToConsoleCheckBoxChanged(int state);
		void fileLogBrowseButtonClicked(bool checked);
};

#endif

