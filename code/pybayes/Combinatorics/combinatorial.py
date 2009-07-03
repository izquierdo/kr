#!/usr/bin/python
# Combinatorial Class
# Copyright 2008 Denis Maua'

### TO-DO: add membership method: if [a,0] in Combination([[a,b,c],[0,1]]): do something

""" Usage example:

	print "Generator approach"
	for c in Combination([['a','b','c'],['X','Y']]).iterate():
		print c

	print
	print "Iterator approach"
	comb = Combination([['a','b','c'],['X','Y']])
	print len(comb), "combinations"
	for c in comb:
		print c  """


class Combination:
	""" Combination Generator
	    input: list of all variables containting a list of its domain
	"""
	def __init__(self,domain):
		self.VarsDomain = domain
		self.state = []
		self.combinations = 1
		self.cur = 0
		self.iteration = 0
		for var in domain:
			self.state.append(0)
			self.combinations *= len(var)

	def __iter__(self):
		return self

	def next(self):
		### iterate combination
		self.iteration += 1
		if self.iteration == 1:
			return [self.VarsDomain[var][self.state[var]] for var in xrange(len(self.VarsDomain))]

		if self.iteration > self.combinations:
			raise StopIteration     # end of iteration
		self.increment_state()
		return [self.VarsDomain[var][self.state[var]] for var in xrange(len(self.VarsDomain))]

	def combination(self):
		""" Retrurn variable state list """
		return [self.VarsDomain[var][self.state[var]] for var in xrange(len(self.VarsDomain))]

	def __str__(self):
		### return variable state list as string
		return str(self.iteration) + " " + str([self.VarsDomain[var][self.state[var]] for var in xrange(len(self.VarsDomain))])
	def __len__(self):
		### return domain cardinality
		return self.combinations

	def iterate(self):
		""" iterate combination
			Generator approach
		"""
		while self.iteration < self.combinations:
			yield [self.VarsDomain[var][self.state[var]] for var in xrange(len(self.VarsDomain))]
			self.increment_state()
			self.iteration += 1


	def increment_state(self):
		""" increment variables state """
		if self.cur >= len(self.state):
			return
		self.state[self.cur] += 1
		if self.state[self.cur] >= len(self.VarsDomain[self.cur]):
			self.state[self.cur] = 0
			self.cur += 1
			if self.cur < len(self.state):
				self.increment_state()
		else:
			self.cur = 0
