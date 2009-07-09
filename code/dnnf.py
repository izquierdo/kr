from collections import defaultdict, deque
from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination
from c2dpipe import run_c2d

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
    B.cpt = Factor([B, A], [0.5,0.5,0.8,0.2])
    # print A.cpt
    # print B.cpt
    g = DBN(V,E,name,header)
    
    # print header
    d = todnnf(g)
    print g.inference({A:'false', B:'true'}, {})
    print d.mpe({}, True)



class Circuit(object):
    def __init__(self, nodes, lambdas, thetas):
        self.nodes = []
        # self._simplify()

        # hacer la sustituciones en el dDNNF:
        # 1. Literales negativos por 1
        # 2. variables theta por la probabilidad correspondiente
        for nodetype, children in nodes:
            if nodetype == "L":
                var = children[0]
                if var < 0:
                    self.nodes.append(["L", [1.0]])
                elif var in thetas:
                    V, inst = thetas[var]
                    p = V.cpt[list(inst)]
                    self.nodes.append(["L", [p]])
                elif var in lambdas:
                    V, value = lambdas[var]
                    self.nodes.append(["L", [V.name, value]])
            else:
                self.nodes.append([nodetype, children])


    def mpe(self, e={}, getinstance=False):
        def varvalue(var, value):
            if var not in e:
                return 1.0
            elif e[var] == value:
                return 1.0
            else:
                return 0.0

        probs = []
        # esto recorre el arbol desde las hojas hata la raiz,
        # propagando las probabilidades hacia arriba de la siguiente
        # manera:
        #  - En los nodos OR calcula el maximo de todos los hijos
        #  - En los nodos AND calcual el producto de todos los hijos
        # Haciendo esto al llegar a la raiz tenemos el MPE
        
        for i, (nodetype, children) in enumerate(self.nodes):
            if nodetype == "L":
                if len(children) == 1:
                    probs.append(children[0])
                else:
                    probs.append(varvalue(children[0], children[1]))
                # print i, "L", probs[-1]

            elif nodetype == "A":
                # print i, "  A (*)", 
                p = 1
                assert children[0] > 0, "nodo AND sin hijos"
                # children[1:] por el primer elemento es el numero de hijos
                for child in children[1:]:
                    p *= probs[child]
                #     print probs[child],
                # print "->", p
                probs.append(p)

            elif nodetype == "O":
                assert children[0] > 0 and children[1] == 2, "nodo OR con propiedades extranas. Ver manual de c2d"
                p = -1
                # print i, "  O (max)",
                # children[2:] por el segundo elemento es el numero de hijos
                for child in children[2:]:
                    p = max(p, probs[child])
                #     print probs[child],
                # print "->", p
                probs.append(p)
            else:
                raise Exception("nodo desconocido")


        instance = None
        if getinstance:
            # para recuperar la instancia mas probable recorremos el
            # arbol partiendo de la raiz de la siguiente manera:
            #
            # - En los nodos OR seguimos descendiendo por el hijo que
            #   tenga la misma probabilidad que el nodo actual. Es
            #   decir, en los nodos OR buscamos el hijo con maxima
            #   probabilidad (que es precisamente la probabilidad del
            #   nodo actual)
            #
            # - En los nodos AND descendemos por todos los hijos
            #
            # - Agregamos a la instancia resultante las variables con
            #   la instancia correspondiente a las hojas que se
            #   visitan
            
            instance = {}
            s = deque()
            s.append(len(self.nodes)-1)
            while s:
                i = s.popleft()
                nodetype, children = self.nodes[i]
                if nodetype == "O":
                    for child in children[2:]:
                        if probs[child] == probs[i]:
                            s.append(child)
                            break
                elif nodetype == "A":
                    s.extend(children[1:])
                elif nodetype == "L":
                    if len(children) > 1:
                        instance[children[0]] = children[1]


        # TODO: dividir probs[-1] por Pr(e)

        return probs[-1], instance

    def __str__(self):
        l = []
        for x, y in self.nodes:
            l.append("%s: %s" %( x, y))
        return "\n".join(l)
        # return "<dDNNF %d nodes>" % len(self.nodes)

        
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

    # for x in lambdas:
    #     print "lambda", x, lambdas[x]

    # for x in thetas:
    #     print "theta", x, thetas[x]

    clauses = []
    for var in dbn.V:
        clauses.append([lambdas[var, value] for value in var.Domain] + [0])
        domain = var.Domain
        for i in range(len(domain)):
            for j in range(i+1, len(domain)):
                clauses.append([-lambdas[var, domain[i]], -lambdas[var, domain[j]], 0])

    for theta, varno in thetas.iteritems():
        var = theta[0]
        u = zip(theta[1], var.cpt.M[0])
        clauses.append([-lambdas[var2, value2] for (value2, var2) in u] + [varno, 0])
        # u.pop(0) # esto supne que la primera variable de un CPT es la variable no condicional
        clauses.extend([-varno, lambdas[var2, value2], 0] for (value2, var2) in u)

    # for x in clauses:
    #     print x

    cnf = "p cnf %s %s\n" % (varcount-1, len(clauses))
    cnf += "\n".join(" ".join(str(y) for y in x) for x in clauses)
    nnf = run_c2d(cnf, ["-smooth", '-reduce'])

    nnf = nnf.split("\n")
    nnf = [[x.split()[0]]+ map(int, x.split()[1:]) for x in nnf if x.strip()]
    header = nnf.pop(0)
    assert header[0] == "nnf"
    g = defaultdict(set)
    index = 0


    vv = {}
    T = {}
    L = {}
    for var, value in lambdas:
        vv[lambdas[var,value]] = ("lambda", var, value)
        L[lambdas[var,value]] = (var, value)
        
        
    for var, inst in thetas:
        vv[thetas[var,inst]] = ("theta", var, inst)
        T[thetas[var,inst]] = (var, inst)
        
    # print vv

    l = [[x[0], x[1:]] for x in nnf]
    d = Circuit(l, L, T)

    return d
    # print d
    
    # for node in nnf:
    #     ntype = node.pop(0)
    #     if ntype == "L":
    #         if node[0] < 0:
    #             g[index] = ('L1', 1.0)
    #         else:
    #             var = vv[node[0]]
    #             if var[0] == "lambda":
    #                 g[index] = ('L2', var[1:])
    #             if var[0] == "theta":
    #                 #g[index] = ('L3', var[1].cpt[list(var[2])], var[1:])
    #                 g[index] = ('L3', var[1].cpt[list(var[2])])
    #     elif ntype == "O":
    #         children = node[2:]
    #         assert len(children) == node[1]
    #         g[index] = ('O', children)
    #     elif ntype == "A":
    #         children = node[1:]
    #         assert len(children) == node[0]
    #         g[index] = ('A', children)
            
    #     index += 1
        
    # g = dict(g)
    # # for x in g:
    # #     print x, g[x]
        

    # # print to_dot(g)
    # return g


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

    
import pybayes.IO.io

if __name__ == "__main__":
    # g = pybayes.IO.io.load_bif("dog-problem.bif")
    # # print g.V
    # # print get_mpe_naive(g, {g.V[0]: 'true'})
    # d = todnnf(g)
    # print to_dot(d)
    test2()
