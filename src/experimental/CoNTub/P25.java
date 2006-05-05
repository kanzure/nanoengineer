
//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import java.text.*;

public class P25 extends JPanel implements ActionListener, ItemListener
{
	private JLabel l1, l2, l3, l4, l5;
	private JTextField t1, t2, t3, t4, t5;
	private JCheckBox cb1, cb2, cb3;
	private JTextArea txtout;
	private JScrollPane ct;
	private JComboBox combo;
	boolean bst, atn, hbk;
	Mira3D pan3D;
	public MoleculaT MW;
	formato fd;


	public P25 ()
	{
		setLayout (new BorderLayout ());
		Box ct1 = Box.createHorizontalBox ();
		  ct1.setBorder (BorderFactory.
				 createCompoundBorder (BorderFactory.
						       createTitledBorder ("Inner indices and length. (\u212B)"), BorderFactory.createEtchedBorder (1)));
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

		Box cls = Box.createHorizontalBox ();
		  cls.setBorder (BorderFactory.
				 createCompoundBorder (BorderFactory.createTitledBorder ("Shells and spacing."), BorderFactory.createEtchedBorder (1)));
		  l4 = new JLabel (" N= ");
		  l5 = new JLabel (" S= ");
		  t4 = new JTextField ("2");
		  t4.addActionListener (this);
		  t5 = new JTextField ("2.48");
		  t5.addActionListener (this);
		  cls.add (l4);
		  cls.add (t4);
		  cls.add (l5);
		  cls.add (t5);

		  combo = new JComboBox ();
		  combo.addItem ("No endings");
		  combo.addItem ("Hydrogen");
		  combo.addItem ("Nitrogen");

		Box cv = Box.createVerticalBox ();
		  cb1 = new JCheckBox ("Ball & Stick (b)");
		  cb1.addItemListener (this);
		  bst = false;
		  cb2 = new JCheckBox ("Atom labels (l)");
		  cb2.addItemListener (this);
		  atn = false;
		  cb3 = new JCheckBox ("Cut back (c)");
		  cb3.addItemListener (this);
		  hbk = false;
		  cv.add (cb1);
		  cv.add (cb2);
		  cv.add (cb3);

		JButton b = new JButton ("CREATE");
		  b.addActionListener (this);

		  txtout = new JTextArea ("", 20, 6);
		  ct = new JScrollPane (txtout);
		  txtout.setEditable (false);
		Font fo = new Font ("Courier", 1, 12);
		  txtout.setFont (fo);

		Box c0 = Box.createVerticalBox ();
		  c0.add (ct1);
		  c0.add (cls);
		  c0.add (combo);
		  c0.add (b);

		JPanel c1 = new JPanel ();
		  c1.setLayout (new BorderLayout ());
		  c1.add (c0, BorderLayout.NORTH);
		  c1.add (ct, BorderLayout.CENTER);
		  c1.add (cv, BorderLayout.SOUTH);

		  pan3D = new Mira3D ();

		  add (pan3D, BorderLayout.CENTER);
		  add (c1, BorderLayout.WEST);

	}
	public void actionPerformed (ActionEvent ev)
	{

		int i1, j1, n;
		double l, s;
		try {
			i1 = Integer.parseInt (t1.getText ().trim ());	//pillamos indice se tubos
			j1 = Integer.parseInt (t2.getText ().trim ());
			n = Integer.parseInt (t4.getText ().trim ());
			l = Double.parseDouble (t3.getText ().trim ());
			s = Double.parseDouble (t5.getText ().trim ());
		}

		catch (Exception e) {
			JOptionPane.showMessageDialog (null, "Stop: wrong input", "Stop", 0);
			return;
		}

		if (i1 == 0 && j1 == 0) {
			JOptionPane.showMessageDialog (null, "Error: Inner tube's indices are incorrect", "Error", JOptionPane.ERROR_MESSAGE);
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

		generatubo (i1, j1, l, n, s);
	}

	void generatubo (int a, int b, double c, int nshells, double sshell)
	{
		formato fi, fd;
		fd = new formato (8, "##0.00");	//para los radios de los tubos
		MW = new MoleculaT ();

		Nanotubo NT = new Nanotubo (a, b);

		MW.setInfo ("Multi-walled nanotube with ");	//+nshells+" shells and inner indices ("+a+","+b+")");

		int guess = (int) (NT.radio () * 2 * Math.PI * c * 0.34);

		for (int i = 1; i <= nshells; i++)

			guess = guess + (int) ((NT.radio () + sshell * i) * 2 * Math.PI * c * 0.34);

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
				MW.addVert (x, y, z, 6);
				MW.addVert (xc, yc, zc, 6);

		}}
		double rad1 = 0.01 * (int) (100 * NT.radio ());
		txtout.setText ("Tube 1 is (" + a + "," + b + "), r=" + fd.aCadena (rad1));


