//#include <SDL/SDL.h>

typedef unsigned char Byte;
typedef unsigned int uint;

#include <GL/glew.h>
#include "CgUtil.h"

//#include <GL/gl.h>
#include <math.h>
//#include <GL/glu.h>

#include <vector>

#include <vcg/space/point3.h>
#include <vcg/space/color4.h>


using namespace vcg;
using namespace std;

#include "CubeMapSamp.h"
#include "OctaMapSamp.h"

#include "Mol.h"
#include "HardSettings.h"
#include "MyCanvas.h"
#include "ShadowMap.h"

bool use_accurate_halo=true;


bool validView(Point3f p){
  if (!hardSettings.doubleSM) return true;
  if (p[0]>0) return true;
  if (p[0]<0) return false;
  
  if (p[1]<0) return true;
  if (p[1]>0) return false;
  
  if (p[2]<0) return true;
  return false;
  
}

extern int CSIZE;  // size for alo patch
extern int BSIZE;  // size for bonds patches

//extern uint shadowFrame, shadowTexture, offsetFrame, haloFrame, haloTexture, finalFrame;
//uint finalFrame=0; // frame dove metto l'immagine finale! 0 se lo schermo.

CgUtil shadowSettings;  
CgUtil shadowSettingsAcc;  

// functions defined later.
static void setMatrices(vcg::Point3f L, int screensize, int screensizeHard, bool sx);
static void restoreMatrices();

static GLint lastviewport[4];


float matSM[4][4];   // matrix used during shadowmmap drawing
float matFinal[4][4];// matrix for FP computation  = matSM x (MV)^(-1) 
float HSratio; // ratio betweenhard and soft shadowbuffer

extern Mol mol;
extern int winx,winy;

// FOR HALOS
void prepareDepthTextureForCurrentViewpoint(){
  
  // Draw depth texture from current viewpoint
  
  haloCanvas.SetSameRes( mainCanvas );
  haloCanvas.SetAsOutput();
  
  if (use_accurate_halo)
    shadowSettingsAcc.BindShaders();
  else 
    shadowSettings.BindShaders();
    
    
  glClear( GL_DEPTH_BUFFER_BIT ) ; 
    
  mol.Draw();

  mainCanvas.SetAsOutput();  
  
  glActiveTextureARB(GL_TEXTURE1_ARB); 
  haloCanvas.SetAsTexture();
  glEnable(GL_TEXTURE_2D); 
  
}

Point3f lastL(0,0,0); // last used light

void ShadowMap::Update(){
  lastL.Zero();
}

void ShadowMap::computeAsTexture(vcg::Point3f L, bool makeboth, MyCanvas &canvas){
  
  if (lastL!=L) {
  
    canvas.SetAsOutput();
      

    setMatrices(L, canvas.GetSoftRes(),canvas.GetHardRes(), true);
    glClearDepth(1);  
    glClear( GL_DEPTH_BUFFER_BIT );
    glDisable(GL_SCISSOR_TEST);
    glDepthFunc(GL_LESS);
    
    m.DrawShadowmap(false);
    restoreMatrices();

    
    if (hardSettings.doubleSM && makeboth) {
      setMatrices(L, canvas.GetSoftRes(), canvas.GetHardRes(), false);
      glClearDepth(-10000);      
      glClear( GL_DEPTH_BUFFER_BIT);
      glDepthFunc(GL_GREATER);

      glDisable(GL_SCISSOR_TEST);

      m.DrawShadowmap(false);

      restoreMatrices();
    }

    glClearDepth(1);  
    glDepthFunc(GL_LESS);

    mainCanvas.SetAsOutput();
  
    lastL=L;
  }
  
  glActiveTextureARB(GL_TEXTURE1_ARB); 
  
  canvas.SetAsTexture();

}


extern ShadowMap shadowmap;
float extractCurrentScaleFactor(float x[4][4]);
float extractCurrentScaleFactor();
//float shadowScaleFactor=1;


void ShadowMap::FeedParameters(){
  for (int i=0; i<3; i++) {
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, i+3, 
      matFinal[0][i],matFinal[1][i],matFinal[2][i],matFinal[3][i]
    );
  }
}

extern CgUtil cgSettings;

