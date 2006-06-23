/* $Id$ */

#include <iostream>
#include <math.h>

#include "W2.h"
#include "pto2D.h"
#include "MoleculaT.h"
#include "Nanotubo.h"

#define min(x,y)   (((x) < (y)) ? (x) : (y))
#define max(x,y)   (((x) > (y)) ? (x) : (y))

typedef int boolean;

W2::W2(int i1, int j1, double lent1, int i2, int j2, double lent2, int terminator) {
    boolean ejes = false;
    boolean vecs = false;
    boolean despleg = false;

    String td1, td2;	//dos cadenas etiquetan primer y segundo defecto

    molecule = MoleculaT ();
    molecule.vaciar ();

    int n = 0, m = 0;	//indices de la cinta strip

    molecule.setInfo (String("(") + i1 + "," + j1 + ")-(" + i2 + "," +
		      j2 + ") Nanotube Heterojunction with lengths " +
		      lent1 + " and " + lent2 + " A.");
    logInfo
	(String("---------------------------------------------------------\n") +
	 " GENERATION OF A (" + i1 + "," + j1 + ")-(" + i2 + "," +
	 j2 + ") CARBON NANOTUBE JUNCTION\n" +
	 "---------------------------------------------------------\n");


    if (i1 == 0 && j1 == 0) {
	std::cerr << "1st tube's indices are incorrect";
	return;
    }
    if (i2 == 0 && j2 == 0) {
	std::cerr << "2nd tube's indices are incorrect";
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
	std::cerr << "Indices of 1st tube automatically translated to ("
		  << i1 << "," << j1 << ")\n";
    }
    if (cambio2) {
	std::cerr << "Indices of 2nd tube automatically translated to ("
		  << i2 << "," << j2 << ")\n";
    }


    // Check validity conditions on parameters
//    if (i2 == i1 && j2 == j1) {
//	std::cerr << "Error: Indices of both tubes coincide";
//	return;
//    }
    if (i2 < 2 && j2 < 2) {
	std::cerr << "Stop: 2nd tube too narrow";
	return;
    }
    if (i1 < 2 && j1 < 2) {
	std::cerr << "Stop: 1st tube too narrow";
	return;
    }



    boolean creciente = true;
    int c = 0;

    // Create the two nanotubes to be joined
    Nanotubo NTA = Nanotubo (i1, j1, 2.46);
    Nanotubo NTB = Nanotubo (i2, j2, 2.46);

    // Warn if structure is large enough to be potentially problematic? Nope.

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
	creciente = true;   // creciente --> flood
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


    logInfo (String("The ") + td1 + " comes first, and the " +
		 td2 + " is at (" + n + "," + m + "). ");

    if (!creciente)
	logInfo (String("The strip is (") + nad + "," +
		     mad + ")[1,0];(" + nbd + "," + mbd + ")[-1,0];");
    else
	logInfo (String("The strip is (") + nai + "," +
		     mai + ")[1,0];(" + nbi + "," + mbi + ")[-1,0];");




    MoleculaB conoplano = MoleculaB ();


    double A = 2.46;
    double r3 = sqrt (3);

    pto2D pA = pto2D (0.0, 0.0);
    pto2D pB = pto2D (A * (i1 + j1 * 0.5), A * r3 / 2 * j1);
    pto2D pC = pto2D (A * (n + m * 0.5), A * r3 / 2 * m);
    pto2D pD = pto2D (A * (n + i2 + (m + j2) * 0.5),
			  A * r3 / 2 * (m + j2));


    // detectanconc --> they detect conc?
    int nconc = detectanconc (pB, pA, pC, pD);

    if (nconc == 0 || nconc == 1) {
	logInfo ("Heterojunction requires a cone");
	logInfo (". Starting cone determination:");

	//DETECTAMOS EL RETCTANGULO que contiene el trapezoide magico
	//WE DETECTED the RECTANGLE that contains the magical trapezoid
	double maxcx = max (max (pA.x, pB.x),
				 max (pC.x, pD.x));
	double maxcy = max (max (pA.y, pB.y),
				 max (pC.y, pD.y));
	double mincx = min (min (pA.x, pB.x),
				 min (pC.x, pD.x));
	double mincy = min (min (pA.y, pB.y),
				 min (pC.y, pD.y));
	if (despleg) {
	    molecule.addVert (pA, 8);
	    molecule.addVert (pB, 8);
	    molecule.addVert (pC, 8);
	    molecule.addVert (pD, 8);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 2);
	    molecule.conecta (molecule.nvert () - 2, molecule.nvert () - 4);
	    molecule.conecta (molecule.nvert () - 4, molecule.nvert () - 3);
	    molecule.conecta (molecule.nvert () - 3, molecule.nvert () - 1);
	}

	double sty = (int) ((mincy - 2.0 * A * r3) / (A * r3)) * A * r3;
	double stx = (int) ((mincx - 2.0 * A) / (A)) * A;


	for (double cely = sty; cely <= (maxcy - mincy) + 4 * A * r3; cely = cely + A * r3)
	    for (double celx = stx; celx <= (maxcx - mincx) + 4 * A; celx = celx + A) {
		pto2D at1 = pto2D (celx,
				       cely + A / r3);
		pto2D at2 = pto2D (celx,
				       cely - A / r3);
		pto2D at3 = pto2D (celx + A / 2,
				       cely + A / 2 / r3);
		pto2D at4 = pto2D (celx + A / 2,
				       cely - A / 2 / r3);
		if (at1.dentro4l (pB, pA, pC, pD)) {
		    conoplano.addVert (at1, 6);
		    if (despleg)
			molecule.addVert (at1, 6);
		}	//
		if (at2.dentro4l (pB, pA, pC, pD)) {
		    conoplano.addVert (at2, 6);
		    if (despleg)
			molecule.addVert (at2, 6);
		}	//
		if (at3.dentro4l (pB, pA, pC, pD)) {
		    conoplano.addVert (at3, 6);
		    if (despleg)
			molecule.addVert (at3, 6);
		}	//
		if (at4.dentro4l (pB, pA, pC, pD)) {
		    conoplano.addVert (at4, 6);
		    if (despleg)
			molecule.addVert (at4, 6);
		}	//
	    }

	pto2D pV;

	double fc = 0;
	if (creciente) {
	    pV = pto2D (A * (i1 + j1 - i1 * 0.5), -A * r3 / 2.0 * i1);
	    fc = -1;
	} else {
	    pV = pto2D (A * (-j1 + (i1 + j1) * 0.5), A * r3 / 2.0 * (i1 + j1));
	    fc = 1;
	}

	double angucono = asin (0.5 / M_PI);
	double db = pV.dista (pA);

	for (int i = 0; i < conoplano.nvert (); i++) {
	    pto3D ptp = conoplano.vert (i);
	    double di = pV.dista (ptp);
	    double an;
	    if (creciente)
		an = pA.menos (pV).a2D ().angulocwhasta (ptp.menos (pV).a2D ());
	    else
		an = pA.menos (pV).a2D ().anguloccwhasta (ptp.menos (pV).a2D ());

	    double TX = di * sin (angucono) * cos (6.0 * an);
	    double TY = di * sin (angucono) * sin (6.0 * an);
	    double TZ = fc * (db - di) * cos (angucono);

	    pto3D ptemp = pto3D (TX, TY, TZ);
	    if (!despleg)
		if (!molecule.ocupa1 (ptemp))
		    molecule.addVert (ptemp, 6);

	}
	logInfo (String("The cone is completed with ") + molecule.nvert () + " atoms");


	if (lent1 <= 15. || lent2 <= 15.)
	    std::cerr << "Open ends remain deformed: Increase length up to 15 Angstrom.\n";

	double curvaP = 0.22;
	double curvaH = 0.22;

	pto3D lt1 = pto3D ();
	pto3D lt2 = pto3D ();

	logInfo (String("Determination of both tubes. "));


	double anT2;
	if (creciente)
	    anT2 = pA.menos (pV).a2D ().angulocwhasta (pC.menos (pV).a2D ());
	else
	    anT2 = pA.menos (pV).a2D ().anguloccwhasta (pC.menos (pV).a2D ());
	double dhT2 = anT2 * 6.0;
	logInfo (String(" Tubes 1 and 2 form a dihedral angle of ") +
		     (int) (dhT2 * 180. / M_PI) + " deg.");
	//y creamos los vec --> and we create the vector
	if (!creciente) {
	    lt1 = pto3D (sin (curvaP), 0, cos (curvaP));
	    lt2 = pto3D (sin (curvaH) * cos (dhT2),
			     sin (curvaH) * sin (dhT2), cos (curvaH));
	} else {
	    lt1 = pto3D (-sin (curvaH), 0, cos (curvaH));
	    lt2 = pto3D (-sin (curvaP) * cos (dhT2),
			     -sin (curvaP) * sin (dhT2), cos (curvaP));
	}

	double ratio1x = lt1.x / lt1.z;
	double ratio1y = lt1.y / lt1.z;
	double ratio2x = lt2.x / lt2.z;
	double ratio2y = lt2.y / lt2.z;

	logInfo (String("Starting 1st tube construction. "));

	pto2D pAcm1 = pto2D (0.0, 0.0);
	pto2D pBcm1 = pto2D (A * (i1 + j1 * 0.5),
				 A * r3 / 2 * j1);
	//determinamos el vector transpuesto --> we determine the transposed vector
	pto2D pTcm1 = pto2D (pBcm1.y, -pBcm1.x);
	pto3D pTcm1corto = pTcm1.aversor ().escala (lent1);
	pto2D pCcm1 = pAcm1.mas (pTcm1corto).a2D ();
	pto2D pDcm1 = pBcm1.mas (pTcm1corto).a2D ();

	logInfo (String("Filling 1st tube planar projection "));

	double maxcx1 = max (max (pAcm1.x, pBcm1.x),
				  max (pCcm1.x, pDcm1.x));
	double maxcy1 = max (max (pAcm1.y, pBcm1.y),
				  max (pCcm1.y, pDcm1.y));
	double mincx1 = min (min (pAcm1.x, pBcm1.x),
				  min (pCcm1.x, pDcm1.x));
	double mincy1 = min (min (pAcm1.y, pBcm1.y),
				  min (pCcm1.y, pDcm1.y));

	MoleculaB cachotubo1 = MoleculaB ();
	int sty1 = (int) round ((mincy1 - 3.0) / A / r3);
	int stx1 = (int) round ((mincx1 - 3.0) / A);
	int enx1 = (int) round ((maxcx1 + 3.0) / A);
	int eny1 = (int) round ((maxcy1 + 3.0) / A / r3);

	int nummax1 = (int) (6 * (maxcx1 - mincx1) * (maxcy1 - mincy1) / A / A / r3);
	int *posis1 = new int[3 * nummax1];
	int indi1 = 0;

	for (int cely = sty1; cely <= eny1; cely++)	//recorrido vertical --> vertical route
	    for (int celx = stx1; celx <= enx1; celx++)	//recorrido horizontal
		{
		    pto2D at1 = pto2D (celx * A,
					   cely * A * r3 + A / r3);
		    pto2D at2 = pto2D (celx * A,
					   cely * A * r3 - A / r3);
		    pto2D at3 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 + A / 2.0 / r3);
		    pto2D at4 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 - A / 2.0 / r3);
		    if (at1.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
			cachotubo1.addVert (at1, 6);
			posis1[indi1] = 1;
			posis1[nummax1 + indi1] = celx - cely;
			posis1[2*nummax1 + indi1] = cely * 2;
			indi1++;
			if (despleg)
			    molecule.addVert (at1, 6);
		    }	//
		    if (at2.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
			cachotubo1.addVert (at2, 6);
			posis1[indi1] = 2;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 2;
			indi1++;
			if (despleg)
			    molecule.addVert (at2, 6);
		    }	//
		    if (at3.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
			cachotubo1.addVert (at3, 6);
			posis1[indi1] = 2;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 1;
			indi1++;
			if (despleg)
			    molecule.addVert (at3, 6);
		    }	//
		    if (at4.dentro4l (pAcm1, pBcm1, pDcm1, pCcm1)) {
			cachotubo1.addVert (at4, 6);
			posis1[indi1] = 1;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 1;
			indi1++;
			if (despleg)
			    molecule.addVert (at4, 6);
		    }	//
		}

	logInfo (String("with ") + cachotubo1.nvert () + " atoms.");


	double da1 = pV.dista (pA);
	pto3D pAm1 = pA.ptomediocon (pB);
	double dop1 = pV.dista (pAm1);
	// proyectado --> projected
	pto3D pdefproy1 = pto3D (da1 * sin (angucono), 0, fc * (db - da1) * cos (angucono));	//P proyectado
	pto3D odefproy1 = pto3D (-dop1 * sin (angucono), 0, fc * (db - dop1) * cos (angucono));	//P proyectado
	pto3D pstart1 = pdefproy1.ptomediocon (odefproy1);
	pto3D pori1 = pdefproy1.menos (pstart1);

	if (ejes) {
	    molecule.addVert (pdefproy1, 9);
	    molecule.addVert (odefproy1, 8);
	    molecule.addVert (pstart1.mas (lt1.escala (-20)), 7);
	    molecule.addVert (pstart1, 6);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 2);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 3);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 4);
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

	    double TX = di * sin (angucono) * cos (an * 6.0) - ratio1x * diz;
	    // pero para el ajuste del primer tubo, es negativo
	    // but for the adjustment of the first tube, it is negative
	    double TY = di * sin (angucono) * sin (an * 6.0) - ratio1y * diz;

	    double TZ = fc * (db - di) * cos (angucono) - diz;

	    pto3D ptemp = pto3D (TX, TY, TZ);

	    int tipoat = posis1[i];
	    int celdai = posis1[nummax1 + i];
	    int celdaj = posis1[2*nummax1 + i];
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
		if (!molecule.ocupa1 (pperf))
		    molecule.addVert (pperf, 6);



	}

	//TEST
	if (vecs) {
	    pto3D pbaseO = aproxNT (pto3D (0, 0, 0), 1, 0, 0,
				    pstart1, i1, j1, lt1,
				    pto3D (1, 0, 0), 1);
	    pto3D pbase1 = aproxNT (pto3D (0, 0, 0), 1, 1, 0,
				    pstart1, i1, j1, lt1,
				    pto3D (1, 0, 0), 1);
	    pto3D pbase2 = aproxNT (pto3D (0, 0, 0), 1, 0, 1,
				    pstart1, i1, j1, lt1,
				    pto3D (1, 0, 0), 1);
	    molecule.addVert (pbaseO, 6);
	    molecule.addVert (pbase1, 7);
	    molecule.addVert (pbase2, 8);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 3);
	    molecule.conecta (molecule.nvert () - 2, molecule.nvert () - 3);
	}


	logInfo (String("\nStarting 2nd tube construction. "));

	pto2D pAcm2 = pC.clona ().a2D ();
	pto2D pBcm2 = pD.clona ().a2D ();

	pto2D pTcm2 = pto2D (-(pBcm2.y - pAcm2.y),
				 pBcm2.x - pAcm2.x);
	pto3D pTcm2corto = pTcm2.aversor ().escala (lent2);
	pto2D pCcm2 = pAcm2.mas (pTcm2corto).a2D ();
	pto2D pDcm2 = pBcm2.mas (pTcm2corto).a2D ();

	double maxcx2 = max (max (pAcm2.x, pBcm2.x),
				  max (pCcm2.x, pDcm2.x));
	double maxcy2 = max (max (pAcm2.y, pBcm2.y),
				  max (pCcm2.y, pDcm2.y));
	double mincx2 = min (min (pAcm2.x, pBcm2.x),
				  min (pCcm2.x, pDcm2.x));
	double mincy2 = min (min (pAcm2.y, pBcm2.y),
				  min (pCcm2.y, pDcm2.y));


	logInfo (String("Filling 2nd tube planar projection "));

	MoleculaB cachotubo2 = MoleculaB ();


	int sty2 = (int) round ((mincy2 - 3.0) / A / r3);
	int stx2 = (int) round ((mincx2 - 3.0) / A);
	int enx2 = (int) round ((maxcx2 + 3.0) / A);
	int eny2 = (int) round ((maxcy2 + 3.0) / A / r3);

	int nummax2 = (int) (6 * (maxcx2 - mincx2) * (maxcy2 - mincy2) / A / A / r3);
	int *posis2 = new int[3 * nummax2];
	int indi2 = 0;

	for (int cely = sty2; cely <= eny2; cely++)	//recorrido vertical, con
	    for (int celx = stx2; celx <= enx2; celx++)	//recorrido horizontal
		{
		    pto2D at1 = pto2D (celx * A,
					   cely * A * r3 + A / r3);
		    pto2D at2 = pto2D (celx * A,
					   cely * A * r3 - A / r3);
		    pto2D at3 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 + A / 2.0 / r3);
		    pto2D at4 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 - A / 2.0 / r3);
		    if (at1.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
			cachotubo2.addVert (at1, 6);
			posis2[indi2] = 1;
			posis2[nummax2 + indi2] = celx - cely;
			posis2[2*nummax2 + indi2] = cely * 2;
			indi2++;
			if (despleg)
			    molecule.addVert (at1, 6);
		    }	//
		    if (at2.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
			cachotubo2.addVert (at2, 6);
			posis2[indi2] = 2;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 2;
			indi2++;
			if (despleg)
			    molecule.addVert (at2, 6);
		    }	//
		    if (at3.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
			cachotubo2.addVert (at3, 6);
			posis2[indi2] = 2;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 1;
			indi2++;
			if (despleg)
			    molecule.addVert (at3, 6);
		    }	//
		    if (at4.dentro4l (pBcm2, pAcm2, pCcm2, pDcm2)) {
			cachotubo2.addVert (at4, 6);
			posis2[indi2] = 1;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 1;
			indi2++;
			if (despleg)
			    molecule.addVert (at4, 6);
		    }	//
		}


	logInfo (String("with ") + cachotubo2.nvert () + " atoms.");

	double dc2 = pV.dista (pC);
	pto3D pCm2 = pC.ptomediocon (pD);
	double dop2 = pV.dista (pCm2);
	pto3D pdefproy2 = pto3D (dc2 * sin (angucono) * cos (dhT2),
				     dc2 * sin (angucono) * sin (dhT2),
				     fc * (db - dc2) * cos (angucono));	//P proyectado
	pto3D odefproy2 = pto3D (-dop2 * sin (angucono) * cos (dhT2)
				     ,
				     -dop2 * sin (angucono) * sin (dhT2)
				     , fc * (db - dop2) * cos (angucono));	//P proyectado

	pto3D pstart2 = pdefproy2.ptomediocon (odefproy2);

	pto3D pori2 = pdefproy2.menos (pstart2);

	if (ejes) {
	    molecule.addVert (pdefproy2, 9);
	    molecule.addVert (odefproy2, 8);
	    molecule.addVert (pstart2.mas (lt2.escala (20)), 7);
	    molecule.addVert (pstart2, 6);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 2);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 3);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 4);
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

	    double TX = di * sin (angucono) * cos (6.0 * an) + diz * ratio2x;	//diz ahora tiene que ser ositivo
	    double TY = di * sin (angucono) * sin (6.0 * an) + diz * ratio2y;
	    double TZ = fc * (db - di) * cos (angucono) + diz;	// y aqui tambien positivo, por eso hay que restarla

	    pto3D ptemp = pto3D (TX, TY, TZ);

	    int tipoat = posis2[i];
	    int celdai = posis2[nummax2 + i] - n;
	    int celdaj = posis2[2*nummax2 + i] - m;
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
		if (!molecule.ocupa1 (pperf))
		    molecule.addVert (pperf, 6);


	}

	if (vecs) {
	    pto3D pbaseO2 = aproxNT (pto3D (0, 0, 0), 1, 0, 0,
				     pstart2, i2, j2, lt2, pori2,
				     1);
	    pto3D pbase12 = aproxNT (pto3D (0, 0, 0), 1, 1, 0,
				     pstart2, i2, j2, lt2, pori2,
				     1);
	    pto3D pbase22 = aproxNT (pto3D (0, 0, 0), 1, 0, 1,
				     pstart2, i2, j2, lt2, pori2,
				     1);
	    molecule.addVert (pbaseO2, 6);
	    molecule.addVert (pbase12, 7);
	    molecule.addVert (pbase22, 8);
	    molecule.conecta (molecule.nvert () - 1, molecule.nvert () - 3);
	    molecule.conecta (molecule.nvert () - 2, molecule.nvert () - 3);
	}
	//represtentacion vec base




	logInfo (String("Structure (") +
		     i1 + "," + j1 + ")-(" + i2 + "," + j2 + ") completed with " + molecule.nvert () + " atoms");
    } else {

	logInfo (String("\nHeterojunction cannot be formed with a cone. Using alternative algorithm."));


	pto2D Qad = pto2D (A * (nad + mad * 0.5),
			       A * r3 / 2 * mad);
	pto2D Qai = pto2D (A * (nai + mai * 0.5),
			       A * r3 / 2 * mai);

	pto2D pA1 = pto2D (0.0, 0.0);
	pto2D pB1 = pto2D (A * (i1 + j1 * 0.5),
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
	    std::cerr << "Unexpected geometry!!\n";

	pto2D pC1 = pto2D (A * (n + m * 0.5), A * r3 / 2 * m);

	pto2D pA2 = pto2D (0.0, 0.0);
	pto2D pB2 = pto2D (A * (i2 + j2 * 0.5),
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

	pto2D pC2 = pto2D (A * (nprima + mprima * 0.5),
			       A * r3 / 2 * mprima);

	double lonmint1 = pC1.proyeccplano (pB1).modulo ();
	double lonmint2 = pC2.proyeccplano (pB2).modulo ();

	// double lm = max (lonmint1, lonmint2);

	if (lent1 <= lonmint1) {
	    logInfo (String("Warning: 1st tube's length too short: Augmented automatically to ")
		     + (int) (lonmint1 + 1) + " Angstrom.");
	}
	if (lent2 <= lonmint2) {
	    logInfo (String("Warning: 2nd tube's length too short: Augmented automatically to ")
		     + (int) (lonmint2 + 1) + " Angstrom.");
	}
	if (lent1 <= 15. || lent2 <= 15.)
	    logInfo (String("Warning: Open ends remain deformed: Increase length up to 15 Angstrom."));


	//Definimos los puntos que enmarcan los tubos
	//We define the points that frame the tubes -- bounding boxes, maybe?
	pto2D vlong1 = pto2D (pB1.y, -pB1.x);
	pto2D vlong2 = pto2D (-pB2.y, pB2.x);

	pto2D pA1b = vlong1.aversor ().escala (lent1).a2D ();
	pto2D pB1b = pB1.mas (pA1b);
	pto2D pA2b = vlong2.aversor ().escala (lent2).a2D ();
	pto2D pB2b = pB2.mas (pA2b);
	pto2D pC1p = pC1.proyeccplano (pA1b).a2D ();
	pto2D pC2p = pC2.proyeccplano (pA2b).a2D ();
	pto2D pC1b = pC1p.mas (pA1b);
	pto2D pC2b = pC2p.mas (pA2b);


	double maxcx1 = max (max (pA1.x, pB1.x),
				  max (pA1b.x, pB1b.x));
	double maxcy1 = max (max (pA1.y, pB1.y),
				  max (pA1b.y, pB1b.y));
	double mincx1 = min (min (pA1.x, pB1.x),
				  min (pA1b.x, pB1b.x));
	double mincy1 = min (min (pA1.y, pB1.y),
				  min (pA1b.y, pB1b.y));

	double maxcx2 = max (max (pA2.x, pB2.x),
				  max (pA2b.x, pB2b.x));
	double maxcy2 = max (max (pA2.y, pB2.y),
				  max (pA2b.y, pB2b.y));
	double mincx2 = min (min (pA2.x, pB2.x),
				  min (pA2b.x, pB2b.x));
	double mincy2 = min (min (pA2.y, pB2.y),
				  min (pA2b.y, pB2b.y));

	logInfo (String("Starting 1st tube construction. "));
	logInfo (String("Filling 1st tube planar projection "));

	MoleculaB cachot1 = MoleculaB ();


	int sty1 = (int) round ((mincy1 - 3.0) / A / r3);
	int stx1 = (int) round ((mincx1 - 3.0) / A);
	int enx1 = (int) round ((maxcx1 + 3.0) / A);
	int eny1 = (int) round ((maxcy1 + 3.0) / A / r3);

	int nummax1 = (int) (4 * (maxcx1 - mincx1) * (maxcy1 - mincy1) / A / A / r3);
	int *posis1 = new int[3 * nummax1];
	int indi1 = 0;
	for (int cely = sty1; cely <= eny1; cely++)	//recorrido vertical
	    for (int celx = stx1; celx <= enx1; celx++)	//recorrido horizontal
		{
		    pto2D at1 = pto2D (celx * A,
					   cely * A * r3 + A / r3);
		    pto2D at2 = pto2D (celx * A,
					   cely * A * r3 - A / r3);
		    pto2D at3 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 + A / 2.0 / r3);
		    pto2D at4 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 - A / 2.0 / r3);
		    if (at1.dentro4l (pA1, pC1, pC1b, pA1b)
			|| at1.dentro4l (pC1, pB1, pB1b, pC1b)) {
			cachot1.addVert (at1, 6);
			posis1[indi1] = 1;
			posis1[nummax1 + indi1] = celx - cely;
			posis1[2*nummax1 + indi1] = cely * 2;
			indi1++;
		    }	//molecule.addVert(at1,7);
		    if (at2.dentro4l (pA1, pC1, pC1b, pA1b)
			|| at2.dentro4l (pC1, pB1, pB1b, pC1b)) {
			cachot1.addVert (at2, 6);
			posis1[indi1] = 2;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 2;
			indi1++;
		    }	//molecule.addVert(at2,7);
		    if (at3.dentro4l (pA1, pC1, pC1b, pA1b)
			|| at3.dentro4l (pC1, pB1, pB1b, pC1b)) {
			cachot1.addVert (at3, 6);
			posis1[indi1] = 2;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 1;
			indi1++;
		    }	//molecule.addVert(at3,7);
		    if (at4.dentro4l (pA1, pC1, pC1b, pA1b)
			|| at4.dentro4l (pC1, pB1, pB1b, pC1b)) {
			cachot1.addVert (at4, 6);
			posis1[indi1] = 1;
			posis1[nummax1 + indi1] = celx - cely + 1;
			posis1[2*nummax1 + indi1] = cely * 2 - 1;
			indi1++;
		    }	//molecule.addVert(at4,7);
		}
	logInfo (String("with ") + cachot1.nvert () + " atoms.");

	MoleculaB cachot2 = MoleculaB ();

	logInfo (String("\nStarting 2nd tube construction. "));
	logInfo (String("Filling 2nd tube planar projection "));

	//hay que calcular la macrocelda del comienzo, que debe ser el centro de un hexagono
	//it is necessary to calculate the macrocell of the beginning, that must be the center of a hexagon
	int sty2 = (int) round ((mincy2 - 3.0) / A / r3);
	int stx2 = (int) round ((mincx2 - 3.0) / A);
	int enx2 = (int) round ((maxcx2 + 3.0) / A);
	int eny2 = (int) round ((maxcy2 + 3.0) / A / r3);

	int nummax2 = (int) (4 * (maxcx2 - mincx2) * (maxcy2 - mincy2) / A / A / r3);
	int *posis2 = new int[3 * nummax2];
	int indi2 = 0;
	for (int cely = sty2; cely <= eny2; cely++)	//recorrido vertical,
	    for (int celx = stx2; celx <= enx2; celx++)	//recorrido horizontal
		{
		    pto2D at1 = pto2D (celx * A,
					   cely * A * r3 + A / r3);
		    pto2D at2 = pto2D (celx * A,
					   cely * A * r3 - A / r3);
		    pto2D at3 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 + A / 2.0 / r3);
		    pto2D at4 = pto2D (celx * A + A / 2.0,
					   cely * A * r3 - A / 2.0 / r3);
		    if (at1.dentro4l (pA2, pA2b, pC2b, pC2)
			|| at1.dentro4l (pC2, pC2b, pB2b, pB2)) {
			cachot2.addVert (at1, 6);
			posis2[indi2] = 1;
			posis2[nummax2 + indi2] = celx - cely;
			posis2[2*nummax2 + indi2] = cely * 2;
			indi2++;
		    }	//molecule.addVert(at1,1);
		    if (at2.dentro4l (pA2, pA2b, pC2b, pC2)
			|| at2.dentro4l (pC2, pC2b, pB2b, pB2)) {
			cachot2.addVert (at2, 6);
			posis2[indi2] = 2;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 2;
			indi2++;
		    }	//molecule.addVert(at2,1);
		    if (at3.dentro4l (pA2, pA2b, pC2b, pC2)
			|| at3.dentro4l (pC2, pC2b, pB2b, pB2)) {
			cachot2.addVert (at3, 6);
			posis2[indi2] = 2;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 1;
			indi2++;
		    }	//molecule.addVert(at3,1);
		    if (at4.dentro4l (pA2, pA2b, pC2b, pC2)
			|| at4.dentro4l (pC2, pC2b, pB2b, pB2)) {
			cachot2.addVert (at4, 6);
			posis2[indi2] = 1;
			posis2[nummax2 + indi2] = celx - cely + 1;
			posis2[2*nummax2 + indi2] = cely * 2 - 1;
			indi2++;
		    }	//molecule.addVert(at4,1);
		}
	logInfo (String("with ") + cachot2.nvert () + " atoms.");


	double C1 = pC1.proyeccplano (pA1b).modulo ();
	double C2 = pC2.proyeccplano (pA2b).modulo ();
	double C = (C1 + C2) * 0.5;
	double B1 = pB1.modulo () - C1;
	double B2 = pB2.modulo () - C2;
	double B = (B1 + B2) * 0.5;


	double AL1 = pB1.angulocwhasta (pC1);
	double AL2 = pB2.angulocwhasta (pC2);	//pueden ser negativos!!
	double Cy1 = C1 * tan (AL1);
	double Cy2 = C2 * tan (AL2);	//y estos tres tambien!!
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
	double R = (B + C) / 2.0 / M_PI;

	// this is an angle in radians
	double curvaP = 0.4;	//esto es un angulillo en radianes
	double curvaH = 0.4;

	pto3D lead11 = pto3D ();
	pto3D lead12 = pto3D ();
	pto3D lead21 = pto3D ();
	pto3D lead22 = pto3D ();


	double a2to1 = (C / R);	//en radianes
	double sa = sin (a2to1);
	double ca = cos (a2to1);
	double sp = sin (curvaP);
	double cp = cos (curvaP);
	double sh = sin (curvaH);
	double ch = cos (curvaH);

	if (directo) {
	    lead11 = pto3D (sp, 0.0, cp);	//De primer tubo     P
	    lead12 = pto3D (-ca * sh, -sa * sh, ch);	//2ndo def      H
	    lead21 = pto3D (-sp, 0.0, cp);	//De segundo tubo    P
	    lead22 = pto3D (ca * sh, sa * sh, ch);	//                   H
	} else {
	    lead11 = pto3D (-sh, 0.0, ch);	//De primer tubo     H
	    lead12 = pto3D (ca * sp, sa * sp, cp);	//2ndo def      P
	    lead21 = pto3D (sh, 0.0, ch);	//De segundo tubo    H
	    lead22 = pto3D (-ca * sp, -sa * sp, cp);	//                   P
	}
	pto3D lt1 = lead11.mas (lead12).aversor ();
	pto3D lt2 = lead21.mas (lead22).aversor ();
	double ratio1x = lt1.x / lt1.z;
	double ratio1y = lt1.y / lt1.z;
	double ratio2x = lt2.x / lt2.z;
	double ratio2y = lt2.y / lt2.z;


	for (int i = 0; i < cachot1.nvert (); i++) {
	    pto3D p = cachot1.susatomos.get(i)->vert;
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
	    double xf = R * cos (M_PI * 2 * xm / (B + C)) + (ratio1x * htolq);	//*ft1+ratio2x*ft2)
	    double yf = R * sin (M_PI * 2 * xm / (B + C)) + (ratio1y * htolq);	//ft1+ratio2y*ft2)*
	    double zf = ym;

	    pto3D ptemp = pto3D (xf, yf, zf);
	    int tipoat = posis1[i];
	    int celdai = posis1[nummax1 + i];
	    int celdaj = posis1[2*nummax1 + i];

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
				       pto3D (0, 0, 0),
				       i1, j1,
				       lt1,
				       pto3D (R, 0, 0),
				       co);
	    if (!molecule.ocupa1 (pperf))
		molecule.addVert (pperf, 6);
	}


	for (int i = 0; i < cachot2.nvert (); i++) {
	    pto3D p = cachot2.susatomos.get(i)->vert;
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


	    double xf = R * cos (M_PI * 2 * xm / (B + C)) + (ratio2x * htolq);	//ft1+ratio2x*ft2)*ym
	    double yf = R * sin (M_PI * 2 * xm / (B + C)) + (ratio2y * htolq);	//ft1+ratio2y*ft2)*ym
	    double zf = ym;

	    pto3D ptemp = pto3D (xf, yf, zf);

	    int tipoat = posis2[i];
	    int celdai = posis2[nummax2 + i];
	    int celdaj = posis2[2*nummax2 + i];


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
				       pto3D (0, 0, 0),
				       i2, j2,
				       lt2,
				       pto3D (R, 0, 0),
				       co);


	    if (!molecule.ocupa1 (pperf))
		molecule.addVert (pperf, 6);
	}

	logInfo (String("Structure (") +
		     i1 + "," + j1 + ")-(" + i2 + "," + j2 + ") completed with " + molecule.nvert () + " atoms");

    }


    //final y visualizacin
    //end and visualization
    molecule.reconec (1.35);
    logInfo (String("Refining process: "));

    int eliminados = molecule.depuraconec ();
    logInfo (String(eliminados) + " bonds removed and ");
    int creados = molecule.remataconec ();
    logInfo (String(creados) + " bonds added.");

    finish(terminator);
}

