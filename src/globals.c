#include "simulator.h"

// Everything in here has to be updated in 6 places:
//
// The top of this file, where the actual symbol is defined.
// The bottom of this file, where the initial value is set.
// In globals.h, where others pick up the definitions.
// The top of sim.pyx, where these symbols are linked to python code.
// In __getattr__ in sim.pyx, to let python get them.
// In __setattr__ in sim.pyx, to let python set them.
//
// Sure would be nice to do it all just once...
//
// That could be done if sim.pyx can have cpp macros in it...

static char const rcsid[] = "$Id$";

int debug_flags;

int Interrupted; /* set to 1 when a SIGTERM is received */

struct xyz Center, Bbox[2];

int Iteration;

char *CommandLine;

// definitions for command line args

int ToMinimize;
int IterPerFrame;
int NumFrames;
int DumpAsText;
int DumpIntermediateText;
int PrintFrameNums;
int OutputFormat;
int KeyRecordInterval;
int DirectEvaluate;
float ExcessiveEnergyLevel;
char *IDKey;
char *InputFileName;
char *OutputFileName;
char *TraceFileName;
char *BaseFileName;
int QualityWarningLevel;
float SimpleMovieForceScale;

FILE *OutputFile;
FILE *TraceFile;

int Count;

int ExcessiveEnergyWarning;
int ExcessiveEnergyWarningThisFrame;
int ComputedParameterWarning;
int InterruptionWarning;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
double Dt;              // seconds
double Dx;              // meters
double Dmass;           // units of mass vs. kg

double Temperature;	// Kelvins

const double Boltz = 1.3806503e-23;	/* k, in J/K */
const double Pi = 3.14159265358979323846;

double totClipped;  // internal thermostat for numerical stability

const double Gamma = 0.01; // for Langevin thermostats
//    double Gamma = 0.1;  // for Langevin thermostats

const double G1=(1.01-0.27*0.01)*1.4*0.1;
//    double G1=(1.01-0.27*0.1)*1.4*0.31623;
//    double G1=(1.01-0.27*Gamma)*1.4*sqrt(Gamma);

void
reinit_globals(void)
{
    debug_flags = 0;
    Interrupted = 0;
    Iteration = 0;
    CommandLine = NULL;
    ToMinimize = 0;
    IterPerFrame = 10;
    NumFrames = 100;
    DumpAsText = 0;
    DumpIntermediateText = 0;
    PrintFrameNums = 1;
    OutputFormat = 1;
    KeyRecordInterval = 32;
    DirectEvaluate = 0;
    ExcessiveEnergyLevel = 0.1; // attoJoules
    IDKey = "";
    InputFileName = NULL;
    OutputFileName = NULL;
    TraceFileName = NULL;
    BaseFileName = NULL;
    QualityWarningLevel = 5;
    SimpleMovieForceScale = 0.1;

    OutputFile = NULL;
    TraceFile = NULL;

    Count = 0;

    ExcessiveEnergyWarning = 0;
    ExcessiveEnergyWarningThisFrame = 0;
    ComputedParameterWarning = 0;
    InterruptionWarning = 0;

    Dt = 1e-16; // seconds
    Dx = 1e-12; // meters
    Dmass = 1e-27; // mass units in kg
    Temperature = 300.0; // Kelvins
    totClipped = 0.0;

    reInitializeBondTable();
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
