#ifndef FORMATO_H_INCLUDED
#define FORMATO_H_INCLUDED

#include "String.h"

class formato
{
    //DecimalFormat formato;
    //int longitud;
    //String distrib;

 public:
    formato ();
    formato (int l, String tipo);
    String aCadena (double numero);
    String aCadena (float numero);
    String aCadena (int numero);
};

#endif
