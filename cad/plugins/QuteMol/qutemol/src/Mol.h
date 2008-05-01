
#include <map>


class MyString{
public:
  int last;
  char lastc;
  char *st;
  MyString(char *_st){
    last=-1;
    st=_st;
  }
  char* sub(int a, int b){
    a--; 
    st[last]=lastc;
    lastc=st[b];
    st[b]=0;
    last=b;
    return st+a;
  }
};


class QAtom{
public: 
  float px,py,pz,r;
  float cr,cg,cb;
  int serial;
  
  int chainIndex;
  unsigned int atomColor;

  float spacefillr, covalentr; 
    
  int tx,ty; // starting places for texture

  bool hetatomFlag;
  //CubeMapSamp s;
  OctaMapSamp s;
  
  inline Point3f P() const {
    return Point3f(px, py, pz);
  }
  
  bool AssignNextTextPos(int texsize);
  
  void SmoothTexture(vector<Byte> &t, int siz){
    /*s.Smooth( t, siz, tx, ty);*/
  }
  void SmoothTexture(vector<int> &t, int siz){
    /*s.Smooth( t, siz, tx, ty);*/
  }
  
  void FillTexture(vector<Byte> &texture, int textsize) {
    s.FillTexture(texture, textsize, tx,ty, cr,cg,cb);
  }
  
  Point3f trp; float trr; // transormed pos and radius
  
  void Transform(const Point3f &ax,const  Point3f &ay,const Point3f &az){
    Point3f p(px,py,pz);
    trp[0]=p*ax;
    trp[1]=p*ay;
    trp[2]=p*az;
    //printf("[r=%f] (%f %f %f) -> (%f %f %f)\n", r, px,py,pz, trp[0],trp[1],trp[2] );
  }
  
  void ScaleTransl(float dx, float dy, float scale){
    trp[0]=(trp[0]+dx)*scale;
    trp[1]=(trp[1]+dy)*scale;
    trr=r*scale;
    //printf("[%f*%f] -> (%f %f %f %f)\n", r, scale, trp[0],trp[1],trp[2],trr );
  }
  
  // color from atom name
  void getCol(const char* st);
  
  QAtom(string st, int chainIndex);
  static bool readError;
  static char lastReadError[1024];
  
  void UpdateColors(float mode, int chainColor);
  
  // sends impostors on screnbuffer
  void Draw();
  // sends halos on screnbuffer
  void DrawHalo();
  void DrawShadowmap();
  
  // for GPU ao.
  void DrawOnTexture();

  /*
  bool operator < (const QAtom& a) const {
    return trp[2]>a.trp[2];
  } 
  */ 

  static unsigned int VBOsize();
  void VBOfill(float * f);
  static void VBOsetup(float *f);

  //inline bool operator <= (QAtom const &a) const {  return px<=a.px;  };
  inline bool operator <  (QAtom const &a) const {  return px< a.px;  };
  
};


class Bond{
public: 
  Point3f a, b;
  Point3f dir;
  Point3f col1, col2;
  float lenght;
  Point3f startp; // start of parameterization
  
  const QAtom *atmA, *atmB;
  
  bool hetatomFlag;
  //Point3f cola, colb;
  void Draw();
  void DrawHalo();
  void DrawShadowmap();
  //Bond(Point3f a,Point3f b, float rada, float radb, Point3f col1, Point3f col2);
  Bond(const QAtom &a,const QAtom &b);
  
  void UpdateColors(); // copies color from atoms
  
  void DrawOnTexture();  // for GPU ao.
  bool AssignNextTextPos(int texsize);
  int tx, ty;
  
};


class Mol{
public: 
  
  bool sticks; // true if ball_and_stick mode
  float colMode; // mode = 1 -> per atom   
                // mode = 0 -> per chain 
                
  void SetColMode(float newColMode);
  
  void SetBallAndSticks(float rad=0.3);  
  void SetLicorice(float rad=0.5);  
  void SetSpaceFill();  
  
  vector<QAtom> atom;
  vector<Bond> bond;
  
  float px,py,pz,r;
  bool textureAssigned;
  
  void Draw();
  void DrawShadowmap(bool invert);
  
  void DrawHalos();
  void DrawOnTexture();

  void FindBonds();

  void ComputeSize();  
  bool ReadPdb(const char *filename);

  float tx0,ty0,tx1,ty1;  // bounding box transformed
  void Transform(const Point3f &ax,const  Point3f &ay,const Point3f &az);  
  
  void ScaleTransl(float scale){
    for (int i=0; i<atom.size(); i++) 
    atom[i].ScaleTransl( -tx0, -ty0, scale);
  }
  
  void SmoothTexture(vector<Byte> &t, int siz){
    for (int i=0; i<atom.size(); i++) 
    atom[i].SmoothTexture(t,siz);
  }

  void SmoothTexture(vector<int> &t, int siz){
    for (int i=0; i<atom.size(); i++) 
    atom[i].SmoothTexture(t,siz);
  }
  
  void Zero() {
    for (int i=0; i<atom.size(); i++) 
    atom[i].s.Zero();
  }
  
  void DuplicateTexels(vector<Byte> &t, int size);
  
  void FillTexture(vector<Byte> &texture, const vector<int> &sumtable, 
                   int texsize, float div );
  
  bool ReassignTexture(int textsize); // for a given texture size
   
  void ReassignTextureAutosize(); // autoselect texture size
  
  int NTotTexels(){
    return atom.size()*atom[0].s.TotTexSizeX()*atom[0].s.TotTexSizeY();
  }
  
  // vertexbuffer objects
  unsigned int vboNorm, vboShadow, vboAO;
  unsigned int vboNormSt, vboShadowSt, vboAOSt; // for the sticks
  
  Mol();
    
  char filename[1024];
  char* GetFilenameTex();
  char* GetFilenameSnap();
  char* GetMolName();

  bool PrepareAOstep(int nsteps=1);
  float PredictAO();
  
  void ResetAO();
  
  bool DoingAO();  // true if AO is being computed
  bool DecentAO(); // true if AO (being computed) is "decent"
  
  // for testing purposes
  bool PrepareAOSingleView();
  
  int natm, nhetatm;  // number of atoms of type hetatm and not ...

  bool IsReady(){return ready;}  
  
  void UpdateColors();
  
  // Functions related to default views (rotation, scale, origin) found in the
  // PDB file's REMARK section.
  bool hasDefaultView() const;
  void getDefaultViewRotation(float* angle,
                              float* axisX, float* axisY, float* axisZ) const;
  
private:
    
    int chainColors[10000]; // Support a ten thousand chains for now.
                            // piotr 080501 increased the array size
                            // It is a temporary fix for large models.

    // unsigned int DL_bonds, DL_atoms; // display lists (UNUSED)
    
    void AddBond(int i, int j);
    
    void PrepareAOallAtOnce();
    
    int AOdoneLvl;
    
    void PrepareAOstart();
    bool AOready;
    bool AOstarted;
    bool ready;
    
    // Variables related to default views (rotation, scale, origin) found in the
    // PDB file's REMARK section.
    bool haveDefaultView;
    float defaultViewRotation[4];
};

extern float stick_radius;

