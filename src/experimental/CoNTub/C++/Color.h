#ifndef COLOR_H_INCLUDED
#define COLOR_H_INCLUDED

class Color {
 public:
    float r, g, b;

    Color() {
	r = g = b = 0.0f;
    }
    Color(float r1, float g1, float b1) {
	r = r1;
	g = g1;
	b = b1;
    }
};

#define BLACK  Color(0.0f, 0.0f, 0.0f)

#endif
