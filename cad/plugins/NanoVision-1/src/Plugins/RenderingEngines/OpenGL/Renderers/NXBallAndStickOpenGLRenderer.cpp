// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXBallAndStickOpenGLRenderer.h"
#include <Nanorex/Interface/NXBondData.h>
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include "../GLT/guarded_gl_ops.h"
#include "../GLT/glt_error.h"

#include <iostream>



using namespace std;
using namespace Nanorex;

// utility function
inline void guarded_delete(NXSGOpenGLNode* &ptr)
{
	if(ptr != (NXSGOpenGLNode*) NULL) {
		delete ptr;
		ptr = (NXSGOpenGLNode*) NULL;
	}
}


// static data
double const NXBallAndStickOpenGLRenderer::BOND_WIDTH(0.5);

// .............................................................................

/* CONSTRUCTOR */
NXBallAndStickOpenGLRenderer::
NXBallAndStickOpenGLRenderer(NXRenderingEngine *parentEngine)
: NXOpenGLRendererPlugin(parentEngine),
canonicalSphereNode(NULL),
canonicalSphereNodeGuard(),
canonicalCylinderNode(NULL),
canonicalCylinderNodeGuard(),
atomicRadiusMap()
{
	for(int bondType=SINGLE_BOND; bondType<NUM_BOND_TYPES; ++bondType)
		canonicalBondNode[bondType] = (NXSGOpenGLNode*) NULL;
	
	initializeAtomicRadiusMap();
}

// .............................................................................

/* DESTRUCTOR */
NXBallAndStickOpenGLRenderer::~NXBallAndStickOpenGLRenderer()
{
	if(isInitialized())
		cleanup(); // will reset the 'initialize' flag
}

// .............................................................................

void NXBallAndStickOpenGLRenderer::initializeAtomicRadiusMap(void)
{
	atomicRadiusMap[0] = 1.1;
	atomicRadiusMap[1] = 1.2;
	atomicRadiusMap[2] = 1.4;
	atomicRadiusMap[3] = 4.0;
	atomicRadiusMap[4] = 3.0;
	atomicRadiusMap[5] = 2.0;
	atomicRadiusMap[6] = 1.84;
	atomicRadiusMap[7] = 1.55;
	atomicRadiusMap[8] = 1.74;
	atomicRadiusMap[9] = 1.65;
	atomicRadiusMap[10] = 1.82;
	atomicRadiusMap[11] = 4.0;
	atomicRadiusMap[12] = 3.0;
	atomicRadiusMap[13] = 2.5;
	atomicRadiusMap[14] = 2.25;
	atomicRadiusMap[15] = 2.11;
	atomicRadiusMap[16] = 2.11;
	atomicRadiusMap[17] = 2.03;
	atomicRadiusMap[18] = 1.88;
	atomicRadiusMap[19] = 5.0;
	atomicRadiusMap[20] = 4.0;
	atomicRadiusMap[21] = 3.7;
	atomicRadiusMap[22] = 3.5;
	atomicRadiusMap[23] = 3.3;
	atomicRadiusMap[24] = 3.1;
	atomicRadiusMap[25] = 3.0;
	atomicRadiusMap[26] = 3.0;
	atomicRadiusMap[27] = 3.0;
	atomicRadiusMap[28] = 3.0;
	atomicRadiusMap[29] = 3.0;
	atomicRadiusMap[30] = 2.9;
	atomicRadiusMap[21] = 2.7;
	atomicRadiusMap[32] = 2.5;
	atomicRadiusMap[33] = 2.2;
	atomicRadiusMap[34] = 2.1;
	atomicRadiusMap[35] = 2.0;
	atomicRadiusMap[36] = 1.9;
	atomicRadiusMap[51] = 2.2;
	atomicRadiusMap[52] = 2.1;
	atomicRadiusMap[53] = 2.0;
	atomicRadiusMap[54] = 1.9;
	
	atomicRadiusMap[200] = 5.0;
	atomicRadiusMap[201] = 4.0;
	atomicRadiusMap[202] = 3.2;
	atomicRadiusMap[203] = 4.0;
	atomicRadiusMap[204] = 3.5;
	atomicRadiusMap[205] = 3.0;
	atomicRadiusMap[206] = 2.5;
	atomicRadiusMap[207] = 4.0;
	atomicRadiusMap[208] = 5.0;
	atomicRadiusMap[209] = 5.0;
	atomicRadiusMap[210] = 2.5;
	atomicRadiusMap[211] = 2.5;
	atomicRadiusMap[212] = 2.5;
	
	atomicRadiusMap[300] = 4.5;
	atomicRadiusMap[301] = 4.5;
	atomicRadiusMap[302] = 3.0;
	atomicRadiusMap[303] = 4.5;
	atomicRadiusMap[304] = 4.5;
	atomicRadiusMap[305] = 4.5;
	atomicRadiusMap[306] = 3.0;
	atomicRadiusMap[307] = 4.5;
	atomicRadiusMap[310] = 2.3;
	atomicRadiusMap[311] = 2.3;
	atomicRadiusMap[312] = 2.3;
}

