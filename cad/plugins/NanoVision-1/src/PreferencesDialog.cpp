// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "PreferencesDialog.h"


/* CONSTRUCTORS */
PreferencesDialog::PreferencesDialog(QWidget *parent)
		: QDialog(parent), Ui_PreferencesDialog() {
		
	setupUi(this);
	
	UserSettings* settings = UserSettings::Instance();
	
	// General/Miscellaneous
	int state = Qt::Checked;
	if (!settings->value("Miscellaneous/SaveWindowSizeOnExit").toBool())
		state = Qt::Unchecked;
	saveWindowSizeCheckBox->setCheckState((Qt::CheckState)state);
	
	// General/Logging
	state = Qt::Checked;
	if (!settings->value("Logging/EnableFileLogging").toBool())
		state = Qt::Unchecked;
	logToFileCheckBoxChanged(state);
	fileLogDetailComboBox->setCurrentIndex
		(settings->value("Logging/FileLoggingLevel").toInt());
	fileLogFilenameLineEdit->setText
		(settings->value("Logging/FileLoggingFilename").toString());
	state = Qt::Checked;
	if (!settings->value("Logging/EnableConsoleLogging").toBool())
		state = Qt::Unchecked;
	logToConsoleCheckBoxChanged(state);
	consoleLogDetailComboBox->setCurrentIndex
		(settings->value("Logging/ConsoleLoggingLevel").toInt());
	
	connect(logToFileCheckBox, SIGNAL(stateChanged(int)),
			this, SLOT(logToFileCheckBoxChanged(int)));
	connect(logToConsoleCheckBox, SIGNAL(stateChanged(int)),
			this, SLOT(logToConsoleCheckBoxChanged(int)));
	connect(fileLogBrowseButton, SIGNAL(clicked(bool)),
			this, SLOT(fileLogBrowseButtonClicked(bool)));
}


/* DESTRUCTOR */
PreferencesDialog::~PreferencesDialog() {
}


/* FUNCTION: accept */
void PreferencesDialog::accept() {
	UserSettings* settings = UserSettings::Instance();

	// General/Miscellaneous
	settings->setValue("Miscellaneous/SaveWindowSizeOnExit",
					   saveWindowSizeCheckBox->checkState() == Qt::Checked);

	// General/Logging
	settings->setValue("Logging/EnableFileLogging",
					   logToFileCheckBox->checkState() == Qt::Checked);
	settings->setValue("Logging/FileLoggingLevel",
					   fileLogDetailComboBox->currentIndex());
	settings->setValue("Logging/FileLoggingFilename",
					   fileLogFilenameLineEdit->text());
	settings->setValue("Logging/EnableConsoleLogging",
					   logToFileCheckBox->checkState() == Qt::Checked);
	settings->setValue("Logging/ConsoleLoggingLevel",
					   fileLogDetailComboBox->currentIndex());

	settings->sync();
	QDialog::accept();
}


/* FUNCTION: logToFileCheckBoxChanged */
void PreferencesDialog::logToFileCheckBoxChanged(int state) {
	if (state == Qt::Checked) {
		logToFileCheckBox->setCheckState(Qt::Checked);
		fileLogDetailLabel->setEnabled(true);
		fileLogDetailComboBox->setEnabled(true);
		fileLogFilenameLineEdit->setEnabled(true);
		fileLogBrowseButton->setEnabled(true);
		
	} else {
		logToFileCheckBox->setCheckState(Qt::Unchecked);
		fileLogDetailLabel->setEnabled(false);
		fileLogDetailComboBox->setEnabled(false);
		fileLogFilenameLineEdit->setEnabled(false);
		fileLogBrowseButton->setEnabled(false);
	}
}


/* FUNCTION: logToConsoleCheckBoxChanged */
void PreferencesDialog::logToConsoleCheckBoxChanged(int state) {
	if (state == Qt::Checked) {
		logToConsoleCheckBox->setCheckState(Qt::Checked);
		consoleLogDetailLabel->setEnabled(true);
		consoleLogDetailComboBox->setEnabled(true);
		
	} else {
		logToConsoleCheckBox->setCheckState(Qt::Unchecked);
		consoleLogDetailLabel->setEnabled(false);
		consoleLogDetailComboBox->setEnabled(false);
	}
}


/* FUNCTION: fileLogBrowseButtonClicked */
void PreferencesDialog::fileLogBrowseButtonClicked(bool checked) {
	QString filename =
		QFileDialog::getSaveFileName(this, tr("Choose a file to log to"),
									 fileLogFilenameLineEdit->text());
	fileLogFilenameLineEdit->setText(filename);
}

