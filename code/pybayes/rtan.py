#!/usr/bin/env python
### 
### Relational TAN (not working really)
###
### (C) 2008 Denis Maua'
### 

# pybayes modules
from bn import * # main module
from graphs import * # graphs manipulation module
from io import * # i/o module
from learning import * # learning module
# standard python modules
import cPickle # save/load objects
import os # system calls
import time # time measurement
import sys # command line parameters parsing

from scipy.stats import chi2 # chi-square distributions

__version__ = 0.1
__name__ = "Relational TAN"
__description__ = "Relational Tree-Augmented Classifier"

# data structure for dataset instances
class Dataset:
	pass

def step1(files):
	#Datasets loading and validation
	#inputs: files
	#outputs: datasets, g_data
	s1mark1 = time.time()
	print "Step 1: Check datasets consistency"
	H = None
	datasets = []
	# load variables description from file
	for filename in files:
		if not os.path.exists(filename+'.names') or not os.path.exists(filename+'.data'):
			print "File do not exist. One of the following files could not be found: %s.names or %s.data. Respective dataset will be discarded." % (filename, filename)
		else:
			mark1 = time.time()
			print " loading variables definition from file %s..." % (filename+'.names'),
			inst = Dataset()
			inst.H = load_c45_header(filename+'.names')
			mark2 = time.time()
			print "done [%.3fs]" % ((mark2-mark1)%60.0)
			if H is None:
				H = inst.H[:]
				inst.filename = filename
				__class_found = False
				inst.V = []
				for h in inst.H:
					if h.name == 'class':
						__class_found = True
						inst.class_variable = h
					else:
						inst.V.append(h)
				if __class_found:
					datasets.append(inst)
				else:
					print " Class variable not found in dataset %s. Dadaset will be discarded." % filename
			else:
				if inst.H != H:
					print " Dataset incoherence! Dataset description %s do not match others datasets. Discarding dataset..." % (filename+'.names')
				else:
					inst.filename = filename
					__class_found = False
					inst.V = []
					for h in inst.H:
						if h.name == 'class':
							__class_found = True
							inst.class_variable = h
						else:
							inst.V.append(h)
					if __class_found:
						datasets.append(inst)
					else:
						print " Class variable not found in dataset %s. Dadaset will be discarded." % filename

	# load csv data.
	for d,dataset in enumerate(datasets):
		mark1 = time.time()
		print " loading data from %s as #%d..." % (dataset.filename+'.data',d),
		tmp_data = load_csv2(dataset.filename+'.data')
		mark2 = time.time()
		print "done [%.3fs]" % ((mark2-mark1)%60.0),
		dataset.data = tmp_data
		print " (%d records)" % len(tmp_data)

		
		s1mark2 = time.time()
	print "Step 1 done [%.3fs]" % ((s1mark2-s1mark1)%60.0)

	return datasets


