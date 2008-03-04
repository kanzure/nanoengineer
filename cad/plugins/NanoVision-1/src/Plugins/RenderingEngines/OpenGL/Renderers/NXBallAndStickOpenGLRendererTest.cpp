// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <QApplication>
#include <iostream>
#include <cassert>
#include <cmath>

#include "glt_vector3.h"
#include "NXBallAndStickOpenGLRendererTest.h"

// #define NO_GLT

using namespace std;

TestMainWindow::TestMainWindow(QWidget *parent)
: QGLWidget(parent),
atomRenderData(0),
bondRenderData(0, 0.0),
renderer(NULL),
scene(NULL)
#ifndef NO_GLT
,
position(0.0, 0.0, 2.0, 1.0),
dir(0.0, 0.0, -1.0),
diffuse(0.5, 0.7, 0.7, 1.0),
specular(0.0, 0.8, 0.0, 1.0),
mat_specular(0.7, 1.0, 0.4, 1.0),
mat_shininess(50.0)
#endif
{
    renderer = new NXBallAndStickOpenGLRenderer;
    // keyboard focus policy
    setFocusPolicy(Qt::ClickFocus);
    setMouseTracking(false);
    setupDefaultMaterials();
}


TestMainWindow::~TestMainWindow()
{
    makeCurrent();
    if(renderer != NULL) {
        renderer->cleanup();
        delete renderer;
        renderer = NULL;
    }
}


void TestMainWindow::keyPressEvent(QKeyEvent *keyEvent)
{
    switch(keyEvent->key()) {
    case Qt::Key_X:
        makeCurrent();
        glMatrixMode(GL_MODELVIEW);
        if(keyEvent->modifiers() && Qt::AltModifier) {
            glRotated(-5.0, 1.0, 0.0, 0.0);
            updateGL();
        }
        else {
            glRotated(5.0, 1.0, 0.0, 0.0);
            updateGL();
        }
        break;
    case Qt::Key_Q:
        close();
        break;
    default:
        keyEvent->ignore();
        break;
    }
}


void TestMainWindow::mousePressEvent(QMouseEvent *mouseEvent)
{
    lastMouseClick = mouseEvent->globalPos();
/*    cerr << "mouse @ (" << lastMouseClick.x() << ','
        << lastMouseClick.y() << ')' << endl;*/
    lastMouseButton = mouseEvent->button();
    trackball.setMouseSpeedDuringRotation(0.001);
    switch(lastMouseButton) {
    // rotations
    case Qt::MidButton:
        makeCurrent();
        trackball.start(lastMouseClick.x(), lastMouseClick.y());
        glGetDoublev(GL_MODELVIEW_MATRIX, modelview_matrix);
        glGetDoublev(GL_PROJECTION_MATRIX, projection_matrix);
        glGetIntegerv(GL_VIEWPORT, viewport);
        break;
    // panning
    case Qt::LeftButton:
        makeCurrent();
        glGetDoublev(GL_MODELVIEW_MATRIX, modelview_matrix);
        glGetDoublev(GL_PROJECTION_MATRIX, projection_matrix);
        glGetIntegerv(GL_VIEWPORT, viewport);
        break;
    // ignore
    default:
        mouseEvent->ignore();
        break;
    }
}


