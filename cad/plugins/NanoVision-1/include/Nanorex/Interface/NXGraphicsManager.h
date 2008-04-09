// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_GRAPHICSMANAGER_H
#define NX_GRAPHICSMANAGER_H

#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
#include "NXRenderingEngine.h"
#include "NXRendererPlugin.h"

#include <QObject>
#include <QDir>
#include <QFileInfo>

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
	bool loadPlugins(NXProperties *const properties);
	
	/// List of all styles supported
	std::vector<std::string> getRenderStyles(void);
		
	NXRenderingEngine* getRenderingEngine(void) { return renderingEngine; }
	
	/// Pointer to renderer-plugin instance that handles the given style, NULL
	/// if style-renderer combination was not registered
	NXRendererPlugin* getRenderer(std::string const& renderStyleCode) const;
	
	std::string getRenderStyleName(std::string const& renderStyleCode);
	
	NXRendererPlugin* getDefaultRenderer(void) { return defaultRenderer; }
	
	/// Create a new rendering-engine instance initialized in the context of
	/// the supplied parent widget, complete with renderer-plugins initialized
	/// in its context
	NXRenderingEngine *newGraphicsInstance(QWidget *parent);
	
protected:
	
	NXProperties properties;
	NXRenderingEngine *renderingEngine;
	
	// Note: a render-style code, like "bas" is what we'd find in MMP files
	//       NE-1 uses 3-letter codes but the user could use arbitrarily long
	//       ones. We must provide a UI so that registering a new one does not
	//       clobber the old ones without prompting the user first.
	
	/// Map between render-style codes and plugins
	/// E.g.: "bas" <---> (NXRendererPlugin*) nxBallAndStickOpenGLRendererInstance
	RenderStyleRendererPluginTable renderStyleRendererPluginTable;
	
	NXRendererPlugin *defaultRenderer;
	
	/// Map between render-style codes and proper display names
	/// E.g.: "bas" <---> "Ball and Stick"
	StringMap renderStyleNameTable;
	
	/// Map between render-style codes and the file-name for the library
	/// providing the code
	StringMap renderStyleFileNameTable;
	
	void reset(void);
	
	bool loadRenderingEngine(NXProperties *const props);
	bool loadRendererPlugins(NXProperties *const props);
	
	template<typename PluginType>
		bool findAndLoadPlugin(string const& baseName, string const& path,
		                       string const& pluginsSearchPath,
		                       PluginType **pluginStore, QDir *cleanPath,
		                       string *absPath);
	
	bool loadPlugin(NXRenderingEngine **pluginStore, QFileInfo const& fileInfo);
	bool loadPlugin(NXRendererPlugin **pluginStore, QFileInfo const& fileInfo);
	
	void detectDefaultRenderer(NXProperties *const props);
	void printDiagnosticLogs(void);
};

} // namespace Nanorex

#endif // NX_GRAPHICSMANAGER_H
