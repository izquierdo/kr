from Graph.graphs import *

def run():
	" Run this example "
	V = ['a','b','c','d','e','f']
	E = [('a','b'),('a','f'),('a','c'),('a','e'),('b','c'),('c','d'),('c','e'),('d','e'),('e','f')]
	EUD = make_undir_graph(V,E)
	W = {}
	for e in E:
		W[e] = 1
	W[('a','c')] = 2
	W[('c','e')] = 2
	W[('a','e')] = 2
	W[('c','d')] = 2
	W[('d','e')] = 3
	W[('e','f')] = 2
	mst,cost = MinimumSpanningTree(V,E,W)
	print 'cost: ', cost
	print mst

