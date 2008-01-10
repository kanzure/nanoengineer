
typedef unsigned char Byte;

#include <math.h>

#include <vector>
#include <vcg/space/point3.h>

using namespace vcg;
using namespace std;

#include "CubeMapSamp.h"
#include "OctaMapSamp.h"

#include "Mol.h"
#include "AO.h"

const float infty=1000;

vector<bool> tmpbool(32*32,false);

void AO::PrintBuffer(){
  int target=32;
  int k=0;
  for (int y=0; y<target; y++){
    for (int x=0; x<target; x++) {
      double b=buf[k];
      if (b==infty) 
      printf("%2s","*");
      else 
      printf("%2s","-");
      if (tmpbool[k]) printf("'"); else printf(" ");

      k++;
//      printf("%7.3f ",buf[k++]);
    }
    printf("\n");
  }
}

void AO::RenderSphere(float cx, float cy, float cz, float rad){
  printf("Rendering %f %f %f %f...\n",cx,cy,cz,rad);
    /*cx*=bufscale;
    cy*=bufscale;
    rad*=bufscale;*/
    int cxi=int(cx);
    int cyi=int(cy);
    
    for (int y=-(int)rad; y<=(int)rad; y++) 
    for (int x=-(int)rad; x<=(int)rad; x++) 
    {
      float tmp=(-x*x-y*y+rad*rad);
      if (tmp>0) {
          tmp=sqrt(tmp)+cz;
          int i=index(x+cxi,y+cyi);
          if (buf[i]>tmp) buf[i]=tmp;
          //buf[i]=0;
      }
    }
}


void AO::CheckAtom(QAtom &a){

   int n=a.s.nsamp();
   for (int i=0; i<n; i++) {
      Point3f f=a.s.dirrot[i]*a.trr;
      
      if (f[2]>0) {
        
        
        int bx=(int) (a.trp[0]+f[0]);
        int by=(int) (a.trp[1]+f[1]);
        tmpbool[index(bx,by)]=true;;
        if (buf[index(bx,by)] == infty ) {
          a.s.sum[i]+=f[2];
        };
        a.s.div[i]+=f[2];
      }
   }
}


AO::AO( Point3f _dir, Mol &m) {
  
  dir=_dir.Normalize();
  
  // orthonormal basis
  Point3f ax,ay,az=dir;
  ax=az^Point3f(1,0,0);
  if (ax.SquaredNorm()<0.1) ax=az^Point3f(0,1,0);
  ax=ax.Normalize();
  ay=(az^ax).Normalize();
  
  // project...
  m.Transform(ax,ay,az);
  
  
  int target=32; // 
  bufx=bufy=target;
  float bufscalex=target/(m.tx1-m.tx0);
  float bufscaley=target/(m.ty1-m.ty0);
  bufscale=(bufscalex<bufscaley)?bufscalex:bufscaley;
                
  m.ScaleTransl(bufscale);
  CubeMapSamp::Transform(ax,ay,az);
  
  printf("Scale=%f\n",bufscale);

  buf.resize(target*target,infty);
  
  for (int i=0; i<m.atom.size()-1; i++) {
    QAtom &a=m.atom[i];
    CheckAtom(a);
    RenderSphere( a.trp[0], a.trp[1], a.trp[2], a.trr );
    PrintBuffer();
  }
  
  
}
