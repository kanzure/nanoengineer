//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;

public class P4 extends JPanel
{
	private JButton B1;
	private JLabel etiq;
	private JTextArea texto;
	public P4 ()
	{
		setLayout (new BorderLayout ());
		texto = new JTextArea ("Texto de ayuda breve y about");
		etiq = new JLabel ("Una simple etiqueta");
		B1 = new JButton ("boton1");
		add (texto, BorderLayout.CENTER);
		add (B1, BorderLayout.NORTH);
	}


}
