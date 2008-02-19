// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExport.h"
#include <fstream>
#include <sstream>

/* CONSTRUCTOR */
NanorexMMPImportExport::NanorexMMPImportExport()
{
}

/* DESTRUCTOR */
NanorexMMPImportExport::~NanorexMMPImportExport()
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
        readMMP_mol(infile, moleculeSet);
    }
    
	// Set the meta information about the data store.
	if (success) {
		dataStoreInfo->setIsSingleStructure(true);
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


/* FUNCTION: populateCommandResult */
void NanorexMMPImportExport::populateCommandResult
(NXCommandResult* result, const string& message) {
    result->setResult(NX_PLUGIN_REPORTS_ERROR);
    vector<QString> resultVector;
    resultVector.push_back("OpenBabelImportExport");
    resultVector.push_back(message.c_str());
    result->setParamVector(resultVector);
}

