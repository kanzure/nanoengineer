#ifndef GLT_MATERIAL_H
#define GLT_MATERIAL_H

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
    \brief OpenGL Material Class
    \ingroup GLT
    
    $Id: material.h,v 1.13 2002/10/07 16:33:35 nigels Exp $
    
    $Log: material.h,v $
    Revision 1.13  2002/10/07 16:33:35  nigels
    Added CVS info

    
*/

#include "glt_gl.h"
#include "glt_color.h"

#include <iosfwd>

/*! \class GltMaterial
    \brief OpenGL Material Class
    \ingroup GLT

    OpenGL material settings object
*/

class GltMaterial
{
public:
	
	/// Constructor
	GltMaterial(const GLenum face = GL_FRONT_AND_BACK,const bool getIt = false);

	/// Full constructor
	GltMaterial
	(
		const GltColor &ambient,
		const GltColor &diffuse,
		const GltColor &specular,
		const GltColor &emission,
		const GLfloat   shininess,
		const GLenum face  = GL_FRONT_AND_BACK
	);

	/// Construct by name
	GltMaterial(const std::string &name,const GLenum face  = GL_FRONT_AND_BACK);

	/// Destructor
	~GltMaterial();

	//

								/// Get the current OpenGL material settings
	void get();
								/// Set the current OpenGL material settings
	void set() const;

	//

										// Front and/or back face
	GLenum   &face();
										// Ambient color
	GltColor &ambient();
										// Diffuse color
	GltColor &diffuse();
										// Specular color
	GltColor &specular();
										// Emissive color
	GltColor &emission();
										// Shininess coefficient
	GLfloat  &shininess();
										// Color Index
	GLint    *colorIndex();

										// Front and/or back face
	const GLenum   &face()       const;
										// Ambient color
	const GltColor &ambient()    const;
										// Diffuse color
	const GltColor &diffuse()    const;
										// Specular color
	const GltColor &specular()   const;
										// Emissive color
	const GltColor &emission()   const;
										// Shininess coefficient
	const GLfloat  &shininess()  const;
										// Color Index
	const GLint    *colorIndex() const;

private:

	GLenum  _face;

	GltColor _ambient;
	GltColor _diffuse;
	GltColor _specular;
	GltColor _emission;
	GLfloat _shininess;

	GLint   _colorIndex[4];

	//

	static const int          _matSize;
	static const char        *_matName [];
	static const GltMaterial *_matValue[];
};

//

extern const GltMaterial blackPlasticMaterial;
extern const GltMaterial blackRubberMaterial;
extern const GltMaterial brassMaterial;
extern const GltMaterial bronzeMaterial;
extern const GltMaterial chromeMaterial;
extern const GltMaterial copperMaterial;
extern const GltMaterial emeraldMaterial;
extern const GltMaterial goldMaterial;
extern const GltMaterial jadeMaterial;
extern const GltMaterial obsidianMaterial;
extern const GltMaterial pearlMaterial;
extern const GltMaterial pewterMaterial;
extern const GltMaterial polishedBronzeMaterial;
extern const GltMaterial polishedCopperMaterial;
extern const GltMaterial polishedGoldMaterial;
extern const GltMaterial polishedSilverMaterial;
extern const GltMaterial rubyMaterial;
extern const GltMaterial silverMaterial;
extern const GltMaterial turquoiseMaterial;
extern const GltMaterial whitePlasticMaterial;

#endif
