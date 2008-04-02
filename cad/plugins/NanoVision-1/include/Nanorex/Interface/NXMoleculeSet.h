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
    
private:
    static unsigned int NextMoleculeIndex;
	bool const deleteInDestructor;
    std::list<NXMoleculeSet*> children;
    std::list<OBMol*> molecules;
    
    std::string title;
    
    void getCountsHelper(unsigned int& moleculeCount,
                         unsigned int& atomCount,
                         unsigned int& bondCount,
                         NXMoleculeSet* moleculeSet);		
};


} // Nanorex::

#endif
