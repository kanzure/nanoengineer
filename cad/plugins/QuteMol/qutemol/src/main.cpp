//
// qutemol on wxWidgets MAIN 
//
// (on DevCpp, download and install "wxWidgets 2.6.1 unicode" DevPak)
//
////////////////////////////////////////////////////////////////////

#define SnapButton 1
#define OpenButton 2
#define QuitButton 3



#include <GL/glew.h>


#ifdef __GNUG__
#pragma implementation
#pragma interface
#endif

// For compilers that support precompilation, includes "wx.h".
#include "wx/wxprec.h"

#include "wx/image.h"
#include "wx/stdpaths.h"

//#include <iostream>
#include <wx/cmdline.h>
#include <wx/statline.h>

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WX_PRECOMP
#include "wx/wx.h"
#endif

#if !wxUSE_GLCANVAS
    #error "OpenGL required: set wxUSE_GLCANVAS to 1 and rebuild the library"
#endif

#include "main.h"
#ifdef __WXMAC__
#  ifdef __DARWIN__
#    include <OpenGL/glu.h>
#  else
#    include <glu.h>
#  endif
#else
#  include <GL/glu.h>
#endif

#include "image/gear2.xpm"
#include "image/qutemolsm.xpm"
#include "image/quiton.xpm"
#include "image/quitoff.xpm"
#include "image/snap_off2.xpm"
#include "image/snap_on.xpm"
#include "image/open_off2.xpm"
#include "image/open_on.xpm"
#include "image/snap_noborder.xpm"
#include "image/open_noborder.xpm"

typedef unsigned char Byte;
typedef unsigned int uint;

#include "CgUtil.h"

#include <math.h>

#include <vector>

#include <vcg/space/point3.h>
#include <vcg/space/color4.h>

#include "gen_normal.h"
#include <wrap/gui/trackball.h>

using namespace vcg;
using namespace std;


#include "CubeMapSamp.h"
#include "OctaMapSamp.h"
#include "Mol.h"
//#include "AOgpu.h"

#include "MyCanvas.h"

#include "ShadowMap.h"
#include "HardSettings.h"

#include "Common.h"

#include "MyTab.h"

#include "saveSnapDialog.h"

#include "progress.h"

#include "AtomColor.h"

extern vcg::Trackball track;
extern vcg::Trackball lightTrack;

extern Mol mol;

bool mustDoHQ=false;

#include <wx/dnd.h>
#include <wx/notebook.h>

wxStopWatch sw;


#include "gifSave.h"

// defined in pngSave
bool PNGSaveWithAlpha( const char * filename, const Byte * data, int sx, int sy, int reverse = 0);
void downsample2x2(Byte * data, int sx, int sy);
void downsample2x2NoAlpha(Byte * data, int sx, int sy);


void MyTab::SceneChanged(){
  ((TestGLCanvas*)frame2redraw)->SceneChanged();
}


void TestGLCanvas::SceneChanged(){
  mustDoHQ=false;
  Refresh(false);
}

void StartTime(){
  sw.Start();
}

long int TakeTime(FILE *f , char *st){
  long int delta=sw.Time();
  fprintf(f,"%5ldmsec: %s\n",delta,st);
  //globaltime=timen;
  return delta;
}
/*long int TakeTotalTime(){
  long int timen=getTicks(), delta=timen-startingtime;
  printf("------------------\nTotal time: %5dmsec\n",delta);
  globaltime=timen;
  return delta;
}*/


long int getTicks(){
  return 0;
}

void MyToolbar::SetTitleText(wxString s){
#ifndef __DARWIN__
  titleText->SetLabel(s);
  titleTextSizer->Layout();
#endif
}
  
class MyDropTarget : public wxFileDropTarget
{
public:
    MyDropTarget(MyFrame *_parent) { parent = _parent;  }

    virtual bool OnDropFiles(wxCoord x, wxCoord y,  const wxArrayString& filenames){
      parent->OnReadFile(filenames[0]);
    };

private:
    MyFrame *parent;
};

void MyToolbar::OnDrag(wxMouseEvent &event){
   
   if ( event.LeftDClick()) {
      parent->Maximize( !(parent->IsMaximized()) );
   }

   static int omx, omy;
   int mx, my;
   mx = event.GetX();
   my = event.GetY();
   
   if ( event.Dragging() ){
     if (!(parent->IsMaximized())) {
      CaptureMouse();
      wxPoint cur=parent->GetPosition();
      int dx=mx-omx;
      int dy=my-omy;
      cur.x+=dx;
      cur.y+=dy;
      omx=mx-dx;
      omy=my-dy;
      parent->SetPosition( cur ); 
     }
   } else {
     omx=mx; omy=my;
     ReleaseMouse();
  }
}

wxNotebook *notebook;

void MyToolbar::UpdateGearsIcon(){
  UpdateGearsIcon( mol.DoingAO() );
}

