#ifndef GLT_LIGHT_H
#define GLT_LIGHT_H

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
    \brief OpenGL Light Source Class
    \ingroup GLT

    $Id: light.h,v 1.8 2002/10/07 16:33:35 nigels Exp $

    $Log: light.h,v $
    Revision 1.8  2002/10/07 16:33:35  nigels
    Added CVS info


*/

#include "glt_gl.h"

#include <iosfwd>

#include "glt_vector3.h"
#include "glt_color.h"

/*! \class GltLight
    \brief OpenGL Light Source Class
    \ingroup GLT

    Convenient manipulation of lightsource configuration.
*/

class GltLight
{
public:
	
	/// Constructor
	GltLight(const GLenum light = GL_LIGHT0,const bool getIt = false);
	/// Destructor
	~GltLight();

	/// Get the current OpenGL light settings
	void get();
	/// Set the current OpenGL light settings
	void set() const;

	GLenum   &light();
	bool     &isEnabled();
	GltColor &ambient();
	GltColor &diffuse();
	GltColor &specular();
	Vector   &position();
        bool     &isDirectional();
	Vector   &spotDirection();
	GLfloat  &spotExponent();
	GLfloat  &spotCutoff();
	GLfloat  &attenutationConstant();
	GLfloat  &attenutationLinear();
	GLfloat  &attenutationQuadratic();
        bool     &inEyeSpace();
    
	const GLenum   &light() const;
	const bool     &isEnabled() const;
	const GltColor &ambient() const;
	const GltColor &diffuse() const;
	const GltColor &specular() const;
	const Vector   &position() const;
        const bool     &isDirectional() const;
	const Vector   &spotDirection() const;
	const GLfloat  &spotExponent() const;
	const GLfloat  &spotCutoff() const;
	const GLfloat  &attenutationConstant() const;
	const GLfloat  &attenutationLinear() const;
	const GLfloat  &attenutationQuadratic() const;
        const bool     &inEyeSpace() const;
    
private:

	GLenum  _light;
	bool    _isEnabled;

	GltColor _ambient;
	GltColor _diffuse;
	GltColor _specular;
	Vector   _position;
        bool     _isDirectional;
	Vector   _spotDirection;
	GLfloat  _spotExponent;
	GLfloat  _spotCutoff;
	GLfloat  _attenuationConstant;
	GLfloat  _attenuationLinear;
	GLfloat  _attenuationQuadratic;
        bool     _inEyeSpace;

	const static GltColor _ambientDefault;
	const static GltColor _diffuseDefault;
	const static GltColor _specularDefault;
	const static Vector   _positionDefault;
	const static Vector   _spotDirectionDefault;
	const static GLfloat  _spotExponentDefault;
	const static GLfloat  _spotCutoffDefault;
	const static GLfloat  _attenuationConstantDefault;
	const static GLfloat  _attenuationLinearDefault;
	const static GLfloat  _attenuationQuadraticDefault;
};

#endif
