// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_HDF5_SIMRESULTSIMPORTEXPORT_H
#define NX_HDF5_SIMRESULTSIMPORTEXPORT_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <QDir>
#include <QFile>
#include <QString>

#include "Nanorex/HDF5_SimResults.h"
#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
//#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"
using namespace Nanorex;

//#include <iostream>
#include <vector>
//#include <string>
//#include <stack>
//#include <list>
//#include <map>
using namespace std;

#ifdef WIN32
#	if _MSC_VER > 1000
#		pragma once
#	endif // _MSC_VER > 1000

// Exclude rarely-used stuff from Windows headers
#	define WIN32_LEAN_AND_MEAN
#	include <windows.h>

// DLL-specific
#	define DLLEXPORT __declspec(dllexport)
#else
#	define DLLEXPORT
#endif

extern "C" DLLEXPORT NXPlugin* instantiate();


/* CLASS: HDF5_SimResultsImportExport */
class HDF5_SimResultsImportExport : public NXDataImportExportPlugin {
	public:
		HDF5_SimResultsImportExport();
		~HDF5_SimResultsImportExport();

		// NXDataImportExportPlugin implementation
		NXCommandResult* importFromFile(NXMoleculeSet* moleculeSet,
										NXDataStoreInfo* dataStoreInfo,
										const std::string& filename,
										unsigned int frameIndex = 0);
		NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
									  NXDataStoreInfo* dataStoreInfo,
									  const std::string& filename,
									  unsigned int frameIndex = 0);

	private:
		void exportToFileHelper(NXMoleculeSet* moleculeSet,
								unsigned int atomIndex, unsigned int bondIndex,
								unsigned int* atomIds,
								unsigned int* atomicNumbers,
								float* positions, void* bonds,
								NXCommandResult* result);
		void populateCommandResult(NXCommandResult* result,
								   const string& message);
};

#endif
