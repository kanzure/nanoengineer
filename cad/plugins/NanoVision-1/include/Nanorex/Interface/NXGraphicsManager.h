// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_GRAPHICSMANAGER_H
#define NX_GRAPHICSMANAGER_H

#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
#include "NXRenderingEngine.h"
#include "NXRendererPlugin.h"

#include <QObject>

#include <map>
#include <vector>
#include <string>


namespace Nanorex {


class NXGraphicsManager : public QObject {
	
	Q_OBJECT;
	
private:
	typedef std::map<std::string, NXRendererPlugin*> RenderStyleRendererPluginTable;
	typedef std::map<std::string, std::string> StringMap;
	
public:
	
	NXGraphicsManager();
	~NXGraphicsManager();
	
	/// Discover rendering engine based on user-prefs and concomitant
	/// renderer-plugins
	void loadPlugins(NXProperties *const properties);
	
	/// List of all styles supported
	std::vector<std::string> getRenderStyles(void);
		
	NXRenderingEngine* getRenderingEngine(void);
	
	NXRendererPlugin* getRenderer(std::string const& renderStyleCode) const;
	
	std::string getRenderStyleName(std::string const& renderStyleCode);
	
	NXRendererPlugin* getDefaultRenderer(void);
	
private:
	
	NXProperties properties;
	NXRenderingEngine *renderingEngine;
	
	// Note: a render-style code, like "bas" is what we'd find in MMP files
	//       NE-1 uses 3-letter codes but the user could use arbitrarily long
	//       ones. We must provide a UI so that registering a new one does not
	//       clobber the old ones without prompting the user first.
	
	/// Map between render-style codes and plugins
	/// E.g.: "bas" <---> (NXRendererPlugin*) nxBallAndStickOpenGLRendererInstance
	RenderStyleRendererPluginTable renderStyleRendererPluginTable;
	NXRendererPlugin *defaultPlugin;
	
	/// Map between render-style codes and proper display names
	/// E.g.: "bas" <---> "Ball and Stick"
	StringMap renderStyleNameTable;
	
	/// Map between render-style codes and the file-name for the library
	/// providing the code
	StringMap renderStyleFileNameTable;
	
	void loadRenderingEngine(NXProperties *const props);
	void loadRendererPlugins(NXProperties *const props);
};

} // namespace Nanorex

#endif // NX_GRAPHICSMANAGER_H
