
/** \file NXVector.h
 *  \brief Implements point-vector classes using expression templates
 */
#ifndef NX_VECTOR_H
#define NX_VECTOR_H

#include "Nanorex/Utility/NXUtility.h"
#include <cmath>
#include <cstring>
#include <iostream>

namespace Nanorex {


// forward declarations for usable types
template<typename T, int N> class NXVectorRef;
template<typename T, int N> class NXVector;

static double const NX_DEFAULTTOL = 1.0e-6;

template<typename T1, typename T2>
	struct promotion_traits;

template<typename T> struct promotion_traits<T,T> { typedef T type; };
template<> struct promotion_traits<float,double> { typedef double type; };
template<> struct promotion_traits<double,float> { typedef double type; };
template<> struct promotion_traits<double,long double> { typedef long double type; };
template<> struct promotion_traits<long double,double> { typedef long double type; };
template<> struct promotion_traits<float,long double> { typedef long double type; };
template<> struct promotion_traits<long double,float> { typedef long double type; };


/* CLASS: NXVectorBase */
template <typename T, int N, template <typename,int> class NXVectorDerived>
	class NXVectorBase {
	public:
		typedef T value_type;
		typedef NXVectorBase<T,N,NXVectorDerived> baseclass_type;
		typedef NXVectorDerived<T,N> subclass_type;
		
	private:
		typedef NXVectorBase<T,N,NXVectorDerived> self_type;
		
		
	public:
		NXVectorBase() {}
		~NXVectorBase() {}
		
		// shallow or deep copy as per the implementation
		template<template <typename, int> class NXVectorDerived2>
			self_type&
			operator = (NXVectorBase<T,N,NXVectorDerived2> const& v) throw()
		{
			asLeaf() = v.asLeaf();
			return *this;
		}
		
		// force deep copy between identical value_types
		template<template <typename, int> class NXVectorDerived2>
			self_type& copy(NXVectorBase<T,N,NXVectorDerived2> const& v) throw()
		{
			NXVectorBase<T,N,NXVectorDerived2>& v_non_const =
				const_cast<NXVectorBase<T,N,NXVectorDerived2>&>(v);
			memcpy((void*) data(),
			       (void*) v_non_const.data(),
			       N * sizeof(T));
			return *this;
		}
		
		// force deep copy between static_cast-able value_types
		template<typename T1, template <typename, int> class NXVectorDerived2>
			self_type& copy(NXVectorBase<T1,N,NXVectorDerived2> const& v) throw()
		{
			for(int n=0; n<N; ++n)
				data()[n] = static_cast<T const>(v.data()[n]);
			return *this;
		}
		
		subclass_type& asLeaf(void) throw() {
			return static_cast<subclass_type&>(*this);
		}
		
		subclass_type const& asLeaf(void) const throw() {
			return static_cast<subclass_type const&>(*this);
		}
		
		// derived classes must implement the data array m_coords
		T *const data(void) throw() { return asLeaf().data(); }
		T const *const data(void) const throw() { return asLeaf().data(); }
		
		T const& operator [] (int const& n) const throw() { return data()[n]; }
		T& operator [] (int const& n) throw() { return data()[n]; }
		
		int size(void) const throw() { return N; }
		
		self_type& zero(void) throw();
		
		/// Unary minus
		NXVector<T,N> operator - (void) const throw();
		
		/// self-increment
		template<typename T1, template <typename, int> class NXVectorDerived2>
			self_type& operator += (NXVectorBase<T1,N,NXVectorDerived2> const& b)
			throw();
		
		/// self-decrement
		template<typename T1, template <typename, int> class NXVectorDerived2>
			self_type& operator -= (NXVectorBase<T1,N,NXVectorDerived2> const& b)
			throw();
		
		/// self-scaling
		template<typename T1>
			self_type& operator *= (T1 const& c) throw();
		
		/// self-scaling
		template<typename T1>
			self_type& operator /= (T1 const& c) throw();
		
		self_type& normalizeSelf(double const& TOL=NX_DEFAULTTOL) throw();
		
		/// normalized copy of self
		NXVector<T,N> normalized(double const& TOL=NX_DEFAULTTOL) const throw();
		
	protected:
		static inline T s_sqr(T const& x) throw() { return x*x; }
		static inline T s_div(T const& a, T const& b) throw()
		{ return static_cast<T>(static_cast<double>(a)/static_cast<double>(b)); }
		
	};


/* CLASS: NXVectorRef */
/**
 * N-dimensional vector view of an array with shallow copy semantics
 */
template<typename T, int N>
	class NXVectorRef : public NXVectorBase<T,N,NXVectorRef> {
	public:
		
