
#include <wx/log.h>
#include <wx/string.h>
#include <wx/tokenzr.h>

#include <GL/glew.h>

typedef unsigned char Byte;

#include <vector>
#include <string>
#include <algorithm>

#include <vcg/space/point3.h>
#include <vcg/space/color4.h>

using namespace vcg;
using namespace std;
#include "CubeMapSamp.h"
#include "OctaMapSamp.h"
#include "Mol.h"
#include "HardSettings.h"

#include "Progress.h"
#include "AtomColor.h"

#include "MyCanvas.h"
#include "MyTab.h"

#include "CgUtil.h"

#include "Common.h"

float stick_radius;

static int lx=0,ly=0;
extern int BSIZE;
extern int CSIZE; // number of texels for a patch of an aotm

int BSIZEx, BSIZEy; // number of texels for a pach of a bond
int SubPatchX, SubPatchY; 
    // an atom size is subdivided in this many subpatches for bonds



#define TOO_BIG 0
#define TOO_SMALL 1
#define SIZE_OK 2


Mol::Mol()
{
    vboNorm=vboShadow=vboAO=666; // not ready
    vboNormSt=vboShadowSt=vboAOSt=666; // not ready
    filename[0]=0;
    AOdoneLvl=0;
    ready=false;
    natm = nhetatm = 0;
    //DL_bonds = DL_atoms = 666;
    colMode=1.0;
    
    // Support a ten thousand chains for now
    for (int i = 0; i < 10000; i++)
        chainColors[i] = 1; // 1 is used to indicate no set chain color
    
    // View related
    haveDefaultView = false;
    defaultViewRotation[0] = 1.0;
    defaultViewRotation[1] = 0.0;
    defaultViewRotation[2] = 0.0;
    defaultViewRotation[3] = 0.0;
}

// how many texels per patch?
int SetCsize(int textsize, int natoms){
  
  // initial guess:
  int i=(int)ceil(sqrt((double)natoms));
  BSIZE=CSIZE= textsize / i;
  
  if (CSIZE>250)  { 
    BSIZE=CSIZE=250;
    return TOO_BIG;
  }
  
  if (CSIZE<6)  { 
    return TOO_SMALL;
  }
  
  return SIZE_OK;
}

bool QAtom::AssignNextTextPos(int texsize){
  
  
  if (texsize<0) { lx=ly=0; return true;};

  tx=lx;
  ty=ly;
  
  if ((lx+s.TotTexSizeX()>texsize) || (ly+s.TotTexSizeY()>texsize)) return false;
  
  lx+=s.TotTexSizeX(); 
  if (lx+s.TotTexSizeX()>texsize) {
    ly+=s.TotTexSizeY();
    lx=0;
  }
  
  return true;
}

bool Bond::AssignNextTextPos(int texsize){
  if (texsize<0) { lx=ly=0; return true;};
    
  tx=lx;
  ty=ly;
    
  if ((lx+BSIZE>texsize) || (ly+CSIZE>texsize)) return false;
    
  lx+=BSIZE; 
  if (lx+BSIZE>texsize)  {
    ly+=CSIZE;
    lx=0;
  }
  return true;
}

bool Mol::ReassignTexture(int textsize) {
  // reset texture 
  atom[0].AssignNextTextPos( -1 );  
    

  // assign texture positions
  for (int i=0; i<atom.size(); i++) {
    if (!atom[i].AssignNextTextPos( textsize )) return false;
  }

  if (sticks)
  for (int i=0; i<bond.size(); i++) {
    if (!bond[i].AssignNextTextPos( textsize )) return false;
  }
    
  return true;
  /*for (int i=0; i<atom.size(); i++)
  atom[i].FillTexture(texture, textsize);*/
  //printf("Texture Filled!\n");
}

extern CgUtil cgSettings;

