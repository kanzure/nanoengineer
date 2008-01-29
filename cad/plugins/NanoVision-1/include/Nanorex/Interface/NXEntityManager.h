// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <vector>
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
 */
class NXEntityManager {
	
	public:
		NXEntityManager();
		~NXEntityManager();

		//
		// Import/export plugins
		//
		void loadDataImportExportPlugins(NXProperties* properties);
		NXCommandResult* importFromFile(const string& filename,
									  int frameSetId = -1, int frameIndex = 0);
		NXCommandResult* exportToFile(const string& filename,
									  int frameSetId = -1, int frameIndex = 0);
									  
		NXDataStoreInfo* getDataStoreInfo() { return dataStoreInfo; }
		
		//
		// Frame sets
		//
		int addFrameSet() {
			vector<NXMoleculeSet*> moleculeSetVector;
			moleculeSets.push_back(moleculeSetVector);
			return moleculeSets.size() - 1;
		}
		int addFrame(int frameSetId) {
			NXMoleculeSet* moleculeSet = new NXMoleculeSet();
			moleculeSets[frameSetId].push_back(moleculeSet);
			return moleculeSets[frameSetId].size() - 1;
		}
		void removeLastFrame(int frameSetId) {
			moleculeSets[frameSetId].pop_back();
		}
		unsigned int getFrameCount(int frameSetId) {
			return moleculeSets[frameSetId].size();
		}
		NXMoleculeSet* getRootMoleculeSet(int frameSetId, int frameIndex);

	private:
		NXPluginGroup* dataImpExpPluginGroup;
		string importFileTypesString, exportFileTypesString;
		map<string, NXDataImportExportPlugin*> dataImportTable;
		map<string, NXDataImportExportPlugin*> dataExportTable;
		
		NXDataStoreInfo* dataStoreInfo;
		
		vector<vector<NXMoleculeSet*> > moleculeSets;
		
		string getFileType(const string& filename);
};

} // Nanorex::

#endif
