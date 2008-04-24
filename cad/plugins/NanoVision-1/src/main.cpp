// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include <QApplication>

#include "main.h"

static NXEntityManager* createEntityManager(QSettings *const settings);
static NXGraphicsManager* createGraphicsManager(QSettings *const settings);


/* FUNCTION: main */
int main(int argc, char *argv[]) {
	
#ifdef WIN32
	// Create a console window to see stdout
	AllocConsole();
	freopen("conin$", "r", stdin);
	freopen("conout$", "w", stdout);
	freopen("conout$", "w", stderr);
#endif

	Q_INIT_RESOURCE(application);
	QApplication* app = new QApplication(argc, argv);
	
	// Show splashscreen
	//QPixmap pixmap(":/Icons/splashscreen.png");
	//SplashScreen* splash = new SplashScreen(pixmap);
 	//splash->show();

	// Get user settings
	UserSettings* settings = UserSettings::Instance();

	// Start logger
	//
	//splash->showMessage("Starting logger...");
	//splash->repaint();
	int logLevel = 0;
	NXLogger* logger = new NXLogger();
	
	// Console logging
	if (settings->value("Logging/EnableConsoleLogging", true).toBool()) {
		logLevel =
			settings->value("Logging/ConsoleLoggingLevel",
						   NXLogLevel_Debug).toInt();
		logger->addHandler(new NXConsoleLogHandler((NXLogLevel)logLevel));
	}
	
	// File logging
	if (settings->value("Logging/EnableFileLogging", true).toBool()) {
		logLevel =
			settings->value("Logging/FileLoggingLevel",
						   NXLogLevel_Config).toInt();
		QString logFilename = settings->fileName();
		logFilename.chop(3);
		logFilename.append("log");
		logFilename =
			settings->value("Logging/FileLoggingFilename", logFilename)
				.toString();
		NXFileLogHandler* logHandler =
			new NXFileLogHandler(qPrintable(logFilename), (NXLogLevel)logLevel);
		logger->addHandler(logHandler);
	}
	
	// TODO: Emit verbose config level log messages
	NXLOG_CONFIG("main", "spew QSysInfo and OpenGL config information here");
	
	// Dock widget logging
	LogHandlerWidget* logHandlerWidget =
		new LogHandlerWidget(NXLogLevel_Config);
	logger->addHandler(logHandlerWidget);

	// Initialize entity manager and load import/export plugins
	//splash->showMessage("Loading entity manager...");
	//splash->repaint();
	
	NXEntityManager *entityManager = createEntityManager(settings);
	NXGraphicsManager *graphicsManager = createGraphicsManager(settings);
	
	// Create main window
	nv1* mainWindow = new nv1(entityManager, graphicsManager, logHandlerWidget);
	mainWindow->show();
	//splash->repaint();
	
	mainWindow->processCommandLine(argc, argv);
	
	//sleep(1);	
	//splash->finish(mainWindow);
	//delete splash;
	int appReturn = app->exec();
	NXLOG_DEBUG("main", "QApplication::exec() returned.");
	delete app;
	return appReturn;
}


NXEntityManager* createEntityManager(QSettings *const settings)
{
	NXProperties* properties = new NXProperties();
	
	QString pluginsSearchPath =
		settings->value("Miscellaneous/PluginsSearchPath").toString();
	properties->setProperty("PluginsSearchPath", qPrintable(pluginsSearchPath));
	settings->beginGroup("NXEntityManager");
	QStringList keys = settings->allKeys();
	QStringList::const_iterator iter;
	for (iter = keys.constBegin(); iter != keys.constEnd(); iter++)
		properties->setProperty(qPrintable(*iter),
		                        qPrintable(settings->value(*iter).toString()));
	settings->endGroup();
	NXEntityManager* entityManager = new NXEntityManager();
	entityManager->loadDataImportExportPlugins(properties);
	delete properties;
	
	return entityManager;
}


NXGraphicsManager* createGraphicsManager(QSettings *const settings)
{
	NXProperties *properties = new NXProperties();
	
	QString pluginsSearchPath =
		settings->value("Miscellaneous/PluginsSearchPath").toString();
	properties->setProperty("PluginsSearchPath", qPrintable(pluginsSearchPath));
	settings->beginGroup("NXGraphicsManager");
	QStringList keys = settings->allKeys();
	QStringList::const_iterator iter;
	for (iter = keys.constBegin(); iter != keys.constEnd(); iter++)
		properties->setProperty(qPrintable(*iter),
		                        qPrintable(settings->value(*iter).toString()));
	settings->endGroup();
	NXGraphicsManager *graphicsManager = new NXGraphicsManager();
	graphicsManager->loadPlugins(properties);
	delete properties;
	
	return graphicsManager;
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
