
#include <GL/glew.h>

#include "MyCanvas.h"
#include "HardSettings.h"

MyCanvas mainCanvas(MyCanvas::COLOR_AND_DEPTH);
MyCanvas shadowmapCanvas(MyCanvas::DEPTH);
MyCanvas shadowAOCanvas(MyCanvas::DEPTH);
MyCanvas haloCanvas(MyCanvas::DEPTH); 
MyCanvas moltextureCanvas(MyCanvas::COLOR,hardSettings.TSIZE);


#define INVALID_ID 666
  
typedef unsigned int uint;

bool MyCanvas::SetAsOutput(){
  if (onVideo) glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0);
  else {
    if (frameID[ currentRes ] == INVALID_ID ) {
      if ( !InitRes() ) return false;
    }
    glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, frameID[ currentRes ] );
  }
  return true;
}

bool MyCanvas::SetAsTexture(){
  glBindTexture( GL_TEXTURE_2D, textureID[ currentRes ] );
}
  
MyCanvas::MyCanvas(Kind k, int size){
  currentRes=0;
  onVideo=false;
  kind=k;
  for (int i=0; i<MAX_RES; i++) {
    frameID[i]=textureID[i]=INVALID_ID;
  }
  SetRes(size);
}

MyCanvas::MyCanvas(Kind k){
  currentRes=0;
  onVideo=false;
  kind=k;
  for (int i=0; i<MAX_RES; i++) {
    frameID[i]=textureID[i]=INVALID_ID;
  }
}

  
void MyCanvas::SetRes( int res ) {
  int i=0;
  softRes=res;
  
  while ( (1<<i) < res)  i++; 
  
  if (i>=MAX_RES) { i=MAX_RES-1; softRes=1<<i; }
  currentRes=i; 
  

}

void MyCanvas::SetResPow2( int pow ){
  currentRes=pow;
  softRes=1<<currentRes;
}
  
void MyCanvas::RedirectToVideo(){
  onVideo=true;
}

void MyCanvas::RedirectToMemory(){
  onVideo=false;
}

void MyCanvas::SetVideoSize(int v){
  videoSize=v;
}

int MyCanvas::GetHardRes(){
  if (onVideo) {
    return videoSize;    
  } else 
  return 1<<currentRes;
}

int MyCanvas::GetSoftRes(){
  if (onVideo) {
    return videoSize;    
  } else 
  return softRes;
}

void MyCanvas::SetSameRes( const MyCanvas &c ){
  if (c.onVideo) {
    SetRes( c.videoSize );
  } else {
    currentRes=c.currentRes;
    softRes=c.softRes;
  }
}

bool CheckFrameBuffer()
{ 
  GLenum res = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT); 
  switch(res) { 
    case GL_FRAMEBUFFER_COMPLETE_EXT: return true; 
    case GL_FRAMEBUFFER_UNSUPPORTED_EXT: 
      //printf("Unsupported FB!\n"); 
      return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT:
      //printf("Incompl: attachment !\n"); 
      return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT:
      //printf("Incompl: missing attach  FB!\n"); 
      return false;  
    //case GL_FRAMEBUFFER_INCOMPLETE_DUPLICATE_ATTACHMENT_EXT:  Note this enum was removed by the Revision 117 of the FBO spec. 
      //printf("Incompl: dupicate attach  FB!\n"); 
    //  return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT:
      //printf("Incompl: dimensions!\n"); 
      return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT:
      //printf("Incompl: formats!\n"); 
      return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT:
      //printf("Incompl: draw buffer!\n"); 
      return false;  
    case GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT:
      //printf("Incompl: read buffer!\n"); 
      return false;  
    default:
      //printf("Unknow FB error!\n"); 
      return false;  
  }
} 


bool MyCanvas::InitRes(){
//bool createOffsetFrame(uint &frameID, uint &textureID, int screensize, int flags){
  
  bool depth= (kind==DEPTH);
  
  bool hide= (kind==DEPTH);
  
  bool use_depth= (kind==COLOR_AND_DEPTH );
  
  
  int screensizex=GetHardRes();
  int screensizey=GetHardRes();
  
  if (ratio2x1) screensizex*=2;
  
  uint status=12345;
  if (glCheckFramebufferStatusEXT!=0)
    status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT); 
 switch(status) { 
   case 12345: 
      //printf("FrameBufferObject Extension not found! [hint: Update drivers] No shadows :(...\n");
      return false; 
   case GL_FRAMEBUFFER_COMPLETE_EXT: break; 
   case GL_FRAMEBUFFER_UNSUPPORTED_EXT:
      //printf("FrameBufferObject not supported by your card! No shadows :(...\n");
      return false; 
  } 

  // creiamo:
  glGenFramebuffersEXT(1, (GLuint *)(& (frameID[ currentRes ])) ); // frame buffer
  
  //if (textureID==666) 
  glGenTextures(1, (GLuint *)(&(textureID[ currentRes ]) )); 

  // settimao l'offset Frame
  glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, frameID[ currentRes ]);

  const int NTRIES=2;
  unsigned int tryme[NTRIES]={GL_DEPTH_COMPONENT24, GL_DEPTH_COMPONENT16};
  static GLuint dummydepth=666;
   
  for (int i=0; i<((depth||use_depth)?NTRIES:1); i++) {
      
/**/  // initialize texture
/**/  //glActiveTextureARB(GL_TEXTURE1_ARB); 
/**/  glBindTexture(GL_TEXTURE_2D, textureID[currentRes] );
/**/  glTexImage2D(GL_TEXTURE_2D, 0, 
/**/  (depth)?tryme[i] :GL_RGBA8, 
/**/    screensizex, screensizey, 0,
/**/   (depth)?GL_DEPTH_COMPONENT:GL_RGBA,
/**/   (depth)?GL_UNSIGNED_INT:GL_UNSIGNED_BYTE, 
/**/    0
/**/  );
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    
  // attach texture to framebuffer depth or color buffer
  glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT,
      (depth)?GL_DEPTH_ATTACHMENT_EXT:GL_COLOR_ATTACHMENT0_EXT, 
      GL_TEXTURE_2D, textureID[currentRes], 0);
      
  if (depth) {
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
/**/  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
/**/  glTexParameteri (GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_LUMINANCE);
    GLuint renderID;
    if (hide) {
      // TODO: render to buffer NONE
      glGenRenderbuffersEXT(1, &renderID ); // render buffer
  
      glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, renderID );
      glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_RGBA, screensizex, screensizey);
  
      glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
        GL_RENDERBUFFER_EXT, renderID );
    }
  }
  
  if (use_depth) {
    
#if 0
    // create dummy depth TEXTURE
    if (dummydepth==666); glGenTextures(1, &dummydepth);
        
    glBindTexture(GL_TEXTURE_2D, dummydepth );
    glTexImage2D(GL_TEXTURE_2D, 0, 
      tryme[i],
      screensizex, screensizey, 0,
      GL_DEPTH_COMPONENT,
      GL_UNSIGNED_INT, 0 
    ); 
    // attach it to framebuffer
    glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_TEXTURE_2D,dummydepth, 0);

#else 
      
    // create dummy depth Renderbuffer (on card)
    if (dummydepth==666) glGenRenderbuffersEXT(1, &dummydepth);
    
    glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, dummydepth );
    glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, tryme[i], screensizex, screensizey );
    // attach it to framebuffer
    glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, dummydepth);

#endif
    
  }


  dummydepth=666;
  if (CheckFrameBuffer()) {
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0 ); 
    return true;
  }
  
 }
  
 glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0 );   
 return false;
}

