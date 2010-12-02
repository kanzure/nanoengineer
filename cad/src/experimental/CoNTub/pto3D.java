class pto3D
{
	float x, y, z;

	  pto3D ()
	{
		x = 0.0f;
		y = 0.0f;
		z = 0.0f;
	}
	pto3D (double X, double Y, double Z)
	{
		x = (float) X;
		y = (float) Y;
		z = (float) Z;
	}

	/*Resumen de operaciones
	   girox(90)
	   girox(90,ptoauxiliar)
	   OK mas(ptosegundo)
	   OK menos(ptosegundo)
	   OK  prodesc(pto2)
	   OK  modulo
	   OK  prodvect(pto2)
	   OK  escala(doble)      Multiplica el vector linealmente
	   OK  dista(pto2)
	   OK  angulocon(pto2)
	   proyeccplano(pto2) Devuelve su proyeccion en el plano marcado por en vect pto2
	   dihedro(pto2)  (respecto vector unitario x)  OBSOLETO
	   OK  dihedro(pto2 pto1) del punto en cuestion a traves de p2 medido respecto p1
	   versor Escala el punto en cuestion para tener modulo 1 */

	/** rotate theta degrees about the x axis *///DUPLICAMOS METODOS PARA GRADOS Y RADIANES
	void giroxr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Ny = (float) (y * ct + z * st);
		float Nz = (float) (-y * st + z * ct);
		y = Ny;
		z = Nz;
	}
	void giroxg (double thetag)
	{
		giroxr (thetag * (Math.PI / 180));
	}			//GRADOS

	/** rotate theta degrees about the y axis */
	void giroyr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Nx = (float) (x * ct + z * st);
		float Nz = (float) (-x * st + z * ct);
		x = Nx;
		z = Nz;
	}
	void giroyg (double thetag)
	{
		giroyr (thetag * (Math.PI / 180));
	}			//GRADOS

	/** rotate theta degrees about the z axis */
	void girozr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Nx = (float) (x * ct + y * st);
		float Ny = (float) (-x * st + y * ct);
		x = Nx;
		y = Ny;
	}
	void girozg (double thetag)
	{
		girozr (thetag * (Math.PI / 180));
	}			//GRADOS

//METODOS RAPIDOS para los giros del visualizador, con cosenos y senos directore

	void rgirox (float ct, float st)
	{
		float Ny = y * ct + z * st;
		float Nz = -y * st + z * ct;
		y = Ny;
		z = Nz;
	}
	void rgiroy (float ct, float st)
	{
		float Nx = x * ct + z * st;
		float Nz = -x * st + z * ct;
		x = Nx;
		z = Nz;
	}
	void rgiroz (float ct, float st)
	{
		float Nx = x * ct + y * st;
		float Ny = -x * st + y * ct;
		x = Nx;
		y = Ny;
	}

   /** rotate theta degrees about the x axis */
	pto3D ngiroxr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Ny = (float) (y * ct + z * st);
		float Nz = (float) (-y * st + z * ct);
		pto3D sal = new pto3D (x, Ny, Nz);
		return sal;
	}
	pto3D ngiroxg (double thetag)
	{
		return ngiroxr (thetag * (Math.PI / 180));
	}			//GRADOS


	/** rotate theta degrees about the y axis */
	pto3D ngiroyr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Nx = (float) (x * ct + z * st);
		float Nz = (float) (-x * st + z * ct);
		pto3D sal = new pto3D (Nx, y, Nz);
		return sal;
	}
	pto3D ngiroyg (double thetag)
	{
		return ngiroyr (thetag * (Math.PI / 180));
	}			//GRADOS

	/** rotate theta degrees about the z axis */
	pto3D ngirozr (double theta)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		float Nx = (float) (x * ct + y * st);
		float Ny = (float) (-x * st + y * ct);
		pto3D sal = new pto3D (Nx, Ny, z);
		return sal;
	}
	pto3D ngirozg (double thetag)
	{
		return ngirozr (thetag * (Math.PI / 180));
	}			//GRADOS

    /** rotate theta degrees about the x axis y cierto punto*/
	void giroxr (double theta, pto3D paux)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		x = x - paux.x;
		y = y - paux.y;
		z = z - paux.z;
		float Ny = (float) (y * ct + z * st);
		float Nz = (float) (-y * st + z * ct);
		y = Ny;
		z = Nz;
		x = x + paux.x;
		y = y + paux.y;
		z = z + paux.z;
	}
	void giroxg (double thetag, pto3D pau)
	{
		giroxr (thetag * (Math.PI / 180), pau);
	}			//GRADOS


	/** rotate theta degrees about the y axis */
	void giroyr (double theta, pto3D paux)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		x = x - paux.x;
		y = y - paux.y;
		z = z - paux.z;
		float Nx = (float) (x * ct + z * st);
		float Nz = (float) (-x * st + z * ct);
		x = Nx;
		z = Nz;
		x = x + paux.x;
		y = y + paux.y;
		z = z + paux.z;
	}
	void giroyg (double thetag, pto3D pau)
	{
		giroyr (thetag * (Math.PI / 180), pau);
	}			//GRADOS

	/** rotate theta degrees about the z axis */
	void girozr (double theta, pto3D paux)
	{
		double ct = Math.cos (theta);
		double st = Math.sin (theta);
		x = x - paux.x;
		y = y - paux.y;
		z = z - paux.z;
		float Nx = (float) (x * ct + y * st);
		float Ny = (float) (-x * st + y * ct);
		x = Nx;
		y = Ny;
		x = x + paux.x;
		y = y + paux.y;
		z = z + paux.z;
	}
	void girozg (double thetag, pto3D pau)
	{
		girozr (thetag * (Math.PI / 180), pau);
	}			//GRADOS