// .............................................................................

NXRendererPlugin*
NXBallAndStickOpenGLRenderer::newInstance(NXRenderingEngine *parentEngine) const
{
	NXBallAndStickOpenGLRenderer* newRenderer =
		new NXBallAndStickOpenGLRenderer(parentEngine);
	return static_cast<NXRendererPlugin*>(newRenderer);
}

// .............................................................................

/// Initialize the plugin. If not successful, as indicated by the return
/// command-result, then the instance is left partially initialized.
/// The user is then expected to destroy the instance to ensure proper cleanup
NXCommandResult const *const NXBallAndStickOpenGLRenderer::initialize(void)
{
	commandResult.setResult((int) NX_CMD_SUCCESS);
	
	// using NXRendererPlugin::initialized
	
	initialized = initializeCanonicalGeometryNodes();
	if(initialized) {
		initialized = initializeCanonicalBondNodes();
		if(initialized) {
			for(int bondType = (int)SINGLE_BOND;
			    bondType < (int) NUM_BOND_TYPES;
			    ++bondType)
			{
				bool const addedChild =
					canonicalBondNodeGuard[bondType].
						addChild(canonicalBondNode[bondType]);
				assert(canonicalBondNodeGuard[bondType].getRefCount() == 0);
				assert(canonicalBondNodeGuard[bondType].getNumChildren() == 1);
	            initialized = initialized && addedChild;
			}
		}
	}
	
	if(!initialized)
		cleanup(); // will again reset the 'initialized' flag
	
    // The failure location, if any, should have recorded the error
	return &commandResult;
}

// .............................................................................

/// Renders the canonical sphere and cylinder in the parent engine's OpenGL
/// context
bool NXBallAndStickOpenGLRenderer::initializeCanonicalGeometryNodes(void)
{
	bool success = true;
	
	success = initializeCanonicalSphereNode();
	if(!success)
		return false;
	
	success = initializeCanonicalCylinderNode();
	if(!success)
		return false;
	
	// assign a minimum ref count of 1. If all nodes that access these canonical
	// nodes as parents cleanup, then these nodes will be deleted when their
	// ref count becomes zero. This initial increment will ensure that the
	// ref count is at least one if all other nodes behave correctly
	bool const guardedSphereNode =
		canonicalSphereNodeGuard.addChild(canonicalSphereNode);
	assert(canonicalSphereNode->getRefCount() == 1);
	assert(canonicalSphereNodeGuard.getNumChildren() == 1);
	
	bool const guardedCylinderNode =
		canonicalCylinderNodeGuard.addChild(canonicalCylinderNode);
	assert(canonicalCylinderNode->getRefCount() == 1);
	assert(canonicalCylinderNodeGuard.getNumChildren() == 1);
	
	if(!guardedSphereNode || !guardedCylinderNode) {
		SetError(commandResult,
		         "Could not set up canonical sphere/cylinder node guards");
	}
	
	success = guardedSphereNode && guardedCylinderNode;
	return success;
}

// .............................................................................

