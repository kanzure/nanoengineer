// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <fstream>
#include <sstream>
#include <cassert>
#include <set>
#include <cmath>

#include <Nanorex/Interface/NXEntityManager.h>
#include <Nanorex/Interface/NXAtomData.h>
#include "NXOpenGLRenderingEngine.h"

using namespace std;
using namespace OpenBabel;


#ifdef NX_DEBUG
#define NX_DEBUG_FAIL assert(0)
#else
#define NX_DEBUG_FAIL
#endif


NXOpenGLRenderingEngine::NXOpenGLRenderingEngine(QWidget *parent)
: QGLWidget(parent), NXRenderingEngine(), camera(this)
{
	initializeElementColorMap();
	initializeDefaultMaterials();
}


NXOpenGLRenderingEngine::~NXOpenGLRenderingEngine()
{
	cleanupPlugins();
}

#if 0
bool NXOpenGLRenderingEngine::setRootMoleculeSet(NXMoleculeSet *const moleculeSet)
{
    isSingleMolecule = false;
    deleteSceneGraph();
    rootMoleculeSet = moleculeSet;
    rootSceneGraphNode = createSceneGraph(rootMoleculeSet);
    if(rootSceneGraphNode != NULL &&
       commandResult.getResult() == (int) NX_CMD_SUCCESS)
    {
        resetView();
#ifdef NX_DEBUG
        rootSceneGraphNode->writeDotGraph(std::cerr);
#endif
        return true;
    }
    else
        return false;
}
#endif


#if 0
bool NXOpenGLRenderingEngine::setRootMolecule(OpenBabel::OBMol *const molPtr)
{
    isSingleMolecule = true;
    deleteSceneGraph();
    rootMolecule = molPtr;
    rootSceneGraphNode = createSceneGraph(rootMolecule);
    if(rootSceneGraphNode != NULL &&
       commandResult.getResult() == (int) NX_CMD_SUCCESS)
    {
        resetView();
#ifdef NX_DEBUG
        rootSceneGraphNode->writeDotGraph(std::cerr);
#endif
        return true;
    }
    else
        return false;
}
#endif


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
	
	// initializePlugins();
	
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
	drawCompass();
	camera.glSetPosition();
	camera.glSetProjection();
	
	if(currentFrameIndex >= 0) {
		NXSGOpenGLNode *currentFrameSGNode =
			dynamic_cast<NXSGOpenGLNode*>(frames[currentFrameIndex]);
		currentFrameSGNode->applyRecursive();
	}
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


void NXOpenGLRenderingEngine::drawCompass(void)
{
	/// @todo
}


NXSGNode*
NXOpenGLRenderingEngine::createSceneGraph (NXMoleculeSet *const molSetPtr)
{
	ClearResult(commandResult);
	// Do nothing if no rendering plugins
	if(!pluginsInitialized) {
		SetResult(commandResult,
		          NX_INTERNAL_ERROR,
		          "Renderer-plugins not set/initialized");
		return NULL;
	}
	
	renderedAtoms.clear();
	renderedBonds.clear();
	NXSGOpenGLNode *node = createOpenGLSceneGraph(molSetPtr);
	return static_cast<NXSGNode*>(node);
}


#if 0 // removed this method from NXRenderingEngine
NXSGNode* createSceneGraph (OpenBabel::OBMol *const molPtr) {
	// Do nothing if no rendering plugins
	if(!pluginsInitialized) {
		SetResult(commandResult, NX_INTERNAL_ERROR,
"Rendering plugin not set/initialized");
		return NULL;
	}
	ClearResult(commandResult);
	NXSGOpenGLNode *node = createOpenGLSceneGraph(molPtr);
	return static_cast<NXSGNode*>(node);
}
#endif

