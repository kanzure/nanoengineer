private pto3D aproxNT(pto3D pto, int posi, int posj, pto3D origen, int i,ing j,
			    pto3D orient, pto3D inicio, double coef)
{
	//tenemos el eje,el pto de origen, y el origen

	//versorizamos tanto la orientacion como el vector de inicio,
	//de modo que tengamos nuestros particulares vx vy perpendiculares a orient

	pto3D vz=orient.aversor();
	pto3d vy=origen.aversor();
	pto3D vx=vy.prodvec(vz);
	Nanotubo NT=new Nanotubo(i,j);

	//contamos los pasos tanto radiales como longitudinales correspondientes a posi, posj

	double deltazeta=posi*NT.deltaz1  +posj*NT.deltaz2; //revisar si el orden esta bien
	double deltaphi= posi*NT.deltaphi1+posj*Nt.deltaphi2;

	double sdp=Math.sin(deltaphi);
	double cdp=Math.cos(deltaphi);

	pto3D objet=origen.mas(vz.escala(deltaz).mas(vx.escala(R*cdp)).mas(vy.escala(R*sdp)));

	return pto.mediapond(objet,coef);

	//una vez supromido el pto medio,


}
