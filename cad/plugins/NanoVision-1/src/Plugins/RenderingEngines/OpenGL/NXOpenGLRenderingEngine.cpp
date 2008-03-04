// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <fstream>
#include <sstream>
#include <cassert>
#include <set>
#include <cmath>

#include <Nanorex/Interface/NXEntityManager.h>
#include "NXOpenGLRenderingEngine.h"
#include "GLT/glt_bbox.h"

#include <openbabel/mol.h>


using namespace std;
using namespace OpenBabel;


namespace Nanorex {

/*static*/
void NXOpenGLRenderingEngine::SetResult(NXCommandResult commandResult,
                                        int errCode,
                                        string const& errMsg)
{
    commandResult.setResult(errCode);
    vector<QString> message;
    message.push_back(tr(errMsg.c_str()));
    commandResult.setParamVector(message);
}


NXOpenGLRenderingEngine::NXOpenGLRenderingEngine(QWidget *parent)
    : QGLWidget(parent),
    NXRenderingEngine(),
    camera(this),
    rootMoleculeSet(NULL),
    mol(NULL),
    isSingleMolecule(false),
    rootSceneGraphNode(NULL),
    renderer(NULL),
    rendererInitialized(false),
    lights(),
    lightModel(),
    // isOrthographicProjection(false),
    // orthographicProjection(),
    // perspectiveProjection(),
    // viewport(),
    elementColorMap(),
    defaultAtomMaterial(),
    defaultBondMaterial(),
    commandResult()
{
    bool ok = true;
    
    ok = initializeElementColorMap();
    /// @todo trap error
    initializeDefaultMaterials();
}


NXOpenGLRenderingEngine::~NXOpenGLRenderingEngine()
{
    cleanupPlugins();
}


void NXOpenGLRenderingEngine::setRootMoleculeSet(NXMoleculeSet *const moleculeSet)
{
    isSingleMolecule = false;
    deleteSceneGraph();
    rootMoleculeSet = moleculeSet;
    rootSceneGraphNode = createSceneGraph(rootMoleculeSet);
    resetView();
}


void NXOpenGLRenderingEngine::setMolecule(OBMol *molPtr)
{
    isSingleMolecule = true;
    deleteSceneGraph();
    mol = molPtr;
    rootSceneGraphNode = createSceneGraph(mol);
    resetView();
}

bool NXOpenGLRenderingEngine::initializeElementColorMap(void)
{
    elementColorMap.clear();
    elementColorMap[0] = NXRGBColor(204,0,0,255);
    elementColorMap[1] = NXRGBColor(199,199,199,255);
    elementColorMap[2] = NXRGBColor(107,115,140,255);
    elementColorMap[3] = NXRGBColor(0,128,128,255);
    elementColorMap[4] = NXRGBColor(250,171,255,255);
    elementColorMap[5] = NXRGBColor(51,51,150,255);
    elementColorMap[6] = NXRGBColor(99,99,99,255);
    elementColorMap[7] = NXRGBColor(31,31,99,255);
    elementColorMap[8] = NXRGBColor(128,0,0,255);
    elementColorMap[9] = NXRGBColor(0,99,51,255);
    elementColorMap[10] = NXRGBColor(107,115,140,255);
    elementColorMap[11] = NXRGBColor(0,102,102,255);
    elementColorMap[12] = NXRGBColor(224,153,230,255);
    elementColorMap[13] = NXRGBColor(128,128,255,255);
    elementColorMap[14] = NXRGBColor(41,41,41,255);
    elementColorMap[15] = NXRGBColor(84,20,128,255);
    elementColorMap[16] = NXRGBColor(219,150,0,255);
    elementColorMap[17] = NXRGBColor(74,99,0,255);
    elementColorMap[18] = NXRGBColor(107,115,140,255);
    elementColorMap[19] = NXRGBColor(0,77,77,255);
    elementColorMap[20] = NXRGBColor(201,140,204,255);
    elementColorMap[21] = NXRGBColor(106,106,130,255);
    elementColorMap[22] = NXRGBColor(106,106,130,255);
    elementColorMap[23] = NXRGBColor(106,106,130,255);
    elementColorMap[24] = NXRGBColor(106,106,130,255);
    elementColorMap[25] = NXRGBColor(106,106,130,255);
    elementColorMap[26] = NXRGBColor(106,106,130,255);
    elementColorMap[27] = NXRGBColor(106,106,130,255);
    elementColorMap[28] = NXRGBColor(106,106,130,255);
    elementColorMap[29] = NXRGBColor(106,106,130,255);
    elementColorMap[30] = NXRGBColor(106,106,130,255);
    elementColorMap[31] = NXRGBColor(153,153,204,255);
    elementColorMap[32] = NXRGBColor(102,115,26,255);
    elementColorMap[33] = NXRGBColor(153,66,179,255);
    elementColorMap[34] = NXRGBColor(199,79,0,255);
    elementColorMap[35] = NXRGBColor(0,102,77,255);
    elementColorMap[36] = NXRGBColor(107,115,140,255);
    elementColorMap[51] = NXRGBColor(153,66,179,255);
    elementColorMap[52] = NXRGBColor(230,89,0,255);
    elementColorMap[53] = NXRGBColor(0,128,0,255);
    elementColorMap[54] = NXRGBColor(102,115,140,255);
    elementColorMap[200] = NXRGBColor(102,102,204,255);
    elementColorMap[201] = NXRGBColor(102,204,102,255);
    elementColorMap[202] = NXRGBColor(102,26,128,255);
    elementColorMap[203] = NXRGBColor(102,204,204,255);
    elementColorMap[204] = NXRGBColor(102,102,204,255);
    elementColorMap[205] = NXRGBColor(102,26,128,255);
    elementColorMap[206] = NXRGBColor(102,204,102,255);
    elementColorMap[207] = NXRGBColor(77,179,77,255);
    return true;
        
#if 0 // read from file - sensitive to location
    /// @todo Remove filename hardcoding
    ifstream elemColorMapFile("default-element-colors.txt", ios::in);
    if(!elemColorMapFile)
        return false;
    while(elemColorMapFile.good()) {
        int const LINEBUF_SIZE = 201;
        char linebuf[LINEBUF_SIZE];
        elemColorMapFile.getline(linebuf, LINEBUF_SIZE);
        assert((int)elemColorMapFile.gcount() < LINEBUF_SIZE);
        
        istringstream line(linebuf);
        // ignore comment lines
        if(line.peek() == '#') continue;
        unsigned int element(-1), rgbColor[3];
        line >> element;
        // trap blank last line effect
        if(element == (unsigned int)-1) break;
        line >> rgbColor[0] >> rgbColor[1] >> rgbColor[2];
        GltColor elementColor(double(rgbColor[0])/255.0, double(rgbColor[1])/255.0, double(rgbColor[2])/255.0);
        elementColorMap[element] = elementColor;
    }
#endif
}


void NXOpenGLRenderingEngine::initializeDefaultMaterials(void)
{
    defaultAtomMaterial.face = GL_FRONT;
    defaultAtomMaterial.ambient[0] = 1.0f;
    defaultAtomMaterial.ambient[1] = 1.0f;
    defaultAtomMaterial.ambient[2] = 1.0f;
    defaultAtomMaterial.ambient[3] = 1.0f;
    
    defaultAtomMaterial.diffuse[0] = 1.0f;
    defaultAtomMaterial.diffuse[1] = 1.0f;
    defaultAtomMaterial.diffuse[2] = 1.0f;
    defaultAtomMaterial.diffuse[3] = 1.0f;
    
    defaultAtomMaterial.specular[0] = 0.5f;
    defaultAtomMaterial.specular[1] = 0.5f;
    defaultAtomMaterial.specular[2] = 0.5f;
    defaultAtomMaterial.specular[3] = 1.0f;
    
    defaultAtomMaterial.shininess = 35.0;
    
    defaultAtomMaterial.emission[0] = 0.0f;
    defaultAtomMaterial.emission[1] = 0.0f;
    defaultAtomMaterial.emission[2] = 0.0f;
    defaultAtomMaterial.emission[3] = 1.0f;
    
    defaultBondMaterial.face = GL_FRONT;
    defaultBondMaterial.ambient[0] = 1.0f;
    defaultBondMaterial.ambient[1] = 1.0f;
    defaultBondMaterial.ambient[2] = 1.0f;
    defaultBondMaterial.ambient[3] = 1.0f;
    
    defaultBondMaterial.diffuse[0] = 1.0f;
    defaultBondMaterial.diffuse[1] = 1.0f;
    defaultBondMaterial.diffuse[2] = 1.0f;
    defaultBondMaterial.diffuse[3] = 1.0f;
    
    defaultBondMaterial.specular[0] = 0.5f;
    defaultBondMaterial.specular[1] = 0.5f;
    defaultBondMaterial.specular[2] = 0.5f;
    defaultBondMaterial.specular[3] = 1.0f;
    
    defaultBondMaterial.shininess = 35.0;
    
    defaultBondMaterial.emission[0] = 0.0f;
    defaultBondMaterial.emission[1] = 0.0f;
    defaultBondMaterial.emission[2] = 0.0f;
    defaultBondMaterial.emission[3] = 1.0f;
}


void NXOpenGLRenderingEngine::initializeGL(void)
{
    glClearColor(1.0, 1.0, 1.0, 1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glEnable(GL_LIGHTING);
    glEnable(GL_DEPTH_TEST);
    
    lightModel.setLocalViewer(1);
    lightModel.setTwoSide(0);
    lightModel.set();
    setupDefaultLights();
    
    camera.gluLookAt(0.0, 0.0, 1.0,
                     0.0, 0.0, 0.0,
                     0.0, 1.0, 0.0);
    camera.glViewport(0, 0, width(), height());
    camera.gluPerspective(55, (GLdouble)width()/(GLdouble)height(), 0.1, 50);
    
    initializePlugins();
    
}


void NXOpenGLRenderingEngine::setupDefaultLights(void)
{
    // light model
    lightModel.setLocalViewer(1);
    lightModel.setTwoSide(0);
    lightModel.set();
    
    // initialize light data
    GLint numSupportedOpenGLLights = 0;
    glGetIntegerv(GL_MAX_LIGHTS, &numSupportedOpenGLLights);
    lights.clear();
    for(GLint iLight=0; iLight<numSupportedOpenGLLights; ++iLight)
    {
        lights.push_back(GltLight(iLight+GL_LIGHT0));
    }
    
    GltColor const WHITE(1.0,1.0,1.0,1.0);
    lights[0].isEnabled() = true;
    lights[0].ambient() = 0.1 * WHITE;
    lights[0].diffuse() = 0.5 * WHITE;
    lights[0].specular() = 0.5 * WHITE;
    lights[0].position() = Vector(-50.0, 70.0, 30.0);
    lights[0].isDirectional() = true;
    lights[0].inEyeSpace() = true;
    lights[0].set();
    
    lights[1].isEnabled() = true;
    lights[1].ambient() = 0.1 * WHITE;
    lights[1].diffuse() = 0.5 * WHITE;
    lights[1].specular() = 0.5 * WHITE;
    lights[1].position() = Vector(-20.0, 20.0, 20.0);
    lights[1].isDirectional() = true;
    lights[1].inEyeSpace() = true;
    lights[1].set();
    
    for(GLint iLight=2; iLight<numSupportedOpenGLLights; ++iLight) {
        lights[iLight].isEnabled() = false;
        lights[iLight].ambient() = 0.1 * WHITE;
        lights[iLight].diffuse() = 0.5 * WHITE;
        lights[iLight].specular() = 0.5 * WHITE;
        lights[iLight].position() = Vector(0.0, 0.0, 100.0);
        lights[iLight].set();
    }
    
}


void NXOpenGLRenderingEngine::resizeGL(int width, int height)
{
    camera.resizeViewport(width, height);
    camera.glSetViewport();
    camera.glSetProjection();
    // glMatrixMode(GL_PROJECTION);
    // glLoadIdentity();
    // gluPerspective(55, (GLdouble)width/(GLdouble)height, 0.1, 50);
    // camera.glGetProjection();
    // camera.glGetViewport();
    
/*    if(isOrthographicProjection)
        orthographicProjection.set();
    else
        perspectiveProjection.set();
    
    viewport.set((GLint) width, (GLint) height);*/
}


void NXOpenGLRenderingEngine::paintGL(void)
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    drawSkyBlueBackground();
    camera.glSetPosition();
    camera.glSetProjection();
    rootSceneGraphNode->applyRecursive();
    glFlush();
    swapBuffers();
}


void NXOpenGLRenderingEngine::drawSkyBlueBackground(void)
{
    glDisable(GL_LIGHTING);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    // * GLPane.py::standard_repaint_0()
    // * drawer.py::drawFullWindow()
    GltColor vtColors0(0.9, 0.9, 0.9, 1.0);
    GltColor vtColors1(0.9, 0.9, 0.9, 1.0);
    GltColor vtColors2(0.33, 0.73, 1.0, 1.0);
    GltColor vtColors3(0.33, 0.73, 1.0, 1.0);
    glBegin(GL_QUADS);
    vtColors0.glColor();
    glVertex3f(-1, -1, 0.999);
    vtColors1.glColor();
    glVertex3f(1, -1, 0.999);
    vtColors2.glColor();
    glVertex3f(1, 1, 0.999);
    vtColors3.glColor();
    glVertex3f(-1, 1, 0.999);
    glEnd();
    glEnable(GL_LIGHTING);
}


NXSGOpenGLNode*
    NXOpenGLRenderingEngine::createSceneGraph(NXMoleculeSet *const molSetPtr)
{
    /// @todo Trap soft-failure cases where pointer returned is non-NULL
    /// but commandResult shows error

    NXSGOpenGLNode *moleculeSetNode = NULL;
    try {
        moleculeSetNode = new NXSGOpenGLNode;
    }
    catch(...) {
        SetResult(commandResult, NX_INTERNAL_ERROR,
                  "Failed to initialize scenegraph node for molecule set");
        return NULL;
    }
    
    OBMolIterator molIter;
    for(molIter = molSetPtr->moleculesBegin();
        molIter != molSetPtr->moleculesEnd();
        ++molIter)
    {
        if((*molIter)->Empty())
            continue;
        NXSGOpenGLNode* molNode = createSceneGraph(*molIter);
        if(molNode != NULL) {
            bool childAdded = moleculeSetNode->addChild(molNode);
            if(!childAdded)
                return moleculeSetNode;
        }
        else {
            return moleculeSetNode;
        }
    }
    
    NXMoleculeSetIterator childrenIter;
    for(childrenIter = molSetPtr->childrenBegin();
        childrenIter != molSetPtr->childrenEnd();
        ++childrenIter)
    {
        NXSGOpenGLNode *childMoleculeSetNode = createSceneGraph(*childrenIter);
        if(childMoleculeSetNode != NULL) {
            bool childAdded = moleculeSetNode->addChild(childMoleculeSetNode);
            if(!childAdded)
                return moleculeSetNode;
        }
        else {
            return moleculeSetNode;
        }
    }
    return moleculeSetNode;
}


NXSGOpenGLNode* NXOpenGLRenderingEngine::createSceneGraph(OBMol *const molPtr)
{
    /// @todo Trap soft-failure cases where pointer returned is non-NULL
    /// but commandResult shows error
    
    assert(!molPtr->Empty());
    
    Vector const canonicalZAxis(0.0, 0.0, 1.0);
    set<OBAtom*> renderedAtoms; // tracks atoms already rendered
    OBAtomIterator atomIter;
    
    // first atom
    OBAtom *firstAtomPtr = molPtr->BeginAtom(atomIter);
    if(firstAtomPtr == (OBAtom*) NULL) {
        string const source("Molecule scenegraph creation");
        string const msg("empty molecule slipped past check");
        SetResult(commandResult, NX_INTERNAL_ERROR, source+" - "+msg);
        return (NXSGOpenGLNode*) NULL;
    }
    
    Vector const firstAtomPosition(firstAtomPtr->GetX(),
                                   firstAtomPtr->GetY(),
                                   firstAtomPtr->GetZ());
    
    NXSGOpenGLTranslate *rootMoleculeNode = NULL;
    try {
        rootMoleculeNode =
            new NXSGOpenGLTranslate(firstAtomPosition.x(),
                                    firstAtomPosition.y(),
                                    firstAtomPosition.z());
    }
    catch(...) {
        if(rootMoleculeNode != NULL)
            delete rootMoleculeNode;
        rootMoleculeNode = NULL;
        SetResult(commandResult,
                  NX_INTERNAL_ERROR,
                  "Error translating to first atom position");
        return NULL;
    }
    
    NXSGOpenGLNode *firstAtomNode =
        createSceneGraph(molPtr,
                         firstAtomPtr,
                         renderedAtoms,
                         canonicalZAxis);
    if(firstAtomNode != NULL) {
        bool childAdded = rootMoleculeNode->addChild(firstAtomNode);
        if(!childAdded) {
            SetResult(commandResult, NX_INTERNAL_ERROR,
                      "Error adding child to first atom node");
            return rootMoleculeNode;
        }
    }
    else {
        return rootMoleculeNode;
    }
    
    // rest of the atoms
    OBAtom *atomPtr = molPtr->NextAtom(atomIter);
    while(atomPtr != (OBAtom*) NULL) {
        set<OBAtom*>::iterator memberIter = renderedAtoms.find(atomPtr);
        if(memberIter == renderedAtoms.end()) { // atom not already rendered
            Vector const atomPosition(atomPtr->GetX(),
                                      atomPtr->GetY(),
                                      atomPtr->GetZ());
            Vector const atomRelativePosition = 
                (atomPosition - firstAtomPosition);
            // move scenegraph "cursor" to this atom
            NXSGOpenGLTranslate *translateToAtomNode = NULL;
            try {
                translateToAtomNode =
                    new NXSGOpenGLTranslate(atomRelativePosition.x(),
                                            atomRelativePosition.y(),
                                            atomRelativePosition.z());
            }
            catch(...) {
                if(translateToAtomNode != NULL)
                    delete translateToAtomNode;
                SetResult(commandResult, NX_INTERNAL_ERROR,
                          "Error translating to atom");
                return rootMoleculeNode;
            }
            
            bool childAdded = rootMoleculeNode->addChild(translateToAtomNode);
            if(!childAdded) {
                SetResult(commandResult, NX_INTERNAL_ERROR,
                          "Error adding translate-to-atom node to molecule root");
                return rootMoleculeNode;
            }
            // render subscenegraph rooted at this atom
            NXSGOpenGLNode *atomNode = 
                createSceneGraph(molPtr,
                                 atomPtr,
                                 renderedAtoms,
                                 canonicalZAxis);
            if(atomNode == NULL)
                return rootMoleculeNode;
            else {
                bool childAdded = translateToAtomNode->addChild(atomNode);
                if(!childAdded) {
                    SetResult(commandResult, NX_INTERNAL_ERROR,
                              "Error adding atom sphere node as child of translation");
                    return rootMoleculeNode;
                }
            }
        }
        atomPtr = molPtr->NextAtom(atomIter);
    }
    return rootMoleculeNode;
}


NXSGOpenGLNode*
    NXOpenGLRenderingEngine::createSceneGraph(OBMol *const molPtr,
                                              OBAtom *const atomPtr,
                                              set<OBAtom*>& renderedAtoms,
                                              Vector const& zAxis)
{
    /// @todo Trap soft-failure cases where pointer returned is non-NULL
    /// but commandResult shows error
    
    // Precondition: *atomPtr shouldn't have been rendered
    assert(renderedAtoms.find(atomPtr) == renderedAtoms.end());
    
    // Do nothing if no rendering plugins
    if(!rendererInitialized) {
        SetResult(commandResult, NX_INTERNAL_ERROR,
                  "Rendering plugin not set/initialized");
        return NULL;
    }
    
    // translate origin to atom center
    Vector atomPosition(atomPtr->GetX(), atomPtr->GetY(), atomPtr->GetZ());
    
    // default color
    NXRGBColor defaultElementColor(0.0, 0.0, 0.0);
    map<uint, NXRGBColor>::iterator defaultElementColorIter =
        elementColorMap.find(atomPtr->GetAtomicNum());
    if(defaultElementColorIter != elementColorMap.end())
        defaultElementColor = defaultElementColorIter->second;
        
    // set default material parameters
    defaultAtomMaterial.ambient[0] = defaultElementColor.r;
    defaultAtomMaterial.ambient[1] = defaultElementColor.g;
    defaultAtomMaterial.ambient[2] = defaultElementColor.b;
    defaultAtomMaterial.ambient[3] = 1.0;
    defaultAtomMaterial.diffuse[0] = defaultElementColor.r;
    defaultAtomMaterial.diffuse[1] = defaultElementColor.g;
    defaultAtomMaterial.diffuse[2] = defaultElementColor.b;
    defaultAtomMaterial.diffuse[3] = 1.0;
    defaultAtomMaterial.specular[0] = defaultElementColor.r;
    defaultAtomMaterial.specular[1] = defaultElementColor.g;
    defaultAtomMaterial.specular[2] = defaultElementColor.b;
    defaultAtomMaterial.specular[3] = 1.0;
    
    // create scenegraph node and mark atom as rendered
    NXAtomRenderData atomRenderData(atomPtr->GetAtomicNum());
    atomRenderData.addData(static_cast<void const *>(&defaultAtomMaterial));
    NXSGOpenGLNode *const atomNode = renderer->renderAtom(atomRenderData);
    if(atomNode == NULL) {
        commandResult = renderer->getCommandResult();
        return NULL;
    }
    renderedAtoms.insert(atomPtr); // mark as rendered
    
    // render outgoing bonds and neighbouring atoms (if applicable) as children
    OBBondIterator bondIter;
    OBBond *bondPtr(NULL);
    for(bondPtr = atomPtr->BeginBond(bondIter);
        bondPtr != NULL;
        bondPtr = atomPtr->NextBond(bondIter))
    {
        // compute bond orientation
        OBAtom *const nbrAtomPtr = bondPtr->GetNbrAtom(atomPtr);
        Vector const nbrAtomPosition(nbrAtomPtr->GetX(),
                                     nbrAtomPtr->GetY(),
                                     nbrAtomPtr->GetZ());
        Vector newZAxis = (nbrAtomPosition - atomPosition);
        newZAxis.normalize();
        Vector const rotationAxis = xProduct(zAxis, newZAxis);
        real const rotationAngleDeg = acos(newZAxis * zAxis) * 180.0 / M_PI;
        
        // align z-axis with bond
        NXSGOpenGLRotate *rotateZAxisNode = NULL;
        try {
            rotateZAxisNode =
                new NXSGOpenGLRotate(rotationAngleDeg,
                                     rotationAxis.x(),
                                     rotationAxis.y(),
                                     rotationAxis.z());
        }
        catch(...) {
            SetResult(commandResult, NX_INTERNAL_ERROR,
                      "Error creating axis rotation scenegraph node");
            return atomNode;
        }
        
        bool childAdded = atomNode->addChild(rotateZAxisNode);
        if(!childAdded) {
            SetResult(commandResult, NX_INTERNAL_ERROR,
                      "Error adding rotation node as child to atom node");
            return atomNode;
        }
        
        void const *const defBondMatPtr = 
            static_cast<void const*>(&defaultBondMaterial);
        NXBondRenderData bondRenderData(bondPtr->GetBondOrder(),
                                        bondPtr->GetLength());
        bondRenderData.addData(defBondMatPtr);
        NXSGOpenGLNode *const bondNode = renderer->renderBond(bondRenderData);
        if(bondNode == NULL) {
            commandResult = renderer->getCommandResult();
            return atomNode;
        }
        childAdded = rotateZAxisNode->addChild(bondNode);
        if(!childAdded) {
            SetResult(commandResult, NX_INTERNAL_ERROR,
                      "Error adding bond node to z-axis rotation node");
            return atomNode;
        }
        // render neighbouring atom not already done, render submolecule
        set<OBAtom*>::iterator memberIter = renderedAtoms.find(nbrAtomPtr);
        if(memberIter == renderedAtoms.end()) {
            
            // translate to neighbouring atom center
            double const bondLength = bondPtr->GetLength();
            NXSGOpenGLTranslate *translateToNbrAtomNode = NULL;
            try {
                translateToNbrAtomNode =
                    new NXSGOpenGLTranslate(0.0, 0.0, bondLength);
            }
            catch(...) {
                SetResult(commandResult, NX_INTERNAL_ERROR,
                          "Error creating trans-bond translation scenegraph node");
                return atomNode;
            }
            childAdded = bondNode->addChild(translateToNbrAtomNode);
            if(!childAdded) {
                SetResult(commandResult, NX_INTERNAL_ERROR,
                          "Error adding trans-bond translation node as child of bond-node");
                return atomNode;
            }
            
            // create scenegraph rooted at neighbouring atom
            NXSGOpenGLNode *nbrAtomNode =
                createSceneGraph(molPtr,
                                 nbrAtomPtr,
                                 renderedAtoms,
                                 atomPosition);
            if(nbrAtomNode == NULL) {
                return atomNode;
            }
            else {
                childAdded = translateToNbrAtomNode->addChild(nbrAtomNode);
                if(!childAdded) {
                    SetResult(commandResult, NX_INTERNAL_ERROR,
                              "Error adding neighboring-atom scenegraph subtree"
                              " as child of trans-bond translation node");
                    return atomNode;
                }
            }
        }
    }
    
    renderedAtoms.insert(atomPtr);
    return atomNode;
}


void NXOpenGLRenderingEngine::resetView(void)
{
    if(isSingleMolecule && mol == NULL ||
       !isSingleMolecule && rootMoleculeSet == NULL)
        return;
    
    // create axis-aligned bounding box
    BoundingBox bbox;
    if(isSingleMolecule)
        bbox = GetMoleculeBoundingBox(mol);
    else
        bbox = GetMoleculeSetBoundingBox(rootMoleculeSet);
    Vector bboxMin = bbox.min();
    Vector bboxMax = bbox.max();
    
    real const bboxXWidth = 1.0*(bboxMax.x() - bboxMin.x());
    real const bboxYWidth = 1.0*(bboxMax.y() - bboxMin.y());
    real const bboxZDepth = 1.0*(bboxMax.z() - bboxMin.z());
    
    real const projCubeWidth = max(bboxXWidth, max(bboxYWidth, bboxZDepth));
    real const circumSphereRad = sqrt(3.0*0.25*projCubeWidth*projCubeWidth);
    real const circumSphereDia = 2.0 * circumSphereRad;
    Vector const bboxCenter = bbox.center();
    
    real l, r, b, t;
    real const n = 1.0;
    real const f = n + circumSphereDia;
    real const aspect = real(width()) / real(height());
    if(aspect < 1.0) {
        l = bboxCenter.x() - circumSphereRad;
        r = bboxCenter.x() + circumSphereRad;
        b = bboxCenter.y() - circumSphereRad / aspect;
        t = bboxCenter.y() + circumSphereRad / aspect;
    }
    else {
        l = bboxCenter.x() - aspect * circumSphereRad;
        r = bboxCenter.x() + aspect * circumSphereRad;
        b = bboxCenter.y() - circumSphereRad;
        t = bboxCenter.y() + circumSphereRad;
    }
    
    makeCurrent();
    camera.gluLookAt(bboxCenter.x(), bboxCenter.y(),
                     bboxCenter.z()+circumSphereRad+n,
                     bboxCenter.x(), bboxCenter.y(), bboxCenter.z(),
                     0.0, 1.0, 0.0);
    // camera.gluPerspective(60.0, double(width())/double(height()), n, f);
    camera.glOrtho(l, r, b, t, n, f);

    updateGL();
}


BoundingBox
    NXOpenGLRenderingEngine::
    GetMoleculeSetBoundingBox(NXMoleculeSet *const molSetPtr)
{
    
    BoundingBox bbox;
    
    // include all atoms
    OBMolIterator molIter;
    for(molIter = molSetPtr->moleculesBegin();
        molIter != molSetPtr->moleculesEnd();
        ++molIter)
    {
        OBMol *const molPtr = *molIter;
        bbox += GetMoleculeBoundingBox(molPtr);
    }
    
    // include children molecule-sets
    NXMoleculeSetIterator molSetIter;
    for(molSetIter = molSetPtr->childrenBegin();
        molSetIter != molSetPtr->childrenEnd();
        ++molSetIter)
    {
        NXMoleculeSet *const molSetPtr = *molSetIter;
        bbox += GetMoleculeSetBoundingBox(molSetPtr);
    }
    return bbox;
}


BoundingBox
    NXOpenGLRenderingEngine::GetMoleculeBoundingBox(OBMol *const molPtr)
{
    BoundingBox bbox;
    OBAtomIterator atomIter;
    OBAtom *atomPtr = NULL;
    
    for(atomPtr = molPtr->BeginAtom(atomIter);
        atomPtr != NULL;
        atomPtr = molPtr->NextAtom(atomIter))
    {
        Vector atomPos(real(atomPtr->GetX()),
                       real(atomPtr->GetY()),
                       real(atomPtr->GetZ()));
        bbox += atomPos;
    }
    
    return bbox;
}


void NXOpenGLRenderingEngine::mousePressEvent(QMouseEvent *mouseEvent)
{
    if(mouseEvent->button() == Qt::MidButton &&
       mouseEvent->modifiers() == Qt::NoModifier)
    {
        camera.rotateStartEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else if(mouseEvent->button() == Qt::LeftButton &&
            mouseEvent->modifiers() == Qt::NoModifier)
    {
        camera.translateStartEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else
        mouseEvent->ignore();
    
    updateGL();
}


void NXOpenGLRenderingEngine::mouseMoveEvent(QMouseEvent *mouseEvent)
{
    assert(mouseEvent->button() == Qt::NoButton);
    Qt::MouseButtons buttons = mouseEvent->buttons();
    
    if((buttons & Qt::MidButton) &&
       mouseEvent->modifiers() == Qt::NoModifier)
    {
        camera.rotatingEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else if((buttons & Qt::LeftButton) &&
            mouseEvent->modifiers() == Qt::NoModifier)
    {
        camera.translatingEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else
        mouseEvent->ignore();
    
    updateGL();
}


void NXOpenGLRenderingEngine::mouseReleaseEvent(QMouseEvent *mouseEvent)
{
    if(mouseEvent->button() == Qt::MidButton)
    {
        camera.rotateStopEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else if(mouseEvent->button() == Qt::LeftButton)
    {
        camera.translateStopEvent(mouseEvent->x(), mouseEvent->y());
        mouseEvent->accept();
    }
    else
        mouseEvent->ignore();
    
    updateGL();
}


bool NXOpenGLRenderingEngine::setRenderer(NXOpenGLRendererPlugin *const plugin)
{
    if(renderer != plugin) {
        renderer = plugin;
        rendererInitialized = false;
        return true;
    }
    else {
        return false;
    }
}


bool NXOpenGLRenderingEngine::initializePlugins(void)
{
    // called from initializeGL so context is current
    NXCommandResult *rendererInitializationResult = renderer->initialize();
    rendererInitialized = 
        (rendererInitializationResult->getResult() == (int) NX_CMD_SUCCESS);
    if(!rendererInitialized) {
        ostringstream logMsgStream;
        logMsgStream << "Rendering plugins couldn't be initialized. ";
        vector<QString> const& msgs =
            rendererInitializationResult->getParamVector();
        vector<QString>::const_iterator msgIter;
        for(msgIter = msgs.begin(); msgIter != msgs.end(); ++msgIter) {
            logMsgStream << ' ' << qPrintable(*msgIter);
        }
        NXLOG_SEVERE("Graphics plugin initialization", logMsgStream.str());
    }
    else {
        NXLOG_INFO("Graphics plugin initialization", "Success");
    }
    return rendererInitialized;
}


bool NXOpenGLRenderingEngine::cleanupPlugins(void)
{
    makeCurrent();
    NXCommandResult *rendererCleanupResult = renderer->cleanup();
    if(rendererCleanupResult->getResult() != (int) NX_CMD_SUCCESS) {
        ostringstream logMsgStream;
        logMsgStream << "Rendering plugins couldn't be cleaned up. ";
        vector<QString> const& msgs =
            rendererCleanupResult->getParamVector();
        vector<QString>::const_iterator msgIter;
        for(msgIter = msgs.begin(); msgIter != msgs.end(); ++msgIter) {
            logMsgStream << ' ' << qPrintable(*msgIter);
        }
        NXLOG_WARNING("Graphics plugin cleanup", logMsgStream.str());
        return false;
    }
    else {
        NXLOG_INFO("Graphics plugin cleanup", "Success");
    }
    rendererInitialized = false;
    return true;
}


} // Nanorex
