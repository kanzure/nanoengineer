#ifndef STRING_H_INCLUDED
#define STRING_H_INCLUDED

class String
{
    char *contents;
public:
    String(char *s) {
	contents = s;
    }
};

#endif
