//package nt;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
//import nttabs.*;

public class GLienzo2 extends JPanel implements MouseListener
{

	JButton bot;
	int n1, m1, n2, m2;
	boolean ph;
	public GLienzo2 ()
	{
		addMouseListener (this);
		n1 = 0;
		m1 = 0;
		n2 = 0;
		m2 = 1;
		ph = true;
	}


	public GLienzo2 (int gn1, int gm1, int gn2, int gm2)
	{
		addMouseListener (this);
		n1 = gn1;
		n2 = gn2;
		m1 = gm1;
		m2 = gm2;
		ph = true;

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
		double e = 4;

		g.drawLine (0, centroy, 2 * centrox, centroy);
		g.drawLine (centrox, 0, centrox, 2 * centroy);
		//dibujvos vector del tubo 1


		//vector1
		double x1 = n1 + m1 / 2;
		double y1 = Math.sqrt (3) / 2 * m1;
		//vector2
		double x2 = n2 + m2 / 2;
		double y2 = Math.sqrt (3) / 2 * m2;
		//vector union
		int na, ma, nb, mb;

		Nanotubo NTA, NTB;	//ambos tubos
		NTA = new Nanotubo (n1, m1, 2.46);
		NTB = new Nanotubo (n2, m2, 2.46);

		int nad = m2 - m1;
		int mad = n1 - n2 + m1 - m2;
		int nbd = n1 + m1 - m2;
		int mbd = n2 - n1 + m2;
		//La solucion invertida (Hep-Pent)
		int nai = n1 - n2 + m1 - m2;
		int mai = n2 - n1;
		int nbi = n2 - m1 + m2;
		int mbi = m1 - n2 + n1;
		//que viene antes, P o H?? si creciente=true, h va primero, p despues
		if (!ph) {
			na = nai;
			ma = mai;
		} else {
			na = nad;
			ma = mad;
		}

		double xa = na + ma / 2;
		double ya = Math.sqrt (3) / 2 * ma;

		//Dibujos
		g.setColor (Color.black);
		g.drawLine (centrox, centroy, (int) (centrox + e * x1), (int) (centroy - e * y1));
		g.setColor (Color.red);
		g.drawLine (centrox, centroy, (int) (centrox + e * xa), (int) (centroy - e * ya));
		g.setColor (Color.black);
		g.drawLine ((int) (centrox + e * xa), (int) (centroy - e * ya), (int) (centrox + e * (xa + x2)), (int) (centroy - e * (ya + y2)));
		g.setColor (Color.blue);
		g.drawLine ((int) (centrox + e * x1), (int) (centroy - e * y1), (int) (centrox + e * (xa + x2)), (int) (centroy - e * (ya + y2)));

		g.setColor (Color.black);
		g.drawString ("(" + n1 + "," + m1 + ")", 20, 20);
		g.drawString ("(" + n2 + "," + m2 + ")", 80, 20);
		if (ph)
			g.drawString ("p-h, h en (" + na + "," + ma + ")", 10, -10 + 2 * centroy);
		else
			g.drawString ("h-, p en (" + na + "," + ma + ")", 10, -10 + 2 * centroy);
	}

	public void mousePressed (MouseEvent ev)
	{

		int nn2 = n2;
		int nm2 = m2;
		if (ev.getButton () == MouseEvent.BUTTON1) {
			nn2 = -m2;
			nm2 = n2 + m2;
		}
		if (ev.getButton () == MouseEvent.BUTTON3)
			ph = !ph;
		redraw (n1, m1, nn2, nm2, ph);
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

	public void redraw (int gn1, int gm1, int gn2, int gm2, boolean b)
	{			//Segundo metodo, de redibujado, parametrizado
		this.n1 = gn1;
		this.n2 = gn2;
		this.m1 = gm1;
		this.m2 = gm2;
		this.ph = b;
		repaint ();
	}
}
