
bool addAtomType(char* namei,  int unused, float radius, float radiusC,
                        int r, int g, int b);

int getAtomColor(const char* atomicElement);
float getAtomRadius(const char* atomicElement);
float getAtomCovalentRadius(const char* atomicElement);

int getChainColor(int chianIndex);

#define MAX_COVALENT_RADIUS 1.688f

                         
bool readArtFile(const char* filename);                                  
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
