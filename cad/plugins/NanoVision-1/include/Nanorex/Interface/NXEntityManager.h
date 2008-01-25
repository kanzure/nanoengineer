// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <string>
using namespace std;

#include <QString>

#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
#include "Nanorex/Utility/NXPluginGroup.h"
#include "Nanorex/Utility/NXStringTokenizer.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
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
		NXCommandResult* importFromFile(NXMoleculeSet* moleculeSet,
										NXDataStoreInfo* dataStoreInfo,
										const string& type,
										const string& filename,
										unsigned int frameIndex = 0);
		NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
									  NXDataStoreInfo* dataStoreInfo,
									  const string& type,
									  const string& filename,
									  unsigned int frameIndex = 0);
									  
		//
		// MoleculeSet
		//
		NXMoleculeSet* getRootMoleculeSet() { return rootMoleculeSet; }

	private:
		NXPluginGroup* dataImpExpPluginGroup;
		map<string, NXDataImportExportPlugin*> dataImportTable;
		map<string, NXDataImportExportPlugin*> dataExportTable;
		
		NXMoleculeSet* rootMoleculeSet;
};

} // Nanorex::

#endif
