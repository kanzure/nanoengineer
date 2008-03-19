// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <Nanorex/Interface/NXGraphicsManager.h>
#include <Nanorex/Utility/NXStringTokenizer.h>

#include <QDir>
#include <QFileInfo>
#include <QPluginLoader>

#include <sstream>

using namespace std;

namespace Nanorex {

NXGraphicsManager::NXGraphicsManager()
	: properties(),
	renderingEngine(NULL),
	renderStyleRendererPluginTable(),
	renderStyleNameTable(),
	renderStyleFileNameTable()
{
}


NXGraphicsManager::~NXGraphicsManager()
{
}


void NXGraphicsManager::loadPlugins(NXProperties *const props)
{
	loadRenderingEngine(props);
	loadRendererPlugins(props);
}


/// Called by findAndLoadPlugin() to load a plugin from an existing file.
/// Returns false if qobject_cast() failed indicating that plugin does not
/// match the expected interface. If successful, then the pointer referenced
/// by pluginStore is updated to point to the loaded instance.
/// This function is called to load both the rendering-engine and renderer-plugins
template<typename PluginType>
	static bool loadPlugin(PluginType **pluginStore,
	                       QFileInfo const fileInfo)
{
	QPluginLoader pluginLoader(fileInfo.absoluteFilePath());
	QObject *pluginObject = pluginLoader.instance();
	/// @fixme Uncomment and commit after testing builds with NXRenderingEngine
	/// Qt-plugin modifications go through
/*	if(pluginObject != (QObject*) 0)
		*pluginStore = qobject_cast<PluginType*>(pluginObject);
	else */
		*pluginStore = (PluginType*) 0;
	
	bool success = ((*pluginStore) != (PluginType*)0);
	return success;
}


/// Locates and loads a plugin given the basename of the file and an initial
/// path to examine. If a load from the initial path is unsuccessful or if the
/// path provided is empty, then it retrieves the plugins-search-path
/// from application-settings and searches it in order for the first file it
/// could successfully find and load. If an engine could be successfully loaded
/// then it returns true and the plugin-pointer referenced by pluginStore is
/// updated to point to the loaded instance. cleanPath then holds the absolute
/// directory specification and absPath holds the full path to the library file.
template<typename PluginType>
	static bool findAndLoadPlugin(string const& baseName, string const& path,
	                              string const& pluginsSearchPath,
	                              PluginType **pluginStore, QDir *cleanPath,
	                              string *absPath)
{
#if defined(WIN32)
	string const fileExt = ".dll";
#elif defined(__APPLE__)
	string const fileExt = ".dylib";
#else
	string const fileExt = ".so";
#endif
	
	string const fileName = baseName + fileExt;
	bool pluginFoundAndLoaded = false;
	
	if(!path.empty()) {
		// user-defined specific path for this plugin - search this first
		*cleanPath = QDir(path.c_str()).absolutePath();
		QFileInfo fileInfo(cleanPath->absoluteFilePath(fileName.c_str()));
		*absPath = qPrintable(fileInfo.absoluteFilePath());
		bool const pluginFound = fileInfo.exists();
		bool pluginLoaded = false;
		if(pluginFound)
			pluginLoaded = loadPlugin(pluginStore, fileInfo);
		pluginFoundAndLoaded = pluginFound && pluginLoaded;
		if(!pluginFoundAndLoaded) {
			string const pluginNotFoundMsg = "Could not find renderer-plugin " +
				fileName + " in specific path " +
				qPrintable(cleanPath->absolutePath()) +
				" - examining plugins-search-path from application-settings";
			NXLOG_WARNING("NXGraphicsManager", pluginNotFoundMsg);
		}
	}
	
	if(!pluginFoundAndLoaded) {
		// either plugin was not found in given path or no specific path was
		// provided for the plugin - search in plugin-paths list
		NXStringTokenizer tokenizer(pluginsSearchPath, ";");
		while(!pluginFoundAndLoaded && tokenizer.hasMoreTokens()) {
			string const token = tokenizer.getNextToken();
			*cleanPath = QDir(token.c_str()).absolutePath();
			QFileInfo fileInfo(cleanPath->absoluteFilePath(fileName.c_str()));
			*absPath = qPrintable(fileInfo.absoluteFilePath());
			bool const pluginFound = fileInfo.exists();
			bool pluginLoaded = false;
			if(pluginFound)
				pluginLoaded = loadPlugin(pluginStore, fileInfo);
			pluginFoundAndLoaded = pluginFound && pluginLoaded;
		}
		if(!pluginFoundAndLoaded) {
			string const pluginNotFoundMsg = "Could not find renderer-plugin " +
				fileName + " in paths " + pluginsSearchPath;
			NXLOG_SEVERE("NXGraphicsManager", pluginNotFoundMsg);
		}
	}
	
	return pluginFoundAndLoaded;
}



/// Loads the rendering-engine from application settings
void NXGraphicsManager::loadRenderingEngine(NXProperties *const props)
{
	/// @fixme What if pluginsSearchPath is empty?

	string baseName = props->getProperty("RenderingEngine.plugin");
	string filePath = props->getProperty("RenderingEngine.pluginPath");
	string const pluginsSearchPath =
		props->getProperty("Miscellaneous/PluginsSearchPath");
	
	QDir cleanPath;
	string absPath;
	bool renderingEngineLoaded = findAndLoadPlugin(baseName, filePath,
	                                               pluginsSearchPath,
	                                               &renderingEngine,
	                                               &cleanPath, &absPath);
	
	if(renderingEngineLoaded) {
		properties.setProperty("RenderingEngine.plugin",
							qPrintable(cleanPath.absolutePath()));
		string const msg = "Rendering-engine loaded from file " + absPath;
		NXLOG_INFO("NXGraphicsManager", msg);
	}
}


void NXGraphicsManager::loadRendererPlugins(NXProperties *const props)
{
	string const pluginsSearchPath =
		props->getProperty("Miscellaneous/PluginsSearchPath");
	
	int pluginNum = 0; // counter
	
	while(true) {
		ostringstream pluginKeyStream;
		pluginKeyStream << "RenderStyle." << pluginNum;
		++pluginNum;
		string const pluginKey = pluginKeyStream.str();
		string const pluginCode = props->getProperty(pluginKey + ".code");
		string pluginBaseName = props->getProperty(pluginKey + ".plugin");
		
		// if code and plugin filename are absent then there are no more plugins
		if(pluginCode.empty() && pluginBaseName.empty())
			break;
		
		// else if only one of them is mentioned then error condition
		else if(pluginCode.empty() || pluginBaseName.empty()) {
			// error condition, both are required, only one is present
			string msg = "Both render-style code and plugin library filename "
				"must be provided for " + pluginKey + " (check app-settings file)";
			NXLOG_SEVERE("NXGraphicsManager", msg);
			// this could be a mistake with just this plugin-spec, continue
			// with next plugin - maybe that one is ok
			continue;
		}
		
		// both code and plugin file have values - try to load
		else {
			string const pluginPath =
				props->getProperty(pluginKey + ".pluginPath");
			
			QDir cleanPath;
			string absPath;
			NXRendererPlugin *rendererPlugin = NULL;
			bool const rendererPluginLoaded =
				findAndLoadPlugin(pluginBaseName, pluginPath, pluginsSearchPath,
				                  &rendererPlugin, &cleanPath, &absPath);
			
			// if successful, record entries in tables
			if(rendererPluginLoaded) {
				string pluginName = props->getProperty(pluginKey + ".name");
				if(pluginName.empty())
					pluginName = pluginCode;
				properties.setProperty("Renderer."+pluginCode+".plugin",
				                       absPath);
				properties.setProperty("Renderer."+pluginCode+".name",
				                       pluginName);
				renderStyleRendererPluginTable[pluginCode] = rendererPlugin;
				renderStyleNameTable[pluginCode] = pluginName;
				renderStyleFileNameTable[pluginCode] = absPath;
				// break out of plugin-search loop upon first successful load
				break;
			}
		}
	}
}


vector<string> NXGraphicsManager::getRenderStyles(void)
{
	vector<string> renderStyles;
	RenderStyleRendererPluginTable::const_iterator renderStyleTableIter;
	for(renderStyleTableIter = renderStyleRendererPluginTable.begin();
	    renderStyleTableIter != renderStyleRendererPluginTable.end();
	    ++renderStyleTableIter)
	{
		renderStyles.push_back(renderStyleTableIter->first);
	}
	return renderStyles;
}


NXRendererPlugin*
	NXGraphicsManager::getRenderer(string const& renderStyleCode) const
{
	RenderStyleRendererPluginTable::const_iterator renderStyleCodeIter =
		renderStyleRendererPluginTable.find(renderStyleCode);
	if(renderStyleCodeIter == renderStyleRendererPluginTable.end())
		return (NXRendererPlugin*) NULL;
	else
		return renderStyleCodeIter->second;
}


string NXGraphicsManager::getRenderStyleName(string const& renderStyleCode)
{
	StringMap::const_iterator renderStyleCodeIter =
		renderStyleNameTable.find(renderStyleCode);
	if(renderStyleCodeIter == renderStyleNameTable.end())
		return string();
	else
		return renderStyleCodeIter->second;
}

} // namespace Nanorex
