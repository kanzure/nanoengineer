#ifndef MOLECULAT_H_INCLUDED
#define MOLECULAT_H_INCLUDED

#include <iostream>
#include "MoleculaB.h"
#include "pto3D.h"

class anillo;   // avoid circular definition, do not include "anillo.h"

class MoleculaT: public MoleculaB
{
    double R1, R2;
    int std;	//dice si esta definido el segundo tubo

 public:
    pto3D TEST1;		//fin del tubo, vc que conecta fin de T1 y principio T2,eje del T2
    pto3D TESTC;
    pto3D TEST2;

    MoleculaT () {
	TEST1 = pto3D ();
	TEST2 = pto3D ();
	TESTC = pto3D ();
	R1 = 0;
	R2 = 0;
	std = 0;
    }

    MoleculaT clonaT ();
    // proyecta --> literally, "it projects": something to do with projections
    void proyecta (MoleculaT maux);
    void proyecta (int i);
    // THIS AUTHORIZES US TO ELIMINATE THE MAUX USE
    pto3D proyecta (pto3D psus);	//ESTO NOS AUTORIZA PARA ELIMINAR EL USO DE MAUX
    void proyecta (int sus, MoleculaT maux);
    //los puntos auxiliares se ponen en la molecula auxiliar, pa que no incordien
    // the auxiliary points are put in the auxiliary molecule, pa that do not incordien
    pto3D proyecta (pto3D sustituido, MoleculaT maux);
    void centraentorno (int num);	//ESTA REPE??
    void centraentorno ();   // literally, "it centers surroundings"
    // Terminate any unfinished hexagons at the end of a nanotube with hydrogens.
    void cierraH ();  // cierra --> it closes, H -> hydrogen
    // Terminate any unfinished hexagons at the end of a nanotube with nitrogens.
    void cierraN ();  // cierra --> it closes, N -> nitrogen
    int remataconec ();	//METODO A usar solo con estructuras grafiticas
    void remataconec2 ();	//Metodo alternatiov, que revisa todos los atomos con
    //ESTA ES LA AARIABLE EMTRE = Y ! QUE DICE SI EL ALGORITMO ES
    // TOTALMENTE RELAJADO (1)(SIGUIENDO PARAMETROS DE VECINO)
    // o estricto (0) (SIGUENDO conectividad TRIGONAL)
    String MoleculaT::exploraanillo (int atocentro);
    //OJO, esta distancia media no incluye el enlace priemro, ani[1],ani[2], porque es el que va a ser sustituido
    double dmedia (anillo ani);
    std::ostream& mmp (std::ostream& ost, int index);
    std::ostream& mmp (std::ostream& ost, String inf, int index);
};

#endif
