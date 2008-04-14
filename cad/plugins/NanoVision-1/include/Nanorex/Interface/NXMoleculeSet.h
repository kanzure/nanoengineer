// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MOLECULESET_H
#define NX_MOLECULESET_H

#include <list>
#include <string>
using namespace std;

#include <openbabel/mol.h>
using namespace OpenBabel;

#include "Nanorex/Interface/NXMoleculeData.h"
#include "Nanorex/Interface/NXNumbers.h"

namespace Nanorex {

class NXMoleculeSet;

typedef std::list<NXMoleculeSet*>::iterator NXMoleculeSetIterator;
typedef std::list<OBMol*>::iterator OBMolIterator;


/* CLASS: NXMoleculeSet */
/**
 * Encapsulates a recursive tree of molecule sets containing molecules.
 *
 * @ingroup ChemistryDataModel, NanorexInterface
 */
class NXMoleculeSet {
public:
	
	enum GroupClassification {
		NONE=0, DNA_GROUP, DNA_SEGMENT, DNA_STRAND,
			BLOCK,
			NANOTUBE_GROUP, NANOTUBE_SEGMENT,
			NUM_GROUP_CLASSIFICATIONS
	};
	
	NXMoleculeSet(bool const& deleteOnDestruct = true);
    ~NXMoleculeSet();
    
    void addChild(NXMoleculeSet* child) { children.push_back(child); }
    NXMoleculeSetIterator childrenBegin() { return children.begin(); }
    NXMoleculeSetIterator childrenEnd() { return children.end(); }
    NXMSInt childCount() { return children.size(); }
    
    //
    // Molecules
    //
    OBMol* newMolecule();
	void addMolecule(OBMol* mol) { molecules.push_back(mol); }
    OBMolIterator moleculesBegin() { return molecules.begin(); }
    OBMolIterator moleculesEnd() { return molecules.end(); }
    NXABMInt moleculeCount() { return molecules.size(); }
    
    void getCounts(unsigned int& moleculeCount, unsigned int& atomCount,
                   unsigned int& bondCount);
    
    /// Does the molecule-set tree have any atoms?
    bool empty(void);
    
    void setTitle(std::string const& theTitle) { title = theTitle; }
    std::string const& getTitle(void) const { return title; }
    
	void setGroupClassification(GroupClassification const& _classification);
	GroupClassification getGroupClassification(void) const;
	void setGroupClassificationString(std::string const& _classification);
	char const *const getGroupClassificationString(void) const;
	
private:
    static unsigned int NextMoleculeIndex;
	bool const deleteInDestructor;
    std::list<NXMoleculeSet*> children;
    std::list<OBMol*> molecules;
    
    std::string title;
	GroupClassification classification;
	
	static char const *const groupClassificationString[NUM_GROUP_CLASSIFICATIONS];
	
    void getCountsHelper(unsigned int& moleculeCount,
                         unsigned int& atomCount,
                         unsigned int& bondCount,
                         NXMoleculeSet* moleculeSet);
};

// --- inline function definitions ---

inline
	void
	NXMoleculeSet::setGroupClassification(NXMoleculeSet::GroupClassification const& _classification)
{
	classification = _classification;
}


inline
	NXMoleculeSet::GroupClassification
	NXMoleculeSet::getGroupClassification(void) const
{
	return classification;
}


inline char const *const NXMoleculeSet::getGroupClassificationString(void) const
{
	return groupClassificationString[classification];
}


inline
	void
	NXMoleculeSet::setGroupClassificationString(std::string const& classificationString)
{
	for(int c = (int)NONE; c < (int)NUM_GROUP_CLASSIFICATIONS; ++c) {
		if(classificationString == groupClassificationString[c]) {
			classification = (GroupClassification) c;
			return;
		}
	}
	classification = NONE;
}


} // Nanorex::

#endif
