import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import java.text.*;

/*
 * This is the GUI element that we use when we're doing heterojunctions, and is therefore
 * of great interest. The really interesting stuff appears to be in the makemol() method.
 */

public class P2 extends JPanel implements ActionListener, ItemListener
{
	private JButton B1, B2;
	private JPanel c1, c0, c2, ct1, ct2;
	private JScrollPane ctxt2;
	private JTextArea txlog;
	private JLabel l1, l2, l3, l4, l5, l6;
	private JTextField t1, t2, t3, t4, t5, t6;
	private Mira3D pan3D;
	private JCheckBox cb1, cb2, cb3;
	private GLienzo2 gl;
	private JComboBox combo;
	private boolean bst, atn, hbk;
	public MoleculaT HJ;
	formato fo = new formato (8, "#0.000");
	formato fd = new formato (8, "###0.000");	//para los doble precision
	formato fi = new formato (5, "#####");	//para los enteros

	private final double GAP = 15.0;	//val absoluto de zona de deformacion
	private final double GMI = 2.0;	//val absoluto de zona de no deformacion


	public P2 ()
	{

		HJ = new MoleculaT ();
		pan3D = new Mira3D ();

		setLayout (new BorderLayout ());
		c0 = new JPanel ();
		c0.setLayout (new BorderLayout ());
		c1 = new JPanel ();
		c1.setLayout (new GridLayout (4, 2, 5, 5));
		c2 = new JPanel ();
		c2.setLayout (new GridLayout (5, 1, 5, 5));

		Box ct1 = Box.createHorizontalBox ();
		Box ct2 = Box.createHorizontalBox ();

		  ct1.setBorder (BorderFactory.
				 createCompoundBorder (BorderFactory.
						       createTitledBorder ("1st Tube:\nIndices and length. (\u212B)"), BorderFactory.createEtchedBorder (1)));
		  ct2.setBorder (BorderFactory.
				 createCompoundBorder (BorderFactory.
						       createTitledBorder ("2nd Tube:\nIndices and length. (\u212B)"), BorderFactory.createEtchedBorder (1)));

		  txlog = new JTextArea ("", 6, 15);
		  ctxt2 = new JScrollPane (txlog);
		  txlog.setEditable (false);
		Font fon = new Font ("Courier", 1, 12);
		  txlog.setFont (fon);

		  B1 = new JButton ("CREATE");
		  B1.addActionListener (this);
		  B2 = new JButton ("CREATE RANDOM");
		  B2.addActionListener (this);

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

		  combo = new JComboBox ();
		  combo.addItem ("No endings");
		  combo.addItem ("Hydrogen");
		  combo.addItem ("Nitrogen");
		//Numeros random
		//int rand1=(int)(25*Math.random());
		//int rand2=(int)(25*Math.random());
		//int rand3=(int)(25*Math.random());
		//int rand4=(int)(25*Math.random());

		  l1 = new JLabel (" i= ");
		  t1 = new JTextField ("5");
		  t1.addActionListener (this);
		  l2 = new JLabel (" j= ");
		  t2 = new JTextField ("5");
		  t2.addActionListener (this);
		  l3 = new JLabel (" l= ");
		  t3 = new JTextField ("20");
		  t3.addActionListener (this);
		  l4 = new JLabel (" i= ");
		  t4 = new JTextField ("10");
		  t4.addActionListener (this);
		  l5 = new JLabel (" j= ");
		  t5 = new JTextField ("10");
		  t5.addActionListener (this);
		  l6 = new JLabel (" l= ");
		  t6 = new JTextField ("20");
		  t6.addActionListener (this);

		  ct1.add (l1);
		  ct1.add (t1);
		  ct1.add (l2);
		  ct1.add (t2);
		  ct1.add (l3);
		  ct1.add (t3);
		  ct2.add (l4);
		  ct2.add (t4);
		  ct2.add (l5);
		  ct2.add (t5);
		  ct2.add (l6);
		  ct2.add (t6);



		  gl = new GLienzo2 ();
		  gl.redraw (Integer.parseInt (t1.getText ().trim ()),
			     Integer.parseInt (t2.getText ().trim ()),
			     Integer.parseInt (t4.getText ().trim ()), Integer.parseInt (t5.getText ().trim ()), true);
		  gl.setPreferredSize (new Dimension (150, 150));

		Box b2 = Box.createVerticalBox ();
		  b2.setPreferredSize (new Dimension (220, 200));
		  b2.add (ct1);
		  b2.add (ct2);
		  b2.add (combo);
		  b2.add (B1);
		//b2.add(B2);

		  c2.setMaximumSize (new Dimension (300, 300));

		  c0.add (b2, BorderLayout.NORTH);
		//c0.add(gl, BorderLayout.CENTER );
		  c0.add (cv, BorderLayout.SOUTH);
		  add (c0, BorderLayout.WEST);
		  add (ctxt2, BorderLayout.SOUTH);
		  add (pan3D, BorderLayout.CENTER);
		  ctxt2.setVerticalScrollBarPolicy (JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		  ctxt2.setBorder (BorderFactory.
				   createCompoundBorder (BorderFactory.createTitledBorder ("Generation Log."), BorderFactory.createEtchedBorder (1)));
		  HJ = new MoleculaT ();
	}

	public void actionPerformed (ActionEvent ev)
	{
		String etiq = ev.getActionCommand ();

		int i1, i2, j1, j2;
		if (etiq == "CREATE") {

			try {
				i1 = Integer.parseInt (t1.getText ().trim ());
				j1 = Integer.parseInt (t2.getText ().trim ());
				i2 = Integer.parseInt (t4.getText ().trim ());
				j2 = Integer.parseInt (t5.getText ().trim ());
			}

			catch (Exception e) {
				JOptionPane.showMessageDialog (null, "Stop: wrong input", "Stop", 0);
				return;
			}
		} else if (etiq == "CREATE RANDOM") {
			i1 = (int) (25 * Math.random ());
			t1.setText ("" + i1);
			j1 = (int) (25 * Math.random ());
			t2.setText ("" + j1);
			i2 = (int) (25 * Math.random ());
			t4.setText ("" + i2);
			j2 = (int) (25 * Math.random ());
			t5.setText ("" + j2);
		} else {
			i1 = 2;
			j1 = 2;
			i2 = 4;
			j2 = 4;
		}
		gl.redraw (i1, j1, i2, j2, true);

		makemol ();
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



	public void makemol ()
	{

		boolean ejes = false;
		boolean vecs = false;
		boolean despleg = false;

		Nanotubo NTA, NTB;	//ambos tubos
		String td1, td2;	//dos cadenas etiquetan primer y segundo defecto
		HJ.vaciar ();


		int n = 0, m = 0;	//indices de la cinta strip

		int i1 = 0;
		int i2 = 0;
		int j1 = 0;
		int j2 = 0;
		double lent1 = 0;
		double lent2 = 0;

		// Get parameters from the GUI.
		try {
			i1 = Integer.parseInt (t1.getText ().trim ());	//pillamos indice se tubos
			j1 = Integer.parseInt (t2.getText ().trim ());
			i2 = Integer.parseInt (t4.getText ().trim ());
			j2 = Integer.parseInt (t5.getText ().trim ());
			lent1 = Double.parseDouble (t3.getText ().trim ());
			lent2 = Double.parseDouble (t6.getText ().trim ());
		}

		catch (NumberFormatException e) {
			JOptionPane.showMessageDialog (null, "Stop: wrong input", "Stop", 0);
			return;
		}


		HJ.setInfo ("(" + i1 + "," + j1 + ")-(" + i2 + "," + j2 + ") Nanotube Heterojunction with lengths " + lent1 + " and " + lent2 + " A.");
		txlog.setText
			("---------------------------------------------------------\n"
			 + " GENERATION OF A (" + i1 + "," + j1 + ")-(" + i2 +
			 "," + j2 + ") CARBON NANOTUBE JUNCTION\n" + "---------------------------------------------------------\n");


		if (i1 == 0 && j1 == 0) {
			JOptionPane.showMessageDialog (null, "Error: 1st tube's indices are incorrect", "Error", JOptionPane.ERROR_MESSAGE);
			return;
		}
		if (i2 == 0 && j2 == 0) {
			JOptionPane.showMessageDialog (null, "Error: 2nd tube's indices are incorrect", "Error", JOptionPane.ERROR_MESSAGE);
			return;
		}



		// If the user put in any negative parameters, fix that now
		boolean cambio1 = false;  // cambio --> change
		boolean cambio2 = false;
		for (; (i1 < 0) || (j1 < 0);) {
			int i1n = -j1;
			int j1n = i1 + j1;
			i1 = i1n;
			j1 = j1n;
			cambio1 = true;
		}
		for (; (i2 < 0) || (j2 < 0);) {
			int i2n = -j2;
			int j2n = i2 + j2;
			i2 = i2n;
			j2 = j2n;
			cambio2 = true;
		}

		if (cambio1) {
			JOptionPane.showMessageDialog (null,
						       "Warning: Indices of 1st tube automatically translated to ("
						       + i1 + "," + j1 + ")", "Warning", JOptionPane.INFORMATION_MESSAGE);
			t1.setText ("" + i1);
			t2.setText ("" + j1);
		}
		if (cambio2) {
			JOptionPane.showMessageDialog (null,
						       "Warning: Indices of 2nd tube automatically translated to ("
						       + i2 + "," + j2 + ")", "Warning", JOptionPane.INFORMATION_MESSAGE);
			t4.setText ("" + i2);
			t5.setText ("" + j2);
		}


		// Check validity conditions on parameters
		if (i2 == i1 && j2 == j1) {
			JOptionPane.showMessageDialog (null, "Error: Indices of both tubes coincide", "Error", JOptionPane.ERROR_MESSAGE);
			return;
		}
		if (i2 < 2 && j2 < 2) {
			JOptionPane.showMessageDialog (null, "Stop: 2nd tube too narrow", "Stop", 0);
			return;
		}
		if (i1 < 2 && j1 < 2) {
			JOptionPane.showMessageDialog (null, "Stop: 1st tube too narrow", "Stop", 0);
			return;
		}



		boolean creciente = true;
		int c = 0;

		// Create the two nanotubes to be joined
		NTA = new Nanotubo (i1, j1, 2.46);
		NTB = new Nanotubo (i2, j2, 2.46);

		int guess = naproxatomos (NTA.radio (), lent1, NTB.radio (),
					  lent2);

		// Warn if structure is large enough to be potentially problematic
		if (guess > 6000) {
			JOptionPane.showMessageDialog (null, "Structure will have more than 6000 Atoms. Process stopped.", "STOP", 0);
			return;
		} else if (guess > 4000) {
			int sale = JOptionPane.showConfirmDialog (null,
								  "Structure will have more than 4000 Atoms. Continue at your own risk",
								  "Warning", 0);
			if (sale == 1)
				return;
		} else if (guess > 2000) {
			JOptionPane.showMessageDialog (null, "Large Structure: using low-consumption display.", "Big molecule", 1);
			pan3D.setlrd ();
		} else
			pan3D.unsetlrd ();

		// The actual algorithm starts here
		int nad = j2 - j1;
		int mad = i1 - i2 + j1 - j2;
		int nbd = i1 + j1 - j2;
		int mbd = i2 - i1 + j2;


		int nai = i1 - i2 + j1 - j2;
		int mai = i2 - i1;
		int nbi = i2 - j1 + j2;
		int mbi = j1 - i2 + i1;

		if (NTA.radio () < NTB.radio ()) {
			creciente = true;
			c = -1;
			n = nai;
			m = mai;
			td1 = "heptagon";
			td2 = "pentagon";
		} else {
			creciente = false;
			c = 1;
			n = nad;
			m = mad;
			td1 = "pentagon";
			td2 = "heptagon";
		}


		txlog.setText (txlog.getText () + "\nThe " + td1 + " comes first, and the " + td2 + " is at (" + n + "," + m + "). ");

		if (!creciente)
			txlog.setText (txlog.getText () + "The strip is (" + nad + "," + mad + ")[1,0];(" + nbd + "," + mbd + ")[-1,0];");
		else
			txlog.setText (txlog.getText () + "The strip is (" + nai + "," + mai + ")[1,0];(" + nbi + "," + mbi + ")[-1,0];");




		MoleculaB conoplano = new MoleculaB ();


		double A = 2.46;
		double r3 = Math.sqrt (3);



		pto2D pA = new pto2D (0.0, 0.0);
		pto2D pB = new pto2D (A * (i1 + j1 * 0.5), A * r3 / 2 * j1);
		pto2D pC = new pto2D (A * (n + m * 0.5), A * r3 / 2 * m);
		pto2D pD = new pto2D (A * (n + i2 + (m + j2) * 0.5),
				      A * r3 / 2 * (m + j2));


		// detectanconc --> they detect conc?
		int nconc = detectanconc (pB, pA, pC, pD);

		if (nconc == 0 || nconc == 1) {
			txlog.setText (txlog.getText () + "\n\nHeterojunction requires a cone");
			txlog.setText (txlog.getText () + ". Starting cone determination:");

//DETECTAMOS EL RETCTANGULO que contiene el trapezoide magico
//WE DETECTED the RECTANGLE that contains the magical trapezoid 
			double maxcx = Math.max (Math.max (pA.x, pB.x),
						 Math.max (pC.x, pD.x));
			double maxcy = Math.max (Math.max (pA.y, pB.y),
						 Math.max (pC.y, pD.y));
			double mincx = Math.min (Math.min (pA.x, pB.x),
						 Math.min (pC.x, pD.x));
			double mincy = Math.min (Math.min (pA.y, pB.y),
						 Math.min (pC.y, pD.y));
			if (despleg) {
				HJ.addVert (pA, 8, Color.black);
				HJ.addVert (pB, 8, Color.black);
				HJ.addVert (pC, 8, Color.black);
				HJ.addVert (pD, 8, Color.black);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 2);
				HJ.conecta (HJ.nvert () - 2, HJ.nvert () - 4);
				HJ.conecta (HJ.nvert () - 4, HJ.nvert () - 3);
				HJ.conecta (HJ.nvert () - 3, HJ.nvert () - 1);
			}

			double sty = (int) ((mincy - 2.0 * A * r3) / (A * r3)) * A * r3;
			double stx = (int) ((mincx - 2.0 * A) / (A)) * A;


			for (double cely = sty; cely <= (maxcy - mincy) + 4 * A * r3; cely = cely + A * r3)
				for (double celx = stx; celx <= (maxcx - mincx) + 4 * A; celx = celx + A) {
					pto2D at1 = new pto2D (celx,
							       cely + A / r3);
					pto2D at2 = new pto2D (celx,
							       cely - A / r3);
					pto2D at3 = new pto2D (celx + A / 2,
							       cely + A / 2 / r3);
					pto2D at4 = new pto2D (celx + A / 2,
							       cely - A / 2 / r3);
					if (at1.dentro4l (pB, pA, pC, pD)) {
						conoplano.addVert (at1, 6);
						if (despleg)
							HJ.addVert (at1, 6, Color.orange);
					}	//
					if (at2.dentro4l (pB, pA, pC, pD)) {
						conoplano.addVert (at2, 6);
						if (despleg)
							HJ.addVert (at2, 6, Color.orange);
					}	//
					if (at3.dentro4l (pB, pA, pC, pD)) {
						conoplano.addVert (at3, 6);
						if (despleg)
							HJ.addVert (at3, 6, Color.orange);
					}	//
					if (at4.dentro4l (pB, pA, pC, pD)) {
						conoplano.addVert (at4, 6);
						if (despleg)
							HJ.addVert (at4, 6, Color.orange);
					}	//
				}

			pto2D pV = null;

			double fc = 0;
			if (creciente) {
				pV = new pto2D (A * (i1 + j1 - i1 * 0.5), -A * r3 / 2.0 * i1);
				fc = -1;
			} else {
				pV = new pto2D (A * (-j1 + (i1 + j1) * 0.5), A * r3 / 2.0 * (i1 + j1));
				fc = 1;
			}

			double angucono = Math.asin (0.5 / Math.PI);
			double db = pV.dista (pA);

			for (int i = 0; i < conoplano.nvert (); i++) {
				pto3D ptp = conoplano.vert (i);
				double di = pV.dista (ptp);
				double an;
				if (creciente)
					an = pA.menos (pV).a2D ().angulocwhasta (ptp.menos (pV).a2D ());
				else
					an = pA.menos (pV).a2D ().anguloccwhasta (ptp.menos (pV).a2D ());

				double TX = di * Math.sin (angucono) * Math.cos (6.0 * an);
				double TY = di * Math.sin (angucono) * Math.sin (6.0 * an);
				double TZ = fc * (db - di) * Math.cos (angucono);

				pto3D ptemp = new pto3D (TX, TY, TZ);
				if (!despleg)
					if (!HJ.ocupa1 (ptemp))
						HJ.addVert (ptemp, 6);

			}
			txlog.setText (txlog.getText () + "\nThe cone is completed with " + HJ.nvert () + " atoms");


			if (lent1 <= 15. || lent2 <= 15.)
				txlog.setText (txlog.getText () + "\n\nWarning: Open ends remain deformed: Increase length up to 15 Angstrom.");

			double curvaP = 0.22;
			double curvaH = 0.22;

			pto3D lt1 = new pto3D ();
			pto3D lt2 = new pto3D ();

			txlog.setText (txlog.getText () + "\n\nDetermination of both tubes. ");


			double anT2;
			if (creciente)
				anT2 = pA.menos (pV).a2D ().angulocwhasta (pC.menos (pV).a2D ());
			else
				anT2 = pA.menos (pV).a2D ().anguloccwhasta (pC.menos (pV).a2D ());
			double dhT2 = anT2 * 6.0;
			txlog.setText (txlog.getText () + " Tubes 1 and 2 form a dihedral angle of " + (int) (dhT2 * 180. / Math.PI) + " deg.");
//y creamos los vec --> and we create the vector
			if (!creciente) {
				lt1 = new pto3D (Math.sin (curvaP), 0, Math.cos (curvaP));
				lt2 = new pto3D (Math.sin (curvaH) * Math.cos (dhT2), Math.sin (curvaH) * Math.sin (dhT2), Math.cos (curvaH));
			} else {
				lt1 = new pto3D (-Math.sin (curvaH), 0, Math.cos (curvaH));
				lt2 = new pto3D (-Math.sin (curvaP) * Math.cos (dhT2), -Math.sin (curvaP) * Math.sin (dhT2), Math.cos (curvaP));
			}

			double ratio1x = lt1.x / lt1.z;
			double ratio1y = lt1.y / lt1.z;
			double ratio2x = lt2.x / lt2.z;
			double ratio2y = lt2.y / lt2.z;

			txlog.setText (txlog.getText () + "\n\nStarting 1st tube construction. ");

			pto2D pAcm1 = new pto2D (0.0, 0.0);
			pto2D pBcm1 = new pto2D (A * (i1 + j1 * 0.5),
						 A * r3 / 2 * j1);
//determinamos el vector transpuesto --> we determine the transposed vector
			pto2D pTcm1 = new pto2D (pBcm1.y, -pBcm1.x);
			pto3D pTcm1corto = pTcm1.aversor ().escala (lent1);
			pto2D pCcm1 = pAcm1.mas (pTcm1corto).a2D ();
			pto2D pDcm1 = pBcm1.mas (pTcm1corto).a2D ();

			txlog.setText (txlog.getText () + "Filling 1st tube planar projection ");

			double maxcx1 = Math.max (Math.max (pAcm1.x, pBcm1.x),
						  Math.max (pCcm1.x, pDcm1.x));
			double maxcy1 = Math.max (Math.max (pAcm1.y, pBcm1.y),
						  Math.max (pCcm1.y, pDcm1.y));
			double mincx1 = Math.min (Math.min (pAcm1.x, pBcm1.x),
						  Math.min (pCcm1.x, pDcm1.x));
			double mincy1 = Math.min (Math.min (pAcm1.y, pBcm1.y),
						  Math.min (pCcm1.y, pDcm1.y));

			MoleculaB cachotubo1 = new MoleculaB ();
			int sty1 = (int) Math.round ((mincy1 - 3.0) / A / r3);
			int stx1 = (int) Math.round ((mincx1 - 3.0) / A);
			int enx1 = (int) Math.round ((maxcx1 + 3.0) / A);
			int eny1 = (int) Math.round ((maxcy1 + 3.0) / A / r3);

			int nummax1 = (int) (6 * (maxcx1 - mincx1) * (maxcy1 - mincy1) / A / A / r3);
			int[][] posis1 = new int[3][nummax1];
			int indi1 = 0;

			for (int cely = sty1; cely <= eny1; cely++)	//recorrido vertical --> vertical route
				for (int celx = stx1; celx <= enx1; celx++)	//recorrido horizontal
				{
					pto2D at1 = new pto2D (celx * A,
							       cely * A * r3 + A / r3);
					pto2D at2 = new pto2D (celx * A,
							       cely * A * r3 - A / r3);
					pto2D at3 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 + A / 2.0 / r3);
					pto2D at4 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 - A / 2.0 / r3);
					if (at1.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
						cachotubo1.addVert (at1, 6);
						posis1[0][indi1] = 1;
						posis1[1][indi1] = celx - cely;
						posis1[2][indi1] = cely * 2;
						indi1++;
						if (despleg)
							HJ.addVert (at1, 6, Color.blue);
					}	//
					if (at2.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
						cachotubo1.addVert (at2, 6);
						posis1[0][indi1] = 2;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 2;
						indi1++;
						if (despleg)
							HJ.addVert (at2, 6, Color.blue);
					}	//
					if (at3.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
						cachotubo1.addVert (at3, 6);
						posis1[0][indi1] = 2;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 1;
						indi1++;
						if (despleg)
							HJ.addVert (at3, 6, Color.blue);
					}	//
					if (at4.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
						cachotubo1.addVert (at4, 6);
						posis1[0][indi1] = 1;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 1;
						indi1++;
						if (despleg)
							HJ.addVert (at4, 6, Color.blue);
					}	//
				}

			txlog.setText (txlog.getText () + "with " + cachotubo1.nvert () + " atoms.");


			double dihedroT1 = 0;

			double da1 = pV.dista (pA);
			pto3D pAm1 = pA.ptomediocon (pB);
			double dop1 = pV.dista (pAm1);
			// proyectado --> projected
			pto3D pdefproy1 = new pto3D (da1 * Math.sin (angucono), 0, fc * (db - da1) * Math.cos (angucono));	//P proyectado 
			pto3D odefproy1 = new pto3D (-dop1 * Math.sin (angucono), 0, fc * (db - dop1) * Math.cos (angucono));	//P proyectado
			pto3D pstart1 = pdefproy1.ptomediocon (odefproy1);
			pto3D pori1 = pdefproy1.menos (pstart1);

			if (ejes) {
				HJ.addVert (pdefproy1, 9);
				HJ.addVert (odefproy1, 8);
				HJ.addVert (pstart1.mas (lt1.escala (-20)), 7);
				HJ.addVert (pstart1, 6);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 2);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 3);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 4);
			}

			for (int i = 0; i < cachotubo1.nvert (); i++) {
				pto3D ptp = cachotubo1.vert (i);
				pto2D puntoproy = ptp.proyeccplano (pTcm1corto).a2D ();
				double diz = ptp.proyeccplano (pBcm1).modulo ();

				double di = pV.dista (puntoproy);
				double an;
				if (creciente) {
					an = pA.menos (pV).a2D ().angulocwhasta (puntoproy.menos (pV).a2D ());
				} else {
					an = pA.menos (pV).a2D ().anguloccwhasta (puntoproy.menos (pV).a2D ());
				}

				double TX = di * Math.sin (angucono) * Math.cos (an * 6.0) - ratio1x * diz;
				// pero para el ajuste del primer tubo, es negativo
				// but for the adjustment of the first tube, it is negative
				double TY = di * Math.sin (angucono) * Math.sin (an * 6.0) - ratio1y * diz;

				double TZ = fc * (db - di) * Math.cos (angucono) - diz;

				pto3D ptemp = new pto3D (TX, TY, TZ);

				int tipoat = posis1[0][i];
				int celdai = posis1[1][i];
				int celdaj = posis1[2][i];
				double co = 0.0;

				if (diz < GMI)
					co = 0.0;
				else if (diz > GAP)
					co = 1.0;
				else
					co = (diz - GMI) / (GAP - GMI);



				pto3D pperf = aproxNT (ptemp,	//Punto a aproximar
						       tipoat,
						       celdai, celdaj,
						       pstart1,
						       i1, j1,
						       lt1,
						       pori1,
						       co);


				if (!despleg)
					if (!HJ.ocupa1 (pperf))
						HJ.addVert (pperf, 6, Color.gray);



			}

