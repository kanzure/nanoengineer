typedef unsigned char Byte;

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
#include "AOgpu.h"
#include "HardSettings.h"

extern int CSIZE;
extern int used_mapping;

bool SaveImagePPM( const char * filename , const Byte *im, int sizex, int sizey);
void ReloadTexture(vector<Byte> t, bool bilinear);
float extractCurrentScaleFactor();


CgUtil mySettings;

vector<Byte> AOgpu::fakeTexture;
vector<unsigned int> AOgpu::snap;
vector<int> AOgpu::sum;
unsigned int AOgpu::div;
float AOgpu::areas;
unsigned int AOgpu::mask=0;

void swapbuffers();

void AOgpu::OpenGLSnap()
{
		GLint vp[4];
		glGetIntegerv( GL_VIEWPORT,vp );		// Lettura viewport
		glPixelStorei( GL_PACK_ROW_LENGTH, 0);
		glPixelStorei( GL_PACK_ALIGNMENT, 1);
		snapx = vp[2];
		snapy = vp[3];

		//Create(tx,ty);
		if (snap.size()!=snapx*snapy+1) snap.resize(snapx*snapy+1);

		GLenum mtype  = 0;

    int format=0;
		if(format==0) {
				format = GL_RGBA;
        mtype = GL_UNSIGNED_BYTE;
		}
		if(format==GL_DEPTH_COMPONENT) {
				format = GL_DEPTH_COMPONENT;
        mtype = GL_FLOAT;
		}
 		glReadPixels(vp[0],vp[1],vp[2],vp[3],format,mtype,(GLvoid *)&snap[0]);
  	//SaveImagePPM("test.ppm" ,(Byte*)(&snap[0]), vp[2],vp[3]);
  	
  	//swapbuffers();
}

AOgpu::AOgpu( Point3f _dir, Mol &m) {
 
  int out=hardSettings.TSIZE*hardSettings.TSIZE;
  glClearColor((out&&255)/255.0 , ((out>>8)&&255)/255.0, (out>>16)/255.0, 0    );
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  dir=_dir.Normalize();
  
  // orthonormal basis
  Point3f ax,ay,az=dir;
  ax=az^Point3f(1,0,0);
  if (ax.SquaredNorm()<0.1) ax=az^Point3f(0,1,0);
  ax=ax.Normalize();
  ay=(az^ax).Normalize();
  
  //CubeMapSamp::Transform(ax,ay,az);
  
  // make a snapshot!
  
  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
	GLfloat nearPlane = 0.1;
	GLfloat farPlane = 200;
  glOrtho(-1,+1,-1,+1, nearPlane, farPlane);
  
  

  glMatrixMode(GL_MODELVIEW);
  glPushMatrix();
  glLoadIdentity();
  gluLookAt( az[0],az[1],az[2],  0,0,0, ay[0], ay[1], ay[2] );
  
  if (areas<0) {
    // only once: compute areas
    GLint vp[4];
		glGetIntegerv( GL_VIEWPORT,vp );
		float sc=extractCurrentScaleFactor()*(1/m.r);
		areas=vp[2]*vp[3]*sc*sc;
  }


  mySettings.BindShaders();    
  
  m.Draw();
  OpenGLSnap();
 
  // interpret spanshot
  int k=0,h=0;
  
  //int* snapi=(int*)(&snap[0]);
  int max=snapy*snapx;
  int maxt=sum.size();
  
  /*static*/ 
  // vector<int> found(sum.size(), false );
  
  for (int i=0; i<max; i++){
    //if (snap[i]==0) printf(" ");
    //sum[snap[i]&0x00ffffff]++;
    //if (sum[snap[i]&0x00ffffff] ) |=mask;
    /*
    int dec=snap[i]&0x00ffffff;
    if (!found[dec]) {
      found[dec]=true; 
      sum[ dec ] += snap[i]>>24;
      printf("[%d]",snap[i]>>24);
    }*/
    

    
    if (sum[ snap[i]&0x00ffffff ]>>24 !=div) {
      sum[ snap[i]&0x00ffffff ] =
      (sum[ snap[i]&0x00ffffff ]+(snap[i]>>24))&0x00ffffff | (div<<24);
      //printf("[%d]",snap[i]>>24);
    }

/*    
    sum[ snap[i]&0x00ffffff ] = 
    (
     ( 
      (sum[ snap[i]&0x00ffffff ] + 
        ((sum[ snap[i]&0x00ffffff ]>>24)!=div)*(snap[i]>>24)
      )&0x00ffffff 
     )
     | (div<<24)
    );  */

  }
  /*
  static Point3f sumv=Point3f(0,0,0);
  sumv+=az;
  printf("%d (%f %f %f) (%f %f %f)\n", div, az[0],az[1],az[2], sumv[0],sumv[1],sumv[2]);
  */

  mask<<=1;  
  div++;
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
  glPopMatrix();
}

  
void AOgpu::Reset(Mol &m){
  
  mySettings.SetForOffLine();

  if (fakeTexture.size()==0) {
    // Prepare And Load fake texture
    fakeTexture.resize(hardSettings.TSIZE*hardSettings.TSIZE*3);
    int k=0, i=0;
    for (int x=0; x<hardSettings.TSIZE; x++)
    for (int y=0; y<hardSettings.TSIZE; y++) {
      fakeTexture[i++]=k&255;
      fakeTexture[i++]=(k>>8)&255;
      fakeTexture[i++]=(k>>16)&255;
      k++;
    }
    m.DuplicateTexels(fakeTexture, hardSettings.TSIZE);
  }
  
  glActiveTextureARB(GL_TEXTURE0_ARB); 
  //glBindTexture(GL_TEXTURE_2D, molTexture);
  //ReloadTexture(fakeTexture, false);
  
  div=0;
  if (sum.size()!=hardSettings.TSIZE*hardSettings.TSIZE) {
    sum.resize(hardSettings.TSIZE*hardSettings.TSIZE,0);
  } else {
    sum.clear();
    sum.resize(hardSettings.TSIZE*hardSettings.TSIZE,0);
  }
  mask=1;
  areas=-1; 

  mySettings.BindShaders();
}


inline unsigned int BitCount(unsigned int x){
  x=(((x>>1)&x)&(0x88888888)) + ((x<<1)^x)&(0xAAAAAAAA) ;
  x = ((x>>2)&(0x33333333)) + ( x &(0x33333333));
  x = ((x>>4)&(0x0F0F0F0F)) + ( x &(0x0F0F0F0F));
  x = ((x>>8)&(0x00FF00FF)) + ( x &(0x00FF00FF));
  return (x&0x0000FFFF)+(x>>16);
}

void AOgpu::GetFinalTexture(vector<Byte> &text,Mol &m){
  int k=0,i=0;
  
  //m.SmoothTexture( sum, hardSettings.TSIZE  );
  int maxt=sum.size();
  /*for (int i=0; i<maxt; i++){
    sum[i]=BitCount(sum[i]);
  }*/
  for (int i=0; i<maxt; i++){
    sum[i]&=0x00ffffff;
  }

  m.FillTexture( text, sum, hardSettings.TSIZE, 4.0/float(div) /*8*2*255 / (div * areas )*/ );
  m.DuplicateTexels(text, hardSettings.TSIZE); 
}