int W2::detectanconc (pto2D pA, pto2D pB, pto2D pC, pto2D pD)
{
    int nconcav = 0;
    //el interior esta por debajo del primer trayecto. si tiene4 concavidades, es el complementario del cuadrado.
    pto2D v1 = pC.menos (pB);
    pto2D v2 = pD.menos (pC);
    pto2D v3 = pA.menos (pD);
    pto2D v4 = pB.menos (pA);

    double a1 = v1.angulocwhasta (v2);
    if (a1 < 0 || a1 > M_PI)
	nconcav++;
    double a2 = v2.angulocwhasta (v3);
    if (a2 < 0 || a2 > M_PI)
	nconcav++;
    double a3 = v3.angulocwhasta (v4);
    if (a3 < 0 || a3 > M_PI)
	nconcav++;
    double a4 = v4.angulocwhasta (v1);
    if (a4 < 0 || a4 > M_PI)
	nconcav++;


    return nconcav;
}

pto3D W2::aproxNT (pto3D pto,	//pto es el punto a aproximar
		   int atotip, int posi, int posj, pto3D origen, int i, int j, pto3D orient, pto3D inicio, double coef)
{



    pto3D inicioperp = inicio.proyeccplano (orient);
    pto3D vprolonori = inicio.menos (inicioperp);	//a la fuerza es la proy de inidio sobre la orientacion

    pto3D vx = inicioperp.aversor ();
    pto3D vz = orient.aversor ();
    pto3D vy = vz.prodvect (vx);

    Nanotubo NT = Nanotubo (i, j);

    //contamos los pasos tanto radiales como longitudinales correspondientes a posi, posj

    double deltazet = -posi * NT.deltaz2 + posj * NT.deltaz1;	//revisar si el orden esta bien los deltaz son todos positivos, ojo a los signos
    double deltaphi = posi * NT.deltaphi2 + posj * NT.deltaphi1;	//OJO por motivos historicos, 1 se refiere alvect de la red que esta
    // por encima de Quiral,


    double deltazetat = atotip * NT.deltazc ();
    double deltaphiat = atotip * NT.deltaphic ();

    double R = NT.radio ();
    double cdp = cos (deltaphi + deltaphiat);
    double sdp = sin (deltaphi + deltaphiat);

    //los tres pasitos
    pto3D vv1 = vz.escala (deltazet + deltazetat);
    pto3D vv2 = vx.escala (R * cdp);
    pto3D vv3 = vy.escala (R * sdp);


    return pto.ptopondcon (origen.mas (vv1).mas (vv2).mas (vv3), coef);

}



