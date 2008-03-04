// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <Nanorex/Interface/NXSceneGraph.h>
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <algorithm>

using namespace std;

namespace Nanorex {

// static data
NXCommandResult NXSGNode::_s_commandResult;

NXSGNode::NXSGNode() throw() : ref_count(0), children() {}
	
NXSGNode::~NXSGNode() { removeAllChildren(); }


void NXSGNode::SetError(int errCode, char const *const errMsg)
{
    _s_commandResult.setResult(errCode);
    vector<QString> message;
    message.push_back(QObject::tr(errMsg));
    _s_commandResult.setParamVector(message);
}



bool NXSGNode::initializeContext(void)
{
    _s_commandResult.setResult((int) NX_CMD_SUCCESS);
    return true;
}


bool NXSGNode::addChild(NXSGNode *const child)
{
    if(child == NULL) return false; // prevent seg-faults early
    child->incrementRefCount();
    try { children.push_back(child); }
    catch(...) {
        SetError((int) NX_INTERNAL_ERROR,
                 "Failed to add scenegraph child");
        return false;
    }
    return true;
}


/// Precondition: childPtr is a valid child of this node
/// Private, so that calling methods know that this is the case
/// Does not remove child from the list of children
inline void NXSGNode::removeChildWithoutCheck(NXSGNode *childPtr)
{
    int childNewRefCount = childPtr->decrementRefCount();
    if(childNewRefCount == 0) {
        delete childPtr; // will call deleteRecursive
    }
}



bool NXSGNode::removeChild(NXSGNode *const child)
{
    ChildrenList::iterator childLoc = std::find(children.begin(),
                                                children.end(),
                                                child);
    if(childLoc != children.end()) {
        removeChildWithoutCheck(*childLoc);
        children.erase(childLoc);
        return true;
    }
    else return false;
}


void NXSGNode::removeAllChildren(void)
{
    {
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            childIter != children.end();
            ++childIter)
        {
            NXSGNode *const childPtr = *childIter;
            removeChildWithoutCheck(childPtr);
        }
        children.clear();
    }
}

bool NXSGNode::applyRecursive(void) const
{
    bool ok = this->apply();
    // ok is false iff subclass encountered error in which case it should have
    // set the commandResult appropriately.
    ChildrenList::const_iterator childIter;
    for(childIter = children.begin();
        childIter != children.end() && ok;
        ++childIter)
    {
        ok = (*childIter)->applyRecursive();
    }
    return ok;
}


} // Nanorex
