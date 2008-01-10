
#include <wx/log.h>


class MyCanvas{
public:
  
  
  bool ratio2x1;
  
  typedef enum{ COLOR, DEPTH, COLOR_AND_DEPTH } Kind;
  Kind kind;
  
  bool SetAsOutput();
  bool SetAsTexture();
  
  bool Test(){return SetAsOutput();}
  
  MyCanvas(Kind k, int size);
  MyCanvas(Kind k);
    
  void SetRes( int res );
  void SetResPow2( int pow );
  
  int GetSoftRes();
  int GetHardRes();
  
  int GetResPow2( ) {return currentRes; }
  
  int GetVideoSize( ) {
    return videoSize;
  }
  
  void SetSameRes( const MyCanvas &c );
  
  void RedirectToVideo();
  void RedirectToMemory();
  void SetVideoSize(int v); // when redirectig to video
  
private:
  int currentRes; // just an index
  enum {MAX_RES=15};
  unsigned int frameID[MAX_RES];
  unsigned int textureID[MAX_RES];
  bool InitRes();
  bool onVideo;
  int videoSize;
  int softRes; // subset image, not a power of 2
};

extern MyCanvas mainCanvas, haloCanvas, moltextureCanvas, shadowmapCanvas, shadowAOCanvas;


