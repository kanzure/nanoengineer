// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef STRUCTUREGRAPHICSWINDOW_H
#define STRUCTUREGRAPHICSWINDOW_H

#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXGraphicsManager.h"
#include <Nanorex/Interface/NXRenderingEngine.h>

using namespace Nanorex;

#include "DataWindow.h"

/* CLASS: StructureGraphicsWindow */
class StructureGraphicsWindow : public DataWindow
{
    Q_OBJECT;
    
public:
    StructureGraphicsWindow(QWidget *parent,
                            NXGraphicsManager *gm);
    ~StructureGraphicsWindow();
    
	NXCommandResult const *const setMoleculeSet(NXMoleculeSet *theMolSetPtr);
	
	// Mouse-event handlers
// 	void mousePressEvent(QMouseEvent *mouseEvent);
// 	void mouseReleaseEvent(QMouseEvent *mouseEvent);
// 	void mouseMoveEvent(QMouseEvent *mouseEvent);
	
	
private:
	NXGraphicsManager *graphicsManager;
	NXMoleculeSet *molSetPtr;
	NXRenderingEngine *renderingEngine;
};

#if 0
#include "Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h"

inline void StructureGraphicsWindow::mousePressEvent(QMouseEvent *mouseEvent)
{
	NXOpenGLRenderingEngine *openglRenderingEngine =
		dynamic_cast<NXOpenGLRenderingEngine*>(renderingEngine);
	openglRenderingEngine->mousePressEvent(mouseEvent);
}

inline void StructureGraphicsWindow::mouseMoveEvent(QMouseEvent *mouseEvent)
{
	NXOpenGLRenderingEngine *openglRenderingEngine =
		dynamic_cast<NXOpenGLRenderingEngine*>(renderingEngine);
	openglRenderingEngine->mouseMoveEvent(mouseEvent);
}

inline void StructureGraphicsWindow::mouseReleaseEvent(QMouseEvent *mouseEvent)
{
	NXOpenGLRenderingEngine *openglRenderingEngine =
		dynamic_cast<NXOpenGLRenderingEngine*>(renderingEngine);
	openglRenderingEngine->mouseReleaseEvent(mouseEvent);
}
#endif

#endif // STRUCTUREGRAPHICSWINDOW_H
