// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXBallAndStickOpenGLRenderer.h"
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <iostream>
using namespace std;

namespace Nanorex {

// static data
double const NXBallAndStickOpenGLRenderer::BOND_WIDTH(0.25);

NXSGOpenGLNode* NXBallAndStickOpenGLRenderer::_s_canonicalBondNode[MAX_BONDS] =
{
    NULL, NULL, NULL, NULL, NULL, NULL
};


/* static */
bool NXBallAndStickOpenGLRenderer::InitializeCanonicalBondNodes(void)
{
    InitializeCanonicalSingleBondNode();
    InitializeCanonicalDoubleBondNode();
    InitializeCanonicalTripleBondNode();
    InitializeCanonicalAromaticBondNode();
    InitializeCanonicalCarbomericBondNode();
    InitializeCanonicalGraphiticBondNode();
    
    bool ok = true;
    for(int iBond=0; iBond<MAX_BONDS; ++iBond)
        ok = ok && (_s_canonicalBondNode[iBond] != NULL);
    
    if(!ok) {
        for(int iBond=0; iBond<MAX_BONDS; ++iBond) {
            if(_s_canonicalBondNode[iBond] != NULL)
                delete _s_canonicalBondNode[iBond];
            _s_canonicalBondNode[iBond] = NULL;
        }

        SetError(_s_commandResult,
                 "Canonical bond scenegraph-nodes creation failed");
        return false;
    }
    
    return true;
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalSingleBondNode(void)
{
    if(_s_canonicalBondNode[0] == NULL) {
        try {
            _s_canonicalBondNode[0] =
                new NXSGOpenGLScale(BOND_WIDTH, BOND_WIDTH, 1.0);
        }
        catch(...) {
            _s_canonicalBondNode[0] = NULL;
            return;
        }
        
        bool ok = _s_canonicalBondNode[0]->addChild(_s_canonicalCylinderNode);
        if(!ok) {
            delete _s_canonicalBondNode[0];
            _s_canonicalBondNode[0] = NULL;
        }
    }
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalDoubleBondNode(void)
{
    if(_s_canonicalBondNode[1] == NULL &&
       _s_canonicalBondNode[0] != NULL)
    {
        bool doubleBondOK = true;
        NXSGOpenGLNode *translateNode1 = NULL;
        NXSGOpenGLNode *translateNode2 = NULL;
        try {
            translateNode1 = new NXSGOpenGLTranslate(BOND_WIDTH, 0.0, 0.0);
            translateNode2 = new NXSGOpenGLTranslate(-BOND_WIDTH, 0.0, 0.0);
            _s_canonicalBondNode[1] = new NXSGOpenGLNode;
        }
        catch(...) {
            doubleBondOK = false;
        }
        if(doubleBondOK) {
            bool ok1 = translateNode1->addChild(_s_canonicalBondNode[0]);
            bool ok2 = translateNode2->addChild(_s_canonicalBondNode[0]);
            if(ok1 && ok2) {
                bool ok3 = _s_canonicalBondNode[1]->addChild(translateNode1);
                bool ok4 = _s_canonicalBondNode[1]->addChild(translateNode2);
                doubleBondOK = ok3 && ok4;
            }
            else {
                doubleBondOK = false;
            }
        }
        
        if(!doubleBondOK) {
            if(translateNode1 != NULL)
                delete translateNode1;
            if(translateNode2 != NULL)
                delete translateNode2;
            if(_s_canonicalBondNode[1] != NULL) {
                delete _s_canonicalBondNode[1];
                _s_canonicalBondNode[1] = NULL;
            }
        }
    }
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalTripleBondNode(void)
{
    if(_s_canonicalBondNode[2] == NULL &&
       _s_canonicalBondNode[1] != NULL &&
       _s_canonicalBondNode[0] != NULL)
    {
        bool tripleBondOK = true;
        NXSGOpenGLNode *translateNode1 = NULL;
        NXSGOpenGLNode *translateNode2 = NULL;
        try {
            translateNode1 = new NXSGOpenGLTranslate(1.5*BOND_WIDTH, 0.0, 0.0);
            translateNode2 = new NXSGOpenGLTranslate(1.5*(-BOND_WIDTH), 0.0, 0.0);
        }
        catch(...) {
            tripleBondOK = false;
        }
        if(tripleBondOK) {
            bool ok1 = translateNode1->addChild(_s_canonicalBondNode[0]);
            bool ok2 = translateNode2->addChild(_s_canonicalBondNode[0]);
            if(ok1 && ok2) {
                bool ok3 = _s_canonicalBondNode[2]->addChild(translateNode1);
                bool ok4 = _s_canonicalBondNode[2]->addChild(translateNode2);
                bool ok5 =
                    _s_canonicalBondNode[2]->addChild(_s_canonicalBondNode[0]);
                tripleBondOK = ok3 && ok4 && ok5;
            }
            else {
                tripleBondOK = false;
            }
        }
        
        if(!tripleBondOK) {
            if(translateNode1 != NULL)
                delete translateNode1;
            if(translateNode2 != NULL)
                delete translateNode2;
        }
    }
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalAromaticBondNode(void)
{
    /// @todo
    _s_canonicalBondNode[3] = _s_canonicalBondNode[0];
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalCarbomericBondNode(void)
{
    /// @todo
    _s_canonicalBondNode[4] = _s_canonicalBondNode[0];
}


/* static */
void NXBallAndStickOpenGLRenderer::InitializeCanonicalGraphiticBondNode(void)
{
    /// @todo
    _s_canonicalBondNode[5] = _s_canonicalBondNode[0];
}


/// Initialize the plugin. If not successful, as indicated by the return
/// command-result, then the instance is left partially initialized.
/// The user is then expected to destroy the instance to ensure proper cleanup
NXCommandResult* NXBallAndStickOpenGLRenderer::initialize(void)
{
    commandResult.setResult((int) NX_CMD_SUCCESS);
    
    bool initialized = NXOpenGLRendererPlugin::initialize();
    if(initialized) {
        bool initialized = InitializeCanonicalBondNodes();
        if(initialized) {
            for(int iBond=0; iBond<MAX_BONDS; ++iBond) {
                bool const addedChild =
                    canonicalBondNodeGuard[iBond].addChild(_s_canonicalBondNode[1]);
                initialized = initialized && addedChild;
            }
        }
    }

    // The failure location, if any, should have recorded the error
    return &commandResult;
}


NXCommandResult* NXBallAndStickOpenGLRenderer::cleanup(void)
{
    NXCommandResult *parentCleanupResult = NXOpenGLRendererPlugin::cleanup();
    return parentCleanupResult;
}


/// It is assumed that the plugin was initialized successfully and that the
/// developer has trapped any errors
NXSGOpenGLNode*
    NXBallAndStickOpenGLRenderer::renderAtom(NXAtomRenderData const& info)
{
    std::vector<void const*> const& paramVec = info.getSupplementalData();
    NXOpenGLMaterial const& defaultMaterial =
        *static_cast<NXOpenGLMaterial const*>(paramVec[0]);
    NXSGOpenGLMaterial *atomNode = NULL;
    try {
        atomNode = new NXSGOpenGLMaterial(defaultMaterial);
    }
    catch (...) { 
        SetError(commandResult, "Could not create node for rendering atom");
        return NULL;
    } // fail silently
    
    if(!atomNode->addChild(_s_canonicalSphereNode)) {
        SetError(commandResult,
                 "Created scenegraph node for atom but could not include it");
        delete atomNode;
        return NULL;
    }
    
    return atomNode;
}


NXSGOpenGLNode* NXBallAndStickOpenGLRenderer::renderBond(NXBondRenderData const& info)
{
    std::vector<void const*> const& paramVec = info.getSupplementalData();
    NXOpenGLMaterial const& defaultMaterial =
        *static_cast<NXOpenGLMaterial const*>(paramVec[0]);
    NXSGOpenGLMaterial *bondNode = NULL;
    try {
        bondNode = new NXSGOpenGLMaterial(defaultMaterial);
    }
    catch (...) {
        SetError(commandResult,
                 "Could not create bond scenegraph node");
        return NULL;
    } // fail silently
    
    NXSGOpenGLScale *bondScale = NULL;
    try {
        bondScale = new NXSGOpenGLScale(1.0,1.0,info.getLength());
    }
    catch(...) {
        SetError(commandResult,
                 "Could not create scaling scenegraph node for bond-length");
        delete bondNode;
        return NULL;
    }
    
    if(!bondNode->addChild(bondScale)) {
        SetError(commandResult,
                 "Created scenegraph nodes for bond but could not include them");
        delete bondNode;
        return NULL;
    }
    
    // note x-y displacements are not affected by z-scaling for length
    
    // single bond
    if(!bondScale->addChild(_s_canonicalBondNode[info.getOrder()])) {
        SetError(commandResult,
                 "Error including canonical bond node in bond scenegraph");
        delete bondNode;
        return NULL;
    }
    return bondNode;
}

} // Nanorex
