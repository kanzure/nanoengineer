// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_HDF5_SIMRESULTSIMPORTEXPORT_H
#define NX_HDF5_SIMRESULTSIMPORTEXPORT_H

#include <QDir>
#include <QFile>
#include <QObject>
#include <QString>
#include <QFileInfo>

#include "Nanorex/HDF5_SimResults.h"
#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"
#include "Nanorex/Interface/NXAtomData.h"
using namespace Nanorex;

#include <vector>
#include <string>
using namespace std;


/* CLASS: HDF5_SimResultsImportExport */
class HDF5_SimResultsImportExport
		: public QObject, public NXDataImportExportPlugin {
	Q_OBJECT
	Q_INTERFACES(Nanorex::NXDataImportExportPlugin)
		
public:
    HDF5_SimResultsImportExport();
    ~HDF5_SimResultsImportExport();
    
	// NXDataImportExportPlugin implementation
    NXCommandResult* importFromFile(NXMoleculeSet* moleculeSet,
                                    NXDataStoreInfo* dataStoreInfo,
                                    const string& filename,
                                    int frameSetId, int frameIndex);
    NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
                                NXDataStoreInfo* dataStoreInfo,
                                const string& filename,
                                int frameSetId, int frameIndex);
	
	virtual NXCommandResult* fixDataStore(const string& filename);
    
private:
    void populateDataStoreInfo(NXDataStoreInfo* dataStoreInfo,
							   HDF5_SimResults* simResults,
							   const string& hdf5FileDirectory,
							   int frameSetId);
	NXProperties* getResultsSummary(HDF5_SimResults* simResults);
    void exportToFileHelper(NXMoleculeSet* moleculeSet,
                            unsigned int atomIndex, unsigned int bondIndex,
                            unsigned int* atomIds,
                            unsigned int* atomicNumbers,
                            float* positions, void* bonds,
                            NXCommandResult* result);
    void populateCommandResult(NXCommandResult* result,
                            const string& message);
	string getHDF5fileDirectory(const string& filename);
};

#endif
