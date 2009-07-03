#!/usr/bin/python
# Split Generator
# Author: Denis D. Maua
# This script generates training and test files in csv input data format conducting a approx. 66% split on original file.
#
# input -f csv_filename - name of the csv file to be splitted
# output -o filenames_stem - stem of the filenames to be generated
#	   two files will be generated filenames_stem.test and filenames_stem.data
#	   containing test and training datasets, resp.
#

import math, random
import time # time measurement


def countlines(file): # count the number of lines in file
    a=None
    n=0
    while not a=='':
        a=file.read(262144) # season to taste
        n+=a.count('\n')
    return n


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    
    parser.add_option('-f', '--file',
                      action='store', type='string', dest='filename',
                      help='the csv file name', metavar="FILE")

    parser.add_option('-o', '--output',
                      action='store', type='string', dest='output',
                      help='the output stem file name', metavar="OUTPUT")

    parser.add_option('-p', '--percentage',
                      action='store', type='string', dest='percentage',
                      help='the split percentage related to training set (def: 66)', metavar="PERCENT")

    (options, args) = parser.parse_args()          
    
    
    if options.filename:
	if not options.percentage:
		percentage = 66 # default splitting rate
	else:
		try:
			percentage = int(options.percentage)
		except:
			percentage = 66

    	random.seed()
	fi = file(options.filename) # open for reading
	ftraining = file(options.output+".data", 'w') # open for writing
	ftest = file(options.output+".test", 'w') # open for writing
	training,test = 0,0


        # TO-DO: split file exactly, not probabilistically
        # TO-DO: converto splitter in removeFold
        """mark1 = time.time()
        print "counting total number of lines in file...",
        total = countlines(fi)
        mark2 = time.time()
        print "done in %.3fs" % ((mark2-mark1)%60.0)

        training = int(total*percentage/100)
        training_percentage = training*100.0/total
        test = total - training
        test_percentage = 100 - training_percentage
        diff = percentage-training_percentage
	print "Total instances: %d" % total
	print " in training set: %d (%.2f%%) <diff:%.4f>" % (training,training_percentage,diff)
	print " in test set: %d (%.2f%%)" % (test,test_percentage)
	print"""


	for line in file(options.filename):
		p = random.randint(0,100)
		if p < percentage: # split for training
			ftraining.write(line[0:len(line)-1]+'\n')
			training += 1
		else:
			ftest.write(line[0:len(line)-1]+'\n')
			test += 1
	fi.close() # close files
	ftraining.close()
	ftest.close()
	total = training + test
	training_rate = training/float(total)
	test_rate = 1.0 - training_rate
	training_percentage = training_rate*100.0
	diff = float(percentage) - training_percentage
	test_percentage = test_rate*100.0
	print "Total instances: %d" % total
	print " in training set: %d (%.2f%%) <diff:%.4f>" % (training,training_percentage,diff)
	print " in test set: %d (%.2f%%)" % (test,test_percentage)
	print
    else:
        parser.print_help()
