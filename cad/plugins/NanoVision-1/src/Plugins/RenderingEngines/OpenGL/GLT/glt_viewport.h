#ifndef GLT_VIEWPORT_H
#define GLT_VIEWPORT_H

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
    \brief   OpenGL Viewport Class
    \ingroup GLT
    
    $Id: viewport.h,v 1.13 2002/10/11 08:33:21 nigels Exp $
    
    $Log: viewport.h,v $
    Revision 1.13  2002/10/11 08:33:21  nigels
    Added GLint *() operator
    Added resize to (image-space) bounding box

    Revision 1.12  2002/10/07 16:33:35  nigels
    Added CVS info

    
*/

#include "glt_config.h"
#include "glt_gl.h"

#include <iosfwd>

/*! \enum    GltHorizontalAlignment
    \brief   Horizontal alignment
    \ingroup GLT
*/

typedef enum GltHorizontalAlignment
{
	GLT_ALIGN_LEFT = 0,
	GLT_ALIGN_HCENTER,
	GLT_ALIGN_RIGHT
} GltHorizontalAlignment;

/*! \enum    GltVerticalAlignment
    \brief   Vertical alignment
    \ingroup GLT
*/

typedef enum GltVerticalAlignment
{
	GLT_ALIGN_TOP = 0,
	GLT_ALIGN_VCENTER,
	GLT_ALIGN_BOTTOM
} GltVerticalAlignment;

class GltTexture;

/*! \class   GltViewport
    \brief   OpenGL Viewport Class
	\ingroup GLT

    Convenient manipulation of viewport information.
*/

class BoundingBox;

class GltViewport
{
public:
	
	/// Constructor
	GltViewport(bool getIt = false);
	/// Copy constructor
	GltViewport(const GltViewport &viewport);
	/// Constructor
	GltViewport(const GLint x,const GLint y,const GLint width,const GLint height);
	/// Destructor
	~GltViewport();

	/// Is the viewport a valid size?
	bool valid() const;

	/// Get the current OpenGL viewport
	void get();

	/// Set the current OpenGL viewport
	void set() const;
	/// Set the current OpenGL viewport width and height
	void set(const GLint width,const GLint height);
	/// Set the current OpenGL viewport x, y, width and height
	void set(const GLint x,const GLint y,const GLint width,const GLint height);

	/// Left position of viewport
	GLint &x();
	/// Right position of viewport
	GLint &y();
	/// Width of viewport
	GLint &width();
	/// Height of viewport
	GLint &height();

	/// Left position of viewport
	const GLint &x() const;
	/// Right position of viewport
	const GLint &y() const;
	/// Width of viewport
	const GLint &width() const;
	/// Height of viewport
	const GLint &height() const;

	/// Viewport size, in pixels
	const GLint  pixels() const;

	///
	operator       GLint *();
	///
	operator const GLint *() const;

	/// Resize the viewport
	bool resize(const GLint width,const GLint height);
	/// Resize the viewport
	bool resize(const GLint x,const GLint y,const GLint width,const GLint height); 
	/// Resize the viewport to fit a texture
	bool resize(const GltTexture &texture);
	/// Resize the viewport to fit an (image-space) bounding box	
	bool resize(const BoundingBox &box);
	
	/// Position viewport horizontally, relative to another viewport
	bool align(const GltHorizontalAlignment &align,const GltViewport &window);
	/// Position viewport vetically, relative to another viewport
	bool align(const GltVerticalAlignment   &align,const GltViewport &window);

	/// Shrink a viewport by a particular margin (in pixels)
	bool shrink(const GLint w);

	//

	/// Assignment operator
	GltViewport &operator=(const GltViewport &viewport);

	/// Compare viewports
	bool operator==(const GltViewport &viewport) const;
	/// Compare viewports
	bool operator!=(const GltViewport &viewport) const;

	//

	/// Draw a covering quad relative to viewport
	void drawQuad() const;
	/// Draw surrounding lines relative to viewport
	void drawLines() const;

private:
	GLint _viewport[4];
};

#endif
