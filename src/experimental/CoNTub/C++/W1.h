#ifndef W1_H_INCLUDED
#define W1_H_INCLUDED

#define HYDROGEN 1
#define NITROGEN 7

#define LOGGING  0

#include "MoleculaT.h"
#include "String.h"

class W1
{
 protected:
    W1(void) { }
    MoleculaT molecule;
    void finish(int terminator) {
	molecule.centrar ();
	molecule.ponconec ();
	if (terminator == HYDROGEN) {
	    molecule.cierraH ();
	    molecule.ponconec ();
	} else if (terminator == NITROGEN) {
	    molecule.cierraN ();
	    molecule.ponconec ();
	}
    }

 public:

    /*
     * (a, b) - nanotube chirality
     * c - nanotube length in angstroms
     * terminator - an element number for terminating atoms, ignored if not HYDROGEN or NITROGEN
     */
    W1(int a, int b, double c, int terminator);

    std::ostream& mmp(std::ostream& s) {
	return molecule.mmp(s);
    }
};

#endif
