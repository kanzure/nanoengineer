// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_H
#define NX_SCENEGRAPH_H

#include <list>
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
public:
    typedef std::list<NXSGNode*> ChildrenList;
    
    NXSGNode() throw();
    virtual ~NXSGNode();

    /// Initialize the scenegraph context, if any
    virtual bool initializeContext(void);
    
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
    void reset(void) { removeAllChildren(); ref_count=0; }
    
    /// @todo write scenegraph structure in GraphViz format
    // virtual void writeDotGraph(std::ostream&) const;
#endif
        
    /// Last error in the context
    static NXCommandResult* GetCommandResult(void) { return &_s_commandResult; }
    
private:
    int ref_count;
    int incrementRefCount(void) throw() { ++ref_count; return ref_count; }
    int decrementRefCount(void) throw()
    { if(ref_count > 0) --ref_count; return ref_count; }
    
    void removeChildWithoutCheck(NXSGNode *const child);
    
protected:
    
    ChildrenList children;
    
    /// Most recent error - to be set by failing node
    /// All calling nodes propagate boolean result back up to root
    static NXCommandResult _s_commandResult;
    
    static void SetError(int errCode, char const *const errMsg);
    
};


} // Nanorex

#endif // NX_SCENEGRAPH_H
