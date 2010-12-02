class Nanotubo
{

	public int i1, i2, ordenmin, d;
	int primos[] = { 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
		53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 1
	};
	double altura[], phi[];  // altura --> height
	double A = 2.46, deltaz1, deltaz2, deltaphi1, deltaphi2;;

	Nanotubo (int I, int J)
	{
		this.i1 = I;
		this.i2 = J;
		ordenmin = 1;  // orden --> order
		d = 1;

		int nn = i1, mm = i2;
		altura = new double[100];
		phi = new double[100];

		// find common factors between nn and mm, move them to d
		for (int i = 1; i <= 25; i++) {
			for (int j = 1; ((nn % primos[i]) == 0)
			     && ((mm % primos[i]) == 0); j++) {
				nn = nn / primos[i];
				mm = mm / primos[i];
				d = d * primos[i];
		}}

		deltaz1 = A * Math.sin (Math.PI / 3 - quiral ());
		deltaz2 = A * Math.sin (quiral ());	//esto, al estar bajo Q, es positivo cuando deberia ser negativo! OJO a esto!
		// this, when being under Q, is positive when it would have to be negative! WATCH this!
		deltaphi1 = A / radio () * Math.cos (Math.PI / 3 - quiral ());
		deltaphi2 = A / radio () * Math.cos (quiral ());

		altura[1] = deltaz1;
		phi[1] = deltaphi1;

		for (int i = 2; i <= (i1 + i2) / d; i++) {
			if (altura[i - 1] < 0) {
				altura[i] = altura[i - 1] + deltaz1;
				phi[i] = phi[i - 1] + deltaphi1;
			} else {
				altura[i] = altura[i - 1] - deltaz2;
				phi[i] = phi[i - 1] + deltaphi2;
			}

			if ((altura[i] < altura[ordenmin]) == (altura[i] > 0.0001))
				ordenmin = i;
		}
	}
	Nanotubo (int I, int J, double aalt)
	{

		A = aalt;
		this.i1 = I;
		this.i2 = J;
		ordenmin = 1;
		d = 1;

		int nn = i1, mm = i2;
		altura = new double[100];
		phi = new double[100];

		for (int i = 1; i <= 25; i++) {
			for (int j = 1; ((nn % primos[i]) == 0)
			     && ((mm % primos[i]) == 0); j++) {
				nn = nn / primos[i];
				mm = mm / primos[i];
				d = d * primos[i];
		}}

		deltaz1 = A * Math.sin (Math.PI / 3 - quiral ());
		deltaz2 = A * Math.sin (quiral ());
		deltaphi1 = A / radio () * Math.cos (Math.PI / 3 - quiral ());
		deltaphi2 = A / radio () * Math.cos (quiral ());

		altura[1] = deltaz1;
		phi[1] = deltaphi1;

		for (int i = 2; i <= (i1 + i2) / d; i++) {
			if (altura[i - 1] < 0) {
				altura[i] = altura[i - 1] + deltaz1;
				phi[i] = phi[i - 1] + deltaphi1;
			} else {
				altura[i] = altura[i - 1] - deltaz2;
				phi[i] = phi[i - 1] + deltaphi2;
			}

			if ((altura[i] < altura[ordenmin]) == (altura[i] > 0.0001))
				ordenmin = i;
		}
	}

	double deltaz ()
	{
		return altura[ordenmin];
	}
	double deltaphi ()
	{
		return phi[ordenmin];
	}
	double radio ()
	{
		return A * Math.sqrt (i1 * i1 + i2 * i2 + i2 * i1) / (2 * Math.PI);
	}
	double quiral ()
	{
		double ang = Math.atan (Math.sqrt (3) * i2 / (2 * i1 + i2));
		if (2 * i1 + i2 < 0)
			ang += (Math.PI);
		return ang;
	}
	double quiralg ()
	{
		return quiral () * (180.0 / Math.PI);
	}
	double deltazc ()
	{
		return A / Math.sqrt (3) * Math.cos (quiral ());
	}
	double deltaphic ()
	{
		return A / Math.sqrt (3) / radio () * Math.sin (quiral ());
	}
	int d ()
	{
		return d;
	}

	double energia (double momm, double momz)
	{
		double numfase = Math.sin (momz * deltaz1 + momm * deltaphi1) + Math.sin (momz * (deltaz1 + deltaz2) + momm * (deltaphi1 - deltaphi2));
		double denfase = 1 + Math.cos (momz * deltaz1 + momm * deltaphi1) + Math.cos (momz * (deltaz1 + deltaz2) + momm * (deltaphi1 - deltaphi2));
		double energ = Math.sqrt (numfase * numfase + denfase * denfase);
		return energ;
	}


}
