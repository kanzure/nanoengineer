


class savesnapDialog:public wxDialog{
public: 
  savesnapDialog(
    wxWindow* parent, 
    int mode // 0 PNG    1 JPG   2 GIF, 
  );
  
  void OnTextCtrl(wxCommandEvent & event);  
  void OnRadioButton(wxCommandEvent & event);
  void OnButton(wxCommandEvent & event);
  void OnCheckBox(wxCommandEvent & event);
  void OnText(wxCommandEvent & event);

  bool TransferDataFromWindow();
  
  DECLARE_EVENT_TABLE()
};
