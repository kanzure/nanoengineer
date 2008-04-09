// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "TrajectoryTestGraphicsManager.h"
#include <Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h>
#include <Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h>

using namespace Nanorex;
using namespace std;


TrajectoryTestGraphicsManager::TrajectoryTestGraphicsManager()
: NXGraphicsManager()
{
	NXOpenGLRenderingEngine *openglRenderingEngine =
		new NXOpenGLRenderingEngine((QWidget*) 0);
	
	renderingEngine = static_cast<NXRenderingEngine*>(openglRenderingEngine);
	
	defaultRenderer = new NXBallAndStickOpenGLRenderer(renderingEngine);
	renderStyleRendererPluginTable.insert(make_pair("bas", defaultRenderer));
	renderStyleNameTable.insert(make_pair("bas", "Ball-and-Stick"));
	// mapping between "def" and defaultRenderer done in newGraphicsInstance()
}


TrajectoryTestGraphicsManager::~TrajectoryTestGraphicsManager()
{
	delete renderingEngine;
	delete defaultRenderer;
}