void MyToolbar::UpdateGearsIcon(bool b){
  if (gearPresent==b) return;
  if (!b) gearS->Detach(gear); else gearS->Add(gear);
  gear->Show(b);
  gearS->Layout();
  gearPresent=b;
/*
  if (b) 
  gear->Raise();
  else
  gear->Lower();*/
}

MyToolbar::MyToolbar(wxTopLevelWindow *_parent, wxWindowID id,
        const wxPoint& pos,
        const wxSize& size, 
        long style,
        const wxString& name): wxPanel(_parent, id, pos, size, style, name){
          
  parent=_parent;
  
  // let's build notebook
  /*wxNotebook **/notebook = new wxNotebook(
    this, id, pos, size, 
    0,/*style/*|wxNO_FULL_REPAINT_ON_RESIZE|wxNB_TOP,*/
    name);
    
  for (int i=0; i<MyTab::Count(); i++) {
    //if (i==2)
    notebook->AddPage(new MyTab(notebook,i), MyTab::Title(i), i==0 );
      parent->SetBackgroundColour(notebook->GetBackgroundColour());
  }
  
#ifndef __DARWIN__
  wxBitmap snap_off2Bitmap(snap_off2_xpm, wxBITMAP_TYPE_XPM);
  wxBitmapButton *snapButton = new wxBitmapButton(this, SnapButton, 
                                snap_off2Bitmap, wxDefaultPosition, wxSize(48,48),0);
  wxBitmap snap_onBitmap(snap_on_xpm, wxBITMAP_TYPE_XPM);
  snapButton->SetBitmapSelected(snap_onBitmap);  
    
  wxBitmap open_off2Bitmap(open_off2_xpm, wxBITMAP_TYPE_XPM);
  wxBitmapButton *openButton = new wxBitmapButton(this, OpenButton, 
                                open_off2Bitmap,wxDefaultPosition, wxSize(48,48),0);
  wxBitmap open_onBitmap(open_on_xpm, wxBITMAP_TYPE_XPM);
  openButton->SetBitmapSelected(open_onBitmap);  
#else
  wxBitmap snap_noborderBitmap(snap_noborder_xpm, wxBITMAP_TYPE_XPM);
  wxBitmapButton *snapButton = new wxBitmapButton(this, SnapButton, 
                                snap_noborderBitmap, wxDefaultPosition, wxSize(48,48),0);
  wxBitmap open_noborderBitmap(open_noborder_xpm, wxBITMAP_TYPE_XPM);
  wxBitmapButton *openButton = new wxBitmapButton(this, OpenButton, 
                                open_noborderBitmap,wxDefaultPosition, wxSize(48,48),0);

#endif
  wxBitmap quitoffBitmap(quitoff_xpm, wxBITMAP_TYPE_XPM);
  wxBitmapButton *quitButton = new wxBitmapButton(this, QuitButton, 
                           quitoffBitmap,
                           wxDefaultPosition, wxSize(15,16) , 0);
  wxBitmap quitonBitmap(quiton_xpm, wxBITMAP_TYPE_XPM);
  quitButton->SetBitmapSelected(quitonBitmap);  

  wxBitmap qutemolsmBitmap(qutemolsm_xpm, wxBITMAP_TYPE_XPM);
  wxStaticBitmap *logo = new wxStaticBitmap(this, wxID_ANY, qutemolsmBitmap, wxDefaultPosition );

  wxBitmap gear2Bitmap(gear2_xpm, wxBITMAP_TYPE_XPM);
  gear = new wxStaticBitmap(this, wxID_ANY, gear2Bitmap, wxDefaultPosition );
  
  wxSizer *sizerButtons = new wxBoxSizer( wxVERTICAL );
  sizerButtons->Add(openButton, 0,  wxALL, 1);
  sizerButtons->Add(snapButton, 0,  wxALL, 1);

  titleText = new wxStaticText(this, wxID_ANY, wxT(""));
  titleText->Disable();
  
#ifndef __DARWIN__
  wxSizer *linesizer1 = new wxBoxSizer(wxVERTICAL);

  linesizer1->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);
  linesizer1->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);
  linesizer1->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);

  wxSizer *linesizer2 = new wxBoxSizer(wxVERTICAL);
  linesizer2->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);
  linesizer2->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);
  linesizer2->Add(new wxStaticLine(this),0,wxALL| wxEXPAND, 1);
 
  titleTextSizer = new wxBoxSizer(wxHORIZONTAL);
  titleTextSizer->Add(3,3,        0,  wxALL, 3); 
  titleTextSizer->Add(linesizer1, 1,  wxALL|wxALIGN_CENTER_VERTICAL, 0); 
  titleTextSizer->Add(titleText,  0,  wxALL|wxALIGN_CENTER_VERTICAL, 0); 
  titleTextSizer->Add(linesizer2, 20,  wxALL|wxALIGN_CENTER_VERTICAL, 0); 
  titleTextSizer->Add(3,3,        0,  wxALL, 3); // spacer
  titleTextSizer->Add(quitButton, 0,  wxALL|wxALIGN_CENTER_VERTICAL, 2); 

