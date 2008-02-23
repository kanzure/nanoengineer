// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <vector>
#include <string>
using namespace std;

#include <QDir>
#include <QMutex>
#include <QObject>
#include <QString>
#include <QThread>
#include <QPluginLoader>

#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
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
class NXEntityManager : public QObject {
	
	Q_OBJECT
	
	public:
		NXEntityManager();
		~NXEntityManager();

		//
		// Import/export plugins
		//
		void loadDataImportExportPlugins(NXProperties* properties);
		NXCommandResult* importFromFile(const string& filename,
										int frameSetId = -1,
										bool inPollingThread = false,
										bool inRecursiveCall = false);
		NXCommandResult* exportToFile(const string& filename,
									  int frameSetId = -1, int frameIndex = 0);

		const string& getImportFileTypes() { return importFileTypesString; }
		const string& getExportFileTypes() { return exportFileTypesString; }
		NXDataStoreInfo* getDataStoreInfo() { return dataStoreInfo; }
		
		//
		// Frame sets
		//
		int addFrameSet() {
			vector<NXMoleculeSet*> moleculeSetVector;
			moleculeSets.push_back(moleculeSetVector);
			int frameSetId = moleculeSets.size() - 1;
			dataStoreInfo->setLastFrame(frameSetId, true);
			dataStoreInfo->setStoreComplete(frameSetId, true);
			return frameSetId;
		}
		int addFrame(int frameSetId, NXMoleculeSet* moleculeSet = 0) {
			QMutexLocker locker(&frameAccessMutex);			
			if (moleculeSet == 0)
				moleculeSet = new NXMoleculeSet();
			moleculeSets[frameSetId].push_back(moleculeSet);
			return moleculeSets[frameSetId].size() - 1;
		}
		unsigned int getFrameCount(int frameSetId) {
			QMutexLocker locker(&frameAccessMutex);
			return moleculeSets[frameSetId].size();
		}
		NXMoleculeSet* getRootMoleculeSet(int frameSetId, int frameIndex) {
			QMutexLocker locker(&frameAccessMutex);
			if (frameIndex < (int)moleculeSets[frameSetId].size())
				return moleculeSets[frameSetId][frameIndex];
			else
				return 0;
		}

	signals:
		// Emitted when a new frame is added from the thread that polls
		// growing frame sets.
		void newFrameAdded(int frameSetId, int frameIndex,
						   NXMoleculeSet* moleculeSet);
		void dataStoreComplete();

	private:
		string importFileTypesString, exportFileTypesString;
		map<string, NXDataImportExportPlugin*> dataImportTable;
		map<string, NXDataImportExportPlugin*> dataExportTable;
		
		NXDataStoreInfo* dataStoreInfo;
		
		QMutex frameAccessMutex;
		vector<vector<NXMoleculeSet*> > moleculeSets;
		
		string getFileType(const string& filename);
};


/* CLASS: DataStorePollingThread */
/**
 * Used internally by NXEntityManager.
 */
class DataStorePollingThread : public QThread {
	
public:
	DataStorePollingThread(NXEntityManager* entityManager, int frameSetId)
			: QThread() {
		this->entityManager = entityManager;
		this->frameSetId = frameSetId;
	}
	
	void run() {
		NXCommandResult* result = 0;
		NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
		while (!dataStoreInfo->storeIsComplete(frameSetId) ||
			   !dataStoreInfo->isLastFrame(frameSetId)) {
				
			// See if there's a new frame
			result =
				entityManager->importFromFile
					(dataStoreInfo->getFileName(frameSetId), frameSetId,
												true); // inPollingThread
		
			// TODO: Handle if result != 0
			
			msleep(100);
		}
	}
	
private:
	int frameSetId;
	NXEntityManager* entityManager;
};

} // Nanorex::

#endif