//TEST
			if (vecs) {
				pto3D pbaseO = aproxNT (new pto3D (0, 0, 0), 1, 0, 0,
							pstart1, i1, j1, lt1,
							new pto3D (1, 0, 0), 1);
				pto3D pbase1 = aproxNT (new pto3D (0, 0, 0), 1, 1, 0,
							pstart1, i1, j1, lt1,
							new pto3D (1, 0, 0), 1);
				pto3D pbase2 = aproxNT (new pto3D (0, 0, 0), 1, 0, 1,
							pstart1, i1, j1, lt1,
							new pto3D (1, 0, 0), 1);
				HJ.addVert (pbaseO, 6);
				HJ.addVert (pbase1, 7);
				HJ.addVert (pbase2, 8);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 3);
				HJ.conecta (HJ.nvert () - 2, HJ.nvert () - 3);
			}


			txlog.setText (txlog.getText () + "\nStarting 2nd tube construction. ");

			pto2D pAcm2 = pC.clona ().a2D ();
			pto2D pBcm2 = pD.clona ().a2D ();

			pto2D pTcm2 = new pto2D (-(pBcm2.y - pAcm2.y),
						 pBcm2.x - pAcm2.x);
			pto3D pTcm2corto = pTcm2.aversor ().escala (lent2);
			pto2D pCcm2 = pAcm2.mas (pTcm2corto).a2D ();
			pto2D pDcm2 = pBcm2.mas (pTcm2corto).a2D ();

			double maxcx2 = Math.max (Math.max (pAcm2.x, pBcm2.x),
						  Math.max (pCcm2.x, pDcm2.x));
			double maxcy2 = Math.max (Math.max (pAcm2.y, pBcm2.y),
						  Math.max (pCcm2.y, pDcm2.y));
			double mincx2 = Math.min (Math.min (pAcm2.x, pBcm2.x),
						  Math.min (pCcm2.x, pDcm2.x));
			double mincy2 = Math.min (Math.min (pAcm2.y, pBcm2.y),
						  Math.min (pCcm2.y, pDcm2.y));


			txlog.setText (txlog.getText () + "Filling 2nd tube planar projection ");

			MoleculaB cachotubo2 = new MoleculaB ();


			int sty2 = (int) Math.round ((mincy2 - 3.0) / A / r3);
			int stx2 = (int) Math.round ((mincx2 - 3.0) / A);
			int enx2 = (int) Math.round ((maxcx2 + 3.0) / A);
			int eny2 = (int) Math.round ((maxcy2 + 3.0) / A / r3);

			int nummax2 = (int) (6 * (maxcx2 - mincx2) * (maxcy2 - mincy2) / A / A / r3);
			int[][] posis2 = new int[3][nummax2];
			int indi2 = 0;

			for (int cely = sty2; cely <= eny2; cely++)	//recorrido vertical, con
				for (int celx = stx2; celx <= enx2; celx++)	//recorrido horizontal
				{
					pto2D at1 = new pto2D (celx * A,
							       cely * A * r3 + A / r3);
					pto2D at2 = new pto2D (celx * A,
							       cely * A * r3 - A / r3);
					pto2D at3 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 + A / 2.0 / r3);
					pto2D at4 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 - A / 2.0 / r3);
					if (at1.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
						cachotubo2.addVert (at1, 6);
						posis2[0][indi2] = 1;
						posis2[1][indi2] = celx - cely;
						posis2[2][indi2] = cely * 2;
						indi2++;
						if (despleg)
							HJ.addVert (at1, 6, Color.red);
					}	//
					if (at2.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
						cachotubo2.addVert (at2, 6);
						posis2[0][indi2] = 2;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 2;
						indi2++;
						if (despleg)
							HJ.addVert (at2, 6, Color.red);
					}	//
					if (at3.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
						cachotubo2.addVert (at3, 6);
						posis2[0][indi2] = 2;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 1;
						indi2++;
						if (despleg)
							HJ.addVert (at3, 6, Color.red);
					}	//
					if (at4.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
						cachotubo2.addVert (at4, 6);
						posis2[0][indi2] = 1;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 1;
						indi2++;
						if (despleg)
							HJ.addVert (at4, 6, Color.red);
					}	//
				}


			txlog.setText (txlog.getText () + "with " + cachotubo2.nvert () + " atoms.");

			double dc2 = pV.dista (pC);
			pto3D pCm2 = pC.ptomediocon (pD);
			double dop2 = pV.dista (pCm2);
			pto3D pdefproy2 = new pto3D (dc2 * Math.sin (angucono) * Math.cos (dhT2),
						     dc2 * Math.sin (angucono) * Math.sin (dhT2),
						     fc * (db - dc2) * Math.cos (angucono));	//P proyectado 
			pto3D odefproy2 = new pto3D (-dop2 * Math.sin (angucono) * Math.cos (dhT2)
						     ,
						     -dop2 * Math.sin (angucono) * Math.sin (dhT2)
						     , fc * (db - dop2) * Math.cos (angucono));	//P proyectado 

			pto3D pstart2 = pdefproy2.ptomediocon (odefproy2);

			pto3D pori2 = pdefproy2.menos (pstart2);

			if (ejes) {
				HJ.addVert (pdefproy2, 9);
				HJ.addVert (odefproy2, 8);
				HJ.addVert (pstart2.mas (lt2.escala (20)), 7);
				HJ.addVert (pstart2, 6);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 2);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 3);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 4);
			}
