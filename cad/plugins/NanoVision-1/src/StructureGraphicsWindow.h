// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef STRUCTUREGRAPHICSWINDOW_H
#define STRUCTUREGRAPHICSWINDOW_H

// #include <Nanorex/Interface/NXRenderingEngine.h>
#include "Nanorex/Interface/NXEntityManager.h"
#include "Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h"
using namespace Nanorex;

#include "DataWindow.h"

/* CLASS: StructureGraphicsWindow */
class StructureGraphicsWindow
: public DataWindow,
  public NXOpenGLRenderingEngine
{
    Q_OBJECT;
    
public:
    StructureGraphicsWindow(QWidget *parent=0);
    ~StructureGraphicsWindow();
    
    void setEntityManager(NXEntityManager *theEntityManager)
    { entityManager = theEntityManager; }
    
private:
    NXEntityManager *entityManager;
};

#endif // STRUCTUREGRAPHICSWINDOW_H
