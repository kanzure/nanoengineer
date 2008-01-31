// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_H
#define NX_SCENEGRAPH_H

#include <list>

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
    
    NXSGNode() : ref_count(0), children() {}
    
    virtual ~NXSGNode() { deleteRecursive(); }

    int incrementRefCount(void) { ++ref_count; return ref_count; }
    
    int decrementRefCount(void)
    { if(ref_count > 0) --ref_count; return ref_count; }
    
    int getRefCount(void) const { return ref_count; }
    
    void addChild(NXSGNode *const child)
    { child->incrementRefCount(); children.push_back(child); }
    
    /// Return true if child was found and was deleted
    bool removeChild(NXSGNode *const child);
    
    ChildrenList const& getChildren(void) const { return children; }
    
    ChildrenList::size_type getNumChildren(void) const
    { return children.size(); }
    
    virtual bool apply(void) const { return true; };
    
    /// Apply the effect of this node and its children
    /// Return true if successful. Abort at the first failure
    virtual bool applyRecursive(void) const;
    
    /// Recursively delete all children. Deleting this node is up to the caller
    virtual void deleteRecursive(void);
    
    bool isLeaf(void) const { return (children.size()==0); }
    
#ifdef NX_DEBUG
    void reset(void) { ref_count=0; children.clear(); }
#endif
        
protected:
    int ref_count;
    ChildrenList children;
};


} // Nanorex

#endif // NX_SCENEGRAPH_H
