
/** \file NXPoint.h
 *  \brief Implements point-vector classes using expression templates
 */
#ifndef NX_POINT_H
#define NX_POINT_H

#include <cmath>
#include "Nanorex/Utility/NXUtility.h"

namespace Nanorex {


template<typename T, int N> class NXPointRef;

template<typename T, int N> class NXPoint;

static double const NX_DEFAULTTOL = 1.0e-6;

/* CLASS: NXPointRef */
/**
 * N-dimensional vector view of an array
 */
template<typename T, int N>
class NXPointRef {
public:
    
    typedef T value_type;
    
    NXPointRef() : m_coords(NULL) {}
    NXPointRef(T *const v) : m_coords(v) {}
    ~NXPointRef() {}
    
    T const& operator [] (int const& n) const { return m_coords[n]; }
    T& operator [] (int const& n) { return m_coords[n]; }

    T *const data(void) { return m_coords; }
    T const *const data(void) const { return m_coords; }
    
    int size(void) const { return N; }
    
    NXPointRef<T,N>& zero(void);
    
    NXPointRef<T,N>& operator += (NXPointRef<T,N> const& b);
    
    NXPointRef<T,N>& operator -= (NXPointRef<T,N> const& b);
    
    NXPointRef<T,N>& operator *= (T const& c);
    
    NXPointRef<T,N>& operator /= (T const& c);
    
    NXPointRef<T,N>& normalizeSelf(double const& TOL=NX_DEFAULTTOL);
    
    NXPoint<T,N> normalized(double const& TOL=NX_DEFAULTTOL) const;
    
protected:
    T *m_coords;
    static inline T s_sqr(T const& x) { return x*x; }
    static inline T s_div(T const& a, T const& b)
    { return (static_cast<double>(a)/static_cast<double>(b)); }
    
};

// typedefs for common instantiations
typedef NXPointRef<float, 2> NXPointRef2f;
typedef NXPointRef<double,2> NXPointRef2d;
typedef NXPointRef<float, 3> NXPointRef3f;
typedef NXPointRef<double,3> NXPointRef3d;
typedef NXPointRef<float, 4> NXPointRef4f;
typedef NXPointRef<double,4> NXPointRef4d;


// ------------------------------------------------------------------------
/* CLASS: NXPoint */
/**
 * N-dimensional point
 * Allocates private data store and uses NXPointRef to refer to it, inheriting
 * the latter's functionality
 */
template<typename T, int N>
class NXPoint : public NXPointRef<T,N> {
public:
    NXPoint() throw () : NXPointRef<T,N>(m_coord_data) {}
    NXPoint(T const& x) throw (NXException);
    NXPoint(T const& y, T const& y) throw (NXException);
    NXPoint(T const& x, T const& y, T const& z) throw (NXException);
    NXPoint(T *const v) throw (); ///< initialize from array
    NXPoint(NXPointRef<T,N> const& v) throw (); ///< deep-copy semantics
	~NXPoint() {}

