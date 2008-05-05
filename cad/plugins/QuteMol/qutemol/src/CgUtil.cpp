#include <GL/glew.h>
#include "CgUtil.h"

#if defined(_WIN32)
#include <windows.h>
#else
#include <string.h>  // for strlen
#endif

//#include <GL/gl.h>
#include <stdio.h>

#include "HardSettings.h"

#include "MyCanvas.h"

extern int CSIZE;
extern int BSIZE;
//extern GeoSettings geoSettings;

void CgUtil::Set(){
}

bool CgUtil::UseHalo(){
  return P_halo_size * P_halo_str >0;
}

bool CgUtil::can_use_doubleshadow(){
  return ((P_light_base==0.0) && (hardSettings.doubleSM) );
}

bool CgUtil::do_use_doubleshadow(){
  return ((P_double_shadows) && (can_use_doubleshadow()));
}

static char* FORMAT="void CgUtil::Set(int K){\nif (K==0){\n P_light_base = %f ;\n P_lighting = %f ;\n P_phong = %f ;\n P_phong_size = %f ;\n P_col_atoms_sat = %f ;\n P_col_atoms_bri = %f ;\n P_texture = %f ;\n P_border_inside = %f ;\n P_border_outside = %f ;\n P_depth_full = %f ;\n P_sem_effect = %d ;\n P_halo_size = %f ;\n P_halo_col = %f ;\n P_halo_str = %f ;\n P_halo_aware = %f ;\n P_fog = %f ;\n P_capping = %d ;\n P_shadowstrenght = %f ;\n P_bg_color_R = %f ;\n P_bg_color_G = %f ;\n P_bg_color_B = %f ;\n auto_normalize = %d ;\n P_double_shadows = %d ;\n P_border_fixed = %d ;\n}\n}";

bool CgUtil::Load(const char* filename){
  FILE *f=fopen(filename, "rt");
  if (!f) return false;
  fscanf(f,FORMAT 
       ,&P_light_base,&P_lighting,&P_phong,&P_phong_size,&P_col_atoms_sat,&P_col_atoms_bri,&P_texture,&P_border_inside,&P_border_outside,&P_depth_full,&P_sem_effect,&P_halo_size,&P_halo_col,&P_halo_str,&P_halo_aware,&P_fog,&P_capping,&P_shadowstrenght,&P_bg_color_R,&P_bg_color_G,&P_bg_color_B,&auto_normalize,&P_double_shadows,&P_border_fixed);
  fclose(f);
  return true;
}

bool CgUtil::Save(const char* filename){
  FILE *f=fopen(filename, "wt");
  if (!f) return false;
  fprintf(f,FORMAT 
       ,P_light_base,P_lighting,P_phong,P_phong_size,P_col_atoms_sat,P_col_atoms_bri,P_texture,P_border_inside,P_border_outside,P_depth_full,P_sem_effect,P_halo_size,P_halo_col,P_halo_str,P_halo_aware,P_fog,P_capping,P_shadowstrenght,P_bg_color_R,P_bg_color_G,P_bg_color_B,auto_normalize,P_double_shadows,P_border_fixed);
  fclose(f);
  return true;
}

 
float CgUtil::_border_outside(){
    return P_border_outside*0.075;
}

float CgUtil::_border_inside(){
    return P_border_inside*0.5;
}

void CgUtil::setGeoSettings(const GeoSettings &gs){
   P_ball_radius = 1.0; // piotr 080501
   if (gs.mode==GeoSettings::BALL_N_STICKS) {
     P_cyl_const_color=gs.use_stick_const_color;
     P_cyl_smooth_color=gs.stick_smooth_color;
     P_cyl_const_color_R = gs.stick_const_color_R;
     P_cyl_const_color_G = gs.stick_const_color_G;
     P_cyl_const_color_B = gs.stick_const_color_B;
     P_ball_radius = 3.0 * gs.ballRadius; // piotr 080501
   }
   if (gs.mode==GeoSettings::LICORICE) {
     P_cyl_const_color=false;
     P_cyl_smooth_color=false;
   }
}

CgUtil::CgUtil() { 
  loaded=false; idf=666; idv=666; auto_normalize=false; norm=1; 
  loadedVertexHalo=false;
  ResetHalo();
  proj_figa=false;
  idfStick=idvStick=666; loadedStick=false; 
  idvHalo=666;
  cyl_radius=0.2; 
  shadowmapBuilding=false; 
  accurateShadowmapBuilding=false; 
  doingAlphaSnapshot=false;
  
  shadersMade=false;
}

void CgUtil::ResetHalo(){
  
  for (int i=0; i<MAXPOW; i++) {
    loadedHalo[i]=false;
    idfHalo[i]=666;
  }
}

char CgUtil::lasterr[255];

bool CgUtil::BindHaloShader(int pow){
  if (idfHalo[pow]==666) glGenProgramsARB(1, &(idfHalo[pow]));
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idfHalo[pow]);  
	
  if (!loadedHalo[pow]) MakeHaloShader(pow);
  
  if (idvHalo==666) glGenProgramsARB(1, &idvHalo);
  glBindProgramARB(GL_VERTEX_PROGRAM_ARB, idvHalo);  
  if (!loadedVertexHalo) LoadVertexHaloShader();
  
  loadedHalo[pow]=true;  
  loadedVertexHalo=true;
  
  return true;
}

void CgUtil::LoadVertexHaloShader(){
 char vp[10096];

 sprintf(vp,"\
!!ARBvp1.0\n\
\n\
ATTRIB pos = vertex.position;\n\
ATTRIB dataA = vertex.texcoord[0];\n\
ATTRIB dataB = vertex.texcoord[1];\n\
\n\
");


 sprintf(vp,"%s\
\n\
PARAM  mat[4] = { state.matrix.mvp };\n\
PARAM  matP[4] = { state.matrix.projection };\n\
\n\
TEMP p,po, disp, dataout, tmp;\n\
\n\
# Transform by concatenation of the\n\
# MODELVIEW and PROJECTION matrices.\n\
DP4 p.x, mat[0], pos;\n\
DP4 p.y, mat[1], pos;\n\
DP4 p.z, mat[2], pos;\n\
DP4 p.w, mat[3], pos;\n\
#MOV p.w, 1; \n\
 \n\
MOV dataout, dataA;\n\
MOV dataout.z, dataB.y;\n\
", vp);
  
 sprintf(vp,"%s\
\n\
MUL disp, dataA, dataB.x; \n\
MUL disp, disp, program.env[0].x; \n\
#MUL disp.x, disp.x, matP[0].x;\n\
#MUL disp.y, disp.y, matP[1].y;\n\
MAD p, {1,1,0,0},  disp, p;\n\
", vp);

 
  sprintf(vp,"%sMOV result.position, p;\n",vp);

  sprintf(vp,"%sMOV result.texcoord, dataout;\n",vp);
  
  sprintf(vp,"%s\nEND\n", vp);
  
  glProgramStringARB(GL_VERTEX_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(vp), vp);

  //printf("\n--------<vp ball>---------\n%s",vp);
  //if(!checkProgramError(vp)) return -1;
  //return true;
}


