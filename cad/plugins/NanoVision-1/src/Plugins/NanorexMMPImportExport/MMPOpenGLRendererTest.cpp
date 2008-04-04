// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXDataStoreInfo.h"
#include "Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h"
#include "Plugins/NanorexMMPImportExport/NanorexMMPImportExport.h"
#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

#include <QApplication>
#include <QMainWindow>

using namespace Nanorex;
using namespace std;

int main(int argc, char *argv[])
{
	NXAtomData basRenderData(0);
	
    // create application and main window
	QApplication app(argc, argv);
	QMainWindow mainWindow;
	NXOpenGLRenderingEngine *renderingEngine
		= new NXOpenGLRenderingEngine(&mainWindow);
	mainWindow.setCentralWidget(renderingEngine);
	NXBallAndStickOpenGLRenderer *renderer =
		new NXBallAndStickOpenGLRenderer(renderingEngine);
	renderingEngine->setRenderer("bas", renderer);
	renderingEngine->setRenderer("def", renderer);
	renderingEngine->initializePlugins();
	
	mainWindow.show();
	
	basRenderData.setRenderStyleCode("bas");
	NXMoleculeSet theMoleculeSet;
	NXDataStoreInfo dataStoreInfo;
	NanorexMMPImportExport importer;
	NXCommandResult const *result =
		importer.importFromFile(&theMoleculeSet, &dataStoreInfo,
		                        "../src/Testing/MMP_TestFiles/benzene.mmp", 0,0);
	assert(result->getResult() == (int) NX_CMD_SUCCESS);
    
	renderingEngine->clearFrames();
	assert(renderingEngine->getFrameCount() == 0);
	result = renderingEngine->addFrame(&theMoleculeSet);
	assert(result->getResult() == (int) NX_CMD_SUCCESS);
	assert(renderingEngine->getFrameCount() == 1);
	renderingEngine->setCurrentFrame(0);
	
	return app.exec();
}


