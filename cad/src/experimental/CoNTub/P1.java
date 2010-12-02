//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import java.text.*;

public class P1 extends JPanel implements ActionListener, ItemListener
{
	private JButton b;
	private JLabel l1, l2, l3;
	private JTextField t1, t2, t3;
	private NTLienzo lienzo;
	private JCheckBox cb1, cb2, cb3;
	private JPanel c1, c0, c2, c3, c4;
	private JComboBox combo;
	boolean bst, atn, hbk;
	Mira3D pan3D;
	public MoleculaT SW;

	public P1 ()
	{
		SW = new MoleculaT ();
		pan3D = new Mira3D ();
		//lienzo=new NTLienzo();

		setLayout (new BorderLayout ());

		JButton b = new JButton (" CREATE ");
		  b.addActionListener (this);

		Box ct1 = Box.createHorizontalBox ();
		  ct1.setBorder (BorderFactory.
				 createCompoundBorder (BorderFactory.
						       createTitledBorder ("Indices and length. (\u212B)"), BorderFactory.createEtchedBorder (1)));
		  l1 = new JLabel ("   i=  ");
		  l2 = new JLabel ("   j=  ");
		  l3 = new JLabel ("   l=  ");
		  t1 = new JTextField (" 5");
		  t1.addActionListener (this);
		  t2 = new JTextField (" 5");
		  t2.addActionListener (this);
		  t3 = new JTextField ("10");
		  t3.addActionListener (this);
		  ct1.add (l1);
		  ct1.add (t1);
		  ct1.add (l2);
		  ct1.add (t2);
		  ct1.add (l3);
		  ct1.add (t3);


		  combo = new JComboBox ();
		  combo.addItem ("No endings");
		  combo.addItem ("Hydrogen");
		  combo.addItem ("Nitrogen");

		Box cv = Box.createVerticalBox ();
		  cb1 = new JCheckBox ("Ball & Stick (b)");
		  cb1.addItemListener (this);
		  bst = false;
		  cb2 = new JCheckBox ("Atom labels (l) ");
		  cb2.addItemListener (this);
		  atn = false;
		  cb3 = new JCheckBox ("Cut back (c)");
		  cb3.addItemListener (this);
		  hbk = false;
		  cv.add (cb1);
		  cv.add (cb2);
		  cv.add (cb3);

		Box c = Box.createVerticalBox ();
		  c.add (ct1);
		  c.add (combo);
		  c.add (b);

		  lienzo = new NTLienzo ();

		JPanel c1 = new JPanel ();
		  c1.setLayout (new BorderLayout ());

		  c1.add (c, BorderLayout.NORTH);
		  c1.add (cv, BorderLayout.SOUTH);
		  c1.add (lienzo, BorderLayout.CENTER);

		  add (c1, BorderLayout.WEST);
		  add (pan3D, BorderLayout.CENTER);


		  lienzo.redraw (1, 0);

	}

	public void actionPerformed (ActionEvent ev)
	{

		int i1, j1;
		double l;
		try {
			i1 = Integer.parseInt (t1.getText ().trim ());	//pillamos indice se tubos
			j1 = Integer.parseInt (t2.getText ().trim ());
			l = Double.parseDouble (t3.getText ().trim ());
		}

		catch (Exception e) {
			JOptionPane.showMessageDialog (null, "Stop: wrong input", "Stop", 0);
			return;
		}

		if (i1 == 0 && j1 == 0) {
			JOptionPane.showMessageDialog (null, "Error: Tube's indices are incorrect", "Error", JOptionPane.ERROR_MESSAGE);
			return;
		}
		//Y giramos automaticamente los indices de los tubos hasta meterlos el el primer sextante
		boolean cambio1 = false;
		for (; (i1 < 0) || (j1 < 0);) {
			int i1n = -j1;
			int j1n = i1 + j1;
			i1 = i1n;
			j1 = j1n;
			cambio1 = true;
		}

		if (i1 == 0) {
			i1 = j1;
			j1 = 0;
		}		//minirevis

		if (cambio1) {
			JOptionPane.showMessageDialog (null,
						       "Warning: Indices automatically translated to ("
						       + i1 + "," + j1 + ")", "Warning", JOptionPane.INFORMATION_MESSAGE);
			t1.setText ("" + i1);
			t2.setText ("" + j1);
		}

		SW.setInfo ("(" + i1 + "," + j1 + ") Nanotube with length " + l + " A.");
		lienzo.redraw (i1, j1);
		generatubo (i1, j1, l);
	}

	void generatubo (int a, int b, double c)
	{
		formato fi, fd;  // formats for printing numbers
		SW.vaciar ();   // vaciar --> empty/clear: remove all atoms and bonds
		Nanotubo NT = new Nanotubo (a, b);

		int guess = (int) (NT.radio () * 2 * Math.PI * c * 0.34);

		if (guess > 6000) {
			JOptionPane.showMessageDialog (null, "Structure will have more than 6000 Atoms. Process stopped.", "STOP", 0);
			return;
		} else if (guess > 4000) {
			int sale = JOptionPane.showConfirmDialog (null,
								  "Structure will have more than 4000 Atoms. Continue at your own risk",
								  "Warning", 0);
			if (sale == 1)
				return;
		} else if (guess > 2000)
			JOptionPane.showMessageDialog (null, "Big Structure: using low-consuming display.", "Big molecule", 1);

		double x, xc, y, yc, z, zc;
		for (int i = 1; i * NT.deltaz () <= c; i++) {
			for (int j = 1; j <= NT.d (); j++) {
				x = NT.deltaz () * i;
				xc = NT.deltaz () * i + NT.deltazc ();
				y = NT.radio () * (float) Math.sin (NT.deltaphi () * i + 2 * (float) Math.PI / NT.d () * j);
				yc = NT.radio () * (float) Math.sin (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) Math.PI / NT.d () * j);
				z = NT.radio () * (float) Math.cos (NT.deltaphi () * i + 2 * (float) Math.PI / NT.d () * j);
				zc = NT.radio () * (float) Math.cos (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) Math.PI / NT.d () * j);
				SW.addVert (x, y, z, 6);
				SW.addVert (xc, yc, zc, 6);
			}
		}
		SW.centrar ();
		SW.ponconec ();
		if (combo.getSelectedItem () == "Hydrogen") {
			SW.cierraH ();
			SW.ponconec ();
		} else if (combo.getSelectedItem () == "Nitrogen") {
			SW.cierraN ();
			SW.ponconec ();
		}
		pan3D.cargarMol (SW);
		pan3D.repaint ();
	}

	public MoleculaT molT ()
	{
		return SW;
	}

	public void itemStateChanged (ItemEvent e)
	{
		Object source = e.getItemSelectable ();
		if (source == cb1) {
			if (e.getStateChange () == ItemEvent.DESELECTED)
				bst = false;
			else
				bst = true;
			pan3D.repinta (bst, atn, hbk);
		} else if (source == cb2) {
			if (e.getStateChange () == ItemEvent.DESELECTED)
				atn = false;
			else
				atn = true;
			pan3D.repinta (bst, atn, hbk);
		} else if (source == cb3) {
			if (e.getStateChange () == ItemEvent.DESELECTED)
				hbk = false;
			else
				hbk = true;
			pan3D.repinta (bst, atn, hbk);
		}


	}

}
