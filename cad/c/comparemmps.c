// Copyright 2004, 2007 Nanorex, Inc.  See LICENSE file for details.
//====================================================================//
/*	Program to compare two mmp files.
	
	Program Arguments: two mmp files.

	Details:
	
	Small differences in the atom positions in the mmp file are neglected
	The Tolerence value for the atom positions in |5|

	main() is in this file itself. This is an independent program

	 -Ninad Sathaye,
	  Nanorex Inc.
	  Date: August 12, 2004
 */
//===================================================================//
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

FILE *file1;
FILE *file2;
FILE *pOutFile;


# define PART 1
# define ATOM 2
# define BOND 3
# define GRND 4
# define MOTOR 5
# define LINMOT 6
# define SHAFT 7
# define BEARING 8
# define SHOW 9
# define END 10
# define OTHERS 11




int gSpaceAtom[]= { 2,3,2,2,0}; // This array is defining the 'empty spaces' between the two
								 // entries , in a line starting with 'atom' :-)

char * gStringArray[]= {"def", "nil", "lin", "cpk", "tub", "mix", "vdw"};//These are the valid codes
																	//after 'show' word in mmp file

int parse(char * psCnt)
{
	 if (0==strncmp(psCnt,"part",4))
		 return PART ;
	 else if (0==strncmp(psCnt,"atom",4))
		 return ATOM;
	 else if (0==strncmp(psCnt,"bond",4))
		return BOND;
	 else if (0==strncmp(psCnt,"ground",6))
		 return GRND;
	 else if (0==strncmp(psCnt,"motor",5))
		 return MOTOR;
	 else if (0==strncmp(psCnt,"linmotor",8))
		 return LINMOT;
	 else if (0==strncmp(psCnt,"shaft",5))
		 return SHAFT;
	 else if (0==strncmp(psCnt,"bearing",7))
		 return BEARING;
	 else if (0==strncmp(psCnt,"show",4))
		 return SHOW;
	 else if (0==strncmp(psCnt,"end",3))
		 return END;
	  else  return OTHERS;
	
}


void main (int argc, char *argv[])
{
	int i;
	int check1,check2; //required in case SHOW
//	int nExit;
	int ntemp=0; //this is temp.

	char filename1[100],filename2[100];
	char buf1[128],buf2[128];

	char *pBuf1= buf1;
	char *pBuf2=buf2;
	
	char *psTok1;//used as StiringTokens
	char *psTok2;

	
	long l1, l2;
	
	char *pFile1;
	char *pFile2;

	pOutFile=fopen ("mmpsCompared.txt","w");
	fprintf(pOutFile,"***\tProgram for comparing two mmp files\t***\n\n");
	fprintf(pOutFile,"Small differences in atom positions are ignored (Tolerence=5)\n");
	fprintf(pOutFile,"Differences in theh 'show' mode are ignored but still check for valid codes such as lin, vdw etc.:\n\n");
	fprintf(pOutFile,"Input mmp files are as follows:\n");
	fprintf(pOutFile,"File1: %s\t File2: %s\n\n\n",argv[1],argv[2]);


	if(argc==3)
	{
		strcpy(filename1, argv[1]);
		strcpy(filename2, argv[2]);
	}
	else
	{
		printf("***Program for comparing two mmp files***");
		printf("This program needs exactly two arguments and you are seeing this message  because \n either those were not provided or more than 2 args were given .\n");
		printf("Please provide the two file names to compare and run the program again");
		exit(1);
	}

	file1=fopen(filename1,"r");
	file2=fopen(filename2,"r");

	i=0;

printf("BEFORE the while loop /n");

	pFile1 = fgets(buf1,127,file1);
	pFile2 = fgets(buf2,127,file2);
	
	while(pFile1 || pFile2)
	{	
		pBuf1 = buf1;
		pBuf2 = buf2;

		switch (parse(pBuf1))
		{
			case PART :
				{	
					break;
				}
			case BOND :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}			
				
				}
			case ATOM :
				{
					pBuf1+=5;
					pBuf2+=5;

					for (i=0;i<5;i++)
					{
						l1= strtol(pBuf1,&pBuf1,10);
						l2 = strtol(pBuf2,&pBuf2,10);
						if (l1 !=l2 && i<2)
						{
							fprintf(pOutFile,"==\n");
							fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
							break;
						}
						else if (i>=2 && labs(l1-l2) >5)
						{
							fprintf(pOutFile,"==\n");
							fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
							break;

						}
						pBuf1+=gSpaceAtom[i];
						pBuf2+=gSpaceAtom[i];
					}
	
					break ;
				}
			case GRND :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						printf("IN the GRND case \n");
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}
					break;
				}
			case MOTOR :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						printf("IN the MOTOR case \n");
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}
					break;
				}
			case LINMOT :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}
					break;
				}
			case SHAFT :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						printf("IN the SHAFT case \n");
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}
					break;
				}
			case BEARING :
				{
					if(0 != strcmp(pBuf1,pBuf2))
					{
						printf("IN the BEARING case \n");
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;						
					}
					break;
				}
			case SHOW :
				{
	
					ntemp++; //this is for debug
					
					pBuf1+=5;
					pBuf2+=5;

					 psTok1=strtok(pBuf1," ");
					 psTok2=strtok(pBuf2," ");

					 check1=check2=0;
					
					 for (i=0;i<7;i++)
						{
							if (0==strncmp(psTok1,gStringArray[i], strlen(gStringArray[i]))) check1=1;
							if (0==strncmp(psTok2,gStringArray[i], strlen(gStringArray[i]))) check2=1;
						}
	
					if(check1!=1 || check2!=1)
					{
						printf("In the SHOW case\t ntemp=%d\n",ntemp);
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						break;					
					}
					break;				
				}
			case END :
				{
					break;				
				}
			case OTHERS : //These are the ones that are not a standard part of mmp files So print those buffers
				{
					fprintf(pOutFile,"==\n");
					fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
					break;	
				
				}
		}
		
		pFile1 = fgets(buf1,127,file1);
		pFile2 = fgets(buf2,127,file2);
	

	}
	fclose(file1);
	fclose(file2);
	fclose(pOutFile);



}

	
	/*	case BOND :
				{
					nExit=0; //To get out of while loop in case a mismatch is found
							//so that no further checking is required. (nExit =1)

					pBuf1+=4;
					pBuf2+=4;

					psTok1=strtok(pBuf1," ");
					psTok2=strtok(pBuf2," ");
					
					while(psTok1!=NULL && psTok2!=NULL && nExit==0)
					{
					
						if(0!= strcmp(psTok1,psTok2))
						{
							
							fprintf(pOutFile,"==\n");
							fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
							nExit=1;					
						}
						//Get the next tokens					
						psTok1=strtok(psTok1+strlen(psTok1)+1," ");					
						psTok2=strtok(psTok2+strlen(psTok2)+1," ");
					}
					break;
				}*/

			/*	case BOND :
				{
					nExit=0; //To get out of while loop in case a mismatch is found
							//so that no further checking is required. (nExit =1)

					pBuf1+=4;
					pBuf2+=4;
					while(pBuf1!=NULL || pBuf2 !=NULL)
					{
						if(*pBuf1++!=*pBuf2))
						{							
							fprintf(pOutFile,"==\n");
							fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
							break;					
						}
						while(pBuf1 ==" " && *pBuf1 != '\0') pBuf1+=1;
						while(pBuf2==" " && *pBuf2 != '\0') pBuf2+=1;												
					}
					break;
				}*/