#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <vector>
#include "SaveSnapDialog.h"
#include "HardSettings.h"


enum{ ID_ResUp=500, ID_ResDown, ID_Res, ID_AntiAlias, ID_Alpha};

static wxString title[]={"PNG snapshot options","JPG snapshot options","GIF animation options"};
static wxTextCtrl * resText;
static wxCheckBox *wxCheckAntia, *wxTransp ;

class EventTableEntry{
public:
  int* data;
  int tmpdata;
  int idButMore,idButLess, idText, idCheck, idRadio;
  int max, min;
  int delta;
  bool pow2;
  int valueIfChecked;
  wxTextCtrl *text;
  wxCheckBox *chkbox;
  wxRadioButton *radio;
  wxSizer* sizer;
  wxStaticText* label;
  wxButton* bm;
  wxButton* bl;
  
  wxRadioButton *enableif;
  
  EventTableEntry(){
    text=NULL;
    chkbox=NULL;
    sizer=NULL;
    label=NULL;
    bm=bl=NULL;
    radio=NULL;
    idButMore=idButLess=idText=idCheck=idRadio=-1;
    delta=1;
    
    enableif=NULL;

  }
  
  void Enable(){
    if (enableif) {
      bool b=enableif->GetValue();
      if (chkbox) chkbox->Enable(b); 
      if (text) text->Enable(b);
      if (radio) radio->Enable(b);
      if (label) label->Enable(b);
      if (bm) bm->Enable(b);
      if (bl) bl->Enable(b);
    }
  }

  void CheckBounds(){
    if (tmpdata>max) tmpdata=max;
    if (tmpdata<min) tmpdata=min;
    wxString st;st.Printf(_T("%d"),tmpdata);
    if (text) text->SetValue(st);
  }
  void More(){
    if (pow2) tmpdata*=2; else tmpdata=((tmpdata)/delta)*delta+delta;
    CheckBounds();
  }
  void Less(){
    if (pow2) tmpdata/=2; else tmpdata=((tmpdata+delta-1)/delta)*delta-delta;
    CheckBounds();
  }
  void Transfer(){
    if (data) {
      if (radio) {
        if (radio->GetValue()) *data=valueIfChecked;
      }
      else *data=tmpdata;
    }
  }
  void SetRadioButton(){
    tmpdata=valueIfChecked;
  }  
  void SetCheck(){
    tmpdata=chkbox->GetValue();
  }
  void SetFromText(){
    wxString st=text->GetValue();
    long int tmp;
    if (st.ToLong(&tmp)) tmpdata=tmp;
  }
  void SetValue(){
    //tmpdata=text->GetValue().ScanF();
    CheckBounds();
  }
  void Init(){
    tmpdata=*data;
    if (chkbox) chkbox->SetValue(tmpdata);
    if (text){ 
      wxString st;st.Printf(_T("%d"),tmpdata);
      if (text) text->SetValue(st);
    };
    if (radio) radio->SetValue(tmpdata==valueIfChecked);
  }
};




int newID(int i=-1){
  static int k;
  if (i!=-1) k=i;
  return k++;
}

class EventTable {
  enum {MAX=100};
  wxWindowID id[MAX];
  wxRadioButton *enableif, *lastRadio;
public:
  std::vector<EventTableEntry> data;
  static wxSizer * sizer;
  static wxDialog* parent;
  
  EventTable(){}
  
  void Clear(){
    data.clear();
    newID(500);
    enableif=lastRadio=NULL;
  }

  bool EndEnableGroup(){
    enableif=NULL;
  }
  
  bool StartEnableGroup(){
    enableif=lastRadio;
  }
  
  bool pressButton(wxWindowID x){
    for (int i=0; i<data.size(); i++) {
      if (data[i].idButMore==x) { data[i].More(); return true;}
      if (data[i].idButLess==x) { data[i].Less();return true;}
    }
    return false;
  }
  
  bool pressRadioButton(wxWindowID x){
    for (int i=0; i<data.size(); i++) 
    if (data[i].idRadio==x) { data[i].SetRadioButton();return true;}
    return false;
  }
  
  bool pressCheck(wxWindowID x){
    for (int i=0; i<data.size(); i++) 
      if (data[i].idCheck==x) { data[i].SetCheck();return true;}
    return false;
  }
  
  void Enable(){
    for (int i=0; i<data.size(); i++) data[i].Enable();
  }
  
  void transfer(){
    for (int i=0; i<data.size(); i++) data[i].Transfer();
  }
  
  bool insertText(wxWindowID x){
    for (int i=0; i<data.size(); i++) 
      if (data[i].idText==x) { data[i].SetFromText();return true;}
    return false;
  }
  
