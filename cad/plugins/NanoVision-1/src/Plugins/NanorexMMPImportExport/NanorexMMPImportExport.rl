// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExport.h"



/* CONSTRUCTOR */
NanorexMMPImportExport::NanorexMMPImportExport()
{
    reset();
}

/* DESTRUCTOR */
NanorexMMPImportExport::~NanorexMMPImportExport()
{
}


void NanorexMMPImportExport::reset(void)
{
}

void NanorexMMPImportExport::readMMP(istream& instream,
                                     NXMoleculeSet *moleculeSet)
{
}



NXCommandResult*
NanorexMMPImportExport::
importFromFile(NXMoleculeSet* moleculeSet,
               NXDataStoreInfo* dataStoreInfo,
               const std::string& filename,
               int frameSetId, int frameIndex)
{
    bool success = true;
    NXCommandResult* result = new NXCommandResult();
    result->setResult(NX_CMD_SUCCESS);
    
    ifstream infile(filename.c_str(), ios::in);
    if(!infile) {
        populateCommandResult(result,
                              (string("Couldn't open file: ") + filename)
                              .c_str());
        success = false;
    }
    else {
        readMMP(infile, moleculeSet);
    }
    
// Retrieve and set the meta information about the data store.
    if (success) {
        QFileInfo fileInfo(filename.c_str());
        dataStoreInfo->addInputStructure(qPrintable(fileInfo.fileName()),
                                         frameSetId);
    }
    
    return result;
}


NXCommandResult*
NanorexMMPImportExport::
exportToFile(NXMoleculeSet* moleculeSet,
             NXDataStoreInfo* dataStoreInfo,
             const std::string& filename,
             int frameSetId, int frameIndex)
{
    /// @todo
}