#else
  quitButton->Hide();
  titleText->Hide();
#endif



  wxSizer *imgsizer = new wxBoxSizer(wxHORIZONTAL);
  imgsizer->Add(22,22, 0); 
  //imgsizer->Add(1,1, 10); 
  imgsizer->Add(logo, 1,  wxALL|wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER_HORIZONTAL, 0); // LOGO
  //imgsizer->Add(1,1, 9); 
  
  gearS = new wxBoxSizer(wxVERTICAL);
  gearS->Add(22,22,1);
  gearS->Add(gear);
  gearPresent=true;
  
  imgsizer->Add(gearS, 0,  wxALL|wxALIGN_BOTTOM|wxALIGN_CENTER_HORIZONTAL, 2); // LOGO
  
  wxSizer *topRsizer = new wxBoxSizer(wxVERTICAL);
#ifndef __DARWIN__
	  topRsizer->Add(titleTextSizer,0, wxALL| wxEXPAND, 0);
#endif 
	topRsizer->Add(imgsizer,1, wxALL| wxEXPAND, 0);
  
  topsizer = new wxBoxSizer(wxHORIZONTAL);
  topsizer->Add(sizerButtons,  0, wxALL, 5);
  topsizer->Add(topRsizer,     1, wxALIGN_TOP| wxALL| wxEXPAND, 0);

  
  wxSizer *globalsizer = new wxBoxSizer(wxVERTICAL);
  globalsizer->Add(topsizer, 0,  wxALL| wxEXPAND, 0);
  //globalsizer->Add(5, 5,       0,  wxALL, 0); // spacer
  globalsizer->Add(notebook, 1,  wxALL|wxEXPAND, 0);
  
  SetSizer(globalsizer);
  
  UpdateGearsIcon(false);
  
}


// `Main program' equivalent, creating windows and returning main app frame
bool MyApp::OnInit()
{
    
    hardSettings.OnStart();
    
    cgSettings.SetDefaults(); // <-- quick hack (solves wrong constructor order): 
      
    //if (!wxApp::OnInit()) return false;

    // questo per caricare salvare PNG...
    wxImage::AddHandler(new wxPNGHandler);
    wxImage::AddHandler(new wxJPEGHandler);
    
    // Create the main frame window
    MyFrame *frame = new MyFrame(NULL, wxT("QuteMolX"),
//        wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE //wxRESIZE_BORDER
#ifdef __DARWIN__
        wxDefaultPosition, wxDefaultSize,wxDEFAULT_FRAME_STYLE| wxRESIZE_BORDER
#else
        wxDefaultPosition, wxDefaultSize,wxRESIZE_BORDER
#endif
        );
        
    /* Make a menubar */
    
    /*
    // ...or, maybe NOT
    wxMenu *fileMenu = new wxMenu;

    fileMenu->Append(wxID_EXIT, wxT("E&xit"));
    fileMenu->Append(wxID_ABOUT, wxT("A&bout"));
    fileMenu->Append(wxID_OPEN, wxT("O&pen"));
    
    wxMenuBar *menuBar = new wxMenuBar;
    menuBar->Append(fileMenu, wxT("&File"));
    
    frame->SetMenuBar(menuBar);
    */

    frame->SetCanvas( 
      new TestGLCanvas(
        frame, wxID_ANY, wxPoint(0,0), wxSize( winx, winy ),   wxNO_BORDER //wxSUNKEN_BORDER
      )
    );

    // onle TestGLCanvas to process idles...
    wxIdleEvent::SetMode(wxIDLE_PROCESS_SPECIFIED);
    frame->SetExtraStyle(wxWS_EX_PROCESS_IDLE );
    
    MyTab::frame2redraw=frame->GetCanvas();
    
    frame->SetToolbar(  
      new MyToolbar(
        frame, wxID_ANY, wxPoint(winx,0), wxDefaultSize,   
       // wxNO_BORDER //wxSUNKEN_BORDER
        wxDEFAULT_FRAME_STYLE 
       |
//                      wxNO_FULL_REPAINT_ON_RESIZE |
                      wxCLIP_CHILDREN |
                      wxTAB_TRAVERSAL
      )
    );
    
    wxSizer *sizer = new wxBoxSizer(wxHORIZONTAL);
    sizer->Add(frame->GetCanvas(),      1, wxGROW|wxSHAPED); 
    sizer->Add(frame->GetToolbar(),      0, wxGROW);
    frame->SetSizer(sizer);

    int tbsize=frame->GetToolbar()->GetBestFittingSize().x;
    frame->GetToolbar()->SetSize(tbsize,winy);
    frame->GetToolbar()->Layout();
   
    //frame->SetMinSize(wxSize(tbsize+200,200));
    frame->SetClientSize(wxSize(winx+tbsize,winy));

    static const wxCmdLineEntryDesc cmdLineDesc[] =
    {
      { 
        wxCMD_LINE_PARAM,_T(""),_T(""),_T("filename.pdb:(molecule to be drawn)"), 
        wxCMD_LINE_VAL_STRING, wxCMD_LINE_PARAM_OPTIONAL 
      },
      { 
        wxCMD_LINE_OPTION,_T("a"),_T(""),_T("filename.art: optional Atom Render Table"), 
        wxCMD_LINE_VAL_STRING, wxCMD_LINE_PARAM_OPTIONAL 
      },
      { 
        wxCMD_LINE_SWITCH,_T("v"),_T(""),_T("don't start, show version name"), 
        wxCMD_LINE_VAL_STRING, wxCMD_LINE_PARAM_OPTIONAL 
      },
      { wxCMD_LINE_NONE }
    };
    
    wxCmdLineParser parser(cmdLineDesc, argc, argv);
    
    parser.Parse();

    InitQuteMol( NULL );

    wxString artFilename;
    if (parser.Found(_T("v"))>0) {
      FILE *f=fopen("output.txt", "wt");
      if (f) { 
        fprintf(f,"ver 0.4.1");
        fclose(f);
      }
      exit(0);
    }
    
    if (parser.Found(_T("a"),&artFilename)>0) {
      if (!readArtFile(artFilename.ToAscii())) {
        wxMessageBox(
          wxString(_T("Error reading art file \"") + artFilename +"\""), 
          _T("Error reading art file"), 
          wxOK | wxICON_EXCLAMATION, frame);
        exit(0);
        return false;
      }
    }
       
    if (parser.GetParamCount()>0)  frame->OnReadFile(parser.GetParam(0));
/*      InitQuteMol( parser.GetParam(0).mb_str(wxConvUTF8) );
    } else {
      InitQuteMol( NULL );
    }*/
  
    /* Show the frame */

    frame->Center();    
    frame->SetDropTarget( new MyDropTarget(frame) );
    frame->Show(true);
    
    return true;
}
void MyFrame::ResetAO(){
  mol.ResetAO();
}

  
IMPLEMENT_APP(MyApp)

