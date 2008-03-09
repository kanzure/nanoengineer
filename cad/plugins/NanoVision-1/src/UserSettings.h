// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef USERSETTINGS_H
#define USERSETTINGS_H

#include <QObject>
#include <QSettings>


/* CLASS: UserSettings */
class UserSettings : public QSettings {
	Q_OBJECT

	public:
		UserSettings();
		~UserSettings();

		static UserSettings* Instance();
		
		void sync();
		
	signals:
		void updated();

	private:
		static UserSettings* ThisInstance;
};

#endif