bool CgUtil::MakeHaloShader(int pow){
 
  char fp[10096];

  sprintf(fp,"\
!!ARBfp1.0\n\
\n\
ATTRIB data   = fragment.texcoord;  \n\
  \n\
TEMP tmp,tmp2,tmp3, t,t0,t1,t2,nor,n,nabs,nsign,disp,res,depth,pos,\n\
     lighting;  \n\
\n\
MOV nor, data;  \n\
MUL tmp, data, data;  \n\
ADD tmp2.x, tmp.x, tmp.y;\n\
ADD tmp2.z, -tmp2.x, 1;\n\
KIL tmp2.z;\n\
\n\
MAD tmp2.x, -data.z, tmp2.x, data.z;\n\
\n\
#TEST!\n\
#ADD tmp2.x, tmp2.x, %10.8f;\n\
#CMP result.color, tmp2.x, {1,0,0,1}, {0,0,1,1};\n\
\n\
MUL tmp, fragment.position, {%14.12f, %14.12f, 0, 0};\n\
#MAD tmp, fragment.position, {0.5, 0.5, 0, 0}, {0.5, 0.5, 0, 0};\n\
TEX tmp.z, tmp, texture[1], 2D; # tmp.z = old depth \n\
ADD tmp.z, tmp.z, -fragment.position.z; \n\
MUL_SAT tmp.z, tmp.z, program.env[0].x; \n\
MUL tmp.z, tmp.z, tmp2.x; \n\
MUL tmp.z, tmp.z, tmp2.x;  # again for smoother edges\n\
", +P_halo_str-1,  1.0f/(1<<pow), 1.0f/(1<<pow) );

  if (P_halo_str<1.0) {
    sprintf(fp,"%sMUL tmp.z , tmp.z, %10.8f;\n",fp, P_halo_str );
  }
  if (!doingAlphaSnapshot)
    sprintf(fp,"%sMAD result.color, {0,0,0,1}, tmp.z, {%5.4f,%5.4f,%5.4f,0.0} ;\n",fp,P_halo_col,P_halo_col,P_halo_col);
  else {
    if (P_halo_col==1.0)  // white halo
      sprintf(fp,"%sMOV result.color, tmp.z;\n",fp);
    else 
      sprintf(fp,"%sMUL result.color, {0,0,0,1}, tmp.z;\n",fp);
  }
  sprintf(fp,"%sEND\n",fp);
  
  


  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
//  printf("\n-------<fp HALO>--------\n%s",fp);
  if(!checkProgramError(fp)) return false;
  return true;  
}

static void addDrawAOShaderSnippet(char* fp) {
  sprintf(fp,"%s\n\
# Find shading value \n\
DP3 l.x, nor, -param; \n\
#MUL_SAT l.x, l.x, param.w; \n\
MUL l.x, l.x, param.w; \n\
#KIL l.x; \n\
",fp);

  if ( (!hardSettings.doubleSM) && (!hardSettings.NVIDIA_PATCH) ) {
  sprintf(fp,"%s\n\
KIL l.x; # early KILL of fragments on the dark side...\n\
",fp);
  }
  
  sprintf(fp,"%s\n\
# Project! \n\
DP4 pos.x, Smat0, origpos;   \n\
DP4 pos.y, Smat1, origpos;    \n\
DP4 pos.z, Smat2, origpos;     \n\
",fp);

  if (hardSettings.doubleSM) sprintf(fp,"%s\n\
CMP tmp, l.x, {0.75,0.5,0.5,1}, {0.25,0.5,0.5,1};\n\
MAD pos, pos, {0.25,0.5,0.5,0}, tmp; \n\
\n\
",fp); else 
sprintf(fp,"%s\n\
MAD pos, pos, {0.5,0.5,0.5,0}, {0.5,0.5,0.5,1}; \n\
",fp);

  sprintf(fp,"%s\n\
# Access shadow map! \n\
TEX tmp.x, pos, texture[1], 2D;\n\
SUB l.z, tmp.x, pos.z; \n\
",fp);

  if (hardSettings.doubleSM) sprintf(fp,"%s\n\
CMP l.z, l.x, -l.z, l.z; \n\
CMP l.x, l.x, -l.x, l.x; # DOUBLE SIDE\n\
\n\
",fp);

  sprintf(fp,"%s\n\
# NVIDIA BUUUUGUUGUGUGUGUGUUGUUGGUGUUGUG GUUGUGUG GGFUCKFUCKFUCKFUCKFUCKFUCKFUCK!!! \n\
%s\
CMP result.color, l.z, 0, l.x;  # <-- (shadow & shading) \n\
#CMP result.color, l.z, 0, 1;   # <-- (TEST: only shadow - works) \n\
#CMP result.color, 1, 0, l.x;   # <-- (TEST: only shading - works) \n\
# NVIDIA BUUUUGUUGUGUGUGUGUUGUUGGUGUUGUG GUUGUGUG GGFUCKFUCKFUCKFUCKFUCKFUCKFUCK!!! \n\
\n\
# TEST1: MAD result.color, {0.5,0.5,0.5,0},nor, {0.5,0.5,0.5,1};\n\
# TEST2: MAD result.color, {0.5,0.5,0.5,0},origpos, {0.5,0.5,0.5,1};\n\
# TEST3: CMP result.color, l.z, {1,0,0,1}, {0,0,0.5,1};\n\
# TEST4: MOV result.color, tmp.x;\n\
\n\
\n\
END\n\
",
fp,
hardSettings.NVIDIA_PATCH?
    "MUL l.x, 0.5, param.w;          # <-- patch! REMOVE ME when N-VIDIA wakes up \n"
    :""
);
}

bool CgUtil::MakeDrawAOShader(){
  char fp[10096];
  sprintf(fp,"\
!!ARBfp1.0  \n\
PARAM  Smat0 = program.env[0];\n\
PARAM  Smat1 = program.env[1];\n\
PARAM  Smat2 = program.env[2];\n\
PARAM  param = program.env[3];\n\
ATTRIB tc   = fragment.texcoord;  \n\
ATTRIB data   = fragment.texcoord[1];  \n\
TEMP tmp,nor, pos,origpos, abs,l;\n\
\n\
# Find shpere normal... \n\
CMP abs, tc, -tc, tc;\n\
MAD nor, -abs, {1,1,0,0}, +1;\n\
CMP tmp.x, tc.x, -nor.y, nor.y;    # tmp_i = sign_i*( 1-abs_i) \n\
CMP tmp.y, tc.y, -nor.x, nor.x;    # tmp_i = sign_i*( 1-abs_i) \n\
ADD nor.z, abs.x, abs.y; \n\
ADD nor.z, nor.z, -1; \n\
CMP nor.x, -nor.z, tmp.x, tc.x;\n\
CMP nor.y, -nor.z, tmp.y, tc.y;\n\
# Normalize \n\
DP3 tmp.x, nor, nor; \n\
RSQ tmp.x, tmp.x; \n\
MUL nor, nor, tmp.x; \n\
\n\
# Find pos \n\
MAD origpos, data.w, nor, data;\n\
MOV origpos.w, 1;\n");

  addDrawAOShaderSnippet(fp);

  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
//  printf("\n-------<fp special>--------\n%s",fp);
  if(!checkProgramError(fp)) return false;
  //ShowShaderInfo(GL_FRAGMENT_PROGRAM_ARB);
  return true;
};

bool CgUtil::MakeDrawAOShaderSticks(){
  char fp[10096];
  sprintf(fp,"\
!!ARBfp1.0  \n\
PARAM  Smat0 = program.env[0];\n\
PARAM  Smat1 = program.env[1];\n\
PARAM  Smat2 = program.env[2];\n\
PARAM  param = program.env[3];\n\
PARAM  radius = program.env[4];\n\
ATTRIB axispos= fragment.texcoord[1];  \n\
ATTRIB data   = fragment.texcoord;  \n\
TEMP tmp,n,nor, pos,origpos, abs,l;\n\
\n\
\n\
# find norm in cyl space \n\
MAD n.y, data.y, -2, 0; \n\
CMP n.y, n.y, -n.y, n.y; \n\
ADD n.x, 2, -n.y; \n\
MIN n.x, n.x, n.y; \n\
CMP n.x, data.y, n.x, -n.x; \n\
MAD n, n, {1,1,0,0}, {0,-1,0,0};\n\
\n\
# normalize \n\
DP3 tmp.x, n, n;\n\
RSQ tmp.x, tmp.x;\n\
MUL n, tmp.x, n;\n\
\n\
# rotate \n\
MUL nor, -n.x, fragment.texcoord[2];\n\
MAD nor,  n.y, fragment.texcoord[3], nor;\n\
\n\
# find position \n\
MAD origpos, nor, radius.y, axispos; \n\
MOV origpos.w, 1;\n\
");

  addDrawAOShaderSnippet(fp);

  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
//  printf("\n-------<fp special>--------\n%s",fp);
  if(!checkProgramError(fp)) return false;
  //ShowShaderInfo(GL_FRAGMENT_PROGRAM_ARB);
  return true;
};

void CgUtil::Normalize(){
/*  if (!auto_normalize) return;
  float sum=P_light_base + P_lighting + P_texture;
  if (sum>1.0) {
    norm=sum;
    P_light_base/=norm;
    P_lighting/=norm;
    P_texture/=norm;
  }*/
}


