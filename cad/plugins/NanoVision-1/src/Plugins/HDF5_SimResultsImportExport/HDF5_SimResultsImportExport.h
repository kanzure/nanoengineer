// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_HDF5_SIMRESULTSIMPORTEXPORT_H
#define NX_HDF5_SIMRESULTSIMPORTEXPORT_H

#include "Nanorex/Utility/NXLogger.h"
//#include "NanoHiveUtil/Utility.h"
//#include "NanoHiveUtil/Geometry.h"
#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXEntityManager.h"
//#include "NanoHiveInterface/NH_Commands.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

//#include <iostream>
//#include <vector>
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

extern "C" DLLEXPORT Nanorex::NXPlugin* instantiate();


/* CLASS: HDF5_SimResultsImportExport */
class HDF5_SimResultsImportExport : public Nanorex::NXDataImportExportPlugin {
	public:
		HDF5_SimResultsImportExport();
		~HDF5_SimResultsImportExport();

		// NXDataImportExportPlugin implementation
		Nanorex::NXCommandResult* importFromFile(NXMSInt moleculeSetId,
												 const std::string& filename);
		Nanorex::NXCommandResult* exportToFile(NXMSInt moleculeSetId,
											   const std::string& filename);

	private:
};

#endif
