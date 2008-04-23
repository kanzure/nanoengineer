
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXDataStoreInfo.h"

namespace Nanorex {


/* CONSTRUCTOR */
NXDataStoreInfo::NXDataStoreInfo() 
    : _isSimulationResults(false),
    _isSingleStructure(false),
    _inputParameters(NULL),
    _resultsSummary(NULL),
	_clipboardStructure(NULL)
{
}


NXDataStoreInfo::~NXDataStoreInfo()
{
	reset(); // will also release owned resources, like clipboard data
}


/* FUNCTION: reset */
void NXDataStoreInfo::reset(void)
{
    _fileNames.clear();
    _inputStructures.clear();
    _trajectories.clear();
    _handle.clear();
    _isLastFrame.clear();
    _storeIsComplete.clear();
    _isSimulationResults = false;
    _isSingleStructure = false;
    if(_inputParameters != NULL) delete _inputParameters;
    if(_resultsSummary != NULL) delete _resultsSummary;
    _inputParameters = _resultsSummary = NULL;
	if(_clipboardStructure != NULL) delete _clipboardStructure;
	_clipboardStructure = NULL;
	homeView.setName("");
	lastView.setName("");
	otherViews.clear();
}


/* FUNCTION: isSingleStructure */
/*
 * @return	True if this data store has only a single frame of structure
 *			data such as in an MMP or PDB file.
 */
bool NXDataStoreInfo::isSingleStructure() { return _isSingleStructure; }


/* FUNCTION: setIsSingleStructure */
void NXDataStoreInfo::setIsSingleStructure(bool _isSingleStructure) {
	this->_isSimulationResults = !_isSingleStructure;
	this->_isSingleStructure = _isSingleStructure;
}


/* FUNCTION: getSingleStructureFileName */
const string& NXDataStoreInfo::getSingleStructureFileName() {
	return (*(_fileNames.begin())).second;
}

		
/* FUNCTION: getSingleStructureId */
int NXDataStoreInfo::getSingleStructureId() {
	return (*(_fileNames.begin())).first;
}


/* FUNCTION: isSimulationResults */
/*
 * @return	True if this data store encapsulates simulation results.
 */
bool NXDataStoreInfo::isSimulationResults() { return _isSimulationResults; }


/* FUNCTION: setIsSimulationResults */
void NXDataStoreInfo::setIsSimulationResults(bool _isSimulationResults) {
	this->_isSimulationResults = _isSimulationResults;
	this->_isSingleStructure = !_isSimulationResults;
}


/* FUNCTION: getInputParameters */
/*
 * @return	Null if this data store doens't have any input parameters.
 */
NXProperties* NXDataStoreInfo::getInputParameters() {
	return _inputParameters;
}


/* FUNCTION: setInputParameters */
void NXDataStoreInfo::setInputParameters(NXProperties* parameters) {
	_inputParameters = parameters;
}


/* FUNCTION: getInputFileNames */
/*
 * @return	A vector of input file names. The vector will be empty if
 *			there are no input file names in this data store.
 */
vector<string> NXDataStoreInfo::getInputFileNames() {
	map<string, int>::iterator iter = _inputStructures.begin();
	vector<string> names;
	while (iter != _inputStructures.end()) {
		names.push_back((*iter).first);
		iter++;
	}
	return names;
}


/* FUNCTION: addInputStructure */
void NXDataStoreInfo::addInputStructure(const string& fileName) {
	_inputStructures[fileName] = -1;
}


/* FUNCTION: getInputStructureId */
/*
 * @return The frame set identifier for the given input structure file name.
 */
int NXDataStoreInfo::getInputStructureId(const string& fileName) {
	return _inputStructures[fileName];
}


/* FUNCTION: setInputStructureId */
void NXDataStoreInfo::setInputStructureId(const string& fileName,
										  int frameSetId) {
	_inputStructures[fileName] = frameSetId;
}


/* FUNCTION: getResultsSummary */
/*
 * @return	Null if this data store doesn't have any results summary data.
 */
NXProperties* NXDataStoreInfo::getResultsSummary() {
	return _resultsSummary;
}


/* FUNCTION: setResultsSummary */
void NXDataStoreInfo::setResultsSummary(NXProperties* resultsSummary) {
	if (_resultsSummary != NULL)
		delete _resultsSummary;
	_resultsSummary = resultsSummary;
}


/* FUNCTION: getTrajectoryNames */
/*
 * @return	A vector of trajectory names. The vector will be empty if
 *			there are no trajectories in this data store.
 */
vector<string> NXDataStoreInfo::getTrajectoryNames() {
	map<string, int>::iterator iter = _trajectories.begin();
	vector<string> names;
	while (iter != _trajectories.end()) {
		names.push_back((*iter).first);
		iter++;
	}
	return names;
}


/* FUNCTION: addTrajectory */
void NXDataStoreInfo::addTrajectory(const string& name, int frameSetId) {
	_trajectories[name] = frameSetId;
}


/* FUNCTION: getTrajectoryId */
int NXDataStoreInfo::getTrajectoryId(const string& name) {
	return _trajectories[name];
}


/* FUNCTION: setLastFrame */
/*
 * Last frame flags (whether the last frame-index is the last
 * frame available in the data store, ie, stop trying to read frames
 * (for now.))
 */
void NXDataStoreInfo::setLastFrame(int frameSetId, bool isLastFrame) {
	_isLastFrame[frameSetId] = isLastFrame;
}


/* FUNCTION: isLastFrame */
bool NXDataStoreInfo::isLastFrame(int frameSetId) {
	return _isLastFrame[frameSetId];
}


/* FUNCTION: storeIsComplete */
/*
 * @return	True if the frame set specified by the frameSetId is
 *			complete, and false if something is still writing frames
 *			to the specified frame set.
 */
bool NXDataStoreInfo::storeIsComplete(int frameSetId) {
	return _storeIsComplete[frameSetId];
}


/* FUNCTION: setStoreComplete */
/*
 * Store complete flags (whether the data store's frame set is complete
 * (true) or if something is still writing new frames to it (false.))
 */
void NXDataStoreInfo::setStoreComplete(int frameSetId, bool storeIsComplete) {
	_storeIsComplete[frameSetId] = storeIsComplete;
}

// TODO: check for existence in getters

/* FUNCTION: getFileName */
const string& NXDataStoreInfo::getFileName(int frameSetId) {
	return _fileNames[frameSetId];
}


/* FUNCTION: setFileName */
void NXDataStoreInfo::setFileName(const string& filename, int frameSetId) {
	_fileNames[frameSetId] = filename;
}


/* FUNCTION: setHandle */
/*
 * (Data store/file) handles
 */
void NXDataStoreInfo::setHandle(int frameSetId, void* handle) {
	_handle[frameSetId] = handle;
}


/* FUNCTION: getHandle */
void* NXDataStoreInfo::getHandle(int frameSetId) { return _handle[frameSetId]; }


} // Nanorex::