void CgUtil::UndoNormalize(){
   //P_light_base*=norm;
   P_lighting*=norm;
   P_texture*=norm;
}

void CgUtil::SetDefaults(){
  P_light_base=0.0;
  P_lighting=0.9;  
  P_phong=0.0;  
  P_phong_size=0.75;  
  
  P_col_atoms_sat=0.5; 
  P_col_atoms_bri=1.0; 

  P_texture=0.0;   
  P_border_inside=0.0;
  
  P_border_outside=0.0; 
  P_depth_full=0.5;  
  
  P_sem_effect=false;
  //P_use_shadowmap=false;
  P_shadowstrenght=0.0;
  P_double_shadows=true;
  P_fog=0;
  
  P_bg_color_R=P_bg_color_G=P_bg_color_B=0.5;

//  textmode=USE_CUBE;
  textmode=USE_OCTA;
  projmode=ORTHO;
  
  writeAlpha=false;
  writeCol=true;
  gap =0.5;

  P_capping=false;

  P_halo_size=0.0; // 1.0;
  P_halo_col =0.0; // 1.0;
  P_halo_str =1.0; // 1.0;
  P_halo_aware=0.5;
    
}

void CgUtil::SetForShadowMap(bool accurate){
  
  P_light_base=0.0;
  P_lighting=0.0;  
  P_phong=0.0;  

  P_col_atoms_sat=0.0; 
  P_col_atoms_bri=0.0; 
  P_texture=0.0;   
  P_border_inside=0.0;
  P_border_outside=0.0; 
  P_sem_effect=false;
  //P_use_shadowmap=false;
  P_shadowstrenght=0.0;
  P_fog=0;

  projmode=ORTHO;
  
  textmode=USE_OCTA;
  writeAlpha=false;
  writeCol=false;

  P_capping=false;
  
  P_halo_size=0.0;
  
  shadowmapBuilding=true;
  accurateShadowmapBuilding=accurate;
}

void CgUtil::SetForOffLine(){

  P_light_base=0.0;
  P_lighting=0.0;  
  P_phong=0.0;  

  P_col_atoms_sat=0.0; 
  P_col_atoms_bri=0.0; 
  P_lighting=0.0;  
  P_texture=1.0;   
  P_border_inside=0.0;
  P_border_outside=0.0; 
  P_sem_effect=false;
  //P_use_shadowmap=false;
  P_shadowstrenght=0.0;
  P_fog=0;
  
  projmode=ORTHO;

  textmode=USE_OCTA;

  writeAlpha=true;
  writeCol=true;

  P_capping=false;
  
  gap =0.2;
  
  P_halo_size=0.0;
}

void CgUtil::BindShaders(){
  if (!loaded)  MakeShaders();
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idf);
	glBindProgramARB(GL_VERTEX_PROGRAM_ARB, idv);
}

void CgUtil::MakeShaders(){
  
  if (shadersMade) return;
  
  shadersMade=true;
  
  if (idf==666) glGenProgramsARB(1, &idf);
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idf);
  setBallFragmentProgram();
  
  if (idv==666) glGenProgramsARB(1, &idv);
	glBindProgramARB(GL_VERTEX_PROGRAM_ARB, idv);
  setBallVertexProgram();
  
  loaded=true;  

  MakeStickShaders();
  
}

void CgUtil::BindStickShaders(){
  if (!loadedStick)  MakeStickShaders();
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idfStick);
	glBindProgramARB(GL_VERTEX_PROGRAM_ARB, idvStick);
}

void CgUtil::MakeStickShaders(){
  
  if (idfStick==666) glGenProgramsARB(1, &idfStick);
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idfStick);
  setStickFragmentProgram();
  
  if (idvStick==666) glGenProgramsARB(1, &idvStick);
	glBindProgramARB(GL_VERTEX_PROGRAM_ARB, idvStick);
  setStickVertexProgram();
  
  loadedStick=true;  

}

bool CgUtil::BindDrawAOShader(){
  if (idf==666) glGenProgramsARB(1, &idf);
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idf);  
  if (!loaded) MakeDrawAOShader();
  loaded=true;  
  return true;
}

bool CgUtil::BindDrawAOShaderSticks(){
  if (idf==666) glGenProgramsARB(1, &idf);
	glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, idf);  
  if (!loaded) MakeDrawAOShaderSticks();
  loaded=true;  
  return true;
}



bool CgUtil::setBallVertexProgram(){
 char vp[10096];

// #####################
// #                   #
// #  VERTEX PROGRAM   #
// #                   #
// #####################
 
 sprintf(vp,"\
!!ARBvp1.0\n\
\n\
ATTRIB pos = vertex.position;\n\
ATTRIB data = vertex.normal;\n\
\n\
");

// DataOut = ( +- OutradX, +- OutRadY, InRad ) 

 if (P_texture>0) sprintf(vp,"%s\
ATTRIB offset = vertex.texcoord;\n\
", vp);

 sprintf(vp,"%s\
\n\
PARAM  mat[4] = { state.matrix.mvp };\n\
PARAM  matP[4] = { state.matrix.projection };\n\
\n\
TEMP p,po, disp, dataout, tmp;\n\
\n\
# Transform by concatenation of the\n\
# MODELVIEW and PROJECTION matrices.\n\
DP4 p.x, mat[0], pos;\n\
DP4 p.y, mat[1], pos;\n\
DP4 p.z, mat[2], pos;\n\
DP4 p.w, mat[3], pos;\n\
#MOV p.w, 1; \n\
 \n\
MOV dataout, data;\n\
MUL dataout.z, dataout.z, program.env[0].x;\n\
", vp);

  // Enlarge impostors to include borders
  if (_border_outside()!=0) // Compute 'almost' radius and scale indep. border 
 sprintf(vp,"%s\
RSQ tmp.y,  dataout.z ;\n\
#MUL tmp.y,  tmp.y , tmp.y; # Comment to 'almost'\n\
MUL tmp.x,  %7.5f , tmp.y;\n\
ADD dataout.w,  tmp.x , 1;\n\
MUL dataout.xy, dataout, dataout.w ;\n\
MAD dataout.w,  dataout.w, dataout.w, -1;\n\
",
 vp, _border_outside()   ); 
  
 float rad = P_ball_radius; // piotr 080501
 
 sprintf(vp,"%s\
\n\
MUL disp, dataout, dataout.z; \n\
#MUL disp.x, disp.x, matP[0].x;\n\
#MUL disp.y, disp.y, matP[1].y;\n\
MAD p, {%f,%f,0,0},  disp, p;\n\
", vp, rad, rad);

 
 sprintf(vp,"%s\
\n\
MOV result.position, p;\n\
\n\
#MOV dataout.w, p.w;\n"
  ,vp);

  sprintf(vp,"%sMOV result.texcoord, dataout;\n",vp);
 
  if ((P_col_atoms_sat>0)&&(P_col_atoms_bri>0)) sprintf(vp,"%sMOV result.color, vertex.color;\n",vp);

  if (P_texture>0) sprintf(vp,"%sMOV result.texcoord[2], offset;\n",vp);
  
  if (P_use_shadowmap() )  sprintf(vp,"%sMOV result.texcoord[3], vertex.position;\n",vp);
  
  sprintf(vp,"%s\nEND\n", vp);
  
  glProgramStringARB(GL_VERTEX_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(vp), vp);

  //printf("\n--------<vp ball>---------\n%s",vp);
  if(!checkProgramError(vp)) return -1;
  return true;
}



