#include <stdio.h>

#if defined(_WIN32)
#include <strings.h>
#else
#include <string.h> // for strcmp
#endif
#include "HardSettings.h"
  
void HardSettings::SetDefaults(){
  TSIZE=1024; // total texture size
  MAX_TSIZE=2048; /// MAX texture size

  
  N_VIEW_DIR=128;

  SHADOWMAP_SIZE=1024;  // texture size for shadowmap
  AOSM_SIZE=256;        // texture size for shadowmmaps for AO comp[utation

  // if true, use double ShadomMap optimization
  doubleSM=1;
  
  NVIDIA_PATCH = 0;
  
  MOVING_QUALITY=100;
  STILL_QUALITY=200;

  SNAP_SIZE=1024;   // snapshots size
  SNAP_ANTIALIAS=1;
  PNG_TRANSPARENT=0;


  // GIF animation settings
  GIF_SNAP_SIZE=256;
  GIF_INITIAL_PAUSE=0;
  GIF_ANIMATION_MODE=0;
  
  GIF_ROT_N_FRAMES=60;
  GIF_ROT_MSEC=3000;
  GIF_ROT_SIDEVIEW_ANGLE=10;
  
  GIF_INSP_N_FRAMES=60;
  GIF_INSP_MSEC=3000;
  GIF_INSP_ANGLE=10;
  
  GIF_6SIDES_N_FRAMES=10;
  GIF_6SIDES_MSEC=400;
  GIF_6SIDES_PAUSE=1000;

};



static char* names[NNAMES]={
  "TSIZE",
  "MAX_TSIZE",
  "N_VIEW_DIR",
  "SHADOWMAP_SIZE",
  "AOSM_SIZE",
  "MOVING_QUALITY",
  "STILL_QUALITY",
  "doubleSM",
  "NVIDIA_PATCH",

  "SNAP_SIZE",
  "SNAP_ANTIALIAS",
  
  "PNG_TRANSPARENT",

  "GIF_SNAP_SIZE",
  "GIF_INITIAL_PAUSE",
  "GIF_ANIMATION_MODE",
  
  "GIF_ROT_N_FRAMES",
  "GIF_GIF_ROT_MSEC",
  "GIF_GIF_ROT_SIDEVIEW_ANGLE",
  
  "GIF_INSP_N_FRAMES",
  "GIF_INSP_MSEC",
  "GIF_INSP_ANGLE",
  
  "GIF_6SIDES_N_FRAMES",
  "GIF_6SIDES_MSEC",
  "GIF_6SIDES_PAUSE",
};


HardSettings::HardSettings(){
  int i=0;
  data[i++]=&TSIZE;
  data[i++]=&MAX_TSIZE;
  data[i++]=&N_VIEW_DIR;
  data[i++]=&SHADOWMAP_SIZE;
  data[i++]=&AOSM_SIZE;
  data[i++]=&MOVING_QUALITY;
  data[i++]=&STILL_QUALITY;
  data[i++]=&doubleSM;
  data[i++]=&NVIDIA_PATCH;
  
  data[i++]=&SNAP_SIZE;
  data[i++]=&SNAP_ANTIALIAS;
  
  data[i++]=&PNG_TRANSPARENT;

  data[i++]=&GIF_SNAP_SIZE;
  data[i++]=&GIF_INITIAL_PAUSE;
  data[i++]=&GIF_ANIMATION_MODE;
  
  data[i++]=&GIF_ROT_N_FRAMES;
  data[i++]=&GIF_ROT_MSEC;
  data[i++]=&GIF_ROT_SIDEVIEW_ANGLE;
  
  data[i++]=&GIF_INSP_N_FRAMES;
  data[i++]=&GIF_INSP_MSEC;
  data[i++]=&GIF_INSP_ANGLE;
  
  data[i++]=&GIF_6SIDES_N_FRAMES;
  data[i++]=&GIF_6SIDES_MSEC;
  data[i++]=&GIF_6SIDES_PAUSE;


}


static char* comments[NNAMES]={
  "favoured texture size for molecule",
  "maximal texture size (used when molecule too large for TSIZE)",
  "number of view directions ussed in AO computation",
  "texture size for shadowmap",
  "texture size for shadowmmaps for AO computation",
  "Quality of image on screen when molecole moves (between 50..200)",
  "Quality of image on screen when molecole is still (between 50..200)",
  "if 1, use double ShadomMap optimization (two way lights)",
  "use 1 - *AND* disable doubleSM - to patch a bug reported on some Nvidia cards (warning: lowers visual quality!)",
 
  "snapshots resolution (per side)",
  "if 1, antialias exported snapshots",
  "if 1, save PNG images with tranparent background",
 
    
  "resolution of exported GIF animations",
  "initial pause in msec before each animation loop",
  "if 0: full rotation. If 1: inspection mode (rotation around current viewpoint). If 2: six-views show.",
  
  "number of frames of exported GIF animations (for full rotation)",
  "total duration in msec of GIF animations loop (for full rotation)",
  "angle (in -45 +45). If 0, perfect side rotation; if >0, look from above; if <0, look from below (for full rotation)",

  "number of frames of exported GIF animations (for inspections)",
  "total duration in msec of GIF animations loop (for inspections)",
  "in (10..45). Animation is an inspection around current view point (for inspections)",
  
  "number of frames of exported GIF animations (for six-views show)",
  "duration in msec of each face shift (for six-views show)",
  "pause in msec after each face shift (for six-views show)",
};




bool HardSettings::Load(char *fn){
  FILE *f=fopen(fn,"rt");
  
  bool present[NNAMES];
  for (int i=0; i<NNAMES; i++) present[i]=false;
  bool duplicated=false;
  bool errors=false;
  
  if (!f) return false;
  char token[255];
  char last[255];
  last[0]==0;
  while (1){
    if (fscanf(f,"%s",token)!=1) break;
    if (token[0]=='=') {
      int val;
      if (fscanf(f,"%d",&val)==1)  {
        bool ok=false;
        for (int i=0; i<NNAMES; i++) {
          if (strcmp(names[i],last)==0) {
            ok=true;
            *(data[i])=val;
            if (present[i]) duplicated=true;
            present[i]=true;
          }
        }
        if (!ok) errors=true;
      } else errors=true;
    }
    sprintf(last,"%s",token);
  }
  fclose(f);
  for (int i=0; i<NNAMES; i++) if (!present[i]) return false;
  
  if (duplicated) return false;
  if (errors) return false;
  return true;
}

bool HardSettings::Save(char *fn){
  FILE *f=fopen(fn,"wt");
  
  static HardSettings defaults;
  defaults.SetDefaults();
  
  if (!f) return false;
  
  for (int i=0; i<NNAMES; i++) {
    if (i==13) // quick hack
    fprintf(f,"  \\\\ PARAMETERS FOR GIF ANIMATION \n  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\n");
    
    fprintf(f,"%s = %d\n  \\\\ %s\n  \\\\ (default: %d ) \n\n", 
    names[i], *(data[i]), comments[i] , *(defaults.data[i]) );
  }
  fclose(f);
  return true;
}

bool HardSettings::OnStart(){
  SetDefaults();
  if (!Load("qutemol.cfg")) {
    Save("qutemol.cfg");
  }
}





HardSettings hardSettings; // SINGLETON