def step2(datasets):
	# Variable generaliation
	#inputs: datasets, g_data
	#outputs: E, E_cond, cprobs, probs
	s2mark1 = time.time()
	print "Step 2: Variable generalization" # check for generalizable variables

	# 2.1 acquire relative frequencies from data
	mark1 = time.time()
	print " producing relative frequencies from data...",

	n = 0 # total number of instances
	for i,dataset in enumerate(datasets):
		groups = [[dataset.class_variable]]
		for v in dataset.V:
			groups.append([v,dataset.class_variable])
		try:
			dataset.dists = pcount(groups,dataset.data,dataset.H)
		except Exception, e:
			print "%s: %s" % (e[0],e[1])
		#print dataset.filename
		#for prob in dataset.probs:
			#print prob
		n+=len(dataset.data)


	# 2.2 add relative frequencies to produce global relative frequency statistics
	global_dists = []
	for dist in datasets[0].dists:
		global_dists.append(dist.copy())

	#print
	#print "--- GLOBAL COUNTING ---"
	#print

	# global distributions
	for i in xrange(len(datasets)-1):
		#print datasets[i+1].filename
		for j,dist in enumerate(datasets[i+1].dists):
			global_dists[j] = global_dists[j] + datasets[i+1].dists[j]
			#print global_dists[j]


	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)


	# 2.3 apply test of homogeinity to look for generalizable variables

	# -===- apply chi-square test for each variable -===-
	# R datasets
	# C categories
	# Ni number of instances in dataset i = len(dataset.data)
	# Nij number of instances of dataset i of category j
	# Nj number of instances of category j = global_dist[j]
	# n total number of intances (counting all datasets) 
	#
	# dof degrees of freedom, dof=(R-1)(C-1)
	#		
	#
	# q = sum_{i=1}^{R}sum_{j=i}^{C}{\frac{(N_{ij}-\hat{E}_{ij})^2}{\hat{E}_{ij}}}
	# \hat{E}_{ij} = \frac{N_iN_j}{n}
	# pvalue = 1 - chi2.cdf(q,dof)

	mark1 = time.time()
	print " p-value computation..."
	# compute chi-square statitics for all variables
	for v,var in enumerate(datasets[0].V):
		dof = (len(datasets)-1)*(len(var)*len(datasets[0].class_variable)-1) # degrees of freedom = (R-1)(CD-1)

		Q = 0.0 # variable statistics
		for i,dataset in enumerate(datasets):
			#for j,c in enumerate(v):
			for j,inst in enumerate(Combination(dataset.dists[v+1].M[0])):
				# Q = sum_{ijk}{ qijk }
				if global_dists[v+1][inst] > 0.0:
					# qijk = (Nijk - Eijk)^2/Eijk
					# Eijk = NiNjk/n
					Q+=(dataset.dists[v+1][inst]-len(dataset.data)*global_dists[v+1][inst]/n)**2/(len(dataset.data)*global_dists[v+1][inst]/n)
				#print dataset.filename,var,inst,dataset.dists[v+1][inst]
		pvalue = 1 - chi2.cdf(Q,dof) # reject if p-value < alpha=0.05
		print var, pvalue



	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)


	# 2.4 convert relative frequencies to probabilities distributions

	#print
	#print "--- DISTRIBUTIONS ---"
	#print

	gamma = 0.001 # priors
	# add low frequency correction and normalize factors to obtain conditional distribution from joint dist.
	for i,dataset in enumerate(datasets):
		#print dataset.filename
		for j,dist in enumerate(dataset.dists):
			gamma_den = 1.0
			for va in dist.M[0]:
				gamma_den *= len(va)
			for k in xrange(dist.cardinality):
				# individual distributions
				dist.M[k+1]+= gamma/gamma_den
			#if j == 0:
				# class distribution
			#	prob /= prob.z()
			#else:
				# conditional distributions
		                #dataset.dists[i] = prob / probs[0]
			dist.normalize(dist.M[0][0])
			#print dist


	#print
	#print "--- GLOBAL DISTRIBUTIONS ---"
	#print

	gamma = 0.001 # priors
	# global distributions
	for i,dist in enumerate(global_dists):
		gamma_den = 1.0
		for va in dist.M[0]:
			gamma_den *= len(va)
		for k in xrange(dist.cardinality):
			# individual distributions
			dist.M[k+1]+= gamma/gamma_den
		for dataset in datasets:
			if i == 0:
				dist /= dist.z()
			else:
				dist.normalize(dist.M[0][0])
		#print global_dists[i]



	#mark1 = time.time()
	#print "normalizing relative frequencies to obtain probabilities distributions (gamma factor used=0.001)...",
	#gamma = 0.001 #priors
	# compute class distribution
	#for inst in Combination(cprob.M[0]):
	#	gamma_den = 1.0
	#	for va in cprob.M[0]:
	#		gamma_den *= len(va)
	#		if counts[len(counts)-1].has_key(tuple(inst)):
	#	                #print inst, ':', counts[i][tuple(inst)]
	#			cprob[inst]=float(counts[len(counts)-1][tuple(inst)]) + gamma/gamma_den
	#		else:
	#	                #print inst, ':', 0.0
	#			cprob[inst]=gamma/gamma_den
	#print cprob
	#for i,prob in enumerate(probs):
	#	gamma_den = 1.0
	#	for va in prob.M[0]:
	#		gamma_den *= len(va)
	#	for inst in Combination(prob.M[0]):
	#		if counts[i].has_key(tuple(inst)):
	#		        #print inst, ':', counts[i][tuple(inst)]
	#			prob[inst]=float(counts[i][tuple(inst)]) + gamma/gamma_den
	#		else:
	#		        #print inst, ':', 0.0
	#			prob[inst]=gamma/gamma_den
	#	probs[i] = prob / cprob
	        #prob /= prob.z()
	#mark2 = time.time()
	#print "done [%.3fs]" % ((mark2-mark1)%60.0)





	### TO-DO: CODE BELOW IS NOT WORKING CORRECTLY. CHECK IT OUT!


	# create a global graph: make an edge between same variables of distinct instances
	# create pairwise joint probabilities
	mark1 = time.time()
	print " generating inter-instance pairwise edges...",
	E = [] # this is used in the MST
	E_cond = [] # this is used for counting

	cprobs = [] # class variables cpds
	# find class variables and add dataset indices to variables
	for d in xrange(len(datasets)):
		datasets[d].V = datasets[d].H[:]
		for i in xrange(len(datasets[d].V)):
			if datasets[d].V[i].name == 'class':
				datasets[d].V[i].name = ''.join([datasets[d].V[i].name,'_'+str(d)])
				cv = datasets[d].V.pop(i)
				datasets[d].class_variable = cv # instance class variable
				cprob = Factor([cv]) # class factor
				cprobs.append(cprob)
			#print str(d)+':',datasets[d].class_variable	
			else:
				datasets[d].V[i].name = ''.join([datasets[d].V[i].name,'_'+str(d)])
			        #print d,':',datasets[d].V[i].name

	        #print datasets[d].H
	        #print datasets[d].V


	probs = [] # attribute factors vector
	# make conditional inter-instance pairwise edges
	for i in xrange(len(datasets)):
		for k in xrange(len(datasets[i].H)-1):
			if [datasets[i].V[k]] not in E:
				probs.append(Factor([datasets[i].V[k],datasets[i].class_variable]))
				E.append([datasets[i].V[k]])
				E_cond.append([datasets[i].V[k],datasets[i].class_variable])
				E_cond.append([datasets[i].class_variable])
	
		for j in xrange(len(datasets)):
			if i != j:
				E_cond.append([datasets[i].class_variable,datasets[j].class_variable])
				for k in xrange(len(datasets[j].H)-1):
				        #if H[k].name != 'class_'+str(i) and H[k].name != 'class_'+str(j):
					if [datasets[i].V[k],datasets[j].V[k]] not in E and  [datasets[j].V[k],datasets[i].V[k]] not in E:
					        #print "%d: (%s,%s)" % (k,datasets[i][k],datasets[j][k])
						probs.append(Factor([datasets[i].V[k],datasets[j].V[k],datasets[i].class_variable,datasets[j].class_variable]))
						E.append([datasets[i].V[k],datasets[j].V[k]])
						E_cond.append([datasets[i].V[k],datasets[j].V[k],datasets[i].class_variable,datasets[j].class_variable])
						
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
        #print E_cond
        #print len(E_cond)

	s2mark2 = time.time()
	print "Step 2 done [%.3fs]" % ((s2mark2-s2mark1)%60.0)

	return (E, E_cond, cprobs, probs)


