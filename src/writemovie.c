/*
 * Copyright (c) 2004-2006 Nanorex, Inc. All Rights Reserved.
 */

#include "simulator.h"

#if defined(__GNUC__) || defined(__MWERKS__)
// GCC and kin
typedef long long int_64;
#else        // #elif defined(WIN32) ???
// Microsoft
typedef __int64 int_64;
#endif

// arrays of 3 times part->num_atoms
static int *ixyz = NULL;
static int *previxyz = NULL;

static int flushWriteWarning = 0;

static void flushOutputFile(FILE *f)
{
    if (fflush(f) < 0 && !flushWriteWarning) {
        /* it's a good bet that this will fail too, but we'll try... */
        WARNING_ERRNO1("Unable to write to file %s", OutFileName);
        flushWriteWarning = 1;
    }
}

void initializeDeltaBuffers(struct part *part)
{
    int i;
    int j;
    struct xyz *pos = part->positions;
    
    if (ixyz != NULL) {
        free(ixyz);
    }
    ixyz=(int *)allocate(sizeof(int) * 3 * part->num_atoms);
    if (previxyz != NULL) {
        free(previxyz);
    }
    previxyz=(int *)allocate(sizeof(int) * 3 * part->num_atoms);
    for (i=0, j=0; i<3*part->num_atoms; i+=3, j++) {
        previxyz[i+0] = (int)pos[j].x;
        previxyz[i+1] = (int)pos[j].y;
        previxyz[i+2] = (int)pos[j].z;
    }
}

static void writeXYZOutputHeader(FILE *f, struct part *part)
{
}

// .xyz files are in angstroms (1e-10 m)
#define XYZ (1.0e-2)

static void writeXYZFrame(FILE *f, struct part *part, struct xyz *pos)
{
    int i;
    
    for (i=0; i<part->num_atoms; i++) {
        fprintf(f, "%s %f %f %f\n", part->atoms[i]->type->symbol,
                pos[i].x*XYZ, pos[i].y*XYZ, pos[i].z*XYZ);
    }
}

static void writeXYZOutputTrailer(FILE *f, struct part *part, int frameNumber)
{
}

static void writeOldOutputHeader(FILE *f, struct part *part)
{
	fwrite(&NumFrames, sizeof(int), 1, f);
}

static void writeOldFrame(FILE *f, struct part *part, struct xyz *pos)
{
    int i;
    int j;
    int *tmp;
    char c0, c1, c2;
    
    for (i=0, j=0; i<3*part->num_atoms; i+=3, j++) {
        ixyz[i+0] = (int)pos[j].x;
        ixyz[i+1] = (int)pos[j].y;
        ixyz[i+2] = (int)pos[j].z;

        c0=(char)(ixyz[i+0] - previxyz[i+0]);
        fwrite(&c0, sizeof(char), 1, f);

        c1=(char)(ixyz[i+1] - previxyz[i+1]);
        fwrite(&c1, sizeof(char), 1, f);

        c2=(char)(ixyz[i+2] - previxyz[i+2]);
        fwrite(&c2, sizeof(char), 1, f);

        //fprintf(stderr, "%d %d %d\n", (int)c0, (int)c1, (int)c2);

    }

    tmp = previxyz;
    previxyz = ixyz;
    ixyz = tmp;
}

static void writeOldOutputTrailer(FILE *f, struct part *part, int frameNumber)
{
    if (frameNumber != NumFrames) {
        rewind(f);
        fwrite(&frameNumber, sizeof(int), 1, f);
    }
}

#define DPB_SYNC_WORD          0xffffffff
#define DPB_BYTE_ORDER_MAGIC   0x01020304
#define DPB_DELTA_RECORD_MAGIC 0x44656c01
#define DPB_DELTA_RECORD_TYPE  0x44656c02
#define DPB_KEY_RECORD_MAGIC   0x4b657901
#define DPB_KEY_RECORD_TYPE    0x4b657902
#define DPB_INDEX_RECORD_MAGIC 0x496e6401
#define DPB_INDEX_RECORD_TYPE  0x496e6402
#define DPB_END_RECORD_MAGIC   0x456f6601
#define DPB_END_RECORD_TYPE    0x456f6602

