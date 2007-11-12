#include "simulator.h"

static double
yg_to_Da(double yoctograms)
{
    
    // one Dalton (atomic mass unit) = 1.660538782 yg
    return yoctograms / 1.660538782;
}

static double
zJ_to_kJpermol(double zeptoJoules)
{
    // kJ/mol = zeptoJoules * 1e-24 kJ/zJ * 6.02214179e23 particles/mol
    return zeptoJoules * 6.02214179e-1;
}

static void
writeGromacsAtom(FILE *top, FILE *gro, struct part *p, struct atom *a)
{
    int residueNumber = 1;
    char *residueName = "xxx";
    int chargeGroupNumber = 1;
    int atomNumber = a->index + 1;
    char atomName[256];
    struct xyz pos = p->positions[a->index];
    
    sprintf(atomName, "A%d", a->atomID);
    
    fprintf(top, "%5d %4s %5d %7s %5s %4d %8.3f %8.3f\n", atomNumber, a->type->symbol, residueNumber, residueName, atomName, chargeGroupNumber, a->type->charge, yg_to_Da(a->mass));
    // positions in pm, gromacs wants nm
    fprintf(gro, "%5d%5s%5s%5d%8.3f%8.3f%8.3f\n", residueNumber, residueName, atomName, atomNumber, pos.x/1000.0, pos.y/1000.0, pos.z/1000.0);
}

static void
writeGromacsBond(FILE *top, struct part *p, struct stretch *stretch)
{
    struct atom *a1 = stretch->a1;
    struct atom *a2 = stretch->a2;
    struct bondStretch *bs = stretch->stretchType;
    double r0;
    double De;
    double ks;
    double beta;

    if (bs->quadratic) {
        r0 = bs->r0 * 1e-3; // convert pm to nm
        // bs->ks in N/m or kg s^-2
        // multiply by 1e21 to get zJ m^-2
        // convert to kJ mol^-1 m^-2
        // multiply by 1e-18 to get kJ mol^-1 nm^-2
        ks = zJ_to_kJpermol(bs->ks * 1e21) * 1e-18;
        fprintf(top, "%5d %5d   6   %12.5e %12.5e\n", a1->index+1, a2->index+1, r0, ks);
    } else {
        r0 = bs->r0 * 1e-3; // convert pm to nm
        De = zJ_to_kJpermol(bs->de * 1e3); // bs->de in aJ
        beta = bs->beta * 1e3; // convert pm^-1 to nm^-1
        fprintf(top, "%5d %5d   3   %12.5e %12.5e %12.5e\n", a1->index+1, a2->index+1, r0, De, beta);
    }
}

static void
writeGromacsAngle(FILE *top, struct part *p, struct bend *b)
{
    struct atom *a1 = b->a1;
    struct atom *ac = b->ac;
    struct atom *a2 = b->a2;
    struct bendData *bd = b->bendType;
    double theta0;
    double ktheta;

    theta0 = bd->theta0*180.0/Pi;
    ktheta = zJ_to_kJpermol(bd->kb * 1e-3); // bd->kb in yJ rad^-2, convert to zJ
    fprintf(top, "%5d %5d %5d   1   %12.5f %12.5e\n", a1->index+1, ac->index+1, a2->index+1, theta0, ktheta);
}

static FILE *closure_topologyFile = NULL;

static void
printAtomtypeHashtableEntry(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;

    double c6 = 0.0;
    double c12 = 0.0;
    
    if (at != NULL) {
        // Particle type is A, not sure what options are here.
        fprintf(closure_topologyFile, " %4s %6d %10.5f %8.4f    A   %10.5f %10.5f\n", at->symbol, at->protons, yg_to_Da(at->mass), at->charge, c6, c12);
    }
}

static char *closure_nonbondedPass1Symbol;
static int closure_nonbondedPass1Number;
static struct part *closure_part;

