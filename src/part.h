
#define VDW_HASH 127
#define VDW_SIZE (VDW_HASH+1)

struct atom 
{
  struct atomType *type;
  struct atom **vdwBucket;
  struct atom *vdwPrev;
  struct atom *vdwNext;
  double inverseMass;
  //double charge;

  // non-zero if this atom is in any ground jigs
  int isGrounded;
  
  int index;
  int atomID;
  int num_bonds;
  struct bond **bonds;
};

struct bond 
{
  struct atom *a1;
  struct atom *a2;
  char order;

  // A serial number indicating when each of the following fields was
  // last calculated.
  int valid;

  // 1 / sqrt( a2-a1 dot a2-a1 )
  double inverseLength;

  // Unit vector from a1 towards a2
  struct xyz rUnit;
};

enum jigtype {
  Ground,
  Thermometer,
  DihedralMeter,
  AngleMeter,
  RadiusMeter,
  Thermostat,
  RotaryMotor,
  LinearMotor
};

struct jig
{
  char *name;
  int num_atoms;
  struct atom **atoms;

  double data;
  double data2;
  struct xyz xdata;
  
  enum jigtype type;
  union {
    struct {
      double temperature;
    } thermostat;
    
    struct {
      double stall;
      double speed;

      // A point on the motor axis
      struct xyz center;

      // Vector along motor axis (from center)
      struct xyz axis;

      // How far the motor has turned.
      double theta;

      // For each atom in motor, vector from atomCenterOfRotation to
      // atom location.
      struct xyz *atomSpoke; // formerly ator

      // For each atom in motor, length of atomSpoke.
      double *atomRadius; // formerly radius
      
    } rmotor;

    struct {
      double force; // formerly stall
      double stiffness; // formerly speed
      struct xyz center;
      struct xyz axis;

      // Project center of atoms in motor onto axis.  Distance along
      // axis from there to center of mass is motorPosition.
      double motorPosition; // formerly theta

      // Position of motor when force is zero.
      double zeroPosition; // formerly theta0
    } lmotor;
  } j;
};

struct vanDerWaals
{
  struct atom *a1;
  struct atom *a2;
  struct vanDerWaalsParameters *parameters;
};

struct stretch 
{
  struct atom *a1;
  struct atom *a2;
  struct bond *b;
  struct bondStretch *stretchType;
};

struct bend
{
  struct atom *a1;
  struct atom *ac;
  struct atom *a2;
  struct bond *b1;
  struct bond *b2;
  int dir1;
  int dir2;
  struct bendData *bendType;
};

struct torsion
{
  struct atom *a1;
  struct atom *aa;
  struct atom *ab;
  struct atom *a2;
  //params;
};

struct part 
{
  // Where this part was loaded from
  char *filename;

  // Function to call to signal an error while loading
  void (*parseError)(void *);

  // Argument for parseError call
  void *stream;

  // What is the highest atom id number to be defined for this part so
  // far?  Defines length of atom_id_to_index_plus_one array.
  int max_atom_id;

  // Maps atom ids (as defined in an mmp file, for example) into
  // sequentially allocated index numbers.  The index number plus one
  // is stored here, so that zero filling of the accumulator (see
  // allocate.c) will generate invalid indexes.
  int *atom_id_to_index_plus_one;

  double totalMass;
  double totalKineticEnergy;
  struct xyz centerOfGravity;
  struct xyz totalMomentum;
  
  int num_atoms;
  struct atom **atoms;

  int num_bonds;
  struct bond **bonds;

  int num_jigs;
  struct jig **jigs;

  int num_vanDerWaals;
  int num_static_vanDerWaals;
  int start_vanDerWaals_free_scan;
  struct vanDerWaals **vanDerWaals;
  void *vanDerWaals_validity;
  
  int num_stretches;
  struct stretch *stretches;

  int num_bends;
  struct bend *bends;

  int num_torsions;
  struct torsion **torsions;

  struct xyz *positions;
  struct xyz *velocities;

  struct atom *vdwHash[VDW_SIZE][VDW_SIZE][VDW_SIZE];
};

extern struct part *makePart(char *filename, void (*parseError)(void *), void *stream);

extern struct part *endPart(struct part *p);

extern void generateStretches(struct part *p);

extern void generateBends(struct part *p);

extern void updateVanDerWaals(struct part *p, void *validity, struct xyz *positions);

extern void makeAtom(struct part *p, int externalID, int elementType, struct xyz position);

extern void makeBond(struct part *p, int atomID1, int atomID2, char order);

extern void makeVanDerWaals(struct part *p, int atomID1, int atomID2);

extern void makeGround(struct part *p, char *name, int atomListLength, int *atomList);

extern void makeThermometer(struct part *p, char *name, int firstAtomID, int lastAtomID);

extern void makeDihedralMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3, int atomID4);

extern void makeAngleMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3);

extern void makeRadiusMeter(struct part *p, char *name, int atomID1, int atomID2);

extern void makeThermostat(struct part *p, char *name, double temperature, int firstAtomID, int lastAtomID);

extern void makeRotaryMotor(struct part *p, char *name, double stall, double speed, struct xyz *center, struct xyz *axis, int atomListLength, int *atomList);

extern void makeLinearMotor(struct part *p, char *name, double force, double stiffness, struct xyz *center, struct xyz *axis, int atomListLength, int *atomList);

extern void printXYZ(FILE *f, struct xyz p);

extern void printAtomShort(FILE *f, struct atom *a);

extern char printableBondOrder(struct bond *b);

extern void printAtom(FILE *f, struct part *p, struct atom *a);

extern void printBond(FILE *f, struct part *p, struct bond *b);

extern char *printableJigType(struct jig *j);

extern void printJig(FILE *f, struct part *p, struct jig *j);

extern void printVanDerWaals(FILE *f, struct part *p, struct vanDerWaals *v);

extern void printStretch(FILE *f, struct part *p, struct stretch *s);

extern void printBend(FILE *f, struct part *p, struct bend *b);

extern void printPart(FILE *f, struct part *p);
