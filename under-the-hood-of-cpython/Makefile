.PHONY: clean

%.pdf:
		pandoc --citeproc --listings meta.yaml $(basename $@).md -t beamer --toc -o $@

clean:
		rm -f *.pdf *.tex
