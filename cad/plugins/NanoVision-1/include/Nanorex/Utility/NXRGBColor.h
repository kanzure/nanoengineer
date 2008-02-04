// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RGBCOLOR_H
#define NX_RGBCOLOR_H

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
};

} // Nanorex

#endif // NX_RGBCOLOR_H
