#ifndef MISC_REFCOUNT_H
#define MISC_REFCOUNT_H

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
    \brief   Templated reference-counting pointer
	\ingroup Misc
*/

#include "glt_config.h"

#include <cassert>

/*! \class   ReferenceCountPtr 
    \brief   Templated reference-counting pointer
	\ingroup Misc

	Dynamically allocated objects (created via 'new') that
	are managed via ReferenceCountPtr are automatically 
	destroyed when the last pointer is destroyed.  Therefore,
	a reference-counted object can be shared in different
	places in the system and will not be leaked or a dangling
	(invalid) pointer.

	A count of the number of pointers to the object is
	maintained, and when this count reaches zero, the
	object is destroyed.

	In a way, ReferenceCountPtr is a safer version of
	std::auto_ptr.

*/

template<class T>
class ReferenceCountPtr
{
public:

	/// Default constructor
	ReferenceCountPtr()
	: _obj(NULL), _count(NULL)
	{
	}

	/// Constructor
	ReferenceCountPtr(T *obj)
	: _obj(obj), _count(new int)
	{
		*_count = 0;
		inc();
	}
	
	/// Copy constructor
	ReferenceCountPtr(const ReferenceCountPtr &ptr)
	: _obj(ptr._obj), _count(ptr._count)
	{
		inc();
	}

	/// Destructor
	~ReferenceCountPtr()
	{
		dec();
	}

	/// Assignment operator
	ReferenceCountPtr &operator=(const ReferenceCountPtr &ptr)
	{
		dec();

		_count = ptr._count;
		_obj   = ptr._obj;

		inc();

		return *this;
	}

	/// Reset the pointer
	void clear() { dec(); }
	/// Reset the pointer
	void reset() { dec(); }

	/// Dereference the pointer 
	inline T &operator*()              { assert(_obj); return *_obj; }
	/// Dereference the pointer 
	inline T *operator->()             { assert(_obj); return  _obj; }
	/// Dereference the pointer 
	inline T *get()                    { return _obj; }

	/// Dereference the pointer 
	inline const T &operator*()  const { assert(_obj); return *_obj; }
	/// Dereference the pointer 
	inline const T *operator->() const { assert(_obj); return  _obj; }
	/// Dereference the pointer 	
	inline const T *get()        const { return _obj; }

private:
	T   *_obj;
	int *_count;

	void inc() 
	{ 
		if (_count) 
			(*_count)++; 
	}

	void dec() 
	{
		if (_count)
		{
			(*_count)--;
			if (*_count==0)
			{
				delete _obj;
				delete _count;
			}
		}

		_obj  = NULL;
		_count = NULL;
	}
};

#endif
