#!/usr/bin/env python
# Naive Bayes Classifier Example
# (C) 2009 Denis Maua'

from pybayes.Classifiers.naivebayes import *
from pybayes.IO.io import load_csv2
from pybayes.Classifiers.Evaluators import accuracy, rank_error
#from pybayes.DataStructures.RandomVariable import *

training_data_filename = "pybayes/Examples/data/rating/experience.training.csv"
test_data_filename = "pybayes/Examples/data/rating/experience.test.csv"
class_position = 0 # position of class variable in data

def run():
	" This example uses the NaiveBayes Class "
	print "loading training data from file..."
	data = load_csv2 (training_data_filename,verbose=True) # load training data from file
	
	names = data.pop (0) # extract variable names from data (first line)

	print "%d variables read." % len(names)

	# extract variable domain from data
	domains = [ [] for name in names ]
	for datum in data:
		for i,domain in enumerate(domains):
			if not datum[i] in domain:
				domain.append (datum[i])
	print "Classes:", sorted(domains[class_position])

	attrs = [] # attribute variables
	for i,name in enumerate(names):
		if i == class_position:
			cv = RandomVariable (name, domains[i])
			print "Class Variable:", cv
		else:
			attrs.append ( RandomVariable (name, [0,1]) )
			#attrs.append ( RandomVariable (name, domains[i]) )
			#print "Attribute:", attrs[-1]

	
	classifier = NaiveBayes (cv, attrs)

	print "learning model from data... (it may take a while)"
	classifier.learn (data, verbose=True)

	print "loading test data from file..."
	data = load_csv2 (test_data_filename,verbose=True) # load test data from 
	data.pop (0) # drop off header
	print "classifying instances..."
	predicted = []
	real = []
	step = 0
	for j,datum in enumerate(data):
		#print '0.'
		real.append ( datum.pop(class_position) ) # extract true value
		instance = {}
		#print '1.'
		for i,var in enumerate(attrs):
			instance[var] = datum[i]
		#print '2.'
		predicted.append ( classifier.classify (instance) )
		#print '3.'
		if 100.0*j/len(data) >= step:
			print "%.2f%%" % (100.0*j/len(data))
			step += 10		
	
	data = None
	print
	print "Accuracy  : %.2f%%" % ( 100.0*accuracy (real, predicted) )
	print "Rank Error: %.2f%%" % ( 100.0*rank_error (real, predicted) )

def run2():
	" This example does not use the NaiveBayes Class "
	print "Not implemented"
