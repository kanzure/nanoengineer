#ifndef COLOR_H_INCLUDED
#define COLOR_H_INCLUDED

class Color {
 public:
    int r, g, b;

    Color() {
	r = g = b = 0;
    }
    Color(int r1, int g1, int b1) {
	r = r1;
	g = g1;
	b = b1;
    }
};

#define BLACK  Color(0, 0, 0)

#endif
