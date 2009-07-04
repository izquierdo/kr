#!/usr/bin/env python
# input and output functions
# (C) 2008 Denis Maua'

'''
	Input and Output Module that aims at loading and saving from/to different formats
'''

import csv
from pyparsing import Word, alphas, nums, ZeroOrMore, OneOrMore, Optional, Suppress, commaSeparatedList, Group, CharsNotIn

caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ()[]-'"
lowers = caps.lower()
digits = "0123456789"
empty = "."

def convertIntegers(tokens):
    return int(tokens[0])

def trimString(tokens):
    return str(tokens[0]).strip()

def load_csv(filename,verbose=False):
	"""Load a Comma Separated File into a list of lists. Each line is a list of
	   comma separated objects, appended to a list of lines.
		input: input filename, verbose mode (optional)
		output: Dataset structure containting data from filename
	"""
	data = []
	if verbose:
		print 'loading instances from %s: 0' % filename,
		import sys
	i = 0
	for line in file(filename):
		if not line[0] == '#':
			datainst = commaSeparatedList.parseString(line)
			inst = []
			for value in datainst:
				if value.isdigit():
					#print 'ld#', value
					inst.append(int(value))
				else:
					inst.append(value)
			data.append(inst)
			i += 1
		if verbose:
			if i % 100 == 0:
				print '%d' % i,
				sys.stdout.flush()
			elif i % 50 == 0:
				print '.',
				sys.stdout.flush()
				
	if verbose:
		print ' %d instances loaded' % i
	return data

def load_csv2(filename,verbose=False):
	"""Load a Comma Separated File into a list of lists. Each line is a list of
	   comma separated objects, appended to a list of lines.
		input: input filename, verbose mode (optional)
		output: Dataset structure containting data from filename

	   Faster version using csv module
	"""
	data = []
	if verbose:
		print 'loading instances from %s: 0' % filename,
		import sys
	i = 0
	reader = csv.reader(open(filename))
	for line in reader:
		inst = []
		for value in line:
			if value.isdigit():
				#print 'ld#', value
				inst.append(int(value))
			else:
				inst.append(value)
		data.append(inst)
		i += 1
		if verbose:
			if i % 100 == 0:
				print '%d' % i,
				sys.stdout.flush()
			elif i % 50 == 0:
				print '.',
				sys.stdout.flush()
				
	if verbose:
		print ' %d instances loaded' % (i-1)
	return data


def load_graph(filename):
	"""Load a graph from file into an adjacency map.
		input: input filename
		output: graph as adjancency map G
		
		File must contain graph as an adjancency list such as
		A: B,C
		B: C
		C: .
		Ending vertices should also be represented explicitly as linking to a dot
	"""
	G = {}
	node = Word(caps + lowers + digits).setResultsName("node") + ": " + OneOrMore(Word(caps + lowers + digits + empty) + Suppress(Optional(","))).setResultsName("edges")

	for line in file(filename):
		graph = node.parseString(line)
		G[graph.node] = graph.edges
		
	return G
	
def save_graph(G, filename):
	""" Save graph to file
		input: adjacency mapping G
	"""
	f = file(filename, 'w') # open for writing
	f.write("%% Filename: " + filename + "\n")
	f.write("%%  \n")
	f.write("\n")

	for v in G:
		f.write(v)
		f.write(': ')
		for i, ch in enumerate(G[v]):
				f.write(ch)			
				if i < len(G[v])-1:
					f.write(',')
		f.write("\n")

	f.close()
	

def load_c45_header(filename):
		"""Load random variables definitions from file (in C45 format).
		File must contain information in format 'Variable Name: Values.' as in the example below:
		0,1.
		A: true,false.
		B: 0,1,2.
		C: c1,c2,c3,c4.
		D: one.
		The first line is related to the class object (expressed in last position at the output header)
		"""
		from DataStructures.randomvariables import RandomVariable
		RV = []

		cvariable = OneOrMore(Word(caps + lowers + digits + ".") + Optional(Suppress(","))).setResultsName("domain")  
		variable = Word(caps + lowers + digits).setResultsName("name") + ": " + OneOrMore(Word(caps + lowers + digits + ".") + Optional(Suppress(","))).setResultsName("domain")  
		class_variable = None
		for line in file(filename):
			if not line[0] == '#' and len(line) > 1:
				if class_variable is None:
					dataline = line[0:(len(line)-2)]
					#print dataline
					rv = cvariable.parseString(dataline)
					domain = []
					for value in rv.domain:
						#print value,
						value = ''.join(value)
						if value.isdigit():
							#print 'lv#', value
							domain.append(int(value))
						else:
							domain.append(value)
					#print
					class_variable = RandomVariable('class',domain)
				else:	
					dataline = line[0:(len(line)-2)]
					#print dataline
					rv = variable.parseString(dataline)
					#print rv.name
					domain = []
					for value in rv.domain:
						#print value,
						value = ''.join(value)
						if value.isdigit():
							#print 'lv#', value
							domain.append(int(value))
						else:
							domain.append(value)
					#print
					var = RandomVariable(rv.name,domain)
					RV.append(var)
		RV.append(class_variable)
		return RV

