/*
  Name: container.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for container representation 
*/

#if !defined(CONTAINER_INCLUDED)
#define CONTAINER_INCLUDED

#include <assert.h>
#include <stdio.h>

template<
	class T >

class Container
{

  public:

	//------------------------------------------------------------------------
	// Constructor

	inline Container();

	//------------------------------------------------------------------------
	// Constructor

	inline Container(
		int n);

	//------------------------------------------------------------------------
	// Destructor

	inline ~Container();

	//------------------------------------------------------------------------
	// Add()
	//
	// add entity in the container
	//
	inline int Add(
		const T & pEntity);

	//------------------------------------------------------------------------
	// Allocate()
	//
	// allocate memory
	//
	inline void Allocate(
		int n);

	//------------------------------------------------------------------------
	// DeleteLast()
	//
	// delete last entity
	//
	inline void DeleteLast();

	//------------------------------------------------------------------------
	// Empty()
	//
	// clear the container
	//
	inline void Empty();

	//------------------------------------------------------------------------
	// GetPtr()
	//
	// return pointer to first entity
	//
	inline T * GetPtr() const;

	//------------------------------------------------------------------------
	// operator []()
	//
	// access to entities
	//
	inline T & operator [](
		int i) const;

	//------------------------------------------------------------------------
	// operator []()
	//
	// access to entities
	//
	inline T & operator [](
		int i);

	//------------------------------------------------------------------------
	// Read()
	//
	// read array from the file
	//
	void Read(
		FILE * f);

	//------------------------------------------------------------------------
	// Size()
	//
	// size of container
	//
	inline int Size() const;

	//------------------------------------------------------------------------
	// Write()
	//
	// write array to the file
	//
	void Write(
		FILE * f);

  private:

	//------------------------------------------------------------------------
	// mData

	T * mData;							// list of entities

	//------------------------------------------------------------------------
	// mNumber

	int mNumber;						// maximum possible number of entities

	//------------------------------------------------------------------------
	// mCurrent

	int mCurrent;						// current number of entities

	//------------------------------------------------------------------------
	// Resize()
	//
	// resize the container
	//
	void Resize();
};

//----------------------------------------------------------------------------
// Constructor

template<
	class T >

inline Container<T>::Container():

	// Private data initialization
	mData(								// list of entities
		0),
	mNumber(							// maximum possible number of entities
		0),
	mCurrent(							// current number of entities
		0)
{

}

//----------------------------------------------------------------------------
// Constructor

template<
	class T >

inline Container<T>::Container(
	int n):

	// Private data initialization
	mData(								// list of entities
		0)
{
	Allocate(n);
}

//----------------------------------------------------------------------------
// Destructor

template<
	class T >

inline Container<T>::~Container()
{
	Empty();
}

//----------------------------------------------------------------------------
// Add()

template<
	class T >

inline int Container<T>::Add(
	const T & pEntity)
{
	if (mCurrent == mNumber) Resize();
	mData[mCurrent] = pEntity;
	return (mCurrent++);
}

//----------------------------------------------------------------------------
// Allocate()

template<
	class T >

inline void Container<T>::Allocate(
	int n)
{
	if (mData) Empty();
	mNumber = n;
	mCurrent = n;
	mData = new T[mNumber];
#ifdef FIELD_BOUNDS_CHECK
	    assert(mData);
#endif
}

//----------------------------------------------------------------------------
// DeleteLast()

template<
	class T >

inline void Container<T>::DeleteLast()
{
	if (mCurrent) mCurrent--;
}

//----------------------------------------------------------------------------
// Empty()

template<
	class T >

inline void Container<T>::Empty()
{
	if (mData) delete [] mData;
	mData = 0;
	mNumber = 0;
	mCurrent = 0;
}

//----------------------------------------------------------------------------
// GetPtr()

template<
	class T >

inline T * Container<T>::GetPtr() const
{
	return (mData);
}

//----------------------------------------------------------------------------
// operator []()

template<
	class T >

inline T & Container<T>::operator [](
	int i) const
{
	return (mData[i]);
}

//----------------------------------------------------------------------------
// operator []()

template<
	class T >

inline T & Container<T>::operator [](
	int i)
{
	return (mData[i]);
}

//----------------------------------------------------------------------------
// Read()

template<
	class T >

void Container<T>::Read(
	FILE * f)
{
	int i;
	int s[1];
	T ar[1];
	Empty();
	fread (s,sizeof(int),1,f);
	for (i=0; i<s[0]; i++)
	{
		fread (ar,sizeof(T),1,f);
		Add(ar[0]);
	}
}

//----------------------------------------------------------------------------
// Resize()

template<
	class T >

void Container<T>::Resize()
{
	mNumber = mNumber ? (mNumber<<1) : 1;
	T * new_data = new T[mNumber];
#ifdef FIELD_BOUNDS_CHECK
	    assert(new_data);
#endif
	if (mCurrent)
	{
		for (int i=0; i<mCurrent; i++)
		{
			new_data[i] = mData[i];
		}
	}
	if (mData) delete [] mData;
	mData = new_data;
}

//----------------------------------------------------------------------------
// Size()

template<
	class T >

inline int Container<T>::Size() const
{
	return (mCurrent);
}

//----------------------------------------------------------------------------
// Write()

template<
	class T >

void Container<T>::Write(
	FILE * f)
{
	int i;
	int s[1];
	T ar[1];
	s[0] = Size();
	fwrite (s,sizeof(int),1,f);
	for (i=0; i<Size(); i++)
	{
		ar[0] = mData[i];
		fwrite (ar,sizeof(T),1,f);
	}
}
#endif  								// CONTAINER_INCLUDED

