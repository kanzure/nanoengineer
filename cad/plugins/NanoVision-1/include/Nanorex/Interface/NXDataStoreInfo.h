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
		
		void addTrajectory(string name, int id) { _trajectories[name] = id; }
		int getTrajectoryId(string name) { return _trajectories[name]; }
		//vector<string> getTrajectoryNames();
		
		void setLastFrame(int id, bool isLastFrame) {
			_isLastFrame[id] = isLastFrame;
		}
		bool isLastFrame(int id) { return _isLastFrame[id]; }
		
		void setStoreComplete(int id, bool storeIsComplete) {
			_storeIsComplete[id] = storeIsComplete;
		}
		bool storeIsComplete(int id) { return _storeIsComplete[id]; }
		
		void setHandle(int id, void* handle) { _handle[id] = handle; }
		void* getHandle(int id) { return _handle[id]; }
		
	private:
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
