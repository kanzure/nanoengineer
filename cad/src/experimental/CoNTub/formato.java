//package nt;

import java.text.*;

public class formato
{
	DecimalFormat formato;
	int longitud;
	String distrib;

	public formato ()
	{
		formato = new DecimalFormat ();
	}			//Constructor neutro


	public formato (int l, String tipo)
	{			//constructor con longitud de cadena y numero de decimales.
		formato = new DecimalFormat (tipo);
		DecimalFormatSymbols dfs = new DecimalFormatSymbols ();
		String ch = ".";

		dfs.setDecimalSeparator (ch.toCharArray ()[0]);
		formato.setDecimalFormatSymbols (dfs);
		longitud = l;
	}


	String aCadena (double numero)
	{
		String s = formato.format (numero);
		int l = s.length ();
		String t = "";
		for (int i = 1; i <= longitud - l; i++)
			t = t + " ";
		String fin = t + s;
		return fin;
	}

	String aCadena (float numero)
	{
		String s = formato.format (numero);
		int l = s.length ();
		String t = " ";
		for (int i = 1; i <= longitud - l; i++)
			t = t + " ";
		String fin = t + s;
		return fin;
	}

	String aCadena (int numero)
	{
		String s = formato.format (numero);
		int l = s.length ();
		String t = "";
		for (int i = 1; i <= longitud - l; i++)
			t = t + " ";
		String fin = t + s;
		return fin;
	}



}
