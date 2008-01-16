// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include <QApplication>

#include "nv1.h"


/* FUNCTION: main */
int main(int argc, char *argv[]) {
	Q_INIT_RESOURCE(application);
	QApplication app(argc, argv);
	nv1 mainWindow;
	mainWindow.show();
	return app.exec();
}
