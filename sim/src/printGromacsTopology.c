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

static int
atomNumber(struct part *p, struct atom *a)
{
    if (a->isGenerated != 0) {
        return a->index + p->num_atoms + 1;
    } else {
        return a->index + 1;
    }
}

static void
writeGromacsAtom(FILE *top, FILE *gro, FILE *ndx, struct part *p, struct atom *a, struct xyz translate)
{
    int residueNumber = 1;
    char *residueName = "xxx";
    int atom_num = atomNumber(p, a);
    int chargeGroupNumber = atom_num;
    char atomName[256];
    struct xyz pos;
    
    sprintf(atomName, "A%d", a->atomID);
    
    fprintf(top, "%5d %5s %5d %7s %5s %4d %8.3f %8.3f\n", atom_num, a->type->symbol, residueNumber, residueName, atomName, chargeGroupNumber, a->type->charge, yg_to_Da(a->mass));
    if (a->type->isVirtual) {
        pos.x = 0.0;
        pos.y = 0.0;
        pos.z = 0.0;
    } else {
        pos = p->positions[a->index];
        vdivc(pos, 1000.0); // convert pm to nm
        vsub(pos, translate); // shift to new bounding volume
    }
    fprintf(gro, "%5d%5s%5s%5d%8.3f%8.3f%8.3f\n", residueNumber, residueName, atomName, atom_num, pos.x, pos.y, pos.z);
    if (a->isGrounded) {
        fprintf(ndx, "%d\n", atom_num);
    }
}

struct atomType *Gv5_type = NULL;
struct atomType *Ax3_type = NULL;
struct atomType *Pl5_type = NULL;
struct atomType *Ss3_type = NULL;

//   Pl   Pl   Pl
//   |    |    |
//  Gv1--Gv2--Gv3
//   |    |    |
//   Pl   Pl   Pl

static int
writeExclusionsOnOneGroove(FILE *top,
                           struct part *p,
                           struct atom *first,
                           struct atom *groove,
                           int gotOne)
{
    struct atom *toExclude;
    struct bond *b;
    int i;
    int j;

    for (i=0; i<groove->num_bonds; i++) {
        b = groove->bonds[i];
        toExclude = NULL;
        if (b->a1 == groove && b->a2 != first && (atomIsType(b->a2, Pl5_type) ||
                                                  atomIsType(b->a2, Ss3_type))) {
            toExclude = b->a2;
        } else if (b->a2 == groove && b->a1 != first && (atomIsType(b->a1, Pl5_type) ||
                                                         atomIsType(b->a1, Ss3_type))) {
            toExclude = b->a1;
        }
        if (toExclude != NULL) {
            if (!gotOne) {
                fprintf(top, "%d", atomNumber(p, first));
                gotOne = 1;
                for (j=0; j<first->num_bonds; j++) {
                    b = first->bonds[j];
                    // add exclusions for Pl5-2-Pl5 bonds, which are
                    // pattern generated bonds between bridging
                    // phosphates in a crossover.
                    if (b->order != '2') {
                        continue;
                    }
                    if (b->a1 == first && atomIsType(b->a2, Pl5_type)) {
                        fprintf(top, " %d", atomNumber(p, b->a2));
                        break;
                    }
                    if (b->a2 == first && atomIsType(b->a1, Pl5_type)) {
                        fprintf(top, " %d", atomNumber(p, b->a1));
                        break;
                    }
                }
            }
            fprintf(top, " %d", atomNumber(p, toExclude));
        }
    }
    return gotOne;
}

static int
writeExclusion(FILE *top,
               struct part *p,
               struct atom *first,
               struct atom *groove1,
               struct atom *groove2,
               int gotOne,
               int depth)
{
    struct bond *b;
    int i;

    gotOne |= writeExclusionsOnOneGroove(top, p, first, groove2, gotOne);
    if (--depth < 1) {
        return gotOne;
    }
    for (i=0; i<groove2->num_bonds; i++) {
        b = groove2->bonds[i];
        if (b->a1 == groove2 && b->a2 != groove1 && (atomIsType(b->a2, Gv5_type) ||
                                                     atomIsType(b->a2, Ax3_type))) {
            gotOne |= writeExclusion(top, p, first, groove2, b->a2, gotOne, depth);
        } else if (b->a2 == groove2 && b->a1 != groove1 && (atomIsType(b->a1, Gv5_type) ||
                                                            atomIsType(b->a1, Ax3_type))) {
            gotOne |= writeExclusion(top, p, first, groove2, b->a1, gotOne, depth);
        }
    }
    return gotOne;
}


