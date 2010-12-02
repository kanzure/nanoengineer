public class W15 extends W1
{
	public W15(int a, int b, double c, int nshells, double sshell, int terminator)
	{
		Nanotubo NT = new Nanotubo (a, b);
		molecule = new MoleculaT ();
		molecule.setInfo ("Multi-walled nanotube with inner indices (" + a + "," + b + ")" + " and " + nshells + " shells");

		if (false) {
			int guess = (int) (NT.radio () * 2 * Math.PI * c * 0.34);
			for (int i = 1; i <= nshells; i++)
				guess = guess + (int) ((NT.radio () + sshell * i) * 2 * Math.PI * c * 0.34);
		}

		double x, xc, y, yc, z, zc;
		for (int i = 1; i * NT.deltaz () <= c; i++) {
			for (int j = 1; j <= NT.d (); j++) {
				x = NT.deltaz () * i;
				xc = NT.deltaz () * i + NT.deltazc ();
				y = NT.radio () * (float) Math.sin (NT.deltaphi () * i + 2 * (float) Math.PI / NT.d () * j);
				yc = NT.radio () * (float) Math.sin (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) Math.PI / NT.d () * j);
				z = NT.radio () * (float) Math.cos (NT.deltaphi () * i + 2 * (float) Math.PI / NT.d () * j);
				zc = NT.radio () * (float) Math.cos (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) Math.PI / NT.d () * j);
				molecule.addVert (x, y, z, 6);
				molecule.addVert (xc, yc, zc, 6);

			}
		}

		double rad1 = 0.01 * (int) (100 * NT.radio ());
		logger.info ("Tube 1 is (" + a + "," + b + "), r=" + rad1);
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
			logger.info ("Tube " + (j + 1) + " is (" + ni + "," + nj + "), r=" + rad);

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
					molecule.addVert (x, y, z, 6);
					molecule.addVert (xc, yc, zc, 6);
				}
			}
		}
		finish(terminator);
	}

	public static void main(String[] argv) {
		int a, b, nshell, terminator;
		double c, sshell;
		a = Integer.parseInt(argv[0]);
		b = Integer.parseInt(argv[1]);
		c = Double.parseDouble(argv[2]);
		nshell = Integer.parseInt(argv[3]);
		sshell = Integer.parseInt(argv[4]);
		terminator = Integer.parseInt(argv[5]);
		W15 w15 = new W15(a, b, c, nshell, sshell, terminator);
		System.out.println(w15.mmp());
		// System.out.println(w1.pdb());
	}
}
