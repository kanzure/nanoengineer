#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

#include <string.h>

class String
{
    char *contents;
public:
    String() { }
    String(char *s) {
	contents = s;
    }
    String operator+ (char *x) {
	String y;
	strcpy(y.contents, "NOT IMPLEMENTED YET");
	return y;
    }
    String operator+ (String x) {
	String y;
	strcpy(y.contents, "NOT IMPLEMENTED YET");
	return y;
    }
    /* http://gethelp.devx.com/techtips/cpp_pro/10min/10min0400.asp */
    friend std::ostream& operator<< (std::ostream& s, const String& x) {
	s << x.contents;
	return s;
    }
};

#endif
