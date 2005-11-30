#include "simulator.h"

int debug_flags = 0;

int Interrupted = 0; /* set to 1 when a SIGTERM is received */

struct xyz Center, Bbox[2];

int Iteration=0;

// definitions for command line args

int ToMinimize=0;
int IterPerFrame=10;
int NumFrames=100;
int DumpAsText=0;
int DumpIntermediateText=0;
int PrintFrameNums=1;
int OutputFormat=1;
int KeyRecordInterval=32;
int DirectEvaluate=1; // XXX should default to 0 eventually
char *IDKey="";

char OutFileName[1024];
char TraceFileName[1024];

char *baseFilename;

// for writing the differential position and trace files
FILE *outf, *tracef;

int Count = 0;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
double Dt = 1e-16;              // seconds
double Dx = 1e-12;              // meters
double Dmass = 1e-27;           // units of mass vs. kg

double Temperature = 300.0;	/* Kelvins */
double Boltz = 1.38e-23;	/* k, in J/K */
double Pi = 3.1415926;

double totClipped=0.0;  // internal thermostat for numerical stability

double Gamma = 0.01; // for Langevin thermostats
//double Gamma = 0.1; // for Langevin thermostats
// double G1=(1.01-0.27*Gamma)*1.4*sqrt(Gamma);

double G1=(1.01-0.27*0.01)*1.4*0.1;
//double G1=(1.01-0.27*0.1)*1.4*0.31623;
