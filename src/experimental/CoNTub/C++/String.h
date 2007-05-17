// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

#include <iostream>
#include "string.h"

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
    String(int p) {
	char tmp[50];
	sprintf(tmp, "%d", p);
	len = strlen(tmp);
	contents = new char[len + 1];
	strcpy(contents, tmp);
    }
    String(double p) {
	char tmp[50];
	sprintf(tmp, "%lf", p);
	len = strlen(tmp);
	contents = new char[len + 1];
	strcpy(contents, tmp);
    }
    String(char *s) {
	contents = s;
	len = strlen(s);
    }
    String operator+ (int x) {
	return *this + String(x);
    }
    String operator+ (double x) {
	return *this + String(x);
    }
    String operator+ (char *x) {
	return *this + String(x);
    }
    String operator+ (String x) {
	String s = String();
	s.len = len + x.len;
	s.contents = new char[s.len + 1];
	strcpy(s.contents, contents);
	strcpy(s.contents + len, x.contents);
	return s;
    }
    void operator+= (String x) {
	int newlen = len + x.len;
	char *newcontents = new char[newlen + 1];
	strcpy(newcontents, contents);
	strcpy(newcontents + len, x.contents);
	len = newlen;
	contents = newcontents;
    }
    void operator+= (char *y) {
	String x = String(y);
	int newlen = len + x.len;
	char *newcontents = new char[newlen + 1];
	strcpy(newcontents, contents);
	strcpy(newcontents + len, x.contents);
	len = newlen;
	contents = newcontents;
    }
    /* http://gethelp.devx.com/techtips/cpp_pro/10min/10min0400.asp */
    friend std::ostream& operator<< (std::ostream& s, const String& x) {
	s << x.contents;
	return s;
    }
};

#endif
