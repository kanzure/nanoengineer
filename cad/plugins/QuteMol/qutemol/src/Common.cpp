
#include <wx/log.h>

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

#include "gen_normal.h"
#include <wrap/gui/trackball.h>

using namespace vcg;
using namespace std;

#include "CubeMapSamp.h"
#include "OctaMapSamp.h"
#include "Mol.h"
//#include "AOgpu.h"

#include "Common.h"
#include "HardSettings.h"
#include "MyCanvas.h"

#include "ShadowMap.h"

extern CgUtil shadowSettings;  
extern CgUtil shadowSettingsAcc;  

GeoSettings geoSettings; // singleton


extern Mol mol;

double aniStep=-1;

void setAniStep(double step){
  aniStep=step;
}

void stopAni(){
  aniStep=-1;
}


void GeoSettings::Apply(){
   if (mol.IsReady()) {
     if (mode==BALL_N_STICKS) {
       mol.SetBallAndSticks(stickRadius);
     }
     if (mode==LICORICE) {
       mol.SetLicorice(licoRadius);
     }
     if (mode==SPACE_FILL) mol.SetSpaceFill();
   }
   
   cgSettings.setGeoSettings(*this);
   cgSettings.UpdateShaders();
   
   UpdateShadowmap();
   
   mol.ResetAO();
}

void SetColMode(float mode){
  mol.SetColMode(mode);
}

void ResetColMode(){
  float tmp=mol.colMode;
  mol.colMode=-1;
  mol.SetColMode(tmp);
}

float GetColMode(){
  return mol.colMode;
}

void GeoSettings::ApplyColor(){
   cgSettings.setGeoSettings(*this);
   cgSettings.UpdateShaders();
}

using namespace vcg;
using namespace std;


// VIS06 presentaiton modes:
bool draw_balls=true; 
bool draw_sticks=true;
bool draw_wireframe_sticks=false;
bool draw_wireframe_balls=false;

int winx=512,winy=winx;



int CSIZE;  // size (texels) per atom patches
int BSIZE;  // size (texels) per pond patches



vcg::Trackball track;
vcg::Trackball lightTrack;
bool MovingLightMode=false;


Mol mol;
ShadowMap shadowmap(mol);
CgUtil cgSettings;

int GetCurrentHetatm(){
  return mol.nhetatm;
}

int GetCurrentAtm(){
  return mol.natm;
}


//void DrawTmp();

void UpdateShadowmap(){
  ShadowMap::Update();
}


void drawFrame(); // def later...

Byte* GetSnapshot(int sx, int sy, bool alpha){

  static uint textureSnap = 666;
  static  uint frameSnap;
  
  // set offline rendering
  mainCanvas.RedirectToMemory();
  mainCanvas.SetRes(sx);
  //hardsx=mainCanvas.GetHardRes();
  
  if (!mainCanvas.SetAsOutput()) return NULL; 

  drawFrame();
  
  // capture frame
  sx=sy=mainCanvas.GetHardRes();
  Byte* res=new(Byte[sx*sy*4]);
  glReadPixels(0,0,sx,sy,alpha?GL_RGBA:GL_RGB,GL_UNSIGNED_BYTE,res);

  
  mainCanvas.RedirectToVideo();
  mainCanvas.SetAsOutput();

  return res;

}


/*
 * FUNCTION: setProjection
 *
glMatrixMode(GL_PROJECTION);
glLoadIdentity();
gluPerspective(60, float(width())/float(height()), 1, 100);
 */
void setProjection(int res) {
    int winx,winy;
    winx=winy=res; 
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
	GLfloat nearPlane = 0.01;
	GLfloat farPlane = 10000;
	float size=1.2f;
	float ratio=size*(float)winx / winy;
	if (cgSettings.projmode==CgUtil::PERSPECTIVE) {
        // BH: Not the usual case.
        gluPerspective(60.0, ratio, nearPlane, farPlane);
        
    } else {
//    if(winx<winy) glOrtho(-1,+1,-(float)winy / winx,+(float)winy / winx, 1, 201);
//    else glOrtho(-(float)winx / winy,+(float)winx / winy,-1,+1, 1, 201);    
//    if(winx<winy) glOrtho(-size,+size,-ratio,+ratio, 1, 201);
//    else glOrtho(-ratio,+ratio,-size,+size, 1, 201);
        if(winx<winy)
            glOrtho(-1,+1,-(float)winy / winx,+(float)winy / winx, 1, 201);
        else
            glOrtho(-(float)winx / winy,+(float)winx / winy,-1,+1, 40-2, 40+200);    
    }
    
    glViewport(0, 0, winx,winy);
  
    glMatrixMode(GL_MODELVIEW);
}




