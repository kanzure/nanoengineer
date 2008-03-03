// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <algorithm>
#include "Nanorex/Interface/NXSceneGraph.h"

namespace Nanorex {

NXSGNode::NXSGNode() throw() : ref_count(0), children() {}
	
NXSGNode::~NXSGNode() { deleteRecursive(); }

bool NXSGNode::addChild(NXSGNode *const child)
{
    if(child == NULL) return false; // prevent seg-faults early
    child->incrementRefCount();
    try { children.push_back(child); }
    catch(...) { return false; }
    return true;
}


bool NXSGNode::removeChild(NXSGNode *const child)
{
    ChildrenList::iterator childLoc = std::find(children.begin(),
                                                children.end(),
                                                child);
    if(childLoc != children.end()) {
        (*childLoc)->decrementRefCount();
        children.erase(childLoc);
        return true;
    }
    else return false;
}

bool NXSGNode::applyRecursive(void) const
{
    bool ok = this->apply();
    ChildrenList::const_iterator childIter;
    for(childIter = children.begin();
        childIter != children.end() && ok;
        ++childIter)
    {
        ok = (*childIter)->applyRecursive();
    }
    return ok;
}


void NXSGNode::deleteRecursive(void)
{
    {
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            childIter != children.end();
            ++childIter)
        {
            NXSGNode *const childPtr = *childIter;
            if(childPtr->decrementRefCount() == 0) {
                childPtr->deleteRecursive();
                delete childPtr;
            }
        }
        children.clear();
    }
}

} // Nanorex
