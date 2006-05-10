class MoleculaT extends MoleculaB
{
	double R1, R2;
	pto3D TEST1;		//fin del tubo, vc que conecta fin de T1 y principio T2,eje del T2
	pto3D TESTC;
	pto3D TEST2;
	boolean std = false;	//dice si esta definido el segundo tubo

	  MoleculaT ()
	{
		this.TEST1 = new pto3D ();
		this.TEST2 = new pto3D ();
		this.TESTC = new pto3D ();
		this.R1 = 0;
		this.R2 = 0;
	}

//LISTA DE METODOS !!!
/*void addVert(pto3D punto,int numeroatomico)
  void addVert(double x, double y, double z, int tip,Color c, double ra)
  void addVert(double x, double y, double z, String et,Color c, double radio)
  void addVert(double x, double y, double z, int tip)
  void addVert(double x, double y, double z)   DESHABILITADO!!!

 double getDim()
 double getDim()

void vaciar ()
void deseleccionar()
void centrar()
void girox(double th)
void addgrid             RESTOS DE OTRI¿O PROYECTO
void rmlast(int n)
void rmlast()

boolean ocupa1(pto3D pto1)
boolean ocupa2(pto3D pto1)
boolean ocupa(pto3D pto1, double limite)
int     atomoqueocupa1(pto3D pto)
int     atomoqueocupa2(pto3D pto)
int     atomoqueocupa(pto3D pto,double limite)

void    sustituye(int num,double x, double y, double z)
void    sustituye(int num,pto3D pto)
void    proyecta(Molecula maux)
void    proyecta(Molecula maux)
void    proyecta(int sus, Molecula maux)
pto3D   proyecta(pto3D sustituido,Molecula maux)
void    colorea(anillo an)                               OJO ANTIGUO
void    ponconec()
int     nvec (int n)
void    centraentorno(int num)
void    centraentorno()

String refina(anillo anori)
anillo findring(pto3D ptoref, int ref)        encuaentra un anillo
int generaanillo(int a1,int a2, pto3D cideprev, Molecula maux)*/

	MoleculaT clonaT ()
	{			///ATENCION; AUNQUE NO SE USA; ESTE METODO CLONA LA MOLECULA CON CARACTERSTICAS DE TUBO
		/// SI SE USA SOLO EL METODO CLONA; EL RESULTADO ES UNA MOLECULA BASICA
		MoleculaT mo = new MoleculaT ();
		for (int i = 0; i < this.nvert (); i++) {
			Atomo a = (Atomo) this.susatomos.get (i);
			mo.susatomos.add (a);
		}
		mo.TEST1 = this.TEST1;
		mo.TEST2 = this.TEST2;
		mo.TESTC = this.TESTC;
		mo.R1 = this.R1;
		mo.R2 = this.R2;
		return mo;
	}

	void proyecta (MoleculaT maux)  // proyecta --> literally, "it projects": something to do with projections
	{
		proyecta (nvert () - 1, maux);
	}			//Insisto, el ultimo es nvert-1

	void proyecta (int i)
	{
		if (i > nvert () - 1)
			return;
		pto3D sustituible = vert (i);
		MoleculaT molau = new MoleculaT ();
		pto3D sustituido = proyecta (sustituible, molau);
		mueve (i, sustituido);
	}

	// THIS AUTHORIZES US TO ELIMINATE THE MAUX USE
	pto3D proyecta (pto3D psus)	//ESTO NOS AUTORIZA PARA ELIMINAR EL USO DE MAUX
	{
		MoleculaT molau = new MoleculaT ();
		pto3D res = proyecta (psus, molau);
		return res;
	}

	void proyecta (int sus, MoleculaT maux)
	{
		pto3D sustituible = vert (sus);
		pto3D sustituido = proyecta (sustituible, maux);
		mueve (sus, sustituido);
	}

	pto3D proyecta (pto3D sustituido, MoleculaT maux)
	{			//los puntos auxiliares se ponen en la molecula auxiliar, pa que no incordien
		// the auxiliary points are put in the auxiliary molecule, pa that do not incordien
		pto3D pto = sustituido.clona ();	//El punto a proyectar (copia, claro)
		pto3D pt = pto.menos (TEST1);	//respecto al final del primer tubo
		pto3D pp = pt.proyeccplano (TESTC);	//se proyecta en el plano TC
		pto3D pl = pp.prodvect (TESTC);	//y este (pl) es el plano sobre el que todo tiene que transcurrir
		pto3D pc = pl.prodvect (TEST1);	//y este (pc) es el vector comun perteneciente a los planos pl y TEST1

		pc = pc.escala (-1);
		pc.versoriza ();	//asociado a esto de arriba!

		pto3D pc2 = pc.escala (R1);	//PC2 es el primer pto contenido en el primer circulo que marca la linea que una ambos circulos
		pto3D pc3 = pc2.mas (TEST1);
		//maux.addVert(pc3.x,pc3.y,pc3.z,7); //VERDE
		pp.versoriza ();
		pto3D pp2 = pp.escala (R2);	// y ahora PP2 es el pto contenido en el segundo circulo
		//maux.addVert(TESTC.mas(TEST1),2);          //Verde
		//maux.addVert(pp2.mas(TESTC).mas(TEST1),3); //MAGENTA

		pto3D p12 = pp2.menos (pc2).mas (TESTC);
		pto3D p = pt.menos (pc2);
		pto3D p12v = p12;
		p12v.versoriza ();
		double proyecfin = p12.prodesc (p);
		p12 = p12v.escala (proyecfin);
		pto3D pfin = TEST1.mas (pc2).mas (p12);	//Proyeccion en heterounion

		//EN PRIMER TUBO
		pto3D vt1 = TEST1.aversor ();
		pto3D proy1 = vt1.escala (vt1.prodesc (pto));
		pto3D ppp1 = pto.menos (proy1);
		double R1old = ppp1.modulo ();
		pto3D sust1 = proy1.mas (ppp1.escala (R1 / R1old));

		//EN SEGUNDO TUBO
		pto3D vt2 = TEST2.aversor ();
		pto3D proy2 = vt2.escala (vt2.prodesc (pto));
		pto3D ppp2 = pto.menos (proy2);
		double R2old = ppp2.modulo ();
		pto3D sust2 = proy2.mas (ppp2.escala (R2 / R2old));

		pto3D sustitucion = new pto3D ();

		if (sustituido.x <= TEST1.x)
			sustitucion = sust1.clona ();
		else {
			if (std == true) {
				pto3D u = sustituido.menos (TEST1);
				pto3D v = TESTC.aversor ();
				double pro = u.prodesc (v);

				if (pro > TESTC.modulo ())
					sustitucion = sust2.clona ();
				else
					sustitucion = pfin.clona ();
			} else {
				sustitucion = pfin.clona ();
			}

		}

		return sustitucion;
	}


	void centraentorno (int num)	//ESTA REPE??
	{
		pto3D pto = vert (num);
		int numvert = this.nvec (num);
		pto3D posnueva = new pto3D ();
		if (numvert == 3) {
			for (int i = 0; i < nvert (); i++) {
				pto3D ptov = vert (i);
				if (ptov.dista (pto) < 1.6)
					posnueva = posnueva.mas (ptov.escala (0.333));
			}
			mueve (num, posnueva);
		}
	}

	void centraentorno ()   // literally, "it centers surroundings"
	{
		centraentorno (this.nvert () - 1);
	}

	// Terminate any unfinished hexagons at the end of a nanotube with hydrogens.
	void cierraH ()  // cierra --> it closes, H -> hydrogen
	{			//ESTABLECER EN FUNCION DE RADIO Y ORIENTACION HEXAGONO
		// TO ESTABLISH BASED ON RADIUS AND HEXAGONAL DIRECTION
		for (int i = 0; i < nvert (); i++) {

			int pos = i;
			int mc[] = ((Atomo) susatomos.get (i)).mconec;

			if (mc[0] == 1) {	//Sustitucion
				int conec = mc[1];
				pto3D conexold = vert (pos).menos (vert (conec));
				pto3D conexnew = conexold.aversor ().escala (1.1);
				sustituye (pos, 1, vert (conec).mas (conexnew));
			} else if (mc[0] == 2) {
				pto3D cona = vert (pos).menos (vert (mc[1]));
				pto3D conb = vert (pos).menos (vert (mc[2]));
				pto3D conexold = cona.mas (conb);
				pto3D conexnew = conexold.aversor ().escala (1.1);
				addVert (vert (pos).mas (conexnew), 1);

			}
		}
		return;

	}

	// Terminate any unfinished hexagons at the end of a nanotube with nitrogens.
	void cierraN ()  // cierra --> it closes, N -> nitrogen
	{

		for (int i = 0; i < nvert (); i++) {

			int pos = i;
			int mc[] = ((Atomo) susatomos.get (i)).mconec;
			//La logica es la siguiente: Si la conectividad es 1, eliminamos y vemos el siguiente, si es uno, se elimina y se sigue
			//hasta que sea dos, en cuyo caso se sustituye por un nitro.
			//Hay un problema, cuando se elimina un atomo, las conectividades no se actualizan, por lo que debemos, en un primer paso,
			//marcar todas las que hay que eliminar, y al final, de un plumazo, quitarlas todas.
			//Para mracarlo, aprovechaos la variable selec de cada atomo, una marca que permanece indeleble indepen
			//dientemente de lo que borremos
			if (mc[0] == 1) {	//eliminacion sustitucionN

				boolean sale = false;
				marcaborra (i);	//lo marcamos para borrar el primero
				int atprev = i;	//inicializamos la variable del atomo previo
				int conectado = mc[1];	//y el atomo conectado
				for (; sale = false;) {
					int mctemp[] = ((Atomo) susatomos.get (conectado)).mconec;	//Matriz conectividad del conectado
					if (mctemp[0] == 1) {
						marcaborra (conectado);
						sale = true;
					}
					//se acabo, el hilo se corta, se marca como borrable, y se sale
					else if (mctemp[0] == 2) {	//de todos modos marcamos para borrar, v
						marcaborra (conectado);
						if (mctemp[1] != atprev) {
							atprev = conectado;
							conectado = mctemp[1];
						}	//la pos 1 es la siguien
						else if (mctemp[2] != atprev) {
							atprev = conectado;
							conectado = mctemp[2];
						}	//la pos 2 es la sig en
						else {
							sale = true;
						}	//en caso de error
					}
					//seguimos,
					else if (mctemp[0] == 3) {
						sale = true;
					}
					//llegamos al final, salimos y dejamos la sustitucion para luego.
					else
						sale = true;
					//llegamos a un nudo, no marcamos el conectado, ya que forma parte del nudo. No sustituimos nada
				}
			}
		}

		borramarcados ();
		//jolin!, hay que recalcular la conectividad una sola vez OJO a este valor
		ponconec (1.4);

		for (int i = 0; i < nvert (); i++) {	//HAcemos un segundo pase para nitrar los flecos cerrados sobre si mismos

			int pos = i;
			int mc[] = ((Atomo) susatomos.get (i)).mconec;


			if (mc[0] == 2) {	// Sustitucion N y no hace falta ver conectividades de nuevo, porque ya esta bien, y lo que hariamos
				// seria mezclarlo todo
				sustituye (pos, 7, vert (pos));
			}
		}

		return;
	}


	int remataconec ()	//METODO A usar solo con estructuras grafiticas
	{
		int nr = 0;
		for (int i = 0; i < nvert () - 1; i++) {
			int mc1[] = ((Atomo) susatomos.get (i)).mconec;
			double distamin = 10;	//en A. Solo se conec si la distamin es menor que el vector  de la celda, 2.46 (o mejor, 2.2 porseguridad)
			int enlazado = 0;
			if (mc1[0] == 2)
				for (int j = i + 1; j < nvert (); j++) {
					int mc2[] = ((Atomo) susatomos.get (j)).mconec;
					//AHora si, si ambas conectividades son dos, planteamos si son o no enlazables.
					if (mc2[0] == 2) {
						double dis = vert (i).dista (vert (j));
						if (dis < distamin) {
							distamin = dis;
							enlazado = j;
						}
					}
				}
			if (distamin < 2.2) {
				conecta (i, enlazado);
				nr++;
			}
		}
		return nr;
	}
	void remataconec2 ()	//Metodo alternatiov, que revisa todos los atomos con
		//falta d econectividad
	{			//Definimos un array que marca las conectividades rapidamente.

		//Primero marcamos a los atomos con solo dos conectividades

		//revisamos los marcados,

		//primero, examinamos un cono estrecho, y escogemos el atomo mas proximo

		//si no, ampliamos el cono, pero reducimos el radio que se puede conectar a 2.2


		//Desmarcamos, y marcamos los que tienen una conectividad

		//Donde estamos? tenemos que localizar el eje?

		//Desmarcamos, y marcamos los que no tienen conectividad.

		//Buscamos el atomo mas proximo


	}


	String exploraanillo (int atocentro)
	{			//ESTA ES LA AARIABLE EMTRE = Y ! QUE DICE SI EL ALGORITMO ES
		// TOTALMENTE RELAJADO (1)(SIGUIENDO PARAMETROS DE VECINO)
		// o estricto (0) (SIGUENDO conectividad TRIGONAL)
		double P = 0.5;
		int mc[] = ((Atomo) susatomos.get (atocentro)).mconec;
		pto3D ptocentro = vert (atocentro);
		int atobif = 0;

		if (mc[0] == 1) {
			atobif = mc[1];	//el atomo de la bifurcacion


			//HAY un caso es pecial en el que por el momento solo se ha conectado uno, y ene ese caso la conecti
			//vidad del atomo bifurcado no es 3, sino 2. En ese caso, el algoritmo esta capado, y solo existira un posible anillo.
			if (mc[0] == 2) {
				anillo an = new anillo ();
				an.addVert (atocentro);
				an.addVert (atobif);
				if (mc[1] != atocentro)
					an.addVert (mc[1]);
				else
					an.addVert (mc[2]);

				//ya tenemos tres, sigamos con el algoritmo estandar
				boolean as = true;	//Por defecto pensamos que el anillo sigue
				for (int i = 3; as; i++)	//as es anillosigue: chequea si el anillo tiene continuidad
				{
					boolean admitido = false;
					int mci[] = ((Atomo) susatomos.get (an.vert[i])).mconec;
					for (int k = 1; k <= mci[0]; k++)	//Buscamos entre todos los conectados
					{
						int cdto = mci[k];	//este es el candidato
						double dhd = dihedro (cdto,
								      an.vert[i],
								      an.vert[i - 1],
								      an.vert[i - 2]);
						//que forma un diedro con los veteranos de ana
						if ((cdto != an.vert[i - 1])
						    && (Math.abs (dhd) < 90.0)) {
							an.addVert (cdto);
							admitido = true;
						}
						//Y lo sumamos a ana si no vamos a atras y es razonablemente plano...
					}
					//Una vez recorridos todos los candidatos,chequeamos
					//las posibilidades que haran que as sea falso
					//Que ninguno haya sido admitido
					if (admitido == false)
						as = false;
					//que el admitido no tenga vecinos (pero eso es imposible, ya tiene como minimo 1
				}

				//Y ya tenemos el anillo. Actuaciones:
				if (an.num == 6) {	//conexion y orientacion con 5
					conecta (an.vert[1], an.vert[6]);
					pto3D v = vert (an.vert[5]).menos (vert (an.vert[4]));
					v.versoriza ();
					double bond = dmedia (an);
					pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
					pto3D ptopro = vert (an.vert[2]).mas (ve);
					ptopro = proyecta (ptopro);
					mueve (atocentro, ptopro);
					return "Caso 6 en conectividad 2 del bifurcado";
				} else if (an.num == 5) {	//orientacion con 5
					pto3D v = vert (an.vert[5]).menos (vert (an.vert[4]));
					v.versoriza ();
					double bond = dmedia (an);
					pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
					pto3D ptopro = vert (an.vert[2]).mas (ve);
					ptopro = proyecta (ptopro);
					mueve (atocentro, ptopro);
					return "Caso 5 en conectividad 2 del bifurcado";
				} else if (an.num < 5) {
					return "atomo libre";
				}
			}
			//Puerta que ahora si que impide que se haga todo el proceso si la conectividad es distinta de 3
			int mcbif[] = ((Atomo) susatomos.get (atobif)).mconec;
			if (mcbif[0] != 3)
				return "Atomo bifurcado presenta mala conectividad (" + mcbif[0] + ")";

			anillo ana = new anillo ();
			anillo anb = new anillo ();

			ana.addVert (atocentro);
			ana.addVert (atobif);
			anb.addVert (atocentro);
			anb.addVert (atobif);

			int j = 0;
			for (int i = 1; i <= 3; i++) {
				int cd4 = mcbif[i];

				if (cd4 == atocentro) {
				} else {
					j++;
					if (j == 1)
						ana.addVert (cd4);
					else if (j == 2)
						anb.addVert (cd4);
					else
						return "Error indeterminado: anillos A y B tienen " + ana.num + " y " + anb.num + " miembroe: Atobif es " +
							atobif;
				}
			}

			//Y ahora, un camino para cada uno de los anillos ya diferenciados entre si

			boolean asa = true;	//Por defecto pensamos que el anillo sigue
			for (int i = 3; asa; i++)	//as es anillosigue: chequea si el anillo tiene continuidad
			{
				boolean admitido = false;
				int mci[] = ((Atomo) susatomos.get (ana.vert[i])).mconec;
				for (int k = 1; k <= mci[0]; k++)	//Buscamos entre todos los conectados
				{
					int cdto = mci[k];	//este es el candidato
					double dhd = dihedro (cdto, ana.vert[i],
							      ana.vert[i - 1],
							      ana.vert[i - 2]);
					//que forma un diedro con los veteranos de ana
					if ((cdto != ana.vert[i - 1])
					    && (Math.abs (dhd) < 90.0)) {
						ana.addVert (cdto);
						admitido = true;
					}
					//Y lo sumamos a ana si no vamos a atras y es razonablemente plano...
				}
				//Una vez recorridos todos los candidatos,
				//chequeamos las posibilidades que haran que as sea falso
				//Que ninguno haya sido admitido
				if (admitido == false)
					asa = false;
				//que el admitido        no tenga vecinos (pero eso es imopsible, ya tiene como minimo 1
			}

			boolean asb = true;	//Por defecto pensamos que el anillo sigue
			for (int i = 3; asb; i++)	//as es anillosigue: chequea si el anillo tiene continuidad
			{
				boolean admitido = false;
				int mci[] = ((Atomo) susatomos.get (anb.vert[i])).mconec;
				for (int k = 1; k <= mci[0]; k++)	//Buscamos entre todos los conectados
				{
					int cdto = mci[k];	//este es el candidato
					double dhd = dihedro (cdto, anb.vert[i],
							      anb.vert[i - 1],
							      anb.vert[i - 2]);
					//que forma un diedro con los veteranos de ana
					if ((cdto != anb.vert[i - 1])
					    && (Math.abs (dhd) < 90.0)) {
						anb.addVert (cdto);
						admitido = true;
					}
					//Y lo sumamos a ana si no vamos a atras y es razonablemente plano...
				}
				//Una vez recorridos todos los candidatos,chequeamos las posibilidades que haran que as sea falso
				//Que ninguno haya sido admitido
				if (admitido == false)
					asb = false;
				//que el admitido        no tenga vecinos (pero eso es imopsible, ya tiene como minimo 1
			}

			//Y ahora, una vez que conocemos los dos anillos que estan conectados, vemos el numero de vertices que tienen
			//si es menor que 5, no hacer nada, es una posicion libre


//EMPEZAMOS LOS CASOS DE UN MODO ORDENADO/////////////////////////////////////////////////////////////////////////////////

			if ((ana.num == 6) && (anb.num == 6)) {	//Si ambos son 6, lo ponemos en el centro de los tres posiciones circundantes.
				pto3D ppro = (vert (ana.vert[6]).mas (vert (anb.vert[6])).mas (vert (ana.vert[2]))).escala (0.333);
				mueve (atocentro, ppro);
				return "Caso 6,6: Atomo encastrado entre " + ana.vert[6] + ", " + anb.vert[6] + " y " + ana.vert[2];
			} else if ((ana.num == 6) && (anb.num < 5))
				//SI alguno es 6, se conecta y se hace que sea paralelo al enlace guia del anillo
			{
				conecta (ana.vert[1], ana.vert[6]);
				pto3D v = vert (ana.vert[5]).menos (vert (ana.vert[4]));
				v.versoriza ();
				double bond = dmedia (ana);
				pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
				pto3D ptopro = vert (ana.vert[2]).mas (ve);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				return "Caso 6,X: desplazamiento lateral guiado por atomo " + ana.vert[5] + " D enlace= " + bond;
			}

			else if ((anb.num == 6) && (ana.num < 5)) {
				conecta (anb.vert[1], anb.vert[6]);
				pto3D v = vert (anb.vert[5]).menos (vert (anb.vert[4]));
				v.versoriza ();
				double bond = dmedia (anb);
				pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
				pto3D ptopro = vert (anb.vert[2]).mas (ve);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				return "Caso 6,X: desplazamiento lateral guiado por atomo " + anb.vert[5] + " D enlace= " + bond;
			}

			else if ((ana.num == 5) && (anb.num == 5))
				//Si ambos son 5, perfecto, hasta podemos ver si la posicion propuesta cae enmedio de los dos ultimos cuernos
			{
				pto3D v1 = vert (ana.vert[5]).menos (vert (ana.vert[4]));
				pto3D v2 = vert (anb.vert[5]).menos (vert (anb.vert[4]));
				pto3D vm = vert (ana.vert[1]).menos (vert (ana.vert[2]));
				pto3D vr = v1.mas (v2);
				vm.versoriza ();
				double bond1 = dmedia (ana);
				double bond2 = dmedia (anb);
				pto3D vme = vm.escala (bond1 / 2 + bond2 / 2);	//PARAMETRO FLEXIBLE
				pto3D ptopro = vert (ana.vert[2]).mas (vme);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				//aqui quizas habria que poner un limitador de angulo, por ahora solo se pone un warning
				return "Caso 5,5: desplazamiento lateral guiado por atomos " + anb.vert[5] + " y " + ana.vert[5] + " D enlace= " + (bond1 / 2 +
																		    bond2 / 2);
			}

			else if ((ana.num == 5) && (anb.num == 6)) {
				conecta (anb.vert[1], anb.vert[6]);
				pto3D pmed = vert (anb.vert[6]).menos (vert (anb.vert[2])).escala (0.5);
				double dmed = pmed.modulo ();
				pto3D v1 = vert (ana.vert[5]).menos (vert (ana.vert[4]));
				pto3D v2 = vert (anb.vert[5]).menos (vert (anb.vert[4]));
				pto3D vm = vert (ana.vert[1]).menos (vert (ana.vert[2]));
				pto3D vr = v1.mas (v2);
				double angu = vr.angulocong (pmed);

				double dbond = dmed / Math.cos (Math.PI / 180 * angu);	//OJO A ESTA FLEXIBILIDAD; NO SE TOCA
				//atenuamos las longitudes de enlace un poco
				if (dbond > 1.8)
					dbond = dbond - (dbond - 1.8) / 2;
				if (dbond > 1.2)
					dbond = dbond - (dbond - 1.2) / 2;
				vr.versoriza ();
				pto3D vre = vr.escala (dbond);

				pto3D ptopro = vert (ana.vert[2]).mas (vre);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				return "Caso 5,6: PRIMERO desplazamiento lateral y guiado por atomo " + anb.vert[6] + " D enlace= " + dbond;
			}

			else if ((ana.num == 5) && (anb.num <= 4)) {	//hacemos que sea paralelo al brazo 5
				pto3D v = vert (ana.vert[5]).menos (vert (ana.vert[4]));
				v.versoriza ();
				double bond = dmedia (ana);
				pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
				pto3D ptopro = vert (ana.vert[2]).mas (ve);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				return "Caso 5,X: desplazamiento lateral guiado por atomo " + ana.vert[5] + " D enlace= " + bond;
			}

			else if ((anb.num == 5) && (ana.num == 6)) {
				conecta (ana.vert[1], ana.vert[6]);
				pto3D pmed = vert (ana.vert[6]).menos (vert (ana.vert[2])).escala (0.5);
				double dmed = pmed.modulo ();
				pto3D v1 = vert (ana.vert[5]).menos (vert (ana.vert[4]));
				pto3D v2 = vert (anb.vert[5]).menos (vert (anb.vert[4]));
				pto3D vm = vert (ana.vert[1]).menos (vert (ana.vert[2]));
				pto3D vr = v1.mas (v2);
				double angu = vr.angulocong (pmed);

				double dbond = dmed / Math.cos (Math.PI / 180 * angu);
				//atenuamos las longitudes de enlace un poco
				if (dbond > 1.8)
					dbond = dbond - (dbond - 1.8) / 2;
				if (dbond < 1.2)
					dbond = dbond - (dbond - 1.2) / 2;	//OJO ESTO PUED SE IMPORTANTE? EN VE Z DE < habia >

				vr.versoriza ();
				pto3D vre = vr.escala (dbond);

				pto3D ptopro = vert (ana.vert[2]).mas (vre);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);
				return "Caso 5,6:SEGUNDO desplazamiento lateral y guiado por atomo " + ana.vert[6];
			} else if ((anb.num == 5) && (ana.num <= 4)) {
				pto3D v = vert (anb.vert[5]).menos (vert (anb.vert[4]));

				v.versoriza ();

				double bond = dmedia (anb);
				pto3D ve = v.escala (bond);	//OJO A ESTOS PARAMETROS; DEBERIAN SER FLEXIBLES
				pto3D ptopro = vert (anb.vert[2]).mas (ve);
				ptopro = proyecta (ptopro);
				mueve (atocentro, ptopro);

				return "Caso 5,X: desplazamiento lateral guiado por atomo " + anb.vert[5] + " D enlace= " + bond;
			}
			//Pensar en las posibles deformaciones (un anillo es de sais, otro de 5, pero el enlace creado es mucho mas largo
			//hay que ver si se tiene margen de maniobra en el otro lado, y se mueve.


			else
				return "Caso no recogido" + ana.num + "," + anb.num + ": Sin conexiones ni desplazamiento";



		}

		else if (mc[0] == 2) {
			//en este caso, aunque habitualmente no deberia producirse,
			//se produciria si al añadir una conexion se detecta un anillo  a la derecha, pero a su vez eso posibilita la existencia de un anillo superior

			//esa posibilidad no es nula, y se da en zonas con excesivos recovecos
			//para asegurarse hay que aplicar dos veces sequidas el algoritmo exploraanillo.!!!!!

			//Bueno, si tenemos dos, habra dos anillos en potencia, vease, a y b, que comparten el primer atomo
			//el segundo sera cada uno de los dos vecinos, y el tercero sera aquiel con diedro de unos 180 con el del otro anillo

			//INICIALIZACION DE ANILLOS

			anillo ana = new anillo ();
			anillo anb = new anillo ();

			ana.addVert (atocentro);
			ana.addVert (mc[1]);
			anb.addVert (atocentro);
			anb.addVert (mc[2]);

			boolean asa = false;	//hasta que no veamos el tercero, el anillo parece no sequir
			int mca2[] = ((Atomo) susatomos.get (ana.vert[2])).mconec;
			for (int i = 1; i <= mca2[0]; i++) {
				if ((mca2[i] != ana.vert[1]) && (Math.abs (dihedro (anb.vert[2], anb.vert[1], ana.vert[2], mca2[i])) > 90)) {
					asa = true;
					ana.addVert (mca2[i]);
				}
			}
			for (int i = 3; asa; i++)	//as es anillosigue: chequea si el anillo tiene continuidad
			{
				boolean admitido = false;
				int mci[] = ((Atomo) susatomos.get (ana.vert[i])).mconec;
				for (int k = 1; k <= mci[0]; k++)	//Buscamos entre todos los conectados
				{
					int cdto = mci[k];	//este es el candidato
					double dhd = dihedro (cdto, ana.vert[i],
							      ana.vert[i - 1],
							      ana.vert[i - 2]);
					//que forma un diedro con los veteranos de ana
					if ((cdto != ana.vert[i - 1])
					    && (Math.abs (dhd) < 90.0)) {
						ana.addVert (cdto);
						admitido = true;
					}	//Y lo sumamos a ana si no vamos a atras y es razonablemente plano...
				}
				//Una vez recorridos todos los candidatos,chequeamos las posibilidades que haran que as sea falso
				//Que ninguno haya sido admitido
				if (admitido == false)
					asa = false;
				//que el admitido        no tenga vecinos (pero eso es imopsible, ya tiene como minimo 1
			}


			boolean asb = false;	//hasta que no veamos el tercero, el anillo parece no sequir
			int mcb2[] = ((Atomo) susatomos.get (anb.vert[2])).mconec;
			for (int i = 1; i <= mcb2[0]; i++) {
				if ((mcb2[i] != anb.vert[1]) && (Math.abs (dihedro (ana.vert[2], ana.vert[1], anb.vert[2], mcb2[i])) > 90)) {
					asb = true;
					anb.addVert (mcb2[i]);
				}
			}

			for (int i = 3; asb; i++)	//as es anillosigue: chequea si el anillo tiene continuidad
			{
				int mci[] = ((Atomo) susatomos.get (anb.vert[i])).mconec;
				boolean admitido = false;
				for (int k = 1; k <= mci[0]; k++)	//Buscamos entre todos los conectados
				{
					int cdto = mci[k];	//este es el candidato
					double dhd = dihedro (cdto, anb.vert[i],
							      anb.vert[i - 1],
							      anb.vert[i - 2]);
					//que forma un diedro con los veteranos de ana
					if ((cdto != anb.vert[i - 1])
					    && (Math.abs (dhd) < 90.0)) {
						anb.addVert (cdto);
						admitido = true;
					}
					//Y lo sumamos a ana si no vamos a atras y es razonablemente plano...
				}
				//Una vez recorridos todos los candidatos,chequeamos las posibilidades que haran que as sea falso
				//Que ninguno haya sido admitido
				if (admitido == false)
					asb = false;
				//que el admitido        no tenga vecinos (pero eso es imopsible, ya tiene como minimo 1
			}

			//UNA VEZ detectados los anillos, pasamos a los casos y a las actuaciones

			//Si ambos son 6,
			if ((ana.num == 6) && (anb.num == 6)) {
				if (ana.vert[6] == anb.vert[6]) {
					conecta (ana.vert[1], ana.vert[6]);
					return "new connection between " + atocentro + " and " + ana.vert[6];
				} else
					return "excessive connections near atom " + atocentro;
			} else {
				if (ana.num == 6) {
					conecta (ana.vert[1], ana.vert[6]);
					return "new connection between " + atocentro + " and " + ana.vert[6];
				} else if (anb.num == 6) {
					conecta (anb.vert[1], anb.vert[6]);
					return "new connection between " + atocentro + " and " + anb.vert[6];
				} else
					return "No connection";
			}

		}

		else if (mc[0] == 3) {
			return "Atom " + atocentro + " is already tricoordinated";
		}

		else {
			String st = "Atom " + atocentro + " is shows " + mc[0] + " connectivity: It should be correctly connected";
			return st;
		}

	}


	double dmedia (anillo ani)
	{			//OJO, esta distancia media no incluye el enlace priemro, ani[1],ani[2], porque es el que va a ser sustituido
		double dm = 0;
		int n = ani.num - 2;
		for (int i = 2; i < ani.num; i++)
			dm = dm + distancia (ani.vert[i], ani.vert[i + 1]) / n;
		return dm;


	}


	public String pdb () {
		return pdb(null);
	}

	public String pdb (String inf) {
		formato fo = new formato (8, "#0.000");
		formato fdec = new formato (7, "#0.000");	//para los doble precision
		formato fi = new formato (5, "#####");	//para los enteros
		StringBuffer pdb = new StringBuffer
			("REMARK ==============================================================================\n");
		if (inf != null) pdb.append("REMARK " + inf + "\n");
		pdb.append("REMARK File generated by CoNTub 1.0 build 22. July 26th 2004\n" +
			   "REMARK Cite as: S.Melchor, J.A. Dobado. J. Chem. Inf. Comp. Sci. 44, 1639-1646 (2004)\n" +
			   "AUTHOR Software available at http://www.ugr.es/local/gmdm/java/contub/contub.html\n" +
			   "AUTHOR For questions and comments: http://www.ugr.es/local/gmdm\n" +
			   "REMARK ==============================================================================\n");
		
		Minimol mmol = new Minimol(this);
		for (int i = 0; i < mmol.nvert; i++) {
			String lab = mmol.minietiqs[i];
			// aCadena -> toString (lit. toChain)
			pdb.append ("HETATM" + fi.aCadena (i + 1) + "  " +
				    lab + "      " + fi.aCadena (i + 1) +
				    "    " +
				    fdec.aCadena (mmol.miniverts[i].x) +
				    fdec.aCadena (mmol.miniverts[i].y) +
				    fdec.aCadena (mmol.miniverts[i].z) + "\n");
		}
		for (int i = 0; i < mmol.nvert; i++)	//CONECTIVIDAD - CONNECTIVITY
		{
			pdb.append ("CONECT" + fi.aCadena (i + 1));
			for (int j = 1; j <= mmol.miniconec[i][0]; j++)
				pdb.append (fi.aCadena (mmol.miniconec[i][j] + 1));
			pdb.append ("\n");
		}
		pdb.append ("END");
		return pdb.toString();
	}


	public String mmp () {
		return mmp(null);
	}

	public String mmp (String inf) {
		formato fo = new formato (8, "#0.000");
		formato fdec = new formato (7, "#0.000");	//para los doble precision
		formato fi = new formato (5, "#####");	//para los enteros
		StringBuffer mmp = new StringBuffer
			("mmpformat 050920 required; 051103 preferred\n");
		if (inf != null) mmp.append("# " + inf + "\n");
		mmp.append("# File generated by CoNTub 1.0 build 22. July 26th 2004\n" +
			   "# Cite as: S.Melchor, J.A. Dobado. J. Chem. Inf. Comp. Sci. 44, 1639-1646 (2004)\n" +
			   "# Software available at http://www.ugr.es/local/gmdm/java/contub/contub.html\n" +
			   "# For questions and comments: http://www.ugr.es/local/gmdm\n" +
			   "# ==============================================================================\n" +
			   "kelvin 300\n" +
			   "group (View Data)\n" +
			   "info opengroup open = True\n" +
			   "csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000)" +
			   " (0.000000, 0.000000, 0.000000) (1.000000)\n" +
			   "csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.943023)" +
			   " (0.000000, 0.000000, 0.000000) (1.000000)\n" +
			   "egroup (View Data)\n" +
			   "group (Nanotube)\n" +
			   "info opengroup open = True\n" +
			   "mol (Nanotube-1) def\n");
		
		Minimol mmol = new Minimol(this);
		for (int i = 0; i < mmol.nvert; i++) {
			Atomo atm = (Atomo) susatomos.get(i);
			int tip1 = atm.tipo;
			mmp.append ("atom " + (i + 1) + " (" + atm.tipo + ") (" +
				    (int) (1000 * mmol.miniverts[i].x) + ", " +
				    (int) (1000 * mmol.miniverts[i].y) + ", " +
				    (int) (1000 * mmol.miniverts[i].z) + ") def\n");
			int[] neighborsG = new int[10];
			int[] neighbors1 = new int[10];
			int numneighborsG = 0;
			int numneighbors1 = 0;
			if (MOLDEBUG) {
				System.out.print("i " + i + " [");
				for (int j = 1; j <= mmol.miniconec[i][0]; j++) {
					int x = mmol.miniconec[i][j];
					Atomo atm2 = (Atomo) susatomos.get(x);
					System.out.print(" " + x);
				}
				System.out.println(" ]");
			}
			for (int j = 1; j <= mmol.miniconec[i][0]; j++) {
				int x = mmol.miniconec[i][j];
				Atomo atm2 = (Atomo) susatomos.get(x);
				if (x < i) {
					if (tip1 == 6 && atm2.tipo == 6) {
						// graphitic bond
						neighborsG[numneighborsG++] = x + 1;
					} else {
						// single bond
						neighbors1[numneighbors1++] = x + 1;
					}
				}
			}
			if (numneighbors1 > 0) {
				mmp.append("bond1");
				for (int k = 0; k < numneighbors1; k++)
					mmp.append(" " + neighbors1[k]);
				mmp.append("\n");
			}
			if (numneighborsG > 0) {
				mmp.append("bondg");
				for (int k = 0; k < numneighborsG; k++)
					mmp.append(" " + neighborsG[k]);
				mmp.append("\n");
			}
			
		}
		mmp.append ("egroup (Nanotube)\n" +
			    "group (Clipboard)\n" +
			    "info opengroup open = False\n" +
			    "egroup (Clipboard)\n" +
			    "end molecular machine part 1\n");
		return mmp.toString();
	}
}
