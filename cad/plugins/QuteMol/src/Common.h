extern int winx, winy;

typedef unsigned char Byte;

// SDL functions: remiplement these
//void swapbuffers();
//void refresh();
long int getTicks();



// drawing & geom settings...
extern CgUtil cgSettings;
extern GeoSettings geoSettings; // singleton

extern bool bilinear;
extern bool MovingLightMode;

extern bool draw_balls; // just to test 
extern bool draw_sticks; // just to test 
extern bool draw_wireframe_sticks;
extern bool draw_wireframe_balls;

extern bool use_accurate_halo;

void setAniStep(double step);
void stopAni();

int InitQuteMol(const char * filename);

#define ERRGL_OK 0
#define ERRGL_NO_FS 1
#define ERRGL_NO_VS 2
#define ERRGL_NO_FBO_SHADOWMAP 4
#define ERRGL_NO_FBO_HALO 8
#define ERRGL_NO_FBO_AO 16
#define ERRGL_NO_GLEW 32

// returns an ERRGL code
int initGl();

void drawFrame(int quality);
void clearFrame();
void UpdateShadowmap();

int GetCurrentHetatm();

int GetCurrentAtm();

void SetTextureAccess(bool bilinear);
//void ReloadTexture(vector<Byte> t, bool bilinear);

Byte* GetSnapshot(int sx, int sy, bool alpha);

//extern Mol mol;
//extern ShadowMap shadowmap;
extern CgUtil shadowSettings; 

extern  float background;

void StartTime();
long int TakeTime(FILE *f, char *st);
long int TakeTotalTime();
void  Cycle(  float &c, float min, float max, float step);

void SetColMode(float mode);
float GetColMode();
void ResetColMode();

void ChangeColorSchema(int i=-1);



//extern vector<Byte> texture;

//bool LoadImagePPM( const char * filename , vector<Byte> &im);
//bool SaveImagePPM( const char * filename , const vector<Byte> &im, int sizex, int sizey);


