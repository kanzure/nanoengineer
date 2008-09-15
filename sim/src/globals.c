// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
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
int QuadraticStretchPotential;
int PrintPotentialEnergy;
float ExcessiveEnergyLevel;
char *IDKey;
char *InputFileName;
char *OutputFileName;
char *TraceFileName;
char *BaseFileName;
char *GromacsOutputBaseName;
char *PathToCpp;
char *SystemParametersFileName;
int QualityWarningLevel;
float SimpleMovieForceScale;
double MinimizeThresholdCutoverRMS;
double MinimizeThresholdCutoverMax;
double MinimizeThresholdEndRMS;
double MinimizeThresholdEndMax;
int TimeReversal;
double ThermostatGamma;
double ThermostatG1;
int UseAMBER;
int TypeFeedback;

// absolute distance in nm beyond which gromacs will consider vdW
// forces to be exactly zero.  If less than zero, user defined tables
// will not be used, and a default value of 1.0 nm will be used.
double VanDerWaalsCutoffRadius;

// multiple of rvdW where interpolation table ends, and van der Waals
// force is considered exactly zero beyond this point.
double VanDerWaalsCutoffFactor;

int EnableElectrostatic;
int NeighborSearching;

// these are not reset by reinit_globals, but rather in
// readBondTableOverlay.
int LoadedSystemParameters;
char *UserParametersFileName;
int LoadedUserParameters;

FILE *OutputFile;
FILE *TraceFile;

int Count;

int ExcessiveEnergyWarning;
int ExcessiveEnergyWarningThisFrame;
int ComputedParameterWarning;
int InterruptionWarning;

// set to one in dynamics when processing the last iteration within a
// frame.  For debugging, hence the leading _.  Doesn't need
// initialization here.
int _last_iteration;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
double Dt;              // seconds
double Dx;              // meters
double Dmass;           // units of mass vs. kg

double Temperature;	// Kelvins

const double Boltz = 1.3806503e-23;	/* k, in J/K */
const double Pi = 3.14159265358979323846;

// permittivity constant, epsilon_naught = 8.854187818 * 10^-12 F/m (Halliday&Resnick, third edition, 1978, p. A23)
// F/m is C/(V m) is A^2 s^4 kg^-1 m^-3
// elementary charge, e = 1.6021892 * 10^-19 C (H&R)
// C is A s

// mksCoulomb = 1/(4 pi epsilon_naught) in kg m^3 A^-2 s^-4
// mksCoulomb e^2 in kg m^3 e^-2 s^-2
// mksCoulomb e^2 10^12 in kg pm m^2 e^-2 s^-2 or J pm e^-2
// mksCoulomb e^2 10^12 10^18 in aJ pm e^-2
// COULOMB = 1e12 * 1e18 * 1.6021892e-19 * 1.6021892e-19 / (4 * Pi * 8.854187818e-12);

// Constant for electrostatic Coulomb force.  Multiply by the charge
// in elementary units, and divide by the separation in pm to get the
// potential in aJ

// aJ pm e^-2
const double COULOMB = 230.711374295;

const double MinElectrostaticSensitivity = 0.0015; // aJ

const double DielectricConstant = 160;

double totClipped;  // internal thermostat for numerical stability


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
    PrintFrameNums = 0;
    OutputFormat = 1;
    KeyRecordInterval = 32;
    DirectEvaluate = 0;
    QuadraticStretchPotential = 0;
    PrintPotentialEnergy = 0;
    ExcessiveEnergyLevel = 0.1; // attoJoules
    IDKey = "";
    InputFileName = NULL;
    OutputFileName = NULL;
    TraceFileName = NULL;
    BaseFileName = NULL;
    GromacsOutputBaseName = NULL;
    PathToCpp = NULL;
    SystemParametersFileName = NULL;
    QualityWarningLevel = 5;
    SimpleMovieForceScale = 1.0;
    TimeReversal = 0;
    ThermostatGamma = 0.01;
    UseAMBER = 0;
    TypeFeedback = 0;
    
    MinimizeThresholdCutoverRMS = 50.0; // pN
    MinimizeThresholdCutoverMax = 0.0; // set by constrainGlobals, below
    MinimizeThresholdEndRMS = 1.0;
    MinimizeThresholdEndMax = 0.0; // set by constrainGlobals, below

    VanDerWaalsCutoffRadius = -1.0; // use gromacs built in functions
    VanDerWaalsCutoffFactor = 1.7;

    EnableElectrostatic = 1;
    NeighborSearching = 1;
    
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

