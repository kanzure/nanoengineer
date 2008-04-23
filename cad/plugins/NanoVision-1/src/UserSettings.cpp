// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "UserSettings.h"

UserSettings* UserSettings::ThisInstance = 0;


/* CONSTRUCTOR */
UserSettings::UserSettings()
#ifdef NX_DEBUG	
: QSettings(QSettings::IniFormat, QSettings::UserScope,
				"Nanorex", "NanoVision-1_d")
#else
: QSettings(QSettings::IniFormat, QSettings::UserScope,
            "Nanorex", "NanoVision-1")
#endif
{
}


/* DESTRUCTOR */
UserSettings::~UserSettings() {
	ThisInstance = 0;
}


/* FUNCTION: Instance */
UserSettings* UserSettings::Instance() {
	if (ThisInstance == 0)
		ThisInstance = new UserSettings();
	return ThisInstance;
}


/* FUNCTION: sync */
void UserSettings::sync() {
	QSettings::sync();
	emit updated();
}

