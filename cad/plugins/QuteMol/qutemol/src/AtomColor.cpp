
#include <wx/log.h>

#include <map>
#include <string>
using namespace std;

#include "AtomColor.h"

static std::map<std::string,float> E2RC; // covalent radius
static std::map<std::string,float> E2R; // radius
static std::map<std::string,int> E2C;  // colors



static void InitTables(){
  if(E2RC.size()==0)
  {
    /// according to http://www.umass.edu/microbio/rasmol/rasbonds.htm
    E2RC[" H"]=   0.320f; 
    E2RC[" C"]=   0.720f; 
    E2RC[" N"]=   0.680f;
    E2RC[" O"]=   0.680f;
    E2RC[" P"]=   1.036f;
    E2RC[" S"]= 	1.020f;
    E2RC["CA"]= 	0.992f;
    E2RC["FE"]= 	1.420f;
    E2RC["ZN"]= 	1.448f;
    E2RC["CD"]= 	1.688f;  // What is CD anyway? 
    E2RC[" I"]= 	1.400f;
  }

  if(E2R.size()==0)
  {    
    // according to http://www.imb-jena.de/ImgLibDoc/glossary/IMAGE_VDWR.html 
    //E2R["H"]=  	1.20f;
    //E2R["C"]= 	1.70f;
    //E2R["N"]= 	1.55f;
    //E2R["O"]= 	1.52f;
    E2R[" F"]= 	1.47f;
    //E2R["P"]= 	1.80f;
    //E2R["S"]= 	1.80f;
    E2R["CL"]= 	1.89f;

    /// according to http://www.umass.edu/microbio/rasmol/rasbonds.htm
    E2R[" H"]=   1.100f; 
    E2R[" C"]=   1.548f; // was changed to 1.400 for some reason 1.548 is the reported value
    E2R[" N"]=   1.400f;
    E2R[" O"]=   1.348f;
    E2R[" P"]=   1.880f;
    E2R[" S"]= 	1.808f;
    E2R["CA"]= 	1.948f;
    E2R["FE"]= 	1.948f;
    E2R["ZN"]= 	1.148f;
    E2R["CD"]= 	1.748f; 
    E2R[" I"]= 	1.748f;
  }
  
  if(E2C.size()==0)
{
E2C[" H"] = /*[255,255,255]*/ 0xFFFFFF  	/* 0xFFFFFF			*/  	;
E2C["HE"]= /*[217,255,255]*/ 0xFFC0CB  	/* 0xD9FFFF			*/  	;
E2C["LI"]= /*[204,128,255]*/ 0xB22222  	/* 0xCC80FF			*/  	;
E2C["BE"]= /*[194,255,  0]*/ 0xFF1493  	/* 0xC2FF00			*/  	;
E2C[" B"] = /*[255,181,181]*/ 0x00FF00  	/* 0xFFB5B5			*/  	;
E2C[" C"] = /*[144,144,144]*/ 0x808080  	/* 0x909090			*/  	;
E2C[" N"] = /*[ 48, 80,248]*/ 0x8F8FFF  	/* 0x3050F8			*/  	;
E2C[" O"] = /*[255, 13, 13]*/ 0xF00000  	/* 0xFF0D0D			*/  	;
E2C[" F"] = /*[144,224, 80]*/ 0xDAA520  	/* 0x90E050			*/  	;
E2C["NE"]= /*[179,227,245]*/ 0xFF1493  	/* 0xB3E3F5			*/  	;
E2C["NA"]= /*[171, 92,242]*/ 0x0000FF  	/* 0xAB5CF2			*/  	;
E2C["MG"]= /*[138,255,  0]*/ 0x228B22  	/* 0x8AFF00			*/  	;
E2C["AL"]= /*[191,166,166]*/ 0x808090  	/* 0xBFA6A6			*/  	;
E2C["SI"]= /*[240,200,160]*/ 0xDAA520  	/* 0xF0C8A0			*/  	;
E2C[" P"] = /*[255,128,  0]*/ 0xFFA500  	/* 0xFF8000			*/  	;
E2C[" S"] = /*[255,255, 48]*/ 0xFFC832  	/* 0xFFFF30			*/  	;
E2C["CL"]= /*[ 31,240, 31]*/ 0x00FF00  	/* 0x1FF01F			*/  	;
E2C["AR"]= /*[128,209,227]*/ 0xFF1493  	/* 0x80D1E3			*/  	;
E2C["K"] = /*[143, 64,212]*/ 0xFF1493  	/* 0x8F40D4			*/  	;
E2C["CA"]= /*[ 61,255,  0]*/ 0x808090  	/* 0x3DFF00			*/  	;
E2C["SC"]= /*[230,230,230]*/ 0xFF1493  	/* 0xE6E6E6			*/  	;
E2C["TI"]= /*[191,194,199]*/ 0x808090  	/* 0xBFC2C7			*/  	;
E2C[" V"] = /*[166,166,171]*/ 0xFF1493  	/* 0xA6A6AB			*/  	;
E2C["CR"]= /*[138,153,199]*/ 0x808090  	/* 0x8A99C7			*/  	;
E2C["MN"]= /*[156,122,199]*/ 0x808090  	/* 0x9C7AC7			*/  	;
E2C["FE"]= /*[224,102, 51]*/ 0xFFA500  	/* 0xE06633			*/  	;
E2C["CO"]= /*[240,144,160]*/ 0xFF1493  	/* 0xF090A0			*/  	;
E2C["NI"]= /*[ 80,208, 80]*/ 0xA52A2A  	/* 0x50D050			*/  	;
E2C["CU"]= /*[200,128, 51]*/ 0xA52A2A  	/* 0xC88033			*/  	;
E2C["ZN"]= /*[125,128,176]*/ 0xA52A2A  	/* 0x7D80B0			*/  	;
E2C["GA"]= /*[194,143,143]*/ 0xFF1493  	/* 0xC28F8F			*/  	;
E2C["GE"]= /*[102,143,143]*/ 0xFF1493  	/* 0x668F8F			*/  	;
E2C["AS"]= /*[189,128,227]*/ 0xFF1493  	/* 0xBD80E3			*/  	;
E2C["SE"]= /*[255,161,  0]*/ 0xFF1493  	/* 0xFFA100			*/  	;
E2C["BR"]= /*[166, 41, 41]*/ 0xA52A2A  	/* 0xA62929			*/  	;
E2C["KR"]= /*[ 92,184,209]*/ 0xFF1493  	/* 0x5CB8D1			*/  	;
E2C["RB"]= /*[112, 46,176]*/ 0xFF1493  	/* 0x702EB0			*/  	;
E2C["SR"]= /*[  0,255,  0]*/ 0xFF1493  	/* 0x00FF00			*/  	;
E2C[" Y"] = /*[148,255,255]*/ 0xFF1493  	/* 0x94FFFF			*/  	;
E2C["ZR"]= /*[148,224,224]*/ 0xFF1493  	/* 0x94E0E0			*/  	;
E2C["NB"]= /*[115,194,201]*/ 0xFF1493  	/* 0x73C2C9			*/  	;
E2C["MO"]= /*[ 84,181,181]*/ 0xFF1493  	/* 0x54B5B5			*/  	;
E2C["TC"]= /*[ 59,158,158]*/ 0xFF1493  	/* 0x3B9E9E			*/  	;
E2C["RU"]= /*[ 36,143,143]*/ 0xFF1493  	/* 0x248F8F			*/  	;
E2C["RH"]= /*[ 10,125,140]*/ 0xFF1493  	/* 0x0A7D8C			*/  	;
E2C["PD"]= /*[  0,105,133]*/ 0xFF1493  	/* 0x006985			*/  	;
E2C["AG"]= /*[192,192,192]*/ 0x808090  	/* 0xC0C0C0			*/  	;
E2C["CD"]= /*[255,217,143]*/ 0xFF1493  	/* 0xFFD98F			*/  	;
E2C["IN"]= /*[166,117,115]*/ 0xFF1493  	/* 0xA67573			*/  	;
E2C["SN"]= /*[102,128,128]*/ 0xFF1493  	/* 0x668080			*/  	;
E2C["SB"]= /*[158, 99,181]*/ 0xFF1493  	/* 0x9E63B5			*/  	;
E2C["TE"]= /*[212,122,  0]*/ 0xFF1493  	/* 0xD47A00			*/  	;
E2C[" I"] = /*[148,  0,148]*/ 0xA020F0  	/* 0x940094			*/  	;
E2C["XE"]= /*[ 66,158,176]*/ 0xFF1493  	/* 0x429EB0			*/  	;
E2C["CS"]= /*[ 87, 23,143]*/ 0xFF1493  	/* 0x57178F			*/  	;
E2C["BA"]= /*[  0,201,  0]*/ 0xFFA500  	/* 0x00C900			*/  	;
E2C["LA"]= /*[112,212,255]*/ 0xFF1493  	/* 0x70D4FF			*/  	;
E2C["CE"]= /*[255,255,199]*/ 0xFF1493  	/* 0xFFFFC7			*/  	;
E2C["PR"]= /*[217,255,199]*/ 0xFF1493  	/* 0xD9FFC7			*/  	;
E2C["ND"]= /*[199,255,199]*/ 0xFF1493  	/* 0xC7FFC7			*/  	;
E2C["PM"]= /*[163,255,199]*/ 0xFF1493  	/* 0xA3FFC7			*/  	;
E2C["SM"]= /*[143,255,199]*/ 0xFF1493  	/* 0x8FFFC7			*/  	;
E2C["EU"]= /*[ 97,255,199]*/ 0xFF1493  	/* 0x61FFC7			*/  	;
E2C["GD"]= /*[ 69,255,199]*/ 0xFF1493  	/* 0x45FFC7			*/  	;
E2C["TB"]= /*[ 48,255,199]*/ 0xFF1493  	/* 0x30FFC7			*/  	;
E2C["DY"]= /*[ 31,255,199]*/ 0xFF1493  	/* 0x1FFFC7			*/  	;
E2C["HO"]= /*[  0,255,156]*/ 0xFF1493  	/* 0x00FF9C			*/  	;
E2C["ER"]= /*[  0,230,117]*/ 0xFF1493  	/* 0x00E675			*/  	;
E2C["TM"]= /*[  0,212, 82]*/ 0xFF1493  	/* 0x00D452			*/  	;
E2C["YB"]= /*[  0,191, 56]*/ 0xFF1493  	/* 0x00BF38			*/  	;
E2C["LU"]= /*[  0,171, 36]*/ 0xFF1493  	/* 0x00AB24			*/  	;
E2C["HF"]= /*[ 77,194,255]*/ 0xFF1493  	/* 0x4DC2FF			*/  	;
E2C["TA"]= /*[ 77,166,255]*/ 0xFF1493  	/* 0x4DA6FF			*/  	;
E2C[" W"] = /*[ 33,148,214]*/ 0xFF1493  	/* 0x2194D6			*/  	;
E2C["RE"]= /*[ 38,125,171]*/ 0xFF1493  	/* 0x267DAB			*/  	;
E2C["OS"]= /*[ 38,102,150]*/ 0xFF1493  	/* 0x266696			*/  	;
E2C["IR"]= /*[ 23, 84,135]*/ 0xFF1493  	/* 0x175487			*/  	;
E2C["PT"]= /*[208,208,224]*/ 0xFF1493  	/* 0xD0D0E0			*/  	;
E2C["AU"]= /*[255,209, 35]*/ 0xDAA520  	/* 0xFFD123			*/  	;
E2C["HG"]= /*[184,184,208]*/ 0xFF1493  	/* 0xB8B8D0			*/  	;
E2C["TL"]= /*[166, 84, 77]*/ 0xFF1493  	/* 0xA6544D			*/  	;
E2C["PB"]= /*[ 87, 89, 97]*/ 0xFF1493  	/* 0x575961			*/  	;
E2C["BI"]= /*[158, 79,181]*/ 0xFF1493  	/* 0x9E4FB5			*/  	;
E2C["PO"]= /*[171, 92,  0]*/ 0xFF1493  	/* 0xAB5C00			*/  	;
E2C["AT"]= /*[117, 79, 69]*/ 0xFF1493  	/* 0x754F45			*/  	;
E2C["RN"]= /*[ 66,130,150]*/ 0xFF1493  	/* 0x428296			*/  	;
E2C["FR"]= /*[ 66,  0,102]*/ 0xFF1493  	/* 0x420066			*/  	;
E2C["RA"]= /*[  0,125,  0]*/ 0xFF1493  	/* 0x007D00			*/  	;
E2C["AC"]= /*[112,171,250]*/ 0xFF1493  	/* 0x70ABFA			*/  	;
E2C["TH"]= /*[  0,186,255]*/ 0xFF1493  	/* 0x00BAFF			*/  	;
E2C["PA"]= /*[  0,161,255]*/ 0xFF1493  	/* 0x00A1FF			*/  	;
E2C[" U"] = /*[  0,143,255]*/ 0xFF1493  	/* 0x008FFF			*/  	;
E2C["NP"]= /*[  0,128,255]*/ 0xFF1493  	/* 0x0080FF			*/  	;
E2C["PU"]= /*[  0,107,255]*/ 0xFF1493  	/* 0x006BFF			*/  	;
E2C["AM"]= /*[ 84, 92,242]*/ 0xFF1493  	/* 0x545CF2			*/  	;
E2C["CM"]= /*[120, 92,227]*/ 0xFF1493  	/* 0x785CE3			*/  	;
E2C["BK"]= /*[138, 79,227]*/ 0xFF1493  	/* 0x8A4FE3			*/  	;
E2C["CF"]= /*[161, 54,212]*/ 0xFF1493  	/* 0xA136D4			*/  	;
E2C["ES"]= /*[179, 31,212]*/ 0xFF1493  	/* 0xB31FD4			*/  	;
E2C["FM"]= /*[179, 31,186]*/ 0xFF1493  	/* 0xB31FBA			*/  	;
E2C["MD"]= /*[179, 13,166]*/ 0xFF1493  	/* 0xB30DA6			*/  	;
E2C["NO"]= /*[189, 13,135]*/ 0xFF1493  	/* 0xBD0D87			*/  	;
E2C["LR"]= /*[199,  0,102]*/ 0xFF1493  	/* 0xC70066			*/  	;
E2C["RF"]= /*[204,  0, 89]*/ 0xFF1493  	/* 0xCC0059			*/  	;
E2C["DB"]= /*[209,  0, 79]*/ 0xFF1493  	/* 0xD1004F			*/  	;
E2C["SG"]= /*[217,  0, 69]*/ 0xFF1493  	/* 0xD90045			*/  	;
E2C["BH"]= /*[224,  0, 56]*/ 0xFF1493  	/* 0xE00038			*/  	;
E2C["HS"]= /*[230,  0, 46]*/ 0xFF1493  	/* 0xE6002E			*/  	;
E2C["MT"]= /*[235,  0, 38]*/ 0xFF1493  	/* 0xEB0026			*/  	;
}                                                          
}