void CgUtil::addShadowMapComputationFP(char* fp) {
  sprintf(fp,"%s\n\
#SHADOWMAP\n\
\n\
#compute orig pos from attributes... MODE 1\n\
#MUL t0.x, data.z, ratio.x;\n\
#MAD pos, n, t0.x, origpos;\n\
#\n\
# ...or MODE 2!!! \n\
MAD posScreen, fragment.position, {1,1,0,0}, {0,0,0,1} ;\n\
MOV posScreen.z, depth.x;\n\
\n\
DP4 t0.x, Smat0, posScreen;        \n\
DP4 t0.y, Smat1, posScreen;         \n\
DP4 t0.z, Smat2, posScreen;          \n\
",fp);  

  if (do_use_doubleshadow()) sprintf(fp,"%s\n\
CMP t1, lighting.z, {0.75,0.5,0.5,1}, {0.25,0.5,0.5,1};\n\
MAD t0, t0, {0.25,0.5,0.5,0}, t1; \n\
\n\
",fp); else {
  double tmp=(hardSettings.doubleSM)?0.25:0.5;
sprintf(fp,"%s\n\
MAD t0, t0, {%4.2f,0.5,0.5,0}, {%4.2f,0.5,0.5,1}; \n\
",fp,tmp,tmp);
  }
/*
  sprintf(fp,"%s\n\
MAD t0, t0, {0.5,0.5,0.5,0}, {0.5,0.5,0.4999999,0}; \n\
",fp);  
*/
  sprintf(fp,"%s\n\
# Access shadow map! \n\
TEX t1, t0, texture[1], 2D;\n\
",fp);

  sprintf(fp,"%s\n\
ADD t.z, -t1.z, t0.z; \n\
",fp);  

  if (do_use_doubleshadow()) sprintf(fp,"%s\n\
CMP t.z, lighting.z, -t.z, t.z; \n\
\n\
",fp);


  if ((!do_use_doubleshadow())&&(P_light_base>0)) {
    sprintf(fp,"%s\n\
CMP t.z, lighting.z, 1, t.z;    # if light<0,  then in shadow \n\
"  ,fp,1.0-P_shadowstrenght);
  }

  if (P_shadowstrenght<1) {
    sprintf(fp,"%s\n\
MUL tmp, lighting, %5.4f; # compute attenuated light \n\
CMP lighting, t.z, lighting, tmp; # if in shadow, then use attenuated light \n\
"  ,fp,1.0-P_shadowstrenght);
  }
  else
  sprintf(fp,"%s\n\
CMP lighting, t.z, lighting, 0; # if in shadow, then no light \n\
#CMP result.color, t.z, {0,1,0,0}, {1,0,0,0}; \n\
#\n\
#MAD t0, t0, {0.5,0.5, 200.0,0}, {0.5,0.5,196.5,0}; \n\
#TEX t1, t0, texture[1], 2D;\n\
#MAD t1, t1, 400, -3.5;\n\
#MUL t1, t1.z, {1,0,1,0};\n\
##ADD t.z, -t1.z, t0.z; \n\
#MAD t0, t0.z, {0,1,0,0}, {0,0,0,0};\n\
#CMP result.color, mat0.x, t1, t0; \n\
#MUL result.color, {0.002,0.002,0,0}, posScreen; \n\
",fp);
 
};

void CgUtil::addTexturingSnippet(char* fp){
  if (P_texture>0) {
    sprintf(fp,"%s%s",fp,"\n\n\
# texture access           \n\
MAD t, t, TNORM, offset;    \n\
TEX t, t, texture[0], 2D;    \n\n");

    if (P_capping) {
        // overwrite ambient occlusion for close fragments
    sprintf(fp,"%s\n\
    \n\
# lighten OC for close frags           \n\
MAD tmp.x, depth.x, -250, 0.50;   \n\
CMP tmp.x, tmp.x, 0, tmp.x;    \n\
# overwrite OC for cut   \n\
CMP tmp.x, depth.x, 0.70, tmp.x;    \n\
LRP t, tmp.x, 1, t;    \n\
", fp);
        
    }
    
    // Add "future" AO prediction (AO not computed yet)
    
    //  Additive prediction:
    //sprintf(fp,"%sADD t, t, program.env[6].x;\n", fp );
    
    // multiplicative prediction:
    sprintf(fp,"%sMUL t, t, program.env[6].x;\n", fp );
    
    sprintf(fp,"%sMAD res, %5.2f, t, res;\n", fp,  P_texture );
    if (P_phong>0.0) {
        // weigth phong with AO light. 
       sprintf(fp, "%s\nMUL lighting.y,lighting.y, t;\n", fp);
    }

  } 
  
  float lighting = (!P_sem_effect) ? P_lighting : (1- P_lighting);


  // apply lighting  
  if ( lighting>0 ) {
    if (P_sem_effect) {
      sprintf(fp,"%sMAD lighting.x, lighting.x, -1, 1 ;\n",fp );
//      sprintf(fp,"%sMUL lighting.x, lighting.x, lighting.x ;\n",fp );
      sprintf(fp,"%s\nMAD lighting.x, %10.8f, lighting.x, %10.8f;\n",fp, lighting, 1-lighting);
      sprintf(fp,"%sMUL res, lighting.x, res;\n",fp );
    }
    else 
      sprintf(fp,"%s\nMAD res, lighting.x, %f, res;\n",fp, lighting);
  }
  
  if (P_col_atoms_sat>0)  {
    if ((P_col_atoms_sat<1)||(P_col_atoms_bri<1)) {
      sprintf(fp,"%sMAD tmp, %5.3f, basecol,%5.3f;\n",fp
          ,P_col_atoms_sat*P_col_atoms_bri, (1.0-P_col_atoms_sat)*P_col_atoms_bri );
      sprintf(fp,"%s%s",fp,"MUL res, res, tmp;\n");
    } else {
      sprintf(fp,"%s%s",fp,"MUL res, res, basecol;\n");
    }
  } else {
    if (P_col_atoms_bri<1.0)
    {
      sprintf(fp,"%s%s",fp,"MUL res, res, %5.3f;\n", P_col_atoms_bri );
    }
  }
  
  if (writeCol) {
    if (P_phong>0) {
      sprintf(fp,"%s%s",fp,"LRP res, lighting.y, 1, res;\n");
    } 

    if (writeAlpha) 
      sprintf(fp,"%s%s",fp,"MOV res.w, nor.z;\n");    
  } 
  
  
  // UNUSED:
  if ( _border_inside()>0 ) {
    sprintf(fp,                "%s \n\
     MAD tmp2.z, border.x, %f, 1;     \n\
     LRP tmp3, tmp2.z, 0, res;\n\
     CMP res, -tmp2.z,  tmp3, res;\n\
     \n",
     fp,
     (1.0/_border_inside())
    );
  };

  if ( _border_outside()>0 ) {
     // Blackens borders:
        
#if (1)     
     // no AA:
     sprintf(fp,"%sCMP res, -border.x,  {0,0,0,0}, res;\n",fp);
#else     
     // internal AA:
     //sprintf(fp,"%sMAD_SAT border.y, -border.x , 10, 1 ;\n",fp);
     //sprintf(fp,"%sMUL res, border.y, res;\n",fp);
#endif
  }

  if ( P_fog>0 ) {
     sprintf(fp,"%sMAD_SAT tmp.x, depth.x,  50, 0;\n",fp);
     sprintf(fp,"%sMUL tmp.x, tmp.x, %5.4f;\n",fp, P_fog);
     sprintf(fp,"%sLRP res, tmp.x, {%10.9f,%10.9f,%10.9f,1}, res;\n",fp, P_bg_color_R,P_bg_color_G,P_bg_color_B);
  }
  
}

void CgUtil::addDepthAdjustSnippet(char* fp) {

  float depth_full=P_depth_full*120.0f;
  
  // DEPTH AWARE
  if ( _border_outside()>0 ) {
    sprintf(fp,                "%s \n\
     MUL tmp3.z,  -border.x,  data.z;\n\
     MAD tmp3.z,  %8.7f , tmp3.z , fragment.position.z;\n\
     CMP depth.x, -border.x, tmp3.z, depth.x;\n\
     \n",fp,
     -depth_full/_border_outside() / 20000.0 //-0.001
    );
  } 

  if (P_capping) {
    
    //
    //sprintf(fp,"%s%s",fp, "MAD tmp.x, depth.x, 0.001, 10;\n");
    //sprintf(fp,"%s%s",fp, "CMP result.depth, depth.x, tmp.x, depth.x;\n");
    //

    sprintf(fp,"%s%s",fp, "ADD result.depth, depth.x, 0.001;\n");  
  }
  else {
//    sprintf(fp,"%s%s",fp, "CMP result.depth, depth.x, 0, depth.x;\n");
    sprintf(fp,"%s%s",fp, "MOV result.depth, depth.x;\n");
  }

  sprintf(fp,"%s%s",fp,"MUL res, res, t;\n" );

  float lighting = (!P_sem_effect) ? P_lighting : (1- P_lighting);

  if ((P_capping) && ( (lighting>0) ||  (P_phong>0) ) )  {
    sprintf(fp,"%s\n\
# Overwrite capped normal    \n\
CMP nor, depth.x, {0,0,1,0}, nor;\n",
    fp );
  }  
}


