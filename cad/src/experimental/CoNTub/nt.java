import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import javax.swing.ImageIcon;

public class nt extends Applet
{
	int i, j;
	public JTabbedPane multipanel;
	public P1 panel1;
	public P15 panel15;
	public P2 panel2;
	public P3 panel3;
	public P35 panel35;

	public void init ()
	{
		setLayout (new BorderLayout ());
		multipanel = new JTabbedPane (SwingConstants.TOP);
		add ("Center", multipanel);
		P1 panel1 = new P1 ();
		P15 panel15 = new P15 ();
		P2 panel2 = new P2 ();
		P3 panel3 = new P3 ();
		P35 panel35 = new P35 (panel2.molT (), panel1.molT (),
				       panel15.molT ());

//ImageIcon I1=new ImageIcon("2T.gif");
//ImageIcon I2=new ImageIcon("2T.gif");
//ImageIcon I3=new ImageIcon("help.gif");
//ImageIcon I4=new ImageIcon("INFO.gif");


		  multipanel.addTab ("NT HeteroJunction", null, panel2, "HeteroJunction Generation");
//multipanel.addTab("SWNT" ,null,panel1,"Single Walled Nanotube Generation");
		  multipanel.addTab ("SWNT", null, panel1, "Single Walled Nanotube Generation");
		  multipanel.addTab ("MWNT", null, panel15, "Multi-Walled Nanotube Generation");
		  multipanel.addTab ("OUTPUT", null, panel35, "Text output in PDB format");
		  multipanel.addTab ("Help", null, panel3, "Short Help");

		  multipanel.setSelectedIndex (0);


	}
	public void destroy ()
	{
	}			//Metodos de destruccion, parada, conienzo
	public void start ()
	{
	}
	public void stop ()
	{
	}
	public void processEvent (AWTEvent e)
	{
		if (e.getID () == Event.WINDOW_DESTROY) {
			System.exit (0);
		}
	}


}
