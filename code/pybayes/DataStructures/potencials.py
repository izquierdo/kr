#!/usr/bin/python
# Potencial Function Class
# Copyright 2008 Denis Maua'

from pybayes.Combinatorics.combinatorial import Combination
from pybayes.DataStructures.randomvariables import RandomVariable
import math

import locale
locale.setlocale(locale.LC_NUMERIC, "")


class Factor:
	typeName = "Factor"
	""" Factor Class

	    Data structure for factors F({Vars}) storage

	    Note that Conditional Probababilities Tables can be represented as factors in a 		    straightforward manner, e.g. by just assuming that the first variable is the non-
	    conditional variable whereas the remaining are conditional variables.

	    Note also that factors are not probability distributions since no restriction is imposed 		    neither to individual values nor to sums or combinations of values. Indeed, variable 
	    elimination procedure can produce values greater than 1.0.
	    
	    Be careful to not enter integers as probabilities. Division by integer numbers performed in algorithms will made probabilities equal to zero.

	    input: header, list of Random Variables (the first varible in the list
		   	is taken as the non-conditional variable
		   M, a list of ordered probabilities (optional). If omitted a uniform 	    			   distribution based on first varible is assigned
			TO-DO: consistencyCheck check whether variables sum up to 1.0 (optional)
 """
	def __init__(self, header, M=None, consistencyCheck=False, name=''):
		self.name = name # for compatibility purposes
		self.__vi_map = {} ### variable to index map
		self.M = [[]] ### this is the main data structure; it holds both domain and values
		# insert header into matrix M and map variables to its position in M header row (M[0] entry)
		for i, v in enumerate(header):
			self.M[0].append(v)
			self.__vi_map[v] = i
		self.__precision = 5
		self.cardinality = 1
		for var in header:
			self.cardinality *= len(var)
		if M is None:
			self.generate_zero_distribution()
			#self.generate_uniform_distribution()
		else:
			#i = 0
			#marginal = 0.0
			for m in M:
				#marginal += round(m,self.__precision)
				self.M.append(m)
				"""### check for probablities consistency in cpts(must sum up to 1.0)
				if i == len(self.M[0][0])-1:
					if marginal != 1.0:
						raise Exception('Inconsistency', 'marginal probabilities do not add up to 1.0')
					marginal = 0.0
					i = 0
				else:
					i += 1 """

	def __len__(self):
		" Return the number of variables "
		return len(self.M[0])
				
	def __getitem__(self,inst):
		""" Return factor value for a given instantiation.
		
		 Computes the expression
		     postion_array = v1 + |v1|*v2 + |v1|v2|*v3 + ... + |v1||v2|...|v(N-1)|*vN,
		 where v1 ... vN are the N variables in the distribution, and
		 |v| is the cardinality of the variable (number of values)	
		 and return the position_array element of the Factor Matrix M"""
		values = []
		if type(inst) == type({}):
			# passed dictionary mapping variables to values
			values = [0 for v in self.M[0]]
			for v in inst:
				values[self.__vi_map[v]] = inst[v]
		elif type(inst) == type([]):
			# passed ordered list containing values
			values = inst
		elif type(inst) == type(0):
			# passed position (index)
			if 0 <= inst and inst < self.cardinality:
				return self.M[inst+1]
			else:
				raise Exception('Index out of range', 'index should be in interval [0,self.cardinality)')
			
		else:
			raise Exception('Wrong type', 'values should be passed as a values list or as a dict mapping variables to values')

		if len(values) != len(self.M[0]):
			raise Exception('Wrong instantiation', 'instantiation vector must have the same number of elements as factor variables. Try printing this factor to get an idea of how instatiations should be')

		acc, pos = 1, 1
		for j, v in enumerate(values):
			i = 0
			for value in self.M[0][j]:
				if value == v:
					break
				i += 1
			pos += i*acc
			acc *= len(self.M[0][j])
		return self.M[pos]

	def __setitem__(self,inst,newvalue):
		""" Set factor value for a give instantiation.
		
		 Computes the expression
		     postion_array = v1 + |v1|*v2 + |v1|v2|*v3 + ... + |v1||v2|...|v(N-1)|*vN,
		 where v1 ... vN are the N variables in the distribution, and
		 |v| is the cardinality of the variable (number of values)	
		 and return the position_array element of the Factor Matrix M"""
		values = []
		if type(inst) == type({}):
			values = [0 for v in self.M[0]]
			for v in inst:
				values[self.__vi_map[v]] = inst[v]
		elif type(inst) == type([]):
			values = inst
		else:
			raise Exception('Wrong type', 'values should be passed as a values list or as a dict mapping variables to values')

		if len(values) != len(self.M[0]):
			raise Exception('Wrong instantiation', 'instantiation vector must have the same number of elements as factor variables. Try printing this factor to get an idea of how instatiations should be')

		acc, pos = 1, 1
		for j, v in enumerate(values):
			i = 0
			for value in self.M[0][j]:
				if value == v:
					break
				i += 1
			pos += i*acc
			acc *= len(self.M[0][j])
		self.M[pos] = newvalue

	def domain(self):
		" Return ordered list of factor variables. "
		return self.M[0]

        def getfunction(self):
                " Return function. "
                return self.M[1:]


	""" Membership """
	def __contains__(self,var):
		" Check whether variable is in factor domain. "
		return var in self.M[0]

	""" Algebric Manipulations """
	def __mul__(self,other):
		" Multiply two factors. "
		M = []

		# if other was a number
		if type(other) == type(0) or type(other) == type(0.0):
			for m in xrange(self.cardinality):
				M.append(self.M[m+1] * other)
			header = self.M[0][:]
			return Factor(header,M,name=self.name)

		header = []
		vi_map = {}
		for i,v in enumerate(self.M[0]):
			header.append(v)
			vi_map[v] = i

		for i,v in enumerate(other.M[0]):
			if not vi_map.has_key(v):
				header.append(v)
				vi_map[v] = i

		#print self.__vi_map,other.__vi_map

		for c in Combination(header):
			f1, f2 = ['' for v in self.M[0]], ['' for v in other.M[0]]
			for i,v in enumerate(header):
				if v in self.M[0]:
					#print 'f1', v, c[i]
					f1[self.__vi_map[v]] = c[i]
				if v in other.M[0]:
					#print 'f2', v, c[i]
					f2[other.__vi_map[v]] = c[i]
			#print f1, self[f1], f2, other[f2]
			M.append(self[f1]*other[f2])
		return Factor(header,M,name=self.name+other.name)

	def __div__(self,other):
		### Divide two factors
		M = []

		# if other was a number
		if type(other) == type(0) or type(other) == type(0.0):
			for m in xrange(self.cardinality):
				M.append(self.M[m+1] / other)
			header = self.M[0][:]
			return Factor(header,M,name=self.name)

		header = []
		vi_map = {}
		for i,v in enumerate(self.M[0]):
			header.append(v)
			vi_map[v] = i

		for i,v in enumerate(other.M[0]):
			if not vi_map.has_key(v):
				header.append(v)
				vi_map[v] = i

		for c in Combination(header):
			f1, f2 = ['' for v in self.M[0]], ['' for v in other.M[0]]
			for i,v in enumerate(header):
				if v in self.M[0]:
					#print 'f1', v, c[i]
					f1[self.__vi_map[v]] = c[i]
				if v in other.M[0]:
					#print 'f2', v, c[i]
					f2[other.__vi_map[v]] = c[i]
			#print f1, self[f1], f2, other[f2], self[f1]/other[f2]
			M.append(self[f1]/other[f2])

		return Factor(header,M,name=self.name+"/"+other.name)

	def __add__(self,other):
		### Add two factors
		M = []

		# if other was a number
		if type(other) == type(0) or type(other) == type(0.0):
			for m in xrange(self.cardinality):
				M.append(self.M[m+1] + other)
			header = self.M[0][:]
			return Factor(header,M,name=self.name)

		header = []
		vi_map = {}
		for i,v in enumerate(self.M[0]):
			header.append(v)
			vi_map[v] = i

		for i,v in enumerate(other.M[0]):
			if not vi_map.has_key(v):
				header.append(v)
				vi_map[v] = i

		for c in Combination(header):
			f1, f2 = ['' for v in self.M[0]], ['' for v in other.M[0]]
			for i,v in enumerate(header):
				if v in self.M[0]:
					#print 'f1', v, c[i]
					f1[self.__vi_map[v]] = c[i]
				if v in other.M[0]:
					#print 'f2', v, c[i]
					f2[other.__vi_map[v]] = c[i]
			#print f1, self[f1], f2, other[f2]
			M.append(self[f1]+other[f2])

		return Factor(header,M,name=self.name+"+"+other.name)

	def __iadd__(self,other):
		### Increase factor by number
		for m in xrange(self.cardinality):
			self.M[m+1] += other
		return self

	def __isub__(self,other):
		### Decrease factor by number
		for m in xrange(self.cardinality):
			self.M[m+1] -= other
		return self

	def __imul__(self,other):
		### Multiply factor by number
		for m in xrange(self.cardinality):
			self.M[m+1] *= other
		return self

	def __idiv__(self,other):
		### Divide factor by number
		for m in xrange(self.cardinality):
			self.M[m+1] /= other
		return self

	def max(self):
		### return the maximum probability value	
		return max(self.M[1:])

	def argmax(self):
		### return the most probable assignment
		M = [(m,i) for i,m in enumerate(self.M[1:])]
		M = sorted(M,reverse=True)
		return M[0]

	def log(self):
		"Take the log of the factor"
		for m in xrange(self.cardinality):
			self.M[m+1] = math.log(self.M[m+1])
		self.name = "log(" + self.name + ")"

	def exp(self):
		"Take the power of the factor"
		for m in xrange(self.cardinality):
			self.M[m+1] = math.exp(self.M[m+1])
		self.name = "exp(" + self.name + ")"

	def eliminate_variable(self,var):
		""" Marginalize Factor over given variable """
		if var not in self.M[0]:
			raise Exception('Membership failed', 'Variable does not belong to factor domain.')
		#if var == self.M[0]:
		#	self.M = []
		#	self.M.append([])
		#	self.M.append(1.0)
		i = 0
		step = 1

		for v in self.M[0]:
			if v == var:
				break
			step *= len(v)
			i += 1

		start = 0
		header = []
		vi_map = {}
		i = 0
		# Construct header by adding all but var variables
		# build new variable-index map
		for v in self.M[0]:
			if v != var:
				header.append(v)
				vi_map[v] = i
				i+=1
		factor = [header]
		# summout variable
		for outter in xrange(self.cardinality/step/len(self.M[0][i])):
			start = outter*step*len(self.M[0][i])
			for inner in xrange(step):
				value = 0.0
				n = start
				for sums in xrange(len(self.M[0][i])):
					#print '#', (n+1), 
					value += self.M[n+1]
					#print " : ", self.M[n+1]
					n+=step
				start += 1
				#print value
				#print
				factor.append(value)
			#start += step
		# correct statistics and update matrix M
		self.cardinality /= len(self.M[0][i])
		self.M = factor
		self.__vi_map = vi_map
		# add summing out descriptiom to factor name
		self.name = "(summout_"+str(var)+" "+self.name+")"

	def maximize_variable(self,var):
		""" Marginalize Factor over given variable (max version) 
		    To be used in the max-sum algorithm """
		if var not in self.M[0]:
			raise Exception('Membership failed', 'Variable does not belong to factor domain.')
		#if var == self.M[0]:
		#	self.M = []
		#	self.M.append([])
		#	self.M.append(1.0)
		i = 0
		step = 1

		for v in self.M[0]:
			if v == var:
				break
			step *= len(v)
			i += 1

		start = 0
		header = []
		vi_map = {}
		i = 0
		# Construct header by adding all but var variables
		# and build new variable-index map
		for v in self.M[0]:
			if v != var:
				header.append(v)
				vi_map[v] = i
				i+=1
		factor = [header]
		# summout variable
		for outter in xrange(self.cardinality/step/len(self.M[0][i])):
			start = outter*step*len(self.M[0][i])
			for inner in xrange(step):
				value = -100000000.0 # - infinity
				n = start
				for sums in xrange(len(self.M[0][i])):
					#print '#', (n+1), 
					value = max(value,self.M[n+1])
					#print " : ", self.M[n+1]
					n+=step
				start += 1
				#print value
				#print
				factor.append(value)
			#start += step
		# correct statistics and update matrix M
		self.cardinality /= len(self.M[0][i])
		self.M = factor
		self.__vi_map = vi_map
		# add summing out descriptiom to factor name
		self.name = "(max_"+str(var)+" "+self.name+")"


	def summout(self,var):
		"Shorthand for variable elimination"
		self.eliminate_variable(var)

	def condvar(self,var,value):
		""" Conditionate Factor over given value without removing
		conditional variables from factor """
		if var not in self.M[0]:
			raise Exception('Membership failed', 'Variable does not belong to factor domain.')
		i = 0
		d = 0
		step = 1
		for v in self.M[0]:
			if v == var:
				for val in v.Domain:
					if val == value:
						break
					d += 1
				break
			step *= len(v)
			i += 1
		
		start = 0
		removed = 0
		M = [self.M[0]]
		for outter in xrange(self.cardinality/step/len(self.M[0][i])):
			start = outter*step*len(self.M[0][i]) - removed
			for inner in xrange(step):
				n = start
				for j, values in enumerate(self.M[0][i]):
					#if j != d: 
					if j == d: 
						#print n+1, " : ", self.M[n+1]
						#self.M.pop(n+1)
						M.append(self.M[n+1])
						#removed += 1
					n += step
				start += 1
			#start += step
		self.M = M
		self.cardinality /= len(self.M[0][i])

		self.M[0][i] = RandomVariable(self.M[0][i].name,[value])

	def condvar2(self,var,value):
		""" Conditionate Factor over given value and
		remove conditional variables from factor """
		if var not in self.M[0]:
			raise Exception('Membership failed', 'Variable does not belong to factor domain.')
		i = 0 # variable index
		d = 0 # value index
		step = 1
		# find variable and value indices
		for v in self.M[0]:
			if v == var:
				for val in v.Domain:
					if val == value:
						break
					d += 1
				break
			step *= len(v)
			i += 1

		start = 0
		removed = 0
		#M = [self.M[0]]
		header = []
		vi_map = {}
		k = 0
		for m in self.M[0]:
			if m != var:
				header.append(m)
				vi_map[m] = k
				k+=1
		M = [header]

		for outter in xrange(self.cardinality/step/len(self.M[0][i])):
			start = outter*step*len(self.M[0][i]) - removed
			for inner in xrange(step):
				n = start
				for j, values in enumerate(self.M[0][i]):
					#if j != d: 
					if j == d: 
						#print n+1, " : ", self.M[n+1]
						#self.M.pop(n+1)
						M.append(self.M[n+1])
						#removed += 1
					n += step
				start += 1
			#start += step
		self.cardinality /= len(self.M[0][i])
		self.M = M

		#self.M[0][i] = RandomVariable(self.M[0][i].name,[value])
		self.__vi_map = vi_map
		self.name = "(" + self.name + "|" + str(var) + "=" + str(value) + ")"

	def z(self):
		""" Return the sum of all values in factor matrix M """
		z = 0.0
		for i in xrange(self.cardinality):
			z += self.M[i+1]
		return z

	def normalize(self,variable):
		""" Normalize matrix M over values of given variable 
		    Useful when you have to compute p(a|b,c,...)
		    just normalize p(a,b,c,...) over a.
		"""
		z = self.__vi_map[variable]
		if variable not in self.M[0]:
			raise Exception('Membership failed', 'Variable does not belong to factor domain.')

		i = 0
		step = 1

		for v in self.M[0]:
			if v == variable:
				break
			step *= len(v)
			i += 1

		start = 0
	
		for outter in xrange(self.cardinality/step/len(self.M[0][i])):
			start = outter*step*len(self.M[0][i])
			for inner in xrange(step):
				value = 0
				n = start
				# compute normalization factor
				for sums in xrange(len(self.M[0][i])):
					# print start, '#', (n+1), 
					value += self.M[n+1]
					# print " : ", self.M[n+1]
					n+=step
				# normalize	
				if value != 0:
					n = start
					# print 'value:', value			
					for sums in xrange(len(self.M[0][i])):
						# print start, '#', (n+1), 
						# print " : ", self.M[n+1],
						self.M[n+1] /= value
						# print self.M[n+1] 
						n+=step
				start += 1
				# print 
			#start += step

	def format_num(self, num):
		""" Format a number according to given places and given float precision.
		Return it as string """
		try:
	        	return str(locale.format("%.*f", (self.__precision, num), True))

	    	except (ValueError, TypeError):
	        	return str(num)

	""" Distributions Generators """
	def generate_zero_distribution(self):
		""" Fill Factor with null probability values """
		instanciations = 1
		for var in self.M[0]:
			instanciations *= len(var)
		
		for i in xrange(instanciations):
			self.M.append(0.0)

	def generate_uniform_distribution(self):
		""" Fill Factor with uniform probability values based on first variable """
		instanciations = 1
		for var in self.M[0]:
			instanciations *= len(var)
		
		for i in xrange(instanciations):
			self.M.append(1/float(len(self.M[0][0])))


	def copy(self):
		""" Make a copy of this object """
		return Factor(self.M[0][:],self.M[1:],name=self.name)

	""" Output """
	def __repr__(self):
		### for built-in string calls and debug
		if len(self.name) > 0:
			return self.name
		else:
			s = [str(m)+" " for m in self.M[0]]
			return 'F(' + ''.join(s).rstrip() + ')'

	def __str__(self):
		### return variables distribution in readable format
		""" Print variables and values table ordering and cpt side by side
		    Useful to use as a guide for probabilities input """
		output = ""
		max = [0 for m in self.M[0]]
		nl = "\n"
		i = 0
		for var in self.M[0]:
			max[i] = len(var.name)
			for value in var.Domain:
				if len(str(value)) > max[i]:
					max[i] = len(str(value))
			output += var.name.center(max[i]) 
			output += " "
			i+=1
		#output += " "
		#output += "P(.)".center(self.__precision+2)
		output += " |  " + self.name.center(self.__precision+2)
		output += nl
		l = 1
		for m in Combination(self.M[0]):
			i = 0
			#output += str(l) + ": "
			for value in m:
				output += str(value).center(max[i]) + " "
				i += 1
			if l < len(self.M):
				output += " |  " + self.format_num(self.M[l])
			output += "\n"
			l += 1
		return output
		
	def debug(self):
		print self
		print "M = ", self.M
		print "__vi_map = ", self.__vi_map
		print "name = ", self.name
		print
