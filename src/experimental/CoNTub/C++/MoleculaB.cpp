#include <math.h>
#include "MoleculaB.h"

typedef int boolean;

//LISTA DE METODOS BASICOS!!!
//A REHACER!!

void MoleculaB::addVert (pto3D punto, int ti, Color c)
{
    // punto --> point, position
    // ti is element number
    susatomos.add (Atomo (punto, ti, c));
}

void MoleculaB::addVert (pto3D punto, int ti)
{
    susatomos.add (Atomo (punto, ti));
}

void MoleculaB::addVert (double x, double y, double z, int ti)
{
    susatomos.add (Atomo (pto3D (x, y, z), ti));
}

//Metodos para añadir etiquetas personalizadas
void MoleculaB::addVert (double x, double y, double z, int ti, String e)
{
    int n = susatomos.size();
    addVert (x, y, z, ti);
    susatomos.get(n)->pers = e;
}

void MoleculaB::addVert (pto3D p, int ti, String e)
{
    int n = susatomos.size();
    addVert (p, ti);
    susatomos.get(n)->pers = e;
}

double MoleculaB::getDim ()
{
    double Dim = 0;
    if (susatomos.size () <= 1)
	return 0;
    for (int i = 0; i < susatomos.size (); i++) {
	for (int j = i + 1; j < susatomos.size (); j++) {
	    pto3D v = susatomos.get(i)->vert;
	    pto3D w = susatomos.get(j)->vert;
	    double dist = v.dista (w);
	    if (dist > Dim)
		Dim = dist;
	}
    }
    return Dim;
}

double MoleculaB::getLejania ()
{
    double lej = 0;
    if (susatomos.size () <= 1)
	return 0;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D v = susatomos.get(i)->vert;
	pto3D c = pto3D (0, 0, 0);
	double dist = v.dista (c);
	if (dist > lej)
	    lej = dist;
    }
    return lej;
}

void MoleculaB::vaciar ()
{
    susatomos = ArrayList (0);
    TablaP = tabPe_getInstance();
}

void MoleculaB::deseleccionar ()
{
    for (int i = 0; i < susatomos.size (); i++)
	susatomos.get(i)->selec = 0;
    nselec = 0;
}
//HABRIA QUE PONER HERRAMIENTAS DE SELECCIONADO


void MoleculaB::centrar ()
{
    if (susatomos.size () <= 0)
	return;
    double x = 0, y = 0, z = 0;
    int nv = susatomos.size ();
    std::cout << "atom 0 x " << susatomos.get(0)->vert.x << "\n";
    for (int i = 0; i < nv; i++) {
	x = x + susatomos.get(i)->vert.x / nv;
	y = y + susatomos.get(i)->vert.y / nv;
	z = z + susatomos.get(i)->vert.z / nv;
    }
    pto3D center = pto3D(x, y, z);
    std::cout << "x center " << x << "\n";
    std::cout << "nv " << nv << "\n";
    for (int i = 0; i < nv; i++) {
	susatomos.get(i)->vert.x -= x;
	susatomos.get(i)->vert.y -= y;
	susatomos.get(i)->vert.z -= z;
    }
    std::cout << "atom 0 x " << susatomos.get(0)->vert.x << "\n";
}

void MoleculaB::giroxr (double th)
{
    for (int i = 0; i < susatomos.size (); i++) {
	susatomos.get(i)->vert.giroxr (th);
    }
}
void MoleculaB::giroyr (double th)
{
    for (int i = 0; i < susatomos.size (); i++) {
	susatomos.get(i)->vert.giroyr (th);
    }
}
void MoleculaB::girozr (double th)
{
    for (int i = 0; i < susatomos.size (); i++) {
	susatomos.get(i)->vert.girozr (th);
    }
}

void MoleculaB::giroxg (double th)
{
    giroxr (th / 180.0 * M_PI);
}
void MoleculaB::giroyg (double th)
{
    giroyr (th / 180.0 * M_PI);
}
void MoleculaB::girozg (double th)
{
    girozr (th / 180.0 * M_PI);
}

MoleculaB MoleculaB::clona ()
{
    MoleculaB mo = MoleculaB ();
    for (int i = 0; i < susatomos.size (); i++) {
	mo.susatomos.add (*susatomos.get(i));
    }
    return mo;
}

