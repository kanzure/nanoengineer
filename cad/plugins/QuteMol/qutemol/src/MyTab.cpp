#ifndef WX_PRECOMP
#include "wx/wx.h"
#endif

//#include "wx/artprov.h"
#include <wx/slider.h>
/*
#include <wx/defs.h>
#include <wx/app.h>
#include <wx/menu.h>
#include <wx/dcclient.h>
*/

//#include <wx/image.h>
#include <GL/glew.h>

#include "MyTab.h"

#include "CgUtil.h"
#include "Common.h"

#include <wx/colordlg.h>
#include <wx/utils.h>
#include <wx/stdpaths.h>
#include <wx/filename.h>

#include "image/logo.xpm"
#include "image/geo1.xpm"
#include "image/geo2.xpm"
#include "image/geo3.xpm"

const float MAX_BLEND = 0.25; // maximal blend factor for colors (when per chain)

// GEOM TAB
////////////

enum{ ID_SetBallnstick=500, ID_SetSpacefill, ID_SetLicorice,
      ID_SetLicoriceRadius, ID_SetBallnstickRadius, ID_SetBallnstickBallRadius,
      
      ID_SetBallnstickSmoothcolor,ID_SetBallnstickBicolor, ID_SetBallnstickConstantcolor,
      
      ID_ChooseBallnstickConstantcolor,ID_SetFog,
      
      ID_SetHetatm,      
      ID_ChooseBgcolor,
      ID_ChooseHAcolor,
      ID_SetBgbrightness,
      ID_SetBaseColorSat,
      ID_SetBaseColorBri,
      ID_SetShine,
      ID_SetShineSize,
      ID_SetLight,
      ID_SetLightBase,
      ID_SetHalo,
      ID_SetAO,
      ID_SetHaloStr,
      ID_SetHaloAware,
      ID_SetAutobalance,
      
      // atom colors
      ID_SetColorPerChain,
      ID_SetColorPerAtom,
      ID_ChangeColorSchema,
      ID_SetColorBlend,
      
//      ID_SetShadow,
      ID_SetShadowStr,
      ID_SetSem,
      ID_SetDoubleShadows,
      ID_SetBorderFixed,
      ID_SetBorderVariable,
      ID_SetBorderDepthAware,
      ID_WebButton,
      ID_WebButton2,
      ID_FirstPreset,
    } ID;
       
       
static wxRadioButton *buttonSetLicorice, *buttonSetSpacefill, *buttonSetBallnstick,
                     *buttonSetColorPerChain, *buttonSetColorPerAtom ;

static wxRadioButton *buttonSetBallnstickBicolor, *buttonSetBallnstickConstantcolor, *buttonSetBallnstickSmoothcolor;

static wxString qutemolwebsite = _T("http://qutemol.sourceforge.net/");
static wxString nanorexQuteMolWebsite =
    _T("http://www.nanoengineer-1.com/QuteMolX");
static wxColor colDisabled, colSticks, colBg(255,255,255);
static float bgbrightness=0.5;

// why not? :-(
//#include<wx/clrpicker.h>
//static wxColourPickerCtrl  *buttonChooseBallnstickConstantcolor;
// fall back:
static wxButton  *buttonChooseBallnstickConstantcolor;
static wxButton  *buttonChooseBgcolor;
static wxButton  *buttonChooseHAcolor;
static wxButton  *buttonChangeColorSchema;

static wxCheckBox  *buttonAutobalance;
static wxCheckBox  *buttonDoubleShadows;
static wxCheckBox  *buttonSem;
static wxCheckBox  *buttonSetHetatm;

static wxSlider *sliderLicorice, *sliderBallnstick, *sliderBallnstickBall,
                *sliderSetBaseColor , *sliderShineSize,
                *sliderAwaren , 
                *sliderSetBgbrightness,
                *sliderLightBase, *sliderLighting, *sliderAO,
                *sliderShadowStr,*sliderHaloAware,
                *sliderHaloSize, *sliderHaloStr,*sliderColorBlend;
        
        
                
static wxStaticText *textLicorice, *textBallnstick, *textShadowStr, *textBallnstickBall,
                    *textBallnstick2, *textShineSize, *textDoubleShadows, 
                    *textAwaren, *textSem, *textLightBase, *textSetHetatm,
                    *textHaloSize, *textHaloStr, *textHaloAware, *textHaloColor,
                    *textColorBlend;

static wxColor normalButtonBg;
static wxColor currentButtonBg;

const int NPreset=15;
static wxButton* preset[NPreset];

static char* presetFile[NPreset] = {
  "presets//real.preset",
  "presets//real2.preset",
  "presets//direct.preset",
  
  "presets//illustr.preset",
  "presets//illustr_new.preset",
  "presets//illustr_motm.preset",

  "presets//qutemol1.preset",
  "presets//qutemol2.preset",
  "presets//qutemol3.preset",
  
  "presets//coolb.preset",
  "presets//coold.preset",
  "presets//borders_cool.preset",
  
  "presets//sem.preset",
  "presets//sem2.preset",
  "presets//shape.preset",
};


static wxString presetName[NPreset]={
  _T("Realistic\n1"),
  _T("Realistic\n2"),
  _T("Direct\nLight Only"),
  
  _T("Illustr-\native 1"),
  _T("Illustr-\native 2"),
  _T("Molecule of\nthe Month"),

  _T("Mixed 1"),
  _T("Mixed 2"),
  _T("Mixed 3"),
  
  _T("Cool\n(bright)"),
  _T("Cool\n(dark)"),
  _T("Cool\nborders"),
  
  _T("Simulated\nS.E.M. 1"),
  _T("Simulated\nS.E.M. 2"),
  _T("Shape\nPerception"),
};

static bool presetEndOfLine[NPreset] = {
  false, true,
  true,
  false, true,
  true,
  false, false, true,
  false, true,
  true,
  false, true,
  true
};

Byte f2b(float x){
  return (Byte)(x*255.0);
}

float b2f(Byte x){
  return ((float)x)/255.0;
}

// quick hack
class SliderTable {
  enum {MAX=100};
  int n;
  wxWindowID id[MAX];
public:
  float* data[MAX];
  wxSlider* slider[MAX];
  SliderTable(){n=0;}
  
  void Add(wxWindowID x, float* y, wxSlider* w){
    if (n<MAX) {
      id[n]=x;
      data[n]=y;
      slider[n]=w;
      n++;
    }
  }
  int operator[](wxWindowID i){
    for (int j=0; j<n; j++) {
      if (id[j]==i) return j;
    }
    return -1;
  }
  
  void UpdateAll(){
    for (int i=0; i<n; i++){
      slider[i]->SetValue(int( (*data[i]*100.0) ) );
    }
  }

} sliderTable;


