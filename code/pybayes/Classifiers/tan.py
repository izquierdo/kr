#!/usr/bin/env python
# Tree Augmented Classifier
# (C) 2008 Denis Maua'

from pybayes.Models.bn import * # main module
from pybayes.Graph.graphs import * # graph manipulation module
from pybayes.IO.io import * # i/o module
from pybayes.Learning.learning import * # learning module
import cPickle # save/load objects
import os # system calls
import time # time measurement
import sys # command line parameters parsing

if len(sys.argv) < 2:
	print 'try %s stem' % sys.argv[0]
	print ' - where stem is the common name of c45 datafiles'
	print ' - e.g. %s data/ft/atl5aug' % sys.argv[0]
	print '    will look after atl5aug.names, atl5aug.data and  atl5aug.test'
	print '    in directory data/ft'
	print
	exit()
else:
	filename = sys.argv[1]

if not os.path.exists(filename+'.names') or not os.path.exists(filename+'.data'):
	print "File do not exist. One of the following files could not be found: %s.names or %s.data. Please enter a valid stem." % (filename, filename)
	exit()

# load variables description from file
start = time.time()
mark1 = time.time()
print "loading variables definition from file...",
H = load_c45_header(filename+'.names')
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
print H
#for v in V:
#	print v, v.Domain

# create a complete graph: make an edge between any two variables
# create pairwise joint probabilities
mark1 = time.time()
print "creating complete graph...",
E = [] # this is used in the MST
V = H[:] # variables vector
E_cond = [] # this is used for counting
class_variable = None  # class variable
# find class variable
for i,u in enumerate(V):
	if u.name == 'class':
		class_variable = V.pop(i)
		cprob = Factor([class_variable]) # class factor
		#E_cond.append([class_variable])
probs = [] # attribute factors vector
# make conditionated pairwise edges
for u in V:
	for v in V:
		if v !=  u and [v,u] not in E:
			probs.append(Factor([u,v,class_variable]))
			E.append([u,v])
			E_cond.append([u,v,class_variable])
mark2 = time.time()

E_cond.append([class_variable])
print "done [%.3fs]" % ((mark2-mark1)%60.0)
data = None
# Check whether relative frequencies and pickled data files exist
if os.path.exists(filename+'.counts') and os.path.exists(filename+'.data.pk'):
	mark1 = time.time()
	print "unpickling data...",
	data_file = open(filename+'.data.pk', 'rb')
	data = cPickle.load(data_file) # fast unpickling
	data_file.close()
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "unpickling counting...",
	counts_file = open(filename+'.counts', 'rb')
	counts = cPickle.load(counts_file)
	counts_file.close()
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
else:
	# otherwise load csv data and produce relative frequencies file.
	mark1 = time.time()
	print "loading data...",
	data = load_csv2(filename+'.data')
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "producing counting...",
	counts = count(E_cond,data,H)
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "saving data to binary file (pickling)..."
	data_file = open(filename+'.data.pk', 'wb')
	cPickle.dump(data, data_file) # fast pickling
	data_file.close()
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "saving couting (next time things will be much faster)...",
	counts_file = open(filename+'.counts', 'wb')
	cPickle.dump(counts, counts_file)
	counts_file.close()
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)

#print E_cond[0]
#print counts[0]

mark1 = time.time()
print "normalizing relative frequencies to obtain probabilities distributions (gamma factor used=0.001)...",
gamma = 0.001 #priors
# compute class distribution
for inst in Combination(cprob.M[0]):
	gamma_den = 1.0
	for va in cprob.M[0]:
		gamma_den *= len(va)
	if counts[len(counts)-1].has_key(tuple(inst)):
		#print inst, ':', counts[i][tuple(inst)]
		cprob[inst]=float(counts[len(counts)-1][tuple(inst)]) + gamma/gamma_den
	else:
		#print inst, ':', 0.0
		cprob[inst]=gamma/gamma_den
