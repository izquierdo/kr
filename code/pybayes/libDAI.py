# Saving DBN into libDAI .fg file format
from Models.bn import *
import IO.io as io

A = RandomVariable('A',['true','false'])
B = RandomVariable('B',['true','false'])
C = RandomVariable('C',['true','false'])
# vertices
V = [A,B,C]
# arcs
E = [(A,B),(A,C),(B,C)]

# CPTS
A.cpt = Factor([A],[0.6,0.4])
B.cpt = Factor([B,A],[0.3,0.7,0.5,0.5])
C.cpt = Factor([C,B,A],[0.1,0.9,0.8,0.2,0.25,0.75,0.0,1,0])

g = DBN(V,E)

print g

io.save_bn_to_fg(g,"test.fg")

print g.inference({A:None},{})
print g.inference({B:None},{})
print g.inference({C:None},{})


