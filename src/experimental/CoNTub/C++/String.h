#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

class String
{
    char *contents;
public:
    String(char *s) {
	contents = s;
    }
#if 0
    friend ostream& operator << (ostream&  s, Vehicle & m) {
	s << "Vehicle: Longitude " << m.longitude;
	s << " Latitude " << m.latitude;
	s << " Gas " << m.gasTank << endl;
	return s;
    }
#endif
    String* operator+ (char *x) {
	return new String("NOT IMPLEMENTED YET");
    }
};

#endif