void MakeHiqualityScreen(int quality){
  int curres=mainCanvas.GetSoftRes();
  
  mainCanvas.RedirectToMemory();
  
  mainCanvas.SetRes(curres * quality / 100 );
  
  if (!mainCanvas.SetAsOutput()) {
    // something went wrong. Fall-back: do a normal screenshot
    mainCanvas.RedirectToVideo();
    mainCanvas.SetAsOutput();
    drawFrame();
    return; 
  }
  
  float HSratio = float(mainCanvas.GetSoftRes()) / mainCanvas.GetHardRes();

  drawFrame();
  
  mainCanvas.RedirectToVideo();
  mainCanvas.SetAsOutput();

  glActiveTextureARB(GL_TEXTURE1_ARB);   
  glDisable(GL_TEXTURE_2D);
  
  glActiveTextureARB(GL_TEXTURE0_ARB);   
  mainCanvas.SetAsTexture();
   
  glDisable(GL_FRAGMENT_PROGRAM_ARB);
  glDisable(GL_VERTEX_PROGRAM_ARB);
  
  setProjection(mainCanvas.GetSoftRes());
  

  glMatrixMode(GL_MODELVIEW);
  //glPushMatrix();
  glLoadIdentity();
    
  //glClearColor(1,1,1,1);
  //glClear(GL_COLOR_BUFFER_BIT);
  
  glEnable(GL_TEXTURE_2D);
  glDisable(GL_DEPTH_TEST);
  
  
  //glColor3f(1,0.75,0.75); // <= TEST HQ
  glColor3f(1,1,1);
  
  float z=-45;
  
  glBegin(GL_QUADS);
    
    glTexCoord2f(0,0);glVertex3f(-1,-1, z);
    glTexCoord2f(HSratio,0);glVertex3f(+1,-1, z);
    glTexCoord2f(HSratio,HSratio);glVertex3f(+1,+1, z);
    glTexCoord2f(0,HSratio);glVertex3f(-1,+1, z);
  glEnd();

  glEnable(GL_FRAGMENT_PROGRAM_ARB);
  glEnable(GL_VERTEX_PROGRAM_ARB);
  glEnable(GL_DEPTH_TEST);
  
  //glMatrixMode(GL_MODELVIEW);glPopMatrix();
  //glMatrixMode(GL_PROJECTION);glPopMatrix();
  
  
}


void drawFrame(int quality){
    if (quality == 100) {               // Moving quality
        drawFrame();
    
    } else {
        MakeHiqualityScreen(quality);   // Still quality
    }
}


// pos camera, coordinate polari
double dist=3.0, alpha=0.0, beta=0.0;

//vector<Byte> texture(hardSettigs.TSIZE*hardSettigs.TSIZE*3,128);

void QAtom::DrawHalo(){
   
  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;
  
  float s=cgSettings.P_halo_size * 2.5;
  
  glMultiTexCoord2fARB(GL_TEXTURE1_ARB, r+s, (r+s)*(r+s) / (s*s+2*r*s));
  
  glTexCoord2f(+1,+1);
  glVertex3f(px,py,pz);

  glTexCoord2f(-1,+1);
  glVertex3f(px,py,pz);
  
  glTexCoord2f(-1,-1);
  glVertex3f(px,py,pz);
  
  glTexCoord2f(+1,-1);
  glVertex3f(px,py,pz);
  
}
  
void QAtom::Draw(){
  
  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;
  
  glColor3f(cr,cg,cb);
  glTexCoord2f(tx/float(moltextureCanvas.GetHardRes()),ty/float(moltextureCanvas.GetHardRes()));
    
  glNormal3f(+1,+1, r);
  glVertex3f(px,py,pz);

  glNormal3f(-1,+1, r);
  glVertex3f(px,py,pz);

  glNormal3f(-1,-1, r);
  glVertex3f(px,py,pz);
  
  glNormal3f(+1,-1, r);
  glVertex3f(px,py,pz);
}

