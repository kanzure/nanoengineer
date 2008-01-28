#include "glt_texture.h"

/*! \file 
    \ingroup GLT
    
    $Id: texture.cpp,v 1.26 2002/10/09 15:09:38 nigels Exp $
    
    $Log: texture.cpp,v $
    Revision 1.26  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

#include "glt_gl.h"
#include "glt_glu.h"
#include "glt_error.h"

//#include "glt_compress.h"
//#include "glt_image.h"

#if !defined(NDEBUG)
#include <iostream>
#endif

#include <cassert>
#include <cstdio>
#include <string>
using namespace std;

//////////////////////////////////////////////////////////////////////////

GltTexture::GltTexture(const GLenum target)
:
	_target(target),
	_components(0),
	_width(0),
	_height(0),
	_border(0),
	_format(0),
	_type(0),
	_alignment(0),
	_wrapS(GL_REPEAT),
	_wrapT(GL_REPEAT),
	_filterMin(GL_LINEAR),
	_filterMag(GL_LINEAR),
	_gamma(1.0),
	_hue(0.0),
	_saturation(0.0),
	_value(0.0),

	_id(0)
{
}

GltTexture::GltTexture(const GltTexture &)
{
	// Can't copy textures
	assert(0);
}

GltTexture::~GltTexture()
{
	#if !defined(NDEBUG)
	if (_id)
		cerr << "WARNING: Potential OpenGL texture leak (" << this << ")" << endl;
	#endif

	clear();
}

GltTexture &
GltTexture::operator=(const GltTexture &)
{
	// Can't copy textures
	assert(0);
	return *this;
}

void 
GltTexture::setWrap(const GLenum s,const GLenum t)
{
	_wrapS = s;
	_wrapT = t;

	if (_id!=0)
	{
		glPushAttrib(GL_TEXTURE_BIT);
			glBindTexture(_target,_id);
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,_wrapS);
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,_wrapT);
		glPopAttrib();
	}
}

void 
GltTexture::setFilter(const GLenum min,const GLenum mag)
{
	_filterMin = min;
	_filterMag = mag;

	if (_id!=0)
	{
		glPushAttrib(GL_TEXTURE_BIT);
			glBindTexture(_target,_id);
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,_filterMin);
			glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,_filterMag); 
		glPopAttrib();
	}
}

void 
GltTexture::setGamma(const real gamma)
{
	_gamma = gamma;
}

void 
GltTexture::setHSVAdjust(const real hue,const real saturation,const real value)
{
	_hue = hue;
	_saturation = saturation;
	_value = value;
}


#if 0
bool
GltTexture::init(const void *data,const bool mipmap)
{
	GLERROR

	clear();

	if (!data)
		return true;

	// Extract the header

	int type,width,height,alignment,compressed;
	void *pixels = getHeader((const byte *) data,type,width,height,alignment,compressed);
	bool deletePixels = false;

	// If the header is valid, initialise texture

	assert(pixels);

	if (pixels)
	{
		switch (type)
		{
		case TEXTURE_TYPE_RGB:			_components = 3; _format = GL_RGB;             break;	
		case TEXTURE_TYPE_RGBA:			_components = 4; _format = GL_RGBA;            break;	
		case TEXTURE_TYPE_GREY:			_components = 1; _format = GL_LUMINANCE;       break;	
		case TEXTURE_TYPE_GREYA:		_components = 2; _format = GL_LUMINANCE_ALPHA; break;
		case TEXTURE_TYPE_ALPHA:        _components = 1; _format = GL_ALPHA;           break;
		case TEXTURE_TYPE_BITMAP:		_components = 1; _format = TEXTURE_TYPE_BITMAP;break;
		case TEXTURE_TYPE_INDEXED_RGB:  _components = 3; _format = GL_RGB;             break;
		case TEXTURE_TYPE_INDEXED_RGBA: _components = 4; _format = GL_RGBA;            break;
		default: assert(0); break;
		}

		if (compressed)
		{
			string tmp;
			bool ok = decompress(tmp,pixels);

			assert(ok);
			assert(tmp.size());

			if (ok && tmp.size())
			{
				const int n = width*height*_components;
				pixels = new unsigned char[n];
				deletePixels = true;

				if (type==TEXTURE_TYPE_INDEXED_RGB)
				{
					string rgb;
					indexed2rgb(rgb,tmp);

					if (_gamma!=1.0)
						adjustGamma(rgb,_gamma);
					
					if (_hue!=0.0 || _saturation!=0.0 || _value!=0.0)
						adjustHSV(rgb,width,height,_hue,_saturation,_value);

					memcpy(pixels,rgb.c_str(),n);

					/* TODO - Deal with indexed data */
				}
				else
				{
					if (_gamma!=1.0)
						adjustGamma(tmp,_gamma);
					
					if (_hue!=0.0 || _saturation!=0.0 || _value!=0.0)
						adjustHSV(tmp,width,height,_hue,_saturation,_value);

					memcpy(pixels,tmp.c_str(),n);
				}
			}
		}

		/* TODO - Deal with uncompressed indexed data */

		_width = width;
		_height = height;

		_type = GL_UNSIGNED_BYTE;
	}

	assert(_components!=0);

	if (pixels && _components!=0)
	{	
		GLERROR

		if (_target==GL_TEXTURE_2D)
		{
			glGenTextures(1,&_id);
			glBindTexture(GL_TEXTURE_2D,_id);
			glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE);
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,_filterMin);
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,_filterMag); 
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, _wrapS);
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, _wrapT);
		}

		if (mipmap)
			gluBuild2DMipmaps(_target,_components,_width,_height,_format,_type,pixels);
		else
			glTexImage2D(_target,0,_components,_width,_height,_border,_format,_type,pixels);

		if (deletePixels)
			delete [] (unsigned char *) pixels;

		GLERROR

		return true;
	}

	GLERROR

	return false;
}