///////////////////////////////////////////////////

	pto3D ngirar (double theta, pto3D eje)
	{
		pto3D pplano = this.proyeccplano (eje);
		pto3D pparal = this.menos (pplano);
		double radio = pplano.modulo ();
		pto3D ejsecundario = eje.prodvect (pplano);
		pto3D ejx = pplano.aversor ();
		pto3D ejy = ejsecundario.aversor ();
		pto3D vgirado = ejx.escala (radio * Math.cos (theta)).mas (ejy.escala (radio * Math.sin (theta)));

		pto3D ptogirado = pparal.mas (vgirado.escala (radio));

		return ptogirado;
	}
	pto3D ngirag (double thetag, pto3D pau)
	{
		return ngirar (thetag * (Math.PI / 180), pau);
	}			//GRADOS

/////////////////////////////////////////////////
	pto3D mas (pto3D pto2)
	{
		pto3D suma = new pto3D ();
		suma.x = this.x + pto2.x;
		suma.y = this.y + pto2.y;
		suma.z = this.z + pto2.z;
		return suma;
	}

	pto3D menos (pto3D pto2)
	{
		pto3D resta = new pto3D ();
		resta.x = this.x - pto2.x;
		resta.y = this.y - pto2.y;
		resta.z = this.z - pto2.z;
		return resta;
	}

	double prodesc (pto3D pto2)
	{
		double prodesc;
		prodesc = this.x * pto2.x + this.y * pto2.y + this.z * pto2.z;
		return prodesc;
	}


	pto3D prodvect (pto3D pto2)
	{
		pto3D pv = new pto3D ();
		pv.x = this.y * pto2.z - this.z * pto2.y;
		pv.y = this.z * pto2.x - this.x * pto2.z;
		pv.z = this.x * pto2.y - this.y * pto2.x;
		return pv;
	}

	double dista (pto3D pto2)
	{
		double dist;
		pto3D vec, pto1;
		pto1 = this;
		vec = pto1.menos (pto2);
		double prod = vec.prodesc (vec);
		dist = Math.sqrt (prod);
		return dist;
	}

	pto3D escala (double factor)
	{
		pto3D res = new pto3D (this.x * factor, this.y * factor,
				       this.z * factor);
		return res;
	}

	double anguloconr (pto3D pto2)
	{
		double mod1 = modulo ();
		double mod2 = pto2.modulo ();
		double pe = prodesc (pto2) / mod1 / mod2;
		if (pe < -1.)
			pe = -1.;
		if (pe > 1.)
			pe = 1.;
		double sal = Math.acos (pe);
		return sal;
	}
	double angulocong (pto3D pto2)
	{
		return anguloconr (pto2) * 180.0 / Math.PI;
	}

