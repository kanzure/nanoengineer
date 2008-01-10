// HARD SETTINGS:
// Settings affecting performance / quality ratio

const int NNAMES=24;

class HardSettings{
public:
  int TSIZE; // total texture size
  int MAX_TSIZE;  // max texture size

  int N_VIEW_DIR;
 

  int SHADOWMAP_SIZE;  // texture size for shadowmap
  int AOSM_SIZE;      // texture size for shadowmmaps for AO computation
  
  int NVIDIA_PATCH;
  
  int MOVING_QUALITY;
  int STILL_QUALITY;
  
  // if true, use double ShadomMap optimization
  int doubleSM;
  
  int SNAP_SIZE;
  int SNAP_ANTIALIAS;
  
  int PNG_TRANSPARENT;

  // GIF animation settings
  int GIF_SNAP_SIZE;
  int GIF_INITIAL_PAUSE;
  int GIF_ANIMATION_MODE;
  
  int GIF_ROT_N_FRAMES;
  int GIF_ROT_MSEC;
  int GIF_ROT_SIDEVIEW_ANGLE;
  
  int GIF_INSP_N_FRAMES;
  int GIF_INSP_MSEC;
  int GIF_INSP_ANGLE;
  
  int GIF_6SIDES_N_FRAMES;
  int GIF_6SIDES_MSEC;
  int GIF_6SIDES_PAUSE;
  
  void SetDefaults();
  bool Load(char *fn);
  bool Save(char *fn);
  bool OnStart(); // tries to load, on faliure setdefaults and saves
  HardSettings();
private:
  int* data[NNAMES];
};

extern HardSettings hardSettings; // SINGLETON
