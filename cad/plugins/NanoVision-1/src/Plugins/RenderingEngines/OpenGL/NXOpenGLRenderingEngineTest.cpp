// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXMoleculeSet.h"
#include "NXOpenGLRenderingEngine.h"
#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

#include <QApplication>
#include <QMainWindow>

#include <cmath>

using namespace Nanorex;
using namespace std;

void makeSF6(OBMol *molPtr);
void makeCO2(OBMol *molPtr);
void makeH2O(OBMol *molPtr);
void makeNO2(OBMol *molPtr);
void makeCH4(OBMol *molPtr);
void makeNH3(OBMol *molPtr);
void makeC2H2(OBMol *molPtr);
void makeC2H4(OBMol *molPtr);
void makeC2H6(OBMol *molPtr);

void makeTheMoleculeSet(NXMoleculeSet& theMoleculeSet);
void translateMolecule(OBMol *molPtr, vector3 const& delta);

double const SCALE = 3.0;

void bond(OBMol *molPtr, OBAtom *atom1Ptr, OBAtom *atom2Ptr, int bondOrder)
{
    OBBond *bondPtr = molPtr->NewBond();
    bondPtr->SetBegin(atom1Ptr);
    bondPtr->SetEnd(atom2Ptr);
    atom1Ptr->AddBond(bondPtr);
    atom2Ptr->AddBond(bondPtr);
    bondPtr->SetBondOrder(bondOrder);
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
    // makeC2H6(molPtr);
    makeTheMoleculeSet(theMoleculeSet);
    
    mainWindow.resize(1000, 600);
    mainWindow.show();
    renderingEngine->setRootMoleculeSet(&theMoleculeSet);
    return app.exec();
}


void makeTheMoleculeSet(NXMoleculeSet& theMoleculeSet)
{
    OBMol *SF6 = theMoleculeSet.newMolecule();
    makeSF6(SF6);
    
    NXMoleculeSet *triatomics = new NXMoleculeSet;
    theMoleculeSet.addChild(triatomics);
    
    OBMol *CO2 = triatomics->newMolecule();
    makeCO2(CO2);
    translateMolecule(CO2, vector3(SCALE*3.0, SCALE*3.0, SCALE*3.0));
    
    OBMol *H2O = triatomics->newMolecule();
    makeH2O(H2O);
    translateMolecule(H2O, vector3(SCALE*3.0, SCALE*3.0, SCALE*-3.0));
    
    OBMol *NO2 = triatomics->newMolecule();
    makeNO2(NO2);
    translateMolecule(NO2, vector3(SCALE*3.0, SCALE*-3.0, SCALE*3.0));
    
    NXMoleculeSet *pyramidal = new NXMoleculeSet;
    theMoleculeSet.addChild(pyramidal);
    
    OBMol *NH3 = pyramidal->newMolecule();
    makeNH3(NH3);
    translateMolecule(NH3, vector3(SCALE*3.0, SCALE*-3.0, SCALE*-3.0));
    
    OBMol *CH4 = pyramidal->newMolecule();
    makeCH4(CH4);
    translateMolecule(CH4, vector3(SCALE*-3.0, SCALE*3.0, SCALE*3.0));
    
    NXMoleculeSet *hydrocarbons = new NXMoleculeSet;
    // ok, don't think too much ... this is only a test
    triatomics->addChild(hydrocarbons);
    
    OBMol *C2H2 = hydrocarbons->newMolecule();
    makeC2H2(C2H2);
    translateMolecule(C2H2, vector3(SCALE*-3.0, SCALE*3.0, SCALE*-3.0));
    
    OBMol *C2H4 = hydrocarbons->newMolecule();
    makeC2H4(C2H4);
    translateMolecule(C2H4, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*3.0));
    
    OBMol *C2H6 = hydrocarbons->newMolecule();
    makeC2H6(C2H6);
    translateMolecule(C2H6, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*-3.0));
}


void translateMolecule(OBMol *molPtr, vector3 const& delta)
{
    OBAtomIterator atomIter;
    OBAtom *atomPtr = NULL;
    for(atomPtr = molPtr->BeginAtom(atomIter);
        atomPtr != NULL;
        atomPtr = molPtr->NextAtom(atomIter))
    {
        vector3 atomPos = atomPtr->GetVector();
        atomPos += delta;
        atomPtr->SetVector(atomPos);
    }
}