struct dpb_record_header 
{
    int byte_order;
    int record_type;
    int record_length;
};

static int frame_number;
static int deltaRecordsBeforeNextKeyRecord;

static int_64 offsetToFirstRecord;
static int_64 offsetToIndexRecord;

static void writeNewKeyRecord(FILE *f, struct part *part);

static void writeNewOutputHeader(FILE *f, struct part *part)
{
    int sync_word = DPB_SYNC_WORD;

    frame_number = 0;
    
    fprintf(f, "#!/usr/local/bin/nanoENGINEER1-viewer\n");
    fprintf(f, "#@ nanoENGINEER-1 atom trajectory file, format version 050404\n");
    fprintf(f, "# molecular dynamics movie file produced by nanoENGINEER-1\n");
    fprintf(f, "# see http://www.nanoENGINEER-1.com\n");
    //fprintf(f, "# generated by simulator version 0.94");

    if (IDKey != NULL && IDKey[0] != '\0') {
        fprintf(f, "IDKey = %s\n", IDKey);
    }
    fprintf(f, "NumberOfAtoms = %d\n", part->num_atoms);
    fprintf(f, "ExpectedFrames = %d\n", NumFrames);
    fprintf(f, "KeyRecordInterval = %d\n", KeyRecordInterval);
    //fprintf(f, "Command = %s\n", "do we need this?");
    fprintf(f, "SpaceResolution = %e\n", 1e-10); // or is it Dx?
    fprintf(f, "FrameTimeInterval = %e\n", IterPerFrame * Dt);

    fprintf(f, "# pad to 4 byte boundary:.");
    while ((ftell(f)+1L) % 4L != 0) {
        fprintf(f, ".");
    }
    fprintf(f, "\n");
    fwrite(&sync_word, 4, 1, f);
    offsetToFirstRecord = (int_64)ftell(f);
    writeNewKeyRecord(f, part);
}

struct indexEntry 
{
    int record_type;
    int frame_number;
    int offset_high;
    int offset_low;
};

static struct indexEntry *frameIndex = NULL;
static int indexBufferLength = 0;
static int indexRecordCount = 0;

static void buildIndex(FILE *f, int recordType)
{
    int_64 offset;
    
    if (indexRecordCount >= indexBufferLength) {
        if (indexBufferLength == 0) {
            indexBufferLength = NumFrames + NumFrames / KeyRecordInterval + 20;
        } else {
            indexBufferLength *= 2;
        }
        frameIndex = realloc(frameIndex, indexBufferLength * sizeof(struct indexEntry));
        if (frameIndex == NULL) {
            ERROR("out of memory");
        }
    }
    frameIndex[indexRecordCount].record_type = recordType;
    frameIndex[indexRecordCount].frame_number = frame_number;
    offset = (int_64)ftell(f);
    frameIndex[indexRecordCount].offset_high = (offset >> 32) & 0xffffffff;
    frameIndex[indexRecordCount].offset_low = offset & 0xffffffff;
    indexRecordCount++;
}

static void writeNewIndex(FILE *f)
{
    struct dpb_record_header hdr;

    // this puts the index record in the index, optional...
    buildIndex(f, DPB_INDEX_RECORD_TYPE);

    offsetToIndexRecord = (int_64)ftell(f);
    
    hdr.byte_order = DPB_BYTE_ORDER_MAGIC;
    hdr.record_type = DPB_INDEX_RECORD_MAGIC;
    hdr.record_length = 8 + (indexRecordCount * sizeof(struct indexEntry));
    fwrite(&hdr, sizeof(struct dpb_record_header), 1, f);
    fwrite(&frame_number, 4, 1, f);
    fwrite(&indexRecordCount, 4, 1, f);
    fwrite(frameIndex, sizeof(struct indexEntry), indexRecordCount, f);
}

