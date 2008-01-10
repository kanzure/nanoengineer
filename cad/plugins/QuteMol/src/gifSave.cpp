/*
  GIFWRAPPER! 
  
  This file is included in QuteMol project 
  as temporary hack waiting for WxWidgets to support 
  saving in GIF format (patent is now expired!)

*/

#include <gif_lib.h>
#include <stdio.h>

#include <vector>

using namespace std;

typedef unsigned char Byte;

typedef vector<GifByteType> Frame;

#include "gifSave.h"

// global vairables


static vector<Frame> frames;
static vector<int> delay;

static ColorMapObject* outputPalette;

GifWrapper::GifWrapper(){
  frames.clear();
  delay.clear();
}


static int gifsx, gifsy;
bool GifWrapper::AddFrame(Byte* data, int sx, int sy, float dt){
  
  gifsx=sx;
  gifsy=sy;
  
  unsigned int npix=sx*sy;
  
  
  int paletteSize=256;

  
  Frame output(npix);//=(Frame) malloc(npix);
  

  if (frames.size()==0) {
  
    
    Frame r(npix),g(npix),b(npix);
  
    // de-interlaeve
    for (int i=0, j=0; i<npix; i++){
    r[i]=data[j++];
    g[i]=data[j++];
    b[i]=data[j++];
    }

    outputPalette = MakeMapObject(paletteSize, NULL);
    if (!outputPalette) return false;
    
    if (QuantizeBuffer(sx, sy, &paletteSize, 
                       &(r[0]),&(g[0]),&(b[0]), &(output[0]), 
                       outputPalette->Colors) == GIF_ERROR) return false;

    
  } else {
    // maunal assignment of color indices
    for (int i = 0, j=0; i < npix; i++) {
        int minIndex = 0,
            minDist = 3 * 256 * 256;
        GifColorType *c = outputPalette->Colors;
 
        /* Find closest color in first color map to this color. */
        for (int k = 0; k < outputPalette->ColorCount; k++) {
          int dr = (int(c[k].Red) - data[j] ) ;
          int dg = (int(c[k].Green) - data[j+1] ) ;
          int db = (int(c[k].Blue) - data[j+2] ) ;
          
          int dist=dr*dr+dg*dg+db*db;
          
          if (minDist > dist) {
            minDist  = dist;
            minIndex = k;
          }
        }
        j+=3;
        output[i] = minIndex;
    }

  }
  
  frames.push_back(output);

  delay.push_back(int(dt*100.0));
  return true;       
}



bool AddLoop(GifFileType *gf){
  
   /* yes this was another attempt at supporting the loop extension */
   int loop_count;
   loop_count=0;
   {
     unsigned char nsle[12] = "NETSCAPE2.0";
     unsigned char subblock[3];
     //if (EGifPutExtension(gf, 0xFF, 11, nsle) == GIF_ERROR) {
     if (EGifPutExtensionFirst(gf, APPLICATION_EXT_FUNC_CODE, 11, nsle) == GIF_ERROR) {
       //gif_push_error();
       //i_push_error(0, "writing loop extension");
       return false;
     }
     subblock[0] = 1;
     subblock[2] = loop_count % 256;
     subblock[1] = loop_count / 256;
     //if (EGifPutExtension(gf, 0, 3, subblock) == GIF_ERROR) {
     if (EGifPutExtensionLast(gf, APPLICATION_EXT_FUNC_CODE, 3, subblock) == GIF_ERROR) {
       //gif_push_error();
       //i_push_error(0, "writing loop extention sub-block");
       return false;
     }
#if 0
     if (EGifPutExtension(gf, 0, 0, subblock) == GIF_ERROR) {
       gif_push_error();
       i_push_error(0, "writing loop extension terminator");
       return false;
     }
#endif   
    }
    return true;
}


bool GifWrapper::Save(const char* filename){
  if (frames.size()==0) return false;
  
  
  GifFileType *GifFile = EGifOpenFileName(filename, FALSE);
  
  if (!GifFile) return false;

  if (EGifPutScreenDesc(
        GifFile,
			  gifsx, gifsy, 8, 0,
        outputPalette
      ) == GIF_ERROR) return false;

  if (!AddLoop(GifFile)) return false;

  for (int ni=0; ni<frames.size(); ni++) {      

    static unsigned char
    ExtStr[4] = { 0x04, 0x00, 0x00, 0xff };
 
    
    ExtStr[0] = (false) ? 0x06 : 0x04;
    ExtStr[1] = delay[ni] % 256;
    ExtStr[2] = delay[ni] / 256;
 
    /* Dump graphics control block. */
    EGifPutExtension(GifFile, GRAPHICS_EXT_FUNC_CODE, 4, ExtStr);
            
    
    if (EGifPutImageDesc(
       GifFile,
		   0, 0, gifsx, gifsy, FALSE, NULL
       ) == GIF_ERROR)  return false;
       
       
    for (int y = 0, j=(gifsy-1)*gifsx; y < gifsy; y++, j-=gifsx) {
  	  if (EGifPutLine(GifFile, &(frames[ni][j]), gifsx) == GIF_ERROR) return false;
    }
  }

  if (EGifCloseFile(GifFile) == GIF_ERROR) return false;

  return true;       
}

  
