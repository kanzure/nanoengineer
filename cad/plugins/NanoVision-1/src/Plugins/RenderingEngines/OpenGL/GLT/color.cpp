#include "glt_color.h"

/*! \file 
    \ingroup GLT
    
    $Id: color.cpp,v 1.16 2002/10/09 15:09:38 nigels Exp $
    
    $Log: color.cpp,v $
    Revision 1.16  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include <string>
#include <iostream>
#include <cassert>
#include <cstdio>

using namespace std;

// #include <glt/rgb.h>
#include "glt_error.h"
#include "glt_gl.h"
#include "glt_string.h"
// #include <math/matrix4.h>

GltColor::GltColor()
: Vector(Vector0), _alpha(1.0)
{
}

GltColor::GltColor(const float red,const float green,const float blue,const float alpha)
: Vector(red,green,blue), _alpha(alpha)
{
}

GltColor::GltColor(const double red,const double green,const double blue,const double alpha)
: Vector(red,green,blue), _alpha(alpha)
{
}

GltColor::GltColor(const int red,const int green,const int blue,const int alpha)
: Vector(red,green,blue), _alpha(alpha)
{
}

GltColor::GltColor(const GltColor &col,const real alpha)
: Vector(col), _alpha(alpha)
{
}

GltColor::GltColor(const Vector &col)
: Vector(col), _alpha(1.0)
{
}

GltColor::GltColor(const GltColor &col)
: Vector(col), _alpha(col._alpha)
{
}

GltColor::GltColor(const string &name)
: _alpha(1.0)
{
	// Convert from HTML style color string

	if (name.size()>=7)
	{
		if (name[0]=='#')
		{
			const int r = fromHex4(name[1])<<4 | fromHex4(name[2]);
			const int g = fromHex4(name[3])<<4 | fromHex4(name[4]);
			const int b = fromHex4(name[5])<<4 | fromHex4(name[6]);

			red()   = real(r)/255.0;
			green() = real(g)/255.0;
			blue()  = real(b)/255.0;

			return;
		}
	}

	// Do a binary search through the list of names

	int i=0;
	int j=_rgbSize;

	for (;;)
	{
		int k = ((j-i)>>1)+i;
		const int res = strcmp(name.c_str(),_rgbName[k]);

		if (res<0)
			j = k;
		else
			if (res>0)
				i = k+1;
			else
			{
				operator=(*_rgbValue[k]);
				return;
			}

		if (i==k && j==k || i==_rgbSize)
		{
			assert(!"Color not found");
                        operator=(GltColor(0.0,0.0,0.0));
			return;
		}
	}
}

GltColor::~GltColor()
{
}

GltColor &
GltColor::operator=(const GltColor &col)
{
	red()   = col.red();
	green() = col.green();
	blue()  = col.blue();
	alpha() = col.alpha();

	return *this;
}

void 
GltColor::glColor() const
{
	#ifdef GLT_FAST_FLOAT
	::glColor4f(x(),y(),z(),_alpha);
	#else
	::glColor4d(x(),y(),z(),_alpha);
	#endif
}

void 
GltColor::glColor(const GLdouble alpha) const
{
	#ifdef GLT_FAST_FLOAT
	::glColor4f(x(),y(),z(),alpha);
	#else
	::glColor4d(x(),y(),z(),alpha);
	#endif
}

void 
GltColor::glClearColor() const
{
	::glClearColor(x(),y(),z(),_alpha);
}

void
GltColor::glFogColor() const
{
	const float col[4] = { x(), y(), z(), _alpha };
    ::glFogfv(GL_FOG_COLOR, col);
}

void 
GltColor::glMaterial(const GLenum face,const GLenum field) const
{
	assert(face==GL_FRONT_AND_BACK || face==GL_FRONT || face==GL_BACK);
	assert(field==GL_AMBIENT || field==GL_DIFFUSE || field==GL_SPECULAR || field==GL_EMISSION);

    GLERROR(std::cerr);

	const GLfloat val[4] = { x(), y(), z(), _alpha };
	::glMaterialfv(face,field,val);

    GLERROR(std::cerr);
}

void 
GltColor::glGetMaterial(const GLenum face,const GLenum field)
{
	assert(face==GL_FRONT_AND_BACK || face==GL_FRONT || face==GL_BACK);
	assert(field==GL_AMBIENT || field==GL_DIFFUSE || field==GL_SPECULAR || field==GL_EMISSION);

	GLERROR(std::cerr);

	GLfloat val[4];
	::glGetMaterialfv(face,field,val);
	x() = val[0]; y() = val[1]; z() = val[2]; _alpha = val[3];

	GLERROR(std::cerr);
}

void 
GltColor::glLight(const GLenum light,const GLenum field) const
{
	assert(light>=GL_LIGHT0 && light<=GL_LIGHT7);
	assert(field==GL_AMBIENT || field==GL_DIFFUSE || field==GL_SPECULAR || field==GL_POSITION || field==GL_SPOT_DIRECTION);

	GLERROR(std::cerr);

	const GLfloat val[4] = { x(), y(), z(), _alpha };
	::glLightfv(light,field,val);

	GLERROR(std::cerr);
}

void 
GltColor::glGetLight(const GLenum light,const GLenum field)
{
	assert(light>=GL_LIGHT0 && light<=GL_LIGHT7);
	assert(field==GL_AMBIENT || field==GL_DIFFUSE || field==GL_SPECULAR || field==GL_POSITION || field==GL_SPOT_DIRECTION);

	GLERROR(std::cerr);

	GLfloat val[4];
	::glGetLightfv(light,field,val);
	x() = val[0]; y() = val[1]; z() = val[2]; _alpha = val[3];

	GLERROR(std::cerr);
}

	  real &GltColor::red()    { return x();    }
	  real &GltColor::green()  { return y();    }
	  real &GltColor::blue()   { return z();    }
	  real &GltColor::alpha()  { return _alpha; }

const real &GltColor::red()    const { return x();    }
const real &GltColor::green()  const { return y();    }
const real &GltColor::blue()   const { return z();    }
const real &GltColor::alpha()  const { return _alpha; }

const real 
GltColor::brightness() const
{
	// (from Colorspace FAQ)
	//  Y = 0.212671 * R + 0.715160 * G + 0.072169 * B;
  
  	return 0.212671*red() + 0.715160*green() + 0.072169*blue();
}

void
GltColor::toHSV(real &h,real &s,real &v) const
{
	// Based on http://www.cs.rit.edu/~ncs/color/t_convert.html

	const real min = MIN(red(),MIN(green(),blue()));
	const real max = MAX(red(),MAX(green(),blue()));

	v = max;
	
	const real delta = max-min;

	if (max!=0.0)
		s = delta/max;
	else 
	{
		// Black
		h = 0.0;
		s = 0.0;
		return;
	}

	if (delta==0.0)	
	{
		h = 0.0;
		s = 0.0;
	}
	else
		if (red()==max)
			h = (green()-blue()) / delta;			// between yellow & magenta
		else 
			if(green()==max)
				h = 2.0 + (blue()-red())/delta;		// between cyan & yellow
			else
				h = 4.0 + (red()-green())/delta;	// between magenta & cyan

	// Scale h to degrees
	
	h *= 60;

	if (h<0.0)
		h += 360.0;
}

void
GltColor::fromHSV(const real h,const real s,const real v)
{
	// Based on http://www.cs.rit.edu/~ncs/color/t_convert.html

	// Achromatic case (grey)

	if (s==0.0) 
	{
		red() = green() = blue() = v;
		return;
	}

		
	const real hue = h/60.0;	// sector 0 to 5
	const int  i   = int(floor(hue));
	const real f   = hue-i;		// factorial part of h
	const real p = v*(1-s);
	const real q = v*(1-s*f);
	const real t = v*(1-s*(1-f));

	switch (i) 
	{
	case 0:
		red()   = v;
		green() = t;
		blue()  = p;
		break;
	case 1:
		red()   = q;
		green() = v;
		blue()  = p;
		break;
	case 2:
		red()   = p;
		green() = v;
		blue()  = t;
		break;
	case 3:
		red()   = p;
		green() = q;
		blue()  = v;
		break;
	case 4:
		red()   = t;
		green() = p;
		blue()  = v;
		break;
	default:		// case 5:
		red()   = v;
		green() = p;
		blue()  = q;
		break;
	}
}

//

const bool 
GltColor::isGrey() const
{
	return red()==green() && green()==blue();
}

std::string 
GltColor::html() const
{
	const int r = CLAMP(int(red()  *255.0+0.5),0,255);
	const int g = CLAMP(int(green()*255.0+0.5),0,255);
	const int b = CLAMP(int(blue() *255.0+0.5),0,255);

	char buffer[8];
	sprintf(buffer,"#%02X%02X%02X",r,g,b);
	return buffer;
}

bool GltColor::operator< (const GltColor &c) const
{
	if (red()!=c.red())     return red()<c.red();
	if (green()!=c.green()) return green()<c.green();
	return blue()<c.blue();
}

bool GltColor::operator> (const GltColor &c) const
{
	if (red()!=c.red())     return red()>c.red();
	if (green()!=c.green()) return green()>c.green();
	return blue()>c.blue();
}

bool GltColor::operator==(const GltColor &c) const
{
	return red()==c.red() && green()==c.green() && blue()==c.blue();
}

/*!
	\brief Scale color
	\ingroup GLT
*/
GltColor operator*(const GltColor  &c, const real x)
{
	return GltColor(c.red()*x,c.green()*x,c.blue()*x,c.alpha()*x);
}

