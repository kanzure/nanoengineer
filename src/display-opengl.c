#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <GL/glut.h>

#include "mol.h"

/** display stuff */


/** White diffuse light. */
GLfloat light_diffuse[] = {1.0, 1.0, 1.0, 1.0};
/** Black. */
GLfloat color_black[] = {0.0, 0.0, 0.0, 1.0};
/** Red. */
GLfloat color_red[] = {1.0, 0.0, 0.0, 1.0};
/** Infinite light location. */
GLfloat light_position[] = {1.0, 1.0, 1.0, 0.0};

/** 20 is too big! Even 10 is too big. For the FMC, there is
 *  a sweet spot around 8. Make the number too small and it
 *  gets ugly. 6 is OK.
 */
#define N   6

/**
 */
void display(void) {
	int i,j;
	struct vdWbuf *nvb;
	GLfloat r;

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	for (i=0; i<Nexatom; i++) {
		if (atom[i].disp==0) continue;
		glPushMatrix();
		glColor3fv(element[atom[i].elt].color);
		glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, element[atom[i].elt].color);
		glMaterialfv(GL_FRONT, GL_SPECULAR, light_diffuse);
		glMaterialf(GL_FRONT, GL_SHININESS, 25.0);
		glTranslatef(avg[i].x, avg[i].y, avg[i].z);
		r=(atom[i].disp==2 ? 100.0 : 10.0) * element[atom[i].elt].rvdw;
		glutSolidSphere(r, 2*N, N);
		glPopMatrix();
	}

	glDisable(GL_LIGHTING);
	glColor3fv(color_black);

	glBegin(GL_LINES);
	for (j=0; j<Nexbon; j++) {
		if (atom[bond[j].an1].disp==1 || atom[bond[j].an2].disp==1) {
			glVertex3d(avg[bond[j].an1].x,
				   avg[bond[j].an1].y,avg[bond[j].an1].z);
			glVertex3d(avg[bond[j].an2].x,
				   avg[bond[j].an2].y,avg[bond[j].an2].z);
		}
	}

	/* show vander waals interactions */
	/*
	  glColor3fv(color_red);
	  for (nvb=&vanderRoot; nvb; nvb=nvb->next)
	  for (j=0; j<nvb->fill; j++) {
	  if (atom[nvb->item[j].a1].disp==1 || atom[nvb->item[j].a2].disp==1) {
	  if (vlen(vdif(avg[nvb->item[j].a1],avg[nvb->item[j].a2])) < 400.0){
	  glVertex3d(avg[nvb->item[j].a1].x,
	  avg[nvb->item[j].a1].y,
	  avg[nvb->item[j].a1].z);
	  glVertex3d(avg[nvb->item[j].a2].x,
	  avg[nvb->item[j].a2].y,
	  avg[nvb->item[j].a2].z);
	  }}
	  }
	*/
	glEnd();
	glEnable(GL_LIGHTING);

	glutSwapBuffers();
}

/**
 */
void snapshot(int n) {
	char fnam[25];
	FILE *file;
	unsigned char buf[3*SCRWID*SCRHIT], buf2[3*SCRWID*SCRHIT];
	int i, j, w=SCRWID, h=SCRHIT;


	glFlush();
	glReadPixels(0,0, w,h, GL_RGB, GL_UNSIGNED_BYTE, buf);
	/* OpenGL returns the image upside down... */
	for (i=0; i<h; i++)
		for (j=0;j<3*w; j++)
			buf2[i*3*w + j]=buf[(h-i-1)*3*w + j];

	// sprintf(fnam,"mol%04d.ppm",ShotNo++);
	sprintf(fnam,"mol%04d.ppm", n);

	file = fopen(fnam,"w");
	fprintf(file, "P6\n%d %d\n%d\n", w, h, 255);
	fwrite(buf2, 1, 3*w*h, file);
	fclose(file);
}


/**
 */
void display_init(int *argc, char *argv[]) {
	double dist;

	glutInit(argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
	glutCreateWindow("Molecule!");
	glutReshapeWindow(SCRWID,SCRHIT);
	glutDisplayFunc(display);
	glutKeyboardFunc(keyboard);

	glClearColor(0.4, 0.9, 0.2, 1.0);

	/* Enable a single OpenGL light. */
	glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);
	glLightfv(GL_LIGHT0, GL_POSITION, light_position);
	glEnable(GL_LIGHT0);
	glEnable(GL_LIGHTING);

	/* Use depth buffering for hidden surface elimination. */
	glEnable(GL_DEPTH_TEST);

	/* Setup the view of the molecule. */
	dist = 1.5 * vlen(vdif(Bbox[1],Bbox[0]));

	glMatrixMode(GL_PROJECTION);
	gluPerspective( /* field of view in degree */ 30.0,
			/* aspect ratio */ 1.33333,
			/* Z near */ dist*0.6, /* Z far */ dist*1.5);
	glMatrixMode(GL_MODELVIEW);
	gluLookAt(Center.x, Center.y-dist, Center.z-dist/3.0,  /* eye is at  */
		  Center.x, Center.y, Center.z,      /* center is at  */
		  1.0, 0.0, 0.);      /* up is in positive Y direction */

}

/**
 */
void display_fini(void) {
}

/**
 */
void display_mainloop() {
	glutMainLoop();
}

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
