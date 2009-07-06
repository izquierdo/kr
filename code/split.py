from collections import defaultdict
from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination
from c2dpipe import run_c2d
import copy


def split(bn, node, Z):
    """
    Hace split de la red bayesiana `bn' en el nodo `node' de acuerdo `Z'
    
    bn:   red bayesiana
    node: variable en la cual hacer el split
    Z:    subconjunto de hijos de node que van a quedar como hijos del
          nuevo nodo (los demas se quedan en el nodo original)
    """
    # no estoy seguro si hace falta crear nuevas variables, pero mas
    # vale prevenir que lamentar
    V = [RandomVariable(var.name, var.Domain) for var in bn.V]

    # mapeo de variables viejas a las nuevas. Sirve mas adelante para
    # crear la lista de arcos
    old2new = dict(zip(bn.V, V))

    # crear el nuevo nodo y agregarlo a la lista de variables
    newnode = RandomVariable(node.name + "*", node.Domain)
    V.append(newnode)

    # crear la lista de arcos
    E = []
    for parent, children in bn.G.iteritems():
        for child in children:
            if parent == node and child in Z:
                E.append((newnode, old2new[child]))
            else:
                E.append((old2new[parent], old2new[child]))

    # TODO: aqui hay que calcular los CPTs.
    for var in V:
        #var.cpt = Factor(...)
        pass
    
    name = bn.name + " splitted"
    return DBN(V,E,name,"")

if __name__=="__main__":
    import pybayes.IO.io
    g = pybayes.IO.io.load_bif("dog-problem.bif")
    # for x,y in g.G.iteritems():
    #     print x,y
    
    print g.V
    # print g.G

    print split(g, g.V[0], [g.V[3]])