void CgUtil::addDirectLightingSnippet(char* fp) {
 
  /* 
   NOTE: 
    lighting.x = lambert direct (halved if opposite side)
    lighting.y = phong  direct (zeroed if opposite side)
    lighting.z = lamber original (negative if opposite side) 
 */
  
  float lighting = (!P_sem_effect) ? P_lighting : (1- P_lighting);

  if (lighting>0) {
    sprintf(fp,"%s%s",fp, " \n\n\
## LIGHTING of Normal        \n\
DP3 lighting.z, nor, LIGHT;        \n\
MUL tmp.y, -lighting.z, 0.35;        \n\
CMP lighting.x, lighting.z, tmp.y, lighting.z; \n\n"
     );
  }
  if (P_phong>0.0) {
   // phong
    sprintf(fp,                "%s\
## PHONG \n\
#ADD hwv, {0,0,+1,0}, LIGHT;\n\
#DP3 lighting.y, hwv, hwv;\n\
#RSQ lighting.y, lighting.y;\n\
#MUL hwv, hwv, lighting.y;\n\
DP3 lighting.y, nor, hwv;\n", fp);

    // compute exponent (TODO: use some sort of EXP funtion)
    for (int i=0; i<(1.0-P_phong_size)*6.0+3; i++)
      sprintf(fp,"%sMUL lighting.y, lighting.y, lighting.y;\n", fp);
    
    if (P_phong<1.0)
      sprintf(fp,"%s\nMUL lighting.y,%5.4f,lighting.y;\n", fp, P_phong);
    
  }
  
  if(P_light_base>0) {
    sprintf(fp,"%s\nLRP lighting.x,%5.4f, 1, lighting.x; # flatten light \n", fp, P_light_base );
  }

  sprintf(fp,"%s\nMOV res, %5.4f;\n", fp, 0.0 );

}

bool CgUtil::shaderHasChanged=false;

bool CgUtil::setStickFragmentProgram(){

  char fp[10096];

  if (shadowmapBuilding) {
    if (!accurateShadowmapBuilding) 
      
      sprintf(fp,"\
!!ARBfp1.0  \n\
  \n\
MOV result.color, 1;\n\
END\n"
      );
      else 
      sprintf(fp,"\
!!ARBfp1.0  \n\
  \n\
ATTRIB data = fragment.texcoord;  \n\
MOV result.color, 0.8;\n\
MAD_SAT tmp.x, data.x, -data.x, 1;   # tmp.z=1-x^2 \n\
RSQ tmp.x, tmp.x;\n\
RCP n.y, tmp.x;\n\
MAD tmp.z, n.y, data.z, 0; \n\
MAD result.depth, -tmp.z, 0.005, fragment.position.z; \n\
END\n");
      
  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
  
  //printf("\n-------<fp stick>--------\n%s",fp);

  if(!checkProgramError(fp)) return false;
  return true;
  }

  sprintf(fp,"\
!!ARBfp1.0\n\
\n\
ATTRIB data = fragment.texcoord;  \n\
ATTRIB normcenter = fragment.texcoord[1];\n\
ATTRIB ROT = fragment.texcoord[2];\n\
ATTRIB offset = fragment.texcoord[3];\n\
ATTRIB normside = fragment.texcoord[4];\n");

  if (!P_cyl_const_color) {
  sprintf(fp,"%s\
ATTRIB col1 = fragment.color.primary;\n\
ATTRIB col2 = fragment.color.secondary;\n",fp);
  }

  sprintf(fp,"%s\
PARAM TNORM={%10.9f,%10.9f,0,0};  \n\
PARAM  mat0 = program.env[0];\n\
PARAM  mat1 = program.env[1];\n\
PARAM  mat2 = program.env[2];\n",fp,
  (moltextureCanvas.GetHardRes()==0)?0:1.0f/moltextureCanvas.GetHardRes(), 
  (moltextureCanvas.GetHardRes()==0)?0:1.0f/moltextureCanvas.GetHardRes() 
);
  if (P_use_shadowmap())
  sprintf(fp,"%s\
PARAM  Smat0  = program.env[3];   \n\
PARAM  Smat1  = program.env[4];   \n\
PARAM  Smat2  = program.env[5];   \n\
#PARAM  ratio  = program.env[6];   \n\
ATTRIB origpos = fragment.texcoord[4];  \n",fp);

   sprintf(fp,"%s\n\
PARAM LIGHT= state.light[0].position ;  \n\
PARAM hwv  = state.light[0].half;\n\
\n\
TEMP tmp, nor, n, lighting, res, t, t0, t1, abs, posScreen; \n\
TEMP basecol, border, depth, tmp2, tmp3; \n\
\n\
\n\
MAD_SAT tmp.x, data.x, -data.x, 1;   # tmp.z=1-x^2 \n\
RSQ tmp.x, tmp.x;\n\
RCP n.y, tmp.x;\n\
MAD tmp.z, n.y, data.z, 0; \n\
MAD depth.x, -tmp.z, 0.005, fragment.position.z; \n\
\n\
", fp);

  if ( (_border_outside()>0 ) ) {
  sprintf(fp,"%s\n\
#CMP border.x, n.y, n.y, -n.y;  \n\
MAD border.x, data.x, data.x, -1; \n\
#ADD border.x, 1, -border.x;  \n\
", fp);
  }
  
  addDepthAdjustSnippet(fp);

  sprintf(fp,"%s\n\
# Compute normal\n\
MUL nor, n.y, normcenter;\n\
MAD nor, data.x, normside, nor;\n\
", fp);

  addDirectLightingSnippet(fp);
   
  sprintf(fp,"%s\n\
#TEXTURING ON STICKS  \n\
\n\
# FIND X (along axis) \n\
MOV t.x, data.y;\n\
MAD t.x, data.w, n.y, t.x;\n\
# FIND Y (project norm) \n\
MOV n.x, data.x; \n\
\n\
\n\
# rotate (n.x, n.y)\n\
MUL tmp, n, {1,1,0,0};\n\
DP3 n.x, tmp, ROT;\n\
MUL n.y, tmp.x, ROT.y;\n\
MAD n.y, tmp.y, -ROT.x , n.y;\n\
\n\
# find x=FindRoll ( n.x, n.y) \n\
ABS abs, n; \n\
ADD abs.z, abs.x, abs.y; \n\
RCP abs.z, abs.z; \n\
MUL n, n, abs.z;\n\
MAD tmp.x, 0.25, n.y, 0.25;\n\
MAD tmp.y, 0.25,-n.y, 0.75;\n\
CMP t.y, n.x, tmp.x, tmp.y;\n\
\n\
\n\
#KILL OUTLIER  FRAGMENTS \n\
CMP t.w, t.x, -t.x, t.x;\n\
ADD t.w, t.w, -1; # w = 1-|x|\n\
KIL -t.w;\n\
",fp);


  if (P_use_shadowmap()) {
    addShadowMapComputationFP(fp);
  };
  
  if ((P_col_atoms_sat>0) && (P_col_atoms_bri>0)) {
    if (P_cyl_const_color) sprintf(fp,"%sMOV basecol, {%10.9f,%10.9f,%10.9f,1};\n", 
        fp,P_cyl_const_color_R, P_cyl_const_color_G, P_cyl_const_color_B);
    else if (P_cyl_smooth_color) {
      sprintf(fp,"%sMAD t.z, t.x, 0.5,0.5;\n",fp);
      sprintf(fp,"%sLRP basecol, t.z, col1,col2;\n",fp);
    } else 
      sprintf(fp,"%sCMP basecol, t.x, col2,col1;\n",fp);
  }

  if (P_texture>0) {
   float sidex=BSIZE, sidey=CSIZE;
    sprintf(fp,"%s\n\
MAD t, t, {%5.2f, %5.2f, 0,0},          \n\
          {%5.2f, %5.2f, 0,0};           \n\
#FRC t, t; \n\
",
fp, 
(sidex-1)/2.0 , sidey-1.0 , (sidex)/2.0, 0.5);

  }
  
  addTexturingSnippet(fp);

  sprintf(fp,"%s%s",fp,"ADD result.color, res, {0,0,0,1};\n\n");    
  sprintf(fp,"%s%s",fp,"END\n");

/*#MOV result.color, n.y;\n\
#MUL tmp.y, data.y, 8;\n\
#FRC result.color.y, tmp.y;\n\
#MOV result.color, fragment.color;\n\
END\n\
");*/

  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
//  printf("\n-------<fp Sticks>--------\n%s",fp);
  if(!checkProgramError(fp)) return false;
  return true;  
}

