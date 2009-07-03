#!/usr/bin/env python
# Naive Bayes Classifier
# (C) 2009 Denis Maua'

from pybayes.Models.bn import *
from pybayes.Learning.learning import ParameterLearner
from pybayes.IO.io import load_csv
import time


class NaiveBayes:
	" A Naive Bayes Classifier Implementation "
	def __init__ (self, class_variable, attribute_variables, name="NaiveBayes Classifier", header=""):
		" Initialize variables "
		self.class_variable = class_variable
		self.attributes = attribute_variables
		V = [class_variable] + attribute_variables
		E = []
		for rv in attribute_variables:
			E.append ( (class_variable,rv) )

		self.bn = DBN (V, E, name, header) # create bayesian net

	def learn (self, data, header=None, gamma=0.001, verbose=False):
		" Estimate parameters from data "
		start = time.time() # mark starting time
		if header is None:
			header = [self.class_variable] + self.attributes
		learner = ParameterLearner(self.bn, data, header)
		# header contains the order of appearance of variables in file (default is attribute variables list passed in __init__)
		learner.learn(gamma) # gamma is the prior probabilities parameter
		end = time.time() # mark ending time
		if verbose:
			print 'Elapsed time: %dm%.3fs' % ((end-start)/60.0,(end-start)%60.0) 

	def classify (self, observed_date, verbose=False):
		" Classify a given instance "
		est_prob = -10000.0
		est_ind = 0
		import math
		for i,value in enumerate (self.class_variable.Domain):
			score = math.log(self.class_variable.cpt[[value]])
			#print "score: %.2f" % score
			for v in self.attributes:
				#print {self.class_variable: value, v: observed_date[v]}
				score += math.log(v.cpt[{self.class_variable: value, v: observed_date[v]}])
				#print "score: %.2f" % score
			#score = self.bn.inference ({self.class_variable: value}, observed_date)
			#score = score.M[1]
			#print value, score
			if score > est_prob:
				est_prob = score
				estimated = value
				est_ind = i
			
		# return most probable class value
		return self.class_variable.Domain[est_ind]
		

	def batch_classify (self, data, verbose=False):
		start = time.time() # mark starting time
		" Classify a list of instances "
		res = []
		for datum in data:
			res.append ( self.classify(datum,verbose) )
		end = time.time() # mark ending time
		if verbose:
			print 'Elapsed time: %dm%.3fs' % ((end-start)/60.0,(end-start)%60.0) 
		return res

	