/*void DrawTmp(){
  
  cgSettings.BindShaders();
  
  glEnable(GL_TEXTURE_2D);
  //glBindTexture(GL_TEXTURE_2D, molTexture);

  glActiveTextureARB(GL_TEXTURE1_ARB); 
  glBindTexture(GL_TEXTURE_2D, shadowTexture);
  
  shadowmap.m.Draw();
//  shadowmap.m.DrawShadowmap(false);

  
  glDisable(GL_VERTEX_PROGRAM_ARB);
  glDisable(GL_FRAGMENT_PROGRAM_ARB);
  glDisable(GL_BLEND);


  /*glActiveTextureARB(GL_TEXTURE0_ARB);   glDisable(GL_TEXTURE_2D); 
  glActiveTextureARB(GL_TEXTURE1_ARB);   glEnable(GL_TEXTURE_2D); 
  glBindTexture(GL_TEXTURE_2D, shadowTexture);*/
//  glBindTexture(GL_TEXTURE_2D, shadowTexture);

/*  glBegin(GL_QUADS);
  glColor3f(0,0,1);
  float h=-0.25, k=-0.25;
  glTexCoord2f(0,0);  glVertex3d( k, h,0.1);
  glTexCoord2f(1,0);  glVertex3d( k,+1,0.1);
  glTexCoord2f(1,1);  glVertex3d(+1,+1,0.1);
  glTexCoord2f(0,1);  glVertex3d(+1, h,0.1);
  glEnd();

  glActiveTextureARB(GL_TEXTURE1_ARB); glDisable(GL_TEXTURE_2D); 
  glActiveTextureARB(GL_TEXTURE0_ARB); glEnable(GL_TEXTURE_2D); 

  glBegin(GL_QUADS);
  glColor3f(1,1,1);
  glTexCoord2f(0,0);  glVertex3d(k-0.75,h-0.75,0);
  glTexCoord2f(1,0);  glVertex3d(k-0.75,0.25,0);
  glTexCoord2f(1,1);  glVertex3d(0.25,0.25,0);
  glTexCoord2f(0,1);  glVertex3d(0.25,h-0.75,0);
  glEnd();
*/
  /*glActiveTextureARB(GL_TEXTURE1_ARB);  glDisable(GL_TEXTURE_2D); 
  glActiveTextureARB(GL_TEXTURE0_ARB);  glEnable(GL_TEXTURE_2D); */
/*}*/



bool ShadowMap::init(){
  shadowSettings.SetForShadowMap(false);
  shadowSettingsAcc.SetForShadowMap(true);
  
  mainCanvas.RedirectToVideo();
  mainCanvas.SetVideoSize(winx);
  
  
  // test shadow and shadowAO canvases
  shadowmapCanvas.SetRes(hardSettings.SHADOWMAP_SIZE);  
  shadowmapCanvas.ratio2x1=(hardSettings.doubleSM==1);
  if (!shadowmapCanvas.Test() ) return false;
  
  shadowAOCanvas.SetRes(hardSettings.AOSM_SIZE);  
  shadowAOCanvas.ratio2x1=(hardSettings.doubleSM==1);
  //shadowAOCanvas.ratio2x1=(hardSettings.doubleSM==1);
  if (!shadowAOCanvas.Test() ) return false;
  
  mainCanvas.SetAsOutput();
  return true;
}

bool ShadowMap::initHalo(){
  
  // test halo canvases
  haloCanvas.SetSameRes(mainCanvas);
  if (!haloCanvas.Test() ) return false;
  
  
  mainCanvas.SetAsOutput();
  return true;
}


bool AOgpu2::init(){
  if (!moltextureCanvas.Test()) return false;
  mainCanvas.SetAsOutput();
}

float myrand();

static CgUtil aogpu_settings;
static CgUtil aogpustick_settings;

void AOgpu2::Reset(Mol &m){
  moltextureCanvas.SetAsOutput();

  glClearColor(0,0,0,1);
  glClear( GL_COLOR_BUFFER_BIT);
}

void AOgpu2::Bind(){
  moltextureCanvas.SetAsOutput();
}

AOgpu2::AOgpu2( Point3f dir, Mol &m, int ndir){
  
  shadowmap.computeAsTexture(dir, true, shadowAOCanvas );
  glFinish();
  
  moltextureCanvas.SetAsOutput();
  
  glDisable(GL_VERTEX_PROGRAM_ARB);
  glEnable(GL_FRAGMENT_PROGRAM_ARB);

  
  aogpu_settings.BindDrawAOShader();
  for (int i=0; i<3; i++) {
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, i, 
      matSM[0][i],matSM[1][i],matSM[2][i],matSM[3][i]
    );
    //printf("Sending %d (%f %f %f %f)\n", i, mat[0][i],mat[1][i],mat[2][i],mat[3][i]);
  }
  glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 3, dir[0],dir[1],dir[2], 4.0/ndir );
  glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 4, 
      0,stick_radius,0,0
  );

  m.DrawOnTexture();
  
  glDisable(GL_BLEND);
  
  glEnable(GL_VERTEX_PROGRAM_ARB);
  
};

