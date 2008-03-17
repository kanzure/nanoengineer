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

// Temporary
#include <Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.h>

namespace Nanorex {

class DataStorePollingThread;
	

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
    
		void reset(void);
		
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
		
		// TODO: Generalize the concept of plugin-provided tools
		NXCommandResult* fixHDF5_DataStore(const string& filename);

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
		DataStorePollingThread* pollingThread;
		
		QMutex frameAccessMutex;
		vector<vector<NXMoleculeSet*> > moleculeSets;
		
		map<int, bool> storeIsComplete_Emitted;
		
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
		_stop = false;
	}
	
	void run() {
		NXCommandResult* result = 0;
		NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
		while (!_stop &&
				(!dataStoreInfo->storeIsComplete(frameSetId) ||
				 !dataStoreInfo->isLastFrame(frameSetId))) {
				
			// See if there's a new frame
			result =
				entityManager->importFromFile
					(dataStoreInfo->getFileName(frameSetId), frameSetId,
												true); // inPollingThread
		
			// TODO: Handle if result != 0
			// TODO: Fix - why does NV1 crash on Win32 when we emit this logging
			//       message?
			if (result->getResult() != NX_CMD_SUCCESS) {
				printf("DataStorePollingThread: %s\n",
					   qPrintable(GetNV1ResultCodeString(result)));
			/*
				NXLOG_WARNING("DataStorePollingThread",
							  qPrintable(GetNV1ResultCodeString(result)));
			*/
			}
			delete result;
			
			msleep(500);//100);
printf("DataStorePollingThread: stop=%d storeComplete=%d lastFrame=%d\n", _stop,dataStoreInfo->storeIsComplete(frameSetId),dataStoreInfo->isLastFrame(frameSetId));fflush(0); 
		}
	}
	
	void stop() {
printf("DataStorePollingThread::stop()\n");
		_stop = true;
	}
	
private:
	int frameSetId;
	bool _stop;
	NXEntityManager* entityManager;
};

} // Nanorex::

#endif
