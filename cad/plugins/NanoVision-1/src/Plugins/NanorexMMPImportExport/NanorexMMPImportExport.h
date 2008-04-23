// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NANOREXMMPIMPORTEXPORT_H
#define NANOREXMMPIMPORTEXPORT_H

#include <openbabel/mol.h>
#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"
#include <Nanorex/Interface/NXAtomData.h>
#include <Nanorex/Interface/NXMoleculeSet.h>
#include <Nanorex/Interface/NXNamedView.h>

#include "RagelIstreamPtr.h"
#include <fstream>
#include <vector>
#include <sstream>
#include <set>
#include <map>
#include <cmath>
// #include <stack>

using namespace std;
using namespace Nanorex;


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
	
	double const& getTemperature(void) const { return kelvinTemp; }
	
	
private:
    
	string inputFilename;
	NXDataStoreInfo *dataStoreInfo;
	
	// extracted data that can be queried later
	string requiredVersion;
	string preferredVersion;
	double kelvinTemp;
	
	// state variables
	int lineNum;
	
// scratch variables to write parsed values to
	OBMol *molPtr;   ///< current molecule
	OBAtom *atomPtr; ///< current atom
	OBBond *bondPtr; ///< current bond

	NXMoleculeSet *molSetPtr;
	///< current molecule-set. This is initialized by the input in
	///< importFromFile() which points to the molecule-structure of interest
	///< to the user. When inside the Clipboard group, this is NULL at the top
	///< level in between groups. Each top-level node will have to be allocated
	///< and assigned to this.
	
	bool insideViewDataGroup;
	NXMoleculeSet *clipboardGroup;
	bool insideClipboardGroup;
		

	int atomicNum, atomId, bondOrder;
	string atomStyle;
	map<int,OBAtom*> foundAtomList;
	vector<OBAtom*> targetAtomList;
	string stringVal, stringVal2;
	int intVal, intVal2;
	double doubleVal;
	// named-view temporaries
	std::string csysViewName;
	double csysQw, csysQx, csysQy, csysQz;
	double csysScale, csysZoomFactor;
	double csysPovX, csysPovY, csysPovZ;
	
    // molecule-set 'stack' to help with recursive 'group' specification
	NXMoleculeSet *rootMoleculeSetPtr;
	std::vector<NXMoleculeSet*> molSetPtrStack;
	std::string molStyle;
	// int molStructGroupLevel; ///< level in recursive specification
	// std::vector<std::string> defaultAtomStyleStack; // track with recursion into groups

	// Ragel + parser state variables
    int cs, top, act;
    int x, y, z;
    int stackSize;
	std::vector<int> stack;
	
    // Ragel pointers to input stream
    RagelIstreamPtr p, pe, eof, ts, te;
	RagelIstreamPtr charStringWithSpaceStart, charStringWithSpaceStop;
	RagelIstreamPtr lineStart;
	
	NXCommandResult commandResult;
	
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
	void newBondDirection(int atomId1, int atomId2);
	void newMolecule(string const& name, string const& style);
	void newViewDataGroup();
	void newNamedView(std::string const& name,
	                  double const& qw, double const& qx, double const& qy,
	                  double const& qz, double const& scale,
	                  double const& povX, double const& povY,
	                  double const& povZ, double const& zoomFactor);
	void newMolStructGroup(std::string const& name,
	                       std::string const& classification);
	void endMolStructGroup(std::string const& name);
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
    
	static int GetBondOrderFromType(string const& type);
	static int GetAtomID(OBAtom *atomPtr);
	// static char const *const GetAtomRenderStyleName(OBAtom *const atomPtr);
	static string const& GetAtomRenderStyleCode(OBAtom *const atomPtr);

    static void populateCommandResult(NXCommandResult* result,
                                      const string& message);
	
	static void SetResult(NXCommandResult& cmdResult,
	                      int errCode, std::string const& errMsg);
	static void ClearResult(NXCommandResult& cmdResult);
	
    

	friend class NanorexMMPImportExportTest;
	
};


#endif // NANOREXMMPIMPORTEXPORT_H
