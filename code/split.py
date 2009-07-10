from collections import defaultdict
from pprint import pprint
from pybayes.Models.bn import *
from pybayes.Graph.graphs import *
from pybayes.Combinatorics.combinatorial import Combination
from c2dpipe import run_c2d
from datetime import datetime
import copy
import dnnf


def split(bn, node, Z=None):
    """
    Hace split de la red bayesiana `bn' en el nodo `node' de acuerdo `Z'
    
    bn:   red bayesiana
    node: variable en la cual hacer el split
    Z:    subconjunto de hijos de node que van a quedar como hijos del
          nuevo nodo (los demas se quedan en el nodo original)
    """
    # no estoy seguro si hace falta crear nuevas variables, pero mas
    # vale prevenir que lamentar
    for v in bn.V:
        if v.name == node:
            node = v
            break
    if Z is None:
        Z = bn.G[node]

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
            de variables de sbn en lista de variables de sbn.
    beta: beta sbn
    e: evidencia
    """
    evars = set(e)
    freevars = [v for v in fbn.V if v.name not in evars]

    # para instanaciar las variables splitted primero. Ver popsition 1
    # del paper
    freevars.sort(key=lambda x: x.name in compat)    
    
    t = datetime.now()
    ac = dnnf.todnnf(sbn)
    print datetime.now() - t
    print "dfs", freevars
    def dfs(q, varsleft, z, k):
        """
        q: cota actual
        varsleft: variables que faltan por instanciar. Se sacan del final.
        z: instanciacion parcial actual
        k: numero de variables splitted que falta por instanciar
        """
        var = varsleft.pop()
        varname = var.name
        domain = var.Domain
        k -= 1
        clones = []
        if varname in compat:
            for clone in compat[varname]:
                clones.append(clone)

        # probar todos sus posibles valores
        for value in domain:
            # agregar ese valor a la instancia parcial
            z[varname] = value
            for clone in clones:
                z[clone] = value
            p = ac.mpe(z)

            if varsleft:
                # si todavia quedan variables por asignar
                # hacer prune si podemos
                
                if k<=0:
                    # ya todas las variables splitted estan
                    # asignadas. Ahora el MPE(sbn) = MPE(fbn), no hace
                    # falta hacer mas asignaciones para obtener el
                    # valor exacto (Proposicion 1 del paper)
                    q = max(q, beta*p)
                else:
                    if p*beta <= q:
                        # la cota superior sobre sbc es menor que la
                        # cota inferior q que llevamos. Por aqui no
                        # hay nada mejor
                        continue
                    else:
                        # todavia puede haber algo bueno por aqui
                        q = max(q, dfs(q, varsleft, z, k))
            else:
                # si no queda ninguna variable por asignar.
                # por un teorema, el MPE(fbn, x) == beta*MPE(sbn, x)
                q = max(q, beta*p)

        # regresar todo al estado orignal
        varsleft.append(var)
        del z[varname]
        for clone in clones:
            del z[clone]
        return q

    return dfs(0.0, freevars, e, len(compat))

if __name__=="__main__":
    import pybayes.IO.io
    g1 = pybayes.IO.io.load_bif("../Grid/Bif/Ratio_50/50-20-1.bif")
    splits = 100
    import random
    g2 = g1
    compat = {}
    for v in random.sample(g1.V, splits):
        g2, aa = split(g2, v.name, None)
        compat[v.name] = [v.name+"*"]
        
        
    beta = 2**splits
    e = {}

    # print "mpe full"
    # print compat.keys()
    # acp = ac1.mpe()
    bbp = find_mpe(g1, g2, compat, beta, e)
    # print "ac", acp
    print "bb", bbp
