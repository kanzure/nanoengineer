#include "glt_lightm.h"

/*! \file 
    \ingroup GLT
    
    $Id: lightm.cpp,v 1.5 2002/10/09 15:09:38 nigels Exp $
    
    $Log: lightm.cpp,v $
    Revision 1.5  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include "glt_error.h"

#include <cstring>
using namespace std;

GltLightModel::GltLightModel(const bool getIt)
{
	memset(_ambient,0,sizeof(_ambient));
	_localViewer = false;
	_twoSide = false;

	if (getIt)
		get();
}

GltLightModel::~GltLightModel()
{
}

void 
GltLightModel::get()
{
	GLint localViewer;
	GLint twoSide;

	GLERROR

	glGetFloatv(GL_LIGHT_MODEL_AMBIENT,_ambient);
	glGetIntegerv(GL_LIGHT_MODEL_LOCAL_VIEWER,&localViewer);
	glGetIntegerv(GL_LIGHT_MODEL_TWO_SIDE,&twoSide);

	GLERROR

	_localViewer = localViewer!=0;
	_twoSide     = twoSide!=0;
}

void 
GltLightModel::set()
{
	GLERROR

	glLightModelfv(GL_LIGHT_MODEL_AMBIENT,_ambient);
	glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER,_localViewer ? 1 : 0);
	glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,_twoSide ? 1 : 0);

	GLERROR
}

void 
GltLightModel::setAmbient(const GLfloat r,const GLfloat g,const GLfloat b,const GLfloat a)
{
	GLERROR

	_ambient[0] = r;
	_ambient[1] = g;
	_ambient[2] = b;
	_ambient[3] = a;
	glLightModelfv(GL_LIGHT_MODEL_AMBIENT,_ambient);

	GLERROR
}

void 
GltLightModel::setLocalViewer(const GLboolean localViewer)
{
	GLERROR

	_localViewer = localViewer;
	glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER,_localViewer ? 1 : 0);

	GLERROR
}

void 
GltLightModel::setTwoSide(const GLboolean twoSide)
{
	GLERROR

	_twoSide = twoSide;
	glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,_twoSide ? 1 : 0);

	GLERROR
}

GLfloat   *GltLightModel::ambient()     { return _ambient;       }
GLboolean &GltLightModel::localViewer() { return _localViewer;   }
GLboolean &GltLightModel::twoSide()		{ return _twoSide;       }