void makeCH4(OBMol *molPtr)
{
    OBAtom *C = molPtr->NewAtom();
    C->SetAtomicNum(6);
    C->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(SCALE*1.0, SCALE*1.0, SCALE*1.0);
    bond(molPtr, C, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(SCALE*-1.0, SCALE*-1.0, SCALE*1.0);
    bond(molPtr, C, H2, 1);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(SCALE*-1.0, SCALE*1.0, SCALE*-1.0);
    bond(molPtr, C, H3, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(SCALE*1.0, SCALE*-1.0, SCALE*-1.0);
    bond(molPtr, C, H4, 1);
}


void makeNH3(OBMol *molPtr)
{
    // double const SCALE = 5.0;
    double const THETA = 120.0 * M_PI/180.0;
    double sinTheta = 0.0, cosTheta = 0.0;
#ifdef _GNU_SOURCE
    sincos(THETA, &sinTheta, &cosTheta);
#else
    sinTheta = sin(THETA);
    cosTheta = cos(THETA);
#endif
    
    OBAtom *N = molPtr->NewAtom();
    N->SetAtomicNum(7);
    N->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(0.0, SCALE*-1.0, SCALE*1.0);
    bond(molPtr, N, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(SCALE*sinTheta, SCALE*-1.0, SCALE*cosTheta);
    bond(molPtr, N, H2, 1);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(SCALE*-sinTheta, SCALE*-1.0, SCALE*cosTheta);
    bond(molPtr, N, H3, 1);
}

void makeSF6(OBMol *molPtr)
{
    // double const SCALE = 5.0;
    
    OBAtom *S = molPtr->NewAtom();
    S->SetAtomicNum(16);
    S->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *F1 = molPtr->NewAtom();
    F1->SetAtomicNum(9);
    F1->SetVector(SCALE*1.0, 0.0, 0.0);
    bond(molPtr, S, F1, 1);
    
    OBAtom *F2 = molPtr->NewAtom();
    F2->SetAtomicNum(9);
    F2->SetVector(SCALE*-1.0, 0.0, 0.0);
    bond(molPtr, S, F2, 1);
    
    OBAtom *F3 = molPtr->NewAtom();
    F3->SetAtomicNum(9);
    F3->SetVector(0.0, SCALE*1.0, 0.0);
    bond(molPtr, S, F3, 1);
    
    OBAtom *F4 = molPtr->NewAtom();
    F4->SetAtomicNum(9);
    F4->SetVector(0.0, SCALE*-1.0, 0.0);
    bond(molPtr, S, F4, 1);
    
    OBAtom *F5 = molPtr->NewAtom();
    F5->SetAtomicNum(9);
    F5->SetVector(0.0, 0.0, SCALE*1.0);
    bond(molPtr, S, F5, 1);
    
    OBAtom *F6 = molPtr->NewAtom();
    F6->SetAtomicNum(9);
    F6->SetVector(0.0, 0.0, SCALE*-1.0);
    bond(molPtr, S, F6, 1);
}


void makeH2O(OBMol *molPtr)
{
    // double const SCALE = 5.0;
    double const THETA = (180.0-104.45)/2 * M_PI/180.0;
    double sinTheta = 0.0, cosTheta = 0.0;
#ifdef _GNU_SOURCE
    sincos(THETA, &sinTheta, &cosTheta);
#else
    sinTheta = sin(THETA);
    cosTheta = cos(THETA);
#endif
    
    OBAtom *O = molPtr->NewAtom();
    O->SetAtomicNum(8);
    O->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(SCALE*cosTheta, SCALE*-sinTheta, 0.0);
    bond(molPtr, O, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(SCALE*-cosTheta, SCALE*-sinTheta, 0.0);
    bond(molPtr, O, H2, 1);
}


void makeNO2(OBMol *molPtr)
{
    // double const SCALE = 5.0;
    double const THETA = (180.0-134.3)/2 * M_PI/180.0;
    double sinTheta = 0.0, cosTheta = 0.0;
#ifdef _GNU_SOURCE
    sincos(THETA, &sinTheta, &cosTheta);
#else
    sinTheta = sin(THETA);
    cosTheta = cos(THETA);
#endif
    
    OBAtom *N = molPtr->NewAtom();
    N->SetAtomicNum(7);
    N->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *O1 = molPtr->NewAtom();
    O1->SetAtomicNum(8);
    O1->SetVector(SCALE*cosTheta, SCALE*-sinTheta, 0.0);
    bond(molPtr, N, O1, 1);
    
    OBAtom *O2 = molPtr->NewAtom();
    O2->SetAtomicNum(8);
    O2->SetVector(SCALE*-cosTheta, SCALE*-sinTheta, 0.0);
    bond(molPtr, N, O2, 1);
}


void makeCO2(OBMol *molPtr)
{
    OBAtom *C = molPtr->NewAtom();
    C->SetAtomicNum(6);
    C->SetVector(0.0, 0.0, 0.0);
    
    OBAtom *O1 = molPtr->NewAtom();
    O1->SetAtomicNum(8);
    O1->SetVector(SCALE*1.0, SCALE*1.0, SCALE*1.0);
    bond(molPtr, C, O1, 2);
    
    OBAtom *O2 = molPtr->NewAtom();
    O2->SetAtomicNum(8);
    O2->SetVector(SCALE*-1.0, SCALE*-1.0, SCALE*-1.0);
    bond(molPtr, C, O2, 2);
}


void makeC2H2(OBMol *molPtr)
{
    OBAtom *C1 = molPtr->NewAtom();
    C1->SetAtomicNum(6);
    C1->SetVector(0.0, SCALE*0.5, 0.0);
    
    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(0.0, SCALE*-0.5, 0.0);
    bond(molPtr, C1, C2, 3);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(0.0, SCALE*1.5, 0.0);
    bond(molPtr, C1, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(0.0, SCALE*-1.5, 0.0);
    bond(molPtr, C2, H2, 1);
}


void makeC2H4(OBMol *molPtr)
{
    OBAtom *C1 = molPtr->NewAtom();
    C1->SetAtomicNum(6);
    C1->SetVector(0.0, SCALE*0.5, 0.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(0.0, SCALE*1.0, SCALE*0.5);
    bond(molPtr, C1, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(0.0, SCALE*1.0, SCALE*-0.5);
    bond(molPtr, C1, H2, 1);

    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(0.0, SCALE*-0.5, 0.0);
    bond(molPtr, C1, C2, 2);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(0.0, SCALE*-1.0, SCALE*0.5);
    bond(molPtr, C2, H3, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(0.0, SCALE*-1.0, SCALE*-0.5);
    bond(molPtr, C2, H4, 1);
}


void makeC2H6(OBMol *molPtr)
{
    double const THETA = 120.0 * M_PI / 180.0;
    double sinTheta = 0.0, cosTheta = 0.0;
#ifdef _GNU_SOURCE
    sincos(THETA, &sinTheta, &cosTheta);
#else
    sinTheta = sin(THETA);
    cosTheta = cos(THETA);
#endif
    
    OBAtom *C1 = molPtr->NewAtom();
    C1->SetAtomicNum(6);
    C1->SetVector(0.0, SCALE*0.5, 0.0);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(0.0, SCALE*1.0, SCALE*0.5);
    bond(molPtr, C1, H1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(SCALE*0.5*sinTheta, SCALE*1.0, SCALE*0.5*cosTheta);
    bond(molPtr, C1, H2, 1);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(SCALE*0.5*-sinTheta, SCALE*1.0, SCALE*0.5*cosTheta);
    bond(molPtr, C1, H3, 1);
    
    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(0.0, SCALE*-0.5, 0.0);
    bond(molPtr, C1, C2, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(0.0, SCALE*-1.0, SCALE*-0.5);
    bond(molPtr, C2, H4, 1);
    
    OBAtom *H5 = molPtr->NewAtom();
    H5->SetAtomicNum(1);
    H5->SetVector(SCALE*0.5*sinTheta, SCALE*-1.0, SCALE*0.5*-cosTheta);
    bond(molPtr, C2, H5, 1);
    
    OBAtom *H6 = molPtr->NewAtom();
    H6->SetAtomicNum(1);
    H6->SetVector(SCALE*0.5*-sinTheta, SCALE*-1.0, SCALE*0.5*-cosTheta);
    bond(molPtr, C2, H6, 1);
}


