#include "simulator.h"

static void
defineAMBERAtomType(char *name,
                    char *type,
                    char *mass,
                    char *charge,
                    char *ptype,
                    char *sigma,
                    char *epsilon)
{
  printf("defineAMBERAtomType(%s %s %s %s %s %s %s)\n",
         name, type, mass, charge, ptype, sigma, epsilon);
}

static void
defineAMBERBondType(char *atom_i,
                    char *atom_j,
                    char *rest)
{
  printf("defineAMBERBondType(%s %s %s)\n",
         atom_i, atom_j, rest);
}

static void
defineAMBERAngleType(char *atom_i,
                     char *atom_j,
                     char *atom_k,
                     char *rest)
{
  printf("defineAMBERAngleType(%s %s %s %s)\n",
         atom_i, atom_j, atom_k, rest);
}

static void
defineAMBERImproperTorsion(char *atom_i,
                           char *atom_j,
                           char *atom_k,
                           char *atom_l,
                           char *func,
                           char *rest)
{
  printf("defineAMBERImproperTorsion(%s %s %s %s %s %s)\n",
         atom_i, atom_j, atom_k, atom_l, func, rest);
}

static void
defineAMBERProperTorsion(char *atom_i,
                         char *atom_j,
                         char *atom_k,
                         char *atom_l,
                         char *func,
                         char *rest)
{
  printf("defineAMBERProperTorsion(%s %s %s %s %s %s)\n",
         atom_i, atom_j, atom_k, atom_l, func, rest);
}

enum sectionType {
  atomtypes,
  bondtypes,
  angletypes,
  dihedraltypes,
};

int
read_amber_itp_file(char *filename)
{
  FILE *f;
  char buf[4096];
  char error[128];
  int lineNumber = 0;
  char *s;
  int i;
  char *token;
  char *sectionName;
  enum sectionType section;
  char *name;
  char *type;
  char *mass;
  char *charge;
  char *ptype;
  char *sigma;
  char *epsilon;
  char *atom_i;
  char *atom_j;
  char *atom_k;
  char *atom_l;
  char *func;
  char *rest;
  
  f = fopen(filename, "r");
  if (f == NULL) {
    snprintf(error, 128, "AMBER itp file not found: %s", filename);
    RAISER(error, 1);
  }
  write_traceline("# reading parameter file: %s\n", filename);
  while (fgets(buf, 4096, f)) {
    lineNumber++;
    s = index(buf, ';');
    if (s != NULL) {
      *s = '\0';
    }
    s = index(buf, '#');
    if (s != NULL) {
      *s = '\0';
    }
    i = strlen(buf) - 1 ;
    while (i >= 0 && (buf[i] == ' ' || buf[i] == '\t' || buf[i] == '\n' || buf[i] == '\r')) {
      i--;
    }
    buf[i+1] = '\0';
    token = strtok(buf, " ");
    if (token) {
      if (!strcmp(token, "[") ) {
        sectionName = strtok(NULL, " ");
        if (!strcmp(sectionName, "atomtypes")) {
          section = atomtypes;
        } else if (!strcmp(sectionName, "bondtypes")) {
          section = bondtypes;
        } else if (!strcmp(sectionName, "angletypes")) {
          section = angletypes;
        } else if (!strcmp(sectionName, "dihedraltypes")) {
          section = dihedraltypes;
        } else {
          snprintf(error, 128, "undefined section [ %s ] in %s", sectionName, filename);
          fclose(f);
          RAISER(error, 1);
        }
      } else {
        switch (section) {
        case atomtypes:
          name = token;
          type = strtok(NULL, " ");
          mass = strtok(NULL, " ");
          charge = strtok(NULL, " ");
          ptype = strtok(NULL, " ");
          sigma = strtok(NULL, " ");
          epsilon = strtok(NULL, " ");
          if (epsilon == NULL) {
            snprintf(error, 128, "not enough fields at line %d of %s", lineNumber, filename);
            fclose(f);
            RAISER(error, 1);
          }
          defineAMBERAtomType(name, type, mass, charge, ptype, sigma, epsilon);
          break;
        case bondtypes:
          atom_i = token;
          atom_j = strtok(NULL, " ");
          rest = strtok(NULL, "");
          if (rest == NULL) {
            snprintf(error, 128, "not enough fields at line %d of %s", lineNumber, filename);
            fclose(f);
            RAISER(error, 1);
          }
          defineAMBERBondType(atom_i, atom_j, rest);
          break;
        case angletypes:
          atom_i = token;
          atom_j = strtok(NULL, " ");
          atom_k = strtok(NULL, " ");
          rest = strtok(NULL, "");
          if (rest == NULL) {
            snprintf(error, 128, "not enough fields at line %d of %s", lineNumber, filename);
            fclose(f);
            RAISER(error, 1);
          }
          defineAMBERAngleType(atom_i, atom_j, atom_k, rest);
          break;
        case dihedraltypes:
          atom_i = token;
          atom_j = strtok(NULL, " ");
          atom_k = strtok(NULL, " ");
          atom_l = strtok(NULL, " ");
          func = strtok(NULL, " ");
          rest = strtok(NULL, "");
          if (rest == NULL) {
            snprintf(error, 128, "not enough fields at line %d of %s", lineNumber, filename);
            fclose(f);
            RAISER(error, 1);
          }
          if (!strcmp(func, "1")) {
            defineAMBERImproperTorsion(atom_i, atom_j, atom_k, atom_l, func, rest);
          } else if (!strcmp(func, "3")) {
            defineAMBERProperTorsion(atom_i, atom_j, atom_k, atom_l, func, rest);
          } else {
            snprintf(error, 128, "unknown torsion function at line %d of %s", lineNumber, filename);
            fclose(f);
            RAISER(error, 1);
          }
          break;
        }
      }
    }
  }
  fclose(f);
  return 0;
}