def load_variables(filename):
		"""Load random variables definitions from file (in C45 format but with class at the end).
		File must contain information in format 'Variable Name: Values.' as in the example below:
		A: true,false.
		B: 0,1,2.
		C: c1,c2,c3,c4.
		D: one.
		"""
		from DataStructures.randomvariables import RandomVariable
		RV = []
#		variable = Word(caps + lowers + digits).setResultsName("name") + ": " + OneOrMore(Group(Word(caps + lowers + digits) + Optional("." + Word(caps + lowers + digits))) + Suppress(Optional(","))).setResultsName("domain") + "."

		variable = Word(caps + lowers + digits).setResultsName("name") + ": " + OneOrMore(Word(caps + lowers + digits + ".") + Optional(Suppress(","))).setResultsName("domain")  
		for line in file(filename):
			if not line[0] == '#':
				dataline = line[0:(len(line)-2)]
				#print dataline
				rv = variable.parseString(dataline)
				#print rv.name
				domain = []
				for value in rv.domain:
					#print value,
					value = ''.join(value)
					if value.isdigit():
						#print 'lv#', value
						domain.append(int(value))
					else:
						domain.append(value)
				#print
				var = RandomVariable(rv.name,domain)
				RV.append(var)
		return RV

def load_bif(filename):
	""" TO-DO: Load bayesian network from BIF file. """
	#from DataStructures.randomvariables import RandomVariable
	#from DataStructures.potencials import Factor
	#from Models.bn import DBN

	f = open(filename)
	data = f.read()

        # basics
        word = Word(alphas, alphas + nums + "_-")
        nninteger = Word("123456789", nums).setParseAction(convertIntegers)
        #nnreal = nninteger 

        type_kw = Suppress('type')
        discrete_kw = Suppress('discrete')
        property_kw = Suppress('property')
        network_kw = Suppress('network')
        variable_kw = Suppress('variable')

        lbrk = Suppress('[')
        rbrk = Suppress(']')
        lbrc = Suppress('{')
        rbrc = Suppress('}')
        sc = Suppress(';')

        # attributes
        property = property_kw + CharsNotIn(";").setParseAction(trimString).setResultsName("property", True) + sc

        cardinality = lbrk + nninteger.setResultsName("cardinality") + rbrk
        domain = lbrc + OneOrMore(word.setResultsName("domain", True)) + rbrc
        type = Group(type_kw + discrete_kw + cardinality + domain + sc).setResultsName("type")

        # blocks
	network = network_kw + word.setResultsName("name") + lbrc + ZeroOrMore(property) + rbrc
	variable = variable_kw + word.setResultsName("name") + lbrc + ZeroOrMore(property) + type + ZeroOrMore(property) + rbrc

#	probability = 'probability' + Word(caps + lowers + digits + '._').setResultsName("name") + '{' + 'type discrete' + '[' + Word(digits).setResultsName("cardinality") + ']' + '{' + OneOrMore(Word(caps + lowers + digits + '._') + Suppress(Optional(' '))).setResultsName("domain") + '};' + '}'

        probability = Word("p")

        # bif
        network = network.setResultsName("network")
        variable = variable.setResultsName("variable", True)
        probability = probability.setResultsName("probability", True)

        bif = network + ZeroOrMore(variable | probability)

        # parse and load
        parsed = bif.parseString(data)

        return parsed

def save_bn_to_fg(bn,filename):
	" Save DBN to libDAI .fg fileformat "
	try:
		f = open(filename,"w")
	except Exception: # substitute with appropriated exception
		print "Error opening file '%s'" % filename
	else:
		f.write(str(len(bn)))
		f.write("\n")
		d = {}
		# map variables to indices (nonnegative integers)
		for i,v in enumerate(bn.V):
			d[v] = i

		# save factors (random vars cpts)
		for v in bn.V:
			f.write("\n")
			f.write(str(len(v.cpt))) # no. of variables
			f.write("\n")
			# variables indices
			for i,var in enumerate(v.cpt.domain()):
				f.write(str(d[var]))
				if i < len(v.cpt)-1:
					f.write(" ")
			f.write("\n")
			# variables size
			for i,var in enumerate(v.cpt.domain()):
				f.write(str(len(var)))
				if i < len(v.cpt)-1:
					f.write(" ")
			f.write("\n")

			# no. of nonzero entries in factor table
			nonzero = sum(1 for i in xrange(v.cpt.cardinality) if v.cpt[i] > 0.0)
			f.write(str(nonzero))
			f.write("\n")

			# write nonzero values
			for i in xrange(v.cpt.cardinality):
				if v.cpt[i] > 0.0:
					f.write(str(i)+" "+str(v.cpt[i]))
					f.write("\n")

		f.close()



