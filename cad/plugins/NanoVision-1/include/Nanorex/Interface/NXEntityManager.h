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
		NXCommandResult* importFromFile(const string& filename);/*,
										NXDataStoreInfo* dataStoreInfo);*/
		NXCommandResult* exportToFile(const string& filename);
									  
		//
		// Frame molecule sets
		//
		unsigned int addFrame() {
			NXMoleculeSet* moleculeSet = new NXMoleculeSet();
			moleculeSets.push_back(moleculeSet);
			return moleculeSets.size() - 1;
		}
		unsigned int getFrameCount() { return moleculeSets.size(); }
		NXMoleculeSet* getRootMoleculeSet(unsigned int frameIndex = 0) {
			if (frameIndex < moleculeSets.size())
				return moleculeSets[frameIndex];
			else {
				// See if there's a new frame
				//   or
				return 0;
			}
		}

	private:
		NXPluginGroup* dataImpExpPluginGroup;
		string importFileTypesString, exportFileTypesString;
		map<string, NXDataImportExportPlugin*> dataImportTable;
		map<string, NXDataImportExportPlugin*> dataExportTable;
		
		vector<NXMoleculeSet*> moleculeSets;
		
		string getFileType(const string& filename);
};

} // Nanorex::

#endif
