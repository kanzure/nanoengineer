/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#ifndef PART_H_INCLUDED
#define PART_H_INCLUDED

#define RCSID_PART_H  "$Id$"

// See part.c for comment defining these values.  Don't change any of
// them without deeply understanding the vdw search algorithm there.
#define GRID_SPACING 300
#define GRID_OCCUPANCY 1
#define GRID_SIZE 128
#define GRID_MASK 127
#define GRID_MASK_FUZZY 126
#define GRID_FUZZY_BUCKET_WIDTH 2
#define GRID_WRAP_COMPARE (GRID_SPACING * GRID_SIZE / 2)

// Si has the highest vdw radius, 225 pm
#define MAX_VDW_RADIUS 225

// width of the whole vdw search grid is GRID_WRAP_COMPARE * 2
// currently 38400 pm, or ~170 times Si vdw radius.

// cutoff distance for DNA pseudo atom interactions should be in the
// several nm range, which still leaves the grid comparison useful.

enum hybridization {
  sp,
  sp2,
  sp2_g, // graphitic
  sp3,
  sp3d
};

struct atom 
{
    struct atomType *type;
    enum hybridization hybridization;
  
    unsigned char vdwBucketIndexX;
    unsigned char vdwBucketIndexY;
    unsigned char vdwBucketIndexZ;    
    unsigned char vdwBucketInvalid;    
    struct atom *vdwPrev;
    struct atom *vdwNext;
    double mass;               // yg, or yoctograms, or 1e-24 g
    double inverseMass;        // Dt*Dt / (mass * 1e-27)
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

enum jointType {
    JointBall,
    JointHinge,
    JointSlider
};

struct joint
{
    enum jointType type;
  
    int rigidBody1;
    int rigidBody2;

    int station1_1;
    int station2_1;

    int axis1_1;
    int axis2_1;
};

struct rigidBody 
{
    char *name;

    // StationPoints are named locations specified in body relative
    // coordinates.  Joints connect bodies together at their
    // StationPoints.
    int num_stations;
    struct xyz *stations;
    char **stationNames;

    // Axes are named orientations specified in body relative
    // coordinates.  Joints can maintain these orientations parallel
    // to each other for a pair of bodies.
    int num_axes;
    struct xyz *axes;
    char **axisNames;

    // Attachments link atoms to rigid bodies.  attachmentLocations
    // are in body relative coordinates, and are calculated from the
    // initial positions of the attached atoms, and the initial
    // position/orientation of the body.
    int num_attachments;
    struct xyz *attachmentLocations;
    int *attachmentAtomIndices;
    
    double inertiaTensor[6];

    double mass;

    struct xyz position;
    struct xyz velocity;

    struct quaternion orientation;
    struct xyz rotation; // Euler angle rotation rates
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

    // The minimizer will allocate this many coordinates to be
    // minimized in addition to the atom positions.
    int degreesOfFreedom;

    // If degreesOfFreedom is non-zero during a minimize, this gives
    // the offset into the coordinate array that those degrees of
    // freedom are represented at.
    int coordinateIndex;
    
    double data;
    double data2;
    struct xyz xdata;
    
    enum jigtype type;
    union {
	struct {
	    double temperature;
	} thermostat;
	
	struct {
	    double stall; // zero speed torque in pN-pm
	    double speed; // zero torque speed in radians per second
            double minimizeTorque; // torque in nN-nm
            double dampingCoefficient; // on springs between atoms and flywheel
	    
	    // A point on the motor axis
	    struct xyz center;
	    
	    // Vector along motor axis (from center)
	    struct xyz axis;

	    // Position of each anchor relative to the motor.  u is
	    // the location along the motor axis that each anchor
	    // rotates around.  v and w are orthogonal to each other,
	    // and to the motor axis.  Anchor position is:
            //   center + u + v cos(theta) + w sin(theta)
	    struct xyz *u, *v, *w;
	    
	    // Around axis.
	    double momentOfInertia; // formerly moment

            // variables below here are updated by the jig code.
            
	    // How far the motor has turned in radians.
	    double theta;

            // current angular speed in radians per second.
	    double omega;
	    
	    // For each atom in motor, the previous displacement of the atom
	    // from its rotating anchor, used for damping oscillations
	    struct xyz *rPrevious;
	    
	    // A boolean to tell whether or not damping is switched on.
	    int damping_enabled;
	} rmotor;
	
	struct {
	    double force; // formerly stall, in pN
	    double stiffness; // formerly speed, in N/m
	    struct xyz constantForce; // force to apply to each atom if stiffness is zero
	    struct xyz axis; // all atoms constrained to move along this axis
	    
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
    double A; // aJ/rad^2
};

struct cumuleneTorsion
{
    struct atom *a1;
    struct atom *aa;
    struct atom *ab;
    struct atom *ay;
    struct atom *az;
    struct atom *a2;
    //params;
    int numberOfDoubleBonds;
    double A; // aJ/rad^2
};

struct outOfPlane
{
    struct atom *ac;
    struct atom *a1;
    struct atom *a2;
    struct atom *a3;
    //params;
    double A; // aJ/pm^2
};


struct part 
{
    // Where this part was loaded from
    char *filename;
    
    // Function to call to signal an error while loading
    int (*parseError)(void *);
    
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
    
    int num_atoms;
    struct atom **atoms;
    
    int num_bonds;
    struct bond **bonds;
    
