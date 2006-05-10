import java.awt.Color;
import java.util.Hashtable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.AbstractList;


class MoleculaB
{
	public static final boolean MOLDEBUG = false;

	ArrayList susatomos;	//de ATOMOS, literally, "his atoms"
	int nselec;
	String info;		//pequeña cadena informativa para pasar un mini titulo
	// small informative string to pass a short title
	formato fm = new formato (6, "###.0");
	double xmin, xmax, ymin, ymax, zmin, zmax;
	TabPe TablaP;   // periodic table - this could be a singlet

	  MoleculaB ()
	{
		susatomos = new ArrayList (0);
		TablaP = TabPe.getInstance();
		nselec = 0;
		info = "";
	}

//LISTA DE METODOS BASICOS!!!
//A REHACER!!

	void addVert (pto3D punto, int ti, Color c)
	{
		// punto --> point, position
		// ti is element number
		susatomos.add (new Atomo (punto, ti, c));
	}

	void addVert (pto3D punto, int ti)
	{
		susatomos.add (new Atomo (punto, ti));
	}

	void addVert (double x, double y, double z, int ti)
	{
		susatomos.add (new Atomo (new pto3D (x, y, z), ti));
	}

//Metodos para añadir etiquetas personalizadas
	void addVert (double x, double y, double z, int ti, String e)
	{
		addVert (x, y, z, ti);
		((Atomo) susatomos.get (susatomos.size ())).pers = e;
	}

	void addVert (pto3D p, int ti, String e)
	{
		addVert (p, ti);
		((Atomo) susatomos.get (susatomos.size ())).pers = e;
	}

	double getDim ()
	{
		double Dim = 0;
		if (susatomos.size () <= 1)
			return 0;
		for (int i = 0; i < susatomos.size (); i++) {
			for (int j = i + 1; j < susatomos.size (); j++) {
				pto3D v = ((Atomo) susatomos.get (i)).vert;
				pto3D w = ((Atomo) susatomos.get (j)).vert;
				double dist = v.dista (w);
				if (dist > Dim)
					Dim = dist;
			}
		}
		return Dim;
	}

	double getLejania ()
	{
		double lej = 0;
		if (susatomos.size () <= 1)
			return 0;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D v = ((Atomo) susatomos.get (i)).vert;
			pto3D c = new pto3D (0, 0, 0);
			double dist = v.dista (c);
			if (dist > lej)
				lej = dist;
		}
		return lej;
	}

	void vaciar ()
	{
		susatomos = new ArrayList (0);
		TablaP = TabPe.getInstance();
	}

	void deseleccionar ()
	{
		for (int i = 0; i < susatomos.size (); i++)
			((Atomo) susatomos.get (i)).selec = 0;
		nselec = 0;
	}
