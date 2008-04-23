// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXAtomData.h"
#include "NXOpenGLRenderingEngine.h"
#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

#include <QApplication>
#include <QMainWindow>

#include <cmath>

using namespace Nanorex;
using namespace std;

#ifdef GENERATE_MMP
#include <map>

map<OBAtom*,int> atomIdxMap;
int atomIdx = 0;
#endif


NXAtomData basRenderData(0);

NXMoleculeSet* newMoleculeSet(NXMoleculeSet *const parent);

void makeSF6(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeCO2(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeH2O(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeNO2(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeCH4(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeNH3(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeC2H2(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeC2H4(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeC2H6(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));
void makeC6H6(OBMol *molPtr, vector3 const& delta = vector3(0.0,0.0,0.0));

void makeTheMoleculeSet(NXMoleculeSet *theMoleculeSet);
// void translateMolecule(OBMol *molPtr, vector3 const& delta);
void setRenderStyleBAS(OBMol *molPtr);

// MMP helpers - defined at the end
void writemmp_group(string const& name);
void writemmp_egroup(string const& name);
void writemmp_mol(string const& name);
void writemmp_atom(OBAtom *const atomPtr);
void writemmp_bond(OBBond *const bondPtr);


double const SCALE = 1.0;

/// atom1Ptr must be the most-recently created
void bond(OBMol *molPtr, OBAtom *atom1Ptr, OBAtom *atom2Ptr, int bondOrder)
{
    OBBond *bondPtr = molPtr->NewBond();
    bondPtr->SetBegin(atom1Ptr);
    bondPtr->SetEnd(atom2Ptr);
    atom1Ptr->AddBond(bondPtr);
    atom2Ptr->AddBond(bondPtr);
    bondPtr->SetBondOrder(bondOrder);
	writemmp_bond(bondPtr);
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
		new NXBallAndStickOpenGLRenderer(renderingEngine);
    renderingEngine->setRenderer("bas", renderer);
	renderingEngine->initializePlugins();
	
	basRenderData.setRenderStyleCode("bas");
    NXMoleculeSet theMoleculeSet;
    // OBMol *molPtr = theMoleculeSet.newMolecule();
    // makeC2H6(molPtr);
    makeTheMoleculeSet(&theMoleculeSet);
    
    mainWindow.resize(1000, 600);
    mainWindow.show();
	// renderingEngine->clearFrames();
    renderingEngine->addFrame(&theMoleculeSet);
	renderingEngine->setCurrentFrame(0);
	renderingEngine->resetView();
	mainWindow.update();
    int result = app.exec();
	return result;
}


NXMoleculeSet* newMoleculeSet(NXMoleculeSet *const parent)
{
	NXMoleculeSet *molSetPtr = new NXMoleculeSet;
	assert(molSetPtr != NULL);
	parent->addChild(molSetPtr);
	return molSetPtr;
}


void makeTheMoleculeSet(NXMoleculeSet* theMoleculeSet)
{
	writemmp_group("The Molecule Set");
	
	OBMol *C6H6 = theMoleculeSet->newMolecule();
	makeC6H6(C6H6);
	setRenderStyleBAS(C6H6);	

	OBMol *SF6 = theMoleculeSet->newMolecule();
	makeSF6(SF6);
	setRenderStyleBAS(SF6);
	
	NXMoleculeSet *hydrocarbonsAndTriatomics = newMoleculeSet(theMoleculeSet);
	writemmp_group("Hydrocarbons and Triatomics");

	
	NXMoleculeSet *triatomics = newMoleculeSet(hydrocarbonsAndTriatomics);
	writemmp_group("Triatomics");
	
    OBMol *H2O = triatomics->newMolecule();
	makeH2O(H2O, vector3(SCALE*3.0, SCALE*3.0, SCALE*-3.0));
	// translateMolecule(H2O, vector3(SCALE*3.0, SCALE*3.0, SCALE*-3.0));
	setRenderStyleBAS(H2O);
	
	NXMoleculeSet *dioxides = newMoleculeSet(triatomics);
	writemmp_group("Dioxides");
	
	OBMol *CO2 = dioxides->newMolecule();
	makeCO2(CO2, vector3(SCALE*3.0, SCALE*3.0, SCALE*3.0));
	// translateMolecule(CO2, vector3(SCALE*3.0, SCALE*3.0, SCALE*3.0));
	setRenderStyleBAS(CO2);
	
	OBMol *NO2 = dioxides->newMolecule();
	makeNO2(NO2, vector3(SCALE*3.0, SCALE*-3.0, SCALE*3.0));
	// translateMolecule(NO2, vector3(SCALE*3.0, SCALE*-3.0, SCALE*3.0));
	setRenderStyleBAS(NO2);
	
	writemmp_egroup("Dioxides");
	writemmp_egroup("Triatomics");
	
	
	NXMoleculeSet *hydrocarbons = newMoleculeSet(hydrocarbonsAndTriatomics);
	writemmp_group("Hydrocarbons");

	NXMoleculeSet *paraffins = newMoleculeSet(hydrocarbons);
	writemmp_group("Paraffins");
	
	OBMol *C2H6 = paraffins->newMolecule();
	makeC2H6(C2H6, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*-3.0));
	// translateMolecule(C2H6, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*-3.0));
	setRenderStyleBAS(C2H6);
	
	writemmp_egroup("Paraffins");
	
	NXMoleculeSet *olefins = newMoleculeSet(hydrocarbons);
	writemmp_group("Olefins");

	
	NXMoleculeSet *alkenes = newMoleculeSet(olefins);
	writemmp_group("Alkenes");
	
	OBMol *C2H4 = alkenes->newMolecule();
	makeC2H4(C2H4, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*3.0));
	// translateMolecule(C2H4, vector3(SCALE*-3.0, SCALE*-3.0, SCALE*3.0));
	setRenderStyleBAS(C2H4);
	
	writemmp_egroup("Alkenes");
	
	NXMoleculeSet *alkynes = newMoleculeSet(olefins);
	writemmp_group("Alkynes");
	
	OBMol *C2H2 = alkynes->newMolecule();
	makeC2H2(C2H2, vector3(SCALE*-3.0, SCALE*3.0, SCALE*-3.0));
	// translateMolecule(C2H2, vector3(SCALE*-3.0, SCALE*3.0, SCALE*-3.0));
	setRenderStyleBAS(C2H2);
	
	writemmp_egroup("Alkynes");
	writemmp_egroup("Olefins");
	writemmp_egroup("Hydrocarbons");
	
	writemmp_egroup("Hydrocarbons and Triatomics");
	
	NXMoleculeSet *pyramidal = newMoleculeSet(theMoleculeSet);
	writemmp_group("Pyramidal");
	
	OBMol *NH3 = pyramidal->newMolecule();
	makeNH3(NH3, vector3(SCALE*3.0, SCALE*-3.0, SCALE*-3.0));
	// translateMolecule(NH3, vector3(SCALE*3.0, SCALE*-3.0, SCALE*-3.0));
	setRenderStyleBAS(NH3);
	
	OBMol *CH4 = pyramidal->newMolecule();
	makeCH4(CH4, vector3(SCALE*-3.0, SCALE*3.0, SCALE*3.0));
	// translateMolecule(CH4, vector3(SCALE*-3.0, SCALE*3.0, SCALE*3.0));
	setRenderStyleBAS(CH4);
	
	writemmp_egroup("Pyramidal");
	writemmp_egroup("The Molecule Set");
}


#if 0
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
#endif


void setRenderStyleBAS(OBMol *molPtr)
{
	OBAtomIterator atomIter;
	OBAtom *atomPtr = NULL;
	for(atomPtr = molPtr->BeginAtom(atomIter);
	    atomPtr != NULL;
	    atomPtr = molPtr->NextAtom(atomIter))
	{
		NXAtomData *atomDataPtr = new NXAtomData(basRenderData);
		atomPtr->SetData(atomDataPtr);
	}
}


void makeCH4(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("CH4");
	writemmp_mol("Methane");
    OBAtom *C = molPtr->NewAtom();
    C->SetAtomicNum(6);
	C->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(C);
	
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
	H1->SetVector(vector3(SCALE*1.0, SCALE*1.0, SCALE*1.0) + delta);
	writemmp_atom(H1);
    bond(molPtr, H1, C, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
	H2->SetVector(vector3(SCALE*-1.0, SCALE*-1.0, SCALE*1.0) + delta);
	writemmp_atom(H2);
    bond(molPtr, H2, C, 1);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
	H3->SetVector(vector3(SCALE*-1.0, SCALE*1.0, SCALE*-1.0) + delta);
	writemmp_atom(H3);
	bond(molPtr, H3, C, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
	H4->SetVector(vector3(SCALE*1.0, SCALE*-1.0, SCALE*-1.0) + delta);
	writemmp_atom(H4);
	bond(molPtr, H4, C, 1);
}


void makeNH3(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("NH3");
	writemmp_mol("Ammonia");
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
    N->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(N);
	
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(vector3(0.0, SCALE*-1.0, SCALE*1.0) + delta);
	writemmp_atom(H1);
	bond(molPtr, H1, N, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(vector3(SCALE*sinTheta, SCALE*-1.0, SCALE*cosTheta) + delta);
	writemmp_atom(H2);
	bond(molPtr, H2, N, 1);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(vector3(SCALE*-sinTheta, SCALE*-1.0, SCALE*cosTheta) + delta);
	writemmp_atom(H3);
	bond(molPtr, H3, N, 1);
}

void makeSF6(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("SF6");
	writemmp_mol("Sulphur Hexafluoride");
    // double const SCALE = 5.0;
    
    OBAtom *S = molPtr->NewAtom();
    S->SetAtomicNum(16);
    S->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(S);
	
    OBAtom *F1 = molPtr->NewAtom();
    F1->SetAtomicNum(9);
    F1->SetVector(vector3(SCALE*1.0, 0.0, 0.0) + delta);
	writemmp_atom(F1);
	bond(molPtr, F1, S, 1);
    
    OBAtom *F2 = molPtr->NewAtom();
    F2->SetAtomicNum(9);
    F2->SetVector(vector3(SCALE*-1.0, 0.0, 0.0) + delta);
	writemmp_atom(F2);
	bond(molPtr, F2, S, 1);
    
    OBAtom *F3 = molPtr->NewAtom();
    F3->SetAtomicNum(9);
    F3->SetVector(vector3(0.0, SCALE*1.0, 0.0) + delta);
	writemmp_atom(F3);
	bond(molPtr, F3, S, 1);
    
    OBAtom *F4 = molPtr->NewAtom();
    F4->SetAtomicNum(9);
    F4->SetVector(vector3(0.0, SCALE*-1.0, 0.0) + delta);
	writemmp_atom(F4);
	bond(molPtr, F4, S, 1);
    
    OBAtom *F5 = molPtr->NewAtom();
    F5->SetAtomicNum(9);
    F5->SetVector(vector3(0.0, 0.0, SCALE*1.0) + delta);
	writemmp_atom(F5);
	bond(molPtr, F5, S, 1);
    
    OBAtom *F6 = molPtr->NewAtom();
    F6->SetAtomicNum(9);
    F6->SetVector(vector3(0.0, 0.0, SCALE*-1.0) + delta);
	writemmp_atom(F6);
	bond(molPtr, F6, S, 1);
}


void makeH2O(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("H2O");
	writemmp_mol("Water");
	
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
    O->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(O);
	
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(vector3(SCALE*cosTheta, SCALE*-sinTheta, 0.0) + delta);
	writemmp_atom(H1);
	bond(molPtr, H1, O, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(vector3(SCALE*-cosTheta, SCALE*-sinTheta, 0.0) + delta);
	writemmp_atom(H2);
	bond(molPtr, H2, O, 1);
}


void makeNO2(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("NO2");
	writemmp_mol("Nitrous Oxide");
	
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
    N->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(N);
	
    OBAtom *O1 = molPtr->NewAtom();
    O1->SetAtomicNum(8);
    O1->SetVector(vector3(SCALE*cosTheta, SCALE*-sinTheta, 0.0) + delta);
	writemmp_atom(O1);
	bond(molPtr, O1, N, 1);
    
    OBAtom *O2 = molPtr->NewAtom();
    O2->SetAtomicNum(8);
    O2->SetVector(vector3(SCALE*-cosTheta, SCALE*-sinTheta, 0.0) + delta);
	writemmp_atom(O2);
	bond(molPtr, O2, N, 1);
}


void makeCO2(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("CO2");
	writemmp_mol("Carbon dioxide");
	
    OBAtom *C = molPtr->NewAtom();
    C->SetAtomicNum(6);
    C->SetVector(vector3(0.0, 0.0, 0.0) + delta);
	writemmp_atom(C);
	
    OBAtom *O1 = molPtr->NewAtom();
    O1->SetAtomicNum(8);
    O1->SetVector(vector3(SCALE*1.0, SCALE*1.0, SCALE*1.0) + delta);
	writemmp_atom(O1);
	bond(molPtr, O1, C, 2);
    
    OBAtom *O2 = molPtr->NewAtom();
    O2->SetAtomicNum(8);
    O2->SetVector(vector3(SCALE*-1.0, SCALE*-1.0, SCALE*-1.0) + delta);
	writemmp_atom(O2);
	bond(molPtr, O2, C, 2);
}


void makeC2H2(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("C2H2");
	writemmp_mol("Ethyne");
	
    OBAtom *C1 = molPtr->NewAtom();
    C1->SetAtomicNum(6);
    C1->SetVector(vector3(0.0, SCALE*0.5, 0.0) + delta);
	writemmp_atom(C1);
	
    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(vector3(0.0, SCALE*-0.5, 0.0) + delta);
	writemmp_atom(C2);
	bond(molPtr, C2, C1, 3);
    
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(vector3(0.0, SCALE*1.5, 0.0) + delta);
	writemmp_atom(H1);
	bond(molPtr, H1, C1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(vector3(0.0, SCALE*-1.5, 0.0) + delta);
	writemmp_atom(H2);
	bond(molPtr, H2, C2, 1);
}


void makeC2H4(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("C2H4");
	writemmp_mol("Ethene");
	
	OBAtom *C1 = molPtr->NewAtom();
    C1->SetAtomicNum(6);
    C1->SetVector(vector3(0.0, SCALE*0.5, 0.0) + delta);
	writemmp_atom(C1);
	
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(vector3(0.0, SCALE*1.0, SCALE*0.5) + delta);
	writemmp_atom(H1);
	bond(molPtr, H1, C1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(vector3(0.0, SCALE*1.0, SCALE*-0.5) + delta);
	writemmp_atom(H2);
	bond(molPtr, H2, C1, 1);

    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(vector3(0.0, SCALE*-0.5, 0.0) + delta);
	writemmp_atom(C2);
	bond(molPtr, C2, C1, 2);
    
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(vector3(0.0, SCALE*-1.0, SCALE*0.5) + delta);
	writemmp_atom(H3);
	bond(molPtr, H3, C2, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(vector3(0.0, SCALE*-1.0, SCALE*-0.5) + delta);
	writemmp_atom(H4);
	bond(molPtr, H4, C2, 1);
}


void makeC2H6(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("C2H6");
	writemmp_mol("Ethane");
	
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
    C1->SetVector(vector3(0.0, SCALE*0.5, 0.0) + delta);
	writemmp_atom(C1);
	
    OBAtom *H1 = molPtr->NewAtom();
    H1->SetAtomicNum(1);
    H1->SetVector(vector3(0.0, SCALE*1.0, SCALE*0.5) + delta);
	writemmp_atom(H1);
	bond(molPtr, H1, C1, 1);
    
    OBAtom *H2 = molPtr->NewAtom();
    H2->SetAtomicNum(1);
    H2->SetVector(vector3(SCALE*0.5*sinTheta, SCALE*1.0, SCALE*0.5*cosTheta) + delta);
	writemmp_atom(H2);
	bond(molPtr, H2, C1, 1);
	
    OBAtom *H3 = molPtr->NewAtom();
    H3->SetAtomicNum(1);
    H3->SetVector(vector3(SCALE*0.5*-sinTheta, SCALE*1.0, SCALE*0.5*cosTheta) + delta);
	writemmp_atom(H3);
	bond(molPtr, H3, C1, 1);
    
    OBAtom *C2 = molPtr->NewAtom();
    C2->SetAtomicNum(6);
    C2->SetVector(vector3(0.0, SCALE*-0.5, 0.0) + delta);
	writemmp_atom(C2);
	bond(molPtr, C2, C1, 1);
    
    OBAtom *H4 = molPtr->NewAtom();
    H4->SetAtomicNum(1);
    H4->SetVector(vector3(0.0, SCALE*-1.0, SCALE*-0.5) + delta);
	writemmp_atom(H4);
	bond(molPtr, H4, C2, 1);
    
    OBAtom *H5 = molPtr->NewAtom();
    H5->SetAtomicNum(1);
    H5->SetVector(vector3(SCALE*0.5*sinTheta, SCALE*-1.0, SCALE*0.5*-cosTheta) + delta);
	writemmp_atom(H5);
	bond(molPtr, H5, C2, 1);
    
    OBAtom *H6 = molPtr->NewAtom();
    H6->SetAtomicNum(1);
    H6->SetVector(vector3(SCALE*0.5*-sinTheta, SCALE*-1.0, SCALE*0.5*-cosTheta) + delta);
	writemmp_atom(H6);
	bond(molPtr, H6, C2, 1);
}


void makeC6H6(OBMol *molPtr, vector3 const& delta)
{
	molPtr->SetTitle("C6H6");
	writemmp_mol("Benzene");
	
	int const N = 6;
	OBAtom *C[N], *H[N];
	int bondOrder = 1;
	for(int i=0; i<N; ++i) {
		C[i] = molPtr->NewAtom();
		C[i]->SetAtomicNum(6);
		H[i] = molPtr->NewAtom();
		H[i]->SetAtomicNum(1);
		double const theta = (i * 360.0/N) * M_PI / 180.0;
		double const cosTheta = cos(theta);
		double const sinTheta = sin(theta);
		C[i]->SetVector(vector3(0.0, 2.0*SCALE * cosTheta, 2.0*SCALE * sinTheta) + delta);
		H[i]->SetVector(vector3(0.0, 3.0*SCALE * cosTheta, 3.0*SCALE * sinTheta) + delta);
		
		writemmp_atom(C[i]);
		if(i > 0) {
			bond(molPtr, C[i], C[i-1], bondOrder);
			bondOrder = 3 - bondOrder;
		}
		
		if(i == N-1)
			bond(molPtr, C[N-1], C[0], bondOrder);
		
		writemmp_atom(H[i]);
		bond(molPtr, H[i], C[i], 1);
		
	}
	
}


void writemmp_group(string const& name)
{
#ifdef GENERATE_MMP
	cout << "group (" << name << ")" << endl;
#endif
}


void writemmp_egroup(string const& name)
{
#ifdef GENERATE_MMP
	cout << "egroup (" << name << ")" << endl;
#endif
}


void writemmp_mol(string const& name)
{
#ifdef GENERATE_MMP
	cout << "mol (" << name << ") def" << endl;
// 	OBAtomIterator atomIter;
// 	OBAtom *atomPtr = NULL;
// 	for(atomPtr = molPtr->BeginAtom();
// 	    atomPtr!=NULL;
// 	    atomPtr=molPtr->NextAtom(atomPtr))
// 	{
// 		
// 	}
#endif
}


void writemmp_atom(OBAtom *const atomPtr)
{
#ifdef GENERATE_MMP
	++atomIdx;
	atomIdxMap[atomPtr] = atomIdx;
	int x = int(atomPtr->GetX() * 1000);
	int y = int(atomPtr->GetY() * 1000);
	int z = int(atomPtr->GetZ() * 1000);
	cout << "atom " << atomIdx << " (" << atomPtr->GetAtomicNum() << ") "
		<< '(' << x << ", " << y << ", " << z << ") def" << endl;
#endif
}


/// Bonds must be created so that the begin-atom is the most-recently created
void writemmp_bond(OBBond *const bondPtr)
{
#ifdef GENERATE_MMP
	OBAtom *const atom2Ptr = bondPtr->GetEndAtom();
	int idx2 = 0;
	idx2 = atomIdxMap[atom2Ptr];
	assert(idx2 != 0);
	cout << "bond" << bondPtr->GetBondOrder() << ' ' << idx2 << endl;
#endif
}