BEGIN_EVENT_TABLE(MyFrame, wxFrame)
    //EVT_PAINT(MyFrame::OnPaint)
#if defined(_WIN32)
   EVT_ERASE_BACKGROUND(MyFrame::OnEraseBackground)
#endif
    EVT_SIZE(MyFrame::OnSize)
    EVT_BUTTON(OpenButton, MyFrame::OnOpenFile)
    EVT_BUTTON(SnapButton, MyFrame::OnSaveSnap)
    EVT_BUTTON(QuitButton, MyFrame::OnExit)
    EVT_KEY_DOWN(MyFrame::OnKeyDown)
    EVT_KEY_UP(MyFrame::OnKeyUp)
    EVT_IDLE(MyFrame::OnIdle)
END_EVENT_TABLE()


BEGIN_EVENT_TABLE(MyToolbar, wxPanel)
   EVT_MOUSE_EVENTS(MyToolbar::OnDrag)
END_EVENT_TABLE()


void MyFrame::OnKeyUp( wxKeyEvent& event ){
  m_canvas->OnKeyUp(event);
}

void MyFrame::OnKeyDown( wxKeyEvent& event ){
  m_canvas->OnKeyDown(event);
}


/* My frame constructor */
MyFrame::MyFrame(wxFrame *frame, const wxString& title, const wxPoint& pos,
    const wxSize& size, long style)
    : wxFrame(frame, wxID_ANY, title, pos, size, style)
{
    // For win32 debugging
#if 0
    wxLogWindow* logger = new wxLogWindow(this, "log");
    wxLog::SetActiveTarget(logger);
    wxLogMessage("logging on");
#endif
   
    m_canvas = NULL;
    m_tb= NULL;
#ifndef __DARWIN__
		SetIcon(wxIcon(_T("sample"),wxBITMAP_TYPE_ICO_RESOURCE,32,32));
#endif
    resize_mode=NATURAL;
}

//void MyFrame::OnPaint( wxPaintEvent& event )
//{
//  wxFrame::OnPaint(event);
//}


