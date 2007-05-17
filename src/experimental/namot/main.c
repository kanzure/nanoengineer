// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
 * Copyright, 1994-1996, The Regents of the University of California. 
 * This software was produced under U.S. Government contract(W-7405-ENG-36) 
 * by Los Alamos National Laboratory, which is operated by the University 
 * of California for the U.S. Department of Energy. The U.S Government 
 * is licensed to use, reproduce, and distribute this software. Permission 
 * is granted to the public to copy and use this software without charge, 
 * provided that this Notice and any statement of authorship are reproduced 
 * on all copies. Neither the Government nor the University makes any 
 * warranty, express or implied, or assumes any liability or responsibility 
 * for the use of this software.
 * LACC-94-11
 */
/*
 * Revision information:
 * $Id$
 */
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <limits.h>

#include "defs.h"
#include "general.h"
#include "x.h"
#include "read_lib.h"
#include "Bases.h"
#include "Backbone.h"
#include "graphics.h"
#include "utility.h"
#include "input.h"
#include "cmd_line.h"
#include "main.h"
#include "spit.h"
#include "strlcpy.h"
#include "strlcat.h"
#include "brokenlinks.h"
#include "singlestrand.h"
#include "amberff.h"
#include "mc.h"
#include "cmds_h.h"
#include "x11win.h"
#include "render.h"

static int  determineBond(ATom *,ATom *);
static int load_resources();
static void sig_caught(int);
static int gen_ss_prms();
static int gen_hub_prms();

Global_Flags_t   FLAGS;
struct _Uphot    Uphot;
struct _Four     Four;
int              warn_level;
char             help_path[PATH_MAX+1];
char             lib_path[PATH_MAX+1];
static int       use_gui = 1;

extern void	  Init_GUI();

    int