//////////////////////////////

			for (int i = 0; i < cachotubo2.nvert (); i++) {
				pto3D ptp = cachotubo2.vert (i).menos (pAcm2);	//ha de ser relativo 
				pto2D puntoproy = ptp.proyeccplano (pTcm2corto).mas (pAcm2).a2D ();	//ha de ser respecto al origen
				double diz = ptp.proyeccplano (pBcm2.menos (pAcm2)).modulo ();	//distancia al vector quiral 2, 
				double di = pV.dista (puntoproy);

				double an;
				if (creciente) {
					an = pA.menos (pV).a2D ().angulocwhasta (puntoproy.menos (pV).a2D ());
				} else {
					an = pA.menos (pV).a2D ().anguloccwhasta (puntoproy.menos (pV).a2D ());
				}

				double TX = di * Math.sin (angucono) * Math.cos (6.0 * an) + diz * ratio2x;	//diz ahora tiene que ser ositivo
				double TY = di * Math.sin (angucono) * Math.sin (6.0 * an) + diz * ratio2y;
				double TZ = fc * (db - di) * Math.cos (angucono) + diz;	// y aqui tambien positivo, por eso hay que restarla

				pto3D ptemp = new pto3D (TX, TY, TZ);

				int tipoat = posis2[0][i];
				int celdai = posis2[1][i] - n;
				int celdaj = posis2[2][i] - m;
				double co = 0.0;

				if (diz < GMI)
					co = 0.0;
				else if (diz > GAP)
					co = 1.0;	//ES el Gap de AProximacion;
				else
					co = (-diz + GMI) / (-GAP + GMI);


				pto3D pperf = aproxNT (ptemp,	//Punto a aproximar
						       tipoat,
						       celdai, celdaj,
						       pstart2,
						       i2, j2,
						       lt2,
						       pori2,
						       co);

				if (!despleg)
					if (!HJ.ocupa1 (pperf))
						HJ.addVert (pperf, 6, Color.gray);


			}

			if (vecs) {
				pto3D pbaseO2 = aproxNT (new pto3D (0, 0, 0), 1, 0, 0,
							 pstart2, i2, j2, lt2, pori2,
							 1);
				pto3D pbase12 = aproxNT (new pto3D (0, 0, 0), 1, 1, 0,
							 pstart2, i2, j2, lt2, pori2,
							 1);
				pto3D pbase22 = aproxNT (new pto3D (0, 0, 0), 1, 0, 1,
							 pstart2, i2, j2, lt2, pori2,
							 1);
				HJ.addVert (pbaseO2, 6);
				HJ.addVert (pbase12, 7);
				HJ.addVert (pbase22, 8);
				HJ.conecta (HJ.nvert () - 1, HJ.nvert () - 3);
				HJ.conecta (HJ.nvert () - 2, HJ.nvert () - 3);
			}
