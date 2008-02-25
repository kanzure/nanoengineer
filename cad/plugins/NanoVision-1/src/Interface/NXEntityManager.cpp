
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXEntityManager.h"

namespace Nanorex {


/* CONSTRUCTOR */
NXEntityManager::NXEntityManager() {
	importFileTypesString = "";
	exportFileTypesString = "";
	dataStoreInfo = new NXDataStoreInfo(); 
}


/* DESTRUCTOR */
NXEntityManager::~NXEntityManager() {
	//delete rootMoleculeSet;
}


/* FUNCTION: loadDataImportExportPlugins */
/**
 * Loads and initializes all the import/export plugins.
 */
void NXEntityManager::loadDataImportExportPlugins(NXProperties* properties) {
	
	// Create a vector of QDirs from the PluginsSearchPath property
	string pluginsSearchPath = properties->getProperty("PluginsSearchPath");
	NXLOG_CONFIG("NXEntityManager",
				 string("Plugins search path: ") + pluginsSearchPath);
	vector<QDir> searchPath;
	NXStringTokenizer tokenizer(pluginsSearchPath, ";");
	while (tokenizer.hasMoreTokens())
		searchPath.push_back(QDir(tokenizer.getNextToken().c_str()));
	
	
	// Initialize for first plugin
	int pluginIndex = 0;
	string msg, pluginFormats;
	string pluginKey = "ImportExport.0";
	string pluginLibrary =
		string(properties->getProperty(pluginKey + ".plugin"));
	if (pluginLibrary.length() == 0) {
		msg = "No Data Import/Export plugins to load.";
		cout << "WARNING: " << msg << endl;
		NXLOG_WARNING("NXEntityManager", msg);
	}
	
	// Iterate over discovered plugins and load them
	bool fileExists = false;
	vector<QDir>::iterator iter;
	QString absPluginLibrary;
	QObject* pluginObject = 0;
	NXDataImportExportPlugin* plugin = 0;
	while (pluginLibrary.length() != 0) {
#if defined(WIN32)
		pluginLibrary += ".dll";
#elif defined(__APPLE__)
		pluginLibrary += ".dylib";
#else
		pluginLibrary += ".so";
#endif

		// Find the plugin file
		fileExists = false;
		iter = searchPath.begin();
		while (!fileExists && iter != searchPath.end()) {
			absPluginLibrary = (*iter).absoluteFilePath(pluginLibrary.c_str());
			if (QFileInfo(absPluginLibrary).exists())
				fileExists = true;
			iter++;
		}
		
		if (fileExists) {
			QPluginLoader loader(absPluginLibrary);
			pluginObject = loader.instance();
			
		} else {
			msg =
				"Couldn't load Data Import/Export plugin (file not found): " +
				pluginLibrary;
			NXLOG_WARNING("NXEntityManager", msg);
			pluginObject = 0;
		}

		if (pluginObject == 0) {
			msg =
				"Couldn't load Data Import/Export plugin: " + pluginLibrary;
			NXLOG_WARNING("NXEntityManager", msg);

		} else {
			plugin = qobject_cast<NXDataImportExportPlugin*>(pluginObject);
			
			// Import formats registration
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".importFormats"));
			if (importFileTypesString.length() == 0)
				importFileTypesString = pluginFormats;
			else
				importFileTypesString.append(";;").append(pluginFormats);
			int index1 = pluginFormats.find("(");
			int index2 = 0;
			string formats, format;
			while (index1 > 0) {
				index2 = pluginFormats.find(")", index1 + 1);
				formats = pluginFormats.substr(index1 + 1, index2 - index1 - 1);
				NXStringTokenizer tokenizer(formats, " ");
				while (tokenizer.hasMoreTokens()) {
					format = tokenizer.getNextToken();
					// Remove the "*."
					format = format.substr(2);
					dataImportTable[format] = plugin;
				}
				index1 = pluginFormats.find("(", index2 + 1);
			}

			// Export formats registration
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".exportFormats"));
			if (exportFileTypesString.length() == 0)
				exportFileTypesString = pluginFormats;
			else
				exportFileTypesString.append(";;").append(pluginFormats);
			index1 = pluginFormats.find("(");
			index2 = 0;
			while (index1 > 0) {
				index2 = pluginFormats.find(")", index1 + 1);
				formats = pluginFormats.substr(index1 + 1, index2 - index1 - 1);
				NXStringTokenizer tokenizer(formats, " ");
				while (tokenizer.hasMoreTokens()) {
					format = tokenizer.getNextToken();
					// Remove the "*."
					format = format.substr(2);
					dataExportTable[format] = plugin;
				}
				index1 = pluginFormats.find("(", index2 + 1);
			}
			msg = "Loaded plugin: " + pluginLibrary;
			NXLOG_INFO("NXEntityManager", msg);
		}
		pluginIndex++;
		pluginKey =
			string("ImportExport.") +
			NXUtility::itos(pluginIndex);
		pluginLibrary =
			string(properties->getProperty(pluginKey + ".plugin"));
	}
}


