// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MMPIMPORTEXPORT_H
#define NX_MMPIMPORTEXPORT_H

#include <openbabel/mol.h>
#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"
#include <Nanorex/Interface/NXAtomData.h>
#include <Nanorex/Interface/NXMoleculeSet.h>

#include "ragelistreamptr.h"
#include <fstream>
#include <vector>
#include <sstream>
#include <set>
#include <map>
#include <stack>

using namespace std;
using namespace Nanorex;

namespace Nanorex {


/* CLASS: NanorexMMPImportExport */
class NanorexMMPImportExport : public QObject, public NXDataImportExportPlugin
{
	Q_OBJECT;
	Q_INTERFACES(Nanorex::NXDataImportExportPlugin);
        
public:
        
    NanorexMMPImportExport();
    ~NanorexMMPImportExport();
    
    // NXDataImportExportPlugin implementation
    NXCommandResult* importFromFile(NXMoleculeSet* moleculeSet,
                                    NXDataStoreInfo* dataStoreInfo,
                                    const std::string& theFilename,
                                    int frameSetId, int frameIndex);
    NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
                                  NXDataStoreInfo* dataStoreInfo,
                                  const std::string& theFilename,
                                  int frameSetId, int frameIndex);

	string const& getRequiredVersion(void) const { return requiredVersion; }
	string const getPreferredVersion(void) const { return preferredVersion; }
	
	double const& getTemperature(void) const { return kelvinTemperature; }
	
	
private:
    
	string inputFilename;
	
	// extracted data that can be queried later
	string requiredVersion;
	string preferredVersion;
	double kelvinTemperature;
	
	int lineNum;
	
	// scratch variables to write parsed values to
	OBMol *molPtr; // current molecule
	OBAtom *atomPtr; // current atom
	OBBond *bondPtr; // current bond
	NXMoleculeSet *molSetPtr; // current molecule-set
	
	int atomicNum, atomId, bond_order;
	string atomStyle;
	// string defaultAtomStyle; // as specified by group, mol settings
	map<int,OBAtom*> foundAtomList;
	vector<OBAtom*> targetAtomList;
	string stringVal, stringVal2;
	int intVal, intVal2;
	double doubleVal;
    // molecule-set 'stack' to help with recursive 'group' specification
	std::stack<NXMoleculeSet*> molSetPtrStack;
	std::stack<string> defaultAtomStyleStack; // track with recursion into groups

	// Ragel + parser state variables
    int cs, top, act;
    int x, y, z;
    int stackSize;
	std::vector<int> stack;
	
    // Ragel pointers to input stream
    RagelIstreamPtr p, pe, eof, ts, te;
	RagelIstreamPtr charStringWithSpaceStart, charStringWithSpaceStop;
    
    // helper functions
	
	void reset(void);
    bool readMMP(istream& instream, NXMoleculeSet *rootMoleculeSetPtr);
	// void createNewMolecule(void);
	// void createNewMoleculeSet(void);
	// void closeMoleculeSet(void);
    
	// void applyAtomType(string const& keyStr, string const& valueStr);
    
	
	// "slots" called for matched patterns
	
	void newAtom(int id, int atomicNum, int x, int y, int z,
	             string const& style);
	void newBond(string const& type, int targetAtomId);
	void newMolecule();
	void newViewDataGroup();
	void newMolStructGroup(std::string const& name, std::string const& style);
	void newClipboardGroup();
	void endGroup(std::string const& groupName);
	
	void newAtomInfo(std::string const& key, std::string const& value);
	void newOpenGroupInfo(std::string const& key, std::string const& value);
	void newChunkInfo(std::string const& key, std::string const& value);
	
	void end1();
	
    // Static data and function members
    
    static int const NUM_BOND_TYPES = 6;
    static char const _s_bondOrderString[NUM_BOND_TYPES];
    static char const _s_bondOrderNameString[NUM_BOND_TYPES][16];
    static char const _s_hybridizationName[8][8];
    
    static void PrintMoleculeSet(ostream& o,
                                 NXMoleculeSet *const molSetPtr);
    static void PrintMolecule(ostream& o, OBMol *const molPtr);
    
    static int GetAtomID(OBAtom *atomPtr);
	// static char const *const GetAtomRenderStyleName(OBAtom *const atomPtr);
	static string const& GetAtomRenderStyleCode(OBAtom *const atomPtr);

    static void populateCommandResult(NXCommandResult* result,
                                      const string& message);
    
	friend class NanorexMMPImportExportTest;
};


} // namespace Nanorex

#endif // NX_MMPIMPORTEXPORT_H