def step3():
	s3mark1 = time.time()
	print "Step 3: First-Order TAN"
	s3mark2 = time.time()
	print "Step 3 done [%.3fs]" % ((s3mark2-s3mark1)%60.0)


def step4():
	s4mark1 = time.time()
	print "Step 4: Extend TAN to non-generalizable variables"
	s4mark2 = time.time()
	print "Step 4 done [%.3fs]" % ((s4mark2-s4mark1)%60.0)


def step5():
	s5mark1 = time.time()
	print "Step 5: Parameter learning"
	s5mark2 = time.time()
	print "Step 5 done [%.3fs]" % ((s5mark2-s5mark1)%60.0)


def step6():
	s6mark1 = time.time()
	print "Step 6: Model validation"
	s6mark2 = time.time()
	print "Step 6 done [%.3fs]" % ((s6mark2-s6mark1)%60.0)


def summary():
	print "Summary report:"



# MAIN THREAD STATS HERE


start = time.time() # start timing

print __name__, __version__
print __description__
print
print


if len(sys.argv) < 2:
	print 'try %s stem1 stem2 ... stemN' % sys.argv[0]
	print ' - where stem is the common name of c45 datafiles'
	print ' - e.g. data/ft/atl5aug data/ft/atl5dec'
	print '    will look after atl5aug.names, atl5aug.data, atl5aug.test,'
	print '    atl5dec.names, atl5dec.data and atl5dec.test in'
	print '    directory data/ft'
	print
	exit()
