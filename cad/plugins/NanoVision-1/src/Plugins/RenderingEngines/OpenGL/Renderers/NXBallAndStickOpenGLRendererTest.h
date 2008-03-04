// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERERTEST_H
#define NX_BALLANDSTICKOPENGLRENDERERTEST_H

#include <QtGui>
#include <QtOpenGL>

#include "glt_color.h"
#include "glt_vector4.h"

#include "Nanorex/Interface/NXAtomRenderData.h"
#include "Nanorex/Interface/NXTrackball.h"
#include "NXBallAndStickOpenGLRenderer.h"

using namespace Nanorex;

class TestMainWindow : public QGLWidget {
public:
    TestMainWindow(QWidget *parent=0);
    ~TestMainWindow(void);
    
    void setAtomRenderData(NXAtomRenderData const& theAtomRenderData);
    void setBondRenderData(NXBondRenderData const& theBondRenderData);
    
    void setupScene(void);
    
    // void setBondRenderData(NXBondRenderData const& theBondRenderData)
    // { bondRenderData = theBondRenderData; }
    
    // override QGLWidget:: virtual methods
    void initializeGL(void);
    void paintGL(void);
    void resizeGL(int w, int h);
    
    // trap keyboard events
    void keyPressEvent(QKeyEvent *keyEvent);
    // mouse events
    void mousePressEvent(QMouseEvent *mouseEvent);
    void mouseMoveEvent(QMouseEvent *mouseEvent);
    // void mouseReleaseEvent(QMouseEvent *mouseEvent);
    
    NXOpenGLMaterial const& getDefaultAtomMaterial(void) const
    { return defaultAtomMaterial; }
    
    NXOpenGLMaterial const& getDefaultBondMaterial(void) const
    { return defaultBondMaterial; }
    
private:
    NXAtomRenderData atomRenderData;
    NXBondRenderData bondRenderData;
    
    NXBallAndStickOpenGLRenderer *renderer;
    NXSGOpenGLNode *scene;
    
#ifndef NO_GLT // using GLT
    Vector4 position;
    Vector dir;
    GltColor diffuse;
    GltColor specular;
    GltColor mat_specular;
    real mat_shininess;
#else
    GLfloat position[4];
    GLfloat dir[3];
    GLfloat diffuse[4];
    GLfloat specular[4];
    GLfloat mat_specular[4];
    GLfloat mat_shininess;
#endif
    
    NXOpenGLMaterial defaultAtomMaterial;
    NXOpenGLMaterial defaultBondMaterial;
    
    NXTrackball trackball;
    
    // mouse manipulation
    QPoint lastMouseClick;
    Qt::MouseButton lastMouseButton;
    GLdouble modelview_matrix[16];
    GLdouble projection_matrix[16];
    GLint viewport[4];
    GLdouble angleDegrees;
    Vector axis;
    
    void setupDefaultMaterials(void);
};


#endif // NX_BALLANDSTICKOPENGLRENDERERTEST_H
