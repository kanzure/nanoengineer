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

#include "Nanorex/Utility/NXPlugin.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXDataStoreInfo.h"

namespace Nanorex {

//class NXEntityManager;

/* CLASS: NXDataImportExportPlugin */
/**
 * Data Import/Export plugin interface.
 * @ingroup NanorexInterface PluginArchitecture
 */
class NXDataImportExportPlugin : public NXPlugin {
	public:
		NXDataImportExportPlugin();

		/** Sets the NXEntityManager to use. Called when this plugin is
		  * created.*/
		//void setEntityManager(NXEntityManager* entityManager);

		/** Sets the type, or mode, of the file being imported/exported. This
		  * is called by the NXEntityManager when importing/exporting files.
		  * For example, if the import type
		  * is "CML", then \c setMode("CML") is called on this
		  * DataImportExportPlugin before any #importFromFile or #exportToFile
		  * call is made.
		  */
		void setMode(const string& mode);

		virtual ~NXDataImportExportPlugin();

		/**
		 * Imports the system from the given file into the given molecule set.
		 *
		 * If frameIndex == 0, populates dataStoreInfo, else, re-uses the file
		 * handle from dataStoreInfo. If opening a multi-frame file, a handle
		 * to it will be stored in the dataStoreInfo for later use (subsequent
		 * importFromFile calls.)
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

	protected:
		string mode;
		//NXEntityManager* entityManager;
};

} // Nanorex::

#endif
