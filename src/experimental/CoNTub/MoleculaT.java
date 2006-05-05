import java.applet.Applet;
import java.awt.Image;
import java.awt.*;
import java.awt.Event;
import java.awt.Graphics;
import java.awt.Dimension;
import java.io.*;
import java.net.URL;
import java.util.Hashtable;
import java.awt.image.IndexColorModel;
import java.awt.image.ColorModel;
import javax.swing.*;
import java.applet.*;

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

Mensaje sniff(pto3D candidato, int gen)          IMPORTANTES
String  sniff2(int gen)

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

	void proyecta (MoleculaT maux)
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
		pto3D pto = sustituido.clona ();	//El punto a proyectar (copia, claro)
		pto3D pt = pto.menos (TEST1);	//respecto al final del primer tubo
		pto3D pp = pt.proyeccplano (TESTC);	//se proyecta en el plano TC
		pto3D pl = pp.prodvect (TESTC);	//y este (pl) es el plano sobre el que todo tiene que transcurrir
		pto3D pc = pl.prodvect (TEST1);	//y este (pc) es el vector comun perteneciente a los planos pl y TEST1

/*    	double dh=pc.dihedro(TESTC,pp);
    	dh=Math.abs(dh);
    	if (dh<1)            pc.versoriza();
    	   else if (dh>179) {pc=pc.escala(-1); pc.versoriza();}
    	   else {pc.x=-10;pc.y=0;pc.z=0;addVert(pc,1);}//MARCA EL ERROR con un punto -10,0,0 ROJO
*/
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

	void centraentorno ()
	{
		centraentorno (this.nvert () - 1);
	}

	Mensaje sniff (pto3D candidato, int gen)	//El punto propuesto, y el indice del atomo a partir del cual se crea.
	{			//Funcion que calcule el numero de vecinos ponderado y devuelve el mensaje (error o no)
		//y toma la decision de añadir o no el átomo
		int nvecnorte = 0, nvecsur = -1, nveccono = 0, nvecinos = 0;
		int nvn[] = new int[10];	//espero que nunca haya mas de diez vecinos
		int nvs[] = new int[10];
		int nvc[] = new int[10];

		double nvecpond = 0;
		String cadena = "";
		pto3D ptoprop = new pto3D ();
		int recom = 0;	//accion recomendada
		Mensaje mens = new Mensaje ();	//el mensaje de salida extendido;
		boolean ocupado = false;
		//Cada una de estas variablex recoge un tipo de parametro

		for (int i = 0; i < nvert (); i++) {
			pto3D ptox = vert (i);
			pto3D u = vert (gen);
			double angulo = ptox.menos (candidato).angulocong (u.menos (candidato));
			double dista = ptox.dista (candidato);
			if (dista < 0.5)
				ocupado = true;
			else if (dista < 2.0 && angulo > 90) {
				nvecnorte++;
				nvn[nvecnorte] = i;
			}
			if (dista < 0.5)
				ocupado = true;
			else if (dista < 2.0 && angulo < 90) {
				nvecsur++;
				nvs[nvecsur] = i;
			}
			if (dista < 0.5)
				ocupado = true;
			else if (dista < 2.0 && angulo < 165 && angulo > 100) {
				nveccono++;
				nvc[nveccono] = i;
			}
			if (dista < 5.0)
				nvecpond = nvecpond + Math.exp (-Math.pow ((dista - 1.5) / 0.5, 2));
		}

		//Y AQUI decidimos, en funcion de esos numeros, si tiene 0, 1, 2  o mas (erroneo) vecinos (descontando el
		// si hay coincidencia
		if (ocupado) {
			cadena = "\nPossition Occupied";
			nvecinos = -1;
		} else if (nveccono == nvecnorte && nveccono == (int) nvecpond)
			nvecinos = nveccono;
		else if (nveccono == nvecnorte) {
			cadena = "" + nvecpond;
			nvecinos = nveccono;
		} else if (nveccono != nvecnorte) {
			nvecinos = 9;
			cadena = "\nWarning: muy complicado!! " + nveccono + " " + nvecnorte;
		} else {
			cadena = "\nSituacion no considerada:" + nveccono + " " + nvecnorte;
			nvecinos = 9;
		}

		//si hay dos valores discrepantes, dar mensaje de warning
		//si hay tres valores, marcamos nvec como "9"

		//Si esta vacio (case 0), explora mas alla en torno a
		//un circulo perpendicular al atomo conectado (gen), aprovechamos la libertad para distender la cosa
		//se busca el/los ptos donde los vecinos estan mas cerca
		//con una distancia de corte adecuada (no mas alla de cierta esfera
		//De esos minimos, habra posiciones casi ocupadas, y posiciones libres, pero con
		//vecinos
		//si no estan vacias ni pueden tener vecinos, no  pasa nada, se pone el pto candidato y se acaba

		//si alguna pos explorada encaja (con un margen de error mas amplio), adecuar la pos para un encaje optimo
		// ssi dos encajan, centrar la posicion resultante entre ambos encajes

		//Si case 1, se comprueba que el angulo es correcto, Si lo es, ajustar distancias, comprobar que el tercer punto esta realmente vacio
		//Si case 2, comprobar angulos, y si OK, centrar
		//si case 3, probablemente hay un atomo demasiado cerca, y haya que sustituirlo. Se escoge entre el
		//candidato y el existente, en funcion de distancias y angulos.

		if (nvecinos == 0) {	//por ahora lo añadimos y ya esta.
			ptoprop = candidato.clona ();
			recom = 1;
		} else if (nvecinos == -1) {
			ptoprop = vert (atomoqueocupa (candidato, 0.5)).clona ();	//si esta ocupado. la salida marca el punto que se ha ocupado
			recom = 4;	//no añadir
		} else if (nvecinos == 1) {	//medimos distancia al vecino y al generador, y el pto
			//propuesto sera gen+(vec-gen)/2+proyplano(vec-gen)escalado (1/raizde3)
			//comprobar que la distancia no es mucha
			ptoprop = candidato.clona ();
			recom = 1;
		} else if (nvecinos == 2) {	//por ahora se calcula la media de los tres
			ptoprop = vert (gen).mas (vert (nvc[1])).mas (vert (nvc[2]));
			ptoprop = ptoprop.escala (1 / 3);
			recom = 1;
		} else if (nvecinos == 3) {
			cadena = cadena + "\n Error: Proposed position  next ot atom " + gen + " has 4 neighbors.";
			// vemos cual de los dos tiene mejor pinta

			ptoprop = new pto3D ();
			recom = 4;

		} else if (nvecinos == 9) {	//marca un error en la determinacion de los vecinos
			cadena = cadena + "\n Error: Unable to find number of neighbors\nfor atom intended to connect to atom " + gen + ": \nAtom not added.";
		} else {
			cadena = cadena +
				"\n Error: Number of neighbor atoms exceeded \nfor atom intended to connect to atom "
				+ gen + ": " + nvecinos + " neighbors.\nAtom not added.";
		}

		mens.cad = cadena + " " + ptoprop.aTexto ();	//Mensaje a divulgar
		mens.pto = ptoprop;	//pto que se propone para añadir
		mens.num = recom;	//accion recomendada 1- añadir 2- sustituir 3 interpolar 4 ocupado 5 no añadir
		return mens;

		//IDEA A REVISAR: intentar emparejar elementos con solo dos vecinos, y que esten proximos.
		//Habra que comprobar que lo que forman a derecha e izquierda son hexagonos!
		//OTRA idea: algo que evite.que se cree el vertice.
	}

	String sniff2 (int gen)
	{
		//Actualmente sniff2 toma el atomo generador,
		//ve los vecinos que tiene, y en funcion de ellos, satura las valencias que
		//pueda     la salida es una simple cadena

		String cadena = "";
		pto3D vecprop = new pto3D ();

//Vemos el numero de vecinos
		double nc = 0;
		int v[] = new int[5];	//almacen temporal de vecinos  //No se hizo ya??
		int nv = 0;
		for (int i = 0; i < nvert (); i++) {
			pto3D pt = vert (i).clona ();
			double dis = pt.dista (vert (gen));
			if (dis < 2.0 && dis > 0.3) {
				nv++;
				v[nv] = i;
			}
		}
//Ya tenemos el numero de vecinos y los que son vecinos

		if (nv == 0) {	//ERROR, el punto de generacion esta solo!!
			cadena = cadena + "\nERROR: no neighbors around atom " + gen;

		} else if (nv == 1) {	//Usar ideas del viejo sniff Por ahora, solo añadimos
			cadena = cadena + "Atomo en segundo orden, USAR SNIF ANTIGUO!!!";
		} else if (nv == 2) {
			//cual esta a la derecha (anillo ccw) y cual a la izq (cw)?
			boolean d1, d2;	//esta a la dereca el 1 o el 2?
			anillo triangulo = new anillo ();
			triangulo.addVert (gen);
			triangulo.addVert (v[1]);
			triangulo.addVert (v[2]);
			triangulo.poncentroide (this);
			triangulo.ordenacw (gen, this);
			v[1] = triangulo.vert[3];
			v[2] = triangulo.vert[2];	//OJO a posibles fallos, quizas hay que permutar

			pto3D A = vert (gen).clona ();
			pto3D B1 = vert (v[1]).clona ();
			pto3D B2 = vert (v[2]).clona ();
			pto3D t2 = B2.menos (A);
			pto3D t1 = B1.menos (A);
			pto3D cd = t2.mas (t1).aversor ();
			cd = cd.escala (-1.4);

			pto3D cand = A.mas (cd);

			pto3D c1 = vert (gen).mas (cd).mas (t1);
			pto3D c2 = vert (gen).mas (cd).mas (t2);

			anillo anillo1 = new anillo ();
			pto3D vv1 = new pto3D ();
			anillo anillo2 = new anillo ();
			pto3D vv2 = new pto3D ();


			//Identificar anillos (comun con primer vecino
			for (int i = 0; i < nvert (); i++) {
				pto3D pt = vert (i).clona ();
				double dis = pt.dista (c1);
				if (dis < 2.0)
					anillo1.addVert (i);
			}

			anillo1.setCentro (c1);
			anillo1.ordenacw (gen, this);	//Sentido de las agujas del reloj

			if (anillo1.num == 2) {	//anillo vacio, fijamos el vectorcillo propuesto
				vv1 = cand.menos (vert (gen));
			} else if (anillo1.num == 3) {	//anillo desperdigado, o vacio fijamos al candidato
				vv1 = cand.menos (vert (gen));
			} else {	//Comprobamos que no hay huecos entre los tres primeros pasos del anillo o proyecto de anillo
/*	OJOOO*/ double da1 =
					vert (anillo1.vert[1]).dista (vert (anillo1.vert[2]));
				double db1 = vert (anillo1.vert[2]).dista (vert (anillo1.vert[3]));
				double dc1 = vert (anillo1.vert[3]).dista (vert (anillo1.vert[4]));
				if (da1 < 2.0 && db1 < 2.0 && dc1 < 2.0) {
					vv1 = vert (anillo1.vert[4]).menos (vert (anillo1.vert[3]));
				} else {	//Hay algun hueco, ante la duda, proponer el de antes
					vv1 = cand.menos (vert (gen));
				}
			}

			//Identificar anillos (comun con segundo vecino

			for (int i = 0; i < nvert (); i++) {
				pto3D pt = vert (i).clona ();
				double dis = pt.dista (c2);
				if (dis < 2.0)
					anillo2.addVert (i);
			}

			anillo2.setCentro (c2);
			anillo2.ordenaccw (gen, this);	//Sentido CONTRARIO a las agujas del reloj

			if (anillo2.num == 2) {	//anillo vacio, fijamos el vectorcillo propuesto
				vv2 = cand.menos (vert (gen));
			} else if (anillo2.num == 3) {	//anillo desperdigado, o vacio fijamos al candidato
				vv2 = cand.menos (vert (gen));
			} else {	//Comprobamos que no hay huecos entre los tres primeros pasos del anillo o proyecto de anillo
				double da2 = vert (anillo2.vert[1]).dista (vert (anillo2.vert[2]));
				double db2 = vert (anillo2.vert[2]).dista (vert (anillo2.vert[3]));
				double dc2 = vert (anillo2.vert[3]).dista (vert (anillo2.vert[4]));
				if (da2 < 2.0 && db2 < 2.0 && dc2 < 2.0) {
					vv2 = vert (anillo1.vert[4]).menos (vert (anillo1.vert[3]));
				} else {	//Hay algun hueco, ante la duda, proponer el de antes
					vv2 = cand.menos (vert (gen));
				}
			}
			vecprop = vv1.mas (vv2).escala (0.5);
			cadena = cadena + "\nAtom added in 1st order next to atom " + gen;

		} else if (nv == 3) {
			cadena = cadena + "\nERROR: Valences saturated in atom " + gen;
			vecprop = new pto3D ();
		}
		//el atomo esta totalmente rodeado!! no añadir nada
		else {
			cadena = cadena + "\nERROR: Too much neighbors:\n" + nv + " atoms around atom " + gen;
			vecprop = new pto3D ();
		}
		//ERROR! demasiados vecinos!!

		return cadena;
	}
