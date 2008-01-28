#ifndef MISC_STRING_H
#define MISC_STRING_H

/*

  GLT OpenGL C++ Toolkit (LGPL)
  Copyright (C) 2000-2002 Nigel Stewart  

  Email: nigels@nigels.com   
  WWW:   http://www.nigels.com/glt/

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
	\brief   string and wstring utility routines 
	\author  Nigel Stewart, RMIT (nigels@nigels.com)
	\ingroup Misc
	\todo    Implement utf8encode
	\note    The std::wstring class is for 16bit unicode text 
*/

#include "glt_config.h"

#ifdef GLT_WIN32
#pragma warning(disable: 4786)		
#endif

#include <string>
#include <vector>
#include <iosfwd>

#ifdef GLT_UNIX
namespace std
{
	typedef basic_string <wchar_t> wstring;
}
#endif

/*! 
	\brief		Test a string for binary bytes
	\ingroup	Misc
*/
bool isBinary(const std::string  &str);

//
// DOS <-> UNIX
//

/*! 
	\brief		Convert text to Unix end-of-line convention
	\ingroup	Misc
*/
void dos2unix(std::string  &dest,const std::string  &src);

/*! 
	\brief		Convert wide text to Unix end-of-line convention
	\ingroup	Misc
*/ 
void dos2unix(std::wstring &dest,const std::wstring &src);

/*! 
	\brief		Convert text to DOS end-of-line convention
	\ingroup	Misc
*/  
void unix2dos(std::string  &dest,const std::string  &src);

/*! 
	\brief		Convert wide text to DOS end-of-line convention
	\ingroup	Misc
*/
void unix2dos(std::wstring &dest,const std::wstring &src);

//
// string <-> stream
//

/*! 
	\brief		Read an input stream into a string, until EOF
	\ingroup	Misc
*/
void readStream (std::istream &is,std::string &dest);

/*! 
	\brief		Write a string to an output stream
	\ingroup	Misc
*/
void writeStream(std::ostream &os,const std::string &src);

/*! 
	\brief		Read an input stream into a wide string, until EOF
	\ingroup	Misc
*/
void readUnicodeStream (std::istream &is,std::wstring &dest);

/*! 
	\brief		Write a wide string to an output stream
	\ingroup	Misc
*/
void writeUnicodeStream(std::ostream &os,const std::wstring &src);

//
// string <-> wstring
//

/*! 
	\brief		Convert a string to a wide string
	\ingroup	Misc
*/
void string2wstring(std::wstring &dest, const std::string  &src);

/*! 
	\brief		Convert a wide string to a string
	\ingroup	Misc
*/
void wstring2string(std::string  &dest, const std::wstring &src);

/*! 
	\brief		Convert a utf8 encoded string to a wide string
	\ingroup	Misc
*/
void utf8decode(std::wstring &dest, const std::string &src);

//
// string -> C/C++ source
// 

/*! 
	\brief		Output a memory buffer as C/C++ source
	\ingroup	Misc
*/
void bin2src(std::ostream &os, const unsigned char *buffer, const int n);

/*! 
	\brief		Output a binary string as C/C++ source
	\ingroup	Misc
*/
void bin2src(std::ostream &os, const std::string &src);

/*! 
	\brief		Encode binary input stream as C/C++ source, until EOF
	\ingroup	Misc
*/
void bin2src(std::ostream &os, std::istream &is);

//
// string -> gcc assembler
//

/*! 
	\brief		Output a memory buffer as gcc assembler
	\ingroup	Misc
*/
void bin2asm(std::ostream &os, const unsigned char *buffer, const int n);

/*! 
	\brief		Output a string as gcc assembler
	\ingroup	Misc
*/
void bin2asm(std::ostream &os, const std::string &src);

/*! 
	\brief		Encode input stream as gcc assembler
	\ingroup	Misc
*/
void bin2asm(std::ostream &os, std::istream &is);

//
// hex conversion
//

/*! 
	\brief		Convert from ASCII character to binary 
	\ingroup	Misc
*/
unsigned int  fromHex4(unsigned char ch);

/*! 
	\brief		Convert from binary to ASCII character
	\ingroup	Misc
*/
unsigned char toHex4(unsigned int val);

//
// string <-> vector<string>
//

/*!
	\brief		Split a string, using a delimiter
	\ingroup	Misc
*/

bool stringSplit(std::vector<std::string> &vec, const std::string &str, const std::string &delim);

/*!
	\brief		Merge a vector of strings, inserting a delimiter
	\ingroup	Misc
*/

bool stringMerge(const std::vector<std::string> &vec, std::string &str, const std::string &delim);

//
// Adaptors for ANSI C functions
//

/*!
	\brief		std::string version of ANSI C atof()
	\ingroup	Misc
*/

double atof(const std::string &str);

/*!
	\brief		std::string version of ANSI C atoi()
	\ingroup	Misc
*/

int    atoi(const std::string &str);

/*!
	\brief		std::string version of ANSI C atol()
	\ingroup	Misc
*/

long   atol(const std::string &str);

/*!
	\brief		std::string to bool, inspired by ANSI C atoi()
	\ingroup	Misc
*/

bool   atob(const std::string &str);

/*!
	\brief		Generalised parsing of containers
	\param		str		string to be parsed
	\param		f			string to element parsing function. atof, atoi etc..
	\param		match		characters the form an element. "+-eE.0123456789"
	\param		begin		iterator to first container element
	\param		end		iterator to last+1 container element
	\ingroup	Misc
*/

template<class T,class I>
const int atoc(const std::string &str,T (*f)(const std::string &),const std::string &match,const I &begin,const I &end)
{
	int    n = 0;
	I      i = begin;
	size_t j = 0;

	while (i!=end)
	{
		j = str.find_first_of(match,j);
		if (j==std::string::npos)
			break;

		*i = f(str.substr(j));
		
		n++;
		i++;

		j = str.find_first_not_of(match,j);
		if (j==std::string::npos)
			break;
	}

	for (;i!=end;i++)
		*i = T();

	return n;
}

#endif
