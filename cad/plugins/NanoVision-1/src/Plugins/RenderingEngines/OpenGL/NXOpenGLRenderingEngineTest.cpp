// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXMoleculeSet.h"
#include "NXOpenGLRenderingEngine.h"
#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

#include <QApplication>
#include <QMainWindow>

#include <cmath>

using namespace Nanorex;
using namespace std;

void bond(OBMol *molPtr, OBAtom *atom1Ptr, OBAtom *atom2Ptr, int bondOrder)
{
    OBBond *bondPtr = molPtr->NewBond();
    bondPtr->SetBegin(atom1Ptr);
    bondPtr->SetEnd(atom2Ptr);
    atom1Ptr->AddBond(bondPtr);
    atom2Ptr->AddBond(bondPtr);
    bondPtr->SetBondOrder(bondOrder);
}

void makeCH4(OBMol *molPtr)
{
    double const sqrt3 = sqrt(3.0);
    double const sqrt_2by3 = sqrt(2.0/3.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(0.0, sqrt3 - 1.0/sqrt3, 0.0);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(-1.0, -1.0/sqrt3, 0.0);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(1.0, -1.0/sqrt3, 0.0);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(0.0, 0.0, 2.0*sqrt_2by3);
    
    OBAtom *C = molPtr->NewAtom();
    C->SetAtomicNum(6);
    C->SetVector(0.0, 0.0, 0.0);
    
    bond(molPtr, C, H1, 1);
    bond(molPtr, C, H2, 1);
    bond(molPtr, C, H3, 1);
    bond(molPtr, C, H4, 1);
}


/*bool loadMoleculeSetFromFile(char const *const filename,
                             NXMoleculeSet& moleculeSet)
{
    // todo
}
*/

int main(int argc, char *argv[])
{
    // create application and main window
    QApplication app(argc, argv);
    QMainWindow mainWindow;
    NXOpenGLRenderingEngine *renderingEngine
        = new NXOpenGLRenderingEngine(&mainWindow);
    mainWindow.setCentralWidget(renderingEngine);
    NXBallAndStickOpenGLRenderer *renderer =
        new NXBallAndStickOpenGLRenderer;
    renderingEngine->setPlugin(renderer);
    
    NXMoleculeSet theMoleculeSet;
    OBMol *molPtr = theMoleculeSet.newMolecule();
    makeCH4(molPtr);
    
    mainWindow.resize(1000, 600);
    mainWindow.show();
    renderingEngine->setRootMoleculeSet(&theMoleculeSet);
    return app.exec();
}


