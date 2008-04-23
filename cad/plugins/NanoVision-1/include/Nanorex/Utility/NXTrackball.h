// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_TRACKBALL_H
#define NX_TRACKBALL_H

#include <Nanorex/Utility/NXQuaternion.h>
#include <cmath>

namespace Nanorex {

class NXTrackball {
public:
    NXTrackball()
        : w2(0.0), h2(0.0), scale(0.0), mouseSpeedDuringRotation(1.0) {}
    
	NXTrackball(int const& w, int const& h) {
        resize(w, h);
        mouseSpeedDuringRotation = 1.0;
    }
    
	~NXTrackball() {}
    
    // accessors
    double getWidth(void) const { return (w2+w2); }
	
    double getHeight(void) const { return (h2+h2); }
	
    void resize(int const& w, int const& h) {
        w2 = 0.5*((double)w);
        h2 = 0.5*((double)h);
        scale = 1.1 / ((w2 < h2) ? w2 : h2);
    }
    
	// double const *const getOldMouse(void) const { return oldMouse; }
	// double const *const getNewMouse(void) const { return newMouse; }
    
	double const& getMouseSpeedDuringRotation(void) const {
		return mouseSpeedDuringRotation;
	}
    void setMouseSpeedDuringRotation(double const& speed) { 
	    mouseSpeedDuringRotation = speed;
    }
    
    void start(int const& x, int const& y) {
        proj2sphere( oldMouse,
                     (double(x) - w2) * scale * mouseSpeedDuringRotation,
                     (h2 - double(y)) * scale * mouseSpeedDuringRotation );
    }
    
    void update(int const& x, int const& y) {
        proj2sphere( newMouse,
                     (double(x) - w2) * scale * mouseSpeedDuringRotation,
                     (h2 - double(y)) * scale * mouseSpeedDuringRotation );
    }
    
	NXQuaternion<double> getRotationQuat(void) {
		return NXQuaternion<double>(NXVectorRef<double,3>(oldMouse),
		                            NXVectorRef<double,3>(newMouse));
	}
	
private:
    double w2; // half-screen-width
    double h2; // half-screen-height
    double scale;
    double mouseSpeedDuringRotation;
    double oldMouse[3];
    double newMouse[3];
    
    /// Project screen coords (x,y) in [-1,1]^2 to unit-sphere and store in wpt
    static void proj2sphere(double *wpt, double const& x, double const& y) {
        double const d = sqrt(x*x+y*y);
        double const theta = M_PI * 0.5 * d;
        if(d > 0.0001) {
#ifdef _GNU_SOURCE
            double sinTheta = 0.0, cosTheta = 0.0;
            sincos(theta, &sinTheta, &cosTheta);
#else
            double const sinTheta = sin(theta);
            double const cosTheta = cos(theta);
#endif
            wpt[0] = sinTheta * x / d;
            wpt[1] = sinTheta * y / d;
            wpt[2] = cosTheta;
        }
    }
};

} // Nanorex

#endif // NX_TRACKBALL_H
