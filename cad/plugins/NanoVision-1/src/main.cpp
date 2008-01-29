// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include <QApplication>

#include "main.h"


/* FUNCTION: main */
int main(int argc, char *argv[]) {
	Q_INIT_RESOURCE(application);
	QApplication* app = new QApplication(argc, argv);
	
	// Show splashscreen
	QPixmap pixmap(":/Icons/splashscreen.png");
	SplashScreen* splash = new SplashScreen(pixmap);
 	splash->show();

	// Get user settings
	QSettings settings(QSettings::IniFormat, QSettings::UserScope,
					   "Nanorex", "NanoVision-1");

	// Start logger
	splash->showMessage("Starting logger...");
	splash->repaint();
	int logLevel = 0;
	NXLogger logger;
	if (settings.value("Logging/EnableConsoleLogging", true).toBool()) {
		logLevel =
			settings.value("Logging/ConsoleLoggingLevel",
						   NXLogLevel_Info).toInt();
		logger.addHandler(new NXConsoleLogHandler((NXLogLevel)logLevel));
	}
	if (settings.value("Logging/EnableFileLogging", true).toBool()) {
		logLevel =
			settings.value("Logging/FileLoggingLevel",
						   NXLogLevel_Info).toInt();
		QString logFilename = settings.fileName();
		logFilename.chop(3);
		logFilename.append("log");
		NXFileLogHandler* logHandler =
			new NXFileLogHandler(qPrintable(logFilename), (NXLogLevel)logLevel);
		logger.addHandler(logHandler);
	}
	
	// Initialize entity manager and load import/export plugins
	splash->showMessage("Loading entity manager...");
	splash->repaint();
	NXProperties* properties = new NXProperties();
	settings.beginGroup("NXEntityManager");
	QStringList keys = settings.allKeys();
	QStringList::const_iterator iter;
	for (iter = keys.constBegin(); iter != keys.constEnd(); iter++)
		properties->setProperty(qPrintable(*iter),
								qPrintable(settings.value(*iter).toString()));
	settings.endGroup();
	NXEntityManager* entityManager = new NXEntityManager();
	entityManager->loadDataImportExportPlugins(properties);
	delete properties;
	
	// Create main window
	nv1* mainWindow = new nv1(entityManager);
	mainWindow->show();
	sleep(1);
	
	splash->finish(mainWindow);
	delete splash;
	int appReturn = app->exec();
	delete app;
	return appReturn;
}


SplashScreen::SplashScreen(const QPixmap &img) : QSplashScreen(img) {
	setMask(
	    QRegion(
	        QPixmap::fromImage(
	            pixmap().toImage().createAlphaMask(
	                Qt::AutoColor | Qt::DiffuseDither | Qt::DiffuseAlphaDither),
	            Qt::AutoColor | Qt::DiffuseDither | Qt::DiffuseAlphaDither)));
}


void SplashScreen::showMessage(const QString &message, int alignment,
							   const QColor &color) {
	QSplashScreen::showMessage(message, alignment, color);
	m_message = message;
}

void SplashScreen::drawContents(QPainter* painter) {
	painter->setBackground(QColor(0, 0, 0, 0));
	painter->setRenderHint(QPainter::Antialiasing);
	painter->setRenderHint(QPainter::SmoothPixmapTransform);
	painter->drawPixmap(0, 0, pixmap());
	painter->drawText(4, height() - 66, m_message);
}