/*!
	\brief Scale color
	\ingroup GLT
*/
GltColor operator/(const GltColor  &c, const real x)
{
	const double s = 1.0/x;
	return GltColor(c.red()*s,c.green()*s,c.blue()*s,c.alpha()*s);
}

/*!
	\brief Scale color
	\ingroup GLT
*/
GltColor operator*(const real      x, const GltColor &c)
{
	return GltColor(c.red()*x,c.green()*x,c.blue()*x,c.alpha()*x);
}

/*!
	\brief Add red, green and blue components
	\ingroup GLT
*/
GltColor operator+(const GltColor &c1, const GltColor &c2)
{
	return GltColor(c1.red()+c2.red(),c1.green()+c2.green(),c1.blue()+c2.blue(),c1.alpha()+c2.alpha());
}

/*!
	\brief Subtract red, green and blue components
	\ingroup GLT
*/
GltColor operator-(const GltColor &c1, const GltColor &c2)
{
	return GltColor(c1.red()-c2.red(),c1.green()-c2.green(),c1.blue()-c2.blue(),c1.alpha()-c2.alpha());
}

//////////////////////////////////////////////////////////////////////

GltClearColor::GltClearColor(bool getIt)
{
	if (getIt)
		get();
}

GltClearColor::~GltClearColor()
{
}

void 
GltClearColor::get()
{
	GLdouble tmp[4];
	glGetDoublev(GL_COLOR_CLEAR_VALUE,tmp);
	x() = tmp[0];
	y() = tmp[1];
	z() = tmp[2];
}
	
void 
GltClearColor::set() const
{
	GltColor::glClearColor();
}

void 
GltClearColor::set(const GltColor &col)
{
	x() = col.x();
	y() = col.y();
	z() = col.z();
	GltColor::glClearColor();
}