//represtentacion vec base




			txlog.setText (txlog.getText () + "\n\nStructure (" +
				       i1 + "," + j1 + ")-(" + i2 + "," + j2 + ") completed with " + HJ.nvert () + " atoms");
		} else {

			txlog.setText (txlog.getText () + "\nHeterojunction cannot be formed with a cone. Using alternative algorithm.");


			pto2D Qad = new pto2D (A * (nad + mad * 0.5),
					       A * r3 / 2 * mad);
			pto2D Qai = new pto2D (A * (nai + mai * 0.5),
					       A * r3 / 2 * mai);

			pto2D pA1 = new pto2D (0, 0);
			pto2D pB1 = new pto2D (A * (i1 + j1 * 0.5),
					       A * r3 / 2 * j1);

			double angulod = pB1.angulocong (Qad);
			double anguloi = pB1.angulocong (Qai);

			boolean directo = true;

			if ((angulod < 90.) && (anguloi > 90.)) {
				directo = true;
				n = nad;
				m = mad;
			} else if ((anguloi < 90.) && (angulod > 90.)) {
				directo = false;
				n = nai;
				m = mai;
			} else
				JOptionPane.showMessageDialog (null, "Warning: Unexpected geometry!!", "Warning", JOptionPane.INFORMATION_MESSAGE);

			pto2D pC1 = new pto2D (A * (n + m * 0.5), A * r3 / 2 * m);

			pto2D pA2 = new pto2D (0, 0);
			pto2D pB2 = new pto2D (A * (i2 + j2 * 0.5),
					       A * r3 / 2 * j2);

			int nprima = 0;
			int mprima = 0;
			if (directo) {
				nprima = -m;
				mprima = n + m;
			} else {
				nprima = n + m;
				mprima = -n;
			}

			pto2D pC2 = new pto2D (A * (nprima + mprima * 0.5),
					       A * r3 / 2 * mprima);

			double lonmint1 = pC1.proyeccplano (pB1).modulo ();
			double lonmint2 = pC2.proyeccplano (pB2).modulo ();

			double lm = Math.max (lonmint1, lonmint2);

			if (lent1 <= lonmint1) {
				txlog.setText (txlog.getText () +
					       "\n\nWarning: 1st tube's length too short: Augmented automatically to " + (int) (lonmint1 + 1) + " Angstrom.");
				t3.setText ("" + (int) (lonmint1 + 1));
			}
			if (lent2 <= lonmint2) {
				txlog.setText (txlog.getText () +
					       "\n\nWarning: 2nd tube's length too short: Augmented automatically to " + (int) (lonmint2 + 1) + " Angstrom.");
				t6.setText ("" + (int) (lonmint2 + 1));
			}
			if (lent1 <= 15. || lent2 <= 15.)
				txlog.setText (txlog.getText () + "\n\nWarning: Open ends remain deformed: Increase length up to 15 Angstrom.");


//Definimos los puntos que enmarcan los tubos
//We define the points that frame the tubes -- bounding boxes, maybe?
			pto2D vlong1 = new pto2D (pB1.y, -pB1.x);
			pto2D vlong2 = new pto2D (-pB2.y, pB2.x);

			pto2D pA1b = vlong1.aversor ().escala (lent1).a2D ();
			pto2D pB1b = pB1.mas (pA1b);
			pto2D pA2b = vlong2.aversor ().escala (lent2).a2D ();
			pto2D pB2b = pB2.mas (pA2b);
			pto2D pC1p = pC1.proyeccplano (pA1b).a2D ();
			pto2D pC2p = pC2.proyeccplano (pA2b).a2D ();
			pto2D pC1b = pC1p.mas (pA1b);
			pto2D pC2b = pC2p.mas (pA2b);


			double maxcx1 = Math.max (Math.max (pA1.x, pB1.x),
						  Math.max (pA1b.x, pB1b.x));
			double maxcy1 = Math.max (Math.max (pA1.y, pB1.y),
						  Math.max (pA1b.y, pB1b.y));
			double mincx1 = Math.min (Math.min (pA1.x, pB1.x),
						  Math.min (pA1b.x, pB1b.x));
			double mincy1 = Math.min (Math.min (pA1.y, pB1.y),
						  Math.min (pA1b.y, pB1b.y));

			double maxcx2 = Math.max (Math.max (pA2.x, pB2.x),
						  Math.max (pA2b.x, pB2b.x));
			double maxcy2 = Math.max (Math.max (pA2.y, pB2.y),
						  Math.max (pA2b.y, pB2b.y));
			double mincx2 = Math.min (Math.min (pA2.x, pB2.x),
						  Math.min (pA2b.x, pB2b.x));
			double mincy2 = Math.min (Math.min (pA2.y, pB2.y),
						  Math.min (pA2b.y, pB2b.y));

			txlog.setText (txlog.getText () + "\n\nStarting 1st tube construction. ");
			txlog.setText (txlog.getText () + "Filling 1st tube planar projection ");

			MoleculaB cachot1 = new MoleculaB ();


			int sty1 = (int) Math.round ((mincy1 - 3.0) / A / r3);
			int stx1 = (int) Math.round ((mincx1 - 3.0) / A);
			int enx1 = (int) Math.round ((maxcx1 + 3.0) / A);
			int eny1 = (int) Math.round ((maxcy1 + 3.0) / A / r3);

			int nummax1 = (int) (4 * (maxcx1 - mincx1) * (maxcy1 - mincy1) / A / A / r3);
			int[][] posis1 = new int[3][nummax1];
			int indi1 = 0;
			for (int cely = sty1; cely <= eny1; cely++)	//recorrido vertical
				for (int celx = stx1; celx <= enx1; celx++)	//recorrido horizontal
				{
					pto2D at1 = new pto2D (celx * A,
							       cely * A * r3 + A / r3);
					pto2D at2 = new pto2D (celx * A,
							       cely * A * r3 - A / r3);
					pto2D at3 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 + A / 2.0 / r3);
					pto2D at4 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 - A / 2.0 / r3);
					if (at1.dentro4l (pA1, pC1, pC1b, pA1b)
					    || at1.dentro4l (pC1, pB1, pB1b, pC1b)) {
						cachot1.addVert (at1, 6);
						posis1[0][indi1] = 1;
						posis1[1][indi1] = celx - cely;
						posis1[2][indi1] = cely * 2;
						indi1++;
					}	//HJ.addVert(at1,7);
					if (at2.dentro4l (pA1, pC1, pC1b, pA1b)
					    || at2.dentro4l (pC1, pB1, pB1b, pC1b)) {
						cachot1.addVert (at2, 6);
						posis1[0][indi1] = 2;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 2;
						indi1++;
					}	//HJ.addVert(at2,7);
					if (at3.dentro4l (pA1, pC1, pC1b, pA1b)
					    || at3.dentro4l (pC1, pB1, pB1b, pC1b)) {
						cachot1.addVert (at3, 6);
						posis1[0][indi1] = 2;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 1;
						indi1++;
					}	//HJ.addVert(at3,7);
					if (at4.dentro4l (pA1, pC1, pC1b, pA1b)
					    || at4.dentro4l (pC1, pB1, pB1b, pC1b)) {
						cachot1.addVert (at4, 6);
						posis1[0][indi1] = 1;
						posis1[1][indi1] = celx - cely + 1;
						posis1[2][indi1] = cely * 2 - 1;
						indi1++;
					}	//HJ.addVert(at4,7);
				}
			txlog.setText (txlog.getText () + "with " + cachot1.nvert () + " atoms.");

			MoleculaB cachot2 = new MoleculaB ();

			txlog.setText (txlog.getText () + "\nStarting 2nd tube construction. ");
			txlog.setText (txlog.getText () + "Filling 2nd tube planar projection ");