/// Encapsulates an OpenGL display list for rendering a unit sphere at the
/// origin in an OpenGL-scenegraph and sets canonicalSphereNode to point to it.
/// Returns true if successful. Upon failure, it releases any resources claimed,
/// sets canonicalSphereNode to NULL and returns false.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalSphereNode(void)
{
    // quick return if node is already created
	if(canonicalSphereNode != NULL)
		return true;
	
	try {
		canonicalSphereNode = new NXSGOpenGLRenderable;
#ifdef NX_DEBUG
		canonicalSphereNode->setName("CanonicalSphere");
#endif
	}
	catch (...) {
        // fail silently if unable to create for any reason
		canonicalSphereNode = NULL;
		SetError(commandResult, "Could not allocated sphere-scenegraph node");
		return false;
	}
	
	if(canonicalSphereNode == NULL) {
		SetError(commandResult, "Could not allocated sphere-scenegraph node");
		return false;
	}
	
	bool beginRenderOK = canonicalSphereNode->beginRender();
	if(!beginRenderOK) {
		NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
		commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
		commandResult.setParamVector(scenegraphCtxtError->getParamVector());
		delete canonicalSphereNode;
		canonicalSphereNode = NULL;
		return false;
	}
	
	drawOpenGLCanonicalSphere();
	
	bool const ok = (commandResult.getResult() == (int) NX_CMD_SUCCESS);
	if(!ok) {
		delete canonicalSphereNode;
		canonicalSphereNode = NULL;
		return false;
	}
	
	bool endRenderOK = canonicalSphereNode->endRender();
	if(!endRenderOK) {
		NXCommandResult *scenegraphCtxtError =
			NXSGOpenGLNode::GetCommandResult();
		commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
		commandResult.setParamVector(scenegraphCtxtError->getParamVector());
		delete canonicalSphereNode;
		canonicalSphereNode = NULL;
		return false;
	}
	
	return true;
}

// .............................................................................

/// Issues OpenGL commands to draw a sphere
void NXBallAndStickOpenGLRenderer::drawOpenGLCanonicalSphere(void)
{
	const double r = 1.0; /* radius */
	double theta, rSinTheta, phi, sinPhi, cosPhi;
	double theta2, rSinTheta2;
	GLint iTheta, iPhi;
	GLdouble x,y,z,z1,z2;
	
	const int ALPHA = 5;
	
    /* Automatic normalization of normals */
	GUARDED_GL_OP(glEnable(GL_NORMALIZE));
	
    /* Top cap - draw triangles instead of quads */
	GUARDED_GL_OP(glBegin(GL_TRIANGLE_FAN));
    /* Top pole */
	GUARDED_GL_OP(glNormal3d(0,0,1));
	GUARDED_GL_OP(glVertex3d(0,0,r));
	theta = ALPHA * M_PI/180.0;
	rSinTheta = r*sin(theta);
	z = r*cos(theta);
	
	for(iPhi = 0; iPhi <= 360; iPhi += ALPHA) {
		phi = M_PI/180.0 * (GLdouble) iPhi;
		x = rSinTheta*cos(phi);
		y = rSinTheta*sin(phi);
        /* normal to point on sphere is ray from center to point */
		GUARDED_GL_OP(glNormal3d(x, y, z));
		GUARDED_GL_OP(glVertex3d(x, y, z));
	}
	GUARDED_GL_OP(glEnd());
	
    /* Sphere body - draw quad strips */
	for(iTheta = ALPHA; iTheta <= 180-(2*ALPHA); iTheta += ALPHA) {
		theta = M_PI/180.0 * (double) iTheta;
		theta2 = M_PI/180.0 * (double) (iTheta+10);
		z1 = (GLdouble) (r*cos(theta));
		z2 = (GLdouble) (r*cos(theta2));
		rSinTheta = r*sin(theta);
		rSinTheta2 = r*sin(theta2);
		GUARDED_GL_OP(glBegin(GL_QUAD_STRIP));
		for(iPhi = 0; iPhi <= 360; iPhi += 10) {
			phi = M_PI/180.00 * (double)(iPhi);
			cosPhi = cos(phi);
			sinPhi = sin(phi);
			x = (GLdouble) (rSinTheta*cosPhi);
			y = (GLdouble) (rSinTheta*sinPhi);
			GUARDED_GL_OP(glNormal3d(x, y, z1));
			GUARDED_GL_OP(glVertex3d(x, y, z1));
			x = (GLdouble) (rSinTheta2*cosPhi);
			y = (GLdouble) (rSinTheta2*sinPhi);
			GUARDED_GL_OP(glNormal3d(x, y, z2));
			GUARDED_GL_OP(glVertex3d(x, y, z2));
		}
		GUARDED_GL_OP(glEnd());
	}
	
    /* Bottom cap - draw triangle fan */
	iTheta = 180-ALPHA;
	theta = M_PI/180.0 * (GLdouble) iTheta;
	z = r*cos(theta);
	rSinTheta = r*sin(theta);
	GUARDED_GL_OP(glBegin(GL_TRIANGLE_FAN));
    /* Bottom pole */
	GUARDED_GL_OP(glNormal3d(0,0,-1));
	GUARDED_GL_OP(glVertex3d(0,0,-r));
	for(iPhi = 0; iPhi <= 360; iPhi += ALPHA) {
		phi = M_PI/180.0 * (GLdouble) iPhi;
		x = rSinTheta*cos(phi);
		y = rSinTheta*sin(phi);
		GUARDED_GL_OP(glNormal3d(x, y, z));
		GUARDED_GL_OP(glVertex3d(x, y, z));
	}
	GUARDED_GL_OP(glEnd());
	
	
	ostringstream errMsgStream;
	GLenum const err = GLERROR(errMsgStream);
	if(err == GL_NO_ERROR) {
		commandResult.setResult(NX_CMD_SUCCESS);
	}
	else {
		SetError(commandResult,
		         ("Error drawing openGL unit sphere"+errMsgStream.str()).c_str());
	}
}

