// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_PLUGINGROUP_H
#define NX_PLUGINGROUP_H

#ifdef WIN32
#	include <windows.h>
	typedef HINSTANCE LIBRARY_IMAGE;
#else
#	include <dlfcn.h>
	typedef void* LIBRARY_IMAGE;
#endif

#include <map>

#include "Nanorex/Utility/NXPlugin.h"
#include "Nanorex/Utility/NXLogger.h"

namespace Nanorex {

typedef NXPlugin* (*INSTANTIATE_PLUGIN)(void);


/* CLASS: NXPluginGroup */
/**
 * Manages a set of NXPlugins.
 * @ingroup NanorexUtility
 */
class NXPluginGroup {
	public:
		NXPluginGroup();
		~NXPluginGroup();
		bool load(const char* libraryFilename);
		NXPlugin* instantiate(const char* libraryFilename);

	private:
		std::map<std::string, LIBRARY_IMAGE> imageMap;
};

} // Nanorex::

#endif


/**
 @class Nanorex::NXPluginGroup
 xxx.
 Plugins are identified by their library names. For Win32 DLLs, the library
 name is the DLL filename without the .dll extension, for example, if the
 DLL is ConsoleCommand.dll, the library name is ConsoleCommand. For Linux, the
 library name is the shared library filename without the .so extension, for
 example, if the SO is libConsoleCommand.so, the library name is
 libConsoleCommand.

 Instantiate one NXPluginGroup, use #load to load the libraries,
 then use #instantiate to get an instantiation of the NXPlugin
 class.

 The NXPluginGroup destructor will un-load all the loaded libraries.
 */