NXSGOpenGLNode*
NXOpenGLRenderingEngine::createOpenGLSceneGraph(NXMoleculeSet *const molSetPtr)
{
    /// @todo Trap soft-failure cases where pointer returned is non-NULL
    /// but commandResult shows error
	NXSGOpenGLNode *moleculeSetNode = NULL;
	try {
		moleculeSetNode = new NXSGOpenGLNode; 
	}
	catch(...) {
		SetResult(commandResult, NX_INTERNAL_ERROR,
		          "Failed to initialize scenegraph node for molecule set " +
		          molSetPtr->getTitle());
		return (NXSGOpenGLNode*) NULL;
	}
	
	OBMolIterator molIter;
	for(molIter = molSetPtr->moleculesBegin();
	    molIter != molSetPtr->moleculesEnd();
	    ++molIter)
	{
		if((*molIter)->Empty())
			continue;
		NXSGOpenGLNode* molNode = createOpenGLSceneGraph(*molIter);
		if(molNode != NULL &&
		   commandResult.getResult() == (int) NX_CMD_SUCCESS)
		{
			bool childAdded = moleculeSetNode->addChild(molNode);
			if(!childAdded) {
				NX_DEBUG_FAIL;
				return moleculeSetNode;
			}
		}
		else {
			NX_DEBUG_FAIL;
			return moleculeSetNode;
		}
		/// @todo POST-FNANO: delete molNode upon failures?
	}
	
	NXMoleculeSetIterator childrenIter;
	for(childrenIter = molSetPtr->childrenBegin();
	    childrenIter != molSetPtr->childrenEnd();
	    ++childrenIter)
	{
		NXSGOpenGLNode *childMoleculeSetNode = createOpenGLSceneGraph(*childrenIter);
		if(childMoleculeSetNode != NULL &&
		   commandResult.getResult() == (int) NX_CMD_SUCCESS)
		{
			bool childAdded = moleculeSetNode->addChild(childMoleculeSetNode);
			if(!childAdded) {
				NX_DEBUG_FAIL;
				return moleculeSetNode;
			}
		}
		else {
			NX_DEBUG_FAIL;
			return moleculeSetNode;
		}
		/// @todo POST-FNANO: delete childMoleculeSetNode upon failures?
	}
	return moleculeSetNode;
}


NXSGOpenGLNode*
NXOpenGLRenderingEngine::createOpenGLSceneGraph(OBMol *const molPtr)
{
	assert(!molPtr->Empty());
	
	Vector const canonicalZAxis(0.0, 0.0, 1.0);
	OBAtomIterator atomIter;
	
    // Find first atom that is not already rendered
	// Necessary because bonds can bridge molecules and molecule-sets and in
	// the case of the second to last molecules rendered, their first atoms
	// may have been rendered while traversing the previous molecules.
	
	OBAtom *firstAtomPtr = molPtr->BeginAtom(atomIter);
	
	if(firstAtomPtr == (OBAtom*) NULL) {
		string const source("Molecule scenegraph creation");
		string const msg("empty molecule slipped past check");
		SetResult(commandResult, NX_INTERNAL_ERROR, source + " - " + msg);
		NX_DEBUG_FAIL;
		return (NXSGOpenGLNode*) NULL;
	}
	
	while(firstAtomPtr != (OBAtom*) NULL && isRendered(firstAtomPtr))
		firstAtomPtr = molPtr->NextAtom(atomIter);
	
	if(firstAtomPtr == (OBAtom*) NULL)
		return new NXSGOpenGLNode;
	
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
		NX_DEBUG_FAIL;
		return NULL;
	}
	
	NXSGOpenGLNode *firstAtomNode =
		createOpenGLSceneGraph(molPtr, firstAtomPtr, canonicalZAxis);
	if(firstAtomNode != NULL && 
	   commandResult.getResult() == (int) NX_CMD_SUCCESS)
	{
        // submolecule scenegraph created completely and successfully
		bool childAdded = rootMoleculeNode->addChild(firstAtomNode);
		if(!childAdded) {
			SetResult(commandResult, NX_INTERNAL_ERROR,
			          "Error adding child to first atom node");
			NX_DEBUG_FAIL;
			return rootMoleculeNode;
		}
	}
	else {
		NX_DEBUG_FAIL;
        // either scenegraph could not be created or was created partially
        // commandResult should hold the error
		return rootMoleculeNode;
	}
	/// @todo POST-FNANO delete firstAtomNode upon failures?
	
    // rest of the atoms
	OBAtom *atomPtr = molPtr->NextAtom(atomIter);
	for(; atomPtr != (OBAtom*) NULL;
	    atomPtr = molPtr->NextAtom(atomIter))
	{
		if(isRendered(atomPtr)) // atom already rendered
			continue;
		
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
			NX_DEBUG_FAIL;
			return rootMoleculeNode;
		}
		
		bool childAdded = rootMoleculeNode->addChild(translateToAtomNode);
		if(!childAdded) {
			SetResult(commandResult, NX_INTERNAL_ERROR,
			          "Error adding translate-to-atom node to molecule root");
			NX_DEBUG_FAIL;
			return rootMoleculeNode;
		}
			/// @todo POST-FNANO delete translateToAtomNode upon failure?
		
            // render subscenegraph rooted at this atom
		NXSGOpenGLNode *atomNode = 
			createOpenGLSceneGraph(molPtr, atomPtr, canonicalZAxis);
		
		if(atomNode != NULL &&
		   commandResult.getResult() == (int) NX_CMD_SUCCESS)
		{
			bool childAdded = translateToAtomNode->addChild(atomNode);
			if(!childAdded) {
				SetResult(commandResult, NX_INTERNAL_ERROR,
				          "Error submolecule scenegraph as child of "
				          "translation");
				NX_DEBUG_FAIL;
				return rootMoleculeNode;
			}
		}
		else {
			NX_DEBUG_FAIL;
			return rootMoleculeNode;
		}
			/// @todo POST-FNANO delete atomNode upon failures?
	} // loop over atoms
	
	return rootMoleculeNode;
}