  void  AddNewCheck(wxString label, int *dataz){
    EventTableEntry e;
    e.idCheck=newID();

    e.label=new wxStaticText(parent, -1, label );
    e.chkbox=new wxCheckBox(parent, e.idCheck, _T("") );
    e.data=dataz;
    e.enableif=enableif;
    e.Init();
    
    sizer->Add( e.label, 1, wxALIGN_RIGHT|wxALIGN_BOTTOM);
    sizer->Add( e.chkbox, 1, wxALIGN_LEFT|wxALIGN_BOTTOM);
    
    data.push_back(e);
  }
  
  void  AddNewRadio(wxString label, int *dataz, int value){
    EventTableEntry e;
    e.idRadio=newID();

    e.label=new wxStaticText(parent, -1, label );
    e.radio=new wxRadioButton(parent, e.idRadio, _T("") );
    e.data=dataz;
    e.valueIfChecked=value;
    e.enableif=enableif;
    e.Init();
    
    lastRadio=e.radio;
    
    sizer->Add( e.label, 1, wxALIGN_RIGHT|wxALIGN_BOTTOM);
    sizer->Add( e.radio, 1, wxALIGN_LEFT|wxALIGN_BOTTOM);

    data.push_back(e);
    //checkButton but=new 
  }
  
  void AddNewInt(wxString label, int *dataz, int min, int max, bool pow2=false, int delta){
    EventTableEntry e;
    
    e.idText=newID();
    e.idButLess=newID();
    e.idButMore=newID();

    e.label=new wxStaticText(parent, -1, label );
    e.bl=new wxButton(parent, e.idButLess, _T("-"),wxDefaultPosition, wxSize(32, 16) );
		e.bm=new wxButton(parent, e.idButMore, _T("+"),wxDefaultPosition, wxSize(32, 16) );
    e.text=new wxTextCtrl(parent, e.idText, _T(""), wxDefaultPosition, wxSize(50,wxDefaultSize.y), 
      (pow2)?wxTE_READONLY:0 );
    e.pow2=pow2;
    e.min=min;
    e.max=max;
    e.data=dataz;
    e.delta=delta;
    e.enableif=enableif;
    
    e.Init();
      
    e.sizer=new wxBoxSizer(wxHORIZONTAL);
    e.sizer->Add( e.bl,0,wxALIGN_BOTTOM);
    e.sizer->Add( e.text,0,wxALIGN_BOTTOM);
    e.sizer->Add( e.bm,0,wxALIGN_BOTTOM);
    
    
    sizer->Add( e.label, 1, wxALIGN_RIGHT|wxALIGN_BOTTOM);
    sizer->Add( e.sizer, 1, wxALIGN_LEFT|wxALIGN_BOTTOM);
       
    data.push_back(e);
 }

};

static EventTable eventt;

wxSizer * EventTable::sizer = NULL;
wxDialog* EventTable::parent =NULL;

void savesnapDialog::OnRadioButton(wxCommandEvent & event){
  eventt.pressRadioButton( event.GetId() );
  eventt.Enable();
}

void savesnapDialog::OnCheckBox(wxCommandEvent & event){
  eventt.pressCheck( event.GetId() );
  eventt.Enable();
}

void savesnapDialog::OnText(wxCommandEvent & event){
  eventt.insertText( event.GetId() );
}
 
void savesnapDialog::OnButton(wxCommandEvent & event){
  int jj=event.GetId();
  if (jj==wxID_CANCEL) {
    m_returnCode=jj;
    EndDialog(jj);
  }
  else if (jj==wxID_OK) {
    m_returnCode=jj;
    AcceptAndClose();
  } else  {
    if (!eventt.pressButton( jj )) eventt.Enable();
  }
    //EmulateButtonClickIfPresent(jj);
    // ARGH! savesnapDialog::OnButton(event) should be protected, NOT private!
    // redoing it
  
}


