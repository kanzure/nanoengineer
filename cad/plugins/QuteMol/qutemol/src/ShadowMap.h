
extern bool validView(Point3f p);

class ShadowMap{
//private: 
public:
  Mol &m;
public:
  void computeAsTexture(vcg::Point3f L, bool makeboth, MyCanvas &canvas);
  bool init();
  bool initHalo();
  
  
  // adapt to current PVMatrix
  static void ShadowMap::GetCurrentPVMatrix();
  
  // feed parametmers to FP
  static void FeedParameters();
  
  static void Update();
  
  ShadowMap(Mol &_m) : m( _m ){
  }
};


class AOgpu2{
public: 
  
static bool init();

static void Reset(Mol &m);
static void Bind();

AOgpu2( Point3f _dir, Mol &m, int nviews);

static void UnBind();

};

//extern unsigned int finalFrame; // frame dove metto l'immagine finale! 0 se lo schermo.

//bool createOffsetFrame(uint &frameID, uint &textureID, int screensize, int flags);

