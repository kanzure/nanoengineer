// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_DATAIMPORTEXPORTPLUGIN_H
#define NX_DATAIMPORTEXPORTPLUGIN_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <string>
using namespace std;

#include <QtPlugin>

#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXDataStoreInfo.h"

namespace Nanorex {


/* CLASS: NXDataImportExportPlugin */
/**
 * Data Import/Export plugin interface.
 * @ingroup NanorexInterface PluginArchitecture
 */
class NXDataImportExportPlugin {
	public:
		virtual ~NXDataImportExportPlugin() {}

		/**
		 * Imports the system from the given file into the given molecule set.
		 *
		 * If frameIndex == 0, populates dataStoreInfo, else, re-uses the file
		 * handle from dataStoreInfo. If opening a multi-frame file, a handle
		 * to it will be stored in the dataStoreInfo for later use (subsequent
		 * importFromFile calls.)
		 *
		 * No modifications to the given moleculeSet will result in deletion
		 * of the frame with the given frameIndex.
		 */
		virtual NXCommandResult* importFromFile
			(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
			 const string& filename, int frameSetId, int frameIndex) = 0;

		/**
		 * Exports the system to the given file from the given molecule set.
		 *
		 * When writing a multi-frame file, caller would set a flag in dataStore
		 * to indicate that, and this function would store a handle to the file
		 * in the dataStore for subsequent use.
		 */
		virtual NXCommandResult* exportToFile
			(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
			 const string& filename, int frameSetId, int frameIndex) = 0;
};

} // Nanorex::

Q_DECLARE_INTERFACE(Nanorex::NXDataImportExportPlugin,
					"com.Nanorex.Interface.NXDataImportExportPlugin/0.1.0")

#endif