savesnapDialog::savesnapDialog(
    wxWindow* parent ,
    int style
):wxDialog(parent,-1,title[style],wxDefaultPosition,wxSize(100,100) )
{
  wxSizer *top=new wxBoxSizer(wxVERTICAL);
 
  wxSizer *upper=new wxGridSizer(0,2,6,6);
  

/*
  wxSizer *res=new wxBoxSizer(wxHORIZONTAL);
  res->Add( new wxButton(this, ID_ResDown, _T("-"), wxDefaultPosition, butSize ),0,wxALIGN_BOTTOM);
  resText=new wxTextCtrl(this, ID_Res, _T("1024"), wxDefaultPosition, textSize, wxTE_READONLY );
  res->Add( resText, 1, wxALIGN_BOTTOM );
  res->Add( new wxButton(this, ID_ResUp, _T("+"), wxDefaultPosition, butSize ),0,wxALIGN_BOTTOM);

  upper->Add( new wxStaticText(this, -1, _T("Resolution:") ), 1, wxALIGN_RIGHT|wxALIGN_BOTTOM);
  upper->Add(res,1,wxALIGN_LEFT|wxALIGN_BOTTOM);
*/
  eventt.Clear();
  EventTable::sizer=upper;
  EventTable::parent=this;
  eventt.AddNewInt( _T("Resolution:"), ((style!=2))? &hardSettings.SNAP_SIZE : &hardSettings.GIF_SNAP_SIZE, 32, 1<<13, true,1);

  eventt.AddNewCheck( _T("AntiAlias:"), &hardSettings.SNAP_ANTIALIAS );

  if (style==0) // png 
  {
    eventt.AddNewCheck( _T("Transparent PNG:"), &hardSettings.PNG_TRANSPARENT );
  }

  wxSizer *mid=NULL;

  if (style==2) // gif 
  {

    eventt.AddNewInt( _T("Initial Pause (ms):"), &hardSettings.GIF_INITIAL_PAUSE, 000, 10000, false, +1000 );  
    //upper->Add(0,0);upper->Add(0,0);

    wxSizer *mode1s=new wxFlexGridSizer(0,2,6,6); 
    EventTable::sizer=mode1s;       
    eventt.AddNewRadio( _T("Full rotation mode:"), &hardSettings.GIF_ANIMATION_MODE, 0);
    eventt.StartEnableGroup();
    eventt.AddNewInt( _T("Rotation Time (ms):"), &hardSettings.GIF_ROT_MSEC, 500, 10000, false, +500 );  
    eventt.AddNewInt( _T("Frames:"), &hardSettings.GIF_ROT_N_FRAMES, 10, 1000, false, +5 );
    eventt.AddNewInt( _T("View angle (deg):"), &hardSettings.GIF_ROT_SIDEVIEW_ANGLE, -45, +45, false, +5 );  
    eventt.EndEnableGroup();
    //upper->Add(0,0);upper->Add(0,0);

    wxSizer *mode2s=new wxFlexGridSizer(0,2,6,6);        
    EventTable::sizer=mode2s;
    eventt.AddNewRadio( _T("Inspection mode:"), &hardSettings.GIF_ANIMATION_MODE, 1);
    eventt.StartEnableGroup();
    eventt.AddNewInt( _T("Rotation Time (ms):"), &hardSettings.GIF_INSP_MSEC, 500, 10000, false, +500 );  
    eventt.AddNewInt( _T("Frames:"), &hardSettings.GIF_INSP_N_FRAMES, 10, 1000, false, +5 );
    eventt.AddNewInt( _T("Angle (deg):"), &hardSettings.GIF_INSP_ANGLE, 5, 35, false, +5 );  
    eventt.EndEnableGroup();
    //upper->Add(0,0);upper->Add(0,0);

    wxSizer *mode3s=new wxFlexGridSizer(0,2,6,6);
    EventTable::sizer=mode3s;    
    eventt.AddNewRadio( _T("Six-Sides mode:"), &hardSettings.GIF_ANIMATION_MODE, 2);
    eventt.StartEnableGroup();
    eventt.AddNewInt( _T("Time x Side (ms):"), &hardSettings.GIF_6SIDES_MSEC, 200, 2000, false, +100 );  
    eventt.AddNewInt( _T("Frames x Side:"), &hardSettings.GIF_6SIDES_N_FRAMES, 10, 200, false, +1 );
    eventt.AddNewInt( _T("Pause x Side (ms):"), &hardSettings.GIF_6SIDES_PAUSE, 500, 10000, false, +250 );
    eventt.EndEnableGroup();
    
    mid=new wxBoxSizer(wxHORIZONTAL);
    mid->Add(mode1s,1,wxLEFT,10);
    mid->Add(mode2s,1,wxLEFT,10);
    mid->Add(mode3s,1,wxLEFT|wxRIGHT,10);
  //int GIF_SIDEVIEW_ANGLE;
  //int GIF_INSPECTION_ANGLE;
  //int GIF_PAUSE;
  }
     
  top->Add( upper, 0,  wxALIGN_CENTER|wxALL, 20 );
  if (mid) top->Add( mid );
  top->Add( CreateSeparatedButtonSizer(wxOK|wxCANCEL), 0, wxALIGN_CENTER |wxALL, 20 );
  SetSizerAndFit(top);
  eventt.Enable();

}

bool savesnapDialog::TransferDataFromWindow(){
  eventt.transfer();
  return true;
}


BEGIN_EVENT_TABLE(savesnapDialog, wxDialog)
    EVT_RADIOBUTTON(-1, savesnapDialog::OnRadioButton)
    
    EVT_BUTTON(-1, savesnapDialog::OnButton)
    EVT_CHECKBOX(-1, savesnapDialog::OnCheckBox)
    EVT_TEXT(-1, savesnapDialog::OnText)
    //EVT_BUTTON(ID_ChooseBallnstickConstantcolor, MyTab::OnChooseBallnstickConstantcolor)
    //EVT_COMMAND_SCROLL(ID_SetLicoriceRadius, MyTab::OnSetLicoriceRadius)
    //EVT_COMMAND_SCROLL(ID_SetBallnstickRadius, MyTab::OnSetBallnstickRadius)
END_EVENT_TABLE()