static void writeNewKeyRecord(FILE *f, struct part *part)
{
    struct dpb_record_header hdr;

    buildIndex(f, DPB_KEY_RECORD_TYPE);
    
    hdr.byte_order = DPB_BYTE_ORDER_MAGIC;
    hdr.record_type = DPB_KEY_RECORD_MAGIC;
    hdr.record_length = 4 + (part->num_atoms * 12);
    fwrite(&hdr, sizeof(struct dpb_record_header), 1, f);
    fwrite(&frame_number, 4, 1, f);
    fwrite(previxyz, 4, 3*part->num_atoms, f);
    deltaRecordsBeforeNextKeyRecord = KeyRecordInterval;
}

static void writeNewDeltaRecord(FILE *f, struct part *part)
{
    int i;
    struct dpb_record_header hdr;
    int pad = 0;
    int delta;
    char c;
    
    buildIndex(f, DPB_DELTA_RECORD_TYPE);

    hdr.byte_order = DPB_BYTE_ORDER_MAGIC;
    hdr.record_type = DPB_DELTA_RECORD_MAGIC;
    hdr.record_length = 4 + (part->num_atoms * 3);
    while (hdr.record_length % 4 != 0) {
        pad++;
        hdr.record_length++;
    }
    
    fwrite(&hdr, sizeof(struct dpb_record_header), 1, f);
    fwrite(&frame_number, 4, 1, f);
    for (i=0; i<(part->num_atoms*3); i++) {
        delta = ixyz[i] - previxyz[i];
        if (delta < -128) {
            delta = -128;
        }
        if (delta > 127) {
            delta = 127;
        }
        c = (char)delta;
        fwrite(&c, 1, 1, f);
    }
    c = '\0';
    while (pad-- > 0) {
        fwrite(&c, 1, 1, f);
    }
}

static void writeNewFrame(FILE *f, struct part *part, struct xyz *pos)
{
    int i;
    int j;
    int *tmp;
    
    for (i=0, j=0; i<3*part->num_atoms; i+=3, j++) {
        ixyz[i+0] = (int)pos[j].x;
        ixyz[i+1] = (int)pos[j].y;
        ixyz[i+2] = (int)pos[j].z;
    }
    if (KeyRecordInterval > 1) {
        writeNewDeltaRecord(f, part);
    }
    
    tmp = previxyz;
    previxyz = ixyz;
    ixyz = tmp;

    if (deltaRecordsBeforeNextKeyRecord-- < 0) {
        writeNewKeyRecord(f, part);
    }
    flushOutputFile(f);
    frame_number++;
}

static void writeNewEndRecord(FILE *f)
{
    struct dpb_record_header hdr;
    int_64 offset;
    int_64 offsetToEndOfFile;
    int high, low;

    offsetToEndOfFile = (int_64)(ftell(f) + 28L);
    
    hdr.byte_order = DPB_BYTE_ORDER_MAGIC;
    hdr.record_type = DPB_END_RECORD_MAGIC;
    hdr.record_length = 16;
    fwrite(&hdr, sizeof(struct dpb_record_header), 1, f);

    offset = offsetToFirstRecord - offsetToEndOfFile;
    high = (offset >> 32) & 0xffffffff;
    low = offset & 0xffffffff;
    fwrite(&high, 4, 1, f);
    fwrite(&low, 4, 1, f);

    offset = offsetToIndexRecord - offsetToEndOfFile;
    high = (offset >> 32) & 0xffffffff;
    low = offset & 0xffffffff;
    fwrite(&high, 4, 1, f);
    fwrite(&low, 4, 1, f);
    flushOutputFile(f);
}

static void writeNewOutputTrailer(FILE *f, struct part *part, int frameNumber)
{
    if (deltaRecordsBeforeNextKeyRecord != KeyRecordInterval) {
        frameNumber--;
        writeNewKeyRecord(f, part);
        frameNumber++;
    }
    writeNewIndex(f);
    writeNewEndRecord(f);
}


