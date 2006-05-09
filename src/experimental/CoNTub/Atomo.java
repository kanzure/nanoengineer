import java.awt.Color;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

class Atomo
{
	int tipo = 0;
	int selec = 0;
	String etiq = "  ";
	String pers = "  ";
	pto3D vert = null;
	Color color = null;
	double r = 0;		//de doubles
	int mconec[];
	int mconecA[];		//array de conec alternativas (para newzmat)
	tabPe TablaP;

	/*************************
	Bucket bucket;
	int index;

	public static final double BUCKETWIDTH = 2.1 * 1.24;

	private static class Triplet {
		int x, y, z;
		public Triplet(int x, int y, int z) {
			this.x = x; this.y = y; this.z = z;
		}
		public Triplet add(int x, int y, int z) {
			return new Triplet(this.x + x, this.y + y, this.z + z);
		}
		public boolean equals(Object other) {
			if (!(other instanceof Triplet))
				return false;
			Triplet tother = (Triplet) other;
			return tother.x == this.x && tother.y == this.y && tother.z == this.z;
		}
	}

	private static Triplet intQuantize(pto3D xyz) {
		return new Triplet((int) ((xyz.x + 0.5 * BUCKETWIDTH) / BUCKETWIDTH),
				   (int) ((xyz.x + 0.5 * BUCKETWIDTH) / BUCKETWIDTH),
				   (int) ((xyz.z + 0.5 * BUCKETWIDTH) / BUCKETWIDTH));
	}

	private static pto3D quantize(pto3D xyz) {
		// Given a position, find the center of the bucket closest to that vector
		// Dado una posición, encontrar el centro del cubo más cercano a ese vector
		return quantize(intQuantize(xyz));
	}
	private static pto3D quantize(Triplet xyzi) {
		// Given a position, find the center of the bucket closest to that vector
		// Dado una posición, encontrar el centro del cubo más cercano a ese vector
		return new pto3D(BUCKETWIDTH * xyzi.x, BUCKETWIDTH * xyzi.y, BUCKETWIDTH * xyzi.z);
	}

	// A Bucket is a cube-sized container to represent the coarse positions of atoms. It is
	// used to find bonds faster - we can pre-sort the atoms into buckets, and when we want
	// to find nearby atoms quickly, we only need to search the nearby buckets.

	// Un Bucket es un envase cubo-clasificado para representar las posiciones gruesas de
	// átomos. Se utiliza para encontrar enlaces más rápidos - preclasificación de la poder los
	// átomos en los Buckets, y cuando deseamos encontrar los átomos próximos rápidamente,
	// nosotros necesitamos solamente buscar los Buckets próximos.

	public static class Bucket {
		// a little bigger than a double bond length?
		private pto3D center;
		private ArrayList susatomos;

		Bucket(Triplet tr) {
			this.center = quantize(tr);
			susatomos = new ArrayList();
		}
		Bucket(pto3D center) {
			this.center = quantize(center);
			susatomos = new ArrayList();
		}
		Bucket(float x, float y, float z) {
			center = quantize(new pto3D(x, y, z));
			susatomos = new ArrayList();
		}

		public void add(Atomo atm) {
			if (!susatomos.contains(atm))
				susatomos.add(atm);
		}
		public int size() {
			return susatomos.size();
		}
		public Atomo get(int i) {
			return (Atomo) susatomos.get(i);
		}
		private class BIterator implements Iterator {
			int i, n;
			Object[] objs;
			private BIterator(ArrayList alst) {
				n = alst.size();
				for (i = 0; i < n; i++)
					objs[i] = alst.get(i);
				i = 0;
			}
			public void remove() throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}
			public boolean hasNext() {
				return i < n;
			}
			public Object next() throws java.util.NoSuchElementException {
				if (i >= n)
					throw new java.util.NoSuchElementException();
				return objs[i++];
			}
		}
		public Iterator iterator() {
			return new BIterator(susatomos);
		}
	}

	public static class BucketMap {
		HashMap buckets;
		public BucketMap() {
			buckets = new HashMap();
		}
		public Bucket get(pto3D xyz) {
			Triplet key = intQuantize(xyz);
			if (!buckets.containsKey(key))
				buckets.put(key, new Bucket(xyz));
			return (Bucket) buckets.get(key);
		}
		private class MetaIterator implements Iterator {
			ArrayList iters;
			private MetaIterator() {
				iters = new ArrayList();
			}
			public void add(Iterator iter) {
				iters.add(iter);
			}
			public void remove() throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}
			public boolean hasNext() {
				if (iters.size() == 0) return false;
				Iterator b = (Iterator) iters.get(0);
				return b.hasNext();
			}
			public Object next() throws java.util.NoSuchElementException {
				if (iters.size() == 0) {
					throw new java.util.NoSuchElementException();
				}
				try {
					Iterator b = (Iterator) iters.get(0);
					return b.next();
				} catch (java.util.NoSuchElementException nsee) {
					iters.remove(0);
					return next();
				}
			}
		}
		public Iterator iterator(pto3D xyz) {
			Bucket b;
			MetaIterator mi = new MetaIterator();
			Triplet xyz0 = intQuantize(xyz);
			b = (Bucket) buckets.get(xyz0);
			if (b != null)
				mi.add(b.iterator());
			int[][] diffs = { { -1, 0, 0 }, { 1, 0, 0 },
					  { 0, -1, 0 }, { 0, 1, 0 },
					  { 0, 0, -1 }, { 0, 0, 1 } };
			for (int i = 0; i < 6; i++) {
				Triplet xyz1 = xyz0.add(diffs[i][0], diffs[i][1], diffs[i][2]);
				b = (Bucket) buckets.get(xyz1);
				if (b != null)
					mi.add(b.iterator());
			}
			return mi;
		}
	}

	public pto3D bucketCenter() {
		return quantize(vert);
	}
	public Iterator getIterator(BucketMap bmap) {
		return bmap.iterator(vert);
	}
	*************************/

	  Atomo ()
	{
		vert = new pto3D (0.0, 0.0, 0.0);
		tipo = 0;
		r = 0.0;
		selec = 0;
		color = Color.black;
		etiq = "  ";
		pers = "  ";
		mconec = new int[10];
		  mconecA = new int[10];
		  TablaP = tabPe.getInstance();

	}

	Atomo (int t, int s, String e, String p, pto3D pto, Color c, double radio)
	{
		tipo = t;
		etiq = e;
		pers = p;
		vert = pto.clona ();
		color = c;
		r = radio;
		mconec = new int[10];
		mconecA = new int[10];
		TablaP = tabPe.getInstance();

	}

	Atomo (pto3D p, int t)
	{
		TablaP = tabPe.getInstance();
		tipo = t;
		vert = p.clona ();
		etiq = TablaP.getSimbolo (t);
		pers = "  ";
		color = TablaP.getColor (t);
		r = TablaP.getSize (t);
		mconec = new int[10];
		mconecA = new int[10];

	}

	Atomo (pto3D p, int t, Color c)
	{
		TablaP = tabPe.getInstance();
		tipo = t;
		vert = p.clona ();
		etiq = TablaP.getSimbolo (t);
		pers = "  ";
		color = c;
		r = TablaP.getSize (t);
		mconec = new int[10];
		mconecA = new int[10];

	}
//LISTA DE METODOS BASICOS!!!



}
