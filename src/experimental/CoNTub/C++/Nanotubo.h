#ifndef NANOTUBO_H_DEFINED
#define NANOTUBO_H_DEFINED

class Nanotubo
{
    double *altura, *phi;  // altura --> height
    double A, deltaz1, deltaz2, deltaphi1, deltaphi2;;

 public:
    int i1, i2, ordenmin, _d;
    Nanotubo (int I, int J);
    Nanotubo (int I, int J, double aalt);
    double deltaz ();
    double deltaphi ();
    double radio ();
    double quiral ();
    double quiralg ();
    double deltazc ();
    double deltaphic ();
    int d ();
    double energia (double momm, double momz);
};

#endif