void Mol::ReassignTextureAutosize() {
  if (textureAssigned) return;
  
  /* 
  // JUST A TEST:
  if (sticks) {
    BSIZE=CSIZE=5;
  }
  else {
    BSIZE=CSIZE=10;
  }
      CubeMapSamp::SetSize(CSIZE); 
    OctaMapSamp::SetSize(CSIZE);
    moltextureCanvas.SetRes(1024);
    ReassignTexture(1024);

  textureAssigned=true;
  return;
  */
  
  int nEl = atom.size();
  if (sticks) nEl+= bond.size();
  
  int guess = hardSettings.TSIZE;
  
  int lastThatWorked = guess;
  
  bool enlarge=false, shrink=false, forced=false;
  
  do {

    if (enlarge && shrink) forced=true;
     
    moltextureCanvas.SetRes(guess);
    
    /*
    if (guess != hardSettings.TSIZE)
    if (!forced) 
    if (!moltextureCanvas.Test()) {
      // use this res!
      guess = lastThatWorked ;
      forced=true;
      continue;
    }
    */
    
    lastThatWorked=guess;
    
    int res= SetCsize(guess, nEl);
  
    if (!forced) {
      
      if ((res==TOO_BIG) && (guess/2>=16)) {
        shrink=true;
        guess/=2;
        continue;
      } 

      if ((res==TOO_SMALL)&& (guess*2<=hardSettings.MAX_TSIZE)) {
        enlarge=true;
        guess*=2;
        continue;
      } 
    }
    
    CubeMapSamp::SetSize(CSIZE); 
    OctaMapSamp::SetSize(CSIZE);
    
    if (!ReassignTexture(guess)) {
      // should never happen
    }
    
    break;
  } while (1);
  

}

Bond::Bond(const QAtom &_a,const QAtom &_b):
atmA(&_a), atmB(&_b)
{
  
  
  a=_a.P();
  b=_b.P();
  
  dir=(a-b).Normalize();
  
  float rada= _a.covalentr;
  float radb= _b.covalentr;
  
  /*a-=dir*(rada*0.60);
  b+=dir*(radb*0.60);*/
  lenght=(a-b).Norm();
  startp=dir^Point3f(0,0,1);
  if (startp.SquaredNorm()<0.1) startp=dir^Point3f(0,1,0);
  startp.Normalize();
  
  hetatomFlag=_a.hetatomFlag || _b.hetatomFlag;
  
  UpdateColors();
  
}


void Mol::AddBond(int i, int j)
{
   bond.push_back( Bond( atom[i], atom[j] ) );
}
      
void Mol::FindBonds(){
  /*
  // (DRAMATICALLY) QUADRATIC VERSION
  for (int i=0; i<atom.size(); i++)
  for (int j=0; j<i; j++) {
    
    const float mind=0.4;
    float maxd=atom[i].covalentr+atom[j].covalentr+0.56;
    float dist=(atom[i].P()-atom[j].P()).SquaredNorm();
    if ( (dist>=mind*mind) && (dist<=maxd*maxd) ) {
      bond.push_back( Bond( atom[i].P(), atom[j].P(), 
      atom[i].covalentr, atom[j].covalentr,
      Point3f(atom[i].cr,atom[i].cg,atom[i].cb), 
      Point3f(atom[j].cr,atom[j].cg,atom[j].cb)
      ) );
    }
  }
  */
  
  // (HOPEFULLY) PSEUDO-LINEAR VERSION
  
  // sort, then find bonds
  const float MIND=0.4;
  const float MAXD=MAX_COVALENT_RADIUS*2+0.56;

  bool showprogress=atom.size()>2000;
  
  if (showprogress) StartProgress("Locating Bonds",atom.size() );
  
  // Sort atoms per x coordinate
  std::sort( atom.begin(), atom.end() );
  
  
  int st=0; // start interval
  for (int i=0; i<atom.size(); i++) {
    if (showprogress) if (i%100) if (!UpdateProgress(i)) {
      bond.clear();
      //SetSpaceFill();
      return;
    };
    float px=atom[i].px;
    for (int j=st; j<atom.size(); j++) {
      if (atom[j].px < px-MAXD) st=j; // move interval forward
      else if (atom[j].px > px ) break; // no more atoms
      else {
         float maxd=atom[i].covalentr+atom[j].covalentr+0.56;
         float dist=(atom[i].P()-atom[j].P()).SquaredNorm();
         if ( (dist>=MIND*MIND) && (dist<=maxd*maxd) ) 
         if ( // one way check
              /*(atom[j].px != px ) || 
              (atom[j].py < atom[i].py ) || 
              ( (atom[j].py == atom[i].py ) && (atom[j].pz < atom[i].pz ) ) */
              i>j
            )
          AddBond(i,j); 
      }
    }
  }
    
  
  if (showprogress) EndProgress();
  printf("%d bonds detected!\n",bond.size() );
}