static void
writeGromacsExclusions(FILE *top, struct part *p, struct atom *a)
{
    struct bond *b;
    struct atom *first;
    int i;
    int j;
    int gotOne = 0;
    int depthToExclude;

    // vdw cutoff radius divided by basepair to basepair distance,
    // with some fudge.
    depthToExclude = (int)(VanDerWaalsCutoffRadius * 1.6 / 0.318); // all in nm

    if (!(atomIsType(a, Gv5_type) || atomIsType(a, Ax3_type))) {
        return;
    }
    for (i=0; i<a->num_bonds; i++) {
        b = a->bonds[i];
        first = NULL;
        if (b->a1 == a && (atomIsType(b->a2, Pl5_type) ||
                           atomIsType(b->a2, Ss3_type))) {
            first = b->a2;
        } else if (b->a2 == a && (atomIsType(b->a1, Pl5_type) ||
                                  atomIsType(b->a1, Ss3_type))) {
            first = b->a1;
        }
        if (first != NULL) {
            gotOne = writeExclusionsOnOneGroove(top, p, first, a, 0);
            for (j=0; j<a->num_bonds; j++) {
                b = a->bonds[j];
                if (b->a1 == a && (atomIsType(b->a2, Gv5_type) ||
                                   atomIsType(b->a2, Ax3_type))) {
                    gotOne |= writeExclusion(top, p, first, a, b->a2, gotOne, depthToExclude);
                } else if (b->a2 == a && (atomIsType(b->a1, Gv5_type) ||
                                          atomIsType(b->a1, Ax3_type))) {
                    gotOne |= writeExclusion(top, p, first, a, b->a1, gotOne, depthToExclude);
                }
            }
            if (gotOne) {
                fprintf(top, "\n");
            }
        }
    }
}


static void
writeGromacsVirtualSite(FILE *top, struct part *p, struct atom *a)
{
    int atom_num = atomNumber(p, a);
    struct atom *v1 = a->creationParameters.v.virtual1;
    struct atom *v2 = a->creationParameters.v.virtual2;
    struct atom *v3 = a->creationParameters.v.virtual3;
    int function = a->virtualFunction;
    double virtualA = a->creationParameters.v.virtualA;
    double virtualB = a->creationParameters.v.virtualB;

    if (a->virtualConstructionAtoms > 0) {
        fprintf(top, "%5d %5d %5d %5d %d %f %f\n", atom_num, atomNumber(p, v1), atomNumber(p, v2), atomNumber(p, v3), function, virtualA, virtualB);
    }
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
        if (fabs(ks) > 1e-8) {
            fprintf(top, "%5d %5d   %d   %12.5e %12.5e\n", atomNumber(p, a1), atomNumber(p, a2), bs->quadratic, r0, ks);
        }
    } else {
        r0 = bs->r0 * 1e-3; // convert pm to nm
        De = zJ_to_kJpermol(bs->de * 1e3); // bs->de in aJ
        beta = bs->beta * 1e3; // convert pm^-1 to nm^-1
        fprintf(top, "%5d %5d   3   %12.5e %12.5e %12.5e\n", atomNumber(p, a1), atomNumber(p, a2), r0, De, beta);
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
    if (fabs(ktheta) > 1e-10) {
        fprintf(top, "%5d %5d %5d   1   %12.5f %12.5e\n", atomNumber(p, a1), atomNumber(p, ac), atomNumber(p, a2), theta0, ktheta);
    }
}

static FILE *closure_topologyFile = NULL;