// .............................................................................

/// Encapsulates an OpenGL display list for rendering a unit cylinder with axis
/// along the z-axis, one cap on the z=0 plane and the other on the z=1 plane,
/// and sets canonicalCylinderNode to point to it.
/// Returns true if successful. Upon failure, it deallocates any resources 
/// claimed, sets canonicalCylinderNode to NULL and returns false.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalCylinderNode(void)
{
	// quick return if already initialized
	if(canonicalCylinderNode != NULL)
		return true;
	
	try {
		canonicalCylinderNode = new NXSGOpenGLRenderable;
#ifdef NX_DEBUG
		canonicalCylinderNode->setName("CanonicalCylinder");
#endif
	}
	catch (...) {
        // fail if unable to create for any reason
		canonicalCylinderNode = NULL;
		SetError(commandResult, "Could not allocate canonical cylinder OpenGL "
		         "scenegraph node");
		return false;
	}
	
    // extra check for NULL before performing ops on it
	if(canonicalCylinderNode == NULL) {
        // fail if unable to create for any reason
		canonicalCylinderNode = NULL;
		SetError(commandResult, "Could not allocate canonical cylinder OpenGL "
		         "scenegraph node");
		return false;
	}
	
	bool beginRenderOK = canonicalCylinderNode->beginRender();
	if(!beginRenderOK) {
		NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
		commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
		commandResult.setParamVector(scenegraphCtxtError->getParamVector());
		delete canonicalCylinderNode;
		canonicalCylinderNode = NULL;
		return false;
	}
	
	drawOpenGLCanonicalCylinder();
	
	bool const ok = (commandResult.getResult() == (int) NX_CMD_SUCCESS);
	if(!ok) {
		delete canonicalCylinderNode;
		canonicalCylinderNode = NULL;
		return false;
	}
	
	
	bool endRenderOK = canonicalCylinderNode->endRender();
	if(!endRenderOK) {
		NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
		commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
		commandResult.setParamVector(scenegraphCtxtError->getParamVector());
		delete canonicalCylinderNode;
		canonicalCylinderNode = NULL;
		return false;
	}
	
#ifdef NX_DEBUG
	// cout << "canonicalCylinderNode scenegraph:" << endl;
	// canonicalCylinderNode->writeDotGraph(cout);
#endif
	return true;
}

// .............................................................................

