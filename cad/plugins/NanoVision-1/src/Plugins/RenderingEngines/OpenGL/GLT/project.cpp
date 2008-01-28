#include "glt_project.h"

/*! \file 
    \ingroup GLT
    
    $Id: project.cpp,v 1.9 2002/10/09 15:09:38 nigels Exp $
    
    $Log: project.cpp,v $
    Revision 1.9  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include <cassert>
#include <iosfwd>
using namespace std;

GltOrtho::GltOrtho()
: _left(-1.0), _right(1.0), _bottom(-1.0), _top(1.0), _zNear(-10.0), _zFar(10.0)
{
}

GltOrtho::~GltOrtho()
{
}

void 
GltOrtho::set()
{
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(_left,_right,_bottom,_top,_zNear,_zFar);
	glMatrixMode(GL_MODELVIEW);
}

void 
GltOrtho::set(int width,int height)
{
	GLdouble x = 1.0;
	GLdouble y = 1.0;

	if (width!=0 && height!=0)
	{
		if (width>height)
			x = GLdouble(width)/GLdouble(height);
		else
			y = GLdouble(height)/GLdouble(width);
	}

	_left   = -x;
	_right  =  x;
	_bottom = -y;
	_top    =  y;
	set();
}

GLdouble &GltOrtho::left()   { return _left;   }
GLdouble &GltOrtho::right()  { return _right;  }
GLdouble &GltOrtho::bottom() { return _bottom; }
GLdouble &GltOrtho::top()    { return _top;    }
GLdouble &GltOrtho::zNear()  { return _zNear;  }
GLdouble &GltOrtho::zFar()   { return _zFar;   }

const GLdouble &GltOrtho::left()   const { return _left;   }
const GLdouble &GltOrtho::right()  const { return _right;  }
const GLdouble &GltOrtho::bottom() const { return _bottom; }
const GLdouble &GltOrtho::top()    const { return _top;    }
const GLdouble &GltOrtho::zNear()  const { return _zNear;  }
const GLdouble &GltOrtho::zFar()   const { return _zFar;   }

bool 
GltOrtho::tile(GltOrtho &frust,const int dx,const int dy,const int n) const
{
	if (dx<1 || dy<1 || n<0 || n>=dx*dy)
	{
		frust = *this;
		return false;
	}

	const int px = n%dx;
	const int py = n/dx;

	const GLdouble width  = (_right-_left)/dx;
	const GLdouble height = (_top-_bottom)/dy;
	
	assert(py<=dy);

	if (py<dy)
	{
		frust._left = frust._right  = _left   + width*px;
		frust._top  = frust._bottom = _bottom + height*py;
	
		frust._right += width;
		frust._top   += height;

		frust._zNear = _zNear;
		frust._zFar  = _zFar;

		return true;
	}
	else
		return false;
}

///////////////////////////


GltFrustum::GltFrustum()
: _left(-1.0), _right(1.0), _bottom(-1.0), _top(1.0), _zNear(1.0), _zFar(10.0)
{
}

GltFrustum::~GltFrustum()
{
}

void 
GltFrustum::set()
{
	assert(_zNear>0.0);
	assert(_zFar>0.0);

	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glFrustum(_left,_right,_bottom,_top,_zNear,_zFar);
	glMatrixMode(GL_MODELVIEW);
}

void 
GltFrustum::set(int width,int height)
{
	GLdouble x = 1.0;
	GLdouble y = 1.0;

	if (width!=0 && height!=0)
	{
		if (width>height)
			x = GLdouble(width)/GLdouble(height);
		else
			y = GLdouble(height)/GLdouble(width);
	}

	_left   = -x;
	_right  =  x;
	_bottom = -y;
	_top    =  y;
	set();
}

GLdouble &GltFrustum::left()   { return _left;   }
GLdouble &GltFrustum::right()  { return _right;  }
GLdouble &GltFrustum::bottom() { return _bottom; }
GLdouble &GltFrustum::top()    { return _top;    }
GLdouble &GltFrustum::zNear()  { return _zNear;  }
GLdouble &GltFrustum::zFar()   { return _zFar;   }

const GLdouble &GltFrustum::left()   const { return _left;   }
const GLdouble &GltFrustum::right()  const { return _right;  }
const GLdouble &GltFrustum::bottom() const { return _bottom; }
const GLdouble &GltFrustum::top()    const { return _top;    }
const GLdouble &GltFrustum::zNear()  const { return _zNear;  }
const GLdouble &GltFrustum::zFar()   const { return _zFar;   }

bool 
GltFrustum::tile(GltFrustum &frust,const int dx,const int dy,const int n) const
{
	if (dx<1 || dy<1 || n<0 || n>=dx*dy)
	{
		frust = *this;
		return false;
	}

	const int px = n%dx;
	const int py = n/dx;

	const GLdouble width  = (_right-_left)/dx;
	const GLdouble height = (_top-_bottom)/dy;
	
	assert(py<=dy);

	if (py<dy)
	{
		frust._left = frust._right  = _left   + width*px;
		frust._top  = frust._bottom = _bottom + height*py;
	
		frust._right += width;
		frust._top   += height;

		frust._zNear = _zNear;
		frust._zFar  = _zFar;

		return true;
	}
	else
		return false;
}

