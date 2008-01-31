// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "ErrorDialog.h"


/* CONSTRUCTOR */
ErrorDialog::ErrorDialog(const QString& message, NXCommandResult* commandResult,
						 QWidget *parent)
		: QDialog(parent), Ui_ErrorDialog() {
		
	setupUi(this);
	errorImageLabel->setPixmap(QPixmap(":/Icons/error.png"));
	
	QString logMessage = message;
	if (commandResult)
		logMessage.append(": ")
			.append(GetNV1ResultCodeString(commandResult)).toStdString();
	NXLOG_SEVERE("", qPrintable(logMessage));
				  
	errorLabel->setText(message);
	if (commandResult)
		textEdit->setText(GetNV1ResultCodeString(commandResult));
	else
		textEdit->setText(message);
}


/* DESTRUCTOR */
ErrorDialog::~ErrorDialog() {
}


