// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "JobSelectorDialog.h"


/* CONSTRUCTORS */
JobSelectorDialog::JobSelectorDialog(QWidget *parent)
		: QDialog(parent), Ui_JobSelectorDialog() {
		
	setupUi(this);
	buttonBox->button(QDialogButtonBox::Ok)->setDisabled(true);
	connect(listWidget, SIGNAL(itemClicked(QListWidgetItem*)),
			this, SLOT(itemSelected(QListWidgetItem*)));
}


/* DESTRUCTOR */
JobSelectorDialog::~JobSelectorDialog() {
}


/* FUNCTION: addActiveJobs */
void JobSelectorDialog::addActiveJobs(const QStringList& activeJobs) {
	listWidget->addItems(activeJobs);
}


/* FUNCTION: getSelection */
QString JobSelectorDialog::getSelection() {
	return listWidget->selectedItems().first()->text();
}


/* FUNCTION: itemSelected */
void JobSelectorDialog::itemSelected(QListWidgetItem* item) {
	buttonBox->button(QDialogButtonBox::Ok)->setDisabled(false);
}

