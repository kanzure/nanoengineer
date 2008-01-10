
class OctaMapSamp{
public:
  
  int TotTexSizeX(){
    return size;
  }

  int TotTexSizeY(){
    return size;
  }
  
  static vector<int> map;     // mappa 2d di indici a dir
  static vector<Point3f> dir;    // direzioni (uniche!)
  static vector<Point3f> dirrot; // direzioni ruotate (uniche!)
  
  vector<float> sum;          // somme (uniche!)
  vector<float> div;          // divisioni (uniche!)

  static int size;

  void Shade(){
    //col.resize(dir.size());
    /*for (int i=0; i<dir.size(); i++) {
      col[i]=dir[i]*Point3d(0.6,0.8,0);
      if (col[i]<0) col[i]*=-1;
      if (col[i]>1) col[i]=1;
    }*/
  }
  
  static inline int nsamp(){
    return dir.size();
  }

  
  // duplicates those texels that are already douplicated
  void DuplicateTexels(vector<Byte> &t, int s, int tx, int ty){
    int e=size-1; // the end
    // four corners
    int k0=(tx+  (ty  )*s)*3;
    int k1=(tx+e+(ty  )*s)*3;
    int k2=(tx+e+(ty+e)*s)*3;
    int k3=(tx+  (ty+e)*s)*3;
    t[k0  ]=t[k1  ]=t[k2  ]=t[k3  ];
    t[k0+1]=t[k1+1]=t[k2+1]=t[k3+1];
    t[k0+2]=t[k1+2]=t[k2+2]=t[k3+2];
    
    // sides 
    for (int i=1; i<size/2; i++) {
      int k0a=(tx    + (ty +i  )*s)*3;
      int k0b=(tx    + (ty +e-i)*s)*3;
      
      int k1a=(tx+e  + (ty +i  )*s)*3;
      int k1b=(tx+e  + (ty +e-i)*s)*3;
      
      int k2a=(tx+i  + (ty     )*s)*3;
      int k2b=(tx+e-i+ (ty     )*s)*3;
      
      int k3a=(tx+i  + (ty +e  )*s)*3;
      int k3b=(tx+e-i+ (ty +e  )*s)*3;

      t[k0a+0]=t[k0b+0]; t[k1a+0]=t[k1b+0]; t[k2a+0]=t[k2b+0]; t[k3a+0]=t[k3b+0];
      t[k0a+1]=t[k0b+1]; t[k1a+1]=t[k1b+1]; t[k2a+1]=t[k2b+1]; t[k3a+1]=t[k3b+1];
      t[k0a+2]=t[k0b+2]; t[k1a+2]=t[k1b+2]; t[k2a+2]=t[k2b+2]; t[k3a+2]=t[k3b+2];
    }
  }
  

  void FillTexture(vector<Byte> &t, int s, int tx, int ty,
                   float cr,float cg,float cb){
    for (int y=0; y<size; y++) {
    for (int x=0; x<size; x++) 
    {
      int k=(x+tx+(y+ty)*s)*3;
      //Byte shade=(int)( col[ Index( x , y ) ] );
      /*t[k++]= shade;
      t[k++]= shade;
      t[k++]= shade;*/
      
      Point3f p=dir[ Index( x , y ) ];

      Point3f q=(p+Point3f(1,1,1))/2.0*255.0;
        t[k++]= (Byte)q[0];
        t[k++]= (Byte)q[1];
        t[k++]= (Byte)q[2];

      /*int shade=(int)(p*Point3d(0.8,0.6,0)*255.0);
      if (shade<0) shade=-shade/2;
      if (shade>255) shade=255;
      t[k++]= shade;
      t[k++]= shade;
      t[k++]= shade;*/
        

/*      float i=255.0*float(map[Index( x , y )])/(size*size*size);
      t[k++]= (int)i;
      t[k++]= (int)i;
      t[k++]= (int)i;
      

      int r=0, g=0, b=0;
      if (y<size) r=255;
      if (x<size) b=255; if (x>=size*2) g=255; 
      k=(x+(y)*s)*3;
      t[k++]= t[k++]/2+r/2;
      t[k++]= t[k++]/2+g/2;
      t[k++]= t[k++]/2+b/2;
      */

      /*
      int r=0, g=0, b=0;
      if (y<size) r=255;
      if (x<size) b=255; if (x>=size*2) g=255; 
      t[k++]= r;
      t[k++]= g;
      t[k++]= b;*/
//      printf("%4d ",map[Index( x , y )]);
      //printf("%3d ",shade);

    }
    //printf("\n");
    }

  }
  
