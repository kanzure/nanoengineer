//package nt;

import java.util.logging.*;

public class W1
{
	/* -------- Logging for errors, warnings, and info -------- */

	protected static Logger logger = Logger.getLogger("mylogger");
	static {
		logger.setLevel(Level.WARNING);
	}

	protected static void logLevel(String str) {
		if ("info".equals(str))
			logger.setLevel(Level.INFO);
		else if ("off".equals(str))
			logger.setLevel(Level.OFF);
		else
			logger.setLevel(Level.WARNING);
	}

	/* ---------------------- */

	public static final int HYDROGEN = 1;
	public static final int NITROGEN = 7;

	protected MoleculaT molecule;

	protected W1() {
		// the constructor inherited by W2 and others
	}

	/*
	 * (a, b) - nanotube chirality
	 * c - nanotube length in angstroms
	 * terminator - an element number for terminating atoms, ignored if not HYDROGEN or NITROGEN
	 */
	public W1(int a, int b, double c, int terminator) {
		molecule = new MoleculaT ();
		molecule.vaciar ();   // vaciar --> empty/clear: remove all atoms and bonds
		Nanotubo NT = new Nanotubo (a, b);

		// estimated number of atoms
		// int guess = (int) (NT.radio () * 2 * Math.PI * c * 0.34);
		// In the original code, this was used as a basis to not compute structures that were
		// too big. I think the reason for not doing them was that they took too long with
		// bond enumeration as an order-N-squared operation.

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
				molecule.addVert (x, y, z, 6);
				molecule.addVert (xc, yc, zc, 6);
			}
		}
		finish(terminator);
	}

	protected void finish(int terminator) {
		molecule.centrar ();
		molecule.ponconec ();
		if (terminator == HYDROGEN) {
			molecule.cierraH ();
			molecule.ponconec ();
		} else if (terminator == NITROGEN) {
			molecule.cierraN ();
			molecule.ponconec ();
		}
	}

	public String pdb() {
		return molecule.pdb();
	}

	public String mmp() {
		return molecule.mmp();
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
