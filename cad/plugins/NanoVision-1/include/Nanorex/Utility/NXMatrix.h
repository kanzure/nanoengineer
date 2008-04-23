// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MATRIX_H
#define NX_MATRIX_H

#include <Nanorex/Utility/NXVector.h>

namespace Nanorex {

/* CLASS: NXMatrix */
/**
 * Column-major matrix of dimensions M x N
 *
 */
template<typename T, int M, int N>
	class NXMatrix {
	public:
		NXMatrix() throw() {}
		~NXMatrix() throw() {}
		
		T const *const data(void) const throw() { return elems; }
		T *const data(void) throw() { return elems; }
		
		/// Access value at m-th row, n-th column
		T const& operator () (int const& m, int const& n) const throw();
		
		/// Access value at m-th row, n-th column
		T& operator () (int const& m, int const& n) throw();
		
		/// Access n-th column
		NXVectorRef<T,N> col(int const& n) throw();
		
		template<typename T1>
			NXMatrix<T,M,N>& operator += (NXMatrix<T1,M,N> const& A) throw();
		
		template<typename T1>
			NXMatrix<T,M,N>& operator -= (NXMatrix<T1,M,N> const& A) throw();
		
		template<typename T1>
			NXMatrix<T,M,N>& operator *= (T1 const& c) throw();
		
		template<typename T1>
			NXMatrix<T,M,N>& operator /= (T1 const& c) throw();
		
		
	private:
		T elems[M*N];
	};


typedef NXMatrix<double,3,3> NXMatrix33d;
typedef NXMatrix<float,3,3>  NXMatrix33f;
typedef NXMatrix<double,4,4> NXMatrix44d;
typedef NXMatrix<float,4,4>  NXMatrix44f;

// Access value at m-th row, n-th column
template<typename T, int M, int N>
	inline
	T const& NXMatrix<T,M,N>::operator () (int const& m, int const& n) const throw()
{
	return elems[n*M + m];
}

// Access value at m-th row, n-th column
template<typename T, int M, int N>
	inline
	T& NXMatrix<T,M,N>::operator () (int const& m, int const& n) throw()
{
	return elems[n*M + m];
}

// Access n-th column
template<typename T, int M, int N>
	inline
	NXVectorRef<T,N> NXMatrix<T,M,N>::col(int const& n) throw()
{
	return NXVectorRef<T,N>(elems + n*M);
}


template<typename T, int M, int N>
	template<typename T1>
	inline
	NXMatrix<T,M,N>&
	NXMatrix<T,M,N>::operator += (NXMatrix<T1,M,N> const& A) throw()
{
	// Exploit isomorphism with M*N-dimensional vectors
	NXVectorRef<T,M*N> selfRef(elems);
	NXVectorRef<T1,M*N> ARef(A.data());
	selfRef += ARef;
	return *this;
}


template<typename T, int M, int N>
	template<typename T1>
	inline
	NXMatrix<T,M,N>&
	NXMatrix<T,M,N>::operator -= (NXMatrix<T1,M,N> const& A) throw()
{
	// Exploit isomorphism with M*N-dimensional vectors
	NXVectorRef<T,M*N> selfRef(elems);
	NXVectorRef<T1,M*N> ARef(A.data());
	selfRef -= ARef;
	return *this;
}


template<typename T, int M, int N>
	template<typename T1>
	inline
	NXMatrix<T,M,N>& NXMatrix<T,M,N>::operator *= (T1 const& c) throw()
{
	// Exploit isomorphism with M*N-dimensional vectors
	NXVectorRef<T,M*N> selfRef(elems);
	selfRef *= c;
	return *this;
}


template<typename T, int M, int N>
	template<typename T1>
	inline
	NXMatrix<T,M,N>& NXMatrix<T,M,N>::operator /= (T1 const& c) throw()
{
	// Exploit isomorphism with M*N-dimensional vectors
	NXVectorRef<T,M*N> selfRef(elems);
	T const one_by_c = T(1) / c;
	selfRef *= one_by_c;
	return *this;
}



/// Matrix-matrix multiplication (inefficient)
template<typename T, int M, int N, int K>
	NXMatrix<T,M,N> operator * (NXMatrix<T,M,K> const& A,
	                            NXMatrix<T,K,N> const& B)
{
	NXMatrix<T,M,N> C; // result
	for(int m=0; m<M; ++m) {
		for(int n=0; n<N; ++n) {
			T sum_mn(0);
			for(int k=0; k<K; ++k) {
				sum_mn += A(m,k) * B(k,n);
			}
			C(m,n) = sum_mn;
		}
	}
}


/// Matrix-vector multiplication (inefficient)
template<typename T, int M, int N>
	NXVector<T,M> operator * (NXMatrix<T,M,N> const& A,
	                          NXVector<T,N> const& x)
{
	NXVector<T,M> y; // result
	y.zero();
	for(int n=0; n<N; ++n) {
		for(int m=0; m<M; ++m) {
			y[m] += A(m,n) * x[n];
		}
	}
}


} // namespace Nanorex

#endif // NX_MATRIX_H