static void
printAtomtypeHashtableEntry(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;

    double A = 0.0;
    double B = 0.0;
    double C = 0.0;
    
    if (at != NULL) {
        fprintf(closure_topologyFile, " %5s %6d %10.5f %8.4f    %c   %10.5f %10.5f %10.5f\n", at->symbol, at->protons, yg_to_Da(at->mass), at->charge, at->isVirtual ? 'V' : 'A', A, B, C);
    }
}

static char *closure_nonbondedPass1Symbol;
static int closure_nonbondedPass1Number;
static struct part *closure_part;

static int nonbonded_function; // 1=Lennard-Jones, 2=Buckingham

static void
writeGromacsNonBonded(FILE *top, struct part *p, struct vanDerWaals *vdw)
{
    struct atom *a1 = vdw->a1;
    struct atom *a2 = vdw->a2;
    struct vanDerWaalsParameters *params = vdw->parameters;
    double rvdW; // nm
    double evdW; // kJ mol^-1
    double A;
    double B;
    double C;

    rvdW = params->rvdW * 1e-3; // convert pm to nm
    if (rvdW > 1e-8) {
        evdW = zJ_to_kJpermol(params->evdW);

        if (nonbonded_function == 1) {
            // Lennard-Jones
            //A = 2.0 * evdW * pow(rvdW, 6.0);
            //B = evdW * pow(rvdW, 12.0);

            // Yukawa (user defined table)
            A = 1.0;
            B = 0.0;
            if (EnableElectrostatic) {
                fprintf(closure_topologyFile, "%4d %4d    1 %12.5e %12.5e\n", atomNumber(p, a1), atomNumber(p, a2), A, B);
            }
        } else {
            A = 2.48e5 * evdW;                 // kJ mol^-1
            B = 12.5 / rvdW;                   // nm^-1
            C = evdW * 1.924 * pow(rvdW, 6.0); // kJ mol^-1 nm^6

            fprintf(closure_topologyFile, "%4d %4d    2 %12.5e %12.5e %12.5e\n", atomNumber(p, a1), atomNumber(p, a2), A, B, C);
        }
    }
}