void Mol::SetSpaceFill(){
  if (sticks) textureAssigned=false;
  sticks=false;

  ReassignTextureAutosize();
  
  for (int i=0; i<atom.size(); i++)  atom[i].r=atom[i].spacefillr;
}

void Mol::SetBallAndSticks(float radius){
  if (bond.size()==0) FindBonds();

  if (!sticks) {
    sticks=true;
    textureAssigned=false;
    UpdateColors(); // updata colori sticks
  }
    
  ReassignTextureAutosize();
  
  for (int i=0; i<atom.size(); i++) {
    atom[i].r=atom[i].covalentr;
    if (atom[i].r<radius)  atom[i].r=radius;
  }
  stick_radius=radius;
}

void Mol::SetLicorice(float radius){
  if (bond.size()==0)  FindBonds();
  
  if (!sticks) {
    sticks=true;
    textureAssigned=false;
    UpdateColors(); // updata colori sticks
  }

  ReassignTextureAutosize();
    
  for (int i=0; i<atom.size(); i++)  atom[i].r=radius;
  stick_radius=radius;
}


void Mol::Transform(const Point3f &ax,const  Point3f &ay,const Point3f &az){
    atom[0].Transform(ax,ay,az);
    tx0=atom[0].trp[0]-atom[0].r;
    tx1=atom[0].trp[0]+atom[0].r;
    ty0=atom[0].trp[1]-atom[0].r;
    ty1=atom[0].trp[1]+atom[0].r;
    for (int i=1; i<atom.size(); i++) {
      atom[i].Transform(ax,ay,az);
      // update bounding box
      if (atom[i].trp[0]-atom[i].r<tx0) tx0=atom[i].trp[0]-atom[i].r;
      if (atom[i].trp[1]-atom[i].r<ty0) ty0=atom[i].trp[1]-atom[i].r;
      if (atom[i].trp[0]+atom[i].r>tx1) tx1=atom[i].trp[0]+atom[i].r;
      if (atom[i].trp[1]+atom[i].r>ty1) ty1=atom[i].trp[1]+atom[i].r;
    }
    sort(atom.begin(), atom.end() );
} 

void Mol::DuplicateTexels(vector<Byte> &t, int texsize){
    for (int i=0; i<atom.size(); i++) {
      atom[i].s.DuplicateTexels(t, texsize, atom[i].tx, atom[i].ty);
    }
}


// color from atom name
void QAtom::getCol(const char* st){
  atomColor=getAtomColor(st);
}

/*  
void QAtom::getCol(const char* st){
    int tmp=st[0]*4123+st[1]*1242+st[2]*4561+3141*st[3];
    tmp%=155;
    double hue=tmp/155.0;
    if (hue<0.5) {cg=hue*2; cr=1.0-cg; cb=0;}
    else { cr=0; cb=(hue-0.5)*2; cg=1.0-cb;  }
    const float W=0.70;
    cr=cr*(1-W)+W;
    cg=cg*(1-W)+W;
    cb=cb*(1-W)+W;
}
*/

// Helper function: 
// Parse a line of the PDB file with the CONECT info
// Obviously atom id are 1 based indexes.
static void AddTmpBonds(string st, vector<int> &v)
{
  int startAtom=atoi( st.substr(6,5).c_str());
	// assert(startAtom >0 && (startAtom-1)<atom.size());  // this assert cannot be used anymore from a static method
	int i=1;
	while(st.size()>6+i*5+4 && isdigit(st[6+i*5+4]))
	{
	 //	printf("'%s' -> '%s' (%c)\n",st.substr(6,5).c_str(),st.substr(6+i*5,5).c_str(),st[6+i*5+4]);
	 int secondAtom=atoi( st.substr(6+i*5,5).c_str());
	 //printf("(%i) CONECT %i -> %i\n",i,startAtom-1,secondAtom-1);
	 ++i;
	 v.push_back(startAtom-1);
	 v.push_back(secondAtom-1);
	 //AddBond(startAtom-1,secondAtom-1);
	}
//	printf("Found %i conect\n",i);
}