    /// Override inerhited shallow-copy with deep-copy semantics
    NXPoint<T,N>& operator = (NXPointRef<T,N> const& v);

private:
    T m_coord_data[N];
};

// typedefs for common instantiations
typedef NXPoint<float, 2> NXPoint2f;
typedef NXPoint<double,2> NXPoint2d;
typedef NXPoint<float, 3> NXPoint3f;
typedef NXPoint<double,3> NXPoint3d;
typedef NXPoint<float, 4> NXPoint4f;
typedef NXPoint<double,4> NXPoint4d;


/* CONSTRUCTOR */
template<typename T, int N>
    inline
    NXPoint<T,N>::NXPoint(T const& x) throw (NXException)
    : NXPointRef<T,N>(m_coord_data)
{
    if(N != 1)
        throw NXException("Initialization with different dimensionality");
    m_coord_data[0] = x;
}

/* CONSTRUCTOR */
template<typename T, int N>
    inline
    NXPoint<T,N>::NXPoint(T const& x, T const& y) throw (NXException)
    : NXPointRef<T,N>(m_coord_data)
{
    if(N != 2)
        throw NXException("Initialization with different dimensionality");
    m_coord_data[0] = x;
    m_coord_data[1] = y;
}

/* CONSTRUCTOR */
template<typename T, int N>
    inline
    NXPoint<T,N>::NXPoint(T const& x, T const& y, T const& z) throw (NXException)
    : NXPointRef<T,N>(m_coord_data)
{
    if(N != 3)
        throw NXException("Initialization with different dimensionality");
    m_coord_data[0] = x;
    m_coord_data[1] = y;
    m_coord_data[2] = z;
}

/* CONSTRUCTOR */
template<typename T, int N>
    inline
    NXPoint<T,N>::NXPoint(T *const v) throw ()
    : NXPointRef<T,N>(m_coord_data)
{
    for(int n=0; n<N; ++n) m_coord_data[n] = v[n];
}

/* CONSTRUCTOR */
template<typename T, int N>
    NXPoint<T,N>::NXPoint(NXPointRef<T,N> const& v) throw ()
    : NXPointRef<T,N>(m_coord_data)
{
    for(int n=0; n<N; ++n) m_coord_data[n] = v[n];
}

/* COPY-ASSIGNMENT */
template<typename T, int N>
inline
NXPoint<T,N>& NXPoint<T,N>::operator = (NXPointRef<T,N> const& v)
{
    for(int n=0; n<N; ++n) m_coord_data[n] = v[n];
    return *this;
}


// ------------------------------------------------------------------------
/* Global functions */

template<typename T>
T dot(NXPointRef<T,1>& a, NXPointRef<T,1>& b){ return a[0]*b[0]; }

template<typename T, int N>
T dot(NXPointRef<T,N>& a, NXPointRef<T,N>& b)
{
    NXPointRef<T,N-1> a1(a.data()), b1(b.data()); 
    T const s = dot(a1, b1);
    T const result = s + a[N-1]*b[N-1];
    return result;
}

template<typename T, int N>
T squared_norm(NXPointRef<T,N>& v) { return dot(v,v); }

template<typename T, int N>
T norm(NXPointRef<T,N>& v) { return sqrt(squared_norm(v)); }

template<typename T, int N>
T length(NXPointRef<T,N>& v) { return norm(v); }

template<typename T>
NXPoint<T,3> cross(NXPointRef<T,3>& a, NXPointRef<T,3>& b)
{
    NXPoint<T,3> c;
    c[0] = a[1] * b[2] - a[2] * b[1];
    c[1] = a[2] * b[0] - a[0] * b[2];
    c[2] = a[0] * b[1] - a[1] * b[0];
    return c;
}

// ------------------------------------------------------------------------
/* NXPointRef member functions */

// template<typename T>
// inline
// NXPointRef<T,1>& NXPointRef<T,1>::zero(void)
// { m_coords[0] = T(0); return *this; }

template<typename T, int N>
inline
NXPointRef<T,N>& NXPointRef<T,N>::zero(void)
{
    for(int n=0; n<N; ++n) m_coords[n] = T(0);
/*    if(N==1) m_coords[0] = T(0);
    else {
        NXPointRef<T,N-1>(m_coords).zero();
        m_coords[N-1]=T(0);
    }*/
    return *this;
}

// increment base-case
// template<typename T>
// inline
// NXPointRef<T,1>& NXPointRef<T,1>::operator += (NXPointRef<T,1> const& v)
// { m_coords[0] += v.m_coords[0]; return *this; }

// increment common-case
template<typename T, int N>
inline
NXPointRef<T,N>& NXPointRef<T,N>::operator += (NXPointRef<T,N> const& v)
{
    for(int n=0; n<N; ++n) m_coords[n] += v[n];
/*    NXPointRef<T,N-1>(m_coords) += NXPointRef<T,N-1>(v.m_coords);
    m_coords[N-1] += v.m_coords[N-1];*/
    return *this;
}

// decrement base-case
// template<typename T>
// inline
// NXPointRef<T,1>& NXPointRef<T,1>::operator -= (NXPointRef<T,1> const& v)
// { m_coords[0] -= v.m_coords[0]; return *this; }

// decrement common-case
template<typename T, int N>
NXPointRef<T,N>& NXPointRef<T,N>::operator -= (NXPointRef<T,N> const& v)
{
    for(int n=0; n<N; ++n) m_coords[n] -= v[n];
/*    NXPointRef<T,N-1>(m_coords) -= NXPointRef<T,N-1>(v.m_coords);
    m_coords[N-1] -= v.m_coords[N-1];*/
    return *this;
}

// scaling base-case
// template<typename T>
// inline
// NXPointRef<T,1>& NXPointRef<T,1>::operator *= (T const& c)
// {
//     m_coords[0] *= c;
//     return *this;
// }

// scaling common-case
template<typename T, int N>
inline
NXPointRef<T,N>& NXPointRef<T,N>::operator *= (T const& c)
{
    for(int n=0; n<N; ++n) m_coords[n] *= c;
/*    NXPointRef<T,N-1>(m_coords) *= c;
    m_coords[N-1] *= c;*/
    return *this;
}

// scaling base-case
// template<typename T>
// inline
// NXPointRef<T,1>& NXPointRef<T,1>::operator /= (T const& c)
// {
//     m_coords[0] /= c;
//     return *this;
// }

// scaling common-case
template<typename T, int N>
inline
NXPointRef<T,N>& NXPointRef<T,N>::operator /= (T const& c)
{
    for(int n=0; n<N; ++n) m_coords[n] /= c;
/*    NXPointRef<T,N-1>(m_coords) /= c;
    m_coords[N-1] /= c;*/
    return *this;
}

template<typename T, int N>
inline
NXPointRef<T,N>& NXPointRef<T,N>::normalizeSelf(double const& TOL)
{
    T const len = norm(*this);
    if(double(len) < TOL) zero();
    else this->operator /= (len);
    return *this;
}


template<typename T, int N>
inline
NXPoint<T,N> NXPointRef<T,N>::normalized(double const& TOL) const
{
    NXPoint<T,N> v(m_coords);
    v.normalizeSelf(TOL);
    return v;
}


} // Nanorex

#endif // NX_POINT_H

