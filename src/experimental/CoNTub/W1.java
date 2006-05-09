//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import java.text.*;

public class W1
{
	public static final int HYDROGEN = 1;
	public static final int NITROGEN = 7;

	protected MoleculaT SW;

	/*
	 * (a, b) - nanotube chirality
	 * c - nanotube length in angstroms
	 * terminator - an element number for terminating atoms, ignored if not HYDROGEN or NITROGEN
	 */
	public W1(int a, int b, double c, int terminator) {
		SW = new MoleculaT ();
		formato fi, fd;  // formats for printing numbers
		SW.vaciar ();   // vaciar --> empty/clear: remove all atoms and bonds
		Nanotubo NT = new Nanotubo (a, b);

		// estimated number of atoms
		int guess = (int) (NT.radio () * 2 * Math.PI * c * 0.34);

		if (guess > 6000) {
			// throw new Exception("too many atoms");
			// worry?
		} else if (guess > 4000) {
			// worry?
		} else if (guess > 2000) {
			// worry?
		}

		double x, xc, y, yc, z, zc;
		for (int i = 1; i * NT.deltaz () <= c; i++) {
			for (int j = 1; j <= NT.d (); j++) {
				x = NT.deltaz () * i;
				xc = NT.deltaz () * i + NT.deltazc ();
				y = NT.radio () * (float) Math.sin (NT.deltaphi () * i +
								    2 * (float) Math.PI / NT.d () * j);
				yc = NT.radio () * (float) Math.sin (NT.deltaphi () * i +
								     NT.deltaphic () +
								     2 * (float) Math.PI / NT.d () * j);
				z = NT.radio () * (float) Math.cos (NT.deltaphi () * i +
								    2 * (float) Math.PI / NT.d () * j);
				zc = NT.radio () * (float) Math.cos (NT.deltaphi () * i +
								     NT.deltaphic () +
								     2 * (float) Math.PI / NT.d () * j);
				SW.addVert (x, y, z, 6);
				SW.addVert (xc, yc, zc, 6);
			}
		}
		finish(SW, terminator);
	}

	protected void finish(MoleculaT SW, int terminator) {
		SW.centrar ();
		SW.ponconec ();
		if (terminator == HYDROGEN) {
			SW.cierraH ();
			SW.ponconec ();
		} else if (terminator == NITROGEN) {
			SW.cierraN ();
			SW.ponconec ();
		}
	}

	public String pdb() {
		return SW.pdb();
	}

	public String mmp() {
		return SW.mmp();
	}

	public static void main(String[] argv) {
		int a, b, terminator;
		double c;
		a = Integer.parseInt(argv[0]);
		b = Integer.parseInt(argv[1]);
		c = Double.parseDouble(argv[2]);
		terminator = Integer.parseInt(argv[3]);
		W1 w1 = new W1(a, b, c, terminator);
		System.out.println(w1.mmp());
		// System.out.println(w1.pdb());
	}
}
