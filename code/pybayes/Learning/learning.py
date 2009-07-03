#!/usr/bin/env python
# learning routines
# (C) 2008 Denis Maua'


### TO-DO: 
###	1) Implement EM
###	2) Implement TAN structure learner

'''
	Learning Module containing learning routines
'''

from pybayes.Combinatorics.combinatorial import Combination # combinatorial object

class ParameterLearner:
	""" Parameter Learning Procedure
		inputs: Bayesian network G, dataset as list data, variable order in header 
	"""
	def __init__(self,G,data,header):
		if len(G) != len(data[0]):
			raise Exception('Structure mismatch','Number of variables in network does not match data instance length.') 
		self.G = G
		self.header = header
		self.D = data
		
	def __getitem__(self,value):
		#D = [[] for var in self.header]
		### transpose data matrix
		#for inst in self.D:
		#	for i,datum in enumerate(inst):
		#		D[i].append(datum)
		D = []
		for inst in self.D:
			line = []
			for i,var in enumerate(self.header):
				if var in value:
					line.append(inst[i])
			D.append(line)
		return D
	
	def learn(self,gamma=0.00):
		""" Learn parameters from complete data """
		cpts = []
		for v in self.G.V:
			cpts.append(v.cpt.M[0])
			
		# first count occurences
		counts = count(cpts,self.D,self.header)
		
		for i,v in enumerate(self.G.V):
			gamma_den = 1.0
			for va in v.cpt.M[0]:
				gamma_den *= len(va)
			for inst in Combination(v.cpt.M[0]):
				if counts[i].has_key(tuple(inst)):
					#print inst, ':', counts[i][tuple(inst)]
					v.cpt[inst]=float(counts[i][tuple(inst)]) + gamma/gamma_den
				else:
					#print inst, ':', 0.0
					v.cpt[inst]=gamma/gamma_den
			#print
		
			# normalize cpts
			v.cpt.normalize(v) ## transform counts on probabilities


### Counting Routines	
def count(groups,data,header):
	"""Return dict of counting on variables values
	
		inputs: groups, list of lists of variables according their proper cpt order
				data, dataset as lists
				header, dataset header containing list o variables in proper order 
	        output: counts, array of frequencies dicts ordered after groups 
	"""
	vmap = {}
	for i,var in enumerate(header):
		vmap[var] = i
	
	counts = [{} for group in groups]
	for inst in data:
		for g,variables in enumerate(groups):
			query = []
			for i,var in enumerate(variables):
				#print var, vmap[var], inst[vmap[var]]
				query.append(inst[vmap[var]])
				if inst[vmap[var]] not in variables[i]:
					raise Exception('Mispecified domain','A value that does not belong to variable domain was found in dataset. Plese correct either dataset or variable domain. Variable: '+str(variables[i])+', value: '+str(inst[vmap[var]]))
			if counts[g].has_key(tuple(query)):
				counts[g][tuple(query)] += 1
			else: 
				counts[g][tuple(query)] = 1
	return counts


def pcount(groups,data,header,gamma=0.0):
	"""Return factor containing frequencies of variable values
	
		inputs: groups, list of lists of variables according their proper cpt order
				data, dataset as lists
				header, dataset header containing list o variables in proper order 
				gamma, dirichlet priors
	        output: factors, array of factor ordered after groups
	"""
	map = {}
	for i,var in enumerate(header):
		map[var] = i
	
	# couting dict
	counts = [{} for group in groups]

	from DataStructures.potencials import Factor

	# frequency factors
	probs = []
	for group in groups:
		probs.append(Factor(group))

	# count frequencies and store them in dicts
	for inst in data:
		for g,variables in enumerate(groups):
			query = []
			
			for i,var in enumerate(variables):
				#print var, map[var], inst[map[var]]
				query.append(inst[map[var]])
				if inst[map[var]] not in variables[i]:
					raise Exception('Misspecifed domain','A value that does not belong to variable domain was found in dataset. Plese correct either dataset or variable domain. Variable: '+str(variables[i])+', value: '+str(inst[map[var]]))
			if counts[g].has_key(tuple(query)):
				counts[g][tuple(query)] += 1
			else: 
				counts[g][tuple(query)] = 1

	# convert dicts to factors and apply priors
	for i,prob in enumerate(probs):
		gamma_den = 1.0
		for va in prob.M[0]:
			gamma_den *= len(va)
			for inst in Combination(prob.M[0]):
				# individual distributions
				if counts[i].has_key(tuple(inst)):
					prob[inst]=float(counts[i][tuple(inst)])+gamma/gamma_den
				else:
					prob[inst]=gamma/gamma_den
			
	return probs


def jointcount(data):
	"""Return dict of counting on variables values"""
	counts = {}
	for inst in data:
		if counts.has_key(tuple(inst)):
			counts[tuple(inst)] += 1
		else: 
			counts[tuple(inst)] = 1
	return counts

def naivecount(data,header):
	"""Return dict of counting on independent variables values"""
	counts = [{} for var in header]
	for inst in data:
		for i,var_value in enumerate(inst):
			if var_value not in header[i]:
				raise Exception('Misspecifed domain','A value that does not belong to variable domain was found in dataset. Plese correct either dataset or variable domain. Variable: '+str(header[i])+', value: '+str(var_value))
			if counts[i].has_key(var_value):
				counts[i][var_value] += 1
			else: 
				counts[i][var_value] = 1
	return counts
		
def naivecountvars(variables,data,header):
	"""Return dict of counting on independent variables values for given variables"""
	map = {}
	for i,var in enumerate(header):
		map[var] = i
	
	counts = [{} for var in variables]
	for i,var in enumerate(variables):
		for inst in self.D[map[var]]:
			if counts[i].has_key(inst):
				counts[i][inst] += 1
			else: 
				counts[i][inst] = 1
	return counts







