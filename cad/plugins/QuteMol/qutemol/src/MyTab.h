
#include <wx/panel.h>


/* Define a new application type */
class MyTab: public wxPanel{
  public: 
    
  MyTab(wxWindow *parent , int i);  // constructor for i-th tab
  
  static wxWindow *frame2redraw;
  static void SceneChanged();
  
  static bool Redispose(int wy);
  
  static int Count(); // number of tabs
   
  static wxString Title(int i); // title of i-th tab
  
  static void EnableGeom();
  static void EnableCustom();
  void emphCurrentPreset(int i);
  
  /* Geometry TAB */
  /*--------------*/
  /*
  void OnSetBallnstick (wxCommandEvent & event);
  void OnSetLicorice (wxCommandEvent & event);
  void OnSetSpacefill (wxCommandEvent & event);
  void OnSetLicoriceRadius(wxScrollEvent & event);
  void OnSetBallnstickRadius(wxScrollEvent & event);
  void OnSetBallnstickSmoothcolor(wxCommandEvent & event);
  void OnSetBallnstickBicolor(wxCommandEvent & event);
  void OnSetBallnstickConstantcolor(wxCommandEvent & event);*/
  
  void OnRadioButton(wxCommandEvent & event);  
  //void OnChooseBallnstickConstantcolor(wxCommandEvent & event);  
  static void setSceneBgcolor(wxColor c);
  void setSceneBgbrightness(float f);
 
  // ALL:
  void OnSlider(wxScrollEvent & event);  
  void OnButton(wxCommandEvent & event);
  void OnCheckBox(wxCommandEvent & event);
  
  static void UpdateAll();
  
  DECLARE_EVENT_TABLE()
};