void
constrainGlobals()
{
    if (MinimizeThresholdEndRMS > MinimizeThresholdCutoverRMS) {
        MinimizeThresholdCutoverRMS = MinimizeThresholdEndRMS;
        MinimizeThresholdCutoverMax = MinimizeThresholdEndMax;
    }
    if (MinimizeThresholdCutoverMax < MinimizeThresholdCutoverRMS) {
        MinimizeThresholdCutoverMax = 5.0 * MinimizeThresholdCutoverRMS;
    }
    if (MinimizeThresholdEndMax < MinimizeThresholdEndRMS) {
        MinimizeThresholdEndMax = 5.0 * MinimizeThresholdEndRMS;
    }
    if (VanDerWaalsCutoffFactor < 1.2) {
        VanDerWaalsCutoffFactor = 1.2;
    }
    if (VanDerWaalsCutoffFactor > 10.0) {
        VanDerWaalsCutoffFactor = 10.0;
    }

    ThermostatG1 = (1.01 - 0.27 * ThermostatGamma) * 1.4 * sqrt(ThermostatGamma);
}

void
printGlobals()
{
    write_traceline("#\n");
    write_traceline("# debug_flags: 0x%x\n", debug_flags);
    write_traceline("# IterPerFrame: %d\n", IterPerFrame);
    write_traceline("# NumFrames: %d\n", NumFrames);
    write_traceline("# DumpAsText: %d\n", DumpAsText);
    write_traceline("# DumpIntermediateText: %d\n", DumpIntermediateText);
    write_traceline("# PrintFrameNums: %d\n", PrintFrameNums);
    write_traceline("# OutputFormat: %d\n", OutputFormat);
    write_traceline("# KeyRecordInterval: %d\n", KeyRecordInterval);
    write_traceline("# DirectEvaluate: %d\n", DirectEvaluate);
    write_traceline("# ExcessiveEnergyLevel: %f aJ\n", ExcessiveEnergyLevel);
    write_traceline("# QualityWarningLevel: %d\n", QualityWarningLevel);
    if (ToMinimize) {
        write_traceline("# MinimizeThresholdCutoverRMS: %f\n", MinimizeThresholdCutoverRMS);
        write_traceline("# MinimizeThresholdCutoverMax: %f\n", MinimizeThresholdCutoverMax);
        write_traceline("# MinimizeThresholdEndRMS: %f\n", MinimizeThresholdEndRMS);
        write_traceline("# MinimizeThresholdEndMax: %f\n", MinimizeThresholdEndMax);
    }
    write_traceline("# VanDerWaalsCutoffRadius: %f\n", VanDerWaalsCutoffRadius);
    write_traceline("# VanDerWaalsCutoffFactor: %f\n", VanDerWaalsCutoffFactor);
    write_traceline("# EnableElectrostatic: %d\n", EnableElectrostatic);
    write_traceline("# NeighborSearching: %d\n", NeighborSearching);
    write_traceline("# ThermostatGamma: %f\n", ThermostatGamma);
    write_traceline("# UseAMBER: %d\n", UseAMBER);
    if (SystemParametersFileName != NULL && LoadedSystemParameters) {
        write_traceline("# SystemParametersFileName: %s\n", SystemParametersFileName);
    }
    if (UserParametersFileName != NULL && LoadedUserParameters) {
        write_traceline("# UserParametersFileName: %s\n", UserParametersFileName);
    }
    if (GromacsOutputBaseName != NULL) {
        write_traceline("# GromacsOutputBaseName: %s\n", GromacsOutputBaseName);
    }
    write_traceline("#\n");
}


/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