pto3D W2::aproxNTchap (pto3D pto,	//pto es el punto a aproximar
		       int atotip, int posi, int posj, pto3D origen, int i, int j, pto3D orient, pto3D inicio, double coef)
{
    pto3D inicioperp = inicio.proyeccplano (orient);
    pto3D vprolonori = inicio.menos (inicioperp);

    origen = origen.mas (vprolonori);

    pto3D vx = inicioperp.aversor ();
    pto3D vz = orient.aversor ();
    pto3D vy = vz.prodvect (vx);

    Nanotubo NT = Nanotubo (i, j);


    double deltazet = -posi * NT.deltaz2 + posj * NT.deltaz1;
    double deltaphi = posi * NT.deltaphi2 + posj * NT.deltaphi1;



    double deltazetat = atotip * NT.deltazc ();
    double deltaphiat = atotip * NT.deltaphic ();

    double R = NT.radio ();
    double cdp = cos (deltaphi + deltaphiat);	//
    double sdp = sin (deltaphi + deltaphiat);	//

    //los tres pasitos
    pto3D vv1 = vz.escala (deltazet + deltazetat);	//
    pto3D vv2 = vx.escala (R * cdp);
    pto3D vv3 = vy.escala (R * sdp);

    return pto.ptopondcon (origen.mas (vv1).mas (vv2).mas (vv3), coef);
}


int main(int argc, char *argv[])
{
    int i1, j1, i2, j2, terminator, index;
    double lent1, lent2;
    char *p, *outputfile;

    if (argc < 10)
	goto bad_input;
    i1 = strtol(argv[1], &p, 10);
    if (*p != '\0') goto bad_input;
    j1 = strtol(argv[2], &p, 10);
    if (*p != '\0') goto bad_input;
    lent1 = strtod(argv[3], &p);
    if (*p != '\0') goto bad_input;
    i2 = strtol(argv[4], &p, 10);
    if (*p != '\0') goto bad_input;
    j2 = strtol(argv[5], &p, 10);
    if (*p != '\0') goto bad_input;
    lent2 = strtod(argv[6], &p);
    if (*p != '\0') goto bad_input;
    terminator = strtol(argv[7], &p, 10);
    if (*p != '\0') goto bad_input;
    index = strtol(argv[8], &p, 10);
    if (*p != '\0') {
    bad_input:
	std::cerr << "BAD INPUT\n";
	return -1;
    }
    outputfile = argv[9];
    W2 w2 = W2(i1, j1, lent1, i2, j2, lent2, terminator);
    w2.molecule.mmp(outputfile, index);
    return 0;
}