NXSGOpenGLNode*
NXOpenGLRenderingEngine::getRotationNode(Vector const& zAxis,
                                         Vector const& newZAxis)
{
	double const dotProduct = zAxis * newZAxis;
	
	if(dotProduct < 0.99999) {
		// Angle between both vectors is more than 0.25 degrees 
		// therefore there is a well-defined rotation
		real const rotationAngleDeg =
			acos(dotProduct) * 180.0 / M_PI;
		
		Vector rotationAxis = xProduct(zAxis, newZAxis);
		rotationAxis.normalize();
		
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
			NX_DEBUG_FAIL;
			return NULL;
		}
		
		return rotateZAxisNode;
	}
	else {
		// length of cross-product is below 1%
		// therefore the two z-axes are parallel to within numerical error
		// bypass creation of rotation scenegraph node
		return NULL;
		
	}
	
}

/// Render given atom in the molecule in a depth-first manner
/// Update the rendered-atoms set to include this atom if successful
NXSGOpenGLNode*
NXOpenGLRenderingEngine::createOpenGLSceneGraph(OBMol *const molPtr,
                                                OBAtom *const atomPtr,
                                                Vector const& zAxis)
{
	// Precondition: *atomPtr shouldn't have been rendered
	assert(renderedAtoms.find(atomPtr) == renderedAtoms.end());
	
    // Do nothing if no rendering plugins
	if(!pluginsInitialized) {
		SetResult(commandResult, NX_INTERNAL_ERROR,
		          "Rendering plugin not set/initialized");
		NX_DEBUG_FAIL;
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
	// NXAtomRenderData atomRenderData(atomPtr->GetAtomicNum());
	// atomRenderData.addData(static_cast<void const *>(&defaultAtomMaterial));
	assert(atomPtr->HasData(NXAtomDataType));
	NXAtomData *atomData =
		static_cast<NXAtomData*>(atomPtr->GetData(NXAtomDataType)); 
	assert(atomData->GetDataType() == NXAtomDataType);
	assert(atomData != NULL);
	string const& atomRenderStyleCode = atomData->getRenderStyleCode();
	atomData->addSupplementalData(static_cast<void const*>(&defaultAtomMaterial));
	/// @todo consider if supplemental data can be added repeatedly and the
	/// corresponding vector grows needlessly
	
	
	// The following dynamic_cast is ok because plugins were type-checked at
	// initialization time
	/// @fixme Use qobject_cast instead of static_cast? dynamic_cast won't work
	NXOpenGLRendererPlugin *renderer =
		static_cast<NXOpenGLRendererPlugin*>(renderStyleMap[atomRenderStyleCode]);
	if(renderer == (NXOpenGLRendererPlugin*) NULL) {
		SetResult(commandResult,
		          NX_PLUGIN_CAUSED_ERROR,
		          "No renderer-plugin found for rendering-style-code '" +
		          atomRenderStyleCode + "'");
		/// @todo POST-FNANO more descriptive error message - which atom# and moleculeSet
		NX_DEBUG_FAIL;
		return (NXSGOpenGLNode*) NULL;
	}
	NXSGOpenGLNode *const atomNode = renderer->renderAtom(*atomData);
	if(atomNode == NULL) {
		commandResult = renderer->getCommandResult();
		NX_DEBUG_FAIL;
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
		OBAtom *const nbrAtomPtr = bondPtr->GetNbrAtom(atomPtr);
		assert(nbrAtomPtr != atomPtr);
		Vector const nbrAtomPosition(nbrAtomPtr->GetX(),
		                             nbrAtomPtr->GetY(),
		                             nbrAtomPtr->GetZ());
		Vector const nbrAtomRelativePosition = (nbrAtomPosition - atomPosition);
		Vector newZAxis = nbrAtomRelativePosition;
		newZAxis.normalize();
		
		if(!isRendered(bondPtr)) {
        // compute bond orientation
			
			// Rotate z-axis to align with bond-direction if necessary
			NXSGOpenGLNode *rotateZAxisNode = getRotationNode(zAxis,newZAxis);
			if(rotateZAxisNode == NULL)
				rotateZAxisNode = atomNode;
			
			else {
				bool childAdded = atomNode->addChild(rotateZAxisNode);
				if(!childAdded) {
					SetResult(commandResult, NX_INTERNAL_ERROR,
					          "Error adding rotation node as child to atom node");
					NX_DEBUG_FAIL;
					return atomNode;
				}	
			}
			
			void const *const defBondMatPtr = 
				static_cast<void const*>(&defaultBondMaterial);
			NXBondData bondRenderData((BondType)bondPtr->GetBondOrder(),
			                          bondPtr->GetLength());
			bondRenderData.addSupplementalData(defBondMatPtr);
			NXSGOpenGLNode *const bondNode = renderer->renderBond(bondRenderData);
			if(bondNode == NULL) {
				commandResult = renderer->getCommandResult();
				NX_DEBUG_FAIL;
				return atomNode;
			}
			bool const childAdded = rotateZAxisNode->addChild(bondNode);
			if(!childAdded) {
				SetResult(commandResult, NX_INTERNAL_ERROR,
				          "Error adding bond node to z-axis rotation node");
				NX_DEBUG_FAIL;
				return atomNode;
			}
			
			markBondRendered(bondPtr);
			
		} // if bond not already rendered
		
		
		if(!isRendered(nbrAtomPtr)) {
			
            // translate to neighbouring atom center
			// double const bondLength = bondPtr->GetLength();
			NXSGOpenGLTranslate *translateToNbrAtomNode = NULL;
			try {
				translateToNbrAtomNode =
					new NXSGOpenGLTranslate(nbrAtomRelativePosition.x(),
					                        nbrAtomRelativePosition.y(),
					                        nbrAtomRelativePosition.z());
			}
			catch(...) {
				SetResult(commandResult, NX_INTERNAL_ERROR,
				          "Error creating trans-bond translation scenegraph node");
				NX_DEBUG_FAIL;
				return atomNode;
			}
			bool const childAdded = atomNode->addChild(translateToNbrAtomNode);
			if(!childAdded) {
				SetResult(commandResult, NX_INTERNAL_ERROR,
				          "Error adding trans-bond translation node as child of"
				          " bond-node");
				NX_DEBUG_FAIL;
				return atomNode;
			}
			
            // create scenegraph rooted at neighbouring atom
			NXSGOpenGLNode *nbrAtomNode =
				createOpenGLSceneGraph(molPtr, nbrAtomPtr, /*newZAxis*/ Vector(0.0, 0.0, 1.0));
			if(nbrAtomNode == NULL) {
				NX_DEBUG_FAIL;
				return atomNode;
			}
			else {
				bool const childAdded =
					translateToNbrAtomNode->addChild(nbrAtomNode);
				if(!childAdded) {
					SetResult(commandResult, NX_INTERNAL_ERROR,
					          "Error adding neighboring-atom scenegraph subtree"
					          " as child of trans-bond translation node");
					NX_DEBUG_FAIL;
					return atomNode;
				}
			}
		} // if neighbouring atom not already rendered
	}
	
	return atomNode;
}


void NXOpenGLRenderingEngine::markBondRendered(OBBond *const bondPtr)
{
	OBAtom *const atom1 = bondPtr->GetBeginAtom();
	OBAtom *const atom2 = bondPtr->GetEndAtom();
	
	pair<OBAtom*,OBAtom*> atomPair = ( atom1 < atom2 ?
	                                   make_pair(atom1, atom2) :
	                                   make_pair(atom2, atom1) );
	renderedBonds.insert(atomPair);
}


bool NXOpenGLRenderingEngine::isRendered(OBAtom *const atomPtr) const
{
	set<OBAtom*>::const_iterator memberIter = renderedAtoms.find(atomPtr);
	bool const result = (memberIter != renderedAtoms.end());
	return result;
}


bool NXOpenGLRenderingEngine::isRendered(OBBond *const bondPtr) const
{
	OBAtom *atom1 = bondPtr->GetBeginAtom();
	OBAtom *atom2 = bondPtr->GetEndAtom();
	
	pair<OBAtom*,OBAtom*> atomPair = (atom1 < atom2 ?
	                                  make_pair(atom1, atom2) :
	                                  make_pair(atom2, atom1));
	
	RenderedBondsTableType::const_iterator memberIter =
		renderedBonds.find(atomPair);
	
	bool const result = (memberIter != renderedBonds.end());
	return result;
}


void NXOpenGLRenderingEngine::resetView(void)
{
    // create axis-aligned bounding box
	if(currentFrameIndex < 0)
		return;
	
	NXMoleculeSet *molSetPtr = moleculeSets[currentFrameIndex];
	BoundingBox bbox = GetBoundingBox(molSetPtr);
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
	real const n = 0.25 * circumSphereDia;
	real const f = 12.0 * circumSphereDia;
	real const aspect = real(width()) / real(height());
	if(aspect < 1.0) {
		l = bboxCenter.x() - circumSphereDia;
		r = bboxCenter.x() + circumSphereDia;
		b = bboxCenter.y() - circumSphereDia / aspect;
		t = bboxCenter.y() + circumSphereDia / aspect;
	}
	else {
		l = bboxCenter.x() - aspect * circumSphereDia;
		r = bboxCenter.x() + aspect * circumSphereDia;
		b = bboxCenter.y() - circumSphereDia;
		t = bboxCenter.y() + circumSphereDia;
	}
	
	makeCurrent();
// 	camera.gluLookAt(bboxCenter.x(), bboxCenter.y(),
// 	                 bboxCenter.z()+circumSphereDia,
// 	                 bboxCenter.x(), bboxCenter.y(), bboxCenter.z(),
// 	                 0.0, 1.0, 0.0);
    // camera.gluPerspective(60.0, double(width())/double(height()), n, f);
	
	camera.gluLookAt(0.0, 0.0, circumSphereDia,
	                 0.0, 0.0, 0.0,
	                 0.0, 1.0, 0.0);
	camera.glOrtho(l, r, b, t, n, f);
	
	updateGL();
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


/// Meant to be called after all renderer-plugins have been set against
/// a render-style. This function initializes all plugins. Calling this
/// function, then including more plugins and then calling this function again
/// will not initialize the newly 
bool NXOpenGLRenderingEngine::initializePlugins(void)
{
	if(pluginsInitialized)
		return true;
	
	bool success = true;
	makeCurrent();
	map<string, NXRendererPlugin*>::iterator pluginIter;
	for(pluginIter = renderStyleMap.begin();
	    pluginIter != renderStyleMap.end();
	    ++pluginIter)
	{
		// since default rendering style must also appear independently
		// do not initialize
		string const& renderStyleCode = pluginIter->first;
		if(renderStyleCode == "def")
			continue;
		
		NXRendererPlugin *plugin = pluginIter->second;
		NXCommandResult const *const result = plugin->initialize();
		
		if(result->getResult() != (int) NX_CMD_SUCCESS) {
			success = false;
			ostringstream logMsgStream;
			logMsgStream << "Plugin for render-style " + pluginIter->first +
				" couldn't be initialized. ";
			vector<QString> const& msgs = result->getParamVector();
			vector<QString>::const_iterator msgIter;
			for(msgIter = msgs.begin(); msgIter != msgs.end(); ++msgIter) {
				logMsgStream << ' ' << qPrintable(*msgIter);
			}
			NXLOG_SEVERE("NXOpenGLRenderingEngine", logMsgStream.str());
		}
		else {
			NXLOG_INFO("NXOpenGLRenderingEngine",
			           "Initialized plugin for render-style " +
			           pluginIter->first);
		}
	}
	
	if(success)
		pluginsInitialized = true;
	
	return success;
}



bool NXOpenGLRenderingEngine::cleanupPlugins(void)
{
	if(!pluginsInitialized)
		return true;
	
	bool success = true;
	makeCurrent();
	
	map<string, NXRendererPlugin*>::iterator pluginIter;
	for(pluginIter = renderStyleMap.begin();
	    pluginIter != renderStyleMap.end();
	    ++pluginIter)
	{
		NXRendererPlugin *plugin = pluginIter->second;
		NXCommandResult const *const result = plugin->cleanup();
		
		if(result->getResult() != (int) NX_CMD_SUCCESS) {
			success = false;
			ostringstream logMsgStream;
			logMsgStream << "Plugin for render-style " + pluginIter->first +
				" could not cleanup. ";
			vector<QString> const& msgs = result->getParamVector();
			vector<QString>::const_iterator msgIter;
			for(msgIter = msgs.begin(); msgIter != msgs.end(); ++msgIter) {
				logMsgStream << ' ' << qPrintable(*msgIter);
			}
			NXLOG_SEVERE("NXOpenGLRenderingEngine", logMsgStream.str());
		}
		else {
			NXLOG_INFO("NXOpenGLRenderingEngine",
			           "Cleaned up plugin for render-style " +
			           pluginIter->first);
		}
	}
	
	pluginsInitialized = false;
	return success;
}


BoundingBox
NXOpenGLRenderingEngine::
GetBoundingBox(NXMoleculeSet *const molSetPtr)
{
	
	BoundingBox bbox;
	
    // include all atoms
	OBMolIterator molIter;
	for(molIter = molSetPtr->moleculesBegin();
	    molIter != molSetPtr->moleculesEnd();
	    ++molIter)
	{
		OBMol *const molPtr = *molIter;
		bbox += GetBoundingBox(molPtr);
	}
	
    // include children molecule-sets
	NXMoleculeSetIterator molSetIter;
	for(molSetIter = molSetPtr->childrenBegin();
	    molSetIter != molSetPtr->childrenEnd();
	    ++molSetIter)
	{
		NXMoleculeSet *const molSetPtr = *molSetIter;
		bbox += GetBoundingBox(molSetPtr);
	}
	return bbox;
}

//..............................................................................

BoundingBox
NXOpenGLRenderingEngine::GetBoundingBox(OBMol *const molPtr)
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

//..............................................................................


Q_EXPORT_PLUGIN2 (NXOpenGLRenderingEngine, NXOpenGLRenderingEngine)
