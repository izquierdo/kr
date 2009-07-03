#!/usr/bin/python
# Graphs Manipulation
# (C) 2008 Denis Maua'

'''
   Simple Graph Module that aims at supporting the Bayesian Networks Structures
	
 	Several routines were extracted from D. Eppstein's PADS library
'''

def make_adj_list(V,E):
	""" Create an adjacency list representation using V and E.
		input: tuple (V,E) of vertices and edges
		output: adjacency map G """
	G = {}
	#pa = {}
	if V is None or E is None:
		return
	for u in V:
		G[u] = []
		#pa[u] = []
		for (w,v) in E:
			if w == u:
				G[u].append(v)
		#pa[v].append(u)
	return G

def make_undir_graph(V,E):
	""" Create an undirected graph for a given directed graph G=(V,E) """
	UD = []
	for (u,v) in E:
		if (v,u) not in E:
			UD.append((u,v))
			UD.append((v,u))
	return UD

def isUndirected(G):
    """Check that G represents a simple undirected graph. -- D. Eppstein, April 2004."""
    for v in G:
        if v in G[v]:
            return False
        for w in G[v]:
            if v not in G[w]:
                return False
    return True

def dfs(G):
	""" Depth-first search 
		input: adjacency map G
		output: topological sort strucutre containg vertices in topological sort,
				and parenthood mapping	"""
	class DfsContext: pass
	c = DfsContext()
	c.adj = G
	c.color = {}
	c.p = {}
	c.d = {}
	c.f = {}
	c.topo = []
	for u in G:
		c.color[u] = 1 # WHITE
		c.p[u] = None
	c.count = 0
	for u in G:
		if c.color[u] == 1: # WHITE
			__dfs_visit(u, c)
	return c

def __dfs_visit(u, c):
    c.color[u] = 3 # GRAY
    c.d[u] = c.count
    c.count = c.count + 1
    for v in c.adj[u]:
        if c.color[v] == 1: # WHITE
            c.p[v] = u
            __dfs_visit(v, c)
    c.color[u] = 2 # BLACK
    c.topo.insert(0,u)
    c.f[u] = c.count
    c.count = c.count + 1

def find_parents(G):
	""" Find parents in adjacency list G """
	pa = {}
	for u in G:
		for v in G[u]:
			if not pa.has_key(v):
				pa[v] = [u]
			else:
				pa[v].append(u)
	return pa
def print_graph(G):
	print "Graph Adjacency List"
	for v in G:
		print v, ": ",
		for adj in G[v]:
			print adj, " ",
		print ""

def union(*graphs):
    """ Return a graph having all edges from the argument graphs. """
    from sets import Set
    out = {}
    for G in graphs:
        for v in G:
            out.setdefault(v,Set()).update(list(G[v]))
    return out

def MinimumSpanningTree(V,E,W):
    """
    Return the minimum spanning tree of an undirected graph G=(V,E) with total its cost.
    W is a weights dictionary containing weight w of edge (u,v)
    as the dict entry W[(u,v)] = W[(v,u)] = w (W should be symmetric).
    The tree is returned as a list of edges.

    Notes: Kruskal's algorithm for minimum spanning 
	   Adpated from D. Eppstein' implementation (April 2006 version).
    """
    
    from UnionFind import UnionFind # used for forests manipulation
    # Kruskal's algorithm: sort edges by weight, and add them one at a time.
    # We use Kruskal's algorithm, first because it is very simple to
    # implement once UnionFind exists, and second, because the only slow
    # part (the sort) is sped up by being built in to Python.
    subtrees = UnionFind()
    tree = []
    #edges = [(G[u][v],u,v) for u in G for v in G[u]]
    edges = [(W[(u,v)],u,v) for (u,v) in E]
    edges.sort()
    cost = 0.0
    for w,u,v in edges:
        if subtrees[u] != subtrees[v]:
            tree.append((u,v))
            subtrees.union(u,v)
	    cost+=w
    return (tree,cost)


	
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    
    parser.add_option('-i', '--input',
                      action='store', type='string', dest='input',
                      help='the graph input file name', metavar="INPUT")

    parser.add_option('-o', '--output',
                      action='store', type='string', dest='output',
                      help='the prism output file name', metavar="OUTPUT")

    (options, args) = parser.parse_args()          
    
    
    if options.input: #and options.output:
		import io
		G = io.load_graph(options.input)
		print G
		#g.print_graph()
		#g.save_graph(G,options.output)
    else:		"""  A simple graph containing five vertices and six arcs

	 		A-->B
	 		|   |\
	 		|   | \
	 		v   v  v
	 		D-->C->E

			AdjList = {
	      		'A': ['B','D'],
	      		'B': ['C','E'],
	      		'C': ['E'],
	      		'D': ['C'],
	      		'E': ['.']
			} """

		V = ['a','b','c','d','e']
		E = [('a','b'), ('a','d'),
			 ('b','c'), ('b','e'),
			 ('c','e'), ('d','c')]

		g = make_adj_list(V,E)

		print "Graph"
		print "  V =", V
		print "  E =", E

		print "Topological Sort"
		c = dfs(g)
		Vt = []
		for v in c.topo:
			Vt.append(v)
		print

		print "  V =", Vt
		print "  E =", E
#        parser.print_help()