bool Mol::ReadPdb(const char* _filename){

    ready = false;
  
    sprintf(filename, "%s", _filename);
    FILE* f = fopen(filename,"r");
    if (!f) {
        sprintf(QAtom::lastReadError, "Error reding %s:\ncould not open file\n",
                filename);
        return false;
    }
    
    long size = 0;
    if (fseek(f, 0, SEEK_END)==0)
        size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    bool showprogress = (size == 0) || (size > 1000000);
    if (showprogress)
        StartProgress("Reading file", size);
    
    char buf[82]; buf[81] = 0;
    int lineN = 0;
    vector<int> tmpBondVec;

    // -1: Use ATOM record chain identifiers
    // >0: Use TER record serial numbers as chain identifiers (for NE1)
    int chainIndex = -1;
    
    // REMARK 7 DISPLAY_STYLE value
    wxString displayStyle = "";
    
    textureAssigned = false;
    QAtom::readError = false;
    
    atom.clear();
    bond.clear();

    while (1) {
        if (!fgets(buf,81,f))
            break;
        lineN++;
        if ((lineN % 1000) == 0) if (size!=0) if (showprogress) {  
            if (!UpdateProgress((int)ftell(f))) return false;  
        }
        wxString st(buf); // piotr 080318
        if ( (strcmp( st.substr(0,6).c_str(), "ATOM  ") == 0 ) || 
             (strcmp( st.substr(0,6).c_str(), "HETATM") == 0 ) ) {
            atom.push_back(QAtom(std::string(st.c_str()), chainIndex)); // piotr 080318
            if (QAtom::readError) {
                sprintf(QAtom::lastReadError,"Error reading %s!\nLine %d: %s",filename,lineN,&(st[0]));
                if (showprogress) EndProgress();
                    return false;
            }
        }
        
        // Chain TER-minator
        // TER       1          A
        if ((st.length() > 21) && (st.substr(0, 4) == "TER "))
            if (chainIndex > 0)
                chainIndex++;
        
        if (strcmp(st.substr(0, 6).c_str(), "CONECT") == 0)
            AddTmpBonds(std::string(st.c_str()), tmpBondVec); // piotr 080318


        if ((st.length() > 10) && (st.substr(0, 10) == "REMARK   7")) {
            
            // Read default view orientation quaternion
            //   REMARK   7 ORIENTATION: 0.000000 0.000000 -1.000000 0.000000
            //
            if ((st.length() > 22) &&
                (st.substr(11, 12) == "ORIENTATION:")) {
                wxString dataLine = st.substr(23).c_str();
                wxStringTokenizer tokenizer(dataLine);
                if (tokenizer.CountTokens() == 4) {
                    defaultViewRotation[0] =
                        atof(tokenizer.GetNextToken().c_str());
                    defaultViewRotation[1] =
                        atof(tokenizer.GetNextToken().c_str());
                    defaultViewRotation[2] =
                        atof(tokenizer.GetNextToken().c_str());
                    defaultViewRotation[3] =
                        atof(tokenizer.GetNextToken().c_str());
                    haveDefaultView = true;
                }
            }
            
            // Read default view scale
            //   REMARK   7 SCALE: 183.270221
            //
            if ((st.length() > 16) &&
                (st.substr(11, 6) == "SCALE:")) {
                r = atof(st.substr(17).c_str());
                haveDefaultView = true;
            }
            
            // Read default view scene center
            //   REMARK   7 POINT_OF_VIEW: -118.925325 -111.553805 1.202609
            //
            if ((st.length() > 24) &&
                (st.substr(11, 14) == "POINT_OF_VIEW:")) {
                wxString dataLine = st.substr(25).c_str();
                wxStringTokenizer tokenizer(dataLine);
                if (tokenizer.CountTokens() == 3) {
                    px = -1 * atof(tokenizer.GetNextToken().c_str());
                    py = -1 * atof(tokenizer.GetNextToken().c_str());
                    pz = -1 * atof(tokenizer.GetNextToken().c_str());
                    haveDefaultView = true;
                }
            }

            // Read tubes display style bond radius
            //             1         2         3         4         5
            //   012345678901234567890123456789012345678901234567890123456789
            //   REMARK   7 BACKGROUND_COLOR: 255   0   0
            //  or
            //   REMARK   7 BACKGROUND_COLOR: SkyBlue
            //
            if ((st.length() > 30) &&
                (st.substr(11, 17) == "BACKGROUND_COLOR:")) {
                wxStringTokenizer tokenizer(st.substr(28));
                int red, green, blue;
                red = green = blue = -1;
                if (tokenizer.CountTokens() == 3) { // RGB color specified
                    red = atoi(tokenizer.GetNextToken().c_str());
                    green = atoi(tokenizer.GetNextToken().c_str());
                    blue = atoi(tokenizer.GetNextToken().c_str());
                    
                } else {
                    wxString colorName = tokenizer.GetNextToken();
                    if (colorName == "SkyBlue") {
                        red = 127;
                        green = 199;
                        blue = 247;
                    }
                }
                if (red > -1)
                    MyTab::setSceneBgcolor(wxColor(red, green, blue));
            }

            // Read tubes display style bond radius
            //   REMARK   7 TUBES_BOND_RADIUS: 0.300
            //
            if ((st.length() > 30) &&
                (st.substr(11, 18) == "TUBES_BOND_RADIUS:")) {
                geoSettings.licoRadius = atof(st.substr(30).c_str());
            }

            // Read ball and stick display style bond radius
            //   REMARK   7 BALL_AND_STICK_BOND_RADIUS: 0.300
            //
            if ((st.length() > 39) &&
                (st.substr(11, 27) == "BALL_AND_STICK_BOND_RADIUS:")) {
                geoSettings.stickRadius = atof(st.substr(39).c_str());
            }

            // Read display style
            //   REMARK   7 DISPLAY_STYLE: tub
            //
            // Display style names:"def", "inv", "cpk", "lin", "bas", "tub"
            //
            if ((st.length() > 28) &&
                (st.substr(11, 14) == "DISPLAY_STYLE:")) {
                displayStyle = st.substr(26, 3);
                if (displayStyle == "bas")
                    geoSettings.mode = GeoSettings::BALL_N_STICKS;
                    
                else if (displayStyle == "tub")
                    geoSettings.mode = GeoSettings::LICORICE;
                    
                else if (displayStyle == "cpk")
                    geoSettings.mode = GeoSettings::SPACE_FILL;
           }


            // Read chain information from records like this:
            //   REMARK   7 CHAIN: 10  DISPLAY_STYLE: Default  COLOR: 0 170 255  NAME: "11"
            //
            if ((st.length() > 16) &&
                (st.substr(11, 6) == "CHAIN:")) {
                wxString dataLine = st.substr(18);
                wxStringTokenizer tokenizer(dataLine);
                if (tokenizer.CountTokens() > 6) { // If the chain has a color
                    int _chainIndex = atoi(tokenizer.GetNextToken().c_str());
                    tokenizer.GetNextToken(); // DISPLAY_STYLE:
                    wxString chainDisplayStyle = tokenizer.GetNextToken();
                    tokenizer.GetNextToken(); // COLOR:
                    int red = atoi(tokenizer.GetNextToken().c_str());
                    int green = atoi(tokenizer.GetNextToken().c_str());
                    int blue = atoi(tokenizer.GetNextToken().c_str());
                    // int color = 0xFFRRGGBB;
                    int color = 0xff000000 + (red<<16) + (green<<8) + blue;
                    chainColors[_chainIndex] = color;
                    SetColMode(0); // Color chains
                    chainIndex = 1;
                    
                    // For some reason, when writing DNA strands, NE1 puts "tub"
                    // for the global display style when the display style is
                    // really "cpk" or "bas" (ball and stick) It does write
                    // "cpk" or "bas" correctly for
                    // the chain display styles however, so we check the first
                    // one here and update the global display style if it's
                    // differnt.
                    //
                    if ((_chainIndex == 1) && (displayStyle == "tub"))
                        if (chainDisplayStyle == "bas")
                            geoSettings.mode = GeoSettings::BALL_N_STICKS;
                            
                        else if (chainDisplayStyle == "cpk")
                            geoSettings.mode = GeoSettings::SPACE_FILL;
                }
            }
        }
        
        if ((st.length() > 10) && (st.substr(0, 10) == "REMARK   8")) {
            wxString dataLine = st.substr(11);
            wxStringTokenizer tokenizer(dataLine);
            if (tokenizer.CountTokens() > 6) {
                wxString atomName = tokenizer.GetNextToken();
                if (atomName[0] != ';') { // Ignore comment lines
                    int atomNumber = atoi(tokenizer.GetNextToken().c_str());
                    float cpkRadius = atof(tokenizer.GetNextToken().c_str());
                    float ballStickRadius =
                        atof(tokenizer.GetNextToken().c_str());
                    int red = atoi(tokenizer.GetNextToken().c_str());
                    int green = atoi(tokenizer.GetNextToken().c_str());
                    int blue = atoi(tokenizer.GetNextToken().c_str());

                    // Prepend single letter atom names with a space.
                    if (atomName.length() == 1) 
                        atomName = wxString(" ").append(atomName); // piotr 080318

                    addAtomType((char*)(atomName.c_str()), atomNumber,
                                cpkRadius, ballStickRadius,
                                red, green, blue);
                }
            }
        }
    }
    
    nhetatm=0;  natm=0;
    for (int i=0; i<atom.size(); i++){
      if (atom[i].hetatomFlag)  nhetatm++; else natm++;
    }

	haveDefaultView = false;
	
    if (!haveDefaultView)
        ComputeSize();

    UpdateColors();
     
    for (int i=0; i<tmpBondVec.size(); i+=2) {
      AddBond(tmpBondVec[i],tmpBondVec[i+1]);
    }

    if (showprogress) EndProgress();
    //if (sticks) FindBonds();
    
    //ReassignTextureAutosize();

    //SetCsize(hardSettings.TSIZE, atom.size()  *21 / 10   ); // approx 2.1 bonds per atom
    
    ready=true;
    ResetAO();
    return true;
}

