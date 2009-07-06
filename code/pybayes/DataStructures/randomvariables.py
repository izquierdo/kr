#!/usr/bin/python
# Random Variables Class
# Copyright 2008 Denis Maua'

class RandomVariable:
	typeName="RandomVariable"
	""" Discrete RandomVarible Class
	    input: variable name and a list containing possible values
	"""
	def __init__(self,name,domain):
		self.name = name
		self.Domain = tuple(domain)
		self.cpt = None

        def domain(self):
            return list(self.Domain)

	def __getitem__(self,value):
		return self.Domain[value]

	def __repr__(self):
		### for built-in string calls and debug
		return self.name

	def __str__(self):
		### for print calls
		return self.name

	def __eq__(self,other):
		### for assessing random variables equality
		if other.name == self.name:
			return True
		return False

	def __ne__(self,other):
		### for assesssing random variables inequality
		if other.name != self.name or other.Domain != self.Domain:
			return True
		return False

	def __hash__(self):
		### hash function - to allow RVs being used as dict keys
		return hash(self.name)

	def __contains__(self,value):
		### value membership test
		if value in self.Domain:
			return True
		return False

	def __len__(self):
		### return domain cardinality
		return len(self.Domain)

	def __add__(self,other):
		### return a RandomVariable containing self Domain extended by other given RV domain
		if type(self) == type(other):
			name = self.name+"_"+other.name
			domain = self.Domain + other.Domain
			return RandomVariable(name,domain)
		else:
			return str(self) + str(other)
