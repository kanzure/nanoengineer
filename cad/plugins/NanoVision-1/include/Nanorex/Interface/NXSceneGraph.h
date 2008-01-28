// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_H
#define NX_SCENEGRAPH_H

#include <vector>

// SceneGraph abstraction to bridge platforms

// #include "Nanorex/Utility/NXCommandResult.h"

namespace Nanorex {

/* CLASS: NXSGNode */
/**
 * Base class for all scenegraph nodes
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGNode {
public:
    NXSGNode() : ref_count(0), children() {}
    virtual ~NXSGNode() {}

    int incrementRefCount(void) { ++ref_count; return ref_count; }
    int decrementRefCount(void) { if(ref_count > 0) --ref_count; return ref_count; }
    int getRefCount(void) const { return ref_count; }
    
    void addChild(NXSGNode *const child) { child->incrementRefCount(); children.push_back(child); }
    
    std::vector<NXSGNode*> const& getChildren(void) const { return children; }
    std::vector<NXSGNode*>::size_type getNumChildren(void) const { return children.size(); }
    
    virtual bool apply(void) const { return true; };
    
    /// Apply the effect of this node and its children
    /// Return true if successful. Abort at the first failure
    virtual bool applyRecursive(void) const {
        bool ok = apply();
        std::vector<NXSGNode*>::const_iterator child_iter;
        for(child_iter = children.begin();
            child_iter != children.end() && ok;
            ++child_iter)
        {
            ok = (*child_iter)->applyRecursive();
        }
        return ok;
    }
    
    /// Recursively delete all children. Deleting this node is up to the caller
    void deleteRecursive(void) {
        for(std::vector<NXSGNode*>::iterator child_iter = children.begin();
            child_iter != children.end();
            ++child_iter)
        {
            if((*child_iter)->decrementRefCount() == 0) delete *child_iter;
        }
        children.clear();
    }
    
    bool isLeaf(void) const { return (children.size()==0); }
        
protected:
    int ref_count;
    std::vector<NXSGNode*> children;
};


} // Nanorex

#endif // NX_SCENEGRAPH_H