bool 
GltTexture::init(const GLsizei width,const GLsizei height,const std::string &image,const bool mipmap)
{
	clear();

	GLenum mode = 0;
	int    channels = 0;

	if (width*height  == (GLsizei)image.size()) { mode = GL_LUMINANCE;       channels = 1; }
	if (width*height*2== (GLsizei)image.size()) { mode = GL_LUMINANCE_ALPHA; channels = 2; }
	if (width*height*3== (GLsizei)image.size()) { mode = GL_RGB;             channels = 3; }
	if (width*height*4== (GLsizei)image.size()) { mode = GL_RGBA;            channels = 3; }

	if (!mode || !channels)
		return false;

	if (_target==GL_TEXTURE_2D)
	{
		glGenTextures(1,&_id);
		glBindTexture(GL_TEXTURE_2D,_id);
		glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,_filterMin);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,_filterMag); 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, _wrapS);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, _wrapT);
	}

	if (mipmap)
		gluBuild2DMipmaps(_target,channels,width,height,mode,GL_UNSIGNED_BYTE,image.data());
	else
		glTexImage2D(_target,0,channels,width,height,0,mode,GL_UNSIGNED_BYTE,image.data());

	return true;
}

#endif

bool 
GltTexture::init(const GLsizei width,const GLsizei height,const byte *image,const GLsizei channels,const bool mipmap)
{
	clear();

	GLenum mode = 0;

	switch (channels)
	{
		case 1:	mode = GL_LUMINANCE;       break;
		case 2:	mode = GL_LUMINANCE_ALPHA; break;
		case 3:	mode = GL_RGB;             break;
		case 4:	mode = GL_RGBA;            break;
		default: return false;
	}

	if (_target==GL_TEXTURE_2D)
	{
		glGenTextures(1,&_id);
		glBindTexture(GL_TEXTURE_2D,_id);
		glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,_filterMin);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,_filterMag); 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, _wrapS);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, _wrapT);
	}

	if (mipmap)
		gluBuild2DMipmaps(_target,channels,width,height,mode,GL_UNSIGNED_BYTE,image);
	else
		glTexImage2D(_target,0,channels,width,height,0,mode,GL_UNSIGNED_BYTE,image);

	return true;
}

void 
GltTexture::clear()
{
	if (_id)
		glDeleteTextures(1,&_id);

	_id = 0;
	_components = 0;
	_width = 0;
	_height = 0;
	_border = 0;
	_format = 0;
	_type = 0;
	_alignment = 0;
}

void 
GltTexture::set() const
{
	if (_id!=0 && _target==GL_TEXTURE_2D)
		glBindTexture(_target,_id);
}

const GLsizei &GltTexture::width()  const { return _width; }
const GLsizei &GltTexture::height() const { return _height; }
const GLuint   GltTexture::id()     const { return _id; }

////////////////////////////////////////////////////////////////////////////

// Create variable-length header for texture data

bool GltTexture::makeHeader
(
	string &header,
	const int            type,
	const int            width,
	const int            height,
	const int            alignment,
	const int            compressed
)
{
	// 11 characters is big enough for integer 2^32 + \0

	char buffer[5+11+11+11+11+11];
	sprintf(buffer,"GLTT %u %u %u %u %u",type,width,height,alignment,compressed);
	header = buffer;
	header += '\0';

	return true;
}

// Decode variable-length header for texture data

void *GltTexture::getHeader
(
	const void * const data,
	int            &type,
	int            &width,
	int            &height,
	int            &alignment,
	int            &compressed
)
{
	const char * const h = (const char * const) data;
	
	if (h[0]=='G' && h[1]=='L' && h[2]=='T' && h[3]=='T' && h[4]==' ')
	{
		if (sscanf(h+5,"%i %i %i %i %i",&type,&width,&height,&alignment,&compressed)==5)
			return (void *) (h + strlen(h) + 1);
	}

	return NULL;
}

