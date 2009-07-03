#!/usr/bin/python
# Bayesian Network Class
# Copyright 2008 Denis Maua'

from sets import Set
import locale
locale.setlocale(locale.LC_NUMERIC, "")

from pybayes.Graph.graphs import * # Graph routines
from pybayes.DataStructures.randomvariables import RandomVariable # Random Variable class
from pybayes.DataStructures.potencials import Factor # Factor class
from pybayes.Combinatorics.combinatorial import Combination # Combination generator
from factorgraph import * # Factor Graph class

class DBN:
	typeName = "DBN"
	""" Discrete Bayesian Network Class 

	    input: V, a list of Random Variables Objects
		   E, list of ordered pairs (u,v) indicating dependencies from random variable u to v
	"""
	def __init__(self,V,E,name='',desc=''):
		self.name = name
		self.desc = desc
		
		self.G = make_adj_list(V,E) # Create adjancency map
		c = dfs(self.G) # Topological sort
		self.V = c.topo
		self.pa = find_parents(self.G)
		make_cpts(self.V,self.pa) # create CPTS if not already created
		
	def __len__(self):
		" Return domain cardinality. "
		return len(self.V)
				
	def to_factor_graph(self):
		" Return a factor graph version of this BN. "
		V1 = []
		V2 = []
		E = []
		for v in self.V:
			F = v.cpt
			V1.append(v)
			V2.append(F)
			E.append((v,F))
			E.append((F,v))
			if self.pa.has_key(v):
				for pa in self.pa[v]:
					if not (pa,v.cpt) in E:
						E.append((pa,F))
						E.append((F,pa))
		return FactorGraph(V1,V2,E)

	def inference(self,queries,evidences):
		return self.exact_inference(queries,evidences)

	def exact_inference(self,queries,evidences):
		" Naive implementation of inference on BN "
		### conditionate net on evidences and factorize joint distribution
		joint = 1.0
		for v in self.V:
			cpt = v.cpt.copy()
			joint = cpt * joint


		### marginalize non evidences and non queries out of joint distribution
		for v in self.V:
			if v not in evidences and v not in queries:
				joint.eliminate_variable(v)
				
		# Conditionate on evidences
		for e in evidences:		
			if e in joint:
				joint.condvar(e,evidences[e])

		### normalize distribution
		if len(evidences) > 0:
			joint /= joint.z()

		# Conditionate on queries value
		for q in queries:
			if queries[q] != None:
				joint.condvar(q,queries[q])

		return joint


	def __str__(self):
	### for print calls
		nl = "\n"
		output = ""
		if self.name is not None:
			output += self.name + nl
		if self.desc is not None:
			output += self.desc + nl
		for v in self.V:
			if v.cpt is None:
				raise Exception('Missing CPT', 'Every variable in the network must have its own CPT attached')
			output += str(v) + nl
			l = 1

			for c in Combination(v.cpt.domain()):
				output += "\tP(" + v.name + "=" + str(c[0])
				if len(v.cpt.M[0]) > 1:
					output += "|"
				for i in xrange(len(c)-1):
					output += v.cpt.M[0][i+1].name + "=" + str(c[i+1])
					if i < len(c)-2:
						output += ","
				output += ")=" + str(v.cpt.M[l]) + nl
				l += 1

			output += nl
		return output
		
def make_cpts(variables,parents):
	""" Create cpts for variables with no cpt assigned """
	for var in variables:
		if var.cpt is None:
			set = [var]
			if parents.has_key(var) and parents[var] is not None:
				for pa in parents[var]:
					set.append(pa)
			var.cpt = Factor(set)

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    
    parser.add_option('-i', '--input',
                      action='store', type='string', dest='input',
                      help='the input stem file name', metavar="file stem")

    parser.add_option('-o', '--output',
                      action='store', type='string', dest='output',
                      help='the report output file name', metavar="filename")

    (options, args) = parser.parse_args()          
    
    
   ### e.g.: py.by -i alarm
    if options.input: #and options.output:
		V = load_variables(options.input + ".names")
		for var in V:
			print var

# TO-DO: load variables from file as well as graph structure and create a network with these
#	 load cpts from file and use them

	#E = load_graph(options.input + ".graph")
	#CPT = load_parameters(options.input + ".parameters")
	#bn = DBN(V,E,CPT)
	#print g
# TO-DO: convert graph format to BIF
#	save_graph(bn,'BIF')
	
    else:

		print \
		"""
		pyBayes
		(C) 2008 Denis Maua'

		"""
		parser.print_help()
