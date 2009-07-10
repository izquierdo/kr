SHELL=/bin/bash
LATEX=latex
PDFLATEX=pdflatex
BIBTEX=bibtex
DVIPDF=dvipdf

DOCUMENTO=informe

EXT_BASURA={log,aux,toc,dvi,pdf,bbl,blg,out,lot}

all: ${DOCUMENTO}.pdf

.SUFFIXES: .tex .pdf .dvi

%.dvi: %.tex
	${LATEX} $(patsubst %.tex,%,$<)
	${BIBTEX} $(patsubst %.tex,%,$<)
	${LATEX} $(patsubst %.tex,%,$<)
	${LATEX} $(patsubst %.tex,%,$<)

.tex.pdf:
	${PDFLATEX} $(patsubst %.tex,%,$<)
	${BIBTEX} $(patsubst %.tex,%,$<)
	${PDFLATEX} $(patsubst %.tex,%,$<)
	${PDFLATEX} $(patsubst %.tex,%,$<)

#${BIBTEX} $(patsubst %.tex,%,$<)
#$(PDFLATEX) $<
#$(PDFLATEX) $<

.PHONY: clean

clean:
	rm -f {${DOCUMENTO},${DOCUMENTO_CD}}.${EXT_BASURA}
