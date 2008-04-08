// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_H
#define NX_SCENEGRAPH_H

#include <list>
#include <string>
#include <iostream>
#include <cassert>
#include <Nanorex/Utility/NXCommandResult.h>

// SceneGraph abstraction to bridge platforms

namespace Nanorex {

/* CLASS: NXSGNode */
/**
 * Base class for all scenegraph nodes
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGNode {
	
	friend class NXSceneGraphTest;
	
public:
    typedef std::list<NXSGNode*> ChildrenList;
    
    NXSGNode() throw();
    virtual ~NXSGNode();

    /// Initialize the scenegraph context, if any
	virtual bool initializeContext(void) { return true; }
    
    /// Cleanup the scenegraph context, if any
    virtual bool cleanupContext(void) { return true; }

    int getRefCount(void) const throw() { return ref_count; }
    
    /// Return true if child could be added successfully
    virtual bool addChild(NXSGNode *const child);
    
    /// Return true if child was found and was removed from children-list.
    /// In the process, if child's reference count becomes zero, it is deleted
    virtual bool removeChild(NXSGNode *const child);
    
    /// Give up parenthood of all existing children and recursively delete if
    /// their reference count becomes zero
    virtual void removeAllChildren(void);
    
    ChildrenList const& getChildren(void) const throw() { return children; }
    
    ChildrenList::size_type getNumChildren(void) const throw()
    { return children.size(); }
    
    virtual bool apply(void) const { return true; }
    
    /// Apply the effect of this node and its children
    /// Return true if successful. Abort at the first failure
    virtual bool applyRecursive(void) const;
    
    bool isLeaf(void) const throw() { return (children.size()==0); }
    
#ifdef NX_DEBUG
	/// Non-destructively remove all children and set ref-count to zero
	void reset(void);
    
    /// Get a name for the node
    virtual std::string const getName(void) const;
	void setName(std::string const& _name) { name = _name; }
	
    /// write scenegraph structure in GraphViz format
    void writeDotGraph(std::ostream& o) const;
	
	static void ResetIdSource(void) { idSource = 0; }
#endif
        
    /// Last error in the context
    static NXCommandResult* GetCommandResult(void) { return &_s_commandResult; }
    
private:
    int ref_count;
    int incrementRefCount(void) throw() { ++ref_count; return ref_count; }
    int decrementRefCount(void) throw()
	{ --ref_count; return ref_count; }
    
    void removeChildWithoutCheck(NXSGNode *const child);
    
protected:
    ChildrenList children;
    
#ifdef NX_DEBUG
	int id;
	static int idSource;
	std::string name;
#endif
	
    /// Most recent error - to be set by failing node
    /// All calling nodes propagate boolean result back up to root
    static NXCommandResult _s_commandResult;
    
    static void SetError(int errCode, char const *const errMsg);
	static void ClearResult(void);
    
};


} // Nanorex

#endif // NX_SCENEGRAPH_H