//HABRIA QUE PONER HERRAMIENTAS DE SELECCIONADO


	void centrar ()
	{
		if (susatomos.size () <= 0)
			return;
		double x = 0, y = 0, z = 0;
		int nv = susatomos.size ();
		for (int i = 0; i < nv; i++) {
			x = x + ((Atomo) susatomos.get (i)).vert.x / nv;
			y = y + ((Atomo) susatomos.get (i)).vert.y / nv;
			z = z + ((Atomo) susatomos.get (i)).vert.z / nv;
		}
		for (int i = 0; i < nv; i++) {
			((Atomo) susatomos.get (i)).vert.x -= x;
			((Atomo) susatomos.get (i)).vert.y -= y;
			((Atomo) susatomos.get (i)).vert.z -= z;
		}
	}

	void giroxr (double th)
	{
		for (int i = 0; i < susatomos.size (); i++) {
			((Atomo) susatomos.get (i)).vert.giroxr (th);
		}
	}
	void giroyr (double th)
	{
		for (int i = 0; i < susatomos.size (); i++) {
			((Atomo) susatomos.get (i)).vert.giroyr (th);
		}
	}
	void girozr (double th)
	{
		for (int i = 0; i < susatomos.size (); i++) {
			((Atomo) susatomos.get (i)).vert.girozr (th);
		}
	}

	void giroxg (double th)
	{
		giroxr (th / 180.0 * Math.PI);
	}
	void giroyg (double th)
	{
		giroyr (th / 180.0 * Math.PI);
	}
	void girozg (double th)
	{
		girozr (th / 180.0 * Math.PI);
	}

	MoleculaB clona ()
	{
		MoleculaB mo = new MoleculaB ();
		for (int i = 0; i < susatomos.size (); i++) {
			mo.susatomos.add (susatomos.get (i));
		}
		return mo;
	}

	void rm (int n)
	{
		if (n > susatomos.size () - 1)
			return;
		else
			susatomos.remove (n);
	}			//elimina elemento n (solo hasta size-1)

	void rmlast (int n)
	{
		for (int i = 1; i <= n; i++)
			this.rmlast ();
	}			//elimina los ultimos N elementos (repite nveces

	void rmlast ()
	{
		susatomos.remove (susatomos.size () - 1);
	}			//DELICADO: un array de 3 elementos tiene como ultimo el 3-1

	boolean ocupa1 (pto3D pto1)
	{
		boolean oc = false;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			double dist = pto2.dista (pto1);
			if (dist < 0.5)
				oc = true;
		}
		return oc;
	}

	boolean ocupa (pto3D pto1, double limite)
	{
		boolean oc = false;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			double dist = pto2.dista (pto1);
			if (dist < limite)
				oc = true;
		}
		return oc;
	}

	boolean ocupa2 (pto3D pto1)
	{
		boolean oc = false;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			double dist = pto2.dista (pto1);
			if (dist < 1.3)
				oc = true;
		}
		return oc;
	}

	int atomoqueocupa1 (pto3D pto)
	{
		int ocup = 0;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			if (pto.dista (pto2) < 0.5)
				ocup = i;
		}
		return ocup;
	}

	int atomoqueocupa (pto3D pto, double limite)
	{
		int ocup = 0;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			if (pto.dista (pto2) < limite)
				ocup = i;
		}
		return ocup;
	}

	int atomoqueocupa2 (pto3D pto)
	{
		int ocup = 0;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pto2 = ((Atomo) susatomos.get (i)).vert;
			if (pto.dista (pto2) < 1.3)
				ocup = i;
		}
		return ocup;
	}

	void mueve (int num, double x, double y, double z)
	{
		if (num < susatomos.size ())
			((Atomo) susatomos.get (num)).vert = new pto3D (x, y, z);
	}			//OJO A LAS SUSTITUCIONES //ANTES ERA SUSTITUYE

	void mueve (int s, pto3D pto)
	{
		if (s < susatomos.size ())
			((Atomo) susatomos.get (s)).vert = pto;
	}

	void sustituye (int num, int ti, pto3D pto)
	{
		if (num <= susatomos.size ())
			susatomos.set (num, new Atomo (pto, ti));
	}
