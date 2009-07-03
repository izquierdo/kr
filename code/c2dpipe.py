from subprocess import Popen, PIPE, check_call, CalledProcessError
import sys
from tempfile import NamedTemporaryFile
import os

"""
Un programa sencillo para correr c2d en un pipe.

c2d solo puede ejectuarse con un archivo de entrada especificado con
el parametro -in. Este programa permite utilizar un pipe del la forma `programa | python c2dpipe'
"""

def main(args):
    infile = NamedTemporaryFile(delete=False)
    outfile = infile.name  + ".nnf"
    try:
        fn = infile.name
        infile.write(sys.stdin.read())
        infile.close()
        try:
            check_call(["./c2d_linux"] + args + ["-in", fn], stdout=PIPE)
        except (OSError, CalledProcessError), e:
            print "Error ejecutando c2d:", e
        else:
            try:
                print open(outfile).read(),
            except Exception, e:
                print "Error abriendo archivo de salida:", e
            else:
                os.unlink(outfile)
    finally:
        os.unlink(infile.name)


if __name__ == "__main__":
    main(sys.argv[1:])