bool addAtomType(char* namei,  int unused, float radius, float radiusC, int r, int g, int b){
  InitTables();
  
  // upperCase(name);
  std::string name(namei);
  int i=0; 
  while (name[i]) { 
    if ((name[i]>='a') && (name[i]<='z')) name[i]=name[i]-'a'+'A'; //else name[i]=namei[i];
    i++; 
  }
  
  if (radius<0.01) radius=0.01;
  E2R[name]=radius;     
  E2C[name]=(r<<16)+(g<<8)+b;
  if (radiusC<0.01) radiusC=0.01;
  E2RC[name]=radiusC;  
  // note: covalent radius does not get updated. If needed, 
  
#if 0 // write a log of added atom types
  static FILE* f=NULL;
  if (f==NULL) { f=fopen("AddedAtomsLog.txt","wt"); };
  fprintf(f,"Added '%s' %d %f %f (%d %d %d)\n",name,unused,radius,radiusR, r,g,b);
  fflush(f);
#endif

  return true;
}


// Adds Pseudo Atoms types used by Nanorex. No longer used as this data is read
// from the ART file now.
/*
static void AddPseudoAtoms(){

 addAtomType("Ax5",	    200 ,	5.0 ,	4.0, 102 ,102 , 204 ); // Axis
 addAtomType("Ae5", 	204 ,	3.5 ,	2.5, 102 ,102 , 204 ); // Axis-end 	
 addAtomType("Ss5", 	201 ,	4.0 ,	3.0, 102 ,204 , 102 ); // Strand sugar 	
 addAtomType("Sj5", 	203 ,	4.0 ,	3.0, 102 ,204 , 204 ); // Strand junction 	
 addAtomType("Pl5", 	202 ,	3.2 ,	2.2, 102 ,26  , 128 ); // Phosphorous link 	
 addAtomType("Pe5", 	205 ,	3.0 ,	2.0, 102 ,26  , 128 ); // Phosphorous end 	
 addAtomType("Sh5", 	206 ,	2.5 ,	1.5, 102 ,204 , 102 ); // Sugar hydroxyl 	
 addAtomType("Hp5", 	207 ,	4.0 ,	3.0, 77  ,179 ,  77 ); // Hairpin 	
 addAtomType(" X", 		0 ,	1.1 ,	0.1, 255*8/10 ,0 ,0 ); // Bondpoint
}
*/


