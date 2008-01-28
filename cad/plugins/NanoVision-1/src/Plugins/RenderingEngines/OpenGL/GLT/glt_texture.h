#ifndef GLT_TEXTURE_H
#define GLT_TEXTURE_H

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
    \brief OpenGL Texture Class
    \ingroup GLT

    $Id: texture.h,v 1.22 2002/10/07 16:33:35 nigels Exp $

    $Log: texture.h,v $
    Revision 1.22  2002/10/07 16:33:35  nigels
    Added CVS info


*/

#include "glt_config.h"
#include "glt_gl.h"

#include "glt_refcount.h"

#include <iosfwd>
#include <string>

/*! \class   GltTexture
    \brief   OpenGL Texture Class
    \ingroup GLT
*/

class GltTexture;
typedef ReferenceCountPtr<GltTexture> GltTexturePtr;

class GltTexture
{
public:
	
	//
	// Constructor/Destructor
	//

	/// Constructor
	GltTexture(const GLenum target = GL_TEXTURE_2D);
	/// Destructor
	~GltTexture();


	//
	// Textures can't be copied
	//

private:

	/// Copy constructor is private to prevent copying
	GltTexture(const GltTexture &);
	/// Assignment operator is private to prevent copying
	GltTexture &operator=(const GltTexture &);

public:

	/// Reset texture and release OpenGL resources
	void clear();
#if 0
	/// Initialise from compressed GLT format
	bool init(const void *,const bool mipmap = true);
	/// Initialise from raw string buffer
	bool init(const GLsizei width,const GLsizei height,const std::string &image,const bool mipmap = true);
#endif
    
        /// Initialise from raw memory buffer
	bool init(const GLsizei width,const GLsizei height,const byte *image,const GLsizei channels,const bool mipmap = true);

	/// Set the current OpenGL texture
	void set() const;

	/*!
		\brief		Set wrapping of OpenGL texture coordinates
		\param		s	 Horizontal mapping mode
		\param		t    Vertical mapping mode

		Wrapping mode can be either of 
		<table>
		<tr><td><b>GL_CLAMP    </b></td><td> Clamp coordinate to [0,1].</td></tr>
		<tr><td><b>GL_REPEAT   </b></td><td> Ignore integer part of coordinate.</td></tr>
		</table>
	*/
	void setWrap(const GLenum s,const GLenum t);

	/*!
		\brief		Set filtering of OpenGL texture
		\param		min	 Texture minification function
		\param		mag  Texture magnification  function

		Wrapping mode is one of  
		<table>
		<tr><td><b>GL_NEAREST               </b></td><td>Nearest texel.</td></tr>
		<tr><td><b>GL_LINEAR                </b></td><td>Linearly interpolate.</td></tr>
		<tr><td><b>GL_NEAREST_MIPMAP_NEAREST</b></td><td>Nearest texel in nearest mipmap.</td></tr>
		<tr><td><b>GL_NEAREST_MIPMAP_LINEAR </b></td><td>Linearly interpolate nearest texel from closest two mipmaps.</td></tr>
		<tr><td><b>GL_LINEAR_MIPMAP_NEAREST </b></td><td>Linearly interpolate from nearest mipmap.</td></tr>
		<tr><td><b>GL_LINEAR_MIPMAP_LINEAR  </b></td><td>Linearly interpolate interpolated texel from closest two mipmaps.</td></tr>
		</table>
	*/
	void setFilter(const GLenum min,const GLenum mag);

	/// Gamma adjustment of OpenGL texture 
	void setGamma(const real gamma);

	/// Hue-saturation-value adjustment of OpenGL texture 
	void setHSVAdjust(const real hue,const real saturation,const real value);

	//
	//
	//

	/// Texture width
	const GLsizei &width()  const;

	/// Texture height
	const GLsizei &height() const;

	/// OpenGL texture identifier
	const GLuint   id() const;

	// Serialisation

	/*!
		\brief GLT texture types
		\ingroup GLT
	*/

	typedef enum
	{
		TEXTURE_TYPE_RGB = 0,			/*!< RGB			  */
		TEXTURE_TYPE_RGBA,				/*!< RGBA			  */
		TEXTURE_TYPE_GREY,				/*!< Greyscale		  */
		TEXTURE_TYPE_GREYA,				/*!< Greyscale, Alpha */
		TEXTURE_TYPE_ALPHA,				/*!< Alpha            */
		TEXTURE_TYPE_BITMAP,			/*!< Bitmap           */
		TEXTURE_TYPE_INDEXED_RGB,		/*!< Indexed RGB      */	
		TEXTURE_TYPE_INDEXED_RGBA,		/*!< Indexed RGBA     */

		// Add new types to the end, for compatibility

	} GltTextureType;

	/// Encode GLT Texture header
	static bool  makeHeader(std::string &header,const int type,const int width,const int height,const int alignment,const int compressed);
	/// Extract GLT Texture header
	static void *getHeader(const void * const h,int &type,int &width,int &height,int &alignment,int &compressed);

private:

	GLenum  _target;

	GLint   _components;
	GLsizei _width;
	GLsizei _height;
	GLint   _border;
	GLenum  _format;
	GLenum  _type;
	GLint   _alignment;

	GLenum  _wrapS,_wrapT;
	GLenum  _filterMin,_filterMag;

	real _gamma;
	real _hue,_saturation,_value;

	GLuint  _id;			// OpenGL texture ID
};

#endif