void TestMainWindow::mouseMoveEvent(QMouseEvent *mouseEvent)
{
    QPoint thisMouseClick = mouseEvent->globalPos();
/*    cerr << "mouse @ (" << thisMouseClick.x() << ','
        << thisMouseClick.y() << ')' << endl;*/
    
    switch(lastMouseButton) {
    // rotations
    case Qt::MidButton:
        {
            trackball.update(thisMouseClick.x(), thisMouseClick.y());
            makeCurrent();
#if 0
            GLdouble objX1, objY1, objZ1, objX2, objY2, objZ2;
            gluUnProject((GLdouble) lastMouseClick.x(),
                         (GLdouble) (height()-lastMouseClick.y()),
                         0.0,
                         modelview_matrix,
                         projection_matrix,
                         viewport,
                         &objX1, &objY1, &objZ1);
            gluUnProject((GLdouble) thisMouseClick.x(),
                         (GLdouble) (height()-thisMouseClick.y()),
                         0.0,
                         modelview_matrix,
                         projection_matrix,
                         viewport,
                         &objX2, &objY2, &objZ2);
            Vector wpt1(objX1, objY1, objZ1); wpt1.normalize();
            Vector wpt2(objX2, objY2, objZ2); wpt2.normalize();
#endif
            Vector wpt1(trackball.getOldMouse()); wpt1.normalize();
            Vector wpt2(trackball.getNewMouse()); wpt2.normalize();
            angleDegrees = (wpt1 * wpt2) * 180.0/M_PI;
            axis = xProduct(wpt1, wpt2);
/*            cerr << "glRotated(" << angleDegrees << ','
                << axis[0] << ',' << axis[1] << ',' << axis[2] << ')' << endl;*/
            glMatrixMode(GL_MODELVIEW);
            glLoadMatrixd(modelview_matrix);
            glRotated(angleDegrees, axis.x(), axis.y(), axis.z());
            updateGL();
        }
        break;
    // panning
    case Qt::LeftButton:
        {
            makeCurrent();
            GLdouble objX1, objY1, objZ1, objX2, objY2, objZ2;
            gluUnProject((GLdouble) lastMouseClick.x(),
                         (GLdouble) (height()-lastMouseClick.y()),
                         0.0,
                         modelview_matrix,
                         projection_matrix,
                         viewport,
                         &objX1, &objY1, &objZ1);
            gluUnProject((GLdouble) thisMouseClick.x(),
                         (GLdouble) (height()-thisMouseClick.y()),
                         0.0,
                         modelview_matrix,
                         projection_matrix,
                         viewport,
                         &objX2, &objY2, &objZ2);
            Vector delta(objX2-objX1, objY2-objY1, objZ2-objZ1);
            glMatrixMode(GL_MODELVIEW);
            glLoadMatrixd(modelview_matrix);
            double const SCALE = 10;
            glTranslated(SCALE*delta.x(), SCALE*delta.y(), SCALE*delta.z());
            updateGL();
        }
        break;
    default:
        mouseEvent->ignore();
        break;
    }
}


#if 0
void TestMainWindow::mouseReleaseEvent(QMouseEvent *mouseEvent)
{
    switch(lastMouseButton) {
    case Qt::MidButton:
        glMatrixMode(GL_MODELVIEW);
        glLoadMatrixd(modelview_matrix);
        glRotated(angleDegrees, axis.x(), axis.y(), axis.z());
        updateGL();
        break;
    default:
        mouseEvent->ignore();
        break;
    }
}
#endif


