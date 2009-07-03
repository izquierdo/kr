#!/usr/bin/python
# The dog problem example
# Copyright 2008 Denis Maua'

from pybayes.Models.bn import *
from pybayes.IO.pyparsing import Word, alphas, OneOrMore, Optional, Suppress, Group

def run():
	"Run this example"
	caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ _"
	lowers = caps.lower()
	digits = "0123456789"
	empty = "."

	name = "dogproblem"
	header = \
	"""	The Dog Problem Network
		 F     B
		 |\   /
		 | \ /
		 v  v
		 L  D-->H

		Extracted from E. Charniak.
		Bayesian networks without tears.
		AI Magazine, 1991. \n """

	F = RandomVariable('family_out',['true','false'])
	B = RandomVariable('bowel_problem',['true','false'])
	L = RandomVariable('lights',['on', 'off'])
	D = RandomVariable('dog_out',['true', 'false'])
	H = RandomVariable('hear_bark',['true', 'false'])
	### Graph Nodes
	V = [F,B,L,D,H]
	### Graph Arcs
	E = [(F,L), (F,D),
	     (B,D), (D,H)]
	### Conditional distributions
	F.cpt = Factor([F],[0.15,0.85])
	B.cpt = Factor([B],[0.01,0.99])
	L.cpt = Factor([L, F], [0.6,0.4,0.05,0.95])
	D.cpt = Factor([D, F, B], [0.99,0.01,0.97,0.03,0.9,0.1,0.3,0.7])	
	H.cpt = Factor([H, D], [0.7,0.3,0.01,0.99])

	""" Print two cpts side by side
	    left, right =  str(F.cpt).split('\n'), str(L.cpt).split('\n')
		lwidth = 0
		for line in left:
			if len(line) > lwidth:
				lwidth = len(line)

		w = '%-' + str(lwidth+5) + 's %s'

		lcount, rcount = len(left), len(right)
		while lcount > 0 or rcount > 0:
			if lcount > 0 and rcount > 0:
				print w % (left[len(left)-lcount], right[len(right)-rcount])
				lcount -= 1
				rcount -= 1
			elif lcount > 0:
				print left[len(left)-lcount]
				lcount -= 1
			elif rcount > 0:
				print w % ('', right[len(right)-rcount])
				rcount -= 1 """
			
	g = DBN(V,E,name,header)

	print header
	print
	for v in g.V:
		print 'Random Variable: %-20s' % v,
		print ' D={',
		for value in v:
			print value,
		print '}'
	

	#print g


	"""		Inference Example:
		
					Evidences:	lights=on, hear_bark=false
					Query	 :	family_out=true
				
						  				        P(f,l,~h)
				    P(F=true|L=true,H=false)  = ---------
									         P(l,~h)

								Sum{b,d}{P(f,B,l,D,~h)}
							      =	----------------------
								    Sum{f,b,d}{P(F,B,l,D,~h)}

								 Sum{b,d}{P(f)P(B)P(l|f)P(D|f,B)P(~h|D))}
							      = ------------------------------------------
				 				    Sum{f,b,d}{P(F)P(B)P(l|F)P(D|F,B)P(~h|D))}


			family_out posterior distribution:
					0.500551727589584		// p(true | evidence )
					0.49944827241041606; 	// p(false | evidence ); """
	
	print
	def help():
		print 'Commands:'
		print "\tInput '!' var=value,var=value,... for evidence entry"
		print "\tInput '?' var=value,var=value,... for query network"
		print "\tInput 'p' var to variable 'var' distribution"
		print "\tInput 'l' for random variables listing"
		print "\tInput '.' for state print out"
		print "\tInput 'c' to clear evidences list"
		print "\tInput 'v' for toogle verbose mode"
		print "\tInput 'x' or 'q' or blank line for leaving."
		print

	help()
	evidences = {}
	queries = {}
	verbose = False
	command = raw_input(': ')
	if command == '':
		command = 'q'
	while (command[0] != 'q' and command[0] != 'x'):

		option = ''

		if command[0] == '!':
			args = command[1:].strip()

			evidence = Group(Word(caps + lowers + digits).setResultsName("name") + '=' + Word(caps + lowers + digits).setResultsName("value"))
			variables = OneOrMore(evidence + Suppress(Optional(","))).setResultsName("vars")

			vars = variables.parseString(args)
			for var in vars:
				found = False
				for v in g.V:
					if v.name == var.name and var.value in v:
						found = True
						evidences[v] = var.value
						break
				if not found:
					print 'Variable name or value not found! Please enter a valid variable name and a value in its domain'
			if verbose:
				print evidences


		elif command[0] == '?':
			args = command[1:].strip()

			query = Group(Word(caps + lowers + digits).setResultsName("name") + '=' + Word(caps + lowers + digits).setResultsName("value"))
			variables = OneOrMore(query + Suppress(Optional(","))).setResultsName("vars")

			vars = variables.parseString(args)
			for var in vars:
				found = False
				for v in g.V:
					if v.name == var.name and var.value in v:
						found = True
						queries[v] = var.value
						break
				if not found:
					print 'Variable name or value not found! Please enter a valid variable name and a value in its domain'

			if verbose:
				print queries
				print 
				print "Inference:"

			print g.inference(queries,evidences)
			queries = {}

		elif command[0] == 'c':
			args = command[1:]
			evidences = {}

		elif command[0] == '.':
			args = command[1:]
			print 'state', args
			print 'evidences: ', evidences

		elif command[0] == 'v':
			args = command[1:]
			print 'verbose', args
			verbose = not verbose

		elif command[0] == "l":
			args = command[1:].strip()
			if args == '':
				for v in g.V:
					print 'Random Variable: %-20s' % v,
					print ' D={',
					for value in v:
						print value,
					print '}'
			else:
				import re
				for v in g.V:
					#if v.name.startswith(args):
					p = re.match('^'+args,v.name)
					if p is not None:
						print 'Random Variable: %-20s' % v,
						print ' D={',
						for value in v:
							print value,
						print '}'
			

		elif command[0] == 'p':
			args = command[1:].strip()
			print 'Distributions:'
			var = Word(caps + lowers + digits)
			variables = OneOrMore(var + Suppress(Optional(",")))

			vars = variables.parseString(args)
			for var in vars:	
				found = False
				for v in g.V:
					if v.name == var:
						found = True
						print v.cpt
						break
				if not found:
					print 'Variable name or value not found! Please enter a valid variable name and a value in its domain'

		elif command[0] == 'h':
			help()
		else:
			print "Unknow command! Type 'h' for help."

		command = raw_input(': ')
		if command == '':
			command = 'q'


		
