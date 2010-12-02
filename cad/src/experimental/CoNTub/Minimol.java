import java.awt.Color;

class Minimol
{
	int nvert;
	pto3D miniverts[];
	String minietiqs[];
	String miniperss[];
	float minisizes[];
	Color minicolor[];
	int miniselec[];
	int miniconec[][];
	double xmin, xmax, ymin, ymax, zmin, zmax;

	  Minimol (int nv)
	{
		nvert = nv;
		miniverts = new pto3D[nvert];
		minietiqs = new String[nvert];
		miniperss = new String[nvert];
		minisizes = new float[nvert];
		  minicolor = new Color[nvert];
		  miniselec = new int[nvert];
		  miniconec = new int[nvert][10];
	}


	Minimol (MoleculaB mo)
	{
		//Creacion de una minimolecula rapida para manipulacion dentro de un visor 3D
		//A partir de una molecula compleja tipo MoleculaB
		nvert = mo.susatomos.size ();
		miniverts = new pto3D[nvert];
		minietiqs = new String[nvert];
		miniperss = new String[nvert];
		minisizes = new float[nvert];
		minicolor = new Color[nvert];
		miniselec = new int[nvert];
		miniconec = new int[nvert][10];
		for (int i = 0; i < nvert; i++) {
			Atomo at = (Atomo) mo.susatomos.get (i);
			miniverts[i] = new pto3D (at.vert.x, at.vert.y, at.vert.z);
			minietiqs[i] = at.etiq;
			miniperss[i] = at.pers;
			minisizes[i] = (float) at.r;
			minicolor[i] = at.color;
			miniselec[i] = 0;
			for (int j = 0; j < 10; j++)
				miniconec[i][j] = at.mconec[j];
		}
	}


	void vaciar ()
	{
	}

//void deseleccionar(){for (int i = 0; i<susatomos.size();i++) ((Atomo)susatomos.get(i)).selec=0; nselec=0;}
//HABRIA QUE PONER HERRAMIENTAS DE SELECCIONADO

	void girox (double th)
	{
		for (int i = 0; i < nvert; i++) {
			float ct = (float) Math.cos (th / 180 * Math.PI);
			float st = (float) Math.sin (th / 180 * Math.PI);
			miniverts[i].rgirox (ct, st);
	}}
	void giroy (double th)
	{
		for (int i = 0; i < nvert; i++) {
			float ct = (float) Math.cos (th / 180 * Math.PI);
			float st = (float) Math.sin (th / 180 * Math.PI);
			miniverts[i].rgiroy (ct, st);
	}}
	void giroz (double th)
	{
		for (int i = 0; i < nvert; i++) {
			float ct = (float) Math.cos (th / 180 * Math.PI);
			float st = (float) Math.sin (th / 180 * Math.PI);
			miniverts[i].rgiroz (ct, st);
	}}

	double getDim ()
	{
		double Dim = 0.01;
		for (int i = 0; i < nvert; i++) {
			for (int j = i + 1; j < nvert; j++) {
				pto3D v = miniverts[i];
				pto3D w = miniverts[j];
				double dist = v.dista (w);
				if (dist > Dim)
					Dim = dist;
			}
		}
		return Dim;
	}


	double distancia (int a, int b)
	{
		pto3D v = miniverts[a];
		pto3D w = miniverts[b];
		return v.dista (w);
	}

	double angulo (int a, int b, int c)	//OJO EN GRADOS
	{
		pto3D v = miniverts[a];
		pto3D w = miniverts[b];
		pto3D u = miniverts[c];
		return u.menos (w).angulocong (v.menos (w));
	}

	double dihedro (int a, int b, int c, int d)
	{
		pto3D v = miniverts[a];
		pto3D w = miniverts[b];
		pto3D u = miniverts[c];
		pto3D s = miniverts[d];
		pto3D v1 = v.menos (w);
		pto3D v2 = w.menos (u);
		pto3D v3 = s.menos (u);
		return v1.dihedrog (v2, v3);
	}			//OJO EN GRADOS


	int selecstatus (int i)
	{
		return miniselec[i];
	}
	void selecciona (int i, int status)
	{
		miniselec[i] = status;
	}
	void deselecciona ()
	{
		for (int i = 0; i < nvert; i++)
			miniselec[i] = 0;
	}

	Minimol clona ()
	{
		Minimol mmn = new Minimol (this.nvert);

		for (int i = 0; i < this.nvert; i++) {
			mmn.miniverts[i] = this.miniverts[i].clona ();
			mmn.minietiqs[i] = this.minietiqs[i];
			mmn.miniperss[i] = this.miniperss[i];
			mmn.minisizes[i] = this.minisizes[i];
			mmn.minicolor[i] = this.minicolor[i];
			mmn.miniselec[i] = this.miniselec[i];
			for (int j = 0; j < 10; j++)
				mmn.miniconec[i][j] = this.miniconec[i][j];

		}
		return mmn;
	}
	double getLejania ()
	{
		double lej = 0;
		if (nvert == 1)
			return 0;
		for (int i = 0; i < nvert; i++) {
			pto3D v = miniverts[i];
			pto3D c = new pto3D (0, 0, 0);
			double dist = v.dista (c);
			if (dist > lej)
				lej = dist;
		}
		return lej;
	}
}