//hay que calcular la macrocelda del comienzo, que debe ser el centro de un hexagono
//it is necessary to calculate the macrocell of the beginning, that must be the center of a hexagon
			int sty2 = (int) Math.round ((mincy2 - 3.0) / A / r3);
			int stx2 = (int) Math.round ((mincx2 - 3.0) / A);
			int enx2 = (int) Math.round ((maxcx2 + 3.0) / A);
			int eny2 = (int) Math.round ((maxcy2 + 3.0) / A / r3);

			int nummax2 = (int) (4 * (maxcx2 - mincx2) * (maxcy2 - mincy2) / A / A / r3);
			int[][] posis2 = new int[3][nummax2];
			int indi2 = 0;
			for (int cely = sty2; cely <= eny2; cely++)	//recorrido vertical,
				for (int celx = stx2; celx <= enx2; celx++)	//recorrido horizontal
				{
					pto2D at1 = new pto2D (celx * A,
							       cely * A * r3 + A / r3);
					pto2D at2 = new pto2D (celx * A,
							       cely * A * r3 - A / r3);
					pto2D at3 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 + A / 2.0 / r3);
					pto2D at4 = new pto2D (celx * A + A / 2.0,
							       cely * A * r3 - A / 2.0 / r3);
					if (at1.dentro4l (pA2, pA2b, pC2b, pC2)
					    || at1.dentro4l (pC2, pC2b, pB2b, pB2)) {
						cachot2.addVert (at1, 6);
						posis2[0][indi2] = 1;
						posis2[1][indi2] = celx - cely;
						posis2[2][indi2] = cely * 2;
						indi2++;
					}	//HJ.addVert(at1,1);
					if (at2.dentro4l (pA2, pA2b, pC2b, pC2)
					    || at2.dentro4l (pC2, pC2b, pB2b, pB2)) {
						cachot2.addVert (at2, 6);
						posis2[0][indi2] = 2;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 2;
						indi2++;
					}	//HJ.addVert(at2,1);
					if (at3.dentro4l (pA2, pA2b, pC2b, pC2)
					    || at3.dentro4l (pC2, pC2b, pB2b, pB2)) {
						cachot2.addVert (at3, 6);
						posis2[0][indi2] = 2;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 1;
						indi2++;
					}	//HJ.addVert(at3,1);
					if (at4.dentro4l (pA2, pA2b, pC2b, pC2)
					    || at4.dentro4l (pC2, pC2b, pB2b, pB2)) {
						cachot2.addVert (at4, 6);
						posis2[0][indi2] = 1;
						posis2[1][indi2] = celx - cely + 1;
						posis2[2][indi2] = cely * 2 - 1;
						indi2++;
					}	//HJ.addVert(at4,1);
				}
			txlog.setText (txlog.getText () + "with " + cachot2.nvert () + " atoms.");


			double C1 = pC1.proyeccplano (pA1b).modulo ();
			double C2 = pC2.proyeccplano (pA2b).modulo ();
			double C = (C1 + C2) * 0.5;
			double B1 = pB1.modulo () - C1;
			double B2 = pB2.modulo () - C2;
			double B = (B1 + B2) * 0.5;


			double AL1 = pB1.angulocwhasta (pC1);
			double AL2 = pB2.angulocwhasta (pC2);	//pueden ser negativos!!
			double Cy1 = C1 * Math.tan (AL1);
			double Cy2 = C2 * Math.tan (AL2);	//y estos tres tambien!!
			double Cy = (Cy1 + Cy2) * 0.5;

			// the sines deformed after the contraction, change!
			double tanAL1d = Cy1 / C;	//los senos deformados /despues de la contraccion, cambian!
			double tanAL2d = Cy2 / C;	//los senos deformados /despues de la contraccion, cambian!
			double tanBE1d = Cy1 / B;	//los senos deformados /despues de la contraccion, cambian!
			double tanBE2d = Cy2 / B;	//los senos deformados /despues de la contraccion, cambian!
			double tanALM = Cy / C;	//los senos deformados /despues de la contraccion, cambian!
			double tanBEM = Cy / B;	//los senos deformados /despues de la contraccion, cambian!


			double ratio11 = tanAL1d - tanALM;
			double ratio12 = tanBE1d - tanBEM;

			double ratio21 = tanAL2d - tanALM;
			double ratio22 = tanBE2d - tanBEM;
			double R = (B + C) / 2.0 / Math.PI;

			// this is an angle in radians
			double curvaP = 0.4;	//esto es un angulillo en radianes
			double curvaH = 0.4;

			pto3D lead11 = new pto3D ();
			pto3D lead12 = new pto3D ();
			pto3D lead21 = new pto3D ();
			pto3D lead22 = new pto3D ();


			double a2to1 = (C / R);	//en radianes
			double sa = Math.sin (a2to1);
			double ca = Math.cos (a2to1);
			double sp = Math.sin (curvaP);
			double cp = Math.cos (curvaP);
			double sh = Math.sin (curvaH);
			double ch = Math.cos (curvaH);

			if (directo) {
				lead11 = new pto3D (sp, 0.0, cp);	//De primer tubo     P
				lead12 = new pto3D (-ca * sh, -sa * sh, ch);	//2ndo def      H
				lead21 = new pto3D (-sp, 0.0, cp);	//De segundo tubo    P
				lead22 = new pto3D (ca * sh, sa * sh, ch);	//                   H
			} else {
				lead11 = new pto3D (-sh, 0.0, ch);	//De primer tubo     H
				lead12 = new pto3D (ca * sp, sa * sp, cp);	//2ndo def      P  
				lead21 = new pto3D (sh, 0.0, ch);	//De segundo tubo    H
				lead22 = new pto3D (-ca * sp, -sa * sp, cp);	//                   P
			}
			pto3D lt1 = lead11.mas (lead12).aversor ();
			pto3D lt2 = lead21.mas (lead22).aversor ();
			double ratio1x = lt1.x / lt1.z;
			double ratio1y = lt1.y / lt1.z;
			double ratio2x = lt2.x / lt2.z;
			double ratio2y = lt2.y / lt2.z;


			for (int i = 0; i < cachot1.nvert (); i++) {
				pto3D p = ((Atomo) cachot1.susatomos.get (i)).vert;
				double xg = p.proyeccplano (pA1b).modulo ();
				double yg = p.proyeccplano (pB1).modulo ();
				if (p.angulocong (pA1b) <= 90.0)
					yg *= -1;

				double xm = xg;
				double ym = yg;
				double htolq = 0;	//Height to linea queb
				if (xg < C1) {
					xm = xg / C1 * C;
					ym = yg + ratio11 * xm;
					htolq = yg + tanAL1d * xm;
				} else {
					xm = C + B - (B1 + C1 - xg) / B1 * B;
					ym = yg + ratio12 * (B + C - xm);
					htolq = yg + tanBE1d * (B + C - xm);
				}
				double xf = R * Math.cos (Math.PI * 2 * xm / (B + C)) + (ratio1x * htolq);	//*ft1+ratio2x*ft2)
				double yf = R * Math.sin (Math.PI * 2 * xm / (B + C)) + (ratio1y * htolq);	//ft1+ratio2y*ft2)*
				double zf = ym;

				pto3D ptemp = new pto3D (xf, yf, zf);
				int tipoat = posis1[0][i];
				int celdai = posis1[1][i];
				int celdaj = posis1[2][i];

				double co = 0.0;
				if (htolq > -GMI)
					co = 0.0;	//ES el Gap MInimo
				else if (htolq < -GAP)
					co = 1.0;	//ES el Gap de AProximacion;
				else
					co = (zf + GMI) / (-GAP + GMI);	//num siempre creciente, den negativo
					// always increasing number, gives negative

				pto3D pperf = aproxNTchap (ptemp,	//Punto a aproximar
							   tipoat,
							   celdai, celdaj,
							   new pto3D (0, 0,
								      0),
							   i1, j1,
							   lt1,
							   new pto3D (R, 0,
								      0),
							   co);
				if (!HJ.ocupa1 (pperf))
					HJ.addVert (pperf, 6);
			}


			for (int i = 0; i < cachot2.nvert (); i++) {
				pto3D p = ((Atomo) cachot2.susatomos.get (i)).vert;
				double xg = p.proyeccplano (pA2b).modulo ();	//OJO a la costura
				double yg = p.proyeccplano (pB2).modulo ();
				if (p.angulocong (pA2b) >= 90.0)
					yg *= -1;	//los que son negativos

				double xm = xg;
				double ym = yg;
				double htolq = 0;
				if (xg < C2) {
					xm = xg / C2 * C;
					ym = yg + ratio21 * xm;
					htolq = yg + tanAL2d * xm;
				} else {
					xm = C + B - (B2 + C2 - xg) / B2 * B;
					ym = yg + ratio22 * (B + C - xm);
					htolq = yg + tanBE2d * (B + C - xm);
				}


				double xf = R * Math.cos (Math.PI * 2 * xm / (B + C)) + (ratio2x * htolq);	//ft1+ratio2x*ft2)*ym
				double yf = R * Math.sin (Math.PI * 2 * xm / (B + C)) + (ratio2y * htolq);	//ft1+ratio2y*ft2)*ym
				double zf = ym;

				pto3D ptemp = new pto3D (xf, yf, zf);

				int tipoat = posis2[0][i];
				int celdai = posis2[1][i];
				int celdaj = posis2[2][i];


				double co = 0.0;
				if (htolq < GMI)
					co = 0.0;	//ES el Gap MInimo
				else if (htolq > GAP)
					co = 1.0;	//ES el Gap de AProximacion;
				else
					co = (zf - GMI) / (GAP - GMI);

				pto3D pperf = aproxNTchap (ptemp,	//Punto a aproximar
							   tipoat,
							   celdai, celdaj,
							   new pto3D (0, 0,
								      0),
							   i2, j2,
							   lt2,
							   new pto3D (R, 0,
								      0),
							   co);


				if (!HJ.ocupa1 (pperf))
					HJ.addVert (pperf, 6, Color.gray);
			}

			txlog.setText (txlog.getText () + "\n\nStructure (" +
				       i1 + "," + j1 + ")-(" + i2 + "," + j2 + ") completed with " + HJ.nvert () + " atoms");

		}


