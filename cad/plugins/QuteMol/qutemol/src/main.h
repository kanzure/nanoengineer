
#ifndef _WX_MAIN_H_
#define _WX_MAIN_H_


#include <wx/defs.h>
#include <wx/app.h>
#include <wx/menu.h>
#include <wx/dcclient.h>

#include <wx/glcanvas.h>

extern "C"
{
//#include "lw.h"
//#include "trackball.h"
}

/* information needed to display lightwave mesh */
//typedef struct
//{
//  gint do_init;         /* true if initgl not yet called */
//    bool do_init;
//    //lwObject *lwobject;   /* lightwave object mesh */
//    float beginx,beginy;  /* position of mouse */
//    float quat[4];        /* orientation of object */
//    float zoom;           /* field of view in degrees */
//} mesh_info;


/* Define a new application type */
class MyApp: public wxApp
{
public:
    bool OnInit();
};

class MyToolbar: public wxPanel
{
public:
  MyToolbar(wxTopLevelWindow *parent, wxWindowID id = wxID_ANY,
        const wxPoint& pos = wxDefaultPosition,
        const wxSize& size = wxDefaultSize, long style = 0,
        const wxString& name = wxT("ToolBar"));
  void OnDrag(wxMouseEvent &event);
  wxSizer *topsizer;
  
  void UpdateGearsIcon(bool b);

  void UpdateGearsIcon();

  void SetTitleText( wxString = wxEmptyString );
  
private:
  wxTopLevelWindow *parent;
  
  wxStaticText *titleText;
  wxSizer *titleTextSizer;
  
  bool gearPresent;
  wxStaticBitmap *gear;
  wxBoxSizer *gearS;  
  
  DECLARE_EVENT_TABLE()
};

/* Define a new frame type */
class TestGLCanvas;

class MyFrame: public wxFrame
{
public:
    MyFrame(wxFrame *frame, const wxString& title, const wxPoint& pos,
        const wxSize& size, long style = wxDEFAULT_FRAME_STYLE);

    void OnExit(wxCommandEvent& event);
    void OnOpenFile (wxCommandEvent & event); // open the open-file dialogs
    void OnReadFile (wxString filename); // reads the file
    void OnSaveSnap (wxCommandEvent & event);
    void OnAbout (wxCommandEvent & event);
    void OnSize(wxSizeEvent& event);
    void Maximize(bool max);
//#if defined(_WIN32)
    void OnEraseBackground(wxEraseEvent& event);
//#endif
    void SetToolbar( MyToolbar *tb ) { m_tb = tb; }
    MyToolbar *GetToolbar() { return m_tb; }

    void OnPaint( wxPaintEvent& WXUNUSED(event) );

#if wxUSE_GLCANVAS

    void SetCanvas( TestGLCanvas *canvas ) { m_canvas = canvas; }
       
    TestGLCanvas *GetCanvas() { return m_canvas; }
    
    void OnKeyUp( wxKeyEvent& event );
    void OnKeyDown( wxKeyEvent& event );

    void ResetAO();
    void OnIdle(wxIdleEvent& event);
    


private:
  
    enum {NATURAL, CUSTOM, FORCED} resize_mode;
    TestGLCanvas *m_canvas;
#endif

    MyToolbar *m_tb;

    DECLARE_EVENT_TABLE()
};

#if wxUSE_GLCANVAS

class TestGLCanvas: public wxGLCanvas
{
public:
    TestGLCanvas(wxWindow *parent, wxWindowID id = wxID_ANY,
        const wxPoint& pos = wxDefaultPosition,
        const wxSize& size = wxDefaultSize, long style = 0,
        const wxString& name = wxT("GLCanvas"));

    ~TestGLCanvas();

    void OnPaint(wxPaintEvent& event);
    void OnSize(wxSizeEvent& event);
    void OnEraseBackground(wxEraseEvent& event);
    void OnMouse( wxMouseEvent& event );
    void OnKeyUp( wxKeyEvent& event );
    void OnKeyDown( wxKeyEvent& event );
    
    void SceneChanged(); // redraw!
 
    bool initdone;

    bool shownHQ;
    
private:
    //wxWindow *parent;
    DECLARE_EVENT_TABLE()
};

#endif // #if wxUSE_GLCANVAS

#endif // #ifndef _WX_MAIN_H_

