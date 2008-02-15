// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MMPIMPORTEXPORT_H
#define NX_MMPIMPORTEXPORT_H

#include <fstream>
#include <vector>
#include <openbabel/mol.h>
#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"

using namespace std;
using namespace Nanorex;

namespace Nanorex {

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
                                    const std::string& filename,
                                    int frameSetId, int frameIndex);
    NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
                                  NXDataStoreInfo* dataStoreInfo,
                                  const std::string& filename,
                                  int frameSetId, int frameIndex);
    
    
protected:
    virtual void readMMP_mol();
    
    NXRagelFilePtr p;
    int cs;
    OBMol *mol;
    std::vector<OBAtom*> targetAtomList;

private:
    void populateCommandResult(NXCommandResult* result,
                               const string& message);
};


} // namespace Nanorex

#endif // NX_MMPIMPORTEXPORT_H
