// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef STRUCTUREGRAPHICSWINDOW_H
#define STRUCTUREGRAPHICSWINDOW_H

#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXGraphicsManager.h"
#include "Nanorex/Interface/NXRenderingEngine.h"
#include "Nanorex/Interface/NXNamedView.h"

using namespace Nanorex;

#include "DataWindow.h"

/* CLASS: StructureGraphicsWindow */
class StructureGraphicsWindow : public DataWindow
{
    Q_OBJECT;
    
public:
    StructureGraphicsWindow(QWidget *parent,
                            NXGraphicsManager *gm,
                            int width = 640, int height = 400);
    ~StructureGraphicsWindow();
    
	NXCommandResult const *const setMoleculeSet(NXMoleculeSet *theMolSetPtr);
	
	void setNamedView(Nanorex::NXNamedView const& view) {
		renderingEngine->setNamedView(view);
	}
	
	void resetView(void) { renderingEngine->resetView(); }
	
	// Mouse-event handlers
 	void mousePressEvent(QMouseEvent *mouseEvent);
 	void mouseReleaseEvent(QMouseEvent *mouseEvent);
 	void mouseMoveEvent(QMouseEvent *mouseEvent);
	
	
private:
	NXGraphicsManager *graphicsManager;
	NXMoleculeSet *molSetPtr;
	NXRenderingEngine *renderingEngine;
};


inline void StructureGraphicsWindow::mousePressEvent(QMouseEvent *mouseEvent) {
	renderingEngine->mousePressEvent(mouseEvent);
}


inline void StructureGraphicsWindow::mouseMoveEvent(QMouseEvent *mouseEvent) {
	renderingEngine->mouseMoveEvent(mouseEvent);
}


inline void StructureGraphicsWindow::mouseReleaseEvent(QMouseEvent *mouseEvent) {
	renderingEngine->mouseReleaseEvent(mouseEvent);
}

#endif // STRUCTUREGRAPHICSWINDOW_H
