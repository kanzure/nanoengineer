#ifndef GLT_PROJECT_H
#define GLT_PROJECT_H

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
    \brief   OpenGL Projection Classes
    \ingroup GLT
    
    $Id: project.h,v 1.11 2002/10/07 16:33:35 nigels Exp $
    
    $Log: project.h,v $
    Revision 1.11  2002/10/07 16:33:35  nigels
    Added CVS info

    
*/

#include "glt_config.h"
#include "glt_gl.h"

/*! \class   GltOrtho
    \brief   OpenGL Orthographic Camera Class
    \ingroup GLT
*/

class GltOrtho
{
public:
	
	/// Constructor
	GltOrtho();
	/// Destructor
	~GltOrtho();

	/// Set OpenGL viewing matrix
	void set();
	/// Set OpenGL viewing matrix
	void set(int width,int height);

									/// Left position
	GLdouble &left();
									/// Right position
	GLdouble &right();
									/// Bottom position
	GLdouble &bottom();
									/// Top position
	GLdouble &top();
									/// zNear position
	GLdouble &zNear();
									/// zFar position
	GLdouble &zFar();

									/// Left position
	const GLdouble &left()   const;
									/// Right position
	const GLdouble &right()  const;
									/// Bottom position
	const GLdouble &bottom() const;
									/// Top position
	const GLdouble &top()    const;
									/// zNear position
	const GLdouble &zNear()  const;
									/// zFar position
	const GLdouble &zFar()   const;

	/// Calculate the n'th tile of a grid: dx*dy
	bool tile(GltOrtho &frust,const int dx,const int dy,const int n) const;

private:

	GLdouble _left;
	GLdouble _right;
	GLdouble _bottom;
	GLdouble _top;
	GLdouble _zNear;
	GLdouble _zFar;
};

/*! \class   GltFrustum
    \brief   OpenGL Perspective Camera Class
    \ingroup GLT
*/

class GltFrustum
{
public:
	
	/// Constructor
	GltFrustum();
	/// Destructor
	~GltFrustum();

	/// Set OpenGL viewing matrix
	void set();
	/// Set OpenGL viewing matrix
	void set(int width,int height);

									/// Left position
	GLdouble &left();
									/// Right position
	GLdouble &right();
									/// Bottom position
	GLdouble &bottom();
									/// Top position
	GLdouble &top();
									/// zNear position
	GLdouble &zNear();
									/// zFar position
	GLdouble &zFar();

									/// Left position
	const GLdouble &left()   const;
									/// Right position
	const GLdouble &right()  const;
									/// Bottom position
	const GLdouble &bottom() const;
									/// Top position
	const GLdouble &top()    const;
									/// zNear position
	const GLdouble &zNear()  const;
									/// zFar position
	const GLdouble &zFar()   const;

	/// Calculate the n'th tile of a grid: dx*dy
	bool tile(GltFrustum &frust,const int dx,const int dy,const int n) const;

private:

	GLdouble _left;
	GLdouble _right;
	GLdouble _bottom;
	GLdouble _top;
	GLdouble _zNear;
	GLdouble _zFar;
};

#endif
