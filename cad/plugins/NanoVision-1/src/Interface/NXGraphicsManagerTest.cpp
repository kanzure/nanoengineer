// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXGraphicsManagerTest.h"
#include <fstream>
#include <sstream>
#include <cstdio>

using namespace std;


NXGraphicsManagerTest::NXGraphicsManagerTest()
: QObject(),
  propertiesFileName("NXGraphicsManagerTest.ini"),
  properties(),
  graphicsManager(),
  logger(NULL)
{
}

void NXGraphicsManagerTest::initTestCase(void)
{
	setUpPropertiesFile(propertiesFileName);
	properties.readFromFile(propertiesFileName);
	logger = new NXLogger;
	logger->addHandler(new NXConsoleLogHandler((NXLogLevel)NXLogLevel_Debug));
}


void NXGraphicsManagerTest::cleanupTestCase(void)
{
	remove(propertiesFileName.c_str());
	delete logger;
}


void NXGraphicsManagerTest::setUpPropertiesFile(string const& filename)
{
	ofstream propertiesFile(filename.c_str(), ios::out);
	if(!propertiesFile)
		return;
	
	// propertiesFile << "PluginsSearchPath=plugins/NanoVision-1/lib" << endl;
	propertiesFile << "PluginsSearchPath=../lib" << endl;
	propertiesFile << endl;
	
	propertiesFile << "RenderingEngine.plugin=libNXOpenGLRenderingEngine"
		<< endl;
	// propertiesFile << "RenderingEngine.pluginPath=plugins/NanoVision-1/lib" << endl;
	propertiesFile << "RenderingEngine.pluginPath=../lib" << endl;
	
	propertiesFile << "RenderStyle.0.code=bas" << endl;
	propertiesFile << "RenderStyle.0.name=Ball and Stick" << endl;
	propertiesFile << "RenderStyle.0.plugin=libNXBallAndStickOpenGLRenderer"
		<< endl;
	
	propertiesFile << "RenderStyle.default=bas" << endl;
}


void NXGraphicsManagerTest::loadPluginsTest(void)
{
	string const badRenderStyleCode = "bad-render-style";
	ostringstream msgStream;
	
	bool pluginsLoaded = graphicsManager.loadPlugins(&properties);
	QVERIFY2(pluginsLoaded, "Could not load plugins");
	
	vector<string> const renderStyles = graphicsManager.getRenderStyles();
	msgStream << "Number of render-styles = " << renderStyles.size();
	QVERIFY2(renderStyles.size() == 2,
	         (msgStream.str()+", expected 2").c_str());
	
	NXRendererPlugin *basRenderer = graphicsManager.getRenderer("bas");
	QVERIFY2(basRenderer != NULL, "No 'bas' style renderer found");
	NXRendererPlugin *nilRenderer =
		graphicsManager.getRenderer(badRenderStyleCode);
	QVERIFY2(nilRenderer == NULL,
	         ("Actually found a renderer for style "+badRenderStyleCode).c_str());
	
	string const basStyleName = graphicsManager.getRenderStyleName("bas");
	QVERIFY2(basStyleName == "Ball and Stick",
	         "'bas' render-style's registered name does not match 'Ball and Stick'");
	string const nilStyleName =
		graphicsManager.getRenderStyleName(badRenderStyleCode);
	QVERIFY2(nilStyleName.empty(),
	         (badRenderStyleCode+" render-style-code actually has a non-empty name").c_str());
	
	NXRendererPlugin *defaultRenderer = graphicsManager.getDefaultRenderer();
	QVERIFY2(defaultRenderer == basRenderer, "Bad default renderer");
}

QTEST_MAIN(NXGraphicsManagerTest)
//#include "NXGraphicsManagerTest.moc"