/* FUNCTION: importFromFile */
/**
 * @param frameSetId	If -1, import all frames into a new frame set,
 *						otherwise, resume importing into the given frame set.
 */
NXCommandResult* NXEntityManager::importFromFile(const string& filename,
												 int frameSetId,
												 bool inPollingThread,
												 bool inRecursiveCall) {
	NXCommandResult* result;
	//PR_Lock(importExportPluginsMutex);
	
	string fileType = getFileType(filename);
	
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataImportTable.find(fileType);
	if (iter != dataImportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;
		
		if (frameSetId == -1)
			frameSetId = addFrameSet();
		if (!inPollingThread && !inRecursiveCall)
			dataStoreInfo->setFileName(filename, frameSetId);
		int frameIndex = getFrameCount(frameSetId);
		NXMoleculeSet* moleculeSet = new NXMoleculeSet();

		try {
			result =
				plugin->importFromFile(moleculeSet,
									   dataStoreInfo, filename, frameSetId,
									   frameIndex);
			
			if (result->getResult() == NX_CMD_SUCCESS) {
				QFileInfo fileInfo(filename.c_str());
			
				// Delete the molecule (and don't add the frame) if the
				// molecule set wasn't populated.
				if ((moleculeSet->childCount() == 0) &&
					(moleculeSet->moleculeCount() == 0)) {
					delete moleculeSet;
					
				} else {
					frameIndex = addFrame(frameSetId, moleculeSet);
					if (inPollingThread) {
						NXLOG_DEBUG("NXEntityManager", "emit newFrameAdded()");
						emit newFrameAdded(frameSetId, frameIndex, moleculeSet);
					}
					
					// Update the frameSetId stored in the dataStoreInfo if this
					// is an input file for a simulation results data store.
					if (inRecursiveCall) {
						string inputFileName = qPrintable(fileInfo.fileName());
						if (dataStoreInfo->getInputStructureId(inputFileName)
								== -1)
							dataStoreInfo->setInputStructureId(inputFileName,
															   frameSetId);
					}
				}
				
				// Read more frames if available
				while (!inRecursiveCall &&
					   (!dataStoreInfo->isLastFrame(frameSetId)) &&
					   (result->getResult() == NX_CMD_SUCCESS)) {
					frameIndex = addFrame(frameSetId);
					result =
						plugin->importFromFile(getRootMoleculeSet(frameSetId,
																  frameIndex),
											   dataStoreInfo, filename,
											   frameSetId, frameIndex);
					if (inPollingThread) {
						NXLOG_DEBUG("NXEntityManager", "emit newFrameAdded()");
						emit newFrameAdded(frameSetId, frameIndex,
										   getRootMoleculeSet(frameSetId,
										   					  frameIndex));
					}
											   
					// TODO: handle result == failed
				}
			
				// Examine the dataStoreInfo for additional files to import
				if (!inPollingThread && !inRecursiveCall) {
					NXCommandResult* _result;
					vector<string> inputFileNames =
						dataStoreInfo->getInputFileNames();
					vector<string>::iterator iter = inputFileNames.begin();
					while (iter != inputFileNames.end()) {
						if (dataStoreInfo->getInputStructureId(*iter) == -1) {
							// Load input file
							/*
							QString inputFileName =
								QString("%1/%2").arg(fileInfo.absolutePath())
												.arg((*iter).c_str());
												*/
							_result =
								importFromFile(*iter,
											   -1 /* frameSetId */,
											   inPollingThread,
											   !inRecursiveCall);
								
							// Set the dataStoreInfo back to a simulation
							// results data store
							dataStoreInfo->setIsSimulationResults(true);
							
							if (_result->getResult() != NX_CMD_SUCCESS) {
								QString logMessage =
									tr("Couldn't load input file: %1")
										.arg(GetNV1ResultCodeString(_result));
								NXLOG_WARNING("NXEntityManager",
											  qPrintable(logMessage));
							} else {
								QString logMessage =
									tr("Input file loaded: %1")
										.arg((*iter).c_str());
								NXLOG_INFO("NXEntityManager",
										   qPrintable(logMessage));
							}
						}
						iter++;
					}
				}
				
				// Spawn a thread to keep reading incomplete data stores
				// as necessary
				if (!inPollingThread && !inRecursiveCall &&
					!dataStoreInfo->storeIsComplete(frameSetId)) {
					DataStorePollingThread* pollingThread =
						new DataStorePollingThread(this, frameSetId);
					pollingThread->start();
				}
				
			} else
				delete moleculeSet;
				
			if (inPollingThread && dataStoreInfo->storeIsComplete(frameSetId)) {
				NXLOG_DEBUG("NXEntityManager", "emit dataStoreComplete()");
				emit dataStoreComplete();
			}

		} catch (...) {
			delete moleculeSet;
			
			string msg = fileType;
			msg += "->importFromFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result = new NXCommandResult();
			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = fileType.c_str();
			pluginDescriptor.append("->importFromFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		string msg =
			"importFromFile: no NXDataImportExportPlugin found to handle type: " +
			fileType;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(fileType.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}


/* FUNCTION: exportToFile */
/**
 * Exports the system to the specified file with the appropriate
 * import/export plugin.
 *
 * @param frameSetId	The identifier of the frame set to export. If frameSetId
 *						is -1, write all framesets.
 * @param frameIndex	The frame to export. If frameIndex is -1, write all
 *						frames.
 */
NXCommandResult* NXEntityManager::exportToFile
		(const string& filename, int frameSetId, int frameIndex) {
	/*
	 * NOTE: We don't explicitly handle frameSetId == -1 (export all frame sets)
	 *		 yet. This would be File | Export | Entire results...
	 */
		
	NXCommandResult* result = 0;
	//PR_Lock(importExportPluginsMutex);
	
	// TODO: Abort if there are no molecule sets, general error checking.
	
	string fileType = getFileType(filename);
	
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataExportTable.find(fileType);
	if (iter != dataExportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;
		try {
			bool allFrameExport = (frameIndex == -1);
			if (allFrameExport)
				frameIndex = 0;
			dataStoreInfo->setLastFrame
				(frameSetId,
				 !allFrameExport ||
					(frameIndex > (int)moleculeSets[frameSetId].size() - 2));
			vector<NXMoleculeSet*>::iterator iter =
				moleculeSets[frameSetId].begin();
			result =
				plugin->exportToFile(*iter, dataStoreInfo, filename,
									 frameSetId, frameIndex);
			iter++;
			frameIndex++;
			while (allFrameExport &&
				   (iter != moleculeSets[frameSetId].end()) &&
				   (result->getResult() == NX_CMD_SUCCESS)) {
				dataStoreInfo->setLastFrame
					(frameSetId,
					 frameIndex > (int)moleculeSets[frameSetId].size() - 2);
				result =
					plugin->exportToFile(*iter, dataStoreInfo, filename,
										 frameSetId, frameIndex);
				iter++;
				frameIndex++;
			}
			if (result->getResult() != NX_CMD_SUCCESS)
				NXLOG_SEVERE("NXEntityManager",
							 qPrintable(GetNV1ResultCodeString(result)));

		} catch (...) {
			string msg = fileType;
			msg += "->exportToFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			std::vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = fileType.c_str();
			pluginDescriptor.append("->exportToFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		std::string msg =
			"exportToFile: no DataImportExportPlugin found to handle type: " +
			fileType;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		// %1 Who is reporting
		// %2 The name of the plugin that was not found
		// %3 Why the plugin was not found
		std::vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(fileType.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}


/* FUNCTION: getFileType */
string NXEntityManager::getFileType(const string& filename) {
	int index = filename.rfind(".");
	if (index > 0)
		return filename.substr(index + 1);
	else
		return "";
}

} // Nanorex::
