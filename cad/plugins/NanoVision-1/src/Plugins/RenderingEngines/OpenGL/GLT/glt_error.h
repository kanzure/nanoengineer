#ifndef GLT_ERROR_H
#define GLT_ERROR_H

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
    \brief   OpenGL Debugging Tools
    \ingroup GLT

    $Id: error.h,v 1.9 2002/10/07 16:27:46 nigels Exp $

    $Log: error.h,v $
    Revision 1.9  2002/10/07 16:27:46  nigels
    Added CVS version control info


*/

#include <ostream>
#include <string>

/*! \define  GLERROR
	\brief	 Check OpenGL error state
	\ingroup GLT
	\note    Does nothing if NDEBUG is defined
*/

#include "glt_config.h"
#include "glt_gl.h"
#include "glt_glu.h"


inline GLenum GLERROR(std::ostream& strm)
{
    GLenum firstCode = glGetError();
    for(GLenum code = firstCode; code!=GL_NO_ERROR; code = glGetError())
    {
        strm << __FILE__;
        strm << ':' << __LINE__;
        strm << ' ' << (char *) gluErrorString(code) << std::endl;
    }
    return firstCode;
}

/// Display warning 
void gltError(const std::string &message);

/// Display error
void gltWarning(const std::string &message);

#endif