void writeOutputHeader(FILE *f, struct part *part)
{
    if (!DumpAsText) {
        initializeDeltaBuffers(part);
    }
    switch (OutputFormat) {
    case 0:
        writeXYZOutputHeader(f, part);
        break;
    case 1:
        writeOldOutputHeader(f, part);
        break;
    case 2:
        writeNewOutputHeader(f, part);
        break;
    default:
        ERROR1("Invalid OutputFormat: %d", OutputFormat);
    }
}

void writeOutputTrailer(FILE *f, struct part *part, int frameNumber)
{
    switch (OutputFormat) {
    case 0:
        writeXYZOutputTrailer(f, part, frameNumber);
        break;
    case 1:
        writeOldOutputTrailer(f, part, frameNumber);
        break;
    case 2:
        writeNewOutputTrailer(f, part, frameNumber);
        break;
    default:
        ERROR1("Invalid OutputFormat: %d", OutputFormat);
    }
}

static float atomColors[10][3] = {
    { 1.0, 0.0, 0.0 }, // X  red
    { 0.0, 1.0, 1.0 }, // H  cyan  
    { 1.0, 1.0, 1.0 }, // He white
    { 1.0, 1.0, 1.0 }, // Li white
    { 1.0, 1.0, 1.0 }, // Be white
    { 1.0, 1.0, 1.0 }, // B  white
    { 0.0, 1.0, 0.0 }, // C  green
    { 1.0, 0.0, 1.0 }, // N  magenta
    { 0.5, 0.0, 0.0 }, // O  red
    { 1.0, 1.0, 1.0 }, // white
};

#define RADIUS_SCALE 5
void
writeSimpleAtomPosition(struct part *part, struct xyz *positions, int i)
{
  struct atom *a = part->atoms[i];
  double vdwr = a->type->vanDerWaalsRadius;
  int protons = a->type->protons;

  if (protons > 9) {
    protons = 9; // don't overrun the atomColors table above
  }
  
  // sphere x y z radius r g b
  fprintf(outf, "s %f %f %f %f %f %f %f\n",
          positions[i].x,
          positions[i].y,
          positions[i].z,
          vdwr * RADIUS_SCALE,
          atomColors[protons][0],
          atomColors[protons][1],
          atomColors[protons][2]
          );
}

static float forceColors[7][3] = {
    { 1.0, 1.0, 1.0 }, // white
    { 1.0, 0.0, 0.0 }, // red
    { 0.0, 1.0, 0.0 }, // green
    { 0.0, 0.0, 1.0 }, // blue
    { 0.0, 1.0, 1.0 }, // cyan
    { 1.0, 0.0, 1.0 }, // magenta
    { 1.0, 1.0, 0.0 }  // yellow
};

#define FORCE_SCALE 0.1
void
writeSimpleForceVector(struct xyz *positions, int i, struct xyz *force, int color, double scale)
{
    double fSquared;
    struct xyz f;
    
    if (1 /*!atom[i].inJig*/) {
        fprintf(outf, "l %f %f %f %f %f %f %f %f %f\n",
                positions[i].x,
                positions[i].y,
                positions[i].z,
                positions[i].x + (force->x * scale * FORCE_SCALE),
                positions[i].y + (force->y * scale * FORCE_SCALE),
                positions[i].z + (force->z * scale * FORCE_SCALE),
                forceColors[color][0],
                forceColors[color][1],
                forceColors[color][2]);
        if (color != 0) {
            f = *force;
            fSquared = vdot(f, f);
            fprintf(stderr, "force: %f type: %d\n", sqrt(fSquared), color);
        }
    }
}

