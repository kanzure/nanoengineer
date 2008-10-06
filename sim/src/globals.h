// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef GLOBALS_H_INCLUDED
#define GLOBALS_H_INCLUDED

#define RCSID_GLOBALS_H  "$Id$"

extern int debug_flags;

extern int Interrupted;

extern struct xyz Center;
extern struct xyz Bbox[2];

extern int Iteration;

extern char *CommandLine;

// definitions for command line args

extern int ToMinimize;
extern int IterPerFrame;
extern int NumFrames;
extern int DumpAsText;
extern int DumpIntermediateText;
extern int PrintFrameNums;
extern int OutputFormat;
extern int KeyRecordInterval;
extern int DirectEvaluate;
extern int QuadraticStretchPotential;
extern int PrintPotentialEnergy;
extern float ExcessiveEnergyLevel;
extern char *IDKey;
extern char *InputFileName;
extern char *OutputFileName;
extern char *TraceFileName;
extern char *BaseFileName;
extern char *GromacsOutputBaseName;
extern char *PathToCpp;
extern char *SystemParametersFileName;
extern char *AmberBondedParametersFileName;
extern char *AmberNonbondedParametersFileName;
extern char *AmberChargesFileName;
extern int QualityWarningLevel;
extern float SimpleMovieForceScale;
extern double MinimizeThresholdCutoverRMS;
extern double MinimizeThresholdCutoverMax;
extern double MinimizeThresholdEndRMS;
extern double MinimizeThresholdEndMax;
extern double VanDerWaalsCutoffRadius;
extern double VanDerWaalsCutoffFactor;
extern int EnableElectrostatic;
extern int NeighborSearching;
extern int TimeReversal;
extern double ThermostatGamma;
extern double ThermostatG1;
extern int UseAMBER;
extern int TypeFeedback;

extern int LoadedSystemParameters;
extern char *UserParametersFileName;
extern int LoadedUserParameters;

extern FILE *OutputFile;
extern FILE *TraceFile;

extern int Count;

// have we warned the user about too much energy in a dynamics run?
// Each warning location warns only if ExcessiveEnergyWarning is zero.
// If it warns, it increments ExcessiveEnergyWarningThisFrame.  After
// each dynamics frame, ExcessiveEnergyWarning is set if
// ExcessiveEnergyWarningThisFrame is non-zero.
extern int ExcessiveEnergyWarning;
extern int ExcessiveEnergyWarningThisFrame;

// have we warned the user about using a generic/guessed force field parameter?
extern int ComputedParameterWarning;

extern int InterruptionWarning;

extern int _last_iteration;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
extern double Dt;
extern double Dx;
extern double Dmass;           // units of mass vs. kg
extern double Temperature;	/* Kelvins */
extern const double Boltz;	/* k, in J/K */
extern const double Pi;
extern const double COULOMB;   // aJ pm e^-2
extern const double MinElectrostaticSensitivity; // aJ
extern const double DielectricConstant; // unitless

extern double totClipped;  // internal thermostat for numerical stability

extern void reinit_globals(void);

extern void constrainGlobals(void);

extern void printGlobals(void);

#endif  /* GLOBALS_H_INCLUDED */
