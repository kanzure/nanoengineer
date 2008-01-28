#ifndef GLT_COLOR_H
#define GLT_COLOR_H

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
    \brief   OpenGL Color Interface
    \ingroup GLT

    $Id: color.h,v 1.13 2002/10/07 16:27:46 nigels Exp $

    $Log: color.h,v $
    Revision 1.13  2002/10/07 16:27:46  nigels
    Added CVS version control info


*/

#include "glt_config.h"
#include "glt_gl.h"

#include <string>

#include "glt_vector3.h"

/*! \class   GltColor
    \brief   OpenGL RGB Color
    \ingroup GLT

    See also Colorspace FAQ
    http://www.faqs.org/faqs/graphics/colorspace-faq/
*/

class GltColor : public Vector
{
public:
	//
	// Constructors
	//

	/// Default constructor: black color
	GltColor();
	/// Construct from float red, green and blue components
	GltColor(const float  red,const float  green,const float  blue,const float  alpha = 1.0);
	/// Construct from double precision red, green and blue components
	GltColor(const double red,const double green,const double blue,const double alpha = 1.0);
	/// Construct from integer red, green and blue components
	GltColor(const int    red,const int    green,const int    blue,const int    alpha = 1);
	/// Copy constructor
	GltColor(const GltColor &col);
	/// Copy constructor with alpha
	GltColor(const GltColor &col,const real alpha);
	/// Construct from x,y,z tuple
	GltColor(const Vector &col);
	/// Construct from name or HTML color string
	GltColor(const std::string &name);

	/// Destructor
	~GltColor();

	/// Assignment operator
	GltColor &operator=(const GltColor &);

	//
	// OpenGL convenience functions
	//

	/// Set the current OpenGL color
	void glColor() const;

	/// Set the current OpenGL color with alpha
	void glColor(const GLdouble alpha)  const;

	/// Set the current OpenGL clear color
	void glClearColor() const;

	/// Set the current OpenGL fog color
        void glFogColor() const;

	/// Set an OpenGL material setting
	void glMaterial(const GLenum face,const GLenum field) const;

	/// Get an OpenGL material setting
	void glGetMaterial(const GLenum face,const GLenum field);

	/// Set an OpenGL lighting setting
	void glLight(const GLenum light,const GLenum field) const;

	/// Get an OpenGL lighting setting
	void glGetLight(const GLenum light,const GLenum field);

	//
	// Access
	//

	/// red component
	real &red();
	/// green component
	real &green();
	/// blue component
	real &blue();
	/// alpha component
	real &alpha();

	/// red component
	const real &red()    const;
	/// green component
	const real &green()  const;
	/// blue component
	const real &blue()   const;
	/// alpha component
	const real &alpha()  const;

	//
	// Misc
	//

	/// Obtain the brightness of the color
	const real brightness() const;

	/// Convert to HSV
	void toHSV(real &h,real &s,real &v) const;

	/// Convert from HSV
	void fromHSV(const real h,const real s,const real v);

#if 0
	/// CIE XYZ conversion
	void toCIE(Vector &XYZ) const;
#endif

	/// Is the color (exactly) grey?
	const bool isGrey() const;

	/// Convert to HTML RGB color string
	std::string html() const;

	/// less-than comparison
	bool operator< (const GltColor &c) const;
	/// greater-than comparison
	bool operator> (const GltColor &c) const;
	/// equal-to comparison
	bool operator==(const GltColor &c) const;

	//
	// Binary operators
	//

	friend GltColor operator*(const GltColor  &c, const real x);
	friend GltColor operator/(const GltColor  &c, const real x);
	friend GltColor operator*(const real       x, const GltColor &c);
	friend GltColor operator+(const GltColor &c1, const GltColor &c2);
	friend GltColor operator-(const GltColor &c1, const GltColor &c2);

private:
	real _alpha;

	static const int       _rgbSize;
	static const char     *_rgbName [];
	static const GltColor *_rgbValue[];
};

//////////////////////////////////////////////////////////////////////

/*! \class   GltClearColor
    \brief   OpenGL RGB Clear Color
    \ingroup GLT
*/

class GltClearColor : public GltColor
{
public:
	//
	// Constructor/Destructor
	//

	/// Constructor
	GltClearColor(bool getIt = false);
	/// Destructor
	~GltClearColor();

	//
	// Get/Set
	//

	/// Get the current OpenGL clear color
	void get();
	/// Set the current OpenGL clear color
	void set() const;
	/// Set the current OpenGL clear color
	void set(const GltColor &col);
};

#endif
