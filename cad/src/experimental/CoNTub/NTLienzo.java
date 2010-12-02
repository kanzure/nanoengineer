//package nt;

import javax.swing.JPanel;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Image;

public class NTLienzo extends JPanel
{				//Creamos la clase NTLienzo, que es una subclase de Canvas
	//Definicion de las variables de clase, las que sean.
	Graphics BuffGr;
	Image Buffer;
	Nanotubo NT;
	int bx0 = 25;
	int by0 = 120;
	int bxl = 80;
	int byl = 27;
	int dx0 = 75;
	int dy0 = 300;


	public void NTLienzo ()
	{
		NT = new Nanotubo (5, 5);
	}

	public void paint (Graphics g)
	{			//Primer metodo, para dibujar este objeto. implementa graficos a traves del objeto g
		int LA = getWidth ();
		int LL = getHeight ();
		int bx0 = 25;
		int by0 = 130;
		int bxl = 80;
		int byl = 27;
		int dx0 = (int) (LA / 2);
		int dy0 = LL - 40;
		double x = 0, y = 0, xc = 0, yc = 0, z = 0, zc = 0;

		g.setColor (Color.LIGHT_GRAY);
		g.fillRect (0, 0, LA, LL);	// blanqueamos
		g.setColor (Color.blue);	//fijamos el color de escritura del objeto con el que pintamos.

		double nde[] = new double[121];	//Calculo de DENSIDAD DE ESTADOS

		double momzmax = 1.475, deltamz = 0.01;	//parametros de escaneo primitivo
		double d = 1.575;	//media longitud vector reciproco

		for (double momm = -2 * NT.i1 - 2 * NT.i2; momm <= 0; momm++) {
			for (double momz = 0; momz <= momzmax; momz = momz + deltamz) {

				double e1 = NT.energia (momm, momz);
				double e2 = NT.energia (momm, momz + deltamz);
				double deltaE = e1 - e2;
				double mommk = momm * 2 * d / NT.i1 * (Math.sin (Math.PI / 3 - NT.quiral ()));

				if (momz * momz + mommk * mommk < 3.2) {	//           momy<2*d+momx*Math.sqrt(3)){


					int orden = (int) Math.round (byl / 2 * (e1 + e2));	//
					if (Math.abs (e1 - e2) > 0.002) {
						nde[orden] = nde[orden] + deltamz / Math.abs (e1 - e2);
					}	//

					int x1 = bx0 + (int) Math.round (bxl * momz);
					int x2 = bx0 + (int) Math.round (bxl * (momz + deltamz));
					int y1 = (int) Math.round (byl * e1);
					int y2 = (int) Math.round (byl * e2);
					g.drawLine (x1, by0 + y1, x2, by0 + y2);	//ESTRUCTURA DE BANDAS
					g.drawLine (x1, by0 - y1, x2, by0 - y2);
				}
		}}
		//EJES DE COORDENADAS
		g.setColor (Color.black);
		g.drawLine (bx0, by0 - 3 * byl, bx0, by0 + 3 * byl);
		g.drawLine (bx0, by0, bx0 + (int) (bxl * 1.7), by0);
		for (int i = -3; i <= 3; i++)
			g.drawLine (bx0, by0 + (int) byl * i, bx0 - 5, by0 + (int) byl * i);
		g.drawString ("Band Structure", bx0 - 15, 13);
		g.drawString ("-3Ep", bx0 - 20, by0 + 3 * byl + 10);
		g.drawString (" 3Ep", bx0 - 20, by0 - 3 * byl - 10);
		g.drawString ("0", bx0 - 10, by0);
		g.drawString ("k", bx0 + bxl + 20, by0 + 5);

		g.setColor (Color.blue);
		for (int ii = 1; ii <= 3 * byl; ii++) {
			if (nde[ii] > 1)
				g.drawLine (dx0 + ii, dy0 - 2, dx0 + ii, dy0 - 2 - (int) (nde[ii] / 2));	//NDESTADOS
			if (nde[ii] > 1)
				g.drawLine (dx0 - ii, dy0 - 2, dx0 - ii, dy0 - 2 - (int) (nde[ii] / 2));
			//g.drawString(" "+nde[ii], 400,10*ii);
		}

		g.setColor (Color.red);
		g.drawLine (dx0 - 3 * byl, dy0, dx0 + 3 * byl, dy0);
		for (int i = -3; i <= 3; i++)
			g.drawLine (dx0 + (int) byl * i, dy0, dx0 + (int) byl * i, dy0 - 2);
		g.setColor (Color.blue);
		g.drawString ("-3Ep", dx0 - 3 * byl - 10, dy0 + 15);
		g.drawString (" 3Ep", dx0 + 3 * byl - 25, dy0 + 15);
		g.drawString ("0", dx0 - 3, dy0 + 15);
		g.drawString ("Density of States", dx0 - 3 * byl - 5, dy0 + 28);



	}

	public void redraw (int n, int m)
	{			//Segundo metodo, de redibujado, parametrizado
		NT = new Nanotubo (n, m);
		repaint ();
	}
}
