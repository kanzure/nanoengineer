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
	mainWindow.resize(640, 400);
	
	NXOpenGLRenderingEngine *renderingEngine
		= new NXOpenGLRenderingEngine(&mainWindow);
	
	mainWindow.setCentralWidget(renderingEngine);
	mainWindow.show();
	
	NXBallAndStickOpenGLRenderer *renderer =
		new NXBallAndStickOpenGLRenderer(renderingEngine);
	renderingEngine->setRenderer("bas", renderer);
	renderingEngine->setRenderer("def", renderer);
	renderingEngine->initializePlugins();
	
	basRenderData.setRenderStyleCode("bas");
	NXMoleculeSet theMoleculeSet;
	NXDataStoreInfo dataStoreInfo;
	NanorexMMPImportExport importer;
	NXCommandResult const *result =
		importer.importFromFile(&theMoleculeSet, &dataStoreInfo,
		                        "../src/Testing/MMP_TestFiles/H2.mmp", 0,0);
	if(result->getResult() != (int) NX_CMD_SUCCESS) {
		vector<QString> const params = result->getParamVector();
		cerr << "Error: ";
		vector<QString>::const_iterator paramIter;
		for(paramIter = params.begin(); paramIter != params.end(); ++paramIter) {
			cerr << ' ' << qPrintable(*paramIter);
		}
		cerr << endl;
		return 1;
	}
    
	// renderingEngine->clearFrames();
	assert(renderingEngine->getFrameCount() == 0);
	result = renderingEngine->addFrame(&theMoleculeSet);
	assert(result->getResult() == (int) NX_CMD_SUCCESS);
	assert(renderingEngine->getFrameCount() == 1);
	
	// renderingEngine->frames[0]->writeDotGraph(cout);
	
	renderingEngine->setCurrentFrame(0);
	renderingEngine->resetView();
	
	return app.exec();
}