void MyFrame::OnSize(wxSizeEvent& event){

  int w,h;
  GetClientSize(&w,&h);
  int hlogo = m_tb->topsizer->GetMinSize().y + 40;
  if (MyTab::Redispose(h - hlogo )) {
    GetToolbar()->SetSize(200,winy);
  }
  
  if (resize_mode==FORCED ) {
    // TODO: fullscreen resize
    //m_canvas->;
    //m_tb->;
    resize_mode=NATURAL;
    wxFrame::OnSize(event);
    //m_tb->Fit();
    //m_tb->GetSizer()->RecalcSizes();
    //GetSizer()->RecalcSizes();
    //notebook->Layout();
    //notebook->SetSize(100,100);
    //m_tb->SetSize(100,100);
    //notebook->GetSizer()->RecalcSizes();;
    //m_tb->Layout();
    //Layout();
//    Fit();
  } else
  if (resize_mode==NATURAL ) {
    wxFrame::OnSize(event);
    /*
    GetClientSize(&w,&h);    
    int tbsize=GetToolbar()->GetBestFittingSize().x;
    winx=w-tbsize;
    winy=h;
    
    GetToolbar()->SetPosition( wxPoint(winx,0) );
    GetToolbar()->SetSize(tbsize,winy);
    GetCanvas()->SetSize(winx,winy);
   */
    resize_mode=CUSTOM;
  }
  else {
  
  static int oldw=0,oldh=0;

  
  int w1=m_tb->GetBestFittingSize().x;
  //

  int sx=w-w1, sy=h , s;
  
  if ((oldw==w) && (oldh!=h)) s=sy; else
  if ((oldh==h) && (oldw!=w)) s=sx; else
    s=(sx+sy)/2;
  
  wxSize size=wxSize(s+w1, s);
  resize_mode=NATURAL;
  SetClientSize(size);
  
  //wxFrame::OnSize( event );
  //wxSizeEvent event2=wxSizeEvent(size);
  //wxFrame::OnSize(event2);
  
  //oldw=w;oldh=h;
  }
}

void MyFrame::Maximize(bool max){
  
  //if (custom_resizing) {
    resize_mode=FORCED;
    wxFrame::Maximize(max);
  //}
}

/* Intercept menu commands */
void MyFrame::OnExit( wxCommandEvent& WXUNUSED(event) )
{
    Close();
}

BEGIN_EVENT_TABLE(TestGLCanvas, wxGLCanvas)
    EVT_SIZE(TestGLCanvas::OnSize)
    EVT_PAINT(TestGLCanvas::OnPaint)
    EVT_ERASE_BACKGROUND(TestGLCanvas::OnEraseBackground)
    EVT_MOUSE_EVENTS(TestGLCanvas::OnMouse)
    EVT_KEY_DOWN(TestGLCanvas::OnKeyDown)
    EVT_KEY_UP(TestGLCanvas::OnKeyUp)
END_EVENT_TABLE()

TestGLCanvas::TestGLCanvas(wxWindow *_parent, wxWindowID id,
    const wxPoint& pos, const wxSize& size, long style, const wxString& name)
    : wxGLCanvas(_parent, id, pos, size, style|wxFULL_REPAINT_ON_RESIZE, name)
{
  initdone=false;
  shownHQ=false;
}

TestGLCanvas::~TestGLCanvas()
{
}


wxString errorMSG(int errcode){
  wxString res;
  res=_T("OpenGL problems:\n\n");
  if (errcode&ERRGL_NO_GLEW) { 
    res+=_T(" - cannot initialize GLEW:\n   ");
    res+= wxString::FromAscii(CgUtil::lasterr);
    res+=_T("\n");
  }
  if (errcode&ERRGL_NO_FS) res+=_T(" - no Programmable Fragment Shader found\n");
  if (errcode&ERRGL_NO_VS) res+=_T(" - no Programmable Vertex Shader found\n");
  if (errcode&ERRGL_NO_FBO_SHADOWMAP) res+=_T(" - cannot initialize FrameBufferObject for shadowmaps\n");
  if (errcode&ERRGL_NO_FBO_HALO) res+=_T(" - cannot initialize FrameBufferObject for halos\n");
  if (errcode&ERRGL_NO_FBO_HALO) res+=_T(" - cannot initialize FrameBufferObject for A.O. computation\n");
  res+=_T("\n(Hint: update graphic card drivers)");
  return res;
}

