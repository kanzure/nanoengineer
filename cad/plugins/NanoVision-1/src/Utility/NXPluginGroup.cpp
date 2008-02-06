// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Utility/NXPluginGroup.h"

namespace Nanorex {

/* CONSTRUCTOR */
/**
 * Constructs an empty NXPluginGroup
 */
NXPluginGroup::NXPluginGroup() {
}


/* DESTRUCTOR */
/**
 * Unloads all loaded plugins.
 */
NXPluginGroup::~NXPluginGroup() {
	LIBRARY_IMAGE image;
	std::map<std::string, LIBRARY_IMAGE>::iterator iter;
	iter = imageMap.begin();
	while (iter != imageMap.end()) {
		image = iter->second;
		if (image != 0) {
			NXLOG_INFO("NXPluginGroup", "Unloading " + iter->first + ".");
#ifdef WIN32
			FreeLibrary(image);
#else
			dlclose(image);
#endif
		}
		iter++;
	}
}


/* FUNCTION: load */
/**
 * Loads the library with the given name into memory.
 * If called with an already-loaded libraryFilename, it doesn't reload it, it
 * just returns successful. Error details are logged.
 *
 * Don't include any extensions in the libraryFilename, for example, use just
 * "cheeto" for cheeto.dll, or cheeto.so
 *
 * @return Whether or not the library was successfully loaded.
 */
bool NXPluginGroup::load(const char* libraryFilename) {
	char* loadError = 0;
	bool success = true;
	LIBRARY_IMAGE image;
	std::string libraryFilenameStr = std::string(libraryFilename);

	// Short-circuit if we've already loaded the library
	if (imageMap.find(libraryFilenameStr) != imageMap.end())
		return success;

	// Load the library
#if defined(_MSC_VER)
	image = LoadLibrary(libraryFilename);
	int errorCode = GetLastError();
	switch (errorCode) {
		case 126:
			loadError = "The specified module could not be found. (126)";
			break;
		case 998:
			loadError = "Invalid access to memory location. (998)";
			break;
		default:
			loadError = new char[120];
			sprintf(loadError,
					"Error %d (see http://msdn.microsoft.com/library/en-us/debug/base/system_error_codes.asp for meaning of code.)", errorCode);
			break;
	}
#elif defined(__APPLE__)
	std::string unixLibName = std::string(libraryFilename) + ".dylib";
	image = dlopen(unixLibName.c_str(), RTLD_NOW);
	loadError = (char*)(dlerror());
#else
	std::string unixLibName = std::string(libraryFilename) + ".so";
	image = dlopen(unixLibName.c_str(), RTLD_NOW);
	loadError = (char*)(dlerror());
#endif

    if (!image) {
		std::string message = "Failed attempt to load " + libraryFilenameStr;
		message += ": " + std::string(loadError);
		NXLOG_WARNING("NXPluginGroup", message);
		success = false;

    } else {
		NXLOG_INFO("NXPluginGroup", "Loaded " + libraryFilenameStr);
		imageMap[libraryFilenameStr] = image;
	}
	return success;
}


/* FUNCTION: instantiate */
/**
 * Calls the instantiate function exported by the library and returns the
 * resulting object.
 *
 * @return	null upon failure after logging details about the error, or a
 *			pointer to the Plugin object.
 */
NXPlugin* NXPluginGroup::instantiate(const char* libraryFilename) {
	char* instantiateError = 0;
	bool libraryLoaded = true;
	std::string libraryFilenameStr = std::string(libraryFilename);

	LIBRARY_IMAGE image = imageMap[libraryFilenameStr];
	if (!image) {
		NXLOG_SEVERE("NXPluginGroup",
					  "Attempt to instantiate non-loaded library: " +
							libraryFilenameStr);
		libraryLoaded = false;
	}

	NXPlugin* plugin = 0;
	if (libraryLoaded) {
		INSTANTIATE_PLUGIN instantiatePlugin =
#ifdef WIN32
			(INSTANTIATE_PLUGIN)GetProcAddress(image, "instantiate");
		int errorCode = GetLastError();
		switch (errorCode) {
			case 126:
				instantiateError = "The specified module could not be found.";
				break;
			default:
				instantiateError = new char[120];
				sprintf(instantiateError,
						"Error %d (see http://msdn.microsoft.com/library/en-us/debug/base/system_error_codes.asp for meaning of code.)", errorCode);
				break;
		}
#else
			(INSTANTIATE_PLUGIN)dlsym(image, "instantiate");
		instantiateError = (char*)(dlerror());
#endif
		if (!instantiatePlugin) {
			NXLOG_WARNING("NXPluginGroup",
						  "Failed to get handle on instantiation function for " +
							libraryFilenameStr + ": " + std::string(instantiateError));
		
		} else {
			plugin = instantiatePlugin();
			NXLOG_INFO("NXPluginGroup", "Instantiated " + libraryFilenameStr);
		}
	}
	delete[] instantiateError;
	return plugin;
}

} // Nanorex::
