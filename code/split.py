from collections import defaultdict
from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination
from c2dpipe import run_c2d
import copy
import dnnf


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

    # calcular los CPTs

    # para cada variable no afectada por el split + variable papa: copiar cpts
    for v in bn.V:
        if not (v in Z):
            old2new[v].cpt = Factor([old2new[e] for e in v.cpt.domain()], v.cpt.getfunction())

    # para la variable creada por el split: cpt uniforme
    newnode.cpt = Factor([newnode], [1.0/len(newnode.domain()) for e in newnode.domain()])

    # para cada variable hijo afectada por el split: cpt igual a anterior, pero
    # con lista de papas cambiada
    def cp(e):
        if e == node:
            return newnode

        return old2new[e]

    for v in Z:
        old2new[v].cpt = Factor([cp(e) for e in v.cpt.domain()], v.cpt.getfunction())
    
    name = bn.name + " splitted"
    beta = 1
    return DBN(V,E,name,""), newnode


def find_mpe(fbn, sbn, compat, beta, e):
    """
    Hallar el mpe de fbn (full bayesian network) utilizando sbn
    (splitted bayesian network) como heuristica.

    fbn: red completa
    sbn: red splitted
    compat: lista de compatibilidades en sbn. Debe ser un diccionario de
            de variables de sbn en lista de variables de sbn. (TODO: cambiar por UnionFind)
    e: evidencia
    """
    # variables que hay que asignar
    fvars = dict((v.name, v) for v in fbn.V)
    svars = dict((v.name, v) for v in sbn.V)

    freevars = {}
    for varname, var in fvars.iteritems():
        if varname not in e:
            freevars[varname] = (var, svars[varname], var.Domain)

    ac = dnnf.todnnf(sbn)

    inst = {}
    ee = dict((fvars[name], value) for name, value in e.iteritems())
    def dfs(alpha, varsleft):
        if not varsleft:
            xx = dict((fvars[name], value) for name, value in inst.iteritems())
            ##ee = dict((fvars[name], value) for name, value in e.iteritems())
            xx.update(ee)
            alpha = max(alpha, fbn.inference(xx, {}).z())
            # print "hojas", alpha
        else:
            varname = varsleft.pop()
            domain = freevars[varname][2]

            # probar todos sus posibles valores
            for value in domain:
                inst[varname] = value

                # instanciar las variables que tienen que ser compatibles:
                xx = inst.copy()
                xx.update(e)
                for parent, clones in compat.iteritems():
                    if parent in inst:
                        for clone in clones:
                            xx[clone] = inst[parent]
                            
                p, i = ac.mpe(xx, False)
                if p*beta <= alpha:
                    continue
                else:
                    alpha = max(alpha, dfs(alpha, varsleft))

            # regresar todo al estado orignal
            varsleft.append(varname)
            del inst[varname]
        return alpha

    p = dfs(0.0, freevars.keys())
    print p

if __name__=="__main__":
    import pybayes.IO.io
    g1 = pybayes.IO.io.load_bif("dog-problem.bif")


    g2, newnode = split(g1, g1.V[0], [g1.V[3]])
    compat = {}
    compat[g1.V[0].name] = [newnode.name]
    
    ac1 = dnnf.todnnf(g1)
    ac2 = dnnf.todnnf(g2)

    print "ac1", ac1.mpe()
    print "ac2", ac2.mpe()
    find_mpe(g1, g2, compat, 2, {})
