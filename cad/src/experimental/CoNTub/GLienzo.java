//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
//import nttabs.*;

public class GLienzo extends JPanel implements MouseListener
{

	JButton bot;
	int n1, m1, n2, m2;
	public GLienzo ()
	{
		addMouseListener (this);
		n1 = 0;
		m1 = 0;
		n2 = 0;
		m2 = 1;
	}


	public GLienzo (int gn1, int gm1, int gn2, int gm2)
	{
		addMouseListener (this);
		n1 = gn1;
		n2 = gn2;
		m1 = gm1;
		m2 = gm2;

	}


	public void paint (Graphics g)
	{
		g.setColor (java.awt.Color.LIGHT_GRAY);
		g.fillRect (0, 0, getSize ().width, getSize ().height);	// blanqueamos

		g.setColor (Color.blue);
		//dibujamos ejes de coordenadas
		int centrox = getSize ().width / 2;
		int centroy = getSize ().height / 2;


		//determinamos la escala en pixeles por unidad. Sean, a buen ojo, 10 px por unidad
		double e = 5;

		g.drawLine (0, centroy, 2 * centrox, centroy);
		g.drawLine (centrox, 0, centrox, 2 * centroy);
		//dibujvos vector del tubo 1
		g.setColor (Color.red);
		double x1 = n1 + m1 / 2;
		double y1 = Math.sqrt (3) / 2 * m1;
		g.drawLine (centrox, centroy, (int) (centrox + e * x1), (int) (centroy - e * y1));
		//dibujamos vector del tubo 2
		g.setColor (Color.green);
		double x2 = n2 + m2 / 2;
		double y2 = Math.sqrt (3) / 2 * m2;
		g.drawLine (centrox, centroy, (int) (centrox + e * x2), (int) (centroy - e * y2));
		//linea que los une
		g.setColor (Color.magenta);
		g.drawLine ((int) (centrox + e * x1), (int) (centroy - e * y1), (int) (centrox + e * x2), (int) (centroy - e * y2));

		g.drawString ("(" + n1 + "," + m1 + ")", 20, 20);
		g.drawString ("(" + n2 + "," + m2 + ")", 80, 20);

		//y girado 60 grasos, aparece la posicion del segundo defecto
		int nh = -(m2 - m1);
		int mh = (m2 - m1) + (n2 - n1);
//y la del primero
		int np = n1 - nh;
		int mp = m1 - mh;


//y la posicion del segundo defecto
		double xh = nh + mh / 2;
		double yh = Math.sqrt (3) / 2 * mh;
//y la posicion del primer defecto
		double xp = np + mp / 2;
		double yp = Math.sqrt (3) / 2 * mp;

		g.setColor (Color.magenta);
		g.drawLine ((int) (centrox + e * x1), (int) (centroy - e * y1), (int) (centrox + e * (x1 + xh)), (int) (centroy - e * (y1 + yh)));
		g.setColor (Color.blue);
		g.drawLine ((int) (centrox + e * x1), (int) (centroy - e * y1), (int) (centrox + e * (x1 + xp)), (int) (centroy - e * (y1 + yp)));

		g.drawString ("(" + np + "," + mp + ") [0,-1]; (" + nh + "," + mh + ")[0,1];", 5, 220);

	}
	public void mousePressed (MouseEvent ev)
	{
		int nn2 = -m2;
		int nm2 = n2 + m2;
		redraw (n1, m1, nn2, nm2);
	}
	public void mouseReleased (MouseEvent ev)
	{
	}
	public void mouseEntered (MouseEvent ev)
	{
	}
	public void mouseExited (MouseEvent ev)
	{
	}
	public void mouseClicked (MouseEvent ev)
	{


	}

	public void redraw (int gn1, int gm1, int gn2, int gm2)
	{			//Segundo metodo, de redibujado, parametrizado
		this.n1 = gn1;
		this.n2 = gn2;
		this.m1 = gm1;
		this.m2 = gm2;
		repaint ();
	}
}