  inline static int Index(int x, int y){
    return x+y*size;
  }
  
  inline static float sign(float x){
    return (x<0)?-1:+1;
  }
  inline static float Abs(float x){
    return (x<0)?-x:+x;
  }  
  
  void Zero(){
    int n=dir.size();
    sum.resize(n,0);
    div.resize(n,0);
  }
  
  // smoothing of an octamap!
  void Smooth(vector<Byte> &t, int s, int tx, int ty){
    vector<int> oldvalue(size*size*6);
    // copy old values
    for (int y=0; y<size*2; y++) 
    for (int x=0; x<size*3; x++) 
    {
      int k=(x+tx+(y+ty)*s)*3;
      int i= Index( x , y );
      oldvalue[i]=t[k];
    }
    
    int dy=size, dx=1;
    
    int e=size-1;
    // smooth old values
    for (int y=0; y<size; y++) 
    for (int x=0; x<size; x++) 
    {
/*      int i= Index( x , y );
      int sum=oldvalue[i];
      
      if (y!=0)  sum+=oldvalue[i-dy];
      else       sum+=oldvalue[ Index( e-x , 1 ) ];
        
      if (x!=0)  sum+=oldvalue[i-dx];
      else       sum+=oldvalue[ Index( 1 , e-y ) ];
        
      if (y!=e)  sum+=oldvalue[i+dy];
      else       sum+=oldvalue[ Index( e-x ,e-1 ) ];
      
      if (x!=e)  sum+=oldvalue[i+dx];
      else       sum+=oldvalue[ Index( e-1 , e-y ) ];
      
      sum=(sum+3)/5;
*/      
      int i= Index( x , y );
      const int TH=2;
      int sum=oldvalue[i];
      int ddiv=1;
      int w;
      
      if (y!=0)  w=oldvalue[i-dy];
      else       w=oldvalue[ Index( e-x , 1 ) ];
      if(w>TH) {sum+=w; ddiv++; }
        
      if (x!=0)  w=oldvalue[i-dx];
      else       w=oldvalue[ Index( 1 , e-y ) ];
      if(w>TH) {sum+=w; ddiv++; }
        
      if (y!=e)  w=oldvalue[i+dy];
      else       w=oldvalue[ Index( e-x ,e-1 ) ];
      if(w>TH) {sum+=w; ddiv++; }
      
      if (x!=e)  w=oldvalue[i+dx];
      else       w=oldvalue[ Index( e-1 , e-y ) ];
      if(w>TH) {sum+=w; ddiv++; }
      
      sum=(sum+ddiv/2)/ddiv;


      int k=(x+tx+(y+ty)*s)*3;
      t[k]=t[k+1]=t[k+2]=sum;
    }
  }

