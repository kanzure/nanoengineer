//====================================================================//
/*	Program to compare two mmp files. 
	
	Program Arguments: two mmp files. 

	Details: 
	
	Small differences in the atom positions in the mmp file are neglected
	Needs further implementation. Not complete as of August 10, 2004
	main() is in this file itself. It is an idependent program

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
	 else return 0;
}


void main (int argc, char *argv[])
{
	int i;
	char filename1[100],filename2[100];
	char buf1[128],buf2[128];

	char *pBuf1= buf1;
	char *pBuf2=buf2;
	char *pEnd;
	int nExit = 0;
	long l1, l2;
	
	char *pFile1;
	char *pFile2;

	pOutFile=fopen ("mmpsCompared.txt","w");
	fprintf(pOutFile,"***\tProgram for comparing two mmp files\t***\n\n");
	fprintf(pOutFile,"This file shows the differences between two files\n\n");
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
		printf("IN the while loop /n");

		switch (parse(pBuf1))
		{
			case PART :
				{						
					pBuf1+=5;
					pBuf2+=5;
					
					printf("");

					pBuf1-=5;
					pBuf2-=5;


					break;
				}
			case BOND :
				{
					nExit=1;
					break;
				}
			case ATOM :
				{
					pBuf1+=5;
					pBuf2+=5;

					//while()
					l1= strtol(pBuf1,&pBuf1,2);
					l2 = strtol(pBuf2,&pBuf2,2);
					if (l1 !=l2) 
					{
						nExit =1;
						fprintf(pOutFile,"==\n");
						fprintf(pOutFile,"file 1 : %sfile 2 : %s",buf1,buf2);
						fprintf(pOutFile,"==\n");
						break;
					}
					pBuf1+=2;
					pBuf2+=2;
	/*				l1= strtol(pBuf1,&pBuf1,2);
					l2 = strtol(pBuf2,&pBuf2,2);
					if(l1 != l2)
					{
						nExit=1;
						fprintf(pOutFile,"file 1 : %s, \tfile 2 : %s \n",buf1,buf2);
						break;

					} */
					
					break ;
				}
			case GRND :
				{
					nExit=1;
					break;
				}
			case MOTOR :
				{
					nExit=1;
					break;
				}
			case LINMOT :
				{
					nExit=1;
					break;
				}
			case SHAFT :
				{
					nExit=1;
					break;
				}
			case BEARING :
				{
					nExit=1;
					break;
				}
		}
		
		pFile1 = fgets(buf1,127,file1);
		pFile2 = fgets(buf2,127,file2);
	

	}
	fclose(pOutFile);
	fclose(file1);
	fclose(file2);

printf("OUT of the while loop /n");

}

/*		while(buf1[i]==buf2[i] && buf1[i]!=''&& buf2[i]!='')
		{
			if(buf1[i]=='(' || buf2[i]=='(') i++;
			if(buf1[i]==',' || buf2[i]==',') i++;
		
			while(buf1[i]!='' || buf2[i]!='')
			{
				
			
			}
			

		
		}
*/

	
