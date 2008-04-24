// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_QUATERNION_H
#define NX_QUATERNION_H

#include <Nanorex/Utility/NXVector.h>
#include <Nanorex/Utility/NXMatrix.h>

#include <cmath>


#ifdef _GNU_SOURCE
inline void sincos(float x, float *sinx, float *cosx) {sincosf(x, sinx, cosx);}
inline void sincos(long double x, long double *sinx, long double *cosx) {
	sincosl(x, sinx, cosx);
}
#endif


namespace Nanorex {

/// Quaternion class stored as cos(theta/2) + sin(theta/2)*(x,y,z)
template<typename T>
class NXQuaternion {
public:
	
	NXQuaternion();
	
	/// w = cos(theta)/2 where theta is rotation angle, (x,y,z) specify axis vector
	/// NXQuaternion(1,0,0,0) => no rotation
	NXQuaternion(T const& _w, // cos(theta)/2
	             T const& _x, T const& _y, T const& _z);
	
	/// Quaternion that rotates the standard axes into the right-handed coordinate
	/// frame described by orthonormal vectors _x, _y and _z
	NXQuaternion(NXVectorRef<T,3> x, NXVectorRef<T,3> y, NXVectorRef<T,3> z);
	
	/// Rotation quaternion
	NXQuaternion(NXVectorRef<T,3> rotAxis, T const& theta);
	
	/// Quaternion that rotates from vec1 to vec2
	NXQuaternion(NXVectorRef<T,3> vec1, NXVectorRef<T,3> vec2);
	
	~NXQuaternion() {}
	
	/// Vector along the rotation axis
	NXVector<T,3> getAxisDirection(void);
	
	/// Rotation angle in radians
	T getAngle(void) const;
	void setAngle(T const& theta);
	
	/// Set to (*this + q) which is the result of applying *this followed by q
	NXQuaternion<T>& operator += (NXQuaternion<T> const& q);
	
	/// Result of (*this + q2)
	NXQuaternion<T> operator + (NXQuaternion<T> const& q2) const;
	
	/// Unary minus
	NXQuaternion<T> operator - (void) const;
	
	NXQuaternion<T>& operator *= (T const& n);
	
	/// Build rotation matrix.
	void buildMatrix(NXMatrix<T,4,4>& R);
	
	NXVector<T,3> rot(NXVectorRef<T,3> v);
	NXVector<T,3> unrot(NXVectorRef<T,3> v);

	NXQuaternion<T>& normalizeSelf(void);
	
private:
	T w; ///< cos(theta/2)
	NXVector<T,3> axis; ///< sin(theta/2) * rotation-axis-vector
	
	int incrementCounter;

