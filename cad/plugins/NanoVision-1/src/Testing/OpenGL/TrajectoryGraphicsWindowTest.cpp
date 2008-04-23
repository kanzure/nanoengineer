// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.


#include <Nanorex/Interface/NXDataStoreInfo.h>
#include <Nanorex/Interface/NXEntityManager.h>
#include "TrajectoryTestGraphicsManager.h"
#include <Nanorex/Interface/NXAtomData.h>
#include <TrajectoryGraphicsWindow.h>

#include <cassert>

#include <QApplication>
#include <QMainWindow>

using namespace Nanorex;
using namespace OpenBabel;
using namespace std;

void initializeEntityManager(NXEntityManager *const entityManager,
                             NXMoleculeSet *theMoleculeSet[],
                             int const NUM_FRAMES);
void createMoleculeSets(NXMoleculeSet *molSetArray[], int const NUM_FRAMES);

int const NUM_FRAMES = 6;
int const NUM_ATOMS = 5;

// atom coordinates in Angstroms
double atomCoords[NUM_FRAMES][NUM_ATOMS][3] = {
	// frame-1
	{ { 0, 4}, { 0, 0}, { 2, 2}, { 4, 0}, { 4, 4} },
	{ {-1, 4}, { 0, 0}, { 1, 2}, { 3, 0}, { 4, 3} },
	{ {-1, 3}, { 0, 0}, { 1, 1}, { 3, 1}, { 4, 2} },
	{ { 0, 2}, { 0, 0}, { 1, 0}, { 4, 1}, { 5, 2} },
	{ {-1, 2}, { 0, 0}, { 2, 0}, { 4, 2}, { 6, 2} },
	{ {-1, 1}, { 0, 0}, { 2, 1}, { 4, 2}, { 6, 3} }
};

int atomicNums[NUM_ATOMS] = { 1, 8, 6, 16, 1 };


int main(int argc, char *argv[])
{
    // create application and main window
	QApplication app(argc, argv);
	QMainWindow mainWindow;
	mainWindow.resize(960, 600);
	
	NXDataStoreInfo dataStoreInfo;
	NXEntityManager entityManager;
	TrajectoryTestGraphicsManager graphicsManager;
	
	TrajectoryGraphicsWindow *trajectoryWindow =
		new TrajectoryGraphicsWindow((QWidget*) 0,
		                             &entityManager,
		                             &graphicsManager);
	
	mainWindow.setCentralWidget(trajectoryWindow);
	mainWindow.show();
	
	NXMoleculeSet *theMoleculeSet[NUM_FRAMES];
	assert(theMoleculeSet != NULL);
	createMoleculeSets(theMoleculeSet, NUM_FRAMES);
	initializeEntityManager(&entityManager, theMoleculeSet, NUM_FRAMES);
	trajectoryWindow->setFrameSetId(0);
	
	mainWindow.update();
	
	int retval = app.exec();
	
	// for(int iFrame = 0; iFrame < NUM_FRAMES; ++iFrame)
	//	delete theMoleculeSet[iFrame];
	
	return retval;
}


void initializeEntityManager(NXEntityManager *const entityManager,
                             NXMoleculeSet *theMoleculeSet[],
                             int const NUM_FRAMES)
{
	// assert(entityManager->getFrameCount(0) == 0);
	int frameSetId = entityManager->addFrameSet();
	for(int iFrame = 0; iFrame < NUM_FRAMES; ++iFrame) {
		int lastFrameId =
			entityManager->addFrame(frameSetId, theMoleculeSet[iFrame]);
		assert(lastFrameId == iFrame);
	}
	assert((int)entityManager->getFrameCount(frameSetId) == NUM_FRAMES);
}


void bond(OBMol *molPtr, OBAtom *atom1Ptr, OBAtom *atom2Ptr, int bondOrder)
{
	OBBond *bondPtr = molPtr->NewBond();
	assert(bondPtr != NULL);
	bondPtr->SetBegin(atom1Ptr);
	bondPtr->SetEnd(atom2Ptr);
	atom1Ptr->AddBond(bondPtr);
	atom2Ptr->AddBond(bondPtr);
	bondPtr->SetBondOrder(bondOrder);
}



void createMoleculeSets(NXMoleculeSet *molSetArray[], int const NUM_FRAMES)
{
	for(int iFrame = 0; iFrame < NUM_FRAMES; ++iFrame) {
		molSetArray[iFrame] = new NXMoleculeSet;
		assert(molSetArray[iFrame] != NULL);
		OBMol *mol = molSetArray[iFrame]->newMolecule();
		assert(mol != NULL);
		OBAtom *atom[NUM_ATOMS];
		for(int iAtom = 0; iAtom < NUM_ATOMS; ++iAtom) {
			atom[iAtom] = mol->NewAtom();
			assert(atom[iAtom] != NULL);
			atom[iAtom]->SetAtomicNum(atomicNums[iAtom]);
			NXAtomData *atomData = new NXAtomData(atomicNums[iAtom]);
			assert(atomData != NULL);
			atomData->setRenderStyleCode("def");
			atomData->setIdx(iAtom);
			atom[iAtom]->SetData(atomData);
			atom[iAtom]->SetVector(atomCoords[iFrame][iAtom][0],
			                       atomCoords[iFrame][iAtom][1],
			                       atomCoords[iFrame][iAtom][2]);
		}
		
		bond(mol, atom[0], atom[1], 1);
		bond(mol, atom[1], atom[2], 2);
		bond(mol, atom[2], atom[3], 2);
		bond(mol, atom[3], atom[4], 1);
	}
}
