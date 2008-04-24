// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_NAMEDVIEW_H
#define NX_NAMEDVIEW_H

#include <Nanorex/Utility/NXVector.h>
#include <Nanorex/Utility/NXQuaternion.h>

#include <iostream>
#include <string>

namespace Nanorex {

/* CLASS: NXNamedView */
class NXNamedView {
public:
	NXNamedView() {}
	NXNamedView(std::string const& theName,
	            NXQuaternion<double> const& theRotationQuat,
	            double const& theScale,
	            NXVector3d const& thePOV,
	            double const& theZoomFactor)
		: name(theName), rotationQuat(theRotationQuat), scale(theScale),
		POV(thePOV), zoomFactor(theZoomFactor), vdist(6.0*scale)
	{
	}
	~NXNamedView() {}
	
	std::string const& getName(void) const { return name; }
	void setName(std::string const& theName) { name = theName; }
	
	NXQuaternion<double> const& getQuat(void) const { return rotationQuat; }
	NXQuaternion<double>& getQuat(void) { return rotationQuat; }
	void setQuat(NXQuaternion<double> const& quat) { rotationQuat = quat; }
	
	double const& getScale(void) const { return scale; }
	void setScale(double const& theScale) { scale = theScale; vdist = 6.0*scale; }
	
	NXVectorRef3d getPOV(void) { return NXVectorRef3d(POV); }
	void setPOV(NXVector3d const& thePOV) { POV = thePOV; }
	
	double const& getZoomFactor(void) const { return zoomFactor; }
	void setZoomFactor(double const& theZoomFactor) {zoomFactor = theZoomFactor;}
	
	static double GetNear(void) { return 0.25; }
	static double GetFar(void) { return 12.0; }
	
	double const& getPOVDistanceFromEye(void) const { return vdist; }
	double getNearPlaneDistanceFromEye(void) const { return GetNear() * vdist; }
	double getFarPlaneDistanceFromEye(void) const { return GetFar() * vdist; }
	
private:
	std::string name;
	NXQuaternion<double> rotationQuat;
	double scale;
	NXVector3d POV;
	double zoomFactor;
	
	double vdist;
};


inline
std::ostream& operator << (std::ostream& o, Nanorex::NXNamedView& view)
{
	o << "csys (" << view.getName() << ") " << view.getQuat()
		<< " (" << view.getScale() << ") " << view.getPOV()
		<< " (" << view.getZoomFactor() << ')';
	return o;
}


} // namespace Nanorex

#endif // NX_NAMEDVIEW_H