void TestGLCanvas::OnPaint( wxPaintEvent& event )
{


    /* must always be here */
    wxPaintDC dc(this);

#ifndef __WXMOTIF__
    if (!GetContext()) return;
#endif

    // Testing for supported extensions isn't enough since video adpater drivers
    // can be buggy themselves, even the latest versions. So we build a list of
    // problematic renderers to warn users. The first one in this list is the
    // renderer for the Macbook.
    //
    static wxString ProblematicRenderers =
        "Intel GMA 950 OpenGL Engine Quadro FX Go1400/PCI/SSE2";
        
    SetCurrent();

    if (!initdone) {
      static bool once=false;
      if (!once) {
        once=true; 
        int errcode=initGl();
        if (errcode != ERRGL_OK) {
            wxMessageBox(errorMSG(errcode),
                         _T("Unrecoverable error: Problems initializing graphics"),
                         wxOK | wxICON_EXCLAMATION, this);
            exit(0);
            
        } else {
            wxString extensions = glGetString(GL_EXTENSIONS);
            wxString renderer = glGetString(GL_RENDERER);
            if (!extensions.Contains("GL_EXT_framebuffer_object") ||
                ProblematicRenderers.Contains(renderer))
                wxMessageBox(_T("QuteMolX makes use of OpenGL extensions that are not implemented, or not stable for your video adapter. If you choose to continue, your computer may crash or freeze. Save your work."),
                         _T("Warning: Potential video adapter problems"),
                         wxOK | wxICON_EXCLAMATION, this);
                         
            initdone=true;
        }
      }
    }
    
    if (!initdone) wxGLCanvas::OnPaint(event); else
    if (mol.IsReady()) { 
      if (mustDoHQ) {
        drawFrame( hardSettings.STILL_QUALITY );  
        shownHQ=true;
        mustDoHQ=false;
      } else {
        drawFrame( hardSettings.MOVING_QUALITY );  
        shownHQ=false;
      }
      SwapBuffers();  
    }  
    else {
      clearFrame();
      SwapBuffers();  
    }   
}

void TestGLCanvas::OnSize(wxSizeEvent& event)
{

    // this is also necessary to update the context on some platforms
    wxGLCanvas::OnSize(event);

    // set GL viewport (not called by wxGLCanvas::OnSize on all platforms...)
    
    GetClientSize(&winx, &winy);
    mainCanvas.SetVideoSize(winx);
#ifndef __WXMOTIF__
    if ( GetContext() )
#endif
    {
        SetCurrent();
        glViewport(0, 0, (GLint) winx, (GLint) winy);
    }
}


void MyFrame::OnEraseBackground(wxEraseEvent& event)
{
  wxFrame::OnEraseBackground(event);
    /* Do nothing, to avoid flashing on MSW */
}

void TestGLCanvas::OnEraseBackground(wxEraseEvent& event)
{
  if (!initdone) wxGLCanvas::OnEraseBackground(event);
    /* Do else do nothing, to avoid flashing on MSW */
}

bool wxConsumeTrackBallEvent(wxMouseEvent& event, Trackball &track);
bool wxConsumeTrackBallEvent(wxKeyEvent& event, bool down, Trackball &track);

void TestGLCanvas::OnKeyUp( wxKeyEvent& event ){
  wxConsumeTrackBallEvent(event,false,track);
}

extern int CSIZE; // number of texels for a patch of an aotm

void TestGLCanvas::OnKeyDown( wxKeyEvent& event ){
  wxConsumeTrackBallEvent(event,true,track);
#ifdef __DARWIN__
	wxString path = wxStandardPaths::Get().GetResourcesDir() + "/presets/new.preset";
#else
	wxString path =  "presets\\new.preset";
#endif
  if (event.GetKeyCode() == WXK_F7 ) {
    cgSettings.Save(path.c_str());
  }

  if (event.GetKeyCode() == WXK_F6 ) {
    if (cgSettings.Load(path.c_str())) {
      MyTab::UpdateAll();
      
      cgSettings.ResetHalo();
      cgSettings.UpdateShaders();
      SceneChanged();
    }

  }

  if (event.GetKeyCode() == WXK_F5 ) {
    mol.PrepareAOSingleView();
    SceneChanged();
  }

  if (event.GetKeyCode() == WXK_F2 ) {
    static int status=0;
    status=(status+1) % 5;
    draw_balls = (status==0) || (status==1)  || (status==2) ; 
    draw_sticks = (status==0) || (status==1) || (status==3) || (status==4) ; 
    draw_wireframe_balls= (status==1)  ;
    draw_wireframe_sticks= (status==1)  || (status==3) ;
    
    SceneChanged();
  }
  
  if (event.GetKeyCode() == WXK_F1 ) {
    wxString text; 
    if (!mol.IsReady() ) text=wxT("(no molecule)");
    else {

      text=wxString( mol.GetMolName(), wxConvUTF8 ).BeforeLast('.') + 
           wxT("\n (file: \"")+wxString( mol.filename, wxConvUTF8 ) +wxT("\")\n\n");
      
      text=text+wxString::Format(wxT("%d atoms\n"),mol.atom.size());
      
      if (mol.sticks) {
        text=text+wxString::Format(wxT("%d bonds\n"),mol.bond.size());
      }
      
           
      text=text+wxString::Format(
        _T("\nUsing:\n Texture size = %dx%d\n Patch size=%dx%d"), 
        moltextureCanvas.GetHardRes(),
        moltextureCanvas.GetHardRes(),
        CSIZE,CSIZE
      );

      
    }       
    wxMessageBox(text, _T("QuteMolX - file info"), wxOK | wxICON_INFORMATION, this);
  }

  if (event.GetKeyCode() == WXK_F6 ) {
    use_accurate_halo=!use_accurate_halo;
    SceneChanged();
  }
  
  // temp, should e set auto depending on dist
  if (event.GetKeyCode() == WXK_F2 ) {

    cgSettings.P_capping=!cgSettings.P_capping;
    cgSettings.UpdateShaders();
    SceneChanged();
  }
}


