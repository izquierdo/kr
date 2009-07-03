#!/usr/bin/python
# The famous grass wet Bayesian Network example
# Copyright 2008 Denis Maua'

from pybayes.Models.bn import *

def run():
	" Run this example "
	name = "Grass Wet Network"
	header = \
			"""
			 Another famous example: the Grass Wet
			    extracted from WikiPedia, http://en.wikipedia.org/
	
			    Sprinkler <-- Rain
			          \       /
			           \     /
			            \   /
			             \ /
			              v
				   Grass Wet
	
			    RAIN                   SPINKLER
			   T    F     	    RAIN   T      F
			  0.2  0.8     	      F    0.4    0.6
			                      T    0.01   0.99
	
				         GRASS WET
		   	SRINKLER   RAIN   T     F
		       	   F	     F   0.0   1.0
			   F	     T	 0.8   0.2
			   T         F   0.9   0.1
			   T         T   0.99  0.01
	
			V = ['RAIN','SRINKLER','GRASS WET']
			E = [('RAIN','SPRINKLER'),('SPRINKLER','GRASS WET'),('RAIN','GRASS WET')]
	
			Inference: P(RAIN=T | GRASS WET=T) ~ 35.77% """

	R = RandomVariable('Rain',['true','false'])
	S = RandomVariable('Sprinkler',['true','false'])
	G = RandomVariable('Grass Wet',['true', 'false'])
	### Graph Nodes
	V = [R,S,G]
	### Graph Arcs
	E = [(R,S), (R,G), (S,G)]
	### Conditional distributions
	R.cpt = Factor([R],[0.2,0.8])
	S.cpt = Factor([S,R],[0.01,0.99,0.4,0.6])
	G.cpt = Factor([G, R, S], [0.99,0.01,0.9,0.1,0.8,0.2,0.0,1.0])

	g = DBN(V,E,name,header)

	print g

	evidences = {G: 'true'}
	queries = {R: 'true'}

	print 'evidences:'
	for e in evidences:		
		print ' ', e, evidences[e]
	print

	print 'queries:'
	for q in queries:
		print ' ',q, queries[q]
	print

	"""Expected: 0.3577"""
	print 'Inference:'
	print g.inference(queries,evidences)