void Bond::DrawHalo(){

  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;

  glTexCoord4f(dir[0],dir[1],dir[2], 1.0/lenght);
  
  glNormal3f(+1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  glNormal3f(-1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  
  glNormal3f(-1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  glNormal3f(+1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  
}

void Bond::Draw(){

  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;

//  glColor3f(cr,cg,cb);
//  glTexCoord2f(tx/float(TSIZE),ty/float(TSIZE));

  glTexCoord4f(dir[0],dir[1],dir[2], 1.0/lenght);
  //glMultiTexCoord3fARB(GL_TEXTURE3_ARB, col1[0],col1[1],col1[2] );
  glColor3fv(&(col1[0]));
  glSecondaryColor3fv(&col2[0]);
  //glMultiTexCoord3fARB(GL_TEXTURE4_ARB, col2[0],col2[1],col2[2] );
  glMultiTexCoord3fARB(GL_TEXTURE1_ARB, startp[0],startp[1],startp[2] );
  glMultiTexCoord2fARB(GL_TEXTURE2_ARB, tx/float(moltextureCanvas.GetHardRes()),ty/float(moltextureCanvas.GetHardRes()));

  glNormal3f(+1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  glNormal3f(-1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  
  glNormal3f(-1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  glNormal3f(+1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  
}

void QAtom::DrawShadowmap(){    

  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;

  glNormal3f(+1,+1, r);
  glVertex3f(px,py,pz);
    
  glNormal3f(-1,+1, r);
  glVertex3f(px,py,pz);
  
  glNormal3f(-1,-1, r);
  glVertex3f(px,py,pz);
  
  glNormal3f(+1,-1, r);
  glVertex3f(px,py,pz);
}

void Bond::DrawShadowmap(){

  if ((!geoSettings.showHetatm)&&(hetatomFlag)) return;
  
  glTexCoord4f(dir[0],dir[1],dir[2], 1.0/lenght);
  
  glNormal3f(+1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  glNormal3f(-1,+1,0);
  glVertex3f(a[0],a[1],a[2]);
  
  glNormal3f(-1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  glNormal3f(+1,-1,0);
  glVertex3f(b[0],b[1],b[2]);
  
}

float extractCurrentScaleFactor(float x[4][4]){
  float det= x[0][0]*x[1][1]*x[2][2]
            -x[0][0]*x[1][2]*x[2][1]
            +x[1][0]*x[2][1]*x[0][2]
            -x[1][0]*x[0][1]*x[2][2]
            +x[2][0]*x[0][1]*x[1][2]
            -x[2][0]*x[1][1]*x[0][2];
  return pow(fabs(det), 1.0f/3.0f);
}

float extractCurrentScaleFactor(){
  float x[4][4];
  glGetFloatv(GL_MODELVIEW_MATRIX, &(x[0][0]));
  return extractCurrentScaleFactor(x);
}

void prepareDepthTextureForCurrentViewpoint();


void Mol::DrawHalos(){ 
  
    // let's try to aviod THIS!
    prepareDepthTextureForCurrentViewpoint(); // hum, unavoidable.
    
    glPushMatrix();
    glScalef(1/r,1/r,1/r);
    glTranslatef(-px,-py,-pz);

    float x[4][4], scalef;
    glGetFloatv(GL_MODELVIEW_MATRIX, &(x[0][0]));
    
    glProgramEnvParameter4fARB(GL_VERTEX_PROGRAM_ARB, 0, 
      scalef=extractCurrentScaleFactor(x), 0,0,0
    );

    glEnable(GL_VERTEX_PROGRAM_ARB);
    glEnable(GL_FRAGMENT_PROGRAM_ARB);
    
    glDepthMask(false);
    glEnable(GL_BLEND);
    
    if (cgSettings.doingAlphaSnapshot)
      glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);
    else
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    cgSettings.BindHaloShader( haloCanvas.GetResPow2() );
    
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 0, 
      (100.0+cgSettings.P_halo_aware*1300.0)/scalef/mol.r, 0,0,0
    );
    
    glBegin(GL_QUADS);
      for (int i=0; i<atom.size(); i++) atom[i].DrawHalo();
    glEnd();

    /*
    glBegin(GL_QUADS);
      for (int i=0; i<bond.size(); i++) bond[i].DrawHalo();
    glEnd();
    */

    glDisable(GL_BLEND);
    cgSettings.BindShaders();
    
    glDepthMask(true);
    
    glPopMatrix();
    

    glDisable(GL_VERTEX_PROGRAM_ARB);
    glDisable(GL_FRAGMENT_PROGRAM_ARB);
}

void Mol::DrawShadowmap(bool invert){
    glPushMatrix();
    glScalef(1/r,1/r,1/r);
    glTranslatef(-px,-py,-pz);

    float x[4][4], scalef;
    glGetFloatv(GL_MODELVIEW_MATRIX, &(x[0][0]));

    glProgramEnvParameter4fARB(GL_VERTEX_PROGRAM_ARB, 0, 
      scalef=extractCurrentScaleFactor(x),0,0,0
    );
    
    /*if (invert) { 
    glScalef(1,1,-1);
    }*/

    glEnable(GL_VERTEX_PROGRAM_ARB);
    glEnable(GL_FRAGMENT_PROGRAM_ARB);
    
    glActiveTextureARB(GL_TEXTURE0_ARB); 
    glDisable(GL_TEXTURE_2D);
    glActiveTextureARB(GL_TEXTURE1_ARB); 
    glDisable(GL_TEXTURE_2D);


    shadowSettings.BindShaders();
    glBegin(GL_QUADS);
      for (int i=0; i<atom.size(); i++)  atom[i].DrawShadowmap();
    glEnd();

    if (sticks) {
      shadowSettings.BindStickShaders();
      
      glProgramEnvParameter4fARB(GL_VERTEX_PROGRAM_ARB, 0,  
        scalef, stick_radius,stick_radius*2,0  );
      
      
      glBegin(GL_QUADS);
        for (int i=0; i<bond.size(); i++) bond[i].DrawShadowmap();
      glEnd();
    }   
    glPopMatrix();

}

void Mol::Draw(){ 
  
    glPushMatrix();
    glScalef(1/r,1/r,1/r);
    glTranslatef(-px,-py,-pz);
    

    float x[4][4], scalef;
    glGetFloatv(GL_MODELVIEW_MATRIX, &(x[0][0]));
    
    glProgramEnvParameter4fARB(GL_VERTEX_PROGRAM_ARB, 0, 
      scalef=extractCurrentScaleFactor(x),0,0,0
    );
    
    /*
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 6, 
      1.0 / ( scalef*scalef) , 0,0,0
    );*/
/*    printf("ScaleFactor= %f, ShadowScaleFactor= %f\n",
    scalef, shadowScaleFactor  );*/


    glEnable(GL_VERTEX_PROGRAM_ARB);
    glEnable(GL_TEXTURE_2D);

    glActiveTextureARB(GL_TEXTURE0_ARB); 
    moltextureCanvas.SetAsTexture();
    
    if (cgSettings.P_shadowstrenght>0) {
      ShadowMap::GetCurrentPVMatrix();
      ShadowMap::FeedParameters();
    }
      
    for (int i=0; i<3; i++)
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, i, 
      x[i][0],x[i][1],x[i][2],0
    );
    
    glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 6, 
      mol.PredictAO(),0,0,0
    );

    if (draw_balls) {
      if (draw_wireframe_balls)  {
        glDisable(GL_FRAGMENT_PROGRAM_ARB);
        for (int i=0; i<atom.size(); i++)  {
          glColor3f(0,0,1);
          glBegin(GL_LINE_LOOP);
          atom[i].Draw();
          glEnd();
        }
      } else {
        glEnable(GL_VERTEX_PROGRAM_ARB);
        glEnable(GL_FRAGMENT_PROGRAM_ARB);
        //if (DL_atoms==666) glGenD
          
        glBegin(GL_QUADS);
        for (int i=0; i<atom.size(); i++)  atom[i].Draw();
        glEnd();
        
        glDisable(GL_VERTEX_PROGRAM_ARB);
        glDisable(GL_FRAGMENT_PROGRAM_ARB);
      }
    }

 
    if (draw_sticks) 
    if (sticks) {
      glEnable(GL_VERTEX_PROGRAM_ARB);
      glEnable(GL_FRAGMENT_PROGRAM_ARB);
      cgSettings.BindStickShaders();
      ShadowMap::FeedParameters();  
      for (int i=0; i<3; i++)
      glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, i, 
        x[i][0],x[i][1],x[i][2],0
      );
      
      /*
      glProgramEnvParameter4fARB(GL_FRAGMENT_PROGRAM_ARB, 6, 
        1.0 / ( scalef*scalef) , stick_radius,1.0 / ( scalef) ,0
      );*/
      
      glEnable(GL_TEXTURE_2D);
      
      glProgramEnvParameter4fARB(GL_VERTEX_PROGRAM_ARB, 0,  
        scalef, stick_radius,stick_radius*2,0  );     
      
      glColor3f(1,1,1);
      if (draw_wireframe_sticks) {
        glDisable(GL_FRAGMENT_PROGRAM_ARB);
        for (int i=0; i<bond.size(); i++)   {
          glColor3f(0,0.6,0.3);
          glBegin(GL_LINE_LOOP);
          bond[i].Draw();
          glEnd();
        }
      }
      else {
        glBegin(GL_QUADS);
        for (int i=0; i<bond.size(); i++) bond[i].Draw();
        glEnd();
      }
      cgSettings.BindShaders();
    }   
    
    glPopMatrix();
}

int random(int max){
  return rand()%max;
}

/*
void FillRandomTexture(){
  int k=0;
  //for (int y=0; y<hardSettigs.TSIZE; y++)
  //for (int x=0; x<hardSettigs.TSIZE; x++) {
  //  texture[k++]=128+random(127);
  //  texture[k++]=128+random(127);
  //  texture[k++]=128+random(127);
  //  random(127);
  // 
  //}
}

void FillRedTexture(){
  int k=0;
  for (int y=0; y<hardSettigs.TSIZE; y++)
  for (int x=0; x<hardSettigs.TSIZE; x++) {
    texture[k++]=255;
    texture[k++]=0;
    texture[k++]=120;
  }
}*/

void FillShadedTexture(){ 
//  OctaMapSamp s(CSIZE);

//  CubeMapSamp::SetSize(CSIZE);
//  s.Shade();
//  s.FillTexture(texture,TSIZE);
}

void drawQuad(float x, float y, float z, float r){
  
  glNormal3f(+1,+1, r);
  glVertex3f(x,y,z);

  glNormal3f(-1,+1, r);
  glVertex3f(x,y,z);
  
  glNormal3f(-1,-1, r);
  glVertex3f(x,y,z);
  
  glNormal3f(+1,-1, r);
  glVertex3f(x,y,z);
}



Point3f getGlLightPos(){
  float pos[4];
  glGetLightfv(GL_LIGHT0, GL_POSITION, pos);
  
  Point3f L=Point3f(pos);
  float x[4][4];
  glGetFloatv(GL_MODELVIEW_MATRIX, &(x[0][0]));
  Point3f res( 
    L * Point3f(x[0]),
    L * Point3f(x[1]),
    L * Point3f(x[2])
  );
  res.Normalize();
  
  return -res;
}

vector<Point3f> DirV;

void Mol::ResetAO(){
  AOready=false;
  AOstarted=false;
  AOdoneLvl=0;
}

bool Mol::DoingAO(){
  if (!ready) return false;
  if (cgSettings.P_texture==0)  return false;
  if (DirV.size()==0) return true;
  return AOdoneLvl<DirV.size();
}

bool Mol::DecentAO(){
 float k=1;
 if (AOdoneLvl>=DirV.size()) return true;
 if (atom.size()<10) return (AOdoneLvl>6*k);
 if (atom.size()<100) return (AOdoneLvl>4*k);
 if (atom.size()<1000) return (AOdoneLvl>2*k);
 if (atom.size()<10000) return (AOdoneLvl>1*k);
 return true;
}

float Mol::PredictAO(){
    //  Additive prediction
    //return 0.6*(DirV.size()-AOdoneLvl)/float(DirV.size());
    
    // multiplicative prediction
    if (DirV.size()==0) return 1.0; else {
      float coeff=0.25+(AOdoneLvl-1)/20.0;
      if (coeff>1.0f) coeff=1.0f;
      return 
      coeff*float(DirV.size()*1.0f) /  (AOdoneLvl/*+DirV.size()*0.3f*/);
    }
}


void Mol::PrepareAOstart(){
  AOdoneLvl=0;
  AOgpu2::Reset(*this);

  AOstarted=true;
  if (DirV.size()==0) {
    // genreate probe views
    GenNormal<float>::Uniform(hardSettings.N_VIEW_DIR,DirV);
    // mix them!
    int N=DirV.size();
    for (int k=0; k<N/2; k++) {
      int i=rand()%N;
      int j=rand()%N;
      Point3f tmp=DirV[i];
      DirV[i]=DirV[j];
      DirV[j]=tmp;
    }
  }
}

// for testing purposes
bool Mol::PrepareAOSingleView(){
  static int i=0;
  PrepareAOstart();
  AOgpu2::Bind();
  AOgpu2 ao(DirV[i], *this, 4 );
  i++; if (i>DirV.size()) i=0;
  AOgpu2::UnBind();
  AOdoneLvl=DirV.size();
}

bool Mol::PrepareAOstep(int nsteps){
  
  if (!DoingAO()) return true;
  if (!AOstarted) PrepareAOstart();
 
  AOgpu2::Bind();
  if (validView(DirV[AOdoneLvl])) AOgpu2 ao(DirV[AOdoneLvl], *this, DirV.size());
  AOgpu2::UnBind();

  
  AOdoneLvl++;
  return  (AOdoneLvl>=DirV.size()) ;
}

void Mol::PrepareAOallAtOnce(){
  if (AOready) return;
  
  StartTime();
  
  while (!PrepareAOstep(1));
    
  //AOgpu2::GetFinalTexture(texture,*this);
            //refresh();
            
  FILE *f = fopen("res.txt", "w");
  long int w=TakeTime(f,"sampled");
            
  fprintf(f,"          %d views done in %d msec (%.2f views x sec), with %d atoms & %d sticks.\n",
     DirV.size(), w,
     DirV.size()*1000.0/w, this->atom.size(),
     this->sticks?(this->bond.size()):0 );
  fclose(f);

  AOready=true;
}

void clearFrame() {
  glClearColor( cgSettings.P_bg_color_R, cgSettings.P_bg_color_G, cgSettings.P_bg_color_B, 0.0f);

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void setLightDir(Point3f d){
  float f[4];
  f[0]=d[0];
  f[1]=d[1];
  f[2]=d[2];
  f[3]=0;
  glLightfv(GL_LIGHT0, GL_POSITION, f );
}

Point3f getDirFromTrackball(vcg::Trackball &tb){
  glPushMatrix();
  gluLookAt(1,-3,-5,   0,0,0,   0,1,0);    

  tb.center=Point3f(0, 0, 0);
  tb.radius= 1;
  
	tb.GetView();
  tb.Apply(false);

  float pos[4]={0.0f,0.0f,-1.0f,0.0f};
  float d[16];
  glGetFloatv(GL_MODELVIEW_MATRIX,d);
  glPopMatrix();
  
  Point3f res(-d[8],-d[9],-d[10]);
  res.Normalize();
  return res;

}


void drawLightDir()
{
	glPushMatrix();
	lightTrack.GetView();
  lightTrack.Apply(false);
#if 0
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT);
	glColor3f(1,1,0);
    glDisable(GL_LIGHTING);
    const int lineNum=3;
	glBegin(GL_LINES);
    for(unsigned int i=0;i<=lineNum;++i)
      for(unsigned int j=0;j<=lineNum;++j) {
        glVertex3f(-1.0f+i*2.0/lineNum,-1.0f+j*2.0/lineNum,-2);
        glVertex3f(-1.0f+i*2.0/lineNum,-1.0f+j*2.0/lineNum, 2);
      }
	glEnd();
    glPopAttrib();
#endif
    
	glPopMatrix();
}


/*
 * FUNCTION: drawFrame
 */
static bool trackInitialized = false;

void drawFrame() {
  
    cgSettings.MakeShaders();
    
    if (mol.DoingAO()) {
      // do at least one more step per rendering
      mol.PrepareAOstep(1);
      // continue until decent
      while (!mol.DecentAO()) mol.PrepareAOstep(1);  
    }

    /*if (cgSettings.UseHalo()>0) {
      // write depth in HaloTexture
      glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, haloFrame);
    } else {
      // write depth in depthbuffer
      glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0);
    }*/
  
  
  mainCanvas.SetAsOutput();
    
  if (cgSettings.doingAlphaSnapshot)    
    glClearColor( cgSettings.P_halo_col, cgSettings.P_halo_col, cgSettings.P_halo_col, 0.0f);
  else
    glClearColor( cgSettings.P_bg_color_R, cgSettings.P_bg_color_G, cgSettings.P_bg_color_B, 0.0f);

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);  
  
  
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
  
  
  Point3f lightDir;
  
  if  ( cgSettings.P_sem_effect  // fixed light dir sem effect
//    || mol.sticks               // quick Hack: fixed light dir when bonds
    )
    lightDir= Point3f(0,0,1);
  else 
    lightDir=getDirFromTrackball(lightTrack);
    
  setLightDir( lightDir );

//  gluLookAt(0,0,-3,   0,0,0,   0,1,0);    original
//  gluLookAt(0,0,-3,   0,0,0,   0,1,0);    ok for tra

    if (mol.hasDefaultView())
        gluLookAt(0,0, 40,   0,0,0,   0,1,0);
    else
        gluLookAt(0,0,-40,   0,0,0,   0,1,0);
        
    if(MovingLightMode)
        drawLightDir();
    glColor3f(1,1,1);

    if (mol.hasDefaultView()) {
        float angle, axisX, axisY, axisZ;
        mol.getDefaultViewRotation(&angle, &axisX, &axisY, &axisZ);
        glRotatef(angle, axisX, axisY, axisZ);
    }


  if (1) {
    
    //track.center=Point3f(0, 0, 0);
    //track.radius= 1;
    //setProjection();

    if (aniStep>=0) // BH: Doesn't normally seem to be aniStep>=0
    {
      double extraRot=360.0*aniStep;
      
      // set extra rotation for GIF animation:
      switch (hardSettings.GIF_ANIMATION_MODE) {
       default:
       case 0: 
        glRotated(-hardSettings.GIF_ROT_SIDEVIEW_ANGLE,1,0,0);
        glRotated(extraRot,0,1,0);
        break;
       case 1:
        glRotated(-extraRot,0,0,1);
        glRotated(hardSettings.GIF_INSP_ANGLE,0,1,0);
        glRotated(extraRot,0,0,1);
        break;
       case 2:{
        double substep[6];
        for (int i=0; i<6; i++) {
          substep[i]=(aniStep*6-i)*90.0;
          if (substep[i]<0) substep[i]=0;
          if (substep[i]>90.0) substep[i]=90.0;
        }
        glRotated(-substep[5], 1,0,0);
        glRotated(-substep[4], 0,1,0);
        glRotated(-substep[3], 0,1,0);
        glRotated(-substep[2], 1,0,0);
        glRotated(-substep[1], 0,1,0);
        glRotated(-substep[0], 0,1,0);
        }break;
      }
    }

    setProjection( mainCanvas.GetVideoSize() );
    track.GetView();
    track.Apply(false); // Set to true to see the trackball itself.
    setProjection( mainCanvas.GetSoftRes() );
    
    if (cgSettings.P_use_shadowmap()) {
      shadowmap.computeAsTexture( getGlLightPos() , cgSettings.do_use_doubleshadow(), shadowmapCanvas);
      //shadowmap.computeAsTexture( Point3f(0,1,0) );
    }

    cgSettings.BindShaders();

    glEnable(GL_TEXTURE_2D);
    //glBindTexture(GL_TEXTURE_2D, molTexture);

    glActiveTextureARB(GL_TEXTURE1_ARB); 
    shadowmapCanvas.SetAsTexture();

    mol.Draw();
    //  shadowmap.m.DrawShadowmap(false);
  
    glDisable(GL_VERTEX_PROGRAM_ARB);
    glDisable(GL_FRAGMENT_PROGRAM_ARB);
    glDisable(GL_BLEND);
    
    if (cgSettings.UseHalo()>0) mol.DrawHalos();
  }

}

void SetTextureAccess(bool bilinear){  
  glActiveTextureARB(GL_TEXTURE0_ARB); 
  moltextureCanvas.SetAsTexture();
  
  
  if (bilinear) {
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
  }
  else {
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  }
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
}

/*
void ReloadTexture(vector<Byte> t, bool bilinear){  
//  glEnable(GL_TEXTURE);
  glEnable(GL_TEXTURE_2D);
  
  
  glActiveTextureARB(GL_TEXTURE0_ARB); 
  glBindTexture(GL_TEXTURE_2D, molTexture);

  glTexImage2D(
    GL_TEXTURE_2D,
    0,
    GL_RGB,
    //TSIZE,TSIZE,
    0,
    GL_RGB,
    GL_UNSIGNED_BYTE,
    (void*)&(t[0])
  );
  
  
  SetTextureAccess(bilinear);
}*/

int initGl(){
  
  int res=0;
  glClearDepth(1.0);
  glDepthFunc(GL_LESS);
  glEnable(GL_DEPTH_TEST);
  glShadeModel(GL_SMOOTH);

  float pos[4]={0.0f,0.8f,0.6f,0.0f};
  glLightfv(GL_LIGHT0, GL_POSITION, pos);
  
  glEnable(GL_VERTEX_PROGRAM_ARB);
  glEnable(GL_FRAGMENT_PROGRAM_ARB);
  
  if (!CgUtil::init())  res|=ERRGL_NO_GLEW;
  if(!GLEW_ARB_vertex_program ) res|=ERRGL_NO_VS;
  if(!GLEW_ARB_fragment_program ) res|=ERRGL_NO_FS;
  
  
  if (!shadowmap.init())     res|=ERRGL_NO_FBO_SHADOWMAP;
  if (!shadowmap.initHalo()) res|=ERRGL_NO_FBO_HALO;
  
  if (! AOgpu2::init()) res|=ERRGL_NO_FBO_AO;
  
  cgSettings.UpdateShaders();
    
  //ReloadTexture(texture, true);
  return res;
  
}

Point3f RandomUnitVec(){
  Point3f k;
  do {
    k=Point3f(
     (random(200)-100)*0.01,
     (random(200)-100)*0.01,
     (random(200)-100)*0.01
    );
  } while (k.SquaredNorm()>1.0);

  return k.Normalize();
}

long int globaltime,startingtime;

void StartTime();/*{
  startingtime=globaltime=getTicks();
}*/

long int TakeTime(FILE *f , char *st);/*{
  long int timen=getTicks(), delta=timen-globaltime;
  fprintf(f,"%5dmsec: %s\n",delta,st);
  globaltime=timen;
  return delta;
}*/
/*long int TakeTotalTime(){
  long int timen=getTicks(), delta=timen-startingtime;
  printf("------------------\nTotal time: %5dmsec\n",delta);
  globaltime=timen;
  return delta;
}*/

float myfabs(float a){
  return (a<0)?-a:a;
}

void  Cycle(  float &c, float min, float max, float step){
  if (myfabs(c-max)<0.02) c=min; 
  else {
    c+=step;
    if (c>max) c=max;
  }
}

int InitQuteMol(const char * filename)
{
  
  CubeMapSamp::SetSize(CSIZE);
  OctaMapSamp::SetSize(CSIZE);

  if (filename==NULL) filename="porin.pdb";
   
  mol.ReadPdb(filename);
  cgSettings.SetDefaults();
  // initGl gets called from the GL canvas on startup.  It's not 
  // legal to call it before that time because the OpenGL context
  // does not exist yet.
    
  /*if (!initGl()) {
    printf("failed to initialize! :(\n");
    return 0;
  }*/

  //FillRandomTexture();
  //mol.DuplicateTexels(texture, TSIZE);
  //ReloadTexture(texture, bilinear);
  return 1;
}



bool SaveImagePPM( const char * filename , const Byte *im, int sizex, int sizey)
{
		FILE * fp = fopen(filename,"wb");
		if(fp==0) return false;


			fprintf(fp,"P6\n%d %d\n255\n",sizex,sizey);

      int k=0;
			for(int i=0;i<sizex*sizey;++i)
			{
			 fwrite(&(im[k++]),1,1,fp);
			 fwrite(&(im[k++]),1,1,fp);
			 fwrite(&(im[k++]),1,1,fp);
			 //k++;
			}
	
		fclose(fp);
		return true;
}

bool SaveImagePPM( const char * filename , const vector<Byte> &im, int sizex, int sizey){
  return 
  SaveImagePPM( filename , (Byte*)(&im[0]), sizex, sizey);
}

bool LoadImagePPM( const char * filename , vector<Byte> &im)
{
		FILE * fp = fopen(filename,"rb");
		if(fp==0) return false;

      int sizex, sizey, res;
			res=fscanf(fp,"P6\n%d %d\n255\n",&sizex,&sizey);
			printf("Loading %s (res=%d)...\n",filename, res);
			if (res!=2) return false;
			printf(" - size= (%d %d) ...\n",sizex, sizey);

      int k=0;
			for(int i=0;i<sizex*sizey;++i)
			{
			 fread(&(im[k++]),1,1,fp);
			 fread(&(im[k++]),1,1,fp);
			 fread(&(im[k++]),1,1,fp);
			}
	
		fclose(fp);
		return true;
}
