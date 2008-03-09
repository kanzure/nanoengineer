// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef MAIN_H
#define MAIN_H

#include <QtGui>
#include <QSettings>
#include <QMainWindow>

#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXProperties.h"
#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "nv1.h"
#include "UserSettings.h"


/* CLASS: SplashScreen */
class SplashScreen : public QSplashScreen {
public:
	SplashScreen(const QPixmap &img);
	void showMessage(const QString &message, int alignment = Qt::AlignLeft,
	    			 const QColor &color = Qt::black);
protected:
	void drawContents(QPainter *p);
	
private:
	QString m_message;
};


#endif
