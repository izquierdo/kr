#!/usr/bin/python

""" Expression tree solver
    Solve expressions parsed into a
    rooted tree recursively

    (C) 2008 Denis Mauá	 """

def evaluate(op,op1,op2):
	"Evaluate local expressions"
	return eval(str(op1) + op + str(op2))

def solve(T,v):
	"""Solve expression recursively
	
	T is a tree stored as a dict, v a root node"""
	#print "(",v,")"
	if not T.has_key(v):
		return int(v)
	else:
		childhood = T[v]
		if v == "*":
			r = 1
		elif v == '+':
			r = 0

		for ch in childhood:
			#print ">"
			s = solve(T,ch)
			#print "<", s
			#print s,v,r,
			r = evaluate(v,r,s)
			#print "=", r
		return r
# simple example
# 2 * (3 + 4) = 14
#    *
# 2     +
#    3     4

T = {'*':['2','+'],'+':['3','4']}
s = solve(T,'*')
print "2 * (3 + 4) = ", s

