
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXMoleculeSet.h"

namespace Nanorex {

unsigned int NXMoleculeSet::NextMoleculeIndex = 0;

char const *const NXMoleculeSet::groupClassificationString[NXMoleculeSet::NUM_GROUP_CLASSIFICATIONS] =
{
	"", "DnaGroup", "DnaSegment", "DnaStrand", "Block",
		"NanotubeGroup", "NanotubeSegment"
};

/* CONSTRUCTOR */
NXMoleculeSet::NXMoleculeSet(bool const& deleteOnDestruct)
	: deleteInDestructor(deleteOnDestruct),
	children(), molecules(),
	title(), classification(NONE)
{
}


/* DESTRUCTOR */
NXMoleculeSet::~NXMoleculeSet() {
	if(deleteInDestructor) {
		OBMolIterator molIter;
		for(molIter = moleculesBegin(); molIter != moleculesEnd(); ++molIter)
			delete *molIter;
		
		NXMoleculeSetIterator molSetIter;
		for(molSetIter = childrenBegin(); molSetIter != childrenEnd(); ++molSetIter)
			delete *molSetIter;
	}
}


/* FUNCTION: newMolecule */
OBMol* NXMoleculeSet::newMolecule() {
	OBMol* molecule = new OBMol();
	NXMoleculeData* moleculeData = new NXMoleculeData();
	moleculeData->SetIdx(NextMoleculeIndex);
	NextMoleculeIndex++;
	molecule->SetData(moleculeData);
	molecules.push_back(molecule);
	return molecule;
}


/* FUNCTION: getCounts */
void NXMoleculeSet::getCounts(unsigned int& moleculeCount,
							  unsigned int& atomCount,
							  unsigned int& bondCount) {
							  
	moleculeCount = atomCount = bondCount = 0;
	getCountsHelper(moleculeCount, atomCount, bondCount, this);
}


/* FUNCTION: getCountsHelper */
void NXMoleculeSet::getCountsHelper(unsigned int& moleculeCount,
									unsigned int& atomCount,
									unsigned int& bondCount,
									NXMoleculeSet* moleculeSet) {
									
	moleculeCount += moleculeSet->moleculeCount();
	OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
	while (moleculeIter != moleculeSet->moleculesEnd()) {
		atomCount += (*moleculeIter)->NumAtoms();
		bondCount += (*moleculeIter)->NumBonds();
		moleculeIter++;
	}
	NXMoleculeSetIterator moleculeSetIter = moleculeSet->childrenBegin();
	while (moleculeSetIter != moleculeSet->childrenEnd()) {
		getCountsHelper(moleculeCount, atomCount, bondCount, *moleculeSetIter);
		moleculeSetIter++;
	}
}


bool NXMoleculeSet::empty(void)
{
    if(molecules.empty()) {
        list<NXMoleculeSet*>::const_iterator childrenIter;
        for(childrenIter = childrenBegin();
            childrenIter != childrenEnd();
            ++childrenIter)
        {
            NXMoleculeSet *const childMolSetPtr = *childrenIter;
            if(!childMolSetPtr->empty()) return false;
        }
        return true; // children are also empty
    }
    else return false;
}




} // Nanorex::
