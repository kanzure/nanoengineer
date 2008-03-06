// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef JOBSELECTORDIALOG_H
#define JOBSELECTORDIALOG_H

#include <QObject>
#include <QPushButton>

#include "ui_JobSelectorDialog.h"

class JobSelectorDialog : public QDialog, private Ui_JobSelectorDialog {

	Q_OBJECT
	
	public:
		JobSelectorDialog(QWidget *parent = 0);
		~JobSelectorDialog();
	
		void addActiveJobs(const QStringList& activeJobs);
		QString getSelection();
	
	public slots:
		void itemSelected(QListWidgetItem* item);
};

#endif