class ButtonTable {
  enum {MAX=100};
  int n;
  wxWindowID id[MAX];
public:
  bool* data[MAX];
  wxCheckBox* chk[MAX];
  ButtonTable(){n=0;}
  
  void Add(wxWindowID x, bool* y, wxCheckBox* w){
    if (n<MAX) {
      id[n]=x;
      data[n]=y;
      chk[n]=w;
      n++;
    }
  }
  int operator[](wxWindowID i){
    for (int j=0; j<n; j++) {
      if (id[j]==i) return j;
    }
    return -1;
  }
  
  void UpdateAll(){
    for (int i=0; i<n; i++){
      chk[i]->SetValue(*(data[i]));
    }
  }

} buttonTable;


wxWindow *MyTab::frame2redraw;

bool doAutobalance(int lastChanged){
  if (buttonAutobalance->GetValue()) {
    float* a[2];
    //a[0]=&cgSettings.P_light_base;
    a[0]=&cgSettings.P_lighting;
    a[1]=&cgSettings.P_texture;
    
    wxSlider* s[2];
    //s[0]=sliderLightBase; 
    s[0]=sliderLighting; 
    s[1]=sliderAO;
    
    int fixed=-1;
    switch (lastChanged){
      //case ID_SetLightBase:fixed=0; break;
      case ID_SetLight:fixed=0; break;
      case ID_SetAO:fixed=1; break;
    }
    float sum=0, sump=0;
    for (int i=0; i<2; i++) {
      sum+=*(a[i]);
      if (i==fixed) sump+=*(a[i]);
    }
    
    if (fixed==-1) {
      if (sum!=0) for (int i=0; i<2; i++) { 
        *(a[i])/=sum;
        s[i]->SetValue( (int)((*a[i])*100.0) );
      }

    } else {
      for (int i=0; i<2; i++) if (i!=fixed) {
        *(a[i])=1-sump;
        s[i]->SetValue( (int)((*a[i])*100.0) );
      }
    }
    
  }
  return false;
}

void MyTab::OnSlider(wxScrollEvent & event){
  wxWindowID id=event.GetId();
  
  if ( (id==ID_SetHalo) || (id==ID_SetHaloStr) ) cgSettings.ResetHalo();
  
  switch ( id ) {
  case ID_SetLicoriceRadius: {
    
    geoSettings.SetLicoRadiusPercentage(  sliderLicorice->GetValue()  );
    geoSettings.Apply();
    SceneChanged();
    break;
  }
  case ID_SetBallnstickRadius: {
    geoSettings.SetStickRadiusPercentage( sliderBallnstick->GetValue() );
    geoSettings.Apply();
    SceneChanged();
    break;
  }

  case ID_SetBallnstickBallRadius: {
    geoSettings.SetBallRadiusPercentage( sliderBallnstickBall->GetValue() );
    geoSettings.Apply();
    SceneChanged();
    break;
  }
  
  case ID_SetColorBlend: {
    SetColMode( sliderColorBlend->GetValue()*0.01f* MAX_BLEND );
    SceneChanged();
    break;
  }
  
  default: 
    int i=sliderTable[id];
    

    if (i!=-1)  {
      float k=(sliderTable.slider[i]->GetValue())/100.0;
      *sliderTable.data[i]=k;
      
      //if ((id==ID_SetAO) && (k>0)) mol.ShowingAO=false;

      if (id==ID_SetBgbrightness) {
        setSceneBgbrightness(bgbrightness);
      }
      
      doAutobalance(id);
      
      cgSettings.UpdateShaders();
      SceneChanged();
      //geoSettings.Apply();
      EnableCustom();
    } //else wxWindow::OnScroll(event); // default actions.
  }
}

void MyTab::OnRadioButton(wxCommandEvent & event){
  int id=event.GetId();
  switch ( id ) {
    
   case ID_SetBallnstick: 
     geoSettings.mode=GeoSettings::BALL_N_STICKS;
     geoSettings.Apply();
     break;
     
   case ID_SetLicorice: 
     geoSettings.mode=GeoSettings::LICORICE;
     geoSettings.Apply();
     break;
     
   case ID_SetSpacefill:
     geoSettings.mode=GeoSettings::SPACE_FILL;
     geoSettings.Apply();
     break;
     
   case ID_SetBallnstickSmoothcolor:
     geoSettings.use_stick_const_color=false;
     geoSettings.stick_smooth_color=true;
     geoSettings.ApplyColor();
     break;
     
   case ID_SetBallnstickBicolor: 
     geoSettings.use_stick_const_color=false;
     geoSettings.stick_smooth_color=false;
     geoSettings.ApplyColor();
     break;
     
   case ID_SetBallnstickConstantcolor:
     geoSettings.use_stick_const_color=true;
     geoSettings.ApplyColor();
     break;

   case ID_SetColorPerChain:
     SetColMode(sliderColorBlend->GetValue()*0.01f* MAX_BLEND );
     SceneChanged();
     break;

   case ID_SetColorPerAtom:
     SetColMode(1); 
     SceneChanged();
     break;
     
  }
  EnableGeom();
}

void MyTab::OnCheckBox(wxCommandEvent & event){
  int id=event.GetId();
  int i=buttonTable[id];

  
  switch ( id ) {
    case ID_SetAutobalance:
      if (doAutobalance(ID_SetAutobalance)) {
        SceneChanged();
        cgSettings.UpdateShaders();
      }
      break;
    case ID_SetHetatm: 
      geoSettings.Apply(); 
      break;
    case ID_SetDoubleShadows: 
      UpdateShadowmap(); 
      break;
  }
  
  if (i!=-1)  {
    bool k=(buttonTable.chk[i]->GetValue());
    *buttonTable.data[i]=k;
    
    cgSettings.UpdateShaders();
    SceneChanged();
    EnableCustom();
  }
  
}

