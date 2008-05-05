
class GeoSettings {
public:
  typedef enum{ SPACE_FILL, BALL_N_STICKS, LICORICE }  GeoMode;
  
  GeoMode mode;
  
  float stickRadius;
  float ballRadius;
  float licoRadius;

  bool stick_smooth_color;
  bool use_stick_const_color;
  float stick_const_color_R,stick_const_color_G,stick_const_color_B;
  
  bool showHetatm;
  
  void SetDefaults(){
    mode=SPACE_FILL;
    //stickRadius=0.2;
    SetLicoRadiusPercentage(50);
    SetStickRadiusPercentage(100);
    SetBallRadiusPercentage(100);
    //licoRadius=0.6;
    
    stick_smooth_color = false;
    use_stick_const_color = false;
    stick_const_color_R=0.75;
    stick_const_color_G=0.50;
    stick_const_color_B=0.50;
    
    showHetatm = false;

  }  
  
  void Rotate(){
    mode=(GeoMode)((((int)mode)+1)%3);
  }
  
  GeoSettings() {
     SetDefaults();
  }
  
  void Apply();
  void ApplyColor();
  
  void SetLicoRadiusPercentage(int percentage){
    licoRadius = 0.3 + percentage/100.0*0.65;
  }

  int GetLicoRadiusPercentage(){
    return int(100.0*((licoRadius - 0.3)/0.65));
  }

  void SetStickRadiusPercentage(int percentage){
    const float tmp=0.32 * 0.85-0.16;
    stickRadius = 0.16 + percentage/10.0*tmp;
  }

  int GetStickRadiusPercentage(){
    const float tmp=0.32 * 0.85-0.16;
    return int(10.0*((stickRadius - 0.16)/tmp));
  }
  
  void SetBallRadiusPercentage(int percentage){
    const float tmp=0.32 * 0.85-0.16;
    ballRadius = 0.16 + percentage/10.0*tmp;
  }

  int GetBallRadiusPercentage(){
    const float tmp=0.32 * 0.85-0.16;
    return int(10.0*((ballRadius - 0.16)/tmp));
  }
  
};

// drawing settings
class CgUtil {
public:

  
  // RENDERING PARAMETERS:
  // Settarli a piacere e poi chiamare setShaders...
  /////////////////////////////////////////////
  
  /*  SERIALIZE_BEGIN   */

  float P_light_base; // from 0 (dark) to 1 (bright)
  float P_lighting;   // from 0 (no lighting) to 1 (full lighting)
  float P_phong;      // from 0 (no phong lighting) to 1 (full lighting)
  float P_phong_size; // from 0 (POW=100) to 1 (POW=1)
  
  float P_col_atoms_sat;  // base color: saturation
  float P_col_atoms_bri;  // base color: brightness
  
  float P_texture;    // FOR AO! from 0 (no AO) to 1 full AO
  float P_border_inside; // size of antialiased borders inside, in % of atom
  float P_border_outside; // borders outside (pure black), full size
  float P_depth_full;     // size of depth step for a full border

  bool P_sem_effect;   
    
  float P_halo_size;
  float P_halo_col;
  float P_halo_str;
  float P_halo_aware;
  
  float P_fog; 
  
  bool P_capping; // capping
  float P_shadowstrenght; // how much light 

  float P_bg_color_R;
  float P_bg_color_G;
  float P_bg_color_B;

  bool auto_normalize;
  
  bool P_double_shadows;
  
  bool P_border_fixed;
  
  /*  SERIALIZE_END   */

  bool do_use_doubleshadow();
  bool can_use_doubleshadow();
  bool P_use_shadowmap() {return P_shadowstrenght>0; };

  // Save and load the above
  bool Load(const char* filename);
  bool Save(const char* filename);
  
  // Set
  void  Set();
  
  // coming from GeoSettings
  bool P_cyl_smooth_color;
  bool P_cyl_const_color;
  float P_cyl_const_color_R,P_cyl_const_color_G,P_cyl_const_color_B;
  float P_ball_radius;
  
  void setGeoSettings(const GeoSettings &gs);

  // Error messages
  static char lasterr[255];

  enum { USE_OCTA, USE_CUBE } textmode; // textmode
  enum {  PERSPECTIVE, ORTHO } projmode; // projmode
  bool proj_figa;
  
  void SetDefaults();    // set defoult params 
  void SetForOffLine();  // set defoult params for an offscreen rendering
  void SetForShadowMap(bool accurate);// set defoult params for an offscreen rendering
  void MakeShaders();    // activates params 
  void UpdateShaders() {shadersMade=false;};    // activates params 
  void BindShaders();    // binds, loads if necessary
  
  void MakeStickShaders();  
  void BindStickShaders();  
  
  bool BindDrawAOShader();
  bool MakeDrawAOShader();
  
  bool BindDrawAOShaderSticks();
  bool MakeDrawAOShaderSticks();
  
  bool UseHalo();
  
  bool BindHaloShader(int powres); // 1^pow = size of halo texture
  bool MakeHaloShader(int powres);
  
  // questi sono settati automaticamente
  /////////////////////////////////////
  float gap; // gap, % of border texels to be skipped
  int textureSideX,textureSideY;
  bool writeAlpha; // true during probe rendering only
  bool writeCol; // write a color at all?
  
  static bool init();
	static void ShowShaderInfo(int i);
  static bool checkError();
  static bool checkProgramError(char *st);
  static bool shaderHasChanged;
  
  float cyl_radius;

  bool doingAlphaSnapshot; // lots of things change when doing an alpha snapshot  

  CgUtil();
  
  void ResetHalo();
  
private:
  
  enum {MAXPOW=15};

  bool shadersMade;
  
  float norm;
  void Normalize();
  void UndoNormalize();
         
  bool setBallVertexProgram();
  bool setBallFragmentProgram();

  bool setStickVertexProgram();
  bool setStickFragmentProgram();
  
  /*static int loadVertexProgram(const char *str);
  static int loadFragmentProgram(const char *str);*/

  static char *readFile(const char *file);

  bool loaded, loadedStick, loadedVertexHalo;
  GLuint idf, idv, idfStick, idvStick;

  bool loadedHalo[MAXPOW];
  GLuint idfHalo[MAXPOW];
  GLuint idvHalo;
  
  void LoadVertexHaloShader();
  
  void addDirectLightingSnippet(char* fp);
  void addTexturingSnippet(char* fp);
  void addShadowMapComputationFP(char* fp);
  void addDepthAdjustSnippet(char* fp);
  
  float _border_outside();
  float _border_inside();

  bool shadowmapBuilding;
  bool accurateShadowmapBuilding;



};

