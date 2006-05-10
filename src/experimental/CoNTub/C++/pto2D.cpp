class pto2D extends pto3D
{

	pto2D ()
	{
		x = 0.0f;
		y = 0.0f;
		z = 0.0f;
	}
	pto2D (float xt, float yt)
	{
		x = xt;
		y = yt;
		z = 0.0f;
	}
	pto2D (double xt, double yt)
	{
		x = (float) xt;
		y = (float) yt;
		z = 0.0f;
	}


	boolean dentro3 (pto2D A, pto2D B, pto2D C)	//Ha de ser un metodo estricto, aunque se ponen >=
	{
		pto3D bisA = B.menos (A).aversor ().mas (C.menos (A).aversor ());	//bisectrices
		pto3D bisB = A.menos (B).aversor ().mas (C.menos (B).aversor ());
		double angulo1 = C.menos (A).anguloconr (bisA);	//angulos maximos
		double angulo2 = C.menos (B).anguloconr (bisB);
		double anguloP1 = menos (A).anguloconr (bisA);	//Angulos del candidato
		double anguloP2 = menos (B).anguloconr (bisB);

		if ((anguloP1 <= angulo1) && (anguloP2 <= angulo2))
			return true;
		else
			return false;
	}
	boolean dentro3l (pto2D A, pto2D B, pto2D C)	//el metodo laxo
	{
		pto2D centro = A.mas (B).mas (C).escala (0.3333).a2D ();
		//Vectores  de conexion a cada uno de los cuatro
		pto2D ca = A.menos (centro).a2D ();
		pto2D cb = B.menos (centro).a2D ();
		pto2D cc = C.menos (centro).a2D ();
		//y nuevos puntos, expandidos
		A = centro.mas (ca).mas (ca.aversor ().escala (0.05)).a2D ();
		B = centro.mas (cb).mas (ca.aversor ().escala (0.05)).a2D ();
		C = centro.mas (cc).mas (ca.aversor ().escala (0.05)).a2D ();
		return dentro3 (A, B, C);
	}

	boolean dentrocasi3 (pto2D A, pto2D B, pto2D v1, pto2D v2)
		//ptos comprendidos en el triangulo cuyo lado esta formado por  AB
		//los lados marcados por v1 (que emerge de A) y v2 (de B)
		//Ha de ser un metodo estricto
	{
		pto3D vAB = B.menos (A);
		pto3D vBA = A.menos (B);
		pto3D bisA = vAB.aversor ().mas (v1.aversor ());	//bisectrices
		pto3D bisB = vBA.aversor ().mas (v2.aversor ());
		double angulo1 = v1.anguloconr (bisA);	//angulos maximos
		double angulo2 = v2.anguloconr (bisB);
		double anguloP1 = menos (A).anguloconr (bisA);	//Angulos del candidato
		double anguloP2 = menos (B).anguloconr (bisB);

		if ((anguloP1 <= angulo1) && (anguloP2 <= angulo2))
			return true;
		else
			return false;
	}



	boolean dentro4cv (pto2D A, pto2D B, pto2D C, pto2D D, double p)
	{
		//SOLO VALIDO PARA TRAP CONVEXOS

//        C---------------------D
//       /                      \
//      A-----------------------B
		// TRAPEZOIDE MAGICO compuesto por A= 0, B quiral 1er tubo
		//C origen segundo tubo D=final segundo tubo
		//angulos subtendidos BAC y CDB

		//Calculamos centroide,
		pto2D centro = A.mas (B).mas (C).mas (D).escala (0.25).a2D ();
		//Vectores  de conexion a cada uno de los cuatro
		pto2D ca = A.menos (centro).a2D ();
		pto2D cb = B.menos (centro).a2D ();
		pto2D cc = C.menos (centro).a2D ();
		pto2D cd = D.menos (centro).a2D ();
		//y nuevos puntos, expandidos
		A = centro.mas (ca.escala (p)).a2D ();
		B = centro.mas (cb.escala (p)).a2D ();
		C = centro.mas (cc.escala (p)).a2D ();
		D = centro.mas (cd.escala (p)).a2D ();

		pto3D bisA = B.menos (A).aversor ().mas (C.menos (A).aversor ());	//bisectrices
		pto3D bisD = B.menos (D).aversor ().mas (C.menos (D).aversor ());

		double anguloA = C.menos (A).anguloconr (bisA);	//angulos maximos
		double anguloD = B.menos (D).anguloconr (bisD);
		//
		double anguloPbisA = menos (A).anguloconr (bisA);	//Angulos del candidato
		double anguloPbisD = menos (D).anguloconr (bisD);

		if ((anguloPbisA < anguloA) && (anguloPbisD < anguloD))
			return true;
		else
			return false;

	}

	boolean dentro4 (pto2D A, pto2D B, pto2D C, pto2D D, double p)
	{
		//esta vez los puntos a, b, c y d tienen que seguir el camino.

//Primero detectamos si es convexo, si tiene cero, una concavidad,
		int nconcav = 0;

//el interior esta por debajo del primer trayecto. si tiene4 concavidades, es el complementario del cuadrado.
		pto2D v1 = B.menos (A);
		pto2D v2 = C.menos (B);
		pto2D v3 = D.menos (C);
		pto2D v4 = A.menos (D);

		pto2D[]ap = new pto2D[4];
		boolean[]ac = new boolean[4];

		ap[0] = A;
		ap[1] = B;
		ap[2] = C;
		ap[3] = D;

		double a2 = v1.angulocwhasta (v2);
		double a3 = v2.angulocwhasta (v3);
		double a4 = v3.angulocwhasta (v4);
		double a1 = v4.angulocwhasta (v1);

		double margen = 0.001;	//Ojo, es vital para evitar cosas raras!
		if (a1 < margen || a1 > Math.PI - margen) {
			nconcav++;
			ac[0] = true;
		} else
			ac[0] = false;
		if (a2 < margen || a2 > Math.PI - margen) {
			nconcav++;
			ac[1] = true;
		} else
			ac[1] = false;
		if (a3 < margen || a3 > Math.PI - margen) {
			nconcav++;
			ac[2] = true;
		} else
			ac[2] = false;
		if (a4 < margen || a4 > Math.PI - margen) {
			nconcav++;
			ac[3] = true;
		} else
			ac[3] = false;

//antes de nada, vemos si hay algun angulo de aprox 180


		if (nconcav == 0) {	//Convexo, usamos el anterior
			return dentro4cv (A, B, D, C, p);	//Hay que darle la vuelta
		} else if (nconcav == 1) {	//identificamos el concavo
			int ocon1 = -1;
			for (int i = 0; i < 4; i++) {
				if (ac[i] == true)
					ocon1 = i;
			}
			int ocona = ocon1 + 1;
			if (ocona > 3)
				ocona -= 4;
			int ocon2 = ocon1 + 2;
			if (ocon2 > 3)
				ocon2 -= 4;
			int oconb = ocon1 + 3;
			if (oconb > 3)
				oconb -= 4;
			boolean dentroa = dentro3l (ap[ocon1], ap[ocona], ap[ocon2]);	//EXPERIMENTAL!!
			boolean dentrob = dentro3l (ap[ocon1], ap[oconb], ap[ocon2]);
			if (dentroa || dentrob)
				return true;
			else
				return false;
		} else if (nconcav == 2) {	//las concavidades han de estar seguidas,
			//a la fuerza, y eso representa un cruce
			//Nos abstenemos?       return false;
			//Prueba con los triangulos formados?
			int conc1 = -1;
			int conc2 = -1;
			int conv1 = -1;
			int conv2 = -1;
			for (int i = 0; i < 4; i++) {
				if (ac[i] == false)
					conc1 = i;
			}
			//Ya tenemos el primero, buscamos el segundo con concavidad
			//van por parejas, conc, conc, no conc, no conc, nunca alternados
			//Buscamos el segundo
			for (int i = 0; i < 4; i++) {
				if ((i != conc1) && (ac[i] == false))
					conc2 = i;
			}
			//Una vez que conocemos los dos concavos, buscamos los convexos
			for (int i = 0; i < 4; i++) {
				if (ac[i] == true)
					conv1 = i;
			}
			for (int i = 0; i < 4; i++) {
				if ((i != conv1) && (ac[i] == true))
					conv2 = i;
			}
			//ahora, asociamos a cada puntillo el vecino con concavidad contraria
			int cc1v1 = conc1 + 1;
			if (cc1v1 > 3)
				cc1v1 -= 4;
			int cc1v2 = conc1 + 3;
			if (cc1v2 > 3)
				cc1v2 -= 4;
			int cc2v1 = conc2 + 1;
			if (cc2v1 > 3)
				cc2v1 -= 4;
			int cc2v2 = conc2 + 3;
			if (cc2v2 > 3)
				cc2v2 -= 4;
			int cv1v1 = conv1 + 1;
			if (cv1v1 > 3)
				cv1v1 -= 4;
			int cv1v2 = conv1 + 3;
			if (cv1v2 > 3)
				cv1v2 -= 4;
			int cv2v1 = conv2 + 1;
			if (cv2v1 > 3)
				cv2v1 -= 4;
			int cv2v2 = conv2 + 3;
			if (cv2v2 > 3)
				cv2v2 -= 4;
			//Ya tenemos a cada uno con sus vecinos. Cual es el de concav opuesta?
			int cc1op = -1;
			if ((ac[cc1v1] != ac[conc1])
			    && (ac[cc1v2] == ac[conc1]))
				cc1op = cc1v1;
			else if ((ac[cc1v2] != ac[conc1])
				 && (ac[cc1v1] == ac[conc1]))
				cc1op = cc1v2;
			int cc2op = -1;
			if ((ac[cc2v1] != ac[conc2])
			    && (ac[cc2v2] == ac[conc2]))
				cc2op = cc2v1;
			else if ((ac[cc2v2] != ac[conc2])
				 && (ac[cc2v1] == ac[conc2]))
				cc2op = cc2v2;
			int cv1op = -1;
			if ((ac[cv1v1] != ac[conv1])
			    && (ac[cv1v2] == ac[conv1]))
				cv1op = cv1v1;
			else if ((ac[cv1v2] != ac[conv1])
				 && (ac[cv1v1] == ac[conv1]))
				cv1op = cv1v2;
			int cv2op = -1;
			if ((ac[cv2v1] != ac[conv2])
			    && (ac[cv2v2] == ac[conv2]))
				cv2op = cv2v1;
			else if ((ac[cv2v2] != ac[conv2])
				 && (ac[cv2v1] == ac[conv2]))
				cv2op = cv2v2;

			boolean ta = dentrocasi3 (ap[conc1], ap[conc2],
						  ap[cc1op].menos (ap[conc1]),
						  ap[cc2op].menos (ap[conc2]));
			boolean tb = dentrocasi3 (ap[conv1], ap[conv2],
						  ap[cv1op].menos (ap[conv1]),
						  ap[cv2op].menos (ap[conv2]));

			if (ta || tb)
				return true;
			else
				return false;


		} else if (nconcav == 3) {
			int ocon1 = -1;
			for (int i = 0; i < 4; i++) {
				if (ac[i] == false)
					ocon1 = i;
			}
			int ocona = ocon1 + 1;
			if (ocona > 3)
				ocona -= 4;
			int ocon2 = ocon1 + 2;
			if (ocon2 > 3)
				ocon2 -= 4;
			int oconb = ocon1 + 3;
			if (oconb > 3)
				oconb -= 4;
			boolean fueraa = !dentro3l (ap[ocon1], ap[ocona], ap[ocon2]);
			boolean fuerab = !dentro3l (ap[ocon1], ap[oconb], ap[ocon2]);
			//if (fueraa&&fuerab) return true;
			//else return false;}
			return true;
		} else if (nconcav == 4) {	//Complementario de convexo, complementario del anterior True si esta fuera
			return !dentro4cv (A, B, D, C, p);	//Hay que darle la vuelta
		} else {
			return false;
		}



	}


	boolean dentro4 (pto2D A, pto2D B, pto2D C, pto2D D)
	{
		return dentro4 (A, B, C, D, 0.0);
	}


	double anguloccwhasta (pto2D phasta)	//EN RADIANES
	{
		double an = 0;
		double a = anguloconr (phasta);
		pto3D pv = prodvect (phasta);
		if (pv.z < 0)
			an = (Math.PI * 2.0) - a;
		else if (pv.z >= 0)
			an = a;
		return an;
	}

	double angulocwhasta (pto2D phasta)	//EN RADIANES
	{
		double an = 0;
		double a = anguloconr (phasta);
		pto3D pv = prodvect (phasta);
		if (pv.z > 0)
			an = (Math.PI * 2.0) - a;
		else if (pv.z <= 0)
			an = a;
		return an;
	}


	boolean dentro4e (pto2D A, pto2D B, pto2D C, pto2D D)
	{
		return dentro4 (A, B, C, D, 1.00);
	}			//estricto

	boolean dentro4l (pto2D A, pto2D B, pto2D C, pto2D D)
	{
		return dentro4 (A, B, C, D, 1.01);
	}			//laxo


	pto2D mas (pto2D p)
	{
		return new pto2D (this.x + p.x, this.y + p.y);
	}
	pto2D menos (pto2D p)
	{
		return new pto2D (this.x - p.x, this.y - p.y);
	}
}
