//package nt;

import javax.swing.*;
import java.awt.*;
import java.net.URL;
import java.awt.event.*;
import java.applet.*;

public class P3 extends JPanel
{
	JEditorPane pweb;
	JEditorPane ta;
	public P3 ()
	{
		pweb = new JEditorPane ();
		pweb.setEditable (true);

		String s = null, t = null;
		  try
		{
			s = "http://www.ugr.es/local/gmdm/java/contub/help/help.html";
			URL helpURL = new URL (s);
			  pweb.setPage (helpURL);
		}
		catch (Exception e)
		{
			System.err.println ("Couldn't create help URL: " + s);
		}




		JScrollPane pwebscroll = new JScrollPane (pweb);
		pwebscroll.setVerticalScrollBarPolicy (JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		pwebscroll.setBorder (BorderFactory.createCompoundBorder (BorderFactory.createTitledBorder ("HELP."), BorderFactory.createEtchedBorder (1)));
		pwebscroll.setPreferredSize (new Dimension (850, 620));
		pwebscroll.setMinimumSize (new Dimension (100, 100));
		add (pwebscroll);




	}


}