bool CgUtil::setStickVertexProgram(){
  /*
  RESULT:
       TC0 = (corner, ... )
       TC1 = NORMAL (on central axis)
       TC2 = ROTATION of basic point
       TC3 = TEXTURE OFFSET
no! -> TC4 = POSITION of proj. over axis (for shadowmap)
       TC4 = DIRECTION of normal of side point
  */
 char vp[10096];
 
 sprintf(vp,"\
!!ARBvp1.0\n\
\n\
ATTRIB pos = vertex.position;\n\
\n\
ATTRIB data = vertex.normal;\n\
ATTRIB dire = vertex.texcoord;\n\
ATTRIB startp = vertex.texcoord[1];\n\
\n\
PARAM  mat[4] = { state.matrix.mvp };\n\
#PARAM  matP[4] = { state.matrix.projection };\n\
PARAM  matM[4] = { state.matrix.modelview };\n\
\n\
TEMP p,tmp,tmp2, d,dr, dataout, disp, disp2, norm, normside; \n\
\n\
");
 if (P_texture>0)
 sprintf(vp,"%s\
# pass down texture offest \n\
MOV result.texcoord[3], vertex.texcoord[2];\n\
\n\
", vp);

 if ((P_col_atoms_sat>0) && (P_col_atoms_bri>0))
 sprintf(vp,"%s\
MOV result.color.primary, vertex.color.primary;\n\
MOV result.color.secondary, vertex.color.secondary;\n\
",vp);

 sprintf(vp,"%s\
# Project direction View frame.\n\
DP3 d.x, matM[0], dire;\n\
DP3 d.y, matM[1], dire;\n\
DP3 d.z, matM[2], dire;\n\
\n\
",vp);

 sprintf(vp,"%s\
# find k = 1/sqrt(d.x^2+d.y^2)  (= tmp.w) \n\
MUL tmp.w, d.x, d.x;        \n\
MAD norm.z,  d.y, d.y, tmp.w; \n\
RSQ tmp.w, norm.z;            \n\
# \n\
# Using orthonormal base B: \n\
#  Bx= (+dx,+dy, 0)*k \n\
#  By= (-dy,+dx, 0)*k \n\
#  Bz= (  0,  0, 1)   \n\
\n\
# now dr = d in B = ( (dx^2+dy^2)*k, 0, dz ) \n\
\n\
",vp);

 if (!shadowmapBuilding)
 sprintf(vp,"%s\
# find normal = ( dr.z*Bx - dr.x*Bz ) = k* (-dx*dz, -dy*dz, dx^2+dy^2)\n\
MUL norm.x,  -d.x, d.z;\n\
MUL norm.y,  -d.y, d.z;\n\
MUL norm,  norm, tmp.w;\n\
\n\
DP3 tmp.x, norm,  norm; # normalization, TEMP TEST!\n\
RSQ tmp.x, tmp.x;\n\
MUL norm, norm, tmp.x;\n\
\n\
",vp);

 sprintf(vp,"%s\
# radius r (=tmp.z) = Raduis*GlobalScaleFactor \n\
MUL tmp.z, program.env[0].y, program.env[0].x; \n\
\n\
SWZ disp, d,  y,-x,0,0; \n\
MUL disp, disp, tmp.w;       \n\
MUL disp2, disp, tmp.z;       \n\
### postponed MAD p, data.x, disp2, p;  \n\
\n\
MOV dataout, data;\n\
\n\
",vp);

  
 if (!shadowmapBuilding)
 sprintf(vp,"%s\
# pre-compute Z offset \n\
\n\
# dataout.z = R*(sen*sen/cos+cos) = R*(z*z*k+1/k) \n\
# dataout.z is the z-offset for the center of the cyl \n\
RCP tmp.x , tmp.w;\n\
MUL tmp.y, d.z, d.z;\n\
MAD tmp.y, tmp.y, tmp.w, tmp.x;\n\
MUL dataout.z, program.env[0].y, tmp.y;\n\
# dataout.w = dz/dx \n\
# dataout.w is the y-offset for the center of the cyl \n\
MUL dataout.w, d.z, tmp.w;\n\
MUL dataout.w, dataout.w, dire.w;\n\
MUL dataout.w, dataout.w, program.env[0].z; # (i.e. rad*2)\n\
\n\
",vp);

  // Further enlarge impostors at sides to include borders
  if (_border_outside()!=0) // Compute 'almost' radius and scale indep. border 
 sprintf(vp,"%s\
#MUL tmp.z, program.env[0].y, program.env[0].x; \n\
RSQ tmp.x,  tmp.z ;\n\
#MUL tmp.x,  tmp.x,  tmp.x; # Comment to 'almost'\n\
MUL tmp.x,  %7.5f , tmp.x;\n\
ADD tmp.x,  tmp.x , 1;\n\
MUL dataout.x, dataout.x, tmp.x ;\n\
",
 vp, _border_outside()   ); 

 if (!shadowmapBuilding)
 sprintf(vp,"%s\
# extend cylinder on bottom do deal with ends \n\
MUL tmp.x, -data.y, dataout.w;\n\
SGE tmp.x, tmp.x, 0;\n\
MUL tmp.x, -dataout.w, tmp.x; \n\
ADD dataout.y, dataout.y, tmp.x;\n\
RCP tmp2.x, dire.w; \n\
MUL tmp.x, tmp.x, tmp2.x; \n\
MUL tmp.x, 0.5, tmp.x; \n\
MAD tmp, dire, tmp.x, pos; \n\
",vp);
 else sprintf(vp,"%s\
MOV tmp, pos; \n\
",vp);

 sprintf(vp,"%s\
\n\
# Project point in View frame.\n\
MOV tmp.w, 1; \n\
DP4 p.x, mat[0], tmp;\n\
DP4 p.y, mat[1], tmp;\n\
DP4 p.z, mat[2], tmp;\n\
DP4 p.w, mat[3], tmp; \n\
\n\
MAD result.position, dataout.x, disp2, p;  \n\
",vp);

 
  // Compute normal at side points
 if (!shadowmapBuilding)
 sprintf(vp,"%s\
MOV result.texcoord[0], dataout;\n\
MOV result.texcoord[1], norm;\n\
XPD normside, d, norm;\n\
\n\
DP3 tmp.x, normside,  normside; # normalization, of normside \n\
RSQ tmp.x, tmp.x;\n\
MUL normside, normside, tmp.x;\n\
\n\
MOV result.texcoord[4], normside;\n\
",vp);

 if (P_texture>0)
 sprintf(vp,"%s\
#ROTATE start vector;\n\
DP3 tmp.x, matM[0], startp;\n\
DP3 tmp.y, matM[1], startp;\n\
DP3 tmp.z, matM[2], startp;\n\
DP3 tmp.w, tmp, tmp;\n\
RSQ tmp.w, tmp.w;\n\
MUL tmp, tmp.w, tmp;\n\
MOV tmp.w, tmp.z;\n\
#MOV tmp.z, 0;\n\
DP3 tmp.x, disp, tmp;\n\
\n\
# cheap way: find an offset to add \n\
# tz=2-tz if tw negative \n\
#SGE tmp.w, 0, -tmp.w; \n\
#MAD tmp.z, tmp.w, -2, 1; \n\
#MUL tmp.x, tmp.z, tmp.x; \n\
#MAD tmp.x, tmp.w, -2, tmp.x; \n\
#MUL result.texcoord[2].x, tmp.x, 0.25;\n\
#\n\
# cool way: store 2D rotation via complex numbers  \n\
# tmp.y = sign(tw)*sqrt(1-tmp.x^2)\n\
SGE tmp.w, 0, -tmp.w; \n\
MAD tmp.z, tmp.w, -2, 1; \n\
MAD tmp.w, tmp.x, -tmp.x, 1;\n\
RSQ tmp.w, tmp.w;\n\
RCP tmp.w, tmp.w;\n\
MUL tmp.y, tmp.w, -tmp.z;\n\
\n\
MOV result.texcoord[2], tmp;\n\
",
  vp);

/*
// Not needed
 if (P_use_shadowmap())
 sprintf(vp,"\%s\n\
MOV result.texcoord[4], pos;\n\
",vp);
*/

 sprintf(vp,"\%s\n\
END\n\
",vp);

  glProgramStringARB(GL_VERTEX_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(vp), vp);

  //printf("\n--------<vp stick>---------\n%s",vp);
  if(!checkProgramError(vp)) return -1;
  return true;
};