else:
	files = sys.argv[1:]


datasets = step1(files) # load and validate data
(E, E_cond, cprobs, probs) = step2(datasets) # data generalization
#step3
#step4
#step5
#step6

end = time.time()
print "Total elapsed time [%.3fs]" % ((end-start)%60.0)
E, E_cond, cprobs, probs
E, E_cond, cprobs, probs


# PROGRAM ENDS HERE
exit()



























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
# Check whether relative frequencies file and pickled data files exist
# TO-DO: Verify if counts file and data file has same data and time.
if os.path.exists(filename+'.counts') and os.path.exists(filename+'.data.pk'):
	mark1 = time.time()
	print "unpickling data...",
	data_file = open(filename+'.data.pk', 'rb')
	data = cPickle.load(data_file)
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
	data = load_csv(filename+'.data')
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "producing counting...",
	counts = count(E_cond,data,H)
	mark2 = time.time()
	print "done [%.3fs]" % ((mark2-mark1)%60.0)
	mark1 = time.time()
	print "saving data to binary file...",
	data_file = open(filename+'.data.pk', 'wb')
	cPickle.dump(data, data_file)
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
test = load_csv(filename+'.test')
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
mark1 = time.time()
print "Testing...",
M = [] # confusion matrix
for value in class_variable.Domain:
	# first index: real
	# second index: esimated
	M.append([0 for value in class_variable.Domain])
for line in test:
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
mark2 = time.time()
print "done [%.3fs]" % ((mark2-mark1)%60.0)
print "Confusion Matrix:"
print '     \ estimated'
print 'real   ',
for value in class_variable.Domain:
	print value,
print
for i,line in enumerate(M):
	print class_variable.Domain[i], '    ',
	for j,col in enumerate(line):
		print col,
	print
	



print __name__, __version__
print __description__
print
print

start = time.time() # start timing
if len(sys.argv) < 2:
	print 'try %s stem1 stem2 ... stemN' % sys.argv[0]
	print ' - where stem is the common name of c45 datafiles'
	print ' - e.g. data/ft/atl5aug data/ft/atl5dec'
	print '    will look after atl5aug.names, atl5aug.data, atl5aug.test,'
	print '    atl5dec.names, atl5dec.data and atl5dec.test in'
	print '    directory data/ft'
	print
	exit()
else:
	files = sys.argv[1:]

step1()
step2()

end = time.time()
print 'Total elapsed time: %.2fs' % ((end-start)%60.0)


