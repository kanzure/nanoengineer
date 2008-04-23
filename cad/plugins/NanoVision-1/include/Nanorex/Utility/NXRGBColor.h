// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RGBCOLOR_H
#define NX_RGBCOLOR_H

#include <cmath>
#include <cassert>

namespace Nanorex {

struct NXRGBColor {
    double r;
    double g;
    double b;
    
	NXRGBColor(double const& R=0.0, double const& G=1.0, double const& B=1.0)
        : r(R), g(G), b(B) {}
    
	NXRGBColor(unsigned int R, unsigned int B, unsigned int G, unsigned int max)
        : r(double(R)/double(max)),
        g(double(G)/double(max)),
        b(double(B)/double(max)) {}
	
    ~NXRGBColor() {}
	
	void convertFromHSV(double const& _h, double const& s, double const& v) {
		// Ref:
		// http://en.wikipedia.org/wiki/HSV_color_space#Conversion_from_HSV_to_RGB
		
		double const h = _h * 360.0; // h is supplied in [0,1]
		
		// check preconditions
		assert(h >= 0.0 && h < 360.0);
		assert(s >= 0.0 && s <= 1.0);
		assert(v >= 0.0 && v <= 1.0);
		
		double const h_by_60 = h / 60.0;
		int const floor_h_by_60 = static_cast<int>(floor(h_by_60));
		int const h_i = floor_h_by_60 % 6;
		double const f = h_by_60 - floor_h_by_60;
		double const p = v * (1.0 - s);
		double const q = v * (1.0 - f*s);
		double const t = v * (1.0 - (1.0-f)*s);
		
		switch(h_i) {
		case 0: r = v; g = t; b = p; break;
		case 1: r = q; g = v; b = p; break;
		case 2: r = p; g = v; b = t; break;
		case 3: r = p; g = q; b = v; break;
		case 4: r = t; g = p; b = v; break;
		case 5: r = v; g = p; b = q; break;
		default:
			assert(0);
		}
	}
};

} // Nanorex

#endif // NX_RGBCOLOR_H
