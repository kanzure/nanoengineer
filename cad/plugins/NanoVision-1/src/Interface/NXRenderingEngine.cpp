// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <Nanorex/Interface/NXRenderingEngine.h>
#include <Nanorex/Interface/NXRendererPlugin.h>
#include <Nanorex/Interface/NXGraphicsManager.h>
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <string>

using namespace std;

namespace Nanorex {


// .............................................................................

/*static*/
void NXRenderingEngine::SetResult(NXCommandResult& commandResult,
                                  int errCode,
                                  string const& errMsg)
{
	commandResult.setResult(errCode);
	vector<QString> message;
	message.push_back(QObject::tr(errMsg.c_str()));
	commandResult.setParamVector(message);
}

// .............................................................................

/* static */
void NXRenderingEngine::
	ClearResult(NXCommandResult& commandResult)
{
	commandResult.setResult((int) NX_CMD_SUCCESS);
	vector<QString> message;
	commandResult.setParamVector(message);
}

// .............................................................................

/* CONSTRUCTOR */
NXRenderingEngine::NXRenderingEngine()
	: // rendererSet(),
	renderStyleMap(),
	graphicsManager(NULL),
	moleculeSets(),
	frames(),
	currentFrameIndex(-1),
	pluginsInitialized(false),
	commandResult()
{
	ClearResult(commandResult);
}

// .............................................................................

/* DESTRUCTOR */
NXRenderingEngine::~NXRenderingEngine()
{
	// release plugin instances initialized in this context
	map<string, NXRendererPlugin*>::iterator pluginIter;
	for(pluginIter = renderStyleMap.begin();
	    pluginIter != renderStyleMap.end();
	    ++pluginIter)
	{
		string const renderStyleCode = pluginIter->first;
		if(renderStyleCode != "def") {
			NXRendererPlugin *plugin = pluginIter->second;
			delete plugin;
		}
	}
	
	// release frame-memory allocated in this context
	std::vector<NXSGNode*>::iterator frameIter;
	for(frameIter = frames.begin(); frameIter != frames.end(); ++frameIter) {
		NXSGNode *frame = *frameIter;
		delete frame;
	}
}

// .............................................................................

/// Returns NULL if index is out of bounds
NXMoleculeSet *const NXRenderingEngine::getFrame(int idx)
{
	if(idx < 0 || idx >= int(moleculeSets.size()))
		return (NXMoleculeSet*) NULL;
	else
		return moleculeSets[idx];
}

// .............................................................................

NXCommandResult const *const
	NXRenderingEngine::addFrame(NXMoleculeSet *const molSetPtr)
{
	ClearResult(commandResult);
	NXSGNode *newFrame = createSceneGraph(molSetPtr);
	if(newFrame != (NXSGNode*) NULL) {
		moleculeSets.push_back(molSetPtr);
		frames.push_back(newFrame);
	}
	return &commandResult;
}

// .............................................................................

void NXRenderingEngine::setCurrentFrame(int frameIdx)
{
	if(frameIdx < int(frames.size()))
		currentFrameIndex = frameIdx;
}

// .............................................................................

#if 0
bool NXRenderingEngine::importRendererPluginsFromGraphicsManager(void)
{
	ClearResult(commandResult);
	
	if(graphicsManager == NULL) {
		string const msg = "Graphics-manager not set";
		SetResult(commandResult, NX_INITIALIZATION_ERROR, msg);
		NXLOG_SEVERE("NXRenderingEngine (import plugins from graphics manager)",
		             msg);
		return false;
	}
	
	bool success = true;
	
	// rendererSet.clear();
	vector<string> renderStyleCodes = graphicsManager->getRenderStyles();
	vector<string>::const_iterator renderStyleCodeIter;
	for(renderStyleCodeIter = renderStyleCodes.begin();
	    renderStyleCodeIter != renderStyleCodes.end();
	    ++renderStyleCodeIter)
	{
		NXRendererPlugin *const plugin =
			graphicsManager->getRenderer(*renderStyleCodeIter);
		NXRendererPlugin *const renderer = plugin->newInstance(this);
		if(renderer == NULL) {
			string const& renderStyleName =
				graphicsManager->getRenderStyleName(*renderStyleCodeIter);
			string const msg = "Failed to create new instance of renderer-plugin"
				" for style '" + renderStyleName + "' from graphics-manager";
			NXLOG_SEVERE("NXRenderingEngine", msg);
			SetResult(commandResult, NX_PLUGIN_CAUSED_ERROR, msg);
			success = false;
		}
		else {
			renderStyleMap[*renderStyleCodeIter] = renderer;
			// rendererSet.push_back(renderer);
		}
	}
	
	return success;
}
#endif

} // Nanorex
