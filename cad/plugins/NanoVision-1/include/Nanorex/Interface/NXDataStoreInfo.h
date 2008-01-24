// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_DATASTOREINFO_H
#define NX_DATASTOREINFO_H

namespace Nanorex {


/* CLASS: NXDataStoreInfo */
/**
 * Fill this out.
 *
 * @ingroup NanorexInterface PluginArchitecture
 */
class NXDataStoreInfo {
	public:
		NXDataStoreInfo() { _isLastFrame = true; }
		
		void setLastFrame(bool isLastFrame) { _isLastFrame = isLastFrame; }
		bool isLastFrame() { return _isLastFrame; }
		
		void setHandle(void* handle) { this->handle = handle; }
		void* getHandle() { return handle; }
		
	private:
		void* handle;
		bool _isLastFrame;
};


} // Nanorex::

#endif
