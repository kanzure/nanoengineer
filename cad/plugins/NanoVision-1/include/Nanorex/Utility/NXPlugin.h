// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_PLUGIN_H
#define NX_PLUGIN_H

namespace Nanorex {
	
/* CLASS: NXPlugin */
/**
 * A type of dynamically loaded library. Implementors of this class must export
 * an instantiate function with the following signature:
 *
 * \code extern "C" DLLEXPORT Nanorex::NXPlugin* instantiate(); \endcode
 *
 * Where \c DLLEXPORT is \c __declspec(dllexport) for win32 DLLs.
 *
 * @see NXPluginGroup
 * @ingroup NanorexUtility
 */
class NXPlugin {
	public:
		virtual ~NXPlugin() = 0;
};

} // Nanorex::

#endif
