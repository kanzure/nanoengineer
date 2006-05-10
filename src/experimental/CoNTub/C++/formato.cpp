#include "formato.h"

formato::formato ()
{
    //formato = new DecimalFormat ();
}			//Constructor neutro


formato::formato (int l, String tipo)
{			//constructor con longitud de cadena y numero de decimales.
#if 0
    formato = new DecimalFormat (tipo);
    DecimalFormatSymbols dfs = new DecimalFormatSymbols ();
    String ch = ".";

    dfs.setDecimalSeparator (ch.toCharArray ()[0]);
    formato.setDecimalFormatSymbols (dfs);
    longitud = l;
#endif
}


String formato::aCadena (double numero)
{
#if 0
    String s = formato.format (numero);
    int l = s.length ();
    String t = "";
    for (int i = 1; i <= longitud - l; i++)
	t = t + " ";
    String fin = t + s;
    return fin;
#endif
    return String("abc");
}

String formato::aCadena (float numero)
{
#if 0
    String s = formato.format (numero);
    int l = s.length ();
    String t = " ";
    for (int i = 1; i <= longitud - l; i++)
	t = t + " ";
    String fin = t + s;
    return fin;
#endif
    return String("abc");
}

String formato::aCadena (int numero)
{
#if 0
    String s = formato.format (numero);
    int l = s.length ();
    String t = "";
    for (int i = 1; i <= longitud - l; i++)
	t = t + " ";
    String fin = t + s;
    return fin;
#endif
    return String("abc");
}