static void
allNonBondedAtomtypesPass2(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;
    int element;
    struct vanDerWaalsParameters *vdw;
    double rvdW; // nm
    double evdW; // kJ mol^-1
    double A; // kJ mol^-1
    double B; // nm^-1
    double C; // kJ mol^-1 nm^6
    
    if (at != NULL) {
        element = at->protons;
        if (element >= closure_nonbondedPass1Number) {
            vdw = getVanDerWaalsTable(closure_nonbondedPass1Number, element);
            rvdW = vdw->rvdW * 1e-3; // convert pm to nm
            if (rvdW > 1e-8) {
                evdW = zJ_to_kJpermol(vdw->evdW);

                A = 2.48e5 * evdW;
                B = 12.5 / rvdW;
                C = evdW * 1.924 * pow(rvdW, 6.0);

                fprintf(closure_topologyFile, "%4s %4s    2 %12.5e %12.5e %12.5e\n", closure_nonbondedPass1Symbol, symbol, A, B, C);
            }
        }
    }
}

static void
allNonBondedAtomtypesPass1(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;

    if (at != NULL) {
        closure_nonbondedPass1Symbol = at->symbol;
        closure_nonbondedPass1Number = at->protons;
        hashtable_iterate(closure_part->atomTypesUsed, allNonBondedAtomtypesPass2);
    }
}


void
printGromacsToplogy(char *basename, struct part *p)
{
    int i;
    FILE *top; // Gromacs topology file (basename.top)
    FILE *gro; // Gromacs coordinate file (basename.gro)
    int len;
    char *fileName;
    
    len = strlen(basename) + 5;
    fileName = allocate(len);
    sprintf(fileName, "%s.top", basename);
    top = fopen(fileName, "w");
    if (top == NULL) {
      perror(fileName);
      free(fileName);
      return;
    }
    sprintf(fileName, "%s.gro", basename);
    gro = fopen(fileName, "w");
    if (gro == NULL) {
      perror(fileName);
      free(fileName);
      return;
    }
    free(fileName);
    
    fprintf(top, "[ defaults ]\n");
    fprintf(top, "; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ\n");
    fprintf(top, "  1             1               no              1.0     1.0\n");
    fprintf(top, "\n");

    fprintf(top, "[ atomtypes ]\n");
    fprintf(top, ";name  at.num    mass    charge   ptype     c6         c12\n");
    closure_topologyFile = top;
    hashtable_iterate(p->atomTypesUsed, printAtomtypeHashtableEntry);
    fprintf(top, "\n");


    fprintf(top, "[ nonbond_params ]\n");
    fprintf(top, ";  i    j func       A           B           C\n");
    closure_part = p;
    hashtable_iterate(p->atomTypesUsed, allNonBondedAtomtypesPass1);
    fprintf(top, "\n");


    fprintf(top, "[ moleculetype ]\n");
    fprintf(top, "; Name            nrexcl (non-bonded exclusion length)\n");
    fprintf(top, "Example             3\n");
    fprintf(top, "\n");

    fprintf(top, "[ atoms ]\n");
    fprintf(top, ";  nr type resnr residue  atom cgnr   charge     mass\n");

    fprintf(gro, "Generated by NanoEngineer-1\n");
    fprintf(gro, "%3d\n", p->num_atoms);
    for (i=0; i<p->num_atoms; i++) {
	writeGromacsAtom(top, gro, p, p->atoms[i]);
    }
    fprintf(gro, "%10.5f%10.5f%10.5f", 10.0, 10.0, 10.0); // periodic box size
    fclose(gro);
    fprintf(top, "\n");

    fprintf(top, "[ bonds ]\n");
    fprintf(top, ";  ai    aj func        r0       Ks or De       beta\n");
    for (i=0; i<p->num_stretches; i++) {
	writeGromacsBond(top, p, &p->stretches[i]);
    }
    fprintf(top, "\n");

    fprintf(top, "[ angles ]\n");
    fprintf(top, ";  ai    aj    ak func       theta0     ktheta\n");
    for (i=0; i<p->num_bends; i++) {
	writeGromacsAngle(top, p, &p->bends[i]);
    }
    fprintf(top, "\n");

    fprintf(top, "[ system ]\n");
    fprintf(top, "; Name\n");
    fprintf(top, "Just Example\n");
    fprintf(top, "\n");

    fprintf(top, "[ molecules ]\n");
    fprintf(top, "; Compound        #mols\n");
    fprintf(top, "Example             1\n");
    fprintf(top, "\n");

    fclose(top);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