//ESTA es una autentica sustitucion

	// A Bucket is a cube-sized container to represent the coarse positions of atoms. It is
	// used to find bonds faster - we can pre-sort the atoms into buckets, and when we want
	// to find nearby atoms quickly, we only need to search the nearby buckets.

	// Un Bucket es un envase cubo-clasificado para representar las posiciones gruesas de
	// átomos. Se utiliza para encontrar enlaces más rápidos - preclasificación de la poder los
	// átomos en los Buckets, y cuando deseamos encontrar los átomos próximos rápidamente,
	// nosotros necesitamos solamente buscar los Buckets próximos.

	private static final double BUCKETWIDTH = 1.5 * 1.24;

	private ArrayList getBucket(HashMap buckets, pto3D v) {
		int x = (int) ((v.x - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		int y = (int) ((v.y - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		int z = (int) ((v.z - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		Integer key = new Integer((x * 5000 + y) * 5000 + z);
		if (buckets.get(key) == null)
			buckets.put(key, new ArrayList());
		return (ArrayList) buckets.get(key);
	}

	// Search the 3x3x3 nearest buckets
	private ArrayList getNeighborhood(HashMap buckets, pto3D v) {
		int x = (int) ((v.x - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		int y = (int) ((v.y - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		int z = (int) ((v.z - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
		ArrayList alst = new ArrayList();
		for (int dx = -1; dx <= 1; dx++)
			for (int dy = -1; dy <= 1; dy++)
				for (int dz = -1; dz <= 1; dz++) {
					Integer key = new Integer(((x + dx) * 5000 + y + dy) * 5000 + z + dz);
					ArrayList alst2 = (ArrayList) buckets.get(key);
					if (alst2 != null)
						for (int i = 0; i < alst2.size(); i++) {
							Object atm = alst2.get(i);
							if (!alst.contains(atm))
								alst.add(atm);
						}
				}
		return alst;
	}

	void ponconec ()
	{
		ponconec (1.30);
	}

	void ponconec (double param)  // ponconec --> put connected??
	{
		HashMap buckets = new HashMap();
		int nv = susatomos.size ();
		for (int i = 0; i < nv; i++) {
			Atomo atm = (Atomo) susatomos.get (i);
			atm.index = i;
			pto3D ptoa = atm.vert;
			ArrayList alst = getBucket(buckets, ptoa);
			alst.add(atm);
		}
		for (int i = 0; i < nv; i++) {
			Atomo atm = (Atomo) susatomos.get (i);
			pto3D ptoa = atm.vert;
			int tipA = atm.tipo;

			//reiniciamos el array de conectividad
			// we reinitiated the connectivity Array 
			int mc[] = new int[10];
			mc[0] = 0;	//un array para cada atomo i
			// an Array for each atom i
			for (int j = 1; j <= 9; j++)
				mc[j] = 0;

			ArrayList alst = getNeighborhood(buckets, ptoa);
			for (int j = 0; j < alst.size(); j++) {
				Atomo atm2 = (Atomo) alst.get(j);
				pto3D ptob = atm2.vert;
				int tipB = atm2.tipo;
				double distamax = param * (TablaP.en1[tipA] + TablaP.en1[tipB]);	//PARAMETRO AQUI
				if (ptoa.dista (ptob) < distamax && ptoa.dista (ptob) > 0.6) {
					if (MOLDEBUG)
						System.out.println("Connect: " + i + " " + j);
					int k = mc[0] + 1;
					mc[0] = k;
					mc[k] = atm2.index;
				}
			}

			//y lo ponemos como un todo El array es mejor manejarlo como un todo, incluso seria
			//conveniente para girarlo, poder sacar y meter un vert[] solo de puntos, en funcion de su efectividad
			// and we put it as a whole the Array is better to handle it like a whole, serious even advisable to
			// turn it, to be able to remove and to put vert [] single of points, based on its effectiveness
			((Atomo) susatomos.get (i)).mconec = mc;
		}
		// depura --> it purifies
		depuraconec ();	//OJO!!!
	}

	void ponconecsafe ()
	{
		ponconec (1.1);
		//CONTINUAR LA ELIMINACION DE CONEXIIONES REDUNDANTES!!
		//TO CONTINUE THE ELIMINATION OF REDUNDANT CONNECTIONS!!
	}

	void reconec ()
	{
		reconec (1.30);
	}

	void reconec (double param)
	{			//IGUAL QUE PONCONEC; pero sin iniciar --> JUST AS PONCONEC; but without initiating
		HashMap buckets = new HashMap();
		int nv = susatomos.size ();
		for (int i = 0; i < nv; i++) {
			Atomo atm = (Atomo) susatomos.get (i);
			atm.index = i;
			pto3D ptoa = atm.vert;
			ArrayList alst = getBucket(buckets, ptoa);
			alst.add(atm);
		}
		for (int i = 0; i < nv; i++) {
			Atomo atm = (Atomo) susatomos.get (i);
			pto3D ptoa = atm.vert;
			int tipA = atm.tipo;

			ArrayList alst = getNeighborhood(buckets, ptoa);
			for (int j = 0; j < alst.size(); j++) {
				Atomo atm2 = (Atomo) alst.get(j);
				pto3D ptob = atm2.vert;
				int tipB = atm2.tipo;
				double distamax = param * (TablaP.en1[tipA] + TablaP.en1[tipB]);	//PARAMETRO AQUI
				if (ptoa.dista (ptob) < distamax && ptoa.dista (ptob) > 0.6)
					conecta (i, atm2.index);
			}
		}
		//depuraconec();                          //OJO!!!
	}

	void reconecsafe ()
	{
		reconec (1.1);
		//CONTINUAR LA ELIMINACION DE CONEXIIONES REDUNDANTES!!
		//TO CONTINUE THE ELIMINATION OF REDUNDANT CONNECTIONS!!
	}

	int depuraconec ()	//metodo paraeliminar conectividades redundantes, angulos demasiado pequeños (<60, en principio)
	{
		int dc = 0;
		for (int i = 0; i < susatomos.size (); i++) {
			pto3D pa = ((Atomo) susatomos.get (i)).vert;
			int mc[] = new int[10];
			mc = ((Atomo) susatomos.get (i)).mconec;
			for (int j = 1; j <= mc[0]; j++) {
				pto3D pb = ((Atomo) susatomos.get (mc[j])).vert;
				for (int k = 1; k <= mc[0]; k++) {
					pto3D pc = ((Atomo) susatomos.get (mc[k])).vert;

					//ahora la condicion para que
					double angulo = pb.menos (pa).angulocong (pc.menos (pa));

					if ((angulo < 60) && (angulo > 1)) {
						if (pb.dista (pa) < pc.dista (pa))
							desconecta (i, mc[k]);
						else
							desconecta (i, mc[j]);
						dc++;
					}
				}
			}

		}

		return dc;
	}



/*void ponconecOLD(){
 	for (int i=1;i<=nvert;i++){
 		pto3D ptoa=vert[i];

 		mconec[i][0]=0;
 		for (int j=1;j<=9;j++)mconec[i][j]=0;

 		for (int j=1;j<=nvert;j++){
 		     pto3D ptob=vert[j];
 		     if (ptoa.dista(ptob)<1.8 && ptoa.dista(ptob)>0.2)
 		       {int k=mconec[i][0]+1;
 		        mconec[i][0]=k;
 		        mconec[i][k]=j;}   }
 		}
   }*/

	int nvec (int n)	//NUMERO DE VECINOS --> number of neighbors
	{
		int nv = 0;
		pto3D pto = ((Atomo) susatomos.get (n)).vert;
		for (int j = 0; j < susatomos.size (); j++) {
			pto3D p = ((Atomo) susatomos.get (j)).vert;
			if (pto.dista (p) < 1.6 && pto.dista (p) > 0.1)
				nv++;
		}
		return nv;
	}


	void centraentorno (int num)	//Centra un atomo en su entorno de tres vecinos
	{
		pto3D pto = ((Atomo) susatomos.get (num)).vert;
		int numvert = this.nvec (num);
		pto3D posnueva = new pto3D ();
		if (numvert == 3) {
			for (int i = 0; i < susatomos.size (); i++) {
				pto3D ptov = ((Atomo) susatomos.get (i)).vert;
				if (ptov.dista (pto) < 1.6)
					posnueva = posnueva.mas (ptov.escala (0.333));
			}
			mueve (num, posnueva);
		}

	}

	void centraentorno ()
	{
		centraentorno (susatomos.size ());
	}

	void conecta (int i, int j)
	{


		int mci[] = ((Atomo) susatomos.get (i)).mconec;
		int mcj[] = ((Atomo) susatomos.get (j)).mconec;

		int ni = mci[0];
		int nj = mcj[0];

		boolean yaconi = false;
		for (int k = 1; k <= ni; k++)
			if (mci[k] == j)
				yaconi = true;
		if (yaconi == false) {
			mci[0] = ni + 1;
			mci[ni + 1] = j;
		}

		boolean yaconj = false;
		for (int k = 1; k <= nj; k++)
			if (mcj[k] == i)
				yaconj = true;
		if (yaconi == false) {
			mcj[0] = nj + 1;
			mcj[nj + 1] = i;
		}

		((Atomo) susatomos.get (i)).mconec = mci;
		((Atomo) susatomos.get (j)).mconec = mcj;
	}


	void conectaA (int i, int j)	//Metodo alternativo para la matriz z
	{
		int mci[] = ((Atomo) susatomos.get (i)).mconecA;
		int mcj[] = ((Atomo) susatomos.get (j)).mconecA;

		int ni = mci[0];
		int nj = mcj[0];

		boolean yaconi = false;
		for (int k = 1; k <= ni; k++)
			if (mci[k] == j)
				yaconi = true;
		if (yaconi == false) {
			mci[0] = ni + 1;
			mci[ni + 1] = j;
		}
		boolean yaconj = false;
		for (int k = 1; k <= nj; k++)
			if (mcj[k] == i)
				yaconj = true;
		if (yaconi == false) {
			mcj[0] = nj + 1;
			mcj[nj + 1] = i;
		}
		((Atomo) susatomos.get (i)).mconecA = mci;
		((Atomo) susatomos.get (j)).mconecA = mcj;
	}


	void desconecta (int i, int j)
	{
		int mci[] = ((Atomo) susatomos.get (i)).mconec;
		int mcj[] = ((Atomo) susatomos.get (j)).mconec;

		int ni = mci[0];
		int nj = mcj[0];

		for (int k = 1; k <= ni; k++) {
			if (j == mci[k]) {
				for (int l = k; l <= ni - 1; l++) {
					mci[l] = mci[l + 1];
				}
				mci[ni] = 0;
				mci[0] = ni - 1;
				ni--;
			}
		}
		for (int k = 1; k <= nj; k++) {
			if (i == mcj[k]) {
				for (int l = k; l <= nj - 1; l++) {
					mcj[l] = mcj[l + 1];
				}
				mcj[nj] = 0;
				mcj[0] = nj - 1;
				nj--;
			}
		}

	}

	double distancia (int a, int b)
	{
		pto3D v = ((Atomo) susatomos.get (a)).vert;
		pto3D w = ((Atomo) susatomos.get (b)).vert;
		return v.dista (w);
	}

	double angulo (int a, int b, int c)	// OJO, en GRADOS
	{
		pto3D v = ((Atomo) susatomos.get (a)).vert;
		pto3D w = ((Atomo) susatomos.get (b)).vert;
		pto3D u = ((Atomo) susatomos.get (c)).vert;
		return u.menos (w).angulocong (v.menos (w));
	}

	double dihedro (int a, int b, int c, int d)	//OJO en GRADOS
	{
		pto3D v = ((Atomo) susatomos.get (a)).vert;
		pto3D w = ((Atomo) susatomos.get (b)).vert;
		pto3D u = ((Atomo) susatomos.get (c)).vert;
		pto3D s = ((Atomo) susatomos.get (d)).vert;
		pto3D v1 = v.menos (w);
		pto3D v2 = w.menos (u);
		pto3D v3 = s.menos (u);
		return v1.dihedrog (v2, v3);
	}

	int nvert ()
	{
		return susatomos.size ();
	}

	pto3D vert (int i)
	{
		return ((Atomo) susatomos.get (i)).vert;
	}
	int tipo (int i)
	{
		return ((Atomo) susatomos.get (i)).tipo;
	}
	String etiq (int i)
	{
		return ((Atomo) susatomos.get (i)).etiq;
	}
	String pers (int i)
	{
		return ((Atomo) susatomos.get (i)).pers;
	}
	Color color (int i)
	{
		return ((Atomo) susatomos.get (i)).color;
	}
	double r (int i)
	{
		return ((Atomo) susatomos.get (i)).r;
	}

	int selecstatus (int i)
	{
		return ((Atomo) susatomos.get (i)).selec;
	}
	void selecciona (int i, int status)
	{
		((Atomo) susatomos.get (i)).selec = status;
	}

	void setInfo (String in)
	{
		this.info = in;
	}
	String getInfo ()
	{
		return this.info;
	}

	void marcaborra (int aborrar)
	{
		((Atomo) susatomos.get (aborrar)).selec = -1;

	}

	void borramarcados ()
	{
		for (int i = 0; i < nvert (); i++) {
			if (((Atomo) susatomos.get (i)).selec == -1) {
				rm (i);
				i--;
			}	//ya que hemos borrado uno, el indice ha de bajar uno, ya que se ocrre el resto
		}
	}

}