/*
String refina(anillo anori){
if (anori.num==6){
	          if (anori.centroide==null) anori.poncentroide(this);
	          anori.ordenaccw(anori.vert[1],this);
	          pto3D plano=new pto3D();
	          for (int i=1;i<=6;i++){
	          	      pto3D va=this.vert[anori.vert[i]].clona();
	          	      pto3D vb=new pto3D();
	          	      if (i==6) vb=this.vert[anori.vert[1]].clona();
	          	          else  vb=this.vert[anori.vert[i+1]].clona();
	          	      pto3D pmenos=va.menos(vb);
	          	      pto3D prel  =va.menos(anori.centroide);
	          	      pto3D pvert =prel.prodvect(pmenos);
	          	      plano=plano.mas(pvert);
	          	      }

	          plano.versoriza();
	          //preparamos un hexagono de referencia, coplanar, con el primer miembro coincidente con el del
	          // anillo a refinar
	          pto3D anref[]=new pto3D[7];

	          pto3D vp=this.vert[anori.vert[1]].menos(anori.centroide);
	                vp.versoriza();
	                vp=vp.escala(1.4);

	          pto3D vq=vp.prodvect(plano).escala(Math.sqrt(3)/2);    //OJO A LA orientacion de ambos anillo, que sea
	          anref[1]=anori.centroide.mas(vp);                      //sea la misma!!! o sea, cw
	          anref[2]=anori.centroide.mas(vp.escala(0.5)).mas(vq);
	          anref[3]=anori.centroide.menos(vp.escala(0.5)).mas(vq);
	          anref[4]=anori.centroide.menos(vp);
	          anref[5]=anori.centroide.menos(vp.escala(0.5)).menos(vq);
	          anref[6]=anori.centroide.mas(vp.escala(0.5)).menos(vq);
	          //ahora comparamos uno a uno, los angulos diedros,  y los almacenamos
	           double mdh[]=new double[7];
	          //desplazam dhdro medio y average
	          double ddm=0,ddav=0;
	          for (int i=1;i<=6;i++){pto3D pa=anref[i].menos(anori.centroide);
	                                 pto3D pb=this.vert[anori.vert[i]].menos(anori.centroide);
	                                 mdh[i]=pa.dihedro(plano,pb);
	                                 ddm=ddm+mdh[i]/6;
	                                 //this.addVert(anref[i]);
	                                 }

	          for (int i=1;i<=6;i++) mdh[i]=mdh[i]-ddm;
	          for (int i=1;i<=6;i++) ddav=ddav+Math.abs(mdh[i])/6;
	          if (ddav>30) return "Error, ring excesively deformed "+mdh[1]+" "+mdh[2]+" "+mdh[3]+" "+mdh[4]+" "+mdh[5]+" "+mdh[6]+"average= "+ddav;
              //Pues bien, ahora recreamos el anillo de referencia, basado en el desplazamiento dihedro medio ddm
              //volvemos a crear vp y vq
              double ddmr=Math.PI/180*ddm;
              pto3D vpn=vp.escala(Math.cos(ddmr)).mas  (vq.escala(Math.sin(ddmr)/Math.sqrt(3)*2)); //ojo que la escala de vp y vq son distintas
              pto3D vqn=vq.escala(Math.cos(ddmr)).menos(vp.escala(Math.sin(ddmr)*Math.sqrt(3)/2));
              anref[1]=anori.centroide.mas(vpn);                      //sea la misma!!! o sea, cw
			  anref[2]=anori.centroide.mas(vpn.escala(0.5)).mas(vqn);
			  anref[3]=anori.centroide.menos(vpn.escala(0.5)).mas(vqn);
			  anref[4]=anori.centroide.menos(vpn);
			  anref[5]=anori.centroide.menos(vpn.escala(0.5)).menos(vqn);
			  anref[6]=anori.centroide.mas(vpn.escala(0.5)).menos(vqn);
	          for (int i=1;i<=6;i++) {pto3D pref=anref[i].menos(this.vert[anori.vert[i]]);
	                                  this.sustituye(anori.vert[i],this.vert[anori.vert[i]].mas(pref.escala(0.5)));
	          }




	          return "Refining seems succesfully. deformation="+ddav;
	          }
else          return "Error: Ring is not an hexagon "+anori.aCadena();

}

anillo findring(pto3D ptoref, int ref) //Tiene que devolver un anillo!
{int siguiente=10000;                  //el mas cercano al pto medio entre ref y ptoref, sin ser ref
 double d=10; pto3D ptomed=ptoref.mas(this.vert[ref]).escala(0.5);
 for (int i=1;i<=this.nvert;i++)
        {double di=ptomed.dista(this.vert[i]);if (di<d&&i!=ref) {d=di;siguiente=i;}}

 int actual= ref;
 anillo ani=new anillo();
 ani.addVert(ref);
 ani.addVert(siguiente);
 int j=1;
 boolean brokenring=false;
 while (siguiente!=ref && brokenring==false) {
	pto3D ptoa=this.vert[actual];
	pto3D ptos=new pto3D();
	pto3D pc  =new pto3D();
	ptos=this.vert[siguiente];  //catch (NullPointerException e){ numeros[200]=""+j;return numeros;}
	pc=ptos.menos(ptoa);     	//catch (NullPointerException e){ numeros[200]=""+j;return numeros;}
	//UN modo de dar la salida en caso de error
	int sigtemp=0;
	double distan=10;
	double dh=180;
	for (int i=1;i<=this.nvert;i++){
		if (i!=actual && i!=siguiente)
		{pto3D pto=this.vert[i]; //c
		pto3D a=   pto.menos(ptos);
		pto3D b=ptoref.menos(ptoa);
		double dista=pto.dista(ptos);
		double ang=a.angulocon(ptoa.menos(ptos));
	    dh=a.dihedro(pc,b);
        //String st=a.dihedrop(pc,b);
        if (dista<distan && ang>90 && (Math.abs(dh)<65)){distan=dista;sigtemp =i;}
        }
    }
    if (sigtemp!=ref) ani.addVert(sigtemp);
    if (sigtemp==0  ) brokenring=true;//Deteccion de Broken ring!"
    actual=siguiente;
    siguiente=sigtemp;
    }

 String s=ani.poncentroide(this);
 return ani;
 }


//Metodo para generar un anillo contiguo a un portalon de salida y a un cenntroide existente
int generaanillo(int a1,int a2, pto3D cideprev){
    pto3D pto1=this.vert[a1];
    pto3D pto2=this.vert[a2];
    pto3D ava1=pto1.menos(cideprev);
    pto3D ava2=pto2.menos(cideprev);
	//addVert(cideprev);

	int a1l=0,a2l=0,a1c=0,a2c=0;
	//Brazo 1
    pto3D p1c=cideprev.mas(ava1.escala(2)); //pto cercano
          p1c=proyecta(p1c);//proyectado
    if   (this.ocupa(p1c,0.8)) {p1c=this.vert[atomoqueocupa(p1c,0.8)].clona();conecta(a1,atomoqueocupa(p1c,0.8));a1c=atomoqueocupa(p1c,0.8);}
    else                       {addVert(p1c,6);                              ;conecta(a1,nvert);                 a1c=nvert;}
    //el segundo es el anterior mas el salto del opuesto
	pto3D p1l=p1c.mas(ava2);
	      p1l=proyecta(p1l);//proyectado
	if   (this.ocupa(p1l,0.8)) {p1l=this.vert[atomoqueocupa(p1l,0.8)].clona();conecta(a1c,atomoqueocupa(p1l,0.8));a1l=atomoqueocupa(p1l,0.8);}
	else                       {addVert(p1l,6);                              ;conecta(a1c,nvert);                 a1l=nvert;}

	//Brazo 2
	pto3D p2c=cideprev.mas(ava2.escala(2)); //pto cercano
	      p2c=proyecta(p2c);//proyectado
    if   (this.ocupa(p2c,0.8)) {p2c=this.vert[atomoqueocupa(p2c,0.8)].clona();conecta(a2,atomoqueocupa(p2c,0.8));a2c=atomoqueocupa(p2c,0.8);}
    else                     {addVert(p2c,6);                                ;conecta(a2,nvert);                 a2c=nvert;}
    //el segundo es el anterior mas el salto del opuesto
	pto3D p2l=p2c.mas(ava1);
	      p2l=proyecta(p2l);//proyectado
    if   (this.ocupa(p2l,0.8)) {p2l=this.vert[atomoqueocupa(p2l,0.8)].clona();conecta(a2c,atomoqueocupa(p2l,0.8));a2l=atomoqueocupa(p2l,0.8);}
    else                       {addVert(p2l,6);                               conecta(a2c,nvert);                 a2l=nvert;}
conecta(a1l,a2l);

return 0;
//tests aqui

 }

String addJunto(int con){
	//
	if (con<=0)    return "Error in connectivity matrix";
	if (con>nvert) return "Error in connectivity matrix";

	//Seleccionamos entre una y dos conectividades
	if      (mconec[con][0]==1)
		{int asta=mconec[con][1];
			pto3D pcon=vert[con];
			pto3D past=vert[asta];
			//Detectamos alas derecha e izquierda que deben de existir
			if (mconec[asta][0]!=3) return "preceeding atom excessively connected"; //ERROR 2
			int ala[] = new int[3];
			int j=1;
			for (int i=1;i<=3;i++){if (mconec[asta][i]!=con)
			                          {ala[j]=mconec[asta][i];
			                           j++;}
			                      }
			// posiciones a y b (orden aleatorio)
			pto3D palaa=vert[ala[1]];
			pto3D palab=vert[ala[2]];

			pto3D candidato1=palaa.mas((pcon.menos(past)).escala(2));
			pto3D candidato2=palab.mas((pcon.menos(past)).escala(2));

			pto3D cd1=proyecta(candidato1);
			pto3D cd2=proyecta(candidato2);

			//Una vez que tenemos los candidatos proyectados, escalamos la distancia de enlace a 1.42
			pto3D cd1r=cd1.menos(pcon);
			pto3D cd2r=cd2.menos(pcon);

			pto3D cd1d=proyecta(cd1r.aversor().escala(1.42).mas(pcon));
			pto3D cd2d=proyecta(cd2r.aversor().escala(1.42).mas(pcon));
			//Donde ya hemos proyectado otra vez, que no se olvide

			//VERIFICACION PRIMITIVA
			int con1=0,con2=0;
			String m1,m2;
			if (ocupa1(cd1d))    {con1=atomoqueocupa1(cd1d);conecta(con1,con);m1=exploraanillo(con1);}
			else {addVert(cd1d,7);con1=nvert;               conecta(con1,con);m1=exploraanillo(con1);}



			if (ocupa1(cd2d))    {con2=atomoqueocupa1(cd2d);conecta(con2,con);m2=exploraanillo(con2);}
			else {addVert(cd2d,8);con2=nvert;               conecta(con2,con);m2=exploraanillo(con2);}

			//DEBE SER:::::::::
            //TODO ESTO SON IDEAS ANTIGUAS
			//Ponemos conexion entre el punto generado y el otro. si no esta en la esfera minima
			//vemos a que distancia esta el resto de vecinos, cuantos hay dentro de las esferas de interes
			//CASO::
			   // ninguno= ok
			   //total de mas de 2 Error, muy complejo
			   //Total de 2, puede ser
			   //Total de 1, auch
			//FIN DEBE SER;;;;;;;;;;;;;;;;;;;;;




			return "added connections to "+con1+" and "+con2+": Ring connections said: "+m1+" and "+m2 ;
			}
	else if (mconec[con][0]==2)
		{   //Detectamos alas derecha e izq, que deben existir
            if (mconec[con][0]!=2) return "preceeding atom excessively connected"; //ERROR 2
			// posiciones a y b (orden aleatorio)
			pto3D pcon=vert[con];
			pto3D palaa=vert[mconec[con][1]];
			pto3D palab=vert[mconec[con][2]];
			pto3D va=pcon.menos(palaa);
			pto3D vb=pcon.menos(palab);

			pto3D v=proyecta(pcon.mas(va).mas(vb));

			pto3D vr=v.menos(pcon);
			pto3D vd=proyecta(vr.aversor().escala(1.42).mas(pcon));


			//VERIFICACION PRIMITIVA
			int con1=0;
			String m1="omitido";
			if (ocupa1(vd)) {   con1=atomoqueocupa1(vd);}
			else            {addVert(vd,9);  con1=nvert;}


			conecta(con1,con);
			m1=exploraanillo(con1);

			return "added conection to "+con1+": Ring connection said : "+m1;}
	else if (mconec[con][0]==3) return "Atom fully connected";
	else    {return "ERROR: unknown connectivity"+mconec[con][0];}




	}
*/

	void cierraH ()
	{			//ESTABLECER EN FUNCION DE RADIO Y ORIENTACION HEXAGONO
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

	void cierraN ()
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

}
