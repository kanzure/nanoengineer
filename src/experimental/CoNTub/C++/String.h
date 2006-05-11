#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

#include <iostream>

class String
{
    int len;
    char *contents;
 public:
    String() {
	contents = "";
	len = 0;
    }
    int length(void) {
	return len;
    }
    String(char *s) {
	contents = s;
	len = strlen(s);
    }
    String operator+ (char *x) {
	return *this + String(x);
    }
    String operator+ (String x) {
	String y;
	std::cerr << "NOT IMPLEMENTED YET";
	return y;
    }
    String operator+= (char *x) {
	String y;
	std::cerr << "NOT IMPLEMENTED YET";
	return y;
    }
    String operator+= (String x) {
	String y;
	std::cerr << "NOT IMPLEMENTED YET";
	return y;
    }
    void append(String x) {
	std::cerr << "NOT IMPLEMENTED YET";
    }
    /* http://gethelp.devx.com/techtips/cpp_pro/10min/10min0400.asp */
    friend std::ostream& operator<< (std::ostream& s, const String& x) {
	s << x.contents;
	return s;
    }
};

#endif
