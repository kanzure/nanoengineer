
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Adjusts the positions of the given atoms so as to minimize the structure's total
energy.
"""

from NE1_Simulation.Parameter import Parameter


class EnergyMinimizer:
	"""
	Adjusts the positions of the given atoms so as to minimize the structure's
	total energy.
	"""


	def minimize(self, structure, parameters):
		"""
		Minimizes the given structure with the given parameters. When NE1 starts
		up, it reads some description of the EnergyMinimizer plugin to load
		which includes a list of Parameters to use for the minimizer
		configuration dialog.
		
		@param structure: whatever NE1 structure object
		@param parameters: an array of L{NE1_Simulation.Parameter.Parameter}
			objects
		@return: the minimized structure object
		"""
		pass

