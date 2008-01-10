

#include <wx/defs.h>
#include <wx/app.h>
//#include <wx/menu.h>
//#include <wx/dcclient.h>


#include <wrap/gui/trackball.h>
using namespace vcg;
using namespace std;

bool wxConsumeTrackBallEvent(wxKeyEvent& event, bool down, Trackball &track){
  if (event.m_keyCode==WXK_CONTROL) { 
    if (down) track.ButtonDown(vcg::Trackball::KEY_CTRL); 
    else track.ButtonUp(vcg::Trackball::KEY_CTRL); 
  }
  if (event.m_keyCode==WXK_SHIFT) { 
    if (down) track.ButtonDown(vcg::Trackball::KEY_SHIFT); 
    else track.ButtonUp(vcg::Trackball::KEY_SHIFT); 
  }
  return false;
}

bool wxConsumeTrackBallEvent(wxSizeEvent& mevent, Trackball &track){
  return false;
}

bool wxConsumeTrackBallEvent(wxMouseEvent& mevent, Trackball &track)
{
  int width, height;
  GLint viewport[4];
  glGetIntegerv(GL_VIEWPORT,viewport);
  width=viewport[2];
  height=viewport[3];
  
  if ( mevent.Dragging() /*|| mevent.Moving() */) {
    track.MouseMove(mevent.m_x, (height - mevent.m_y));
    return true;
  }
  
  if ( mevent.LeftUp() || mevent.RightUp() ) {
    track.MouseUp  (mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_LEFT); 
    return true;
  }

  if ( mevent.LeftDown() || mevent.RightDown() ) {
    track.MouseDown(mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_LEFT); 
    return true;
  }

  if ( mevent.MiddleDown() ) {
    track.MouseDown(mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_MIDDLE); 
    return true;
  }
  if ( mevent.MiddleUp() ) {
    track.MouseUp  (mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_MIDDLE); 
    return true;
  }

/*  if ( mevent.RightUp() ) {
    track.MouseUp  (mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_RIGHT); 
    return true;
  }

  if ( mevent.RightDown() ) {
    track.MouseDown(mevent.m_x, (height - mevent.m_y), vcg::Trackball::BUTTON_RIGHT); 
    return true;
  }*/

  if ( mevent.m_wheelRotation !=0 ) {
    if ( mevent.m_wheelRotation>0) track.MouseWheel( 1); 
    if ( mevent.m_wheelRotation<0) track.MouseWheel(-1); 
    return true;
  }
        /*
  switch( event.type ) {
      case SDL_KEYDOWN:                                        
			  switch(event.key.keysym.sym) {
//			    case SDLK_h: track.Home(); return true;
			    case SDLK_RCTRL:
			    case SDLK_LCTRL: track.ButtonDown(vcg::Trackball::KEY_CTRL); return true;
			    case SDLK_LSHIFT:
			    case SDLK_RSHIFT: track.ButtonDown(vcg::Trackball::KEY_SHIFT); return true;
			  }  break;
      case SDL_KEYUP: 
			  switch(event.key.keysym.sym) {
			    case SDLK_RCTRL:
			    case SDLK_LCTRL: track.ButtonUp(vcg::Trackball::KEY_CTRL); return true;
			    case SDLK_LSHIFT:
			    case SDLK_RSHIFT: track.ButtonUp(vcg::Trackball::KEY_SHIFT); return true;
			  }	break;
      case SDL_MOUSEBUTTONDOWN:   
	      switch(event.button.button) {
          case SDL_BUTTON_WHEELUP:    track.MouseWheel( 1); return true;
          case SDL_BUTTON_WHEELDOWN:  track.MouseWheel(-1); return true;
          case SDL_BUTTON_LEFT:	      track.MouseDown(event.button.x, (height - event.button.y), vcg::Trackball::BUTTON_LEFT); return true;
          case SDL_BUTTON_RIGHT:	    track.MouseDown(event.button.x, (height - event.button.y), vcg::Trackball::BUTTON_RIGHT);return true;
        } break;
        
      case SDL_MOUSEBUTTONUP:          
	      switch(event.button.button) {
          case SDL_BUTTON_LEFT:	      track.MouseUp(event.button.x, (height - event.button.y), vcg::Trackball::BUTTON_LEFT); return true;
          case SDL_BUTTON_RIGHT:	    track.MouseUp(event.button.x, (height - event.button.y), vcg::Trackball::BUTTON_RIGHT);return true;
        } break;
      case SDL_MOUSEMOTION: 
	      track.MouseMove(event.button.x, (height - event.button.y));
	      while(SDL_PeepEvents(&event, 1, SDL_GETEVENT, SDL_MOUSEMOTIONMASK))
	      track.MouseMove(event.button.x, (height - event.button.y));
	      return true;  
      default: break;
      }
      */
		return false;
}