void AOgpu2::UnBind(){
  mainCanvas.SetAsOutput();
};

float myrand(){
  static int k=0;
  k+=1231543214;
  return ((k%12421)/12421.0);
}

void Bond::DrawOnTexture(){
  //glColor3f(myrand(),myrand(),myrand());
  float h=0.0;
  
  float Xm=(-1.0)-1.0/BSIZE;
  float Xp=+1.0+1.0/BSIZE;
  float Ym=Xm, 
        Yp=+1.0+1.0/CSIZE/1.0;
  Point3f tmp=startp^dir;
  startp.Normalize();
  tmp.Normalize();
  glMultiTexCoord3fARB(GL_TEXTURE2_ARB, startp[0],startp[1],startp[2]);
  glMultiTexCoord3fARB(GL_TEXTURE3_ARB, tmp[0],tmp[1],tmp[2] );
  
  glMultiTexCoord3fARB(GL_TEXTURE1_ARB, b[0],b[1],b[2] );
  glTexCoord2f(Xm,Yp); glVertex2f(-h+tx,      -h+ty+CSIZE);
  glTexCoord2f(Xm,Ym); glVertex2f(-h+tx,      -h+ty);
  glMultiTexCoord3fARB(GL_TEXTURE1_ARB, a[0],a[1],a[2] );
  glTexCoord2f(Xp,Ym); glVertex2f(-h+tx+BSIZE,-h+ty);  
  glTexCoord2f(Xp,Yp); glVertex2f(-h+tx+BSIZE,-h+ty+CSIZE);
}

void QAtom::DrawOnTexture(){
  glColor3f(myrand(),myrand(),myrand());
  float h=0.0;
  
  float Xm=(-1.0)-1.0/CSIZE/1.0;
  float Xp=+1.0+1.0/CSIZE/1.0;
  float Ym=Xm, Yp=Xp;
  glMultiTexCoord4fARB(GL_TEXTURE1_ARB, px,py,pz,r );
  glTexCoord2f(Xm,Ym); glVertex2f(-h+tx,      -h+ty);
  glTexCoord2f(Xp,Ym); glVertex2f(-h+tx+CSIZE,-h+ty);
  glTexCoord2f(Xp,Yp); glVertex2f(-h+tx+CSIZE,-h+ty+CSIZE);
  glTexCoord2f(Xm,Yp); glVertex2f(-h+tx,      -h+ty+CSIZE);
}

void Mol::DrawOnTexture(){
  
  
  glEnable(GL_BLEND);
  glBlendFunc(GL_ONE, GL_ONE );
  
  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
  glOrtho(0,moltextureCanvas.GetSoftRes(),0,moltextureCanvas.GetSoftRes(), 0,1);
  
  
  glMatrixMode(GL_MODELVIEW);
  glPushMatrix();
  glLoadIdentity();
  
  
  glGetIntegerv(GL_VIEWPORT, lastviewport);
  glViewport(0,0,moltextureCanvas.GetSoftRes(),moltextureCanvas.GetSoftRes());

  glActiveTextureARB(GL_TEXTURE1_ARB); 
  glDisable(GL_TEXTURE_2D); 
  glActiveTextureARB(GL_TEXTURE0_ARB); 
  glDisable(GL_TEXTURE_2D); 
  
  glBegin(GL_QUADS);
  for (int i=0; i<atom.size(); i++)
  atom[i].DrawOnTexture();
  glEnd();



  
  
  if (sticks) {
    aogpustick_settings.BindDrawAOShaderSticks();
    //glDisable(GL_BLEND);
    //glDisable(GL_FRAGMENT_PROGRAM_ARB);
    glBegin(GL_QUADS);
    for (int i=0; i<bond.size(); i++)  bond[i].DrawOnTexture();
    glEnd();
    //glEnable(GL_FRAGMENT_PROGRAM_ARB);
  }
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
  glPopMatrix();
  glViewport(lastviewport[0],lastviewport[1],lastviewport[2],lastviewport[3]);
};







static void restoreMatrices(){
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
  glPopMatrix();
  glViewport(lastviewport[0],lastviewport[1],lastviewport[2],lastviewport[3]);
}

