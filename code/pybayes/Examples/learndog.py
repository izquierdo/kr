#!/usr/bin/env python
# Learning Example
# Dog Problem
# (C) 2008 Denis Maua'

from pybayes.Models.bn import *
from pybayes.Learning.learning import ParameterLearner
from pybayes.IO.io import load_csv
import time

data_filename = 'pybayes/Examples/data/dog/dog100.dat'
#data_filename = 'pybayes/Examples/data/dog/dog1000.dat'
#data_filename = 'pybayes/Examples/data/dog/dog10000.dat'

def run():
	" Run this example "
	begining = time.time()

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

	F = RandomVariable('family_out',['yes','no'])
	B = RandomVariable('bowel_problem',['yes','no'])
	L = RandomVariable('lights',['on', 'off'])
	D = RandomVariable('dog_out',['yes', 'no'])
	H = RandomVariable('hear_bark',['yes', 'no'])
	### Graph Nodes
	V = [F,B,L,D,H]
	### Graph Arcs
	E = [(F,L), (F,D),
	     (B,D), (D,H)]

	### Bayesian network
	g = DBN(V,E,name,header)

	markone = time.time() # mark time

	dat = load_csv(data_filename)

	names = [F,B,L,D,H] # variable ordering in datafile

	marktwo = time.time() # mark time

	learner = ParameterLearner(g,dat,names)
	learner.learn(0.001)

	markthree = time.time() # mark time

	#for v in g.V:
	#	print v.cpt
	print g

	end = time.time()

	print 'Elapsed time on network construction: %dm%.3fs' % ((markone-begining)/60.0,(markone-begining)%60.0) 
	print 'Elapsed time on loading data: %dm%.3fs' % ((marktwo-markone)/60.0,(marktwo-markone)%60.0) 
	print 'Elapsed time on learning: %dm%.3fs' % ((markthree-marktwo)/60.0,(markthree-marktwo)%60.0) 
	print 'Total elapsed time: %dm%.3fs' % ((end-begining)/60.0,(end-begining)%60.0) 


	# dog Bayesian Network used to produce data

	# b: : yes (p: 0.010000000) no (p: 0.990000000)
	# f: : yes (p: 0.150000000) no (p: 0.850000000)
	# h(no): : yes (p: 0.010000000) no (p: 0.990000000)
	# h(yes): : yes (p: 0.700000000) no (p: 0.300000000)
	# l(no): : on (p: 0.050000000) off (p: 0.950000000)
	# l(yes): : on (p: 0.600000000) off (p: 0.400000000)
	# d(no,no): : yes (p: 0.300000000) no (p: 0.700000000)
	# d(no,yes): : yes (p: 0.970000000) no (p: 0.030000000)
	# d(yes,no): : yes (p: 0.900000000) no (p: 0.100000000)
	# d(yes,yes): : yes (p: 0.990000000) no (p: 0.010000000)

	### Obtained with PRISM

	# dog 100
	# b: : yes (p: 0.020000000) no (p: 0.980000000)
	# f: : yes (p: 0.170000000) no (p: 0.830000000)
	# h(no): : yes (p: 0.000000000) no (p: 1.000000000)
	# h(yes): : yes (p: 0.697674419) no (p: 0.302325581)
	# l(no): : o'pybayes/Examples/data/dog/dog100.dat'n (p: 0.060240964) off (p: 0.939759036)
	# l(yes): : on (p: 0.588235294) off (p: 0.411764706)
	# d(no,no): : yes (p: 0.308641975) no (p: 0.691358025)
	# d(no,yes): : yes (p: 1.000000000) no (p: 0.000000000)
	# d(yes,no): : yes (p: 0.941176471) no (p: 0.058823529)
	# d(yes,yes): : yes (p: 0.990000000) no (p: 0.010000000)


	#dog 1000
	# b: : yes (p: 0.014000000) no (p: 0.986000000)
	# f: : yes (p: 0.184000000) no (p: 0.816000000)
	# h(no): : yes (p: 0.000000000) no (p: 1.000000000)
	# h(yes): : yes (p: 0.686695279) no (p: 0.313304721)
	# l(no): : on (p: 0.057598039) off (p: 0.942401961)
	# l(yes): : on (p: 0.603260870) off (p: 0.396739130)
	# d(no,no): : yes (p: 0.346583851) no (p: 0.653416149)
	# d(no,yes): : yes (p: 1.000000000) no (p: 0.000000000)
	# d(yes,no): : yes (p: 0.955801105) no (p: 0.044198895)
	# d(yes,yes): : yes (p: 1.000000000) no (p: 0.000000000)


	#dog 10000
	# b: : yes (p: 0.014600000) no (p: 0.985400000)
	# f: : yes (p: 0.186900000) no (p: 0.813100000)
	# h(no): : yes (p: 0.000000000) no (p: 1.000000000)
	# h(yes): : yes (p: 0.689057879) no (p: 0.310942121)
	# l(no): : on (p: 0.057188538) off (p: 0.942811462)
	# l(yes): : on (p: 0.605136437) off (p: 0.394863563)
	# d(no,no): : yes (p: 0.351243284) no (p: 0.648756716)
	# d(no,yes): : yes (p: 1.000000000) no (p: 0.000000000)
	# d(yes,no): : yes (p: 0.960021610) no (p: 0.039978390)
	# d(yes,yes): : yes (p: 1.000000000) no (p: 0.000000000)


	#dog 100000
	# b: : yes (p: 0.014660000) no (p: 0.985340000)
	# f: : yes (p: 0.186870000) no (p: 0.813130000)
	# h(no): : yes (p: 0.000000000) no (p: 1.000000000)
	# h(yes): : yes (p: 0.690391534) no (p: 0.309608466)
	# l(no): : on (p: 0.058256367) off (p: 0.941743633)
	# l(yes): : on (p: 0.604966019) off (p: 0.395033981)
	# d(no,no): : yes (p: 0.351348653) no (p: 0.648651347)
	# d(no,yes): : yes (p: 1.000000000) no (p: 0.000000000)
	# d(yes,no): : yes (p: 0.957539230) no (p: 0.042460770)
	# d(yes,yes): : yes (p: 1.000000000) no (p: 0.000000000)
