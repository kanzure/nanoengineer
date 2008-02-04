#ifndef GLT_GL_H
#define GLT_GL_H

/*

  GLT OpenGL C++ Toolkit      
  Copyright (C) 2000-2002 Nigel Stewart
  Email: nigels@nigels.com   WWW: http://www.nigels.com/glt/

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

*/

/*! \file 
    \brief   OpenGL (proxy) header file
    \ingroup GLT

    #include <GL/gl.h> proxy header

    This header can be used instead of GL/gl.h.
	Other necessary dependencies such as windows.h
	are handled here.
	
    $Id: gl.h,v 1.10 2002/10/09 15:18:17 nigels Exp $
    
    $Log: gl.h,v $
    Revision 1.10  2002/10/09 15:18:17  nigels
    Tidy

    Revision 1.9  2002/10/07 16:27:46  nigels
    Added CVS version control info
    
*/

#include "glt_config.h"

#ifdef GLT_WIN32
#define NOMINMAX
#include <windows.h>
#endif

extern "C" {
#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif
}

#endif