		//GENERAMOS EL RESTO DE CAPAS
		double A = 2.46;
		double dz1 = A * Math.sin (Math.PI / 3 - NT.quiral ());
		double dz2 = A * Math.sin (NT.quiral ());
		double dx1 = A * Math.cos (Math.PI / 3 - NT.quiral ());
		double dx2 = A * Math.cos (NT.quiral ());
		int ni = a;
		int nj = b;
		double zeta = 0;

		double cshell = NT.radio () * 2 * Math.PI;	//circungitud primera capa
		double radpaso = NT.radio () * 2 * Math.PI;	//que a su vez es inicio


		for (int j = 1; j <= nshells - 1; j++) {
			cshell = cshell + sshell * 2 * Math.PI;	//Objetivo

			for (int k = 0; radpaso < cshell; k++) {	//radpaso busca al objetivo
				if (zeta < 0) {
					nj++;
					zeta = zeta + dz2;
					radpaso = radpaso + dx2;
				} else {
					ni++;
					zeta = zeta - dz1;
					radpaso = radpaso + dx1;
				}
			}

			Nanotubo NTC = new Nanotubo (ni, nj);
			double rad = 0.01 * (int) (100 * NTC.radio ());
			txtout.setText (txtout.getText () + "\nTube " + (j + 1) + " is (" + ni + "," + nj + "), r=" + fd.aCadena (rad));

			for (int i = 1; i * NTC.deltaz () <= c; i++) {
				for (int k = 1; k <= NTC.d (); k++) {
					x = NTC.deltaz () * i;
					xc = NTC.deltaz () * i + NTC.deltazc ();
					y = NTC.radio () * (float) Math.sin (NTC.deltaphi ()
									     * i + 2 * (float)
									     Math.PI / NTC.d () * k);
					yc = NTC.radio () * (float) Math.sin (NTC.deltaphi ()
									      * i + NTC.deltaphic ()
									      + 2 * (float)
									      Math.PI / NTC.d () * k);
					z = NTC.radio () * (float) Math.cos (NTC.deltaphi ()
									     * i + 2 * (float)
									     Math.PI / NTC.d () * k);
					zc = NTC.radio () * (float) Math.cos (NTC.deltaphi ()
									      * i + NTC.deltaphic ()
									      + 2 * (float)
									      Math.PI / NTC.d () * k);
					MW.addVert (x, y, z, 6);
					MW.addVert (xc, yc, zc, 6);
			}}
		}
		MW.centrar ();
		MW.ponconec ();
		if (combo.getSelectedItem () == "Hydrogen") {
			MW.cierraH ();
			MW.ponconec ();
		} else if (combo.getSelectedItem () == "Nitrogen") {
			MW.cierraN ();
			MW.ponconec ();
		}
		//MW.setInfo(MW.getInfo()+" and length "+c+" A.");

		fi = new formato (5, "#####");	//para los enteros
		StringBuffer pdb = new StringBuffer ("");
		Minimol mmol = new Minimol (MW);
		for (int i = 0; i < mmol.nvert; i++) {
			String lab = mmol.minietiqs[i];
			pdb.append ("HETATM" + fi.aCadena (i + 1) + "  " +
				    lab + "      " + fi.aCadena (i + 1) +
				    "    " + fd.aCadena (mmol.miniverts[i].x) + fd.aCadena (mmol.miniverts[i].y) + fd.aCadena (mmol.miniverts[i].z) + "\n");
		}
		for (int i = 0; i < mmol.nvert; i++)	//CONECTIVIDAD
		{
			pdb.append ("CONECT" + fi.aCadena (i + 1));
			for (int j = 1; j <= mmol.miniconec[i][0]; j++)
				pdb.append (fi.aCadena (mmol.miniconec[i][j] + 1));
			pdb.append ("\n");
		}
		pdb = pdb.append ("END");

		txtout.setText (pdb + "");



		pan3D.cargarMol (MW);
		pan3D.repaint ();

	}
	public MoleculaT molT ()
	{
		return MW;
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
		//Now that we know which button was pushed, find out
		//whether it was selected or deselected.

	}
}
