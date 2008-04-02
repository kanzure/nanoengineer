// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_GRAPHICSMANAGERTEST_H
#define NX_GRAPHICSMANAGERTEST_H

#include <string>

#include <QtGui>
#include <QtTest/QtTest>

#include "Nanorex/Interface/NXGraphicsManager.h"

using namespace Nanorex;
using namespace OpenBabel;

class NXGraphicsManagerTest : public QObject {

	Q_OBJECT;
	
public:
	NXGraphicsManagerTest();
	virtual ~NXGraphicsManagerTest() {}
	
private:
	string propertiesFileName;
	NXProperties properties;
	NXGraphicsManager graphicsManager;
	NXLogger *logger;
	
	void setUpPropertiesFile(std::string const& filename);

private slots:
	
	void initTestCase(void);
	void cleanupTestCase(void);
	
	void loadPluginsTest(void);
	
};


#endif // NX_GRAPHICSMANAGERTEST_H