		NXVectorRef() : m_coords(NULL) {}
		NXVectorRef(T *const v) : m_coords(v) {}
		NXVectorRef(NXVector<T,N>& v) : m_coords(v.data()) {}
		
		// shallow copy constructor
		template<template <typename, int> class NXVectorDerived>
			NXVectorRef<T,N>& operator = (NXVectorBase<T,N,NXVectorDerived>& v) {
				m_coords = v.data();
				return *this;
			}
		~NXVectorRef() {}
		
		T *const data(void) throw() { return m_coords; }
		T const *const data(void) const throw() { return m_coords; }
	
	protected:
		T *m_coords;
	};

// typedefs for common instantiations
typedef NXVectorRef<float, 2> NXVectorRef2f;
typedef NXVectorRef<double,2> NXVectorRef2d;
typedef NXVectorRef<float, 3> NXVectorRef3f;
typedef NXVectorRef<double,3> NXVectorRef3d;
typedef NXVectorRef<float, 4> NXVectorRef4f;
typedef NXVectorRef<double,4> NXVectorRef4d;


// -----------------------------------------------------------------------------
/* CLASS: NXVector */
/**
 * N-dimensional point
 * Allocates private data store and inherits functionality from NXVectorBase
 */
template<typename T, int N>
	class NXVector : public NXVectorBase<T,N,NXVector> {
	public:
		NXVector() throw () {}
		NXVector(T const& x) throw (NXException);
		NXVector(T const& y, T const& y) throw (NXException);
		NXVector(T const& x, T const& y, T const& z) throw (NXException);
		NXVector(T const v[]) throw (); ///< initialize from array
		
		// copy assignment with deep copy semantics
		template<typename T1, template <typename, int> class NXVectorDerived>
			NXVector<T,N>&
			operator = (NXVectorBase<T1,N,NXVectorDerived> const& v) throw();
		
		// copy constructor with deep copy semantics
		template<typename T1, template <typename, int> class NXVectorDerived>
			NXVector(NXVectorBase<T1,N,NXVectorDerived> const& v) throw ();
		
		~NXVector() {}
		
		T *const data(void) throw() { return m_coords; }
		T const *const data(void) const throw() { return m_coords; }
		