	template<typename S>
		friend std::ostream& operator << (std::ostream& o, NXQuaternion<S> const& q);
};


template<typename T>
	inline
	NXQuaternion<T>::NXQuaternion()
	: w(1.0), axis(0.0, 0.0, 1.0)
{
}


template<typename T>
	inline
	NXQuaternion<T>::NXQuaternion(T const& _w,
	                              T const& _x, T const& _y, T const& _z)
	: w(_w), axis(), incrementCounter(0)
{
	/// @fixme check domain of _w
	T const sin_half_theta = sqrt(1.0 - _w*_w);
	axis[0] = sin_half_theta * _x;
	axis[1] = sin_half_theta * _y;
	axis[2] = sin_half_theta * _z;
	normalizeSelf();
}


// Rotation quaternion
template<typename T>
	inline
	NXQuaternion<T>::NXQuaternion(NXVectorRef<T,3> rotAxis, T const& theta)
	: w(0), axis(rotAxis), incrementCounter(0)
{
	setAngle(theta);
}


// Quaternion that rotates from vec1 to vec2
template<typename T>
	inline
	NXQuaternion<T>::NXQuaternion(NXVectorRef<T,3> vec1, NXVectorRef<T,3> vec2)
	: w(0), axis(), incrementCounter(0)
{
	NXVector<T,3> x = vec1;
	NXVector<T,3> y = vec2;
	x.normalizeSelf();
	y.normalizeSelf();
	T const dotxy = dot(x,y);
	NXVector<T,3> v = cross(x,y);
	T const vLen = length(v);
	
	if(vLen < 0.000001) {
		// x, y are very close, or very close to opposite, or one of them is zero
		if(dotxy < 0.0) {
			// close to opposite; treat as actually opposite
			w = 0.0;
			NXVector<T,3> X_AXIS(1,0,0), Y_AXIS(0,1,0);
			NXVector<T,3> ax1 = cross(x, X_AXIS);
			NXVector<T,3> ax2 = cross(x, Y_AXIS);
			if(length(ax1) > length(ax2))
				axis = ax1;
			else
				axis = ax2;
		}
		else {
		// very close, or one is zero -- we could pretend they're equal, but let's be a little
		//  more accurate than that -- vl is sin of desired theta, so vl/2 is approximately sin(theta/2)
		//  (##e could improve this further by using a better formula to relate sin(theta/2) to sin(theta)),
		//  so formula for xyz part is v/vl * vl/2 == v/2 [bruce 050730]
			NXVector<T,3> const xyz = v / 2.0;
			double const sin_half_theta = vLen / 2.0;
			double const cos_half_theta = sqrt(1 - sin_half_theta * sin_half_theta);
			w = cos_half_theta;
			axis = xyz;
		}
	}
	
	else {
		/// @todo check for possible instability when dotxy ~ 1
		T const maxval = T(-1.0) > dotxy ? T(-1.0) : dotxy;
		T const minval = T(1.0) < maxval ? T(1.0) : maxval;
		T theta = acos(minval);
		NXVector<T,3> crossxv = cross(x,v);
		T const doty_crossxv = dot(y, crossxv);
		if (doty_crossxv > 0.0)
			theta = 2.0 * M_PI - theta;
		w = cos(theta * 0.5);
		double const s = sqrt(1 - w*w) / vLen;
		axis = s * v;
	}
}

template<typename T>
	NXVector<T,3> NXQuaternion<T>::getAxisDirection(void)
{
	if(axis[0] == 0.0 && axis[1] == 0.0 && axis[2] == 0.0)
		// no rotation => return arbitrary axis
		return NXVector<T,3>(0.0, 0.0, 1.0);
	else
		return axis;
}


template<typename T>
	inline
	T twistor_angle(NXVectorRef<T,3> axis,
	                NXVectorRef<T,3> pt1,
	                NXVectorRef<T,3> pt2)
{
	NXQuaternion<T> q(axis, NXVector<T,3>(0,0,1));
	pt1 = q.rot(pt1);
	pt2 = q.rot(pt2);
	T const a1 = atan2(pt1[1], pt1[0]);
	T const a2 = atan2(pt2[1], pt2[0]);
	T const theta = a2 - a1;
	return theta;
}


template<typename T>
	inline
	NXQuaternion<T> twistor(NXVectorRef<T,3> axis,
	                        NXVectorRef<T,3> pt1,
	                        NXVectorRef<T,3> pt2)
{
	T const theta = twistor_angle(axis, pt1, pt2);
	return NXQuaternion<T>(axis, theta);
}


/* CONSTRUCTOR */
// Placed here because of dependence on twistor() which in turn depends on other constructors
// Quaternion that rotates the standard axes into the right-handed coordinate
// frame described by orthonormal vectors _x, _y and _z
template<typename T>
	inline
	NXQuaternion<T>::NXQuaternion(NXVectorRef<T,3> x,
	                              NXVectorRef<T,3> y,
	                              NXVectorRef<T,3> z)
	: w(0), axis(), incrementCounter(0)
{
	NXVector<T,3> const X_AXIS(1.0, 0.0, 0.0);
	NXVector<T,3> const Y_AXIS(1.0, 0.0, 0.0);
	
	NXQuaternion<T> xfixer(X_AXIS, x);
	NXVector<T,3> yAxis2 = xfixer.rot(Y_AXIS);
	NXQuaternion<T> yfixer = twistor(x, yAxis2, y); /// @todo implement twistor
	NXQuaternion<T> res = xfixer + yfixer;
	
	*this = res;
}




template<typename T>
inline T NXQuaternion<T>::getAngle(void) const
{
	if(w > -1.0 && w < 1.0) {
		T const retval = 2.0 * acos(w);
		return retval;
	}
	else
		return 0.0;
}


template<typename T>
inline void NXQuaternion<T>::setAngle(T const& theta)
{
	T const half_theta = 0.5 * theta;
#ifdef _GNU_SOURCE
	T sin_half_theta = 0.0, cos_half_theta = 0.0;
	sincos(half_theta, &sin_half_theta, &cos_half_theta);
#else
	T const sin_half_theta = sin(half_theta);
	T const cos_half_theta = cos(half_theta);
#endif
	w = cos_half_theta;
	axis *= sin_half_theta;
	normalizeSelf();
}


template<typename T>
	inline
	NXQuaternion<T> NXQuaternion<T>::operator + (NXQuaternion<T> const& q2) const
{
	NXQuaternion<T> q;
	q.w = q2.w*w - q2.axis[0]*axis[0] - q2.axis[1]*axis[1] - q2.axis[2]*axis[2];
	q.axis[0] = q2.w*axis[0] + q2.axis[0]*w       + q2.axis[1]*axis[2] - q2.axis[2]*axis[1];
	q.axis[1] = q2.w*axis[1] - q2.axis[0]*axis[2] + q2.axis[1]*w       + q2.axis[2]*axis[0];
	q.axis[2] = q2.w*axis[2] + q2.axis[0]*axis[1] - q2.axis[1]*axis[0] + q2.axis[2]*w;
	return q;
}


template<typename T>
	inline NXQuaternion<T>& NXQuaternion<T>::operator += (NXQuaternion<T> const& q)
{
	*this = *this + q;
	++incrementCounter;
	if(incrementCounter == 50)
		normalizeSelf();
	return *this;
}

/// multiplication by a scalar, i.e. Q1 * 1.3, defined so that
/// e.g. Q1 * 2 == Q1 + Q1, or Q1 = Q1 * 0.5 + Q1 * 0.5
template<typename T>
	inline NXQuaternion<T> operator * (NXQuaternion<T> const& q, T const& n)
{
	NXQuaternion<T> qResult(q);
	qResult.setAngle(n * q.getAngle());
	return qResult;
}

template<typename T>
	inline NXQuaternion<T>& NXQuaternion<T>::operator *= (T const& n)
{
	*this = *this * n;
	return *this;
}


template<typename T>
	inline NXQuaternion<T> NXQuaternion<T>::operator - (void) const
{
	NXQuaternion<T> q;
	q.w = w; // cos is even
	q.axis = -axis;
	return q;
}


template<typename T>
	inline NXQuaternion<T> conj(NXQuaternion<T> const& q)
{
	return -q;
}


template<typename T>
	inline NXQuaternion<T>& NXQuaternion<T>::normalizeSelf(void)
{
	T const len = length(axis);
	if(len != 0.0) {
		T const s = sqrt(1.0 - w*w) / len;
		axis *= s;
	}
	else {
		w = 1.0;
		axis.zero();
	}
	return *this;
}


/// Build rotation matrix
template<typename T>
	inline void NXQuaternion<T>::buildMatrix(NXMatrix<T,4,4>& R)
{
	normalizeSelf();
	R(0,0) = T(1.0) - T(2.0) * (axis[1] * axis[1] + axis[2] * axis[2]);
	R(0,1) = T(2.0) * (axis[0] * axis[1] - axis[2] * w);
	R(0,2) = T(2.0) * (axis[2] * axis[0] + axis[1] * w);
	R(0,3) = T(0.0);
	
	R(1,0) = T(2.0) * (axis[0] * axis[1] + axis[2] * w);
	R(1,1) = T(1.0) - T(2.0) * (axis[2] * axis[2] + axis[0] * axis[0]);
	R(1,2) = T(2.0) * (axis[1] * axis[2] - axis[0] * w);
	R(1,3) = T(0.0);
	
	R(2,0) = T(2.0) * (axis[2] * axis[0] - axis[1] * w);
	R(2,1) = T(2.0) * (axis[1] * axis[2] + axis[0] * w);
	R(2,2) = T(1.0) - T(2.0) * (axis[1] * axis[1] + axis[0] * axis[0]);
	R(2,3) = T(0.0);
	
	R(3,0) = T(0.0);
	R(3,1) = T(0.0);
	R(3,2) = T(0.0);
	R(3,3) = T(1.0);
	
}


template<typename T>
	inline
	NXVector<T,3> NXQuaternion<T>::rot(NXVectorRef<T,3> v)
{
	NXMatrix<T,4,4> R;
	buildMatrix(R);
	NXVector<T,4> v4;
	NXVectorRef<T,3>(v4.data()).copy(v);
	v4[3] = T(0);
	NXVector<T,4> result4 = R * v4;
	NXVector<T,3> result;
	result.copy(NXVectorRef<T,3>(result4.data()));
	return result;
}


template<typename T>
	inline
	NXVector<T,3> NXQuaternion<T>::unrot(NXVectorRef<T,3> v)
{
	NXMatrix<T,4,4> R;
	NXVector<T,3> result;
	
	// compute R^T v
	buildMatrix(R);
	for(int m=0; m<3; ++m) {
		NXVectorRef<T,3> R_col_m(R.col(m).data());
		result[m] = dot(R_col_m, v);
	}
	
	return result;
}


template<typename T>
	std::ostream& operator << (std::ostream& o, NXQuaternion<T> const& q)
{
	o << '(' << q.w << ',' << q.axis[0] << ',' << q.axis[1] << ',' << q.axis[2] << ')';
	return o;
}


} // namespace Nanorex

#endif // NX_QUATERNION_H
