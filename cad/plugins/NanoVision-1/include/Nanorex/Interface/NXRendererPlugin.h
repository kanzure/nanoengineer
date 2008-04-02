// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERERPLUGIN_H
#define NX_RENDERERPLUGIN_H

#include <Nanorex/Utility/NXCommandResult.h>
#include <Nanorex/Interface/NXRenderingEngine.h>
#include <string>

namespace Nanorex {

/* CLASS: NXRendererPlugin */
/**
 * Base class for all rendering plugins
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXRendererPlugin {
public:
	NXRendererPlugin(NXRenderingEngine *parent = NULL);
	virtual ~NXRendererPlugin();

    /// Initialize the plugin, for example when its rendering context is made 
	/// ready by the parent rendering-engine. Derived classes must implement and
	/// must set the 'initialized' flag to true
    virtual NXCommandResult const *const initialize() = 0;
    
	/// Returns true of the plugin is initialized
	bool isInitialized(void) const { return initialized; }
	
    /// Cleanup the plugin. Must be called before deleting the object.
    /// Implements a cleanup mechanism in parallel to the destructor.
    /// This is necessary because the ability to cleanup may depend on external
    /// circumstances, like the availability of a certain resource like a
    /// rendering/drawing context. Must set the 'initialize' flag to false.
    virtual NXCommandResult const *const cleanup() = 0;
	
	/// Fully-implemented derived classes have enough information to create a
	/// functioning plugin and must return an instance created using the 'new'
	/// operator
	virtual NXRendererPlugin* newInstance(NXRenderingEngine *parent) const = 0;
	
	void setParent(NXRenderingEngine *parent) { parentEngine = parent; }
	
	/// Result of previous public API call
	Nanorex::NXCommandResult const& getCommandResult(void) const
	{ return commandResult; }
	

protected:
	NXRenderingEngine *parentEngine;
	bool initialized;
	
	Nanorex::NXCommandResult commandResult;
	static void ClearResult(Nanorex::NXCommandResult& cmdResult);
	static void SetError(Nanorex::NXCommandResult& cmdResult,
	                     std::string const& errMsg);
	static void SetWarning(Nanorex::NXCommandResult& cmResult,
	                       std::string const& warnMsg);
	
};

//..............................................................................

/* static */
inline void NXRendererPlugin::ClearResult(NXCommandResult& commandResult)
{
	commandResult.setResult(NX_CMD_SUCCESS);
	commandResult.setParamVector(vector<QString>());
}

//..............................................................................

/* static */
inline void NXRendererPlugin::SetError(NXCommandResult& commandResult,
                                       std::string const& errMsg)
{
	commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
	vector<QString> message;
	message.push_back(QObject::tr(errMsg.c_str()));
	commandResult.setParamVector(message);
}

//..............................................................................

/* static */
inline void NXRendererPlugin::SetWarning(NXCommandResult& commandResult,
                                         std::string const& warnMsg)
{
	commandResult.setResult(NX_PLUGIN_REPORTS_WARNING);
	vector<QString> message;
	message.push_back(QObject::tr(warnMsg.c_str()));
	commandResult.setParamVector(message);
}

//..............................................................................

inline
NXRendererPlugin::NXRendererPlugin(NXRenderingEngine *parent)
	: parentEngine(parent), initialized(false)
{
}

//..............................................................................

inline NXRendererPlugin::~NXRendererPlugin()
{
}


} // Nanorex

Q_DECLARE_INTERFACE(Nanorex::NXRendererPlugin,
                    "com.Nanorex.Interface.NXRendererPlugin/0.1.0")

#endif // NX_RENDERERPLUGIN_H
