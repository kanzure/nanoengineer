// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_DATASTOREINFO_H
#define NX_DATASTOREINFO_H

#include <map>
#include <string>
using namespace std;

namespace Nanorex {


/* CLASS: NXDataStoreInfo */
/**
 * Fill this out.
 *
 * @ingroup NanorexInterface PluginArchitecture
 */
class NXDataStoreInfo {
	public:
		NXDataStoreInfo() { }
		
		// Filenames
		const string& getFilename(int frameSetId) {
			return _filenames[frameSetId];
		}
		void setFilename(const string& filename, int frameSetId) {
			_filenames[frameSetId] = filename;
		}
		
		// Input structures
		void addInputStructure(string name, int frameSetId) {
			_inputStructures[name] = frameSetId;
		}
		
		// Trajectories
		void addTrajectory(string name, int frameSetId) {
			_trajectories[name] = frameSetId;
		}
		int getTrajectoryId(string name) { return _trajectories[name]; }
		//vector<string> getTrajectoryNames();
		
		// Last frame flags (whether the last frame-index is the last
		// frame in the data store.)
		void setLastFrame(int frameSetId, bool isLastFrame) {
			_isLastFrame[frameSetId] = isLastFrame;
		}
		bool isLastFrame(int frameSetId) { return _isLastFrame[frameSetId]; }
		
		// Store complete flags (whether the data store's frame set is complete
		// (true) or if something is still writing new frames to it (false.))
		void setStoreComplete(int frameSetId, bool storeIsComplete) {
			_storeIsComplete[frameSetId] = storeIsComplete;
		}
		bool storeIsComplete(int frameSetId) {
			return _storeIsComplete[frameSetId];
		}
		
		// (Data store/file) handles
		void setHandle(int frameSetId, void* handle) {
			_handle[frameSetId] = handle;
		}
		void* getHandle(int frameSetId) { return _handle[frameSetId]; }
		
	private:
		map<int, string> _filenames;
		
		// Maps input structure name to its frame set id.
		map<string, int> _inputStructures;
		
		// Maps trajectory name to its frame set id.
		map<string, int> _trajectories;
		
		// Maps frame set id to its file handle.
		map<int, void*> _handle;
		
		// Maps frame set id to its last-frame status
		map<int, bool> _isLastFrame;
		
		// Maps frame set id to its store-complete status
		map<int, bool> _storeIsComplete;
};


} // Nanorex::

#endif