/// Issues OpenGL commands to render a canonical cylinder
void NXBallAndStickOpenGLRenderer::drawOpenGLCanonicalCylinder(void)
{
	int const NUM_FACETS = 72;
	const double DELTA_PHI = 360.0 / (double) NUM_FACETS;
	GLdouble vertex[NUM_FACETS][2]; // store (x,y) values
	double x=0.0, y=0.0;
    // GLdouble const z = 0.5;
	
    // generate vertices
	int iFacet = 0; // counter
	double phi = 0.0;
	for(iFacet=0; iFacet<NUM_FACETS; ++iFacet, phi+=DELTA_PHI) {
		double const phi_rad = M_PI/180.0 * phi;
#ifdef _GNU_SOURCE
		sincos(phi_rad, &y, &x);
#else
		x = cos(phi_rad);
		y = sin(phi_rad);
#endif
		vertex[iFacet][0] = (GLdouble)(x);
		vertex[iFacet][1] = (GLdouble)(y);
	}
	
	
    /* Automatic normalization of normals */
	GUARDED_GL_OP(glEnable(GL_NORMALIZE));
	
    /* Fill polygons */
	GUARDED_GL_OP(glShadeModel(GL_SMOOTH));
	GUARDED_GL_OP(glPolygonMode(GL_FRONT, GL_FILL));
	
    /* Top cap - draw triangles instead of quads */
	GUARDED_GL_OP(glBegin(GL_TRIANGLE_FAN));
	GUARDED_GL_OP(glNormal3d(0,0,1));
	GUARDED_GL_OP(glVertex3d(0.0, 0.0, 1.0));
	for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
		GUARDED_GL_OP(glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 1.0));
	}
    // close top-cap
	GUARDED_GL_OP(glVertex3d(vertex[0][0], vertex[0][1], 1.0));
	GUARDED_GL_OP(glEnd());
	
	
    /* Cylinder body - draw triangle strips */
	GUARDED_GL_OP(glBegin(GL_TRIANGLE_STRIP));
	for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
		GUARDED_GL_OP(glNormal3d(vertex[iFacet][0], vertex[iFacet][1], 0.0));
		GUARDED_GL_OP(glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 1.0));
		GUARDED_GL_OP(glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 0.0));
	}
    // close the side surface
	GUARDED_GL_OP(glNormal3d(vertex[0][0], vertex[0][1], 0.0));
	GUARDED_GL_OP(glVertex3d(vertex[0][0], vertex[0][1], 1.0));
	GUARDED_GL_OP(glVertex3d(vertex[0][0], vertex[0][1], 0.0));
	GUARDED_GL_OP(glEnd());
	
	
	
    /* Bottom cap - draw triangle fan */
	GUARDED_GL_OP(glBegin(GL_TRIANGLE_FAN));
	/* Bottom pole */
	GUARDED_GL_OP(glNormal3d(0,0,-1));
	GUARDED_GL_OP(glVertex3d(0.0, 0.0, 0.0));
	for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
		GUARDED_GL_OP(glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 0.0));
	}
    // close bottom-cap
	GUARDED_GL_OP(glVertex3d(vertex[0][0], vertex[0][1], 0.0));
	GUARDED_GL_OP(glEnd());
	
	
	ostringstream errMsgStream;
	GLenum const err = GLERROR(errMsgStream);
	if(err == GL_NO_ERROR) {
		commandResult.setResult(NX_CMD_SUCCESS);
	}
	else {
		SetError(commandResult,
		         ("Error drawing openGL unit cylinder"+errMsgStream.str()).c_str());
	}
}

// .............................................................................

