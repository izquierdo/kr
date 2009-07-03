# Example using Factor Graphs and Loopy Belief Propagation
from Models.factorgraph import FactorGraph
from Models.bn import *

#if __name__ == "__main__":
def run():
	" Run this example "
	print \
	"""
	pyBayes
	(C) 2008 Denis Maua'
	This class implements Factor Graphs and the sum-product algorithm.
	"""
	print 
	print " Example extracted from Kschischang et al. 2001. Factor Graphs and the Sum-Product Algorithm. IEEE  Trans. On Inf. Theory. Vol 47. No. 2. "
	print """
  FA -- X1        FD -- X4
         \       /
          FC -- X3
         /       \\
  FB -- X2        FE -- X5
        """
        
	#""" 
	X1 = RandomVariable('X1',['true','false'])
	X2 = RandomVariable('X2',['true','false'])
	X3 = RandomVariable('X3',['true','false'])
	X4 = RandomVariable('X4',['true','false'])
	X5 = RandomVariable('X5',['true','false'])

	FA = Factor([X1],[0.4,0.6],name='FA')
	FB = Factor([X2],[0.3,0.7],name='FB')
	FC = Factor([X3,X1,X2],[0.2,0.8,0.5,0.5,0.6,0.4,0.1,0.9],name='FC')
	FD = Factor([X4,X3],[0.4,0.6,0.7,0.3],name='FD')
	FE = Factor([X5,X3],[0.1,0.9,0.7,0.3],name='FE')

	V1 = [X1,X2,X3,X4,X5]
	V2 = [FA,FB,FC,FD,FE]
	E = [(FA,X1),(X1,FA),(FB,X2),(X2,FB),(X1,FC),(FC,X1),(X2,FC),(FC,X2),(FC,X3),(X3,FC),(X3,FD),(FD,X3),(X3,FE),(FE,X3),(FD,X4),(X4,FD),(FE,X5),(X5,FE)]
	#"""


	""" # Dog Example in Factor Graph form
	F = RandomVariable('family_out',['true','false'])
	B = RandomVariable('bowel_problem',['true','false'])
	L = RandomVariable('lights',['on', 'off'])
	D = RandomVariable('dog_out',['true', 'false'])
	H = RandomVariable('hear_bark',['true', 'false'])

	FF = Factor([F],[0.15,0.85])
	FB = Factor([B],[0.01,0.99])
	FL = Factor([L, F], [0.6,0.4,0.05,0.95])
	FD = Factor([D, F, B], [0.99,0.01,0.97,0.03,0.9,0.1,0.3,0.7])	
	FH = Factor([H, D], [0.7,0.3,0.01,0.99])

	V1 = [F,B,L,D,H]
	V2 = [FF,FB,FL,FD,FH]
	E = [(FF,F),(F,FF),(FB,B),(B,FB),(F,FL),(FL,F),(FL,L),(L,FL),(F,FD),(FD,F),(FD,B),(B,FD),(FD,D),(D,FD),(D,FH),(FH,D),(FH,H),(H,FH)]
	#"""

	#"""
	fg = FactorGraph(V1,V2,E)
	fg.sum_product(verbose=False)
	print "-- FG Inference -------------------------------"
	fg.marginals()


	X1.cpt = FA
	X2.cpt = FB
	X3.cpt = FC
	X4.cpt = FD
	X5.cpt = FE

	E1 = [(X1,X3),(X2,X3),(X3,X4),(X3,X5)]

	g = DBN(V1,E1)
	print "-- BN Inference -------------------------------"
	print g.inference({X1:None},{})
	print g.inference({X2:None},{})
	print g.inference({X3:None},{})
	print g.inference({X4:None},{})
	print g.inference({X5:None},{})



	fg2 = FactorGraph(V1,V2,E)
	fg2.max_product(verbose=False)
	print "-- MAP Product --------------------------------"
	#fg2.marginals()
	fg2.map()
	print
	#print FA*FB*FC*FD*FE

	#"""

	# Take the log-factor (log-linear model)
	FA.log()
	FB.log()
	FC.log()
	FD.log()
	FE.log()

	logfg = FactorGraph(V1,V2,E)
	#logfg.log_sum_product(verbose=False)
	logfg.viterbi(verbose=False)
	print "-- Log-Linear MAP Inference -----------------"
	#logfg.marginals2()
	logfg.map2()
	print
	#print FA+FB+FC+FD+FE


	#"""

	"""
	print '-- BN ---------------------------------------'
	print g.inference({X3:None},{X4:'false',X5:'true'})
	print

	print fg.G[X3]
	print fg.mi[X3][FC]
	print fg.mi[X3][FD]
	print fg.mi[X3][FE]
	#"""

	"""v = X3
	for n in fg.G[v]:	
		g = fg.mi[v][n] * g
	print "Marginal", v
	print g"""