void MyFrame::OnAbout(wxCommandEvent& WXUNUSED(event))
{
}



void MyFrame::OnSaveSnap (wxCommandEvent & event)
{
      
  int sx,sy;
  static const wxString FILETYPES = _T( 
     "PNG (lossless)|*.png|"
     "JPEG (lossy)|*.jpg|"
     "GIF animation|*.gif"
                  );
   wxFileDialog * saveSnapDialog =
       new wxFileDialog ( this,
                          wxString  (_T("Save a snapshot")),
                          wxString(), // def path
                          wxString(), 
                          FILETYPES,
                          wxSAVE | /*wxCHANGE_DIR |*/ wxOVERWRITE_PROMPT
                          );
                          
   static int lastFilterIndex=-1;
   
   if (lastFilterIndex==-1) lastFilterIndex=saveSnapDialog->GetFilterIndex();
   saveSnapDialog->SetFilterIndex( lastFilterIndex );
  
   wxString ext;   
   if (lastFilterIndex==1) ext=_T(".jpg"); 
   else if (lastFilterIndex==2) ext=_T(".gif"); 
   else ext=_T(".png");
   saveSnapDialog->SetFilename( wxString( mol.GetFilenameSnap(), wxConvUTF8 )+ ext );
   static wxString CANNOT_SAVE = _T("Could not save snap!\n\nYou might try setting\na lower resolution\nor removing AntiAliasing...");
   if (saveSnapDialog->ShowModal() == wxID_OK) 
   if ((new savesnapDialog(this,saveSnapDialog->GetFilterIndex()))->ShowModal() == wxID_OK )
   { 
      
      
      int jj=saveSnapDialog->GetFilterIndex();
      lastFilterIndex=jj;

      Byte* snap;
      int AAMult=(hardSettings.SNAP_ANTIALIAS)?2:1;
      bool useTransp=(hardSettings.PNG_TRANSPARENT==1) && (jj==0);
      if (jj!=2) {
        
        sx=sy=hardSettings.SNAP_SIZE*AAMult;
      
        if ((useTransp) && (cgSettings.UseHalo()>0)) {
          cgSettings.doingAlphaSnapshot=true;
          cgSettings.ResetHalo();
          cgSettings.UpdateShaders();
        }
      
        snap= GetSnapshot(sx,sy, useTransp );
      
        if (cgSettings.doingAlphaSnapshot) {
          cgSettings.doingAlphaSnapshot=false;
          cgSettings.ResetHalo();
          cgSettings.UpdateShaders();
        }      
        if (!snap) {
         wxMessageBox(CANNOT_SAVE, _T("OpenGL problems?"), wxOK | wxICON_EXCLAMATION, this);
         return;
        }
     } else sx=sy=hardSettings.GIF_SNAP_SIZE*AAMult;
     {
        
       wxString fn=saveSnapDialog->GetPath();
        
        // fix filename Extension
        //////////////////////////
        //wxString ext[3]={   _T("png"),   _T("jpg") ,  _T("png") };
        //wxString cext=fn.AfterLast('.');
        //if (cext.CmpNoCase(ext[0])||cext.CmpNoCase(ext[1])) fn=fn.BeforeLast('.');
        //fn=fn+_T('.')+ext[ jj ];
        
        switch (jj) {
          case 0:
          case 1: 
            if (!useTransp) {
              StartProgress("Saving snap!", 2);
              wxImage snapi(sx,sy,snap);
              if (AAMult!=1) snapi=snapi.Scale(sx/AAMult,sy/AAMult);
              UpdateProgress(1);
              wxBitmap(snapi.Mirror(false)).SaveFile(
                fn,
                (jj==0)?wxBITMAP_TYPE_PNG:wxBITMAP_TYPE_JPEG
              );
              UpdateProgress(2);
              EndProgress();
            }
            else {
              if (AAMult!=1) downsample2x2(snap, sx, sy);
              PNGSaveWithAlpha((const char*)fn.mb_str(wxConvUTF8),snap,sx/AAMult,sy/AAMult,1);
            };
           break;
          case 2: {
            GifWrapper gifw;
            int N;
            double totalTime;
            double subStepTime=0;
            double startTime;startTime=hardSettings.GIF_INITIAL_PAUSE/1000.0;
            if (hardSettings.GIF_ANIMATION_MODE==0) {
              N=hardSettings.GIF_ROT_N_FRAMES;
              totalTime=hardSettings.GIF_ROT_MSEC/1000.0;
            } 
            if (hardSettings.GIF_ANIMATION_MODE==1) {
              N=hardSettings.GIF_INSP_N_FRAMES;
              totalTime=hardSettings.GIF_INSP_MSEC/1000.0;
            } 
            if (hardSettings.GIF_ANIMATION_MODE==2) {
              N=hardSettings.GIF_6SIDES_N_FRAMES*6;
              totalTime=hardSettings.GIF_6SIDES_MSEC*6.0/1000.0;
              subStepTime=hardSettings.GIF_6SIDES_PAUSE/1000.0;
            } 
            
            StartProgress("Saving GIF", N);         
            for (int i=0; i<N; i++) {
              if (!UpdateProgress(i)) break;
              setAniStep(double(i)/N);
              snap = GetSnapshot(sx,sy, false);
              
              if (!snap) {
                 wxMessageBox(CANNOT_SAVE, _T("OpenGL problems?"), wxOK | wxICON_EXCLAMATION, this);
                 EndProgress();
                 return;
              }
              
              if (AAMult!=1) downsample2x2NoAlpha(snap, sx, sy);
              gifw.AddFrame(snap, sx/AAMult, sy/AAMult, 
                totalTime/N 
                + ( (i==0)?startTime:0) 
                + ( (i%(N/6)==0)?subStepTime:0) 
              ); 
            } 
            stopAni();
            gifw.Save( (const char*)fn.mb_str(wxConvUTF8) );
            EndProgress();
            } break;
        }
        
      }
   }
                  
}