void MoleculaB::rm (int n)
{
    if (n > susatomos.size () - 1)
	return;
    else
	susatomos.remove (n);
}			//elimina elemento n (solo hasta size-1)

void MoleculaB::rmlast (int n)
{
    for (int i = 1; i <= n; i++)
	rmlast ();
}			//elimina los ultimos N elementos (repite nveces

void MoleculaB::rmlast ()
{
    susatomos.remove (susatomos.size () - 1);
}			//DELICADO: un array de 3 elementos tiene como ultimo el 3-1

boolean MoleculaB::ocupa1 (pto3D pto1)
{
    boolean oc = false;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	double dist = pto2.dista (pto1);
	if (dist < 0.5)
	    oc = true;
    }
    return oc;
}

boolean MoleculaB::ocupa (pto3D pto1, double limite)
{
    boolean oc = false;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	double dist = pto2.dista (pto1);
	if (dist < limite)
	    oc = true;
    }
    return oc;
}

boolean MoleculaB::ocupa2 (pto3D pto1)
{
    boolean oc = false;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	double dist = pto2.dista (pto1);
	if (dist < 1.3)
	    oc = true;
    }
    return oc;
}

int MoleculaB::atomoqueocupa1 (pto3D pto)
{
    int ocup = 0;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	if (pto.dista (pto2) < 0.5)
	    ocup = i;
    }
    return ocup;
}

int MoleculaB::atomoqueocupa (pto3D pto, double limite)
{
    int ocup = 0;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	if (pto.dista (pto2) < limite)
	    ocup = i;
    }
    return ocup;
}

int MoleculaB::atomoqueocupa2 (pto3D pto)
{
    int ocup = 0;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pto2 = susatomos.get(i)->vert;
	if (pto.dista (pto2) < 1.3)
	    ocup = i;
    }
    return ocup;
}

void MoleculaB::mueve (int num, double x, double y, double z)
{
    if (num < susatomos.size ())
	susatomos.get(num)->vert = pto3D (x, y, z);
}			//OJO A LAS SUSTITUCIONES //ANTES ERA SUSTITUYE

void MoleculaB::mueve (int s, pto3D pto)
{
    if (s < susatomos.size ())
	susatomos.get(s)->vert = pto;
}

void MoleculaB::sustituye (int num, int ti, pto3D pto)
{
    if (num <= susatomos.size ())
	susatomos.set (num, Atomo (pto, ti));
}
//ESTA es una autentica sustitucion

// A Bucket is a cube-sized container to represent the coarse positions of atoms. It is
// used to find bonds faster - we can pre-sort the atoms into buckets, and when we want
// to find nearby atoms quickly, we only need to search the nearby buckets.

// Un Bucket es un envase cubo-clasificado para representar las posiciones gruesas de
// átomos. Se utiliza para encontrar enlaces más rápidos - preclasificación de la poder los
// átomos en los Buckets, y cuando deseamos encontrar los átomos próximos rápidamente,
// nosotros necesitamos solamente buscar los Buckets próximos.

#define  BUCKETWIDTH   (1.5 * 1.24)

