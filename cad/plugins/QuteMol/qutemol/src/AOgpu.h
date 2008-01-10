
class AOgpu{
//private:
  Point3f dir; // direction
  void CheckAtom(QAtom &a);

  static vector<Byte> fakeTexture;
  static vector<unsigned int> snap;
  
  static vector<int> sum;
  static unsigned int div;
  static float areas; // expected area coverage of a 1 radius sphere
  
  int snapx, snapy;
  
  void OpenGLSnap();
  bool SavePPM( const char * filename );
  
  static unsigned int mask;
public:

static void Reset(Mol &m);

AOgpu( Point3f _dir, Mol &m);

static void GetFinalTexture(vector<Byte> &text, Mol &m);

};