void TestMainWindow::setupDefaultMaterials(void)
{
    defaultAtomMaterial.ambient[0] = defaultBondMaterial.ambient[0] = 0.0;
    defaultAtomMaterial.ambient[1] = defaultBondMaterial.ambient[1] = 0.0;
    defaultAtomMaterial.ambient[2] = defaultBondMaterial.ambient[2] = 0.0;
    defaultAtomMaterial.ambient[3] = defaultBondMaterial.ambient[3] = 0.0;
    
    mat_shininess = 50.0;
    
    defaultAtomMaterial.emission[0] = defaultBondMaterial.emission[0] = 0.0;
    defaultAtomMaterial.emission[1] = defaultBondMaterial.emission[1] = 0.0;
    defaultAtomMaterial.emission[2] = defaultBondMaterial.emission[2] = 0.0;
    defaultAtomMaterial.emission[3] = defaultBondMaterial.emission[3] = 0.0;
    
#ifdef NO_GLT
    position[0] = 0.0;
    position[1] = 0.0;
    position[2] = 2.0;
    position[3] = 1.0;
    dir[0] = 0.0;
    dir[1] = 0.0;
    dir[2] = -1.0;
    defaultAtomMaterial.diffuse[0] = diffuse[0] = 0.5;
    defaultAtomMaterial.diffuse[0] = diffuse[1] = 0.7;
    defaultAtomMaterial.diffuse[0] = diffuse[2] = 0.7;
    defaultAtomMaterial.diffuse[0] = diffuse[3] = 1.0;
    specular[0] = 0.0;
    specular[1] = 0.8;
    specular[2] = 0.0;
    specular[3] = 1.0;
    defaultAtomMaterial.specular[0] = mat_specular[0] = 0.7;
    defaultAtomMaterial.specular[1] = mat_specular[1] = 1.0;
    defaultAtomMaterial.specular[2] = mat_specular[2] = 0.4;
    defaultAtomMaterial.specular[3] = mat_specular[3] = 1.0;

#else // using GLT
    
    defaultAtomMaterial.diffuse[0] = diffuse.red();
    defaultAtomMaterial.diffuse[1] = diffuse.green();
    defaultAtomMaterial.diffuse[2] = diffuse.blue();
    defaultAtomMaterial.diffuse[3] = diffuse.alpha();
    
    defaultAtomMaterial.specular[0] = mat_specular.red();
    defaultAtomMaterial.specular[1] = mat_specular.green();
    defaultAtomMaterial.specular[2] = mat_specular.blue();
    defaultAtomMaterial.specular[3] = mat_specular.alpha();
    
    defaultAtomMaterial.shininess = mat_shininess;
#endif
    
    defaultBondMaterial.diffuse[0] = defaultAtomMaterial.specular[0];
    defaultBondMaterial.diffuse[1] = defaultAtomMaterial.specular[1];
    defaultBondMaterial.diffuse[2] = defaultAtomMaterial.specular[2];
    defaultBondMaterial.diffuse[3] = defaultAtomMaterial.specular[3];

    defaultBondMaterial.specular[0] = defaultAtomMaterial.diffuse[0];
    defaultBondMaterial.specular[1] = defaultAtomMaterial.diffuse[1];
    defaultBondMaterial.specular[2] = defaultAtomMaterial.diffuse[2];
    defaultBondMaterial.specular[3] = defaultAtomMaterial.diffuse[3];
}

void TestMainWindow::setAtomRenderData(NXAtomRenderData const& theAtomRenderData)
{
    atomRenderData = theAtomRenderData;
}


void TestMainWindow::setBondRenderData(NXBondRenderData const& theBondRenderData)
{
    bondRenderData = theBondRenderData;
}


void TestMainWindow::setupScene(void)
{
    makeCurrent();
    
    // create sample atom render data
    NXAtomRenderData H_renderData(1);
    NXOpenGLMaterial const& defaultAtomMaterial =
        getDefaultAtomMaterial();
    H_renderData.addData((void*) &defaultAtomMaterial);
    setAtomRenderData(H_renderData);
    
    // create sample bond render data
    NXBondRenderData H_bond_renderData(3, 1.0);
    NXOpenGLMaterial const& defaultBondMaterial =
        getDefaultBondMaterial();
    H_bond_renderData.addData((void*) &defaultBondMaterial);
    setBondRenderData(H_bond_renderData);
    
    if(scene != NULL) {
        delete scene;
        scene = NULL;
    }
    scene = new NXSGOpenGLNode;
    NXSGOpenGLNode *atom1 = renderer->renderAtom(atomRenderData);
    NXSGOpenGLNode *atom1Move = new NXSGOpenGLTranslate(0.0f, 1.0f, 1.0f);
    NXSGOpenGLNode *atom2 = renderer->renderAtom(atomRenderData);
    NXSGOpenGLNode *atom2Move = new NXSGOpenGLTranslate(0.0f, -1.0f, -1.0f);
    bool nodesCreated = (scene != NULL &&
                         atom1 != NULL && atom1Move != NULL &&
                         atom2 != NULL && atom2Move != NULL );
    bool addedChildren = true;
    if(nodesCreated) {
        addedChildren = scene->addChild(atom1Move);
        addedChildren = addedChildren && atom1Move->addChild(atom1);
        addedChildren = addedChildren && scene->addChild(atom2Move);
        addedChildren = addedChildren && atom2Move->addChild(atom2);
    }
    else {
        cerr << "scene: Failed to create nodes" << endl;
    }
    if(!addedChildren) {
        cerr << "scene: Failed to add children" << endl;
        return;
    }
    NXSGOpenGLNode *bond12 = renderer->renderBond(bondRenderData);
    GLfloat const BOND_WIDTH = 0.25f;
    NXSGOpenGLNode *bond12Rotate = new NXSGOpenGLRotate(-45.0, 1.0, 0.0, 0.0);
    if(bond12 != NULL && bond12Rotate != NULL) {
        scene->addChild(bond12Rotate);
        bond12Rotate->addChild(bond12);
    }
    else {
        cerr << "scene: Failed to create bond nodes" << endl;
    }
}


