from collections import defaultdict
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
    
    g = todnnf(g)
    mpe = get_mpe(g, {A:'true'})

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
    A.cpt = Factor([A], [0.3,0.7])
    B.cpt = Factor([B, A], [0.1,0.9,0.8,0.2])
    print A.cpt
    print B.cpt
    g = DBN(V,E,name,header)
    
    # print header
    g = todnnf(g)
    mpe = get_mpe(g, {A:'true'})


def get_mpe(g, evidence):
    print "MPE----------------------------------"
    print "evidence:", evidence
    g = g.copy()

    def add_evidence(g, evidence):
        freevars = []
        for node, props in g.iteritems():
            if props[0] =="L2":
                if props[1][0] in evidence:
                    if props[1][1] == evidence[props[1][0]]:
                        g[node] = ("Le", 1.0)
                    else:
                        g[node] = ("Le", 0.0)
                else:
                    if props[1][0] not in freevars:
                        freevars.append(props[1][0])

        return freevars

    def doeval(g, root):
        nodet = g[root][0]
        if nodet[0] == "O":
            r = 0
            for child in g[root][1]:
                r += doeval(g, child)
            return r
        elif nodet[0] == "A":
            r = 1
            for child in g[root][1]:
                r *= doeval(g, child)
            return r
        elif nodet[0].startswith("L"):
            return g[root][1]

        assert 0
        
    freevars = add_evidence(g, evidence)
    for m in Combination(freevars):
        g2 = g.copy()
        inst = dict(zip(freevars, m))
        add_evidence(g2, inst)
        p = doeval(g2, max(g2.keys()))
        print inst, p
    # for node, props in g.iteritems():
    #     print node, props

        
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
            #domain = var.cpt.domain()
            # selfindex = domain.index(var)
            # print var, p, var.cpt.domain(), selfindex
            for m in Combination(var.cpt.domain()):
                thetas[var, tuple(m)] = varcount
                varcount += 1
        else:
            for m in Combination(var.cpt.domain()):
                thetas[var, tuple(m)] = varcount
                varcount += 1

    # print lambdas
    # print thetas

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
    nnf = run_c2d(cnf, [])

    nnf = nnf.split("\n")
    nnf = [[x.split()[0]]+ map(int, x.split()[1:]) for x in nnf if x.strip()]
    header = nnf.pop(0)
    assert header[0] == "nnf"
    g = defaultdict(set)
    index = 0


    vv = {}
    for var, value in lambdas:
        vv[lambdas[var,value]] = ("lambda", var, value)
        
    for var, inst in thetas:
        vv[thetas[var,inst]] = ("theta", var, inst)
    # print vv

    for node in nnf:
        ntype = node.pop(0)
        if ntype == "L":
            if node[0] < 0:
                g[index] = ('L1', 1.0)
            else:
                var = vv[node[0]]
                if var[0] == "lambda":
                    g[index] = ('L2', var[1:])
                if var[0] == "theta":
                    #g[index] = ('L3', var[1].cpt[list(var[2])], var[1:])
                    g[index] = ('L3', var[1].cpt[list(var[2])])
        elif ntype == "O":
            children = node[2:]
            assert len(children) == node[1]
            g[index] = ('O', children)
        elif ntype == "A":
            children = node[1:]
            assert len(children) == node[0]
            g[index] = ('A', children)
            
        index += 1
        
    g = dict(g)
    for x in g:
        print x, g[x]
        

    # print to_dot(g)
    return g


def to_dot(g):
    s = ["digraph g {"]
    for node, props in g.iteritems():
        if props[0] in ["L1", "L3"]:
            s.append('n%d [label="%s"]' % (node, props[1]))
        elif props[0] == "L2":
            s.append('n%d [label="%s=%s"]' % (node, props[1][0], props[1][1]))
        elif props[0] == "O":
            s.append('n%d [label="+"]' % node)
            for child in props[1]:
                s.append("n%d -> n%d" % (node, child))
        elif props[0] == "A":
            s.append('n%d [label="*"]' % node)
            for child in props[1]:
                s.append("n%d -> n%d" % (node, child))
        else:
            raise Exception("tipo de nodo desconocido")
    s.append("}")
    return "\n".join(s)

    

if __name__ == "__main__":
    test2()
