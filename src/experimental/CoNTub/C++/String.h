#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

#include <iostream>

class String
{
    char *contents;
 public:
    String() { }
    int length();
    String(char *s) {
	contents = s;
    }
    String operator+ (char *x) {
	String y;
	std::cerr << "NOT IMPLEMENTED YET";
	return y;
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
