import javax.swing.JPanel;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.BasicStroke;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Font;
import java.awt.event.MouseEvent;
import java.awt.event.KeyEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.KeyListener;

public class Mira3D extends JPanel implements MouseListener, MouseMotionListener, KeyListener
{
	Image Buffer;
	Graphics BuffGr;
	int Ox, Oy, Nx, Ny, Ax, Ay, Sx, Sy;
	int nr, nr2;
	int biasx, biasy;
	double lr;
	pto3D versorx, versory, versorz;
	BasicStroke fino, gros, line;

	double escala;
	double dim = 0;
	int morden[][] = new int[6000][200];

	Minimol mmol, mmolg;	//La molecula en si y la que gira, que es la que se visualiza
	boolean pintado = true;
	boolean autocon = true;
	boolean bst = false;	//pintar bolas
	boolean atn = false;	//poner numeros
	boolean hbk = false;	//esconder parte atras
	boolean abt = false;	//about
	boolean hlp = false;	//miniayuda
	boolean ini = true;	//minicadena sugiriendo la ayuda
	boolean lrd = false;	//Low Requirement Display
	boolean lrdf = false;	//lrd fijo
	int nselec = 0;		//numero de atomos selecionados
	int selec[];		//array de cuatro numeros, que son los que se han seleccionado
	int anchomed = 0, altomed = 0;	//Anchura y altura entre dos

	public Mira3D ()
	{
		addMouseMotionListener (this);
		addMouseListener (this);
		addKeyListener (this);
		mmol = new Minimol (0);
		mmolg = new Minimol (0);
		resetea ();

	}			//Constructor

	public void cargarMol (MoleculaT m)
	{
		mmol = new Minimol (m);	//Cuando cargo la mol, solo giro mmolg
		mmolg = new Minimol (m);	//lo demas se mira en mmol
		resetea ();
	}