	private:
		T m_coords[N];
	};

// typedefs for common instantiations
typedef NXVector<float, 2> NXVector2f;
typedef NXVector<double,2> NXVector2d;
typedef NXVector<float, 3> NXVector3f;
typedef NXVector<double,3> NXVector3d;
typedef NXVector<float, 4> NXVector4f;
typedef NXVector<double,4> NXVector4d;


/* CONSTRUCTOR */
template<typename T, int N>
	inline
	NXVector<T,N>::NXVector(T const& x) throw (NXException)
	: NXVector<T,N>::baseclass_type()
	// : NXVectorRef<T,N>(m_coord_data)
{
	if(N != 1)
		throw NXException("Initialization with different dimensionality");
	m_coords[0] = x;
}

/* CONSTRUCTOR */
template<typename T, int N>
	inline
	NXVector<T,N>::NXVector(T const& x, T const& y) throw (NXException)
	: NXVector<T,N>::baseclass_type()
	// : NXVectorRef<T,N>(m_coord_data)
{
	if(N != 2)
		throw NXException("Initialization with different dimensionality");
	m_coords[0] = x;
	m_coords[1] = y;
}

/* CONSTRUCTOR */
template<typename T, int N>
	inline
	NXVector<T,N>::NXVector(T const& x, T const& y, T const& z) throw (NXException)
	: NXVector<T,N>::baseclass_type()
	// : NXVectorRef<T,N>(m_coord_data)
{
	if(N != 3)
		throw NXException("Initialization with different dimensionality");
	m_coords[0] = x;
	m_coords[1] = y;
	m_coords[2] = z;
}

/* CONSTRUCTOR */
template<typename T, int N>
	inline
	NXVector<T,N>::NXVector(T const v[]) throw ()
	: NXVector<T,N>::baseclass_type()
	// : NXVectorRef<T,N>(m_coord_data)
{
	// for(int n=0; n<N; ++n) m_coords[n] = v[n];
	std::memcpy((void*) m_coords,
	            (void*) const_cast<T*>(v),
	            N * sizeof(T));
}

/* COPY-ASSIGNMENT */
/// Deep copy semantics
template<typename T, int N>
	template<typename T1, template <typename, int> class NXVectorDerived>
	inline
	NXVector<T,N>&
	NXVector<T,N>::operator = (NXVectorBase<T1,N,NXVectorDerived> const& v) throw()
{
	for(int n=0; n<N; ++n) m_coords[n] = static_cast<T const>(v[n]);
	return *this;
}

/* CONSTRUCTOR */
// copy constructor with deep copy semantics
template<typename T, int N>
	template<typename T1, template <typename, int> class NXVectorDerived>
	inline
	NXVector<T,N>::NXVector(NXVectorBase<T1,N,NXVectorDerived> const& v) throw ()
	: NXVector<T,N>::baseclass_type()
{
	(void) (*this = v); // use copy assignment
}


// ------------------------------------------------------------------------
/* Global functions */

template<typename T, template<typename,int> class NXVectorDerived>
	inline
	T dot(NXVectorBase<T,1,NXVectorDerived>& a,
	      NXVectorBase<T,1,NXVectorDerived>& b)
{ 
	return a[0]*b[0];
}

template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	T dot(NXVectorBase<T,N,NXVectorDerived>& a,
	      NXVectorBase<T,N,NXVectorDerived>& b)
{
	NXVectorRef<T,N-1> a1(a.data()), b1(b.data()); 
	T const s = dot(a1, b1);
	T const result = s + a[N-1]*b[N-1];
	return result;
}

template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	T squared_norm(NXVectorBase<T,N,NXVectorDerived>& v) { return dot(v,v); }

template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	T norm(NXVectorBase<T,N,NXVectorDerived>& v)
{
	double const sqr_nrm = static_cast<double>(squared_norm(v));
	double const nrm = sqrt(sqr_nrm);
	return static_cast<T>(nrm);
}

template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	T length(NXVectorBase<T,N,NXVectorDerived>& v)
{
	return norm(v);
}

template<typename T,
	template<typename,int> class NXVectorDerived1,
	template<typename,int> class NXVectorDerived2
	>
	inline
	NXVector<T,3> cross(NXVectorBase<T,3,NXVectorDerived1>& a,
	                    NXVectorBase<T,3,NXVectorDerived2>& b)
{
	NXVector<T,3> c;
	c[0] = a[1] * b[2] - a[2] * b[1];
	c[1] = a[2] * b[0] - a[0] * b[2];
	c[2] = a[0] * b[1] - a[1] * b[0];
	return c;
}

// ------------------------------------------------------------------------
/* NXVectorBase member functions - common operations */

// template<typename T>
// inline
// NXVectorRef<T,1>& NXVectorRef<T,1>::zero(void)
// { m_coords[0] = T(0); return *this; }

template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVectorBase<T,N, NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::zero(void) throw()
{
	for(int n=0; n<N; ++n) data()[n] = T(0);
/*    if(N==1) m_coords[0] = T(0);
    else {
        NXVectorRef<T,N-1>(m_coords).zero();
        m_coords[N-1]=T(0);
    }*/
	return *this;
}

// increment base-case
// template<typename T>
// inline
// NXVectorRef<T,1>& NXVectorRef<T,1>::operator += (NXVectorRef<T,1> const& v)
// { m_coords[0] += v.m_coords[0]; return *this; }

// increment common-case
template<typename T, int N, template<typename,int> class NXVectorDerived>
	template<typename T1, template<typename, int> class NXVectorDerived2>
	inline
	NXVectorBase<T,N,NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::
	operator += (NXVectorBase<T1,N,NXVectorDerived2> const& v)
	throw()
{
	for(int n=0; n<N; ++n) data()[n] += static_cast<T const>(v.data()[n]);
/*    NXVectorRef<T,N-1>(m_coords) += NXVectorRef<T,N-1>(v.m_coords);
    m_coords[N-1] += v.m_coords[N-1];*/
	return *this;
}

// decrement base-case
// template<typename T>
// inline
// NXVectorRef<T,1>& NXVectorRef<T,1>::operator -= (NXVectorRef<T,1> const& v)
// { m_coords[0] -= v.m_coords[0]; return *this; }

// decrement common-case
template<typename T, int N, template<typename,int> class NXVectorDerived>
	template<typename T1, template<typename, int> class NXVectorDerived2>
	inline
	NXVectorBase<T,N,NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::
	operator -= (NXVectorBase<T1,N,NXVectorDerived2> const& v)
	throw()
{
	for(int n=0; n<N; ++n) data()[n] -= static_cast<T const>(v.data()[n]);
/*    NXVectorRef<T,N-1>(m_coords) -= NXVectorRef<T,N-1>(v.m_coords);
    m_coords[N-1] -= v.m_coords[N-1];*/
	return *this;
}

// scaling base-case
// template<typename T>
// inline
// NXVectorRef<T,1>& NXVectorRef<T,1>::operator *= (T const& c)
// {
//     m_coords[0] *= c;
//     return *this;
// }

// scaling common-case
template<typename T, int N, template<typename,int> class NXVectorDerived>
	template<typename T1>
	inline
	NXVectorBase<T,N,NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::operator *= (T1 const& c)  throw()
{
	for(int n=0; n<N; ++n) data()[n] *= static_cast<T const>(c);
/*    NXVectorRef<T,N-1>(m_coords) *= c;
    m_coords[N-1] *= c;*/
	return *this;
}

// scaling base-case
// template<typename T>
// inline
// NXVectorRef<T,1>& NXVectorRef<T,1>::operator /= (T const& c)
// {
//     m_coords[0] /= c;
//     return *this;
// }

// scaling common-case
template<typename T, int N, template<typename,int> class NXVectorDerived>
	template<typename T1>
	inline
	NXVectorBase<T,N,NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::operator /= (T1 const& c)  throw()
{
	for(int n=0; n<N; ++n) data()[n] /= static_cast<T1 const>(c);
/*    NXVectorRef<T,N-1>(m_coords) /= c;
    m_coords[N-1] /= c;*/
	return *this;
}


template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVectorBase<T,N,NXVectorDerived>&
	NXVectorBase<T,N,NXVectorDerived>::normalizeSelf(double const& TOL)  throw()
{
	/// @fixme possible loss of precision through repeated interconversion
	T const len = norm(*this);
	if(double(len) < TOL) zero();
	else this->operator /= (len);
	return *this;
}

/// Return normalized copy without modifying self
template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVector<T,N>
	NXVectorBase<T,N,NXVectorDerived>::normalized(double const& TOL) const throw()
{
	NXVector<T,N> v(data());
	v.normalizeSelf(TOL);
	return v;
}

/// Unary minus
template<typename T, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVector<T,N>
	NXVectorBase<T,N,NXVectorDerived>::operator - (void) const throw()
{
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = -data()[n];
	return result;
}

// Binary operators

/// Addition
template<typename T1, typename T2, int N,
	template<typename,int> class NXVectorDerived1,
	template<typename,int> class NXVectorDerived2
	>
	inline
	NXVector<typename promotion_traits<T1,T2>::type, N>
	operator + (NXVectorBase<T1,N,NXVectorDerived1>& v1,
	            NXVectorBase<T2,N,NXVectorDerived2>& v2)
{
	typedef typename promotion_traits<T1,T2>::type T;
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = v1[n] + v2[n];
	return result;
}


/// Subtraction
template<typename T1, typename T2, int N,
	template<typename,int> class NXVectorDerived1,
	template<typename,int> class NXVectorDerived2
	>
	inline
	NXVector<typename promotion_traits<T1,T2>::type, N>
	operator - (NXVectorBase<T1,N,NXVectorDerived1>& v1,
	            NXVectorBase<T2,N,NXVectorDerived2>& v2)
{
	typedef typename promotion_traits<T1,T2>::type T;
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = v1[n] - v2[n];
	return result;
}


/// Scaling
template<typename T1, typename T2, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVector<typename promotion_traits<T1,T2>::type, N>
	operator * (T1 const& c, NXVectorBase<T2,N,NXVectorDerived>& v)
{
	typedef typename promotion_traits<T1,T2>::type T;
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = static_cast<T>(c) * static_cast<T>(v[n]);
	return result;
}


/// Scaling - post-multiplication by scalar
template<typename T1, typename T2, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVector<typename promotion_traits<T1,T2>::type, N>
	operator * (NXVectorBase<T2,N,NXVectorDerived>& v, T1 const& c)
{
	typedef typename promotion_traits<T1,T2>::type T;
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = static_cast<T>(c) * static_cast<T>(v[n]);
	return result;
}


/// Scaling - division by
template<typename T1, typename T2, int N, template<typename,int> class NXVectorDerived>
	inline
	NXVector<typename promotion_traits<T1,T2>::type, N>
	operator / (NXVectorBase<T2,N,NXVectorDerived>& v, T1 const& c)
{
	typedef typename promotion_traits<T1,T2>::type T;
	NXVector<T,N> result;
	for(int n=0; n<N; ++n)
		result[n] = static_cast<T>(v[n]) / static_cast<T>(c);
	return result;
}


template <typename T, int N, template <typename,int> class NXVectorDerived>
	inline
	std::ostream& operator << (std::ostream& o,
	                           NXVectorBase<T,N,NXVectorDerived> const& v)
{
	o << '(';
	for(int n=0; n<N-1; ++n)
		o << v[n] << ',';
	o << v[N-1] << ')';
	return o;
}

} // Nanorex

#endif // NX_VECTOR_H

