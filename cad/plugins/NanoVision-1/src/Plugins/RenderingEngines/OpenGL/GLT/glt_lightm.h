#ifndef GLT_LIGHTM_H
#define GLT_LIGHTM_H

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
    \brief OpenGL Lighting Model Class
    \ingroup GLT
    
    $Id: lightm.h,v 1.6 2002/10/07 16:33:35 nigels Exp $
    
    $Log: lightm.h,v $
    Revision 1.6  2002/10/07 16:33:35  nigels
    Added CVS info

    
*/

#include "glt_config.h"
#include "glt_gl.h"

#include <iosfwd>

/*! \class GltLightModel
    \brief OpenGL Lighting Model Class
    \ingroup GLT

    Convenient manipulation of lighting model configuration.
*/

class GltLightModel
{
public:
	
	GltLightModel(const bool getIt = false);
	~GltLightModel();

	void get();
	void set();

	void setAmbient    (const GLfloat r,const GLfloat g,const GLfloat b,const GLfloat a);
	void setLocalViewer(const GLboolean localViewer);
	void setTwoSide    (const GLboolean twoSide);

	GLfloat   *ambient();
	GLboolean &localViewer();
	GLboolean &twoSide();

private:

	GLfloat _ambient[4];
	GLboolean  _localViewer;
	GLboolean  _twoSide;
};

#endif