static void
allNonBondedAtomtypesPass2(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;
    int element;
    struct vanDerWaalsParameters *vdw;
    double rvdW; // nm
    double evdW; // kJ mol^-1
    double A;
    double B;
    double C;

    if (at != NULL) {
        element = at->protons;
        if (element >= closure_nonbondedPass1Number) {
            vdw = getVanDerWaalsTable(closure_nonbondedPass1Number, element);
            if (vdw != NULL) {
                rvdW = vdw->rvdW * 1e-3; // convert pm to nm
                if (rvdW > 1e-8) {
                    evdW = zJ_to_kJpermol(vdw->evdW);

                    if (nonbonded_function == 1) {
                        // Lennard-Jones
                        //A = 2.0 * evdW * pow(rvdW, 6.0);
                        //B = evdW * pow(rvdW, 12.0);

                        // Yukawa (user defined table)
                        A = 1.0;
                        B = 0.0;
                        if (element > 110 && EnableElectrostatic) {
                            fprintf(closure_topologyFile, "%4s %4s    1 %12.5e %12.5e\n", closure_nonbondedPass1Symbol, symbol, A, B);
                        }
                    } else {
                        A = 2.48e5 * evdW;                 // kJ mol^-1
                        B = 12.5 / rvdW;                   // nm^-1
                        C = evdW * 1.924 * pow(rvdW, 6.0); // kJ mol^-1 nm^6

                        fprintf(closure_topologyFile, "%4s %4s    2 %12.5e %12.5e %12.5e\n", closure_nonbondedPass1Symbol, symbol, A, B, C);
                    }
                }
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

static char *
io_error(char *fileName)
{
    char *message = strerror(errno);
    int len = strlen(message) + strlen(fileName) + 4;
    char *ret = (char *)allocate(len);
    
    sprintf(ret, "%s: %s\n", fileName, message);
    return ret;
}

static void
getBoundingVolume(struct part *p, struct xyz *minp, struct xyz *maxp, double vdwCutoff)
{
    int i;
    double delta;
    struct xyz min;
    struct xyz max;
    struct xyz pos;
    struct xyz boxsize;
    
#define MAX_FLOAT 3e38
    min.x = min.y = min.z = MAX_FLOAT;
    max.x = max.y = max.z = -MAX_FLOAT;

    for (i=0; i<p->num_atoms; i++) {
	pos = p->atoms[i]->creationParameters.r.initialPosition;
        if (min.x > pos.x) {
            min.x = pos.x;
        }
        if (min.y > pos.y) {
            min.y = pos.y;
        }
        if (min.z > pos.z) {
            min.z = pos.z;
        }
        if (max.x < pos.x) {
            max.x = pos.x;
        }
        if (max.y < pos.y) {
            max.y = pos.y;
        }
        if (max.z < pos.z) {
            max.z = pos.z;
        }
    }
    max.x /= 1000.0 ; // convert pm to nm
    max.y /= 1000.0 ;
    max.z /= 1000.0 ;
    min.x /= 1000.0 ;
    min.y /= 1000.0 ;
    min.z /= 1000.0 ;
    
    // Expand the bounding volume to allow for expansion during
    // minimization.  The bounding volume must be at least vdwCutoff
    // in each direction, so objects don't show up more than once in
    // the non-bonded calculations.  Make it be at least that size,
    // then grow it by a constant factor.
    vsub2(boxsize, max, min);
    if (boxsize.x < vdwCutoff) {
        delta = (vdwCutoff - boxsize.x) / 2.0;
        max.x += delta;
        min.x -= delta;
    }
    if (boxsize.y < vdwCutoff) {
        delta = (vdwCutoff - boxsize.y) / 2.0;
        max.y += delta;
        min.y -= delta;
    }
    if (boxsize.z < vdwCutoff) {
        delta = (vdwCutoff - boxsize.z) / 2.0;
        max.z += delta;
        min.z -= delta;
    }
#define EXPANSION_FACTOR 1.3
    vsub2(boxsize, max, min);
    delta = (boxsize.x * EXPANSION_FACTOR) / 2.0;
    max.x += delta;
    min.x -= delta;
    delta = (boxsize.y * EXPANSION_FACTOR) / 2.0;
    max.y += delta;
    min.y -= delta;
    delta = (boxsize.z * EXPANSION_FACTOR) / 2.0;
    max.z += delta;
    min.z -= delta;

    *minp = min;
    *maxp = max;
}


// returns NULL for success, or an error string.
char *
printGromacsToplogy(char *basename, struct part *p)
{
    int i;
    FILE *top; // Gromacs topology file (basename.top)
    FILE *gro; // Gromacs coordinate file (basename.gro)
    FILE *mdp; // Gromacs configuration file (basename.mdp)
    FILE *ndx; // Gromacs group (index) file (basename.ndx)
    FILE *translate; // Add this to each .gro position to get .mmp positions (basename.translate)
    int len;
    double vdwCutoff;
    char *fileName;
    char *ret = NULL;
    struct jig *jig;
    struct xyz boxsize; // far corner of bounding volume starting at origin
    struct xyz min; // most negative corner of bounding volume
    struct xyz max; // most positive corner of bounding volume
    int EnableNeighborSearchGrid = 0;
    struct patternParameter *param;
    int enableExclusions;

    for (i=0; i<p->num_jigs; i++) {
        jig = p->jigs[i];
        switch (jig->type) {
        case Ground:         // supported
        case Thermometer:    // measurement
        case DihedralMeter:  // measurement
        case AngleMeter:     // measurement
        case RadiusMeter:    // measurement
        case Thermostat:     // questionable, but meaningless
            break; // these are allowed in gromacs minimize
        default:
            WARNING("Part contains active jig, ignored in GROMACS minimize.");
            i = p->num_jigs ; // only warn once
            break;
        }
    }
    
    param = getPatternParameter("enableExclusions"); BAILR(py_exc_str);
    enableExclusions = (int)param->value;
    
    len = strlen(basename) + 12;
    fileName = allocate(len);
    sprintf(fileName, "%s.top", basename);
    top = fopen(fileName, "w");
    if (top == NULL) {
        ret = io_error(fileName);
        free(fileName);
        return ret;
    }
    sprintf(fileName, "%s.gro", basename);
    gro = fopen(fileName, "w");
    if (gro == NULL) {
        ret = io_error(fileName);
        free(fileName);
        fclose(top);
        return ret;
    }
    sprintf(fileName, "%s.mdp", basename);
    mdp = fopen(fileName, "w");
    if (mdp == NULL) {
        ret = io_error(fileName);
        free(fileName);
        fclose(top);
        fclose(gro);
        return ret;
    }
    sprintf(fileName, "%s.ndx", basename);
    ndx = fopen(fileName, "w");
    if (ndx == NULL) {
        ret = io_error(fileName);
        free(fileName);
        fclose(top);
        fclose(gro);
        fclose(mdp);
        return ret;
    }
    sprintf(fileName, "%s.translate", basename);
    translate = fopen(fileName, "w");
    if (translate == NULL) {
        ret = io_error(fileName);
        free(fileName);
        fclose(top);
        fclose(gro);
        fclose(mdp);
        fclose(ndx);
        return ret;
    }
    free(fileName);

    Gv5_type = getAtomTypeByName("Gv5");
    Ax3_type = getAtomTypeByName("Ax3");
    Pl5_type = getAtomTypeByName("Pl5");
    Ss3_type = getAtomTypeByName("Ss3");
    
    fprintf(mdp, "title               =  NE1-minimize\n");
    fprintf(mdp, "constraints         =  none\n");
    if (PathToCpp != NULL) {
        fprintf(mdp, "cpp                 =  %s\n", PathToCpp);
    }
    fprintf(mdp, "pbc                 =  %s\n", EnableNeighborSearchGrid ? "xyz" : "no"); // periodic boundary conditions
    fprintf(mdp, "integrator          =  cg\n"); // cg or steep, for conjugate gradients or steepest descent
    fprintf(mdp, "nsteps              =  100000\n"); // max number of iterations
    fprintf(mdp, "nstcgsteep          =  100\n"); // frequency of steep steps during cg
    fprintf(mdp, "nstlist             =  %d\n", NeighborSearching ? 10 : 0); // update frequency for neighbor list
    fprintf(mdp, "ns_type             =  %s\n", EnableNeighborSearchGrid ? "grid" : "simple"); // neighbor search type, must be simple for pbc=no
    fprintf(mdp, "nstxout             =  10\n"); // frequency to write coordinates to output trajectory file

    if (VanDerWaalsCutoffRadius < 0) {
        vdwCutoff = 1.0;
        nonbonded_function = 2;
    } else {
        vdwCutoff = VanDerWaalsCutoffRadius;
        fprintf(mdp, "coulombtype         =  User\n");
        fprintf(mdp, "vdwtype             =  User\n");
        fprintf(mdp, "table-extension     =  %f\n", vdwCutoff);
        nonbonded_function = 1;
    }

    // rlist, rcoulomb and rvdw must be equal when ns_type = simple
    fprintf(mdp, "rlist               =  %f\n", vdwCutoff); // short range neighbor list cutoff distance
    fprintf(mdp, "rcoulomb            =  %f\n", vdwCutoff); // coulomb function cutoff distance
    fprintf(mdp, "rvdw                =  %f\n", vdwCutoff); // vdw cutoff distance
    
    fprintf(mdp, "epsilon_r           =  %f\n", DielectricConstant);
    fprintf(mdp, "freezegrps          =  Anchor\n"); // which group of atoms to hold fixed
    fprintf(mdp, "freezedim           =  Y Y Y\n"); // fix in all three dimensions
    fprintf(mdp, ";\n");
    fprintf(mdp, ";       Energy minimizing stuff\n");
    fprintf(mdp, ";\n");
    // emtol in kJ mol^-1 nm^-1
    // MinimizeThresholdEndRMS is in pN (1e-12 J m^-1), or zJ nm^-1
    fprintf(mdp, "emtol               =  %f\n", zJ_to_kJpermol(MinimizeThresholdEndRMS));
    fprintf(mdp, "emstep              =  0.01\n"); // initial step size in nm
    fclose(mdp);
    
    fprintf(top, "[ defaults ]\n");
    fprintf(top, "; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ\n");
    fprintf(top, "  %d             1              no               1.0     1.0\n", nonbonded_function);
    fprintf(top, "\n");

    fprintf(top, "[ atomtypes ]\n");
    fprintf(top, ";name   at.num    mass    charge   ptype     A          B          C\n");
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
    fprintf(top, ";  nr type  resnr residue  atom cgnr   charge     mass\n");

    fprintf(gro, "Generated by NanoEngineer-1\n");
    fprintf(gro, "%3d\n", p->num_atoms + p->num_generated_atoms);

    if (EnableNeighborSearchGrid) {
        getBoundingVolume(p, &min, &max, vdwCutoff);
        vsub2(boxsize, max, min);
    } else {
        vsetc(min, 0.0);
        vsetc(max, 0.0);
        vsetc(boxsize, 0.0);
    }

    fprintf(translate, "%10.5f\n%10.5f\n%10.5f\n", min.x, min.y, min.z);
    fprintf(translate, "X, Y, and Z offsets in nm between coordinates in .gro file\n");
    fprintf(translate, "and those in .mmp file.  Add these offsets to the .gro\n");
    fprintf(translate, "positions and multiply by 10000 to get .mmp positions (in 0.1pm)\n");
    fclose(translate);
    
    fprintf(ndx, "[ Anchor ]\n");

    for (i=0; i<p->num_atoms; i++) {
	writeGromacsAtom(top, gro, ndx, p, p->atoms[i], min);
    }
    for (i=0; i<p->num_generated_atoms; i++) {
	writeGromacsAtom(top, gro, ndx, p, p->generated_atoms[i], min);
    }

    fprintf(gro, "%10.5f%10.5f%10.5f\n", boxsize.x, boxsize.y, boxsize.z); // periodic box size
    fclose(gro);
    fclose(ndx);
    
    fprintf(top, "\n");

    fprintf(top, "[ virtual_sites3 ]\n");
    for (i=0; i<p->num_atoms; i++) {
        writeGromacsVirtualSite(top, p, p->atoms[i]);
    }
    for (i=0; i<p->num_generated_atoms; i++) {
        writeGromacsVirtualSite(top, p, p->generated_atoms[i]);
    }
    fprintf(top, "\n");
    
    fprintf(top, "[ bonds ]\n");
    fprintf(top, ";  ai    aj func        r0       Ks or De       beta\n");
    for (i=0; i<p->num_stretches; i++) {
	writeGromacsBond(top, p, &p->stretches[i]);
    }
    fprintf(top, "\n");
    
    fprintf(top, "[ pairs ]\n");
    fprintf(top, "; ai   aj   func        A            B            C\n");
    for (i=0; i<p->num_static_vanDerWaals; i++) {
	writeGromacsNonBonded(top, p, p->vanDerWaals[i]);
    }
    fprintf(top, "\n");

    fprintf(top, "[ angles ]\n");
    fprintf(top, ";  ai    aj    ak func       theta0     ktheta\n");
    for (i=0; i<p->num_bends; i++) {
	writeGromacsAngle(top, p, &p->bends[i]);
    }
    fprintf(top, "\n");

    if (enableExclusions) {
        fprintf(top, "[ exclusions ]\n");
        for (i=0; i<p->num_atoms; i++) {
            writeGromacsExclusions(top, p, p->atoms[i]);
        }
        fprintf(top, "\n");
    }

    fprintf(top, "[ system ]\n");
    fprintf(top, "; Name\n");
    fprintf(top, "Just Example\n");
    fprintf(top, "\n");

    fprintf(top, "[ molecules ]\n");
    fprintf(top, "; Compound        #mols\n");
    fprintf(top, "Example             1\n");
    fprintf(top, "\n");

    fclose(top);
    return NULL;
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