#print cprob
for i,prob in enumerate(probs):
	gamma_den = 1.0
	for va in prob.M[0]:
		gamma_den *= len(va)
	for inst in Combination(prob.M[0]):
		if counts[i].has_key(tuple(inst)):
			#print inst, ':', counts[i][tuple(inst)]
			prob[inst]=float(counts[i][tuple(inst)]) + gamma/gamma_den
		else:
			#print inst, ':', 0.0
			prob[inst]=gamma/gamma_den
	probs[i] = prob / cprob
	#prob /= prob.z()
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)

mark1 = time.time()
print "computing mutual information...",
W = {}
from math import log
for i,(u,v) in enumerate(E):
		I = 0.0
		#print probs[i]	
		probu = probs[i].copy()
		probv = probs[i].copy()
		#print u
		#print
		probu.eliminate_variable(v)
		#print v
		#print
		probv.eliminate_variable(u)

		#print probu
		#print probv

		for x in u.Domain:
			for y in v.Domain:
				for c in class_variable.Domain:
					if probs[i][[x,y,c]] != 0.0:
						I += probs[i][[x,y,c]]*log(probs[i][[x,y,c]]/(probu[[x,c]]*probv[[y,c]]))
		W[(u,v)] = -I
mark2 = time.time()
print "done [%.2fs]" % ((mark2-mark1)%60.0)
#print "Mutual Information Weights (note that weights are multiplied by -1 so we can use standard MST):"
#print W
#print probs[0].M
mark1 = time.time()
print "finding minimum spannning tree...",
MST,cost = MinimumSpanningTree(V,E,W)
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
print "Minimum Spanning Tree:"
print MST
print 'Total tree cost: ', (-cost)
mark1 = time.time()
print "Adding arcs from class to attributes...",
for v in V:
	MST.append((class_variable,v))
V.append(class_variable)
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
mark1 = time.time()
print "Building Bayesian network...",
bn = DBN(V,MST,filename+' network')
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
# In case data has not been loaded yet
if data is None:
	data = load_csv(filename+'.data')
print "Bayes Net Structure:"
for v in bn.V:
	if bn.pa.has_key(v):
		print '--', v, bn.pa[v]
	else:
		print '-', v
mark1 = time.time()
print "Learning parameters from TAN network...",
learner = ParameterLearner(bn,data,H)
learner.learn(0.001)
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
mark1 = time.time()
print "Loading test file...",
test = load_csv2(filename+'.test')
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
mark1 = time.time()
print "Testing...",
M = [] # confusion matrix
for value in class_variable.Domain:
	# first index: real
	# second index: esimated
	M.append([0 for value in class_variable.Domain])
l = 0
for line in test:
	l+=1
	evidences = {}
	for var in xrange(len(H)-1):
		evidences[H[var]]=line[var]
	est_prob = -1.0
	est_ind = 0
	for i,value in enumerate(class_variable.Domain):
		#print {class_variable: value},
		inf = bn.inference({class_variable: value},evidences)
		inf = inf.M[1]
		#print inf
		if inf > est_prob:
			est_prob = inf
			estimated = value
			est_ind = i
	real = line[-1]
	#print 'real',real,'estimated',estimated
	if real == estimated:
		M[est_ind][est_ind] += 1		
	else:
		for i,value in enumerate(class_variable.Domain):
			if value == real:
				break;
		M[i][est_ind] += 1
	if l % 100 == 0:
		print l,
		sys.stdout.flush()
	elif l % 50 == 0:
		print '.',
		sys.stdout.flush()
print '(%d) ' % l,
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
print "Confusion Matrix:"
print '     \ estimated'
print 'real   ',
for value in class_variable.Domain:
	print value,
print
corrects = 0
total = 0
for i,line in enumerate(M):
	print class_variable.Domain[i], '    ',
	for j,col in enumerate(line):
		if i==j:
			corrects += col
		total += col
		print col,
	print
acc = corrects*100.0/total
print
print 'Acc.: %.2f%%' % (acc)
print
end = time.time()
print 'Total elapsed time: %.2fs' % ((end-start)%60.0)