// quick and dirty: reads a line, returns it first 80 chars, skips initial spaces and empty lines
static char* getLine(FILE* f){
  static char res[80];
  int i=0;
  while (1) {
    
    char c=fgetc(f); 
    if (c==EOF) { if (i==0) return NULL; else break;}
    if (c==13 ) { if (i==0) continue; else break; }
    if ((i<80) && (c!=10) && ((i!=0) ||(c!=' ')) ) res[i++]=c;
  }
  res[i]=0; return res;
}

// Reads a Nanorex "ART" file, describing custom atom types.
bool readArtFile(const char* filename){
  InitTables();
  FILE* f=fopen(filename,"rb");
  if (!f) return false;
  while (1) {
    char* line=getLine(f); 
    if (!line) break;
    if (line[0]!='#') {
      char a[100]; int b; float c1,c2; int d,e,f;
      sscanf(line,"%s %d %f %f %d %d %d",a,&b,&c1,&c2,&d,&e,&f);
      
      // Prepend single letter atom names with a space.
      if (strlen(a) == 1) {
        a[2] = a[1];
        a[1] = a[0];
        a[0] = ' ';
      }
      
      addAtomType(a,b,c1,c2,d,e,f); // addAtomType() uppercases the atom name
    }
  }
  fclose(f);
  return true;
}

