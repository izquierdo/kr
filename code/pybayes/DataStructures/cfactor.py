#!/usr/bin/python
# This class is << intended >> to be a faster implementation of
# a Factor structure.
import probstat # combinatorics module

class Variable:
    " Defines a random variable object "
    
    def __init__(self,domain):
        " domain, ordered variable outcomes "
        self.data = domain # discrete domain
        self.__index = -1


    def __len__(self):
        " Variable domain size (cardinality) "
        return len(self.data)

    def __getitem__(self,index):
        " Return value "
        return self.data[index]

    def __iter__(self):
        return self

    def next(self):
        " iterate through values in domain "
        if self.index >= len(self.data)-1:
            self.__index = -1
            raise StopIteration

        self.__index = self.__index + 1
        return self.data[self.__index]        

class IndexMap:
    """ Maps one set of variables to another one by mathcing indices.
    This is useful when multiplying factors. """

    def __init__(self,V1,V2):
        " Input: V1, V2, ordered list of variables s.t. V1 \in V2 "
        self.V1 = V1
        self.V2 = V2
        self.__mapping = {} # maps var index in V1 to V2
        for i,v1 in enumerate(V1):
            for j,v2 in enumerate(V2):
                if v1==v2:
                    self.__mapping[i] = j

        #self.index = -1
    def __getitem__(self,config):
        " return mapping from full configuration to V1 subconfig "
        return [ config[self.__mapping[i]] for i in xrange(len(self.V1)) ]      

    def __iter__(self):
        self.it = iter(probstat.Cartesian([ range(len(v)) for v in self.V2 ]))
        return self
    
    def next(self):
        " iterate through V2 domain "
        x = self.it.next()
        return [ x[self.__mapping[i]] for i in xrange(len(self.V1)) ]
        

class Factor:
    " Defines a factor object "
    
    def __init__(self,args):
        " Input: args, ordered list of variables "
        self.variables = args # argument variables      
        length = 1
        for var in args:
            length *= len(var)
        self.__data = [ 0.0 for value in xrange(length) ]

    def __getitem__(self,inst):
        """ Input: values, listtuple of variable value indices
        in the same ordering as passed in the constructor 
            Output: F(values), factor value for given argument
        """
        assert (len(inst) == len(self.variables)), "Wrong number of values indices"

        pos = 0
        acc = 1
        for i in xrange(len(self.variables)):
            pos += acc*inst[i]
            acc *= len(self.variables[i])
        return self.__data[pos]


    def __setitem__(self,inst,value):
        " Input: instatiantion, corresponding factor value "       
        assert (len(inst) == len(self.variables)), "Wrong number of values indices"

        pos = 0
        acc = 1
        for i in xrange(len(self.variables)):
            pos += acc*inst[i]
            acc *= len(self.variables[i])
        self.__data[pos] = value

    def __iter__(self):
        " iterate through configurations indices "
        #self.it = iter(probstat.Cartesian([[x.data] for x in self.variables]))
        return iter(probstat.Cartesian([ range(len(var)) for var in self.variables ]))

    def __len__(self):
        " Return factor domain size "
        return len(self.__data)


    def __mul__(self,other):
        " Multiply two factors "
        #mapping = {} # maps config var indices to subconfig var indices

        args = self.variables[:]
        #j = len(args)
        for i,v in enumerate(other.variables):
            if v not in args:
                args.append(v)
                #j = j + 1
                #mapping[i]=j
            #else:
            #    for k,w in enumerate(self.variables):
            #        if w == v:
            #            mapping[i]=k
                        #break

        #print mapping, len(args)

        f = Factor(args)

        i1 = iter(IndexMap(self.variables,args))
        i2 = iter(IndexMap(other.variables,args))

        for i in xrange(len(f)):
            x1 = i1.next() # get next index mapping for this factor
            x2 = i2.next() # get next index mapping for other factor
            #print i, x1, self[x1],
            #print [ mapping[i] for i in xrange(len(other.variables)) ],
            #print x2, other[x2], '=' , self[x1]*other[x2]
            f.__data[i] = self[ x1 ] * other[ x2 ]

        return f

    def __str__(self):
        " Print factor data matrix "
        return "{%s}" % ", ".join(map(str, self.__data))


if __name__ == "__main__":

    x1 = Variable(range(2))
    x2 = Variable(range(3))
    x3 = Variable(range(1))
    x4 = Variable(['yes','no','maybe'])
    clique = [x1,x2,x4]
    pair1 = [x4,x2]
    pair2 = [x1,x3]
    f1 = Factor(clique)
    f2 = Factor(pair1)
    f3 = Factor(pair2)
    #print [v for v in x1]
    #print [v for v in x4]
    
    #it = iter(probstat.Cartesian([x.data for x in [x1,x2,x3]]))
    #print it.next()
    #print it.next()

    #f1[0,0,0] = 0.5
    #f1[0,0,2] = 0.4
    #f1[1,1,1] = 0.7
    for x in probstat.Cartesian([ range(len(x)) for x in clique ]):
        f1[x] = x[0]+x[1]+x[2]

    for x in probstat.Cartesian([ range(len(x)) for x in pair1 ]):
        f2[x] = x[0]+x[1]

    for x in probstat.Cartesian([ range(len(x)) for x in pair2 ]):
        f3[x] = x[0]-x[1]

    print 'f1'
    for v in f1:
        print v, f1[v]
                       
    print
    print 'f2'
    
    for v in f2:
        print v, f2[v]

    print
    print 'f3'

    for v in f3:
        print v, f3[v]

    #for v in IndexMap([x4,x1],clique):
    #    #pass
    #    print v
                      

    #print
    #print
    
    #f = f1*f2
    #for v in f:
    #    print v, f[v], '|'

    print
    print
    
    f = f2*f3
    print 'f2*f3'
    for v in f:
        print v, f[v]
