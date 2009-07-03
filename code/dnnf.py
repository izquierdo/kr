from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination
from c2dpipe import run_c2d

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
    B.cpt = Factor([B, A], [0.6,0.4,0.05,0.95])
    g = DBN(V,E,name,header)
    
    # print header
    todnnf(g)


def todnnf(dbn):
    parents = find_parents(dbn.G)
    lambdas = {}
    thetas = {}
    varcount = 1

    # crear las variables
    for var in dbn.V:
        for value in var.Domain:
            lambdas[var, value] = varcount
            varcount += 1

        p = parents.get(var)
        if p is not None:
            domain = var.cpt.domain()
            # selfindex = domain.index(var)
            # print var, p, var.cpt.domain(), selfindex
            for m in Combination(var.cpt.domain()):
                thetas[var, tuple(m)] = varcount
                varcount += 1


    clauses = []
    for var in dbn.V:
        clauses.append([lambdas[var, value] for value in var.Domain] + [0])
        domain = var.Domain
        for i in range(len(domain)):
            for j in range(i+1, len(domain)):
                clauses.append([-lambdas[var, domain[i]], -lambdas[var, domain[j]], 0])

    for theta in thetas:
        var = theta[0]
        u = zip(theta[1], var.cpt.M[0])
        clauses.append([-lambdas[var2, value2] for (value2, var2) in u] + [thetas[theta], 0])
        u.pop(0) # esto supne que la primera variable de un CPT es la variable no condicional
        clauses.extend([-thetas[theta], lambdas[var2, value2], 0] for (value2, var2) in u)
            
    cnf = "p cnf %s %s\n" % (varcount-1, len(clauses))
    cnf += "\n".join(" ".join(str(y) for y in x) for x in clauses)
    nnf = run_c2d(cnf)
    print nnf
    return nnf


if __name__ == "__main__":
    test2()