bool CgUtil::setBallFragmentProgram(){
  CgUtil::shaderHasChanged=true;
  char fp[10096];
  
  if (shadowmapBuilding) {
      sprintf(fp,"\
!!ARBfp1.0  \n\
  \n\
ATTRIB data = fragment.texcoord;  \n\
TEMP tmp; \n\
\n\
MAD tmp.x, data.x, data.x, -1;  \n\
MAD tmp.x, data.y, data.y, tmp.x;  \n\
KIL -tmp.x;");
      if (accurateShadowmapBuilding) 
        sprintf(fp,"%s\
RSQ tmp.x, tmp.x;  \n\
RCP tmp.x, tmp.x;  \n\
MUL tmp.x, tmp.x, data.z; \n\
MAD result.depth, -tmp.x, 0.005, fragment.position.z;\n"
,fp);

      sprintf(fp,"\
%sMOV result.color, 1;\n\
END\n",fp);
      
    glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
  
    //printf("\n-------<fp>--------\n%s",fp);

    if(!checkProgramError(fp)) return false;
    return true;
  }
// ############################
// #                          #
// #  FRAGMENT PROGRAM  BALL  #
// #                          #
// ############################

  sprintf(fp,"\
!!ARBfp1.0  \n\
  \n\
ATTRIB data = fragment.texcoord;  \n\
ATTRIB offset = fragment.texcoord[2];\n\
ATTRIB basecol = fragment.color;  \n\
");
  if (P_use_shadowmap())
  sprintf(fp,"%s\
PARAM  Smat0  = program.env[3];   \n\
PARAM  Smat1  = program.env[4];   \n\
PARAM  Smat2  = program.env[5];   \n\
#PARAM  ratio  = program.env[6];   \n\
ATTRIB origpos = fragment.texcoord[3];  \n\
",fp);

  sprintf(fp,"%s\
  \n\
TEMP tmp,tmp2,tmp3, t,t0,t1,t2,nor,n,nabs,nsign,disp,res,depth,\n\
     lighting, border, posScreen;  \n\
PARAM TNORM={%10.9f,%10.9f,0,0};  \n\
  \n\
PARAM LIGHT= state.light[0].position ;  \n\
PARAM hwv  = state.light[0].half;\n\
  \n\
PARAM  mat[4] = { state.matrix.projection };  \n\
PARAM  mat0 = program.env[0];\n\
PARAM  mat1 = program.env[1];\n\
PARAM  mat2 = program.env[2];\n\
\n",
  fp, 
  (moltextureCanvas.GetHardRes()==0)?0:1.0f/moltextureCanvas.GetHardRes(), 
  (moltextureCanvas.GetHardRes()==0)?0:1.0f/moltextureCanvas.GetHardRes() );

  sprintf(fp,"%s\
MOV nor, data;  \n"
  ,fp);
  
  // tentativo prospettiva figa
  if ((projmode==PERSPECTIVE)&&(proj_figa)) {
/*  sprintf(fp,"%s\
MAD tmp, fragment.position, {0.00390625, 0.00390625, 0,0}, {-1,-1,0,0};  \n\
DP4 tmp.x, tmp, data;  \n\
MUL tmp.x, tmp.x, 0.5;  \n\
MAD data.xy, data, tmp.x, data;  \n\
"
  ,fp);*/
    
  }
  
  sprintf(fp,"%s\
MUL tmp, data, data;  \n\
MOV tmp.z, 1;          \n\
DP3 border.x, tmp, {1,1,-1,0};  \n" // border.x = ( (x^2+y^2)-1 )
  ,fp);
  
  // 1.20*.120 -1 = 0.44
  
if (_border_outside()>0) {
sprintf(fp,"%s\n\n\
ADD tmp2.y, -border.x, data.w;  # allow for border (part ii)  \n\
#MAD tmp2.y, data.z, -border.x, %7.5f;\n\
#MAD tmp2.y, data.z, tmp2.y, %7.5f;\n\
KIL tmp2.y;  \n\
",fp, -2*_border_outside(), _border_outside()*_border_outside());
}
else sprintf(fp,"%s\n\nKIL -border.x;  \n",fp);

sprintf(fp,"%s\
  \n\
RSQ tmp2.y, border.x;  \n\
RCP tmp2.x, tmp2.y;  \n\
MOV nor.z, tmp2.x;  \n\
  \n\
MAD tmp2.y, tmp2.x, data.z, 0;  # note: add an extra range of 0 \n\
\n",
  fp); // nor = x, y, z=(1- x^2+y^2)
  
  
/*  if (projmode==PERSPECTIVE) //  new_z = old_z / (1/W) + sph_z * W
    sprintf(fp,"%s%s",fp,"\
MUL tmp2.y, tmp2.y,  fragment.position.w;  \n\
MAD depth.x, fragment.position.z, data.w, -tmp2.y; # prospettiva: new_z = old_z + 0.005*sph_z\n\
MUL depth.x, depth.x, 0.1; \n\
");
  else*/  
  
  //  new_z = old_z + 0.005*sph_z
    sprintf(fp,"%s%s",fp, "\
MAD depth.x, -tmp2.y, 0.005, fragment.position.z; # ortho \n\
");

  addDepthAdjustSnippet(fp);
  
  if ((P_texture>0)|| (P_use_shadowmap())) {

  sprintf(fp,"%s%s",fp," \n\n\
# rotate normal           \n\
DP3 n.x, mat0, nor;        \n\
DP3 n.y, mat1, nor;         \n\
DP3 n.z, mat2, nor;          \n\
MOV n.w, 0;                   \n\n");
  }

  addDirectLightingSnippet(fp);  

  if (P_use_shadowmap()) {
      addShadowMapComputationFP(fp);
  };
  
  if (P_texture>0) {
    if (textmode==USE_CUBE) 
    sprintf(fp,     "%s      \n\n\
## TEXTURING CUBEMAP STYLE    \n\
#                              \n\
# project on cube: find face    \n\
CMP nabs, n, -n, n;              \n\
MOV t, n;                    \n\
SWZ t0, t, z,x,y,1;           \n\
SWZ t1, t0, z,x,y,-1;          \n\
#                               \n\
SUB t2.x, nabs.z, nabs.y;        \n\
CMP t, t2.x, t0, t;               \n\
#                            \n\
CMP t2.z, t.z, -t.z, t.z;     \n\
SUB t2.x, t2.z, nabs.x;        \n\
CMP t, t2.x, t1, t;             \n\
#                                \n\
# find face                       \n\
ADD disp.x, t.w, 1;                \n\
CMP disp.y, t.z, 0, 1;              \n\
#                                    \n\
# divide by max coord            \n\
RCP t.z, t.z;                     \n\
MUL t, t, t.z;                     \n\
#                                   \n\
# find coords on face                \n\
MAD t, t, 0.5, 0.5;                   \n\
MAD t, t, {%5.2f,%5.2f,0,0}, {%5.2f, %5.2f, 0,0};  \n\
MAD t, {%5.2f,%5.2f,0,0}, disp, t;            \n\n",
  fp, CSIZE-gap*2.0, CSIZE-gap*2.0, gap, gap, CSIZE, CSIZE  );
  
    else  sprintf(fp,     "%s\n\n\
## TEXTURING OCTAMAP STYLE    \n\
#                              \n\
CMP nabs, n, -n, n;             \n\
DP3 tmp.y, {1,1,1,0}, nabs;      \n\
RCP tmp.z, tmp.y;                 \n\
MUL t0, n, tmp.z;                  \n\
MAD t1, nabs, tmp.z, -1;            \n\
#   t1= -(1-abs(t))                  \n\
CMP t2.x, n.x, t1.y, -t1.y;           \n\
CMP t2.y, n.y, t1.x, -t1.x;            \n\
CMP t0, n.z, t0, t2;                    \n\
MAD t, t0, {%5.2f, %5.2f, 0,0},          \n\
           {%5.2f, %5.2f, 0,0};           \n\n",
fp, 
CSIZE/2.0 - gap, CSIZE/2.0 - gap, CSIZE/2.0, CSIZE/2.0);

  }

  addTexturingSnippet(fp);
  
  sprintf(fp,"%s%s",fp,"ADD result.color, res, {0,0,0,1};\n\n"); 
  sprintf(fp,"%s%s",fp,"END\n");

  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(fp), fp);  
  
  //printf("\n-------<fp>--------\n%s",fp);

  if(!checkProgramError(fp)) return false;
  return true;

  
}


