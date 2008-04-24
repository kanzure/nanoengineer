// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERER_H
#define NX_BALLANDSTICKOPENGLRENDERER_H

#include <map>
#include <cassert>

extern "C" {
#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif
}

#include "../NXOpenGLRendererPlugin.h"


/* CLASS: NXBallAndStickOpenGLRenderer */
/**
 * Renders atoms and bonds using balls and sticks
 */
class NXBallAndStickOpenGLRenderer : public NXOpenGLRendererPlugin {
	Q_OBJECT;
	Q_INTERFACES(NXOpenGLRendererPlugin);
	
public:
	NXBallAndStickOpenGLRenderer(Nanorex::NXRenderingEngine *parent = NULL);
	virtual ~NXBallAndStickOpenGLRenderer();

	Nanorex::NXCommandResult const *const initialize(void);
	Nanorex::NXCommandResult const *const cleanup(void);
    
	Nanorex::NXRendererPlugin* newInstance(Nanorex::NXRenderingEngine *) const;
	
    /// Call plugin to render the atom display list and return the scenegraph node. Returns NULL upon failure.
    /// Must set commandResult to indicate success or failure
	NXSGOpenGLNode* renderAtom(Nanorex::NXAtomData const&);
    
    /// Call plugin to render the atom display list and return the scenegraph node. Returns NULL upon failure.
    /// Must set commandResult to indicate success or failure
	NXSGOpenGLNode* renderBond(Nanorex::NXBondData const&);
    
#if 0
	/// @fixme r1.0.0 hacks
	// -- begin hacks --
	NXSGOpenGLNode* renderDnaSegment(/*TODO*/);
	NXSGOpenGLNode* renderDnaStrand(/*TODO*/);
	// -- end hacks --
#endif
	
private:
    static double const BOND_WIDTH;
    static int const MAX_BONDS = 6;
	
	// The 'guard' scenegraph objects ensure that each scenegraph element has
	// a ref-count of at least one if all scenegraphs using these nodes are
	// constructed properly. This is to ensure that these nodes are available
	// even after a previously constructed scenegraph is deleted. Without these
	// guards, these nodes would be deleted by the last parent node when their
	// reference count becomes zero.
	
	// sphere nodes, for atoms
	NXSGOpenGLRenderable *canonicalSphereNode;
	Nanorex::NXSGNode canonicalSphereNodeGuard;
	
	// cylinder nodes, for bonds
	NXSGOpenGLRenderable *canonicalCylinderNode;
	Nanorex::NXSGNode canonicalCylinderNodeGuard;
	
	// bonds
	NXSGOpenGLNode *canonicalBondNode[MAX_BONDS];
	Nanorex::NXSGNode canonicalBondNodeGuard[MAX_BONDS];
    
	std::map<int,double> atomicRadiusMap;
	
	// initialization helpers
	void initializeAtomicRadiusMap(void);
	bool initializeCanonicalGeometryNodes(void);
	bool initializeCanonicalSphereNode(void);
	void drawOpenGLCanonicalSphere(void);
	bool initializeCanonicalCylinderNode(void);
	void drawOpenGLCanonicalCylinder(void);
    bool initializeCanonicalBondNodes(void);
    bool initializeCanonicalSingleBondNode(void);
    bool initializeCanonicalDoubleBondNode(void);
    bool initializeCanonicalTripleBondNode(void);
    bool initializeCanonicalAromaticBondNode(void);
    bool initializeCanonicalCarbomericBondNode(void);
    bool initializeCanonicalGraphiticBondNode(void);
    
    friend class NXBallAndStickOpenGLRendererTest;
};

#endif // NX_BALLANDSTICKOPENGLRENDERER_H