void
writeSimpleStressVector(struct xyz *positions, int a1, int a2, int ac, double stress, double min, double max)
{
  float r;
  float b;
  float intensity;
  int sign = stress < 0.0;
#define MIN_INTENSITY 0.2

  intensity = (fabs(stress) - min) / (max - min);
  if (intensity < 0) {
    return;
  }
  intensity = MIN_INTENSITY + intensity / (1.0 - MIN_INTENSITY);
  if (intensity > 1.0) {
    intensity = 1.0;
  }
  if (sign) {
    r = intensity;
    b = 0.0;
  } else {
    r = 0.0;
    b = intensity;
  }
  fprintf(outf, "l %f %f %f %f %f %f %f %f %f\n",
          positions[a1].x,
          positions[a1].y,
          positions[a1].z,
          positions[a2].x,
          positions[a2].y,
          positions[a2].z,
          r, 0.0, b);
  if (ac >= 0) {
    fprintf(outf, "l %f %f %f %f %f %f %f %f %f\n",
            positions[ac].x,
            positions[ac].y,
            positions[ac].z,
            (positions[a1].x + positions[a2].x) / 2.0,
            (positions[a1].y + positions[a2].y) / 2.0,
            (positions[a1].z + positions[a2].z) / 2.0,
            r, 0.0, b);
  }
}

void
writeSimpleMovieFrame(struct part *part, struct xyz *positions, struct xyz *forces, const char *format, ...)
{
    int i;
    va_list args;
    
    for (i=0; i<part->num_atoms; i++) {
        writeSimpleAtomPosition(part, positions, i);
        if (forces != NULL) {
          writeSimpleForceVector(positions, i, &forces[i], 0, 1.0);
        }
    }
    fprintf(outf, "f ");
    va_start(args, format);
    vfprintf(outf, format, args);
    va_end(args);
    fprintf(outf, "\n");
    fflush(outf);
}

/**
 */
void writeDynamicsMovieFrame(FILE *outf, int n, struct part *part, struct xyz *pos)
{
    callback_writeFrame(part, pos);  // wware 060101  callback for pyrex
    if (outf != NULL) {
	switch (OutputFormat) {
	case 0:
	    fprintf(outf, "%d\nFrame %d, Iteration: %d\n", part->num_atoms, n, Iteration);
	    writeXYZFrame(outf, part, pos);
	    break;
	case 1:
	    writeOldFrame(outf, part, pos);
	    break;
	case 2:
	    writeNewFrame(outf, part, pos);
	    break;
	}
	traceJigData(tracef, part);
	flushOutputFile(outf);
    }
    // fprintf(stderr, "found Ke = %e\n",FoundKE);
}

static int interruptionWarning = 0;

/**
 */
int writeMinimizeMovieFrame(FILE *outf,
                            struct part *part,
                            int final,
                            struct xyz *pos,
                            double rms,
                            double max_force,
                            int frameNumber,
                            char *callLocation,
                            char *message)
{
    callback_writeFrame(part, pos);  // wware 060101  callback for pyrex
    switch (OutputFormat) {
    case 0:
        if (final || DumpIntermediateText) {
	    fprintf(outf, "%d\nRMS=%f\n", part->num_atoms, rms);
            writeXYZFrame(outf, part, pos);
        }
        break;
    case 1:
        if (frameNumber < NumFrames) {
          writeOldFrame(outf, part, pos);
        }
        break;
    case 2:
        writeNewFrame(outf, part, pos);
        break;
    }
    flushOutputFile(outf);

    if (message == NULL) {
      message = "";
    }
    // wware 060102  callback for trace file
    write_traceline("%4d %20f %20f %s %s\n", frameNumber, rms, max_force, callLocation, message);
    DPRINT5(D_MINIMIZE, "%4d %20e %20e %s %s\n", frameNumber, rms, max_force, callLocation, message);
    if (message[0] != '\0') {
      message[0] = '\0';
    }
    if (final) {
        writeOutputTrailer(outf, part, frameNumber);
    }
    if (Interrupted && !interruptionWarning) {
        WARNING("minimizer run was interrupted");
        interruptionWarning = 1;
    }
    return interruptionWarning;
}
