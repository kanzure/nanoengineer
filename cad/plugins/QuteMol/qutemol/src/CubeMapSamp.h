
class CubeMapSamp{
public:

  static int size; // dim lato

  static vector<int> map;     // mappa 2d di indici a dir
  static vector<Point3f> dir;    // direzioni (uniche!)
  static vector<Point3f> dirrot; // direzioni ruotate (uniche!)
  
  vector<float> sum;          // somme (uniche!)
  vector<float> div;          // divisioni (uniche!)

    
    
  static void Transform(Point3f ax, Point3f ay, Point3f az){
    for (int i=0; i<dir.size(); i++) {
      dirrot[i][0]=dir[i]*ax;
      dirrot[i][1]=dir[i]*ay;
      dirrot[i][2]=dir[i]*az;
    }
  }
  
  
  static int TotTexSizeX(){
    return size*3;
  }

  static int TotTexSizeY(){
    return size*2;
  }

  static inline int nsamp(){
    return dir.size();
  }
  
  
  // duplicates those texels that are already douplicated
  void DuplicateTexels(vector<Byte> &t, int s, int tx, int ty){
    int nUnique=map.size();
    vector<int> dupi(nUnique, -1);
    for (int y=0; y<size*2; y++) 
    for (int x=0; x<size*3; x++) 
    {
      int k=(x+tx+(y+ty)*s)*3;
      int i= map[Index( x , y )];
      if (dupi[i]<0) {
        dupi[i]=k;
      } else {
        int a=dupi[i];
        t[a+0]=t[k+0];
        t[a+1]=t[k+1];
        t[a+2]=t[k+2];
      }
    }
  }
  
  void FillTexture(vector<Byte> &t, int s, int tx, int ty,
                   float cr,float cg,float cb){
    for (int y=0; y<size*2; y++) {
    for (int x=0; x<size*3; x++) 
    {
      int k=(x+tx+(y+ty)*s)*3;
      int i= map[Index( x , y )];
      /*Byte col=0, colr=255;
      if (div[i]>0) { col=(Byte)(sum[i]/div[i]*255); colr=128; }
      t[k++]= colr;
      t[k++]= col;
      t[k++]= col;*/
      
      /*
      Byte shade=(int)(dir[map[ Index( x , y ) ] ][2] * 255.0);
      t[k++]= shade;
      t[k++]= shade;
      t[k++]= shade;
      */

      //t[k++]= t[k++]= t[k++]= 200;
      
      Point3f p=dir[map[ Index( x , y ) ] ];
      Point3f q=(p+Point3f(1,1,1))/2.0*255.0;
        t[k++]= (Byte)(q[0]*cr);
        t[k++]= (Byte)(q[1]*cg);
        t[k++]= (Byte)(q[2]*cb);
      

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
  
  
  static inline int Index(int x, int y){
    return x+y*size*3;
  }

  static inline int Index3(int x, int y, int z){
    return x+y*size+z*size*size;
  }
  
  static inline int I(int x){
    return size-1-x;
  }

  void Zero(){
    int n=dir.size();
    sum.resize(n,0);
    div.resize(n,0);
  }
    
  static void initMap(){
    map.resize(size*size*6);
    int dx=0;

    int nsampl=size*size*size - (size-2)*(size-2)*(size-2);
    dir.resize(nsampl);
    dirrot.resize(nsampl);
      
    vector<int> tmpmap(size*size*size);
    int k=0;
    for (int z=0; z<size; z++)
    for (int y=0; y<size; y++)
    for (int x=0; x<size; x++) {
      if ((x==0) || (y==0) || (z==0) || 
         (x==size-1) || (y==size-1) || (z==size-1) ) {
            
         tmpmap[ Index3(x,y,z) ] = k;
         float h=(size-1)*0.5;
         dir[k]=Point3f(x-h,y-h,z-h);
         dir[k].Normalize();
         k++;
      }
    }
    dx=size;
    for (int x=0; x<size; x++) 
    for (int y=0; y<size; y++) {
      map[ Index( x +dx, y      ) ] =  tmpmap[ Index3( x, y, size-1) ];
      map[ Index( I(x) +dx, I(y)+size ) ] =  tmpmap[ Index3( x, y,      0) ];
    }

    dx=0;
    for (int y=0; y<size; y++) 
    for (int z=0; z<size; z++) {
      map[ Index( y+dx, z      ) ] = tmpmap[ Index3( size-1, y, z) ];
      map[ Index( I(y)+dx, I(z)+size ) ] = tmpmap[ Index3(      0, y, z) ];
    }

    dx=size*2;
    for (int x=0; x<size; x++) 
    for (int z=0; z<size; z++) {
      map[ Index( z+dx, x     ) ] = tmpmap[ Index3( x, size-1,  z) ];
      map[ Index( I(z)+dx, I(x)+size) ] = tmpmap[ Index3( x,      0,  z) ];
    }
    
  }

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
    
    int dy=size*3, dx=1;
    const int TH=-1;
    // smooth old values
    for (int y=0; y<size*2; y++) 
    for (int x=0; x<size*3; x++) 
    {
      int i= Index( x , y );
      int sum=oldvalue[i], div=1;
      if ((y%size)!=0) if (oldvalue[i-dy]>TH) {
        sum+=oldvalue[i-dy];
        div++;
      }
      if ((x%size)!=0) if (oldvalue[i-dx]>TH){
        sum+=oldvalue[i-dx];
        div++;
      }
      if (((y+1)%size)!=0) if (oldvalue[i+dy]>TH){
        sum+=oldvalue[i+dy];
        div++;
      }
      if (((x+1)%size)!=0) if (oldvalue[i+dy]>TH){
        sum+=oldvalue[i+dx];
        div++;
      }
      sum/=div;
      int k=(x+tx+(y+ty)*s)*3;
      t[k]=t[k+1]=t[k+2]=sum;
    }
    
    // merge texels
    int nUnique=map.size();
    vector<int> dupi(nUnique, -1);
    for (int y=0; y<size*2; y++) 
    for (int x=0; x<size*3; x++) 
    {
      int k=(x+tx+(y+ty)*s)*3;
      int i= map[Index( x , y )];
      if (dupi[i]<0) {
        dupi[i]=k;
      } else {
        int a=dupi[i];
        t[a+0]=t[k+0]=(t[a+0]+t[k+0])/2;
        t[a+1]=t[k+1]=(t[a+0]+t[k+0])/2;
        t[a+2]=t[k+2]=(t[a+0]+t[k+0])/2;
      }
    }
    
  }
  
  static void SetSize(int _size){
    size=_size;
    initMap();
  }
  
  CubeMapSamp(){
  }
  
};