char* Mol::GetFilenameTex(){
  static char res[1024];
  sprintf(res,"%s.ppm",filename);
  return res;
}

char* Mol::GetFilenameSnap(){
  static char res[2048];
  sprintf(res,"%s",filename);
  // REMOVE PATH: quick and dirty: find last '/'
  int i=0, pos=-1;
  while (res[i]) {
      if ((res[i]=='\\') || (res[i]=='/')) pos=i;
    i++;
  }
  return res+pos+1;
  return filename;
}

char* Mol::GetMolName(){
  static char res[2048];
  sprintf(res,"%s",filename);
  // REMOVE PATH: quick and dirty: find last '/'
  int i=0, pos=-1;
  while (res[i]) {
      if ((res[i]=='\\') || (res[i]=='/')) pos=i;
    i++;
  }
  return res+pos+1;
  return filename;
}
  
void Mol::ComputeSize(){
    // bounding box!
    float x0,y0,z0,x1,y1,z1;
    if (atom.size()>0)
    x0=x1=atom[0].px;
    y0=y1=atom[0].py;
    z0=z1=atom[0].pz;
    for (int i=1; i<atom.size(); i++) {
      if (x1>atom[i].px) x1=atom[i].px;
      if (y1>atom[i].py) y1=atom[i].py;
      if (z1>atom[i].pz) z1=atom[i].pz;
      if (x0<atom[i].px) x0=atom[i].px;
      if (y0<atom[i].py) y0=atom[i].py;
      if (z0<atom[i].pz) z0=atom[i].pz;
    }
    px=(x0+x1)/2;
    py=(y0+y1)/2;
    pz=(z0+z1)/2;
    int k=-4;
    r=sqrt( (x1-x0+k)*(x1-x0+k) + (y1-y0+k)*(y1-y0+k) + (z1-z0+k)*(z1-z0+k) );
    r*=0.5;
    
    //printf("pos=(%f %f %f) size=%f\n",px,py,pz,r);

}

