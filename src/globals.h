#ifndef GLOBALS_H_INCLUDED
#define GLOBALS_H_INCLUDED

typedef struct sim_context {
    int ToMinimize;
} sim_context;

extern int debug_flags;

extern int Interrupted;

extern struct xyz Center;
extern struct xyz Bbox[2];

extern int Iteration;

// definitions for command line args

extern int IterPerFrame;
extern int NumFrames;
extern int DumpAsText;
extern int DumpIntermediateText;
extern int PrintFrameNums;
extern int OutputFormat;
extern int KeyRecordInterval;
extern int DirectEvaluate;
extern char *IDKey;

extern char OutFileName[1024];
extern char TraceFileName[1024];
extern char *baseFilename;

// for writing the differential position and trace files
extern FILE *outf;
extern FILE *tracef;

extern int Count;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
extern double Dt;
const extern double Dx;
const extern double Dmass;           // units of mass vs. kg
extern double Temperature;	/* Kelvins */
const extern double Boltz;	/* k, in J/K */
const extern double Pi;

extern double totClipped;  // internal thermostat for numerical stability

const extern double Gamma; // for Langevin thermostats

const extern double G1;

#endif
