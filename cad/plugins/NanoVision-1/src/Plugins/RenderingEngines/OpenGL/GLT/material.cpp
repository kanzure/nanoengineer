#include "glt_material.h"

/*! \file 
    \ingroup GLT
    
    $Id: material.cpp,v 1.10 2002/10/09 15:09:38 nigels Exp $
    
    $Log: material.cpp,v $
    Revision 1.10  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include "glt_error.h"

#include <cassert>
#include <cstring>
#include <iostream>
using namespace std;

GltMaterial::GltMaterial(const GLenum face,const bool getIt)
: _face(face)
{
	assert(_face==GL_FRONT_AND_BACK || _face==GL_FRONT || _face==GL_BACK);

	// TODO - OpenGL Defaults
	
	_shininess = 0.0;
	memset(_colorIndex,0,sizeof(_colorIndex));

	if (getIt)
		get();
}

GltMaterial::GltMaterial
(
	const GltColor &ambient,
	const GltColor &diffuse,
	const GltColor &specular,
	const GltColor &emission,
	const GLfloat   shininess,
	const GLenum face
)
: 
	_face(face),
	_ambient(ambient),
	_diffuse(diffuse),
	_specular(specular),
	_emission(emission),
	_shininess(shininess)
{
	assert(_face==GL_FRONT_AND_BACK || _face==GL_FRONT || _face==GL_BACK);

	memset(_colorIndex,0,sizeof(_colorIndex));
}

GltMaterial::GltMaterial(const std::string &name,const GLenum face)
: _face(face)
{
	assert(_face==GL_FRONT_AND_BACK || _face==GL_FRONT || _face==GL_BACK);

	// Do a binary search through the list of names

	int i=0;
	int j=_matSize;

	for (;;)
	{
		int k = ((j-i)>>1)+i;
		const int res = strcmp(name.c_str(),_matName[k]);

		if (res<0)
			j = k;
		else
			if (res>0)
				i = k+1;
			else
			{
				operator=(*_matValue[k]);
				return;
			}

		if (i==k && j==k || i==_matSize)
		{
			assert(!"Material not found");
			operator=(GltMaterial());
			return;
		}
	}
}

GltMaterial::~GltMaterial()
{
}

void 
GltMaterial::get()
{
	// Can't query front and back at same time - beware
	const GLenum face = (_face==GL_FRONT_AND_BACK ? GL_FRONT : _face);

	GLERROR(std::cerr);

	_ambient. glGetMaterial(face,GL_AMBIENT);
	_diffuse. glGetMaterial(face,GL_DIFFUSE);
	_specular.glGetMaterial(face,GL_SPECULAR);
	_emission.glGetMaterial(face,GL_EMISSION);

	glGetMaterialfv(face, GL_SHININESS, &_shininess);

	GLERROR(std::cerr);
}

void 
GltMaterial::set() const
{
	GLERROR(std::cerr);

	_ambient. glMaterial(_face,GL_AMBIENT);
	_diffuse. glMaterial(_face,GL_DIFFUSE);
	_specular.glMaterial(_face,GL_SPECULAR);
	_emission.glMaterial(_face,GL_EMISSION);

	glMaterialfv(_face, GL_SHININESS, &_shininess);

	GLERROR(std::cerr);
}

GLenum   &GltMaterial::face()       { return _face;       }
GltColor &GltMaterial::ambient()    { return _ambient;    }
GltColor &GltMaterial::diffuse()    { return _diffuse;    }
GltColor &GltMaterial::specular()   { return _specular;   }
GltColor &GltMaterial::emission()   { return _emission;   }
GLfloat  &GltMaterial::shininess()  { return _shininess;  }
GLint    *GltMaterial::colorIndex() { return _colorIndex; }

const GLenum   &GltMaterial::face()       const { return _face;       }
const GltColor &GltMaterial::ambient()    const { return _ambient;    }
const GltColor &GltMaterial::diffuse()    const { return _diffuse;    }
const GltColor &GltMaterial::specular()   const { return _specular;   }
const GltColor &GltMaterial::emission()   const { return _emission;   }
const GLfloat  &GltMaterial::shininess()  const { return _shininess;  }
const GLint    *GltMaterial::colorIndex() const { return _colorIndex; }

//
// Adapted from 
//	http://www.cs.utk.edu/~kuck/materials_ogl.htm
//	http://devernay.free.fr/cours/opengl/materials.html
//  http://www.sgi.com/software/opengl/advanced98/notes/node119.html
//  

/// Black Plastic Material

const GltMaterial blackPlasticMaterial
(
	GltColor(0.00, 0.00, 0.00),	// Ambient
	GltColor(0.01, 0.01, 0.01),	// Diffuse
	GltColor(0.50, 0.50, 0.50), // Specular
	GltColor(0.00, 0.00, 0.00),	// Emission
	32.0f						// Shininess
);

/// Black Rubber Material

const GltMaterial blackRubberMaterial
(
	GltColor(0.02, 0.02, 0.02),	// Ambient
	GltColor(0.01, 0.01, 0.01),	// Diffuse
	GltColor(0.40, 0.40, 0.40), // Specular
	GltColor(0.00, 0.00, 0.00),	// Emission
	10.0f						// Shininess
);

/// Brass Material

const GltMaterial brassMaterial
(
	GltColor(0.329412, 0.223529, 0.027451),	// Ambient
	GltColor(0.780392, 0.568627, 0.113725),	// Diffuse
	GltColor(0.992157, 0.941176, 0.807843), // Specular
	GltColor(0.0,0.0,0.0),					// Emission
	27.8974f								// Shininess
);

/// Bronze Material

const GltMaterial bronzeMaterial
(
	GltColor(0.2125  , 0.1275  , 0.054   ),	// Ambient
	GltColor(0.714   , 0.4284  , 0.18144 ),	// Diffuse
	GltColor(0.393548, 0.271906, 0.166721), // Specular
	GltColor(0.0,0.0,0.0),					// Emission
	25.6f									// Shininess
);

/// Chrome Material

const GltMaterial chromeMaterial
(
	GltColor(0.25,     0.25,     0.25    ),	// Ambient
	GltColor(0.4,      0.4,      0.4     ),	// Diffuse
	GltColor(0.774597, 0.774597, 0.774597), // Specular
	GltColor(0.0,0.0,0.0),					// Emission
	76.8f									// Shininess
);

/// Copper Material

const GltMaterial copperMaterial
(
	GltColor(0.19125,  0.0735,   0.0225  ),	// Ambient
	GltColor(0.7038,   0.27048,  0.0828  ),	// Diffuse
	GltColor(0.256777, 0.137622, 0.086014),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	12.8f									// Shininess
);

/// Emerald Material

const GltMaterial emeraldMaterial
(
	GltColor(0.0215,  0.1745,   0.0215 ),	// Ambient
	GltColor(0.07568, 0.61424,  0.07568),	// Diffuse
	GltColor(0.633,   0.727811, 0.633  ),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	76.8f									// Shininess
);

/// Gold Material

const GltMaterial goldMaterial
(
	GltColor(0.24725,  0.1995,   0.0745),	// Ambient
	GltColor(0.75164,  0.60648,  0.22648),	// Diffuse
	GltColor(0.628281, 0.555802, 0.366065),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	51.2f									// Shininess
);

/// Jade Material

const GltMaterial jadeMaterial
(
	GltColor(0.135,    0.2225,   0.1575  ),	// Ambient
	GltColor(0.135,    0.2225,   0.1575  ),	// Diffuse
	GltColor(0.316228, 0.316228, 0.316228),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	12.8f									// Shininess
);

/// Obsidian Material

const GltMaterial obsidianMaterial
(
	GltColor(0.05375,  0.05,     0.06625 ),	// Ambient
	GltColor(0.18275,  0.17,     0.22525 ),	// Diffuse
	GltColor(0.332741, 0.328634, 0.346435),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	38.4f									// Shininess
);

/// Pearl Material

const GltMaterial pearlMaterial
(
	GltColor(0.25,     0.20725,  0.20725 ),	// Ambient
	GltColor(1.0,      0.829,    0.829   ),	// Diffuse
	GltColor(0.296648, 0.296648, 0.296648),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	11.264f									// Shininess
);

/// Pewter Material

const GltMaterial pewterMaterial
(
	GltColor(0.105882, 0.058824, 0.113725),	// Ambient
	GltColor(0.427451, 0.470588, 0.541176),	// Diffuse
	GltColor(0.333333, 0.333333, 0.521569),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	9.84615f								// Shininess
);

/// Polished Bronze Material

const GltMaterial polishedBronzeMaterial
(
	GltColor(0.25    , 0.148   , 0.06475 ),	// Ambient
	GltColor(0.4     , 0.2368  , 0.1036  ),	// Diffuse
	GltColor(0.774597, 0.458561, 0.200621), // Specular
	GltColor(0.0,0.0,0.0),					// Emission
	76.8f									// Shininess
);

/// Polished Copper Material

const GltMaterial polishedCopperMaterial
(
	GltColor(0.2295,   0.08825,  0.0275   ),	// Ambient
	GltColor(0.5508,   0.2118,   0.066    ),	// Diffuse
	GltColor(0.580594, 0.223257, 0.0695701),	// Specular
	GltColor(0.0,0.0,0.0),						// Emission
	51.2f										// Shininess
);

/// Polished Gold Material

const GltMaterial polishedGoldMaterial
(
	GltColor(0.24725,  0.2245,   0.0645  ),	// Ambient
	GltColor(0.34615,  0.3143,   0.0903  ),	// Diffuse
	GltColor(0.797357, 0.723991, 0.208006),	// Specular
	GltColor(0.0,0.0,0.0),					// Emission
	83.2f									// Shininess
);

/// Polished Silver Material

const GltMaterial polishedSilverMaterial
(
	GltColor(0.23125, 0.23125, 0.23125),	// Ambient
	GltColor(0.2775,  0.2775,  0.2775),		// Diffuse
	GltColor(0.773911, 0.773911, 0.773911),	// Specular
	GltColor(0.0,0.0,0.0),					// Emission
	89.6f									// Shininess
);

/// Ruby Material

const GltMaterial rubyMaterial
(
	GltColor(0.1745,   0.01175,  0.01175),	// Ambient
	GltColor(0.61424,  0.04136,  0.04136),	// Diffuse
	GltColor(0.727811, 0.626959, 0.626959),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	76.8f									// Shininess
);

/// Silver Material

const GltMaterial silverMaterial
(
	GltColor(0.19225,  0.19225,  0.19225 ),	// Ambient
	GltColor(0.50754,  0.50754,  0.50754 ),	// Diffuse
	GltColor(0.508273, 0.508273, 0.508273),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	51.2f									// Shininess
);

/// Turquoise Material

const GltMaterial turquoiseMaterial
(
	GltColor(0.1,      0.18725, 0.1745  ),	// Ambient
	GltColor(0.396,    0.74151, 0.69102 ),	// Diffuse
	GltColor(0.297254, 0.30829, 0.306678),	// Specular
	GltColor(0.00,0.00,0.00),				// Emission
	12.8f									// Shininess
);

/// White Plastic Material

const GltMaterial whitePlasticMaterial
(
	GltColor(0.00, 0.00, 0.00),	// Ambient
	GltColor(0.55, 0.55, 0.55),	// Diffuse
	GltColor(0.70, 0.70, 0.70), // Specular
	GltColor(0.00, 0.00, 0.00),	// Emission
	32.0f						// Shininess
);

//

const int   GltMaterial::_matSize = 20;

const char *GltMaterial::_matName[20] =
{
	"blackPlastic",
	"blackRubber",
	"brass",
	"bronze",
	"chrome",
	"copper",
	"emerald",
	"gold",
	"jade",
	"obsidian",
	"pearl",
	"pewter",
	"polishedBronze",
	"polishedCopper",
	"polishedGold",
	"polishedSilver",
	"ruby",
	"silver",
	"turquoise",
	"whitePlastic"
};

const GltMaterial *GltMaterial::_matValue[20] =
{
	&::blackPlasticMaterial,
	&::blackRubberMaterial,
	&::brassMaterial,
	&::bronzeMaterial,
	&::chromeMaterial,
	&::copperMaterial,
	&::emeraldMaterial,
	&::goldMaterial,
	&::jadeMaterial,
	&::obsidianMaterial,
	&::pearlMaterial,
	&::pewterMaterial,
	&::polishedBronzeMaterial,
	&::polishedCopperMaterial,
	&::polishedGoldMaterial,
	&::polishedSilverMaterial,
	&::rubyMaterial,
	&::silverMaterial,
	&::turquoiseMaterial,
	&::whitePlasticMaterial
};
