from subprocess import Popen, PIPE, check_call, CalledProcessError
import sys
from tempfile import NamedTemporaryFile
import os

"""
Un programa sencillo para correr c2d en un pipe.

c2d solo puede ejectuarse con un archivo de entrada especificado con
el parametro -in. Este programa permite utilizar un pipe del la forma
`programa | python c2dpipe'
"""

class C2DError(Exception):
    pass

def run_c2d(cnf, args=[]):
    infile = NamedTemporaryFile(delete=False)
    outfile = infile.name  + ".nnf"
    try:
        fn = infile.name
        infile.write(cnf)
        infile.close()
        msg = ""
        try:
            p = Popen(["./c2d_linux"] + args + ["-in", fn], stdout=PIPE)
            msg = p.communicate()[0]
            return open(outfile).read()
        except (IOError, OSError), e:
            raise C2DError(str(e) + ("\n" + msg if msg else ""))
        else:
            os.unlink(outfile)
    finally:
        os.unlink(infile.name)
    

def main(args):
    try:
        print run_c2d(sys.stdin.read(), args),
    except (Exception), e:
        print "Error ejecutando c2d:", e
    

if __name__ == "__main__":
    main(sys.argv[1:])
