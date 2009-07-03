#!/usr/bin/python
# Factor Class
# Copyright 2009 Denis Maua'
# This class is intended to be a faster and clever implementation of Factor Structures
from pybayes.Combinatorics.combinatorial import Combination
from pybayes.DataStructures.randomvariables import RandomVariable
import math

import locale
locale.setlocale(locale.LC_NUMERIC, "")

def find(l,o):
	# find function for lists
	try:
		return l.index(o)
	except:
		return -1

class UniformDistribution:
	""" Uniform Distribution Class
	    Assigns normalized probability values
	    to a given set of random variables """
	typeName = "Distribution"

	def __init__(self, variables):
		" Input: variables, a list of random variables "
		self.N = 1 # total number of states
		for var in variables:
			self.N *= len(var)

	def probability(self, state):
		" Return the probabilty of a given configuration "
		return 1.0/self.N

class Factor:
	""" Factor Class

	    Data structure for factor function storage and manipulation
	"""
	typeName = "Factor"    

	def __init__(self, variables, function=None):
		" Input: variables, an ordered list of variables "
		self.variables = variables # argument variables
		if not function:
			# if no function is given, assign uniform distribution
			self.function = UniformDistribution(variables).probability
		else:
			self.function = function
		self.__precision = 5 # nr. of decimal places in output

	def __getitem__(self,configuration):
		""" Input: state, list/tuple of variable values 
		in the same order as passed in the constructor 
		Output: F(values), factor value for given configuration
		"""
		assert (len(configuration) == len(self.variables)), "Wrong dimension! This is a %d dimension Factor. " % len(self.variables)

		return self.function(configuration)

	def domain(self):
		" Return ordered list of factor variables. "
		return self.variables

	""" Manipulation """
	def __mul__(self,other):
		" Multiply two factors "
		# new factor domain is the union of two domains
		variables = list(set(self.variables + other.variables))
		# map particular domains to new domain order
		selfmap = []
		othermap = []
		for v in variables:
			selfmap.append(find(self.variables,v))
			othermap.append(find(other.variables,v))

#		selfmap = [find(self.variables,v) for v in variables]
#		othermap = [find(other.variables,v) for v in variables]

		data = {}
#		print variables, self.variables, other.variables
		for s in Combination(variables):
			selfstate = [None for v in self.variables]
			otherstate = [None for v in other.variables]
			for i,v in enumerate(s):
				if selfmap[i] != -1:
					selfstate[selfmap[i]] = v
				if othermap[i] != -1:
					otherstate[othermap[i]] = v
#			print 'new', s
#			print 'R  ', selfstate
#			print 'S  ', otherstate
			data[tuple(s)] = self[selfstate]*other[otherstate]

		return Factor(variables, lambda x: data[tuple(x)])

	""" Membership """
	def __contains__(self,var):
		" Check whether variable is in factor domain. "
		return var in self.variables

	""" Output """
	def format_num(self, num):
		""" Format a number according to given places and given float precision.
		Return it as string """
		try:
	        	return str(locale.format("%.*f", (self.__precision, num), True))

	    	except (ValueError, TypeError):
	        	return str(num)

	def __repr__(self):
		" short string representation "
		s = [str(m)+" " for m in self.variables]
		return 'F(' + ''.join(s).strip() + ')'

	def __str__(self):
		""" Print variables and values table ordering
		 and cpt side by side """
		output = ""
		max = [0 for m in self.variables]
		nl = "\n"
		i = 0
		nr_states = 1
		for var in self.variables:
			max[i] = len(var.name)
			for value in var.Domain:
				if len(str(value)) > max[i]:
					max[i] = len(str(value))
			output += var.name.center(max[i]) 
			output += " "
			nr_states *= len(var)
			i+=1
		#output += " "
		output += " | P(.)".center(self.__precision+2)
		#output += " |  " + self.name.center(self.__precision+2)
		output += nl

		l = 1
		for m in Combination(self.variables):
			i = 0
			#output += str(l) + ": "
			for value in m:
				output += str(value).center(max[i]) + " "
				i += 1
			if l <= nr_states:
				output += " | " + self.format_num(self.function(m))
			output += "\n"
			l += 1
		return output