void mysscanf(const char* st, const char* format, float *f){
  if (!sscanf( st, "%f", f)) {
    if (sscanf( st, " - %f", f))
    *f=-*f; 
    else  *f=1.0;
  }
}

void Mol::FillTexture(vector<Byte> &texture, const vector<int> &sumtable, 
                   int texsize, float div )
{
  /*
    for (int i=0; i<atom.size(); i++) 
    atom[i].s.FillTexture(
        texture, sumtable, 
        texsize, div , atom[i].tx, atom[i].ty  );
  */
}




void Bond::UpdateColors(){
  col1=Point3f(atmA->cr,atmA->cg,atmA->cb);
  col2=Point3f(atmB->cr,atmB->cg,atmB->cb);
}


void QAtom::UpdateColors(float mode, int chainColor) {

    if ((chainColor < 1) && (mode < 0.0025)) {
        // Use specified chain color. Chain colors are encoded like this:
        // int color = 0xff000000 + (red<<16) + (green<<8) + blue; // 0xFFRRGGBB
        chainColor -= 0xff000000;
        cr = (chainColor>>16) / 255.0f;
        cg = ((chainColor & 0x00FF00)>>8) / 255.0f;
        cb = (chainColor & 0x0000FF) / 255.0f;
        
    } else {
        Color4b ca,cc;
  
        *((int *)&ca )= atomColor;
    
        *((int *)&cc )= getChainColor( chainIndex );
  

        cb=(float(ca[0])/255.0f)*mode+ (float(cc[0])/255.0f) * (1.0f-mode);
        cg=(float(ca[1])/255.0f)*mode+ (float(cc[1])/255.0f) * (1.0f-mode);
        cr=(float(ca[2])/255.0f)*mode+ (float(cc[2])/255.0f) * (1.0f-mode);
    }
}


