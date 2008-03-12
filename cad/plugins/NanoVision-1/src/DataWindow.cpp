// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "DataWindow.h"


/* CONSTRUCTOR */
DataWindow::DataWindow(QWidget *parent) : QWidget(parent) {
	//setAttribute(Qt::WA_DeleteOnClose);

	static int sequenceNumber = 1;
	QString curFile = tr("document%1").arg(sequenceNumber++);
	setWindowTitle(curFile);
}


/* FUNCTION: closeEvent */
void DataWindow::closeEvent(QCloseEvent *event) {
	event->accept();
}


/* FUNCTION: formatParamter */
void DataWindow::formatParameter(string& key, string& value, string& units) {
	string originalValue = value;
	value = "<td>" + value;
	units = "</td>";
	
	//
	// Results parameters
	//
	if (key == "RunResult") {
		key = "Run Result";
		if (originalValue == "0")
			value = "<td>Success";
		else if (originalValue == "1")
			value = "<td>Still running";
		else if (originalValue == "2")
			value = "<td>Failure";
		else if (originalValue == "3")
			value = "<td>Aborted";
		
	} else if (key == "RunResultMessage") {
		key = "Run Result Message";
		
	} else if (key == "FinalStep") {
		key = "Final Step";
		
	} else if (key == "MaximumForce") {
		key = "Maximum Force";
		units = "kJ mol<sup>-1</sup> nm<sup>-1</sup></td>";
		
	} else if (key == "TotalEnergy") {
		key = "Total Energy";
		units = "kJ mol<sup>-1</sup></td>";
		
	//
	// GROMACS parameters
	//
	} else if (key == "GMX.emstep") {
		key = "Initial step-size (emstep)";
		units = "nm</td>";
		
	} else if (key == "GMX.emtol") {
		key = "Maximum force criteria (emtol)";
		units = "kJ mol<sup>-1</sup> nm<sup>-1</sup></td>";
		
	} else if (key == "GMX.epsilon_r") {
		key = "Relative dielectric constant (epsilon_r)";

	} else if (key == "GMX.integrator") {
		key = "Integrator (integrator)";
		if (originalValue == "cg")
			value = "<td>Conjugate gradients";
		
	} else if (key == "GMX.ns_type") {
		key = "Neighbor search (ns_type)";

	} else if (key == "GMX.nstcgsteep") {
		key = "Steep descent frequencty (nstcgsteep)";
		units = "steps</td>";

	} else if (key == "GMX.nsteps") {
		key = "Maximum integration steps (nsteps)";
		
	} else if (key == "GMX.nstlist") {
		key = "Neighbor list update frequency (nstlist)";
		units = "steps</td>";
		
	} else if (key == "GMX.pbc") {
		key = "Periodic boundary conditions (pbc)";
		
	} else if (key == "GMX.rcoulomb") {
		key = "Coulomb cutoff (rcoulomb)";
		units = "nm</td>";
		
	} else if (key == "GMX.rlist") {
		key = "Neighbor list cutoff (rlist)";
		units = "nm</td>";
		
	} else if (key == "GMX.rvdw") {
		key = "LJ or Buckingham cut-off (rvdw)";
		units = "nm</td>";	
	}
}

