/*
  PNGWRAPPER! 
  
  This file is included in QuteMol project 
  as temporary hack waiting for WxWidgets to support 
  alpha channel in PNG writing.

*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <vector>
#include <iostream>
using namespace std;

#include <png.h>
 
#include "progress.h"

typedef Byte byte;


void downsample2x2(byte * data, int sx, int sy){
  int j=0;
  for (int y=0; y<sy/2; y++)
  for (int x=0; x<sx/2; x++)
  for (int c=0; c <4; c++) {
    data[j++]=(
      int(data[((y*2+0)*sx+(x*2+0))*4+c])+
      int(data[((y*2+0)*sx+(x*2+1))*4+c])+
      int(data[((y*2+1)*sx+(x*2+0))*4+c])+
      int(data[((y*2+1)*sx+(x*2+1))*4+c])+
      2
      )/4;
  }
}

void downsample2x2NoAlpha(byte * data, int sx, int sy){
  int j=0;
  for (int y=0; y<sy/2; y++)
  for (int x=0; x<sx/2; x++)
  for (int c=0; c <3; c++) {
    data[j++]=(
      int(data[((y*2+0)*sx+(x*2+0))*3+c])+
      int(data[((y*2+0)*sx+(x*2+1))*3+c])+
      int(data[((y*2+1)*sx+(x*2+0))*3+c])+
      int(data[((y*2+1)*sx+(x*2+1))*3+c])+
      2
      )/4;
  }
}

void trace(const char  *st, const char  *st2=NULL){
  static FILE *f=NULL;
  if (!f) f=fopen("trace.txt","wt");
  fprintf(f,st);
  if (st2) fprintf(f,st2);
  fflush(f);
}

void donttrace(char*x){};
void donttrace( const char*x, const char*y){};
#define TRACE donttrace
//#define TRACE trace
void handle_error(struct png_struct_def *png,const char *error) {
	TRACE("Error:\n", error);
}

bool PNGSaveWithAlpha( const char * filename, const byte * const data, int sx, int sy, int reverse ){
  int type=4; int depth=8;
	assert(filename);
	assert(data);
	TRACE("Start\n");
	FILE *fp;
	fp=fopen(filename, "wb+");
	if(!fp) 
		return false;
	TRACE("File open (wb+)\n");

	png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING,
									   //NULL, NULL, NULL);
					                   NULL, //&handle_error, 
                                       &handle_error,
                                       &handle_error);
	TRACE("png_create_write\n");
    if (png_ptr == NULL) {
		fclose(fp);
		return false; 
    }
    
    // Allocate/initialize the image information data.  REQUIRED 
    png_infop png_info_ptr = png_create_info_struct(png_ptr);
	TRACE("png_create_info\n");
    if (png_info_ptr == NULL) {
		fclose(fp);
		png_destroy_write_struct(&png_ptr,  (png_infopp)NULL);
		TRACE("png_destroy_write\n");
		return false;
    }
	
	png_init_io(png_ptr, fp);
	TRACE("png_init_io\n");
	//type: 1 -> PNG_COLOR_TYPE_GRAY (bit depths 1, 2, 4, 8, 16)
    //    2 -> PNG_COLOR_TYPE_GRAY_ALPHA (bit depths 8, 16)
    //    3 -> PNG_COLOR_TYPE_RGB (bit_depths 8, 16)
    //    4 -> PNG_COLOR_TYPE_RGB_ALPHA (bit_depths 8, 16)
	int pixel_type = 1;
	switch(type) {
	case 1: pixel_type = PNG_COLOR_TYPE_GRAY; break;
	case 2: pixel_type = PNG_COLOR_TYPE_GRAY_ALPHA; break;
	case 3: pixel_type = PNG_COLOR_TYPE_RGB; break;
	case 4: pixel_type = PNG_COLOR_TYPE_RGB_ALPHA; break;
	}
	//TRACE("sx %d, sy %d, depth %d, pixel_type %d\n", sx, sy, depth, pixel_type);
  png_set_IHDR(png_ptr, png_info_ptr, sx, sy, depth, pixel_type, 
		        PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
	//TRACE("png_set_IHDR\n");
  png_write_info(png_ptr, png_info_ptr);
	//TRACE("png_write_info\n");
	//TRACE("uffa");*/
	char **rows = new char *[sy];
	for(int i = 0; i < sy; i++)
		rows[i] = (char *)data + i * type * (depth/8) * sx; 
	if(reverse) {
    if (sy>200) StartProgress("Saving PNG", sy);
		for(int r = sy -1; r >= 0; r--) {
      if (r%100) { if (!UpdateProgress(sy-r)) { fclose(fp); return false; }  }
			png_write_rows(png_ptr, (png_byte **)(&(rows[r])), 1);
    }
    EndProgress();
	} else {
		png_write_rows(png_ptr, (png_byte **)(rows), sy);
	}
	delete []rows;
	TRACE("png_write_rows\n");
	png_write_end(png_ptr, png_info_ptr);
	TRACE("png_write_end\n");
	png_destroy_write_struct(&png_ptr, &png_info_ptr);
	TRACE("png_destroy_write\n");
	fclose(fp);
	return true;
}