	public void paint (Graphics g)
	{
		//GROSOR DE Trazos
		double grosor0 = 0.1f * (float) escala;	//FINO,  0.1   Angs
		double grosor2 = grosor0 * 1.25;	//Medio  0.125 Angs
		double grosor = grosor0 * 2.5;	//Entero 0.25
		int grint0 = (int) grosor0;
		int grint2 = (int) grosor2;
		int grint = (int) grosor;
		fino = new BasicStroke (grint0, 0, 1);	//cap_butt, uniones round
		gros = new BasicStroke (grint, 0, 1);
		line = new BasicStroke (1, 0, 1);

		Graphics2D g2 = (Graphics2D) g;
		g2.setRenderingHint (RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
		g2.setColor (java.awt.Color.white);
		g2.fillRect (0, 0, getSize ().width, getSize ().height);	// blanqueamos

		//antes de cada pintado, clasificamos los atomos por su posicion, en un array con el doble de rodajas que angstroms tenga de
		// longitud la molecula pillamos la longitud, que es dim
		int nplanos = (int) (4 * dim);

		if (!lrd)	//solo con display normal
		{		//reiniciamos la matriz de orden mo[6000][2000]
			for (int i = 1; i <= nplanos; i++)
				morden[i][0] = 0;
			//calculamos la matriz de orden
			for (int i = 0; i < mmolg.nvert; i++) {
				int indice = (int) (2 * (dim + mmolg.miniverts[i].z));	//multiplicamos por 2, para duplicar el numero de rodajas por angstrom.
				morden[indice][0]++;
				morden[indice][morden[indice][0]] = i;
		}} else
			g2.setColor (java.awt.Color.red);

		//pintamos plano a plano
		int planoini = nplanos;
		if (hbk)
			planoini = (int) (nplanos / 2);

		if (!lrd) {
			for (int i = planoini; i >= 1; i--) {
				//pintamos conectividades
				for (int j = 1; j <= morden[i][0]; j++) {
					int ii = morden[i][j];	//ii marca el atomo j del plano i
					int nconect = mmolg.miniconec[ii][0];	//vemos en numero de vecinos del atomo ii
					pto3D v = mmolg.miniverts[ii];
					Color c = mmolg.minicolor[ii];
					int x = (int) (anchomed + (int) (v.x * escala));	//vemos la posicion de ii en el canvas
					int y = (int) (altomed + (int) (v.y * escala));
					int r = (int) (escala * mmolg.minisizes[ii] / 4.0) + 2;	//su tamaño

					if (autocon)
						g2.setColor (mmolg.minicolor[ii]);
					else
						g2.setColor (Color.black);

					for (int k = 1; k <= nconect; k++) {
						pto3D w = null;
						if (autocon)
							w = mmolg.miniverts[mmolg.miniconec[ii]
									    [k]].clona ();
						else
							w = mmolg.miniverts[mmolg.miniconec[ii][k]].clona ();	//Conectividad alternativa
						//vemos la posicion de ii en el canvas. nos interesa el punto medio entre atomo actual (atomo ii)
						pto3D vw = v.mas (w).escala (0.5);
						int xw = (int) (anchomed + (int) (vw.x * escala));
						int yw = (int) (altomed + (int) (vw.y * escala));
						//pintamos el enlace. La idea es hacerlo hasta la mitad para que cada parte tenga su color
						g2.setStroke (gros);
						g2.drawLine (biasx + x, biasy + y, biasx + xw, biasy + yw);
					}
					//Fin de cadauna de las conectividades. Seguimos en el atomo del plano
					//Pintamos el atomo, primero vemos si esta seleccionado
					if (autocon) {
						if (mmol.selecstatus (ii) == 1) {
							g2.setColor (mmol.minicolor[ii].darker ());
							g2.fillOval (biasx + x - r - 3, biasy + y - r - 3, 2 * r + 6, 2 * r + 6);
						} else if (mmol.selecstatus (ii) == 2) {
							g2.setColor (Color.black);
							g2.fillOval (biasx + x - r - 3, biasy + y - r - 3, 2 * r + 6, 2 * r + 6);
						} else {
							if (mmol.selecstatus (ii)
							    == 1) {
								g2.setColor (Color.black);
								g2.fillOval (biasx + x - r - 3, biasy + y - r - 3, 2 * r + 6, 2 * r + 6);
							} else if (mmol.selecstatus (ii) == 2) {
								g2.setColor (Color.black);
								g2.fillOval (biasx + x - r - 3, biasy + y - r - 3, 2 * r + 6, 2 * r + 6);
							}
						}
						g2.setColor (mmol.minicolor[ii]);
					} else
						g2.setColor (Color.white);

					if (bst)
						g2.fillOval (biasx + x - r, biasy + y - r, 2 * r, 2 * r);
					else {
						if (atn) {
							g2.setColor (Color.white);
							g2.fillOval (biasx + x - r, biasy + y - r, 2 * r, 2 * r);
						} else if (nconect == 0)
							g2.fillOval (biasx + x - grint2, biasy + y - grint2, grint, grint);
					}

					int rl = (int) (r * 1.2);	//Rl es el radio donde se inscribiran las letras, que debe ser un poquito mayor que r

					if (atn) {
						if (bst)
							g2.setColor (Color.white);
						else
							g2.setColor (Color.black);

						int pj = (int) (0.85 * rl / mmol.minietiqs[ii].trim ().length ());	//

						//el punteaje tiene que ser menor que esto
						g2.setFont (new Font ("Courier", Font.BOLD, 2 * pj));
						g2.drawString (mmol.minietiqs[ii].trim ().toUpperCase (), biasx + x - rl / 2, biasy + y + rl / 2);
					}
				}	//Fin atomo
			}	//Fin plano

		} else {
			for (int i = 0; i < mmol.nvert; i++) {
				int x = (int) (anchomed + (int) (mmolg.miniverts[i].x * escala));
				int y = (int) (altomed + (int) (mmolg.miniverts[i].y * escala));
				g2.fillRect (biasx + x - 1, biasy + y - 1, 2, 2);
			}
		}
		//Comienzo cadenas informativas
		g2.setColor (java.awt.Color.black);
		g2.setFont (new Font ("Arial", Font.ITALIC, 12));
		g2.drawString (mmol.nvert + " atoms, " + nselec + " selected.", 10, 17);

		formato forma = new formato (7, "##0.###");
		g2.setFont (new Font ("Arial", Font.ITALIC, 10));

		if (nselec == 1) {
			pto3D v = mmol.miniverts[selec[1]];
			g2.drawString ("Atom " + selec[1] + " at " + v.aTexto (), 10, getHeight () - 10);
		} else if (nselec == 2) {
			pto3D v = mmol.miniverts[selec[1]];
			pto3D w = mmol.miniverts[selec[2]];
			g2.drawString ("" + selec[1] + "-" + selec[2] + " distance = " + forma.aCadena (v.dista (w)), 10, getHeight () - 10);
		} else if (nselec == 3) {
			pto3D v = mmol.miniverts[selec[1]];
			pto3D w = mmol.miniverts[selec[2]];
			pto3D u = mmol.miniverts[selec[3]];
			g2.drawString ("" + selec[1] + "-" + selec[2] + "-" +
				       selec[3] + " angle = " + forma.aCadena (u.menos (w).angulocong (v.menos (w))), 10, getHeight () - 10);
		} else if (nselec == 4) {
			pto3D v = mmol.miniverts[selec[1]];
			pto3D w = mmol.miniverts[selec[2]];
			pto3D u = mmol.miniverts[selec[3]];
			pto3D s = mmol.miniverts[selec[4]];
			pto3D a = v.menos (w);
			pto3D b = w.menos (u);
			pto3D c = s.menos (u);
			g2.drawString ("" + selec[1] + "-" + selec[2] + "-" +
				       selec[3] + "-" + selec[4] + " dihedral = " + forma.aCadena (a.dihedrog (b, c)), 10, getHeight () - 10);
		}

		else {
		}
		//los ejes de coordenadas, en una esquinita
		int vxx = (int) (40 + (int) (versorx.x * 30));
		int vxy = (int) (40 + (int) (versorx.y * 30));
		int vyx = (int) (40 + (int) (versory.x * 30));
		int vyy = (int) (40 + (int) (versory.y * 30));
		int vzx = (int) (40 + (int) (versorz.x * 30));
		int vzy = (int) (40 + (int) (versorz.y * 30));
		g2.setStroke (line);
		g2.drawLine (40, 40, vxx, vxy);
		g2.drawLine (40, 40, vyx, vyy);
		g2.drawLine (40, 40, vzx, vzy);
		g2.drawString ("x", vxx + 2, vxy - 1);
		g2.drawString ("y", vyx + 2, vyy - 1);
		g2.drawString ("z", vzx + 2, vzy - 1);

		setPainted ();
	}

	public synchronized void setPainted ()
	{
		pintado = true;
		notifyAll ();
	}

	public void mousePressed (MouseEvent ev)
	{
		Ox = ev.getX ();
		Oy = ev.getY ();
	}

	public void mouseMoved (MouseEvent ev)
	{
	}

	public void mouseClicked (MouseEvent ev)
	{

		//METODOS DEL EDITOR; QUE MUESTRA DISTANCIAS Y ANGULOS

		nselec++;
		if (nselec == 5) {
			deselec ();
		} else {
			Sx = ev.getX ();
			Sy = ev.getY ();

			double dista = 400;	//la distancia en pixeles tiene que ser menor que este valor
			int prox = 0;


			for (int i = 0; i < mmol.nvert; i++) {
				pto3D v = mmolg.miniverts[i];
				int px = (int) (biasx + getWidth () / 2 + v.x * escala);
				int py = (int) (biasy + getHeight () / 2 + v.y * escala);
				double dist = Math.sqrt ((Sx - px) * (Sx - px) + (Sy - py) * (Sy - py));
				if (dist < dista) {
					dista = dist;
					prox = i;
				}
			}
			this.selec[nselec] = prox;

			if (ev.getButton () == 1)
				mmol.selecciona (prox, 1);
			else if (ev.getButton () == 3)
				deselec ();

		}
		this.repaint ();

	}
	public void mouseReleased (MouseEvent ev)
	{
		if (!lrdf)
			lrd = false;
		else
			lrd = true;
		repaint ();

	}
	public void mouseEntered (MouseEvent ev)
	{
		requestFocus ();
	}
	public void mouseExited (MouseEvent ev)
	{
	}
	public void keyTyped (KeyEvent ev)
	{
	}

	public void keyPressed (KeyEvent ev)
	{
		int kc = ev.getKeyCode ();
		if (kc == 32) {
			resetea ();
			this.repaint ();
		}		//Espacio
		else if (kc == 33) {
			if (escala < 200)
				escala *= 1.2;;
			this.repaint ();
		}		//Re Zoom +10%
		else if (kc == 34) {
			if (escala > 2)
				escala *= 0.8;;
			this.repaint ();
		}		//Av Zoom -10%
		else if (kc == 38) {
			biasy -= 20;
			this.repaint ();
		}		//ARR
		else if (kc == 39) {
			biasx += 20;
			this.repaint ();
		} else if (kc == 40) {
			biasy += 20;
			this.repaint ();
		} else if (kc == 72) {
			if (this.hlp == true)
				this.hlp = false;
			else
				this.hlp = true;
			this.repaint ();
		}		//H para ayuda
		else if (kc == 66) {
			if (this.bst == true)
				this.bst = false;
			else
				this.bst = true;
			this.repaint ();
		}		//B para Ball
		else if (kc == 76) {
			if (this.atn == true)
				this.atn = false;
			else
				this.atn = true;
			this.repaint ();
		}		//L para labels
		else if (kc == 67) {
			if (this.hbk == true)
				this.hbk = false;
			else
				this.hbk = true;
			this.repaint ();
		}		//C para corte
		else if (kc == 65) {
			if (this.abt == true)
				this.abt = false;
			else
				this.abt = true;
			this.repaint ();
		}		//A para about
		else if (kc == 82) {
			if (this.lrd == true) {
				this.lrd = false;
				this.repaint ();
				this.lrd = true;
			}
		}		// R para Render temporal
		else if (kc == 37) {
			biasx -= 20;
			this.repaint ();
		} else if (kc == 37) {
			biasx -= 20;
			this.repaint ();
		} else if (kc == 37) {
			biasx -= 20;
			this.repaint ();
		} else if (kc == 10) {
			this.repaint ();
		}		//enter
		else {
		}

	}

	public void resetea ()
	{			//Molecula
		mmolg = mmol.clona ();
		if (mmol.nvert > 6000)
			lrdf = true;
		else
			lrdf = false;
		//Seleccion
		selec = new int[5];
		nselec = 0;
		this.deselec ();
		//ESCALA
		anchomed = getWidth () / 2;
		altomed = getHeight () / 2;
		double d = mmolg.getDim () + 3;
		dim = mmolg.getLejania () + 1;
		escala = getWidth () / d;	//pixeles/angstrom
//versores
		versorx = new pto3D (1, 0, 0);
		versory = new pto3D (0, 1, 0);
		versorz = new pto3D (0, 0, 1);
//Trazos
		double grosor = 0.1f * (float) escala;	//0.1 Angs
		double grosor2 = grosor * 2.0;	//0.2 Amgs
		double grosor3 = grosor * 2.5;	// Cuarto de Angstrom
		int grint = (int) grosor;
		int grint2 = (int) grosor2;
		int grint3 = (int) grosor3;
		gros = new BasicStroke (grint, 0, 1);	//cap_butt, uniones round
		fino = new BasicStroke (grint2, 0, 1);
		line = new BasicStroke (1, 0, 1);
		//BIASES
		biasx = 0;
		biasy = 0;

	}

	public void keyReleased (KeyEvent ev)
	{
	}

	public void mouseDragged (MouseEvent ev)
	{
		if (pintado == true)	//en cuanto arrastro, mido donde estoy
		{
			pintado = false;
			Nx = ev.getX ();
			Ny = ev.getY ();	//Cojo las nuevas posiciones cartesianas
			Ax = Nx - Ox;	// las comparo con las antiguas
			Ay = Ny - Oy;
			double thx = (double) (-360 * (Ax) / getWidth ());
			double thy = (double) (-360 * (Ay) / getHeight ());
			mmolg.giroy (thx);
			mmolg.girox (thy);
			versorx.giroyg (thx);
			versorx.giroxg (thy);
			versory.giroyg (thx);
			versory.giroxg (thy);
			versorz.giroyg (thx);
			versorz.giroxg (thy);

			if (mmol.nvert > 800)
				lrd = true;
			else
				lrd = false;
			repaint ();
			Ox = Nx;
			Oy = Ny;	//una vez usadas, ya son las antiguas
			setPainted ();

		}
	}
	void deselec ()
	{
		this.nselec = 0;
		selec[1] = 0;
		selec[2] = 0;
		selec[3] = 0;
		selec[4] = 0;
		nselec = 0;
		mmol.deselecciona ();
	}


	public void repinta (boolean b, boolean a, boolean h)
	{
		if (b)
			this.bst = true;
		else
			this.bst = false;
		if (a)
			this.atn = true;
		else
			this.atn = false;
		if (h)
			this.hbk = true;
		else
			this.hbk = false;
		this.repaint ();
	}

	public void pintaCon ()
	{
		autocon = true;
		repaint ();
	}
	public void pintaAlt ()
	{
		autocon = false;
		repaint ();
	}

	public void setlrd ()
	{
		this.lrd = true;
		return;
	}
	public void unsetlrd ()
	{
		this.lrd = false;
		return;
	}
	public void setatn ()
	{
		this.atn = true;
		return;
	}
	public void unsetatn ()
	{
		this.atn = false;
		return;
	}
	public void sethbk ()
	{
		this.hbk = true;
		return;
	}
	public void unsethbk ()
	{
		this.hbk = false;
		return;
	}
	public void setbst ()
	{
		this.bst = true;
		return;
	}
	public void unsetbst ()
	{
		this.bst = false;
		return;
	}
}