bool CgUtil::init() {

  GLenum err=glewInit();
  if(err!=GLEW_OK) {
    sprintf(lasterr,"%s\n",glewGetErrorString(err));
    return false;
  }
  /*
  if(!GLEW_ARB_vertex_program || !GLEW_ARB_fragment_program )
    {
			printf("Extension: 'ARB_fragment_program' and/or 'ARB_vertex_program' not supported.\n");
			return false;
	}
  */
  return true;
}

/*
int CgUtil::loadVertexProgram(const char *str) {
  unsigned int program;
  checkError();
  glGenProgramsARB(1, &program);
  checkError();
  glBindProgramARB(GL_VERTEX_PROGRAM_ARB, program);
  checkError();
  char *text = readFile(str);
  if(!text) {
    printf("could not find file %s\n", str);
    exit(0);
  }
  glProgramStringARB(GL_VERTEX_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(text), text);

  if(!checkProgramError(text)) {
    delete []text;
    return -1;
  }
  delete []text;
  return program;
}
int CgUtil::loadFragmentProgram(const char *str) {
  unsigned int program;
  glGenProgramsARB(1, &program);
  checkError();
  glBindProgramARB(GL_FRAGMENT_PROGRAM_ARB, program);
  checkError();
  char *text = readFile(str);
  if(!text) {
    printf("could not find file %s\n", str);
    exit(0);
  }
  char *c=text;
  while ((*c)!=0) {
    if ((*c == '(') || (*c == ')') ) *c=' ';
    if ( *c == '/') *c='#';
    c++;
  }
  glProgramStringARB(GL_FRAGMENT_PROGRAM_ARB, GL_PROGRAM_FORMAT_ASCII_ARB, strlen(text), text);  
  if(!checkProgramError(text)) {
    delete []text;
    return -1;
  }
  return program;
}
*/

bool CgUtil::checkError() {
  int error = glGetError();
  if(error == GL_NO_ERROR)
    return true;
  const char *str;
  switch(error) {
    case GL_INVALID_ENUM:      str = "Invalid Enum"; break;
    case GL_INVALID_OPERATION: str = "Invalid Operation"; break;
    case GL_INVALID_VALUE:     str = "Invalid Value"; break;
    case GL_STACK_OVERFLOW:    str = "Stack Overflow"; break;
    case GL_STACK_UNDERFLOW:    str = "Stack Underflow"; break;    
    case GL_OUT_OF_MEMORY:     str = "Out of memory"; break;
    default: str = "Unknown error"; break;
  }
  printf("Error %s (%d)\n", str, error);
  return false;
}

bool CgUtil::checkProgramError(char *st) {
 bool res=true;
 while (1)  {
  int error = glGetError();
  if(error == GL_NO_ERROR ) return res;

  res=false;  
  if(error == GL_INVALID_OPERATION) {

    GLint errPos;
    glGetIntegerv( GL_PROGRAM_ERROR_POSITION_ARB, &errPos );
    const GLubyte *errString = glGetString( GL_PROGRAM_ERROR_STRING_ARB);
    fprintf( stderr, "error at position: %d\n[%s]\n", errPos, errString );
    fprintf(stderr,"\n\"...");  
    for (int i=errPos-40; i<errPos+40; i++) 
      if (i>=0) { 
         if (!st[i]) break; 
         if (i==errPos) fprintf(stderr,"(*)");
         fprintf(stderr,"%c", (st[i]=='\n')?'\\':st[i] ); 
      }
    fprintf(stderr,"...\"\n");  
  } else {
    const GLubyte *errString = gluErrorString( error );
    fprintf( stderr, "error: [%s]\n", errString );
  }
 }
}


char *CgUtil::readFile(const char *file) {
  FILE *fp = fopen(file, "r");
  if(!fp) return NULL;
  char *pippo = new char[1<<18];
  int tot = 0;
  while(1) {
    int nread = fread(pippo + tot, 1, 1024, fp);
    tot += nread;
    if(nread < 1024) {
      pippo[tot] = '\0';
      break;
    }
  }
  fclose(fp);
  return pippo;
}


void CgUtil::ShowShaderInfo(int fp){
	static GLint i[10],j[10],k[10],h[10];
	
	glGetProgramivARB(fp, GL_MAX_PROGRAM_INSTRUCTIONS_ARB,     i);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_ALU_INSTRUCTIONS_ARB, i+1);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_TEX_INSTRUCTIONS_ARB, i+2);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_TEX_INDIRECTIONS_ARB, i+3);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_TEMPORARIES_ARB,      i+4);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_PARAMETERS_ARB,       i+5);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_ATTRIBS_ARB,          i+6);

	glGetProgramivARB(fp, GL_PROGRAM_INSTRUCTIONS_ARB,     j);
	glGetProgramivARB(fp, GL_PROGRAM_ALU_INSTRUCTIONS_ARB, i+1);
	glGetProgramivARB(fp, GL_PROGRAM_TEX_INSTRUCTIONS_ARB, j+2);
	glGetProgramivARB(fp, GL_PROGRAM_TEX_INDIRECTIONS_ARB, j+3);
	glGetProgramivARB(fp, GL_PROGRAM_TEMPORARIES_ARB,      j+4);
	glGetProgramivARB(fp, GL_PROGRAM_PARAMETERS_ARB,       j+5);
	glGetProgramivARB(fp, GL_PROGRAM_ATTRIBS_ARB,          j+6);

	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_INSTRUCTIONS_ARB,     k);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB, k+1);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB, k+2);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB, k+3);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_TEMPORARIES_ARB,      k+4);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_PARAMETERS_ARB,       k+5);
	glGetProgramivARB(fp, GL_PROGRAM_NATIVE_ATTRIBS_ARB,          k+6);

	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_INSTRUCTIONS_ARB,     h);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB, h+1);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB, h+2);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB, h+3);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_TEMPORARIES_ARB,      h+4);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_PARAMETERS_ARB,       h+5);
	glGetProgramivARB(fp, GL_MAX_PROGRAM_NATIVE_ATTRIBS_ARB,          h+6);

  
	char st[10][10]={"Instr","Alu Instr","Tex Instr","Tex Indir","Temp","Param","Attr"};
  printf("            %s PROGRAM STATS       \n", 
          (fp==GL_FRAGMENT_PROGRAM_ARB)?"FRAGMENT":"VERTEX");
  printf("              original    |  native         \n");
  printf("            MAX   current |    MAX   current\n");
	for (int c=0; c<7; c++) {
	printf( "%10s   %5d %5d  |  %5d %5d\n",st[c],i[c],j[c],h[c],k[c]);
	}
  printf("\n\n");
}