    int num_jigs;
    struct jig **jigs;

    int num_rigidBodies;
    struct rigidBody *rigidBodies;

    int num_joints;
    struct joint *joints;

    // pointer to a data structure that holds data which is specific
    // to the particular rigid body library in use.  rigid.c selects
    // the library to use and calls into rigid-*.c as appropriate.
    void *rigid_body_info;
    
    int num_vanDerWaals;
    int num_static_vanDerWaals;
    int start_vanDerWaals_free_scan;
    struct vanDerWaals **vanDerWaals;
    void *vanDerWaals_validity;

    // The largest vdW radius of any atom actually present in the
    // part, in pm.
    double maxVanDerWaalsRadius;

    // Absolute value of the greatest charge on any particle in the
    // part in multiples of the proton charge.
    double maxParticleCharge;
    
    int num_stretches;
    struct stretch *stretches;
    
    int num_bends;
    struct bend *bends;
    
    int num_torsions;
    struct torsion *torsions;
    
    int num_cumuleneTorsions;
    struct cumuleneTorsion *cumuleneTorsions;
    
    int num_outOfPlanes;
    struct outOfPlane *outOfPlanes;
    
    struct xyz *positions;
    struct xyz *velocities;
    
    struct atom *vdwHash[GRID_SIZE][GRID_SIZE][GRID_SIZE];
};

extern struct part *makePart(char *filename, int (*parseError)(void *), void *stream);

extern void destroyPart(struct part *p);

extern struct part *endPart(struct part *p);

extern void initializePart(struct part *p);

extern void generateStretches(struct part *p);

extern void generateBends(struct part *p);

extern void generateTorsions(struct part *p);

extern void generateOutOfPlanes(struct part *p);

extern void updateVanDerWaals(struct part *p, void *validity, struct xyz *positions);

extern void setThermalVelocities(struct part *p, double temperature);

extern void makeAtom(struct part *p, int externalID, int elementType, struct xyz position);

extern void setAtomHybridization(struct part *p, int atomID, enum hybridization h);

extern void makeBond(struct part *p, int atomID1, int atomID2, char order);

extern void makeVanDerWaals(struct part *p, int atomID1, int atomID2);

extern double calculateKinetic(struct part *p);

extern void makeRigidBody(struct part *p, char *name, double mass, double *inertiaTensor, struct xyz position, struct quaternion orientation);

extern void makeStationPoint(struct part *p, char *bodyName, char *stationName, struct xyz position);

extern void makeBodyAxis(struct part *p, char *bodyName, char *axisName, struct xyz orientation);

extern void makeAtomAttachments(struct part *p, char *bodyName, int atomListLength, int *atomList);

extern void makeBallJoint(struct part *p, char *bodyName1, char *stationName1, char *bodyName2, char *stationName2);

extern void makeHingeJoint(struct part *p, char *bodyName1, char *stationName1, char *axisName1, char *bodyName2, char *stationName2, char *axisName2);

extern void makeSliderJoint(struct part *p, char *bodyName1, char *axisName1, char *bodyName2, char *axisName2);

extern void makeGround(struct part *p, char *name, int atomListLength, int *atomList);

extern void makeThermometer(struct part *p, char *name, int firstAtomID, int lastAtomID);

extern void makeDihedralMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3, int atomID4);

extern void makeAngleMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3);

extern void makeRadiusMeter(struct part *p, char *name, int atomID1, int atomID2);

extern void makeThermostat(struct part *p, char *name, double temperature, int firstAtomID, int lastAtomID);

extern struct jig * makeRotaryMotor(struct part *p, char *name, double stall, double speed, struct xyz *center, struct xyz *axis, int atomListLength, int *atomList);

extern void setInitialSpeed(struct jig *j, double initialSpeed);

extern void setDampingCoefficient(struct jig *j, double dampingCoefficient);

extern void setDampingEnabled(struct jig *j, int dampingEnabled);

extern void makeLinearMotor(struct part *p, char *name, double force, double stiffness, struct xyz *center, struct xyz *axis, int atomListLength, int *atomList);

extern void printXYZ(FILE *f, struct xyz p);

extern void printQuaternion(FILE *f, struct quaternion q);

extern void printInertiaTensor(FILE *f, double *t);

extern void printAtomShort(FILE *f, struct atom *a);

extern char printableBondOrder(struct bond *b);

extern char *hybridizationString(enum hybridization h);

extern void printAtom(FILE *f, struct part *p, struct atom *a);

extern void printBond(FILE *f, struct part *p, struct bond *b);

extern char *printableJigType(struct jig *j);

extern void printJig(FILE *f, struct part *p, struct jig *j);

extern void printJoint(FILE *f, struct part *p, struct joint *j);

extern void printRigidBody(FILE *f, struct part *p, struct rigidBody *rb);

extern void printVanDerWaals(FILE *f, struct part *p, struct vanDerWaals *v);

extern void printStretch(FILE *f, struct part *p, struct stretch *s);

extern void printBend(FILE *f, struct part *p, struct bend *b);

extern void printTorsion(FILE *f, struct part *p, struct torsion *t);

extern void printCumuleneTorsion(FILE *f, struct part *p, struct cumuleneTorsion *t);

extern void printOutOfPlane(FILE *f, struct part *p, struct outOfPlane *o);

extern void printPart(FILE *f, struct part *p);

extern void deallocate_part(struct part *p);

#endif

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