float getMaxCovelentRadius(){
  return 1.688f;
}




float getAtomRadius(const char* atomicElementCharP)
{
  InitTables();
  //std::string ss0,ss1;
  string atomicElement(atomicElementCharP);
  //ss0=atomicElement.substr(0,1);
  //ss1=atomicElement.substr(0,2);
  float rad=E2R[atomicElement];                                 
  //if(rad==0) rad = E2R[ss0];
  if(rad==0) rad=1.5;
  return rad;
}

float getAtomCovalentRadius(const char* atomicElementCharP){
  InitTables();
  //std::string ss0,ss1;
  string atomicElement(atomicElementCharP);
  //ss0=atomicElement.substr(0,1);
  //ss1=atomicElement.substr(0,2);
  float rad=E2RC[atomicElement];  
                                 
  //if(rad==0) rad = E2RC[ss0];
  
  // HACK: covalent (B&S) radius of undefined atoms is defined as half the SpaceFill rad
  if (rad==0) rad=getAtomRadius(atomicElementCharP)/2.0; 

  return rad;
}

int getAtomColor(const char* atomicElementCharP){
  InitTables();
  string atomicElement(atomicElementCharP);

  //std::string ss0,ss1,ss2;
  //size_t last=std::min(atomicElement.length(),atomicElement.find_first_of(' '));
  //ss0=atomicElement.substr(0,1);
  int color=E2C[atomicElement];                                 
  if(color==0) 
  { 
  //  printf("color 0 for %s\n",ss0.c_str());
    //ss1=atomicElement.substr(0,2);
    //color = 0x000000;
  }
  
  return color+0xff000000;
}


// VERY QUICK AND DIRTY random color schema computation:
// -----------------------------------------------------

static int basecol = 1;

void ChangeColorSchema(int i){
  static int index=3;
  if (i==-1) i=index++;
  
  basecol=i*1231123;
}

bool tooDark(int c){
  return (c&255)+ ((c>>8)&255) + ((c>>16)&255) < 200;
}

int getChainColor(int index) {
  int res = basecol * index * 35634379;
  int antiloop = 0;
  while (tooDark(res) && (antiloop++ < 10) ) {
    res=(res + 1231) * 645633737;
  }
  return res;
}

