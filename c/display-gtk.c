#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// #include <libxml/tree.h>
#include <gtk/gtk.h>
#include <libgnome/libgnome.h>
#include <libgnomeui/libgnomeui.h>
#include <gconf/gconf-client.h>

#include "mol.h"

/**
 * Ultimately, I'd like this to support some other graphics library,
 * maybe GTK. Ideally we'd establish a standard interface and modules
 * that plug in for different graphics libraries.
 *
 * If we go with a closed-source model, we should probably try to make
 * them dynamically loadable libraries. If open-source, statically linked
 * libraries should be OK.
 */



#define ENABLED 0


GLfloat light_diffuse[] = {1.0, 1.0, 1.0, 1.0};  /* White diffuse light. */
GLfloat color_black[] = {0.0, 0.0, 0.0, 1.0};  /* Black. */
GLfloat color_red[] = {1.0, 0.0, 0.0, 1.0};  /* Red. */
GLfloat light_position[] = {1.0, 1.0, 1.0, 0.0};  /* Infinite light location. */


void display(void) {
#if ENABLED
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
		glutSolidSphere(r, 40,20);
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
#endif
}

void snapshot() {
	char fnam[25];
	FILE *file;
	unsigned char buf[3*SCRWID*SCRHIT], buf2[3*SCRWID*SCRHIT];
	int i, j, w=SCRWID, h=SCRHIT;


#if ENABLED
	glFlush();
	glReadPixels(0,0, w,h, GL_RGB, GL_UNSIGNED_BYTE, buf);
#endif
	/* OpenGL returns the image upside down... */
	for (i=0; i<h; i++)
		for (j=0;j<3*w; j++)
			buf2[i*3*w + j]=buf[(h-i-1)*3*w + j];

	sprintf(fnam,"mol%04d.ppm",ShotNo++);

	file = fopen(fnam,"w");
	fprintf(file, "P6\n%d %d\n%d\n", w, h, 255);
	fwrite(buf2, 1, 3*w*h, file);
	fclose(file);
}


void display_init() {
#if ENABLED
	double dist;

	glutInit(&argc, argv);
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
#endif
}


void display_mainloop() {
	gtk_main();
}

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
