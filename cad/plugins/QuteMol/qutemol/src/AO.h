
// class to compute ambient occlusion

class AO{
//private:
  Point3f dir; // direction
  
  vector<float> buf;
  int bufx, bufy;
  float bufscale;
  
  inline int index(int x, int y){
    int res=x+bufx*y;
    if (res<0) res=0; 
    if (res>=buf.size()) res=buf.size()-1;
    return res;
    //return x+bufx*y;
  }

  void PrintBuffer();
  void RenderSphere(float cx, float cy, float cz, float rad);  
  void CheckAtom(QAtom &a);
  
public:

AO( Point3f _dir, Mol &m);

};