ArrayList MoleculaB::getBucket(HashMap buckets, pto3D v) {
    int x = (int) ((v.x - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    int y = (int) ((v.y - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    int z = (int) ((v.z - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    int key = (x * 5000 + y) * 5000 + z;
    if (!buckets.hasKey(key))
	buckets.put(key, ArrayList());
    return (ArrayList) buckets.get(key);
}

// Search the 3x3x3 nearest buckets
ArrayList MoleculaB::getNeighborhood(HashMap buckets, pto3D v) {
    int x = (int) ((v.x - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    int y = (int) ((v.y - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    int z = (int) ((v.z - 0.5*BUCKETWIDTH) / BUCKETWIDTH);
    ArrayList alst = ArrayList();
    for (int dx = -1; dx <= 1; dx++)
	for (int dy = -1; dy <= 1; dy++)
	    for (int dz = -1; dz <= 1; dz++) {
		int key = ((x + dx) * 5000 + y + dy) * 5000 + z + dz;
		if (buckets.hasKey(key)) {
		    ArrayList alst2 = (ArrayList) buckets.get(key);
		    for (int i = 0; i < alst2.size(); i++) {
			Atomo *atm = alst2.get(i);
			if (!alst.contains(*atm))
			    alst.add(*atm);
		    }
		}
	    }
    return alst;
}

void MoleculaB::ponconec ()
{
    ponconec (1.30);
}

void MoleculaB::ponconec (double param)  // ponconec --> put connected??
{
    HashMap buckets = HashMap();
    int nv = susatomos.size ();
    for (int i = 0; i < nv; i++) {
	Atomo *atm = susatomos.get(i);
	atm->index = i;
	pto3D ptoa = atm->vert;
	ArrayList alst = getBucket(buckets, ptoa);
	alst.add(*atm);
    }
    for (int i = 0; i < nv; i++) {
	Atomo *atm = susatomos.get(i);
	pto3D ptoa = atm->vert;
	int tipA = atm->tipo;

	//reiniciamos el array de conectividad
	// we reinitiated the connectivity Array
	int *mc = new int[10];
	mc[0] = 0;	//un array para cada atomo i
			// an Array for each atom i
	for (int j = 1; j <= 9; j++)
	    mc[j] = 0;

	ArrayList alst = getNeighborhood(buckets, ptoa);
	for (int j = 0; j < alst.size(); j++) {
	    Atomo *atm2 = alst.get(j);
	    pto3D ptob = atm2->vert;
	    int tipB = atm2->tipo;
	    double distamax = param * (TablaP.en1[tipA] + TablaP.en1[tipB]);	//PARAMETRO AQUI
	    if (ptoa.dista (ptob) < distamax && ptoa.dista (ptob) > 0.6) {
		int k = mc[0] + 1;
		mc[0] = k;
		mc[k] = atm2->index;
	    }
	}

	//y lo ponemos como un todo El array es mejor manejarlo como un todo, incluso seria
	//conveniente para girarlo, poder sacar y meter un vert[] solo de puntos, en funcion de su efectividad
	// and we put it as a whole the Array is better to handle it like a whole, serious even advisable to
	// turn it, to be able to remove and to put vert [] single of points, based on its effectiveness
	susatomos.get(i)->mconec = mc;
    }
    // depura --> it purifies
    depuraconec ();	//OJO!!!
}

void MoleculaB::ponconecsafe ()
{
    ponconec (1.1);
    //CONTINUAR LA ELIMINACION DE CONEXIIONES REDUNDANTES!!
    //TO CONTINUE THE ELIMINATION OF REDUNDANT CONNECTIONS!!
}

void MoleculaB::reconec ()
{
    reconec (1.30);
}

void MoleculaB::reconec (double param)
{			//IGUAL QUE PONCONEC; pero sin iniciar --> JUST AS PONCONEC; but without initiating
    HashMap buckets = HashMap();
    int nv = susatomos.size ();
    for (int i = 0; i < nv; i++) {
	Atomo *atm = susatomos.get(i);
	atm->index = i;
	pto3D ptoa = atm->vert;
	ArrayList alst = getBucket(buckets, ptoa);
	alst.add(*atm);
    }
    for (int i = 0; i < nv; i++) {
	Atomo *atm = susatomos.get (i);
	pto3D ptoa = atm->vert;
	int tipA = atm->tipo;

	ArrayList alst = getNeighborhood(buckets, ptoa);
	for (int j = 0; j < alst.size(); j++) {
	    Atomo *atm2 = alst.get(j);
	    pto3D ptob = atm2->vert;
	    int tipB = atm2->tipo;
	    double distamax = param * (TablaP.en1[tipA] + TablaP.en1[tipB]);	//PARAMETRO AQUI
	    if (ptoa.dista (ptob) < distamax && ptoa.dista (ptob) > 0.6)
		conecta (i, atm2->index);
	}
    }
    //depuraconec();                          //OJO!!!
}

void MoleculaB::reconecsafe ()
{
    reconec (1.1);
    //CONTINUAR LA ELIMINACION DE CONEXIIONES REDUNDANTES!!
    //TO CONTINUE THE ELIMINATION OF REDUNDANT CONNECTIONS!!
}

int MoleculaB::depuraconec ()	//metodo paraeliminar conectividades redundantes, angulos demasiado pequeños (<60, en principio)
{
    int dc = 0;
    for (int i = 0; i < susatomos.size (); i++) {
	pto3D pa = susatomos.get(i)->vert;
	int *mc = new int[10];
	mc = susatomos.get(i)->mconec;
	for (int j = 1; j <= mc[0]; j++) {
	    pto3D pb = susatomos.get(mc[j])->vert;
	    for (int k = 1; k <= mc[0]; k++) {
		pto3D pc = susatomos.get(mc[k])->vert;

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

int MoleculaB::nvec (int n)	//NUMERO DE VECINOS --> number of neighbors
{
    int nv = 0;
    pto3D pto = susatomos.get(n)->vert;
    for (int j = 0; j < susatomos.size (); j++) {
	pto3D p = susatomos.get(j)->vert;
	if (pto.dista (p) < 1.6 && pto.dista (p) > 0.1)
	    nv++;
    }
    return nv;
}


void MoleculaB::centraentorno (int num)	//Centra un atomo en su entorno de tres vecinos
{
    pto3D pto = susatomos.get(num)->vert;
    int numvert = nvec (num);
    pto3D posnueva = pto3D ();
    if (numvert == 3) {
	for (int i = 0; i < susatomos.size (); i++) {
	    pto3D ptov = susatomos.get(i)->vert;
	    if (ptov.dista (pto) < 1.6)
		posnueva = posnueva.mas (ptov.escala (0.333));
	}
	mueve (num, posnueva);
    }

}

void MoleculaB::centraentorno ()
{
    centraentorno (susatomos.size ());
}

void MoleculaB::conecta (int i, int j)
{


    int *mci = susatomos.get(i)->mconec;
    int *mcj = susatomos.get(j)->mconec;

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

    susatomos.get(i)->mconec = mci;
    susatomos.get(j)->mconec = mcj;
}


void MoleculaB::conectaA (int i, int j)	//Metodo alternativo para la matriz z
{
    int *mci = susatomos.get(i)->mconecA;
    int *mcj = susatomos.get(j)->mconecA;

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
    susatomos.get(i)->mconecA = mci;
    susatomos.get(j)->mconecA = mcj;
}


void MoleculaB::desconecta (int i, int j)
{
    int *mci = susatomos.get(i)->mconec;
    int *mcj = susatomos.get(j)->mconec;

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

double MoleculaB::distancia (int a, int b)
{
    pto3D v = susatomos.get(a)->vert;
    pto3D w = susatomos.get(b)->vert;
    return v.dista (w);
}

double MoleculaB::angulo (int a, int b, int c)	// OJO, en GRADOS
{
    pto3D v = susatomos.get(a)->vert;
    pto3D w = susatomos.get(b)->vert;
    pto3D u = susatomos.get(c)->vert;
    return u.menos (w).angulocong (v.menos (w));
}

double MoleculaB::dihedro (int a, int b, int c, int d)	//OJO en GRADOS
{
    pto3D v = susatomos.get(a)->vert;
    pto3D w = susatomos.get(b)->vert;
    pto3D u = susatomos.get(c)->vert;
    pto3D s = susatomos.get(d)->vert;
    pto3D v1 = v.menos (w);
    pto3D v2 = w.menos (u);
    pto3D v3 = s.menos (u);
    return v1.dihedrog (v2, v3);
}

int MoleculaB::nvert ()
{
    return susatomos.size ();
}

pto3D MoleculaB::vert (int i)
{
    return susatomos.get(i)->vert;
}
int MoleculaB::tipo (int i)
{
    return susatomos.get(i)->tipo;
}
String MoleculaB::etiq (int i)
{
    return susatomos.get(i)->etiq;
}
String MoleculaB::pers (int i)
{
    return susatomos.get(i)->pers;
}
Color MoleculaB::color (int i)
{
    return susatomos.get(i)->color;
}
double MoleculaB::r (int i)
{
    return susatomos.get(i)->r;
}

int MoleculaB::selecstatus (int i)
{
    return susatomos.get(i)->selec;
}
void MoleculaB::selecciona (int i, int status)
{
    susatomos.get(i)->selec = status;
}

void MoleculaB::setInfo (String in)
{
    info = in;
}
String MoleculaB::getInfo ()
{
    return info;
}

void MoleculaB::marcaborra (int aborrar)
{
    susatomos.get(aborrar)->selec = -1;

}

void MoleculaB::borramarcados ()
{
    for (int i = 0; i < nvert (); i++) {
	if (susatomos.get(i)->selec == -1) {
	    rm (i);
	    i--;
	}	//ya que hemos borrado uno, el indice ha de bajar uno, ya que se ocrre el resto
    }
}
