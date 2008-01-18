// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
#include "Nanorex/Utility/NXPluginGroup.h"
#include "Nanorex/Utility/NXStringTokenizer.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"

namespace Nanorex {


/* CLASS: NXEntityManager */
/**
 * Encapsulates the storage of molecular and related data.
 * @ingroup ChemistryDataModel, NanorexInterface
 *
 * TODO:
 * - Store/handle DNA strand direction information. This is the equivalent of
 *   bond direction data coming out of NE1.
 */
class NXEntityManager {
	
	public:
		NXEntityManager();
		~NXEntityManager();

		//
		// Import/export plugins
		//
		void loadDataImportExportPlugins(NXProperties* properties);
		int importFromFile(const unsigned int& moleculeSetId,
						   const std::string& fileType,
						   const std::string& fileName,
						   std::string& message);
		int exportToFile(const unsigned int& moleculeSetId,
						 const std::string& fileType,
						 const std::string& fileName,
						 std::string& message);
		//
		// MoleculeSet
		//
		NXMoleculeSet* getRootMoleculeSet() { return rootMoleculeSet; }

	private:
		NXPluginGroup* dataImpExpPluginGroup;
		std::map<std::string, NXDataImportExportPlugin*> dataImportTable;
		std::map<std::string, NXDataImportExportPlugin*> dataExportTable;
		
		NXMoleculeSet* rootMoleculeSet;
};

} // Nanorex::

#endif
