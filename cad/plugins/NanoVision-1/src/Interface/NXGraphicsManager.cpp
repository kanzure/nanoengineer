// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <Nanorex/Interface/NXGraphicsManager.h>
#include <Nanorex/Utility/NXStringTokenizer.h>

#include <QPluginLoader>

#include <sstream>

#ifdef NX_DEBUG
#define NX_DEBUG_FAIL  assert(0);
#else
#define NX_DEBUG_FAIL
#endif


using namespace std;

namespace Nanorex {

/* CONSTRUCTOR */
NXGraphicsManager::NXGraphicsManager()
	: properties(),
	renderingEngine(NULL),
	renderStyleRendererPluginTable(),
	defaultRenderer(NULL),
	renderStyleNameTable(),
	renderStyleFileNameTable()
{
	reset();
}

/* DESTRUCTOR */
NXGraphicsManager::~NXGraphicsManager()
{
}

// .............................................................................

void NXGraphicsManager::reset(void)
{
	properties.clear();
	if(renderingEngine != (NXRenderingEngine*)NULL) {
		delete renderingEngine;
		renderingEngine = (NXRenderingEngine*) NULL;
	}
	renderStyleRendererPluginTable.clear();
	if(defaultRenderer != (NXRendererPlugin*) NULL) {
		delete defaultRenderer;
		defaultRenderer = (NXRendererPlugin*) NULL;
	}
	renderStyleNameTable.clear();
	renderStyleFileNameTable.clear();
}

// .............................................................................

bool NXGraphicsManager::loadPlugins(NXProperties *const props)
{
	reset();
	bool success = true;
	success = loadRenderingEngine(props);
	if(success)
		success = loadRendererPlugins(props);
	if(success) {
		detectDefaultRenderer(props);
		printDiagnosticLogs();
	}
	else
		NX_DEBUG_FAIL;
	return success;
}

// .............................................................................

void NXGraphicsManager::printDiagnosticLogs(void)
{
	/// @todo
}

// .............................................................................

/// Called by findAndLoadPlugin() to load a rendering-engine from an existing file.
/// Returns false if qobject_cast() failed indicating that plugin does not
/// match the expected interface. If successful, then the pointer referenced
/// by pluginStore is updated to point to the loaded instance.
/// This function is called to load both the rendering-engine and renderer-plugins
bool NXGraphicsManager::loadPlugin(NXRenderingEngine **pluginStore,
                                   QFileInfo const& fileInfo)
{
	/// @todo log-messages
	QPluginLoader pluginLoader(fileInfo.absoluteFilePath());
	bool pluginLoaded = pluginLoader.load();
	if(!pluginLoaded)
		return false;
	QObject *pluginObject = pluginLoader.instance();
	if(pluginObject != (QObject*) 0)
		*pluginStore = qobject_cast<NXRenderingEngine*>(pluginObject);
	else 
		*pluginStore = (NXRenderingEngine*) 0;
	
	bool success = ((*pluginStore) != (NXRenderingEngine*)0);
	return success;
}

// .............................................................................

/// Called by findAndLoadPlugin() to load a renderer-plugin from an existing file.
/// Returns false if qobject_cast() failed indicating that plugin does not
/// match the expected interface or if loaded plugin was incompatible with the
/// rendering-engine. If successful, then the pointer referenced by pluginStore
/// is updated to point to the loaded instance. This function is called to load
/// both the rendering-engine and renderer-plugins
bool NXGraphicsManager::loadPlugin(NXRendererPlugin **pluginStore,
                                   QFileInfo const& fileInfo)
{
	QPluginLoader pluginLoader(fileInfo.absoluteFilePath());
	bool pluginLoaded = pluginLoader.load();
	if(!pluginLoaded)
		return false;
	QObject *pluginObject = pluginLoader.instance();
	
	/// @fixme Uncomment and commit after testing builds with NXRenderingEngine
	/// Qt-plugin modifications go through
	string pluginFileName = qPrintable(fileInfo.fileName());
	if(pluginObject != (QObject*) 0) {
		NXLOG_INFO("NXGraphicsManager",
				   "Plugin loaded: " + pluginFileName);
		*pluginStore = renderingEngine->renderer_cast(pluginObject);
		if(*pluginStore != (NXRendererPlugin*)0) {
			NXLOG_INFO("NXGraphicsManager",
					   "Plugin is compatible: " + pluginFileName);
		}
		else {
			NXLOG_SEVERE("NXGraphicsManager",
						 "Plugin is incompatible: " + pluginFileName);
		}
	}
	else  {
		*pluginStore = (NXRendererPlugin*) 0;
		NXLOG_SEVERE("NXGraphicsManager",
					 "Failed to load plugin: " + pluginFileName);
	}
	
	bool success = ((*pluginStore) != (NXRendererPlugin*)0);
	return success;
}

// .............................................................................

/// Locates and loads a plugin given the basename of the file and an initial
/// path to examine. If a load from the initial path is unsuccessful or if the
/// path provided is empty, then it retrieves the plugins-search-path
/// from application-settings and searches it in order for the first file it
/// could successfully find and load. If an engine could be successfully loaded
/// then it returns true and the plugin-pointer referenced by pluginStore is
/// updated to point to the loaded instance. cleanPath then holds the absolute
/// directory specification and absPath holds the full path to the library file.
template<typename PluginType>
	bool NXGraphicsManager::findAndLoadPlugin(string const& baseName,
	                                          string const& path,
	                                          string const& pluginsSearchPath,
	                                          PluginType **pluginStore,
	                                          QDir *cleanPath,
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

// .............................................................................

/// Loads the rendering-engine from application settings
bool NXGraphicsManager::loadRenderingEngine(NXProperties *const props)
{
	/// @fixme What if pluginsSearchPath is empty?
	
	string baseName = props->getProperty("RenderingEngine.plugin");
	string filePath = props->getProperty("RenderingEngine.pluginPath");
	string const pluginsSearchPath = props->getProperty("PluginsSearchPath");
	
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
	
	return renderingEngineLoaded;
}

// .............................................................................

/// Pre-condition: rendering-engine should have loaded successfully
bool NXGraphicsManager::loadRendererPlugins(NXProperties *const props)
{
	string const pluginsSearchPath = props->getProperty("PluginsSearchPath");
	
	int pluginNum = 0; // counter
	bool success = true;
	
	NXLOG_INFO("NXGraphicsManager", "Loading renderer-plugins");
	
	while (true) {
		ostringstream pluginKeyStream;
		pluginKeyStream << "RenderStyle." << pluginNum;
		++pluginNum;
		
		string const pluginKey = pluginKeyStream.str();
		string const pluginCode = props->getProperty(pluginKey + ".code");
		string pluginBaseName = props->getProperty(pluginKey + ".plugin");
		string const pluginPath = props->getProperty(pluginKey + ".pluginPath");
		string pluginName = props->getProperty(pluginKey + ".name");
		if(pluginName.empty())
			pluginName = pluginCode;
		
		NXLOG_DEBUG("NXGraphicsManager", "Parsing " + pluginKey);
		
		if (pluginCode == "def") {
			NXLOG_WARNING("NXGraphicsManager",
			              "Render-style code cannot be 'def' (reserved "
			              "internally for default) - ignoring");
			continue;
		}

		if (pluginName != "")		
			NXLOG_INFO("NXGraphicsManager",
				   	   "Attempting to discover renderer-plugin for rendering-style: "
				   			+ pluginName);
		
		// if code and plugin filename are absent then there are no more plugins
		if (pluginCode == "" && pluginBaseName == "") {
			break;
		
		// else if only one of them is mentioned then error condition
		} else if (pluginCode=="" || pluginBaseName=="") {
			// error condition, both are required, only one is present
			string msg = "Both render-style code and plugin library filename "
				"must be provided for " + pluginKey + " (check app-settings file)";
			NXLOG_SEVERE("NXGraphicsManager", msg);
			// this could be a mistake with just this plugin-spec, continue
			// with next plugin - maybe that one is ok
			success = false;
			continue;
		}
		
		// both code and plugin file have values - try to load
		else {
			NXLOG_DEBUG("NXGraphicsManager", "\tcode = " + pluginCode);
			NXLOG_DEBUG("NXGraphicsManager", "\tplugin = " + pluginBaseName);
			NXLOG_DEBUG("NXGraphicsManager", "\tpluginPath = " + pluginPath);
			NXLOG_DEBUG("NXGraphicsManager", "\tname = " + pluginName);
			
			QDir cleanPath;
			string absPath;
			NXRendererPlugin *rendererPlugin = NULL;
			bool const rendererPluginLoaded =
				findAndLoadPlugin(pluginBaseName, pluginPath, pluginsSearchPath,
				                  &rendererPlugin, &cleanPath, &absPath);
			
			// if successful, record entries in tables
			if (rendererPluginLoaded) {
				// compatibility test
				properties.setProperty("Renderer."+pluginCode+".plugin",
				                       absPath);
				properties.setProperty("Renderer."+pluginCode+".name",
				                       pluginName);
				renderStyleRendererPluginTable[pluginCode] = rendererPlugin;
				renderStyleNameTable[pluginCode] = pluginName;
				renderStyleFileNameTable[pluginCode] = absPath;
				NXLOG_INFO("NXGraphicsManager",
						   "Renderer-plugin loaded: " + pluginName);
			}
			else {
				NXLOG_SEVERE("NXGraphicsManager",
				             "Failed to load renderer-plugin");
				success = false;
			}
		}
	}
	
	NXLOG_INFO("NXGraphicsManager", "Renderer-plugins loaded");
	return success;
}

// .............................................................................

void NXGraphicsManager::detectDefaultRenderer(NXProperties *const props)
{
	if(defaultRenderer != (NXRendererPlugin*) NULL)
		return;
	
	string const defaultRendererCode =
		props->getProperty("RenderStyle.default");
	
	if(!defaultRendererCode.empty()) {
		RenderStyleRendererPluginTable::iterator rendererFinder =
			renderStyleRendererPluginTable.find(defaultRendererCode);
		if(rendererFinder == renderStyleRendererPluginTable.end()) {
			defaultRenderer = renderStyleRendererPluginTable.begin()->second;
			NXLOG_WARNING("NXGraphicsManager",
			              "Invalid default render-style code - "
			              "assigning arbitrarily");
		}
		else {
			defaultRenderer = rendererFinder->second;
		}
	}
	else {
		if(!renderStyleRendererPluginTable.empty()) {
			defaultRenderer = renderStyleRendererPluginTable.begin()->second;
			NXLOG_WARNING("NXGraphicsManager",
			              "No default render-style code - assigning arbitrarily");
		}
		else {
			NXLOG_SEVERE("NXGraphicsManager", "Default renderer not specified -"
			             " and no renderers to assign arbitrarily as default");
		}
	}
}

// .............................................................................

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

// .............................................................................

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

// .............................................................................

string NXGraphicsManager::getRenderStyleName(string const& renderStyleCode)
{
	StringMap::const_iterator renderStyleCodeIter =
		renderStyleNameTable.find(renderStyleCode);
	if(renderStyleCodeIter == renderStyleNameTable.end())
		return string();
	else
		return renderStyleCodeIter->second;
}

// .............................................................................

/// Instantiates a new rendering-engine and sets up its plugins and initializes
/// the whole package. Returns a pointer the new engine which is then owned by
/// the caller.
NXRenderingEngine* NXGraphicsManager::newGraphicsInstance(QWidget *parent)
{
	NXRenderingEngine *newEngine = renderingEngine->newInstance(parent);
	if(newEngine == (NXRenderingEngine*) NULL) {
		NXLOG_SEVERE("NXGraphicsManager",
		             "Failed to create new graphics instance");
		return (NXRenderingEngine*) NULL;
	}
	
	RenderStyleRendererPluginTable::const_iterator renderStyleCodeIter;
	for(renderStyleCodeIter = renderStyleRendererPluginTable.begin();
	    renderStyleCodeIter != renderStyleRendererPluginTable.end();
	    ++renderStyleCodeIter)
	{
		string const& renderStyleCode = renderStyleCodeIter->first;
		assert(renderStyleCode != "def");
		string const& renderStyleName = renderStyleNameTable[renderStyleCode];
		NXRendererPlugin *plugin = renderStyleCodeIter->second;
		NXRendererPlugin *newPlugin = plugin->newInstance(newEngine);
		if(newPlugin == (NXRendererPlugin*)NULL) {
			NXLOG_WARNING("NXGraphicsManager", "Failed to create new instance "
			              "of plugin for " + renderStyleName + " render-style");
		}
		newEngine->setRenderer(renderStyleCode, newPlugin);
		
		if(defaultRenderer == plugin)
			newEngine->setRenderer("def", newPlugin);
	}
	
	bool pluginsInitialized = newEngine->initializePlugins();
	if(!pluginsInitialized) {
		NXLOG_SEVERE("NXGraphicsManager",
		             "Failed to initialize renderer-plugins in new rendering-"
		             "engine context");
	}
	
	return newEngine;
}


} // namespace Nanorex
