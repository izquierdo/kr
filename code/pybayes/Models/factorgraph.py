#!/usr/bin/python
# Factor Graph Class
# Copyright 2008 Denis Maua'

from pybayes.Graph import graphs # Graph routines
from pybayes.DataStructures.randomvariables import RandomVariable # Random Variable class
from pybayes.DataStructures.potencials import Factor # Factor class
from pybayes.Combinatorics.combinatorial import Combination # Combination generator

class FactorGraph:
	typeName = "FactorGraph"
	""" This class implements a Factor Graph structure,
	a bi-partite graph with factor and random variables
	as nodes

	"""
	def __init__(self,V1,V2,E,name='',desc=''):
		"Constructor"
		self.name = name
		self.desc = desc
		self.V = V1
		V = []
		for v in V1:
			V.append(v)
		for v in V2:
			V.append(v)
		self.G = graphs.make_adj_list(V,E) # Create adjancency map

	def sum_product(self,verbose=False):
		"Sum-product algorithm "
		self.initialize(verbose)
		self.message_passing(self.forward,verbose)	
	def log_sum_product(self,verbose=False):
		"Sum-product algorithm for log-linear models"
		self.initialize(verbose)
		self.message_passing(self.forward_log,verbose)

	def max_product(self,verbose=False):
		"Sum-product algorithm (map version)"
		self.initialize(verbose)
		self.message_passing(self.forward_max,verbose)

	def viterbi(self,verbose=False):
		"Sum-product algorithm (max-sum version)"
		self.initialize(verbose)
		self.message_passing(self.forward_sum,verbose)

	def initialize(self,verbose=False):
		" Initialize message passing alg."
		self.mo = {}
		self.mi = {}
		self.M = {} # message count
		for v in self.G:
			self.M[v] = 0
			self.mo[v] = {}
			self.mi[v] = {}
		self.it = 1

	def message_passing(self,forward,verbose=False):
		" Common message passing loop "
		F = [None]
		while len(F) > 0:
			if verbose:
				print self.it
			F = []
			for v in self.G:
				# wait until all but one neighbor has passed a message
				if len(self.mi[v]) == len(self.G[v])-1:	
					m = 1.0
					nv = []
					w = None
					for n in self.G[v]:
						if n in self.mi[v]:
							nv.append(n)
						else:
							w = n

					F.append((v,w,nv))
				else:
					# reply messages
					nv = []
					for n in self.mi[v]:
						if not n in self.mo[v]:	
							nv.append(n)
							
					for n in nv:
						nnv = []
						for u in self.G[v]:
							if u != n:
								nnv.append(u)
						F.append((v,n,nnv))

			for (v,w,n) in F:
				if not self.mo[v].has_key(w):
					forward(v,w,n)
					if verbose:
						print [v],"->",[w],[self.mo[v][w]],n
	
			#print self.mi
			#print self.mo
			self.it+=1			

	def forward(self,u,v,n):
		"Forward message from u to v"
		p = 1.0
		for w in n:
			p = self.mo[w][u] * p
		#if u.typeName=="RandomVariable":
		if u.typeName=="Factor":
			p = u * p
			for w in n:
				if w in p:
					p.eliminate_variable(w)

		self.mo[u][v] = p # outgoing message
		self.mi[v][u] = p # ingoing message
		#print [u],"<-",[v],[self.mi[v][u]]
		
	def forward_log(self,u,v,n):
		"Forward message from u to v in log-linear models"
		p = 1.0
		for w in n:
			p = self.mo[w][u] * p
		if u.typeName=="Factor":
			f = u.copy()
			f.exp()
			p = f * p
			for w in n:
				if w in p:
					# p.maximize_variable(w)
					p.eliminate_variable(w)

		self.mo[u][v] = p # outgoing message
		self.mi[v][u] = p # ingoing message
		#print [u],"<-",[v],[self.mi[v][u]]


	def forward_max(self,u,v,n):
		"Forward message from u to v in MAP models"
		p = 1.0
		for w in n:
			p = self.mo[w][u] * p
		if u.typeName=="Factor":
			p = u * p
			for w in n:
				if w in p:
					p.maximize_variable(w)

		self.mo[u][v] = p # outgoing message
		self.mi[v][u] = p # ingoing message
		#print [u],"<-",[v],[self.mi[v][u]]

	def forward_sum(self,u,v,n):
		"Forward message from u to v in log-MAP models"
		p = 0.0
		for w in n:
			p = self.mo[w][u] + p
		if u.typeName=="Factor":
			p = u + p
			for w in n:
				if w in p:
					p.maximize_variable(w)

		self.mo[u][v] = p # outgoing message
		self.mi[v][u] = p # ingoing message
		#print [u],"<-",[v],[self.mi[v][u]]

	def marginals(self):
		"Compute marginals"
		if self.it > 0:
			for v in self.V:
				g = 1.0
				# compute the product of input messages
				for n in self.G[v]:
					g = self.mi[v][n] * g
				print "Marginal", v
				print g
		
	def marginals2(self):
		"Compute marginals"
		if self.it > 0:
			for v in self.V:
				g = 0.0
				# compute the sum of input messages
				for n in self.G[v]:
					g = self.mi[v][n] + g
				print "Marginal", v
				#g.exp()
				print g

	def map(self):
		"Compute maximum a posteriori assignments"
		if self.it > 0:
			for v in self.V:
				g = 1.0
				# compute the product of input messages
				for n in self.G[v]:
					g = self.mi[v][n] * g
				print v, "=",
				p,i = g.argmax()
				print v[i], p
		
	def map2(self):
		"Compute maximum a posteriori assignments"
		if self.it > 0:
			for v in self.V:
				g = 0.0
				# compute the sum of input messages
				for n in self.G[v]:
					g = self.mi[v][n] + g
				print v, "=",
				p,i = g.argmax()
				print v[i], p