  // smoothing of an octamap!
  void Smooth(vector<int> &t, int s, int tx, int ty){
    vector<int> oldvalue(size*size*6);
    // copy old values
    for (int y=0; y<size*2; y++) 
    for (int x=0; x<size*3; x++) 
    {
      int k=(x+tx+(y+ty)*s);
      int i= Index( x , y );
      oldvalue[i]=t[k];
    }
    
    int dy=size, dx=1;
    
    int e=size-1;
    // smooth old values
    for (int y=0; y<size; y++) 
    for (int x=0; x<size; x++) 
    {
      int i= Index( x , y );
      const int TH=5;
      int sum=oldvalue[i];
      int ddiv=1;
      int w;
      
      if (y!=0)  w=oldvalue[i-dy];
      else       w=oldvalue[ Index( e-x , 1 ) ];
      if(w>TH) {sum+=w; ddiv++; }
        
      if (x!=0)  w=oldvalue[i-dx];
      else       w=oldvalue[ Index( 1 , e-y ) ];
      if(w>TH) {sum+=w; ddiv++; }
        
      if (y!=e)  w=oldvalue[i+dy];
      else       w=oldvalue[ Index( e-x ,e-1 ) ];
      if(w>TH) {sum+=w; ddiv++; }
      
      if (x!=e)  w=oldvalue[i+dx];
      else       w=oldvalue[ Index( e-1 , e-y ) ];
      if(w>TH) {sum+=w; ddiv++; }
      
      sum=(sum+ddiv/2)/ddiv;
      
      int k=(x+tx+(y+ty)*s);
      t[k]=sum;
    }
  }
  
  static void SetSize(int _size){
    size=_size;
    initMap();
    ComputeWeight();
  }

  static Point3f getDir(float x, float y){
    float fs=float(size)-1;
    Point3f p(x*2/fs-1,y*2/fs-1,0);
    float ax=Abs(p[0]), ay=Abs(p[1]), az=+1;
    if (ax+ay>1.0) {
      p=Point3f( sign(p[0])*(1-ay),
                 sign(p[1])*(1-ax), 0);
      az=-1;
    }
    p[2]=(1-ax-ay)*az;
    p.Normalize();
    return p;
  }
  
  static void initMap(){
    dir.resize(size*size);
    
    for (int y=0; y<size; y++) 
    for (int x=0; x<size; x++) 
      dir[Index(x,y)]=getDir(x,y);
  }

  static vector<float> weight;
  
  static float Area(Point3f a, Point3f b, Point3f c){
    return Abs( ((b-a)^(c-a)).Norm()*0.5 );
  }
  
  static void ComputeWeight(){
    weight.resize(size*size);
    
    for (int y=0,k=0; y<size; y++)
    for (int x=0; x<size; x++,k++){
      float h=0.5;
      
      Point3f p00=getDir(x-h,y-h);
      Point3f p01=getDir(x-h,y+0);
      Point3f p02=getDir(x-h,y+h);
      Point3f p10=getDir(x+0,y-h);
      Point3f p11=getDir(x+0,y+0);
      Point3f p12=getDir(x+0,y+h);
      Point3f p20=getDir(x+h,y-h);
      Point3f p21=getDir(x+h,y+0);
      Point3f p22=getDir(x+h,y+h);
      
      float tota=0; int c=0; int e=size-1;

      if ( (x!=0) && (y!=0) ){
        tota+=Area( p00, p10, p01 );
        tota+=Area( p10, p11, p01 );
        c++;
      }
      if ( (x!=0) && (y!=e) ){
        tota+=Area( p01, p11, p12 );
        tota+=Area( p01, p12, p02 );
        c++;
      }
      if ( (x!=e) && (y!=0) ){
        tota+=Area( p10, p20, p21 );
        tota+=Area( p21, p11, p10 );
        c++;
      }
      if ( (x!=e) && (y!=e) ){
        tota+=Area( p11, p21, p12 );
        tota+=Area( p21, p22, p12 );
        c++;
      }
      weight[k]=1.0/(tota*4/c);
      //printf("%8.6f%c",weight[k], (x%size==size-1)?'\n':' ' );
    }
  }
  
  void FillTexture(vector<Byte> &texture, const vector<int> &sumtable, 
                   int texsize, float div, int tx, int ty );

  OctaMapSamp(){ }

};