/*String anguloconrp(pto3D pto2){                 //Metodo de prueba que da salida de texto
	double mod1=Math.sqrt(this.prodesc(this));
	double mod2=Math.sqrt(pto2.prodesc(pto2));
	double pe=pto2.prodesc(this);
	double sal=0;
	String salt="";
	pto3D v1=this.aversor();
	pto3D v2=pto2.aversor();
	double d=v1.dista(v2);
	sal=180.0/Math.PI*Math.acos(pe/mod1/mod2);
	salt="los vectores v1 y v2 son: "+this.aTexto()+" "+pto2.aTexto()+" su prod esc es: "+pe/mod1/mod2+" el acos es "+Math.acos(pe/mod1/mod2)+" y estan separados una distancia "+d+" produciendo una salida "+sal;
	return salt;}*/

	double modulo ()
	{
		double mod2 = this.prodesc (this);
		return Math.sqrt (mod2);
	}


	pto3D proyeccplano (pto3D pto2)
	{
		double mo = pto2.modulo ();	//versor pto2
		pto3D vers2 = pto2.escala (1 / mo);
		double mod2 = this.prodesc (vers2);	//proyeccion escalar
		pto3D ptoplo = vers2.escala (mod2);
		pto3D proy = this.menos (ptoplo);
		return proy;

	}

	double dihedror (pto3D ptoc, pto3D pto1)
	{			//ACLARACION dihedro positivo es cuando, mirando en el sentido marcado
		pto3D p2 = this.proyeccplano (ptoc);	//por el vector (ptoc), el vector (pto1) esta a la derecha de (this)
		pto3D p1 = pto1.proyeccplano (ptoc);
		double res = p1.anguloconr (p2);
		pto3D pp = ptoc.prodvect (p1);
		pto3D ppc = pp.escala (-1);
		if (p2.dista (pp) > p2.dista (ppc))
			res = res * -1;
		return res;
	}

	double dihedrog (pto3D ptoc, pto3D pto1)
	{
		return dihedror (ptoc, pto1) * 180.0 / Math.PI;
	}
/*String dihedrorp(pto3D ptoc,pto3D pto1){	//ACLARACION dihedro positivo es cuando, mirando en el sentido marcado
	  pto3D p2=this.proyeccplano(ptoc);	//por el vector (ptoc), el vector (pto1) esta a la derecha de (this)
	  pto3D p1=pto1.proyeccplano(ptoc);
	  double res=p1.angulocon(p2);
	  String st=p1.anguloconp(p2);
	  pto3D pp =ptoc.prodvect(p1);
	  pto3D ppc=pp.escala(-1);
	  if (p2.dista(pp) > p2.dista(ppc)) res=res*-1;
	String cad=p2.aTexto()+"  p1 "+p1.aTexto()+" resultado="+res+" y el angulop dice: "+st;
	return cad;}*/

	pto3D aversor ()
	{
		pto3D p = new pto3D (this.x, this.y, this.z);
		p.versoriza ();
		return p;
	}

	void versoriza ()
	{
		double mod = this.modulo ();
		pto3D pc = this.escala (1 / mod);
		this.x = pc.x;
		this.y = pc.y;
		this.z = pc.z;
	}

	String aTexto ()
	{
		formato f = new formato (7, "##0.000");
		String texto = f.aCadena (this.x) + "," + f.aCadena (this.y) + "," + f.aCadena (this.z);
		return texto;
	}

	pto3D clona ()
	{
		pto3D sal = new pto3D (this.x, this.y, this.z);
		return sal;
	}

	pto3D ptomediocon (pto3D v1)
	{
		return ptopondcon (v1, 0.5);
	}


	pto3D ptopondcon (pto3D v1, double param)
	{			//ESTABAMOS CREANDO UN VERSOR MEDIO PONDERADO DE 0 A 1
		//SI 0, se parece a this, si 1, a v1!
		pto3D salida = null;
		if (param < 0)
			salida = this.clona ();
		else if (param > 1)
			salida = v1.clona ();
		else {
			pto3D cone = v1.menos (this);
			salida = this.mas (cone.escala (param));
		}
		return salida;
	}

	pto2D a2D ()
	{
		return new pto2D (x, y);
	}

}