Inits(
    ) {
    int	  ctr1;
    char *tmp;
    FLAGS=(WCAd|RotAd|AutoResize|Europa);
    if(signal(SIGSEGV,sig_caught)==SIG_ERR) {
	fprintf(stderr,"Could not setup proper signal control\n");
	return NAMOTERR;
	}
    if(signal(SIGINT,sig_caught)==SIG_ERR) {
	fprintf(stderr,"Could not setup proper signal control\n");
	return NAMOTERR;
	}
    if(signal(SIGTERM,sig_caught)==SIG_ERR) {
	fprintf(stderr,"Could not setup proper signal control\n");
	return NAMOTERR;
	}
    if(signal(SIGHUP,sig_caught)==SIG_ERR) {
	fprintf(stderr,"Could not setup proper signal control\n");
	return NAMOTERR;
	}
    if(signal(SIGQUIT,sig_caught)==SIG_ERR) {
	fprintf(stderr,"Could not setup proper signal control\n");
	return NAMOTERR;
	}

    (void)strlcpy(help_path,HELP_FILE_DIR,PATH_MAX);
    (void)strlcpy(lib_path,LIB_HOME,PATH_MAX);
    if((tmp=getenv("NAMOT_HELP_PATH"))) {
	(void)strlcpy(help_path,tmp,PATH_MAX);
	}
    if((tmp=getenv("NAMOT_LIB_PATH"))) {
	(void)strlcpy(lib_path,tmp,PATH_MAX);
	}
    NCmdInit();
    if(load_base_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(load_sug_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if( load_phop_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(load_unit_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(load_helix_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(load_form_library()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(InitAmberFF()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(RenderInit()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    if(GraphicsInit()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    warn_level=0;
    Four.a1[0]='\0'; Four.a2[0]='\0'; Four.a3[0]='\0'; Four.a4[0]='\0';

    for(ctr1=0;ctr1<MAXDISTS;ctr1++) {
	    dis_list[ctr1].atom1=0;
	    dis_list[ctr1].atom2=0;
	    }

    if (use_gui)
        X11Init();

    XHeight=XWidth=IMAGESIZE;
    if ( !(FLAGS & GUI) ) {
	if(CreateImage()==NAMOTERR) {
	    ExitNamot(1,(char **)NULL);
	    }
	}
    if(load_resources()==NAMOTERR) {
	exit(EXIT_FAILURE);
	}
    angles=(Angle *)0;
    torsionals=(Torsional *)0;
    return NAMOTOK;
    }

    int
main(
    int argc,
    char *argv[]
    ) {
    if (argc > 1 && strcmp(argv[1], "-nogui") == 0)
        use_gui = 0;
    if(Inits()==NAMOTERR) {
	warning(NAMOTERROR,"Unable to initialize\n");
	exit(EXIT_FAILURE);
	}

    if ( FLAGS & GUI ) {
	Init_GUI(argc,argv); }
    else {
	WorkCommandLine();
	}
    ExitNamot(0,(char **)NULL);
    return(0);
    }

    static int
gen_hub_prms(
    ) {
    if(calculate_bu_parms()==NAMOTERR) {
	return NAMOTERR;
	}
    if(bkpar()==NAMOTERR) {
	return NAMOTERR;
	}
    return NAMOTOK;
    }

    static int
gen_ss_prms(
    ) {
    Helix *hptr;
    Base_unit *buptr;
    Base *bptr;

    for(hptr=helix;hptr;hptr=hptr->next_helix) {
	buptr=hptr->base_units;
	if(!buptr) { continue ; }
	bptr=buptr->bases;
	if(!bptr)  { continue ; }
	if(bptr->next_base) {
	    continue;
	    }
	if(SSTDetermineParams(hptr)==NAMOTERR) {
	    return NAMOTERR;
	    }
	}
    return NAMOTOK;
    }
/* 
 * Runs the functions to determine parameters
 */
    int
gen_prms(
    ) {
    if(gen_hub_prms()==NAMOTERR) {
	return NAMOTERR;
	}
    return gen_ss_prms();
    }

/*
 * Empty existing atomic data
 */

    int
empty_data(
    Molecule *mptr
    ) {
    register ATom	*aptr,*paptr;
    register Group	*gptr;
    register Chain	*cptr;

    for(cptr=mptr->chains;cptr;cptr=cptr->cnext) {
	for(gptr=cptr->groups;gptr;gptr=gptr->gnext) {
	    paptr=gptr->atoms;
	    if(!paptr)
		continue;
	    for(aptr=paptr->anext;aptr;aptr=paptr->anext) {
		if(DeleteNonbond(aptr)==NAMOTERR) {
		    return NAMOTERR;
		    }
		if(deleteAtom(paptr,aptr)==NAMOTERR) {
		    return NAMOTERR;
		    }
		}

	    if(DeleteNonbond(paptr)==NAMOTERR) {
		return NAMOTERR;
		}
	    free(paptr);
	    gptr->atoms=(ATom *)0;
	    }
	}
    mptr->flag=(mptr->flag | Bonded)-Bonded;

    return NAMOTOK;
    }
/*
 * Make atom data
 */
    int
make_data(
    Molecule *mptr
    ) {
    register ATom	*aptr;
    register Group	*gptr;
    register Chain	*cptr;
    register Base	*bptr;
    register int	ctr1;
    register int	at=0;


    for( cptr=mptr->chains;cptr;cptr=cptr->cnext) {
	for( gptr=cptr->groups;gptr;gptr=gptr->gnext) {
	    bptr=gptr->base;
	    if(!bptr) {
		IE(__FILE__,__LINE__);
		return NAMOTERR;
		}

	    gptr->atoms=(ATom*) calloc(1,sizeof(ATom));
	    if(gptr->atoms==(ATom *)0) {
		warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
		return NAMOTERR;
		}
	    aptr=gptr->atoms;

	    if(!bptr->def) {
		IE(__FILE__,__LINE__);
		return NAMOTERR;
		}
	    if(!bptr->sug_def) {
		IE(__FILE__,__LINE__);
		return NAMOTERR;
		}
	    if(!bptr->phop_def) {
		IE(__FILE__,__LINE__);
		return NAMOTERR;
		}

	    at=bptr->def->atoms+bptr->sug_def->atoms+bptr->phop_def->atoms;

	    if ( gptr == cptr->groups && !gptr->gnext) {
		at=at-bptr->phop_def->atoms+2;
		}
	    else if (gptr == cptr->groups) {
		if(cptr->groups->base->flags.is_circular) {
		    at=at;
		    }
		else {
		    at=at-bptr->phop_def->atoms+1;
		    }
		}
	    else if (!gptr->gnext) {
		if(gptr->base->flags.is_circular)
		    at=at;
		else
		    at=at+1;
		}

	    for(ctr1=1;ctr1< at; ctr1++) {
		aptr->anext=(ATom *)calloc(1,sizeof(ATom));
		if(aptr->anext == (ATom*)0) {
		    warning(NAMOTERROR,"Error allocatiing memory");
		    return NAMOTERR;
		    }
		aptr=aptr->anext;
		}
	    aptr->anext=NULL;
	    }
	}
    return NAMOTOK;
    }


/* 
 * Generates xyzs
 * Fixes Masses and colours
 * Handss off to determine bonds()
 */
    int
generate(
    ) {
    Molecule		*mptr;
    Chain		*cptr;
    Group		*gptr;
    Group		*ngptr;
    Helix		*hptr;
    int			flag=NAMOTOK,ctr1=0;
    int			brokenlinks=0;
    int			ctr2=0,ctr3=0;
    enum {
	RECALCNONE,
	RECALCHUB,
	RECALCSS } NeedRecalc;
    if(Tag_base_ends()==NAMOTERR) {
	IE(__FILE__,__LINE__);
	return NAMOTERR;
	}

    NeedRecalc=RECALCNONE;
    if(generate_bp()==NAMOTERR) {
	IE(__FILE__,__LINE__);
	return NAMOTERR;
	}

    for(mptr=molecule,ctr1=0; mptr; mptr=mptr->mnext,ctr1++)
	if (!(mptr->flag & Rigid) )
	    for(ctr2=0,cptr=mptr->chains; cptr; cptr=cptr->cnext,ctr2++)
		for(ctr3=0,gptr=cptr->groups; gptr; gptr=gptr->gnext,ctr3++) {
		    if(!gptr->base_unit) {
			IE(__FILE__,__LINE__);
			return NAMOTERR;
			}
		    if(!gptr->helix) {
			IE(__FILE__,__LINE__);
			return NAMOTERR;
			}
		    if(!gptr->base_unit->bases) {
			IE(__FILE__,__LINE__);
			return NAMOTERR;
			}
		    if(!gptr->base_unit->bases->next_base &&
			    !(gptr->helix->flags&GENFROMHUB)) {
			continue;
			}
		    if(generate_sugar(gptr)==NAMOTERR) {
			warning(NAMOTERROR,"generate_sugar failed on m%d:%d:%d\n",
			    ctr1,ctr2,ctr3);
			return NAMOTERR;
			}
		    }
    for(hptr=helix;hptr;hptr=hptr->next_helix) {
	if(!hptr->base_units)
	    continue;
	if(!hptr->base_units->bases)
	    continue;
	if(hptr->base_units->bases->next_base || (hptr->flags&GENFROMHUB))
	    continue;
	NeedRecalc=RECALCHUB;
	if(SSTBuildAtomics(hptr)==NAMOTERR) {
	    IE(__FILE__,__LINE__);
	    return NAMOTERR;
	    }
	}

    for(mptr=molecule; mptr; mptr=mptr->mnext) {
	if (!(mptr->flag & Rigid) ) {
	    for(cptr=mptr->chains; cptr; cptr=cptr->cnext) {
		for(gptr=cptr->groups,ctr1=0; gptr;ctr1++,gptr=gptr->gnext) {
		    if(!gptr->base) {
			IE(__FILE__,__LINE__);
			return NAMOTERR;
			}
		    if(gptr->base->flags.is_circular && !gptr->gnext)
			ngptr=cptr->groups;
		    else
			ngptr=gptr->gnext;

		    if(ngptr) {
			if((ngptr->base_unit->bases->next_base==(Base*)0)) {
			    if(!(ngptr->helix->flags&GENFROMHUB)) {
				continue;
				}
			    }
			}
		    if ( generate_phosphate(gptr,ngptr,ctr1) == NAMOTERR ) {
			flag=NAMOTERR;
			}
		    }
		}
	    }
	}
    
    (void)BrokenLinkNum(&brokenlinks);
    if(brokenlinks) {
	char buf[80];
	int  m1=0,m2=0,c1=0,c2=0,g1=0,g2=0;
	double d=0.0,dx=0.0,dy=0.0,dz=0.0;
	memset(buf,0,sizeof(buf));
	for(ctr1=0;ctr1<brokenlinks;ctr1++) {
	    if(BrokenLinkGet(ctr1,&m1,&c1,&g1,&m2,&c2,&g2,&d,&dx,&dy,&dz)==NAMOTERR) {
		continue;
		}
	    sprintf(buf,"Bad P Distance:%d m%d:%d:%d -> m%d:%d:%d:%8.3f(%8.3f,%8.3f,%8.3f)\n",
			ctr1,m1,c1,g1,m2,c2,g2,d,dx,dy,dz);
	    warning(NAMOTERROR,buf);
	    }
	}
    for(hptr=helix;hptr;hptr=hptr->next_helix) {
	if(hptr->flags&GENFROMHUB) {
	    NeedRecalc=RECALCSS;
	    }
	hptr->flags=(hptr->flags|GENFROMHUB)-GENFROMHUB;
	}
    if(empty_bonds()==NAMOTERR) {
	return NAMOTERR;
	}
    FLAGS=(FLAGS|UpdateI)-UpdateI;
    if(generate_bonds()==NAMOTERR) {
	return NAMOTERR;
	}
    distance_mon();
    if(flag == NAMOTERR )
	    FLAGS=(FLAGS | BadMolecule );
    else if (flag == NAMOTOK )
	    FLAGS=(FLAGS | BadMolecule )-BadMolecule;
    
    if(NeedRecalc==RECALCSS) {
	if(gen_ss_prms()==NAMOTERR) {
	    IE(__FILE__,__LINE__);
	    return NAMOTERR;
	    }
	}
    else if(NeedRecalc==RECALCHUB) {
	if(gen_hub_prms()==NAMOTERR) {
	    IE(__FILE__,__LINE__);
	    return NAMOTERR;
	    }
	}
    return flag;
    }

/*
 * generate bonds for  molecule(s)
 */
    int
generate_bonds(
    ) {
    Molecule    *mptr;
    Chain       *cptr;
    Group       *gptr,*ngptr;
    ATom	*aptr_src=(ATom *)NULL,*aptr_dst=(ATom *)NULL,*aptr;
    Bond	*bond_ptr=0;
    COUNTER	placer,ctr1,ctr2=0,dest;
    Base_lib	*base_lib_ptr;
    Sug_lib	*sug_lib_ptr;
    Phop_lib	*phop_lib_ptr;


    for(mptr=molecule;mptr;mptr=mptr->mnext) {
	if((mptr->flag & Rigid) || (mptr->flag & Bonded))
	    continue;
	if (!mptr->bonds) {
	    mptr->bonds=(Bond *)calloc(1,sizeof(Bond));
	    if(mptr->bonds == (Bond*)0) {
		warning(NAMOTERROR,"Error allocating memory");
		return NAMOTERR;
		}
	    bond_ptr=mptr->bonds;
	    }
	else {
	    for(bond_ptr=mptr->bonds;bond_ptr->bnext;
		    bond_ptr=bond_ptr->bnext)
		;
	    bond_ptr->bnext=(Bond *) calloc(1,sizeof(Bond));
	    if(bond_ptr->bnext == (Bond*)0) {
		warning(NAMOTERROR,"Error allocating memory");
		return NAMOTERR;
		}
	    bond_ptr=bond_ptr->bnext;
	    }

	for(cptr=mptr->chains;cptr;cptr=cptr->cnext) {
	    for(gptr=cptr->groups;gptr;gptr=gptr->gnext) {
		if(!gptr->base) {
		    IE(__FILE__,__LINE__);
		    return NAMOTERR;
		    }
		base_lib_ptr = gptr->base->def;
		sug_lib_ptr  = gptr->base->sug_def;
		phop_lib_ptr = gptr->base->phop_def;
		if(!base_lib_ptr) {
		    IE(__FILE__,__LINE__);
		    return NAMOTERR;
		    }
		if(!sug_lib_ptr) {
		    IE(__FILE__,__LINE__);
		    return NAMOTERR;
		    }
		if(!phop_lib_ptr) {
		    IE(__FILE__,__LINE__);
		    return NAMOTERR;
		    }

		placer=0;ctr1=1;


/* Phosphate bonds */
		if(gptr!=cptr->groups || gptr->base->flags.is_circular) {
		    for(ctr1=0;ctr1<phop_lib_ptr->atoms;ctr1++) {
			aptr_src=getATom(gptr,ctr1);
			if(!aptr_src) {
			    warning(NAMOTERROR,"While making phosphate bonds:\n");
    warning(NAMOTERROR,"getATom returned null %i %i %i!\n",ctr1,ctr2,placer);
			    continue;
			    }
			for(ctr2=1;ctr2<MAXBONDS;ctr2++) {
			    dest=phop_lib_ptr->conn[ctr1][ctr2];
			    if (dest == 0 ) {
				break;
				}
			    dest--;
			    if( dest <= ctr1) continue;

			    if(!bond_ptr->bnext) {
				bond_ptr->bnext=(Bond *)
					    calloc(1,sizeof(Bond));
				if(bond_ptr->bnext==(Bond *)0) {
				    warning(NAMOTERROR,
					"Unable to allocate memory\n");
				    return NAMOTERR;
				    }
				}
			    aptr_dst=getATom(gptr, dest);

			    if(!aptr_dst) {
				warning(NAMOTERROR,
				    "While making phosphate bonds:\n",
				    ctr1,ctr2,placer);
				warning(NAMOTERROR,
				    "getATom returned null %i %i %i!\n",
				    ctr1,ctr2,placer);
				continue;
				}
			    if(aptr_src->NumBonds>=MAXBONDS) {
				IE(__FILE__,__LINE__);
				return NAMOTERR;
				}
			    if(aptr_dst->NumBonds>=MAXBONDS) {
				IE(__FILE__,__LINE__);
				return NAMOTERR;
				}
			    bond_ptr->srcatom=aptr_src;
			    bond_ptr->dstatom=aptr_dst;
			    aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
			    aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
			    aptr_src->NumBonds=aptr_src->NumBonds+1;
			    aptr_dst->NumBonds=aptr_dst->NumBonds+1;
			    bond_ptr=bond_ptr->bnext;
			    bond_ptr->srcatom=aptr_src;
			    bond_ptr->dstatom=aptr_dst;
			    }
			}
		    }
		placer=ctr1;
/* sug bonds*/
		for(ctr1=0;ctr1<sug_lib_ptr->atoms;ctr1++) {
		    aptr_src=getATom(gptr,ctr1+placer);
		    for(ctr2=1;ctr2<MAXBONDS;ctr2++) {
			dest=sug_lib_ptr->conn[ctr1][ctr2];
			if (dest == 0 ) {
			    break;
			    }
			dest--;
			if( dest <= ctr1) continue;
			if (!bond_ptr->bnext) {
			    bond_ptr->bnext=(Bond *)
				  calloc(1,sizeof(Bond));
			    if(bond_ptr->bnext==(Bond *)0) {
				warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
				return NAMOTERR;
				}
			    }
			aptr_dst=getATom(gptr,dest+placer);
			if(!aptr_dst) {
			    warning(NAMOTERROR,"getATom=null in gen_bond\n");
			    continue;
			    }

			if(aptr_src->NumBonds>=MAXBONDS) {
			    IE(__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			if(aptr_dst->NumBonds>=MAXBONDS) {
			    IE(__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			bond_ptr->srcatom=aptr_src;
			bond_ptr->dstatom=aptr_dst;
			aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
			aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
			aptr_src->NumBonds=aptr_src->NumBonds+1;
			aptr_dst->NumBonds=aptr_dst->NumBonds+1;
			bond_ptr=bond_ptr->bnext;
			}
		    }
		placer+=ctr1;

/*base connections */
		for(ctr1=0;ctr1<base_lib_ptr->atoms;ctr1++) {
		    aptr_src=getATom(gptr,ctr1+placer);
		    if(!aptr_src) {
			warning(NAMOTERROR,
			    "getATom returned null:%i %i %i!\n",
			    ctr1,ctr2,placer);
			continue;
			}
		    for(ctr2=1;ctr2<MAXBONDS;ctr2++) {
			dest=base_lib_ptr->conn[ctr1][ctr2];
			if (dest == 0 ) break;
			dest--;
			if( dest <= ctr1) continue;
			if (!bond_ptr->bnext) {
			    bond_ptr->bnext=(Bond *)
				 calloc(1,sizeof(Bond));
			    if(bond_ptr->bnext==(Bond *)0) {
				warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
				return NAMOTERR;
				}
			    }
    
			aptr_dst=getATom(gptr,dest+placer);
			if(!aptr_dst) {
			    warning(NAMOTERROR,
				"getATom returned null:%i %i %i!\n",
				ctr1,ctr2,placer);
			    continue;
			    }
			if(aptr_src->NumBonds>=MAXBONDS) {
			    IE(__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			if(aptr_dst->NumBonds>=MAXBONDS) {
			    IE(__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			bond_ptr->srcatom=aptr_src;
			bond_ptr->dstatom=aptr_dst;
			aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
			aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
			aptr_src->NumBonds=aptr_src->NumBonds+1;
			aptr_dst->NumBonds=aptr_dst->NumBonds+1;
			bond_ptr=bond_ptr->bnext;
			}
		    }

/*	Make base->sugar connection */
		for(aptr=gptr->atoms;aptr;aptr=aptr->anext) {
		    if (!strcasecmp(aptr->name,
			    base_lib_ptr->rib_con)) {
			aptr_src=aptr;
			break;
			}
		    }
		for(aptr=gptr->atoms;aptr;aptr=aptr->anext) {
		    if (aptr->type==ATC1P) {
			aptr_dst=aptr;
			break;
			}
		    }
		if(!aptr_dst || !aptr_src) {
		    IE(__FILE__,__LINE__);
		    return NAMOTERR;
		    }
		bond_ptr->srcatom=aptr_src;
		bond_ptr->dstatom=aptr_dst;
		aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
		aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
		aptr_src->NumBonds=aptr_src->NumBonds+1;
		aptr_dst->NumBonds=aptr_dst->NumBonds+1;
		if (!bond_ptr->bnext) {
		    bond_ptr->bnext=(Bond *) calloc(1,sizeof(Bond));
		    if(bond_ptr->bnext==(Bond *)0) {
			warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
			return NAMOTERR;
			}
		    }
		bond_ptr=bond_ptr->bnext;
	
		placer=ctr1;

/* sug-phop*/
		if ( gptr->gnext || gptr->base->flags.is_circular) {
		    if(gptr->gnext)
			ngptr=gptr->gnext;
		    else
			ngptr=cptr->groups;

		    for(aptr=ngptr->atoms;aptr;aptr=aptr->anext)
			if (aptr->type==ATP) {
			    aptr_src=aptr;
			    break;
			    }

		    for(aptr=gptr->atoms;aptr;aptr=aptr->anext)
			if (aptr->type==ATO3P) {
			    aptr_dst=aptr;
			    break;
			    }

		    if(!aptr_src || !aptr_dst) {
			continue;
			}
		    bond_ptr->srcatom=aptr_src;
		    bond_ptr->dstatom=aptr_dst;
		    aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
		    aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
		    aptr_src->NumBonds=aptr_src->NumBonds+1;
		    aptr_dst->NumBonds=aptr_dst->NumBonds+1;
		    if(!bond_ptr->bnext) {
			bond_ptr->bnext=(Bond *) calloc(
			    1,sizeof(Bond));
			if(bond_ptr->bnext==(Bond *)0) {
			    warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			}
		    bond_ptr=bond_ptr->bnext;

		    aptr_dst=NULL;
		    aptr_src=NULL;

		    for(aptr=ngptr->atoms;aptr;aptr=aptr->anext)
			    if (aptr->type==ATP) {
				aptr_dst=aptr;
				break;
				}

		    for(aptr=ngptr->atoms;aptr;aptr=aptr->anext)
			    if (aptr->type==ATO5P) {
				aptr_src=aptr;
				break;
				}

		    if (!aptr_dst ) {
			warning(NAMOTERROR,"Unable to find P\n");
			continue;
			}

		    if (!aptr_src ) {
			warning(NAMOTERROR,"Unable to find O5*\n");
			continue;
			}

		    bond_ptr->srcatom=aptr_src;
		    bond_ptr->dstatom=aptr_dst;
		    aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
		    aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
		    aptr_src->NumBonds=aptr_src->NumBonds+1;
		    aptr_dst->NumBonds=aptr_dst->NumBonds+1;
		    if(!bond_ptr->bnext) {
			bond_ptr->bnext=(Bond *) calloc(
				    1,sizeof(Bond));
			if(bond_ptr->bnext==(Bond *)0) {
			    warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			}
		    bond_ptr=bond_ptr->bnext;
		    }

/* O3'->H3' */
		if (!gptr->gnext&& !(gptr->base->flags.is_circular)) {
		    for(aptr=gptr->atoms;aptr;aptr=aptr->anext)
			if (aptr->type==ATO3P) {
			    aptr_src=aptr;
			    break;
			    }

		    for(aptr=gptr->atoms;aptr;aptr=aptr->anext)
			if (!strcasecmp(aptr->name,"HE")) {
			    aptr_dst=aptr;
			    break;
			    }

		    bond_ptr->srcatom=aptr_src;
		    bond_ptr->dstatom=aptr_dst;
		    aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
		    aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
		    aptr_src->NumBonds=aptr_src->NumBonds+1;
		    aptr_dst->NumBonds=aptr_dst->NumBonds+1;
		    if(!bond_ptr->bnext) {
			bond_ptr->bnext=(Bond *) calloc(1,sizeof(Bond));
			if(bond_ptr->bnext==(Bond *)0) {
			    warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
			    return NAMOTERR;
			    }
			}
		    bond_ptr=bond_ptr->bnext;
		    }

/* O5'->H5' */
		if(gptr==cptr->groups && !(gptr->base->flags.is_circular) ) {
		    for(aptr=gptr->atoms;aptr;aptr=aptr->anext)
			if (aptr->type==ATO5P) {
			    aptr_src=aptr;
			    break;
			    }

		    for(aptr=gptr->atoms;aptr;aptr=aptr->anext)
			if (!strcasecmp(aptr->name,"HB")) {
			    aptr_dst=aptr;
			    break;
			    }
		    if(!aptr) {
			warning(NAMOTERROR,"Couldn't locate HB\n");
			}
		    else {
			if(!bond_ptr->bnext) {
			    bond_ptr->bnext=(Bond *) calloc(
				1,sizeof(Bond));
			    if(bond_ptr->bnext==(Bond *)0) {
				warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
				return NAMOTERR;
				}
			    }
			bond_ptr->srcatom=aptr_src;
			bond_ptr->dstatom=aptr_dst;
			aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
			aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
			aptr_src->NumBonds=aptr_src->NumBonds+1;
			aptr_dst->NumBonds=aptr_dst->NumBonds+1;
			bond_ptr=bond_ptr->bnext;
			}
		    }
		}
	    }
	mptr->flag|=Bonded;
	}
    for(mptr=molecule;mptr;mptr=mptr->mnext) {
	if(!(mptr->flag & Rigid) || (mptr->flag & Bonded ))
	    continue;
	if (!mptr->bonds) {
	    mptr->bonds=(Bond *)calloc(1,sizeof(Bond));
	    if(mptr->bonds==(Bond *)0) {
		warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
		return NAMOTERR;
		}
	    bond_ptr=mptr->bonds;
	    }
	if (!bond_ptr) {
	    for(bond_ptr=mptr->bonds;bond_ptr->bnext;
		    bond_ptr=bond_ptr->bnext)
		;
	    bond_ptr->bnext=(Bond *) calloc(1,sizeof(Bond));
	    if(bond_ptr->bnext==(Bond *)0) {
		warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
		return NAMOTERR;
		}
	    bond_ptr=bond_ptr->bnext;
	    }
	for(cptr=mptr->chains;cptr;cptr=cptr->cnext) {
	    for(gptr=cptr->groups;gptr;gptr=gptr->gnext) {
		for(aptr_src=gptr->atoms;aptr_src;
					aptr_src=aptr_src->anext) {
		    for(aptr_dst=aptr_src->anext;aptr_dst;
			    aptr_dst=aptr_dst->anext)
			if ( determineBond(aptr_src,aptr_dst) ) {
			    if(!bond_ptr->bnext) {
				bond_ptr->bnext=(Bond *)
				     calloc(1, sizeof(Bond));
				if(bond_ptr->bnext==(Bond *)0) {
				    warning(NAMOTERROR,
					"Unable to allocate memory\n");
				    return NAMOTERR;
				    }
				}
			    bond_ptr->srcatom=aptr_src;
			    bond_ptr->dstatom=aptr_dst;
			    aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
			    aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
			    aptr_src->NumBonds=aptr_src->NumBonds+1;
			    aptr_dst->NumBonds=aptr_dst->NumBonds+1;
			    bond_ptr=bond_ptr->bnext;
			    }

		    if(!gptr->gnext) continue;
		    for(ngptr=gptr->gnext;ngptr;ngptr=ngptr->gnext) {
			for(aptr_dst=ngptr->atoms;aptr_dst;
				aptr_dst=aptr_dst->anext) {
			    if ( determineBond(aptr_src,aptr_dst) ) {
				if(!bond_ptr->bnext) {
				    bond_ptr->bnext=(Bond *)
					 calloc(1, sizeof(Bond));
				    if(bond_ptr->bnext==(Bond *)0) {
					warning(NAMOTERROR,
					    "Unable to allocate memory\n");
					return NAMOTERR;
					}
				    }
				bond_ptr->srcatom=aptr_src;
				bond_ptr->dstatom=aptr_dst;
				aptr_src->bond[aptr_src->NumBonds]=bond_ptr;
				aptr_dst->bond[aptr_dst->NumBonds]=bond_ptr;
				aptr_src->NumBonds=aptr_src->NumBonds+1;
				aptr_dst->NumBonds=aptr_dst->NumBonds+1;
				bond_ptr=bond_ptr->bnext;
				}
			    }
			}
		    }
		}
	    }	
	if ( !mptr->bonds->srcatom  || !mptr->bonds->dstatom ) {
	    free(mptr->bonds);
	    mptr->bonds=(Bond *)0;
	    }
	}
    for(mptr=molecule;mptr;mptr=mptr->mnext)
	mptr->flag|=Bonded;
    return NAMOTOK;
    }

/*
 * Set the right index for colors.
 */
#ifdef __STDC__
void coloratoms()
#else
void
coloratoms()
#endif
{
Molecule	*mptr;
Chain		*cptr;
Group		*gptr;
ATom		*aptr;
char		c;

for(mptr=molecule; mptr; mptr=mptr->mnext)
    for(cptr=mptr->chains; cptr; cptr=cptr->cnext)
	for(gptr=cptr->groups; gptr; gptr=gptr->gnext)
	    for(aptr=gptr->atoms; aptr; aptr=aptr->anext) {
		if(isdigit(aptr->name[0]))
		    c=aptr->name[1];
		else
		    c=aptr->name[0];
		switch(tolower(c)) {
/* H*/
		    case 104:
		    aptr->colour=(unsigned char)WHITE;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.00;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;

/* C*/
		    case 99:
		    aptr->colour=(unsigned char)GREY;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.65;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;

/* O*/
		    case 111:
		    aptr->colour=(unsigned char)RED;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.50;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;
/* N*/
		    case 110:
		    aptr->colour=(unsigned char)BLUE;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.5;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;

/* P*/
		    case 112:
		    aptr->colour=(unsigned char)ORANGE;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.90;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;

		    case 's':
		    aptr->colour=(unsigned char)YELLOW;
		    if(aptr->Sambertype[0]=='\0') {
			aptr->rad=1.85;
			}
		    else {
			if(FFGetVDWc(aptr->Sambertype,&aptr->rad)==NAMOTERR) {
			    IE(__FILE__,__LINE__);
			    }
			}
		    break;

		    default:
		    aptr->colour=(unsigned char)GREEN;
		    aptr->rad=1.8;
		    break;
		    }

		}
}

static double 	carbon[] =
	{	2.722, 1.562,	/* C */
		1.392, 0.960,  /* H */
		3.066, 1.44,	/* N */
		2.326, 1.275,	/* O */
		0.000, 0.000,  /* P */
		3.648, 2.924,  /* S */
		3.648, 0.980 } /* U */;
static double 	hydrogen[] =
	{	1.392, 0.960,	/* C */
		0.000, 0.000,	/* H */
		1.232, 0.828,	/* N */
		1.124, 0.740,	/* O */
		0.000, 0.000,  /* P */
		2.062, 1.528,	/* S */
		2.062, 0.828 } /* U */;
static double 	nitrogen[] =
	{	2.163, 1.450,	/* C */
		1.232, 0.828,	/* H */
		0.000, 0.000,	/* N */
		0.000, 0.000,	/* O */
		0.000, 0.000,	/* P */
		0.000, 0.000,  /* S */
		2.163, 0.828 } /* U */;
static double 	oxygen[] =
	{	2.325, 1.275,	/* C */
		1.124, 0.828,	/* H */
		0.000, 0.000,	/* N */
		0.000, 0.000,	/* O */
		2.924, 1.904,  /* P */
		0.000, 0.000,	/* S */
		2.924, 0.828 } /* U */;
static double 	phosphate[] =
	{	0.000, 0.000,	/* C */
		0.000, 0.000,	/* H */
		0.000, 0.000,	/* N */
		2.924, 1.904,	/* O */
		0.000, 0.000,  /* P */
		0.000, 0.000,  /* S */
		2.924, 1.904 } /* U */;
static double 	sulfur[] =
	{	3.648, 2.924,	/* C */
		2.062, 1.528,	/* H */
		0.000, 0.000,	/* N */
		0.000, 0.000,	/* O */
		2.924, 2.280,  /* P */
		4.571, 2.683,  /* S */
		4.571, 1.528 } /* U */;
static double 	unk[] =
	{	3.648, 0.980,	/* C */
		2.062, 0.828,	/* H */
		2.163, 0.828,	/* N */
		2.924, 0.828,	/* O */
		2.924, 1.904,  /* P */
		4.571, 1.528,  /* S */
		2.300, 0.863 } /* U */;

/*
 *  Determine if two atoms are within bond distance.
 */
    static int
determineBond(
    ATom *src,
    ATom *dst
    ) {
    register int		dsti;
    register char		srcc,dstc;
    register double	max=0.0,min=0.0,dist=0.0;
    enum {
	C,
	H,
	N,
	O,
	P,
	S,
	U
	} ;

    if(isdigit(src->name[0]))
	srcc=tolower(src->name[1]);
    else
	srcc=tolower(src->name[0]);

    if(isdigit(dst->name[0]))
	dstc=tolower(dst->name[1]);
    else
	dstc=tolower(dst->name[0]);
		    
    if ( dstc == 'c')
	dsti=C;
    else if (dstc == 'h' )
	dsti=H;
    else if (dstc == 'n' )
	dsti=N;
    else if (dstc == 'o' )
	dsti=O;
    else if (dstc == 'p' )
	dsti=P;
    else if (dstc == 'a' )
	dsti=S;
    else 
	dsti=4;

    if ( srcc == 'c') {
	max=carbon[dsti*2+0];
	min=carbon[dsti*2+1];
	}
    else if (srcc == 'h' ) {
	max=hydrogen[dsti*2+0];
	min=hydrogen[dsti*2+1];
	}
    else if (srcc == 'n' ) {
	max=nitrogen[dsti*2+0];
	min=nitrogen[dsti*2+1];
	}
    else if (srcc == 'o' ) {
	max=oxygen[dsti*2+0];
	min=oxygen[dsti*2+1];
	}
    else if (srcc == 'p' ) {
	max=phosphate[dsti*2+0];
	min=phosphate[dsti*2+1];
	}
    else if (srcc == 's' ) {
	max=sulfur[dsti*2+0];
	min=sulfur[dsti*2+1];
	}
    else {
	max=unk[dsti*2+0];
	min=unk[dsti*2+1];
	}

    if ( min == 0.0 && max ==0.0 )
	return 0;

    dist=(src->x-dst->x)*(src->x-dst->x)+
	(src->y-dst->y)*(src->y-dst->y)+
	(src->z-dst->z)*(src->z-dst->z);

    if ( min < dist  && dist < max )
	return 1;
    else
	return 0;
    }

/*
 * Delete the bond information for all molecules
 */
    int
empty_bonds(
    ) {
    Molecule	*mptr;
    Chain	*cptr;
    Group	*gptr;
    ATom	*aptr;
    Bond	*bptr,*pbptr;

    for(mptr=molecule;mptr;mptr=mptr->mnext) {
/*
 * There is a case where the user has moved a chain from
 * another molecule to a new molecule. The new molecule
 * will not have any bonds associated, but the atom
 * pointer will indicate bonds.
 */
	for(cptr=mptr->chains;cptr;cptr=cptr->cnext) {
	    for(gptr=cptr->groups;gptr;gptr=gptr->gnext) {
		for(aptr=gptr->atoms;aptr;aptr=aptr->anext) {
		    aptr->NumBonds=0;
		    }
		}
	    }

	pbptr=mptr->bonds;
	if(!pbptr)
	    continue;

	for(bptr=pbptr->bnext;bptr;bptr=pbptr->bnext)
	    if(deleteBond(pbptr,bptr)==NAMOTERR) {
		return NAMOTERR;
		}

	free(mptr->bonds);
	mptr->bonds=(Bond *) 0;
	}

    for(mptr=molecule;mptr;mptr=mptr->mnext)
	mptr->flag=(mptr->flag | Bonded) - Bonded;
    return NAMOTOK;
    }

/*
 * Load ~/.namotrc
 */
    static int
load_resources(
    ) {
    char	namotrc[PATH_MAX];
    char	*name;

    name=getenv("HOME");
    sprintf(namotrc,"%.*s/.namotrc",PATH_MAX-10,name);

    if ( access(namotrc,R_OK) )
	    return NAMOTOK;
    return ProcessFile(namotrc);
    }

/*
 * If namot encounters a non-recoverable error, spit up as much as possible
 * and exit.
 */
    void
FatalError(
    ) {
    (void)spit_pdb("dead.pdb");
    (void)spit_helix("dead.parm");
    (void)spit_parm("dead.param");
    (void)spit_history("dead.history");
#ifdef HAVE_LIBXEXT
    if(FLAGS & ShmOn && FLAGS & InitG)
	(void)DestroyShmImage();
#endif
    exit(EXIT_FAILURE);
    }

/*
 * print error message on coring.
 */
    static void
sig_caught(
    int sig_no
    ) {
    switch(sig_no) {
	case SIGSEGV:
	    fprintf(stderr, "Namot has encountered a segmentation ");
	    fprintf(stderr, "violation.\nPlease mail ");
	    fprintf(stderr, "namot@transposon.lanl.gov with a bug report\n");
	    if(signal(sig_no,SIG_DFL)==SIG_ERR) {
		fprintf(stderr, "Error setting signal back to sigdefault\n");
		exit(EXIT_FAILURE);
		}
	    break;
	default:
	    signal(sig_no,SIG_IGN);
	    ExitNamot(0,(char **)0);
	    break;
	}
    }

/*
 * Execute the commands in filename
 */
    int
ProcessFile(
    char *filename
    ) {
    FILE 	*rc;
    char	*line,*echol;
    int		len=0;
    int		echolen=0;
    int		RetCode=0;


    rc=fopen(filename,"r");
    if(rc == (FILE *)NULL) {
	warning(NAMOTERROR,"Unable to open file:%s\n",filename);
	return NAMOTERR;
	}


    while((line=GetLine(rc,1))) {
	echolen=strlen(line)+10;
	echol=(char *)calloc(echolen,sizeof(char));
	if(echol==(char *)0) {
	    warning(NAMOTERROR,"Unable to allocate memory:%s:%d\n",__FILE__,__LINE__);
	    return NAMOTERR;
	    }
	(void)strlcpy(echol,"echo ",echolen);
	(void)strlcat(echol,line,echolen);
/* Strip out extra newline */
	len=strlen(echol)-1;
	if (len > 0 ) echol[len]='\0';
	(void)ProcessString(echol,(char )1);
	RetCode=ProcessString(line,(char )0);
	if(RetCode==NAMOTERR && !(FLAGS & IGNOREERRORS)) {
	    warning(NAMOTERROR,"Abandoning script processing, consider using \"set ignorescripterrors\".\n");
	    free(line);
	    free(echol);
	    (void)fclose(rc);
	    return RetCode;
	    }
	free(line);
	free(echol);
	}
    (void)fclose(rc);
    return NAMOTOK;
    }

/*
 * Exit namot normally
 */
    int
ExitNamot(
    int code,
    /*@unused@*/ char *argv[]
    ) {
    (void)Close_All(0,(char **)0);
#ifdef HAVE_LIBXEXT
    if(FLAGS & ShmOn && FLAGS & InitG)
	(void)DestroyShmImage();
#endif
    DeleteBaseLib();
    DeleteSugLib();
    DeletePhopLib();
    DeleteUnitLib();
    DeleteHelixLib();
    DeleteFormLib();
    DeleteVDWLib();
    CmdFinish();
    (void)GraphicsFinish();
    FFFinish();
    MCFinish();
    exit(code);
    }