/// Creates scenegraph nodes for different kinds of bonds
bool NXBallAndStickOpenGLRenderer::initializeCanonicalBondNodes(void)
{
	bool success = true;
    success = success && initializeCanonicalSingleBondNode();
	success = success && initializeCanonicalDoubleBondNode();
	success = success && initializeCanonicalTripleBondNode();
	success = success && initializeCanonicalAromaticBondNode();
	success = success && initializeCanonicalCarbomericBondNode();
	success = success && initializeCanonicalGraphiticBondNode();
	return success;	
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a single bond. On success, sets
/// canonicalBondNode[SINGLE_BOND] to point to it and returns true. On failure,
/// releases any resources acquired, sets canonicalBondNode[SINGLE_BOND] to NULL,
/// and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalSingleBondNode(void)
{
    if(canonicalBondNode[SINGLE_BOND] == NULL) {
        try {
            canonicalBondNode[SINGLE_BOND] =
                new NXSGOpenGLScale(BOND_WIDTH, BOND_WIDTH, 1.0);
#ifdef NX_DEBUG
	        canonicalBondNode[SINGLE_BOND]->setName("SingleBond_Scale");
#endif
        }
        catch(...) {
            canonicalBondNode[SINGLE_BOND] = NULL;
	        SetError(commandResult, "Could not allocated single-bond OpenGL "
	                 "scenegraph node");
            return false;
        }
#ifdef NX_DEBUG
	    // canonicalCylinderNode->writeDotGraph(cerr);
#endif
	    assert(canonicalCylinderNode->getNumChildren()==0);
	    assert(canonicalBondNode[SINGLE_BOND]->getNumChildren()==0);
        bool ok =
		    canonicalBondNode[SINGLE_BOND]->addChild(canonicalCylinderNode);
        if(!ok) {
            delete canonicalBondNode[SINGLE_BOND];
            canonicalBondNode[SINGLE_BOND] = NULL;
	        SetError(commandResult, "Allocated single-bond OpenGL scenegraph "
	                 "node but could not parent it");
	        return false;
        }
    }
	return true;
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a double bond. On success, sets
/// canonicalBondNode[DOUBLE_BOND] to point to it and returns true. On failure,
/// releases any resources acquired, sets canonicalBondNode[DOUBLE_BOND] to NULL,
/// and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalDoubleBondNode(void)
{
	bool doubleBondOK = true;
	if(canonicalBondNode[DOUBLE_BOND] == NULL &&
       canonicalBondNode[SINGLE_BOND] != NULL)
    {
        NXSGOpenGLNode *translateNode1 = NULL;
        NXSGOpenGLNode *translateNode2 = NULL;
        try {
            translateNode1 = new NXSGOpenGLTranslate(BOND_WIDTH, 0.0, 0.0);
            translateNode2 = new NXSGOpenGLTranslate(-BOND_WIDTH, 0.0, 0.0);
            canonicalBondNode[DOUBLE_BOND] = new NXSGOpenGLNode;
#ifdef NX_DEBUG
	        canonicalBondNode[DOUBLE_BOND]->setName("DoubleBond");
#endif
        }
        catch(...) {
            doubleBondOK = false;
        }
        if(doubleBondOK) {
            bool ok1 = translateNode1->addChild(canonicalBondNode[SINGLE_BOND]);
            bool ok2 = translateNode2->addChild(canonicalBondNode[SINGLE_BOND]);
            if(ok1 && ok2) {
                bool ok3 = canonicalBondNode[DOUBLE_BOND]->addChild(translateNode1);
                bool ok4 = canonicalBondNode[DOUBLE_BOND]->addChild(translateNode2);
                doubleBondOK = ok3 && ok4;
            }
            else {
                doubleBondOK = false;
            }
        }
        
#ifdef NX_DEBUG
	    translateNode1->setName("DoubleBond_TranslateSingle1");
	    translateNode2->setName("DoubleBond_TranslateSingle2");
#endif
	    
	    // if any of the above steps failed, release partially allocated mem
        if(!doubleBondOK) {
            if(translateNode1 != NULL)
                delete translateNode1;
            if(translateNode2 != NULL)
                delete translateNode2;
            if(canonicalBondNode[DOUBLE_BOND] != NULL) {
                delete canonicalBondNode[DOUBLE_BOND];
                canonicalBondNode[DOUBLE_BOND] = NULL;
            }
        }
    }
	
	return doubleBondOK;
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a triple bond. On success, sets
/// canonicalBondNode[TRIPLE_BOND] to point to it and returns true. On failure,
/// releases any resources acquired, sets canonicalBondNode[TRIPLE_BOND] to NULL,
/// and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalTripleBondNode(void)
{
	bool tripleBondOK = true;
	
	if(canonicalBondNode[TRIPLE_BOND] == NULL &&
       canonicalBondNode[DOUBLE_BOND] != NULL &&
       canonicalBondNode[SINGLE_BOND] != NULL)
    {
        NXSGOpenGLNode *translateNode1 = NULL;
        NXSGOpenGLNode *translateNode2 = NULL;
        try {
            translateNode1 = new NXSGOpenGLTranslate(1.5*BOND_WIDTH, 0.0, 0.0);
            translateNode2 =
		        new NXSGOpenGLTranslate(1.5*(-BOND_WIDTH), 0.0, 0.0);
            canonicalBondNode[TRIPLE_BOND] = new NXSGOpenGLNode;
#ifdef NX_DEBUG
	        canonicalBondNode[TRIPLE_BOND]->setName("TripleBond_Group");
	        translateNode1->setName("TripleBond_TranslateSingle1");
	        translateNode2->setName("TripleBond_TranslateSingle2");
#endif
        }
        catch(...) {
            tripleBondOK = false;
        }
        if(tripleBondOK) {
            bool ok1 = translateNode1->addChild(canonicalBondNode[SINGLE_BOND]);
            bool ok2 = translateNode2->addChild(canonicalBondNode[SINGLE_BOND]);
            if(ok1 && ok2) {
                bool ok3 =
		            canonicalBondNode[TRIPLE_BOND]->addChild(translateNode1);
                bool ok4 =
		            canonicalBondNode[TRIPLE_BOND]->addChild(translateNode2);
                bool ok5 =
                    canonicalBondNode[TRIPLE_BOND]->
		            addChild(canonicalBondNode[SINGLE_BOND]);
                tripleBondOK = ok3 && ok4 && ok5;
            }
            else {
                tripleBondOK = false;
            }
        }
        
	    // if any of the above steps failed, release partially allocated mem
        if(!tripleBondOK) {
            if(translateNode1 != NULL)
                delete translateNode1;
            if(translateNode2 != NULL)
                delete translateNode2;
            if(canonicalBondNode[TRIPLE_BOND] != NULL) {
                delete canonicalBondNode[TRIPLE_BOND];
                canonicalBondNode[TRIPLE_BOND] = NULL;
            }
        }
    }
	
	return tripleBondOK;
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a aromatic bond. On success, sets
/// canonicalBondNode[AROMATIC_BOND] to point to it and returns true. On failure,
/// releases any resources acquired, sets canonicalBondNode[AROMATIC_BOND] to
/// NULL, and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalAromaticBondNode(void)
{
    /// @todo check NE-1 for aromatic bond representation and implement
    /// ref. bond_drawer.py
        
	bool success = true;
    try {
        canonicalBondNode[AROMATIC_BOND] = new NXSGOpenGLNode;
#ifdef NX_DEBUG
	    canonicalBondNode[AROMATIC_BOND]->setName("AromaticBond");
#endif
	    if(!canonicalBondNode[AROMATIC_BOND]->
           addChild(canonicalBondNode[SINGLE_BOND]))
        {
            delete canonicalBondNode[AROMATIC_BOND];
            canonicalBondNode[AROMATIC_BOND] = NULL;
        }
    }
    catch(...) {
	    success = false;
	    SetError(commandResult, "Failed to allocate or parent aromatic bond "
	             "OpenGL scenegraph node");
	    guarded_delete(canonicalBondNode[AROMATIC_BOND]);
    }
	return success;
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a carbomeric bond. On success, sets
/// canonicalBondNode[CARBOMERIC_BOND] to point to it and returns true. On
/// failure, releases any resources acquired, sets
/// canonicalBondNode[CARBOMERIC_BOND] to NULL, and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalCarbomericBondNode(void)
{
    /// @todo check NE-1 for carbomeric bond representation and implement
    /// ref. bond_drawer.py
        
	bool success = true;
    try {
        canonicalBondNode[CARBOMERIC_BOND] = new NXSGOpenGLNode;
#ifdef NX_DEBUG
	    canonicalBondNode[CARBOMERIC_BOND]->setName("CarbomericBond");
#endif
	    if(!canonicalBondNode[CARBOMERIC_BOND]->
           addChild(canonicalBondNode[SINGLE_BOND]))
        {
            delete canonicalBondNode[CARBOMERIC_BOND];
            canonicalBondNode[CARBOMERIC_BOND] = NULL;
        }
    }
    catch(...) {
	    success = false;
	    SetError(commandResult, "Failed to allocate or parent carbomeric bond "
	             "OpenGL scenegraph node");
	    guarded_delete(canonicalBondNode[CARBOMERIC_BOND]);
    }
	return success;
}

// .............................................................................

/// Creates an OpenGL scenegraph node for a graphitic bond. On success, sets
/// canonicalBondNode[GRAPHITIC_BOND] to point to it and returns true. On
/// failure, releases any resources acquired, sets
/// canonicalBondNode[GRAPHITIC_BOND] to NULL, and returns true.
bool NXBallAndStickOpenGLRenderer::initializeCanonicalGraphiticBondNode(void)
{
    /// @todo check NE-1 for graphitic bond representation and implement
    /// ref. bond_drawer.py
        
	bool success = true;
    try {
        canonicalBondNode[GRAPHITIC_BOND] = new NXSGOpenGLNode;
#ifdef NX_DEBUG
	    canonicalBondNode[GRAPHITIC_BOND]->setName("GraphiticBond");
#endif
        if(!canonicalBondNode[GRAPHITIC_BOND]->
           addChild(canonicalBondNode[SINGLE_BOND]))
        {
            delete canonicalBondNode[GRAPHITIC_BOND];
            canonicalBondNode[GRAPHITIC_BOND] = NULL;
        }
    }
    catch(...) {
	    success = false;
	    SetError(commandResult, "Failed to allocate or parent graphitic bond "
	             "OpenGL scenegraph node");
	    guarded_delete(canonicalBondNode[GRAPHITIC_BOND]);
    }
	return success;
}

// .............................................................................

/// Release (partially-) allocated resources if initialized. Afterwards,
/// set the initialized flag to false.
NXCommandResult const *const NXBallAndStickOpenGLRenderer::cleanup(void)
{
	NXRendererPlugin::ClearResult(commandResult);
	if(initialized) {
		// guarded_delete(canonicalSphereNode);
		// guarded_delete(canonicalCylinderNode);
		
		/// @note no need to delete bond pointers because bond-guards will
		/// delete them when they get destructed. The single-bond node is 
		/// heavily referenced by all other bond-nodes and therefore it alone
		/// will have a ref-count > 1. All other should have a ref-count == 1
		for(int bondType = (int)GRAPHITIC_BOND;
		    bondType > (int)SINGLE_BOND;
		    --bondType)
		{
			// guarded_delete(canonicalBondNode[bondType]);
			assert(canonicalBondNode[bondType]->getRefCount() == 1);
		}
		initialized = false;
	}
	return &commandResult;
}

// .............................................................................

/// It is assumed that the plugin was initialized successfully and that the
/// developer has trapped any errors
NXSGOpenGLNode*
    NXBallAndStickOpenGLRenderer::renderAtom(NXAtomData const& info)
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
    
	NXSGOpenGLScale *atomScaleNode;
	try {
		int atomicNum = info.getAtomicNum();
		// cerr << "NXBallAndStickOpenGLRenderer: rendering atomicNum = " << atomicNum << endl;
		double radius = atomicRadiusMap[atomicNum] * 0.25;
		atomScaleNode = new NXSGOpenGLScale(radius, radius, radius);
	}
	catch (...) {
		SetError(commandResult, "Could not create node for rendering atom");
		return NULL;
	} // fail silently
	
	if(!atomNode->addChild(atomScaleNode)) {
		SetError(commandResult,
		         "Created scenegraph node for atom but could not scale it");
		delete atomNode;
		return NULL;
	}
	
    if(!atomScaleNode->addChild(canonicalSphereNode)) {
        SetError(commandResult,
                 "Created scenegraph node for atom but could not include it");
        delete atomNode;
        return NULL;
    }
    
    return atomNode;
}

// .............................................................................

NXSGOpenGLNode*
	NXBallAndStickOpenGLRenderer::renderBond(NXBondData const& info)
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
	    double const bondLength = info.getLength();
	    // cerr << "bond-length = " << bondLength << endl;
        bondScale = new NXSGOpenGLScale(0.25, 0.25, bondLength);
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
    if(!bondScale->addChild(canonicalBondNode[info.getOrder()-1])) {
        SetError(commandResult,
                 "Error including canonical bond node in bond scenegraph");
        delete bondNode;
        return NULL;
    }
    return bondNode;
}

// .............................................................................
#if 0
/// @fixme r1.0.0 hacks
	// -- begin hacks --
NXSGOpenGLNode* NXBallAndStickOpenGLRenderer::renderDnaSegment(/*TODO*/)
{
	/// @todo implement
}
#endif
// .............................................................................

#if 0
NXSGOpenGLNode* NXBallAndStickOpenGLRenderer::renderDnaStrand(/*TODO*/)
{
	/// @todo implement
}
#endif

// -- end hacks --


Q_EXPORT_PLUGIN2(NXBallAndStickOpenGLRenderer, NXBallAndStickOpenGLRenderer)
