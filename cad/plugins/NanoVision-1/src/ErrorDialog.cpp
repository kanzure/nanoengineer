// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "ErrorDialog.h"


/* CONSTRUCTOR */
ErrorDialog::ErrorDialog(QString message, NXCommandResult* commandResult,
						 QWidget *parent)
		: QDialog(parent), Ui_ErrorDialog() {
		
	setupUi(this);
	errorImageLabel->setPixmap(QPixmap(":/Icons/error.png"));
	
	NXLOG_SEVERE("",
				 (message + ": " +
				  GetNV1ResultCodeString(commandResult)).toStdString());
	errorLabel->setText(message);
	textEdit->setText(GetNV1ResultCodeString(commandResult));
}


/* DESTRUCTOR */
ErrorDialog::~ErrorDialog() {
}


