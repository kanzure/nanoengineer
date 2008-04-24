// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "StructureGraphicsWindow.h"

/* CONSTRUCTOR */
StructureGraphicsWindow::
StructureGraphicsWindow(QWidget *parent,
                        NXGraphicsManager *theGraphicsManager,
                        int width, int height)
: DataWindow(parent),
graphicsManager(theGraphicsManager),
molSetPtr(NULL),
renderingEngine(NULL)
{
	renderingEngine = graphicsManager->newGraphicsInstance(this);
	QWidget *renderingEngineWidget = renderingEngine->asQWidget();
	QLayout *thisWidgetLayout = layout();
	if(thisWidgetLayout == (QLayout*) 0) {
		thisWidgetLayout = new QHBoxLayout(this);
		thisWidgetLayout->setSpacing(0);
	}
	thisWidgetLayout->addWidget(renderingEngineWidget);
	resize(width, height);
	update();
}


/* DESTRUCTOR */
StructureGraphicsWindow::~StructureGraphicsWindow()
{
	if(renderingEngine != (NXRenderingEngine*) NULL)
		delete renderingEngine;
	renderingEngine = NULL;
}


NXCommandResult const *const
StructureGraphicsWindow::setMoleculeSet(NXMoleculeSet *theMolSetPtr)
{
	assert(renderingEngine->getFrameCount() == 0);
	NXCommandResult const *const result =
		renderingEngine->addFrame(theMolSetPtr);
	if(result->getResult() == (int) NX_CMD_SUCCESS) {
		molSetPtr = theMolSetPtr;
		renderingEngine->setCurrentFrame(0);
		// renderingEngine->resetView();
	}
	return result;
}