void TestMainWindow::initializeGL(void)
{
#ifdef NO_GLT
/*    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse);
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, &mat_shininess);*/
    
    // *** broken ***
    glLightfv(GL_LIGHT0, GL_POSITION, position);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular);
    
#else
    
/*    diffuse.glMaterial(GL_FRONT, GL_DIFFUSE);
    mat_specular.glMaterial(GL_FRONT, GL_SPECULAR);
    GLfloat shininess = mat_shininess;
    glMaterialfv(GL_FRONT, GL_SHININESS, &shininess);*/
    
/*    GLfloat position_data[4];
    position_data[0] = position.x();
    position_data[1] = position.y();
    position_data[2] = position.z();
    position_data[3] = position.w();
    glLightfv(GL_LIGHT0, GL_POSITION, position_data);
    */
    position.glLight(GL_LIGHT0, GL_POSITION);
    diffuse.glLight(GL_LIGHT0, GL_DIFFUSE);
    specular.glLight(GL_LIGHT0, GL_SPECULAR);
#endif
    
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE);
    
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    glEnable(GL_DEPTH_TEST);
  
    /* Background colour */
    glClearColor(0.0, 0.0, 0.0, 1.0);
    
    /* Initial camera location and orientation */
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(-4, -2, 3, 0, 0, 0, 0, 1, 0);
    
    renderer->initialize();
    setupScene();
}


void TestMainWindow::paintGL(void)
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    if(scene != NULL) {
/*        cerr << "scene display list id = "
            << reinterpret_cast<NXSGOpenGLRenderable*>(scene)->getDisplayListID()
            << endl;*/
        assert(scene->applyRecursive());
    }
    else {
        glBegin(GL_QUADS);
        glVertex3f(-1.0f, -1.0f, 0.0f);
        glVertex3f( 1.0f, -1.0f, 0.0f);
        glVertex3f( 1.0f,  1.0f, 0.0f);
        glVertex3f(-1.0f,  1.0f, 0.0f);
        glEnd();
    }
    
    /* Draw the canonical axes */
    /* Note: got to disable lighting calculations here otherwise
    *       we won't see the colours we've requested */
    
    glDisable(GL_LIGHTING);
    glLineWidth(2.0);
    glBegin(GL_LINES);
    glColor3f(1.0, 0.3, 0.3);
    glVertex3f(-100,0,0);
    glVertex3f(100,0,0);
    glColor3f(0.3, 1.0, 0.3);
    glVertex3f(0,-100,0);
    glVertex3f(0,100,0);
    glColor3f(0.3, 0.3, 1.0);
    glVertex3f(0,0,-100);
    glVertex3f(0,0,100);
    glEnd();
    glEnable(GL_LIGHTING);
}


void TestMainWindow::resizeGL(int width, int height)
{
    trackball.resize(width, height);
    /* Instruct Open GL to use the whole window for drawing */
    glViewport(0, 0, (GLsizei) width, (GLsizei) height);
    
    /* Set the perspective - later in this course */
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(55, (GLdouble)width/(GLdouble)height, 0.1, 25);
}


int main(int argc, char *argv[])
{
    QApplication testApp(argc, argv);
    TestMainWindow testMainWindow;
    testMainWindow.show();
    
    
    // testApp.setMainWidget(&testMainWindow);
     return testApp.exec();
}
