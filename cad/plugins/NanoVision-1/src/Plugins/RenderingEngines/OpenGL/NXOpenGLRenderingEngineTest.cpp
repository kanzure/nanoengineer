// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#define NX_DEBUG

#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXOpenGLRenderingEngine.h"
#include "../src/Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

using namespace Nanorex;


bool loadMoleculeSetFromFile(char const *const filename,
                             NXMoleculeSet& moleculeSet)
{
    // todo
}

int main(int argc, char *argv[])
{
    // create application and main window
    QApplication app;
    QMainWindow *mainWindow = new QMainWindow;
    app.SetMainWindow(mainWindow);
    NXOpenGLRenderingEngine *renderer = new NXOpenGLRenderingEngine(mainWindow);
    
    // load sample molecule from file
    char const filename[] = "/home/rmanoj/Entertainment/code-expts/openbabel/SF6.gpr";
    NXMoleculeSet theMoleculeSet;
    bool const moleculeLoaded = loadMoleculeSetFromFile(filename, theMoleculeSet);
    if(!moleculeLoaded)
        return 1;
    
    renderer->setRootMoleculeSet(&theMoleculeSet);
    mainWindow->Show();
    return app.exec();
}


