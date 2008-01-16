// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_DATAIMPORTEXPORTPLUGIN_H
#define NX_DATAIMPORTEXPORTPLUGIN_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <string>

#include "Nanorex/Utility/NXPlugin.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXNumbers.h"

namespace Nanorex {

class NXEntityManager;

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
		void setEntityManager(NXEntityManager* entityManager);

		/** Sets the type, or mode, of the file being imported/exported. This
		  * is called by the NXEntityManager when importing/exporting files.
		  * For example, if the import type
		  * is "CML", then \c setMode("CML") is called on this
		  * DataImportExportPlugin before any #importFromFile or #exportToFile
		  * call is made.
		  */
		void setMode(const std::string& mode);

		virtual ~NXDataImportExportPlugin();

		/**
		 * Imports the system from the given file into the molecule set with
		 * the given identifier.
		 */
		virtual NXCommandResult* importFromFile
			(NXMSInt moleculeSetId, const std::string& filename) = 0;

		/**
		 * Exports the system from the given file from the molecule set with
		 * the given identifier.
		 */
		virtual NXCommandResult* exportToFile
			(NXMSInt moleculeSetId, const std::string& filename) = 0;

	protected:
		std::string mode;
		NXEntityManager* entityManager;
};

} // Nanorex::

#endif