void Mol::UpdateColors(){
  for (int i=0; i<atom.size(); i++){
    atom[i].UpdateColors(colMode, chainColors[atom[i].chainIndex]);
  }
  
  if (sticks)
  for (int i=0; i<bond.size(); i++) {
    bond[i].UpdateColors();
  } 
}

void Mol::SetColMode(float newColMode){
  if (colMode!=newColMode) {
    colMode=newColMode;
    UpdateColors();
  }
  else colMode=newColMode;
}

bool QAtom::readError=false;
char QAtom::lastReadError[1024];



QAtom::QAtom(string st, int chainIndex) {

 // PDB Specification: Columns 13-16: Atom name
 string elem = st.substr( 12, 4);
 
 // Internal convention: Atom names are uppercase and trimmed except for single
 // letter atom names which are preceded by a space. Eg, " C", "SI"
 //
 // Trim front.
 while ((elem.length() != 0) && (elem[0] == ' '))
    elem.erase(0, 1);
    
 // Trim end.
 while ((elem.length() != 0) && (elem[elem.length() - 1] == ' '))
    elem.erase(elem.length() - 1, 1);
    
 // Pad single character atom name with a space
 if (elem.length() == 1)
    elem = string(" ").append(elem);
    
 // Convert to uppercase
 for (int index = 0; index < elem.length(); index++)
    elem[index] = toupper(elem[index]);
 
 if (strcmp( st.substr(0,6).c_str(), "ATOM  ") == 0 ) 
 {
    hetatomFlag=false;             

    getCol( elem.c_str() );
    mysscanf(st.substr( 30, 8).c_str(),"%f", &px);
    mysscanf(st.substr( 38, 8).c_str(),"%f", &py);
    mysscanf(st.substr( 46, 8).c_str(),"%f", &pz);
    
    if (chainIndex > 0)
        this->chainIndex = chainIndex; // Use the given (NE1) chain index
    else
        this->chainIndex = (int)st[22]; // Use the ATOM record chain identifier

    
    r=spacefillr=getAtomRadius(elem.c_str()); //  Van der Waals radii
    covalentr=getAtomCovalentRadius(elem.c_str()); 
  }
  else if (strcmp( st.substr(0,6).c_str(), "HETATM") == 0 ) 
  {
    hetatomFlag=true;

    getCol( elem.c_str() );
    mysscanf(st.substr( 30, 8).c_str(),"%f", &px);
    mysscanf(st.substr( 38, 8).c_str(),"%f", &py);
    mysscanf(st.substr( 46, 8).c_str(),"%f", &pz);
    
    this->chainIndex = (int) st[22];

    r=spacefillr=getAtomRadius(elem.c_str()); //  Van der Waals radii
    covalentr=getAtomCovalentRadius(elem.c_str()); 
  }
  covalentr*=0.85; // mystical value!!!
}


/*
 * FUNCTION: hasDefaultView
 */
bool Mol::hasDefaultView() const { return haveDefaultView; }


/*
 * FUNCTION: getDefaultViewRotation
 */
void Mol::getDefaultViewRotation
        (float* angle, float* axisX, float* axisY, float* axisZ) const {
	float scale =
        sqrt(defaultViewRotation[1] * defaultViewRotation[1] +
             defaultViewRotation[2] * defaultViewRotation[2] +
             defaultViewRotation[3] * defaultViewRotation[3]);
	if (scale<1e-8) scale = 1.0;		 
	*axisX = defaultViewRotation[1] / scale;
	*axisY = defaultViewRotation[2] / scale;
	*axisZ = defaultViewRotation[3] / scale;
	*angle = (360 * acos(defaultViewRotation[0]) * 2.0f) / (2 * 3.14159);
}
