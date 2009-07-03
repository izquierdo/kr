from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination

def test():
    name = "dogproblem"
    header = \
    """ The Dog Problem Network
         F     B
         |\   /
         | \ /

         v  v
         L  D-->H

        Extracted from E. Charniak.
        Bayesian networks without tears.
        AI Magazine, 1991. \n """

    F = RandomVariable('family_out',['true','false'])
    B = RandomVariable('bowel_problem',['true','false'])
    L = RandomVariable('lights',['on', 'off'])
    D = RandomVariable('dog_out',['true', 'false'])
    H = RandomVariable('hear_bark',['true', 'false'])
    ### Graph Nodes
    V = [F,B,L,D,H]
    ### Graph Arcs
    E = [(F,L), (F,D),
         (B,D), (D,H)]
    ### Conditional distributions
    F.cpt = Factor([F],[0.15,0.85])
    B.cpt = Factor([B],[0.01,0.99])
    L.cpt = Factor([L, F], [0.6,0.4,0.05,0.95])
    D.cpt = Factor([D, F, B], [0.99,0.01,0.97,0.03,0.9,0.1,0.3,0.7])    
    H.cpt = Factor([H, D], [0.7,0.3,0.01,0.99])
            
    g = DBN(V,E,name,header)
    
    print header
    todnnf(g)

def test2():
    name = "jcproblem"
    header = \
    """ The JC Problem Network
         A
         |
         |
         v
         B"""

    A = RandomVariable('A',['true','false'])
    B = RandomVariable('B',['true','false'])
    ### Graph Nodes
    V = [A,B]
    ### Graph Arcs
    E = [(A,B)]
    ### Conditional distributions
    A.cpt = Factor([A],[0.15,0.85])
    B.cpt = Factor([A, B], [0.6,0.4,0.05,0.95])
    g = DBN(V,E,name,header)
    
    print header
    todnnf(g)


def todnnf(dbn):
    parents = find_parents(dbn.G)
    lambdas = {}
    thetas = {}
    varn = 1

    # crear las variables
    for var in dbn.V:
        for value in var.Domain:
            lambdas[var, value] = varn
            varn += 1

        p = parents.get(var)
        if p is not None:
            domain = var.cpt.domain()
            # selfindex = domain.index(var)
            # print var, p, var.cpt.domain(), selfindex
            for m in Combination(var.cpt.domain()):
                thetas[var, tuple(m)] = varn
                varn += 1

    for var in dbn.V:
        for value in var.Domain:
            print lambdas[var, value],
        print 0
        domain = var.Domain
        for i in range(len(domain)):
            for j in range(i+1, len(domain)):
                print -lambdas[var, domain[i]], -lambdas[var, domain[j]], 0

    for theta in thetas:
        print theta
        var = theta[0]
        varvalue = theta[1][-1]     # esto supone que la ultima columna en el CPT siempre es la variable del mismo nodo

        u = zip(theta[1], var.cpt.M[0])
        print u
        for (value2, var2) in u:
            print -lambdas[var2, value2],
        print thetas[theta], 0

        u.pop()
        for value2, var2 in u:
            print -thetas[theta], lambdas[var2, value2]
            
        
            

if __name__ == "__main__":
    test2()