static void setMatrices(vcg::Point3f L, int screensize, int screensizeHard, bool sx){
  // orthonormal basis
  L.Normalize();
  Point3f ax,ay,az=L;
  ax=az^Point3f(1,0,0);
  if (ax.SquaredNorm()<0.1) ax=az^Point3f(0,1,0);
  ax=ax.Normalize();
  ay=(az^ax).Normalize();

  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
/*  if (!sx) {
    glScalef(1,1,-1);
  }*/

  
	GLfloat nearPlane = 1.0;
	GLfloat farPlane = 201;
  glOrtho(-1,+1,-1,+1, nearPlane, farPlane);

  glMatrixMode(GL_MODELVIEW);
  
  // PREPARE MATRIX for shadow test...
  
  glPushMatrix();
  glLoadIdentity();
  glOrtho(-1,+1,-1,+1, nearPlane, farPlane);
  
  gluLookAt(0,0,-4,   0,0,0,   0,1,0);    
  gluLookAt( az[0],az[1],az[2],  0,0,0, ay[0], ay[1], ay[2] );

  float r=shadowmap.m.r;
  float px=shadowmap.m.px;
  float py=shadowmap.m.py;
  float pz=shadowmap.m.pz;
  glScalef(1/r,1/r,1/r);
  glTranslatef(-px,-py,-pz);
  
  glGetFloatv(GL_MODELVIEW_MATRIX, &(matSM[0][0]));
  
  // ...done!
  
  glLoadIdentity();
  gluLookAt(0,0,-4,   0,0,0,   0,1,0);    
  gluLookAt( az[0],az[1],az[2],  0,0,0, ay[0], ay[1], ay[2] );

  //shadowScaleFactor=extractCurrentScaleFactor()/r;
  
  glGetIntegerv(GL_VIEWPORT, lastviewport);
  
  if (sx) {
    glViewport(0,0,screensize,screensize);
    glEnable(GL_SCISSOR_TEST);
    glScissor(0,0,screensize,screensize);
  }
  else {
    glViewport(screensize,0,screensize,screensize);
    glEnable(GL_SCISSOR_TEST);
    glScissor(screensize,0,screensize,screensize);
  }

  HSratio = float(screensize) / float(screensizeHard) ;
  //for (int i=0; i<4; i++)
  //for (int j=0; j<2; j++) matSM[i][j] /=ratio;
  
}


// quick and dirty
#include <vcg/math/matrix44.h>
void ShadowMap::GetCurrentPVMatrix(){
    
    float matP[16];  
  float matMV[16];  
  
  glGetFloatv(GL_PROJECTION_MATRIX, matP);
  glGetFloatv(GL_MODELVIEW_MATRIX,  matMV);
  
  Matrix44f A(matSM[0]);
  Matrix44f B(matMV);
  Matrix44f C(matP);
  
  A=vcg::Transpose( A );
  B=vcg::Transpose( B );
  C=vcg::Transpose( C );

  Matrix44f P = C*B;
  P=vcg::Invert( P );
  Matrix44f res =  A*P;
  
  Matrix44f mul;
  Matrix44f add;
  
  GLint vp[4];
  glGetIntegerv(GL_VIEWPORT,  vp);
  
  mul.SetScale(Point3f(2.0f/vp[2], 2.0f/vp[3], 2));
  add.SetTranslate(Point3f(-1,-1,-1));
  
  //Matrix44f mulHS;
  //mulHS.SetScale(Point3f(HSratio,HSratio,1) );
  
  res=res*add*mul;

  for (int i=0; i<4; i++) 
  for (int j=0; j<4; j++) 
  matFinal[i][j]=res[j][i];
}
/*
void ShadowMap::GetCurrentPVMatrix(){
  
  computeAxBm1xCm1( &(res[0][0]) , &(A[0][0]) , &(B[0][0]) , &(C[0][0]));
}*/



void test(){

  return;  
  float nf[2];
  glGetFloatv(GL_DEPTH_RANGE,  nf);
  FILE *f=fopen("test.txt","w");
  fprintf(f,"near=%f,far=%f\n\n",nf[0],nf[1]);
  fclose(f);
  
  float mat[16];
  float matP[16];
  
  glGetFloatv(GL_MODELVIEW_MATRIX,  mat);
  glGetFloatv(GL_PROJECTION_MATRIX,  matP);

  
  Matrix44f A(mat);
  A=vcg::Transpose( A );

  Matrix44f B(matP);
  B=vcg::Transpose( B );
  
  A = B*A;
  
  for (int i=0; i<4; i++) 
  for (int j=0; j<4; j++) 
  mat[i*4+j]=A[j][i];

  glMatrixMode(GL_PROJECTION);
  glLoadIdentity(  );
  
  glMatrixMode(GL_MODELVIEW);
  glLoadMatrixf( mat );

  
}