//final y visualizacin
//end and visualization
		HJ.reconec (1.35);
		txlog.setText (txlog.getText () + "\n\nRefining process: ");

		int eliminados = HJ.depuraconec ();
		txlog.setText (txlog.getText () + eliminados + " bonds removed and ");
		int creados = HJ.remataconec ();
		txlog.setText (txlog.getText () + creados + " bonds added.");



		if (combo.getSelectedItem () == "Hydrogen") {
			HJ.cierraH ();
			HJ.ponconec (1.35);
		} else if (combo.getSelectedItem () == "Nitrogen") {
			HJ.cierraN ();
			HJ.ponconec (1.35);
		}
		HJ.centrar ();
		pan3D.cargarMol (HJ);
		pan3D.repaint ();


	}

	public MoleculaT molT ()
	{
		return HJ;
	}

	private int detectanconc (pto2D pA, pto2D pB, pto2D pC, pto2D pD)
	{
		int nconcav = 0;
//el interior esta por debajo del primer trayecto. si tiene4 concavidades, es el complementario del cuadrado.
		pto2D v1 = pC.menos (pB);
		pto2D v2 = pD.menos (pC);
		pto2D v3 = pA.menos (pD);
		pto2D v4 = pB.menos (pA);

		double a1 = v1.angulocwhasta (v2);
		if (a1 < 0 || a1 > Math.PI)
			nconcav++;
		double a2 = v2.angulocwhasta (v3);
		if (a2 < 0 || a2 > Math.PI)
			nconcav++;
		double a3 = v3.angulocwhasta (v4);
		if (a3 < 0 || a3 > Math.PI)
			nconcav++;
		double a4 = v4.angulocwhasta (v1);
		if (a4 < 0 || a4 > Math.PI)
			nconcav++;


		return nconcav;
	}

	private pto3D aproxNT (pto3D pto,	//pto es el punto a aproximar
			       int atotip, int posi, int posj, pto3D origen, int i, int j, pto3D orient, pto3D inicio, double coef)
	{



		pto3D inicioperp = inicio.proyeccplano (orient);
		pto3D vprolonori = inicio.menos (inicioperp);	//a la fuerza es la proy de inidio sobre la orientacion

		pto3D vx = inicioperp.aversor ();
		pto3D vz = orient.aversor ();
		pto3D vy = vz.prodvect (vx);

		Nanotubo NT = new Nanotubo (i, j);

//contamos los pasos tanto radiales como longitudinales correspondientes a posi, posj

		double deltazet = -posi * NT.deltaz2 + posj * NT.deltaz1;	//revisar si el orden esta bien los deltaz son todos positivos, ojo a los signos
		double deltaphi = posi * NT.deltaphi2 + posj * NT.deltaphi1;	//OJO por motivos historicos, 1 se refiere alvect de la red que esta
// por encima de Quiral,


		double deltazetat = atotip * NT.deltazc ();
		double deltaphiat = atotip * NT.deltaphic ();

		double R = NT.radio ();
		double cdp = Math.cos (deltaphi + deltaphiat);
		double sdp = Math.sin (deltaphi + deltaphiat);

//los tres pasitos
		pto3D vv1 = vz.escala (deltazet + deltazetat);
		pto3D vv2 = vx.escala (R * cdp);
		pto3D vv3 = vy.escala (R * sdp);


		return pto.ptopondcon (origen.mas (vv1).mas (vv2).mas (vv3), coef);

	}



	private pto3D aproxNTchap (pto3D pto,	//pto es el punto a aproximar
				   int atotip, int posi, int posj, pto3D origen, int i, int j, pto3D orient, pto3D inicio, double coef)
	{
		pto3D inicioperp = inicio.proyeccplano (orient);
		pto3D vprolonori = inicio.menos (inicioperp);

		origen = origen.mas (vprolonori);

		pto3D vx = inicioperp.aversor ();
		pto3D vz = orient.aversor ();
		pto3D vy = vz.prodvect (vx);

		Nanotubo NT = new Nanotubo (i, j);


		double deltazet = -posi * NT.deltaz2 + posj * NT.deltaz1;
		double deltaphi = posi * NT.deltaphi2 + posj * NT.deltaphi1;



		double deltazetat = atotip * NT.deltazc ();
		double deltaphiat = atotip * NT.deltaphic ();

		double R = NT.radio ();
		double cdp = Math.cos (deltaphi + deltaphiat);	//
		double sdp = Math.sin (deltaphi + deltaphiat);	//

//los tres pasitos
		pto3D vv1 = vz.escala (deltazet + deltazetat);	//
		pto3D vv2 = vx.escala (R * cdp);
		pto3D vv3 = vy.escala (R * sdp);

		return pto.ptopondcon (origen.mas (vv1).mas (vv2).mas (vv3), coef);
	}


	int naproxatomos (double r1, double l1, double r2, double l2)
	{
		double dens = 0.34;	//atomos opr A cuadrado
		double d1 = Math.PI * 2 * r1;
		double d2 = Math.PI * 2 * r2;

		double rr1 = 6.0 * r1;	//Radios del cono proyectado en el plano
		double rr2 = 6.0 * r2;
		double acono = 0.;
		if (r1 > r2)
			acono = Math.PI * (rr1 * rr1 - rr2 * rr2) / 6.0;
		else
			acono = Math.PI * (rr2 * rr2 - rr1 * rr1) / 6.0;

		return (int) (dens * (d1 * l1 + d2 * l2 + acono));

	}


}