void MyTab::OnButton(wxCommandEvent & event){
  wxColourDialog* dialog;
  wxColourData data;

  int id=event.GetId();  
  
  switch ( id ) {
    
  case ID_ChangeColorSchema: 
    ChangeColorSchema();
    ResetColMode();
    SceneChanged();
    break;

  case ID_WebButton:
    if (!wxLaunchDefaultBrowser(qutemolwebsite)) {
       wxMessageBox(_T("Browser, browser,\nwhere art thou?"), _T(":-("), wxOK | wxICON_EXCLAMATION, this);
    }
    break;

  case ID_WebButton2:
    if (!wxLaunchDefaultBrowser(nanorexQuteMolWebsite)) {
       wxMessageBox(_T("Browser, browser,\nwhere art thou?"), _T(":-("), wxOK | wxICON_EXCLAMATION, this);
    }
    break;

  case ID_ChooseBallnstickConstantcolor: 
    data.SetChooseFull(true);
    data.SetCustomColour(0, colBg );
    data.SetColour(colSticks);

    dialog=new wxColourDialog(this,&data);
    dialog->SetTitle(_T("Choose stick color:"));
    if (dialog->ShowModal() == wxID_OK)
    {
      colSticks = dialog->GetColourData().GetColour();
      geoSettings.stick_const_color_R=b2f(colSticks.Red());
      geoSettings.stick_const_color_G=b2f(colSticks.Green());
      geoSettings.stick_const_color_B=b2f(colSticks.Blue());
      buttonChooseBallnstickConstantcolor->SetBackgroundColour(colSticks);
      geoSettings.ApplyColor();
      SceneChanged();
    }
  break;
  
  case ID_ChooseHAcolor: 
    {
    cgSettings.P_halo_col=1.0*(cgSettings.P_halo_col!=1);
    int k=(int)(cgSettings.P_halo_col*255.0);
    buttonChooseHAcolor->SetBackgroundColour(wxColor(k,k,k));
    
    cgSettings.ResetHalo();
    cgSettings.UpdateShaders();
    SceneChanged();
    }
    break;

  case ID_ChooseBgcolor: 
    
    data.SetChooseFull(true);
    data.SetCustomColour(0, colBg);
    data.SetColour(colBg);

    dialog=new wxColourDialog(this,&data);
    dialog->SetTitle(_T("Choose background color:"));
    if (dialog->ShowModal() == wxID_OK)
    {
      setSceneBgcolor(dialog->GetColourData().GetColour());
      cgSettings.UpdateShaders();
      SceneChanged();
    }
  break;

  default:
    int pid=id-ID_FirstPreset;
    
    // Determine absolute path to presets
    wxStandardPaths standardPaths;
    wxString presetsPath = standardPaths.GetExecutablePath();
    wxFileName fileName(presetsPath);
    presetsPath = fileName.GetPath(wxPATH_GET_SEPARATOR);
    
    if ( (pid>=0) && (pid<NPreset) ) {
#ifdef __DARWIN__
                        wxString presetPath = wxStandardPaths::Get().GetResourcesDir() + "/" + presetFile[pid];
                        if (!cgSettings.Load( presetPath.c_str() )) {
#else
      if (!cgSettings.Load( presetFile[pid] )) {
#endif
        wxMessageBox(_T("Unable to load presets!"), _T(":-("), wxOK | wxICON_EXCLAMATION, this);
      }
      emphCurrentPreset(pid);
      //cgSettings.Set();
      
      UpdateAll();
      
      cgSettings.ResetHalo();
      cgSettings.UpdateShaders();
      SceneChanged();
    }
   break;
  
  
  }
}

void MyTab::emphCurrentPreset(int j){
/*   for (int i=0; i<NPreset; i++) {
      if (i!=j) preset[i]->SetForegroundColour(normalButtonBg);
      else preset[i]->SetForegroundColour(currentButtonBg);
   }
*/
//  preset[j]->Press();
}


void MyTab::setSceneBgcolor(wxColor c){
  float r=b2f(c.Red()),
        g=b2f(c.Green()),
        b=b2f(c.Blue());
  float max=(r<g)?g:r;
  max=(max<b)?b:max;
  
  bgbrightness = max;
  
  cgSettings.P_bg_color_R=r;
  cgSettings.P_bg_color_G=g;
  cgSettings.P_bg_color_B=b;      
  
  if (bgbrightness==0) colBg.Set(255,255,255); else
  colBg.Set( Byte(r/max*255.0), Byte(g/max*255.0), Byte(b/max*255.0));
  
  buttonChooseBgcolor->SetBackgroundColour(c);
  sliderSetBgbrightness->SetValue(int(bgbrightness*100));
}

wxColor col(float r, float g, float b){
  wxColor c( Byte(r*255.0), Byte(g*255.0), Byte(b*255.0));
  return c; 
}

wxColor col(float r){
  return col(r,r,r); 
}

void MyTab::setSceneBgbrightness(float br){
  
  bgbrightness=br;
  
  float r=colBg.Red()*bgbrightness/255.0,
        g=colBg.Green()*bgbrightness/255.0,
        b=colBg.Blue()*bgbrightness/255.0;
        
  //if (r+b+g<0.01) r=g=b=bgbrightness/255.0;
  
  cgSettings.P_bg_color_R=r;
  cgSettings.P_bg_color_G=g;
  cgSettings.P_bg_color_B=b;      
  
  buttonChooseBgcolor->SetBackgroundColour( col(r,g,b) );
}

void MyTab::EnableCustom(){
  
  bool b=(cgSettings.P_phong>0);
  sliderShineSize->Enable(b);
  textShineSize->Enable(b);

  b=(cgSettings.P_border_outside>0);
  sliderAwaren->Enable(b);
  textAwaren->Enable(b);

  b=(cgSettings.P_lighting>0)||(cgSettings.P_phong>0);
  textShadowStr->Enable(b);
  sliderShadowStr->Enable(b);
  
  b=(cgSettings.P_lighting>0);
  textLightBase->Enable(b);
  sliderLightBase->Enable(b);
  
  b=( cgSettings.can_use_doubleshadow() );
  
  if (!b) buttonDoubleShadows->SetValue(false);
  else buttonDoubleShadows->SetValue(cgSettings.P_double_shadows);
  
  buttonDoubleShadows->Enable(b);
  textDoubleShadows->Enable(b);
  
  b = cgSettings.P_halo_size>0;
  sliderHaloStr->Enable(b);
  sliderHaloAware->Enable(b);
  textHaloStr->Enable(b);
  textHaloAware->Enable(b);
  textHaloColor->Enable(cgSettings.UseHalo());
  buttonChooseHAcolor->Enable(cgSettings.UseHalo());
  
}


void MyTab::EnableGeom(){
  
  
  
  
  bool lico=false, bns=false, sf=false;
  if (geoSettings.mode == GeoSettings::SPACE_FILL) sf=true;
  if (geoSettings.mode == GeoSettings::LICORICE) lico=true;
  if (geoSettings.mode == GeoSettings::BALL_N_STICKS) bns=true;
  
  buttonSetLicorice->SetValue(lico);
  buttonSetSpacefill->SetValue(sf);
  buttonSetBallnstick->SetValue(bns);
  sliderBallnstick->Enable(bns);
  textBallnstick->Enable(bns);
  sliderBallnstickBall->Enable(bns);
  textBallnstickBall->Enable(bns);
  textBallnstick2->Enable(bns);
  sliderLicorice->Enable(lico);
  textLicorice->Enable(lico);
  
  float c=GetColMode();
  
  //sliderColorBlend->SetValue(int(c*100*1.0f)); 
  buttonSetColorPerChain->SetValue(c!=1); 
  buttonChangeColorSchema->Enable(c!=1);
  sliderColorBlend->Enable(c!=1); 
  textColorBlend->Enable(c!=1);
  buttonSetColorPerAtom->SetValue(c==1);   
  
  buttonSetBallnstickBicolor->Enable(bns);
  buttonSetBallnstickConstantcolor->Enable(bns);
  buttonSetBallnstickSmoothcolor->Enable(bns);
  
  //buttonChooseBallnstickConstantcolor->Enable(bns && constant);
  

  if (bns) {
    bool bi, constant, smooth;
    constant = (geoSettings.use_stick_const_color);
    smooth = (!constant) & (geoSettings.stick_smooth_color);
    bi = (!smooth) && (!constant);
    
    buttonSetBallnstickBicolor->SetValue(bi);
    buttonSetBallnstickConstantcolor->SetValue(constant);
    buttonSetBallnstickSmoothcolor->SetValue(smooth);

    buttonChooseBallnstickConstantcolor->Enable(constant);
    if (constant) {
      colSticks.Set( 
        f2b(geoSettings.stick_const_color_R),
        f2b(geoSettings.stick_const_color_G),
        f2b(geoSettings.stick_const_color_B)
      );
      buttonChooseBallnstickConstantcolor->SetBackgroundColour(colSticks);
    } else
      buttonChooseBallnstickConstantcolor->SetBackgroundColour(colDisabled);
  } else {
    buttonChooseBallnstickConstantcolor->SetBackgroundColour(colDisabled);
    buttonChooseBallnstickConstantcolor->Enable(false);
  }
  
  /*bool b=
  sliderColorBlend()->GetValue()*0.01f *0.1f);*/
  
  int h=GetCurrentHetatm();
  int a=GetCurrentAtm();
  bool e=true, set=geoSettings.showHetatm;
  if ((h==0) && (a!=0)) {e=false;set=false;}
  if ((h!=0) && (a==0)) {e=false;set=true;}
  buttonSetHetatm->Enable(e);
  textSetHetatm->Enable(e);
  buttonSetHetatm->SetValue(set);
  
  SceneChanged();

}

int MyTab::Count(){
  return 4;
}



wxString MyTab::Title(int i)
{
  switch (i) {
   case 0: return wxString(_T("Presets")); break;
   case 1: return wxString(_T("Geometry")); break;
   case 2: return wxString(_T("Customize")); break;
   case 3: return wxString(_T("Info")); break;
  }
  return wxString(_T(""));
}

BEGIN_EVENT_TABLE(MyTab, wxPanel)
    EVT_RADIOBUTTON(-1, MyTab::OnRadioButton)
    /*EVT_RADIOBUTTON(ID_SetLicorice, MyTab::OnSetLicorice)
    EVT_RADIOBUTTON(ID_SetSpacefill, MyTab::OnSetSpacefill)
    
    EVT_RADIOBUTTON(ID_SetBallnstickSmoothcolor, MyTab::OnSetBallnstickSmoothcolor)
    EVT_RADIOBUTTON(ID_SetBallnstickBicolor, MyTab::OnSetBallnstickBicolor)
    EVT_RADIOBUTTON(ID_SetBallnstickConstantcolor, MyTab::OnSetBallnstickConstantcolor)*/
    
    EVT_BUTTON(-1, MyTab::OnButton)
    EVT_COMMAND_SCROLL_THUMBTRACK(-1, MyTab::OnSlider)
    EVT_CHECKBOX(-1, MyTab::OnCheckBox)
    //EVT_BUTTON(ID_ChooseBallnstickConstantcolor, MyTab::OnChooseBallnstickConstantcolor)
    //EVT_COMMAND_SCROLL(ID_SetLicoriceRadius, MyTab::OnSetLicoriceRadius)
    //EVT_COMMAND_SCROLL(ID_SetBallnstickRadius, MyTab::OnSetBallnstickRadius)
END_EVENT_TABLE()

wxBitmap *LoadPngImage(wxString st);

wxSlider* tmpSlider;
wxCheckBox* tmpChk;
wxStaticText* tmpStaticText;
wxSizer *newLabelledSlider( wxWindow* parent, wxWindowID  idSlider,
                         const wxString& labelString, 
                         int pos ,
                         wxSlider* &slider=tmpSlider,
                         wxStaticText* &label = tmpStaticText) {
  // 
  wxSizer *res = new wxBoxSizer(wxHORIZONTAL);
  label=new wxStaticText(parent, wxID_ANY, labelString);
  slider=new wxSlider(parent,idSlider, pos, 0, 100, wxDefaultPosition, wxDefaultSize/*,  wxNO_FULL_REPAINT_ON_RESIZE */ );
  res->Add(label, 0);
  res->Add(slider, 1, wxEXPAND);
  return res;
}


static int SLIDERSIZE=80;

wxSizer *newAutoSlider( wxWindow* parent, wxWindowID  idSlider,
                        const wxString& labelString, 
                        float *pos ,
                        wxSlider* &slider=tmpSlider,
                        wxStaticText* &label=tmpStaticText) {
  // 
  wxSizer *res = new wxBoxSizer(wxHORIZONTAL);
  label=new wxStaticText(parent, wxID_ANY, labelString);
  slider=new wxSlider(parent,idSlider, 
     int((*pos)*100.0f), 0, 100, wxDefaultPosition, wxSize(SLIDERSIZE,wxDefaultSize.y),  wxNO_FULL_REPAINT_ON_RESIZE  
  );
  res->Add(label, 0);
  res->Add(slider, 0);
  
  sliderTable.Add(idSlider, pos, slider);
  return res;
}

#define AUTO_TEXT_ON_RIGHT 1

wxSizer *newAutoCheckBox(wxWindow* parent, wxWindowID  idChk,
                        const wxString& labelString, 
                        bool *value,
                        wxCheckBox* &chk=tmpChk,
                        wxStaticText* &label=tmpStaticText,
                        int flags=0) {
  // 
  wxSizer *res = new wxBoxSizer(wxHORIZONTAL);
  label=new wxStaticText(parent, wxID_ANY, labelString);
  chk=new wxCheckBox(parent,idChk, _T(""));
  chk->SetValue(*value);
  
  if (flags&AUTO_TEXT_ON_RIGHT) {
    //res->Add(SLIDERSIZE - 10 - chk->GetSize().x ,0,1);
    res->Add(chk, 0, wxBOTTOM | wxTOP, 3);
    res->Add(10 ,0,0);
    res->Add(label, 0, wxALIGN_CENTER);
  }
  else {
    res->Add(label, 0, wxALIGN_CENTER);
    res->Add(10 ,0,0);
    res->Add(chk, 0, wxBOTTOM | wxTOP, 3);
    res->Add(SLIDERSIZE - 10 - chk->GetSize().x ,0,1);
  }
  
  buttonTable.Add(idChk, value, chk);
  return res;
}

static wxSizer *globalSizerH=NULL;
static wxSizer *globalSizerV=NULL;
static wxBoxSizer *sizerR, *sizerL;

// returns an emphatized version of a given color
wxColor emphColor(wxColor c){
  unsigned char rgb[3];
  rgb[0]=c.Red();
  rgb[1]=c.Green();
  rgb[2]=c.Blue();
  for (int i=0; i<3; i++)
  {
    int K=100;
    if (rgb[i]>255-K) rgb[i]-=K;
    else if (rgb[i]>128) rgb[i]+=K;
    else if (rgb[i]>K) rgb[i]-=K;
    else rgb[i]+=K;
  }
  return wxColor(rgb[0],rgb[1],rgb[2]);
}

int _TH;
//wxSizer *obj1, *obj2;

// remove newlines from a strings
wxString noNewLine(wxString x){
  static wxString res;
  res.Clear();
  for (int i=0; i<x.Length(); i++){
    if ((x[i]=='-')&&(x[i+1]=='\n')) i++;
    else 
    if (x[i]=='\n') res.sprintf("%s ",res.ToAscii());
    else res.sprintf("%s%c",res.ToAscii(),x[i]);
  }
  return res;
}

MyTab::MyTab(wxWindow *parent , int n): wxPanel( parent, wxID_ANY, wxDefaultPosition, wxDefaultSize,
                                                 /*wxNO_FULL_REPAINT_ON_RESIZE |*/ wxCLIP_CHILDREN | wxTAB_TRAVERSAL)
{
  
  int i;
  
  bool thinButtons=false;
#ifdef __DARWIN__
  thinButtons=true; // unsupported newlines in wxButtons under MAC! :(
#endif

  if (n==0) { // presets tab (visual presets)
    wxSizer *sizer,*subSizer=NULL;
    if (thinButtons) sizer = new wxBoxSizer(wxVERTICAL);
    else sizer = new wxGridSizer(5,3,15,15);
    
    wxSize butSize; 
    //if (thinButtons) butSize= wxSize(90,-1); // -1 = use default button height
    if (thinButtons) butSize= wxSize(90,24); // -1 = use default button height
    else butSize= wxSize(70,50);
    
    for (int i=0; i<NPreset; i++) {
      preset[i]=new wxButton(this, ID_FirstPreset + i, 
        thinButtons?noNewLine(presetName[i]):presetName[i], 
        wxDefaultPosition); //, butSize );
      preset[i]->SetMinSize(butSize);
      if (presetName[i]==wxEmptyString) preset[i]->Show(false);
      if (thinButtons) {
        if (!subSizer) subSizer=new wxBoxSizer(wxHORIZONTAL);
        subSizer->Add( preset[i], 1, wxALIGN_CENTER|wxEXPAND|wxALL,4 );
        if (presetEndOfLine[i]) {
          sizer->Add( subSizer, 1, wxALIGN_CENTER|wxEXPAND);
          subSizer=NULL;
        }
      } else {
        sizer->Add( preset[i], 1, wxALIGN_CENTER );
      }
    }
    
    normalButtonBg=preset[0]->GetForegroundColour();
    currentButtonBg=emphColor(normalButtonBg);

    wxSizer *topLvlSizer = new wxBoxSizer(wxVERTICAL);
//    topLvlSizer->Add(10,10,0);
    topLvlSizer->Add(1,1,1);
    topLvlSizer->Add(sizer,0, wxALIGN_CENTER); //|wxEXPAND);
    topLvlSizer->Add(1,1,1);
    SetSizer(topLvlSizer);
  }
  if (n==1) { // geometry tab (ball and stick, stick radius, etc)
    

    
    wxStaticBox *box1 = new wxStaticBox(this, wxID_ANY, _T("Space-Fill") );
    wxSizer *sizer1 = new wxStaticBoxSizer(box1, wxHORIZONTAL);
    
    buttonSetSpacefill = new wxRadioButton(this, ID_SetSpacefill, _T(""), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
    
    wxBitmap geo1Bitmap(geo1_xpm, wxBITMAP_TYPE_XPM);
    wxStaticBitmap *bitmap1 = new wxStaticBitmap(this, wxID_ANY, geo1Bitmap, wxDefaultPosition );
    
    sizer1->Add(bitmap1);
    sizer1->Add(5, 5,      1,  wxALL, 5); // spacer
    
    wxSizer *sizerMode1 = new wxBoxSizer(wxHORIZONTAL);
    sizerMode1->Add(buttonSetSpacefill, 0, wxRIGHT|wxALIGN_CENTER, 4);
    sizerMode1->Add(sizer1, 1);
    


    wxStaticBox *box2 = new wxStaticBox(this, wxID_ANY, _T("Balls'n'Sticks") );
    wxSizer *sizer2 = new wxStaticBoxSizer(box2, wxHORIZONTAL);
    //sizer2->Enable(false);
    
    buttonSetBallnstick= new wxRadioButton(this, ID_SetBallnstick, _T(""), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
    wxBitmap geo2Bitmap(geo2_xpm, wxBITMAP_TYPE_XPM);
    wxStaticBitmap *bitmap2 = new wxStaticBitmap(this, wxID_ANY, geo2Bitmap, wxDefaultPosition );

    wxSizer *sizer2r = new wxBoxSizer(wxVERTICAL);
      sizer2r->Add( newLabelledSlider( 
        this, ID_SetBallnstickRadius,
        _T("Stick size:"), 
        geoSettings.GetStickRadiusPercentage(),
        sliderBallnstick, 
        textBallnstick
      ) );

      sizer2r->Add( newLabelledSlider( 
        this, ID_SetBallnstickBallRadius,
        _T("Ball size:"), 
        geoSettings.GetBallRadiusPercentage(),
        sliderBallnstickBall, 
        textBallnstickBall
      ) );

      {
      wxSizer *sizer2rr = new wxBoxSizer(wxHORIZONTAL);
        textBallnstick2=new wxStaticText(this, wxID_ANY, _T("Stick color:"));
        sizer2rr->Add(textBallnstick2, 0);
        wxSizer *sizerColbox = new wxBoxSizer(wxVERTICAL);
            buttonSetBallnstickBicolor = new wxRadioButton
                (this, ID_SetBallnstickBicolor, _T("Split"), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
            sizerColbox->Add( buttonSetBallnstickBicolor, 1, wxALL, 1);
            buttonSetBallnstickSmoothcolor = new wxRadioButton
                (this, ID_SetBallnstickSmoothcolor, _T("Blended"), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
            sizerColbox->Add( buttonSetBallnstickSmoothcolor, 1, wxALL, 1);
            buttonSetBallnstickConstantcolor = new wxRadioButton
                (this, ID_SetBallnstickConstantcolor, _T("Constant:"), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
            sizerColbox->Add( buttonSetBallnstickConstantcolor, 1, wxALL, 1);
            
            buttonChooseBallnstickConstantcolor = new wxButton(this, ID_ChooseBallnstickConstantcolor,
              wxEmptyString, wxDefaultPosition, wxSize(16,16),wxNO_BORDER);
            colDisabled = this->GetBackgroundColour();
//            wxColor col(255,0,0);
//            buttonChooseBallnstickConstantcolor ->SetBackgroundColour(col);
            /*
            :-(
            buttonChooseBallnstickConstantcolor = new wxColourPickerCtrl(this, ID_ChooseBallnstickConstantcolor);
            */
            
        sizer2rr->Add(sizerColbox, 1);
        sizer2rr->Add( buttonChooseBallnstickConstantcolor, 0, wxALL|wxALIGN_BOTTOM, 1);
      //sizer2r->Add(5, 5,      0,  wxALL, 5); // spacer
      sizer2r->Add(sizer2rr, 0);
      }
    
    sizer2->Add(bitmap2);
    sizer2->Add(5, 5,      0,  wxALL, 5); // spacer
    sizer2->Add(sizer2r, 1);


    wxSizer *sizerMode2 = new wxBoxSizer(wxHORIZONTAL);
    sizerMode2->Add(buttonSetBallnstick, 0, wxRIGHT|wxALIGN_CENTER, 4);
    sizerMode2->Add(sizer2, 1);


    wxStaticBox *box3 = new wxStaticBox(this, wxID_ANY, _T("Licorice") );
    wxSizer *sizer3 = new wxStaticBoxSizer(box3, wxHORIZONTAL);
    
    buttonSetLicorice = new wxRadioButton(this, ID_SetLicorice, _T(""), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );
    wxBitmap geo3Bitmap(geo3_xpm, wxBITMAP_TYPE_XPM);
    wxStaticBitmap *bitmap3 = new wxStaticBitmap(this, wxID_ANY, geo3Bitmap, wxDefaultPosition );
    
    wxSizer *sizer3r = new wxBoxSizer(wxVERTICAL);
      /*wxSizer *sizer3rr = new wxBoxSizer(wxHORIZONTAL);
        textLicorice=new wxStaticText(this, wxID_ANY, _T("Thickness:"));
        sizer3rr->Add(textLicorice, 0);
        sizer3rr->Add(sliderLicorice, 1);
      sizer3r->Add(5, 5,      0,  wxALL, 5); // spacer*/
      sizer3r->Add( newLabelledSlider( 
        this, ID_SetLicoriceRadius,
        _T("Thickness:"), 
        geoSettings.GetLicoRadiusPercentage(),
        sliderLicorice, 
        textLicorice
      ) , 0, wxALIGN_BOTTOM);

      
    sizer3->Add(bitmap3, 0);
    sizer3->Add(5, 5,      0,  wxALL, 5); // spacer
    sizer3->Add(sizer3r, 1, wxALIGN_CENTER);
    
    
    wxStaticBoxSizer *sizerColors = new wxStaticBoxSizer(new wxStaticBox(this, wxID_ANY, _T("Material Color") ) , wxHORIZONTAL );
    
    wxSizer *subsizerColors = new wxBoxSizer(wxVERTICAL);
    buttonSetColorPerChain = 
      new wxRadioButton(this, ID_SetColorPerChain, _T("Per chain"), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );      

    buttonSetColorPerAtom = 
      new wxRadioButton(this, ID_SetColorPerAtom, _T("Per atom"), wxDefaultPosition, wxDefaultSize, wxRB_SINGLE );      
      
    buttonChangeColorSchema =
      new wxButton(this, ID_ChangeColorSchema, _T("Change cols") ); //_T("Change\ncolor\nschema")
    subsizerColors->Add( buttonSetColorPerAtom ); 
    subsizerColors->Add( buttonSetColorPerChain ); 
    subsizerColors->Add(2,2);
    subsizerColors->Add( 
     newLabelledSlider( 
        this, ID_SetColorBlend,
        _T("Diff:"), 
        0,
        sliderColorBlend, 
        textColorBlend
     ), 1, wxLEFT|wxALIGN_RIGHT,30
    );
    sizerColors->Add( subsizerColors );
    sizerColors->Add(2,2);
    sizerColors->Add( buttonChangeColorSchema, 1, wxRIGHT|wxALIGN_RIGHT|wxALIGN_BOTTOM,5 ); 

    wxSizer *sizerMode3 = new wxBoxSizer(wxHORIZONTAL);
    sizerMode3->Add(buttonSetLicorice, 0, wxRIGHT|wxALIGN_CENTER, 5);
    sizerMode3->Add(sizer3, 1);
    
    wxSizer *sizer = new wxBoxSizer(wxVERTICAL);
    sizer->Add(sizerMode1, 0, wxGROW | wxALL , 4);
    sizer->Add(sizerMode3, 0, wxGROW | wxALL , 4);
    sizer->Add(sizerMode2, 0, wxGROW | wxALL , 4);
    
    wxSizer *sizerG = new wxBoxSizer(wxVERTICAL);
    sizer->Add(5,5,0); // spacer
    sizer->Add(newAutoCheckBox( 
       this,ID_SetHetatm,
        _T("Show 'HET' atmos"), 
        &(geoSettings.showHetatm),
        buttonSetHetatm, textSetHetatm,
        AUTO_TEXT_ON_RIGHT
      ), 0 , wxALIGN_LEFT | wxLEFT,8
     );
    sizer->Add(5,5,0); // spacer
    sizer->Add(sizerColors, 0 , wxALIGN_RIGHT);
    
    sizerG->Add(sizer,0,wxALIGN_CENTER );
    SetSizer(sizerG);
    
    EnableGeom();
    
  }
  if (n==2) { // customize tab (sliders for all graphic fxs)

      
    wxStaticText *label1=new wxStaticText(this, wxID_ANY, _T("Color:"));
    buttonChooseBgcolor=new  wxButton(this, ID_ChooseBgcolor,
              wxEmptyString, wxDefaultPosition, wxSize(16,16),wxNO_BORDER);
    wxSizer *sizerBgcolor = new wxBoxSizer(wxHORIZONTAL);
    
    sizerBgcolor->Add(label1,0,wxALL, 5);
    sizerBgcolor->Add(buttonChooseBgcolor,0,wxALL, 5);
    setSceneBgbrightness(bgbrightness);
              
              
    wxStaticBox *boxBG = new wxStaticBox(this, wxID_ANY, _T("Background") );
    wxSizer *sizerBG = new wxStaticBoxSizer(boxBG, wxVERTICAL);

    sizerBG->Add(newAutoSlider( 
        this, ID_SetBgbrightness,
        _T("Brightn.:"), 
        &(bgbrightness),
        sliderSetBgbrightness
      ), 0 , wxALIGN_RIGHT );

    sizerBG->Add(sizerBgcolor,0 , wxALIGN_CENTER);
    
    wxStaticBox *boxBC = new wxStaticBox(this, wxID_ANY, _T("Base Colors") );
    wxSizer *sizerBC = new wxStaticBoxSizer(boxBC, wxVERTICAL);
    
    sizerBC->Add(newAutoSlider( 
        this, ID_SetBaseColorSat,
        _T("Saturation:"), 
        &(cgSettings.P_col_atoms_sat)
      ), 0 , wxALIGN_RIGHT );

     /*
     // Useless! Redundant with basic light
    sizerBC->Add(newAutoSlider( 
        this, ID_SetBaseColorBri,
        _T("Brightness:"), 
        &(cgSettings.P_col_atoms_bri)
      ), 0 , wxALIGN_RIGHT );
      */

    wxStaticBox *boxPL = new wxStaticBox(this, wxID_ANY, _T("Point Light"));
    wxSizer *sizerPL = new wxStaticBoxSizer(boxPL, wxVERTICAL);
    
    
    sizerPL->Add(newAutoSlider( 
        this, ID_SetLight,
        _T("Intensity*:"), 
        &(cgSettings.P_lighting),
        sliderLighting
      ), 0 , wxALIGN_RIGHT );
      
    sizerPL->Add(newAutoSlider( 
        this, ID_SetLightBase,
        _T("Flatten:"), 
        &(cgSettings.P_light_base),
        sliderLightBase, textLightBase
      ), 0 , wxALIGN_RIGHT );

    sizerPL->Add(newAutoSlider( 
        this, ID_SetShine,
        _T("Shininess:"), 
        &(cgSettings.P_phong)
      ), 0 , wxALIGN_RIGHT );

    sizerPL->Add(newAutoSlider( 
        this, ID_SetShineSize,
        _T("Glossiness:"), 
        &(cgSettings.P_phong_size),
        sliderShineSize, textShineSize
      ), 0 , wxALIGN_RIGHT
    );

/*    sizerPL->Add(newAutoCheckBox( 
       this,ID_SetShadow,
        _T("Cast Shadows:"), 
        &(cgSettings.P_use_shadowmap()),
        buttonShadow, textShadow
      ), 0 , wxALIGN_RIGHT
     );*/


    sizerPL->Add(newAutoSlider( 
        this, ID_SetShadowStr,
        _T("Shadows:"), 
        &(cgSettings.P_shadowstrenght),
        sliderShadowStr, textShadowStr
      ), 0 , wxALIGN_RIGHT
    );

    sizerPL->Add(newAutoCheckBox( 
       this,ID_SetDoubleShadows,
        _T("2way Light:"), 
        &(cgSettings.P_double_shadows ),
        buttonDoubleShadows, textDoubleShadows
      ), 0 , wxALIGN_RIGHT
     );

    sizerPL->Add(newAutoCheckBox( 
       this,ID_SetSem,
        _T("Fake SEM:"), 
        &(cgSettings.P_sem_effect),
        buttonSem, textSem
      ), 0 , wxALIGN_RIGHT
     );

    wxStaticBox *boxDB = new wxStaticBox(this, wxID_ANY, _T("Depth Cueing") );
    wxSizer *sizerDB = new wxStaticBoxSizer(boxDB, wxVERTICAL);
    
    sizerDB->Add(newAutoSlider( 
        this, ID_SetFog,
        _T("Strenght:"), 
        &(cgSettings.P_fog)
      ), 0 , wxALIGN_RIGHT );


    wxStaticBox *boxHA = new wxStaticBox(this, wxID_ANY, _T("Halos") );
    wxSizer *sizerHA = new wxStaticBoxSizer(boxHA, wxVERTICAL);
    
    sizerHA->Add(newAutoSlider( 
        this, ID_SetHalo,
        _T("Size:"), 
        &(cgSettings.P_halo_size),
        sliderHaloSize, textHaloSize
      ), 0 , wxALIGN_RIGHT );

    sizerHA->Add(newAutoSlider( 
        this, ID_SetHaloStr,
        _T("Strenght:"), 
        &(cgSettings.P_halo_str),
        sliderHaloStr, textHaloStr
      ), 0 , wxALIGN_RIGHT );

    sizerHA->Add(newAutoSlider( 
        this, ID_SetHaloAware,
        _T("Variance:"), 
        &(cgSettings.P_halo_aware),
        sliderHaloAware, textHaloAware
      ), 0 , wxALIGN_RIGHT );

    textHaloColor=new wxStaticText(this, wxID_ANY, _T("Color:"));
    buttonChooseHAcolor=new  wxButton(this, ID_ChooseHAcolor,
              wxEmptyString, wxDefaultPosition, wxSize(16,16),wxNO_BORDER);
    buttonChooseHAcolor->SetBackgroundColour( col(cgSettings.P_halo_col) );
    

    wxSizer *sizerHAcolor = new wxBoxSizer(wxHORIZONTAL);


    
 
    sizerHAcolor->Add(textHaloColor,0,wxALL, 5);
    sizerHAcolor->Add(buttonChooseHAcolor,0,wxALL, 5);
    
    sizerHA->Add(sizerHAcolor, 0 , wxALIGN_CENTER);


    // borders

    wxStaticBox *boxBR = new wxStaticBox(this, wxID_ANY, _T("Borders") );
    wxSizer *sizerBR = new wxStaticBoxSizer(boxBR, wxVERTICAL);
    
    /*
    sizerBR->Add(newAutoSlider( 
        this, ID_SetBorderFixed,
        _T("Fixed Size:"), 
        &(cgSettings.P_border_inside)
      ), 0 , wxALIGN_RIGHT );*/

    sizerBR->Add(newAutoSlider( 
        this, ID_SetBorderVariable,
        _T("Size:"), 
        &(cgSettings.P_border_outside)
      ), 0 , wxALIGN_RIGHT );

    sizerBR->Add(newAutoSlider( 
        this, ID_SetBorderDepthAware,
        _T("Variance:"), 
        &(cgSettings.P_depth_full),
        sliderAwaren, textAwaren
      ), 0 , wxALIGN_RIGHT );




    wxStaticBox *boxAO = new wxStaticBox(this, wxID_ANY, _T("Ambient Light") );
    wxSizer *sizerAO = new wxStaticBoxSizer(boxAO, wxVERTICAL);
    
    sizerAO->Add(newAutoSlider( 
        this, ID_SetAO,
        _T("Intensity*:"), 
        &(cgSettings.P_texture),
        sliderAO
      ), 0 , wxALIGN_RIGHT );


    wxSizer *sizerAB = new wxBoxSizer(wxVERTICAL);
    buttonAutobalance = new wxCheckBox(this, ID_SetAutobalance,  _T("* Autobalance") );
    buttonAutobalance->SetValue(false);
    sizerAB->Add(buttonAutobalance, 1, wxALIGN_CENTER );
    buttonTable.Add(ID_SetAutobalance, &(cgSettings.auto_normalize), buttonAutobalance);
    
    int SPACE=6;

    sizerL = new wxBoxSizer(wxVERTICAL);
    sizerL->Add(sizerBC, 0, wxEXPAND);
    sizerL->Add(SPACE,SPACE, 0);
    sizerL->Add(sizerPL, 0, wxEXPAND);
    sizerL->Add(SPACE,SPACE, 0);
    sizerL->Add(sizerAO, 0, wxEXPAND);
    sizerL->Add(SPACE,SPACE, 0);
    sizerL->Add(sizerAB, 0, wxEXPAND|wxALIGN_CENTER );


    /*wxBoxSizer */sizerR = new wxBoxSizer(wxVERTICAL);
    sizerR->Add(sizerBG, 0, wxEXPAND);
    sizerR->Add(SPACE,SPACE, 0);
    sizerR->Add(sizerDB, 0, wxEXPAND);
    sizerR->Add(SPACE,SPACE, 0);
    sizerR->Add(sizerHA, 0, wxEXPAND);
    sizerR->Add(SPACE,SPACE, 0);
    sizerR->Add(sizerBR, 0, wxEXPAND);
      
    globalSizerV = new wxBoxSizer(wxVERTICAL);
    globalSizerV->Add(sizerL, 1, wxEXPAND);

    globalSizerH = new wxBoxSizer(wxHORIZONTAL);
    globalSizerH->Add(globalSizerV, 1);
    globalSizerH->Add(sizerR,1, wxEXPAND|wxLEFT, 5);

    
    _TH=sizerL->GetMinSize().y + sizerR->GetMinSize().y;
    
    SetSizer(globalSizerH);
    
    EnableCustom();

  }
  if (n==3) { // info tab (about, trackball instructions, and a button for advanced properties)

    wxSizer *sizerA = new wxBoxSizer(wxVERTICAL);
    sizerA->Add(new wxStaticText(this,
                                 wxID_ANY,
                                 _T("This is QuteMolX, the Nanorex branch of QuteMol")) 
       ,0, wxALIGN_CENTER );
    sizerA->Add(new wxStaticText(this, wxID_ANY,_T("which integrates with NanoEngineer-1.")) 
       ,0, wxALIGN_CENTER );
    //sizerA->Add(1,1,1);
    sizerA->Add(
       new wxButton(this, ID_WebButton2, nanorexQuteMolWebsite )
       ,0, wxALIGN_CENTER|wxTOP|wxBOTTOM, 10);
    //sizerA->Add(1,1,1);
    sizerA->Add(new wxStaticText(this, wxID_ANY,_T("QuteMol was originally created by")) 
       ,0, wxALIGN_CENTER|wxTOP, 10);
    sizerA->Add(new wxStaticText(this, wxID_ANY,_T("Marco Tarini and Paolo Cignoni.")) 
       ,0, wxALIGN_CENTER|wxBOTTOM, 10);
    sizerA->Add(
       new wxButton(this, ID_WebButton, qutemolwebsite )
       ,0, wxALIGN_CENTER|wxALL);


    wxSizer *sizerB = new wxStaticBoxSizer(new wxStaticBox(this, wxID_ANY, _T("Instructions") ), wxVERTICAL);
    sizerB->Add(new wxStaticText(this, wxID_ANY,_T("\
Left Mouse Button: rotate molecule\n\
Mouse wheel / Shift+Left: zoom molecule\n\
Middle Mouse / Ctrl+Left Mouse : pan molecule\n\
Right Mouse Button: move Light\n\
"), wxDefaultPosition, wxDefaultSize, wxALIGN_CENTER) 
      ,0, wxALIGN_CENTER );
    
   
    wxSizer *sizerC = new wxBoxSizer( wxHORIZONTAL);
    wxBitmap logoBitmap(logo_xpm, wxBITMAP_TYPE_XPM);
    wxStaticBitmap *bitmap = new wxStaticBitmap(this, wxID_ANY, logoBitmap, wxDefaultPosition );    
    sizerC->Add(bitmap, 0, wxALIGN_BOTTOM);
    sizerC->Add(1,1,1);
    sizerC->Add(new wxStaticText(this, wxID_ANY,
         _T("Version 0.5.0")
         /*_T("ver 0.4.1 ("__DATE__")")*/
       ),0, wxALIGN_BOTTOM|wxALL,10);
    
    wxSizer *sizer = new wxBoxSizer(wxVERTICAL);
     sizer->Add(1,1,1);
    sizer->Add(sizerA,0, wxEXPAND|wxLEFT|wxRIGHT,10);
       /*
    sizer->Add(1,1,1);
    sizer->Add(
       new wxButton(this, ID_WebButton, qutemolwebsite )
       ,0, wxALIGN_CENTER|wxALL);
    sizer->Add(
       new wxButton(this, ID_WebButton2, nanorexQuteMolWebsite )
       ,0, wxALIGN_CENTER|wxALL);
       */
    sizer->Add(1,1,1);

     sizer->Add(sizerB,0, wxEXPAND|wxLEFT|wxRIGHT,10);
    sizer->Add(1,1,1);
    sizer->Add(sizerC,0, wxEXPAND);
    
    SetSizer(sizer);
  }
}

bool MyTab::Redispose(int wy){
  bool res=false;
  if (globalSizerH) {
    if (_TH<wy) {
      if (globalSizerH->Detach(sizerR)) {
        globalSizerV->Detach(sizerL);
        globalSizerV->Add(sizerL,1, wxEXPAND|wxLEFT|wxRIGHT|wxTOP,10);
        globalSizerV->Add(sizerR,1, wxEXPAND|wxLEFT|wxRIGHT,10);
        res=true;
      }
    }
    else 
    {
      if (globalSizerV->Detach(sizerR)) {
        globalSizerV->Detach(sizerL);
        globalSizerV->Add(sizerL,1, wxEXPAND);
        globalSizerH->Add(sizerR,1, wxEXPAND|wxLEFT, 5);
        res=true;
      }
    }
    globalSizerV->Layout();
    globalSizerV->CalcMin();
    globalSizerV->RecalcSizes();
    globalSizerH->Layout();
    globalSizerH->CalcMin();
    globalSizerH->RecalcSizes();
  }
  return res;
}

void MyTab::UpdateAll(){
  setSceneBgcolor( col(cgSettings.P_bg_color_R,cgSettings.P_bg_color_G, cgSettings.P_bg_color_B) );
  int k=(int)(cgSettings.P_halo_col*255.0);
  buttonChooseHAcolor->SetBackgroundColour(wxColor(k,k,k));
  sliderTable.UpdateAll();
  buttonTable.UpdateAll(); 
  //EnableGeom();
  EnableCustom();
}

