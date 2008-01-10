typedef unsigned char Byte;

#include <GL/glew.h>
#include "CgUtil.h"

//#include <GL/gl.h>
#include <math.h>
//#include <GL/glu.h>

#include <vector>

#include <vcg/space/point3.h>
#include <vcg/space/color4.h>

using namespace vcg;
using namespace std;

#include "CubeMapSamp.h"
#include "OctaMapSamp.h"

int CubeMapSamp::size;
int OctaMapSamp::size;

vector<Point3f> CubeMapSamp::dir;
vector<Point3f> CubeMapSamp::dirrot;
vector<int> CubeMapSamp::map;   // mappa 2d di indici a dir
//vector<float> CubeMapSamp::weight;

vector<Point3f> OctaMapSamp::dir;
vector<Point3f> OctaMapSamp::dirrot;
vector<float> OctaMapSamp::weight;

void OctaMapSamp::FillTexture(vector<Byte> &texture, const vector<int> &sumtable, 
                   int texsize, float div, int tx, int ty )
{
    for (int y=0,k=0; y<size; y++) 
    for (int x=0; x<size; x++,k++) 
    {
      int h=(x+tx+(y+ty)*texsize);
      
      int res= (int) ( sumtable[h] * div /** weight[k]*/ );
      if (res>255) res=255;
      texture[h*3+0]= res;
      texture[h*3+1]= res;
      texture[h*3+2]= res; 
     /* if (res<512-275)  {
        texture[h*3+0]= 0;
        texture[h*3+1]= res;
        texture[h*3+2]= res; 
      } else if (res<254) {
        texture[h*3+0]= 0;
        texture[h*3+1]= 255;
        texture[h*3+2]= 0; 
      } else
      if (res>275)  {
      texture[h*3+0]= 255;
      texture[h*3+1]= res-255;
      texture[h*3+2]= res/2-255; } else {
        texture[h*3+0]= res;
       if (res>255) res=255;
       texture[h*3+1]= res;
      texture[h*3+2]= res; 
      }*/
    }
    
}
