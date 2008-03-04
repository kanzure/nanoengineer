#include "glt_viewport.h"

/*! \file 
    \ingroup GLT
    
    $Id: viewport.cpp,v 1.13 2002/10/11 08:33:12 nigels Exp $
    
    $Log: viewport.cpp,v $
    Revision 1.13  2002/10/11 08:33:12  nigels
    Added GLint *() operator
    Added resize to (image-space) bounding box

    Revision 1.12  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include "glt_texture.h"
#include "glt_error.h"

#include "glt_bbox.h"

#include <cstring>
#include <iostream>
using namespace std;

GltViewport::GltViewport(bool getIt)
{
	memset(_viewport,0,sizeof(_viewport));

	if (getIt)
		get();
}

GltViewport::GltViewport(const GltViewport &viewport)
{
	memcpy(_viewport,viewport._viewport,sizeof(_viewport));
}

GltViewport::GltViewport(const GLint x,const GLint y,const GLint width,const GLint height)
{
	set(x,y,width,height);
}

GltViewport::~GltViewport()
{
}

GltViewport &
GltViewport::operator=(const GltViewport &viewport)
{
	memcpy(_viewport,viewport._viewport,sizeof(_viewport));
	return *this;
}

bool 
GltViewport::operator==(const GltViewport &viewport) const
{
	return memcmp(_viewport,viewport._viewport,sizeof(_viewport))==0;
}

bool 
GltViewport::operator!=(const GltViewport &viewport) const
{
	return memcmp(_viewport,viewport._viewport,sizeof(_viewport))!=0;
}

bool 
GltViewport::valid() const
{
	return x()>=0 && y()>=0 && width()>0 && height()>0;
}

void 
GltViewport::get()
{
	GLERROR(std::cerr);
	glGetIntegerv(GL_VIEWPORT,(GLint *) _viewport);
	GLERROR(std::cerr);
}

void 
GltViewport::set() const
{
	GLERROR(std::cerr);
	glViewport(x(),y(),width(),height());
	GLERROR(std::cerr);
}

void 
GltViewport::set(const GLint width,const GLint height)
{
	GltViewport::width()  = width;
	GltViewport::height() = height;
	set();
}

void 
GltViewport::set(const GLint x,const GLint y,const GLint width,const GLint height)
{
	GltViewport::x() = x;
	GltViewport::y() = y;
	GltViewport::width() = width;
	GltViewport::height() = height;
	set();
}

//

GLint &GltViewport::x()      { return _viewport[0]; }
GLint &GltViewport::y()      { return _viewport[1]; }
GLint &GltViewport::width()  { return _viewport[2]; }
GLint &GltViewport::height() { return _viewport[3]; }

const GLint &GltViewport::x() const      { return _viewport[0]; }
const GLint &GltViewport::y() const      { return _viewport[1]; }
const GLint &GltViewport::width() const  { return _viewport[2]; }
const GLint &GltViewport::height() const { return _viewport[3]; }

const GLint  GltViewport::pixels() const { return _viewport[2]*_viewport[3]; }

GltViewport::operator const GLint *() const { return _viewport; }
GltViewport::operator       GLint *()       { return _viewport; }

//

bool GltViewport::resize(const GLint width,const GLint height)
{
	GltViewport::width() = width;
	GltViewport::height() = height;	

	return valid();
}

bool GltViewport::resize(const GLint x,const GLint y,const GLint width,const GLint height)
{
	GltViewport::x() = x;
	GltViewport::y() = y;
	GltViewport::width() = width;
	GltViewport::height() = height;	

	return valid();
}

bool GltViewport::resize(const GltTexture &texture)
{
	GltViewport::width() = texture.width();
	GltViewport::height() = texture.height();
	
	return valid();
}

bool GltViewport::resize(const BoundingBox &box)
{
	GltViewport::x()      = (GLint) floor(box.min().x());
	GltViewport::y()      = (GLint) floor(box.min().y());
	GltViewport::width()  = (GLint) ceil(box.width());
	GltViewport::height() = (GLint) ceil(box.height());	
	
	return valid();
}
                        
bool GltViewport::align(const GltHorizontalAlignment &align,const GltViewport &window)
{
	switch (align)
	{
	case GLT_ALIGN_LEFT:    x() = window.x();                                 break;
	case GLT_ALIGN_HCENTER: x() = window.x() + ((window.width()-width())>>1); break;
	case GLT_ALIGN_RIGHT:   x() = window.x() + window.width()-width();        break;
	}

	return valid();
}

bool GltViewport::align(const GltVerticalAlignment &align,const GltViewport &window)
{
	switch (align)
	{
	case GLT_ALIGN_TOP:     y() = window.y() + window.height()-height();        break;
	case GLT_ALIGN_VCENTER: y() = window.y() + ((window.height()-height())>>1); break;
	case GLT_ALIGN_BOTTOM:  y() = window.y();                                   break;
	}

	return valid();
}

bool GltViewport::shrink(const GLint w)
{
	x() += w;
	y() += w;

	width()  -= w<<1;
	height() -= w<<1;

	return true;
}

//

void GltViewport::drawQuad() const
{
	const GLint x = width();
	const GLint y = height();

	glBegin(GL_QUADS);
	glVertex2i(0,0);
	glVertex2i(x,0);
	glVertex2i(x,y);
	glVertex2i(0,y);
	glEnd();
}

void GltViewport::drawLines() const
{
	const GLint x = width()-1;
	const GLint y = height()-1;

	glBegin(GL_LINE_LOOP);
	glVertex2i(0,0);
	glVertex2i(x,0);
	glVertex2i(x,y);
	glVertex2i(0,y);
	glEnd();
}



