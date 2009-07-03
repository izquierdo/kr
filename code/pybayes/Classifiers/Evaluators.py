#!/usr/bin/env python
# Classifier Evaluation Functions
# (C) 2009 Denis Maua'


# Loss functions
def zeroloss (t):
	# Zero Loss Function
	# t = (c,p), where c is the correct value, p the predicted one
	if t[0] == t[1]:
		return 1
	return 0

def rankloss (t):
	# Rank Loss Function
	# t = (c,p), where c is the correct value, p the predicted one
	return abs ( float(t[0]) - float(t[1]) )


# Evaluation metrics
def accuracy (true_data, predicted_data):
	" Accuracy: Apply Zero-One Loss to a list of instances "
	return 1.0 * sum ( map (zeroloss, zip (*[true_data, predicted_data]) ) ) / len(true_data)
	

def rank_error (true_data, predicted_data):
	" Error: Apply Rank Loss to a list of instances "
	return 1.0 * sum ( map (rankloss, zip (*[true_data, predicted_data]) ) ) / len(true_data)
