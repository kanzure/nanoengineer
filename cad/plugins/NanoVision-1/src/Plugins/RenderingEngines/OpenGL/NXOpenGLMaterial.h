// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLMATERIAL_H
#define NX_OPENGLMATERIAL_H

/* CLASS: NXOpenGLMaterial */
/**
 * Lightweight OpenGL material information for use in class NXAtomRenderData
 */
struct NXOpenGLMaterial {
    GLenum face;
    GLfloat ambient[4];
    GLfloat diffuse[4];
    GLfloat specular[4];
    GLfloat emission[4];
    GLfloat shininess;
    
    NXOpenGLMaterial(GLenum whichFace = GL_FRONT) {
        face = whichFace;
        ambient[0] = -1.0f;
        diffuse[0] = -1.0f;
        specular[0] = -1.0f;
        emission[0] = -1.0f;
        shininess = 35.0;
    };
    
    ~NXOpenGLMaterial() {}
    
    bool invalid(void) const {
        return ((face != GL_FRONT &&
                 face != GL_BACK &&
                 face != GL_FRONT_AND_BACK) ||
                ambient[0] < 0.0 ||
                diffuse[0] < 0.0 ||
                specular[0] < 0.0 ||
                emission[0] < 0.0);
    }
    
    bool valid(void) const { return !invalid(); }
};


#endif // NX_OPENGLMATERIAL_H