void MyFrame::OnReadFile (wxString filename)
{
   if (mol.ReadPdb((const char*)filename.mb_str(wxConvUTF8) )) {
       if ((mol.natm==0) && (mol.nhetatm!=0)) geoSettings.showHetatm=true;
       MyTab::EnableGeom();
       UpdateShadowmap();
       wxString name( mol.GetMolName(), wxConvUTF8 ); 
       SetTitle(  name.BeforeLast('.')+ _T(" - QuteMolX") );
       m_tb->SetTitleText(name);
       geoSettings.Apply();

       // redo shaders, as texture size could have changed 
       cgSettings.UpdateShaders();

   } else {
      wxMessageBox(wxString::FromAscii(QAtom::lastReadError), _T(":-("), wxOK | wxICON_EXCLAMATION, this);
      m_tb->SetTitleText();
   }
   
  // remake shaders cos texture size could have changed...

   
   //theText->LoadFile(openFileDialog->GetFilename());
   //SetStatusText(GetCurrentFilename(), 0);      
}


void MyFrame::OnOpenFile (wxCommandEvent & event)
{ 
  static const wxString FILETYPES = _T( 
                   "Protein Data Bank molecule (pdb, vdb, qdb)|*.pdb;*.vdb;*.qdb|"
                   "All files|*.*"
                  );
  wxFileDialog * openFileDialog =
       new wxFileDialog ( this,
                          wxString(_T("Open file")),
                          wxString(), // def path
                          wxString(), 
                          FILETYPES,
                          wxOPEN | wxFILE_MUST_EXIST/*| wxCHANGE_DIR*/,
                          wxDefaultPosition);

   if (openFileDialog->ShowModal() == wxID_OK) {
     OnReadFile( openFileDialog->GetPath() );
   }
/* wxString filename=openFileDialog->GetFilename();
   wxString dir=openFileDialog->GetDirectory();*/
}

void MyFrame::OnIdle(wxIdleEvent& event){
  if (mol.DoingAO()) {
    m_tb->UpdateGearsIcon(true);
    if (mol.PrepareAOstep()) {
      m_canvas->SceneChanged();
      event.RequestMore(false); 
      m_tb->UpdateGearsIcon(false);
      return;
    }
    else event.RequestMore(true);      
  } else {
    event.RequestMore(false); 
    if (hardSettings.STILL_QUALITY!=hardSettings.MOVING_QUALITY)
    if (!m_canvas->shownHQ) {
      m_canvas->shownHQ=true;
      mustDoHQ=true;
      m_canvas->Refresh(false);
    }
    m_tb->UpdateGearsIcon(false);
  }
}

void TestGLCanvas::OnMouse( wxMouseEvent& event )
{
    
    static bool useLightTrack=false;

    if ( event.m_rightDown || event.m_leftDown || event.m_middleDown ) {
      if (!HasCapture()) CaptureMouse();
    }
    else if (HasCapture()) ReleaseMouse();
    
    useLightTrack=event.m_rightDown;

    bool consumed=false;
    if (useLightTrack) {
      MovingLightMode=true;
      if (wxConsumeTrackBallEvent( event, lightTrack)) {
        SetFocus();
        consumed=true;
      }
    } else {
      MovingLightMode=false;
      if (wxConsumeTrackBallEvent( event, track)) {
        SetFocus();
        consumed=true;
      }
    }
    
    if ((consumed) && (!event.ButtonUp()) && (!event.ButtonDown())) SceneChanged();
    
/*   if ( event.m_rightUp ) {
      useLightTrack=false;
    }*/

}
