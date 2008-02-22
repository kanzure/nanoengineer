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

#if 0
/* CLASS: NXRagelFilePtr */
/**
 * Behaves like a char* but actually sequentially accesses a file.
 * This is to fool Ragel into thinking that it is accessing a char[] with
 * MMP strings to be parsed. Implements just enough methods to be compatible
 * with Ragel v5.25
 */

class NXRagelFilePtr {
public:
    RagelFilePtr(char const *const filename)
        : infile(filename, std::ios::in) , c('\0')
    { if(infile) c = infile.peek(); }
    ~RagelFilePtr() { if(infile.is_open()) infile.close(); }
      // allow advancement or pointer
    ragelfile_ptr& operator += (int n)
    { for(int i=0;i<n;++i) infile.get(c); return *this;}
      // allow access to current character
    char operator * () { return c; }
private:
    std::ifstream infile;
    char c;
};
#endif


/* CLASS: NanorexMMPImportExport */
class NanorexMMPImportExport : public QObject, public NXDataImportExportPlugin
{
    Q_OBJECT
    Q_INTERFACES(Nanorex::NXDataImportExportPlugin)
        
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

private:
    
    // Ragel + parser state variables
    int cs, stack[1000], top;
    int intval, atomicNum, atomID, bond_order;
    int x, y, z;
    int line;
    
    // Ragel pointers to input stream
    RagelIstreamPtr p, pe, eof;
    
    string filename;
    
    // scratch variables to write parsed values to
    OBMol *molPtr;
    OBAtom *atomPtr;
    NXAtomData::RenderStyleID atomStyleID;
    OBBond *bondPtr;
    NXMoleculeSet *molSetPtr;
    map<int,OBAtom*> foundAtomList;
    vector<OBAtom*> targetAtomList;
    string stringval, stringval2;
    
    // molecule-set 'stack' to help with recursive 'group' specification
    std::stack<NXMoleculeSet*> molSetPtrStack;
    
    void reset(void);
    bool readMMP(istream& instream, NXMoleculeSet *rootMoleculeSetPtr);
    void createNewMolecule(void);
    void createNewMoleculeSet(void);
    void closeMoleculeSet(void);
    
    void applyAtomType(string const& keyStr, string const& valueStr);
    
    // Static data and function members
    
    static int const NUM_BOND_TYPES = 6;
    static char const _s_bondOrderString[NUM_BOND_TYPES];
    static char const _s_bondOrderNameString[NUM_BOND_TYPES][16];
    static char const _s_hybridizationName[8][8];
    
    static void PrintMoleculeSet(ostream& o,
                                 NXMoleculeSet *const molSetPtr);
    static void PrintMolecule(ostream& o, OBMol *const molPtr);
    
    static int GetAtomID(OBAtom *atomPtr);
    static char const *const GetAtomRenderStyleName(OBAtom *const atomPtr);


    static void populateCommandResult(NXCommandResult* result,
                                      const string& message);
    
};




} // namespace Nanorex

#endif // NX_MMPIMPORTEXPORT_H
