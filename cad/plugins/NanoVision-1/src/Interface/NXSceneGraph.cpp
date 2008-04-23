// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <Nanorex/Interface/NXSceneGraph.h>
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <Nanorex/Utility/NXUtility.h>
#include <algorithm>
#include <sstream>
#include <iostream>
#include <cassert>

using namespace std;

namespace Nanorex {

// static data
NXCommandResult NXSGNode::_s_commandResult;
#ifdef NX_DEBUG
int NXSGNode::idSource(0);
#endif

NXSGNode::NXSGNode() throw() :
    ref_count(0), children()
#ifdef NX_DEBUG
	,id(idSource++), name()
#endif
{
#ifdef NX_DEBUG
// 	cerr << "creating " << getName()
// 		<< " [ref = " << getRefCount() << ']' << endl;
#endif
}
	
NXSGNode::~NXSGNode()
{
	assert(ref_count == 0);
#ifdef NX_DEBUG
	cerr << "deleting " << getName()
		<< " [ref = " << getRefCount() << ']' << endl;
#endif
	removeAllChildren(); 
}


void NXSGNode::SetError(int errCode, char const *const errMsg)
{
    _s_commandResult.setResult(errCode);
    vector<QString> message;
    message.push_back(QObject::tr(errMsg));
    _s_commandResult.setParamVector(message);
}


void NXSGNode::ClearResult(void)
{
	_s_commandResult.setResult(NX_CMD_SUCCESS);
	_s_commandResult.setParamVector(vector<QString>());
}


bool NXSGNode::addChild(NXSGNode *const child)
{
	ClearResult();
    if(child == NULL) return false; // prevent seg-faults early
	assert(find(children.begin(), children.end(), child) == children.end());
	try { children.push_back(child); }
    catch(...) {
        SetError((int) NX_INTERNAL_ERROR,
                 "Failed to add scenegraph child");
        return false;
    }
	child->incrementRefCount();
	return true;
}


/// Precondition: childPtr is a valid child of this node
/// Private, so that calling methods know that this is the case
/// Does not remove child from the list of children
inline void NXSGNode::removeChildWithoutCheck(NXSGNode *childPtr)
{
	assert(childPtr->getRefCount() >= 1);
	int childNewRefCount = childPtr->decrementRefCount();
	if(childNewRefCount == 0) {
        delete childPtr; // will call deleteRecursive
    }
}



bool NXSGNode::removeChild(NXSGNode *const child)
{
	ClearResult();
	ChildrenList::iterator childLoc = std::find(children.begin(),
	                                            children.end(),
	                                            child);
	if(childLoc != children.end()) {
		removeChildWithoutCheck(*childLoc);
		children.erase(childLoc);
		return true;
	}
	else {
		SetError((int) NX_INTERNAL_ERROR, "Cannot remove non-child node");
		return false;
	}
}


void NXSGNode::removeAllChildren(void)
{
	ClearResult();
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
	    NXSGNode *childNode = *childIter;
        ok = childNode->applyRecursive();
    }
    return ok;
}


#ifdef NX_DEBUG
void NXSGNode::reset(void)
{
	ChildrenList::iterator childIter;
	for(childIter=children.begin(); childIter!=children.end(); ++childIter)
		(*childIter)->decrementRefCount();
	children.clear();
	ref_count = 0;
}

string const NXSGNode::getName() const
{
// 	ostringstream strm;
// 	strm << "Node_" << name << "-" << id;
//     return strm.str();
	
	return "Node_" + name + "_" + NXUtility::itos(id);
}

void NXSGNode::writeDotGraph(ostream& o) const
{
	ChildrenList::const_iterator childIter;
    for(childIter = children.begin(); childIter != children.end(); ++childIter) {
        (*childIter)->writeDotGraph(o);
    }
    o << '\n' << getName() << endl;
    
    for(childIter = children.begin(); childIter != children.end(); ++childIter) {
        o << getName() << " -> " << (*childIter)->getName() << endl;
    }
}
#endif

} // Nanorex
