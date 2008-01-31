// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "ErrorDialog.h"


/* CONSTRUCTORS */
ErrorDialog::ErrorDialog(const QString& shortMessage,
						 NXCommandResult* commandResult,
						 QWidget *parent)
		: QDialog(parent), Ui_ErrorDialog() {
		
	setupUi(this);
	errorImageLabel->setPixmap(QPixmap(":/Icons/error.png"));
	
	QString longMessage;
	if (commandResult)
		longMessage = GetNV1ResultCodeString(commandResult);
	else
		longMessage = shortMessage;
		
	setMessage(shortMessage, longMessage);
}
ErrorDialog::ErrorDialog(const QString& shortMessage,
						 const QString& longMessage,
						 QWidget *parent)
		: QDialog(parent), Ui_ErrorDialog() {
		
	setupUi(this);
	errorImageLabel->setPixmap(QPixmap(":/Icons/error.png"));
				  
	setMessage(shortMessage, longMessage);
}


/* DESTRUCTOR */
ErrorDialog::~ErrorDialog() {
}


/* FUNCTION: setMessage */
void ErrorDialog::setMessage(const QString& shortMessage,
							 const QString& longMessage) {
	
	QString logMessage = shortMessage;
	if (shortMessage != longMessage)
		logMessage.append(": ").append(longMessage);
	NXLOG_SEVERE("", qPrintable(logMessage));
	
	errorLabel->setText(shortMessage);
	textEdit->setText(longMessage);
}
